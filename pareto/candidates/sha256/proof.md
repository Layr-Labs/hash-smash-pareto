# sha256-r64: an 85,805-instruction native bit-sliced birthday walk, with the recovery array inside the dead plane copy, a bit-sliced 47-bit trail table, and a weighted cascade stage-1 test

This package is a credited derivative of newjordan's round-64 entry c31fe915-4f3a-4dd2-8247-54a554490279 (`time_log2` 124.12385), itself a credited derivative of samsmith's f330da42-b03f-4ed5-90c1-de35c89fded1 (124.12387). It changes one thing: the four SAT-proved one-gate window replacements that both predecessors leave unused are applied too, by first renaming the live ranges of five values into registers that are free over the extended range. The kernel falls from 85,809 to 85,805 instructions and the claim from 124.12385 to 124.12379. Section D (before Appendix A) states the change, why it is exact, and every moved number; the moved numbers are also updated in place below. Nothing else changes: the cascade, the walk, the table, the recovery, Lemma 2, the plan and the experiments are c31fe915's.

The base c31fe915 changes one thing relative to f330da42, the stage-1 test that runs after every batch: it becomes a cascade whose conditional work is enforced and charged through one capped weighted counter. Section C (before Appendix A) states the change, its deterministic work bound, its probability argument and the moved numbers. Everything else is the predecessor's: the kernel, the emitters, the walk, the table, the recovery, Lemma 2 and the experiments. The text below is the predecessor's, with the numbers that move updated in place; first-person passages, Appendix B and the history of the lineage are samsmith's and sraiw's. Section C supersedes the predecessor's two-stage prefilter charge (item (4), Section 3.3.1a, Appendix B.6).

This package is a derivative of the round-64 entry 6ea56109-6ec6-4623-96c7-4c005c54463e (sraiw, commit 8065669, `time_log2` 124.12440). It carries that entry's complete program `experiments/bssha.py` and the structure and wording of its proof, and it changes how the search memory is laid out. The kernel is that of 6ea56109 after twenty-five exact one-gate window rewrites (item (5) and Section D): 67,482 XOR, 11,023 AND, and 7,300 OR native instructions, or 85,805 in total, allocated in 863 data registers with zero moves. So are, apart from the final rewrite step of item (5) that both generators now apply, the two generators (the bounded Python generator and the freestanding C emitter build the same network, and the self-test requires byte equality, scalar equivalence, chained-walk equivalence, zero moves, recovery equivalence, and complete two-block digest agreement), the addition-choice selector, the six offsets, the rolled recovery program (452 records, 2,670 executed per call), the walk and the probability model.

What changed relative to 6ea56109 is two layout decisions, one declared allowance, the charge of the stage-1 test, and one exact kernel rewrite step, and nothing else (Appendix B lists every changed line of the program and justifies each). (1) The 112-word recovery array (3,584 bytes) is no longer a separate allocation: it is stored in the first 3,584 bytes of the 8,192-byte plane copy, which no step reads once step 6 begins. 6ea56109 already stores its pass-1 checkpoints in the table, which is dead from the same moment. (2) Trail keys have 47 bits (the 36 bits of x above bit 121 and the 11-bit code of F) instead of 48, and they are held in a bit-sliced table of 432 groups of 256 trail numbers with 47 words of 32 bytes per group (Section 3.3.1). The table has 110,592 slots instead of 108,153 and needs only aligned 256-bit loads and stores and immediate shifts. (3) The declared handler code is 1,250 five-byte records instead of 1,000; the table routines of Section 3.3.1 need at most 133 of them. (4) The stage-1 distinguished-point test is charged as a two-stage prefilter: a 12-plane prefilter is charged to every batch, and the remaining 8 planes plus a passing-budget guard are charged only to the batches that pass it (expected fraction `1 - (1 - 2^-12)^256 = 0.0606`), as on the BLAKE3 and SHA3 tracks (Section 3.3.1a, Appendix B.6). This lowers the per-batch body from 85,855 to 85,847 operations and adds one guarded cost row; it does not touch the search, the table, or the plan. (5) Twenty-five disjoint windows of the kernel (3 to 11 consecutive records each, nine of them in two or three separate pieces) are replaced by windows with one record fewer. The windows were found by an exhaustive search over the connected sub-networks of the 85,830-gate kernel with at most 8 gates and at most 6 inputs: the local function of each window was synthesised exactly over {XOR, AND, OR} by SAT (CaDiCaL), and 25 pairwise disjoint windows with a replacement of one gate fewer were found; a replacement was accepted only where the solver proved that it computes the same function of the window's inputs on all input patterns (no don't-care assumptions are used). The emitter applies the replacements in place to the allocated record stream, after the allocator has run, by the table `PT` of `GEN_C` (943 hexadecimal characters: for each window its position or positions, the length L of each replaced span, and L - 1 records, each written as an opcode and three indices into the list of the distinct registers of the replaced spans; for four windows also one or two live-range renames, Section D). All 25 proved windows are used: 21 (as in f330da42 and c31fe915) need only the registers of their own spans, and the other four first rename the live range of one or two values into a register that is free over the extended range (Section D). Every replacement leaves the registers that later records read and write unchanged: it is validated by a symbolic simulation of register contents, so no other record changes (later records move up by the number of records saved). This lowers the instruction count from 85,830 to 85,805: in f330da42 the 21 windows lowered the per-batch body from 85,847 to 85,826 and the claim by 0.00035 bit, and the four of Section D lower the body (with the cascade of Section C) from 85,823 to 85,819 and the claim by a further 0.000067 bit. The step is an exact equivalence, not a premise: besides the SAT proofs, ABC combinational equivalence checking proves the complete 85,830-instruction and 85,805-instruction netlists equal on all 2^256 inputs (Appendix B.4 and Section D), and the self-test compares the emitted kernel with the word-level SHA-256 walk. With (1) to (3), `tmax` = 110,329 (107,890 in 6ea56109) and `Tp` = 1701 (1663); the plan, memory, table geometry and probability certificate are exactly those of items (1) to (3), and only the ledger's cost rows move. The exact plan, ledger and certificate are re-derived by the program of Appendix A, which is that of 6ea56109 with these constants.

The native body instruction remains exactly 32 bits: a 2-bit opcode and three 10-bit register fields. The machine executes it directly for one word operation. No decoder or interpreter runs in the priced path. The body occupies 343,220 bytes. Control and recovery use native fixed 5-byte instructions.

The six-offset search evaluates 1,641 complete builds. The ledger reserves one baseline and two passes over all 463 alternatives in the 100-site reduction inventory, or 927 complete builds. Every build is charged at `2^48` operations. The emitted selector sets site 76 to 1 (covered by pass 1 of the charged 927-build selector audit) and all other 99 sites to 0. The final plan uses 110,329 completed trails in 110,592 bit-sliced sentinel slots (432 groups of 256 trail numbers). Search memory is 1,047,108 bytes (`<= 1,048,576`).

The exact ledger is

```
N = 113825532506474517424596925128261686934717 word operations
log2(N / 4912) = 124.123781253700
```

The claim rounds upward to `time_log2 = 124.12379`. This entry is a derivative of c31fe915-4f3a-4dd2-8247-54a554490279 (newjordan, `time_log2` 124.12385): it changes only the kernel, by the four window rewrites of Section D, which moves the instruction count, the main-loop row and the setup row; the plan (tmax, Tp, B) and the certificate are those of c31fe915, which is a derivative of f330da42-b03f-4ed5-90c1-de35c89fded1 (samsmith, 124.12387) that replaces the two-stage prefilter by the cascade of Section C and lets the table capacity, Tp, B and the certificate follow the larger code and register file. Setup memory is 893,331 bytes. H1, the fixed-function random-function comparison stated in Sections 4 and 5, is the only score-critical premise. Circuit changes, counts, and memory bounds are exact checked claims, not premises. The prices that this package declares in addition to those of 6ea56109 are the handler-code allowance of item (3) and the lifetime argument of item (1) (Appendix B.1 and B.3).

## 1. Target and relation

Target `sha256-r64-prefix-v1` (the Pareto lane `sha256`, round 64, the full SHA-256 step count). The two colliding messages have 64 bytes each. With x a 256-bit integer and y0..y7 its eight 32-bit words (big-endian, y0 the highest), M(x) is the 16 big-endian words W0..W15 with
- W0..W7 = the constant words 3e73281c, 752d8ed2, ad19eff1, 7250fceb, d4095422, 44fdb519, 43f22c5b, d8d6aac4 (computed from the standard IV by `_anchor_prefix` so that the eight new a-words of steps 0..7 are K9 - K8, -K9, 0, 0, 0, 0, 0, 0; the working state after step 7 is therefore (a,b,c,d,e,f,g,h) = (0, 0, 0, 0, 0, 0, -K9, K9 - K8), which makes steps 8 and 9 cheap),
- W8 = y0, W9 = y1, and W(8+k) = y_k - K(8+k) modulo 2^32 for k = 2..7.
FIPS 180-4 padding appends 0x80, 55 zero bytes and the 64-bit length 512: the padded message is 128 bytes, two blocks, and block 2 is the same for every x. The target runs the steps 0 to 63 on each block, block 1 from the standard IV and block 2 from the chaining value cv1 = IV + s(x) word by word, where s(x) is the working state after step 63 of block 1; the digest is the result of block 2 with its feed-forward (`verifier/hash_functions.py:digest(M(x), "sha256", 64)`). The profile's message domain is "finite byte strings of bit length below 2^64"; a 64-byte string is in it.
Write a_i, e_i for the a and e words after i steps of block 1 (a_0, e_0 from the IV), T1_i for the T1 of the step that produces them and W_j for the schedule word of step j. With the fixed 32-bit polarity masks `QM = 0x0772d77a` and `XM = 0xa2c126f1`, f(x) is walk B (4684dfc2) with per-bit polarity-matched disjoint-support shears on Q and X. Define the eight words bw = [e_61, e_62, a_57, a_58, Q, T1_60, X, Y] with X = e_59 + Ch(e_62, XM, e_60) + W_62 (at bit j: `e_62[j] | e_60[j]` when `(XM >> j) & 1 == 1` and `~e_62[j] & e_60[j]` when `(XM >> j) & 1 == 0`; since `Ch(e2, e3, e4) = Ch(e2, XM, e4) + (e2 & e3 & ~XM) - (e2 & ~e3 & XM) mod 2^32`, the inverse adds `(e2 & e3 & ~XM) - (e2 & ~e3 & XM)`), Q = T1_59 + Ch(a_58 ^ a_57, a_56, QM) (at bit j: `~(a_58[j] ^ a_57[j]) | a_56[j]` when `(QM >> j) & 1 == 1` and `(a_58[j] ^ a_57[j]) & a_56[j]` when `(QM >> j) & 1 == 0`; since `Maj(a6, a7, a8) = Ch(a6 ^ a7, a8, QM) + (a6 & a7 & ~QM) - (~a6 & ~a7 & QM) mod 2^32`, the inverse adds `(a6 & a7 & ~QM) - (~a6 & ~a7 & QM)`), and Y = e_60 + W_63. Then f(x) is the 256-bit integer whose eight 32-bit words, most significant first, are bw[6], bw[1], bw[7], bw[0], bw[5], bw[4], bw[2], bw[3] = X, e_62, Y, e_61, T1_60, Q, a_57, a_58 (the permutation PERM = (6, 1, 7, 0, 5, 4, 2, 3), the order with no register move, Section 3.2; `enc_words`, `words_of` and `int_of` in the program). In particular the low 32 bits of f(x), which hold the distinguished-point test bits of Section 2, are a_58, and the next word up is a_57. In the program these are bw = [E[r-3], E[r-2], A[r-7], A[r-6], ..., T[r-4], ...] with r = 64. These words determine s(x): the program's `enc_invert` recovers a_59 = Q + (a_58 & a_57 & ~QM) - (~a_58 & ~a_57 & QM) + Sigma0(a_58), then a_60, a_61, a_62, the T1 of steps 62 (= X + (e_62 & e_61 & ~XM) - (e_62 & ~e_61 & XM) + Sigma1(e_62) + K_62) and 63 and the whole state, by additions, subtractions and the round functions. The walk is g(x) = f(x) XOR q, q the fixed 256-bit mask `22273a6c5e8abef676dc5de11e7bc9e3468ac54393e15c2405e9e8acbfb29d63` (134 output planes that the generator leaves complemented instead of spending a NOT).
So g(x) = g(y) gives s(x) = s(y), hence the same cv1, the same block 2 and equal digests. x != y gives M(x) != M(y), since x -> W8..W15 is a bijection. The attack outputs two distinct 64-byte messages with equal complete 256-bit digests.
The selftest (`python3 bssha.py --selftest`) compares the program with scalar g on 2,560 lanes, including all-zero and all-one inputs, checks four chained steps, checks the inverse on 10,000 random states, checks the recovery program and experiment digest network, and runs six width-16 search attempts. It also runs the independent ordinary builder and requires byte equality with the normative bounded emitter.

