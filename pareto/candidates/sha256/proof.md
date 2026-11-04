# VOL40: a counted cost bound for a 40-step SHA-256 ordinary collision

Score (collision-frontier-v5): time_log2 = 255.45258 target-compressions. Memory is reported separately: 2^18.98 bytes by construction (complete under the model; term max(0, log2-20) = 0).

## 1. Target and prices
- Target: two distinct messages under the standard IV, the first 40 steps, standard padding and feed-forward, all 256 output bits equal. Each message is one 64-byte data block followed by the common SHA-256 padding block; the two data blocks give an equal chaining value, so the equal padding block preserves the collision and the full messages collide.
- Prices: one 40-step target compression is one unit. Every other primitive word operation (add, sub, xor, and, or, not, shift, rotate, compare, random word, table index) costs 1/C, with C = 2896.

## 2. Head (experiment v40-headtail-01)
- The shipped program (v7/v7e) outputs message pairs whose expanded difference follows the msb17 body on all 40 words. The v5 word-level generator is a cross-check only.
- It works bit-sliced on 256 lanes; a gate on 256 lanes counts as one word operation, the accounting of the board's R40 entry df1f1cd1.
- Each kept pair costs 4,008.9 charged operations (2^0.46913 units): 1002.216 word operations (220.216 generation + 782 junction recognition), each charged with its two operand loads and one result store (4,008.9), times 1.000000000356 for discarded low-yield batches (Section 4). Each word operation is charged together with its two operand loads and one result store (the data-movement upper bound of a register-free RAM program under collision-frontier-v5), so the charged total before the yield factor is 1002.216 x 4 = 4,008.9 operations per kept pair.
- Derivation of the count (auditable from the organizer report and the source):
  - generation per batch: ops_used minus 782 x kept, as reported per trial; measured over 20,000 batches of 256 lanes: minimum 38,064, maximum 38,758; the ledger charges the maximum as the per-batch budget;
  - kept lanes per batch: measured mean 216.5, minimum 193 (per-lane rate 0.846); the ledger uses the floor 176 (premise H-kept-pair-yield), so generation per kept pair = 38,758 / 176 = 220.216;
  - recognition per kept lane, v5 primitives: schedule words 16..26 of both members, 11 x 21 x 2 = 462; steps 23..26 of both members, 4 x 38 x 2 = 304; 8-word compare 16; total 782 (one schedule word = two sigma functions of 9 primitives and 3 additions; one step = 38 primitives: two Sigma functions of 11, Ch 4, Maj 5, 7 additions). The program adds 782 to ops_used for every kept lane;
  - the 2,048-lane development run reported 176 generation operations per kept pair at a higher kept count (Section 7, v7e_head_run.txt); the shipped 256-lane program is charged at its own measured maximum and floor above. The program's control loop rebuilds each kept lane's schedule and runs steps 23..26 of both members to confirm the landing; that recognition is mandatory and is charged here by exact count, not left out of the total.
- A found pair is checked by 4 reduced verification compressions (data block and padding block of each of the two messages), charged as one unit each (4 units per found pair), and written out.
- Evidence: v7e_head_run.txt (Section 7) (3,498 of 4,096 lanes kept; schedule control and sliced-vs-word check 3,498 of 3,498). The v5 word-level run (1,447 ops, 13 random words per pair) is kept as a cross-check.
- The program counts every operation, including the per-kept-lane recognition, and halts generation before the next retry would pass its hard budget (cap_hit records a halt).
- Control: the full 40-word schedule check passed for 4,096 of 4,096 pairs.
- Evidence: v5_head_run_4096.txt (Section 7).

