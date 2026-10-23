# UISemTest exported pytest suite

This directory contains 44 retained tests: 3 business assertions and 41
structural constraints, as recorded in `business_test_catalog.json`. Its recorded
source is `rwa/flat-fix-01/cases/L1-BANK-03/union` under
`eval/ui_semantics/deepseek-ablation-20260913/` (data volume 2).
See `docs/EXPORT-FORMAT.md` in the repository.

`conftest.py` locates the frozen source relative to the package root. Set
`UISEMTEST_ARTIFACT_ROOT` to use another extracted copy of the package. Extract
data volume 2 and follow `INSTALL.md` before executing the tests. From the
repository root:

```sh
.venv/bin/python -m pytest -q eval/ui_semantics/deepseek-ablation-20260913/rwa/pytest-export-flat/L1-BANK-03
```
