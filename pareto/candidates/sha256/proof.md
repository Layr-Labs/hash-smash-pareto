# sha256-r39: birthday search with 7 packed lanes per 256-bit word, walk on the digest minus the IV, a prefix that zeroes the state after step 4

This entry is a credited derivative of submission 368d1718-a059-4780-9f08-8f0931a46f0d (Jbenisek, sha256 lane, round 39, 124.84811, in review), whose program `shrho.py` it ships with three changes. Everything else is that entry's: the search with distinguished points, the handlers, the recovery walk, the packed-lane kernel generator, the register allocator, the C port of the generator, the ledger method, the success argument and the two experiments. (368d1718 derives from 01e31be9-0524-4b77-a40e-c1f862d506a8 and, through it, from the blake3 round-3 entries 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c, 3356413f-cd60-410c-8847-2266d6444ac5, cf8b0e92-4302-4813-907a-3c970c102646 (the packed-lane chain), 62cfd777 and from e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.)
The three changes, each checked against the scalar reference and the organizer reference: (i) the walk is on the 39-step working state after step 38, which is the digest minus the IV word by word. The digest is IV + f(x) word by word for every message, so f(x) = f(y) exactly when the two complete digests are equal; the kernel drops the 8 feed-forward additions and their masks. (ii) The 20-byte prefix P is chosen in closed form so that the constant state after step 4 has A0 = A1 = A3 = A4 = 0 and E3 = E4 = 0. The generator folds constants: in step 5 the new a and the new e cost no addition beyond T1, and the choice and majority of step 6 become constants (9 operations fewer). The choice and majority of step 7 get a zero input. (iii) The generator folds CH(e, f, 0) = e & f and MAJ(a, b, 0) = a & b (1 operation instead of 3). The kernel is 2180 operations for 7 trails instead of 2206 (26 fewer), and time_log2 falls from 124.84811 to **124.83147**. The success bound charges the halt on a third cut trail in full (a union bound, no independence assumption), and the age cap is raised from 12 L to 13 L so that this halt has probability 6.2e-5 (Section 4). Memory stays at most 2^20 bytes, so the scalar score equals time_log2.
The target is the plain one. The message is M(x) = P || x, a constant 20-byte prefix P followed by the 32-byte string x: 52 bytes in one block with FIPS padding, the standard IV, 39 steps, the feed-forward, and the complete 256-bit digest. No advice is used and no differential property of the 39 steps; the step structure is used only by the prefix, to make the kernel cheaper, never for the success probability. P is a constant of the program, the same for every input and computed by `prefix_words()`; it is not advice. The chain step is 2180 operations for 7 trails, which is 311.43 per trail or 0.1108 of the 2812 operations of one reference compression. The price is a declared register file of 64 words of 256 bits (counted as memory, every transfer charged; the line needs 43), a program of 5,031 instructions of 36 bytes, and a table of 33,715 entries.

## 1. Target and relation

Target `sha256-r39-prefix-v1` (the Pareto lane `sha256`, round 39). The two colliding messages have 52 bytes: M(x) = P || x, with P the 20 bytes 03f777b3 eec88896 e8ebdb1c 1b70c247 177c95e3 (hex, big-endian words W0..W4) and x the 256-bit integer written as 32 bytes big-endian. FIPS 180-4 padding (0x80, zero bytes to 56 modulo 64, then the 64-bit big-endian bit length 416) makes one block: W0..W4 = P, W5..W12 = the eight big-endian 32-bit words of x, W13 = 0x80000000, W14 = 0, W15 = 0x1A0. The compression executes the steps with indices 0 to 38 of the standard schedule and constants, starts from the standard IV, and adds the incoming state to the working state at the end. The digest is the eight state words, big-endian (`verifier/hash_functions.py:digest(M(x), "sha256", 39)`). Write s(x) for the working state after step 38 as 8 words (a, b, c, d, e, f, g, h), and f(x) for s(x) read as a 256-bit big-endian integer. Then digest(M(x)) = IV + s(x), word by word modulo 2^32 (the feed-forward with the standard IV, the only IV of a one-block message).
**Lemma 0.** For all x, y: f(x) = f(y) if and only if digest(M(x)) = digest(M(y)). *Proof:* adding the fixed IV word by word is a bijection of the 8-word state. ∎
The walk is x -> f(x); the 8 state words are the next input words W5..W12 (chain word j is message word W(5+j)). The attack outputs x != y with f(x) = f(y); by Lemma 0, M(x) != M(y) are two distinct messages with equal complete 256-bit digests. The profile's message domain is "finite byte strings of bit length below 2^64"; a 52-byte string is in it, and no length is fixed by the profile.
Prefix. `prefix_words()` fixes the state words of steps 0 to 4 to A0 = A1 = 0, A2 = S0^-1(IV[0]) and A3 = A4 = 0. S0 is GF(2)-linear and invertible; its inverse is computed by Gaussian elimination, and the program asserts S0(A2) = IV[0]. Each message word W_i fixes A_i, because E_i = A_{i-4} + E_{i-4} + S1(E_{i-1}) + CH(E_{i-1}, E_{i-2}, E_{i-3}) + K_i + W_i and A_i = E_i - A_{i-4} + S0(A_{i-1}) + MAJ(A_{i-1}, A_{i-2}, A_{i-3}). Then E4 = A4 + A0 - S0(A3) - MAJ(A3, A2, A1) = 0 - 0 - MAJ(0, A2, 0) = 0, and E3 = A3 + A_{-1} - S0(A2) - MAJ(A2, A1, A0) = 0 + IV[0] - IV[0] - 0 = 0. The program asserts both and that the constant P equals `prefix_words()`. Running steps 0..4 on P gives the state (A4, A3, A2, A1) = (0, 0, ba2ee7e3, 0), with ba2ee7e3 = S0^-1(IV[0]), and (E4, E3, E2, E1) = (0, 0, 75969668, 126d4d6d). This is a property of a constant of the program, used by the generator's constant folding; it is not a restriction of the target.
Validation (all run in a Linux container; none of it is used as an estimate):
- Against the organizer reference `verifier/hash_functions.py:digest(M(x), "sha256", 39)`, the program's scalar f plus the IV gave 0 differences on 300 random messages, and the packed kernel (7 lanes chained for 64 steps, 448 evaluations, each output plus the IV) gave 0 differences. Every pair returned by the experiment checks of Section 5 was also verified with an independent 39-step SHA-256 written from FIPS 180-4, applied to the full padded messages.
- The selftest (`python3 shrho.py --selftest`) compares the kernel with the scalar compression on 4,102 lanes (586 batches of 7, the full 256-bit f), on all-zero and all-one inputs, and on 7 lanes chained for 4 steps. It also runs the register-allocated code on a register file and runs the width-18 chain and 16 search attempts (3 of 16 returned a verified pair; `selftest True`).

