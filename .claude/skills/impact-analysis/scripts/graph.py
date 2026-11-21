#!/usr/bin/env python3
"""Business impact graph for the QA workspace (stdlib only).

Builds one graph per project from:
  qa/traceability/model.md   Features, Entities, Shared rules, Impact hubs, Screens
  qa/specs/*/ac.md           AC with optional bullets: Rules, Entities, Hubs
  qa/testcases/*/tc.md       TC with Covers AC and optional Screens

Usage (repo root):
  graph.py check  [--strict]                 broken links (exit 1) and warnings
  graph.py impact <ID> [<ID> …] [--depth N]   ranked AC/TC/feature/hub list for a change
  graph.py view   <ID> [--depth N] [--mermaid] local graph around one node
  graph.py matrix [--write | --check]        generate qa/traceability/matrix.md
Add --example to use the golden examples (folders named _example*).

<ID> is an AC, TC, RULE, HUB or SCR ID, a Feature Code, an entity name or a Jira key.
Exit codes: 0 clean · 1 findings · 2 usage or file error.
"""
import argparse
import glob
import os
import re
import sys
from collections import deque

CODE = r'[A-Z]{3,4}'
AC_H = re.compile(rf'^###\s+(AC-{CODE}-\d{{3}})\b\s*:?\s*(.*)$')
TC_H = re.compile(rf'^##\s+(TC-{CODE}-\d{{3}})\b\s*:?\s*(.*)$')
AC_ID = re.compile(rf'\bAC-{CODE}-\d{{3}}\b')
FEATURE_H = re.compile(r'^#\s+AC:\s*(.*?)\s*\((' + CODE + r')\)\s*$')
SEP_RE = re.compile(r'^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$')
ICONS = {'🔴': 4, '🟠': 3, '🟡': 2, '⚪': 1}
ICON_OF = {v: k for k, v in ICONS.items()}
NONE = {'', '—', '-', 'none', 'n/a'}
AUTO_RANK = {'done': 3, 'candidate': 2, 'not yet': 1}
AUTO_NAME = {3: 'Done', 2: 'Candidate', 1: 'Not yet'}
MAX_ENTITIES = 5
KIND_ORDER = {'AC': 0, 'TC': 1, 'Feature': 2, 'Hub': 3, 'Entity': 4}
MATRIX = 'qa/traceability/matrix.md'


class FormatError(Exception):
    pass


# ---------- parsing helpers ----------

def read(path):
    try:
        with open(path, encoding='utf-8-sig') as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise FormatError(f'cannot read {path}: {getattr(e, "strerror", None) or e}')
    out, fence = [], None
    for line in lines:  # blank out fenced code
        m = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            out.append('')
            continue
        if m:
            fence = m.group(1)
            out.append('')
            continue
        out.append(line)
    return out


def cells(line):
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'):
        s = s[:-1]
    parts, buf, in_code = [], '', False
    for ch in s:
        if ch == '`':
            in_code = not in_code
        if ch == '|' and not in_code:
            parts.append(buf.strip())
            buf = ''
        else:
            buf += ch
    parts.append(buf.strip())
    return parts


def tables(lines, start, stop):
    i = start
    while i < stop:
        if lines[i].lstrip().startswith('|') and i + 1 < stop and SEP_RE.match(lines[i + 1]):
            header = [h.strip('* ').lower() for h in cells(lines[i])]
            rows, j = [], i + 2
            while j < stop and lines[j].lstrip().startswith('|'):
                r = cells(lines[j])
                rows.append(dict(zip(header, r + [''] * (len(header) - len(r)))))
                j += 1
            yield header, rows
            i = j
            continue
        i += 1


def section(lines, title):
    for i, l in enumerate(lines):
        if re.match(rf'^##\s+{re.escape(title)}\s*$', l, re.I):
            end = next((j for j in range(i + 1, len(lines)) if re.match(r'^#{1,2}\s', lines[j])), len(lines))
            return i, end
    return None


def first_table(lines, title):
    span = section(lines, title)
    if not span:
        return []
    for _, rows in tables(lines, *span):
        return [r for r in rows if any(v.strip() for v in r.values())]
    return []


