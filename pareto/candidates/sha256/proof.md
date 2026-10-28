# sha256-r64: an 85,830-instruction native bit-sliced birthday walk

This package improves on the round-64 entry 1f18d544-cd04-4177-8739-fad19d55a98a (mpjunior92, commit 840c9a1, `time_log2` 124.12602), which ported the round-40 package 27984c2d-fc4b-4285-a430-c5f364c10a7e (lineage f7b1dea4, fb8a3bce, b3f10279, ff37a322) to the full 64-step target (improving on c9ae3732-bbe0-4b3f-8e14-4c685a7d0ec2, `time_log2` 124.13635, 86,375 instructions). At 64 steps our kernel has 67,507 XOR, 11,021 AND, and 7,302 OR native instructions, or 85,830 total (one fewer than 1f18d544 and 545 fewer than c9ae3732), and allocates in 863 data registers with zero moves (42 fewer registers than 1f18d544). The implementation keeps both generators: the bounded Python generator and the freestanding C emitter build the same network, and the self-test requires byte equality, scalar equivalence, chained-walk equivalence, zero moves, recovery equivalence, and complete two-block digest agreement.

What changed relative to 1f18d544 (and its parent 27984c2d) is: (1) bit-interleaved round and message-schedule emission with targeted allocator non-target fallback (`_MF`), which lowers peak register pressure by 42 registers so the streaming allocator achieves zero moves in `REGISTERS = 863` data registers (866 total registers, `REGFILE = 27,712` bytes vs 29,056 bytes), freeing 1,344 bytes for 224 additional 48-bit table slots (`tmax = 107,929` vs 107,705, `Tp = 1664` vs 1660); (2) addition-choice selector `1` at `addm` site 76 (`W[53]`), which saves 1 gate (`85,830` vs `85,831` instructions, `343,320` vs `343,324` code bytes) within the already-charged 927-build selector validation envelope; and (3) preloading `W0 + K0` and `W8 - K9` as one-time initialization records in `RecProg` (125 init records and 327 per-call loop records, still 452 total records, executing `2,670` records per call instead of `2,671`). As in 1f18d544, `ROUNDS = 64`, `UNIT = C = 4912`, `QM = 0x0772d77a`, `XM = 0xa2c126f1`, and `Gen._baseline` guards the four-word carry-fusion branch by `not cv` (Section 6).

The native body instruction remains exactly 32 bits: a 2-bit opcode and three 10-bit register fields. The machine executes it directly for one word operation. No decoder or interpreter runs in the priced path. The body occupies 343,320 bytes. Control and recovery use native fixed 5-byte instructions.

The six-offset search evaluates 1,641 complete builds. The ledger reserves one baseline and two passes over all 463 alternatives in the 100-site reduction inventory, or 927 complete builds. Every build is charged at `2^48` operations. The emitted selector sets site 76 to 1 (covered by pass 1 of the charged 927-build selector audit) and all other 99 sites to 0. The final plan uses 107,929 completed trails in 108,192 48-bit sentinel slots. Search memory is 1,048,572 bytes (`<= 1,048,576`).

The exact ledger is

```
N = 113998998025037447331371507131763478591406 word operations
log2(N / 4912) = 124.125978189133
```

The claim rounds upward to `time_log2 = 124.12598`, which is 0.00004 bit below 1f18d544's claimed 124.12602 (0.000032 bit between the unrounded values) and 0.01037 bit below c9ae3732's 124.13635. Setup memory is 863,215 bytes. H1, the fixed-function random-function comparison stated in Sections 4 and 5, is the only score-critical premise. Circuit changes, counts, and memory bounds are exact checked claims, not premises.

## 1. Target and relation