## 2. The attack (program `experiments/shrho.py`, sections 4 to 6)

Parameters for n = 256 (all computed by `plan(256)` from the stated formulas, printed by `python3 shrho.py --ledger`): N = 2^256, 7 lanes. A point x is distinguished (a DP) when its low 32 bits are zero (chain word 7, the message word W12 of M(x)) and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 506. The density is theta = 506 / 2^122 and L = 1 / theta = 2^122 / 506 = 2^113.01701. The key of a DP is the 55 bits of x above bit 121 followed by the 9 low bits of F (F < 506 < 2^9, so those bits are F); 64 bits in all (`plan`: fb = 9, kb = 55).
The search uses one fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a DP.
1. 7 trails run in the 7 lanes: lane l of the packed words holds the current point of its trail. A batch is one evaluation of f for all 7 lanes by the generated straight line of Section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch, the stage-1 test (Section 3.3) forms the mask of lanes whose low 32 bits (packed word 7) are all zero. If it is zero, the next batch runs at once.
3. For each set lane (a stage-1 hit), the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, Section 7) and start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches, a lane whose trail has age >= c = 13 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when a finished trail must be stored in a full table (33,715 keys; the 33,716th finished trail halts), when a third trail would be cut, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps of f, then step both together. At the first step with f(a) = f(b) and a != b, output (a, b). Both lanes of one evaluation of the same kernel are used (the 2180 operations appear twice in the program, in the loop and in the recovery routine), with an exact equality test of the two lanes on the 8 output words. At most capr = c + S batches are run (the program halts if l1 > capr); the ledger charges capr + 1 kernel evaluations, the last one being the step that exhibits the pair.
Constants: Tp = 506, L = 2658455991569831745807614120560689152 / 253, B = 48521025487616899070617358942662296867, Q = 7 B = 0.998133 * 2^128 evaluations, e2max = 158160542330387185092233825817, c = 136600505495683054132407049673078890 (= 13 L = 2^116.717), table capacity tmax = 33,715 entries of 25 bytes. The trail numbers t stay below 2^16 (finished trails <= 33,715, cut trails <= 2, plus the 7 starts), and every length is below c + S < 2^119. So the 2-byte and 15-byte fields of an entry never overflow; the program asserts both when it stores an entry.
Per attempt: one fresh r; no restart, no amplification, no stored collision, no nonuniform advice.

## 3. Operation ledger

### 3.1 Machine
The machine convention is declared by this entry, as in 368d1718 (heuristic H3, score-critical because time_log2 depends on it; the benchmark fixes none of the three points below). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units". Its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch" and "independent uniform random 256-bit word". Its memory includes "code", "working state" and "tables". It fixes the word size and prices loads and stores. It gives no register count, no rule for constants and no rule for packing several independent computations into one word.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 64 registers (Section 3.5 prices smaller files and the absence of immediates). Each of the following is charged one operation: every addition, AND, OR, XOR, shift, comparison and conditional branch, the one random word, every load of a word from memory, every store of a word to memory, and every register move. Constants (masks, the round constants) are immediate operands. The organizer's reference count (`scripts/reference_operation_costs.py` of the benchmark repository) likewise counts only the add, and, or, xor, shift and invert operations on data words; its docstring says that memory traffic is excluded, and constants enter it as plain operands. A word holds 7 independent values (lanes) of 36 bits. One machine operation on the word is one operation; the cost model prices a word operation at 1/C whatever the word holds.
The main loop has no loads, stores or moves. The generated straight line needs 43 registers (`allocate` in the program assigns them; output word j is written into the register that held input word j, so the next batch reads the same registers). That leaves 21 of the 64 for the loop counter, the limit and the handlers' temporaries. The register file is counted as memory: 2,048 bytes (Section 7).
The organizer's reference count C(sha256-r39) = 2812 (`reference_operation_cost` 2812 in `pareto_candidate.py --family sha256 --rounds 39 --show-contract`) is used only as the unit: Unit = 2812 operations. Every instruction is charged 36 bytes of code (opcode, registers and an inline 256-bit immediate), including those with three registers.

