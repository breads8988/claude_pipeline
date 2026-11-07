# AC / TC vocabulary (shared)

Technical words for AC and TC text. `scripts/lint.py` reads every table whose first header is `Banned`.

## How the lint reads this file

| Column | Meaning |
|---|---|
| Banned | Plain words, comma-separated. `…` matches one word. Text in `( )` is a note. `/regex/` is a case-sensitive pattern. |
| Use | Replacement shown in the lint output. |
| Level | `error` fails the lint (exit 1). `warn` prints only. Empty means `error`. |
| Example | For writers. Not read by the lint. |

- Text in backticks or double quotes (app copy) is never linted.
- Projects add, replace or allow words in `.claude/rules/vocabulary.project.md`.
- Inside a `/regex/`, write `\|` for alternation and `\x7c` for a literal pipe.

## 1 · Navigation and actions (When, TC steps)

| Banned | Use | Level | Example |
|---|---|---|---|
| /(?:^\s*(?:\d+\.\s+)?\|\x7c\s*)Open\s+(?=[A-Z])/ (Open <Page> at step start) | navigate to | error | Navigate to `<Page>` › `<Tab>` |
| views, view | navigates to · is on | warn | When the user navigates to the `<Tab>` tab |
| sees | is displayed | error | the error state is displayed |
| choose, chooses | select (option) · click (card, button) | error | Select `<option>` in the `<Field>` dropdown |
| pick, picks, picked | select · selected · auto-selected | error | the selected `<item>` |
| find the | locate | error | Locate `<element>` |
| tries to | attempts to | error | attempts to submit |
| any entry point, anywhere else, every other entry, elsewhere | each entry by name | error | `<Page A>` button, `<Page B>` link |
| switch the stub | set the stub to return | error | Set the `<service>` stub to return HTTP 200 |
| leaves | clears · submits … blank · returns no results | warn | clears the `<Field>` field |
| typed | entered | error | the amount entered |
| look at | locate | error | Locate the `<Column>` column |

## 2 · UI state and display (Then, Expected result)

| Banned | Use | Level | Example |
|---|---|---|---|
| shown, shows, show | displayed · displays | error | the `<Button>` button is displayed |
| reads | displays text … (exact match) | warn | `<element>` displays `<copy>` (exact match) |
| word for word | (exact match) | error | |
| offered | available · enabled · listed in `<menu>` | error | listed in the column menu |
| stays | remains · persists | error | the error state persists |
| still | remains · persists | warn | |
| unavailable | disabled | error | the `<Button>` button is disabled |
| not shown | hidden · not rendered | error | the `<Column>` column is hidden |
| holds | contains · is populated with | warn | the field is populated with `<value>` |
| nothing happens | no action: no navigation, no request | error | |
| gone | removed · deleted | error | the `<item>` is deleted |
| back on | resets to | error | pagination resets to page 1 |
| the one | the `<named>` record · option | warn | the inactive `<option>` option |
| same as | unchanged · identical to | warn | the amount is unchanged |
| no longer exists | deleted · removed | error | the draft is deleted |

## 3 · Data and status

| Banned | Use | Level | Example |
|---|---|---|---|
| lands, lands in | status transitions to · status = | error | status = `<Status>` |
| moves it, moves to | transitions to | error | transitions to `<Status>` |
| becomes | transitions to · is set to | error | |
| noted | logged (timeline event) · captured as `<variable>` | warn | `<ID>` captured as `<own ID>` |
| nothing changes, no … changes | no side effects: … not created or updated | error | no side effects: no `<record>` updated |
| kept, keeps | persisted · retained | warn | the `<name>` is retained |
| carries, carry | contains · is formatted with | warn | formatted with 2 decimals |
| not yet | pending · before `<event>` | warn | |
| goes, goes to | transitions to | warn | status transitions to `<Status>` |
| happens | occurs · is executed | warn | the posting is executed |

## 4 · Validation and errors

| Banned | Use | Level | Example |
|---|---|---|---|
| refused | rejected with `ERR-…` | error | rejected with `ERR-<CODE>-NN`: `<copy>` |
| blocked | rejected · disabled · not permitted | warn | |
| cannot | is not permitted (role) · disabled (UI) | warn | the `<Toggle>` toggle is disabled |
| does not respond | times out · returns HTTP 5xx | error | the `<service>` returns HTTP 503 |
| not allowed | not permitted | error | |
| is cut, are cut, cut to | truncated · truncated to | error | extra decimals truncated to 2 |

## 5 · System and integration

| Banned | Use | Level | Example |
|---|---|---|---|
| on its own | automatically · no auto-transition | error | |
| fires | is sent · is triggered | error | notification `<ID>` is sent |

"Run" stays: a test run is "this test run", never "this execution". A process that runs "is executed" or "is triggered".

## Sentence templates (Then, Expected result)

1. `<element>` displays `<copy>` (exact match)
2. `<element>` is enabled · disabled · hidden
3. status = `<Status>` · status transitions to `<Status>`
4. no side effects: `<record>` not created · updated · posted
5. rejected with `ERR-<CODE>-NN`: `<copy>`

## UI element names

button · toggle · dropdown · checkbox · radio · field · modal · drawer · side sheet · popover · toast · tooltip ·
badge · chip · tab · grid · column · row menu · pager · empty state · error state · stepper
