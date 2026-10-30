# sha256-r40: a 43,541-instruction native bit-sliced birthday walk

This package builds on fb8a3bce-1839-4b9a-ab67-76670b4a05c9, combining the accepted native-4-byte machine and accounting of ff37a322-c5e7-4656-bb89-02f1a5d0e213 with circuit and schedule ideas documented by b3f10279-3fa4-4d7b-9011-3faa2ae352c8. The implementation is independent: the bounded Python generator and freestanding C emitter both build the network, and the self-test requires byte equality, scalar equivalence, chained-walk equivalence, zero moves, recovery equivalence, and complete two-block digest agreement.

The kernel has 34,096 XOR, 5,866 AND, and 3,579 OR native instructions, or 43,541 total. The savings come from the fused bit-0 and bit-1 `_t1hg + add3` path, 15 four-word carry fusions, the `_ch3` eight-gate columns in the walk-B tail, two-operand constant-adder folding (`_adduc`), split `W[16]`/`W[23]` constant folding across steps 19..24, and the schedule placement that permits a zero-move 884-register allocation. The rolled recovery has 404 records, 76 initialization records, and executes 1,393 records per call, eliminating three redundant state-shift register moves by advancing the live register map `(a..h, w0..w15)` directly across the 20 two-round loop iterations and 8 initial schedule steps.

The native body instruction remains exactly 32 bits: a 2-bit opcode and three 10-bit register fields. The machine executes it directly for one word operation. No decoder or interpreter runs in the priced path. The body occupies 174,164 bytes. Control and recovery use native fixed 5-byte instructions.

The six-offset search evaluates 1,641 complete builds. The ledger reserves one baseline and two passes over all 203 alternatives in the current 56-site reduction inventory, or 407 complete builds. Every build is charged at `2^48` operations. The emitted selector is the all-zero baseline, so no unrecorded selector result affects the circuit. The final plan uses 136,267 completed trails in 136,530 48-bit sentinel slots. Search memory is 1,048,575 bytes.

The exact ledger is

```
N = 57747387988117957968284748330063459455061 word operations
log2(N / 2896) = 123.907033600881
```

The claim rounds upward to `time_log2 = 123.90704`, which is 0.0025664 bit below fb8a3bce's 123.90960 and 0.0032564 bit below b3f10279's 123.91029. Setup memory is 647,691 bytes. H1, the fixed-function random-function comparison stated in Sections 4 and 5, is the only score-critical premise. Circuit changes, counts, and memory bounds are exact checked claims, not premises.

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

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished when its low 20 bits are zero and the 102-bit number F = (x >> 20) mod 2^102 is below Tp = 2105. Thus D = 122, theta = 2105 / 2^122, and L = 5316911983139663491615228241121378304 / 2105 = 2^110.96108. The key is the 36 bits of x above bit 121 followed by the 12-bit encoding of F. It has 48 bits; F < 2105 < 2^12.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated program of Section 3.2. The start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 20 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask, the lane is extracted and the window test F < Tp decides whether it is a DP. If `key + 1` is in the table, go to step 6. Otherwise write `key + 1` into 48-bit slot t and start the next trail in that lane. Zero is the unwritten sentinel. The slot position is t, so neither t nor the length is stored.
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = ceil(35 L) batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 136,267 keys, when an eighth trail would be cut (`CMAX = 7`), or if step 6 finds no pair.
6. Recovery (checkpoint resolution). Pass 1 walks the two trails together for at most cr = ceil((63/5) L) = 31825696431144779094703979020489011 calls, recording every D-th point of each unfinished trail (D = ceil(cr / kchk) = 2486771091666258719698701283052, kchk = floor(table_bytes / 64) - 1 = 12798) and the two terminal lengths and endpoints; if either trail has not reached a DP within cr steps, the attempt halts. Pass 2 aligns the longer trail to each checkpoint of the shorter trail by a walk of (l_long - l_short) mod D < D steps, locates by binary search the last checkpoint pair where the aligned walks still differ (at most ceil(log2(kchk + 1)) <= 16 probes of < D steps each), and steps the two trails together from that checkpoint pair for at most D steps until their next values agree. The first predecessor pair a != b with g(a) = g(b) is returned. The rolled two-lane program has 404 fixed 5-byte records, 76 initialization records, and executes 1,393 records per call. Pass 1 runs at most cr calls and pass 2 runs at most 17 D calls.
Constants printed by `--ledger`: Tp = 2105, L = 5316911983139663491615228241121378304 / 2105, B = 1324456381789593000000000000000000000, Q = 339060833738135808000000000000000000000, e2max = 646707217670699707031250000000064, c = 88404712308735497485288830612469473, cr = 31825696431144779094703979020489011, kchk = 12798, capr = 88404712308735497485570305589180129, and tmax = 136,267. The 136,530 total slots cover 256 initial trails, all stored trails, and seven cut trails. The maximum trail number is 136,529 < 2^18; the boundary test asserts it.
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is a constant of the program).

