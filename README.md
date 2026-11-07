# claude_pipeline

Generic QA repo skeleton for Claude Code. Manual QA first, automation later.
One copy per project. Shared files stay identical across projects; only per-project files change.

## Per-project files (edit for each project)

| File | What to fill in |
|---|---|
| `.claude/rules/project.md` | Project name, domain, Jira key, Feature Codes, comment caps |
| `.claude/rules/domain.md` | Domain entities, rules, compliance, Glossary, checklist |
| `.claude/rules/vocabulary.project.md` | Extra banned words, Allow list for domain terms |
| `.claude/settings.json` | Permissions, MCP tool names of the project's connectors |
| `.mcp.json` | Project-level MCP servers (disabled by default) |
| `qa/specs/`, `qa/testcases/`, `qa/tickets/`, `qa/reports/` | Project artifacts |
| `qa/traceability/matrix.md` | Project traceability rows |
| `automation/` (later) | Project test code and config |

## Shared files (never edit per project)

| File | Purpose |
|---|---|
| `CLAUDE.md` | Layout, IDs, workflow, rules |
| `.claude/rules/writing-style.md` | Always-on writing principles |
| `.claude/rules/naming.md` | ID and file naming |
| `.claude/skills/**` | write-ac, gen-testcase, log-ticket, impact-analysis, comment-style |
| `.claude/agents/**` | ac-reviewer, tc-reviewer |
| `.claude/commands/**` | /gen-ac, /gen-tc, /impact |
| `qa/_templates/**` | AC, TC, bug, task templates |
| `README.md`, `.gitignore` | Repo docs and ignores |

- Change a shared file here first, then copy it to each project.
- A project need that a shared file cannot cover goes into a per-project file, never into the shared file.

## New project
1. Copy this repo (or use it as a GitHub template).
2. Fill the per-project files above.
3. Run `python3 -m unittest discover -s .claude/skills/comment-style/scripts/tests`.

## Update an existing project
- Copy only the shared files. Per-project files are never overwritten.
