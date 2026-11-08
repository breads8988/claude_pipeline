#!/usr/bin/env python3
"""Summarise a run file and export a self-contained HTML report.

Usage:
  python3 report.py qa/runs/<run>.md [--out <file.html>] [--no-update]

- Reads the header table (Field | Value) and the Results table of the run file.
- Writes the HTML report first, then recounts results into the run file's Summary table
  (skip with --no-update; use it on `_example` files).
- Default output: `<repo>/qa/reports/<run>.html` when the run file sits under a `runs` folder,
  else next to the run file.
- Embeds screenshots for failed TCs only. Source: the path in the row's Evidence cell (as saved by the
  browser tool), else `<runs>/<run>/evidence/<TC-ID>.png`.
- Lists 🔴 Critical passes as an optional re-check. Warns on stderr when State is not Done.

Exit codes: 0 report written · 2 usage, file or format error.
"""
import argparse
import base64
import html
import os
import re
import sys
import tempfile

STATES = ('Pass', 'Fail', 'Blocked', 'Skip', 'Not run')
EMOJI = {'✅': 'Pass', '❌': 'Fail', '⛔': 'Blocked', '⏭': 'Skip', '⬜': 'Not run'}
SEP_RE = re.compile(r'^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$')
TC_ID = re.compile(r'^TC-[A-Z]{3,4}-\d{3}$')
IMAGE_TYPES = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}


class RunError(Exception):
    pass


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


def tables(lines):
    """Yield (heading, header, rows, start, end) for each markdown table outside code fences."""
    heading, i, fence = '', 0, None
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            if m and m.group(1)[0] == fence[0]:
                fence = None
            i += 1
            continue
        if m:
            fence = m.group(1)
            i += 1
            continue
        if line.startswith('#'):
            heading = re.sub(r'^#+\s*', '', line).strip()
        if line.lstrip().startswith('|') and i + 1 < len(lines) and SEP_RE.match(lines[i + 1]):
            header = [h.lower() for h in cells(line)]
            rows, j = [], i + 2
            while j < len(lines) and lines[j].lstrip().startswith('|'):
                rows.append((j, cells(lines[j])))
                j += 1
            yield heading, header, rows, i, j
            i = j
            continue
        i += 1


def state_of(cell):
    """Exact result tokens only: an emoji and/or a state word."""
    text = cell.replace('\ufe0f', '').strip()
    state = None
    for e, s in EMOJI.items():
        if text.startswith(e):
            state, text = s, text[len(e):].strip()
            break
    if not text:
        return state or 'Not run'
    word = next((s for s in STATES if text.lower() == s.lower()), None)
    if word and (state is None or state == word):
        return word
    return None


def parse(path):
    try:
        with open(path, encoding='utf-8-sig') as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise RunError(f'cannot read {path}: {getattr(e, "strerror", None) or e}')
    title = next((re.sub(r'^#\s+', '', l).strip() for l in lines if l.startswith('# ')), os.path.basename(path))
    meta, results, summary_span, summary_head = {}, None, None, None
    for i, l in enumerate(lines):
        if re.match(r'^##\s+Summary\b', l, re.I):
            summary_head = i
    for heading, header, rows, start, end in tables(lines):
        if header[:2] == ['field', 'value'] and not meta:
            meta = {r[0]: r[1] for _, r in rows if len(r) >= 2}
        elif 'tc' in header and 'result' in header:
            if results is not None:
                raise RunError(f'{path}: more than one Results table')
            results = []
            for _, r in rows:
                if len(r) > len(header):
                    raise RunError(f'{path}: row "{r[0]}" has more cells than the header (unescaped |?)')
                results.append(dict(zip(header, r + [''] * (len(header) - len(r)))))
        elif heading.lower().startswith('summary') and 'total' in header:
            summary_span = (start, end)
    if results is None:
        raise RunError(f'{path}: no Results table (needs TC and Result columns)')
    for r in results:
        s = state_of(r.get('result', ''))
        if s is None:
            raise RunError(f'{path}: unknown result "{r.get("result")}" for {r.get("tc")}; '
                           'use ✅ Pass, ❌ Fail, ⛔ Blocked, ⏭ Skip or ⬜')
        r['state'] = s
    return title, meta, results, lines, summary_span, summary_head


def counts(results):
    c = {s: 0 for s in STATES}
    for r in results:
        c[r['state']] += 1
    return c


