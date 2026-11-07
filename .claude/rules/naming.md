# Naming and ID rules

## IDs
| Item | Format | Example |
| --- | --- | --- |
| Feature Code | 3-4 uppercase letters | `USR`, `ORD`, `RPT` |
| Acceptance criteria | `AC-<CODE>-<NNN>` | `AC-USR-001` |
| Test case | `TC-<CODE>-<NNN>` | `TC-USR-014` |
| Open question | `OQ-<CODE>-<NNN>` | `OQ-USR-002` |
| Business rule | `BR-<CODE>-<NNN>` | `BR-USR-001` |
| Data constraint (field) | `FLD-<CODE>-<NN>` | `FLD-USR-01` |
| Decision table / rule | `DT-<CODE>-<NN>` / `.R<n>` | `DT-USR-01.R3` |
| State model / transition | `ST-<CODE>-<NN>` / `.T<n>` | `ST-USR-01.T2` |
| Bug draft file | `qa/tickets/BUG-<jira-key>.md` | `BUG-ABC-123.md` |
| Task draft file | `qa/tickets/TASK-<jira-key>.md` | `TASK-ABC-124.md` |

- AC, TC, OQ, BR use 3 digits; FLD, DT, ST use 2 digits. Sequential per Feature Code, never reused.
- Do not renumber. Mark removed items `Status: Deprecated`.
- Feature Codes are listed in `.claude/rules/project.md`. Add new codes there first.

## Criticality and priority
- One scale for AC, rules, models and TC: 🔴 Critical · 🟠 High · 🟡 Medium · ⚪ Low.
- A TC's priority = the highest criticality among the items it covers.
- AC `Type`: Functional | Non-functional | Transition. AC `Likelihood`: Normal | High.

## Folders
- Feature folder: lowercase kebab-case (`user-invitation`, `order-history`).
- One `ac.md` and one `tc.md` per feature folder.

## Traceability
- Each AC lists its Jira ticket key.
- Each TC lists the AC IDs it covers.
- When automation exists, scripts carry the tag `@TC-<CODE>-<NNN>`.

## TC fields
- `Role`: a role from `.claude/rules/project.md`.
- `Priority`: 🔴 | 🟠 | 🟡 | ⚪.
- `Type`: Functional | Negative | Boundary | Regression | Smoke.
- `Automation`: Not yet | Candidate | Done.
- `Status`: Active | Blocked | Deprecated. `Blocked` needs `Blocked by: OQ-<CODE>-<NNN>`.

## File status (header of `ac.md` and `tc.md`)
- `Draft` → `Approved` (via `/approve`) or `Changes requested` (via `/reject`).
- Any edit to an `Approved` file sets it back to `Draft`.

## Runs
- Run file: `qa/runs/<YYYY-MM-DD>-<feature>-<build>.md`.
- Evidence: `qa/runs/<run>/evidence/<TC-ID>.png` (failed TCs only, git-ignored).
- Report: `qa/reports/<run>.html` (git-ignored).
- Examples live in `_example/` folders and are never edited per project.
