# VOL49: a counted cost bound for a 49-step SHA-256 ordinary collision

Score (collision-frontier-v5): time_log2 = 258.07584 target-compressions. Memory is reported separately: 2^19.27 bytes by construction (complete under the model; term max(0, log2-20) = 0).

## 1. Target and prices
- Target: two distinct messages under the standard IV, the first 49 steps, standard padding and feed-forward, all 256 output bits equal. Each message is one 64-byte data block followed by the common SHA-256 padding block; the two data blocks give an equal chaining value, so the equal padding block preserves the collision and the full messages collide.
- Prices: one 49-step target compression is one unit. Every other primitive word operation (add, sub, xor, and, or, not, shift, rotate, compare, random word, table index) costs 1/C, with C = 3652. C = 3652 is the organizer reference operation count of the 49-step compression (hash-smash/scripts/reference_operation_costs.py counting method run at 49 rounds; it gives 2896 at 40 rounds).

## 2. Head (experiment v49-shift-01)
- Generator: the VOL40 v7e generator with the W13 retry count raised from 14 to 22 outputs message pairs whose expanded difference follows the msb17 body (difference silent on words 27..39).
- Shift: each pair is replaced by its schedule words -9..6, computed backward from the expansion rule (W_-1 = W15 - sigma1(W13) - W8 - sigma0(W0), then W_-2 = W14 - sigma1(W12) - W7 - sigma0(W_-1), and so on to W_-9 = W7 - sigma1(W5) - W0 - sigma0(W_-8)). The resulting words 0..15 are each member's complete 64-byte data block (equal length; standard padding appends the same final block to both); both are run from the standard IV through all 49 steps using the unmodified SHA-256 schedule recurrence and constants K_i at their original indices i (no step, word, or constant is renumbered), so the claimed event is an ordinary collision of two complete messages. The expansion of the shifted pair is the original expansion moved by 9 words, so the difference is silent on words 36..48 (checked on every pair).
- The generator, the shift, the expansion and the recomputation of the shifted pair from the standard IV work bit-sliced on 256 lanes; a gate on 256 lanes counts as one word operation, the accounting of the board's R40 entry df1f1cd1. Early abort: 4 steps before the junction the batch checks a 32-bit necessary condition that needs only half of the next step (the output a - e of a step equals T2 - d, so the two members must differ there by exactly 2^31); a batch with a live lane then computes that step and checks the register-a and register-e differences (64 bits per lane, counted).
- Each kept pair costs 31,148.1 charged operations (2^3.09239 units): 7,779.245 word operations per kept pair = (214,000 generation budget + 256 x 4,900 recognition of every lane + 180,800 per-batch control block) / 212, each charged with its two operand loads and one result store (31,117.0), times 1/(1 - 0.001) for discarded batches = 31,148.1 (Section 4). Each word operation is charged together with its two operand loads and one result store (the data-movement upper bound of a register-free RAM program under collision-frontier-v5), so the charged total before the discard factor is 7,779.245 x 4 = 31,117.0 operations per kept pair, and 31,148.1 after it.
- Derivation of the count (auditable from the organizer report and the source):
  - generation per batch: ops_used minus 4,900 x kept minus 180,800, as reported per trial; measured over 24 batches of 256 lanes: minimum 136,818, maximum 137,329 (136,510-137,678 over 20,000 batches of the shipped program); the ledger charges the declared budget 214,000 per batch (a hard upper bound on the executed generation of every batch: before each retry the program halts unless the running count plus the maximum cost of one retry round, 1,585, plus the maximum cost of the mandatory work after the loop, 177,645, fits under it; both maxima count every gate at its unfolded price with every branch taken; a batch that halts is discarded and still charged the full budget);
  - kept lanes per batch: measured mean 242.2, minimum 235 over 24 batches (per-lane rate 0.946; mean 242.4, minimum 224 over 20,000 batches of the shipped program); the ledger uses the floor 212 (premise H-kept-pair-yield), so the per-kept-pair charge is (214,000 + 256 x 4,900 + 180,800) / 212 = 7,779.245 word operations (the per-lane block charged for every lane, the control block once per batch);
  - per-lane and per-batch work, v5 primitives, itemized from the shipped source (trial(), the per-lane loop, tail49_sl.py:152-185): one schedule word = two sigma functions of 9 primitives and 3 additions = 21; one step = 38 primitives (two Sigma functions of 11, Ch 4, Maj 5, 7 additions); every other primitive 1; loop control 3 per iteration (index, compare, branch); a leading-bit count built from primitives as a 5-step binary search (compare, branch, shift per step; 15 primitives):
    - per kept lane (every kept lane):
      - lane loop control (every lane): 4
      - copy base word vector and set W13; build the second member (16 additions): 81
      - sample tests: kept <= 16, kept <= 32 (2 compares) + 3 branches: 5
      - shift back() of both members, nine words: 2 x (16 copy + 9 x (21 + 16 word moves + 3 loop control)): 752
      - two shifted schedules, words 16..34 (19 x 21 x 2) + loop control (19 x 3 x 2): 912
      - copy the IV for both; steps 0..30 of both shifted members (31 x 38 x 2) + loop control: 2,465
      - steps 31..34 of both (4 x 38 x 2) + loop control: 316
      - J35 difference (8 xor), leading-bit count (8 x (xor, test, 15)) + loop control, four landing counters, best-lane compare and branch: 178
      - landing k4 counter (compare, add): 2
      - total 4,715; charged RECOG = 4,900 per lane (tail49_sl.py:109) for every one of the 256 lanes, kept or not. The program adds 4,900 to ops_used for every kept lane; a lane that is not kept executes only the loop control.
    - control block, on each of the first NC = 16 kept lanes of a batch (tail49_sl.py:207):
      - shifted schedules extended, words 35..48 of both (14 x 21 x 2) + loop control (14 x 3 x 2): 672
      - shifted sliced control (xor, compare, add): 3
      - shifted schedule check: words 36..48 equal (13 compares), words 25..35 difference (11 x (index sub, sub, compare)) + loop control (24 x 3) + and + tally: 120
      - two unshifted schedules to word 39 (24 words x 21 x 2) + loop control: 1,152
      - expanded differences 16..39 checked (24 subtractions + 24 compares) + loop control + tally: 121
      - copy both states; steps 13..22 of both unshifted members (10 x 38 x 2) + loop control: 806
      - sliced-control compare (2 xor, 2 compare, and, add): 6
      - steps 23..25 of both unshifted members (3 x 38 x 2) + loop control: 237
      - shifted forced-target tail 35..48 and negative control: 2 x (8 copy + 8 xor + 14 x 38 x 2 + 8 compare + add) + loop control (2 x 14 x 3): 2,262
      - unshifted forced-target tail 26..39 and negative control (asserted only, not an observation key): 2 x (8 copy + 8 xor + 14 x 38 x 2 + 8 compare + add + branch) + loop control: 2,264
      - per control lane 7,643
    - per-bit uniformity tallies, on each of the first NB = 32 kept lanes of a batch (tail49_sl.py:207): 8 x (1 xor + 32 x (shift, and, sub, add)) + loop control: 1,824
    - control block per batch: 16 x 7,643 + 32 x 1,824 = 180,656; charged CTRL = 180,800 once per batch (tail49_sl.py:207), added to ops_used on every trial.
  - Everything the program executes on every kept lane (the second member, the shift of both, both shifted schedules to word 34, steps 0..34 of both shifted members, the junction counts and the loop control) is charged in RECOG; everything it executes only on the first 16 or 32 kept lanes (both 40-word schedules and their difference check, the shifted schedules to word 48 and their check, steps 13..25 of both unshifted members, the sliced controls, the two shifted and the two unshifted tail evaluations, the per-bit tallies) is charged in CTRL as if all 16 and 32 lanes ran; nothing on the per-lane path is left out of the total.
