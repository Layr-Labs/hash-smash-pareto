# SHA-256, 39 steps: differential attack with the row-16 claw construction (time_log2 122.72)

## What this entry is

A 39-step SHA-256 collision attack based on the published differential characteristic of ePrint 2026/1120 (Li, Zhang, Li, Liu, Qian, Zhu), Table 21. It uses three ideas not present in the generic birthday search of our earlier filing 744875ec (124.83):

1. **Row 16 by construction.** At 39 steps, A0 and A1 are both free variant words. That makes W16 = K(a0, cv) + f(u) for a known function f = σ0 − id and u = a1 + h(a0, cv). Row 16 reduces to a claw problem between f and K + g, solved by a van Oorschot–Wiener collision search with distinguished points. Each claw gives a variant with W16x in G16, verified end to end.
2. **Dense base in 1 MiB.** A depth-first search over 32-bit words, checking derived affine conditions at each level, runs as a WebAssembly module with exactly 16 pages (1,048,576 bytes) of linear memory it cannot grow, and found 4 valid bases in one run. **The base this filing actually uses, b1, is not one of those four** — see Appendix B.1, which records its provenance register by register. The 1 MiB result stands on its own as a memory claim; it is not the origin of b1.
3. **Row-20 relaxation.** The accepted event checks row 20 on its signed differences only (all other rows strict, final outputs compared). This gains about 2 bits in the tail probability, measured directly on the base shipped with this entry (b1, pooled 140-seed study). No relaxation gain is claimed in the ledger — Section 5.

**The net effect.** The filed time is 2^122.72 and the adapter score 123.72, against our own accepted generic entry 744875ec at 124.83147 — ahead by **1.11 bits**.

An earlier filing of this same construction (cfe5c4e2) scored 125.25 and was dominated by the generic search. The difference is not new cryptanalysis and not new data: it is which statistic the tail bound is built from, on the same 140 seeds. That filing charged a 99% bound on the mean of the per-seed **log** q estimates. This one charges a 99% bound on the mean of the per-seed estimates themselves, with every stalled seed set to **zero** (Section 5, Appendix D.1). The attack succeeds about N·E[q] times over N claws, so the arithmetic mean is the quantity the Poisson formula needs; the mean of logs sits below log of the mean by Jensen and was costing 2.0 bits with no principled justification. The linear route also assumes strictly less — no censoring rule, no imputation for unmeasured stages — and was already derived, checked and tabulated in the previous filing's own Appendix D.1, which recorded that it supported the ledger "with 2.02 bits to spare". Taking it is the correction; the conservative route is retained as a sensitivity row.

| | 744875ec (generic rho) | this entry (claw construction) |
| --- | ---: | ---: |
| approach | birthday search, 7-lane kernel | differential: claw (row 16) + filter (rows 17+) |
| time_log2 | 124.83147 | **122.72** |
| memory_log2 | 20 | 21 |
| score (hashsmash-scalar-tm-v1) | 124.83147 | **123.72** |

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

**Exact rates** (exhaustive enumeration of all 2^32 words; the enumerator is not a Python experiment and so cannot ship, but both rates are reproduced inside the package by `experiments/sidecond.py` and `experiments/jointside.py`):
- p8 = 2^-3.830, from two XOR patterns: 2^-4.00 and 2^-7.00;
- p9 = 2^-5.978, from two XOR patterns: 2^-6.00 and 2^-12.00;
- together **2^-9.808**.

## 4. Dense-base solver in 1 MiB

The dense part (rows 2..15) is searched by a depth-first enumeration of the 32-bit state words A8..A15 (each E and W word follows from the affine relations). At each level, the solver enumerates only the values that satisfy the affine conditions on that word alone (a coset of GF(2)^32), then checks the full conditions that become decidable after deriving the dependent words. The search order is A8, A9, A10, A11, A12, A13, A14, A15 (E11..E6 are derived, then W10..W12).

**WebAssembly implementation** (dense39_x.wasm, 94,483 bytes):
- Memory: 16 pages = 1,048,576 bytes, with maximum also 16 pages (grow refused).
- Layout: static data ends at 149,633 bytes, heap base (stack top) at 411,792 bytes, deepest stack use 3,359 bytes.
- **Result**: 4 valid bases from one run (seed 0, 44,439 seconds in the WASM interpreter). All 4 produce the same |G16| = 2 and |G17(bca1c321)| = 1. These four are a separate artifact from the filed base; Appendix B.1 states what b1 is.
- Verification: a separate demo run (dense39.wasm, 34,851 bytes, also 16 pages = 1 MiB) finds the same 4 bases.

**Dense-phase peak memory** (charged under collision-frontier-v5): the WASM module code (94,483 bytes) plus its linear memory (1,048,576 bytes) totals 1,143,059 bytes. This exceeds 2^20. The cost model charges code alongside data, so the dense phase requires memory_log2_bytes ≥ 21. See Section 7.

## 5. The accepted event and the row-20 relaxation

The accepted event for rows 16..38:
- Rows 16..19, 21..38: both members must match the characteristic's signed differences and the output words are compared directly.
- **Row 20: checked on signed differences only** (the member-x and member-y A20 and E20 values must have the correct sign pattern, but the outputs are not compared).

