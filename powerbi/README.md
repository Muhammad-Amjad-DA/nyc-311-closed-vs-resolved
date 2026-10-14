# Power BI report: "Closed" is not "fixed"

Status: **build spec and data model, ready to assemble. The .pbix is not published yet.** No screenshots are shown here until the report exists.

The report imports four small aggregated tables from `data/` (about 1.3 MB total, no addresses, no row-level tickets). Every number below can be re-created with `python python/export_powerbi.py` and ties to the SQL results in the main README.

## Data model
| Table | Grain | Used for |
|---|---|---|
| `closure_outcomes` | one row per closing outcome | Page 1 |
| `refile_by_type_outcome_month` | complaint type x outcome x closing month | Pages 1 and 3 |
| `heat_building_concentration` | one row per heat building, ranked by 30-day re-files | Page 2 |
| `heat_monthly` | closing month | Page 2 |

No relationships are needed. Add a `Date` table only if you want a continuous time axis.

## DAX measures (`measures.dax`)
See [measures.dax](measures.dax). Control totals the report must show: **2,954,866** in-scope closed tickets, **46.5%** re-filed within 30 days, heat/hot water **70.0%** on 182,033 tickets, top 1,000 buildings **41.2%** of 127,507 heat repeats.

## Page 1: Overview. "Closed" does not mean "fixed"
- Question as the page title: *When NYC 311 says a ticket is closed, what actually happened?*
- Cards: Closed tickets in scope, Re-filed in 30 days %, Behaviour vs Condition re-file %.
- Bar: closing outcomes (`closure_outcomes`), sorted. Highlight `no_finding` and `action_taken`.
- Slicer: complaint family.
- Takeaway text box: "Almost half of closed tickets at the same address and type come back within 30 days."

## Page 2: Heat and hot water. Where it repeats
- Question: *Where do heat complaints keep coming back, and when?*
- Cards: 70.0% re-filed in 30 days, 34,552 buildings, top 1,000 buildings = 41.2% of repeats.
- Line (Pareto): cumulative share of repeats by building rank (x = `building_rank`, y = `Cumulative Repeat Share`).
- Column + line: monthly closed tickets and re-file rate (`heat_monthly`). Peaks Oct to Jan.
- Takeaway text box: "A thousand buildings drive two in five repeat heat complaints."

## Page 3: Where to act
- Question: *Which complaint types should get a follow-up check first?*
- Table sorted by re-file rate: complaint type, family, closed tickets, re-file 7d / 14d / 30d, with data bars. Add a minimum closed-ticket filter (20,000), the same as the SQL.
- Scatter: closed tickets (x) vs re-file rate (y), bubble = family, to find high-volume and high-repeat types.
- Recommendation panel: pilot an inspector follow-up call at the top 1,000 heat buildings; scenario of 10 to 25% fewer repeats = about 5,300 to 13,100 fewer tickets (no cost assumed).
- Caveat footer: same address is not same household; behaviour complaints re-file because behaviour recurs.

## Build steps (about 90 minutes)
1. Power BI Desktop > Get data > Text/CSV, load the four files from `data/`.
2. Paste the measures from `measures.dax` into a `_Measures` table.
3. Build the three pages as above, theme colours navy `#1F3A5F`, orange `#E07A1F`, grey `#8A94A3`.
4. Check the control totals on Page 1 and Page 2 against the numbers above.
5. Save as `nyc311_closed_vs_fixed.pbix`, export a PDF, add screenshots to `images/` and link them from the main README.