### 3.2 One batch = 2187 operations for 7 trails
Representation (368d1718's): lane l of a packed word occupies bits 36 l to 36 l + 35 of the 256-bit word (7 lanes, 252 bits): 32 data bits and 4 guard bits above them. The kernel is a straight line of 2180 operations on registers and immediates of the form REP * c (REP has a 1 at bit 36 l of every lane; c is a 32-bit constant): add, AND, OR, XOR, shift left and shift right by an immediate.
The field invariant is enforced by the generator (`Tracer`). Every register carries an upper bound on the value of a lane. The data bits of a result are always the 32-bit result of the corresponding SHA-256 expression: additions are emitted only when the sum of the two bounds stays below 2^36 (otherwise the larger operand is first ANDed with REP * 0xFFFFFFFF), so no carry leaves a lane, and XOR and AND never leave the lane. The low 32 bits of a sum depend only on the low 32 bits of the operands, so garbage in the guard bits is harmless to the data bits.
Rotation by r of the 32-bit lane takes 5 operations: (x >> r) AND REP * (2^(32-r) - 1), then (x << (32-r)) AND REP * ((2^r - 1) << (32-r)), then OR. The first mask removes the bits that cross in from the next lane and the guard bits of the lane itself. The second keeps only the r wrapped bits. A rotation is correct for any lane value below 2^36. A shift right by k (the sigma functions) is 2 operations. The top lane's shifted-out bits (above bit 255) are lost in the machine and are masked off in every use.
Lines of the kernel (counted by the tracer; `python3 shrho.py --selftest` prints the counts per operation): 2180 = 1,360 rotation operations (272 rotations of 5) + 74 for 37 shifts right + 331 XOR + 64 AND (the choice and majority functions) + 281 additions + 70 masks that keep sums below 2^36. 368d1718 has 2206 = 1,360 + 74 + 337 + 66 + 292 + 77; the differences are -6 XOR, -2 AND, -11 additions and -7 masks.
- Per step of the compression: Sigma0 and Sigma1 are 17 operations each (3 rotations and 2 XOR). The choice is 3 (g ^ (e & (f ^ g))), or 1 (e & f) when g is the constant 0. The majority is 3 (it reuses the XOR a ^ b of the previous step as b ^ c), or 1 (a & b) when c is the constant 0. There are 7 additions (four for T1, one for T2, one for the new a, one for the new e) and 2 masks (new a, new e).
- Each schedule word W16..W38 costs 14 + 14 operations for the two sigma functions and 3 additions (and a mask when the bound requires it).
- The first steps fold the constant IV and the constant words W0..W4 and W13..W15 at build time. There is no feed-forward.
The three changes, counted by the program's own tracer with each change switched on or off (it reproduces 368d1718's count of 2206 for the zero prefix with the feed-forward):

| prefix | feed-forward | CH/MAJ folding | kernel operations |
|---|---|---|---|
| 20 zero bytes | yes | no | 2206 (368d1718) |
| 20 zero bytes | no | no | 2190 |
| A = (IV[0] + 1, IV[0] + 1, 0xFFFFFFFF, 0, 0) | no | no | 2182 |
| this entry's P: A = (0, 0, S0^-1(IV[0]), 0, 0) | no | no | 2181 |
| this entry's P | yes | yes | 2196 |
| this entry's P | no | yes | **2180** |

- (i) No feed-forward saves the 8 additions of the IV and their 8 masks (16 operations). The outputs are the state words, which the kernel has already masked when it computed them.
- (ii) The prefix changes three things. With E4 = E3 = 0, S1(E4) and CH(E4, E3, E2) = E2 are constants of step 5, and CH(E5, E4, E3) = 0 in step 6. With A4 = A3 = 0, MAJ(A4, A3, A2) = 0 in step 5 and MAJ(A5, A4, A3) = 0 in step 6, so T2 of step 5 is the constant 0 and A5 = T1 costs nothing. With A1 = 0, E5 = A1 + T1 = T1 costs nothing.
- (iii) With E4 = 0 and A4 = 0 the choice of step 7 is E6 & E5 and the majority of step 7 is A6 & A5.
The input words are a renaming (output word j is still written to the register of input word j); the chain value keeps its big-endian order, and the message is an ordinary message of the profile's domain.
Validation: 4,102 lanes against the scalar f in the selftest, and the experiment checks of Section 5 (every returned pair verified with an independent 39-step digest of the full messages). The register-allocated code executed on a register file gives the same words as the generated function (selftest).
The generator runs once at the start. Its work is charged in the setup row (Section 3.3); its code and peak storage are accounted in Section 3.6 and Section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 2180 + stage-1 test 4 + loop control 3 = 2187 operations.
Stage 1: the packed word 7 of the output is added to REP * 0xFFFFFFFF, ANDed with REP << 32, compared with REP << 32, and branched on: 4 operations (`FILT_OPS`). The word is the low 32 bits of the next point, with clear guard bits because the kernel's outputs are masked. Bit 32 of a lane is set exactly when the lane's low word is non-zero. The test loses no event: a DP has all 32 low bits zero, so its bit 32 stays clear and the comparison fails.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no hit lane (probability about 1 - 2^-29) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers; every operation is one of the model's primitives):
- Stage-1 hit: XOR with REP << 32 gives the hit lanes at bit 36 l + 32. Scanning the 7 lanes costs at most 7 * 7 = 49 operations (shift by 36 l, AND, branch, increment, compare, branch). For a hit lane (shift register s = 36 l), the words 6, 5 and 4 are extracted ((P >> s) AND 0xFFFFFFFF: 2 operations each). The window test F < Tp is a compare and branch on word 6 plus two zero tests, on word 5 and on word 4 AND (2^26 - 1): 13 operations. Total below 100 per hit lane; charged **400** per hit lane (the hit budget e2max is enforced by a halt).
- Finished trail (a DP, new start), charged **800**; the actual total is below 200:
  - extraction of words 3 and 2 and key formation (about 25 operations);
  - three read-modify-write field stores of the 25-byte entry (about 30);
  - length = b - birth (3) and the new start r + t' (1 add);
  - insertion of its 256 bits in the lane: for each of the 8 words extract (2), shift left by s (1), clear the lane in the packed word (1) and OR (1): 40, plus the lane mask (2);
  - lane arrays and counters (about 20).

  The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails are stored (a halt on a full table).
