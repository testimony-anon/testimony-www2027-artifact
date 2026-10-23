# D8: historical adjudication and evidence

This reading edition paraphrases selected D8 passages from the unchanged
[historical source](design/subjects-expansion-20260919/27-论文数字汇总表.md).
The line numbers below refer to that original file. The selection covers D8
reproduction, candidate associations and the historical tally; the reproduction
scope is set out separately.

Source SHA-256:

```text
0b03a30a511fd902bf012a802ca8f88c442e3c56684eeb7715413f8b64329502
```

## Historical record: 2026-09-23

| Original lines | English summary |
|---|---|
| 778 | An independent reproduction on unpatched Paperless-ngx 3.2.0 confirmed a pagination defect. The archived materials include a standalone script, 157 HTTP exchanges and a result summary. |
| 780–788 | With 61 documents and explicit `ordering=-created`, consecutive pages returned 53 distinct documents at `page_size=50` (8 duplicated and 8 omitted), and 43 at `page_size=10` or `20` (18 duplicated and 18 omitted). The response count remained 61. |
| 792, 808 | The recorded decision associates the 14 P3 candidates of `L1-DOCLIST-07` with D8, changing their final classification from IP to RD. They are repeated instances of one proposition, linked to one defect. Candidate identities are preserved in the [original adjudication](../eval/ui_semantics/refuted-review-20260923/final-adjudication-source-20260923.json). |
| 794–801, 808 | At that historical stage, the 94 refuted candidates comprised 22 defect associations, 63 candidate errors, 8 ill-posed scenarios and 1 unconfirmed lead; the catalog contained eight defects, D1–D8. |

The subsequent D9 adjudication produces the current totals: **23 defect
associations, 63 candidate errors, 8 ill-posed scenarios and 0 unconfirmed
leads; nine defects, D1–D9**. See the [current review](REFUTED-REVIEW.md) and
[final classification](../eval/ui_semantics/refuted-review-20260923/final-classifications-94.json).

## Reproduction scope

The independent experiment confirms duplicates and omissions across consecutive
pages under explicit ordering. The executed combinations were:

- `ordering=-created`: page sizes 10, 20 and 50, three rounds each.
- `ordering=created`: page size 10, three rounds.
- `ordering=id` and `ordering=-created,-id`: page size 10, three rounds each.
- Default ordering without an `ordering` parameter: page sizes 10 and 50,
  three rounds each.

The original M12 comparison concerned two first-page queries, with and without
an owner filter. In phase G, five repetitions produced identical first pages;
the original M12 same-page discrepancy was not reproduced. The 14-candidate
association follows the historical adjudication; the archived requests establish
the cross-page defect.

The original UI HAR contains first-page requests. Page-2 URLs appearing in
derived artifacts do not establish that the UI or M12 executed those requests.
The [investigation, §§5.5–5.6](../eval/ui_semantics/refuted-review-20260923/source-review-20260923.md#55-判定)
details the request provenance and evidence scope.

## Supporting records

- [Standalone reproduction script](../eval/ui_semantics/bug-leads-20260923/paperless-pagination/reproduce_paperless_pagination.py)
- [Original request/response evidence](../eval/ui_semantics/bug-leads-20260923/paperless-pagination/evidence.jsonl)
- [Reproduction summary](../eval/ui_semantics/bug-leads-20260923/paperless-pagination/summary.json)
- [Original adjudication, including the source hash and line 808](../eval/ui_semantics/refuted-review-20260923/final-adjudication-source-20260923.json)

The original source, adjudication and execution records are retained unchanged.
