# sha256-r60 (the first 60 steps of the SHA-256 compression function): birthday search with 7 packed lanes per 256-bit word, chain value in the message words W5..W12

This is a credited derivative of our own entries on this lane, all declared as dependencies of this submission (same challenge): 5790b7ac-f746-4954-8dd2-0ad1dd3ae8d5 (round 64, 124.99150), 0bcb5aeb-b5ee-4cc4-a774-98cfb0d294d4 (round 40, 124.86300), 368d1718-a059-4780-9f08-8f0931a46f0d (round 39, 124.84811) and 01e31be9-0524-4b77-a40e-c1f862d506a8 (round 39, 124.98494). Their search with distinguished points, handlers, recovery walk, packed-lane kernel generator with the 52-byte message layout, ledger method and experiments are reused as they are. (They derive from our blake3 round-3 entries 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c, 3356413f-cd60-410c-8847-2266d6444ac5, cf8b0e92-4302-4813-907a-3c970c102646 (the packed-lane chain), 62cfd777 and from Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.) What is new here: (1) the round count is 60 of the 64 steps of the SHA-256 compression function, with the round constants of the steps 39 to 59 and the message schedule W16..W59; (2) the proof of the success probability of Section 4 is Lemma 2 v2: a theorem about the random function F with no premise besides H1 (lottery blocks, a rigorous trapezoid Chernoff bound, the cut count proved, the bound certified in exact arithmetic by Appendix A), with the adaptive-hazard premise declared as H1 clause (d) (Section 5), answering the rulings on our entries 5790b7ac and 0bcb5aeb (Section 9) and the judges' finding on our blake3 entry 41b32afc; (3) a register file of 128 words, because the 60-step line needs 63 registers. The kernel is 3912 operations for 7 trails and time_log2 is 124.97758.
The target is the plain one: the message is M(x) = P || x, a constant 20-byte prefix P (zero bytes) followed by the 32-byte string x, 52 bytes in one block with FIPS padding, standard IV, 60 steps, feed-forward, the complete 256-bit digest; no advice, no differential or structural property of the 60 steps is used (P is a constant of the program, the same for every input; it is not advice). The chain step is 3912 operations for 7 trails (559.86 per trail, 0.1223 of the 4576 operations of one reference compression). The price is a declared register file of 128 words of 256 bits (counted as memory, every transfer charged; the line needs 63), a program of 8,495 instructions of 36 bytes and a table of 29,298 entries.

## 1. Target and relation

