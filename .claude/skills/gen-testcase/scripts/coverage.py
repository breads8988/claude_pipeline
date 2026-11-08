#!/usr/bin/env python3
"""Coverage validator: every coverage item in ac.md is exercised by a TC in tc.md.

Usage:
  python3 coverage.py qa/specs/<feature>/ac.md qa/testcases/<feature>/tc.md [--summary]

Coverage items come from ac.md (AC, BR, DT columns, ST transitions, FLD boundaries) and from the
`## Test analysis` partition table in tc.md (EP partitions). Deprecated items are excluded.

Errors (exit 1):
  - An active AC, BR, DT column, valid transition (and invalid transition at 🔴 depth), EP partition
    or required BVA value has no TC. Items covered only by blocked TCs are reported as blocked, not errors.
  - A FLD has no partition row, or lacks a valid or an invalid partition.
  - A BVA label is unknown, or its value does not match the FLD min/max/step.
  - A TC cites an ID that is not in ac.md, or an EP partition that is not in the partition table.
  - TC priority ≠ highest criticality among its `Covers AC` and its coverage items.
  - Blocking: a `Blocked` TC needs `Blocked by: OQ-…` and a `TBD (OQ-…)` line; a TC with `TBD (OQ-…)`
    must be `Blocked` by that OQ; the OQ must exist and be `Open` or `Posted`.
  - A TC citing `EG:`, `CHK:` or pairwise (`PW-NN`) items has no `Covers AC`.
  - Pairwise: a `PW-NN` row of the Test analysis table has no TC, a TC cites an unknown row, or the
    rows miss a pair of values of two parameters (all-pairs).
  - Duplicate AC or TC IDs; a TC section without a Field/Value table.
  - The `## Coverage summary` table in tc.md differs from the computed one.

--summary prints the computed Coverage summary table.
Exit codes: 0 full coverage · 1 errors found · 2 usage, file or format error.
"""
import argparse
import math
import re
import sys

ICONS = {'🔴': 4, '🟠': 3, '🟡': 2, '⚪': 1}
WORDS = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
ICON_OF = {v: k for k, v in ICONS.items()}
CODE = r'[A-Z]{3,4}'
SEP_RE = re.compile(r'^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$')
AC_H = re.compile(rf'^###\s+(AC-{CODE}-\d{{3}})\b')
DT_H = re.compile(rf'^###\s+(DT-{CODE}-\d{{2}})\b')
ST_H = re.compile(rf'^###\s+(ST-{CODE}-\d{{2}})\b')
TC_H = re.compile(rf'^##\s+(TC-{CODE}-\d{{3}})\b')
ITEM_ID = re.compile(rf'\b((?:AC|BR)-{CODE}-\d{{3}}|(?:DT|ST)-{CODE}-\d{{2}}\.[RT]\d+|FLD-{CODE}-\d{{2}})\b')
FLD_ITEM = re.compile(rf'^(FLD-{CODE}-\d{{2}})\s+(EP|BVA)\s*:\s*(.+)$')
TBD_RE = re.compile(rf'TBD\s*\((OQ-{CODE}-\d{{3}})\)')
TRUE = {'yes', 'y', 'valid', 'true', '✅', '✓'}
FALSE = {'no', 'n', 'invalid', 'false', '❌', '✗'}
OPEN_OQ = ('open', 'posted')
TECHS = ('Scenario (AC)', 'Business rules', 'EP', 'BVA', 'Decision table', 'State transition')
OPTIONAL_TECHS = ('Pairwise',)  # listed in the summary only when the tc.md has items for them
PW_ID = re.compile(r'\bPW-\d{2}\b')


class FormatError(Exception):
    pass


