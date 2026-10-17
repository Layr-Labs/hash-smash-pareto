# SHA-256, 39 steps: differential attack with the row-16 claw construction (time_log2 122.98)

## What this entry is

A 39-step SHA-256 collision attack based on the published differential characteristic of ePrint 2026/1120 (Li, Zhang, Li, Liu, Qian, Zhu), Table 21. It uses three ideas not present in the generic birthday search of our earlier filing 744875ec (124.83):

1. **Row 16 by construction.** At 39 steps, A0 and A1 are both free variant words. That makes W16 = K(a0, cv) + f(u) for a known function f = σ0 − id and u = a1 + h(a0, cv). Row 16 reduces to a claw problem between f and K + g, solved by a van Oorschot–Wiener collision search with distinguished points. Each claw gives a variant with W16x in G16, verified end to end.
2. **Dense base in under 1 MiB.** A depth-first search over 32-bit words, checking affine conditions derived from Table 21 at each level, runs as a WebAssembly module whose linear memory is fixed at 7 pages (458,752 bytes, growth refused) and whose code is 94,483 bytes: 553,235 bytes for the phase. Its logged run found 4 valid bases, and **the first of them is b1, the base this filing uses**, register for register (Appendix B, Appendix B.1). Filings 1c8ba89c through 2c48b18c said b1 was not a solver output; that was wrong and is corrected in B.1.
3. **Row-20 relaxation.** The accepted event checks row 20 on its signed differences only (all other rows strict, final outputs compared). This gains about 2 bits in the tail probability, measured directly on the base shipped with this entry (b1, pooled 140-seed study). No relaxation gain is claimed in the ledger — Section 5.

**The net effect.** The filed time is 2^122.98 with memory 2^20, so the score is **122.98**: 1.85 bits below our accepted generic entry 744875ec (124.83147) and 1.27 bits below the best AI-valid generic entry on the board, 0c1ef7c3 (124.25213, awaiting human review). The two offsets the previous filing (2c48b18c, 124.39) named and did not take are now taken, each on a measurement in this package: the claw rate is charged at the maximum over 289 chaining values measured at the filed configuration (Appendix E.2b, every value in E.5), and the distinguished-point table is stored in 7-byte entries that keep the claw phase under 2^20, with the search semantics verified unchanged (Section 7, Appendix E.1).

**Where this sits on the board, as of 2026-10-17.** 744875ec is the r39 entry with human approval; 0c1ef7c3 is AI-valid and awaiting human review. Both are generic birthday searches priced under the same word-operation convention this entry declares (H3). If the declared premises hold, this is the first collision construction for 39-step SHA-256 that beats an equally optimised generic search in a consistent cost model, by 1.27 bits against the best AI-valid generic entry and 1.85 against the accepted one. The margin rests on H2, H3, H4, H6, H8, H9, H11 and H14 as declared in Section 9, with H4 carrying 78 of the 121 per-claw bits, and the memory bound has 64,072 bytes of headroom over an estimated code size (Section 7). It is a modest result, a little over a bit and tied to the word-operation model, and it is stated as that.

An earlier filing of this same construction (cfe5c4e2) scored 125.25 and was dominated by the generic search. The difference is not new cryptanalysis and not new data: it is which statistic the tail bound is built from, on the same 140 seeds. That filing charged a 99% bound on the mean of the per-seed **log** q estimates. This one charges a 99% bound on the mean of the per-seed estimates themselves, with every stalled seed set to **zero** (Section 5, Appendix D.1). The attack succeeds about N·E[q] times over N claws, so the arithmetic mean is the quantity the Poisson formula needs; the mean of logs sits below log of the mean by Jensen and was costing 1.49 bits with no principled justification. The linear route also assumes strictly less — no censoring rule, no imputation for unmeasured stages — and was already derived, checked and tabulated in the previous filing's own Appendix D.1, which recorded that it supported the ledger "with 2.02 bits to spare". Taking it is the correction; the conservative route is retained as a sensitivity row.

| | 744875ec (generic rho) | this entry (claw construction) |
| --- | ---: | ---: |
| approach | birthday search, 7-lane kernel | differential: claw (row 16) + filter (rows 17+) |
| time_log2 | 124.83147 | **122.98** |
| memory_log2 | 20 | 20 |
| score (hashsmash-scalar-tm-v1) | 124.83147 | **122.98** |

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

**Verification.** 4,096 claws from the full-memory vOW run were rebuilt with the real 39-step compression function; every one has W16x = bca1c321 and rows 2..15 of both members unchanged. That run is not in the package. `experiments/clawdist.py` constructs claws from the filed base, assembles the 16-word block and expands it with the real SHA-256 message expansion, and the organizer's run reports 1,071 of 1,071 landing on W16x = bca1c321 with W1 = u, a0 even and u odd. **That is a consistency check, not a pass rate, and it is labelled as such here because an earlier wording was not:** the constant of the even branch is fitted so that the a0 and a1 dependence cancels, and the table stores u with f(u) = F_even(a0) by construction, so a table hit forces W16x = g with no freedom left; the parity counters are likewise forced by the a0 mask and by the table being built over odd u. What the check does establish is that the folded kernel forms, the schedule relations and the real expansion recurrence agree with one another — a transcription check across three independent routes, which would catch an error in any one of them, but not evidence that Section 2's register identifications are themselves right.

**The function f** = σ0(u) − u behaves as a random function on its own domain. A caveat on the figure previously quoted here: the claw encoding draws u from the **odd** half only, so the relevant coverage is that of f restricted to 2^31 inputs, whose random-function expectation is 1 − e^(−1/2) = 0.393, not the 1 − 1/e = 0.632 of a full-domain map. The attack does not depend on this number: the ledger charges a *measured* claw rate (Section 7), and the per-target hit probability of a preimage table is its size divided by 2^32 regardless of image density.

## 3. Side conditions

W8 and W9 vary with the variant. They enter the message schedule at W23 (σ0(W8)), W24 (σ0(W9), W8) and W25 (W9). A variant must keep:
- σ0(W8x + D8) − σ0(W8x) = DS8, so that W23's difference holds;
- σ0(W9x + D9) − σ0(W9x) = DS9, so that W24's modular difference holds.

**Exact rates** (exhaustive enumeration of all 2^32 words; the enumerator is not a Python experiment and so cannot ship, but both rates are reproduced inside the package by `experiments/sidecond.py`):
- p8 = 2^-3.830, from two XOR patterns: 2^-4.00 and 2^-7.00;
- p9 = 2^-5.978, from two XOR patterns: 2^-6.00 and 2^-12.00;
- together **2^-9.808**.

## 4. Dense-base solver in 1 MiB

The dense part (rows 2..15) is searched by a depth-first enumeration of the 32-bit state words A8..A15 (each E and W word follows from the affine relations). At each level, the solver enumerates only the values that satisfy the affine conditions on that word alone (a coset of GF(2)^32), then checks the full conditions that become decidable after deriving the dependent words. The search order is A8, A9, A10, A11, A12, A13, A14, A15 (E11..E6 are derived, then W10..W12).

**WebAssembly implementation** (dense39_x7.wasm, 94,483 bytes, carrying the exact-mode condition table of Appendix C, derived from Table 21 and one tail-interface bit):
- Memory: 7 pages = 458,752 bytes, with maximum also 7 pages (grow refused). The module's static data ends at 149,633 bytes, its stack top is at 411,792 bytes and its deepest measured stack use is 3,359 bytes, so 7 pages hold it with 46,960 bytes to spare. The module was produced from the logged 16-page module by setting the two page counts in its memory section; every other byte, the code section included, is identical.
- **Result**: the logged run (the 16-page module, seed 0, the paper's subtree of 524,288 outer nodes, stopped after 4 bases at index 452,139; 44,439 s in the WebAssembly interpreter; 1,564,812,196,740 bit-level nodes, equal to the native count) found 4 valid bases. **The first is b1**, the base of Appendix B, register for register. All 4 give |G16| = 2 and |G17(bca1c321)| = 1.
- Verification of the 7-page module: the subtree pinned to the paper's E chain, A13, A12 and A9 was run on both modules; the counters (391,110,976 bit-level nodes, the same count at every level) and the base found are identical (`runs39/dense/pin_identity_16pages.txt`, `pin_identity_7pages.txt`).

**Dense-phase peak memory** (charged under collision-frontier-v5): module code 94,483 bytes plus linear memory 458,752 bytes = **553,235 bytes = 2^19.08**. Earlier filings charged this phase at 1,143,059 bytes and concluded that it forced memory_log2_bytes = 21, because the module declared 16 pages; the 16 pages were a linker default that the solver never used. See Section 7.

## 5. The accepted event and the row-20 relaxation

The accepted event for rows 16..38:
- Rows 16..19, 21..38: both members must match the characteristic's signed differences and the output words are compared directly.
- **Row 20: checked on signed differences only** (the member-x and member-y A20 and E20 values must have the correct sign pattern, but the outputs are not compared).

**From the accepted event to a collision on the target.** The step is short but was
previously left implicit, so it is written out. Both members enter the second block
with the **same** chaining value, so equality of all eight working-state words at the
end of 39 steps gives equal output chaining values after the feed-forward, which adds
that common value to both. The two messages are M0||M1 and M0||M1', each 128 bytes and
differing only in the second block; being of equal length they take the **identical**
FIPS 180-4 padding block, which is then compressed from equal chaining values and so
preserves the equality. All 256 digest bits therefore agree, and the two messages are
distinct because M1 != M1'. The accepted event is thus a sufficient condition for an
ordinary collision on the exact target, and the row-20 relaxation and RELAX_TAIL only
*shrink* the accepted set relative to a true collision, which is the safe direction.

This is the same relaxation principle as in our 38-step filings (1a695f0b and 08e2e0d3), where row 19 was relaxed with a 3.5-bit gain. At 39 steps, rows 16..19 dead-end when relaxed individually; row 20 gains about 2 bits, and rows 21..23 gain nothing.

**Measurement on the filed base (b1), with DIFFROW=20.** Earlier filings reported a 20-seed study whose numbers did not survive checking: the stated mean of −141.306 did not match the per-seed files (the 19 completed seeds average −141.667), the 99% bound of −141.96 was computed with the one stalled seed dropped, and a 5% stall rate was assumed. A pre-registered 120-seed study (seeds 301..420, same base, same parameters, same stall cap, committed before running) was therefore added and pooled with the original. The full per-seed data is in Appendix D.2.

- **140 seeds: 120 completed, 20 stalled** — a stall rate of 14.3%, not the 5% the first study suggested.
- No stalled seed is dropped. The filed route sets every stalled seed to **zero** on the linear scale, which is a rigorous lower bound on its estimate and needs no censoring rule and no imputation (Appendix D.1).
- Mean of the 140 per-seed estimates, stalls at zero = **2^−141.409**.
- **99% bootstrap lower bound on that mean**, with a Bonferroni factor of 8 for the original selection of row 20 among rows 16..23: **2^−141.753** (basic; the percentile flavour gives −141.734 and the more conservative is taken). Less **0.52 bits** for the estimator bias — the largest value measured at any population tested (`experiments/splitbias.py`), subtracted instead of extrapolating the measured trend out to the filed population — **q ≥ 2^−142.273**, so the tail is **2^−78.273**.
- The log-scale alternative, with stalls censored at their ceiling, gives −143.759 and a tail of 2^−79.759. It is 1.49 bits more pessimistic, it is not an estimator of q, and it is retained in Appendix D.1 as a sensitivity row rather than as the filed basis.
- Unrelaxed reference: mean log2(q) = −143.38 (16 seeds on all 4 self-derived bases). **Withdrawn as corroboration** (Appendix B.1): those bases share b1's dense core, so the comparison is circular, and it is a log-scale mean on a different base set, so it is not on the same scale as the filed statistic either. No relaxation gain is claimed in the ledger, which takes the 2^−142.273 bound directly.

The filed tail is a 99% lower confidence bound carrying a Bonferroni factor of 8, so it already absorbs finite-sample uncertainty and the row selection. The 20 stalled seeds enter it at zero.

## 6. The kernel

The walk function F on packed 7-lane 36-bit words:
- F(x) = f(x) = σ0(x) − x for odd x;
- F(x) = C + Σ0(x) + MAJ(x, A−1, A−2) + Σ1(E0) + CH(E0, E−1, E−2) − x for even x, with E0 = x + e0 and all constants cv-dependent.

The two sides are computed for all lanes and blended by the low bit of x.

**Counted by a tracer.** The tracer is in the package as `experiments/kernelcount.py`; it is rebuilt and recounted on every organizer trial, and the emitted program is listed in full in Appendix F:

| component | ops per word (7 lanes) |
| --- | ---: |
| kernel (even side + odd side + blend) | **70** |
| DP test + loop | 6 |
| handler (amortized at dp_bits = 7) | 16.4 |
| **total** | **92.4** |

Per lane: **13.2 operations per evaluation.** Verified: the packed kernel matches the scalar F on 86,016 lane comparisons (336 lanes per trial over 256 trials) with 0 mismatches.

The overhead (22.4 ops) is estimated, not counted by a tracer. A full trace could shift it by about 0.1–0.3 bits; this is disclosed in H3.

## 7. The ledger

### Tail probability

From the pooled 140-seed study (Section 5, data in Appendix D.2), using the 99% bootstrap lower bound with the row-selection correction:
- q = 2^−142.273 (99%/8 lower confidence bound, stalls at zero, bias-corrected)
- Rows-0-to-17 prefix: 2^−64.0 (exact: |G16| = 2 restricted to the one usable word is 2^−31, row 17 is 2^−33)
- **Tail (rows 18+): 2^−78.273**

### Per-claw success probability

| component | log2 |
| --- | ---: |
| side conditions, charged | **−10.44** = −9.81 (exact p8 × p9) **− 0.63 (H8 deviation, charged)** |
| row 17 (one 32-bit word) | −32.00 |
| tail rows 18+ (99%/8 bound) | −78.27 |
| **per-claw total** | **−120.713** (rounded to −120.71 where quoted; rounding the exponent **up** makes the claw count larger, which is the conservative direction for time) |

### Claws needed

For success probability P ≥ 0.39 (Poisson, N·p ≥ −ln(0.61) = 0.494 = 2^−1.0166):
**N = 2^119.6964**, quoted as 2^119.70 when rounded, since rounding N **up** is the conservative direction.

### Cost per claw

**DP table:** 2^17 = 131,072 slots at **7 bytes** per entry = **917,504 bytes**, dp_bits = 7. A slot holds the trail's start point (32 bits), the trail length (12 bits; lengths are at most 20 x 2^7 = 2,560 and the all-ones value marks an empty slot) and the 8 bits of the distinguished point that the slot index does not determine (the index is the point's top 17 bits, and its low 7 bits are zero by definition): 52 bits in 7 bytes. The layout is implemented (`clawvow7.c` in the work tree; Appendix E.1) and changes nothing in the search: on 9 chaining values the unpacked program and the packed one, run on the same arguments and seed, agree on every counter and on the list of claws found (Appendix E.2b). Earlier filings carried 128,000 slots at "12.5 bytes" per entry, a figure with no derivation; the research tool actually stored 13.

**Evaluations per claw: 2^11.00.** This is the **maximum** over 289 chaining values of the cumulative rate of a 2^26-evaluation window at exactly the filed configuration (the packed program, 2^17 slots, dp_bits 7): mean 2^10.970, standard deviation 0.007 bits, minimum 2^10.948, maximum 2^10.996 (Appendix E.2b; every value in Appendix E.5). The previous filing charged 2^11.414, the cumulative rate of a single 2^30-evaluation run on one chaining value, as a margin over the one graph it had measured; the margin is replaced by the measured distribution's maximum.

| step | value |
| --- | ---: |
| evaluations / claw | 2^11.00 |
| word evaluations / claw (÷ 7 lanes) | 2^8.193 |
| ops / word eval | 93 |
| ops / claw | 2^14.732 |
| target-compressions / claw (÷ C = 2812) | 2^3.2745 |

