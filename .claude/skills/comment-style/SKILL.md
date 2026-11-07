---
name: comment-style
description: Layout for every Jira comment (table-first, hard length cap) and technical wording for AC and TC text, with a vocabulary lint. Use whenever you write a Jira comment, AC or TC.
---

# comment-style

Base principles live in `.claude/rules/writing-style.md`. This skill adds two parts.

| Part | Applies to | Reference |
|---|---|---|
| 1. Comment layout | Every Jira comment and hand-off message | `references/comment-patterns.md` |
| 2. Technical wording | AC and TC text, and comments | `references/vocabulary.md` + `scripts/lint.py` |

## Scope rules
- A comment is a digest. The artifact file is the full record.
- Never reshape an artifact template (`qa/_templates/`) to match a comment table.
- A ticket description (bug or task) follows its template. The comment cap does not apply to it.
- Comments on a ticket (retest, follow-up, hand-off) follow part 1.

## Project overrides
| What | Where |
|---|---|
| Comment caps | `Comment caps` rows in the `CLAUDE.md` config table |
| Extra or allowed words | `.claude/rules/vocabulary.project.md` |
| Domain terms that collide with banned words | `Allow` table in `vocabulary.project.md` (define them in the `domain.md` Glossary) |

The project value wins. Do not copy these rules into other skills; reference this skill.

## Lint (required for AC and TC files)
Run from the repo root before saving:

```bash
python3 .claude/skills/comment-style/scripts/lint.py qa/specs/<feature>/ac.md
```

| Exit | Meaning | Action |
|---|---|---|
| 0 | Clean. Warnings may print. | Review warnings, then save. |
| 1 | Error-level words found | Rewrite each line. Keep meaning and IDs. Re-run. |
| 2 | Usage, file or vocabulary error | Fix the cause. Never skip the lint. |

- Never change app copy (backticks, double quotes) to pass the lint.
- A plain word missing from the list: use the technical term anyway. Add a row to `vocabulary.project.md`. Report `vocab: <word> → <use>` in the result.

## Before posting a comment
- [ ] 1 headline, 1 table, 1 `Next` bullet.
- [ ] Within caps, or an exemption applies.
- [ ] Real IDs, sorted by severity.
- [ ] Numbers, not adjectives.
