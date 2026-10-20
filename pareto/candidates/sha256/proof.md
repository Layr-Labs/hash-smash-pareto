# sha256-r47: birthday search with 256 bit-sliced lanes, one unrolled program of 5-byte records, a 64-byte message (two blocks after padding)

Credited derivative of our filed round-43 entry 87cb17fa and of the entries named here, all declared as dependencies (same challenge): 87cb17fa-d025-4066-bd13-91d9936ce327 (124.28559, our filed round-43 entry), 4684dfc2-cdac-4441-af91-c9979e2888a9 (124.26094, mitchuski's round-64 entry), 1884db5b-acc6-42e7-ac3c-5877e77b8277 (124.22926, mitchuski's round-57 entry), 3642e1cd-e391-41a7-81e0-456c02e4becd (124.31538, lamb356's round-64 entry), 6b678689-e6a2-42b0-87d8-fff55432f2f6 (124.41766, dariolina's round-64 entry), 744875ec-f063-4208-8075-b61192ac4d69 (124.83147, dariolina's round-39 entry), 44870635-2031-4c6a-aa62-c44672c7f338 (118.346, lamb356's round-39 entry) and 38912d66-c0d0-4238-9058-1e8a2775f695 (120.46, sraiw's round-39 entry). From 87cb17fa this entry keeps the search with distinguished points, the trail table, the handlers, the ledger method, the success bound (Lemma 2 of Section 4: bounded restart with the detection delay integrated, as in our blake3 entries; no premise besides H1), the unrolled kernel of 5-byte body records (the price of dariolina's 6b678689, Section 3.1), its allocator and C generator, and the rolled two-lane recovery program. Five things are new (at round 43 they are the whole difference in cost against 87cb17fa):
(1) The message is 64 bytes, so FIPS padding adds a second block: the padded message is 128 bytes, two blocks. Block 1 holds 8 constant words and the 8 words of the chain value; block 2 is padding only. Two-block messages on this lane are in the accepted precedent of lamb356's 44870635 and of sraiw's 38912d66.
(2) The 8 constant words are chosen so that the first 8 steps set a_1 = K9 - K8, a_2 = -K9 and a_3 = ... = a_8 = 0 (the zeroing prefix of dariolina's 744875ec, extended to 8 words). Steps 0 to 7 are constants, and the round constants K8 and K9 cancel in steps 8 and 9.
(3) The chain words enter as W8 = y0, W9 = y1 and W(8+k) = y_k - K(8+k) for k = 2..7, so K + W = y enters steps 10..15 with no adder.
(4) The walk is on walk B of mitchuski's 4684dfc2 and 1884db5b: an explicit bijection of the final working state that stops the last six steps early, with the output words in an order that needs no register move, and a carry-in of one replaces part of each folded constant (lamb356's 3642e1cd). We re-implemented both from the notes; no file of a rival entry was used or run.
(5) A sum of three or more variable words takes its first three in one ripple of pair-carry columns, 9 gates per bit where two ripples of full adders cost 10 (Section 3.2): the column templates of mitchuski's blake3 entry 1b7bd746 on the pair encoding of Demenkov, Kojevnikov, Kulikov and Yaroslavtsev (2010); 1b7bd746 is on another challenge, so it is credited here and not as a dependency. Re-implemented from its note; no file of it used or run.
The kernel evaluates one block-1 compression of 47 steps for 256 independent trails at once in bit-sliced form (one 256-bit word holds bit j of all 256 states; rotations are renaming). One batch of 256 trails is 56,657 program records (221.32 per trail, 0.0635 of the 3484 operations of one reference compression). The price is a declared register file of 1,024 words of 256 bits (32,768 bytes, counted as memory), 56,657 body records at 5 bytes (283,285 bytes), 1,684 other instructions at 36 bytes, an array of 3,008 bytes and a table of 29,659 entries. No advice; no differential or structural property of the 47 steps is used.

## 1. Target and relation

Target `sha256-r47-prefix-v1` (the Pareto lane `sha256`, round 47). The two colliding messages have 64 bytes each. With x a 256-bit integer and y0..y7 its eight 32-bit words (big-endian, y0 the highest), M(x) is the 16 big-endian words W0..W15 with
- W0..W7 = the constant words 3e73281c, 752d8ed2, ad19eff1, 7250fceb, d4095422, 44fdb519, 43f22c5b, d8d6aac4 (Section 3.2 gives how they are computed),
- W8 = y0, W9 = y1, and W(8+k) = y_k - K(8+k) modulo 2^32 for k = 2..7.
FIPS 180-4 padding appends 0x80, 55 zero bytes and the 64-bit length 512: the padded message is 128 bytes, two blocks, and block 2 is the same for every x. The target runs the steps 0 to 46 on each block, block 1 from the standard IV and block 2 from the chaining value cv1 = IV + s(x) word by word, where s(x) is the working state after step 46 of block 1; the digest is the result of block 2 with its feed-forward (`verifier/hash_functions.py:digest(M(x), "sha256", 47)`). The profile's message domain is "finite byte strings of bit length below 2^64"; a 64-byte string is in it.
Write a_i, e_i for the a and e words after i steps of block 1 (a_0, e_0 from the IV), T1_i for the T1 of the step that produces them and W_j for the schedule word of step j. f(x) is walk B (4684dfc2): the eight words e_(47-3), e_(47-2), X = e_(47-5) + Ch(e_(47-2), e_(47-3), e_(47-4)) + W_45, T1_(47-4), Q = T1_(47-5) + Maj(a_(47-6), a_(47-7), a_(47-8)), a_(47-6), a_(47-7), Y = e_(47-4) + W_46, in this order (the order with no register move, Section 3.2), as a 256-bit integer. These words determine s(x): the program's `enc_invert` recovers a_(47-5) = Q + Sigma0(a_(47-6)), then a_(47-4), a_(47-3), a_(47-2), the T1 of steps 45 and 46 and the whole state, by additions, subtractions and the round functions. The walk is g(x) = f(x) XOR q, q a fixed 256-bit mask (130 output planes that the generator leaves complemented instead of spending a NOT).
So g(x) = g(y) gives s(x) = s(y), hence the same cv1, the same block 2 and equal digests. x != y gives M(x) != M(y), since x -> W8..W15 is a bijection. The attack outputs two distinct 64-byte messages with equal complete 256-bit digests.
Checked outside the shipped experiments (`ext_regress.py`, not shipped): the program output, inverted and completed with block 2, equals the organizer reference `digest(M(x), "sha256", 47)` on 2,560 random messages; the scalar state plus block 2 on 300 more; the inverse on 300 states; the recovery program on 100; 256 lanes chained for 4 steps against the scalar g: 0 differences in every check (the reference at 64 steps equals hashlib.sha256 on 50 messages of 64 bytes). The selftest (`python3 bssha.py --selftest`) compares the program with the scalar g on 2,560 lanes (including all-zero and all-one inputs), 4 chained steps, the inverse on 10,000 states, the recovery program, the experiments' digest network and a width-18 search.

## 2. The attack (program `experiments/bssha.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 32 bits are zero (chain word y7; the 32 low planes) and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 441. The density is theta = 441 / 2^122 and L = 1 / theta = 2^113.2154. The key of a DP is the 31 bits of x above bit 121 followed by the 9 low bits of F (F < 441 < 2^9); 40 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated program of Section 3.2. The start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 32 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (22-byte entry, Section 7) and start trail t' = next index in that lane.
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 13 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 29,659 keys, when a third trail would be cut, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps of g, then step both together; at the first step with g(a) = g(b) and a != b output (a, b). The recovery program (2,113 records executed per call, 440 records: g of two chain values in the two lanes of 256-bit words, rolled, 36-byte instructions, Section 3.3) is used. At most capr = c + S batches are run (the program halts if l1 > capr).
Constants (all computed by `plan(256)` of the program, printed by `python3 bssha.py --ledger`): Tp = 441, L = 5316911983139663491615228241121378304 / 441, B = 1335287087142000000000000000000000000, Q = 256 B = 1.00456 * 2^128 evaluations, e2max = 159178625004529953002929687564, c = 156734366849922053040811716858453329 (= 2^116.916), table capacity tmax = 29,659 entries of 22 bytes. The trail numbers stay below 2^16 and every length is below c + S < 2^119, so the entry fields never overflow (the program asserts both when it stores an entry).
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is a constant of the program).

