import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import graph  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))

MODEL = """# Model

## Features

| Code | Module | Depends on | Owner |
| --- | --- | --- | --- |
| AAA | M | — | qa |
| BBB | M | AAA | qa |
| CCC | M | BBB | qa |

## Entities

| Entity | Meaning | Owner | Scope |
| --- | --- | --- | --- |
| Order | x | AAA | Normal |
| User | x | — | Broad |

## Shared rules

| Rule ID | Rule | Criticality | Hubs | Status |
| --- | --- | --- | --- | --- |
| RULE-LIM-001 | limit | 🔴 | HUB-money | Active |
| RULE-OLD-001 | old | 🟡 | — | Deprecated |

## Impact hubs

| Hub ID | Applies when | Checklist |
| --- | --- | --- |
| HUB-money | money moves | totals match |

## Screens

| Screen ID | Name | Path | Roles |
| --- | --- | --- | --- |
| SCR-a | A | /a | Admin |
"""


def ac_file(code, jira, scenarios):
    out = [f'# AC: Feature {code} ({code})', '', '| Field | Value |', '| --- | --- |', f'| Jira | {jira} |', '',
           '## Scenarios', '']
    for aid, lines in scenarios:
        out += [f'### {aid}: title', '- Criticality: 🔴 Critical', '- Status: Active'] + lines + ['- Given: g', '']
    return '\n'.join(out)


def tc_file(rows):
    out = ['# TC: x', '']
    for tid, covers, screens in rows:
        out += [f'## {tid}: t', '| Field | Value |', '| --- | --- |', f'| Covers AC | {covers} |']
        if screens is not None:
            out.append(f'| Screens | {screens} |')
        out += ['| Priority | 🔴 |', '| Automation | `Candidate` |', '| Status | `Active` |', '']
    return '\n'.join(out)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, '.claude/rules'))
        self.write('.claude/rules/project.md', '# p\n')
        self.write('qa/traceability/model.md', MODEL)
        self.write('qa/specs/aaa/ac.md', ac_file('AAA', 'J-1', [
            ('AC-AAA-001', ['- Rules: RULE-LIM-001', '- Entities: Order, User']),
            ('AC-AAA-002', ['- Entities: Order']),
        ]))
        self.write('qa/specs/bbb/ac.md', ac_file('BBB', 'J-2', [
            ('AC-BBB-001', ['- Rules: RULE-LIM-001', '- Entities: Order']),
            ('AC-BBB-002', ['- Entities: Order', '- Hubs: HUB-money']),
        ]))
        self.write('qa/specs/ccc/ac.md', ac_file('CCC', 'J-3', [('AC-CCC-001', ['- Entities: User'])]))
        self.write('qa/testcases/aaa/tc.md', tc_file([('TC-AAA-001', 'AC-AAA-001', 'SCR-a'),
                                                       ('TC-AAA-002', 'AC-AAA-002', 'SCR-a')]))
        self.write('qa/testcases/bbb/tc.md', tc_file([('TC-BBB-001', 'AC-BBB-001', 'SCR-a'),
                                                       ('TC-BBB-002', 'AC-BBB-002', 'SCR-a')]))
        self.write('qa/testcases/ccc/tc.md', tc_file([('TC-CCC-001', 'AC-CCC-001', '—')]))

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, rel, text):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)

    def g(self):
        return graph.load(self.root)

    def ids(self, rows, kind):
        return {r['id'] for r in rows if r['kind'] == kind}


class TestCheck(Fixture):
    def test_clean_fixture(self):
        errors, warnings = graph.check(self.g())
        self.assertEqual(errors, [])

    def test_unknown_references_are_errors(self):
        self.write('qa/specs/ccc/ac.md', ac_file('CCC', 'J-3', [
            ('AC-CCC-001', ['- Rules: RULE-NOP-001', '- Entities: Ghost', '- Hubs: HUB-none'])]))
        self.write('qa/testcases/ccc/tc.md', tc_file([('TC-CCC-001', 'AC-CCC-009', 'SCR-zz')]))
        errors, _ = graph.check(self.g())
        text = '\n'.join(errors)
        for needle in ('unknown rule RULE-NOP-001', 'unknown entity Ghost', 'unknown hub HUB-none',
                       'covers unknown AC-CCC-009', 'unknown screen SCR-zz'):
            self.assertIn(needle, text)

    def test_deprecated_rule_and_unknown_feature(self):
        self.write('qa/specs/ddd/ac.md', ac_file('DDD', 'J-4', [('AC-DDD-001', ['- Rules: RULE-OLD-001'])]))
        errors, _ = graph.check(self.g())
        text = '\n'.join(errors)
        self.assertIn('uses deprecated rule RULE-OLD-001', text)
        self.assertIn('feature DDD is not in model.md', text)

    def test_warnings(self):
        self.write('qa/specs/ccc/ac.md', ac_file('CCC', 'J-3', [
            ('AC-CCC-001', []), ('AC-CCC-002', ['- Entities: User'])]))
        self.write('qa/testcases/ccc/tc.md', tc_file([('TC-CCC-001', 'AC-CCC-001', None)]))
        _, warnings = graph.check(self.g())
        text = '\n'.join(warnings)
        self.assertIn('AC-CCC-001: no Rules, Entities or Hubs line', text)
        self.assertIn('TC-CCC-001: no Screens row', text)

    def test_cycle_warning(self):
        self.write('qa/traceability/model.md', MODEL.replace('| AAA | M | — | qa |', '| AAA | M | CCC | qa |'))
        _, warnings = graph.check(self.g())
        self.assertTrue(any('dependency cycle' in w for w in warnings))

    def test_duplicate_ids(self):
        self.write('qa/specs/eee/ac.md', ac_file('AAA', 'J-9', [('AC-AAA-001', ['- Entities: Order'])]))
        errors, _ = graph.check(self.g())
        self.assertTrue(any('duplicate AC-AAA-001' in e for e in errors))


