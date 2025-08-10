CREATE TABLE IF NOT EXISTS karma.entropy_scores
(
  ts DateTime,
  entity_id String,
  step LowCardinality(String),
  kind LowCardinality(String), -- predicted|deviation
  score Float32,
  eta DateTime,
  details JSON
)
ENGINE = MergeTree
ORDER BY (entity_id, step, ts);