### 1.1 Choice of the tail shear masks

`QM` and `XM` only choose, bit by bit, which of two disjoint-support forms of Maj and Ch enters the encoded words Q and X; `enc_invert` adds back the exact difference, so every choice gives a bijective encoding of the same state and the same collision relation. The round-40 masks were tuned to the round-40 constants. For round 64 they were re-chosen in 1f18d544 by a greedy single-bit pass over the 64 mask bits, starting from the round-40 values, accepting a flip only when the kernel instruction count strictly decreased: 85,866 instructions with the round-40 masks, 85,831 with the shipped masks (and 85,830 with bit-interleaved emission and `_ch3` operand ordering) (and 85,830 once site 76 is enabled). This is a participant-side choice of two constants of the walk (64 complete count-only builds); its cost is covered by the charged offset-search envelope of Section 3.2 at `2^48` operations per build, and no claim depends on its optimality.

## 2. The attack (program `experiments/bssha.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished when its low 20 bits are zero and the 102-bit number F = (x >> 20) mod 2^102 is below Tp = 1701. Thus D = 122, theta = 1701 / 2^122, and L = 5316911983139663491615228241121378304 / 1701 = 2^111.26783. The key is the 36 bits of x above bit 121 followed by the 11-bit encoding of F. It has 47 bits; F < 1701 < 2^11.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated program of Section 3.2. The start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 20 low planes are all zero. If it is zero, the next batch runs at once. In this entry the test is the cascade of Section C: it stops as soon as no lane can still have its low bits zero, and the mask it hands to step 3 is the same.
3. For each set bit of the mask, the lane is extracted and the window test F < Tp decides whether it is a DP. If `key + 1` is in the table, go to step 6. Otherwise write `key + 1` into slot t of the bit-sliced table of Section 3.3.1 and start the next trail in that lane. Zero is the unwritten sentinel. The slot position is t, so neither t nor the length is stored.
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = ceil(35 L) batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the weighted stage-1 counter is negative at its check (Section C), when the table holds 110,329 keys, when an eighth trail would be cut (`CMAX = 7`), or if step 6 finds no pair.
6. Recovery (checkpoint resolution). Pass 1 walks the two trails together for at most cr = ceil((62/5) L) = 38759381887673031920063980123400995 calls, recording every D-th point of each unfinished trail (D = ceil(cr / kchk) = 3818282128625064714812725851976, kchk = floor(table_bytes / 64) - 1 = 10151) and the two terminal lengths and endpoints; if either trail has not reached a DP within cr steps, the attempt halts. Pass 2 aligns the longer trail to each checkpoint of the shorter trail by a walk of (l_long - l_short) mod D < D steps, locates by binary search the last checkpoint pair where the aligned walks still differ (at most ceil(log2(kchk + 1)) <= 16 probes of < D steps each), and steps the two trails together from that checkpoint pair for at most D steps until their next values agree. The first predecessor pair a != b with g(a) = g(b) is returned. Step 6 needs only r, t0 and t1: the plane copy and the table are dead from its start, the 3,584-byte recovery array is placed at the start of the plane copy and the checkpoints in the table (Appendix B.1). The rolled two-lane program has 452 fixed 5-byte records in total, of which 125 are one-time initialization records, and executes 2,670 records per call. Pass 1 runs at most cr calls and pass 2 runs at most 17 D calls.
Constants printed by `--ledger`: Tp = 1701, L = 5316911983139663491615228241121378304 / 1701, B = 1325066062655416000000000000000000000, Q = 339216912039786496000000000000000000000, e2max = 647004913405964843750000000000064, c = 109401481134560977193728976154760871, cr = 38759381887673031920063980123400995, kchk = 10151, capr = 109401481134560977194010451131471527, and tmax = 110,329. The 110,592 total slots (432 groups of 256 trail numbers) cover 256 initial trails, all stored trails, and seven cut trails. The maximum trail number is 110,591 < 2^18; the boundary test asserts it.
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is a constant of the program).

## 3. Operation ledger

### 3.1 Machine
Machine model of this entry (declared cost-model prices). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices operations and memory; it gives no register count and no instruction size. For round 64 the organizer contract sets `reference_operation_cost = 4912` (`python3 scripts/pareto_candidate.py --family sha256 --rounds 64 --show-contract`).
This entry declares a load/store machine with 256-bit words and 868 registers, 863 data registers, three pointer registers and the two registers of the stage-1 cascade (Section C). Charged, one operation each: every XOR, AND, OR and NOT of a 256-bit register, every register move, every set of a register to a constant, every load and store, every pointer addition, comparison and conditional branch, and the one random word. Nothing is free except renaming a bit-sliced rotation.
The body uses this machine's native fixed 32-bit instruction: a 2-bit opcode and three 10-bit register fields. Opcode values 0, 1, and 2 mean XOR, AND, and OR; 3 is reserved. The machine fetches and executes each instruction directly for one operation. There is no decoder or interpreter in the priced path. `Prog.run`, `Prog.compile`, and `Prog.fast` are test mirrors only. All 85,830 kernel instructions use the native format, so the body occupies 343,320 bytes. Recovery and control use native fixed 40-bit instructions. Every executed instruction costs one word operation.

### 3.2 One batch = 85,819 operations charged to every batch, for 256 trails
Representation is bit-sliced: one 256-bit machine word holds one bit position for 256 trails, and a SHA-256 rotation only renames planes. Signals carry a node and a free polarity bit. The pivot full adder costs five gates. `add3` carries the pair `(u,U)`, representing `1 if U else 2u`; its T0, T1, and T2 templates cost nine gates per ordinary column and eight at bit 30. The self-test exhausts all 32 input rows for each template relation.

The round fusion passes `h[0]` and `u[0] = h[0] XOR Ch[0]` into `add3`. Bit 0 combines the half-adder on the other two operands with the `h + Ch` carry in seven gates for either absorbed carry. At bit 1, `_add_u` begins from a carry-free root and may use the alternate `ch1 = f1 XOR (~e1 AND (f1 XOR g1))` form when its stored polarity avoids a penalty, while `_adduc` folds the round constant into `h + u` across suffix columns `m..31` using the 96-word `UCD` template table. The selector absorbs `c0 + 2c1 + delta` into the folded constant, and splits `W[16]` and `W[23]` into carry-saved sums plus deferred constants across steps 19..24. These are exact rearrangements of `h + Ch + Sigma1 + K + W` and are checked against scalar SHA-256.

For every four-variable sum with zero absorbed constant, `addm` orders `(A,B,D,C)`, computes `add3(A,B,C)` with the bit-0 half-adder carry `D0`, and then adds `[0,D1..D31]`. The outgoing bit-0 carry occupies the otherwise unused pair-carry slot at bit 1, so the second adder's bit 1 is a two-gate half adder. At round 64 there are 39 such sums (the 15 of round 40 plus the 24 schedule words W38..W61; at round 64, W62 and W63 are three-operand sums because their `sigma1` terms are deferred into X and Y); 38 use this baseline and site 76 (`W[53]`) uses selector choice `1` (the first three-of-four `add3` reduction followed by `add2`), which saves one gate by CSE interaction with step 53.

The walk-B tail uses the per-bit shears `QM = 0x0772d77a` and `XM = 0xa2c126f1`. `_ch3` fuses `B + Ch` into the first `add3`: each column forms `w5 = hg XOR (e AND (f XOR g))` and selects a polarity-matched multiset of `[W,a,Sigma1(e)]`. Its column relation is exhaustively checked. `enc_invert` applies the matching Q and X corrections, so equal walk values imply equal block-1 states and complete digests. The tail also defers the `sigma1` terms of W_62 and W_63 into X and Y (W_62 and W_63 are formed only as `W(i-16) + sigma0(W(i-15)) + W(i-7)`), which is exact because X and Y are the only consumers of W_62 and W_63.

The schedule advances `W[21]` and `s23_raw` to step 19, defers the constant adders for `W[22]` and `W[23]` until after their rounds, advances `W[32]` to step 31, and interleaves the bit-level emission of `Sigma0(a)` and `Maj(a,b,c)` inside `add3` and the `sigma0`/`sigma1` bit generators inside `W[21]`, `s23_raw`, and `W[24..63]`, so intermediate rotation/XOR nodes are consumed immediately and freed within the same column. The streaming allocator routes short-lived nodes (`uses <= 3` before the output horizon) into idle output targets (excluding `W[8]` and liberating `W[14]` closer to the horizon) with tiered fallback masks (`_MF`) and otherwise takes a dying operand or the lowest free non-target register. The output permutation `(6,1,7,0,5,4,2,3)` needs zero moves. With 863 data registers the shipped allocator emits zero moves, and the register file is priced at that size.

Per-step cost at round 64: steady rounds cost 1,211 to 1,223 instructions and schedule words W24..W63 cost 543 to 544 instructions each (W53 costs 543 with selector choice 1; the last two, without their deferred `sigma1`, are cheaper); rounds 9..15 cost 436, 776, 872, and 1,148 four times. The equivalent counts of c9ae3732 are 1,214 to 1,233 per steady round and 545 per schedule word. The ported kernel's advantage is the fused round columns, the earlier-round constant folding, site 76, and the tail.

The six offsets are preprocessing output. Their deterministic search evaluates exactly 1,641 complete candidates: 64 endpoint placements, one initial coordinate point, three complete sweeps of 192 bits, and 1,000 perturbations from the fixed xorshift seed `6a09e667bb67ae85`. Bits are visited by increasing word and then increasing bit. A strict improvement replaces the incumbent, so ties retain the earlier candidate. The shipped offsets are those of 27984c2d (`W(8+k) = y_k - K(8+k)`); the 1,641-build envelope is charged as an upper bound on offset-selection work and is not claimed to reproduce them. All other count-only work done for round 64 is covered by the two charged envelopes (1,641 + 927 = 2,568 builds at `2^48` each): the mask pass of Section 1.1 (two passes, at most 129 builds), the pass over the 463 addition-choice alternatives in the 100-site inventory that selected site 76 = 1, the register-count and pass-1 order scan, and the 12-point plan scan over the cut age and `CMAX`.

The addition audit is also charged preprocessing. Among 100 nonconstant `addm` sites, 51 have exactly three operands (44 three-variable sums and 7 two-variable sums with a constant) and admit one three-of-three reduction. Forty-one have four operands (39 four-variable sums and 2 three-variable sums with a constant) and admit four three-of-four reductions plus six unordered pair-first reductions; the two with a constant also admit the constant-carry form. The remaining eight sites have fewer than three operands. One complete pass therefore has

```text
51 + 41 * 10 + 2 = 463 alternatives.
```

The charged validation envelope contains the deterministic fused baseline and all 463 alternatives in two complete passes. Its emitted hint table sets site 76 to `1` (found in pass 1 of the 463-alternative audit) and all other 99 sites to `0`. The envelope is `1 + 2 * 463 = 927` complete builds.

Both searches use a count-only builder with an eight-probe CSE table and an eight-entry recent-gate ring. One complete build has at most two builder passes, 160 multiword sums, 64 first-triple masks per sum, 32 columns, 13 current-column forms, 13 lookahead forms, and 12 trial gates per form. Charging 1,024 word operations for each trial gate, including lookup, rollback, and bookkeeping, gives

```text
2 * 160 * 64 * 32 * 13 * 13 * 12 * 1024
= 1,360,967,761,920 < 2^41 operations.
```

One more copy covers the rest of the network, scoring, comparisons, loop control, and deterministic candidate generation. The round-64 build has 100 multiword sums, below the 160 of the envelope, and the bounded emitter performs 337,942 helper calls for both passes together. The package charges `2^48` operations per complete build, more than 100 times that doubled structural bound (2^48 / (2 * 1,360,967,761,920) = 103.4). The exact search charges are

```text
offsets:  1641 * 2^48 = 461900436782186496 operations
selector:  927 * 2^48 = 260927303410778112 operations.
```

These bounds follow the loops and fixed array limits. They do not rely on a development call counter or an unshipped trace.

Executed per batch: 67,482 XOR + 11,023 AND + 7,300 OR = 85,805 gates; zero NOT, set, move, load, store, or control instructions. Per lane evaluation (one evaluation of g in one lane) this is 335.191 operations.
Validation is by the bounded emitter, its stream hash, the independent builder comparison, the exhaustive algebraic checks inherited from the frontier, and the scalar and end-to-end tests described in Sections 1 and 6.
The generator runs once at the start; its work is charged in the setup row (3.3), its code and peak storage in Sections 3.6 and 7.

