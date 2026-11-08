# Plan: UI interaction testing (hover, collapse, expand, tooltip …)

Status: all decisions agreed 2026-11-08 · Ready to build

## Problem
- AC and TC cover business behaviour well, but UI component behaviour has no model: default state, triggers (mouse, keyboard, focus), dismissal, persistence.
- Without a model, TCs check "it opens on click" and miss keyboard, Escape, focus, hover persistence and state attributes.

## Sources

| Source | What it gives |
|---|---|
| W3C WAI-ARIA Authoring Practices Guide (APG) | Expected behaviour per component pattern: keyboard keys, roles, states. Disclosure: Enter/Space toggles; `aria-expanded` true/false. Accordion: Enter/Space expand/collapse; single vs multiple open; `aria-disabled` when a panel cannot collapse. Tooltip: shows on hover or focus after a small delay; Escape dismisses; stays while the pointer is over trigger or tooltip; `role=tooltip`, `aria-describedby`. The tooltip pattern is marked work in progress (no consensus yet). |
| WCAG 2.2 SC 1.4.13 Content on Hover or Focus (AA) | Content shown on hover or focus must be **dismissible** (e.g. Esc, without moving pointer or focus), **hoverable** (pointer can move onto it), **persistent** (stays until trigger removed, dismissed or invalid). Failures F95, F114. Browser `title` tooltips are excepted. |
| WCAG 2.2 SC 2.1.1, 2.4.7, 4.1.2 | Keyboard operable; focus visible; name, role, value (state) exposed. |
| ISTQB CTFL v4.0.1 | §4.2.4 state transition testing (component states), §4.2.1–4.2.2 EP/BVA (viewport breakpoints), §4.4.3 checklist-based testing. |
| ISTQB CT-UT v1.0 (usability) | §4.2.3 heuristic evaluation with Nielsen's 10 heuristics; §3.2.2 WCAG levels, AA recommended; §3.1 UI guidelines as low-level rules. |

## Core idea
A UI component is a small state machine with a known pattern. Write it as a model in AC, test it with state transition + a pattern checklist in TC.

| Layer | Item | Technique |
|---|---|---|
| AC (behaviour, still implementation-free) | `UIC-<CODE>-NN` UI component model: pattern, default state, states, triggers, rules | — |
| TC | Each valid state change per trigger (click, Enter, Space, Escape, hover in/out, focus/blur) | State transition (§4.2.4) |
| TC | Pattern checklist items (APG keys and states, WCAG 1.4.13, 2.1.1, 2.4.7, 4.1.2) | Checklist-based (§4.4.3) |
| TC | Viewport breakpoints where layout or component changes (e.g. 767 / 768 px) | EP + BVA (§4.2.1–4.2.2) |
| Review (optional) | Nielsen's 10 heuristics on the screen | Heuristic evaluation (CT-UT §4.2.3) |

## Phase U1 · Model in AC

| # | Item | Files |
|---|---|---|
| U1.1 | New AC section **UI components**: one row per component — `UIC` ID, element, pattern (APG name), default state, states, triggers, rules (single/multiple open, persistence after reload or navigation, delay), criticality, covers AC | `qa/_templates/ac.md`, `naming.md` |
| U1.2 | AC wording stays behavioural: "the Fees section is collapsed by default; expanding it displays fee lines". Never selectors, pixels or click coordinates | `ac-techniques.md` |
| U1.3 | Analysis checklist adds: which components change state, their defaults, how the user triggers them, what persists | `ac-techniques.md` |
| U1.4 | Design sources, read in this order to save tokens: (1) design repo (local clone: component specs, tokens, exported frames), (2) Figma connector (frames named in the ticket), (3) Claude Design artifact link, (4) screenshots attached to the ticket. Unseen UI is never invented | `write-ac/SKILL.md`, `project.md` (`Design sources` table) |

## Phase U2 · Techniques in TC

| # | Item | Files |
|---|---|---|
| U2.1 | Shared **UI pattern checklist**, one block per pattern: disclosure, accordion, tooltip, menu button, dialog (modal), tabs, combobox/listbox, toast. Each item cites APG or WCAG | `gen-testcase/references/ui-pattern-checklist.md` |
| U2.2 | Technique map adds: `UIC` → state transition per trigger + pattern checklist; breakpoints → EP/BVA | `test-design-techniques.md` |
| U2.3 | Coverage item notation: `UIC-USR-01: Enter expands`, `UIC-USR-01 CHK: Esc dismisses`, `VP: 767 px` | `test-design-techniques.md` |
| U2.4 | Expected results state the visible result **and** the exposed state when checkable: "fee lines are displayed; `aria-expanded` = `true`" | `gen-testcase/SKILL.md`, example |
| U2.5 | Depth by criticality: 🔴 = every trigger + full pattern checklist; 🟠/🟡 = pointer + keyboard primary keys + 1.4.13 for hover content; ⚪ = pointer path + default state | `test-design-techniques.md` |
| U2.6 | Validator: every `UIC` has a TC per listed trigger; checklist items cited must exist in the pattern checklist | `coverage.py` + tests |

