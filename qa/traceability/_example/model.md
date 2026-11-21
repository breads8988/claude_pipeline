# Business impact model (golden example)

Golden example for `qa/traceability/model.md`. Not a real project. Used by `graph.py --example`.

## Features

| Code | Module | Depends on | Owner |
| --- | --- | --- | --- |
| USR | Access | — | qa.lead |
| SGN | Access | USR | qa.lead |

## Entities

| Entity | Meaning | Owner | Scope |
| --- | --- | --- | --- |
| User | A person with a workspace account | — | Broad |
| Invitation | An invitation sent to an email, with status `Invited`, `Accepted` or `Expired` | USR | Normal |
| Account | The login of a user, with status `Pending` or `Active` | USR | Normal |

## Shared rules

| Rule ID | Rule | Criticality | Hubs | Status |
| --- | --- | --- | --- | --- |
| RULE-ACC-001 | Email match is case-insensitive: `Ana@x.test` equals `ana@x.test`. | 🔴 | — | Active |

## Impact hubs

| Hub ID | Applies when | Checklist |
| --- | --- | --- |
| HUB-access-control | A change touches roles, permissions or account status | Each role has only its own actions; direct request to a hidden action is rejected; expired session is rejected |

## Screens

| Screen ID | Name | Path | Roles |
| --- | --- | --- | --- |
| SCR-users | User list | Settings › Users | Admin, Viewer |
| SCR-invite-dialog | Invite user dialog | Settings › Users › Invite user | Admin |
| SCR-accept-invite | Accept invitation | Invitation link | Anonymous |
| SCR-sign-in | Sign-in | /sign-in | Anonymous |
