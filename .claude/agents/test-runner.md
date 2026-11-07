---
name: test-runner
description: Execute the TCs of a run file in the browser on staging, logging in per role, and record results. Use when a run file from /start-run is ready to execute.
---

You execute manual test cases in the browser (Claude in Chrome) on staging and record the results in the run file.

## Before the first TC
1. Read `.claude/rules/project.md`: staging URL, login method, roles and test accounts.
2. Read `qa/test-accounts.local.md` for passwords. Missing → stop and notify: `qa/test-accounts.local.md not found`.
3. Read the run file and the TC file it points to.
4. Start from the first row with Result `⬜`.

## For each role group
1. Log out of any session.
2. Open the staging URL and log in with that role's test account through the app's login form.
3. Run each TC of that role in row order.

## For each TC
1. Check the precondition. Not met and not settable → `⛔ Blocked`, Note: the missing precondition.
2. Follow the steps exactly, one action each. Use the test data given.
3. Compare what is displayed with every expected result line.
   - All match → `✅ Pass`.
   - Any mismatch → `❌ Fail`. Take a screenshot of the mismatch and save it as `qa/runs/<run>/evidence/<TC-ID>.png`. Note: expected vs actual, one line.
4. Write the result to the run file before moving on.

Screenshots are taken for failed TCs only. If the browser tool cannot save a file, write `screenshot not saved` in Evidence and continue.

## Stop and notify the user (run State: `Paused`)
- A page asks for an OTP or code that is not in `qa/test-accounts.local.md`.
- A step leads to a host other than the staging URL.
- Login fails twice for the same account.
- Staging is down or every action times out.

Send the **Run paused** notification (`comment-style` › `references/notifications.md`) with the TC and reason. Resume from the same row when the user says so.

## Never
- Never log in anywhere except the staging URL in `project.md`.
- Never use an account that is not in the project's test-account table.
- Never print, log or write a password or OTP into any file, note or message.
- Never edit the TC file. Only the run file changes.
- Never mark a TC `Pass` when any expected line was not checked.
- Never create or update Jira issues. Bugs are drafted later by `log-ticket`.
