"""Scores the keyword rules against the hand-labelled sheet.
Usage (from repo root):  python python/score_validation.py validation/validation_sheet_labelled.xlsx
Prints raw accuracy, prevalence-weighted accuracy, per-bucket precision/recall and every disagreement.
"""
import re, sys, pathlib, duckdb, pandas as pd

root = pathlib.Path(__file__).resolve().parents[1]
labelled = pd.read_excel(sys.argv[1], sheet_name="Label", dtype={"unique_key": str})
labelled = labelled.rename(columns={labelled.columns[5]: "human", labelled.columns[4]: "note"})
assert labelled.human.notna().all(), "every row needs a label"
labelled["human"] = labelled.human.astype(str).str.strip()

con = duckdb.connect()
for stmt in re.split(r";\s*(?:\n|$)", (root / "sql" / "01_clean.sql").read_text()):
    if re.sub(r"--[^\n]*", "", stmt).strip():
        con.execute(stmt)
rules = con.execute("SELECT CAST(unique_key AS VARCHAR) AS unique_key, outcome AS rule FROM tickets").fetchdf()
sizes = con.execute("SELECT outcome AS rule, COUNT(*) AS n FROM tickets WHERE status='Closed' AND outcome <> 'no_resolution_text' GROUP BY 1").fetchdf()

d = labelled.merge(rules, on="unique_key", how="left"); d["match"] = d.human == d.rule
print(f"Raw accuracy on the stratified sample: {100*d.match.mean():.1f}%  ({d.match.sum()}/{len(d)})")
w = d.groupby("rule").match.mean().rename("acc").reset_index().merge(sizes, on="rule")
print(f"Prevalence-weighted accuracy (what share of ALL closed tickets with text the rules label correctly): {100*(w.acc*w.n).sum()/w.n.sum():.1f}%")
print("\nPer rule bucket (sample size, share of that bucket the human agreed with):")
print(d.groupby("rule").match.agg(["size", "mean"]).round(2).to_string())
print("\nDisagreements:")
for r in d[~d.match].itertuples(): print(f"- #{r.n} rule={r.rule} human={r.human} | {str(r.note)[:160]}")

# Write a ready-to-publish results file (numbers only, nothing hand-edited)
per = d.groupby("rule").match.agg(["size", "mean"])
lines = ["# Validation result", "",
         f"Hand-labelled {len(d)} closing notes (stratified by rule bucket) and compared them with the keyword rules.", "",
         f"- Raw agreement on the stratified sample: **{100*d.match.mean():.1f}%** ({d.match.sum()} of {len(d)})",
         f"- Prevalence-weighted agreement (share of all closed tickets with text that the rules label correctly): **{100*(w.acc*w.n).sum()/w.n.sum():.1f}%**", "",
         "| Rule bucket | Notes checked | Agreement |", "|---|---|---|"]
lines += [f"| {k} | {int(v['size'])} | {100*v['mean']:.0f}% |" for k, v in per.iterrows()]
lines += ["", "## Disagreements", ""] + [f"- #{r.n}: rule `{r.rule}`, my label `{r.human}`. {str(r.note)[:160]}" for r in d[~d.match].itertuples()]
lines += ["", "Small samples per bucket (10 to 15 notes): treat bucket-level percentages as indicative."]
(root / "validation" / "RESULT.md").write_text("\n".join(lines) + "\n")
print("wrote validation/RESULT.md")
