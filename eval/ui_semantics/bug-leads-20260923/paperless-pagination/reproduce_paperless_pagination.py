"""Controlled reproduction of the Paperless-ngx pagination lead (task brief 41).

Lead (doc 40 section 2, group P3): `Document.created` is a day-granular
DateField and `Meta.ordering = ("-created",)` carries no secondary key, so the
61 seeded documents occupy only 3 distinct sort keys.  The question this script
answers with evidence, not with reasoning:

  * does the SAME query, repeated, return the same first page?
  * does a user who pages through the list with `ordering=-created` see every
    document exactly once (union == the whole result set, no duplicates)?
  * does a total-order key (`ordering=id`) behave differently (control)?
  * does the API accept a multi-key ordering such as `-created,-id`?
  * the exact M12 query pair of L1-DOCLIST-07 (with / without `owner__id__in=2`).
  * does the IMPLICIT default ordering (no `ordering` parameter at all) behave
    differently from the explicit `ordering=-created`?  The pinned version
    already carries upstream PR #12440, which appended `-id` to the queryset's
    own `.order_by(...)` in `DocumentViewSet.get_queryset` (views.py:1215), but
    DRF's OrderingFilter REPLACES that ordering when the client sends
    `ordering=`, so the two paths must be measured separately.

Runs against the pinned deployment (`deploy/paperless/README.md`), version
3.2.0, image digest sha256:22dc423f..., no fault patch applied.
Plain HTTP through urllib, no UISemTest pipeline code, no LLM.
Every request is appended to evidence.jsonl; the verdict inputs go to
summary.json.  Credentials are read from the environment and never written out.

Usage (from the repository root, with .env sourced):
    .venv/bin/python eval/ui_semantics/bug-leads-20260923/paperless-pagination/\
reproduce_paperless_pagination.py
"""

from __future__ import annotations

import http.cookiejar
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

BASE = os.environ.get("PAPERLESS_BASE_URL", "http://127.0.0.1:18091")
OUT = Path(__file__).resolve().parent
EVIDENCE = OUT / "evidence.jsonl"
SUMMARY = OUT / "summary.json"

# The exact query-string shape L1-DOCLIST-07 used in M12 (doc 40 section 2, P3),
# minus page/page_size/ordering which each phase sets itself.
M12_EXTRA = {"include_selection_data": "true", "truncate_content": "true"}

_seq = 0