def read(path):
    try:
        with open(path, encoding='utf-8-sig') as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        raise FormatError(f'cannot read {path}: {getattr(e, "strerror", None) or e}')
    lines = text.splitlines()
    # Blank out fenced code so examples inside fences are never parsed.
    out, fence = [], None
    for line in lines:
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
    """Split a table row on unescaped pipes outside code spans."""
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'):
        s = s[:-1]
    parts, buf, in_code, i = [], '', False, 0
    while i < len(s):
        ch = s[i]
        if ch == '\\' and i + 1 < len(s) and s[i + 1] == '|':
            buf += '|'
            i += 2
            continue
        if ch == '`':
            in_code = not in_code
        if ch == '|' and not in_code:
            parts.append(buf.strip())
            buf = ''
        else:
            buf += ch
        i += 1
    parts.append(buf.strip())
    return parts


def level(text):
    t = text.strip().strip('*').strip()
    for icon, v in ICONS.items():
        if icon in t:
            return v
    for w, v in WORDS.items():
        if t.lower().startswith(w):
            return v
    return 0


def tables(lines, start, stop):
    """Yield (header, rows) for tables between line indexes start and stop."""
    i = start
    while i < stop:
        if lines[i].lstrip().startswith('|') and i + 1 < stop and SEP_RE.match(lines[i + 1]):
            header = [h.strip('* ').lower() for h in cells(lines[i])]
            rows, j = [], i + 2
            while j < stop and lines[j].lstrip().startswith('|'):
                rows.append(cells(lines[j]))
                j += 1
            yield header, rows
            i = j
            continue
        i += 1


def sections(lines, rx, max_level):
    """[(id, start, end)] for headings matching rx; ends at the next heading of level ≤ max_level."""
    found = [(m.group(1), i) for i, l in enumerate(lines) for m in [rx.match(l)] if m]
    stop_rx = re.compile(rf'^#{{1,{max_level}}}\s')
    out = []
    for sid, start in found:
        end = next((j for j in range(start + 1, len(lines)) if stop_rx.match(lines[j])), len(lines))
        out.append((sid, start, end))
    return out


def bullet(lines, start, end, name):
    rx = re.compile(rf'^\s*-\s*\**{name}\**\s*:\s*\**\s*(.+?)\s*$', re.I)
    for i in range(start, end):
        m = rx.match(lines[i])
        if m:
            return m.group(1).strip()
    return ''


def deprecated(text):
    return text.strip().strip('`*').lower().startswith('deprecated')


def number(text):
    """The plain number in a cell, or None (empty, TBD, an ID or a mixed value)."""
    t = text.strip().strip('`*').replace('\u2212', '-').replace('\u00a0', '').replace(' ', '')
    t = re.sub(r'(?<=\d),(?=\d{3}\b)', '', t)  # thousands separator
    m = re.fullmatch(r'-?\d+(?:\.\d+)?', t)
    return float(m.group(0)) if m else None


def col(row, *names):
    for k, v in row.items():
        if any(k.startswith(n) for n in names):
            return v
    return ''


