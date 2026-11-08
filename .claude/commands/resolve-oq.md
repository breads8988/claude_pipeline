---
description: Record the answer to an open question and update the AC and TC it blocks
argument-hint: <OQ-ID> "<answer>"
---

Resolve: $ARGUMENTS

1. Find the open question in `qa/specs/*/ac.md` (skip `_example`). It must be `Open` or `Posted`. Set `Status: Answered` and note the answer.
2. Add the answer as a business rule. Update every AC and model row that carries `TBD (<OQ-ID>)` or is in its `Blocks` column.
3. In `qa/testcases/<feature>/tc.md`, for each TC with `Blocked by: <OQ-ID>`:
   - Replace every `TBD (<OQ-ID>)` with the answered content.
   - Set `Status: Active`, `Blocked by: —`.
4. Update `Open questions: <n>` in the AC header.
5. Edited files go back to `Draft`: the AC file, and the TC file of the feature (`naming.md` › File status).
6. Run the lint on both files and the coverage validator with `--summary` (paste the new summary); fix until all exit 0.
7. Send the **OQ resolved** notification: AC and TC changed, files waiting for `/approve` again.
8. Posted questions: offer one Jira comment on the ticket with the answer (ask first).