class TestImpact(Fixture):
    def test_owner_change_reaches_readers(self):
        rows, notes, _ = graph.impact(self.g(), ['AC-AAA-002'])
        self.assertEqual(self.ids(rows, 'AC'), {'AC-AAA-002', 'AC-BBB-001', 'AC-BBB-002'})
        self.assertIn('HUB-money', self.ids(rows, 'Hub'))
        self.assertNotIn('AC-AAA-001', self.ids(rows, 'AC'), 'same feature is not re-entered')

    def test_reader_change_does_not_reach_owner(self):
        rows, _, _ = graph.impact(self.g(), ['AC-BBB-002'])
        self.assertEqual(self.ids(rows, 'AC'), {'AC-BBB-002'})
        self.assertIn('CCC', self.ids(rows, 'Feature'), 'CCC depends on BBB')

    def test_shared_rule_crosses_features_and_broad_is_not_expanded(self):
        rows, notes, _ = graph.impact(self.g(), ['AC-AAA-001'])
        self.assertIn('AC-BBB-001', self.ids(rows, 'AC'))
        self.assertNotIn('AC-CCC-001', self.ids(rows, 'AC'))
        self.assertTrue(any('User (Broad)' in n for n in notes))

    def test_rule_start(self):
        rows, _, _ = graph.impact(self.g(), ['RULE-LIM-001'])
        self.assertEqual(self.ids(rows, 'AC'), {'AC-AAA-001', 'AC-BBB-001'})
        self.assertIn('HUB-money', self.ids(rows, 'Hub'))

    def test_screen_start_has_no_business_propagation(self):
        rows, _, _ = graph.impact(self.g(), ['SCR-a'])
        self.assertEqual(self.ids(rows, 'TC'), {'TC-AAA-001', 'TC-AAA-002', 'TC-BBB-001', 'TC-BBB-002'})
        self.assertNotIn('AC-CCC-001', self.ids(rows, 'AC'))

    def test_jira_key_and_feature(self):
        rows, _, _ = graph.impact(self.g(), ['J-1'])
        self.assertTrue({'AC-AAA-001', 'AC-AAA-002'} <= self.ids(rows, 'AC'))
        rows2, _, _ = graph.impact(self.g(), ['AAA'])
        self.assertEqual(self.ids(rows, 'AC'), self.ids(rows2, 'AC'))

    def test_order_and_unknown(self):
        rows, _, _ = graph.impact(self.g(), ['AC-AAA-002'])
        self.assertEqual(rows[0]['id'], 'AC-AAA-002')
        self.assertEqual([r['dist'] for r in rows], sorted(r['dist'] for r in rows))
        with self.assertRaises(graph.FormatError):
            graph.impact(self.g(), ['NOPE-1'])

    def test_gaps(self):
        self.write('qa/testcases/bbb/tc.md', tc_file([('TC-BBB-001', 'AC-BBB-001', 'SCR-a')]))
        _, _, gaps = graph.impact(self.g(), ['AC-AAA-002'])
        self.assertIn('AC-BBB-002: no TC', gaps)


class TestOutputs(Fixture):
    def test_matrix_keeps_auto_script_and_feature_links(self):
        self.write(graph.MATRIX, '| Ticket | Feature | AC | Auto script |\n| --- | --- | --- | --- |\n'
                                 '| J-1 | AAA | AC-AAA-001 | tests/a_spec.rb |\n')
        text = graph.matrix(self.g(), os.path.join(self.root, graph.MATRIX))
        self.assertIn('tests/a_spec.rb |', text)
        self.assertIn('| BBB | AAA | CCC | AAA |', text)

    def test_view_mermaid(self):
        out = graph.view(self.g(), 'BBB', 1, mermaid=True)
        self.assertIn('BBB -->|depends_on| AAA', out)

    def test_cli_matrix_check(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(graph.main(['--root', self.root, 'matrix', '--write']), 0)
            self.assertEqual(graph.main(['--root', self.root, 'matrix', '--check']), 0)
        self.write('qa/specs/ccc/ac.md', ac_file('CCC', 'J-3', [('AC-CCC-002', ['- Entities: User'])]))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(graph.main(['--root', self.root, 'matrix', '--check']), 1)


class TestGoldenExample(unittest.TestCase):
    def test_example_is_clean(self):
        g = graph.load(ROOT, example=True)
        errors, warnings = graph.check(g)
        self.assertEqual((errors, warnings), ([], []))

    def test_example_impact(self):
        g = graph.load(ROOT, example=True)
        rows, _, _ = graph.impact(g, ['AC-USR-006'])
        acs = {r['id'] for r in rows if r['kind'] == 'AC'}
        self.assertEqual(acs, {'AC-USR-006', 'AC-SGN-001', 'AC-SGN-002', 'AC-SGN-003'})

    def test_project_matrix_is_current(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(graph.main(['--root', ROOT, 'matrix', '--check']), 0)


if __name__ == '__main__':
    unittest.main()
