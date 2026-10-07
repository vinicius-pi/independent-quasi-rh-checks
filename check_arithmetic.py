"""Finite, source-bound checks of arithmetic identities in openai/math.

Pinned source: openai/math adc7f1241b42e322a6451854ab7e4b4c146bf78a,
preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/build/paper2.tex,
Lemma lem:arithmetic, Lemma lem:poisson, and the arithmetic appendix.

These are numerical falsification checks, not a proof of either lemma or of the
paper's zero-free-region theorem. Python standard library only.
"""

import cmath
import json
import math


OPENAI_COMMIT = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
PRIMARY_PRIMES = [(1, 3), (4, 3), (-2, 3), (1, 6), (7, 3)]
COMPOSITE_PAIRS = [((1, 3), (4, 3)), ((1, 3), (7, 3)), ((4, 3), (-2, 3))]
MODULUS = (7, 3)  # Norm 37; its sextic character is trivial on the six units.
MASKED_CASES = [((1, 3), 4.0), ((4, 3), 4.0),
                ((4, 3), 10.0), ((4, 3), 20.0), ((-2, 3), 4.0)]
LATTICE_CUTOFF = 60
TOLERANCE = 1e-10


def norm(z):
    a, b = z
    return a * a - a * b + b * b


def multiply(z, w):
    """Multiply (a+b omega)(c+d omega), where omega^2+omega+1=0."""
    a, b = z
    c, d = w
    return (a * c - b * d, a * d + b * c - b * d)


def alpha(z):
    a, b = z
    return complex(a - b / 2, b * math.sqrt(3) / 2) / math.sqrt(norm(z))