def items(text):
    return [x.strip().strip('`*').strip() for x in re.split(r'[,;]', text or '')
            if x.strip().strip('`*').strip().lower() not in NONE]


def level(text):
    for icon, v in ICONS.items():
        if icon in (text or ''):
            return v
    return 0


def bullet(lines, start, end, name):
    rx = re.compile(rf'^\s*-\s*\**{name}\**\s*:\s*(.*?)\s*$', re.I)
    for i in range(start, end):
        m = rx.match(lines[i])
        if m:
            return m.group(1)
    return None


def inactive(text):
    return (text or '').strip('` *').lower().startswith('deprecated')


# ---------- model ----------

class Graph:
    def __init__(self):
        self.features = {}   # code -> {module, depends, owner, name}
        self.entities = {}   # name -> {meaning, broad}
        self.rules = {}      # id -> {text, crit, hubs, inactive}
        self.hubs = {}       # id -> {when, checklist}
        self.screens = {}    # id -> {name, path, roles}
        self.acs = {}        # id -> {feature, title, crit, inactive, rules, entities, hubs, linked, jira, file}
        self.tcs = {}        # id -> {covers, screens, crit, status, automation, file, has_screens}
        self.errors = []
        self.dups = []

    # reverse indexes
    def acs_with(self, key, value):
        return sorted(a for a, d in self.acs.items() if value in d[key] and not d['inactive'])

    def tcs_of(self, ac):
        return sorted(t for t, d in self.tcs.items() if ac in d['covers'] and d['status'] != 'deprecated')

    def tcs_on(self, scr):
        return sorted(t for t, d in self.tcs.items() if scr in d['screens'] and d['status'] != 'deprecated')

    def feature_of(self, ac):
        return self.acs[ac]['feature']


def load(root, example=False):
    g = Graph()
    model = os.path.join(root, 'qa/traceability/_example/model.md' if example else 'qa/traceability/model.md')
    lines = read(model)
    for r in first_table(lines, 'Features'):
        code = r.get('code', '').strip('` ')
        if code:
            g.features[code] = {'module': r.get('module', ''), 'depends': items(r.get('depends on')),
                                'owner': r.get('owner', ''), 'name': ''}
    for r in first_table(lines, 'Entities'):
        name = r.get('entity', '').strip('` ')
        if name:
            g.entities[name] = {'meaning': r.get('meaning', ''), 'owner': r.get('owner', '').strip('` '),
                                'broad': r.get('scope', '').strip('` ').lower() == 'broad'}
    for r in first_table(lines, 'Shared rules'):
        rid = r.get('rule id', '').strip('` ')
        if rid:
            g.rules[rid] = {'text': r.get('rule', ''), 'crit': level(r.get('criticality')),
                            'hubs': items(r.get('hubs')), 'inactive': inactive(r.get('status'))}
    for r in first_table(lines, 'Impact hubs'):
        hid = r.get('hub id', '').strip('` ')
        if hid:
            g.hubs[hid] = {'when': r.get('applies when', ''), 'checklist': r.get('checklist', '')}
    for r in first_table(lines, 'Screens'):
        sid = r.get('screen id', '').strip('` ')
        if sid:
            g.screens[sid] = {'name': r.get('name', ''), 'path': r.get('path', ''), 'roles': r.get('roles', '')}

    def wanted(path):
        folder = os.path.basename(os.path.dirname(path))
        return folder.startswith('_example') if example else not folder.startswith('_')

    for path in sorted(glob.glob(os.path.join(root, 'qa/specs/*/ac.md'))):
        if wanted(path):
            parse_ac(g, path, root)
    for path in sorted(glob.glob(os.path.join(root, 'qa/testcases/*/tc.md'))):
        if wanted(path):
            parse_tc(g, path, root)
    return g


