# TC: <Feature name> (<CODE>)

| Field | Value |
| --- | --- |
| AC file | `qa/specs/<feature>/ac.md` |
| Status | `Draft` |
| Approved by | — |
| Approved on | — |
| Last updated | <YYYY-MM-DD> |

## Coverage summary
Paste the output of `coverage.py … --summary`. The validator fails when this table is out of date.

| Technique | Items identified | Covered | Blocked | Coverage |
| --- | --- | --- | --- | --- |
| Scenario (AC) | 0 | 0 | 0 | — |
| Business rules | 0 | 0 | 0 | — |
| EP | 0 | 0 | 0 | — |
| BVA | 0 | 0 | 0 | — |
| Decision table | 0 | 0 | 0 | — |
| State transition | 0 | 0 | 0 | — |

## Test analysis

EP partitions (one TC per invalid partition):

| FLD | Partition | Kind | Example value |
| --- | --- | --- | --- |
| FLD-<CODE>-01 | valid | valid | <value> |
| FLD-<CODE>-01 | <partition name> | invalid | <value> |

BVA values (depth per `test-design-techniques.md` §3: 3-value at 🟠 and 🔴, else 2-value):

| FLD | Label | Value | TC |
| --- | --- | --- | --- |
| FLD-<CODE>-01 | min-1 | <value> | TC-<CODE>-<NNN> |

Pairwise (optional, 3+ parameters; output of `pairwise.py`; adds a `Pairwise` summary row):

| PW | <Parameter 1> | <Parameter 2> | <Parameter 3> |
| --- | --- | --- | --- |
| PW-01 | <value> | <value> | <value> |

## Exploratory charters (optional)

| Charter | Covers AC | Explore | With | To discover | Time box |
| --- | --- | --- | --- | --- | --- |
| CH-<CODE>-01 | AC-<CODE>-<NNN> | <target area> | <role, data, tools> | <risk to look for> | <e.g. 45 min> |

## TC-<CODE>-001: <short title>
| Field | Value |
| --- | --- |
| Covers AC | AC-<CODE>-001 |
| Technique | <one or more: Scenario, EP, BVA, Decision table, State transition, Checklist, Error guessing> |
| Coverage items | <each in backticks: `AC-<CODE>-001`, `FLD-<CODE>-01 EP: <partition>`, `FLD-<CODE>-01 BVA: max+1 = 255`, `DT-<CODE>-01.R2`, `ST-<CODE>-01.T4`, `EG: <idea>`> |
| Role | <role from project.md> |
| Type | Functional / Non-functional |
| Priority | 🔴 / 🟠 / 🟡 / ⚪ |
| Automation | `Not yet` / `Candidate` / `Done` |
| Status | `Active` / `Blocked` / `Deprecated` |
| Blocked by | <OQ ID or —> |

**Precondition**
- <role logged in, system and data state>

**Test data**
| Field | Value |
| --- | --- |
| <name> | <synthetic value> |

**Steps**
1. <one action>
2. <one action>

**Expected result**
- <observable result: copy, status, grid row, error code>
- TBD (OQ-<CODE>-001): <the part that depends on the answer>

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
