# sha256-r40: a 43,647-record bit-sliced birthday walk

This package is a credited derivative of a4c6ba2c-25e0-4d35-80e9-ae2ea22eb05d, d22ae1b2-2368-460a-b6d4-1e5e37ceb735, and 95263e47-d61b-43a6-bb46-30ced2488280. It keeps a4c6ba2c's 40-step walk, carry absorption, polarity-matched tail shears, 926-register allocator, stage-1 split, rolled recovery, random-function proof, and experiments. The round-64 lineage supplies the charged whole-network addition selector, recent-XOR cancellation rule, compact bounded-emitter structure, and the rule that every search which fixes a program constant is charged.

The scored changes are small and mechanical:

- A whole-network selector sweep tests every admissible three-of-n reduction and pair-first four-word reduction at all 60 multiword-addition sites. Only site 33 wins. Its fixed mask `7` reduces the frontier kernel from 43,648 to 43,647 records. The charged search has one baseline and two complete passes over 182 alternatives, or 365 complete builds. Section 3.2 derives the `2^48`-operation bound for each build.
- The six-offset search evaluates 64 endpoint choices, one initial coordinate point, three complete 192-bit coordinate passes, and 1,000 fixed-seed perturbations. None beats the frontier offsets. These categories total exactly 1,641 complete builds, each charged at `2^48` operations.
- A body record is exactly 32 bits: a 2-bit opcode and three 10-bit register fields. The kernel uses only XOR, AND, and OR and register indices at most 925. All control and recovery records use a separate fixed 5-byte format. The recovery format has a 4-bit opcode and three fields below 10 bits; the general control format has a 5-bit opcode and three 10-bit fields.
- The trail-index table stores `key + 1` in a 48-bit slot. Zero is the unwritten sentinel, so no written bit is needed; the slot position is the trail number. At the final plan the maximum key is 281,474,976,708,660, hence `key + 1 < 2^48`. The table holds 136,004 completed trails in 136,266 total slots.
- The compact freestanding C emitter embedded as `GEN_C` is the normative setup program. Its two passes enforce 43,905 nodes, 43,647 records, 926 data registers, 1,024 CSE slots, and all packed-field boundaries. It emits 174,588 bytes with SHA-256 `885c76492ea4caa497752afad7ae041f334bb55f1b776df41e7a50ae68f9b338`. The organizer runs the byte-exact Python mirror before every experiment. The ordinary builder runs in `--selftest` and must reproduce the same bytes.

The resulting kernel has 34,228 XOR, 5,791 AND, and 3,628 OR records, with no NOT, move, set, load, or store. Stage 1 and loop control add 25 operations, so one batch costs 43,672 operations. The exact ledger is

```
N = 57943024946780646873611801817502375963436 word operations
log2(N / 2896) = 123.91191291
```

The claim rounds upward to `time_log2 = 123.91192`. Search memory is 1,048,574 bytes, setup memory is 520,395 bytes, and the memory score term is zero. The circuit changes are exact Boolean and modular-arithmetic equivalences checked by the self-test. They are not premises. H1, the fixed-function random-function comparison stated in Sections 4 and 5, remains the only score-critical premise.

## 1. Target and relation

Target `sha256-r40-prefix-v1` (the Pareto lane `sha256`, round 40). The two colliding messages have 64 bytes each. With x a 256-bit integer and y0..y7 its eight 32-bit words (big-endian, y0 the highest), M(x) is the 16 big-endian words W0..W15 with
- W0..W7 = the constant words 3e73281c, 752d8ed2, ad19eff1, 7250fceb, d4095422, 44fdb519, 43f22c5b, d8d6aac4 (Section 3.2 gives how they are computed),
- W8 = y0, W9 = y1, and W(8+k) = y_k - K(8+k) modulo 2^32 for k = 2..7.
FIPS 180-4 padding appends 0x80, 55 zero bytes and the 64-bit length 512: the padded message is 128 bytes, two blocks, and block 2 is the same for every x. The target runs the steps 0 to 39 on each block, block 1 from the standard IV and block 2 from the chaining value cv1 = IV + s(x) word by word, where s(x) is the working state after step 39 of block 1; the digest is the result of block 2 with its feed-forward (`verifier/hash_functions.py:digest(M(x), "sha256", 40)`). The profile's message domain is "finite byte strings of bit length below 2^64"; a 64-byte string is in it.
Write a_i, e_i for the a and e words after i steps of block 1 (a_0, e_0 from the IV), T1_i for the T1 of the step that produces them and W_j for the schedule word of step j. With the fixed 32-bit polarity masks `QM = 0x74a40866` and `XM = 0x46eb57e6`, f(x) is walk B (4684dfc2) with per-bit polarity-matched disjoint-support shears on Q and X: the eight words e_(40-3), e_(40-2), X = e_(40-5) + Ch(e_(40-2), XM, e_(40-4)) + W_38 (at bit j: `e_(40-2)[j] | e_(40-4)[j]` when `(XM >> j) & 1 == 1` and `~e_(40-2)[j] & e_(40-4)[j]` when `(XM >> j) & 1 == 0`; since `Ch(e2, e3, e4) = Ch(e2, XM, e4) + (e2 & e3 & ~XM) - (e2 & ~e3 & XM) mod 2^32`, the inverse adds `(e2 & e3 & ~XM) - (e2 & ~e3 & XM)`), T1_(40-4), Q = T1_(40-5) + Ch(a_(40-6) ^ a_(40-7), a_(40-8), QM) (at bit j: `~(a_(40-6)[j] ^ a_(40-7)[j]) | a_(40-8)[j]` when `(QM >> j) & 1 == 1` and `(a_(40-6)[j] ^ a_(40-7)[j]) & a_(40-8)[j]` when `(QM >> j) & 1 == 0`; since `Maj(a6, a7, a8) = Ch(a6 ^ a7, a8, QM) + (a6 & a7 & ~QM) - (~a6 & ~a7 & QM) mod 2^32`, the inverse adds `(a6 & a7 & ~QM) - (~a6 & ~a7 & QM)`), a_(40-6), a_(40-7), Y = e_(40-4) + W_39, in this order (permutation (6, 1, 7, 0, 5, 4, 2, 3) of bw, the order with no register move, Section 3.2), as a 256-bit integer. These words determine s(x): the program's `enc_invert` recovers a_(40-5) = Q + (a_(40-6) & a_(40-7) & ~QM) - (~a_(40-6) & ~a_(40-7) & QM) + Sigma0(a_(40-6)), then a_(40-4), a_(40-3), a_(40-2), the T1 of steps 38 (= X + (e_(40-2) & e_(40-3) & ~XM) - (e_(40-2) & ~e_(40-3) & XM) + Sigma1(e_(40-2)) + K_38) and 39 and the whole state, by additions, subtractions and the round functions. The walk is g(x) = f(x) XOR q, q a fixed 256-bit mask (127 output planes that the generator leaves complemented instead of spending a NOT).
So g(x) = g(y) gives s(x) = s(y), hence the same cv1, the same block 2 and equal digests. x != y gives M(x) != M(y), since x -> W8..W15 is a bijection. The attack outputs two distinct 64-byte messages with equal complete 256-bit digests.
The selftest (`python3 bssha.py --selftest`) compares the program with scalar g on 2,560 lanes, including all-zero and all-one inputs, checks four chained steps, checks the inverse on 10,000 random states, checks the recovery program and experiment digest network, and runs six width-16 search attempts. It also runs the independent ordinary builder and requires byte equality with the normative bounded emitter.