## 3. Operation ledger

### 3.1 Machine
Machine model of this entry (declared cost-model prices). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices operations and memory; it gives no register count and no instruction size.
This entry declares a load/store machine with 256-bit words and 1,024 registers (the 1021 data registers that the shipped allocator uses and three pointer registers; a declared register file was accepted for our blake3 entry 0a9640ed with 1,024 registers). Charged, one operation each: every XOR, AND, OR and NOT of a 256-bit register, every register move, every set of a register to a constant, every load and store, every pointer addition, comparison and conditional branch, and the one random word. Nothing is free except the renaming of a bit-sliced rotation, and nothing is executed that is not a record of the program. The operation ledger is the exact count of the records of the submitted program, listed by `python3 bssha.py --text` and counted by `--ledger` (Appendix A); the organizer can regenerate it.
THE 5-BYTE BODY PRICE (a cost-model price, score-critical, the convention of dariolina's 6b678689, kept from our 87cb17fa). A main-loop body instruction is a register-to-register XOR, AND, OR, NOT or move of 256-bit registers with no immediate operand, encoded in 5 bytes: an opcode byte and three 10-bit register fields. The 56,657 records of the kernel are all of this kind (44,592 XOR, 7,383 AND, 4,682 OR, 0 NOT, 0 moves, 0 sets), so the kernel is 283,285 bytes of code. Every other instruction (stage 1, the batch loop, the handlers, the recovery program, setup and the generator's code image) is charged 36 bytes. At 36 bytes per body record the kernel alone would be 1.9 times the limit of 2^20 bytes.

