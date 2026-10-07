# Deviation Detector (Streaming)

- Subscribe to `events.normalized`.
- For each step start, check current time against p95 baseline from ClickHouse.
- If late/missing, publish `entropy.deviation` to Kafka and insert into `karma.entropy_scores`.

## Implementation status

The job source is currently a placeholder. The bullets above describe intended behavior, not a running prediction or detection service. See [Karma implementation and proof status](../../../docs/adage-proving-ground.md).
