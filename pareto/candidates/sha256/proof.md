# VOL40: a counted cost bound for a 40-step SHA-256 ordinary collision (DRAFT)

Score (collision-frontier-v5): time_log2 = 250.94304 target-compressions. Memory is reported separately: 2^18.45 bytes by construction.

## 1. Target and prices
- Target: two distinct one-block messages under the standard IV, the first 40 steps, standard padding and feed-forward, all 256 output bits equal.
- Prices: one 40-step target compression is one unit. Every other primitive word operation (add, sub, xor, and, or, not, shift, rotate, compare, random word, table index) costs 1/C, with C = 2896.

## 2. Head (experiment v40-headtail-01)
- The v7 generator outputs message pairs whose expanded difference follows the msb17 body on all 40 words.
- It works bit-sliced on 256 lanes; a gate on 256 lanes counts as one word operation, the accounting of the board's R40 entry df1f1cd1.
- Each kept pair costs 176 counted operations (2^-4.04 units).
- A found pair is checked by 2 verification compressions, charged as one unit each (2 units per found pair), and written out.
- Evidence: measurement log v7e_head_run.txt (kept outside the package) (3,498 of 4,096 lanes kept; schedule control and sliced-vs-word check 3,498 of 3,498). The v5 word-level run (1,447 ops, 13 random words per pair) is kept as a cross-check.
- The program counts every operation and halts before passing its hard cap.
- Control: the full 40-word schedule check passed for 4,096 of 4,096 pairs.
- Evidence: measurement log v5_head_run_4096.txt. (kept outside the package)

## 3. Landing and tail (experiment v40-headtail-01)
- P1: the J26 XOR difference of a generated pair equals the target with probability 2^-256.
  - Measured on 2^36 head-induced states, k-bit match: 2^-8.00, 2^-16.00, 2^-23.98, 2^-31.83 for k = 8, 16, 24, 32.
  - The shipped program itself, 20,000 organizer-format trials on a second machine (4,331,098 pairs): k=8 landing 16,883 (expected 16,918.4), k=16 landing 82 (expected 66.1), best match 22 bits; per-trial k=8 counts: mean 0.8441 vs 0.8459 expected, variance 0.8488, dispersion chi-square 20,067 vs 19,999 +- 200 (no clustering); tail collisions 4,331,098 of 4,331,098; operation cap never hit.
  - Per-bit bias at most 0.00001.
- P2: a pair at the target collides after step 40 with probability 1.
  - 5,000 of 5,000 on head-induced states.
  - Negative control: 0 of 2,000.
- P3: landing events of distinct pairs are independent.
  - Correlation within batches -0.0009, across batches -0.0010, noise 0.0022.
  - v7c (batch shares steps 0..12): 64 batches x 512 pairs, per-batch k=8 landing counts mean 2.094 vs 2.000, variance 2.055, dispersion chi-square 65.0 vs 64 +- 11.3 (no clustering); per-bit chi-square 259.3 vs 256 +- 22.6.
  - Evidence: measurement log DEPENDENCE.md (kept outside the package) and measurement log v5_dep_32_256_4.txt. (kept outside the package)

## 4. Ledger
- N = ln(1/0.61) x 2^256 pairs.
- T = N x 2^-4.04 + 2 x (pairs found).
- log2 T = 250.94304 (exact 250.94303381, rounded up).
- Success: under P1-P3 the probability is at least 1 - exp(-ln(1/0.61)) = 0.39.

## 5. Preprocessing and memory
- Lists are built by exhaustive enumeration of 2^32 words per list condition, 2^28.2 compressions in total. Selecting their subsets costs 422 compressions.
- The online memory is the list subsets: 357,408 bytes, by construction.
- Evidence: measurement log MEMORY.md (kept outside the package) and measurement log RANDOM_WORDS.md. (kept outside the package)

## 6. Declared premises
- P1-uniform-junction, P2-tail-induced and P3-independence, with the evidence above.
- Not measured: bits beyond 32 jointly (P1), and naturally landed states (P2: the target was forced).
