# Notifications

Channel: the `Notifications` field in `.claude/rules/project.md`.

## How to send a Claude notification
Every notification has two parts.

| Part | Where | Content |
|---|---|---|
| Push | Push-notification tool, if the session has one (none → skip this part) | The headline only, one line, no table, no Markdown |
| Chat block | Final message of the turn | Headline, one table, `Next` line (`comment-patterns.md`) |

- Push text: `<item> · <state> — <counts> · <action>`. Max 120 characters.
- No push tool → send the chat block only.
- Notify only where the user must act: the two review gates, a paused run, a run with failures. Nothing else.
- One notification per event.
- No notification for lint or validator errors: the skill fixes them (max 3 attempts). Errors left after 3 attempts go in the `Next` line of the ready notification.
- No notification for a command the user just ran (`/approve`, `/resolve-oq`): reply in chat.
- Row caps of `comment-patterns.md` do not apply to the AC-ready table: list every open question.

## Events

| Event | Sent by | Table | Also to Jira |
|---|---|---|---|
| AC ready for review | `write-ac` | All open questions (table 2), or none | Only OQ the user replies `skip` to |
| TC ready for review | `gen-testcase` | Hand-off (table 1) + blocked TC count | No |
| Run paused | main session, from the `test-runner` block | TC, reason (OTP, unknown host, page down, accounts file missing) | No |
| Run failed: ≥ 1 `❌` | `/end-run` | Run summary + failed TCs | No |

## Formats

### AC ready for review

Push: `AC-<CODE> ready · <n> AC · <n> OQ open · reply in chat`

```markdown
**AC-<CODE> · ⚠️ review** — <n> AC · <n> OQ · `qa/specs/<feature>/ac.md`

| OQ | Risk | Question | Blocks |
|---|---|---|---|
| OQ-<CODE>-001 | 🔴 | <question> | AC-<CODE>-004 |

- **Next:** answer each OQ here, or reply `skip <OQ-ID>`. Then `/approve <feature>`.
```

- List **all** open questions, 🔴 first. No cap on rows.
- No open questions → replace the table with `No open questions.`

### Run failed

Push: `Run <feature> <b> done · <n> ✅ · <n> ❌ · <n> ⛔ · confirm fails in chat`

```markdown
**Run <feature> · build <b> · ✅ done** — <n> TC · <n> ✅ · <n> ❌ · <n> ⛔

| TC | Result | Role | Note |
|---|---|---|---|
| TC-<CODE>-014 | ❌ | <role> | <one line> |

- **Next:** confirm failed TCs, then bugs go to Jira. Report: `qa/reports/<run>.html`
```

- No `❌` in the run → no notification; reply in chat with the headline and report path.
- Rows: failed TCs first, then blocked. Passed TCs are counted in the headline only.

### TC ready for review

Push: `TC-<CODE> ready · <n> TC · <n> blocked · /approve <feature> --tc`

```markdown
**TC-<CODE> · ⚠️ review** — <n> TC · <n> 🔴 · <n> 🟠 · <n> 🟡 · <n> ⚪ · <n> blocked · `qa/testcases/<feature>/tc.md`

| Technique | Items | Covered | Blocked | Coverage |
|---|---|---|---|---|
| <technique> | <n> | <n> | <n> | <n>% |

- **Next:** review, then `/approve <feature> --tc`. Reviewer findings left open: <n>.
```

- Table: the `## Coverage summary` of `tc.md`, unchanged.

### Run paused

Push: `Run <feature> paused at <TC-ID> · <reason>`

```markdown
**Run <feature> · build <b> · ⏸ paused** — <n> done · <n> left

| TC | Role | Reason |
|---|---|---|
| TC-<CODE>-014 | <role> | <OTP not in accounts file · unknown host <host> · login failed twice · staging down · accounts file missing> |

- **Next:** fix the cause, then reply `resume` (or `/start-run --resume <run file>`). Or `/end-run` to stop here.
```
