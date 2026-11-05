# SHIFT39-40: a counted-and-carried cost for a 40-step SHA-256 ordinary collision from the shifted 39-step characteristic

Score (collision-frontier-v5): time_log2 = 123.135 (exact 123.13485) target-compressions. Memory is reported separately: 2^20 bytes by construction (peak 1,047,428 B; term max(0, log2 - 20) = 0).

## 1. Target and claim
- Target: two distinct messages under the standard IV, the first 40 steps, standard padding and feed-forward, all 256 output bits equal. Ordinary collision, two 64-byte data blocks per message: block 1 differs (M0 != M0'), block 2 differs (N != N'); the common padding block preserves the collision.
- Prices: one 40-step target compression is one unit; every other primitive word operation (add, sub, xor, and, or, not, shift, rotate, compare, random word, table index) costs 1/C.
- Cost: time_log2 = 123.135 (exact 123.13485); memory 2^20 bytes (term 0); success >= 0.39.
- Shape: block 1 is a near-collision whose 40-step output differs only in register h, by 0xc0000000 or 0; block 2 is one cancelling step followed by the 39-step characteristic on round constants K1..K39. This is 0.77217 bit below the accepted board-best R40 (df1f1cd1, 123.90702).

## 2. The two exact steps (construction; unit test experiments/shiftchk.py)
**(a) Schedule shift (identity).** Define N_t = W_{t-1} for t = 1..15 and N_0 = W_{-1} := W15 - sigma1(W13) - W8 - sigma0(W0). Then the expanded schedule satisfies N_t = W_{t-1} for every t >= 0: the recurrence N_t = sigma1(N_{t-2}) + N_{t-7} + sigma0(N_{t-15}) + N_{t-16} has the same form as W's, and its first instance t = 16 reads N16 = sigma1(W13) + W8 + sigma0(W0) + W_{-1} = W15. The lit set over steps 0..39 is {0, 9-13, 17, 18, 25, 27}; N28..N39 carry no difference. Since W0, W13, W15 are equal in the 39-step pairs, dN0 = -dW8 (modular) = +0x40000000 = +2^30.

**(b) Step-0 cancellation (identity).** Step 0 computes T1 = h + Sigma1(e) + Ch(e,f,g) + K + N0, A0 = T1 + T2(a,b,c), E0 = d + T1. If the two chaining values agree in a..g and differ in h by dh = -dN0 = 0xc0000000, then T1 is equal (modular), so A0 and E0 are equal and the state after step 0 is equal, for all state values.

**Unit test (executed).** A verified factory 39-step pair (S115 000fe6c3502f.pair) was transformed by (a) and (b): the schedule identity holds for t = 1..63; dN0 = 0x40000000; the back-stepped chaining values differ in h only, by 0xc0000000.

## 3. Block 1: a 254-bit distinguished-point walk on the accepted df1f1cd1 engine
Block 1 is the 256-lane bit-sliced distinguished-point engine of our accepted R40 entry df1f1cd1, with the full 40-step compression as the walk map. Block 2 can cancel dh in {+2^30, -2^30} (sign chosen by swapping the pair), and dh = 0 is already a full 40-step collision; these are three of the four values of h's top two bits with a..g and h's low 30 bits equal.
- **Map.** Block 1 walks on psi(x) = (a, ..., g, h mod 2^30), a 254-bit map: one AND per evaluation, no subtraction.
- **Usable outcomes.** A collision psi(x) = psi(y) gives dh = h_x - h_y uniform on {0, 2^30, 2^31, 3*2^30}; three of four are usable, so usable collisions per T^2 rise by 2^2 * (3/4) = 3 and T shrinks by sqrt(3): -1/2 * log2(3) = -0.79248 bit.
- **Cost line.** Anchor: df1f1cd1's accepted R40 walk, 123.90702 at the success floor 0.61 (lambda0 = -ln 0.61). With the 254-bit reduction the walk base is a0 = 123.90702 - 1/2 * log2(3) = 123.11454. At the two-block split optimum P1 = 0.4037 the walk is 123.1465. The one AND for the mask is below the board claim quantum (10^-3, HashSmash.md:697).

