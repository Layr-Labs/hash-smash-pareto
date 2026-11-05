# VOL44: a counted cost bound for a 44-step SHA-256 ordinary collision

Score (collision-frontier-v5): time_log2 = 256.52252 target-compressions. Memory is reported separately: 2^19.59 bytes by construction (complete under the model; term max(0, log2-20) = 0).

## 1. Target and prices
- Target: two distinct messages under the standard IV, the first 44 steps, standard padding and feed-forward, all 256 output bits equal. Each message is one 64-byte data block followed by the common SHA-256 padding block; the two data blocks give an equal chaining value, so the equal padding block preserves the collision and the full messages collide.
- Prices: one 44-step target compression is one unit. Every other primitive word operation (add, sub, xor, and, or, not, shift, rotate, compare, random word, table index) costs 1/C, with C = 3232. C = 3232 is the organizer reference operation count of the 44-step compression (hash-smash/scripts/reference_operation_costs.py counting method run at 44 rounds; it gives 2896 at 40 rounds).

## 2. Head (experiment v44-shift-01)
- Generator: the VOL40 v7e generator with the W13 retry count raised from 14 to 22 outputs message pairs whose expanded difference follows the msb17 body (difference silent on words 27..39).
- Shift: each pair is replaced by its schedule words -4..11, computed backward from the expansion rule (W_-1 = W15 - sigma1(W13) - W8 - sigma0(W0), and so on to W_-4). The resulting words 0..15 are each member's complete 64-byte data block (equal length; standard padding appends the same final block to both); both are run from the standard IV through all 44 steps using the unmodified SHA-256 schedule recurrence and constants K_i at their original indices i (no step, word, or constant is renumbered), so the claimed event is an ordinary collision of two complete messages. The expansion of the shifted pair is the original expansion moved by 4 words, so the difference is silent on words 31..43 (checked on every pair).
- The generator, the shift, the expansion and the recomputation of the shifted pair from the standard IV work bit-sliced on 256 lanes; a gate on 256 lanes counts as one word operation, the accounting of the board's R40 entry df1f1cd1. Early abort: 4 steps before the junction the batch checks a 32-bit necessary condition that needs only half of the next step (the output a - e of a step equals T2 - d, so the two members must differ there by exactly 2^31); a batch with a live lane then computes that step and checks the register-a and register-e differences (64 bits per lane, counted).
- Each kept pair costs 9,392.4 charged operations (2^1.53907 units): 2,345.755 word operations per kept pair = (183,000 generation budget + 256 x 300 recognition of every lane + 237,500 per-batch control block) / 212, each charged with its two operand loads and one result store (9,383.0), times 1/(1 - 0.001) for discarded batches = 9,392.4 (Section 4). Each word operation is charged together with its two operand loads and one result store (the data-movement upper bound of a register-free RAM program under collision-frontier-v5), so the charged total before the discard factor is 2,345.755 x 4 = 9,383.0 operations per kept pair, and 9,392.4 after it.
- Derivation of the count (auditable from the organizer report and the source):
  - generation per batch: ops_used minus 300 x kept minus 237,500, as reported per trial; measured over 200 batches of 256 lanes: minimum 103,062, maximum 103,683 (127,471-128,729 over 20,000 batches of the shipped program); the ledger charges the declared budget 183,000 per batch (a hard upper bound on the executed generation of every batch: before each retry the program halts unless the running count plus the maximum cost of one retry round, 1,585, plus the maximum cost of the mandatory work after the loop, 144,249, fits under it; both maxima count every gate at its unfolded price with every branch taken; a batch that halts is discarded and still charged the full budget);
  - kept lanes per batch: measured mean 242.3, minimum 232 over 200 batches (per-lane rate 0.946; mean 242.5, minimum 227 over 20,000 batches of the shipped program); the ledger uses the floor 212 (premise H-kept-pair-yield), so the per-kept-pair charge is (183,000 + 256 x 300 + 237,500) / 212 = 2,345.755 word operations (the per-lane block charged for every lane, the control block once per batch);
  - per-lane and per-batch work, v5 primitives, itemized from the shipped source (trial(), the per-lane loop, tail44_sl.py:266-300): one schedule word = two sigma functions of 9 primitives and 3 additions = 21; one step = 38 primitives (two Sigma functions of 11, Ch 4, Maj 5, 7 additions); every other primitive 1; loop control 3 per iteration (index, compare, branch); a leading-bit count built from primitives as a 5-step binary search (compare, branch, shift per step; 15 primitives):
    - The junction differences of all 256 lanes come from the bit-sliced block once per batch (steps to the junction run on every lane, 8 registers, transposed once, 8 x 32 operations inside the generation count); the per-lane work is the leading-bit count on the lane's 8 transposed words and its counters.
    - per kept lane (every kept lane):
      - lane loop control (every lane): 4
      - kept counter (add): 1
      - sample tests: kept <= NC, kept <= NB (2 compare) + 2 branches: 4
      - transpose share: the lane's 8 junction-difference words read from the batch-transposed DS (8 x (index add, load)); the transpose itself is per batch, in generation (8 x 32, line 262): 16
      - leading-bit count (8 x (xor with target, test, 15)) + loop control (8 x 3), four landing counters (4 x (compare, add)), best-lane compare and branch, best-lane record (2 stores): 172
      - landing k4 counter (compare, add): 2
      - total 199; charged 300 per lane for every one of the 256 lanes, kept or not. The program adds 300 to ops_used for every kept lane; a lane that is not kept executes only the loop control.
    - evidence block (word level), on each of the first NC = 16 kept lanes of a batch (tail44_sl.py:321):
      - copy base word vector and set W13; build the second member (16 additions): 81
      - back() of both members, KS = 4: 352
      - two shifted schedules, words 16..29 + loop control: 672
      - shifted schedules extended, words 30..43 of both + loop control: 672
      - copy IV for both; steps 0..25 of both + loop control: 2,070
      - steps 26..29 of both + loop control: 316
      - sliced control: register a at step 26 (xor, compare, add) + full J30 difference vs DS (8 xor, 8 compare, 8 and, 1 and): 28
      - shifted schedule check: words 31..43 equal, words 20..30 difference + loop control + and + tally: 120
      - two 40-word schedules + loop control: 1,152
      - expanded differences 16..39 checked + loop control + tally: 121
      - copy both states; steps 13..22 of both + loop control: 806
      - sliced-control compare (2 xor, 2 compare, and, add): 6
      - steps 23..25 of both + loop control: 237
      - shifted forced-target tail and negative control: 2,262
      - 26..39 forced-target tail and negative control: 2,264
      - per NC lane 11,159
    - per-bit uniformity tallies, on each of the first NB = 32 kept lanes of a batch: per-bit tallies: 8 x (1 xor + 32 x (shift, and, sub, add)) + loop control: 1,824
    - best-lane output, once per batch: branch; rebuild W13 and the second member (81); back() of both (352): 434
    - 16 x 11,159 + 32 x 1,824 + 434 = 237,346; charged 237,500 per batch.
  - Everything the program executes on every kept lane (the lane's 8 junction-difference words read from the batch-transposed sliced difference, the leading-bit count, the landing counters, the best-lane compare and record, and the loop control) is charged in RECOG; the shift, both shifted schedules and the steps to the junction of all 256 lanes run bit-sliced inside the generation count; everything it executes only on the first 16 or 32 kept lanes (the word-level recomputation of the second member, the shift of both, both shifted schedules to word 29 and steps 0..29 of both shifted members, both 40-word schedules and their difference check, the shifted schedules to word 43 and their check, steps 13..25 of both unshifted members, the sliced controls, the two shifted and the two unshifted tail evaluations, the per-bit tallies) and once per batch for the best lane (its second member and the shift of both) is charged in CTRL as if all 16 and 32 lanes ran; nothing on the per-lane path is left out of the total.
- A found pair is checked by 4 reduced verification compressions (data block and padding block of each of the two messages), charged as one unit each (4 units per found pair), and written out.
- The program counts every operation, including the per-kept-lane recognition and the per-batch control block, and halts generation before any retry after which the maximum remaining work (one retry round at most 1,585 plus the post-loop work at most 144,249, every gate at its unfolded price, every branch taken) could pass the budget, so no batch executes more than the budget (cap_hit records a halt).
- Controls on the first 16 kept pairs of every batch (NC = 16, tail44_sl.py:321): the 40-word and the shifted 44-word schedule difference, and a word-level recomputation of the junction states (sliced-vs-word), for both the unshifted J26 and the shifted J30 junction.
- Evidence: Section 7 (200 trials: schedule control, sliced control and tail 48,459 of 48,459; 36 trials: 8,749 of 8,749).

## 3. Landing and tail (experiment v44-shift-01)
- P1: the J30 XOR difference of a shifted pair equals the target with probability 2^-256 (a declared heuristic; the full-width rate is the premise, not a measured fact). Organizer-run evidence: each trial reports landing_k8, landing_k16, landing_k24, landing_k32 and best_lead_bits over its kept pairs (expected kept x 2^-k); the organizer's seeds are fixed public seeds (reproducibility evidence, not a holdout). On 20,000 further fresh-seed trials of the shipped program the per-bit uniformity check held on every trial (bit-match counts 2..30 of 32 tally lanes); landing k8 18,940 (expected 18,941.9), k16 86 (74.0), k24 0 (0.29), k32 0 (0.001); failed trials 0.
  - Shifted pairs of this generator and shift: 36 trials (8,749 pairs) k=8 landing 44 (expected 34.2); 200 trials (48,459 pairs) k=8 landing 220 (expected 189.3), k=16 landing 1 (expected 0.74).
  - Pooled over the 21 shifted packages R41-R61 (same generator, 183,497 pairs): k=8 landing 745 (expected 716.8), k=16 landing 4 (expected 2.80); a further 4,704 trials of the same 21 experiments on a second machine (1,138,197 pairs): k=8 landing 4,518 (expected 4,446.1), k=16 landing 14 (expected 17.37); all 1,321,694 pairs together: k=8 landing 5,263 (expected 5,162.9), k=16 landing 18 (expected 20.17); landing-rate check z = +1.39 on the pooled k=8 count (one-sided p 0.08), z = -0.27 for the unshifted program on 4,331,098 pairs.
  - The unshifted generator pairs, measured on 2^36 head-induced states, k-bit match: 2^-8.00, 2^-16.00, 2^-23.98, 2^-31.83 for k = 8, 16, 24, 32; per-bit bias at most 0.00001.
- P2: a shifted pair at the target collides after step 44 with probability 1, by construction. The shifted schedule difference is the body's difference moved by four words: words 31..43 have difference 0 (checked by the schedule control on the first 16 kept pairs of every batch, 13 compares each, and on every kept pair of the 200-batch full-control run); words 20..30 carry the body's differences 16..26. The target is the state difference (0,0,0,0,0,0,0,0x80000000) at the junction after step 29; step 30 adds the lit word 30 whose difference cancels it, and from step 31 on equal words are added to equal states, so the states and the feed-forward are equal.
  - 48,459 of 48,459 (200 trials) and 8,749 of 8,749 (36 trials) on real program states with the target set.
  - Negative control (bit 30 of register h): 0 in both.
- P3: landing events of distinct pairs are independent (declared). Pairs of one batch share the generator words except the retried word; after the shift no compression step is shared, and each trial is one batch of 256 lanes, so the per-trial dispersion tests the within-batch dependence. Lane-keeping dispersion over 200 batches: variance 11.90 vs binomial 12.97 (ratio 0.917), the model declared in H-kept-pair-yield. Organizer-run evidence: the per-trial landing_k8 counts of the trusted report (one batch of 256 lanes per trial) form the dispersion sample; under P3 their variance equals their mean.
  - Shifted pairs over the 4,200 second-machine trials whose per-trial outputs were retained (1,016,296 pairs; the other 504 kept only totals, k=8 508 vs 476.2 expected): mean 0.9548 vs 0.9452 expected, variance 0.9446, dispersion chi-square 4,197.8 vs 4,199 +- 91.6 (no clustering); this program's 200 trials alone: chi-square 214.2 vs 199 +- 19.9; the shipped program over 20,000 trials: kept-per-batch variance 12.88 vs binomial 12.83 (ratio 1.004).
  - VOL40 batch test of the shared generator part: 64 batches x 512 pairs, dispersion chi-square 65.0 vs 64 +- 11.3.

## 4. Ledger
- Fixed batch count: B = ceil(N / (212 x (1 - 0.001))) batches, N = (ln(1/0.61) + 2^-990) x 2^256 kept pairs. Every batch is charged at the declared generation budget 183,000 plus recognition of all 256 lanes (300 each = 76,800) plus the per-batch control block CTRL = 237,500 (controls and tails on the first 16 kept lanes, per-bit tallies on the first 32), whether a lane is kept or not and whether the batch is kept or discarded: T = B x (183,000 + 256 x 300 + 237,500) x 4 / 3232 + 4 + 2^28.2, a deterministic total-work bound. Per kept pair this is (183,000 + 76,800 + 237,500) / 212 = 2,345.755 word operations, x 4 loads/stores = 9,383.0, x 1/(1 - 0.001) = 9,392.4 charged operations = 2^1.53907 units. The shipped program runs the per-lane block only on kept lanes, so its executed work is below this charge.
- Discard rate: measured 0 of 200 batches (none under the floor, none at the budget, no hard-check failure; every failed check discards the batch and is in this count); over the 20,000 fresh-seed batches of the shipped program: 0 discarded (none under the floor, none at the budget, no hard-check failure). The declared per-batch discard probability is p <= 2e-4 (above the one-sided Clopper-Pearson 95% upper bound 1.50e-04 of 0 in 20,000); the declared fraction 0.001 is 5 times p; with B about 2^247.3 independent batches, Pr[more than 0.001 B discarded] < exp(-B x D(0.001 || 2e-4)) < 2^-1000 (D = 0.00081 nats per batch), included in the 0.39.
- T = N x 2^1.53907 + 4 x (pairs found).
- log2 N = 256 + log2(ln(1/0.61)) = 254.98345; log2 T = 256.52252 (exact 256.52251646, rounded up to five decimals).
- Success: under P1-P3 the conditional probability, given that at most a 0.001 fraction of the B batches is discarded, is at least 1 - exp(-ln(1/0.61) - 2^-990) = 0.39 + 0.61 x (1 - exp(-2^-990)) > 0.39 + 2^-991; subtracting the probability of the bad event (below 2^-1000, Section 4) leaves an unconditional success probability above 0.39. The 2^-990 margin in N changes log2 T by less than 2^-290. The run stops at the first found pair; its verification (4 reduced compressions) and the preprocessing 2^28.2 are added to T; neither changes the rounded exponent.
- Hard-asserted checks (tail44_sl.py:303-312): on every organizer trial the shipped program asserts, and fails the trial otherwise: schedule control = 16 passes on the first 16 kept lanes (40-word and shifted 44-word); sliced control = 16 passes on those lanes (J26 state and J30); the sliced control also requires the word-level junction difference of each control lane to equal its transposed sliced difference; forced-target tail = 16 and negative control = 0 on those lanes (shifted 30..43 and unshifted 26..39); kept >= 212; generation within its budget 183,000; every one of the 256 J30 junction-difference bits matches the target bit for 16 +- 6 sqrt(32)/2 of the first 32 kept lanes (per-bit band; at 32 lanes this 6-sigma band, 16 +- 17.0, is wide and admits every count, so the uniformity evidence for P1 is the pooled count over 20,000 trials, not this check); landing_k4 <= kept/16 + 6 sqrt(kept/16) over all kept lanes. A failed trial returns null messages and reports checks_failed and checks_mask (bits 1, 2, 4, 8, 16, 32, 64 in the order above), so the organizer's byte-identical rerun carries these checks.

## 5. Preprocessing and memory
- Preprocessing ledger (lists as VOL40): each of the 7 lists (W4 row 19; W5 row 20; W6 row 21; W7 row 22; W12 row 27; W17 targets; W25 targets) is built by enumerating all 2^32 candidate words against its condition at <= 24 word operations each: 2^32 x 24 / 3232 = 2^24.93 compressions per list, 7 lists = 2^27.74; the W8 and W10 subsets (2^12 each) cost 422 compressions; total 2^27.74, declared 2^28.2 (rounded up).
- The online memory, complete under the model (every live container of trial() at its peak, inventoried on the shipped program, seed 1): list subsets 357,408 (a conservative bound, below) + program code 65,032 + sliced working state 345,216 + word-level working state 17,296 + current messages 128 = 785,080 bytes = 2^19.59 (exponent rounded up; term max(0, log2-20) = 0).
  - Sliced state (one sliced word = 32 bit-planes x 256 lanes = 1,024 bytes; one 256-lane mask = 32 bytes), by program name: S.prev 148, CK 48, W 24, Vc 24, m1 18, m2s 18, X 8, Y 8, XS 8, YS 8, DS 8, V2 2, and 15 single sliced words (tc, d26, c20, c22, c24, c26, rb, r13, W20, W22, W24, W26, eq, v20, v22) = 337 sliced words = 345,088 bytes; lane masks done, z, new, FULL, 4 x 32 = 128 bytes; total 345,216 bytes.
  - Word-level state (one 32-bit word = 4 bytes), by program name: DU 2,048, da 256, de 256, SLA 256, k13 256, bitmatch 256, K 48, av 44, bv 44, aw 40, bw 40, _a 40, _b 40, dW 40, _c 32, _r 32, INV 32, POW 32, e 24, a24 24, b24 24, base 16, v 16, w 16, m2 16, v1 16, v2 16, A 8, B 8, dd 8, P3 8, Q3 8, P 8, Q 8, tg 8, P4 8, Q4 8, P2 8, Q2 8, IV 8, TGT 8, IV0 8, best 2; 43 single words (wops, lops, _, j, t, RECOG, cap, kk, i, y, ops, kept, sc, dc, tcol, ncol, FLOOR, k4, l3, wi, o, hb, key, y17, S.G, M, L, TRY, C13, OPCAP, RETRY_MAX, POST_MAX, _k, _p, r, t23, t25, t28, NOPS, KS, NC, NB, CTRL); keys of the step cache S.prev, 2 x 80 = 160; transient locals of run(), 39; total 4,324 words = 17,296 bytes.
  - Lists: L17_r19_W4 32,768 + L17_r20_W5 512 + L17_r21_W6 176 + L17_r22_W7 16 + L17_r27_W12 28,160 + L17_W17_joint(2^15) 131,072 + L17_r27_W25(2^15) 131,072 + W8 subset 16,384 + small tables = 357,408 (as VOL40). Random words per pair: W10, W12 index draws, each charged as one word op. The program holds 6,320 list words = 25,280 bytes (L4, L5, L6, L7, L17, L25, L8, L10, with L12 reached through the loop name Lst); the full-list figure 357,408 is kept as a conservative bound.

## 6. Declared premises
- P1-uniform-junction, P2-tail-induced, P3-independence and H-kept-pair-yield, with the evidence above.
- Not measured: bits beyond 16 jointly on shifted pairs (the shipped program over 20,000 trials: k24 0 vs 0.29 expected, k32 0 vs 0.001) and beyond 32 on the unshifted generator (P1, the full-width rate is the declared premise); a naturally landed pair (expected only after ~2^256 pairs; P2 rests on the structural argument, not on natural samples).

- Seeds and selection: the organizer trials use the organizer's fixed public seed; our 20,000-trial runs of the shipped program use the consecutive integer seeds 120,000..139,999, fixed in the run script before the first run, with no re-draw, no discarded run and every trial reported; the 200-batch figures are the complete output of this row's earlier evidence run (seeds fixed by its script) and the 36-trial figures the complete output of its first run; no seed, run, batch or row was selected or dropped after seeing results, and the pooled cross-package count includes every shifted row.
## 7. Measurement logs (inlined; every declared bound in Sections 1-5 rounds up)
### 200 organizer-format trials of v44-shift-01 (generator and shift as shipped; per-lane recognition then outside ops_used)
```
trials 200, lanes 256, kept 48459 (per trial min 232, mean 242.30, max 250, variance 11.90), generation ops_used 117812..118503, cap_hit 0
schedule control 48459/48459, sliced control 48459/48459, tail 48459/48459, negative control 0
shifted landing k8 220 (expected 189.3), k16 1 (expected 0.74)
```
### 36 organizer-format trials (TRY 22, early abort J-4)
```
trials 36 pairs 8749 k8 44 k16 0 tail 8749 neg 0
```
### Dispersion of per-trial k=8 landing
```
S113 all 21 shift packages, 4,200 trials: trials 4200, pairs 1016296, k8 total 4010, per-trial mean 0.9548 vs expected 0.9452, variance 0.9446 (Poisson: 0.9452), dispersion chi2 4197.8 vs 4199 +- 91.6
S113 R44 only, 200 trials: trials 200, pairs 48459, k8 total 220, per-trial mean 1.1000 vs expected 0.9465, variance 0.9900 (Poisson: 0.9465), dispersion chi2 214.2 vs 199 +- 19.9
```
### Shipped program, one trial (seed 1)
```
{"kept": 249, "schedule_control_pass": 16, "sliced_control_pass": 16, "ops_used": 439885, "cap_hit": 0, "landing_k8": 0, "landing_k16": 0, "landing_k24": 0, "landing_k32": 0, "best_lead_bits": 6, "bit_match_min": 7, "bit_match_max": 24, "checks_failed": 0, "checks_mask": 0, "tail_collide": 16, "neg_control_collide": 0}
```
ops_used = 127,685 generation + 249 x 300 + 237,500.
### Shipped program, 20,000 fresh-seed trials
```
trials 20000 pairs 4849122 k8 18940 k16 86 k24 0 k32 0 checks_failed_total 0 failed_trials 0 masks {0: 20000} kept_min 227 kept_mean 242.46 kept_max 255 gen_min 117648 gen_max 118906 bitmatch_min 2 bitmatch_max 30
```
