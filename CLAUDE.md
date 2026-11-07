# QA Project: <PROJECT NAME>

## Project config (fill in once per project)
| Field | Value |
| --- | --- |
| Project name | <name> |
| Domain | <e.g. payments, e-commerce, HR> |
| Jira project key | <e.g. ABC> |
| Feature codes | <3-4 chars each, e.g. TRF, FX, KYC> |
| Doc language | English |
| Automation stack | None yet |

Skills read this table. Keep it up to date.

## Repo layout
- `qa/specs/<feature>/ac.md`: acceptance criteria per feature.
- `qa/testcases/<feature>/tc.md`: manual test cases per feature.
- `qa/bugs/`: bug drafts before they go to Jira.
- `qa/traceability/matrix.md`: Ticket <-> AC <-> TC <-> Automation.
- `qa/reports/`: test run summaries.
- `qa/_templates/`: AC, TC and bug templates.
- `.claude/skills/`: write-ac, gen-testcase, log-bug, impact-analysis.
- `.claude/agents/`: ac-reviewer, tc-reviewer (read-only reviewers).
- `.claude/commands/`: /gen-ac, /gen-tc, /impact (shortcuts that call the skills).
- `.claude/rules/`: naming, writing style, domain. Read before writing AC or TC.

## ID convention
- Feature Code: 3-4 uppercase letters (`TRF`, `FX`, `KYC`).
- AC: `AC-<CODE>-NNN`. TC: `TC-<CODE>-NNN`. Example: `AC-TRF-001`.
- IDs are never reused or renumbered. Retire with `Status: Deprecated`.
- Details: `.claude/rules/naming.md`.

## Workflow
1. Jira ticket -> `write-ac` -> `qa/specs/<feature>/ac.md`.
2. AC -> `gen-testcase` -> `qa/testcases/<feature>/tc.md`.
3. Defect -> `log-bug` -> draft in `qa/bugs/`, then Jira.
4. Change request -> `impact-analysis` -> affected AC and TC.
5. Update `qa/traceability/matrix.md` after every AC or TC change.

## Rules
- Every TC links to at least one AC. Every AC links to a Jira ticket.
- Every TC has precondition, data, steps, expected result, Priority, Automation.
- Use synthetic or masked data only. Never real customer or account data.
- Never read or write `.env`, secrets or production config.
- Jira writes (create, comment, transition) need user confirmation first.
- Domain-specific checks live in `.claude/rules/domain.md`. Skills must not hardcode a domain.

## Commands
- No test commands yet. Add them here when `automation/` is created.
