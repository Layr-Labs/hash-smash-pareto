# sha256-r64: birthday search with a bit-sliced kernel of 256 lanes, distinguished points on planes, recovery with the packed kernel

This entry is a credited derivative of the accepted sha256 round-39 package (itself a derivative of 368d1718-a059-4780-9f08-8f0931a46f0d, Jbenisek, 124.84811; through it of 01e31be9-0524-4b77-a40e-c1f862d506a8, of the blake3 round-3 entries 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c, 3356413f-cd60-410c-8847-2266d6444ac5, cf8b0e92-4302-4813-907a-3c970c102646 (the packed-lane chain), 62cfd777, and of e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca). It ships the program `experiments/shrho64.py`, the round-39 program `shrho.py` run at 64 steps with one structural change and one new machine convention. The change: the main loop no longer evaluates 7 trails packed in 36-bit lanes of a word; it evaluates **256 trails at once in a bit-sliced representation**, one 256-bit machine word per bit position of each of the 8 state words (a plane; lane l is bit l of every plane). Rotations and shifts become relabelings of planes and cost nothing, each addition ripples through full adders of 5 operations per bit, the round constants are folded bit by bit, and a plane may be kept complemented until an AND or OR needs it. The kernel is **100,212 operations for 256 trails** (391.5 per trail, 0.0797 of the 4,912 operations of one reference compression) against 4,216 for 7 trails (602.3 per trail, 0.1228 of C) for the round-39 program's packed kernel run at 64 steps. The recovery walk, which handles two trails, keeps the packed kernel at 64 steps (its sliced evaluation would cost 100K operations per step). Everything else is the round-39 package's: the walk on the digest minus the IV (Lemma 0), its constant prefix P that zeroes the state after step 4, the search with distinguished points, the handlers (scaled to 256 lanes), the ledger method, the success argument, the two organizer experiments (adapted to 256 lanes) and the C port of the generator (extended to the sliced generator).
The convention: the sliced kernel keeps 866 planes live, and its 100K-line body has no immediate operands. This entry therefore declares (heuristic H3, Section 3.1) a register file of **R = 1024 words of 256 bits** (32,768 bytes, counted as memory) and a **5-byte register-to-register instruction** for the main loop body (36 bytes are kept for the packed recovery kernel, the handlers and the generators, as in the round-39 package). Under those two conventions time_log2 is **124.41766** with memory 1,048,570 bytes <= 2^20 (so the scalar score equals time_log2). Section 3.5 prices the whole trade-off: with the round-39 package's own convention (64 registers, 36-byte instructions) the sliced kernel is worse than the packed one or does not fit in 1 MiB at all, and the same ledger with the packed kernel in the main loop (7 lanes, 64 registers, 36-byte instructions) gives 124.97721. The gain of this entry exists only together with its convention, and the convention is declared, not hidden.
The target is the plain one: M(x) = P || x, 52 bytes in one block with FIPS padding, the standard IV, the 64 steps with indices 0 to 63, the feed-forward, the complete 256-bit digest. No advice is used and no differential property; the step structure is used only by the prefix, to make the kernel cheaper, never for the success probability.

## 1. Target and relation

Target `sha256-r64-prefix-v1` (the Pareto lane `sha256`, round 64: "Execute indices 0 through 63, inclusive, on every padded block"). The two colliding messages have 52 bytes: M(x) = P || x, with P the 20 bytes 03f777b3 eec88896 e8ebdb1c 1b70c247 177c95e3 (hex, big-endian words W0..W4) and x the 256-bit integer written as 32 bytes big-endian. FIPS 180-4 padding (0x80, zero bytes to 56 modulo 64, then the 64-bit big-endian bit length 416) makes one block: W0..W4 = P, W5..W12 = the eight big-endian 32-bit words of x, W13 = 0x80000000, W14 = 0, W15 = 0x1A0. The compression executes the 64 steps of the standard schedule and constants, starts from the standard IV, and adds the incoming state to the working state at the end. The digest is the eight state words, big-endian (`verifier/hash_functions.py:digest(M(x), "sha256", 64)`). Write s(x) for the working state after step 63 as 8 words (a, b, c, d, e, f, g, h), and f(x) for s(x) read as a 256-bit big-endian integer. Then digest(M(x)) = IV + s(x), word by word modulo 2^32 (the feed-forward with the standard IV, the only IV of a one-block message).
**Lemma 0.** For all x, y: f(x) = f(y) if and only if digest(M(x)) = digest(M(y)). *Proof:* adding the fixed IV word by word is a bijection of the 8-word state. ∎
The walk is x -> f(x); the 8 state words are the next input words W5..W12 (chain word j is message word W(5+j)). The attack outputs x != y with f(x) = f(y); by Lemma 0, M(x) != M(y) are two distinct messages with equal complete 256-bit digests. The profile's message domain is "finite byte strings of bit length below 2^64"; a 52-byte string is in it, and no length is fixed by the profile.
Prefix. P is the round-39 package's constant, unchanged, and its property concerns steps 0 to 4 only, so it holds for any round count: `prefix_words()` fixes the state words of steps 0 to 4 to A0 = A1 = 0, A2 = S0^-1(IV[0]) and A3 = A4 = 0 (S0 is GF(2)-linear and invertible; the program inverts it by Gaussian elimination and asserts S0(A2) = IV[0]). Each message word W_i fixes A_i, because E_i = A_{i-4} + E_{i-4} + S1(E_{i-1}) + CH(E_{i-1}, E_{i-2}, E_{i-3}) + K_i + W_i and A_i = E_i - A_{i-4} + S0(A_{i-1}) + MAJ(A_{i-1}, A_{i-2}, A_{i-3}). Then E4 = A4 + A0 - S0(A3) - MAJ(A3, A2, A1) = 0 and E3 = A3 + A_{-1} - S0(A2) - MAJ(A2, A1, A0) = IV[0] - IV[0] = 0. The program asserts both and that the constant P equals `prefix_words()` (selftest). Running steps 0..4 on P gives (A4, A3, A2, A1) = (0, 0, ba2ee7e3, 0) and (E4, E3, E2, E1) = (0, 0, 75969668, 126d4d6d). In the sliced generator the constant state and the constant words are folded automatically by the plane algebra: steps 0 to 4 cost no operation, step 5 costs 59, step 6 588, step 7 930, step 8 1,023, and the steady state is about 1,910 operations per step including its schedule word. This is a property of a constant of the program, not a restriction of the target.
Validation (none of it is used as an estimate):
- Against the organizer reference `verifier/hash_functions.py:digest(M(x), "sha256", 64)`: the program's scalar f plus the IV gave 0 differences on 300 random messages; the sliced kernel, two chained batches of 256 lanes against the scalar f and all 256 outputs of a batch plus the IV against the verifier digest of the full 52-byte messages, 0 differences; the packed recovery kernel, 7 lanes plus the IV against the verifier, 0 differences (run locally in the challenge checkout; the sandbox has no verifier).
- The selftest (`python3 shrho64.py --selftest`, output in Section 5) compares the allocated sliced code executed on a register file, the same code compiled to Python functions, and the scalar compression on 1,024 lanes (4 batches, lanes 0 and 1 all-zero and all-one), on whole batches of all-zero and all-one inputs, and on 3 chained batches; the packed kernel on 308 lanes and its allocated code; the recovery form f2; the stage-1 test, lane extraction and insertion on planes; the width-18 chain; and 16 search attempts at width 18 (14 of 16 returned a verified pair).

## 2. The attack (program `experiments/shrho64.py`, sections 4 to 6)

