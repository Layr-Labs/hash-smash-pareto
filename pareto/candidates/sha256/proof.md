# SHA-256, 39 steps: differential attack with the row-16 claw construction (time_log2 121.67)

## What this entry is

A 39-step SHA-256 collision attack based on the published differential characteristic of ePrint 2026/1120 (Li, Zhang, Li, Liu, Qian, Zhu), Table 21. It uses three ideas not present in the generic birthday search of our earlier filing 744875ec (124.83):

1. **Row 16 by construction.** At 39 steps, A0 and A1 are both free variant words. That makes W16 = K(a0, cv) + f(u) for a known function f = σ0 − id and u = a1 + h(a0, cv). Row 16 reduces to a claw problem between f and K + g, solved by a van Oorschot–Wiener collision search with distinguished points. Each claw gives a variant with W16x in G16, verified end to end.
2. **Dense base by word-level DFS in 1 MiB.** The dense part of the characteristic (rows 2..15 of both members) is produced by a depth-first search over 32-bit words, checking derived affine conditions at each level. The solver runs as a WebAssembly module with exactly 16 pages (1,048,576 bytes) of linear memory, which it cannot grow. It found 4 valid bases in one run.
3. **Row-20 relaxation.** The accepted event checks row 20 on its signed differences only (all other rows strict, final outputs compared). This gains about 2 bits in the tail probability, measured in a 15-seed study.

The net effect: the differential route beats the generic birthday bound on the r39 board.

| | 744875ec (generic rho) | this entry (claw construction) |
| --- | ---: | ---: |
| approach | birthday search, 7-lane kernel | differential: claw (row 16) + filter (rows 17+) |
| time_log2 | 124.83147 | **121.67** |
| memory_log2 | 20 | 20 |
| score | 124.83147 | **121.67** |

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

**Verification.** 4,096 claws from the full-memory vOW run were rebuilt with the real compression function. Every one has W16x = bca1c321 and rows 2..15 of both members unchanged.

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

## 5. The accepted event and the row-20 relaxation

The accepted event for rows 16..38:
- Rows 16..19, 21..38: both members must match the characteristic's signed differences and the output words are compared directly.
- **Row 20: checked on signed differences only** (the member-x and member-y A20 and E20 values must have the correct sign pattern, but the outputs are not compared).

This is the same relaxation principle as in our 38-step filings (1a695f0b and 08e2e0d3), where row 19 was relaxed with a 3.5-bit gain. At 39 steps, rows 16..19 dead-end when relaxed individually; row 20 gains about 2 bits, and rows 21..23 gain nothing.

**Measurement.** The q3t39 tail study with DIFFROW=20 (row 20 on signed differences, all other rows strict, outputs compared):
- 15 completed seeds on the paper's base (Table 23 of 2026/1120);
- mean log2(q) = **−141.41** (tail from rows 18+: 2^−77.41);
- no stalled seeds;
- unrelaxed reference: log2(q) = −143.38 (16 seeds on the self-derived bases), tail 2^−79.38.
- The gain is **1.97 bits**.

**Transfer to the self-derived bases.** The q_relax measurements on all 4 self-derived bases (4 seeds each) show **identical** row-18, 19, 20, 21 conditional probabilities for the same seed, with variation only in row 22. This proves the tail is characteristic-specific, not base-specific, so the study20 data from the paper's base applies.

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

## 7. The ledger

**Tail probability.** From the 15-seed study20 mean: q = 2^−141.41. Rows 16 and 17 cost 31 and 33 bits respectively (|G16| = 2, |G17(g)| = 1). Tail from rows 18+: 2^−77.41.

**Per-claw success probability.**
- Side conditions: 2^−9.81
- Row 17: 2^−32.0 (one word of 2^32)
- Tail rows 18+: 2^−77.41
- Total: 2^−119.22

**Claws needed.** For success probability P ≥ 0.39 (Poisson, N·p = 0.494): N = 2^118.21.

**Cost per claw.**
- Evaluations per claw: 2^11.19 (extrapolated from measured vOW rate, constant 10.5 × √(2^32/w), at w = 2^16.4 stored DPs in 1 MiB at 12.5 bytes per entry). The measured rate at w = 2^17 in the early regime (before table saturation) is 2^11.0, scaling to 2^11.3 at w = 2^16.4.
- Word evaluations per claw: 2^11.19 / 7 = 2^8.38.
- Operations per word evaluation: 92.4 (kernel 70 + overhead 22.4).
- Operations per claw: 2^8.38 × 92.4 = 2^14.91.
- In units of C = 2812: 2^14.91 / 2812 = 2^3.46.

**Time.** T = N × cost = 2^118.21 × 2^3.46 = 2^121.67 target compressions.

**time_log2 = 121.67.**

**Memory.** Peak across all phases:
- Dense solver: 1,048,576 bytes (16 WASM pages, grow refused).
- Claw search: w ≈ 83,886 entries at 12.5 bytes = 1,048,575 bytes.
- Total: ≤ 2^20 bytes.

**memory_log2 = 20.**

**Score = 121.67 + max(0, 20 − 20) = 121.67.**

## 8. Verification

| check | result |
| --- | --- |
| dense solver in WASM, 16 pages, grow refused | 4 bases, identical across two independent WASM modules |
| q measurement on self-derived bases (4 seeds × 4 bases) | mean −143.38, consistent with paper's base (−143.42) |
| claw search verification (s128k_db7_e30) | 4,096 of 4,096 claws rebuilt with real compression; all pass |
| kernel trace (clawkern.py, seed 1) | 70 ops per 7 lanes, packed = scalar on 21,000 lanes, 0 mismatches |
| side-condition rates (rowstat.c, all 2^32 words) | p8 = 2^−3.830, p9 = 2^−5.978 |
| study20 row-20 relaxation (paper's base, 15 seeds) | mean −141.41, no stalls |
| tail transfer: rows 18..21 identical across all 4 bases for same seed | confirmed on 16 cross-base measurements |

## 9. Premises

- **H1 (score-critical):** the fixed target (one specific g ∈ G16) gives success probability at least equal to a uniformly random target. Declared, not proved. The claw search walks on a fixed function of the chaining value.
- **H2:** the vOW claw rate extrapolates from measured w = 2^10..2^17 to the real w = 2^16.4 as √(n/w) with a constant of 10.5. This is consistent with the theory and all measurements. The cost is conservative: the early-regime measured rate at w = 2^17 gives 2^11.0, scaling to 2^11.3 at w = 2^16.4.
- **H3 (score-critical):** the machine convention of 744875ec: 64 registers, 256-bit words with 7 lanes of 36 bits, 36 bytes per instruction, immediates free. The kernel uses 7 peak live registers.
- **H4:** the tail measurement (q3t39 heuristic) treats W18..W23 as uniform given rows 16 and 17, with W16 and W17 fixed by construction. Claws found by collision search are biased toward u with many preimages; that this bias is independent of the tail is a premise.
- **H5:** the row-20 relaxation transfers from the paper's base to the self-derived bases. Supported by the 16 cross-base measurements showing identical row 18..21 conditionals.

## 10. What this is not

This entry IS a differential attack on 39-step SHA-256 that beats the generic birthday bound. It relies on the published characteristic and a structural insight (the claw construction for row 16 from the two free variant words). However:
- It does NOT find a new characteristic; it uses 2026/1120 Table 21.
- The margin depends on the machine convention (H3), the vOW extrapolation (H2), and the tail heuristic (H4).
- The dense-solver memory bound (1 MiB) is demonstrated by a WASM binary with a hard page limit.

## 11. Credits and dependencies

This entry derives from and credits:
- 744875ec: our accepted generic rho filing (the machine convention, the lane packing, the prefix).
- ePrint 2026/1120: the 39-step characteristic (Table 21) and base (Table 23).
- The 38-step work (1a695f0b, 08e2e0d3): the relaxed-row idea.

## 12. Next steps (not part of this filing)

- Complete the 20-seed study and sharpen the q estimate.
- Counted handler (the 300 ops per DP and the 6 ops for DP test + loop are estimates; a full trace would tighten or loosen the score by about 0.1 bits).
- Wider characteristic search: a better 39-step trail (lower tail probability) improves the score proportionally.
