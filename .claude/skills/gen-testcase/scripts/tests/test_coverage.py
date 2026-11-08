"""Tests for gen-testcase coverage.py. Run from repo root:

python3 -m unittest discover -s .claude/skills/gen-testcase/scripts/tests -v
"""
import contextlib
import importlib.util
import io
import os
import re
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
spec = importlib.util.spec_from_file_location('coverage_mod', os.path.join(HERE, '..', 'coverage.py'))
cov = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cov)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


AC = read(os.path.join(ROOT, 'qa', 'specs', '_example', 'ac.md'))
TC = read(os.path.join(ROOT, 'qa', 'testcases', '_example', 'tc.md'))


def drop_tc(text, tc_id):
    """Remove one TC section."""
    return re.sub(rf'## {tc_id}:.*?(?=\n## )', '', text, flags=re.S)


class CoverageTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def go(self, ac=AC, tc=TC, *args):
        a, t = os.path.join(self.dir, 'ac.md'), os.path.join(self.dir, 'tc.md')
        for p, s in ((a, ac), (t, tc)):
            with open(p, 'w', encoding='utf-8') as f:
                f.write(s)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cov.main([a, t, *args])
        return code, out.getvalue(), err.getvalue()

    def test_golden_example_is_fully_covered(self):
        code, out, _ = self.go()
        self.assertEqual(code, 0, out)

    def test_summary_table_printed(self):
        _, out, _ = self.go(AC, TC, '--summary')
        self.assertIn('| Decision table | 3 | 3 | 100% |', out)

    def test_uncovered_ac_reported(self):
        code, out, _ = self.go(AC, drop_tc(TC, 'TC-USR-009'))
        self.assertEqual(code, 1)
        self.assertIn('AC-USR-006: no TC covers this AC', out)
        self.assertIn('ST-USR-01.T2: valid transition not covered', out)

    def test_uncovered_business_rule_and_dt_column(self):
        code, out, _ = self.go(AC, drop_tc(TC, 'TC-USR-008'))
        self.assertIn('BR-USR-001: no TC covers this business rule', out)
        self.assertIn('DT-USR-01.R3: decision table column not covered', out)

    def test_invalid_transition_required_for_critical_model(self):
        code, out, _ = self.go(AC, drop_tc(TC, 'TC-USR-011'))
        self.assertIn('ST-USR-01.T4: invalid (required for 🔴) transition not covered', out)

    def test_invalid_transition_optional_below_critical(self):
        ac = AC.replace('### ST-USR-01: Invitation lifecycle\n- Criticality: 🔴', '### ST-USR-01: Invitation lifecycle\n- Criticality: 🟠')
        code, out, _ = self.go(ac, drop_tc(TC, 'TC-USR-011'))
        self.assertNotIn('ST-USR-01.T4', out)

    def test_missing_ep_invalid_partition(self):
        tc = drop_tc(drop_tc(TC, 'TC-USR-002'), 'TC-USR-003')
        code, out, _ = self.go(AC, tc)
        self.assertIn('FLD-USR-01: no EP invalid partition covered', out)

    def test_bva_count_2_value(self):
        code, out, _ = self.go(AC, drop_tc(TC, 'TC-USR-006'))
        self.assertIn('FLD-USR-01: 3/4 BVA values (2-value, 2 boundaries)', out)

    def test_bva_count_3_value_for_critical_field(self):
        ac = AC.replace('| `local@domain.tld`, no spaces | 🟠 |', '| `local@domain.tld`, no spaces | 🔴 |')
        code, out, _ = self.go(ac, TC)
        self.assertIn('FLD-USR-01: 4/6 BVA values (3-value, 2 boundaries)', out)

    def test_unknown_id_reported(self):
        tc = TC.replace('`DT-USR-01.R2`', '`DT-USR-01.R9`')
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-007: cites DT-USR-01.R9, which is not in ac.md', out)

    def test_wrong_priority_reported(self):
        tc = TC.replace('| Technique | Decision table |\n| Coverage items | `AC-USR-003`, `BR-USR-002`, `DT-USR-01.R2` |\n| Role | Admin |\n| Type | Functional |\n| Priority | 🔴 |',
                        '| Technique | Decision table |\n| Coverage items | `AC-USR-003`, `BR-USR-002`, `DT-USR-01.R2` |\n| Role | Admin |\n| Type | Functional |\n| Priority | 🟡 |')
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-007: priority 🟡 should be 🔴', out)

    def test_blocked_by_answered_question(self):
        ac = AC.replace('| BA/PO | Open |', '| BA/PO | Answered |')
        code, out, _ = self.go(ac, TC)
        self.assertIn('TC-USR-010: OQ-USR-001 is answered; unblock this TC', out)

    def test_blocked_without_question(self):
        tc = TC.replace('| Blocked by | OQ-USR-001 |', '| Blocked by | — |', 1)
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-010: blocked without an open question', out)

    def test_deprecated_ac_not_required(self):
        head, tail = AC.split('### AC-USR-006', 1)
        ac = head + '### AC-USR-006' + tail.replace('- Status: Active', '- Status: Deprecated', 1)
        self.assertIn('- Status: Deprecated', ac)
        code, out, _ = self.go(ac, drop_tc(TC, 'TC-USR-009'))
        self.assertNotIn('AC-USR-006', out)

    def test_missing_file_exits_2(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cov.main([os.path.join(self.dir, 'nope.md'), os.path.join(self.dir, 'nope2.md')])
        self.assertEqual(code, 2)
        self.assertIn('cannot read', err.getvalue())

    def test_no_ac_sections_exits_2(self):
        code, _, err = self.go('# nothing\n', TC)
        self.assertEqual(code, 2)
        self.assertIn('no AC sections', err)

    def test_no_tc_sections_exits_2(self):
        code, _, err = self.go(AC, '# nothing\n')
        self.assertEqual(code, 2)
        self.assertIn('no TC sections', err)


if __name__ == '__main__':
    unittest.main()
