---
name: log-ticket
description: Draft a Jira bug or task, or a comment on one (retest, follow-up, hand-off). Use when the user reports a defect, asks for a task ticket, or asks for a Jira comment.
---

# log-ticket

Style: `.claude/rules/writing-style.md`. Comment layout: `comment-style` skill.

## What to write

| Request | Template | Draft file | Length cap |
|---|---|---|---|
| Bug | `qa/_templates/bug.md` | `qa/tickets/BUG-<key>.md` | None: fill every field |
| Task | `qa/_templates/task.md` | `qa/tickets/TASK-<key>.md` | None: fill every field |
| Comment on a ticket | `comment-style` table (retest = table 6) | No file | `comment-style` caps |

Use `TBD` as `<key>` until Jira assigns one, then rename the file.

## Steps
1. Read `.claude/rules/project.md` (Jira project key, Feature Codes).
2. Collect the facts. Bug: actual, expected, steps, environment, evidence. Task: goal, scope, done checklist.
3. Link the related AC and TC IDs when known.
4. Write the draft from the template, or the comment from `comment-style`.
5. Show the draft to the user. Ask before creating or commenting in Jira.
6. After approval, create the issue or post the comment with the Atlassian MCP. Rename the draft to the real key.

## Do not
- Do not include real customer or account data. Mask it.
- Do not write to Jira without confirmation.
- Do not shorten a ticket description to fit comment caps.
