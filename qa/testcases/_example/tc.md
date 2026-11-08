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
| Technique | Items identified | Covered | Blocked | Coverage |
| --- | --- | --- | --- | --- |
| Scenario (AC) | 11 | 9 | 2 | 81% |
| Business rules | 4 | 4 | 0 | 100% |
| EP | 11 | 11 | 0 | 100% |
| BVA | 6 | 6 | 0 | 100% |
| Decision table | 4 | 4 | 0 | 100% |
| State transition | 10 | 7 | 3 | 70% |

## Test analysis

EP partitions (one TC per invalid partition):

| FLD | Partition | Kind | Example value |
| --- | --- | --- | --- |
| FLD-USR-01 | valid | valid | `new.user+001@example.test` |
| FLD-USR-01 | empty | invalid | empty |
| FLD-USR-01 | whitespace only | invalid | three spaces |
| FLD-USR-01 | no @ | invalid | `new.user.example.test` |
| FLD-USR-01 | two @ | invalid | `new@user@example.test` |
| FLD-USR-01 | contains space | invalid | `new user@example.test` |
| FLD-USR-01 | local part over 64 characters | invalid | 65 × `a` + `@example.test` |
| FLD-USR-01 | empty local part | invalid | `@example.test` |
| FLD-USR-01 | missing domain | invalid | `new.user@` |
| FLD-USR-01 | missing TLD | invalid | `new.user@example` |
| FLD-USR-01 | domain label over 63 characters | invalid | `new.user@` + 64 × `b` + `.test` |

BVA values (depth 🟠 → 3-value, step 1 character):

| FLD | Label | Value | TC |
| --- | --- | --- | --- |
| FLD-USR-01 | min-1 | 5 | TC-USR-009 |
| FLD-USR-01 | min | 6 | TC-USR-002 |
| FLD-USR-01 | min+1 | 7 | TC-USR-002 |
| FLD-USR-01 | max-1 | 253 | TC-USR-002 |
| FLD-USR-01 | max | 254 | TC-USR-002 |
| FLD-USR-01 | max+1 | 255 | TC-USR-010 |

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
- Logged in as Admin. No user or invitation exists for the test email.

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

## TC-USR-002: Accept emails at the boundary lengths
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-001 |
| Technique | BVA |
| Coverage items | `FLD-USR-01 BVA: min = 6`, `FLD-USR-01 BVA: min+1 = 7`, `FLD-USR-01 BVA: max-1 = 253`, `FLD-USR-01 BVA: max = 254` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin. No user or invitation exists for any test email.

**Test data**
| Field | Value |
| --- | --- |
| Email, row 1 (6 characters) | `a@b.cd` |
| Email, row 2 (7 characters) | `a@b.cde` |
| Email, row 3 (253 characters) | 64 × `a` + `@` + 63 × `b` + `.` + 63 × `c` + `.` + 55 × `d` + `.test` |
| Email, row 4 (254 characters) | 64 × `a` + `@` + 63 × `b` + `.` + 63 × `c` + `.` + 56 × `d` + `.test` |

Data-driven: run the steps once per test data row. Each row is one execution.

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter the email of the current row in the Email field.
4. Click `Send invite`.

**Expected result**
- Toast `Invitation sent.` is displayed.
- The users grid lists the email with status = `Invited`.

## TC-USR-003: Reject an email: empty
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `AC-USR-002`, `FLD-USR-01 EP: empty` |
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

## TC-USR-004: Reject an email: whitespace only
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: whitespace only` |
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
| Email | three spaces |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter three spaces in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-005: Reject an email: no @
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: no @` |
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

## TC-USR-006: Reject an email: two @
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: two @` |
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
| Email | `new@user@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new@user@example.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-007: Reject an email: contains space
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: contains space` |
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
| Email | `new user@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new user@example.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-008: Reject an email: local part over 64 characters
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: local part over 64 characters` |
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
| Email | 65 × `a` + `@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter the 78-character email in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-009: Reject an email one character below the minimum length
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
| Email (5 characters) | `a@b.c` |