### 1.1 Why the 39-step differential characteristic does not extend to 40 steps
In the 39-step collision attack (`44870635`, `7c4da9b7`) based on Table 23 of ePrint 2026/1120, the 19-step local collision spans steps r = 8..26 with active message words {8, 9, 10, 11, 12, 16, 17, 24, 26}, giving dW_r = dA_(r+1) = dE_(r+1) = 0 for the 12 steps r = 27..38. At step r = 39 (the 40th step), W_39 = sigma1(W_37) + W_32 + sigma0(W_24) + W_23 has dW_37 = dW_32 = dW_23 = 0, while step 24 requires dW_24 = 0x03010000 != 0 to cancel dh = dE_21 = -0x03010000. Because sigma0(x) = ROTR^7(x) ^ ROTR^18(x) ^ (x >> 3) has full F_2-rank 32 (is a bijection on {0,1}^32), dW_39 = sigma0(W'_24) - sigma0(W_24) != 0 with probability 1 for all 2^32 values of W_24. Shifting the local collision by +1 step (r = 9..27) moves offset d = 7 from the free initial word W_15 to the recurrence word W_16 = sigma1(W_14) + W_9 + sigma0(W_1) + W_0, forcing nonzero differences in W_0, W_1 or W_14 and activating steps 0..1 from the fixed IV. Thus 40-step SHA-256 remains in the generic birthday regime.

## 2. The attack (program `experiments/bssha.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished when its low 20 bits are zero and the 102-bit number F = (x >> 20) mod 2^102 is below Tp = 2101. Thus D = 122, theta = 2101 / 2^122, and L = 1 / theta = 2^110.96314. The key is the 36 bits of x above bit 121 followed by the 12-bit encoding of F. It has 48 bits; F < 2101 < 2^12.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated program of Section 3.2. The start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 20 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask, the lane is extracted and the window test F < Tp decides whether it is a DP. If `key + 1` is in the table, go to step 6. Otherwise write `key + 1` into 48-bit slot t and start the next trail in that lane. Zero is the unwritten sentinel. The slot position is t, so neither t nor the length is stored.
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = ceil(13 L) batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 136,004 keys, when a seventh trail would be cut (`CMAX = 6`), or if step 6 finds no pair.
6. Recovery. Pass 1 recomputes the stored trail length. The two trails are aligned, then stepped together until their next values agree. The first predecessor pair a != b with g(a) = g(b) is returned. The rolled two-lane program has 414 fixed 5-byte records, 65 initialization records, and executes 1,424 records per call. Each pass runs at most capr = c + S calls.
Constants printed by `--ledger`: Tp = 2101, L = 5316911983139663491615228241121378304 / 2101, B = 1324531803055719000000000000000000000, Q = 256 B, e2max = 646744044460800292968750000000064, c = 32898551061787541832935729240636801, capr = 32898551061787541833217204217347457, and tmax = 136,004. The 136,266 total slots cover 256 initial trails, all stored trails, and six cut trails. The maximum trail number is 136,265 < 2^18; the boundary test asserts it.
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is a constant of the program).

## 3. Operation ledger

### 3.1 Machine
Machine model of this entry (declared cost-model prices). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices operations and memory; it gives no register count and no instruction size.
This entry declares a load/store machine with 256-bit words and 929 registers (the 926 data registers that the shipped allocator uses and three pointer registers). Charged, one operation each: every XOR, AND, OR and NOT of a 256-bit register, every register move, every set of a register to a constant, every load and store, every pointer addition, comparison and conditional branch, and the one random word. Nothing is free except the renaming of a bit-sliced rotation, and nothing is executed that is not a record of the program. The operation ledger is the exact count of the records of the submitted program, listed by `python3 bssha.py --text` and counted by `--ledger` (Appendix A); the organizer can regenerate it.
Fixed record formats are a declared machine price. The 32-bit body record is this machine's native fixed-width instruction, not an encoded stream interpreted by another program. The native instruction has a 2-bit opcode and three 10-bit register fields. Opcode values 0, 1, and 2 mean XOR, AND, and OR; 3 is reserved. The machine fetches and executes each instruction directly for the same one-operation price used by the accepted 5-byte native format. There is no normative decoder, dispatch loop, or extra register-file access program. Python methods `Prog.run`, `Prog.compile`, and `Prog.fast` are experiment and self-test mirrors only; none is executed in the priced search path. All 43,647 kernel instructions use the native 32-bit format, so the body occupies 174,588 bytes. Recovery instructions use a native fixed 40-bit format with a 4-bit opcode and three 10-bit fields. The recovery program uses 13 opcodes and its largest field is 63. Other control instructions use a native fixed 40-bit format with a 5-bit opcode and three 10-bit fields. Constants live in the counted constant and counter arrays; no instruction contains an inline 256-bit immediate. Every executed instruction costs one word operation.

