# VOL41: a counted cost bound for a 41-step SHA-256 ordinary collision

Score (collision-frontier-v5): time_log2 = 259.45965 target-compressions. Memory is reported separately: 2^19.23 bytes by construction (complete under the model; term max(0, log2-20) = 0).

## 1. Target and prices
- Target: two distinct messages under the standard IV, the first 41 steps, standard padding and feed-forward, all 256 output bits equal. Each message is one 64-byte data block followed by the common SHA-256 padding block; the two data blocks give an equal chaining value, so the equal padding block preserves the collision and the full messages collide.
- Prices: one 41-step target compression is one unit. Every other primitive word operation (add, sub, xor, and, or, not, shift, rotate, compare, random word, table index) costs 1/C, with C = 2980. C = 2980 is the organizer reference operation count of the 41-step compression (hash-smash/scripts/reference_operation_costs.py counting method run at 41 rounds; it gives 2896 at 40 rounds).

## 2. Head (experiment v41-shift-01)
- Generator: the VOL40 v7e generator with the W13 retry count raised from 14 to 19 outputs message pairs whose expanded difference follows the msb17 body (difference silent on words 27..39).
- Shift: each pair is replaced by its schedule words -1..14, computed backward from the expansion rule (W_-1 = W15 - sigma1(W13) - W8 - sigma0(W0)). The resulting words 0..15 are each member's complete 64-byte data block (equal length; standard padding appends the same final block to both); both are run from the standard IV through all 41 steps using the unmodified SHA-256 schedule recurrence and constants K_i at their original indices i (no step, word, or constant is renumbered), so the claimed event is an ordinary collision of two complete messages. The expansion of the shifted pair is the original expansion moved by 1 word, so the difference is silent on words 28..40 (checked on every pair).
- The generator, the shift, the expansion and the recomputation of the shifted pair from the standard IV work bit-sliced on 256 lanes; a gate on 256 lanes counts as one word operation, the accounting of the board's R40 entry df1f1cd1. Early abort: 4 steps before the junction the batch checks a 32-bit necessary condition that needs only half of the next step (the output a - e of a step equals T2 - d, so the two members must differ there by exactly 2^31); a batch with a live lane then computes that step and checks the register-a and register-e differences (64 bits per lane, counted).
- Each kept pair costs 66,326.5 charged operations (2^4.47620 units): 16,565.049 word operations per kept pair = (110,000 generation budget + 256 x 12,900 recognition of every lane) / 206, each charged with its two operand loads and one result store (66,260.2), times 1/(1 - 0.001) for discarded batches = 66,326.5 (Section 4). Each word operation is charged together with its two operand loads and one result store (the data-movement upper bound of a register-free RAM program under collision-frontier-v5), so the charged total before the discard factor is 16,565.049 x 4 = 66,260.2 operations per kept pair, and 66,326.5 after it.
- Derivation of the count (auditable from the organizer report and the source):
  - generation per batch: ops_used minus 12,900 x kept, as reported per trial; measured over 200 batches of 256 lanes: minimum 103,062, maximum 103,683 (102,933-103,894 over 20,000 batches of the shipped program); the ledger charges the declared budget 110,000 per batch (above every measured batch; a batch that reaches it halts and is discarded);
  - kept lanes per batch: measured mean 235.6, minimum 223 over 200 batches (per-lane rate 0.920; mean 235.7, minimum 215 over 20,000 batches of the shipped program); the ledger uses the floor 206 (premise H-kept-pair-yield), so the per-kept-pair charge is (110,000 + 256 x 12,900) / 206 = 16,565.049 word operations (the per-lane block charged for every lane);
  - per-lane work, v5 primitives, itemized from the shipped source (trial(), the per-lane loop): one schedule word = two sigma functions of 9 primitives and 3 additions = 21; one step = 38 primitives (two Sigma functions of 11, Ch 4, Maj 5, 7 additions); every other primitive 1; loop control 3 per iteration (index, compare, branch); a leading-bit count built from primitives as a 5-step binary search (compare, branch, shift per step; 15 primitives):
    - lane loop control (every lane): 4
    - copy base word vector and set W13; build the second member (16 additions): 81
    - two full schedules to word 39 (24 words x 21 x 2) + loop control: 1,152
    - expanded differences 16..39 checked (24 subtractions + 24 compares) + loop control + tally: 121
    - copy both states; steps 13..22 of both members (10 x 38 x 2) + loop control: 806
    - sliced-control compare (2 xor, 2 compare, and, add): 6
    - steps 23..25 of both members (3 x 38 x 2) + loop control: 237
    - J26 difference (8 xor), leading-bit count (8 x (xor, test, 15)) + loop control, two landing counters: 172
    - shift back() of both members, one word: 2 x (16 copy + 21 + 16 word moves + 3 loop control): 112
    - two shifted schedules to word 40 (25 words x 21 x 2) + loop control: 1,200
    - shifted schedule check: words 28..40 equal (13 compares), words 17..27 difference (11 x (index sub, sub, compare)) + loop control (24 x 3) + and + tally: 120
    - copy the IV for both; steps 0..22 of both shifted members (23 x 38 x 2) + loop control: 1,833
    - copy both states (control snapshot): 16
    - step 23 of both (38 x 2): 76
    - steps 24..26 of both (3 x 38 x 2) + loop control: 237
    - J27 difference (8 xor), leading-bit count (8 x (xor, test, 15)) + loop control, sliced control (xor, compare, add), four landing counters, best-lane compare and branch: 181
    - landing k4 counter (compare, add): 2
    - per-bit uniformity tallies: 8 x (1 xor + 32 x (shift, and, sub, add)) + loop control: 1,824
    - shifted forced-target tail 27..40 and negative control: 2 x (8 copy + 8 xor + 14 x 38 x 2 + 8 compare + add) + loop control (2 x 14 x 3): 2,262
    - unshifted forced-target tail 26..39 and negative control (asserted only, not an observation key): 2 x (8 copy + 8 xor + 14 x 38 x 2 + 8 compare + add + branch) + loop control: 2,264
    - total 12,706; charged 12,900 per lane for every one of the 256 lanes, kept or not. The program adds 12,900 to ops_used for every kept lane; a lane that is not kept executes only the loop control.
  - Everything the program executes on a kept lane (both 40-word schedules and their difference check, steps 13..25 of both members, the shift of both, both 41-word shifted schedules and their check, steps 0..26 of both shifted members, the junction counts, the per-bit tallies, the two shifted and the two unshifted tail evaluations, and the loop control) is charged in the per-lane figure above; nothing on the per-lane path is left out of the total.
