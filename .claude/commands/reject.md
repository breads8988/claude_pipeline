---
description: Request changes to the AC (or TC) of a feature
argument-hint: <feature-folder> [--tc] "<what to change>"
---

Request changes: $ARGUMENTS

1. Target file: `qa/specs/<feature>/ac.md`, or `qa/testcases/<feature>/tc.md` with `--tc`.
2. Set the header `Status: Changes requested`.
3. Add a `Review log` row: date, `Changes requested`, name from `git config user.name`, the note.
4. Apply the requested changes with the matching skill (`write-ac` or `gen-testcase`).
5. When done, set `Status: Draft` and send the matching "ready for review" notification.
