---
name: gen-testcase
description: Generate manual test cases from approved acceptance criteria with role, precondition, data, steps and expected result. Use when the user asks for TC from AC or a feature.
---

# gen-testcase

## Input
- Feature folder or AC IDs.

## Gate
- Read the header of `qa/specs/<feature>/ac.md`.
- `Status` is not `Approved` → stop. Reply: `AC is <status>. Run /approve <feature> first.`

## Steps
1. Read `.claude/rules/project.md` (Feature Codes, Roles, Notifications).
2. Read `qa/specs/<feature>/ac.md`.
3. Read `.claude/rules/naming.md` and `domain.md`. Load the `comment-style` skill for wording.
4. Read `qa/testcases/_example/tc.md` as the reference for detail and format.
5. Read existing `qa/testcases/<feature>/tc.md`. Continue its numbering.
6. For each active AC, write positive, negative and boundary TCs where they apply.
7. Fill every field of `qa/_templates/tc.md`. Set `Role` from the project roles.
8. AC listed in the `Blocks` column of an open question → write the TC anyway:
   - `Status: Blocked`, `Blocked by: <OQ-ID>`.
   - Write every part you can. Mark the dependent part `TBD (<OQ-ID>): <what is unknown>`.
9. Set `Priority` from AC criticality (Critical → P1, High → P1/P2, others → P2/P3).
10. Set `Automation`: `Candidate` for stable, high-value or data-driven flows. Otherwise `Not yet`.
11. Set the header: `Status: Draft`, `Last updated`.
12. Run the `comment-style` lint on `tc.md`; fix until exit 0. Add TC IDs to `qa/traceability/matrix.md`.
13. Send the **TC ready for review** notification. Include AC with no TC and blocked TC count.

## Quality bar
- Precondition states the role and the system state.
- Test data is explicit and synthetic.
- Steps are numbered, one action each, and use element names from the UI.
- Expected result is observable: UI text, status, grid row, error code.
- RBAC: each role restriction has its own TC, run with that role.

## Do not
- Do not create a TC without an AC link.
- Do not use real customer or account data.
- Do not set `Approved`. Only `/approve --tc` does that.
