"""Independently reproduce duplicate likes using plain HTTP, without Testimony.

Start an unmodified RWA backend at commit bdf6169232b919d9618ec29032addbd865f986cd.
Use a disposable checkout: /testData/seed resets its database for each arm.
Example:
  python3 reproduce_rwa_duplicate_likes.py --output-dir /tmp/rwa-like-repro-01
The output directory must not exist. Existing evidence is never overwritten.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import platform
import time
import urllib.error
import urllib.parse
import urllib.request


PINNED_COMMIT = "bdf6169232b919d9618ec29032addbd865f986cd"
USERS = {"A": "Heath93", "B": "Arvilla_Hegmann"}
PASSWORD = os.environ.get("RWA_SEED_PASSWORD", "s3cret")


def now():
    return datetime.now(timezone.utc).isoformat()


def redact(value):
    if isinstance(value, dict):
        return {
            k: "[REDACTED]" if k.lower() in {
                "password", "passwordhash", "token", "accesstoken", "refreshtoken"
            } else redact(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


class Evidence:
    def __init__(self, base_url, output):
        self.base_url = base_url.rstrip("/")
        self.path = output / "evidence.jsonl"
        self.path.touch(exist_ok=False)
        self.sequence = 0

    def session(self, label):
        jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        return Session(self, label, opener)


class Session:
    def __init__(self, evidence, label, opener):
        self.evidence, self.label, self.opener = evidence, label, opener

    def call(self, method, path, body=None, *, round_number, arm, step):
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self.evidence.base_url + path, data=data, headers=headers, method=method
        )
        started = time.monotonic()
        self.evidence.sequence += 1
        seq = self.evidence.sequence
        try:
            response = self.opener.open(request, timeout=15)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            status = response.status
            raw = response.read().decode("utf-8", errors="replace")
            content_type = response.headers.get("Content-Type")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = raw
        record = {
            "seq": seq, "round": round_number, "arm": arm, "step": step,
            "actor": self.label, "method": method, "path": path,
            "request_body": redact(body), "status": status,
            "response": redact(parsed), "response_content_type": content_type,
            "elapsed_ms": round((time.monotonic() - started) * 1000, 3),
            "at_utc": now(),
        }
        with self.evidence.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        return status, parsed, seq


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def execute_arm(evidence, round_number, arm):
    options = {"round_number": round_number, "arm": arm}
    anon = evidence.session("anonymous")
    status, _, _ = anon.call("POST", "/testData/seed", step="reset", **options)
    require(status == 200, f"Seed failed: {status}")
    sessions, user_ids = {}, {}
    for actor, username in USERS.items():
        session = evidence.session(actor)
        status, body, _ = session.call(
            "POST", "/login", {"username": username, "password": PASSWORD},
            step="login", **options,
        )
        require(status == 200 and isinstance(body, dict), f"Login {actor} failed")
        sessions[actor], user_ids[actor] = session, body["user"]["id"]
    require(user_ids["A"] != user_ids["B"], "Control actors must be distinct")

    status, body, _ = sessions["A"].call(
        "POST", "/transactions",
        {"transactionType": "payment", "receiverId": user_ids["B"],
         "amount": 20, "description": f"duplicate-like reproduction {round_number} {arm}"},
        step="create_fresh_transaction", **options,
    )
    require(status in (200, 201), f"Transaction creation failed: {status}")
    transaction_id = body["transaction"]["id"]
    observations, calls = [], []

    def observe(step):
        status, body, seq = sessions["B"].call(
            "GET", f"/transactions/{transaction_id}", step=step, **options
        )
        require(status == 200, f"Observation failed: {status}")
        transaction = body["transaction"]
        require(transaction["id"] == transaction_id, "Wrong observed transaction")
        likes = transaction.get("likes", [])
        require(all(x["transactionId"] == transaction_id for x in likes),
                "A like refers to a different transaction")
        observation = {
            "step": step, "evidence_seq": seq, "count": len(likes),
            "likes": [{k: x[k] for k in ("id", "userId", "transactionId")}
                      for x in likes],
            "by_actor": {actor: sum(x["userId"] == uid for x in likes)
                         for actor, uid in user_ids.items()},
        }
        observations.append(observation)
        return observation

    before = observe("before")
    require(before["count"] == 0, "Fresh transaction already has likes")
    for occurrence, actor in enumerate(
        ["B", "B"] if arm == "same_user_twice" else ["B", "A"], 1
    ):
        status, _, seq = sessions[actor].call(
            "POST", f"/likes/{transaction_id}", {"transactionId": transaction_id},
            step=f"like_{occurrence}", **options,
        )
        calls.append({"actor": actor, "status": status, "evidence_seq": seq})
        after = observe(f"after_{occurrence}")
        if occurrence == 1:
            require(status == 200 and after["count"] == 1 and
                    after["by_actor"]["B"] == 1,
                    "First like did not establish the required baseline")

    final = observations[-1]
    if arm == "same_user_twice":
        duplicated = final["by_actor"]["B"] > 1
        distinct_ids = len({x["id"] for x in final["likes"]}) == final["count"]
        if duplicated and distinct_ids:
            verdict = "BUG_REPRODUCED"
        elif final["count"] == 1 and final["by_actor"]["B"] == 1:
            verdict = "NOT_REPRODUCED"
        else:
            verdict = "INCONCLUSIVE"
    else:
        passed = (all(x["status"] == 200 for x in calls) and final["count"] == 2
                  and final["by_actor"] == {"A": 1, "B": 1})
        verdict = "CONTROL_PASS" if passed else "CONTROL_FAIL"
    return {
        "round": round_number, "arm": arm, "transaction_id": transaction_id,
        "user_ids": user_ids, "like_requests": calls,
        "observations": observations, "verdict": verdict,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:14101")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--rounds", type=int, default=3)
    args = parser.parse_args()
    parsed = urllib.parse.urlsplit(args.base_url)
    require(parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"}
            and not parsed.username and not parsed.password,
            "Use a disposable local backend over plain HTTP")
    require(args.rounds >= 1, "At least one round is required")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    evidence = Evidence(args.base_url, output)
    result = {
        "subject": "cypress-realworld-app", "pinned_commit": PINNED_COMMIT,
        "lead": "L9", "source_case": "L4-LIKE-NOTIFY-01",
        "source_candidate": "v2-candidate-0054",
        "business_rule": "A user can contribute at most one like to a transaction.",
        "interpretation": "A successful repeated request alone is not a bug; duplicate persisted likes from the same user are the criterion.",
        "independent_reproduction": "Plain urllib HTTP only; no Testimony code, LLM calls, injected faults, or frozen-result edits.",
        "credential_recording": "Passwords and credential fields are redacted; cookies and authentication headers are not recorded.",
        "base_url": args.base_url, "started_at_utc": now(),
        "python_version": platform.python_version(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "requested_rounds": args.rounds, "arms": [],
    }
    try:
        for round_number in range(1, args.rounds + 1):
            for arm in ("same_user_twice", "two_users_once_each"):
                record = execute_arm(evidence, round_number, arm)
                result["arms"].append(record)
                print(json.dumps({"round": round_number, "arm": arm,
                                  "counts": [x["count"] for x in record["observations"]],
                                  "verdict": record["verdict"]}), flush=True)
        treatments = [x for x in result["arms"] if x["arm"] == "same_user_twice"]
        controls = [x for x in result["arms"] if x["arm"] == "two_users_once_each"]
        result["verdict"] = (
            "BUG_REPRODUCED" if all(x["verdict"] == "BUG_REPRODUCED" for x in treatments)
            and all(x["verdict"] == "CONTROL_PASS" for x in controls)
            else "NOT_CONFIRMED"
        )
    except Exception as error:
        result["verdict"] = "INCOMPLETE"
        result["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        result["finished_at_utc"] = now()
        result["http_exchange_count"] = evidence.sequence
        with (output / "summary.json").open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    print("Final verdict:", result["verdict"], flush=True)


if __name__ == "__main__":
    main()