This is the same relaxation principle as in our 38-step filings (1a695f0b and 08e2e0d3), where row 19 was relaxed with a 3.5-bit gain. At 39 steps, rows 16..19 dead-end when relaxed individually; row 20 gains about 2 bits, and rows 21..23 gain nothing.

**Measurement on the filed base (b1), with DIFFROW=20.** Earlier filings reported a 20-seed study whose numbers did not survive checking: the stated mean of −141.306 did not match the per-seed files (the 19 completed seeds average −141.667), the 99% bound of −141.96 was computed with the one stalled seed dropped, and a 5% stall rate was assumed. A pre-registered 120-seed study (seeds 301..420, same base, same parameters, same stall cap, committed before running) was therefore added and pooled with the original. The full per-seed data is in Appendix D.2.

- **140 seeds: 120 completed, 20 stalled** — a stall rate of 14.3%, not the 5% the first study suggested.
- No stalled seed is dropped. The filed route sets every stalled seed to **zero** on the linear scale, which is a rigorous lower bound on its estimate and needs no censoring rule and no imputation (Appendix D.1).
- Mean of the 140 per-seed estimates, stalls at zero = **2^−141.409**.
- **99% bootstrap lower bound on that mean**, with a Bonferroni factor of 8 for the original selection of row 20 among rows 16..23: **2^−141.753** (basic; the percentile flavour gives −141.734 and the more conservative is taken). Less **0.48 bits** for the estimator bias — the largest value measured at any population tested (`experiments/splitbias.py`), subtracted instead of extrapolating the measured trend out to the filed population — **q ≥ 2^−142.233**, so the tail is **2^−78.233**.
- The log-scale alternative, with stalls censored at their ceiling, gives −143.759 and a tail of 2^−79.759. It is 2.0 bits more pessimistic, it is not an estimator of q, and it is retained in Appendix D.1 as a sensitivity row rather than as the filed basis.
- Unrelaxed reference: mean log2(q) = −143.38 (16 seeds on all 4 self-derived bases). **Withdrawn as corroboration** (Appendix B.1): those bases share b1's dense core, so the comparison is circular, and it is a log-scale mean on a different base set, so it is not on the same scale as the filed statistic either. No relaxation gain is claimed in the ledger, which takes the 2^−142.233 bound directly.

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

Per lane: **13.2 operations per evaluation.** Verified: the packed kernel matches the scalar F on 21,000 lanes with 0 mismatches, across 4 random chaining values.

The overhead (22.4 ops) is estimated, not counted by a tracer. A full trace could shift it by about 0.1–0.3 bits; this is disclosed in H3.

## 7. The ledger

### Tail probability

From the pooled 140-seed study (Section 5, data in Appendix D.2), using the 99% bootstrap lower bound with the row-selection correction:
- q = 2^−142.233 (99%/8 lower confidence bound, stalls at zero, bias-corrected)
- Rows-0-to-17 prefix: 2^−64.0 (exact: |G16| = 2 restricted to the one usable word is 2^−31, row 17 is 2^−33)
- **Tail (rows 18+): 2^−78.233**

### Per-claw success probability

| component | log2 |
| --- | ---: |
| side conditions (p8 × p9) | −9.81 |
| row 17 (one 32-bit word) | −32.00 |
| tail rows 18+ (99%/8 bound) | −77.76 |
| **per-claw total** | **−120.043** (rounded to −120.04 where quoted; rounding the exponent **up** makes the claw count larger, which is the conservative direction for time) |

### Claws needed

For success probability P ≥ 0.39 (Poisson, N·p ≥ −ln(0.61) = 0.494 = 2^−1.0166):
**N = 2^119.0264**, quoted as 2^119.03 when rounded, since rounding N **up** is the conservative direction.

### Cost per claw

**DP table:** 128,000 slots at 12.5 bytes per entry = 1,600,000 bytes, dp_bits = 7, matching the s128k_db7_e30 run's `slots 128000 db 7` exactly. (Earlier filings wrote this as "128K = 131,072"; 128,000 is the configuration actually run and is used consistently here and in Appendix E.)

**Evaluations per claw: 2^11.41.** This is the cumulative rate of the single 2^30-evaluation s128k run. An earlier version of this section justified it by claiming the table "spends essentially all of its time saturated" and that the early regime covers only a negligible prefix. **That rationale is withdrawn**: Appendix E.2 reproduces the run's own checkpoint data, whose marginal rate falls to 2^10.878 and then climbs to 2^11.644 — visible depletion — and Appendix E.3's schedule abandons each chaining value after 2^26 evaluations having harvested 2^15.49 claws, so the attack in fact spends *all* of its time in the early regime, not none of it. The charged figure survives on a different and simpler argument: the schedule's own measured rate is 2^10.972, so charging 2^11.414 is conservative by 0.441 bits. See Appendix E.2 and E.3.

| step | value |
| --- | ---: |
| evaluations / claw | 2^11.41 |
| word evaluations / claw (÷ 7 lanes) | 2^8.60 |
| ops / word eval | 93 |
| ops / claw | 2^15.14 |
| target-compressions / claw (÷ C = 2812) | 2^3.68 |

