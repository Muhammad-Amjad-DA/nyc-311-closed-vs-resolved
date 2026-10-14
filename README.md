# NYC 311: When a Complaint Is "Closed", Does It Stay Solved?

![98.6% of 311 tickets are closed. 7 in 10 heat complaints come back.](images/hero_refile_rate.png)

**Question:** NYC 311 reports "% closed" and "time to close". Do those KPIs tell us whether the problem stayed solved, and where should the city look first?

| | |
|---|---|
| **Answer** | 98.56% of tickets are closed (median 6.6 hours), but the closing note records an action in only **29.5%** of them, and **70% of closed heat / hot water complaints are followed by a new heat complaint at the same address within 30 days**. "Closed" is an administrative status, not evidence of the outcome. |
| **Recommendation** | Track repeat rate next to "% closed", and treat buildings, not tickets, as the unit for heat complaints. Pilot on the **1,000 buildings that produce 41% of heat repeats**, ahead of the next heating season (starts 1 October). |
| **Impact (scenario)** | In 2025 the top 1,000 buildings generated about **52,500 repeat heat tickets**. Cutting their repeats by 10% to 25% means **5,300 to 13,100 fewer repeat tickets**. No cost is assumed. |
| **Data** | NYC Open Data, 311 Service Requests, 3,655,042 requests created in 2025 |
| **Tools** | SQL (DuckDB, PostgreSQL-compatible syntax), Python for the runner and charts |

---

## 1. Business problem
A 311 dashboard shows two numbers: percent closed and median time to close. Both can look excellent while the same problem keeps coming back. The question is whether "closed" is a quality signal, and if not, what to measure instead.

## 2. Data
3.65M requests across 14 columns, one year. 769 distinct free-text closing notes written by different agencies. Details in [`docs/data_quality_log.md`](docs/data_quality_log.md).

## 3. Cleaning (what changed the numbers)

| Issue | Rows | Decision |
|---|---|---|
| Closed before created | 916 | Time to close left blank |
| Missing address | 122,913 | Excluded from re-file analysis |
| Closed as "duplicate" by the agency | 144,383 | Excluded from re-file scope so they don't count as instant re-files |
| Closing notes in 769 different wordings | 3.6M closed | Mapped to 8 outcome buckets with keyword rules |
| Tickets closed in December | - | Excluded (no complete 30-day window) |

## 4. Analysis

**Three different things are easy to confuse here, and this project keeps them apart:**

| Concept | What it is | How it is measured here |
|---|---|---|
| Administrative closure | The agency set the ticket to "Closed" | `status = Closed`, 98.56% of tickets |
| Repeat complaint | A new ticket at the same address and complaint type within 30 days of closure | The re-file rate, 46.5% overall and 70.0% for heat |
| Physical resolution | The problem was actually fixed | **Not observable in this data.** A repeat suggests it may not have been, but a new outbreak or a neighbouring tenant can also cause one |


**"Closed" is not evidence of an outcome.** Reading the closing note of every closed ticket:

![Closure outcomes](images/closure_outcomes.png)

**Does the problem come back?** A ticket is *re-filed* when a new request with the same address and the same complaint type is created within 30 days of its closure. Overall 46.5% of in-scope closed tickets are re-filed, but that figure mixes two different things:

| Complaint family | Closed tickets | Re-filed within 30 days | Reading |
|---|---|---|---|
| Behaviour (noise, parking, drugs...) | 1,670,663 | 57.7% | The behaviour recurred. Not read as failed closure |
| **Condition (heat, plumbing, leaks...)** | **1,284,203** | **32.0%** | **Suggests the problem persisted or returned** |

Heat / hot water stands out at **70.0%**, and the result is stable across windows: 52.2% within 7 days, 61.8% within 14, 70.0% within 30.

