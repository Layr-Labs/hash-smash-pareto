# sha256-r41: a 45,302-instruction native bit-sliced birthday walk, with the recovery array inside the dead plane copy, a bit-sliced 47-bit trail table, a weighted cascade stage-1 test and nine exact window rewrites

## Credited direct-initialization derivative

This filing is an exact credited derivative of live R41 submission `96a30aa7-f13a-485f-9ca9-cde87397d715` at evaluated commit `9f031f31dd23b6ed93b64235c289f2d482325fcf` (input package SHA-256 `7a5cf9dccedb10f82532a214676bd433cf9cb7d8349d89bb06fcc610bb52ac3c`). The parent source SHA-256 is `11dc6210a7b82d5b45dd78101ab365e90b260ee0e0036c9b24797c263723eb89` and this source SHA-256 is `413190ae3058b5e31b85efffcf817b319d254817fbb2e15a65d500a22e40a26a`. The only executable change is in `stage1c`: `a=0; for q in P[:CJ]: a|=q` becomes `a=P[0]; for q in P[1:CJ]: a|=q`, with `S1U=CJ+1` becoming `S1U=CJ`. For the fixed `CJ=10`, both fragments compute exactly the OR of `P[0]` through `P[9]`; the derivative removes the redundant OR with zero. The kernel, cascade levels and guard, target relation, walk, recovery, experiments, probability argument and H1 are unchanged. The direct-init path reduces the unconditional stage-1 charge from 11 to 10 operations and the body from 45,316 to 45,315 operations per batch.


This package ports the round-64 package d65d81b1-a243-4661-a418-4e2961ebc1e5 (samsmith, `time_log2` 124.12379) to the 41-step target `sha256-r41-prefix-v1`, on sraiw's round-41 entry cda94445-1839-4c4e-b188-a79d66f1bc4b (`time_log2` 123.92331). The two are instances of one program: sraiw's round-64 package 6ea56109 and its round-41 instance cda94445 differ only in round-specific data and the recovery prologue, and d65d81b1 is 6ea56109 with the changes listed below. Everything round-specific in this package is therefore cda94445's, and every change that d65d81b1 and its lineage made at round 64 is applied unchanged in method. The merge was made from this author's round-58 port 56b698c6-c143-4804-8ccf-180874bb420d (Appendix B), whose program is the same as this one apart from round-specific data. The numbers below are the round-41 values, re-derived by this package's program and by the program of Appendix A.

cda94445 instantiates the program at round 41 with round-specific data plus one structural change in the rolled recovery program. `ROUNDS = 41` and `UNIT = C = 2980`; the round-constant table has the first 41 SHA-256 constants; the C emitter's `RND` is 41 and its schedule array has 41 words; the addition-choice table has one all-zero entry for each of the 57 nonconstant `addm` sites; the two per-bit tail shear masks were re-chosen for round 41 (`QM = 0x9f5937e8`, `XM = 0xeaab0b62`, Section 1.1); the register file has 884 data registers. The recovery loop runs four rounds per iteration and covers rounds 10 to ROUNDS - 7; at round 41 that is 25 rounds, not a multiple of four, so the per-call program first runs round 10 and the schedule word W16 unrolled and then runs the unchanged loop body six times from memory offset 1 (Section 3.3). At 41 steps the kernel that cda94445's generators build has 35,491 XOR, 6,047 AND, and 3,773 OR native instructions, or 45,311 in total, before the window rewrites of Section D. Both generators are kept: the bounded Python generator and the freestanding C emitter build the same network, and the self-test requires byte equality, scalar equivalence, chained-walk equivalence, zero moves, recovery equivalence, and complete two-block digest agreement.

What changed relative to cda94445 is two layout decisions, one declared allowance, the charge of the stage-1 test, and one exact kernel rewrite step, and nothing else (Appendix B lists them and justifies each). (1) The 66-word recovery array (2,112 bytes) is no longer a separate allocation: it is stored in the first 2,112 bytes of the 8,192-byte plane copy, which no step reads once step 6 begins. cda94445 already stores its pass-1 checkpoints in the table, which is dead from the same moment. (2) Trail keys have 47 bits (the 36 bits of x above bit 121 and the 11-bit code of F) instead of 48, and they are held in a bit-sliced table of 540 groups of 256 trail numbers with 47 words of 32 bytes per group (Section 3.3.1). The table has 138,240 slots instead of 135,287 and needs only aligned 256-bit loads and stores and immediate shifts. (3) The declared handler code is 1,250 five-byte records instead of 1,000; the table routines of Section 3.3.1 need at most 133 of them. (4) The stage-1 distinguished-point test is the weighted cascade of newjordan's round-64 entry c31fe915 (Section C), with this derivative's exact direct accumulator initialization: 10 operations in every batch instead of the parent's 11 and the 22 of the full 20-plane test, with the unchanged conditional levels paid through one capped weighted counter and charged once as the `stage-1 cascade` row. (5) Nine disjoint windows of the kernel (each in one to three pieces of 1 to 11 consecutive records; four of them have two or three pieces) are replaced by windows with one record fewer. The windows were found by the search of d65d81b1, run on the 45,311-gate round-41 kernel: every connected sub-network with at most 8 gates and at most 6 inputs, its local function synthesised exactly over {XOR, AND, OR} by SAT (CaDiCaL). Nine pairwise disjoint windows have a replacement with one gate fewer, and a replacement is accepted only where the solver proved that it computes the same function of the window's inputs on all input patterns (no don't-care assumptions are used). The emitter applies the replacements in place to the allocated record stream, after the allocator has run, by the table `PT` of `GEN_C` (376 hexadecimal characters); three of the windows first rename the live range of one or two values into a register that is free over the extended range (Section D). Every replacement leaves the registers that later records read and write unchanged: it is validated by a symbolic simulation of register contents, so no other record changes (later records move up by the number of records saved). The kernel falls from 45,311 to 45,302 instructions. The step is an exact equivalence, not a premise: besides the SAT proofs, ABC combinational equivalence checking proves the complete 45,311-instruction and 45,302-instruction netlists equal on all 2^256 inputs (Section D, Appendix B.4), and the self-test compares the emitted kernel with the word-level SHA-256 walk. With (1) to (4), `tmax` = 137,977 (135,024 in cda94445) and `Tp` = 2132 (2086). The exact plan, ledger and certificate are re-derived by the program of Appendix A, which is that of d65d81b1 with cda94445's round-41 constants and this package's counts.

The native body instruction remains exactly 32 bits: a 2-bit opcode and three 10-bit register fields. The machine executes it directly for one word operation. No decoder or interpreter runs in the priced path. The body occupies 181,208 bytes. Control and recovery use native fixed 5-byte instructions.

The six-offset search evaluates 1,641 complete builds. The ledger reserves one baseline and two passes over all 213 alternatives in the 57-site reduction inventory, or 427 complete builds. Every build is charged at `2^48` operations. The emitted selector is the all-zero baseline, so no unrecorded selector result affects the circuit. The final plan uses 137,977 completed trails in 138,240 bit-sliced sentinel slots (540 groups of 256 trail numbers). Search memory is 1,048,270 bytes.

The exact ledger is

```
N = 60074435816065403106810366381900294477380 word operations
log2(N / 2980) = 123.922778374616
```

The claim rounds upward to `time_log2 = 123.92278`, 0.00003181 bit below the immediate live parent 123.92282 and 0.00025 bit below newjordan's 123.92303 entry. Setup memory is 687,860 bytes. H1, the fixed-function random-function comparison stated in Sections 4 and 5, is the only score-critical premise. Circuit changes, counts, and memory bounds are exact checked claims, not premises. The prices that this package declares in addition to those of cda94445 are the handler-code allowance of item (3) and the lifetime argument of item (1) (Appendix B.1 and B.3).

## 1. Target and relation

Target `sha256-r41-prefix-v1` (the Pareto lane `sha256`, round 41; the first 41 of the 64 SHA-256 steps on every block). The two colliding messages have 64 bytes each. With x a 256-bit integer and y0..y7 its eight 32-bit words (big-endian, y0 the highest), M(x) is the 16 big-endian words W0..W15 with
- W0..W7 = the constant words 3e73281c, 752d8ed2, ad19eff1, 7250fceb, d4095422, 44fdb519, 43f22c5b, d8d6aac4 (computed from the standard IV by `_anchor_prefix` so that the eight new a-words of steps 0..7 are K9 - K8, -K9, 0, 0, 0, 0, 0, 0; the working state after step 7 is therefore (a,b,c,d,e,f,g,h) = (0, 0, 0, 0, 0, 0, -K9, K9 - K8), which makes steps 8 and 9 cheap),
- W8 = y0, W9 = y1, and W(8+k) = y_k - K(8+k) modulo 2^32 for k = 2..7.
FIPS 180-4 padding appends 0x80, 55 zero bytes and the 64-bit length 512: the padded message is 128 bytes, two blocks, and block 2 is the same for every x. The target runs the steps 0 to 40 on each block, block 1 from the standard IV and block 2 from the chaining value cv1 = IV + s(x) word by word, where s(x) is the working state after step 40 of block 1; the digest is the result of block 2 with its feed-forward (`verifier/hash_functions.py:digest(M(x), "sha256", 41)`). The profile's message domain is "finite byte strings of bit length below 2^64"; a 64-byte string is in it.
Write a_i, e_i for the a and e words after i steps of block 1 (a_0, e_0 from the IV), T1_i for the T1 of the step that produces them and W_j for the schedule word of step j. With the fixed 32-bit polarity masks `QM = 0x9f5937e8` and `XM = 0xeaab0b62`, f(x) is walk B (4684dfc2) with per-bit polarity-matched disjoint-support shears on Q and X. Define the eight words bw = [e_38, e_39, a_34, a_35, Q, T1_37, X, Y] with X = e_36 + Ch(e_39, XM, e_37) + W_39 (at bit j: `e_39[j] | e_37[j]` when `(XM >> j) & 1 == 1` and `~e_39[j] & e_37[j]` when `(XM >> j) & 1 == 0`; since `Ch(e2, e3, e4) = Ch(e2, XM, e4) + (e2 & e3 & ~XM) - (e2 & ~e3 & XM) mod 2^32`, the inverse adds `(e2 & e3 & ~XM) - (e2 & ~e3 & XM)`), Q = T1_36 + Ch(a_35 ^ a_34, a_33, QM) (at bit j: `~(a_35[j] ^ a_34[j]) | a_33[j]` when `(QM >> j) & 1 == 1` and `(a_35[j] ^ a_34[j]) & a_33[j]` when `(QM >> j) & 1 == 0`; since `Maj(a6, a7, a8) = Ch(a6 ^ a7, a8, QM) + (a6 & a7 & ~QM) - (~a6 & ~a7 & QM) mod 2^32`, the inverse adds `(a6 & a7 & ~QM) - (~a6 & ~a7 & QM)`), and Y = e_37 + W_40. Then f(x) is the 256-bit integer whose eight 32-bit words, most significant first, are bw[6], bw[1], bw[7], bw[0], bw[5], bw[4], bw[2], bw[3] = X, e_39, Y, e_38, T1_37, Q, a_34, a_35 (the permutation PERM = (6, 1, 7, 0, 5, 4, 2, 3), the order with no register move, Section 3.2; `enc_words`, `words_of` and `int_of` in the program). In particular the low 32 bits of f(x), which hold the distinguished-point test bits of Section 2, are a_35, and the next word up is a_34. In the program these are bw = [E[r-3], E[r-2], A[r-7], A[r-6], ..., T[r-4], ...] with r = 41. These words determine s(x): the program's `enc_invert` recovers a_36 = Q + (a_35 & a_34 & ~QM) - (~a_35 & ~a_34 & QM) + Sigma0(a_35), then a_37, a_38, a_39, the T1 values of the 0-based steps 39 (= X + (e_39 & e_38 & ~XM) - (e_39 & ~e_38 & XM) + Sigma1(e_39) + K_39) and 40 and the whole state, by additions, subtractions and the round functions. The walk is g(x) = f(x) XOR q, q the fixed 256-bit mask `148a004430b746c9e01d4dfb0cc5bf671d4f25b8601a6eab227bb195b5b60ae1` (121 output planes that the generator leaves complemented instead of spending a NOT).
So g(x) = g(y) gives s(x) = s(y), hence the same cv1, the same block 2 and equal digests. x != y gives M(x) != M(y), since x -> W8..W15 is a bijection. The attack outputs two distinct 64-byte messages with equal complete 256-bit digests.
The selftest (`python3 bssha.py --selftest`) compares the program with scalar g on 2,560 lanes, including all-zero and all-one inputs, checks four chained steps, checks the inverse on 10,000 random states, checks the recovery program and experiment digest network, and runs six width-16 search attempts. It also runs the independent ordinary builder and requires byte equality with the normative bounded emitter.

### 1.1 Choice of the tail shear masks

`QM` and `XM` only choose, bit by bit, which of two disjoint-support forms of Maj and Ch enters the encoded words Q and X; `enc_invert` adds back the exact difference, so every choice gives a bijective encoding of the same state and the same collision relation. For round 41 they were re-chosen by the same sequential single-bit pass as in 26d9ad0b (mask bits QM 0..31 then XM 0..31, a flip kept only when the kernel instruction count strictly decreases, at most two passes), starting from the round-52 values `QM = 0xbe79bcfb`, `XM = 0x3b6d8189`: 45,339 instructions with the starting masks, 45,312 with the shipped masks (and 45,311 with bit-interleaved emission and `_ch3` operand ordering) (27 flips in the first pass, none in the second; 129 count-only builds). This is a participant-side choice of two constants of the walk; its cost is covered by the charged envelopes of Section 3.2 at `2^48` operations per build, and no claim depends on its optimality.

## 2. The attack (program `experiments/bssha.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished when its low 20 bits are zero and the 102-bit number F = (x >> 20) mod 2^102 is below Tp = 2132. Thus D = 122, theta = 2132 / 2^122, and L = 2658455991569831745807614120560689152 / 2132 = 2^110.94201. The key is the 36 bits of x above bit 121 followed by the 12-bit encoding of F. It has 47 bits; F < 2132 < 2^12.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated program of Section 3.2. The start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 20 low planes are all zero. If it is zero, the next batch runs at once. In this entry the test is the cascade of Section C: it stops as soon as no lane can still have its low bits zero, and the mask it hands to step 3 is the same.
3. For each set bit of the mask, the lane is extracted and the window test F < Tp decides whether it is a DP. If `key + 1` is in the table, go to step 6. Otherwise write `key + 1` into slot t of the bit-sliced table of Section 3.3.1 and start the next trail in that lane. Zero is the unwritten sentinel. The slot position is t, so neither t nor the length is stored.
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = ceil(35 L) batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the weighted stage-1 counter is negative at its check (Section C), when the table holds 137,977 keys, when an eighth trail would be cut (`CMAX = 7`), or if step 6 finds no pair.
6. Recovery (checkpoint resolution). Pass 1 walks the two trails together for at most cr = ceil((62/5) L) = 30923878325953014679188006655677811 calls, recording every D-th point of each unfinished trail (D = ceil(cr / kchk) = 2437061890294981060697297395830, kchk = floor(table_bytes / 64) - 1 = 12689) and the two terminal lengths and endpoints; if either trail has not reached a DP within cr steps, the attempt halts. Pass 2 aligns the longer trail to each checkpoint of the shorter trail by a walk of (l_long - l_short) mod D < D steps, locates by binary search the last checkpoint pair where the aligned walks still differ (at most ceil(log2(kchk + 1)) <= 16 probes of < D steps each), and steps the two trails together from that checkpoint pair for at most D steps until their next values agree. The first predecessor pair a != b with g(a) = g(b) is returned. Step 6 needs only r, t0 and t1: the plane copy and the table are dead from its start, the 2,112-byte recovery array is placed at the start of the plane copy and the checkpoints in the table (Appendix B.1). The rolled two-lane program has 466 fixed 5-byte records in total, of which 78 are one-time initialization records, and executes 1,453 records per call. Pass 1 runs at most cr calls and pass 2 runs at most 17 D calls.
Constants printed by `--ledger`: Tp = 2132, L = 2658455991569831745807614120560689152 / 2132, B = 1324588912053250000000000000000000000, Q = 339094761485632000000000000000000000000, e2max = 646771929713500976562500000000064, c = 87285140436157702723514534915219626, cr = 30923878325953014679188006655677811, kchk = 12689, capr = 87285140436157702723796009891930282, and tmax = 137,977. The 138,240 total slots (540 groups of 256 trail numbers) cover 256 initial trails, all stored trails, and seven cut trails. The maximum trail number is 138,239 < 2^18; the boundary test asserts it.
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is a constant of the program).

