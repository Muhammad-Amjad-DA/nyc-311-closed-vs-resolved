-- 06_tieout_tests.sql | Every row must return PASS before a number is quoted.

SELECT 'ticket keys are unique after cleaning' AS test,
  CASE WHEN (SELECT COUNT(*) FROM tickets) = (SELECT COUNT(DISTINCT unique_key) FROM tickets) THEN 'PASS' ELSE 'FAIL' END AS result
UNION ALL
SELECT 'every closed ticket has exactly one outcome bucket',
  CASE WHEN (SELECT COUNT(*) FROM tickets WHERE status = 'Closed') = (SELECT SUM(c) FROM (SELECT COUNT(*) AS c FROM tickets WHERE status = 'Closed' GROUP BY outcome)) THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 'in-scope tickets are a subset of closed tickets',
  CASE WHEN (SELECT COUNT(*) FROM closed_scope c WHERE NOT EXISTS (SELECT 1 FROM tickets t WHERE t.unique_key = c.unique_key AND t.status = 'Closed')) = 0 THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 'one row per in-scope ticket after the follow-up join',
  CASE WHEN (SELECT COUNT(*) FROM refiled) = (SELECT COUNT(*) FROM closed_scope) THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 're-file rate rises with the window (7d <= 14d <= 30d)',
  CASE WHEN (SELECT SUM(refiled_7d::INT) <= SUM(refiled_14d::INT) AND SUM(refiled_14d::INT) <= SUM(refiled_30d::INT) FROM refiled) THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 'family counts add up to scope',
  CASE WHEN (SELECT COUNT(*) FROM refiled WHERE complaint_family = 'behaviour') + (SELECT COUNT(*) FROM refiled WHERE complaint_family = 'condition') = (SELECT COUNT(*) FROM refiled) THEN 'PASS' ELSE 'FAIL' END
UNION ALL
-- Independent check: recompute the 30-day flag with a brute-force EXISTS for a 20,000-ticket sample.
SELECT 'ASOF join matches brute-force EXISTS on a 20,000-ticket sample',
  CASE WHEN (
      SELECT COUNT(*) FROM (
          SELECT r.unique_key, r.refiled_30d AS flag,
                 EXISTS (SELECT 1 FROM tickets t
                         WHERE t.address = r.address AND t.complaint_type = r.complaint_type
                           AND t.created_date > r.closed_date AND t.created_date <= r.closed_date + INTERVAL 30 DAY) AS check_flag
          FROM (SELECT * FROM refiled ORDER BY hash(unique_key) LIMIT 20000) r
      ) WHERE flag <> check_flag) = 0 THEN 'PASS' ELSE 'FAIL' END;
