# sha256-r53: a 66,453-instruction native bit-sliced birthday walk

This package ports the round-40 package 27984c2d-fc4b-4285-a430-c5f364c10a7e (lineage f7b1dea4, fb8a3bce, b3f10279, ff37a322) to the 53-step target `sha256-r53-prefix-v1`, in the same way as the round-64 and round-52 ports 1f18d544-cd04-4177-8739-fad19d55a98a and 26d9ad0b-e6f1-4370-abb4-b36aa97ab9e6 (mpjunior92), whose program this package instantiates at round 53. That lineage's fused round kernel, `_adduc` constant folding, four-word carry fusion, `_ch3` tail and polarity-sheared walk-B encoding had not been applied to round 53; the current best round-53 entry 8436c1e7 (time_log2 124.06965) uses a 66,926-record kernel with 5-byte records. At 53 steps the ported kernel has 52,207 XOR, 8,662 AND, and 5,584 OR native instructions, or 66,453 total. The implementation keeps both generators: the bounded Python generator and the freestanding C emitter build the same network, and the self-test requires byte equality, scalar equivalence, chained-walk equivalence, zero moves, recovery equivalence, and complete two-block digest agreement.

What changed relative to 26d9ad0b is round-specific data plus one structural change in the rolled recovery program. `ROUNDS = 53` and `UNIT = C = 3988`; the round-constant table has the first 53 SHA-256 constants; the C emitter's `RND` is 53 and its schedule array has 53 words; the addition-choice table has one all-zero entry for each of the 79 nonconstant `addm` sites; the two per-bit tail shear masks were re-chosen for round 53 (`QM = 0x827d8f1f`, `XM = 0x00f4e657`, Section 1.1); the register file has 907 data registers. The recovery loop runs four rounds per iteration and covers rounds 10 to ROUNDS - 7; at round 53 that is 37 rounds, not a multiple of four, so the per-call program first runs round 10 and the schedule word W16 unrolled and then runs the unchanged loop body nine times from memory offset 1 (Section 3.3). The digest-network guard in `Gen._baseline` (taken only when the absorbed constant is zero) is kept from 26d9ad0b; every kernel four-variable sum has zero constant, so the emitted body is unaffected (Section 6). The per-call recovery charge is itemized (Section 3.3), including the re-set of the registers a call overwrites.

The native body instruction remains exactly 32 bits: a 2-bit opcode and three 10-bit register fields. The machine executes it directly for one word operation. No decoder or interpreter runs in the priced path. The body occupies 265,812 bytes. Control and recovery use native fixed 5-byte instructions.

The six-offset search evaluates 1,641 complete builds. The ledger reserves one baseline and two passes over all 343 alternatives in the 79-site reduction inventory, or 687 complete builds. Every build is charged at `2^48` operations. The emitted selector is the all-zero baseline, so no unrecorded selector result affects the circuit. The final plan uses 120,698 completed trails in 120,961 48-bit sentinel slots. Search memory is 1,048,572 bytes.

The exact ledger is

```
N = 88231920371180619547889294928080393029695 word operations
log2(N / 3988) = 124.056974786698
```

The claim rounds upward to `time_log2 = 124.05698`, which is 0.01267 bit below the current best round-53 claim 124.06965 (8436c1e7). Setup memory is 740,623 bytes. H1, the fixed-function random-function comparison stated in Sections 4 and 5, is the only score-critical premise. Circuit changes, counts, and memory bounds are exact checked claims, not premises.

## 1. Target and relation

