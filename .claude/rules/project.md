# Project config (per-project: fill in once)

Skills read this file. Keep it up to date. Everything project-specific that is not domain knowledge goes here.
Keep every row. A field the project does not use: write `—`.

| Field | Value |
| --- | --- |
| Project name | <name> |
| Domain | <e.g. payments, e-commerce, HR> |
| Jira project key | <e.g. ABC> |
| Atlassian site | <e.g. yourcompany.atlassian.net, or cloudId> |
| Doc language | English |
| Automation stack | None yet |
| AC source of record | repo |
| Notifications | Claude notification |

## Feature Codes

| Code | Feature | Folder |
| --- | --- | --- |
| <3-4 chars, e.g. USR> | <feature name> | <kebab-case, e.g. user-invitation> |

## Jira mapping

| Field | Value |
| --- | --- |
| Bug issue type | <e.g. Bug> |
| Task issue type | <e.g. Task> |
| Priority values (🔴 🟠 🟡 ⚪) | <e.g. Highest · High · Medium · Low> |
| Severity field | <field name and values, or —> |
| Component | <default component, or —> |
| Required fields on create | <extra required fields, or —> |
| Bug or task | Bug: displayed or stored result differs from an approved AC or TC. Task: anything else (test data, environment, tooling). |

## Test environment

| Field | Value |
| --- | --- |
| Staging URL | <https://staging.example.com> |
| Allowed hosts | <exact hosts the agent may open, comma-separated: staging + login or IdP host, e.g. staging.example.com, auth.staging.example.com> |
| Login | App login form |
| OTP / 2FA | None |
| Test mailbox | <inbox or mail-catcher URL for invite links and email OTP, or —> |
| Test data backdoor | <seed script, admin page or API to set preconditions, or —> |

- The test agent opens the Allowed hosts only, exact host match (no subdomain wildcard). Any other host pauses the run.
- Test mailbox and backdoor hosts must be in Allowed hosts.
- Passwords are never stored here. They live in `qa/test-accounts.local.md` (git-ignored, copy from `qa/_templates/test-accounts.local.md`).

## Roles and test accounts

| Role | Test account | Can do |
| --- | --- | --- |
| <role, e.g. Admin> | <username, e.g. qa_admin_01> | <one line> |
| Anonymous | — (no login) | <what is displayed to a visitor, or —> |

## Comment caps (leave empty to use the `comment-style` defaults)

| Item | Value |
| --- | --- |
| Whole comment (lines) | |
| Headline (words) | |
| Table cell (words) | |

## UI and design (later: `docs/plan-ui-interaction.md`)

| Field | Value |
| --- | --- |
| Design sources | <in order: design repo path · Figma file · Claude Design link · screenshots folder, or —> |
| Design tolerances | color exact hex · font exact · size ±1 px · spacing ±2 px |
| Viewport desktop | 1440 × 900 |
<!-- | Viewport tablet | 768 × 1024 | -->
<!-- | Viewport mobile | 390 × 844 | -->
