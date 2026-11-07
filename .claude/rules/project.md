# Project config (per-project: fill in once)

Skills read this file. Keep it up to date. Everything project-specific that is not domain knowledge goes here.

| Field | Value |
| --- | --- |
| Project name | <name> |
| Domain | <e.g. payments, e-commerce, HR> |
| Jira project key | <e.g. ABC> |
| Doc language | English |
| Automation stack | None yet |
| AC source of record | repo |
| Notifications | Claude notification |

## Feature Codes

| Code | Feature | Folder |
| --- | --- | --- |
| <3-4 chars, e.g. TRF> | <feature name> | <kebab-case, e.g. transfer> |

## Test environment

| Field | Value |
| --- | --- |
| Staging URL | <https://staging.example.com> |
| Login | App login form |
| OTP / 2FA | None |

- The test agent opens this host only. Any other host stops the run.
- Passwords are never stored here. They live in `qa/test-accounts.local.md` (git-ignored, copy from `qa/_templates/test-accounts.local.md`).

## Roles and test accounts

| Role | Test account | Can do |
| --- | --- | --- |
| <role, e.g. Admin> | <username, e.g. qa_admin_01> | <one line> |

## Comment caps (leave empty to use the `comment-style` defaults)

| Item | Value |
| --- | --- |
| Whole comment (lines) | |
| Headline (words) | |
| Table cell (words) | |