Target `sha256-r53-prefix-v1` (the Pareto lane `sha256`, round 53; the first 53 of the 64 SHA-256 steps on every block). The two colliding messages have 64 bytes each. With x a 256-bit integer and y0..y7 its eight 32-bit words (big-endian, y0 the highest), M(x) is the 16 big-endian words W0..W15 with
- W0..W7 = the constant words 3e73281c, 752d8ed2, ad19eff1, 7250fceb, d4095422, 44fdb519, 43f22c5b, d8d6aac4 (computed from the standard IV by `_anchor_prefix` so that the eight new a-words of steps 0..7 are K9 - K8, -K9, 0, 0, 0, 0, 0, 0; the working state after step 7 is therefore (a,b,c,d,e,f,g,h) = (0, 0, 0, 0, 0, 0, -K9, K9 - K8), which makes steps 8 and 9 cheap),
- W8 = y0, W9 = y1, and W(8+k) = y_k - K(8+k) modulo 2^32 for k = 2..7.
FIPS 180-4 padding appends 0x80, 55 zero bytes and the 64-bit length 512: the padded message is 128 bytes, two blocks, and block 2 is the same for every x. The target runs the steps 0 to 52 on each block, block 1 from the standard IV and block 2 from the chaining value cv1 = IV + s(x) word by word, where s(x) is the working state after step 52 of block 1; the digest is the result of block 2 with its feed-forward (`verifier/hash_functions.py:digest(M(x), "sha256", 53)`). The profile's message domain is "finite byte strings of bit length below 2^64"; a 64-byte string is in it.
Write a_i, e_i for the a and e words after i steps of block 1 (a_0, e_0 from the IV), T1_i for the T1 of the step that produces them and W_j for the schedule word of step j. With the fixed 32-bit polarity masks `QM = 0x827d8f1f` and `XM = 0x00f4e657`, f(x) is walk B (4684dfc2) with per-bit polarity-matched disjoint-support shears on Q and X. Define the eight words bw = [e_50, e_51, a_46, a_47, Q, T1_49, X, Y] with X = e_48 + Ch(e_51, XM, e_49) + W_51 (at bit j: `e_51[j] | e_49[j]` when `(XM >> j) & 1 == 1` and `~e_51[j] & e_49[j]` when `(XM >> j) & 1 == 0`; since `Ch(e2, e3, e4) = Ch(e2, XM, e4) + (e2 & e3 & ~XM) - (e2 & ~e3 & XM) mod 2^32`, the inverse adds `(e2 & e3 & ~XM) - (e2 & ~e3 & XM)`), Q = T1_48 + Ch(a_47 ^ a_46, a_45, QM) (at bit j: `~(a_47[j] ^ a_46[j]) | a_45[j]` when `(QM >> j) & 1 == 1` and `(a_47[j] ^ a_46[j]) & a_45[j]` when `(QM >> j) & 1 == 0`; since `Maj(a6, a7, a8) = Ch(a6 ^ a7, a8, QM) + (a6 & a7 & ~QM) - (~a6 & ~a7 & QM) mod 2^32`, the inverse adds `(a6 & a7 & ~QM) - (~a6 & ~a7 & QM)`), and Y = e_49 + W_52. Then f(x) is the 256-bit integer whose eight 32-bit words, most significant first, are bw[6], bw[1], bw[7], bw[0], bw[5], bw[4], bw[2], bw[3] = X, e_51, Y, e_50, T1_49, Q, a_46, a_47 (the permutation PERM = (6, 1, 7, 0, 5, 4, 2, 3), the order with no register move, Section 3.2; `enc_words`, `words_of` and `int_of` in the program). In particular the low 32 bits of f(x), which hold the distinguished-point test bits of Section 2, are a_47, and the next word up is a_46. In the program these are bw = [E[r-3], E[r-2], A[r-7], A[r-6], ..., T[r-4], ...] with r = 53. These words determine s(x): the program's `enc_invert` recovers a_48 = Q + (a_47 & a_46 & ~QM) - (~a_47 & ~a_46 & QM) + Sigma0(a_47), then a_49, a_50, a_51, the T1 values of the 0-based steps 51 (= X + (e_51 & e_50 & ~XM) - (e_51 & ~e_50 & XM) + Sigma1(e_51) + K_51) and 52 and the whole state, by additions, subtractions and the round functions. The walk is g(x) = f(x) XOR q, q the fixed 256-bit mask `be24390accbe9b61e95138fe5511b644b3c993ab0dea46d6c217239f3f81439e` (129 output planes that the generator leaves complemented instead of spending a NOT).
So g(x) = g(y) gives s(x) = s(y), hence the same cv1, the same block 2 and equal digests. x != y gives M(x) != M(y), since x -> W8..W15 is a bijection. The attack outputs two distinct 64-byte messages with equal complete 256-bit digests.
The selftest (`python3 bssha.py --selftest`) compares the program with scalar g on 2,560 lanes, including all-zero and all-one inputs, checks four chained steps, checks the inverse on 10,000 random states, checks the recovery program and experiment digest network, and runs six width-16 search attempts. It also runs the independent ordinary builder and requires byte equality with the normative bounded emitter.

### 1.1 Choice of the tail shear masks

`QM` and `XM` only choose, bit by bit, which of two disjoint-support forms of Maj and Ch enters the encoded words Q and X; `enc_invert` adds back the exact difference, so every choice gives a bijective encoding of the same state and the same collision relation. For round 53 they were re-chosen by the same sequential single-bit pass as in 26d9ad0b (mask bits QM 0..31 then XM 0..31, a flip kept only when the kernel instruction count strictly decreases, at most two passes), starting from the round-52 values `QM = 0xbe79bcfb`, `XM = 0x3b6d8189`: 66,486 instructions with the starting masks, 66,453 with the shipped masks (33 flips in the first pass, none in the second; 129 count-only builds). This is a participant-side choice of two constants of the walk; its cost is covered by the charged envelopes of Section 3.2 at `2^48` operations per build, and no claim depends on its optimality.

## 2. The attack (program `experiments/bssha.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished when its low 20 bits are zero and the 102-bit number F = (x >> 20) mod 2^102 is below Tp = 1862. Thus D = 122, theta = 1862 / 2^122, and L = 2658455991569831745807614120560689152 / 931 = 2^111.13736. The key is the 37 bits of x above bit 121 followed by the 11-bit encoding of F. It has 48 bits; F < 1862 < 2^11.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated program of Section 3.2. The start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 20 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask, the lane is extracted and the window test F < Tp decides whether it is a DP. If `key + 1` is in the table, go to step 6. Otherwise write `key + 1` into 48-bit slot t and start the next trail in that lane. Zero is the unwritten sentinel. The slot position is t, so neither t nor the length is stored.
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = ceil(13 L) batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 120,698 keys, when an eighth trail would be cut (`CMAX = 7`), or if step 6 finds no pair.
6. Recovery. Pass 1 recomputes the stored trail length. The two trails are aligned, then stepped together until their next values agree. The first predecessor pair a != b with g(a) = g(b) is returned. The rolled two-lane program has 490 fixed 5-byte records in total, of which 102 are one-time initialization records, and executes 2,092 records per call. Each pass runs at most capr = c + S calls.
Constants printed by `--ledger`: Tp = 1862, L = 2658455991569831745807614120560689152 / 931, B = 1324786413462774000000000000000000000, Q = 339145321846470144000000000000000000000, e2max = 646868365948620117187500000000064, c = 37121297411823644141244880308581052, capr = 37121297411823644141526355285291708, and tmax = 120,698. The 120,961 total slots cover 256 initial trails, all stored trails, and seven cut trails. The maximum trail number is 120,960 < 2^18; the boundary test asserts it.
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is a constant of the program).

## 3. Operation ledger

### 3.1 Machine
Machine model of this entry (declared cost-model prices). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices operations and memory; it gives no register count and no instruction size. For round 53 the organizer contract sets `reference_operation_cost = 3988` (`python3 scripts/pareto_candidate.py --family sha256 --rounds 53 --show-contract`).
This entry declares a load/store machine with 256-bit words and 910 registers, 907 data registers and three pointer registers. Charged, one operation each: every XOR, AND, OR and NOT of a 256-bit register, every register move, every set of a register to a constant, every load and store, every pointer addition, comparison and conditional branch, and the one random word. Nothing is free except renaming a bit-sliced rotation.
The body uses this machine's native fixed 32-bit instruction: a 2-bit opcode and three 10-bit register fields. Opcode values 0, 1, and 2 mean XOR, AND, and OR; 3 is reserved. The machine fetches and executes each instruction directly for one operation. There is no decoder or interpreter in the priced path. `Prog.run`, `Prog.compile`, and `Prog.fast` are test mirrors only. All 66,453 kernel instructions use the native format, so the body occupies 265,812 bytes. Recovery and control use native fixed 40-bit instructions. Every executed instruction costs one word operation.