def parse_ac(path):
    lines = read(path)
    ac, seen = {}, set()
    dups = []
    for sid, s, e in sections(lines, AC_H, 3):
        if sid in seen:
            dups.append(sid)
        seen.add(sid)
        ac[sid] = {'crit': level(bullet(lines, s, e, 'Criticality')),
                   'active': not deprecated(bullet(lines, s, e, 'Status')),
                   'high': bullet(lines, s, e, 'Likelihood').lower().startswith('high'),
                   'text': '\n'.join(lines[s:e])}
    if not ac:
        raise FormatError(f'{path}: no AC sections (### AC-<CODE>-NNN)')
    br, fld, oq = {}, {}, {}
    for header, rows in tables(lines, 0, len(lines)):
        for r in rows:
            row = dict(zip(header, r + [''] * (len(header) - len(r))))
            first = (r[0] if r else '').strip('` ')
            if deprecated(col(row, 'status')):
                continue
            if re.fullmatch(rf'BR-{CODE}-\d{{3}}', first):
                br[first] = level(col(row, 'criticality'))
            elif re.fullmatch(rf'FLD-{CODE}-\d{{2}}', first):
                lo, hi = col(row, 'min'), col(row, 'max')
                step = number(col(row, 'step')) or 1.0
                fld[first] = {'crit': level(col(row, 'criticality')), 'min': lo, 'max': hi, 'step': step}
            elif re.fullmatch(rf'OQ-{CODE}-\d{{3}}', first):
                oq[first] = col(row, 'status').strip('` ').lower()
    dt, st, links, dt_meta = {}, {}, {}, {}
    for sid, s, e in sections(lines, DT_H, 3):
        if deprecated(bullet(lines, s, e, 'Status')):
            continue
        crit = level(bullet(lines, s, e, 'Criticality'))
        covers = set(re.findall(rf'AC-{CODE}-\d{{3}}', bullet(lines, s, e, 'Covers')))
        cols, merged = [], False
        for header, rows in tables(lines, s, e):
            cols = [c.upper() for c in header if re.fullmatch(r'r\d+', c)]
            if cols:
                idx = [i for i, c in enumerate(header) if re.fullmatch(r'r\d+', c)]
                for r in rows:
                    if r and 'outcome' in r[0].lower() or (r and r[0].startswith('**')):
                        continue
                    merged |= any(i < len(r) and r[i].strip() in ('–', '-', '—') for i in idx)
                break
        if not cols:
            raise FormatError(f'{path}: {sid} has no table with R1…Rn columns')
        for c in cols:
            dt[f'{sid}.{c}'] = crit
        links[sid] = covers
        dt_meta[sid] = {'crit': crit, 'merged': merged}
    for sid, s, e in sections(lines, ST_H, 3):
        if deprecated(bullet(lines, s, e, 'Status')):
            continue
        crit = level(bullet(lines, s, e, 'Criticality'))
        links[sid] = set(re.findall(rf'AC-{CODE}-\d{{3}}', bullet(lines, s, e, 'Covers')))
        found = 0
        for header, rows in tables(lines, s, e):
            if 't' not in header:
                continue
            if 'valid' not in header:
                raise FormatError(f'{path}: {sid} transition table has no Valid column')
            for r in rows:
                row = dict(zip(header, r))
                t = row.get('t', '').strip('* ')
                if not re.fullmatch(r'T\d+', t):
                    continue
                v = row.get('valid', '').strip('* ').lower()
                if TBD_RE.search(row.get('valid', '')):
                    st[f'{sid}.{t}'] = {'crit': crit, 'valid': None, 'model': sid}
                    found += 1
                    continue
                if v not in TRUE | FALSE:
                    raise FormatError(f'{path}: {sid}.{t} Valid must be Yes or No, got "{v}"')
                st[f'{sid}.{t}'] = {'crit': crit, 'valid': v in TRUE, 'model': sid}
                found += 1
            break
        if not found:
            raise FormatError(f'{path}: {sid} has no transition rows (T1…Tn)')
    # Depth (test-design-techniques §3): max(item, covered AC) + one level if a covered AC has
    # Likelihood High, capped at 🔴. Links: the model's `Covers` bullet plus AC that cite the item ID.
    def depth(item_id, crit):
        acs = {a for a in links.get(item_id, set()) | {a for a, v in ac.items() if item_id in v['text']}
               if a in ac and ac[a]['active']}
        base = max([crit] + [ac[a]['crit'] for a in acs])
        return min(4, base + (1 if any(ac[a]['high'] for a in acs) else 0))
    for f, v in fld.items():
        v['depth'] = depth(f, v['crit'])
    for t, v in st.items():
        v['depth'] = depth(v['model'], v['crit'])
    errors = []
    for sid, m in dt_meta.items():
        d = depth(sid, m['crit'])
        if m['merged'] and d >= 3:
            errors.append(f'{sid}: minimised table (merged "–" cells) at {ICON_OF[d]} depth; list every feasible column')
    return {'ac': ac, 'br': br, 'fld': fld, 'dt': dt, 'st': st, 'oq': oq, 'dups': dups, 'errors': errors}


