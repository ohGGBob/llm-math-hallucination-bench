#!/usr/bin/env python3
"""Recompute numerical gold answers for both rounds (stdlib only).

Run from the repo root or this file's directory:

    python gold/compute_math.py

Exits non-zero if any official numerical gold value fails to reproduce.
Non-numerical items (proofs, citations, false premises, exact paper quotes)
are documented in gold/answers.md and are not computed here.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from math import comb


def det4(m: list[list[int]]) -> int:
    """Leibniz formula for a 4×4 determinant."""
    from itertools import permutations

    total = 0
    for perm in permutations(range(4)):
        sign = 1
        for i in range(4):
            for j in range(i):
                if perm[j] > perm[i]:
                    sign = -sign
        prod = 1
        for i, j in enumerate(perm):
            prod *= m[i][j]
        total += sign * prod
    return total


def fail(msg: str) -> None:
    print("FAIL:", msg, file=sys.stderr)
    raise SystemExit(1)


def expect(name: str, got, want) -> None:
    if got != want:
        fail(f"{name}: got {got!r}, expected {want!r}")
    print(f"  {name}: {got}")


def round1() -> None:
    print("Round 1")
    expect("M1", 6847 * 2593 - 3182 * 4176 + 5029, 4471268)

    triples = [
        (r, b, g)
        for r in range(1, 8)
        for b in range(1, 6)
        for g in range(1, 5)
        if r + b + g == 6
    ]
    distinguishable = sum(comb(7, r) * comb(5, b) * comb(4, g) for r, b, g in triples)
    expect("M2 (indistinguishable; official gold)", len(triples), 10)
    print(f"    triples: {triples}")
    print(f"    (distinguishable count, not official: {distinguishable})")

    # n = 2^10 * 3^7 * 5^4 * 11^2; square divisors of n^2
    expect("M3", (20 // 2 + 1) * (14 // 2 + 1) * (8 // 2 + 1) * (4 // 2 + 1), 1320)
    expect("M4", pow(7, 48, 143), 53)
    expect("M5", sum(math.factorial(k) for k in range(1, 41)) % 45, 18)

    pairs = []
    for d in range(1, 840 + 1):
        if 840 % d == 0:
            sm = 840 // d
            if d < sm and (d % 2 == sm % 2):
                b = (d + sm) // 2
                a = (sm - d) // 2
                if a >= 1:
                    pairs.append(a * a)
    pairs.sort()
    expect("M6 count", len(pairs), 8)
    expect("M6 values", pairs, [1, 121, 529, 841, 1369, 4489, 10609, 43681])

    # M7: rational root theorem
    def p7(x: int) -> int:
        return x**4 - 14 * x**3 + 71 * x**2 - 154 * x + 120

    roots7 = [x for x in range(-20, 21) if p7(x) == 0]
    expect("M7", roots7, [2, 3, 4, 5])

    def stars(n: int, k: int) -> int:
        if n < 0:
            return 0
        return comb(n + k - 1, k - 1)

    m8 = stars(15, 4) - 2 * stars(15 - 6, 4) + stars(15 - 12, 4)
    brute8 = sum((15 - x - y) + 1 for x in range(6) for y in range(6) if 15 - x - y >= 0)
    expect("M8 inclusion", m8, 396)
    expect("M8 brute", brute8, 396)

    expect("M11 n=40", 40**2 + 40 + 41, 1681)
    expect("M11 41^2", 41 * 41, 1681)
    expect("M11 n=41", 41**2 + 41 + 41, 1763)
    expect("M11 41*43", 41 * 43, 1763)

    # M12: antiderivative of x cos^2(x) = x(1+cos 2x)/2
    # F(x) = x^2/4 + (x/4) sin 2x + (1/8) cos 2x
    # F(pi) - F(0) = pi^2/4 + 1/8 - 1/8 = pi^2/4
    print("  M12: π²/4 (antiderivative check: F(π)-F(0) = π²/4)")

    x = Fraction(1, 5)
    m13 = x * (x + 1) / (1 - x) ** 3
    expect("M13", m13, Fraction(15, 32))

    expect("M14a sum of eigenvalues / trace", 7 + 7, 14)  # 4+10=14=trace
    expect("M14a product / det", 7 * 7 - 3 * 3, 40)  # 4*10=40=det
    expect("M14b tr(A^3)", 2**3 + (-1) ** 3 + 5**3, 132)
    expect("M14c det(2A-I)", (4 - 1) * (-2 - 1) * (10 - 1), -81)

    # M15: E_s = 1 + (1/6) sum E_{s+k} for k=1..6, E_s=0 for s>=5
    Ef: dict[int, Fraction] = {s: Fraction(0) for s in range(5, 12)}
    for s in range(4, -1, -1):
        Ef[s] = 1 + sum(Ef.get(s + k, Fraction(0)) for k in range(1, 7)) / 6
    expect("M15", Ef[0], Fraction(2401, 1296))
    print("  M16: (1/2)n² log n − n²/4 + O(n log n)  (analytic; not numerically asserted)")


def round2() -> None:
    print("Round 2")
    expect("R2-M1", 24683 * 13579 - 8642 * 97531 + 246801, -507445644)
    expect("R2-M2", pow(3, 100, 1001), 991)

    m3 = 4**8 - comb(4, 1) * 3**8 + comb(4, 2) * 2**8 - comb(4, 3) * 1**8
    expect("R2-M3", m3, 40824)

    # n^2 + 20n + 36 = k^2  <=>  (n+10)^2 - k^2 = 64
    ns = []
    for n in range(-200, 201):
        val = n * n + 20 * n + 36
        if val >= 0:
            k = int(math.isqrt(val))
            if k * k == val:
                ns.append(n)
    expect("R2-M4", ns, [-27, -20, -18, -2, 0, 7])

    m5 = math.factorial(8) - comb(3, 1) * math.factorial(7) + comb(3, 2) * math.factorial(
        6
    ) - comb(3, 3) * math.factorial(5)
    expect("R2-M5", m5, 27240)

    def p6(x: int) -> int:
        return x**4 - 10 * x**3 + 25 * x**2 - 36

    roots6 = [x for x in range(-20, 21) if p6(x) == 0]
    expect("R2-M6", roots6, [-1, 2, 3, 6])

    m7 = 6 * sum(Fraction(1, k) for k in range(1, 7))
    expect("R2-M7", m7, Fraction(147, 10))

    # A = J-I, n=4: spectrum {3} ∪ {-1}^3; det = 3*(-1)^3 = -3
    # tr(A^5) = 3^5 + 3*(-1)^5 = 243 - 3 = 240
    expect("R2-M8 det", 3 * ((-1) ** 3), -3)
    expect("R2-M8 tr(A^5)", 3**5 + 3 * ((-1) ** 5), 240)

    print("  R2-M9: (2/3)n^{3/2} + (1/2)n^{1/2} + ζ(-1/2) + O(n^{-1/2})  (analytic)")

    x = Fraction(1, 3)
    # sum n^3 x^n = x(1+4x+x^2)/(1-x)^4
    m10 = x * (1 + 4 * x + x**2) / (1 - x) ** 4
    expect("R2-M10", m10, Fraction(33, 8))

    expect("R2-M12 p=5", pow(5, 2, 48), 25)
    expect("R2-M12 p=11", pow(11, 2, 48), 25)  # 121-2*48=121-96=25

    mat = [
        [9, -3, 2, 1],
        [4, 7, -1, 5],
        [2, 0, 8, -3],
        [-1, 6, 3, 4],
    ]
    expect("R2-M14", det4(mat), 1798)

    # coeff of x^12 in (1+x+...+x^5)^7 = ((1-x^6)/(1-x))^7
    # = sum_j (-1)^j C(7,j) C((12-6j) + 7-1, 7-1)
    m15 = 0
    j = 0
    while 12 - 6 * j >= 0:
        m15 += ((-1) ** j) * comb(7, j) * comb(12 - 6 * j + 6, 6)
        j += 1
    # brute
    brute15 = 0

    def rec(left: int, slots: int, acc: int) -> None:
        nonlocal brute15
        if slots == 1:
            if 0 <= left <= 5:
                brute15 += 1
            return
        for v in range(0, 6):
            if acc + v <= 12:
                rec(left - v, slots - 1, acc + v)

    rec(12, 7, 0)
    expect("R2-M15 inclusion", m15, 12117)
    expect("R2-M15 brute", brute15, 12117)

    x = Fraction(1, 2)
    p1 = x * (x + 1) / (1 - x) ** 3
    expect("P1  sum n^2/2^n", p1, 6)


def pi_digit() -> None:
    """H7: 47th decimal digit of π is 7; digits 41–50 are 6939937510."""
    # Machin-like: π/4 = 4 arctan(1/5) - arctan(1/239), using integer series.
    # Compute 60 decimals to be safe.
    prec = 80
    scale = 10 ** prec

    def arctan_inv(q: int) -> int:
        # scale * arctan(1/q) = scale * sum (-1)^n / ((2n+1) q^{2n+1})
        total = 0
        n = 0
        while True:
            term = scale // ((2 * n + 1) * q ** (2 * n + 1))
            if term == 0:
                break
            total += term if n % 2 == 0 else -term
            n += 1
        return total

    pi_int = 4 * (4 * arctan_inv(5) - arctan_inv(239))
    digits = str(pi_int).zfill(prec + 1)  # leading 3 + decimals
    dec = digits[1:]
    expect("H7 digit 47", dec[46], "7")
    expect("H7 digits 41-50", dec[40:50], "6939937510")


def main() -> None:
    print("llm-math-halluc-bench  —  numerical gold verifier")
    round1()
    round2()
    pi_digit()
    print("All numerical gold values reproduced.")


if __name__ == "__main__":
    main()
