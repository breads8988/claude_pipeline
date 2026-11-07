---
description: Start a test cycle for a feature on staging and execute it
argument-hint: <feature-folder> --build <build> --scope smoke|regression|all|retest [TC-IDs]
---

Start a run: $ARGUMENTS

1. Follow the `test-run` skill, section **Start**. Show the run file path and the TC count per role.
2. Then follow section **Execute**: run the `test-runner` agent on the run file.
3. When every row has a result, follow section **End** (same as `/end-run`).
