#!/usr/bin/env python3
"""Vocabulary lint for AC and TC files (comment-style skill).

Usage:
  python3 lint.py <file.md> [<file.md> ...] [--vocab FILE]... [--shared FILE] [--no-project]

Vocabulary load order (later wins on the same Banned term):
  1. Shared list: ../references/vocabulary.md (or --shared FILE).
  2. Project list: .claude/rules/vocabulary.project.md, found by walking up from each
     page's folder, then from the current directory (skip with --no-project).
  3. Each --vocab FILE.
A table whose first header is `Allow` removes terms from the merged list.

Skipped in pages: front matter, fenced code, table header and separator rows,
text in backticks or double quotes (app copy), ALL-CAPS matches longer than 3 chars.

Exit codes: 0 no errors (warnings allowed) · 1 error-level hits · 2 usage, file or vocabulary error.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED_DEFAULT = os.path.normpath(os.path.join(HERE, '..', 'references', 'vocabulary.md'))
PROJECT_REL = os.path.join('.claude', 'rules', 'vocabulary.project.md')
LEVELS = ('error', 'warn')

SEP_RE = re.compile(r'^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$')
CELL_SPLIT = re.compile(r'(?<!\\)\|')
QUOTED = re.compile(r'`[^`]*`|"(?=\S)[^"\n]*(?<=\S)"|“[^”\n]*”')
PLACEHOLDER = ' QQ '  # replaces app copy so surrounding words never join
NOISE = re.compile(r'\]\([^)]*\)|<!--.*?-->|https?://\S+')
REGEX_CELL = re.compile(r'^/(.+)/\s*(\(.*\))?$')
FENCE_RE = re.compile(r'^\s*(`{3,}|~{3,})')


class ConfigError(Exception):
    pass


class Rule:
    def __init__(self, key, rx, term, use, level, source):
        self.key, self.rx, self.term, self.use, self.level, self.source = key, rx, term, use, level, source
        self.is_regex = key.startswith('re:')


def read_lines(path, what):
    try:
        with open(path, encoding='utf-8-sig') as f:
            return f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise ConfigError(f'cannot read {what}{path}: {getattr(e, "strerror", None) or e}')


def fenced(lines):
    """Set of line indexes inside code fences (fence lines included)."""
    out, fence = set(), None
    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if fence:
            out.add(i)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
        elif m:
            fence = m.group(1)
            out.add(i)
    return out


def split_cells(line):
    s = line.strip()
    if not s.startswith('|'):
        return None
    parts = CELL_SPLIT.split(s)[1:]
    if parts and parts[-1].strip() == '':
        parts = parts[:-1]
    return [p.strip().replace('\\|', '|') for p in parts]


def table_rows(path):
    """Yield (line_no, header, cells) for every data row of every markdown table."""
    lines = read_lines(path, 'vocabulary ')
    skip = fenced(lines)
    header = None
    for i, line in enumerate(lines):
        if i in skip:
            continue
        cells = split_cells(line)
        if cells is None:
            header = None
            continue
        if SEP_RE.match(line):
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        if SEP_RE.match(nxt):
            header = [h.lower() for h in cells]
            continue
        if header:
            yield i + 1, header, cells


def compile_term(term):
    """Return (key, regex, label) or None for an empty term."""
    m = REGEX_CELL.match(term)
    if m:
        try:
            return 're:' + m.group(1), re.compile(m.group(1)), m.group(2).strip('()') if m.group(2) else m.group(1)
        except re.error as e:
            raise ConfigError(f'bad regex /{m.group(1)}/: {e}')
    term = re.sub(r'\([^)]*\)', '', term).strip()
    if not term:
        return None
    words = term.split()
    pat = r'\s+'.join(r'\S+' if w == '…' else re.escape(w) for w in words)
    rx = re.compile(r'(?<![\w`<-])' + pat + r'(?![\w`>-])', re.I)
    return ' '.join(words).lower(), rx, term


def terms_of(cell):
    if REGEX_CELL.match(cell):
        return [cell]
    return [t for t in re.sub(r'\([^)]*\)', '', cell).split(',')]


def load_vocab(path, rules, allow, require_banned=False):
    banned_rows = 0
    for n, header, cells in table_rows(path):
        kind = header[0]
        where = f'{path}:{n}'
        if kind == 'banned':
            if 'use' not in header:
                raise ConfigError(f'{where}: Banned table has no Use column')
            row = dict(zip(header, cells + [''] * (len(header) - len(cells))))
            use, level = row.get('use', '').strip(), (row.get('level', '') or 'error').strip().lower()
            if not use:
                raise ConfigError(f'{where}: empty Use cell')
            if level not in LEVELS:
                raise ConfigError(f'{where}: Level must be error or warn, got "{level}"')
            banned_rows += 1
            for t in terms_of(cells[0]):
                c = compile_term(t.strip())
                if c:
                    key, rx, label = c
                    rules[key] = Rule(key, rx, label, use, level, path)
        elif kind == 'allow':
            for t in terms_of(cells[0]):
                c = compile_term(t.strip())
                if c:
                    allow.add(c[0])
    if require_banned and banned_rows == 0:
        raise ConfigError(f'{path}: no Banned table found')


def find_project(start):
    d = os.path.abspath(start)
    while True:
        p = os.path.join(d, PROJECT_REL)
        if os.path.isfile(p):
            return p
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def lint_page(path, rules):
    lines = read_lines(path, '')
    skip = fenced(lines)
    front_end = 0
    if lines and lines[0].strip() == '---':
        close = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
        if close is not None:
            front_end = close + 1
    hits = []
    for idx, line in enumerate(lines):
        n = idx + 1
        if idx < front_end or idx in skip or SEP_RE.match(line):
            continue
        nxt = lines[idx + 1] if idx + 1 < len(lines) else ''
        if line.lstrip().startswith('|') and SEP_RE.match(nxt):
            continue
        prose = QUOTED.sub(PLACEHOLDER, NOISE.sub(' ', line))
        found = []
        for r in rules:
            for m in r.rx.finditer(prose):
                txt = m.group(0).strip(' |')
                if not r.is_regex and txt.isupper() and len(txt) > 3:
                    continue
                found.append((m.start(), m.end(), txt, r))
        for s0, e0, txt, r in found:
            if any(s1 <= s0 and e0 <= e1 and (e1 - s1) > (e0 - s0) for s1, e1, _, _ in found):
                continue
            hits.append((n, txt, r))
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description='Vocabulary lint for AC and TC files.')
    ap.add_argument('files', nargs='+')
    ap.add_argument('--vocab', action='append', default=[], help='extra vocabulary file (repeatable)')
    ap.add_argument('--shared', default=SHARED_DEFAULT, help='shared vocabulary file')
    ap.add_argument('--no-project', action='store_true', help='do not load vocabulary.project.md')
    a = ap.parse_args(argv)
    try:
        cache = {}

        def active_rules(project):
            if project not in cache:
                rules, allow = {}, set()
                load_vocab(a.shared, rules, allow, require_banned=True)
                for p in ([project] if project else []) + a.vocab:
                    load_vocab(p, rules, allow)
                cache[project] = [r for k, r in rules.items() if k not in allow]
            return cache[project]

        errors = warns = 0
        for page in a.files:
            project = None if a.no_project else (
                find_project(os.path.dirname(os.path.abspath(page))) or find_project(os.getcwd()))
            for n, txt, r in sorted(lint_page(page, active_rules(project)), key=lambda h: h[0]):
                print(f'{page}:{n}: {r.level}: "{txt}" → {r.use}')
                if r.level == 'error':
                    errors += 1
                else:
                    warns += 1
    except ConfigError as e:
        print(f'lint: config error: {e}', file=sys.stderr)
        return 2
    print(f'lint: {errors} error(s), {warns} warning(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
