# blake3-r7: polarity-exact pair-carry columns, 44,310 gates per 256-lane step

This is a credited derivative of mitchuski's f88f3751-f08b-4561-a764-a04b5f7a899a, which is itself a derivative of Jbenisek's b9f7a2bc-2ba7-4a34-a4c0-8efa7527fba1. We retain their target relation, generic distinguished-point birthday search, five-byte gate format, table and recovery algorithms, random-function Lemma 2, and bounded experiments. f88f3751 contributed the pair-encoded carry and the two general nine-gate column templates. b9f7a2bc contributed the rest of the search construction and credits the full lineage listed in Section 8.

What changed is narrow and mechanical. f88f3751's templates sometimes cost ten physical word operations because a mixed-polarity AND expands to an AND plus XOR. The generated r7 circuit loses exactly 50 gates this way. We encoded the full five-input column relation in SAT, with exact `s` and `U'` outputs and the permitted don't-care on `u'` when `U' = 1`. The development search found a nine-gate full column for the one expensive stored-polarity context, mask 0x10, and an eight-gate penultimate column where `u'` is dead. Independent C checks exhaust all 32 input rows. Substituting those circuits removes the 50 lost gates and changes no attack logic. A separate development-only eight-gate UNSAT observation is disclosed in Section 3.2 but is not part of this claim.

The exact step is 44,310 gates instead of f88f3751's 44,360: 36,312 XOR, 3,337 AND, and 4,661 OR. The emitted full search program leaves room for 91,483 table entries and uses distinguished-point numerator 1,398. The exact ledger is 58,988,094,089,452,902,017,216,346,428,406,269,062,049 word operations, or unrounded `time_log2 = 124.915947152086` after division by 1,470. The submitted upper bound is 124.91595. Search memory is 1,048,510 bytes, so the normalized score is also 124.91595. The previous frontier score was 124.91757.

The target remains the plain one: 64-byte messages `0^32 || x`, one block, flags 11, standard IV, no prefix, no advice, and no BLAKE3 weakness. The circuit computes the same complete seven-round digest. Its output polarities define a fixed mask q and the walk `g(x) = f(x) XOR q`; equality under g is equality under f.

## 1. Target and relation

