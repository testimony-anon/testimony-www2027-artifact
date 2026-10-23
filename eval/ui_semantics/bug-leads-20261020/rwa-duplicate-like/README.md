# Independent reproduction of duplicate transaction likes

## Scope and result

This reproduces lead L9 from the frozen candidate
`rwa/L4-LIKE-NOTIFY-01/v2-candidate-0054`. It is a separate plain-HTTP
experiment, without Testimony pipeline code, model calls, or injected faults.
The reproduction run itself does not alter frozen M12 verdicts or initial
review labels. The subsequent [2026-10-20 adjudication](../../refuted-review-20260923/final-adjudication-source-20261020.json)
associates this candidate with confirmed defect D9 in the [current final classification](../../refuted-review-20260923/final-classifications-94.json).

Subject: `cypress-io/cypress-realworld-app`, pinned commit
`bdf6169232b919d9618ec29032addbd865f986cd`, with unmodified application
business source. Runtime: Node.js 22.22.1 and Python 3.12; the exact Python
version and source-file hashes are recorded in `summary.json`.

All three treatment rounds reproduced the same outcome: one user sent two
identical `POST /likes/:transactionId` requests, both returned HTTP 200, and
the newly created transaction's stored likes increased from 0 to 1 to 2.
The two records have distinct like IDs but the same user ID and transaction
ID. This violates the rule that one user contributes at most one like to a
transaction. The pinned UI expresses this rule by disabling the like button
once `currentUserLikesTransaction` is true.

In three control rounds, two different users each liked a fresh transaction
once. Both requests succeeded, producing two records with distinct user IDs
and exactly one record per user. The experiment used six successful seed
resets and six fresh transaction IDs, with 54 recorded HTTP exchanges.

The defect criterion is an additional persisted like by the same user.
Successful idempotent handling would keep a single like record.

## Upstream status

Checked on 2026-10-20: issue #111 was closed by merged PR #112, whose
like-specific fix disables the UI button after a user has liked the
transaction. The backend still lacks a check for an existing like by that
user on that transaction at the inspected default-branch commit
`develop@0729f68ac220f7cda4ad09c5693dba11d7c532c6`. All four relevant source
files match the pinned reproduction version byte for byte. See the
[upstream investigation](UPSTREAM-STATUS.md) for issue/PR links, the fix's
scope, source inspection and search results.

A retrospective source check on 2026-10-22 also verifies the
[September 2026 cutoff status](UPSTREAM-STATUS.md#september-2026-cutoff):
the four relevant files at commit `9dfcb986` (2026-09-29) match the pinned
reproduction version. The reproduction and original upstream investigation
remain dated 2026-10-20.

## Files

- `reproduce_rwa_duplicate_likes.py`: standalone Python standard-library client.
- `evidence.jsonl`: each request and response, with round, arm, actor and step.
- `summary.json`: source provenance, observations, verdicts and cleanup checks.
- `UPSTREAM-STATUS.md`: historical issue/fix status and current source findings.
- `upstream-check-20261020.json`: dated queries, issue/PR metadata and source hashes.

Passwords and credential fields are redacted; cookies and authentication
headers are not stored. Accounts are the subject's synthetic seed accounts.

## Reproduce

Use a disposable checkout of the pinned subject, Node.js 22 and its installed
dependencies. Do not point the client at a running scientific experiment:
the script resets the database before each treatment and control arm.

Prepare the standard mock AWS configuration supplied by that pinned commit:

```sh
yarn copy:mock:awsexports
```

Start only the backend from the subject checkout, with cloud-authentication
options unset:

```sh
NODE_ENV=development PORT=14100 VITE_BACKEND_PORT=14101 PAGINATION_PAGE_SIZE=10 \
  node node_modules/ts-node/dist/bin.js -P tsconfig.tsnode.json --files backend/app.ts
```

In another terminal, run the included client with a new output directory:

```sh
python3 reproduce_rwa_duplicate_likes.py \
  --base-url http://127.0.0.1:14101 \
  --output-dir /tmp/rwa-duplicate-like-new-run --rounds 3
```

The default password is the subject's public local-test default. It can be
provided through `RWA_SEED_PASSWORD`. The output directory must not exist,
so a re-run cannot overwrite the evidence shipped here.

For this execution, the application was exported from the pinned Git commit
into an isolated directory. A launcher restricted its listener to loopback;
this affected socket binding only. The mock AWS file was copied verbatim
from the pinned project's `scripts/mock-aws-exports.js`; cloud authentication
was disabled. Application business-source hashes were unchanged after the
run. The backend was stopped after the run.
