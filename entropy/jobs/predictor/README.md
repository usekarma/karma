# Entropy Predictor (MVP)

- Pull recent features from ClickHouse (e.g., p95 latency per (entity_id, step)).
- Compute ETA/confidence using median/MAD baselines.
- Publish `entropy.predicted` to Kafka and insert a row into `karma.entropy_scores`.

## Implementation status

The job source is currently a placeholder. The bullets above describe intended behavior, not a running prediction or detection service. See [Karma implementation and proof status](../../../docs/adage-proving-ground.md).