Target `blake3-r7-prefix-v1` (the benchmark's blake3 round-7 profile, the full seven rounds of BLAKE3). The two colliding messages are 64 bytes, M(x) = 0^32 || LE32(x): 32 zero bytes (words m0..m7 = 0) followed by the 256-bit integer x (words m8..m15, little endian). It is one chunk of one block: chaining value IV, counter 0, block length 64, flags 11 = CHUNK_START | CHUNK_END | ROOT, 7 rounds with the BLAKE3 message permutation between rounds, digest = the 8 words v[i] XOR v[i+8] (i < 8), little endian (this is `verifier/blake3.py:blake3(M(x), 7)`). Write f(x) for the digest read as a 256-bit little-endian integer.
The walk is on g(x) = f(x) XOR q, where q is the fixed 256-bit mask (weight 112) of the polarities of the 256 digest planes of the circuit that the generator of Section 3.2 builds; q is printed by `python3 bsrho.py --ledger`. g(x) = g(y) if and only if f(x) = f(y): XOR with a constant is a bijection. The attack outputs x != y with g(x) = g(y), hence f(x) = f(y), and M(x) != M(y) are two distinct messages with equal complete 256-bit digests (a finite byte string of 64 bytes is in the profile's message domain, "Finite byte strings of bit length below 2^64").
Our independent C generator emits the 40-bit register program and an independent C evaluator compares complete digests with a scalar BLAKE3 reference. Four fixed vectors came from the organizer reference. Another 8,193 deterministic random messages and 4,096 independent seven-step chains gave zero differences. The allocated program was executed directly, not only the node graph; it uses 773 registers. The package's separate selftest compares 4,096 lanes and 4,096 chained lanes, checks the allocated program, the reduced-width chain, and the packed recovery circuit.

## 2. The attack (program `experiments/bsrho.py`, sections 3 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 32 bits are zero and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 1398. The density is theta = 1398 / 2^122 and L = 1 / theta = 2^111.5519. The key of a DP is the 36 bits of x above bit 121 followed by the 11 low bits of F (F < 1398 <= 2^11, so those 11 bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated straight line of Section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 32 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above. If the key is in the table, go to 6. Otherwise store t under the key (8-byte entry: key and t in one 64-bit slot, no length, Section 7) and
   start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 16 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 91,483 keys, when a second trail would be cut, or if step 6 finds no pair. The terminal event that discovers a full table is processed before that halt and is charged separately in Section 3.4.
6. Recovery, two passes, each of at most capr batches. Pass 1 (lengths): the two trails t and t' with the same key are walked together from their starts r + t and r + t' (both lanes of one packed circuit), one step per batch, and after each step each lane that has not finished is tested for being a DP (low 32 bits zero, then the next 90 bits below Tp); the step count at which a lane first is a DP is its length, l1 for the longer trail, l2 for the other. Pass 2: advance the longer trail from its start by l1 - l2 steps of g, then step both together; at the first step
   with g(a) = g(b) and a != b output (a, b). Both lanes of one packed circuit (1540 operations: the compression and one XOR of each of the 8 output words with the 32-bit word of q; used by nothing else) are used. Pass 1 runs at most capr = c + S packed calls. Pass 2 can run capr + 1 calls because its final equality check is inclusive. The program halts if a lane has not reached a DP after capr steps in pass 1, or if l1 > capr.
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 bsrho.py --ledger`): Tp = 1398, L = 2658455991569831745807614120560689152 / 699, B = 1325746535010000000000000000000000000, Q = 256 B = 0.997381 * 2^128 evaluations,
e2max = 158041302562952041625976562564, c = 60851639292013316069988306050030081 (= 2^115.552), table capacity tmax = 91,483 entries of 8 bytes. The trail numbers t stay below 2^17 (the 256 starts, stored finished trails <= 91,483, one terminal finished trail, and cut trails <= 1 keep t below 256 + 91,483 + 1 < 2^17), so the 17-bit field of an entry never overflows (the program asserts LANES + tmax + CMAX < 2^17 in its plan and t < 2^17 when it stores an entry); every length is below c + S < 2^115.6 and is recomputed by pass 1 of the recovery, not stored.
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is derived by the generator at setup and is also written into the recovery circuit as immediates).

## 3. Operation ledger

### 3.1 Machine
Machine model declared by this entry, b9f7a2bc's (as in Jbenisek's 0a9640ed, which passed the judges with it). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices loads and stores, and it gives no register count.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 800 registers (a declared convention of the entry, H3, supporting; Section 3.5 prices smaller files). Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each.
The main loop has no loads, stores or moves: the generated straight line needs 773 registers (`allocate` in the program assigns them; output plane j is written into the register that held input plane j, so the next batch reads the same registers), leaving 27 of the 800 for the loop counter, the limit and the handlers' temporaries. The file of 800 registers is counted as memory: 25,600 bytes (Section 7).
Constants of the step are folded into the circuit at build time. The organizer's reference count C(r7) = 1,470 (222, 430, 638, 846, 1,054, 1,262 and 1,470 for 1 to 7 rounds, that is 14 + 208 r; the value printed by the lane contract, `pareto_candidate.py --family blake3 --rounds 7 --show-contract`: reference_operation_cost 1470) is used only as the unit: Unit = 1,470 operations. Code is memory, and the cost model does not fix its format; this entry prices it. A register-format instruction is one 40-bit word, charged 5 bytes: an 8-bit opcode and three 10-bit fields. The register-format instructions are XOR, AND, OR and ADD of two registers into a register (the fields are the destination and the two operand registers, all below 1,024 since 800 registers are declared), NOT of a register (one field unused), and a shift of a register by a constant count (the third field holds the count, which is below 32). None of them carries an immediate or an address. Charged at 5 bytes are: the gates of the step (XOR, AND, OR); 32 of the 34 operations of the stage-1 test (31 ORs and the complement); and the operations of the recovery circuit (1540 operations: 252 ADDs, 208 XORs and 208 ORs of two registers, 416 shifts by a constant count, and 432 ANDs, 16 XORs and 8 ADDs whose second operand is a constant held in a register). Every AND, XOR or ADD of the recovery circuit that has a constant operand uses one of 33 distinct 256-bit constants (the lane masks of the packed 36-bit lanes and of the rotations, the words of q, and the folded additive constants). These constants are loaded once, at the start of the recovery, into 33 registers that the halted search no longer uses: 33 load-immediate instructions of 36 bytes of code each, and 33 operations in the recovery row of Section 3.4. Charged at 36 bytes (opcode, registers and an inline 256-bit immediate or address) are the compare and the branch of the stage-1 test, the loop control, and every other instruction: handlers, setup, cut and slice, the recovery besides its circuit, the constant loads, spill loads and stores, and the WebAssembly image of the generator. The program of the generator writes the step's records in this format (Section 3.6). The 5-byte word is a price stated by this entry (H3), not a measurement; Section 7 counts the code instruction by instruction.

### 3.2 One batch = 44347 operations for 256 trails
Representation: a 32-bit word is 32 planes; plane j is a 256-bit integer whose bit l is bit j of the word of lane l. A rotation is a renaming of planes (no operation). XOR, AND, OR of words are 32 operations each. The sum of two words is a ripple of full adders over the planes; the lowest bit has 2 gates (no carry in) and the highest 2 (no carry out), and constants (the IV words, the zero words m0..m7, the length and the flag word) are folded at build time.
The full adder is the pivot adder of 6ae36351 (Jbenisek's re-implementation in b9f7a2bc, `Gen.fa`, unchanged). Each signal is a pair (node, polarity): the register holds the node's value and the true plane is that value XOR polarity, so complements are free. Of three variable inputs a, b, c, two have the same polarity (pigeonhole); take the third as the pivot p and the two equal ones as x and y. With u = x XOR p and v = y XOR p: sum = u XOR y, carry = (u AND v) XOR p, because maj(x, y, p) = p XOR ((x XOR p) AND (y XOR p)). u and v have equal polarity, so the AND is always one gate (an AND of two upright planes, or an OR of two inverted planes, with the result's polarity set); every full adder with three variable inputs is 5 gates (XOR for u, XOR for the sum, XOR for v, the AND, XOR for the carry). With one constant input, sum = x XOR y XOR k and carry = x AND y or x OR y (2 or 3 gates); with two the plane passes through. The program generates the straight line at run time. At this target no two gates of the network are equal and every gate is used (the reference generator `Gen`/`Step`, which would share equal gates and drop unused ones, finds none: the selftest prints 0 shared and 0 unused gates), so the machine generator of Section 3.6 builds the network in two passes and keeps no node table.
The 3-operand column (this entry's change). An addition a + b + m whose three words all hold a variable plane (52 of them at seven rounds: every a + b + m with a message word of x, outside the folded first half-round) is computed in one ripple instead of two. Bit 0 is the pivot full adder above (5 gates), whose carry k is passed on as the pair (0, k). At bits 1 to 31 the carry into the column is a pair of planes (u, U) whose value is 1 when U = 1 and 2u when U = 0; the column receives the addend bits x, y, z (a, b, m in an order chosen below) and the pair, and returns the sum bit s and the pair (u', U') of the next column, with x + y + z + value(u, U) = s + 2 value(u', U'). Two 9-gate columns are used (all signals are (node, polarity) pairs as above; | is OR):
    template 0: n5 = z ^ U, n9 = x ^ n5, s = y ^ n9, n6 = x ^ y, n8 = U | (z ^ u), n11 = !n6 & n9, u' = n5 ^ n11, U' = n8 ^ n11;
    template 1: w = y ^ U, n8 = z ^ w, s = x ^ n8, n6 = U | (y ^ u), U' = n6 ^ ((z ^ w) & (x ^ w)), u' = n6 ^ w.
Each identity is a finite statement on five input bits. A column needs seven XORs and two AND-type gates. An AND-type gate costs one physical word operation when its operand polarities permit AND or OR, and two for a mixed-polarity input. f88f3751 tries all six orders of `(a,b,m)` and both templates, then keeps the first cheapest. That generator produces 44,360 gates and pays 50 excess gates to mixed polarity.

The new exact circuits apply when the stored-signal polarity mask `(x,y,z,u,U)` is 0x10. For a full column the nine gates are:

```
g5=x^z; g6=y^U; g7=u^g6; g8=U&g7; g9=g5^g6;
g10=x^g6; g11=g6^g8; g12=g5|g10; g13=g8^g12;
s=!g9; u'=g11; U'=g13.
```

At bit 30, `u'` is dead because the top sum bit depends only on the parity selector `U'`. The eight-gate circuit is:

```
g5=y^U; g6=u^g5; g7=U&g6; g8=x^g5;
g9=x^z; g10=z^g8; g11=g8|g9; g12=g7^g11;
s=!g10; U'=g12.
```

Here the five named inputs denote the stored planes, so the semantic U input is inverted. The generator still runs the inherited twelve dry trials first, then dispatches to these circuits for mask 0x10. Its normal constant folding remains active. The final step has 44,310 gates, exactly 50 fewer than f88f3751 and 1,664 fewer than b9f7a2bc's 45,974-gate two-ripple step.

The SAT encoding has one selector for each unordered pair of earlier signals, one of XOR/AND/OR per gate, row values for all 32 assignments, and output selectors with free output polarity. `s` and `U'` are constrained on all rows; `u'` is unconstrained exactly when `U'=1`. During development, CaDiCaL 2.1.3 returned UNSAT for an unrestricted eight-gate instance with 634 variables and 64,666 clauses. This is a disclosed development observation, not a premise or conclusion of the submitted claim, because the 305,453,033-byte binary DRAT proof is not in the package. The CNF SHA-256 is `34ee22b960024541210be66285a6f23fe55510566e29c7b4e467b63aa61d1388`; the binary DRAT SHA-256 is `1424bb5997ff92eb6378517b3d453cac16bd327bf87033ecffb82f3b3663dbbb`; its gzip SHA-256 is `f5f0be62d61634ca3a63790441e59758d32e23b7e5b0f7d1b01dd7891ba1f1b3`. The result does not need minimality. The two used SAT circuits are established directly by a separate C checker that exhausts all 32 input rows for each model.
The mask walk: the circuit's 256 output planes are stored in registers exactly as the circuit produces them (a register holds the node value, the digest plane is that value XOR q_j, q_j the polarity of the signal) and they are the 256 input planes of the next batch. So no operation complements a plane, no polarity vector is chosen, and the chain is x -> g(x) = f(x) XOR q. q is a fixed constant of the circuit (weight 112 of 256); the generator derives it while it builds the circuit, and the recovery circuit uses it as 8 immediates. Equality under g is equivalent to equality under f (Section 1), so a collision of g is a collision of f.
The generated line (`python3 bsrho.py --ledger`, `--selftest`): 44310 gates = 36312 XOR + 3337 AND + 4661 OR = **44310 operations**, no complement operation. Per trail 173.0859375 operations = 0.117746 unit, against 1 unit for a compression.
Validation: 4,096 lanes and 4,096 lanes chained for 7 steps against the scalar digest in the selftest (stored planes = f XOR q); 4,096 lanes against the organizer reference (Section 1); the register-allocated code executed on a register file gives the same planes as the generated function (selftest).
The generator itself runs once at the start; its work is charged in the setup row (Section 3.3), its code and peak storage are accounted in Section 3.6 and Section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 44310 + stage-1 test 34 + loop control 3 = 44347 operations. Stage 1: the 32 low planes of digest word 0 (stored planes, which are the planes of the next point x) are combined into the mask of zero lanes: 31 ORs over the 32 planes, a complement, a compare of the mask with zero and a branch: 34 operations (`stage1_ops`; 32 register-format, the compare and the branch 36 bytes of code each). The test loses no event: a DP has all 32 low bits zero, so its lane is flagged.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no flagged lane (probability about 1 - 2^-24) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers):
- Stage-1 hit (a flagged lane): store the 256 planes to a 8 KiB copy in memory (256 stores), then a loop over the planes: load, shift right by the lane number, AND 1, shift left by the plane number, OR into the accumulator, address increment, plane counter increment, compare, branch (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (3 extractions and at most 12 further operations), counters. Total below 2,800; charged **2,800** per hit (the polarity XOR of the earlier entries is not needed any more). The hit budget e2max is enforced by a halt.
- Finished trail (a DP, new start): key formation, one store of the 8-byte entry (key and t in one 64-bit slot), the new start r + t' (1 add), insertion of the 256 bits of the new start in the lane: per plane load, shift, AND 1, shift left by the lane number, AND with the complement of the lane bit, OR, store, address and counter increments, compare, branch (12 per plane, 3,072), reload of the 256 planes (256), lane arrays and counters (below 200). Total below 3,550; charged **3,800**. The key scan of the table is charged separately: the table holds 4 slots per 256-bit word, testing a word costs 8 operations, 9 with the AND that clears the 17 trail-number bits of each 64-bit lane (Section 7), charged 3 per key (12 per word). At most tmax finished trails (a halt on a full table).
- Slice check (every 2^48 batches): the 256 births (load, subtract, compare, branch: 1,024), slice counter: charged **1,300** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **4,200**; at most 1 cut trail (a halt on the second).
- Recovery batch (both lanes in one packed circuit, 1540 operations, the last 8 of them the XORs with q) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations. The shared call, return, eight digest moves, loop increment, compare and branch cost 13 more, so pass 2 uses 39 extra operations. A pass-1 batch replaces the 26-operation equality test with 20 operations for the two DP tests and finished flags, for 33 extra operations. The emitted static program therefore contains the 13 shared instructions once, 20 pass-1-only instructions, and 26 pass-2-only instructions: 59, not 47. Every packed call is still conservatively charged at 1540 + 64 = 1604 operations. Pass 1 uses at most capr calls. The inclusive pass-2 loop can use capr + 1, so the ledger charges `2 capr + 1` calls.
- Setup and generator: 1 random word; the 256 starts r + t inserted in memory (256 x 3,100 = 793,600, each at most 12 x 256 + 28) and one reload; counters; fixed part charged 813,600. The generator: 921,976 primitive calls (two passes of 460,988 calls each, the dry trials of the 3-operand columns included) and 44310 emitted lines, each charged 200 word operations: 193,257,200. Setup and generator together 194,070,800 operations = 2^17.01 units, charged in the time bound (3.4). There is no other preprocessing: no scan, no climb, no advice.
Code size is derived from the emitted program, not from those prose bounds. `bsrho.py --program` emits 47,139 canonical physical-register records and `--ledger` hashes their canonical text. The sections are 44,310 step gates, 32 stage-1 register operations, 2 stage-1 control instructions, 3 loop instructions, 1,000 handler instructions, 160 setup/cut/slice instructions, 33 recovery constant loads, 1,540 allocated recovery-circuit instructions, and recovery control split as 13 shared, 20 pass-1-only and 26 pass-2-only instructions. The 1,000- and 160-instruction inherited reserves contain explicit charged `NOP` padding after their complete routines. The image has 45,882 five-byte records and 1,257 thirty-six-byte records, 274,662 bytes total. Its SHA-256 is `080d18f04edc5d4e65f6d17d095bf315a7ffacb0e0617ec5c18b207092740ec8`.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 44347 | 58,792,881,588,088,470,000,000,000,000,000,000,000,000 (= 5.8793e+40) |
| slice checks: ceil(B / 2^48) * 1,300 | 6,122,997,204,418,112,460,189,800 |
| stage-1 hits: e2max * 2,800 | 442,515,647,176,265,716,552,734,375,179,200 |
| finished trails: (91,483 + 1) * (3,800 + 3 * 91,483), including the terminal full-table event | 25,455,331,516 |
| cut trails: 1 * 4,200 | 4,200 |
| recovery: (2 * (c + 2^48) + 1) * (1540 + 64) + 600 + 33, c + 2^48 = 2^115.552 | 195,212,058,848,778,717,953,425,457,533,784,286,533 |
| setup and generator | 194,070,800 |
N = 58,988,094,089,452,902,017,216,346,428,406,269,062,049 = 5.898809e+40 operations.
N / 1,470 = 4.012796e+37 units = 2^124.915947. Claim `time_log2` = 124.91595 (integer power certificate in Appendix A: (a + 1) / 100000, an upper bound, 2.85e-06 above the unrounded 124.915947152086). The main loop is 99.67 percent of it, recovery 0.33 percent.

### 3.5 Register file and smaller files
Convention H3 gives the machine 800 registers of 256 bits. The generated line needs 773. Both independent C allocation and the package allocator produce that peak, pin output plane j to the register that held input plane j, and execute the allocated instructions against the node graph. No spill, move, load, or store occurs in the main line. Machines with fewer than 773 registers require charged spills; this entry makes no numerical claim for those machines.

### 3.6 Generator code and peak storage of the setup
The generator that builds the straight line at the start of the run is part of the machine code. It is the credited two-pass freestanding C generator with `col3_m10` and `col3_m10_no_u` added. Pass 0 counts node uses. Pass 1 rebuilds the same network, frees a register at its last use, pins the final 256 outputs to registers 0 through 255, and writes five-byte instruction records. It keeps no node table. The package's independent Python generator and allocator reproduce the same 44,310 records and 773-register step peak. Native `gcc -Os` compilation of the C port contains 1,159 machine instructions. The ledger charges a conservative 2,200 instructions, 79,200 bytes at 36 bytes each, which also exceeds the parent generator's 2,003-instruction WebAssembly image plus the added routines. q falls out of the output polarities and is written into recovery as eight immediates.
Its scratch (`gen_scratch` of the program) is: use counts 44,567 nodes x 8 bits = 44,568 bytes, signal state 2,528 (the 16 x 32 state words 2,048, three 32-word temporaries 384, the free-register bitmap 96), shadow stack 2,048, result record 68, and 128 bytes for the 124 bytes of scalar globals and IV/PERM/GC tables not charged to the image. Total scratch is 49,340 bytes. The generator builds the network twice, with the dry trials of the columns in both passes; its work is charged in the setup row (Section 3.3): 921,976 primitive calls (2 x 460,988, the trials included) and 44,310 emitted lines at 200 word operations each.
Layout. The setup phase holds the main code, 274,662 bytes; counters and plane copy, 16,384; the declared 800-register file, 25,600; the conservative 79,200-byte generator image; and 49,340 bytes of scratch. The total is 445,186 bytes. The search phase holds 731,864 table bytes, the same 25,600-byte register file, counters, and main code: 1,048,510 bytes. Thus the larger phase stays 66 bytes below 1,048,576, after the plan deliberately reserves 64 bytes.
No other run determines a number of the claim: the circuit, its size, its registers, q and the instruction count come from the generator; the plan (Tp, B, c, tmax) is a deterministic computation of `plan(256)` from the stated formulas, and the experiments and checks of Sections 1, 5 and 6 test the program and select nothing.

### 3.7 Preprocessing
None offline. The generator is run inside every attempt and is charged in the setup row; the claim declares preprocessing_log2 = 17.02, the setup and generator row, which is also inside time_log2. The memory figure of Section 7 covers this preprocessing: the generator runs in the setup phase of the same attempt, its code image, scratch and declared register file are in the setup-phase total of Section 3.6 (445,186 bytes), and nothing it produces is stored outside the 1,048,510 bytes of the search phase.

### 3.8 Memory and the scalar score
The lane's scoring policy is `hashsmash-scalar-tm-v1` (memoryUnitBytes 1,048,576, minimumMemoryUnits 1): score = time_log2 + max(0, memory_log2_bytes - 20). With the register-format instructions charged 5 bytes and all others 36 (Section 3.1) the program, its registers, counters and table are 1,048,510 bytes (Section 7), not above 2^20 = 1,048,576; the claim states memory_log2_bytes = 20, the log2 of the 2^20 budget, and the term is 0: the scalar score is 124.91595. (Jbenisek's 1cd0dd3b charged 36 bytes per gate, had 1,912,272 bytes and paid 0.86686 bit; b9f7a2bc introduced the 5-byte price that this entry keeps.)

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bsrho.py --loss` (the function `_lossq`); Appendix A recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
pass 1 of step 6 recomputes the two lengths and pass 2 aligns and walks them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F (F < 1398 <= 2^11 and the key holds its 11 low bits), so equal keys of two DPs differ only if their bits above 157 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds g^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A 47-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B = 0.997381 * 2^128 evaluations numbered t = 1, ..., Q batch by batch and lane by lane inside a batch, b(t) = ceil(t / 256) the batch of t; N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(16 L) = 60851639292013316069988306050030081, S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 89237.66, tmax = 91,483, CMAX = 1 (the program halts when a second trail would be cut). Pi_m = (1 - 0/N')(1 - 1/N') ... (1 - (m-1)/N') is the probability that m independent uniform values of a set of N' elements are distinct. PP = Q (Q - 1) / (2 N') = 0.49738, H = (Q (Q - 1) / 2 + 2^17 Q) / N' = 0.49738. Let k = 91472 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 257, p = e^(-c/L) >= (1 - theta)^c, p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)), and tmax = 91,483. Let F be a uniformly random function on 256-bit values and P_F the success probability of the attempt when every evaluation of g is replaced by F (lazy sampling). Then, with no premise,
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = Pi_Q / (1 - k Q / N') = 0.608119235   (the first collision exists),
    P_delay = (1 - k Q / N')^-1 * sum over the bins (a, b] of [0, Q] of (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = 0.001741   (the merged path needs a DP in the batches that are left; 22,000 bins, Step 5),
    P_own = Q L / N' = 1.115e-05   (the first collision is a cycle of its own trail),
    P_long = M Q p (q + 256) / ((1 - p) N') = 1.796e-06   (its partner is on a trail with c evaluations without a DP),
    P_age = PP p2 = 9.515e-07   (the merged trail is too old when it reaches the DP),
    P_dist = PP L (Q + 2^17) / N' = 5.545e-06   (a later collision on the rest of the merged path),
    P_cut = P(Binomial(n2, p) >= 2) + E_S + E_X + E_J2a + E_J2b + E_Y (Step 6) = 7.718e-05, with E_S = Q L / N', E_X = (Q / N') L e^(-(c-2)/(2L)) (2 + (c - 1)/L) + PP p2, E_J2a = Q L H / N' + (Q + 2^17) L PP / N', E_J2b = PP (1 - theta) p2, E_Y = e^(-(c-1)/L) H,
    P_key = C(tmax, 2) / (2^kb Tp) = 4.36e-05, kb = 36,
    P_table = e^-q (e q / (tmax - 59))^(tmax - 59) = 3.73e-12,
    P_tiny = Q 2^17 / N + k^2 L / N' + 255 Q / N' + exp(-120 + (e^2 - 1) H) + 2^-90 (Step 7; it needs 240 M <= Q, which holds here).
The numbers are printed by `python3 bsrho.py --loss` (the function `_lossq`) and Appendix A recomputes the whole bound in exact rationals and 60-digit decimals (`certify`, outward rounding) and asserts the result >= 0.39: P_F >= 0.390000001000 (the program's float value, planned at the target 0.390000001, is 0.390000001). The program's B is the least multiple of 10^24 for which the float bound reaches 0.390000001 (Appendix A). H1 (Section 5) is the only premise of this entry: it states that the real attempt succeeds at least as often as A_F.

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

Step 3 (a first collision with a good partner is output). Say that the pair (t, y) with tau = t and V_t = V_y is good when (G1) y is not on the trail of t, (G2) b(y) < b(t), (G3) the trail of y is short, (G4) rho(y) <= B - b(t) and a(t) + rho(y) <= c - 1, and that it is undisturbed when no fresh evaluation of the trail of y after t, up to its first DP, is a collision. Claim. On a good undisturbed pair, if the run does not halt early (second cut, table full, stage-1 budget, key false match) and is outside E1 and E2, the program outputs a pair. Proof. Let X and Y be the trails of t and y. The input of X after t is V_t = V_y, the input of Y after y, so the evaluations that X performs after t are the evaluations Y performs after y, the j-th of them in batch b(t) + j for X and in batch b(y) + j for Y (Y does not restart before its DP, because its trail is short, hence never cut, and its first DP is the (rho(y))-th evaluation after y). By (G2) Y evaluates each of them strictly before X, so X only repeats points (they are not fresh). Undisturbed: the evaluations of Y after t are fresh and not collisions (those before t are not collisions, tau being the first), so the lottery of the lane of Y decides the DP: Y ends with a DP at its rho(y)-th evaluation after y, in batch b(y) + rho(y) < b(t) + rho(y) <= B (G4), inside the run, and the key of the DP is stored (the table is not full). X repeats it in batch b(t) + rho(y) <= B with the same DP and the same key; X has then done a(t) + rho(y) + 1 <= c evaluations, so no slice check cut it (a slice check cuts a trail of age >= c, and the age before its last evaluation is a(t) + rho(y) <= c - 1). The two trails are different (G1), finished, with the same key, and the inputs of t and of y are different (t is fresh) with g(t) = g(y): Lemma 1 applies. QED.

Step 4 (the pairs that are not good, and the disturbance). Let W(t, y) be the event (tau = t, V_t = V_y) with xi_t = xi_y = 0 and work on N1 <= k - 1 outside E1 and E2. By Step 2, P(W(t, y) | xi) <= Pi_(t-1) / ((1 - kQ/N') N') <= 1 / ((1 - kQ/N') N'), and sum over t of P(W(t, y) | xi) is at most the sum over t of 1 / N', so at most Q / N'. A pair that is not good fails one of the following; each failure is bounded by the expected number of pairs of that kind times the hazard.
(a) (G1) fails: y is among the a(t) earlier evaluations of the trail of t; a(t) is at most g(t), the number of consecutive 0 coins just before t on its lane (g(t) as in Step 6 (ii)), E g(t) <= sum over i >= 1 of (1 - theta)^i <= L - 1, so the failure has probability at most Q L / N' = P_own.
(b) (G2) fails: y is in the batch of t before t, at most 255 pairs per t: 255 Q / N' (charged in P_tiny).
(c) (G3) fails: y is on a long trail. A long trail has at most M evaluations (it is cut at the first slice check at age >= c, or finishes before), a y has at most Q partners t, and the number of long trails is at most the number of successes of the scan of Step 6 (i) (disjoint windows of c coins 0), with expectation at most p (q + 256) / (1 - p) there: M Q p (q + 256) / ((1 - p) N') = P_long.
(d) (G4) fails. rho(y) > B - b(t) means that the B - b(t) coins after y on its lane are all 0 (they lie in the batches b(y) + 1, ..., b(y) + B - b(t) <= B, inside the run), probability (1 - theta)^(B - b(t)) <= e^(-theta (B - b(t))) for each y. By Step 2 the pairs (t, y) with y < t contribute at most sum over t of (t - 1) Pi_(t-1) / ((1 - kQ/N') N') e^(-theta (B - b(t))), and (t - 1) Pi_(t-1) / N' = Pi_(t-1) - Pi_t, so, with b(t) <= ceil(b / 256) for t <= b and the sum of Pi_(t-1) - Pi_t over t in (a, b] equal to Pi_a - Pi_b, at most (1 - kQ/N')^-1 sum over the bins (a, b] (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = P_delay (the bins and the enclosures of Pi are in Appendix A). The second part, a(t) + rho(y) >= c: a(t) <= g(t) and rho(y) >= 1, so it requires g(t) + (rho(y) - 1) >= c - 1. If t and y are on different lanes the two coin sets are disjoint and g(t), rho(y) - 1 are dominated by independent geometric variables with values in 0, 1, 2, ...; the sum of two such variables is at least c - 1 only if a single i.i.d. sequence of coins has at most one 1 among its first c coins, hence among its first c - 1 coins: probability at most (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. If they are on the same lane and (G1) and (G3) hold, y is on an earlier trail of the lane that is short, so it ended with a 1 before the start of the trail of t, and the two coin sets (those of rho(y) up to that 1, those of g(t) after it) are disjoint: the same bound. At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': PP p2 = P_age.
(e) Disturbance. For a good pair let r' be the number of evaluations of the lane of y with index > t up to and including the first with xi = 1; the coins there are independent of F_t (L5, t is a stopping time) and r' is dominated by a geometric variable of mean L. The evaluations of Y after t and before its DP are at most r' fresh evaluations, each a collision with conditional probability at most (Q + 2^17) / N' given the history (L1; the last one, a DP-valued evaluation, is covered by E2, and counting it here only overcounts). For this bound W(t, y) is taken without the restriction to N1 <= k - 1 and outside E1, E2: it is the event (tau = t, V_t = V_y), which is F_t-measurable, so P(W(t, y) and disturbed) <= P(W(t, y)) L (Q + 2^17) / N'; the events W(t, y) for different (t, y) are disjoint (the values V_y are distinct before tau), so the sum of P(W(t, y)) is at most P(tau <= Q) <= sum over t of (t - 1)/N' = PP: PP L (Q + 2^17) / N' = P_dist.

Step 5 (the sum). With P(tau <= Q, N1 <= k - 1) >= 1 - Pi_(Q-k+1) - 2^-40 >= 1 - P_coll - 2^-40 (Pi_(Q-k+1) <= Pi_Q / (1 - kQ/N'): n0(Q) >= Q - k + 1 on N1 <= k - 1 and Pi decreases) and Step 3, the attempt succeeds unless one of the failures (a) to (e) occurs for the first collision, or E1, E2, N1 >= k occur, or the run halts early: P_F >= 1 - P_coll - 2^-40 - P_own - P_long - P_delay - P_age - P_dist - 255 Q / N' - P(E1) - P(E2) - P(early halt). The early halts are charged in Step 6 (second cut) and Step 7 (table full, key false match, stage-1 budget).

Step 6 (the cut count and the long trails; no premise). Let K be the number of trails that the run cuts or would cut (the second one halts the run). Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.
(i) K_A. A trail counted by K_A has c fresh evaluations with non-DP outputs at c consecutive positions of its lane, so xi = 0 there; different such trails of a lane use disjoint positions. Scan each lane with trials: a trial starts at the current position u and succeeds if the c positions u, ..., u + c - 1 are all 0 (next trial at u + c); otherwise it fails at its first 1 (next trial after that 1). The scan of a lane stops at the first trial that would start after the run. Inside a maximal run of 0s the trials start at its first position and succeed floor(length / c) times, the largest number of disjoint length-c windows it holds; so K_A on a lane is at most the successes on that lane. Every failure but the last of a lane ends at a 1 of the run, so the failures are at most N1 + 256 <= k - 1 + 256 on N1 <= k - 1. Trial outcomes are independent Bernoulli(p'), p' = (1 - theta)^c <= p = e^(-c/L) (disjoint positions of an i.i.d. lottery; lanes concatenated as in (L3)). All successes therefore occur before failure number k + 256 of an infinite i.i.d. trial sequence, and two successes before that failure mean two successes among the first n2 = k + 257 trials:
    P(K_A >= 2, N1 <= k - 1) <= P(Binomial(n2, p) >= 2) = 1 - (1 - p)^n2 - n2 p (1 - p)^(n2 - 1)
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
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; E[g(t) + 1] <= sum for i >= 0 of (1 - theta)^i = L, so E_S <= Q L / N' = 1.115e-05.
- X: E_X <= sum over pairs e' < t of P(sigma(e') + g(t) >= c) / N'. Different lanes: sigma(e') - 1 and g(t) are independent and dominated by geometric variables on {0, 1, ...}, so the probability is at most P(at most one 1 in c - 1 Bernoulli trials) = (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. Same lane, e' = t - j 256: if a 1 lies between them the two runs of 0s are disjoint and the same bound p2 holds; if the j positions are all 0, the probability is at most (1 - theta)^j T(c - 1 - 2j) with T the tail above (T = 1 below 1); the sum over j of these is at most L e^(-(c - 2)/(2L)) (2 + (c - 1)/L). Hence E_X <= (Q / N') L e^(-(c-2)/(2L)) (2 + (c-1)/L) + PP p2 = 1.019e-06.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^17) / N': E_J2a2 <= (Q + 2^17) L Q (Q - 1) / (2 N'^2). E_J2a = 1.109e-05.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2 = 9.515e-07.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 5.597e-08.
So P(K >= 2) <= P(K_A >= 2, N1 <= k - 1) + P(N1 >= k) + P(K_B >= 1) <= P(Binomial(n2, p) >= 2) + E_S + E_X + E_J2a + E_J2b + E_Y + [P(N1 >= k), charged once as 2^-40]; P(Binomial(n2, p) >= 2) = 5.291e-05 and P_cut = 7.718e-05 (the program's `cut_halt`). There is no premise about K: the number of cut trails is bounded by this argument, and it needs no distribution of K. The bounds on S and J2a are not small (about Q L / N' each); they are the real cost of trails that close a cycle or join a path that is itself disturbed.

Step 7 (the early halts and the small terms). The attempt can end before it outputs the pair of Step 3 only by an early halt or by the events E1, E2, N1 >= k: the second cut (P_cut, Step 6); the table full (finished trails are at most N1 + 59 outside 60 or more collisions, so tmax keys need N1 >= tmax - 59: P_table = 2.90e-12); a key false match (P_key = 4.36e-05: the stored ends are at most tmax fresh DP values, uniform on the DP class, and the key space is 2^36 * 1398 = 2^46.45); the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^32 = 7.90e+28: the fresh stage-1 hits are at most the sum of eta_t = 1[low 32 bits of V_t zero], exactly Binomial(Q, 2^-32), above 1.5 mu2 with probability at most e^(-0.108 mu2); the repeated hits after merges come from at most 60 colliding trails, each repeating at most M points that lie in at most 60 lane windows of total length at most M, and every such union of windows holds more than 2 M / 2^32 hits with probability at most e^(-0.386 M / 2^32), so with 240 M <= Q (checked: M = 6.085e+34, Q = 3.394e+38) the repeated hits are below mu2 / 2 except with probability below e^-1000; a recovery with no pair (a key false match, counted, or a start on another trail, 2^-100). The number of collisions: every fresh evaluation with xi = 0 is a collision with conditional probability at most (t - 1 + 2^17) / N' (L1), so E w^(number of collisions) <= exp((w - 1) H) for w = e^2 (the factor per evaluation is at most 1 + (w - 1)(t - 1 + 2^17)/N' <= e^((w-1)(t-1+2^17)/N')), and P(60 or more collisions) <= exp(-120 + (e^2 - 1) H). P_tiny collects Q 2^17 / N (E1), k^2 L / N' (E2), 255 Q / N' (Step 4 (b)), exp(-120 + (e^2 - 1) H), and 2^-90 for everything else of this step (the stage-1 budget, the recovery with no pair) and for the rounding of the factors 1 - kQ/N' and of the enclosures of Pi (each below 2^-96). This proves the lemma. QED.
Consequently P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny = 1 - 0.608119257 - 0.001740569 - 1.115e-05 - 1.796e-06 - 9.515e-07 - 5.545e-06 - 7.718e-05 - 9.1e-13 - 4.356e-05 - 2.90e-12 - 2^-90 = 0.390000001 (float, planned at 0.390000001; the printed terms are rounded), and the exact certificate of Appendix A is 0.390000001000 >= 0.39 (B is the least multiple of 10^24 that reaches the planning target).

Sensitivity to H1 (d). If the hazard of a collision is (1 - eps) / N instead of 1 / N (clause (d) of H1; the same sensitivity as a deficit eps of the pair-collision rate in clause (a)), the plan of this program (same lemma with N / (1 - eps)) needs, to restore 0.39: 0.0073 bit for eps = 0.01 (Tp 1391); 0.0370 bit for eps = 0.05 (Tp 1363); 0.0760 bit for eps = 0.10 (Tp 1326); 0.2075 bit for eps = 0.25 (Tp 1211).

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function g and about one attempt; it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved: an assumption, no proof is known. Its content, in the terms Lemma 2 uses, is four clauses: (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of g from the starts r + t have the first-collision law of a random mapping; (c) whether an iterate is a DP is independent of the collision events and has probability 1398 / 2^122; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of g; clause (d) is that this adaptivity does not lower the collision hazard, that is, for every fresh evaluation, given the whole history of the run and which later outputs are distinguished points, the output equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard that F has by construction, L1 of Section 4). Clause (d) replaces the fixed-U birthday step of the earlier Lemma 2, which the judges asked to be either proved or declared (41b32afc, finding F1-adaptive-finished-trail-conditioning, aggregate heuristic H4); it is both: Lemma 2 now proves the bound for F from the hazard alone (the first collision of the run and the detection delay, no conditioning on which trails finish), and (d) is the premise that g has that hazard. Nothing else in the success bound is heuristic: Lemma 1, the lazy-sampling facts, the first-collision bound, the Chernoff bounds and the cut count are proved in Section 4 for F; Sections 3 and 7 are counts of the program. Sensitivity: a hazard (1 - eps) / N costs the same as a deficit eps in clause (a): 0.0073 bit for eps = 0.01, 0.0370 bit for eps = 0.05, 0.0760 bit for eps = 0.10, 0.2075 bit for eps = 0.25 (Section 4). The only evidence for (a) to (d) is the 18-bit and 21-bit program checks of Section 6, which do not reach the full 256-bit event and are not used as estimates.
Evidence that the program is right and that nothing gross is wrong is produced by the two organizer experiments (Section 6). They are program checks: the organizer recomputes every returned pair, the counts of returned pairs are reported, and they are not used as estimates of any number of this entry. No quantitative inference is drawn from a count, no confidence interval is formed, and the entry does not rely on the independence of trials (the trial seeds are public and the experiment is a check of the program). A prior descriptive run on seeds derived from SHA-256 of a counter produced the following untrusted observations (they are identical to b9f7a2bc's counts: the walk g, the seeds and the search are the same, only the circuit that evaluates g changed):
    T3 n=18: attempts returning a verified pair: target 167 of 256, ideal function 182 of 256
    T1 n=12 fresh K: 256 runs, mean first repeat 81.97 (sqrt(pi N/2) = 80.21)
    T2 width 256, K=0: 2048 points, 21-bit projections, equal pairs per trial if uniform 0.9995, trials with a pair if uniform 0.6319
      source uniform (86 trials): returned pairs 53 (uniform reference 54.3); w0 82 (uniform reference 86.0); w3 74 (uniform reference 86.0); w7 82 (uniform reference 86.0); xor8 63 (uniform reference 86.0); sum8 78 (uniform reference 86.0); p01 88 (uniform reference 86.0); p23 64 (uniform reference 86.0)
      source counter (85 trials): returned pairs 51 (uniform reference 53.7); w0 75 (uniform reference 85.0); w3 85 (uniform reference 85.0); w7 94 (uniform reference 85.0); xor8 77 (uniform reference 85.0); sum8 90 (uniform reference 85.0); p01 69 (uniform reference 85.0); p23 90 (uniform reference 85.0)
      source iterates (85 trials): returned pairs 53 (uniform reference 53.7); w0 83 (uniform reference 85.0); w3 85 (uniform reference 85.0); w7 88 (uniform reference 85.0); xor8 80 (uniform reference 85.0); sum8 80 (uniform reference 85.0); p01 92 (uniform reference 85.0); p23 99 (uniform reference 85.0)
The organizer's pipeline ran this program on the public seed and reran each experiment; its attached report holds the checked trials and results, and this proof quotes none of its counts.
At width 18 a halt "recovery found no pair" (a trail start lying on another trail) is frequent; at width 256 it has probability below 2^-100 (Section 4). It happens equally for the ideal function.
Not tested: the full 256-bit functional graph; iterations of length above 2^40; other values of K; the bit-sliced search above width 18. A deviation of g from H1 that raises the collision rate only helps; one that lowers it by eps costs the extra time of Section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/bsrho.py` (the program dispatches on the experiment id; no outside code or library is used; the standard library only).
`bsrho-n18`: per trial, from the trial seed, one attempt of the 256-lane search at width n = 18 (DP = low 2 bits zero, plan(18): 8 batches, cut rule, table, recovery on the packed circuit) on the target chain g (K = 0: the block 0^32 || x, the low 18 bits of g); the trial returns the two 64-byte messages 0^32 || x, 0^32 || y when the attempt succeeded and two nulls otherwise. The checked event is that the complete 7-round digests agree in the low 18 bits and the messages are distinct. Observations (untrusted): the same attempt on the ideal function, and one family-law run with a fresh key at n = 12.
`proj-k0-w256`: per trial, 2048 points of the K = 0 target at width 256 evaluated with the bit-sliced circuit (source by trial index mod 3), returning two points whose digests agree in the low 21 bits when the set contains such a pair. The digests are recovered from the stored planes by XOR with q before the projections are formed. The checked event is that the digests agree in the low 21 bits and the messages are distinct. Observations (untrusted): equal-pair counts of seven projections.
They check the circuit at full width, the bit-sliced search, lane insertion and extraction, the table, the recovery, q, and the message construction on the real target. They do not measure full-width attack cost or success probability. Organizer intake ran 256 trials for each experiment twice in fresh one-CPU, 128-MiB containers. Both stdout pairs were byte-identical. The organizer recomputed every returned event: 174 of 256 reduced-width trials and 160 of 256 projection trials returned valid distinct pairs. The success counts are implementation evidence only, not iid probability estimates.

## 7. Memory

Table: 91,483 entries * 8 bytes = 731,864 bytes. Each entry packs a 47-bit key and 17-bit trail number in one 64-bit slot. Four slots fit in one 256-bit word. Lengths are recomputed during recovery and are not stored.
Code: 45,882 register-format words * 5 bytes (44,310 step gates, 32 stage-1 operations, 1,540 recovery operations) plus 1,257 other instructions * 36 bytes = 274,662 bytes. The canonical listing and its hash are in Section 3.3.
Counters and copies use 16,384 bytes. The 800 counted registers use 25,600 bytes. There is no advice. Search memory is 274,662 + 731,864 + 16,384 + 25,600 = 1,048,510 bytes, 66 bytes below 2^20. Setup uses 445,186 bytes, including the register file and the generator globals and tables listed in Section 3.6. The claim rounds `memory_log2_bytes` up to 20, so the scalar memory term is zero.
The table size is the largest that fits: tmax = floor((1,048,576 - 64 - 274,662 - 25,600 - 16,384) / 8) = 91,483, with the 1,048,576-byte budget 2^20. A larger table lowers the time, so the budget is used in full. Tp = 1398 is the largest integer for which the success bound of Section 4 reaches 0.39 at the largest mean number of trails that the table holds with capacity tail below 2^-40 (Appendix A computes both).

## 8. Heuristics, conventions and what is credited

The premises of this entry are: H1 (the model premise of Sections 4 and 5, clauses (a) to (d), score-critical) and H3 (the 800-register machine convention and the instruction charges, 5 bytes per register-only gate and 36 bytes per other instruction, supporting). There is no prefix, no advice and no polarity climb; the entry has no two-block mode.
Credited to f88f3751-f08b-4561-a764-a04b5f7a899a: the pair-carry representation, general nine-gate templates, their generator integration, and the complete inherited construction. Credited through it to b9f7a2bc-2ba7-4a34-a4c0-8efa7527fba1: the relation, walk, bit-sliced search, five-byte instruction format, plan, handlers, recovery, ledger method, Lemma 2 and its certificate, experiments, and proof structure. Through b9f7a2bc we also credit jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 for the pivot full adder and mask walk, TheTradoor's 09fe5fcd-5614-4329-8b7d-48957c238fac for the 64-bit table slot, b1e6de75-6ea4-4946-82ad-addc9a6b909e for the 47-bit key, and Jbenisek's a2e94df7-bff4-4461-ad40-7f75930cb241, 1cd0dd3b-eb60-4572-a75f-937cd771ec4a, a6ee439c-5b82-41f2-8acb-9917c8c70756, 41b32afc-ed4c-4ef1-b9f2-8c72ab163582, 75d5e1f9-8948-4f49-b7a6-5e9475495a7a, 62cfd777-5613-463f-b561-e2340e00e528, 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c, 3356413f-cd60-410c-8847-2266d6444ac5, cf8b0e92-4302-4813-907a-3c970c102646, and e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.

Our contribution is limited to the SAT encoding and two checked mask-0x10 circuits, their generator integration, independent C generation and complete-digest checks, the emitted full-program accounting, and the re-planned ledger. The unrestricted UNSAT run is only the disclosed development observation of Section 3.2. The pair encoding itself remains f88f3751's credited use of the modified double full adder encoding of Demenkov, Kojevnikov, Kulikov, and Yaroslavtsev.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point bound only selects B and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 bsrho.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, expm1, log1p

PH, STEPI, FILT, LOOP, LANES = 44310, 44310, 34, 3, 256   # operations executed by one step, instructions of its code, stage-1 test, batch loop control, lanes
GEN_CALLS = 921976                              # generator primitive calls, both passes, column trials included (the C port; 2 x 460,988 in python3 bsrho.py --ledger)
PH7, EXTRA, PASSES = 1540, 64, 2                            # packed recovery circuit, extra operations per recovery batch
TB, KEYB = 17, 47                                  # trail-number bits and key bits of a table entry (64 bits = 8 bytes)
N_BITS, S1, W, KAPPA = 256, 32, 90, 16          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 1
MEM_LIMIT = 1048576                                       # bytes: 2^20
GATE, INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 5, 36, 1219, 800 * 32, 16384, 8, 0, 64   # handlers 1000 + setup 160 + recovery control 59
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN = 10 ** 24                                # B is a multiple of GRAIN
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP                                        # one batch = 44,347 operations
NCONST, S1BR = 33, 2                            # recovery constants loaded once into registers (36 bytes each); compare and branch of the stage-1 test
code_bytes = (STEPI + FILT - S1BR + PH7) * GATE + (LOOP + OTHER_CODE + S1BR + NCONST) * INSTR     # register-format instructions at 5 bytes, all others at 36
tmax = (MEM_LIMIT - SPARE - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY  # table entries that fit in MEM_LIMIT bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


def plower(Tp, q):            # the lower bound of Lemma 2 on the success probability, q = Q / L (floats; certify() below is the proof)
    L = Fraction(1 << D, Tp)
    c = -(-KAPPA * L.numerator // L.denominator)
    th, Lf, cf = Tp / 2.0 ** D, float(L), float(c)
    Q, B, Np = q * Lf, q * Lf / LANES, 2.0 ** N_BITS
    k = int(q) + 1
    while tail_log2(q, k) > -40:                               # N1 ~ Binomial(Q, theta) <= k - 1 except with probability 2^-40
        k += 1
    n2, shift = k + LANES + 1, 1 / (1 - k * Q / Np)
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
    t = [pi(Q) * shift, delay * shift, ql, (cf + SB) * Q * p * (q + LANES) / ((1 - p) * Np), hq * p2, hq * Lf * (Q + 2.0 ** TB) / Np, 2.0 ** -40,
         -expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p)) + ql * (1 + (2 + KAPPA) * exp(-KAPPA / 2) + 2 * hq) + hq * p * (3 + 2 * KAPPA),
         tmax * (tmax - 1) / 2 * 2.0 ** -(min(KEYB - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp)), 2.0 ** tail_log2(q, tmax - 59),
         Q * 2.0 ** TB / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -120 + (exp(2) - 1) * hh)) + 2.0 ** -90]
    return 1 - sum(t)


