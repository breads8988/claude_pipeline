# Test design techniques (ISTQB-aligned)

Source: ISTQB CTFL syllabus v4.0.1 (2024-09-15), chapter 4 (test analysis and design) and sec. 5.2 (risk). Section numbers below refer to it.

## 1. Test analysis → test design

1. **Test conditions** ("what to test", sec. 1.4.1): list every item in `ac.md` that a test must exercise. Write the EP partitions and BVA values in the `## Test analysis` section of `tc.md`.
2. **Coverage items**: derive them per technique (table sec. 2).
3. **Test cases** ("how to test"): one TC exercises one or more coverage items, with preconditions, inputs and expected results.
4. **Coverage** = coverage items exercised ÷ coverage items identified, per technique.

## 2. Model → technique → coverage items

| `ac.md` item | Technique | Coverage items | Syllabus |
|---|---|---|---|
| `FLD` data constraint | Equivalence partitioning (EP) | Every valid and invalid partition; one test per partition is sufficient | sec. 4.2.1 |
| `FLD` with min or max | Boundary value analysis (BVA) | 2-value: boundary + nearest neighbour outside. 3-value: boundary + both neighbours | sec. 4.2.2 |
| `DT` decision table (incl. role × action) | Decision table testing | Every feasible column (`DT-…R<n>`) | sec. 4.2.3 |
| `ST` state model | State transition testing | Valid transitions; with *all transitions*, also each invalid transition | sec. 4.2.4 |
| `AC` GWT scenario | Scenario test (ATDD) | Each scenario | sec. 4.5.3 |
| `BR` business rule (rule-oriented AC) | Covered through the TC that applies the rule | Each rule at least once | sec. 4.5.2 |
| `domain.md` checklist | Checklist-based testing | Each applicable checklist item | sec. 4.4.3 |
| Tester experience | Error guessing | Each anticipated defect type (fault attack) | sec. 4.4.1 |

### Equivalence partitioning (sec. 4.2.1)
- Split each field's values into partitions the system treats the same way: valid and invalid. List them in the `Test analysis` table (FLD, partition, kind, example). The validator counts this table: every partition needs a TC.
- Typical invalid partitions: below min, above max, wrong type, wrong format, empty when required.
- Several fields → *Each Choice*: every partition of every field at least once; combinations are not required.
- Combine valid partitions of several fields in one TC; give each invalid partition its own TC, so one failure cannot hide another.

### Boundary value analysis (sec. 4.2.2)
- Only for ordered partitions (numbers, lengths, dates).
- Range 1–100, 2-value: `0, 1, 100, 101`. 3-value: `0, 1, 2, 99, 100, 101`.
- The neighbour is one `Step` away (FLD column): 1 for integers and lengths, 0.01 for amounts with 2 decimals, the currency's minor unit for money, 1 day for dates.
- Label each value `min-1`, `min`, `min+1`, `max-1`, `max`, `max+1` with its number: `FLD-…-01 BVA: max+1 = 255`. The validator checks the number.
- 3-value is "more rigorous" and catches defects 2-value misses (e.g. `x ≤ 10` coded as `x = 10`).

### Decision table testing (sec. 4.2.3)
- Condition rows on top, action rows below. Each column is one rule: a combination of conditions and its actions.
- Remove infeasible columns. A minimised table merges columns where a condition does not change the outcome.
- With many conditions, the number of columns grows exponentially; minimise or select by risk.

### State transition testing (sec. 4.2.4)
| Criterion | Coverage items | Strength |
|---|---|---|
| All states | Each state | Weakest |
| Valid transitions (0-switch) | Each valid transition | "Most widely used"; implies all states |
| All transitions | Each valid transition and each invalid transition | Implies both above; "minimum requirement for mission and safety-critical software" |

- Test **one invalid transition per TC**, to avoid defect masking.

### Scenario test / ATDD (sec. 4.5.3)
- Order: positive, then negative, then non-functional.
- Cover every characteristic of the story, nothing beyond it.
- No two TCs for the same characteristic.

### Checklist-based and error guessing (sec. 4.4)
- A checklist should not contain items that can be checked automatically; keep the `domain.md` checklist current.
- An `EG:` or `CHK:` TC still needs a `Covers AC`. A case that no AC describes becomes an AC or an open question first.
- Error guessing ideas: double submission, session expiry mid-flow, back button after submit, stale data in a second tab, special characters, very long input, concurrent edits.

## 3. Depth by risk (internal convention on sec. 5.2.3)

The syllabus states that product risk determines "the test techniques to be employed and the coverage to be achieved". It does not map levels to techniques; this table is our convention.

| Depth | EP | BVA | Decision table | State transition |
|---|---|---|---|---|
| 🔴 Critical | All partitions | 3-value | All feasible columns | All transitions (valid + invalid) |
| 🟠 High · 🟡 Medium | All partitions | 2-value | All feasible columns | Valid transitions |
| ⚪ Low | All partitions | 2-value | Minimised table | Valid transitions |

- **Depth** of a `FLD`, `DT` or `ST` = the highest of its own criticality and the criticality of the AC it covers (`Covers` bullet, or AC that cite its ID).
- `Likelihood: High` on a covered AC raises the depth one level, capped at 🔴 (risk = likelihood × impact, sec. 5.2).
- Depth sets the technique only. TC priority does not change (`naming.md`).
- ⚪ minimised table: write the minimised table in `ac.md`. Its columns are the coverage items.
- The validator applies this rule to BVA (3-value) and invalid transitions.

## 4. Coverage item notation in a TC

| Item | Notation |
|---|---|
| AC scenario | `AC-USR-002` |
| Business rule | `BR-USR-001` |
| EP partition | `FLD-USR-01 EP: empty` (name from the Test analysis table) |
| BVA value | `FLD-USR-01 BVA: max+1 = 255` |
| Decision table column | `DT-USR-01.R2` |
| Transition | `ST-USR-01.T4` |
| Checklist item | `CHK: double submission` |
| Error guess | `EG: back button after submit` |

## 5. Priority and execution order (sec. 5.1.5)
- TC priority: rule in `.claude/rules/naming.md` (highest of `Covers AC` and coverage items).
- Runs execute risk-based: 🔴 first. Dependencies can override the order.

## 6. Blocked TCs and coverage
- Only a TC whose content depends on an open question (it contains `TBD (OQ-…)`) is `Blocked`. Other TCs of that AC stay `Active`.
- Items covered only by blocked TCs are reported in the `Blocked` column of the summary. They are not counted as covered.
