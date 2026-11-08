---
description: Approve the AC (or TC) of a feature
argument-hint: <feature-folder> [--tc]
---

Approve: $ARGUMENTS

BABOK v3 task 5.5 *Approve Requirements*. Before approving, the user checks value (task 7.3 *Validate Requirements*): each AC supports the business need of the ticket.

1. Target file: `qa/specs/<feature>/ac.md`, or `qa/testcases/<feature>/tc.md` with `--tc`.
2. The header must be `Status: Draft`. Otherwise stop and say why (`Changes requested` → apply the changes first; `Approved` → nothing to do).
3. Run the `comment-style` lint on it. Exit not 0 → stop and show the hits.
4. `--tc` only:
   - The AC file must be `Approved`. Otherwise stop.
   - Run `python3 .claude/skills/gen-testcase/scripts/coverage.py qa/specs/<feature>/ac.md qa/testcases/<feature>/tc.md`. Exit not 0 → stop and show the errors.
5. AC only: ask once `Does every AC serve the ticket's goal? (yes / list AC to drop)`. A listed AC → stop, nothing changed; run `/reject`.
6. Set the header:
   - `Status: Approved`
   - `Approved by:` `git config user.name`; empty → ask the user for the name.
   - `Approved on:` today (YYYY-MM-DD)
7. Add a `Review log` row: date, `Approved`, name, open question count (`Open` + `Posted`).
8. Reply in one line, then the next step: `/gen-tc <feature>` after AC, `/start-run <feature> --build <build> --scope smoke` after TC.

Do not change any other line of the file.
