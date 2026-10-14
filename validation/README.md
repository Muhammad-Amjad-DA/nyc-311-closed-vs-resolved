# Manual validation of the closing-note rules

The closing-note buckets (action taken, nothing found, could not reach, ...) come from keyword rules in `sql/01_clean.sql`.
This folder checks them against **my own hand labels** on 100 notes.

## Method
1. `python python/validation_sample.py` draws 100 closed tickets with closing text (15 per bucket for six buckets, 10 from `other`, fixed hash order) into `validation/validation_sheet.xlsx`. The rule's answer is **not** in that file.
2. I read each note and picked a label from the dropdown using the definitions below (also on the sheet's Guide tab), without looking at any rule output.
3. `python python/score_validation.py validation/validation_sheet_labelled.xlsx` compares my labels with the rules and weights agreement by each bucket's real share of closed tickets.

## Label definitions
| Label | Use when the note says... |
|---|---|
| `action_taken` | the agency fixed it, cleaned, repaired, issued a summons/violation, or completed the work |
| `no_finding` | nothing was found: no violation, no evidence, condition not observed, no action necessary |
| `could_not_reach_or_gone` | the inspector could not get in, could not complete the inspection, or those responsible were gone |
| `fixed_per_caller_unverified` | someone (caller, tenant, occupant) said it was fixed, with no inspection confirming it |
| `duplicate` | closed because it duplicates another complaint or an earlier one at the same location |
| `info_or_referral` | information only, referral to another agency, jurisdiction, or "see website" |
| `other` | none of the above fits |

## Result
**Status: sheet drawn, labels not yet entered, so the rules are not yet validated.** Once the sheet is labelled, running the scorer writes `validation/RESULT.md` and that file is linked from the main README.
