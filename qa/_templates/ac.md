# AC: <Feature name> (<CODE>)

| Field | Value |
| --- | --- |
| Jira | <KEY-123> |
| Status | `Draft` |
| Approved by | — |
| Approved on | — |
| Open questions | 0 |
| Last updated | <YYYY-MM-DD> |

## User story
**As a** <role>, **I want** <capability>, **so that** <benefit>.

## Impacted existing behaviour
- <feature (CODE): BR/AC/DT/ST IDs checked, conflicts found> or `None, isolated change.`

## Scenarios

### AC-<CODE>-001: <short title>
- Type: Functional | Non-functional | Transition
- Criticality: 🔴 Critical | 🟠 High | 🟡 Medium | ⚪ Low
- Likelihood: Normal | High
- Status: Active | Deprecated
- Given: <context already true>
- When: <one action or event>
- Then: <observable result: status, error code, copy, value, record>

## Business rules
| Rule ID | Rule | Criticality | Source |
| --- | --- | --- | --- |
| BR-<CODE>-001 | <rule with an example value> | 🔴 | <ticket or doc> |

## Data constraints
| FLD | Field | Type | Required | Min | Max | Format or allowed values | Criticality |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FLD-<CODE>-01 | <field> | <text / number / date / list> | Yes / No | <min or —> | <max or —> | <format> | 🔴 |

## Decision tables

### DT-<CODE>-01: <decision name>
- Criticality: 🔴
- Covers: AC-<CODE>-001

| Condition | R1 | R2 | R3 |
| --- | --- | --- | --- |
| <condition 1> | Y | Y | N |
| <condition 2> | Y | N | – |
| **Outcome** | <outcome> | <outcome> | <outcome> |

## State models

### ST-<CODE>-01: <entity> lifecycle
- Criticality: 🔴
- Covers: AC-<CODE>-001

| T | From | Event | To | Valid |
| --- | --- | --- | --- | --- |
| T1 | — | <event> | <state> | Yes |
| T2 | <state> | <event> | <state> | No |

## Open questions
| OQ | Risk | Question | Blocks | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| OQ-<CODE>-001 | 🔴 / 🟠 / 🟡 | <closed-ended question> | <ID or —> | BA/PO | Open |

## Review log
| Date | Action | By | Note |
| --- | --- | --- | --- |