- Slice check (every 2^48 batches): the 7 births (load, subtract, compare, branch: 4 each) and the slice counter, charged **120** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **800**; at most 2 cut trails (a halt on the third).
- Recovery batch, charged as 64 operations beyond the kernel (2244 per batch), for at most capr + 1 batches. It is one evaluation of the kernel for both lanes (2180 operations) plus 39 operations:
  - the exact equality test of lane 0 and lane 1 on the 8 output words: 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26;
  - loop increment, compare and branch = 3;
  - call and return = 2;
  - 8 moves of the inputs, needed to output the colliding pair.

  The first l1 - l2 steps move one lane only and need no test; they are also inside the 2244.
- Setup and generator: a fixed part charged 4,800 (1 random word, the 7 starts r + t inserted in the lanes, counters), and the generator charged 2,154,400: 3,206 calls of the tracer and 2180 emitted lines, each charged 400 word operations. Together 2,159,200 operations = 2^9.585 units, charged in the time bound (3.4). There is no other preprocessing: no scan, no climb, no advice. `prefix_words()` is not run by the attempt; the prefix is a constant of the program. Running it would cost a 32 x 32 GF(2) elimination and 5 steps, below 10^5 operations, which is also below the setup charge.

Code size, instructions: loop body 2187 + recovery copy of the kernel with its test 2244 + handlers, key scan, cut and slice checks and setup 600 = 5,031 instructions.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A and by `python3 shrho.py --ledger` (the two agree).
| item | bound (operations) |
| --- | --- |
| main loop: B * 2187 | 106,115,482,741,418,158,267,440,164,007,602,443,248,129 (= 1.0612e+41) |
| slice checks: ceil(B / 2^48) * 120 | 2.0686e+25 |
| stage-1 hits: e2max * 400 | 6.3264e+31 |
| finished trails: (33,715 + 1) * (800 + 3 * 33,715) | 3,437,177,620 |
| cut trails: 2 * 800 | 1,600 |
| recovery: (c + 2^48 + 1) * (2180 + 64) + 600, c + 2^48 = 2^116.717 | 3.0653e+38 |
| setup and generator | 2,159,200 |
N = 106,422,014,339,014,708,658,826,106,207,929,894,447,777 = 1.064220e+41 operations.
N / 2812 = 3.7846e+37 units = 2^124.831468. Claim `time_log2` = 124.83147 (integer power certificate in Appendix A, rounded up). The main loop is 99.71 percent of it, recovery 0.29 percent.