## 3. Landing and tail (experiment v40-headtail-01)
- P1: the J26 XOR difference of a generated pair equals the target with probability 2^-256 (a declared heuristic; the full-width rate is the premise, not a measured fact). Organizer-run evidence: each trial reports landing_k8, landing_k16, landing_k24, landing_k32 and best_lead_bits over its kept pairs (expected kept x 2^-k); the organizer's own seeds are the holdout.
  - Measured on 2^36 head-induced states, k-bit match: 2^-8.00, 2^-16.00, 2^-23.98, 2^-31.83 for k = 8, 16, 24, 32.
  - The shipped program itself, 20,000 organizer-format trials on a second machine (4,331,098 pairs): k=8 landing 16,883 (expected 16,918.4), k=16 landing 82 (expected 66.1), best match 22 bits; per-trial k=8 counts: mean 0.8441 vs 0.8459 expected, variance 0.8488, dispersion chi-square 20,067 vs 19,999 +- 200 (no clustering); tail collisions 4,331,098 of 4,331,098; operation cap never hit.
  - Per-bit bias at most 0.00001.
- P2: a pair at the target collides after step 40 with probability 1, by construction. Differential table of the body (schedule difference of the two members, from the program constants): words 16, 18-24 and 27-39 have difference 0; words 17, 25 and 26 are the only lit schedule words. The target is the state difference (0,0,0,0,0,0,0,0x80000000) at the junction after step 25; step 26 adds the lit word 26 whose difference cancels it, and from step 27 on equal words are added to equal states, so the states and the feed-forward are equal. The same two literal 16-word messages in the source reproduce the table.
  - 5,000 of 5,000 on head-induced states.
  - Negative control: 0 of 2,000.
- P3: landing events of distinct pairs are independent (declared). Lane-keeping dispersion over 20,000 batches: variance 33.27 vs binomial 33.37 (ratio 0.997), the model declared in H-kept-pair-yield. Organizer-run evidence: the per-trial landing_k8 counts of the trusted report (one batch of 256 lanes per trial) form the dispersion sample; under P3 their variance equals their mean.
  - Correlation within batches -0.0009, across batches -0.0010, noise 0.0022.
  - v7c (batch shares steps 0..12): 64 batches x 512 pairs, per-batch k=8 landing counts mean 2.094 vs 2.000, variance 2.055, dispersion chi-square 65.0 vs 64 +- 11.3 (no clustering); per-bit chi-square 259.3 vs 256 +- 22.6.
  - Evidence: DEPENDENCE.md (Section 7).

## 4. Ledger
- N = ln(1/0.61) x 2^256 kept pairs, produced from N/176 batches times 1/(1 - 6.44e-11): a batch with fewer than 176 kept lanes is discarded and its budget 38,758 and its recognition work (at most 175 x 782) are charged. Factor = (1 + 6.44e-11 x (1 + 175 x 782 / 38,758)) / (1 - 6.44e-11) = 1.000000000356; it changes log2 T by less than 1e-9 and is included in the rounded figure.
- T = N x 2^0.46913 + 4 x (pairs found).
- log2 T = 255.45258 (exact 255.45257982, rounded up).
- Success: under P1-P3 the probability is at least 1 - exp(-ln(1/0.61)) = 0.39. The run stops at the first found pair; its verification (4 reduced compressions) and the preprocessing 2^28.21 are added to T; neither changes the rounded exponent.
- Hard-asserted checks (v6): on every organizer trial the shipped program asserts, and fails the trial otherwise: schedule control = kept; sliced control = kept; forced-target tail = kept and negative control = 0; kept >= 176; generation within its budget; every one of the 256 junction-difference bits matches the target bit for kept/2 +- 6 sqrt(kept)/2 lanes (per-bit uniformity, the base of P1); landing_k4 <= kept/16 + 6 sqrt(kept/16). A failed trial returns null messages, so the organizer's byte-identical rerun carries these checks.

