# Power BI report: 3 pages, fully specified

**Status:** data model, DAX and page specification. The `.pbix` file is added after it is built from this spec; until then no screenshots are shown.
Data: six small aggregated tables in `data/` (about 1.6 MB, no addresses, no row-level tickets). Regenerate with `python python/export_powerbi.py`.

## Setup (once)
| Setting | Value |
|---|---|
| Canvas | 16:9, 1280 x 720 |
| Font | Segoe UI. Page title 24 bold, subtitle 12 grey, visual titles 14 bold, labels 11 |
| Colours | Navy `#1F3A5F` (default), orange `#E07A1F` (the one thing to look at), grey `#8A94A3` (context), background white |
| Data | Get data > Text/CSV, load the 6 files in `data/`. Create no relationships. Load measures from `measures.dax` into a blank table `_Measures` |
| Rule | Every visual has a title, a one-line subtitle that states the unit or base, data labels on, gridlines off, no legend unless stated |

Control totals the report must show before it is published: **46.5%**, **70.0%**, **34,552**, **127,507**, **41.2%**.

---

## Page 1: Executive Overview
**Question:** Does "closed" tell us whether the problem stays solved?
**Title:** "When 311 says 'closed', does the problem stay solved?" **Subtitle:** "3.65M requests created in 2025, NYC Open Data 311 Service Requests"

| Element | Spec |
|---|---|
| Card 1 | Measure `[Closed Tickets (all)]`. Label "Closed tickets". Expect **3,602,425** |
| Card 2 | `[Action Taken Share]`. Label "Closing note records an action". Expect **29.5%**. Orange |
| Card 3 | `[Refile Rate 30d]`. Label "Re-filed within 30 days". Expect **46.5%** |
| Card 4 | `[Heat Refile Rate 30d]`. Label "Heat / hot water re-filed within 30 days". Expect **70.0%**. Orange |
| Visual A: horizontal bar | Axis (Y): `closure_outcomes[outcome]`, sorted by value descending. Values (X): `[Closed Outcome Share]`, axis hidden, labels as 0.0%. Colour: `action_taken` orange, others grey (Format > Data colours > By rules). **Title:** "What the closing notes say happened". **Subtitle:** "Share of all closed tickets, by outcome (keyword rules on the closing note)". **Answers:** how often does a closed ticket record an action? Tooltip: `[Closed Tickets (all)]` |
| Visual B: clustered column | Axis: `refile_by_type_outcome_month[complaint_family]`. Values: `[Refile Rate 30d]`. Y axis 0 to 100%. Navy columns, labels on. **Title:** "Do they come back?" **Subtitle:** "Share re-filed at the same address and complaint type within 30 days". **Answers:** do condition and behaviour complaints repeat equally? Tooltip: `[Closed Tickets (in scope)]`, `[Refiled 30d]`. Expect behaviour **57.7%**, condition **32.0%** |
| Annotation (text box under B) | "Behaviour repeats (noise, parking) mean the behaviour recurred. Condition repeats (heat, plumbing) suggest the problem persisted or came back." |
| Takeaway (text box, bottom, 14 bold navy) | "'% closed' and 'time to close' cannot see repeats. Heat complaints return 7 times in 10." |
| Filters | None on this page |

## Page 2: Repeat Complaints & Building Concentration
**Question:** Are heat repeats spread thin, or concentrated in a few buildings, and when do they peak?
**Title:** "Heat complaints repeat, and a few buildings drive most of it" **Subtitle:** "Heat / hot water tickets closed January to November 2025"