def atomic_write(path, text):
    d = os.path.dirname(os.path.abspath(path))
    try:
        os.makedirs(d, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=d, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError as e:
        raise RunError(f'cannot write {path}: {e.strerror or e}')


def update_summary(path, lines, span, head, c, total, newline):
    row = f"| {total} | {c['Pass']} | {c['Fail']} | {c['Blocked']} | {c['Skip']} | {c['Not run']} |"
    block = ['| Total | Pass | Fail | Blocked | Skip | Not run |', '| --- | --- | --- | --- | --- | --- |', row]
    if span:
        lines = lines[:span[0]] + block + lines[span[1]:]
    elif head is not None:
        lines = lines[:head + 1] + block + lines[head + 1:]
    else:
        lines = lines + ['', '## Summary'] + block
    atomic_write(path, newline.join(lines) + newline)


def runs_root(run_path):
    """Nearest ancestor folder named 'runs', or None."""
    d = os.path.dirname(os.path.abspath(run_path))
    while True:
        if os.path.basename(d) == 'runs':
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def default_out(run_path, stem):
    root = runs_root(run_path)
    base = os.path.join(os.path.dirname(root), 'reports') if root else os.path.dirname(os.path.abspath(run_path))
    return os.path.join(base, f'{stem}.html')


def evidence_img(run_path, row):
    """Data URI for a failed row's screenshot, or None."""
    run_dir = os.path.dirname(os.path.abspath(run_path))
    candidates = []
    cell = row.get('evidence', '').strip().strip('`')
    if os.path.splitext(cell)[1].lower() in IMAGE_TYPES:
        if os.path.isabs(cell):
            candidates.append(cell)
        else:
            candidates.append(os.path.join(run_dir, cell))
            root = runs_root(run_path)
            if root:  # repo-relative path (`qa/runs/<run>/evidence/…`): resolve from the repo root
                candidates.append(os.path.join(os.path.dirname(os.path.dirname(root)), cell))
    tc = row.get('tc', '').strip()
    if TC_ID.match(tc):
        stem = os.path.splitext(os.path.basename(run_path))[0]
        candidates.append(os.path.join(run_dir, stem, 'evidence', f'{tc}.png'))
        if cell and '/' not in cell:
            candidates.append(os.path.join(run_dir, stem, 'evidence', cell))
    for p in candidates:
        ext = os.path.splitext(p)[1].lower()
        if ext in IMAGE_TYPES and os.path.isfile(p):
            with open(p, 'rb') as f:
                return f'data:{IMAGE_TYPES[ext]};base64,' + base64.b64encode(f.read()).decode()
    return None


CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--line:#e4e1d8;--card:#fff;
--pass:#2f7d4f;--fail:#b3261e;--blocked:#8a5a00;--skip:#5b5b8a;--notrun:#7a7a7a}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#171715;--fg:#ecebe6;--muted:#a3a29b;
--line:#33322e;--card:#1f1f1c;--pass:#6cc58f;--fail:#f08a80;--blocked:#e2b155;--skip:#a9a9de;--notrun:#9a9a9a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:1080px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:32px 0 10px}
.muted{color:var(--muted)}.meta{display:flex;flex-wrap:wrap;gap:6px 18px;margin:8px 0 20px;font-size:13px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.tile b{display:block;font-size:24px;font-variant-numeric:tabular-nums}
.bar{display:flex;height:8px;border-radius:4px;overflow:hidden;margin:14px 0 0;background:var(--line)}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}
table{border-collapse:collapse;width:100%;min-width:760px;font-size:14px}
.nw{white-space:nowrap}
code{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--line);padding:1px 4px;border-radius:4px}
.ev{display:block;margin-top:4px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
tr:last-child td{border-bottom:0}
.s{font-weight:600;white-space:nowrap}.s-Pass{color:var(--pass)}.s-Fail{color:var(--fail)}
.s-Blocked{color:var(--blocked)}.s-Skip{color:var(--skip)}.s-NotRun{color:var(--notrun)}
details{margin-top:6px}details img{max-width:100%;border:1px solid var(--line);border-radius:6px;margin-top:8px}
summary{cursor:pointer;color:var(--muted);font-size:13px}
"""

COLOR = {'Pass': 'var(--pass)', 'Fail': 'var(--fail)', 'Blocked': 'var(--blocked)',
         'Skip': 'var(--skip)', 'Not run': 'var(--notrun)'}
ORDER = {'Fail': 0, 'Blocked': 1, 'Not run': 2, 'Skip': 3, 'Pass': 4}


def md(text):
    """Escape, then render `code` spans."""
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', html.escape(text))


def is_critical(pri):
    p = pri.strip()
    return p.startswith('🔴') or p.lower().startswith('critical')


def cls(state):
    return 's-' + state.replace(' ', '').replace('Notrun', 'NotRun')


def render(run_path, title, meta, results):
    e = html.escape
    c, total = counts(results), len(results)
    executed = total - c['Not run'] - c['Skip'] - c['Blocked']
    rate = f"{round(100 * c['Pass'] / executed)}%" if executed else '—'
    meta_html = ''.join(f'<span><span class="muted">{e(k)}:</span> {md(v)}</span>' for k, v in meta.items())
    tiles = ''.join(f'<div class="tile"><span class="muted">{s}</span><b class="{cls(s)}">{c[s]}</b></div>'
                    for s in STATES)
    tiles = f'<div class="tile"><span class="muted">Total</span><b>{total}</b></div>' + tiles + \
        f'<div class="tile"><span class="muted">Pass rate</span><b>{rate}</b></div>'
    bar = ''.join(f'<span style="width:{100 * c[s] / total:.2f}%;background:{COLOR[s]}" title="{s}: {c[s]}"></span>'
                  for s in STATES if total and c[s])
    rows = []
    for r in sorted(results, key=lambda r: (ORDER[r['state']], r.get('tc', ''))):
        ev = ''
        if r['state'] == 'Fail':
            img = evidence_img(run_path, r)
            ev = (f'<details><summary>Screenshot</summary><img alt="Screenshot for {e(r.get("tc", ""))}" src="{img}"></details>'
                  if img else '<span class="muted ev">No screenshot</span>')
        rows.append('<tr>' + ''.join([
            f'<td class="nw">{e(r.get("tc", ""))}</td>', f'<td>{md(r.get("title", ""))}</td>',
            f'<td>{e(r.get("role", ""))}</td>', f'<td>{e(r.get("pri", ""))}</td>',
            f'<td class="s {cls(r["state"])}">{e(r["state"])}</td>',
            f'<td class="nw">{e(r.get("bug", ""))}</td>', f'<td>{md(r.get("note", ""))}{ev}</td>']) + '</tr>')
    recheck = [r for r in results if r['state'] == 'Pass' and is_critical(r.get('pri', ''))]
    recheck_html = ('<ul>' + ''.join(f'<li>{e(r.get("tc", ""))} · {e(r.get("title", ""))} · {e(r.get("role", ""))}</li>'
                                     for r in recheck) + '</ul>') if recheck else '<p class="muted">No 🔴 passes.</p>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><style>{CSS}</style></head>
<body><main>
<h1>{e(title)}</h1>
<div class="meta">{meta_html}</div>
<div class="tiles">{tiles}</div>
<div class="bar" role="img" aria-label="Result distribution">{bar}</div>
<h2>Results</h2>
<div class="wrap"><table><thead><tr><th>TC</th><th>Title</th><th>Role</th><th>Pri</th><th>Result</th><th>Bug</th><th>Note / evidence</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<h2>Optional re-check: 🔴 passes ({len(recheck)})</h2>
{recheck_html}
</main></body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description='Export a run file to an HTML report.')
    ap.add_argument('run')
    ap.add_argument('--out')
    ap.add_argument('--no-update', action='store_true', help='do not rewrite the Summary table')
    a = ap.parse_args(argv)
    try:
        title, meta, results, lines, span, head = parse(a.run)
        c = counts(results)
        stem = os.path.splitext(os.path.basename(a.run))[0]
        out = a.out or default_out(a.run, stem)
        if os.path.isdir(out):
            raise RunError(f'--out {out} is a directory; give a file name')
        atomic_write(out, render(a.run, title, meta, results))
        if not a.no_update:
            with open(a.run, encoding='utf-8-sig', newline='') as f:
                newline = '\r\n' if '\r\n' in f.read() else '\n'
            update_summary(a.run, lines, span, head, c, len(results), newline)
    except RunError as err:
        print(f'report: {err}', file=sys.stderr)
        return 2
    missing = [r.get('tc', '?') for r in results if r['state'] == 'Fail' and not evidence_img(a.run, r)]
    if missing:
        print(f'report: warning: no screenshot found for {", ".join(missing)}', file=sys.stderr)
    state = meta.get('State', '').strip('` ')
    if state and state.lower() != 'done':
        print(f'report: warning: run State is "{state}", not Done', file=sys.stderr)
    print(f"report: {out} · {len(results)} TC · " + ' · '.join(f'{s} {c[s]}' for s in STATES))
    return 0


if __name__ == '__main__':
    sys.exit(main())
