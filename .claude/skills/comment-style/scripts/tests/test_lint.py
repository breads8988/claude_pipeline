"""Tests for comment-style lint.py. Run from repo root:

python3 -m unittest discover -s .claude/skills/comment-style/scripts/tests -v
"""
import contextlib
import importlib.util
import io
import os
import shutil
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lint', os.path.join(HERE, '..', 'lint.py'))
lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)

VOCAB = textwrap.dedent('''\
    # Test vocabulary

    | Banned | Use | Level | Example |
    |---|---|---|---|
    | shown, shows | displayed | error | |
    | still | remains | warn | |
    | the one | the named record | error | |
    | no … changes | no side effects | error | |
    | /(?:^\\s*(?:\\d+\\.\\s+\\|[-*]\\s+)?\\|\\x7c\\s*)Open\\s+(?=[A-Z])/ (Open <Page>) | navigate to | error | |
    ''')


class LintTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.dir)
        self.vocab = self.write('vocab.md', VOCAB)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.dir)

    def write(self, name, text):
        path = os.path.join(self.dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent(text))
        return path

    def run_lint(self, page_text, *extra, shared=None):
        page = self.write('page.md', page_text)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lint.main([page, '--shared', shared or self.vocab, *extra])
        return code, out.getvalue(), err.getvalue()

    # matching
    def test_clean_page_exits_0(self):
        code, out, _ = self.run_lint('The Retry button is displayed.\n')
        self.assertEqual(code, 0)
        self.assertIn('0 error(s), 0 warning(s)', out)

    def test_error_word_exits_1_with_line_and_use(self):
        code, out, _ = self.run_lint('line one\nThe button is shown.\n')
        self.assertEqual(code, 1)
        self.assertIn('page.md:2: error: "shown" → displayed', out)

    def test_case_insensitive(self):
        code, _, _ = self.run_lint('Shows the toast.\n')
        self.assertEqual(code, 1)

    def test_warn_only_exits_0(self):
        code, out, _ = self.run_lint('The error state is still displayed.\n')
        self.assertEqual(code, 0)
        self.assertIn('warn: "still"', out)

    def test_ellipsis_matches_one_word(self):
        code, out, _ = self.run_lint('no balance changes.\n')
        self.assertEqual(code, 1)
        self.assertIn('"no balance changes"', out)

    def test_multiword_spans_whitespace(self):
        code, _, _ = self.run_lint('pick the  one option\n')
        self.assertEqual(code, 1)

    # regex rows
    def test_regex_open_at_step_start(self):
        code, _, _ = self.run_lint('1. Open Settings.\n')
        self.assertEqual(code, 1)

    def test_regex_open_in_table_cell(self):
        code, _, _ = self.run_lint('| x | y |\n|---|---|\n| 1 | Open Settings |\n')
        self.assertEqual(code, 1)

    def test_regex_open_as_status_not_hit(self):
        code, _, _ = self.run_lint('status = open\n| 1 | Open |\n')
        self.assertEqual(code, 0)

    # exemptions
    def test_backticks_and_double_quotes_skipped(self):
        code, _, _ = self.run_lint('The `Shown` label and "shows more" copy are displayed.\n')
        self.assertEqual(code, 0)

    def test_smart_quotes_skipped(self):
        code, _, _ = self.run_lint('The “shown items” copy is displayed.\n')
        self.assertEqual(code, 0)

    def test_fenced_code_skipped(self):
        code, _, _ = self.run_lint('```\nshown\n```\n~~~\nshows\n~~~\n')
        self.assertEqual(code, 0)

    def test_table_header_and_separator_skipped(self):
        code, _, _ = self.run_lint('| Shown | Still |\n|---|---|\n| a | b |\n')
        self.assertEqual(code, 0)

    def test_front_matter_skipped(self):
        code, _, _ = self.run_lint('---\ntitle: shown\n---\nok\n')
        self.assertEqual(code, 0)

    def test_all_caps_skipped(self):
        code, _, _ = self.run_lint('SHOWN ITEMS heading\n')
        self.assertEqual(code, 0)

    # false positives
    def test_hyphenated_word_not_hit(self):
        code, _, _ = self.run_lint('Enter the one-time code.\n')
        self.assertEqual(code, 0)

    def test_substring_not_hit(self):
        code, _, _ = self.run_lint('The showroom and stillness are displayed.\n')
        self.assertEqual(code, 0)

    def test_placeholder_not_hit(self):
        code, _, _ = self.run_lint('<shown> placeholder\n')
        self.assertEqual(code, 0)

    # project vocabulary
    def test_project_file_adds_word(self):
        self.write('.claude/rules/vocabulary.project.md',
                   '| Banned | Use |\n|---|---|\n| credited | posted |\n')
        code, out, _ = self.run_lint('Amount credited.\n')
        self.assertEqual(code, 1)
        self.assertIn('posted', out)

    def test_project_file_overrides_level(self):
        self.write('.claude/rules/vocabulary.project.md',
                   '| Banned | Use | Level |\n|---|---|---|\n| shown | displayed | warn |\n')
        code, _, _ = self.run_lint('The button is shown.\n')
        self.assertEqual(code, 0)

    def test_project_file_allow_removes_word(self):
        self.write('.claude/rules/vocabulary.project.md',
                   '| Allow | Reason |\n|---|---|\n| shown, shows | domain term |\n')
        code, _, _ = self.run_lint('The button is shown and shows a badge.\n')
        self.assertEqual(code, 0)

    def test_no_project_flag_ignores_project_file(self):
        self.write('.claude/rules/vocabulary.project.md',
                   '| Allow | Reason |\n|---|---|\n| shown | x |\n')
        code, _, _ = self.run_lint('The button is shown.\n', '--no-project')
        self.assertEqual(code, 1)

    def test_extra_vocab_flag(self):
        extra = self.write('extra.md', '| Banned | Use |\n|---|---|\n| fires | is sent |\n')
        code, _, _ = self.run_lint('The event fires.\n', '--vocab', extra)
        self.assertEqual(code, 1)

    # configuration and errors
    def test_missing_page_exits_2(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lint.main([os.path.join(self.dir, 'nope.md'), '--shared', self.vocab])
        self.assertEqual(code, 2)
        self.assertIn('cannot read', err.getvalue())

    def test_missing_vocab_exits_2(self):
        code, _, err = self.run_lint('ok\n', shared=os.path.join(self.dir, 'nope.md'))
        self.assertEqual(code, 2)

    def test_vocab_without_banned_table_exits_2(self):
        bad = self.write('bad.md', '# nothing here\n')
        code, _, err = self.run_lint('ok\n', shared=bad)
        self.assertEqual(code, 2)
        self.assertIn('no Banned table', err)

    def test_bad_level_exits_2(self):
        bad = self.write('bad.md', '| Banned | Use | Level |\n|---|---|---|\n| x | y | fatal |\n')
        code, _, err = self.run_lint('ok\n', shared=bad)
        self.assertEqual(code, 2)
        self.assertIn('Level must be', err)

    def test_bad_regex_exits_2(self):
        bad = self.write('bad.md', '| Banned | Use |\n|---|---|\n| /(unclosed/ | y |\n')
        code, _, err = self.run_lint('ok\n', shared=bad)
        self.assertEqual(code, 2)

    def test_empty_use_exits_2(self):
        bad = self.write('bad.md', '| Banned | Use |\n|---|---|\n| x |  |\n')
        code, _, err = self.run_lint('ok\n', shared=bad)
        self.assertEqual(code, 2)

    # shared vocabulary sanity
    def test_shared_vocabulary_loads(self):
        rules, allow = {}, set()
        lint.load_vocab(lint.SHARED_DEFAULT, rules, allow, require_banned=True)
        self.assertGreater(len(rules), 60)
        self.assertTrue(any(k.startswith('re:') for k in rules))


    # review 2026-11-08
    def test_open_with_backticked_page(self):
        code, _, _ = self.run_lint('1. Open `Settings` › `Users`.\n')
        self.assertEqual(code, 1)

    def test_open_at_bullet_start(self):
        code, _, _ = self.run_lint('- Open Settings page.\n')
        self.assertEqual(code, 1)

    def test_quoted_span_does_not_join_words(self):
        code, out, _ = self.run_lint('Select the `Primary` one.\n')
        self.assertNotIn('the one', out.lower().replace('"the one" →', ''))
        self.assertEqual(code, 0)

    def test_ellipsis_rule_across_quoted_span(self):
        code, out, _ = self.run_lint('no `Invoice` changes\n')
        self.assertEqual(code, 1)

    def test_bom_and_front_matter(self):
        code, _, _ = self.run_lint('\ufeff---\ntitle: shown\n---\nok\n')
        self.assertEqual(code, 0)

    def test_unclosed_front_matter_is_linted(self):
        code, _, _ = self.run_lint('---\nThe button is shown.\n')
        self.assertEqual(code, 1)

    def test_non_utf8_page_exits_2(self):
        page = os.path.join(self.dir, 'bad.md')
        with open(page, 'wb') as f:
            f.write(b'\xff\xfe bad')
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lint.main([page, '--shared', self.vocab])
        self.assertEqual(code, 2)

    def test_mixed_fence_markers(self):
        code, _, _ = self.run_lint('```\n~~~\n```\nshown\n')
        self.assertEqual(code, 1)

    def test_inch_mark_is_not_a_quote(self):
        code, _, _ = self.run_lint('The 5" screen shows a toast and "x".\n')
        self.assertEqual(code, 1)

    def test_overlapping_hits_counted_once(self):
        extra = self.write('extra.md', '| Banned | Use |\n|---|---|\n| not shown | hidden |\n')
        code, out, _ = self.run_lint('The column is not shown.\n', '--vocab', extra)
        self.assertIn('1 error(s)', out)

    def test_urls_and_comments_ignored(self):
        code, _, _ = self.run_lint('[spec](https://x.test/shows/1) <!-- shown -->\n')
        self.assertEqual(code, 0)

    def test_comma_inside_note(self):
        extra = self.write('extra.md', '| Banned | Use |\n|---|---|\n| fires (in UI, not API) | is sent |\n')
        code, out, _ = self.run_lint('not API) here\n', '--vocab', extra)
        self.assertEqual(code, 0)

    def test_regex_rule_matches_acronym(self):
        extra = self.write('extra.md', '| Banned | Use |\n|---|---|\n| /TODO/ | remove |\n')
        code, _, _ = self.run_lint('TODO fix\n', '--vocab', extra)
        self.assertEqual(code, 1)

    def test_short_separator_row(self):
        code, _, _ = self.run_lint('| Shown | Still |\n|-|-|\n| a | b |\n')
        self.assertEqual(code, 0)

    def test_project_vocab_found_from_page_folder(self):
        proj = os.path.join(self.dir, 'other')
        os.makedirs(os.path.join(proj, '.claude', 'rules'))
        with open(os.path.join(proj, '.claude', 'rules', 'vocabulary.project.md'), 'w', encoding='utf-8') as f:
            f.write('| Allow | Reason |\n|---|---|\n| shown | x |\n')
        page = os.path.join(proj, 'page.md')
        with open(page, 'w', encoding='utf-8') as f:
            f.write('The button is shown.\n')
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lint.main([page, '--shared', self.vocab])
        self.assertEqual(code, 0, out.getvalue())


if __name__ == '__main__':
    unittest.main()
