# Domain rules (rewrite per project)

This is the only rule file that changes between projects.
Replace the generic checklist with domain terms, limits, states and compliance items.

## Project domain
- Domain: <fill in>
- Key entities: <fill in>
- Key business rules: <fill in>
- Compliance or regulation: <fill in>

## Entities
| Entity | Meaning | Features that use it |
| --- | --- | --- |
| <entity> | <one line> | <feature codes> |

- `write-ac` searches other features by entity to find impacted existing behaviour.

## Glossary
| Term | Meaning |
| --- | --- |
| <term> | <one-line meaning> |

- If a term collides with a banned word, add it to the `Allow` table in `vocabulary.project.md`.

## Generic checklist (use to find missing AC and TC)

### Input and validation
- Required, optional, format, length, allowed characters.
- Boundary values: min, min-1, max, max+1, empty, null, zero, negative.

### Permission and roles
- Who can view, create, edit, delete, approve.
- Behavior for unauthenticated, unauthorized and expired sessions.

### State and lifecycle
- List all states and allowed transitions.
- Forbidden transitions must be rejected.

### Calculation and data
- Rounding, units, currency, time zone, date format.
- Totals shown in UI equal totals in API and storage.

### Errors and edge cases
- Error messages for each failure. Retry, timeout, duplicate submit.
- Partial failure and rollback.

### Integration
- Upstream and downstream systems, request and response contracts.
- Behavior when a dependency is slow or down.

### Audit and notification
- Who, what, when is logged.
- Notifications sent at key events.

### Data safety
- Use synthetic or masked data only in qa files.

## Examples of domain additions
- Payments: FX rate lock, fees, limits, corridors, KYC, sanctions screening, ledger.
- E-commerce: cart, stock, promo rules, tax, shipping, refunds.