## 3. Operation ledger

### 3.1 Machine
Machine model of this entry (declared cost-model prices). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices operations and memory; it gives no register count and no instruction size. For round 41 the organizer contract sets `reference_operation_cost = 2980` (`python3 scripts/pareto_candidate.py --family sha256 --rounds 41 --show-contract`).
This entry declares a load/store machine with 256-bit words and 889 registers, 884 data registers, three pointer registers and the two registers of the stage-1 cascade (Section C). Charged, one operation each: every XOR, AND, OR and NOT of a 256-bit register, every register move, every set of a register to a constant, every load and store, every pointer addition, comparison and conditional branch, and the one random word. Nothing is free except renaming a bit-sliced rotation.
The body uses this machine's native fixed 32-bit instruction: a 2-bit opcode and three 10-bit register fields. Opcode values 0, 1, and 2 mean XOR, AND, and OR; 3 is reserved. The machine fetches and executes each instruction directly for one operation. There is no decoder or interpreter in the priced path. `Prog.run`, `Prog.compile`, and `Prog.fast` are test mirrors only. All 45,302 kernel instructions (the kernel after the window rewrites of Section D) use the native format, so the body occupies 181,208 bytes. Recovery and control use native fixed 40-bit instructions. Every executed instruction costs one word operation.

### 3.2 One batch = 45,316 operations charged to every batch, for 256 trails
Representation is bit-sliced: one 256-bit machine word holds one bit position for 256 trails, and a SHA-256 rotation only renames planes. Signals carry a node and a free polarity bit. The pivot full adder costs five gates. `add3` carries the pair `(u,U)`, representing `1 if U else 2u`; its T0, T1, and T2 templates cost nine gates per ordinary column and eight at bit 30. The self-test exhausts all 32 input rows for each template relation.

The round fusion passes `h[0]` and `u[0] = h[0] XOR Ch[0]` into `add3`. Bit 0 combines the half-adder on the other two operands with the `h + Ch` carry in seven gates for either absorbed carry. At bit 1, `_add_u` begins from a carry-free root and may use the alternate `ch1 = f1 XOR (~e1 AND (f1 XOR g1))` form when its stored polarity avoids a penalty, while `_adduc` folds the round constant into `h + u` across suffix columns `m..31` using the 96-word `UCD` template table. The selector absorbs `c0 + 2c1 + delta` into the folded constant, and splits `W[16]` and `W[23]` into carry-saved sums plus deferred constants across steps 19..24. These are exact rearrangements of `h + Ch + Sigma1 + K + W` and are checked against scalar SHA-256.

For every four-variable sum with zero absorbed constant, `addm` orders `(A,B,D,C)`, computes `add3(A,B,C)` with the bit-0 half-adder carry `D0`, and then adds `[0,D1..D31]`. The outgoing bit-0 carry occupies the otherwise unused pair-carry slot at bit 1, so the second adder's bit 1 is a two-gate half adder. At round 41 there are 16 such sums (the 15 of round 40 plus the schedule word W38; at round 41, W39 and W40 are three-operand sums because their `sigma1` terms are deferred into X and Y).

The walk-B tail uses the per-bit shears `QM = 0x9f5937e8` and `XM = 0xeaab0b62`. `_ch3` fuses `B + Ch` into the first `add3`: each column forms `w5 = hg XOR (e AND (f XOR g))` and selects a polarity-matched multiset of `[W,a,Sigma1(e)]`. Its column relation is exhaustively checked. `enc_invert` applies the matching Q and X corrections, so equal walk values imply equal block-1 states and complete digests. The tail also defers the `sigma1` terms of W_39 and W_40 into X and Y (W_39 and W_40 are formed only as `W(i-16) + sigma0(W(i-15)) + W(i-7)`), which is exact because X and Y are the only consumers of W_39 and W_40.

The schedule advances `W[21]` and `s23_raw` to step 19, defers the constant adders for `W[22]` and `W[23]` until after their rounds, and advances `W[32]` to step 31. The streaming allocator routes short-lived nodes into idle output targets and otherwise takes a dying operand or the lowest free non-target register. The output permutation `(6,1,7,0,5,4,2,3)` needs zero moves. With 884 data registers the shipped allocator emits zero moves, and the register file is priced at that size.

The six offsets are preprocessing output. Their deterministic search evaluates exactly 1,641 complete candidates: 64 endpoint placements, one initial coordinate point, three complete sweeps of 192 bits, and 1,000 perturbations from the fixed xorshift seed `6a09e667bb67ae85`. Bits are visited by increasing word and then increasing bit. A strict improvement replaces the incumbent, so ties retain the earlier candidate. The shipped offsets are those of 27984c2d (`W(8+k) = y_k - K(8+k)`); the 1,641-build envelope is charged as an upper bound on offset-selection work and is not claimed to reproduce them. All other count-only work done for round 41 is covered by the two charged envelopes (1,641 + 427 = 2,068 builds at `2^48` each): a first steepest-descent mask pass that was stopped after nine accepted steps (at most 641 builds), the shipped mask pass of Section 1.1 (129 builds), the register-count scan (121 allocator runs, 880 through 1,000 data registers) and a few dimension probes, together fewer than 1,000 builds. The addition-choice selector is the all-zero baseline of 26d9ad0b; no selector search was run for round 41.

The addition audit is also charged preprocessing. Among 57 nonconstant `addm` sites, 31 have exactly three operands (24 three-variable sums and 7 two-variable sums with a constant) and admit one three-of-three reduction. 18 have four operands (16 four-variable sums and 2 three-variable sums with a constant) and admit four three-of-four reductions plus six unordered pair-first reductions; the two with a constant also admit the constant-carry form. The remaining eight sites have fewer than three operands. One complete pass therefore has

```text
31 + 18 * 10 + 2 = 213 alternatives.
```

The charged validation envelope contains the deterministic fused baseline and all 213 alternatives in two complete passes. The candidate does not depend on an unshipped winning alternative: its emitted hint table is the all-zero baseline. The envelope is `1 + 2 * 213 = 427` complete builds.

Both searches use a count-only builder with an eight-probe CSE table and an eight-entry recent-gate ring. One complete build has at most two builder passes, 160 multiword sums, 64 first-triple masks per sum, 32 columns, 13 current-column forms, 13 lookahead forms, and 12 trial gates per form. Charging 1,024 word operations for each trial gate, including lookup, rollback, and bookkeeping, gives

```text
2 * 160 * 64 * 32 * 13 * 13 * 12 * 1024
= 1,360,967,761,920 < 2^41 operations.
```

One more copy covers the rest of the network, scoring, comparisons, loop control, and deterministic candidate generation. The round-41 build has 57 multiword sums, below the 160 of the envelope, and the bounded emitter performs 181,200 helper calls for both passes together. The package charges `2^48` operations per complete build, more than 100 times that doubled structural bound (2^48 / (2 * 1,360,967,761,920) = 103.4). The exact search charges are

```text
offsets:  1641 * 2^48 = 461900436782186496 operations
selector:  427 * 2^48 = 120189815055450112 operations.
```

These bounds follow the loops and fixed array limits. They do not rely on a development call counter or an unshipped trace.

Executed per batch: 35,482 XOR + 6,049 AND + 3,771 OR = 45,302 gates; zero NOT, set, move, load, store, or control instructions. Per lane evaluation (one evaluation of g in one lane) this is 176.961 operations.
Validation is by the bounded emitter, its stream hash, the independent builder comparison, the exhaustive algebraic checks inherited from the frontier, and the scalar and end-to-end tests described in Sections 1 and 6.
The generator runs once at the start; its work is charged in the setup row (3.3), its code and peak storage in Sections 3.6 and 7.

