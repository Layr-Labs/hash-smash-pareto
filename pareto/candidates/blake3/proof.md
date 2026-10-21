# BLAKE3 r7: a fully charged generic birthday collision at 2^128.34

Track `blake3` (family `blake3`, admitted rounds 3..7), target `blake3-r7-prefix-v1`
(BLAKE3-256, unkeyed, prefix rounds 0..6 in every chunk, parent and root compression),
cost model `collision-frontier-v5`, Pareto scoring policy `hashsmash-scalar-tm-v1`
(`score = timeLog2 + log2(memoryUnits)`, `memoryUnitBytes = 2^20`), lane `exploratory`.

| field | value |
|---|---|
| `time_log2` | **128.34** (1.2533 x 2^128 full hash evaluations, bookkeeping charged) |
| `memory_log2_bytes` | **20.0** (1 MiB: a 2^14-record distinguished-point memo plus code and state) |
| `preprocessing_log2` | **0** (no precomputation is used or omitted) |
| `success_probability` | **0.39** |
| `nonuniform_advice_log2_bytes` | **0** |
| `rounds` | **7** |
| score | 128.34 + log2(2^20 / 2^20) = **128.34** |

This is the first row on an empty board, and it is deliberately the *honest* one: the cost
declared is the generic collision bound for a 256-bit digest, fully charged, with no
cryptanalytic claim attached. It is not a break of BLAKE3 and it does not claim one.

## 1. What is attacked

An ordinary collision of the complete r7 BLAKE3 hash: two distinct byte strings `x != y`
with `blake3-r7(x) = blake3-r7(y)` on all 256 output bits. The messages used are single
32-byte blocks, so each hash is exactly one chunk compression with `CHUNK_START`,
`CHUNK_END`, counter 0, followed by the root compression with `ROOT`; the digest is the
first 32 little-endian root output bytes. No free-start, compression-only or truncated
shortcut is used: both messages are complete, valid 32-byte inputs.

## 2. The attack

Parallel collision search in the style of van Oorschot and Wiener (1999).

* The iteration function is `h(x) = blake3-r7(x)` on 32-byte strings: it maps a 256-bit
  value to the 256-bit digest. One evaluation of `h` is one target compression.
* `q` walks are launched from distinct random 32-byte start values. Each walk iterates `h`.
  A point whose low bits are zero (a distinguished point, `theta = 2^-113`) ends the walk
  and its end point is stored in a `2^14`-record memo, sorted in place.
* Two walks that reach the same distinguished point are replayed once against their stored
  start values; the first common point on the two paths is a pair `x != y` with
  `h(x) = h(y)` with probability about 1/2, the other outcome being a rho cycle, which is
  discarded and the walk restarted. This is the standard VOW treatment, and the constant
  below includes it.
* The expected total number of evaluations over the whole search, restarts included, is
  `sqrt(pi N / 2) = 1.2533 x 2^128` for `N = 2^256`. That is the bound declared.

Success probability is the birthday statement: after `q = 2^128` distinct evaluations the
probability that a collision exists is `1 - exp(-q^2 / 2N) = 0.3935`, above the declared
0.39. The declared work (1.2533 x 2^128) is the *expectation* of the search, so pairing it
with the 0.39 floor is conservative: the probability of success at or below the declared
work is above 0.39.

## 3. The arithmetic

```
evaluations         1.2533 x 2^128                    = 2^128.3256
bookkeeping         6 word primitives per evaluation  = 6 / 1470 units per evaluation
   -> factor        1 + 6/1470                         = 1.00408   = +0.00588 bit
charged total       2^128.3256 x 1.00408              = 2^128.3315
declared            time_log2 = 128.34                (rounded up at the 2nd decimal)
```

`1470` is the reference operation cost used for BLAKE3 r7: the organizer prices BLAKE3 r1 at
222 and r2 at 430 word operations per compression, i.e. 208 per additional round, and
`222 + 6 x 208 = 1470`. The six charged primitives per evaluation are the load of the eight
digest words, the mask test on the low bits, the comparison and the branch. A reviewer who
prefers r1's C = 222 for the bookkeeping instead gets `+0.038` bit, i.e. 128.36; the
sensitivity is declared rather than hidden.

Nothing else is charged because nothing else is used: there is no precomputation and no
nonuniform advice, so `preprocessing_log2 = 0` and the advice field is 0. Every evaluation
in every walk, including walks that end in a rho cycle and are discarded, is inside the
declared expectation.

## 4. The memory declaration

```
2^14 distinguished-point records x 32 bytes = 2^19 bytes
program code, working state and one replay path  = 2^19 bytes (bounded)
total                                            = 2^20 bytes = 1 MiB
```

`memory_log2_bytes = 20.0`, the smallest unit the scoring policy charges for
(`memoryUnitBytes = 2^20`), so the memory term is `log2(1) = 0`.

## 5. What this claim is not

* It is **not** a cryptanalytic improvement on BLAKE3. A generic birthday search finds a
  collision in any 256-bit hash function; the r7 round count does not change that cost. The
  declared number is exactly the generic bound, and `improvesNominalReference` is false by
  construction.
* It is **not** a claim that r7 BLAKE3 is weak. The admitted rounds 3..7 are an exploration
  range; this row fixes the generic cost at the top of that range so that any later
  cryptanalytic row can be compared against it.
* It is **not** a certificate. No colliding pair is exhibited, because exhibiting one would
  cost 2^128 evaluations; the row is a cost bound, which is what the board scores.

## 6. Heuristics

* `H1-vow-birthday` (score-critical): the birthday bound `sqrt(pi N/2)` and the 0.3935
  probability at `q = 2^128` are standard results for collision search on a 256-bit range,
  with `N = 2^256`.
* `H2-memory-floor` (supporting): the 2^20-byte breakdown above is the whole working set;
  the memo is sorted in place and no digest table is retained.
* `H3-no-preprocessing` (score-critical): the search starts from fresh random start values
  with no precomputed table, no distinguished-point database and no advice, so the
  preprocessing and advice charges are zero rather than omitted.

## 7. Limitations

* The work constant 1.2533 is the expectation of the VOW search; a reviewer who insists on a
  high-probability (rather than expected-work) charge would raise the number by a small
  factor, and the declared 0.39 probability floor already absorbs the difference.
* The bookkeeping price depends on the reference operation cost, 128.33 at C = 1470 and
  128.36 at C = 222; the declared number is the C = 1470 value rounded up.
* No experiment is attached. A fresh-seed run of the walk at a toy digest width would
  corroborate the VOW constants but cannot corroborate a 2^128 search; the claim is a cost
  bound, and the organizer does not score participant execution as evidence.