### 3.5 Register file, immediates and smaller files
Premise H3: the machine has 64 registers of 256 bits. The generated line needs 43 (peak live words 39, no spills: `spill_ops(64)` = 0; `allocate` gives the registers, and a check executes the allocated code).
If the machine has fewer registers, the program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`) adds loads and stores to every batch, including the recovery copy. The table also shrinks, because the code grows:
| R | loads+stores per batch | operations per batch | table entries | Tp | time_log2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 64 (claimed) | 0 | 2,187 | 33,715 | 506 | 124.83147 |
| 32 | 14 | 2,201 | 33,716 | 506 | 124.84067 |
| 16 | 59 | 2,246 | 33,606 | 505 | 124.86988 |
Each row is the ledger of the program with that R (register file R x 32 bytes counted as memory, spill instructions counted as code). The claim assumes R >= 43; 64 is declared. Even at R = 32 the time bound is below 368d1718's 124.84811.
Immediates. The kernel has 696 operations with a 256-bit immediate operand (67 distinct patterns: the lane masks of the rotations and shifts, 0xFFFFFFFF, the round constants and the constants that the folding creates). If the machine had no immediates, 18 of the 21 spare registers could hold the 18 most used patterns for the whole run (loaded once at setup; 3 stay with the loop counter, the limit and a handler temporary), and every other use would be one load. That is 125 loads per batch (also in the recovery copy), a table of 33,355 entries, Tp = 501, and time_log2 124.91171 (Appendix A's program with 2180 + 125 kernel operations). Fewer registers and no immediates together are not priced.

### 3.6 Generator code and peak storage of the setup
The generator that builds the straight line at the start of the run is part of the machine code of this entry. It consists of the tracer (`Tracer`, with `build_lines`) and the register allocator (`allocate`): `python3 shrho.py --gencode` counts 1,141 bytecode instructions, and the entry charges the 1,190 of 368d1718 (an upper bound), 42,840 bytes. It keeps no node table; the emitted lines are the code records themselves. Its scratch (model `GEN_SCRATCH` = 16,384 bytes) holds the last use and the register of each emitted line (2 + 2 bytes each, 2180 lines), 256 free-register flags, the output marks, and the 16-byte values of the 39 schedule words and the state.
Layout. The setup phase holds 264,916 bytes: the main code (counted at its final size, 181,116 bytes; it is written as the generator emits it), the counters (22,528, including the 16,384-byte reserve of Section 7), the register file (2,048), the generator's code image (42,840) and its scratch (16,384). The generator is never called after setup. In the search phase the same region holds the table (842,875 bytes), the register file (2,048) and the counters: main code + counters + register file + table = 1,048,567 bytes. The memory of the entry is the larger of the two, 1,048,567 bytes. The table size of Section 7 is the largest that fits after the reserve.
Measured: the C port of the generator (source embedded in `experiments/shrho.py` as `GEN_C`, printed by `python3 shrho.py --gen-c`; this entry changes its prefix constant, its choice and majority (the two folds) and its outputs (no feed-forward)) was compiled twice:
1. To WebAssembly (clang 17, `--target=wasm32 -nostdlib -ffreestanding`, linked with initial and maximum memory both 1,048,576 bytes = 16 pages, 64 KiB stack) and run in Node.js 22. The guest memory stays 1,048,576 bytes. It emits 2,180 instructions with 43 registers and 3,206 tracer calls, and the instruction list (op, destination, operands, immediate) is identical line by line to the Python generator's: sha256 of the text a5009eee967308aaaf35bf553f9d326aef90a5bed2f02474d8f5e12fcf69e3ba for both.
2. Natively (gcc), with the same list.

The C port's own static arrays total 201,108 bytes: the code region (181,116), its counter region (6,144), the scratch (13,096) and its values (752). The generator charge of 400 word operations per tracer call and per emitted line (2,154,400) bounds its work: a tracer call does a constant number of comparisons and one 36-byte record write, and the allocator does a free-register scan of at most 43 registers per line. The whole setup row is 2^9.585 units, about 2^-115 of the time bound, so even a charge 1,000 times larger would not change time_log2 at 5 decimals. The Python generator's own resident set is the interpreter's (tens of megabytes) and is not charged; it is the footprint of the interpreter, not of the machine model.

### 3.7 Preprocessing
None offline. The generator is run inside every attempt and is charged in the setup row. The claim declares preprocessing_log2 = 9.6, the setup and generator row (2^9.585 units), which is also inside time_log2. The memory figure of Section 7 covers this preprocessing: the generator runs in the setup phase of the same attempt, its code image and scratch are in the setup-phase total of Section 3.6 (264,916 bytes), and nothing it produces is stored outside the 1,048,567 bytes of the search phase. The prefix P is a constant written in the program (Section 1); `prefix_words()` reproduces it and is not part of the attempt.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values. The attempt uses the walk function only by evaluating f at points that the procedure chooses. Write A_F for the same procedure with every evaluation of f replaced by F (lazy sampling), and P_F for its success probability, taken over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. It is stated for this f. The functional graph of x -> f(x) differs from that of x -> digest(M(x)) used by 368d1718, but by Lemma 0 the two maps have the same colliding pairs, and both are fixed bijective post-processings of the same 39-step compression of the same 52-byte message family. The sub-claims under H1 (the numbers below are printed by `python3 shrho.py --loss`) are computations for the random function F, with these approximations named as heuristic H2 (score-critical at this margin; not proved here):
- H2 (a): the age of the trail of one lane at the halt is dominated by an exponential with mean L, and the 7 ages are independent, although restarts depend on the history of the run.
- H2 (b): the number of cut trails is Poisson with the stated mean.
- H2 (c): the loss for a cut trail enters linearly with the stated slope.
- H2 (d): trail lengths are geometric with mean L (used for the colliding pairs inside trails).
- H2 (e): the birthday bound below is applied to the U points of the finished trails, a set that the walk selects adaptively, as for a fixed set of U uniform points (the standard treatment of distinguished-point collision search).

Lemma 1 (a statement about f itself, no premise). A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output. Both trails continue identically from f(x), so they end at the same DP with the same key, and the stored lengths let step 6 align and walk them. Step 6 returns the first merge pair, found within max(l1, l2) <= capr batches: a trail is cut at a slice check once its age is >= c, and slice checks are S batches apart, so every length is below c + S. The returned pair satisfies f(x) = f(y) with x != y, and the recovery checks equality before it returns; by Lemma 0 the two messages collide.
The key determines F (F < 506 < 2^10, and the key holds its 10 low bits), so equal keys of two DPs differ only if their bits above 121 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds f^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F, under H2). Let U be the number of evaluations on trails finished before the halt. The number of evaluations is Q = 7 B = 0.998133 * 2^128.
- *Unfinished trails.* For F the DP indicators of the successive points of one trail are independent with probability theta. So the age of one lane's trail at the halt (steps since its last restart) satisfies P(age >= a) <= (1 - theta)^a <= exp(-a / L), and (H2 a) the 7 ages are independent: each is stochastically dominated by an exponential with mean L. The sum of 7 such variables exceeds M L with probability at most exp(-7 (x - 1 - ln x)), x = M / 7 (Chernoff); for M = 32 this is 5.79e-07 <= 1e-6. So the 7 unfinished trails hold at most 32 L points, except with probability 1e-6.
- *Cut trails.* A cut trail costs at most c + S, that is 4.022e-04 Q. The number K of cut trails is (H2 b) Poisson with mean (Q / L) e^-13 = 32323.6 e^-13 = 0.0731: P(K = 0, 1, 2) = 0.9295, 0.0679, 0.00248, and P(K >= 3) = 6.15e-05; the third cut is a halt, charged as failure.
- *Cut-trail deficit.* The allowance 1.5e-4 Q already in U covers 0.373 of one cut trail. For K = 1 and K = 2 the remaining loss lowers the success probability by 1.525e-04 and 3.957e-04 (H2 c: slope of 1 - exp(-U^2/2N) at the target, 2 * 0.497 * e^-0.497 = 0.605 per unit of relative loss). K >= 3 is charged in full, P(K >= 3) itself, with no assumption that the halt is independent of success (a union bound). So the cut-trail deficit is 0.0679 * 1.525e-04 + 0.00248 * 3.957e-04 + 6.15e-05 = 7.29e-05.
- *Evaluations on finished trails.* Hence U >= (1 - 1.5e-4) Q - 32 L - 1 = 0.99700 * 2^128 when K = 0 and the ages are within the bound.
- *Collision bound.* For U distinct inputs the probability of no colliding pair is prod (1 - i/N) <= exp(-U(U-1)/(2N)) <= exp(-0.497); the program's B is the least that gives U(U-1) >= 2 * 0.497 N.
- *Pairs inside trails.* The expected number of colliding pairs inside trails, summed over all trails, is at most Q L / N = 2^-14.99 = 3.08e-05 (H2 d: a trail of length l has at most l(l-1)/2 pairs, E[l^2] <= 2 L^2, and there are Q / L trails).
- *Key false matches.* The expected number of two different DP ends with the same 64-bit key is below 33,715^2 / 2 / 2^63.983 = 3.1e-11 (the key space is 2^55 * 506 = 2^63.983).

Programmed aborts:
- Table capacity: the number of finished trails is at most the number of DP events among the Q evaluations. That count is binomial with mean Q / L = 32323.6 (and no more than a Poisson count of the same mean in the Chernoff bound). The abort needs 33,716 or more, which has probability at most exp(-mean) (e mean / 33,716)^33,716 = 2^-42.7 = 1.4e-13 (Chernoff bound).
- Stage-1 budget: the number of stage-1 hits is at most binomial with mean mu2 = Q / 2^32 = 7.908e+28, and the abort needs 2 mu2 + 64. Its probability is at most e^(-mu2 (2 ln 2 - 1)) = e^(-3.1e+28).
- Recovery: a recovery that finds no pair needs a key false match or a start lying on another trail (at most 3.1e-11 + 2^-100).

The losses add to 1e-06 + 3.08e-05 + 7.29e-05 + 3.1e-11 + 1.4e-13 + 7.9e-31 = 1.047e-04. So P_F >= 1 - e^-0.497 - 1.047e-04 = 0.39154 >= 0.39; the 0.0015 left over is kept as margin.
If the real pair-collision rate is (1 - eps) of the model, P stays at least 0.39 for eps <= 0.0050 (the exact threshold is 0.00509). In general, at most 0.5 * log2(1/(1-eps)) more bits of time restore 0.39: 0.0072 for eps = 0.01, 0.037 for 0.05, 0.076 for 0.10 and 0.21 for 0.25.

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function f and about one attempt, and it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved. Its content, in the terms the ledger uses:
- (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists);
- (b) the iterates of f from the starts r + t have the first-collision law of a random mapping;
- (c) whether an iterate is a DP is independent of the collision events and has probability 506 / 2^122.

A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01). Subtracting the IV is a fixed bijection of the digest. The chosen prefix is one constant 20-byte string; its constant state after step 4 is the starting point of the 34 remaining steps of the same compression, and nothing in the search depends on its algebraic form.
The two organizer experiments (Section 6) produce evidence that the program is right and that nothing gross is wrong. They are program checks: the organizer recomputes every returned pair and the counts of returned pairs are reported, but they are not used as estimates of any number of this entry. No quantitative inference is drawn from a count, no confidence interval is formed, and the entry does not rely on the independence of trials (the trial seeds are public, and the experiment is a check of the program). The program also prints its own observations (`python3 shrho.py --stats`, seeds from SHA-256 of a counter). They are untrusted and only descriptive:
    T3 n=18: attempts returning a verified pair: target 123 of 256, ideal function 119 of 256
    T1 n=10 fresh K: 256 runs, mean first repeat 41.52 (sqrt(pi N/2) = 40.11)
    T2 width 256: 448 points, 16-bit projections, equal pairs per trial if uniform 1.5278, trials with a pair if uniform 0.7830
      source uniform (86 trials): returned pairs 72 (uniform reference 67.3); w0 149 (uniform reference 131.4); w3 142; w7 129; xor8 131; sum8 137; p01 131; p23 120
      source counter (85 trials): returned pairs 67 (uniform reference 66.6); w0 116 (uniform reference 129.9); w3 146; w7 155; xor8 136; sum8 132; p01 134; p23 112
      source iterates (85 trials): returned pairs 66 (uniform reference 66.6); w0 133 (uniform reference 129.9); w3 140; w7 119; xor8 140; sum8 139; p01 127; p23 125
Local runs of the two declared experiments through the program's own stdin server: 48 trials of `shrho-n18` and 24 trials of `proj-k0-w256`, with seeds SHA-256 of "check/<id>/<i>". Every returned pair was verified with an independent 39-step SHA-256 written from FIPS 180-4, applied to the full padded messages: `shrho-n18` returned 18 pairs and 18 verified (distinct 52-byte messages, digests equal in the low 18 bits); `proj-k0-w256` returned 20 pairs and 20 verified (digests equal in the low 16 bits). These are this entry's runs, not organizer runs, and are reported without inference.
An unsuccessful attempt of the width-18 experiment either ends with a halt of the program or runs its 92 batches without finding a pair. The halt can be a budget, or "recovery found no pair" when a trail start lies on another trail; the latter is frequent at width 18 and has probability below 2^-100 at width 256 (Section 4). The single attempt is not amplified. The ideal function behaves the same way.
Toy-scale end-to-end run, outside the shipped experiments, with the same program and kernel (`toy40.py`, not shipped). At n = 40, plan(40) uses DP = low 6 bits zero and a 4-bit window, 52-byte messages P || x, and 154,052 batches of 7 lanes per attempt. 6 of 20 single attempts returned a pair, and 6 of 6 were verified with the independent digest (distinct messages, equal low 40 bits of the complete 39-step digests); 178 s in all.
Not tested: the full 256-bit functional graph, iterations of length above 2^40, and the search above width 40. A deviation that lowers the pair-collision rate by eps costs the table of Section 4. Other structured deviations, such as unusually many short cycles inside trails or starts landing on other trails, would add failures that the model does not price; nothing in the runs above indicates them, but those runs are far below width 256.

## 6. Experiments

Two organizer experiments are declared; the organizer's executor runs the shipped program `experiments/shrho.py` (no organizer result exists yet for this package). The program dispatches on the experiment id; no outside code or library is used, only the standard library.
`shrho-n18`: per trial, from the trial seed, one attempt of the 7-lane search at width n = 18 (DP = low 2 bits zero, plan(18): 92 batches of 7 lanes, cut rule, table, recovery with the same kernel) on the target chain f, which is the low 18 bits of the digest minus the IV of the 52-byte message M(x) = P || x with x < 2^18 (x sits in W12 and W5..W11 are 0, so this is a different function from the width-256 walk; the experiment checks the program, not the full-width function). The trial returns the two 52-byte messages M(x), M(y) when the attempt succeeded and two nulls otherwise. The checked event is that the complete 39-step digests agree in the low 18 bits and the messages are distinct. This is implied by the walk at width 18: the low 18 bits of digest word 7 are those of IV[7] + f_7. Untrusted observations: the same attempt on the ideal function, and one family-law run with a fresh random 20-byte prefix at n = 10.
`proj-k0-w256`: per trial, 448 points of the target at full width 256 evaluated with the packed kernel. The source is chosen by trial index mod 3: uniform inputs from the seed, counter inputs r + i, or iterates of f from 7 seed-derived starts. The trial returns two distinct points whose f values agree in the low 16 bits when the set contains such a pair, and two nulls otherwise. The checked event is that the complete digests agree in the low 16 bits and the messages are distinct, which is equivalent by the same argument. Untrusted observations: the numbers of equal pairs in seven 16-bit projections of f.
They check the kernel at full width, the packed search, lane insertion and extraction, the table, the recovery and the message construction on the real target. They do not measure the cost or the success probability at width 256. At reduced width the plan also uses other halt rules (no cap on cut trails, table capacity 4 Q / L + 64, age cap 12 L), so the experiments do not exercise the width-256 halts.

## 7. Memory

Table: 33,715 entries * 25 bytes = 842,875 bytes (the table region is empty until the search starts). An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: 5,031 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 181,116 bytes: loop body 2187, recovery copy 2244, and 600 for the handlers, key scan, cut, slice and setup.
Counters and copies: 22,528 bytes. This covers the trail numbers, birth batches, counters and the lane arrays used by the handlers (about 2,048 bytes), a reserve of 4,096 bytes for the stack, alignment and anything not itemised, and a reserve of 16,384 bytes against the handler-code estimate (600 instructions charged; the reserve holds 455 more instructions of 36 bytes). The reserve costs 0.0001 bit of time (a smaller table). The 64 registers are counted as memory: 2,048 bytes. No advice.
Memory peak = max(setup phase 264,916, search phase 1,048,567) = 1,048,567 bytes <= 2^20 = 1,048,576; the 16,384-byte reserve is inside this total. The peak is the search phase; the preprocessing runs inside the smaller setup phase (Section 3.6). Claim `memory_log2_bytes` = 20, so max(0, memory_log2_bytes - 20) = 0 and the scalar score equals time_log2. `python3 shrho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 181,116 - 2,048 - 22,528) / 25) = 33,715. Tp = 506 is the largest integer for which the table-capacity bound of Section 4 stays below 2^-40 (Appendix A computes both).

