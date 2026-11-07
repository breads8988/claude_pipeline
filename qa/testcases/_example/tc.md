# TC: User invitation (USR)

Golden example: the reference for level of detail. Not a real feature.

| Field | Value |
| --- | --- |
| AC file | `qa/specs/_example/ac.md` |
| Status | `Approved` |
| Approved by | qa.lead |
| Approved on | 2026-11-07 |
| Last updated | 2026-11-07 |

## TC-USR-001: Invite a user with a valid email
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-001 |
| Role | Admin |
| Type | Smoke |
| Priority | P1 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin. No user exists with the test email.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+001@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new.user+001@example.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- Toast `Invitation sent.` is displayed.
- The users grid lists `new.user+001@example.test` with status = `Invited`.

## TC-USR-002: Reject an invite for an existing email
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Role | Admin |
| Type | Negative |
| Priority | P1 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin. User `ana@example.test` exists.

**Test data**
| Field | Value |
| --- | --- |
| Email | `ana@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `ana@example.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `This email is already in use.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-003: Viewer does not see the invite button
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-003 |
| Role | Viewer |
| Type | Negative |
| Priority | P1 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Viewer.

**Test data**
| Field | Value |
| --- | --- |
| — | — |

**Steps**
1. Navigate to Settings › Users.

**Expected result**
- The `Invite user` button is hidden.

## TC-USR-004: Invitation link expires after the expiry time
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-004 |
| Role | Admin |
| Type | Boundary |
| Priority | P2 |
| Automation | `Not yet` |
| Status | `Blocked` |
| Blocked by | OQ-USR-001 |

**Precondition**
- An invitation for `new.user+004@example.test` was sent and not accepted.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+004@example.test` |
| Expiry | TBD (OQ-USR-001) |

**Steps**
1. Wait until the expiry time passes, or move the invitation date earlier on staging.
2. Navigate to the invitation link.

**Expected result**
- The page displays `This invitation has expired.`
- TBD (OQ-USR-001): status transitions to `Expired` after 24 h or 72 h.

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
| 2026-11-07 | Approved | qa.lead | TC-USR-004 blocked by OQ-USR-001 |