- A found pair is checked by 4 reduced verification compressions (data block and padding block of each of the two messages), charged as one unit each (4 units per found pair), and written out.
- The program counts every operation, including the per-kept-lane recognition and the per-batch control block, and halts generation before any retry after which the maximum remaining work (one retry round at most 1,585 plus the post-loop work at most 177,645, every gate at its unfolded price, every branch taken) could pass the budget, so no batch executes more than the budget (cap_hit records a halt).
- Controls on the first 16 kept pairs of every batch (NC = 16, tail49_sl.py:207): the 40-word and the shifted 49-word schedule difference, and a word-level recomputation of the junction states (sliced-vs-word), for both the unshifted J26 and the shifted J35 junction.
- Evidence: Section 7 (24 trials: schedule control, sliced control and tail 5,812 of 5,812; 36 trials: 8,749 of 8,749).

## 3. Landing and tail (experiment v49-shift-01)
- P1: the J35 XOR difference of a shifted pair equals the target with probability 2^-256 (a declared heuristic; the full-width rate is the premise, not a measured fact). Organizer-run evidence: each trial reports landing_k8, landing_k16, landing_k24, landing_k32 and best_lead_bits over its kept pairs (expected kept x 2^-k); the organizer's seeds are fixed public seeds (reproducibility evidence, not a holdout). On 20,000 further fresh-seed trials of the shipped program the per-bit uniformity check held on every trial (bit-match counts 2..29 of 32 tally lanes); landing k8 18,914 (expected 18,938.2), k16 82 (74.0), k24 0 (0.29), k32 0 (0.001); failed trials 0.
  - Shifted pairs of this generator and shift: 36 trials (8,749 pairs) k=8 landing 33 (expected 34.2); 24 trials (5,812 pairs) k=8 landing 23 (expected 22.7), k=16 landing 0 (expected 0.09).
  - Pooled over the 21 shifted packages R41-R61 (same generator, 183,497 pairs): k=8 landing 745 (expected 716.8), k=16 landing 4 (expected 2.80); a further 4,704 trials of the same 21 experiments on a second machine (1,138,197 pairs): k=8 landing 4,518 (expected 4,446.1), k=16 landing 14 (expected 17.37); all 1,321,694 pairs together: k=8 landing 5,263 (expected 5,162.9), k=16 landing 18 (expected 20.17); landing-rate check z = +1.39 on the pooled k=8 count (one-sided p 0.08), z = -0.27 for the unshifted program on 4,331,098 pairs.
  - The unshifted generator pairs, measured on 2^36 head-induced states, k-bit match: 2^-8.00, 2^-16.00, 2^-23.98, 2^-31.83 for k = 8, 16, 24, 32; per-bit bias at most 0.00001.
