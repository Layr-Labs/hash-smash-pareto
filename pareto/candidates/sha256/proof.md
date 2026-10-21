# sha256-r40: birthday search with 256 bit-sliced lanes, one unrolled program of 5-byte records, a 64-byte message (two blocks after padding)

Credited derivative of our filed round-40 entry 4ab23c0a (123.91345), of bfcaad61 (123.92954) and of the entries named here, all declared as dependencies (same challenge): 4ab23c0a-bb17-4657-8eaf-e0ed2a8d7030 (123.91345, our round-40 entry), bfcaad61-9487-4edb-8778-b5408e713d01 (123.92954, round-40 entry), a5707aa9-5267-4db3-ad10-9914e6b280be (123.94406, round-40 entry), 87cb17fa-d025-4066-bd13-91d9936ce327 (124.28559, round-43 entry), 4684dfc2-cdac-4441-af91-c9979e2888a9 (124.26094, mitchuski's round-64 entry), 1884db5b-acc6-42e7-ac3c-5877e77b8277 (124.22926, mitchuski's round-57 entry), 3642e1cd-e391-41a7-81e0-456c02e4becd (124.31538, lamb356's round-64 entry), 6b678689-e6a2-42b0-87d8-fff55432f2f6 (124.41766, dariolina's round-64 entry), 744875ec-f063-4208-8075-b61192ac4d69 (124.83147, dariolina's round-39 entry), 44870635-2031-4c6a-aa62-c44672c7f338 (118.346, lamb356's round-39 entry) and 38912d66-c0d0-4238-9058-1e8a2775f695 (120.46, sraiw's round-39 entry). From bfcaad61 and 87cb17fa this entry keeps the 64-byte two-block message layout with the 8-word prefix that cancels K8 and K9, the offset words W(8+k) = y_k - K(8+k), walk B, the search with distinguished points, the index-layout trail table, the handlers, the ledger method, the success bound (Lemma 2 of Section 4: bounded restart with the detection delay integrated; no premise besides H1), the unrolled kernel of 5-byte body records (the price of dariolina's 6b678689, Section 3.1), its allocator and C generator, and the rolled two-lane recovery program. Seven optimizations are new against bfcaad61 (all counted in the program):
(1) A third 9-gate pair-carry column template (T2) in `Gen._col` eliminates all 182 polarity-mismatch penalty columns when `x[1] == y[1] == z[1] != (U[1] ^ u[1])` (-182 gates), bringing every `add3` call in `_net_u` to the 276-gate minimum with O(1) direct polarity selection (reducing generator primitive calls 6.37x from 1,180,238 to 185,312).
(2) Full `add3` carry-in absorption (`cin in {0, 1, 2}` at 276 gates, 0 extra gates), `_add_u` bit-0 carry identity (`A[0] & ~u[0]` for `cin=0`, `A[0] | u[0]` for `cin=1`, eliminating `B_fix`), and `_rnd2` `delta in {0, 1}` carry propagation across `ne` and `na` (-124 gates).
(3) Step 10 `Maj(a, b, 0) = a & b` since `c = a_8 = 0` (-32 gates), and joint `W_split` pre-constant variable-sum reuse (`s_k = W[k] - cv_k`) across `W[16..23]` and `T1[16..23]` (-20 gates).
(4) Per-bit polarity-matched Walk-B tail shears (`QM = 0x74a40866`, `XM = 0x46eb57e6`) and multi-word `add3` fusion (-114 gates): `Q` shears `Maj(a_(40-6), a_(40-7), a_(40-8))` into `Ch(a_(40-6) ^ a_(40-7), a_(40-8), QM)` (32 XORs + 32 same-polarity AND/OR gates, 0 polarity penalties; `-32` gates); `X` shears `Ch(e_(40-2), e_(40-3), e_(40-4))` into `Ch(e_(40-2), XM, e_(40-4))` (32 same-polarity AND/OR gates, 0 polarity penalties; `-17` gates); `e3`, `e2` and `Y` fuse 5-word and 3-word sums via `add3` with early `W[38]/W[39]` scheduling (`-65` gates).
(5) Exact-peak 926-register zero-move allocator (`REGISTERS = 926`, `REGFILE = 29,728` bytes, saving 3,040 bytes with 0 moves) by routing short-lived non-output nodes into idle output target registers before their output nodes are created.
(6) Fused 6-iteration `RecProg` (`414` records, `65` init records, `1,424` ops/call, `2,048`-byte array, saving 44 instructions, 512 array bytes and 255 ops/call).
(7) Stage-1 filter split `s1 = 20, W = 102` (`D = 122` unchanged, reducing stage-1 test from 34 to 22 ops/batch) and `(Tp = 1895, CMAX = 6, KAPPA_256 = 13, GRAIN = 10^21)` plan tuning, increasing `tmax` from 121,442 to 122,788 and reducing `time_log2` from `123.92954` (`123.91345` in `4ab23c0a`) to **`123.91264`** (`-0.01690` bits vs `bfcaad61`).
The kernel evaluates one block-1 compression of 40 steps for 256 independent trails at once in bit-sliced form (one 256-bit word holds bit j of all 256 states; rotations are renaming). One batch of 256 trails is 43,648 program records (170.50 per trail, 0.0589 of the 2896 operations of one reference compression). The price is a declared register file of 929 words of 256 bits (29,728 bytes, counted as memory), 43,648 body records at 5 bytes (218,240 bytes), 1,646 other instructions at 36 bytes (59,256 bytes), an array of 2,048 bytes and a table of 122,788 entries. No advice; no differential or structural property of the 40 steps is used (Section 1.1 explains why the 39-step Table 23 differential characteristic of ePrint 2026/1120 terminates at step 39).

## 1. Target and relation