## 8. Heuristics, conventions and what is credited

The premises of this entry are those of 368d1718:
- H1, the model premise of Section 4 (score-critical);
- H2, the named approximations (a) to (e) of Lemma 2 (score-critical at this margin: the success bound depends on them);
- H3, the machine convention: 64 registers, immediates, lanes of 36 bits in a word and a 36-byte instruction charge (score-critical: time_log2 depends on it). H3 is a declared convention priced in Section 3.5, not a statistical premise; the success argument does not depend on it, and even the 32-register price (124.84067) is below 368d1718's claim.

There is no advice and no polarity climb; the entry has no two-block mode. The constant message prefix P is part of the program, not advice.
What is credited: to 368d1718 (Jbenisek), the program `shrho.py`, which includes the relation with the chain value in W5..W12, the packed-lane kernel generator and register allocator, the C port of the generator, the trail-and-table search, handlers, recovery, ledger method, success argument, experiments and the machine convention. Through 368d1718, credit also goes to 01e31be9, to the blake3 round-3 entries 0a9640ed, 3356413f, cf8b0e92 (packed lanes) and 62cfd777, and to e479cbbf.
What this entry adds: the walk on the digest minus the IV (Lemma 0) without a feed-forward in the kernel; the closed-form prefix with A0 = A1 = A3 = A4 = 0 and E3 = E4 = 0 after step 4 (`prefix_words()`); the folding of CH and MAJ with a zero constant input in the generator and in its C port; the selftest's search check over 16 attempts instead of 6 (the selftest asks that one of them succeeds, and one attempt succeeds with probability about 0.45 at n = 18); the union-bound charge of the third-cut halt with the age cap 13 L; the charge of capr + 1 recovery batches and tmax + 1 finished-trail events; the 16,384-byte memory reserve; and every number of this document, recomputed by the program.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 shrho.py --ledger`. It is 368d1718's Appendix A with the kernel count 2180, the generator call count 3206, the age cap 13, the 22,528 bytes of counters, the capr + 1 recovery batches and the tmax + 1 finished-trail events.

