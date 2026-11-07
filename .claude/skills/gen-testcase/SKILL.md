---
name: gen-testcase
description: Design manual test cases from approved acceptance criteria with ISTQB techniques (EP, BVA, decision table, state transition, scenario, checklist), risk-based depth and measured coverage. Use when the user asks for TC from AC or a feature.
---

# gen-testcase

Method: `references/test-design-techniques.md`. Format: `qa/_templates/tc.md`. Reference: `qa/testcases/_example/tc.md`.

## Gate
- Read the header of `qa/specs/<feature>/ac.md`.
- `Status` is not `Approved` → stop. Reply: `AC is <status>. Run /approve <feature> first.`

## Steps
1. Read `.claude/rules/project.md` (Feature Codes, roles, notifications) and `.claude/rules/domain.md` (checklist).
2. Read `qa/specs/<feature>/ac.md`, `references/test-design-techniques.md` and `qa/testcases/_example/tc.md`.
3. Read existing `qa/testcases/<feature>/tc.md`. Continue its numbering.
4. **Test analysis** (§1, §2): list test conditions from every active AC, BR, FLD, DT column, ST transition and applicable checklist item.
5. **Depth** (§3): set each item's depth from its criticality; raise one level for `Likelihood: High`.
6. **Coverage items**: derive them per technique and depth: partitions, boundary values, DT columns, transitions (invalid ones for 🔴), scenarios, checklist items, error guesses.
7. **Design TCs**:
   - Order: positive, negative, non-functional (ATDD).
   - Combine valid partitions in one TC; one invalid partition per TC; one invalid transition per TC.
   - No two TCs for the same coverage item and characteristic.
   - Steps use real element names and run as the TC's `Role`.
8. Fill every field of `qa/_templates/tc.md`, including `Technique` and `Coverage items` (notation §4).
9. Set `Priority` = highest criticality among the TC's coverage items (§5).
10. AC listed in an open question's `Blocks` → write the TC anyway: `Status: Blocked`, `Blocked by: <OQ-ID>`, and `TBD (<OQ-ID>): <unknown part>`.
11. Set `Automation`: `Candidate` for stable, high-value or data-driven flows; else `Not yet`. `Type: Non-functional` TCs run only when they can be checked manually on staging.
12. Fill the **Coverage summary** in the header: per technique, items identified, covered, %.
13. Set the header: `Status: Draft`, `Last updated`.
14. Run the coverage validator and the lint; fix until both exit 0:
    - `python3 .claude/skills/gen-testcase/scripts/coverage.py qa/specs/<feature>/ac.md qa/testcases/<feature>/tc.md`
    - `python3 .claude/skills/comment-style/scripts/lint.py qa/testcases/<feature>/tc.md`
15. Add TC IDs to `qa/traceability/matrix.md`.
16. Send the **TC ready for review** notification: TC count by priority, coverage % per technique, blocked TC count.

## Do not
- Do not create a TC without a coverage item from `ac.md`.
- Do not test beyond the AC; raise a missing case as an open question on the AC instead.
- Do not use real customer or account data.
- Do not set `Approved`. Only `/approve --tc` does that.
