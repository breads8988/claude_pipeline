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
| App error code | `ERR-<CODE>-<NN>`, taken from the source; missing → open question | `ERR-USR-01` |
| Bug draft file | `qa/tickets/BUG-TBD-<TC-ID>.md`, renamed `BUG-<jira-key>.md` once created | `BUG-ABC-123.md` |
| Task draft file | `qa/tickets/TASK-TBD-<slug>.md`, renamed `TASK-<jira-key>.md` once created | `TASK-ABC-124.md` |

- AC, TC, OQ, BR use 3 digits; FLD, DT, ST use 2 digits. Sequential per Feature Code, never reused.
- Do not renumber. Mark removed items `Status: Deprecated`.
- Feature Codes are listed in `.claude/rules/project.md`. Add new codes there first.

## Criticality and priority
- One scale for AC, rules, models and TC: 🔴 Critical · 🟠 High · 🟡 Medium · ⚪ Low.
- **TC priority** = the highest criticality among its `Covers AC` and its `Coverage items`. Single source of this rule; the coverage validator enforces it.
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
- `Type`: Functional | Non-functional.
- `Technique`: one or more of Scenario, EP, BVA, Decision table, State transition, Checklist, Error guessing.
- `Coverage items`: notation in `gen-testcase` › `references/test-design-techniques.md` sec. 4.
- `Automation`: Not yet | Candidate | Done.
- `Status`: Active | Blocked | Deprecated. Only a TC that contains `TBD (OQ-…)` is `Blocked`, with `Blocked by` set to that question. Other TCs of the same AC stay `Active`.
- Data-driven TC: several test data rows, steps run once per row; each row is one execution.
- `EG:` and `CHK:` items need a `Covers AC`. A case no AC describes becomes an AC or an open question first.

## Open question status
- `Open`: asked, waiting. `Posted`: the user replied `skip`; the question is on the Jira ticket. `Answered`: answer recorded.
- Before `/approve`, answers given in chat are applied by `write-ac`. After `/approve`, use `/resolve-oq`.

## Item status in AC tables
- Business rules and data constraints have a `Status` column: Active | Deprecated. Decision tables and state models may carry a `- Status: Deprecated` line.

## File status (header of `ac.md` and `tc.md`)
- `Draft` → `Approved` (via `/approve`) or `Changes requested` (via `/reject`).
- Any edit to an `Approved` `ac.md` sets it **and** its `tc.md` back to `Draft`. Any edit to an approved `tc.md` sets it back to `Draft`.
- A run needs both files `Approved`.

## Runs
- Run file: `qa/runs/<YYYY-MM-DD>-<feature>-<build>.md`.
- Evidence: failed TCs only. The run row's `Evidence` cell holds the screenshot path returned by the browser tool, or `qa/runs/<run>/evidence/<TC-ID>.png` (git-ignored).
- Report: `qa/reports/<run>.html` (git-ignored).
- Examples live in `_example/` folders and are never edited per project.