Parameters for n = 256 (all computed by `plan(256)` from the stated formulas, printed by `python3 shrho64.py --ledger`): N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 32 bits are zero (chain word 7, the message word W12 of M(x)) and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 154. The density is theta = 154 / 2^122 and L = 1 / theta = 2^122 / 154 = 2^114.73321. The key of a DP is the 56 bits of x above bit 121 followed by the 8 low bits of F (F < 154 < 2^8, so those bits are F); 64 bits in all (`plan`: fb = 8, kb = 56).
The search uses one fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the planes holds the current point of its trail (bit l of plane 32 i + j is bit 32 (7 - i) + j of the point). A batch is one evaluation of f for all 256 lanes by the generated straight line of Section 3.2; its 256 output planes are its next input planes. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch, the stage-1 test (Section 3.3) ORs the 32 planes of word 7 and compares the result with all-ones: a lane whose low 32 bits are zero has a zero bit in the OR. If the OR is all-ones, the next batch runs at once.
3. For each zero bit (a stage-1 hit), the lane's words 6, 5 and 4 are extracted from the planes and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above (words 3 and 2 and the top bits of word 4 extracted), length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, Section 7) and start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane: one bit of each plane).
4. At every multiple of S = 2^48 batches, a lane whose trail has age >= c = 13 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when a finished trail must be stored in a full table (10,966 keys; the 10,967th finished trail halts), when a third trail would be cut, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps of f, then step both together. At the first step with f(a) = f(b) and a != b, output (a, b). The two trails occupy two of the 7 lanes of one evaluation of the packed 64-step kernel (4,216 operations; the round-39 package's generator with 64 steps and 64 round constants), with an exact equality test of the two lanes on the 8 output words. At most capr = c + S batches are run (the program halts if l1 > capr); the ledger charges capr + 1 kernel evaluations, the last one being the step that exhibits the pair.
Constants: Tp = 154, L = 2658455991569831745807614120560689152 / 77, B = 1372642907409490479844181200006684859 = 2^120.0464, Q = 256 B = 2^128.04637 evaluations, e2max = 163631785799204168301127100055, c = 448830232342958606435051734640116351 (= 13 L = 2^118.434), table capacity tmax = 10,966 entries of 25 bytes, M = 350 (Section 4). The trail numbers t stay below 2^16 (finished trails <= 10,966, cut trails <= 2, plus the 256 starts), and every length is below c + S < 2^119. So the 2-byte and 15-byte fields of an entry never overflow; the program asserts both when it stores an entry.
Per attempt: one fresh r; no restart, no amplification, no stored collision, no nonuniform advice.

## 3. Operation ledger

### 3.1 Machine
The machine convention is declared by this entry (heuristic H3, score-critical because time_log2 depends on it; the benchmark fixes none of the points below). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units". Its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch" and "independent uniform random 256-bit word". Its memory includes "code", "working state" and "tables". It fixes the word size and prices loads and stores. It gives no register count, no rule for constants, no instruction size and no rule for packing several independent computations into one word.
This entry declares a load/store machine with 256-bit words and:
- **R = 1024 registers** of 256 bits, counted as memory (32,768 bytes). The sliced straight line keeps at most 866 planes live and the program's allocator assigns it 866 registers; the packed recovery kernel needs 68. The remaining registers hold the loop counter, the limit and the handlers' temporaries. Section 3.5 prices every smaller file from 768 down to 64 with the program's Belady allocation.
- **Two instruction sizes.** The main loop body consists of register-to-register instructions without immediate operands: the 100,224 lines of the sliced kernel (XOR, AND, OR, NOT of one register, and 12 register moves), the 31 ORs of the stage-1 test, and 5 control instructions (two compares, two branches, one increment, whose operands are registers and a code address). Each is charged **5 bytes**: an opcode byte and three 10-bit register fields in the other four bytes (4 bytes would hold a 2-bit opcode and the three fields, with NOT written as XOR with a register that holds all-ones and a move as OR of a register with itself; that encoding is priced as an alternative in Section 3.5). Every other instruction, with its inline 256-bit immediate, is charged **36 bytes** as in the round-39 package: the packed recovery kernel (whose masks and round constants are immediates), the handlers, the setup, and the two generators.
- One word operation is one operation whatever the word holds: here each word holds one bit of 256 independent trails. Each of the following is charged one operation: every addition, AND, OR, XOR, NOT, shift, comparison and conditional branch, the one random word, every load of a word from memory, every store of a word to memory, and every register move. The main loop has 12 moves (the allocator's final permutation of the output planes into the input registers) and no load or store. The organizer's reference count (`scripts/reference_operation_costs.py` of the benchmark repository) likewise counts only operations on data words; its docstring says that memory traffic is excluded, and constants enter it as plain operands.
The organizer's reference count C(sha256-r64) = 4912 (`reference_operation_cost` in `pareto_candidate.py --family sha256 --rounds 64 --show-contract`) is used only as the unit: Unit = 4912 operations.

### 3.2 One batch = 100,260 operations for 256 trails
Representation. The 8 state words of 256 trails are 256 planes; plane 32 i + j is the 256-bit word holding bit j of state word i of every trail (lane l is bit l). A 32-bit word of the compression is a list of 32 planes. A plane is either a constant (all-zero or all-one, never stored) or a node of the straight line with a polarity flag (the plane may be kept complemented); constants and complements never appear as operands of an emitted line.
- A rotation or a shift of a word is a relabeling of its planes: no operation. Sigma0 and Sigma1 are 2 XORs per bit (64 per word); sigma0 costs 61 and sigma1 54, the shifted-in zero planes folding away.
- An addition modulo 2^32 ripples from bit 0 through full adders: (sum, carry) = (x ^ y ^ z, maj(x, y, z)) in 5 operations for any polarity of the inputs, with maj(x, y, z) = x ^ ((x ^ y) & (x ^ z)) for positive inputs, maj(~p, y, z) = p ^ ((p ^ y) | (p ^ z)), maj(~p, ~q, z) = ~(z ^ ((z ^ p) | (z ^ q))), maj(~p, ~q, ~r) = ~maj(p, q, r); a half adder (one constant input) costs 2 (XOR and AND, or XOR and OR). Sums of several words are reduced by 3:2 carry-save layers to two words and then one ripple adder (the same number of full adders as sequential ripple adders, with the dropped top carries and the zero bottom carry saved). The round constant K_t and every other constant word are folded into one constant word added last (about 64 operations instead of 154 for a variable operand).
- Ch(e, f, g) = g ^ (e & (f ^ g)) or f ^ (~e & (f ^ g)), whichever form has matching polarities at the AND: 3 operations per bit. Maj(a, b, c) = b ^ ((a ^ b) & (b ^ c)) with a ^ b computed once per step and reused as b ^ c in the next: 2 operations per bit plus the shared XOR, 3 when the two shared XORs have opposite polarities (then a ^ c = (a ^ b) ^ (b ^ c) is formed).
- A complemented plane is materialised by one NOT, cached and shared, only when an AND or OR mixes polarities and De Morgan does not absorb the complement (~p & ~q = ~(p | q) costs nothing extra). The 256 output planes are materialised positive at the end (133 NOTs), because the next batch reads them as inputs.
Lines of the kernel (counted by the generator; `python3 shrho64.py --selftest` prints the counts per operation): **100,212 = 79,072 XOR + 13,813 OR + 6,036 AND + 1,291 NOT**, plus **12 moves** of the final permutation (Section 3.6), from 120,311 generator calls; no emitted line is dead (the selftest asserts it). By function:

| part | operations | note |
| --- | ---: | --- |
| T1 = h + Sigma1 + Ch + K + W (three variable additions, one folded constant) | 29,954 | 901 of the NOTs |
| schedule words W16..W63: three additions each | 19,760 | 412 per word; early words have constant operands |
| new a = T1 + Sigma0 + Maj (two additions) | 17,628 | |
| new e = d + T1 (one addition) | 8,574 | |
| Maj with the shared a ^ b | 6,336 | 3.4 per bit |
| Ch | 5,418 | 3 per bit; constants in steps 5 to 7 |
| sigma0, sigma1 of the schedule | 4,985 | XOR only |
| Sigma1 | 3,712 | 64 per step, XOR only |
| Sigma0 | 3,712 | 64 per step, XOR only |
| outputs: NOT of complemented planes | 133 | once per batch |

The first steps fold the constant IV, the constant words W0..W4, W13..W15 and the constant state of the prefix at build time (Section 1). There is no feed-forward. The polarity overhead is 1,291 NOTs plus 768 extra operations in Maj (2.1 percent), the price of folding K_t without normalising polarities.
Per trail with the loop overhead (Section 3.3): 100,260 / 256 = 391.64 operations, 0.07973 of C = 4912. The round-39 package's packed kernel run at 64 steps costs 4,216 operations for 7 trails (531 additions, 609 shifts right, 522 shifts left, 1,401 AND, 522 OR, 631 XOR; 62 percent of it in the 522 rotations of 5 operations); with its stage-1 test and loop, 4,223 / 7 = 603.29 per trail, 0.12282 of C. The ratio is 1.5404 = 2^0.6233. The packed kernel is relatively more expensive at 64 steps than at 39 (0.1111 of C = 2812 there), because the schedule's share grows from 23 of 39 words to 48 of 64.
Validation: Section 1 (verifier) and the selftest (the allocated code on a register file, the compiled code and the scalar f agree on 1,024 lanes; whole batches of zeros and ones; 3 chained batches), and the experiment checks of Section 5 (every returned pair of the full-width experiment verified by the organizer on the complete digests).
The generator runs once at the start. Its work is charged in the setup row (Section 3.3); its code and peak storage are accounted in Section 3.6 and Section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 100,212 + 12 moves + stage-1 test 33 + loop control 3 = 100,260 operations.
Stage 1: the OR of the 32 output planes of word 7 (31 operations), compared with the all-ones word, and a branch: 33 operations (`FILT_OPS`). Bit l of the OR is clear exactly when the low 32 bits of lane l are all zero. The test loses no event: a DP has its 32 low bits zero, so its bit is clear and the comparison fails.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no hit lane (probability about 1 - 2^-24) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the spare registers; every operation is one of the model's primitives):
- Stage-1 hit: the miss mask is the OR XOR all-ones (1 operation per hit batch). For each set bit: its lane number by binary search on the mask (8 levels of shift, AND, compare, branch and add: about 40), clearing the bit (2), extraction of words 6, 5 and 4 from the 96 planes (shift right by l, AND 1, shift left by j, OR: 4 per plane, 384), the window test F < Tp (word 6 < 154, word 5 = 0, the low 26 bits of word 4 = 0: 13) and the hit counter against e2max (4). Total below 450 per hit lane; charged **600** (the hit budget e2max is enforced by a halt).
- Finished trail (a DP, new start), charged **3,000**; the actual total is below 1,700:
  - extraction of words 3 and 2 (64 planes, 256) and key formation (about 20);
  - three read-modify-write field stores of the 25-byte entry (about 30);
  - length = b - birth (3) and the new start r + t' (1 add);
  - insertion of its 256 bits in the lane: for each plane, extract the bit of the start (shift, AND: 2), shift it to position l (1), clear bit l of the plane (AND with the lane mask: 1) and OR (1): 1,280, plus the lane mask (2);
  - lane arrays and counters (about 30).

  The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails are stored (a halt on a full table).
- Slice check (every 2^48 batches): the 256 births (load, subtract, compare, branch: 4 each) and the slice counter, charged **1,040** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **3,000**; at most 2 cut trails (a halt on the third).
- Recovery batch, charged as 64 operations beyond the packed kernel (4,280 per batch), for at most capr + 1 batches. It is one evaluation of the packed kernel for both lanes (4,216 operations) plus 39 operations: the exact equality test of lane 0 and lane 1 on the 8 output words (8 shifts, 8 XORs, 7 ORs, 1 AND with the lane-0 mask, 1 compare, 1 branch = 26), loop increment, compare and branch (3), call and return (2), and 8 moves of the inputs, needed to output the colliding pair. The first l1 - l2 steps move one lane only and need no test; they are also inside the 4,280. The packed kernel's 64 live words fit in the register file with no spill.
- Setup and generators: a fixed part charged 360,400 (1 random word, the 256 starts r + t transposed into the planes: 256 bits each, extracted and ORed into the zero planes, 4 operations per bit, charged 1,400 per start; counters: 2,000), and the two generators charged 92,302,400: 400 word operations per generator call and per emitted line (the round-39 package's charge), for 120,311 calls and 100,212 lines of the sliced generator and 6,017 calls and 4,216 lines of the packed one. Together 92,662,800 operations = 2^14.203 units, charged in the time bound (3.4). There is no other preprocessing: no scan, no climb, no advice. `prefix_words()` is not run by the attempt; the prefix is a constant of the program.

Code size: main loop body 100,260 instructions of 5 bytes (501,300 bytes) + the recovery kernel with its test 4,280 instructions of 36 bytes (154,080) + handlers, key scan, cut and slice checks and setup 1,600 instructions of 36 bytes (57,600) = **712,980 bytes**.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A and by `python3 shrho64.py --ledger` (the two agree).
| item | bound (operations) |
| --- | --- |
| main loop: B * 100,260 | 137,621,177,896,875,515,509,177,607,112,670,223,963,340 (= 1.3762e+41) |
| slice checks: ceil(B / 2^48) * 1,040 | 5.0717e+24 |
| stage-1 hits: e2max * 600 | 9.8179e+31 |
| finished trails: (10,966 + 1) * (3,000 + 3 * 10,966) | 393,693,366 |
| cut trails: 2 * 3,000 | 6,000 |
| recovery: (c + 2^48 + 1) * (4,216 + 64) + 600, c + 2^48 = 2^118.434 | 1.9210e+39 |
| setup and generators | 92,662,800 |
N = 139,542,171,389,482,454,895,914,856,823,180,739,673,666 = 1.395422e+41 operations.
N / 4912 = 2.8408e+37 units = 2^124.4176582. Claim `time_log2` = 124.41766 (integer power certificate in Appendix A, rounded up). The main loop is 98.62 percent of it, the recovery 1.38 percent (its share is larger than in the round-39 package because the trails are longer: L = 2^114.73 instead of 2^113.02, Section 3.5).

### 3.5 Register file, instruction size and the trade-off curve
Premise H3 has two parts, and the gain of the sliced kernel depends on both. The ledger below (`python3 shrho64.py --ledger`; every row is the program's full ledger with that convention: the register file R x 32 bytes counted as memory, the spill instructions counted as code at the body's instruction size, the table shrunk to what fits, Tp re-selected by the table rule of Section 7, and the losses of Section 4 recomputed) prices every alternative.
Smaller register files. The program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`, three chained batches with the middle one counted, so the input loads, the output stores and the interior spills of a steady-state batch are all charged) adds loads and stores to every batch:

| R | loads + stores per batch | operations per batch | code bytes | table entries | Tp | L | time_log2 | P_F lower bound |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 1024, 5-byte body (claimed) | 0 | 100,260 | 712,980 | 10,966 | 154 | 2^114.733 | **124.41766** | 0.39152 |
| 1024, 4-byte body | 0 | 100,260 | 612,720 | 14,976 | 215 | 2^114.252 | 124.39801 | 0.39155 |
| 768 | 784 | 101,044 | 716,900 | 11,137 | 157 | 2^114.705 | 124.42743 | 0.39153 |
| 512 | 3,587 | 103,847 | 730,915 | 10,904 | 153 | 2^114.743 | 124.46813 | 0.39152 |
| 256 | 15,949 | 116,209 | 792,725 | 8,759 | 121 | 2^115.081 | 124.64585 | 0.39149 |
| 128 | 25,056 | 125,316 | 838,260 | 7,101 | 96 | 2^115.415 | 124.77425 | 0.39146 |
| 64 (the round-39 package's file) | 40,491 | 140,751 | 915,435 | 4,096 | 51 | 2^116.328 | 125.02389 | 0.39129 |

The claim assumes R >= 866; 1024 is declared. The register file costs 32,768 bytes of the memory budget, which is why the table has 10,966 entries instead of the 27,851 that the same ledger gives the packed 64-step kernel (code 327,708 bytes, 64 registers); the smaller table lowers Tp from 416 to 154, lengthens the trails and costs about 0.06 bits in two places: the 256 unfinished trails hold M L = 350 L points at the halt (3.44 percent of Q, against 0.12 percent for 7 lanes; 0.048 bits) and the recovery walk is longer (0.015 bits). The kernel gain of 0.623 bits (Section 3.2) becomes 0.560 bits in the ledger.
Instruction size. The 100,260 instructions of the body have no immediate operand, so 5 bytes (or 4) encode each; at the round-39 package's 36 bytes per instruction the body alone would be 3,609,360 bytes, the program 3,821,040 bytes, and no table would fit in 1 MiB: with the 27,851-entry table of the packed 64-step machine the memory would be about 4.6 MB = 2^22.1, which adds 2.1 to the score. A rolled loop over 16 steps would cut the body eightfold but loses the folding of the round constants (about 106 more operations per step, with the constant planes loaded as data), a net loss of about 0.03 bits; it is not pursued.
The comparison. The same ledger (Appendix A with the packed constants: 4,216 + 4 + 3 operations per batch of 7 lanes, 36-byte instructions, R = 64, the round-39 package's handler charges, M = 32) gives **124.97721** for the round-39 package ported to 64 steps as it is (Tp 416, table 27,851, P_F >= 0.39156). So under the round-39 package's own convention the sliced kernel loses (125.02389 at R = 64 against 124.97721), and under this entry's convention it gains 0.560 bits (124.41766). A reviewer who holds the entry to 64 registers or to 36-byte instructions obtains the priced row; the success argument and the set of colliding pairs are unaffected by the convention.

### 3.6 Generator code and the setup phase
The two generators that build the straight lines at the start of the run are part of the machine code of this entry: the sliced generator (the plane tracer `Tracer`, the word functions, `build_sliced` and the allocator `Kernel.allocate`) and the packed generator of the round-39 package (`PTracer`, `build_packed`, `allocate_packed`). `python3 shrho64.py --gencode` counts 3,088 and 1,232 bytecode instructions; the entry charges 4,400 instructions (an upper bound), 158,400 bytes at 36 bytes each.
The sliced generator keeps no name table and no separate last-use array (either would not fit beside the code: 100K names). Its emitted lines are the code records themselves, 5 bytes each, written twice in place:
- SSA form, written by the tracer: a 2-bit opcode, two 17-bit node names and two "dies here" bits (38 bits). The dies bits are set by one backward pass over the records with a bitmap of one bit per name (12,561 bytes; the 256 output names are pre-marked, so an output is never freed).
- Register form, written by the forward allocation pass over the same records: a 3-bit opcode (the fifth value is the move), three 10-bit register fields (33 bits). The register of a name is read from the record of the line that defined it, which has already been rewritten when the name is used.

The allocator is linear: input plane k starts in register k, a dead value's register is reused (the lowest free register above 255 first, then the lowest free input register), an output plane takes its own register k when that register is free, and the output planes not in their register at the end are moved there (12 moves). It uses 866 registers, the peak number of live planes, so the file is not oversized. Its scratch (model `GEN_SCRATCH`) is the bitmap, a 4,096-slot cache of the materialised complements (5 bytes per slot), the plane values of the 64 schedule words and the 8 state words (4 bytes per plane), the 256 output ids, the free-register bitmaps and the permutation table: 46,612 bytes; the packed generator's scratch is the round-39 package's 22,528 bytes. The two are charged together: 69,140 bytes.
Layout. The setup phase holds 969,192 bytes: the main code (counted at its final size, 712,980 bytes; the sliced records are written in place and the packed records in the recovery region), the counters (28,672, including the 16,384-byte reserve of Section 7), the generators' code image (158,400) and their scratch (69,140). The register file is not in use during setup. The generators are never called after setup. In the search phase the same region holds the table (274,150 bytes), the register file (32,768) and the counters: main code + counters + register file + table = 1,048,570 bytes. The memory of the entry is the larger of the two, 1,048,570 bytes. The table size of Section 7 is the largest that fits after the reserve.
Measured: the C port of both generators (Appendix B; freestanding C, no libc, no allocation; the packed part is the round-39 package's C port with 64 steps and 64 constants) was compiled twice:
1. To WebAssembly (clang 17, `--target=wasm32 -O2 -nostdlib -ffreestanding -fno-builtin`, linked by wasm-ld with initial and maximum memory both 1,048,576 bytes = 16 pages and a 16 KiB stack) and run in Node.js 22. The module has 26,456 bytes and no imports; its memory section declares min = max = 16 pages, the guest memory is 1,048,576 bytes and a request to grow it by one page is refused. Its static data end at 723,396 bytes (the sliced records 501,120, the packed records 151,776, the two scratches 46,612 and 22,528, the constants) and the stack above them at 739,792. It emits the sliced list of 100,224 instructions with 866 registers and 12 moves from 120,311 tracer calls, and the packed list of 4,216 instructions with 68 registers from 6,017 calls; both lists (op, destination, operands, immediate), written one instruction per line, are identical to the Python generators' (`python3 shrho64.py --dump` and `--dump packed`): sha256 6bb7c2ac5a6b78de0fc9f027fd81cdba8426b03e9abf9966f092ad7d2ec75482 for the sliced list and 24479fba71703da23eaccde29488e9f5369bae54500e624c9c0247bba41a185e for the packed list, from all three sources.
2. Natively (clang, macOS), with the same two lists.

The generator charge of 400 word operations per tracer call and per emitted line (92,302,400) bounds its work: a tracer call does a constant number of comparisons, at most two probes of the complement cache and one 5-byte record write; the backward pass reads each record once; the allocator reads each record once, reads two registers from earlier records and scans at most 32 bitmap words per line; the final permutation touches 256 outputs. The whole setup row is 2^14.203 units, about 2^-110 of the time bound, so even a charge 1,000 times larger would not change time_log2 at 5 decimals. The Python generator's own resident set is the interpreter's and is not charged; it is the footprint of the interpreter, not of the machine model.

### 3.7 Preprocessing
None offline. The generators run inside every attempt and are charged in the setup row. The claim declares preprocessing_log2 = 14.21, the setup and generator row (2^14.203 units), which is also inside time_log2. The memory figure of Section 7 covers this preprocessing: the generators run in the setup phase of the same attempt, their code image and scratch are in the setup-phase total of Section 3.6 (969,192 bytes), and nothing they produce is stored outside the 1,048,570 bytes of the search phase. The prefix P is a constant written in the program (Section 1); `prefix_words()` reproduces it and is not part of the attempt.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values. The attempt uses the walk function only by evaluating f at points that the procedure chooses. Write A_F for the same procedure with every evaluation of f replaced by F (lazy sampling), and P_F for its success probability, taken over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. It is stated for this f, the 64-step map; by Lemma 0 it has the same colliding pairs as x -> digest(M(x)). The sub-claims under H1 (the numbers below are printed by `python3 shrho64.py --loss`) are computations for the random function F, with these approximations named as heuristic H2 (score-critical at this margin; not proved here):
- H2 (a): the age of the trail of one lane at the halt is dominated by an exponential with mean L, and the 256 ages are independent, although restarts depend on the history of the run.
- H2 (b): the number of cut trails is Poisson with the stated mean.
- H2 (c): the loss for a cut trail enters linearly with the stated slope.
- H2 (d): trail lengths are geometric with mean L (used for the colliding pairs inside trails).
- H2 (e): the birthday bound below is applied to the U points of the finished trails, a set that the walk selects adaptively, as for a fixed set of U uniform points (the standard treatment of distinguished-point collision search).

Lemma 1 (a statement about f itself, no premise). A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output. Both trails continue identically from f(x), so they end at the same DP with the same key, and the stored lengths let step 6 align and walk them. Step 6 returns the first merge pair, found within max(l1, l2) <= capr batches: a trail is cut at a slice check once its age is >= c, and slice checks are S batches apart, so every length is below c + S. The returned pair satisfies f(x) = f(y) with x != y, and the recovery checks equality before it returns; by Lemma 0 the two messages collide. The recovery evaluates f with the packed kernel and the main loop with the sliced kernel; both compute the same function f (Section 1 validation: both agree with the scalar compression and with the organizer verifier; the full-width experiment of Section 6 records their agreement in every trial), so the trails the recovery walks are the trails the search found.
The key determines F (F < 154 < 2^8, and the key holds its 8 low bits), so equal keys of two DPs differ only if their bits above 121 differ. The lanes do not interact: the generated straight line applies the same function to every lane, bit l of every plane (Section 3.2), so lane l holds f^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its bit of the OR is clear and the lane is examined. A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F, under H2). Let U be the number of evaluations on trails finished before the halt. The number of evaluations is Q = 256 B = 2^128.04637.
- *Unfinished trails.* For F the DP indicators of the successive points of one trail are independent with probability theta. So the age of one lane's trail at the halt (steps since its last restart) satisfies P(age >= a) <= (1 - theta)^a <= exp(-a / L), and (H2 a) the 256 ages are independent: each is stochastically dominated by an exponential with mean L. The sum of 256 such variables exceeds M L with probability at most exp(-256 (x - 1 - ln x)), x = M / 256 (Chernoff); for M = 350 this is 8.88e-07 <= 1e-6 (M = 349 gives 1.1e-6). So the 256 unfinished trails hold at most 350 L points, except with probability 1e-6. These 350 L points are 3.44 percent of Q (the price of 256 lanes with long trails; the budget B includes them, Appendix A).
- *Cut trails.* A cut trail costs at most c + S, that is 1.277e-03 Q. The number K of cut trails is (H2 b) Poisson with mean (Q / L) e^-13 = 10177.9 e^-13 = 0.02301: P(K = 0, 1, 2) = 0.97726, 0.02248, 0.00026, and P(K >= 3) = 2.0e-06; the third cut is a halt, charged as failure.
- *Cut-trail deficit.* The allowance 1.5e-4 Q already in U covers 0.117 of one cut trail. For K = 1 and K = 2 the remaining loss lowers the success probability by 6.82e-04 and 1.454e-03 (H2 c: slope of 1 - exp(-U^2/2N) at the target, 2 * 0.497 * e^-0.497 = 0.605 per unit of relative loss). K >= 3 is charged in full, P(K >= 3) itself, with no assumption that the halt is independent of success (a union bound). So the cut-trail deficit is 0.02248 * 6.82e-04 + 0.00026 * 1.454e-03 + 2.0e-06 = 1.77e-05.
- *Evaluations on finished trails.* Hence U >= (1 - 1.5e-4) Q - 350 L - 1 = 0.96546 Q = 2^127.9957 when K = 0 and the ages are within the bound.
- *Collision bound.* For U distinct inputs the probability of no colliding pair is prod (1 - i/N) <= exp(-U(U-1)/(2N)) <= exp(-0.497); the program's B is the least that gives U(U-1) >= 2 * 0.497 N.
- *Pairs inside trails.* The expected number of colliding pairs inside trails, summed over all trails, is at most Q L / N = 2^-13.22 = 1.05e-04 (H2 d: a trail of length l has at most l(l-1)/2 pairs, E[l^2] <= 2 L^2, and there are Q / L trails). This term is three times the round-39 package's because the trails are longer.
- *Key false matches.* The expected number of two different DP ends with the same 64-bit key is below 10,966^2 / 2 / 2^63.267 = 5.4e-12 (the key space is 2^56 * 154 = 2^63.267).

Programmed aborts:
- Table capacity: the number of finished trails is at most the number of DP events among the Q evaluations. That count is binomial with mean Q / L = 10177.9 (and no more than a Poisson count of the same mean in the Chernoff bound). The abort needs 10,967 or more, which has probability at most exp(-mean) (e mean / 10,967)^10,967 = 2^-43.0 = 1.1e-13 (Chernoff bound).
- Stage-1 budget: the number of stage-1 hits is at most binomial with mean mu2 = Q / 2^32 = 8.18e+28, and the abort needs 2 mu2 + 64. Its probability is at most e^(-mu2 (2 ln 2 - 1)) = e^(-3.2e+28).
- Recovery: a recovery that finds no pair needs a key false match or a start lying on another trail (at most 5.4e-12 + 2^-100).

The losses add to 1e-06 + 1.05e-04 + 1.77e-05 + 5.4e-12 + 1.1e-13 + 7.9e-31 = 1.235e-04. So P_F >= 1 - e^-0.497 - 1.235e-04 = 0.39152 >= 0.39; the 0.0015 left over is kept as margin. The kappa sweep (`plan(256, kappa)` for kappa = 9..16, Section 5) confirms the choice: 11 and 12 give P_F >= 0.39072 and 0.39146 with 0.0015 to 0.0031 bits less time; 13 keeps the margin of the round-39 package; 10 drops below 0.39.
If the real pair-collision rate is (1 - eps) of the model, P stays at least 0.39 for eps <= 0.0050 (the exact threshold is 0.00503). In general, at most 0.5 * log2(1/(1-eps)) more bits of time restore 0.39: 0.0072 for eps = 0.01, 0.037 for 0.05, 0.076 for 0.10 and 0.21 for 0.25.

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function f and about one attempt, and it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved. Its content, in the terms the ledger uses:
- (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists);
- (b) the iterates of f from the starts r + t have the first-collision law of a random mapping;
- (c) whether an iterate is a DP is independent of the collision events and has probability 154 / 2^122.

A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01). Subtracting the IV is a fixed bijection of the digest. The chosen prefix is one constant 20-byte string; its constant state after step 4 is the starting point of the 59 remaining steps of the same compression, and nothing in the search depends on its algebraic form. The sliced representation changes nothing about f: it is an implementation of the same 64-step compression on 256 inputs at once (Section 1 validation).
The two organizer experiments (Section 6) produce evidence that the program is right and that nothing gross is wrong. They are program checks: the organizer recomputes every returned pair and the counts of returned pairs are reported, but they are not used as estimates of any number of this entry. No quantitative inference is drawn from a count, no confidence interval is formed, and the entry does not rely on the independence of trials. The program also prints its own observations (`python3 shrho64.py --stats 256`, seeds from SHA-256 of a counter). They are untrusted and only descriptive:
    T3 n=18: attempts returning a verified pair: target 234 of 256, ideal function 116 of 128; cut trails 1186, restarts on a stored trail 95
    T2 width 256: 256 points, 14-bit projections, equal pairs per trial if uniform 1.9922, trials with a pair if uniform 0.8636; packed_agree 256 of 256
      source uniform (86 trials): returned pairs 71 (uniform reference 74.3); equal pairs (uniform reference 171.3 each): w0 174, w3 181, w7 157, xor8 172, sum8 184, p01 180, p23 166
      source counter (85 trials): returned pairs 72 (uniform reference 73.4); equal pairs (uniform reference 169.3 each): w0 155, w3 198, w7 169, xor8 178, sum8 178, p01 171, p23 173
      source iterates (85 trials): returned pairs 69 (uniform reference 73.4); equal pairs (uniform reference 169.3 each): w0 143, w3 173, w7 164, xor8 166, sum8 186, p01 158, p23 155
The width-18 success rate is high (about 0.9) because at that width the budget of 5 batches of 256 lanes evaluates 1,280 points of a space of 262,144, far past the birthday scale; the ideal control (run on the even trials) behaves the same way. The returned pairs of the width-256 experiment and the equal pairs in its seven projections are close to the uniform reference, and the packed recovery kernel agreed with the sliced kernel in every trial. The selftest output (`python3 shrho64.py --selftest`):
    sliced kernel, 64 steps: 100212 operations {'^': 79072, '|': 13813, '&': 6036, '~': 1291} + 12 moves, 866 registers; generator calls 120311; dead lines 0; peak live 866
    prefix equals prefix_words() (A0 = A1 = A3 = A4 = 0, E3 = E4 = 0 after step 4): True
    1024 lanes (lanes 0, 1 all-zero, all-one), full 256-bit f: allocated code on a register file = compiled = scalar f: True
    whole batch of all-zero / all-one inputs: True  (twice)
    3 chained batches (output planes are the next input planes): True
    packed 64-step kernel (recovery): 4216 operations {'+': 531, '>>': 609, '&': 1401, '<<': 522, '|': 522, '^': 631}, 68 registers; 308 lanes vs scalar f and the allocated code: True
    recovery form f2 (5 values in one packed evaluation) vs scalar: True
    stage-1 test on planes, lane extraction and insertion: True
    n=18 chain, 3 steps, 256 lanes: True
    search n=18 (5 batches of 256 lanes per attempt): 14 of 16 attempts returned a verified pair; 105 cut trails, 11 restarts on a start lying on a stored trail
    selftest True
Local runs of the two declared experiments through the organizer's own executor (`experiments.run_experiments` of the benchmark repository, the pinned Docker image python:3.12.12-slim-bookworm@sha256:2986c55f..., one CPU, 128 MiB, no network, 20-second timeout, each request run twice in fresh containers and compared byte for byte), at 8 trials and at the organizer's default of 256 trials: every returned pair was recomputed by the executor on the complete 64-step digests of the full padded messages and checked against the declared mask. Counts are in Section 6. These are this entry's runs of the organizer's executor, not organizer runs, and are reported without inference.
Not tested: the full 256-bit functional graph, iterations of length above 2^40, and the search above width 18 with 256 lanes (the round-39 package's toy run at width 40 used its 7-lane program). A deviation that lowers the pair-collision rate by eps costs the table of Section 4. Other structured deviations, such as unusually many short cycles inside trails or starts landing on other trails, would add failures that the model does not price; nothing in the runs above indicates them, but those runs are far below width 256.

## 6. Experiments

Two organizer experiments are declared; the organizer's executor runs the shipped program `experiments/shrho64.py` (no organizer result exists yet for this package). The program dispatches on the experiment id; no outside code or library is used, only the standard library. In the sandbox one batch of the sliced kernel (100,224 big-integer operations in CPython 3.12) costs about 8 milliseconds once the allocated code has been compiled to Python functions (0.7 s at start); the search experiment therefore runs 5 batches per trial and the ideal control on every second trial, and the lane handlers at reduced width touch only the planes of the n low bits. Measured in the pinned image on one emulated amd64 CPU: 256 trials of `sliced-n18` in 10.5 s and of `sliced-k0-w256` in 12.9 s, container start included, inside the executor's 20 seconds.
`sliced-n18`: per trial, from the trial seed, one attempt of the 256-lane search at width n = 18 (DP = low bit zero, plan(18): 5 batches of 256 lanes, age cap 4 batches checked after every batch, table, recovery with the packed kernel) on the target chain f, which is the low 18 bits of the digest minus the IV of the 52-byte message M(x) = P || x with x < 2^18 (x sits in W12 and W5..W11 are 0, so this is a different function from the width-256 walk; the experiment checks the program, not the full-width function). The trial returns the two 52-byte messages M(x), M(y) when the attempt succeeded and two nulls otherwise. The checked event is that the complete 64-step digests agree in the low 18 bits and the messages are distinct. This is implied by the walk at width 18: the low 18 bits of digest word 7 are those of IV[7] + f_7. Two rules differ from the width-256 program and are stated in the manifest: a key match whose recovery finds no pair (the start of one trail lies on the other trail; the expected number of such events per attempt is about Q^2 / (L N), several at this width and 2^-100 at width 256) restarts the lane instead of halting the attempt and is counted (observation target_robin); and there is no cap on cut trails. Untrusted observations: the attempt's counts, and on the even trials the same attempt on an ideal function of the same width (keyed blake2b; ideal_ok = -1 on the odd trials).
`sliced-k0-w256`: per trial, 256 points of the target at full width 256 evaluated as one batch of the sliced kernel. The source is chosen by trial index mod 3: uniform inputs from the seed, counter inputs r + i, or 128 seed-derived starts and their images under f. The trial returns two distinct points whose f values agree in the low 14 bits when the set contains such a pair, and two nulls otherwise. The checked event is that the complete digests agree in the low 14 bits and the messages are distinct, which is equivalent by the same argument. Untrusted observations: the numbers of equal pairs in seven 14-bit projections of f, and packed_agree = 1 when the packed recovery kernel gives the same f on the first 7 lanes of the batch.
They check the sliced kernel at full width, the planes (transposition, stage-1 test, lane extraction and insertion), the table, the recovery with the packed kernel and the message construction on the real target. They do not measure the cost or the success probability at width 256. At reduced width the plan also uses other halt rules (no cap on cut trails, table capacity 4 Q / L + 64, the restart rule above), so the experiments do not exercise the width-256 halts.
Runs through the organizer's executor (Section 5): at 8 trials, `sliced-n18` returned 5 pairs and `sliced-k0-w256` 8, all checked. At the organizer's default of 256 trials (report sha256 4c9d713012675512672a46f83d1c023d68022b1dfd20b9badefe45c64a0a97c7; 51 s of wall time for the four container runs on this machine), `sliced-n18` completed with 229 of 256 trials returning a checked pair (24 of them pairs already returned by an earlier trial, which the executor marks as repeated; the untrusted observations it recorded: the ideal control succeeded on 115 of its 128 trials, 1,359 cut trails, 97 restarts of a lane whose start lay on a stored trail), and `sliced-k0-w256` completed with 221 of 256 trials returning a checked pair (no repeated pair; packed_agree 256 of 256; 492 equal pairs in the low 14 bits over the 256 trials, uniform reference 510). Every returned pair passed the executor's check of the declared mask on the complete 64-step digests of the full padded messages; none was a full collision.

## 7. Memory

Table: 10,966 entries * 25 bytes = 274,150 bytes (the table region is empty until the search starts). An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: 712,980 bytes (Section 3.3): the main loop body, 100,260 instructions of 5 bytes (501,300); the recovery kernel with its test, 4,280 instructions of 36 bytes (154,080); the handlers, key scan, cut, slice and setup, 1,600 instructions of 36 bytes (57,600).
Register file: 1,024 words of 256 bits, counted as memory: 32,768 bytes.
Counters and copies: 28,672 bytes. This covers the 256 trail numbers (2 bytes each) and births (15 bytes each), the counters and the lane arrays used by the handlers (about 6,400 bytes in all), a reserve of 4,096 bytes for the stack, alignment and anything not itemised, and a reserve of 16,384 bytes against the handler-code estimate (1,600 instructions charged; the reserve holds 455 more instructions of 36 bytes). The reserve costs 0.0001 bit of time (a smaller table). No advice.
Memory peak = max(setup phase 969,192, search phase 1,048,570) = 1,048,570 bytes <= 2^20 = 1,048,576; the 16,384-byte reserve is inside this total. The peak is the search phase; the preprocessing runs inside the smaller setup phase (Section 3.6). Claim `memory_log2_bytes` = 20, so max(0, memory_log2_bytes - 20) = 0 and the scalar score equals time_log2. `python3 shrho64.py --ledger` prints both phases.
The table size is the largest that fits: tmax = floor((2^20 - 712,980 - 32,768 - 28,672) / 25) = 10,966. Tp = 154 is the largest integer for which the table-capacity bound of Section 4 stays below 2^-40 (Appendix A computes both). With the 4-byte encoding of the body the table would hold 14,976 entries and Tp would be 215 (Section 3.5).

## 8. Heuristics, conventions and what is credited

The premises of this entry:
- H1, the model premise of Section 4 (score-critical), the round-39 package's, stated for the 64-step f.
- H2, the named approximations (a) to (e) of Lemma 2 (score-critical at this margin: the success bound depends on them), with M = 350 for the 256 unfinished trails.
- H3, the machine convention of Section 3.1: 1024 registers of 256 bits counted as memory, 5-byte register-to-register instructions for the main loop body and 36-byte instructions elsewhere, one word operation = one operation whatever the word holds (score-critical: time_log2 depends on it). H3 is a declared convention priced in Section 3.5, not a statistical premise; the success argument does not depend on it. It differs from the round-39 package's H3 (64 registers, 36-byte instructions, 7 lanes of 36 bits), and Section 3.5 states what the entry is worth under that convention: nothing, because the sliced kernel then loses to the packed one.

There is no advice and no polarity climb; the entry has no two-block mode. The constant message prefix P is part of the program, not advice.
What is credited: to the accepted sha256 round-39 package and, through it, to 368d1718 (Jbenisek), 01e31be9, the blake3 round-3 entries 0a9640ed, 3356413f, cf8b0e92 (packed lanes), 62cfd777 and e479cbbf: the message family and the walk on the digest minus the IV (Lemma 0), the closed-form prefix, the CH/MAJ folding, the trail-and-table search with distinguished points, the handlers, the recovery walk, the packed-lane kernel generator and its allocator and C port (here the recovery kernel), the ledger method with its halts and charges, the success argument with the union-bound charge of the third cut and the age cap 13 L, the two experiments and their checks, and the memory reserve.
What this entry adds: the bit-sliced kernel of 256 lanes (the plane algebra with constant folding and polarity tracking, the full-adder and carry-save additions, the shared-XOR majority, the folded round constants, the relabeled rotations); its generator and its linear register allocator with the in-place 5-byte records; the C port of that generator in the same 1 MiB; the stage-1 test on planes, the handlers for 256 lanes and their charges; the ledger with 256 lanes (M = 350), the register-file charge and the two instruction sizes; the trade-off curve of Section 3.5 and the comparison with the packed kernel at 64 steps; the experiments at 256 lanes (and their reduced-width restart rule); and every number of this document, recomputed by the program.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 shrho64.py --ledger`. It is the round-39 package's Appendix A with the sliced constants: 256 lanes, the kernel count 100,212 plus 12 moves, the stage-1 test 33, the handler charges 600 / 3,000 / 3,000 / 1,040, the two generators' calls and lines, the packed recovery kernel 4,216, the 5-byte body instructions, the 1,024-word register file, the 28,672 bytes of counters and C = 4912. To price the packed 64-step package instead (Section 3.5), set PH, MOVES, FILT, LANES = 4216, 0, 4, 7, GEN_CALLS, GEN_LINES = 6017, 4216, HIT, EVENT, CUTOPS, SLICE = 400, 800, 800, 120, SETUP_FIXED = 7 * 400 + 2000, INSTR_MAIN = 36, OTHER_CODE = 600, REGFILE = 64 * 32 and COUNTERS = 22528: it prints time_log2 = 124.97721.

```python
from fractions import Fraction
from math import isqrt, log, exp, log2

PH, MOVES, FILT, LOOP, LANES = 100212, 12, 33, 3, 256     # operations of the sliced step (generator), output moves, stage-1 test, loop control, lanes
GEN_CALLS, GEN_LINES = 120311 + 6017, 100212 + 4216      # generator calls and emitted lines of the sliced and the packed generator (python3 shrho64.py --ledger)
PR, EXTRA = 4216, 64                                      # the packed recovery kernel and the extra operations per recovery batch
N_BITS, S1, W, KAPPA = 256, 32, 90, 13                    # width, stage-1 bits, window bits (D = 122), age cap in units of L
LAM, CUT = Fraction(497, 1000), Fraction(15, 100000)
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 600, 3000, 3000, 1040, 400
SETUP_FIXED, CMAX = 256 * 1400 + 2000, 2
INSTR_MAIN, INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE = 5, 36, 1600, 1024 * 32, 28672, 25, 0
TAIL_AGES = 1e-6


def inflight_m(lanes=LANES, eps=TAIL_AGES):    # smallest M with P(sum of `lanes` exponential ages > M L) <= eps (Chernoff, exact in the exponent)
    m = lanes
    while True:
        x = m / lanes
        if exp(-lanes * (x - 1 - log(x))) <= eps:
            return m
        m += 1


M = inflight_m()
body = PH + MOVES + FILT + LOOP                                # one batch = one loop body = 100,260 operations
code_bytes = body * INSTR_MAIN + (PR + EXTRA + OTHER_CODE) * INSTR    # main body at 5 bytes; recovery kernel and handlers at 36 bytes
tmax = ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY    # table entries that fit in 2^20 bytes with the code and the register file
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
gen = GEN_FACTOR * (GEN_CALLS + GEN_LINES)
rows = [("main loop: B * 100260", body * B),
        ("slice checks: ceil(B / 2^48) * 1040", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 600", e2max * HIT),
        ("finished trails: (tmax + 1) * (3000 + 3 * tmax)", (tmax + 1) * (EVENT + 3 * tmax)),
        ("cut trails: 2 * 3000", CMAX * CUTOPS),
        ("recovery: (c + 2^48 + 1) * (4216 + 64) + 600", (capr + 1) * (PR + EXTRA) + 600),
        ("setup and generators", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("M =", M, " Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("code bytes =", code_bytes, " memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
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
M = 350  Tp = 154  tmax = 10966  B = 1372642907409490479844181200006684859  e2max = 163631785799204168301127100055  c = 448830232342958606435051734640116351
code bytes = 712980  memory bytes = 1048570
main loop: B * 100260                                137621177896875515509177607112670223963340
slice checks: ceil(B / 2^48) * 1040                  5071671522592673749720320
stage-1 hits: e2max * 600                            98179071479522500980676260033000
finished trails: (tmax + 1) * (3000 + 3 * tmax)      393693366
cut trails: 2 * 3000                                 6000
recovery: (c + 2^48 + 1) * (4216 + 64) + 600         1920993394427862835543226137160019594840
setup and generators                                 92662800
N = 139542171389482454895914856823180739673666
certificate: 2^12441765 * 4912^100000 <= N^100000 < 2^12441766 * 4912^100000
log2(N/C) = 124.4176582334
time_log2 = 124.41766
```

## Appendix B. The C port of the two generators

Freestanding C (no libc, no allocation, no imports); part A is the sliced generator of Section 3.6, part B the round-39 package's packed generator at 64 steps. Built and run as described in Section 3.6; both instruction lists are identical to the Python generators' (sha256 6bb7c2ac...5482 and 24479fba...185e). The `#ifdef NATIVE` tail is the native harness only (it uses stdio); the WebAssembly build excludes it.

```c
/* Freestanding C port of the two circuit generators of shrho64.py (sha256-r64 bit-sliced candidate).
   No libc, no malloc, no imports.  Exports: run_sliced(), run_packed(), info_ptr(), sliced_ptr(), packed_ptr().
   Part A: the sliced generator (Tracer / build_sliced / Kernel.allocate): emits 5-byte records into `sliced`, in SSA form
   (op 2 bits, a 17 bits, b 17 bits, dies_a, dies_b = 38 bits), then rewrites each record in place into register form
   (op 3 bits, dst 10, a 10, b 10 = 33 bits); the 12 output moves are appended.  The allocator reads reg[name] from the
   rewritten record of the line that defined the name, so no separate name table exists.
   Part B: the packed generator (PTracer / build_packed / allocate_packed) of the accepted 39-round package at ROUNDS = 64:
   36-byte records into `packed` (op, dst, a, b as u16, b-is-immediate flag, 32-bit immediate, zero padding).
   Static memory: sliced 501,120 B (100,224 records), packed 151,776 B (4,216 records), scratch (see info). */
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;

#define ROUNDS 64
#define M32 0xFFFFFFFFull
#define SL_MAX 100224          /* sliced lines + output moves */
#define SL_REC 5
#define NAMES (SL_MAX + 257)   /* node ids: 1..256 inputs, 257.. lines */
#define HASHN 4096             /* complement cache: open addressing, key/value 17-bit names, 5 bytes per slot */
#define PK_MAX 4216
#define PK_REC 36
#define LIM36 (1ull << 36)

static u8 sliced[SL_MAX * SL_REC];
static u8 packed[PK_MAX * PK_REC];
static struct {                                   /* the sliced generator's scratch */
  u8 bits[(NAMES + 7) / 8];                       /* backward pass: seen; forward pass: is-output */
  u8 hash[HASHN * 5];                             /* complement cache */
  u32 W[ROUNDS][32]; u32 st[8][32]; u32 bc[32];   /* plane values: bit 31 = variable, bits 0..16 = node or constant bit, bit 17 = neg */
  u32 outs[256];                                  /* output node ids */
  u32 freelo[8]; u32 freehi[24];                  /* free-register bitmaps (0..255, 256..1023) */
  u16 where[1024];                                /* final permutation: register -> output index + 1, or 0 */
} S;
static struct { u32 ninst, nreg, calls, moves, err, nots, sz_sliced, sz_packed, sz_scratch, sz_pk_scratch; } info;

static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u32 K[64] = {
0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,
0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,
0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,
0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u};
static const u32 PREFIX_W[5] = {0x03f777b3u, 0xeec88896u, 0xe8ebdb1cu, 0x1b70c247u, 0x177c95e3u};
static const u32 TAIL_W[3] = {0x80000000u, 0, 0x1A0u};

#ifdef __wasm__
#define EXPORT(n) __attribute__((export_name(n)))
#else
#define EXPORT(n)
#endif
EXPORT("info_ptr") u32 info_ptr(void) { return (u32)(unsigned long)&info; }
EXPORT("sliced_ptr") u32 sliced_ptr(void) { return (u32)(unsigned long)sliced; }
EXPORT("packed_ptr") u32 packed_ptr(void) { return (u32)(unsigned long)packed; }

/* ================================================================ Part A: the sliced generator */
/* plane value encoding: constant: bit 0 = the bit, bit 31 = 0.  variable: bit 31 = 1, bits 0..16 = node, bit 17 = neg. */
#define ISV(x) ((x) >> 31)
#define NODE(x) ((x) & 0x1FFFFu)
#define NEG(x) (((x) >> 17) & 1u)
#define CST(b) ((u32)(b))
#define VAR(n, neg) (0x80000000u | (u32)(n) | ((u32)(neg) << 17))
static inline u32 NOTV(u32 x) { return ISV(x) ? (x ^ 0x20000u) : (x ^ 1u); }
static u32 nin, nname, calls, err;

static u32 emit(u32 op, u32 a, u32 b) {          /* op 0 '^', 1 '&', 2 '|', 3 '~' (b unused: stored as 0) */
  if (nin >= SL_MAX) { err = 1; return 0; }
  u64 r = (u64)op | ((u64)a << 2) | ((u64)b << 19);  /* dies bits (37, 38) are set by the backward pass */
  u8 *p = sliced + (u32)SL_REC * nin;
  p[0] = (u8)r; p[1] = (u8)(r >> 8); p[2] = (u8)(r >> 16); p[3] = (u8)(r >> 24); p[4] = (u8)(r >> 32);
  nin++;
  return ++nname;
}
/* complement cache: node -> node */
static u32 hslot(u32 k) { return (k * 2654435761u) >> 20; }   /* 12-bit slot */
static int hget(u32 key, u32 *val) {
  u32 s = hslot(key) & (HASHN - 1);
  for (;;) {
    u8 *e = S.hash + 5 * s;
    u64 v = (u64)e[0] | ((u64)e[1] << 8) | ((u64)e[2] << 16) | ((u64)e[3] << 24) | ((u64)e[4] << 32);
    if (v == 0) return 0;
    if ((u32)(v & 0x1FFFF) == key) { *val = (u32)((v >> 17) & 0x1FFFF); return 1; }
    s = (s + 1) & (HASHN - 1);
  }
}
static void hput(u32 key, u32 val) {
  u32 s = hslot(key) & (HASHN - 1);
  for (;;) {
    u8 *e = S.hash + 5 * s;
    if ((e[0] | e[1] | e[2] | e[3] | e[4]) == 0) {
      u64 v = (u64)key | ((u64)val << 17) | (1ull << 34);
      e[0] = (u8)v; e[1] = (u8)(v >> 8); e[2] = (u8)(v >> 16); e[3] = (u8)(v >> 24); e[4] = (u8)(v >> 32);
      return;
    }
    s = (s + 1) & (HASHN - 1);
  }
}
static int hasnot(u32 n) { u32 v; return hget(n, &v); }
static u32 notnode(u32 a) {
  u32 v;
  if (hget(a, &v)) return v;
  u32 n = emit(3, a, 0);
  info.nots++;
  hput(a, n); hput(n, a);
  return n;
}
static u32 xorv(u32 x, u32 y) {
  calls++;
  if (!ISV(x) && !ISV(y)) return CST((x ^ y) & 1);
  if (!ISV(x)) { u32 t = x; x = y; y = t; }
  if (!ISV(y)) return (y & 1) ? NOTV(x) : x;
  if (NODE(x) == NODE(y)) return CST(NEG(x) != NEG(y));
  return VAR(emit(0, NODE(x), NODE(y)), NEG(x) ^ NEG(y));
}
static u32 andv(u32 x, u32 y) {
  calls++;
  if (!ISV(x) && !ISV(y)) return CST(x & y & 1);
  if (!ISV(x)) { u32 t = x; x = y; y = t; }
  if (!ISV(y)) return (y & 1) ? x : CST(0);
  if (NODE(x) == NODE(y)) return NEG(x) == NEG(y) ? x : CST(0);
  if (!NEG(x) && !NEG(y)) return VAR(emit(1, NODE(x), NODE(y)), 0);
  if (NEG(x) && NEG(y)) return VAR(emit(2, NODE(x), NODE(y)), 1);
  if (!NEG(x)) { u32 t = x; x = y; y = t; }
  if (hasnot(NODE(x)) || !hasnot(NODE(y))) { u32 nx = notnode(NODE(x)); return VAR(emit(1, nx, NODE(y)), 0); }
  { u32 ny = notnode(NODE(y)); return VAR(emit(2, NODE(x), ny), 1); }
}
static u32 orv(u32 x, u32 y) {
  calls++;
  if (!ISV(x) && !ISV(y)) return CST((x | y) & 1);
  if (!ISV(x)) { u32 t = x; x = y; y = t; }
  if (!ISV(y)) return (y & 1) ? CST(1) : x;
  if (NODE(x) == NODE(y)) return NEG(x) == NEG(y) ? x : CST(1);
  if (!NEG(x) && !NEG(y)) return VAR(emit(2, NODE(x), NODE(y)), 0);
  if (NEG(x) && NEG(y)) return VAR(emit(1, NODE(x), NODE(y)), 1);
  if (!NEG(x)) { u32 t = x; x = y; y = t; }
  if (hasnot(NODE(x)) || !hasnot(NODE(y))) { u32 nx = notnode(NODE(x)); return VAR(emit(2, nx, NODE(y)), 0); }
  { u32 ny = notnode(NODE(y)); return VAR(emit(1, NODE(x), ny), 1); }
}
static u32 xor3(u32 x, u32 y, u32 z) { return xorv(xorv(x, y), z); }
#define POS(v) VAR(NODE(v), 0)

static u32 maj(u32 x, u32 y, u32 z, u32 xy, int have_xy) {
  calls++;
  u32 vs[3]; int nv = 0, k = 0;
  u32 in[3] = {x, y, z};
  for (int i = 0; i < 3; i++) { if (ISV(in[i])) vs[nv++] = in[i]; else k += in[i] & 1; }
  if (nv < 3) {
    if (nv == 0) return CST(k >= 2);
    if (nv == 1) return k == 1 ? vs[0] : CST(k == 2);
    return k == 0 ? andv(vs[0], vs[1]) : orv(vs[0], vs[1]);
  }
  { const u32 tr[3][3] = {{x, y, z}, {x, z, y}, {y, z, x}};
    for (int i = 0; i < 3; i++) { u32 u = tr[i][0], v = tr[i][1], w = tr[i][2]; if (NODE(u) == NODE(v)) return NEG(u) == NEG(v) ? u : w; } }
  u32 negs[3], poss[3]; int nn = 0, np = 0;
  for (int i = 0; i < 3; i++) { if (NEG(in[i])) negs[nn++] = in[i]; else poss[np++] = in[i]; }
  if (nn == 0) {
    u32 a = x, b = y, c = z;
    u32 ab = have_xy ? xy : xorv(a, b);
    u32 ac = xorv(a, c); u32 an = andv(ab, ac);
    return xorv(a, an);
  }
  if (nn == 1) {
    u32 p = POS(negs[0]), y1 = poss[0], z1 = poss[1];
    u32 py = xorv(p, y1); u32 pz = xorv(p, z1); u32 o = orv(py, pz);
    return xorv(p, o);
  }
  if (nn == 2) {
    u32 p = POS(negs[0]), q = POS(negs[1]), z1 = poss[0];
    u32 zp = xorv(z1, p); u32 zq = xorv(z1, q); u32 o = orv(zp, zq);
    return NOTV(xorv(z1, o));
  }
  { u32 p = POS(negs[0]), q = POS(negs[1]), r = POS(negs[2]);
    u32 pq = xorv(p, q); u32 pr = xorv(p, r); u32 an = andv(pq, pr);
    return NOTV(xorv(p, an)); }
}
static void fa(u32 x, u32 y, u32 z, u32 *sum, u32 *carry) {
  calls++;
  u32 vs[3]; int nv = 0, k = 0;
  u32 in[3] = {x, y, z};
  for (int i = 0; i < 3; i++) { if (ISV(in[i])) vs[nv++] = in[i]; else k += in[i] & 1; }
  if (nv < 3) {
    if (nv == 0) { *sum = CST(k & 1); *carry = CST(k >> 1); return; }
    if (nv == 1) { u32 p = vs[0]; if (k == 0) { *sum = p; *carry = CST(0); } else if (k == 1) { *sum = NOTV(p); *carry = p; } else { *sum = p; *carry = CST(1); } return; }
    { u32 p = vs[0], q = vs[1]; u32 s = xorv(p, q);
      if (k == 0) { *sum = s; *carry = andv(p, q); } else { *sum = NOTV(s); *carry = orv(p, q); } return; }
  }
  { const u32 tr[3][3] = {{x, y, z}, {x, z, y}, {y, z, x}};
    for (int i = 0; i < 3; i++) { u32 u = tr[i][0], v = tr[i][1], w = tr[i][2];
      if (NODE(u) == NODE(v)) { *sum = xor3(u, v, w); *carry = NEG(u) == NEG(v) ? u : w; return; } } }
  u32 negs[3], poss[3]; int nn = 0, np = 0;
  for (int i = 0; i < 3; i++) { if (NEG(in[i])) negs[nn++] = in[i]; else poss[np++] = in[i]; }
  if (nn == 0) {
    u32 a = x, b = y, c = z;
    u32 ab = xorv(a, b);
    *sum = xorv(ab, c);
    { u32 ac = xorv(a, c); u32 an = andv(ab, ac); *carry = xorv(a, an); }
    return;
  }
  if (nn == 1) {
    u32 p = POS(negs[0]), y1 = poss[0], z1 = poss[1];
    u32 u1 = xorv(p, y1);
    { u32 pz = xorv(p, z1); u32 o = orv(u1, pz); *carry = xorv(p, o); }
    *sum = NOTV(xorv(u1, z1));
    return;
  }
  if (nn == 2) {
    u32 p = POS(negs[0]), q = POS(negs[1]), z1 = poss[0];
    u32 u1 = xorv(z1, p);
    { u32 zq = xorv(z1, q); u32 o = orv(u1, zq); *carry = NOTV(xorv(z1, o)); }
    *sum = xorv(u1, q);
    return;
  }
  { u32 p = POS(negs[0]), q = POS(negs[1]), r = POS(negs[2]);
    u32 pq = xorv(p, q);
    *sum = NOTV(xorv(pq, r));
    { u32 pr = xorv(p, r); u32 an = andv(pq, pr); *carry = NOTV(xorv(p, an)); } }
}
static u32 ch(u32 e, u32 f, u32 g) {
  calls++;
  u32 d = xorv(f, g);
  if (!ISV(d)) return (d & 1) == 0 ? g : xorv(g, e);
  if (!ISV(e)) return (e & 1) ? f : g;
  if (NEG(e) == NEG(d)) { u32 an = andv(e, d); return xorv(g, an); }
  { u32 an = andv(NOTV(e), d); return xorv(f, an); }
}
/* words: u32 w[32] */
static void cword(u32 c, u32 *w) { for (int j = 0; j < 32; j++) w[j] = CST((c >> j) & 1); }
static int is_cword(const u32 *w) { for (int j = 0; j < 32; j++) if (ISV(w[j])) return 0; return 1; }
static u32 cval(const u32 *w) { u32 c = 0; for (int j = 0; j < 32; j++) c |= (w[j] & 1) << j; return c; }
static void copyw(const u32 *s, u32 *d) { for (int j = 0; j < 32; j++) d[j] = s[j]; }
/* xor of three rotated/shifted copies: sel = 0 Sigma (3 rotations), 1 sigma (2 rotations, 1 shift) */
static void sig(const u32 *w, int r1, int r2, int r3, int shift3, u32 *out) {
  for (int j = 0; j < 32; j++) {
    u32 a = w[(j + r1) % 32], b = w[(j + r2) % 32];
    u32 c = shift3 ? (j + r3 < 32 ? w[j + r3] : CST(0)) : w[(j + r3) % 32];
    out[j] = xorv(xorv(a, b), c);
  }
}
static void xorw(const u32 *a, const u32 *b, u32 *out) { for (int j = 0; j < 32; j++) out[j] = xorv(a[j], b[j]); }
static void chw(const u32 *e, const u32 *f, const u32 *g, u32 *out) { for (int j = 0; j < 32; j++) out[j] = ch(e[j], f[j], g[j]); }
static void majw(const u32 *a, const u32 *b, const u32 *c, const u32 *ab, const u32 *bc, u32 *out) {
  for (int j = 0; j < 32; j++) {
    u32 x = a[j], y = b[j], z = c[j], p = ab[j], q = bc[j];
    int anyc = !ISV(x) || !ISV(y) || !ISV(z);
    int distinct = ISV(x) && ISV(y) && ISV(z) && NODE(x) != NODE(y) && NODE(x) != NODE(z) && NODE(y) != NODE(z);
    if (anyc || !distinct) out[j] = maj(x, y, z, p, 1);
    else if (!ISV(p) || !ISV(q) || NEG(p) == NEG(q)) { u32 an = andv(p, q); out[j] = xorv(y, an); }
    else { u32 r = xorv(p, q); if (NEG(p) == NEG(r)) { u32 an = andv(p, r); out[j] = xorv(x, an); } else { u32 an = andv(r, q); out[j] = xorv(z, an); } }
  }
}
static void add2w(const u32 *x, const u32 *y, u32 *out) {
  u32 c = CST(0);
  for (int j = 0; j < 32; j++) { if (j < 31) fa(x[j], y[j], c, &out[j], &c); else out[j] = xor3(x[j], y[j], c); }
}
static void csaw(const u32 *x, const u32 *y, const u32 *z, u32 *s, u32 *c) {
  u32 cc[32]; cc[0] = CST(0);
  for (int j = 0; j < 32; j++) { if (j < 31) fa(x[j], y[j], z[j], &s[j], &cc[j + 1]); else s[j] = xor3(x[j], y[j], z[j]); }
  copyw(cc, c);
}
static void add_many(int n, u32 (*words)[32], u32 *out) {
  u32 vs[6][32]; int nv = 0; u32 k = 0;
  for (int i = 0; i < n; i++) { if (is_cword(words[i])) k += cval(words[i]); else copyw(words[i], vs[nv++]); }
  if (nv == 0) { cword(k, out); return; }
  if (k) cword(k, vs[nv++]);
  while (nv > 2) {
    u32 s[32], c[32];
    csaw(vs[0], vs[1], vs[2], s, c);
    copyw(s, vs[0]); copyw(c, vs[1]);
    for (int i = 3; i < nv; i++) copyw(vs[i], vs[i - 1]);
    nv--;
  }
  if (nv == 2) add2w(vs[0], vs[1], out); else copyw(vs[0], out);
}

static void build_sliced(void) {
  u32 (*W)[32] = S.W;
  for (int i = 0; i < 5; i++) cword(PREFIX_W[i], W[i]);
  for (int i = 5; i < 13; i++) for (int j = 0; j < 32; j++) W[i][j] = VAR(32 * (i - 5) + j + 1, 0);
  for (int i = 13; i < 16; i++) cword(TAIL_W[i - 13], W[i]);
  nname = 256;
  u32 *a = S.st[0], *b = S.st[1], *c = S.st[2], *d = S.st[3], *e = S.st[4], *f = S.st[5], *g = S.st[6], *h = S.st[7];
  for (int i = 0; i < 8; i++) cword(IV[i], S.st[i]);
  xorw(b, c, S.bc);
  for (int i = 0; i < ROUNDS; i++) {
    if (i >= 16) {
      u32 ops[4][32];
      sig(W[i - 15], 7, 18, 3, 1, ops[1]);
      sig(W[i - 2], 17, 19, 10, 1, ops[3]);
      copyw(W[i - 16], ops[0]); copyw(W[i - 7], ops[2]);
      add_many(4, ops, W[i]);
    }
    u32 s1[32], chv[32], t1[32], s0[32], ab[32], mj[32], na[32], ne[32];
    sig(e, 6, 11, 25, 0, s1);
    chw(e, f, g, chv);
    { u32 ops[5][32]; copyw(h, ops[0]); copyw(s1, ops[1]); copyw(chv, ops[2]); cword(K[i], ops[3]); copyw(W[i], ops[4]); add_many(5, ops, t1); }
    sig(a, 2, 13, 22, 0, s0);
    xorw(a, b, ab);
    majw(a, b, c, ab, S.bc, mj);
    copyw(ab, S.bc);
    { u32 ops[3][32]; copyw(t1, ops[0]); copyw(s0, ops[1]); copyw(mj, ops[2]); add_many(3, ops, na); }
    { u32 ops[2][32]; copyw(d, ops[0]); copyw(t1, ops[1]); add_many(2, ops, ne); }
    /* rotate the state: a, b, c, d, e, f, g, h = na, a, b, c, ne, e, f, g */
    copyw(g, h); copyw(f, g); copyw(e, f); copyw(ne, e); copyw(c, d); copyw(b, c); copyw(a, b); copyw(na, a);
  }
  for (int i = 0; i < 8; i++) for (int j = 0; j < 32; j++) {
    u32 p = S.st[i][j];
    if (!ISV(p)) { err = 2; return; }
    S.outs[32 * i + j] = NEG(p) ? notnode(NODE(p)) : NODE(p);
  }
}

static inline u64 rd5(const u8 *p) { return (u64)p[0] | ((u64)p[1] << 8) | ((u64)p[2] << 16) | ((u64)p[3] << 24) | ((u64)p[4] << 32); }
static inline void wr5(u8 *p, u64 r) { p[0] = (u8)r; p[1] = (u8)(r >> 8); p[2] = (u8)(r >> 16); p[3] = (u8)(r >> 24); p[4] = (u8)(r >> 32); }
static inline int bit(const u8 *m, u32 i) { return (m[i >> 3] >> (i & 7)) & 1; }
static inline void setbit(u8 *m, u32 i) { m[i >> 3] |= (u8)(1 << (i & 7)); }
static int lowest(const u32 *m, int words) { for (int w = 0; w < words; w++) if (m[w]) return 32 * w + __builtin_ctz(m[w]); return -1; }
static u32 regof(u32 name) { return name <= 256 ? name - 1 : (u32)((rd5(sliced + (u64)SL_REC * (name - 257)) >> 3) & 0x3FF); }

EXPORT("run_sliced") int run_sliced(void) {
  err = 0; nin = 0; calls = 0; info.nots = 0;
  for (u32 i = 0; i < sizeof S.hash; i++) S.hash[i] = 0;
  for (u32 i = 0; i < sizeof S.bits; i++) S.bits[i] = 0;
  build_sliced();
  info.calls = calls;
  if (err) { info.err = err; return err; }
  /* backward pass: dies bits (an output never dies) */
  for (int k = 0; k < 256; k++) setbit(S.bits, S.outs[k]);
  for (u32 k = nin; k-- > 0;) {
    u8 *p = sliced + (u64)SL_REC * k;
    u64 r = rd5(p);
    u32 op = (u32)(r & 3), a = (u32)((r >> 2) & 0x1FFFF), b = (u32)((r >> 19) & 0x1FFFF);
    if (!bit(S.bits, a)) { r |= 1ull << 37; setbit(S.bits, a); }
    if (op != 3 && b != a && !bit(S.bits, b)) { r |= 1ull << 38; setbit(S.bits, b); }
    wr5(p, r);
  }
  /* forward pass: register allocation, records rewritten in place */
  for (u32 i = 0; i < sizeof S.bits; i++) S.bits[i] = 0;
  for (int k = 0; k < 256; k++) setbit(S.bits, S.outs[k]);              /* is-output */
  for (int i = 0; i < 8; i++) S.freelo[i] = 0;
  for (int i = 0; i < 24; i++) S.freehi[i] = 0;
  u32 nxt = 256, top = 256;
  for (u32 k = 0; k < nin; k++) {
    u8 *p = sliced + (u64)SL_REC * k;
    u64 r = rd5(p);
    u32 op = (u32)(r & 3), a = (u32)((r >> 2) & 0x1FFFF), b = (u32)((r >> 19) & 0x1FFFF);
    int da = (int)((r >> 37) & 1), db = (int)((r >> 38) & 1);
    u32 ra = regof(a), rb = op == 3 ? 0 : regof(b);
    if (da) { if (ra < 256) S.freelo[ra >> 5] |= 1u << (ra & 31); else { u32 q = ra - 256; S.freehi[q >> 5] |= 1u << (q & 31); } }
    if (op != 3 && db) { if (rb < 256) S.freelo[rb >> 5] |= 1u << (rb & 31); else { u32 q = rb - 256; S.freehi[q >> 5] |= 1u << (q & 31); } }
    u32 dst = k + 257, d;
    int pinned = -1;
    if (bit(S.bits, dst)) { for (int o = 0; o < 256; o++) if (S.outs[o] == dst) { pinned = o; break; } }
    if (pinned >= 0 && (S.freelo[pinned >> 5] >> (pinned & 31)) & 1) { d = (u32)pinned; S.freelo[d >> 5] &= ~(1u << (d & 31)); }
    else {
      int lo = lowest(S.freehi, 24);
      if (lo >= 0) { d = 256 + (u32)lo; S.freehi[lo >> 5] &= ~(1u << (lo & 31)); }
      else { lo = lowest(S.freelo, 8); if (lo >= 0) { d = (u32)lo; S.freelo[lo >> 5] &= ~(1u << (lo & 31)); } else d = nxt++; }
    }
    if (d + 1 > top) top = d + 1;
    wr5(p, (u64)op | ((u64)d << 3) | ((u64)ra << 13) | ((u64)rb << 23));
  }
  /* final permutation: output k into register k */
  for (int i = 0; i < 1024; i++) S.where[i] = 0;
  for (int o = 0; o < 256; o++) S.where[regof(S.outs[o])] = (u16)(o + 1);
  u32 moves = 0;
  static u32 oreg[256];
  for (int o = 0; o < 256; o++) oreg[o] = regof(S.outs[o]);
  for (int o = 0; o < 256; o++) {
    if (oreg[o] == (u32)o) continue;
    if (S.where[o]) {
      u32 other = S.where[o] - 1;
      u32 spare = 0; while (spare < top && S.where[spare]) spare++;
      if (nin >= SL_MAX) { info.err = 5; return 5; }
      wr5(sliced + (u64)SL_REC * nin, 4ull | ((u64)spare << 3) | ((u64)o << 13)); nin++;
      S.where[spare] = (u16)(other + 1); oreg[other] = spare; S.where[o] = 0; moves++;
    }
    if (nin >= SL_MAX) { info.err = 5; return 5; }
    wr5(sliced + (u64)SL_REC * nin, 4ull | ((u64)o << 3) | ((u64)oreg[o] << 13)); nin++;
    S.where[oreg[o]] = 0; S.where[o] = (u16)(o + 1); oreg[o] = (u32)o; moves++;
  }
  info.ninst = nin; info.nreg = top; info.moves = moves; info.err = err;
  info.sz_sliced = sizeof sliced; info.sz_packed = sizeof packed; info.sz_scratch = sizeof S + sizeof oreg;
  return err;
}

/* ================================================================ Part B: the packed generator (the accepted package's C port at ROUNDS = 64) */
typedef struct { u8 kind; u8 pad; u16 name; u32 c; u64 bound; } PV;       /* kind 0: constant c; kind 1: register value name, bound */
static struct { u16 last[PK_MAX + 8]; u16 reg[PK_MAX + 8]; u8 isfree[256]; u8 outpin[PK_MAX + 8]; PV W[ROUNDS]; PV outv[8]; } P;
static u32 pnin, pcalls, perr;

static u32 pemit(char op, u32 a, u32 b, int bimm) {
  pcalls++;
  if (pnin >= PK_MAX) { perr = 1; return 0; }
  u8 *rec = packed + (u32)PK_REC * pnin;
  for (int i = 0; i < PK_REC; i++) rec[i] = 0;
  rec[0] = (u8)op;
  rec[1] = (u8)(pnin + 8); rec[2] = (u8)((pnin + 8) >> 8);
  rec[3] = (u8)a; rec[4] = (u8)(a >> 8);
  if (bimm) { rec[7] = 1; rec[8] = (u8)b; rec[9] = (u8)(b >> 8); rec[10] = (u8)(b >> 16); rec[11] = (u8)(b >> 24); }
  else { rec[5] = (u8)b; rec[6] = (u8)(b >> 8); }
  return 8 + pnin++;
}
static int bitlen(u64 x) { int n = 0; while (x) { n++; x >>= 1; } return n; }
static PV pcst(u32 c) { PV v; v.kind = 0; v.pad = 0; v.name = 0; v.c = c; v.bound = 0; return v; }
static PV pvar(u32 name, u64 bound) { PV v; v.kind = 1; v.pad = 0; v.name = (u16)name; v.c = 0; v.bound = bound; return v; }
static PV pmask(PV a) { return pvar(pemit('&', a.name, (u32)M32, 1), M32); }
static PV pclean(PV a) { return (a.kind == 0 || a.bound <= M32) ? a : pmask(a); }
static PV padd(int n, const PV *xs) {
  pcalls++;
  u32 c = 0; PV acc; int have = 0;
  for (int i = 0; i < n; i++) if (xs[i].kind == 0) c += xs[i].c;
  for (int i = 0; i < n; i++) {
    if (xs[i].kind == 0) continue;
    if (!have) { acc = xs[i]; have = 1; continue; }
    PV v = xs[i];
    while (acc.bound + v.bound >= LIM36) { if (acc.bound >= v.bound) acc = pmask(acc); else v = pmask(v); }
    acc = pvar(pemit('+', acc.name, v.name, 0), acc.bound + v.bound);
  }
  if (!have) return pcst(c);
  if (c) {
    if (acc.bound + c >= LIM36) acc = pmask(acc);
    acc = pvar(pemit('+', acc.name, c, 1), acc.bound + c);
  }
  return acc;
}
static PV padd2(PV a, PV b) { PV x[2]; x[0] = a; x[1] = b; return padd(2, x); }
static PV padd4(PV a, PV b, PV c, PV d) { PV x[4]; x[0] = a; x[1] = b; x[2] = c; x[3] = d; return padd(4, x); }
static PV padd5(PV a, PV b, PV c, PV d, PV e) { PV x[5]; x[0] = a; x[1] = b; x[2] = c; x[3] = d; x[4] = e; return padd(5, x); }
static PV pxor(PV a, PV b) {
  pcalls++;
  if (a.kind == 0 && b.kind == 0) return pcst(a.c ^ b.c);
  if (a.kind == 0) { PV t = a; a = b; b = t; }
  if (b.kind == 0) {
    if (b.c == 0) return a;
    int m = bitlen(a.bound) > bitlen(b.c) ? bitlen(a.bound) : bitlen(b.c);
    return pvar(pemit('^', a.name, b.c, 1), (1ull << m) - 1);
  }
  int m = bitlen(a.bound) > bitlen(b.bound) ? bitlen(a.bound) : bitlen(b.bound);
  return pvar(pemit('^', a.name, b.name, 0), (1ull << m) - 1);
}
static PV pand(PV a, PV b) {
  pcalls++;
  if (a.kind == 0 && b.kind == 0) return pcst(a.c & b.c);
  if (a.kind == 0) { PV t = a; a = b; b = t; }
  if (b.kind == 0) {
    if (b.c == 0) return pcst(0);
    return pvar(pemit('&', a.name, b.c, 1), a.bound < b.c ? a.bound : b.c);
  }
  return pvar(pemit('&', a.name, b.name, 0), a.bound < b.bound ? a.bound : b.bound);
}
static u32 ror32(u32 v, int k) { return (v >> k) | (v << (32 - k)); }
static PV pror(PV a, int r) {
  pcalls++;
  if (a.kind == 0) return pcst(ror32(a.c, r));
  u32 s1 = pemit('>', a.name, (u32)r, 1);
  u32 h = pemit('&', s1, (u32)((1ull << (32 - r)) - 1), 1);
  u32 s2 = pemit('<', a.name, (u32)(32 - r), 1);
  u32 lo = pemit('&', s2, (u32)((((1ull << r) - 1) << (32 - r)) & M32), 1);
  return pvar(pemit('|', h, lo, 0), M32);
}
static PV pshr(PV a, int k) {
  pcalls++;
  if (a.kind == 0) return pcst(a.c >> k);
  u32 s1 = pemit('>', a.name, (u32)k, 1);
  u64 m = (1ull << (32 - k)) - 1;
  return pvar(pemit('&', s1, (u32)m, 1), m);
}
static void build_packed(void) {
  PV *W = P.W;
  for (int i = 0; i < 5; i++) W[i] = pcst(PREFIX_W[i]);
  for (int i = 5; i < 13; i++) W[i] = pvar((u32)(i - 5), M32);
  for (int i = 13; i < 16; i++) W[i] = pcst(TAIL_W[i - 13]);
  for (int i = 16; i < ROUNDS; i++) {
    PV x = W[i - 15], y = W[i - 2];
    PV r7 = pror(x, 7); PV r18 = pror(x, 18); PV p0 = pxor(r7, r18); PV h3 = pshr(x, 3); PV s0 = pxor(p0, h3);
    PV r17 = pror(y, 17); PV r19 = pror(y, 19); PV p1 = pxor(r17, r19); PV h10 = pshr(y, 10); PV s1 = pxor(p1, h10);
    W[i] = padd4(W[i - 16], s0, W[i - 7], s1);
  }
  PV a = pcst(IV[0]), b = pcst(IV[1]), c = pcst(IV[2]), d = pcst(IV[3]), e = pcst(IV[4]), f = pcst(IV[5]), g = pcst(IV[6]), h = pcst(IV[7]);
  PV bc = pxor(b, c);
  for (int i = 0; i < ROUNDS; i++) {
    PV e6 = pror(e, 6); PV e11 = pror(e, 11); PV pe = pxor(e6, e11); PV e25 = pror(e, 25); PV s1 = pxor(pe, e25);
    PV chv;
    if (g.kind == 0 && g.c == 0) chv = pand(e, f);
    else { PV fg = pxor(f, g); PV an = pand(e, fg); chv = pxor(g, an); }
    PV t1 = padd5(h, s1, chv, pcst(K[i]), W[i]);
    PV a2 = pror(a, 2); PV a13 = pror(a, 13); PV pa = pxor(a2, a13); PV a22 = pror(a, 22); PV s0 = pxor(pa, a22);
    PV ab = pxor(a, b);
    PV mj;
    if (c.kind == 0 && c.c == 0) mj = pand(a, b);
    else { PV an2 = pand(ab, bc); mj = pxor(an2, b); }
    bc = ab;
    PV t2 = padd2(s0, mj);
    PV na = pclean(padd2(t1, t2));
    PV ne = pclean(padd2(d, t1));
    h = g; g = f; f = e; e = ne; d = c; c = b; b = a; a = na;
  }
  PV st[8]; st[0] = a; st[1] = b; st[2] = c; st[3] = d; st[4] = e; st[5] = f; st[6] = g; st[7] = h;
  for (int i = 0; i < 8; i++) P.outv[i] = pclean(st[i]);
}
static void put16(u8 *p, u32 v) { p[0] = (u8)v; p[1] = (u8)(v >> 8); }
static u32 get16(const u8 *p) { return (u32)p[0] | ((u32)p[1] << 8); }

EXPORT("run_packed") int run_packed(void) {
  perr = 0; pnin = 0; pcalls = 0;
  build_packed();
  info.sz_pk_scratch = sizeof P;
  if (perr) { info.err = 10 + perr; return info.err; }
  for (int i = 0; i < 8; i++) if (P.outv[i].kind != 1 || P.outv[i].bound > M32) { info.err = 13; return 13; }
  for (u32 k = 0; k < PK_MAX + 8; k++) { P.last[k] = 0xFFFF; P.reg[k] = 0; P.outpin[k] = 0; }
  for (u32 k = 0; k < pnin; k++) {
    u8 *rec = packed + (u32)PK_REC * k;
    P.last[get16(rec + 3)] = (u16)k;
    if (!rec[7]) P.last[get16(rec + 5)] = (u16)k;
  }
  for (int j = 0; j < 8; j++) P.outpin[P.outv[j].name] = (u8)(1 + j);
  for (int j = 0; j < 8; j++) P.reg[j] = (u16)j;
  for (int j = 0; j < 256; j++) P.isfree[j] = 0;
  u32 nxt = 8, top = 8;
  for (u32 k = 0; k < pnin; k++) {
    u8 *rec = packed + (u32)PK_REC * k;
    u32 nm = get16(rec + 1), a = get16(rec + 3), b = get16(rec + 5), bimm = rec[7];
    u32 ra = P.reg[a], rb = bimm ? 0 : P.reg[b];
    if (P.last[a] == k && !P.outpin[a] && P.reg[a] >= 8) P.isfree[P.reg[a]] = 1;
    if (!bimm && b != a && P.last[b] == k && !P.outpin[b] && P.reg[b] >= 8) P.isfree[P.reg[b]] = 1;
    u32 d;
    if (P.outpin[nm]) {
      d = (u32)P.outpin[nm] - 1;
      if (P.last[d] != 0xFFFF && P.last[d] > k) { info.err = 14; return 14; }
    } else {
      d = 0;
      for (u32 r = 8; r < nxt; r++) if (P.isfree[r]) { d = r; break; }
      if (d) P.isfree[d] = 0; else d = nxt++;
    }
    P.reg[nm] = (u16)d;
    if (d + 1 > top) top = d + 1;
    put16(rec + 1, d); put16(rec + 3, ra);
    if (!bimm) put16(rec + 5, rb);
  }
  info.calls = pcalls; info.ninst = pnin; info.nreg = top; info.err = perr;
  return perr;
}

#ifdef NATIVE
#include <stdio.h>
static void dump_sliced(FILE *f, u32 n) {
  static const char *OPS[] = {"^", "&", "|", "~", "mov"};
  for (u32 k = 0; k < n; k++) {
    u64 r = rd5(sliced + (u64)SL_REC * k);
    u32 op = (u32)(r & 7), d = (u32)((r >> 3) & 0x3FF), a = (u32)((r >> 13) & 0x3FF), b = (u32)((r >> 23) & 0x3FF);
    if (op >= 3) fprintf(f, "%s %u %u\n", OPS[op], d, a); else fprintf(f, "%s %u %u %u\n", OPS[op], d, a, b);
  }
}
static void dump_packed(FILE *f, u32 n) {
  for (u32 k = 0; k < n; k++) {
    const u8 *rec = packed + (u32)PK_REC * k;
    char opb[3] = {(char)rec[0], 0, 0}; if (rec[0] == '<' || rec[0] == '>') { opb[1] = opb[0]; }
    if (rec[7]) fprintf(f, "%s %u %u #%u\n", opb, get16(rec + 1), get16(rec + 3), (u32)rec[8] | ((u32)rec[9] << 8) | ((u32)rec[10] << 16) | ((u32)rec[11] << 24));
    else fprintf(f, "%s %u %u %u\n", opb, get16(rec + 1), get16(rec + 3), get16(rec + 5));
  }
}
int main(int argc, char **argv) {
  int rc = run_sliced();
  printf("run_sliced rc %d: lines %u, registers %u, moves %u, calls %u, nots %u; static: sliced %u B, packed %u B, sliced scratch %u B\n",
         rc, info.ninst, info.nreg, info.moves, info.calls, info.nots, info.sz_sliced, info.sz_packed, info.sz_scratch);
  u32 ns = info.ninst;
  if (argc > 1) { FILE *f = fopen(argv[1], "w"); dump_sliced(f, ns); fclose(f); }
  rc = run_packed();
  printf("run_packed rc %d: lines %u, registers %u, calls %u; packed scratch %u B\n", rc, info.ninst, info.nreg, info.calls, info.sz_pk_scratch);
  if (argc > 2) { FILE *f = fopen(argv[2], "w"); dump_packed(f, info.ninst); fclose(f); }
  return 0;
}
#endif
```