| Element | Spec |
|---|---|
| Card 1 | `[Heat Buildings]`. Label "Buildings with a closed heat complaint". Expect **34,552** |
| Card 2 | `[Heat Repeat Tickets]`. Label "Repeat heat tickets (re-filed within 30 days)". Expect **127,507** |
| Card 3 | `[Heat Refile Rate 30d]`. Label "Re-filed within 30 days". Expect **70.0%** |
| Card 4 | `[Top 1000 Share]`. Label "Share of repeats from the top 1,000 buildings". Expect **41.2%**. Orange |
| Visual A: line chart (Pareto) | Axis (X): `heat_building_concentration[building_rank]`, continuous, range 0 to 10,000. Values (Y): `[Cumulative Repeat Share]`, 0 to 100%, navy line. Analytics pane > X-axis constant line at **1000**, orange, label "Top 1,000 buildings". **Title:** "A thousand buildings produce two in five repeats". **Subtitle:** "Cumulative share of repeat heat tickets, buildings ranked from most to fewest repeats". **Answers:** is the problem concentrated enough to target? Tooltip: `building_rank`, `[Cumulative Repeat Share]` |
| Visual B: clustered column | Axis: three measures `[Heat Refile Rate 7d]`, `[Heat Refile Rate 14d]`, `[Heat Refile Rate 30d]` (rename 7 days, 14 days, 30 days). Y 0 to 100%, labels on, 30 days orange. **Title:** "Not an artefact of the 30-day window". **Subtitle:** "Heat re-file rate by follow-up window". **Answers:** does the result depend on the window? Expect **52.2%, 61.8%, 70.0%** |
| Visual C: line and clustered column | Axis: `heat_monthly[closed_month]` (Month). Columns: `[Heat Closed Tickets]` (grey, primary axis). Line: `[Heat Monthly Refile Rate]` (navy, secondary axis 0 to 100%, labels on). **Title:** "Repeats peak in the heating season". **Subtitle:** "Heat tickets closed per month (bars) and share re-filed within 30 days (line)". **Answers:** when should an intervention be in place? Tooltip: month, `[Heat Closed Tickets]`, `[Heat Monthly Refile Rate]`. Expect October **75.9%**, November **78.4%** |
| Annotation (text box under C) | "December is excluded: tickets closed then have no complete 30-day window in the data." |
| Takeaway | "Manage heat by building, and have the pilot running before 1 October." |
| Filters | None. The tables are already limited to heat / hot water |

## Page 3: Closure Quality / Operational Investigation
**Question:** Does how a ticket is closed, or how fast, tell us whether it comes back?
**Title:** "Fast and closed is not the same as solved" **Subtitle:** "How agencies close tickets and what happens next"

| Element | Spec |
|---|---|
| Card 1 | `[No Finding Share]`. Label "Closed with no finding". Expect **31.8%** |
| Card 2 | `[Could Not Reach Share]`. Label "Closed: could not reach or gone". Expect **14.1%** |
| Card 3 | `[Heat Caller-Said-Fixed Share]`. Label "Heat tickets closed on the caller's word". Expect **45.0%**. Orange |
| Card 4 | `[Heat Median Hours to Close]`. Label "Heat median hours to close". Expect **39.4** |
| Visual A: 100% stacked bar | Axis (Y): `closure_by_agency_outcome[agency]`. Legend: `outcome`. Values: `[Agency Closed Tickets]`. Visual-level filter: agency, Top N = 8 by `[Agency Closed Tickets]`. `action_taken` orange, `no_finding` navy, `could_not_reach_or_gone` grey-blue, others light grey. **Title:** "How each agency closes tickets". **Subtitle:** "Outcome mix of closed tickets, 8 largest agencies". **Answers:** do agencies close for different reasons? Tooltip: `agency`, `outcome`, `[Agency Closed Tickets]`, `[Agency Outcome Share]` |
| Visual B: bar | Axis (Y): `refile_by_type_outcome_month[outcome]`. Values: `[Refile Rate 30d]`, axis 0 to 100%, labels on. Visual-level filters: `complaint_type` = HEAT/HOT WATER and `[Closed Tickets (in scope)]` is at least 3000. `info_or_referral` orange, others navy. **Title:** "For heat, how it was closed barely changes the repeat rate". **Subtitle:** "30-day re-file rate by closing outcome, heat / hot water". **Answers:** do verified closures last longer? Expect **61% to 71%**, information-only **88.4%** |
| Visual C: scatter | X: `[Type Median Hours]`, log scale. Y: `[Type Refile Rate]`, 0 to 100%. Details: `type_speed_repeat[complaint_type]`. Legend: `complaint_family` (condition navy, behaviour grey). Size: `[Type Closed Tickets]`. Label only HEAT/HOT WATER (orange). **Title:** "Closing fast does not predict staying closed". **Subtitle:** "Median hours to close vs 30-day re-file rate, complaint types with 20,000+ closed tickets". **Answers:** is speed a quality signal? Tooltip: type, median hours, rate, tickets |
| Annotation (text box, right of C) | "Noise and parking close in about an hour and still repeat. Heat takes 39 hours and returns 70%. Repeat rate adds information that speed does not." |
| Method note (footer, 10 grey) | "Repeat = a new ticket at the same address and complaint type within 30 days of closure. Same address is not the same household. Closing outcomes come from keyword rules; see /validation." |
| Filters | None |

---

## Finish
1. Check the five control totals above. If one differs, stop and re-export the data.
2. Save as `nyc311_closed_vs_resolved.pbix`. Export each page as PNG at 1280 x 720 into `images/powerbi_page1.png` to `page3.png`, and a PDF of all three pages.
3. Add the three images and the file to the main README under "Power BI report".
