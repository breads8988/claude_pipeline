# TC: User invitation (USR)

Golden example: the reference for level of detail. Not a real feature.

| Field | Value |
| --- | --- |
| AC file | `qa/specs/_example/ac.md` |
| Status | `Approved` |
| Approved by | qa.lead |
| Approved on | 2026-11-08 |
| Last updated | 2026-11-08 |

## Coverage summary
| Technique | Items identified | Covered | Coverage |
| --- | --- | --- | --- |
| Scenario (AC) | 6 | 6 | 100% |
| Business rules | 2 | 2 | 100% |
| EP | 2 | 2 | 100% |
| BVA | 4 | 4 | 100% |
| Decision table | 3 | 3 | 100% |
| State transition | 4 | 4 | 100% |

## TC-USR-001: Invite a person with a valid email
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-001 |
| Technique | Scenario, Decision table, State transition, EP |
| Coverage items | `AC-USR-001`, `DT-USR-01.R1`, `ST-USR-01.T1`, `FLD-USR-01 EP: valid` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
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

## TC-USR-002: Reject an email without @
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `AC-USR-002`, `FLD-USR-01 EP: invalid, format` |
| Role | Admin |
| Type | Functional |
| Priority | 🟠 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user.example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new.user.example.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-003: Reject an empty email
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: invalid, empty` |
| Role | Admin |
| Type | Functional |
| Priority | 🟠 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin.

**Test data**
| Field | Value |
| --- | --- |
| Email | empty |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Clear the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-004: Accept emails at the minimum and maximum length
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-001 |
| Technique | BVA |
| Coverage items | `FLD-USR-01 BVA: min = 6`, `FLD-USR-01 BVA: max = 254` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin. No user exists with either test email.

**Test data**
| Field | Value |
| --- | --- |
| Email (6 chars) | `a@b.cd` |
| Email (254 chars) | 242 × `a` + `@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`, enter the 6-character email, click `Send invite`.
3. Click `Invite user`, enter the 254-character email, click `Send invite`.

**Expected result**
- Toast `Invitation sent.` is displayed after each invite.
- The users grid lists both emails with status = `Invited`.

## TC-USR-005: Reject an email one character below the minimum
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | BVA |
| Coverage items | `FLD-USR-01 BVA: min-1 = 5` |
| Role | Admin |
| Type | Functional |
| Priority | 🟠 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin.

**Test data**
| Field | Value |
| --- | --- |
| Email (5 chars) | `a@b.c` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `a@b.c` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-006: Reject an email one character above the maximum
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | BVA |
| Coverage items | `FLD-USR-01 BVA: max+1 = 255` |
| Role | Admin |
| Type | Functional |
| Priority | 🟠 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin.

**Test data**
| Field | Value |
| --- | --- |
| Email (255 chars) | 243 × `a` + `@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter the 255-character email in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-007: Reject an invite for an existing email, any letter case
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-003 |
| Technique | Decision table |
| Coverage items | `AC-USR-003`, `BR-USR-002`, `DT-USR-01.R2` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin. User `ana@example.test` exists.

**Test data**
| Field | Value |
| --- | --- |
| Email | `Ana@Example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `Ana@Example.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `This email is already in use.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-008: Viewer is not permitted to invite
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-004 |
| Technique | Decision table |
| Coverage items | `AC-USR-004`, `BR-USR-001`, `DT-USR-01.R3` |
| Role | Viewer |
| Type | Functional |
| Priority | 🔴 |
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

## TC-USR-009: Invitee accepts a valid invitation
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-006 |
| Technique | State transition |
| Coverage items | `AC-USR-006`, `ST-USR-01.T2` |
| Role | Invitee (no login) |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- An invitation for `new.user+009@example.test` has status = `Invited`.

**Test data**
| Field | Value |
| --- | --- |
| Password | `Synthetic#Pass9` |

**Steps**
1. Navigate to the invitation link.
2. Enter `Synthetic#Pass9` in the Password field.
3. Click `Accept invitation`.

**Expected result**
- The dashboard is displayed for `new.user+009@example.test`.
- In Settings › Users (as Admin), the user has status = `Active`.

## TC-USR-010: Invitation expires after the expiry time
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-005 |
| Technique | State transition |
| Coverage items | `AC-USR-005`, `ST-USR-01.T3` |
| Role | Invitee (no login) |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Blocked` |
| Blocked by | OQ-USR-001 |

**Precondition**
- An invitation for `new.user+010@example.test` has status = `Invited`.

**Test data**
| Field | Value |
| --- | --- |
| Expiry | TBD (OQ-USR-001) |

**Steps**
1. Move the invitation date earlier than the expiry time on staging.
2. Navigate to the invitation link.

**Expected result**
- The page displays `This invitation has expired.`
- TBD (OQ-USR-001): status transitions to `Expired` after 24 h or 72 h.

## TC-USR-011: Accepting an expired invitation is rejected
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-005 |
| Technique | State transition |
| Coverage items | `ST-USR-01.T4` |
| Role | Invitee (no login) |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Blocked` |
| Blocked by | OQ-USR-001 |

**Precondition**
- An invitation for `new.user+011@example.test` has status = `Expired`.

**Test data**
| Field | Value |
| --- | --- |
| Password | `Synthetic#Pass11` |

**Steps**
1. Navigate to the invitation link.

**Expected result**
- The page displays `This invitation has expired.`
- The `Accept invitation` button is hidden.
- No side effects: status remains `Expired`.

## TC-USR-012: Double click on Send invite creates one invitation
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-001 |
| Technique | Error guessing |
| Coverage items | `AC-USR-001`, `EG: double submission` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin. No user exists with the test email.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+012@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new.user+012@example.test` in the Email field.
4. Double-click `Send invite`.

**Expected result**
- The users grid lists `new.user+012@example.test` once, with status = `Invited`.

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
| 2026-11-08 | Approved | qa.lead | TC-USR-010 and TC-USR-011 blocked by OQ-USR-001 |
