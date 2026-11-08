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
| ISTQB CTFL v4.0.1 | sec. 4.2.4 state transition testing (component states), sec. 4.2.1–4.2.2 EP/BVA (viewport breakpoints), sec. 4.4.3 checklist-based testing. |
| ISTQB CT-UT v1.0 (usability) | sec. 4.2.3 heuristic evaluation with Nielsen's 10 heuristics; sec. 3.2.2 WCAG levels, AA recommended; sec. 3.1 UI guidelines as low-level rules. |

## Core idea
A UI component is a small state machine with a known pattern. Write it as a model in AC, test it with state transition + a pattern checklist in TC.

| Layer | Item | Technique |
|---|---|---|
| AC (behaviour, still implementation-free) | `UIC-<CODE>-NN` UI component model: pattern, default state, states, triggers, rules | — |
| TC | Each valid state change per trigger (click, Enter, Space, Escape, hover in/out, focus/blur) | State transition (sec. 4.2.4) |
| TC | Pattern checklist items (APG keys and states, WCAG 1.4.13, 2.1.1, 2.4.7, 4.1.2) | Checklist-based (sec. 4.4.3) |
| TC | Viewport breakpoints where layout or component changes (e.g. 767 / 768 px) | EP + BVA (sec. 4.2.1–4.2.2) |
| Review (optional) | Nielsen's 10 heuristics on the screen | Heuristic evaluation (CT-UT sec. 4.2.3) |

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

| Component | WCAG 2.2 success criteria checked (level) |
|---|---|
| Disclosure, accordion | 2.1.1 Keyboard (A), 2.4.7 Focus Visible (AA), 2.4.11 Focus Not Obscured (Minimum) (AA), 4.1.2 Name, Role, Value (A) (`aria-expanded`), 2.5.3 Label in Name (A), 2.5.8 Target Size (Minimum) (AA) |
| Tooltip, popover | 1.4.13 Content on Hover or Focus (AA), 2.1.1 Keyboard (A), 4.1.2 Name, Role, Value (A) |
| Form field | 1.3.1 Info and Relationships (A), 1.3.5 Identify Input Purpose (AA), 1.4.1 Use of Color (A), 1.4.3 Contrast (Minimum) (AA), 2.4.6 Headings and Labels (AA), 2.5.3 Label in Name (A), 3.2.2 On Input (A), 3.3.1 Error Identification (A), 3.3.2 Labels or Instructions (A), 3.3.3 Error Suggestion (AA), 3.3.4 Error Prevention (Legal, Financial, Data) (AA), 3.3.7 Redundant Entry (A) |
| Login | 3.3.8 Accessible Authentication (Minimum) (AA), 1.3.5 Identify Input Purpose (AA) |
| Dialog (modal) | 2.1.1 Keyboard (A), 2.1.2 No Keyboard Trap (A), 2.4.3 Focus Order (A), 4.1.2 Name, Role, Value (A) |
| Drag and drop | 2.5.7 Dragging Movements (AA) |
| Status message, toast | 4.1.3 Status Messages (AA), 2.2.1 Timing Adjustable (A) |
| Text, images, icons | 1.1.1 Non-text Content (A), 1.4.1 Use of Color (A), 1.4.3 Contrast (Minimum) (AA), 1.4.4 Resize Text (AA), 1.4.10 Reflow (AA), 1.4.11 Non-text Contrast (AA), 1.4.12 Text Spacing (AA) |
| Page | 2.4.1 Bypass Blocks (A), 2.4.2 Page Titled (A), 2.4.6 Headings and Labels (AA), 3.1.1 Language of Page (A), 3.2.6 Consistent Help (A) |

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
| U5.1 | `/heuristic-review <screen or feature>`: optional review of a screen against Nielsen's 10 heuristics (ISTQB CT-UT sec. 4.2.3). Findings only linked to a heuristic; no invented heuristics | `.claude/commands/heuristic-review.md` |
| U5.2 | Output: findings table (heuristic, location, issue, severity 🔴🟠🟡⚪, suggestion) saved to `qa/reports/heuristic-<feature>-<date>.md`; serious findings can become open questions or tickets | command, `log-ticket` |
| U5.3 | Runs on staging through Claude in Chrome, or on designs from the design sources | command |

## Phase U6 · Design check (separate from functional TCs)

Placement: side flow **5b**, run alongside stage 5 on staging when a screen is new or its UI changes. It does not block gates G1/G2. Input: design sources from stage 0. Output: UI bugs into stage 7. Shares the staging, browser agent, design sources, `log-ticket` and reports.

Why separate from TCs: the source of truth is the design (not the AC), it runs when a screen is new or its UI changes (not every regression), the audience is designers and frontend developers, and the result is a list of deviations with tolerances. Mixing it into TCs would bloat the suite and tie AC to pixels.

| # | Item | Files |
|---|---|---|
| U6.1 | `/design-check <screen or feature>` on staging through Claude in Chrome | `.claude/commands/design-check.md` |
| U6.2 | Spec from the design sources, design repo first (token JSON is cheapest), then Figma variables and frames | command, `project.md` (`Design sources`) |
| U6.3 | **CSS vs token comparison** per component: color, font family, size, weight, line height, padding, margin, gap, radius, border, width and height. Values read from the computed style of the element | command |
| U6.4 | Tolerances in `project.md` (`Design tolerances`): color exact hex, font exact, size ±1 px, spacing ±2 px | `project.md` |
| U6.5 | Optional side-by-side: staging screenshot next to the design frame, Claude lists visible differences (missing element, wrong layout). Used only when the CSS check passes but the screen still looks wrong | command |
| U6.6 | Report `qa/reports/design-<feature>-<date>.md`: component, property, design value, actual value, deviation, severity. Real deviations → `log-ticket` UI bug with a link to the design frame | command, `log-ticket` |

Split into its own pipeline when at least one holds:
- Designers or frontend developers own design checks instead of QA.
- A component library exists (e.g. Storybook): check each component once, before staging (shift-left), instead of every screen.
- A design-token repo changes often and needs a check on every token change.
- Visual regression moves to automation and runs in CI on every PR.

Not in this phase: pixel diff regression (new build vs previous screenshot). It belongs to automation (e.g. visual snapshots) and is in the backlog.

## Phase U4 · Example
- Add to `_example`: a disclosure (invitation details row) and a tooltip (role info icon) with UIC rows, TCs for each trigger and checklist items, and the validator at 100%.

## Out of scope (now)

| Item | Why |
|---|---|
| Pixel diff regression (new build vs previous) | Needs visual-regression automation; design-vs-build comparison is covered by U6 |
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
| 5 | Design comparison: separate `/design-check` (CSS vs token, tolerances, optional side-by-side). Pixel diff regression goes to automation later. |
