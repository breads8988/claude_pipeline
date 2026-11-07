---
name: gen-testcase
description: Generate manual test cases from acceptance criteria with precondition, data, steps and expected result. Use when the user asks for TC from AC or a feature.
---

# gen-testcase

## Input
- Feature folder or AC IDs.

## Steps
1. Read the config table in `CLAUDE.md`.
2. Read `qa/specs/<feature>/ac.md`.
3. Read `.claude/rules/naming.md`, `writing-style.md` and `domain.md`.
4. Read existing `qa/testcases/<feature>/tc.md`. Continue its numbering.
5. For each AC, write positive, negative and boundary TCs where they apply.
6. Fill every field of `qa/_templates/tc.md`.
7. Set `Priority` from AC criticality (Critical -> P1, High -> P1/P2, others -> P2/P3).
8. Set `Automation`: Candidate for stable, high-value or data-driven flows. Otherwise Not yet.
9. Add TC IDs to `qa/traceability/matrix.md`.
10. Report any AC with no TC and any gaps found.

## Quality bar
- Precondition states system and account state.
- Test data is explicit and synthetic.
- Steps are numbered, one action each.
- Expected result is observable: UI text, API field, status, stored record.

## Do not
- Do not create a TC without an AC link.
- Do not use real customer or account data.
