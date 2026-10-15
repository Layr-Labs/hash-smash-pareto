# sha256-r64 (the complete SHA-256 compression function): birthday search with 7 packed lanes per 256-bit word, chain value in the message words W5..W12

This is our third entry on this lane and a credited derivative of our own entries 368d1718-a059-4780-9f08-8f0931a46f0d (round 39, 124.84811, in review) and 01e31be9-0524-4b77-a40e-c1f862d506a8 (round 39, 124.98494, in review), both declared as dependencies of this submission (same challenge). Their search with distinguished points, handlers, recovery walk, packed-lane kernel generator with the 52-byte message layout, ledger method and experiments are reused as they are. (They derive from our blake3 round-3 entries 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c, 3356413f-cd60-410c-8847-2266d6444ac5, cf8b0e92-4302-4813-907a-3c970c102646 (the packed-lane chain), 62cfd777 and from Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.) What is new here: (1) the round count is 64, that is every step of the SHA-256 compression function (the organizer's reference at 64 steps equals hashlib.sha256, Section 1), with the round constants of the steps 39 to 63 and the message schedule W16..W63; (2) the proof of the success probability: Section 4 no longer uses a fixed-size birthday step but a supermartingale over the evaluations (Lemma 2), with the adaptive-hazard premise declared as H1 clause (d) (Section 5), after the judges' finding on our blake3 entry 41b32afc; (3) a register file of 128 words, because the 64-step line needs 67 registers. The kernel is 4241 operations for 7 trails and time_log2 is 124.9915.
The target is the plain one: the message is M(x) = P || x, a constant 20-byte prefix P (zero bytes) followed by the 32-byte string x, 52 bytes in one block with FIPS padding, standard IV, 64 steps, feed-forward, the complete 256-bit digest; no advice, no differential or structural property of the 64 steps is used (P is a constant of the program, the same for every input; it is not advice). The chain step is 4241 operations for 7 trails (606.86 per trail, 0.1235 of the 4912 operations of one reference compression). The price is a declared register file of 128 words of 256 bits (counted as memory, every transfer charged; the line needs 67), a program of 9,153 instructions of 36 bytes and a table of 28,350 entries.

## 1. Target and relation

Target `sha256-r64-prefix-v1` (the Pareto lane `sha256`, round 64). The two colliding messages have 52 bytes: M(x) = P || x with P = 20 zero bytes and x the 256-bit integer written as 32 bytes big-endian. FIPS 180-4 padding (0x80, zero bytes to 56 modulo 64, the 64-bit big-endian bit length 416) makes one block: W0..W4 = 0 (the prefix P), W5..W12 are the eight big-endian 32-bit words of x, W13 = 0x80000000, W14 = 0, W15 = 0x1A0 (416, the length in bits). The compression executes the steps with indices 0 to 63 of the standard schedule and constants, starts from the standard IV, and adds the incoming state to the working state at the end; the digest is the eight state words, big-endian (this is `verifier/hash_functions.py:digest(M(x), "sha256", 64)`). Write f(x) for the digest read as a 256-bit big-endian integer.
The walk is x -> f(x); the digest words H0..H7 are the next input words W5..W12 (chain word j is message word W(5+j)). The attack outputs x != y with f(x) = f(y); M(x) != M(y) are two distinct messages with equal complete 256-bit digests (the profile's message domain is "finite byte strings of bit length below 2^64"; a 52-byte string is in it, and no length is fixed by the profile).
The scalar digest of the program (`digest_words`) was compared outside the shipped experiments with the organizer reference `digest(M(x), "sha256", 64)` on 300 random messages: 0 differences. The packed kernel (`ext_regress.py`, not shipped) was compared with the reference on 8,197 random messages (one step) and on 7 chains of 64 steps; 0 differences in each. (The same check confirmed that the organizer reference at 64 steps equals hashlib.sha256 on 50 messages, so this target is the complete SHA-256 compression function with the standard IV and padding.) The program's own selftest (`python3 shrho.py --selftest`) compares the kernel with the scalar compression on 4,102 lanes (586 batches of 7, the full 256-bit f), on all-zero and all-one inputs, on 7 lanes chained for 4 steps, runs the register-allocated code on a register file, and runs the width-18 chain and search.

## 2. The attack (program `experiments/shrho.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 7 lanes. A point x is distinguished (a DP) when its low 32 bits are zero (chain word 7, the message word W12 of M(x)) and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 423. The density is theta = 423 / 2^122 and L = 1 / theta = 2^113.2755. The key of a DP is the 55 bits of x above bit 121 followed by the 9 low bits of F (F < 423 < 2^9, so those bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a DP.
1. 7 trails run in the 7 lanes: lane l of the packed words holds the current point of its trail. A batch is one evaluation of f for all 7 lanes by the generated straight line of Section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the mask of lanes whose low 32 bits (packed word 7) are all zero. If it is zero, the next batch runs at once.
3. For each set lane (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, Section 7) and start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 17 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 28,350 keys, when a second trail would be cut, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps of f, then step both together; at the first step with f(a) = f(b) and a != b output (a, b). Both lanes of one evaluation of the same kernel (the 4241 operations appear twice in the program, in the loop and in the recovery routine) are used, with an exact equality test of the two lanes on the 8 output words. At most capr = c + S batches are run (the program halts if l1 > capr).
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 shrho.py --ledger`): Tp = 423, L = 5316911983139663491615228241121378304 / 423, B = 48678446648581898093000000000000000000, Q = 7 B = 1.00137 * 2^128 evaluations, e2max = 158673676913638267037924379174, c = 213682041875589312901794042787383999 (= 2^117.363), table capacity tmax = 28,350 entries of 25 bytes. The trail numbers t stay below 2^16 (finished trails <= 28,350, cut trails <= 1, plus the 7 starts) and every length is below c + S < 2^119, so the 2-byte and 15-byte fields of an entry never overflow (the program asserts both when it stores an entry).
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice.

## 3. Operation ledger

### 3.1 Machine
Machine convention declared by this entry (supporting heuristic H3; the benchmark fixes none of the three points below). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices loads and stores; it gives no register count, no rule for constants and no rule for packing several independent computations into one word.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 128 registers (Section 3.5 prices smaller files and the absence of immediates). Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word, one operation each; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each. Constants (masks, the round constants, the IV words) are immediate operands, as in the organizer's reference count, which charges none for them. A word holds 7 independent values (lanes) of 36 bits; one machine operation on the word is one operation, the cost model pricing a word operation at 1/C whatever the word holds.
The main loop has no loads, stores or moves: the generated straight line needs 67 registers (`allocate` in the program assigns them; output word j is written into the register that held input word j, so the next batch reads the same registers), leaving 61 of the 128 for the loop counter, the limit and the handlers' temporaries. The register file is counted as memory: 4,096 bytes (Section 7).
The organizer's reference count C(sha256-r64) = 4912 (`reference_operation_cost` 4912 in `pareto_candidate.py --family sha256 --rounds 64 --show-contract`; the counter adds 84 per step: 2,812 at 39 steps) is used only as the unit: Unit = 4912 operations. Every instruction is charged 36 bytes of code (opcode, registers and an inline 256-bit immediate), also those with three registers; the straight line is not given a shorter encoding.

### 3.2 One batch = 4248 operations for 7 trails
Representation: lane l of a packed word occupies bits 36 l to 36 l + 35 of the 256-bit word (7 lanes, 252 bits): 32 data bits and 4 guard bits above them. The kernel is a straight line of 4241 operations on registers and immediates of the form REP * c (REP has a 1 at bit 36 l of every lane; c a 32-bit constant): add, AND, OR, XOR, shift left and shift right by an immediate.
Field invariant, enforced by the generator (`Tracer`): every register carries an upper bound on the value of a lane; the data bits of a result are always the 32-bit result of the corresponding SHA-256 expression, because additions are emitted only when the sum of the two bounds stays below 2^36 (otherwise the larger operand is first ANDed with REP * 0xFFFFFFFF), so no carry leaves a lane, and XOR and AND never leave the lane. The low 32 bits of a sum depend only on the low 32 bits of the operands, so garbage in the guard bits is harmless to the data bits. Rotation by r of the 32-bit lane: (x >> r) AND REP * (2^(32-r) - 1), then (x << (32-r)) AND REP * ((2^r - 1) << (32-r)), then OR: 5 operations. The first mask removes the bits that cross in from the next lane and the guard bits of the lane itself, which land at bit 32 - r and above; the second removes everything but the r wrapped bits (shifted-up guard bits land at bit 32 or above, and bits that overflow into the next lane land below bit 32 - r), so a rotation is correct for any lane value below 2^36 and needs no clean input. A shift right by k (the sigma functions) is 2 operations. The top lane's shifted-out bits (above bit 255) are lost in the machine and are masked off in every use.
Lines of the kernel (counted by the tracer; `python3 shrho.py --selftest` prints the counts per operation): 4241 = 2,610 rotation operations (522 rotations of 5) + 174 for 87 shifts right + 637 XOR + 116 AND (the choice and majority functions) + 542 additions + 162 masks that keep sums below 2^36. Per step of the compression: Sigma0 and Sigma1 are 17 operations each (3 rotations and 2 XOR); the choice is 3 (g ^ (e & (f ^ g))), the majority is 3 (it reuses the XOR a ^ b of the previous step as b ^ c); 7 additions (four for T1, one for T2, one for the new a, one for the new e) and 2 masks (new a, new e). Each schedule word W16..W63 costs 14 + 14 operations for the two sigma functions and 3 additions (and a mask when the bound requires it). The first steps fold the constant IV and the constant words W0..W4 and W13..W15 at build time; the IV is added again in the feed-forward (8 additions, with the masks they need).
Layout. The chain value is in the message words W5..W12 and the prefix P (20 zero bytes) in W0..W4. The generator (`Tracer`) does no operation on values that are constants in every lane, so the five compression steps 0 to 4, whose message words W0..W4 are constants, are folded entirely (the state after step 4 is a constant), and the schedule terms that combine constants cost nothing; the first variable additions are in the later steps and from W16 onward. It is a renaming of the input words: output word j is still written to the register of input word j, the chain value keeps its big-endian order, and the message is an ordinary message of the profile's domain. The prefix is the zero string; no other prefix was tried at 64 steps.
Validation: 4,102 lanes against the scalar digest in the selftest; 8,197 messages and 7 lanes chained for 64 steps against the organizer reference (Section 1); the register-allocated code executed on a register file gives the same words as the generated function (selftest).
The generator itself runs once at the start; its work is charged in the setup row (Section 3.3), its code and peak storage are accounted in Section 3.6 and Section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 4241 + stage-1 test 4 + loop control 3 = 4248 operations. Stage 1: the packed word 7 of the output (the low 32 bits of the next point, guard bits clear because the kernel's outputs are masked) is added to REP * 0xFFFFFFFF, ANDed with REP << 32 (bit 32 of a lane is set exactly when the lane's low word is non-zero), compared with REP << 32 and a branch: 4 operations (`FILT_OPS`). The test loses no event: a DP has all 32 low bits zero, so its bit 32 stays clear and the comparison fails.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no hit lane (probability about 1 - 2^-29) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers; every operation is one of the model's primitives):
- Stage-1 hit: XOR with REP << 32 gives the hit lanes at bit 36 l + 32. Scanning the 7 lanes costs at most 7 * 7 = 49 operations (shift by 36 l, AND, branch, increment, compare, branch). For a hit lane (shift register s = 36 l): the words 6, 5 and 4 are extracted ((P >> s) AND 0xFFFFFFFF: 2 operations each), the window test F < Tp is a compare and branch on word 6 and two zero tests on word 5 and on word 4 AND (2^26 - 1): 13 operations. Total below 100 per hit lane; charged **400** per hit lane (the hit budget e2max is enforced by a halt).
- Finished trail (a DP, new start): extraction of words 3 and 2 and key formation (about 25 operations), three read-modify-write field stores of the 25-byte entry (about 30), length = b - birth (3), the new start r + t' (1 add), insertion of its 256 bits in the lane: for each of the 8 words extract (2), shift left by s (1), clear the lane in the packed word (1) and OR (1): 40, plus the lane mask (2), lane arrays and counters (about 20). Total below 200; charged **800**. The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails (a halt on a full table).
- Slice check (every 2^48 batches): the 7 births (load, subtract, compare, branch: 4 each) and the slice counter: charged **120** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **800**; at most 1 cut trail (a halt on the second).
- Recovery batch (both lanes in one evaluation of the kernel, 4241 operations) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the inputs (needed to output the colliding pair): 39, charged as 64 per recovery batch (4305 per batch). The first l1 - l2 steps move one lane only and need no test, also inside the 4305.
- Setup and generator: 1 random word; the 7 starts r + t inserted in the lanes; counters; fixed part charged 4,800. The generator: 6,058 calls of the tracer and 4241 emitted lines, each charged 400 word operations: 4,119,600. Setup and generator together 4,124,400 operations = 2^9.71 units, charged in the time bound (3.4). There is no other preprocessing: no scan, no climb, no advice.
Code size, instructions: loop body 4248 + recovery copy of the kernel with its test 4305 + handlers, key scan, cut and slice checks and setup 600 = 9,153 instructions.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 4248 | 206,786,041,363,175,903,099,064,000,000,000,000,000,000 (= 2.0679e+41) |
| slice checks: ceil(B / 2^48) * 120 | 2.075e+25 |
| stage-1 hits: e2max * 400 | 6.3469e+31 |
| finished trails: 28,350 * (800 + 3 * 28,350) | 2,433,847,500 |
| cut trails: 1 * 800 | 800 |
| recovery: (c + 2^48) * (4241 + 64) + 600, c + 2^48 = 2^117.363 | 9.1990e+38 |
| setup and generator | 4,124,400 |
N = 207,705,942,616,919,806,609,432,734,460,423,869,930,515 = 2.077059e+41 operations.
N / 4912 = 4.2285e+37 units = 2^124.991500. Claim `time_log2` = 124.9915 (integer power certificate in Appendix A, rounded up with 4.6e-07 of slack). The main loop is 99.56 percent of it, recovery 0.44 percent.

### 3.5 Register file, immediates and smaller files
Premise H3: the machine has 128 registers of 256 bits. The generated line needs 67 (peak live words 63, no spills: `spill_ops(128)` = 0; `allocate` gives the registers and a check executes the allocated code). If the machine has fewer registers, the program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`) adds loads and stores to every batch (to the recovery copy too), and the table shrinks because the code grows:
| R | loads+stores per batch | operations per batch | table entries | Tp | time_log2 | success lower bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 128 (claimed) | 0 | 4,248 | 28,350 | 423 | 124.99150 | 0.39000 |
| 64 (Belady schedule; `allocate` needs 67, so a file of 64 needs a better allocator than the program's) | 0 | 4,248 | 28,432 | 424 | 124.99147 | 0.39000 |
| 32 | 62 | 4,310 | 28,294 | 422 | 125.01243 | 0.39000 |
| 16 | 123 | 4,371 | 28,139 | 419 | 125.03278 | 0.39000 |
Each row is the ledger of the program with that R (register file R x 32 bytes counted as memory, spill instructions counted as code). The claim assumes R >= 67; 128 is declared.
Immediates. The kernel has 1,379 operations with a 256-bit immediate operand (104 distinct patterns: the lane masks of the rotations and shifts, 0xFFFFFFFF, the round constants, the IV words). If the machine had no immediates, the 61 registers left over could hold the 61 most used patterns for the whole run (loaded once at setup) and every other use would be one load: 43 loads per batch (also in the recovery copy), table 28,226 entries, time_log2 125.00608.

### 3.6 Generator code and peak storage of the setup
The generator that builds the straight line at the start of the run is part of the machine code of this entry: the tracer (`Tracer`, with `build_lines`) and the register allocator (`allocate`), which are 1,190 bytecode instructions (`python3 shrho.py --gencode`, one instruction each) and are charged 1,190 instructions * 36 bytes = 42,840 bytes. It keeps no node table: the emitted lines are the code records themselves. Its scratch (model `GEN_SCRATCH` = 24,576 bytes): the last use and the register of each emitted line (2 + 2 bytes each, 4241 lines), 256 free-register flags, the output marks, and the 16-byte values of the 64 schedule words and the state.
Layout. The setup phase holds the main code (counted at its final size, 329,508 bytes; it is written as the generator emits it), the counters (6,144), the generator's code image (42,840) and its scratch (24,576): 403,068 bytes. The generator is never called after setup. In the search phase the same region holds the table (708,750 bytes), the register file (4,096) and the counters: main code + counters + register file + table = 1,048,498 bytes. The memory of the entry is the larger of the two, 1,048,498 bytes (78 bytes to spare under 2^20); the region is 718,990 bytes against 67,416 bytes of generator image and scratch. The table size of Section 7 is the largest that fits.
Measured peak memory of the generator (not the machine model, which is the byte account above): the circuit generator written in freestanding C (source embedded in `experiments/shrho.py` as `GEN_C`, printed by `python3 shrho.py --gen-c`, 9,856 bytes) compiled to WebAssembly and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes emits the identical program: 4,241 instructions, 67 registers, 6,058 tracer calls, and the instruction text equal line by line to the Python generator's (sha256 equal). Its static arrays total 358,860 bytes, of which 329,508 are the code region (36-byte records) and 6,144 the counters; its scratch is 22,056 bytes and its values 1,152 bytes; it needs 2,473,212 wasm operations, below the 4,119,600 word operations the ledger charges for the generator. The guest links in 6 pages.

### 3.7 Preprocessing
None offline. The generator is run inside every attempt and is charged in the setup row; the claim declares preprocessing_log2 = 9.8, the setup and generator row, which is also inside time_log2. The memory figure of Section 7 covers this preprocessing: the generator runs in the setup phase of the same attempt, its code image and scratch are in the setup-phase total of Section 3.6 (403,068 bytes), and nothing it produces is stored outside the 1,048,498 bytes of the search phase.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of f replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F: its inputs are Lemma 1 (a statement about f itself), the lazy-sampling facts of Step 1 (statements about F), and the supporting premise H2. H1 clause (d) (Section 5) is the premise that the lazy-sampling hazard of F also holds for the adaptive choices of the program (which trails finish, are cut or abort depend on earlier outputs). The numbers below are printed by `python3 shrho.py --loss` (the function `_lossq`; Appendix A recomputes them with its own copy).
H2 (supporting). The number K of cut trails in the run of A_F is Poisson with mean mu = (Q / L) e^-17 = 0.0011; the program halts at the second cut and that halt is charged as failure: P(K >= 2) = 6.29e-07. This is the only use of H2; no age, trail-length or collision count is assumed.

Lemma 1 (a statement about f itself, no premise). A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output: both trails continue identically from f(x), so they end at the same DP with the same key and the stored lengths let step 6 align and walk them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies f(x) = f(y) with x != y; the recovery checks equality before it returns.
The key determines F (F < 423 <= 2^9 and the key holds its 9 low bits), so equal keys of two DPs differ only if their bits above 176 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds f^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F; premise H2 only). P_F >= 1 - e^-theta - (the terms of Step 6) = 0.39000 >= 0.39, with theta = 0.49862 (Step 5). The program's B is the least multiple of 10^18 for which the bound reaches 0.39 (Appendix A).

Notation. The program makes Q = 7 B = 1.00137 * 2^128 evaluations, one per lane in each of B batches; number them t = 1, ..., Q in order (batch by batch, lane by lane inside a batch), and write b(t) for the batch of t. A trail is the run of evaluations of one lane between two restarts; a(t) is the number of earlier evaluations of the trail of t (its age) and the length of a trail is its number of evaluations. A trail is finished when an evaluation returns a distinguished point (DP; that evaluation is its last), cut when a slice check restarts it, open when the halt comes first. Every length is at most c + S (S = 2^48), a trail of length at most c is never cut, and a DP output has probability theta_D = Tp / 2^122 = 1 / L. Put q = Q / L = 27109.13 and h = floor(c / 2). An evaluation is fresh when its input has not been evaluated before; the starts r + t' (t' < 2^16) differ from every value the run produces except with probability 2^-100 (r is uniform and independent of F; Q 2^16 / N < 2^-100), and below this event is excluded, so a non-fresh evaluation exists only after a collision (defined in Step 2) and is a repetition of points of an earlier trail.

