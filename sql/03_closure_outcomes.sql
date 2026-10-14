-- 03_closure_outcomes.sql | "Closed" does not mean "fixed". What do the closing notes actually say?

SELECT outcome,
       COUNT(*)                                                  AS closed_tickets,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)        AS pct_of_closed
FROM tickets WHERE status = 'Closed' GROUP BY 1 ORDER BY 2 DESC;

-- Same view for the three biggest complaint types
SELECT complaint_type, outcome, COUNT(*) AS closed_tickets,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY complaint_type), 1) AS pct_within_type
FROM tickets
WHERE status = 'Closed' AND complaint_type IN ('Illegal Parking', 'Noise - Residential', 'HEAT/HOT WATER')
GROUP BY 1, 2 ORDER BY 1, 3 DESC;
