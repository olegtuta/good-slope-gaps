"""Enumerate prime-field fibers with two fixed points and prescribed injective slopes."""

from collections import Counter


def counts(prime, required):
    """Count fibers by their full injective-slope mask, for one required subset."""
    base = min(required)
    slopes = range(1, prime)
    limits = [1 if slope in required else 2 for slope in slopes]

    # z = y + base*x labels the points because the base projection is injective.
    outputs = {
        (z, x): tuple((z + (slope - base) * x) % prime for slope in slopes)
        for z in range(prime) for x in range(prime)
    }
    occupancy = [[0] * prime for _ in slopes]
    found = Counter()

    def mark(z, x, delta):
        for row, value in zip(occupancy, outputs[z, x], strict=True):
            row[value] += delta

    def extend(unassigned):
        if not unassigned:
            mask = sum(1 << s for s, row in enumerate(occupancy, 1) if max(row) == 1)
            found[mask] += 1
            return

        # Choosing the shortest list only changes the order of exhaustive search.
        choices = {}
        for z in unassigned:
            choices[z] = [
                x for x in range(prime)
                if all(row[value] < limit for row, value, limit in
                       zip(occupancy, outputs[z, x], limits, strict=True))
            ]
            if not choices[z]:
                return
        z = min(unassigned, key=lambda label: len(choices[label]))
        rest = tuple(label for label in unassigned if label != z)
        for x in choices[z]:
            mark(z, x, 1)
            extend(rest)
            mark(z, x, -1)

    mark(0, 0, 1)
    mark(base - 1, 1, 1)
    extend(tuple(z for z in range(prime) if z not in (0, base - 1)))
    return found