def character_for_prime(p):
    """Sextic residue character for primary p=a+b omega of rational prime norm.

    In O/(p)=F_q, omega maps to -a/b.  The complex sixth root exp(pi*i/3)
    is 1+omega, so its reduction fixes the identification of sixth roots.
    """
    a, b = p
    q = norm(p)
    assert (a - 1) % 3 == 0 and b % 3 == 0
    omega_mod_q = (-a * pow(b, -1, q)) % q
    zeta_mod_q = (1 + omega_mod_q) % q
    root_index = {pow(zeta_mod_q, j, q): j for j in range(6)}
    assert len(root_index) == 6

    def chi(z):
        x, y = z
        residue = (x + y * omega_mod_q) % q
        if residue == 0:
            return 0j
        sixth_power = pow(residue, (q - 1) // 6, q)
        return cmath.exp(1j * math.pi * root_index[sixth_power] / 3)

    return chi


def gauss(primes, exponent):
    """gamma_j(n), using rational representatives for the listed moduli.

    Each prime here has a distinct rational prime norm, so Z maps onto
    O/(product primes) by the Chinese remainder theorem.
    For n=A+B omega, e(x/n)=exp(-2*pi*i*B*x/N(n)) when x is rational.
    """
    n = (1, 0)
    for p in primes:
        n = multiply(n, p)
    q = norm(n)
    b = n[1]
    characters = [character_for_prime(p) for p in primes]
    total = sum(
        math.prod(chi((x, 0)) for chi in characters) ** exponent
        * cmath.exp(-2j * math.pi * b * x / q)
        for x in range(q)
    )
    return total / math.sqrt(q)


def G(primes):
    chi4 = math.prod(character_for_prime(p)((4, 0)) for p in primes)
    return chi4.conjugate() * gauss(primes, 3)


def check_prime(p):
    a, b = p
    cubic = abs(gauss([p], 2) ** 3 + alpha(p))
    quadratic = (1 + 1j ** (-b) + 1j ** a + 1j ** (b - a)) / 2
    quadratic_residual = abs(gauss([p], 3) - quadratic)
    assert max(cubic, quadratic_residual) < TOLERANCE
    return {"p": [a, b], "norm": norm(p),
            "gamma2_cubic_residual": cubic,
            "quadratic_gauss_residual": quadratic_residual}


def check_composite(p, r):
    n = multiply(p, r)
    chi_p = character_for_prime(p)
    chi_r = character_for_prime(r)
    reciprocity = chi_r(p) / chi_p(r)
    a_n = alpha(n).conjugate() * gauss([p, r], 2)
    a_p = alpha(p).conjugate() * gauss([p], 2)
    a_r = alpha(r).conjugate() * gauss([r], 2)
    residuals = {
        "gamma2_cubic": abs(gauss([p, r], 2) ** 3 - alpha(n)),
        "gauss_jacobi": abs(gauss([p, r], 1) * gauss([p, r], 2)
                            - alpha(n) * G([p, r])),
        "G_reciprocity": abs(G([p, r]) - G([p]) * G([r]) * reciprocity),
        "a_crt": abs(a_n - a_p * a_r * chi_r(p) ** 4),
        "reciprocity_is_sign": min(abs(reciprocity - 1),
                                   abs(reciprocity + 1)),
    }
    assert max(residuals.values()) < TOLERANCE
    omitted_reciprocity_residual = abs(G([p, r]) - G([p]) * G([r]))
    if reciprocity.real < 0:
        assert omitted_reciprocity_residual > 1
    return {"p": list(p), "r": list(r), "norm": norm(n),
            "reciprocity_sign": 1 if reciprocity.real > 0 else -1,
            "omitted_reciprocity_residual": omitted_reciprocity_residual,
            "residuals": residuals}


def gaussian_transform(t):
    """For Phi(u)=exp(-pi*u), the paper's normalized transform is this."""
    return 2 / math.sqrt(3) * math.exp(-4 * math.pi * t / 3)


def lattice_gaussian_tail(c):
    """Bound sum_{max(|a|,|b|)>R} exp(-c*N(a+b*omega)).

    N(a+b*omega) >= 3*max(a*a,b*b)/4.  The max-norm shell m has 8m
    points.  Starting at M=R+1, successive shell bounds have ratio at
    most (1+1/M)*exp(-(3c/4)*(2M+1)).
    """
    m = LATTICE_CUTOFF + 1
    k = 3 * c / 4
    ratio = (1 + 1 / m) * math.exp(-k * (2 * m + 1))
    assert ratio < 1
    return 8 * m * math.exp(-k * m * m) / (1 - ratio)


def check_masked_poisson(mask_prime, H):
    """Check lem:poisson with a nontrivial sextic character and prime mask."""
    q = norm(MODULUS)
    r = norm(mask_prime)
    mask_a, mask_b = mask_prime
    omega_mod_r = (-mask_a * pow(mask_b, -1, r)) % r
    chi = character_for_prime(MODULUS)
    gamma = gauss([MODULUS], 1)
    chi_mask = chi(mask_prime)
    lhs = 0j
    dual = 0j
    dual_without_mask_term = 0j

    for a in range(-LATTICE_CUTOFF, LATTICE_CUTOFF + 1):
        for b in range(-LATTICE_CUTOFF, LATTICE_CUTOFF + 1):
            z = (a, b)
            n = norm(z)
            value = chi(z)
            if (a + b * omega_mod_r) % r != 0:
                lhs += value * math.exp(-math.pi * n / H)
            if value != 0:
                basic = value.conjugate() * gaussian_transform(H * n / q)
                correction = (value.conjugate() * chi_mask / r
                              * gaussian_transform(H * n / (q * r)))
                dual += basic - correction
                dual_without_mask_term += basic

    factor = H * gamma / math.sqrt(q)
    residual = abs(lhs - factor * dual)
    omitted_mask_residual = abs(lhs - factor * dual_without_mask_term)
    # The trivial finite Gauss bound |gamma|<=sqrt(q) gives |factor|<=H.
    tail_bound = lattice_gaussian_tail(math.pi / H) + H * 2 / math.sqrt(3) * (
        lattice_gaussian_tail(4 * math.pi * H / (3 * q))
        + lattice_gaussian_tail(4 * math.pi * H / (3 * q * r)) / r
    )
    assert residual + tail_bound < TOLERANCE
    assert omitted_mask_residual > 1e-7  # The negative control is detectable.
    return {"modulus": list(MODULUS), "modulus_norm": q,
            "excluded_prime": list(mask_prime), "excluded_norm": r,
            "H": H, "lhs": [lhs.real, lhs.imag],
            "residual": residual,
            "truncation_tail_bound": tail_bound,
            "omitted_mask_residual": omitted_mask_residual}


def main():
    prime_results = [check_prime(p) for p in PRIMARY_PRIMES]
    composite_results = [check_composite(p, r) for p, r in COMPOSITE_PAIRS]
    masked_results = [check_masked_poisson(p, H) for p, H in MASKED_CASES]
    all_residuals = [x["gamma2_cubic_residual"] for x in prime_results]
    all_residuals += [x["quadratic_gauss_residual"] for x in prime_results]
    all_residuals += [v for x in composite_results for v in x["residuals"].values()]
    all_residuals += [x["residual"] for x in masked_results]
    print(json.dumps({
        "source_commit": OPENAI_COMMIT,
        "scope": "finite arithmetic and Gaussian Poisson spot-checks only",
        "prime_cases": prime_results,
        "composite_cases": composite_results,
        "masked_poisson_cases": masked_results,
        "maximum_absolute_residual": max(all_residuals),
        "all_checks_passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