def parse_tc(path):
    lines = read(path)
    tcs, dups, errors = {}, [], []
    partitions = {}
    pw, pw_params = {}, []
    summary = None
    for i, line in enumerate(lines):
        if re.match(r'^##\s+Test analysis\b', line, re.I):
            end = next((j for j in range(i + 1, len(lines)) if re.match(r'^#{1,2}\s', lines[j])), len(lines))
            for header, rows in tables(lines, i, end):
                if header and header[0] == 'pw':
                    pw_params[:] = header[1:]
                    if len(set(header[1:])) != len(header[1:]):
                        errors.append('Test analysis: pairwise table has duplicate parameter names')
                    for r in rows:
                        rid = (r[0] if r else '').strip('`* ')
                        if len(r) > len(header):
                            errors.append(f'Test analysis: {rid} has more cells than the pairwise header')
                        if PW_ID.fullmatch(rid):
                            if rid in pw:
                                errors.append(f'Test analysis: duplicate pairwise row {rid}')
                            pw[rid] = {h: norm(r[i + 1]) if i + 1 < len(r) else '' for i, h in enumerate(header[1:])}
                if header[:2] == ['fld', 'partition']:
                    for r in rows:
                        row = dict(zip(header, r + [''] * (len(header) - len(r))))
                        f = row['fld'].strip('` ')
                        label = norm(row['partition'])
                        kind = row.get('kind', '').strip().lower()
                        partitions.setdefault(f, {})[label] = kind
        if re.match(r'^##\s+Coverage summary\b', line, re.I):
            end = next((j for j in range(i + 1, len(lines)) if re.match(r'^#{1,2}\s', lines[j])), len(lines))
            for header, rows in tables(lines, i, end):
                summary = {r[0]: r[1:] for r in rows if r}
                break
    for sid, s, e in sections(lines, TC_H, 2):
        if sid in tcs:
            dups.append(sid)
        fields = None
        for header, rows in tables(lines, s, e):
            if header[:2] == ['field', 'value']:
                cand = {r[0].strip('* ').lower(): (r[1] if len(r) > 1 else '') for r in rows}
                if 'covers ac' in cand or 'priority' in cand:
                    fields = cand
                    break
        if fields is None:
            errors.append(f'{sid}: no Field/Value table')
            fields = {}
        items_cell = fields.get('coverage items', '')
        items = re.findall(r'`([^`]+)`', items_cell) or [x for x in re.split(r'[,;]', items_cell) if x.strip()]
        covers = set(re.findall(rf'AC-{CODE}-\d{{3}}', fields.get('covers ac', '')))
        body = '\n'.join(lines[s:e])
        flds = [m.groups() for m in (FLD_ITEM.match(x.strip()) for x in items) if m]
        pws = {x.strip() for x in items if PW_ID.fullmatch(x.strip())}
        tcs[sid] = {
            'covers': covers,
            'ids': set(ITEM_ID.findall(items_cell)) | covers,
            'items': set(ITEM_ID.findall(items_cell)),
            'fld': [(f, tech.upper(), lab.strip()) for f, tech, lab in flds],
            'eg': any(re.match(r'^\s*(EG|CHK)\s*:', x) for x in items),
            'pw': pws,
            'priority': level(fields.get('priority', '')),
            'status': fields.get('status', '').strip('` ').lower(),
            'blocked_by': fields.get('blocked by', '').strip(),
            'tbd': set(TBD_RE.findall(body)),
        }
    if not tcs:
        raise FormatError(f'{path}: no TC sections (## TC-<CODE>-NNN)')
    return tcs, dups, errors, {'ep': partitions, 'pw': pw}, summary


def norm(label):
    return re.sub(r'\s+', ' ', label.strip().strip('`').lower())