## 4. Block 2: the 39-step construction on constants K1..K39
Steps 1..39 of block 2 run the 39-step characteristic with step t using K[t] where the original used K[t-1]. Constants carry no difference, so the signed differences are unchanged; only value conditions see different constants. Block 2's input chaining value is the state after the cancelling step, uniform because N0 is free.
- **Rows <= 16 executed.** The head-factory control r39_K16 with encoder sha_cnf_mdw (KOFF=1), clean chaining value, one cadical per seed, 300 s cap: SAT on 3 of 3 seeds in 69, 86, 122 s (the unshifted control 96, 145, 148 s). Every pinned A/E/W bit holds, 0 violations, independently recomputed with the shifted constants (experiments/koffconf.py); each pair violates 231-262 bits under the other constant set.
- **Carried ledger terms (5f8e6192 decomposition).** -log2 lambda0 = -1.0165; claw -log2(p8 p9) = +9.8077; W17 pin +32.0000; tail +74.3238; groups/claw r = 0.998473 -> +0.0022; ops/claw +1.5647; leader tightening (fce2f19e) -0.0609; = 116.621 at success 0.39. The carried board base is the best accepted r39 (9993eaa8 / 9993eaa8), 116.58624.
- **Tail transfer, measured by the shifted-constant comparison.** tailgen_gpu over 2^30 samples per junction gives the same junction-weight histogram on the shifted pair (steps 1..39 = K1..K39) as on the original (K0..K38) within sampling noise: J22 443,739,873 vs 443,737,969 kept, 4,187 vs 4,251 at weight 6 (experiments/tailshift.sh).
- **Cost line.** Converted to 40-step compressions, b0 = 116.58624 - log2(2896/2812) = 116.5437; at the split optimum P2 = 0.9492 the block-2 leg is 119.1776.

## 5. Shared work budget and success split (price40d.py (research record; the ledger of Section 5 reproduces it))
- **Driver.** One driver runs the 254-bit walk until the first usable collision; if exact it stops, else it runs block 2 in the remaining budget, halting at success or when the accumulated work reaches W (the r39 record 9993eaa8 driver rule).
- **Model.** Walk: P(T1 <= t) = 1 - exp(-lambda0 (t/2^a0)^2), lambda0 = -ln 0.61, a0 = 123.11454. Block 2: 1 - exp(-lambda0 (W - T1)/2^b0), b0 = 116.5437.
- **Success.** Success(W) = E[1{T1 <= W} * (1/3 + 2/3 * P2(W - T1))] = 0.39, the 1/3 being block 1's dh = 0 collisions that are already full 40-step collisions; solved by bisection.
- **Result.** log2 W = 123.135 (exact 123.13485), 0.77217 below the accepted board-best R40 (123.90702). Cross-checks: the separate-budget accounting gives 123.242 (price40b.py); our own walk base gives 123.13494; block 2 on 5f8e6192 gives 123.13696 (all within 0.002).

## 6. Memory
Both blocks run one after the other on the same 2^20-byte distinguished-point arena (PROFILE_5f8e6192 s3, s6: peak 1,047,428 B < 1,048,576), so the memory term is max(0, 19.998 - 20) = 0. Dropping h's top two bits uses zero extra arena: those two bit-slices are not referenced. Block-2 advice preprocessing (2^43) adds nothing to time.

## 7. Declared premises
- **P1 (walk random-function premise).** df1f1cd1's accepted random-function premise, applied to the 254-bit map psi (the 40-step output with h's top two bits dropped) with the same output distribution; the 254-bit outcome law (dh uniform on the top two bits) follows from psi's definition. Evidence: df1f1cd1 board ledger; outcome law section 3.
- **H1 (claw rates on K1..K39).** The 5f8e6192 claw rates and the W17 pin, declared to transfer to constants K1..K39 because the constants change value conditions only, never differences; rows <= 16 executed in section 3. Evidence: section 3 (3/3 SAT, 0 violations); 5f8e6192 proof s2.4, s5.
- **H2 (tail on K1..K39).** The 5f8e6192 tail (-log2 p >= 74.3238), transfer to K1..K39 supported by the shifted-constant histogram comparison (section 4, J22 443,739,873 vs 443,737,969). Evidence: 5f8e6192 proof s8; experiments/tailshift.sh.

## 8. Organizer-format experiment
The shipped program runs 256 trials, a 20 s watchdog, one CPU, and emits partial events (HEURISTIC_EXPERIMENTS.md format). Per trial it emits:
- shiftchk: the schedule identity for t = 1..63, dN0 = 0x40000000, and the h-only back-stepped chaining difference 0xc0000000 on a verified pair;
- koffconf: the r39_K16 conformance under K1..K39 (0 violations) and the control under K0..K38;
- tailshift: the per-junction kept/weight histogram on the shifted pair against the original;
- price40d: the bisection solving Success(W) = 0.39, printing log2 W = 123.135 (exact 123.13485), P1 = 0.4037, P2 = 0.9492.
A failed assertion returns null and fails the trial, so the organizer's byte-identical rerun carries these checks.
