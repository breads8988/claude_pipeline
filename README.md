# claude_pipeline

Generic QA repo skeleton for Claude Code. Manual QA first, automation later.
One copy per project. Shared files stay identical across projects; only per-project files change.

## Per-project files (edit for each project)

| File | What to fill in |
|---|---|
| `.claude/rules/project.md` | Project name, domain, Jira key, AC source of record, notifications, Feature Codes, staging URL, roles and test accounts (no passwords), comment caps |
| `.claude/rules/domain.md` | Domain entities, rules, compliance, Glossary, checklist |
| `.claude/rules/vocabulary.project.md` | Extra banned words, Allow list for domain terms |
| `.claude/settings.json` | Permissions, MCP tool names of the project's connectors |
| `.mcp.json` | Project-level MCP servers (disabled by default) |
| `qa/specs/`, `qa/testcases/`, `qa/tickets/`, `qa/runs/`, `qa/reports/` | Project artifacts (except `_example/`) |
| `qa/test-accounts.local.md` | Test account passwords, local only, git-ignored |
| `qa/traceability/matrix.md` | Project traceability rows |
| `automation/` (later) | Project test code and config |
| `docs/project/` | Project-specific notes and decisions (create when needed) |

## Shared files (never edit per project)

| File | Purpose |
|---|---|
| `CLAUDE.md` | Layout, IDs, workflow, rules |
| `.claude/rules/writing-style.md` | Always-on writing principles |
| `.claude/rules/naming.md` | ID and file naming |
| `.claude/skills/**` | write-ac, gen-testcase, log-ticket, impact-analysis, comment-style, test-run |
| `.claude/agents/**` | ac-reviewer, tc-reviewer, test-runner |
| `.claude/commands/**` | /gen-ac, /approve, /reject, /resolve-oq, /gen-tc, /start-run, /end-run, /impact |
| `qa/_templates/**` | AC, TC, bug, task, run, test-account templates |
| `qa/**/_example/` | Golden examples |
| `docs/` | Template plans, decisions, review and backlog. Generic only: no project terms |
| `README.md`, `.gitignore` | Repo docs and ignores |

- Change a shared file here first, then copy it to each project.
- A project need that a shared file cannot cover goes into a per-project file, never into the shared file.

## New project
1. Copy this repo (or use it as a GitHub template).
2. Fill the per-project files above. Copy `qa/_templates/test-accounts.local.md` to `qa/test-accounts.local.md`.
3. Run the three test suites: lint, coverage, report (`CLAUDE.md` › Commands).
4. Project notes and decisions go in `docs/project/` (per-project), never in the shared `docs/` files.

## Update an existing project
- Copy only the shared files. Per-project files are never overwritten.
