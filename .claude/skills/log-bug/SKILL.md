---
name: log-bug
description: Draft a bug log, task or Jira comment in the QA team's style (tables and bullets, short sentences). Use when the user reports a defect or asks for a Jira comment.
---

# log-bug

## Style
- English only. Tables and bullets only. No prose paragraphs.
- Each point max 20 words.
- No "written by AI" note or disclaimer.

## Steps
1. Collect: what happened, expected result, steps, environment, evidence.
2. Link the failing TC and AC if known.
3. Write the draft to `qa/bugs/BUG-<key>.md` using `qa/_templates/bug.md`.
4. Show the draft to the user. Ask before creating or commenting in Jira.
5. After approval, create the issue or comment with the Atlassian MCP.

## Do not
- Do not include real customer or account data. Mask it.
- Do not write to Jira without confirmation.