def parse_ac(g, path, root):
    lines = read(path)
    rel = os.path.relpath(path, root)
    jira, fname = '', ''
    for l in lines:
        m = FEATURE_H.match(l)
        if m:
            fname = m.group(1)
            break
    for _, rows in tables(lines, 0, len(lines)):
        for r in rows:
            if r.get('field', '').strip('* ').lower() == 'jira':
                jira = r.get('value', '').strip('` ')
        break
    heads = [(i, m) for i, l in enumerate(lines) for m in [AC_H.match(l)] if m]
    for k, (i, m) in enumerate(heads):
        end = next((j for j in range(i + 1, len(lines)) if re.match(r'^#{1,3}\s', lines[j])), len(lines))
        aid = m.group(1)
        if aid in g.acs:
            g.dups.append(f'{rel}: duplicate {aid}')
        raw = {n: bullet(lines, i, end, n) for n in ('Rules', 'Entities', 'Hubs')}
        code = aid.split('-')[1]
        if code in g.features and fname:
            g.features[code]['name'] = fname
        g.acs[aid] = {
            'feature': code, 'title': m.group(2).strip(), 'file': rel, 'jira': jira,
            'crit': level(bullet(lines, i, end, 'Criticality')),
            'inactive': inactive(bullet(lines, i, end, 'Status')),
            'rules': set(items(raw['Rules'])), 'entities': set(items(raw['Entities'])),
            'hubs': set(items(raw['Hubs'])), 'linked': any(v is not None for v in raw.values()),
        }


def parse_tc(g, path, root):
    lines = read(path)
    rel = os.path.relpath(path, root)
    heads = [(i, m) for i, l in enumerate(lines) for m in [TC_H.match(l)] if m]
    for i, m in heads:
        end = next((j for j in range(i + 1, len(lines)) if re.match(r'^#{1,2}\s', lines[j])), len(lines))
        tid = m.group(1)
        if tid in g.tcs:
            g.dups.append(f'{rel}: duplicate {tid}')
        fields = {}
        for header, rows in tables(lines, i, end):
            if header[:2] == ['field', 'value']:
                fields = {r['field'].strip('* ').lower(): r.get('value', '') for r in rows}
                break
        g.tcs[tid] = {
            'covers': set(AC_ID.findall(fields.get('covers ac', ''))),
            'screens': set(items(fields.get('screens'))), 'has_screens': 'screens' in fields,
            'crit': level(fields.get('priority')),
            'status': fields.get('status', '').strip('` ').lower(),
            'automation': fields.get('automation', '').strip('` ').lower(), 'file': rel,
        }


# ---------- check ----------

def check(g):
    errors, warnings = list(g.dups), []
    for aid, a in sorted(g.acs.items()):
        where = f'{a["file"]}: {aid}'
        if a['feature'] not in g.features:
            errors.append(f'{where}: feature {a["feature"]} is not in model.md › Features')
        for r in sorted(a['rules']):
            if r not in g.rules:
                errors.append(f'{where}: unknown rule {r}')
            elif g.rules[r]['inactive'] and not a['inactive']:
                errors.append(f'{where}: uses deprecated rule {r}')
        for e in sorted(a['entities']):
            if e not in g.entities:
                errors.append(f'{where}: unknown entity {e}')
        for h in sorted(a['hubs']):
            if h not in g.hubs:
                errors.append(f'{where}: unknown hub {h}')
        if a['inactive']:
            continue
        if not a['linked']:
            warnings.append(f'{where}: no Rules, Entities or Hubs line (cross-feature impact unknown)')
        if len(a['entities']) > MAX_ENTITIES:
            warnings.append(f'{where}: {len(a["entities"])} entities (max {MAX_ENTITIES}); link only what the AC changes or reads')
    for tid, t in sorted(g.tcs.items()):
        where = f'{t["file"]}: {tid}'
        for a in sorted(t['covers']):
            if a not in g.acs:
                errors.append(f'{where}: covers unknown {a}')
        for s in sorted(t['screens']):
            if s not in g.screens:
                errors.append(f'{where}: unknown screen {s}')
        if t['status'] != 'deprecated' and not t['has_screens']:
            warnings.append(f'{where}: no Screens row')
    for code, f in sorted(g.features.items()):
        for d in f['depends']:
            if d not in g.features:
                errors.append(f'model.md: {code} depends on unknown feature {d}')
    for rid, r in sorted(g.rules.items()):
        for h in r['hubs']:
            if h not in g.hubs:
                errors.append(f'model.md: {rid} names unknown hub {h}')
        feats = {g.feature_of(a) for a in g.acs_with('rules', rid)}
        if not r['inactive'] and len(feats) < 2:
            warnings.append(f'model.md: {rid} is used by {len(feats)} feature(s); a shared rule needs 2+')
    for name, e in sorted(g.entities.items()):
        if not g.acs_with('entities', name):
            warnings.append(f'model.md: entity {name} is used by no AC')
        if e['owner'].lower() in NONE:
            if not e['broad']:
                warnings.append(f'model.md: entity {name} has no Owner; every AC that uses it spreads impact')
        elif e['owner'] not in g.features:
            errors.append(f'model.md: entity {name} owner {e["owner"]} is not a feature')
    cycle = find_cycle(g)
    if cycle:
        warnings.append('model.md: dependency cycle ' + ' → '.join(cycle))
    return errors, warnings


