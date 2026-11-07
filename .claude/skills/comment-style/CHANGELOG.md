# Changelog

## 2.1.0 — 2026-11-07
- `blocked` narrowed to `is/are/was blocked`: `Blocked` is now a TC and run status.
- AC header field renamed `Open OQ` → `Open questions` (false hit on the `Open <Page>` rule).

## 2.0.0 — 2026-11-07: shared, project-independent version

Source: the comment-style skill of one earlier project (SKILL.md, `references/vocabulary.md`, `scripts/lint.py`).

### Removed (project-specific)
| Item | Reason | Now lives in |
|---|---|---|
| Issue tracker and wiki tool names | Tied to one project's tools | Generic "Jira comment" and "repo file" |
| Phase codes (P0–P4), human-gate steps, epic pipeline mode, lead hand-offs | One project's workflow | Not carried over |
| Named reviewer and ruling dates | Personal attribution | Not carried over |
| Feature-specific IDs and examples (feature codes, currency, page names) | Domain examples | `<CODE>` and `<placeholder>` examples |
| References to that project's other skills | Not in this repo | Not carried over |

### Moved
| Item | From | To |
|---|---|---|
| Base writing principles | SKILL.md | `.claude/rules/writing-style.md` (single source) |
| Comment rules, tables, exemptions | SKILL.md | `references/comment-patterns.md` |
| `nothing credited` (payments word) | Shared vocabulary | Add per project in `vocabulary.project.md` |
| `open` special case | Hardcoded in lint.py | Regex row in `references/vocabulary.md` |
| Table header skip list | Hardcoded in lint.py | Detected from the `---` row under any header |

### Changed
| Item | Before | After |
|---|---|---|
| Comment caps | 15 lines + 120 words outside table; cell and row caps only in epic mode | 15 lines; headline ≤ 15 words; ≤ 3 judgement bullets; cell ≤ 15 words; all comments |
| Tables | 5 (incl. P0 decomposition) | 6: hand-off, open questions, coverage, scope breakdown, progress, retest |
| Vocabulary format | `Banned \| Use \| Example` | Adds `Level` (`error` / `warn`); empty = `error` |
| Ambiguous words | All errors | `warn`: views, leaves, reads, still, holds, the one, same as, noted, kept, carries, not yet, goes, happens, blocked, cannot |
| Project vocabulary | Not supported | `.claude/rules/vocabulary.project.md`: add, override, Allow |

### Lint fixes
| Defect | Effect before | Fix |
|---|---|---|
| Terms not passed through `re.escape` | Special characters broke or widened matches | Escaped; `…` still matches one word |
| Fenced code not skipped | Code and diagrams were linted | Skips ``` and ~~~ blocks |
| `Open <Page>` missed after `1.` | Numbered steps passed | Regex allows a step number |
| Hyphen not a word boundary | `the one-time code` hit `the one` | Hyphen ends a word |
| Smart quotes not skipped | App copy in “ ” was linted | Skipped like `"…"` |
| Front matter not skipped | YAML linted | Skipped |
| Missing file or bad vocabulary | Traceback, exit 1 (same as hits) | Message on stderr, exit 2 |
| Any table in vocabulary read as banned | Extra tables polluted rules | Only tables whose first header is `Banned` (or `Allow`) |

### Verified
- Old and new lint on one sample page: same hits, except the 4 intended fixes (step number, hyphen, fenced code, `still` → warn).
- 30 unit tests pass: `python3 -m unittest discover -s .claude/skills/comment-style/scripts/tests`.