```python
from fractions import Fraction
from math import isqrt, log, exp, log2

PH, FILT, LOOP, LANES = 2180, 4, 3, 7           # operations of the packed step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 3206                                # generator calls (python3 shrho.py --ledger)
EXTRA = 64                                      # extra operations per recovery batch beyond the kernel
N_BITS, S1, W, KAPPA = 256, 32, 90, 13          # width, stage-1 bits, window bits (D = 122), age cap in units of L
LAM, CUT = Fraction(497, 1000), Fraction(15, 100000)
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 400, 800, 800, 120, 400
SETUP_FIXED, CMAX = 7 * 400 + 2000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE = 36, 600, 64 * 32, 22528, 25, 0
TAIL_AGES = 1e-6


def inflight_m(lanes=LANES, eps=TAIL_AGES):    # smallest M with P(sum of `lanes` exponential ages > M L) <= eps (Chernoff, exact in the exponent)
    m = lanes
    while True:
        x = m / lanes
        if exp(-lanes * (x - 1 - log(x))) <= eps:
            return m
        m += 1


M = inflight_m()
body = PH + FILT + LOOP                                        # one batch = one loop body = 2,187 operations
code_bytes = (body + (PH + EXTRA) + OTHER_CODE) * INSTR        # main body + recovery copy of the kernel + handlers
tmax = ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY    # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def plan_tp(Tp):
    L = Fraction(1 << D, Tp)                                   # trail length scale 1/theta, theta = Tp / 2^D
    ureq = isqrt(2 * Nn * LAM.numerator // LAM.denominator) + 2
    num, den = ureq + M * L + 1, CUT.denominator
    q = -(-(num * den) // (den - CUT.numerator))
    b = -(-q // LANES)
    c = -(-KAPPA * L.numerator // L.denominator)
    return L, b, c


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


Tp = max(t for t in range(1, 8193)
         if float(plan_tp(t)[1] * LANES / plan_tp(t)[0]) < tmax + 1
         and tail_log2(float(plan_tp(t)[1] * LANES / plan_tp(t)[0]), tmax + 1) <= -40)
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + PH)
rows = [("main loop: B * 2187", body * B),
        ("slice checks: ceil(B / 2^48) * 120", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 400", e2max * HIT),
        ("finished trails: (tmax + 1) * (800 + 3 * tmax)", (tmax + 1) * (EVENT + 3 * tmax)),
        ("cut trails: 2 * 800", CMAX * CUTOPS),
        ("recovery: (c + 2^48 + 1) * (2180 + 64) + 600", (capr + 1) * (PH + EXTRA) + 600),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("M =", M, " Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 2812
a = (N ** P // C ** P).bit_length() - 1                        # 2^a * C^P <= N^P < 2^(a+1) * C^P
while (1 << (a + 1)) * C ** P <= N ** P:
    a += 1
while (1 << a) * C ** P > N ** P:
    a -= 1
print("certificate: 2^%d * %d^%d <= N^%d < 2^%d * %d^%d" % (a, C, P, P, a + 1, C, P))
print("log2(N/C) = %.10f" % (log2(N) - log2(C)))
print("time_log2 = %.5f" % ((a + 1) / P))
```

Output:

```
M = 32  Tp = 506  tmax = 33715  B = 48521025487616899070617358942662296867  e2max = 158160542330387185092233825817  c = 136600505495683054132407049673078890
memory bytes = 1048567
main loop: B * 2187                                  106115482741418158267440164007602443248129
slice checks: ceil(B / 2^48) * 120                   20685757315114116353790360
stage-1 hits: e2max * 400                            63264216932154874036893530326800
finished trails: (tmax + 1) * (800 + 3 * tmax)       3437177620
cut trails: 2 * 800                                  1600
recovery: (c + 2^48 + 1) * (2180 + 64) + 600         306531534332312773473753049314127744068
setup and generator                                  2159200
N = 106422014339014708658826106207929894447777
certificate: 2^12483146 * 2812^100000 <= N^100000 < 2^12483147 * 2812^100000
log2(N/C) = 124.8314676273
time_log2 = 124.83147
```