def find_cycle(g):
    state = {}

    def visit(n, path):
        state[n] = 1
        for d in g.features.get(n, {}).get('depends', []):
            if state.get(d) == 1:
                return path[path.index(d):] + [d] if d in path else [n, d]
            if d in g.features and not state.get(d):
                c = visit(d, path + [d])
                if c:
                    return c
        state[n] = 2
        return None

    for n in sorted(g.features):
        if not state.get(n):
            c = visit(n, [n])
            if c:
                return c
    return None


# ---------- impact ----------

def resolve(g, token):
    """Return (kind, seed ACs at distance 0, direct rows)."""
    t = token.strip()
    if t in g.acs:
        return 'AC', [t]
    if t in g.tcs:
        return 'TC', []
    if t in g.rules:
        return 'Rule', g.acs_with('rules', t)
    if t in g.hubs:
        return 'Hub', []
    if t in g.screens:
        return 'Screen', sorted({a for tc in g.tcs_on(t) for a in g.tcs[tc]['covers'] if a in g.acs})
    if t in g.features:
        return 'Feature', sorted(a for a, d in g.acs.items() if d['feature'] == t and not d['inactive'])
    if t in g.entities:
        return 'Entity', g.acs_with('entities', t)
    jira = sorted(a for a, d in g.acs.items() if d['jira'] == t and not d['inactive'])
    if jira:
        return 'Jira', jira
    raise FormatError(f'unknown ID "{token}": not an AC, TC, rule, hub, screen, feature, entity or Jira key')


