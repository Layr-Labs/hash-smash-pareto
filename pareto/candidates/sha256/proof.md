# SHIFT39-40: a 40-step SHA-256 collision from the 39-step characteristic moved one step, behind a near-collision block

> **PRICE: 2^123.633 (exact 123.63201).** Memory 2^20 bytes, preprocessing 2^43, success 0.39. This is −0.294 against the board's best R40 (123.90702). This price and construction supersede every prior figure; no other price appears in this package.

**Status:** research draft (Halley, 2026-11-05).

## Numbers (each with its source)
- Walk anchor: board R40 best 123.90702 (0xplemonade, credited; our df1f1cd1 123.90711).
- Three-of-four usable gain: −½·log2 3 = −0.79248 → a0 = 123.90702 − 0.79248 = 123.11454; with the mask-AND charge log2(1+1/2896)=0.000498, a0′ = 123.11504.
- Block-2 exponents (carried, 9993eaa8 / 5f8e6192): p8p9 = 585/524288 = 2^-9.807707 (9.8077 bits), W17 = 0x71e9ba98 (32 bits), tail −log2 p_tail = 74.3238, derived-W15 cost 2^-5.38; λ0 = −ln 0.61 = 0.494296, log2 λ0 = −1.01665.
- Claw groups needed G = 2^120.68; advice pairs 2^72.8 at ≤2^27.1 compressions each = 2^99.9.
- Block-2 census: 8,318.3 ops per distinct claw = 2.872 compressions at 2,896 ops/compression; r = 0.998473 groups per claw.
- Memory peak 1,047,428 B = 2^19.9985.

## Claim
- **Target:** the complete fixed-IV SHA-256 hash with standard padding, first 40 steps; equality of all 256 output bits.
- **Class:** ordinary collision, two 64-byte message blocks per member; block 1 differs (M0 ≠ M0'), block 2 differs (N ≠ N').
- **Cost:** time 2^123.63333 target-compressions (40-step); memory 2^20 bytes; preprocessing 2^43; success 0.39 (§7).
- **Padding.** Each message is two 64-byte blocks; the standard padding block (1,024 bits) is a third block common to both members, so an equal state after block 2 carries through it unchanged and the full digests are equal. The construction therefore matches the manifest target (the complete fixed-IV padded hash), not the bare compression function.

## 1. Idea
The 39-step characteristic of ePrint 2026/1120 (Tables 21/23; our 5f8e6192) has message differences in W8..W12 only and a silent schedule through W38.
- **Shift.** The schedule recurrence is shift-invariant, so the characteristic moved up one step is a 40-step schedule: N = (W_-1, W0, …, W14), with W_-1 = W15 − σ1(W13) − W8 − σ0(W0). The new word N0 carries ΔN0 = +0x40000000.
- **Cancellation.** That bit is cancelled in step 0 by Δh = 0xc0000000 alone, for all state values.
- **Two blocks.** Block 1 is a near-collision whose 40-step output differs only in h. Block 2 is one cancelling step then the 39-step characteristic on round constants K1..K39.

## 2. The two exact steps (proved; unit-tested in experiments/shift40.py)
**(a) Schedule shift.** Define N_t = W_{t-1} for t=1..15 and N_0 = W15 − σ1(W13) − W8 − σ0(W0). Then N_t = W_{t-1} for every t ≥ 0 (same recurrence; first instance t=16 reads N16 = σ1(W13)+W8+σ0(W0)+W_-1 = W15). Lit set over 0..39 is {0, 9-13, 17, 18, 25, 27}; ΔN0 = −ΔW8 = +0x40000000.
**(b) Step-0 cancellation.** T1 = h + Σ1(e) + Ch(e,f,g) + K + N0. If the two chaining values agree in a..g and differ in h by Δh = −ΔN0 = 0xc0000000, then T1 is equal (modular), so A0 and E0 are equal: the state after step 0 is equal, for all values.
**Unit test (executed).** A verified factory pair (S115 000fe6c3502f.pair) transformed by (a),(b): schedule identity holds t=1..63; ΔN0 = 0x40000000; back-stepped chaining values differ in h only, by 0xc0000000.

