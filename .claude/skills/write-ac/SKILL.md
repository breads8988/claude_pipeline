---
name: write-ac
description: Write acceptance criteria from a Jira ticket as Given/When/Then plus business rules. Use when the user gives a ticket key or asks for AC of a feature.
---

# write-ac

## Input
- Jira ticket key or pasted requirement.
- Feature Code and folder (ask only if unclear).

## Steps
1. Read the config table in `CLAUDE.md`.
2. Read the ticket with the Atlassian MCP. Read linked Confluence pages if any.
3. Read `.claude/rules/naming.md` and `domain.md`. Load the `comment-style` skill for wording.
4. Read existing `qa/specs/<feature>/ac.md` if present. Continue its numbering.
5. Split the requirement into small, testable scenarios.
6. Write each scenario as Given/When/Then, using `qa/_templates/ac.md`. Put business rules in a separate table.
7. Rate each AC: Critical | High | Medium | Low.
8. List open questions for BA/PO. Do not guess missing rules.
9. Save to `qa/specs/<feature>/ac.md`. Run the `comment-style` lint on it; fix until exit 0.
10. Add rows to `qa/traceability/matrix.md` (Ticket and AC columns).

## Output rules
- Include negative and boundary scenarios, not only the happy path.
- Every AC has Jira key, ID and criticality.
- Use the sentence templates in `comment-style` `references/vocabulary.md`.
- Open questions get IDs `OQ-<CODE>-NNN`.

## Do not
- Do not invent rules the ticket does not state.
- Do not renumber existing AC.
