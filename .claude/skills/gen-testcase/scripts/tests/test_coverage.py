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
    out = re.sub(rf'## {tc_id}:.*?(?=\n## )', '', text, flags=re.S)
    assert out != text, tc_id
    return out


def section(text, tc_id):
    return re.search(rf'## {tc_id}:.*?(?=\n## )', text, flags=re.S).group(0)


def sub(text, old, new, count=1):
    assert old in text, old
    return text.replace(old, new, count)


class CoverageTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def go(self, ac=AC, tc=TC, *args, raw=False):
        a, t = os.path.join(self.dir, 'ac.md'), os.path.join(self.dir, 'tc.md')
        for p, s in ((a, ac), (t, tc)):
            mode = 'wb' if raw else 'w'
            with open(p, mode, **({} if raw else {'encoding': 'utf-8'})) as f:
                f.write(s)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cov.main([a, t, *args])
        return code, out.getvalue(), err.getvalue()

    # baseline
    def test_golden_example_passes(self):
        code, out, _ = self.go()
        self.assertEqual(code, 0, out)
        self.assertIn('4 item(s) blocked', out)

    def test_summary_table_has_blocked_column(self):
        code, out, _ = self.go(AC, TC, '--summary')
        self.assertEqual(code, 0, out)
        self.assertIn('| State transition | 9 | 6 | 3 | 66% |', out)
        self.assertIn('| Scenario (AC) | 10 | 9 | 1 | 90% |', out)

    # missing coverage
    def test_uncovered_ac_and_valid_transition(self):
        code, out, _ = self.go(AC, drop_tc(TC, 'TC-USR-015'))
        self.assertEqual(code, 1)
        self.assertIn('AC-USR-006: no TC covers this AC', out)
        self.assertIn('ST-USR-01.T2: valid transition not covered', out)

    def test_uncovered_business_rule_and_dt_column(self):
        code, out, _ = self.go(AC, drop_tc(TC, 'TC-USR-012'))
        self.assertEqual(code, 1)
        self.assertIn('BR-USR-001: no TC covers this business rule', out)
        self.assertIn('DT-USR-01.R3: decision table column not covered', out)

    def test_invalid_transition_required_for_critical_model(self):
        code, out, _ = self.go(AC, drop_tc(TC, 'TC-USR-018'))
        self.assertEqual(code, 1)
        self.assertIn('ST-USR-01.T4: invalid (required for 🔴) transition not covered', out)

    def test_invalid_transition_optional_below_critical(self):
        ac = sub(AC, '### ST-USR-01: Invitation lifecycle\n- Criticality: 🔴', '### ST-USR-01: Invitation lifecycle\n- Criticality: 🟠')
        code, out, _ = self.go(ac, drop_tc(TC, 'TC-USR-018'))
        self.assertNotIn('ST-USR-01.T4', out)

    # EP
    def test_ep_partition_not_covered(self):
        code, out, _ = self.go(AC, drop_tc(TC, 'TC-USR-006'))
        self.assertEqual(code, 1)
        self.assertIn('FLD-USR-01: EP partition "two @" not covered', out)

    def test_ep_partition_not_in_analysis_table(self):
        tc = sub(TC, '`FLD-USR-01 EP: two @`', '`FLD-USR-01 EP: three @`')
        code, out, _ = self.go(AC, tc)
        self.assertIn('EP partition "three @" of FLD-USR-01 is not in the Test analysis table', out)

    def test_ep_label_with_comma_kept_whole(self):
        tc = TC.replace('| FLD-USR-01 | two @ |', '| FLD-USR-01 | two @, adjacent |').replace('`FLD-USR-01 EP: two @`', '`FLD-USR-01 EP: two @, adjacent`')
        code, out, _ = self.go(AC, tc)
        self.assertEqual(code, 0, out)

    def test_field_without_partitions(self):
        tc = re.sub(r'\| FLD-USR-01 \| [^|]+ \| (valid|invalid) \|[^\n]*\n', '', TC)
        code, out, _ = self.go(AC, tc)
        self.assertIn('FLD-USR-01: no partitions in the Test analysis table', out)

    # BVA
    def test_bva_value_missing(self):
        code, out, _ = self.go(AC, drop_tc(TC, 'TC-USR-010'))
        self.assertIn('FLD-USR-01: BVA max+1 not covered (2-value)', out)

    def test_bva_wrong_value(self):
        tc = sub(TC, '`FLD-USR-01 BVA: max+1 = 255`', '`FLD-USR-01 BVA: max+1 = 256`')
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-010: FLD-USR-01 BVA max+1 = 256, expected 255', out)

    def test_bva_three_value_for_critical_field(self):
        ac = sub(AC, 'domain labels 1–63 characters | 🟠 |', 'domain labels 1–63 characters | 🔴 |')
        code, out, _ = self.go(ac, TC)
        self.assertIn('FLD-USR-01: BVA min+1 not covered (3-value)', out)
        self.assertIn('FLD-USR-01: BVA max-1 not covered (3-value)', out)

    def test_bva_bad_label(self):
        tc = sub(TC, '`FLD-USR-01 BVA: min-1 = 5`', '`FLD-USR-01 BVA: x`')
        code, out, _ = self.go(AC, tc)
        self.assertIn('BVA label "x" for FLD-USR-01 must look like', out)

    def test_bva_step_for_decimals(self):
        ac = sub(AC, '| Yes | 6 | 254 | 1 |', '| Yes | 0.01 | 100 | 0.01 |')
        tc = sub(sub(sub(sub(TC, 'min-1 = 5`', 'min-1 = 0`'), 'min = 6`', 'min = 0.01`'), 'max = 254`', 'max = 100`'), 'max+1 = 255`', 'max+1 = 100.01`')
        code, out, _ = self.go(ac, tc)
        self.assertNotIn('BVA', out.replace('BVA |', ''))

    # IDs and priority
    def test_unknown_id(self):
        tc = sub(TC, '`DT-USR-01.R2`', '`DT-USR-01.R9`')
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-011: cites DT-USR-01.R9, which is not in ac.md', out)

    def test_wrong_priority(self):
        sec = section(TC, 'TC-USR-011')
        tc = TC.replace(sec, sec.replace('| Priority | 🔴 |', '| Priority | 🟡 |'))
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-011: priority 🟡 should be 🔴', out)

    def test_priority_words_accepted(self):
        sec = section(TC, 'TC-USR-011')
        tc = TC.replace(sec, sec.replace('| Priority | 🔴 |', '| Priority | Critical |'))
        code, out, _ = self.go(AC, tc)
        self.assertEqual(code, 0, out)

    # blocking and open questions
    def test_blocked_by_answered_question(self):
        ac = sub(AC, '| BA/PO | Posted |', '| BA/PO | Answered |')
        code, out, _ = self.go(ac, TC)
        self.assertIn('TC-USR-013: OQ-USR-001 is answered; unblock this TC', out)

    def test_posted_question_counts_as_open(self):
        code, out, _ = self.go()
        self.assertNotIn('OQ-USR-001 is', out)

    def test_blocked_without_tbd_line(self):
        sec = section(TC, 'TC-USR-013')
        tc = TC.replace(sec, sec.replace('TBD (OQ-USR-001)', '72 h'))
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-013: blocked by OQ-USR-001 but has no "TBD (OQ-USR-001)" line', out)

    def test_tbd_in_active_tc(self):
        sec = section(TC, 'TC-USR-001')
        tc = TC.replace(sec, sec.replace('- Toast `Invitation sent.` is displayed.', '- TBD (OQ-USR-002): toast copy.'))
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-001: contains TBD (OQ-USR-002) but is not Blocked by OQ-USR-002', out)

    def test_blocked_without_question(self):
        sec = section(TC, 'TC-USR-013')
        tc = TC.replace(sec, sec.replace('| Blocked by | OQ-USR-001 |', '| Blocked by | — |'))
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-013: blocked without an open question', out)

    def test_blocked_items_not_counted_as_covered(self):
        tc = drop_tc(TC, 'TC-USR-013')
        code, out, _ = self.go(AC, tc)
        self.assertIn('ST-USR-01.T3: valid transition not covered', out)

    def test_eg_needs_covers_ac(self):
        sec = section(TC, 'TC-USR-019')
        tc = TC.replace(sec, sec.replace('| Covers AC | AC-USR-009 |', '| Covers AC | — |').replace('`AC-USR-009`, ', ''))
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-019: EG/CHK items need a Covers AC', out)

    # summary
    def test_summary_mismatch(self):
        tc = sub(TC, '| EP | 7 | 7 | 0 | 100% |', '| EP | 2 | 2 | 0 | 100% |')
        code, out, _ = self.go(AC, tc)
        self.assertEqual(code, 1)
        self.assertIn('Coverage summary row "EP"', out)

    # structure and robustness
    def test_duplicate_tc_id(self):
        tc = sub(TC, '## TC-USR-021:', '## TC-USR-020:')
        code, out, _ = self.go(AC, tc)
        self.assertIn('duplicate TC-USR-020', out)

    def test_tc_without_field_table(self):
        sec = section(TC, 'TC-USR-016')
        tc = TC.replace(sec, sec.replace('| Field | Value |\n| --- | --- |\n| Covers AC', '| Key | Value |\n| --- | --- |\n| Covers AC', 1))
        code, out, _ = self.go(AC, tc)
        self.assertIn('TC-USR-016: no Field/Value table', out)

    def test_subheading_inside_tc_is_kept(self):
        tc = sub(TC, '## TC-USR-007: Reject an email: contains space\n', '## TC-USR-007: Reject an email: contains space\n### Notes\n')
        tc = tc.replace('### Notes\n| Field | Value |', '| Field | Value |', 0)
        code, out, _ = self.go(AC, tc)
        self.assertEqual(code, 0, out)

    def test_escaped_pipe_does_not_shift_columns(self):
        ac = sub(AC, '`local@domain.tld`; local part', '`a\\|b` or `local@domain.tld`; local part')
        ac = sub(ac, 'domain labels 1–63 characters | 🟠 |', 'domain labels 1–63 characters | 🔴 |')
        code, out, _ = self.go(ac, TC)
        self.assertIn('FLD-USR-01: BVA min+1 not covered (3-value)', out)

    def test_pipe_inside_code_span(self):
        ac = sub(AC, 'case-insensitive: `Ana@x.test` equals', 'case-insensitive: `a | b` and `Ana@x.test` equals')
        code, out, _ = self.go(ac, TC)
        self.assertEqual(code, 0, out)

    def test_valid_column_words(self):
        ac = sub(AC, '| T2 | Invited | Invitee accepts | Accepted | Yes |', '| T2 | Invited | Invitee accepts | Accepted | Valid |')
        code, out, _ = self.go(ac, TC)
        self.assertEqual(code, 0, out)

    def test_valid_column_bad_value_exits_2(self):
        ac = sub(AC, '| T2 | Invited | Invitee accepts | Accepted | Yes |', '| T2 | Invited | Invitee accepts | Accepted | maybe |')
        code, _, err = self.go(ac, TC)
        self.assertEqual(code, 2)
        self.assertIn('Valid must be Yes or No', err)

    def test_min_max_header_variants(self):
        ac = sub(AC, '| Required | Min | Max | Step |', '| Required | Min length | Max length | Step |')
        code, out, _ = self.go(ac, TC)
        self.assertEqual(code, 0, out)

    def test_legend_table_before_dt(self):
        ac = sub(AC, '- Covers: AC-USR-001, AC-USR-003, AC-USR-004\n', '- Covers: AC-USR-001, AC-USR-003, AC-USR-004\n\n| Symbol | Meaning |\n| --- | --- |\n| – | any value |\n')
        code, out, _ = self.go(ac, TC)
        self.assertEqual(code, 0, out)

    def test_dt_without_rule_columns_exits_2(self):
        ac = sub(AC, '| Condition | R1 | R2 | R3 |', '| Condition | A | B | C |')
        code, _, err = self.go(ac, TC)
        self.assertEqual(code, 2)
        self.assertIn('DT-USR-01 has no table with R1…Rn columns', err)

    def test_fenced_content_ignored(self):
        ac = AC + '\n```\n| BR-USR-099 | fenced | 🔴 | Active | x |\n```\n'
        tc = sub(TC, '## Review log', '```\n## TC-USR-099: fenced\n```\n\n## Review log')
        code, out, _ = self.go(ac, tc)
        self.assertEqual(code, 0, out)

    def test_deprecated_items_excluded(self):
        ac = sub(AC, '| BR-USR-004 |', '| BR-USR-005 | Old rule. | 🔴 | Deprecated | ABC-1 |\n| BR-USR-004 |')
        code, out, _ = self.go(ac, TC)
        self.assertEqual(code, 0, out)

    def test_deprecated_ac_not_required(self):
        head, tail = AC.split('### AC-USR-007', 1)
        ac = head + '### AC-USR-007' + tail.replace('- Status: Active', '- Status: Deprecated', 1)
        code, out, _ = self.go(ac, drop_tc(TC, 'TC-USR-016'))
        self.assertNotIn('AC-USR-007: no TC', out)

    def test_bom_accepted(self):
        code, out, _ = self.go('﻿' + AC, TC)
        self.assertEqual(code, 0, out)

    # errors
    def test_missing_file_exits_2(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cov.main([os.path.join(self.dir, 'nope.md'), os.path.join(self.dir, 'nope2.md')])
        self.assertEqual(code, 2)
        self.assertIn('cannot read', err.getvalue())

    def test_non_utf8_exits_2(self):
        code, _, err = self.go(b'\xff\xfe bad', TC.encode('utf-8'), raw=True)
        self.assertEqual(code, 2)

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