### WCAG by component (decision 1)
- Scope: WCAG 2.2 Level A + AA, applied only to the components present on the screen.
- `ui-pattern-checklist.md` maps each component type to its criteria. Examples:

| Component | WCAG 2.2 criteria checked |
|---|---|
| Disclosure, accordion | 2.1.1 Keyboard, 2.4.7 Focus Visible, 2.4.11 Focus Not Obscured, 4.1.2 Name Role Value (`aria-expanded`), 2.5.8 Target Size |
| Tooltip, popover | 1.4.13 Content on Hover or Focus, 2.1.1, 4.1.2 |
| Form field | 1.3.1 Info and Relationships, 3.3.1 Error Identification, 3.3.2 Labels, 3.3.3 Error Suggestion, 3.3.4 Error Prevention (financial), 3.3.7 Redundant Entry, 1.4.3 Contrast |
| Login | 3.3.8 Accessible Authentication |
| Dialog (modal) | 2.1.2 No Keyboard Trap, 2.4.3 Focus Order, 2.1.1, 4.1.2 |
| Drag and drop | 2.5.7 Dragging Movements |
| Status message, toast | 4.1.3 Status Messages, 2.2.1 Timing Adjustable |
| Text, images, icons | 1.1.1 Non-text Content, 1.4.3 Contrast, 1.4.11 Non-text Contrast, 1.4.4 Resize Text, 1.4.10 Reflow |
| Page | 2.4.2 Page Titled, 3.1.1 Language of Page, 3.2.6 Consistent Help, 2.4.1 Bypass Blocks |

## Phase U3 · Agent execution (Claude in Chrome)

Available actions (verified in the tool schema): `hover`, `key` (Enter, Space, Escape, Tab), `left_click`, `read_page` (accessibility tree), `find`, `zoom`, `screenshot` with `save_to_disk`.

| # | Item | Files |
|---|---|---|
| U3.1 | Interaction recipes in `test-runner`: hover → wait for the delay → check; move onto the tooltip → still displayed (hoverable); Escape → hidden (dismissible); Tab to trigger → focus visible; Enter/Space → toggles | `.claude/agents/test-runner.md` |
| U3.2 | State check: read `aria-expanded`, `role`, `aria-describedby` from the accessibility tree instead of guessing from pixels | `test-runner.md` |
| U3.3 | Animations: wait until the transition ends before asserting; a timeout is a Fail with note `no state change after <n> s` | `test-runner.md` |
| U3.4 | Viewport TCs: set the window size, then run the steps | `test-runner.md` |

## Phase U5 · Heuristic review (decision 4)

| # | Item | Files |
|---|---|---|
| U5.1 | `/heuristic-review <screen or feature>`: optional review of a screen against Nielsen's 10 heuristics (ISTQB CT-UT §4.2.3). Findings only linked to a heuristic; no invented heuristics | `.claude/commands/heuristic-review.md` |
| U5.2 | Output: findings table (heuristic, location, issue, severity 🔴🟠🟡⚪, suggestion) saved to `qa/reports/heuristic-<feature>-<date>.md`; serious findings can become open questions or tickets | command, `log-ticket` |
| U5.3 | Runs on staging through Claude in Chrome, or on designs from the design sources | command |

## Phase U4 · Example
- Add to `_example`: a disclosure (invitation details row) and a tooltip (role info icon) with UIC rows, TCs for each trigger and checklist items, and the validator at 100%.

## Out of scope (now)

| Item | Why |
|---|---|
| Pixel-perfect visual comparison | Needs visual-regression automation |
| Screen-reader output | The agent reads ARIA attributes, not spoken output |
| Touch gestures (no hover on touch) | Staging runs in desktop Chrome |
| Full WCAG audit | Only the interaction criteria above unless decided otherwise |

## Decisions

| # | Decision |
|---|---|
| 1 | Accessibility: WCAG 2.2 Level A + AA, applied per component present on the screen (mapping table above). |
| 2 | Viewports: desktop is active. Tablet and mobile rows are kept in `project.md`, commented out, for later. |
| 3 | Design sources in order: design repo → Figma connector → Claude Design link → screenshots. Repo first to save tokens. |
| 4 | Heuristic review: added as an optional command (`/heuristic-review`). |