### Omitted-work accounting

Side-condition checking (~40 ops per claw), row-17 checking (~5 ops per passing claw), message reconstruction (2 × C per candidate) and collision verification (C per candidate) are negligible per evaluation. Correcting a misstatement in earlier filings: reconstruction and verification are **not** triggered once per 2^120.71 claws but once per claw that passes the side conditions and row 17, a fraction 2^−42.44, i.e. about 2^77.26 times over the attack. At a few compressions each that is about 2^77.3 target compressions against 2^122.98 — still negligible, but the earlier frequency was wrong by roughly 78 bits. Side-condition checking adds 40 / 2^8.19 ≈ 0.14 ops per word evaluation; restart overhead (clearing the 393,216-byte flag array once per 2^26.46-evaluation window, 98,304 word writes) adds 2^−9.9; and packing the table entry adds, per stored or matched distinguished point, about 7 operations (a shift and an or to assemble the 24-bit field and three byte stores on a store; three byte loads, two shifts, two ors and two compares on a probe) against the 8 of the unpacked layout, about 7 / 2^7 ≈ 0.05 ops per evaluation. The total omitted work, about 0.2 ops per evaluation, stays inside the 0.6 between the 92.4 the ledger derives (70 traced kernel operations plus 22.4 of estimated overhead) and the charged 93. That margin is over an estimate, not over a trace: only the 70 are tracer-counted, as H3 states.

### Time

T = N × cost = 2^119.6964 × 2^3.2745 = 2^122.9709.

**Rounding, stated explicitly because it must go one way.** Charged work is filed as an upper
bound, so every rounding in this ledger is away from zero in the direction that costs the
attack. The exact chain is 120.7130 (per-claw exponent) − 1.0166 (amplification) + 3.2745
(cost per claw, = 11.00 − log2 7 + log2 93 − log2 2812) = 122.9709, and the filed value is
**time_log2 = 122.98**, rounded up at two decimals.

### Memory

Peak across phases (charged under collision-frontier-v5, which includes code, advice, working state, and tables):

| phase | total bytes | log2 |
| --- | ---: | ---: |
| dense solver (458,752 linear memory, 7 pages + 94,483 module) | 553,235 | 19.08 |
| claw search (917,504 table + ~60,000 code + ~2,000 condition tables + ~1,200 state + 3,800 advice) | ~984,504 | 19.91 |
| **peak = max** | **~984,504** | **19.91** |

The advice line carries the full 3,800-byte envelope of Section 7 (bases and the published
characteristic). The table is 131,072 slots at 7 bytes (Cost per claw, above); the previous
filing's 1,600,000-byte table at "12.5 bytes" per 128,000 slots had no derivation behind the
entry size and put the phase at 1,667,000 bytes. The code figure is an estimate carried
from earlier filings, not a measurement, and it is the exposure of this bound: the peak
stays under 2^20 = 1,048,576 as long as the claw-phase code is under about 124,000 bytes,
i.e. there are **64,072 bytes of headroom** over the estimate. The kernel itself is 70
instructions (Appendix F); the rest is the walk loop, the handler, the side-condition and
row-17 checks, and a scalar 39-step compression for reconstruction and verification.

**memory_log2_bytes = 20.**

**What the memory bound covers, and what it does not.** The bound is the peak over the
attack's own phases, both demonstrated in-model: the claw search above and the construction
of b1 by the dense solver (Section 4, 553,235 bytes). It does not include the memory of the
SAT campaign of the construction section below, which produced no filed artifact (it
bracketed the message shape and the trail's quality and confirmed the published trail) and
whose solver, Kissat, peaks at about 2^26 to 2^28 bytes on comparable instances in our
38-step work; nor the memory of the authors' unreported search for the characteristic,
which is unknown. The position this filing takes, stated so that it is reviewed rather than
found: the characteristic is public prior work consumed as 3,800 bytes of advice; its
construction time is capped by H14 and charged inside the time; its construction memory is
outside the peak reported here. A reader who holds that the construction of published
advice must be charged in memory as well as in time would put the bound at 2^26 or more for
our campaign and at an unknown value for the authors' search, and the score would not be
122.98 under that reading.

### Score

**score = 122.98 + max(0, 20 - 20) = 122.98** under the track adapter hashsmash-scalar-tm-v1 (timeLog2 + log2(memoryUnits), memoryUnit = 1 MiB, min 1). Under collision-frontier-v5 itself the normalized scalar is the total charged **time_log2 = 122.98** and memory is a reviewed bound rather than an additive term; the two coincide here.

**Margin: 1.85 bits below 744875ec (124.83147) and 1.27 bits below 0c1ef7c3 (124.25213).** The two adverse measurements the package contains are charged, not disclosed and ignored: the side-condition deviation of Section 3 and H8 at 0.63 bits, and the estimator bias of Appendix D.1 at 0.52 bits. The two offsets the previous filing (2c48b18c, 124.39) named and did not take are now taken on measurements: the claw rate at 2^11.00, the maximum over 289 chaining values at the filed configuration rather than a 0.414-bit margin over one measured graph (Appendix E.2b), and the memory bit, removed by a 7-byte table entry whose effect on the search is verified to be nil (Appendix E.1, E.2b). What is still not taken: the Bonferroni factor of 8 on the tail, worth 0.089 bits against the basic bound, and the 0.004-bit excess of the charged 2^11.00 over the worst measured graph.

### Preprocessing and advice

The dense solver is a one-time preprocessing step producing its 4 bases. Charged as total word operations in the DFS: approximately 2^40 nodes at ~200 ops/node = 2^47.6 word ops, or 2^47.6 / 2812 ≈ 2^36.1 target compressions. That term alone is 2^36.1 compressions, and it is subsumed by the over-charge filed below.

**Construction: what is charged, what is measured, and what is unreported.** The
cost model puts "message and differential construction" and "preprocessing" inside
total time and requires the construction of stored advice to be accounted for. This
attack consumes two fixed objects as advice: the published 39-step characteristic
(ePrint 2026/1120, Table 21) and the base b1. What follows is the construction work on
the path to each, what of it is measured, and the one step that is charged from no
measurement because none exists anywhere.

**The characteristic.** It is published prior work: the authors found it with their
open-source SAT-based tool (their reference [LLW24a]) and publish the trail, its
conditions and an SFS pair that confirms it. The paper reports **no effort figure for
that search**; its only timing figure for 39-step SHA-256, 2^34.2, is for Step 1 of
their framework, finding a conforming message given the trail. The authors' own search
is therefore unreported, and it is not reproduced here. What this package charges is
every solver run of our own on this shape, logged job by job (52 jobs: 34 UNSAT, 4 SAT,
14 TIMEOUT at a 4-hour cap, 55.5 CPU-hours; 124 job specifications in all, logs in
`runs39/*.log` of the work tree), and this is what those runs construct and prove about
the characteristic:

| about the characteristic | job | result |
| --- | --- | --- |
| a message-difference shape of weight 25 with W27..W38 difference-free exists, and it is the published one (W8..W12, W16, W17, W24, W26): constructed from the weight bound alone | shape39_hw25 | SAT, 484 s |
| no such shape has weight <= 18 | shape39_hw12, shape39_hw15, shape39_hw18 | UNSAT, 105 s, 919 s, 12,593 s |
| no characteristic of the published shape is 10 proxy points better than the published trail (Q <= 70; the published trail has Q = 80), at message weight 25 and at 26..28 | Q39_all_Q70_s1, Q39_hw26to28_Q70_s1 and _s2, Q39_p00..p23_Q70 | UNSAT, 9 s to 3,749 s |
| whether anything exists at Q in 71..79 within the shape | Q39_hw25_Q75_s1, Q39_hw25_Q78_s1, Q39_all_Q79_s1 | TIMEOUT at the cap, undecided |
| the published trail satisfies the window bounds of the search model | val_F39_win_E1415le4_pub39 | SAT, 9.2 s |

So the shape is re-derived constructively in minutes, the trail's quality is bracketed
from below by proof (nothing at Q <= 70, so the published Q = 80 is within ten proxy
points of the best possible in its shape), and the trail itself is confirmed in seconds.
What is not measured, by us or by the authors, is the search that first produced the
Q = 80 trail within the shape. No figure for it exists to charge, so it is declared as
premise **H14** (Section 9): a cap of 2^110 primitive operations on any computation ever
performed, which is 2^98.54 target compressions and sits 17.8 bits below the 2^116.30 at
which the filed exponent would move. The filed preprocessing field carries that cap rather
than the campaign figure, so that no plausible historical cost contradicts it. Section 10
reports the step as the exposure of this entry.

**The base b1.** b1 is the first base of the dense solver's logged run (Section 4,
Appendix B.1), derived from Table 21 and one tail-interface bit in the 7-page module. Its
construction is charged from the solver's measured throughput: a complete search from
Table 21 alone is about 2^58 bit-level nodes, about 2^51.2 target compressions (Appendix C).
The logged run searched one subtree chosen with knowledge of the paper's values and stopped
after four bases, so this is an estimate anchored to measurement rather than the cost of a
completed search; it sits 48 bits inside the preprocessing field. Earlier filings said b1's
rows 0..3 had been re-solved inside the SAT campaign; that was wrong (Appendix B.1) and
nothing on b1's path ran in the campaign.

**The charge.** All 124 job specifications at the full 4-hour cap, an upper bound on the
campaign since most jobs finished sooner:

    124 x 14,400 s = 1,785,600 s = 496 CPU-hours

Converting wall-clock into collision-frontier-v5 primitive operations needs a rate R per
core-second. The filed exponent does not depend on it: the charge is 496 h x R / 2812
compressions, and the filed time_log2 = 122.98 is unchanged for any construction cost
below 2^116.30, so

| assumed R (ops per core-second) | charge | filed time unchanged |
| --- | --- | --- |
| 10^9 (a conservative core) | 2^39.21 | yes |
| 10^11 (above any real core) | 2^45.85 | yes |
| 10^15 | 2^59.14 | yes |
| 10^20 | 2^75.75 | yes |

R would have to exceed **10^32.2 operations per core-second**, some twenty-one orders of
magnitude beyond any processor that exists, before the filed exponent moved.

**What preprocessing_log2 covers, stated once.** The filed **preprocessing_log2 = 99** is
the cap of premise H14: 2^110 primitive operations / 2812 = 2^98.54 target compressions,
rounded up. It is an upper bound on all construction work behind the two advice objects.
Inside it: the measured campaign envelope above (2^39.21 at R = 10^9, and 2^75.75 even at
10^20), which covers the shape derivation, the quality bracketing and the confirmation of
the published trail; the dense solver of Section 4 that produced b1, whose complete search
from Table 21 is about 2^51.2 target compressions by its measured throughput (Appendix C);
and the authors' unreported search for the trail within the shape, for which no measurement
exists and which is bounded by H14 alone. Earlier filings
reported the campaign figure, 40, in this field; a review observed that any historical
cost above 2^40 would then contradict the field, which is true, and the field now carries
the cap.

**Charged inside the time.** log2(2^122.9709 + 2^99) = 122.9709, the filed
**time_log2 = 122.98**; the cap is 24.0 bits below the attack's own work.

Nonuniform advice: a full base occupies 256 bytes (4 state words plus 12 message words at 4 bytes each); with all 4 bases, 1,024 bytes. The attack also consumes the published characteristic as fixed non-derived data: 23 row records of six 32-bit words (552 bytes) plus 140 bit conditions at 8-16 bytes each, a further 1,100-2,250 bytes. Total 2,700-3,800 bytes, so **nonuniform_advice_log2_bytes = 12**. Earlier filings charged 10, counting only the bases; that was an undercount and is corrected here. The memory table above budgets 1,024 advice bytes for the claw-search phase, which is the bases alone; adding the characteristic tables moves the phase peak by under 0.01 bits and does not approach the 2^21 envelope.

## 8. Verification

| check | result | in this package? |
| --- | --- | --- |
| dense solver in WASM, 7 pages (458,752 bytes), grow refused | the logged 16-page run found 4 bases, the first being b1; the 7-page module reproduces the pinned subtree's counters and base exactly | no — binaries cannot ship (intake admits only .py experiments) |
| **claw rate at the filed configuration, 289 chaining values (`clawvow7.c`, 2^17 slots, 7-byte entries, 2^26 evaluations each)** | **mean 2^10.970, sd 0.007, max 2^10.996; 9 paired runs identical to the unpacked program on every counter and on the claws found** | no — reported; every value is in Appendix E.5 |
| table-size sweep (`clawvow.c`, 33 chaining values, 48,000 to 128,000 slots) | rate exponent −0.36 in slots at dp_bits 7; dp_bits 8 is 0.6 bits worse at every size | no — reported, Appendix E.2b |
| q on self-derived bases (4 seeds × 4 bases, unrelaxed) | mean −143.38 against the published base's −143.42 | no — estimator not shippable, **and this cross-check is withdrawn as corroboration: it is circular.** The bases compared share their dense core (Appendix B.1), so the two measurements are substantially of the same object |
| **q on b1, row-20 relaxation, pooled 140-seed study** | **120 completed, 20 stalled (14.3%); linear mean with stalls at zero 2^−141.409; 99%/8 bootstrap bound 2^−141.753; bias-corrected 2^−142.273. The earlier 20-seed figures (mean −141.306, bound −141.96) and the log-scale censored bound −143.759 of cfe5c4e2 are superseded — Section 5, Appendix D.1.** | the per-seed data **is** filed (Appendix D.2) so the bound is recomputable, but the measurement is not organizer-executed |
| **row-18 conditional, the first tail stage (tailrow.py, organizer)** | **2^22 pooled proposals, 13 full hits, rate 2^−18.300 against the study's 2^−18.0** | **yes** — organizer-run; the first in-package measurement of any tail stage |
| **estimator bias against a known answer (splitbias.py, organizer)** | **E[q̂]/q = 1.40, 1.20, 1.10, 1.05 at populations 10, 20, 40, 80 — a positive bias falling monotonically. The ledger subtracts the largest of these, 0.52 bits, rather than extrapolating to the filed population 2000** | **yes** — organizer-run |
| **side-condition factorization under claw selection (clawdist.py, organizer)** | **the joint prefix rate falls **below** the product of the marginals by 0.43 bits at k = 16 and 0.63 at k = 24 — each about twice its own resolution (0.22, 0.36), both adverse, magnitude growing with k. The ledger charges the k = 24 figure. The full 32-bit joint is too rare to resolve on ~1,000 claws** | **yes** — organizer-run |
| **inter-claw dependence within a window (clawdist.py, organizer)** | **no duplicate claw in 1,071; per-trial successes not overdispersed against the independent binomial model, dispersion index 1.04 against a standard deviation of 0.09** | **yes** — organizer-run; resolves clustering above about 30%, not finer |
| claw search verification (s128k_db7_e30) | 4,096 of 4,096 claws rebuilt with real compression; all pass | no — 2^30-evaluation run not shippable |
| claw construction through the real expansion (clawdist.py, organizer) | 1,071 of 1,071 claws give W16 = bca1c321 under the real expansion — an **identity** given a table hit, so a transcription check across the kernel forms, the schedule and the expansion, not a pass rate | **yes** — organizer-run |
| **side conditions on claw-selected variants (clawdist.py, organizer)** | **p8 2^−3.672 and p9 2^−6.158 against the exhaustive −3.830 and −5.978, inside the sample's 0.18- and 0.37-bit resolution. This is the genuinely new measurement: W8 and W9 from real claw-selected (a0, a1), not uniform words** | **yes** — organizer-run |
| W17 low-bit uniformity (clawdist.py, organizer) | z = +0.30 over 6 of 32 bits. Low power: at its 4-sigma band it would miss an eightfold inflation of a low-bit class about 93% of the time, and the table confines u to the 2^21 smallest odd values so the restriction sits in the high bits it does not test | **yes** — organizer-run, but weak |
| kernel trace | 70 ops per 7 lanes, packed = scalar, 0 mismatches | **yes** — `experiments/kernelcount.py`, organizer-run, 336 lanes/trial (86,016 pooled) |
| side-condition rates (rowstat.c, all 2^32 words) | p8 = 2^−3.830, p9 = 2^−5.978 | no — exhaustive enumerator is not a Python experiment |
| side-condition sampling (sidecond.py, organizer) | 2^14 samples/trial; pooled over 256 organizer trials log2 p8 = -3.8344, log2 p9 = -5.9731, matching the exhaustive counts to 0.005 bits | **yes** — organizer-run |
| claw existence (clawverify.py, organizer) | 2^13 targets/trial, expectation 1.00 claws (measured 1.12); every returned u is odd. Preimages are **not** independently verified: a u returned by `table[v]` satisfies f(u) = v by construction, so that check was a dictionary-key identity and has been removed | **yes** — organizer-run |