## 3. Operation ledger

### 3.1 Machine
Machine model of this entry (declared cost-model prices). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices operations and memory; it gives no register count and no instruction size.
This entry declares a load/store machine with 256-bit words and 887 registers, 884 data registers and three pointer registers. Charged, one operation each: every XOR, AND, OR and NOT of a 256-bit register, every register move, every set of a register to a constant, every load and store, every pointer addition, comparison and conditional branch, and the one random word. Nothing is free except renaming a bit-sliced rotation.
The body uses this machine's native fixed 32-bit instruction: a 2-bit opcode and three 10-bit register fields. Opcode values 0, 1, and 2 mean XOR, AND, and OR; 3 is reserved. The machine fetches and executes each instruction directly for one operation. There is no decoder or interpreter in the priced path. `Prog.run`, `Prog.compile`, and `Prog.fast` are test mirrors only. All 43,541 kernel instructions use the native format, so the body occupies 174,164 bytes. Recovery and control use native fixed 40-bit instructions. Every executed instruction costs one word operation.

### 3.2 One batch = 43,565 operations for 256 trails
Representation is bit-sliced: one 256-bit machine word holds one bit position for 256 trails, and a SHA-256 rotation only renames planes. Signals carry a node and a free polarity bit. The pivot full adder costs five gates. `add3` carries the pair `(u,U)`, representing `1 if U else 2u`; its T0, T1, and T2 templates cost nine gates per ordinary column and eight at bit 30. The self-test exhausts all 32 input rows for each template relation.

The new round fusion passes `h[0]` and `u[0] = h[0] XOR Ch[0]` into `add3`. Bit 0 combines the half-adder on the other two operands with the `h + Ch` carry in seven gates for either absorbed carry. At bit 1, `_add_u` begins from a carry-free root and may use the alternate `ch1 = f1 XOR (~e1 AND (f1 XOR g1))` form when its stored polarity avoids a penalty, while `_adduc` folds the round constant into `h + u` across suffix columns `m..31` using the 96-word `UCD` template table. The selector absorbs `c0 + 2c1 + delta` into the folded constant, and splits `W[16]` and `W[23]` into carry-saved sums plus deferred constants across steps 19..24. These are exact rearrangements of `h + Ch + Sigma1 + K + W` and are checked against scalar SHA-256.

For every four-variable sum with zero absorbed constant, `addm` orders `(A,B,D,C)`, computes `add3(A,B,C)` with the bit-0 half-adder carry `D0`, and then adds `[0,D1..D31]`. The outgoing bit-0 carry occupies the otherwise unused pair-carry slot at bit 1, so the second adder's bit 1 is a two-gate half adder. All 15 applicable sums use 429 gates.

The walk-B tail keeps the fixed per-bit shears `QM = 0x74a40866` and `XM = 0x46eb57e6`. `_ch3` fuses `B + Ch` into the first `add3`: each column forms `w5 = hg XOR (e AND (f XOR g))` and selects a polarity-matched multiset of `[W,a,Sigma1(e)]`. Its column relation is exhaustively checked. `enc_invert` applies the matching Q and X corrections, so equal walk values imply equal block-1 states and complete digests.

The schedule advances `W[21]` and `s23_raw` to step 19, defers the constant adders for `W[22]` and `W[23]` until after their rounds, and advances `W[32]` to step 31. The streaming allocator routes short-lived nodes into idle output targets and otherwise takes a dying operand or the lowest free non-target register. The output permutation `(6,1,7,0,5,4,2,3)` needs zero moves. The measured peak is 884 data registers.

The six offsets are preprocessing output. Their deterministic search evaluates exactly 1,641 complete candidates: 64 endpoint placements, one initial coordinate point, three complete sweeps of 192 bits, and 1,000 perturbations from the fixed xorshift seed `6a09e667bb67ae85`. Bits are visited by increasing word and then increasing bit. A strict improvement replaces the incumbent, so ties retain the earlier candidate.

The addition audit is also charged preprocessing. Among 56 nonconstant `addm` sites, 31 have exactly three operands and admit one three-of-three reduction. Seventeen have four operands and admit four three-of-four reductions plus six unordered pair-first reductions; two of those also admit the constant-carry form. The remaining eight sites have fewer than three operands. One complete pass therefore has

```text
31 + 17 * 10 + 2 = 203 alternatives.
```

The charged validation envelope contains the deterministic fused baseline and all 203 alternatives in two complete passes. The candidate does not depend on an unshipped winning alternative: its emitted hint table is the all-zero baseline. The envelope is `1 + 2 * 203 = 407` complete builds.

Both searches use a count-only builder with an eight-probe CSE table and an eight-entry recent-gate ring. One complete build has at most two builder passes, 160 multiword sums, 64 first-triple masks per sum, 32 columns, 13 current-column forms, 13 lookahead forms, and 12 trial gates per form. Charging 1,024 word operations for each trial gate, including lookup, rollback, and bookkeeping, gives