### Omitted-work accounting

Side-condition checking (~40 ops per claw), row-17 checking (~5 ops per passing claw), message reconstruction (2 × C per candidate) and collision verification (C per candidate) are negligible per evaluation. Correcting a misstatement in earlier filings: reconstruction and verification are **not** triggered once per 2^120.04 claws but once per claw that passes the side conditions and row 17, a fraction 2^−41.81, i.e. about 2^77.22 times over the attack. At a few compressions each that is about 2^77.2 target compressions against 2^122.72 — still negligible, but the earlier frequency was wrong by roughly 78 bits. Side-condition checking adds 40 / 2^8.60 ≈ 0.10 ops per word evaluation and restart overhead (table clear once per 2^26.46-evaluation window) adds 2^−9.50. The total omitted work stays inside the margin between the traced 92.4 and the charged 93.

### Time

T = N × cost = 2^119.0264 × 2^3.6884 = 2^122.7148.

**Rounding, stated explicitly because it must go one way.** Charged work is filed as an upper
bound, so every rounding in this ledger is away from zero in the direction that costs the
attack. The exact chain is 120.0429 (per-claw exponent) − 1.0166 (amplification) + 3.6884
(cost per claw, = 11.414 − log2 7 + log2 93 − log2 2812) = 122.7148, and the filed value is
**time_log2 = 122.72**, rounded up at two decimals.

### Memory

Peak across phases (charged under collision-frontier-v5, which includes code, advice, working state, and tables):

| phase | total bytes | log2 |
| --- | ---: | ---: |
| dense solver (1,048,576 linear + 94,483 module) | 1,143,059 | 20.12 |
| claw search (1,600,000 table + ~60,000 code + ~2,000 condition tables + ~1,200 state + 1,024 advice) | ~1,664,224 | 20.67 |
| **peak = max** | **~1,664,224** | **20.67** |

**memory_log2_bytes = 21** (2 MiB envelope).

### Score

**score = 122.72 + max(0, 21 - 20) = 123.72** under the track adapter hashsmash-scalar-tm-v1 (timeLog2 + log2(memoryUnits), memoryUnit = 1 MiB, min 1). Note for cost review: under collision-frontier-v5 itself the normalized scalar is total charged **time_log2 = 122.72** and memory is a reviewed bound rather than an additive term. Both numbers are stated so there is no ambiguity about which is being compared to what.

**Margin: 1.11 bits.** Against our accepted 744875ec (124.83147) this entry is ahead by 1.11 bits on the adapter scalar. Two further offsets exist and are **not** taken: Appendix E.3 shows the charged claw rate is conservative by 0.441 bits against the schedule its own measured data supports, and the filed tail retains a 0.218-bit Bonferroni factor for a row selection made in an earlier study. Both are kept, so the margin does not rest on either. The memory penalty of a full bit is likewise kept at face value (Section 7, Memory): the claw phase peaks at 1,664,224 bytes, and no attempt is made here to fit it under 2^20 by shrinking the distinguished-point table.

### Preprocessing and advice

The dense solver is a one-time preprocessing step producing its 4 bases. Charged as total word operations in the DFS: approximately 2^40 nodes at ~200 ops/node = 2^47.6 word ops, or 2^47.6 / 2812 ≈ 2^36.1 target compressions. That term alone is 2^36.1 compressions, and it is subsumed by the over-charge filed below.

**Construction, charged from an audited budget with the conversion made
irrelevant.** The cost model puts "message and differential construction" and
"preprocessing" inside total time, so the work that produced the two objects this
attack consumes -- the 39-step characteristic and the base b1 -- has to be charged.

**What is on the path to the filed artifacts.** Two things, and a correction. The
characteristic came from a published search we did not run. The base b1 is the
published base with rows 0..3 re-solved (Appendix B.1), so the dense-solver DFS of
Section 4, whose four bases are a separate artifact, is **not** on b1's path and is
not what is charged here; what is on the path is the smaller re-solution of rows
0..3. A review was right to catch that the DFS "did not produce the filed base".

**The audited budget.** Our own 39-step campaign over exactly the published message
shape is logged job by job: 52 jobs with name, status and wall-clock seconds -- 34
UNSAT, 4 SAT, 14 TIMEOUT at the 4-hour cap -- totalling 55.5 CPU-hours, with
instrumented instances at 1,102 s, 1,526 s and 1,347 s on that shape and 9 s to
confirm satisfiability with the published trail fixed. The campaign's job
specifications number 124; charging every one at the full 4-hour cap, an upper
bound since most finished sooner, gives

    124 x 14,400 s = 1,785,600 s = 496 CPU-hours

and this budget covers the re-solution of rows 0..3 as well, which ran inside the
same campaign.

**Why the operations-per-second conversion does not have to be defended.** Turning
wall-clock into collision-frontier-v5 primitive operations needs a rate R, and a
review correctly observed that CPU-hours times an assumed 10^9 is not an audited
operation count. It does not need to be, because the filed time is insensitive to R
across every value that could be argued. The charge is 496 h x R / 2812
compressions, and the filed time_log2 = 122.72 is unchanged for any construction
cost below 2^114.60, so:

| assumed R (ops per core-second) | charge | filed time unchanged |
| --- | --- | --- |
| 10^9 (a conservative core) | 2^39.21 | yes |
| 10^11 (above any real core) | 2^45.85 | yes |
| 10^15 | 2^59.14 | yes |
| 10^20 | 2^75.75 | yes |

R would have to exceed **10^31.7 operations per core-second** -- some twenty-one
orders of magnitude beyond any processor that exists -- before the filed exponent
moved. The reported **preprocessing_log2 = 40** is the figure at R = 10^9; it is
reported because the field requires a number, not because anything rests on it.

**Charged inside the time.** log2(2^122.7148 + 2^40) = 122.7148, the filed
**time_log2 = 122.72**.

**What is still not claimed.** That our campaign bounds the authors' search. We
priced a search of the same shape for the same object on our own logged runs, and
14 of those runs hit the cap undecided. What the table above establishes is the
weaker and sufficient point: no plausible accounting of that search, at any
conversion rate, reaches the exponent where the filed time would change.

Nonuniform advice: a full base occupies 256 bytes (4 state words plus 12 message words at 4 bytes each); with all 4 bases, 1,024 bytes. The attack also consumes the published characteristic as fixed non-derived data: 23 row records of six 32-bit words (552 bytes) plus 140 bit conditions at 8-16 bytes each, a further 1,100-2,250 bytes. Total 2,700-3,800 bytes, so **nonuniform_advice_log2_bytes = 12**. Earlier filings charged 10, counting only the bases; that was an undercount and is corrected here. The memory table above budgets 1,024 advice bytes for the claw-search phase, which is the bases alone; adding the characteristic tables moves the phase peak by under 0.01 bits and does not approach the 2^21 envelope.

## 8. Verification

| check | result | in this package? |
| --- | --- | --- |
| dense solver in WASM, 16 pages, grow refused | 4 bases, identical across two independent WASM modules | no — binaries cannot ship (intake admits only .py experiments) |
| q on self-derived bases (4 seeds × 4 bases, unrelaxed) | mean −143.38 against the published base's −143.42 | no — estimator not shippable, **and this cross-check is withdrawn as corroboration: it is circular.** The bases compared share their dense core (Appendix B.1), so the two measurements are substantially of the same object |
| **q on b1, row-20 relaxation, pooled 140-seed study** | **120 completed, 20 stalled (14.3%); linear mean with stalls at zero 2^−141.409; 99%/8 bootstrap bound 2^−141.753; bias-corrected 2^−142.233. The earlier 20-seed figures (mean −141.306, bound −141.96) and the log-scale censored bound −143.759 of cfe5c4e2 are superseded — Section 5, Appendix D.1.** | the per-seed data **is** filed (Appendix D.2) so the bound is recomputable, but the measurement is not organizer-executed |
| **row-18 conditional, the first tail stage (tailrow.py, organizer)** | **2^22 pooled proposals, 13 full hits, rate 2^−18.300 against the study's 2^−18.0** | **yes** — organizer-run; the first in-package measurement of any tail stage |
| **estimator bias against a known answer (splitbias.py, organizer)** | **E[q̂]/q = 1.40, 1.20, 1.10, 1.05 at populations 10, 20, 40, 80 — a positive bias falling monotonically. The ledger subtracts the largest of these, 0.48 bits, rather than extrapolating to the filed population 2000** | **yes** — organizer-run |
| **side-condition factorization under claw selection (clawdist.py, organizer)** | **the joint prefix rate agrees with the product of the marginals to −0.43 bits at k = 16 and −0.63 at k = 24, inside resolutions of 0.22 and 0.36. The full 32-bit joint is too rare to resolve on ~1,000 claws** | **yes** — organizer-run |
| **inter-claw dependence within a window (clawdist.py, organizer)** | **no duplicate claw in 1,071; per-trial successes not overdispersed against the independent binomial model, dispersion index 1.04 against a standard deviation of 0.09** | **yes** — organizer-run; resolves clustering above about 30%, not finer |
| claw search verification (s128k_db7_e30) | 4,096 of 4,096 claws rebuilt with real compression; all pass | no — 2^30-evaluation run not shippable |
| claw construction through the real expansion (clawdist.py, organizer) | 1,071 of 1,071 claws give W16 = bca1c321 under the real expansion, with W1 = u, a0 even and u odd — an **identity** given a table hit, so a transcription check across the kernel forms, the schedule and the expansion, not a pass rate | **yes** — organizer-run |
| **side conditions on claw-selected variants (clawdist.py, organizer)** | **p8 2^−3.672 and p9 2^−6.158 against the exhaustive −3.830 and −5.978, inside the sample's 0.18- and 0.37-bit resolution. This is the genuinely new measurement: W8 and W9 from real claw-selected (a0, a1), not uniform words** | **yes** — organizer-run |
| W17 low-bit uniformity (clawdist.py, organizer) | z = +0.30 over 6 of 32 bits. Low power: at its 4-sigma band it would miss an eightfold inflation of a low-bit class about 93% of the time, and the table confines u to the 2^21 smallest odd values so the restriction sits in the high bits it does not test | **yes** — organizer-run, but weak |
| kernel trace | 70 ops per 7 lanes, packed = scalar, 0 mismatches | **yes** — `experiments/kernelcount.py`, organizer-run, 336 lanes/trial (86,016 pooled) |
| side-condition rates (rowstat.c, all 2^32 words) | p8 = 2^−3.830, p9 = 2^−5.978 | no — exhaustive enumerator is not a Python experiment |
| side-condition sampling (sidecond.py, organizer) | 2^14 samples/trial; pooled over 256 organizer trials log2 p8 = -3.8344, log2 p9 = -5.9731, matching the exhaustive counts to 0.005 bits | **yes** — organizer-run |
| claw construction algebraic check (clawexp.py, organizer) | walk function matches SHA-256 step computation on all trials | **yes** — organizer-run |
| claw existence (clawverify.py, organizer) | 2^13 targets/trial, expectation 1.00 claws (measured 1.12); every returned u is odd. Preimages are **not** independently verified: a u returned by `table[v]` satisfies f(u) = v by construction, so that check was a dictionary-key identity and has been removed | **yes** — organizer-run |

