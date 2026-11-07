# AC: User invitation (USR)

Golden example: the reference for level of detail. Not a real feature.

| Field | Value |
| --- | --- |
| Jira | ABC-101 |
| Status | `Approved` |
| Approved by | qa.lead |
| Approved on | 2026-11-07 |
| Open questions | 1 |
| Last updated | 2026-11-07 |

## Scenarios

### AC-USR-001: Admin invites a user with a valid email
- Criticality: Critical
- Status: Active
- Given: an Admin is on Settings › Users
- When: the Admin enters a valid, unused email and clicks `Send invite`
- Then: toast `Invitation sent.` is displayed and the user is listed with status = `Invited`

### AC-USR-002: Duplicate email is rejected
- Criticality: High
- Status: Active
- Given: `ana@example.test` already exists as a user
- When: the Admin submits an invite for `ana@example.test`
- Then: rejected with ERR-USR-01: `This email is already in use.`; no side effects: no invitation created

### AC-USR-003: Viewer is not permitted to invite
- Criticality: Critical
- Status: Active
- Given: a Viewer is on Settings › Users
- When: the page loads
- Then: the `Invite user` button is hidden

### AC-USR-004: Invitation link expires
- Criticality: High
- Status: Active
- Given: an invitation was sent and not accepted
- When: the expiry time passes
- Then: the link displays `This invitation has expired.` and status transitions to `Expired`

## Business rules
| Rule ID | Rule | Source |
| --- | --- | --- |
| BR-USR-001 | Only Admin can invite users. | ABC-101 |
| BR-USR-002 | One user per email address. | ABC-101 |

## Open questions
| OQ | Risk | Question | Blocks | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| OQ-USR-001 | 🔴 | Is the invitation expiry 24 h or 72 h? | AC-USR-004 | BA/PO | Open |

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
| 2026-11-07 | Approved | qa.lead | 1 open OQ (OQ-USR-001) |
