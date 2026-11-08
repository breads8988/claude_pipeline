#!/usr/bin/env python3
"""Coverage validator: every coverage item in ac.md is exercised by a TC in tc.md.

Usage:
  python3 coverage.py qa/specs/<feature>/ac.md qa/testcases/<feature>/tc.md [--summary]

Checks (each failure is an error):
  - Every active AC is covered by at least one active or blocked TC.
  - Every business rule (BR) appears in a TC's coverage items.
  - Every decision table column (DT-…R<n>) is covered.
  - Every valid transition (ST-…T<n>) is covered; invalid transitions too when the model is 🔴.
  - Every field (FLD) has an EP valid and an EP invalid item, and enough BVA items:
    boundaries × 2 (2-value) or × 3 (3-value for 🔴).
  - Every ID a TC cites exists in ac.md.
  - TC priority = highest criticality among its covered items.
  - A blocked TC names an open question that exists and is still open.

Not checked here (tc-reviewer does it): correctness of partitions and boundary values,
Likelihood: High depth raise, wording.

--summary prints the Coverage summary table for the tc.md header.
Exit codes: 0 full coverage · 1 errors found · 2 usage, file or format error.
"""
import argparse
import re
import sys

ICONS = {'🔴': 4, '🟠': 3, '🟡': 2, '⚪': 1}
WORDS = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
ICON_OF = {v: k for k, v in ICONS.items()}
CODE = r'[A-Z]{3,4}'
SEP_RE = re.compile(r'^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$')
AC_H = re.compile(rf'^###\s+(AC-{CODE}-\d{{3}})\b')
DT_H = re.compile(rf'^###\s+(DT-{CODE}-\d{{2}})\b')
ST_H = re.compile(rf'^###\s+(ST-{CODE}-\d{{2}})\b')
TC_H = re.compile(rf'^##\s+(TC-{CODE}-\d{{3}})\b')
ITEM_ID = re.compile(rf'\b((?:AC|BR)-{CODE}-\d{{3}}|(?:DT|ST)-{CODE}-\d{{2}}\.[RT]\d+|FLD-{CODE}-\d{{2}})\b')
FLD_ITEM = re.compile(rf'(FLD-{CODE}-\d{{2}})\s+(EP|BVA)\s*:\s*([^`,;]+)')


class FormatError(Exception):
    pass