Target `sha256-r64-prefix-v1` (the Pareto lane `sha256`, round 64, the full SHA-256 step count). The two colliding messages have 64 bytes each. With x a 256-bit integer and y0..y7 its eight 32-bit words (big-endian, y0 the highest), M(x) is the 16 big-endian words W0..W15 with
- W0..W7 = the constant words 3e73281c, 752d8ed2, ad19eff1, 7250fceb, d4095422, 44fdb519, 43f22c5b, d8d6aac4 (computed from the standard IV by `_anchor_prefix` so that the eight new a-words of steps 0..7 are K9 - K8, -K9, 0, 0, 0, 0, 0, 0; the working state after step 7 is therefore (a,b,c,d,e,f,g,h) = (0, 0, 0, 0, 0, 0, -K9, K9 - K8), which makes steps 8 and 9 cheap),
- W8 = y0, W9 = y1, and W(8+k) = y_k - K(8+k) modulo 2^32 for k = 2..7.
FIPS 180-4 padding appends 0x80, 55 zero bytes and the 64-bit length 512: the padded message is 128 bytes, two blocks, and block 2 is the same for every x. The target runs the steps 0 to 63 on each block, block 1 from the standard IV and block 2 from the chaining value cv1 = IV + s(x) word by word, where s(x) is the working state after step 63 of block 1; the digest is the result of block 2 with its feed-forward (`verifier/hash_functions.py:digest(M(x), "sha256", 64)`). The profile's message domain is "finite byte strings of bit length below 2^64"; a 64-byte string is in it.
Write a_i, e_i for the a and e words after i steps of block 1 (a_0, e_0 from the IV), T1_i for the T1 of the step that produces them and W_j for the schedule word of step j. With the fixed 32-bit polarity masks `QM = 0x0772d77a` and `XM = 0xa2c126f1`, f(x) is walk B (4684dfc2) with per-bit polarity-matched disjoint-support shears on Q and X. Define the eight words bw = [e_61, e_62, a_57, a_58, Q, T1_60, X, Y] with X = e_59 + Ch(e_62, XM, e_60) + W_62 (at bit j: `e_62[j] | e_60[j]` when `(XM >> j) & 1 == 1` and `~e_62[j] & e_60[j]` when `(XM >> j) & 1 == 0`; since `Ch(e2, e3, e4) = Ch(e2, XM, e4) + (e2 & e3 & ~XM) - (e2 & ~e3 & XM) mod 2^32`, the inverse adds `(e2 & e3 & ~XM) - (e2 & ~e3 & XM)`), Q = T1_59 + Ch(a_58 ^ a_57, a_56, QM) (at bit j: `~(a_58[j] ^ a_57[j]) | a_56[j]` when `(QM >> j) & 1 == 1` and `(a_58[j] ^ a_57[j]) & a_56[j]` when `(QM >> j) & 1 == 0`; since `Maj(a6, a7, a8) = Ch(a6 ^ a7, a8, QM) + (a6 & a7 & ~QM) - (~a6 & ~a7 & QM) mod 2^32`, the inverse adds `(a6 & a7 & ~QM) - (~a6 & ~a7 & QM)`), and Y = e_60 + W_63. Then f(x) is the 256-bit integer whose eight 32-bit words, most significant first, are bw[6], bw[1], bw[7], bw[0], bw[5], bw[4], bw[2], bw[3] = X, e_62, Y, e_61, T1_60, Q, a_57, a_58 (the permutation PERM = (6, 1, 7, 0, 5, 4, 2, 3), the order with no register move, Section 3.2; `enc_words`, `words_of` and `int_of` in the program). In particular the low 32 bits of f(x), which hold the distinguished-point test bits of Section 2, are a_58, and the next word up is a_57. In the program these are bw = [E[r-3], E[r-2], A[r-7], A[r-6], ..., T[r-4], ...] with r = 64. These words determine s(x): the program's `enc_invert` recovers a_59 = Q + (a_58 & a_57 & ~QM) - (~a_58 & ~a_57 & QM) + Sigma0(a_58), then a_60, a_61, a_62, the T1 of steps 62 (= X + (e_62 & e_61 & ~XM) - (e_62 & ~e_61 & XM) + Sigma1(e_62) + K_62) and 63 and the whole state, by additions, subtractions and the round functions. The walk is g(x) = f(x) XOR q, q the fixed 256-bit mask `22273a6c5e8abef676dc5de11e7bc9e3468ac54393e15c2405e9e8acbfb29d63` (134 output planes that the generator leaves complemented instead of spending a NOT).
So g(x) = g(y) gives s(x) = s(y), hence the same cv1, the same block 2 and equal digests. x != y gives M(x) != M(y), since x -> W8..W15 is a bijection. The attack outputs two distinct 64-byte messages with equal complete 256-bit digests.
The selftest (`python3 bssha.py --selftest`) compares the program with scalar g on 2,560 lanes, including all-zero and all-one inputs, checks four chained steps, checks the inverse on 10,000 random states, checks the recovery program and experiment digest network, and runs six width-16 search attempts. It also runs the independent ordinary builder and requires byte equality with the normative bounded emitter.

### 1.1 Choice of the tail shear masks

`QM` and `XM` only choose, bit by bit, which of two disjoint-support forms of Maj and Ch enters the encoded words Q and X; `enc_invert` adds back the exact difference, so every choice gives a bijective encoding of the same state and the same collision relation. The round-40 masks were tuned to the round-40 constants. For round 64 they were re-chosen in 1f18d544 by a greedy single-bit pass over the 64 mask bits, starting from the round-40 values, accepting a flip only when the kernel instruction count strictly decreased: 85,866 instructions with the round-40 masks, 85,831 with the shipped masks (and 85,830 once site 76 is enabled). This is a participant-side choice of two constants of the walk (64 complete count-only builds); its cost is covered by the charged offset-search envelope of Section 3.2 at `2^48` operations per build, and no claim depends on its optimality.

## 2. The attack (program `experiments/bssha.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished when its low 20 bits are zero and the 102-bit number F = (x >> 20) mod 2^102 is below Tp = 1664. Thus D = 122, theta = 1664 / 2^122, and L = 5316911983139663491615228241121378304 / 1664 = 41538374868278621028243970633760768 / 13 = 2^111.29956. The key is the 37 bits of x above bit 121 followed by the 11-bit encoding of F. It has 48 bits; F < 1664 < 2^11.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated program of Section 3.2. The start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 20 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask, the lane is extracted and the window test F < Tp decides whether it is a DP. If `key + 1` is in the table, go to step 6. Otherwise write `key + 1` into 48-bit slot t and start the next trail in that lane. Zero is the unwritten sentinel. The slot position is t, so neither t nor the length is stored.
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = ceil(13 L) batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 107,929 keys, when an eighth trail would be cut (`CMAX = 7`), or if step 6 finds no pair.
6. Recovery. Pass 1 recomputes the stored trail length. The two trails are aligned, then stepped together until their next values agree. The first predecessor pair a != b with g(a) = g(b) is returned. The rolled two-lane program has 452 fixed 5-byte records in total, of which 125 are one-time initialization records, and executes 2,670 records per call. Each pass runs at most capr = c + S calls.
Constants printed by `--ledger`: Tp = 1664, L = 41538374868278621028243970633760768 / 13, B = 1325130249475836000000000000000000000, Q = 339233343865814016000000000000000000000, e2max = 647036254626873046875000000000064, c = 41538374868278621028243970633760768, capr = 41538374868278621028525445610471424, and tmax = 107,929. The 108,192 total slots cover 256 initial trails, all stored trails, and seven cut trails. The maximum trail number is 108,191 < 2^18; the boundary test asserts it.
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is a constant of the program).

## 3. Operation ledger

