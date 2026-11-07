---
name: write-ac
description: Act as a senior BA and write BABOK-aligned acceptance criteria from a Jira ticket - GWT scenarios, business rules, data constraints, decision tables and state models - then collect open-question answers. Use when the user gives a ticket key or asks for AC of a feature.
---

# write-ac

Method: `references/ac-techniques.md`. Format: `qa/_templates/ac.md`. Reference: `qa/specs/_example/ac.md`.

## Input
- Jira ticket key or pasted requirement.
- Feature Code and folder (ask only if unclear).
- Optional: screenshots or design images to ground UI states. Never invent UI you have not seen.

## Steps
1. Read `.claude/rules/project.md` (Jira key, Feature Codes, roles, notifications) and `.claude/rules/domain.md` (entities, glossary, checklist).
2. Read the ticket with the Atlassian MCP: summary, description, type, comments, linked pages. An Epic → read every child issue; trace each AC to the child it came from.
3. Read `references/ac-techniques.md` and `qa/specs/_example/ac.md`.
4. **Analyse** (§1): fill the analysis items, write the user story, check INVEST.
5. **Impacted existing behaviour** (§6): search other features by entity, cite real IDs, report the result.
6. Read existing `qa/specs/<feature>/ac.md` if present. Continue every numbering (AC, BR, FLD, DT, ST, OQ).
7. **Model**: write data constraints, decision tables (including role × action) and state models wherever the requirement has them (§3, §4).
8. **Scenarios**: write GWT AC for each scenario class that applies (§4, §5). Set `Type`, `Criticality`, `Likelihood` (§2, §7).
9. **Business rules**: one row per rule, with an example value.
10. **Open questions** (§8): every assumption and ambiguity, closed-ended, with `Blocks`.
11. **Gate**: run the IIBA quality gate and final checklist (§9, §11). Fix every miss.
12. Set the header: `Status: Draft`, `Open questions: <n>`, `Last updated`.
13. Save to `qa/specs/<feature>/ac.md`. Run the `comment-style` lint; fix until exit 0.
14. Add rows to `qa/traceability/matrix.md` (Ticket and AC columns).
15. Send the **AC ready for review** notification (`comment-style` › `references/notifications.md`). Add one line each for: impacted behaviour result, counts by type and criticality, scenario classes skipped and why.

## Open questions: answer first, then Jira
1. Wait for the user's replies to the notification.
2. An answer → update the AC and models, set the OQ `Status: Answered`, add the answer as a business rule. Re-run the gate and the lint.
3. `skip <OQ-ID>` → collect it. `skip all` → collect every open question.
4. Post the collected questions as **one** Jira comment on the ticket (`comment-style` table 2). `skip` is the user's approval to post.
5. Update `Open questions: <n>` in the header.

## Do not
- Do not invent rules, IDs or UI the sources do not state.
- Do not renumber existing items.
- Do not write clicks, screens or technical detail in AC.
- Do not set `Approved`. Only `/approve` does that.
- Do not post an open question to Jira unless the user replied `skip` for it.