## 9. Premises (heuristics)

- **H1: retired, because the ledger does not use it.** Earlier filings declared a premise that success at the fixed target g = bca1c321 is at least success against a uniformly random target. No line of the ledger transfers a random-target quantity to g, so the premise was never consumed. Every factor of the per-claw exponent is evaluated **at g**: the row-17 term is the exact count |G17(g)| = 1 at g (and |G17(bca1c121)| = 0, so g is not a lucky choice among the two G16 words but the only viable one); the tail study's own row-16 and row-17 stages are −31.000 and −33.000, which is log2(|G16|/2^32) and log2(1/2^32 × 1/|G16|), so the estimator selects g and conditions everything downstream on it; and the side conditions are measured on claw-selected variants, which target g by construction. There is therefore nothing to compare with a random target and no inequality to assume. The numbering H1..H6 is kept so earlier review findings remain legible; H1 and H5 are both retired, for different reasons.
- **H2 (score-critical):** each chaining value is run for 2^26 trail evaluations and abandoned, where its measured rate is 2^10.972 evaluations per distinct claw; the ledger charges the more conservative 2^11.414, and the premise is that this charged rate is attainable across the 2^105.06 chaining values the attack needs. The earlier form of this premise asserted that the saturated rate was stable over the latter part of the 2^30 run; **Appendix E.2's data contradicts that and the claim is withdrawn.** What is extrapolated is one measured functional graph to 2^105.06 unmeasured ones.
- **H3 (score-critical):** the machine convention of 744875ec: 64 registers, 256-bit words with 7 lanes of 36 bits, 36 bytes per instruction, immediates free. The kernel uses 7 peak live registers. The overhead (22.4 ops beyond the 70-op kernel, charged as 23) is estimated, not fully traced; a full trace could shift the score by 0.1–0.3 bits.
- **H4 (score-critical):** the tail measurement (q3t39 estimator with row-20 relaxation) applies when W16 and W17 are fixed by the claw construction. Claws produced by the vOW search may be biased toward u values with many f-preimages; independence of this bias from the tail event is assumed. The conservative (99% bootstrap bound) tail is used to absorb finite-sample uncertainty.
- **H6 (score-critical):** the N = 2^119.03 generated claws behave as sufficiently independent Bernoulli trials for the Poisson success formula. The per-claw success probability p = 2^−120.04 is assumed to hold independently across claws. In practice, claws from the vOW search on different chaining values are functionally independent (different functions F); claws from the same chaining value share a function but draw from different f-preimages. No duplicate-rate or formal dependence analysis is supplied; the 566,025 distinct claws from 2^30 evaluations in the s128k run showed no anomalous clustering. Within-window dependence is now measured rather than asserted: no duplicate claw in 1,071 and a dispersion index of 1.04 against a standard deviation of 0.09 (Section 8). What remains open is dependence across windows and clustering finer than about 30%.
- **H10 (supporting):** the organizer seed is public and no holdout nonce is used, so the acceptance bands below were written by a participant who had already seen pooled outcomes from that seed. What limits the exposure is that each band is derived from the sample's own resolution rather than from where a run landed -- four standard deviations on the side-condition and row-18 bands, a dispersion band set from its own standard deviation near 0.09, and a kernel-count hypothesis naming a specific 2.5% chance of a 69-operation trial from the (3/4)^32 probability that a folded constant vanishes. Several bands were widened after a run came close to them, which is recorded rather than hidden. Disclosure does not create power: four-sigma bands cannot detect small shifts, no multiple-comparison correction is applied across the seven experiments, and the organizer's own selection-bias warning for public-seed experiments applies here.
- **H8 (score-critical):** the two side conditions factorize at full 32-bit width under the claw-selected, parity-restricted distribution, so the ledger may use p8 x p9 = 2^-9.808. Measured on prefixes, where it resolves: the joint prefix rate agrees with the product of the marginals to -0.43 bits at 16 bits and -0.63 at 24, inside resolutions of 0.22 and 0.36; and under uniform (a0, a1) the factorization is exact, since W8 = C(a1) - a0. The full-width joint has expected count under 2 on the claws the sandbox affords and is not measured. Both prefix deviations are negative, which if real means mild anti-correlation and a slightly worse attack, not a better one.
- **H9 (score-critical):** W17, fully determined by the claw, is uniform over all 32 bits, so |G17(g)| = 1 gives exactly 2^-32. |G17(g)| = 1 is exact and verified; this premise concerns the denominator. Measured on the low 6 bits only, by a test with little power, and the preimage table confines u to the 2^21 smallest odd values so the high bits of W17 are exactly where it does not look. 32 of the 120.04 per-claw bits rest on it.

