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
6. Read existing `qa/specs/<feature>/ac.md` if present. Continue every numbering (AC, BR, FLD, DT, ST, OQ). A Feature Code missing from `project.md`: propose the row (code, feature, folder) and add it after the user confirms.
7. **Model**: write data constraints, decision tables (including role × action) and state models wherever the requirement has them (§3, §4). A state model lists every state × event pair.
8. **Scenarios**: write GWT AC for each scenario class that applies (§4, §5). Set `Type`, `Criticality`, `Likelihood` (§2, §7).
9. **Business rules**: one row per rule, with an example value.
10. **Open questions** (§8): every assumption and ambiguity, closed-ended, with `Blocks`.
11. **Gate**: run the IIBA quality gate and final checklist (§9, §11). Fix every miss. Fill `## Coverage notes` (checklist items not applicable, scenario classes skipped and why).
12. Set the header: `Status: Draft`, `Open questions: <n>`, `Last updated`. Save to `qa/specs/<feature>/ac.md`.
13. Run the `comment-style` lint on the saved file; fix and re-run, max 3 attempts. Errors left → list them in the notification.
14. Run the `ac-reviewer` agent. Fix its findings, then re-run the lint.
15. Add one row per AC to `qa/traceability/matrix.md` (Ticket, Feature, AC, Criticality; TC `—`).
16. Last: send the **AC ready for review** notification (`comment-style` › `references/notifications.md`). Add one line each for: impacted behaviour result, counts by type and criticality, reviewer findings left open.

## Open questions: answer first, then Jira
Applies while the AC file is `Draft`. After `/approve`, answers go through `/resolve-oq`.
1. Wait for the user's replies to the notification.
2. An answer → update the AC and models, set the OQ `Status: Answered`, add the answer as a business rule. Re-run the gate and the lint.
3. `skip <OQ-ID>` → collect it. `skip all` → collect every question still `Open` (never `Posted` ones again).
4. Post the collected questions as **one** Jira comment on the ticket (`comment-style` table 2). `skip` is the user's approval to post. Set each posted question to `Status: Posted`.
5. Update `Open questions: <n>` in the header (`Open` + `Posted`).

## Do not
- Do not invent rules, IDs or UI the sources do not state.
- Do not renumber existing items.
- Do not write clicks, screens or technical detail in AC.
- Do not set `Approved`. Only `/approve` does that.
- Do not post an open question to Jira unless the user replied `skip` for it.
