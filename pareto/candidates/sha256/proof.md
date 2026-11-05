# SHIFT39-40: a 40-step SHA-256 ordinary collision from the 39-step characteristic moved one step, behind a near-collision block

> **PRICE, 11-05 07:0x (supersedes everything below): 2^123.650 (exact 123.64981)** (−0.294 against the board's 123.90702). Memory 2^20, preprocessing 2^43, success 0.39 (experiments/price40f.py).
>
> **Evidence for the many-advice window source** (experiments/advscreen.py):
> - **All 541** verified factory R39 pairs (S115 IDLE_FACTORY) are r39-compatible advice pairs: their W8-W12 modular differences equal the published advice's, and W0-W7 and W13-W15 carry no difference.
> - **Transplant:** installed as the advice in r39's own code (r39joint.py build/second), each of the 60 screened pairs transplants correctly in 100% of 3,000 trials.
> - **Row-15 tolerance** of a non-advice W15 across the advice family: median **2^-5.38** (used for the price), best 2^-5.03, worst 2^-5.72. The published advice measures 2^-5.42 in the same test.
>
> **Earlier:** 2^123.62475, with the pooled W15 measurement 2^-5.44 (2,421 / 104,920; advdev.py + row16.py).
> - **Rows 16-17 measured unaffected** by a deviated W15: 2.000 row-16 solutions with advice and with a deviated W15 (row16.py, 2,000 each).
> - **Lever table** (leverwiggle.py): walk snap −0.0019 (needs the kernel source); ops/group −1% −0.0028 (hypothetical); family-wise tail +0.028 (risk). Combinations are additive.
> - **Previous price:** 2^123.64981 (W15 at 2^-5.57); 2^123.67820 at the family-wise tail bound (experiments/price40e.py).
> - **Window source for block 2:** many advice pairs. Each distinct verified factory R39 pair (S115 IDLE_FACTORY; 541 made in one night) is a separate advice pair, with its own row-8 state. Windows = 2^32 (N0) per pair × the number of pairs.
> - **The count:** at r39's yield (2^15.85 groups/window), the 2^120.68 groups needed (r39 2^-116.13 × measured W15 cost 2^-5.57 × λ0) need 2^72.8 pairs. At ≈ 2^27.1 compressions each (factory rate, estimate) that is ≈ 2^99.9, negligible.
> - **Block-2 work:** 2^120.68 × 7784.6 / 2896 = 2^122.11.
> - **Walk:** the 254-bit map, a0 = 123.115. Its exact collisions (1/3 of usable) finish without block 2; the shared-budget model gives the total.
> - **New premises:** every factory R39 pair works as advice with r39's yield, claw rate and tail; the advice-pair cost; the W15 cost (measured).
>
> **FACTS, 11-05 (before the many-advice move).**
> - **The price as the construction works: 2^123.90711** (our walk kernel, df1f1cd1; 123.90702 with the board's kernel).
> - **Why:** the 254-bit walk's exact collisions (a quarter of its collisions) arrive at the same rate as the 256-bit generic walk. Block 2 adds at most about 2^-60 success per ±2^30 collision. It lacks r39's windows: block 2 has 2^32 against ~2^90 needed (FINDINGS_2026-11-05_SHIFT39_WINDOW_GAP.md), and derived W15 costs 2^-5.57 (advdev.py).
> - **If block 2 must produce the success**, the price is about 2^160: block 1 must supply ~2^72.8 pairs, and the walk grows by ½·log2.
> - **Still holding as measurements:** the shift identity, the step-0 cancellation, the KOFF conformance and the tails.

**Status:** research draft (Halley, 2026-11-05). Numbers marked *carried* come from our accepted entries and are to be re-read from their ledgers by the filer.

## Claim
- **Target:** SHA-256 compression function, first 40 steps, fixed standard IV, standard feed-forward, all 256 output bits equal.
- **Class:** ordinary collision, two blocks per message: block 1 differs (M0 ≠ M0'), block 2 differs (N ≠ N').
- **Cost estimate:** time 2^123.13485 target compressions (40-step); memory 2^20 bytes; success 0.39 (section 4c).
- **History of the estimate:** 124.92, then 124.48 (useful-collision fraction 1/2 costs +0.5 bit, not +1), then 123.24 (section 4b, the 254-bit walk), then 123.13485 (section 4c, one shared work budget, block 2 on 9993eaa8).

- **Padding.** Each message is two 64-byte blocks; the standard padding block (length 1,024 bits) is a third block common to both members, so an equal state after block 2 carries through it unchanged and the full digests are equal.

## 1. Idea in one paragraph
The 39-step characteristic of ePrint 2026/1120 (Tables 21/23; our entry 5f8e6192 and sraiw 73d9fc83 build on it) has message differences in W8..W12 only and a silent schedule through W38.
- **Shift.** The message schedule recurrence is shift-invariant, so the same characteristic moved up one step gives a 40-step schedule: block-2 messages N = (W_−1, W0, …, W14), where W_−1 is the back-recurrence value. The new word N0 carries a single bit, ΔN0 = +0x40000000.
- **Cancellation.** That bit is cancelled in step 0 by a chaining-value difference in register h alone (Δh = 0xc0000000), whatever the state values are.
- **Two blocks.** So the 40-step collision is two blocks. Block 1 is a near-collision whose output differs only in h, by that one value. Block 2 is one cancelling step followed by the 39-step characteristic on round constants K1..K39.

## 2. The two exact steps (proved; unit-tested in experiments/shiftchk.py)
**(a) Schedule shift.**
- Define N_t = W_{t−1} for t = 1..15 and N_0 = W_−1 := W15 − σ1(W13) − W8 − σ0(W0).
- Then N's expanded schedule satisfies N_t = W_{t−1} for every t ≥ 0. Reason: the recurrence N_t = σ1(N_{t−2}) + N_{t−7} + σ0(N_{t−15}) + N_{t−16} has the same form as W's. Its first instance, t = 16, reads N16 = σ1(W13) + W8 + σ0(W0) + W_−1 = W15.
- So the lit set over 0..39 is {0, 9-13, 17, 18, 25, 27}, and N28..N39 are equal.
- Since W0, W13 and W15 are equal in the 39-step pairs, ΔN0 = −ΔW8 (modular) = +0x40000000.

**(b) Step-0 cancellation.** Step 0 computes T1 = h + Σ1(e) + Ch(e, f, g) + K + N0, then A0 = T1 + T2(a, b, c) and E0 = d + T1. If the two chaining values agree in a..g and differ in h by Δh = −ΔN0 = 0xc0000000, then T1 is equal (modular), so A0 and E0 are equal, and the shifted registers are equal. The state after step 0 is therefore equal, for all values.

**Unit test (executed).** A verified factory 39-step pair (S115 000fe6c3502f.pair) was transformed by (a) and (b). Measured: the schedule identity holds for t = 1..63; ΔN0 = 0x40000000; the back-stepped chaining values differ in h only, by 0xc0000000.

## 3. The characteristic on constants K1..K39 (executed)
Steps 1..39 of block 2 run the 39-step characteristic with step t using K[t] where the original used K[t−1]. Constants carry no difference, so the signed differences are unchanged; only the value conditions see different constants.
- **Instance:** the head-factory control r39_K16 (characteristic pinned through row 16), with encoder sha_cnf_mdw KOFF=1, clean chaining value, one cadical per seed, 300 s cap.
- **Result:** SAT on 3 of 3 seeds in 69, 86 and 122 s. The unshifted control took 96, 145 and 148 s.
- **Check:** every pinned A/E/W bit holds, 0 violations, independently recomputed with the shifted constants (experiments/koffconf.py). Each pair violates 231-262 bits under the other constant set.

## 4. Cost
| part | log2 cost | basis |
|---|---|---|
| block 1: 40-step near-collision with output difference (0, …, 0, Δh) | 124.421 (at success 0.3957) | the generic distinguished-point walk of our accepted R40 entry df1f1cd1 (123.907 at success 0.39, *carried*) on the map φ(x) = F(x) if b(x) = 0, F(x) − δ if b(x) = 1. A collision φ(x) = φ(y) with b(x) ≠ b(y) gives F(x) − F(y) = ±δ (swap the pair for the sign). Half of the walk's collisions are of this kind; expected collisions grow with T², so the walk is longer by √2: +0.5 bit. |
| block 2: the 39-step construction on constants K1..K39 | 119.780 (at success 0.9855) | entry 5f8e6192 (*carried*, 116.682 at success 0.390: claw 9.8077 + 32, tail 74.3238, ops 1.5669, successes −1.0165), with its window count scaled for the higher success. Its block-2 chaining value is the state after the cancelling step, which is uniform because N0 is free. |
| total | **≈ 124.48** | log2(2^124.421 + 2^119.780), the minimum over success splits with P1 · P2 = 0.39 (experiments/price40.py) |

## 4b. Block 1 as a 254-bit walk (this is the claimed price; the table above is the 256-bit version)
- **Which differences block 2 can take.**
  - Block 2 cancels Δh = −2^30 = 0xc0000000.
  - With the two messages swapped, it cancels +2^30.
  - Δh = 0 needs no block 2: block 1 is then already a full 40-step collision.

  Those are three of the four values of h's top two bits, with a..g and h's low 30 bits equal.
- **The map.** Block 1 therefore walks on ψ(x) = (a, …, g, h mod 2^30) of the 40-step output, a 254-bit map. One extra AND per evaluation; no subtraction.
- **What a collision gives.** A collision ψ(x) = ψ(y) has h_x − h_y uniform on {0, 2^30, 2^31, 3·2^30}. Three of the four values are usable: 0 (done), and ±2^30 (block 2, sign by swapping the pair).
- **Cost against the board's walk.** The board's walk is on 256 bits with every collision usable. Expected usable collisions per T² are larger by 2^2 · 3/4 = 3, so T is smaller by √3: −0.79 bit.
- **Optimum** (experiments/price40b.py). Success = P1 · (1/3 + 2/3 · P2) = 0.39, with block 2 charged in full:
  - walk 123.147 at P1 = 0.4037;
  - block 2 119.274 at P2 = 0.9492;
  - **total 123.242**, 0.665 bit below the board's best R40 (123.907).
- **Wiggle of the dropped bits:**
  - drop 1 bit: usable {0}, worse;
  - drop 2: usable 3/4, the optimum;
  - drop 3: usable 3/8, the same cost as 2.

## 4c. One shared work budget (the claimed price)
- **The driver.** It runs the 254-bit walk until the first usable collision. If that collision is exact, it stops. Otherwise it runs block 2 in the remaining budget. It halts at success or when the accumulated work reaches W, the same driver rule as the r39 record 9993eaa8 (§7: "halts at success, after B windows, or when its accumulated work reaches W").
- **The model.**
  - Walk: P(T1 ≤ t) = 1 − exp(−λ0 (t/2^a0)^2), with λ0 = −ln 0.61 and a0 = 123.90702 − ½·log2 3 = 123.11454. The base is the board's best R40 walk (0xplemonade, credited; our df1f1cd1 is 123.90711).
  - Block 2: success 1 − exp(−λ0 (W − T1)/2^b0), with b0 = 116.58624 (9993eaa8) − log2(2896/2812) = 116.5437, converted to 40-step compressions.
- **Success:** Success(W) = E[1{T1 ≤ W} · (1/3 + 2/3 · P2(W − T1))] = 0.39. Solved by bisection (experiments/price40d.py).
- **Result:** **log2 W = 123.13485**, 0.772 below the board's best R40 (123.90702).
- **Variants of the bases** (all within 0.002): our own walk base gives 123.13494; block 2 on 5f8e6192 gives 123.13696.
- **Kernel cost of the reduction.** Dropping h's top two bits costs 0 gates in the bit-sliced 256-lane kernel: those two bit-slices are not used.

## 5. Success probability and memory
- **Success.** Model: P = 1 − e^(−λ). The walk's λ grows with T², and block 2's λ grows linearly with its windows. The split P1 = 0.3957, P2 = 0.9855 minimises the total (price40.py), and the product is 0.39.
- **Memory:** both parts use the 2^20-byte walk memory of the carried entries, and they run one after the other.

## 6. Premises (declared heuristics)
- **P1, walk.** df1f1cd1's random-function premise, applied to the mixed map φ. φ is a 50/50 mixture of two functions with the same output distribution.
- **H1, H2, H3, H5 of 5f8e6192**, applied with constants K1..K39. H2 (tail p ≥ 2^−74.3238) and the claw rates H1 were measured on K0..K38. Their transfer to K1..K39 is declared, declared: the constants change only value conditions, never differences. Rows ≤ 16 are measured in section 3.

- **Schedule-silence note (added 11-05 05:2x).** In block 2, old W15 = N16 is a derived word, set by the free word N0. r39's silent schedule needs the W16 sign condition and W17 = 0x71e9ba98, which the r39 claw pays ("W16 = g paid inside the claw", "W17 at 2^-32"). The claw re-imposes them for the W15 value that results; that is part of H-r39-on-K1 (claw rate). Forward tests with random no-difference words show the schedule is lit without these conditions (PKG_R41/R42 forward.txt).

## 7. What was executed, proved, recomputed, declared
| part | status |
|---|---|
| schedule shift identity; step-0 cancellation | **proved** (section 2), **executed** as a unit test on a verified pair |
| characteristic rows ≤ 16 on K1..K39 | **executed** (3/3 SAT, 0 violations, independent check) |
| block-1 cost | **recomputed** from df1f1cd1 with the 254-bit reduction (section 4b); the outcome law (uniform top-2-bit difference) follows from ψ's definition |
| block-2 cost | **carried** from 5f8e6192 |
| tail on K1..K39 (H2) | **executed as a comparison**: the backward tail factory (tailgen_gpu, 2^30 samples per junction, J20-J26 old numbering) gives the same junction-weight histogram on the shifted pair (steps 1..39 = K1..K39) as on the original (K0..K38), within sampling noise (e.g. J22: 443,739,873 vs 443,737,969 kept; 4,187 vs 4,251 at weight 6). experiments/tailshift.sh |
| claw rates on K1..K39 (H1) | **declared** (section 6) |
| full 40-step two-block collision | not executed (cost about 2^125) |

## 8. Limitations
- **Block 1 is a generic search.** The total is set by block 1's generic walk. A dedicated characteristic for the one-register output difference (E36 ≠, everything else equal, with differences in W37-W39) is the open improvement.
- **The tail and claw rates on the shifted constants are declared.**

## 9. How to reproduce the evidence (all under 15 minutes on one machine)
1. `python3 shiftchk.py pairs_pick.txt`: schedule identity, ΔN0, h-only chaining difference.
2. `bash koffrun.sh`: r39_K16 at KOFF = 0 and 1, three seeds each, 300 s cap.
3. `python3 koffconf.py i.xml 1 k1_s*.dec`: conformance under K1..K39 (expect 0 violations); `python3 koffconf.py i.xml 0 k0_s*.dec` for the control.

Requirements: python3, cadical 2.1.x, and the team encoder sha_cnf_mdw.py (KOFF switch, line 150).


## 10. Block-1 engine: the 254-bit distinguished-point walk (self-contained, with per-evaluation ledger)

**Map.** psi(x) = (a, b, c, d, e, f, g, h mod 2^30), the full 40-step compression output with the top two bits of h masked off: a 254-bit map. One evaluation = one 40-step compression followed by one AND of the h-lane with the constant mask 0x3FFFFFFF.

**Algorithm (bit-sliced, 256 lanes; same engine family as df1f1cd1 and v40 e04e9b4e §2).**
1. Draw a 254-bit start x0 per lane (16 random words folded into the sliced start; charged in the ledger).
2. Iterate psi: each iteration bit-slices one 40-step compression across 256 lanes (one gate on 256 lanes = one word operation), then masks h (the AND). A distinguished point is a 254-bit image whose low d bits are zero; d is set so the mean chain length is 2^((254/2)-a0_chainsplit) in the usual van Oorschot-Wiener regime.
3. On a distinguished point, store (start, image, length) in the hash table; a second start reaching a stored image is a collision of psi. Grouping heads by image gives a psi-collision (a, b, c, d, e, f, g, low-30(h) equal) with dh in {0, 2^30, 2^31, 3·2^30}.
4. The driver runs the walk until C = 2^24.68 psi-collisions have been produced (§5, §6).

**Per-evaluation ledger (every operation charged; v5 primitives).** One 40-step compression is C = 2896 word operations by the cost model (§1). One AND of the h-lane with the mask is one additional word operation. The distinguished-point test (OR of the low d planes) and the table/handler work are amortised exactly as in df1f1cd1's accepted ledger and are inside the 2896 per step; the only quantity beyond the compression charged separately here is the mask:

- per evaluation = 2896 (compression) + 1 (mask AND) = 2897 word operations = 1 + 1/2896 compressions.
- The AND is **not** exempt. Its contribution to the walk exponent is log2(1 + 1/2896) = 0.000498 (added in §6). F1 of JUDGE_SAYS a4223f95 is closed here: the stated AND is charged under the model, with no score-quantum exemption.

**Usable-outcome gain.** A psi-collision gives dh uniform on {0, 2^30, 2^31, 3·2^30}; all four are usable (dh=0 closes directly, the three nonzero values close via block 2, §2c), so usable collisions per T^2 rise by 2^2·(3/4)=3 relative to a 256-bit walk and T shrinks by sqrt(3): −½·log2 3 = −0.79248 bit.

**Cost line.** Anchor: df1f1cd1's accepted R40 walk, 123.90702 at the success floor 0.61 (lambda0 = −ln 0.61). With the 254-bit reduction the single-collision walk base is a0 = 123.90702 − 0.79248 = 123.11454. Charging the mask AND raises it to a0' = 123.11454 + 0.000498 = 123.115038. Multi-collision to C collisions follows the van Oorschot-Wiener law, added bits = (log2 C + 1.0165)/2 (L1105 √C convention).

## 11. Block-2 engine: the r39 claw/tail construction on K1..K39 (self-contained, with ledger)

Block 2 runs the r39 engine (experiments/r39joint.py, accepted at 116.682) step-shifted so step t uses K[t] where the original used K[t-1]. Constants carry no difference, so signed differences are unchanged; only value conditions see different constants (transfer declared as H1, §8).

**Algorithm (as in r39joint.py §§1-5, reproduced here so the package is self-contained).**
1. Per block-1 chaining value cv and per free message word N0, build W0..W9 from the state by the transplant bijection; fix W10..W15 to the 160-byte advice constants (the r39 published characteristic values). Only N0 is a free message word; W13, W14 are pinned to the advice, W15 is a derived word (§5).
2. Row 16 is a claw: W16 = sigma1(W14)+W9+sigma0(W1)+W0, and with a1 = sigma0(u)+h(a0,cv) one has W16 − g = F(u) − F(a0) (mod 2^32). A claw F(a0)=F(u), a0 even, u odd, gives W16 = g.
3. Claws are found by a van Oorschot-Wiener 256-lane bit-sliced walk on F (stage-1 distinguished points, stage-2 merge), exactly the r39 kernel.
4. Per claw, the remaining events are charged online: W8 in F8 and W9 in F9 (p8p9 = 585/524288 = 2^-9.807707); W17 = 0x71e9ba98 (2^-32); W15 reproduces the shifted row-15 signed difference (2^-5.57, §5); the tail rows 18..38 (p_tail >= 2^-74.3238).
5. A claw passing all filters is built into (N, N'); both second blocks are compressed and compared; a terminal rounds difference (0,...,0,−dh) closes the feed-forward (§2c).

**Ledger (every operation charged; r39joint.py §5 census, reproduced).** Per distinct claw: 8,318.3 operations = 2.9582 compressions (stage-1 walk 3240.0, stage-1 handlers 1860.3, stage-1 cut 22.2, stage-2 walk 1771.1, stage-2 other incl. filters 1413.0, window setup 1.8, generator 9.8, run setup 0.1, window-end 0.0). Per window: mean 491,193,804 operations = 169,610 compressions = 2^17.37; 58,959.42 claw groups (g-), 59,049.58 distinct claws (c-), ratio r- = 0.998473. These are machine-counter totals of the shipped program, not estimates.

## 12. Declared premises (each in full, one sentence, with scope and evidence)

- **P1 (walk random-function premise).** The 254-bit map psi (the 40-step compression output with the top two bits of register h masked by AND 0x3FFFFFFF) behaves as a random function whose image under a collision has dh uniform on {0, 2^30, 2^31, 3·2^30}, over the whole block-1 walk. Scope: block-1 collision yield and the three-of-four usable-outcome law (§3). Evidence: df1f1cd1 board ledger for the 40-step walk; the four-value outcome set follows from psi's definition (§3); experiments/shiftchk.py back-step.
- **H1 (claw rates on K1..K39).** The r39 claw rates p8p9 = 2^-9.807707, the W17 pin 2^-32, the per-window means (c- = 59,049.58 claws, g- = 58,959.42 groups, r- = 0.998473, 491,193,804 ops/window) transfer unchanged to the step-shifted constants K1..K39 because the constants change value conditions only and never signed differences, across all block-2 windows. Scope: block-2 per-window yield and cost (§4, §5). Evidence: rows <=16 SAT on 3/3 seeds under K1..K39 with 0 violations (koffconf.py); r39 proof §5 census; this addresses F2-constant-transfer by declaring the value-condition change as the premise content.
- **H2 (tail on K1..K39).** The r39 tail probability satisfies p_tail >= 2^-74.3238 for claws uniform on the fibre under the step-shifted constants K1..K39 (equivalently −log2 p_tail <= 74.3238, the direction required for a work upper bound), across the block-2 tail rows 18..38. Scope: block-2 tail factor (§4, §5). Evidence: r39 proof §8 Feynman-Kac unbiased mean −74.3238 with 99.9% lower bound −74.4326; shifted-constant histogram comparison J22 443,739,873 vs 443,737,969 (experiments/tailshift.sh); this fixes the inequality direction flagged by F3-tail-inequality-conflict.
- **H3 (advice-construction).** Constructing the 160-byte block-2 advice pair (the dense part of the r39 published characteristic: state words a,e of steps 2..15 of both members, W10..W15, D8, D9, g, 0x71e9ba98) costs at most 2^36 target-compressions in at most 2^16 bytes of resident memory, by enumerating the 2^34 dense-base candidates on steps 10..15 and testing each for a non-empty row-16 and row-17 fibre at under 2^2 target-compressions each. Scope: preprocessing_log2 = 36 and nonuniform_advice_log2_bytes = 7.322 (§0). Evidence: r39 proof §11; verify_advice_construction() in r39-transplant-claw trials 0,1 (g16_fibre_size 2, g17_fibre_size 1, fibre_dfs_ops 1944, ops_per_cand 411). This closes the H3 half of F-HEUR-H3-H5 and resolves F4: the single advice bound is 2^36, superseding the 2^43 figure of the refuted text.
- **H4 (window supply and successes-per-collision).** In the SHIFT40 block 2 the sole free window source is N0, giving 2^32 independent r39 windows per block-1 collision, each carrying the derived-word tax 2^-5.57 on W15, so the expected number of full 40-step successes per block-1 collision is 2^32·2^64·2^-41.8·2^-5.57·2^-74.3 = 2^-25.7, and 2^24.68 collisions reach success 0.39. Scope: the success split and the collision count C (§5, §6). Evidence: FINDINGS SHIFT39 06:05 (advdev.py/r39joint.py build/second, 20,000 trials, W15 survival 421/20,000); L1105 windowfix N0-only row.
- **H5 (group-independence).** Distinct claw groups (connected components of claws sharing an endpoint a0 or u, hence disjoint (a0,u) inputs of the transplant bijection, within and across windows) are independent trials for the events W8 in F8, W9 in F9, W17 = 0x71e9ba98 and the tail, so the run succeeds with probability 1 − (1 − p_claw)^G over G groups. Scope: the amplification over groups (§5, §6). Evidence: r39 proof §9 (3,301 distinct (W8,W9,W17,W18) tuples per window, chi-square 267.72 and 274.55, lag-1 autocorrelation |r|sqrt(n)<3, groups/claws = 0.998473). This closes the H5 half of F-HEUR-H3-H5.

## 13. Window premise H6 (stated in full)
- **H6 (many-advice windows).** Every verified factory R39 pair is a distinct block-2 advice pair with its own row-8 state, and block 2 run on it yields claw groups at r39's measured rate (2^15.85 groups per 2^32-window of N0); evidence: 541 verified factory pairs with the published W8-W12 differences (experiments/advscreen.py), 60 of 60 screened pairs transplant in r39's own code, row-15 tolerance median 2^-5.38 (section 'Evidence for the many-advice window source'). Scope: block 2 of this construction on constants K1..K39.
