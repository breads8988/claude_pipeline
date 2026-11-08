# QA workspace (shared, generic)

This file is identical in every project. Project values live in `.claude/rules/project.md`.
Per-project vs shared files: `README.md`.

## Repo layout
- `qa/specs/<feature>/ac.md`: acceptance criteria per feature.
- `qa/testcases/<feature>/tc.md`: manual test cases per feature.
- `qa/tickets/`: bug and task drafts before they go to Jira.
- `qa/traceability/matrix.md`: Ticket <-> AC <-> TC <-> Automation.
- `qa/runs/`: one run file per test cycle (Zephyr-style); evidence of failed TCs is git-ignored.
- `qa/reports/`: HTML run reports (git-ignored).
- `qa/_templates/`: AC, TC, bug, task, run and local test-account templates.
- `qa/**/_example/`: golden examples. Read them before writing AC, TC or a run.
- `docs/plan.md`: agreed decisions and roadmap.
- `.claude/skills/`: write-ac, gen-testcase, log-ticket, impact-analysis, comment-style, test-run.
- `.claude/agents/`: ac-reviewer, tc-reviewer (read-only), test-runner (browser on staging).
- `.claude/commands/`: /gen-ac, /approve, /reject, /resolve-oq, /gen-tc, /start-run, /end-run, /impact.
- `.claude/rules/`: project (config), naming, writing-style, domain, vocabulary.project. Read before writing AC or TC.

## ID convention
- Feature Code: 3-4 uppercase letters, listed in `.claude/rules/project.md`.
- AC: `AC-<CODE>-NNN`. TC: `TC-<CODE>-NNN`. Example: `AC-USR-001`.
- IDs are never reused or renumbered. Retire with `Status: Deprecated`.
- Details: `.claude/rules/naming.md`.

## Workflow
1. `/gen-ac <JIRA-KEY>` → AC `Draft` → notification with all open questions.
2. User answers open questions in chat; `skip` ones go to Jira as one comment.
3. `/approve <feature>` → AC `Approved` (open questions allowed).
4. `/gen-tc <feature>` → TC `Draft`; AC blocked by an open question get `Blocked` TCs.
5. `/approve <feature> --tc` → TC `Approved`.
6. `/start-run <feature> --build <b> --scope <s>` → `test-runner` executes on staging → `/end-run` → HTML report + notification.
7. Failed TC → user confirms → `log-ticket` → Jira.
8. `/resolve-oq <OQ-ID> "<answer>"` → AC and TC updated, blocked TCs become `Active`.
9. Change request → `impact-analysis` → affected AC and TC.
10. Update `qa/traceability/matrix.md` after every AC or TC change. Every Jira comment and notification follows `comment-style`.

## Rules
- Every TC links to at least one AC. Every AC links to a Jira ticket.
- Every TC has precondition, data, steps, expected result, Priority, Automation.
- Use synthetic or masked data only. Never real customer or account data.
- Never read or write `.env`, secrets or production config.
- Jira writes (create, comment, transition) need user confirmation first. A `skip` reply to an open question is that confirmation.
- Only `/approve` sets `Approved`. Any edit to an approved AC or TC file sets it back to `Draft`.
- `gen-testcase` needs an approved AC. A run needs an approved TC file.
- The test agent logs in only on the staging URL in `project.md`, with project test accounts. Passwords stay in `qa/test-accounts.local.md`.
- Domain-specific checks live in `.claude/rules/domain.md`. Skills must not hardcode a domain.
- Run the `comment-style` lint on AC and TC files, and the coverage validator on TC files, before saving. Exit 1 or 2 blocks the save.
- AC follow BABOK (`write-ac` › `references/ac-techniques.md`). TCs follow ISTQB CTFL v4.0.1 (`gen-testcase` › `references/test-design-techniques.md`).
- Shared files stay generic for all projects. Put project-specific content only in the per-project files listed in `README.md`.

## Commands
- Lint AC/TC: `python3 .claude/skills/comment-style/scripts/lint.py <file.md>`
- Lint tests: `python3 -m unittest discover -s .claude/skills/comment-style/scripts/tests`
- Coverage: `python3 .claude/skills/gen-testcase/scripts/coverage.py qa/specs/<feature>/ac.md qa/testcases/<feature>/tc.md --summary`
- Coverage tests: `python3 -m unittest discover -s .claude/skills/gen-testcase/scripts/tests`
- Run report: `python3 .claude/skills/test-run/scripts/report.py qa/runs/<run>.md`
- Report tests: `python3 -m unittest discover -s .claude/skills/test-run/scripts/tests`
- No automation commands yet. Add them here when `automation/` is created.
