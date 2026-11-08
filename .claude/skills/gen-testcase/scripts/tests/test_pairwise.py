"""Tests for pairwise.py. Run: python3 -m unittest discover -s .claude/skills/gen-testcase/scripts/tests"""
import contextlib
import importlib.util
import io
import itertools
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pairwise_mod', os.path.join(HERE, '..', 'pairwise.py'))
pw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pw)


def covers_all_pairs(params, rows):
    for i, j in itertools.combinations(range(len(params)), 2):
        need = {(a, b) for a in params[i][1] for b in params[j][1]}
        if need - {(r[i], r[j]) for r in rows}:
            return False
    return True


class PairwiseGenTest(unittest.TestCase):
    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = pw.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_three_binary_params_four_rows(self):
        params = pw.parse(['A=1,2', 'B=x,y', 'C=p,q'])
        rows = pw.generate(params)
        self.assertTrue(covers_all_pairs(params, rows))
        self.assertEqual(len(rows), 4)

    def test_fewer_rows_than_full_product(self):
        params = pw.parse(['A=1,2,3', 'B=1,2,3', 'C=1,2,3', 'D=1,2,3'])
        rows = pw.generate(params)
        self.assertTrue(covers_all_pairs(params, rows))
        self.assertLess(len(rows), 81)
        self.assertLessEqual(len(rows), 12)

    def test_deterministic(self):
        params = pw.parse(['A=1,2,3', 'B=x,y', 'C=p,q,r,s'])
        self.assertEqual(pw.generate(params), pw.generate(params))

    def test_large_space_fallback(self):
        params = pw.parse([f'P{i}=' + ','.join(str(v) for v in range(4)) for i in range(10)])
        rows = pw.generate(params)
        self.assertTrue(covers_all_pairs(params, rows))

    def test_table_output(self):
        code, out, _ = self.run_main('--param', 'Browser=Chrome,Edge', '--param', 'Locale=en,vi')
        self.assertEqual(code, 0)
        self.assertIn('| PW | Browser | Locale |', out)
        self.assertIn('| PW-01 |', out)

    def test_usage_errors(self):
        self.assertEqual(self.run_main('--param', 'A=1,2')[0], 2)
        self.assertEqual(self.run_main('--param', 'A=1,1', '--param', 'B=1')[0], 2)
        self.assertEqual(self.run_main('--param', 'A=1', '--param', 'A=2')[0], 2)
        self.assertEqual(self.run_main('--param', 'bad', '--param', 'B=1')[0], 2)


if __name__ == '__main__':
    unittest.main()