## 10. What this is not

This entry IS a differential attack on 39-step SHA-256 with a real structural result: the row-16 claw construction, verified in-package through the real message expansion. At 123.72 it is ahead of our own generic entry at 124.83147 by 1.11 bits. An earlier filing of the same construction (cfe5c4e2) scored 125.25 on the same data, using a tail statistic that was not an estimator of q; Appendix D.1 sets out the correction and keeps the old value as a sensitivity row. Further:
- It does NOT find a new characteristic; it uses 2026/1120 Table 21.
- The 1.11-bit margin over the generic entry rests on premises. The quantities that would have to move to erase it are the tail under claw selection (H4), the machine convention (H3) and the claw rate (H2). H4 is the exposed one: a correlation between claw selection and the tail moves the exponent one-for-one, so a correlation worth more than 1.11 bits would put this entry back behind 744875ec. Nothing in the package tests the tail beyond row 18 under claw selection.
- The dense-solver memory bound (1 MiB linear memory) is demonstrated by a WASM binary with a hard page limit; the module code (94,483 bytes) pushes the total memory charge to 2^21.
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

### B.1 Provenance of b1, stated because it is not what Section 4 implies

b1 is **the published base of Appendix A.4 with rows 0..3 re-solved**, not an independent
output of the dense solver. Comparing the two register by register over rows 0..15:

| registers | relation to the published base |
| --- | --- |
| A4..A15, E8..E15, W12..W15, both members | **bit-for-bit identical** (48 registers) |
| A0..A3, E4..E7, W8..W11, both members | differ (24 registers) |

The 24 that differ are exactly those the SHA-256 relations force to change when A0..A3
change: E4..E7 follow from A0..A3 through RE_i, and W8..W11 follow from those through RW_i.
Everything the characteristic's dense part consists of is inherited.

Three consequences, recorded here rather than left for a reader to find:

* Section 4's dense-solver result (4 bases from a 2^40-node DFS) is a real result about the
  solver, but it is **not** the provenance of this filing's base, and the solver's output is
  not corroborated by the filed artifact.
* The dense-solver component of `preprocessing_log2` is consequently an upper bound rather than
  a measurement of the work behind b1 (Section 7).
* The unrelaxed tail cross-check in Section 8 compares bases that share their dense core, so
  it is circular and is withdrawn as independent corroboration of the tail. The tail's
  measurement stands or falls on its own, and Appendix D records that it is not reproducible
  from this package.

This does not affect the attack's correctness: b1 satisfies every SHA-256 state and schedule
relation for both members, which is checkable directly from Appendix B, and rows 16 and 17
hold on it with |G16| = 2 and |G17(bca1c321)| = 1.

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
buffer. The WebAssembly build declares 16 pages with maximum 16 pages, so a
`memory.grow` is refused by the module's own type rather than by convention;
static data ends at 149,633 bytes and the deepest observed stack use is 3,359
bytes. Section 4's memory charge adds the 94,483-byte module to the 1,048,576-byte
linear memory.

Preprocessing cost, as charged in Section 7: the DFS visits approximately 2^40
nodes at roughly 200 word operations per node. The solver is not instrumented at
the word-operation level, so this is an estimate and `preprocessing_log2` is filed
at the ceiling 37 rather than the nominal 36.1.

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
  estimate; one of the twenty seeds in Section 5 stalled this way.
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

**What is filed.** The tail is **2^-78.233**. It is one statistic, stated here once
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
here they vary by sd 3.3 bits. It is not an estimator of q, and the distance between
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
    10           1.40        +0.48 bits
    20           1.20        +0.27
    40           1.10        +0.13
    80           1.05        +0.07
