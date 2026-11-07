# Naming and ID rules

## IDs
| Item | Format | Example |
| --- | --- | --- |
| Feature Code | 3-4 uppercase letters | `TRF`, `FX`, `KYC` |
| Acceptance criteria | `AC-<CODE>-<NNN>` | `AC-TRF-001` |
| Test case | `TC-<CODE>-<NNN>` | `TC-TRF-014` |
| Bug draft file | `BUG-<jira-key>.md` | `BUG-ABC-123.md` |

- Numbers have 3 digits, sequential per Feature Code, never reused.
- Do not renumber. Mark removed items `Status: Deprecated`.
- Feature Codes are listed in the CLAUDE.md config table. Add new codes there first.

## Folders
- Feature folder: lowercase kebab-case (`transfer`, `fx-rate`).
- One `ac.md` and one `tc.md` per feature folder.

## Traceability
- Each AC lists its Jira ticket key.
- Each TC lists the AC IDs it covers.
- When automation exists, scripts carry the tag `@TC-<CODE>-<NNN>`.

## TC fields
- `Priority`: P1 | P2 | P3.
- `Type`: Functional | Negative | Boundary | Regression | Smoke.
- `Automation`: Not yet | Candidate | Done.
