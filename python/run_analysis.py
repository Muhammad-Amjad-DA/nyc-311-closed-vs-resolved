"""Runs the SQL pipeline in order and writes every SELECT result to outputs/*.csv.
Usage (from repo root):  python python/run_analysis.py
"""
import re, pathlib, duckdb

root = pathlib.Path(__file__).resolve().parents[1]
out = root / "outputs"; out.mkdir(exist_ok=True)
con = duckdb.connect()

for f in sorted((root / "sql").glob("*.sql")):
    n = 0
    for stmt in re.split(r";\s*(?:\n|$)", f.read_text()):
        body = re.sub(r"--[^\n]*", "", stmt).strip()   # drop comments
        if not body:
            continue
        res = con.execute(stmt)
        if re.match(r"(SELECT|WITH)\b", body, re.I):
            n += 1
            df = res.fetchdf()
            df.to_csv(out / f"{f.stem}_q{n}.csv", index=False)
            print(f"\n=== {f.name} (result {n}) ===")
            print(df.to_string(index=False))