### 3.2 One batch = 66,478 operations for 256 trails
Representation is bit-sliced: one 256-bit machine word holds one bit position for 256 trails, and a SHA-256 rotation only renames planes. Signals carry a node and a free polarity bit. The pivot full adder costs five gates. `add3` carries the pair `(u,U)`, representing `1 if U else 2u`; its T0, T1, and T2 templates cost nine gates per ordinary column and eight at bit 30. The self-test exhausts all 32 input rows for each template relation.

The round fusion passes `h[0]` and `u[0] = h[0] XOR Ch[0]` into `add3`. Bit 0 combines the half-adder on the other two operands with the `h + Ch` carry in seven gates for either absorbed carry. At bit 1, `_add_u` begins from a carry-free root and may use the alternate `ch1 = f1 XOR (~e1 AND (f1 XOR g1))` form when its stored polarity avoids a penalty, while `_adduc` folds the round constant into `h + u` across suffix columns `m..31` using the 96-word `UCD` template table. The selector absorbs `c0 + 2c1 + delta` into the folded constant, and splits `W[16]` and `W[23]` into carry-saved sums plus deferred constants across steps 19..24. These are exact rearrangements of `h + Ch + Sigma1 + K + W` and are checked against scalar SHA-256.

For every four-variable sum with zero absorbed constant, `addm` orders `(A,B,D,C)`, computes `add3(A,B,C)` with the bit-0 half-adder carry `D0`, and then adds `[0,D1..D31]`. The outgoing bit-0 carry occupies the otherwise unused pair-carry slot at bit 1, so the second adder's bit 1 is a two-gate half adder. At round 53 there are 28 such sums (the 15 of round 40 plus the schedule words W38 to W50; at round 53, W51 and W52 are three-operand sums because their `sigma1` terms are deferred into X and Y).

The walk-B tail uses the per-bit shears `QM = 0x827d8f1f` and `XM = 0x00f4e657`. `_ch3` fuses `B + Ch` into the first `add3`: each column forms `w5 = hg XOR (e AND (f XOR g))` and selects a polarity-matched multiset of `[W,a,Sigma1(e)]`. Its column relation is exhaustively checked. `enc_invert` applies the matching Q and X corrections, so equal walk values imply equal block-1 states and complete digests. The tail also defers the `sigma1` terms of W_51 and W_52 into X and Y (W_51 and W_52 are formed only as `W(i-16) + sigma0(W(i-15)) + W(i-7)`), which is exact because X and Y are the only consumers of W_51 and W_52.

The schedule advances `W[21]` and `s23_raw` to step 19, defers the constant adders for `W[22]` and `W[23]` until after their rounds, and advances `W[32]` to step 31. The streaming allocator routes short-lived nodes into idle output targets and otherwise takes a dying operand or the lowest free non-target register. The output permutation `(6,1,7,0,5,4,2,3)` needs zero moves. With 907 data registers the shipped allocator emits zero moves; 907 is the smallest count with that property in a scan of 880 through 1,000 data registers, and the register file is priced at that size.

The six offsets are preprocessing output. Their deterministic search evaluates exactly 1,641 complete candidates: 64 endpoint placements, one initial coordinate point, three complete sweeps of 192 bits, and 1,000 perturbations from the fixed xorshift seed `6a09e667bb67ae85`. Bits are visited by increasing word and then increasing bit. A strict improvement replaces the incumbent, so ties retain the earlier candidate. The shipped offsets are those of 27984c2d (`W(8+k) = y_k - K(8+k)`); the 1,641-build envelope is charged as an upper bound on offset-selection work and is not claimed to reproduce them. All other count-only work done for round 53 is covered by the two charged envelopes (1,641 + 687 = 2,328 builds at `2^48` each): a second single-bit mask pass from the round-64 values (129 builds), the shipped mask pass of Section 1.1 (129 builds), the register-count scan (121 allocator runs, 880 through 1,000 data registers) and a few dimension probes, together fewer than 1,000 builds. The addition-choice selector is the all-zero baseline of 26d9ad0b; no selector search was run for round 53.

The addition audit is also charged preprocessing. Among 79 nonconstant `addm` sites, 41 have exactly three operands (34 three-variable sums and 7 two-variable sums with a constant) and admit one three-of-three reduction. 30 have four operands (28 four-variable sums and 2 three-variable sums with a constant) and admit four three-of-four reductions plus six unordered pair-first reductions; the two with a constant also admit the constant-carry form. The remaining eight sites have fewer than three operands. One complete pass therefore has

```text
41 + 30 * 10 + 2 = 343 alternatives.
```

The charged validation envelope contains the deterministic fused baseline and all 343 alternatives in two complete passes. The candidate does not depend on an unshipped winning alternative: its emitted hint table is the all-zero baseline. The envelope is `1 + 2 * 343 = 687` complete builds.

Both searches use a count-only builder with an eight-probe CSE table and an eight-entry recent-gate ring. One complete build has at most two builder passes, 160 multiword sums, 64 first-triple masks per sum, 32 columns, 13 current-column forms, 13 lookahead forms, and 12 trial gates per form. Charging 1,024 word operations for each trial gate, including lookup, rollback, and bookkeeping, gives

```text
2 * 160 * 64 * 32 * 13 * 13 * 12 * 1024
= 1,360,967,761,920 < 2^41 operations.
```