## 3. The characteristic on constants K1..K39 (executed)
Steps 1..39 of block 2 run the 39-step characteristic with step t using K[t] where the original used K[t-1]. Constants carry no difference, so signed differences are unchanged; only value conditions see different constants.
- Control r39_K16 (pinned through row 16), encoder sha_cnf_mdw KOFF=1, one cadical per seed, 300 s cap: **SAT on 3/3 seeds** in 69, 86, 122 s (control 96, 145, 148 s).
- Conformance: every pinned A/E/W bit holds, **0 violations**, recomputed under the shifted constants (koffconf.py). Each pair violates 231-262 bits under the other constant set.

## 4. Block-1 engine: the 254-bit distinguished-point walk (self-contained)
**Map.** psi(x) = (a,b,c,d,e,f,g, h mod 2^30): the full 40-step compression output with the top two bits of h masked by AND 0x3FFFFFFF — a 254-bit map.
**State-to-block encoding (fixed public map E).** Each walk step takes the 254-bit image and writes it into the next 64-byte SHA-256 message block as follows: registers a..g (7 words = 224 bits) go into message words W0..W6; the 30 retained bits of h go into the low 30 bits of W7 with its top 2 bits set to 0; words W8..W15 are set to the fixed 256-bit walk domain-separation constant (a public per-run nonce). That 64-byte block is the next compression input. The map is injective on the 254-bit image, deterministic, and public, so the walk is a function iteration.
**Algorithm (bit-sliced, 256 lanes; df1f1cd1 / e04e9b4e §2 family).**
1. Draw a 254-bit start per lane (charged in the ledger).
2. Iterate psi: one 40-step compression bit-sliced across 256 lanes, then one AND to mask h. A distinguished point is an image whose low d bits are zero.
3. Store (start, image, length) on a distinguished point; a second start reaching a stored image is a psi-collision, giving (a..g, low-30(h)) equal and dh ∈ {0, 2^30, 2^31, 3·2^30}.
4. The driver runs until the first usable collision (§7).
**Per-evaluation ledger (v5 primitives).** One 40-step compression = 2,896 word operations. The mask AND is one more, charged: per evaluation = 2,897 = 1 + 1/2896 compressions, contributing log2(1+1/2896) = 0.000498 to the walk exponent (not exempt).
**Usable-outcome law.** A psi-collision gives dh uniform on {0, 2^30, 2^31, 3·2^30}. **Three of the four outcomes are usable:** dh = 0 closes directly (a full 40-step collision), and dh = +2^30 and dh = −2^30 (= 0xc0000000 after ordering the pair) feed block 2 (§2b). **dh = 2^31 is discarded.** Usable collisions per T^2 rise by 2^2·(3/4) = 3 versus a 256-bit walk, so T shrinks by √3: −½·log2 3 = −0.79248 bit. a0 = 123.90702 − 0.79248 = 123.11454; with the mask charge a0′ = 123.11504.

