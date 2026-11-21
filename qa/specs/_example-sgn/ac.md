# AC: Sign-in (SGN)

Golden example of a second feature linked to USR through the impact graph. Not a real feature.

| Field | Value |
| --- | --- |
| Jira | ABC-102 |
| Status | `Approved` |
| Approved by | qa.lead |
| Approved on | 2026-11-21 |
| Open questions | 0 |
| Last updated | 2026-11-21 |

## User story
**As a** user with an active account, **I want** to sign in with my email and password, **so that** I can use the workspace.

## Impacted existing behaviour
- USR: `AC-USR-006` activates the account that SGN checks. `RULE-ACC-001` is shared with `AC-USR-003`.

## Coverage notes
- Checklist (`domain.md`): input, permission and errors covered; integration, notification and audit not applicable (ABC-102 states none).
- Scenario classes skipped: non-functional (no performance requirement in ABC-102).

## Scenarios

### AC-SGN-001: An active user signs in with the email in any letter case
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Rules: RULE-ACC-001
- Entities: Account, User
- Given: an account with status = `Active` (`BR-SGN-001`)
- When: the user submits the email in a different letter case and the correct password
- Then: the user is signed in and the user list is displayed

### AC-SGN-002: A wrong password is rejected
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Entities: Account
- Given: an account with status = `Active`
- When: the user submits the email and a wrong password
- Then: rejected with ERR-SGN-01: `Email or password is incorrect.`; no side effects: no session created

### AC-SGN-003: Sign-in is rejected for an account that is not active
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Entities: Account, Invitation
- Hubs: HUB-access-control
- Given: an account with status = `Pending` (invitation not accepted) (`BR-SGN-001`)
- When: the user submits the email and a password
- Then: rejected with ERR-SGN-01: `Email or password is incorrect.`; no side effects: no session created

## Business rules
| Rule ID | Rule | Criticality | Status | Source |
| --- | --- | --- | --- | --- |
| BR-SGN-001 | Only an account with status = `Active` may sign in. | 🔴 | Active | ABC-102 |

## Open questions
| OQ | Risk | Question | Blocks | Owner | Status |
| --- | --- | --- | --- | --- | --- |

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
| 2026-11-21 | Approved | qa.lead | 0 open questions |