- P2: a shifted pair at the target collides after step 49 with probability 1, by construction. The shifted schedule difference is the body's difference moved by nine words: words 36..48 have difference 0 (checked by the schedule control on the first 16 kept pairs of every batch, 13 compares each, and on every kept pair of the 200-batch full-control run); words 25..35 carry the body's differences 16..26. The target is the state difference (0,0,0,0,0,0,0,0x80000000) at the junction after step 34; step 35 adds the lit word 35 whose difference cancels it, and from step 36 on equal words are added to equal states, so the states and the feed-forward are equal.
  - 5,812 of 5,812 (24 trials) and 8,749 of 8,749 (36 trials) on real program states with the target set.
  - Negative control (bit 30 of register h): 0 in both.
- P3: landing events of distinct pairs are independent (declared). Pairs of one batch share the generator words except the retried word; after the shift no compression step is shared, and each trial is one batch of 256 lanes, so the per-trial dispersion tests the within-batch dependence. Lane-keeping dispersion over 24 batches: variance 10.14 vs binomial 13.09 (ratio 0.775), the model declared in H-kept-pair-yield. Organizer-run evidence: the per-trial landing_k8 counts of the trusted report (one batch of 256 lanes per trial) form the dispersion sample; under P3 their variance equals their mean.
  - Shifted pairs over the 4,200 second-machine trials whose per-trial outputs were retained (1,016,296 pairs; the other 504 kept only totals, k=8 508 vs 476.2 expected): mean 0.9548 vs 0.9452 expected, variance 0.9446, dispersion chi-square 4,197.8 vs 4,199 +- 91.6 (no clustering); this program's 24 trials alone: chi-square 13.7 vs 23 +- 6.8; the shipped program over 20,000 trials: kept-per-batch variance 13.05 vs binomial 12.87 (ratio 1.014).
  - VOL40 batch test of the shared generator part: 64 batches x 512 pairs, dispersion chi-square 65.0 vs 64 +- 11.3.