def bva_required(f):
    """Required BVA labels and expected values for a field."""
    three = f.get('depth', f['crit']) >= 3  # 🟠 and 🔴: 3-value (test-design-techniques §3)
    req = {}
    for side, raw in (('min', f['min']), ('max', f['max'])):
        if not raw.strip() or raw.strip() in ('—', '-', 'n/a', 'N/A'):
            continue
        base = number(raw)
        step = f['step']
        offs = {'min': (-1, 0, 1) if three else (-1, 0), 'max': (-1, 0, 1) if three else (0, 1)}[side]
        for o in offs:
            label = side if o == 0 else f'{side}{"+" if o > 0 else "-"}1'
            req[label] = None if base is None else round(base + o * step, 6)
    return req


def all_pairs_missing(rows):
    """Pairs of values (two parameters) that no row contains. Values per parameter = values used in rows."""
    if not rows:
        return []
    params = list(next(iter(rows.values())))  # every row has every header parameter (blank = '')
    values = {p: sorted({r.get(p, '') for r in rows.values()} - {''}) for p in params}
    missing = []
    for i, a in enumerate(params):
        for b in params[i + 1:]:
            seen = {(r.get(a), r.get(b)) for r in rows.values()}
            missing += [f'{a}={x} × {b}={y}' for x in values[a] for y in values[b] if (x, y) not in seen]
    blanks = sorted(f'{rid} {p}' for rid, r in rows.items() for p in params if not r.get(p))
    missing += [f'{b} is blank' for b in blanks]
    return missing


