#!/usr/bin/env python3
"""Pairwise (all-pairs) row generator for the Test analysis table of tc.md.

Usage:
  python3 pairwise.py --param "Browser=Chrome,Edge" --param "Locale=en,vi" --param "Role=Admin,Owner"

Prints a Markdown table `| PW | <param> | … |` with rows PW-01…PW-NN in which every pair of values of
any two parameters appears at least once. Greedy and deterministic: same input, same rows.
Exit codes: 0 table printed · 2 usage error.
"""
import argparse
import itertools
import random
import sys

MAX_CANDIDATES = 5_000  # full search below this; AETG-style above
CANDIDATES = 30
MAX_ROWS = 99


def parse(params):
    out = []
    for p in params:
        name, _, vals = p.partition('=')
        values = [v.strip() for v in vals.split(',') if v.strip()]
        if not name.strip() or len(values) < 1:
            raise ValueError(f'bad --param "{p}": use Name=v1,v2')
        if len(set(values)) != len(values):
            raise ValueError(f'duplicate value in --param "{p}"')
        out.append((name.strip(), values))
    if len(out) < 2:
        raise ValueError('give at least 2 parameters')
    if len({n.lower() for n, _ in out}) != len(out):
        raise ValueError('duplicate parameter name (case-insensitive)')
    for n, vals in out:
        if len({v.lower() for v in vals}) != len(vals):
            raise ValueError(f'duplicate value in {n} (case-insensitive)')
        if any('|' in x for x in [n] + vals):
            raise ValueError(f'"|" is not allowed in {n} or its values')
    top = sorted((len(v) for _, v in out), reverse=True)
    if top[0] * top[1] > MAX_ROWS:
        raise ValueError(f'at least {top[0] * top[1]} rows needed (two largest value counts); max {MAX_ROWS}: split the parameters')
    return out


def pairs_of(row):
    return {(i, row[i], j, row[j]) for i, j in itertools.combinations(range(len(row)), 2)}


def generate(params):
    values = [v for _, v in params]
    todo = set()
    for i, j in itertools.combinations(range(len(values)), 2):
        todo |= {(i, a, j, b) for a in values[i] for b in values[j]}
    total = 1
    for v in values:
        total *= len(v)
    rows = []
    if total <= MAX_CANDIDATES:
        cands = list(itertools.product(*values))
        while todo:
            best = max(cands, key=lambda r: len(pairs_of(r) & todo))
            rows.append(best)
            todo -= pairs_of(best)
        return rows
    # Large spaces (AETG-style): per row, build CANDIDATES rows greedily from an uncovered pair in a
    # shuffled parameter order and keep the one that covers most uncovered pairs. Fixed seed: deterministic.
    rng = random.Random(7)
    n = len(values)

    def covers(row, k, v):
        return sum(1 for m in range(n) if row[m] is not None and m != k and
                   ((m, row[m], k, v) if m < k else (k, v, m, row[m])) in todo)

    while todo:
        best, best_gain = None, -1
        pool = sorted(todo)
        for _ in range(CANDIDATES):
            i, a, j, b = pool[rng.randrange(len(pool))]
            row = [None] * n
            row[i], row[j] = a, b
            order = [k for k in range(n) if row[k] is None]
            rng.shuffle(order)
            for k in order:
                row[k] = max(values[k], key=lambda v: (covers(row, k, v), -values[k].index(v)))
            gain = len(pairs_of(row) & todo)
            if gain > best_gain:
                best, best_gain = tuple(row), gain
        rows.append(best)
        todo -= pairs_of(best)
    return rows


def table(params, rows):
    lines = ['| PW | ' + ' | '.join(n for n, _ in params) + ' |',
             '| --- | ' + ' | '.join('---' for _ in params) + ' |']
    lines += [f'| PW-{i:02d} | ' + ' | '.join(r) + ' |' for i, r in enumerate(rows, 1)]
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Generate all-pairs rows for the tc.md Test analysis table.')
    ap.add_argument('--param', action='append', default=[], help='Name=v1,v2,… (repeat, at least 2)')
    a = ap.parse_args(argv)
    try:
        params = parse(a.param)
    except ValueError as e:
        print(f'pairwise: {e}', file=sys.stderr)
        return 2
    rows = generate(params)
    if len(rows) > MAX_ROWS:
        print('pairwise: more than 99 rows; split the parameters', file=sys.stderr)
        return 2
    print(table(params, rows))
    return 0


if __name__ == '__main__':
    sys.exit(main())
