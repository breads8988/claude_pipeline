---
name: impact-analysis
description: Find AC and TC affected by a change request or ticket update using the traceability matrix. Use when scope changes or before a regression plan.
---

# impact-analysis

## Input
- Changed Jira ticket key, or a description of the change.

## Steps
1. Read `qa/traceability/matrix.md`. Find rows for the ticket and related features.
2. Read the AC files of those features. Mark AC the change touches.
3. Follow links from affected AC to TCs. Mark TCs to update, re-run or retire.
4. Check neighbor features that share rules (see `domain.md`).
5. Report new AC or TC that are needed.

## Output (table)
| Item | ID | Impact | Action |
| --- | --- | --- | --- |
| AC | AC-USR-003 | Rule changed | Update |
| TC | TC-USR-009 | Expected result changed | Update and re-run |

- Add a short list of risks and open questions.
- Order rows by priority.
- Do not edit files unless the user asks.

## Do not
- Do not guess links missing from the matrix. Flag the gap instead.