def check(spec, tcs, analysis):
    partitions, pw_rows = analysis['ep'], analysis['pw']
    errors = []
    live = {k: v for k, v in tcs.items() if not v['status'].startswith('deprecated')}
    active = {k: v for k, v in live.items() if not v['status'].startswith('blocked')}
    blocked = {k: v for k, v in live.items() if v['status'].startswith('blocked')}
    cited_a = set().union(*[t['ids'] for t in active.values()]) if active else set()
    cited_b = set().union(*[t['ids'] for t in blocked.values()]) if blocked else set()
    known = set(spec['ac']) | set(spec['br']) | set(spec['dt']) | set(spec['st']) | set(spec['fld'])
    summary = {}

    def tally(name, items, covered_a, covered_b):
        a = [i for i in items if i in covered_a]
        b = [i for i in items if i not in covered_a and i in covered_b]
        summary[name] = (len(items), len(a), len(b))
        return [i for i in items if i not in covered_a and i not in covered_b], b

    item_a = set().union(*[t['items'] for t in active.values()]) if active else set()
    item_b = set().union(*[t['items'] for t in blocked.values()]) if blocked else set()
    missing, _ = tally('Scenario (AC)', [a for a, v in spec['ac'].items() if v['active']], item_a, item_b)
    errors += [f'{i}: no TC cites this AC in Coverage items' for i in missing]
    for name, items, label in (
            ('Business rules', list(spec['br']), 'no TC covers this business rule'),
            ('Decision table', list(spec['dt']), 'decision table column not covered')):
        missing, _ = tally(name, items, cited_a, cited_b)
        errors += [f'{i}: {label}' for i in missing]
    need_st = [t for t, v in spec['st'].items()
               if v['valid'] or v['valid'] is None or v.get('depth', v['crit']) == 4]
    missing, _ = tally('State transition', need_st, cited_a, cited_b)
    for t in missing:
        kind = {True: 'valid', None: 'TBD'}.get(spec['st'][t]['valid'], 'invalid (required at 🔴 depth)')
        errors.append(f'{t}: {kind} transition not covered')

    # EP: partitions from the tc.md test analysis table.
    ep_total = ep_a = ep_b = 0
    ep_cited = {}
    for tid, t in live.items():
        for fid, tech, lab in t['fld']:
            if tech == 'EP':
                ep_cited.setdefault((fid, norm(lab)), set()).add(tid)
    for (fid, lab), tids in sorted(ep_cited.items()):
        if lab not in partitions.get(fid, {}):
            errors.append(f'{", ".join(sorted(tids))}: EP partition "{lab}" of {fid} is not in the Test analysis table')
    for f in spec['fld']:
        parts = partitions.get(f, {})
        if not parts:
            errors.append(f'{f}: no partitions in the Test analysis table')
            continue
        kinds = set(parts.values())
        if 'valid' not in kinds:
            errors.append(f'{f}: no valid partition listed')
        if 'invalid' not in kinds:
            errors.append(f'{f}: no invalid partition listed')
        for lab in parts:
            ep_total += 1
            tids = ep_cited.get((f, lab), set())
            if tids & set(active):
                ep_a += 1
            elif tids & set(blocked):
                ep_b += 1
            else:
                errors.append(f'{f}: EP partition "{lab}" not covered')
    summary['EP'] = (ep_total, ep_a, ep_b)

    # Pairwise: rows of the PW table in Test analysis.
    if pw_rows:
        pw_a = set().union(*[t['pw'] for t in active.values()]) if active else set()
        pw_b = set().union(*[t['pw'] for t in blocked.values()]) if blocked else set()
        missing, _ = tally('Pairwise', sorted(pw_rows), pw_a, pw_b)
        errors += [f'{r}: pairwise row not covered' for r in missing]
        errors += [f'pairwise: pair {p} is in no PW row' for p in all_pairs_missing(pw_rows)]
    for tid, t in live.items():
        for r in sorted(t['pw'] - set(pw_rows)):
            errors.append(f'{tid}: {r} is not in the pairwise table of Test analysis')

    # BVA: labels and values against min/max/step.
    bva_total = bva_a = bva_b = 0
    for f, v in spec['fld'].items():
        req = bva_required(v)
        got = {}
        for tid, t in live.items():
            for fid, tech, lab in t['fld']:
                if fid != f or tech != 'BVA':
                    continue
                m = re.match(r'^\s*(min|max)\s*([+-]\s*1)?\s*(?:=\s*(.+))?$', lab, re.I)
                if not m:
                    errors.append(f'{tid}: BVA label "{lab}" for {f} must look like "min-1 = 5"')
                    continue
                key = m.group(1).lower() + (m.group(2) or '').replace(' ', '')
                if key not in req:
                    errors.append(f'{tid}: BVA label "{key}" is not required for {f}')
                    continue
                want = req[key]
                tbd_oq = TBD_RE.search(v['min'] if key.startswith('min') else v['max'])
                if tbd_oq and tid in active:
                    errors.append(f'{tid}: {f} {key[:3]} is TBD ({tbd_oq.group(1)}); this TC must be Blocked by it')
                have = number(m.group(3) or '')
                if want is not None and have is not None and abs(have - want) > 1e-9:
                    errors.append(f'{tid}: {f} BVA {key} = {m.group(3).strip()}, expected {want:g}')
                got.setdefault(key, set()).add(tid)
        # Labels with the same value (narrow range, e.g. min+1 = max) are one coverage item.
        groups = {}
        for key, want in req.items():
            groups.setdefault(key if want is None else want, []).append(key)
        for keys in groups.values():
            bva_total += 1
            tids = set().union(*[got.get(k, set()) for k in keys])
            if tids & set(active):
                bva_a += 1
            elif tids & set(blocked):
                bva_b += 1
            else:
                depth = '3-value' if v.get('depth', v['crit']) >= 3 else '2-value'
                errors.append(f'{f}: BVA {" / ".join(keys)} not covered ({depth})')
    summary['BVA'] = (bva_total, bva_a, bva_b)

    for tid, t in sorted(tcs.items()):
        for i in sorted(t['ids'] - known):
            errors.append(f'{tid}: cites {i}, which is not in ac.md')
        if tid in active:
            for i in sorted(x for x in t['ids'] if x in spec['st'] and spec['st'][x]['valid'] is None):
                errors.append(f'{tid}: cites {i}, whose Valid is TBD; this TC must be Blocked by that open question')
        crits = [spec['ac'].get(i, {}).get('crit', 0) if i.startswith('AC-') else
                 spec['br'].get(i, 0) if i.startswith('BR-') else
                 spec['dt'].get(i, 0) if i.startswith('DT-') else
                 spec['st'].get(i, {}).get('crit', 0) if i.startswith('ST-') else
                 spec['fld'].get(i, {}).get('crit', 0) for i in t['ids']]
        top = max(crits, default=0)
        if top and t['priority'] != top:
            errors.append(f'{tid}: priority {ICON_OF.get(t["priority"], "none")} should be {ICON_OF[top]} '
                          '(highest of Covers AC and coverage items)')
        if (t['eg'] or t['pw']) and not t['covers']:
            errors.append(f'{tid}: EG/CHK/PW items need a Covers AC; raise an AC or open question first')
        is_blocked = t['status'].startswith('blocked')
        oq = re.search(rf'OQ-{CODE}-\d{{3}}', t['blocked_by'])
        if is_blocked:
            if not oq:
                errors.append(f'{tid}: blocked without an open question in Blocked by')
            else:
                q = oq.group(0)
                if q not in spec['oq']:
                    errors.append(f'{tid}: Blocked by {q}, which is not in ac.md')
                elif not spec['oq'][q].startswith(OPEN_OQ):
                    errors.append(f'{tid}: {q} is {spec["oq"][q]}; unblock this TC')
                if q not in t['tbd']:
                    errors.append(f'{tid}: blocked by {q} but has no "TBD ({q})" line; only TCs with TBD are blocked')
        for q in sorted(t['tbd']):
            if not is_blocked or not oq or oq.group(0) != q:
                errors.append(f'{tid}: contains TBD ({q}) but is not Blocked by {q}')

    eg = sum(1 for t in live.values() if t['eg'])
    return errors, summary, eg


