# AC: User invitation (USR)

Golden example: the reference for level of detail. Not a real feature.

| Field | Value |
| --- | --- |
| Jira | ABC-101 |
| Status | `Approved` |
| Approved by | qa.lead |
| Approved on | 2026-11-08 |
| Open questions | 2 |
| Last updated | 2026-11-08 |

## User story
**As an** Admin, **I want** to invite a person by email, **so that** they can join the workspace with their own account.

## Impacted existing behaviour
- None, isolated change. Entity `User` checked: no other feature in this example.

## Coverage notes
- Checklist (`domain.md`): input, permission (incl. direct request), state, errors and idempotency covered; integration, notification and audit not applicable (ABC-101 states no partner system, email content or audit log).
- Scenario classes skipped: non-functional (no performance or accessibility requirement in ABC-101).

## Scenarios

### AC-USR-001: Admin invites a person with a valid, unused email
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Given: an Admin and no user with the email
- When: the Admin sends an invitation to the email
- Then: an invitation is created with status = `Invited` and the confirmation `Invitation sent.` is displayed

### AC-USR-002: An invalid email is rejected
- Type: Functional
- Criticality: 🟠 High
- Likelihood: Normal
- Status: Active
- Given: an Admin
- When: the Admin sends an invitation to an email that breaks `FLD-USR-01`
- Then: rejected with ERR-USR-02: `Enter a valid email.`; no side effects: no invitation created

### AC-USR-003: An email that belongs to a user is rejected
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Given: a user with the email exists, in any letter case (`BR-USR-002`)
- When: the Admin sends an invitation to that email
- Then: rejected with ERR-USR-01: `This email is already in use.`; no side effects: no invitation created

### AC-USR-004: A non-Admin invitation request is rejected
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Given: a Viewer (`BR-USR-001`)
- When: the Viewer submits an invitation
- Then: rejected with ERR-USR-03: `You do not have permission to invite users.`; no side effects: no invitation created

### AC-USR-005: An invitation expires
- Type: Functional
- Criticality: 🟠 High
- Likelihood: High
- Status: Active
- Given: an invitation with status = `Invited`
- When: the expiry time passes (OQ-USR-001)
- Then: status transitions to `Expired`

### AC-USR-006: The invitee accepts a valid invitation
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Given: an invitation with status = `Invited`
- When: the invitee completes acceptance with a password
- Then: status transitions to `Accepted` and the invitee's account is active

### AC-USR-007: A Viewer has no invite action
- Type: Functional
- Criticality: 🟠 High
- Likelihood: Normal
- Status: Active
- Given: a Viewer
- When: the user list is displayed
- Then: the invite action is not available

### AC-USR-008: An invitation that is no longer valid is not accepted
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Given: an invitation with status = `Expired` or `Accepted` (`BR-USR-004`)
- When: the invitee attempts to accept it
- Then: rejected with copy `This invitation is no longer valid.`; no side effects: status unchanged

### AC-USR-009: A repeated submission creates one invitation
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Given: an Admin and no user with the email
- When: the same invitation is submitted again before the first submission returns (`BR-USR-003`)
- Then: one invitation is created

### AC-USR-010: Re-inviting an email with a pending or expired invitation
- Type: Functional
- Criticality: 🟠 High
- Likelihood: Normal
- Status: Active
- Given: an invitation for the email with status = `Invited` or `Expired`
- When: the Admin sends an invitation to the same email
- Then: TBD (OQ-USR-002)

### AC-USR-011: Expiry has no effect on an accepted or expired invitation
- Type: Functional
- Criticality: 🟠 High
- Likelihood: Normal
- Status: Active
- Given: an invitation with status = `Accepted` or `Expired`
- When: the expiry time passes (OQ-USR-001)
- Then: status unchanged

## Business rules
| Rule ID | Rule | Criticality | Status | Source |
| --- | --- | --- | --- | --- |
| BR-USR-001 | Only the Admin role may invite. | 🔴 | Active | ABC-101 |
| BR-USR-002 | One user per email address, case-insensitive: `Ana@x.test` equals `ana@x.test`. | 🔴 | Active | ABC-101 |
| BR-USR-003 | A second identical submission sent before the first one returns creates no second invitation (idempotent). A later submission is a re-invite (OQ-USR-002). | 🔴 | Active | ABC-101 |
| BR-USR-004 | An invitation link can be accepted once, and only while status = `Invited`. | 🔴 | Active | ABC-101 |

## Data constraints
| FLD | Field | Type | Required | Min | Max | Step | Format or allowed values | Criticality | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FLD-USR-01 | Email (length in characters) | text | Yes | 6 | 254 | 1 | `local@domain.tld`; local part 1–64 characters; one `@`; no spaces; domain labels 1–63 characters | 🟠 | Active |

## Decision tables

### DT-USR-01: Invitation outcome
- Criticality: 🔴
- Covers: AC-USR-001, AC-USR-003, AC-USR-004

| Condition | R1 | R2 | R3 | R4 |
| --- | --- | --- | --- | --- |
| Requester role is Admin | Y | Y | N | N |
| Email belongs to an existing user | N | Y | N | Y |
| **Outcome** | Invitation created | ERR-USR-01 | ERR-USR-03 | ERR-USR-03 |

🔴 depth: every feasible column is listed; R3 and R4 are not merged (`test-design-techniques.md` §3).

## State models

### ST-USR-01: Invitation lifecycle
- Criticality: 🔴
- Covers: AC-USR-001, AC-USR-003, AC-USR-005, AC-USR-006, AC-USR-008, AC-USR-010, AC-USR-011

States: `Invited`, `Accepted`, `Expired`. Events: Admin sends invitation, invitee accepts, expiry time passes. Every state × event pair is listed.

| T | From | Event | To | Valid |
| --- | --- | --- | --- | --- |
| T1 | — | Admin sends invitation | Invited | Yes |
| T2 | Invited | Invitee accepts | Accepted | Yes |
| T3 | Invited | Expiry time passes | Expired | Yes |
| T4 | Accepted | Invitee accepts | Accepted (rejected, `BR-USR-004`) | No |
| T5 | Accepted | Expiry time passes | Accepted (no effect) | No |
| T6 | Expired | Invitee accepts | Expired (rejected, `BR-USR-004`) | No |
| T7 | Accepted | Admin sends invitation | Accepted (rejected, ERR-USR-01) | No |
| T8 | Invited | Admin sends invitation | TBD (OQ-USR-002) | TBD (OQ-USR-002) |
| T9 | Expired | Admin sends invitation | TBD (OQ-USR-002) | TBD (OQ-USR-002) |
| T10 | Expired | Expiry time passes | Expired (no effect) | No |

## Open questions
| OQ | Risk | Question | Blocks | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| OQ-USR-001 | 🔴 | Is the invitation expiry 24 h or 72 h? | AC-USR-005, AC-USR-011 | BA/PO | Posted |
| OQ-USR-002 | 🟠 | Re-inviting a pending or expired invitation: resend the same invitation, create a new one, or reject? | AC-USR-010, ST-USR-01.T8, ST-USR-01.T9 | BA/PO | Open |

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
| 2026-11-08 | Approved | qa.lead | 2 open questions (OQ-USR-001 posted to Jira, OQ-USR-002 open) |
