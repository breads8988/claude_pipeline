# Notifications

Channel: the `Notifications` field in `.claude/rules/project.md`.

## How to send a Claude notification
- Use the session's push-notification tool when it has one.
- Otherwise end the turn with the notification block as the final message.
- One notification per event. Same layout as a comment (`comment-patterns.md`): headline, one table, `Next` line.

## Events

| Event | Sent by | Table | Also to Jira |
|---|---|---|---|
| AC ready for review | `write-ac` | All open questions (table 2), or none | Only OQ the user replies `skip` to |
| TC ready for review | `gen-testcase` | Hand-off (table 1) + blocked TC count | No |
| Lint failed and not fixable | any skill | File, line, word | No |
| OQ resolved | `/resolve-oq` | AC and TC changed | No |
| Run paused | `test-runner` | TC, reason (OTP, unknown host, page down) | No |
| Run finished | `/end-run` | Run summary + failed TCs | No |

## Formats

### AC ready for review

```markdown
**AC-<CODE> · ⚠️ review** — <n> AC · <n> OQ · `qa/specs/<feature>/ac.md`

| OQ | Risk | Question | Blocks |
|---|---|---|---|
| OQ-<CODE>-001 | 🔴 | <question> | AC-<CODE>-004 |

- **Next:** answer each OQ here, or reply `skip <OQ-ID>`. Then `/approve <feature>`.
```

- List **all** open questions, 🔴 first. No cap on rows.
- No open questions → replace the table with `No open questions.`

### Run finished

```markdown
**Run <feature> · build <b> · ✅ done** — <n> TC · <n> ✅ · <n> ❌ · <n> ⛔

| TC | Result | Role | Note |
|---|---|---|---|
| TC-<CODE>-014 | ❌ | <role> | <one line> |

- **Next:** confirm failed TCs, then bugs go to Jira. Report: `qa/reports/<run>.html`
```

- Rows: failed TCs first, then blocked. Passed TCs are counted in the headline only.