### 3.2 One batch = 43,672 operations for 256 trails
Representation: a 32-bit word is 32 planes; plane j holds bit j of the word of every lane. A rotation is a renaming of planes. The sum of two words is a ripple of full adders over the planes. The full adder is the pivot adder of 6ae36351 (`Gen.fa`): each signal is a (node, polarity) pair, so complements are free; with three variable inputs, two share a polarity and the third is the pivot p: sum = u XOR y, carry = (u AND (y XOR p)) XOR p with u = x XOR p, 5 gates. With constant inputs the gates fold at build time.
Constants fold at build time: in a sum of several words (`Gen.addm`) the constant words are added first at no cost, then `add3` and ripple adders reduce the variable words; carry-ins into `add3` (up to 2 per `add3` call) and into `add` (1 per `add` call) subtract `bb` from the constant `cv` at zero extra gates so that `cv - bb` has the most trailing zeros, and the remaining constant `cv - bb`, if nonzero, is one more adder. When `cv - bb != 0`, `Gen.addm` also records the pre-constant variable sum `s_k = W[k] - (cv - bb)` in `g.split` so downstream rounds (`i = 17, 19, 21, 23`) can fold `cv - bb` directly into `K[i]` or the next schedule constant (`-20` gates). A gate whose two operands are the same two input planes as an earlier gate is not built twice (a node table; the first XORs of sigma0(W8) are those of Sigma0(a_9), since a_9 = y0).
Pair-carry path (`Gen.add3(A, B, C, cin)` for `cin in {0, 1, 2}`): a sum with three or more variable words takes three words at a time in one ripple whose carry between columns is a pair of planes (u, U) standing for U ? 1 : 2u. At bit 0: for `cin = 0`, `(s[0], U) = fa(A[0], B[0], C[0])`, `u = ZERO` (5 gates at bit 0, 8 at bit 1); for `cin = 2` (adding +2), `(s[0], c0) = fa(A[0], B[0], C[0])`, `u = ONE, U = ~c0` (5 gates at bit 0, 8 at bit 1); for `cin = 1` (adding +1), with pivot `p` and equal-polarity pair `x, y` among `(A[0], B[0], C[0])`, `u0 = x ^ p, s[0] = u0 ^ ~y, u = p, U = u0 | (y ^ p)` (4 gates at bit 0, 9 at bit 1). In all three cases bits 0..1 take 13 gates total. A column of bits 1 to 30 takes the three addend bits x, y, z and the incoming pair (u, U) and returns the sum bit and the outgoing pair by one of three 9-gate templates: (T0) `n5 = z ^ U, n9 = x ^ n5, s = y ^ n9, n6 = x ^ y, n8 = U | (z ^ u), n11 = ~n6 & n9, u' = n5 ^ n11, U' = n8 ^ n11`; (T1) `w = y ^ U, n8 = z ^ w, s = x ^ n8, n6 = U | (y ^ u), u' = n6 ^ w, U' = n6 ^ (n8 & (x ^ w))`; (T2) `w5 = x ^ y, w6 = z ^ w5, s = U ^ w6, w9 = u ^ w6, w10 = U | ~w9, w11 = w5 | (x ^ z), u' = w6 ^ ~w10, U' = w10 ^ ~w11`. All three satisfy `x + y + z + val(u, U) = s + 2 val(u', U')` on all 32 input rows. T0 and T1 cover all cases where at least one addend bit has polarity `U[1] ^ u[1]`, while T2 covers `x[1] == y[1] == z[1] != (U[1] ^ u[1])` because `w5 = x ^ y` and `x ^ z` both have polarity 0 and `~w9` has polarity `U[1]`. Every column is therefore 9 gates (8 at bit 1 when `u` is constant and at bit 30 where only `U'` is built, 3 at bit 31: **276 gates** per `add3`, with zero 10-gate penalty columns), and the template/permutation is selected in O(1) directly from the input polarities.
The program is ONE straight network (`_net_u`), with no loop, no load, no store:
- The message words: W0..W7 are constants; W8, W9 are the chain words y0, y1 (registers 256..511 hold the chain value: plane j of x is in register 256 + 32 (7 - j div 32) + j mod 32); W10..W15 are y_k - K(8+k), one adder each with the constant folded in, used only by the schedule. W_i for 16 <= i <= 37 is built right before step i; at i = 38, 39, `W[i]` pre-reduces `(W[i-16], s0(W[i-15]), W[i-7])` via `add3`.
- The prefix: W0..W7 are chosen step by step from the IV so that a_1 = K9 - K8, a_2 = -K9, a_3 = ... = a_8 = 0 (`_anchor_prefix`: each W_i sets the next a to the anchor). So e_5 = K9 - K8, e_6 = -K9, e_7 = e_8 = 0, steps 0 to 7 are constants (no gate), step 8 has T1 = e_5 + Ch(0, 0, e_6) + K8 + W8 = y0, and step 9 has T1 = Sigma1(y0) + y1: K8 and K9 cancel, and K + W = y enters steps 10..15 directly.
- A full step does T1 = h + Ch + Sigma1 + (K + W) - delta (`delta in {0, 1}`) with `u = h XOR Ch = (h XOR g) XOR (e AND (f XOR g))` and `_add_u(g, h, u, cin_u)` (`c_0 = h[0] & ~u[0]` for `cin_u = 0`, `c_0 = h[0] | u[0]` and `s[0] = ~u[0]` for `cin_u = 1`), so `Ch` and `B_fix` are never built; `Maj = a & b` at step 10 (where `c = a_8 = 0`) and `((a XOR b) AND (b XOR c)) XOR b` otherwise, sharing the previous step's `a XOR b`; `new e = d + T1 + delta`, `new a = T1 + Sigma0 + Maj + delta`. The full steps are 0 to 33.
- The last six steps form walk B (Section 1): `T5 = T1_(40-5) - 1`, `e_(40-5) = a_(40-9) + T5 + 1` and `Q = T5 + Ch(a_(40-6) ^ a_(40-7), a_(40-8), QM) + 1`; `T4 = T1_(40-4)` and `e_(40-4) = a_(40-8) + T4`; `e_(40-3)` and `e_(40-2)` via 5-word `addm(a, h, _ch_direct, Sigma1, K, W)`; `X = addm(W_38_part, s1(W_36), e_(40-5), Ch(e_(40-2), XM, e_(40-4)))`; `Y = addm(W_39_part, s1(W_37), e_(40-4))`. No T2 and no new a is formed in these steps.
- The allocator is a streaming register allocator: short-lived non-output nodes borrow idle output targets that die before their output nodes arrive, while longer-lived nodes take a dying operand register or the lowest free non-target register. The output planes go to registers 256..511. Permutation `(6, 1, 7, 0, 5, 4, 2, 3)` gives zero output moves. The program peaks at 926 live planes and uses 926 data registers.

The six offsets are preprocessing output. Their deterministic search evaluates exactly 1,641 complete candidates: 64 endpoint placements, one initial coordinate point, three complete sweeps of 192 bits, and 1,000 perturbations from the fixed xorshift seed `6a09e667bb67ae85`. Bits are visited by increasing word and then increasing bit. A strict improvement replaces the incumbent, so ties retain the earlier candidate.

The addition selector is also preprocessing output. Among the 60 nonconstant `addm` sites, 32 have exactly three operands and admit one three-of-three reduction. Fifteen have four variable operands and admit four three-of-four reductions plus six unordered pair-first reductions. The remaining 13 sites have fewer than three operands, a forced carry plan, or six operands and admit no selector alternative. One complete pass therefore has

```text
32 * 1 + 15 * (4 + 6) = 182 alternatives.
```

The search evaluates the all-zero baseline, all 182 alternatives in the first pass, and all 182 alternatives again after site 33 becomes the incumbent. The second pass finds no further strict improvement. The exact count is `1 + 2 * 182 = 365` complete builds. Mask 7 at site 33 is the only retained choice and changes the full allocated network from 43,648 to 43,647 records.

Both searches use a count-only builder with an eight-probe CSE table and an eight-entry recent-gate ring. One complete build has at most two builder passes, 160 multiword sums, 64 first-triple masks per sum, 32 columns, 13 current-column forms, 13 lookahead forms, and 12 trial gates per form. Charging 1,024 word operations for each trial gate, including lookup, rollback, and bookkeeping, gives

```text
2 * 160 * 64 * 32 * 13 * 13 * 12 * 1024
= 1,360,967,761,920 < 2^41 operations.
```

One more copy covers the rest of the network, scoring, comparisons, loop control, and deterministic candidate generation. The package charges `2^48` operations per complete build, more than 128 times that doubled structural bound. The exact search charges are

```text
offsets:  1641 * 2^48 = 461900436782186496 operations
selector:  365 * 2^48 = 102738366499389440 operations.
```

These bounds follow the loops and fixed array limits. They do not rely on a development call counter or an unshipped trace.

Executed per batch: 34,228 XOR + 5,791 AND + 3,628 OR = 43,647 gates; zero NOT, set, move, load, store, or control records. Per trail this is 170.496 operations.
Validation is by the bounded emitter, its stream hash, the independent builder comparison, the exhaustive algebraic checks inherited from the frontier, and the scalar and end-to-end tests described in Sections 1 and 6.
The generator runs once at the start; its work is charged in the setup row (3.3), its code and peak storage in Sections 3.6 and 7.

