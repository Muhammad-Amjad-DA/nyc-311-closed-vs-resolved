# KPI definitions

One definition per KPI. If a number in this repo does not match one of these, it is a bug.

| KPI | Definition | Value |
|---|---|---|
| Tickets | Distinct `unique_key` values for requests created 2025-01-01 to 2025-12-31 | 3,655,042 |
| % closed (official-style KPI) | Tickets with `status = 'Closed'` / all tickets | 98.56% |
| Time to close | Hours from `created_date` to `closed_date`. Blank when closed before created (916 tickets) | median 6.6 h, 90th percentile 409.5 h |
| Closure outcome | Bucket assigned to the closing note by keyword rules in `sql/01_clean.sql` (first match wins): `duplicate`, `could_not_reach_or_gone`, `action_taken`, `fixed_per_caller_unverified`, `no_finding`, `info_or_referral`, `other`, `no_resolution_text` | see README |
| In-scope closed ticket | Closed, has an address, not closed as a duplicate, closed between 2025-01-01 and 2025-11-30 (so a full 30-day follow-up window exists in the data) | 2,954,866 |
| **Re-filed within 30 days** | An in-scope ticket is re-filed if a NEW request with the same address and the same complaint type was created after its closure and within 30 days | 46.5% overall |
| Complaint family | `behaviour`: NYPD tickets, noise, drug activity, vendor enforcement, encampment, homeless assistance, blocked driveway. `condition`: everything else (heat, plumbing, leaks, street condition...) | - |
| Re-file reading | `behaviour` re-files mean the behaviour recurred. They are **not** read as failed closure. `condition` re-files suggest the problem persisted or came back. They do not prove the original fix failed | behaviour 57.7%, condition 32.0% |
| Repeat tickets (building level) | Sum of re-filed flags for heat / hot water tickets by address | 127,507 across 34,552 buildings |