### 3.1 Machine
Machine model of this entry (declared cost-model prices). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices operations and memory; it gives no register count and no instruction size. For round 64 the organizer contract sets `reference_operation_cost = 4912` (`python3 scripts/pareto_candidate.py --family sha256 --rounds 64 --show-contract`).
This entry declares a load/store machine with 256-bit words and 866 registers, 863 data registers and three pointer registers. Charged, one operation each: every XOR, AND, OR and NOT of a 256-bit register, every register move, every set of a register to a constant, every load and store, every pointer addition, comparison and conditional branch, and the one random word. Nothing is free except renaming a bit-sliced rotation.
The body uses this machine's native fixed 32-bit instruction: a 2-bit opcode and three 10-bit register fields. Opcode values 0, 1, and 2 mean XOR, AND, and OR; 3 is reserved. The machine fetches and executes each instruction directly for one operation. There is no decoder or interpreter in the priced path. `Prog.run`, `Prog.compile`, and `Prog.fast` are test mirrors only. All 85,830 kernel instructions use the native format, so the body occupies 343,320 bytes. Recovery and control use native fixed 40-bit instructions. Every executed instruction costs one word operation.

### 3.2 One batch = 85,855 operations for 256 trails
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

Executed per batch: 67,507 XOR + 11,021 AND + 7,302 OR = 85,830 gates; zero NOT, set, move, load, store, or control instructions. Per lane evaluation (one evaluation of g in one lane) this is 335.273 operations.
Validation is by the bounded emitter, its stream hash, the independent builder comparison, the exhaustive algebraic checks inherited from the frontier, and the scalar and end-to-end tests described in Sections 1 and 6.
The generator runs once at the start; its work is charged in the setup row (3.3), its code and peak storage in Sections 3.6 and 7.

