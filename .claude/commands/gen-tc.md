---
description: Generate manual test cases from the approved AC of a feature
argument-hint: <feature-folder>
---

Use the `gen-testcase` skill for: $ARGUMENTS

The skill stops when the AC file is not `Approved`. It runs the coverage validator, the lint and the `tc-reviewer` agent before it sends the notification.