def read(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read().splitlines()
    except OSError as e:
        raise FormatError(f'cannot read {path}: {e.strerror}')


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def level(text):
    t = text.strip()
    for icon, v in ICONS.items():
        if icon in t:
            return v
    for w, v in WORDS.items():
        if t.lower().startswith(w):
            return v
    return 0


def tables_after(lines, start, stop):
    """Yield (header, rows) for tables between line indexes start and stop."""
    i = start
    while i < stop:
        if lines[i].lstrip().startswith('|') and i + 1 < stop and SEP_RE.match(lines[i + 1]):
            header = cells(lines[i])
            rows, j = [], i + 2
            while j < stop and lines[j].lstrip().startswith('|'):
                rows.append(cells(lines[j]))
                j += 1
            yield header, rows
            i = j
            continue
        i += 1


def sections(lines, rx):
    """Return [(id, start, end)] for headings matching rx; a section ends at the next heading of level ≤ 3."""
    found = []
    for i, line in enumerate(lines):
        m = rx.match(line)
        if m:
            found.append((m.group(1), i))
    out = []
    for k, (sid, start) in enumerate(found):
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if re.match(r'^#{1,3}\s', lines[j]):
                end = j
                break
        out.append((sid, start, end))
    return out


def bullet(lines, start, end, name):
    rx = re.compile(rf'^\s*-\s*{name}\s*:\s*(.+)$', re.I)
    for i in range(start, end):
        m = rx.match(lines[i])
        if m:
            return m.group(1).strip()
    return ''


def parse_ac(path):
    lines = read(path)
    ac = {}
    for sid, s, e in sections(lines, AC_H):
        status = bullet(lines, s, e, 'Status')
        ac[sid] = {'crit': level(bullet(lines, s, e, 'Criticality')),
                   'active': not status.lower().startswith('deprecated')}
    if not ac:
        raise FormatError(f'{path}: no AC sections (### AC-<CODE>-NNN)')
    br, fld, oq = {}, {}, {}
    for header, rows in tables_after(lines, 0, len(lines)):
        h = [x.lower() for x in header]
        for r in rows:
            row = dict(zip(h, r + [''] * (len(h) - len(r))))
            first = r[0] if r else ''
            if re.fullmatch(rf'BR-{CODE}-\d{{3}}', first):
                br[first] = level(row.get('criticality', ''))
            elif re.fullmatch(rf'FLD-{CODE}-\d{{2}}', first):
                bounds = sum(1 for k in ('min', 'max') if re.search(r'\d', row.get(k, '')))
                fld[first] = {'crit': level(row.get('criticality', '')), 'bounds': bounds}
            elif re.fullmatch(rf'OQ-{CODE}-\d{{3}}', first):
                oq[first] = row.get('status', '').strip().lower()
    dt, st = {}, {}
    for sid, s, e in sections(lines, DT_H):
        crit = level(bullet(lines, s, e, 'Criticality'))
        for header, _ in tables_after(lines, s, e):
            for col in header[1:]:
                if re.fullmatch(r'R\d+', col):
                    dt[f'{sid}.{col}'] = crit
            break
    for sid, s, e in sections(lines, ST_H):
        crit = level(bullet(lines, s, e, 'Criticality'))
        for header, rows in tables_after(lines, s, e):
            h = [x.lower() for x in header]
            for r in rows:
                row = dict(zip(h, r))
                t = row.get('t', '')
                if re.fullmatch(r'T\d+', t):
                    valid = row.get('valid', 'yes').strip().lower().startswith('y')
                    st[f'{sid}.{t}'] = {'crit': crit, 'valid': valid}
            break
    return {'ac': ac, 'br': br, 'fld': fld, 'dt': dt, 'st': st, 'oq': oq}


def parse_tc(path):
    lines = read(path)
    tcs = {}
    for sid, s, e in sections(lines, TC_H):
        fields = {}
        for header, rows in tables_after(lines, s, e):
            if [x.lower() for x in header[:2]] == ['field', 'value']:
                fields = {r[0].lower(): (r[1] if len(r) > 1 else '') for r in rows}
            break
        items_cell = fields.get('coverage items', '')
        tcs[sid] = {
            'covers': set(re.findall(rf'AC-{CODE}-\d{{3}}', fields.get('covers ac', ''))),
            'ids': set(ITEM_ID.findall(items_cell)) | set(re.findall(rf'AC-{CODE}-\d{{3}}', fields.get('covers ac', ''))),
            'fld': [(m.group(1), m.group(2).upper(), m.group(3).strip().lower()) for m in FLD_ITEM.finditer(items_cell)],
            'priority': level(fields.get('priority', '')),
            'status': fields.get('status', '').strip('` ').lower(),
            'blocked_by': fields.get('blocked by', '').strip(),
        }
    if not tcs:
        raise FormatError(f'{path}: no TC sections (## TC-<CODE>-NNN)')
    return tcs


def check(spec, tcs):
    errors = []
    live = {k: v for k, v in tcs.items() if not v['status'].startswith('deprecated')}
    cited = set().union(*[t['ids'] for t in live.values()]) if live else set()
    known = set(spec['ac']) | set(spec['br']) | set(spec['dt']) | set(spec['st']) | set(spec['fld'])
    summary = {}

    def tally(name, items, covered):
        summary[name] = (len(items), len([i for i in items if i in covered]))

    act = [a for a, v in spec['ac'].items() if v['active']]
    tally('Scenario (AC)', act, cited)
    errors += [f'{a}: no TC covers this AC' for a in act if a not in cited]
    tally('Business rules', list(spec['br']), cited)
    errors += [f'{b}: no TC covers this business rule' for b in spec['br'] if b not in cited]
    tally('Decision table', list(spec['dt']), cited)
    errors += [f'{d}: decision table column not covered' for d in spec['dt'] if d not in cited]
    need_st = [t for t, v in spec['st'].items() if v['valid'] or v['crit'] == 4]
    tally('State transition', need_st, cited)
    for t in need_st:
        if t not in cited:
            kind = 'valid' if spec['st'][t]['valid'] else 'invalid (required for 🔴)'
            errors.append(f'{t}: {kind} transition not covered')

    ep_items, ep_cov, bva_items, bva_cov = 0, 0, 0, 0
    for f, v in spec['fld'].items():
        labels = [(tech, lab) for t in live.values() for (fid, tech, lab) in t['fld'] if fid == f]
        ep = {lab for tech, lab in labels if tech == 'EP'}
        has_valid = any(l.startswith('valid') for l in ep)
        has_invalid = any(l.startswith('invalid') for l in ep)
        ep_items += 2
        ep_cov += int(has_valid) + int(has_invalid)
        if not has_valid:
            errors.append(f'{f}: no EP valid partition covered')
        if not has_invalid:
            errors.append(f'{f}: no EP invalid partition covered')
        need = v['bounds'] * (3 if v['crit'] == 4 else 2)
        got = len({lab for tech, lab in labels if tech == 'BVA'})
        bva_items += need
        bva_cov += min(got, need)
        if got < need:
            depth = '3-value' if v['crit'] == 4 else '2-value'
            errors.append(f'{f}: {got}/{need} BVA values ({depth}, {v["bounds"]} boundaries)')
    summary['EP'] = (ep_items, ep_cov)
    summary['BVA'] = (bva_items, bva_cov)

    for tid, t in sorted(tcs.items()):
        for i in sorted(t['ids'] - known):
            errors.append(f'{tid}: cites {i}, which is not in ac.md')
        crits = [spec['ac'].get(i, {}).get('crit', 0) if i.startswith('AC-') else
                 spec['br'].get(i, 0) if i.startswith('BR-') else
                 spec['dt'].get(i, 0) if i.startswith('DT-') else
                 spec['st'].get(i, {}).get('crit', 0) if i.startswith('ST-') else
                 spec['fld'].get(i, {}).get('crit', 0) for i in t['ids']]
        top = max(crits, default=0)
        if top and t['priority'] != top:
            have = ICON_OF.get(t['priority'], 'none')
            errors.append(f'{tid}: priority {have} should be {ICON_OF[top]} (highest covered item)')
        if t['status'].startswith('blocked'):
            oq = re.search(rf'OQ-{CODE}-\d{{3}}', t['blocked_by'])
            if not oq:
                errors.append(f'{tid}: blocked without an open question in Blocked by')
            elif oq.group(0) not in spec['oq']:
                errors.append(f'{tid}: Blocked by {oq.group(0)}, which is not in ac.md')
            elif spec['oq'][oq.group(0)] != 'open':
                errors.append(f'{tid}: {oq.group(0)} is {spec["oq"][oq.group(0)]}; unblock this TC')
    return errors, summary


def summary_table(summary):
    rows = ['| Technique | Items identified | Covered | Coverage |', '| --- | --- | --- | --- |']
    for name in ('Scenario (AC)', 'Business rules', 'EP', 'BVA', 'Decision table', 'State transition'):
        total, cov = summary.get(name, (0, 0))
        pct = f'{round(100 * cov / total)}%' if total else '—'
        rows.append(f'| {name} | {total} | {cov} | {pct} |')
    return '\n'.join(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Check that tc.md covers every coverage item in ac.md.')
    ap.add_argument('ac')
    ap.add_argument('tc')
    ap.add_argument('--summary', action='store_true', help='print the Coverage summary table')
    a = ap.parse_args(argv)
    try:
        spec, tcs = parse_ac(a.ac), parse_tc(a.tc)
    except FormatError as e:
        print(f'coverage: {e}', file=sys.stderr)
        return 2
    errors, summary = check(spec, tcs)
    for e in errors:
        print(f'coverage: {e}')
    if a.summary:
        print(summary_table(summary))
    print(f'coverage: {len(errors)} error(s), {len(tcs)} TC')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
