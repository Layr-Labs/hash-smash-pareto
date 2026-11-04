# VOL40: a counted cost bound for a 40-step SHA-256 ordinary collision

Score (collision-frontier-v5): time_log2 = 253.38749 target-compressions. Memory is reported separately: 2^18.86 bytes by construction (complete under the model; term max(0, log2-20) = 0).

## 1. Target and prices
- Target: two distinct messages under the standard IV, the first 40 steps, standard padding and feed-forward, all 256 output bits equal. Each message is one 64-byte data block followed by the common SHA-256 padding block; the two data blocks give an equal chaining value, so the equal padding block preserves the collision and the full messages collide.
- Prices: one 40-step target compression is one unit. Every other primitive word operation (add, sub, xor, and, or, not, shift, rotate, compare, random word, table index) costs 1/C, with C = 2896.

## 2. Head (experiment v40-headtail-01)
- The shipped program (v7/v7e) outputs message pairs whose expanded difference follows the msb17 body on all 40 words. The v5 word-level generator is a cross-check only.
- It works bit-sliced on 256 lanes; a gate on 256 lanes counts as one word operation, the accounting of the board's R40 entry df1f1cd1.
- Each kept pair costs 958 counted operations (2^-1.59596 units) = 176 generation + 782 junction recognition. The program's control loop rebuilds each kept lane's schedule and runs steps 23..26 of both members to confirm the landing; that recognition is mandatory and is charged here by exact count, not left out of the total.
- A found pair is checked by 4 reduced verification compressions (data block and padding block of each of the two messages), charged as one unit each (4 units per found pair), and written out.
- Evidence: measurement log v7e_head_run.txt (3,498 of 4,096 lanes kept; schedule control and sliced-vs-word check 3,498 of 3,498). The v5 word-level run (1,447 ops, 13 random words per pair) is kept as a cross-check.
- The program counts every operation and halts before passing its hard cap.
- Control: the full 40-word schedule check passed for 4,096 of 4,096 pairs.
- Evidence: measurement log v5_head_run_4096.txt.

## 3. Landing and tail (experiment v40-headtail-01)
- P1: the J26 XOR difference of a generated pair equals the target with probability 2^-256 (a declared heuristic; the full-width rate is the premise, not a measured fact).
  - Measured on 2^36 head-induced states, k-bit match: 2^-8.00, 2^-16.00, 2^-23.98, 2^-31.83 for k = 8, 16, 24, 32.
  - The shipped program itself, 20,000 organizer-format trials on a second machine (4,331,098 pairs): k=8 landing 16,883 (expected 16,918.4), k=16 landing 82 (expected 66.1), best match 22 bits; per-trial k=8 counts: mean 0.8441 vs 0.8459 expected, variance 0.8488, dispersion chi-square 20,067 vs 19,999 +- 200 (no clustering); tail collisions 4,331,098 of 4,331,098; operation cap never hit.
  - Per-bit bias at most 0.00001.
- P2: a pair at the target collides after step 40 with probability 1, by construction (the schedule difference is silent on the words after the junction and the target cancels the step-26 word difference, so the two computations coincide from the junction on).
  - 5,000 of 5,000 on head-induced states.
  - Negative control: 0 of 2,000.
- P3: landing events of distinct pairs are independent.
  - Correlation within batches -0.0009, across batches -0.0010, noise 0.0022.
  - v7c (batch shares steps 0..12): 64 batches x 512 pairs, per-batch k=8 landing counts mean 2.094 vs 2.000, variance 2.055, dispersion chi-square 65.0 vs 64 +- 11.3 (no clustering); per-bit chi-square 259.3 vs 256 +- 22.6.
  - Evidence: measurement log DEPENDENCE.md and measurement log v5_dep_32_256_4.txt.

## 4. Ledger
- N = ln(1/0.61) x 2^256 kept pairs (every generated pair, kept or not, is charged in the 958-op figure, which is batch operations divided by kept lanes).
- T = N x 2^-1.59596 + 4 x (pairs found).
- log2 T = 253.38749 (exact 253.38748403, rounded up).
- Success: under P1-P3 the probability is at least 1 - exp(-ln(1/0.61)) = 0.39.

## 5. Preprocessing and memory
- Lists are built by exhaustive enumeration of 2^32 words per list condition, 2^28.2 compressions in total. Selecting their subsets costs 422 compressions.
- The online memory, complete under the model: list subsets 357,408 + program code 44,909 + 256-lane working state 73,728 + current messages 128 = 476,173 bytes = 2^18.86 (term 0). Lists: L17_r19_W4 32,768 + L17_r20_W5 512 + L17_r21_W6 176 + L17_r22_W7 16 + L17_r27_W12 28,160 + L17_W17_joint(2^15) 131,072 + L17_r27_W25(2^15) 131,072 + W8 subset 16,384 + small tables = 357,408. Random words per pair: W10, W12 index draws, each charged as one word op.
- Evidence: measurement log MEMORY.md and measurement log RANDOM_WORDS.md.

## 6. Declared premises
- P1-uniform-junction, P2-tail-induced and P3-independence, with the evidence above.
- Not measured: bits beyond 32 jointly (P1, the full-width rate is the declared premise); a naturally landed pair (expected only after ~2^256 pairs; P2 rests on the structural argument, not on natural samples).
