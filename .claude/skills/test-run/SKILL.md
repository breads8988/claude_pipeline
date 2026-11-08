---
name: test-run
description: Plan, execute and report a manual test cycle on staging (Zephyr-style run file, agent execution by role, HTML report). Use for /start-run, running TCs, /end-run, or a test report.
---

# test-run

A run is one test cycle: one feature, one build, one scope. TCs are specs and are never edited by a run.

| Item | Path |
|---|---|
| Run file | `qa/runs/<YYYY-MM-DD>-<feature>-<build>.md` (from `qa/_templates/run.md`) |
| Evidence | Path in the row's `Evidence` cell: the path the browser tool returned, or `qa/runs/<run>/evidence/<TC-ID>.png` (git-ignored). Failed TCs only |
| Report | `qa/reports/<run>.html` (git-ignored) |
| Report script | `python3 .claude/skills/test-run/scripts/report.py <run file>` |

## 1. Start
1. Both headers must be `Status: Approved`: `ac.md` and `tc.md`. Otherwise stop: `<AC|TC> is <status>. Run /approve <feature> [--tc] first.`
2. Select TCs by scope. Never include `Deprecated`.

| Scope | TCs |
|---|---|
| `smoke` | `Priority: 🔴` |
| `regression` | `--change <JIRA-KEY>` → TCs picked by `impact-analysis` for that change; no `--change` → all active TCs |
| `all` | Every active and blocked TC |
| `retest` | TCs failed in the latest run of the feature, or the TC IDs given |

3. Create the run file. Same name exists → add `-2`, `-3`.
4. One row per TC: ID, title, role, priority. Result `⬜`.
5. `Status: Blocked` TCs → Result `⛔ Blocked`, Note `<OQ-ID>`. They are never executed.
6. Order rows by role, then priority (🔴 first, risk-based), so the agent logs in once per role.
7. Charters in `tc.md` (`CH-<CODE>-NN`): ask whether to include them. Included → one row each in `## Exploratory sessions`. They run after the TCs, within their time box; findings go to `log-ticket`.
8. Empty selection (e.g. `smoke` with no 🔴 TC) → stop and say so; no run file.
9. **Seed preconditions**: list the TC preconditions marked "Seeded on staging". A seed script in `project.md` › Test data backdoor → show the command and run it after the user says yes. No script → ask the user to seed, or accept those TCs as `⛔ Blocked`.
10. Set `State: In progress` and `Started` (date and time).

## 2. Execute
- Run the `test-runner` agent once per role group, with the run file path and the role. Repeat until no `⬜` row is left or the run is `Paused`.
- The agent updates one row at a time, so a stopped run can resume from the first `⬜`.
- The agent returns a **Run paused** block → send it to the user as the notification (push + chat). The agent cannot reach the user.
- `resume` (or `/start-run --resume <run file>`) → set `State: In progress`, continue from the first `⬜` row of the paused role group.

## 3. End
1. Every row has a result other than `⬜`, or the user ends the run early (rest stay `⬜`).
2. Set `State: Done` and `Finished`.
3. Evidence: for each `❌` row, copy the file at the Evidence path to `qa/runs/<run>/evidence/<TC-ID>.png` and write that path in the cell. The path is not reachable here (browser on another machine) → ask the user to save the screenshot there.
4. Run the report script. Exit 2 → fix the run file and run it again.
5. At least one `❌` → send the **Run failed** notification (`comment-style` › `references/notifications.md`). None → reply in chat only.
6. Each `❌ Fail` → draft `qa/tickets/BUG-TBD-<TC-ID>.md` with `log-ticket` (run, TC, AC, evidence path). Show the drafts.
7. The user confirms a failure → create the bug in Jira. Rename the draft `BUG-<key>.md` and write the key in the run row's `Bug` cell.
8. Evidence files are not uploaded by any tool. Ask the user to attach them to the bug.

## 4. Retest
1. `/start-run <feature> --build <b> --scope retest` with the failed TC IDs.
2. Per bug, draft one retest comment (`comment-style` table 6) with the result. Ask before posting.
3. All its TCs pass → ask whether to transition the bug (e.g. to `Done`). Never transition without a yes.

## Rules
- An agent `Pass` is final. The report lists 🔴 passes for an optional re-check.
- A `Fail` is confirmed by the user before a bug goes to Jira.
- A run never edits `ac.md` or `tc.md`.
- Results are written as `✅ Pass` · `❌ Fail` · `⛔ Blocked` · `⏭ Skip` · `⬜`.

| Result | Meaning | Set by |
|---|---|---|
| `⛔ Blocked` | Cannot run: open question, or precondition missing on staging. Note: OQ ID or missing precondition | Start step or agent |
| `⏭ Skip` | Not run by the user's decision, e.g. feature off in this build. Note: reason | User only |
| `⬜` | Not run yet | Start step |