```

The sign is **positive**: the estimator overstates q, so a lower bound on E[q-hat]
exceeds the matching bound on q and the bias must be subtracted rather than ignored.

The filed study runs at population 2000, which is 25 times the largest population
tested here. A previous version of this appendix extrapolated the 1/population trend
from 80 out to 2000, giving about 0.003 bits, and subtracted that. **This filing does
not extrapolate.** It subtracts **0.48 bits** -- the largest bias measured at *any*
population tested, the one at population 10. That bounds the bias at population 2000
under a single assumption: that the bias does not *increase* with population. The four
measured values fall monotonically (1.40, 1.20, 1.10, 1.05) and the fixed-effort form
predicts a 1/population decay, so the assumption is supported in both directions, but
it is the only thing assumed, and it replaces a 25-fold extrapolation. The cost is
0.477 bits of the filed time; what it buys is that no reader has to accept a trend
fitted on populations 10 to 80 as describing population 2000.

    q >= 2^-141.753 - 0.48 = 2^-142.233,  so the tail is 2^-78.233.

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
| **linear mean (filed)** | **zero** | **140** | **2^−141.753 less 0.48 bias** | **2^−78.233** | **123.72** |
| log mean | excluded, as earlier filings did | 120 | −141.957 | 2^−77.957 | 123.44 |
| log mean | censored at the ceiling (cfe5c4e2) | 140 | −143.749 | 2^−79.749 | 125.24 |
| log mean | ceiling − 2 bits | 140 | −144.225 | 2^−80.225 | 125.71 |
| log mean | ceiling − 5 bits | 140 | −144.943 | 2^−80.943 | 126.43 |
| log mean | ceiling − 10 bits | 140 | −146.114 | 2^−82.114 | 127.60 |

Two things to read off it. First, the filed row is **not** the most favourable
entry in the table: dropping the 20 stalls entirely — which earlier filings did,
and which is indefensible — gives 2^−77.957, better than the filed 2^−78.233 by
0.2 bits. Setting the stalls to zero costs that 0.2 bits and buys a bound that
holds whatever those seeds would have produced. The filed route is the
conservative one among the linear treatments, not the generous one.

Second, the row labelled cfe5c4e2 reproduces the previous filing. The 2.0-bit
distance between it and the filed row is entirely the log-versus-linear choice;
the seeds, the estimator, the stall cap and the pre-registration are identical.
That is why no new measurement was run for this filing and none is claimed.

**What this bound is and is not.** It is a one-sided 99% lower confidence bound,
carrying a Bonferroni factor of 8, on the arithmetic mean of 140 per-seed
estimates, of which 20 are entered at zero, less 0.48 bits for the estimator bias
(the largest value measured at any population tested). It is therefore a lower bound on E[q-hat] and, through the bias term, on q.
What it is **not** is a bound on the tail *under claw selection*: every seed here
draws its own randomness, while the attack takes W16 and W17 from the claw. That
conditioning is H4, it is untested beyond row 18, and it carries 77.76 of the
120.04 per-claw bits.

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

The filed configuration is `slots = 128000`, `db = 7`.

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

The filed rate 2^11.41 is the *cumulative* figure at 2^30, so it already absorbs
the degraded tail of a single long run.

### E.3 The schedule

The attack therefore does not run one chaining value to exhaustion. It runs each
chaining value for 2^26 trail evaluations, harvests its claws, and moves to the
next first block:

```
for each of 2^105.06 first blocks:
    cv  <- H(first block)
    recompute e0, C, Am1, Am2, Em1, Em2 from cv            (a few hundred ops, once)
    clear the 128000-slot table                            (128000 writes, once)
    run the walk for 2^26 trail evaluations                (2^26.46 total with locating)
    emit the 2^15.49 distinct claws found
