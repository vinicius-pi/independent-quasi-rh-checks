# Independent finite checks of two arithmetic lemmas in OpenAI's October 2026 manuscript

**Vinicius M. Pimenta, with AI assistance · 7 October 2026**

This repository is a small, reproducible numerical spot-check of specified formulas in OpenAI's [*The Quasi-Riemann Hypothesis*, October 5 manuscript](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/build/paper2.tex). **No discrepancy was found.** It checks two narrowly defined areas:

1. finite Gauss-sum identities from `lem:arithmetic`; and
2. Gaussian instances of masked Poisson summation from `lem:poisson`.

These are finite numerical checks. They do not verify the uniform analytic estimates, the paper's theorem, or the Riemann hypothesis.

## Reproduce the check

The [stdlib-only Python checker](check_arithmetic.py) prints machine-readable JSON. With Python 3.8 or later, run:

```text
python check_arithmetic.py > fresh-results.json
```

The saved reference output from the preparation host is [results.json](results.json). `fresh-results.json` is a new output file created by the command above; the saved reference remains available for direct comparison.

## What the finite tests cover

The arithmetic checks use five primary Eisenstein primes with norms **7, 13, 19, 31, and 37**, plus three coprime composite moduli with norms **91, 259, and 247**. They check the cubic Gauss identity, quadratic Gauss phase, Gauss–Jacobi conversion, reciprocity factor, and coefficient CRT identity for the trivial fixed ray-class twist. Residuals are below `2.6e-14` in double precision.

The three composite cases also provide a negative control for the reciprocity factor. Two have reciprocity sign `-1`; deleting that factor changes the check by approximately `2` (the recorded residuals are `1.999999999999999` and `1.9999999999999984`). This is informative because a deliberately omitted required factor produces a visible failure rather than merely another small floating-point residual.

The masked-Poisson checks use a nonprincipal sextic character modulo the primary prime `7+3ω` of norm 37, excluded primes of norms 7, 13, and 19, and **five** scale cases. They use `Φ(t)=exp(-πt)`, for which the paper's normalization gives `Φ̂(t)=2/√3 exp(-4πt/3)`. The maximum observed identity residual is below `2.6e-14`. Deliberately deleting the excluded-prime correction changes every recorded check by at least `1.9e-6` (the smallest saved value is `1.9831865569574575e-06`), providing a second detectable negative control.

The residual measures the numerical mismatch in the checked finite computation. It is not the same as the analytic Gaussian tail envelope used to control truncation: on these cases, the numerically evaluated envelope for the omitted lattice tails is below `1.8e-27`. Successful finite tests and small residuals therefore support the implementation of these spot-checks but do not establish the general analytic identities.

## Exact scope and source references

The source is pinned to `openai/math` commit `adc7f1241b42e322a6451854ab7e4b4c146bf78a`; the checked TeX file has SHA-256 `d9a8f15aa770cf883d0eabd2b775fad694ce20b44cba7928f5c0c9a6d8750d4d`.

| Source obligation | Inputs and outcome |
| --- | --- |
| [`lem:arithmetic`, equations `eq:gj`, `eq:recip`, `eq:crt-a`](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/build/paper2.tex#L823-L860) and its [appendix proof](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/build/paper2.tex#L2687-L2872) | Five primary Eisenstein primes of norms 7, 13, 19, 31, 37; three coprime composite moduli of norms 91, 259, 247. Checks the cubic Gauss identity, quadratic Gauss phase, Gauss–Jacobi conversion, reciprocity factor, and coefficient CRT identity for the trivial fixed ray-class twist. Residuals are below `2.6e-14` in double precision. Two composites have reciprocity sign `-1`; deleting that factor changes their check by about `2`. |
| [`lem:poisson`, equation `eq:poisson`](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/build/paper2.tex#L875-L932) | A nonprincipal sextic character modulo the primary prime `7+3ω` of norm 37, excluded primes of norms 7, 13, 19, and five scales. Uses `Φ(t)=exp(-πt)`, for which the paper's normalization gives `Φ̂(t)=2/√3 exp(-4πt/3)`. Maximum observed residual is below `2.6e-14`; a numerically evaluated analytic Gaussian envelope for the omitted lattice tails is below `1.8e-27` on these cases. Deliberately deleting the excluded-prime term changes each check by at least `1.9e-6`. |

Here `ω²+ω+1=0`, `N(a+bω)=a²-ab+b²`, and the additive character is exactly the paper's `e(z)=exp(4πi Im(z)/√3)`. For each listed primary prime `p=a+bω` of rational prime norm `q`, the script identifies `O/(p)` with `F_q` via `ω ↦ -a/b` and maps the sixth roots through `1+ω`. For the listed composite products, rational integers give all residue classes by the Chinese remainder theorem. These choices make the phase conventions explicit; a different normalization would change the checked identities.

The Poisson sums use `|a|,|b|≤60`. The tail envelope uses `N(a+bω)≥3 max(a²,b²)/4` and the `8m` points in each max-norm shell. Floating-point evaluation and this finite set of moduli remain limitations; the tests are falsification probes, not a proof of the general identities.

## Limitations and provenance

The underlying code and interpretation are AI-assisted and have not been independently checked by a human mathematician. The independently runnable checks should not be confused with independent human mathematical review.

This audit arose from a private review of 117 numbered RH-ASTRA research cycles against the public OpenAI release. The cycles were indexed and selected claims were audited; 117 separate proofs were **not** independently established. That review found no local theorem that improves or replaces an OpenAI proof step. This repository supplies a reproducible finite spot-check of phase and mask normalizations in the published 11/12 manuscript. Its deliberate omissions are test controls, not discoveries about the paper. It makes no claim of new number theory.
