# Traceability matrix

One row per AC. Update after every AC or TC change.

| Column | Rule |
| --- | --- |
| Ticket | Jira key of the AC |
| Feature | Feature Code |
| AC | One AC ID |
| Criticality | Criticality of the AC (🔴 🟠 🟡 ⚪) |
| TC | Every TC ID that lists this AC in `Covers AC`, comma-separated. Blocked TCs end with `(Blocked)` |
| Automation | Most advanced state among the TCs: Not yet · Candidate · Done |
| Auto script | Script path. Empty until automation exists |

- Deprecated AC: keep the row, add `(Deprecated)` after the ID.
- AC with no TC yet: TC cell `—`.
- Rows from `_example` are never added here.

| Ticket | Feature | AC | Criticality | TC | Automation | Auto script |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |
