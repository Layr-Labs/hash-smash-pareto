# SHA-256, 39 steps: differential attack with the row-16 claw construction (time_log2 122.44)

## What this entry is

A 39-step SHA-256 collision attack based on the published differential characteristic of ePrint 2026/1120 (Li, Zhang, Li, Liu, Qian, Zhu), Table 21. It uses three ideas not present in the generic birthday search of our earlier filing 744875ec (124.83):

1. **Row 16 by construction.** At 39 steps, A0 and A1 are both free variant words. That makes W16 = K(a0, cv) + f(u) for a known function f = σ0 − id and u = a1 + h(a0, cv). Row 16 reduces to a claw problem between f and K + g, solved by a van Oorschot–Wiener collision search with distinguished points. Each claw gives a variant with W16x in G16, verified end to end.
2. **Dense base by word-level DFS in 1 MiB.** The dense part of the characteristic (rows 2..15 of both members) is produced by a depth-first search over 32-bit words, checking derived affine conditions at each level. The solver runs as a WebAssembly module with exactly 16 pages (1,048,576 bytes) of linear memory, which it cannot grow. It found 4 valid bases in one run.
3. **Row-20 relaxation.** The accepted event checks row 20 on its signed differences only (all other rows strict, final outputs compared). This gains about 2 bits in the tail probability, measured directly on the base shipped with this entry (b1, 20-seed study).

The net effect: the differential route beats the generic birthday bound on the r39 board.

| | 744875ec (generic rho) | this entry (claw construction) |
| --- | ---: | ---: |
| approach | birthday search, 7-lane kernel | differential: claw (row 16) + filter (rows 17+) |
| time_log2 | 124.83147 | **122.44** |
| memory_log2 | 20 | 21 |
| score (hashsmash-scalar-tm-v1) | 124.83147 | **123.44** |

## 1. The published characteristic and the variant attack

The 39-step characteristic from ePrint 2026/1120, Table 21, is a signed-difference trail with message differences in W8..W12, W16, W17, W24, W26 (the shifted shape, HW 25). The two-block variant attack fixes rows 2..15 of the dense base S (A2..A15, E6..E15 of both members, and W10..W15) and leaves A0 = a0 and A1 = a1 free; W0..W9 are recomputed from the chaining value cv = H(first block).

At 38 steps, only A0 is free (E4 carries conditions). At 39 steps, E4 and E5 carry no conditions, so A1 is free too. This extra freedom enables the row-16 construction.

## 2. The claw construction for row 16

From the free words and the dense base:
- W0 = a0 + k0(cv)
- W1 = u := a1 + h(a0, cv), a bijection between a1 and u for fixed (a0, cv)
- W9 = c9 − a1 (E5 = a1 + const, the rest of row 9 fixed)
- **W16 = σ1(W14) + W9 + σ0(W1) + W0 = Kc(a0, cv) + f(u), with f(u) = σ0(u) − u.**

For fixed (a0, cv), the offset Kc is a known constant, and f(u) = σ0(u) − u is a fixed function on 32-bit words. Row 16 holds when W16x ∈ G16 = {bca1c121, bca1c321}; only bca1c321 admits a row-17 word (a single W17x). So the task is to find u with f(u) = g − Kc(a0, cv), where g = bca1c321.

This is a **claw problem**: define F(x) = f(x) for odd x and F(x) = g − Kc(x, cv) for even x. A collision F(x) = F(y) with x odd and y even gives a claw (a0 = y, u = x), and a1 = u − h(a0, cv) puts W16x = g.

**Verification.** 4,096 claws from the full-memory vOW run were rebuilt with the real 39-step compression function. Every one has W16x = bca1c321 and rows 2..15 of both members unchanged.

**The function f** = σ0(u) − u behaves as a random function: its image covers 63.4% of 2^32 values (0.6321 expected), with a matching preimage histogram.

## 3. Side conditions

W8 and W9 vary with the variant. They enter the message schedule at W23 (σ0(W8)), W24 (σ0(W9), W8) and W25 (W9). A variant must keep:
- σ0(W8x + D8) − σ0(W8x) = DS8, so that W23's difference holds;
- σ0(W9x + D9) − σ0(W9x) = DS9, so that W24's modular difference holds.

**Exact rates** (m39/rowstat.c, all 2^32 words):
- p8 = 2^-3.830, from two XOR patterns: 2^-4.00 and 2^-7.00;
- p9 = 2^-5.978, from two XOR patterns: 2^-6.00 and 2^-12.00;
- together **2^-9.808**.

## 4. Dense-base solver in 1 MiB

The dense part (rows 2..15) is searched by a depth-first enumeration of the 32-bit state words A8..A15 (each E and W word follows from the affine relations). At each level, the solver enumerates only the values that satisfy the affine conditions on that word alone (a coset of GF(2)^32), then checks the full conditions that become decidable after deriving the dependent words. The search order is A8, A9, A10, A11, A12, A13, A14, A15 (E11..E6 are derived, then W10..W12).

**WebAssembly implementation** (dense39_x.wasm, 94,483 bytes):
- Memory: 16 pages = 1,048,576 bytes, with maximum also 16 pages (grow refused).
- Layout: static data ends at 149,633 bytes, heap base (stack top) at 411,792 bytes, deepest stack use 3,359 bytes.
- **Result**: 4 valid bases from one run (seed 0, 44,439 seconds in the WASM interpreter). All 4 produce the same |G16| = 2 and |G17(bca1c321)| = 1.
- Verification: a separate demo run (dense39.wasm, 34,851 bytes, also 16 pages = 1 MiB) finds the same 4 bases.

**Dense-phase peak memory** (charged under collision-frontier-v5): the WASM module code (94,483 bytes) plus its linear memory (1,048,576 bytes) totals 1,143,059 bytes. This exceeds 2^20. The cost model charges code alongside data, so the dense phase requires memory_log2_bytes ≥ 21. See Section 7.

## 5. The accepted event and the row-20 relaxation

The accepted event for rows 16..38:
- Rows 16..19, 21..38: both members must match the characteristic's signed differences and the output words are compared directly.
- **Row 20: checked on signed differences only** (the member-x and member-y A20 and E20 values must have the correct sign pattern, but the outputs are not compared).

This is the same relaxation principle as in our 38-step filings (1a695f0b and 08e2e0d3), where row 19 was relaxed with a 3.5-bit gain. At 39 steps, rows 16..19 dead-end when relaxed individually; row 20 gains about 2 bits, and rows 21..23 gain nothing.

**Measurement on the filed base (b1), with DIFFROW=20:**
- 20 seeds launched, **19 completed, 1 stalled** (seed 218, counted as 0).
- Mean log2(q) = **−141.306** (tail from rows 18+: **2^−77.31**).
- **99% bootstrap lower bound**: log2(q) = **−141.96** (conservative tail: **2^−77.96**).
- Unrelaxed reference: mean log2(q) = −143.38 (16 seeds on all 4 self-derived bases), tail 2^−79.38.
- Gain from relaxation: **1.97 bits** (point), **1.42 bits** (conservative).

The conservative (99% bound) tail is used in the filed score to account for finite-sample uncertainty and the stalled seed.

## 6. The kernel

The walk function F on packed 7-lane 36-bit words:
- F(x) = f(x) = σ0(x) − x for odd x;
- F(x) = C + Σ0(x) + MAJ(x, A−1, A−2) + Σ1(E0) + CH(E0, E−1, E−2) − x for even x, with E0 = x + e0 and all constants cv-dependent.

The two sides are computed for all lanes and blended by the low bit of x.

**Counted by a tracer (m39/clawkern.py):**

| component | ops per word (7 lanes) |
| --- | ---: |
| kernel (even side + odd side + blend) | **70** |
| DP test + loop | 6 |
| handler (amortized at dp_bits = 7) | 16.4 |
| **total** | **92.4** |

Per lane: **13.2 operations per evaluation.** Verified: the packed kernel matches the scalar F on 21,000 lanes with 0 mismatches, across 4 random chaining values.

The overhead (22.4 ops) is estimated, not counted by a tracer. A full trace could shift it by about 0.1–0.3 bits; this is disclosed in H3.

## 7. The ledger

### Tail probability

From the b1 20-seed study (Section 5), using the 99% bootstrap lower bound:
- q = 2^−141.96 (conservative)
- Rows-0-to-17 prefix: 2^−64.0 (characteristic-determined, stable across studies)
- **Tail (rows 18+): 2^−77.96** (conservative)

### Per-claw success probability

| component | log2 |
| --- | ---: |
| side conditions (p8 × p9) | −9.81 |
| row 17 (one 32-bit word) | −32.00 |
| tail rows 18+ (conservative) | −77.96 |
| **per-claw total** | **−119.77** |

### Claws needed

For success probability P ≥ 0.39 (Poisson, N·p ≥ −ln(0.61) = 0.494 = 2^−1.017):
**N = 2^118.76.**

### Cost per claw

**DP table:** 128K slots at 12.5 bytes per entry = 1,638,400 bytes, dp_bits = 7. This matches the s128k_db7_e30 experiment configuration exactly.

**Evaluations per claw: 2^11.41** (the saturated rate from the s128k run). Rationale: the full attack generates 2^118+ claws; the table spends essentially all of its time saturated. The early-regime rate (2^11.0) applies only to the first ~2^17 claws, a negligible fraction. This is an extrapolation heuristic (H2): the 2^30-evaluation run observed 566,025 claws at a saturated rate, and we extrapolate that rate to the 2^118.76 claws needed by the attack.

| step | value |
| --- | ---: |
| evaluations / claw | 2^11.41 |
| word evaluations / claw (÷ 7 lanes) | 2^8.60 |
| ops / word eval | 93 |
| ops / claw | 2^15.14 |
| target-compressions / claw (÷ C = 2812) | 2^3.68 |

### Omitted-work accounting

Side-condition checking (~20 ops per claw), row-17 checking (~5 ops per passing claw), message reconstruction (2 × C per candidate), and collision verification (C per candidate) are all negligible per evaluation: side checking adds 20 / 2^8.60 ≈ 0.05 ops/word-eval, and reconstruction/verification happen once per 2^119.77 claws. Restart overhead (table init: 2^17 writes per restart, one restart per ~2^24 evaluations) adds ~0.008 ops/eval. The total omitted work adds < 0.1 ops per word evaluation, absorbed into the margin between 92.4 and a rounded 93.

### Time

T = N × cost = 2^118.76 × 2^3.68 = **2^122.44 target compressions**.

### Memory

Peak across phases (charged under collision-frontier-v5, which includes code, advice, working state, and tables):

| phase | total bytes | log2 |
| --- | ---: | ---: |
| dense solver (1,048,576 linear + 94,483 module) | 1,143,059 | 20.12 |
| claw search (1,638,400 table + ~5,000 code + ~1,200 state + 1,024 advice) | ~1,645,624 | 20.65 |
| **peak = max** | **~1,645,624** | **20.65** |

**memory_log2_bytes = 21** (2 MiB envelope).

### Score

**score = 122.44 + max(0, 21 − 20) = 123.44** (hashsmash-scalar-tm-v1: timeLog2 + log2(memoryUnits), memoryUnit = 1 MiB, min 1).

Margin below the leader (744875ec at 124.83): **1.39 bits** (conservative).

### Preprocessing and advice

The dense solver is a one-time preprocessing step producing the 4 bases. Charged as total word operations in the DFS: approximately 2^40 nodes at ~200 ops/node = 2^47.6 word ops, or 2^47.6 / 2812 ≈ 2^36.1 target compressions. Filed as **preprocessing_log2 = 37** (rounded up from 36.1; the solver is not instrumented at the word-operation level, so the ceil is conservative).

Nonuniform advice: 1 dense base = 4 state words (A, E of both members at the dense boundary) × 4 bytes = 16 bytes per word × 4 words = 64 bytes. With the derived message words, a full base occupies 256 bytes (4 state words plus 12 message words at 4 bytes each). With all 4 bases: 1,024 bytes. Filed as **nonuniform_advice_log2_bytes = 10**.

## 8. Verification

| check | result |
| --- | --- |
| dense solver in WASM, 16 pages, grow refused | 4 bases, identical across two independent WASM modules |
| q on self-derived bases (4 seeds × 4 bases, unrelaxed) | mean −143.38, consistent with paper's base (−143.42) |
| **q on b1 (filed base), row-20 relaxation, 20 seeds** | **19 completed, 1 stall; mean −141.306; 99% bound −141.96** |
| claw search verification (s128k_db7_e30) | 4,096 of 4,096 claws rebuilt with real compression; all pass |
| kernel trace (clawkern.py, seed 1) | 70 ops per 7 lanes, packed = scalar on 21,000 lanes, 0 mismatches |
| side-condition rates (rowstat.c, all 2^32 words) | p8 = 2^−3.830, p9 = 2^−5.978 |
| side-condition sampling (sidecond.py, organizer) | 2^20-sample rates match exhaustive counts on all trials |
| claw construction algebraic check (clawexp.py, organizer) | walk function matches SHA-256 step computation on all trials |
| claw existence (clawverify.py, organizer) | 6–12 claws per trial from 2^15 targets, all preimages verified |

## 9. Premises (heuristics)

- **H1 (score-critical):** the fixed target (one specific g ∈ G16) gives success probability at least equal to a uniformly random target. Declared, not proved. The claw search walks on a fixed function of the chaining value. Evidence: the image coverage (63.4%) and 4,096 verified claws all producing W16x = g = bca1c321.
- **H2 (score-critical):** the saturated rate of 2^11.41 evaluations per distinct claw, measured at 128K slots with 2^30 evaluations (566,025 distinct claws), applies to the full 2^118.76 claws needed by the attack. This is an extrapolation: the early-regime rate (2^11.0) gives way to the saturated rate once the DP table fills (~2^17 claws), and the saturated rate is stable over the latter portion of the 2^30-evaluation run. However, the run produced far fewer claws than the 2^118.76 needed, so rate drift at scale (due to function-graph structure, cycle lengths, or collision depletion) is possible but unquantified.
- **H3 (score-critical):** the machine convention of 744875ec: 64 registers, 256-bit words with 7 lanes of 36 bits, 36 bytes per instruction, immediates free. The kernel uses 7 peak live registers. The overhead (22.4 ops beyond the 70-op kernel, charged as 23) is estimated, not fully traced; a full trace could shift the score by 0.1–0.3 bits.
- **H4 (score-critical):** the tail measurement (q3t39 estimator with row-20 relaxation) applies when W16 and W17 are fixed by the claw construction. Claws produced by the vOW search may be biased toward u values with many f-preimages; independence of this bias from the tail event is assumed. The conservative (99% bootstrap bound) tail is used to absorb finite-sample uncertainty.
- **H6 (score-critical):** the N generated claws behave as sufficiently independent Bernoulli trials for the Poisson success formula. The per-claw success probability p = 2^−119.77 is assumed to hold independently across claws. In practice, claws from the vOW search on different chaining values are functionally independent (different functions F); claws from the same chaining value share a function but draw from different f-preimages. No duplicate-rate or formal dependence analysis is supplied; the 566,025 distinct claws from 2^30 evaluations in the s128k run showed no anomalous clustering.

## 10. What this is not

This entry IS a differential attack on 39-step SHA-256 that beats the generic birthday bound. It relies on the published characteristic and a structural insight (the claw construction for row 16 from the two free variant words). However:
- It does NOT find a new characteristic; it uses 2026/1120 Table 21.
- The margin depends on the machine convention (H3), the tail heuristic (H4), and the inter-claw independence premise (H6).
- The dense-solver memory bound (1 MiB linear memory) is demonstrated by a WASM binary with a hard page limit; the module code (94,483 bytes) pushes the total memory charge to 2^21.
- The experiment (Section 8) tests the algebraic correctness of the claw construction, not the packed kernel. The packed-kernel operation count and register allocation are claimed by the tracer (H3) and not independently validated by an organizer experiment.

## 11. Credits and dependencies

This entry derives from and credits:
- 744875ec: our accepted generic rho filing (the machine convention, the lane packing, C = 2812).
- ePrint 2026/1120: the 39-step characteristic (Table 21) and base (Table 23).
- The 38-step work (1a695f0b, 08e2e0d3): the relaxed-row idea.

## 12. Next steps (not part of this filing)

- Counted handler (the 22.4 ops of overhead beyond the 70-op kernel are estimates; a full trace would tighten or loosen the score by about 0.1–0.3 bits).
- Wider characteristic search: a better 39-step trail (lower tail probability) improves the score proportionally.
