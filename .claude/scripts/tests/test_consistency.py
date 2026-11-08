"""Tests for consistency.py. Run: python3 -m unittest discover -s .claude/scripts/tests"""
import contextlib
import importlib.util
import io
import os
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
spec = importlib.util.spec_from_file_location('consistency', os.path.join(HERE, '..', 'consistency.py'))
cons = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cons)


class ConsistencyTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        for rel in ('.claude/rules/project.md', '.claude/rules/naming.md',
                    '.claude/skills/comment-style/references/notifications.md',
                    'qa/_templates/test-accounts.local.md', 'docs/plan-ui-interaction.md'):
            os.makedirs(os.path.join(self.dir, os.path.dirname(rel)), exist_ok=True)
            shutil.copy(os.path.join(ROOT, rel), os.path.join(self.dir, rel))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, rel, text):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)

    def go(self, root=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cons.main([root or self.dir])
        return code, out.getvalue() + err.getvalue()

    def test_real_repo_is_clean(self):
        code, out = self.go(ROOT)
        self.assertEqual(code, 0, out)

    def test_restated_priority_rule(self):
        self.write('.claude/agents/x.md', '- Priority = highest criticality among its items.\n')
        code, out = self.go()
        self.assertEqual(code, 1)
        self.assertIn('TC priority rule restated', out)

    def test_stale_terms(self):
        self.write('qa/x.md', 'Priority P1\nState: Running\n| Invitee (no login) |\nsee **Run finished** notification\n')
        code, out = self.go()
        for msg in ('P1–P3', 'In progress', 'Anonymous', 'retired notification'):
            self.assertIn(msg, out)

    def test_retired_mention_allowed(self):
        self.write('docs/plan-x.md', '`P1`–`P3` is retired everywhere.\n')
        code, out = self.go()
        self.assertEqual(code, 0, out)

    def test_bad_frontmatter(self):
        self.write('.claude/commands/x.md', '---\nargument-hint: [a] b\n---\nbody\n')
        code, out = self.go()
        self.assertIn('frontmatter is not valid YAML', out)

    def test_unknown_project_field(self):
        self.write('.claude/agents/x.md', 'Read `project.md` › Secret hosts.\n')
        code, out = self.go()
        self.assertIn('project.md has no field "Secret hosts"', out)

    def test_known_project_field(self):
        self.write('.claude/agents/x.md', 'Read `project.md` › Allowed hosts and more.\n')
        code, out = self.go()
        self.assertEqual(code, 0, out)

    def test_missing_path(self):
        self.write('.claude/agents/x.md', 'See `.claude/skills/nope/SKILL.md`.\n')
        code, out = self.go()
        self.assertIn('path `.claude/skills/nope/SKILL.md` does not exist', out)

    def test_placeholder_path_skipped(self):
        self.write('.claude/agents/x.md', 'See `docs/<feature>.md`.\n')
        code, out = self.go()
        self.assertEqual(code, 0, out)

    def test_unknown_notification(self):
        self.write('.claude/agents/x.md', 'Send the **Lint exploded** notification.\n')
        code, out = self.go()
        self.assertIn('notification "Lint exploded" is not an event', out)

    def test_history_files_skipped(self):
        self.write('docs/review-2026-01-01.md', 'P1 and State: Running\n')
        code, out = self.go()
        self.assertEqual(code, 0, out)

    def test_not_repo_root_exits_2(self):
        code, out = self.go(tempfile.gettempdir())
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
