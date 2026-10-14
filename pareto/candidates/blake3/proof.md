# blake3-r3: bit-sliced distinguished-point collision search, time_log2 124.91252, memory below 2^20 bytes

## 1. Claim

- Target: blake3-r3-prefix-v1, an ordinary collision of the complete 256-bit digest (standard IV, unkeyed, rounds 0 to 2 in every compression, standard chunk, flags and root output).
- Output: two distinct 64-byte messages with equal digests.
- Time: at most N = 25,540,762,476,809,282,676,729,775,392,181,909,527,814 word operations, that is N / 638 target compressions, time_log2 = 124.91252 (Section 6, integer certificate in 6.3).
- Memory: at most 1,004,023 bytes including code, registers, the table and all working state, memory_log2_bytes = 20 (Section 4.3), 44,553 bytes below 2^20.
- Pareto cost: normalizedTimeMemoryLog2 = 124.91252 + max(0, 20 - 20) = 124.91252 at 3 rounds.
- Success probability: at least 0.3905 for one attempt, over the algorithm's fresh coins, under the declared premise H_rand (Section 7). The bound uses only the first repeat and a detection window; every tail term is an exact inequality (no Gamma or Poisson substitution). No amplification, no advice; preprocessing is the generation of the code (Section 6.2).
- Machine convention: a 256-bit word RAM with a declared file of 1,024 registers whose bytes are counted as memory (premise H_reg, Section 4.1). Smaller files are priced in Section 10.
- The required `baseline_improved` identifier names the organizer's nominal entry. It is a nominal reference, not an established attack or baseline; nothing here depends on it.

## 2. Messages and the chain function

