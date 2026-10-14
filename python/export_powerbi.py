"""Builds the small aggregated tables the Power BI report imports (no row-level data, no addresses).
Usage (from repo root, after data/ is populated):  python python/export_powerbi.py
"""
import re, pathlib, duckdb
root = pathlib.Path(__file__).resolve().parents[1]
con = duckdb.connect()
def run(path, upto=None):
    for stmt in re.split(r";\s*(?:\n|$)", path.read_text()):
        s = re.sub(r"--[^\n]*", "", stmt).strip()
        if s and not s.upper().startswith("SELECT"):
            con.execute(stmt)
import os; os.chdir(root)
run(root/"sql"/"01_clean.sql"); run(root/"sql"/"04_refiled_within_30d.sql")
out = root/"powerbi"/"data"
def save(name, q):
    con.execute(f"COPY ({q}) TO '{out/name}' (HEADER, DELIMITER ',')")
# Page 1: what "closed" means
save("closure_outcomes.csv", """
 SELECT outcome, COUNT(*) AS closed_tickets FROM tickets
 WHERE status='Closed' GROUP BY 1""")
# Page 1/2: re-file rates by complaint type, family, outcome and closing month
save("refile_by_type_outcome_month.csv", """
 SELECT complaint_type, complaint_family, outcome, DATE_TRUNC('month', closed_date)::DATE AS closed_month,
        COUNT(*) AS closed_tickets, SUM(refiled_7d::INT) AS refiled_7d, SUM(refiled_14d::INT) AS refiled_14d,
        SUM(refiled_30d::INT) AS refiled_30d
 FROM refiled GROUP BY ALL""")
# Page 2: repeat concentration for heat/hot water (same definition as sql/05: buildings ranked by 30-day re-files).
# No addresses leave the repo: only the rank and counts.
save("heat_building_concentration.csv", """
 WITH b AS (SELECT address, SUM(refiled_30d::INT) AS repeats FROM refiled WHERE complaint_type='HEAT/HOT WATER' GROUP BY 1),
 r AS (SELECT ROW_NUMBER() OVER (ORDER BY repeats DESC, address) AS building_rank, repeats FROM b)
 SELECT building_rank, repeats, SUM(repeats) OVER (ORDER BY building_rank) AS cumulative_repeats,
        SUM(repeats) OVER () AS total_repeats, COUNT(*) OVER () AS n_buildings FROM r""")
# Page 2: seasonality
save("heat_monthly.csv", """
 SELECT DATE_TRUNC('month', closed_date)::DATE AS closed_month, COUNT(*) AS closed_tickets,
        SUM(refiled_30d::INT) AS refiled_30d FROM refiled WHERE complaint_type='HEAT/HOT WATER' GROUP BY 1""")
# Page 3: how agencies close tickets (all closed tickets, incl. duplicates and no-text)
save("closure_by_agency_outcome.csv", """
 SELECT agency, outcome, COUNT(*) AS closed_tickets FROM tickets WHERE status='Closed' GROUP BY 1, 2""")
# Page 3: speed vs repeat, by complaint type (types with at least 20,000 in-scope closed tickets)
save("type_speed_repeat.csv", """
 WITH s AS (SELECT complaint_type, MEDIAN(hours_to_close) AS median_hours_to_close FROM tickets WHERE status='Closed' GROUP BY 1)
 SELECT r.complaint_type, ANY_VALUE(r.complaint_family) AS complaint_family, COUNT(*) AS closed_tickets,
        SUM(r.refiled_30d::INT) AS refiled_30d, ROUND(ANY_VALUE(s.median_hours_to_close), 1) AS median_hours_to_close
 FROM refiled r JOIN s USING (complaint_type) GROUP BY r.complaint_type HAVING COUNT(*) >= 20000""")
print("ok")