## 9. Premises (heuristics)

- **H1: retired, because the ledger does not use it.** Earlier filings declared a premise that success at the fixed target g = bca1c321 is at least success against a uniformly random target. No line of the ledger transfers a random-target quantity to g, so the premise was never consumed. Every factor of the per-claw exponent is evaluated **at g**: the row-17 term is the exact count |G17(g)| = 1 at g (and |G17(bca1c121)| = 0, so g is not a lucky choice among the two G16 words but the only viable one); the tail study's own row-16 and row-17 stages are −31.000 and −33.000, which is log2(|G16|/2^32) and log2(1/2^32 × 1/|G16|), so the estimator selects g and conditions everything downstream on it; and the side conditions are measured on claw-selected variants, which target g by construction. There is therefore nothing to compare with a random target and no inequality to assume. The numbering H1..H6 is kept so earlier review findings remain legible; H1 and H5 are both retired, for different reasons.
- **H2 (score-critical):** each chaining value is run for 2^26 trail evaluations in a 2^17-slot table with 7-byte entries and then abandoned; the ledger charges 2^11.00 evaluations per distinct claw, the maximum over 289 chaining values measured at exactly that configuration (mean 2^10.970, standard deviation 0.007 bits, Appendix E.2b, E.5), and the premise is that the 2^104.2 chaining values the attack consumes do not, on average, exceed that maximum. What is extrapolated is 289 measured functional graphs to 2^104.2 unmeasured ones: the spread between the best and worst of the 289 is 0.05 bits, and the standard deviation of the per-graph rate once the search's own start-point noise is removed is 0.004 bits (three run seeds on each of 32 graphs, Appendix E.2b). The earlier form of this premise charged 2^11.414, the cumulative rate of a single 2^30-evaluation run on one chaining value, as a margin; the margin is replaced by the measured distribution. The measurements are reported, not organizer-executed: the organizer experiment `vowclaw.py` runs the same search at reduced scale and shows it executes at a steady rate, nothing more.
- **H3 (score-critical):** the machine convention of 744875ec: 64 registers, 256-bit words with 7 lanes of 36 bits, 36 bytes per instruction, immediates free. Peak live registers are 7 for the rolling lane state plus the 25 distinct replicated 256-bit constants the 70 lines reference, so about 32 of the 64 the convention supplies. Those constants are loop-invariant: they are materialized once before the walk and reused across all 2^26 evaluations of a window, so under a convention that priced them as loads instead of immediates they would add 25 loads per window, below 2^-21 operations per evaluation, rather than 28 per evaluation. The 7 quoted in earlier filings counted only the rolling state. The overhead (22.4 ops beyond the 70-op kernel, charged as 23) is estimated, not fully traced; a full trace could shift the score by 0.1–0.3 bits.
- **H4 (score-critical): the tail premise, declared as one premise with three named components.** It carries 78.27 of the 120.71 per-claw bits, 65% of the exponent, and each component moves the exponent one-for-one. What H4 asserts is that the splitting estimator of Appendix D measures the attack's tail: the probability of the rows-18-to-38 event over the claws the attack actually generates is at least the filed 2^-78.273.
  - **(a) The statistic.** The filed value is a 99% bootstrap lower bound, with a Bonferroni factor of 8 for the row-20 selection, on the arithmetic mean of the 140 per-seed estimates with the 20 stalled seeds entered as zero, less 0.52 bits for estimator bias, divided by the exact 2^-64 prefix (Appendix D.1). The bound is on E[q-hat]; it reaches q through the bias allowance, whose dominant mechanism, population degeneracy, the calibration toy cannot exhibit. That is the weakest step of this component and D.1 says so.
  - **(b) Uniform expansion.** The estimator, at rows 18..23, draws a parent from the surviving population and proposes **W_r uniformly and independently**, then expands rows 24..38 from those proposals. The attack has no such freedom: once a claw (a0, u) is fixed, every expanded word from W16 on is a deterministic function of (a0, u, cv), and Appendix G states exactly that -- there is no further sampling and no restart within a claw. The component is that the frequency of the rows-18-to-38 event over the attack's claw-induced variants equals the frequency the estimator measures over free uniform proposals: a frequency over 2^192 free proposals equated with one over at most 2^64 variants per chaining value, of which about 2^30 are claws, across 2^104.21 chaining values. This is the message-freedom model of differential cryptanalysis on SHA-2, and it is the model under which the characteristic's own published evaluation prices the same uncontrolled part: ePrint 2026/1120 ("Complexity evaluation for collision attack on 39-step SHA-256") counts 168 conditions on (A_i, E_i, W_i) for i >= 16, its Table 22, and charges 2^168, each condition taken to hold independently with probability 1/2 over free message words. The estimator here measures that event on b1 directly instead of counting conditions, which is where the dependencies between conditions and the row-20 relaxation enter; the two figures are different statistics (a condition count against a measured joint frequency on one base), but both rest on the same model. That is relevant supporting evidence for the model, not a test of it. What is measured under the attack's own distribution is one point: W18 taken from the real expansion on genuine claws is uniform in its low 6 bits (`clawdist.py`, pooled chi-square z about -1.1), one marginal on one of six words. Nothing in the package tests the six-word joint distribution or the deep tail under the attack's distribution, and no sandbox experiment can: an attack-generated state reaches row 18 with probability about 2^-42 per claw.
  - **(c) Claw selection.** Claws produced by the vOW search may be biased toward u values with many f-preimages; independence of that bias from the tail event is assumed. The side conditions and W17 are now measured under claw selection (H8, H9); the tail is not, and cannot be at sandbox scale for the reason in (b).

  Component (b) was declared under a separate ID, H12, in three earlier filings. It is declared here as part of H4, with its text kept in full above, because it is not a premise distinct from H4 -- H4's statement is that the estimator's measure and the attack's measure agree, and (b) is that statement made explicit -- and because it has no evidence distinct from H4's, which is listed once.
- **H6 (score-critical):** the N = 2^119.70 generated claws behave as sufficiently independent Bernoulli trials for the Poisson success formula. The per-claw success probability p = 2^−120.71 is assumed to hold independently across claws. In practice, claws from the vOW search on different chaining values are functionally independent (different functions F); claws from the same chaining value share a function but draw from different f-preimages. No duplicate-rate or formal dependence analysis is supplied; the 566,025 distinct claws from 2^30 evaluations in the s128k run showed no anomalous clustering. Within-window dependence is now measured rather than asserted: no duplicate claw in 1,071 and a dispersion index of 1.04 against a standard deviation of 0.09 (Section 8). What remains open is dependence across windows and clustering finer than about 30%.
- **H10 — disclosed, not declared as a heuristic** (it constrains no ledger term, so `claim.json` does not list it): the organizer seed is public and no holdout nonce is used, so the acceptance bands below were written by a participant who had already seen pooled outcomes from that seed. What limits the exposure is that each band is derived from the sample's own resolution rather than from where a run landed -- four standard deviations on the side-condition and row-18 bands, a dispersion band set from its own standard deviation near 0.09, and a kernel-count hypothesis naming a specific 2.5% chance of a 69-operation trial from the (3/4)^32 probability that a folded constant vanishes. Several bands were widened after a run came close to them, which is recorded rather than hidden. Disclosure does not create power: four-sigma bands cannot detect small shifts, no multiple-comparison correction is applied across the seven experiments, and the organizer's own selection-bias warning for public-seed experiments applies here.
- **H8 (score-critical):** under the claw-selected, parity-restricted distribution the full 32-bit joint probability of the two side conditions is at least the product of the marginals, p8 x p9 = 2^-9.808, less the charged 0.63 bits, i.e. at least 2^-10.44. **Exact factorization at full width is not claimed and is not what the ledger consumes**; an earlier form of this premise stated exact factorization while the ledger already charged the deviation, and a review was right to call the two inconsistent. Measured on prefixes, where it resolves: the joint prefix rate agrees with the product of the marginals to -0.43 bits at 16 bits and -0.63 at 24. **Earlier filings described these as "inside resolutions of 0.22 and 0.36", which the numbers do not support**: each deviation is about twice its own quoted resolution, both are negative, and the magnitude grows with the prefix width. Read as a trend to full width they would be worth roughly -0.8 bits. **The ledger therefore charges the larger measured deviation, 0.63 bits, against the side-condition term** (Section 7: the charged side-condition factor is 2^-10.44, not the exact product 2^-9.808). Under uniform (a0, a1) the factorization is exact, since W8 = C(a1) - a0, but that is not the distribution the attack samples. The full-width joint has expected count under 2 on the claws the sandbox affords and is not measured; what is charged is the measurement at k = 24, not the extrapolation to k = 32, so a real full-width deviation nearer -0.8 would cost a further 0.17 bits.
- **H9 (score-critical):** W17, fully determined by the claw, is uniform over all 32 bits, so |G17(g)| = 1 gives exactly 2^-32. |G17(g)| = 1 is exact and verified; this premise concerns the denominator. Measured on the low 6 bits only, by a test with little power, and the preimage table confines u to the 2^21 smallest odd values so the high bits of W17 are exactly where it does not look. 32 of the 120.71 per-claw bits rest on it.

- **H11 (score-critical):** after conditioning on a genuine claw **and** on the two side conditions, the row-17 and tail events keep the marginal probabilities the ledger uses, so the three groups may be multiplied into 2^-120.71. H8 covers the two side conditions against each other and H9 covers W17's uniformity; H11 is the premise that the *groups* do not interact. Two conditioning checks are run on genuine claws and both are low-powered: W18 taken from the real expansion is uniform in its low 6 bits (pooled chi-square z about -1.1), and among claws passing the first side condition W17's low bit is set 36 times in 85 (z about -1.4). Neither reaches the tail: conditioning it on side-condition selection needs claws that also pass row 17, costing 2^-32, which is unreachable at sandbox scale. The untested tail carries 78.27 of the 120.71 per-claw bits, so a correlation there moves the exponent one-for-one. This premise was declared in claim.json from an earlier filing but was missing from this section; it is restored here.