### 3.2 One batch = 56,694 operations for 256 trails
Representation: a 32-bit word is 32 planes; plane j holds bit j of the word of every lane. A rotation is a renaming of planes. The sum of two words is a ripple of full adders over the planes. The full adder is the pivot adder of 6ae36351 (our re-implementation, `Gen.fa`): each signal is a (node, polarity) pair, so complements are free; with three variable inputs, two share a polarity and the third is the pivot p: sum = u XOR y, carry = (u AND (y XOR p)) XOR p with u = x XOR p, 5 gates. With constant inputs the gates fold at build time.
Constants fold at build time: in a sum of several words (`Gen.addm`) the constant words are added first at no cost, then one ripple adder per variable word; carry-ins of one into those adders take up to (number of adders) off the constant at no gate, chosen so that the remaining constant has the most trailing zeros (lamb356's 3642e1cd carry-in absorption), and the remaining constant, if not zero, is one more adder. A gate whose two operands are the same two input planes as an earlier gate is not built twice (a node table; in this program the first XORs of sigma0(W8) are those of Sigma0(a_9), since a_9 = y0).
Pair-carry path (`Gen.add3`): a sum with three or more variable words may instead take its first three in one ripple whose carry between columns is a pair of planes (u, U) standing for U ? 1 : 2u. Bit 0 is a full adder, its carry passed on as the pair (0, k). A column of bits 1 to 30 takes the three addend bits x, y, z and the incoming pair and returns the sum bit and the outgoing pair by one of two templates: (T0) n5 = z ^ U, n9 = x ^ n5, s = y ^ n9, n8 = U | (z ^ u), n11 = !(x ^ y) & n9, u' = n5 ^ n11, U' = n8 ^ n11; (T1) w = y ^ U, n8 = z ^ w, s = x ^ n8, n6 = U | (y ^ u), u' = n6 ^ w, U' = n6 ^ (n8 & (x ^ w)). Both satisfy x + y + z + val(u, U) = s + 2 val(u', U') on all 32 input rows. A column is 9 gates (8 at bit 1, where u = 0, and at bit 30, where only U' is built), 10 where every order and template meets an AND or OR of operands of unequal polarity (2 gates); bit 31 is 3 XORs. The generator chooses the addend order and template of each column, and for each sum the pair-carry or the ripple path, by a dry trial that counts the gates each choice adds and keeps the first least; the C generator makes the same choices, and the work of its trials is in its generator calls. The templates are those of mitchuski's blake3 entry 1b7bd746, on the pair encoding of the modified double full adder of Demenkov, Kojevnikov, Kulikov and Yaroslavtsev (2010).
The program is ONE straight network (`_net_u`), with no loop, no load, no store:
- The message words: W0..W7 are constants; W8, W9 are the chain words y0, y1 (registers 256..511 hold the chain value: plane j of x is in register 256 + 32 (7 - j div 32) + j mod 32); W10..W15 are y_k - K(8+k), one adder each with the constant folded in, used only by the schedule. W_i for i >= 16 = W_(i-16) + s0(W_(i-15)) + W_(i-7) + s1(W_(i-2)) is built right before step i (a ring of 16 words).
- The prefix: W0..W7 are chosen step by step from the IV so that a_1 = K9 - K8, a_2 = -K9, a_3 = ... = a_8 = 0 (`_anchor_prefix`: each W_i sets the next a to the anchor). So e_5 = K9 - K8, e_6 = -K9, e_7 = e_8 = 0, steps 0 to 7 are constants (no gate), step 8 has T1 = e_5 + Ch(0, 0, e_6) + K8 + W8 = y0, and step 9 has T1 = Sigma1(y0) + y1: K8 and K9 cancel, and K + W = y enters steps 10..15 directly.
- A full step does T1 = h + Ch + Sigma1 + (K + W) with u = h XOR Ch = (h XOR g) XOR (e AND (f XOR g)) and the carry h XOR (u AND (h XOR c)), so Ch is not built; Maj = ((a XOR b) AND (b XOR c)) XOR b, sharing the previous step's a XOR b; new e = d + T1, new a = T1 + Sigma0 + Maj (one sum, `Gen.addm`). Where the two operands of such an AND have opposite polarity the complemented form is used (one gate either way). The full steps are 0 to 40.
- The last six steps form walk B (Section 1): T1_(47-5), e_(47-5) and Q = T1_(47-5) + Maj; T1_(47-4) and e_(47-4); T1_(47-3), e_(47-3), T1_(47-2), e_(47-2); X = e_(47-5) + Ch + W_45 with no Sigma1 and no K; Y = e_(47-4) + W_46. No T2 and no new a is formed in these steps.
- The allocator (`_alloc`, mirrored by the C generator) is a streaming register allocator: a result takes the register of an operand that dies at the gate, else the lowest free register that is not the target of an output plane. The output planes go to registers 256..511, the input registers of the next batch. The order of the eight output words (permutation (6, 1, 7, 0, 5, 4, 2, 3) of walk B) is the one with no register move: 0 moves, 0 NOTs (a plane of negative polarity is left complemented and recorded in q). The program peaks at 926 live planes and uses 1021 data registers.
Executed per batch (56,657 records, all 5-byte body records): 44,592 XOR + 7,383 AND + 4,682 OR = 56,657 gates; 0 NOT; 0 set; 0 moves; no load, no store, no control record. Per trail 221.316 operations = 0.0635 unit.
Validation: the selftest and the organizer-reference checks of Section 1; the C generator of Section 3.6 emits the identical records.
The generator runs once at the start; its work is charged in the setup row (3.3), its code and peak storage in Sections 3.6 and 7.

### 3.3 Loop, stage 1, handlers and the other events
One batch: 56,657 body records + stage-1 test 34 + loop control 3 = 56,694 operations. Stage 1: the 32 low planes are combined into the mask of zero lanes: 31 ORs, a compare with zero and a branch: 34 operations (`stage1_ops`), charged as 36-byte instructions. A DP has all 32 low bits zero, so its lane is flagged.
Loop control of the batch loop: counter increment, compare with the next slice limit, branch back: 3 operations.
Handlers (charged per event at the stated bounds; 36 bytes per instruction):
- Stage-1 hit: store the 256 planes to an 8 KiB copy (256 stores), extract the lane (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (at most 15), counters. Below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail: key formation, three field stores of the 22-byte entry, the new start r + t' (1 add), insertion of the 256 bits of the new start in the lane (12 per plane, 3,072), reload of the 256 planes (256), lane arrays and counters (below 200). Below 3,550; charged **3,800**. The key scan of the table is charged 3 per key. At most tmax finished trails.
- Slice check (every 2^48 batches): charged **1,300** each. Cut trail: charged **4,200**; at most 2 cut trails.
- Recovery program (`RecProg`): a second program of the same machine that evaluates g for two chain values at once, lane 0 in bits 0..31 and lane 1 in bits 128..159 of each 256-bit register (a rotation is a doubled word and right shifts, one AND with the lane mask). It is rolled and uses 36-byte instructions: the message words and K sit in memory (3,008 bytes, Section 7). Per call: the six offset words get y_k - K(8+k) by three records each, the eight input words are stored as W8..W15, the state after step 7 is set by 9 constant records, a schedule loop computes W16..W46, 1 leading step(s) are straight code, a round loop runs 4 steps per iteration up to step 40, and the walk-B tail is straight code. 440 records in all, 112 executed once per recovery (the mask, K and the constant words stored into memory); 2,113 records executed per call (loops included).
- Recovery batch: one call (2,113 records) plus the exact equality test of the two lanes on the 8 output words (26 operations), loop control 3, call and return 2 and 8 moves: charged as 64 per recovery batch (2,177 per batch).
- Setup and generator: 1 random word; the 256 starts inserted (256 x 3,100 = 793,600) and one reload; counters; fixed part charged 813,600. The generator: 1,516,486 primitive calls (both passes) and 56,657 emitted records, each charged 200 word operations: 314,628,600. Setup and generator together 315,442,200 operations = 2^16.47 units, charged in the time bound (3.4).
Code size: 56,657 body records at 5 bytes = 283,285 bytes; stage 1 34 + batch loop 3 + handlers 1,000 + recovery 487 + setup, cut and slice 160 = 1,684 other instructions at 36 bytes = 60,624 bytes; 343,909 bytes in all.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 56,694 | 75,702,766,118,428,548,000,000,000,000,000,000,000,000 (= 7.5703e+40) |
| slice checks: ceil(B / 2^48) * 1,300 | 6.167e+24 |
| stage-1 hits: e2max * 2,800 | 4.4570e+32 |
| finished trails: 29,659 * (3,800 + 3 * 29,659) | 2,751,673,043 |
| cut trails: 2 * 4,200 | 8,400 |
| recovery: (c + 2^48) * (2,113 + 64) + 600 + 112, c + 2^48 = 2^116.916 | 3.4121e+38 |
| setup and generator | 315,442,200 |
N = 76,043,977,280,760,984,489,214,837,786,409,191,535,900 = 7.604398e+40 operations.
N / 3484 = 2.1827e+37 units = 2^124.037429. Claim `time_log2` = 124.03743 (Appendix A, rounded up with 1.1e-06 of slack). The main loop is 99.55 percent of it, recovery 0.45 percent. The walk never computes block 2: equal block-1 states give equal digests (Section 1), so one evaluation of g is one block-1 compression of 47 steps, priced by its records.

### 3.5 Register file and smaller files
Declared prices: the machine has 1,024 registers of 256 bits: the 1021 data registers that the shipped allocator uses (peak 926 live planes) and three pointers. A machine with fewer registers than the peak needs spill loads and stores that the shipped allocator does not produce; no estimate of their cost is claimed. The register file is counted as memory (32,768 bytes, Section 7).

### 3.6 Generator code and peak storage of the setup
The generator that builds the program at the start of the run is part of the machine code. It is written in freestanding C (embedded in `experiments/bssha.py` as `GEN_C`, printed by `python3 bssha.py --gen-c`, 16,723 bytes): the network builder with the pivot adder, the constant folding and the node table for gates of two input planes, the network, the register allocator and the emission of 5-byte records, in two passes (pass 0 counts the uses of every node, pass 1 builds the network again and emits). Compiled to WebAssembly with clang -Oz it is 4,317 wasm instructions, charged 4,317 * 36 bytes = 155,412 bytes. q falls out of the generator.
The generator emits the 56,657 records of `python3 bssha.py --text` (sha256 c6a5f9fb1708de261f5faeb7fa9bd061e6ce87281d7bc78f8d46313dbdd25d78), with 1,516,486 primitive calls and 0 moves. Its scratch is 82,130 bytes (the use counts 56,914 bytes, 24,192 bytes of tables and signal state, a shadow stack of 1,024 bytes), and the record buffer is 283,285 bytes (56,657 x 5). The generator fits in 2^20, see the layout below.
Layout. The setup phase holds the program code at its final size (343,909 bytes), the counters and plane copy (16,384), the generator's code image (155,412) and its scratch (82,130): 597,835 bytes. In the search phase the same region holds the table (652,498 bytes) and the register file (32,768): code + counters + register file + array + table = 1,048,567 bytes. The memory of the entry is the larger of the two, 1,048,567 bytes (9 bytes to spare under 2^20).

### 3.7 Preprocessing
None offline. The generator runs inside every attempt and is charged in the setup row; the claim declares preprocessing_log2 = 16.46628, the setup and generator row (315,442,200 operations = 2^16.466272 units, rounded up: the generator charge of 314,628,600 operations (3.3) and the 813,600 fixed setup operations), which is also inside time_log2. Its code image and scratch are in the setup-phase total of Section 3.6 (597,835 bytes).
## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bssha.py --loss` (the function `_lossq`); Appendix A recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
pass 1 of step 6 recomputes the two lengths and pass 2 aligns and walks them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F (F < 441 <= 2^9 and the key holds its 9 low bits), so equal keys of two DPs differ only if their bits above 152 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds g^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A 40-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B = 1.00456 * 2^128 evaluations numbered t = 1, ..., Q batch by batch and lane by lane inside a batch, b(t) = ceil(t / 256) the batch of t; N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(13 L) = 156734366849922053040811716858453329, S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 28352.65, tmax = 29,659, CMAX = 2 (the program halts when a third trail would be cut). Pi_m = (1 - 0/N')(1 - 1/N') ... (1 - (m-1)/N') is the probability that m independent uniform values of a set of N' elements are distinct. PP = Q (Q - 1) / (2 N') = 0.50457, H = (Q (Q - 1) / 2 + 2^16 Q) / N' = 0.50457. Let k = 29616 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 258, p = e^(-c/L) >= (1 - theta)^c, p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)), and tmax = 29,659. Let F be a uniformly random function on 256-bit values and P_F the success probability of the attempt when every evaluation of g is replaced by F (lazy sampling). Then, with no premise,
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = Pi_Q / (1 - k Q / N') = 0.603765898   (the first collision exists),
    P_delay = (1 - k Q / N')^-1 * sum over the bins (a, b] of [0, Q] of (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = 0.005516   (the merged path needs a DP in the batches that are left; 22,000 bins, Step 5),
    P_own = Q L / N' = 3.559e-05   (the first collision is a cycle of its own trail),
    P_long = M Q p (q + 256) / ((1 - p) N') = 2.992e-05   (its partner is on a trail with c evaluations without a DP),
    P_age = PP p2 = 1.597e-05   (the merged trail is too old when it reaches the DP),
    P_dist = PP L (Q + 2^16) / N' = 1.796e-05   (a later collision on the rest of the merged path),
    P_cut = P(Binomial(n2, p) >= 3) + E_S + E_X + E_J2a + E_J2b + E_Y (Step 6) = 1.542e-04, with E_S = Q L / N', E_X = (Q / N') L e^(-(c-2)/(2L)) (2 + (c - 1)/L) + PP p2, E_J2a = Q L H / N' + (Q + 2^16) L PP / N', E_J2b = PP (1 - theta) p2, E_Y = e^(-(c-1)/L) H,
    P_key = C(tmax, 2) / (2^kb Tp) = 4.6e-04, kb = 31,
    P_table = e^-q (e q / (tmax - 59))^(tmax - 59) = 1.8e-12,
    P_tiny = Q 2^16 / N + k^2 L / N' + 255 Q / N' + exp(-300 + (e^5 - 1) H) + 2^-90 (Step 7; it needs 240 M <= Q, which holds here).
The numbers are printed by `python3 bssha.py --loss` (the function `_lossq`) and Appendix A recomputes the whole bound in exact rationals and 60-digit decimals (`certify`, outward rounding) and asserts the result >= 0.39: P_F >= 0.390000001000 (the program's float value, planned at the target 0.390000001, is 0.390000001). The program's B is the least multiple of 10^24 for which the float bound reaches 0.390000001 (Appendix A). H1 (Section 5) is the only premise of this entry: it states that the real attempt succeeds at least as often as A_F.

Proof.
Step 0 (notation). A trail is the run of evaluations of one lane between two restarts; a(t) is the number of earlier evaluations of the trail of t (its age); the length of a trail is its number of evaluations. A trail is finished when an evaluation returns a distinguished point (DP; that evaluation is its last), cut when a slice check restarts it at age >= c, open when the halt comes first. Every length is at most M, and a trail of length at most c is never cut. An evaluation is fresh when its input has not been evaluated before. A collision is a fresh evaluation whose value equals an earlier value (an earlier output or a start). The starts r + t' (t' < 2^16) differ from every value the run produces except with probability Q 2^16 / N (r is uniform and independent of F); this event is excluded below and charged in P_tiny, so a non-fresh evaluation exists only after a collision on its trail.

Step 1 (lazy sampling with a lottery). Realise F by independent uniform values V_1, V_2, ...: the t-th evaluation returns V_t if it is fresh and the value stored for its input otherwise. This is the lazy sampling of F for every adaptive choice of the points. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(theta), one per evaluation index, fresh or not; given all of them the V_t are independent and uniform on their class (the theta N DP values, or the N' other values). Index t belongs to lane (t - 1) mod 256, and the lane positions of a lane are its indices in increasing order; the lottery is extended beyond Q by further independent draws (used in the proof only). G_t is the history of the first t evaluations together with the whole lottery; F_t is the history of the first t evaluations together with xi_1, ..., xi_t only.
(L1) If t is fresh and xi_t = 0, then P(V_t = v | G_(t-1)) = 1 / N' for every non-DP value v (and 0 for DP values), and the events for different v are disjoint.
(L2) Whether t is fresh, its input, its batch, its age and the trails before t are determined by G_(t-1).
(L3) The lottery of a lane is i.i.d. Bernoulli(theta); the lanes are independent. Scanning the lanes one after the other, a scan that takes from each lane a number of positions that is a stopping time of that lane (with further independent coins after the run) reads one i.i.d. Bernoulli(theta) sequence.
(L4) N1 = xi_1 + ... + xi_Q is exactly Binomial(Q, theta), so P(N1 >= k) <= e^-q (e q / k)^k <= 2^-40 (Chernoff: the binomial moment generating function is below the Poisson one); P(N1 >= k) is charged once, as 2^-40.
(L5) The run up to evaluation t is F_t-measurable (it depends on V_1, ..., V_t only, and V_s depends on xi_s and an independent uniform). If s is a stopping time of (F_t), the lottery after s is independent of F_s and i.i.d. (strong Markov property of an i.i.d. sequence).

Step 2 (the free run and the first collision). Given the whole lottery xi, the free run is the run in which every evaluation is fresh: the trail boundaries (a DP at every xi = 1, a restart of a trail of age >= c at a slice check), the ages a(t), the lengths and the batches are functions of xi alone, and so are the sets of long trails (a trail is long when its first c coins are all 0, i.e. when it has c evaluations without a DP; the other trails are short, of length at most c, and are never cut) and the numbers rho(y) = the number of evaluations of the lane of y after y up to and including the first with xi = 1. Let n0(t) be the number of s <= t with xi_s = 0. Let tau be the first t with xi_t = 0 whose value V_t equals V_y for some y < t with xi_y = 0 (the first collision of the non-DP class), E1 the event that a start equals a value of the run (Q 2^16 / N), E2 the event that some DP-valued evaluation equals an earlier DP value (on N1 <= k - 1 its probability is at most k^2 L / N': a DP-valued evaluation is uniform on the theta N DP values, at most k - 1 earlier DP values exist, and there are at most k - 1 such evaluations). Outside E1 and E2 the real run is the free run up to tau (every evaluation is fresh), and until then the non-DP values are independent uniform on the N' non-DP values (L1). Hence, for t with xi_t = 0 and y < t with xi_y = 0,
    P(tau = t, V_t = V_y | xi) = Pi_(n0(t) - 1) / N',    sum over y of that = Pi_(n0(t)-1) - Pi_(n0(t)),    P(tau <= Q | xi) = 1 - Pi_(n0(Q)).
On N1 <= k - 1, n0(t) - 1 >= t - k, and Pi_(t-k) <= Pi_(t-1) / (1 - kQ/N') for t <= Q (Pi_(t-1) = Pi_(t-k) times at most k - 1 factors that are each at least 1 - Q/N'; Pi_m = 1 for m <= 1). Pi_m is bounded by exp(-m (m - 1) / (2 N')) from above and by exp(-m (m - 1) / (2 N') - (m - 1) m (2m - 1) / (6 N'^2)) from below (ln (1 - x) >= -x - x^2 for 0 <= x <= 1/2).

Step 3 (a first collision with a good partner is output). Say that the pair (t, y) with tau = t and V_t = V_y is good when (G1) y is not on the trail of t, (G2) b(y) < b(t), (G3) the trail of y is short, (G4) rho(y) <= B - b(t) and a(t) + rho(y) <= c - 1, and that it is undisturbed when no fresh evaluation of the trail of y after t, up to its first DP, is a collision. Claim. On a good undisturbed pair, if the run does not halt early (second cut, table full, stage-1 budget, key false match) and is outside E1 and E2, the program outputs a pair. Proof. Let X and Y be the trails of t and y. The input of X after t is V_t = V_y, the input of Y after y, so the evaluations that X performs after t are the evaluations Y performs after y, the j-th of them in batch b(t) + j for X and in batch b(y) + j for Y (Y does not restart before its DP, because its trail is short, hence never cut, and its first DP is the (rho(y))-th evaluation after y). By (G2) Y evaluates each of them strictly before X, so X only repeats points (they are not fresh). Undisturbed: the evaluations of Y after t are fresh and not collisions (those before t are not collisions, tau being the first), so the lottery of the lane of Y decides the DP: Y ends with a DP at its rho(y)-th evaluation after y, in batch b(y) + rho(y) < b(t) + rho(y) <= B (G4), inside the run, and the key of the DP is stored (the table is not full). X repeats it in batch b(t) + rho(y) <= B with the same DP and the same key; X has then done a(t) + rho(y) + 1 <= c evaluations, so no slice check cut it (a slice check cuts a trail of age >= c, and the age before its last evaluation is a(t) + rho(y) <= c - 1). The two trails are different (G1), finished, with the same key, and the inputs of t and of y are different (t is fresh) with g(t) = g(y): Lemma 1 applies. QED.

Step 4 (the pairs that are not good, and the disturbance). Let W(t, y) be the event (tau = t, V_t = V_y) with xi_t = xi_y = 0 and work on N1 <= k - 1 outside E1 and E2. By Step 2, P(W(t, y) | xi) <= Pi_(t-1) / ((1 - kQ/N') N') <= 1 / ((1 - kQ/N') N'), and sum over t of P(W(t, y) | xi) is at most the sum over t of 1 / N', so at most Q / N'. A pair that is not good fails one of the following; each failure is bounded by the expected number of pairs of that kind times the hazard.
(a) (G1) fails: y is among the a(t) earlier evaluations of the trail of t; a(t) is at most g(t), the number of consecutive 0 coins just before t on its lane (g(t) as in Step 6 (ii)), E g(t) <= sum over i >= 1 of (1 - theta)^i <= L - 1, so the failure has probability at most Q L / N' = P_own.
(b) (G2) fails: y is in the batch of t before t, at most 255 pairs per t: 255 Q / N' (charged in P_tiny).
(c) (G3) fails: y is on a long trail. A long trail has at most M evaluations (it is cut at the first slice check at age >= c, or finishes before), a y has at most Q partners t, and the number of long trails is at most the number of successes of the scan of Step 6 (i) (disjoint windows of c coins 0), with expectation at most p (q + 256) / (1 - p) there: M Q p (q + 256) / ((1 - p) N') = P_long.
(d) (G4) fails. rho(y) > B - b(t) means that the B - b(t) coins after y on its lane are all 0 (they lie in the batches b(y) + 1, ..., b(y) + B - b(t) <= B, inside the run), probability (1 - theta)^(B - b(t)) <= e^(-theta (B - b(t))) for each y. By Step 2 the pairs (t, y) with y < t contribute at most sum over t of (t - 1) Pi_(t-1) / ((1 - kQ/N') N') e^(-theta (B - b(t))), and (t - 1) Pi_(t-1) / N' = Pi_(t-1) - Pi_t, so, with b(t) <= ceil(b / 256) for t <= b and the sum of Pi_(t-1) - Pi_t over t in (a, b] equal to Pi_a - Pi_b, at most (1 - kQ/N')^-1 sum over the bins (a, b] (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = P_delay (the bins and the enclosures of Pi are in Appendix A). The second part, a(t) + rho(y) >= c: a(t) <= g(t) and rho(y) >= 1, so it requires g(t) + (rho(y) - 1) >= c - 1. If t and y are on different lanes the two coin sets are disjoint and g(t), rho(y) - 1 are dominated by independent geometric variables with values in 0, 1, 2, ...; the sum of two such variables is at least c - 1 only if a single i.i.d. sequence of coins has at most one 1 among its first c coins, hence among its first c - 1 coins: probability at most (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. If they are on the same lane and (G1) and (G3) hold, y is on an earlier trail of the lane that is short, so it ended with a 1 before the start of the trail of t, and the two coin sets (those of rho(y) up to that 1, those of g(t) after it) are disjoint: the same bound. At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': PP p2 = P_age.
(e) Disturbance. For a good pair let r' be the number of evaluations of the lane of y with index > t up to and including the first with xi = 1; the coins there are independent of F_t (L5, t is a stopping time) and r' is dominated by a geometric variable of mean L. The evaluations of Y after t and before its DP are at most r' fresh evaluations, each a collision with conditional probability at most (Q + 2^16) / N' given the history (L1; the last one, a DP-valued evaluation, is covered by E2, and counting it here only overcounts). For this bound W(t, y) is taken without the restriction to N1 <= k - 1 and outside E1, E2: it is the event (tau = t, V_t = V_y), which is F_t-measurable, so P(W(t, y) and disturbed) <= P(W(t, y)) L (Q + 2^16) / N'; the events W(t, y) for different (t, y) are disjoint (the values V_y are distinct before tau), so the sum of P(W(t, y)) is at most P(tau <= Q) <= sum over t of (t - 1)/N' = PP: PP L (Q + 2^16) / N' = P_dist.

Step 5 (the sum). With P(tau <= Q, N1 <= k - 1) >= 1 - Pi_(Q-k+1) - 2^-40 >= 1 - P_coll - 2^-40 (Pi_(Q-k+1) <= Pi_Q / (1 - kQ/N'): n0(Q) >= Q - k + 1 on N1 <= k - 1 and Pi decreases) and Step 3, the attempt succeeds unless one of the failures (a) to (e) occurs for the first collision, or E1, E2, N1 >= k occur, or the run halts early: P_F >= 1 - P_coll - 2^-40 - P_own - P_long - P_delay - P_age - P_dist - 255 Q / N' - P(E1) - P(E2) - P(early halt). The early halts are charged in Step 6 (second cut) and Step 7 (table full, key false match, stage-1 budget).

Step 6 (the cut count and the long trails; no premise). Let K be the number of trails that the run cuts or would cut (the third one halts the run). Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.
(i) K_A. A trail counted by K_A has c fresh evaluations with non-DP outputs at c consecutive positions of its lane, so xi = 0 there; different such trails of a lane use disjoint positions. Scan each lane with trials: a trial starts at the current position u and succeeds if the c positions u, ..., u + c - 1 are all 0 (next trial at u + c); otherwise it fails at its first 1 (next trial after that 1). The scan of a lane stops at the first trial that would start after the run. Inside a maximal run of 0s the trials start at its first position and succeed floor(length / c) times, the largest number of disjoint length-c windows it holds; so K_A on a lane is at most the successes on that lane. Every failure but the last of a lane ends at a 1 of the run, so the failures are at most N1 + 256 <= k - 1 + 256 on N1 <= k - 1. Trial outcomes are independent Bernoulli(p'), p' = (1 - theta)^c <= p = e^(-c/L) (disjoint positions of an i.i.d. lottery; lanes concatenated as in (L3)). All successes therefore occur before failure number k + 256 of an infinite i.i.d. trial sequence, and three successes before that failure mean three successes among the first n2 = k + 258 trials:
    P(K_A >= 3, N1 <= k - 1) <= P(Binomial(n2, p) >= 3) = 1 - (1 - p)^n2 - n2 p (1 - p)^(n2 - 1) - C(n2, 2) p^2 (1 - p)^(n2 - 2)
(the tail increases with p, so p = e^(-c/L) is allowed).
The same scan counts the long trails of Step 2: a long trail of the free run is a window of c coins 0 at its start, the windows of different trails of a lane are disjoint, and a run of 0s holds at most floor(length / c) disjoint windows, which is what the scan finds; so the number of long trails is at most the number S_c of successes. The trial outcomes form one i.i.d. Bernoulli(p') sequence read in a stopping-time order (L3), so Wald's identity gives E S_c = p' E T, T = S_c + F_c the number of trials, with F_c <= N1 + 256 the number of failures, E F_c <= q + 256: E S_c <= p (q + 256) / (1 - p) (used in Step 4 (c)).
(ii) K_B. A trail T in K_B has a first non-fresh evaluation at age <= c - 1. Its previous evaluation t (age a(t) <= c - 2, T fresh up to t, so a(t) <= g(t), where g(t) is the number of consecutive 0s of the lottery just before t on its lane) is fresh, and V_t equals the input of an earlier fresh evaluation e' (the first evaluation of that input; a start is excluded). Call t the joining collision of T and e' its target. For a lane position e let sigma(e) be the number of positions from e to the first 1 at or after e (inclusive), and f'(e) that position: sigma is a function of the lottery, so it is determined by G. Choose T in K_B with the earliest joining collision. One of the following root events occurs:
- S: e' is on T itself. T then cycles through its own non-DP points and is cut.
- X: e' is on another trail T' and a(t) + sigma(e') >= c (hence g(t) + sigma(e') >= c).
- J2a: e' on T', a(t) + sigma(e') <= c - 1, and T' has a collision at a fresh position in [e', f'(e')).
- J2b: e' on T', and e' lies in a run of 0s of length >= c of its lane.
- Y: some trail has a collision at a fresh evaluation t'' while it has been fresh for at least c - 1 evaluations (g(t'') >= c - 1).
Proof that one occurs. Suppose not S, X, J2a. T evaluates the inputs evaluated by T' from e' on, one batch later or more, so T repeats them (non-fresh) while T' is ahead. If T' evaluates e', e' + 256, ..., f'(e') freshly (no collision there by not-J2a, and every non-fresh evaluation of T' is preceded by a collision of T'), the output at f'(e') is a DP (fresh, xi = 1), and T outputs the same DP at age a(t) + sigma(e') <= c - 1, before any slice check can cut it: T is not cut, a contradiction. If the run ends first, T, which is behind, is not cut either. So T' is cut before f'(e'), with all its evaluations from e' to the cut fresh. If all evaluations of T' from its start to the cut are fresh, they are >= c consecutive 0s containing e': J2b. Otherwise T' has a non-fresh evaluation before e', hence a joining collision before e' and before t; if it is at age <= c - 1, T' is in K_B with an earlier joining collision than T, against the choice of T; if not, the first c evaluations of T' were fresh and T' collided at age >= c - 1 while fresh: Y. QED.
Expected numbers of root events, each from the hazard (L1) (a collision of t with a given earlier value has conditional probability at most 1 / N' given G_(t-1), which includes the lottery, so lottery conditions can be attached):
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; E[g(t) + 1] <= sum for i >= 0 of (1 - theta)^i = L, so E_S <= Q L / N' = 3.559e-05.
- X: E_X <= sum over pairs e' < t of P(sigma(e') + g(t) >= c) / N'. Different lanes: sigma(e') - 1 and g(t) are independent and dominated by geometric variables on {0, 1, ...}, so the probability is at most P(at most one 1 in c - 1 Bernoulli trials) = (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. Same lane, e' = t - j 256: if a 1 lies between them the two runs of 0s are disjoint and the same bound p2 holds; if the j positions are all 0, the probability is at most (1 - theta)^j T(c - 1 - 2j) with T the tail above (T = 1 below 1); the sum over j of these is at most L e^(-(c - 2)/(2L)) (2 + (c - 1)/L). Hence E_X <= (Q / N') L e^(-(c-2)/(2L)) (2 + (c-1)/L) + PP p2 = 1.677e-05.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^16) / N': E_J2a2 <= (Q + 2^16) L Q (Q - 1) / (2 N'^2). E_J2a = 3.592e-05.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2 = 1.597e-05.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 1.140e-06.
So P(K >= 3) <= P(K_A >= 3, N1 <= k - 1) + P(N1 >= k) + P(K_B >= 1) <= P(Binomial(n2, p) >= 3) + E_S + E_X + E_J2a + E_J2b + E_Y + [P(N1 >= k), charged once as 2^-40]; P(Binomial(n2, p) >= 3) = 4.878e-05 and P_cut = 1.542e-04 (the program's `cut_halt`). There is no premise about K: the number of cut trails is bounded by this argument, and it needs no distribution of K. The bounds on S and J2a are not small (about Q L / N' each); they are the real cost of trails that close a cycle or join a path that is itself disturbed.

Step 7 (the early halts and the small terms). The attempt can end before it outputs the pair of Step 3 only by an early halt or by the events E1, E2, N1 >= k: the third cut (P_cut, Step 6); the table full (finished trails are at most N1 + 59 outside 60 or more collisions, so tmax keys need N1 >= tmax - 59: P_table = 1.8e-12); a key false match (P_key = 4.6e-04: the stored ends are at most tmax fresh DP values, uniform on the DP class, and the key space is 2^31 * 441 = 2^39.78); the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^32 = 7.96e+28: the fresh stage-1 hits are at most the sum of eta_t = 1[low 32 bits of V_t zero], exactly Binomial(Q, 2^-32), above 1.5 mu2 with probability at most e^(-0.108 mu2); the repeated hits after merges come from at most 60 colliding trails, each repeating at most M points that lie in at most 60 lane windows of total length at most M, and every such union of windows holds more than 2 M / 2^32 hits with probability at most e^(-0.386 M / 2^32), so with 240 M <= Q (checked: M = 1.567e+35, Q = 3.418e+38) the repeated hits are below mu2 / 2 except with probability below e^-1000; a recovery with no pair (a key false match, counted, or a start on another trail, 2^-100). The number of collisions: every fresh evaluation with xi = 0 is a collision with conditional probability at most (t - 1 + 2^16) / N' (L1), so E w^(number of collisions) <= exp((w - 1) H) for w = e^5 (the factor per evaluation is at most 1 + (w - 1)(t - 1 + 2^16)/N' <= e^((w-1)(t-1+2^16)/N')), and P(60 or more collisions) <= exp(-300 + (e^5 - 1) H). P_tiny collects Q 2^16 / N (E1), k^2 L / N' (E2), 255 Q / N' (Step 4 (b)), exp(-300 + (e^5 - 1) H), and 2^-90 for everything else of this step (the stage-1 budget, the recovery with no pair) and for the rounding of the factors 1 - kQ/N' and of the enclosures of Pi (each below 2^-96). This proves the lemma. QED.
Consequently P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny = 1 - 0.603765898 - 0.005516 - 3.559e-05 - 2.992e-05 - 1.597e-05 - 1.796e-05 - 1.542e-04 - 9.1e-13 - 4.6e-04 - 1.8e-12 - 2^-90 = 0.390000001 (float, planned at 0.390000001; the printed terms are rounded), and the exact certificate of Appendix A is 0.390000001000 >= 0.39 (B is the least multiple of 10^24 that reaches the planning target).

Sensitivity to H1 (d). If the hazard of a collision is (1 - eps) / N instead of 1 / N (clause (d) of H1; the same sensitivity as a deficit eps of the pair-collision rate in clause (a)), the plan of this program (same lemma with N / (1 - eps)) needs, to restore 0.39: 0.0072 bit for eps = 0.01 (Tp 439); 0.0370 bit for eps = 0.05 (Tp 430); 0.0761 bit for eps = 0.10 (Tp 418); 0.2077 bit for eps = 0.25 (Tp 382).

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function g and about one attempt; it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved: an assumption, no proof is known. Its content, in the terms Lemma 2 uses, is four clauses: (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of g from the starts r + t have the first-collision law of a random mapping; (c) whether an iterate is a DP is independent of the collision events and has probability 441 / 2^122; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of g; clause (d) is that this adaptivity does not lower the collision hazard, that is, for every fresh evaluation, given the whole history of the run and which later outputs are distinguished points, the output equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard that F has by construction, L1 of Section 4). Lemma 2 proves the bound for F from the hazard alone (a supermartingale over the evaluations, no conditioning on which trails finish), and (d) is the premise that g has that hazard. Nothing else in the success bound is heuristic: Lemma 1, the lazy-sampling facts, the supermartingale, the counting of pairs, the Chernoff bounds and the cut count are proved in Section 4 for F; Sections 3 and 7 are counts of the program. Sensitivity: a hazard (1 - eps) / N costs the same as a deficit eps in clause (a): 0.0072 bit for eps = 0.01, 0.0370 bit for eps = 0.05, 0.0761 bit for eps = 0.10, 0.2077 bit for eps = 0.25 (Section 4). The only evidence for (a) to (d) is the program checks of Section 6 and the toy runs below, which do not reach the full 256-bit event and are not used as estimates.
Support of H1 (stated; it is not measured at width 256). (1) It is the generic premise of parallel collision search with distinguished points (van Oorschot and Wiener, J. Cryptology 12 (1999) 1-28): a fixed compression function, iterated from fresh starts with no chosen input difference, is modelled by a random function. The generic entries of this track rest on it; on the board, with status review: 3017c952 (round 51), 1884db5b (round 57), 3642e1cd, 6b678689 and 4684dfc2 (round 64; 4684dfc2 is the source of walk B), and our d4f8f4e4 to 05004d0b (rounds 40 to 53) with this H1. (2) Clause (d) fails only if g, along its own iterates, collides less often than a random function by a constant factor 1 - eps; that is a property that separates 47-step SHA-256 from a random function. This entry uses no differential property. (3) A deviation that raises the hazard only helps; a deficit eps is priced in Section 4.
The two organizer experiments (Section 6) are program checks: the organizer recomputes the complete two-block digest of every returned pair. Observations consistent with H1 at reduced scale, from our local run of the organizer's pipeline on this program (its Docker policy and trial seeds; the organizer's own run reports its own counts). They are reproducible observations, not estimates: no interval or population bound is drawn from them, and H1 rests on the support above. Beside each count of 16-bit digest pairs is its reference value for 256 independent uniform 16-bit values per trial (exact: P(a pair) = 1 - prod_{i<256} (1 - i / 2^16) = 0.392678, 100.53 of 256 trials; mean number of equal pairs C(256, 2) / 2^16 = 0.498047 per trial, 127.50 over 256 trials).
    bssha-n16 (our local run of the organizer pipeline): 180 of 256 trials returned a pair that the organizer verified (complete two-block digests equal in the low 16 bits); halts 76 (a program check; no reference value).
    proj-k0-w256 (our local run): 89 of 256 trials returned a verified pair (reference 100.53); by source: uniform 32 of 86; counter 24 of 85; iterates of g 33 of 85; equal pairs in the low 16 digest bits (program's own), total over 256 trials: 116 (reference 127.50).
Every unsuccessful attempt of the width-16 experiment ended with a halt of the program (the halts equal the unsuccessful trials). At width 16 a halt "recovery found no pair" (a trail start lying on another trail) is frequent; at width 256 it has probability below 2^-100 (Section 4).
Toy-scale end-to-end runs of the same search on the same program (the low 30 and 36 bits of the digest, outside the shipped experiments, checked against the organizer reference): n = 30: 13 of 30 single attempts returned a pair, 13 of 13 confirmed by the organizer reference (distinct messages, equal low 30 bits of the complete 47-step digests); n = 36: 7 of 20 single attempts returned a pair, 7 of 7 confirmed by the organizer reference (distinct messages, equal low 36 bits of the complete 47-step digests).
Not tested: the full 256-bit functional graph; iterations of length above 2^40; the bit-sliced search above width 36. A deviation of g from H1 that raises the collision rate only helps; one that lowers it by eps costs the extra time of Section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/bssha.py` (it dispatches on the experiment id; standard library only). In both, the complete digest of a returned message is what the organizer recomputes: the 64-byte message, padded to two blocks.
`bssha-n16`: per trial, one attempt of the 256-lane search at width 16 (DP = low 2 bits zero, plan(16): 7 batches, cut rule, table, recovery) on the walk g16(x) = the low 16 bits of the complete digest of M(x), x < 2^16. Each batch runs the shipped program on the 256 planes (the 240 high input planes zero), then the experiment's digest network (`DigestNet`, bit-sliced, experiment code only, not in the ledger) inverts walk B, forms cv1 = IV + state and runs block 2; the recovery runs the rolled recovery program and the same inverse and block 2 in scalar form. The trials run side by side: the planes of trial i occupy bits 256 i to 256 i + 255 of each word, so one pass of the program and of the digest network serves every live trial, and each bitwise record acts on every trial's 256 bits alone. The trial returns M(x), M(y) when the attempt succeeded and two nulls otherwise. Checked event: the messages are distinct and their complete 47-step digests agree in the low 16 bits. This is exact, because at width 16 the walk is those 16 digest bits. The width-16 walk differs from the width-256 walk g only in the map after the program (inverse, block 2, low 16 bits); it runs the same program, search, table and recovery.
`proj-k0-w256`: per trial, 256 points at width 256 (source by trial index mod 3: uniform from the seed, counter r + i, iterates of g from 256 seed-derived starts) evaluated with the shipped program; their complete digests are formed by the digest network; the trial returns two points whose digests agree in the low 16 bits when the set holds such a pair. Checked event: as above. It checks at full width the program, the inverse of walk B, the chaining value, block 2 and the message construction.
They do not measure the cost or the success probability at width 256; the counts are program checks, not estimates. Running times on the development machine: 2.8 s and 3.2 s for 256 trials each.

## 7. Memory

Table: 29,659 entries * 22 bytes = 652,498 bytes (the table region is empty until the search starts). An entry is the key (40 bits in 5 bytes), the trail number t (2 bytes) and the length (15 bytes, below c + 2^48 < 2^119); `pack_entry` of the program builds and checks it.
Code: 56,657 body records * 5 bytes (an opcode and three 10-bit register fields, no immediate: the convention of Section 3.1) = 283,285 bytes, plus 1,684 other instructions * 36 bytes (opcode, registers and an inline 256-bit immediate; stage 1 34, batch loop 3, handlers 1,000, recovery 487, setup, cut and slice 160) = 60,624 bytes: 343,909 bytes in all.
Counters and copies: 16,384 bytes (trail numbers 512, birth batches 4,096, counters, and the 8,192-byte copy of the 256 planes used by the handlers). The 1,024 registers (the 1021 the program uses and three pointers), counted as memory: 32,768 bytes. The array of the rolled recovery program (the schedule words W0..W46 and the constants K0..K46, one 32-byte word each): 3,008 bytes. No advice. Memory peak = max(setup phase 597,835, search phase 1,048,567) = 1,048,567 bytes <= 2^20 = 1,048,576; the preprocessing is inside the setup phase. Claim `memory_log2_bytes` = 20. `python3 bssha.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 343,909 - 32,768 - 16,384 - 3,008) / 22) = 29,659, and Tp = 441 is the plan of Appendix A: the mean number of trails is the largest that the table holds with a capacity tail below 2^-40, and Tp is the largest integer (found by bisection; any Tp is a valid plan) for which the success bound of Section 4 reaches the planning target 0.390000001 at that mean (Appendix A computes both and certifies P_F >= 0.39 in exact arithmetic).

## 8. Heuristics, conventions and what is credited

The premise of this entry is H1 (the model premise of Sections 4 and 5, clauses (a) to (d), score-critical); the machine prices (the 1,024-register file; the 5-byte price of a body record with no immediate operand, every other instruction 36 bytes; every NOT, move, load, store and loop-control record charged one operation) are the declared cost model of Section 3.1, not a heuristic. Lemma 2 proves the cut count (no cut-count heuristic); its form (bounded restart, the detection delay integrated) is that of our blake3 entry 76ab339a and of TheTradoor's 09fe5fcd on the blake3 lane (other lane, not declarable). There is no advice and no polarity search; the prefix W0..W7 is a fixed constant of the program, computed in closed form.
Credited (all dependencies, same challenge): our 87cb17fa (the search, handlers, ledger method, the unrolled kernel, its allocator and C generator, the rolled recovery, the experiments' form); mitchuski's 4684dfc2 and 1884db5b (walk B, Sections 1 and 3.2; re-implemented from the notes, our own inverse and output order); lamb356's 3642e1cd (carry-in absorption of the folded constant, Section 3.2); dariolina's 6b678689 (the 5-byte body price and the full unroll, Section 3.1); dariolina's 744875ec (no feed-forward and the prefix that zeroes state words, which this entry extends to 8 words, Sections 1 and 3.2); lamb356's 44870635 and sraiw's 38912d66 (two-block messages on this lane, Section 1). Also credited, on other lanes and not declarable: jungjipdo's 6ae36351 (the pivot full adder) and our blake3 entries 0a9640ed and 62cfd777 (the bit-sliced chain and the declared register file). We used or ran no file of any rival entry.
New in this entry: the 64-byte two-block layout with the 8-word prefix that cancels K8 and K9, the offset words W(8+k) = y_k - K(8+k), walk B on that layout with the zero-move output order, and the C generator for all of it.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate, and `certify` recomputes the bound of Lemma 2 in exact rationals and 60-digit decimals with outward rounding: the line `P_lower certified` is a proved lower bound on P_F, asserted >= 0.39. The same numbers come from `python3 bssha.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 56657, 34, 3, 256      # records executed per batch (setup excluded), stage-1 test, loop control, lanes
GEN_CALLS, INSTR_REC = 1516486, 56657             # generator primitive calls of both passes of the network (python3 bssha.py --ledger), records of the program
PH7, EXTRA, RECINIT = 2113, 64, 112          # records executed per call of the rolled recovery program, extra operations per recovery batch, records executed once per recovery
N_BITS, S1, W, KAPPA = 256, 32, 90, 13          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, ARRAYS = 36, 1647, 32768, 16384, 22, 0, 3008
KEYB = 40                                             # key bits (5 bytes)
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 24, 16                       # B is a multiple of GRAIN; trail-number bits of a table entry
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP                                        # one batch = 56,694 operations
code_bytes = INSTR_REC * 5 + (FILT + LOOP + OTHER_CODE) * INSTR     # the body records once at 5 bytes, every other instruction once at 36 bytes
tmax = ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE - ARRAYS) // ENTRY  # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


def plower(Tp, q):            # the lower bound of Lemma 2 on the success probability, q = Q / L (floats, as the program's _lossq; certify() below is the proof)
    L = Fraction(1 << D, Tp)
    c = -(-KAPPA * L.numerator // L.denominator)
    th, Lf, cf = Tp / 2.0 ** D, float(L), float(c)
    Q, B, Np = q * Lf, q * Lf / LANES, 2.0 ** N_BITS
    k = int(q) + 1
    while tail_log2(q, k) > -40:                               # N1 ~ Binomial(Q, theta) <= k - 1 except with probability 2^-40
        k += 1
    n2, shift = k + LANES + CMAX, 1 / (1 - k * Q / Np)
    pi = lambda m: exp(-m * (m - 1) / (2 * Np))
    split = max(1.0, Q - 120 * LANES * Lf)
    edges = [split * i / COARSE for i in range(COARSE + 1)] + [split + (Q - split) * i / FINE for i in range(1, FINE + 1)]
    delay, pa = 0.0, 1.0
    for b in edges[1:]:
        pb = pi(b)
        delay += (pa - pb) * exp(-th * max(0.0, B - b / LANES))
        pa = pb
    p, ql, hq = exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np)
    p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** TB * Q) / Np
    cuts = 1 - sum(comb(n2, j) * p ** j * exp((n2 - j) * log1p(-p)) for j in range(CMAX + 1))
    t = [pi(Q) * shift, delay * shift, ql, (cf + SB) * Q * p * (q + LANES) / ((1 - p) * Np), hq * p2, hq * Lf * (Q + 2.0 ** TB) / Np, 2.0 ** -40,
         cuts + ql * (1 + (2 + KAPPA) * exp(-KAPPA / 2) + 2 * hq) + hq * p * (3 + 2 * KAPPA),
         tmax * (tmax - 1) / 2 * 2.0 ** -(min(KEYB - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp)), 2.0 ** tail_log2(q, tmax - 59),
         Q * 2.0 ** TB / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** -90]
    return 1 - sum(t)


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


def certify(Tp, B):           # Lemma 2 in exact rationals and 60-digit decimals (every exp and ln correctly rounded), results moved outward by 1e-40
    from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
    getcontext().prec = 60
    up = lambda x: x * (1 + Dm("1e-40")) + Dm("1e-58")
    dn = lambda x: x * (1 - Dm("1e-40")) - Dm("1e-58")

    def fd(x, u):             # Fraction -> Decimal rounded up (u) or down
        with localcontext() as cx:
            cx.rounding = ROUND_CEILING if u else ROUND_FLOOR
            return Dm(x.numerator) / Dm(x.denominator)
    ex = lambda x: up(fd(x, True).exp())                         # upper bound on exp(x), x rational
    L = Fraction(1 << D, Tp)
    th, Q = 1 / L, LANES * B
    Np = Fraction(Nn - Tp * (1 << (N_BITS - D)))                 # N' = N (1 - theta), an integer
    q = Q / L
    c = -(-KAPPA * L.numerator // L.denominator)
    M = c + SB
    qu, qd, lne = fd(q, True), fd(q, False), -Dm(2).ln() * 40
    k = int(q) + 1                                               # P(N1 >= k) <= e^-q (e q / k)^k <= 2^-40
    while up(-qd + k * (1 + (qu / k).ln())) > lne * (1 - Dm("1e-40")):
        k += 1
    n2 = k + LANES + CMAX
    shift = fd(1 / (1 - k * Q / Np), True)                       # Pi_(t-k) <= Pi_(t-1) shift, t <= Q
    lam = lambda m: Fraction(m * (m - 1), 2) / Np
    pi_up = lambda m: up((-fd(lam(m), False)).exp())             # Pi_m <= exp(-m (m - 1) / (2 N'))
    pi_lo = lambda m: dn((-fd(lam(m) + Fraction((m - 1) * m * (2 * m - 1), 6) / Np ** 2, True)).exp())   # ln (1 - x) >= -x - x^2 for x <= 1/2
    split = max(1, Q - 120 * LANES * (1 << D) // Tp)
    E = [split * i // COARSE for i in range(COARSE + 1)] + [split + (Q - split) * i // FINE for i in range(1, FINE + 1)]
    delay, pa = Dm(0), pi_up(E[0])
    for a, b in zip(E, E[1:]):
        pb = pi_lo(b)
        R = max(0, B - (-(-b // LANES)))
        delay += (pa - pb) * ex(-th * R)                         # sum over the bins (a, b] of (Pi_a - Pi_b) (1 - theta)^(B - ceil(b / 256)) <= e^(-theta R)
        pa = pi_up(b)
    delay = up(delay) * shift
    p = ex(-c * th)                                              # (1 - 1/L)^c <= e^(-c / L)
    p2 = ex(-(c - 1) * th) * fd(1 + (c - 1) * th / (1 - th), True)
    Hs = Fraction(Q * (Q - 1), 2) + (1 << TB) * Q
    H, PP = Hs / Np, Fraction(Q * (Q - 1), 2) / Np
    EK = p * (fd(q, True) + LANES) / (1 - p)
    terms = [pi_up(Q) * shift, delay,                            # collision (no partner), detection delay
             fd(Q * L / Np, True),                               # the partner is on the trail of t
             up(fd(Fraction(M * Q) / Np, True) * EK),            # the partner is on a trail with c free evaluations
             fd(PP, True) * p2,                                  # trail of t too old when the DP is reached
             fd(PP * L * (Q + (1 << TB)) / Np, True),            # a collision on the rest of the path
             Dm(2) ** -40,                                       # N1 >= k
             up(1 - sum(comb(n2, j) * p ** j * (1 - p) ** (n2 - j) for j in range(CMAX + 1))),   # step 6: fresh cut trails, P(Bin(n2, p) > CMAX)
             fd(Q * L / Np, True),                               # S
             fd(Q / Np, True) * fd(L, True) * ex(-(c - 2) * th / 2) * fd(2 + (c - 1) * th, True) + fd(PP, True) * p2,   # X
             fd(Q * L * H / Np + (Q + (1 << TB)) * L * PP / Np, True),   # J2a
             fd(PP * (1 - th), True) * p2, ex(-(c - 1) * th) * fd(H, True),   # J2b, Y
             fd(Fraction(tmax * (tmax - 1), 2 * Tp) / (1 << min(KEYB - (Tp - 1).bit_length(), N_BITS - D)), True),   # key false match
             up((-qd + (tmax - 59) * (1 + (qu / (tmax - 59)).ln())).exp()),   # table capacity
             fd(Fraction(Q << TB, Nn) + Fraction(k * k) * L / Np + 255 * Q / Np, True) + up((-300 + (Dm(5).exp() - 1) * fd(H, True)).exp()) + Dm(2) ** -90]
    assert Fraction(Q, 1 << 32) * Fraction(108, 1000) > 1000 and 240 * M <= Q   # stage-1 budget (Step 7): below e^-1000, inside the last term
    return 1 - sum(terms)


lo, hi = 1.0, tmax + 1.0                                       # the largest mean number of trails the table holds (tail within 2^-40)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
a, z = 1, 4097                                                 # bisection: a Tp that reaches 0.39 at that mean (any Tp is a valid plan; not claimed optimal)
while z - a > 1:
    m = (a + z) // 2
    a, z = (m, z) if plower(m, lo) >= P_MIN else (a, m)
Tp = a
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + INSTR_REC)
rows = [("main loop: B * %d" % body, body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 2 * 4200", CMAX * CUTOPS),
        ("recovery: (c + 2^48) * (%d + 64) + 600 + %d" % (PH7, RECINIT), capr * (PH7 + EXTRA) + 600 + RECINIT),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE + ARRAYS)
print("P_lower = %.5f" % plower(Tp, float(B * LANES / L)))
pc = certify(Tp, B)
print("P_lower certified (exact rationals, 60-digit decimals) = %s" % str(pc)[:14])
assert pc >= Fraction(39, 100)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 3484
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
Tp = 441  tmax = 29659  B = 1335287087142000000000000000000000000  e2max = 159178625004529953002929687564  c = 156734366849922053040811716858453329
memory bytes = 1048567
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000001000
main loop: B * 56694                                 75702766118428548000000000000000000000000
slice checks: ceil(B / 2^48) * 1300                  6167060509499577847237000
stage-1 hits: e2max * 2800                           445700150012683868408203125179200
finished trails: tmax * (3800 + 3 * tmax)            2751673043
cut trails: 2 * 4200                                 8400
recovery: (c + 2^48) * (2113 + 64) + 600 + 112       341210716632280309470459878625151996057
setup and generator                                  315442200
N = 76043977280760984489214837786409191535900
certificate: 2^12403742 * 3484^100000 <= N^100000 < 2^12403743 * 3484^100000
log2(N/C) = 124.0374288772
time_log2 = 124.03743
```