One more copy covers the rest of the network, scoring, comparisons, loop control, and deterministic candidate generation. The round-53 build has 79 multiword sums, below the 160 of the envelope, and the bounded emitter performs 263,248 helper calls for both passes together. The package charges `2^48` operations per complete build, more than 100 times that doubled structural bound (2^48 / (2 * 1,360,967,761,920) = 103.4). The exact search charges are

```text
offsets:  1641 * 2^48 = 461900436782186496 operations
selector:  687 * 2^48 = 193373309000220672 operations.
```

These bounds follow the loops and fixed array limits. They do not rely on a development call counter or an unshipped trace.

Executed per batch: 52,207 XOR + 8,662 AND + 5,584 OR = 66,453 gates; zero NOT, set, move, load, store, or control instructions. Per lane evaluation (one evaluation of g in one lane) this is 259.582 operations.
Validation is by the bounded emitter, its stream hash, the independent builder comparison, the exhaustive algebraic checks inherited from the frontier, and the scalar and end-to-end tests described in Sections 1 and 6.
The generator runs once at the start; its work is charged in the setup row (3.3), its code and peak storage in Sections 3.6 and 7.

### 3.3 Loop, stage 1, handlers and the other events
One batch: 66,453 body instructions + stage-1 test 22 + loop control 3 = 66,478 operations. Stage 1 uses 19 ORs, one NOT, one comparison, and one branch. A DP has all 20 low bits zero, so its lane is flagged.
Loop control of the batch loop: counter increment, compare with the next slice limit, branch back: 3 operations.
Handlers are charged per event at the stated operation bounds and stored as fixed 5-byte control records:
- Stage-1 hit: store the 256 planes to an 8 KiB copy (256 stores), extract the lane (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (at most 15), counters. Below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail: key formation, sentinel encoding, the slot write, the new start, insertion of its 256 bits, reload of the planes, lane arrays, and counters fit below 3,800 operations. The key scan is charged six operations per slot, including extraction, comparison, and branch. The source increments the counter and scans before its `finished > tmax` halt, so the ledger charges `tmax + 1` handled events. At most `tmax` keys are stored.
- Slice check (every 2^48 batches): charged **1,300** each. Cut trail: charged **4,200**; at most 7 cut trails (`CMAX = 7`).
- Recovery program (`RecProg`): a second program evaluates g for two chain values at once, in bits 0..31 and 128..159 of each word. The message and constant array has 90 words (53 schedule words and the 37 constants K10..K46 of the rounds before the tail), or 2,880 bytes. Preloaded tail constants and masks remove repeated setup; the preloaded offsets and the state registers that a call overwrites are re-set before each call and charged in the recovery batch below. The loop body (four rounds and four schedule words per iteration, with the live-register permutation of 26d9ad0b) needs a multiple of four rounds; at round 53 the rounds before the tail are 10..46, 37 rounds. The per-call program therefore runs round 10 unrolled with the same round code, forms W16 = W0 + sigma0(W1) + W9 + sigma1(W14) and the next partial sum W1 + W10, shifts the six schedule registers by one word (six register copies), and then runs the unchanged loop body nine times with its memory pointer starting at 1 (rounds 11..46, schedule words W17..W52). The one-round renaming of the state registers is undone at the end of the tail by two register copies (a_47 and a_46 back to the input registers). There are 490 fixed 5-byte records in total (102 one-time initialization records and 388 records of the per-call program) and 2,092 executed records per call. The self-test compares this program with scalar g.
- Recovery batch: one call (2,092 records) plus at most 76 surrounding operations, or 2,168 operations per batch, the same in both passes. The 76 are itemized as: 10 re-sets of registers whose start value the call reads and that a call overwrites (registers 5, 6, 10, 11, 12 hold the offsets `-K10..-K14`, register 30 holds `W0`, and registers 3, 4, 7, 8 must start at zero; the participant found this set by perturbing every non-input register before a call, and checked at round 53 that perturbing any other register leaves the output unchanged (the eight it reads are preloaded constants that no call overwrites) and that five consecutive calls with exactly these ten re-sets reproduce scalar g), 8 copies saving the predecessor pair, 34 for the two-lane equality test (per word: shift by 128, XOR, mask, OR-accumulate; then compare and branch), 18 for the pass-1 DP test (mask, compare, branch, window test of at most 15), 3 for counter increment, cap comparison and branch, and 3 spare. Every call is charged all 76 regardless of pass.
- Setup and emitter: fixed work is 813,600. Section 3.6 gives the participant-measured 125,714,851 wasm operators. Charging two word operations per measured operator plus one gives `813600 + 2 * 125714851 + 1 = 252243303` operations.
Code size: 265,812 bytes of body instructions, 2,450 bytes for 490 recovery instructions, and 6,160 bytes for the other 1,232 control instructions. Total code is 274,422 bytes.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 66,478 | 88,069,151,194,178,289,972,000,000,000,000,000,000,000 |
| slice checks: ceil(B / 2^48) * 1,300 | 6,118,562,856,377,729,275,437,400 |
| stage-1 hits: e2max * 2,800 | 1,811,231,424,656,136,328,125,000,000,000,179,200 |
| finished events: 120,699 * (3,800 + 6 * 120,961) | 88,057,886,634 |
| cut trails: 7 * 4,200 | 29,400 |
| recovery: 2 (c + 2^48) * (2,092 + 76) + 600 + 102 | 160,957,945,577,667,320,997,658,276,517,024,846,590 |
| setup and generator | 252,243,303 |
| charged offset search | 461,900,436,782,186,496 |
| charged selector search | 193,373,309,000,220,672 |
N = 88,231,920,371,180,619,547,889,294,928,080,393,029,695 operations.
N / 3988 has log2 124.056974786698. Claim `time_log2` = 124.05698, rounded upward. The walk never computes block 2: equal block-1 states give equal digests, so one evaluation of g is one block-1 compression of 53 steps, priced by its instructions.

### 3.5 Register file and smaller files
Declared prices: the machine has 910 registers of 256 bits: 907 data registers (Section 3.2) and three pointers. The register file is counted as 29,120 bytes.

### 3.6 Bounded emitter and peak setup storage

The freestanding C source embedded in `experiments/bssha.py` as `GEN_C` is the normative setup implementation. `python3 experiments/bssha.py --gen-c` prints its exact 25,723 bytes. Its SHA-256 is `7922a70b7ec73e8449c25f364fd1aca40ae306436fb4376cff0230f0ad1ebc73`. Pass 0 counts uses and output nodes. Pass 1 rebuilds the same network, allocates registers online, and writes native 32-bit instructions directly to the final code buffer. The emitter enforces `MAX_NODES = 66,710`, `MAX_RECORDS = 66,453`, 907 data registers, a 1,024-slot CSE table, at most 900 occupied slots, and every packed-field bound.

The C emitter reports the 15-field tuple

```text
(records=66453, registers=907, nodes=66710, calls=263248,
 moves=0, error=0, XOR=52207, AND=8662, OR=5584,
 code=265812, counters=16384, uses=66710, state=30592,
 choices=79, constants=692).
```

The emitted byte stream has SHA-256 `26a8521266d3aad460c5a54a496e549b343785467bb3dec0ecdc581d4964452a`. Its polarity mask is `be24390accbe9b61e95138fe5511b644b3c993ab0dea46d6c217239f3f81439e`. Before every experiment, the organizer-run Python mirror checks all 15 fields, the C source hash, stream hash, polarity mask, and equality with the independent builder. The participant also compiled `GEN_C` natively with gcc 15.2.0 against a small driver that calls `run()` and writes the code buffer: it reported the same 15 fields and polarity mask and wrote the byte stream with the SHA-256 above.

The participant compiled `GEN_C` with wasi-sdk 34 (clang 23.1.0-rc3 and its wasm-ld) using the flags of 26d9ad0b:

```sh
clang --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

The stripped 20,695-byte module has SHA-256 `36131126f5bf93ec8e59b71673dffbf6bb1310e97cd6b120ae04be6a0d9a9a96`. `llvm-objdump -d` counts 8,768 static instructions. Participant measurement with the Wasmtime Python runtime 49.0.0 and fuel enabled reports exactly 125,714,851 fuel units consumed by exported function `run` (initial minus remaining fuel); the module reported the same 15 fields, polarity mask and stream hash as the Python mirror. Charging two word operations per fuel unit plus one covers the measured and structural operators:

```text
2 * 125714851 + 1 = 251429703 operations.
```

The organizer does not compile or execute the wasm module. The compiler version, module hash, static instruction count, and fuel count are participant-run setup accounting. The organizer runs the Python mirror and checks the emitted bytes. The setup row is negligible: any bound below 2^100 operations would leave the claimed `time_log2` unchanged.

The emitter image has 8,768 instructions at 36 bytes, or 315,648 bytes. Its scratch is 102,169 bytes:

```text
use counts                                                   66,710
recent gates                                                    128
CSE keys and values                                           8,192
free and pending register maps                                  256
W array (53 words)                                            6,784
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
state subtotal (the preceding 16 rows)                       30,592
addition choices                                                 79
IV, K, PW, PERM, and UCD constants                              692
shadow stack                                                  4,096
total                                                       102,169
```

`experiments/bssha.py` computes the 30,592-byte state and 692-byte constant subtotals from named arrays and compares them with the C report. Complete setup memory is

```text
274422 program bytes + 16384 counters + 29120 registers
+ 2880 recovery arrays + 315648 emitter image + 102169 scratch
= 740623 bytes.
```

Search memory is code 274,422 + counters 16,384 + registers 29,120 + recovery array 2,880 + table 725,766 = 1,048,572 bytes. The count-only searches rebuild each candidate and do not retain DAGs. Their 10,000-instruction image is 360,000 bytes. With 102,169 bytes of builder scratch and 65,536 bytes of trial state, the offset and selector peaks are 527,753 and 527,784 bytes (the parts above plus 48 bytes of offset-search words and the 79-byte selector table, respectively). All phases run sequentially. Search is the overall peak, 1,048,572 bytes (`<= 2^20` bytes).

### 3.7 Preprocessing

No work is free or nonuniform. Final emission plus fixed setup costs 252,243,303 operations. The offset search costs 461,900,436,782,186,496 operations and the selector audit costs 193,373,309,000,220,672. Total preprocessing is 655,273,746,034,650,471 operations, included in N. In target-compression units,

```text
log2(655273746034650471 / 3988) = 47.22342564906544.
```

The claim rounds this upward to `preprocessing_log2 = 47.22343`. There is no nonuniform advice.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bssha.py --loss` (the function `_lossq`); Appendix A recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
pass 1 of step 6 recomputes the two lengths and pass 2 aligns and walks them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F because F < 1862 < 2^11 and the low 11 key bits hold F. Equal keys of two DPs can differ only above bit 158. The lanes do not interact.
The stage-1 test loses no event. A 48-bit key match without a merge ends the run; its probability and one recovery are charged.

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B evaluations, N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(13 L), S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 118769.8031, tmax = 120,698, and CMAX = 7. Let Pi_m = product from i = 0 to m - 1 of (1 - i/N'), PP = Q(Q - 1)/(2N'), and H = (Q(Q - 1)/2 + 2^18 Q)/N'. Let k = 121346 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 263, p = e^(-c/L), and p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)). Let F be uniformly random on 256-bit values and P_F the success probability when every evaluation of g is replaced by lazy sampling from F. Then
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = 0.608557359293 (the no-useful-collision term shift * Pi_Q of Step 2, shift = 1/(1 - kQ/N')),
    P_delay = 0.001306833249,
    P_own = 8.363474e-06,
    P_long = 2.925122e-05,
    P_age = 1.571674e-05,
    P_dist = 4.153838e-06,
    P_cut = 4.941650e-05,
    P_key = C(tmax, 2) / (2^37 Tp) = 2.846276e-05,
    P_table = 4.419219e-07,
    P_tiny = P_start + P_DP-repeat + P_same-batch + P_60 + 2^-90,
    P_start = Q 2^18 / N = 7.677978e-34,
    P_DP-repeat = k^2 L / N' = 3.631214e-34,
    P_same-batch = 255 Q / N' = 7.468736e-37,
    P_60 = exp(-300 + (e^5 - 1) H) = 3.224408e-99.
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
(i) K_A. The disjoint-window scan from the credited proof bounds eight fresh cut trails by the upper tail of `Binomial(n2,p)` with `n2 = k + 263` and `p = exp(-c/L)`. Its value is `6.3319e-10`.
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
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; the bound is `Q L / N' = 8.363e-06`.
- X: the same-lane and different-lane geometric-tail calculation gives `E_X = 1.590535e-05`.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^18) / N': E_J2a2 <= (Q + 2^18) L Q (Q - 1) / (2 N'^2). E_J2a = 8.307675e-06.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2 = 1.571674e-05.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 1.122624e-06.
Combining the fresh tail with the same S, X, J2a, J2b, and Y root-event bounds gives `P_cut = 4.941650e-05`. There is no cut-count premise.

Step 7 (the early halts and residual events). The early halts are the eighth cut, table full, key false match, stage-1 budget, or recovery failure.

Table capacity and key matches. Outside `P_60`, fewer than 60 collisions occur. The number of finished trails is then at most `N1 + 59`, so filling `tmax` entries requires `N1 >= tmax - 59`. The Chernoff bound is `P_table = 4.419219e-07`. A false 48-bit key match costs `P_key = 2.846276e-05`, using key space `2^37 * 1862`.

Sixty collisions. At a fresh evaluation t, the collision probability is at most `(t - 1 + 2^18) / N'`. For `w = e^5`, multiplication of the conditional moment bounds gives

```text
E[w^C] <= exp((w - 1) H),
P(C >= 60) <= exp(-300 + (e^5 - 1) H)
             = P_60 = 3.224408e-99.
```

Stage-1 budget. Let `eta_t` mark that the low 20 bits of the independent uniform value `V_t` are zero, and let `mu2 = Q / 2^20 = 323434182974310058593750000000000`. Fresh stage-1 hits are at most `sum eta_t`, which is `Binomial(Q, 2^-20)`. The multiplicative Chernoff bound gives

```text
P(fresh hits > 1.5 mu2) <= exp(-0.108 mu2)
                            = exp(-34930891761225486328125000000000)
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
         = 13665028382266928328160450887.4550708347321...
         > 1000.
```

Appendix A evaluates `A_replay` downward and charges the outward upper bound `P_replay-simple < exp(-1000)`. It also checks

```text
240 M = 8909111378837674593966325268470009920
      <= 339145321846470144000000000000000000000 = Q.
```

Outside the root-event union and the new `P_replay-simple` term, each of the 60 replay windows has at most `2 M / 2^20` hits. Thus the repeated hits are at most `120 M / 2^20 <= mu2 / 2`. Together with at most `1.5 mu2` fresh hits, this is at most `2 mu2`, below `e2max = 2 mu2 + 64`. The residual probability of the stage-1 budget halt is below `P_stage-fresh + P_replay-simple < 2 exp(-1000)`, in addition to `P_60` and the root-event union already charged in `P_cut`.

Recovery and the three small structural events. A recovery without a pair comes from a false key match, already charged by `P_key`, or from one of the fewer than `2^18` starts lying on an evaluated trail. The latter event is `P_start = Q 2^18 / N = 7.677978e-34`. Outside those events, Lemma 1 returns a pair within `capr` calls. A repeated DP-valued output costs `P_DP-repeat = k^2 L / N' = 3.631214e-34`. A partner in the same batch costs `P_same-batch = 255 Q / N' = 7.468736e-37`.

The outward-rounded certificate gives `P_start + P_DP-repeat + P_same-batch + P_60 < 1.131667e-33`. It adds `P_stage-fresh` and the new `P_replay-simple` term to `residual_actual`; each is below `exp(-1000)`. The total fits inside the charged `2^-90 = 8.077936e-28` reserve. The certificate uses outward rounding for every exponential and rational term, so it needs no probabilistic rounding allowance. This proves the lemma. QED.
Consequently the printed float bound is

```text
1 - 0.608557359293 - 0.001306833249 - 8.363474e-06
  - 2.925122e-05 - 1.571674e-05 - 4.153838e-06
  - 4.941650e-05 - 2^-40 - 2.846276e-05
  - 4.419219e-07 - P_tiny
= 0.3900000010001152.
```

Appendix A independently certifies `P_F >= 0.390000001000 >= 0.39` with exact rationals and outward-rounded decimals.

Sensitivity is recomputed from the live plan by replacing N with `N/(1-eps)` and reoptimizing Tp and B:

| hazard deficit eps | replacement Tp | extra time bits to restore 0.39 |
| ---: | ---: | ---: |
| 0.01 | 1853 | 0.00724949 |
| 0.05 | 1815 | 0.03700175 |
| 0.10 | 1767 | 0.07600421 |
| 0.25 | 1613 | 0.20752832 |

A collision-hazard surplus helps. No robustness margin is treated as a theorem.

## 5. Premise H1 and its evidence

H1 compares this fixed function with a uniformly random function. Its four clauses are:

- (a) Distinct fresh evaluated inputs have independent uniform outputs and pair-collision hazard `2^-256`.
- (b) Iterates from the starts `r+t` have the first-collision law of a random mapping.
- (c) A fresh output is a DP with probability `1862/2^122`, independently of collision events.
- (d) Under the adaptive program history and later DP flags, a fresh output hits any fixed earlier non-DP output with probability at least `2^-256`.

Lemma 2 proves the bound for the random function. H1 transfers that bound to the fixed target. The circuit, ledger, memory, and random-function theorem are exact claims.

Support of H1 (stated; it is not measured at width 256):

1. H1 is the generic premise of parallel collision search with distinguished points. Paul C. van Oorschot and Michael J. Wiener, "Parallel Collision Search with Cryptanalytic Applications", *Journal of Cryptology* 12(1):1-28, 1999, DOI 10.1007/PL00003816, model a fixed compression function iterated from fresh starts, without a chosen input difference, by a random function. The generic entries of this track use the same premise: mitchuski 3017c952, 1884db5b, and 4684dfc2; lamb356 3642e1cd; dariolina 6b678689; and 0xplemonade's 7523902c, 7347a2b6, 60dbf898, 332b47e1, 5ed693e8, ff37a322, c9ae3732 (round 64), and Jbenisek's 31eb4be6 (round 53); 8436c1e7 is the current best round-53 entry.
2. Clause (d) fails in the adverse direction only if `g`, along its own iterates, collides less often than a random function by a constant factor `1 - eps`. Such a property would separate this 53-step function from a random function in a way that no published result shows. This entry chooses no input difference and uses no differential property.
3. A deviation that raises the collision hazard helps. Section 4 prices a deficit exactly: 0.00724949 bit for `eps = 0.01`, 0.03700175 bit for `eps = 0.05`, 0.07600421 bit for `eps = 0.10`, and 0.20752832 bit for `eps = 0.25`.
4. The program checks agree with random-function reference values at their scopes. For `proj-k0-w256`, 256 independent uniform 16-bit projections contain a pair with probability 0.392678 per trial, or 100.53 of 256 trials. The expected number of equal pairs is `C(256,2)/2^16 = 0.498047` per trial, or 127.50 over 256 trials. For the exact seven-batch `plan(16)` (unchanged from the round-40 package), the credited lazy-random-function reference over 10,000,000 complete mappings gave probability 0.6958435 with standard error 0.00014548, or 178.14 successes per 256 trials. A participant-run replay of both declared experiments, using the organizer request format and organizer-style per-trial seeds derived from a substitute commitment (not the organizer's own seed material), returned 178 checked width-16 search pairs in 256 trials for `bssha-n16` and 89 checked full-width projection pairs in 256 trials for `proj-k0-w256`; every returned pair was recomputed with `verifier/hash_functions.py:digest(..., "sha256", 53)` and satisfied the declared low-16-bit event. These are within about 1.5 standard deviations of the references (sd about 7.4 and 7.8 trials). The organizer's own counts are produced by its executor at evaluation time. These are consistency checks that can expose implementation-level deviations. No count is used to change the score.

Limitation: H1 cannot be measured at width 256, so these experiments do not measure the full-width collision hazard or the success probability at `2^128` scale.

## 6. Experiments

Two organizer consistency checks run `experiments/bssha.py`. Before dispatch, `bounded_check` runs the byte-exact mirror of the normative C emitter. The organizer recomputes the complete digest of every returned message pair.
`bssha-n16`: per trial, one attempt of the 256-lane search at width 16 (DP = low 2 bits zero, plan(16): 7 batches, cut rule, table, recovery) on the walk g16(x) = the low 16 bits of the complete digest of M(x), x < 2^16. Each batch runs the shipped program on the 256 planes (the 240 high input planes zero), then the experiment's digest network (`DigestNet`, bit-sliced, experiment code only, not in the ledger) inverts walk B, forms cv1 = IV + state and runs block 2; the recovery runs the rolled recovery program and the same inverse and block 2 in scalar form. The trials run side by side: the planes of trial i occupy bits 256 i to 256 i + 255 of each word, so one pass of the program and of the digest network serves every live trial, and each bitwise record acts on every trial's 256 bits alone. The trial returns M(x), M(y) when the attempt succeeded and two nulls otherwise. Checked event: the messages are distinct and their complete 53-step digests agree in the low 16 bits. This is exact, because at width 16 the walk is those 16 digest bits. The width-16 walk differs from the width-256 walk g only in the map after the program (inverse, block 2, low 16 bits); it runs the same program, search, table and recovery.
`proj-k0-w256`: per trial, 256 points at width 256 (source by trial index mod 3: uniform from the seed, counter r + i, iterates of g from 256 seed-derived starts) evaluated with the shipped program; their complete digests are formed by the digest network; the trial returns two points whose digests agree in the low 16 bits when the set holds such a pair. Checked event: as above. It checks at full width the program, the inverse of walk B, the chaining value, block 2 and the message construction.
The experiments check execution, witnesses, and agreement with the scope-matched reference values in Section 5. Their counts do not enter the cost or success bound.
The digest network is built with the same `Gen` class as the kernel. Its inverse of walk B contains a four-variable sum with the nonzero constant `1 + K_51`. In the round-64 port the inherited four-word carry-fusion branch of `Gen._baseline` dropped the corresponding constant `1 + K_62` (the branch is reached when the chosen carry-in count is zero), so the branch is guarded by `not cv` (taken only when the absorbed constant is zero). The guard is kept unchanged from 26d9ad0b and 1f18d544; whether or not the branch is reached at round 53, the self-test checks the guarded digest network against scalar SHA-256. The guard does not change the kernel: all 28 kernel four-variable sums have zero constant, and the emitted stream hash is unchanged by it. The normative C emitter's `addm` contains the same branch (`nv == 4 && !bb`) without the guard; it is unaffected for the same reason, since the kernel has no four-variable sum with a nonzero constant (the C and Python streams are byte-identical). The self-test checks the digest network against scalar SHA-256 on 256 random full-width lanes.

## 7. Memory

Table: 120,961 slots * 48 bits = 725,766 bytes. Slot t belongs to trail t and stores `key + 1`; zero is empty. The maximum key is 281,474,976,710,469, so the sentinel transform fits.
Code: 66,453 body instructions * 4 bytes = 265,812 bytes. The 490 recovery records use 2,450 bytes. The other 1,232 fixed 5-byte instructions use 6,160 bytes. Total code is 274,422 bytes.
Counters and copies use 16,384 bytes; this area holds the fresh word r, the trail counter t, the batch and slice counters, the per-lane age records, the 8 KiB stage-1 plane copy, and the recovery predecessor copies. The 910 registers use 29,120 bytes. The 90-word recovery array uses 2,880 bytes. No advice. Memory peak is `max(740623,1048572) = 1048572` bytes, below `2^20`.
The table size is the largest that fits: `floor(8 * (2^20 - 274422 - 29120 - 16384 - 2880) / 48) - 263 = 120698`. Appendix A derives Tp = 1862 and certifies `P_F >= 0.39`.

## 8. Heuristics, conventions and what is credited

The premise is H1. The 910-register file and native formats are declared machine prices, not statistical premises. Lemma 2 proves the cut count. There is no advice.

Direct dependency: 26d9ad0b-e6f1-4370-abb4-b36aa97ab9e6 (mpjunior92, round 52) supplies the complete program `experiments/bssha.py` (kernel generator, normative C emitter, allocator, rolled recovery, search, table, plan, probability certificate and experiments), its round-port method and the structure and wording of this proof; its round-64 instance 1f18d544-cd04-4177-8739-fad19d55a98a supplies the recovery itemization and the digest-network guard. Through them, 27984c2d-fc4b-4285-a430-c5f364c10a7e (sraiw, round 40) supplies the program, f7b1dea4-2883-45d6-9c0c-89a5d4ad1b1a the recovery compaction, fb8a3bce-1839-4b9a-ab67-76670b4a05c9 the baseline package, b3f10279-3fa4-4d7b-9011-3faa2ae352c8 the fused kernel, schedule, allocator, and recovery design, and ff37a322-c5e7-4656-bb89-02f1a5d0e213 the native-4-byte machine and accounting base. New here: the round-53 instantiation (constants, emitter dimensions, register count, recovery array), the recovery-program prologue for a round count with (ROUNDS - 16) mod 4 = 1, re-chosen tail masks, the round-53 wasm build and fuel measurement, and the re-derived round-53 plan, ledger and certificate. The current best round-53 entry 8436c1e7 (time_log2 124.06965) is cited for its score only; no code or text of it is used.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate, and `certify` recomputes the bound of Lemma 2 in exact rationals and 60-digit decimals with outward rounding: the line `P_lower certified` is a proved lower bound on P_F, asserted >= 0.39. The same numbers come from `python3 bssha.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 66453, 22, 3, 256
INSTR_REC = 66453
PH7, EXTRA, RECINIT = 2092, 76, 102
N_BITS, S1, W, KAPPA = 256, 20, 102, 13         # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE = 2800, 3800, 4200, 1300
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 7
CUT_HALT_ORDER = CMAX + 1
assert CUT_HALT_ORDER == 8
WASM_RUN_OPERATORS, WASM_OPERATOR_FACTOR = 125714851, 2
BODYB, CTRLB, RECB, REC_RECORDS = 4, 5, 5, 490
CONTROL, REGFILE, COUNTERS, ADVICE, ARRAYS = 1207, 29120, 16384, 0, 2880
KEYB = SLOTB = 48                              # key+1; zero is the unwritten sentinel
SEARCH_EVAL_OPS = 1 << 48
OFFSET_SEARCH = 1641 * SEARCH_EVAL_OPS            # 64 endpoint + 1 initial + 3 * 192 coordinate + 1000 perturbation builds
SELECTOR_SEARCH = 687 * SEARCH_EVAL_OPS
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
        ("finished events: (tmax + 1) * (3800 + 6 * (tmax + 263))", (tmax + 1) * (EVENT + 6 * (tmax + LANES + CMAX))),
        ("cut trails: 7 * 4200", CMAX * CUTOPS),
        ("recovery: 2 (c + 2^48) * (%d + 76) + 600 + %d" % (PH7, RECINIT), 2 * capr * (PH7 + EXTRA) + 600 + RECINIT),
        ("setup and generator", SETUP_FIXED + emitter),
        ("charged offset search", OFFSET_SEARCH),
        ("charged selector search", SELECTOR_SEARCH)]
N = int(sum(v for _, v in rows))
assert N == 88231920371180619547889294928080393029695
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
P, C = 100000, 3988
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
Tp = 1862  tmax = 120698  B = 1324786413462774000000000000000000000  e2max = 646868365948620117187500000000064  c = 37121297411823644141244880308581052
memory bytes = 1048572
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000001000
residual P_start          7.67797798931757910781446200276864411477926409680442806385671E-34
residual P_DP-repeat      3.63121391834508136050760562283265813894318970617832594896249E-34
residual P_same-batch     7.46873621855156964299273609430696462603088664989667994656247E-37
residual P_60             3.22440783632908465394552395776463010782739485759456838346740E-99
residual fresh exponent   34930891761225486328125000000000
residual replay exponent  13665028382266928328160450887.4550708347321930731081080936417
residual P_stage-fresh    5.07595889754945676529180947957433691930610687878259230750892E-435
residual P_replay-simple  5.07595889754945676529180947957433691930610687878259230750892E-435
residual residual actual  1.13166606438812120379650603616956092183484846896326506927658E-33
residual 2^-90 reserve    8.07793566946316088741610050849573099185363389551639556884766E-28
residual reserve slack    8.07792435280251700620406254343536929624441554703170593619697E-28
residual P_tiny charged   8.07794698612380476862813847355609268746285224400108520149835E-28
main loop: B * 66478                                 88069151194178289972000000000000000000000
slice checks: ceil(B / 2^48) * 1300                  6118562856377729275437400
stage-1 hits: e2max * 2800                           1811231424656136328125000000000179200
finished events: (tmax + 1) * (3800 + 6 * (tmax + 263)) 88057886634
cut trails: 7 * 4200                                 29400
recovery: 2 (c + 2^48) * (2092 + 76) + 600 + 102     160957945577667320997658276517024846590
setup and generator                                  252243303
charged offset search                                461900436782186496
charged selector search                              193373309000220672
N = 88231920371180619547889294928080393029695
certificate: 2^12405697 * 3988^100000 <= N^100000 < 2^12405698 * 3988^100000
log2(N/C) = 124.0569747867
time_log2 = 124.05698
```