def plan_tp(Tp):              # the least B (a multiple of GRAIN) with plower >= 0.39
    L = Fraction(1 << D, Tp)
    lo, hi = 1.0, tmax + 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if plower(Tp, mid) >= P_MIN else (mid, hi)
    b = -(-int(hi * L / LANES) // GRAIN) * GRAIN
    b += GRAIN                                                   # stay one public grain above the floating transition
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
    n2 = k + LANES + 1
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
             up(1 - (1 - p) ** n2 - n2 * p * (1 - p) ** (n2 - 1)),   # step 6: fresh cut trails, P(Bin(n2, p) >= 2)
             fd(Q * L / Np, True),                               # S
             fd(Q / Np, True) * fd(L, True) * ex(-(c - 2) * th / 2) * fd(2 + (c - 1) * th, True) + fd(PP, True) * p2,   # X
             fd(Q * L * H / Np + (Q + (1 << TB)) * L * PP / Np, True),   # J2a
             fd(PP * (1 - th), True) * p2, ex(-(c - 1) * th) * fd(H, True),   # J2b, Y
             fd(Fraction(tmax * (tmax - 1), 2 * Tp) / (1 << min(KEYB - (Tp - 1).bit_length(), N_BITS - D)), True),   # key false match
             up((-qd + (tmax - 59) * (1 + (qu / (tmax - 59)).ln())).exp()),   # table capacity
             fd(Fraction(Q << TB, Nn) + Fraction(k * k) * L / Np + 255 * Q / Np, True) + up((-120 + (Dm(2).exp() - 1) * fd(H, True)).exp()) + Dm(2) ** -99]
    assert Fraction(Q, 1 << 32) * Fraction(108, 1000) > 1000 and 240 * M <= Q   # stage-1 budget (Step 7): below e^-1000, inside the last term
    return 1 - sum(terms)