```text
2 * 160 * 64 * 32 * 13 * 13 * 12 * 1024
= 1,360,967,761,920 < 2^41 operations.
```

One more copy covers the rest of the network, scoring, comparisons, loop control, and deterministic candidate generation. The package charges `2^48` operations per complete build, more than 128 times that doubled structural bound. The exact search charges are

```text
offsets:  1641 * 2^48 = 461900436782186496 operations
selector:  407 * 2^48 = 114560315521236992 operations.
```

These bounds follow the loops and fixed array limits. They do not rely on a development call counter or an unshipped trace.

Executed per batch: 34,096 XOR + 5,866 AND + 3,579 OR = 43,541 gates; zero NOT, set, move, load, store, or control instructions. Per trail this is 170.082 operations.
Validation is by the bounded emitter, its stream hash, the independent builder comparison, the exhaustive algebraic checks inherited from the frontier, and the scalar and end-to-end tests described in Sections 1 and 6.
The generator runs once at the start; its work is charged in the setup row (3.3), its code and peak storage in Sections 3.6 and 7.

### 3.3 Loop, stage 1, handlers and the other events
One batch: 43,541 body instructions + stage-1 test 21 + loop control 3 = 43,565 operations. Stage 1 uses 19 ORs, one comparison (`nz == ALL`), and one branch (`hit = ALL ^ nz` runs in the stage-1 hit handler only when `nz != ALL`). A DP has all 20 low bits zero, so its lane is flagged.
Loop control of the batch loop: counter increment, compare with the next slice limit, branch back: 3 operations.
Handlers are charged per event at the stated operation bounds and stored as fixed 5-byte control records:
- Stage-1 hit: invert `nz` (`hit = ALL ^ nz`, one NOT), store the 256 planes to an 8 KiB copy (256 stores), extract the lane (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (at most 15), counters. Below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail: key formation, sentinel encoding, the slot write, the new start, insertion of its 256 bits, reload of the planes, lane arrays, and counters fit below 3,800 operations. The key scan is charged six operations per slot, including extraction, comparison, and branch. The source increments the counter and scans before its `finished > tmax` halt, so the ledger charges `tmax + 1` handled events. At most `tmax` keys are stored.
- Slice check (every 2^48 batches): charged **1,300** each. Cut trail: charged **4,200**; at most 7 cut trails (`CMAX = 7`).
- Recovery program (`RecProg`): a second program evaluates g for two chain values at once, in bits 0..31 and 128..159 of each word. The message and constant array has 64 words, or 2,048 bytes. Preloaded offsets and tail constants remove repeated setup and masks, and live-register permutation across the two-round body and eight-step schedule loop removes three register-move instructions. There are 404 fixed 5-byte records, 76 initialization records, and 1,393 executed records per call.
- Recovery batch: one call (1,393 records) plus at most 39 surrounding operations, or 1,432 operations per batch, the same in both passes (pass 1 runs at most cr = 31825696431144779094703979020489011 batches plus kchk * 80 = 12798 * 80 checkpoint-store operations; pass 2 runs at most 17 * D = 17 * 2486771091666258719698701283052 batches plus 16 * 100 probe operations and 600 + 76 fixed operations; 47 additional 5-byte control instructions, RECOVERY_CODE = 94 vs 47, hold the two-pass checkpoint and binary-search control).
- Setup and emitter: fixed work is 813,600. Section 3.6 gives the participant-measured 89,747,938 wasm operators. Charging two word operations per measured operator plus one gives `813600 + 2 * 89747938 + 1 = 180309477` operations.
Code size: 174,164 bytes of body instructions, 2,020 bytes for 404 recovery instructions, and 6,395 bytes for the other 1,279 control instructions. Total code is 182,579 bytes.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 43,565 | 57,699,942,272,663,619,045,000,000,000,000,000,000,000 |
| slice checks: ceil(B / 2^48) * 1,300 | 6,117,038,595,926,057,453,767,100 |
| stage-1 hits: e2max * 2,800 | 1,810,780,209,477,959,179,687,500,000,000,179,200 |
| finished events: 136,268 * (3,800 + 6 * 136,530) | 112,145,838,640 |
| cut trails: 7 * 4,200 | 29,400 |
| recovery: cr * (1,393 + 39) + kchk * 80 + 17 * D * (1,393 + 39) + 16 * 100 + 600 + 76 | 45,634,935,244,854,847,065,888,443,141,375,907,756 |
| setup and generator | 180,309,477 |
| charged offset search | 461,900,436,782,186,496 |
| charged selector search | 114,560,315,521,236,992 |
N = 57,747,387,988,117,957,968,284,748,330,063,459,455,061 operations.
N / 2896 has log2 123.907033600881. Claim `time_log2` = 123.90704, rounded upward. The walk never computes block 2: equal block-1 states give equal digests, so one evaluation of g is one block-1 compression of 40 steps, priced by its instructions.

### 3.5 Register file and smaller files
Declared prices: the machine has 887 registers of 256 bits: 884 data registers, matching the exact live peak, and three pointers. The register file is counted as 28,384 bytes.

### 3.6 Bounded emitter and peak setup storage

The freestanding C source embedded in `experiments/bssha.py` as `GEN_C` is the normative setup implementation. `python3 experiments/bssha.py --gen-c` prints its exact 27,033 bytes. Its SHA-256 is `0838d00e6b24114617a61f90592b5f0b7232bc986d8106e345f5270e620672fa`. Pass 0 counts uses and output nodes. Pass 1 rebuilds the same network, allocates registers online, and writes native 32-bit instructions directly to the final code buffer. The emitter enforces `MAX_NODES = 43,836`, `MAX_RECORDS = 43,541`, 884 data registers, a 1,024-slot CSE table, at most 900 occupied slots, and every packed-field bound.

The C emitter reports the 15-field tuple

```text
(records=43541, registers=884, nodes=43798, calls=174430,
 moves=0, error=0, XOR=34096, AND=5866, OR=3579,
 code=174164, counters=16384, uses=43836, state=28928,
 choices=56, constants=640).
```

The emitted byte stream has SHA-256 `cff4d5fb7f9293ddec010dc88c4923fe4b136040aa6a342692035210318be3ce`. Its polarity mask is `e7309a100cc5bf67eea64df025e3b2545785e20fdeb3df8208948c9c227bb195`. Before every experiment, the organizer-run Python mirror checks all 15 fields, the C source hash, stream hash, polarity mask, and equality with the independent builder.

The participant compiled `GEN_C` with Homebrew clang 20.1.6 and LLD 22.1.8:

```sh
clang --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

The stripped 22,112-byte module has SHA-256 `25d311c7e5b359fd90cc5629e3755c69250ac995b4e6a7a10ae2b4f8047276f4`. `llvm-objdump -d` counts 9,465 static instructions. Participant measurement with Wasmtime 50.0.0 and fuel enabled reports exactly 89,747,938 executed operators for exported function `run`. Charging two word operations per fuel unit plus one covers the measured and structural operators:

```text
2 * 89747938 + 1 = 179495877 operations.
```

The organizer does not compile or execute the wasm module. The compiler version, module hash, static instruction count, and fuel count are participant-run setup accounting. The organizer runs the Python mirror and checks the emitted bytes.

The emitter image has 9,465 instructions at 36 bytes, or 340,740 bytes. Its scratch is 77,556 bytes:

```text
use counts                                                   43,836
recent gates                                                    128
CSE keys and values                                           8,192
free and pending register maps                                  256
W array                                                        5,120
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
state subtotal (the preceding 16 rows)                      28,928
addition choices                                                 56
IV, K, PW, PERM, and UCD constants                              640
shadow stack                                                  4,096
total                                                        77,556
```

`experiments/bssha.py` computes the 28,928-byte state and 640-byte constant subtotals from named arrays and compares them with the C report. Complete setup memory is

```text
182579 program bytes + 16384 counters + 28384 registers
+ 2048 recovery arrays + 340740 emitter image + 77556 scratch
= 647691 bytes.
```

Search memory is code 182,579 + counters 16,384 + registers 28,384 + recovery array 2,048 + table 819,180 = 1,048,575 bytes. The count-only searches rebuild each candidate and do not retain DAGs. Their 10,000-instruction image is 360,000 bytes. With 77,556 bytes of builder scratch and 65,536 bytes of trial state, the offset and selector peaks are 503,140 and 503,148 bytes. All phases run sequentially. Search is the overall peak, 1,048,575 bytes (`<= 2^20` bytes).

### 3.7 Preprocessing

No work is free or nonuniform. Final emission plus fixed setup costs 180,309,477 operations. The offset search costs 461,900,436,782,186,496 operations and the selector audit costs 114,560,315,521,236,992. Total preprocessing is 576,460,752,483,732,965 operations, included in N. In target-compression units,

```text
log2(576460752483732965 / 2896) = 47.500154113353176.
```

The claim rounds this upward to `preprocessing_log2 = 47.50016`. There is no nonuniform advice.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bssha.py --loss` (the function `_lossq`); Appendix A recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
when both trails have length <= cr, pass 1 of step 6 records every D-th point of each walk and the terminal lengths l0, l1 <= cr, and pass 2 aligns the longer walk via its checkpoints and binary-searches the floor(min(l0, l1) / D) + 1 checkpoint intervals (at most 16 probes of < D steps) before stepping the two walks together for at most D steps to the first merge pair, found within cr + 17 D batches. The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F because F < 2104 < 2^12 and the low 12 key bits hold F. Equal keys of two DPs can differ only above bit 157. The lanes do not interact.
The stage-1 test loses no event. A 48-bit key match without a merge ends the run; its probability and one recovery are charged.

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B evaluations, N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(35 L), cr = ceil((63/5) L), S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 134236.3871, tmax = 136,267, and CMAX = 7. Let Pi_m = product from i = 0 to m - 1 of (1 - i/N'), PP = Q(Q - 1)/(2N'), and H = (Q(Q - 1)/2 + 2^18 Q)/N'. Let k = 136974 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 263, p = e^(-c/L), and p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)). Let F be uniformly random on 256-bit values and P_F the success probability when every evaluation of g is replaced by lazy sampling from F. Then
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_rec - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = 0.608707951908,
    P_delay = 0.001155974329,
    P_own = 7.396157e-06,
    P_long = 2.195154e-14,
    P_age = 1.126787e-14,
    P_rec = 2 PP e^(-(12.6 L - 1)/L) (1 + (12.6 L - 1) theta / (1 - theta)) = 4.553075e-05,
    P_dist = 3.671576e-06,
    P_cut = 1.473931e-05,
    P_key = C(tmax, 2) / (2^36 Tp) = 6.418245e-05,
    P_table = 5.525191e-07,
    P_tiny = P_start + P_DP-repeat + P_same-batch + P_60 + 2^-90,
    P_start = Q 2^18 / N = 7.676065e-34,
    P_DP-repeat = k^2 L / N' = 4.092651e-34,
    P_same-batch = 255 Q / N' = 7.466876e-37,
    P_60 = exp(-300 + (e^5 - 1) H) = 3.108919e-99.
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
(f) (G5) fails. The first part, a(t) + rho(y) >= cr, is the second part of (d) with cr in place of c: probability at most p2(cr) = e^(-(cr-1)/L) (1 + (cr - 1) theta / (1 - theta)) per pair. The second part, a(y) + rho(y) >= cr: the g(y) coins 0 before y, the coin of y and the rho(y) - 1 coins 0 after it form a run of 0s of length at least cr among coins disjoint and dominated by independent geometric variables, so the probability is again at most p2(cr). At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': 2 PP p2(cr) <= P_rec (cr = ceil(12.6 L), and p2(cr) <= p2(12.6 L)). The union bound runs over all Q (Q - 1) / 2 pairs, so it covers every collision pair, in particular the pair behind the first detected key match, not only the first collision.

Step 5 (the sum). With P(tau <= Q, N1 <= k - 1) >= 1 - Pi_(Q-k+1) - 2^-40 and the failure bounds above (including the recovery-cap failure (f), P_rec), the early halts are charged in Step 6 (eighth cut) and Step 7 (table full, key false match, stage-1 budget, recovery cap).

Step 6 (the cut count and the long trails; no premise). Let K be the number of trails that the run cuts or would cut; the eighth one halts the run because `CMAX = 7`. Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.
(i) K_A. The disjoint-window scan from the credited proof bounds eight fresh cut trails by the upper tail of `Binomial(n2,p)` with `n2 = k + 263` and `p = exp(-c/L)`. Its value is `4.5848e-56`.
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
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; the bound is `Q L / N' = 7.396e-06`.
- X: the same-lane and different-lane geometric-tail calculation gives `E_X = 6.882813e-12`.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^18) / N': E_J2a2 <= (Q + 2^18) L Q (Q - 1) / (2 N'^2). E_J2a = 7.343151e-06.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2 = 1.126787e-14.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 3.129965e-16.
Combining the fresh tail with the same S, X, J2a, J2b, and Y root-event bounds gives `P_cut = 1.473931e-05`. There is no cut-count premise.

