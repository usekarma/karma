-- Example entropy calculation over latency buckets (adjust JSON paths as needed)
WITH
  toInt32(intDiv(CAST(JSON_VALUE(attrs, '$.latency_sec') AS Int32), 30))*30 AS bucket
SELECT
  entity_id,
  JSON_VALUE(tags, '$.step') AS step,
  -sum(p * log2(p)) AS entropy
FROM (
  SELECT
    entity_id,
    JSON_VALUE(tags, '$.step') AS step,
    bucket,
    count() AS c,
    c / sum(c) OVER (PARTITION BY entity_id, JSON_VALUE(tags, '$.step')) AS p
  FROM karma.events_raw
  WHERE event_type = 'step.completed' AND ts > now() - INTERVAL 7 DAY
  GROUP BY entity_id, step, bucket
)
GROUP BY entity_id, step
ORDER BY entropy DESC
LIMIT 100;
