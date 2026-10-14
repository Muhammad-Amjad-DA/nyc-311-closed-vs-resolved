"""Builds the README images from outputs/*.csv. Run after run_analysis.py."""
import pathlib, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = pathlib.Path(__file__).resolve().parents[1]
out, img = root / "outputs", root / "images"; img.mkdir(exist_ok=True)
NAVY, ORANGE, GREY = "#1F3A5F", "#E07A1F", "#8A94A3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": GREY, "axes.labelcolor": "#333", "xtick.color": "#333", "ytick.color": "#333"})

def titles(fig, title, sub):
    fig.suptitle(title, x=0.05, ha="left", fontsize=18, fontweight="bold", color=NAVY)
    fig.text(0.05, 0.885, sub, fontsize=11, color=GREY)

# 1) Hero: 30-day re-file rate, physical-condition complaints
t = pd.read_csv(out / "04_refiled_within_30d_q2.csv")
t = t[t.complaint_family == "condition"].sort_values("refiled_pct", ascending=False).head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(12, 6.3), dpi=100)
cols = [ORANGE if c == "HEAT/HOT WATER" else NAVY for c in t.complaint_type]
bars = ax.barh(t.complaint_type.str.title().str.replace("Heat/Hot Water", "Heat / Hot Water"), t.refiled_pct, color=cols)
for b, v in zip(bars, t.refiled_pct): ax.text(v + 0.8, b.get_y() + b.get_height()/2, f"{v:.1f}%", va="center", fontsize=11, fontweight="bold")
ax.set_xticks([]); ax.spines["bottom"].set_visible(False); ax.set_xlim(0, 80)
ax.tick_params(axis="y", labelsize=11)
titles(fig, "98.6% of 311 tickets are 'closed'. 7 in 10 heat complaints come back.",
       "% of closed tickets re-filed at the same address, same type, within 30 days (physical-condition complaints, 2025)")
fig.tight_layout(rect=[0, 0, 1, 0.87]); fig.savefig(img / "hero_refile_rate.png"); plt.close(fig)

# 2) Closure outcomes
o = pd.read_csv(out / "03_closure_outcomes_q1.csv")
names = {"no_finding": "Nothing found / no violation", "action_taken": "Action taken (fixed, summons, cleaned)",
         "could_not_reach_or_gone": "Could not reach, no access, or gone", "info_or_referral": "Information or referral only",
         "other": "Other", "duplicate": "Closed as duplicate", "fixed_per_caller_unverified": "Caller said fixed (not verified)",
         "no_resolution_text": "No resolution text"}
o["label"] = o.outcome.map(names); o = o.iloc[::-1]
fig, ax = plt.subplots(figsize=(12, 6.3), dpi=100)
cols = [ORANGE if x == "action_taken" else GREY for x in o.outcome]
bars = ax.barh(o.label, o.pct_of_closed, color=cols)
for b, v in zip(bars, o.pct_of_closed): ax.text(v + 0.5, b.get_y() + b.get_height()/2, f"{v:.1f}%", va="center", fontsize=11, fontweight="bold")
ax.set_xticks([]); ax.spines["bottom"].set_visible(False); ax.set_xlim(0, 38); ax.tick_params(axis="y", labelsize=11)
titles(fig, "Only 3 in 10 'closed' tickets record an action taken",
       "What the closing note says, 3.6M closed NYC 311 tickets from 2025 (keyword rules on resolution text)")
fig.tight_layout(rect=[0, 0, 1, 0.87]); fig.savefig(img / "closure_outcomes.png"); plt.close(fig)

# 3) Concentration
c = pd.read_csv(out / "05_heat_deep_dive_q1.csv").iloc[0]
labels = ["Worst 1%\nof buildings", "Worst 5%", "Worst 25%"]; vals = [c.top_1pct_share_pct, c.top_5pct_share_pct, c.top_25pct_share_pct]
fig, ax = plt.subplots(figsize=(12, 6.3), dpi=100)
bars = ax.bar(labels, vals, color=[NAVY, ORANGE, NAVY], width=0.55)
for b, v in zip(bars, vals): ax.text(b.get_x() + b.get_width()/2, v + 1.5, f"{v:.1f}%", ha="center", fontsize=15, fontweight="bold")
ax.set_ylim(0, 105); ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.tick_params(axis="x", labelsize=13)
titles(fig, "5% of buildings generate 53% of repeat heat complaints",
       f"Share of all 30-day heat re-files, buildings ranked by repeats ({int(c.buildings):,} buildings, {int(c.total_repeat_tickets):,} repeats)")
fig.tight_layout(rect=[0, 0, 1, 0.87]); fig.savefig(img / "heat_concentration.png"); plt.close(fig)

# 4) Seasonality
m = pd.read_csv(out / "05_heat_deep_dive_q2.csv")
fig, ax = plt.subplots(figsize=(12, 6.3), dpi=100)
ax.plot(m.closed_month, m.refiled_pct, color=NAVY, lw=3, marker="o")
for _, r in m.iterrows(): ax.text(r.closed_month, r.refiled_pct + 2.5, f"{r.refiled_pct:.0f}", ha="center", fontsize=10)
ax.set_xticks(range(1, 12)); ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"], fontsize=11)
ax.set_ylim(0, 95); ax.set_yticks([]); ax.spines["left"].set_visible(False)
ax.set_xlabel("Month the ticket was closed (December excluded: no full 30-day window)")
titles(fig, "Heat complaints come back most during the heating season",
       "% of closed heat / hot water tickets re-filed at the same address within 30 days, by month closed, 2025")
fig.tight_layout(rect=[0, 0, 1, 0.87]); fig.savefig(img / "heat_seasonality.png"); plt.close(fig)
print("ok")
