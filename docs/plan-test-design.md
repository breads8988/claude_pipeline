# Plan: BABOK in write-ac, ISTQB in gen-testcase

Status: proposed 2026-11-07 · Decisions 1, 2, 4, 5 agreed 2026-11-08 · Decision 3 pending · Blocks the pilot

## Why
- `write-ac` and `gen-testcase` define format only. They do not say how to analyse a requirement or how to design tests.
- Without method, AC miss rules and combinations, and TCs are written by intuition with no coverage measure.

## Sources

| Source | Version | Used for |
|---|---|---|
| IIBA BABOK Guide | v3 (current guide). The Business Analysis Standard (2025) complements it, same 6 knowledge areas and 30 tasks | Requirement analysis, AC quality, business rules, decision and state models |
| IIBA "9 quality criteria for requirements" | — | AC quality gate |
| ISTQB CTFL syllabus | v4.0.1, chapter 4 (test analysis and design), chapter 5 (risk, defect reports) | Test techniques, coverage items, risk-based depth, defect report fields |
| Existing skill `gen-ac-from-jira` (user's) | — | Ported: analysis checklist, scenario classes, GWT rules, criticality, final gate |

## Core idea: AC models feed test techniques

BABOK models written in the AC file are the direct input of ISTQB black-box techniques.

| BABOK model in `ac.md` | ISTQB technique in `tc.md` | Coverage items |
|---|---|---|
| **Data constraints** table (data dictionary): field, type, required, min, max, format | Equivalence partitioning + boundary value analysis | Valid and invalid partitions; boundary values |
| **Decision table** (decision modelling): conditions → outcome per rule | Decision table testing | Feasible rules (columns) |
| **State model** (state modelling): states, events, valid transitions | State transition testing | Valid transitions; invalid transitions for Critical |
| **Role × action matrix** (business rules, permissions) | Decision table testing on roles | Each role × action cell |
| **GWT scenarios** (acceptance criteria, scenarios) | Scenario test (ATDD order: positive → negative → non-functional) | Each scenario |
| `domain.md` checklist + error guessing list | Checklist-based, error guessing | Each checklist item |

New IDs make each coverage item traceable:

| Item | ID | Example |
|---|---|---|
| Data constraint (field) | `FLD-<CODE>-NN` | `FLD-USR-01` Email |
| Decision table / rule | `DT-<CODE>-NN` / `.R<n>` | `DT-USR-01.R3` |
| State model / transition | `ST-<CODE>-NN` / `.T<n>` | `ST-USR-01.T2` |

## Phase A · BABOK in `write-ac`

| # | Item | Files |
|---|---|---|
| A1 | Port `gen-ac-from-jira` techniques, made generic (no vault, entity notes or project names): requirement analysis checklist, user story + INVEST, scenario classes, GWT rules, criticality, gaps, two-way coverage, final gate | `write-ac/references/ac-techniques.md` |
| A2 | Requirement classification (BABOK schema) per AC: `Functional` · `Non-functional` · `Transition` (data migration, cut-over) | `qa/_templates/ac.md`, `naming.md` |
| A3 | New AC sections, filled when the requirement has them: **Data constraints**, **Decision tables**, **State model**, **Role × action matrix** | `qa/_templates/ac.md` |
| A4 | Impacted existing behaviour: search other features' Business Rules, decision tables and state models that share the same entities (`domain.md` entity list). Cite real IDs only; conflicts become open questions | `write-ac/SKILL.md`, `domain.md` (Entities table) |
| A5 | AC are implementation-free: behaviour, not UI clicks. UI steps live in TCs only | `ac-techniques.md`, golden example |
| A6 | Quality gate = IIBA 9 criteria (understandable, concise, feasible, atomic, complete, testable, prioritized, consistent, unambiguous) + port's final checklist | `ac-techniques.md`, `ac-reviewer.md` |
| A7 | `ac-reviewer` = BABOK *Verify requirements* (checklist). `/approve` = *Validate requirements* (human) | `ac-reviewer.md` |

## Phase B · ISTQB in `gen-testcase`

| # | Item | Files |
|---|---|---|
| B1 | Technique reference: EP, BVA (2-value / 3-value), decision table, state transition, scenario/ATDD, checklist, error guessing. Definitions, coverage items, worked examples | `gen-testcase/references/test-design-techniques.md` |
| B2 | Test analysis step: list test conditions from every AC, BR, FLD, DT rule, ST transition, role cell, checklist item before writing TCs | `gen-testcase/SKILL.md` |
| B3 | Technique selection matrix (table above) + depth by risk | `test-design-techniques.md` |
| B4 | Risk-based depth: risk = AC criticality (impact) × likelihood (new, complex, changed, defect history) | `test-design-techniques.md` |
| B5 | TC fields: `Technique`, `Coverage items` (e.g. `FLD-USR-01: max+1`, `DT-USR-01.R3`, `ST-USR-01.T2`) | `qa/_templates/tc.md`, `naming.md` |
| B6 | Coverage summary in `tc.md` header: per technique, items total / covered / % | `qa/_templates/tc.md` |
| B7 | Rules from ISTQB: cover the story fully, nothing beyond it; no duplicate TCs; one TC may cover several items when it stays readable | `gen-testcase/SKILL.md` |
| B8 | `tc-reviewer` checks: every coverage item has a TC, technique fits the model, depth matches risk | `tc-reviewer.md` |
| B9 | Defect report fields (ISTQB ch. 5): `Severity` (tester) separate from `Priority to fix` (PO); context: TC, technique, test data | `qa/_templates/bug.md` |

### Depth by risk (proposed defaults)

| Risk | EP | BVA | Decision table | State transition |
|---|---|---|---|---|
| High (Critical AC, or High + likely) | All partitions | 3-value | All feasible rules | All transitions, valid and invalid |
| Medium | All partitions | 2-value | All feasible rules | Valid transitions (0-switch) |
| Low | Valid + main invalid | 2-value on main field | Merge same-outcome rules | All states |

## Phase C · Examples, lint, validator

| # | Item |
|---|---|
| C1 | Rewrite the `_example` feature: implementation-free AC; add FLD, DT, ST, role matrix; TCs with technique and coverage items; coverage summary |
| C2 | Vocabulary: keep ISTQB and BABOK terms out of the banned list; add domain-neutral checks if the pilot shows misses |
| C3 | Validator (pulled forward from phase 4): every FLD, DT rule, ST transition and role cell is referenced by at least one TC; every TC's coverage items exist |

## Order
1. Phase A → commit.
2. Phase B → commit.
3. Phase C → commit, run lint and tests on the example.
4. Pilot on one real ticket (existing `docs/plan.md`).

## Decisions

| # | Decision |
|---|---|
| 1 | One scale for AC criticality and TC priority, with icons: 🔴 Critical · 🟠 High · 🟡 Medium · ⚪ Low. TC priority = criticality of the AC it covers (highest one). `P1`–`P3` is retired everywhere (templates, naming, run file, smoke scope = 🔴). |
| 2 | AC are implementation-free. Clicks and screens live in TCs only. |
| 3 | Depth by risk: pending explanation and review. |
| 4 | Non-functional AC stay in AC. Their TCs are typed `Non-functional` and run only when they can be checked manually on staging. |
| 5 | Keep `gen-ac-from-jira` for its current project. Port a generic copy into `write-ac`. |
