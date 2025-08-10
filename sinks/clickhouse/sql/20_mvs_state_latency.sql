CREATE MATERIALIZED VIEW IF NOT EXISTS karma.mv_event_counts_5m
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (toStartOfFiveMinute(ts), event_type)
AS
SELECT toStartOfFiveMinute(ts) AS ts, event_type, countState() AS cnt_state
FROM karma.events_raw
GROUP BY ts, event_type;

CREATE OR REPLACE VIEW karma.v_event_counts_5m AS
SELECT ts, event_type, countMerge(cnt_state) AS events
FROM karma.mv_event_counts_5m
GROUP BY ts, event_type
ORDER BY ts, event_type;
