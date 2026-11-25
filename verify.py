"""Replay the finite parts of the good-slope gap proof (Python 3.10+)."""

from collections import Counter
from gzip import decompress
from itertools import combinations, product
import json
from math import gcd, prod
from pathlib import Path

from anchors import PRIMES, anchor_profiles, cnf, replay
from fibers import counts

DATA = Path(__file__).resolve().parent / "certificates"


def check_cut(widths, inside, boundary, flow):
    grid = list(product(*(range(w) for w in widths)))
    size = len(grid)
    source, sink = 2 * size, 2 * size + 1
    high = boundary * size + 1
    capacity = {}
    for i, x in enumerate(grid):
        capacity[source, i] = high if i == 0 else boundary - inside
        capacity[size + i, sink] = boundary
        for j, y in enumerate(grid):
            if sum(a != b for a, b in zip(x, y)) <= 1:
                capacity[i, size + j] = high
    balance = Counter()
    used = set()
    for u, v, amount in flow:
        assert (u, v) not in used and 0 < amount <= capacity[u, v]
        used.add((u, v))
        balance[u] -= amount
        balance[v] += amount
    assert all(balance[i] == 0 for i in range(2 * size))
    assert balance[sink] == -balance[source] == (boundary - inside) * size + 48
    print(f"Verified flow of value {balance[sink]} on {widths}.")


def check_fibers():
    expected_good = {2, 5, 6, 7, 8, 11}
    expected_mask = sum(1 << s for s in expected_good)
    passed = tested = 0
    for required in combinations(range(2, 13), 5):
        histogram = counts(13, required)
        assert set(histogram) <= {expected_mask}
        assert bool(histogram) == (set(required) <= expected_good)
        passed += bool(histogram)
        tested += 1
    assert (tested, passed) == (462, 6)
    print("Verified all 462 direction sets over F_13; six admit a fiber.")


def check_anchors():
    traces = json.loads(decompress((DATA / "anchors.json.gz").read_bytes()))
    assert len(traces) == 16
    total = 0
    for index, (shape, trace) in enumerate(zip(product(*(anchor_profiles(p) for p in PRIMES)),
                                               traces, strict=True)):
        width, clauses = cnf(shape)
        assert (width, len(clauses)) == (2260, 42275)
        assert trace[-1].strip() == "0"
        total += replay(width, clauses, trace)
        print(f"Verified anchor orientation {index + 1}/16.", flush=True)
    assert total == 9368
    print(f"Verified {total} reverse unit propagation steps.")


def check_witnesses():
    for n, q, target in [(105, 7, 40), (165, 11, 72), (231, 11, 108),
                         (385, 11, 216), (455, 13, 264), (715, 13, 440),
                         (prod(PRIMES), 13, 528)]:
        k = n // q
        f = [2*x % n if x % k == 0 else x for x in range(n)]
        assert len(set(f)) == n
        good = {m for m in range(n) if len({(v + m*x) % n for x, v in enumerate(f)}) == n}
        predicted = {m for m in range(n) if gcd(1 + m, k) == 1 and m % q not in (q-1, q-2)}
        assert good == predicted and len(good) == target
        print(f"Verified all {n} slopes of the witness: {target} good.")


def main():
    if not __debug__:
        raise SystemExit("Run Python without -O or -OO; proof checks use assertions.")
    check_witnesses()
    last, middle = json.loads((DATA / "cuts.json").read_text(encoding="utf-8"))
    check_cut((2, 4, 6), 1, 6, last)
    check_cut((2, 4), 6, 18, middle)
    check_fibers()
    check_anchors()
    print("All finite checks passed.")


if __name__ == "__main__":
    main()
