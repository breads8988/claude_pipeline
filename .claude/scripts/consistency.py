#!/usr/bin/env python3
"""Repo consistency check for the shared QA workspace.

Usage (repo root):
  python3 .claude/scripts/consistency.py [repo-root]

Checks every Markdown file except history files (docs/review-*.md, CHANGELOG.md):
  1. Single source: a rule text that may only appear in its source file.
  2. Stale terms: names that were retired or renamed.
  3. Frontmatter of .claude/**/*.md is valid YAML (skipped when PyYAML is missing).
  4. References `project.md` › <Field> name a field or heading of .claude/rules/project.md.
  5. Backticked repo paths (.claude/…, qa/_templates/…, docs/…) exist (not checked in docs/plan*, docs/backlog*).
  6. Notification names (**<Name>** notification) are events in comment-style notifications.md.

Exit codes: 0 clean · 1 findings · 2 usage or file error.
"""
import os
import re
import sys

# (pattern, the only file allowed to contain it, what it is)
SINGLE_SOURCE = [
    (r'highest criticality among', '.claude/rules/naming.md', 'TC priority rule'),
    (r'^\|\s*Depth\s*\|\s*EP\s*\|\s*BVA\s*\|', '.claude/skills/gen-testcase/references/test-design-techniques.md',
     'depth table'),
    (r'Only a TC that contains `TBD \(OQ-', '.claude/rules/naming.md', 'Blocked TC rule'),
]
# (pattern, message)
STALE = [
    (r'^(?!.*\bretired\b).*\bP[123]\b', 'P1–P3 priority is retired; use 🔴 🟠 🟡 ⚪'),
    (r'IIBA 9', 'cite BABOK v3 §7.2.4.1'),
    (r'\*\*(Lint failed|OQ resolved|Run finished)\*\*', 'retired notification'),
    (r'State: Running', 'run state is `In progress`'),
    (r'Invitee \(no login\)', 'role is `Anonymous`'),
    (r'BUG-TBD\.md|qa/bugs/|log-bug\b', 'bug drafts are qa/tickets/BUG-TBD-<TC-ID>.md (log-ticket)'),
    (r'3-value for 🔴', 'depth rule: test-design-techniques §3'),
]
PLANNED = re.compile(r'^docs/(plan|backlog)[^/]*\.md$')  # plans name files that do not exist yet
SKIP = re.compile(r'(^|/)(docs/review-[^/]*\.md|CHANGELOG\.md)$')
PATH_RE = re.compile(r'`((?:\.claude|qa/_templates|docs)/[^`\s<>*]+?)`')
FIELD_REF = re.compile(r'project\.md` › ([A-Za-z][A-Za-z /]+)')
NOTIF_REF = re.compile(r'\*\*([A-Z][A-Za-z ]+?)\*\* notification')


def md_files(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ('.git', '__pycache__', 'node_modules')]
        for f in files:
            if f.endswith('.md'):
                p = os.path.relpath(os.path.join(d, f), root).replace(os.sep, '/')
                if not SKIP.search(p):
                    yield p


def read(root, rel):
    with open(os.path.join(root, rel), encoding='utf-8-sig') as f:
        return f.read()


def project_fields(root):
    text = read(root, '.claude/rules/project.md')
    names = {m.group(1).strip().lower() for m in re.finditer(r'^\|\s*([^|]+?)\s*\|', text, re.M)}
    names |= {m.group(1).strip().lower() for m in re.finditer(r'^#+\s+(.+?)\s*(\(.*)?$', text, re.M)}
    return {n for n in names if n and not set(n) <= set('- ')}


def notification_events(root):
    text = read(root, '.claude/skills/comment-style/references/notifications.md')
    return {m.group(1).strip().lower() for m in re.finditer(r'^###\s+(.+?)\s*$', text, re.M)}


def check(root):
    findings = []
    try:
        fields = project_fields(root)
        events = notification_events(root)
    except OSError as e:
        raise SystemExit(f'consistency: {e}')
    try:
        import yaml
    except ImportError:
        yaml = None
    for rel in sorted(md_files(root)):
        text = read(root, rel)
        lines = text.split('\n')
        for pat, source, what in SINGLE_SOURCE:
            if rel == source:
                continue
            for i, l in enumerate(lines, 1):
                if re.search(pat, l):
                    findings.append(f'{rel}:{i}: {what} restated; point to {source}')
        for pat, msg in STALE:
            for i, l in enumerate(lines, 1):
                if re.search(pat, l):
                    findings.append(f'{rel}:{i}: stale term: {msg}')
        if yaml and rel.startswith('.claude/') and text.startswith('---\n'):
            end = text.find('\n---', 4)
            try:
                yaml.safe_load(text[4:end] if end > 0 else '')
            except yaml.YAMLError as e:
                findings.append(f'{rel}:1: frontmatter is not valid YAML ({str(e).splitlines()[0]})')
        for i, l in enumerate(lines, 1):
            for m in FIELD_REF.finditer(l):
                ref = m.group(1).strip().lower()
                if not any(ref.startswith(f) for f in fields):
                    findings.append(f'{rel}:{i}: project.md has no field "{m.group(1).strip()}"')
            for m in ([] if PLANNED.search(rel) else PATH_RE.finditer(l)):
                p = m.group(1).rstrip('.,;:)')
                if any(c in p for c in '<{*') or p.endswith('/…'):
                    continue
                if not os.path.exists(os.path.join(root, p)):
                    findings.append(f'{rel}:{i}: path `{p}` does not exist')
            for m in NOTIF_REF.finditer(l):
                name = m.group(1).strip().lower()
                if name not in events:
                    findings.append(f'{rel}:{i}: notification "{m.group(1)}" is not an event in notifications.md')
    return findings


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    root = os.path.abspath(argv[0] if argv else '.')
    if not os.path.isfile(os.path.join(root, '.claude/rules/project.md')):
        print(f'consistency: {root} is not the repo root (no .claude/rules/project.md)', file=sys.stderr)
        return 2
    findings = check(root)
    for f in findings:
        print(f'consistency: {f}')
    print(f'consistency: {len(findings)} finding(s)')
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
