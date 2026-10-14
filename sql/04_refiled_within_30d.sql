-- 04_refiled_within_30d.sql | Does the problem come back after a ticket is closed?
-- Re-filed = a NEW request for the SAME address and SAME complaint type, created after the ticket was closed
-- and within 30 days of closure.
-- Scope: closed tickets with an address, not closed as "duplicate", closed between 2025-01-01 and 2025-11-30
-- so that a full 30-day follow-up window exists inside the data.
-- CAVEAT: same address is not same household. In multi-unit buildings a re-file may come from a neighbour.

CREATE OR REPLACE TABLE closed_scope AS
SELECT unique_key, address, complaint_type, agency, outcome, closed_date,
       CASE WHEN agency = 'NYPD' OR complaint_type ILIKE 'Noise%'
              OR complaint_type IN ('Drug Activity', 'Vendor Enforcement', 'Encampment', 'Homeless Person Assistance', 'Blocked Driveway')
            THEN 'behaviour' ELSE 'condition' END AS complaint_family
FROM tickets
WHERE status = 'Closed' AND address IS NOT NULL AND hours_to_close IS NOT NULL
  AND outcome <> 'duplicate'
  AND closed_date >= TIMESTAMP '2025-01-01' AND closed_date < TIMESTAMP '2025-12-01';

-- For each closed ticket: the next ticket (same address + type) created after its closure.
CREATE OR REPLACE TABLE refiled AS
SELECT c.*, n.created_date AS next_created,
       COALESCE(n.created_date <= c.closed_date + INTERVAL 7 DAY,  FALSE) AS refiled_7d,
       COALESCE(n.created_date <= c.closed_date + INTERVAL 14 DAY, FALSE) AS refiled_14d,
       COALESCE(n.created_date <= c.closed_date + INTERVAL 30 DAY, FALSE) AS refiled_30d
FROM closed_scope c
ASOF LEFT JOIN (SELECT address, complaint_type, created_date FROM tickets WHERE address IS NOT NULL) n
  ON c.address = n.address AND c.complaint_type = n.complaint_type AND c.closed_date < n.created_date;

-- Headline, split by complaint family.
-- "behaviour" (noise, parking, drugs...) re-files mean the behaviour recurred, so they are NOT read as failed closure.
-- "condition" (heat, plumbing, leaks...) re-files suggest the physical problem was not fixed.
SELECT complaint_family, COUNT(*) AS closed_tickets, SUM(refiled_30d::INT) AS refiled,
       ROUND(100.0 * AVG(refiled_30d::INT), 1) AS refiled_pct
FROM refiled GROUP BY 1
UNION ALL
SELECT 'all', COUNT(*), SUM(refiled_30d::INT), ROUND(100.0 * AVG(refiled_30d::INT), 1) FROM refiled;

-- By complaint type (min 20,000 closed tickets)
SELECT complaint_type, complaint_family, COUNT(*) AS closed_tickets, ROUND(100.0 * AVG(refiled_30d::INT), 1) AS refiled_pct
FROM refiled GROUP BY 1, 2 HAVING COUNT(*) >= 20000 ORDER BY 4 DESC;

-- Does HOW a ticket was closed predict whether it comes back? Compare outcomes WITHIN the same complaint type.
SELECT complaint_type, outcome, COUNT(*) AS closed_tickets, ROUND(100.0 * AVG(refiled_30d::INT), 1) AS refiled_pct
FROM refiled
WHERE complaint_type IN ('HEAT/HOT WATER', 'Illegal Parking', 'Noise - Residential', 'UNSANITARY CONDITION', 'PLUMBING')
GROUP BY 1, 2 HAVING COUNT(*) >= 3000 ORDER BY 1, 3 DESC;

-- Window sensitivity for heat / hot water
SELECT ROUND(100.0 * AVG(refiled_7d::INT), 1)  AS d7_pct,
       ROUND(100.0 * AVG(refiled_14d::INT), 1) AS d14_pct,
       ROUND(100.0 * AVG(refiled_30d::INT), 1) AS d30_pct
FROM refiled WHERE complaint_type = 'HEAT/HOT WATER';