def impact(g, tokens, depth=1):
    """Propagation rules:
    - A changed AC (or Jira key, or feature) reaches other features' AC through its shared rules and through
      Normal entities its feature owns. A reader's change does not reach the owner or other readers.
    - A changed rule or entity reaches the AC that use it; one more hop needs --depth 2.
    - A changed screen reaches its TC and their AC only (UI change, no business propagation).
    - Propagation never enters the changed features again and never goes through a Broad entity or a hub.
    - Hubs of every listed AC and its rules are listed with their checklist.
    - Features that depend on a changed feature get a regression row.
    """
    rows = {}
    broad, gaps = {}, []

    def add(kind, nid, dist, via, crit, action):
        key = (kind, nid)
        if key not in rows or dist < rows[key]['dist']:
            rows[key] = {'kind': kind, 'id': nid, 'dist': dist, 'via': via, 'crit': crit, 'action': action}

    dist, via, budget = {}, {}, {}
    queue = deque()
    changed = set()
    for tok in tokens:
        kind, seeds = resolve(g, tok)
        tok = tok.strip()
        if kind == 'TC':
            add('TC', tok, 0, 'changed', g.tcs[tok]['crit'], 'Update and re-run')
        if kind == 'Hub':
            add('Hub', tok, 0, 'changed', 0, 'Re-check every AC in the hub: ' + ', '.join(g.acs_with('hubs', tok)))
        if kind == 'Entity' and g.entities[tok]['broad']:
            broad.setdefault(tok, set()).add('changed')
        if kind == 'Screen':
            for tc in g.tcs_on(tok):
                add('TC', tc, 0, tok, g.tcs[tc]['crit'], 'Re-run (screen changed)')
        hops = {'AC': depth, 'Jira': depth, 'Feature': depth, 'Rule': depth - 1, 'Entity': depth - 1}.get(kind, 0)
        for a in seeds:
            if a not in dist:
                dist[a], via[a], budget[a] = 0, ('changed' if kind in ('AC', 'Jira', 'Feature') else tok), hops
                queue.append(a)
                if kind in ('AC', 'Jira', 'Feature'):
                    changed.add(a)
    seed_features = {g.feature_of(a) for a in dist}
    while queue:
        a = queue.popleft()
        ac = g.acs[a]
        hubs = set(ac['hubs']) | {h for r in ac['rules'] if r in g.rules for h in g.rules[r]['hubs']}
        for h in sorted(hubs):
            if h in g.hubs:
                add('Hub', h, dist[a], a, 0, 'Run checklist: ' + g.hubs[h]['checklist'])
        if budget[a] <= 0:
            continue
        links = [(r, 'rules') for r in sorted(ac['rules']) if r in g.rules and not g.rules[r]['inactive']]
        for e in sorted(ac['entities']):
            if e not in g.entities:
                continue
            if g.entities[e]['broad']:
                broad.setdefault(e, set()).add(a)
                continue
            owner = g.entities[e]['owner']
            if owner.lower() in NONE or owner == ac['feature']:
                links.append((e, 'entities'))  # the owner changed it: readers are impacted
        for node, key in links:
            for other in g.acs_with(key, node):
                if other in dist or g.feature_of(other) in seed_features or g.feature_of(other) == ac['feature']:
                    continue
                dist[other], via[other], budget[other] = dist[a] + 1, node, budget[a] - 1
                queue.append(other)
    for a, d in dist.items():
        ac = g.acs[a]
        is_changed = a in changed
        add('AC', a, d, via[a], ac['crit'], 'Update' if is_changed else 'Re-check')
        tcs = g.tcs_of(a)
        for tc in tcs:
            add('TC', tc, d, a, g.tcs[tc]['crit'], 'Update and re-run' if is_changed else 'Re-run')
        if not tcs:
            gaps.append(f'{a}: no TC')
        if not ac['linked']:
            gaps.append(f'{a}: no Rules, Entities or Hubs line; cross-feature impact unknown')
    hit = {g.feature_of(a) for a in changed}
    touched = {g.feature_of(a) for a in dist}
    for code, f in sorted(g.features.items()):
        for dep in f['depends']:
            if dep in hit and code not in touched:
                add('Feature', code, 1, dep, 0, f'Regression check (depends on {dep})')
    notes = [f'{e} (Broad) used by {", ".join(sorted(x for x in src if x != "changed")) or "the change"}; '
             'review by hand' for e, src in sorted(broad.items())]
    ordered = sorted(rows.values(), key=lambda r: (r['dist'], KIND_ORDER[r['kind']], -r['crit'], r['id']))
    return ordered, notes, sorted(set(gaps))


def render_impact(rows, notes, gaps):
    out = ['| Item | ID | Distance | Via | Criticality | Action |', '| --- | --- | --- | --- | --- | --- |']
    for r in rows:
        out.append(f'| {r["kind"]} | {r["id"]} | {r["dist"]} | {r["via"]} | '
                   f'{ICON_OF.get(r["crit"], "—")} | {r["action"]} |')
    counts = {}
    for r in rows:
        counts[r['kind']] = counts.get(r['kind'], 0) + 1
    out.append('')
    out.append('- Total: ' + ' · '.join(f'{v} {k}' for k, v in sorted(counts.items(), key=lambda x: KIND_ORDER[x[0]])))
    for n in notes:
        out.append(f'- Not expanded: {n}')
    for gp in gaps:
        out.append(f'- Gap: {gp}')
    return '\n'.join(out)


# ---------- view ----------

