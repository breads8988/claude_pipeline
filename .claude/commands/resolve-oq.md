---
description: Record the answer to an open question and update the AC and TC it blocks
argument-hint: <OQ-ID> "<answer>"
---

Resolve: $ARGUMENTS

1. Find the open question in `qa/specs/*/ac.md`. Set its `Status: Answered` and note the answer.
2. Add the answer as a business rule. Update every AC in its `Blocks` column.
3. In `qa/testcases/<feature>/tc.md`, for each TC with `Blocked by: <OQ-ID>`:
   - Replace every `TBD (<OQ-ID>)` with the answered content.
   - Set `Status: Active`, `Blocked by: —`.
4. Update `Open questions: <n>` in the AC header.
5. Edited files that were `Approved` go back to `Draft` (naming rules).
6. Run the `comment-style` lint on both files; fix until exit 0.
7. Send the **OQ resolved** notification: AC and TC changed, and which files need `/approve` again.
