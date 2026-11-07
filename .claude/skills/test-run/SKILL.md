---
name: test-run
description: Plan, execute and report a manual test cycle on staging (Zephyr-style run file, agent execution by role, HTML report). Use for /start-run, running TCs, /end-run, or a test report.
---

# test-run

A run is one test cycle: one feature, one build, one scope. TCs are specs and are never edited by a run.

| Item | Path |
|---|---|
| Run file | `qa/runs/<YYYY-MM-DD>-<feature>-<build>.md` (from `qa/_templates/run.md`) |
| Evidence | `qa/runs/<run>/evidence/<TC-ID>.png`, failed TCs only (git-ignored) |
| Report | `qa/reports/<run>.html` (git-ignored) |
| Report script | `python3 .claude/skills/test-run/scripts/report.py <run file>` |

## 1. Start
1. The TC file header must be `Status: Approved`. Otherwise stop: `TC is <status>. Run /approve <feature> --tc first.`
2. Select TCs by scope. Never include `Deprecated`.

| Scope | TCs |
|---|---|
| `smoke` | `Priority: 🔴` |
| `regression` | TCs picked by `impact-analysis` for the change; no change given → all active TCs |
| `all` | Every active and blocked TC |
| `retest` | TCs failed in the latest run of the feature, or the TC IDs given |

3. Create the run file. Same name exists → add `-2`, `-3`.
4. One row per TC: ID, title, role, priority. Result `⬜`.
5. `Status: Blocked` TCs → Result `⛔ Blocked`, Note `<OQ-ID>`. They are never executed.
6. Order rows by role, then priority (🔴 first, risk-based), so the agent logs in once per role.

## 2. Execute
- Run the `test-runner` agent with the run file path.
- The agent updates one row at a time, so a stopped run can resume from the first `⬜`.

## 3. End
1. Every row has a result other than `⬜`, or the user ends the run early (rest stay `⬜`).
2. Set `State: Done` and `Finished`.
3. Run the report script. Exit 2 → fix the run file and run it again.
4. Each `❌ Fail` → draft a bug with the `log-ticket` skill (run, TC, AC, evidence). Bugs go to Jira only after the user confirms the failure.
5. Send the **Run finished** notification (`comment-style` › `references/notifications.md`).

## Rules
- An agent `Pass` is final. The report lists 🔴 passes for an optional re-check.
- A `Fail` is confirmed by the user before a bug goes to Jira.
- Results are written as `✅ Pass` · `❌ Fail` · `⛔ Blocked` · `⏭ Skip` · `⬜`.
