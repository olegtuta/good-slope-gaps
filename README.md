# Good-slope gaps over squarefree residue rings

Verification files for Oleg Kyzlasov, *Sharp good-slope gaps for permutations of squarefree residue rings*, version 1.0 (25 November 2026). [Read the preprint](manuscript/good-slope-gaps.pdf).

For a permutation `f` modulo `n`, count the coefficients `u` for which `f(x) + ux` is also a permutation. The largest possible count is Euler's totient of `n`. The paper determines the next largest count in the following cases.

| Modulus | Largest count below the maximum | Proof |
| --- | ---: | --- |
| `apq`, primes `a < p < q`, with `a = 3` or `5` | `(a-1)(p-1)(q-2)` | Theorem 1, coordinate-row argument |
| `1365 = 3 × 5 × 7 × 13` | 528, below a maximum of 576 | Theorem 2, coordinate-row argument and finite certificates |

Bhunia gave the construction attaining the proposed count. Earlier work covers 105, 165 and a separated range of prime pairs in the 3pq family. See [Bhunia, Question 10.2](https://arxiv.org/html/2611.04551v1#S10) and the [AFTD report](https://rainwangphy.github.io/aftd-platform/blog/2026-11-19-op-1027/).

## Run the finite checks

From the root of this directory, with Python 3.10 or later:

```sh
python -B verify.py
```

The program runs offline using the standard library. A successful run exits with status 0 and ends with `All finite checks passed.` Run with assertions enabled (the default).

| Check | What is reconstructed |
| --- | --- |
| Attainment | The explicit permutation and its full set of good slopes at seven moduli, including every coefficient modulo 1365 |
| Neighborhood bounds | Two finite networks. The checker tests capacities, conservation and the claimed values of the flows in [cuts.json](certificates/cuts.json). |
| Thirteen-point fibers | All 462 choices of five required unit directions, with exhaustive completion of the two fixed points in [fibers.py](fibers.py) |
| Compatibility | The 16 Boolean formulas for the four fibers, rebuilt from their coordinate domains in [anchors.py](anchors.py). Each refutation is checked against its own formula by reverse unit propagation. |

The section on three prime factors proves the infinite-family statement. The finite computations in later sections close the four-prime case. The base case at 105 uses the [published formal theorem](https://rainwangphy.github.io/aftd-platform/d/good_slopes_gap_mod_105/).

### Certificate formats

The two entries in `cuts.json` are lists of triples `[tail, head, flow]`. Grid points are numbered from zero in lexicographic order. For a grid of size `k`, the first and second copies start at 0 and `k`, with source `2*k` and sink `2*k+1`. The first network has side lengths (2, 4, 6), the second (2, 4).

Decompressing `certificates/anchors.json.gz` gives a JSON list of 16 clause traces. Orientations are ordered lexicographically over primes 3, 5, 7 and 13, in the order of the two displayed profiles in Section 5. Integers are signed variable numbers. A trailing zero terminates each clause, and the line `0` denotes the empty clause. The traces contain 9,368 clause additions in all.

## Manuscript and citation

Both LaTeX sources are in [manuscript](manuscript/). From that directory, run `tectonic good-slope-gaps.tex`. Alternatively, run pdfLaTeX twice to resolve internal references. For a citation to this code and certificate set, use [version 1.0](https://github.com/olegtuta/good-slope-gaps/tree/v1.0). Copyright © 2026 Oleg Kyzlasov. The manuscript, code and certificates are distributed under [CC BY 4.0](LICENSE).