### 3.3 Loop, stage 1, handlers and the other events
One batch: 85,805 body instructions + unconditional stage-1 work 11 + loop control 3 = 85,819 operations charged to every batch. Stage 1 is the weighted cascade of Section C, which replaces the predecessor's two-stage prefilter (Section 3.3.1a): in every batch 9 ORs fold planes 0 to 9, one comparison with the all-ones register and one branch skip the rest when no lane has those 10 bits zero; the conditional levels (planes 10 to 19, the guard check and the final NOT) are paid through a capped weighted counter, charged once as the `stage-1 cascade` row of Section 3.4. A DP has all 20 low bits zero, so its lane is flagged.
Loop control of the batch loop: counter increment, compare with the next slice limit, branch back: 3 operations.
Handlers are charged per event at the stated operation bounds and stored as fixed 5-byte control records:
- Stage-1 hit: store the 256 planes to an 8 KiB copy (256 stores), extract the lane (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (at most 15), counters. Below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail: key formation, sentinel encoding, the slot write, the new start, insertion of its 256 bits, reload of the planes, lane arrays, and counters fit below 3,800 operations. The scan of the table for `key + 1` is charged six operations per slot, including extraction, comparison, and branch; the routine of Section 3.3.1 needs 1.68 per slot. The source increments the counter and scans before its `finished > tmax` halt, so the ledger charges `tmax + 1` handled events. At most `tmax` keys are stored.
- Slice check (every 2^48 batches): charged **1,300** each. Cut trail: charged **4,200**; at most 7 cut trails (`CMAX = 7`).
- Recovery program (`RecProg`): a second program evaluates g for two chain values at once, in bits 0..31 and 128..159 of each word. The message and constant array has 112 words (64 schedule words and the 48 constants K10..K57 of the loop), or 3,584 bytes. The array lies in the first 3,584 bytes of the 8 KiB plane copy, which is dead when the recovery starts (Appendix B.1); the one-time initialization (125 records, charged in the fixed operations of the recovery below) writes it at the start of the recovery. Preloaded tail constants, masks, `W0 + K0`, and `W8 - K9` remove repeated setup; the preloaded offsets and the state registers that a call overwrites are re-set before each call and charged in the recovery batch below. The live-register permutation across the four-round body and four-word schedule step avoids register-move instructions. There are 452 fixed 5-byte records in total (125 one-time initialization records and 327 records of the per-call program) and 2,670 executed records per call.
- Recovery batch: one call (2,670 records) plus at most 39 surrounding operations, or 2,709 operations per batch, the same in both passes (pass 1 runs at most cr = 38759381887673031920063980123400995 batches plus kchk * 80 = 10151 * 80 checkpoint-store operations; pass 2 runs at most 17 * D = 17 * 3818282128625064714812725851976 batches plus 16 * 100 probe operations and 600 + 125 fixed operations; 47 additional 5-byte control instructions, RECOVERY_CODE = 94 vs 47, hold the two-pass checkpoint and binary-search control). The 39 are itemized as: 10 re-sets of registers whose start value the call reads and that a call overwrites, 2 copies saving the predecessor pair, 9 for the two-lane equality test, 12 for the pass-1 DP test, 3 for counter increment, cap comparison and branch, and 3 spare. Every call is charged all 39 regardless of pass.
- Setup and emitter: fixed work is 813,600. Section 3.6 gives the participant-measured 203,093,252 wasm operators. Charging two word operations per measured operator plus one gives `813600 + 2 * 203093252 + 1 = 407000105` operations.
Code size: 343,220 bytes of body instructions, 2,260 bytes for 452 recovery instructions, and 7,740 bytes for the other 1,548 control instructions (the stage-1 cascade has 41 records where the stage-1 code of f330da42 had 22, Section C). Total code is 353,220 bytes.

### 3.3.1 Bit-sliced trail table

6ea56109 keeps the keys in 6-byte slots and charges six operations per slot for the scan. This package keeps 47-bit keys in a bit-sliced table, which needs no sub-word addressing.

Layout. Trail numbers are grouped by 256. Group g, 0 <= g < 432, is 47 consecutive 32-byte words W[g][0..46] (1,504 bytes); bit i of W[g][b] is bit b of `key + 1` of trail 256 g + i. An unwritten slot is 47 zero bits; since `key + 1 >= 1`, it equals no key. The table has 432 * 47 * 32 = 649,728 bytes and 110,592 slots (`tmax` + 263: the 256 initial trails, at most `tmax` stored trails, and seven cut trails). Every access is an aligned 256-bit load or store at an immediate word offset from a group pointer, and every shift is by an immediate.

Scan (step 3: is `key + 1` in the table?). Let k be the 47-bit `key + 1` in a register. The pointer is set to the table start (1 operation). For each group, a copy kr of k and an accumulator acc = 0 are made, and for b = 0, ..., 46: load W[g][b]; K = 0 - (kr & 1), which is all ones if bit b of k is 1 and zero otherwise; acc = acc | (W[g][b] ^ K); kr = kr >> 1; advance the pointer; compare with the group end; branch. That is 9 operations per word. A zero bit i of acc means that all 47 bits of slot 256 g + i equal k. After the 47 words, the complement of acc (one XOR with all ones) is tested by a branch on nonzero. Per group: 47 * 9 + 2 (copy, clear) + 1 + 1 + 2 (loop compare and branch) = 429 operations; for 432 groups and the pointer set-up 185,329 operations, or 1.676 per slot. If the complement is nonzero in a group g', the lowest set bit i' is found by the halving routine of the stage-1 hit (at most 8 steps of 5 operations = 40), t0 = 256 g' + i' is the trail of the earlier key, and the program goes to step 6; this happens at most once per attempt.

Write (step 3, no match). Let t = 256 g + i be the trail number of the lane (from the lane arrays); g = t >> 8 and i = t & 255 take 2 operations. The one-hot word E = 1 << i is made by eight conditional shifts: E = 1; for k = 0, ..., 7: mask = 0 - ((i >> k) & 1) (3 operations), X = E << 2^k (1), E = E ^ ((E ^ X) & mask) (3); 57 operations in all. The group offset 1504 g = (g << 10) + (g << 9) - (g << 5) takes 5 operations and 1 move to a pointer register. Then kr = k (1) and, for b = 0, ..., 46: load W; K = 0 - (kr & 1) (2); W = W ^ ((W ^ K) & E) (3); store; kr = kr >> 1; advance the pointer, compare, branch (3), that is 11 operations per word. Total 2 + 57 + 5 + 1 + 1 + 47 * 11 = 583 operations.

Cost and code. The table work of one finished-trail event is at most 185,329 + 40 + 583 = 185,952 operations. The ledger already charges 6 * 110,592 = 663,552 operations per event for the scan alone (Section 3.3, finished trail), and the 3,800 operations charged for the rest of the event are unchanged, so the new routines fit inside the existing charge with a factor of more than 3.5 to spare. The three constants 0, 1 and all ones are set once per event (3 operations, inside the 3,800). The routines take at most 133 five-byte records (scan: 9 in the loop, 2 before it, 4 after it and 1 for the pointer, 16 in all; write: 2 + 57 + 5 + 1 + 1 + 11 = 77; 40 more if the lane-finding routine of the stage-1 hit is copied rather than shared), against a declared handler-code allowance that grows from 1,000 to 1,250 records. The 1,000 of 6ea56109 already include its own table routines, which this package no longer uses. That allowance is a declared price, like the 1,000 of 6ea56109, and is not itemized; Appendix B.3 gives its sensitivity.

### 3.3.1a The two-stage distinguished-point prefilter
*Superseded in this entry by the cascade of Section C; this subsection describes the predecessor's charge and its numbers.*

The stage-1 test asks whether any of the 256 lanes reached a distinguished point, that is, has its low 20 bits zero. It is the same predicate as in 6ea56109, charged in two stages. First a 12-plane prefilter (the low 12 of the 20 planes) is ANDed and branched on: 11 ORs, one comparison, one branch, 14 operations, charged to every batch in the per-batch body. A lane with all 20 low bits zero necessarily has its low 12 zero, so the prefilter never misses a distinguished point; it is exact, not probabilistic. Only a batch in which some lane passes the prefilter runs the remaining 8 planes, the hit branch, and the passing-budget-guard decrement, 11 operations, charged in the separate `stage-1 pass` row.

A batch passes the prefilter with probability `P12 = 1 - (1 - 2^-12)^256 = 0.0606` (exact rational in Appendix A). The number of passing batches over the run is `Binomial(B, P12)` with mean `m = ceil(B * P12)`. The passing-budget guard is a down-counter that halts the attempt if the passing count exceeds `Bpass = m + ceil(sqrt(126 m)) = m + isqrt(126 m) + 1`, so the `stage-1 pass` charge `Bpass * 11` is a certified upper bound, not an average. This is the same device 6ea56109 applies to the stage-1 hit count through `e2max` (Section 2, step 5; the hit guard `cnt["stage1_hits"] > e2max`), but charged at the tight Chernoff-optimal margin rather than the conservative `2x` the predecessor and `e2max` use: the slack `t = ceil(sqrt(126 m))` is chosen so the Chernoff bound `P(Binomial(B, P12) >= m + t) <= exp(-t^2 / (2 m + 2 t / 3)) <= exp(-63) < 2^-90` holds (with `t ~ sqrt(126 m)` and `t << m`, `t^2 / (2 m) = 63`). Because the mean `m ~ 8.0e34` is so large, this tight margin makes `Bpass` essentially `m` (the slack `t ~ 3.2e18` is `~4e-17` of `m`), halving the `stage-1 pass` charge relative to the `2x` predecessor while keeping the halt a certified `<= 2^-90` event. That halt is charged explicitly in Lemma 2: it is the extra `2^-90` term added to the residual, and the residual reserve is raised to `2^-89` to cover it (Appendix A `residual_reserve`, Lemma 2 Step 7); the certified `P_lower` is unchanged at `0.390000001000`. The guard's down-counter is a handler record inside the declared 1,250-record allowance of Section 3.3.1 (at most ten records; the table and guard routines together stay below 143 of the 1,250), so it adds no code and the memory, table geometry, `tmax`, `Tp`, `B` are exactly those of items (1) to (3) of the introduction.

The charge is a refinement of the stage-1 cost only, with no change to the search, the collisions found, the table, or the plan; it mirrors the stage-1 prefilter of the BLAKE3 entries `a7f7020b` and `e6b316ce` and the SHA3 entries on this challenge (Section 8, Appendix B.6).

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 85,819 | 113,715,844,431,025,145,704,000,000,000,000,000,000,000 |
| stage-1 cascade: U + 30 (Section C) | 2,701,452,811,253,085,602,513,764,546,052,482,456 |
| slice checks: ceil(B / 2^48) * 1,300 | 6,119,854,423,943,283,450,172,200 |
| stage-1 hits: e2max * 2,800 | 1,811,613,757,536,701,562,500,000,000,000,179,200 |
| finished events: 110,330 * (3,800 + 6 * 110,592) | 73,628,946,160 |
| cut trails: 7 * 4,200 | 29,400 |
| recovery: cr * (2,670 + 39) + kchk * 80 + 17 * D * (2,670 + 39) + 16 * 100 + 600 + 125 | 105,175,008,880,575,813,576,764,592,617,955,160,588 |
| setup and generator | 407,000,105 |
| charged offset search | 461,900,436,782,186,496 |
| charged selector search | 260,927,303,410,778,112 |
N = 113,825,532,506,474,517,424,596,925,128,261,686,934,717 operations.
N / 4912 has log2 124.123781254. Claim `time_log2` = 124.12379, rounded upward. The walk never computes block 2: equal block-1 states give equal digests, so one evaluation of g is one block-1 compression of 64 steps, priced by its instructions.

### 3.5 Register file and smaller files
Declared prices: the machine has 868 registers of 256 bits: 863 data registers (Section 3.2), three pointers, and the two registers of the stage-1 cascade (the weighted counter w and the all-ones constant, Section C). The register file is counted as 27,776 bytes.

### 3.6 Bounded emitter and peak setup storage

The freestanding C source embedded in `experiments/bssha.py` as `GEN_C` is the normative setup implementation. `python3 experiments/bssha.py --gen-c` prints its exact 29,762 bytes. Its SHA-256 is `c89231ab59be22066b852d68196a338f22091c34d214ac9abc63e8f3acb499bd`. Pass 0 counts uses and output nodes. Pass 1 rebuilds the same network, allocates registers online, and writes native 32-bit instructions directly to the final code buffer. The emitter enforces `MAX_NODES = 86,123`, `MAX_RECORDS = 85,830`, 863 data registers, a 1,024-slot CSE table, at most 900 occupied slots, and every packed-field bound.

The C emitter reports the 15-field tuple

```text
(records=85805, registers=863, nodes=86087, calls=337942,
 moves=0, error=0, XOR=67482, AND=11023, OR=7300,
 code=343320, counters=16384, uses=86123, state=32000,
 choices=100, constants=1680).
```

The emitted byte stream has SHA-256 `6ef09eeca51528903e6ef94498359c4d57b5526d847d684f32f693d59dcaa856`. Its polarity mask is `22273a6c5e8abef676dc5de11e7bc9e3468ac54393e15c2405e9e8acbfb29d63`. Before every experiment, the organizer-run Python mirror checks all 15 fields, the C source hash, stream hash, polarity mask, and equality with the independent builder. The participant also ran the compiled wasm module below in Wasmtime, called `run()`, and read the info block and the code buffer: it reported the same 15 fields and wrote the byte stream with the SHA-256 above, which equals the stream of the independently verified patched netlist.

The participant compiled `GEN_C` with Ubuntu clang 18.1.3 and Ubuntu LLD 18.1.3 (`wasm-ld`):

```sh
clang --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

The stripped 25,014-byte module has SHA-256 `1d1a9449e6a73d6e31b2a5dbc82cf72501507b612d203ea749012a8614f76e4b`. `llvm-objdump -d` counts 10,332 static instructions. Participant measurement with Wasmtime 50.0.1 (Python bindings) and fuel enabled reports exactly 203,093,252 units of fuel consumed by exported function `run`, started with an ample budget; the least budget with which `run` completes, found by bisection, is 11 units lower (203,093,241), and the larger, consumed figure is charged. (The same 11-unit gap holds for the module of f330da42 and c31fe915, 194,442,296 consumed and 194,442,285 least; their text called the consumed figure the least budget, and their charge was conservative in the same way.) Charging two word operations per fuel unit plus one covers the measured and structural operators:

```text
2 * 203093252 + 1 = 406186505 operations.
```

The organizer does not compile or execute the wasm module. The compiler version, module hash, static instruction count, and fuel count are participant-run setup accounting. The organizer runs the Python mirror and checks the emitted bytes. The setup row is negligible: any bound below 2^100 operations would leave the claimed `time_log2` unchanged.

The emitter image has 10,332 instructions at 36 bytes, or 371,952 bytes. Its scratch is 123,999 bytes:

```text
use counts                                                   86,123
recent gates                                                    128
CSE keys and values                                           8,192
free and pending register maps                                  256
W array (64 words)                                            8,192
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
state subtotal (the preceding 16 rows)                       32,000
addition choices                                                100
IV, K, PW, PERM, UCD, and PT constants                        1,680
shadow stack                                                  4,096
total                                                       123,999
```

`experiments/bssha.py` computes the 32,000-byte state and 1,680-byte constant subtotals from named arrays and compares them with the C report. Complete setup memory is

```text
353220 program bytes + 16384 counters + 27776 registers
+ 371952 emitter image + 123999 scratch
= 893331 bytes.
```

Search memory is code 353,220 + counters 16,384 + registers 27,776 + table 649,728 = 1,047,108 bytes (the recovery array lies inside the plane copy, which is part of the counters; Appendix B.1). The count-only searches rebuild each candidate and do not retain DAGs. Their 10,000-instruction image is 360,000 bytes. With 123,999 bytes of builder scratch and 65,536 bytes of trial state, the offset and selector peaks are 549,583 and 549,635 bytes. All phases run sequentially. Search is the overall peak, 1,047,108 bytes (`<= 2^20` bytes).

### 3.7 Preprocessing

No work is free or nonuniform. Final emission plus fixed setup costs 407,000,105 operations. The offset search costs 461,900,436,782,186,496 operations and the selector audit costs 260,927,303,410,778,112. Total preprocessing is 722,827,740,599,964,713 operations, included in N. In target-compression units,

```text
log2(722827740599964713 / 4912) = 47.06433464256445.
```

The claim rounds this upward to `preprocessing_log2 = 47.06434`. There is no nonuniform advice.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bssha.py --loss` (the function `_lossq`); Appendix A recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
when both trails have length <= cr, pass 1 of step 6 records every D-th point of each walk and the terminal lengths l0, l1 <= cr, and pass 2 aligns the longer walk via its checkpoints and binary-searches the floor(min(l0, l1) / D) + 1 checkpoint intervals (at most 16 probes of < D steps) before stepping the two walks together for at most D steps to the first merge pair, found within cr + 17 D batches. The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F because F < 1701 < 2^11 and the low 11 key bits hold F. Equal keys of two DPs can differ only above bit 158. The lanes do not interact.
The stage-1 test loses no event. A 47-bit key match without a merge ends the run; its probability and one recovery are charged.

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B evaluations, N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(35 L), cr = ceil((62/5) L), S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 108523.1370, tmax = 110,329, and CMAX = 7. Let Pi_m = product from i = 0 to m - 1 of (1 - i/N'), PP = Q(Q - 1)/(2N'), and H = (Q(Q - 1)/2 + 2^18 Q)/N'. Let k = 110986 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 263, p = e^(-c/L), and p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)). Let F be uniformly random on 256-bit values and P_F the success probability when every evaluation of g is replaced by lazy sampling from F. Then
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_rec - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = 0.608429755879 (the no-useful-collision term shift * Pi_Q of Step 2, shift = 1/(1 - kQ/N')),
    P_delay = 0.001430524077,
    P_own = 9.157012e-06,
    P_long = 2.198166e-14,
    P_age = 1.127825e-14,
    P_rec = 2 PP e^(-(12.4 L - 1)/L) (1 + (12.4 L - 1) theta / (1 - theta)) = 5.484403e-05,
    P_dist = 4.549879e-06,
    P_cut = 1.825678e-05,
    P_key = C(tmax, 2) / (2^36 Tp) = 5.206685e-05,
    P_table = 8.445015e-07,
    P_tiny = P_start + P_DP-repeat + P_same-batch + P_60 + 2^-90,
    P_start = Q 2^18 / N = 7.679599e-34,
    P_DP-repeat = k^2 L / N' = 3.325161e-34,
    P_same-batch = 255 Q / N' = 7.470313e-37,
    P_60 = exp(-300 + (e^5 - 1) H) = 3.325641e-99.
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
(i) K_A. The disjoint-window scan from the credited proof bounds eight fresh cut trails by the upper tail of `Binomial(n2,p)` with `n2 = k + 263` and `p = exp(-c/L)`. Its value is `2.3307e-56`.
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
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; the bound is `Q L / N' = 9.157e-06`.
- X: the same-lane and different-lane geometric-tail calculation gives `E_X = 8.518780e-12`.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^18) / N': E_J2a2 <= (Q + 2^18) L Q (Q - 1) / (2 N'^2). E_J2a = 9.099758e-06.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2 = 1.127825e-14.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 3.132847e-16.
Combining the fresh tail with the same S, X, J2a, J2b, and Y root-event bounds gives `P_cut = 1.825678e-05`. There is no cut-count premise.

Step 7 (the early halts and residual events). The early halts are the eighth cut, table full, key false match, stage-1 budget, or recovery failure.

Table capacity and key matches. Outside `P_60`, fewer than 60 collisions occur. The number of finished trails is then at most `N1 + 59`, so filling `tmax` entries requires `N1 >= tmax - 59`. The Chernoff bound is `P_table = 8.445015e-07`. A false 47-bit key match costs `P_key = 5.206685e-05`, using key space `2^36 * 1701`.

Sixty collisions. At a fresh evaluation t, the collision probability is at most `(t - 1 + 2^18) / N'`. For `w = e^5`, multiplication of the conditional moment bounds gives

```text
E[w^C] <= exp((w - 1) H),
P(C >= 60) <= exp(-300 + (e^5 - 1) H)
             = P_60 = 3.325641e-99.
```

Stage-1 budget. Let `eta_t` mark that the low 20 bits of the independent uniform value `V_t` are zero, and let `mu2 = Q / 2^20 = 323502456702982421875000000000000`. Fresh stage-1 hits are at most `sum eta_t`, which is `Binomial(Q, 2^-20)`. The multiplicative Chernoff bound gives

```text
P(fresh hits > 1.5 mu2) <= exp(-0.108 mu2)
                            = exp(-34938265323922101562500000000000)
                            < exp(-1000).
```

Repeated-hit partition. Work on `N1 <= k - 1` outside E1 and E2, as in Steps 2 through 6. Outside `P_60`, fewer than 60 fresh collisions occur, so there are at most 60 maximal replay windows. A replay window starts after a trail joins a previously evaluated orbit and ends at its next DP, cut, or halt. Split these windows into non-simple and simple windows according to whether an input repeats before the terminal DP.

Non-simple replay lemma. A non-simple replay is contained in the root-event union `S union X union J2a union J2b union Y` already charged inside `P_cut`. To see this, choose the non-simple replay whose first joining collision t is earliest, and call its target e'. If e' is on the trail of t, event S holds. Otherwise use the target trail T' from Step 6 (ii). If `a(t) + sigma(e') >= c`, event X holds. If T' has a fresh collision between e' and `f'(e')`, event J2a holds. Assume neither event occurs. If T' evaluates the segment from e' through `f'(e')` freshly, T replays that distinct segment and reaches its DP before age c. That contradicts non-simplicity. The observed non-simple replay occurs before the run ends, so T' either is cut before `f'(e')` or has a nonfresh evaluation before e'. In the first case, an all-zero run of length c through e' gives J2b. If the trail was already nonfresh, take its first earlier joining collision. At age at least `c - 1`, that collision gives Y. Below age `c - 1`, if T' is cut before the downstream repeat, then T' is a nonfresh cut trail in `K_B`, and Step 6 (ii) gives S, X, J2a, J2b, or Y. If T' is not cut before the observed repeat, its replay follows the same DP-free suffix to that repeated input, so it is an earlier non-simple replay, contrary to the choice of t. This is the same exhaustive descent used in Step 6 (ii), with non-simplicity replacing the assumption that T is cut. A DP-free cycle is the direct special case: the collision that closes it is S when it closes on the same trail, and otherwise the descent gives X, J2a, J2b, or Y. The cycle cannot contain a DP because the first traversal would have ended there. Step 6 bounds the occurrence of each root event, not only the final cut halt, so this use adds no second charge.

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
         = 40272685735645806500328096338.6435494323731...
         > 1000.
```