- A point is a 256-bit value x. Its message is M(x) = 0^32 || LE32(x): 32 zero bytes followed by the 32 little-endian bytes of x, 64 bytes in all. M is injective; two different points give two different messages; every message has bit length 512 < 2^64.
- A 64-byte message is one chunk of one block. Its hash is the first 32 bytes of the root compression with chaining value IV, block words w0..w15 (little-endian 32-bit words of M(x), so w0..w7 = 0 and w8..w15 are the words of x), counter 0, block length 64 and flags CHUNK_START | CHUNK_END | ROOT = 11. The compression runs rounds 0, 1, 2 (eight G calls each, the message permutation between rounds) and outputs v[i] XOR v[i+8], i = 0..7. No parent node or further compression occurs.
- f(x) is that digest read as a little-endian 256-bit value. If x != x' and f(x) = f(x'), M(x) and M(x') are distinct messages with equal complete digests: an ordinary collision of the target.
- The search walks g(x) = f(x) XOR q for a fixed 256-bit mask q (Section 3.4). g(x) = g(x') if and only if f(x) = f(x').

## 3. The bit-sliced chain step

### 3.1 Representation

- A batch is 256 trails. Plane (word, bit) is one 256-bit word whose bit t is that bit for trail t. The 256 input planes are the bits of the current points; the 256 digest planes are the next points.
- Rotations rename planes and cost nothing. A plane that is the same constant for every trail is folded and never stored (the IV, the counter, the block length, the flags and the zero words w0..w7 are constants).
- NOT is folded into a polarity: every plane is held physically as its logical value XOR a known bit p.

### 3.2 Gates

Three operations on registers, each one word operation: XOR, AND, OR. For logical a = A xor pa and b = B xor pb:

- a XOR b = (A XOR B) xor (pa xor pb): one XOR.
- a AND b: one AND if pa = pb = 0, one OR with output polarity 1 if pa = pb = 1, otherwise two operations (A AND NOT B = A XOR (A AND B)).
- Constants and equal operands are folded; every binary operation on the same pair of physical words is emitted once.

### 3.3 Additions

Each 32-bit addition is a ripple of full adders, bit 31 without a carry out. For bit i with inputs a, b and carry c, the generator picks a pivot p among {a, b, c} such that the other two, x and y, have equal polarity (two of three polarities always agree; constants are folded first):

- u = x XOR p, sum = u XOR y,
- carry = ((u AND (y XOR p)) XOR p) = maj(x, y, p).

u and y XOR p have equal polarity, so the AND is one operation and every bit costs five operations (fewer when an input is constant). This is the known minimal size 5 of a full adder over AND/OR/XOR; the pivot choice removes the extra operation that a fixed formula pays when the polarities of its two AND inputs differ.

G is the standard function: a = a + b + mx; d = (d XOR a) >>> 16; c = c + d; b = (b XOR c) >>> 12; a = a + b + my; d = (d XOR a) >>> 8; c = c + d; b = (b XOR c) >>> 7. Additions of the zero words w0..w7 fold away; the first column step of round 0 is entirely constant.

### 3.4 Chain feed and the mask q

Digest plane j is written into register j, which held input plane j. The program is generated for input polarity 0; the polarity of digest plane j is a fixed bit q_j (129 of the 256 are 1). The physical digest planes are taken as the next point as they are, so the walk is g(x) = f(x) XOR q with q = sum q_j 2^j, and no NOT is executed. Distinguished points (Section 5) and the table use physical values, that is points of g.

### 3.5 Registers

Input plane j and digest plane j live in register j (j < 256). The remaining values are allocated to registers 256 to 1,023 in program order: a register is freed after the last use of its value. The peak is 771 registers; the main loop has no loads or stores.

### 3.6 Ledger of one step

The generator is the program experiments/b3r3_rho.py (`--ledger`). One step of 256 trails is:

| operation | count |
| --- | ---: |
| XOR | 14,265 |
| AND | 1,030 |
| OR | 2,060 |
| **total** | **17,355** |

That is 67.79 word operations per evaluation of f, against the reference cost 638 of one compression: 0.10626 target compressions per evaluation.

### 3.7 Correctness of the step

- `--selftest 512` executes the generated straight line on 512 uniform points and four chained steps each, against an independent plain implementation of the three-round compression in the same file, which matches the organizer reference verifier/blake3.py blake3(M, rounds=3) on random messages. Result: 0 differences in 2,048 chained evaluations.
- The organizer experiment proj-w256 (Section 9) runs the same straight line at full width for eight chained steps from random planes; every returned pair is recomputed by the organizer's trusted digest.

## 4. Machine convention and memory

### 4.1 Machine (premise H_reg)

The machine is the cost model's 256-bit word RAM: every load, store, add, subtract, AND, OR, XOR, NOT, shift, compare, branch and random word is one operation, and the selected-round compression is one unit (638 operations). This entry declares a register file of 1,024 registers of 256 bits; register operands cost nothing beyond the operation, and the file's 32,768 bytes are counted as memory. The profile and cost model fix no register count; the same convention is used by the pareto blake3 entry 0a9640ed. Smaller files are priced in Section 10.

### 4.2 Code encoding

The straight line has only register operations without immediates. One instruction is stored in 5 bytes: a 3-bit opcode and three 12-bit register numbers (39 bits). All other code (loop, tests, handlers, cap scan, the recovery and its one-walk compression) is charged 40 bytes per instruction, for at most 4,096 instructions.

### 4.3 Memory map

| region | bytes |
| --- | ---: |
| straight line, 17,355 instructions of 5 bytes | 86,775 |
| other code, at most 4,096 instructions of 40 bytes | 163,840 |
| register file, 1,024 words | 32,768 |
| per lane: start index (8 bytes) and start batch (16 bytes), 256 lanes | 6,144 |
| R, the batch counter, the next index, the stage-1 counter, the entry count, B, q and constants | 256 |
| handler scratch (one copy of 256 planes) | 8,192 |
| recovery state (two compression states and two points) | 2,048 |
| table, 22,000 entries of 32 bytes | 704,000 |
| **total** | **1,004,023** |

1,004,023 <= 1,048,576 = 2^20, so memory_log2_bytes = 20 and the memory term of the cost is 0. The headroom of 44,553 bytes holds 1,113 more 40-byte instructions beyond the 4,096 charged for the non-straight-line code, whose parts are listed with their operation counts in Sections 5.2 to 5.6.

## 5. The search

Parameters: d = 114 (a point is distinguished when its physical planes 0 to 113 are all zero in its lane, probability p = 2^-114 for a uniform point), L = 2^114, cap = 16L, K = 2^64, table capacity E = 22,000, detection window W = 4.5 L = 93,461,343,453,626,897,313,548,933,925,961,728 batches, B0 = 1,348,330,585,466,577,683,499,105,865,228,069,194 batches, B = B0 + W = 1,441,791,928,920,204,580,812,654,799,154,030,922 batches (about 2^120.1173), Q = 256 B = 369,098,733,803,572,372,688,039,628,583,431,916,032 evaluations; the first n0 = 256 B0 = 345,172,629,879,443,886,975,771,101,498,385,713,664 evaluations are the ones the success bound counts.

### 5.1 Setup

1. Draw one random word R (the cost model's independent uniform random 256-bit word).
2. Trail i starts at s_i = R + i mod 2^256. Lanes 0 to 255 get starts 0 to 255 (the 256 x 256 bits are written into the planes, at most 196,608 + 256 operations), and the next index is 256.
3. Every lane stores its start index and its start batch 0.

### 5.2 Main loop (one batch)

1. The straight line (17,355 operations) replaces the 256 points x by g(x).
2. Stage-1 test: w = OR of planes 0 to 31 (31 operations); compare w with the all-ones word and branch (2). Lane t has bit t of w equal to 0 exactly when its planes 0 to 31 are zero.
3. Loop: add one to the batch counter b, compare with B, branch (3). At b = B the attempt halts with failure.

A batch is 17,391 operations.

### 5.3 Stage-1 handler (when w is not all ones)

v = OR of planes 32 to 113 (81 operations), z = w OR v, compare z with all ones and branch: 84 operations. If z is all ones no lane is distinguished and the loop continues. The attempt halts with failure if the stage-1 handler runs more than S1 = 2 floor(B / 2^24) + 2^20 times.

### 5.4 Distinguished-point handler

For each lane t with bit t of z equal to 0 (a scan of 256 bit positions, 768 operations):

1. The key is the 64 physical bits 114 to 177 of the lane (256 operations).
2. The table is scanned linearly for the key (3 operations per stored entry, at most 66,000).
3. If the key is present: recovery (5.6) with that entry and the current trail (start index, length b - start batch). After the recovery the attempt stops: it outputs the pair if the recovery found one and fails otherwise.
4. If the table holds E entries the attempt halts with failure. Otherwise the entry (key, start index, length) is appended (4 stores).
5. Restart: the lane gets the next index i and the point R + i, written into its 256 planes (about 1,310 operations), and start batch b.

A distinguished-point event costs at most 67,570 operations; there are at most E of them.

### 5.5 Cap scan

Every K = 2^64 batches every lane whose age b - start batch exceeds cap is restarted as in 5.4.5 (at most 336,384 operations per scan). A trail is therefore cut after at most cap + K < 17L evaluations.

### 5.6 Recovery

Given two trails (start s_a, length l_a) and (s_b, l_b) that end at points with the same key, with l_a >= l_b: compute g^(l_a - l_b)(s_a), then step both values together until their images under g are equal; the two values with equal images are returned. Each evaluation of g is one call of the selected-round compression (one unit) plus at most 64 operations (writing the eight words of x and the constant state, reading and joining the eight output words, XOR with q, the comparison and the loop). At most 2(cap + K) calls. When the attempt stops it writes the two 64-byte messages and halts (charged 2^16 operations).

If the two trails reach the same distinguished point and the first trail is not a suffix of the second, the first equal images occur at two distinct values: the merge point of the trails. They are a collision of g, hence of f.

## 6. Time

### 6.1 Ledger

| part | bound | word operations |
| --- | --- | ---: |
| main loop | B batches x 17,391 | 25,074,203,435,851,277,864,912,879,612,087,751,764,502 |
| stage-1 handler | S1 = 171,874,991,526,628,086,663,802,098,660 runs x 84 | 14,437,499,288,236,759,279,759,376,287,440 |
| distinguished-point events | E x (768 + 67,570) | 1,503,436,000 |
| cap scans | (floor(B / 2^64) + 1) x 336,384 | 26,291,671,542,682,371,394,560 |
| recovery, compression calls | 2(cap + K) = 664,613,997,892,457,973,345,391,677,559,275,520 calls x 638 | 424,023,730,655,388,186,994,359,890,282,817,781,760 |
| recovery, other operations | 2(cap + K) x 64 | 42,535,295,865,117,310,294,105,067,363,793,633,280 |
| generation of the straight line (preprocessing) | charged 2^32 | 4,294,967,296 |
| setup | 256 x 256 x 3 + 256 + 512 + 64 | 197,440 |
| output of the pair and halt | charged 2^16 | 65,536 |
| **N** | | **25,540,762,476,809,282,676,729,775,392,181,909,527,814** |

The main loop is 98.17 percent of N, the recovery 1.83 percent; everything else is below 10^-9. The counts of the handlers are upper bounds of their straight-line descriptions in Section 5; the attempt halts (fails) before any count exceeds the number charged here (S1 runs of the stage-1 handler, E distinguished-point events, one recovery).

### 6.2 Preprocessing

The straight line is produced by the generator in experiments/b3r3_rho.py from the IV, the permutation and the rotation amounts. Its work (one generation of about 18,000 symbolic gates, dead-code elimination and allocation) is well below 2^32 word operations, charged in N; preprocessing_log2 = 32 - log2(638) < 23 target compressions is declared as 23.

### 6.3 Certificate

time_log2 = log2(N / 638). The claim 124.91252 is log2(N / 638) rounded up at the fifth decimal: 2^124.91251 * 638 <= N < 2^124.91252 * 638, checked in exact integer arithmetic as 638^100000 * 2^12491251 <= N^100000 < 638^100000 * 2^12491252 (Python big integers, true).

## 7. Success probability

### 7.1 Premise H_rand and the probability space

The coins of the attempt are the word R. H_rand: for the points the search evaluates, the image under g of a point not evaluated before is uniform on 256-bit values and independent of the history of the attempt (all earlier points, images and decisions). Equivalently, the attempt behaves as if g were a uniformly random function on the evaluated points. (g and f differ by the fixed mask q, so this is the same statement for f.) Everything below is a consequence of H_rand and exact counting; no further independence is assumed. In particular, while no repeat has occurred every evaluation is at a fresh point, so its distinguished-point indicator is Bernoulli(p) and independent of the history.

Evaluations are ordered by batch and, within a batch, by lane. A repeat is an evaluation whose image equals a point already in the attempt (an earlier start or an earlier image).

### 7.2 The first repeat

Let tau be the index of the first repeat. Every evaluation before tau is at a fresh point, and the number of points already in the attempt before evaluation i is at least i. Under H_rand, P(evaluation i is not a repeat | no earlier repeat) <= 1 - i/2^256. Hence

P(tau > n0) <= prod_{i < n0} (1 - i/2^256) <= exp(-n0(n0 - 1)/2^257) = 0.5978147.

Evaluations 1 to n0 are the batches 1 to B0, so on the event tau <= n0 the first repeat happens at a batch b <= B0 = B - W.

### 7.3 Detection of the first repeat

Let the first repeat be the evaluation of lane A at point x, with image y = g(x), a point already in the attempt.

1. Robin Hood: y is a start R + j. At most 2^15 starts exist and at most Q images are drawn, so P <= Q 2^15 / 2^256 < 2^-100.
2. Self: y lies on A's own current trail. Lane A's current trail has at most cap + K points, so P(some evaluation hits its own trail) <= Q (cap + K)/2^256 < 2^-12.
3. Otherwise y lies on the trail of another lane-trail, B, with y != start of B; let x' be the predecessor of y on B. Then x != x' (x was fresh before tau and x' was evaluated earlier) and g(x) = g(x') = y. From y on, A and B follow the same path, B being at least one batch ahead, or in the same batch with a lower lane index (evaluations within a batch are ordered by lane, and the distinguished-point handler processes lanes in increasing order, so B's key is stored before A's lookup in either case).

In case 3 let D be the number of steps from y to the first distinguished point on this path. The points after y on the path were evaluated (by B, before tau) or will be evaluated (by B, after tau, while no further repeat occurs) at fresh points, so their distinguished-point indicators are independent Bernoulli(p) under H_rand. The image y is uniform on 256-bit values and independent of the history, so given that it is a point of the attempt it is uniform over those points. For every point of the attempt, the event that its next W path points are all non-distinguished has probability at most (1 - p)^W (indicators already drawn were drawn as independent Bernoulli(p), the others will be); averaging over the uniform choice of y gives P(D > W) <= (1 - p)^W <= e^-4.5 = 0.0111090.

If D <= W, trail B reaches the distinguished point no later than A does and stores its key first (unless the table is full or B is cut), and trail A reaches it at batch b + D <= B, finds the key and runs the recovery, which returns the pair (x, x') because the first trail is not a suffix of the second (case 1 excluded). Trails A and B are not cut if their lengths stay below cap: A's length at the distinguished point is its age at batch b plus D, and B's length is at most its full trail length. A's age is at least 11.5 L only if its last 11.5 L indicators were all non-distinguished, probability at most e^-11.5; B's trail, which contains the uniformly hit point y, is at least 16 L long with probability at most (1 + 16) e^-16 (a uniform point lies on a length-biased trail). Together below 2.22e-5.

A further repeat before the path reaches the distinguished point (B or A hitting a point already in the attempt within the W steps) has probability at most W Q / 2^256 < 3.1e-4. It is counted as a failure, although the merged path would still end at a distinguished point.

### 7.4 Other failure events

| event | bound |
| --- | --- |
| no repeat among the first n0 evaluations (7.2) | 0.5978147 |
| first repeat detected too late, D > W (7.3) | 0.0111090 |
| a further repeat on the path within W (7.3) | 3.1e-4 |
| first repeat on the own trail (7.3) | 2.44e-4 |
| A or B cut before the distinguished point (7.3) | 2.22e-5 |
| table full: more than E - 256 distinguished points among Q fresh evaluations (Binomial(Q, 2^-114), mean 17,771, Chernoff) | below 1e-30 |
| a key match between different distinguished points (64-bit keys, fewer than 2^15 entries and lookups) before the true one | below 2^-36 |
| Robin Hood (7.3) | below 2^-100 |
| the stage-1 handler runs more than S1 times (Binomial(B, at most 256 2^-32), Chernoff) | below 1e-30 |

The success probability is at least 1 - 0.5978147 - 0.0111090 - 0.0003100 - 0.0002441 - 0.0000222 = 0.3905000 >= 0.39; B0 is the least batch count for which this bound reaches 0.3905 (Decimal arithmetic, 80 digits).

## 8. Heuristic premises and their evidence

- H_rand (score-critical) is a premise about one fixed function; it cannot be tested at width 256. If the real pair-collision rate among the evaluated images is (1 - eps) of the random-function rate, the margin 0.3905 - 0.39 covers eps up to 0.0016; a larger eps costs 0.5 log2(1 / (1 - eps)) more bits of time (0.0073 for eps = 0.01). The tail terms of Section 7 are exact consequences of H_rand, not further premises. Evidence: the experiments of Section 9 and the step checks of 3.7.
- H_reg (supporting, cost convention) is the register file of Section 4.1. Its effect is priced in Section 10.

## 9. Experiments

Both experiments are declared in experiments/manifest.json and run the shipped program experiments/b3r3_rho.py, which regenerates the straight line of Section 3 and executes it on 256 trails per batch. The organizer recomputes every returned pair with its trusted digest.

### 9.1 rho-w22

Per trial, one attempt of the search of Section 5 at width 22: points are 22-bit values, the message of a point is M(x) with the upper bits of x zero, planes 22 to 255 are reset to 0 after every step, a point is distinguished when its physical planes 0 and 1 are zero, cap 36, 14 batches (3,584 evaluations), starts R + i from one random word, a dictionary table and the recovery of 5.6 with the plain compression. The trial returns the pair the recovery finds, or two nulls.

- Event: digest-xor-mask on the 22 low digest bits (mask ffff3f followed by 29 zero bytes, expected zero).
- Ideal-function control (our run, not organizer-executed): the same search with the image replaced by an independent uniform 22-bit value per new point succeeds in 2,139 of 4,000 attempts, 0.535 (95 percent interval 0.519 to 0.550).
- Expectation if H_rand holds at this width: about 136.9 of 256 successes, standard deviation 8.0.
- Our runs on random seeds: 838 of 1,500 (0.559) for the target.
- Scope: a reduced-width search with the claimed program and control flow; it tests the program end to end and the rate of detected merges at 22 bits. It does not test 256-bit collision rates or full-scale trail lengths.

### 9.2 proj-w256

Per trial: 256 random planes as starting points (uniform points), eight chained full-width steps of the straight line, and the first pair, in step-major order, of distinct evaluated inputs whose images agree on the 22 low bits. The pair's inputs are recomputed from the trial's random planes with the plain compression and returned.

- Event: digest-xor-mask on the 22 low digest bits (q is fixed, so image agreement under g and digest agreement under f are the same event).
- If the images of the 2,048 distinct evaluated inputs are uniform on 22 bits, a trial succeeds with probability 1 - prod_{i < 2048} (1 - i/2^22) = 0.39337: expectation 100.7 of 256, standard deviation 7.8. Our run: 109 of 256.
- Scope: iterates of the full-width chain, a 22-bit projection, 2,048 points per trial. A success is a partial match, not a collision.

## 10. Sensitivity

- Register file (H_reg). With the same straight line and Belady allocation (furthest next use), loads and stores add 1,128 operations per batch for 512 registers (+0.0907 bit, cost 125.00322), 3,624 for 256 registers (+0.2731, 125.18562) and 9,263 for 64 registers (+0.6160, 125.52852).
- H_rand deficit: Section 8.

## 11. Relation to other entries, credits and literature

- Jbenisek's pareto blake3 entries e479cbbf (125.1087) and 0a9640ed (124.96822) are the earlier points at 3 rounds: the same relation (collision of the digest of 0^32 || x), a generic distinguished-point search and, in 0a9640ed, a bit-sliced 256-lane circuit of 19,022 operations with a declared 1,024-register file. This entry was built independently (program, ledger, experiments and proof are ours) and differs in the step (17,355 operations: the pivot-chosen full adder of 3.3 and the mask walk of 3.4), in the code encoding (5 bytes per straight-line instruction, Section 4.2, which leaves room for a table of 22,000 entries and trails of mean length 2^114) and in the success argument (first repeat and detection window, Section 7). Credit for the relation, the bit-sliced direction and the register-file convention.
- Distinguished-point parallel collision search: P. C. van Oorschot and M. J. Wiener, Parallel collision search with cryptanalytic applications, Journal of Cryptology 12 (1999). Rho method: J. M. Pollard (1975). The argument needed here is given in Section 7.
- Minimal full adders over AND/OR/XOR (5 gates) and the ripple-carry adder: standard; Section 3.3 states the variant used.

## 12. Reproduction

- `python3 experiments/b3r3_rho.py --ledger` prints the instruction counts, the register peak (771) and the weight of q (129).
- `python3 experiments/b3r3_rho.py --selftest 512` checks the straight line against the plain three-round compression.
- `python3 experiments/b3r3_rho.py --stats 256` runs both experiments locally on random seeds and the ideal-function control.
- The integers of Sections 5 to 7 are produced by a separate reproduction script (Decimal arithmetic) from the constants listed in Sections 5 and 6; the script is a few dozen lines of the formulas stated there.
