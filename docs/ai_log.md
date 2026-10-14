# How AI was used

This project was built with Claude (Anthropic) as a coding and writing assistant. This log records what it did, where it went wrong, and which decisions are analytical judgement calls to challenge.

## What AI did
- Wrote the SQL files, the Python runner and the chart code
- Drafted the keyword rules that bucket the closing text, then iterated them after reading the largest unmatched texts
- Drafted the README from the computed result files
- Built the 100-note validation sheet and scorer, the Power BI data export and the page specification. The hand-labelling and the Power BI build are done by the analyst, not by AI

## What AI did **not** do
No language model is applied to the data. The closing text is classified with transparent keyword rules, which can be audited line by line. A model-based classifier validated against a hand-labelled sample would be a natural next step.

## Where the first analysis was wrong (caught during validation)
1. **A confounded hypothesis.** Pooled across all complaint types, tickets closed on a caller's unverified say-so were re-filed 64% of the time versus 28% to 56% for other closure types. That looked like a headline. Comparing **within the same complaint type** removed the effect: almost all of those tickets are heat complaints, which are re-filed 61% to 71% for most closure outcomes. The claim was dropped, and the README reports that the closing method barely changes the repeat rate.
2. **A NULL-handling bug in the window check.** The 14-day re-file rate (71.5%) came out higher than the 30-day rate (70.0%) because `AVG` ignored NULLs. Fixed with `COALESCE`, and a tie-out test now asserts 7 days <= 14 days <= 30 days.
3. **Behaviour vs condition.** The first headline (46.5% of closed tickets re-filed) treated a noise complaint at the same address as a failed closure. The analysis now separates recurring behaviour from physical conditions.

## Judgement calls made by the analyst (review these)
- Which complaint types count as "behaviour" and which as "condition"
- The 30-day window and the "same address + same type" definition of a repeat
- Treating tickets closed as duplicates as out of scope
- The keyword rules for the outcome buckets

## What was not delegated
Every headline number is reconciled by `sql/06_tieout_tests.sql`, including an independent brute-force recomputation of the re-file flag on a 20,000-ticket sample.
