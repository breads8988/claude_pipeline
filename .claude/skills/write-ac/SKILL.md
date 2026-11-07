---
name: write-ac
description: Write acceptance criteria from a Jira ticket as Given/When/Then plus business rules, then collect open-question answers. Use when the user gives a ticket key or asks for AC of a feature.
---

# write-ac

## Input
- Jira ticket key or pasted requirement.
- Feature Code and folder (ask only if unclear).

## Steps
1. Read `.claude/rules/project.md` (Jira key, Feature Codes, Notifications).
2. Read the ticket with the Atlassian MCP. Read linked Confluence pages if any.
3. Read `.claude/rules/naming.md` and `domain.md`. Load the `comment-style` skill for wording.
4. Read `qa/specs/_example/ac.md` as the reference for detail and format.
5. Read existing `qa/specs/<feature>/ac.md` if present. Continue its numbering.
6. Split the requirement into small, testable scenarios.
7. Write each scenario as Given/When/Then, using `qa/_templates/ac.md`. Put business rules in a separate table.
8. Rate each AC: Critical | High | Medium | Low.
9. Log every missing rule as an open question. Fill `Blocks` with the AC it holds up.
10. Set the header: `Status: Draft`, `Open questions: <n>`, `Last updated`.
11. Save to `qa/specs/<feature>/ac.md`. Run the `comment-style` lint; fix until exit 0.
12. Add rows to `qa/traceability/matrix.md` (Ticket and AC columns).
13. Send the **AC ready for review** notification (`comment-style` › `references/notifications.md`).

## Open questions: answer first, then Jira
1. Wait for the user's replies to the notification.
2. An answer → update the AC, set the OQ `Status: Answered`, add the answer to the AC's business rules. Re-run the lint.
3. `skip <OQ-ID>` → collect it. `skip all` → collect every open question.
4. Post the collected questions as **one** Jira comment on the ticket (`comment-style` table 2). `skip` is the user's approval to post.
5. Update `Open questions: <n>` in the header.

## Output rules
- Include negative and boundary scenarios, not only the happy path.
- Every AC has Jira key, ID and criticality.
- Use the sentence templates in `comment-style` `references/vocabulary.md`.
- Open questions get IDs `OQ-<CODE>-NNN` and are closed-ended.

## Do not
- Do not invent rules the ticket does not state.
- Do not renumber existing AC.
- Do not set `Approved`. Only `/approve` does that.
- Do not post an open question to Jira unless the user replied `skip` for it.
