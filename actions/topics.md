# Karma Actions Topics

- `actions.requested` — commands to execute
- `actions.progress` — in-flight updates
- `actions.result` — outcomes (succeeded/failed/cancelled)
- `actions.dlq` — dead letters

Partition key: use `entity_id` or target resource to preserve order per entity.