### 3.3 Loop, stage 1, handlers and the other events
One batch: 45,302 body instructions + unconditional stage-1 work 11 + loop control 3 = 45,316 operations charged to every batch. Stage 1 is the weighted cascade of Section C, which replaces the full 20-plane test that cda94445 charges to every batch (19 ORs, one NOT, one comparison and one branch: 22 operations): in every batch 9 ORs fold planes 0 to 9, one comparison with the all-ones register and one branch skip the rest when no lane has those 10 bits zero; the conditional levels (planes 10 to 19, the guard check and the final NOT) are paid through a capped weighted counter, charged once as the `stage-1 cascade` row of Section 3.4. A DP has all 20 low bits zero, so its lane is flagged.
Loop control of the batch loop: counter increment, compare with the next slice limit, branch back: 3 operations.
Handlers are charged per event at the stated operation bounds and stored as fixed 5-byte control records:
- Stage-1 hit: store the 256 planes to an 8 KiB copy (256 stores), extract the lane (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (at most 15), counters. Below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail: key formation, sentinel encoding, the slot write, the new start, insertion of its 256 bits, reload of the planes, lane arrays, and counters fit below 3,800 operations. The scan of the table for `key + 1` is charged six operations per slot, including extraction, comparison, and branch; the routine of Section 3.3.1 needs 1.68 per slot. The source increments the counter and scans before its `finished > tmax` halt, so the ledger charges `tmax + 1` handled events. At most `tmax` keys are stored.
- Slice check (every 2^48 batches): charged **1,300** each. Cut trail: charged **4,200**; at most 7 cut trails (`CMAX = 7`).
- Recovery program (`RecProg`): a second program evaluates g for two chain values at once, in bits 0..31 and 128..159 of each word. The message and constant array has 66 words (41 schedule words and the 25 constants K10..K34 of the rounds before the tail), or 2,112 bytes. The array lies in the first 2,112 bytes of the 8 KiB plane copy, which is dead when the recovery starts (Appendix B.1); the one-time initialization (78 records, charged in the fixed operations of the recovery below) writes it at the start of the recovery. Preloaded tail constants and masks remove repeated setup; the preloaded offsets and the state registers that a call overwrites are re-set before each call and charged in the recovery batch below. The loop body (four rounds and four schedule words per iteration, with the live-register permutation of 26d9ad0b) needs a multiple of four rounds; at round 41 the rounds before the tail are 10..34, 25 rounds. The per-call program therefore runs round 10 unrolled with the same round code, forms W16 = W0 + sigma0(W1) + W9 + sigma1(W14) and the next partial sum W1 + W10, shifts the six schedule registers by one word (six register copies), and then runs the unchanged loop body six times with its memory pointer starting at 1 (rounds 11..34, schedule words W17..W40). The one-round renaming of the state registers is undone at the end of the tail by two register copies (a_35 and a_34 back to the input registers). There are 466 fixed 5-byte records in total (78 one-time initialization records and 388 records of the per-call program) and 1,453 executed records per call. Per call these are 39 records that write the inputs' message words W8 to W15 to the array and set up the starting state, 58 for the unrolled round and its schedule word, 2 that set the loop pointers, 6 * (210 + 3) = 1,278 for the loop (four rounds and four schedule words, then the pointer step, compare and branch) and 76 for the tail: 39 + 58 + 2 + 1,278 + 76 = 1,453. The self-test compares this program with scalar g.
- Recovery batch: one call (1,453 records) plus at most 39 surrounding operations, or 1,492 operations per batch, the same in both passes (pass 1 runs at most cr = 30923878325953014679188006655677811 batches plus kchk * 80 = 12689 * 80 checkpoint-store operations; pass 2 runs at most 17 * D = 17 * 2437061890294981060697297395830 batches plus 16 * 100 probe operations and 600 + 78 fixed operations; 47 additional 5-byte control instructions, RECOVERY_CODE = 94 vs 47, hold the two-pass checkpoint and binary-search control). The 39 are itemized as: 10 re-sets of registers whose start value the call reads and that a call overwrites, 2 copies saving the predecessor pair, 9 for the two-lane equality test, 12 for the pass-1 DP test, 3 for counter increment, cap comparison and branch, and 3 spare. Every call is charged all 39 regardless of pass.
- Setup and emitter: fixed work is 813,600. Section 3.6 gives the participant-measured 102,032,006 wasm fuel units. Charging two word operations per measured unit plus one gives `813600 + 2 * 102032006 + 1 = 204877613` operations.
Code size: 181,208 bytes of body instructions, 2,330 bytes for 466 recovery instructions, and 7,740 bytes for the other 1,548 control instructions (the stage-1 cascade has 41 records where the stage-1 code of cda94445 had 22, Section C). Total code is 191,278 bytes.

### 3.3.1 Bit-sliced trail table

cda94445 keeps the keys in 6-byte slots and charges six operations per slot for the scan. This package keeps 47-bit keys in a bit-sliced table, which needs no sub-word addressing.

Layout. Trail numbers are grouped by 256. Group g, 0 <= g < 540, is 47 consecutive 32-byte words W[g][0..46] (1,504 bytes); bit i of W[g][b] is bit b of `key + 1` of trail 256 g + i. An unwritten slot is 47 zero bits; since `key + 1 >= 1`, it equals no key. The table has 540 * 47 * 32 = 812,160 bytes and 138,240 slots (`tmax` + 263: the 256 initial trails, at most `tmax` stored trails, and seven cut trails). Every access is an aligned 256-bit load or store at an immediate word offset from a group pointer, and every shift is by an immediate.

Scan (step 3: is `key + 1` in the table?). Let k be the 47-bit `key + 1` in a register. The pointer is set to the table start (1 operation). For each group, a copy kr of k and an accumulator acc = 0 are made, and for b = 0, ..., 46: load W[g][b]; K = 0 - (kr & 1), which is all ones if bit b of k is 1 and zero otherwise; acc = acc | (W[g][b] ^ K); kr = kr >> 1; advance the pointer; compare with the group end; branch. That is 9 operations per word. A zero bit i of acc means that all 47 bits of slot 256 g + i equal k. After the 47 words, the complement of acc (one XOR with all ones) is tested by a branch on nonzero. Per group: 47 * 9 + 2 (copy, clear) + 1 + 1 + 2 (loop compare and branch) = 429 operations; for 540 groups and the pointer set-up 231,661 operations, or 1.676 per slot. If the complement is nonzero in a group g', the lowest set bit i' is found by the halving routine of the stage-1 hit (at most 8 steps of 5 operations = 40), t0 = 256 g' + i' is the trail of the earlier key, and the program goes to step 6; this happens at most once per attempt.

Write (step 3, no match). Let t = 256 g + i be the trail number of the lane (from the lane arrays); g = t >> 8 and i = t & 255 take 2 operations. The one-hot word E = 1 << i is made by eight conditional shifts: E = 1; for k = 0, ..., 7: mask = 0 - ((i >> k) & 1) (3 operations), X = E << 2^k (1), E = E ^ ((E ^ X) & mask) (3); 57 operations in all. The group offset 1504 g = (g << 10) + (g << 9) - (g << 5) takes 5 operations and 1 move to a pointer register. Then kr = k (1) and, for b = 0, ..., 46: load W; K = 0 - (kr & 1) (2); W = W ^ ((W ^ K) & E) (3); store; kr = kr >> 1; advance the pointer, compare, branch (3), that is 11 operations per word. Total 2 + 57 + 5 + 1 + 1 + 47 * 11 = 583 operations.

Cost and code. The table work of one finished-trail event is at most 231,661 + 40 + 583 = 232,284 operations. The ledger already charges 6 * 138,240 = 829,440 operations per event for the scan alone (Section 3.3, finished trail), and the 3,800 operations charged for the rest of the event are unchanged, so the new routines fit inside the existing charge with a factor of more than 3.5 to spare. The three constants 0, 1 and all ones are set once per event (3 operations, inside the 3,800). The routines take at most 133 five-byte records (scan: 9 in the loop, 2 before it, 4 after it and 1 for the pointer, 16 in all; write: 2 + 57 + 5 + 1 + 1 + 11 = 77; 40 more if the lane-finding routine of the stage-1 hit is copied rather than shared), against a declared handler-code allowance that grows from 1,000 to 1,250 records. The 1,000 of cda94445 already include its own table routines, which this package no longer uses. That allowance is a declared price, like the 1,000 of cda94445, and is not itemized; Appendix B.3 gives its sensitivity.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 45,315 | 60,023,746,549,693,023,750,000,000,000,000,000,000,000 |
| stage-1 cascade: U + 30 (Section C) | 2,678,064,869,068,096,623,746,628,580,370,015,209 |
| slice checks: ceil(B / 2^48) * 1,300 | 6,117,650,690,630,771,492,807,100 |
| stage-1 hits: e2max * 2,800 | 1,810,961,403,197,802,734,375,000,000,000,179,200 |
| finished events: 137,978 * (3,800 + 6 * 138,240) | 114,968,788,720 |
| cut trails: 7 * 4,200 | 29,400 |
| recovery: cr * (1,453 + 39) + kchk * 80 + 17 * D * (1,453 + 39) + 16 * 100 + 600 + 78 | 46,200,240,100,107,339,800,972,032,181,420,143,530 |
| setup and generator | 204,877,613 |
| charged offset search | 461,900,436,782,186,496 |
| charged selector search | 120,189,815,055,450,112 |
N = 60,074,435,816,065,403,106,810,366,381,900,294,477,380 operations.
N / 2980 has log2 123.922778374616. Claim `time_log2` = 123.92278, rounded upward. The walk never computes block 2: equal block-1 states give equal digests, so one evaluation of g is one block-1 compression of 41 steps, priced by its instructions.

### 3.5 Register file and smaller files
Declared prices: the machine has 889 registers of 256 bits: 884 data registers (Section 3.2), three pointers, and the two registers of the stage-1 cascade (the weighted counter w and the all-ones constant, Section C). The register file is counted as 28,448 bytes.

### 3.6 Bounded emitter and peak setup storage

The freestanding C source embedded in `experiments/bssha.py` as `GEN_C` is the normative setup implementation. `python3 experiments/bssha.py --gen-c` prints its exact 28,917 bytes. Its SHA-256 is `0722af621f17ed139bda6610b1d1900592fd485ed6212df8de5c4b87aa85c32c`. Pass 0 counts uses and output nodes. Pass 1 rebuilds the same network, allocates registers online, and writes native 32-bit instructions directly to the final code buffer; the routine `patch` then applies the window rewrites of Section D in place. The emitter enforces `MAX_NODES = 45,568`, `MAX_RECORDS = 45,311`, 884 data registers, a 1,024-slot CSE table, at most 900 occupied slots, and every packed-field bound.

The C emitter reports the 15-field tuple

```text
(records=45302, registers=884, nodes=45568, calls=181200,
 moves=0, error=0, XOR=35482, AND=6049, OR=3771,
 code=181244, counters=16384, uses=45568, state=29056,
 choices=57, constants=1021).
```

In this tuple `records` is the length of the emitted stream after the window rewrites of Section D (45,302 records, 181,208 bytes), and `code` is `sizeof code`, the size of the emitter's static code buffer, which is dimensioned for `MAX_RECORDS` = 45,311 records (181,244 bytes); its last 36 bytes are not part of the stream. The emitted byte stream has SHA-256 `a70c53633aaf34750b92efc014ba094eb853fa2d322abeef2d68787a2cd75d10`. Its polarity mask is `148a004430b746c9e01d4dfb0cc5bf671d4f25b8601a6eab227bb195b5b60ae1`. Before every experiment, the organizer-run Python mirror checks all 15 fields, the C source hash, stream hash, polarity mask, and equality with the independent builder (after the same window rewrites). The participant also ran the compiled wasm module below in Wasmtime, called `run()`, and read the info block and the code buffer: it reported the same 15 fields and wrote the byte stream with the SHA-256 above, which equals the stream of the independently verified patched netlist (Section D).

The participant compiled `GEN_C` with Ubuntu clang 18.1.3 and Ubuntu LLD 18.1.3:

```sh
clang --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

The stripped 24,365-byte module has SHA-256 `f67bebb0a26b324480d2c769a7687bf886c6bd8f09eb92d42dee69b3402a1d65`. `llvm-objdump -d` counts 10,332 static instructions. Participant measurement with Wasmtime 50.0.1 (Python bindings) and fuel enabled reports exactly 102,032,006 units of fuel consumed by exported function `run`, started with an ample budget; the least budget with which `run` completes, found by bisection, is 11 units lower (102,031,995), and the larger, consumed figure is charged. Charging two word operations per fuel unit plus one covers the measured and structural operators:

```text
2 * 102032006 + 1 = 204064013 operations.
```

The organizer does not compile or execute the wasm module. The compiler version, module hash, static instruction count, and fuel count are participant-run setup accounting. The organizer runs the Python mirror and checks the emitted bytes. The setup row is negligible: any bound below 2^100 operations would leave the claimed `time_log2` unchanged.

The emitter image has 10,332 instructions at 36 bytes, or 371,952 bytes. Its scratch is 79,798 bytes:

```text
use counts                                                   45,568
recent gates                                                    128
CSE keys and values                                           8,192
free and pending register maps                                  256
W array (41 words)                                            5,248
WS array and WCV words                                        2,112
V and Y arrays                                                2,304
14 one-word scratch arrays                                    1,792
X2, AM, and A3 scratch arrays                                   384
TB carry arrays                                               1,408
four tail scratch arrays                                        512
AW pointers                                                      32
six output and allocator arrays                               6,144
output polarities                                               256
info block                                                       92
17 scalar globals                                                68
alignment allowance                                             128
state subtotal (the preceding 16 rows)                       29,056
addition choices                                                 57
IV, K, PW, PERM, UCD, and PT constants                        1,021
shadow stack                                                  4,096
total                                                       79,798
```

`experiments/bssha.py` computes the 29,056-byte state and 1,021-byte constant subtotals from named arrays and compares them with the C report (the constants are cda94445's 644 bytes plus the 377 bytes of `PT`). Complete setup memory is

```text
191278 program bytes + 16384 counters + 28448 registers
+ 371952 emitter image + 79798 scratch
= 687860 bytes.
```

Search memory is code 191,278 + counters 16,384 + registers 28,448 + table 812,160 = 1,048,270 bytes (the recovery array lies inside the plane copy, which is part of the counters; Appendix B.1). The count-only searches rebuild each candidate and do not retain DAGs. Their 10,000-instruction image is 360,000 bytes. With 79,798 bytes of builder scratch and 65,536 bytes of trial state, the offset and selector peaks are 505,382 and 505,391 bytes (the parts above plus 48 bytes of offset-search words and the 57-byte selector table, respectively). All phases run sequentially. Search is the overall peak, 1,048,270 bytes (`<= 2^20` bytes).

### 3.7 Preprocessing

No work is free or nonuniform. Final emission plus fixed setup costs 204,877,613 operations. The offset search costs 461,900,436,782,186,496 operations and the selector audit costs 120,189,815,055,450,112. Total preprocessing is 582,090,252,042,514,221 operations, included in N. In target-compression units,

```text
log2(582090252042514221 / 2980) = 47.47292385547319.
```

The claim rounds this upward to `preprocessing_log2 = 47.47293`. There is no nonuniform advice.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bssha.py --loss` (the function `_lossq`); Appendix A recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
when both trails have length <= cr, pass 1 of step 6 records every D-th point of each walk and the terminal lengths l0, l1 <= cr, and pass 2 aligns the longer walk via its checkpoints and binary-searches the floor(min(l0, l1) / D) + 1 checkpoint intervals (at most 16 probes of < D steps) before stepping the two walks together for at most D steps to the first merge pair, found within cr + 17 D batches. The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F because F < 2132 < 2^12 and the low 12 key bits hold F. Equal keys of two DPs can differ only above bit 157. The lanes do not interact.
The stage-1 test loses no event. A 47-bit key match without a merge ends the run; its probability and one recovery are charged.

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B evaluations, N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(35 L), cr = ceil((62/5) L), S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 135971.7885, tmax = 137,977, and CMAX = 7. Let Pi_m = product from i = 0 to m - 1 of (1 - i/N'), PP = Q(Q - 1)/(2N'), and H = (Q(Q - 1)/2 + 2^18 Q)/N'. Let k = 138727 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 263, p = e^(-c/L), and p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)). Let F be uniformly random on 256-bit values and P_F the success probability when every evaluation of g is replaced by lazy sampling from F. Then
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_rec - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = 0.608647478717 (the no-useful-collision term shift * Pi_Q of Step 2, shift = 1/(1 - kQ/N')),
    P_delay = 0.001141336522,
    P_own = 7.303221e-06,
    P_long = 2.195540e-14,
    P_age = 1.127013e-14,
    P_rec = 2 PP e^(-(12.4 L - 1)/L) (1 + (12.4 L - 1) theta / (1 - theta)) = 5.480453e-05,
    P_dist = 3.626166e-06,
    P_cut = 1.455556e-05,
    P_key = C(tmax, 2) / (2^36 Tp) = 1.299401e-04,
    P_table = 9.541748e-07,
    P_tiny = P_start + P_DP-repeat + P_same-batch + P_60 + 2^-90,
    P_start = Q 2^18 / N = 7.676833e-34,
    P_DP-repeat = k^2 L / N' = 4.144913e-34,
    P_same-batch = 255 Q / N' = 7.467623e-37,
    P_60 = exp(-300 + (e^5 - 1) H) = 3.154787e-99.
Step 7 derives every component and proves that the two remaining stage-1 tails fit together inside the charged `2^-90` reserve. Appendix A evaluates each component with outward rounding.
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

Step 3 (a first collision with a good partner is output). Say that the pair (t, y) with tau = t and V_t = V_y is good when (G1) y is not on the trail of t, (G2) b(y) < b(t), (G3) the trail of y is short, (G4) rho(y) <= B - b(t) and a(t) + rho(y) <= c - 1, (G5) a(t) + rho(y) <= cr - 1 and a(y) + rho(y) <= cr - 1, and that it is undisturbed when no fresh evaluation of the trail of y after t, up to its first DP, is a collision. Claim. On a good undisturbed pair, if the run does not halt early (eighth cut, table full, stage-1 budget, key false match, recovery cap) and is outside E1 and E2, the program outputs a pair. Proof. Let X and Y be the trails of t and y. The input of X after t is V_t = V_y, the input of Y after y, so the evaluations that X performs after t are the evaluations Y performs after y, the j-th of them in batch b(t) + j for X and in batch b(y) + j for Y (Y does not restart before its DP, because its trail is short, hence never cut, and its first DP is the (rho(y))-th evaluation after y). By (G2) Y evaluates each of them strictly before X, so X only repeats points. Undisturbed, Y reaches its DP first and stores the key; X later repeats it before any cut. By (G5) both trails have length <= cr, so pass 1 reaches both DPs and pass 2 returns the distinct predecessor pair. QED.

Step 4 (the pairs that are not good, and the disturbance). Let W(t, y) be the event (tau = t, V_t = V_y) with xi_t = xi_y = 0 and work on N1 <= k - 1 outside E1 and E2. By Step 2, P(W(t, y) | xi) <= Pi_(t-1) / ((1 - kQ/N') N') <= 1 / ((1 - kQ/N') N'), and sum over t of P(W(t, y) | xi) is at most the sum over t of 1 / N', so at most Q / N'. A pair that is not good fails one of the following; each failure is bounded by the expected number of pairs of that kind times the hazard.
(a) (G1) fails: y is among the a(t) earlier evaluations of the trail of t; a(t) is at most g(t), the number of consecutive 0 coins just before t on its lane (g(t) as in Step 6 (ii)), E g(t) <= sum over i >= 1 of (1 - theta)^i <= L - 1, so the failure has probability at most Q L / N' = P_own.
(b) (G2) fails: y is in the batch of t before t, at most 255 pairs per t: 255 Q / N' (charged in P_tiny).
(c) (G3) fails: y is on a long trail. A long trail has at most M evaluations (it is cut at the first slice check at age >= c, or finishes before), a y has at most Q partners t, and the number of long trails is at most the number of successes of the scan of Step 6 (i) (disjoint windows of c coins 0), with expectation at most p (q + 256) / (1 - p) there: M Q p (q + 256) / ((1 - p) N') = P_long.
(d) (G4) fails. rho(y) > B - b(t) means that the B - b(t) coins after y on its lane are all 0 (they lie in the batches b(y) + 1, ..., b(y) + B - b(t) <= B, inside the run), probability (1 - theta)^(B - b(t)) <= e^(-theta (B - b(t))) for each y. By Step 2 the pairs (t, y) with y < t contribute at most sum over t of (t - 1) Pi_(t-1) / ((1 - kQ/N') N') e^(-theta (B - b(t))), and (t - 1) Pi_(t-1) / N' = Pi_(t-1) - Pi_t, so, with b(t) <= ceil(b / 256) for t <= b and the sum of Pi_(t-1) - Pi_t over t in (a, b] equal to Pi_a - Pi_b, at most (1 - kQ/N')^-1 sum over the bins (a, b] (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = P_delay (the bins and the enclosures of Pi are in Appendix A). The second part, a(t) + rho(y) >= c: a(t) <= g(t) and rho(y) >= 1, so it requires g(t) + (rho(y) - 1) >= c - 1. If t and y are on different lanes the two coin sets are disjoint and g(t), rho(y) - 1 are dominated by independent geometric variables with values in 0, 1, 2, ...; the sum of two such variables is at least c - 1 only if a single i.i.d. sequence of coins has at most one 1 among its first c coins, hence among its first c - 1 coins: probability at most (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. If they are on the same lane and (G1) and (G3) hold, y is on an earlier trail of the lane that is short, so it ended with a 1 before the start of the trail of t, and the two coin sets (those of rho(y) up to that 1, those of g(t) after it) are disjoint: the same bound. At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': PP p2 = P_age.
(e) Disturbance. For a good pair let r' be the number of evaluations of the lane of y with index > t up to and including the first with xi = 1; the coins there are independent of F_t (L5, t is a stopping time) and r' is dominated by a geometric variable of mean L. The evaluations of Y after t and before its DP are at most r' fresh evaluations, each a collision with conditional probability at most (Q + 2^18) / N' given the history (L1; the last one, a DP-valued evaluation, is covered by E2, and counting it here only overcounts). For this bound W(t, y) is taken without the restriction to N1 <= k - 1 and outside E1, E2: it is the event (tau = t, V_t = V_y), which is F_t-measurable, so P(W(t, y) and disturbed) <= P(W(t, y)) L (Q + 2^18) / N'; the events W(t, y) for different (t, y) are disjoint (the values V_y are distinct before tau), so the sum of P(W(t, y)) is at most P(tau <= Q) <= sum over t of (t - 1)/N' = PP: PP L (Q + 2^18) / N' = P_dist.
(f) (G5) fails. The first part, a(t) + rho(y) >= cr, is the second part of (d) with cr in place of c: probability at most p2(cr) = e^(-(cr-1)/L) (1 + (cr - 1) theta / (1 - theta)) per pair. The second part, a(y) + rho(y) >= cr: the g(y) coins 0 before y, the coin of y and the rho(y) - 1 coins 0 after it form a run of 0s of length at least cr among coins disjoint and dominated by independent geometric variables, so the probability is again at most p2(cr). At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': 2 PP p2(cr) <= P_rec (cr = ceil(12.4 L), and p2(cr) <= p2(12.4 L)). The union bound runs over all Q (Q - 1) / 2 pairs, so it covers every collision pair, in particular the pair behind the first detected key match, not only the first collision.

Step 5 (the sum). With P(tau <= Q, N1 <= k - 1) >= 1 - Pi_(Q-k+1) - 2^-40 and the failure bounds above (including the recovery-cap failure (f), P_rec), the early halts are charged in Step 6 (eighth cut) and Step 7 (table full, key false match, stage-1 budget, recovery cap).

Step 6 (the cut count and the long trails; no premise). Let K be the number of trails that the run cuts or would cut; the eighth one halts the run because `CMAX = 7`. Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.
(i) K_A. The disjoint-window scan from the credited proof bounds eight fresh cut trails by the upper tail of `Binomial(n2,p)` with `n2 = k + 263` and `p = exp(-c/L)`. Its value is `8.6259e-86`.
    P(K_A >= 8, N1 <= k - 1) <= P(Binomial(n2, p) >= 8) = 1 - sum_{j=0..7} C(n2, j) p^j (1 - p)^(n2 - j)
(the tail increases with p, so p = e^(-c/L) is allowed).
Any run with at least eight total cuts has either eight fresh cuts, or at least one non-fresh cut. The displayed order-8 tail covers the first case. Step 6 (ii) covers the second case through the S, X, J2a, J2b, and Y root events.
The same scan counts the long trails of Step 2: a long trail of the free run is a window of c coins 0 at its start, the windows of different trails of a lane are disjoint, and a run of 0s holds at most floor(length / c) disjoint windows, which is what the scan finds; so the number of long trails is at most the number S_c of successes. The trial outcomes form one i.i.d. Bernoulli(p') sequence read in a stopping-time order (L3), so Wald's identity gives E S_c = p' E T, T = S_c + F_c the number of trials, with F_c <= N1 + 256 the number of failures, E F_c <= q + 256: E S_c <= p (q + 256) / (1 - p) (used in Step 4 (c)).
(ii) K_B. A trail T in K_B has a first non-fresh evaluation at age <= c - 1. Its previous evaluation t (age a(t) <= c - 2, T fresh up to t, so a(t) <= g(t), where g(t) is the number of consecutive 0s of the lottery just before t on its lane) is fresh, and V_t equals the input of an earlier fresh evaluation e' (the first evaluation of that input; a start is excluded). Call t the joining collision of T and e' its target. For a lane position e let sigma(e) be the number of positions from e to the first 1 at or after e (inclusive), and f'(e) that position: sigma is a function of the lottery, so it is determined by G. Choose T in K_B with the earliest joining collision. One of the following root events occurs:
- S: e' is on T itself. T then cycles through its own non-DP points and is cut.
- X: e' is on another trail T' and a(t) + sigma(e') >= c (hence g(t) + sigma(e') >= c).
- J2a: e' on T', a(t) + sigma(e') <= c - 1, and T' has a collision at a fresh position in [e', f'(e')).
- J2b: e' on T', and e' lies in a run of 0s of length >= c of its lane.
- Y: some trail has a collision at a fresh evaluation t'' while it has been fresh for at least c - 1 evaluations (g(t'') >= c - 1).
Proof that one occurs. Suppose not S, X, J2a. T evaluates the inputs evaluated by T' from e' on, one batch later or more, so T repeats them (non-fresh) while T' is ahead. If T' evaluates e', e' + 256, ..., f'(e') freshly (no collision there by not-J2a, and every non-fresh evaluation of T' is preceded by a collision of T'), the output at f'(e') is a DP (fresh, xi = 1), and T outputs the same DP at age a(t) + sigma(e') <= c - 1, before any slice check can cut it: T is not cut, a contradiction. If the run ends first, T, which is behind, is not cut either. So T' is cut before f'(e'), with all its evaluations from e' to the cut fresh. If all evaluations of T' from its start to the cut are fresh, they are >= c consecutive 0s containing e': J2b. Otherwise T' has a non-fresh evaluation before e', hence a joining collision before e' and before t; if it is at age <= c - 1, T' is in K_B with an earlier joining collision than T, against the choice of T; if not, the first c evaluations of T' were fresh and T' collided at age >= c - 1 while fresh: Y. QED.
Expected numbers of root events, each from the hazard (L1) (a collision of t with a given earlier value has conditional probability at most 1 / N' given G_(t-1), which includes the lottery, so lottery conditions can be attached):
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; the bound is `Q L / N' = 7.303e-06`.
- X: the same-lane and different-lane geometric-tail bound, the X term that the program charges, is `E_X <= Q L (2 + kappa) e^(-kappa/2) / N' = 6.785202e-12`.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^18) / N': E_J2a2 <= (Q + 2^18) L Q (Q - 1) / (2 N'^2). E_J2a = 7.252333e-06.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2 = 1.127013e-14.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 3.130592e-16.
Combining the fresh tail with the same S, X, J2a, J2b, and Y root-event bounds gives `P_cut = 1.455556e-05`. There is no cut-count premise.

Step 7 (the early halts and residual events). The early halts are the eighth cut, table full, key false match, stage-1 budget, or recovery failure.

Table capacity and key matches. Outside `P_60`, fewer than 60 collisions occur. The number of finished trails is then at most `N1 + 59`, so filling `tmax` entries requires `N1 >= tmax - 59`. The Chernoff bound is `P_table = 9.541748e-07`. A false 47-bit key match costs `P_key = 1.299401e-04`, using key space `2^36 * 2132`.

Sixty collisions. At a fresh evaluation t, the collision probability is at most `(t - 1 + 2^18) / N'`. For `w = e^5`, multiplication of the conditional moment bounds gives

```text
E[w^C] <= exp((w - 1) H),
P(C >= 60) <= exp(-300 + (e^5 - 1) H)
             = P_60 = 3.154787e-99.
```

Stage-1 budget. Let `eta_t` mark that the low 20 bits of the independent uniform value `V_t` are zero, and let `mu2 = Q / 2^20 = 323385964856750488281250000000000`. Fresh stage-1 hits are at most `sum eta_t`, which is `Binomial(Q, 2^-20)`. The multiplicative Chernoff bound gives

```text
P(fresh hits > 1.5 mu2) <= exp(-0.108 mu2)
                            = exp(-34925684204529052734375000000000)
                            < exp(-1000).
```

Repeated-hit partition. Work on `N1 <= k - 1` outside E1 and E2, as in Steps 2 through 6. Outside `P_60`, fewer than 60 fresh collisions occur, so there are at most 60 maximal replay windows. A replay window starts after a trail joins a previously evaluated orbit and ends at its next DP, cut, or halt. Split these windows into non-simple and simple windows according to whether an input repeats before the terminal DP.

Non-simple replay lemma. A non-simple replay is contained in the root-event union `S union X union J2a union J2b union Y` already charged inside `P_cut`. To see this, choose the non-simple replay whose first joining collision t is earliest, and call its target e'. If e' is on the trail of t, event S holds. Otherwise use the target trail T' from Step 6 (ii). If `a(t) + sigma(e') >= c`, event X holds. If T' has a fresh collision between e' and `f'(e')`, event J2a holds. Assume neither event occurs. If T' evaluates the segment from e' through `f'(e')` freshly, T replays that distinct segment and reaches its DP before age c. That is inconsistent with non-simplicity. The observed non-simple replay occurs before the run ends, so T' either is cut before `f'(e')` or has a nonfresh evaluation before e'. In the first case, an all-zero run of length c through e' gives J2b. If the trail was already nonfresh, take its first earlier joining collision. At age at least `c - 1`, that collision gives Y. Below age `c - 1`, if T' is cut before the downstream repeat, then T' is a nonfresh cut trail in `K_B`, and Step 6 (ii) gives S, X, J2a, J2b, or Y. If T' is not cut before the observed repeat, its replay follows the same DP-free suffix to that repeated input, so it is an earlier non-simple replay, contrary to the choice of t. This is the same exhaustive descent used in Step 6 (ii), with non-simplicity replacing the assumption that T is cut. A DP-free cycle is the direct special case: the collision that closes it is S when it closes on the same trail, and otherwise the descent gives X, J2a, J2b, or Y. The selected cycle is DP-free by construction because a first traversal ends upon reaching a DP. Step 6 bounds the occurrence of each root event, not only the final cut halt, so this use adds no second charge.

Simple replay lemma. Fix any deterministic 256-bit point z. Expose the random-function orbit from z until either an input repeats or M outputs have been sampled. Each output at a distinct input is an independent uniform 256-bit value. Pad the sequence with independent uniform values after the first repeat. Its low-20-zero indicators are then `M` independent `Bernoulli(2^-20)` variables. Every simple replay from z is a prefix of this sequence. A DP-ended prefix includes its terminal DP hit; a cut-ended or halt-ended prefix is shorter. In every case its stage-1 count is at most the count in the padded length-M sequence. Therefore its stage-1 count is bounded by `Binomial(M, 2^-20)`, and, since `2 ln 2 - 1 > 0.386`,

```text
P(a fixed simple replay has more than 2 M / 2^20 hits)
    <= exp(-0.386 M / 2^20).
```

The merge target may be selected adaptively from the earlier history. Rather than condition on that selection, take a union bound over all `N = 2^256` possible targets and all 60 replay windows. This simultaneous event covers every adaptive choice:

```text
P_replay-simple
    <= 60 * 2^256 * exp(-0.386 M / 2^20)
    = exp(-A_replay),
A_replay = 0.386 M / 2^20 - 256 ln 2 - ln 60
         = 32131256302220223666558513286.5205554195405...
         > 1000.
```

Appendix A evaluates `A_replay` downward and charges the outward upper bound `P_replay-simple < exp(-1000)`. It also checks

```text
240 M = 20948433704677848653711042374063267680
      <= 339094761485632000000000000000000000000 = Q.
```

Outside the root-event union and the new `P_replay-simple` term, each of the 60 replay windows has at most `2 M / 2^20` hits. Thus the repeated hits are at most `120 M / 2^20 <= mu2 / 2`. Together with at most `1.5 mu2` fresh hits, this is at most `2 mu2`, below `e2max = 2 mu2 + 64`. The residual probability of the stage-1 budget halt is below `P_stage-fresh + P_replay-simple < 2 exp(-1000)`, in addition to `P_60` and the root-event union already charged in `P_cut`.

Recovery and the three small structural events. A recovery without a pair comes from a false key match, already charged by `P_key`, or from one of the fewer than `2^18` starts lying on an evaluated trail. The latter event is `P_start = Q 2^18 / N = 7.676833e-34`. Outside those events, Lemma 1 returns a pair within `cr + 17 D` calls (when both trails have length <= cr; longer colliding trails are charged in `P_rec`). A repeated DP-valued output costs `P_DP-repeat = k^2 L / N' = 4.144913e-34`. A partner in the same batch costs `P_same-batch = 255 Q / N' = 7.467623e-37`.

The outward-rounded certificate gives `P_start + P_DP-repeat + P_same-batch + P_60 < 1.182922e-33`. It adds `P_stage-fresh` and the new `P_replay-simple` term to `residual_actual`; each is below `exp(-1000)`. The total fits inside the charged `2^-90 = 8.077936e-28` reserve of the program's float bound; the exact certificate of Appendix A charges the larger reserve `2^-89` (its output labels that row `2^-90 reserve`), which only lowers the certified bound. The certificate uses outward rounding for every exponential and rational term, so it needs no probabilistic rounding allowance. This proves the lemma. QED.
Consequently the printed float bound is

```text
1 - 0.608647478717 - 0.001141336522 - 7.303221e-06
  - 2.195540e-14 - 1.127013e-14 - 5.480453e-05
  - 3.626166e-06 - 1.455556e-05 - 2^-40
  - 1.299401e-04 - 9.541748e-07 - P_tiny
= 0.3900000010001293.
```

Appendix A independently certifies `P_F >= 0.390000001000 >= 0.39` with exact rationals and outward-rounded decimals.

Sensitivity is recomputed from the live plan by replacing N with `N/(1-eps)` and reoptimizing Tp and B:

| hazard deficit eps | replacement Tp | extra time bits to restore 0.39 |
| ---: | ---: | ---: |
| 0.01 | 2121 | 0.00725124 |
| 0.04 | 2078 | 0.03700836 |
| 0.10 | 2022 | 0.07585444 |
| 0.25 | 1846 | 0.20738722 |

A collision-hazard surplus helps. No robustness margin is treated as a theorem.

## 5. Premise H1 and its evidence

H1 compares this fixed function with a uniformly random function. Its four clauses are:

- (a) Distinct fresh evaluated inputs have independent uniform outputs and pair-collision hazard `2^-256`.
- (b) Iterates from the starts `r+t` have the first-collision law of a random mapping.
- (c) A fresh output is a DP with probability `2132/2^122`, independently of collision events.
- (d) Under the adaptive program history and later DP flags, a fresh output hits any fixed earlier non-DP output with probability at least `2^-256`.

Lemma 2 proves the bound for the random function. H1 transfers that bound to the fixed target. The circuit, ledger, memory, and random-function theorem are exact claims.

Support of H1 (stated; measured experiments cover width 16 and 16-bit projections of full-width points):

1. H1 is the generic premise of parallel collision search with distinguished points. Paul C. van Oorschot and Michael J. Wiener, "Parallel Collision Search with Cryptanalytic Applications", *Journal of Cryptology* 12(1):1-28, 1999, DOI 10.1007/PL00003816, model a fixed compression function iterated from fresh starts, without a chosen input difference, by a random function. The generic entries of this track use the same premise: mitchuski 3017c952, 1884db5b, and 4684dfc2; lamb356 3642e1cd; dariolina 6b678689; and 0xplemonade's 7523902c, 7347a2b6, 60dbf898, 332b47e1, 5ed693e8, ff37a322, c9ae3732 (round 64), and Jbenisek's e08e7b6a (round 41); 7347a2b6 is the current best round-41 entry.
2. Clause (d) fails in the adverse direction only if `g`, along its own iterates, collides less often than a random function by a constant factor `1 - eps`. Such a property would separate this 41-step function from a random function in a way that no published result shows. This entry chooses no input difference and uses no differential property.
3. A deviation that raises the collision hazard helps. Section 4 prices a deficit exactly: 0.00725124 bit for `eps = 0.01`, 0.03700836 bit for `eps = 0.05`, 0.07585444 bit for `eps = 0.10`, and 0.20738722 bit for `eps = 0.25`.
4. The program checks agree with random-function reference values at their scopes. For `proj-k0-w256`, 256 independent uniform 16-bit projections contain a pair with probability 0.392678 per trial, or 100.53 of 256 trials. The expected number of equal pairs is `C(256,2)/2^16 = 0.498047` per trial, or 127.50 over 256 trials. For the exact seven-batch `plan(16)` (unchanged from the round-40 package), the credited lazy-random-function reference over 10,000,000 complete mappings gave probability 0.6958435 with standard error 0.00014548, or 178.14 successes per 256 trials. A participant-run replay of both declared experiments reported by cda94445, using the organizer request format and organizer-style per-trial seeds derived from a substitute commitment (not the organizer's own seed material), returned 175 checked width-16 search pairs in 256 trials for `bssha-n16` and 106 checked full-width projection pairs in 256 trials for `proj-k0-w256`; every returned pair was recomputed with `verifier/hash_functions.py:digest(..., "sha256", 41)` and satisfied the declared low-16-bit event. These are within about 0.7 standard deviations of the references (sd about 7.4 and 7.8 trials). For this package, a replay on 48-trial requests (other substitute seeds) returned 35 and 20 pairs (references 33.4 and 18.8), every pair satisfying the declared event, with outputs byte-identical to those of the cda94445 source on the same requests (Appendix B.4). The organizer's own counts are produced by its executor at evaluation time. In bssha-n16 the width-16 plan keeps the recovery cap c + S, so this experiment does not exercise the cr cap of the width-256 plan. These are consistency checks that can expose implementation-level deviations. No count is used to change the score.

Limitation: measured experiments cover the complete width-16 search and 16-bit projections of 256 full-width points. The full-width collision hazard and `2^128`-scale success probability remain an explicit extrapolation under H1.

## 6. Experiments

Two organizer consistency checks run `experiments/bssha.py`. Before dispatch, `bounded_check` runs the byte-exact mirror of the normative C emitter. The organizer recomputes the complete digest of every returned message pair.
`bssha-n16`: per trial, one attempt of the 256-lane search at width 16 (DP = low 2 bits zero, plan(16): 7 batches, cut rule, table, recovery) on the walk g16(x) = the low 16 bits of the complete digest of M(x), x < 2^16. Each batch runs the shipped program on the 256 planes (the 240 high input planes zero), then the experiment's digest network (`DigestNet`, bit-sliced, experiment code only, not in the ledger) inverts walk B, forms cv1 = IV + state and runs block 2; the recovery runs the rolled recovery program and the same inverse and block 2 in scalar form. The trials run side by side: the planes of trial i occupy bits 256 i to 256 i + 255 of each word, so one pass of the program and of the digest network serves every live trial, and each bitwise record acts on every trial's 256 bits alone. The trial returns M(x), M(y) when the attempt succeeded and two nulls otherwise. Checked event: the messages are distinct and their complete 41-step digests agree in the low 16 bits. This is exact, because at width 16 the walk is those 16 digest bits. The width-16 walk differs from the width-256 walk g only in the map after the program (inverse, block 2, low 16 bits); it runs the same program, search, table and recovery.
`proj-k0-w256`: per trial, 256 points at width 256 (source by trial index mod 3: uniform from the seed, counter r + i, iterates of g from 256 seed-derived starts) evaluated with the shipped program; their complete digests are formed by the digest network; the trial returns two points whose digests agree in the low 16 bits when the set holds such a pair. Checked event: as above. It checks at full width the program, the inverse of walk B, the chaining value, block 2 and the message construction.
The experiments check execution, witnesses, and agreement with the scope-matched reference values in Section 5. Their counts do not enter the cost or success bound. The changes of this package alter the width-256 plan (memory layout, table size, `Tp`), the width-256 stage-1 test and the instruction stream of the kernel, not its function; the width-16 attempt and the 256-point projection execute the same code paths, and on the 48-trial requests used for the local replay (Section 5, Appendix B.4) the outputs of this package are byte-identical to those of the cda94445 source.
The digest network is built with the same `Gen` class as the kernel. Its inverse of walk B contains a four-variable sum with the nonzero constant `1 + K_39`. In the round-64 port the inherited four-word carry-fusion branch of `Gen._baseline` dropped the corresponding constant `1 + K_62` (the branch is reached when the chosen carry-in count is zero), so the branch is guarded by `not cv` (taken only when the absorbed constant is zero). The guard is kept unchanged from 26d9ad0b and 1f18d544; whether or not the branch is reached at round 41, the self-test checks the guarded digest network against scalar SHA-256. The guard does not change the kernel: all 16 kernel four-variable sums have zero constant, and the emitted stream hash is unchanged by it. The normative C emitter's `addm` contains the same branch (`nv == 4 && !bb`) without the guard; it is unaffected for the same reason, since the kernel has no four-variable sum with a nonzero constant (the C and Python streams are byte-identical). The self-test checks the digest network against scalar SHA-256 on 256 random full-width lanes.

## 7. Memory

Table: 540 groups * 47 words * 32 bytes = 812,160 bytes (138,240 slots). Slot t belongs to trail t: its `key + 1` is bit t mod 256 of the 47 words of group floor(t / 256); an all-zero slot is empty. The maximum key is 140,737,488,353,363, so `key + 1 < 2^47` and the sentinel transform fits.
Code: 45,302 body instructions * 4 bytes = 181,208 bytes. The shipped `experiments/bssha.py` is 65,420 bytes and remains inside the declared persistent code envelope, not in addition to it. The 466 recovery records use 2,330 bytes. The other 1,548 fixed 5-byte instructions (41 stage-1, 3 loop, 1,250 handler, 94 recovery control, 160 setup) use 7,740 bytes. Total code is 191,278 bytes.
Counters and copies use 16,384 bytes, of which the first 8,192 are the plane copy; the 66-word (2,112-byte) recovery array lies inside that copy and adds no memory (Appendix B.1). The 889 registers use 28,448 bytes. No advice. Memory peak is `max(687860,1048270) = 1048270` bytes, at most `2^20` (306 bytes of slack).
The table size is the largest that fits: `floor((2^20 - 191278 - 28448 - 16384) / 1504) * 256 - 263 = 540 * 256 - 263 = 137977`. Appendix A derives Tp = 2132 and certifies `P_F >= 0.39`.

## 8. Heuristics, conventions and what is credited

The premise is H1. The 889-register file and native formats are declared machine prices, not statistical premises. Lemma 2 proves the cut count. There is no advice.

Bases of this entry. cda94445-1839-4c4e-b188-a79d66f1bc4b (sraiw, round 41, `time_log2` 123.92331) supplies everything round-specific: the round-41 instantiation of the program (constants, emitter dimensions, the 884-data-register kernel and allocator, `_ch3` operand order, addition-choice and selector inventories, tail shear masks and polarity mask), the recovery prologue for (ROUNDS - 16) mod 4 = 1, the offsets, the experiments, and the round-41 text of Sections 1 to 6. d65d81b1-a243-4661-a418-4e2961ebc1e5 (samsmith, round 64, `time_log2` 124.12379) supplies, from its lineage, the changes applied here: f330da42-b03f-4ed5-90c1-de35c89fded1 and its predecessors 1edea573, d6e0ed78, b5e68e62 and 4efa37b5 (samsmith) the recovery array inside the plane copy, the bit-sliced 47-bit table, the 1,250-record handler allowance, the window search and the patch mechanism; c31fe915-4f3a-4dd2-8247-54a554490279 (newjordan, round 64, 124.12385) the weighted cascade stage-1 test of Section C (newjordan cites yukonautominer's split-filter counter and their own cascade entries on the BLAKE3 track as its model); d65d81b1 itself the live-range renames of Section D. newjordan's round-41 entry 3912cb79-ee34-468d-9b08-b22bcd310233 (`time_log2` 123.92303), the best round-41 entry before this one, applies the cascade test of c31fe915 to cda94445; it is cited for its score only, and no code or text of it is used.

Historical dependency scores and provenance follow. cda94445 credits bd7331be-ec65-4fe1-ab4b-2952af5fd39d (mpjunior92, round 41, published historical score 123.92470, 910 data registers) for the round-41 instantiation, tail masks, and rolled recovery prologue; c83bda97-88bb-4125-b581-5b76c6c7de6a (sraiw, round 64, published historical score 124.12598, 863 data registers) and e7631f7c-9d3e-489d-b7fc-6baac3a2ed45 (sraiw, round 63, published historical score 124.12095, 863 data registers) supply the bit-interleaved round and message-schedule emission, `_ch3` operand ordering, and `_MF` allocator non-target fallback that reduce the kernel from 45,312 to 45,311 gates and the register file from 910 to 884 data registers with zero moves; 26d9ad0b-e6f1-4370-abb4-b36aa97ab9e6 (mpjunior92, round 52) supplies the complete program `experiments/bssha.py` (kernel generator, normative C emitter, allocator, rolled recovery, search, table, plan, probability certificate and experiments), its round-port method and the structure and wording of this proof; its round-64 instance 1f18d544-cd04-4177-8739-fad19d55a98a supplies the recovery itemization and the digest-network guard. Through them, 27984c2d-fc4b-4285-a430-c5f364c10a7e (sraiw, round 40) supplies the program, f7b1dea4-2883-45d6-9c0c-89a5d4ad1b1a the recovery compaction, fb8a3bce-1839-4b9a-ab67-76670b4a05c9 the baseline package, b3f10279-3fa4-4d7b-9011-3faa2ae352c8 the fused kernel, schedule, allocator, and recovery design, and ff37a322-c5e7-4656-bb89-02f1a5d0e213 the native-4-byte machine and accounting base. The checkpoint recovery resolution (Step 6, the recovery charge of Section 3.3, the loss term P_rec of Lemma 2 Step 4 (f), RECOVERY_CODE = 94, and the Appendix A checkpoint accounting) is ported from Jbenisek's round-55 entry 93618c27-3783-4744-904a-5d688ff610f8 and round-63 entry a74a20c8-3a52-4742-8970-e20dc0ad8b76 (and akki-rock05's round-64 entry 068ba228-dd60-437d-b36d-6773fec1a7be), combined with the 863-data-register bit-interleaved schedule/allocator kernel (c83bda97-88bb-4125-b581-5b76c6c7de6a), with re-optimized age/recovery caps (KAPPA_256 = 35, KR = 62/5) and discrete Tp selection.

New here: the port itself (the merge of Appendix B), the window search on the round-41 kernel and its 9 rewrites (Section D), the round-41 wasm build and fuel measurement, the recovery start-state test for the round-41 recovery program (Appendix B.1), and the re-derived 137,977-trail plan (`Tp = 2132`), ledger, certificate and sensitivity tables.

## Section C. The weighted cascade stage-1 test (from c31fe915)

This section describes the stage-1 test of newjordan's round-64 entry c31fe915-4f3a-4dd2-8247-54a554490279 with this package's round-41 numbers. The mechanism, its caps and its probability argument are unchanged; only B, M and the kernel size differ.

### C1. What changes

cda94445 charges the full stage-1 test to every batch: 19 ORs, one NOT, one comparison and one branch, 22 operations. A lane is a stage-1 hit when its 20 low bits are zero.

This package replaces that test with a cascade that computes the same mask. Let A_j be the OR of the stored planes 0..j-1 (the planes are upright: `Prog` sets the polarity vector `pin` to zero). A batch "passes j" (a level-j event) when A_j differs from the all-ones word, that is, when some lane has its j low bits all zero. For a batch with 256 fresh evaluations the probability of that event is P_j = 1 - (1 - 2^-j)^256. The native sequence is:

1. Unconditional: initialize the accumulator from plane 0, OR planes 1..9 (9 ORs), then run the unchanged all-ones guard: **10 charged operations per batch** (immediate parent: 11; cda94445: 22). This computes the same A_10 because `0 OR P[0] OR ... OR P[9]` equals `P[0] OR ... OR P[9]`.
2. Level 10 (A_10 is not all ones): SUB w, w, 7; compare w < 0; branch to the halt (the guard check); OR planes 10 and 11; compare with all ones; branch to the loop control. Debit 7.
3. Levels 12, 14, 16: SUB w, w, 5; OR planes k and k + 1; compare with all ones; branch to the loop control. Debit 5 each.
4. Level 18: SUB w, w, 6; OR planes 18 and 19; compare with all ones; branch to the loop control; NOT. The result is the complement of A_20, cda94445's hit mask, and it enters the unchanged hit handler. Debit 6.

Every debit covers the whole work of its level, including the subtract and, at level 10, the guard's compare and branch. An early exit is charged the full debit (the final NOT is charged even when the level exits before it). The OR count is 19 (9 + 2 + 2 + 2 + 2 + 2), the plain 20-plane test's. The function `stage1c` of `experiments/bssha.py` is the semantic program of this sequence at width 256: it returns 0 when some level finds all ones and the complement of A_20 otherwise, which is exactly the mask of the plain test, and it debits the counter `cnt["g"]` by the weight of every level it enters and halts when the counter is negative after the level-10 debit. The reduced-width search of the experiments (n = 16) keeps the plain test, so the experiments are byte-identical in behavior.

The two new registers are the counter w, a signed 256-bit register, and an all-ones constant used by the comparisons. Both are set once before the search (2 operations, 2 records).

### C2. The work bound (deterministic)

For each level k in 10, 12, 14, 16, 18 let

p_k = ceil((1 + 2^-20) B P_k + 120 M / 2^k) + 64,

with B = 1324588912053250000000000000000000000 and M = c + S = 87285140436157702723796009891930282 (the M of Lemma 2). The counter starts at

U = 7 p10 + 5 p12 + 5 p14 + 5 p16 + 6 p18 = 2678064869068096623746628580370015179.

The caps are: k = 10: P_k = 0.221294, debit 7, p_k = 303353038007448076721519694340427750, 120 M / 2^k / (B P_k) = 0.0349; k = 12: P_k = 0.060594, debit 5, p_k = 82819538645796108100298759528942046, 120 M / 2^k / (B P_k) = 0.0319; k = 14: P_k = 0.015504, debit 5, p_k = 21175784533349727093017357216102452, 120 M / 2^k / (B P_k) = 0.0311; k = 16: P_k = 0.003899, debit 5, p_k = 5323950884833540458990894346120689, 120 M / 2^k / (B P_k) = 0.0309; k = 18: P_k = 0.000976, debit 6, p_k = 1332872116010534739075944088532499, 120 M / 2^k / (B P_k) = 0.0309. The only check follows the level-10 debit. When a check passes (w >= 0 after the debit), the debits so far are at most U. The same batch can add at most 5 + 5 + 5 + 6 = 21 more, and the next level-10 debit (7) then halts the run. So the conditional stage-1 work is at most U + 28 on every run, whatever g returns, and with the two register sets the ledger row is **U + 30 = 2678064869068096623746628580370015209** (`pbud(p) + GOV` in the program, `stage-1 cascade` in Appendix A). The unconditional part is conservatively charged as 10 operations in the batch body: 45,302 kernel instructions + 10 + 3 loop control = 45,315 operations per batch. The conditional cascade and guard envelope are unchanged.

In expectation the conditional work is sum of debit times P_k = 1.9549 operations per batch; the charged row is 2.0218 operations per batch, the difference being the cap margins (mostly the replay allowance 120 M / 2^k). Against the 22 operations per batch of cda94445's test and the immediate parent's 11-operation unconditional path, the charged stage-1 work falls to 10 + 2.0218 = 12.0218 operations per batch.

### C3. Probability

The guard halts only when some level count exceeds its cap. If for every level k the number of level-k batches is at most p_k, then at every check w >= U - sum of debit times count >= 0, and the run is, batch for batch, the run with the plain test: the same hits, table, cuts, recovery and output. So the cascade adds to the failure probability only the probability that some level count exceeds its cap, and the argument of Step 7 ("Stage-1 budget") applies to each level k with k low bits in place of 20:

- Fresh level-k batches. A batch is a fresh level-k batch when one of its fresh evaluations returns a value with its k low bits zero. Given the history, a batch has at most 256 fresh evaluations, each uniform and independent of the history, so it is a fresh level-k batch with conditional probability at most P_k. Over the at most B batches of the run the count is dominated by Binomial(B, P_k), and the multiplicative Chernoff bound gives P(count > (1 + 2^-20) B P_k) <= exp(-2^-40 B P_k / 3). Appendix A checks 2^-40 B P_k / 3 > 1000 for every level (the smallest, at k = 18, is about 3.9e20).
- Repeated level-k batches. A level-k batch that is not fresh contains a repeated evaluation whose value has its k low bits zero. Outside the root-event union already charged in P_cut, every repeated evaluation lies in one of at most 60 simple replay windows (Step 7, non-simple replay lemma). By the simple replay lemma with k in place of 20, a fixed simple replay of at most M outputs holds more than 2 M / 2^k values with k low bits zero with probability at most exp(-0.386 M / 2^k). The union over 60 windows and all 2^256 targets is at most exp(-(0.386 M / 2^k - 256 ln 2 - ln 60)); Appendix A checks that this exponent exceeds 1000 for every level (the smallest, at k = 18, is about 1.3e29). Outside it the repeated level-k batches are at most 120 M / 2^k.

On the complement of these two events the count is at most (1 + 2^-20) B P_k + 120 M / 2^k <= p_k - 64. The ten tails (fresh and replay for five levels), each below exp(-1000), are union-bounded with no independence assumed and are added to `residual_actual` in Appendix A (`P_cascade`), inside the charged residual reserve (2^-89 in Appendix A), which they do not exhaust. The stage-1 hit budget e2max and its two tails are cda94445's.

The plan of Appendix A is derived from this package's tmax (Section 7) with cda94445's procedure: Tp = 2132, and B is the least multiple of 10^21 at which the float bound reaches 0.390000001: B = 1324588912053250000000000000000000000. P_table = 9.541748e-07 and P_key = 1.299401e-04 (Section 4). Appendix A's exact certificate, with outward rounding, gives **P_F >= 0.390000001000 >= 0.39**; the float bound of Lemma 2 is 0.3900000010001293. The hazard-deficit table of Section 4 was recomputed for this plan.

H1 is cda94445's premise, unchanged. The declared machine has 889 registers.

### C4. Memory and code

The counter and the all-ones constant take two registers: the register file is 28,448 bytes (889 registers; cda94445: 887, 28,384 bytes). Direct initialization removes one executable fixed record, so the source computes 191,273 code bytes and 1,048,265 search bytes. The filing conservatively retains the immediate parent's 191,278-byte code envelope and 1,048,270-byte search envelope (memory term 0), leaving the removed five-byte record as charged slack. The shipped 65,420-byte Python module lies inside that persistent code envelope; it is not additional memory.

### C5. Ledger

The unchanged `stage-1 cascade` row U + 30 and the main loop at 45,315 operations per batch are in Section 3.4; Appendix A prints both.

### C6. Checks

`python3 -B bssha.py --ledger` and `--loss` print the plan, rows, N and Lemma 2 terms; `--selftest` prints True (bounded emitter and C-source hash, stream hash, builder equality, scalar and chained equivalence, recovery program, digest network and six width-16 search attempts); Appendix A, with the cascade caps, the per-level Chernoff and replay exponents and the `P_cascade` residual, runs end to end (output below). The cascade structure is inherited from c31fe915. For this derivative, independent verification compares parent and candidate `stage1c` masks and counter debits on deterministic edge panels and seeded random 256-lane panels, then replays the exact ledger and self-test. The setup loop `_Y5` starts at 256, increases monotonically, and reaches the asserted constant `Aq=350` after 95 tests. The search coroutine's `while True` exits when `Ac` raises `StopIteration`; `Ac` performs at most the declared `B` batches and each per-batch hit loop clears one of at most 256 lane bits. The fixed `random.Random(3)` occurs only inside the deterministic self-test; the attack path takes the fresh uniform `r` declared in Section 2 and the claim.

## Section D. Nine exact window rewrites (the method of d65d81b1 on the round-41 kernel)

### D1. The windows and their realization

The window search of d65d81b1 was run on the 45,311-gate round-41 kernel: all 218,254 connected sub-networks with at most 8 gates and at most 6 inputs, grouped by local function, each distinct function synthesised exactly over {XOR, AND, OR} by SAT (CaDiCaL), with the proof results of this author's earlier searches (rounds 64 and 58 and the rows of this sweep run before this one) reused for functions that also occur in those kernels. Nine pairwise disjoint windows have an exact replacement with one gate fewer. All nine are realized on the allocated stream.

Six need only the registers of their own spans. The other three (at records 1562 to 3581, 7897 to 7982 and 20084 to 20163 of the allocated stream, the same windows as in d65d81b1, since the first rounds of the two kernels coincide) first rename live ranges, as in d65d81b1. Renaming value X into register F changes the destination field of X's producer to F, and every source field that reads X to F. The reads of X are exactly the reads of the producer's old destination register from the producer up to and including the next record that writes that register. A rename is used only where F is not written, and its current content is not read, from X's producer through the last use of X in the rewritten stream, and F is not live at the end. Renaming changes no operation and no value. Four renames are used (one before the windows at 1562 and 20084, two before the window at 7897); together they rewrite 17 records in place.

Every window is then realised under the same rule: inside the replaced spans, and between the pieces of a window, every unchanged record reads its original values; after the window, every register that is read later holds its original value. These conditions were checked by a symbolic simulation of register contents (one label per value), and the result was checked functionally and formally (D4). The kernel falls from 45,311 to 45,302 instructions: 35,482 XOR, 6,049 AND and 3,771 OR, still in 884 data registers with zero moves. The per-batch body is 45,316 operations (45,302 + 11 + 3).

### D2. Encoding and both emitters

`PT` has 376 hexadecimal characters, in the format of d65d81b1. For each window it gives:
- its position or positions;
- the length L of each replaced span;
- L - 1 records, each an opcode and three indices into the list of the distinct registers of the replaced spans.

A group whose first hexadecimal digit h is at least 8 has h - 8 spans and carries renames: one digit m, then m entries of five digits (the original position of X's producer) and three digits (F). Both emitters apply a group's renames before they build the group's register list: the C routine `patch` and the Python mirror `_patch`. For each rename they map the original position to the current one (adding the record deltas of the spans already applied before it), set the producer's destination field to F, and walk forward. The walk replaces source fields equal to the old destination with F until a record writes the old destination, that record's sources included. The C loop is bounded by the stream length. The emitter numbers are in Section 3.6.

### D3. Program size

The program is 65,418 bytes (limit 65,536). `GEN_C` is recompressed as an LZMA-alone stream, and 0 internal identifiers, beyond those already renamed in d65d81b1, were renamed to two-character names. None of them appears in any other file of the package, in any string literal or as a keyword argument. `--ledger` prints identical output before and after these renames.

### D4. Checks run for this package

- **Simulation:** the patched 45,302-record stream computes the same outputs as the 45,311-record stream on the kernel's eight test vectors and on 20 random 256-lane inputs.
- **ABC `cec`** (`read_blif`, `strash`, `cec`) on the complete 45,311-instruction and 45,302-instruction netlists: "Networks are equivalent".
- **Emitter output:** the compiled wasm emitter, run in Wasmtime 50.0.1, writes the 45,302-record stream with the SHA-256 of Section 3.6. The Python mirror `_patch` produces the same stream from the ordinary builder's output (self-test).
- **Self-test and ledger:** `python3 -B bssha.py --selftest` prints True; `--ledger` prints the N of Section 3.4.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate, and `certify` recomputes the bound of Lemma 2 in exact rationals and 60-digit decimals with outward rounding: the line `P_lower certified` is a proved lower bound on P_F, asserted >= 0.39. The same numbers come from `python3 bssha.py --ledger`.

```python
from fractions import Fraction
CK = 1
KR = Fraction(62, 5)
REC1 = REC2 = 39
CHK, PROBE, RECFIX = 80, 100, 600
from math import log, exp, log2, log1p, comb, expm1, isqrt

PH, PREFILT, FILT, LOOP, LANES = 45302, 10, 41, 3, 256   # PREFILT: unconditional stage-1 operations; FILT: stage-1 cascade records (Section C)
CASC = ((10, 12, 7), (12, 14, 5), (14, 16, 5), (16, 18, 5), (18, 20, 6))   # cascade groups (first plane, end plane, debit), Section C
GOV = 30                                       # overshoot 28 + the two register sets
PREFILTER_PLANES, STAGE1_GUARD_TAIL, STAGE1_PASS_MULT = 12, 3, 2
REST = FILT - PREFILT + STAGE1_GUARD_TAIL
INSTR_REC = 45302
PH7, EXTRA, RECINIT = 1453, 39, 78
N_BITS, S1, W, KAPPA = 256, 20, 102, 35         # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE = 2800, 3800, 4200, 1300
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 7
CUT_HALT_ORDER = CMAX + 1
assert CUT_HALT_ORDER == 8
WASM_RUN_OPERATORS, WASM_OPERATOR_FACTOR = 102032006, 2
BODYB, CTRLB, RECB, REC_RECORDS = 4, 5, 5, 466
CONTROL, REGFILE, COUNTERS, ADVICE, ARRAYS = 1457 + 47 * CK, 28448, 16384, 0, 0   # ARRAYS = 0: the 2,112-byte recovery array lies inside the dead 8,192-byte plane copy; handler allowance 1,250 records
KEYB = 47                                      # key+1; zero is the unwritten sentinel
GROUP, GROUPB = 256, KEYB * 32                  # bit-sliced table: 256 trail numbers per group of KEYB 32-byte words
SEARCH_EVAL_OPS = 1 << 48
OFFSET_SEARCH = 1641 * SEARCH_EVAL_OPS            # 64 endpoint + 1 initial + 3 * 192 coordinate + 1000 perturbation builds
SELECTOR_SEARCH = 427 * SEARCH_EVAL_OPS
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 21, 18                        # B is a multiple of GRAIN; trail numbers are below 2^18
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + PREFILT + LOOP
code_bytes = INSTR_REC * BODYB + REC_RECORDS * RECB + (FILT + LOOP + CONTROL) * CTRLB
tmax = ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE - ARRAYS) // GROUPB * GROUP - LANES - CMAX  # stored trails: one slot per trail number (LANES starts + tmax + CMAX cuts)
table_bytes = -(-(tmax + LANES + CMAX) // GROUP) * GROUPB
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48
KCHK = table_bytes // 64 - 1
assert (KCHK + 1) * 64 <= table_bytes


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
    kr = float(KR) * Lf
    prec = CK * 2 * hq * exp(-(kr - 1) * th) * (1 + (kr - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** TB * Q) / Np
    cuts = 1 - sum(comb(n2, j) * p ** j * exp((n2 - j) * log1p(-p)) for j in range(CUT_HALT_ORDER))
    t = [pi(Q) * shift, delay * shift, ql, (cf + SB) * Q * p * (q + LANES) / ((1 - p) * Np), hq * p2, prec, hq * Lf * (Q + 2.0 ** TB) / Np, 2.0 ** -40,
         cuts + ql * (1 + (2 + KAPPA) * exp(-KAPPA / 2) + 2 * hq) + hq * p * (3 + 2 * KAPPA),
         tmax * (tmax - 1) / 2 * 2.0 ** -(min(KEYB - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp)), 2.0 ** tail_log2(q, tmax - 59),
         Q * 2.0 ** TB / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** -90 + 2.0 ** -90]
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
    upr = lambda x: x * (1 + Dm("1e-40"))
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
    p_start = fd(Fraction(Q << TB, Nn), True)
    p_dp_repeat = fd(Fraction(k * k) * L / Np, True)
    p_same_batch = fd(Fraction(255 * Q, Np), True)
    exp5 = up(Dm(5).exp())
    p_60 = upr((-Dm(300) + (exp5 - 1) * fd(H, True)).exp())
    fresh_exponent = Fraction(108 * Q, 1000 * (1 << S1))
    replay_raw_exponent = Fraction(386 * M, 1000 * (1 << S1))
    replay_exponent = fd(replay_raw_exponent, False) - 256 * upr(Dm(2).ln()) - upr(Dm(60).ln())
    assert fresh_exponent > 1000 and replay_exponent > 1000 and 240 * M <= Q
    for k0, _, _ in CASC:                                         # Section C: each cascade level count exceeds its cap with probability < 2 e^-1000
        Pk = 1 - Fraction((1 << k0) - 1, 1 << k0) ** LANES
        assert Fraction(1, 1 << 40) * B * Pk / 3 > 1000         # Chernoff, fresh level-k batches above (1 + 2^-20) B P_k
        assert fd(Fraction(386 * M, 1000 * (1 << k0)), False) - 256 * upr(Dm(2).ln()) - upr(Dm(60).ln()) > 1000   # 60 simple replay windows
    exp_minus_1000 = upr(Dm(-1000).exp())
    p_stage_fresh = exp_minus_1000
    p_replay_simple = exp_minus_1000
    p_cascade = 2 * len(CASC) * exp_minus_1000                   # Section C: the five level caps, fresh and replay tails (replaces the passing-budget guard term)
    residual_actual = p_start + p_dp_repeat + p_same_batch + p_60 + p_stage_fresh + p_replay_simple + p_cascade
    residual_reserve = Dm(2) ** -89
    assert residual_actual < residual_reserve
    residual_slack = residual_reserve - residual_actual
    p_tiny = p_start + p_dp_repeat + p_same_batch + p_60 + residual_reserve
    terms = [pi_up(Q) * shift, delay,                            # collision (no partner), detection delay
             fd(Q * L / Np, True),                               # the partner is on the trail of t
             up(fd(Fraction(M * Q) / Np, True) * EK),            # the partner is on a trail with c free evaluations
             fd(PP, True) * p2,                                  # trail of t too old when the DP is reached
             CK * 2 * fd(PP, True) * ex(-(KR * L - 1) * th) * fd(1 + (KR * L - 1) * th / (1 - th), True),   # P_rec
             fd(PP * L * (Q + (1 << TB)) / Np, True),            # a collision on the rest of the path
             Dm(2) ** -40,                                       # N1 >= k
             up(1 - sum(comb(n2, j) * p ** j * (1 - p) ** (n2 - j) for j in range(CUT_HALT_ORDER))),   # step 6: fresh cut trails, P(Bin(n2, p) >= CMAX + 1)
             fd(Q * L / Np, True),                               # S
             fd(Q / Np, True) * fd(L, True) * ex(-(c - 2) * th / 2) * fd(2 + (c - 1) * th, True) + fd(PP, True) * p2,   # X
             fd(Q * L * H / Np + (Q + (1 << TB)) * L * PP / Np, True),   # J2a
             fd(PP * (1 - th), True) * p2, ex(-(c - 1) * th) * fd(H, True),   # J2b, Y
             fd(Fraction(tmax * (tmax - 1), 2 * Tp) / (1 << min(KEYB - (Tp - 1).bit_length(), N_BITS - D)), True),   # key false match
             up((-qd + (tmax - 59) * (1 + (qu / (tmax - 59)).ln())).exp()),   # table capacity
             p_tiny]
    residual = {"P_start": p_start, "P_DP-repeat": p_dp_repeat,
                "P_same-batch": p_same_batch, "P_60": p_60,
                "fresh exponent": fd(fresh_exponent, False),
                "replay exponent": replay_exponent,
                "P_stage-fresh": p_stage_fresh,
                "P_replay-simple": p_replay_simple,
                "P_cascade": p_cascade,
                "residual actual": residual_actual,
                "2^-90 reserve": residual_reserve,
                "reserve slack": residual_slack, "P_tiny charged": p_tiny}
    return 1 - sum(terms), residual


lo, hi = 1.0, float(tmax - 59)                                 # the largest mean number of trails the table holds (tail within 2^-20)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax - 59) <= -20 else (lo, mid)
a, z = 1, 4097                                                 # bisection: a Tp that reaches 0.39 at that mean (any Tp is a valid plan; not claimed optimal)
while z - a > 1:
    m = (a + z) // 2
    a, z = (m, z) if plower(m, lo) >= P_MIN else (a, m)
Tp = min((a, a + 1), key=lambda t: (plan_tp(t)[1], t))
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
cr = -(-(KR * L.numerator) // L.denominator)
DCK = -(-cr // KCHK)
emitter = WASM_OPERATOR_FACTOR * WASM_RUN_OPERATORS + 1
def pcap(k0):                                                  # p_k = ceil((1 + 2^-20) B P_k + 120 M / 2^k) + 64 (Section C)
    f = (1 + Fraction(1, 1 << 20)) * B * (1 - Fraction((1 << k0) - 1, 1 << k0) ** LANES) + Fraction(120 * (c + SB), 1 << k0)
    return -(-f.numerator // f.denominator) + 64
U = sum(w * pcap(k0) for k0, _, w in CASC)
rows = [("main loop: B * %d" % body, body * B),
        ("stage-1 cascade: U + 30", U + GOV),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished events: (tmax + 1) * (3800 + 6 * (tmax + 263))", (tmax + 1) * (EVENT + 6 * (tmax + LANES + CMAX))),
        ("cut trails: 7 * 4200", CMAX * CUTOPS),
        ("recovery", (cr * (PH7 + REC1) + KCHK * CHK + 17 * DCK * (PH7 + REC2) + 16 * PROBE + RECFIX + RECINIT) if CK else 2 * capr * (PH7 + EXTRA) + 600 + RECINIT),
        ("setup and generator", SETUP_FIXED + emitter),
        ("charged offset search", OFFSET_SEARCH),
        ("charged selector search", SELECTOR_SEARCH)]
N = int(sum(v for _, v in rows))
assert N == 60074435816065403106810366381900294477380
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", table_bytes + code_bytes + REGFILE + COUNTERS + ADVICE + ARRAYS)
print("P_lower = %.5f" % plower(Tp, float(B * LANES / L)))
pc, residual = certify(Tp, B)
print("P_lower certified (exact rationals, 60-digit decimals) = %s" % str(pc)[:14])
assert pc >= Fraction(39, 100)
for name, value in residual.items():
    print("residual %-16s %s" % (name, value))
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 2980
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
Tp = 2132  tmax = 137977  B = 1324588912053250000000000000000000000  e2max = 646771929713500976562500000000064  c = 87285140436157702723514534915219626
memory bytes = 1048270
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000001000
residual P_start          7.67683334331292933271255737930568462790181857886113424989299E-34
residual P_DP-repeat      4.14491252938749243074282157797850744161247232134733185556026E-34
residual P_same-batch     7.46762276666563789307289936722927232772626816214909487285468E-37
residual P_60             3.15478694032053443234534852804372038787315141811441408779489E-99
residual fresh exponent   34925684204529052734375000000000
residual replay exponent  32131256302220223666558513286.5205554195405426824831080936417
residual P_stage-fresh    5.07595889754945676529180947957433691930610687878259230750892E-435
residual P_replay-simple  5.07595889754945676529180947957433691930610687878259230750892E-435
residual P_cascade        5.07595889754945676529180947957433691930610687878259230750892E-434
residual residual actual  1.18292134954670874013484518566514213418420171683706152003261E-33
residual 2^-90 reserve    1.61558713389263217748322010169914619837072677910327911376953E-27
residual reserve slack    1.61558595097128263077447996685396053322859259490156227670801E-27
residual P_tiny charged   1.61558831681398172419196023654433186351286096330499595083105E-27
main loop: B * 45315                                 60023746549693023750000000000000000000000
stage-1 cascade: U + 30                              2678064869068096623746628580370015209
slice checks: ceil(B / 2^48) * 1300                  6117650690630771492807100
stage-1 hits: e2max * 2800                           1810961403197802734375000000000179200
finished events: (tmax + 1) * (3800 + 6 * (tmax + 263)) 114968788720
cut trails: 7 * 4200                                 29400
recovery                                             46200240100107339800972032181420143530
setup and generator                                  204877613
charged offset search                                461900436782186496
charged selector search                              120189815055450112
N = 60074435816065403106810366381900294477380
certificate: 2^12392277 * 2980^100000 <= N^100000 < 2^12392278 * 2980^100000
log2(N/C) = 123.9227783746
time_log2 = 123.92278
```

## Appendix B. Changes relative to cda94445

The program is cda94445's with the changes that d65d81b1 and its lineage made to 6ea56109, the round-64 instance of the same program. It was produced by a three-way merge, first of the statements of `experiments/bssha.py` and then of the embedded C source, with b6ffba81 (sraiw's round-58 instance) as the base and this author's round-58 port 56b698c6 (b6ffba81 with d65d81b1's changes, merged the same way from 6ea56109) and cda94445 as the two sides. Before the merge, the identifiers of b6ffba81 and cda94445 were mapped to the names of 56b698c6 by aligning the token streams of the programs (the three name some locals differently); the mapping renames names only. The C sources merged without conflict, and the program merge had no unresolved conflict after the mapping; every hunk in which the merged program differs from 56b698c6 was checked by hand. Each is either one of cda94445's round-41 changes or one of d65d81b1's changes:
- **cda94445's round-41 changes:** round count and cost unit, round constants, tail shear masks, polarity mask, register count, node and record limits, `_ch3` operand order, the addition-choice and selector inventories, and the recovery prologue and its tail copies.
- **Recorded constants:** the round-58 values of the emitter info, hashes and `WASM_RUN_OPERATORS` that 56b698c6 carries were replaced by placeholders and recomputed by the build (below).

After the merge, `PT` was regenerated for the round-41 kernel (Section D), the wasm emitter was rebuilt and re-measured, and the program constants that record it were set.

| quantity | cda94445 | this package |
| --- | ---: | ---: |
| table | 6-byte slots, 135,287 slots | 540 groups of 47 words, 138,240 slots |
| table bytes | 811,722 | 812,160 |
| recovery array | separate, 2,112 bytes | inside the plane copy |
| handler allowance (records) | 1,000 | 1,250 |
| stage-1 charge | full 20-plane test every batch (22) | weighted cascade with direct init: 10 every batch + row U + 30 (Section C) |
| kernel instructions | 45,311 | 45,302 |
| registers | 887 | 889 |
| code bytes | 189,969 | 191,278 |
| tmax (stored trails) | 135,024 | 137,977 |
| Tp | 2086 | 2132 |
| P_key (false key match) | 6.359084e-05 | 1.299401e-04 |
| per-batch body (operations) | 45,336 | 45,315 |
| B (batches) | 1324499565109662000000000000000000000 | 1324588912053250000000000000000000000 |
| cr (recovery cap) | 31605804693639418646226668355659200 | 30923878325953014679188006655677811 |
| kchk (checkpoints) | 12682 | 12689 |
| N (word operations) | 60096542195273113206711709022419654133703 | 60074435816065403106810366381900294477380 |
| log2(N / 2980) | 123.923309164405 | 123.922778374616 |
| claimed time_log2 | 123.92331 | 123.92278 |
| search memory (bytes) | 1,048,571 | 1,048,270 |
| setup memory (bytes) | 657,010 | 687,860 |

The program differs from cda94445 in these groups of lines:
- **Recovery array:** `ARRAYS = 0`, and the assertion `ARRAY_BYTES <= PLANE_COPY <= COUNTERS` that the 2,112-byte array fits in the 8,192-byte plane copy.
- **Bit-sliced table:** `KEYB = 47`, `GROUP_BYTES = KEYB * 32`, and the table capacity of the plan.
- **Handler allowance:** `HANDLER_CODE = 1250`.
- **Cascade:** `stage1c`, `pcap`, `pbud`, `CASC`, `GOV`, the two extra registers in `REGFILE`, and the `stage-1 cascade` ledger row in place of the stage-1 term of the body.
- **Window rewrites:** `PT` and `patch` in `GEN_C`, and `_patch` in the Python mirror, applied in `BoundedEmitter.run` and in the self-test's builder comparison.
- **Recorded emitter constants:** `EXPECTED_EMITTER_INFO`, the C-source, stream and wasm hashes, `WASM_RUN_OPERATORS` and `WASM_EMITTER_INSTR`.
- **Size:** the recompressed `GEN_C`, and the internal identifier renames of d65d81b1 and Section D3.

### B.1 The recovery array inside the plane copy

What is in the plane copy and when. The stage-1 hit stores the 256 planes to the 8 KiB copy (256 stores, Section 3.3). The finished-trail routine reloads the planes from it at its end. Between two hits the copy holds stale data that nothing reads before the next hit rewrites it.

When step 6 starts. Step 6 is entered only from step 3, inside the finished-trail routine, after the scan has found `key + 1` in the table. At that moment the routine holds t0 (from the scan), t1 = t (from the lane arrays) and r, and step 6 needs nothing else: the trails are s_t = r + t. Step 6 ends the attempt: it returns a pair or halts (Section 2, step 5), and no path returns to the search, so the planes are never reloaded after it starts. The plane copy is therefore dead from the first operation of step 6 on. cda94445 uses the same fact for the table: its pass 1 writes `kchk` = floor(table_bytes / 64) - 1 checkpoints of 64 bytes into the table (Section 2, step 6), which is dead from the same moment.

Where the array is and what it needs. The recovery program's 66 array words (41 schedule words and the 25 constants K10..K34) occupy the first 2,112 bytes of the plane copy, which has 8,192 bytes (inside the 16,384 counter bytes that the ledger already counts), so the ledger takes `ARRAYS = 0`. The 78 one-time initialization records, charged in the fixed operations of the recovery, run after the planes are dead. They write 32 of the 66 words (the 25 round constants and the 7 constant schedule words). Every array word that a call reads before writing it is one of these 32, and no call changes the 32. Registers: a call reads 18 registers besides its 8 input registers before writing them; 14 are set by the initialization, and the other 4 (registers 3, 4, 7, 8) are zero-valued. Ten of these registers are overwritten by a call and are re-set before each call (4 zero-valued: 3, 4, 7, 8; 6 holding their initialization values: 5, 6, 10, 11, 12, 30). These are the 10 re-sets already charged inside the 39 surrounding operations of each recovery batch (Section 3.3), so nothing is added to the recovery charge. These counts were derived by tracing the round-41 recovery program; they coincide with those of the round-64 program of d65d81b1 except for the array size and the number of words written by the initialization.

Test. A script outside the package traced the 78 initialization records and then six consecutive calls, with the 10 re-sets before each call, for ten recoveries. Before the initialization, the array words and all 32 registers were set to zeros, to random values, or to `None`, so that any read of an unwritten word or register would raise an error (five combinations). In every combination all 60 calls of the ten recoveries returned g exactly as the scalar reference does. With the re-sets skipped the same test fails, so it can detect such a dependence.

What is not claimed. The registers of the declared machine are not addressable memory, so nothing is overlaid on them; only the RAM-to-RAM overlay above is used.

### B.2 The table

Why a bit-sliced layout. The saving of narrower keys is realized only if slots are packed without padding. Contiguous 47-bit slots would need access at bit offsets: unaligned loads, or 256 code copies, one per alignment class, because gcd(47, 256) = 1. Evaluated at round 64 (Appendix B.2 of d65d81b1), such a plan is worth only about 0.000006 bit more, and it rests on an addressing mechanism the declared machine does not itemize. The bit-sliced table uses 47 bits per slot exactly, with aligned accesses and immediate shifts only; its cost is rounding the table to whole groups of 1,504 bytes (here 306 bytes of slack remain).

Why 47 bits. P_key, the probability of a false key match, grows by a factor 2 per bit removed, while a bit saved buys 2.1 percent more slots. The immediate parent's exact key-width table is retained below as a conservative sensitivity table. Its rows use the parent's 11-operation unconditional charge; direct initialization removes one charged operation per batch from each corresponding fixed plan, so none of these inherited bounds understates candidate work:

| key bits | Tp | tmax | groups | P_key | time_log2 (unrounded) | claim |
| --- | --- | --- | --- | --- | --- | --- |
| 45 | 2226 | 144,121 | 564 | 5.4313e-04 | 123.923630674 | 123.92364 |
| 46 | 2175 | 140,793 | 551 | 2.6525e-04 | 123.923055216 | 123.92306 |
| **47** | **2132** | **137,977** | **540** | **1.2994e-04** | **123.922810184** | **123.92282** |
| 48 | 2084 | 134,905 | 528 | 6.3540e-05 | 123.922740914 | 123.92275 |
| 49 | 2044 | 132,345 | 518 | 1.5587e-05 | 123.922704152 | 123.92271 |

Every row is a plan by the same program with only `KEYB` changed, and each is certified by the same bound; 47 is the minimum. P_key (1.2994e-04) is charged in the success probability of Lemma 2 and in the certificate of Appendix A.

### B.3 What is declared rather than derived, and sensitivity

1. Handler-code allowance. As in cda94445, the handler is not listed record by record; its size is a declared allowance of 5-byte records. This package declares 1,250, of which the new table routines need at most 133 (Section 3.3.1) and the inherited routines need what cda94445 declares for them. Conservative inherited-parent sensitivity (the direct-init saving is not applied to these alternative rows): any allowance up to 1,311 gives the same plan (306 bytes of slack are 61 records); 1,312 to 1,612 gives 539 groups (claim 123.92282); 1,613 to 1,912 gives 538 groups (claim 123.92283); and 1,913 to 2,000 gives 537 groups (claim 123.92284). The claim stays below 123.92331 for every allowance up to 2,000 records, and below newjordan's 123.92303 as well.
2. Scan price. The ledger keeps the six operations per slot of cda94445; the routine of Section 3.3.1 needs 1.68 (232,284 / 138,240, write included). The routine's work would have to be 6 * 138,240 / 232,284 = 3.57 times larger than counted before it exceeded the charge, and the events are 1.1e11 of 6.0e40 operations, so even a tenfold error would move the claim by less than 1e-29 bit.
3. Lifetime argument (B.1). It rests on the control flow of Section 2 (step 6 is final) and on the recovery program's start-state test above.
4. Everything cda94445 declares is unchanged and not re-derived here: the 2,800, 3,800, 1,300 and 4,200 operation charges, the 1,000-record handler allowance included in the 1,250, the 39 surrounding operations, the 887-register file (889 with the two cascade registers), and the premise H1 with its sensitivity (Section 5).

### B.4 Checks that were run

All local, in an isolated sandbox without network, on the final source:
- **Self-test:** `python3 experiments/bssha.py --selftest` exits 0, including the assertions that every key is below 2^47 and every trail number below 2^18.
- **Appendix A:** the program prints the N and certificate above (`P_lower certified = 0.390000001000`), the same N that `--ledger` prints.
- **Experiments:** the two declared experiments, replayed on 48-trial requests with substitute seeds, return byte-identical outputs from this program and from the cda94445 source. 35 of 48 trials of `bssha-n16` and 20 of 48 trials of `proj-k0-w256` return a pair. Every returned pair was recomputed with `verifier/hash_functions.py:digest(..., "sha256", 41)` and agrees in digest bytes 30 and 31.
- **Table routines:** the routines of Section 3.3.1 are d65d81b1's, unchanged. Its model check on 256-bit integers covered the one-hot construction for all 256 indices, inserts, lookups and the operation counts.
- **Window rewrites:** the patched stream was checked on the kernel's eight test vectors and on 20 random 256-lane inputs. ABC (`cec`) reported the complete 45,311-instruction and 45,302-instruction netlists equivalent, and the compiled wasm emitter, run in Wasmtime, emits the verified stream byte for byte.
- **Recovery start state:** the start-state test of B.1 was run on this package's recovery program.
- **Recomputed tables:** the key-width table (B.2), the handler-allowance sensitivity (B.3) and the hazard-deficit table (Section 4) were recomputed for this package.
- **Package check:** `scripts/pareto_candidate.py --family sha256 --rounds 41` reports the package ready.

### B.5 Corrections of inherited text

Statements of cda94445 that disagree with its own program or numbers are not carried over:
- **Binomial tail:** Lemma 2, Step 6 (i), states the order-8 binomial tail of `Binomial(n2, p)` as 3.1320e-56, while the stated formula gives about 7e-86 at its plan. This text gives the exact value of the stated formula at this package's plan.
