# Paperless-ngx ablation recording root

This recording root selects 32 cases from `recordings-01`, excluding
`L1-DOCLIST-01`, `L1-DOCLIST-02`, and `L1-DOCLIST-04`, for the RQ3 ablation
of Paperless-ngx (2026-09-21). The selection and recorded statuses are retained
in `suite_manifest.json` and `suite_recording_result.json`.

The selected case directories are supplied as byte-for-byte copies in `cases/`.
Their original recordings remain under `../recordings-01/cases/`. No copying is
needed to use the supplied recording root. If reconstructing a recording root
whose selected case directories are absent, follow the
[32-case list and reconstruction instructions](cases/CASE-DIRECTORIES.md) in a
working copy. Use ordinary copies rather than symbolic links: the suite runner
resolves case roots and requires them to remain inside this recording root.
The instructions leave `recordings-01` unchanged and refuse to overwrite an
existing destination.

Reading the saved results or recomputing offline summaries does not require
this preparation step.
