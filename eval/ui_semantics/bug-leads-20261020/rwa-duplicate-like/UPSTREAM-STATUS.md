# Upstream status of duplicate transaction likes

Checked on **2026-10-20** (America/Denver) against
[cypress-io/cypress-realworld-app](https://github.com/cypress-io/cypress-realworld-app).
The inspected default branch is `develop`, at commit
[`0729f68ac220f7cda4ad09c5693dba11d7c532c6`](https://github.com/cypress-io/cypress-realworld-app/commit/0729f68ac220f7cda4ad09c5693dba11d7c532c6)
(commit date: 2026-10-07 UTC).

**Status: a related UI fix was merged in PR #112; the API-side check for
duplicate likes by the same user on the same transaction is still absent
from the inspected default-branch source.**

## Historical issue and fix

[Issue #111](https://github.com/cypress-io/cypress-realworld-app/issues/111)
included a task to prevent repeated likes on the transaction detail page.
It was closed by [PR #112](https://github.com/cypress-io/cypress-realworld-app/pull/112),
merged on 2020-02-13.

The like-specific [commit `843b637`](https://github.com/cypress-io/cypress-realworld-app/commit/843b637900fbb54ba25675ce112e4e45a47d67bd)
changes the transaction detail component, a utility, and the utility's tests.
It disables the like button when the current user has already liked the
transaction. It adds no duplicate check to the like API route or storage
function. The enclosing PR also changes unrelated backend payment logic;
those changes do not add a duplicate-like check.

Thus, the historical issue is closed and its UI fix is merged, while the
backend behavior investigated as D9 remains present in the inspected source.

## Current source inspection

| Source at the inspected commit | Finding |
|---|---|
| [`backend/database.ts`, lines 608–643](https://github.com/cypress-io/cypress-realworld-app/blob/0729f68ac220f7cda4ad09c5693dba11d7c532c6/backend/database.ts#L608-L643) | A new like receives a new ID and is appended to storage. The creation path does not check for an existing `(userId, transactionId)` pair. |
| [`backend/like-routes.ts`, lines 26–37](https://github.com/cypress-io/cypress-realworld-app/blob/0729f68ac220f7cda4ad09c5693dba11d7c532c6/backend/like-routes.ts#L26-L37) | The authenticated POST route calls `createLikes` and returns HTTP 200, without a duplicate-like check. |
| [`src/components/TransactionDetail.tsx`, lines 178–185](https://github.com/cypress-io/cypress-realworld-app/blob/0729f68ac220f7cda4ad09c5693dba11d7c532c6/src/components/TransactionDetail.tsx#L178-L185) | The UI disables the button according to `currentUserLikesTransaction`. |
| [`src/utils/transactionUtils.ts`, lines 130–137](https://github.com/cypress-io/cypress-realworld-app/blob/0729f68ac220f7cda4ad09c5693dba11d7c532c6/src/utils/transactionUtils.ts#L130-L137) | The helper detects whether the current user already has a like on that transaction. |

All four files have the same SHA-256 hashes as the corresponding files in
the pinned reproduction commit,
`bdf6169232b919d9618ec29032addbd865f986cd`. The runtime evidence remains
the pinned-version [reproduction summary](summary.json) and
[HTTP records](evidence.jsonl). Current upstream status is established by
the source inspection above.

## September 2026 cutoff

The reproduction and original upstream investigation were conducted on
2026-10-20. A retrospective source check on 2026-10-22 verifies the
September 2026 cutoff status.

The latest commit in the inspected `develop` history as of
2026-09-30 23:59:59 UTC is
[`9dfcb9869533ce8a8963c556facc0d80457f9d39`](https://github.com/cypress-io/cypress-realworld-app/commit/9dfcb9869533ce8a8963c556facc0d80457f9d39)
(commit date: 2026-09-29 UTC). The four relevant files have these SHA-256
hashes, identical to those in the pinned reproduction version and the
October snapshot recorded in [the original investigation](upstream-check-20261020.json):

| Source at the September cutoff | SHA-256 |
|---|---|
| [`backend/database.ts`](https://github.com/cypress-io/cypress-realworld-app/blob/9dfcb9869533ce8a8963c556facc0d80457f9d39/backend/database.ts) | `31abf78ad783723d364086ab52755b8ed9ce20d9a28764e15c95118a48e142e9` |
| [`backend/like-routes.ts`](https://github.com/cypress-io/cypress-realworld-app/blob/9dfcb9869533ce8a8963c556facc0d80457f9d39/backend/like-routes.ts) | `9a29aa1abcf3584db249ef345d531552d039da43ae8265f3b5afb35a053cd9e7` |
| [`src/components/TransactionDetail.tsx`](https://github.com/cypress-io/cypress-realworld-app/blob/9dfcb9869533ce8a8963c556facc0d80457f9d39/src/components/TransactionDetail.tsx) | `70767aeb20d67fb8caba3526a56cf00a6fefdfce6d89a28b5b269967dc8799ce` |
| [`src/utils/transactionUtils.ts`](https://github.com/cypress-io/cypress-realworld-app/blob/9dfcb9869533ce8a8963c556facc0d80457f9d39/src/utils/transactionUtils.ts) | `6a3c0b0ca268fa123bc30d5fec677b13b8377ff4a2bfea4c87cc1e1bfcdc829c` |

PR #112 was merged in 2020, and its merge commit is an ancestor of this
September snapshot. The UI disables repeated likes, while the API route
and storage function still lack a check for an existing
`(userId, transactionId)` pair. This supports the September cutoff status:
**UI fix merged; API-side duplicate-like check absent.** The runtime
evidence remains the 2026-10-20 reproduction on the pinned commit, linked
above.

## Issue and pull request searches

GitHub REST searches covered titles and bodies of both open and closed
issues and pull requests in this repository. All returned
`incomplete_results: false`, and each result set fit within one page.

| Search terms after the repository and `in:title,body` filters | Results |
|---|---:|
| `likes` | 11 |
| `"duplicate likes"` | 0 |
| `"multiple likes"` | 1 |
| `"POST /likes"` | 3 |
| `"same user" "like"` | 0 |
| `"like" "idempotent"` | 0 |

The related duplicate-like record is #111. Issues #9 and #65 describe the
original like feature. Issues #403, #1332 and #1666 concern test flakiness;
PR #1710 is an unmerged flakiness demonstration. These records do not
provide a backend duplicate-like fix. No separate backend fix was identified
in the recorded searches.

[Machine-readable investigation record](upstream-check-20261020.json)
contains the exact queries, result metadata, issue/PR status, commit IDs,
source links and file hashes.
