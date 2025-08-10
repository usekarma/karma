CREATE TABLE IF NOT EXISTS karma.events_raw
(
  ts               DateTime,
  event_type       LowCardinality(String),
  entity_id        String,
  correlation_id   String,
  tags             JSON,
  attrs            JSON,
  idempotency_key  String,
  source           JSON,
  _ingested_at     DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (entity_id, ts);
