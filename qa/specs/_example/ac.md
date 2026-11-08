# AC: User invitation (USR)

Golden example: the reference for level of detail. Not a real feature.

| Field | Value |
| --- | --- |
| Jira | ABC-101 |
| Status | `Approved` |
| Approved by | qa.lead |
| Approved on | 2026-11-08 |
| Open questions | 1 |
| Last updated | 2026-11-08 |

## User story
**As an** Admin, **I want** to invite a person by email, **so that** they can join the workspace with their own account.

## Impacted existing behaviour
- None, isolated change. Entity `User` checked: no other feature in this example.

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

### AC-USR-003: A duplicate email is rejected
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Given: a user with the email exists
- When: the Admin sends an invitation to that email
- Then: rejected with ERR-USR-01: `This email is already in use.`; no side effects: no invitation created

### AC-USR-004: Only an Admin may invite
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Given: a Viewer
- When: the Viewer opens the user list
- Then: the invite action is hidden and an invite request from a Viewer is rejected with HTTP 403

### AC-USR-005: An invitation expires
- Type: Functional
- Criticality: 🟠 High
- Likelihood: High
- Status: Active
- Given: an invitation with status = `Invited`
- When: the expiry time passes (OQ-USR-001)
- Then: status transitions to `Expired` and the link displays `This invitation has expired.`

### AC-USR-006: The invitee accepts a valid invitation
- Type: Functional
- Criticality: 🔴 Critical
- Likelihood: Normal
- Status: Active
- Given: an invitation with status = `Invited`
- When: the invitee accepts it and sets a password
- Then: status transitions to `Active` and the invitee is logged in

## Business rules
| Rule ID | Rule | Criticality | Source |
| --- | --- | --- | --- |
| BR-USR-001 | Only the Admin role may invite. A Viewer request returns HTTP 403. | 🔴 | ABC-101 |
| BR-USR-002 | One user per email address, case-insensitive: `Ana@x.test` equals `ana@x.test`. | 🔴 | ABC-101 |

## Data constraints
| FLD | Field | Type | Required | Min | Max | Format or allowed values | Criticality |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FLD-USR-01 | Email | text | Yes | 6 | 254 | `local@domain.tld`, no spaces | 🟠 |

## Decision tables

### DT-USR-01: Invitation outcome
- Criticality: 🔴
- Covers: AC-USR-001, AC-USR-003, AC-USR-004

| Condition | R1 | R2 | R3 |
| --- | --- | --- | --- |
| Role is Admin | Y | Y | N |
| Email unused | Y | N | – |
| **Outcome** | Invitation created | ERR-USR-01 | HTTP 403, invite action hidden |

## State models

### ST-USR-01: Invitation lifecycle
- Criticality: 🔴
- Covers: AC-USR-001, AC-USR-005, AC-USR-006

| T | From | Event | To | Valid |
| --- | --- | --- | --- | --- |
| T1 | — | Admin sends invitation | Invited | Yes |
| T2 | Invited | Invitee accepts | Active | Yes |
| T3 | Invited | Expiry time passes | Expired | Yes |
| T4 | Expired | Invitee accepts | Expired (rejected) | No |

## Open questions
| OQ | Risk | Question | Blocks | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| OQ-USR-001 | 🔴 | Is the invitation expiry 24 h or 72 h? | AC-USR-005 | BA/PO | Open |

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
| 2026-11-08 | Approved | qa.lead | 1 open question (OQ-USR-001) |