Step 7 (the early halts and residual events). The early halts are the eighth cut, table full, key false match, stage-1 budget, or recovery failure.

Table capacity and key matches. Outside `P_60`, fewer than 60 collisions occur. The number of finished trails is then at most `N1 + 59`, so filling `tmax` entries requires `N1 >= tmax - 59`. The Chernoff bound is `P_table = 5.525191e-07`. A false 48-bit key match costs `P_key = 6.418245e-05`, using key space `2^36 * 2104`.

Sixty collisions. At a fresh evaluation t, the collision probability is at most `(t - 1 + 2^18) / N'`. For `w = e^5`, multiplication of the conditional moment bounds gives

```text
E[w^C] <= exp((w - 1) H),
P(C >= 60) <= exp(-300 + (e^5 - 1) H)
             = P_60 = 3.108919e-99.
```

Stage-1 budget. Let `eta_t` mark that the low 20 bits of the independent uniform value `V_t` are zero, and let `mu2 = Q / 2^20 = 323353608835349853515625000000000`. Fresh stage-1 hits are at most `sum eta_t`, which is `Binomial(Q, 2^-20)`. The multiplicative Chernoff bound gives

```text
P(fresh hits > 1.5 mu2) <= exp(-0.108 mu2)
                            = exp(-34922189754217784179687500000000)
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
         = 32543391181156065015249383704.2474926582337...
         > 1000.
```

