# Plan: approval, open questions and test execution

Status: agreed 2026-11-07 · Not started

## Scope
- Pre-launch: one user runs and approves everything.
- Target later: whole team, many projects. Keep shared files generic; project values go in per-project files (`README.md`).
- Testing: manual only, on staging only. Automation is out of scope.

## Decisions

| # | Decision |
|---|---|
| D1 | AC source of record is the repo. Jira holds links and comments only. |
| D2 | The user approves AC and TC with `/approve`. Approval is allowed with open questions. Editing an approved file returns it to `Draft`. |
| D3 | Notifications go through Claude notifications (to the person running the session). |
| D4 | AC done → one notification: headline + table of all open questions. Open questions are also commented on the Jira ticket. |
| D5 | AC blocked by an open question still gets TCs (IDs exist). Those TCs get `Status: Blocked`, `Blocked by: OQ-…`, and `TBD (OQ-…)` where content depends on the answer. |
| D6 | Execution model like Zephyr: TC = spec, never edited by a run. One run file per cycle. |
| D7 | Default execution is Mode B: an agent runs TCs in Claude in Chrome on staging. |
| D8 | The agent logs in by itself through the app's login form, with one test account per role. TCs carry a `Role` field. |
| D9 | Report is exported as one HTML file. Screenshots are taken and embedded for failed TCs only. |

## Pipeline

```
Jira story
  → write-ac → ac.md (Draft) → ac-reviewer → 🔔 headline + OQ table · Jira comment (OQ table)
  → /approve → Approved
  → gen-testcase → tc.md (Active | Blocked by OQ) → tc-reviewer → 🔔
  → /approve --tc → Approved
  → /start-run → run file → test-runner (Mode B, staging, per role) → /end-run → HTML report → 🔔
       Fail → log-ticket (bug draft) → user verifies → Jira
OQ answered → /resolve-oq → update AC → TC Blocked → Active → 🔔
```

## Work items

### Phase 1 · Foundation

| # | Item | Files | Done when |
|---|---|---|---|
| 1.1 | Project config additions: AC source of record, staging URL, roles and test accounts (no passwords), notification channel | `.claude/rules/project.md` (per-project) | Skills read every field from this file |
| 1.2 | Ignore local secrets and heavy output | `.gitignore` | `qa/test-accounts.local.md`, `qa/runs/*/evidence/`, `qa/reports/*.html` ignored |
| 1.3 | Status fields. AC: `Draft · Approved · Changes requested`, `Approved by`, `Approved on`. TC: `Active · Blocked · Deprecated`, `Blocked by`, `Role` | `qa/_templates/ac.md`, `tc.md`, `naming.md` | Lint clean on templates |
| 1.4 | Golden examples: one complete feature with AC, TC (incl. one Blocked TC) and a hand-off comment | `qa/specs/_example/`, `qa/testcases/_example/` | Reviewers find 0 issues on the example |

### Phase 2 · Approval and open questions

| # | Item | Files | Done when |
|---|---|---|---|
| 2.1 | `/approve <feature> [--tc]`, `/reject <feature> "<note>"` | `.claude/commands/` | Status and approval fields updated; reject note logged |
| 2.2 | `gen-testcase` runs only on approved AC | `gen-testcase/SKILL.md` | Refuses with a clear message on `Draft` |
| 2.3 | `write-ac` sends the notification (D4) and the Jira OQ comment | `write-ac/SKILL.md` | Notification shows all OQ in one table |
| 2.4 | Blocked TCs for OQ-blocked AC (D5) | `gen-testcase/SKILL.md` | Every OQ `Blocks` target has TCs with `Blocked by` |
| 2.5 | `/resolve-oq <OQ-ID> "<answer>"`: update AC, fill `TBD`, unblock TCs, notify | `.claude/commands/`, `impact-analysis` | No `TBD (OQ-ID)` left after resolve |

### Phase 3 · Test execution

| # | Item | Files | Done when |
|---|---|---|---|
| 3.1 | `/start-run <feature> --build <b> --scope smoke\|regression\|all\|retest`: create run file, list approved TCs, Blocked TCs pre-filled as ⛔, grouped by role | `.claude/commands/`, `qa/_templates/run.md` | `qa/runs/<date>-<feature>-<build>.md` created |
| 3.2 | `test-runner` agent (Mode B): log in per role on the staging URL only, run steps, compare with expected, record `Pass (agent)` · `Fail` · `Blocked` · `Skip` | `.claude/agents/test-runner.md` | Stops and notifies on OTP or an unknown URL |
| 3.3 | Screenshot on Fail only, saved under the run's `evidence/` | `test-runner.md` | No screenshots for non-failed TCs |
| 3.4 | Fail → `log-ticket` drafts the bug. User verifies before Jira. | `log-ticket/SKILL.md` | Bug draft links TC, AC, run and evidence |
| 3.5 | `/end-run`: summary, HTML report (fail screenshots embedded), notification | `.claude/commands/`, report script | One self-contained HTML file per run |

### Phase 4 · Enforcement

| # | Item | Done when |
|---|---|---|
| 4.1 | Hook: run the lint after any write to `qa/specs/` or `qa/testcases/` | Edit with a banned word is flagged at once |
| 4.2 | Validator: ID format, required fields, status values, linked AC and OQ exist | Runs in the hook and in CI |
| 4.3 | GitHub Action: unit tests, lint, validator, PII scan (card-like numbers, emails) | PR fails on any violation |

### Pilot
- After phases 1–3, run one real ticket end to end.
- Record: lint hits, false positives, reviewer findings, agent Pass/Fail accuracy, time spent.
- Adjust rules and vocabulary from the results before phase 4.

## Backlog (later)

| Item | Trigger |
|---|---|
| Generate `matrix.md` from IDs; base for the traceability graph | After pilot |
| `VERSION` + sync script; plugin at 3+ projects | Second project starts |
| Move the domain checklist out of always-on rules | `domain.md` grows |
| Jira as AC source of record (mode `jira`) | A project needs it |
| Team notifications (Jira mention, Slack) and reviewer roles | Team rollout |
| Scheduled checks for approvals and OQ answers | After pilot |
| Onboarding guide and shared-layer owner | Team rollout |
| Automation of stable Mode B TCs | Later phase |

## Open points
- D4 vs the rule "Jira writes need confirmation": auto-post OQ comments, or ask once per AC hand-off?
- How a `Pass (agent)` becomes `Pass (verified)`: per TC, or one confirm per run?
