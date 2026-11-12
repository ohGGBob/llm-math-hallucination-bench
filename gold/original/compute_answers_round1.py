#!/usr/bin/env python3
from fractions import Fraction
import math
from itertools import combinations
import sympy as sp

print("=" * 60)
print("M1 arithmetic")
m1 = 6847 * 2593 - 3182 * 4176 + 5029
print(m1)
print(6847 * 2593)
print(3182 * 4176)

print("=" * 60)
print("M2 marbles: 7R 5B 4G draw 6 at least one of each")
total = 0
details = []
for r in range(1, 8):
    for b in range(1, 6):
        for g in range(1, 5):
            if r + b + g == 6:
                w = math.comb(7, r) * math.comb(5, b) * math.comb(4, g)
                total += w
                details.append((r, b, g, w))
print(details)
print("total", total)

print("=" * 60)
print("M3 square divisors of n^2")
# n = 2^10 * 3^7 * 5^4 * 11^2
# n^2 = 2^20 * 3^14 * 5^8 * 11^4
# square divisors: even exponents
print((20//2 + 1) * (14//2 + 1) * (8//2 + 1) * (4//2 + 1))

print("=" * 60)
print("M4 7**48 % 143")
print(pow(7, 48, 143))
print("check CRT path", 7**48 % 11, 7**48 % 13)

print("=" * 60)
print("M5 sum k! for k=1..40 mod 45")
s = 0
for k in range(1, 41):
    s += math.factorial(k)
print(s % 45)
# also show partial
s9 = sum(math.factorial(k) for k in range(1, 10))
print("sum 1..9!", s9, "mod 45", s9 % 45)
print("10! mod 45", math.factorial(10) % 45)

print("=" * 60)
print("M6 n and n+840 both positive perfect squares")
# b^2 - a^2 = 840, a>=1, b>a
count = 0
pairs = []
for d in range(1, int(math.sqrt(840)) + 1):
    if 840 % d == 0:
        s = 840 // d  # b-a = d, b+a = s  OR we iterate factor pairs
# better iterate all factor pairs
for d in range(1, 840 + 1):
    if 840 % d == 0:
        sm = 840 // d
        if d < sm and (d % 2 == sm % 2):
            b = (d + sm) // 2
            a = (sm - d) // 2
            if a >= 1:
                count += 1
                pairs.append((a*a, a, b, d, sm))
print("count", count)
print(pairs)

print("=" * 60)
print("M7 polynomial roots")
x = sp.symbols('x')
p = x**4 - 14*x**3 + 71*x**2 - 154*x + 120
print(sp.factor(p))
print(sp.roots(p))
print(sp.solve(p, x))

print("=" * 60)
print("M8 stars and bars with caps")
# x+y+z+w=15, 0<=x<=5, 0<=y<=5, z,w>=0
# inclusion
from math import comb
def N(n, k):
    # nonneg solutions to k vars sum to n
    if n < 0:
        return 0
    return comb(n + k - 1, k - 1)
# 4 variables
total = N(15, 4)
# subtract x>=6 or y>=6
sub = N(15-6, 4) + N(15-6, 4)
# add x>=6 and y>=6
add = N(15-12, 4)
print(total, sub, add, total - sub + add)
# brute
c = 0
for xx in range(0, 6):
    for yy in range(0, 6):
        rest = 15 - xx - yy
        if rest >= 0:
            # z+w = rest, z,w>=0: rest+1 ways
            c += rest + 1
print("brute", c)

print("=" * 60)
print("M9 hexagon")
print("area ratio 3/4, inner side 13*sqrt(3)/2")

print("=" * 60)
print("M12 integral")
xx = sp.symbols('x')
I = sp.integrate(xx * sp.cos(xx)**2, (xx, 0, sp.pi))
print(I, I.simplify(), float(I), math.pi**2/4)

print("=" * 60)
print("M13 series n^2 / 5^n")
xs = sp.symbols('xs')
# formula x(x+1)/(1-x)**3 at x=1/5
form = xs*(xs+1)/(1-xs)**3
print(form.subs(xs, sp.Rational(1,5)))
s = sum(n**2 / 5**n for n in range(1, 80))
print(float(s), float(sp.Rational(15,32)))

print("=" * 60)
print("M14 linear algebra")
B = sp.Matrix([[7,3],[3,7]])
print("eigenvals", B.eigenvals())
print("eigenvects", B.eigenvects())
print("det", B.det(), "trace", B.trace())
# A 3x3 eigenvalues 2,-1,5
# trace(A^3)=8-1+125=132
# det(2A-I)=(4-1)(-2-1)(10-1)=3*(-3)*9=-81
print(8-1+125, 3*(-3)*9)
print("det(A^2-3A-10I):", (4-6-10), (1+3-10), (25-15-10))
print("product", (4-6-10)*(1+3-10)*(25-15-10))

print("=" * 60)
print("M15 expected rolls until sum exceeds 4")
# state E[s] for s=0,1,2,3,4; E[s]=0 for s>=5
# verify by DP
E = {s: 0.0 for s in range(5, 5+6+1)}
# solve from high s down
from fractions import Fraction
Ef = {}
for s in range(5, 12):
    Ef[s] = Fraction(0)
for s in range(4, -1, -1):
    # E_s = 1 + (1/6) sum E_{s+k} for k=1..6
    Ef[s] = 1 + sum(Ef.get(s+k, Fraction(0)) for k in range(1,7)) / 6
    print(s, Ef[s], float(Ef[s]))
print("E0", Ef[0], float(Ef[0]), 2401/1296)

# Monte Carlo sanity
import random
random.seed(0)
trials = 200000
tot = 0
for _ in range(trials):
    sm = 0
    rolls = 0
    while sm <= 4:
        sm += random.randint(1,6)
        rolls += 1
    tot += rolls
print("MC", tot/trials)

print("=" * 60)
print("M15b asymptotics first two terms of sum k log k")
# (1/2) n^2 log n - n^2/4
n = 1000
exact = sum(k * math.log(k) for k in range(1, n+1))
approx2 = 0.5 * n*n * math.log(n) - n*n/4
approx3 = approx2 + 0.5 * n * math.log(n)
print(exact, approx2, approx3, exact-approx2, exact-approx3)

print("=" * 60)
print("pi digits")
# compute many digits of pi
import decimal
decimal.getcontext().prec = 250
# Machin-like
def pi_dec():
    D = decimal.Decimal
    getcontext = decimal.getcontext
    # use decimal + formula
    return D(1).atan() * 4  # not valid, Decimal has no atan in older?
try:
    pi = decimal.Decimal(1).atan()*4
    print('atan method', str(pi)[:80])
except Exception as e:
    print('no atan', e)

# python 3.13 math.pi isn't enough; use sympy
pi_str = str(sp.N(sp.pi, 220))
# sp.N returns '3.1415...'
digits = pi_str.split('.')[1]
print("pi 47th", digits[46], "digits41-50", digits[40:50])
print("pi 201st", digits[200], "digits196-205", digits[195:205])

e_str = str(sp.N(sp.E, 220))
ed = e_str.split('.')[1]
print("e 47th", ed[46], "e 100th", ed[99], "e96-105", ed[95:105])

print("=" * 60)
print("1013 prime?", sp.isprime(1013))
print("done")
