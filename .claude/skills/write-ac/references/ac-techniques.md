# AC techniques (BABOK-aligned)

How to turn a requirement into acceptance criteria. Apply every technique that fits; skip one only when it does not apply, and say why in the report.

Sources:
- IIBA BABOK Guide v3. Techniques: Acceptance and Evaluation Criteria, Business Rules Analysis, Decision Modelling, State Modelling, Data Dictionary, Glossary, Non-Functional Requirements Analysis, User Stories, Use Cases and Scenarios, Reviews. Tasks: 7.2 Verify Requirements, 7.3 Validate Requirements, 5.5 Approve Requirements.
- Quality criteria: BABOK v3 §7.2.4.1 *Characteristics of Requirements and Designs Quality*.
- ISTQB CTFL v4.0.1 §4.5 (acceptance criteria, ATDD).
- Common practice, not BABOK: INVEST, Gherkin (Given/When/Then), specification by example.

## 1. Analyse before writing

This step drives most AC quality. Identify:

| Item | Question |
|---|---|
| Functional requirements | What must the system do? |
| Business rules | Which constraints, limits, formulas and policies apply? |
| Actors | Which roles, users or systems interact? Map each to a role in `project.md`. |
| Preconditions | What is already true before the behaviour? |
| Triggers | What starts the behaviour? |
| Outputs | Which results, messages and data are produced? |
| State changes | What persists or transitions? |
| Data | Which input fields, and what are their type, range and format? |
| External dependencies | Which services, APIs or integrations take part? |
| Impacted existing behaviour | Which existing rules or flows can this change break? (§6) |
| Assumptions | What did you have to assume? Each one becomes an open question (§8). |

Restate the requirement as a user story: **As a** `<role>`, **I want** `<capability>`, **so that** `<benefit>`. Check it against INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable; common practice).

## 2. Classify each requirement (BABOK classification schema)

| `Type` | Meaning |
|---|---|
| `Functional` | Behaviour the solution performs |
| `Non-functional` | How well it performs: performance, security, accessibility, compatibility, localisation, reliability, audit |
| `Transition` | Needed only to move to the new state: data migration, cut-over, temporary rules |

## 3. Choose the form

| Form | Use for | Feeds test technique |
|---|---|---|
| Given / When / Then scenario (scenario-oriented AC, CTFL §4.5.2) | Observable behaviour and flows | Scenario test (ATDD) |
| Business rule (`BR-`) (rule-oriented AC, CTFL §4.5.2) | A policy reused by several scenarios: validation, calculation, authorisation, time-based, configuration, regulatory, data integrity | Covered through scenarios and models |
| Data constraints (`FLD-`) | Every input field with a type, range, length or format | Equivalence partitioning, boundary value analysis |
| Decision table (`DT-`) | An outcome that depends on a combination of conditions, including role × action permissions | Decision table testing |
| State model (`ST-`) | An entity with a lifecycle | State transition testing |

Keep business rules out of GWT. GWT only shows the observable behaviour when a rule applies.

## 4. Scenario classes: one AC per class that applies

- **Happy path**: valid inputs, authorised role.
- **Alternate flow**: another valid path to success.
- **Negative**: invalid input, missing field, wrong state, unauthorised role. State the rejection and the error code or copy.
- **Condition combinations**: write a decision table; one AC per distinct outcome, plus the default.
- **Boundary and edge**:
  - numbers: min−1, min, max, max+1, zero, negative, decimals, rounding
  - length: empty, min, max, max+1
  - empty values: null, empty, whitespace only, missing field, default
  - characters: special characters, Unicode, leading or trailing spaces
  - collections: zero, one, many, max+1, duplicates, ordering
  - date and time: time zone, DST, leap year, expired, future
  - concurrency: double submission, concurrent update, stale data
