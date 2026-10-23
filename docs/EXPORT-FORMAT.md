# Export format

The pytest exporter produces deterministic Python test functions and reporting
metadata for retained tests, including business assertions and structural
constraints. Each directory lists its retained count, frozen source, and command.

The generated test functions expose every ordered HTTP, capture, binding,
settle, and assertion step. Each function docstring identifies the normalized
producer, observer, business predicate, candidate ID, canonical relation core,
and every raw M10 rationale source. Raw rationales are proposal metadata; they
do not affect candidate identity, exact deduplication, setup, verdict, or M14
retention.
`business_test_catalog.json` contains the reporting metadata and a
physical-test-occurrence versus canonical-core summary.

M11a records candidate lineage. Executable request material comes from M11b
`execution_material.json`, and the exported tests use the repository's M14
runtime. The `schema_type` assertion checks the JSON type at a frozen target
JSONPath.

Target-associated and setup-associated labels come from the post-M14 effect
reference report, using an independently defined target-workflow reference.
