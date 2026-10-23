# Testimony — reproduction package

This package accompanies the paper *Testimony: LLM-assisted API Test Carving and Assertion Generation from UI Tests*. Testimony is the paper's name for the approach; the implementation keeps its internal name — Python package `ui_semantics`, command `scripts/uisemtest`, environment variables `UISEMTEST_*`, and the names inside generated artifacts. The package contains the implementation, the 171 UI action sequences of the five subject applications and their recordings, model inputs and raw answers of the reported runs, the recorded candidate-validation evidence, the final API regression tests, the semantic-review records (RQ1), the fault catalogue with per-fault outcomes and defect reproduction scripts (RQ2), and the ablation runs (RQ3). The analysis commands below recompute the listed RQ1–RQ3 summaries from the shipped records and data volumes. Official UI-suite statistics additionally require the corresponding pinned upstream test sources; controlled defect reproductions require the subject applications.

The five subject applications and their inputs:

| Subject | Pinned version | Inputs | Deployment | Run directory |
|---|---|---:|---|---|
| Conduit | commit `5e127d8` | 38 | `deploy/conduit/` (Docker, PostgreSQL) | `eval/ui_semantics/deepseek-full-20260912/conduit/` |
| RWA (cypress-realworld-app) | commit `bdf6169` | 45 | local Node.js checkout (INSTALL.md) | `eval/ui_semantics/deepseek-full-20260912/rwa/` |
| Umami | 3.4.0, commit `ec0ff50` | 22 | `deploy/umami/` (image + separate PostgreSQL) | `eval/ui_semantics/umami-20260921/umami/` |
| Paperless-ngx | 3.2.0, commit `961f018` | 35 | `deploy/paperless/` (image + sidecars) | `eval/ui_semantics/paperless-20260921/paperless/` |
| Ghost | 5.130.6, commit `a07c753` | 31 | `deploy/ghost/` (single container, SQLite) | `eval/ui_semantics/ghost-20260921/ghost/` |