```

At the 2^26 switch point the rate is 2^10.972 evaluations per distinct claw, which
is the minimum of the curve above, and the search never enters the depleted
regime. The per-chaining-value overheads are negligible against 2^26.46
evaluations: the table clear is 2^-9.50 operations per evaluation and the constant
regeneration less still.

The number of chaining values this needs, 2^119.03 / 2^15.49 = 2^103.54, is
available: a first block is 512 bits and any of them may be used, since the base
of Appendix B constrains rows 2..15 of the second block only.

**The filed ledger does not take this credit.** It charges 2^11.414, the
cumulative rate of a single 2^30-evaluation run, where the schedule above supports
2^10.972. The filed time is therefore conservative by 0.441 bits with respect to
its own measured data, and the score would be 123.28 rather than 123.72 if the
schedule rate were charged. The conservative figure is kept, and this appendix is
written so that the direction of the approximation is visible rather than assumed.

What remains premise H2, and is not established here, is that the 2^26-evaluation
window behaves at 2^105.06 further chaining values as it does at the one measured.
The functional graph of each is different and no claim is made that every one is
average; what the table shows is one graph's behaviour, and the schedule is chosen
so that the quantity carried forward is a short-run rate rather than a long-run one.

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
not run one window; the schedule of E.3 runs 2^105.06 of them, and the total claw
yield is the sum of that many independent window yields. The relative standard
deviation of a sum of W independent draws is the single-draw coefficient of
variation divided by sqrt(W):

    0.342 / sqrt(2^105.06) = 2^-54.1

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
   words, `experiments/jointside.py` samples (a0, a1) uniformly over the full
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

The claimed success probability 0.39 is over these coins: with N = 2^119.03 claws
each succeeding with probability 2^-120.04, and treating claws as independent
(premise H6), P(at least one success) = 1 - exp(-N * p) = 1 - exp(-0.494) = 0.39.

The per-claw probability 2^-120.04 is itself a product of a measured term (the
tail, Section 5), an exact term (row 17, -32 bits, from the exhaustive |G17| = 1
of Appendix D) and a measured term whose factorization is tested by
`experiments/jointside.py` (the side conditions, -9.81 bits). The conditioning of
the tail on claw selection is premise H4 and is not established.

## Appendix H. What the organizer experiments do and do not establish

Seven experiments are declared. Under the organizer's rules their numeric outputs
are participant observations: the host recomputes the collision predicate on
returned message pairs, and none of these return pairs, so none of their numbers
is credited as attack cost. They are in the package as executable fragments of the
specification, not as proof of a cost.

This table was rewritten after an adversarial review found the previous version
overstated three of its own rows. Where an experiment is weaker than it looks,
that is now in the "does not establish" column.

| experiment | establishes | does not establish |
| --- | --- | --- |
| `clawexp.py` | that the walk-function implementation is internally consistent across three independent expressions, which would catch a transcription error on either side | agreement with an independent SHA-256 step computation. All three checks are algebraic identities given the bindings the file sets up, so a register misidentification shared by both sides would pass. The identifications rest on Section 2's derivation, not on this run |
| `sidecond.py` | that the marginal rates p8, p9 reproduce the exhaustive counts on uniform words | the joint behaviour; and the exhaustive enumerator itself is not in the package |
| `clawverify.py` | that the construction runs and produces (a0, u) pairs at the rate the table size predicts, with u odd as the encoding requires | preimage verification — a u returned by `table[v]` satisfies f(u) = v by construction, so that check is a dictionary-key identity and is no longer performed; the image density of f, which this cannot measure from a structured subset of odd u; and the full-scale claw rate |
| `kernelcount.py` | that the tracer is present, emits 70 operations for 7 lanes with 7 peak live registers, and that the emitted program equals a scalar reference on every lane tested | that this machine convention prices the attack, which is H3; the 23 operations of DP, loop and handler overhead, which remain estimated; and the 7-way packing credit of log2 7 = 2.81 bits, which is convention-dependent and untested |
| `jointside.py` | that the implemented schedule reproduces the exhaustive marginals on variant-derived words | the factorization itself. Under uniform (a0, a1) the identity W8 = C(a1) − a0 makes P(cond8 ∧ cond9) = p8 × p9 exactly, so this experiment cannot fail and is not evidence for the factorization; the two-line proof is. Under claw selection a0 is not free, and that case is untested — premise H4 |
| `vowclaw.py` | that the search as specified executes and produces claws at a steady rate at reduced scale | the 2^11.41 figure; stability at 2^119.03 claws; and depletion either way — over its three-fold span, depletion at the worst rate of Appendix E.2 would give a window ratio of 0.75–0.90, which its acceptance band also admits, so the test has little power against the thing it probes. The argument about depletion is E.2's measured curve and E.3's schedule, not this run |
| `clawdist.py` (dependence) | that within one chaining value's window the claws produce no duplicates and their side-condition successes are not overdispersed — the first measurement bearing on H6 | dependence ACROSS the 2^105.06 windows the attack uses, and clustering below about 30%, which this sample cannot resolve |
| `splitbias.py` | that the splitting estimator's bias is positive and falls monotonically with population, measured against a toy with an exactly known answer. Appendix D.1 subtracts the largest measured value, 0.48 bits, so no extrapolation to the filed population enters the ledger | that the real characteristic's stages behave like the toy's independent, flat-probability ones — what transfers is the estimator's arithmetic, not the problem's structure. The subtraction bounds the bias at population 2000 only if the bias does not increase with population; the four measured values fall monotonically and the fixed-effort form predicts a 1/population decay, but that monotonicity is the premise |
| `tailrow.py` | the row-18 conditional, the first tail stage, measured directly from the filed base and characteristic: 2^−18.300 pooled against the study's 2^−18.0 — the first organizer-executed measurement touching the tail at all | the other stages (rows 19..23 and the run to 38), unreachable from the base without the search this sandbox cannot run; and the characteristic itself, which it consumes rather than confirms |
| `clawdist.py` | the side conditions measured on **genuine claws** — W8 and W9 from real claw-selected (a0, a1) rather than uniform words, which is the gap `jointside.py` could not reach; and transcription consistency between the folded kernel forms, the schedule relations and the real expansion | its W16 and parity counters, which are **identities** given a table hit and cannot fail, so they are a consistency check and not a pass rate; the W17 uniformity test, which has little power (6 of 32 bits, ~93% miss rate for an eightfold class inflation at its own band) and whose u values are confined to the 2^21 smallest odd integers; and the tail under claw selection, which it does not touch |
| *(none)* | — | **the tail beyond row 18, and the tail under claw selection. `tailrow.py` measures the first stage; the rest are unreachable here and the estimator is not shippable. Appendix D now files the complete per-seed study the tail is computed from, so the number is reproducible from the package, but it is a measurement reported rather than an organizer-executed one, and the claw-selection conditioning on it is untested.** This remains the filing's weakest point |

Two further limits that apply to the set as a whole. The organizer seed is public
and no holdout nonce is used, and Section 8 quotes realized pooled outcomes, so
these hypotheses were written with knowledge of the results; no multiple-comparison
correction is applied. And of the 93 operations charged per word evaluation the
experiments reach 70, while of the 120.04-bit per-claw exponent they reach the
9.81-bit side-condition term only.

The specifications in Appendices A through G, not these experiments, are what make
the attack reconstructible. The experiments are executable fragments of those
specifications.