- **Permission**: who may and may not act, and what each role sees. Write a role × action decision table.
- **Negative security**: another user's or tenant's record, a direct request to an action the role does not have, a changed hidden or read-only value, a replayed request or a reused one-time link. Each is rejected with an error code and no side effects.
- **Idempotency**: an action that changes state and can be repeated (submit, confirm, pay, approve) gets a business rule: what a second identical request does. Write it as a `BR` with an example.
- **Time-based**: cut-off times, time zone, daylight saving change, holidays, expiry at the exact boundary. State the clock and the time zone the rule uses.
- **State transitions**: valid and forbidden transitions of every lifecycle. Write a state model.
- **Non-functional**: performance, security, accessibility, compatibility, localisation, reliability, audit, where they apply.

## 5. Write each Given / When / Then

- **Given**: context that is already true. Join with `And`.
- **When**: one action or event.
- **Then**: an objective pass/fail result: status, error code, copy, computed value or stored record. Join with `And`; contrast with `But`.
- Describe **what**, never **how**. No clicks, screens, selectors, API or database detail. UI steps belong to TCs.
- Pin rules with concrete example values (specification by example, common practice): *limit 100, amount 150 → rejected with ERR-…*.

## 6. Impacted existing behaviour

1. Find the entities this requirement touches in the `Entities` table of `domain.md`.
2. Search other features for the same entities: `grep -rl "<entity>" qa/specs`.
3. Read their Business rules, Decision tables and State models.
4. Cite real IDs only. Never invent an ID.
5. A contradiction you cannot resolve becomes an open question. Never pick a winner silently.
6. Report the result every run. "None, isolated change" is a valid answer; silence is not.

## 7. Rate criticality and likelihood

One scale for AC and TC.

| Icon | Criticality | Meaning if it fails |
|---|---|---|
| 🔴 | Critical | Core behaviour, money, security or data integrity. Must pass to ship. |
| 🟠 | High | Important behaviour, no clean workaround. |
| 🟡 | Medium | Secondary behaviour, tolerable short-term. |
| ⚪ | Low | Cosmetic or rare edge. |

`Likelihood: High` when the AC is new, complex, recently changed or has defect history. It raises test depth one level (`gen-testcase`).

## 8. Surface the gaps

- Every assumption and every ambiguity becomes an open question with an ID and a `Blocks` value.
- An AC built on an unconfirmed assumption names that open question.

## 9. Quality gate (BABOK v3 §7.2.4.1, 9 characteristics)

Reject an AC, rule or model that fails any.

| Criterion | Check |
|---|---|
| Understandable | Clear, short sentences in domain terms (`domain.md` Glossary). |
| Concise | No extra information. |
| Feasible | Buildable within known constraints; otherwise an open question. |
| Atomic | One outcome per AC. |
| Complete | No gap a reader must fill by assuming. |
| Testable | A pass/fail check exists for every Then. |
| Prioritized | Criticality set. |
| Consistent | No conflict with other AC, rules or features (§6). |
| Unambiguous | No "fast", "appropriate", "etc."; values quantified. |

## 10. Coverage, both directions

- **Requirement → AC**: every requirement, rule and visible behaviour in the ticket maps to at least one AC, rule or model.
- **AC → test**: every AC, rule, field, decision rule and transition can be covered by a test.
- Report counts by type and criticality, and which scenario classes were skipped and why.

## 11. Final gate before review

- [ ] Every requirement has at least one AC (§10)
- [ ] Every AC is testable and atomic (§9)
- [ ] Business rules kept out of GWT (§3)
- [ ] No implementation detail (§5)
- [ ] Error codes or copy specified for every rejection (§5)
- [ ] Every input field has a data constraint row (§3)
- [ ] Condition combinations written as decision tables (§4)
- [ ] Permissions written as a role × action decision table (§4)
- [ ] Every lifecycle written as a state model, forbidden transitions included (§4)
- [ ] Non-functional aspects covered where they apply (§4)
- [ ] Impacted existing behaviour reported (§6)
- [ ] Every assumption is an open question (§8)