## 5. Preprocessing and memory
- Preprocessing ledger: each of the 7 lists (W4 row 19; W5 row 20; W6 row 21; W7 row 22; W12 row 27; W17 targets; W25 targets) is built by enumerating all 2^32 candidate words against its condition at <= 24 word operations each: 2^32 x 24 / 2896 = 2^25.09 compressions per list, 7 lists = 2^27.89; the W8 and W10 subsets (2^12 each) cost 422 compressions; total 2^27.89, declared 2^28.21 (rounded up).
- The online memory, complete under the model: list subsets 357,408 + program code 45,512 + sliced working state 112,640 + word-level working state 928 + current messages 128 = 516,616 bytes = 2^18.98 (exponent rounded up; term 0). Live-state inventory of the shipped program (one sliced word = 32 bit-planes x 256 lanes = 1,024 bytes): schedule words of member 1, 24; of member 2, 24; member-2 schedule with the retried word, 24; both states after the counted window, 16; hoisted batch constants, 4; retried-word candidates, 2; retry schedule words, 4; lane masks and kept word, 4; temporaries in add/sigma (upper bound), 8 = 110 sliced words = 112,640 bytes. Word-level: message words of both members 32, states after step 12 16, word-level schedules 48, one lane's control copies 112, masks 24 = 232 words = 928 bytes. Lists: L17_r19_W4 32,768 + L17_r20_W5 512 + L17_r21_W6 176 + L17_r22_W7 16 + L17_r27_W12 28,160 + L17_W17_joint(2^15) 131,072 + L17_r27_W25(2^15) 131,072 + W8 subset 16,384 + small tables = 357,408. Random words per pair: W10, W12 index draws, each charged as one word op.
- Evidence: MEMORY.md (Section 7) and RANDOM_WORDS.md (Section 7).

## 6. Declared premises
- P1-uniform-junction, P2-tail-induced, P3-independence and H-kept-pair-yield, with the evidence above.
- Not measured: bits beyond 32 jointly (P1, the full-width rate is the declared premise); a naturally landed pair (expected only after ~2^256 pairs; P2 rests on the structural argument, not on natural samples).

