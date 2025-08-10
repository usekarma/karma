CREATE OR REPLACE VIEW karma.v_latest_by_entity AS
SELECT *
FROM (
  SELECT *, row_number() OVER (PARTITION BY entity_id ORDER BY ts DESC) AS rn
  FROM karma.events_raw
)
WHERE rn = 1;
