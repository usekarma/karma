-- ClickHouse canonical ledger for normalized events
CREATE TABLE IF NOT EXISTS events_raw
(
  ts               DateTime CODEC(Delta, ZSTD),
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
ORDER BY (entity_id, ts)
TTL ts + INTERVAL 90 DAY DELETE
SETTINGS index_granularity = 8192;