Appendix A evaluates `A_replay` downward and charges the outward upper bound `P_replay-simple < exp(-1000)`. It also checks

```text
240 M = 21217130954096519396536873341403230960
      <= 339060833738135808000000000000000000000 = Q.
```

Outside the root-event union and the new `P_replay-simple` term, each of the 60 replay windows has at most `2 M / 2^20` hits. Thus the repeated hits are at most `120 M / 2^20 <= mu2 / 2`. Together with at most `1.5 mu2` fresh hits, this is at most `2 mu2`, below `e2max = 2 mu2 + 64`. The residual probability of the stage-1 budget halt is below `P_stage-fresh + P_replay-simple < 2 exp(-1000)`, in addition to `P_60` and the root-event union already charged in `P_cut`.

Recovery and the three small structural events. A recovery without a pair comes from a false key match, already charged by `P_key`, or from one of the fewer than `2^18` starts lying on an evaluated trail. The latter event is `P_start = Q 2^18 / N = 7.676065e-34`. Outside those events, Lemma 1 returns a pair within `cr + 17 D` calls (when both trails have length <= cr; longer colliding trails are charged in `P_rec`). A repeated DP-valued output costs `P_DP-repeat = k^2 L / N' = 4.092651e-34`. A partner in the same batch costs `P_same-batch = 255 Q / N' = 7.466876e-37`.

