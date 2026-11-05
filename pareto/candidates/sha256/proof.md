# SHIFT39-41: a counted-and-carried cost for a 41-step SHA-256 ordinary collision from the shifted 39-step characteristic

Score (collision-frontier-v5): time_log2 = 121.505 target-compressions (exact 121.50474, rounded up). Memory is reported separately: 2^20 bytes by construction (peak 1,047,428 B; term max(0, log2 - 20) = 0).

## 1. Target and claim
- Target: two distinct messages under the standard IV, the first 41 steps, standard padding and feed-forward, all 256 output bits equal. Ordinary collision, two 64-byte data blocks per message: block 1 differs (M0 != M0'), block 2 differs (N != N'); the common padding block preserves the collision (equal inputs give the equal padding block, so a first-data-block collision is a full-message collision).
- Prices: one 41-step target compression is one unit; every other primitive word operation (add, sub, xor, and, or, not, shift, rotate, compare, random word, table index) costs 1/C.
- Cost: time_log2 = 121.505; memory 2^20 bytes (term 0); success >= 0.39.
- Shape: block 1 is a near-collision whose 41-step output lies in the set the shift cancels (a difference in g and h only); block 2 is two cancelling steps followed by the 39-step characteristic on round constants K2..K40. This is 2.41857 bit below the board-best R41 (cda94445, 123.92331).

## 2. The two exact steps (construction; unit test experiments/r41_shift.py)
**(a) Schedule shift (identity).** Define N_t = W_{t-2} for t = 2..15 and the two back-recurrence words N_1 = W_{-1}, N_0 = W_{-2} from W_{-i} = W15 - sigma1(W13) - W8 - sigma0(W0) iterated twice. Then the expanded schedule satisfies N_t = W_{t-2} for every t >= 0: the recurrence N_t = sigma1(N_{t-2}) + N_{t-7} + sigma0(N_{t-15}) + N_{t-16} has the same form as W's. The lit set over steps 0..40 is {0, 1, 10-14, 18, 19, 26, 28}; N29..N40 carry no difference. The new words carry dN1 = +2^30 and dN0 = -(sigma1(W12') - sigma1(W12)) - (sigma0(N1 + 2^30) - sigma0(N1)).

**(b) Step-0/1 cancellation (identity).** Over the first two steps the two new word differences are absorbed by a chaining-value difference in registers g and h alone: with the two block-1 chaining values equal in a..f, dg = -dN1 = 0xc0000000 and dh = -dN0 - dCh, dCh = Ch(e, f, g + dg) - Ch(e, f, g), the state after steps 0 and 1 is equal for all state values.

**Unit test (executed).** A verified factory 39-step pair (S115 000fe6c3502f.pair) moved up two steps: the schedule identity holds for t = 2..63; dN1 = 0x40000000; and over 100,000 random block-1 chaining values the state after steps 0-1 is equal in 100,000 of 100,000 (experiments/r41_shift.py; shift2chk.py).

## 3. Block 1: a 235-bit distinguished-point walk on the accepted df1f1cd1 engine
Block 1 is the 256-lane bit-sliced distinguished-point engine of our accepted R40 entry df1f1cd1, anchored at the board-best R41 generic walk cda94445 (123.92331). Block 2's free word N1 selects which single-bit sigma0 sign pattern it carries, so the set of cancellable dN0 is S with |S| = 64 distinct values, all equal mod 2^13 (experiments/r41_shift.py). The walk therefore need not resolve the bits that S spans.
- **Map.** Block 1 walks on the 41-step output with g's top 2 bits and h's top 19 bits dropped, a 235-bit map: one AND per evaluation, no subtraction.
- **Usable outcomes.** With the half-useful offset map (F(x) or F(x) - r on h, r the common low residue 0xbfc) a cross-bit collision carries the residue, so the usable-outcome count is U = 0.5*|S| + 0.5 = 32.5; the walk reduction is -0.5*log2(32.5) = -2.511184 bit.
- **Cost line.** Reduced walk base a0 = 123.92331 - 0.5*log2(32.5) = 121.412126 at the success floor 0.61 (lambda0 = -ln 0.61). The one AND for the mask is below the board claim quantum (10^-3, HashSmash.md:697).