### 3.3 Loop, stage 1, handlers and the other events
One batch: 85,830 body instructions + stage-1 test 22 + loop control 3 = 85,855 operations. Stage 1 uses 19 ORs, one NOT, one comparison, and one branch. A DP has all 20 low bits zero, so its lane is flagged.
Loop control of the batch loop: counter increment, compare with the next slice limit, branch back: 3 operations.
Handlers are charged per event at the stated operation bounds and stored as fixed 5-byte control records:
- Stage-1 hit: store the 256 planes to an 8 KiB copy (256 stores), extract the lane (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (at most 15), counters. Below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail: key formation, sentinel encoding, the slot write, the new start, insertion of its 256 bits, reload of the planes, lane arrays, and counters fit below 3,800 operations. The key scan is charged six operations per slot, including extraction, comparison, and branch. The source increments the counter and scans before its `finished > tmax` halt, so the ledger charges `tmax + 1` handled events. At most `tmax` keys are stored.
- Slice check (every 2^48 batches): charged **1,300** each. Cut trail: charged **4,200**; at most 7 cut trails (`CMAX = 7`).
- Recovery program (`RecProg`): a second program evaluates g for two chain values at once, in bits 0..31 and 128..159 of each word. The message and constant array has 112 words (64 schedule words and the 48 constants K10..K57 of the loop), or 3,584 bytes. Preloaded tail constants, masks, `W0 + K0`, and `W8 - K9` remove repeated setup; the preloaded offsets and the state registers that a call overwrites are re-set before each call and charged in the recovery batch below. The live-register permutation across the four-round body and four-word schedule step avoids register-move instructions. There are 452 fixed 5-byte records in total (125 one-time initialization records and 327 records of the per-call program) and 2,670 executed records per call.
- Recovery batch: one call (2,670 records) plus at most 76 surrounding operations, or 2,746 operations per batch, the same in both passes. The 76 are itemized as: 10 re-sets of registers whose start value the call reads and that a call overwrites (registers 5, 6, 10, 11, 12 hold the offsets `-K10..-K14`, register 30 holds `W0 + K0`, register 31 holds `W8 - K9`, and registers 3, 4, 7 must start at zero; the participant found this set by perturbing every non-input register before a call, and checked that five consecutive calls with exactly these ten re-sets reproduce scalar g), 8 copies saving the predecessor pair, 34 for the two-lane equality test (per word: shift by 128, XOR, mask, OR-accumulate; then compare and branch), 18 for the pass-1 DP test (mask, compare, branch, window test of at most 15), 3 for counter increment, cap comparison and branch, and 3 spare. Every call is charged all 76 regardless of pass.
- Setup and emitter: fixed work is 813,600. Section 3.6 gives the participant-measured 176,676,752 wasm operators. Charging two word operations per measured operator plus one gives `813600 + 2 * 176676752 + 1 = 354167105` operations.
Code size: 343,320 bytes of body instructions, 2,260 bytes for 452 recovery instructions, and 6,160 bytes for the other 1,232 control instructions. Total code is 351,740 bytes.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 85,855 | 113,769,057,568,747,899,780,000,000,000,000,000,000,000 |
| slice checks: ceil(B / 2^48) * 1,300 | 6,120,150,872,556,659,749,080,400 |
| stage-1 hits: e2max * 2,800 | 1,811,701,512,955,244,531,250,000,000,000,179,200 |
| finished events: 107,930 * (3,800 + 6 * 108,192) | 70,473,109,360 |
| cut trails: 7 * 4,200 | 29,400 |
| recovery: 2 (c + 2^48) * (2,670 + 76) + 600 + 125 | 228,128,754,776,586,186,688,661,747,292,709,061,333 |
| setup and generator | 354,167,105 |
| charged offset search | 461,900,436,782,186,496 |
| charged selector search | 260,927,303,410,778,112 |
N = 113,998,998,025,037,447,331,371,507,131,763,478,591,406 operations.
N / 4912 has log2 124.125978189133. Claim `time_log2` = 124.12598, rounded upward. The walk never computes block 2: equal block-1 states give equal digests, so one evaluation of g is one block-1 compression of 64 steps, priced by its instructions.

### 3.5 Register file and smaller files
Declared prices: the machine has 866 registers of 256 bits: 863 data registers (Section 3.2) and three pointers. The register file is counted as 27,712 bytes.

### 3.6 Bounded emitter and peak setup storage

The freestanding C source embedded in `experiments/bssha.py` as `GEN_C` is the normative setup implementation. `python3 experiments/bssha.py --gen-c` prints its exact 27,323 bytes. Its SHA-256 is `fad9835cd5fc5194a5e59386b0fb46a6b5d751a3809d7cffca660da0e480cef2`. Pass 0 counts uses and output nodes. Pass 1 rebuilds the same network, allocates registers online, and writes native 32-bit instructions directly to the final code buffer. The emitter enforces `MAX_NODES = 86,123`, `MAX_RECORDS = 85,830`, 863 data registers, a 1,024-slot CSE table, at most 900 occupied slots, and every packed-field bound.

The C emitter reports the 15-field tuple

```text
(records=85830, registers=863, nodes=86087, calls=337942,
 moves=0, error=0, XOR=67507, AND=11021, OR=7302,
 code=343320, counters=16384, uses=86123, state=32000,
 choices=100, constants=736).
```

The emitted byte stream has SHA-256 `7ec18f9ddfb2cd3b106fb0d6f624834b34f063770598d2cf0afc2499de0b70e5`. Its polarity mask is `22273a6c5e8abef676dc5de11e7bc9e3468ac54393e15c2405e9e8acbfb29d63`. Before every experiment, the organizer-run Python mirror checks all 15 fields, the C source hash, stream hash, polarity mask, and equality with the independent builder. The participant also compiled `GEN_C` natively against a small driver that calls `run()` and writes the code buffer: it reported the same 15 fields and polarity mask and wrote the byte stream with the SHA-256 above.

The participant compiled `GEN_C` with clang 20.1.6 and LLD 22.1.8 (`wasm-ld`):

```sh
clang --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

The stripped 22,210-byte module has SHA-256 `423eeb720345ad1673a642868af6a38c16ea8979a884d6bf7c28bc52944e6674`. `llvm-objdump -d` counts 9,465 static instructions. Participant measurement with Wasmtime 50.0.0 and fuel enabled reports exactly 176,676,752 executed operators for exported function `run` (the least fuel budget for which `run` completes, found by bisection). Charging two word operations per fuel unit plus one covers the measured and structural operators:

```text
2 * 176676752 + 1 = 353353505 operations.
```

The organizer does not compile or execute the wasm module. The compiler version, module hash, static instruction count, and fuel count are participant-run setup accounting. The organizer runs the Python mirror and checks the emitted bytes. The setup row is negligible: any bound below 2^100 operations would leave the claimed `time_log2` unchanged.

The emitter image has 9,465 instructions at 36 bytes, or 340,740 bytes. Its scratch is 123,055 bytes:

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
IV, K, PW, PERM, and UCD constants                              736
shadow stack                                                  4,096
total                                                       123,055
```

`experiments/bssha.py` computes the 32,000-byte state and 736-byte constant subtotals from named arrays and compares them with the C report. Complete setup memory is

```text
351740 program bytes + 16384 counters + 27712 registers
+ 3584 recovery arrays + 340740 emitter image + 123055 scratch
= 863215 bytes.
```

Search memory is code 351,740 + counters 16,384 + registers 27,712 + recovery array 3,584 + table 649,152 = 1,048,572 bytes. The count-only searches rebuild each candidate and do not retain DAGs. Their 10,000-instruction image is 360,000 bytes. With 123,055 bytes of builder scratch and 65,536 bytes of trial state, the offset and selector peaks are 548,639 and 548,691 bytes. All phases run sequentially. Search is the overall peak, 1,048,572 bytes (`<= 2^20` bytes).

### 3.7 Preprocessing

No work is free or nonuniform. Final emission plus fixed setup costs 354,167,105 operations. The offset search costs 461,900,436,782,186,496 operations and the selector audit costs 260,927,303,410,778,112. Total preprocessing is 722,827,740,547,131,713 operations, included in N. In target-compression units,

```text
log2(722827740547131713 / 4912) = 47.06433464245901.
```

The claim rounds this upward to `preprocessing_log2 = 47.06434`. There is no nonuniform advice.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bssha.py --loss` (the function `_lossq`); Appendix A recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
pass 1 of step 6 recomputes the two lengths and pass 2 aligns and walks them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F because F < 1664 < 2^11 and the low 11 key bits hold F. Equal keys of two DPs can differ only above bit 158. The lanes do not interact.
The stage-1 test loses no event. A 48-bit key match without a merge ends the run; its probability and one recovery are charged.

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B evaluations, N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(13 L), S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 106167.6940, tmax = 107,929, and CMAX = 7. Let Pi_m = product from i = 0 to m - 1 of (1 - i/N'), PP = Q(Q - 1)/(2N'), and H = (Q(Q - 1)/2 + 2^18 Q)/N'. Let k = 108604 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 263, p = e^(-c/L), and p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)). Let F be uniformly random on 256-bit values and P_F the success probability when every evaluation of g is replaced by lazy sampling from F. Then
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = 0.608400467526 (the no-useful-collision term shift * Pi_Q of Step 2, shift = 1/(1 - kQ/N')),
    P_delay = 0.001462332174,
    P_own = 9.361076e-06,
    P_long = 2.927387e-05,
    P_age = 1.572490e-05,
    P_dist = 4.651724e-06,
    P_cut = 5.144891e-05,
    P_key = C(tmax, 2) / (2^37 Tp) = 2.546708e-05,
    P_table = 1.271732e-06,
    P_tiny = P_start + P_DP-repeat + P_same-batch + P_60 + 2^-90,
    P_start = Q 2^18 / N = 7.679971e-34,
    P_DP-repeat = k^2 L / N' = 3.254759e-34,
    P_same-batch = 255 Q / N' = 7.470675e-37,
    P_60 = exp(-300 + (e^5 - 1) H) = 3.349325e-99.
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

Step 3 (a first collision with a good partner is output). Say that the pair (t, y) with tau = t and V_t = V_y is good when (G1) y is not on the trail of t, (G2) b(y) < b(t), (G3) the trail of y is short, (G4) rho(y) <= B - b(t) and a(t) + rho(y) <= c - 1, and that it is undisturbed when no fresh evaluation of the trail of y after t, up to its first DP, is a collision. Claim. On a good undisturbed pair, if the run does not halt early (eighth cut, table full, stage-1 budget, key false match) and is outside E1 and E2, the program outputs a pair. Proof. Let X and Y be the trails of t and y. The input of X after t is V_t = V_y, the input of Y after y, so the evaluations that X performs after t are the evaluations Y performs after y, the j-th of them in batch b(t) + j for X and in batch b(y) + j for Y (Y does not restart before its DP, because its trail is short, hence never cut, and its first DP is the (rho(y))-th evaluation after y). By (G2) Y evaluates each of them strictly before X, so X only repeats points. Undisturbed, Y reaches its DP first and stores the key; X later repeats it before any cut. Recovery returns the distinct predecessor pair. QED.

Step 4 (the pairs that are not good, and the disturbance). Let W(t, y) be the event (tau = t, V_t = V_y) with xi_t = xi_y = 0 and work on N1 <= k - 1 outside E1 and E2. By Step 2, P(W(t, y) | xi) <= Pi_(t-1) / ((1 - kQ/N') N') <= 1 / ((1 - kQ/N') N'), and sum over t of P(W(t, y) | xi) is at most the sum over t of 1 / N', so at most Q / N'. A pair that is not good fails one of the following; each failure is bounded by the expected number of pairs of that kind times the hazard.
(a) (G1) fails: y is among the a(t) earlier evaluations of the trail of t; a(t) is at most g(t), the number of consecutive 0 coins just before t on its lane (g(t) as in Step 6 (ii)), E g(t) <= sum over i >= 1 of (1 - theta)^i <= L - 1, so the failure has probability at most Q L / N' = P_own.
(b) (G2) fails: y is in the batch of t before t, at most 255 pairs per t: 255 Q / N' (charged in P_tiny).
(c) (G3) fails: y is on a long trail. A long trail has at most M evaluations (it is cut at the first slice check at age >= c, or finishes before), a y has at most Q partners t, and the number of long trails is at most the number of successes of the scan of Step 6 (i) (disjoint windows of c coins 0), with expectation at most p (q + 256) / (1 - p) there: M Q p (q + 256) / ((1 - p) N') = P_long.
(d) (G4) fails. rho(y) > B - b(t) means that the B - b(t) coins after y on its lane are all 0 (they lie in the batches b(y) + 1, ..., b(y) + B - b(t) <= B, inside the run), probability (1 - theta)^(B - b(t)) <= e^(-theta (B - b(t))) for each y. By Step 2 the pairs (t, y) with y < t contribute at most sum over t of (t - 1) Pi_(t-1) / ((1 - kQ/N') N') e^(-theta (B - b(t))), and (t - 1) Pi_(t-1) / N' = Pi_(t-1) - Pi_t, so, with b(t) <= ceil(b / 256) for t <= b and the sum of Pi_(t-1) - Pi_t over t in (a, b] equal to Pi_a - Pi_b, at most (1 - kQ/N')^-1 sum over the bins (a, b] (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = P_delay (the bins and the enclosures of Pi are in Appendix A). The second part, a(t) + rho(y) >= c: a(t) <= g(t) and rho(y) >= 1, so it requires g(t) + (rho(y) - 1) >= c - 1. If t and y are on different lanes the two coin sets are disjoint and g(t), rho(y) - 1 are dominated by independent geometric variables with values in 0, 1, 2, ...; the sum of two such variables is at least c - 1 only if a single i.i.d. sequence of coins has at most one 1 among its first c coins, hence among its first c - 1 coins: probability at most (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. If they are on the same lane and (G1) and (G3) hold, y is on an earlier trail of the lane that is short, so it ended with a 1 before the start of the trail of t, and the two coin sets (those of rho(y) up to that 1, those of g(t) after it) are disjoint: the same bound. At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': PP p2 = P_age.
(e) Disturbance. For a good pair let r' be the number of evaluations of the lane of y with index > t up to and including the first with xi = 1; the coins there are independent of F_t (L5, t is a stopping time) and r' is dominated by a geometric variable of mean L. The evaluations of Y after t and before its DP are at most r' fresh evaluations, each a collision with conditional probability at most (Q + 2^18) / N' given the history (L1; the last one, a DP-valued evaluation, is covered by E2, and counting it here only overcounts). For this bound W(t, y) is taken without the restriction to N1 <= k - 1 and outside E1, E2: it is the event (tau = t, V_t = V_y), which is F_t-measurable, so P(W(t, y) and disturbed) <= P(W(t, y)) L (Q + 2^18) / N'; the events W(t, y) for different (t, y) are disjoint (the values V_y are distinct before tau), so the sum of P(W(t, y)) is at most P(tau <= Q) <= sum over t of (t - 1)/N' = PP: PP L (Q + 2^18) / N' = P_dist.

Step 5 (the sum). With P(tau <= Q, N1 <= k - 1) >= 1 - Pi_(Q-k+1) - 2^-40 and the failure bounds above, the early halts are charged in Step 6 (eighth cut) and Step 7 (table full, key false match, stage-1 budget).

Step 6 (the cut count and the long trails; no premise). Let K be the number of trails that the run cuts or would cut; the eighth one halts the run because `CMAX = 7`. Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.
(i) K_A. The disjoint-window scan from the credited proof bounds eight fresh cut trails by the upper tail of `Binomial(n2,p)` with `n2 = k + 263` and `p = exp(-c/L)`. Its value is `2.6795e-10`.
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
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; the bound is `Q L / N' = 9.361e-06`.
- X: the same-lane and different-lane geometric-tail calculation gives `E_X = 1.593601e-05`.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^18) / N': E_J2a2 <= (Q + 2^18) L Q (Q - 1) / (2 N'^2). E_J2a = 9.303449e-06.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2 = 1.572490e-05.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 1.123207e-06.
Combining the fresh tail with the same S, X, J2a, J2b, and Y root-event bounds gives `P_cut = 5.144891e-05`. There is no cut-count premise.

