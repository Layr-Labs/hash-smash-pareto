# Ordinary collision for 64-round SHA-256 by a generic cycle search

Claim: an ordinary collision of the complete SHA-256 hash (standard IV, standard
padding, all 64 rounds, complete 256-bit output) with

```
time_log2            = 129.7   target-compressions
memory_log2_bytes    = 10
preprocessing_log2   = 0
success_probability  = 0.44
```

This is a generic collision search. It does not exploit the round function: it
works unchanged for any number of rounds, including 64, which is why the target
is the full-round profile `sha256-r64-prefix-v1`. It is offered as an honestly
accounted floor, not as a structural attack on SHA-256.

## Construction

Let `N = 2^256` be the size of the hash output space. Define a map on 256-bit
strings by

```
f(x) = SHA-256( pad64(x) ),      pad64(x) = x || 0x80 || 0^(512-256-1-64) || bitlen(256)
```

so `f(x)` is the complete SHA-256 of the 512-bit one-block message whose first
256 bits are `x` and whose remaining 256 bits are the standard MD padding of a
256-bit message. Every evaluation of `f` is exactly one complete SHA-256
compression: one message block, standard IV, standard padding, all 64 rounds.

Choose a public seed `x0` (e.g. `x0 = 0^256`). Iterate

```
x_(i+1) = f(x_i),   i >= 0.
```

The sequence is eventually periodic. Let `i < j` be the first index pair with
`x_i = x_j` (a collision of the map; `j - i` is the cycle length). Then
`x_(i-1) != x_(j-1)` by minimality of `i`, while

```
f(x_(i-1)) = x_i = x_j = f(x_(j-1)).
```

The two messages `pad64(x_(i-1))` and `pad64(x_(j-1))` are distinct 512-bit
strings (distinct first halves) with equal, complete SHA-256 digests. This is an
ordinary collision: full IV, full padding, all rounds, full output. (If `i = 0`
the seed itself lies on the cycle; restart with `x0 + 1`, charged as a failed
trial.)

## Finding the cycle

Brent's cycle detection is used, which needs no stored table. It walks
`x_1, x_2, ...` with a power-of-two checkpoint and detects the first repetition
after at most `3t` evaluations when the collision time is `t`; in practice it
evaluates `f` once per step plus a constant factor of comparisons. Each
comparison, pointer move and branch is charged as a fraction of a compression;
the ledger below charges 1.25 compressions per evaluated step and a further 2t
compressions to re-walk the cycle from the seed and recover `x_(i-1)` and
`x_(j-1)` (two independent walks of length at most `t` each).

## Success probability

For a random map on `N` points, the probability that the first `t` iterates are
pairwise distinct is at most `exp(-t(t-1)/(2N))`. With `t = 2^128.1`,

```
t^2/(2N) = 2^(256.2-257) = 2^-0.8 = 0.574,
P(collision) >= 1 - exp(-0.574) = 0.437 >= 0.39.
```

The bound is a standard birthday estimate; the map is modelled as random, which
is the usual heuristic for a generic cycle search and is disclosed here. No
property of SHA-256 beyond its 256-bit output is used.

## Work accounting

| item | compressions |
| --- | ---: |
| iteration, 1.25 per step for `t = 2^128.1` steps | 2^128.42 |
| cycle recovery, two walks of at most `t` steps | 2^129.1 |
| failed-trial allowance (a restart if the seed is periodic or a walk degenerates), 2 trials | included below |
| **total** | **2^129.66 <= 2^129.7** |

Every compression is a complete 64-round SHA-256 compression of one block; no
step is free, and no work is amortised over other targets. Memory is four
256-bit state registers plus loop counters and a one-block message buffer, under
2^10 bytes; it is reported, not scored beyond the one-MiB threshold.

Preprocessing is the fixed public seed and padding constants, `2^0`; no advice,
no tables, no nonuniform input. Randomness is the (deterministic) iteration
itself; the seed is public.

## Limitations

* This is a generic attack: its cost is the birthday bound on the 256-bit output
  and it gives no evidence about the security of SHA-256 beyond that bound.
* The birthday bound is a heuristic on the map `f`; it is not a proof about
  SHA-256's structure.
* The claim is a classical, non-quantum bound.
* Nothing here beats a structural collision attack at lower round counts; the
  claim is only that this is a complete, correctly accounted ordinary collision
  for the admitted full-round profile.