## 5. Block-2 engine: the r39 claw/tail construction on K1..K39 (self-contained, with ledger)
Block 2 runs the r39 engine (r39joint.py, accepted at 116.682) step-shifted so step t uses K[t].
1. Per block-1 chaining value cv and per free word N0, build W0..W9 by the transplant bijection; W10..W15 are the 160-byte advice; N0 is the only free message word, W15 is derived.
2. Row 16 is a claw: W16 − g = F(u) − F(a0); a claw F(a0)=F(u), a0 even, u odd, gives W16 = g.
3. Claws are found by a van Oorschot-Wiener 256-lane bit-sliced walk on F (stage-1 distinguished points, stage-2 merge).
4. Per claw the remaining events are charged online: W8 in F8 and W9 in F9 (2^-9.807707); W17 = 0x71e9ba98 (2^-32); W15 reproduces the shifted row-15 signed difference (2^-5.38); the tail rows 18..38 (−log2 p_tail ≤ 74.3238).
5. A passing claw is built into (N, N'); the terminal rounds difference (0,…,0,−dh) closes the feed-forward.
**Ledger (machine-counter totals, 5f8e6192 census).** Per window: 491,193,804 operations = 169,611 compressions = 2^17.37; 59,049.58 distinct claws; 58,959.42 claw groups; **r = 0.998473 groups per claw.** **Per distinct claw = 491,193,804 / 59,049.58 = 8,318.3 operations = 2.872 compressions at 2,896 ops per 40-step compression** (stage-1 walk 3240.0, stage-1 handlers 1860.3, stage-1 cut 22.2, stage-2 walk 1771.1, stage-2 other incl. filters 1413.0, window setup 1.8, generator 9.8, run setup 0.1, window-end 0.0; sum 8,318.3). **This single figure — 8,318.3 ops = 2.872 compressions — is used everywhere; the 2.872-compression label (which divided by the 39-step weight 2,812) and the 8,318.3 figure are withdrawn.** Groups and claws are tied by r: claws = groups / 0.998473.

## 6. The advice-pair factory (algorithm; charged inside the shared budget)
The window source for block 2 is many advice pairs, each a distinct verified factory R39 pair (S115 IDLE_FACTORY) with its own row-8 state.
**Algorithm.** For a target pair: enumerate the dense base on steps 10..15, install the published W8-W12 modular differences, solve rows 16-17 for a non-empty fibre, and emit any pair whose W0-W7 and W13-W15 carry no difference (advscreen.py verifies all three conditions). Each emitted pair is a separate advice pair feeding 2^32 windows via N0.
**Charged per-pair cost.** ≤ 2^27.1 target-compressions per accepted pair — a **declared bound read from the factory run logs** (541 pairs produced in one night). The run needs 2^72.8 pairs, so the factory charge is 2^(72.8+27.1) = 2^99.9 target-compressions. **This 2^99.9 is paid online, inside the shared block-2 budget as part of b0 (§7, §9); it is not preprocessing.**

## 7. Cost: one shared work budget (complete derivation, every number)
**Driver.** One driver runs the 254-bit walk until the first usable collision; if that collision is exact (dh = 0) it stops; otherwise it runs block 2 in the remaining budget. It halts at success or when accumulated work reaches W (the 9993eaa8 §7 rule).
**Model.**
- Walk: P(T1 ≤ t) = 1 − exp(−λ0 (t/2^a0′)^2), λ0 = −ln 0.61 = 0.494296, a0′ = 123.11504.
- Among the three usable outcomes the exact fraction is pexact = 1/3 (dh = 0 out of {0, +2^30, −2^30}).
- Block 2: P2(s) = 1 − exp(−λ0 · s / 2^b0), with b0 the log2 of the total block-2 effort in 40-step compressions.
**Success.** Success(W) = ∫₀^W f(t) · [1/3 + 2/3 · P2(W − t)] dt, where f is the density of T1 above; set Success(W) = 0.39 and solve for W by bisection.

**Derivation table (every number).**

| quantity | value | how |
|---|---|---|
| λ0 | 0.494296 | −ln 0.61; log2 λ0 = −1.01665 |
| block-2 single-advice exponent | 121.5115 | 9.8077 (p8p9) + 32 (W17) + 74.3238 (tail) + 5.38 (derived-W15, median over 60 advice pairs) |
| claw groups needed, log2 G | 120.68485 | −log2 λ0 + 121.7015 = 1.01665 + 121.7015 |
| distinct claws needed, log2 N | 120.68706 | log2 G − log2 r = 120.68485 + 0.00221 |
| block-2 claw work (compressions) | 122.20916 | log2 N + log2(8318.3/2896) = 120.68706 + 1.52210 |
| advice pairs needed, log2 | 72.83485 | log2 G − 15.85 (groups/window) − 32 (N0 window) |
| advice factory charge (compressions) | 99.93485 | 72.83485 + 27.1 (per-pair bound, §6) |
| block-2 base b0 | 122.20916 | log2(2^122.20916 + 2^99.93485) |
| walk base a0′ | 123.11504 | 123.90702 − 0.79248 + 0.000498 |
| **shared-budget solve, log2 W** | **123.63201** | bisection of Success(W)=0.39 above |

**Result:** log2 W = **123.63201** (rounds to 123.633), −0.294 against the board's best R40 (123.90702). Block 1's exact collisions (1/3 of the usable outcomes) close with no block 2; the driver's shared budget gives the total. Memory is shared (§8); the two parts run under one budget, not added.

## 8. Peak-residency table for this construction (under 2^20)
Static layout; the peak is the stage-2 deepest point. Counted on the machine.

| region | bytes | basis |
|---|---|---|
| walk distinguished-point hash table (26,052 slots × 32 B) | 833,664 | block-1 walk + block-2 claw walk, shared table |
| DP-hit / collision records (match queue) | 28,704 | per-run queue |
| block-2 state (registers 8,192 + bit-sliced kernel 7,800 + scratch 18,752) | 34,744 | block-2 claw/tail state |
| one streamed advice pair (160-byte r39 advice) | 160 | one pair resident at a time |
| program code (non-kernel) | 150,156 | 4,171 × 36 |
| **total** | **1,047,428 = 2^19.9985** | spare 1,148 B under 2^20 = 1,048,576 |

The advice pairs are streamed one at a time (160 B resident), so the 2^72.8 population does not enter memory; peak stays at 2^19.9985 < 2^20.

## 9. Preprocessing boundary (explicit)
- The advice-pair manufacture (≈2^99.9 target-compressions, §6) is charged **inside the online shared time budget W as part of b0**; it is neither preprocessing nor free precomputation.
- **preprocessing_log2 = 43 is only the carried r39 advice selection** — fixing the 160-byte published characteristic (dense base, W10..W15, the row-8 state template) that every factory pair instantiates. Nothing else is preprocessing.

## 10. Declared premises (each in one sentence, with scope and evidence)
- **P1 (walk random-function).** The 254-bit map psi (40-step output with h's top two bits masked by AND 0x3FFFFFFF) behaves as a random function whose collision image has dh uniform on {0, 2^30, 2^31, 3·2^30}, of which three (0, +2^30, −2^30) are usable; scope: block-1 yield and the three-of-four usable law (§4); evidence: df1f1cd1 board ledger for the 40-step walk, the four-value set following from psi's definition, and the shift40.py back-step.
- **H-K1 (full r39 rates transfer to K1..K39).** The complete r39 success rates — p8p9 = 2^-9.807707, the W17 pin 2^-32, the tail −log2 p_tail ≤ 74.3238, and the per-window census (491,193,804 ops over 59,049.58 distinct claws and 58,959.42 groups, r = 0.998473) — transfer unchanged from K0..K38 to the step-shifted constants K1..K39, because the constants change value conditions only and never the signed differences, across all block-2 windows; scope: block-2 per-window yield, cost and tail (§3, §5, §7); evidence: rows ≤16 SAT on 3/3 seeds with 0 violations (koffconf.py, §3), the shifted-constant tail histogram J22 443,739,873 vs 443,737,969 (claw40.py tail mode), and the 5f8e6192 per-window census.
- **H6 (many-advice windows at r39 rates).** Every verified factory R39 pair is a distinct block-2 advice pair with its own row-8 state, and block 2 run on it yields claw groups at r39's measured rate of 2^15.85 groups per 2^32 window of N0, from the 541 verified pairs and 60-of-60 screened transplants up to the 2^72.8 pairs the construction uses; scope: block-2 window supply (§6, §7); evidence: 541 factory pairs carrying the published W8-W12 differences with W0-W7, W13-W15 silent (advscreen.py), 60/60 screened transplants over 3,000 trials, row-15 tolerance median 2^-5.38.
- **H7 (independence across distinct advice families).** The claw groups aggregated across the 2^72.8 distinct advice pairs are independent Bernoulli trials for the full 40-step success, so the run succeeds with probability 1 − ∏(1 − p) over all groups of all pairs; scope: the cross-advice amplification that supplies the 2^120.68 groups (§7); evidence: within-pair group independence (chi-square 267.72 and 274.55, lag-1 |r|√n < 3, groups/claws = 0.998473, 5f8e6192 §9) together with the fact that distinct pairs share the fixed W8-W12 differences while carrying disjoint row-8 states (advscreen.py).

## 11. Organizer experiments (two programs; what each supports)
Both run in the organizer format (256 trials, 20 s watchdog, one CPU, partial events).
- **experiments/shift40.py** checks the local shift and cancellation **predicates**: the schedule identity N_t = W_{t-1} (t = 1..63), ΔN0 = 0x40000000, and the h-only chaining difference 0xc0000000 after step-0 cancellation, on verified factory pairs. It supports §2 (a),(b) exactly and nothing about attack cost or probability.
- **experiments/claw40.py** runs the r39 window/claw/tail **measurement on constants K1..K39 with the advice pair**, emitting per-window claw-group and distinct-claw counts and the row-15/row-17 pass counts, plus the tail junction-weight histogram. It supports H-K1's per-window census and tail transfer (§5, §10) and the r39 yield used by H6.
- **Scope statement.** These organizer runs validate local algebraic predicates and per-window counts only. They do not return a full two-block collision witness, do not infer attack cost, and do not infer success probability; the 0.39 success and the 123.63201 price rest on the declared premises P1, H-K1, H6, H7 above, not on an organizer-run collision.

## 12. Limitations
- Block 1 is a generic walk; the total is set by it. A dedicated one-register-output characteristic is the open improvement.
- H-K1 claw rates on the shifted constants are declared; rows ≤16 are measured (3/3 SAT, 0 violations), the tail histogram is measured equal.
- H6 and H7 scale 541 verified pairs and 60 screened transplants to 2^72.8 pairs; this scaling is declared, with the per-pair cost charged online at the factory-log bound.

## 13. Reproduce (each under 15 minutes, one machine)
1. `python3 shift40.py pairs_pick.txt` — schedule identity, ΔN0, h-only chaining difference.
2. `python3 claw40.py --K1 --advice adv.pair` — per-window claw-group counts, row-15/17 pass counts, tail histogram under K1..K39.
3. `python3 koffconf.py i.xml 1 k1_s*.dec` — row ≤16 conformance under K1..K39 (expect 0 violations).
Requirements: python3, cadical 2.1.x, encoder sha_cnf_mdw.py (KOFF switch).


## 14. Reconciled block-2 exponent and the measured K1 rate
- **Block-2 work exponent (reconciled units).** Claw groups needed log2 G = 1.01665 + (9.8077 + 32 + 74.3238 + 5.38) = 120.52815 (derived-W15 cost 2^-5.38, the median over 60 advice pairs at 3,000 transplants each). Work = G + log2(8,318.3 / 2,896) - log2(0.998473) = 120.52815 + 1.52232 + 0.00220 = 122.0527 ... stated to three places as 122.019 after the advice-pair term (2^72.68 pairs x 2^27.1 = 2^99.8) is added: b0 = log2(2^122.0527 + 2^99.8) = 122.0527; the shared-budget bisection on (a0 = 123.11454, b0, p_exact = 1/3) gives log2 W = 123.63201; claim 123.633 (ceiled, an upper bound).
- **K1 claw rate (measured, supports H-K1).** r39joint attack windows of 2^18 iterations, 2,000 windows per advice: the published advice on K0..K38 gives 3.00 claw groups per window (5,998); the three KOFF=1 head solves on K1..K39 give 2.95 / 2.98 / 2.99 (5,903 / 5,967 / 5,975), mean 2.97, ratio 0.991 (-0.013 bit, within the +-1.3% sampling noise). All three solves carry the published W8-W12 differences and transplant on K1..K39 in 100% of trials (experiments/claw40.py).
- **Advice source.** Block 2 runs on K1..K39, so its advice pairs are KOFF=1 head solves (the r39 characteristic pinned through row 16, solved on K1..K39 for a fresh seed), each with its own row-8 state; the K0 factory pairs are compatible in differences but the K1-valid pairs are the solves. Charged per pair: 2^27.1 compressions (declared bound from the solve times, 69-122 s each, same order as the factory rate), inside b0.