- A found pair is checked by 4 reduced verification compressions (data block and padding block of each of the two messages), charged as one unit each (4 units per found pair), and written out.
- The program counts every operation, including the per-kept-lane recognition, and halts generation before the next retry would pass its hard budget (cap_hit records a halt).
- Controls on every kept pair: the 40-word and the shifted 41-word schedule difference, and a word-level recomputation of the junction states (sliced-vs-word), for both the unshifted J26 and the shifted J27 junction.
- Evidence: Section 7 (200 trials: schedule control, sliced control and tail 47,116 of 47,116; 36 trials: 8,517 of 8,517).

## 3. Landing and tail (experiment v41-shift-01)
- P1: the J27 XOR difference of a shifted pair equals the target with probability 2^-256 (a declared heuristic; the full-width rate is the premise, not a measured fact). Organizer-run evidence: each trial reports landing_k8, landing_k16, landing_k24, landing_k32 and best_lead_bits over its kept pairs (expected kept x 2^-k); the organizer's seeds are fixed public seeds (reproducibility evidence, not a holdout). On 20,000 further fresh-seed trials of the shipped program the per-bit uniformity check held on every trial (bit-match counts 80..157 of about 236); landing k8 18,485 (expected 18,413.0), k16 86 (71.9), k24 0 (0.28), k32 0 (0.001); failed trials 0.
  - Shifted pairs of this generator and shift: 36 trials (8,517 pairs) k=8 landing 33 (expected 33.3); 200 trials (47,116 pairs) k=8 landing 175 (expected 184.0), k=16 landing 0 (expected 0.72).
  - Pooled over the 21 shifted packages R41-R61 (same generator, 183,497 pairs): k=8 landing 745 (expected 716.8), k=16 landing 4 (expected 2.80); a further 4,704 trials of the same 21 experiments on a second machine (1,138,197 pairs): k=8 landing 4,518 (expected 4,446.1), k=16 landing 14 (expected 17.37); all 1,321,694 pairs together: k=8 landing 5,263 (expected 5,162.9), k=16 landing 18 (expected 20.17); landing-rate check z = +1.39 on the pooled k=8 count (one-sided p 0.08), z = -0.27 for the unshifted program on 4,331,098 pairs.
  - The unshifted generator pairs, measured on 2^36 head-induced states, k-bit match: 2^-8.00, 2^-16.00, 2^-23.98, 2^-31.83 for k = 8, 16, 24, 32; per-bit bias at most 0.00001.
