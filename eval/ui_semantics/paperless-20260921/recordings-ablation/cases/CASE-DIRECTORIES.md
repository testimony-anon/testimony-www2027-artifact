# Preparing the Paperless-ngx ablation recordings

The 32 case directories listed below are selected by `../suite_manifest.json`
and are supplied here as byte-for-byte copies. The source directories remain
under `../../recordings-01/cases/`. No copying is needed for the supplied package.
Use ordinary copies rather than symbolic links when reconstructing this root,
because the suite runner requires resolved case roots to remain inside the
recording root. Offline summaries of saved results need no copies.

If reconstructing a recording root whose selected case directories are absent,
run the following command from the repository root in a working copy. It checks
the list against the saved manifest and checks all sources and destinations
before copying. It leaves the original recordings unchanged and stops if a
selected destination already exists.

```sh
python3 - <<'PYTHON'
from pathlib import Path
import json
import re
import shutil

recording_root = Path("eval/ui_semantics/paperless-20260921/recordings-ablation")
source_cases = recording_root.parent / "recordings-01" / "cases"
target_cases = recording_root / "cases"
case_ids = re.findall(r"^- `(L[0-9]+-[A-Z0-9-]+)`$",
                      (target_cases / "CASE-DIRECTORIES.md").read_text(), re.M)
manifest = json.loads((recording_root / "suite_manifest.json").read_text())
manifest_ids = {case["case_id"] for case in manifest["cases"]}
if len(case_ids) != 32 or len(set(case_ids)) != 32 or set(case_ids) != manifest_ids:
    raise SystemExit("Case list and manifest do not match; no directories copied.")
for case_id in case_ids:
    source = source_cases / case_id
    target = target_cases / case_id
    if not source.is_dir() or source.is_symlink():
        raise SystemExit(f"Missing source directory or symbolic link: {source}")
    if any(path.is_symlink() for path in source.rglob("*")):
        raise SystemExit(f"Source contains a symbolic link: {source}")
    if target.exists() or target.is_symlink():
        raise SystemExit(f"Destination already exists: {target}")
for case_id in case_ids:
    shutil.copytree(source_cases / case_id, target_cases / case_id)
PYTHON
```

## Selected case directories

- `L1-DASHBOARD-01`
- `L1-DASHBOARD-02`
- `L1-DASHBOARD-03`
- `L1-DASHBOARD-04`
- `L1-DASHBOARD-05`
- `L1-DOCDETAIL-01`
- `L1-DOCDETAIL-02`
- `L1-DOCDETAIL-03`
- `L1-DOCDETAIL-04`
- `L1-DOCDETAIL-05`
- `L1-DOCLIST-03`
- `L1-DOCLIST-05`
- `L1-DOCLIST-06`
- `L1-DOCLIST-07`
- `L1-DOCLIST-08`
- `L1-PERMISSIONS-01`
- `L1-PERMISSIONS-02`
- `L1-PERMISSIONS-03`
- `L1-PERMISSIONS-04`
- `L1-PERMISSIONS-05`
- `L1-PERMISSIONS-06`
- `L1-PERMISSIONS-07`
- `L1-PERMISSIONS-08`
- `L1-SETTINGS-01`
- `L1-SETTINGS-02`
- `L1-SETTINGS-03`
- `L2-DOCEDIT-01`
- `L2-DOCEDIT-02`
- `L2-DOCEDIT-03`
- `L3-SHARING-01`
- `L3-SHARING-02`
- `L3-SHARING-03`