`a@b.c` meets the FLD-USR-01 format (one-character labels are allowed). Only the length rule rejects it, so a missing length check is not masked by the format check.

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `a@b.c` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-010: Reject an email one character above the maximum length
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
| Email (255 characters) | 64 × `a` + `@` + 63 × `b` + `.` + 63 × `c` + `.` + 57 × `d` + `.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter the 255-character email in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-011: Reject an invite for an existing user, any letter case
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-003 |
| Technique | Decision table, State transition |
| Coverage items | `AC-USR-003`, `BR-USR-002`, `DT-USR-01.R2`, `ST-USR-01.T7` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin. User `ana@example.test` exists with an accepted invitation.

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

## TC-USR-012: Reject an invitation request sent by a Viewer
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
| Request | `POST /api/invitations` with email `viewer.try@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Send the request from the test data with the browser JavaScript tool (`fetch`, same session).

**Expected result**
- Response status = 403 and error code = `ERR-USR-03`.
- Response message = `You do not have permission to invite users.`

## TC-USR-013: Invitation expires after the expiry time
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-005 |
| Technique | State transition |
| Coverage items | `AC-USR-005`, `ST-USR-01.T3` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Blocked` |
| Blocked by | OQ-USR-001 |

**Precondition**
- Logged in as Admin.
- Seeded on staging: invitation for `new.user+013@example.test` created TBD (OQ-USR-001) ago, status = `Invited`.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+013@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Locate the row for `new.user+013@example.test`.

**Expected result**
- The row displays status = `Expired`.

## TC-USR-014: Expiry has no effect on an accepted invitation
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-011 |
| Technique | State transition |
| Coverage items | `AC-USR-011`, `ST-USR-01.T5` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin.
- Seeded on staging: invitation for `new.user+014@example.test` accepted, created 80 h ago (past both candidate expiry times).

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+014@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Locate the row for `new.user+014@example.test`.

**Expected result**
- The row displays status = `Accepted`.
- No side effects: no `Expired` status displayed.

## TC-USR-015: Invitee accepts a valid invitation
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-006 |
| Technique | State transition |
| Coverage items | `AC-USR-006`, `ST-USR-01.T2` |
| Role | Anonymous |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Seeded on staging: invitation for `new.user+015@example.test` with status = `Invited`; its link is in the test mailbox.

**Test data**
| Field | Value |
| --- | --- |
| Password | `Synthetic#Pass15` |

**Steps**
1. Navigate to the invitation link.
2. Enter `Synthetic#Pass15` in the Password field.
3. Click `Accept invitation`.

**Expected result**
- The dashboard is displayed.
- The profile menu displays `new.user+015@example.test`.

## TC-USR-016: Viewer has no invite action
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-007 |
| Technique | Scenario |
| Coverage items | `AC-USR-007` |
| Role | Viewer |
| Type | Functional |
| Priority | 🟠 |
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

## TC-USR-017: Accepting an expired invitation is rejected
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-008 |
| Technique | State transition |
| Coverage items | `AC-USR-008`, `BR-USR-004`, `ST-USR-01.T6` |
| Role | Anonymous |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Seeded on staging: invitation for `new.user+017@example.test` created 80 h ago, status = `Expired`; its link is in the test mailbox.

**Test data**
| Field | Value |
| --- | --- |
| Password | `Synthetic#Pass17` |

**Steps**
1. Navigate to the invitation link.
2. Enter `Synthetic#Pass17` in the Password field.
3. Click `Accept invitation`.

**Expected result**
- Copy `This invitation is no longer valid.` is displayed.
- No side effects: no account is created and the dashboard is not displayed.

## TC-USR-018: Reusing an accepted invitation link is rejected
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-008 |
| Technique | State transition |
| Coverage items | `ST-USR-01.T4` |
| Role | Anonymous |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Seeded on staging: invitation for `new.user+018@example.test` already accepted; its link is in the test mailbox.

**Test data**
| Field | Value |
| --- | --- |
| Password | `Synthetic#Pass18` |