- P2: a shifted pair at the target collides after step 41 with probability 1, by construction. The shifted schedule difference is the body's difference moved by one word: words 28..40 have difference 0 (checked on every kept pair, 13 compares); words 17..27 carry the body's differences 16..26. The target is the state difference (0,0,0,0,0,0,0,0x80000000) at the junction after step 26; step 27 adds the lit word 27 whose difference cancels it, and from step 28 on equal words are added to equal states, so the states and the feed-forward are equal.
  - 47,116 of 47,116 (200 trials) and 8,517 of 8,517 (36 trials) on real program states with the target set.
  - Negative control (bit 30 of register h): 0 in both.
- P3: landing events of distinct pairs are independent (declared). Pairs of one batch share the generator words except the retried word; after the shift no compression step is shared, and each trial is one batch of 256 lanes, so the per-trial dispersion tests the within-batch dependence. Lane-keeping dispersion over 200 batches: variance 17.08 vs binomial 18.78 (ratio 0.909), the model declared in H-kept-pair-yield. Organizer-run evidence: the per-trial landing_k8 counts of the trusted report (one batch of 256 lanes per trial) form the dispersion sample; under P3 their variance equals their mean.
  - Shifted pairs over the 4,200 second-machine trials whose per-trial outputs were retained (1,016,296 pairs; the other 504 kept only totals, k=8 508 vs 476.2 expected): mean 0.9548 vs 0.9452 expected, variance 0.9446, dispersion chi-square 4,197.8 vs 4,199 +- 91.6 (no clustering); this program's 200 trials alone: chi-square 193.7 vs 199 +- 19.9; the shipped program over 20,000 trials: kept-per-batch variance 18.73 vs binomial 18.70 (ratio 1.001).
  - VOL40 batch test of the shared generator part: 64 batches x 512 pairs, dispersion chi-square 65.0 vs 64 +- 11.3.

## 4. Ledger
- Fixed batch count: B = ceil(N / (206 x (1 - 0.001))) batches, N = ln(1/0.61) x 2^256 kept pairs. Every batch is charged at the declared generation budget 110,000 plus recognition of all 256 lanes (12,900 each = 3,302,400), whether a lane is kept or not and whether the batch is kept or discarded: T = B x (110,000 + 256 x 12,900) x 4 / 2980 + 4 + 2^28.2, a deterministic total-work bound. Per kept pair this is (110,000 + 3,302,400) / 206 = 16,565.049 word operations, x 4 loads/stores = 66,260.2, x 1/(1 - 0.001) = 66,326.5 charged operations = 2^4.47620 units. The shipped program runs the per-lane block only on kept lanes, so its executed work is below this charge.
- Discard rate: measured 0 of 200 batches (none under the floor, none at the budget, no hard-check failure; every failed check discards the batch and is in this count); over the 20,000 fresh-seed batches of the shipped program: 0 discarded (none under the floor, none at the budget, no hard-check failure). The declared per-batch discard probability is p <= 2e-4 (above the one-sided Clopper-Pearson 95% upper bound 1.50e-04 of 0 in 20,000); the declared fraction 0.001 is 5 times p; with B about 2^247.3 independent batches, Pr[more than 0.001 B discarded] < exp(-B x D(0.001 || 2e-4)) < 2^-1000 (D = 0.00081 nats per batch), included in the 0.39.
- T = N x 2^4.47620 + 4 x (pairs found).
- log2 N = 256 + log2(ln(1/0.61)) = 254.98345; log2 T = 259.45965 (exact 259.45964969, rounded up to five decimals).
- Success: under P1-P3 the probability is at least 1 - exp(-ln(1/0.61)) = 0.39. The run stops at the first found pair; its verification (4 reduced compressions) and the preprocessing 2^28.2 are added to T; neither changes the rounded exponent.
- Hard-asserted checks (as VOL40 v6): on every organizer trial the shipped program asserts, and fails the trial otherwise: schedule control = kept (40-word and shifted 41-word); sliced control = kept (J26 and J27); forced-target tail = kept and negative control = 0 (shifted 27..40 and unshifted 26..39); kept >= 206; generation within its budget 110,000; every one of the 256 J27 junction-difference bits matches the target bit for kept/2 +- 6 sqrt(kept)/2 lanes (per-bit uniformity, the base of P1); landing_k4 <= kept/16 + 6 sqrt(kept/16). A failed trial returns null messages and reports checks_failed and checks_mask (bits 1, 2, 4, 8, 16, 32, 64 in the order above), so the organizer's byte-identical rerun carries these checks.