The outward-rounded certificate gives `P_start + P_DP-repeat + P_same-batch + P_60 < 1.177618e-33`. It adds `P_stage-fresh` and the new `P_replay-simple` term to `residual_actual`; each is below `exp(-1000)`. The total fits inside the charged `2^-90 = 8.077936e-28` reserve. The certificate uses outward rounding for every exponential and rational term, so it needs no probabilistic rounding allowance. This proves the lemma. QED.
Consequently the printed float bound is

```text
1 - 0.608707951908 - 0.001155974329 - 7.396157e-06
  - 2.195154e-14 - 1.126787e-14 - 4.553075e-05
  - 3.671576e-06 - 1.473931e-05 - 2^-40
  - 6.418245e-05 - 5.525191e-07 - P_tiny
= 0.3900000010002327.
```

Appendix A independently certifies `P_F >= 0.390000001000 >= 0.39` with exact rationals and outward-rounded decimals.

Sensitivity is recomputed from the live plan by replacing N with `N/(1-eps)` and reoptimizing Tp and B:

| hazard deficit eps | replacement Tp | extra time bits to restore 0.39 |
| ---: | ---: | ---: |
| 0.01 | 2095 | 0.00725066 |
| 0.05 | 2052 | 0.03700428 |
| 0.10 | 1997 | 0.07592893 |
| 0.25 | 1823 | 0.20745386 |

A collision-hazard surplus helps. No robustness margin is treated as a theorem.

## 5. Premise H1 and its evidence

H1 compares this fixed function with a uniformly random function. Its four clauses are:

- (a) Distinct fresh evaluated inputs have independent uniform outputs and pair-collision hazard `2^-256`.
- (b) Iterates from the starts `r+t` have the first-collision law of a random mapping.
- (c) A fresh output is a DP with probability `2104/2^122`, independently of collision events.
- (d) Under the adaptive program history and later DP flags, a fresh output hits any fixed earlier non-DP output with probability at least `2^-256`.

Lemma 2 proves the bound for the random function. H1 transfers that bound to the fixed target. The circuit, ledger, memory, and random-function theorem are exact claims.

Support of H1 (stated; it is not measured at width 256):

1. H1 is the generic premise of parallel collision search with distinguished points. Paul C. van Oorschot and Michael J. Wiener, "Parallel Collision Search with Cryptanalytic Applications", *Journal of Cryptology* 12(1):1-28, 1999, DOI 10.1007/PL00003816, model a fixed compression function iterated from fresh starts, without a chosen input difference, by a random function. The generic entries of this track use the same premise: mitchuski 3017c952, 1884db5b, and 4684dfc2; lamb356 3642e1cd; dariolina 6b678689; and our 7523902c, 7347a2b6, 60dbf898, 332b47e1, 5ed693e8, and ff37a322.
2. Clause (d) fails in the adverse direction only if `g`, along its own iterates, collides less often than a random function by a constant factor `1 - eps`. Such a property would separate this 40-step function from a random function in a way that no published result shows. This entry chooses no input difference and uses no differential property.
3. A deviation that raises the collision hazard helps. Section 4 prices a deficit exactly: 0.00725066 bit for `eps = 0.01`, 0.03700428 bit for `eps = 0.05`, 0.07592893 bit for `eps = 0.10`, and 0.20745386 bit for `eps = 0.25`.
4. The organizer program checks agree with random-function reference values at their scopes. For `proj-k0-w256`, 256 independent uniform 16-bit projections contain a pair with probability 0.392678 per trial, or 100.53 of 256 trials; the organizer observed 107. The expected number of equal pairs is `C(256,2)/2^16 = 0.498047` per trial, or 127.50 over 256 trials. For the exact seven-batch `plan(16)`, an independent lazy-random-function reference over 10,000,000 complete mappings gave probability 0.6958435 with standard error 0.00014548, or 178.14 successes per 256 trials; the organizer observed 178. The reference simulator assigns a uniform 16-bit output on the first query of each input, then runs the same starts, DP rule, table, and recovery. These are consistency checks that can expose implementation-level deviations. No count is used to change the score.