Step 7 (the early halts and residual events). The early halts are the eighth cut, table full, key false match, stage-1 budget, or recovery failure.

Table capacity and key matches. Outside `P_60`, fewer than 60 collisions occur. The number of finished trails is then at most `N1 + 59`, so filling `tmax` entries requires `N1 >= tmax - 59`. The Chernoff bound is `P_table = 1.271732e-06`. A false 48-bit key match costs `P_key = 2.546708e-05`, using key space `2^37 * 1664`.

Sixty collisions. At a fresh evaluation t, the collision probability is at most `(t - 1 + 2^18) / N'`. For `w = e^5`, multiplication of the conditional moment bounds gives

```text
E[w^C] <= exp((w - 1) H),
P(C >= 60) <= exp(-300 + (e^5 - 1) H)
             = P_60 = 3.349325e-99.
```

Stage-1 budget. Let `eta_t` mark that the low 20 bits of the independent uniform value `V_t` are zero, and let `mu2 = Q / 2^20 = 323518127313436523437500000000000`. Fresh stage-1 hits are at most `sum eta_t`, which is `Binomial(Q, 2^-20)`. The multiplicative Chernoff bound gives

```text
P(fresh hits > 1.5 mu2) <= exp(-0.108 mu2)
                            = exp(-34939957749851144531250000000000)
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
         = 15291035365253017155657598319.3239772144319...
         > 1000.
```

