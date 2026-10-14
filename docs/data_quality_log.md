# Data quality log

Source: NYC Open Data, *311 Service Requests from 2010 to Present* (dataset `erm2-nwe9`), requests created in 2025, 14 columns, pulled through the Socrata API one month at a time.

| # | Issue found | Rows affected | Decision | Effect on results |
|---|---|---|---|---|
| 1 | Duplicate `unique_key` | 0 | `SELECT DISTINCT` kept as a safeguard, and a tie-out test checks uniqueness | None |
| 2 | Closed before created (impossible duration) | 916 | `hours_to_close` set to blank; ticket kept | Excluded from timing and from the re-file scope |
| 3 | No `closed_date` | 54,675 (of which 6,024 have status Closed) | Not used for timing | 98.56% "closed" is based on `status`, not on the date |
| 4 | Missing address | 122,913 (3.4%) | Excluded from the re-file analysis (cannot match locations) | Re-file results cover address-based complaints only |
| 5 | Borough missing or "Unspecified" | 2,607 | Set to blank. Borough is not used in headline numbers | None |
| 6 | Missing or "N/A" resolution text | 39,608 missing, 30,503 "N/A" | Outcome bucket `no_resolution_text` | 1.1% of closed tickets |
| 7 | Closing text varies in wording across agencies (769 distinct texts) | all closed | Keyword rules map text to 8 outcome buckets. 'other' started at 13.4% and was reduced to 7.1% after reading the top unmatched texts | **Rules are not yet validated against a hand-labelled sample.** Workflow in `validation/` (see limitations) |
| 8 | Duplicates closed by the agency ("a duplicate of a previously filed complaint") | 144,383 closed tickets | Excluded from the re-file scope. Otherwise they would count as instant re-files | Prevents inflating the rate |
| 9 | Tickets closed in December 2025 | - | Excluded from the re-file scope (no complete 30-day follow-up) | Avoids understating re-files |
