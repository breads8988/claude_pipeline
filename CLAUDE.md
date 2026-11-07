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
| Comment caps | Default (see `comment-style`): 15 lines, headline 15 words, cell 15 words |

Skills read this table. Keep it up to date.

## Repo layout
- `qa/specs/<feature>/ac.md`: acceptance criteria per feature.
- `qa/testcases/<feature>/tc.md`: manual test cases per feature.
- `qa/tickets/`: bug and task drafts before they go to Jira.
- `qa/traceability/matrix.md`: Ticket <-> AC <-> TC <-> Automation.
- `qa/reports/`: test run summaries.
- `qa/_templates/`: AC, TC, bug and task templates.
- `.claude/skills/`: write-ac, gen-testcase, log-ticket, impact-analysis, comment-style.
- `.claude/agents/`: ac-reviewer, tc-reviewer (read-only reviewers).
- `.claude/commands/`: /gen-ac, /gen-tc, /impact (shortcuts that call the skills).
- `.claude/rules/`: naming, writing-style (always on), domain, vocabulary.project. Read before writing AC or TC.

## ID convention
- Feature Code: 3-4 uppercase letters (`TRF`, `FX`, `KYC`).
- AC: `AC-<CODE>-NNN`. TC: `TC-<CODE>-NNN`. Example: `AC-TRF-001`.
- IDs are never reused or renumbered. Retire with `Status: Deprecated`.
- Details: `.claude/rules/naming.md`.

## Workflow
1. Jira ticket -> `write-ac` -> `qa/specs/<feature>/ac.md`.
2. AC -> `gen-testcase` -> `qa/testcases/<feature>/tc.md`.
3. Defect or task -> `log-ticket` -> draft in `qa/tickets/`, then Jira.
4. Change request -> `impact-analysis` -> affected AC and TC.
5. Update `qa/traceability/matrix.md` after every AC or TC change.
6. Every Jira comment -> `comment-style` layout.

## Rules
- Every TC links to at least one AC. Every AC links to a Jira ticket.
- Every TC has precondition, data, steps, expected result, Priority, Automation.
- Use synthetic or masked data only. Never real customer or account data.
- Never read or write `.env`, secrets or production config.
- Jira writes (create, comment, transition) need user confirmation first.
- Domain-specific checks live in `.claude/rules/domain.md`. Skills must not hardcode a domain.
- Run the `comment-style` lint on AC and TC files before saving. Exit 1 or 2 blocks the save.

## Commands
- Lint AC/TC: `python3 .claude/skills/comment-style/scripts/lint.py <file.md>`
- Lint tests: `python3 -m unittest discover -s .claude/skills/comment-style/scripts/tests`
- No automation commands yet. Add them here when `automation/` is created.
