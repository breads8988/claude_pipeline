# TC: Sign-in (SGN)

Golden example of a second feature linked to USR through the impact graph. Not a real feature.

| Field | Value |
| --- | --- |
| AC file | `qa/specs/_example-sgn/ac.md` |
| Status | `Approved` |
| Approved by | qa.lead |
| Approved on | 2026-11-21 |
| Last updated | 2026-11-21 |

## Coverage summary
| Technique | Items identified | Covered | Blocked | Coverage |
| --- | --- | --- | --- | --- |
| Scenario (AC) | 3 | 3 | 0 | 100% |
| Business rules | 1 | 1 | 0 | 100% |
| EP | 0 | 0 | 0 | — |
| BVA | 0 | 0 | 0 | — |
| Decision table | 0 | 0 | 0 | — |
| State transition | 0 | 0 | 0 | — |

## TC-SGN-001: Sign in with the email in upper case
| Field | Value |
| --- | --- |
| Covers AC | AC-SGN-001 |
| Screens | SCR-sign-in, SCR-users |
| Technique | Scenario |
| Coverage items | `AC-SGN-001`, `BR-SGN-001` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Account `new.user+001@example.test` has status = `Active`.

**Test data**
| Field | Value |
| --- | --- |
| Email | `NEW.USER+001@EXAMPLE.TEST` |
| Password | from `qa/test-accounts.local.md` |

**Steps**
1. Navigate to /sign-in.
2. Enter `NEW.USER+001@EXAMPLE.TEST` in the Email field.
3. Enter the password in the Password field.
4. Click `Sign in`.

**Expected result**
- The user list is displayed.

## TC-SGN-002: Reject a wrong password
| Field | Value |
| --- | --- |
| Covers AC | AC-SGN-002 |
| Screens | SCR-sign-in |
| Technique | Scenario |
| Coverage items | `AC-SGN-002` |
| Role | Admin |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Candidate` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- Account `new.user+001@example.test` has status = `Active`.

**Test data**
| Field | Value |
| --- | --- |
| Email | `new.user+001@example.test` |
| Password | `Wrong-Pass-01` |

**Steps**
1. Navigate to /sign-in.
2. Enter `new.user+001@example.test` in the Email field.
3. Enter `Wrong-Pass-01` in the Password field.
4. Click `Sign in`.

**Expected result**
- Error `Email or password is incorrect.` is displayed.
- The sign-in page remains displayed.

## TC-SGN-003: Reject sign-in for a pending account
| Field | Value |
| --- | --- |
| Covers AC | AC-SGN-003 |
| Screens | SCR-sign-in |
| Technique | Scenario |
| Coverage items | `AC-SGN-003`, `BR-SGN-001` |
| Role | Anonymous |
| Type | Functional |
| Priority | 🔴 |
| Automation | `Not yet` |
| Status | `Active` |
| Blocked by | — |

**Precondition**
- An invitation for `pending.user+002@example.test` has status = `Invited`; its account has status = `Pending`.

**Test data**
| Field | Value |
| --- | --- |
| Email | `pending.user+002@example.test` |
| Password | `Any-Pass-02` |

**Steps**
1. Navigate to /sign-in.
2. Enter `pending.user+002@example.test` in the Email field.
3. Enter `Any-Pass-02` in the Password field.
4. Click `Sign in`.

**Expected result**
- Error `Email or password is incorrect.` is displayed.
- The sign-in page remains displayed.

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
| 2026-11-21 | Approved | qa.lead | — |