**Steps**
1. Navigate to the invitation link.
2. Enter `Synthetic#Pass18` in the Password field.
3. Click `Accept invitation`.

**Expected result**
- Copy `This invitation is no longer valid.` is displayed.
- No side effects: the password of the account is unchanged.

## TC-USR-019: Double click on Send invite creates one invitation
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-009 |
| Technique | Scenario, Error guessing |
| Coverage items | `AC-USR-009`, `BR-USR-003`, `EG: double submission` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin. No user or invitation exists for the test email.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+019@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new.user+019@example.test` in the Email field.
4. Double-click `Send invite`.

**Expected result**
- The users grid lists `new.user+019@example.test` once, with status = `Invited`.

## TC-USR-020: Re-invite an email with a pending invitation
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-010 |
| Technique | State transition |
| Coverage items | `AC-USR-010`, `ST-USR-01.T8` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Blocked` |
| Blocked by | OQ-USR-002 |

**Precondition**
- Logged in as Admin.
- Seeded on staging: invitation for `new.user+020@example.test` with status = `Invited`.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+020@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new.user+020@example.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- TBD (OQ-USR-002): invitation resent, new invitation created, or rejected.

## TC-USR-021: Re-invite an email with an expired invitation
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-010 |
| Technique | State transition |
| Coverage items | `ST-USR-01.T9` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Blocked` |
| Blocked by | OQ-USR-002 |

**Precondition**
- Logged in as Admin.
- Seeded on staging: invitation for `new.user+021@example.test` with status = `Expired`.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+021@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new.user+021@example.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- TBD (OQ-USR-002): invitation resent, new invitation created, or rejected.

## TC-USR-022: Reject an email: empty local part
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: empty local part` |
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
| Email | `@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `@example.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-023: Reject an email: missing domain
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: missing domain` |
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
| Email | `new.user@` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new.user@` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-024: Reject an email: missing TLD
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: missing TLD` |
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
| Email | `new.user@example` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new.user@example` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-025: Reject an email: domain label over 63 characters
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-002 |
| Technique | EP |
| Coverage items | `FLD-USR-01 EP: domain label over 63 characters` |
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
| Email | `new.user@` + 64 × `b` + `.test` |

**Steps**
1. Navigate to Settings › Users.
2. Click `Invite user`.
3. Enter `new.user@` + 64 × `b` + `.test` in the Email field.
4. Click `Send invite`.

**Expected result**
- Error `Enter a valid email.` is displayed under the Email field.
- No side effects: no new row in the users grid.

## TC-USR-026: Reject an invitation request by a Viewer for an existing user
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-004 |
| Technique | Decision table |
| Coverage items | `AC-USR-004`, `DT-USR-01.R4` |
| Role | Viewer |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Viewer. User `ana@example.test` exists.

**Test data**
| Field | Value |
| --- | --- |
| Request | `POST /api/invitations` with email `ana@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Send the request from the test data with the browser JavaScript tool (`fetch`, same session).

**Expected result**
- Response status = 403 and error code = `ERR-USR-03`.
- No side effects: no invitation created; the response does not reveal that the user exists.

## TC-USR-027: Expiry has no effect on an expired invitation
| Field | Value |
| --- | --- |
| Covers AC | AC-USR-011 |
| Technique | State transition |
| Coverage items | `AC-USR-011`, `ST-USR-01.T10` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Logged in as Admin.
- Seeded on staging: invitation for `new.user+027@example.test` created 160 h ago, status = `Expired`.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+027@example.test` |

**Steps**
1. Navigate to Settings › Users.
2. Locate the row for `new.user+027@example.test`.

**Expected result**
- The row displays status = `Expired`.
- No side effects: no second expiry event in the row history.

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
| 2026-11-08 | Approved | qa.lead | TC-USR-013 blocked by OQ-USR-001; TC-USR-020 and TC-USR-021 blocked by OQ-USR-002. TC-USR-022 to 027 are newer than TC-USR-001 to 021; IDs are never renumbered |