Appendix A evaluates `A_replay` downward and charges the outward upper bound `P_replay-simple < exp(-1000)`. It also checks

```text
240 M = 26256355472294634526562508271553166480
      <= 339216912039786496000000000000000000000 = Q.
```

Outside the root-event union and the new `P_replay-simple` term, each of the 60 replay windows has at most `2 M / 2^20` hits. Thus the repeated hits are at most `120 M / 2^20 <= mu2 / 2`. Together with at most `1.5 mu2` fresh hits, this is at most `2 mu2`, below `e2max = 2 mu2 + 64`. The residual probability of the stage-1 budget halt is below `P_stage-fresh + P_replay-simple < 2 exp(-1000)`, in addition to `P_60` and the root-event union already charged in `P_cut`.

Recovery and the three small structural events. A recovery without a pair comes from a false key match, already charged by `P_key`, or from one of the fewer than `2^18` starts lying on an evaluated trail. The latter event is `P_start = Q 2^18 / N = 7.679599e-34`. Outside those events, Lemma 1 returns a pair within `cr + 17 D` calls (when both trails have length <= cr; longer colliding trails are charged in `P_rec`). A repeated DP-valued output costs `P_DP-repeat = k^2 L / N' = 3.325161e-34`. A partner in the same batch costs `P_same-batch = 255 Q / N' = 7.470313e-37`.

The outward-rounded certificate gives `P_start + P_DP-repeat + P_same-batch + P_60 < 1.101977e-33`. It adds `P_stage-fresh` and the new `P_replay-simple` term to `residual_actual`; each is below `exp(-1000)`. The total fits inside the charged `2^-90 = 8.077936e-28` reserve. The certificate uses outward rounding for every exponential and rational term, so it needs no probabilistic rounding allowance. This proves the lemma. QED.
Consequently the printed float bound is

```text
1 - 0.608429755879 - 0.001430524077 - 9.157012e-06
  - 2.198166e-14 - 1.127825e-14 - 5.484403e-05
  - 4.549879e-06 - 1.825678e-05 - 2^-40
  - 5.206685e-05 - 8.445015e-07 - P_tiny
= 0.3900000010000794.
```

Appendix A independently certifies `P_F >= 0.390000001000 >= 0.39` with exact rationals and outward-rounded decimals.

Sensitivity is recomputed from the live plan by replacing N with `N/(1-eps)` and reoptimizing Tp and B:

| hazard deficit eps | replacement Tp | extra time bits to restore 0.39 |
| ---: | ---: | ---: |
| 0.01 | 1696 | 0.00725061 |
| 0.05 | 1662 | 0.03700356 |
| 0.10 | 1617 | 0.07600856 |
| 0.25 | 1477 | 0.20753837 |

