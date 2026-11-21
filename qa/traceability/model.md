# Business impact model (per project)

Nodes that link features to each other. `graph.py` parses this file with every `ac.md` and `tc.md`.
Rules for IDs and edges: `.claude/rules/naming.md` › Impact graph.

- Keep every table, even when empty. A row is one node.
- `—` = none. Lists are comma-separated.
- A node used by only one feature adds no cross-feature link. Keep it in the feature's own `ac.md` instead.

## Features
Every Feature Code in `.claude/rules/project.md`, plus the features it needs.

| Code | Module | Depends on | Owner |
| --- | --- | --- | --- |

## Entities
Business concepts that BA and users name. Not database tables.

| Entity | Meaning | Owner | Scope |
| --- | --- | --- | --- |

- `Owner`: the Feature Code that creates or changes the entity. Other features only read it.
- A change in the owner reaches every reader. A change in a reader does not reach the owner.
- `Scope`: `Normal` or `Broad`. Broad = used by most features (e.g. `User`). Impact lists it but does not expand through it.

## Shared rules
Business rules used by 2 or more features. A rule of one feature remains a `BR-` row in its `ac.md`.

| Rule ID | Rule | Criticality | Hubs | Status |
| --- | --- | --- | --- | --- |

## Impact hubs
Risk areas to check on every change that touches them.

| Hub ID | Applies when | Checklist |
| --- | --- | --- |

## Screens
Screens named in TC steps. One row per screen, not per component.

| Screen ID | Name | Path | Roles |
| --- | --- | --- | --- |