Step 1 (lazy sampling with a lottery). Realise F by independent uniform values V_1, ..., V_Q: the t-th evaluation returns V_t if it is fresh and the value stored for its input otherwise. This is the lazy sampling of F; the value of a fresh evaluation is uniform on all N values whatever happened before, for every adaptive choice of the points. Let xi_t = 1 if V_t is a DP. The xi_t are independent with P(xi_t = 1) = theta_D, and given all of them the V_t are independent, each uniform on its class (the DP values, or the other values). Let G_t be the history of the first t evaluations together with all of xi_1, ..., xi_Q (the lottery, future included). Facts: (L1) if t is fresh and xi_t = 0 and v is a value that is not a DP, then P(V_t = v | G_(t-1)) = 1 / N' >= 1 / N, with N' = (1 - theta_D) N >= (1 - 2^-100) N, and the events for different v are disjoint. (L2) whether t is fresh, its input, its batch, its age and the trails before t are determined by G_(t-1). (L3) number the trails in order of start and give the j-th its free length l_j, the number of evaluations from its start to the first one on its lane with xi = 1. Each position is chosen by the past, so by optional skipping the l_j are independent geometric variables of mean L = 1 / theta_D; a trail without collision that is not cut has length l_j.

Step 2 (usable collisions). A collision is a fresh evaluation t whose value V_t equals an earlier value (the output of an earlier fresh evaluation). For y an evaluation on lane lambda let f(y) be the first position t' >= y on the same lane with xi_(t') = 1 and d(y) = b(f(y)) - b(y) + 1. For fresh t with xi_t = 0 let Y_t be the set of evaluations y with
(i) b(y) < b(t); y is fresh; the output of y is not a DP; y is not on the trail of t;
(ii) every evaluation of the trail of y up to t - 1 is fresh and none of them is a collision;
(iii) if s(y) is the batch where the trail of y started, b(f(y)) - s(y) + 1 <= c and b(f(y)) <= B;
(iv) b(t) + d(y) - 1 <= B and a(t) + d(y) <= c.
For t not fresh or with xi_t = 1 put Y_t = empty. By (L2) Y_t is determined by G_(t-1). The usable collision C_t is the event that t is fresh, xi_t = 0 and V_t = F(y) for some y in Y_t. An unusable collision D_t is a collision at a fresh t with xi_t = 0 that is not C_t.
Claim 1. Let C_t occur with y in Y_t, and assume that after t no fresh evaluation on the trail of y before f(y) is a collision, and that the run does not stop early (second cut, table full, stage-1 budget, key false match). Then the program outputs a pair. Proof. Let x be the input of t and p_k the input of y, so F(x) = F(p_k): the trail of t continues with the points p_(k+1), p_(k+2), ... that the trail of y evaluates after y. The j-th of them is evaluated by the trail of y in batch b(y) + j and by the trail of t in batch b(t) + j > b(y) + j, so the trail of t only repeats points that were already evaluated (not fresh). By (ii), (iii) and the assumption, the trail of y is not cut and its evaluations up to f(y) are fresh with no collision; f(y) is the first position with xi = 1, so the trail of y finishes there, with a DP, within c batches and before the halt. The trail of t reaches the same point d(y) - 1 batches after t, in batch b(t) + d(y) - 1 <= B and at age at most a(t) + d(y) <= c by (iv): it is not cut and it finishes with the same DP. The two trails are different (y is not on the trail of t, (i)), the inputs x and p_k are different (x is fresh) and F(x) = F(p_k): Lemma 1 applies. QED.
Claim 2. For fresh t the values F(y), y in Y_t, are pairwise different. Proof. If y and y' in Y_t, y' evaluated later, had the same value, V_(y') would equal an earlier value, so y' is a collision on its own trail, against (ii). QED.

Step 3 (disturbance). Let tau be the first t with C_t. After tau the trail of y has at most c + S further fresh evaluations before f(y), each with xi = 0; by (L1) each is a collision with conditional probability at most (Q + 2^16) / N' given G, so P(some is a collision | G_tau) <= (c + S) Q / N (1 + 2^-100) = delta = 6.288e-04. By Claim 1, P(C occurs and the program does not halt early) >= P(C occurs) - delta - P(early halt).

Step 4 (a supermartingale). Let S_t = sum of |Y_s| over s <= t, u_t = |Y_t| / N' for fresh t with xi_t = 0 (and 0 otherwise), h_t = (t - 1 + 2^16 - |Y_t|) / N', H_t the sum of the h_s, R_t the number of unusable collisions up to t, and w >= 1 a constant. By (L1) and Claim 2, P(C_t | G_(t-1)) = u_t exactly, since the usable values F(y) are |Y_t| different non-DP values, and P(D_t | G_(t-1)) <= h_t, since at most t - 1 + 2^16 earlier values (outputs and starts) exist, |Y_t| of which are usable. Put
M_t = exp(S_t / N' - (w - 1) H_t) w^(R_t) 1[no usable collision up to t].
For fresh t with xi_t = 0, E[M_t / M_(t-1) | G_(t-1)] <= e^(u_t - (w-1) h_t) (1 - u_t + (w - 1) h_t) <= 1 (the factor is 1 - P(C) - P(D) + w P(D) = 1 - P(C) + (w - 1) P(D), and 1 + x <= e^x); for the other t, M_t = M_(t-1) or smaller. So (M_t) is a supermartingale with M_0 = 1, E M_Q <= 1 and P(M_Q >= e^x) <= e^-x. The same computation without the factors S_t and 1[...] gives E[w^(R_Q) e^(-(w-1) H_Q)] <= 1; since H_Q <= Q^2 / (2 N') + 2^16 Q / N', E[w^(R_Q)] <= e^((w - 1) 0.6) and P(R_Q >= 60) <= w^-60 e^((w - 1) 0.6) <= e^-200 for w = e^5: fewer than 60 trails collide.

Step 5 (counting S_Q from below). Let A be the event that there is no usable collision, the run lasts Q evaluations, K <= 1, R_Q < 60, no start coincides with another value, no fresh evaluation with xi = 1 returns an earlier DP value (probability at most Q k / N), and no finished trail is longer than c (a trail longer than c that finishes before the next slice check: probability at most 2.6e-23). On A count the pairs (y, t) with b(y) < b(t): P0 = 7^2 B (B - 1) / 2 >= (1 - 2^-100) Q^2 / 2. The pair is in S_Q (that is, y in Y_t, t fresh, xi_t = 0) unless one of the following holds.
(a) t has xi_t = 1 or y has a DP output: at most 2 k Q pairs, below 2^-100 Q^2 (k - 1 = 27723 bounds the number of DP outputs, see below).
(b) y or t lies on a trail that contains a collision (a colliding trail): there are R_Q of them, each with at most c + S evaluations, so at most 2 (c + S) Q pairs per colliding trail.
(c) y lies on a cut trail: at most (c + S) Q pairs for each of the K cut trails.
For the remaining trails (free trails: every evaluation fresh and no collision) the length is the free length of (L3); let m = min(l, c + S) for a free length l and X(m) = m (m + 1) / 2.
(d) y and t on the same trail: at most X(m) pairs per trail.
(e) y on a trail open at the halt (age a <= l): the pairs (y, t) with b(t) > b(y) are 7 (B - b(y)) per y, in total at most 7 a (a - 1) / 2 <= 7 X(m).
(f) y on a finished free trail of length l = m: by (iv) the batches b(t) > B - d(y) + 1 are lost, at most 7 (d(y) - 1) pairs per y, in total at most 7 sum_y d(y) <= 7 X(m).
(g) (iv), second part: a(t) + d(y) > c forces a(t) > h or d(y) > c - h. The evaluations with a(t) > h are at most (m - h)+ per trail and those with d(y) > c - h at most (m - h)+ per finished trail (c - h >= h), so at most 2 Q (m - h)+ pairs per trail.
Hence, with z(m) = (8 X(m)) + 2 Q (m - h)+ and the free lengths l_j of (L3),
S_Q >= Q^2 / 2 - Z - K (c + S) Q - R_Q kap0 - 2^-100 Q^2, where Z = sum over j <= n_max of z(min(l_j, c + S)) and kap0 = 2 (c + S) Q + z(c + S) (the term z(c + S) pays for the index of a trail that is not free: the free trails are among the first n_max + R_Q indices).
n_max = 27723 + 1 + 7 = 27731, where 27723 = k - 1 bounds the number of finished free trails: each ends with a fresh evaluation with xi = 1, so their number is at most the number of the Q positions with xi = 1, binomial with mean q, and P(more than k - 1) <= e^-q (e q / k)^k <= 1e-03 (Chernoff); the other trails are at most 1 cut and 7 open.
The free lengths are independent geometric variables of mean L (L3), exponential in the units L (relative error 1 / L < 2^-100). In the units L^2, z(m) / L^2 = (8 / 2) u^2 + 2 q (u - h / L)+ for u = m / L, u ~ Exp(1) cut at (c + S) / L = 17. The Chernoff bound for the sum of n_max independent copies (exact moment generating function by numerical integration, the optimal exponent found by search; `_zq`) gives P(Z > z*) <= 1e-03 for z* = 1.5555e+06 L^2 = 0.0042 Q^2 / 2.
Take w with ln w = w kap0 / N (kap0 / N = 0.00189, w = 1.00189); N' is replaced by N from here on (a relative change of 2^-100 in every exponent, included in the last term). On A with Z <= z*, using H_Q <= (Q^2 / 2 - S_Q) / N' + 2^-100:
ln M_Q = S_Q / N - (w - 1) H_Q + R_Q ln w >= (w S_Q - (w - 1) Q^2 / 2) / N + R_Q ln w - 2^-100 >= (w (Q^2 / 2 - z* - 1 (c + S) Q) - (w - 1) Q^2 / 2) / N - 2^-100 = theta - 2^-100,
because the terms with R_Q add up to R_Q (ln w - w kap0 / N) = 0. Here theta = 0.49862. By Markov, P(A and Z <= z*) <= P(M_Q >= e^(theta - 2^-100)) <= e^-theta (1 + 2^-100).

Step 6 (the sum). P_F >= 1 - e^-theta - (1e-03 finished-trail count + 1e-03 trail sums) - 6.29e-07 (second cut) - 6.29e-04 (Step 3) - 2.6e-11 (key false match) - 9.3e-12 (table full) - 2.6e-23 (long finish) - 2^-100 = 0.39000, with e^-theta = 0.60737 and the sum of the other terms 0.00263.
Key false matches: the expected number of pairs of different DP ends with the same 64-bit key (key space 2^55 * 423 = 2^63.72) is below 28,350^2 / 2 / 2^63.72 = 2.6e-11. Programmed aborts: the number of finished trails is at most k - 1 plus the (at most 60) trails that merge, so the table (tmax = 28,350 keys) fills with probability at most exp(-q) (e q / 28291)^28291 = 2^-36.6 = 9.3e-12 (Chernoff, tfull = tmax - 59); the stage-1 budget (2 mu2 + 65 hits, mu2 = Q / 2^32 = 7.93e+28) is exceeded with probability at most e^(-mu2 (2 ln 2 - 1)) = e^(-3.1e+28); a recovery that finds no pair needs a key false match or a start on another trail (at most 2.6e-11 + 2^-100).
Consequently P_F >= 1 - 0.61000 >= 0.39, and the margin above 0.39 is 3.9e-13 (B is the least multiple of 10^18 that reaches 0.39).

Sensitivity to H1 (d). If the hazard of a collision is (1 - eps) / N instead of 1 / N (clause (d) of H1; the same sensitivity as a deficit eps of the pair-collision rate in clause (a)), the plan of this program (same lemma with N / (1 - eps)) needs, to restore 0.39: 0.0073 bit for eps = 0.01 (Tp 420); 0.0370 bit for eps = 0.05 (Tp 412); 0.0760 bit for eps = 0.10 (Tp 401); 0.2075 bit for eps = 0.25 (Tp 366). The sensitivity to H2: if P(K >= 2) were ten times larger, the bound would lose 5.7e-06 of probability.

## 5. Premise H1 and its evidence

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function f and about one attempt; it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved: an assumption, no proof is known. Its content, in the terms Lemma 2 uses, is four clauses: (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of f from the starts r + t have the first-collision law of a random mapping; (c) whether an iterate is a DP is independent of the collision events and has probability 423 / 2^122; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of f; clause (d) is that this adaptivity does not lower the collision hazard, that is, for every fresh evaluation, given the whole history of the run and which later outputs are distinguished points, the output equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard that F has by construction, L1 of Section 4). Clause (d) replaces the fixed-size birthday step of the Lemma 2 of our earlier entries on this lane (the same step that the judges asked to be proved or declared on our blake3 round-4 entry 41b32afc, finding F1-adaptive-finished-trail-conditioning, aggregate heuristic H4); it is both: Lemma 2 now proves the bound for F from the hazard alone (a supermartingale over the evaluations, no conditioning on which trails finish), and (d) is the premise that f has that hazard. Nothing else in the success bound is heuristic apart from H2 (the cut count): Lemma 1, the lazy-sampling facts, the supermartingale, the counting of pairs and the Chernoff bounds are proved in Section 4 for F; Sections 3 and 7 are counts of the program. Sensitivity: a hazard (1 - eps) / N costs the same as a deficit eps in clause (a): 0.0073 bit for eps = 0.01 (Tp 420); 0.0370 bit for eps = 0.05 (Tp 412); 0.0760 bit for eps = 0.10 (Tp 401); 0.2075 bit for eps = 0.25 (Tp 366) (Section 4). The only evidence for (a) to (d) is the program checks of Section 6, which do not reach the full 256-bit event and are not used as estimates.
Evidence that the program is right and that nothing gross is wrong is produced by the two organizer experiments (Section 6). They are program checks: the organizer recomputes every returned pair, the counts of returned pairs are reported, and they are not used as estimates of any number of this entry. No quantitative inference is drawn from a count, no confidence interval is formed, and the entry does not rely on the independence of trials (the trial seeds are public and the experiment is a check of the program). The program also prints its own observations (`python3 shrho.py --stats`, seeds from SHA-256 of a counter), which are untrusted and are only descriptive:
    T3 n=18: attempts returning a verified pair: target 117 of 256, ideal function 119 of 256
    T1 n=10 fresh K: 256 runs, mean first repeat 40.41 (sqrt(pi N/2) = 40.11)
    T2 width 256: 448 points, 16-bit projections, equal pairs per trial if uniform 1.5278, trials with a pair if uniform 0.7830
      source uniform (86 trials): returned pairs 75 (uniform reference 67.3); w0 147 (uniform reference 131.4); w3 131 (uniform reference 131.4); w7 123 (uniform reference 131.4); xor8 130 (uniform reference 131.4); sum8 136 (uniform reference 131.4); p01 130 (uniform reference 131.4); p23 124 (uniform reference 131.4)
      source counter (85 trials): returned pairs 64 (uniform reference 66.6); w0 126 (uniform reference 129.9); w3 147 (uniform reference 129.9); w7 114 (uniform reference 129.9); xor8 128 (uniform reference 129.9); sum8 156 (uniform reference 129.9); p01 135 (uniform reference 129.9); p23 133 (uniform reference 129.9)
      source iterates (85 trials): returned pairs 71 (uniform reference 66.6); w0 128 (uniform reference 129.9); w3 140 (uniform reference 129.9); w7 103 (uniform reference 129.9); xor8 126 (uniform reference 129.9); sum8 123 (uniform reference 129.9); p01 125 (uniform reference 129.9); p23 135 (uniform reference 129.9)
Run by the organizer's pipeline on this program with the public seed (the pipeline reruns each experiment and requires identical output), reported without inference:
    shrho-n18 (organizer run, public seed): 114 of 256 trials returned a pair that the organizer verified; ideal-function control (program's own) 126 of 256; family-law runs at n = 10 (program's own): mean first repeat 38.56; halts target 45, ideal 42.
    proj-k0-w256 (organizer run): 201 of 256 trials returned a verified pair; by source: uniform 68 of 86; counter 68 of 85; iterates 65 of 85; equal pairs in the seven projections (program's own), total over 256 trials: w0 378, w3 343, w7 417, xor8 446, sum8 389, p01 376, p23 372.
An unsuccessful attempt of the width-18 experiment either ends with a halt of the program (a budget, or "recovery found no pair" when a trail start lies on another trail, which is frequent at width 18 and has probability below 2^-100 at width 256, Section 4) or runs its 92 batches without finding a pair; the single attempt is not amplified. The ideal function behaves the same way.
Toy-scale end-to-end runs (outside the shipped experiments, same program, same kernel, development machine; `toy_run.py`, not shipped): n = 40 (plan(40): DP = low 6 bits zero and a 4-bit window, 154,052 batches of 7 lanes per attempt, 52-byte messages P || x): 21 of 60 single attempts returned a pair, 21 of 21 confirmed by the organizer reference (distinct messages, equal low 40 bits of the complete 64-step digests); 1252 s of CPU in all (two seed sets of 30); the earlier entries also ran n = 48, not repeated here.
Not tested: the full 256-bit functional graph; iterations of length above 2^40; the search above width 40. A deviation of f from H1 that raises the collision rate only helps; one that lowers it by eps costs the table of Section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/shrho.py` (the program dispatches on the experiment id; no outside code or library is used; the standard library only).
`shrho-n18`: per trial, from the trial seed, one attempt of the 7-lane search at width n = 18 (DP = low 2 bits zero, plan(18): 92 batches of 7 lanes, cut rule, table, recovery with the same kernel) on the target chain f (the low 18 bits of the digest of the 52-byte message M(x) = P || x with x < 2^18); the trial returns the two 52-byte messages M(x), M(y) when the attempt succeeded and two nulls otherwise. The checked event is that the complete 64-step digests agree in the low 18 bits and the messages are distinct. Observations (untrusted): the same attempt on the ideal function, and one family-law run with a fresh random 20-byte prefix at n = 10.
`proj-k0-w256`: per trial, 448 points of the target at full width 256 evaluated with the packed kernel (source by trial index mod 3: uniform inputs from the seed, counter inputs r + i, iterates of f from 7 seed-derived starts), returning two distinct points whose complete digests agree in the low 16 bits when the set contains such a pair, two nulls otherwise. The checked event is that the digests agree in the low 16 bits and the messages are distinct. Observations (untrusted): the numbers of equal pairs in seven 16-bit projections of the digest.
They check the kernel at full width, the packed search, lane insertion and extraction, the table, the recovery and the message construction on the real target. They do not measure the cost or the success probability at width 256. Running times: 5.6 s and 3.5 s on the development machine; 7.4 s and 4.9 s (the slower of two runs each) in the organizer pipeline's Docker sandbox, against its limit of 20 s per experiment.

## 7. Memory

Table: 28,350 entries * 25 bytes = 708,750 bytes (the table region is empty until the search starts). An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: 9,153 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 329,508 bytes (loop body 4248, recovery copy 4305, handlers, key scan, cut, slice and setup 600).
Counters and copies: 6,144 bytes (trail numbers, birth batches, counters and the lane arrays used by the handlers, about 2,048 bytes, and a reserve of 4,096 bytes for the stack, alignment and anything not itemised). The 128 registers, counted as memory: 4,096 bytes. No advice. Memory peak = max(setup phase 403,068, search phase 1,048,498) = 1,048,498 bytes <= 2^20 = 1,048,576; the preprocessing is inside the setup phase. This is the search phase; the setup phase, in which the circuit generator runs, is smaller (403,068 bytes, Section 3.6). Claim `memory_log2_bytes` = 20. `python3 shrho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 64 - 329,508 - 4,096 - 6,144) / 25) = 28,350 (64 bytes are left unused as a margin), and Tp = 423 is the largest integer for which the success bound of Section 4 reaches 0.39 at the largest mean number of trails whose table-capacity tail stays below 2^-40 (Appendix A computes both).

## 8. Heuristics, conventions and what is credited

The premises of this entry are: H1 (the model premise of Sections 4 and 5, clauses (a) to (d), score-critical), H2 (the number of cut trails, supporting) and H3 (the machine convention: 128 registers, immediates, lanes of 36 bits in a word, 36-byte instruction charge; supporting: it is a declared convention priced in Section 3.5, not a statistical premise, and the success argument does not depend on it). There is no advice and no polarity climb; the entry has no two-block mode. The constant message prefix P (20 zero bytes) is part of the program, not advice.
Credited to our own earlier entries on this lane, 368d1718-a059-4780-9f08-8f0931a46f0d (the message layout, the 52-byte message with the chain value in W5..W12) and 01e31be9-0524-4b77-a40e-c1f862d506a8 (the packed-lane search, kernel generator, ledger and experiments), both declared as dependencies (same challenge); through them to our blake3 round-3 entries 0a9640ed, 3356413f, cf8b0e92 (the packed-lane chain), 62cfd777 (declared register file and generator accounting) and to Jbenisek's e479cbbf: the relation, the trail-and-table search, the handlers, the recovery, the ledger method and the experiments' form. The supermartingale proof of Section 4 follows the proof we wrote for our blake3 round-4 line after the judges' finding on 41b32afc (not a dependency: that entry is on another challenge). The target, the round constants of steps 39 to 63 in the kernel and every number here are new.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 shrho.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, factorial

PH, FILT, LOOP, LANES = 4241, 4, 3, 7           # operations of the packed step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 6058                                # generator calls (python3 shrho.py --ledger)
EXTRA = 64                                      # extra operations per recovery batch beyond the kernel
N_BITS, S1, W, KAPPA = 256, 32, 90, 17          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 400, 800, 800, 120, 400
SETUP_FIXED, CMAX = 7 * 400 + 2000, 1
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 36, 600, 128 * 32, 6144, 25, 0, 64
EPS, HZ, GRAIN = 1e-3, (LANES + 1) / 2, 10 ** 18  # Lemma 2 tail budgets, weight of a squared trail length, B is a multiple of GRAIN
body = PH + FILT + LOOP                                        # one batch = one loop body
code_bytes = (body + (PH + EXTRA) + OTHER_CODE) * INSTR        # main body + recovery copy of the kernel + handlers
tmax = ((1 << 20) - SPARE - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY    # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


def zq(q, uc, uh, n):         # Chernoff quantile at EPS (units L^2) of the sum of n independent z(u) = HZ m^2 + 2 q (m - uh)+, m = min(u, uc), u ~ Exp(1)
    k = 1500
    h = uc / k
    us = [(i + .5) * h for i in range(k)]
    zs = [HZ * u * u + 2 * q * max(0.0, u - uh) for u in us]
    zc = HZ * uc * uc + 2 * q * (uc - uh)

    def f(lam):
        a = [lam * z - u for z, u in zip(zs, us)]
        m = max(max(a), lam * zc - uc)
        return (n * (m + log(sum(exp(x - m) for x in a) * h + exp(lam * zc - uc - m))) - log(EPS)) / lam
    lo, hi = -16.0, -4.0
    for _ in range(50):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        lo, hi = (lo, m2) if f(exp(m1)) < f(exp(m2)) else (m1, hi)
    return f(exp((lo + hi) / 2))


def plower(Tp, q):            # the lower bound of Lemma 2 on the success probability, q = Q / L
    L = Fraction(1 << D, Tp)
    c = -(-KAPPA * L.numerator // L.denominator)
    uc, uh = float((c + SB) / L), float((c // 2) / L)
    k = int(q) + 1
    while tail_log2(q, k) > log(EPS, 2):
        k += 1
    z = zq(q, uc, uh, k - 1 + CMAX + LANES)
    l2n = float(L * L / Nn)
    kap = (2 * q * uc + HZ * uc * uc + 2 * q * (uc - uh)) * l2n
    if kap >= 0.3:
        return -1.0
    w = 1.0
    for _ in range(100):
        w = exp(w * kap)
    s0 = q * q / 2
    th = l2n * (w * (s0 - z - CMAX * uc * q) - (w - 1) * s0)
    mu = q * exp(-KAPPA)
    cuts = 1 - sum(exp(-mu) * mu ** j / factorial(j) for j in range(CMAX + 1))
    keyfm = tmax * (tmax - 1) / 2 * 2.0 ** -(min(64 - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp))
    return 1 - exp(-th) - 2 * EPS - cuts - uc * q * l2n - keyfm - 2.0 ** tail_log2(q, tmax - 59) - (k + CMAX + LANES) * exp(-KAPPA) * float(SB / L) - 2.0 ** -100


def plan_tp(Tp):              # the least B (a multiple of GRAIN) with plower >= 0.39
    L = Fraction(1 << D, Tp)
    lo, hi = 1.0, tmax + 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if plower(Tp, mid) >= 0.39 else (mid, hi)
    b = -(-int(hi * L / LANES) // GRAIN) * GRAIN
    while plower(Tp, float(b * LANES / L)) < 0.39:
        b += GRAIN
    return L, b, -(-KAPPA * L.numerator // L.denominator)


lo, hi = 1.0, tmax + 1.0                                       # the largest mean number of trails the table holds (tail within 2^-40)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
a, b_ = 1, 8192                                                # the largest Tp that reaches 0.39 at that mean (the bound falls as Tp grows at a fixed mean)
while b_ - a > 1:
    m_ = (a + b_) // 2
    a, b_ = (m_, b_) if plower(m_, lo) >= 0.39 else (a, m_)
Tp = a
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + PH)
rows = [("main loop: B * %d" % body, body * B),
        ("slice checks: ceil(B / 2^48) * 120", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 400", e2max * HIT),
        ("finished trails: tmax * (800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 1 * 800", CMAX * CUTOPS),
        ("recovery: (c + 2^48) * (%d + 64) + 600" % PH, capr * (PH + EXTRA) + 600),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
print("P_lower = %.5f" % plower(Tp, float(B * LANES / L)))
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 4912
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
Tp = 423  tmax = 28350  B = 48678446648581898093000000000000000000  e2max = 158673676913638267037924379174  c = 213682041875589312901794042787383999
memory bytes = 1048498
P_lower = 0.39000
main loop: B * 4248                                  206786041363175903099064000000000000000000
slice checks: ceil(B / 2^48) * 120                   20752869992541277252797840
stage-1 hits: e2max * 400                            63469470765455306815169751669600
finished trails: tmax * (800 + 3 * tmax)             2433847500
cut trails: 1 * 800                                  800
recovery: (c + 2^48) * (4241 + 64) + 600             919901190274411992043435103974427490375
setup and generator                                  4124400
N = 207705942616919806609432734460423869930515
certificate: 2^12499149 * 4912^100000 <= N^100000 < 2^12499150 * 4912^100000
log2(N/C) = 124.9914995383
time_log2 = 124.99150
```