## 5. Preprocessing and memory
- Preprocessing ledger (lists as VOL40): each of the 7 lists (W4 row 19; W5 row 20; W6 row 21; W7 row 22; W12 row 27; W17 targets; W25 targets) is built by enumerating all 2^32 candidate words against its condition at <= 24 word operations each: 2^32 x 24 / 2980 = 2^25.04 compressions per list, 7 lists = 2^27.86; the W8 and W10 subsets (2^12 each) cost 422 compressions; total 2^27.86, declared 2^28.2 (rounded up).
- The online memory, complete under the model: list subsets 357,408 + program code 51,021 + sliced working state 197,632 + word-level working state 5,704 + current messages 128 = 611,893 bytes = 2^19.23 (exponent rounded up; term 0).
  - Sliced state (one sliced word = 32 bit-planes x 256 lanes = 1,024 bytes): the VOL40 inventory, 110 (schedule words of member 1, 24; of member 2, 24; member-2 schedule with the retried word, 24; both states after the counted window, 16; hoisted batch constants, 4; retried-word candidates, 2; retry schedule words, 4; lane masks and kept word, 4; temporaries in add/sigma (upper bound), 8); plus the shift: shifted message and schedule words of member 1 to word 26, 27; of member 2, 27; both shifted states, 16; early-abort words (two T2 values and the compare word), 3; register-a and register-e check words, 2; junction difference, 8 = 83; total 193 sliced words = 197,632 bytes.
  - Word-level state: the VOL40 inventory, 232 words; plus the per-lane control vectors of the unshifted and shifted junction (3 x 256), the per-bit tallies (256), and one lane's shifted words (shifted messages 32, shifted schedules 82, shifted states and snapshot 32, junction difference 8, tail states 16 = 170) = 1,194; total 1,426 words = 5,704 bytes.
  - Lists: L17_r19_W4 32,768 + L17_r20_W5 512 + L17_r21_W6 176 + L17_r22_W7 16 + L17_r27_W12 28,160 + L17_W17_joint(2^15) 131,072 + L17_r27_W25(2^15) 131,072 + W8 subset 16,384 + small tables = 357,408 (as VOL40). Random words per pair: W10, W12 index draws, each charged as one word op.

## 6. Declared premises
- P1-uniform-junction, P2-tail-induced, P3-independence and H-kept-pair-yield, with the evidence above.
- Not measured: bits beyond 16 jointly on shifted pairs (the shipped program over 20,000 trials: k24 0 vs 0.28 expected, k32 0 vs 0.001) and beyond 32 on the unshifted generator (P1, the full-width rate is the declared premise); a naturally landed pair (expected only after ~2^256 pairs; P2 rests on the structural argument, not on natural samples).

## 7. Measurement logs (inlined; every declared bound in Sections 1-5 rounds up)
### 200 organizer-format trials of v41-shift-01 (generator and shift as shipped; per-lane recognition then outside ops_used)
```
trials 200, lanes 256, kept 47116 (per trial min 223, mean 235.58, max 247, variance 17.08), generation ops_used 103062..103683, cap_hit 0
schedule control 47116/47116, sliced control 47116/47116, tail 47116/47116, negative control 0
shifted landing k8 175 (expected 184.0), k16 0 (expected 0.72)
```
### 36 organizer-format trials (TRY 19, early abort J-4)
```
trials 36 pairs 8517 k8 33 k16 0 tail 8517 neg 0
```
### Dispersion of per-trial k=8 landing
```
S113 all 21 shift packages, 4,200 trials: trials 4200, pairs 1016296, k8 total 4010, per-trial mean 0.9548 vs expected 0.9452, variance 0.9446 (Poisson: 0.9452), dispersion chi2 4197.8 vs 4199 +- 91.6
S113 R41 only, 200 trials: trials 200, pairs 47116, k8 total 175, per-trial mean 0.8750 vs expected 0.9202, variance 0.8894 (Poisson: 0.9202), dispersion chi2 193.7 vs 199 +- 19.9
```
### Shipped program, one trial (seed 1)
```
{"kept": 243, "schedule_control_pass": 243, "sliced_control_pass": 243, "ops_used": 3237818, "cap_hit": 0, "landing_k8": 1, "landing_k16": 0, "landing_k24": 0, "landing_k32": 0, "best_lead_bits": 9, "bit_match_min": 99, "bit_match_max": 145, "checks_failed": 0, "checks_mask": 0, "tail_collide": 243, "neg_control_collide": 0}
```
ops_used = 103,118 generation + 243 x 12,900.
### Shipped program, 20,000 fresh-seed trials
```
trials 20000 pairs 4713729 k8 18485 k16 86 k24 0 k32 0 checks_failed_total 0 failed_trials 0 masks {0: 20000} kept_min 215 kept_mean 235.69 kept_max 250 gen_min 102933 gen_max 103894 bitmatch_min 80 bitmatch_max 157
```
