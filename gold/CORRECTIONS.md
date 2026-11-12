# Corrections to the original round-1 gold notes

The official scoring key is `gold/answers.md`. This file only records two
issues found in `gold/original/answers_round1.md` (and the associated
`compute_answers_round1.py`) while packaging the public set.

## M2: official gold is 10, not 6545

The prompt (round 1, `math1.txt`) says the bag has 7 red, 5 blue and 4 green
balls, **same-color balls are indistinguishable** (同色球不可分辨), and asks
how many different 6-ball draws contain at least one ball of each color.

The original script summed `\binom{7}{r}\binom{5}{b}\binom{4}{g}` over
`r+b+g=6` with `r,b,g ≥ 1` in range, getting 6545. That would be correct if
the balls were distinguishable. Under the written prompt, the answer is the
number of color triples `(r,b,g)`:

`(1,1,4), (1,2,3), (1,3,2), (1,4,1), (2,1,3), (2,2,2), (2,3,1), (3,1,2), (3,2,1), (4,1,1)`

so **10**. This is the key used when scoring the qwen4-max-preview baseline
(the model answered 10 and was marked correct).

## M11: typo in the counterexample arithmetic

The original note said:

> FALSE; counterexample n=40: 40^2+40+41=1641=3*547 (or n=41: 41^2=1681=41*41)

The claim (the polynomial is not always prime) is right, but the arithmetic
is not:

- For `n=40`: `40² + 40 + 41 = 1681 = 41²`
- For `n=41`: `41² + 41 + 41 = 1763 = 41 × 43`

The official key uses these corrected values. The baseline model's
counterexamples (`n=40` → `1681=41²`, `n=41` → `1763=41×43`) match the
corrected arithmetic.