def neighbours(g, n):
    """[(edge, node)] for one node, both directions."""
    out = []
    if n in g.acs:
        a = g.acs[n]
        out.append(('in feature', a['feature']))
        out += [('shares_rule', r) for r in sorted(a['rules'])]
        out += [('uses_entity', e) for e in sorted(a['entities'])]
        out += [('in_hub', h) for h in sorted(a['hubs'])]
        out += [('validated_by', t) for t in g.tcs_of(n)]
    elif n in g.tcs:
        out += [('validates', a) for a in sorted(g.tcs[n]['covers'])]
        out += [('realized_in', s) for s in sorted(g.tcs[n]['screens'])]
    elif n in g.rules:
        out += [('used_by', a) for a in g.acs_with('rules', n)]
        out += [('in_hub', h) for h in g.rules[n]['hubs']]
    elif n in g.hubs:
        out += [('contains', a) for a in g.acs_with('hubs', n)]
        out += [('contains', r) for r, d in sorted(g.rules.items()) if n in d['hubs']]
    elif n in g.screens:
        out += [('shows', t) for t in g.tcs_on(n)]
    elif n in g.features:
        out += [('depends_on', d) for d in g.features[n]['depends']]
        out += [('needed_by', c) for c, f in sorted(g.features.items()) if n in f['depends']]
        out += [('has', a) for a, d in sorted(g.acs.items()) if d['feature'] == n and not d['inactive']]
    elif n in g.entities:
        out += [('used_by', a) for a in g.acs_with('entities', n)]
    else:
        raise FormatError(f'unknown ID "{n}"')
    return out


def kind_of(g, n):
    for kind, store in (('AC', g.acs), ('TC', g.tcs), ('Rule', g.rules), ('Hub', g.hubs),
                        ('Screen', g.screens), ('Feature', g.features), ('Entity', g.entities)):
        if n in store:
            return kind
    return '?'


def view(g, start, depth=1, mermaid=False):
    seen, edges, queue = {start: 0}, [], deque([start])
    while queue:
        n = queue.popleft()
        if seen[n] >= depth:
            continue
        for e, m in neighbours(g, n):
            edges.append((n, e, m))
            if m not in seen and kind_of(g, m) != '?':
                seen[m] = seen[n] + 1
                queue.append(m)
    if mermaid:
        safe = lambda x: re.sub(r'\W', '_', x)
        out = ['```mermaid', 'graph LR']
        for n in seen:
            out.append(f'  {safe(n)}["{kind_of(g, n)}: {n}"]')
        for a, e, b in dict.fromkeys(edges):
            out.append(f'  {safe(a)} -->|{e}| {safe(b)}')
        out.append('```')
        return '\n'.join(out)
    out = ['| From | Edge | To | Kind |', '| --- | --- | --- | --- |']
    for a, e, b in dict.fromkeys(edges):
        out.append(f'| {a} | {e} | {b} | {kind_of(g, b)} |')
    return '\n'.join(out)


# ---------- matrix ----------

MATRIX_HEAD = """# Traceability matrix

Generated by `graph.py matrix --write`. Do not edit rows by hand; edit `ac.md`, `tc.md` or `model.md` and regenerate.
Only `Auto script` is kept from the previous file.

| Column | Rule |
| --- | --- |
| Ticket | Jira key of the AC |
| Feature | Feature Code |
| AC | One AC ID |
| Criticality | Criticality of the AC (🔴 🟠 🟡 ⚪) |
| TC | Every TC ID that lists this AC in `Covers AC`, comma-separated. Blocked TCs end with `(Blocked)` |
| Screens | Screens of those TCs |
| Links | Shared rules, entities and hubs of the AC |
| Automation | Most advanced state among the TCs: Not yet · Candidate · Done |
| Auto script | Script path. Empty until automation exists |

- Deprecated AC: `(Deprecated)` after the ID.
- AC with no TC yet: TC cell `—`.
- Rows from `_example` are never added here.
"""


def old_scripts(path):
    scripts = {}
    if os.path.exists(path):
        lines = read(path)
        for _, rows in tables(lines, 0, len(lines)):
            for r in rows:
                ids = AC_ID.findall(r.get('ac', ''))
                if ids and r.get('auto script', '').strip():
                    scripts[ids[0]] = r['auto script'].strip()
    return scripts