Appendix A evaluates `A_replay` downward and charges the outward upper bound `P_replay-simple < exp(-1000)`. It also checks

```text
240 M = 9969209968386869046846106946513141760
      <= 339233343865814016000000000000000000000 = Q.
```

Outside the root-event union and the new `P_replay-simple` term, each of the 60 replay windows has at most `2 M / 2^20` hits. Thus the repeated hits are at most `120 M / 2^20 <= mu2 / 2`. Together with at most `1.5 mu2` fresh hits, this is at most `2 mu2`, below `e2max = 2 mu2 + 64`. The residual probability of the stage-1 budget halt is below `P_stage-fresh + P_replay-simple < 2 exp(-1000)`, in addition to `P_60` and the root-event union already charged in `P_cut`.

Recovery and the three small structural events. A recovery without a pair comes from a false key match, already charged by `P_key`, or from one of the fewer than `2^18` starts lying on an evaluated trail. The latter event is `P_start = Q 2^18 / N = 7.679971e-34`. Outside those events, Lemma 1 returns a pair within `capr` calls. A repeated DP-valued output costs `P_DP-repeat = k^2 L / N' = 3.254759e-34`. A partner in the same batch costs `P_same-batch = 255 Q / N' = 7.470675e-37`.

The outward-rounded certificate gives `P_start + P_DP-repeat + P_same-batch + P_60 < 1.094221e-33`. It adds `P_stage-fresh` and the new `P_replay-simple` term to `residual_actual`; each is below `exp(-1000)`. The total fits inside the charged `2^-90 = 8.077936e-28` reserve. The certificate uses outward rounding for every exponential and rational term, so it needs no probabilistic rounding allowance. This proves the lemma. QED.
Consequently the printed float bound is

```text
1 - 0.608400467526 - 0.001462332174 - 9.361076e-06
  - 2.927387e-05 - 1.572490e-05 - 4.651724e-06
  - 5.144891e-05 - 2^-40 - 2.546708e-05
  - 1.271732e-06 - P_tiny
= 0.3900000010002157.
```

Appendix A independently certifies `P_F >= 0.390000001000 >= 0.39` with exact rationals and outward-rounded decimals.

Sensitivity is recomputed from the live plan by replacing N with `N/(1-eps)` and reoptimizing Tp and B:

| hazard deficit eps | replacement Tp | extra time bits to restore 0.39 |
| ---: | ---: | ---: |
| 0.01 | 1655 | 0.00725118 |
| 0.05 | 1621 | 0.03700352 |
| 0.10 | 1578 | 0.07600588 |
| 0.25 | 1441 | 0.20752824 |

A collision-hazard surplus helps. No robustness margin is treated as a theorem.

## 5. Premise H1 and its evidence

H1 compares this fixed function with a uniformly random function. Its four clauses are:

- (a) Distinct fresh evaluated inputs have independent uniform outputs and pair-collision hazard `2^-256`.
- (b) Iterates from the starts `r+t` have the first-collision law of a random mapping.
- (c) A fresh output is a DP with probability `1664/2^122`, independently of collision events.
- (d) Under the adaptive program history and later DP flags, a fresh output hits any fixed earlier non-DP output with probability at least `2^-256`.

Lemma 2 proves the bound for the random function. H1 transfers that bound to the fixed target. The circuit, ledger, memory, and random-function theorem are exact claims.

Support of H1 (stated; it is not measured at width 256):