Target `sha256-r40-prefix-v1` (the Pareto lane `sha256`, round 40). The two colliding messages have 64 bytes each. With x a 256-bit integer and y0..y7 its eight 32-bit words (big-endian, y0 the highest), M(x) is the 16 big-endian words W0..W15 with
- W0..W7 = the constant words 3e73281c, 752d8ed2, ad19eff1, 7250fceb, d4095422, 44fdb519, 43f22c5b, d8d6aac4 (Section 3.2 gives how they are computed),
- W8 = y0, W9 = y1, and W(8+k) = y_k - K(8+k) modulo 2^32 for k = 2..7.
FIPS 180-4 padding appends 0x80, 55 zero bytes and the 64-bit length 512: the padded message is 128 bytes, two blocks, and block 2 is the same for every x. The target runs the steps 0 to 39 on each block, block 1 from the standard IV and block 2 from the chaining value cv1 = IV + s(x) word by word, where s(x) is the working state after step 39 of block 1; the digest is the result of block 2 with its feed-forward (`verifier/hash_functions.py:digest(M(x), "sha256", 40)`). The profile's message domain is "finite byte strings of bit length below 2^64"; a 64-byte string is in it.
Write a_i, e_i for the a and e words after i steps of block 1 (a_0, e_0 from the IV), T1_i for the T1 of the step that produces them and W_j for the schedule word of step j. With the fixed 32-bit polarity masks `QM = 0x74a40866` and `XM = 0x46eb57e6`, f(x) is walk B (4684dfc2) with per-bit polarity-matched disjoint-support shears on Q and X: the eight words e_(40-3), e_(40-2), X = e_(40-5) + Ch(e_(40-2), XM, e_(40-4)) + W_38 (at bit j: `e_(40-2)[j] | e_(40-4)[j]` when `(XM >> j) & 1 == 1` and `~e_(40-2)[j] & e_(40-4)[j]` when `(XM >> j) & 1 == 0`; since `Ch(e2, e3, e4) = Ch(e2, XM, e4) + (e2 & e3 & ~XM) - (e2 & ~e3 & XM) mod 2^32`, the inverse adds `(e2 & e3 & ~XM) - (e2 & ~e3 & XM)`), T1_(40-4), Q = T1_(40-5) + Ch(a_(40-6) ^ a_(40-7), a_(40-8), QM) (at bit j: `~(a_(40-6)[j] ^ a_(40-7)[j]) | a_(40-8)[j]` when `(QM >> j) & 1 == 1` and `(a_(40-6)[j] ^ a_(40-7)[j]) & a_(40-8)[j]` when `(QM >> j) & 1 == 0`; since `Maj(a6, a7, a8) = Ch(a6 ^ a7, a8, QM) + (a6 & a7 & ~QM) - (~a6 & ~a7 & QM) mod 2^32`, the inverse adds `(a6 & a7 & ~QM) - (~a6 & ~a7 & QM)`), a_(40-6), a_(40-7), Y = e_(40-4) + W_39, in this order (permutation (6, 1, 7, 0, 5, 4, 2, 3) of bw, the order with no register move, Section 3.2), as a 256-bit integer. These words determine s(x): the program's `enc_invert` recovers a_(40-5) = Q + (a_(40-6) & a_(40-7) & ~QM) - (~a_(40-6) & ~a_(40-7) & QM) + Sigma0(a_(40-6)), then a_(40-4), a_(40-3), a_(40-2), the T1 of steps 38 (= X + (e_(40-2) & e_(40-3) & ~XM) - (e_(40-2) & ~e_(40-3) & XM) + Sigma1(e_(40-2)) + K_38) and 39 and the whole state, by additions, subtractions and the round functions. The walk is g(x) = f(x) XOR q, q a fixed 256-bit mask (127 output planes that the generator leaves complemented instead of spending a NOT).
So g(x) = g(y) gives s(x) = s(y), hence the same cv1, the same block 2 and equal digests. x != y gives M(x) != M(y), since x -> W8..W15 is a bijection. The attack outputs two distinct 64-byte messages with equal complete 256-bit digests.
The selftest (`python3 bssha.py --selftest`) compares the program with the scalar g on 2,560 lanes (including all-zero and all-one inputs), 4 chained steps, the inverse on 10,000 random states, the recovery program, the experiments' digest network and 6 width-16 search attempts; the compiled C generator (`GEN_C`) emits the exact same 43,648 records and q mask.

### 1.1 Why the 39-step differential characteristic does not extend to 40 steps
In the 39-step collision attack (`44870635`, `7c4da9b7`) based on Table 23 of ePrint 2026/1120, the 19-step local collision spans steps r = 8..26 with active message words {8, 9, 10, 11, 12, 16, 17, 24, 26}, giving dW_r = dA_(r+1) = dE_(r+1) = 0 for the 12 steps r = 27..38. At step r = 39 (the 40th step), W_39 = sigma1(W_37) + W_32 + sigma0(W_24) + W_23 has dW_37 = dW_32 = dW_23 = 0, while step 24 requires dW_24 = 0x03010000 != 0 to cancel dh = dE_21 = -0x03010000. Because sigma0(x) = ROTR^7(x) ^ ROTR^18(x) ^ (x >> 3) has full F_2-rank 32 (is a bijection on {0,1}^32), dW_39 = sigma0(W'_24) - sigma0(W_24) != 0 with probability 1 for all 2^32 values of W_24. Shifting the local collision by +1 step (r = 9..27) moves offset d = 7 from the free initial word W_15 to the recurrence word W_16 = sigma1(W_14) + W_9 + sigma0(W_1) + W_0, forcing nonzero differences in W_0, W_1 or W_14 and activating steps 0..1 from the fixed IV. Thus 40-step SHA-256 remains in the generic birthday regime.

## 2. The attack (program `experiments/bssha.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 20 bits are zero (`s1 = 20`; low 20 bits of chain word y7, the 20 low planes) and the 102-bit number F = (x >> 20) mod 2^102 (`W = 102`, `D = s1 + W = 122`) is below Tp = 1895. The density is theta = 1895 / 2^122 and L = 1 / theta = 2^111.1121. The key of a DP is the 35 bits of x above bit 121 followed by the 11 low bits of F (F < 1895 < 2^11); 46 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated program of Section 3.2. The start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 20 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise write the key and a written bit into slot t of the table (47-bit slots, Section 7; t is the slot position, no length is stored) and start trail t' = next index in that lane.
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = ceil(13 L) batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 122,803 keys, when a seventh trail would be cut (`CMAX = 6`), or if step 6 finds no pair.
6. Recovery. Pass 1 recomputes the length of the stored trail: step g from its start until the first DP (`trail_length`; the length of the new trail is known). The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps of g, then step both together; at the first step with g(a) = g(b) and a != b output (a, b). The recovery program (1,418 records executed per call, 408 records: g of two chain values in the two lanes of 256-bit words, rolled, 36-byte instructions, Section 3.3) is used. Each pass runs at most capr = c + S batches (the program halts if a length exceeds capr).
Constants (all computed by `plan(256)` of the program, printed by `python3 bssha.py --ledger`): Tp = 1895, L = 5316911983139663491615228241121378304 / 1895, B = 1324927479007690000000000000000000000, Q = 256 B = 0.99676 * 2^128 evaluations, e2max = 646937245609223632812500000000064, c = 36474857931828826063851169991861699 (= 2^114.812), table capacity tmax = 122,803 stored trails in 123,065 = tmax + 256 + 6 slots of 47 bits, one per trail number (256 starts, tmax stored trails, 6 cut trails). The trail numbers stay below 123,065 < 2^17, so every trail has its slot (the program asserts it when it writes a slot).
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is a constant of the program).

## 3. Operation ledger

### 3.1 Machine
Machine model of this entry (declared cost-model prices). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices operations and memory; it gives no register count and no instruction size.
This entry declares a load/store machine with 256-bit words and 929 registers (the 926 data registers that the shipped allocator uses and three pointer registers). Charged, one operation each: every XOR, AND, OR and NOT of a 256-bit register, every register move, every set of a register to a constant, every load and store, every pointer addition, comparison and conditional branch, and the one random word. Nothing is free except the renaming of a bit-sliced rotation, and nothing is executed that is not a record of the program. The operation ledger is the exact count of the records of the submitted program, listed by `python3 bssha.py --text` and counted by `--ledger` (Appendix A); the organizer can regenerate it.
THE 5-BYTE BODY PRICE (a cost-model price, score-critical, the convention of dariolina's 6b678689, kept from 87cb17fa and bfcaad61). A main-loop body instruction is a register-to-register XOR, AND, OR, NOT or move of 256-bit registers with no immediate operand, encoded in 5 bytes: an opcode byte and three 10-bit register fields. The 43,648 records of the kernel are all of this kind (34,230 XOR, 5,782 AND, 3,636 OR, 0 NOT, 0 moves, 0 sets), so the kernel is 218,240 bytes of code. Every other instruction (stage 1, the batch loop, the handlers, the recovery program, setup and the generator's code image) is charged 36 bytes. At 36 bytes per body record the kernel alone would be 1.5 times the limit of 2^20 bytes.

