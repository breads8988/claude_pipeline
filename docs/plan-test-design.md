# Plan: BABOK in write-ac, ISTQB in gen-testcase

Status: all decisions agreed 2026-11-08 · Phases A, B, C built 2026-11-08 · Next: pilot

## Why
- `write-ac` and `gen-testcase` define format only. They do not say how to analyse a requirement or how to design tests.
- Without method, AC miss rules and combinations, and TCs are written by intuition with no coverage measure.

## Sources

| Source | Version | Used for |
|---|---|---|
| IIBA BABOK Guide | v3 (current guide). The Business Analysis Standard (2025) complements it, same 6 knowledge areas and 30 tasks | Requirement analysis, AC quality, business rules, decision and state models |
| BABOK v3 §7.2.4.1 Characteristics of Requirements and Designs Quality (9) | — | AC quality gate |
| ISTQB CTFL syllabus | v4.0.1, 2024-09-15, official PDF; chapter 4 (test analysis and design), chapter 5 (risk, defect reports) | Test techniques, coverage items, risk-based depth, defect report fields |
| Existing skill `gen-ac-from-jira` (user's) | — | Ported: analysis checklist, scenario classes, GWT rules, criticality, final gate |

## Core idea: AC models feed test techniques

BABOK models written in the AC file are the direct input of ISTQB black-box techniques.

| BABOK model in `ac.md` | ISTQB technique in `tc.md` | Coverage items |
|---|---|---|
| **Data constraints** table (data dictionary): field, type, required, min, max, format | Equivalence partitioning + boundary value analysis | Valid and invalid partitions; boundary values |
| **Decision table** (decision modelling): conditions → outcome per rule | Decision table testing | Feasible rules (columns) |
| **State model** (state modelling): states, events, valid transitions | State transition testing | Valid transitions; invalid transitions for Critical |
| **Role × action** permissions: written as a decision table (`DT`), not a separate matrix | Decision table testing | Each feasible column |
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
| A3 | New AC sections, filled when the requirement has them: **Data constraints**, **Decision tables**, **State model** (role × action goes in a decision table) | `qa/_templates/ac.md` |
| A4 | Impacted existing behaviour: search other features' Business Rules, decision tables and state models that share the same entities (`domain.md` entity list). Cite real IDs only; conflicts become open questions | `write-ac/SKILL.md`, `domain.md` (Entities table) |
| A5 | AC are implementation-free: behaviour, not UI clicks. UI steps live in TCs only | `ac-techniques.md`, golden example |
| A6 | Quality gate = BABOK v3 §7.2.4.1 (9 characteristics) (understandable, concise, feasible, atomic, complete, testable, prioritized, consistent, unambiguous) + port's final checklist | `ac-techniques.md`, `ac-reviewer.md` |
| A7 | `ac-reviewer` = BABOK 7.2 *Verify Requirements* (checklist). `/approve` = 5.5 *Approve Requirements* with a 7.3 *Validate* value question (human) | `ac-reviewer.md` |

## Phase B · ISTQB in `gen-testcase`

| # | Item | Files |
|---|---|---|
| B1 | Technique reference: EP, BVA (2-value / 3-value), decision table, state transition, scenario/ATDD, checklist, error guessing. Definitions, coverage items, worked examples | `gen-testcase/references/test-design-techniques.md` |
| B2 | Test analysis step: list test conditions from every AC, BR, FLD, DT rule, ST transition, checklist item before writing TCs | `gen-testcase/SKILL.md` |
| B3 | Technique selection matrix (table above) + depth by risk | `test-design-techniques.md` |
| B4 | Risk-based depth: risk = AC criticality (impact) × likelihood (new, complex, changed, defect history) | `test-design-techniques.md` |
| B5 | TC fields: `Technique`, `Coverage items` (e.g. `FLD-USR-01 EP: empty`, `FLD-USR-01 BVA: max+1 = 255`, `DT-USR-01.R3`, `ST-USR-01.T2`) | `qa/_templates/tc.md`, `naming.md` |
| B6 | Coverage summary in `tc.md` header: per technique, items total / covered / % | `qa/_templates/tc.md` |
| B7 | Rules from ISTQB: cover the story fully, nothing beyond it; no duplicate TCs; one TC may cover several items when it stays readable | `gen-testcase/SKILL.md` |
| B8 | `tc-reviewer` checks: every coverage item has a TC, technique fits the model, depth matches risk | `tc-reviewer.md` |
| B9 | Defect report fields (ISTQB ch. 5): `Severity` (tester) separate from `Priority to fix` (PO); context: TC, technique, test data | `qa/_templates/bug.md` |

### Depth by risk

Source: ISTQB CTFL v4.0.1 (2024-09-15), read in full for chapters 4 and 5.

What the syllabus states:

| Section | Statement |
|---|---|
| 5.2.3 | Product risk analysis determines "the test techniques to be employed and the coverage to be achieved" and may influence thoroughness. |
| 5.2 | Risk level = likelihood × impact (quantitative), or a risk matrix (qualitative). |
| 4.2.1 | EP: one test per partition is sufficient; 100% = every valid and invalid partition covered. *Each Choice* coverage for several fields, no combinations. |
| 4.2.2 | 3-value BVA is "more rigorous than 2-value BVA" and may detect defects 2-value misses. |
| 4.2.3 | Decision table: coverage items = feasible columns. Tables may be minimised (merge columns where a condition does not change the outcome). With many conditions, a minimised table or a risk-based approach may reduce the rules. |
| 4.2.4 | Valid transitions (0-switch) is "the most widely used" criterion. All transitions (valid + invalid) "should be a minimum requirement for mission and safety-critical software". One invalid transition per test case, to avoid defect masking. |
| 4.4 | Checklists hold no automatically checkable items and are updated regularly. Error guessing and exploratory testing complement formal techniques. |
| 4.5 | ATDD order: positive, negative, then non-functional. Cover every story characteristic, nothing beyond it, no two tests for the same characteristic. |
| 5.1.5 | Execution order may be risk-based, coverage-based or requirements-based; dependencies can override it. |

Internal convention built on 5.2.3 (the syllabus does not map risk levels to techniques; this table is ours):

Current table and rule: `gen-testcase` › `references/test-design-techniques.md` §3 (single source).

- EP stays at 100% at every level: one test per partition is cheap.
- 🔴 uses the strongest criteria named in 4.2.2 and 4.2.4. Monetary amounts, limits and transaction states are typically 🔴.
- Likelihood (5.2): recorded per AC as `Likelihood: High` when the AC is new, complex, recently changed or has defect history.
- Each invalid transition gets its own TC (4.2.4).

## Phase C · Examples, lint, validator

| # | Item |
|---|---|
| C1 | Rewrite the `_example` feature: implementation-free AC; add FLD, DT, ST, role matrix; TCs with technique and coverage items; coverage summary |
| C2 | Vocabulary: keep ISTQB and BABOK terms out of the banned list; add domain-neutral checks if the pilot shows misses |
| C3 | Validator (pulled forward from phase 4): every FLD, DT rule and ST transition is referenced by at least one TC; every TC's coverage items exist |

## Order
1. Phase A → commit.
2. Phase B → commit.
3. Phase C → commit, run lint and tests on the example.
4. Pilot on one real ticket (existing `docs/plan.md`).

## Decisions

| # | Decision |
|---|---|
| 1 | One scale for AC criticality and TC priority, with icons: 🔴 Critical · 🟠 High · 🟡 Medium · ⚪ Low. TC priority: `naming.md` (single source). `P1`–`P3` is retired everywhere (templates, naming, run file, smoke scope = 🔴). |
| 2 | AC are implementation-free. Clicks and screens live in TCs only. |
| 3 | Depth by risk: the sourced table above, agreed. |
| 4 | Non-functional AC stay in AC. Their TCs are typed `Non-functional` and run only when they can be checked manually on staging. |
| 5 | Keep `gen-ac-from-jira` for its current project. Port a generic copy into `write-ac`. |