### 3.3 Loop, stage 1, handlers and the other events
One batch: 43,647 body records + stage-1 test 22 + loop control 3 = 43,672 operations. Stage 1 uses 19 ORs, one NOT, one comparison, and one branch. A DP has all 20 low bits zero, so its lane is flagged.
Loop control of the batch loop: counter increment, compare with the next slice limit, branch back: 3 operations.
Handlers are charged per event at the stated operation bounds and stored as fixed 5-byte control records:
- Stage-1 hit: store the 256 planes to an 8 KiB copy (256 stores), extract the lane (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (at most 15), counters. Below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail: key formation, sentinel encoding, the slot write, the new start, insertion of its 256 bits, reload of the planes, lane arrays, and counters fit below 3,800 operations. The key scan is charged six operations per slot, including extraction, comparison, and branch. The source increments the counter and scans before its `finished > tmax` halt, so the ledger charges `tmax + 1` handled events. At most `tmax` keys are stored.
- Slice check (every 2^48 batches): charged **1,300** each. Cut trail: charged **4,200**; at most 6 cut trails (`CMAX = 6`).
- Recovery program (`RecProg`): a second program evaluates g for two chain values at once, in bits 0..31 and 128..159 of each word. The message and constant array has 64 words, or 2,048 bytes. A fused six-iteration loop computes W16..W39 and rounds 10..33; the walk-B tail is straight code. There are 414 fixed 5-byte records, 65 initialization records, and 1,424 executed records per call.
- Recovery batch: one call (1,424 records) plus the exact equality test of the two lanes on the 8 output words (26 operations; in pass 1 the DP test of lane 0, at most 26), loop control 3, call and return 2 and 8 moves: 39 per recovery batch (1,463 per batch), the same in both passes.
- Setup and emitter: one random word; 256 inserted starts; counters; fixed work 813,600. Section 3.6 derives the normative wasm emitter's exact 92,997,536 executed-operator count. The ledger charges two word operations per measured operator plus one, so setup and emission cost `813600 + 2 * 92997536 + 1 = 186808673` operations.
Code size: 174,588 bytes of body records, 2,070 bytes for 414 recovery records, and 6,160 bytes for the other 1,232 control records. Total code is 182,818 bytes.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 43,672 | 57,844,952,903,049,360,168,000,000,000,000,000,000,000 |
| slice checks: ceil(B / 2^48) * 1,300 | 6,117,386,931,139,047,234,751,600 |
| stage-1 hits: e2max * 2,800 | 1,810,883,324,490,240,820,312,500,000,000,179,200 |
| finished events: 136,005 * (3,800 + 6 * 136,266) | 111,713,962,980 |
| cut trails: 6 * 4,200 | 25,200 |
| recovery: 2 (c + 2^48) * (1,424 + 39) + 600 + 65 | 96,261,160,406,790,347,403,993,539,539,958,659,847 |
| setup and generator | 186,808,673 |
| charged offset search | 461,900,436,782,186,496 |
| charged selector search | 102,738,366,499,389,440 |
N = 57,943,024,946,780,646,873,611,801,817,502,375,963,436 = 5.794302e+40 operations.
N / 2896 has log2 123.91191291. Claim `time_log2` = 123.91192, rounded upward. The walk never computes block 2: equal block-1 states give equal digests, so one evaluation of g is one block-1 compression of 40 steps, priced by its records.

### 3.5 Register file and smaller files
Declared prices: the machine has 929 registers of 256 bits: the 926 data registers that the shipped allocator uses (matching the exact peak of 926 live planes) and three pointers. A machine with fewer registers than the peak needs spill loads and stores that the shipped allocator does not produce; no estimate of their cost is claimed. The register file is counted as memory (29,728 bytes, Section 7).

### 3.6 Bounded emitter and peak setup storage

The freestanding C source embedded in `experiments/bssha.py` as `GEN_C` is the normative setup implementation. `python3 experiments/bssha.py --gen-c` prints its exact 17,546 bytes. Its SHA-256 is `0bfc40dec4de742c08e93e5b50f9ef55d4bef313f1ab3ad6d3c3c0cb882f0a4d`. Pass 0 counts uses and output nodes. Pass 1 rebuilds the same network, allocates registers online, and writes 32-bit records directly to the final code buffer. The emitter enforces `MAX_NODES = 43,905`, `MAX_RECORDS = 43,647`, 926 data registers, a 1,024-slot CSE table, at most 900 occupied slots, and the fixed bounds on every record field.

The C emitter reports the 15-field tuple

```text
(records=43647, registers=926, nodes=43904, calls=185446,
 moves=0, error=0, XOR=34228, AND=5791, OR=3628,
 code=174588, counters=16384, uses=43905, state=25856,
 choices=60, constants=256).
```

The emitted byte stream has SHA-256 `885c76492ea4caa497752afad7ae041f334bb55f1b776df41e7a50ae68f9b338`. Its polarity mask is `e7309a100cc5bf67eea64df025e3b2545785e20fdeb3df8208948c9c227bb195` in canonical big-endian form. The organizer-run `BoundedEmitter` is a byte-exact Python mirror. Before every declared experiment, `bounded_check` checks all 15 fields, the C source hash, the stream hash, the polarity mask, and equality with the ordinary Python builder.

The participant compiled `GEN_C` with Ubuntu clang 18.1.3 and LLD 22.1.2:

```sh
clang-18 --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

The stripped 14,370-byte module has SHA-256 `4f506054fd8068c50ea61b21af8ead13d193660f82657f948ba16a75839e943b`. `llvm-objdump -d` counts 5,979 static instructions. Participant measurement with Wasmtime 49.0.0 and fuel consumption enabled reports exactly 92,997,536 executed operators for exported function `run`. The module has no `if`, `else`, `call_indirect`, or bulk-memory operator. Wasmtime omits structural operators such as `block`, `loop`, and `end` from fuel. Every uncharged return closes either a charged call or the one entry call. Charging two word operations per fuel unit plus one therefore covers both charged and uncharged operators:

```text
2 * 92997536 + 1 = 185995073 operations.
```

The organizer does not compile or execute the wasm module. The compiler version, module hash, static instruction count, and fuel count are participant-run setup accounting. The organizer runs the Python mirror and checks the emitted bytes.

The emitter image has 5,979 instructions at 36 bytes, or 215,244 bytes. Its scratch is 74,173 bytes:

```text
use counts                                                   43,905
recent gates                                                    128
CSE keys and values                                           8,192
free and pending register maps                                  256
W array                                                        2,048
WS array and WCV words                                        2,112
V and Y arrays                                                2,304
14 one-word scratch arrays                                    1,792
X2, AM, and A3 scratch arrays                                   384
TB carry arrays                                               1,408
four tail scratch arrays                                        512
AW pointers                                                      32
six output and allocator arrays                               6,144
output polarities                                               256
info block                                                        92
17 scalar globals                                                68
alignment allowance                                             128
emitter arrays and globals subtotal                          25,856
addition choices                                                 60
IV, K, PW, and PERM constants                                   256
shadow stack                                                  4,096
total                                                        74,173
```

`experiments/bssha.py` computes the 25,856-byte state and 256-byte constant subtotals from named arrays and compares them with the C report. Complete setup memory is

```text
182818 program bytes + 16384 counters + 29728 registers
+ 2048 recovery arrays + 215244 emitter image + 74173 scratch
= 520395 bytes.
```

Search memory is code 182,818 + counters 16,384 + registers 29,728 + recovery array 2,048 + table 817,596 = 1,048,574 bytes. The count-only searches rebuild each candidate and do not retain candidate DAGs. Their declared image has at most 10,000 instructions, or 360,000 bytes. Both use the 74,173-byte builder scratch and 65,536 bytes of trial state. The offset vectors add 48 bytes for a 499,757-byte peak. The selector result table adds 60 bytes for a 499,769-byte peak. Setup, preprocessing searches, and the main search run sequentially, so their peaks do not add. The main search is the peak, two bytes below one MiB.

### 3.7 Preprocessing

No work is free or nonuniform. Final emission plus fixed setup costs 186,808,673 operations. The offset search costs 461,900,436,782,186,496 operations and the selector search costs 102,738,366,499,389,440. Total preprocessing is 564,638,803,468,384,609 operations, included in N. In target-compression units,

```text
log2(564638803468384609 / 2896) = 47.470260004006285.
```

The claim rounds this upward to `preprocessing_log2 = 47.47027`. There is no nonuniform advice because preprocessing constructs the fixed offsets and the selector choice, and setup constructs the body program.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bssha.py --loss` (the function `_lossq`); Appendix A recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
pass 1 of step 6 recomputes the two lengths and pass 2 aligns and walks them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F because F < 2101 < 2^12 and the low 12 key bits hold F. Equal keys of two DPs can differ only above bit 157. The lanes do not interact: the generated step applies the same function to every lane, so lane l holds g^b of its start after b batches.
The stage-1 test loses no event. A 48-bit key match without a merge ends the run; its probability and one recovery are charged.

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B evaluations, N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(13 L), S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 133988.94, tmax = 136,004, and CMAX = 6. Let Pi_m = product from i = 0 to m - 1 of (1 - i/N'), PP = Q(Q - 1)/(2N'), and H = (Q(Q - 1)/2 + 2^18 Q)/N'. Let k = 136724 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 262, p = e^(-c/L), and p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)). Let F be uniformly random on 256-bit values and P_F the success probability when every evaluation of g is replaced by lazy sampling from F. Then
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = 0.608673537399,
    P_delay = 0.001158175795,
    P_own = 7.410660e-06,
    P_long = 2.923283e-05,
    P_age = 1.571070e-05,
    P_dist = 3.679194e-06,
    P_cut = 4.752108e-05,
    P_key = C(tmax, 2) / (2^36 Tp) = 6.405666e-05,
    P_table = 6.746837e-07,
    P_tiny = Q 2^18 / N + k^2 L / N' + 255 Q / N' + exp(-300 + (e^5 - 1) H) + 2^-90 (Step 7; it needs 240 M <= Q, which holds here).
The numbers are printed by `python3 bssha.py --loss` (the function `_lossq`) and Appendix A recomputes the whole bound in exact rationals and 60-digit decimals (`certify`, outward rounding) and asserts the result >= 0.39: P_F >= 0.390000001000 (the program's float value, planned at the target 0.390000001, is 0.390000001). The program's B is the least multiple of 10^21 for which the float bound reaches 0.390000001 (Appendix A). H1 (Section 5) is the only premise of this entry: it states that the real attempt succeeds at least as often as A_F.

Proof.
Step 0 (notation). A trail is the run of evaluations of one lane between two restarts; a(t) is the number of earlier evaluations of the trail of t (its age); the length of a trail is its number of evaluations. A trail is finished when an evaluation returns a distinguished point (DP; that evaluation is its last), cut when a slice check restarts it at age >= c, open when the halt comes first. Every length is at most M, and a trail of length at most c is never cut. An evaluation is fresh when its input has not been evaluated before. A collision is a fresh evaluation whose value equals an earlier value (an earlier output or a start). The starts r + t' (t' < 2^18) differ from every value the run produces except with probability Q 2^18 / N (r is uniform and independent of F); this event is excluded below and charged in P_tiny, so a non-fresh evaluation exists only after a collision on its trail.

Step 1 (lazy sampling with a lottery). Realise F by independent uniform values V_1, V_2, ...: the t-th evaluation returns V_t if it is fresh and the value stored for its input otherwise. This is the lazy sampling of F for every adaptive choice of the points. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(theta), one per evaluation index, fresh or not; given all of them the V_t are independent and uniform on their class (the theta N DP values, or the N' other values). Index t belongs to lane (t - 1) mod 256, and the lane positions of a lane are its indices in increasing order; the lottery is extended beyond Q by further independent draws (used in the proof only). G_t is the history of the first t evaluations together with the whole lottery; F_t is the history of the first t evaluations together with xi_1, ..., xi_t only.
(L1) If t is fresh and xi_t = 0, then P(V_t = v | G_(t-1)) = 1 / N' for every non-DP value v (and 0 for DP values), and the events for different v are disjoint.
(L2) Whether t is fresh, its input, its batch, its age and the trails before t are determined by G_(t-1).
(L3) The lottery of a lane is i.i.d. Bernoulli(theta); the lanes are independent. Scanning the lanes one after the other, a scan that takes from each lane a number of positions that is a stopping time of that lane (with further independent coins after the run) reads one i.i.d. Bernoulli(theta) sequence.
(L4) N1 = xi_1 + ... + xi_Q is exactly Binomial(Q, theta), so P(N1 >= k) <= e^-q (e q / k)^k <= 2^-40 (Chernoff: the binomial moment generating function is below the Poisson one); P(N1 >= k) is charged once, as 2^-40.
(L5) The run up to evaluation t is F_t-measurable (it depends on V_1, ..., V_t only, and V_s depends on xi_s and an independent uniform). If s is a stopping time of (F_t), the lottery after s is independent of F_s and i.i.d. (strong Markov property of an i.i.d. sequence).

Step 2 (the free run and the first collision). Given the whole lottery xi, the free run is the run in which every evaluation is fresh: the trail boundaries (a DP at every xi = 1, a restart of a trail of age >= c at a slice check), the ages a(t), the lengths and the batches are functions of xi alone, and so are the sets of long trails (a trail is long when its first c coins are all 0, i.e. when it has c evaluations without a DP; the other trails are short, of length at most c, and are never cut) and the numbers rho(y) = the number of evaluations of the lane of y after y up to and including the first with xi = 1. Let n0(t) be the number of s <= t with xi_s = 0. Let tau be the first t with xi_t = 0 whose value V_t equals V_y for some y < t with xi_y = 0 (the first collision of the non-DP class), E1 the event that a start equals a value of the run (Q 2^18 / N), E2 the event that some DP-valued evaluation equals an earlier DP value (on N1 <= k - 1 its probability is at most k^2 L / N': a DP-valued evaluation is uniform on the theta N DP values, at most k - 1 earlier DP values exist, and there are at most k - 1 such evaluations). Outside E1 and E2 the real run is the free run up to tau (every evaluation is fresh), and until then the non-DP values are independent uniform on the N' non-DP values (L1). Hence, for t with xi_t = 0 and y < t with xi_y = 0,
    P(tau = t, V_t = V_y | xi) = Pi_(n0(t) - 1) / N',    sum over y of that = Pi_(n0(t)-1) - Pi_(n0(t)),    P(tau <= Q | xi) = 1 - Pi_(n0(Q)).
On N1 <= k - 1, n0(t) - 1 >= t - k, and Pi_(t-k) <= Pi_(t-1) / (1 - kQ/N') for t <= Q (Pi_(t-1) = Pi_(t-k) times at most k - 1 factors that are each at least 1 - Q/N'; Pi_m = 1 for m <= 1). Pi_m is bounded by exp(-m (m - 1) / (2 N')) from above and by exp(-m (m - 1) / (2 N') - (m - 1) m (2m - 1) / (6 N'^2)) from below (ln (1 - x) >= -x - x^2 for 0 <= x <= 1/2).

Step 3 (a first collision with a good partner is output). Say that the pair (t, y) with tau = t and V_t = V_y is good when (G1) y is not on the trail of t, (G2) b(y) < b(t), (G3) the trail of y is short, (G4) rho(y) <= B - b(t) and a(t) + rho(y) <= c - 1, and that it is undisturbed when no fresh evaluation of the trail of y after t, up to its first DP, is a collision. Claim. On a good undisturbed pair, if the run does not halt early (seventh cut, table full, stage-1 budget, key false match) and is outside E1 and E2, the program outputs a pair. Proof. Let X and Y be the trails of t and y. The input of X after t is V_t = V_y, the input of Y after y, so the evaluations that X performs after t are the evaluations Y performs after y, the j-th of them in batch b(t) + j for X and in batch b(y) + j for Y (Y does not restart before its DP, because its trail is short, hence never cut, and its first DP is the (rho(y))-th evaluation after y). By (G2) Y evaluates each of them strictly before X, so X only repeats points (they are not fresh). Undisturbed: the evaluations of Y after t are fresh and not collisions (those before t are not collisions, tau being the first), so the lottery of the lane of Y decides the DP: Y ends with a DP at its rho(y)-th evaluation after y, in batch b(y) + rho(y) < b(t) + rho(y) <= B (G4), inside the run, and the key of the DP is stored (the table is not full). X repeats it in batch b(t) + rho(y) <= B with the same DP and the same key; X has then done a(t) + rho(y) + 1 <= c evaluations, so no slice check cut it (a slice check cuts a trail of age >= c, and the age before its last evaluation is a(t) + rho(y) <= c - 1). The two trails are different (G1), finished, with the same key, and the inputs of t and of y are different (t is fresh) with g(t) = g(y): Lemma 1 applies. QED.

Step 4 (the pairs that are not good, and the disturbance). Let W(t, y) be the event (tau = t, V_t = V_y) with xi_t = xi_y = 0 and work on N1 <= k - 1 outside E1 and E2. By Step 2, P(W(t, y) | xi) <= Pi_(t-1) / ((1 - kQ/N') N') <= 1 / ((1 - kQ/N') N'), and sum over t of P(W(t, y) | xi) is at most the sum over t of 1 / N', so at most Q / N'. A pair that is not good fails one of the following; each failure is bounded by the expected number of pairs of that kind times the hazard.
(a) (G1) fails: y is among the a(t) earlier evaluations of the trail of t; a(t) is at most g(t), the number of consecutive 0 coins just before t on its lane (g(t) as in Step 6 (ii)), E g(t) <= sum over i >= 1 of (1 - theta)^i <= L - 1, so the failure has probability at most Q L / N' = P_own.
(b) (G2) fails: y is in the batch of t before t, at most 255 pairs per t: 255 Q / N' (charged in P_tiny).
(c) (G3) fails: y is on a long trail. A long trail has at most M evaluations (it is cut at the first slice check at age >= c, or finishes before), a y has at most Q partners t, and the number of long trails is at most the number of successes of the scan of Step 6 (i) (disjoint windows of c coins 0), with expectation at most p (q + 256) / (1 - p) there: M Q p (q + 256) / ((1 - p) N') = P_long.
(d) (G4) fails. rho(y) > B - b(t) means that the B - b(t) coins after y on its lane are all 0 (they lie in the batches b(y) + 1, ..., b(y) + B - b(t) <= B, inside the run), probability (1 - theta)^(B - b(t)) <= e^(-theta (B - b(t))) for each y. By Step 2 the pairs (t, y) with y < t contribute at most sum over t of (t - 1) Pi_(t-1) / ((1 - kQ/N') N') e^(-theta (B - b(t))), and (t - 1) Pi_(t-1) / N' = Pi_(t-1) - Pi_t, so, with b(t) <= ceil(b / 256) for t <= b and the sum of Pi_(t-1) - Pi_t over t in (a, b] equal to Pi_a - Pi_b, at most (1 - kQ/N')^-1 sum over the bins (a, b] (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = P_delay (the bins and the enclosures of Pi are in Appendix A). The second part, a(t) + rho(y) >= c: a(t) <= g(t) and rho(y) >= 1, so it requires g(t) + (rho(y) - 1) >= c - 1. If t and y are on different lanes the two coin sets are disjoint and g(t), rho(y) - 1 are dominated by independent geometric variables with values in 0, 1, 2, ...; the sum of two such variables is at least c - 1 only if a single i.i.d. sequence of coins has at most one 1 among its first c coins, hence among its first c - 1 coins: probability at most (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. If they are on the same lane and (G1) and (G3) hold, y is on an earlier trail of the lane that is short, so it ended with a 1 before the start of the trail of t, and the two coin sets (those of rho(y) up to that 1, those of g(t) after it) are disjoint: the same bound. At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': PP p2 = P_age.
(e) Disturbance. For a good pair let r' be the number of evaluations of the lane of y with index > t up to and including the first with xi = 1; the coins there are independent of F_t (L5, t is a stopping time) and r' is dominated by a geometric variable of mean L. The evaluations of Y after t and before its DP are at most r' fresh evaluations, each a collision with conditional probability at most (Q + 2^18) / N' given the history (L1; the last one, a DP-valued evaluation, is covered by E2, and counting it here only overcounts). For this bound W(t, y) is taken without the restriction to N1 <= k - 1 and outside E1, E2: it is the event (tau = t, V_t = V_y), which is F_t-measurable, so P(W(t, y) and disturbed) <= P(W(t, y)) L (Q + 2^18) / N'; the events W(t, y) for different (t, y) are disjoint (the values V_y are distinct before tau), so the sum of P(W(t, y)) is at most P(tau <= Q) <= sum over t of (t - 1)/N' = PP: PP L (Q + 2^18) / N' = P_dist.

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
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; E[g(t) + 1] <= sum for i >= 0 of (1 - theta)^i = L, so E_S <= Q L / N' = 7.411e-06.
- X: E_X <= sum over pairs e' < t of P(sigma(e') + g(t) >= c) / N'. Different lanes: sigma(e') - 1 and g(t) are independent and dominated by geometric variables on {0, 1, ...}, so the probability is at most P(at most one 1 in c - 1 Bernoulli trials) = (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. Same lane, e' = t - j 256: if a 1 lies between them the two runs of 0s are disjoint and the same bound p2 holds; if the j positions are all 0, the probability is at most (1 - theta)^j T(c - 1 - 2j) with T the tail above (T = 1 below 1); the sum over j of these is at most L e^(-(c - 2)/(2L)) (2 + (c - 1)/L). Hence E_X <= (Q / N') L e^(-(c-2)/(2L)) (2 + (c-1)/L) + PP p2 = 1.570e-05.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^18) / N': E_J2a2 <= (Q + 2^18) L Q (Q - 1) / (2 N'^2). E_J2a = 7.366e-06.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2 = 1.571e-05.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 1.121e-06.
So P(K >= 7) <= P(K_A >= 7, N1 <= k - 1) + P(N1 >= k) + P(K_B >= 1) <= P(Binomial(n2, p) >= 7) + E_S + E_X + E_J2a + E_J2b + E_Y + [P(N1 >= k), charged once as 2^-40]; P(Binomial(n2, p) >= 7) = 2.080e-08 and P_cut = 4.752e-05 (the program's `cut_halt`). There is no premise about K: the number of cut trails is bounded by this argument, and it needs no distribution of K. The bounds on S and J2a are not small (about Q L / N' each); they are the real cost of trails that close a cycle or join a path that is itself disturbed.

Step 7 (the early halts and the small terms). The attempt can end before it outputs the pair of Step 3 only by an early halt or by the events E1, E2, N1 >= k: the seventh cut (P_cut, Step 6); the table full (finished trails are at most N1 + 59 outside 60 or more collisions, so tmax keys need N1 >= tmax - 59: P_table = 6.747e-07); a key false match (P_key = 6.406e-05: the stored ends are at most tmax fresh DP values, uniform on the DP class, and the key space is 2^36 * 2101 = 2^47.04); the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^20 = 3.235e+32: the fresh stage-1 hits are at most the sum of eta_t = 1[low 20 bits of V_t zero], exactly Binomial(Q, 2^-20), above 1.5 mu2 with probability at most e^(-0.108 mu2); the repeated hits after merges come from at most 60 colliding trails, each repeating at most M points that lie in at most 60 lane windows of total length at most M, and every such union of windows holds more than 2 M / 2^20 hits with probability at most e^(-0.386 M / 2^20), so with 240 M <= Q (checked: M = 3.290e+34, Q = 3.392e+38) the repeated hits are below mu2 / 2 except with probability below e^-1000; a recovery with no pair (a key false match, counted, or a start on another trail, 2^-100). The number of collisions: every fresh evaluation with xi = 0 is a collision with conditional probability at most (t - 1 + 2^18) / N' (L1), so E w^(number of collisions) <= exp((w - 1) H) for w = e^5 (the factor per evaluation is at most 1 + (w - 1)(t - 1 + 2^18)/N' <= e^((w-1)(t-1+2^18)/N')), and P(60 or more collisions) <= exp(-300 + (e^5 - 1) H). P_tiny collects Q 2^18 / N (E1), k^2 L / N' (E2), 255 Q / N' (Step 4 (b)), exp(-300 + (e^5 - 1) H), and 2^-90 for everything else of this step (the stage-1 budget, the recovery with no pair) and for the rounding of the factors 1 - kQ/N' and of the enclosures of Pi (each below 2^-96). This proves the lemma. QED.
Consequently P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny = 1 - 0.608673537 - 0.001158176 - 7.411e-06 - 2.923e-05 - 1.571e-05 - 3.679e-06 - 4.752e-05 - 9.1e-13 - 6.406e-05 - 6.747e-07 - 2^-90 = 0.390000001 (float, planned at 0.390000001; the printed terms are rounded), and the exact certificate of Appendix A is 0.390000001000 >= 0.39 (B is the least multiple of 10^21 that reaches the planning target).

Sensitivity to H1 (d) is explicit: replace N by N/(1 - eps) in the same bound and rerun `plan`. A collision-hazard surplus helps; a deficit increases the required batch count. No robustness margin is silently treated as a theorem.

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function g and one attempt; it cannot be tested at width 256. It is declared, not proved. Its four clauses are uniform fresh outputs and collision hazard, random-mapping iterate behavior, independent DP selection with probability 2101 / 2^122, and preservation of the lazy-sampling hazard under the program's adaptive choices. Lemma 2 proves the bound for F. H1 is used only to compare the real fixed function with F. The circuit equivalences, ledger, memory layout, cut count, and exact bound for F are not premises.
Support of H1 (stated; it is not measured at width 256). (1) It is the generic premise of parallel collision search with distinguished points (van Oorschot and Wiener, J. Cryptology 12 (1999) 1-28): a fixed compression function, iterated from fresh starts with no chosen input difference, is modelled by a random function. The generic entries of this track rest on it; on the board, with status review: bfcaad61 and a5707aa9 (round 40), 3017c952 (round 51), 1884db5b (round 57), 3642e1cd, 6b678689 and 4684dfc2 (round 64; 4684dfc2 is the source of walk B), and d4f8f4e4 to 05004d0b (rounds 40 to 53) with this H1. (2) Clause (d) fails only if g, along its own iterates, collides less often than a random function by a constant factor 1 - eps; that is a property that separates 40-step SHA-256 from a random function. This entry uses no differential property. (3) A deviation that raises the hazard only helps; a deficit eps is priced in Section 4.
The two functional organizer experiments in Section 6 make the organizer recompute the complete two-block digest of every returned pair. Because the walk g(x) = f(x) XOR q differs from bfcaad61's only by the invertible Maj-shear on Q, the OR-shear on X, and the constant output mask q, `enc_invert` and `DigestNet` recover the target digest exactly. Reference values for 256 independent uniform 16-bit values per trial are P(a pair) = 1 - prod_{i<256} (1 - i / 2^16) = 0.392678, or 100.53 of 256 trials, and mean equal pairs C(256, 2) / 2^16 = 0.498047 per trial, or 127.50 over 256 trials. In bfcaad61's run of the same digest walk, `bssha-n16` returned 198 of 256 verified pairs with 58 halts, and `proj-k0-w256` returned 98 of 256 verified pairs with 121 total equal pairs.

The third organizer experiment, `rf-model-r20`, addresses clauses (b) and (c) directly at reduced width. It runs the actual emitted walk `h(x) = g(x) mod 2^20` in 128 two-lane groups for at most 2,048 evaluations per group. A reduced distinguished point has five zero low bits, so its random-function density is exactly 1/32. Fresh endpoints use the same trail-index layout, `key + 1` sentinel, table scan, and `r + t` restart rule as the full search.

The null preserves the dependence that the tested groups have. The first 128 organizer trial seeds define the observed roots. The remaining 128 seeds are committed to the calibration role by hashing their ordered `(seed, trial)` strings before any null simulation; the low 32 bits of that commitment are exported as `hold`. From that organizer-supplied holdout, the program runs 48 complete null ensembles. Each ensemble contains 128 groups and one shared lazy-sampled 20-bit random function, so groups in an ensemble can share inputs, outputs, and merged tails exactly as groups under the fixed tested function can. Each ensemble uses the same DP, table, and restart procedure as the observation.

For collision timing, the program bins each group into four 512-evaluation bins plus one censored bin. It computes the observed Pearson statistic against the 48-ensemble mean. Each null ensemble receives a leave-one-out Pearson statistic against the other 47 ensembles. `px` is the add-one empirical upper-tail rank among those 48 null statistics. For distinguished points, the program counts an output only when its input is globally fresh across the whole 128-group ensemble. It reports the usual density-1/32 standardized score only as a scalar ordering, then calibrates `abs(z)` against the 48 complete-ensemble scores; `pz` is the add-one empirical rank. The hard acceptance rule fixed in source is `px >= 0.05` and `pz >= 0.05`, with resolution 1/49. The organizer-visible first row exports the holdout commitment, ensemble count, observed bins, both statistics, and both calibrated ranks. Passing is evidence for random-mapping collision timing and DP density for this fixed walk at width 20, including the scaled adaptive table logic. It is not evidence at width 256 by itself, does not measure the adaptive hazard conditioned on future DP flags, and does not prove H1.
Every unsuccessful attempt of the width-16 experiment ends with a halt of the program (the halts equal the unsuccessful trials). At width 16 a halt "recovery found no pair" (a trail start lying on another trail) is frequent; at width 256 it has probability below 2^-100 (Section 4).
Not tested: the full 256-bit functional graph; iterations of length above 2^40; the bit-sliced search above width 36. A deviation of g from H1 that raises the collision rate only helps; one that lowers it by eps costs the extra time of Section 4.

## 6. Experiments

Three organizer experiments run the shipped program `experiments/bssha.py` (it dispatches on the experiment id; standard library only). Before dispatch, `bounded_check` runs the byte-exact Python mirror of the normative C emitter. For the first two experiments, the complete digest of a returned message is what the organizer recomputes: the 64-byte message, padded to two blocks.
`bssha-n16`: per trial, one attempt of the 256-lane search at width 16 (DP = low 2 bits zero, plan(16): 7 batches, cut rule, table, recovery) on the walk g16(x) = the low 16 bits of the complete digest of M(x), x < 2^16. Each batch runs the shipped program on the 256 planes (the 240 high input planes zero), then the experiment's digest network (`DigestNet`, bit-sliced, experiment code only, not in the ledger) inverts walk B, forms cv1 = IV + state and runs block 2; the recovery runs the rolled recovery program and the same inverse and block 2 in scalar form. The trials run side by side: the planes of trial i occupy bits 256 i to 256 i + 255 of each word, so one pass of the program and of the digest network serves every live trial, and each bitwise record acts on every trial's 256 bits alone. The trial returns M(x), M(y) when the attempt succeeded and two nulls otherwise. Checked event: the messages are distinct and their complete 40-step digests agree in the low 16 bits. This is exact, because at width 16 the walk is those 16 digest bits. The width-16 walk differs from the width-256 walk g only in the map after the program (inverse, block 2, low 16 bits); it runs the same program, search, table and recovery.
`proj-k0-w256`: per trial, 256 points at width 256 (source by trial index mod 3: uniform from the seed, counter r + i, iterates of g from 256 seed-derived starts) evaluated with the shipped program; their complete digests are formed by the digest network; the trial returns two points whose digests agree in the low 16 bits when the set holds such a pair. Checked event: as above. It checks at full width the program, the inverse of walk B, the chaining value, block 2 and the message construction.
`rf-model-r20`: the first 128 organizer trial seeds define the observed roots, and the second 128 are committed to the calibration seed. Two lanes per root run the emitted walk truncated to 20 bits. The scaled DP condition, table slots, sentinel, and restart rule match the search as described above. Forty-eight complete shared-function ensembles calibrate the collision Pearson statistic and the globally-fresh-input DP score. The experiment returns only null message pairs. Its first organizer-visible observation reports the five observed bins, Pearson statistic and empirical rank, global-fresh DP count and score and empirical rank, ensemble count, and holdout commitment.
The experiments do not measure the cost or success probability of the width-256 attempt. The first two are functional checks. The third gives bounded reduced-width evidence for two clauses of H1.

## 7. Memory

Table: 136,266 slots * 48 bits = 817,596 bytes. Slot t belongs to trail t. It stores `key + 1`; zero is empty. Neither t nor length is stored. The maximum key is 281,474,976,708,660, so the sentinel transform fits. The shorter-slot experiment is fully charged and negative: a 32-bit fingerprint table fits 191,292 completed trails, but its alias overflow and replay budget produces `time_log2 = 123.91448`, so this package does not use it.
Code: 43,647 body records * 4 bytes = 174,588 bytes. The 414 rolled-recovery records use 2,070 bytes. The other 1,232 fixed 5-byte records use 6,160 bytes. Total code is 182,818 bytes.
Counters and copies: 16,384 bytes (trail numbers 768, birth batches 4,096, counters, and the 8,192-byte copy of the 256 planes used by the handlers). The 929 registers (the 926 data registers the program uses and three pointers), counted as memory: 29,728 bytes. The array of the rolled recovery program (the 40 schedule words W0..W39 and 24 constants K10..K33, one 32-byte word each, 64 words): 2,048 bytes. No advice. Memory peak = max(setup phase 520,395, search phase 1,048,574) = 1,048,574 bytes <= 2^20 = 1,048,576. Claim `memory_log2_bytes` = 20. `python3 bssha.py --ledger` prints both phases.
The table size is the largest that fits: tmax = floor(8 (2^20 - 182,818 - 29,728 - 16,384 - 2,048) / 48) - 262 = 136,004. Appendix A computes Tp = 2101 and certifies P_F >= 0.39.

## 8. Heuristics, conventions and what is credited

The premise is H1. The 929-register file and fixed record formats are declared machine prices, not statistical premises. Lemma 2 proves the cut count. There is no advice.

Direct dependencies are a4c6ba2c-25e0-4d35-80e9-ae2ea22eb05d, d22ae1b2-2368-460a-b6d4-1e5e37ceb735, and 95263e47-d61b-43a6-bb46-30ced2488280. Through a4c6ba2c, the construction also uses the credited round-40 lineage bfcaad61-9487-4edb-8778-b5408e713d01, a5707aa9-5267-4db3-ad10-9914e6b280be, 87cb17fa-d025-4066-bd13-91d9936ce327, 4684dfc2-cdac-4441-af91-c9979e2888a9, 1884db5b-acc6-42e7-ac3c-5877e77b8277, 3642e1cd-e391-41a7-81e0-456c02e4becd, 6b678689-e6a2-42b0-87d8-fff55432f2f6, 744875ec-f063-4208-8075-b61192ac4d69, 44870635-2031-4c6a-aa62-c44672c7f338, and 38912d66-c0d0-4238-9058-1e8a2775f695. The current entry changes the frozen reduction choice, record formats, bounded setup emitter, table sentinel, and plan. It does not claim the older entries' work as new.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate, and `certify` recomputes the bound of Lemma 2 in exact rationals and 60-digit decimals with outward rounding: the line `P_lower certified` is a proved lower bound on P_F, asserted >= 0.39. The same numbers come from `python3 bssha.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 43647, 22, 3, 256      # records executed per batch (setup excluded), stage-1 test, loop control, lanes
INSTR_REC = 43647                               # records of the body program
PH7, EXTRA, RECINIT = 1424, 39, 65              # records executed per call of the rolled recovery program, extra operations per recovery batch, records executed once per recovery
N_BITS, S1, W, KAPPA = 256, 20, 102, 13         # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE = 2800, 3800, 4200, 1300
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 6
WASM_RUN_OPERATORS, WASM_OPERATOR_FACTOR = 92997536, 2
BODYB, CTRLB, RECB, REC_RECORDS = 4, 5, 5, 414
CONTROL, REGFILE, COUNTERS, ADVICE, ARRAYS = 1207, 29728, 16384, 0, 2048
KEYB = SLOTB = 48                              # key+1; zero is the unwritten sentinel
SEARCH_EVAL_OPS = 1 << 48
OFFSET_SEARCH = 1641 * SEARCH_EVAL_OPS            # 64 endpoint + 1 initial + 3 * 192 coordinate + 1000 perturbation builds
SELECTOR_SEARCH = 365 * SEARCH_EVAL_OPS           # 1 baseline + 2 * (32 + 15 * (4 + 6)) complete builds
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 21, 18                        # B is a multiple of GRAIN; trail numbers are below 2^18
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP                                        # one batch = 43,672 operations
code_bytes = INSTR_REC * BODYB + REC_RECORDS * RECB + (FILT + LOOP + CONTROL) * CTRLB
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
emitter = WASM_OPERATOR_FACTOR * WASM_RUN_OPERATORS + 1
rows = [("main loop: B * %d" % body, body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished events: (tmax + 1) * (3800 + 6 * (tmax + 262))", (tmax + 1) * (EVENT + 6 * (tmax + LANES + CMAX))),
        ("cut trails: 6 * 4200", CMAX * CUTOPS),
        ("recovery: 2 (c + 2^48) * (%d + 39) + 600 + %d" % (PH7, RECINIT), 2 * capr * (PH7 + EXTRA) + 600 + RECINIT),
        ("setup and generator", SETUP_FIXED + emitter),
        ("charged offset search", OFFSET_SEARCH),
        ("charged selector search", SELECTOR_SEARCH)]
N = int(sum(v for _, v in rows))
assert N == 57943024946780646873611801817502375963436
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
Tp = 2101  tmax = 136004  B = 1324531803055719000000000000000000000  e2max = 646744044460800292968750000000064  c = 32898551061787541832935729240636801
memory bytes = 1048574
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000001000
main loop: B * 43672                                 57844952903049360168000000000000000000000
slice checks: ceil(B / 2^48) * 1300                  6117386931139047234751600
stage-1 hits: e2max * 2800                           1810883324490240820312500000000179200
finished events: (tmax + 1) * (3800 + 6 * (tmax + 262)) 111713962980
cut trails: 6 * 4200                                 25200
recovery: 2 (c + 2^48) * (1424 + 39) + 600 + 65      96261160406790347403993539539958659847
setup and generator                                  186808673
charged offset search                                 461900436782186496
charged selector search                               102738366499389440
N = 57943024946780646873611801817502375963436
certificate: 2^12391191 * 2896^100000 <= N^100000 < 2^12391192 * 2896^100000
log2(N/C) = 123.9119129117
time_log2 = 123.91192
```