## 4. Ledger
- Fixed batch count: B = ceil(N / (212 x (1 - 0.001))) batches, N = ln(1/0.61) x 2^256 kept pairs. Every batch is charged at the declared generation budget 214,000 plus recognition of all 256 lanes (4,900 each = 1,254,400) plus the per-batch control block CTRL = 180,800 (controls and tails on the first 16 kept lanes, per-bit tallies on the first 32), whether a lane is kept or not and whether the batch is kept or discarded: T = B x (214,000 + 256 x 4,900 + 180,800) x 4 / 3652 + 4 + 2^28.2, a deterministic total-work bound. Per kept pair this is (214,000 + 1,254,400 + 180,800) / 212 = 7,779.245 word operations, x 4 loads/stores = 31,117.0, x 1/(1 - 0.001) = 31,148.1 charged operations = 2^3.09239 units. The shipped program runs the per-lane block only on kept lanes, so its executed work is below this charge.
- Discard rate: measured 0 of 24 batches (none under the floor, none at the budget, no hard-check failure; every failed check discards the batch and is in this count); over the 20,000 fresh-seed batches of the shipped program: 0 discarded (none under the floor, none at the budget, no hard-check failure). The declared per-batch discard probability is p <= 2e-4 (above the one-sided Clopper-Pearson 95% upper bound 1.50e-04 of 0 in 20,000); the declared fraction 0.001 is 5 times p; with B about 2^247.3 independent batches, Pr[more than 0.001 B discarded] < exp(-B x D(0.001 || 2e-4)) < 2^-1000 (D = 0.00081 nats per batch), included in the 0.39.
- T = N x 2^3.09239 + 4 x (pairs found).
- log2 N = 256 + log2(ln(1/0.61)) = 254.98345; log2 T = 258.07584 (exact 258.07583492, rounded up to five decimals).
- Success: under P1-P3 the probability is at least 1 - exp(-ln(1/0.61)) = 0.39. The run stops at the first found pair; its verification (4 reduced compressions) and the preprocessing 2^28.2 are added to T; neither changes the rounded exponent.
- Hard-asserted checks (tail49_sl.py:189-198): on every organizer trial the shipped program asserts, and fails the trial otherwise: schedule control = 16 passes on the first 16 kept lanes (40-word and shifted 49-word); sliced control = 16 passes on those lanes (J26 state and J35); forced-target tail = 16 and negative control = 0 on those lanes (shifted 35..48 and unshifted 26..39); kept >= 212; generation within its budget 214,000; every one of the 256 J35 junction-difference bits matches the target bit for 16 +- 6 sqrt(32)/2 of the first 32 kept lanes (per-bit band; at 32 lanes this 6-sigma band, 16 +- 17.0, is wide and admits every count, so the uniformity evidence for P1 is the pooled count over 20,000 trials, not this check); landing_k4 <= kept/16 + 6 sqrt(kept/16) over all kept lanes. A failed trial returns null messages and reports checks_failed and checks_mask (bits 1, 2, 4, 8, 16, 32, 64 in the order above), so the organizer's byte-identical rerun carries these checks.

## 5. Preprocessing and memory
- Preprocessing ledger (lists as VOL40): each of the 7 lists (W4 row 19; W5 row 20; W6 row 21; W7 row 22; W12 row 27; W17 targets; W25 targets) is built by enumerating all 2^32 candidate words against its condition at <= 24 word operations each: 2^32 x 24 / 3652 = 2^24.75 compressions per list, 7 lists = 2^27.56; the W8 and W10 subsets (2^12 each) cost 422 compressions; total 2^27.56, declared 2^28.2 (rounded up).
- The online memory, complete under the model: list subsets 357,408 + program code 52,002 + sliced working state 214,016 + word-level working state 5,768 + current messages 128 = 629,322 bytes = 2^19.27 (exponent rounded up; term 0).
  - Sliced state (one sliced word = 32 bit-planes x 256 lanes = 1,024 bytes): the VOL40 inventory, 110 (schedule words of member 1, 24; of member 2, 24; member-2 schedule with the retried word, 24; both states after the counted window, 16; hoisted batch constants, 4; retried-word candidates, 2; retry schedule words, 4; lane masks and kept word, 4; temporaries in add/sigma (upper bound), 8); plus the shift: shifted message and schedule words of member 1 to word 34, 35; of member 2, 35; both shifted states, 16; early-abort words (two T2 values and the compare word), 3; register-a and register-e check words, 2; junction difference, 8 = 99; total 209 sliced words = 214,016 bytes.
  - Word-level state: the VOL40 inventory, 232 words; plus the per-lane control vectors of the unshifted and shifted junction (3 x 256), the per-bit tallies (256), and one lane's shifted words (shifted messages 32, shifted schedules 98, shifted states and snapshot 32, junction difference 8, tail states 16 = 186) = 1,210; total 1,442 words = 5,768 bytes.
  - Lists: L17_r19_W4 32,768 + L17_r20_W5 512 + L17_r21_W6 176 + L17_r22_W7 16 + L17_r27_W12 28,160 + L17_W17_joint(2^15) 131,072 + L17_r27_W25(2^15) 131,072 + W8 subset 16,384 + small tables = 357,408 (as VOL40). Random words per pair: W10, W12 index draws, each charged as one word op.