**The closing method barely changes the repeat rate.** Within heat complaints, re-file rates sit between 61% and 71% whether the ticket was closed after an inspection with action (69.6%), a phone check with the caller (70.5%), no finding (64.7%) or an inspector who could not get in (60.9%). Only information-only closures are higher (88.4%). Heat tickets are also unusual in how they are closed: **45%** of in-scope closed heat tickets are closed on the caller's word that the problem was fixed, with no inspection result (3.4% of closed tickets overall). A first pooled comparison suggested caller-verified closures were worse. That was a complaint-type effect and is documented as a mistake in [`docs/ai_log.md`](docs/ai_log.md).

**The repeats are concentrated.**

![Heat concentration](images/heat_concentration.png)

The worst 1,000 of 34,552 buildings account for 41.2% of all repeat heat tickets. Repeats are also seasonal:

![Heat seasonality](images/heat_seasonality.png)

## 5. Key insight
"% closed" and "time to close" cannot see repeats. For heat, 7 in 10 closed tickets are followed by another heat complaint at the same address within 30 days, however the ticket was closed, and a small group of buildings produces a large share of them. That does not prove the fixes failed. It shows the city is not measuring whether they held.

## 6. Recommendation
1. **Add a 30-day repeat rate** beside "% closed" in the 311 reporting, by complaint family. Owner: 311 data team.
2. **Manage heat complaints per building.** A building with a second heat complaint inside 30 days becomes one escalated case with a follow-up inspection, instead of a new ticket. Owner: HPD.
3. **Pilot on the 1,000 worst buildings** before the next heating season. Repeat rates reach 76% to 78% in October and November.
4. **Do not read noise or parking re-files as failed closure.** They need a different response (pattern enforcement), not a re-inspection.

## 7. Business impact (scenario, not a forecast)
In 2025 (tickets closed January to November) the 1,000 worst buildings produced 41.2% of 127,507 repeat heat tickets, about 52,500. A 10% cut would be about 5,300 fewer repeat tickets, and a 25% cut about 13,100. Each is a new complaint at an address that had just been closed. A cost per ticket is not assumed here because the agency's handling costs are not in the data.

## Validation
**Computation:** `sql/06_tieout_tests.sql` must return PASS on every row. All seven pass, including a brute-force recomputation of the re-file flag on a 20,000-ticket sample, which matches the join-based result exactly.

**Closing-note rules:** the outcome buckets come from keyword rules, so they need a human check. [`validation/`](validation/) holds a 100-note sheet to be labelled by hand without seeing the rule output, and a scorer that compares the labels with the rules. The result is not claimed here until the labelled sheet has been scored (`validation/RESULT.md` will be added at that point).

## Power BI report
Three pages (Executive Overview, Repeat Complaints & Building Concentration, Closure Quality / Operational Investigation) are specified visual by visual in [`powerbi/`](powerbi/), with the data tables and DAX measures.

## Limitations
- One year of one city. 2025 only.
- Same address is not same household. In multi-unit buildings a re-file can come from a neighbour. For heat that still signals a building-level problem, but it is not proof the original fix failed.
- "Behaviour" vs "condition" is my classification of complaint types.
- Closing-note buckets come from keyword rules and are **not validated against a hand-labelled sample**. 7.1% of closed tickets fall in "other".
- Observational. This does not show why a problem returned.
- No cost data, so the impact is expressed in tickets.

## How AI was used
See [`docs/ai_log.md`](docs/ai_log.md): what AI drafted, three corrections made during validation, and the judgement calls to challenge. No language model is applied to the data itself.

## Reproduce
```
pip install duckdb pandas matplotlib
# download the 2025 monthly CSVs from NYC Open Data (dataset erm2-nwe9) into data/ as 311_2025_01.csv ... 311_2025_12.csv
python python/run_analysis.py
python python/make_charts.py
```

## Repo map
`sql/` pipeline in run order | `python/` runner, charts, validation and Power BI export | `docs/` KPI definitions, data quality log, AI log | `validation/` hand-check of the closing-note rules | `powerbi/` data, DAX and page specification | `images/` README visuals

*Data: NYC Open Data, 311 Service Requests from 2010 to Present. See the source page for terms of use.*
