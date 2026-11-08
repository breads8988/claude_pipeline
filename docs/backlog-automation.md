# Backlog: automation (API and E2E)

Status: backlog 2026-11-08 · To discuss after the manual pilot

## Principle
- Test pyramid (ISTQB CTFL v4.0.1 §5.1.6). Internal principle based on it: put each check at the lowest layer that can detect the defect.
- API tests are the bulk. E2E stays a few journeys per feature. The rest stays manual.

## AC item → layer

| AC item | API automation | E2E automation (UI) | Manual (Mode B / human) |
|---|---|---|---|
| `FLD` EP and BVA | All partitions and boundaries, data-driven | One valid case inside the main journey | Until the API exists |
| `DT` decision table (fees, limits, eligibility) | Every column | — | — |
| `DT` role × action | Every cell: 401 / 403 for roles not permitted | 1–2 cases: hidden action | Hidden vs displayed in the UI |
| `ST` state model | Every transition, invalid ones included | Main path only | — |
| `BR` calculations (fee, FX, rounding) | All | Displayed value matches the API in one case | — |
| 🔴 scenarios (main journeys) | Each step at API level | Main journey across systems | First runs, before the flow is stable |
| `UIC` UI interactions | — | Critical interactions on 🔴 screens only | Most, by APG checklist |
| WCAG | — | Automated scan on key pages (partial) | The rest |
| Design check | — | Visual regression (snapshots) | `/design-check` |
| Heuristic, exploratory | — | — | All |

## API automation scope
- Validation: every partition and boundary; error codes and error format.
- Business rules: fees, FX, rounding, limits, eligibility (e.g. KYC, sanctions); every decision table column.
- Authorisation: every role × action, expired token, access to another user's resource.
- Lifecycle: every valid and forbidden transition.
- Non-functional at API level: idempotency (same request twice creates one record), concurrency, timeout and retry, partner failure through stubs.
- Contracts: schema, status codes, error format between services.

## E2E automation scope
- 🔴 main journeys across systems (e.g. log in → create → confirm → status displayed → notification).
- Multi-role flows (e.g. maker creates, checker approves).
- Smoke per build: a few journeys.
- Critical UI interactions on 🔴 screens only.
- Later: automated accessibility scan, visual regression.

## Pipeline changes when automation starts
| Item | Change |
|---|---|
| TC field `Layer` | `API` / `E2E` / `Manual`, proposed by `gen-testcase` from the table above |
| `Automation: Candidate` | Stable, 🔴/🟠, data-driven, repeated in regression |
| Script tags | `@TC-<CODE>-NNN` (already in `naming.md`) so matrix and reports merge manual and automated results |
| Folders | `automation/api/`, `automation/e2e/`, shared fixtures; stack chosen per project in `project.md` |
| CI | API suite on every PR; E2E smoke per build; full E2E nightly |

## Open points for the discussion
- Stack per layer (e.g. API: REST client + test runner; E2E: Playwright).
- Test data and stubs for partners on staging.
- Who writes and maintains scripts; review rules.
- Where results land: run files, HTML report, or a test dashboard.