## 7. Measurement logs (inlined; the files named above, verbatim - their own rounding is kept; every declared bound in Sections 1-5 rounds up)
### v7e_head_run.txt
```
collisions found 0 (collisions.txt); VERIFY compressions 0
kept 3498 of 4096 lanes (TRY 14); CONTROL full schedule 3498/3498; sliced step-23 a/e diff == word level 3498/3498
per kept pair: gates 170 + batch word ops 4.8 + per-lane ops 1 = 176 ops
  C = 2352: head 0.0747 = 2^-3.74 -> total 251.24
  C = 2896: head 0.0607 = 2^-4.04 -> total 250.94
  UNIFORMITY batch 0: 227 kept, distinct J26 227, fixed bits 0, mean weight 128.2, max per-bit |p-0.5| 0.099 (3-sigma 0.100)
  UNIFORMITY batch 1: 223 kept, distinct J26 223, fixed bits 0, mean weight 128.7, max per-bit |p-0.5| 0.083 (3-sigma 0.100)
  UNIFORMITY batch 2: 218 kept, distinct J26 218, fixed bits 0, mean weight 127.6, max per-bit |p-0.5| 0.133 (3-sigma 0.102)
  UNIFORMITY batch 3: 224 kept, distinct J26 224, fixed bits 0, mean weight 127.6, max per-bit |p-0.5| 0.103 (3-sigma 0.100)
  UNIFORMITY batch 4: 226 kept, distinct J26 226, fixed bits 0, mean weight 128.9, max per-bit |p-0.5| 0.115 (3-sigma 0.100)
  UNIFORMITY batch 5: 217 kept, distinct J26 217, fixed bits 0, mean weight 128.3, max per-bit |p-0.5| 0.150 (3-sigma 0.102)
  UNIFORMITY batch 6: 220 kept, distinct J26 220, fixed bits 0, mean weight 128.8, max per-bit |p-0.5| 0.095 (3-sigma 0.101)
  UNIFORMITY batch 7: 212 kept, distinct J26 212, fixed bits 0, mean weight 128.0, max per-bit |p-0.5| 0.094 (3-sigma 0.103)
  UNIFORMITY batch 8: 222 kept, distinct J26 222, fixed bits 0, mean weight 127.6, max per-bit |p-0.5| 0.090 (3-sigma 0.101)
  UNIFORMITY batch 9: 212 kept, distinct J26 212, fixed bits 0, mean weight 127.4, max per-bit |p-0.5| 0.085 (3-sigma 0.103)
  UNIFORMITY batch 10: 219 kept, distinct J26 219, fixed bits 0, mean weight 127.8, max per-bit |p-0.5| 0.098 (3-sigma 0.101)
  UNIFORMITY batch 11: 211 kept, distinct J26 211, fixed bits 0, mean weight 128.2, max per-bit |p-0.5| 0.107 (3-sigma 0.103)
  UNIFORMITY batch 12: 223 kept, distinct J26 223, fixed bits 0, mean weight 127.5, max per-bit |p-0.5| 0.110 (3-sigma 0.100)
  UNIFORMITY batch 13: 217 kept, distinct J26 217, fixed bits 0, mean weight 127.7, max per-bit |p-0.5| 0.122 (3-sigma 0.102)
  UNIFORMITY batch 14: 215 kept, distinct J26 215, fixed bits 0, mean weight 128.7, max per-bit |p-0.5| 0.105 (3-sigma 0.102)
  UNIFORMITY batch 15: 212 kept, distinct J26 212, fixed bits 0, mean weight 127.5, max per-bit |p-0.5| 0.085 (3-sigma 0.103)
```
### v5_head_run_4096.txt
```
pairs 4096; CONTROL full 40-word schedule check 4096/4096; J26 full-target hits 0 (expected ~3.5e-74)
ops per pair 1447 = 0.615 compressions (2352 unit) = 2^-0.70; board unit 2896: 2^-1.00
volume total = head + 256 - 1.02 = 254.28 (2352) / 253.98 (2896)
random 32-bit words per pair 13.00; preprocessing (W8/W10 subsets) 993510 ops = 422 compressions
list memory by construction: 89136 words = 356544 bytes = 2^18.44
```
### MEMORY.md
```
# MEMORY.md: peak memory of the v5 head generator BY CONSTRUCTION (ruling F3-memory-is-sample-maximum)

Kepler, 11-03 23:5x. These are the data structures the algorithm holds, each counted as 32-bit words x 4 bytes. This is not a measured process maximum. The interpreter's own overhead is not part of the algorithm and is not counted.

## Lists (fixed tables, loaded once)

| table | content | entries | bytes |
|---|---|---|---|
| L17_r19_W4.txt | W4 values meeting the row-19 s0 condition | 8,192 | 32,768 |
| L17_r20_W5.txt | W5, row 20 | 128 | 512 |
| L17_r21_W6.txt | W6, row 21 | 44 | 176 |
| L17_r22_W7.txt | W7, row 22 | 4 | 16 |
| L17_r27_W12.txt | W12, row 27 | 7,040 | 28,160 |
| L17_W17_joint.txt (first 2^15) | W17 targets | 32,768 | 131,072 |
| L17_r27_W25.txt (first 2^15) | W25 targets | 32,768 | 131,072 |
| W8 subset | 2^12 s0-condition solutions | 4,096 | 16,384 |
| W10 subset | 2^12 s0-condition solutions | 4,096 | 16,384 |
| **total lists** | | **89,136 words** | **356,544 B = 2^18.44** |

The table above matches what `v5_head.py` prints: "list memory by construction: 89136 words = 356544 bytes".

## Working state

| item | words |
|---|---|
| batch base W0..W15 | 16 |
| batch state after step 9, both members | 16 |
| per-pair W[0..39], both members | 80 |
| per-pair working state, both members | 16 |
| s1 inverse matrix | 32 |
| SHA-256 round constants | 48 |
| J26 target | 8 |
| **total** | **216 words = 864 B** |

## Peak

**357,408 B = 2^18.45**, below 2^20, so the memory term max(0, mem_log2 - 20) is 0. Nothing grows with the number of pairs, because the pairs are streamed and tested one at a time.

## Before v5

The 150,994,944 B L17_W17_joint.txt (2^27.2 B) is no longer held.

- That file is truncated at 2^24 of the 2^26.0 solutions, because siglist_gpu writes at most 2^24 lines.
- Any 2^15 of those solutions serve as W17 targets.
- The pair space stays far above 2^257: about 358 free bits per pair.

## Margin

The margin to 2^20 is 691 KB. Code size and the runtime are not algorithm memory under the word-RAM model. If the filing rule counts them, the margin is still about 0.7 MB.
```
### RANDOM_WORDS.md
```
# RANDOM_WORDS.md: random 32-bit words per accepted pair (ruling F5-random-block-generation-omitted)

Kepler, 11-03 23:5x. Counted by `v5_head.py` (the `RANDOM` counter). Each random word, and each list index draw, is also charged as 1 word op in the op counter.

## Per pair

| draw | words | note |
|---|---|---|
| W10 (index into its 2^12 subset) | 1 | |
| W12 (index into L17_r27_W12) | 1 | |
| W14 | 1 | |
| W13, first draw | 1 | |
| W13, redraws in the row-28 loop | 6.9 average | measured mean tries 7.9-8.0 |
| W17 target (index) | 1 | |
| W25 target (index) | 1 | |
| batch share, amortized over B = 1024 | 21 / 1024 = 0.02 | W0..W15 (16) and the indices for W4..W8 (5) |
| **total** | **13.00** | measured by v5_head.py over 4096 pairs |

## Preprocessing (once)

- The W8 and W10 subsets come from rejection sampling: about 8 x 4096 random words each, so about 66k words in all.
- That costs 993,510 ops = 422 compressions, as v5_head.py prints.

## Pairs, all accepted

- Acceptance is 100% by construction: the full 40-word schedule check passes on 4096 / 4096 pairs.
- So there are no rejected-attempt draws to charge.

## In the op count

Random words are already part of the **1,447 ops per pair** = 2^-0.70 compressions (2352 unit). The volume total is therefore **254.28** (2352 unit) or **253.98** (2896 unit).
```
### DEPENDENCE.md
```
# DEPENDENCE.md: junction landing across accepted heads (ruling 39f70726, F5-independence / EX-F4)

Kepler, 11-03 23:5x box time. Produced by `v5_head.py --dep 64 256 4`. Every number below was MEASURED.

## Setup

- Pairs come from the v5 generator, in batches. The pairs in one batch share W0..W9 and the both-member state after step 9.
- There is no first block: the construction runs from the standard IV, so every head shares the "first block" (the IV).
- **Landing indicator:** the J26 XOR difference matches the J26 target on the first k = 4 bits of register a. k = 4 is small so the counts give statistical power.

## Results

| quantity | value |
|---|---|
| pairs | 16,384 (64 batches x 256) |
| landing rate, k = 4 | 0.06152 (uniform model 2^-4 = 0.06250) |
| correlation of landing, two pairs in the SAME batch | -0.0023 |
| correlation of landing, two pairs in DIFFERENT batches | -0.0054 |
| noise of these estimates (pool of 16,384 pairs) | about 1/sqrt(16384) = 0.008 |

## Further evidence

These are measured on the same generator, as recorded in FINDINGS_2026-11-03_R40_TARGET.md.

**Uniformity within batches of 1024** (`junc17e.py`, 3 batches):

- J26 differences distinct: 1024 / 1024 in every batch;
- fixed bits: 0;
- mean weight: 127.8-128.2;
- maximum per-bit |p - 0.5|: 0.043-0.048, against a 3-sigma noise of 0.047.

**k-bit landing on the GPU** (`vp5gpu.cu`, 2^36 pairs, batches of 1024):

| k | landing rate | uniform model |
|---|---|---|
| 8 | 2^-8.00 | 2^-8 |
| 16 | 2^-16.00 | 2^-16 |
| 24 | 2^-23.98 | 2^-24 |
| 32 | 2^-31.83 (18 hits, 16 expected) | 2^-32 |

- Per-bit maximum |p - 0.5|: 0.00001, against a noise of 0.00001.

## Reading

- Landing is uncorrelated between pairs that share a batch, and between pairs in different batches, to within noise at this sample size.
- The k-bit rates follow 2^-k out to k = 32 under batching.
- **Not measured: k = 256 itself.** A full landing has probability about 2^-256, so the claim rests on the uniform-landing premise, measured up to k = 32. Declare it as an assumption.
```