def pct(total, cov):
    return f'{math.floor(100 * cov / total)}%' if total else '—'


def summary_rows(summary):
    names = list(TECHS) + [n for n in OPTIONAL_TECHS if n in summary]
    return [(n, str(summary.get(n, (0, 0, 0))[0]), str(summary.get(n, (0, 0, 0))[1]),
             str(summary.get(n, (0, 0, 0))[2]), pct(summary.get(n, (0, 0, 0))[0], summary.get(n, (0, 0, 0))[1]))
            for n in names]


def summary_table(summary):
    rows = ['| Technique | Items identified | Covered | Blocked | Coverage |', '| --- | --- | --- | --- | --- |']
    rows += [f'| {a} | {b} | {c} | {d} | {e} |' for a, b, c, d, e in summary_rows(summary)]
    return '\n'.join(rows)


def compare_summary(header_table, summary):
    if header_table is None:
        return ['tc.md: no "## Coverage summary" table; run with --summary and paste it']
    errs = []
    for name, *vals in summary_rows(summary):
        have = [c.strip() for c in header_table.get(name, [])][:4]
        if have != list(vals):
            errs.append(f'Coverage summary row "{name}" is {have or "missing"}, expected {list(vals)}; '
                        'run with --summary and paste the table')
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser(description='Check that tc.md covers every coverage item in ac.md.')
    ap.add_argument('ac')
    ap.add_argument('tc')
    ap.add_argument('--summary', action='store_true', help='print the computed Coverage summary table')
    a = ap.parse_args(argv)
    try:
        spec = parse_ac(a.ac)
        tcs, tc_dups, tc_errors, analysis, header = parse_tc(a.tc)
    except FormatError as e:
        print(f'coverage: {e}', file=sys.stderr)
        return 2
    errors, summary, eg = check(spec, tcs, analysis)
    errors = [f'duplicate {d}' for d in spec['dups'] + tc_dups] + spec['errors'] + tc_errors + errors
    errors += compare_summary(header, summary)
    for e in errors:
        print(f'coverage: {e}')
    if a.summary:
        print(summary_table(summary))
    blocked = sum(v[2] for v in summary.values())
    print(f'coverage: {len(errors)} error(s), {len(tcs)} TC, {blocked} item(s) blocked, {eg} EG/CHK TC')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