Limitation: H1 cannot be measured at width 256, so these experiments do not measure the full-width collision hazard or the success probability at `2^128` scale.

## 6. Experiments

Two organizer consistency checks run `experiments/bssha.py`. Before dispatch, `bounded_check` runs the byte-exact mirror of the normative C emitter. The organizer recomputes the complete digest of every returned message pair.
`bssha-n16`: per trial, one attempt of the 256-lane search at width 16 (DP = low 2 bits zero, plan(16): 7 batches, cut rule, table, recovery) on the walk g16(x) = the low 16 bits of the complete digest of M(x), x < 2^16. Each batch runs the shipped program on the 256 planes (the 240 high input planes zero), then the experiment's digest network (`DigestNet`, bit-sliced, experiment code only, not in the ledger) inverts walk B, forms cv1 = IV + state and runs block 2; the recovery runs the rolled recovery program and the same inverse and block 2 in scalar form. The trials run side by side: the planes of trial i occupy bits 256 i to 256 i + 255 of each word, so one pass of the program and of the digest network serves every live trial, and each bitwise record acts on every trial's 256 bits alone. The trial returns M(x), M(y) when the attempt succeeded and two nulls otherwise. Checked event: the messages are distinct and their complete 40-step digests agree in the low 16 bits. This is exact, because at width 16 the walk is those 16 digest bits. The width-16 walk differs from the width-256 walk g only in the map after the program (inverse, block 2, low 16 bits); it runs the same program, search, table and recovery.
`proj-k0-w256`: per trial, 256 points at width 256 (source by trial index mod 3: uniform from the seed, counter r + i, iterates of g from 256 seed-derived starts) evaluated with the shipped program; their complete digests are formed by the digest network; the trial returns two points whose digests agree in the low 16 bits when the set holds such a pair. Checked event: as above. It checks at full width the program, the inverse of walk B, the chaining value, block 2 and the message construction.
The experiments check execution, witnesses, and agreement with the scope-matched reference values in Section 5. Their counts do not enter the cost or success bound.

## 7. Memory

Table: 136,530 slots * 48 bits = 819,180 bytes. Slot t belongs to trail t and stores `key + 1`; zero is empty. The maximum key is 281,474,976,708,663, so the sentinel transform fits.
Code: 43,541 body instructions * 4 bytes = 174,164 bytes. The 404 recovery records use 2,020 bytes. The other 1,279 fixed 5-byte instructions use 6,395 bytes. Total code is 182,579 bytes.
Counters and copies use 16,384 bytes. The 887 registers use 28,384 bytes. The 64-word recovery array uses 2,048 bytes. No advice. Memory peak is `max(647691,1048575) = 1048575` bytes, below `2^20`.
The table size is the largest that fits: `floor(8 * (2^20 - 182579 - 28384 - 16384 - 2048) / 48) - 263 = 136267`. Appendix A derives Tp = 2104 and certifies `P_F >= 0.39`.

## 8. Heuristics, conventions and what is credited

The premise is H1. The 887-register file and native formats are declared machine prices, not statistical premises. Lemma 2 proves the cut count. There is no advice.

Direct dependencies include f7b1dea4-2883-45d6-9c0c-89a5d4ad1b1a for the 404-record recovery compaction, fb8a3bce-1839-4b9a-ab67-76670b4a05c9 for the baseline package, b3f10279-3fa4-4d7b-9011-3faa2ae352c8 for the fused kernel, schedule, allocator, and recovery design, and ff37a322-c5e7-4656-bb89-02f1a5d0e213 for the native-4-byte machine and accounting base. `package-v2-work/dependencies.json` lists the complete same-challenge lineage and the evidence used from each entry. The checkpoint recovery resolution (Step 6, the recovery charge of Section 3.3, the loss term P_rec of Lemma 2 Step 4 (f), RECOVERY_CODE = 94, and the Appendix A checkpoint accounting) is ported from Jbenisek's round-55 entry 93618c27-3783-4744-904a-5d688ff610f8 and round-63 entry a74a20c8-3a52-4742-8970-e20dc0ad8b76 (and akki-rock05's round-64 entry 068ba228-dd60-437d-b36d-6773fec1a7be); this entry combines checkpoint recovery with the 863-data-register bit-interleaved schedule/allocator kernel (c83bda97-88bb-4125-b581-5b76c6c7de6a) and re-optimizes the age/recovery caps (KAPPA_256 = 35, KR = 63/5) and discrete Tp selection.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate, and `certify` recomputes the bound of Lemma 2 in exact rationals and 60-digit decimals with outward rounding: the line `P_lower certified` is a proved lower bound on P_F, asserted >= 0.39. The same numbers come from `python3 bssha.py --ledger`.

