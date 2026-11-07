"""Tests for test-run report.py. Run from repo root:

python3 -m unittest discover -s .claude/skills/test-run/scripts/tests -v
"""
import base64
import contextlib
import importlib.util
import io
import os
import shutil
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('report', os.path.join(HERE, '..', 'report.py'))
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)

PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')

RUN = textwrap.dedent('''\
    # Run: invite · build 2.4.1 · smoke · 2026-11-08

    | Field | Value |
    | --- | --- |
    | Feature | invite (USR) |
    | Build | 2.4.1 |
    | State | `Done` |

    ## Results

    | TC | Title | Role | Pri | Result | Bug | Evidence | Note |
    | --- | --- | --- | --- | --- | --- | --- | --- |
    | TC-USR-001 | Invite valid email | Admin | P1 | ✅ Pass | — | — | |
    | TC-USR-002 | Reject duplicate | Admin | P1 | ❌ Fail | BUG-TBD | TC-USR-002.png | no error displayed |
    | TC-USR-003 | Viewer hidden button | Viewer | P2 | ✅ Pass | — | — | |
    | TC-USR-004 | Link expiry | Admin | P2 | ⛔ Blocked | — | — | OQ-USR-001 |
    | TC-USR-005 | <script>x</script> | Admin | P3 | ⬜ | | | |

    ## Summary
    | Total | Pass | Fail | Blocked | Skip | Not run |
    | --- | --- | --- | --- | --- | --- |
    | 0 | 0 | 0 | 0 | 0 | 0 |
    ''')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.run = os.path.join(self.dir, '2026-11-08-invite-2.4.1.md')
        with open(self.run, 'w', encoding='utf-8') as f:
            f.write(RUN)
        ev = os.path.join(self.dir, '2026-11-08-invite-2.4.1', 'evidence')
        os.makedirs(ev)
        for tc in ('TC-USR-001', 'TC-USR-002'):
            with open(os.path.join(ev, f'{tc}.png'), 'wb') as f:
                f.write(PNG)
        self.out = os.path.join(self.dir, 'out', 'report.html')

    def tearDown(self):
        shutil.rmtree(self.dir)

    def go(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = report.main([self.run, '--out', self.out, *args])
        html = read(self.out) if os.path.exists(self.out) else ''
        return code, out.getvalue(), err.getvalue(), html

    def test_writes_report_and_counts(self):
        code, out, _, html = self.go()
        self.assertEqual(code, 0)
        self.assertIn('Pass 2 · Fail 1 · Blocked 1 · Skip 0 · Not run 1', out)
        self.assertIn('<title>Run: invite', html)

    def test_screenshot_embedded_for_fail_only(self):
        _, _, _, html = self.go()
        self.assertEqual(html.count('data:image/png;base64,'), 1)
        self.assertIn('Screenshot for TC-USR-002', html)

    def test_fail_listed_first(self):
        _, _, _, html = self.go()
        self.assertLess(html.index('TC-USR-002'), html.index('TC-USR-001'))

    def test_p1_passes_listed_for_recheck(self):
        _, _, _, html = self.go()
        section = html[html.index('Optional re-check'):]
        self.assertIn('TC-USR-001', section)
        self.assertNotIn('TC-USR-003', section)

    def test_html_escaped(self):
        _, _, _, html = self.go()
        self.assertNotIn('<script>x</script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_summary_rewritten_in_run_file(self):
        self.go()
        md = read(self.run)
        self.assertIn('| 5 | 2 | 1 | 1 | 0 | 1 |', md)
        self.assertEqual(md.count('## Summary'), 1)

    def test_no_update_leaves_run_file(self):
        self.go('--no-update')
        self.assertIn('| 0 | 0 | 0 | 0 | 0 | 0 |', read(self.run))

    def test_missing_screenshot_noted(self):
        os.remove(os.path.join(self.dir, '2026-11-08-invite-2.4.1', 'evidence', 'TC-USR-002.png'))
        _, _, _, html = self.go()
        self.assertIn('No screenshot', html)
        self.assertNotIn('data:image/png', html)

    def test_missing_run_file_exits_2(self):
        os.remove(self.run)
        code, _, err, _ = self.go()
        self.assertEqual(code, 2)
        self.assertIn('cannot read', err)

    def test_no_results_table_exits_2(self):
        with open(self.run, 'w', encoding='utf-8') as f:
            f.write('# Run\n\nnothing\n')
        code, _, err, _ = self.go()
        self.assertEqual(code, 2)
        self.assertIn('no Results table', err)

    def test_unknown_result_exits_2(self):
        with open(self.run, 'w', encoding='utf-8') as f:
            f.write(RUN.replace('✅ Pass | — | — | |\n| TC-USR-002', 'Maybe | — | — | |\n| TC-USR-002'))
        code, _, err, _ = self.go()
        self.assertEqual(code, 2)
        self.assertIn('unknown result', err)


if __name__ == '__main__':
    unittest.main()