## 4. Block 2: the 39-step construction on constants K2..K40
Steps 2..40 of block 2 run the 39-step characteristic with step t using K[t] where the original used K[t-2]. Constants carry no difference, so the signed differences are unchanged; only value conditions see different constants. Block 2's input chaining value is the state after the two cancelling steps, uniform because N0, N1 are free.
- **Rows <= 16 executed.** The head-factory control r39_K16 with encoder sha_cnf_mdw (KOFF = 2), clean chaining value, one cadical per seed, 300 s cap: SAT on 3 of 3 seeds. Every pinned A/E/W bit holds, 0 violations, independently recomputed with the shifted constants (koffconf.py); each pair violates 231-262 bits under the other constant set.
- **Carried ledger terms (5f8e6192 decomposition).** -log2 lambda0 = -1.0165; claw -log2(p8 p9) = +9.8077; W17 pin +32.0000; tail +74.3238; groups/claw r = 0.998473 -> +0.0022; ops/claw +1.5647; leader tightening -0.0609. The carried board base is the best accepted r39 (9993eaa8), 116.58624. The free word N1 selecting dN0 in S adds no condition.
- **Tail transfer, measured by the shifted-constant comparison.** tailgen_gpu over 2^30 samples per junction gives the same junction-weight histogram on the shifted pair (steps 2..40 = K2..K40) as on the original (K0..K38) within sampling noise: J22 443,739,873 vs 443,737,969 kept, 4,187 vs 4,251 at weight 6 (tailshift.sh).
- **Cost line.** Converted to 41-step compressions, b0 = 116.58624 - log2(2968/2812) = 116.508346.

## 5. Shared work budget and success split (experiments/r41_shift.py)
- **Driver.** One driver runs the 235-bit walk until the first usable collision; if the collision is already a full 41-step collision it stops, else it runs block 2 in the remaining budget, halting at success or when the accumulated work reaches W (the r39 record driver rule).
- **Model.** Walk: P(T1 <= t) = 1 - exp(-lambda0 (t/2^a0)^2), lambda0 = -ln 0.61, a0 = 121.412126. Block 2: 1 - exp(-lambda0 (W - T1)/2^b0), b0 = 116.508346.
- **Success.** Success(W) = E[1{T1 <= W} (pexact + (1 - pexact) P2(W - T1))] = 0.39, pexact = 0.5/U = 0.0153846 being the fraction of usable collisions that are already full 41-step collisions; solved by bisection.
- **Result.** log2 W = 121.50474, 2.41857 below the board-best R41 (123.92331). Cross-checks: block 2 in 39-step units gives 121.50967; the bare walk base is 121.412126 (all within 0.1).

## 6. Memory
Both blocks run one after the other on the same 2^20-byte distinguished-point arena (peak 1,047,428 B < 1,048,576), so the memory term is max(0, 19.998 - 20) = 0. Dropping g's top 2 and h's top 19 bits uses zero extra arena: those bit-slices are not referenced. Block-2 advice preprocessing (2^36) adds nothing to time.

## 7. Declared premises
- **P1 (walk random-function premise).** df1f1cd1's accepted random-function premise, applied to the 235-bit map (the 41-step output with g's top 2 and h's top 19 bits dropped) with the same output distribution; the usable-outcome count U = 32.5 follows from the map and the set S. Evidence: df1f1cd1 board ledger; section 3.
- **H1 (claw rates on K2..K40).** The 5f8e6192 claw rates and the W17 pin transfer to constants K2..K40 because the constants change value conditions only, never differences; rows <= 16 executed in section 4. Evidence: section 4 (3/3 SAT, 0 violations); 5f8e6192 proof s2.4, s5.
- **H2 (tail on K2..K40).** The 5f8e6192 tail (-log2 p >= 74.3238), transfer to K2..K40 supported by the shifted-constant histogram comparison (section 4, J22 443,739,873 vs 443,737,969). Evidence: 5f8e6192 proof s8; section 4.

## 8. Organizer-format experiment
The shipped program experiments/r41_shift.py runs 256 trials, one CPU, standard library only, deterministic from each per-trial seed, every loop bounded by a constant (HEURISTIC_EXPERIMENTS.md format). Per trial it emits the two shifted block-2 messages and numeric observations:
- schedule_identity_ok = 1 and lit_word_count = 11 for the embedded verified pair, with dN0, dN1;
- cancel_ok = cancel_total = 2,000: the two-step cancellation equalises the state after steps 0-1 for every seed-drawn block-1 chaining value;
- S_size = 64, S_equal_mod_bits = 13, usable_U = 32.5: the free-word set S;
- walk_cost_log2 = 121.412126, block2_b0_log2 = 116.508346, total_log2 = 121.504737: the shared-budget bisection.
The organizer's byte-identical rerun recomputes these checks from its own seeds.