lo, hi = 1.0, tmax + 1.0                                       # the largest mean number of trails the table holds (tail within 2^-40)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
Tp = next(t for t in range(1500, 0, -1) if plower(t, lo) >= P_MIN)  # the largest Tp that reaches 0.39 at that mean
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + STEPI)
rows = [("main loop: B * 44347", body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: (tmax + 1) * (3800 + 3 * tmax)", (tmax + 1) * (EVENT + 3 * tmax)),
        ("cut trails: 1 * 4200", CMAX * CUTOPS),
        ("recovery: (2 * (c + 2^48) + 1) * (1540 + 64) + 600 + 33", (PASSES * capr + 1) * (PH7 + EXTRA) + 600 + NCONST),
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
P, C = 100000, 1470
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
Tp = 1398  tmax = 91483  B = 1325746535010000000000000000000000000  e2max = 158041302562952041625976562564  c = 60851639292013316069988306050030081
memory bytes = 1048510
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000001000
main loop: B * 44347                                 58792881588088470000000000000000000000000
slice checks: ceil(B / 2^48) * 1300                  6122997204418112460189800
stage-1 hits: e2max * 2800                           442515647176265716552734375179200
finished trails: (tmax + 1) * (3800 + 3 * tmax)      25455331516
cut trails: 1 * 4200                                 4200
recovery: (2 * (c + 2^48) + 1) * (1540 + 64) + 600 + 33 195212058848778717953425457533784286533
setup and generator                                  194070800
N = 58988094089452902017216346428406269062049
certificate: 2^12491594 * 1470^100000 <= N^100000 < 2^12491595 * 1470^100000
log2(N/C) = 124.9159471521
time_log2 = 124.91595
```