def matrix(g, previous=None):
    scripts = old_scripts(previous) if previous else {}
    out = [MATRIX_HEAD, '## Rows', '',
           '| Ticket | Feature | AC | Criticality | TC | Screens | Links | Automation | Auto script |',
           '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for aid, a in sorted(g.acs.items()):
        tcs = [t for t in sorted(g.tcs) if aid in g.tcs[t]['covers'] and g.tcs[t]['status'] != 'deprecated']
        tc_cell = ', '.join(t + (' (Blocked)' if g.tcs[t]['status'] == 'blocked' else '') for t in tcs) or '—'
        screens = sorted({s for t in tcs for s in g.tcs[t]['screens']})
        links = sorted(a['rules']) + sorted(a['entities']) + sorted(a['hubs'])
        auto = max((AUTO_RANK.get(g.tcs[t]['automation'], 0) for t in tcs), default=0)
        out.append(f'| {a["jira"] or "—"} | {a["feature"]} | {aid}{" (Deprecated)" if a["inactive"] else ""} | '
                   f'{ICON_OF.get(a["crit"], "—")} | {tc_cell} | {", ".join(screens) or "—"} | '
                   f'{", ".join(links) or "—"} | {AUTO_NAME.get(auto, "—")} | {scripts.get(aid, "")} |')
    out += ['', '## Feature links', '',
            '| Feature | Depends on | Needed by | Shares rules or entities with |',
            '| --- | --- | --- | --- |']
    for code, f in sorted(g.features.items()):
        needed = sorted(c for c, x in g.features.items() if code in x['depends'])
        mine = [a for a, d in g.acs.items() if d['feature'] == code and not d['inactive']]
        shared = set()
        for a in mine:
            for r in g.acs[a]['rules']:
                shared |= {g.feature_of(o) for o in g.acs_with('rules', r)}
            for e in g.acs[a]['entities']:
                if e in g.entities and not g.entities[e]['broad']:
                    shared |= {g.feature_of(o) for o in g.acs_with('entities', e)}
        shared.discard(code)
        out.append(f'| {code} | {", ".join(f["depends"]) or "—"} | {", ".join(needed) or "—"} | '
                   f'{", ".join(sorted(shared)) or "—"} |')
    return '\n'.join(out) + '\n'


# ---------- CLI ----------

def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, '.claude/rules/project.md')):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def main(argv=None):
    ap = argparse.ArgumentParser(description='Business impact graph: check, impact, view, matrix.')
    ap.add_argument('--root', default='.')
    ap.add_argument('--example', action='store_true', help='use the _example folders and _example/model.md')
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check')
    c.add_argument('--strict', action='store_true', help='warnings fail too')
    i = sub.add_parser('impact')
    i.add_argument('ids', nargs='+')
    i.add_argument('--depth', type=int, default=1)
    v = sub.add_parser('view')
    v.add_argument('id')
    v.add_argument('--depth', type=int, default=1)
    v.add_argument('--mermaid', action='store_true')
    m = sub.add_parser('matrix')
    m.add_argument('--write', action='store_true')
    m.add_argument('--check', action='store_true')
    a = ap.parse_args(argv)
    root = find_root(a.root)
    if not root:
        print('graph: not inside the repo (no .claude/rules/project.md)', file=sys.stderr)
        return 2
    try:
        g = load(root, a.example)
        if a.cmd == 'check':
            errors, warnings = check(g)
            for e in errors:
                print(f'graph: error: {e}')
            for w in warnings:
                print(f'graph: warning: {w}')
            print(f'graph: {len(errors)} error(s), {len(warnings)} warning(s), '
                  f'{len(g.acs)} AC, {len(g.tcs)} TC, {len(g.features)} feature(s)')
            return 1 if errors or (a.strict and warnings) else 0
        if a.cmd == 'impact':
            rows, notes, gaps = impact(g, a.ids, a.depth)
            print(render_impact(rows, notes, gaps))
            return 0
        if a.cmd == 'view':
            print(view(g, a.id, a.depth, a.mermaid))
            return 0
        if a.cmd == 'matrix':
            path = os.path.join(root, MATRIX)
            text = matrix(g, path)
            if a.write:
                if a.example:
                    print('graph: --write is not allowed with --example', file=sys.stderr)
                    return 2
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f'graph: wrote {MATRIX} ({len(g.acs)} AC)')
                return 0
            if a.check:
                current = ''
                if os.path.exists(path):
                    with open(path, encoding='utf-8-sig') as f:
                        current = f.read()
                if current != text:
                    print(f'graph: {MATRIX} is out of date; run graph.py matrix --write')
                    return 1
                print(f'graph: {MATRIX} is up to date')
                return 0
            print(text, end='')
            return 0
    except FormatError as e:
        print(f'graph: {e}', file=sys.stderr)
        return 2
    return 2


if __name__ == '__main__':
    sys.exit(main())