1. H1 is the generic premise of parallel collision search with distinguished points. Paul C. van Oorschot and Michael J. Wiener, "Parallel Collision Search with Cryptanalytic Applications", *Journal of Cryptology* 12(1):1-28, 1999, DOI 10.1007/PL00003816, model a fixed compression function iterated from fresh starts, without a chosen input difference, by a random function. The generic entries of this track use the same premise: mitchuski 3017c952, 1884db5b, and 4684dfc2; lamb356 3642e1cd; dariolina 6b678689; 0xplemonade's 7523902c, 7347a2b6, 60dbf898, 332b47e1, 5ed693e8, ff37a322, and c9ae3732; and mpjunior92's 1f18d544.
2. Clause (d) fails in the adverse direction only if `g`, along its own iterates, collides less often than a random function by a constant factor `1 - eps`. Such a property would separate this 64-step function from a random function in a way that no published result shows. This entry chooses no input difference and uses no differential property.
3. A deviation that raises the collision hazard helps. Section 4 prices a deficit exactly: 0.00725118 bit for `eps = 0.01`, 0.03700352 bit for `eps = 0.05`, 0.07600588 bit for `eps = 0.10`, and 0.20752824 bit for `eps = 0.25`.
4. The program checks agree with random-function reference values at their scopes. For `proj-k0-w256`, 256 independent uniform 16-bit projections contain a pair with probability 0.392678 per trial, or 100.53 of 256 trials. The expected number of equal pairs is `C(256,2)/2^16 = 0.498047` per trial, or 127.50 over 256 trials. For the exact seven-batch `plan(16)` (unchanged from the round-40 package), the credited lazy-random-function reference over 10,000,000 complete mappings gave probability 0.6958435 with standard error 0.00014548, or 178.14 successes per 256 trials. A participant-run replay of both declared experiments, using the organizer request format and organizer-style per-trial seeds derived from a substitute commitment (not the organizer's own seed material), returned 187 checked width-16 search pairs in 256 trials for `bssha-n16` and 88 checked full-width projection pairs in 256 trials for `proj-k0-w256`; every returned pair was recomputed with `verifier/hash_functions.py:digest(..., "sha256", 64)` and satisfied the declared low-16-bit event. These are within about 1.6 standard deviations of the references (sd about 7.4 and 7.8 trials). The organizer's own counts are produced by its executor at evaluation time. These are consistency checks that can expose implementation-level deviations. No count is used to change the score.

Limitation: H1 cannot be measured at width 256, so these experiments do not measure the full-width collision hazard or the success probability at `2^128` scale.

## 6. Experiments

Two organizer consistency checks run `experiments/bssha.py`. Before dispatch, `bounded_check` runs the byte-exact mirror of the normative C emitter. The organizer recomputes the complete digest of every returned message pair.
`bssha-n16`: per trial, one attempt of the 256-lane search at width 16 (DP = low 2 bits zero, plan(16): 7 batches, cut rule, table, recovery) on the walk g16(x) = the low 16 bits of the complete digest of M(x), x < 2^16. Each batch runs the shipped program on the 256 planes (the 240 high input planes zero), then the experiment's digest network (`DigestNet`, bit-sliced, experiment code only, not in the ledger) inverts walk B, forms cv1 = IV + state and runs block 2; the recovery runs the rolled recovery program and the same inverse and block 2 in scalar form. The trials run side by side: the planes of trial i occupy bits 256 i to 256 i + 255 of each word, so one pass of the program and of the digest network serves every live trial, and each bitwise record acts on every trial's 256 bits alone. The trial returns M(x), M(y) when the attempt succeeded and two nulls otherwise. Checked event: the messages are distinct and their complete 64-step digests agree in the low 16 bits. This is exact, because at width 16 the walk is those 16 digest bits. The width-16 walk differs from the width-256 walk g only in the map after the program (inverse, block 2, low 16 bits); it runs the same program, search, table and recovery.
`proj-k0-w256`: per trial, 256 points at width 256 (source by trial index mod 3: uniform from the seed, counter r + i, iterates of g from 256 seed-derived starts) evaluated with the shipped program; their complete digests are formed by the digest network; the trial returns two points whose digests agree in the low 16 bits when the set holds such a pair. Checked event: as above. It checks at full width the program, the inverse of walk B, the chaining value, block 2 and the message construction.
The experiments check execution, witnesses, and agreement with the scope-matched reference values in Section 5. Their counts do not enter the cost or success bound.
The digest network is built with the same `Gen` class as the kernel. Its inverse of walk B contains a four-variable sum with the nonzero constant `1 + K_62`; the inherited four-word carry-fusion branch of `Gen._baseline` would have dropped that constant, so the branch is now guarded by `not cv` (taken only when the absorbed constant is zero). At round 40 no digest-network sum reached that branch with a nonzero constant. The guard does not change the kernel: all 39 kernel four-variable sums have zero constant, and the emitted stream hash is unchanged by it. The normative C emitter's `addm` contains the same branch (`nv == 4 && !bb`) without the guard; it is unaffected for the same reason, since the kernel has no four-variable sum with a nonzero constant (the C and Python streams are byte-identical). The self-test checks the digest network against scalar SHA-256 on 256 random full-width lanes.

## 7. Memory

Table: 108,192 slots * 48 bits = 649,152 bytes. Slot t belongs to trail t and stores `key + 1`; zero is empty. The maximum key is 281,474,976,710,271, so the sentinel transform fits.
Code: 85,830 body instructions * 4 bytes = 343,320 bytes. The 452 recovery records use 2,260 bytes. The other 1,232 fixed 5-byte instructions use 6,160 bytes. Total code is 351,740 bytes.
Counters and copies use 16,384 bytes. The 866 registers use 27,712 bytes. The 112-word recovery array uses 3,584 bytes. No advice. Memory peak is `max(863215,1048572) = 1048572` bytes, below `2^20`.
The table size is the largest that fits: `floor(8 * (2^20 - 351740 - 27712 - 16384 - 3584) / 48) - 263 = 107929`. Appendix A derives Tp = 1664 and certifies `P_F >= 0.39`.

## 8. Heuristics, conventions and what is credited

The premise is H1. The 866-register file and native formats are declared machine prices, not statistical premises. Lemma 2 proves the cut count. There is no advice.

Direct dependency: 6f66a099-7772-441d-ab2c-67d94c620e13 (sraiw, commit 18b1400, round 64, 124.12599), 1f18d544-cd04-4177-8739-fad19d55a98a (mpjunior92, commit 840c9a1, round 64) and its parent 27984c2d-fc4b-4285-a430-c5f364c10a7e (sraiw, round 40) supply the complete program `experiments/bssha.py` (kernel generator, normative C emitter, allocator, rolled recovery, search, table, plan, probability certificate and experiments) and the structure and wording of this proof. Through them, f7b1dea4-2883-45d6-9c0c-89a5d4ad1b1a supplies the recovery compaction, fb8a3bce-1839-4b9a-ab67-76670b4a05c9 the baseline package, b3f10279-3fa4-4d7b-9011-3faa2ae352c8 the fused kernel, schedule, allocator, and recovery design, and ff37a322-c5e7-4656-bb89-02f1a5d0e213 the native-4-byte machine and accounting base. New here: bit-interleaved round and message-schedule emission with targeted allocator non-target fallback (`_MF`) (863 data registers with zero moves vs 905), site-76 addition-choice selector hint (85,830 instructions vs 85,831), preloaded `W0 + K0` and `W8 - K9` recovery initialization (2,670 executed recovery records per call vs 2,671), the re-measured wasm32 emitter, and the re-derived 107,929-trail plan (`Tp = 1664`), ledger and certificate. The earlier round-64 entry c9ae3732-bbe0-4b3f-8e14-4c685a7d0ec2 is cited for its score only.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate, and `certify` recomputes the bound of Lemma 2 in exact rationals and 60-digit decimals with outward rounding: the line `P_lower certified` is a proved lower bound on P_F, asserted >= 0.39. The same numbers come from `python3 bssha.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 85830, 22, 3, 256
INSTR_REC = 85830
PH7, EXTRA, RECINIT = 2670, 76, 125
N_BITS, S1, W, KAPPA = 256, 20, 102, 13         # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE = 2800, 3800, 4200, 1300
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 7
CUT_HALT_ORDER = CMAX + 1
assert CUT_HALT_ORDER == 8
WASM_RUN_OPERATORS, WASM_OPERATOR_FACTOR = 176676752, 2
BODYB, CTRLB, RECB, REC_RECORDS = 4, 5, 5, 452
CONTROL, REGFILE, COUNTERS, ADVICE, ARRAYS = 1207, 27712, 16384, 0, 3584
KEYB = SLOTB = 48                              # key+1; zero is the unwritten sentinel
SEARCH_EVAL_OPS = 1 << 48
OFFSET_SEARCH = 1641 * SEARCH_EVAL_OPS            # 64 endpoint + 1 initial + 3 * 192 coordinate + 1000 perturbation builds
SELECTOR_SEARCH = 927 * SEARCH_EVAL_OPS
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 21, 18                        # B is a multiple of GRAIN; trail numbers are below 2^18
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP
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
    cuts = 1 - sum(comb(n2, j) * p ** j * exp((n2 - j) * log1p(-p)) for j in range(CUT_HALT_ORDER))
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
    exp_minus_1000 = upr(Dm(-1000).exp())
    p_stage_fresh = exp_minus_1000
    p_replay_simple = exp_minus_1000
    residual_actual = p_start + p_dp_repeat + p_same_batch + p_60 + p_stage_fresh + p_replay_simple
    residual_reserve = Dm(2) ** -90
    assert residual_actual < residual_reserve
    residual_slack = residual_reserve - residual_actual
    p_tiny = p_start + p_dp_repeat + p_same_batch + p_60 + residual_reserve
    terms = [pi_up(Q) * shift, delay,                            # collision (no partner), detection delay
             fd(Q * L / Np, True),                               # the partner is on the trail of t
             up(fd(Fraction(M * Q) / Np, True) * EK),            # the partner is on a trail with c free evaluations
             fd(PP, True) * p2,                                  # trail of t too old when the DP is reached
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
                "residual actual": residual_actual,
                "2^-90 reserve": residual_reserve,
                "reserve slack": residual_slack, "P_tiny charged": p_tiny}
    return 1 - sum(terms), residual


lo, hi = 1.0, float(tmax - 59)                                 # the largest mean number of trails the table holds (tail within 2^-19.5)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax - 59) <= -19.5 else (lo, mid)
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
        ("finished events: (tmax + 1) * (3800 + 6 * (tmax + 263))", (tmax + 1) * (EVENT + 6 * (tmax + LANES + CMAX))),
        ("cut trails: 7 * 4200", CMAX * CUTOPS),
        ("recovery: 2 (c + 2^48) * (%d + 76) + 600 + %d" % (PH7, RECINIT), 2 * capr * (PH7 + EXTRA) + 600 + RECINIT),
        ("setup and generator", SETUP_FIXED + emitter),
        ("charged offset search", OFFSET_SEARCH),
        ("charged selector search", SELECTOR_SEARCH)]
N = int(sum(v for _, v in rows))
assert N == 113998998025037447331371507131763478591406
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
Tp = 1664  tmax = 107929  B = 1325130249475836000000000000000000000  e2max = 647036254626873046875000000000064  c = 41538374868278621028243970633760768
memory bytes = 1048572
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000001000
residual P_start          7.67997073721520006243924880755898383378872271762767196224305E-34
residual P_DP-repeat      3.25475948442287268865179991181382499251868515473558361840967E-34
residual P_same-batch     7.47067465969038397187045458193794819077199728820129474408170E-37
residual P_60             3.34932457036842131477442277370413737495126843601246154021598E-99
residual fresh exponent   34939957749851144531250000000000
residual replay exponent  15291035365253017155657598319.3239772144319001043581080936417
residual P_stage-fresh    5.07595889754945676529180947957433691930610687878259230750892E-435
residual P_replay-simple  5.07595889754945676529180947957433691930610687878259230750892E-435
residual residual actual  1.09422008962977631350629191739547467744981798696514568753968E-33
residual 2^-90 reserve    8.07793566946316088741610050849573099185363389551639556884766E-28
residual reserve slack    8.07792472726226458965296544557655703710685939733652591739078E-28
residual P_tiny charged   8.07794661166405718517923557141490494660040839369626522030454E-28
main loop: B * 85855                                 113769057568747899780000000000000000000000
slice checks: ceil(B / 2^48) * 1300                  6120150872556659749080400
stage-1 hits: e2max * 2800                           1811701512955244531250000000000179200
finished events: (tmax + 1) * (3800 + 6 * (tmax + 263)) 70473109360
cut trails: 7 * 4200                                 29400
recovery: 2 (c + 2^48) * (2670 + 76) + 600 + 125     228128754776586186688661747292709061333
setup and generator                                  354167105
charged offset search                                461900436782186496
charged selector search                              260927303410778112
N = 113998998025037447331371507131763478591406
certificate: 2^12412597 * 4912^100000 <= N^100000 < 2^12412598 * 4912^100000
log2(N/C) = 124.1259781891
time_log2 = 124.12598
```
