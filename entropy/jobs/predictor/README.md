# Entropy Predictor (MVP)

- Pull recent features from ClickHouse (e.g., p95 latency per (entity_id, step)).
- Compute ETA/confidence using median/MAD baselines.
- Publish `entropy.predicted` to Kafka and insert a row into `karma.entropy_scores`.
