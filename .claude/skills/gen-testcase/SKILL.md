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
4. **Test analysis** (§1, §2): list test conditions from every active AC, BR, FLD, DT column, ST transition and applicable checklist item. Write the EP partitions and BVA values into `## Test analysis` of `tc.md`.
5. **Depth** (§3): set each item's depth by the rule in §3.
6. **Coverage items**: derive them per technique and depth: partitions, boundary values, DT columns, transitions (invalid ones at 🔴 depth, §3), scenarios, checklist items, error guesses.
   - 3+ parameters whose combinations matter → pairwise rows with `pairwise.py` (references §Pairwise).
   - Thin spec or 🔴 area → add exploratory charters (`CH-<CODE>-NN`).
7. **Design TCs**:
   - Order: positive, negative, non-functional (ATDD).
   - Combine valid partitions in one TC; one invalid partition per TC; one invalid transition per TC.
   - No two TCs for the same coverage item and characteristic.
   - Steps run as the TC's `Role`. Element names (buttons, fields, menus) come from `project.md` › Design sources or screenshots the user attached. No source → write `TBD (UI): <element>` and list it in the notification. Never invent a name.
8. Fill every field of `qa/_templates/tc.md`, including `Technique` and `Coverage items` (notation §4).
9. Set `Priority` per `.claude/rules/naming.md` › Criticality and priority.
10. Content that depends on an open question → write the TC anyway with `TBD (<OQ-ID>): <unknown part>`, `Status: Blocked`, `Blocked by: <OQ-ID>`. TCs that do not depend on it stay `Active`.
11. Set `Automation`: `Candidate` for stable, high-value or data-driven flows; else `Not yet`. `Type: Non-functional` TCs run only when they can be checked manually on staging.
12. Set the header: `Status: Draft`, `Last updated`. Save `tc.md`.
13. Run the validator with `--summary`, paste its table into `## Coverage summary`, run it again; fix and re-run, max 3 attempts. Errors left → list them in the notification:
    - `python3 .claude/skills/gen-testcase/scripts/coverage.py qa/specs/<feature>/ac.md qa/testcases/<feature>/tc.md --summary`
14. Run the lint; fix and re-run, max 3 attempts. Errors left → list them in the notification: `python3 .claude/skills/comment-style/scripts/lint.py qa/testcases/<feature>/tc.md`
15. Run the `tc-reviewer` agent. Fix its findings, then re-run steps 13–14.
16. In `qa/traceability/matrix.md`, fill the TC and Automation cells of each AC row (rules in the file header).
17. Last: send the **TC ready for review** notification: TC count by priority, coverage % per technique, blocked count, reviewer findings left open.

## Do not
- Do not create a TC without a coverage item from `ac.md`.
- Do not test beyond the AC. Error guessing and checklist TCs need a `Covers AC`; a missing case becomes an AC or an open question first.
- Do not use real customer or account data.
- Do not set `Approved`. Only `/approve --tc` does that.