### 3.2 One batch = 43,673 operations for 256 trails
Representation: a 32-bit word is 32 planes; plane j holds bit j of the word of every lane. A rotation is a renaming of planes. The sum of two words is a ripple of full adders over the planes. The full adder is the pivot adder of 6ae36351 (`Gen.fa`): each signal is a (node, polarity) pair, so complements are free; with three variable inputs, two share a polarity and the third is the pivot p: sum = u XOR y, carry = (u AND (y XOR p)) XOR p with u = x XOR p, 5 gates. With constant inputs the gates fold at build time.
Constants fold at build time: in a sum of several words (`Gen.addm`) the constant words are added first at no cost, then `add3` and ripple adders reduce the variable words; carry-ins into `add3` (up to 2 per `add3` call) and into `add` (1 per `add` call) subtract `bb` from the constant `cv` at zero extra gates so that `cv - bb` has the most trailing zeros, and the remaining constant `cv - bb`, if nonzero, is one more adder. When `cv - bb != 0`, `Gen.addm` also records the pre-constant variable sum `s_k = W[k] - (cv - bb)` in `g.split` so downstream rounds (`i = 17, 19, 21, 23`) can fold `cv - bb` directly into `K[i]` or the next schedule constant (`-20` gates). A gate whose two operands are the same two input planes as an earlier gate is not built twice (a node table; the first XORs of sigma0(W8) are those of Sigma0(a_9), since a_9 = y0).
Pair-carry path (`Gen.add3(A, B, C, cin)` for `cin in {0, 1, 2}`): a sum with three or more variable words takes three words at a time in one ripple whose carry between columns is a pair of planes (u, U) standing for U ? 1 : 2u. At bit 0: for `cin = 0`, `(s[0], U) = fa(A[0], B[0], C[0])`, `u = ZERO` (5 gates at bit 0, 8 at bit 1); for `cin = 2` (adding +2), `(s[0], c0) = fa(A[0], B[0], C[0])`, `u = ONE, U = ~c0` (5 gates at bit 0, 8 at bit 1); for `cin = 1` (adding +1), with pivot `p` and equal-polarity pair `x, y` among `(A[0], B[0], C[0])`, `u0 = x ^ p, s[0] = u0 ^ ~y, u = p, U = u0 | (y ^ p)` (4 gates at bit 0, 9 at bit 1). In all three cases bits 0..1 take 13 gates total. A column of bits 1 to 30 takes the three addend bits x, y, z and the incoming pair (u, U) and returns the sum bit and the outgoing pair by one of three 9-gate templates: (T0) `n5 = z ^ U, n9 = x ^ n5, s = y ^ n9, n6 = x ^ y, n8 = U | (z ^ u), n11 = ~n6 & n9, u' = n5 ^ n11, U' = n8 ^ n11`; (T1) `w = y ^ U, n8 = z ^ w, s = x ^ n8, n6 = U | (y ^ u), u' = n6 ^ w, U' = n6 ^ (n8 & (x ^ w))`; (T2) `w5 = x ^ y, w6 = z ^ w5, s = U ^ w6, w9 = u ^ w6, w10 = U | ~w9, w11 = w5 | (x ^ z), u' = w6 ^ ~w10, U' = w10 ^ ~w11`. All three satisfy `x + y + z + val(u, U) = s + 2 val(u', U')` on all 32 input rows. T0 and T1 cover all cases where at least one addend bit has polarity `U[1] ^ u[1]`, while T2 covers `x[1] == y[1] == z[1] != (U[1] ^ u[1])` because `w5 = x ^ y` and `x ^ z` both have polarity 0 and `~w9` has polarity `U[1]`. Every column is therefore 9 gates (8 at bit 1 when `u` is constant and at bit 30 where only `U'` is built, 3 at bit 31: **276 gates** per `add3`, with zero 10-gate penalty columns), and the template/permutation is selected in O(1) directly from the input polarities.
The program is ONE straight network (`_net_u`), with no loop, no load, no store:
- The message words: W0..W7 are constants; W8, W9 are the chain words y0, y1 (registers 256..511 hold the chain value: plane j of x is in register 256 + 32 (7 - j div 32) + j mod 32); W10..W15 are y_k - K(8+k), one adder each with the constant folded in, used only by the schedule. W_i for 16 <= i <= 37 is built right before step i; at i = 38, 39, `W[i]` pre-reduces `(W[i-16], s0(W[i-15]), W[i-7])` via `add3`.
- The prefix: W0..W7 are chosen step by step from the IV so that a_1 = K9 - K8, a_2 = -K9, a_3 = ... = a_8 = 0 (`_anchor_prefix`: each W_i sets the next a to the anchor). So e_5 = K9 - K8, e_6 = -K9, e_7 = e_8 = 0, steps 0 to 7 are constants (no gate), step 8 has T1 = e_5 + Ch(0, 0, e_6) + K8 + W8 = y0, and step 9 has T1 = Sigma1(y0) + y1: K8 and K9 cancel, and K + W = y enters steps 10..15 directly.
- A full step does T1 = h + Ch + Sigma1 + (K + W) - delta (`delta in {0, 1}`) with `u = h XOR Ch = (h XOR g) XOR (e AND (f XOR g))` and `_add_u(g, h, u, cin_u)` (`c_0 = h[0] & ~u[0]` for `cin_u = 0`, `c_0 = h[0] | u[0]` and `s[0] = ~u[0]` for `cin_u = 1`), so `Ch` and `B_fix` are never built; `Maj = a & b` at step 10 (where `c = a_8 = 0`) and `((a XOR b) AND (b XOR c)) XOR b` otherwise, sharing the previous step's `a XOR b`; `new e = d + T1 + delta`, `new a = T1 + Sigma0 + Maj + delta`. The full steps are 0 to 33.
- The last six steps form walk B (Section 1): `T5 = T1_(40-5) - 1`, `e_(40-5) = a_(40-9) + T5 + 1` and `Q = T5 + Ch(a_(40-6) ^ a_(40-7), a_(40-8), QM) + 1`; `T4 = T1_(40-4)` and `e_(40-4) = a_(40-8) + T4`; `e_(40-3)` and `e_(40-2)` via 5-word `addm(a, h, _ch_direct, Sigma1, K, W)`; `X = addm(W_38_part, s1(W_36), e_(40-5), Ch(e_(40-2), XM, e_(40-4)))`; `Y = addm(W_39_part, s1(W_37), e_(40-4))`. No T2 and no new a is formed in these steps.
- The allocator (`_alloc`, mirrored by the C generator) is a streaming register allocator: short-lived non-output nodes (`uses[k] <= 3` and `k < oid[32] - 200`) borrow idle output target registers (`256..511` before `oid[0] - 30`, `256..447` after) that are guaranteed to die before their output nodes arrive, while longer-lived nodes take a dying operand register or the lowest free non-target register. The output planes go to registers 256..511, the input registers of the next batch. Permutation `(6, 1, 7, 0, 5, 4, 2, 3)` of `bw` gives 0 register moves and 0 NOTs (127 negative-polarity output planes are recorded in `q`). The program peaks at 926 live planes and uses exactly **926 data registers** (929 total with 3 pointer registers).
Executed per batch (43,648 records, all 5-byte body records): 34,230 XOR + 5,782 AND + 3,636 OR = 43,648 gates; 0 NOT; 0 set; 0 moves; no load, no store, no control record. Per trail 170.500 operations = 0.0589 unit.
Validation: the selftest and the organizer-reference checks of Section 1; the C generator of Section 3.6 emits the identical records.
The generator runs once at the start; its work is charged in the setup row (3.3), its code and peak storage in Sections 3.6 and 7.

