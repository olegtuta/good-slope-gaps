"""Build the 22-point compatibility formula and replay its RUP certificate."""

from collections import Counter, defaultdict, deque
from itertools import combinations, product

PRIMES = (3, 5, 7, 13)


def anchor_profiles(r):
    # Both long lines meet at a crossing of the coordinates of the
    # two anchors. Determine the two displacements from each anchor.
    q = {x*x % r for x in range(1, r)}
    choices = []
    for a, b, scale in ((0, r-1, 1), (1, 0, -1)):
        h = {(a + scale*t) % r for t in q}
        v = {(b + scale*t) % r for t in q}
        fiber = tuple(sorted({(a, b)} | {(x, b) for x in h} | {(a, y) for y in v}))
        assert len(fiber) == r and {(0, 0), (1, r-1)} <= set(fiber)
        for u in range(1, r):
            hits = Counter((y + u*x) % r for x, y in fiber)
            assert (len(hits) < r) == (u in q) and max(hits.values()) <= 2
        choices.append(fiber)
    return choices


def source_domains(profiles):
    places = [tuple(((0, 0),) for _ in PRIMES), tuple(((1, r-1),) for r in PRIMES)]
    for axis, fiber in enumerate(profiles):
        r = PRIMES[axis]
        for point in fiber:
            if point in ((0, 0), (1, r-1)):
                continue
            places.append(tuple((point,) if axis == i else tuple((x, -x % p) for x in range(p))
                                for i, p in enumerate(PRIMES)))
    return places


def cnf(profiles):
    clauses = []
    variables = 0

    def fresh():
        nonlocal variables
        variables += 1
        return variables

    locations = []
    for place in source_domains(profiles):
        row = []
        for domain in place:
            literals = {state: fresh() for state in domain}
            clauses.append(tuple(literals.values()))
            clauses.extend((-a, -b) for a, b in combinations(literals.values(), 2))
            row.append(literals)
        locations.append(row)

    def encode_flag(table):
        flags = {value for _, _, value in table}
        if len(flags) == 1:
            return next(iter(flags))
        lit = fresh()
        clauses.extend((-a, -b, lit if value else -lit) for a, b, value in table)
        return lit

    def add(lits):
        if not any(value is True for value in lits):
            clauses.append(tuple(lit for lit in lits if lit is not False))

    def inverse(value):
        return not value if type(value) is bool else -value

    for a, b in combinations(locations, 2):
        escapes, leaked, differs = [], [], []
        for p, left, right in zip(PRIMES, a, b, strict=True):
            nonsquares = set(range(1, p)) - {x*x % p for x in range(1, p)}
            collision, outside, distinct = [], [], []
            for (x, y), (z, w) in product(left, right):
                u = left[x, y]
                v = right[z, w]
                hits = {s for s in range(1, p) if (y+s*x-w-s*z) % p == 0}
                collision.append((u, v, not hits))
                outside.append((u, v, bool(hits & nonsquares)))
                distinct.append((u, v, x != z))
            escapes.append(encode_flag(collision))
            leaked.append(encode_flag(outside))
            differs.append(encode_flag(distinct))
        add(differs)
        for flag in leaked:
            add([inverse(flag), *escapes])
    return variables, clauses


class UnitReplay:
    """Watched-clause unit propagation with a fresh assignment per proof line."""

    def __init__(self, initial):
        self.clauses = []
        self.watches = defaultdict(list)
        self.units = []
        self.empty = False
        for row in initial:
            self.add(row)

    def add(self, row):
        if len(row) <= 1:
            if row:
                self.units.append(row[0])
            else:
                self.empty = True
            return
        clause = list(row)
        self.watches[clause[0]].append(len(self.clauses))
        self.watches[clause[1]].append(len(self.clauses))
        self.clauses.append(clause)

    def contradicts(self, assumptions):
        if self.empty:
            return True
        waiting = deque((*self.units, *assumptions))
        true = set()
        while waiting:
            lit = waiting.popleft()
            if -lit in true:
                return True
            if lit in true:
                continue
            true.add(lit)
            indices = self.watches[-lit]
            i = 0
            while i < len(indices):
                index = indices[i]
                clause = self.clauses[index]
                if clause[0] == -lit:
                    clause[0], clause[1] = clause[1], clause[0]
                assert clause[1] == -lit
                if clause[0] in true:
                    i += 1
                    continue
                swap = next((j for j in range(2, len(clause)) if -clause[j] not in true), None)
                if swap is not None:
                    clause[1], clause[swap] = clause[swap], clause[1]
                    self.watches[clause[1]].append(index)
                    indices[i] = indices[-1]
                    indices.pop()
                    continue
                if -clause[0] in true:
                    return True
                waiting.append(clause[0])
                i += 1
        return False


def replay(width, clauses, lines):
    unit = UnitReplay(clauses)
    count = 0
    for line in lines:
        if line.startswith("d ") or not line.strip():
            continue
        numbers = tuple(map(int, line.split()))
        assert numbers[-1] == 0
        row = tuple(dict.fromkeys(numbers[:-1]))
        assert all(0 < abs(lit) <= width for lit in row)
        assert unit.contradicts(-lit for lit in row), (count, row)
        unit.add(row)
        count += 1
    assert unit.contradicts(())
    return count
