---
description: Start a test cycle for a feature on staging and execute it
argument-hint: "<feature-folder> --build <build> --scope smoke|all|retest [TC-IDs]|regression [--change <JIRA-KEY>] · or --resume <run file>"
---

Start a run: $ARGUMENTS

`--resume <run file>`: skip Start; follow section **Execute** from the first `⬜` row.

1. Follow the `test-run` skill, section **Start**. Show the run file path and the TC count per role.
2. Then follow section **Execute**: run the `test-runner` agent once per role group.
3. When every row has a result, follow section **End** (same as `/end-run`).