class Session:
    """Cookie-jar session with the double-submit CSRF the profile declares."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
        )

    def cookie(self, name: str) -> str | None:
        for c in self.jar:
            if c.name == name:
                return c.value
        return None

    def call(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        body: dict | None = None,
        note: str = "",
        phase: str = "",
        record_body: bool = False,
    ) -> tuple[int, object]:
        global _seq
        _seq += 1
        url = BASE + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        token = self.cookie("csrftoken")
        if token and method != "GET":
            headers["X-CSRFToken"] = token
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        started = time.time()
        try:
            with self.opener.open(req, timeout=60) as resp:
                status = resp.status
                raw = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            status = exc.code
            raw = exc.read().decode("utf-8", "replace")
        elapsed = round((time.time() - started) * 1000, 1)
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = None
        record = {
            "seq": _seq,
            "phase": phase,
            "actor": self.label,
            "method": method,
            "url": url[len(BASE):],
            "status": status,
            "elapsed_ms": elapsed,
            "note": note,
            "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        if isinstance(parsed, dict) and "results" in parsed:
            results = parsed.get("results") or []
            record["count"] = parsed.get("count")
            record["page_len"] = len(results)
            record["result_ids"] = [d.get("id") for d in results]
            record["result_created"] = [d.get("created") for d in results]
            all_ids = parsed.get("all")
            record["all_len"] = len(all_ids) if isinstance(all_ids, list) else None
            record["all_ids"] = all_ids if isinstance(all_ids, list) else None
            record["next"] = parsed.get("next")
        elif record_body:
            record["response"] = parsed if parsed is not None else raw[:500]
        else:
            record["response_kind"] = type(parsed).__name__
        with EVIDENCE.open("a") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return status, parsed


def login(label: str, user_env: str, pass_env: str) -> Session:
    s = Session(label)
    # Priming GET: Django serves the login page and sets the csrftoken cookie.
    s.call("GET", "/accounts/login/", note="prime csrftoken cookie", phase="login")
    username = os.environ[user_env]
    password = os.environ[pass_env]
    status, body = s.call(
        "POST",
        "/api/auth/headless/browser/v1/auth/login",
        body={"username": username, "password": password},
        note="cookie_session login (credentials from env, not logged)",
        phase="login",
    )
    if status not in (200, 401):
        raise SystemExit(f"login failed: HTTP {status}")
    status, _ = s.call("GET", "/api/profile/", note="identity probe", phase="login")
    if status != 200:
        raise SystemExit(f"identity probe failed: HTTP {status}")
    return s


def page(
    s: Session,
    phase: str,
    ordering: str | None,
    page_no: int,
    page_size: int,
    note: str,
    extra: dict | None = None,
) -> dict:
    params = {
        **({"ordering": ordering} if ordering is not None else {}),
        "page": page_no,
        "page_size": page_size,
        **M12_EXTRA,
        **(extra or {}),
    }
    status, body = s.call("GET", "/api/documents/", params=params, note=note, phase=phase)
    if status != 200 or not isinstance(body, dict):
        raise SystemExit(f"{phase}: HTTP {status}")
    return {
        "count": body.get("count"),
        "ids": [d.get("id") for d in body.get("results") or []],
        "created": [d.get("created") for d in body.get("results") or []],
        "all": body.get("all"),
    }


def sweep(s: Session, phase: str, ordering: str | None, page_size: int, total: int, rnd: int,
          extra: dict | None = None) -> dict:
    """One user-style pass: request page 1, 2, ... until the set is covered."""
    pages = (total + page_size - 1) // page_size
    seen: list[int] = []
    per_page = []
    for p in range(1, pages + 1):
        res = page(s, phase, ordering, p, page_size,
                   f"round {rnd} page {p}/{pages} (page_size={page_size}, ordering={ordering})",
                   extra)
        per_page.append(res["ids"])
        seen.extend(res["ids"])
    counts = Counter(seen)
    duplicates = sorted([i for i, n in counts.items() if n > 1])
    missing = sorted(set(range(1, total + 1)) - set(seen)) if total else []
    return {
        "round": rnd,
        "ordering": ordering,
        "page_size": page_size,
        "pages": pages,
        "per_page_ids": per_page,
        "seen_total": len(seen),
        "distinct_seen": len(counts),
        "duplicate_ids": duplicates,
        "duplicate_pairs": {str(i): counts[i] for i in duplicates},
        "missing_ids": missing,
    }


def main() -> int:
    EVIDENCE.write_text("")
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    s = login("actor_a", "UISEMTEST_PAPERLESS_ACTOR_A_USERNAME",
              "UISEMTEST_PAPERLESS_ACTOR_A_PASSWORD")

    out: dict[str, object] = {
        "base_url": BASE,
        "subject": "paperless-ngx 3.2.0 (image digest sha256:22dc423f...), no fault patch",
        "started_at": started,
        "lead": (
            "documents are ordered by the day-granular `created` DateField with no "
            "secondary sort key, so repeated queries and successive pages of the "
            "same ordering may disagree"
        ),
    }

    # --- phase A: census of the golden state ---------------------------------
    census = page(s, "A_census", "-created", 1, 100000, "full result set, one page")
    dates = Counter(census["created"])
    total = census["count"]
    out["A_census"] = {
        "count": total,
        "page_len": len(census["ids"]),
        "distinct_created_dates": len(dates),
        "created_histogram": dict(sorted(dates.items())),
        "ids_sorted": sorted(census["ids"]),
    }

    # --- phase B: is the SAME first page stable under repetition? ------------
    repeats = 12
    b_pages = []
    for i in range(1, repeats + 1):
        res = page(s, "B_repeat_page1", "-created", 1, 50, f"repeat {i}/{repeats}")
        b_pages.append(res["ids"])
    b_sets = [frozenset(p) for p in b_pages]
    out["B_repeat_page1"] = {
        "repeats": repeats,
        "page_size": 50,
        "distinct_orders": len({tuple(p) for p in b_pages}),
        "distinct_member_sets": len(set(b_sets)),
        "first_page_ids": b_pages[0],
        "all_identical_order": len({tuple(p) for p in b_pages}) == 1,
        "all_identical_members": len(set(b_sets)) == 1,
    }

    # --- phase C/D: a user pages through the list ----------------------------
    for page_size in (10, 20, 50):
        rounds = []
        for rnd in range(1, 4):
            rounds.append(sweep(s, f"C_sweep_ps{page_size}", "-created", page_size, total, rnd))
        out[f"C_sweep_page_size_{page_size}"] = {
            "rounds": rounds,
            "any_duplicate": any(r["duplicate_ids"] for r in rounds),
            "any_missing": any(r["missing_ids"] for r in rounds),
        }

    # --- phase E: control, a total-order key ---------------------------------
    e_rounds = [sweep(s, "E_control_id", "id", 10, total, rnd) for rnd in (1, 2, 3)]
    out["E_control_ordering_id"] = {
        "rounds": e_rounds,
        "any_duplicate": any(r["duplicate_ids"] for r in e_rounds),
        "any_missing": any(r["missing_ids"] for r in e_rounds),
    }

    # --- phase F: does the API accept a multi-key ordering? ------------------
    f_params = {"ordering": "-created,-id", "page": 1, "page_size": 50, **M12_EXTRA}
    f_status, f_body = s.call("GET", "/api/documents/", params=f_params,
                              note="multi-key ordering accepted?", phase="F_multikey")
    f_ok = f_status == 200 and isinstance(f_body, dict)
    f_rounds = []
    if f_ok:
        f_rounds = [sweep(s, "F_multikey", "-created,-id", 10, total, rnd) for rnd in (1, 2, 3)]
    out["F_multikey_ordering"] = {
        "status": f_status,
        "accepted": f_ok,
        "first_page_ids": [d.get("id") for d in (f_body or {}).get("results", [])] if f_ok else None,
        "rounds": f_rounds,
        "any_duplicate": any(r["duplicate_ids"] for r in f_rounds) if f_rounds else None,
        "any_missing": any(r["missing_ids"] for r in f_rounds) if f_rounds else None,
    }

    # --- phase G: the exact M12 pair of L1-DOCLIST-07 ------------------------
    g = []
    for rnd in (1, 2, 3, 4, 5):
        src = page(s, "G_m12_pair", "-created", 1, 50, f"round {rnd} source_query (no owner filter)")
        q1 = page(s, "G_m12_pair", "-created", 1, 50, f"round {rnd} followup_query q1 (owner__id__in=2)",
                  extra={"owner__id__in": "2"})
        left, right = set(q1["ids"]), set(src["ids"])
        g.append({
            "round": rnd,
            "source_count": src["count"],
            "q1_count": q1["count"],
            "subset_holds": left <= right,
            "intersection": len(left & right),
            "q1_only": sorted(left - right),
            "source_only": sorted(right - left),
        })
    out["G_m12_pair"] = {
        "rounds": g,
        "subset_ever_holds": any(r["subset_holds"] for r in g),
        "subset_always_holds": all(r["subset_holds"] for r in g),
    }

    # --- phase H: the IMPLICIT default ordering (no `ordering` parameter) ----
    # PR #12440 appended `-id` to DocumentViewSet.get_queryset's own order_by;
    # DRF's OrderingFilter replaces that ordering whenever `ordering=` is sent,
    # so this path and phase C measure two different code paths.
    h = {}
    for page_size in (10, 50):
        rounds = [sweep(s, f"H_default_ps{page_size}", None, page_size, total, rnd)
                  for rnd in (1, 2, 3)]
        h[f"page_size_{page_size}"] = {
            "rounds": rounds,
            "any_duplicate": any(r["duplicate_ids"] for r in rounds),
            "any_missing": any(r["missing_ids"] for r in rounds),
            "first_page_ids": rounds[0]["per_page_ids"][0],
        }
    out["H_implicit_default_ordering"] = h

    # --- phase I: explicit ascending `ordering=created` -----------------------
    i_rounds = [sweep(s, "I_explicit_created_asc", "created", 10, total, rnd)
                for rnd in (1, 2, 3)]
    out["I_explicit_created_asc"] = {
        "rounds": i_rounds,
        "any_duplicate": any(r["duplicate_ids"] for r in i_rounds),
        "any_missing": any(r["missing_ids"] for r in i_rounds),
    }

    # --- phase J: is the `all` id list (UI "select all") complete? ------------
    j = page(s, "J_all_list", "-created", 1, 10, "page 1 of 7, inspect the `all` array")
    all_ids = j["all"] or []
    out["J_all_list"] = {
        "all_len": len(all_ids),
        "all_distinct": len(set(all_ids)),
        "all_equals_full_set": sorted(set(all_ids)) == sorted(out["A_census"]["ids_sorted"]),
    }

    out["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    SUMMARY.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items()
                      if k in ("A_census", "B_repeat_page1")}, ensure_ascii=False, indent=1))
    keys = ["C_sweep_page_size_10", "C_sweep_page_size_20", "C_sweep_page_size_50",
            "E_control_ordering_id", "F_multikey_ordering", "I_explicit_created_asc"]
    for key in list(out["H_implicit_default_ordering"]):
        v = out["H_implicit_default_ordering"][key]
        print("H_implicit_default", key, "any_duplicate=", v["any_duplicate"],
              "any_missing=", v["any_missing"])
        for r in v["rounds"]:
            print("   round", r["round"], "seen", r["seen_total"], "distinct", r["distinct_seen"],
                  "dups", r["duplicate_ids"], "missing", r["missing_ids"])
    print("J_all_list", out["J_all_list"])
    for key in keys:
        v = out[key]
        print(key, "any_duplicate=", v.get("any_duplicate"), "any_missing=", v.get("any_missing"))
        for r in v.get("rounds") or []:
            print("   round", r["round"], "seen", r["seen_total"], "distinct", r["distinct_seen"],
                  "dups", r["duplicate_ids"], "missing", r["missing_ids"])
    print("G subset_always", out["G_m12_pair"]["subset_always_holds"],
          "subset_ever", out["G_m12_pair"]["subset_ever_holds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