Target `sha256-r60-prefix-v1` (the Pareto lane `sha256`, round 60). The two colliding messages have 52 bytes: M(x) = P || x with P = 20 zero bytes and x the 256-bit integer written as 32 bytes big-endian. FIPS 180-4 padding (0x80, zero bytes to 56 modulo 64, the 64-bit big-endian bit length 416) makes one block: W0..W4 = 0 (the prefix P), W5..W12 are the eight big-endian 32-bit words of x, W13 = 0x80000000, W14 = 0, W15 = 0x1A0 (416, the length in bits). The compression executes the steps with indices 0 to 59 of the standard schedule and constants, starts from the standard IV, and adds the incoming state to the working state at the end; the digest is the eight state words, big-endian (this is `verifier/hash_functions.py:digest(M(x), "sha256", 60)`). Write f(x) for the digest read as a 256-bit big-endian integer.
The walk is x -> f(x); the digest words H0..H7 are the next input words W5..W12 (chain word j is message word W(5+j)). The attack outputs x != y with f(x) = f(y); M(x) != M(y) are two distinct messages with equal complete 256-bit digests (the profile's message domain is "finite byte strings of bit length below 2^64"; a 52-byte string is in it, and no length is fixed by the profile).
The scalar digest of the program (`digest_words`) was compared outside the shipped experiments with the organizer reference `digest(M(x), "sha256", 60)` on 300 random messages: 0 differences. The packed kernel (`ext_regress.py`, not shipped) was compared with the reference on 8,197 random messages (one step) and on 7 chains of 60 steps; 0 differences in each. (The same check confirmed that the organizer reference at 64 steps equals hashlib.sha256 on 50 messages, so the round constants are in the standard order; this target is its first 60 steps with the standard IV and padding.) The program's own selftest (`python3 shrho.py --selftest`) compares the kernel with the scalar compression on 4,102 lanes (586 batches of 7, the full 256-bit f), on all-zero and all-one inputs, on 7 lanes chained for 4 steps, runs the register-allocated code on a register file, and runs the width-18 chain and search.

## 2. The attack (program `experiments/shrho.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 7 lanes. A point x is distinguished (a DP) when its low 32 bits are zero (chain word 7, the message word W12 of M(x)) and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 437. The density is theta = 437 / 2^122 and L = 1 / theta = 2^113.2285. The key of a DP is the 55 bits of x above bit 121 followed by the 9 low bits of F (F < 437 < 2^9, so those bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a DP.
1. 7 trails run in the 7 lanes: lane l of the packed words holds the current point of its trail. A batch is one evaluation of f for all 7 lanes by the generated straight line of Section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the mask of lanes whose low 32 bits (packed word 7) are all zero. If it is zero, the next batch runs at once.
3. For each set lane (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, Section 7) and start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 18 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 29,298 keys, when a second trail would be cut, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps of f, then step both together; at the first step with f(a) = f(b) and a != b output (a, b). Both lanes of one evaluation of the same kernel (the 3912 operations appear twice in the program, in the loop and in the recovery routine) are used, with an exact equality test of the two lanes on the 8 output words. At most capr = c + S batches are run (the program halts if l1 > capr).
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 shrho.py --ledger`): Tp = 437, L = 5316911983139663491615228241121378304 / 437, B = 48677996211575832668000000000000000000, Q = 7 B = 1.00136 * 2^128 evaluations, e2max = 158672208656105598749592900340, c = 219003239580123439013899561419187208 (= 2^117.398), table capacity tmax = 29,298 entries of 25 bytes. The trail numbers t stay below 2^16 (finished trails <= 29,298, cut trails <= 1, plus the 7 starts) and every length is below c + S < 2^119, so the 2-byte and 15-byte fields of an entry never overflow (the program asserts both when it stores an entry).
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice.

## 3. Operation ledger

### 3.1 Machine
Machine convention declared by this entry (supporting heuristic H3; the benchmark fixes none of the three points below). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices loads and stores; it gives no register count, no rule for constants and no rule for packing several independent computations into one word.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 128 registers (Section 3.5 prices smaller files and the absence of immediates). Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word, one operation each; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each. Constants (masks, the round constants, the IV words) are immediate operands, as in the organizer's reference count, which charges none for them. A word holds 7 independent values (lanes) of 36 bits; one machine operation on the word is one operation, the cost model pricing a word operation at 1/C whatever the word holds.
The main loop has no loads, stores or moves: the generated straight line needs 63 registers (`allocate` in the program assigns them; output word j is written into the register that held input word j, so the next batch reads the same registers), leaving 65 of the 128 for the loop counter, the limit and the handlers' temporaries. The register file is counted as memory: 4,096 bytes (Section 7).
The organizer's reference count C(sha256-r60) = 4576 (`reference_operation_cost` 4576 in `pareto_candidate.py --family sha256 --rounds 60 --show-contract`; the counter adds 84 per step: 2,812 at 39 steps) is used only as the unit: Unit = 4576 operations. Every instruction is charged 36 bytes of code (opcode, registers and an inline 256-bit immediate), also those with three registers; the straight line is not given a shorter encoding.

### 3.2 One batch = 3919 operations for 7 trails
Representation: lane l of a packed word occupies bits 36 l to 36 l + 35 of the 256-bit word (7 lanes, 252 bits): 32 data bits and 4 guard bits above them. The kernel is a straight line of 3912 operations on registers and immediates of the form REP * c (REP has a 1 at bit 36 l of every lane; c a 32-bit constant): add, AND, OR, XOR, shift left and shift right by an immediate.
Field invariant, enforced by the generator (`Tracer`): every register carries an upper bound on the value of a lane; the data bits of a result are always the 32-bit result of the corresponding SHA-256 expression, because additions are emitted only when the sum of the two bounds stays below 2^36 (otherwise the larger operand is first ANDed with REP * 0xFFFFFFFF), so no carry leaves a lane, and XOR and AND never leave the lane. The low 32 bits of a sum depend only on the low 32 bits of the operands, so garbage in the guard bits is harmless to the data bits. Rotation by r of the 32-bit lane: (x >> r) AND REP * (2^(32-r) - 1), then (x << (32-r)) AND REP * ((2^r - 1) << (32-r)), then OR: 5 operations. The first mask removes the bits that cross in from the next lane and the guard bits of the lane itself, which land at bit 32 - r and above; the second removes everything but the r wrapped bits (shifted-up guard bits land at bit 32 or above, and bits that overflow into the next lane land below bit 32 - r), so a rotation is correct for any lane value below 2^36 and needs no clean input. A shift right by k (the sigma functions) is 2 operations. The top lane's shifted-out bits (above bit 255) are lost in the machine and are masked off in every use.
Lines of the kernel (counted by the tracer; `python3 shrho.py --selftest` prints the counts per operation): 3912 = 2,410 rotation operations (482 rotations of 5) + 158 for 79 shifts right + 589 XOR + 108 AND (the choice and majority functions) + 502 additions + 145 masks that keep sums below 2^36. Per step of the compression: Sigma0 and Sigma1 are 17 operations each (3 rotations and 2 XOR); the choice is 3 (g ^ (e & (f ^ g))), the majority is 3 (it reuses the XOR a ^ b of the previous step as b ^ c); 7 additions (four for T1, one for T2, one for the new a, one for the new e) and 2 masks (new a, new e). Each schedule word W16..W59 costs 14 + 14 operations for the two sigma functions and 3 additions (and a mask when the bound requires it). The first steps fold the constant IV and the constant words W0..W4 and W13..W15 at build time; the IV is added again in the feed-forward (8 additions, with the masks they need).
Layout. The chain value is in the message words W5..W12 and the prefix P (20 zero bytes) in W0..W4. The generator (`Tracer`) does no operation on values that are constants in every lane, so the five compression steps 0 to 4, whose message words W0..W4 are constants, are folded entirely (the state after step 4 is a constant), and the schedule terms that combine constants cost nothing; the first variable additions are in the later steps and from W16 onward. It is a renaming of the input words: output word j is still written to the register of input word j, the chain value keeps its big-endian order, and the message is an ordinary message of the profile's domain. The prefix is the zero string; no other prefix was tried at 60 steps.
Validation: 4,102 lanes against the scalar digest in the selftest; 8,197 messages and 7 lanes chained for 60 steps against the organizer reference (Section 1); the register-allocated code executed on a register file gives the same words as the generated function (selftest).
The generator itself runs once at the start; its work is charged in the setup row (Section 3.3), its code and peak storage are accounted in Section 3.6 and Section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 3912 + stage-1 test 4 + loop control 3 = 3919 operations. Stage 1: the packed word 7 of the output (the low 32 bits of the next point, guard bits clear because the kernel's outputs are masked) is added to REP * 0xFFFFFFFF, ANDed with REP << 32 (bit 32 of a lane is set exactly when the lane's low word is non-zero), compared with REP << 32 and a branch: 4 operations (`FILT_OPS`). The test loses no event: a DP has all 32 low bits zero, so its bit 32 stays clear and the comparison fails.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no hit lane (probability about 1 - 2^-29) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers; every operation is one of the model's primitives):
- Stage-1 hit: XOR with REP << 32 gives the hit lanes at bit 36 l + 32. Scanning the 7 lanes costs at most 7 * 7 = 49 operations (shift by 36 l, AND, branch, increment, compare, branch). For a hit lane (shift register s = 36 l): the words 6, 5 and 4 are extracted ((P >> s) AND 0xFFFFFFFF: 2 operations each), the window test F < Tp is a compare and branch on word 6 and two zero tests on word 5 and on word 4 AND (2^26 - 1): 13 operations. Total below 100 per hit lane; charged **400** per hit lane (the hit budget e2max is enforced by a halt).
- Finished trail (a DP, new start): extraction of words 3 and 2 and key formation (about 25 operations), three read-modify-write field stores of the 25-byte entry (about 30), length = b - birth (3), the new start r + t' (1 add), insertion of its 256 bits in the lane: for each of the 8 words extract (2), shift left by s (1), clear the lane in the packed word (1) and OR (1): 40, plus the lane mask (2), lane arrays and counters (about 20). Total below 200; charged **800**. The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails (a halt on a full table).
- Slice check (every 2^48 batches): the 7 births (load, subtract, compare, branch: 4 each) and the slice counter: charged **120** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **800**; at most 1 cut trail (a halt on the second).
- Recovery batch (both lanes in one evaluation of the kernel, 3912 operations) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the inputs (needed to output the colliding pair): 39, charged as 64 per recovery batch (3976 per batch). The first l1 - l2 steps move one lane only and need no test, also inside the 3976.
- Setup and generator: 1 random word; the 7 starts r + t inserted in the lanes; counters; fixed part charged 4,800. The generator: 5,605 calls of the tracer and 3912 emitted lines, each charged 400 word operations: 3,806,800. Setup and generator together 3,811,600 operations = 2^9.70 units, charged in the time bound (3.4). There is no other preprocessing: no scan, no climb, no advice.
Code size, instructions: loop body 3919 + recovery copy of the kernel with its test 3976 + handlers, key scan, cut and slice checks and setup 600 = 8,495 instructions.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 3919 | 190,769,067,153,165,688,225,892,000,000,000,000,000,000 (= 1.9077e+41) |
| slice checks: ceil(B / 2^48) * 120 | 2.075e+25 |
| stage-1 hits: e2max * 400 | 6.3469e+31 |
| finished trails: 29,298 * (800 + 3 * 29,298) | 2,598,556,812 |
| cut trails: 1 * 800 | 800 |
| recovery: (c + 2^48) * (3912 + 64) + 600, c + 2^48 = 2^117.398 | 8.7076e+38 |
| setup and generator | 3,811,600 |
N = 191,639,824,097,205,163,234,532,582,996,280,715,658,556 = 1.916398e+41 operations.
N / 4576 = 4.1879e+37 units = 2^124.977578. Claim `time_log2` = 124.97758 (integer power certificate in Appendix A, rounded up with 2.1e-06 of slack). The main loop is 99.55 percent of it, recovery 0.45 percent.

### 3.5 Register file, immediates and smaller files
Premise H3: the machine has 128 registers of 256 bits. The generated line needs 63 (peak live words 59, no spills: `spill_ops(128)` = 0; `allocate` gives the registers and a check executes the allocated code). If the machine has fewer registers, the program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`) adds loads and stores to every batch (to the recovery copy too), and the table shrinks because the code grows:
| R | loads+stores per batch | operations per batch | table entries | Tp | time_log2 | success lower bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 128 (claimed) | 0 | 3,919 | 29,298 | 437 | 124.97758 | 0.39000 |
| 64 (Belady schedule; `allocate` needs 63, so a file of 64 needs a better allocator than the program's) | 0 | 3,919 | 29,380 | 438 | 124.97755 | 0.39000 |
| 32 | 54 | 3,973 | 29,265 | 437 | 124.99732 | 0.39000 |
| 16 | 113 | 4,032 | 29,116 | 434 | 125.01866 | 0.39000 |
Each row is the ledger of the program with that R (register file R x 32 bytes counted as memory, spill instructions counted as code). The claim assumes R >= 63; 128 is declared.
Immediates. The kernel has 1,270 operations with a 256-bit immediate operand (100 distinct patterns: the lane masks of the rotations and shifts, 0xFFFFFFFF, the round constants, the IV words). If the machine had no immediates, the 65 registers left over could hold the 65 most used patterns for the whole run (loaded once at setup) and every other use would be one load: 35 loads per batch (also in the recovery copy), table 29,197 entries, time_log2 124.99043.

### 3.6 Generator code and peak storage of the setup
The generator that builds the straight line at the start of the run is part of the machine code of this entry: the tracer (`Tracer`, with `build_lines`) and the register allocator (`allocate`), which are 1,190 bytecode instructions (`python3 shrho.py --gencode`, one instruction each) and are charged 1,190 instructions * 36 bytes = 42,840 bytes. It keeps no node table: the emitted lines are the code records themselves. Its scratch (model `GEN_SCRATCH` = 24,576 bytes): the last use and the register of each emitted line (2 + 2 bytes each, 3912 lines), 256 free-register flags, the output marks, and the 16-byte values of the 60 schedule words and the state.
Layout. The setup phase holds the main code (counted at its final size, 305,820 bytes; it is written as the generator emits it), the counters (6,144), the generator's code image (42,840) and its scratch (24,576): 379,380 bytes. The generator is never called after setup. In the search phase the same region holds the table (732,450 bytes), the register file (4,096) and the counters: main code + counters + register file + table = 1,048,510 bytes. The memory of the entry is the larger of the two, 1,048,510 bytes (66 bytes to spare under 2^20); the region is 742,690 bytes against 67,416 bytes of generator image and scratch. The table size of Section 7 is the largest that fits.
Measured peak memory of the generator (not the machine model, which is the byte account above): the circuit generator written in freestanding C (source embedded in `experiments/shrho.py` as `GEN_C`, printed by `python3 shrho.py --gen-c`, 9,807 bytes) compiled to WebAssembly and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes emits the identical program: 3,912 instructions, 63 registers, 5,605 tracer calls, and the instruction text equal line by line to the Python generator's (sha256 equal). Its static arrays total 333,828 bytes, of which 305,820 are the code region (36-byte records) and 6,144 the counters; its scratch is 20,776 bytes and its values 1,088 bytes; it needs 2,239,076 wasm operations, below the 3,806,800 word operations the ledger charges for the generator. The guest links in 6 pages.

### 3.7 Preprocessing
None offline. The generator is run inside every attempt and is charged in the setup row; the claim declares preprocessing_log2 = 9.8, the setup and generator row, which is also inside time_log2. The memory figure of Section 7 covers this preprocessing: the generator runs in the setup phase of the same attempt, its code image and scratch are in the setup-phase total of Section 3.6 (379,380 bytes), and nothing it produces is stored outside the 1,048,510 bytes of the search phase.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of f replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about f itself) and the lazy-sampling facts of Step 1 (statements about F); H1 is the only premise of this entry. H1 clause (d) (Section 5) is the premise that the lazy-sampling hazard of F also holds for the adaptive choices of the program (which trails finish, are cut or abort depend on earlier outputs). The numbers below are printed by `python3 shrho.py --loss` (the function `_lossq`; Appendix A recomputes them with its own copy and certifies the bound in exact rationals and 60-digit decimals: its line `P_lower certified` = 0.390000003188).
Lemma 1 (a statement about f itself, no premise). A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output: both trails continue identically from f(x), so they end at the same DP with the same key and the stored lengths let step 6 align and walk them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies f(x) = f(y) with x != y; the recovery checks equality before it returns.
The key determines F (F < 437 <= 2^9 and the key holds its 9 low bits), so equal keys of two DPs differ only if their bits above 176 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds f^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 is stated for the setting of Sections 2 and 3. LANES = 7 lanes, B batches, Q = LANES B evaluations numbered t = 1..Q batch by batch and lane by lane inside a batch, b(t) the batch of t. N = 2^256. A point is a DP when its low 32 bits are zero and the next 90 bits are below Tp: theta_D = Tp / 2^122, L = 1 / theta_D. Cut age c = ceil(kappa L) (kappa = 18), slice interval S = 2^48, M = c + S, h = floor(c / 2), q = Q / L, N' = (1 - theta_D) N, table capacity tmax, CMAX = 1 (the program halts when a second trail would be cut). H = (Q (Q - 1) / 2 + 2^16 Q) / N'. z(m) = ((LANES + 1) / 2) m (m + 1) + 2 Q (m - h)+.