The six anonymous data volumes (the run roots with the model calls, the validation evidence and the RQ2 run evidence) are attached to [Release `v1.0-review`](https://github.com/testimony-anon/testimony-www2027-artifact/releases/tag/v1.0-review); [VOLUMES.md](VOLUMES.md) lists their download links, content and actual SHA-256 sums. [Anonymization details](docs/ANONYMIZATION.md) distinguish the distributed bytes from their historical source digests. Volumes 1–3 carry the Conduit and RWA runs, volumes 4–6 the Umami, Paperless-ngx and Ghost runs. Archives can be downloaded and extracted separately; cross-configuration analyses need both main-line and ablation material. Extract the volumes required by the chosen offline analysis or live continuation into this directory before running it.

The layout mirrors the research repository so that the analysis scripts run unchanged:

| Path | Content |
|---|---|
| `src/`, `scripts/uisemtest`, `contracts/`, `pyproject.toml` | Implementation (Python 3.12). `contracts/` holds the JSON schemas of every pipeline artifact. The research repository's unit-test suite and its subpackages that `scripts/uisemtest` does not import are not part of the package. |
| `fixtures/profiles`, `fixtures/adapters`, `fixtures/provider_configs` | Subject configuration of the five applications (test accounts via environment variables), their runtime adapters, the model configuration used by the reported runs (`deepseek_flash_current.json`). |
| `fixtures/recording_workflows/{conduit,rwa,umami,paperless,ghost}_modular/` | The 171 UI action sequences (`inventory.json` lists them per module; `origin.json` records for the three subjects whose suites carry it whether a sequence was rewritten from the application's own UI test or written by the authors). |
| `deploy/conduit/`, `deploy/umami/`, `deploy/paperless/`, `deploy/ghost/` | Deployment, reset and seed scripts of the pinned subject versions (image digests are in the adapters); RWA is a local checkout, see INSTALL.md. The scripts only ever name environment variables. |
| `eval/ui_semantics/deepseek-full-20260912/` | Conduit and RWA main-line runs that form their part of the final test suite (Section 5.1, Table 2): per subject the run roots `full-01`, `retry-01` (`rerecord-01` for RWA) hold the model calls (M10), `m11fix-01`/`m11fix-02` hold the validation and compiled tests (M11–M14); `pytest-export-final/` holds the exported pytest tests. |
| `eval/ui_semantics/{umami,paperless,ghost}-20260921/` | Per subject: `recordings-01/` (the recorded traces of its sequences), the main-line run root (`umami/full-01`, `paperless/m11fix-03` with `paperless/full-01` as its M10 source, `ghost/full-01`), `pytest-export-final/`, the launcher scripts and the suite run results. |
| `eval/ui_semantics/deepseek-ablation-20260913/` | RQ3 ablation runs of Conduit and RWA (`temporal-*`, `flat-*`), their exports and the comparison scripts. |
| `eval/ui_semantics/subjects-ablation-20260921/` | RQ3 ablation runs of Umami, Paperless-ngx and Ghost (`<subject>/{temporal-01,flat-01}`), their exports, the launcher and comparison scripts, the run locks and the machine-readable comparisons. |
| `eval/ui_semantics/rq2-deepseek-final2-20260912/`, `eval/ui_semantics/rq2-20260907/` | RQ2 data of Conduit and RWA: fault definitions (`suite/response-faults.jsonl`, `rq2-20260907/patches/` = the 42 source patches), per fault–test outcomes (`suite/outcomes-*.jsonl`), compositions, report and summary, evidence of every alarm/unknown pair (`suite/runs/`). |
| `eval/ui_semantics/rq2-subjects-20260921/` | RQ2 data of Umami, Paperless-ngx and Ghost: the fault registries and their frozen copies (`inputs/faults-<subject>.jsonl`, format in `inputs/FAULT-CATALOG-SPEC.md`), the source patches (`patches/`), per fault–test outcomes (`suite/outcomes-*.jsonl`), per-subject report and summary, evidence of every alarm/unknown pair and the whole normal-version run (`suite/runs/`), and the runner scripts. |
| `docs/FAULT-CATALOGUE.md` | RQ2 fault catalogue in English: the business rules, the seeded source faults, the injected response faults and the cross-flow compositions of all five subjects, with the identifiers used in the result files. |
| `docs/METHOD-SUPPLEMENT.md` | Supplement to Section 3 of the paper: terms, pipeline stages and modules, the 17 relation kinds and 20 predicate families with definitions, the legal relation × predicate combinations and one example each from the final test set, the 9 validation plans with examples, plan dispatch, completion statistics and the values of the bounded rules. |
| `docs/ANONYMIZATION.md`, `docs/anonymization-manifest.json` | Identity-only transformations, actual and historical source digests, and the preserved experimental records. |
| `docs/RUN-NOTES.md` | Environment, the code commit of every run root, parameters, wall-clock time, token usage, the engineering repairs made during the study, and the mechanism of the RQ2 runs. |
| `docs/REVIEW-ADJUDICATIONS.md` | RQ1 review: the two assertion layers, the adjudication rules A/B/C of the business relations and every decision per suite, and the criterion, the groups of adjudicated items and the results of the structural-constraint review (Section 4.4). |
| `docs/DEFECTS.md` | Controlled reproduction of the nine confirmed application defects D1–D9, including the existing D8 pagination evidence and the independent D9 duplicate-like reproduction. |
| `docs/D8-ADJUDICATION-SOURCE-EXCERPT.md` | D8 reading edition: source SHA-256 and original line references, historical adjudication and archived reproduction scope. |
| `docs/REFUTED-REVIEW.md` | Current final classification of all 94 refuted candidates: 23 linked to confirmed defects, 63 candidate errors, 8 ill-posed scenarios and 0 unconfirmed leads. The original 57-candidate Conduit/RWA review is preserved as a historical section. |
| `docs/ABLATION-RESULTS.md` | RQ3: the three-configuration tables of all five subjects, the evidence-citation statistics, the paired comparisons and run provenance (Table 6, Section 5.3). |
| `eval/ui_semantics/bug-leads-20260912/` | Original reproduction scripts and step-by-step evidence of D1–D7, preserved unchanged. |
| `eval/ui_semantics/bug-leads-20260923/paperless-pagination/` | Existing D8 reproduction script, original request/response evidence and summary. |
| `eval/ui_semantics/bug-leads-20261020/rwa-duplicate-like/` | Independent D9 reproduction: script, 54 request/response records, summary, fixed-version provenance and instructions; three treatment and three control rounds. |
| `eval/ui_semantics/refuted-review-20260923/final-classifications-94.json` | Current combined final classification, with original labels retained and separate D8/D9 adjudication sources. |
| `docs/design/cpv-expansion/rq1-audit-deepseek*/` | RQ1 semantic review of the Conduit/RWA suites: review packets (`tests.jsonl`), initial labels with one-line rationale (`reviews.jsonl`), author adjudications (`main-review.jsonl`; written up in `docs/REVIEW-ADJUDICATIONS.md`), merged labels (`tests-labeled.jsonl`), semantic groups, primary-effect checklist results (`targets.jsonl`), summaries. The Full directory also holds the review of the structural constraints (`structural-reviews.jsonl`, `structural-summary.md`, `structural-review-failures.jsonl`, `structural-main-review.jsonl`, `structural-labels-final.jsonl`). `rq1-audit/scopes.jsonl` is the per-sequence list of primary effects and `rq1-audit/tests.jsonl` the labelled tests of the earlier round of the study, reduced to the fields the summariser reads. |
| `docs/design/subjects-expansion-20260919/rq1-audit-{umami,paperless,ghost}{,-temporal,-flat}/` | RQ1 semantic review of the Umami, Paperless-ngx and Ghost suites, same file set; the three Full directories also hold the `structural-*` files of the structural-constraint review. The per-sequence effect lists of these three subjects are `docs/design/cpv-expansion/rq1-audit-{umami,paperless,ghost}/scopes.jsonl`; `docs/RUN-NOTES.md` describes the scope of this supplementary primary-target analysis. |
| `docs/design/cpv-expansion/*.md`, `docs/design/subjects-expansion-20260919/rq3-*.md` | The generated RQ3 comparison tables (`rq3-*-comparison.md`, `rq3-evidence-dependence-*.md`). |

The free-text fields of the original audit data (effect lists, adjudication reasons and evidence notes, the coverage rationale in `targets.jsonl`, the notes in `refuted-review-final.json`) were written in Chinese during the study and were translated into English for this package; translation did not change their labels, codes or counts. Subsequent D8 and D9 adjudications are separate records linked from [the current final review](docs/REFUTED-REVIEW.md). They update the derived final classification while preserving the original reviews and frozen execution outcomes.

## Three levels of reproduction

1. **Inspect records and recompute the listed RQ1–RQ3 summaries offline.** Extract the required volumes first; these summaries need neither model calls nor subject deployment. See [Recorded results and analysis commands](#recorded-results-and-analysis-commands).
2. **Re-run validation and the final tests without model calls.** Prepare the subject dependencies as described in [INSTALL.md](INSTALL.md), then run an exported pytest suite or continue a frozen M10 output through M11–M14. The runtime manages the application lifecycle; separate data-layer preparation is described per subject.
3. **Run the method from saved UI recordings, including model calls.** Uses the configured model endpoint and key; model answers are not bit-reproducible. Fresh UI recording is a separate operation.

## Recorded results and analysis commands

Run `python3 scripts/relocate.py` once on a working copy after extracting the required volumes; it rewrites the relocatable placeholders to local paths. All commands below run from the package root and use the virtual environment in [INSTALL.md](INSTALL.md). RQ1/RQ3 summaries read saved records without model calls. The table also identifies source-file inspection and defect evidence, which are separate from these offline summaries.

| Paper | Command | Output |
|---|---|---|
| Table 1 input counts; accompanying input classifications | `fixtures/recording_workflows/*_modular/inventory.json` and `origin.json`; API/mixed/UI-only classes in `docs/design/cpv-expansion/rq1-audit{,-umami,-paperless,-ghost}/scopes.jsonl` | — |
| Section 4.2 assertion statistics of the applications' own UI suites | Command syntax: `.venv/bin/python scripts/experiments/subject_survey/cypress_assertion_stats.py --root <pinned-upstream-checkout> --glob '<recorded-spec-glob>' --framework <framework>`; `--help` lists parameters. Use the recorded source revision, spec selection, framework and custom-command options. | stdout; requires the upstream test sources |
| Section 5.1 funnel numbers and Table 2, Conduit and RWA | `.venv/bin/python eval/ui_semantics/deepseek-full-20260912/rq1_summarize_deepseek.py pytest-export-final` | `docs/design/cpv-expansion/rq1-audit-deepseek/summary.md` |
| Section 5.1 funnel numbers and Table 2, one of Umami / Paperless-ngx / Ghost | `.venv/bin/python scripts/experiments/rq1_tools/rq1_summarize_deepseek.py --config scripts/experiments/rq1_tools/configs/<subject>-20260921.json` | `docs/design/subjects-expansion-20260919/rq1-audit-<subject>/summary.md` |
| Initial structural-review summary (offline; no model key) | `.venv/bin/python scripts/experiments/rq1_tools/rq1_review_structural.py --config scripts/experiments/rq1_tools/configs/<subject>-20260921.json --summarize` reads the shipped initial review labels. Final Full-suite labels are in `structural-labels-final.jsonl`; see [review coverage](docs/REVIEW-ADJUDICATIONS.md). | `docs/design/.../rq1-audit-<subject>/structural-summary.md` |
| Read-back-after-write analysis | `.venv/bin/python scripts/experiments/subjects/readback_after_write.py 'eval/ui_semantics/ghost-20260921/ghost/full-01/cases/*/union'` (one glob of case union directories per subject) | stdout |
| Table 3 and the composition results of Section 5.2 (Conduit, RWA) | `UISEMTEST_RQ2_ROOT=$PWD/eval/ui_semantics/rq2-deepseek-final2-20260912/suite UISEMTEST_RQ2_LEGACY=$PWD/eval/ui_semantics/rq2-deepseek-final2-20260912/inputs UISEMTEST_RQ2_RWA_SOURCE=run PYTHONPATH=src .venv/bin/python -m ui_semantics.rq2_evaluation summarize` | `.../suite/report.md`, `.../suite/summary.json` |
| Table 3 rows of Umami / Paperless-ngx / Ghost | `UISEMTEST_RQ2_ROOT=$PWD/eval/ui_semantics/rq2-subjects-20260921/suite UISEMTEST_RQ2_LEGACY=$PWD/eval/ui_semantics/rq2-subjects-20260921/inputs PYTHONPATH=src .venv/bin/python scripts/experiments/rq2_subjects/rq2_subjects.py summarize --subject <subject>` | `.../suite/report-<subject>.md`, `.../suite/summary-<subject>.json` |
| Fault definitions of Table 3 | `docs/FAULT-CATALOGUE.md` (regenerated by `scripts/artifact/make_fault_catalogue.py`) | — |
| Confirmed application defects | `docs/DEFECTS.md`; original D1–D7 evidence in `eval/ui_semantics/bug-leads-20260912/`, D8 in `eval/ui_semantics/bug-leads-20260923/paperless-pagination/`, and D9 in `eval/ui_semantics/bug-leads-20261020/rwa-duplicate-like/` | Nine confirmed defects; current candidate counts and their sources are in `eval/ui_semantics/refuted-review-20260923/final-classifications-94.json` |
| Table 6, Conduit and RWA | `.venv/bin/python eval/ui_semantics/deepseek-ablation-20260913/ablation_compare.py temporal docs/design/cpv-expansion/rq1-audit-deepseek-temporal eval/ui_semantics/deepseek-ablation-20260913 temporal-retry-02,temporal-01` (and `flat … flat-fix-01,flat-retry-01,flat-01`); the RQ1 summaries of the ablation suites: `DEEPSEEK_RUNS_ROOT=eval/ui_semantics/deepseek-ablation-20260913 RQ1_AUDIT_DIR=docs/design/cpv-expansion/rq1-audit-deepseek-temporal .venv/bin/python eval/ui_semantics/deepseek-full-20260912/rq1_summarize_deepseek.py pytest-export-temporal` | `docs/design/cpv-expansion/rq3-*-comparison.md`, `…/rq1-audit-deepseek-*/summary.md` |
| Table 6, Umami / Paperless-ngx / Ghost | `.venv/bin/python eval/ui_semantics/subjects-ablation-20260921/ablation_compare_subjects.py temporal` (and `flat`); RQ1 summaries: `.venv/bin/python scripts/experiments/rq1_tools/rq1_summarize_deepseek.py --config scripts/experiments/rq1_tools/configs/<subject>-ablation-temporal.json` (use `<subject>-ablation-flat.json` for Flat). | `docs/design/subjects-expansion-20260919/rq3-*-comparison.md`, `…/rq1-audit-<subject>-*/summary.md` |
| Additional RQ3 analysis: strata by validation plan, counts across UI actions and evidence-citation ratios | `.venv/bin/python eval/ui_semantics/deepseek-ablation-20260913/evidence_dependence.py` with `DEP_CONFIG` set to `full`, `temporal` or `flat` (see the script header for the run-root variables) | `docs/design/cpv-expansion/rq3-evidence-dependence-*.md` |
| Token usage accompanying Section 4.3; details in RUN-NOTES.md | `.venv/bin/python scripts/artifact/usage_by_config.py` | stdout |

Reported results are collected in `docs/ABLATION-RESULTS.md` (RQ3), `docs/FAULT-CATALOGUE.md` (RQ2 definitions) and `docs/RUN-NOTES.md` (runs and parameters). `scripts/selfcheck_l1.sh` regenerates and compares configured RQ1 summaries, RQ3 comparison JSON files and RQ2 reports for the five subjects. It relocates paths and writes derived outputs; run it on a working copy after extracting all six volumes. Some RQ1 entries are skipped when their configuration or existing summary is absent. Official-suite source statistics, final structural-label adjudication, functional-point mappings and live defect reproductions are outside this check.

Directories with a `.stale-export-*` suffix retain historical exports; they are not additional input sequences. Reported summaries use the saved audit inputs and the documented run precedence rather than the sum of every export directory.

For the official-suite survey, the available `origin.json` files identify the upstream test revisions and source locations. Obtain those sources separately and use the original analysis scope; the generic syntax above alone does not specify every subject's original survey command. For Paperless-ngx, distinguish the official UI-test source revision in `origin.json` from the deployed image revision in the subject table.

`eval/ui_semantics/subjects-ablation-20260921/run_rq1_ablation.sh` is a research export/extract/review/summarize workflow. It enters the model-review tool and can append review records; use the direct summarizer above for offline checks. Likewise, omitting `--summarize` from `rq1_review_structural.py` enters model-assisted review rather than an offline summary.

## Running the final tests (level 2)

Each exported case directory (`…/<subject>/pytest-export-final/<CASE>/`) contains `conftest.py` and `test_final_calibrated_suite.py`, which describe the frozen requests, captures, bindings and assertions. Install pytest, prepare the dependencies in [INSTALL.md](INSTALL.md), and export the test-account variables. Example commands are `.venv/bin/pytest eval/ui_semantics/deepseek-full-20260912/conduit/pytest-export-final/L1-ARTICLE-01` and `.venv/bin/pytest eval/ui_semantics/ghost-20260921/ghost/pytest-export-final/L1-POST-01`. The runtime starts and stops the application, resets it, authenticates the actors and injects fresh identifiers. Do not start a second copy of the same application beforehand. The Flat RWA `L1-BANK-03` fixture locates its frozen source in data volume 2 relative to the package root; see its [case README](eval/ui_semantics/deepseek-ablation-20260913/rwa/pytest-export-flat/L1-BANK-03/README.md).

## Continuing a frozen run (level 2) and full runs (level 3)

Live CLI runs use `docs/ACTIVE-EXECUTION.json`. Copy the matching template from `docs/active-templates/` before a live command and restore `closed.json` afterwards, as described in [INSTALL.md](INSTALL.md#run-lock-for-live-commands). These setup commands change the reviewer's working copy; the saved run roots remain the source material.

For Conduit and RWA, `scripts/continue_frozen_case.sh <subject> <CASE>` selects a completed frozen M10 source and matching profile, then writes under `eval/ui_semantics/reviewer-continuation/<subject>/cases/<CASE>/union`.

For Umami, Paperless-ngx and Ghost, use the single-case CLI directly with `continue-<subject>.json`. The following is a command template: replace every `<...>` field, choose an unused output directory, and use a profile fixture whose bytes match `<frozen-case-union>/inputs/subject/profile.json` and whose path is admitted by the chosen lock. The completion digest is the SHA-256 of `<frozen-case-union>/M10/proposal_run_completion.json`.

```sh
scripts/uisemtest run \
  --profile <matching-profile-fixture> \
  --adapter fixtures/adapters/<subject>_current_local.json \
  --frozen-m10-source <frozen-case-union> \
  --frozen-m10-completion-sha256 <completion-sha256> \
  --output-root eval/ui_semantics/reviewer-continuation/<subject>/cases/<CASE>/union \
  --output-level forensic --probe-budget 0
```

The historical batch helper `scripts/experiments/rq1_tools/continue_frozen_m10_subject.sh` writes to `<runs-root>/<subject>/<new-run>` and uses macOS `caffeinate`. Its default output layout differs from the reviewer continuation templates; the direct CLI above provides the corresponding cross-platform entrypoint. Match the frozen source, profile and lock before execution.

For a new suite run from saved UI recordings, use `suite-<subject>.json` and the complete template below. The suite, recording root, adapter, output root and protocol parameters must match that lock. The recording roots below are those named by the supplied suite templates; extract the relevant material first.

| Subject | Saved recording root |
|---|---|
| `conduit` | `eval/ui_semantics/deepseek-ablation-20260913/conduit/recordings-final` |
| `rwa` | `eval/ui_semantics/deepseek-ablation-20260913/rwa/recordings-final` |
| `umami` | `eval/ui_semantics/umami-20260921/recordings-01` |
| `paperless` | `eval/ui_semantics/paperless-20260921/recordings-01` |
| `ghost` | `eval/ui_semantics/ghost-20260921/recordings-01` |

```sh
scripts/uisemtest run \
  --suite fixtures/recording_workflows/<subject>_modular/inventory.json \
  --recording-root <saved-recording-root-from-table> \
  --adapter fixtures/adapters/<subject>_current_local.json \
  --provider openai_compatible \
  --provider-policy fixtures/provider_configs/deepseek_flash_current.json \
  --output-root eval/ui_semantics/reviewer-run/<subject> \
  --output-level forensic --probe-budget 0 \
  --m10-samples 3 --m10-sample-mode union --provider-concurrency 48
```

The specified provider configuration reads `LLM_BASE_URL` and `LLM_API_KEY`. If using the `DEEPSEEK_BASE_URL` and `DEEPSEEK_API_KEY` names in `.env.example`, explicitly export them as `LLM_BASE_URL` and `LLM_API_KEY` for this command. Model-assisted review tools can use different environment names as declared by their own configurations. This suite command consumes saved recordings; it does not re-record UI actions. The Paperless `recordings-ablation` root includes its 32 selected recording copies; its [recording selection and reconstruction instructions](eval/ui_semantics/paperless-20260921/recordings-ablation/README.md) explain the source and how to rebuild missing copies.

## Notes

- Absolute machine paths inside manifests were rewritten to `<ARTIFACT_ROOT>` (this directory), `<SUBJECTS>` (checkout directory of the subjects), `<PAPER_CODE_WORKTREE>` (the checkout of the pinned code an ablation was run from) and `<HOME>` during packaging; the recorded traces and model answers are otherwise unmodified. `scripts/relocate.py` fills the placeholders in on your machine (`<PAPER_CODE_WORKTREE>` only when you pass `--paper-code-worktree <dir>`; pass this directory to run the ablation launchers against the shipped code), except in three kinds of provenance manifests (recording session manifests, recording input manifests, recording workflow results) whose bytes are pinned by SHA-256 in the frozen lineage: those keep the placeholders, and `docs/artifact-relocation.json` maps their shipped digests to the original ones so that every pin check still passes (`ui_semantics/artifact_relocation.py`). `BUILD-REPORT.json` lists what the packaging step did.
- Test-account credentials in the fixtures and in `.env.example` are local placeholders, not real secrets.
- The implementation's earlier internal name, `carverflow`, survives in a few machine identifiers because the frozen artifacts carry them: the `tool_version` string of artifact envelopes (`carverflow 0.1.0`), the `x-carverflow-*` OpenAPI extension keys, the HAR creator name of the recorder, and the local placeholder accounts (`carver@carverflow.local`). These identifiers are retained for compatibility with the frozen artifacts.
- The `contract_inventory` and `method_hashes` sections of the run manifests record the SHA-256 digests of the schema and source files at the time of each run. The shipped code is the state after the execution-framework fixes described in `docs/RUN-NOTES.md`, and its comments, docstrings and schema descriptions were translated into English for the package, so the digests of the shipped files differ from the recorded ones; the frozen-lineage pins that the pipeline verifies (recording bundles, input manifests, candidate oracles, model responses) are unaffected.
- The earlier round of the study with another model (gpt-6-astra, single round) is represented by its review scope list and export catalogues used by the summariser; its run outputs are outside this package.
- Licenses: code under MIT (`LICENSE`), data and documents under CC BY 4.0 (`LICENSE-DATA`).
