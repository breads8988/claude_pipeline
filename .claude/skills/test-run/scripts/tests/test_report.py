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
    | TC-USR-001 | Invite valid email | Admin | 🔴 | ✅ Pass | — | — | |
    | TC-USR-002 | Reject duplicate | Admin | 🔴 | ❌ Fail | BUG-TBD | TC-USR-002.png | no error displayed |
    | TC-USR-003 | Viewer hidden button | Viewer | 🟠 | ✅ Pass | — | — | |
    | TC-USR-004 | Link expiry | Admin | 🟡 | ⛔ Blocked | — | — | OQ-USR-001 |
    | TC-USR-005 | <script>x</script> | Admin | ⚪ | ⬜ | | | |

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

    def test_critical_passes_listed_for_recheck(self):
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

    def test_missing_screenshot_warned(self):
        os.remove(os.path.join(self.dir, '2026-11-08-invite-2.4.1', 'evidence', 'TC-USR-002.png'))
        code, _, err, _ = self.go()
        self.assertEqual(code, 0)
        self.assertIn('no screenshot found for TC-USR-002', err)

    def test_repo_relative_evidence_path(self):
        repo = os.path.join(self.dir, 'repo')
        runs = os.path.join(repo, 'qa', 'runs')
        ev = os.path.join(runs, 'r1', 'evidence')
        os.makedirs(ev)
        with open(os.path.join(ev, 'shot1.png'), 'wb') as f:
            f.write(PNG)
        run = os.path.join(runs, 'r1.md')
        with open(run, 'w', encoding='utf-8') as f:
            f.write(RUN.replace('| TC-USR-002.png |', '| qa/runs/r1/evidence/shot1.png |'))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = report.main([run, '--out', self.out])
        with open(self.out, encoding='utf-8') as f:
            html = f.read()
        self.assertEqual(code, 0, err.getvalue())
        self.assertIn('data:image/png;base64,', html)

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


    # robustness (review 2026-11-08)
    def write_run(self, text, name='2026-11-08-invite-2.4.1.md', raw=False):
        path = os.path.join(self.dir, name)
        with open(path, 'wb' if raw else 'w', **({} if raw else {'encoding': 'utf-8', 'newline': ''})) as f:
            f.write(text)
        return path

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = report.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_escaped_pipe_in_title(self):
        self.write_run(RUN.replace('| Invite valid email |', '| Invite a\\|b |'))
        code, _, _, html = self.go()
        self.assertEqual(code, 0)
        self.assertIn('Invite a|b', html)

    def test_pipe_inside_code_span_in_note(self):
        self.write_run(RUN.replace('| no error displayed |', '| `a | b` not displayed |'))
        code, _, _, html = self.go()
        self.assertEqual(code, 0)
        self.assertIn('<code>a | b</code>', html)

    def test_out_is_directory_exits_2(self):
        os.makedirs(os.path.join(self.dir, 'adir'))
        code, _, err = self.run_main(self.run, '--out', os.path.join(self.dir, 'adir'))
        self.assertEqual(code, 2)
        self.assertIn('is a directory', err)

    def test_non_utf8_exits_2(self):
        self.write_run(b'\xff\xfe bad', raw=True)
        code, _, err, _ = self.go()
        self.assertEqual(code, 2)

    def test_result_must_be_exact(self):
        self.write_run(RUN.replace('✅ Pass | — | — | |\n| TC-USR-002', 'Passed with notes | — | — | |\n| TC-USR-002'))
        code, _, err, _ = self.go()
        self.assertEqual(code, 2)
        self.assertIn('unknown result', err)

    def test_word_results_and_variation_selector(self):
        self.write_run(RUN.replace('| ✅ Pass | — | — | |\n| TC-USR-002', '| Pass | — | — | |\n| TC-USR-002')
                       .replace('| ⬜ |', '| ⏭\ufe0f Skip |'))
        code, out, _, _ = self.go()
        self.assertEqual(code, 0)
        self.assertIn('Skip 1', out)

    def test_default_out_under_runs_goes_to_reports(self):
        runs = os.path.join(self.dir, 'qa', 'runs')
        os.makedirs(runs)
        path = os.path.join(runs, 'r.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(RUN)
        cwd = os.getcwd()
        os.chdir(self.dir)
        try:
            code, out, _ = self.run_main(path)
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 0)
        self.assertTrue(os.path.isfile(os.path.join(self.dir, 'qa', 'reports', 'r.html')))

    def test_default_out_elsewhere_is_next_to_run(self):
        code, _, _ = self.run_main(self.run)
        self.assertEqual(code, 0)
        self.assertTrue(os.path.isfile(os.path.join(self.dir, '2026-11-08-invite-2.4.1.html')))

    def test_evidence_from_cell_path(self):
        os.remove(os.path.join(self.dir, '2026-11-08-invite-2.4.1', 'evidence', 'TC-USR-002.png'))
        shot = os.path.join(self.dir, 'saved-by-browser.png')
        with open(shot, 'wb') as f:
            f.write(PNG)
        self.write_run(RUN.replace('| TC-USR-002.png |', f'| {shot} |'))
        _, _, _, html = self.go()
        self.assertIn('data:image/png;base64,', html)

    def test_evidence_ignores_unsafe_tc_value(self):
        secret = os.path.join(self.dir, 'secret.png')
        with open(secret, 'wb') as f:
            f.write(PNG)
        self.write_run(RUN.replace('| TC-USR-002 | Reject duplicate', '| ../../secret | Reject duplicate').replace('| TC-USR-002.png |', '| — |'))
        _, _, _, html = self.go()
        self.assertNotIn('data:image/png', html)

    def test_state_warning(self):
        self.write_run(RUN.replace('| State | `Done` |', '| State | `In progress` |'))
        code, _, err, _ = self.go()
        self.assertEqual(code, 0)
        self.assertIn('not Done', err)

    def test_summary_heading_without_table(self):
        text = RUN[:RUN.index('## Summary')] + '## Summary\n\nTBD\n'
        self.write_run(text)
        self.go()
        md = read(self.run)
        self.assertEqual(md.count('## Summary'), 1)
        self.assertIn('| 5 | 2 | 1 | 1 | 0 | 1 |', md)

    def test_crlf_preserved_and_idempotent(self):
        self.write_run(RUN.replace('\n', '\r\n'))
        self.go()
        first = open(self.run, 'rb').read()
        self.go()
        second = open(self.run, 'rb').read()
        self.assertIn(b'\r\n', first)
        self.assertEqual(first, second)

    def test_bom_title(self):
        self.write_run('\ufeff' + RUN)
        _, _, _, html = self.go()
        self.assertIn('<title>Run: invite', html)

    def test_hash_in_title_kept(self):
        self.write_run(RUN.replace('# Run: invite', '# #123 hotfix run'))
        _, _, _, html = self.go()
        self.assertIn('<title>#123 hotfix run', html)


if __name__ == '__main__':
    unittest.main()
