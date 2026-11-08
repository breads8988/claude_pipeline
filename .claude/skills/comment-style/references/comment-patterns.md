# Comment patterns

Applies to every Jira comment. Not a suggestion.

## The 5 rules

| Rule | What it means |
|---|---|
| Table-first | 1 headline → exactly 1 table → 1 `- **Next:**` bullet. That is the whole comment. |
| Hard cap | See *Caps*. Longer content belongs in a repo file; the comment links it. |
| Numbers, not adjectives | `14 AC · 4 🔴 · 2 gaps`, never "coverage is fairly complete". |
| Bullets | Every line outside the table is a bullet or numbered step. Only the bold headline stands alone. |
| Never include | Ticket recap, source restatement, process narration, "I have completed…", pasted artifact bodies, diagrams. |

## Caps (defaults; override in `.claude/rules/project.md`)

| Item | Default |
|---|---|
| Whole comment | ≤ 15 rendered lines |
| Headline | ≤ 15 words |
| Outside the table | Headline + `Next` bullet + max 3 judgement bullets |
| Table cell | ≤ 15 words |

Sentence length follows `.claude/rules/writing-style.md`.

## Skeleton

```markdown
**<ARTIFACT> · <STATUS>** — <≤15 words>

<exactly one table>

- **Next:** <who> → <what>
```

Status tokens: `✅ done` · `🔄 in progress` · `⛔ blocked` · `⚠️ gated`.

## Use real artifact IDs

- The first column carries the artifact's own ID: `OQ-<CODE>-001`, `AC-<CODE>-005`, `TC-<CODE>-012`.
- Never substitute `1, 2, 3`. The comment must be greppable back to its file.
- Sort rows by severity, not by ID.
- Renumbered IDs (rare): one row per `old ID → new ID`. More than 8 → one row linking the map.

## The 6 tables

Pick the one that matches the comment.

### 1. Hand-off / artifact delivered

```markdown
| Artifact | Where | Count | Status |
|---|---|---|---|
| AC - <Feature> | `qa/specs/<feature>/ac.md` | 14 AC · 4 🔴 | ✅ |
```

### 2. Open questions

```markdown
| OQ | Risk | Question | Blocks |
|---|---|---|---|
| OQ-<CODE>-001 | 🔴 | Is retry allowed after a 30s gateway timeout? | AC-<CODE>-005 |
```

- Risk: impact if the answer is wrong, on the `naming.md` scale: 🔴 Critical · 🟠 High · 🟡 Medium · ⚪ Low. 🔴 rows first.
- `Blocks` = the exact ID it holds up, or `—`.
- 🟠 and 🟡 rows: one closed-ended line.
- Log questions, never answer them. No recommendations.

### 3. Coverage / gap report

```markdown
| Gap | Type | Item | Suggested test intent | Sev |
|---|---|---|---|---|
| No TC for retry after timeout | coverage | AC-<CODE>-005 | assert retry rejected post-timeout | 🔴 |
```

No gaps → replace the table with one verdict line: `**Coverage · ✅** — 0 gaps.`

### 4. Scope breakdown

```markdown
| # | Feature | Scope | Risk | Depends on |
|---|---|---|---|---|
| 1 | <Feature> | <in scope, one line> | 🔴 | — |
```

Features have no IDs yet, so a positional `#` is correct here only.

### 5. Progress

```markdown
| Step | State | Note |
|---|---|---|
| write-ac | 🔄 | waiting on design for <screen> |
```

### 6. Retest

```markdown
| Case | TC | Result | Build | Evidence |
|---|---|---|---|---|
| 3 decimals | TC-<CODE>-014 | ❌ Fail | 2.4.1 | TC-<CODE>-014.png |
| 2 decimals | TC-<CODE>-013 | ✅ Pass | 2.4.1 | — |
```

- Headline status: `✅ fixed` when all pass, `⛔ reopened` when any fail.
- Failed rows first.
- Evidence: file name of the run row's `Evidence` path. Attach the file to the ticket.

## Exemptions: when the cap does not apply

1. **Artifact fallback.** When the artifact cannot be saved or linked, post it in full. Headline: `**<ARTIFACT> · ⚠️ publish pending** — <reason>. Full artifact below.` Never truncate an artifact to fit the cap.
2. **🔴 open question detail.** Each 🔴 row may carry one `> OQ-<CODE>-NNN: <context>` blockquote under the table. Facts only, no options analysis.
3. **Judgement / trade-off.** Max 3 bullets, one line each, when a decision cannot be tabled.

## Mentions

`@mention` rules still apply. Put the mention on the `Next` line. Brevity never overrides a mention rule.
