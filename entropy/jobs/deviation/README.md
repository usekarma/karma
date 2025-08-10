# Deviation Detector (Streaming)

- Subscribe to `events.normalized`.
- For each step start, check current time against p95 baseline from ClickHouse.
- If late/missing, publish `entropy.deviation` to Kafka and insert into `karma.entropy_scores`.
