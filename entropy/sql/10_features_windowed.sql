CREATE TABLE IF NOT EXISTS karma.features_windowed
(
  ts DateTime,
  entity_id String,
  step LowCardinality(String),
  count UInt32,
  p50 Float32, p95 Float32, avg Float32, stddev Float32,
  day_of_week UInt8, hour UInt8
)
ENGINE = MergeTree
ORDER BY (entity_id, step, ts);