A collision-hazard surplus helps. No robustness margin is treated as a theorem.

## 5. Premise H1 and its evidence

H1 compares this fixed function with a uniformly random function. Its four clauses are:

- (a) Distinct fresh evaluated inputs have independent uniform outputs and pair-collision hazard `2^-256`.
- (b) Iterates from the starts `r+t` have the first-collision law of a random mapping.
- (c) A fresh output is a DP with probability `1701/2^122`, independently of collision events.
- (d) Under the adaptive program history and later DP flags, a fresh output hits any fixed earlier non-DP output with probability at least `2^-256`.

Lemma 2 proves the bound for the random function. H1 transfers that bound to the fixed target. The circuit, ledger, memory, and random-function theorem are exact claims.

Support of H1 (stated; it is not measured at width 256):

1. H1 is the generic premise of parallel collision search with distinguished points. Paul C. van Oorschot and Michael J. Wiener, "Parallel Collision Search with Cryptanalytic Applications", *Journal of Cryptology* 12(1):1-28, 1999, DOI 10.1007/PL00003816, model a fixed compression function iterated from fresh starts, without a chosen input difference, by a random function. The generic entries of this track use the same premise: mitchuski 3017c952, 1884db5b, and 4684dfc2; lamb356 3642e1cd; dariolina 6b678689; 0xplemonade's 7523902c, 7347a2b6, 60dbf898, 332b47e1, 5ed693e8, ff37a322, and c9ae3732; and mpjunior92's 1f18d544.
2. Clause (d) fails in the adverse direction only if `g`, along its own iterates, collides less often than a random function by a constant factor `1 - eps`. Such a property would separate this 64-step function from a random function in a way that no published result shows. This entry chooses no input difference and uses no differential property.
3. A deviation that raises the collision hazard helps. Section 4 prices a deficit exactly: 0.00725061 bit for `eps = 0.01`, 0.03700356 bit for `eps = 0.05`, 0.07600856 bit for `eps = 0.10`, and 0.20753837 bit for `eps = 0.25`.
4. The program checks agree with random-function reference values at their scopes. For `proj-k0-w256`, 256 independent uniform 16-bit projections contain a pair with probability 0.392678 per trial, or 100.53 of 256 trials. The expected number of equal pairs is `C(256,2)/2^16 = 0.498047` per trial, or 127.50 over 256 trials. For the exact seven-batch `plan(16)` (unchanged from the round-40 package), the credited lazy-random-function reference over 10,000,000 complete mappings gave probability 0.6958435 with standard error 0.00014548, or 178.14 successes per 256 trials. Two participant-run replays of both declared experiments used the organizer request format and organizer-style per-trial seeds derived from a substitute commitment (not the organizer's own seed material). The replay reported by 6ea56109 returned 187 checked width-16 search pairs in 256 trials for `bssha-n16` and 88 checked full-width projection pairs in 256 trials for `proj-k0-w256`. The replay of this package (other substitute seeds) returned 178 and 113; every returned pair of it was recomputed with `verifier/hash_functions.py:digest(..., "sha256", 64)` and with Python's `hashlib`, which agree, and satisfied the declared low-16-bit event, and its outputs are byte-identical to those of the 6ea56109 source on the same requests (Appendix B.4). All four counts are within about 1.6 standard deviations of the references (sd about 7.4 and 7.8 trials). The organizer's own counts are produced by its executor at evaluation time. In bssha-n16 the width-16 plan keeps the recovery cap c + S, so this experiment does not exercise the cr cap of the width-256 plan. These are consistency checks that can expose implementation-level deviations. No count is used to change the score.

Limitation: H1 cannot be measured at width 256, so these experiments do not measure the full-width collision hazard or the success probability at `2^128` scale.

## 6. Experiments

Two organizer consistency checks run `experiments/bssha.py`. Before dispatch, `bounded_check` runs the byte-exact mirror of the normative C emitter. The organizer recomputes the complete digest of every returned message pair.
`bssha-n16`: per trial, one attempt of the 256-lane search at width 16 (DP = low 2 bits zero, plan(16): 7 batches, cut rule, table, recovery) on the walk g16(x) = the low 16 bits of the complete digest of M(x), x < 2^16. Each batch runs the shipped program on the 256 planes (the 240 high input planes zero), then the experiment's digest network (`DigestNet`, bit-sliced, experiment code only, not in the ledger) inverts walk B, forms cv1 = IV + state and runs block 2; the recovery runs the rolled recovery program and the same inverse and block 2 in scalar form. The trials run side by side: the planes of trial i occupy bits 256 i to 256 i + 255 of each word, so one pass of the program and of the digest network serves every live trial, and each bitwise record acts on every trial's 256 bits alone. The trial returns M(x), M(y) when the attempt succeeded and two nulls otherwise. Checked event: the messages are distinct and their complete 64-step digests agree in the low 16 bits. This is exact, because at width 16 the walk is those 16 digest bits. The width-16 walk differs from the width-256 walk g only in the map after the program (inverse, block 2, low 16 bits); it runs the same program, search, table and recovery.
`proj-k0-w256`: per trial, 256 points at width 256 (source by trial index mod 3: uniform from the seed, counter r + i, iterates of g from 256 seed-derived starts) evaluated with the shipped program; their complete digests are formed by the digest network; the trial returns two points whose digests agree in the low 16 bits when the set holds such a pair. Checked event: as above. It checks at full width the program, the inverse of walk B, the chaining value, block 2 and the message construction.
The experiments check execution, witnesses, and agreement with the scope-matched reference values in Section 5. Their counts do not enter the cost or success bound. The changes of this package alter only constants of the width-256 plan (memory layout, table size, `Tp`); the width-16 attempt and the 256-point projection execute the same code paths, and on the 256-trial requests used for the local replay (Section 5, Appendix B.4) the outputs of this package are byte-identical to those of the 6ea56109 source.
The digest network is built with the same `Gen` class as the kernel. Its inverse of walk B contains a four-variable sum with the nonzero constant `1 + K_62`; the inherited four-word carry-fusion branch of `Gen._baseline` would have dropped that constant, so the branch is now guarded by `not cv` (taken only when the absorbed constant is zero). At round 40 no digest-network sum reached that branch with a nonzero constant. The guard does not change the kernel: all 39 kernel four-variable sums have zero constant, and the emitted stream hash is unchanged by it. The normative C emitter's `addm` contains the same branch (`nv == 4 && !bb`) without the guard; it is unaffected for the same reason, since the kernel has no four-variable sum with a nonzero constant (the C and Python streams are byte-identical). The self-test checks the digest network against scalar SHA-256 on 256 random full-width lanes.

## 7. Memory

Table: 432 groups * 47 words * 32 bytes = 649,728 bytes (110,592 slots). Slot t belongs to trail t: its `key + 1` is bit t mod 256 of the 47 words of group floor(t / 256); an all-zero slot is empty. The maximum key is 140,737,488,354,984, so `key + 1 < 2^47` and the sentinel transform fits.
Code: 85,805 body instructions * 4 bytes = 343,220 bytes. The 452 recovery records use 2,260 bytes. The other 1,548 fixed 5-byte instructions (41 stage-1, 3 loop, 1,250 handler, 94 recovery control, 160 setup) use 7,740 bytes. Total code is 353,220 bytes.
Counters and copies use 16,384 bytes, of which the first 8,192 are the plane copy; the 112-word (3,584-byte) recovery array lies inside that copy and adds no memory (Appendix B.1). The 868 registers use 27,776 bytes. No advice. Memory peak is `max(893331,1047108) = 1047108` bytes, at most `2^20` (1468 bytes of slack).
The table size is the largest that fits: `floor((2^20 - 353220 - 27776 - 16384) / 1504) * 256 - 263 = 432 * 256 - 263 = 110329`. Appendix A derives Tp = 1701 and certifies `P_F >= 0.39`.

## 8. Heuristics, conventions and what is credited

The premise is H1. The 868-register file and native formats are declared machine prices, not statistical premises. Lemma 2 proves the cut count. There is no advice.

Direct base of this entry: c31fe915-4f3a-4dd2-8247-54a554490279 (newjordan, round 64, `time_log2` 124.12385) supplies the complete package, including the weighted cascade stage-1 test of Section C and its accounting; this entry changes only what Section D lists. Its base f330da42-b03f-4ed5-90c1-de35c89fded1 (samsmith, round 64, 124.12387) supplies the 25 SAT-proved windows, the 21 window rewrites already applied and the patch mechanism that Section D extends. The lineage below is that of f330da42 and c31fe915.

Underlying program: 6ea56109-6ec6-4623-96c7-4c005c54463e (sraiw, commit 8065669, round 64, `time_log2` 124.12440) supplies the complete program `experiments/bssha.py` (kernel generator, normative C emitter, allocator, rolled recovery, search, table, plan, probability certificate and experiments) and the structure and wording of this proof; this package keeps all of it and changes only what Appendix B lists. Its own lineage is credited as in 6ea56109: 6f66a099-7772-441d-ab2c-67d94c620e13 (sraiw, commit 18b1400, round 64, 124.12599), 1f18d544-cd04-4177-8739-fad19d55a98a (mpjunior92, commit 840c9a1, round 64) and its parent 27984c2d-fc4b-4285-a430-c5f364c10a7e (sraiw, round 40) supplied the program and the proof that 6ea56109 carries. Through them, f7b1dea4-2883-45d6-9c0c-89a5d4ad1b1a supplies the recovery compaction, fb8a3bce-1839-4b9a-ab67-76670b4a05c9 the baseline package, b3f10279-3fa4-4d7b-9011-3faa2ae352c8 the fused kernel, schedule, allocator, and recovery design, and ff37a322-c5e7-4656-bb89-02f1a5d0e213 the native-4-byte machine and accounting base. What 6ea56109 itself introduced and this package inherits unchanged: bit-interleaved round and message-schedule emission with targeted allocator non-target fallback (`_MF`) (863 data registers with zero moves vs 905), site-76 addition-choice selector hint (85,830 instructions vs 85,831), preloaded `W0 + K0` and `W8 - K9` recovery initialization (2,670 executed recovery records per call vs 2,671), the re-measured wasm32 emitter, the re-derived two-pass checkpoint-recovery plan, ledger and certificate. New here: the recovery array inside the dead plane copy (Appendix B.1), 47-bit keys in a bit-sliced table (Section 3.3.1, Appendix B.2), the 1,250-record handler allowance (Appendix B.3), the two-stage stage-1 prefilter with a tight Chernoff-optimal passing-budget margin (Section 3.3.1a, Appendix B.6), and the re-derived 110,329-trail plan (`Tp = 1701`), ledger and certificate. The two-stage prefilter at the conservative `2x` margin was submitted as the direct predecessor of this package (round-64, `time_log2` 124.12423); this package tightens only item (4)'s guard margin to reach 124.12422. The two-stage distinguished-point prefilter and its passing-budget guard are the technique of the BLAKE3 round-7 entries a7f7020b-9374... (24/98 split) and e6b316ce (the guard charge) and the SHA3-256 entries on this challenge; this package ports the charging structure to SHA-256's stage-1 test and re-derives the ledger (no code of those entries is used). The earlier round-64 entry c9ae3732-bbe0-4b3f-8e14-4c685a7d0ec2 is cited for its score only. The checkpoint recovery resolution (Step 6, the recovery charge of Section 3.3, the loss term P_rec of Lemma 2 Step 4 (f), RECOVERY_CODE = 94, and the Appendix A checkpoint accounting) is ported from Jbenisek's round-55 entry 93618c27-3783-4744-904a-5d688ff610f8 and round-63 entry a74a20c8-3a52-4742-8970-e20dc0ad8b76 (and akki-rock05's round-64 entry 068ba228-dd60-437d-b36d-6773fec1a7be); this entry combines checkpoint recovery with the 863-data-register bit-interleaved schedule/allocator kernel (c83bda97-88bb-4125-b581-5b76c6c7de6a) and re-optimizes the age/recovery caps (KAPPA_256 = 35, KR = 62/5) and discrete Tp selection.


## Section C. The weighted cascade stage-1 test of c31fe915 (newjordan; derivative of f330da42-b03f-4ed5-90c1-de35c89fded1)

This section is newjordan's, unchanged; "this entry" and "the predecessor" in it mean c31fe915-4f3a-4dd2-8247-54a554490279 and f330da42. Its kernel figures (85,809 instructions, 85,823 operations per batch, the main-loop row and N) are those of c31fe915; with the kernel of Section D they become 85,805, 85,819, the main-loop row of Section 3.4 and the N of Section D. The cascade, its caps, U and the probability argument do not depend on the kernel and are unchanged.

### C1. What changes

