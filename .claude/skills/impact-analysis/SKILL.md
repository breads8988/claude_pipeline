---
name: impact-analysis
description: Find AC, TC, features and impact hubs affected by a change, using the business impact graph (features, shared rules, business entities, hubs, screens). Use when scope changes, a rule or screen changes, or before a regression plan.
---

# impact-analysis

Graph rules: `.claude/rules/naming.md` › Impact graph. Nodes: `qa/traceability/model.md`.
Tool: `scripts/graph.py` (stdlib). Golden example: `graph.py --example impact AC-USR-006`.

## Input
- A Jira key, an AC, TC, `RULE-`, `HUB-` or `SCR-` ID, a Feature Code or an entity name.
- Or a change description. Map it to those IDs first and list the mapping.

## Steps
1. Run `graph.py check`. Errors → report them first; impact on a broken graph misses items.
2. Run `graph.py impact <ID> [<ID> …]`. Default depth 1. Use `--depth 2` only when the user asks, or for a 🔴 shared rule.
3. Read the AC listed with `Update` or `Re-check`. Confirm each one is really affected. Drop a row only with a one-line reason.
4. For each Hub row: add its checklist items to the regression scope.
5. For each Feature row (`Regression check`): add its 🔴 TCs as a smoke set.
6. List new AC or TC that the change needs.
7. Optional: `graph.py view <ID> --mermaid` for a picture of the local graph.

## Propagation rules (single source)
| Change | Reaches |
| --- | --- |
| AC, Jira key, feature | Its TC; AC of other features through its shared rules and the Normal entities its feature owns |
| Shared rule | Every AC that uses it, and their TC |
| Entity | Every AC that uses it, and their TC |
| Screen | TC on the screen and their AC only; no business propagation |
| Any listed AC | Hubs of the AC and of its rules, with the checklist |
| Changed feature | Features that depend on it, as a regression row |

- An entity reader's change does not reach the owner or other readers.
- Propagation never re-enters a changed feature and never passes a Broad entity or a hub.
- `--depth N` adds hops; each hop crosses one shared rule or owned entity.

## Output (table)
| Item | ID | Distance | Via | Criticality | Action |
| --- | --- | --- | --- | --- | --- |
| AC | AC-USR-006 | 0 | changed | 🔴 | Update |
| AC | AC-SGN-003 | 1 | Account | 🔴 | Re-check |
| Hub | HUB-access-control | 1 | AC-SGN-003 | — | Run checklist |

- Keep the tool's order: distance, then item type, then criticality.
- Add: rows you dropped and why, gaps (`no TC`, unlinked AC), Broad entities to review by hand, open questions.
- Do not edit files unless the user asks.

## Do not
- Do not guess links missing from the graph. Report the gap and propose the `model.md` row or AC bullet.
- Do not expand through a Broad entity by hand to "be safe". List it for a human decision.