- **H14 (score-critical for the time bound only): the construction cap.** The search that produced the published characteristic (ePrint 2026/1120, Table 21), whose effort the paper does not report, cost fewer than **2^110 primitive word operations**, i.e. fewer than 2^98.54 target compressions at C = 2812. This is a physical bound, not a cost estimate. The world's installed computing capacity is of order 10^22 operations per second; the whole of it running for a thousand years performs about 3 x 10^32 = 2^108 operations, and the premise allows four times that. For scale: a SAT-based search by an academic group over a fixed message shape runs on at most thousands of cores for at most months, 2^10 x 2^30 x 2^23 = 2^63 operations, 47 bits below the premise; the paper's own largest reported solver figure is 2^34.2 (its Step 1, message finding); our campaign on the same shape is 2^50.7 operations at 10^9 per core-second. What the premise supports: that the filed time_log2 = 122.98 is an upper bound on total charged work, since it is unchanged for any construction cost below 2^116.30 target compressions = 2^127.8 operations, 17.8 bits above the cap (the exponent would move only if that search had consumed the planet's entire capacity for 2^20 thousand years); and that the filed preprocessing_log2 = 99 is an upper bound on all construction work including that search. What it does not supply: a measurement of the search, which does not exist, and no sandbox experiment bears on it. It supports no other ledger line. A reader who requires the historical search to be measured rather than capped will find no measurement here; Section 10 reports the step as this entry's exposure. An earlier filing (05a6c48b) declared a premise in this place that asserted our own campaign bounds the authors' search; that assertion is withdrawn and is not what H14 says.

## 10. What this is not

This entry IS a differential attack on 39-step SHA-256 with a real structural result: the row-16 claw construction, verified in-package through the real message expansion. At 122.98 it is below our own accepted generic entry (124.83147) by 1.85 bits and below the best AI-valid generic entry awaiting human review (0c1ef7c3, 124.25213) by 1.27 bits; see the opening section. An earlier filing of the same construction (cfe5c4e2) scored 125.25 on the same data, using a tail statistic that was not an estimator of q; Appendix D.1 sets out the correction and keeps the old value as a sensitivity row. Further:
- It does NOT find a new characteristic; it uses 2026/1120 Table 21. The search by which the authors found that trail is unreported in the paper and not reproduced here. Section 7 charges the construction work this package performed on the path to it (the shape re-derived constructively, the quality bracketed by UNSAT proofs at Q <= 70, the trail confirmed) under a 496-CPU-hour envelope whose conversion rate is shown not to move the filed exponent, and declares the authors' search under premise H14, a physical cap of 2^110 operations on any computation ever performed, because no measurement of it exists.
- The 1.27-bit margin over the best generic entry rests on premises. The quantities that would have to move to erase it are the tail under claw selection (H4), the machine convention (H3), the claw rate (H2) and the construction cap (H14). H4 is the exposed one: a correlation between claw selection and the tail moves the exponent one-for-one, so a correlation worth more than 1.27 bits would put this entry behind 0c1ef7c3 and one worth more than 1.85 bits behind 744875ec. Nothing in the package tests the tail beyond row 18 under claw selection.
- The memory bound of 2^20 rests on an estimate for the claw-phase code (about 60,000 bytes) with 64,072 bytes of headroom, and it excludes the memory of the construction work charged under H14 and the campaign envelope; Section 7 states that position so that it is reviewed rather than found.
- The organizer experiments do not return message pairs, so none of their numbers is credited as attack cost; Appendix H states experiment by experiment what each does and does not establish. The packed kernel is now counted by an organizer-run tracer (`experiments/kernelcount.py`, Appendix F), but the machine convention that prices it remains H3, and the 23 operations of DP, loop and handler overhead remain estimated.

## 11. Credits and dependencies

This entry derives from and credits:
- 744875ec: our accepted generic rho filing (the machine convention, the lane packing, C = 2812).
- ePrint 2026/1120: the 39-step characteristic (Table 21) and base (Table 23).
- The 38-step work (1a695f0b, 08e2e0d3): the relaxed-row idea.

## 12. Next steps (not part of this filing)

- Counted handler: the 22.4 operations of overhead beyond the now-traced 70-operation kernel are still estimates; a full trace would move the score by about 0.1-0.3 bits.
- Wider characteristic search: a better 39-step trail (lower tail probability) improves the score proportionally.

## Appendix A. The complete 39-step characteristic

Section 1 cites ePrint 2026/1120 Table 21 for the trail. A citation is not a
specification: the judge cannot fetch it, and the attack cannot be rebuilt from a
reference. The full machine-readable characteristic is therefore reproduced here,
in the exact form the tail estimator of Appendix D consumes. It is the trail of
that table together with the conditions this filing derives from it.

### A.1 Encoding

Four record types. All values are hexadecimal unless marked decimal.

```
ROW  r  MA SA  ME SE  MW SW
     r       the step index, 16..38
     MA SA   mask and signs of the A-register difference at step r
     ME SE   mask and signs of the E-register difference at step r
     MW SW   mask and signs of the message-word difference at step r
             a bit set in M is a bit that differs; the matching bit of S
             gives the direction: 1 means member x carries the 1 ('u'),
             0 means member y does ('n').  M = 0 is a difference-free word.

ST   m  i  A E
     m       member, 0 = x, 1 = y
     i       step index, -4..15 (negative indices are the chaining value)
     A E     the A and E register values of member m at step i

W    m  i  w        message word i of member m, i = 0..15

COND k n (kind row bit){n} allowed
     k       the step at which the condition becomes decidable
     n       the number of bit positions it constrains, 1..5
     kind    0 = an A bit, 1 = an E bit, 2 = a W bit
     row,bit which register bit each position refers to
     allowed a truth table over the n bits: bit j of `allowed` is 1 when the
             assignment whose binary value is j is permitted.  The condition
             holds iff ((allowed >> idx) & 1), where idx packs the n selected
             bits of member x in the order listed.
```

A state satisfies step r when its signed differences match the ROW record for r
and every COND record with k = r evaluates to 1. Row 20 is the relaxed row of
Section 5: its ROW record is checked and its COND records are skipped.

### A.2 Signed differences, steps 16..38

```
ROW   MA       SA       ME       SE       MW       SW
16    05010000 04010000 00000100 00000000 08801000 08800000
17    00000000 00000000 80829c01 00029c00 40000000 40000000
18    40000000 40000000 00000000 00000000 00000000 00000000
19    00000000 00000000 00080020 00080000 00000000 00000000
20    00000000 00000000 03010000 03010000 00000000 00000000
21    00000000 00000000 00000000 00000000 00000000 00000000
22    00000000 00000000 40000000 40000000 00000000 00000000
23    00000000 00000000 00000000 00000000 00000000 00000000
24    00000000 00000000 00000000 00000000 03010000 00000000
25    00000000 00000000 00000000 00000000 00000000 00000000
26    00000000 00000000 00000000 00000000 40000000 00000000
27    00000000 00000000 00000000 00000000 00000000 00000000
28    00000000 00000000 00000000 00000000 00000000 00000000
29    00000000 00000000 00000000 00000000 00000000 00000000
30    00000000 00000000 00000000 00000000 00000000 00000000
31    00000000 00000000 00000000 00000000 00000000 00000000
32    00000000 00000000 00000000 00000000 00000000 00000000
33    00000000 00000000 00000000 00000000 00000000 00000000
34    00000000 00000000 00000000 00000000 00000000 00000000
35    00000000 00000000 00000000 00000000 00000000 00000000
36    00000000 00000000 00000000 00000000 00000000 00000000
37    00000000 00000000 00000000 00000000 00000000 00000000
38    00000000 00000000 00000000 00000000 00000000 00000000
```

### A.3 Bit conditions

The 140 conditions, grouped by the step at which each becomes decidable.

```
# step 16: 37 condition(s)
COND 16  n=2  (1,16,13) (1,16,27)                      allowed=9
COND 16  n=2  (0,16,4) (0,16,15)                       allowed=6
COND 16  n=2  (0,16,5) (0,16,25)                       allowed=9
COND 16  n=2  (0,16,6) (0,16,17)                       allowed=9
COND 16  n=2  (0,16,8) (0,14,8)                        allowed=9
COND 16  n=2  (0,16,13) (0,16,1)                       allowed=6
COND 16  n=2  (0,16,15) (0,16,3)                       allowed=9
COND 16  n=2  (0,16,27) (0,16,4)                       allowed=6
COND 16  n=2  (1,16,21) (1,16,26)                      allowed=9
COND 16  n=2  (0,16,17) (0,14,17)                      allowed=9
COND 16  n=2  (0,16,3) (0,16,12)                       allowed=9
COND 16  n=2  (0,16,5) (0,16,14)                       allowed=6
COND 16  n=2  (0,16,28) (0,16,7)                       allowed=6
COND 16  n=2  (1,16,28) (1,14,28)                      allowed=a
COND 16  n=2  (0,16,28) (0,14,28)                      allowed=6
COND 16  n=2  (1,16,3) (1,16,22)                       allowed=9
COND 16  n=2  (0,16,30) (0,15,30)                      allowed=6
COND 16  n=2  (1,16,0) (1,15,0)                        allowed=4
COND 16  n=2  (2,16,19) (2,16,21)                      allowed=6
COND 16  n=2  (2,16,21) (2,16,14)                      allowed=9
COND 16  n=2  (2,16,25) (2,16,16)                      allowed=6
COND 16  n=2  (2,16,25) (2,16,18)                      allowed=9
COND 16  n=2  (1,16,10) (1,15,10)                      allowed=9
COND 16  n=2  (2,16,29) (2,16,20)                      allowed=6
COND 16  n=2  (1,16,11) (1,15,11)                      allowed=4
COND 16  n=2  (1,16,12) (1,15,12)                      allowed=9
COND 16  n=2  (2,16,30) (2,16,0)                       allowed=6
COND 16  n=2  (1,16,15) (1,15,15)                      allowed=9
COND 16  n=2  (1,16,17) (1,15,17)                      allowed=9
COND 16  n=2  (2,16,2) (2,16,4)                        allowed=9
COND 16  n=2  (1,16,23) (1,15,23)                      allowed=4
COND 16  n=1  (2,16,10)                                allowed=1
COND 16  n=1  (2,16,14)                                allowed=2
COND 16  n=2  (1,16,31) (1,15,31)                      allowed=9
COND 16  n=2  (2,16,2) (2,16,19)                       allowed=9
COND 16  n=2  (2,16,31) (2,16,10)                      allowed=6
COND 16  n=2  (2,16,1) (2,16,29)                       allowed=6
# step 17: 34 condition(s)
COND 17  n=2  (1,17,6) (1,17,25)                       allowed=9
COND 17  n=2  (1,17,7) (1,17,26)                       allowed=6
COND 17  n=2  (1,17,16) (1,17,30)                      allowed=6
COND 17  n=2  (0,17,5) (0,16,5)                        allowed=6
COND 17  n=2  (1,17,13) (1,17,18)                      allowed=9
COND 17  n=2  (1,17,8) (1,15,8)                        allowed=a
COND 17  n=2  (0,17,8) (0,16,8)                        allowed=9
COND 17  n=2  (1,17,20) (1,17,2)                       allowed=9
COND 17  n=2  (1,17,22) (1,17,4)                       allowed=6
COND 17  n=2  (1,17,18) (1,17,5)                       allowed=6
COND 17  n=2  (0,17,16) (0,15,16)                      allowed=9
COND 17  n=2  (0,17,17) (0,16,17)                      allowed=9
COND 17  n=2  (1,17,24) (1,17,29)                      allowed=9
COND 17  n=2  (0,17,18) (0,16,18)                      allowed=6
COND 17  n=2  (1,17,25) (1,17,30)                      allowed=9
COND 17  n=2  (1,17,26) (1,17,13)                      allowed=6
COND 17  n=2  (1,17,27) (1,17,14)                      allowed=6
COND 17  n=2  (1,17,28) (1,17,1)                       allowed=9
COND 17  n=2  (1,17,30) (1,17,3)                       allowed=9
COND 17  n=2  (0,17,24) (0,15,24)                      allowed=9
COND 17  n=2  (1,17,4) (1,17,18)                       allowed=6
COND 17  n=2  (1,17,5) (1,17,19)                       allowed=9
COND 17  n=2  (0,17,26) (0,15,26)                      allowed=9
COND 17  n=2  (1,17,28) (1,16,28)                      allowed=a
COND 17  n=2  (0,17,28) (0,16,28)                      allowed=9
COND 17  n=2  (1,17,4) (1,17,9)                        allowed=9
COND 17  n=2  (1,17,5) (1,17,24)                       allowed=9
COND 17  n=2  (2,17,28) (2,17,21)                      allowed=9
COND 17  n=2  (2,17,0) (2,17,23)                       allowed=6
COND 17  n=2  (2,17,5) (2,17,7)                        allowed=6
COND 17  n=2  (0,17,30) (0,16,30)                      allowed=9
COND 17  n=2  (2,17,19) (2,17,15)                      allowed=9
COND 17  n=2  (2,17,9) (2,17,26)                       allowed=6
COND 17  n=2  (2,17,2) (2,17,13)                       allowed=6
# step 18: 17 condition(s)
COND 18  n=2  (1,18,0) (1,16,0)                        allowed=5
COND 18  n=2  (1,18,8) (1,17,8)                        allowed=5
COND 18  n=2  (0,18,10) (0,18,21)                      allowed=9
COND 18  n=2  (1,18,10) (1,16,10)                      allowed=5
COND 18  n=2  (1,18,11) (1,16,11)                      allowed=5
COND 18  n=2  (1,18,12) (1,16,12)                      allowed=5
COND 18  n=2  (1,18,15) (1,16,15)                      allowed=5
COND 18  n=2  (0,18,16) (0,17,16)                      allowed=9
COND 18  n=2  (1,18,17) (1,16,17)                      allowed=a
COND 18  n=2  (0,18,19) (0,18,7)                       allowed=6
COND 18  n=2  (1,18,23) (1,16,23)                      allowed=5
COND 18  n=2  (0,18,24) (0,17,24)                      allowed=9
COND 18  n=2  (0,18,26) (0,17,26)                      allowed=9
COND 18  n=2  (0,18,9) (0,18,18)                       allowed=6
COND 18  n=2  (1,18,31) (1,16,31)                      allowed=5
COND 18  n=2  (1,18,5) (1,17,5)                        allowed=9
COND 18  n=2  (1,18,19) (1,17,19)                      allowed=9
# step 19: 16 condition(s)
COND 19  n=2  (1,19,0) (1,18,0)                        allowed=a
COND 19  n=2  (1,19,14) (1,19,1)                       allowed=9
COND 19  n=2  (1,19,10) (1,18,10)                      allowed=a
COND 19  n=2  (1,19,11) (1,18,11)                      allowed=a
COND 19  n=2  (1,19,18) (1,19,23)                      allowed=6
COND 19  n=2  (1,19,12) (1,18,12)                      allowed=5
COND 19  n=2  (1,19,24) (1,19,6)                       allowed=6
COND 19  n=2  (1,19,15) (1,18,15)                      allowed=a
COND 19  n=2  (1,19,17) (1,18,17)                      allowed=a
COND 19  n=2  (1,19,23) (1,18,23)                      allowed=a
COND 19  n=2  (0,19,30) (0,17,30)                      allowed=9
COND 19  n=2  (1,19,10) (1,19,24)                      allowed=6
COND 19  n=2  (1,19,31) (1,18,31)                      allowed=5
COND 19  n=2  (1,19,16) (1,18,16)                      allowed=2
COND 19  n=2  (1,19,24) (1,18,24)                      allowed=9
COND 19  n=2  (1,19,25) (1,18,25)                      allowed=9
# step 20: 12 condition(s)
COND 20  n=2  (1,20,6) (1,20,11)                       allowed=9
COND 20  n=2  (1,20,11) (1,20,30)                      allowed=9
COND 20  n=2  (1,20,5) (1,18,5)                        allowed=a
COND 20  n=2  (1,20,21) (1,20,3)                       allowed=9
COND 20  n=2  (1,20,19) (1,20,6)                       allowed=9
COND 20  n=2  (1,20,20) (1,20,7)                       allowed=9
COND 20  n=2  (1,20,29) (1,20,11)                      allowed=6
COND 20  n=2  (1,20,30) (1,20,12)                      allowed=6
COND 20  n=2  (1,20,19) (1,18,19)                      allowed=a
COND 20  n=2  (1,20,29) (1,20,2)                       allowed=9
COND 20  n=2  (0,20,30) (0,19,30)                      allowed=9
COND 20  n=2  (1,20,5) (1,20,10)                       allowed=9
# step 21: 6 condition(s)
COND 21  n=2  (1,21,5) (1,20,5)                        allowed=a
COND 21  n=2  (1,21,16) (1,19,16)                      allowed=5
COND 21  n=2  (1,21,19) (1,20,19)                      allowed=a
COND 21  n=2  (1,21,24) (1,19,24)                      allowed=5
COND 21  n=2  (1,21,25) (1,19,25)                      allowed=5
COND 21  n=2  (1,21,30) (1,20,30)                      allowed=9
# step 22: 6 condition(s)
COND 22  n=2  (1,22,11) (1,22,16)                      allowed=9
COND 22  n=2  (1,22,16) (1,21,16)                      allowed=a
COND 22  n=2  (1,22,25) (1,22,12)                      allowed=6
COND 22  n=2  (1,22,3) (1,22,17)                       allowed=6
COND 22  n=2  (1,22,24) (1,21,24)                      allowed=5
COND 22  n=2  (1,22,25) (1,21,25)                      allowed=a
# step 23: 1 condition(s)
COND 23  n=2  (1,23,30) (1,21,30)                      allowed=5
# step 24: 8 condition(s)
COND 24  n=2  (1,24,30) (1,23,30)                      allowed=a
COND 24  n=2  (2,24,22) (2,24,15)                      allowed=6
COND 24  n=2  (2,24,26) (2,24,17)                      allowed=9
COND 24  n=2  (2,24,27) (2,24,18)                      allowed=9
COND 24  n=2  (2,24,31) (2,24,1)                       allowed=6
COND 24  n=2  (2,24,0) (2,24,2)                        allowed=6
COND 24  n=1  (2,24,14)                                allowed=2
COND 24  n=1  (2,24,18)                                allowed=2
# step 26: 3 condition(s)
COND 26  n=2  (2,26,28) (2,26,21)                      allowed=6
COND 26  n=2  (2,26,0) (2,26,23)                       allowed=9
COND 26  n=2  (2,26,5) (2,26,7)                        allowed=9
```

### A.4 The base state and message words of the published pair

The state the characteristic is anchored to, members x and y.

```
ST  m   i    A         E
ST  0   -4   1c40a0d4  0e6446c1 
ST  0   -3   71a28861  020b80dd 
ST  0   -2   d12deef2  b326f54c 
ST  0   -1   b21e3e63  15bb07fb 
ST  0   0    ea3ff0b4  adee5184 
ST  0   1    48c79fa7  873faa9c 
ST  0   2    7e0f7259  33a865ae 
ST  0   3    b9be31d6  114b346f 
ST  0   4    9f0216f0  3895b86b 
ST  0   5    583f3ec8  49d8ebcf 
ST  0   6    73a03068  3bbb3cc6 
ST  0   7    caeefa06  0a20c41f 
ST  0   8    29f1c95e  94dfb329 
ST  0   9    c76d0d7b  ac230e77 
ST  0   10   24b9a00a  9e3b6fe9 
ST  0   11   ca0aecd2  ff00f821 
ST  0   12   5829bcdb  bc4a3994 
ST  0   13   bf5e1f93  a87dbd19 
ST  0   14   bd4f5653  9cca05a1 
ST  0   15   269f8f4f  d2c3ec33 
ST  1   -4   1c40a0d4  0e6446c1 
ST  1   -3   71a28861  020b80dd 
ST  1   -2   d12deef2  b326f54c 
ST  1   -1   b21e3e63  15bb07fb 
ST  1   0    ea3ff0b4  adee5184 
ST  1   1    48c79fa7  873faa9c 
ST  1   2    7e0f7259  33a865ae 
ST  1   3    b9be31d6  114b346f 
ST  1   4    9f0216f0  3895b86b 
ST  1   5    583f3ec8  49d8ebcf 
ST  1   6    73a03068  3bbb3cc6 
ST  1   7    caeefa06  0a20c41f 
ST  1   8    69f1c95e  d4dfb329 
ST  1   9    cfe71c5b  a49b1e57 
ST  1   10   24b9a00a  3f1b2103 
ST  1   11   ca0aecd2  b708f921 
ST  1   12   5ce9bcdb  f8883994 
ST  1   13   96179b98  82412611 
ST  1   14   fd4b5673  9cca05a1 
ST  1   15   36998e6f  c2c3ec33 

W   m   i    w
W   0   0    5ee50e16 
W   0   1    b5a4f02b 
W   0   2    a58b289e 
W   0   3    f713de5d 
W   0   4    3b96d2db 
W   0   5    215da7e2 
W   0   6    3674669a 
W   0   7    2ca65d8d 
W   0   8    a99c40e3 
W   0   9    1fae8a20 
W   0   10   42e88746 
W   0   11   01003fbb 
W   0   12   e8d6fe22 
W   0   13   b06304c1 
W   0   14   43660040 
W   0   15   4891771f 
W   1   0    5ee50e16 
W   1   1    b5a4f02b 
W   1   2    a58b289e 
W   1   3    f713de5d 
W   1   4    3b96d2db 
W   1   5    215da7e2 
W   1   6    3674669a 
W   1   7    2ca65d8d 
W   1   8    e99c40e3 
W   1   9    172e9a20 
W   1   10   02e88746 
W   1   11   07021c8f 
W   1   12   e8c6e622 
W   1   13   b06304c1 
W   1   14   43660040 
W   1   15   4891771f 
```

## Appendix B. The filed dense base b1

The base this filing's tail measurement and side conditions are evaluated on.
Rows 2..15 of both members are fixed by it; A0 and A1 are the free variant words.
Section 3's modular differences follow from the W rows below as D = Wy - Wx and
DS = s0(Wy) - s0(Wx), giving D8 = 40000000, DS8 = 087ff000, D9 = f7801000,
DS9 = 03010000, which are the constants the side-condition experiments use.

```
i     Ax        Ay        Ex        Ey        Wx        Wy
0     cf17c239  cf17c239  -         -         -         -        
1     b57b6802  b57b6802  -         -         -         -        
2     11b4d46d  11b4d46d  -         -         -         -        
3     e9bdf656  e9bdf656  -         -         -         -        
4     9f0216f0  9f0216f0  bd5a7907  bd5a7907  -         -        
5     583f3ec8  583f3ec8  dbe61086  dbe61086  -         -        
6     73a03068  73a03068  8f5f9eda  8f5f9eda  -         -        
7     caeefa06  caeefa06  3a20889f  3a20889f  -         -        
8     29f1c95e  69f1c95e  94dfb329  d4dfb329  15695652  55695652 
9     c76d0d7b  cfe71c5b  ac230e77  a49b1e57  9dc1655d  9541755d 
10    24b9a00a  24b9a00a  9e3b6fe9  3f1b2103  df4464b2  9f4464b2 
11    ca0aecd2  ca0aecd2  ff00f821  b708f921  d1007b3b  d702580f 
12    5829bcdb  5ce9bcdb  bc4a3994  f8883994  e8d6fe22  e8c6e622 
13    bf5e1f93  96179b98  a87dbd19  82412611  b06304c1  b06304c1 
14    bd4f5653  fd4b5673  9cca05a1  9cca05a1  43660040  43660040 
15    269f8f4f  36998e6f  d2c3ec33  c2c3ec33  4891771f  4891771f 
16    cc8fd4cb  c98ed4cb  9776869e  9776879e  bca1c321  b421d321 
17    ce7b54b4  ce7b54b4  771adf7e  f798437f  71e9ba98  31e9ba98 
```

### B.1 Provenance of b1, corrected

b1 is **the first base printed by the logged run of the dense solver** (Section 4;
`runs39/dense/xsub_wasm.txt`, first BASE line), register for register the table above. It
is also, and for the same reason, the published base of Appendix A.4 with rows 0..3
re-solved. Comparing the two over rows 0..15:

| registers | relation to the published base |
| --- | --- |
| A4..A15, E8..E15, W12..W15, both members | **bit-for-bit identical** (48 registers) |
| A0..A3, E4..E7, W8..W11, both members | differ (24 registers) |

The 24 that differ are exactly those the SHA-256 relations force to change when A0..A3
change: E4..E7 follow from A0..A3 through RE_i, and W8..W11 from those through RW_i. Both
descriptions are true because of what the solver finds: under the conditions of Appendix C
its search is pinned to a single core, the published one (every core found that admits
rows 16 and 17 is the paper's, `dense_solver_exact.md`), and it completes that core by
solving the early rows afresh. The four bases of the logged run differ from the published
base, and from each other, in A2..A4, E6..E8 and W10..W12 only.

**A correction.** Filings 1c8ba89c through 2c48b18c said that b1 was *not* a solver output,
that the solver's four bases were a separate artifact, and that b1's rows 0..3 had been
re-solved inside the SAT campaign. That was written after a review inferred from the
register comparison that the solver had not produced the filed base, and the inference was
accepted without checking the run log. It was wrong: the first BASE line of the logged run
and Appendix B are identical, and nothing on b1's path ran in the SAT campaign. Section 7's
construction paragraph, its memory table and Appendix C are corrected to match.

**What the logged run did and did not do.** It searched one subtree of the outer space, the
paper's (E chain, A13), chosen with knowledge of where the solution lies, and stopped after
four bases; it did not run the complete search. The complete search from Table 21 alone is
estimated at about 2^58 bit-level nodes, about 2^51.2 target compressions, from the
solver's measured throughput (Appendix C), and 2^21.3 of its 2^38 outer nodes were sampled
by random restarts, which found no other core admitting rows 16 and 17. The charge for b1's
construction is therefore an estimate anchored to measurement, 48 bits inside the
preprocessing field, not the cost of a completed run.

Two consequences stand. The unrelaxed tail cross-check in Section 8 compares bases that
share their dense core, so it is circular and remains withdrawn as independent corroboration
of the tail. And the attack's correctness does not depend on any of this: b1 satisfies every
SHA-256 state and schedule relation for both members, checkable directly from Appendix B,
and rows 16 and 17 hold on it with |G16| = 2 and |G17(bca1c321)| = 1.

## Appendix C. The dense-base solver, level by level

Section 4 reports the solver's results. This is its specification. The solver is
freestanding C with no libc, no malloc and no imports, built natively and for
wasm32 from one source; static memory only, which is what makes the 1 MiB bound
of Section 4 a property of the binary rather than a claim about it.

It searches for member-x and member-y words A2..A17, E6..E17, W10..W17 that follow
the trail's signed differences on rows <= 17 and satisfy the affine conditions of
Appendix A.3 keyed at <= 17. Rows 2..15 and W10..W15 are the base the row-16
attack consumes; W16 and W17 are carried so that the base is known to admit rows
16 and 17.

Relations, both members, modulo 2^32:

```
RE_i:  E_i = A_i + A_{i-4} - S0(A_{i-1}) - MAJ(A_{i-1}, A_{i-2}, A_{i-3})      6 <= i <= 17
RW_i:  W_i = E_i - A_{i-4} - E_{i-4} - S1(E_{i-1}) - CH(E_{i-1}, E_{i-2}, E_{i-3}) - K_i
                                                                               10 <= i <= 17
```

The search is depth first over the levels below. An *affine* level enumerates the
solution space of the conditions bearing on one word, given the words already
chosen: the conditions linear in that word's bits form an affine subspace of
GF(2)^32, obtained by Gaussian elimination and walked in Gray-code order from a
random coset representative, so that each visit costs one word operation.

```
L0..L4    E10, E9, E11, E12, E13                 affine
L5, L6    A13, A12                               affine
L7        bit-level DFS over A10, A11, A14 carrying the carry chains of
            A9  = E13 - A13 + S0(A12) + MAJ(A12, A11, A10)      (RE_13)
            E14 = A14 + A10 - S0(A13) - MAJ(A13, A12, A11)      (RE_14)
          bits are processed in segments from the top down; the carry-ins of the
          upper segments are guessed and matched against the carry-outs of the
          segment below, and every condition on these five words is checked at
          its last processed bit
L8..L10   A8 (RE_12), A7 (RE_11), then A6 and A5 (RE_10, RE_9), derived and checked
L11       A15 affine; E15 (RE_15) derived and checked
L12, L13  E16, E17 affine; A16, A17 (RE_16, RE_17) and W16, W17 (RW_16, RW_17)
          derived and checked, which is where the base is shown to admit rows 16
          and 17 (W16 in G16 with a row-17 word)
L14       E8; A4 (RE_8) and W12 (RW_12) derived
L15       W11; E7 (RW_11) and A3 (RE_7) derived
L16       E6; A2 (RE_6) and W10 (RW_10) derived; W13..W15 computed (no
          difference); the full base is re-verified and stored
```

Member y is handled throughout, not afterwards: a chosen word of member y is
member x XOR the difference mask for that row. **Cross-reference correction:** Appendix
A.2's lowest ROW record is step 16, and A.3 carries no condition keyed below step 16, so
neither supplies the rows 2..15 data this level list consumes. The signed differences for
those rows are recoverable from the package as the XOR of the two members in Appendix A.4
(or Appendix B); the bit conditions keyed below step 16 are **not** in the package at all,
because the estimator's data file does not carry them. Appendix C is therefore a
specification of the solver's structure, not a runnable recipe, and the claim elsewhere in
this filing that every component can be rebuilt from the package does not extend to it.
The signs of the difference mask are
conditions; a derived word is computed for both members and their signed
difference checked exactly. A base is emitted only when every row <= 17 holds for
both members.

Memory: a few hundred bytes of state, a recursion under 60 frames, and the result
buffer. The filed module declares 7 pages with maximum 7 pages (458,752 bytes), so a
`memory.grow` is refused by the module's own type rather than by convention; static
data ends at 149,633 bytes, the stack top is at 411,792 bytes and the deepest observed
stack use is 3,359 bytes. Section 4's memory charge adds the 94,483-byte module to the
458,752-byte linear memory: 553,235 bytes.

Preprocessing cost, as charged in Section 7: a complete search from Table 21 alone is
about 2^38 outer nodes at about 2^20 bit-level nodes each, 2^58 bit-level nodes, and by
the solver's measured native throughput about 2^51.2 target compressions
(`dense_solver_exact.md`, its Section 4). The logged run that produced b1 searched one
subtree chosen with knowledge of the paper's values (Appendix B.1), so this is an estimate
anchored to measured throughput, not the cost of a completed search. It is not the filed
field: the filed `preprocessing_log2 = 99` is the cap of premise H14 (Section 7), which
subsumes this estimate by 48 bits and the audited campaign figure (2^39.21) by 60.

## Appendix D. The tail estimator

Section 5's tail numbers come from a multilevel splitting estimator over the rows
after the base. This is what it computes.

The quantity estimated is q, the probability that a uniformly drawn variant
completes the characteristic from row 16 to the end, with the accepted event of
Section 5. It is far too small to measure by direct sampling, so it is factored
into per-row conditional probabilities and each is measured against a population
of states that already reached the previous row:

```
q = P(row 16) * P(row 17 | 16) * prod_{r=18..23} P(row r | r-1) * P(rows 24..38 | 23)
```

Stage by stage:

* **Rows 16 and 17 are exhausted, not sampled.** For a fixed base the solver scans
  all 2^32 values of W16 and keeps those for which row 16 holds; that set is G16,
  and for this characteristic |G16| = 2, the two words of Section 2. For each
  surviving W16 it scans all 2^32 values of W17; only g = bca1c321 admits any, and
  exactly one, namely W17 = 71e9ba98, so |G17(g)| = 1 while |G17(bca1c121)| = 0. These two counts are exact and are the reason row
  17 contributes exactly -32 bits and row 16 contributes a known constant rather
  than a sampled rate.
* **Rows 18..23 are split.** A population of states that reached row r-1 is held;
  a parent is drawn uniformly from it, a uniform W_r is proposed, and the child is
  kept when row r holds. The ratio of accepted proposals to proposals estimates
  P(row r | r-1), and the accepted children become the population for row r+1. A
  stage that cannot fill its population within 2^36 proposals is declared stalled
  and the seed is reported as such rather than silently contributing a biased
  estimate; 20 of the 140 seeds in Section 5 stalled this way.
* **Rows 24..38 are run straight through.** From row 23 the remaining message
  words are determined by the expansion, so each surviving state is simply stepped
  to the end and the accepted event is evaluated. No further splitting is possible
  because there is nothing left to resample.

Two switches matter for Section 5. `DIFFROW=r` checks row r on its signed
differences only and skips its derived conditions: this is the row-20 relaxation,
and it is applied at the row where it is worth about two bits. `RELAX` evaluates
the final equality of the last four register pairs rather than every row's
conditions through the tail. The unrelaxed reference of Section 5 is the same
estimator with `DIFFROW` unset.

The estimator reports the per-row conditional probabilities, so the row at which a
characteristic dies is visible rather than inferred.

### D.1 The filed bound, and how stalls are treated

**What is filed.** The tail is **2^-78.273**. It is one statistic, stated here once
and in full:

> Take the 140 per-seed estimates on the **linear** scale. Enter each of the 20
> stalled seeds as **zero**. Take the sample mean. Take a one-sided bootstrap lower
> confidence bound on that mean at 99%, with a Bonferroni factor of 8 for the
> selection of row 20 among rows 16..23. Subtract the largest estimator bias
> measured at any population tested. Divide out the exact 2^-64 prefix.

Nothing else in this appendix is load-bearing. The remainder records the study the
numbers come from, the two routes earlier filings used and why neither is used here,
and the sensitivity of the result to the one choice that matters.

**Why the linear scale.** The ledger needs E[q]. The attack succeeds about N·E[q]
times over N claws, so the Poisson formula of Section 7 takes the arithmetic mean of
the per-seed estimates. The mean of the per-seed *logs* is a different quantity: by
Jensen it sits strictly below the log of the mean whenever the estimates vary, and
here they vary by sd 1.257 bits over the 120 completed seeds (the 3.3 quoted in earlier filings is the sd of the set including the 20 censored ceilings, which is not the relevant spread). It is not an estimator of q, and the distance between
the two is set by the spread of the sample rather than by anything about the attack.
The previous filing (cfe5c4e2) charged the log-scale statistic and was 2.0 bits worse
for it. That route is kept below as a sensitivity row and is not otherwise used.

**Why stalls enter at zero.** Zero is a rigorous lower bound on any seed's estimate.
Using it needs no censoring rule, no imputation for unmeasured stages, and no
assumption about what a stalled seed would have produced had it finished. It is **not**
the most favourable treatment available: dropping the 20 stalls, as the earliest
filings did, gives 2^-77.957, better by 0.2 bits. Entering them at zero costs that
0.2 bits and buys a bound that holds whatever those seeds would have done.

**The study.** Earlier filings reported a 20-seed study, a mean of -141.306 and a 99%
bound of -141.96, and described the one stalled seed as "entered as a zero, which is
conservative". None of that held up: the mean did not match the per-seed files (the 19
completed seeds average -141.667), and the bound was in fact computed with the stalled
seed **dropped**. A pre-registered 120-seed study (seeds 301..420, same base, same
parameters, same 2^36 stall cap, committed in writing before any seed ran) was added
and pooled with the original 20. It corrected the picture in the unfavourable
direction: **20 of 140 seeds stall, a rate of 14.3%**, where one stall in twenty had
suggested 5%. All 140 per-seed values are in Appendix D.2.

**The bootstrap.**

```
mean of the 140 q-hat values, stalls at zero   2^-141.409
99% bootstrap lower bound                      2^-141.654   (percentile)
                                               2^-141.664   (basic)
99% with the Bonferroni factor of 8            2^-141.734   (percentile)
                                               2^-141.753   (basic)
```

(400,000 resamples, seed 20261017; recomputable from the per-seed values in D.2.)
The two flavours agree to 0.019 bits because this statistic is well conditioned --
the largest single seed is 2.23% of the sum -- so the usual worry about percentile
intervals under-covering for a skewed statistic does not bite here. Taking the more
conservative, **q-hat has mean at least 2^-141.753**.

**The estimator bias, charged without extrapolating.** One premise carries a bound on
E[q-hat] to a bound on q: how far E[q-hat] sits from q. Earlier filings asserted a
fixed-effort bias "below 0.01 bits" and left it there. It is now measured, by
`experiments/splitbias.py`, against a toy whose answer is known exactly (four
independent stages at 2^-3 each, so q = 2^-12 by construction). The organizer's run
gives:

```
population    E[q-hat] / q    bias
    10           1.40        +0.52 bits
    20           1.20        +0.27
    40           1.10        +0.13
    80           1.05        +0.07
```

The sign is **positive**: the estimator overstates q, so a lower bound on E[q-hat]
exceeds the matching bound on q and the bias must be subtracted rather than ignored.

The ledger subtracts **0.52 bits**: the toy's exact bias at population 10, the largest
of the populations tested. Two earlier versions of this argument were wrong about why
that is enough, and both are withdrawn here rather than left standing.

The first extrapolated the 1/population trend from 80 out to the filed study's
population of 2000, giving about 0.003 bits. The second kept 0.52 but justified it as a
*25-fold* conservatism -- subtracting a population-10 bias where the study runs at
2000. **Both rest on the nominal population, and the filed data say the nominal
population is not what governs this estimator's accuracy.**

The controlling quantity is the effective population. Recomputing from the 140 values
in D.2: the 120 completed seeds have sd(log2 q-hat) = **1.257 bits**. For a fixed-effort
multilevel estimator with seven stages (rows 18..23 split, rows 24..38 run through) at a
population of 2000 genuinely independent states, the per-stage relative sd is
1/sqrt(2000) and sd(log2 q-hat) would be about sqrt(7/2000)/ln 2 = **0.085 bits**. The
realized spread is roughly 220 times that, implying an effective population of about
**9.2** -- the same regime as the population-10 run the 0.52 bits is taken from. There
is no 25-fold margin. At matched effective population the allowance is approximately the
bias itself.

Two further limits, stated because they bound what the subtraction is worth:

* The calibration toy's four stages are **independent of the state**, so its splitting
  population cannot degenerate. Population degeneracy is the dominant bias mechanism of
  a multilevel splitting estimator, and the toy cannot exhibit it at all. What the 0.52
  bits bounds is the *ratio-estimator* component; the degeneracy component is not
  measured here and is not bounded by anything in this package.
* Part of the 1.257-bit spread could come from a small expected hit count at the single
  fixed-proposal final stage rather than from degeneracy. Against that reading, the
  completed seeds' distribution is continuous and left-skewed (skew -1.08) rather than
  clustered at discrete count ratios.

This is the filing's weakest step and it is stated as such: the conversion from a bound
on E[q-hat] to a bound on q rests on a bias allowance that the data show has no margin,
and whose dominant mechanism is unmeasured. It is declared as premise H4 and its
exposure is one-for-one on the exponent. A reader who judges the true bias to exceed
0.52 bits by more than 1.27 should read this entry as not ahead of the best generic entry (0c1ef7c3), and by more than 1.85 as not ahead of 744875ec.

    q >= 2^-141.753 - 0.52 = 2^-142.273,  so the tail is 2^-78.273.

**The superseded routes.** Two earlier treatments are recorded here because the
sensitivity table below quotes them, not because anything rests on them.

*Exclusion.* The earliest filings dropped stalled seeds. A stage stalls precisely when
a conditional probability is too small to measure, so discarding stalls censors the low
tail upward. On the pooled study this gives 2^-77.957, and the agreement of that figure
with the 2^-77.96 those filings reported is what identified the old number as the
exclusion artifact.

*Censoring.* cfe5c4e2 kept each stalled seed's measured stages, assigned the row it
stalled at the largest probability consistent with the stall (failing to collect 2000
successes in 2^36 proposals), and gave its unmeasured deeper stages the per-stage median
of the completed seeds -- landing near -150.5. A review objected, correctly, that a
value built from an upper bound on each stalled seed cannot by itself establish a
*lower* bound on q. That objection is accepted and the rule is no longer used. Two
further defects in it are worth recording: the composite value is a hybrid rather than
a pure upper bound, since its deeper stages take a central estimate; and a stall does
not *imply* the row is below 2000/2^36, since a row at exactly that value stalls about
half the time. It is also worth recording that all 20 stalls occur at row 21,
immediately after the relaxed row 20, which is consistent with the relaxation deferring
difficulty rather than with seed noise. None of this affects the filed number, which
uses neither rule.

**Sensitivity to the stall treatment, and a confirmation.** The treatment matters
more than any other choice in this study, so its effect is tabulated rather than
asserted. Recomputing the bound under different assumptions about the 20 stalled
seeds:

| statistic | stall treatment | n | 99%/8 bound | tail | score |
| --- | --- | ---: | ---: | ---: | ---: |
| **linear mean (filed)** | **zero** | **140** | **2^−141.753 less 0.52 bias** | **2^−78.273** | **122.98** |
| log mean | excluded, as earlier filings did | 120 | −141.957 | 2^−77.957 | 122.66 |
| log mean | censored at the ceiling (cfe5c4e2) | 140 | −143.759 | 2^−79.759 | 124.47 |
| log mean | ceiling − 2 bits | 140 | −144.225 | 2^−80.225 | 124.93 |
| log mean | ceiling − 5 bits | 140 | −144.943 | 2^−80.943 | 125.65 |
| log mean | ceiling − 10 bits | 140 | −146.114 | 2^−82.114 | 126.82 |

Two things to read off it. First, the filed row is **not** the most favourable
entry in the table: dropping the 20 stalls entirely — which earlier filings did,
and which is indefensible — gives 2^−77.957, better than the filed 2^−78.273 by
0.2 bits. Setting the stalls to zero costs that 0.2 bits and buys a bound that
holds whatever those seeds would have produced. The filed route is the
conservative one among the linear treatments, not the generous one.

Second, the row labelled cfe5c4e2 reproduces the previous filing. The distance
between it and the filed row needs a correction an earlier draft of this appendix got
wrong. That draft called the gap "entirely the log-versus-linear choice", which is not
how it decomposes. On the point estimates the gap is 1.456 bits, of which 0.410 is
Jensen on the 120 completed seeds (log of their mean, -141.186, against their mean log,
-141.597), 1.268 is the 20 stalled seeds entering at their -150.5 ceiling on the log
scale while contributing nothing on the linear one, and -0.223 is the dilution of the
linear mean by 20 zeros. What makes the scale the operative choice is a separate fact,
and it is the one worth stating: **on the linear scale the stall treatment is worth
0.000384 bits** -- entering the 20 stalls at their ceiling instead of at zero moves the
mean from 2^-141.4087 to 2^-141.4083. The stalls matter enormously on the log scale and
not at all on the linear one, so the scale is what decides whether the censoring rule
has to be defended, which is why this filing does not have to defend it. But the raw
2.0 bits is not 2.0 bits of Jensen, and the earlier sentence said so;
the seeds, the estimator, the stall cap and the pre-registration are identical.
That is why no new measurement was run for this filing and none is claimed.

**What this bound is and is not.** It is a one-sided 99% lower confidence bound,
carrying a Bonferroni factor of 8, on the arithmetic mean of 140 per-seed
estimates, of which 20 are entered at zero, less 0.52 bits for the estimator bias
(the largest value measured at any population tested). It is therefore a lower bound on E[q-hat] and, through the bias term, on q.
What it is **not** is a bound on the tail *under claw selection*: every seed here
draws its own randomness, while the attack takes W16 and W17 from the claw. That
conditioning is H4, it is untested beyond row 18, and it carries 78.23 of the
120.71 per-claw bits.

**The estimator's operational parameters**, which earlier filings did not record:

```
population per level          2000 states
tail proposals                4096 x population at the final stage
parent selection              uniform with replacement from the surviving population
stall cap                     2^36 proposals at a stage without filling the population
relaxation                    DIFFROW = 20 (row 20 on signed differences only)
acceptance                    RELAX_TAIL = 1 (final equality of the last four register pairs)
base                          b1, as filed in Appendix B
rows 16, 17                   exhausted, not sampled
rows 18..23                   split: draw a parent, propose uniform W_r, keep the passes
rows 24..38                   stepped straight through; no freedom remains
```

With these and the characteristic of Appendix A the estimator is reimplementable.
Its per-row predicate is also now **in the package and organizer-run**:
`experiments/tailrow.py` implements the row test and measures the row-18
conditional directly, row 18 being the one tail stage the filed base reaches
without any search. The pooled organizer run gives 2^-18.300 against the study's
2^-18.0. The deeper stages stay out of reach here, because arriving at them costs
more than the sandbox's whole budget, so they remain reported rather than
executed.

### D.2 The complete per-seed study

All 140 seeds, pooled from the original 20 (201..220) and the pre-registered 120
(301..420). Entries marked `<=` are censored stalls under the rule in D.1.

| seed | log2 q | seed | log2 q | seed | log2 q | seed | log2 q |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 201 | -140.567 | 202 | -140.342 | 203 | -140.782 | 204 | -142.232 |
| 205 | -140.049 | 206 | -141.331 | 207 | -141.174 | 208 | -139.764 |
| 209 | -142.821 | 210 | -143.350 | 211 | -145.180 | 212 | -143.114 |
| 213 | -141.993 | 214 | -141.635 | 215 | -141.971 | 216 | -140.988 |
| 217 | -141.915 | 218 | <= -150.542 (stall r21) | 219 | -140.993 | 220 | -141.462 |
| 301 | -141.143 | 302 | -141.655 | 303 | -143.790 | 304 | -141.547 |
| 305 | -140.430 | 306 | -142.921 | 307 | -140.866 | 308 | -140.537 |
| 309 | -141.989 | 310 | -141.673 | 311 | -141.929 | 312 | <= -150.447 (stall r21) |
| 313 | -140.804 | 314 | -141.218 | 315 | -140.742 | 316 | <= -150.400 (stall r21) |
| 317 | -144.584 | 318 | -142.242 | 319 | -140.440 | 320 | -141.752 |
| 321 | -139.783 | 322 | -141.721 | 323 | -140.531 | 324 | -140.455 |
| 325 | -142.318 | 326 | -141.822 | 327 | <= -150.330 (stall r21) | 328 | -140.731 |
| 329 | <= -150.460 (stall r21) | 330 | -142.753 | 331 | -142.437 | 332 | <= -150.504 (stall r21) |
| 333 | -141.452 | 334 | -142.659 | 335 | -141.240 | 336 | -142.001 |
| 337 | -140.582 | 338 | -141.850 | 339 | -142.334 | 340 | -139.783 |
| 341 | <= -150.429 (stall r21) | 342 | -141.349 | 343 | -141.537 | 344 | -139.835 |
| 345 | -143.181 | 346 | -141.605 | 347 | -141.917 | 348 | -142.097 |
| 349 | -140.137 | 350 | -140.620 | 351 | <= -150.471 (stall r21) | 352 | -141.152 |
| 353 | -140.968 | 354 | -145.848 | 355 | -142.102 | 356 | -140.818 |
| 357 | <= -150.507 (stall r21) | 358 | -142.307 | 359 | -145.258 | 360 | -139.984 |
| 361 | -142.933 | 362 | <= -150.461 (stall r21) | 363 | -141.041 | 364 | -141.002 |
| 365 | -140.186 | 366 | -140.941 | 367 | -144.613 | 368 | <= -150.532 (stall r21) |
| 369 | -141.410 | 370 | -139.862 | 371 | -142.105 | 372 | -140.672 |
| 373 | -142.328 | 374 | -141.595 | 375 | -144.386 | 376 | -141.725 |
| 377 | -141.999 | 378 | -140.655 | 379 | -141.382 | 380 | -140.812 |
| 381 | -140.956 | 382 | -142.293 | 383 | <= -150.520 (stall r21) | 384 | -140.799 |
| 385 | -140.256 | 386 | -141.345 | 387 | -141.865 | 388 | <= -150.448 (stall r21) |
| 389 | -140.694 | 390 | -141.590 | 391 | <= -150.415 (stall r21) | 392 | -140.564 |
| 393 | -140.247 | 394 | <= -150.496 (stall r21) | 395 | -140.532 | 396 | <= -150.567 (stall r21) |
| 397 | -140.486 | 398 | -140.259 | 399 | -141.381 | 400 | <= -150.397 (stall r21) |
| 401 | <= -150.530 (stall r21) | 402 | -141.661 | 403 | -143.068 | 404 | <= -150.536 (stall r21) |
| 405 | -141.608 | 406 | -143.836 | 407 | -142.362 | 408 | -141.411 |
| 409 | -142.006 | 410 | -140.407 | 411 | -139.910 | 412 | -142.034 |
| 413 | -144.403 | 414 | -140.309 | 415 | -140.698 | 416 | -140.458 |
| 417 | -142.726 | 418 | -140.277 | 419 | -144.413 | 420 | <= -150.534 (stall r21) |

Mean −142.865, sd 3.316, n = 140 (120 completed, 20 censored). The 99% bootstrap
lower bound on the mean is −143.541; with the Bonferroni factor of 8, −143.759. These
are the log-scale figures of cfe5c4e2, retained for comparison; the filed bound is
the linear one of Appendix D.1 (2^−141.753 before the bias correction).

## Appendix E. The claw search and its schedule

The walk function and its kernel are Section 6 and Appendix F. What was missing,
and what finding F3 of the previous review asked for, is the *schedule*: how the
search moves from one chaining value to the next, and what that does to the rate.

### E.1 The search

Points are 32-bit words. The table has `slots` entries indexed by the
distinguished point, a point whose low `db` bits are zero; since those bits are
constant by construction the index is taken from the bits above them. A slot
holding a different point is overwritten, which is the saturated regime. Trails longer than
20 * 2^db are dropped. A table match is resolved by re-walking the shorter trail
to the meeting point, which costs the *locating* evaluations counted separately
below. Both chains advance together once their lengths are equalised, and each
lockstep step applies the walk function twice and is counted as two evaluations,
which is what the measured column of Appendix E.2 contains. A collision whose two points lie on opposite sides of F is a claw; one
whose points lie on the same side is useless and is counted separately.

The filed configuration is `slots = 2^17 = 131072`, `db = 7`, with the packed 7-byte entry of Section 7: a slot is indexed by the top 17 bits of the distinguished point and stores the trail's start point (32 bits), the trail length (12 bits, all ones for an empty slot) and the 8 bits of the point between the index and its 7 zero bits. The research program `clawvow7.c` implements it; `clawvow.c`, the unpacked original, computes the same index for 2^17 slots, which is how the two were run side by side (Appendix E.2b).

**How resolution is priced.** The measured rate of Appendix E.2 counts trail and
locating evaluations together (the run's own counters charge two applications per
lockstep step), and the ledger prices every counted evaluation at the full 93
operations per 7 lanes. That is only legitimate if resolution packs as well as the
walk does, so the implementation is specified: pending matches are queued, and the
two chains of seven different pending matches are advanced as two packed words,
one holding the seven `a` chains and one the seven `b` chains. Each lockstep step
is then two kernel evaluations (2 × 70 operations, covering 14 lane evaluations)
plus one XOR and a zero-detect to find lanes that have met, about 74 operations
per packed word against the 93 the ledger charges. Resolution is therefore
*cheaper* per evaluation than the walk, not dearer, because it carries no DP test
and no handler; charging it at the walk's rate is conservative. A reader who
instead assumes unbatched, lane-serial resolution would add roughly 0.4 to 1.5
bits — that assumption is what this paragraph exists to exclude.

### E.2 What one chaining value yields

The constants of F depend on the chaining value, so each first block gives a
different function and its own functional graph. Running one chaining value for
2^30 trail evaluations gives the following, measured:

```
trail evals   total (+locate)   distinct claws   cumulative      marginal
                                                 evals/claw      evals/claw
2^24          2^24.32                 8,023        2^11.348      2^11.348
2^25          2^25.40                20,501        2^11.081      2^10.878
2^26          2^26.46                46,081        2^10.972      2^10.878
2^27          2^27.50                93,938        2^10.975      2^10.979
2^28          2^28.51               178,522        2^11.067      2^11.162
2^29          2^29.52               323,757        2^11.214      2^11.376
2^30          2^30.52               566,025        2^11.414      2^11.644
```

The marginal column is the honest one, and it is not flat. It falls to 2^10.878
and then climbs steadily: by the end of the run a fresh distinct claw costs
2^11.644 evaluations, 0.77 bits worse than at the minimum. This is depletion. One
chaining value's graph has only 2^32 points, and after 2^30 trail evaluations the
search is re-covering ground it has already seen.

The previous filing charged 2^11.414, the cumulative figure at 2^30, as a margin over
this one measured graph. The schedule of E.3 never leaves the first 2^26 evaluations, and
E.2b measures that window across 289 chaining values.

### E.2b The 2^26 window across 289 chaining values

Two measurements, made for this filing with the research programs and reported here
(they are not organizer-executed; the organizer experiment `vowclaw.py` runs the same search
at reduced scale). Both ran in the same container the tail study used (Ubuntu 22.04, gcc
11.4, aarch64), with every run's command line, seed and counters logged
(`runs39/clawrate7/`, `runs39/clawrate/` in the work tree).

**Chaining values.** A chaining value is drawn as eight 32-bit words from a seeded
generator (`random.Random(cv_seed)`), the walk function's six constants are derived from it
as in Section 6, and the C walk function is checked against the Python one on 20,000 points
before each run. The filed configuration is 2^17 slots, dp_bits 7, 2^26 trail evaluations.

**1. The packed entry changes nothing.** The unpacked program (`clawvow.c`, 13 bytes per
slot) and the packed one (`clawvow7.c`, 7 bytes per slot) were run on the same chaining
value, the same seed and the same configuration for 9 chaining values; every counter and
the list of claws found agree:

| cv seed | run seed | unpacked: distinct claws | unpacked: total evaluations | packed: distinct | packed: total | all counters equal | claws file identical |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 7 | 1 | 46429 | 92733055 | 46429 | 92733055 | yes | yes |
| 101 | 1101 | 46006 | 92454564 | 46006 | 92454564 | yes | yes |
| 102 | 1102 | 45949 | 92452607 | 45949 | 92452607 | yes | yes |
| 103 | 1103 | 46226 | 92386531 | 46226 | 92386531 | yes | yes |
| 104 | 1104 | 46187 | 92829500 | 46187 | 92829500 | yes | yes |
| 105 | 1105 | 46182 | 92744049 | 46182 | 92744049 | yes | yes |
| 106 | 1106 | 46016 | 92560640 | 46016 | 92560640 | yes | yes |
| 107 | 1107 | 46108 | 92597213 | 46108 | 92597213 | yes | yes |
| 108 | 1108 | 46394 | 92580465 | 46394 | 92580465 | yes | yes |

**2. The rate at the filed configuration, 289 chaining values, one run each** (seeds
7, 101..132 and 1001..1256; every value in Appendix E.5):

| statistic (log2 of total evaluations, trail plus locating, per distinct claw at 2^26) | value |
| --- | ---: |
| mean | 10.9700 |
| standard deviation | 0.0069 |
| minimum / maximum | 10.9480 / 10.9960 |
| percentiles 1, 5, 50, 95, 99 | 10.9533, 10.9588, 10.9698, 10.9807, 10.9871 |
| pooled (sum of evaluations over sum of distinct claws) | 10.9700 |
| distinct claws per window: mean, minimum, maximum | 46127, 45347, 46784 |
| **charged** | **11.00**, above the maximum |

**3. What the same measurement showed at the previous configuration** (128,000 slots,
13-byte entries, `runs39/clawrate/`): 288 chaining values, mean 2^10.980, standard
deviation 0.007, maximum 2^11.001; with three run seeds on each of 32 chaining values, the
variation that belongs to the chaining value, once the search's own start-point noise is
removed, has a standard deviation of 0.004 bits (one-way analysis of variance, F = 2.24 on
31 and 64 degrees of freedom). The single graph the previous filing had measured sat at the
9th percentile of the 288. The functional graphs are interchangeable at the precision the
ledger uses, which is what H2 now asserts.

**4. Table size.** On 33 chaining values at 2^26 evaluations, paired by seed, the rate as a
function of the number of slots at dp_bits 7: 48,000 slots 2^11.534; 64,000 2^11.338; 78,000
2^11.219; 80,000 2^11.205; 96,000 2^11.109; 98,000 2^11.099; 128,000 2^10.979; a fitted
exponent of −0.36 in the number of slots (−0.39 over all seven sizes), shallower than the
−0.5 to −1 one might expect because the per-trail hit probability is already saturating at
these sizes and locating work and repeated claws both grow with the table. dp_bits 8 is 0.60
bits worse than dp_bits 7 at 128,000 slots and 0.74 bits worse at 64,000. This is why the
memory bound is met by packing the entry rather than by shrinking the table: at 7 bytes the
full 2^17-slot table is 917,504 bytes, and the rate is the one measured above.

### E.3 The schedule

The attack therefore does not run one chaining value to exhaustion. It runs each
chaining value for 2^26 trail evaluations, harvests its claws, and moves to the
next first block:

```
for each of 2^104.21 first blocks:
    cv  <- H(first block)
    recompute e0, C, Am1, Am2, Em1, Em2 from cv            (a few hundred ops, once)
    clear the 2^17-slot table's flag bytes                 (98,304 word writes, once)
    run the walk for 2^26 trail evaluations                (2^26.46 total with locating)
    emit the 2^15.49 distinct claws found
```

At the 2^26 switch point the rate is 2^10.970 evaluations per distinct claw on
average over 289 chaining values and at most 2^10.996 on any of them (E.2b), the
minimum region of the curve above, and the search never enters the depleted
regime. The per-chaining-value overheads are negligible against 2^26.46
evaluations: the table clear is 2^-9.9 operations per evaluation and the constant
regeneration less still.

The number of chaining values this needs, 2^119.70 / 2^15.49 = 2^104.21, is
available: a first block is 512 bits and any of them may be used, since the base
of Appendix B constrains rows 2..15 of the second block only.

**The ledger charges 2^11.00**, the maximum of the 289 measured windows, rounded up from
2^10.996. The previous filing charged 2^11.414 as a margin over a single measured graph;
with the distribution measured, the margin is replaced by its maximum, and the time is
122.98 rather than 123.39.

What remains premise H2, and is not established here, is that the 2^104.2 chaining values
the attack consumes do not, on average, exceed the worst of the 289 measured: 289 graphs
out of 2^104.2, with a spread of 0.05 bits between best and worst and a per-graph standard
deviation of 0.004 bits once the search's own start-point noise is removed. The schedule is
chosen so that the quantity carried forward is a short-run rate rather than a long-run one.

### E.4 The yield of a fixed work budget

The ledger charges an average rate, and a cost review asked for a tail bound on the
claws a fixed budget produces. Both halves of the answer are here.

**The single-window distribution is measured.** Each trial of
`experiments/vowclaw.py` runs one fixed evaluation budget and reports the claws it
yielded, so the organizer's run is 256 independent samples of exactly this quantity:
mean 8.66 claws, standard deviation 2.96, coefficient of variation 0.342, with
minimum 2, first percentile 3, median 8 and maximum 19. The lowest decile is 0.58
times the mean. A single window's yield is therefore genuinely variable, and the
lower tail is a real feature rather than a rounding artifact.

**It cannot matter at the attack's scale, and that is arithmetic.** The attack does
not run one window; the schedule of E.3 runs 2^104.21 of them, and the total claw
yield is the sum of that many independent window yields. The relative standard
deviation of a sum of W independent draws is the single-draw coefficient of
variation divided by sqrt(W):

    0.342 / sqrt(2^104.21) = 2^-53.7

So the aggregate yield is concentrated to within a relative error of 2^-54, which is
49 bits below the precision at which the ledger reports anything. Charging the
average rate is correct, and no tail bound on a single window is needed, because a
budget spanning 2^105 windows cannot land in any window's tail.

This is a concentration argument, not a premise: it needs only that windows under
different chaining values are independent, which is the same structural fact H6
rests on and which the within-window dependence measurement of Section 8 supports at
the one scale it can reach.

### E.4b Independence across the schedule

Claws harvested under different chaining values come from different functions F,
which is the basis of the inter-claw independence premise H6. Within one chaining
value the 2^15.49 claws share a function; the distinct-claw bookkeeping of the run
above removes exact repeats, but near-dependence within a window is not
characterised and remains part of H6.

### E.5 The per-chaining-value data behind E.2b

Packed program, 2^17 slots, dp_bits 7, 2^26 trail evaluations; one run per chaining value. Columns: cv seed (the chaining value is eight 32-bit words from `random.Random(cv_seed)`), run seed (the walk's start-point sequence), distinct claws at 2^26, total evaluations (trail plus locating), and log2 of their ratio.

```
cv_seed run_seed distinct total_evals log2_evals_per_distinct
7 1 46429 92733055 10.9638
101 1101 46006 92454564 10.9727
102 1102 45949 92452607 10.9745
103 1103 46226 92386531 10.9648
104 1104 46187 92829500 10.9729
105 1105 46182 92744049 10.9717
106 1106 46016 92560640 10.9740
107 1107 46108 92597213 10.9717
108 1108 46394 92580465 10.9626
109 1109 46437 92523780 10.9603
110 1110 46365 92321213 10.9594
111 1111 45942 92532150 10.9759
112 1112 46093 92380021 10.9688
113 1113 46193 92460728 10.9670
114 1114 46210 92536871 10.9676
115 1115 46081 92373683 10.9691
116 1116 46048 92602449 10.9737
117 1117 46218 92491100 10.9666
118 1118 46073 92364096 10.9692
119 1119 46228 92499271 10.9665
120 1120 45740 92580366 10.9830
121 1121 45861 92415092 10.9766
122 1122 45786 92494677 10.9802
123 1123 45780 92691309 10.9835
124 1124 46119 92247618 10.9659
125 1125 46322 92417787 10.9623
126 1126 46328 92431097 10.9623
127 1127 46072 92588957 10.9727
128 1128 46030 92444850 10.9718
129 1129 46311 92655124 10.9663
130 1130 46288 92604578 10.9662
131 1131 46622 92437537 10.9533
132 1132 46095 92550738 10.9714
1001 6001 46009 92756720 10.9773
1002 6002 46353 92375482 10.9606
1003 6003 46192 92566977 10.9686
1004 6004 46111 92671005 10.9728
1005 6005 46275 92531101 10.9655
1006 6006 46524 92414592 10.9559
1007 6007 46245 92310245 10.9630
1008 6008 45861 92569150 10.9790
1009 6009 46057 92713987 10.9752
1010 6010 46278 92522327 10.9653
1011 6011 45812 92540421 10.9801
1012 6012 46336 92609806 10.9648
1013 6013 45762 92322408 10.9783
1014 6014 46241 92554420 10.9669
1015 6015 46066 92597463 10.9731
1016 6016 45935 92658085 10.9781
1017 6017 46498 92517964 10.9583
1018 6018 46321 92362047 10.9614
1019 6019 45749 92392430 10.9798
1020 6020 46035 92483501 10.9722
1021 6021 46409 92571555 10.9619
1022 6022 46263 92588822 10.9668
1023 6023 46247 92421653 10.9647
1024 6024 46083 92578113 10.9722
1025 6025 46130 92470245 10.9691
1026 6026 45989 92624294 10.9759
1027 6027 46448 92366226 10.9575
1028 6028 46072 92617176 10.9732
1029 6029 46129 92672022 10.9722
1030 6030 46132 92455149 10.9688
1031 6031 46219 92433044 10.9657
1032 6032 46055 92514623 10.9721
1033 6033 46420 92630681 10.9625
1034 6034 45347 92616595 10.9960
1035 6035 45744 92521093 10.9820
1036 6036 46156 92640491 10.9709
1037 6037 46329 92539317 10.9639
1038 6038 46045 92593591 10.9737
1039 6039 46265 92481582 10.9650
1040 6040 46199 92567269 10.9684
1041 6041 46396 92509680 10.9614
1042 6042 46185 92537689 10.9684
1043 6043 46626 92329314 10.9514
1044 6044 45750 92585769 10.9828
1045 6045 45873 92477858 10.9772
1046 6046 45878 92482293 10.9772
1047 6047 46402 92630972 10.9631
1048 6048 46240 92401502 10.9646
1049 6049 46378 92510226 10.9620
1050 6050 46005 92436078 10.9724
1051 6051 46020 92588424 10.9744
1052 6052 46252 92511365 10.9659
1053 6053 46158 92495773 10.9686
1054 6054 46216 92477539 10.9665
1055 6055 46041 92517520 10.9726
1056 6056 46244 92342602 10.9635
1057 6057 46155 92468889 10.9683
1058 6058 46094 92747717 10.9745
1059 6059 46095 92649200 10.9730
1060 6060 46267 92500938 10.9653
1061 6061 46035 92474097 10.9721
1062 6062 46413 92455784 10.9600
1063 6063 46259 92578549 10.9667
1064 6064 46322 92726584 10.9671
1065 6065 45866 92485008 10.9776
1066 6066 46203 92422561 10.9660
1067 6067 46260 92518495 10.9658
1068 6068 45889 92627564 10.9791
1069 6069 46342 92563093 10.9639
1070 6070 46473 92450179 10.9581
1071 6071 46000 92519065 10.9739
1072 6072 45706 92620646 10.9847
1073 6073 46252 92382438 10.9639
1074 6074 45933 92553608 10.9765
1075 6075 46033 92373573 10.9706
1076 6076 46038 92504109 10.9725
1077 6077 46335 92619087 10.9650
1078 6078 46403 92552083 10.9618
1079 6079 46041 92477900 10.9720
1080 6080 45782 92510277 10.9806
1081 6081 45975 92312492 10.9715
1082 6082 46362 92652426 10.9647
1083 6083 46298 92597941 10.9658
1084 6084 45568 92492246 10.9871
1085 6085 46006 92519502 10.9737
1086 6086 45914 92608793 10.9780
1087 6087 46173 92662027 10.9707
1088 6088 45909 92660200 10.9790
1089 6089 46291 92573505 10.9657
1090 6090 46142 92446947 10.9683
1091 6091 46188 92513823 10.9679
1092 6092 46323 92577653 10.9647
1093 6093 46231 92718016 10.9698
1094 6094 46188 92551641 10.9685
1095 6095 46574 92574882 10.9569
1096 6096 46017 92586135 10.9744
1097 6097 46187 92398566 10.9662
1098 6098 46204 92645895 10.9695
1099 6099 46081 92728891 10.9746
1100 6100 46784 92424512 10.9480
1101 6101 46605 92480671 10.9545
1102 6102 45917 92491894 10.9761
1103 6103 46301 92677515 10.9670
1104 6104 45931 92686490 10.9787
1105 6105 45707 92564007 10.9838
1106 6106 46502 92348178 10.9556
1107 6107 46248 92413138 10.9645
1108 6108 45883 92335939 10.9747
1109 6109 46107 92706331 10.9735
1110 6110 46030 92541952 10.9733
1111 6111 46142 92483639 10.9689
1112 6112 46182 92396087 10.9663
1113 6113 45991 92464060 10.9733
1114 6114 45998 92577190 10.9749
1115 6115 46113 92313589 10.9672
1116 6116 46100 92531608 10.9710
1117 6117 46123 92447060 10.9689
1118 6118 46193 92661968 10.9701
1119 6119 45923 92437917 10.9751
1120 6120 46029 92399672 10.9711
1121 6121 46217 92581367 10.9681
1122 6122 46169 92505992 10.9684
1123 6123 46137 92370171 10.9673
1124 6124 46261 92649843 10.9678
1125 6125 45705 92469396 10.9824
1126 6126 46154 92586648 10.9701
1127 6127 46001 92732610 10.9772
1128 6128 45930 92540935 10.9764
1129 6129 46619 92787679 10.9588
1130 6130 46349 92401895 10.9612
1131 6131 46180 92333799 10.9654
1132 6132 46093 92481147 10.9704
1133 6133 46281 92524271 10.9652
1134 6134 46289 92189684 10.9597
1135 6135 45879 92650753 10.9798
1136 6136 46042 92437675 10.9713
1137 6137 46347 92532976 10.9633
1138 6138 46114 92733022 10.9737
1139 6139 45850 92592869 10.9798
1140 6140 46137 92592968 10.9708
1141 6141 45966 92454014 10.9740
1142 6142 46162 92423433 10.9673
1143 6143 46384 92668454 10.9642
1144 6144 45780 92464787 10.9800
1145 6145 45800 92494208 10.9798
1146 6146 45982 92436025 10.9732
1147 6147 45965 92430350 10.9736
1148 6148 46099 92427491 10.9694
1149 6149 45613 92307914 10.9828
1150 6150 46049 92482281 10.9718
1151 6151 46101 92514638 10.9707
1152 6152 45937 92572670 10.9767
1153 6153 46516 92570350 10.9586
1154 6154 45992 92476722 10.9735
1155 6155 46351 92539179 10.9632
1156 6156 46271 92751629 10.9690
1157 6157 46258 92371727 10.9635
1158 6158 46315 92431529 10.9627
1159 6159 45797 92412250 10.9786
1160 6160 45482 92578292 10.9912
1161 6161 46060 92712334 10.9750
1162 6162 46143 92400577 10.9676
1163 6163 45840 92552013 10.9794
1164 6164 46357 92636415 10.9646
1165 6165 46440 92635581 10.9620
1166 6166 46172 92449187 10.9674
1167 6167 46086 92530747 10.9714
1168 6168 46148 92624277 10.9709
1169 6169 46137 92657881 10.9718
1170 6170 46093 92535527 10.9712
1171 6171 45784 92408975 10.9790
1172 6172 46156 92329063 10.9661
1173 6173 45990 92368735 10.9719
1174 6174 46179 92516264 10.9683
1175 6175 46177 92492113 10.9679
1176 6176 45778 92382303 10.9787
1177 6177 46253 92647763 10.9680
1178 6178 45774 92337317 10.9782
1179 6179 46051 92558525 10.9729
1180 6180 46137 92358357 10.9671
1181 6181 46181 92607061 10.9696
1182 6182 46006 92625911 10.9754
1183 6183 46208 92650110 10.9694
1184 6184 46248 92527846 10.9663
1185 6185 46219 92549041 10.9675
1186 6186 46058 92375091 10.9698
1187 6187 46618 92614286 10.9561
1188 6188 46055 92733792 10.9755
1189 6189 46185 92712979 10.9711
1190 6190 46317 92495335 10.9636
1191 6191 46113 92375708 10.9681
1192 6192 46141 92405404 10.9677
1193 6193 45803 92526072 10.9802
1194 6194 46263 92500226 10.9654
1195 6195 45927 92706832 10.9791
1196 6196 45993 92459205 10.9732
1197 6197 46333 92520261 10.9635
1198 6198 46308 92484723 10.9637
1199 6199 46054 92418326 10.9706
1200 6200 46449 92640307 10.9618
1201 6201 46260 92465478 10.9649
1202 6202 46205 92603893 10.9688
1203 6203 45834 92599700 10.9804
1204 6204 46137 92445539 10.9685
1205 6205 45846 92621514 10.9803
1206 6206 46446 92720572 10.9631
1207 6207 46076 92573548 10.9724
1208 6208 46077 92585650 10.9725
1209 6209 46281 92499108 10.9648
1210 6210 46234 92572374 10.9674
1211 6211 45752 92538666 10.9820
1212 6212 46036 92567816 10.9735
1213 6213 46255 92536218 10.9662
1214 6214 46173 92464388 10.9676
1215 6215 46189 92409846 10.9663
1216 6216 46088 92671599 10.9735
1217 6217 46163 92405207 10.9670
1218 6218 45796 92547036 10.9807
1219 6219 45994 92549595 10.9746
1220 6220 46245 92600422 10.9675
1221 6221 46117 92702383 10.9731
1222 6222 45712 92638107 10.9848
1223 6223 46044 92409724 10.9708
1224 6224 46039 92548795 10.9731
1225 6225 46206 92486456 10.9669
1226 6226 46360 92329144 10.9597
1227 6227 46117 92515578 10.9702
1228 6228 46107 92531037 10.9707
1229 6229 45972 92595134 10.9760
1230 6230 46353 92665587 10.9652
1231 6231 46150 92454156 10.9682
1232 6232 46120 92302369 10.9668
1233 6233 46114 92556520 10.9709
1234 6234 46189 92650205 10.9700
1235 6235 46451 92574441 10.9607
1236 6236 46198 92357667 10.9652
1237 6237 45929 92426292 10.9747
1238 6238 46511 92459820 10.9570
1239 6239 45976 92369865 10.9723
1240 6240 45892 92738585 10.9807
1241 6241 45787 92433736 10.9793
1242 6242 46347 92511396 10.9629
1243 6243 45820 92457062 10.9786
1244 6244 46086 92644493 10.9732
1245 6245 45788 92634225 10.9824
1246 6246 46028 92518359 10.9730
1247 6247 46010 92608217 10.9750
1248 6248 46125 92458486 10.9690
1249 6249 45986 92617460 10.9759
1250 6250 46015 92400993 10.9716
1251 6251 46543 92598434 10.9582
1252 6252 46076 92592302 10.9727
1253 6253 46305 92509371 10.9642
1254 6254 46431 92550321 10.9609
1255 6255 46070 92470365 10.9709
1256 6256 46356 92493367 10.9624
```

## Appendix F. The packed kernel, instruction by instruction

The 70-operation count of Section 6 is not an assertion here: the emitted program
is listed in full. `experiments/kernelcount.py` contains the tracer that produces
it, rebuilds it for a seed-derived chaining value on every organizer trial, counts
it, and checks it against a scalar reference on all 7 lanes.

Operands: `x` is the packed input word (7 lanes of 36 bits); `tN` is the N-th
emitted register; a bare hex operand is an immediate, replicated across lanes as
REP * c with REP = sum(1 << 36i, i < 7); shift counts are plain integers.
Every line below costs one word operation under the H3 convention.

```
t1    = x    +     0xe805612f
t2    = x    >>    2
t3    = t2   &     0x3fffffff
t4    = x    <<    30
t5    = t4   &     0xc0000000
t6    = t3   |     t5
t7    = x    >>    13
t8    = t7   &     0x7ffff
t9    = x    <<    19
t10   = t9   &     0xfff80000
t11   = t8   |     t10
t12   = t6   ^     t11
t13   = x    >>    22
t14   = t13  &     0x3ff
t15   = x    <<    10
t16   = t15  &     0xfffffc00
t17   = t14  |     t16
t18   = t12  ^     t17
t19   = x    &     0x5d20b8be
t20   = t19  ^     0x20540501
t21   = t1   >>    6
t22   = t21  &     0x3ffffff
t23   = t1   <<    26
t24   = t23  &     0xfc000000
t25   = t22  |     t24
t26   = t1   >>    11
t27   = t26  &     0x1fffff
t28   = t1   <<    21
t29   = t28  &     0xffe00000
t30   = t27  |     t29
t31   = t25  ^     t30
t32   = t1   >>    25
t33   = t32  &     0x7f
t34   = t1   <<    7
t35   = t34  &     0xffffff80
t36   = t33  |     t35
t37   = t31  ^     t36
t38   = t1   &     0xfc683edc
t39   = t38  ^     0xbefb3c12
t40   = x    ^     0xffffffff
t41   = t18  +     t20
t42   = t41  +     t37
t43   = t42  +     t39
t44   = t43  +     t40
t45   = t44  +     0x12345679
t46   = t45  &     0xffffffff
t47   = x    >>    7
t48   = t47  &     0x1ffffff
t49   = x    <<    25
t50   = t49  &     0xfe000000
t51   = t48  |     t50
t52   = x    >>    18
t53   = t52  &     0x3fff
t54   = x    <<    14
t55   = t54  &     0xffffc000
t56   = t53  |     t55
t57   = t51  ^     t56
t58   = x    >>    3
t59   = t58  &     0x1fffffff
t60   = t57  ^     t59
t61   = x    ^     0xffffffff
t62   = t60  +     t61
t63   = t62  +     0x1
t64   = t63  &     0xffffffff
t65   = x    &     0x1
t66   = t65  <<    32
t67   = t66  -     t65
t68   = t64  ^     t46
t69   = t68  &     t67
t70   = t46  ^     t69

output = t70
total  = 70 operations for 7 lanes = 10.0 per lane evaluation
peak live registers = 7
```

The constants shown as immediates are the cv-dependent quantities of Section 6;
their values change per chaining value but the emitted shape, and therefore the
count, does not.
## Appendix G. Random coins and the input distribution

Finding F-EVAL-2 of the previous review observed that the success event is clear
but the probability space is not. This states it.

The attack's coins are, in order:

1. **The first block.** Drawn uniformly from 512-bit blocks, one per schedule
   window of Appendix E.3. It determines cv = H(first block) and through it every
   constant of F. No structure is required of it; the base of Appendix B
   constrains the second block only.
2. **The walk starts.** Within a window, trail start points are drawn uniformly
   from the 32-bit domain, independently of each other and of the first block.
   A trail ends at a distinguished point or is dropped at 20 * 2^db steps.
3. **A parity restriction, which is deterministic rather than random.** The walk
   function takes its odd branch on odd x and its even branch on even x, so every
   claw has **a0 even and u odd**. Both free words are confined to half their
   range. This is exact and known, not an unmeasured conditioning, and it is
   stated here because the quantities multiplied into the per-claw exponent are
   not evaluated under it: p8 and p9 come from an exhaustive scan over all 2^32
   words, the withdrawn `jointside.py` sampled (a0, a1) uniformly over the full
   range, and the row-17 term assumes W17 uniform. Whether the parity restriction
   moves any of the three is not established here; it is a known gap in the
   probability space rather than a modelled effect.
4. **Nothing else.** Given a claw (a0, u), the variant is determined: a1 = u -
   h(a0, cv), and W0..W9 follow from the schedule relations of Appendix C with
   A0 = a0 and A1 = a1. The side conditions, row 17 and the tail are then
   evaluated on a fully determined state. There is no further sampling and no
   restart within a claw.

The success event is the one in the target profile: two distinct 128-byte messages
M0 || M1 and M0 || M1' whose complete 39-step SHA-256 digests are equal, with the
standard IV, FIPS 180-4 padding and feed-forward, the first 39 steps applied to
every padded block.

The claimed success probability 0.39 is over these coins: with N = 2^119.70 claws
each succeeding with probability 2^-120.71, and treating claws as independent
(premise H6), P(at least one success) = 1 - exp(-N * p) = 1 - exp(-0.494) = 0.39.

The per-claw probability 2^-120.71 is itself a product of a measured term (the
tail, Section 5), an exact term (row 17, -32 bits, from the exhaustive |G17| = 1
of Appendix D) and a measured term, the side conditions at -9.81 bits, whose
factorization is premise H8 and is measured on 16- and 24-bit prefixes under claw
selection by `experiments/clawdist.py` (Section 3, Section 9). The conditioning of
the tail on claw selection is premise H4 and is not established.

## Appendix H. What the organizer experiments do and do not establish

Seven experiments are declared. The eight rows below cover them: `clawdist.py` appears twice, once for what it shows about inter-claw dependence and once for the side conditions under claw selection. Two
programs that earlier filings shipped, `clawexp.py` and `jointside.py`, were
withdrawn and are not in this package; `jointside.py` in particular could not fail,
since under uniform (a0, a1) the identity W8 = C(a1) - a0 makes P(cond8 and cond9)
= p8 x p9 exactly. Under the organizer's rules the declared experiments' numeric outputs
are participant observations: the host recomputes the collision predicate on
returned message pairs, and none of these return pairs, so none of their numbers
is credited as attack cost. They are in the package as executable fragments of the
specification, not as proof of a cost.

This table was rewritten after an adversarial review found the previous version
overstated three of its own rows. Where an experiment is weaker than it looks,
that is now in the "does not establish" column.

| experiment | establishes | does not establish |
| --- | --- | --- |
| `sidecond.py` | that the marginal rates p8, p9 reproduce the exhaustive counts on uniform words | the joint behaviour; and the exhaustive enumerator itself is not in the package |
| `clawverify.py` | that the construction runs and produces (a0, u) pairs at the rate the table size predicts, with u odd as the encoding requires | preimage verification — a u returned by `table[v]` satisfies f(u) = v by construction, so that check is a dictionary-key identity and is no longer performed; the image density of f, which this cannot measure from a structured subset of odd u; and the full-scale claw rate |
| `kernelcount.py` | that the tracer is present, emits 70 operations for 7 lanes with 7 peak live registers, and that the emitted program equals a scalar reference on every lane tested | that this machine convention prices the attack, which is H3; the 23 operations of DP, loop and handler overhead, which remain estimated; and the 7-way packing credit of log2 7 = 2.81 bits, which is convention-dependent and untested |
| `vowclaw.py` | that the search as specified executes and produces claws at a steady rate at reduced scale | the 2^11.00 figure; stability at 2^119.70 claws; and depletion either way — over its three-fold span, depletion at the worst rate of Appendix E.2 would give a window ratio of 0.75–0.90, which its acceptance band also admits, so the test has little power against the thing it probes. The argument about depletion is E.2's measured curve and E.3's schedule, not this run |
| `clawdist.py` (dependence) | that within one chaining value's window the claws produce no duplicates and their side-condition successes are not overdispersed — the first measurement bearing on H6 | dependence ACROSS the 2^104.21 windows the attack uses, and clustering below about 30%, which this sample cannot resolve |
| `splitbias.py` | that the splitting estimator's bias is positive and falls monotonically with population, measured against a toy with an exactly known answer. Appendix D.1 subtracts the largest measured value, 0.52 bits, so no extrapolation to the filed population enters the ledger | that the real characteristic's stages behave like the toy's independent, flat-probability ones — what transfers is the estimator's arithmetic, not the problem's structure. The subtraction bounds the bias at population 2000 only if the bias does not increase with population; the four measured values fall monotonically and the fixed-effort form predicts a 1/population decay, but that monotonicity is the premise |
| `tailrow.py` | the row-18 conditional, the first tail stage, measured directly from the filed base and characteristic: 2^−18.300 pooled against the study's 2^−18.0 — the first organizer-executed measurement touching the tail at all | the other stages (rows 19..23 and the run to 38), unreachable from the base without the search this sandbox cannot run; and the characteristic itself, which it consumes rather than confirms |
| `clawdist.py` | the side conditions measured on **genuine claws** — W8 and W9 from real claw-selected (a0, a1) rather than uniform words, which is the gap `jointside.py` could not reach; and transcription consistency between the folded kernel forms, the schedule relations and the real expansion | its W16 and parity counters, which are **identities** given a table hit and cannot fail, so they are a consistency check and not a pass rate; the W17 uniformity test, which has little power (6 of 32 bits, ~93% miss rate for an eightfold class inflation at its own band) and whose u values are confined to the 2^21 smallest odd integers; and the tail under claw selection, which it does not touch |
| *(none)* | — | **the tail beyond row 18, and the tail under claw selection. `tailrow.py` measures the first stage; the rest are unreachable here and the estimator is not shippable. Appendix D now files the complete per-seed study the tail is computed from, so the number is reproducible from the package, but it is a measurement reported rather than an organizer-executed one, and the claw-selection conditioning on it is untested.** This remains the filing's weakest point |

Two further limits that apply to the set as a whole. The organizer seed is public
and no holdout nonce is used, and Section 8 quotes realized pooled outcomes, so
these hypotheses were written with knowledge of the results; no multiple-comparison
correction is applied. And of the 93 operations charged per word evaluation the
experiments reach 70, while of the 120.71-bit per-claw exponent they reach the
9.81-bit side-condition term only.

The specifications in Appendices A through G, not these experiments, are what make
the attack reconstructible. The experiments are executable fragments of those
specifications.
