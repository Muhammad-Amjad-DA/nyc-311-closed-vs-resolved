-- 02_closed_headline.sql | What the official KPI says: share closed and time to close.

SELECT COUNT(*)                                                    AS tickets,
       ROUND(100.0 * AVG((status = 'Closed')::INT), 2)             AS pct_closed,
       ROUND(MEDIAN(hours_to_close), 1)                            AS median_hours_to_close,
       ROUND(QUANTILE_CONT(hours_to_close, 0.9), 1)                AS p90_hours_to_close
FROM tickets;

-- By agency (top 8 by volume)
SELECT agency, COUNT(*) AS tickets,
       ROUND(MEDIAN(hours_to_close), 1) AS median_hours_to_close,
       ROUND(100.0 * AVG((status = 'Closed')::INT), 1) AS pct_closed
FROM tickets GROUP BY 1 ORDER BY 2 DESC LIMIT 8;