Lemma 2. Let F be a uniformly random function on 256-bit values and P_F the success probability of the attempt with every evaluation replaced by F (lazy sampling). Let k be the least integer with e^-q (e q / k)^k <= EPS = 1e-3; let z* be any number with e^(-s z*) Phi_up(s)^(k - 1 + LANES) <= EPS for some s > 0, Phi_up of Step 5.3; let w >= 1 satisfy ln w >= w kap0 / N' with kap0 = 2 M Q + z(M). Put

    theta = [ w (P0 - 2 k Q - CUT - z* L^2) - (w - 1)(Q (Q - 1) / 2 + 2^16 Q) ] / N'
    P0 = LANES^2 B (B - 1) / 2,   CUT = M Q + min( (M - h) Q, z* L^2 / (LANES + 1) + S Q ).

Then, with no premise,

    P_F >= 1 - e^-theta - 2 EPS - P_cut - delta - P_key - P_table - P_long - P_tiny,

where

    P_cut   = P(Binomial(k + LANES + 1, p) >= 2) + E_S + E_X + E_J2a + E_J2b + E_Y           (Step 6)
              p = e^(-c/L) >= (1 - 1/L)^c,  p2 = e^(-(c-1)/L) (1 + (c - 1) theta_D / (1 - theta_D)),  PP = Q (Q - 1) / (2 N')
              E_S = Q L / N'
              E_X = (Q / N') L e^(-(c - 2)/(2L)) (2 + (c - 1)/L) + PP p2
              E_J2a = Q L H / N' + (Q + 2^16) L PP / N'
              E_J2b = PP (1 - theta_D) p2
              E_Y = e^(-(c - 1)/L) H
    delta   = M (Q + 2^16) / N'                                                                (Step 3)
    P_key   = C(tmax, 2) / (2^kb Tp),  kb = min(64 - bitlength(Tp - 1), 134)
    P_table = e^-q (e q / (tmax - 59))^(tmax - 59)
    P_long  = (k + LANES + 1) e^(-c/L) S / L
    P_tiny  = Q 2^16 / N + Q k / N + k^2 L / N + exp(-300 + (e^5 - 1) H) + 2^-99               (Step 7; needs 240 M <= Q, true here: M < 2^120 and Q > 2^127)

H1 (clauses (a) to (d), declared, score-critical) is the only premise of the entry: it states that the real attempt succeeds at least as often as A_F. Lemma 2 v2 is a theorem about F.

Numbers of this entry (`python3 shrho.py --loss`): theta = 0.49876, e^-theta = 0.60728, z* = 1.3586e+06 L^2, w = 1.00194, k = 28631, n_max = k - 1 + LANES = 28637, P_cut = 7.22e-05, delta = 6.44e-04, P_key = 2.7e-11, P_table = 2.4e-12, P_long = 1.0e-23; the float plan target is P_MIN = 0.390000001 and the bound printed is 0.390000001; Appendix A recomputes the whole bound in exact arithmetic (`P_lower certified` = 0.390000003188), which is the proved value: P_F >= 0.390000003188 >= 0.39. B is the least multiple of 10^18 for which the float bound reaches P_MIN.

Proof of Lemma 2.

**Step 0 (notation).** A trail is the run of evaluations of one lane between two restarts; a(t) is the number of earlier evaluations of the trail of t (its age); a trail is finished (its last evaluation returns a DP), cut (a slice check restarts it at age >= c) or open (the halt comes first). Every length is at most M, a trail of length at most c is never cut. An evaluation is fresh when its input was not evaluated before. A collision is a fresh evaluation whose value equals an earlier value (an earlier output or a start). The starts r + t' (t' < 2^16) differ from every value the run produces except with probability Q 2^16 / N (r is uniform and independent of F); this event is excluded below and charged in P_tiny, so a non-fresh evaluation exists only after a collision on its trail.

**Step 1 (lazy sampling with a lottery).** Realise F by independent uniform values V_1, V_2, ...: the t-th evaluation returns V_t if it is fresh and the stored value otherwise. This is the lazy sampling of F for every adaptive choice of the points. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(theta_D), one per evaluation index, fresh or not; given all of them the V_t are independent and uniform on their class. Index t belongs to lane (t - 1) mod LANES, and the lane positions of a lane are its indices in increasing order; the lottery is extended beyond Q by further independent draws (used in the proof only). G_t is the history of the first t evaluations together with the whole lottery; F_t is the history of the first t evaluations together with xi_1..xi_t only.

- (L1) If t is fresh and xi_t = 0, then P(V_t = v | G_(t-1)) = 1 / N' for every non-DP value v (and 0 for DP values).
- (L2) Whether t is fresh, its input, its batch, its age and the trails before t are G_(t-1)-measurable.
- (L3') Lottery blocks. Cut the lottery of a lane after every 1: the blocks (a run of 0s and the 1 that ends it) have i.i.d. geometric lengths beta on {1, 2, ...}, P(beta >= m) = (1 - theta_D)^(m - 1) (a fixed i.i.d. sequence, no selection). Take on each lane the blocks that begin at a position of the run (batch <= B), lane after lane, then further independent geometric variables: the result is an i.i.d. sequence beta_1, beta_2, ... (the number of blocks taken from a lane is a stopping time of that lane's sequence, and the lanes are independent). The number of blocks taken is at most N1 + LANES, since every block but the last of a lane ends with a 1 inside the run.
- (L4) N1 = xi_1 + ... + xi_Q is exactly Binomial(Q, theta_D): a sum of Q independent Bernoulli variables by construction. A fresh evaluation outputs a DP if and only if its xi is 1, so the fresh DP outputs are at most N1, and P(N1 >= k) <= e^-q (e q / k)^k (Chernoff: the binomial MGF is below the Poisson MGF), which is <= EPS by the choice of k. Repeated inputs after a merge have correlated DP indicators, but they are not counted by N1: the count is over the lottery.
- (L5) The run up to evaluation t is F_t-measurable (it depends on V_1..V_t only, and V_s depends on xi_s and an independent uniform). If s is a stopping time of (F_t), for example the start of the j-th trail, the lottery after s is independent of F_s and i.i.d. (strong Markov property of an i.i.d. sequence).

**Step 2 (usable collisions).** For y an evaluation on a lane let f(y) be the first position >= y on that lane with xi = 1, and d(y) = b(f(y)) - b(y) + 1. For fresh t with xi_t = 0, Y_t is the set of evaluations y with (i) b(y) < b(t), y fresh, the output of y not a DP, y not on the trail of t; (ii) every evaluation of the trail of y up to t - 1 is fresh and none is a collision; (iii) b(f(y)) - s(y) + 1 <= c and b(f(y)) <= B, s(y) the batch where the trail of y started; (iv) b(t) + d(y) - 1 <= B and a(t) + d(y) <= c. Y_t = empty for other t. Y_t is G_(t-1)-measurable (L2). C_t: t fresh, xi_t = 0 and V_t = F(y) for some y in Y_t (usable collision); D_t: a collision at a fresh t with xi_t = 0 that is not C_t.
Claim 1. Let C_t occur with y in Y_t, and assume that after t no fresh evaluation on the trail of y before f(y) is a collision, and that the run does not stop early (second cut, table full, stage-1 budget, key false match). Then the program outputs a pair. Proof. Let x be the input of t and p_k the input of y, so F(x) = F(p_k): the trail of t continues with the points p_(k+1), p_(k+2), ... that the trail of y evaluates after y. The j-th of them is evaluated by the trail of y in batch b(y) + j and by the trail of t in batch b(t) + j > b(y) + j, so the trail of t only repeats points that were already evaluated (not fresh). By (ii), (iii) and the assumption, the trail of y is not cut and its evaluations up to f(y) are fresh with no collision; f(y) is the first position with xi = 1, so the trail of y finishes there, with a DP, within c batches and before the halt. The trail of t reaches the same point d(y) - 1 batches after t, in batch b(t) + d(y) - 1 <= B and at age at most a(t) + d(y) <= c by (iv): it is not cut and it finishes with the same DP. The two trails are different (y is not on the trail of t, (i)), the inputs x and p_k are different (x is fresh) and F(x) = F(p_k): Lemma 1 applies. QED.
Claim 2. For fresh t the values F(y), y in Y_t, are pairwise different. Proof. If y and y' in Y_t, y' evaluated later, had the same value, V_(y') would equal an earlier value, so y' is a collision on its own trail, against (ii). QED.

**Step 3 (disturbance).** After the first usable collision tau the trail of y has at most c further fresh evaluations before f(y), each a collision with conditional probability at most (Q + 2^16) / N' by (L1); so P(C occurs and the program does not halt early) >= P(C occurs) - delta - P(early halt), delta = M (Q + 2^16) / N'.

**Step 4 (supermartingale).** S_t = sum of |Y_s| over s <= t; u_t = |Y_t| / N' and h_t = (t - 1 + 2^16 - |Y_t|) / N' (for every t); H_t = sum of h_s; R_t = number of unusable collisions up to t; M_t = exp(S_t / N' - (w - 1) H_t) w^(R_t) 1[no usable collision up to t]. For fresh t with xi_t = 0, P(C_t | G_(t-1)) = u_t exactly (L1, Claim 2) and P(D_t | G_(t-1)) <= h_t, so E[M_t / M_(t-1) | G_(t-1)] <= e^(u_t - (w - 1) h_t) (1 - u_t + (w - 1) h_t) <= 1; for the other t, M_t <= M_(t-1). Hence E M_Q <= 1 and P(M_Q >= e^x) <= e^-x. The same computation with every collision at a fresh t with xi_t = 0 counted (hazard at most (t - 1 + 2^16) / N') gives E[w^(#collisions)] <= e^((w - 1) H), so P(60 or more collisions) <= exp(-300 + (e^5 - 1) H) with w = e^5 (the term is charged in P_tiny).

**Step 5 (counting S_Q from below).**

Let A be the event: no usable collision; the run lasts Q evaluations; K <= 1; fewer than 60 collisions; no start coincides with a value; no fresh evaluation with xi = 1 returns an earlier DP value; N1 <= k - 1; no free finished trail is longer than c. On A count the pairs (y, t) with b(y) < b(t): P0 = LANES^2 B (B - 1) / 2. A pair is in S_Q (y in Y_t, t fresh, xi_t = 0) unless one of the following holds.

5.1 The exclusions.

- (a) xi_t = 1, or y has a DP output: at most 2 k Q pairs (at most k - 1 positions with xi = 1, at most k - 1 fresh DP outputs, (L4); a non-fresh y is on a colliding trail, (b)).
- (b) y or t on a colliding trail (a trail that contains a collision): at most 2 M Q pairs per colliding trail, and on A there are at most R_Q of them. Charged as R_Q kap0 with kap0 = 2 M Q + z(M) (the z(M) part is no longer needed with the blocks of 5.2 and is kept as slack).
- (c) the cut trail (K <= 1 on A; if it is colliding it is already in (b)). As y: (iii) fails for all its y, at most M Q pairs. As t: its evaluations are fresh with xi = 0 and condition (i) to (iii) concern y only, so a pair (y, t) is lost through t only by (iv) second part, a(t) + d(y) > c. For a y on a free finished trail with d(y) = d, the evaluations of the cut trail with age above c - d are at most d + S (its ages are below M), so these pairs are at most the sum of d(y) + S over y, which is at most sum over free finished trails of X(m) + S Q, X(m) = m (m + 1) / 2; and also at most (M - h) Q (the t of age above h, each with at most Q partners; for a(t) <= h the loss needs d(y) > c - h and is charged to y in (g)). Since (LANES + 1) X(m) <= z(m), on Z <= z* L^2 the cut trail costs at most CUT = M Q + min((M - h) Q, z* L^2 / (LANES + 1) + S Q).
- For the remaining trails (free trails that are finished or open: every evaluation fresh, no collision), with m the length:
- (d) y and t on the same trail: at most X(m) pairs.
- (e) y on an open trail of age a <= m: (iii) fails (b(f(y)) > B); the pairs with b(t) > b(y) are at most LANES a (a - 1) / 2 <= LANES X(m).
- (f) y on a finished free trail: by (iv) first part the batches b(t) > B - d(y) + 1 are lost, at most LANES (d(y) - 1) per y, in all at most LANES X(m).
- (g) (iv) second part: a(t) + d(y) > c forces a(t) > h or d(y) > c - h; at most (m - h)+ evaluations of each kind per trail, so at most 2 Q (m - h)+ pairs per trail.

Hence S_Q >= P0 - 2 k Q - R_Q kap0 - CUT - Z, where Z = sum over the free finished or open trails of z(m).

5.2 Trail sums by lottery blocks. A free trail lies in one lottery block of its lane: all its evaluations are fresh, so xi = 0 at every non-final position (the output is not a DP) and, if it finished, xi = 1 at its last. Its length is at most min(beta, M) for that block. Two free trails that are finished or open lie in different blocks: a finished free trail ends at the 1 of its block, and an open trail is the last trail of its lane (the cut trail, which may share a block with one of them, is charged in (c)). As z is increasing, on N1 <= k - 1, by (L3'),

    Z <= sum of z(min(beta, M)) over the blocks of the run <= Z' := sum_{i <= k - 1 + LANES} z(min(beta_i, M)),

a sum of k - 1 + LANES independent identically distributed terms, with no selection and no indexing of trails. In particular sum of X(m) over free finished trails <= Z / (LANES + 1).

5.3 The tail of Z'. Coupling: with E ~ Exp(1) and lambda = -ln(1 - theta_D) >= theta_D, beta = ceil(E / lambda) has the law of the block length and beta <= L E + 1. With x = min(beta, M) / L <= min(E + 1/L, uc), uc = M / L, uh = h / L,

    z(min(beta, M)) / L^2 = HZ (x^2 + x / L) + 2 q (x - uh)+ <= zeta(x + 1/(2L)),   zeta(v) = HZ v^2 + 2 q (v - uh)+,   HZ = (LANES + 1)/2,

so z / L^2 <= zeta(V) with V = min(E + delta1, uc'), delta1 = 3/(2L), uc' = uc + 1/(2L). For s > 0,

    Phi(s) = E exp(s zeta(V)) = e^delta1 [ integral from delta1 to uc' of phi(y) dy + phi(uc') ] <= e^delta1 [ integral from 0 to uc' of phi + phi(uc') ],   phi(y) = exp(s zeta(y) - y).

zeta is convex on [0, inf) (HZ v^2 is convex and 2 q (v - uh)+ is convex; its slope jumps up by 2 q at the hinge), s zeta(y) - y is convex, and phi, the exponential of a convex function, is convex. A convex function lies below its chord on every interval: the integral of phi over a panel [a, b] is at most (b - a)(phi(a) + phi(b)) / 2. Summing over the K panels of [0, K hh] with K hh >= uc' gives

    Phi(s) <= Phi_up(s) := e^delta1 [ hh (phi(0)/2 + phi(hh) + ... + phi((K - 1) hh) + phi(K hh)/2) + phi(uc') ],

an upper bound (a midpoint sum would be a lower bound for convex phi). Chernoff: P(Z' > z L^2) <= e^(-s z) Phi(s)^n <= e^(-s z) Phi_up(s)^n for every s > 0, n = k - 1 + LANES, so z* = (n ln Phi_up(s) - ln EPS) / s gives P(Z' > z* L^2) <= EPS. s is chosen by a search in floats; only its certified evaluation matters (any s > 0 gives a valid bound).

Arithmetic. The program (`_zq`, K = 20,000 panels) multiplies the float trapezoid sum by 1 + 2^-30, which covers the float rounding of the 20,001-term sum (relative error below 1e-11) and the shifts of order 1 / L < 2^-110; it plans with the target P_MIN = 0.390000001. Appendix A (`certify`) recomputes z* and the whole bound in exact rationals and Python decimal arithmetic at 60 significant digits: the nodes i hh are exact, q is rounded up and uh down inside zeta, uc' is rounded up inside zeta and down inside e^-uc', every exp and ln is correctly rounded by the decimal module, and every transcendental result is moved outward by a relative 1e-40, far above the accumulated rounding (below 1e-50). The certified value is a proved lower bound on P_F. The trapezoid excess is of order hh^2 and is inside the bound; with K = 20,000 panels it costs about 1e-7 of probability.

5.4 theta. Take w >= 1 with ln w >= w kap0 / N' (the program iterates w = exp(w kap0 / N) from 1, which converges to the smallest root from below, and multiplies the result by 1 + 2^-40; Appendix A checks ln w >= w kap0 / N' in decimals). Summing h_t over all t gives H_Q = (Q (Q - 1) / 2 + 2^16 Q - S_Q) / N'. On A, with Z' <= z* L^2 and no usable collision,

    ln M_Q = [w S_Q - (w - 1)(Q (Q - 1) / 2 + 2^16 Q)] / N' + R_Q ln w
          >= [w (P0 - 2 k Q - CUT - z* L^2) - (w - 1)(Q (Q - 1) / 2 + 2^16 Q)] / N' + R_Q (ln w - w kap0 / N') >= theta.

So P(no usable collision, A, Z' <= z* L^2) <= P(M_Q >= e^theta) <= e^-theta. (No N to N' replacement and no 2^-100 rounding of P0 is used: P0, k Q, Q (Q - 1) / 2 and N' enter exactly.)

**Step 6 (the cut count).** Let K be the number of trails that the run cuts or would cut (the second one halts the run). Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.

(i) K_A. A trail counted by K_A has c fresh evaluations with non-DP outputs at c consecutive positions of its lane, so xi = 0 there; different such trails of a lane use disjoint positions. Scan each lane with trials: a trial starts at the current position u and succeeds if the c positions u, ..., u + c - 1 are all 0 (next trial at u + c); otherwise it fails at its first 1 (next trial after that 1). The scan of a lane stops at the first trial that would start after the run. Inside a maximal run of 0s the trials start at its first position and succeed floor(length / c) times, the largest number of disjoint length-c windows it holds; so K_A on a lane is at most the successes on that lane. Every failure but the last of a lane ends at a 1 of the run, so the failures are at most N1 + LANES <= k - 1 + LANES on N1 <= k - 1. Trial outcomes are independent Bernoulli(p'), p' = (1 - theta_D)^c <= p = e^(-c/L) (disjoint positions of an i.i.d. lottery; lanes concatenated as in (L3')). All successes therefore occur before failure number k + LANES of an infinite i.i.d. trial sequence, and two successes before that failure means two successes among the first k + LANES + 1 trials:

    P(K_A >= 2, N1 <= k - 1) <= P(Binomial(k + LANES + 1, p) >= 2) = 1 - (1 - p)^n2 - n2 p (1 - p)^(n2 - 1),   n2 = k + LANES + 1

(the tail increases with p, so p = e^(-c/L) is allowed).

(ii) K_B. A trail T in K_B has a first non-fresh evaluation at age <= c - 1. Its previous evaluation t (age a(t) <= c - 2, T fresh up to t, so a(t) <= g(t), where g(t) is the number of consecutive 0s of the lottery just before t on its lane) is fresh, and V_t equals the input of an earlier fresh evaluation e' (the first evaluation of that input; a start is excluded). Call t the joining collision of T and e' its target. For a lane position e let rho(e) be the number of positions from e to the first 1 at or after e (inclusive), and f'(e) that position: rho is a function of the lottery, so it is G-measurable. Choose T in K_B with the earliest joining collision. One of the following root events occurs:

- S: e' is on T itself. T then cycles through its own non-DP points and is cut.
- X: e' is on another trail T' and a(t) + rho(e') >= c (hence g(t) + rho(e') >= c).
- J2a: e' on T', a(t) + rho(e') <= c - 1, and T' has a collision at a fresh position in [e', f'(e')).
- J2b: e' on T', and e' lies in a run of 0s of length >= c of its lane.
- Y: some trail has a collision at a fresh evaluation t'' while it has been fresh for at least c - 1 evaluations (g(t'') >= c - 1).

Proof that one occurs. Suppose not S, X, J2a. T evaluates the inputs evaluated by T' from e' on, one batch later or more, so T repeats them (non-fresh) while T' is ahead. If T' evaluates e', e' + LANES, ..., f'(e') freshly (no collision there by not-J2a, and every non-fresh evaluation of T' is preceded by a collision of T'), the output at f'(e') is a DP (fresh, xi = 1), and T outputs the same DP at age a(t) + rho(e') <= c - 1, before any slice check can cut it: T is not cut, a contradiction. If the run ends first, T, which is behind, is not cut either. So T' is cut before f'(e'), with all its evaluations from e' to the cut fresh. If all evaluations of T' from its start to the cut are fresh, they are >= c consecutive 0s containing e': J2b. Otherwise T' has a non-fresh evaluation before e', hence a joining collision before e' and before t; if it is at age <= c - 1, T' is in K_B with an earlier joining collision than T, against the choice of T; if not, the first c evaluations of T' were fresh and T' collided at age >= c - 1 while fresh: Y. QED.

Expected numbers of root events, each from the hazard (L1) (a collision of t with a given earlier value has conditional probability at most 1/N' given G_(t-1), which includes the lottery, so lottery conditions can be attached):

- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; E[g(t) + 1] <= sum_{i >= 0} (1 - theta_D)^i = L, so E_S <= Q L / N'.
- X: E_X <= sum over pairs e' < t of P(rho(e') + g(t) >= c) / N'. Different lanes: rho(e') - 1 and g(t) are independent and dominated by geometric variables on {0, 1, ...}, so the probability is at most P(at most one 1 in c - 1 Bernoulli trials) = (1 - theta_D)^(c-1) + (c - 1) theta_D (1 - theta_D)^(c-2) <= p2. Same lane, e' = t - j LANES: if a 1 lies between them the two runs of 0s are disjoint and the same bound p2 holds; if the j positions are all 0, the probability is at most (1 - theta_D)^j T(c - 1 - 2j) with T the tail above (T = 1 below 1); the sum over j of these is at most L e^(-(c - 2)/(2L)) (2 + (c - 1)/L). Hence E_X <= (Q / N') L e^(-(c-2)/(2L)) (2 + (c-1)/L) + (Q (Q - 1) / (2 N')) p2.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of rho(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E rho = L), and each such position is a collision with probability at most (Q + 2^16) / N': E_J2a2 <= (Q + 2^16) L Q (Q - 1) / (2 N'^2).
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta_D) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= (Q (Q - 1) / (2 N')) (1 - theta_D) p2.
- Y: P(g(t'') >= c - 1) <= (1 - theta_D)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H.

So P(K >= 2) <= P(K_A >= 2, N1 <= k - 1) + P(N1 >= k) + P(K_B >= 1) <= P(Binomial(n2, p) >= 2) + E_S + E_X + E_J2a + E_J2b + E_Y + [P(N1 >= k), charged once as EPS]. No premise about K is used. The bounds on S and J2a are not small (they are about Q L / N' each); they are the real cost of trails that close a cycle or join a path that is itself disturbed.

**Step 7 (the sum).** The attempt fails only if (no usable collision) or (an early halt) or (a disturbance after tau, Step 3). No usable collision is covered by: e^-theta on A and Z' <= z* L^2; P(Z' > z* L^2) <= EPS; P(N1 >= k) <= EPS; the complement of A, whose parts are: K >= 2 (P_cut), 60 or more collisions, a start coincidence (Q 2^16 / N), a fresh xi = 1 evaluation returning an earlier DP value (at most k (k + 60) L / N <= k^2 L / N + Q k / N), a free finished trail longer than c (P_long), and the early halts. Early halts: the second cut (P_cut, counted once); the table full (finished trails are at most N1 + 59, so tmax keys need N1 >= tmax - 59: P_table); a key false match (P_key, the stored ends are at most tmax fresh DP values, uniform on the DP class); the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^32: the fresh stage-1 hits are at most the sum of eta_t = 1[low 32 bits of V_t zero], exactly Binomial(Q, 2^-32), above 1.5 mu2 with probability at most e^(-0.108 mu2); the repeated hits after merges come from at most 60 colliding trails, each repeating at most M points that lie in at most 60 lane windows of total length at most M, and every such union of windows holds more than 2 M / 2^32 hits with probability at most e^(-0.386 M / 2^32), so with 240 M <= Q (checked) the repeated hits are below mu2 / 2 except with probability below e^-1000; a recovery with no pair (a key false match, counted, or a start on another trail, 2^-100). P_long: a free finished trail longer than c is fresh from its start, so its lottery from its start has c 0s and a 1 within the next S positions; by (L5) and Wald's identity the expected number of trails with that property is (1 - theta_D)^c (1 - (1 - theta_D)^S) E[J] <= e^(-c/L) (S / L) (q + LANES + H + 1), J the number of trails started (finished trails <= N1 + collisions, at most one cut restart), and k + LANES + 1 >= q + LANES + H + 1. All terms of order 2^-99 or below are collected in P_tiny. This proves the lemma. QED.

Sensitivity to H1 (d). If the hazard of a collision is (1 - eps) / N instead of 1 / N (clause (d) of H1; the same sensitivity as a deficit eps of the pair-collision rate in clause (a)), the plan of this program (same lemma with N / (1 - eps)) needs, to restore 0.39: 0.0072 bit for eps = 0.01 (Tp 435); 0.0370 bit for eps = 0.05 (Tp 426); 0.0760 bit for eps = 0.10 (Tp 415); 0.2075 bit for eps = 0.25 (Tp 378). No other premise enters Lemma 2.

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function f and about one attempt; it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved: an assumption, no proof is known. Its content, in the terms Lemma 2 uses, is four clauses: (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of f from the starts r + t have the first-collision law of a random mapping; (c) whether an iterate is a DP is independent of the collision events and has probability 437 / 2^122; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of f; clause (d) is that this adaptivity does not lower the collision hazard, that is, for every fresh evaluation, given the whole history of the run and which later outputs are distinguished points, the output equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard that F has by construction, L1 of Section 4). Clause (d) replaces the fixed-size birthday step of the Lemma 2 of our earlier entries on this lane (the same step that the judges asked to be proved or declared on our blake3 round-4 entry 41b32afc, finding F1-adaptive-finished-trail-conditioning, aggregate heuristic H4); it is both: Lemma 2 now proves the bound for F from the hazard alone (a supermartingale over the evaluations, no conditioning on which trails finish), and (d) is the premise that f has that hazard. Nothing else in the success bound is heuristic: Lemma 1, the lazy-sampling facts, the supermartingale, the counting of pairs and the Chernoff bounds are proved in Section 4 for F; Sections 3 and 7 are counts of the program. Sensitivity: a hazard (1 - eps) / N costs the same as a deficit eps in clause (a): 0.0072 bit for eps = 0.01 (Tp 435); 0.0370 bit for eps = 0.05 (Tp 426); 0.0760 bit for eps = 0.10 (Tp 415); 0.2075 bit for eps = 0.25 (Tp 378) (Section 4). The only evidence for (a) to (d) is the program checks of Section 6, which do not reach the full 256-bit event and are not used as estimates.
Evidence that the program is right and that nothing gross is wrong is produced by the two organizer experiments (Section 6). They are program checks: the organizer recomputes every returned pair, the counts of returned pairs are reported, and they are not used as estimates of any number of this entry. No quantitative inference is drawn from a count, no confidence interval is formed, and the entry does not rely on the independence of trials (the trial seeds are public and the experiment is a check of the program). The program also prints its own observations (`python3 shrho.py --stats`, seeds from SHA-256 of a counter), which are untrusted and are only descriptive:
    T3 n=18: attempts returning a verified pair: target 126 of 256, ideal function 119 of 256
    T1 n=10 fresh K: 256 runs, mean first repeat 37.55 (sqrt(pi N/2) = 40.11)
    T2 width 256: 448 points, 16-bit projections, equal pairs per trial if uniform 1.5278, trials with a pair if uniform 0.7830
      source uniform (86 trials): returned pairs 65 (uniform reference 67.3); w0 119 (uniform reference 131.4); w3 130 (uniform reference 131.4); w7 129 (uniform reference 131.4); xor8 115 (uniform reference 131.4); sum8 121 (uniform reference 131.4); p01 131 (uniform reference 131.4); p23 133 (uniform reference 131.4)
      source counter (85 trials): returned pairs 63 (uniform reference 66.6); w0 120 (uniform reference 129.9); w3 137 (uniform reference 129.9); w7 125 (uniform reference 129.9); xor8 137 (uniform reference 129.9); sum8 121 (uniform reference 129.9); p01 140 (uniform reference 129.9); p23 120 (uniform reference 129.9)
      source iterates (85 trials): returned pairs 69 (uniform reference 66.6); w0 134 (uniform reference 129.9); w3 134 (uniform reference 129.9); w7 102 (uniform reference 129.9); xor8 127 (uniform reference 129.9); sum8 125 (uniform reference 129.9); p01 140 (uniform reference 129.9); p23 140 (uniform reference 129.9)
Run by the organizer's pipeline on this program with the public seed (the pipeline reruns each experiment and requires identical output), reported without inference:
    shrho-n18 (organizer run, public seed): 124 of 256 trials returned a pair that the organizer verified; ideal-function control (program's own) 120 of 256; family-law runs at n = 10 (program's own): mean first repeat 37.98; halts target 42, ideal 56.
    proj-k0-w256 (organizer run): 201 of 256 trials returned a verified pair; by source: uniform 66 of 86; counter 68 of 85; iterates 67 of 85; equal pairs in the seven projections (program's own), total over 256 trials: w0 368, w3 387, w7 383, xor8 391, sum8 407, p01 388, p23 391.
An unsuccessful attempt of the width-18 experiment either ends with a halt of the program (a budget, or "recovery found no pair" when a trail start lies on another trail, which is frequent at width 18 and has probability below 2^-100 at width 256, Section 4) or runs its 92 batches without finding a pair; the single attempt is not amplified. The ideal function behaves the same way.
Toy-scale end-to-end runs (outside the shipped experiments, same program, same kernel, development machine; `toy_run.py`, not shipped): n = 30 (plan(30)): 13 of 30 single attempts returned a pair, 13 of 13 confirmed by the organizer reference (distinct messages, equal low 30 bits of the complete 60-step digests); 23 s of CPU in all; the earlier entries also ran n = 40 and 48, not repeated here.
Not tested: the full 256-bit functional graph; iterations of length above 2^40; the search above width 40. A deviation of f from H1 that raises the collision rate only helps; one that lowers it by eps costs the table of Section 4.


## 6. Experiments

Two organizer experiments run the shipped program `experiments/shrho.py` (the program dispatches on the experiment id; no outside code or library is used; the standard library only).
`shrho-n18`: per trial, from the trial seed, one attempt of the 7-lane search at width n = 18 (DP = low 2 bits zero, plan(18): 92 batches of 7 lanes, cut rule, table, recovery with the same kernel) on the target chain f (the low 18 bits of the digest of the 52-byte message M(x) = P || x with x < 2^18); the trial returns the two 52-byte messages M(x), M(y) when the attempt succeeded and two nulls otherwise. The checked event is that the complete 60-step digests agree in the low 18 bits and the messages are distinct. Observations (untrusted): the same attempt on the ideal function, and one family-law run with a fresh random 20-byte prefix at n = 10.
`proj-k0-w256`: per trial, 448 points of the target at full width 256 evaluated with the packed kernel (source by trial index mod 3: uniform inputs from the seed, counter inputs r + i, iterates of f from 7 seed-derived starts), returning two distinct points whose complete digests agree in the low 16 bits when the set contains such a pair, two nulls otherwise. The checked event is that the digests agree in the low 16 bits and the messages are distinct. Observations (untrusted): the numbers of equal pairs in seven 16-bit projections of the digest.
They check the kernel at full width, the packed search, lane insertion and extraction, the table, the recovery and the message construction on the real target. They do not measure the cost or the success probability at width 256. Running times: 9.6 s and 8.9 s on the development machine; 12.1 s and 8.9 s (the slower of two runs each) in the organizer pipeline's Docker sandbox, against its limit of 20 s per experiment.

## 7. Memory

Table: 29,298 entries * 25 bytes = 732,450 bytes (the table region is empty until the search starts). An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: 8,495 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 305,820 bytes (loop body 3919, recovery copy 3976, handlers, key scan, cut, slice and setup 600).
Counters and copies: 6,144 bytes (trail numbers, birth batches, counters and the lane arrays used by the handlers, about 2,048 bytes, and a reserve of 4,096 bytes for the stack, alignment and anything not itemised). The 128 registers, counted as memory: 4,096 bytes. No advice. Memory peak = max(setup phase 379,380, search phase 1,048,510) = 1,048,510 bytes <= 2^20 = 1,048,576; the preprocessing is inside the setup phase. This is the search phase; the setup phase, in which the circuit generator runs, is smaller (379,380 bytes, Section 3.6). Claim `memory_log2_bytes` = 20. `python3 shrho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 64 - 305,820 - 4,096 - 6,144) / 25) = 29,298 (64 bytes are left unused as a margin), and Tp = 437 is the largest integer for which the success bound of Section 4 reaches the plan target 0.390000001 (proved >= 0.39, Appendix A) at the largest mean number of trails whose table-capacity tail stays below 2^-40 (Appendix A computes both).

## 8. Heuristics, conventions and what is credited

The premises of this entry are: H1 (the model premise of Sections 4 and 5, clauses (a) to (d), score-critical) and H3 (the machine convention: 128 registers, immediates, lanes of 36 bits in a word, 36-byte instruction charge; supporting: it is a declared convention priced in Section 3.5, not a statistical premise, and the success argument does not depend on it). There is no advice and no polarity climb; the entry has no two-block mode. The constant message prefix P (20 zero bytes) is part of the program, not advice.
Credited to our own earlier entries on this lane, all declared as dependencies (same challenge): 5790b7ac-f746-4954-8dd2-0ad1dd3ae8d5 (round 64: the program at 64 steps, Lemma 2 of Section 4 and the register accounting), 0bcb5aeb-b5ee-4cc4-a774-98cfb0d294d4 (round 40: the packed-lane program at another round count), 368d1718-a059-4780-9f08-8f0931a46f0d (the message layout, the 52-byte message with the chain value in W5..W12) and 01e31be9-0524-4b77-a40e-c1f862d506a8 (the packed-lane search, kernel generator, ledger and experiments); through them to our blake3 round-3 entries 0a9640ed, 3356413f, cf8b0e92 (the packed-lane chain), 62cfd777 (declared register file and generator accounting) and to Jbenisek's e479cbbf: the relation, the trail-and-table search, the handlers, the recovery, the ledger method and the experiments' form.
The supermartingale proof of Section 4 follows the proof we wrote for our blake3 round-4 line after the judges' finding on 41b32afc (not a dependency: that entry is on another challenge), and it is the Lemma 2 of our round-64 entry 5790b7ac. The target, the round constants of steps 39 to 59 in the kernel and every number here are new.

## 9. Response to 5790b7ac findings

Response to 5790b7ac findings. This entry carries the answers to the rulings on our round-64 entry 5790b7ac-f746-4954-8dd2-0ad1dd3ae8d5 (sha256 round 64, status not_evaluable, reason `lane_experiments/heuristic/H2-cut-count`) and on our round-40 entry 0bcb5aeb-b5ee-4cc4-a774-98cfb0d294d4 (not_evaluable, reasons `lane_cryptanalysis/heuristic/H2-cut-count` and `lane_cost/heuristic/H2-cut-count`), the first two of its dependencies; its program is the program of 5790b7ac at round 60 with the changes of Section 4 only. Every finding id of the 5790b7ac ruling (eleven findings and the heuristic assessment) and of the 0bcb5aeb ruling is named in the bullets below, with the same answer where the finding has the same content.

- Quadrature findings (material, invalid_inference): `lane_cryptanalysis/F1-uncertified-midpoint-chernoff-bound`, `lane_cost/F-success-numerical-margin` (and, from the 5790b7ac ruling of the same text, `lane_cryptanalysis/F1-uncertified-mgf-quadrature`, `lane_cost/F1-uncertified-tail-quadrature`, `lane_evaluability/F2-uncertified-numerical-tail-bound`). Confirmed and fixed; the judges are right on substance, not only on form: the 1,500-point midpoint sum was below the true Chernoff quantile (the effect on the success bound is of the order of 1e-5). The integrand exp(s zeta(u) - u) is convex, so on every panel it lies below its chord and the trapezoid sum is an upper bound of the integral (Section 4, Step 5.3); the geometric block length is dominated by L E + 1 (E exponential), the shift and the atom at the cap are bounded explicitly, the program multiplies the trapezoid sum (20,000 panels) by 1 + 2^-30, and Appendix A (`certify`) recomputes z* and the whole bound in exact rationals and 60-digit decimals with outward rounding: `P_lower certified` = 0.390000003188 >= 0.39, asserted by the program.
- Cut-count findings: `lane_cost/F-H2-poisson-law`, `lane_cryptanalysis/F2-unsubstantiated-exact-cut-law` (and `lane_cryptanalysis/F3-cut-count-law-unestablished`, `lane_cost/F4-cut-poisson-support`, `lane_experiments/heuristic/H2-cut-count` of the 5790b7ac ruling). Confirmed; the premise H2 (a Poisson law for the number K of cut trails) is withdrawn, there is no premise about K left to test and no heuristic H2 in claim.json. Section 4, Step 6 proves the cut term for this entry as a theorem about F: K = K_A + K_B; K_A (cut trails whose first c evaluations are fresh) is at most the number of successes of an i.i.d. Bernoulli(p) trial sequence, p = (1 - 1/L)^c, before failure number k + 8, so P(K_A >= 2, N1 <= k - 1) <= P(Binomial(k + 8, p) >= 2); K_B (cut trails that join another path) needs one of five root events (S, X, J2a, J2b, Y), each bounded by an expected count from the collision hazard. The cut term is 7.22e-05; it is in the program (`_lossq`, `cut_halt`) and in Appendix A.
- `lane_cost/F-H1-scale-extrapolation`, `lane_experiments/F-EXP-1` and `lane_experiments/F-EXP-2` (F-EXP-2 also names H2: withdrawn, see above) (and `lane_cryptanalysis/F2-full-scale-random-function-extrapolation`, `lane_cost/F2-full-scale-random-model-extrapolation`, `lane_evaluability/F1-full-scale-H1-evidence-gap` of the 5790b7ac ruling): not a Lemma 2 matter. H1 (the comparison of the fixed target with a random function, clauses (a) to (d)) stays a declared, score-critical premise and the entry still makes no inference from the organizer frequencies; Lemma 2 is now a theorem about F whose only premise is H1 (Sections 4 and 5). No change claimed; the scale gap is stated in Section 5 (not tested: the 256-bit functional graph, 2^128 evaluations).
- `lane_cost/F-memory-realization-gap`, `lane_experiments/F-EXP-3` (and `lane_cost/F3-exact-machine-ledger-not-implemented` of the 5790b7ac ruling): ledger and machine convention (H3), unchanged and addressed in Section 3 (the ledger, the register file, the generator in the 1 MiB VM). The program grows by 120 bytes (the rigorous quadrature), and the instruction and memory account is the program's own `--ledger` output (Appendix A).
- On the judge ruling on our round-61 entry e8242c6e (its loop counter needed a persistent register with all 64 in use; this round-60 line, at 63 registers, uses the same 128-word file): the loop counter and the loop limit now sit in dedicated registers of the declared 128-word register file, and no counter load or store occurs.

Two corrections that no judge named, found while proving the lemma, are part of this version and are charged: (L3) of the earlier text (the free lengths of the trails are independent geometric variables by optional skipping) was not exact when a trail merges and finishes early, so the trail sums are now bounded by the lottery blocks of each lane, i.i.d. without selection (Step 5.2); and the cut trail is charged explicitly (as y and as t, Step 5.1 (c)) instead of being counted among the typical trails. Effect: under the corrected lemma the plans of our earlier entries on this lane fall below 0.39 at their filed B (round 64: 0.389749 at Tp 423, round 40: 0.389806 at Tp 510), so B rises; this entry's plan has Tp 437, k = 28631, and time_log2 124.97758.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate, and `certify` recomputes the bound of Lemma 2 in exact rationals and 60-digit decimals with outward rounding: the line `P_lower certified` is a proved lower bound on P_F, asserted >= 0.39. The same numbers come from `python3 shrho.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, expm1, log1p

PH, FILT, LOOP, LANES = 3912, 4, 3, 7           # operations of the packed step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 5605                                # generator calls (python3 shrho.py --ledger)
EXTRA = 64                                      # extra operations per recovery batch beyond the kernel
N_BITS, S1, W, KAPPA = 256, 32, 90, 18          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 400, 800, 800, 120, 400
SETUP_FIXED, CMAX = 7 * 400 + 2000, 1
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 36, 600, 128 * 32, 6144, 25, 0, 64
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
EPS, HZ, GRAIN = 1e-3, (LANES + 1) / 2, 10 ** 18  # Lemma 2 tail budgets, weight of a squared trail length, B is a multiple of GRAIN
body = PH + FILT + LOOP                                        # one batch = one loop body
code_bytes = (body + (PH + EXTRA) + OTHER_CODE) * INSTR        # main body + recovery copy of the kernel + handlers
tmax = ((1 << 20) - SPARE - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY    # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


def zq(q, uc, uh, n):         # (z*, lam): P(sum of n i.i.d. block terms z(min(beta, c + S)) / L^2 > z*) <= EPS (Chernoff), beta geometric of mean L
    k = 20000                 # UPPER bound on the MGF: beta <= L E + 1, E ~ Exp(1); exp(lam z(u) - u) is convex, so the trapezoid rule (chords) bounds
    h = uc / k                # its integral from above; 1 + 2^-30 covers float rounding and the 1/L shifts; certify() below redoes it in decimals
    us = [i * h for i in range(k + 1)]
    zs = [HZ * u * u + 2 * q * max(0.0, u - uh) for u in us]

    def f(lam):
        a = [lam * z - u for z, u in zip(zs, us)]
        m = max(a)
        e = [exp(x - m) for x in a]
        return (n * (m + log(((sum(e) - (e[0] + e[-1]) / 2) * h + e[-1]) * (1 + 2.0 ** -30))) - log(EPS)) / lam
    lo, hi = -16.0, -4.0
    for _ in range(50):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        lo, hi = (lo, m2) if f(exp(m1)) < f(exp(m2)) else (m1, hi)
    return f(exp((lo + hi) / 2)), exp((lo + hi) / 2)


def plower(Tp, q):            # the lower bound of Lemma 2 (v2) on the success probability, q = Q / L
    L = Fraction(1 << D, Tp)
    c = -(-KAPPA * L.numerator // L.denominator)
    uc, uh = float((c + SB) / L), float((c // 2) / L)
    k = int(q) + 1
    while tail_log2(q, k) > log(EPS, 2) - 1e-6:                 # lottery count N1 ~ Binomial(Q, 1/L) <= k - 1 except with probability EPS
        k += 1
    z = zq(q, uc, uh, k - 1 + LANES)[0]                         # at most k - 1 + LANES lottery blocks
    l2n = float(L * L / Nn)
    kap = (2 * q * uc + HZ * uc * uc + 2 * q * (uc - uh)) * l2n
    if kap >= 0.3:
        return -1.0
    w = 1.0
    for _ in range(100):
        w = exp(w * kap)
    w *= 1 + 2.0 ** -40                                          # ln w >= w kap
    s0 = q * q / 2
    th = l2n * (w * (s0 - z - CMAX * (q * uc + min(q * (uc - uh), z / (LANES + 1) + q * float(SB / L)))) - (w - 1) * s0)   # cut trail (Step 5 (c))
    p, hq, ql, n2 = exp(-KAPPA), s0 * l2n, q * l2n, k + LANES + 1
    cuts = -expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p))   # P(Bin(n2, p) >= 2): fresh cut trails (Step 5b (i))
    cuts += ql * (1 + (2 + KAPPA) * exp(-KAPPA / 2) + 2 * hq) + hq * p * (3 + 2 * KAPPA)   # colliding cut trails: S, X, J2a, J2b, Y (Step 5b (ii))
    keyfm = tmax * (tmax - 1) / 2 * 2.0 ** -(min(64 - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp))
    return 1 - exp(-th) - 2 * EPS - cuts - uc * q * l2n - keyfm - 2.0 ** tail_log2(q, tmax - 59) - n2 * p * float(SB / L) - 2.0 ** -90


def plan_tp(Tp):              # the least B (a multiple of GRAIN) with plower >= 0.39
    L = Fraction(1 << D, Tp)
    lo, hi = 1.0, tmax + 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if plower(Tp, mid) >= P_MIN else (mid, hi)
    b = -(-int(hi * L / LANES) // GRAIN) * GRAIN
    while plower(Tp, float(b * LANES / L)) < P_MIN:
        b += GRAIN
    return L, b, -(-KAPPA * L.numerator // L.denominator)

def certify(Tp, B, K=20000):  # Lemma 2 v2 in exact rationals and 60-digit decimals (every exp and ln correctly rounded), results moved outward by 1e-40
    from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
    getcontext().prec = 60
    up = lambda x: x * (1 + Dm("1e-40")) + Dm("1e-58")

    def fd(x, u):             # Fraction -> Decimal rounded up (u) or down
        with localcontext() as cx:
            cx.rounding = ROUND_CEILING if u else ROUND_FLOOR
            return Dm(x.numerator) / Dm(x.denominator)
    ex = lambda x: up(fd(x, True).exp())                         # upper bound on exp(x), x rational
    L = Fraction(1 << D, Tp)
    th_D, Q, Np = 1 / L, LANES * B, Fraction(Nn) * (1 - 1 / L)
    q = Q / L
    c = -(-KAPPA * L.numerator // L.denominator)
    h, M, HF = c // 2, c + SB, Fraction(LANES + 1, 2)
    qu, qd, lnE = fd(q, True), fd(q, False), Dm("0.001").ln()
    k = int(q) + 1                                               # P(N1 >= k) <= e^-q (e q / k)^k <= EPS
    while up(-qd + k * (1 + (qu / k).ln())) > lnE * (1 + Dm("1e-40")):
        k += 1
    n = k - 1 + LANES
    lam = Dm(repr(zq(float(q), float(M / L), float(h / L), n)[1]))
    ucu, ucd, uhd, dl = fd(M / L + th_D / 2, True), fd(M / L + th_D / 2, False), fd(h / L, False), fd(3 * th_D / 2, True)
    with localcontext() as cx:
        cx.prec, cx.rounding = 40, ROUND_CEILING
        hh = ucu / K
    with localcontext() as cx:
        cx.prec = 100
        ys = [i * hh for i in range(K + 1)]                      # exact nodes, K hh >= uc + 1 / (2 L)
    zeta = lambda y: Dm(HF.numerator) / Dm(HF.denominator) * y * y + 2 * qu * max(Dm(0), y - uhd)
    ph = [(lam * zeta(y) - y).exp() for y in ys]
    mgf = up(dl.exp() * (hh * (sum(ph) - (ph[0] + ph[-1]) / 2) + (lam * zeta(ucu) - ucd + dl).exp()))
    zstar = Fraction(up((n * up(mgf.ln()) - lnE) / lam))       # P(trail sums > zstar L^2) <= EPS
    kap = fd((2 * M * Q + HF * M * (M + 1) + 2 * Q * (M - h)) / Np, True)
    w = Dm(1)
    for _ in range(200):
        w = (w * kap).exp()
    w *= 1 + Dm("1e-30")
    assert w.ln() >= w * kap                                    # ln w >= w kap0 / N'
    w = Fraction(w)
    Hs = Fraction(Q * (Q - 1), 2) + (1 << 16) * Q
    theta = (w * (Fraction(LANES * LANES * B * (B - 1), 2) - 2 * k * Q - CMAX * (M * Q + min(Q * (M - h), zstar * L * L / (LANES + 1) + SB * Q)) - zstar * L * L) - (w - 1) * Hs) / Np
    p = ex(-c * th_D)                                            # (1 - 1/L)^c <= e^(-c / L)
    p2 = ex(-(c - 1) * th_D) * fd(1 + (c - 1) * th_D / (1 - th_D), True)
    n2, H, PP = k + LANES + 1, Hs / Np, Fraction(Q * (Q - 1), 2) / Np
    kt = tmax - 59
    terms = [ex(-theta), Dm("0.002"),                            # main; finished-trail count and trail sums (EPS each)
             up(1 - (1 - p) ** n2 - n2 * p * (1 - p) ** (n2 - 1)),   # fresh cut trails: P(Bin(n2, p) >= 2)
             fd(Q * L / Np, True),                               # S: a trail closes a cycle
             fd(Q / Np, True) * fd(L, True) * ex(-(c - 2) * th_D / 2) * fd(2 + (c - 1) * th_D, True) + fd(PP, True) * p2,   # X
             fd(Q * L * H / Np + (Q + (1 << 16)) * L * PP / Np, True),   # J2a
             fd(PP * (1 - th_D), True) * p2, ex(-(c - 1) * th_D) * fd(H, True),   # J2b, Y
             fd(M * (Q + (1 << 16)) / Np, True),                 # Step 3
             fd(Fraction(tmax * (tmax - 1), 2 * Tp) / (1 << min(64 - (Tp - 1).bit_length(), N_BITS - D)), True),   # key false match
             up((-qd + kt * (1 + (qu / kt).ln())).exp()),           # table capacity
             n2 * p * fd(SB * th_D, True),                       # long finish
             fd(Fraction(Q << 16, Nn) + Fraction(Q * k, Nn) + k * k * L / Nn, True) + up((-300 + (Dm(5).exp() - 1) * fd(H, True)).exp()) + Dm(2) ** -99]
    assert Fraction(Q, 1 << 32) * Fraction(108, 1000) > 1000 and 240 * M <= Q   # stage-1 budget (Step 6): below e^-1000, inside the last term
    return 1 - sum(terms)


lo, hi = 1.0, tmax + 1.0                                       # the largest mean number of trails the table holds (tail within 2^-40)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
a, b_ = 1, 8192                                                # the largest Tp that reaches 0.39 at that mean (the bound falls as Tp grows at a fixed mean)
while b_ - a > 1:
    m_ = (a + b_) // 2
    a, b_ = (m_, b_) if plower(m_, lo) >= P_MIN else (a, m_)
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
pc = certify(Tp, B)
print("P_lower certified (exact rationals, 60-digit decimals) = %s" % str(pc)[:14])
assert pc >= Fraction(39, 100)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 4576
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
Tp = 437  tmax = 29298  B = 48677996211575832668000000000000000000  e2max = 158672208656105598749592900340  c = 219003239580123439013899561419187208
memory bytes = 1048510
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000003188
main loop: B * 3919                                  190769067153165688225892000000000000000000
slice checks: ceil(B / 2^48) * 120                   20752677959695730863245480
stage-1 hits: e2max * 400                            63468883462442239499837160136000
finished trails: tmax * (800 + 3 * tmax)             2598556812
cut trails: 1 * 800                                  800
recovery: (c + 2^48) * (3912 + 64) + 600             870756880570570793520383800710089907864
setup and generator                                  3811600
N = 191639824097205163234532582996280715658556
certificate: 2^12497757 * 4576^100000 <= N^100000 < 2^12497758 * 4576^100000
log2(N/C) = 124.9775779480
time_log2 = 124.97758
```