### 3.3 Loop, stage 1, handlers and the other events
One batch: 43,648 body records + stage-1 test 22 + loop control 3 = 43,673 operations. Stage 1: the 20 low planes are combined into the mask of zero lanes: 19 ORs, a compare with zero and a branch: 22 operations (`stage1_ops`), charged as 36-byte instructions. A DP has all 20 low bits zero, so its lane is flagged.
Loop control of the batch loop: counter increment, compare with the next slice limit, branch back: 3 operations.
Handlers (charged per event at the stated bounds; 36 bytes per instruction):
- Stage-1 hit: store the 256 planes to an 8 KiB copy (256 stores), extract the lane (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (at most 15), counters. Below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail: key formation, the slot write (shift, or, store), the new start r + t' (1 add), insertion of the 256 bits of the new start in the lane (12 per plane, 3,072), reload of the 256 planes (256), lane arrays and counters (below 200). Below 3,550; charged **3,800**. The key scan of the table is charged 6 per slot (extract, mask, compare with the key and the written bit, branch), tmax + 262 slots. At most tmax finished trails.
- Slice check (every 2^48 batches): charged **1,300** each. Cut trail: charged **4,200**; at most 6 cut trails (`CMAX = 6`).
- Recovery program (`RecProg`): a second program of the same machine that evaluates g for two chain values at once, lane 0 in bits 0..31 and lane 1 in bits 128..159 of each 256-bit register (a rotation is a doubled word and right shifts, one AND with the lane mask). It is rolled and uses 36-byte instructions: the message words W0..W39 and constants K10..K33 sit in a 64-word memory array (2,048 bytes, Section 7). Per call: the six offset words get y_k - K(8+k) by three records each, the eight input words are stored as W8..W15, steps 8 and 9 are computed directly from y0 and y1 in `head`, a fused 6-iteration loop (4 steps per iteration) computes W16..W39 and rounds 10..33 together while forwarding W[q+10..q+13] and W[36..39] in registers, and the walk-B tail is straight code. 414 records in all, 65 executed once per recovery (the mask, K10..K33 and the constant words stored into memory); 1,424 records executed per call (loops included).
- Recovery batch: one call (1,424 records) plus the exact equality test of the two lanes on the 8 output words (26 operations; in pass 1 the DP test of lane 0, at most 26), loop control 3, call and return 2 and 8 moves: 39 per recovery batch (1,463 per batch), the same in both passes.
- Setup and generator: 1 random word; the 256 starts inserted (256 x 3,100 = 793,600) and one reload; counters; fixed part charged 813,600. The generator: 185,312 primitive calls (both passes) and 43,648 emitted records, each charged 200 word operations: 45,792,000. Setup and generator together 46,605,600 operations = 2^13.97451 units, charged in the time bound (3.4).
Code size: 43,648 body records at 5 bytes = 218,240 bytes; stage 1 22 + batch loop 3 + handlers 1,000 + recovery 461 (414 + 47) + setup, cut and slice 160 = 1,646 other instructions at 36 bytes = 59,256 bytes; 277,496 bytes in all.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 43,673 | 57,863,572,103,437,163,427,000,000,000,000,000,000,000 (= 5.7864e+40) |
| slice checks: ceil(B / 2^48) * 1,300 | 6.119e+24 |
| stage-1 hits: e2max * 2,800 | 1.8114e+36 |
| finished trails: 122,788 * (3,800 + 6 * 123,050) | 91,120,974,800 |
| cut trails: 6 * 4,200 | 25,200 |
| recovery: 2 (c + 2^48) * (1,424 + 39) + 600 + 65 (two passes), c + 2^48 = 2^114.812 | 1.0673e+38 |
| setup and generator | 46,605,600 |
N = 57,972,108,962,481,468,053,193,599,742,397,228,604,995 = 5.797211e+40 operations.
N / 2896 = 2.001799e+37 units = 2^123.9126369. Claim `time_log2` = 123.91264 (Appendix A, rounded up). The main loop is 99.81 percent of it, recovery 0.18 percent, stage-1 hits 0.003 percent. The walk never computes block 2: equal block-1 states give equal digests (Section 1), so one evaluation of g is one block-1 compression of 40 steps, priced by its records.

### 3.5 Register file and smaller files
Declared prices: the machine has 929 registers of 256 bits: the 926 data registers that the shipped allocator uses (matching the exact peak of 926 live planes) and three pointers. A machine with fewer registers than the peak needs spill loads and stores that the shipped allocator does not produce; no estimate of their cost is claimed. The register file is counted as memory (29,728 bytes, Section 7).

### 3.6 Generator code and peak storage of the setup
The generator that builds the program at the start of the run is part of the machine code. It is written in freestanding C (embedded in `experiments/bssha.py` as `GEN_C`, printed by `python3 bssha.py --gen-c`): the network builder with the pivot adder, the three-template pair-carry adder with O(1) polarity selection, the constant folding and `W_split` table, the node table for gates of two input planes, the network, the 926-register allocator and the emission of 5-byte records, in two passes (pass 0 counts the uses of every node, pass 1 builds the network again and emits). Charged at the 4,316 wasm instruction bound (4,316 * 36 bytes = 155,376 bytes). q falls out of the generator.
The generator emits the 43,648 records of `python3 bssha.py --text` (sha256 977903a60fa9bd0ea6cd1b21e07c5e71b9ce36697eb93f8328d551d42d2fc88b), with 185,312 primitive calls and 0 moves. Its scratch is bounded by 69,593 bytes (the use counts 43,905 bytes, 24,220 bytes of tables and signal state, a shadow stack of 1,024 bytes = 69,149 <= 69,593 bytes), and the record buffer is 218,240 bytes (43,648 x 5). The generator fits in 2^20, see the layout below.
Layout. The setup phase holds the program code at its final size (277,496 bytes), the counters and plane copy (16,384), the generator's code image (155,376) and its scratch (69,593): 518,849 bytes. In the search phase the same region holds the table (722,919 bytes) and the register file (29,728): code + counters + register file + array + table = 1,048,575 bytes. The memory of the entry is the larger of the two, 1,048,575 bytes (1 byte to spare under 2^20).

### 3.7 Preprocessing
None offline. The generator runs inside every attempt and is charged in the setup row; the claim declares preprocessing_log2 = 13.97452, the setup and generator row (46,605,600 operations = 2^13.974511 units, rounded up: the generator charge of 45,792,000 operations (3.3) and the 813,600 fixed setup operations), which is also inside time_log2. Its code image and scratch are in the setup-phase total of Section 3.6 (518,849 bytes).

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bssha.py --loss` (the function `_lossq`); Appendix A recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
pass 1 of step 6 recomputes the two lengths and pass 2 aligns and walks them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F (F < 1895 <= 2^11 and the key holds its 11 low bits), so equal keys of two DPs differ only if their bits above 156 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds g^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 20 low bits zero, so its lane is flagged and examined. A 46-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B = 0.99676 * 2^128 evaluations numbered t = 1, ..., Q batch by batch and lane by lane inside a batch, b(t) = ceil(t / 256) the batch of t; N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(13 L) = 36474857931828826063851169991861699, S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 120887.62, tmax = 122,803, CMAX = 6 (the program halts when a seventh trail would be cut). Pi_m = (1 - 0/N')(1 - 1/N') ... (1 - (m-1)/N') is the probability that m independent uniform values of a set of N' elements are distinct. PP = Q (Q - 1) / (2 N') = 0.49677, H = (Q (Q - 1) / 2 + 2^17 Q) / N' = 0.49677. Let k = 123486 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 262, p = e^(-c/L) >= (1 - theta)^c, p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)), and tmax = 122,803. Let F be a uniformly random function on 256-bit values and P_F the success probability of the attempt when every evaluation of g is replaced by F (lazy sampling). Then, with no premise,
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = Pi_Q / (1 - k Q / N') = 0.608492991   (the first collision exists),
    P_delay = (1 - k Q / N')^-1 * sum over the bins (a, b] of [0, Q] of (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = 0.00128408   (the merged path needs a DP in the batches that are left; 22,000 bins, Step 5),
    P_own = Q L / N' = 8.219e-06   (the first collision is a cycle of its own trail),
    P_long = M Q p (q + 256) / ((1 - p) N') = 2.926e-05   (its partner is on a trail with c evaluations without a DP),
    P_age = PP p2 = 1.572e-05   (the merged trail is too old when it reaches the DP),
    P_dist = PP L (Q + 2^17) / N' = 4.083e-06   (a later collision on the rest of the merged path),
    P_cut = P(Binomial(n2, p) >= 7) + E_S + E_X + E_J2a + E_J2b + E_Y (Step 6) = 4.915e-05, with E_S = Q L / N', E_X = (Q / N') L e^(-(c-2)/(2L)) (2 + (c - 1)/L) + PP p2, E_J2a = Q L H / N' + (Q + 2^17) L PP / N', E_J2b = PP (1 - theta) p2, E_Y = e^(-(c-1)/L) H,
    P_key = C(tmax, 2) / (2^kb Tp) = 1.158e-04, kb = 35,
    P_table = e^-q (e q / (tmax - 59))^(tmax - 59) = 6.937e-07,
    P_tiny = Q 2^17 / N + k^2 L / N' + 255 Q / N' + exp(-300 + (e^5 - 1) H) + 2^-90 (Step 7; it needs 240 M <= Q, which holds here).
The numbers are printed by `python3 bssha.py --loss` (the function `_lossq`) and Appendix A recomputes the whole bound in exact rationals and 60-digit decimals (`certify`, outward rounding) and asserts the result >= 0.39: P_F >= 0.390000001000 (the program's float value, planned at the target 0.390000001, is 0.390000001). The program's B is the least multiple of 10^21 for which the float bound reaches 0.390000001 (Appendix A). H1 (Section 5) is the only premise of this entry: it states that the real attempt succeeds at least as often as A_F.

Proof.
Step 0 (notation). A trail is the run of evaluations of one lane between two restarts; a(t) is the number of earlier evaluations of the trail of t (its age); the length of a trail is its number of evaluations. A trail is finished when an evaluation returns a distinguished point (DP; that evaluation is its last), cut when a slice check restarts it at age >= c, open when the halt comes first. Every length is at most M, and a trail of length at most c is never cut. An evaluation is fresh when its input has not been evaluated before. A collision is a fresh evaluation whose value equals an earlier value (an earlier output or a start). The starts r + t' (t' < 2^17) differ from every value the run produces except with probability Q 2^17 / N (r is uniform and independent of F); this event is excluded below and charged in P_tiny, so a non-fresh evaluation exists only after a collision on its trail.

Step 1 (lazy sampling with a lottery). Realise F by independent uniform values V_1, V_2, ...: the t-th evaluation returns V_t if it is fresh and the value stored for its input otherwise. This is the lazy sampling of F for every adaptive choice of the points. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(theta), one per evaluation index, fresh or not; given all of them the V_t are independent and uniform on their class (the theta N DP values, or the N' other values). Index t belongs to lane (t - 1) mod 256, and the lane positions of a lane are its indices in increasing order; the lottery is extended beyond Q by further independent draws (used in the proof only). G_t is the history of the first t evaluations together with the whole lottery; F_t is the history of the first t evaluations together with xi_1, ..., xi_t only.
(L1) If t is fresh and xi_t = 0, then P(V_t = v | G_(t-1)) = 1 / N' for every non-DP value v (and 0 for DP values), and the events for different v are disjoint.
(L2) Whether t is fresh, its input, its batch, its age and the trails before t are determined by G_(t-1).
(L3) The lottery of a lane is i.i.d. Bernoulli(theta); the lanes are independent. Scanning the lanes one after the other, a scan that takes from each lane a number of positions that is a stopping time of that lane (with further independent coins after the run) reads one i.i.d. Bernoulli(theta) sequence.
(L4) N1 = xi_1 + ... + xi_Q is exactly Binomial(Q, theta), so P(N1 >= k) <= e^-q (e q / k)^k <= 2^-40 (Chernoff: the binomial moment generating function is below the Poisson one); P(N1 >= k) is charged once, as 2^-40.
(L5) The run up to evaluation t is F_t-measurable (it depends on V_1, ..., V_t only, and V_s depends on xi_s and an independent uniform). If s is a stopping time of (F_t), the lottery after s is independent of F_s and i.i.d. (strong Markov property of an i.i.d. sequence).

Step 2 (the free run and the first collision). Given the whole lottery xi, the free run is the run in which every evaluation is fresh: the trail boundaries (a DP at every xi = 1, a restart of a trail of age >= c at a slice check), the ages a(t), the lengths and the batches are functions of xi alone, and so are the sets of long trails (a trail is long when its first c coins are all 0, i.e. when it has c evaluations without a DP; the other trails are short, of length at most c, and are never cut) and the numbers rho(y) = the number of evaluations of the lane of y after y up to and including the first with xi = 1. Let n0(t) be the number of s <= t with xi_s = 0. Let tau be the first t with xi_t = 0 whose value V_t equals V_y for some y < t with xi_y = 0 (the first collision of the non-DP class), E1 the event that a start equals a value of the run (Q 2^17 / N), E2 the event that some DP-valued evaluation equals an earlier DP value (on N1 <= k - 1 its probability is at most k^2 L / N': a DP-valued evaluation is uniform on the theta N DP values, at most k - 1 earlier DP values exist, and there are at most k - 1 such evaluations). Outside E1 and E2 the real run is the free run up to tau (every evaluation is fresh), and until then the non-DP values are independent uniform on the N' non-DP values (L1). Hence, for t with xi_t = 0 and y < t with xi_y = 0,
    P(tau = t, V_t = V_y | xi) = Pi_(n0(t) - 1) / N',    sum over y of that = Pi_(n0(t)-1) - Pi_(n0(t)),    P(tau <= Q | xi) = 1 - Pi_(n0(Q)).
On N1 <= k - 1, n0(t) - 1 >= t - k, and Pi_(t-k) <= Pi_(t-1) / (1 - kQ/N') for t <= Q (Pi_(t-1) = Pi_(t-k) times at most k - 1 factors that are each at least 1 - Q/N'; Pi_m = 1 for m <= 1). Pi_m is bounded by exp(-m (m - 1) / (2 N')) from above and by exp(-m (m - 1) / (2 N') - (m - 1) m (2m - 1) / (6 N'^2)) from below (ln (1 - x) >= -x - x^2 for 0 <= x <= 1/2).

Step 3 (a first collision with a good partner is output). Say that the pair (t, y) with tau = t and V_t = V_y is good when (G1) y is not on the trail of t, (G2) b(y) < b(t), (G3) the trail of y is short, (G4) rho(y) <= B - b(t) and a(t) + rho(y) <= c - 1, and that it is undisturbed when no fresh evaluation of the trail of y after t, up to its first DP, is a collision. Claim. On a good undisturbed pair, if the run does not halt early (seventh cut, table full, stage-1 budget, key false match) and is outside E1 and E2, the program outputs a pair. Proof. Let X and Y be the trails of t and y. The input of X after t is V_t = V_y, the input of Y after y, so the evaluations that X performs after t are the evaluations Y performs after y, the j-th of them in batch b(t) + j for X and in batch b(y) + j for Y (Y does not restart before its DP, because its trail is short, hence never cut, and its first DP is the (rho(y))-th evaluation after y). By (G2) Y evaluates each of them strictly before X, so X only repeats points (they are not fresh). Undisturbed: the evaluations of Y after t are fresh and not collisions (those before t are not collisions, tau being the first), so the lottery of the lane of Y decides the DP: Y ends with a DP at its rho(y)-th evaluation after y, in batch b(y) + rho(y) < b(t) + rho(y) <= B (G4), inside the run, and the key of the DP is stored (the table is not full). X repeats it in batch b(t) + rho(y) <= B with the same DP and the same key; X has then done a(t) + rho(y) + 1 <= c evaluations, so no slice check cut it (a slice check cuts a trail of age >= c, and the age before its last evaluation is a(t) + rho(y) <= c - 1). The two trails are different (G1), finished, with the same key, and the inputs of t and of y are different (t is fresh) with g(t) = g(y): Lemma 1 applies. QED.

Step 4 (the pairs that are not good, and the disturbance). Let W(t, y) be the event (tau = t, V_t = V_y) with xi_t = xi_y = 0 and work on N1 <= k - 1 outside E1 and E2. By Step 2, P(W(t, y) | xi) <= Pi_(t-1) / ((1 - kQ/N') N') <= 1 / ((1 - kQ/N') N'), and sum over t of P(W(t, y) | xi) is at most the sum over t of 1 / N', so at most Q / N'. A pair that is not good fails one of the following; each failure is bounded by the expected number of pairs of that kind times the hazard.
(a) (G1) fails: y is among the a(t) earlier evaluations of the trail of t; a(t) is at most g(t), the number of consecutive 0 coins just before t on its lane (g(t) as in Step 6 (ii)), E g(t) <= sum over i >= 1 of (1 - theta)^i <= L - 1, so the failure has probability at most Q L / N' = P_own.
(b) (G2) fails: y is in the batch of t before t, at most 255 pairs per t: 255 Q / N' (charged in P_tiny).
(c) (G3) fails: y is on a long trail. A long trail has at most M evaluations (it is cut at the first slice check at age >= c, or finishes before), a y has at most Q partners t, and the number of long trails is at most the number of successes of the scan of Step 6 (i) (disjoint windows of c coins 0), with expectation at most p (q + 256) / (1 - p) there: M Q p (q + 256) / ((1 - p) N') = P_long.
(d) (G4) fails. rho(y) > B - b(t) means that the B - b(t) coins after y on its lane are all 0 (they lie in the batches b(y) + 1, ..., b(y) + B - b(t) <= B, inside the run), probability (1 - theta)^(B - b(t)) <= e^(-theta (B - b(t))) for each y. By Step 2 the pairs (t, y) with y < t contribute at most sum over t of (t - 1) Pi_(t-1) / ((1 - kQ/N') N') e^(-theta (B - b(t))), and (t - 1) Pi_(t-1) / N' = Pi_(t-1) - Pi_t, so, with b(t) <= ceil(b / 256) for t <= b and the sum of Pi_(t-1) - Pi_t over t in (a, b] equal to Pi_a - Pi_b, at most (1 - kQ/N')^-1 sum over the bins (a, b] (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = P_delay (the bins and the enclosures of Pi are in Appendix A). The second part, a(t) + rho(y) >= c: a(t) <= g(t) and rho(y) >= 1, so it requires g(t) + (rho(y) - 1) >= c - 1. If t and y are on different lanes the two coin sets are disjoint and g(t), rho(y) - 1 are dominated by independent geometric variables with values in 0, 1, 2, ...; the sum of two such variables is at least c - 1 only if a single i.i.d. sequence of coins has at most one 1 among its first c coins, hence among its first c - 1 coins: probability at most (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. If they are on the same lane and (G1) and (G3) hold, y is on an earlier trail of the lane that is short, so it ended with a 1 before the start of the trail of t, and the two coin sets (those of rho(y) up to that 1, those of g(t) after it) are disjoint: the same bound. At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': PP p2 = P_age.
(e) Disturbance. For a good pair let r' be the number of evaluations of the lane of y with index > t up to and including the first with xi = 1; the coins there are independent of F_t (L5, t is a stopping time) and r' is dominated by a geometric variable of mean L. The evaluations of Y after t and before its DP are at most r' fresh evaluations, each a collision with conditional probability at most (Q + 2^17) / N' given the history (L1; the last one, a DP-valued evaluation, is covered by E2, and counting it here only overcounts). For this bound W(t, y) is taken without the restriction to N1 <= k - 1 and outside E1, E2: it is the event (tau = t, V_t = V_y), which is F_t-measurable, so P(W(t, y) and disturbed) <= P(W(t, y)) L (Q + 2^17) / N'; the events W(t, y) for different (t, y) are disjoint (the values V_y are distinct before tau), so the sum of P(W(t, y)) is at most P(tau <= Q) <= sum over t of (t - 1)/N' = PP: PP L (Q + 2^17) / N' = P_dist.

Step 5 (the sum). With P(tau <= Q, N1 <= k - 1) >= 1 - Pi_(Q-k+1) - 2^-40 >= 1 - P_coll - 2^-40 (Pi_(Q-k+1) <= Pi_Q / (1 - kQ/N'): n0(Q) >= Q - k + 1 on N1 <= k - 1 and Pi decreases) and Step 3, the attempt succeeds unless one of the failures (a) to (e) occurs for the first collision, or E1, E2, N1 >= k occur, or the run halts early: P_F >= 1 - P_coll - 2^-40 - P_own - P_long - P_delay - P_age - P_dist - 255 Q / N' - P(E1) - P(E2) - P(early halt). The early halts are charged in Step 6 (seventh cut) and Step 7 (table full, key false match, stage-1 budget).

Step 6 (the cut count and the long trails; no premise). Let K be the number of trails that the run cuts or would cut (the seventh one halts the run, `CMAX = 6`). Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.
(i) K_A. A trail counted by K_A has c fresh evaluations with non-DP outputs at c consecutive positions of its lane, so xi = 0 there; different such trails of a lane use disjoint positions. Scan each lane with trials: a trial starts at the current position u and succeeds if the c positions u, ..., u + c - 1 are all 0 (next trial at u + c); otherwise it fails at its first 1 (next trial after that 1). The scan of a lane stops at the first trial that would start after the run. Inside a maximal run of 0s the trials start at its first position and succeed floor(length / c) times, the largest number of disjoint length-c windows it holds; so K_A on a lane is at most the successes on that lane. Every failure but the last of a lane ends at a 1 of the run, so the failures are at most N1 + 256 <= k - 1 + 256 on N1 <= k - 1. Trial outcomes are independent Bernoulli(p'), p' = (1 - theta)^c <= p = e^(-c/L) (disjoint positions of an i.i.d. lottery; lanes concatenated as in (L3)). All successes therefore occur before failure number k + 256 of an infinite i.i.d. trial sequence, and seven successes before that failure mean seven successes among the first n2 = k + 262 trials:
    P(K_A >= 7, N1 <= k - 1) <= P(Binomial(n2, p) >= 7) = 1 - sum_{j=0..6} C(n2, j) p^j (1 - p)^(n2 - j)
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
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; E[g(t) + 1] <= sum for i >= 0 of (1 - theta)^i = L, so E_S <= Q L / N' = 8.219e-06.
- X: E_X <= sum over pairs e' < t of P(sigma(e') + g(t) >= c) / N'. Different lanes: sigma(e') - 1 and g(t) are independent and dominated by geometric variables on {0, 1, ...}, so the probability is at most P(at most one 1 in c - 1 Bernoulli trials) = (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. Same lane, e' = t - j 256: if a 1 lies between them the two runs of 0s are disjoint and the same bound p2 holds; if the j positions are all 0, the probability is at most (1 - theta)^j T(c - 1 - 2j) with T the tail above (T = 1 below 1); the sum over j of these is at most L e^(-(c - 2)/(2L)) (2 + (c - 1)/L). Hence E_X <= (Q / N') L e^(-(c-2)/(2L)) (2 + (c-1)/L) + PP p2 = 1.591e-05.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^17) / N': E_J2a2 <= (Q + 2^17) L Q (Q - 1) / (2 N'^2). E_J2a = 8.166e-06.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2 = 1.572e-05.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 1.123e-06.
So P(K >= 7) <= P(K_A >= 7, N1 <= k - 1) + P(N1 >= k) + P(K_B >= 1) <= P(Binomial(n2, p) >= 7) + E_S + E_X + E_J2a + E_J2b + E_Y + [P(N1 >= k), charged once as 2^-40]; P(Binomial(n2, p) >= 7) = 2.082e-08 and P_cut = 4.915e-05 (the program's `cut_halt`). There is no premise about K: the number of cut trails is bounded by this argument, and it needs no distribution of K. The bounds on S and J2a are not small (about Q L / N' each); they are the real cost of trails that close a cycle or join a path that is itself disturbed.

Step 7 (the early halts and the small terms). The attempt can end before it outputs the pair of Step 3 only by an early halt or by the events E1, E2, N1 >= k: the seventh cut (P_cut, Step 6); the table full (finished trails are at most N1 + 59 outside 60 or more collisions, so tmax keys need N1 >= tmax - 59: P_table = 6.937e-07); a key false match (P_key = 1.158e-04: the stored ends are at most tmax fresh DP values, uniform on the DP class, and the key space is 2^35 * 1895 = 2^45.89); the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^20 = 3.235e+32: the fresh stage-1 hits are at most the sum of eta_t = 1[low 20 bits of V_t zero], exactly Binomial(Q, 2^-20), above 1.5 mu2 with probability at most e^(-0.108 mu2); the repeated hits after merges come from at most 60 colliding trails, each repeating at most M points that lie in at most 60 lane windows of total length at most M, and every such union of windows holds more than 2 M / 2^20 hits with probability at most e^(-0.386 M / 2^20), so with 240 M <= Q (checked: M = 3.647e+34, Q = 3.392e+38) the repeated hits are below mu2 / 2 except with probability below e^-1000; a recovery with no pair (a key false match, counted, or a start on another trail, 2^-100). The number of collisions: every fresh evaluation with xi = 0 is a collision with conditional probability at most (t - 1 + 2^17) / N' (L1), so E w^(number of collisions) <= exp((w - 1) H) for w = e^5 (the factor per evaluation is at most 1 + (w - 1)(t - 1 + 2^17)/N' <= e^((w-1)(t-1+2^17)/N')), and P(60 or more collisions) <= exp(-300 + (e^5 - 1) H). P_tiny collects Q 2^17 / N (E1), k^2 L / N' (E2), 255 Q / N' (Step 4 (b)), exp(-300 + (e^5 - 1) H), and 2^-90 for everything else of this step (the stage-1 budget, the recovery with no pair) and for the rounding of the factors 1 - kQ/N' and of the enclosures of Pi (each below 2^-96). This proves the lemma. QED.
Consequently P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny = 1 - 0.608492991 - 0.00128408 - 8.219e-06 - 2.926e-05 - 1.572e-05 - 4.083e-06 - 4.915e-05 - 9.1e-13 - 1.158e-04 - 6.937e-07 - 2^-90 = 0.390000001 (float, planned at 0.390000001; the printed terms are rounded), and the exact certificate of Appendix A is 0.390000001000 >= 0.39 (B is the least multiple of 10^21 that reaches the planning target).

Sensitivity to H1 (d). If the hazard of a collision is (1 - eps) / N instead of 1 / N (clause (d) of H1; the same sensitivity as a deficit eps of the pair-collision rate in clause (a)), the plan of this program (same lemma with N / (1 - eps)) needs, to restore 0.39: 0.0073 bit for eps = 0.01 (Tp 1885); 0.0370 bit for eps = 0.05 (Tp 1847); 0.0760 bit for eps = 0.10 (Tp 1798); 0.2076 bit for eps = 0.25 (Tp 1641).

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function g and about one attempt; it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved: an assumption, no proof is known. Its content, in the terms Lemma 2 uses, is four clauses: (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of g from the starts r + t have the first-collision law of a random mapping; (c) whether an iterate is a DP is independent of the collision events and has probability 1895 / 2^122; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of g; clause (d) is that this adaptivity does not lower the collision hazard, that is, for every fresh evaluation, given the whole history of the run and which later outputs are distinguished points, the output equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard that F has by construction, L1 of Section 4). Lemma 2 proves the bound for F from the hazard alone (a supermartingale over the evaluations, no conditioning on which trails finish), and (d) is the premise that g has that hazard. Nothing else in the success bound is heuristic: Lemma 1, the lazy-sampling facts, the supermartingale, the counting of pairs, the Chernoff bounds and the cut count are proved in Section 4 for F; Sections 3 and 7 are counts of the program. Sensitivity: a hazard (1 - eps) / N costs the same as a deficit eps in clause (a): 0.0073 bit for eps = 0.01, 0.0370 bit for eps = 0.05, 0.0760 bit for eps = 0.10, 0.2076 bit for eps = 0.25 (Section 4). The only evidence for (a) to (d) is the program checks of Section 6 and the toy runs below.
Support of H1 (stated; it is not measured at width 256). (1) It is the generic premise of parallel collision search with distinguished points (van Oorschot and Wiener, J. Cryptology 12 (1999) 1-28): a fixed compression function, iterated from fresh starts with no chosen input difference, is modelled by a random function. The generic entries of this track rest on it; on the board, with status review: bfcaad61 and a5707aa9 (round 40), 3017c952 (round 51), 1884db5b (round 57), 3642e1cd, 6b678689 and 4684dfc2 (round 64; 4684dfc2 is the source of walk B), and d4f8f4e4 to 05004d0b (rounds 40 to 53) with this H1. (2) Clause (d) fails only if g, along its own iterates, collides less often than a random function by a constant factor 1 - eps; that is a property that separates 40-step SHA-256 from a random function. This entry uses no differential property. (3) A deviation that raises the hazard only helps; a deficit eps is priced in Section 4.
The two organizer experiments (Section 6) are program checks: the organizer recomputes the complete two-block digest of every returned pair. Because the walk g(x) = f(x) XOR q differs from bfcaad61's only by the invertible Maj-shear on Q, the OR-shear on X, and the constant output mask q (all inverted exactly by `enc_invert` and `DigestNet` before forming the complete two-block digest), the width-16 digest walk g16(x) and full-width digest evaluations in `bssha-n16` and `proj-k0-w256` are functionally identical on the target digest; the official remote organizer evaluation executes both experiments in its isolated Docker sandbox and records the verified counts (reference values for 256 independent uniform 16-bit values per trial: P(a pair) = 1 - prod_{i<256} (1 - i / 2^16) = 0.392678, 100.53 of 256 trials; mean number of equal pairs C(256, 2) / 2^16 = 0.498047 per trial, 127.50 over 256 trials; in bfcaad61's run of the same digest walk: `bssha-n16` returned 198 of 256 verified pairs with 58 halts, and `proj-k0-w256` returned 98 of 256 verified pairs with 121 total equal pairs).
Every unsuccessful attempt of the width-16 experiment ends with a halt of the program (the halts equal the unsuccessful trials). At width 16 a halt "recovery found no pair" (a trail start lying on another trail) is frequent; at width 256 it has probability below 2^-100 (Section 4).
Not tested: the full 256-bit functional graph; iterations of length above 2^40; the bit-sliced search above width 36. A deviation of g from H1 that raises the collision rate only helps; one that lowers it by eps costs the extra time of Section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/bssha.py` (it dispatches on the experiment id; standard library only). In both, the complete digest of a returned message is what the organizer recomputes: the 64-byte message, padded to two blocks.
`bssha-n16`: per trial, one attempt of the 256-lane search at width 16 (DP = low 2 bits zero, plan(16): 7 batches, cut rule, table, recovery) on the walk g16(x) = the low 16 bits of the complete digest of M(x), x < 2^16. Each batch runs the shipped program on the 256 planes (the 240 high input planes zero), then the experiment's digest network (`DigestNet`, bit-sliced, experiment code only, not in the ledger) inverts walk B, forms cv1 = IV + state and runs block 2; the recovery runs the rolled recovery program and the same inverse and block 2 in scalar form. The trials run side by side: the planes of trial i occupy bits 256 i to 256 i + 255 of each word, so one pass of the program and of the digest network serves every live trial, and each bitwise record acts on every trial's 256 bits alone. The trial returns M(x), M(y) when the attempt succeeded and two nulls otherwise. Checked event: the messages are distinct and their complete 40-step digests agree in the low 16 bits. This is exact, because at width 16 the walk is those 16 digest bits. The width-16 walk differs from the width-256 walk g only in the map after the program (inverse, block 2, low 16 bits); it runs the same program, search, table and recovery.
`proj-k0-w256`: per trial, 256 points at width 256 (source by trial index mod 3: uniform from the seed, counter r + i, iterates of g from 256 seed-derived starts) evaluated with the shipped program; their complete digests are formed by the digest network; the trial returns two points whose digests agree in the low 16 bits when the set holds such a pair. Checked event: as above. It checks at full width the program, the inverse of walk B, the chaining value, block 2 and the message construction.
They do not measure the cost or the success probability at width 256; the counts are program checks, not estimates.

## 7. Memory

Table: 123,050 slots * 47 bits = 722,919 bytes (the table region is empty until the search starts). Slot t belongs to trail number t: its position is the trail number, so the number is not stored (the index layout of Hong, Lee and Ma, eprint 2011/387, Section 2; Trimoska, Ionica and Dequen, eprint 2017/581). A slot is the key (46 bits) and a written bit, no length (recovery pass 1 recomputes it); `_search` of the program writes and scans the slots.
Code: 43,648 body records * 5 bytes (an opcode and three 10-bit register fields, no immediate: the convention of Section 3.1) = 218,240 bytes, plus 1,646 other instructions * 36 bytes (opcode, registers and an inline 256-bit immediate; stage 1 22, batch loop 3, handlers 1,000, recovery 461 = 414 + 47, setup, cut and slice 160) = 59,256 bytes: 277,496 bytes in all.
Counters and copies: 16,384 bytes (trail numbers 768, birth batches 4,096, counters, and the 8,192-byte copy of the 256 planes used by the handlers). The 929 registers (the 926 data registers the program uses and three pointers), counted as memory: 29,728 bytes. The array of the rolled recovery program (the 40 schedule words W0..W39 and 24 constants K10..K33, one 32-byte word each, 64 words): 2,048 bytes. No advice. Memory peak = max(setup phase 518,849, search phase 1,048,575) = 1,048,575 bytes <= 2^20 = 1,048,576; the preprocessing is inside the setup phase. Claim `memory_log2_bytes` = 20. `python3 bssha.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor(8 (2^20 - 277,496 - 29,728 - 16,384 - 2,048) / 47) - 262 = 122,788, and Tp = 1895 is the plan of Appendix A: the mean number of trails is the largest that the table holds with a capacity tail below 2^-20, and Tp is the largest integer (found by bisection; any Tp is a valid plan) for which the success bound of Section 4 reaches the planning target 0.390000001 at that mean (Appendix A computes both and certifies P_F >= 0.39 in exact arithmetic).

## 8. Heuristics, conventions and what is credited

The premise of this entry is H1 (the model premise of Sections 4 and 5, clauses (a) to (d), score-critical); the machine prices (the 929-register file; the 5-byte price of a body record with no immediate operand, every other instruction 36 bytes; every NOT, move, load, store and loop-control record charged one operation) are the declared cost model of Section 3.1, not a heuristic. Lemma 2 proves the cut count (no cut-count heuristic); its form (bounded restart, the detection delay integrated) is that of 76ab339a and 09fe5fcd on the blake3 lane. There is no advice and no polarity search; the prefix W0..W7 is a fixed constant of the program, computed in closed form.
Credited (all dependencies, same challenge): 4ab23c0a, bfcaad61, a5707aa9 and 87cb17fa (the two-block layout, search, index-layout table, handlers, ledger method, the unrolled kernel, its allocator and C generator, the rolled recovery, the experiments' form); mitchuski's 4684dfc2 and 1884db5b (walk B, Sections 1 and 3.2); lamb356's 3642e1cd (carry-in absorption of the folded constant, Section 3.2); dariolina's 6b678689 (the 5-byte body price and the full unroll, Section 3.1); dariolina's 744875ec (no feed-forward and the zeroing prefix, Sections 1 and 3.2); lamb356's 44870635 and sraiw's 38912d66 (two-block messages on this lane, Section 1). Also credited, on other lanes and not declarable: mitchuski's 1b7bd746 (pair-carry templates T0/T1), jungjipdo's 6ae36351 (the pivot full adder) and 0a9640ed / 62cfd777 (the bit-sliced chain and declared register file).

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate, and `certify` recomputes the bound of Lemma 2 in exact rationals and 60-digit decimals with outward rounding: the line `P_lower certified` is a proved lower bound on P_F, asserted >= 0.39. The same numbers come from `python3 bssha.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 43648, 22, 3, 256      # records executed per batch (setup excluded), stage-1 test, loop control, lanes
GEN_CALLS, INSTR_REC = 185312, 43648            # generator primitive calls of both passes of the network (python3 bssha.py --ledger), records of the program
PH7, EXTRA, RECINIT = 1424, 39, 65              # records executed per call of the rolled recovery program, extra operations per recovery batch, records executed once per recovery
N_BITS, S1, W, KAPPA = 256, 20, 102, 13         # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 6
INSTR, OTHER_CODE, REGFILE, COUNTERS, ADVICE, ARRAYS = 36, 1621, 29728, 16384, 0, 2048
KEYB = 46                                             # key bits
SLOTB = KEYB + 1                                # a table slot: the key and a written bit; the slot index is the trail number
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 21, 17                        # B is a multiple of GRAIN; trail numbers are below 2^17
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP                                        # one batch = 43,673 operations
code_bytes = INSTR_REC * 5 + (FILT + LOOP + OTHER_CODE) * INSTR     # the body records once at 5 bytes, every other instruction once at 36 bytes
tmax = 8 * ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE - ARRAYS) // SLOTB - LANES - CMAX  # stored trails: one slot per trail number (LANES starts + tmax + CMAX cuts)
table_bytes = -(-(tmax + LANES + CMAX) * SLOTB // 8)
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
    lo, hi = 1.0, float(tmax - 59)
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail_log2(mid, tmax - 59) <= -15.5 else (lo, mid)
    q_hi = lo
    lo, hi = 1.0, q_hi
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
    assert Fraction(Q, 1 << S1) * Fraction(108, 1000) > 1000 and 240 * M <= Q   # stage-1 budget (Step 7): below e^-1000, inside the last term
    return 1 - sum(terms)


lo, hi = 1.0, float(tmax - 59)                                 # the largest mean number of trails the table holds (tail within 2^-20)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax - 59) <= -20 else (lo, mid)
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
        ("finished trails: tmax * (3800 + 6 * (tmax + 262))", tmax * (EVENT + 6 * (tmax + LANES + CMAX))),
        ("cut trails: 6 * 4200", CMAX * CUTOPS),
        ("recovery: 2 (c + 2^48) * (%d + 39) + 600 + %d" % (PH7, RECINIT), 2 * capr * (PH7 + EXTRA) + 600 + RECINIT),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", table_bytes + code_bytes + REGFILE + COUNTERS + ADVICE + ARRAYS)
print("P_lower = %.5f" % plower(Tp, float(B * LANES / L)))
pc = certify(Tp, B)
print("P_lower certified (exact rationals, 60-digit decimals) = %s" % str(pc)[:14])
assert pc >= Fraction(39, 100)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 2896
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
Tp = 1895  tmax = 122788  B = 1324927806732699000000000000000000000  e2max = 646937405631200683593750000000064  c = 36474857931828826063851169991861699
memory bytes = 1048575
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000001000
main loop: B * 43673                                 57863572103437163427000000000000000000000
slice checks: ceil(B / 2^48) * 1300                  6119215885123128018108800
stage-1 hits: e2max * 2800                           1811424735767361914062500000000179200
finished trails: tmax * (3800 + 6 * (tmax + 262))    91120974800
cut trails: 6 * 4200                                 25200
recovery: 2 (c + 2^48) * (1424 + 39) + 600 + 65      106725434308531145063652119178042711395
setup and generator                                  46605600
N = 57972108962481468053193599742397228604995
certificate: 2^12391263 * 2896^100000 <= N^100000 < 2^12391264 * 2896^100000
log2(N/C) = 123.9126368773
time_log2 = 123.91264
```
