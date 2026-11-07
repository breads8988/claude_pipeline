# Naming and ID rules

## IDs
| Item | Format | Example |
| --- | --- | --- |
| Feature Code | 3-4 uppercase letters | `TRF`, `FX`, `KYC` |
| Acceptance criteria | `AC-<CODE>-<NNN>` | `AC-TRF-001` |
| Test case | `TC-<CODE>-<NNN>` | `TC-TRF-014` |
| Open question | `OQ-<CODE>-<NNN>` | `OQ-TRF-002` |
| Bug draft file | `qa/tickets/BUG-<jira-key>.md` | `BUG-ABC-123.md` |
| Task draft file | `qa/tickets/TASK-<jira-key>.md` | `TASK-ABC-124.md` |

- Numbers have 3 digits, sequential per Feature Code, never reused.
- Do not renumber. Mark removed items `Status: Deprecated`.
- Feature Codes are listed in `.claude/rules/project.md`. Add new codes there first.

## Folders
- Feature folder: lowercase kebab-case (`transfer`, `fx-rate`).
- One `ac.md` and one `tc.md` per feature folder.

## Traceability
- Each AC lists its Jira ticket key.
- Each TC lists the AC IDs it covers.
- When automation exists, scripts carry the tag `@TC-<CODE>-<NNN>`.

## TC fields
- `Role`: a role from `.claude/rules/project.md`.
- `Priority`: P1 | P2 | P3.
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
