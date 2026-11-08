---
name: log-ticket
description: Draft a Jira bug or task, or a comment on one (retest, follow-up, hand-off). Use when the user reports a defect, asks for a task ticket, or asks for a Jira comment.
---

# log-ticket

Style: `.claude/rules/writing-style.md`. Comment layout: `comment-style` skill.

## What to write

| Request | Template | Draft file | Length cap |
|---|---|---|---|
| Bug | `qa/_templates/bug.md` | `qa/tickets/BUG-TBD-<TC-ID>.md` (no TC: `BUG-TBD-<slug>.md`) | None: fill every field |
| Task | `qa/_templates/task.md` | `qa/tickets/TASK-TBD-<slug>.md` | None: fill every field |
| Comment on a ticket | `comment-style` table (retest = table 6) | No file | `comment-style` caps |

After Jira assigns a key, rename the file `BUG-<key>.md` or `TASK-<key>.md` (`naming.md`).

## Steps
1. Read `.claude/rules/project.md`: Jira project key, Atlassian site, Feature Codes, Jira mapping (issue types, priority, severity, component, required fields, bug or task rule).
2. Collect the facts. Bug: actual, expected, steps, environment, evidence. Task: goal, scope, done checklist.
3. Link the related AC and TC IDs when known. From a run: also link the run file and the evidence path; take steps and expected result from the TC.
4. Write the draft from the template, or the comment from `comment-style`. Map priority 🔴🟠🟡⚪ to the project's Jira values. A Jira mapping value `—` or missing → ask the user once.
5. Show the draft to the user. Ask before creating or commenting in Jira. A bug from a run needs the user to confirm the failure first.
6. After approval, create the issue or post the comment with the Atlassian MCP. Rename the draft to the real key.
7. From a run: write the key in the run row's `Bug` cell.
8. Evidence: no tool uploads attachments. List the evidence paths and ask the user to attach them.
9. Retest comment: `comment-style` table 6, one per bug. Ask before posting and before any transition.

## Do not
- Do not include real customer or account data. Mask it.
- Do not write to Jira without confirmation.
- Do not shorten a ticket description to fit comment caps.
