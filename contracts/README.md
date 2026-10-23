# contracts/ — inter-stage contracts (frozen assets)

Every pipeline artifact is a JSON document validated against one of the schemas in this directory (the artifact's `schema_version` field names the schema). The schemas are frozen; a schema change is a breaking change. Each schema has a minimal example instance under `examples/`.

## Extension keywords

| Keyword | Location | Meaning |
|---|---|---|
| `x-carverflow-counts` | schema property objects inside `initial_oas` | `{n_present, n_total}`: how often the field occurred over all observations of the operation (the evidence for required/optional decisions) |

The `x-carverflow-*` extension keywords carry the implementation's earlier internal name; they are part of the frozen artifact format and are kept as they are.

## Schema relationships

`run_config.schema.json` references `app_profile.schema.json`; the run-config example follows that definition.

`augmented_oas.schema.json#/$defs/ui_observation` follows the shape of `initial_oas.schema.json#/$defs/observation` with an additional `source` constant. Probe observations use `probe_id`, while recorded observations use `run_id` and `entry_index`. When updating the shared observation fields, keep the two definitions consistent.