The predecessor (f330da42-b03f-4ed5-90c1-de35c89fded1, samsmith, [64, 124.12387]) charges its stage-1 test in two stages (its Section 3.3.1a and Appendix B.6): a 12-plane prefilter of 14 operations in every batch, and 11 operations (the other 8 planes, the hit branch and a guard decrement) on the batches that pass the prefilter, charged as Bpass * 11 = 883198294137190057814291807564621008 with Bpass = m + isqrt(126 m) + 1, m = ceil(B P12). Charged per batch this is 14.6665 operations. A lane is a stage-1 hit when its 20 low bits are zero.

This entry replaces both stages, and the passing-budget row, with a cascade that computes the same mask. Let A_j be the OR of the stored planes 0..j-1 (the planes are upright: `Prog` sets the polarity vector `pin` to zero). A batch "passes j" (a level-j event) when A_j differs from the all-ones word, that is, when some lane has its j low bits all zero. For a batch with 256 fresh evaluations the probability of that event is P_j = 1 - (1 - 2^-j)^256. The native sequence is:

1. Unconditional: OR planes 0..9 (9 ORs), compare A_10 with the all-ones register, branch to the loop control when they are equal: **11 operations per batch** (the predecessor's prefilter: 14).
2. Level 10 (A_10 is not all ones): SUB w, w, 7; compare w < 0; branch to the halt (the guard check); OR planes 10 and 11; compare with all ones; branch to the loop control. Debit 7.
3. Levels 12, 14, 16: SUB w, w, 5; OR planes k and k + 1; compare with all ones; branch to the loop control. Debit 5 each.
4. Level 18: SUB w, w, 6; OR planes 18 and 19; compare with all ones; branch to the loop control; NOT. The result is the complement of A_20, the predecessor's hit mask, and it enters the unchanged hit handler. Debit 6.

Every debit covers the whole work of its level, including the subtract and, at level 10, the guard's compare and branch. An early exit is charged the full debit (the final NOT is charged even when the level exits before it). The OR count is 19 (9 + 2 + 2 + 2 + 2 + 2), the plain 20-plane test's. The function `stage1c` of `experiments/bssha.py` is the semantic program of this sequence at width 256: it returns 0 when some level finds all ones and the complement of A_20 otherwise, which is exactly the predecessor's `stage1` mask, and it debits the counter `cnt["g"]` by the weight of every level it enters and halts when the counter is negative after the level-10 debit. The reduced-width search of the experiments (n = 16) keeps the predecessor's test unchanged, so the experiments are byte-identical in behavior.

The two new registers are the counter w, a signed 256-bit register, and an all-ones constant used by the comparisons. Both are set once before the search (2 operations, 2 records).

### C2. The work bound (deterministic)

For each level k in 10, 12, 14, 16, 18 let

p_k = ceil((1 + 2^-20) B P_k + 120 M / 2^k) + 64,

with B = 1325066062655416000000000000000000000 and M = c + S = 109401481134560977194010451131471527 (the M of Lemma 2). The counter starts at

U = 7 p10 + 5 p12 + 5 p14 + 5 p16 + 6 p18 = 2701452811253085602513764546052482426.

The caps are: k = 10: P_k = 0.221294, debit 7, p_k = 306050387512050045483946974980980264, 120 M / 2^k / (B P_k) = 0.0437; k = 12: P_k = 0.060594, debit 5, p_k = 83496390856184683640187893417804157, 120 M / 2^k / (B P_k) = 0.0399; k = 14: P_k = 0.015504, debit 5, p_k = 21345167216052779850717118383947657, 120 M / 2^k / (B P_k) = 0.0390; k = 16: P_k = 0.003899, debit 5, p_k = 5366307363983626460728147947207700, 120 M / 2^k / (B P_k) = 0.0388; k = 18: P_k = 0.000976, debit 6, p_k = 1343461914604972394661653740137168, 120 M / 2^k / (B P_k) = 0.0387. The only check follows the level-10 debit. When a check passes (w >= 0 after the debit), the debits so far are at most U. The same batch can add at most 5 + 5 + 5 + 6 = 21 more, and the next level-10 debit (7) then halts the run. So the conditional stage-1 work is at most U + 28 on every run, whatever g returns, and with the two register sets the ledger row is **U + 30 = 2701452811253085602513764546052482456** (`pbud(p) + GOV` in the program, `stage-1 cascade` in Appendix A). The unconditional part, 11 operations, is in the batch body: 85,826 -> 85,823 operations per batch (85,809 kernel + 11 + 3 loop control).

In expectation the conditional work is sum of debit times P_k = 1.9549 operations per batch; the charged row is 2.0387 operations per batch, the difference being the cap margins (mostly the replay allowance 120 M / 2^k). Against the predecessor's charged 14.6665 operations per batch the charged stage-1 work falls by 1.6278 operations per batch.

### C3. Probability

The guard halts only when some level count exceeds its cap. If for every level k the number of level-k batches is at most p_k, then at every check w >= U - sum of debit times count >= 0, and the run is, batch for batch, the predecessor's run: the same hits, table, cuts, recovery and output. So the cascade adds to the failure probability only the probability that some level count exceeds its cap, and the argument of Step 7 ("Stage-1 budget") applies to each level k with k low bits in place of 20:

- Fresh level-k batches. A batch is a fresh level-k batch when one of its fresh evaluations returns a value with its k low bits zero. Given the history, a batch has at most 256 fresh evaluations, each uniform and independent of the history, so it is a fresh level-k batch with conditional probability at most P_k. Over the at most B batches of the run the count is dominated by Binomial(B, P_k), and the multiplicative Chernoff bound gives P(count > (1 + 2^-20) B P_k) <= exp(-2^-40 B P_k / 3). Appendix A checks 2^-40 B P_k / 3 > 1000 for every level.
- Repeated level-k batches. A level-k batch that is not fresh contains a repeated evaluation whose value has its k low bits zero. Outside the root-event union already charged in P_cut, every repeated evaluation lies in one of at most 60 simple replay windows (Step 7, non-simple replay lemma). By the simple replay lemma with k in place of 20, a fixed simple replay of at most M outputs holds more than 2 M / 2^k values with k low bits zero with probability at most exp(-0.386 M / 2^k). The union over 60 windows and all 2^256 targets is at most exp(-(0.386 M / 2^k - 256 ln 2 - ln 60)); Appendix A checks that this exponent exceeds 1000 for every level. Outside it the repeated level-k batches are at most 120 M / 2^k.

On the complement of these two events the count is at most (1 + 2^-20) B P_k + 120 M / 2^k <= p_k - 64. The ten tails (fresh and replay for five levels), each below exp(-1000), are union-bounded with no independence assumed and are added to `residual_actual` in Appendix A (`P_cascade`), inside the charged residual reserve (2^-89 in this package), which they do not exhaust. The predecessor's stage-1 hit budget e2max and its two tails are unchanged. The predecessor's passing-budget guard and its 2^-90 residual term are removed with the guard; the residual reserve stays at the predecessor's 2^-89.

The larger code and register file shrink the table (C4), and the plan of Appendix A is re-derived from the new tmax with the predecessor's procedure. Tp = 1701 (predecessor 1705); c, c_r, L and M follow Tp and are updated in place. P_table moves from 8.532533e-07 to 8.445015e-07 and P_key from 5.218603e-05 to 5.206685e-05; the program re-derives B to the least multiple of 10^21 at which the float bound reaches 0.390000001 again: B = 1325066062655416000000000000000000000 (predecessor 1325058821778652000000000000000000000). Appendix A's exact certificate, with outward rounding, gives **P_F >= 0.390000001000 >= 0.39**. The float bound of Lemma 2 moves from 0.3900000010000435 to 0.3900000010000794; every term of Lemma 2 that depends on Q is updated in place in Sections 2 to 4. The sensitivity table of Section 4 (the extra bits that restore 0.39 under a hazard deficit) and the reference values of Section 5 are the predecessor's and were not recomputed for the new tmax; they are supporting statements, not part of the claim.

H1 is the predecessor's premise, unchanged. The declared machine now has 868 registers.

### C4. Memory and code

The counter and the all-ones constant take two registers: the register file goes from 27712 to 27776 bytes (866 -> 868 registers). The stage-1 code has 41 fixed 5-byte records instead of the 22 that the predecessor's code row charges: 11 unconditional, 7 + 5 + 5 + 5 + 6 = 28 in the levels, and the 2 register sets, or 95 more bytes. Code goes from 353141 to 353236 bytes. The predecessor had 107 bytes to spare, so the bit-sliced table loses one group of 256 trail numbers and is again the largest that fits: tmax goes from 110585 to 110329 (110848 -> 110592 slots, 651232 -> 649728 bytes) and kchk = floor(table_bytes / 64) - 1 from 10174 to 10151. Search memory is 1047124 bytes (predecessor 1048469), at most 2^20, so the memory term is 0. The 64 KiB source budget: to make room for `stage1c`, `pcap` and `pbud`, the embedded `GEN_C` blob is recompressed (LZMA alone format, lc = 0, lp = 0, pb = 0, nice_len = 128); it decompresses to the identical C source, whose SHA-256 `bounded_check` still asserts, and the helper `stage1_ops` and the prefilter budget computation in `ledger` are removed (no longer used). `experiments/bssha.py` is 65525 bytes.

### C5. Ledger and claim

Rows changed against the predecessor (all exact, printed by `python3 bssha.py --ledger` and by Appendix A): the main loop (B * 85,823), the `stage-1 cascade` row U + 30 in place of the predecessor's `stage-1 pass` row, and the rows that follow Tp, B, tmax or kchk (slices, stage-1 hits, finished events, recovery). The setup, offset-search and selector-search rows are the predecessor's. The total is

N = 113830832770725139088596925128261669632805 word operations (predecessor 113832121107528140540498769188954351557806).

log2(N / 4912) = 124.123848430956 (predecessor 124.123864759279). The claim is its upward rounding at five decimals, **124.12385**, -0.00002 bit against the predecessor's 124.12387. Appendix A prints the integer certificate of the rounding.

### C6. Checks run for this entry

- `python3 -B bssha.py --ledger` and `--loss` print the plan, rows, N and Lemma 2 terms above.
- `python3 -B bssha.py --selftest`: True (bounded emitter and C-source hash, stream hash, builder equality, scalar and chained equivalence, recovery program, digest network and six width-16 search attempts).
- A separate check of `stage1c` against the predecessor's `stage1` on 30,000 random 256-lane plane sets with biased densities: identical masks; the debit of every call equals the native operation count of the levels it entered (minus the uncharged final NOT on an exit at level 18), and the counter halts exactly when it is negative after a level-10 debit.
- Appendix A, extended with the cascade caps, the per-level Chernoff and replay exponents and the `P_cascade` residual, run end to end: the output printed below.
- `scripts/pareto_candidate.py --family sha256 --rounds 64`: ready. The organizer's `run_intake` with the arm64 variant of the pinned python 3.12.12 image under the same sandbox policy: mechanically valid; both experiments give the same counts as the predecessor's package under the same seed.

## Section D. This entry: the four remaining window rewrites, by live-range renaming (derivative of c31fe915-4f3a-4dd2-8247-54a554490279)

### D1. What changes

The window search of item (5) found 25 pairwise disjoint windows of the 85,830-gate kernel whose local function has an exact SAT-proved replacement with one gate fewer. f330da42 applies 21 of them, and c31fe915 keeps that kernel. The other four windows (at records 1562 to 3581, 7897 to 7982, 20084 to 20163 and 76980 to 78744 of the allocated stream, each of 7 gates in two or three separate pieces) could not be realised with the registers of their own spans. In each, the shorter circuit uses a value at a point where no register still holds it (the allocator overwrote it after its last original use), or it computes an output early, into a register that still has to hold another value until the output's original position.

This entry realises all four by renaming live ranges. Renaming value X into register F:
- changes the destination field of X's producer to F, and
- changes every source field that reads X to F.

The reads of X are exactly the reads of the producer's old destination register from the producer up to and including the next record that writes that register (in a straight-line program, a record that reads and writes it reads first). A rename is used only where F is not written, and its current content is not read, from X's producer through the last use of X in the rewritten stream, and F is not live at the end. Renaming changes no operation and no value: every record computes the same function of the same values as before, and only the register that carries X changes.

Five renames are used: one before each of the windows at 1562, 20084 and 76980, and two before the window at 7897. Together they rewrite 20 records in place. After them, each of the four windows is realised exactly like the other 21: inside the replaced spans, every unchanged record reads its original values; between the pieces of a window, every record reads its original values; and after the window, every register that is read later holds its original value. These conditions were checked by a symbolic simulation of register contents (one label per value), and the result was checked functionally and formally (D5).

The kernel falls from 85,809 to 85,805 instructions: 67,482 XOR, 11,023 AND and 7,300 OR, still in 863 data registers with zero moves. The per-batch body falls from 85,823 to 85,819 operations (85,805 + 11 + 3).

### D2. Encoding and both emitters

`PT` grows from 737 to 943 hexadecimal characters. A group whose first hexadecimal digit h is at least 8 has h - 8 spans and carries renames: one digit m, then m entries of five digits (the original position of X's producer) and three digits (F). Both emitters, the C routine `patch` and the Python mirror `_patch`, apply a group's renames before they build the group's register list. For each rename they:
1. map the original position to the current one, exactly as for spans (adding the record deltas of the spans already applied before it);
2. set the producer's destination field to F;
3. walk forward, replacing source fields equal to the old destination with F, until a record writes the old destination (that record's sources included).

The C loop is bounded by the stream length. The 21 earlier groups are encoded as before.

The emitter numbers move as follows:
- **C source:** 29,762 bytes, SHA-256 `c89231ab59be22066b852d68196a338f22091c34d214ac9abc63e8f3acb499bd`.
- **Wasm module:** 25,014 bytes, SHA-256 `1d1a9449e6a73d6e31b2a5dbc82cf72501507b612d203ea749012a8614f76e4b`, built with the same toolchain and flags; 10,332 static instructions (`llvm-objdump -d`).
- **Fuel:** 203,093,252 units consumed by `run`, so the setup row is 813,600 + 2 * 203,093,252 + 1 = 407,000,105 operations. The least budget with which `run` completes is 11 units lower (Section 3.6).
- **Emitter tuple:** `EXPECTED_EMITTER_INFO = (85805, 863, 86087, 337942, 0, 0, 67482, 11023, 7300, 343320, 16384, 86123, 32000, 100, 1680)`. The constants grow by the 206 bytes of `PT`.
- **Stream:** SHA-256 `6ef09eeca51528903e6ef94498359c4d57b5526d847d684f32f693d59dcaa856`.
- **Setup memory:** 893,331 bytes (Section 3.6).

### D3. Plan, memory and ledger

**Memory and plan.** Code falls from 353,236 to 353,220 bytes and search memory from 1,047,124 to 1,047,108 bytes. The slack is 1,468 bytes, less than one 1,504-byte table group, so tmax = 110,329 and Tp = 1701 are unchanged. B = 1325066062655416000000000000000000000 and the success-probability certificate (`P_lower certified = 0.390000001000`) are also unchanged.

**Ledger.** Two rows move:
- the main loop, B * 85,819 = 113715844431025145704000000000000000000000;
- setup and generator, 407,000,105.

```text
N = 113825532506474517424596925128261686934717
log2(N / 4912) = 124.123781253700
certificate: 2^12412378 * 4912^100000 <= N^100000 < 2^12412379 * 4912^100000
```

The claim is 124.12379, 0.000067 bit below c31fe915's unrounded 124.123848431. preprocessing_log2 stays 47.06434.

### D4. Program size

The program is 65,464 bytes (limit 65,536), for two reasons:
- `GEN_C` is recompressed as an LZMA-alone stream (lc = lp = pb = 0, nice_len 64, BT2 match finder). It decompresses to the hash-checked C source.
- 33 further internal identifiers were renamed to two-character names. None of them appears in any other file of the package, in any string literal or as a keyword argument. `--ledger` prints identical output before and after the renames.

### D5. Checks run for this entry

- **Simulation:** the patched 85,805-record stream computes the same outputs as the original 85,830-record stream on the kernel's eight test vectors and on 20 random 256-lane inputs.
- **ABC `cec`** (`read_blif`, `strash`, `cec`) on the complete 85,830-instruction and 85,805-instruction netlists: "Networks are equivalent".
- **Emitter output:** the compiled wasm emitter, run in Wasmtime 50.0.1, writes the 85,805-record stream with the SHA-256 above. The Python mirror `_patch` produces the same stream from the ordinary builder's output (self-test).
- **Self-test and ledger:** `python3 -B bssha.py --selftest` prints True; `--ledger` prints the N above.
- **Appendix A:** the program, with `PH`, `INSTR_REC`, `WASM_RUN_OPERATORS` and the final assertion updated, prints the same N, the certificate and `P_lower certified = 0.390000001000`.
- **Experiments:** both declared experiments, replayed on the same request files, return byte-identical outputs from this program and from c31fe915's.
- **Recomputed tables:** the key-width table (Appendix B.2) and the handler-allowance sensitivity (Appendix B.3) were recomputed for this package (cascade and 85,805-instruction kernel). 47 bits remain the minimum.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate, and `certify` recomputes the bound of Lemma 2 in exact rationals and 60-digit decimals with outward rounding: the line `P_lower certified` is a proved lower bound on P_F, asserted >= 0.39. The same numbers come from `python3 bssha.py --ledger`.

```python
from fractions import Fraction
CK = 1
KR = Fraction(62, 5)
REC1 = REC2 = 39
CHK, PROBE, RECFIX = 80, 100, 600
from math import log, exp, log2, log1p, comb, expm1, isqrt

PH, PREFILT, FILT, LOOP, LANES = 85805, 11, 41, 3, 256   # PREFILT: unconditional stage-1 operations; FILT: stage-1 cascade records (Section C)
CASC = ((10, 12, 7), (12, 14, 5), (14, 16, 5), (16, 18, 5), (18, 20, 6))   # cascade groups (first plane, end plane, debit), Section C
GOV = 30                                       # overshoot 28 + the two register sets
PREFILTER_PLANES, STAGE1_GUARD_TAIL, STAGE1_PASS_MULT = 12, 3, 2
REST = FILT - PREFILT + STAGE1_GUARD_TAIL
INSTR_REC = 85805
PH7, EXTRA, RECINIT = 2670, 39, 125
N_BITS, S1, W, KAPPA = 256, 20, 102, 35         # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE = 2800, 3800, 4200, 1300
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 7
CUT_HALT_ORDER = CMAX + 1
assert CUT_HALT_ORDER == 8
WASM_RUN_OPERATORS, WASM_OPERATOR_FACTOR = 203093252, 2
BODYB, CTRLB, RECB, REC_RECORDS = 4, 5, 5, 452
CONTROL, REGFILE, COUNTERS, ADVICE, ARRAYS = 1457 + 47 * CK, 27776, 16384, 0, 0   # ARRAYS = 0: the 3,584-byte recovery array lies inside the dead 8,192-byte plane copy; handler allowance 1,250 records
KEYB = 47                                      # key+1; zero is the unwritten sentinel
GROUP, GROUPB = 256, KEYB * 32                  # bit-sliced table: 256 trail numbers per group of KEYB 32-byte words
SEARCH_EVAL_OPS = 1 << 48
OFFSET_SEARCH = 1641 * SEARCH_EVAL_OPS            # 64 endpoint + 1 initial + 3 * 192 coordinate + 1000 perturbation builds
SELECTOR_SEARCH = 927 * SEARCH_EVAL_OPS
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


lo, hi = 1.0, float(tmax - 59)                                 # the largest mean number of trails the table holds (tail within 2^-19.5)
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
assert N == 113825532506474517424596925128261686934717
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
Tp = 1701  tmax = 110329  B = 1325066062655416000000000000000000000  e2max = 647004913405964843750000000000064  c = 109401481134560977193728976154760871
memory bytes = 1047108
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000001000
residual P_start          7.67959873385723922966418813499409642743134862376844251949031E-34
residual P_DP-repeat      3.32516090958350360938335620678781970733019579269428355364904E-34
residual P_same-batch     7.47031279424131776262042226571462713431764899538875082873350E-37
residual P_60             3.32564093239457115954793150115583845624843384806723431004014E-99
residual fresh exponent   34938265323922101562500000000000
residual replay exponent  40272685735645806500328096338.6435494323731842840456080936417
residual P_stage-fresh    5.07595889754945676529180947957433691930610687878259230750892E-435
residual P_replay-simple  5.07595889754945676529180947957433691930610687878259230750892E-435
residual P_cascade        5.07595889754945676529180947957433691930610687878259230750892E-434
residual residual actual  1.10122299562349841568101647640476307618958620654581148239681E-33
residual 2^-90 reserve    1.61558713389263217748322010169914619837072677910327911376953E-27
residual reserve slack    1.61558603266963655398480442068266979360765058951707256795805E-27
residual P_tiny charged   1.61558823511562780098163578271562260313380296868948565958101E-27
main loop: B * 85819                                 113715844431025145704000000000000000000000
stage-1 cascade: U + 30                              2701452811253085602513764546052482456
slice checks: ceil(B / 2^48) * 1300                  6119854423943283450172200
stage-1 hits: e2max * 2800                           1811613757536701562500000000000179200
finished events: (tmax + 1) * (3800 + 6 * (tmax + 263)) 73628946160
cut trails: 7 * 4200                                 29400
recovery                                             105175008880575813576764592617955160588
setup and generator                                  407000105
charged offset search                                461900436782186496
charged selector search                              260927303410778112
N = 113825532506474517424596925128261686934717
certificate: 2^12412378 * 4912^100000 <= N^100000 < 2^12412379 * 4912^100000
log2(N/C) = 124.1237812537
time_log2 = 124.12379
```

## Appendix B. Changes relative to 6ea56109

*Appendix B is the predecessor's account of its changes relative to 6ea56109, with the predecessor's numbers; Section C gives this entry's change and numbers.*

6ea56109 is the package this one derives from (Section 8). Its proof and program are kept; the following table lists every quantity of the plan that moved, and B.1 to B.5 justify the changes, state what is declared rather than derived, and list the checks that were run.

| quantity | 6ea56109 | this package |
| --- | --- | --- |
| recovery array | 3,584 bytes, separate | 0 bytes (first 3,584 bytes of the 8,192-byte plane copy) |
| key bits (kb + 11) | 48 (kb = 37) | 47 (kb = 36) |
| table | 6-byte slots, 108,153 slots | 432 groups of 47 words, 110,592 slots |
| table bytes | 648,918 | 649,728 |
| handler-code allowance (records) | 1,000 | 1,250 (needed: at most 133) |
| kernel instructions | 85,830 | 85,805 |
| code bytes | 351,975 | 353,220 |
| tmax (stored trails) | 107,890 | 110,329 |
| Tp | 1663 | 1701 |
| P_key (false key match) | 2.546398e-05 | 5.206685e-05 |
| stage-1 charge | full 20-plane test every batch | weighted cascade (Section C; f330da42: 12-plane prefilter + guarded pass, B.6) |
| per-batch body (operations) | 85,855 | 85,819 |
| stage-1 conditional row (operations) | none | U + 30 = 2701452811253085602513764546052482456 |
| B (batches) | 1325080891611792000000000000000000000 | 1325066062655416000000000000000000000 |
| cr (recovery cap) | 39645044251913305650047402399221342 | 38759381887673031920063980123400995 |
| kchk (checkpoints) | 10138 | 10151 |
| N (word operations) | 113874210100292317988431669910942899661174 | 113825532506474517424596925128261686934717 |
| log2(N / 4912) | 124.124398091677 | 124.123781254 |
| claimed time_log2 | 124.12440 | 124.12379 |
| search memory (bytes) | 1,048,573 | 1,047,108 |
| setup memory (bytes) | 863,450 | 893,331 |

The program differs from 6ea56109 in exactly these places: the handler allowance (`HANDLER_CODE` 1000 to 1250); `ARRAYS` 3584 to 0, with `PLANE_COPY = LANES * 32`, `ARRAY_BYTES = (2 * ROUNDS - 16) * 32` and an assertion `ARRAY_BYTES <= PLANE_COPY <= COUNTERS`; `KEYB` 48 to 47; `SLOTB` replaced by `GROUP = 256` and `GROUP_BYTES = KEYB * 32`; the table size `table_bytes(t) = ceil((t + LANES + CMAX) / GROUP) * GROUP_BYTES`; the largest `tmax` that fits, `(MEM_LIMIT - code - REGFILE - COUNTERS - ADVICE - ARRAYS) // GROUP_BYTES * GROUP - LANES - CMAX`; and the matching assertion of `boundary_test`. For the prefilter (item 4, Appendix B.6): the constants `PFP = 12` (prefilter planes), `GC = 0` (guard records, absorbed into the 1,250 handler allowance), `GT = 3` (guard-tail operations) and `PM = 2` (passing-budget margin); in `machine_constants` the body charges `stage1_ops(pr.pin, PFP)` (the prefilter) while the code still charges `stage1_ops(pr.pin, STAGE1_PLANES)` (the full test); and `ledger` gains one `stage1_pass` part, `Bpass * (stage1_ops(STAGE1_PLANES) - stage1_ops(PFP) + GT)` with `Bpass = PM * ceil(B * P12) + 64`. The emitter source `GEN_C`, its hashes and `EXPECTED_EMITTER_INFO` change only as described at the end of this paragraph (item (5)); `STAGE1_PLANES`, `CFG`, `stage1` and the search are untouched. The program of Appendix A differs from that of 6ea56109 by the same constants (its `CONTROL`, `ARRAYS`, `KEYB`, `GROUP`, `GROUPB`, `tmax` and `table_bytes` lines, the `PREFILT`/`REST`/`Bpass` additions, the `stage-1 pass` row, and the final assertion on N). Item (5) adds: in `GEN_C`, the table `PT`, the helper `hx` and the routine `patch` (called once, after the second `trace()`; it rewrites the spans of each window in reverse order, shifts the tail of the buffer up by the number of records saved, and recounts the opcodes), and `sizeof PT` in the constants report; in the program, the function `_patch`, its call in `BoundedEmitter.run` and in the self-test's comparison with the independent builder (which now compares the independent builder's stream after `_patch`); `EXPECTED_EMITTER_INFO`, the stream, C and wasm hashes, `WASM_RUN_OPERATORS` and `WASM_EMITTER_INSTR` (values of this package: Section D). To keep the program of f330da42 under the 65,536-byte limit (65,315 bytes; this package: 65,464 bytes, Section D) `GEN_C` is stored as an LZMA-alone stream instead of an `.xz` stream, and 57 internal identifiers that appear in no other file were renamed to shorter names; no other line changed.

### B.1 The recovery array inside the plane copy

What is in the plane copy and when. The stage-1 hit stores the 256 planes to the 8 KiB copy (256 stores, Section 3.3). The finished-trail routine reloads the planes from it at its end. Between two hits the copy holds stale data that nothing reads before the next hit rewrites it.

When step 6 starts. Step 6 is entered only from step 3, inside the finished-trail routine, after the scan has found `key + 1` in the table. At that moment the routine holds t0 (from the scan), t1 = t (from the lane arrays) and r, and step 6 needs nothing else: the trails are s_t = r + t. Step 6 ends the attempt: it returns a pair or halts (Section 2, step 5), and no path returns to the search, so the planes are never reloaded after it starts. The plane copy is therefore dead from the first operation of step 6 on. 6ea56109 uses the same fact for the table: its pass 1 writes `kchk` = floor(table_bytes / 64) - 1 checkpoints of 64 bytes into the table (Section 2, step 6), which is dead from the same moment.

Where the array is and what it needs. The recovery program's 112 array words (64 schedule words and the 48 constants K10..K57) occupy the first 3,584 bytes of the plane copy, which has 8,192 bytes (inside the 16,384 counter bytes that the ledger already counts), so the ledger takes `ARRAYS = 0`. The 125 one-time initialization records, charged in the fixed operations of the recovery, run after the planes are dead. They write 55 of the 112 words (the 48 round constants and the 7 constant schedule words). Every array word that a call reads is one of these 55 or was written earlier in the same call, and no call changes the 55. Registers: a call reads 18 registers besides its 8 input registers before writing them; 14 are set by the initialization, and the other 4 (registers 3, 4, 7, 8) are zero-valued. Ten of these registers are overwritten by a call and are re-set before each call (4 zero-valued: 3, 4, 7, 8; 6 holding their initialization values: 5, 6, 10, 11, 12, 30). These are the 10 re-sets already charged inside the 39 surrounding operations of each recovery batch (Section 3.3), so nothing is added to the recovery charge.

Test. A script outside the package ran the 125 initialization records and then six consecutive calls with the 10 re-sets before each call, for ten recoveries, with the array words and all 32 registers set before the initialization to zeros, to random values, or to `None` so that any read of an unwritten word or register would raise an error (five combinations). In every combination all 60 calls of the ten recoveries returned g exactly as the scalar reference does. With the re-sets skipped the same test fails, so it can detect such a dependence.

What is not claimed. The registers of the declared machine are not addressable memory, so nothing is overlaid on them; only the RAM-to-RAM overlay above is used.

### B.2 The table

Why a bit-sliced layout. The saving of narrower keys is realized only if slots are packed without padding. Contiguous 47-bit slots would need access at bit offsets: unaligned loads, or 256 code copies, one per alignment class, because gcd(47, 256) = 1; such a plan, at declared prices of 100 more handler records and twelve operations per slot, is worth about 0.000006 bit more (claim 124.12434, evaluated on the kernel of 6ea56109) but rests on an addressing mechanism the declared machine does not itemize. The bit-sliced table uses 47 bits per slot exactly, aligned accesses and immediate shifts only; its cost is rounding the table to whole groups of 1,504 bytes (here 1,468 bytes of slack remain).

Why 47 bits. P_key, the probability of a false key match, grows by a factor 2 per bit removed, while a bit saved buys 2.1 percent more slots. The exact plan (Section 4, Appendix A) for each key width, with the kernel of 85,805 instructions, the handler allowance of 1,250 records and the stage-1 cascade of Section C (recomputed for this package):

| key bits | Tp | tmax | groups | P_key | time_log2 (unrounded) | claim |
| --- | --- | --- | --- | --- | --- | --- |
| 45 | 1780 | 115,449 | 452 | 2.1792e-04 | 124.123962183 | 124.12397 |
| 46 | 1741 | 112,889 | 442 | 1.0652e-04 | 124.123800898 | 124.12381 |
| **47** | **1701** | **110,329** | **432** | **5.2067e-05** | **124.123781254** | **124.12379** |
| 48 | 1665 | 108,025 | 423 | 2.5497e-05 | 124.123821836 | 124.12383 |
| 49 | 1633 | 105,977 | 415 | 1.2510e-05 | 124.123887193 | 124.12389 |

Every row is a plan by the same program with only `KEYB` changed, and each is certified by the same bound; 47 is the minimum. P_key (5.2067e-05) is charged in the success probability of Lemma 2 and in the certificate of Appendix A.

### B.3 What is declared rather than derived, and sensitivity

1. Handler-code allowance. As in 6ea56109, the handler is not listed record by record; its size is a declared allowance of 5-byte records. This package declares 1,250, of which the new table routines need at most 133 (Section 3.3.1) and the inherited routines need what 6ea56109 declares for them. Sensitivity (everything else fixed, recomputed for this package): any allowance up to 1,543 gives the same plan (1,468 bytes of slack are 293 records), 1,544 to 1,844 gives 431 groups (claim 124.12380), and 1,845 to 2,000 gives 430 groups (claim 124.12381). The claim stays below 124.12385 for every allowance up to 2,000 records.
2. Scan price. The ledger keeps the six operations per slot of 6ea56109; the routine of Section 3.3.1 needs 1.68 (185,952 / 110,848, write included). The routine's work would have to be 6 * 110,848 / 185,952 = 3.57 times larger than counted before it exceeded the charge, and the events are 7.4e10 of 1.14e41 operations, so even a tenfold error would move the claim by less than 1e-29 bit.
3. Lifetime argument (B.1). It rests on the control flow of Section 2 (step 6 is final) and on the recovery program's start-state test above.
4. Everything 6ea56109 declares is unchanged and not re-derived here: the 2,800, 3,800, 1,300 and 4,200 operation charges, the 1,000-record handler allowance included in the 1,250, the 39 surrounding operations, the 866-register file, and the premise H1 with its sensitivity (Section 5).

### B.4 Checks that were run

All local, in an isolated sandbox without network, on the final source: `python3 experiments/bssha.py --selftest` exits 0 (including the assertions that every key is below 2^47 and every trail number below 2^18); the program of Appendix A prints the N and certificate above (`P_lower certified = 0.390000001000`); the two declared experiments, run on 256-trial requests, return byte-identical outputs to those of the 6ea56109 source (178 of 256 trials of `bssha-n16` and 113 of 256 trials of `proj-k0-w256` return a pair) and every returned pair was recomputed with `verifier/hash_functions.py:digest(..., "sha256", 64)` and with Python's `hashlib` (the two agree) and agrees in digest bytes 30 and 31. A model of the routines of Section 3.3.1 on 256-bit integers (not part of the package) confirmed the one-hot construction for all 256 indices, 3,000 random inserts into distinct slots with no false match before any insert, every stored key found at its own slot, no match for keys that differ in one bit, and the operation counts above. For item (5): the SAT-proved window replacements were applied to the netlist of the previous version of this program and checked on the kernel's eight test vectors and on 20 random 256-lane inputs; ABC (`cec`) reported the complete 85,830-instruction and 85,809-instruction netlists equivalent (and, for Section D, the 85,830-instruction and 85,805-instruction netlists); the compiled wasm emitter, run in Wasmtime, emits the verified stream byte for byte (85,809 instructions in f330da42, 85,805 here); and the two declared experiments, replayed on 48-trial requests with a new seed on the previous version of this program and on this one, return byte-identical outputs (30 of 48 trials of `bssha-n16` and 18 of 48 of `proj-k0-w256` return a pair). The 256-trial counts above were obtained before item (5); the kernel computes the same function, so they are unchanged.

### B.5 Corrections of inherited text

Statements of the 6ea56109 package that disagree with its own numbers are not carried over: its claim lists 76 itemized surrounding operations per recovery call while its proof itemizes 39 (39 is used throughout; the ledger always charged 39); its introduction compared 124.12440 with 124.12602 as a difference of 0.00004 bit (the difference is 0.0016 bit); its credit paragraph named a 107,929-trail plan (that was the earlier entry's plan; 6ea56109 used 107,890); and Lemma 2 printed 1.094221e-33 for the sum of four small terms whose exact sum is 1.093973e-33 for 6ea56109 (the sum of this package's terms is printed from the Appendix A residuals).

### B.6 The two-stage distinguished-point prefilter

What it is and why it is exact (Section 3.3.1a). The stage-1 test, which asks whether any of the 256 lanes reached a distinguished point (low 20 bits zero), is charged in two stages: a 12-plane prefilter (14 operations) to every batch, and the remaining 8 planes plus a passing-budget-guard decrement (11 operations) only to the `P12 = 0.0606` fraction of batches that pass the prefilter. A lane with all 20 low bits zero has its low 12 zero, so the prefilter is exact; the predicate, the search, the collisions found, the table and the plan are identical to items (1) to (3). Only the ledger's cost rows move: the per-batch body falls from 85,855 to 85,847, and one `stage-1 pass` row of `Bpass * 11` is added, with `Bpass = m + isqrt(126 m) + 1` and `m = ceil(B * P12)` the mean passing count.

Why it is a valid charge. The passing count is `Binomial(B, P12)`, and the guard halts if it exceeds `Bpass = m + t` with `t = isqrt(126 m) + 1 ~ sqrt(126 m)`. By the Chernoff bound `P(Binomial(B, P12) >= m + t) <= exp(-t^2 / (2 m + 2 t / 3))`, and since `t << m` so `t^2 / (2 m) = 63`, the halt probability is at most `exp(-63) < 2^-90`. This is the same guard device 6ea56109 uses for the stage-1 hit count `e2max`, but charged at the tight Chernoff-optimal margin rather than the `2x` the predecessor and `e2max` use. The halt is charged explicitly: the residual of Lemma 2 gains a `2^-90` term and the residual reserve is raised from `2^-90` to `2^-89` to cover it (Appendix A `residual_reserve`; the `assert residual_actual < residual_reserve` still holds, with `residual_actual = 8.08e-28 < 2^-89 = 1.62e-27`). The certified `P_lower` is unchanged at `0.390000001000`. The guard's down-counter is at most ten handler records inside the declared 1,250-record allowance (Appendix B.3), so `tmax`, `Tp`, `B` and the table geometry are byte-for-byte those of items (1) to (3) (the memory peak is 1,048,469 bytes after item (5)); the Appendix A output confirms every row other than `main loop` and `stage-1 pass` is unchanged from the predecessor, and `stage-1 pass` itself is halved.

Effect and sensitivity. Item (4) in full lowers the claim (evaluated on the 85,830-instruction kernel of 6ea56109, before item (5)) from 124.12435 to 124.12422 (unrounded 124.124340502870 to 124.124217383, a reduction of 0.000123 bit): the two-stage prefilter accounts for 124.12423 (unrounded 124.124228573, reduction 0.000112 bit), and tightening the passing-budget margin from `2x` to the Chernoff-optimal `m + sqrt(126 m)` accounts for the last step to 124.12422 (a further 0.0000112 bit, from halving the `stage-1 pass` charge). The prefilter width is one free parameter; 12 planes is near the optimum (11 or 13 planes give the same claim, within 2e-5 bit). Widening the distinguished-point low-bit count from `s1 = 20` to `s1 = 24` alongside the prefilter would recover a further ~1e-5 bit; it changes the DP split and `e2max`, so it is left for a later entry to keep this one a minimal change.

Precedent. The two-stage prefilter and the passing-budget guard are the technique of the BLAKE3 round-7 entries a7f7020b (the 24/98 distinguished-point split) and e6b316ce (the guard charged per passing batch) and the SHA3-256 entries on this challenge, all accepted as plausible_not_refuted. This package ports only the charging structure to SHA-256's stage-1 test; no code of those entries is used.