```python
from fractions import Fraction
CK = 1
KR = Fraction(63, 5)
REC1 = REC2 = 39
CHK, PROBE, RECFIX = 80, 100, 600
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 43541, 21, 3, 256
INSTR_REC = 43541
PH7, EXTRA, RECINIT = 1393, 39, 76
N_BITS, S1, W, KAPPA = 256, 20, 102, 35         # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE = 2800, 3800, 4200, 1300
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 7
CUT_HALT_ORDER = CMAX + 1
assert CUT_HALT_ORDER == 8
WASM_RUN_OPERATORS, WASM_OPERATOR_FACTOR = 89747938, 2
BODYB, CTRLB, RECB, REC_RECORDS = 4, 5, 5, 404
CONTROL, REGFILE, COUNTERS, ADVICE, ARRAYS = 1208 + 47 * CK, 28384, 16384, 0, 2048
KEYB = SLOTB = 48                              # key+1; zero is the unwritten sentinel
SEARCH_EVAL_OPS = 1 << 48
OFFSET_SEARCH = 1641 * SEARCH_EVAL_OPS            # 64 endpoint + 1 initial + 3 * 192 coordinate + 1000 perturbation builds
SELECTOR_SEARCH = 407 * SEARCH_EVAL_OPS
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 21, 18                        # B is a multiple of GRAIN; trail numbers are below 2^18
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP
code_bytes = INSTR_REC * BODYB + REC_RECORDS * RECB + (FILT + LOOP + CONTROL) * CTRLB
tmax = 8 * ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE - ARRAYS) // SLOTB - LANES - CMAX  # stored trails: one slot per trail number (LANES starts + tmax + CMAX cuts)
table_bytes = -(-(tmax + LANES + CMAX) * SLOTB // 8)
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
rows = [("main loop: B * %d" % body, body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished events: (tmax + 1) * (3800 + 6 * (tmax + 263))", (tmax + 1) * (EVENT + 6 * (tmax + LANES + CMAX))),
        ("cut trails: 7 * 4200", CMAX * CUTOPS),
        ("recovery", (cr * (PH7 + REC1) + KCHK * CHK + 17 * DCK * (PH7 + REC2) + 16 * PROBE + RECFIX + RECINIT) if CK else 2 * capr * (PH7 + EXTRA) + 600 + RECINIT),
        ("setup and generator", SETUP_FIXED + emitter),
        ("charged offset search", OFFSET_SEARCH),
        ("charged selector search", SELECTOR_SEARCH)]
N = int(sum(v for _, v in rows))
assert N == 57747387988117957968284748330063459455061
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
Tp = 2105  tmax = 136267  B = 1324456381789593000000000000000000000  e2max = 646707217670699707031250000000064  c = 88404712308735497485288830612469473
memory bytes = 1048575
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000001000
residual P_start          7.67606524632994687954373786809930176459154889989850800471409E-34
residual P_DP-repeat      4.09265143324347487691597427533014135661367593952941427894909E-34
residual P_same-batch     7.46687560201315480912648451372269716231114114659258824082144E-37
residual P_60             3.10891940807559829967311186605242458872380939492880202710441E-99
residual fresh exponent   34922189754217784179687500000000
residual replay exponent  32543391181156065015249383704.2474926582337799871706080936417
residual P_stage-fresh    5.07595889754945676529180947957433691930610687878259230750892E-435
residual P_replay-simple  5.07595889754945676529180947957433691930610687878259230750892E-435
residual residual actual  1.17761835551754349112688386279431658183675359805745148719040E-33
residual 2^-90 reserve    8.07793566946316088741610050849573099185363389551639556884766E-28
residual reserve slack    8.07792389327960571198118923965710304868781552798041499433279E-28
residual P_tiny charged   8.07794744564671606285101177733435893501945226305237614336253E-28
main loop: B * 43565                                 57699942272663619045000000000000000000000
slice checks: ceil(B / 2^48) * 1300                  6117038595926057453767100
stage-1 hits: e2max * 2800                           1810780209477959179687500000000179200
finished events: (tmax + 1) * (3800 + 6 * (tmax + 263)) 112145838640
cut trails: 7 * 4200                                 29400
recovery                                             45634935244854847065888443141375907756
setup and generator                                  180309477
charged offset search                                461900436782186496
charged selector search                              114560315521236992
N = 57747387988117957968284748330063459455061
certificate: 2^12390703 * 2896^100000 <= N^100000 < 2^12390704 * 2896^100000
log2(N/C) = 123.9070336009
time_log2 = 123.90704
```
