-- 05_heat_deep_dive.sql | Heat and hot water: how concentrated are the repeats, and when do they happen?

-- Concentration: share of all 30-day re-files that come from the worst X% of buildings.
WITH b AS (
    SELECT address, SUM(refiled_30d::INT) AS repeats
    FROM refiled WHERE complaint_type = 'HEAT/HOT WATER' GROUP BY 1
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (ORDER BY repeats DESC) AS rk,
           COUNT(*) OVER () AS n_buildings, SUM(repeats) OVER () AS total_repeats
    FROM b
)
SELECT MAX(n_buildings) AS buildings, MAX(total_repeats) AS total_repeat_tickets,
       ROUND(100.0 * SUM(CASE WHEN rk <= 100            THEN repeats END) / MAX(total_repeats), 1) AS top_100_share_pct,
       ROUND(100.0 * SUM(CASE WHEN rk <= 1000           THEN repeats END) / MAX(total_repeats), 1) AS top_1000_share_pct,
       ROUND(100.0 * SUM(CASE WHEN rk <= n_buildings*.01 THEN repeats END) / MAX(total_repeats), 1) AS top_1pct_share_pct,
       ROUND(100.0 * SUM(CASE WHEN rk <= n_buildings*.05 THEN repeats END) / MAX(total_repeats), 1) AS top_5pct_share_pct,
       ROUND(100.0 * SUM(CASE WHEN rk <= n_buildings*.25 THEN repeats END) / MAX(total_repeats), 1) AS top_25pct_share_pct
FROM ranked;

-- Seasonality: heat re-file rate by month the ticket was closed.
SELECT MONTH(closed_date) AS closed_month, COUNT(*) AS closed_tickets, ROUND(100.0 * AVG(refiled_30d::INT), 1) AS refiled_pct
FROM refiled WHERE complaint_type = 'HEAT/HOT WATER' GROUP BY 1 ORDER BY 1;

-- Official time-to-close for heat vs what happens next
SELECT ROUND(MEDIAN(hours_to_close), 1) AS median_hours_to_close
FROM tickets WHERE complaint_type = 'HEAT/HOT WATER' AND status = 'Closed';