## 6. Declared premises
- P1-uniform-junction, P2-tail-induced, P3-independence and H-kept-pair-yield, with the evidence above.
- Not measured: bits beyond 16 jointly on shifted pairs (the shipped program over 20,000 trials: k24 0 vs 0.29 expected, k32 0 vs 0.001) and beyond 32 on the unshifted generator (P1, the full-width rate is the declared premise); a naturally landed pair (expected only after ~2^256 pairs; P2 rests on the structural argument, not on natural samples).

- Seeds and selection: the organizer trials use the organizer's fixed public seed; our 20,000-trial runs of the shipped program use the consecutive integer seeds 220,000..239,999, fixed in the run script before the first run, with no re-draw, no discarded run and every trial reported; the 200-batch figures are the complete output of this row's earlier evidence run (seeds fixed by its script) and the 36-trial figures the complete output of its first run; no seed, run, batch or row was selected or dropped after seeing results, and the pooled cross-package count includes every shifted row.
## 7. Measurement logs (inlined; every declared bound in Sections 1-5 rounds up)
### 24 organizer-format trials of v49-shift-01 (generator and shift as shipped; per-lane recognition then outside ops_used)
```
trials 24, lanes 256, kept 5812 (per trial min 235, mean 242.17, max 248, variance 10.14), generation ops_used 136818..137329, cap_hit 0
schedule control 5812/5812, sliced control 5812/5812, tail 5812/5812, negative control 0
shifted landing k8 23 (expected 22.7), k16 0 (expected 0.09)
```
### 36 organizer-format trials (TRY 22, early abort J-4)
```
trials 36 pairs 8749 k8 33 k16 1 tail 8749 neg 0
```
### Dispersion of per-trial k=8 landing
```
S113 all 21 shift packages, 4,200 trials: trials 4200, pairs 1016296, k8 total 4010, per-trial mean 0.9548 vs expected 0.9452, variance 0.9446 (Poisson: 0.9452), dispersion chi2 4197.8 vs 4199 +- 91.6
S112 R49 only, 24 trials: trials 24, pairs 5812, k8 total 23, per-trial mean 0.9583 vs expected 0.9460, variance 0.5399 (Poisson: 0.9460), dispersion chi2 13.7 vs 23 +- 6.8
```
### Shipped program, one trial (seed 1)
```
{"kept": 249, "schedule_control_pass": 16, "sliced_control_pass": 16, "ops_used": 1537679, "cap_hit": 0, "landing_k8": 1, "landing_k16": 0, "landing_k24": 0, "landing_k32": 0, "best_lead_bits": 9, "bit_match_min": 9, "bit_match_max": 24, "checks_failed": 0, "checks_mask": 0, "tail_collide": 16, "neg_control_collide": 0}
```
ops_used = 136,779 generation + 249 x 4,900 + 180,800.
### Shipped program, 20,000 fresh-seed trials
```
trials 20000 pairs 4848187 k8 18914 k16 82 k24 0 k32 0 checks_failed_total 0 failed_trials 0 masks {0: 20000} kept_min 224 kept_mean 242.41 kept_max 254 gen_min 136510 gen_max 137678 bitmatch_min 2 bitmatch_max 29
```
