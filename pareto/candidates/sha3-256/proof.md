# SHA3-256 with 23 prefix rounds: distinguished-point collision search with a linear-structure message embedding, a 136,662-operation bit-sliced step and an index-file table of five key slots per word, time_log2 124.45691

## 1. Claim

Target `sha3-256-r23-prefix-v1`: SHA3-256 (FIPS 202) with Keccak-f rounds 0 to 22 in the single permutation call, zero initial state, rate 136 bytes, suffix 0x06 with pad10*1, and the full 256-bit digest. The algorithm outputs two distinct 128-byte one-block messages with equal complete digests (an ordinary collision).

| Quantity | Value |
|---|---|
| time_log2 (collision-frontier-v5, unit 6233 word operations, rounded up) | 124.45691 (Sections 4 and 5, certificate in Appendix A) |
| memory | at most 1,048,424 bytes <= 2^20 (margin 152 bytes), memory_log2_bytes = 20 (Section 6) |
| score: time_log2 (memory reviewed separately) | 124.45691 |
| success probability | at least 0.39 for one attempt, under the premise H_rand (Section 5) |
| preprocessing | the generator run `gen3 512 1000 8`, the parameter scan and the assembly of the other code (Section 3.7; the charge K of the constant basis stays in PRE, though design X does not run the basis), charged 1,037,604,497,543,936 word operations inside N; preprocessing_log2 = 38; no advice |

The method is a distinguished-point parallel collision search (van Oorschot-Wiener) on a chain function F, with 256 walks per step. It has three parts.

1. **Embedding.** The 256-bit point is spread over ten message lanes by design X of mpjunior92's entry 11565cb4, so that round 0 of the permutation and the theta step of round 1 are affine in the point (a one-round linear structure in the sense of Guo, Liu and Song, 2016) and column 3 of round 1 is constant. With constants folded, those steps cost a few thousand word operations instead of one round each.
2. **Step program.** One step of the 256 walks is a bit-sliced straight line of 136,662 register operations. It follows the step design of jungjipdo's entry 67f781f8 (theta evaluated lazily per chi row, per-row complement subsets, dead-code elimination, last-use register allocation, the digest written over the input, a declared register file and its instruction format of a 3-bit opcode and three 12-bit registers) and adds four things of ours (Section 3): a 10-gate chi row, a polarity plan for the NOTs, an exact search over the round-1 rows that have a constant input (Section 3.3), and a generator that writes the program round by round as it builds it, so that its own memory stays far below 2^20.
3. **Search.** The search is the one of our entries 0dc77160 (SHA3GENV4B_R23, sha3-256 Pareto round 23) and 90753795 (F1023094554, round 23, 124.46582): lockstep walks with a restart on each distinguished point, a replay of the colliding pair, and the success bound of Section 5. The search keeps from 90753795: a distinguished-point probability theta that is not a power of two (Section 4), no trail cut with the replay refusing trails of more than LRC evaluations (failure term F6, Section 5) and the success bound. This package keeps the one-round-lookahead polarity plan (Section 3.3), the search, the distinguished-point rule and the other code (apart from its message builder) of 90753795 and changes 5 things: the message embedding is design X of mpjunior92 entry 11565cb4: the point is spread over ten lanes (lanes x and 10 + x carry v_x xor constants, with v_4 a fixed XOR of rotations of u0..u3), lanes 5 to 9 are all-ones and lane 15 zero, so every column sum of round 0 is constant, round 0 is affine and column 3 of round 1 is constant; the constants K_0..K_4 of the 512 trials are drawn by xorshift (Section 2); the round-1 rows that have a constant input are decided by an exact search: in at most two sweeps each such row tries every complement subset of its variable inputs with every 10-gate choice, and a flip of each of its five term polarities, building rounds 0 and 1 each time and keeping a change that lowers 16 x (the operation count of rounds 0 and 1) + 3 x (the least row costs of round 2 over its input patterns); here rounds 0 and 1 drop from 3,238 to 3,187 operations and the round-2 estimate from 1,930 to 1,821 (Section 3.3); the message builder of the other code (in evalF and in the output of the pair) writes the design X state, 44 instructions with its return instead of 27, so one evaluation in the replay costs e = 6,279 and the success exit 101 (Sections 4.2 and 4.3); the plan anneals 150,000,000 iterations per round instead of 600,000,000, so that the generator run stays below 15 minutes (Section 3.3); and the program names 2,025 registers and the declared file has 2,036 registers instead of 2,034 (Section 3.6).

claim.json declares three heuristics. H_rand (Section 5) is the one score-critical premise. H_reg (register file) and H_code (code-memory encoding) are machine conventions of the cost model with role supporting (Section 3.6).

## 2. The function F and the encoding

Let u be a 256-bit point with little-endian 64-bit lanes u0, u1, u2, u3. The message m(u) has 128 bytes, the 16 lanes 0 to 15 of the absorbed state (lane index x + 5y):

- v_x = u_x for x = 0..3 and v_4 = rotr(u0, 36) xor rotr(u1, 29) xor rotr(u2, 60) xor rotr(u3, 14) (the rotations (39 - ROT[x][2]) mod 64, ROT the rho offsets);
- lane x = v_x xor K_x and lane 10 + x = v_x xor K_(10+x) for x = 0..4 (rows y = 0 and y = 2 of column x), with K_(10+x) = K_x xor 0x5555555555555555, and for x = 1 also xor 0x8000000000000006 (the padding lane 16);
- lanes 5 to 9 are all-ones and lane 15 is zero.

This is the design X embedding of mpjunior92's entry 11565cb4 (Section 8).

With the SHA3 padding, byte 128 is 0x06 and byte 135 is 0x80: one absorbed block, lane 16 = 0x8000000000000006, lanes 17 to 24 zero. Rounds 0 to 22 are applied and the digest is lanes 0 to 3 of the result (32 bytes). Define

    F(u) = SHA3-256-r23(m(u)) xor PD

where PD is a fixed 256-bit mask (the polarity of the program's digest planes, Section 3.4). The map u -> m(u) is injective (lanes 0 to 3 are u xor constants), so F(a) = F(b) with a != b gives two distinct messages m(a), m(b) with equal complete digests. XOR with a fixed mask is a bijection of the range, so F is a fixed function from 256 bits to 256 bits like the plain digest map.

Constants (hexadecimal). The generator chose them as trial 1106, one of the 512 constant sets of trials 1000 to 1511 (trial t: K_0..K_4 are the 11th to 15th outputs of the 64-bit xorshift generator of gen3.c started at 0x9E3779B97F4A7C15 x t + 1 mod 2^64, the other lanes follow from the rules above); the selection run is charged in N as preprocessing (Section 3.7):

```
K0  e7f61a326551f37e  K1  4893e125f5b84f18  K2  5685826a2aaff986  K3  4a6602d9a5de07f5
K4  13340fdb6c9ee6ba  K5  ffffffffffffffff  K6  ffffffffffffffff  K7  ffffffffffffffff
K8  ffffffffffffffff  K9  ffffffffffffffff  K10 b2a34f673004a62b  K11 9dc6b470a0ed1a4b
K12 03d0d73f7ffaacd3  K13 1f33578cf08b52a0  K14 46615a8e39cbb3ef  K15 0000000000000000
PD (lanes 0..3) 9bfefcf268f945ec 1d010a181d878610 400103091f06ba12 4400010502003802
```

**Why round 0 is affine and column 3 of round 1 is constant** (the argument of 11565cb4; each statement below is checked on these constants by GF(2) affine forms when the package is made).
- *Theta of round 0.* Column x sums lanes x, 5 + x, 10 + x, 15 + x and 20 + x: (v_x xor K_x) xor all-ones xor (v_x xor K_(10+x)) xor (lane 16 for x = 1) = 0xaaaaaaaaaaaaaaaa for every x, since the v_x cancel in pairs. So every D of round 0 is all-ones and theta complements every lane.
- *Chi of round 0.* rho and pi move row y = 0 to position 0 and row y = 2 to position 2 of the chi rows; positions 1, 3 and 4 hold constants (0, all-ones except where lane 16 lands, all-ones). Each product (not b[X+1]) and b[X+2] has a constant factor, so chi of round 0 is affine in u, and its outputs at positions 3 and 4 are constants.
- *Round 1.* The rotations in v_4 make rotl(v_0, 3) xor rotl(v_1, 10) xor rotl(v_2, 43) xor rotl(v_3, 25) xor rotl(v_4, 39) = 0, so the column sum C[2] after round 0 is constant, as is C[4]; then D[3] of round 1 is constant and the whole column x = 3 of round 1 is constant: every chi row of round 1 has a constant input (317 rows with one constant input, 3 rows with two constant inputs). Round-1 theta is affine.
- *Degrees of freedom.* 640 bits in ten lanes, minus 320 for the cancelling column pairs, minus 64 for the relation, leave 256: the point u.

The generator tracks each value as a GF(2) affine form in the 256 input bits as long as it is affine, emits an operation only when the form is new, and stops tracking forms at the first nonlinear operation (chi of round 1). The search uses no algebraic property: F is only evaluated.

## 3. One step of 256 walks: the straight line

### 3.1 Planes, polarity, gates

A batch is 256 walks. Plane (lane, z) is one 256-bit word whose bit t is bit z of that lane for walk t. The rotations of rho and the moves of pi rename planes and cost nothing.

Each value is held as a register and a polarity p: the logical value is the register word xor p, all-ones or zero. NOT and XOR with a constant flip p for free; constants are folded and never stored. The operations, each one word operation, are:
- XOR: one operation;
- logical a AND b: one AND when both polarities are 0, one OR with output polarity 1 when both are 1, and two operations otherwise, either A xor (A and B) (output polarity 0) or (not A) or B (output polarity 1);
- NOT: one operation, used for the row complements of 3.2 and the theta and output complements of 3.3.

Equal operands fold, and a binary operation on the same pair of registers is emitted once (hash-consing).

### 3.2 Rounds

For each round r = 0..22, with the round constant of the profile:

1. Column sums C[x][z] (the five planes of the column, folded) and D[x][z] = C[x-1][z] xor C[x+1][z-1], computed slice by slice with C[.][63] first, so that few C values are live at once.
2. The chi rows, in order Y = 0..4 and z = 0..63. Each row XORs D into its five inputs b[X] = A[x][y][z - rho(x,y)] xor D[x][z - rho(x,y)] (x = 3Y + X mod 5, y = X) when the row is computed (lazy theta).
3. **Row decision.** chi computes out[X] = b[X] xor ((not b[X+1]) and b[X+2]). Before it, the generator may NOT some of the five inputs (a complement subset s, one operation each), and it may compute one output j from the finished output k = j + 1 of the same row (the **10-gate row**): wherever b[k+1] = 1, out[k] = b[k] xor ((not 1) and b[k+2]) = b[k]; wherever b[k+1] = 0 both sides below are 0; so

        (not out[k]) and b[k+1] = (not b[k]) and b[k+1],

   and the term of output j may read out[k] in place of b[k]. The polarity of out[k] is set by its own term, so the odd five-cycle of equal polarities, which forces at least one two-operation term in a plain row, is broken. For rows with five distinct variable inputs the decision depends only on the five polarities and is read from a table made once (Appendix B, `mk_tables2`, `eval_row`): for each polarity pattern it evaluates the 32 subsets and every trick set T (bit j of T: out[j] reads the finished out[j+1]; T is acyclic, so not all five), computing the outputs in an order where out[j+1] is finished before out[j], and keeps the first cheapest (the **chained** form; the mechanism of 0xplemonade's entry 4ea0966b). The table has a second kind of entry: after the five outputs are computed, a subset E of them may be complemented, one NOT per output (E = 0 is the entry above); for each input pattern and each requested output vector `mk_tables2` keeps the cheapest decision together with its E (Section 3.3). The identity above holds for each link of a chain because out[j+1] is finished when out[j] reads it. Other rows evaluate the 32 subsets and the six choices j in (none, 0..4) and keep the first cheapest (`row_choose`). In this program 6,396 rows use the 10-gate form.
4. iota flips the polarity of the lane-0 planes where the round constant has a 1.

**The last round** computes only row Y = 0 and the outputs X = 0..3 (the digest lanes); the 10-gate form is used there when both outputs j and j + 1 are needed.

**Dead-code elimination** removes every operation on which no state plane of the next round (no digest plane, in the last round) depends.

### 3.3 Polarity plan

With AND, OR and XOR, the polarity of every value follows from the operations that built it, so the row costs of 3.2 depend on NOTs placed earlier. Four kinds of choices move polarities at a known cost:

- a NOT on a column sum C[x][z] costs one operation and flips the polarity of the 10 chi inputs it reaches through D;
- the D of a lane (x, z) reaches five chi inputs, one in each of the five chi rows (row y takes the plane of row y of column x). For a lane whose 5-bit mask F[x][z] is not 0 the generator builds D' = NOT D, one operation, and chi input y of the lane reads D' when bit y of F[x][z] is 1 and D when it is 0. The mask 31 complements all five inputs, any other nonzero mask only some of them, for the same one NOT. At most 100 lanes of a round have a mask other than 0 and 31;
- a two-operation term has a free output polarity (A xor (A and B) or (not A) or B, two operations either way), which flips its output plane and, through the theta of the next round, 11 chi inputs there;
- an output complement: a planned row (below) may complement a subset E of its five outputs after computing them, one NOT per output, which flips those planes and the chi inputs they reach in the next round.

**The last round** (row Y = 0, the four digest outputs) is planned alone. A simulated annealing (150,000,000 iterations, deterministic xorshift, temperature 1.2 e^(-3.178 i / 150,000,000) at iteration i) chooses its C NOTs, its whole-lane D NOTs (mask 31 or 0) and the free output polarities of the two-operation terms of the round before it, against the exact cost table of the row decision of 3.2 (the cheapest decision for each of the 32 input-polarity patterns, made by the same function the build uses), minimising the row costs plus the NOTs. A free polarity that a 10-gate row needs is fixed by that row and is not offered to the plan.

**Rounds 2 to 21: one round of lookahead (as in 90753795), with D masks and output complements.** In each of these rounds this generator (optmode 5, `polopt2` in Appendix B) anneals a larger state: the C NOTs and the D masks of the round and, for each of the 320 chi rows of the round, the polarity vector of its five outputs. The cost is 16 x (the row costs of the round for the chosen outputs + the NOTs, one for each C NOT and one for each lane with a nonzero mask) + 3 x (for each row of the next round, the least row cost over its input-polarity pattern, which the chosen outputs fix through iota and theta, plus 5; when the next round is the last, the exact cost of its four needed outputs). Row costs come from a table made once by the same row function (`mk_tables2`, Appendix B): for each of the 32 input patterns and each of the 32 output vectors, the cheapest decision that gives those outputs, namely a complement subset, a trick set, the mixed-term polarities and an output complement E whose NOTs are counted in the row cost (the tables ROWCt, ARGt and ARGE). A move changes the mask of one lane (it flips one bit of the mask or draws a new mask; probability 1/5), flips one C NOT (1/5), or changes bits of one row's output vector (3/5); a move that leaves more than 100 lanes with a mask other than 0 and 31 is refused. The run is 150,000,000 iterations per round (deterministic xorshift, temperature 19.2 x e^(-3.178 i / 150,000,000) at iteration i). The build then gives each row of the round the table's decision for its pattern and its chosen outputs, including E.

**Round 1 (inputs affine in part).** Its plan has two steps. First a greedy pass over the C and D complements of rounds 0 and 1 (`r1greedy`): each of the 320 lanes in turn takes the mask, of the 32 possible, that gives the least operation count of rounds 0 and 1 (31 trial builds per lane), then each of the 320 C complements G1 is flipped when that lowers the count; at most three sweeps, and a sweep without a gain ends the pass (it saves 105 operations here). Then `polopt1` plans the rows of round 1 that have five distinct variable inputs like the rows of the later rounds: it anneals the output vectors of those rows (150,000,000 iterations, the cost and the temperature of the paragraph above, output moves only) with the lookahead of round 2, and each such row takes the table's decision for its pattern and its chosen outputs, including E. The other rows of round 1 (those with a constant input) are decided before `polopt1` by an exact search (`r1rowopt`, two sweeps): each row in turn tries every complement subset of its variable inputs with every 10-gate choice (`r1ov`) and a flip of each of its five term polarities, building rounds 0 and 1 for every candidate, and keeps a change when it lowers 16 x (the operation count of rounds 0 and 1) + 3 x (for each row of round 2, the least row cost over its input-polarity pattern); a sweep without a gain ends the search. Here it moves rounds 0 and 1 from 3,238 to 3,187 operations in 63,714 builds per plan.

The build is multi-pass: pass 1 plans round 1, pass k (2 <= k <= 22) plans round k on the state the earlier passes built, and the final build writes the program. The plan places 13 to 115 theta NOTs (C NOTs plus lanes with a nonzero D mask) per round in rounds 2 to 22. The rows of the next round see the polarities a round produced, so the plan changes decisions, never the function computed: the self-test, the KAT and the experiment program (which reads F1, G1, F, G, DEC, DECE, PHI, R1OV and R1E from plan.txt) check the program that is built. The ledger counts the program that is built, not the plan's prediction.

### 3.4 Chain feed

Digest plane j is written into register j, which held input plane j. The physical digest word is the next point: F folds the digest polarity PD into the function (Section 2). There is no copy and no NOT between steps.

### 3.5 The ledger of one step

Printed by the generator (Appendix B):

| operation | count |
|---|---:|
| XOR | 100,288 |
| AND | 18,704 |
| OR | 14,509 |
| NOT | 3,161 |
| load / store | 0 / 0 |
| **total** | **136,662** |

That is 533.84 word operations per evaluation of F, 0.0856 of the reference cost 6233 per evaluation.

### 3.6 Registers and code encoding (machine conventions H_reg and H_code)

**Registers.** Values are allocated to registers in program order, and a register is freed at the last use of its value. Input and digest plane j use register j. Every other value takes the lowest-numbered register of an operand that dies at its instruction, when the value may use that register (the instruction then has destination = first operand, the short form of the encoding below); otherwise it takes the lowest-numbered free register it may use. The registers a value may use: registers 0 to 255 are open to each value that dies before the last round, except the state planes of lanes 0, 6, 12, 18 and 24 after round 21 (they feed the digest row of the last round); in the last round, register j < 256 is open to a value whose last use is not after the instruction that defines digest plane j, so digest plane j always finds register j free. The program uses registers 0 to 2,024 (2,025 registers, equal to the 2,025 values live at once at the peak), so every register number of the straight line is below 2^11. The search keeps its state in registers 2,025 to 2,034 (the step counter, a spare word, the next trail number, rho, the hit counter, the all-ones word, the prefilter word, two return addresses, a zero word); register 2,035 is spare. The handlers of Section 4.3 use registers 256 to 2,024 as temporaries: their contents are dead between two steps, because every straight-line value is defined before it is used and only the planes 0 to 255 are carried from one step to the next. The step has no loads or stores.

**H_reg (declared machine convention, role supporting in claim.json).** The cost model and the target profile fix no register count. This package uses the 256-bit word RAM of collision-frontier-v5 with a declared file of 2,036 registers of 256 bits. An operation on register operands costs one word operation, with no load or store. Every load and store of the other code is a charged word operation (Section 4). The file's 65,152 bytes are counted as memory (Section 6). This is the convention of 67f781f8 (a declared file of 2,304 registers), credited in Section 8.

**H_code (declared code-memory charging convention, role supporting in claim.json).** The cost model and the target profile fix no code encoding.
- **Encoding.** Each straight-line instruction has only register operands. It is written in a two-address encoding: bits 0-1 the opcode (0 XOR, 1 AND, 2 OR, 3 NOT), bit 2 a flag t; with t = 1 the destination is the first operand and the instruction continues with the first operand and, for XOR, AND and OR, the second (11-bit register numbers); with t = 0 it continues with the destination, the first operand and, for XOR, AND and OR, the second. A NOT is 14 or 25 bits, an XOR, AND or OR 25 or 36 bits. XOR, AND and OR commute, so an instruction whose destination is its second operand is written with its operands swapped. The instructions are packed with no padding in a little-endian bit stream (bit k of the block is bit k mod 8 of byte k div 8); prog.bin holds the 136,662 instructions of the step (552 of 14 bits, 108,002 of 25 bits, 28,108 of 36 bits; 105,945 with t = 1, 77.5%), 464,959 bytes, and pf.bin the 15 prefilter ORs, 49 bytes (the prefilter word is register 2,030, below 2^11). The decoder reads the instructions in order; the length of each follows from its first three bits. The memory table charges the two files at their measured sizes.
- **Other code.** All other code (setup, loop control, hit handler, DP handler, restart, replay, output) is real code of one machine, written out in Appendix D and assembled: 1,955 instructions of 8 bytes and a literal pool of 11 words of 32 bytes (15,992 bytes), measured from the assembled file. An instruction word has a 5-bit opcode, a flag L, three 11-bit register numbers and a 25-bit immediate field; with L = 1 the immediate is literal number imm of the pool (the pool follows the instruction words; it holds the distinct immediates of 2^25 or more). Jump targets are instruction numbers, as before; every instruction has the same size. Each instruction costs one word operation, except PERM, which applies the 23-round permutation to the 1,600-bit state held in seven registers and costs one unit (6233 operations), the cost model's own price of one permutation. The other instructions are the model's primitives: register-register and register-immediate XOR, AND, NOT, addition, subtraction, shifts, a compare that writes 0 or 1, a conditional branch on that register (always right after its compare, checked by the assembler), jumps, load and store with address register plus immediate, and the random word.
- **Time ledger.** Each instruction is charged as the one word operation it performs; there is no separate charge for fetching or decoding.

The program file is 464,959 bytes. Its SHA-256 is 847d1d673642aed7e61f9de0662966daeeb37091141f97aa3558ebbb2c06a009.

### 3.7 Generation and constant selection (preprocessing)

**The generator writes the program as it builds it.** gen3.c (Appendix B) is a freestanding C program without libc, with static arrays only. Its nodes live in a ring of 8,192 slots that holds one round (rounds 0 and 1 share it; this build needs at most 6,847 slots and 1,813 of the 2,048 affine-form slots). When a round is built, the generator removes its dead nodes (liveness from the state planes, or from the digest planes in the last round), gives every value its last use (every use of a value lies in its own round or, for a state plane, in the next round), allocates registers in node order and writes the round's instructions to prog.bin at once. It then keeps only the 1,600 state planes (register and flags) and reuses the ring for the next round. The program is never held in the generator's memory. **The cut pass (CUTS 1).** After round 1 is built and its dead nodes are marked, the generator rewrites the live nodes of rounds 0 and 1 once, in node order, and marks the dead nodes again: (a) a NOT of a NOT node is its operand, and a second NOT of one value is the first NOT; (b) for a XOR of p and an AND (OR) node that has no other use and that reads p, with q its other operand, the identity p XOR (p AND q) = p AND NOT q (p XOR (p OR q) = NOT p AND q) turns the XOR node into an AND node on p and a NOT node of q (of p), where that NOT node is the operand of q when q is a NOT node, else an existing live NOT node of q defined before the XOR, else the AND (OR) node itself rewritten as the NOT. Each rewrite keeps the value of every node it keeps, so every state plane keeps its value (selftest.c, the known-answer test and the exact comparison with the plain implementation check it on every lane); the pass never adds a node, and the instruction count in the ledger is the count after it. experiments/ls1.py repeats the pass.

**The run `gen3 512 1000 8`** is the preprocessing:
1. for each of the 512 constant sets of trials 1000 to 1511 (Section 2: K_0..K_4 from the xorshift generator of trial t) it builds the straight line without the plan and counts its operations (trial 1000 gives 141,855; the lowest is 141,645);
2. the trial with the lowest count is built with the plan of 3.3 and counted: trial 1106: 136,662;
3. that trial, 1106, is built again and written out (prog.bin; the ledger goes to standard output).

The check run `gen3 1 1106 8 i` rebuilds trial 1106 alone and writes the identical prog.bin (compared byte for byte), meta.txt (constants and PD) and plan.txt (the decisions of the plan, embedded in the experiment program); like the self-test, it is a verification run, and the search uses none of its output.

- **Time.** The ledger charges every build 2^32 word operations and every annealing iteration 2^12 (a move and its undo update at most 2 x 56 rows of the cost tables, with one exponential), the plan's row tables 2^32 once: at most 189,430 builds (512 trial builds, then for each of the two plan runs the first prefix build, the round-1 greedy builds (three sweeps of 320 x 31 mask builds and 320 flips, each counted as a full build), the 63,714 builds of the round-1 row search, the build that records round 1, one build per planned round 2 to 22 and the counting or writing build) and 6,600,000,000 iterations, plus 2^10 per trial for its constants, count and comparison: G = 840,633,550,372,864. The 512-set scan of the constants is step 1 of this run and is inside G; no other generator run's output is used. PRE = G + K + P + O = 1,037,604,497,543,936 = 2^49.88 word operations, part of N (Section 4.4), with K, P and O below. Since 2^37 < PRE / 6233 <= 2^38, preprocessing_log2 is 38. The generator run took 723.98 s of user time on one core of an AMD Ryzen 9 7900X (at most 5.6 GHz): at most 8 retired instructions per cycle gives below 2^44.9 machine instructions, below the charge.
- **Memory.** Measured with `size`: text 78,810 bytes, data 12 bytes, BSS 456,096 bytes, an image of 534,918 bytes. `gen3 512 1000 8` was run under `nice -n 10 prlimit --as=1048576 --stack=16384` (an address-space limit of 2^20 bytes and a 16,384-byte stack) and completed. Its peak resident memory, read by the program from /proc/self/status VmHWM, is 466,944 bytes. Section 6 charges the image, a 16,384-byte stack reserve and the whole program file, as if the program were held.

**The other preprocessing steps.** Every other step whose output the search uses is charged in PRE (pre_ops() in Appendix A). Each is deterministic, runs once, alone, before the search, and holds less than the generator bound of Section 6.

- *K, the constant basis (kbasis.h).* Not run by this generator: the design X constants are drawn by xorshift (Section 2). The ledger keeps its charge K = 2^24 in PRE.
- *P, the parameter scan (the native program scan.c, D.5, which wrote params.json and scan_counts.txt).* A coarse grid of 8 octaves of theta x 16 thresholds x 12 replay caps (1,536 points), then 25 thresholds x 9 caps around the best. For each point, the least Tb with model success at least 0.3902: at most 210 geometric steps and 50 bisection steps of a float model of the bound of Section 5. Then the exact least Tb with the Decimal bound of Appendix A. Counted in the run: 156,190 float evaluations over 2,590,117,602 bins and 21 exact evaluations over 1,621,347 bins. Charges: a double-precision operation costs at most 2^9 word operations (53-step shift-and-add multiplication or restoring division, with unpacking, normalisation and rounding). exp, expm1, log and log1p cost at most 2^14 each (range reduction and at most 30 such operations). A float bin (three of these functions and 12 operations) is charged 2^16, and the fixed part of a float evaluation (four functions and 20 operations) 2^17. An 80-digit Decimal is an integer below 2^340 (two words) with an exponent. A multiplication or division costs at most 2^13, exp at most 2^9 of these (2^22), and ln at most four exps. An exact bin (two exps and 10 operations) is charged 2^24, and the fixed part of an exact evaluation (two lns, two exps, two integer powers and 30 operations, below 2^25) 2^27. The grid records and their sort are charged 2^20. P = 196,970,927,751,168 = 2^47.48. The scan took 53.63 s of user time on the same machine, below 2^41.1 machine instructions, far below P. Memory: run as the native program scan.c (D.5, compiled with `-DREGS=2,036`; the same params.json and scan_counts.txt, byte for byte), at most 131,072 bytes, the measured peak of the whole process (code, data, stack) under a 2^20-byte address-space limit.
- *O, the assembly (`other4.py build`, Appendix D).* It emits the 1,955 instructions, resolves the jump targets, checks every branch, encodes each instruction in an 8-byte word (with the literal pool), and writes other.bin, the 49-byte prefilter pf.bin and the 16-word data image. It hashes the three files with SHA-256 (261 blocks) for counts.txt. Charged 2^8 per instruction, 2^13 per SHA-256 block (64 rounds of at most 48 operations and the schedule) and 2^12 for the data image: O = 2,642,688. Memory: run as the native program other.c (D.6, compiled with `-DRB0=2,025`; the same other.bin, byte for byte), 77,824 bytes, the measured peak of the whole process under a 2^20-byte address-space limit.

### 3.8 Correctness of the step (checked by execution)

- `selftest` (our C program, Appendix B) executes the program file, decoded from its two-address encoding, on 64 x 256 uniform points for four chained steps each, and compares every output with F computed by a plain lane-wise 23-round implementation of m(u): 65,536 chained evaluations, run with three different seeds, 0 mismatches each.
- That reference matches hashlib.sha3_256 at 24 rounds on 300 messages of lengths 0 to 299, and the organizer's verifier/keccak.py sha3_256(m, rounds=23) on the same messages: 0 mismatches.
- The experiment program regenerates the same straight line in Python from the generator's decisions (plan.txt, embedded) and refuses to run unless its encoding hashes to the SHA-256 above. Before its trials it checks two chained full-width steps against the plain implementation.

## 4. The search

Parameters:
- L = 256 walks.
- Distinguished point (DP): the 256-bit image x of F (bit j = plane j) is a DP when x < THR = 584 x 2^135: the planes 145 to 255 are zero and the 10 planes 144 down to 135, read as a number, are less than 584. The probability of a DP for a uniform image is theta = 584 x 2^-121 (H = -log2 theta = 111.8102); it is a rational number, exactly this, and is not a power of two.
- Replay cap LRC = 77,207 x 2^99 = 48,935,749,945,910,453,700,677,982,188,732,416 steps = 10.75 / theta. No trail is cut; the replay refuses a trail of more than LRC evaluations.
- U = 77,120: the limit on trails started in one attempt.
- S = 15,424 table words, five slots each (77,120 slots, one per trail: U = 5 S); 2^14 = 16,384 > S.
- Tb = 1326663716884019821919338815169757184 = 535835208 x 2^91 = 0.99807085 x 2^120 steps of 256 walks per attempt.
- HMAX = floor(Tb (1 + 2^-20) / 2^8) + 1 + LRC = 54118035032196129959512860308537345: the cap on prefilter hits; the attempt aborts at hit HMAX + 1.

State:
- in registers: the 256 input planes (registers 0 to 255); the step counter c, the next trail number idn, rho, the hit counter h, the all-ones word, the prefilter word and the return addresses (registers 2,025 to 2,034);
- in memory (word addressed): the table TAB of S words; the walk word WK[l] of each walk l, which holds LST[l], the number of the first step of its trail, in bits 0 to 127 and LID[l], its trail number, in bits 128 to 255 (both fit: Tb < 2^128, t(U) < 2^128); a data image of 16 words: the 7 words of lane constants of the absorbed state (K, with the lanes of u zero), PD, and 8 words for the output pair.

A table word holds five slots of 51 bits (slot k = bits 51 k to 51 k + 50, k = 0 to 4; bit 255 is unused). Trail i (i = 0, 1, ..., U - 1, in the order the trails start) has the trail number t(i) = (i mod S) + 51 floor(i / S) x 2^14 and owns slot floor(i / S) of word i mod S: the low 14 bits of t(i) are the word, the bits above them the slot's bit offset. The numbers t(i) are distinct, so the starts rho + t(i) are distinct points, and t(l) = l for l < 256 <= S. A written slot is

    1 | (bits 0 to 49 of the trail's end) << 1,

never zero; an unwritten slot is zero. Neither the trail number nor the trail's length is stored: the slot's place gives the number, and the replay measures the length.

```
setup: rho := random word; idn := 256; h := 0; c := 0; TAB := 0; for l < 256: WK[l] := l << 128 (LID[l] = l, LST[l] = 0); lane l of the input planes := rho + l
loop:
  the straight line (136,662): the input planes become F of the 256 walks
  pf := OR of the 16 planes 240..255 (15 ORs)
  if pf != all-ones (compare, branch):          -- some walk has planes 240..255 zero (probability 2^-16 each)
      h += 1; if h > HMAX: halt, the attempt failed   -- hit counter and abort (F5)
      dp := complement of (pf OR (OR of the planes 145..239))      -- the walks with the top 111 planes zero; c1 := c + 1 = steps completed including this one
      dp := dp AND (the walks whose planes 144..135, read as a number, are < 584)      -- bit-parallel comparison with the constant 584: the walks at a DP
      while dp != 0: l := the lowest set bit of dp; clear it;
          end := the 50-bit value with bit j = bit l of plane j, j = 0..49 (the only bits of the point the record reads)
          record := 1 | end << 1;  rep := the record in each of the five slots
          for each word w = 0 .. S - 1: load it and XOR rep; for its slots k = 0 .. 4 in order (shift, mask) test for zero:
             zero: slot k of word w equals the record (an unwritten slot never does): REPLAY(w + 51 k 2^14, walk l, c1);
                if it returns a != b, output m(a), m(b) and stop; otherwise halt, the attempt failed
          no slot equals the record: t := LID[l] (WK[l] >> 128); word (t mod 2^14) := word OR (record << (t >> 14)); restart(l, c1); next DP walk
  c += 1; if c != Tb goto loop
  halt, the attempt failed                           -- c = Tb
restart(l, s): if idn = t(U): halt, the attempt failed
               WK[l] := s | idn << 128 (LID[l] := idn; LST[l] := s); lane l of the input planes := rho + idn; idn += 1;
               if idn mod 2^14 = S: idn += 51 x 2^14 - S      -- so idn = t(i) for the i-th trail
REPLAY(trail a, walk l of trail b, c1):
  b := LID[l]; lb := c1 - LST[l]                       -- the new trail's length is known; if lb > LRC: return nothing
  walk trail a from a_0 = rho + a to its first DP: la := the number of evaluations (stop with failure if LRC are passed);
      when G divides i, the point a_i is stored in TAB[i / G]      -- checkpoints, G = ceil(LRC / (S - 1)), in the table words
  d := la - lb; i := max(d, 0)                          -- aligned pairs (a_i, b_(i-d)), b_j = j evaluations from b_0 = rho + b
  p := a_i (from TAB[floor(i / G)], i mod G evaluations); q := b_(i-d) (from b_0, max(-d, 0) evaluations)
  if p = q return nothing
  repeat: n := the least multiple of G above i
      if n >= la: m := la - i; leave                    -- the last segment ends at the common DP
      q' := b_(n-d) (n - i evaluations from q)
      if q' = TAB[n / G]: m := n - i; leave            -- equal at the checkpoint: the trails merge inside this segment
      p := TAB[n / G]; q := q'; i := n
  repeat m times: if F(p) = F(q) return (p, q); p := F(p); q := F(q)
  return nothing
```

No trail is cut: a walk runs until its DP, however long that takes, and only the replay refuses a trail of more than LRC evaluations (the entry test lb <= LRC, and the measuring walk of trail a stops with failure after LRC evaluations without a DP). A trail restarted inside step c (at a DP) starts at step c + 1, hence LST[l] := c1. A trail is recorded at its first DP, so walking it from its start to its first DP gives its length; the walk of the replay stops at that DP. The DP test of the replay is x < THR on the image, the test of the loop above. The replay is the last routine of an attempt (it stops with the pair or with failure), so the table words are free for the checkpoints; a stored trail has at most floor((LRC - 1) / G) + 1 = 15,423 <= S checkpoints (G = 3,172,907,342,664,232,231,127,405,964,387). Two trails with the same DP agree from their merge on: a point common to both trails is followed by the same evaluations up to the common DP, so it sits at aligned positions, and a_i = b_(i-d) holds from the merge on and fails before it. So the first checkpoint with equal points bounds the merge to its segment, and the lock step from the last unequal pair finds the first F(p) = F(q) with p != q, the pair the full lock step of 0dc77160 returns.

### 4.1 One iteration of the loop

An iteration costs the straight line (136,662), the prefilter (15), its test (2) and the counter (3: add, compare, branch): **BSTEP = 136,682 operations**, the instructions at the labels `loop` and `cont` of Appendix D around the straight-line block. No other operation runs in an iteration without a prefilter hit.

### 4.2 The replay

The replay evaluates F on one point at a time with the permutation, one unit (6233 operations) per call. The routine `evalF` (Appendix D) loads the 7 words of lane constants, XORs the point into the lanes 0 to 3 and 10 to 13 and v_4 (four rotations of its limbs, XORed) into the lanes 4 and 14 (43 instructions with the loads), calls PERM, loads PD and XORs it into the first state word: one evaluation with its return costs **e = 6279** operations.

Counted from the emitted code:
- taking the trail number from the place of the matching slot costs 3 (move, or, jump) and the entry 12 (the walk word: load, shift, mask, subtract; the test lb <= LRC 2; the two starts; four initial moves);
- a measuring evaluation of trail a costs e + 10 (the checkpoint test 2, call, add, the DP test of the image x < THR 2, the cap test 2, move, jump), e + 6 for the one that lands on the DP, and 3 more when it stores a checkpoint (store, two adds);
- the alignment, with the test d < 0: for d >= 0, 16 + 6 K + r (e + 7) with K = floor(d / G) checkpoints passed and r = d - K G < G evaluations of a; for d < 0, 8 + (lb - la)(e + 7);
- the test p = q 2; a segment without a merge 14 + m (e + 6) for its m evaluations of trail b (end test 2, three moves, the checkpoint load and comparison 3, six moves and adds), the segment with the merge 8 + m (e + 6), the last segment 3;
- a lock-step iteration 2e + 13, the success exit 101 (two message builds of 44 with their calls and moves, 8 stores, the halt).

With la, lb <= LRC and nc = floor((la - 1) / G) + 1 checkpoints: trail a costs at most la (e + 10) - 4 + 3 nc; trail b is evaluated at most lb times in all (alignment and segments, each at most e + 7); the alignment of a takes r < G evaluations and K <= nc - 1 checkpoint steps; there are at most nc - 1 - K segments without a merge; the lock step runs through one segment, at most G iterations. For d >= 0 this gives at most 15 + la (e + 10) - 4 + 3 nc + 16 + 6 K + (G - 1)(e + 7) + 2 + 14 (nc - 1 - K) + 8 + (lb - 1)(e + 6) + (G - 1)(2e + 13) + 2e + 110 <= (2e + 16) LRC + (3e + 20)(G - 1) + 17 nck + e + 127, and for d < 0 at most (2e + 17) LRC + (2e + 13)(G - 1) + 17 nck + e + 118, with nck = floor((LRC - 1) / G) + 1 = 15,423; an exhausted lock step (m (2e + 13) + 3) and every refusal cost less. So the replay costs at most **12575 LRC + 18857 G + 17 nck + 6406** (e = 6279, G = 3,172,907,342,664,232,231,127,405,964,387). At most one replay runs per attempt: the attempt stops after it, with the pair or with failure.

### 4.3 Rare operations

Every routine is real code of the machine of Section 3.6 (Appendix D). The counts, each for the longest path, are read from the emitted code (`other4.py build`, D.2):

| routine | operations |
|---|---:|
| a prefilter hit with no DP walk (counter 3; OR of the planes 145..239; combine and complement 2; the comparison of the planes 144..135 with 584, at most 4 per plane, and a move; c1; test of the DP mask 2) | **121** |
| one DP walk without a match, without its restart: DP-mask test 2, lowest set bit and clearing 44, gather of the 50 end bits 198, the record, its five copies and the word index 13, the insertion into the trail's slot 8, move, call and jump back 3; and 24 for each of the S words (load, XOR, five slot tests of 3 or 4, next word 3) | 268 + 24 S |
| restart(l, s) with its return: cap check 2, the walk word (shift, or, store) 3, add and increment 2, the wrap test 3 and its add 1 (charged on every restart), the insertion of the new point into lane l and the return | **1,294** (the call that halts at idn = t(U): 3) |
| the event c = Tb: the HALT after the iteration's counter, compare and branch | 1 |
| setup: clearing TAB (eight words per pass), the 256 starts | **351,456** |

The numbers of events. At most HMAX + 1 prefilter hits are processed in every execution, and the ledger charges that number. The counter idn runs through t(256), t(257), ..., t(U), one value per completed restart, so at most U - 256 restarts complete; each DP walk except the last is followed by a completed restart, so at most U - 255 DP walks are processed (the last stores its record and halts at idn = t(U), or starts the replay of 4.2). A DP walk without a match passes all S words, so it costs exactly 268 + 24 S; a match ends the scan earlier and starts the replay. The event c = Tb happens once.

R = (HMAX + 1) x 121 + (U - 255) x (268 + 24 S) + (U - 256) x (1,294 + 3) + 3 + 1 + 351,456 = 6,548,282,238,895,731,725,101,056,125,907,240,994.

### 4.4 Total

N = Tb x 136,682 + replay + R + PRE = **181,953,025,320,464,077,606,017,378,024,280,737,053,874** word operations (Appendix A).

| part | operations | share |
|---|---:|---:|
| main loop, Tb x 136,682 | 181,331,050,151,141,597,299,579,067,935,032,751,423,488 | 0.99658 |
| replay, 12575 LRC + 18857 G + 17 nck + 6406 | 615,426,887,083,584,574,713,207,995,517,580,845,456 | 0.00338 |
| rare operations R and preprocessing PRE | 6,548,282,238,895,731,725,101,056,125,907,240,994 + 1,037,604,497,543,936 | 3.60e-05 |

time_log2 = log2(N / 6233) rounded up at the fifth decimal = **124.45691**, checked in exact integer arithmetic:

    6233^100000 * 2^12445690 < N^100000 <= 6233^100000 * 2^12445691

## 5. Success probability and the premise H_rand

**Premise H_rand (our theory): over the algorithm's coins, the program run on the fixed SHA3-256-r23 target succeeds with probability at least the probability computed below for a uniformly random function F.** The target is fixed: F of Section 2, with its fixed constants K and PD, is one deterministic function, and the only randomness of the algorithm is the random word rho. That transfer is the premise, and it is the one score-critical premise of this package. In claim.json it has four fields: the statement above; role score-critical; scope, the fixed function F of Section 2 on the points of one attempt; limitations, our theory with no proof. The organizer runs of Section 7.1 are not used in this section: The success bound assumes nothing about the organizer-seeded trials (no independence or identical distribution of the trials is used). Everything else in this section is computed in the random-function model M: F is a uniformly random function from 256 bits to 256 bits (values at distinct inputs independent and uniform) and rho is uniform and independent of F. In M:

- (i) the first coincidence of images among e evaluations has probability 1 - prod_(k<e)(1 - k/n) >= 1 - exp(-e(e-1)/(2n)) =: G(e), where n = 2^256;
- (ii) after the first coincidence e* (partner s), the number l of further evaluations of the trail until its DP satisfies P(l >= j | e*, s, history) <= (1 - theta)^j (1 + 2^-108) for every j: a lemma derived from (iii) below, not a premise;
- (iii) F is realised by lazy sampling: a fresh evaluation draws a new independent uniform value, so given the whole history of the run it equals one given earlier output with probability 2^-256, whatever inputs the adaptive program chose. This is a property of M, not a claim about the fixed target, for which the run given rho is deterministic.

The first coincidence is a stopping time over all evaluations in their execution order (step by step, walk by walk). Under (i) and (iii), when k earlier images are distinct the next fresh evaluation coincides with an earlier image with conditional probability exactly k/n, so G(e) of (i) is the probability that the first e fresh evaluations contain a coincidence; no fixed-size birthday product over a random set and no conditioning on which trails finish is used.

**Lemma (ii), derived.** Write q = 1 - theta and E = 256 Tb. Realise F by lazy sampling as in F2: one uniform value V_t per evaluation index t, xi_t = 1 when V_t is a DP, the xi_t independent Bernoulli(theta). The walks run in lockstep, so the evaluations of a walk sit at fixed indices 256 apart, fixed before the run. Let e* = t with partner s < t (V_t = V_s), s on trail A. B's next input is the input A evaluated at s + 256, and s + 256 k < t + 256 k, so A evaluates every later point of the common path first: l is the first k >= 1 with xi_(s + 256 k) = 1 (the indicators after a DP of A's walk are again iid, so this holds also when A ended before t). By (iii), P(V_t = V_s | past) = 1/n exactly, whatever the indicators xi_(s + 256 k) are; the event (e* = t, partner s) depends on them only through the event D that V_1, ..., V_(t-1) are distinct. Given the m = t - 1 indicators before t, k < U of them DPs (outside F2), those images are uniform on the theta n DP points and on the (1 - theta) n others; comparing the two products with pi_m = prod_(i<m)(1 - i/n) term by term, P(D | indicators) lies in [pi_m (1 - delta), pi_m (1 - E/n)^-U] with delta <= U E/n + E^2 theta/(2n) + U^2/(2 theta n) = 2^-111.8 + 2^-112.8 + 2^-112.7 < 2^-109 (Appendix A). By Bayes, given the event (e* = t, partner s) and the indicators of the other walks, the law of the indicators along A's walk after s is within a factor (1 - E/n)^-U / (1 - delta) <= 1 + 2^-108 of the iid law, under which P(l >= j) = q^j. Merges: if the path then reaches a point p already evaluated on a third trail C, the remaining distance is the first DP among C's indicators after p; that merge is again an image coincidence of a fresh evaluation, of probability exactly 1/n given the past by (iii) whatever C's later indicators are, so the indicators along the path stay iid across it, and by induction over the merges P(l >= j | e*, s, history) <= q^j (1 + 2^-108). The bin sum and F6 use this tail with weights at most 1, so the factor costs at most 2^-108 at the bin sum and 2^-108 F6 at F6: the term FL = 2^-108 (1 + F6) = 3.082e-33 (Appendix A).

**The coincidence.** Let e* be the first evaluation whose image equals an earlier image, at step b* = ceil(e*/256). The trail B of that evaluation and the earlier trail A have equal points from then on and both end at the same DP after l further evaluations of B. B is recorded at step b* + l at the latest; A reached the same point no later, so A was recorded before, or in the same step in a lower walk, and the later record finds the earlier one.

The search succeeds if all of these hold: (a) b* + l <= Tb; (b) both trails have at most LRC evaluations; (c) fewer than U trails are started; (d) the coincidence is between two different trails; (e) no record of a different end has the same 50 stored end bits, and the replay finds the merge.

Split l into bins of w = 2^(111 - 12) steps: bin j holds l in [(j - 1) w, j w - 1], j = 1 .. J = 77,207, J w = LRC, with probability p_j = (1 - theta)^((j-1) w) - (1 - theta)^(j w). If l is in bin j, (a) holds when e* <= 256 (Tb - j w). By lemma (ii), with its factor 1 + 2^-108 charged in FL,

    Pr[(a)] >= sum_j p_j G(256 (Tb - j w)).

The failure events the sum does not cover:

- **F6**, the colliding pair has a trail of more than LRC evaluations. No trail is cut; the replay refuses such a pair, and this term bounds the probability that the pair of the first coincidence is such a pair. Write q = 1 - theta and E = 256 Tb, the number of evaluations of an attempt at most. The age of an evaluation is its place in its trail: the number of evaluations of the trail up to and including it. Until the first coincidence every input is fresh and the DP indicators xi of the evaluations are independent Bernoulli(theta) (as in F2); an evaluation of age at least a has the a - 1 earlier evaluations of its walk all non-DP, so P(age >= a) <= q^(a - 1) for every evaluation. Take evaluations s < t. By (iii), given the history before t, t has the image of s with probability 1/n, and the ages a_s and a_t, which depend only on evaluations before s and before t, are then fixed. By lemma (ii) the number l of further evaluations to the DP has P(l >= j | e*, s, history) <= q^j (1 + 2^-108), the factor charged in FL, and la = a_s + l, lb = a_t + l. The replay needs la <= LRC and lb <= LRC, so it fails when l >= LRC + 1 - max(a_s, a_t), with probability g(max(a_s, a_t)) <= g(a_s) + g(a_t), where g(a) = min(1, q^(LRC + 1 - a)). The function g does not decrease, g(1) = q^LRC, and g(a) - g(a - 1) = q^(LRC + 1 - a) (1 - q) for 2 <= a <= LRC + 1, g(a) = 1 beyond. By summation by parts, for any evaluation u, E[g(age_u)] = g(1) + sum over a >= 2 of (g(a) - g(a - 1)) P(age_u >= a) <= q^LRC + LRC (1 - q) q^LRC = q^LRC (1 + LRC theta). Call this G6 = q^LRC (1 + LRC theta); it holds for the ages computed from the DP indicators alone (each walk restarting after its DPs), which are the true ages before the first coincidence. Only the pair of the first coincidence matters. Write pi_m = prod_(i<m)(1 - i/n), and let t be the first coincidence: the images V_1, ..., V_(t-1) of F2's lazy sampling are distinct (event D) and V_t equals V_s for some s < t, probability 1/n for each s given the history. Given the DP indicators of the m = t - 1 evaluations before t, k of them DPs, those images are independent and uniform on the DP points and on the other points, so P(D | indicators) <= prod_(i<m-k)(1 - i/((1 - theta) n)) <= pi_(m-k) <= pi_m (1 - E/n)^-k, and k < U outside F2. The ages before t are functions of these indicators. So the first coincidence is at t and the replay refuses it with probability at most (1/n) pi_(t-1) (1 - E/n)^-U sum_(s<t) E[g(a_s) + g(a_t)] <= 2 G6 (1 - E/n)^-U (t - 1) pi_(t-1) / n. Since (t - 1) pi_(t-1) / n = pi_(t-1) - pi_t, the sum over t = 1, ..., E is 1 - pi_E, and ln(1 - x) >= -x - x^2 (0 <= x <= 1/2) gives pi_E >= exp(-E^2/(2n) - E^3/(3n^2)). So F6 = 2 G6 (1 - exp(-E^2/(2n) - E^3/(3n^2))) (1 - E/n)^-U = 1.977e-4. This covers (b) outside F2 and F4, whose terms follow.
- **F2**, more than U - 256 restarts after a DP (a fact proved here). Realise F by lazy sampling with independent uniform values V_1, ..., V_(256 Tb), one per evaluation index in execution order: the t-th evaluation returns V_t if its input is fresh and the stored value otherwise. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(theta), so N1 = xi_1 + ... + xi_(256 Tb) is binomial with mean mu = 256 Tb theta. A DP output at a fresh input is a position with xi_t = 1. A DP output at a repeated input never causes a restart: the value is the stored output of the first evaluation of that input, whose trail ended there and was recorded with another trail number, and the scan of the S words finds that record, so the attempt goes to REPLAY and stops. Hence the restarts after a DP are at most N1. The halt at idn = U needs N1 >= U - 255, and the Chernoff bound e^-mu (e mu / (U - 256))^(U - 256) >= P(N1 >= U - 256) gives 2.144e-15. This covers (c).
- **F3**, the coincidence lies inside one trail: at most U / (theta^2 n) = 1.380e-5. This covers (d).
- **F4**, 2^-90 + U^2 2^-51 = 2.641e-6. This covers (e): a start rho + t(i) equal to a point of another trail (U starts, about 2^128 images: below 2^-113); and two different ends with the same 50 stored bits: in M the ends are uniform on the bits below the 10 comparison planes, so a pair agrees with probability 2^-50, and there are fewer than U^2 / 2 pairs.
- **F5**, the hit counter aborts the attempt before it stops: below 2^-1000. Call a walk's input at a step fresh if F was not evaluated at it before in the attempt, and let X' count the steps at which some walk with a fresh input lands on planes 240..255 zero. Given the past, each step adds to X' with conditional probability at most 1 - (1 - 2^-16)^256 < 2^-8 (in M). A hit not counted in X' needs a walk at a repeated input; outside F4 these occur only after the first image coincidence, and a successful attempt outside F6 stops at step b* + l with l <= LRC. So h <= X' + LRC on success, and an abort needs X' >= floor(Tb (1 + d) 2^-8) + 2 > (1 + d) mu, with d = 2^-20 and mu = Tb 2^-8. The Chernoff bound for indicators with conditional probabilities at most 2^-8 (supermartingale exp(s X'_t - (e^s - 1) t 2^-8)) gives at most exp(-d^2 mu / (2 + d)) = exp(-2,356,627,043,343,743,856,968) < 2^-1000, checked in exact rationals in Appendix A.

With FL = 3.082e-33 for lemma (ii) and a further 2^-60 for rounding, the success probability of one attempt is at least 0.3900000004 at Tb, and 0.3899999993 at Tb - 2^91: Tb is the least multiple of 2^91 that reaches 0.39 (Appendix A, 80-digit decimals). In evaluations, 256 Tb = 0.998071 x 2^128; the birthday point for success 0.39 is 0.9943 x 2^128, and the wait for the DPs of the last trails, 256 / theta evaluations, is most of the difference.

A failed attempt can be repeated with a fresh rho at the same cost. The claim is one attempt with success 0.39, a probability over the algorithm's coin rho for the fixed target, under the premise H_rand.

## 6. Memory

The search, at its peak:

| region | bytes |
|---|---:|
| register file, 2,036 words of 32 bytes (H_reg) | 65,152 |
| straight line plus prefilter, 136,677 instructions, two-address encoding, prog.bin + pf.bin (H_code) | 465,008 |
| other code (Appendix D), 1,955 instructions x 8 bytes + 11 literals x 32 bytes, measured | 15,992 |
| table, 15,424 words of five slots | 493,568 |
| walk words of the 256 walks (LST and LID), 256 words | 8,192 |
| data image (lane constants K of the absorbed state, PD, output pair), 16 words | 512 |
| **total** | **1,048,424** |

The preprocessing `gen3 512 1000 8` runs before the search and ends before it starts:

| `gen3 512 1000 8` | bytes |
|---|---:|
| image (text, data, BSS; all arrays static) | 534,918 |
| stack reserve (the run completes with a 16,384-byte stack limit) | 16,384 |
| the program it writes, prog.bin (written out round by round, counted here in full) | 464,959 |
| **bound used** | **1,016,261** |
| measured peak resident memory (VmHWM) | 466,944 |

The scan (at most 131,072 bytes) and the assembly (77,824 bytes) of Section 3.7 each run alone, below this bound. The claimed memory covers both phases, the preprocessing included: peak = max(search 1,048,424, preprocessing 1,016,261) = 1,048,424, since the two phases do not overlap; 1,048,424 <= 1,048,576 = 2^20: memory_log2_bytes = 20. The margin to 2^20 is 152 bytes (search phase 152, preprocessing 32,315).

The declared experiments and the C checks of Sections 3.8 and 7 are verification runs; they build nothing the search uses.

## 7. Evidence for the step and for H_rand

### 7.1 Organizer experiments (experiments/manifest.json, program experiments/ls1.py)

Both experiments regenerate the straight line in Python from the generator's decisions (the encoding must hash to the SHA-256 of Section 3.6), check it against the plain 23-round implementation, and execute it on Python integers, all trials side by side. Every trial seed is prefixed by the 16-byte salt of ls1.py (constant SALT), drawn once when this package was generated; our own runs below used the same program with an empty salt. The runs are witnesses of what they execute (the regenerated line equals the plain implementation; the search works at width 22; chained full-width steps give recomputed 22-bit matches). They do not test a complete collision, 2^128 evaluations or the distinguished-point rate at full size, and their frequencies carry no statistical weight in this package: The success bound assumes nothing about the organizer-seeded trials (no independence or identical distribution of the trials is used).

- **rho-w22** runs the search of Section 4 end to end at width 22. The planes 22 to 255 are set to zero after every step. Parameters: a DP is an image whose 4 low bits are zero and whose 3 bits above them, as a number, are less than 5 (theta = 5/128), replay cap 256, no trail cut, 3,000 trails and 400 steps per attempt; the table keeps the trail number of each end and the replay measures the stored trail by walking it to its DP, keeping every 16th point as a checkpoint, walks the new trail once and lock-steps the segment of the merge, and refuses trails of more than 256 evaluations, as in Section 4. Every trial returns two messages whose 23-round digests agree on the 22 low bits. At this width a start often lies on another trail, so a replay that returns nothing restarts the walk instead of ending the attempt (the full-size rule halts, as F4 accounts). An ideal-function control (F replaced by a lazily sampled random function on 22 bits, the same rules) needs 20.47 steps to the pair on average (20,000 trials, standard deviation 7.91). Our own run of 256 trials (our seeds): 256 of 256 pairs, mean 20.72 steps; 14.1 s on one core here.
- **proj-w256** runs eight chained full-width steps from 256 uniform points per trial and finds the first two distinct evaluated inputs whose images agree on the 22 low bits; a random function gives success probability 0.3934 per trial, 100.7 of 256 (standard deviation 7.8). Our own run of 256 trials: 91 of 256; four further seed sets of 256 trials gave 109, 99, 118, 88, 505 of 1,280 trials in all (model 503.6, standard deviation 17.5); 8.3 s here.

### 7.2 Measured checks of H_rand on this program (our runs, not organizer runs)

The embedding makes round 0 affine, so F has one nonlinear round fewer than the plain digest map. hrand_test.c (Appendix C) executes the program file of this package and measures the quantity the search depends on, the rate of image coincidences among evaluated points, on three 32-bit windows (bits 0-31, 128-159 and 224-255; the top window lies inside the DP bits), for uniform inputs (A), consecutive starts rho + i (B; the starts rho + t(i) of the search are five runs of S consecutive values) and chained iterates (C), and the output differences of single-bit input differences (D):

```
A uniform inputs: M=2^24, pairs agreeing on 32 bits: low 32867, mid 32677, top 32801; expected 32768.0 each (sd 181.0); ratios 1.0030 0.9972 1.0010; z 0.55 -0.50 0.18
B consecutive inputs R+i: M=2^24, pairs agreeing on 32 bits: low 32805, mid 32767, top 32815; expected 32768.0 each (sd 181.0); ratios 1.0011 1.0000 1.0014; z 0.20 -0.01 0.26
C chained iterates (256 chains x 65536 steps): M=2^24, pairs agreeing on 32 bits: low 32685, mid 32493, top 32453; expected 32768.0 each (sd 181.0); ratios 0.9975 0.9916 0.9904; z -0.46 -1.52 -1.74
D single-bit differences: 65536 cells x 4096 pairs, max |z| 4.44 at input bit 195 output bit 202 (largest of 65536 normal cells is about 4.4); mean z^2 0.9986 (expected 1)
```

The coincidence rates lie within |z| <= 1.74 of the random-function values. If the real pair-coincidence rate is (1 - eps) of the random value, the same success needs about 0.5 log2(1/(1 - eps)) more bits of time, 0.0073 bit for eps = 0.01.

Further evidence on the same embedding from earlier builds (other constants or another digest mask PD; GPU, F checked against a CPU reference on 20,000 points with 0 mismatches): the length of a rho walk on F truncated to w bits has mean ratio to the random-function value 1.0017 (CI95 0.9977 to 1.0057) at w = 44 and 1.0039 (0.9958 to 1.0120) at w = 48 for the 8-round F, and 1.0041 (1.0001 to 1.0081) at w = 44, 0.9939 (0.9859 to 1.0019) at w = 48 for the 12-round F. These test the embedding and the truncation in rho length only.

### 7.3 The emitted program, executed (our runs, not organizer runs)

other4_test.py (Appendix D) executes the assembled bytes: other.bin decoded from its 8-byte words and literal pool, and the straight line (prog.bin and the 15 prefilter instructions) decoded from its two-address encoding and compiled to Python integer operations (D.3, D.4).
- **Routines, at the full-size immediates of this package.** The straight line against the plain 23-round implementation on every lane (2 x 256 points, 3 chained steps) and the prefilter word; setup, setwalk, restart and its halting call, evalF and the message builder against the plain implementation; a hit with no DP walk and the hit-counter abort; restart across a word wrap (t(2S - 1) to t(2S)); the DP handler on its path over all S words of a full table, writing the record into the slot of trail 255, 3 S + 17 and 5 S - 1; a match in each of the five slots of the first, a middle and the last word, with the trail number it yields and its operation count; the DP mask of the hit handler against the comparison x < THR on 1,024 constructed walks, and the iteration that reaches Tb. Each executed count equals the count of Section 4.3.
- **Replay.** Pairs of trails of the 12-bit truncation of F with a DP of about 1 in 21, for the checkpoint gaps G = 1, 8, 23: 119 pairs with the same end, both signs of d (the replay measures la, stores the checkpoints, aligns, walks the segments and finds the pair; the executed count equals the per-step counts of Section 4.2 summed along the path exactly, the pair equals the first merge of the trails, and it is checked with an independent Keccak), 102 pairs where one start lies on the other trail (p = q) and 21 pairs with different ends (a false key match: the replay exhausts and the attempt halts), each within the bound of Section 4.2, and the guards of the measuring walk and of lb.
- **End to end at reduced width.** The whole emitted program (setup, loop, straight line, hit handler, DP handler, restart, replay, output) runs with the planes W..255 set to zero after each step and the replay's F truncated alike (one extra ANDI in evalF, test builds only), the other immediates reduced; instruction for instruction it is the program of the full-size build. 16 runs on eight parameter sets (W = 26; W = 32 with a replay cap that refuses long colliding trails; a table of 400 words; a hit cap of 3; Tb = 5; U = 264; a table of 264 words with U = 1,320, so that every word fills its five slots; no comparison planes). Every pair found was checked with an independent Keccak, the executed operations were at or below the counted bounds of Section 4.3, and the sub-counts (setwalk, gather, loop, replay) matched exactly: 967 checks, 0 failures.

## 8. Credits and literature

A credit is not an endorsement; nobody named here has reviewed this package.

- **jungjipdo, entry 67f781f8 (sha3-256-r6).** Its Section 3 describes the step design this package follows: theta evaluated lazily per chi row, per-row complement subsets, dead-code elimination, the digest written over the input register, last-use allocation into a declared register file, and the straight-line instruction format (3-bit opcode, three 12-bit registers, stored there in 5 bytes; here a 2-bit opcode and three 11-bit registers, packed at 35 bits, after a lowest-free allocation); the register-file convention of Section 3.6 is its convention. We read its proof as a description; the generator, self-test, ledger, search code and text are our own, and none of its code was run, imported or compiled. It is on another challenge, so it is credited here and not declared as a dependency.
- **0xplemonade, entry 4ea0966b (sha3-256 Pareto round 24).** Its step lets a chi row read finished outputs in a chain; Section 3.2 builds the row table with that chained form, written from its description on our generator; credited as a dependency. None of its code was run, imported or compiled.
- **0xplemonade, entry 3a6995fc (sha3-256 Pareto round 23, 124.47268), the best entry of another participant on this row.** Its note describes a row synthesizer with chained chi tricks, the form of Section 3.2, and a search over the eight cheapest constant trials; this package uses the chained form only (one trial is planned in full). Credited as a dependency. None of its code was run, imported or compiled.
- **mitchuski, entry c9a7e62c (sha3-256 Pareto round 24).** Its search uses a distinguished-point threshold DT that is not a power of two, a replay cap in place of a trail cut, and four records per table word; this package keeps the first two from 90753795 (Section 4) and replaces the table layout; credited for them. It is on another challenge, so it is credited here and not declared as a dependency. None of its code was run, imported or compiled.
- **mpjunior92, entry 11565cb4 (sha3-256 Pareto round 8).** Its design X is the message embedding of Section 2 (the ten lanes, v_4, the all-ones and zero lanes, the constant offsets and the argument for round 0 and column 3 of round 1), and its note plans the round-1 rows that have a constant input with their own costs and a lookahead into round 2, the idea of the row search of Section 3.3; written from its note on our generator, credited as a dependency.
- **Our entries 90753795 (F1023094554, sha3-256 Pareto round 23, 124.46582) and 0dc77160 (SHA3GENV4B_R23, sha3-256 Pareto round 23, 124.84948)**, the declared dependencies. 90753795 is our best entry of this round on this line: its constants, polarity plan, search and other code are the base of this package, and what changed is listed in Section 1 (Search). 0dc77160 is the generic entry of this round; the search, success bound and rare-operation accounting follow it, and the replay of Section 4.2 replaces its full lock step by a checkpoint walk.
- **J. Guo, M. Liu, L. Song, Linear Structures: Applications to Cryptanalysis of Round-Reduced Keccak, ASIACRYPT 2016.** The linear-structure placement of message lanes that keeps round 0 affine (Section 2).
- **P. C. van Oorschot and M. J. Wiener, Parallel collision search with cryptanalytic applications, J. Cryptology 12 (1999); J. M. Pollard (1975).** The distinguished-point and rho methods.
- **G. Bertoni, J. Daemen, M. Peeters, G. Van Assche, Keccak implementation overview.** The lane complementing transform, applied plane by plane in Sections 3.2 and 3.3.

## Appendix A. The exact ledger

This program (cert4.py, with the inputs of this row written into it) computes the step count, the success bound of Section 5, N, the memory table and the integer certificate. It uses integers and Fractions; Decimal with 80 digits is used only for the exponentials and logarithms of the success bound. The constants of the rare operations and of the replay are the counts of Section 4.3, printed by `other4.py build` (D.2). H, kappa, S, U and Tb were chosen by the parameter scan, charged in PRE as P from its counted evaluations (scan_counts.txt, Section 3.7); the run below re-checks that Tb is the least multiple of 2^91 with success at least 0.39.

```python
INLINE = {
"ledger.txt": "LS1 step ledger (256 lanes, one chain step, 23 rounds), streaming generator gen3\nXOR 100288\nAND 18704\nOR  14509\nNOT 3161  (row complements chosen pre-DCE: 299)\nLOAD 0\nSTORE 0\nTOTAL 136662\nTRICKROWS 6396 ; forced term polarities 4\nfeed NOTs 0 (digest polarity folded into the chain function: F(u)=H(m(u))^PD)\nnodes created pre-DCE 136869 ; ring peak 6847 of 8192 ; linear forms 1813 of 2048\nmax live values 2025 ; registers used 2025 (limit 2304)\nconstants trial 1106 of 512 ; optmode 5 ; designx 1 ; shared round-1 pins 0 ; round-1 greedy gain 105 ; round-1 row search rounds 0..1 3238 -> 3187 ; r2 lookahead 1930 -> 1821\nround-1 row search builds per plan 63714\nannealing iterations per round 150000000\ntrials carried to the plan build 1\nplan r2 predicted row cost 1652 theta NOTs 112 free polarities set 0\nplan r3 predicted row cost 1644 theta NOTs 102 free polarities set 0\nplan r4 predicted row cost 1651 theta NOTs 111 free polarities set 0\nplan r5 predicted row cost 1639 theta NOTs 105 free polarities set 0\nplan r6 predicted row cost 1644 theta NOTs 111 free polarities set 0\nplan r7 predicted row cost 1644 theta NOTs 95 free polarities set 0\nplan r8 predicted row cost 1638 theta NOTs 109 free polarities set 0\nplan r9 predicted row cost 1641 theta NOTs 108 free polarities set 0\nplan r10 predicted row cost 1643 theta NOTs 112 free polarities set 0\nplan r11 predicted row cost 1642 theta NOTs 105 free polarities set 0\nplan r12 predicted row cost 1637 theta NOTs 113 free polarities set 0\nplan r13 predicted row cost 1646 theta NOTs 103 free polarities set 0\nplan r14 predicted row cost 1639 theta NOTs 115 free polarities set 0\nplan r15 predicted row cost 1641 theta NOTs 111 free polarities set 0\nplan r16 predicted row cost 1645 theta NOTs 109 free polarities set 0\nplan r17 predicted row cost 1645 theta NOTs 110 free polarities set 0\nplan r18 predicted row cost 1640 theta NOTs 103 free polarities set 0\nplan r19 predicted row cost 1649 theta NOTs 109 free polarities set 0\nplan r20 predicted row cost 1643 theta NOTs 113 free polarities set 0\nplan r21 predicted row cost 1646 theta NOTs 96 free polarities set 0\nplan r22 predicted row cost 261 theta NOTs 13 free polarities set 8\ncum after round 1 3187\ncum after round 2 9747\ncum after round 3 16293\ncum after round 4 22855\ncum after round 5 29399\ncum after round 6 35954\ncum after round 7 42493\ncum after round 8 49040\ncum after round 9 55589\ncum after round 10 62144\ncum after round 11 68691\ncum after round 12 75241\ncum after round 13 81790\ncum after round 14 88344\ncum after round 15 94896\ncum after round 16 101450\ncum after round 17 108005\ncum after round 18 114548\ncum after round 19 121106\ncum after round 20 127662\ncum after round 21 134204\ncum after round 22 136662\ngenerator peak RSS (VmHWM, this process image) 456 KiB = 466944 bytes (limit 1048576)\n",
"size.txt": "   text\t   data\t    bss\t    dec\t    hex\tfilename\n  78810\t     12\t 456096\t 534918\t  82986\tgen3\n",
"counts.txt": "other code: 1955 instructions x 8 bytes + 11 literals x 32 bytes = 15992 bytes (other.bin sha256 5d294e3f513f97796c250be21663b4d57bf86afce9868609e0da85ba9add949a)\nprefilter: 15 instructions, two-address encoding, 49 bytes (pf.bin sha256 8b0405c9870c5de287d7797b355ee12b97ecc07eeaf96ba8caed3e8d9b16ae93); the straight-line block = prog.bin (136662 instructions, 464959 bytes) then pf.bin, 136677 instructions, sits in front of instruction 26 (label loop)\ndata image: 16 words x 32 bytes = 512 bytes (data.bin sha256 2c3ebe318ee06cb0d87e50a077b1969c83fedad8eac0deff38a49bce593c8da8): KW[0..6], PD, 8 output words\nmemory map (words): TAB 0..15423, WK (walk words, LST | LID << 128) 15424..15679, data 15680..15695\nreplay checkpoint gap G = ceil(LRC / (S - 1)) = 3172907342664232231127405964387, at most 15423 checkpoints\nroutine entry points (instruction index): start 0, loop 26, hit 28, dpl 148, dp1 150, gather 194, record 392, probe 405, insert 429, ins 437, match0 440, cont 455, dl 458, restart 459, setwalk 471, evalF 1754, outm 1801, match 1845, meas 1857, measd 1870, bl 1894, walk0 1905, seg 1907, last 1927, lloop 1928, found 1941, end 1955\nn_instr            1955\nsetwalk            1283\nrestart            1294\nrestart_halt       3\nhit                121\nctz_clear          44\ngather             198\nrecord_slot        13\nprobe_word         24\ninsert             8\ndp_fixed           268\ndp_max             370444\ndl_final           1\ne_eval             6279\ne_outm             44\nmatch_entry        15\nmeas_iter          6289\nmeas_last          6285\nckpt               3\nadv_iter           6286\nbwalk_iter         6285\nseg_iter           14\nreplay_iter        12571\nreplay_gap         3172907342664232231127405964387\nreplay_rate        12575\nreplay_g           18857\nreplay_nck         17\nreplay_const       6406\nreplay_max         615426887083584574713207995517580845456\nsetup              351456\nother_bytes        15992\nother_literals     11\nprog_bytes         464959\npf_bytes           49\nsl_bytes           465008\nstatic opcode mix: OR 413 ANDI 337 SHRI 284 AND 266 SHL 258 SHLI 72 SHR 50 XOR 30 ADDI 26 MOV 25 MOVI 22 EQI 22 ST 20 BNZ 19 BZ 17 LDA 15 JMP 13 NOT 10 JAL 10 SUB 7 LTI 6 LD 6 EQ 5 HALT 5 SUBI 5 ADD 4 JR 3 LT 3 RND 1 PERM 1\nhighest register named: 2034 (file of 2036)\n",
"params.json": "{\n \"NR\": 23,\n \"HF\": 111,\n \"DPLO\": 145,\n \"DK\": 10,\n \"DT\": 584,\n \"S\": 15424,\n \"U\": 77120,\n \"SB\": 14,\n \"W\": 633825300114114700748351602688,\n \"J\": 77207,\n \"LRC\": 48935749945910453700677982188732416,\n \"Tb\": 1326663716884019821919338815169757184,\n \"HMAX\": 54118035032196129959512860308537345,\n \"PFLO\": 240,\n \"PFN\": 16\n}",
"stack.txt": "16384\n",
"scan_counts.txt": "float_evals 156190\nfloat_bins 2590117602\nexact_evals 21\nexact_bins 1621347\n"
}
# cert4.py - LS1 exact ledger at SHA3-256 round count NR: step count, success bound, N, memory, integer certificate
# (integers and Fractions; Decimal with 80 digits only for the exponentials and logarithms of the success bound).
#   python3 cert4.py            exact ledger of the row in this directory: ledger.txt (generator counts), size.txt
#                               (generator image), counts.txt (other code), params.json (search parameters)
#   (the parameter scan, which chooses the DP threshold, the replay cap, S, U, Tb and wrote params.json and scan_counts.txt, is the native program scan.c, Appendix D.5)
import sys, os, re, json, math
from fractions import Fraction as Fr
from decimal import Decimal as D, getcontext, ROUND_CEILING
getcontext().prec = 80
ceil = lambda v: int(v.to_integral_value(rounding=ROUND_CEILING)) if isinstance(v, D) else -((-v.numerator) // v.denominator)
try:
    INLINE                                       # the inputs written into this listing (proof.md Appendix A)
except NameError:
    INLINE = None                                # the factory run: the inputs are read from the row's files
rd = lambda p: INLINE[p] if INLINE else open(p).read()

# ---- one step of 256 walks (Section 3; counts printed by the generator gen3.c, ledger.txt) ----
led = rd('ledger.txt')
g = lambda k: int(re.search(r'^%s\s+(\d+)' % k, led, re.M).group(1))
NR = int(re.search(r'one chain step, (\d+) rounds', led).group(1))
XOR, AND, OR, NOT = g('XOR'), g('AND'), g('OR'), g('NOT')
LINE = XOR + AND + OR + NOT                      # the straight line, no loads or stores (registers, H_reg)
assert LINE == g('TOTAL')
REGUSED = int(re.search(r'registers used (\d+)', led).group(1)); assert REGUSED <= 2037
PF = 15                                          # prefilter: OR of the 16 planes 240..255
BSTEP = LINE + PF + 2 + 3                        # + compare pf with all-ones and branch; c += 1, compare with Tb, branch
UNIT = 271 * NR                                  # the cost model's price of one NR-round permutation
L = 256
n = D(2) ** 256
RPW = 5                                          # slots per table word (51 bits each: written bit and 50 key bits)
KEYB = 50                                        # key bits of a slot

# ---- the other code (Section 4.3): instruction count and routine counts of the emitted code (other4.py build) ----
def read_counts(p='counts.txt'):
    c = {}
    for line in rd(p).split(chr(10)):
        m = re.match(r'^([a-z_0-9]+)\s+(\d+)$', line.strip())
        if m: c[m.group(1)] = int(m.group(2))
    return c

CB = read_counts()                               # measured bytes of the emitted files (other4.py build, counts.txt)

# ---- memory (Section 6) ----
REGS = REGUSED + 11                                      # registers 0..REGUSED-1 by the straight line, REGUSED..REGUSED+9 search state, REGUSED+10 spare
sz = rd('size.txt').split('\n')[1].split()
GEN_IMAGE = int(sz[0]) + int(sz[1]) + int(sz[2])  # gen3: text + data + BSS, size(1); all arrays are static
GEN_STACK = int(rd('stack.txt')) if (INLINE or os.path.exists('stack.txt')) else 8192                                 # stack reserve; the run completes with the stack limited to this value (stack.txt, written by row4.sh)
GEN_HWM = int(re.search(r'VmHWM, this process image\) \d+ KiB = (\d+) bytes', led).group(1))
MARGIN = 0


def mem_search(S, NI):
    return {'register file, %d words' % REGS: 32 * REGS,
            'straight line incl. prefilter, %d instructions, two-address encoding (prog.bin + pf.bin)' % (LINE + PF): CB['sl_bytes'],
            'other code (setup, loop, handlers, restart, replay), %d instructions x 8 bytes + %d literals x 32 bytes' % (NI, CB['other_literals']): CB['other_bytes'],
            'table, %d words (five slots each)' % S: 32 * S,
            'walk words of the 256 walks (LST | LID << 128), 256 words': 32 * 256,
            'data image (lane constants K, PD, output pair), 16 words': 32 * 16}


def mem_pre():
    return max(GEN_HWM, GEN_IMAGE + GEN_STACK) + CB['prog_bytes']   # the generator (image and stack) plus the program it writes


def fit_S(NI):
    fixed = sum(mem_search(0, NI).values())
    S = (2 ** 20 - MARGIN - fixed) // 32 // 8 * 8
    while S + 100 >= 1 << S.bit_length(): S -= 8   # keeps 100 slots of room below 2^SB (routine tests)
    return S


def u_of(S): return RPW * S                      # trail limit: one slot per trail


# ---- the distinguished point: x < THR, THR = DT 2^(DPLO - DK); theta = DT 2^-(256 - DPLO + DK), exactly ----
def theta_of(DPLO, DK, DT): return D(DT) / D(2) ** (256 - DPLO + DK)


# ---- success probability (Section 5) ----
def success(Tb, theta, w, J, U, K, parts=False):
    """theta: the DP probability; w: bin width (steps, an integer); J: number of bins, the replay cap is LRC = J w;
    U: trail limit; K: key bits of a slot."""
    LRC = J * w; lq = (1 - theta).ln()
    mu, k = D(L * Tb) * theta, U - L
    if k <= mu: return (D(-1), None) if parts else D(-1)
    s, qprev = D(0), D(1)
    for j in range(1, J + 1):
        qj = (w * j * lq).exp()
        e = L * (Tb - j * w)
        if e > 1:
            s += (qprev - qj) * (1 - (-D(e) * (e - 1) / (2 * n)).exp())
        qprev = qj
    E = L * Tb                                               # evaluations of one attempt, at most
    G6 = ((LRC) * lq).exp() * (1 + LRC * theta)              # E g(age) of one evaluation (summation by parts)
    Ghi = 1 - (-D(E) * E / (2 * n) - D(E) ** 3 / (3 * n * n)).exp()   # 1 - pi_E: a coincidence among E evaluations, upper bound
    infl = (-D(U) * (1 - D(E) / n).ln()).exp()               # pi_(m-k) <= pi_m (1 - E/n)^-U for k <= U DPs
    e6 = 2 * G6 * Ghi * infl                                 # F6 (first coincidence): its pair has a trail longer than LRC
    e2 = (-mu + k * (1 + (mu / k).ln())).exp()               # F2: more than U - L distinguished points (Chernoff, k > mu)
    e3 = D(U) / (theta * theta * n)                          # F3: a coincidence inside one trail
    e4 = D(2) ** -90 + D(U) ** 2 * D(2) ** -(K + 1)          # F4: starts, replay, and two different ends with equal K key bits
    e5 = D(2) ** -1000                                       # F5: the hit counter passes HMAX (abort); bound proved below
    eL = D(2) ** -108 * (1 + e6)                              # FL: lemma (ii), the factor 1 + 2^-108 at the bin sum and at F6
    p = s - (e2 + e3 + e4 + e5 + e6 + eL + D(2) ** -60)
    return (p, (e6, e2, e3, e4)) if parts else p


def find_tb(theta, w, J, U, K, G, lo_t=None, hi_t=None):
    if hi_t is None:
        cap = int((D(U - L) / (D(L) * theta)) * D('0.999'))
        lo, hi, t = 2 ** 118, None, int(D(2) ** D('119.5'))
        while t <= min(2 ** 121, cap):
            if success(t // G * G, theta, w, J, U, K) >= D('0.39'): hi = t // G * G; break
            lo = t // G * G; t = int(t * D('1.01'))
        if hi is None: return None
    else:
        lo, hi = lo_t // G * G, hi_t // G * G
    while hi - lo > G:
        mid = (lo + hi) // 2 // G * G
        if success(mid, theta, w, J, U, K) >= D('0.39'): hi = mid
        else: lo = mid
    return hi


# ---- the ledger (Section 4) ----
def gap(LRC, S): return -(-LRC // (S - 1))                  # the checkpoint gap of the replay, G = ceil(LRC / (S - 1))


def ledger(TB, S, U, LRC, c, NI):
    G = gap(LRC, S); NCK = (LRC - 1) // G + 1                # at most one replay per attempt, lengths <= LRC
    replay = c['replay_rate'] * LRC + c['replay_g'] * G + c['replay_nck'] * NCK + c['replay_const']
    DELTA = Fr(1, 2 ** 20)
    HMAX = (TB * (1 + DELTA)) // 2 ** 8 + 1 + LRC            # the driver aborts (attempt failed) when hit number HMAX + 1 occurs
    MU = Fr(TB, 2 ** 8)
    EXPO = DELTA ** 2 * MU / (2 + DELTA)                     # P[F5] <= exp(-EXPO)
    assert EXPO > 1000 * Fr(6932, 10000)                     # ln 2 < 0.6932, so P[F5] < 2^-1000 (the e5 of success())
    hits = HMAX + 1                                          # at most HMAX + 1 hits are processed in every execution
    C_dp = c['dp_fixed'] + c['probe_word'] * S               # every DP passes the S words
    N_DP, N_RESTART = U - 255, U - 256
    Rr = (hits * c['hit'] + N_DP * C_dp + N_RESTART * (c['restart'] + 3) + c['restart_halt'] + c['dl_final'] + c['setup'])
    return replay, HMAX, Rr, EXPO


def sha_blocks(n): return (n + 9 + 63) // 64                 # SHA-256 blocks of an n-byte file


def pre_ops(NI):
    """preprocessing = every step whose output the search uses, each run once before the search (proof.md Section 3.7):
    G: the run `gen3 512 1000 4`: build count B (2^32 operations each),
       annealing iterations A (2^12 each, the rolling-horizon move and its undo), per trial 2^10 (constants, count, comparison, line)
       and 2^32 for the plan's row tables;
    K: the constant basis (kbasis.h): Gaussian elimination of 704 equations in 768 bits, at most 2^24;
    P: the parameter scan (scan.c; counts in scan_counts.txt): float-model bins and evaluations 2^16 and 2^17 each,
       exact bins and evaluations 2^24 and 2^27 each, grid bookkeeping 2^20;
    O: `other4.py build`: 2^8 per emitted instruction, 2^13 per SHA-256 block of other.bin, pf.bin and data.bin, data image 2^12."""
    SWEEPS = 3; TOPK = int(re.search(r'^trials carried to the plan build (\d+)', led, re.M).group(1)); OPTIT = int(re.search(r'^annealing iterations per round (\d+)', led, re.M).group(1))
    plan_builds = 1 + SWEEPS * (320 * 31 + 320) + (NR - 1) + 1                # round-1 greedy (prefix builds counted as full) and the passes
    B = 512 + TOPK * (plan_builds + 1) + (plan_builds + 1)
    m_ = re.search(r'^round-1 row search builds per plan (\d+)', led, re.M)   # design X: the exact round-1 row search
    if m_: B += (TOPK + 1) * int(m_.group(1))
    A = (TOPK + 1) * (NR - 1) * OPTIT
    G = B * 2 ** 32 + A * 2 ** 12 + 512 * 2 ** 10 + 2 ** 32   # + the plan's row tables (mk_tables2), one build's charge
    K = 2 ** 24
    sc = {l.split()[0]: int(l.split()[1]) for l in rd('scan_counts.txt').split(chr(10)) if l.strip()}
    P_ = (sc['float_bins'] << 16) + (sc['float_evals'] << 17) + (sc['exact_bins'] << 24) + (sc['exact_evals'] << 27) + 2 ** 20
    HB = sha_blocks(CB['other_bytes']) + sha_blocks(CB['pf_bytes']) + sha_blocks(32 * 16)
    O = NI * 2 ** 8 + HB * 2 ** 13 + 2 ** 12
    return G + K + P_ + O, B, A, (G, K, P_, O, HB, sc)


def cert(N):
    K = 100000
    e = ceil(K * (D(N) / UNIT).ln() / D(2).ln())
    while N ** K > (UNIT ** K) << e: e += 1
    while N ** K <= (UNIT ** K) << (e - 1): e -= 1
    return K, e



# ---------------- the exact ledger ----------------
P = json.loads(rd('params.json'))
assert P['NR'] == NR
HF, DPLO, DK, DT, S, U, TB, W, J, LRC = P['HF'], P['DPLO'], P['DK'], P['DT'], P['S'], P['U'], P['Tb'], P['W'], P['J'], P['LRC']
c = read_counts(); NI = c['n_instr']
THETA = theta_of(DPLO, DK, DT)
GRAN = 2 ** (HF - 20)
assert DPLO == 256 - HF and 0 < DT < 2 ** DK and DK >= 1 and 2 ** (DK - 1) <= DT                 # 1/2 <= DT / 2^DK < 1
assert TB % GRAN == 0 and LRC == J * W and W == 2 ** (HF - 12) and P['SB'] == S.bit_length() and U <= RPW * S
assert DPLO - DK > KEYB
print('rounds %d, unit %d word operations' % (NR, UNIT))
print('step of 256 walks: straight line', LINE, '(xor %d and %d or %d not %d) + prefilter %d + test 2 + counter 3 =' % (XOR, AND, OR, NOT, PF), BSTEP)
print('parameters: DP = planes %d..255 zero and the %d planes below them < %d (theta = %d x 2^-%d = 2^-%.6f), replay cap LRC = %d x %d = %.4f / theta, U %d trails, S %d table words (%d slots), key bits %d'
      % (DPLO, DK, DT, DT, 256 - DPLO + DK, -math.log2(THETA), J, W, LRC * THETA, U, S, RPW * S, KEYB))
p, (e6, e2, e3, e4) = success(TB, THETA, W, J, U, KEYB, parts=True)
p_less = success(TB - GRAN, THETA, W, J, U, KEYB)
assert p >= D('0.39') > p_less
print('Tb = %d = %d * 2^%d = %.8f * 2^120, evaluations %.6f * 2^128' % (TB, TB // GRAN, HF - 20, D(TB) / D(2) ** 120, D(L * TB) / D(2) ** 128))
print('failure terms: F6 %s  F2 %s  F3 %s  F4 %s  success bound %s  (2^%d steps fewer: %s)' % tuple([format(x, '.3e') for x in (e6, e2, e3, e4)] + [str(p)[:12], HF - 20, str(p_less)[:12]]))
lg = lambda x: -(D(x).ln() / D(2).ln())
EL = L * TB; la, lb, lc = D(U) * EL / n, D(EL) ** 2 * THETA / (2 * n), D(U) ** 2 / (2 * THETA * n)   # lemma (ii), Section 5
fct = (-D(U) * (1 - D(EL) / n).ln()).exp() / (1 - (la + lb + lc))
assert la + lb + lc < D(2) ** -109 and fct - 1 < D(2) ** -108
print('lemma (ii): U E/n = 2^-%.1f, E^2 theta/(2n) = 2^-%.1f, U^2/(2 theta n) = 2^-%.1f, delta < 2^-109, (1 - E/n)^-U / (1 - delta) = 1 + 2^-%.1f, FL = %s'
      % (lg(la), lg(lb), lg(lc), lg(fct - 1), format(D(2) ** -108 * (1 + e6), '.3e')))
replay, HMAX, Rr, EXPO = ledger(TB, S, U, LRC, c, NI)
assert HMAX == P['HMAX']
print('hit counter: HMAX =', HMAX, '; P[abort before the stop on success] <= exp(-%d) < 2^-1000' % (EXPO.numerator // EXPO.denominator))
GC = gap(LRC, S); assert GC == c['replay_gap']
print('replay: %d LRC + %d G + %d nck + %d = %d (G = %d, nck = %d; measuring walk e + 10, walk of b e + 7, lock step 2e + 13, e = %d)' % (
    c['replay_rate'], c['replay_g'], c['replay_nck'], c['replay_const'], replay, GC, (LRC - 1) // GC + 1, c['e_eval']))
assert c['e_eval'] == UNIT + 46   # design X message setup: 43 instructions (LS1: 26)
PRE, B, A, PP = pre_ops(NI)
N = TB * BSTEP + replay + Rr + PRE
print('main', TB * BSTEP, ' replay', replay, ' rare', Rr, ' preprocessing', PRE, '(builds %d, annealing iterations %d)' % (B, A))
print('preprocessing parts: generator %d basis %d scan %d assembly %d (scan: float evaluations %d bins %d, exact evaluations %d bins %d; SHA-256 blocks %d)'
      % (PP[0], PP[1], PP[2], PP[3], PP[5]['float_evals'], PP[5]['float_bins'], PP[5]['exact_evals'], PP[5]['exact_bins'], PP[4]))
pl = 0
while (UNIT << pl) < PRE: pl += 1
print('preprocessing_log2: 2^%d < PRE / %d <= 2^%d, declared %d' % (pl - 1, UNIT, pl, pl))
print('N =', N)
print('shares: main %.5f replay %.5f other %.2e' % (TB * BSTEP / N, replay / N, (Rr + PRE) / N))
ms = mem_search(S, NI)
run_total = sum(ms.values()); pre_total = mem_pre()
for k, v in ms.items(): print('  %9d  %s' % (v, k))
print('search memory', run_total, '; preprocessing (gen3): image', GEN_IMAGE, '+ stack', GEN_STACK, '+ program', CB['prog_bytes'], '=', pre_total, '(measured resident peak %d)' % GEN_HWM)
mem = max(run_total, pre_total)
assert mem <= 2 ** 20 - MARGIN
print('memory', mem, '<= 2^20 = 1048576 with a margin of', 2 ** 20 - mem, 'bytes (search phase', 2 ** 20 - run_total, ', preprocessing', 2 ** 20 - pre_total, '): memory_log2_bytes = 20')
K, e = cert(N)
print('certificate: %d^%d * 2^%d < N^%d <= %d^%d * 2^%d' % (UNIT, K, e - 1, K, UNIT, K, e))
print('time_log2 = %d.%05d' % divmod(e, K))
print('score = time_log2 (memory reviewed separately) = %d.%05d' % divmod(e, K))
```

Output:

```
rounds 23, unit 6233 word operations
step of 256 walks: straight line 136662 (xor 100288 and 18704 or 14509 not 3161) + prefilter 15 + test 2 + counter 3 = 136682
parameters: DP = planes 145..255 zero and the 10 planes below them < 584 (theta = 584 x 2^-121 = 2^-111.810175), replay cap LRC = 77207 x 633825300114114700748351602688 = 10.7500 / theta, U 77120 trails, S 15424 table words (77120 slots), key bits 50
Tb = 1326663716884019821919338815169757184 = 535835208 * 2^91 = 0.99807085 * 2^120, evaluations 0.998071 * 2^128
failure terms: F6 1.977e-4  F2 2.144e-15  F3 1.380e-5  F4 2.641e-6  success bound 0.3900000004  (2^91 steps fewer: 0.3899999993)
lemma (ii): U E/n = 2^-111.8, E^2 theta/(2n) = 2^-112.8, U^2/(2 theta n) = 2^-112.7, delta < 2^-109, (1 - E/n)^-U / (1 - delta) = 1 + 2^-110.2, FL = 3.082e-33
hit counter: HMAX = 54118035032196129959512860308537345 ; P[abort before the stop on success] <= exp(-2356627043343743856968) < 2^-1000
replay: 12575 LRC + 18857 G + 17 nck + 6406 = 615426887083584574713207995517580845456 (G = 3172907342664232231127405964387, nck = 15423; measuring walk e + 10, walk of b e + 7, lock step 2e + 13, e = 6279)
main 181331050151141597299579067935032751423488  replay 615426887083584574713207995517580845456  rare 6548282238895731725101056125907240994  preprocessing 1037604497543936 (builds 189430, annealing iterations 6600000000)
preprocessing parts: generator 840633550372864 basis 16777216 scan 196970927751168 assembly 2642688 (scan: float evaluations 156190 bins 2590117602, exact evaluations 21 bins 1621347; SHA-256 blocks 261)
preprocessing_log2: 2^37 < PRE / 6233 <= 2^38, declared 38
N = 181953025320464077606017378024280737053874
shares: main 0.99658 replay 0.00338 other 3.60e-05
      65152  register file, 2036 words
     465008  straight line incl. prefilter, 136677 instructions, two-address encoding (prog.bin + pf.bin)
      15992  other code (setup, loop, handlers, restart, replay), 1955 instructions x 8 bytes + 11 literals x 32 bytes
     493568  table, 15424 words (five slots each)
       8192  walk words of the 256 walks (LST | LID << 128), 256 words
        512  data image (lane constants K, PD, output pair), 16 words
search memory 1048424 ; preprocessing (gen3): image 534918 + stack 16384 + program 464959 = 1016261 (measured resident peak 466944)
memory 1048424 <= 2^20 = 1048576 with a margin of 152 bytes (search phase 152 , preprocessing 32315 ): memory_log2_bytes = 20
certificate: 6233^100000 * 2^12445690 < N^100000 <= 6233^100000 * 2^12445691
time_log2 = 124.45691
score = time_log2 (memory reviewed separately) = 124.45691
```

## Appendix B. The generator (gen3.c) and the self-test (selftest.c)

Compiled with `gcc -O2 -static -nostdlib -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns -fno-stack-protector -fno-pie -no-pie -DNR=23 -DR1ROW=2 -DR1LOOK=3 -DOPTIT=150000000 -DMAXF=2048`; run as `gen3 512 1000 8`.

```c
/* gen3.c - LS1 step generator for sha3-256-rNR (NR prefix rounds of Keccak-f[1600]), streaming version.
 * Freestanding (no libc, static arrays only) so the measured peak resident memory is the generator's own working set.
 *
 * Chain function on physical 256-bit points u (4 lanes u0..u3):
 *   message m(u) = 128 bytes = lanes 0..15 of the absorbed state:
 *     lane 1 = u0, lane 6 = u1, lane 11 = u0^u1^K[11]   (column x=1, rows 0,1,2)
 *     lane 4 = u2, lane 9 = u3, lane 14 = u2^u3^K[14]   (column x=4, rows 0,1,2)
 *     other lanes 0..15 = constants K[l]; lane 16 = 0x8000000000000006 (SHA3 pad);
 *   F(u) = SHA3-256-rNR(m(u)) XOR PD   (PD = fixed digest polarity mask of the program).
 * Round 0 is linear in u and round-1 theta stays linear (Guo-Liu-Song 2016 linear structure).
 *
 * Representation: plane (lane,z) is one 256-bit word (bit t = walk t). A value is (node, polarity):
 * logical = physical(node) XOR p. Constants folded. Linear nodes (rounds 0 and 1) carry their GF(2) form over the
 * 256 input bits, deduplicated by form. Lazy theta: C, D per round; each chi row XORs D into its five planes.
 * Chi row: complement subset s (NOTs) and, optionally, the 10-gate form (TRICK): output j reads the finished output
 * k = j+1 instead of input k, since (NOT a_k) AND a_{k+1} = (NOT chi_k) AND a_{k+1}.
 * Polarity plan (optmode >= 1): per round, NOTs on theta parities C and on D chosen by simulated annealing against the
 * exact row-cost table; optmode >= 2 adds the free output polarity of the two-operation terms (A^(A&B) or (NOT A)|B);
 * optmode 3 adds a greedy pass over the round-1 C/D complements.
 * optmode 4 (rolling horizon, polopt2): for each round r >= 2 except the last, one annealing chooses the C and D NOTs
 * together with the output polarity vector of every chi row, minimising SC x (row costs of round r + NOTs) + WLOOK x
 * (a lower estimate of the row costs of round r + 1 that those output polarities give); each row then takes the cheapest
 * decision (complement subset, 10-gate position, term polarities) that yields its chosen outputs (tables ROWCt / ARGt).
 * optmode 5 (polarity masks and output complements; the plan this entry uses with design X): (a) the D NOT of a lane (x,z) is a 5-bit mask
 * F[x][z]: one NOT builds D' = NOT D (one operation when the mask is not 0), and the chi row y of that lane reads D' where bit y
 * of the mask is 1 and D where it is 0 (the mask 31 is the whole-lane NOT of optmode 4); at most PCAP lanes of a round have a
 * mask other than 0 and 31. (b) A planned row may NOT outputs after they are computed: an output complement E (5 bits, one
 * operation per set bit) is part of the row table (ARGE), so a row output vector o is reached as the output of a decision
 * (s, T, mc) with o' = o xor E. (c) Round 1 is planned like the later rounds: polopt1 anneals the output polarity vectors of
 * the round-1 rows with the lookahead of round 2 (rows with five distinct variable inputs; the others keep the row_choose
 * decision), and the round-1 C and D complements are the greedy 5-bit masks F1 (each lane: the best of the 32 masks, three
 * sweeps) and the 1-bit G1. Every decision (F1, G1, FG, DEC, DECE, PHI) is written to plan.txt by the check run.
 *
 * STREAMING: nodes live in a ring of W slots that holds ONE round (rounds 0 and 1 together). When a round is built,
 * its dead nodes are removed (liveness from the state planes, or from the digest planes in the last round), every
 * value gets its last use (all uses of a value lie in its own round or, for a state plane, in the next round), the
 * registers are allocated in node order and the instructions are written to prog.bin at once. The 1,600 state planes
 * are then pinned (register and flags) and the ring is reused for the next round. The program is never held.
 * Register j (j < 256) holds input plane j and receives digest plane j (free chain feed).
 * Allocation: a value takes the lowest register of an operand that dies at it, when it may use that register (then the
 * instruction has destination = first operand); otherwise the LOWEST free register it may use. Registers 0..255 are open to every value that dies
 * before the last round, except the state planes of lanes 0, 6, 12, 18, 24 after round NR-2 (they feed the digest row);
 * in the last round register j < 256 is open to a value whose last use is not after the definition of digest plane j.
 * With these rules the program names as many registers as the maximum number of live values (ledger: registers used), below 2^11.
 *
 * Outputs of the charged run (gen3 512 1000 8): the file prog.bin (two-address encoding, packed little-endian: 2-bit op, 1-bit t;
 * t=1: dst = a, then a and (not NOT) b; t=0: dst, a and (not NOT) b; registers 11 bits; 14, 25 or 36 bits) and the ledger on
 * standard output. No other file is written. The separate inspection command (gen3 1 TRIAL 8 inspect), a check run, writes
 * meta.txt and plan.txt (the decisions of the plan, read by the Python port); the search does not run it.
 * Usage: gen3 ntrials first optmode.  ntrials > 1: the cheap build (optmode 0) of trials first..first+ntrials-1, the
 * full build (optmode) of the TOPK lowest of them, and the lowest full count wins.  The search runs "gen3 512 1000 8". SC = 16, WLOOK = 3, OPTIT = 600,000,000, PCAP = 100.
 * optmode 8 (this entry): the design X embedding of mpjunior92 11565cb4 (set_consts, build: lanes x and 10+x carry v_x ^ K) with the
 * optmode-5 plan; compiled with -DR1ROW=2 -DR1LOOK=3, the round-1 rows with a constant input are first decided by the exact
 * row search r1rowopt (two sweeps, objective 16 x ops of rounds 0..1 + 3 x round-2 row minima); plan.txt adds R1OV and R1E.
 */
typedef unsigned long u64; typedef unsigned int u32; typedef unsigned short u16; typedef unsigned char u8;
typedef long i64;

/* ---------- freestanding runtime ---------- */
__asm__(".global _start\n_start:\n xor %rbp,%rbp\n mov %rsp,%rdi\n and $-16,%rsp\n call cmain\n mov %rax,%rdi\n mov $60,%rax\n syscall\n");
static i64 sc3(i64 n, i64 a, i64 b, i64 c){ i64 r; __asm__ volatile("syscall":"=a"(r):"a"(n),"D"(a),"S"(b),"d"(c):"rcx","r11","memory"); return r; }
void *memset(void *d, int c, unsigned long n){ u8 *p=d; while(n--) *p++=(u8)c; return d; }
void *memcpy(void *d, const void *s, unsigned long n){ u8 *p=d; const u8 *q=s; while(n--) *p++=*q++; return d; }
static int fd_out = 1;
static char obuf[4096]; static int olen;
static void oflush(void){ if(olen){ sc3(1,fd_out,(i64)obuf,olen); olen=0; } }
static void oc(char c){ if(olen==4096) oflush(); obuf[olen++]=c; }
static void os(const char *s){ while(*s) oc(*s++); }
static void ou(u64 v){ char t[24]; int n=0; do{ t[n++]='0'+v%10; v/=10; }while(v); while(n) oc(t[--n]); }
static void ox(u64 v){ for(int i=60;i>=0;i-=4) oc("0123456789abcdef"[(v>>i)&15]); }
static void ox8(u8 v){ oc("0123456789abcdef"[v>>4]); oc("0123456789abcdef"[v&15]); }
static int fopen_w(const char *p){ return (int)sc3(2,(i64)p,01|0100|01000,0644); } /* O_WRONLY|O_CREAT|O_TRUNC */
static void fclose_(int fd){ sc3(3,fd,0,0); }
static void die(const char *m){ oflush(); fd_out=2; os("gen3: "); os(m); oc('\n'); oflush(); sc3(60,1,0,0); }
static int atoi_(const char *s){ int v=0; while(*s>='0'&&*s<='9') v=v*10+(*s++-'0'); return v; }

/* ---------- Keccak constants ---------- */
static const u64 RC[24]={0x0000000000000001UL,0x0000000000008082UL,0x800000000000808aUL,0x8000000080008000UL,
 0x000000000000808bUL,0x0000000080000001UL,0x8000000080008081UL,0x8000000000008009UL,0x000000000000008aUL,
 0x0000000000000088UL,0x0000000080008009UL,0x000000008000000aUL,0x000000008000808bUL,0x800000000000008bUL,
 0x8000000000008089UL,0x8000000000008003UL,0x8000000000008002UL,0x8000000000000080UL,0x000000000000800aUL,
 0x800000008000000aUL,0x8000000080008081UL,0x8000000000008080UL,0x0000000080000001UL,0x8000000080008008UL};
static const int ROT[5][5]={{0,36,3,41,18},{1,44,10,45,2},{62,6,43,15,61},{28,55,25,21,56},{27,20,39,8,14}}; /* ROT[x][y] */
#ifndef NR
#define NR 8
#endif
#ifndef TRICK
#define TRICK 1          /* 10-gate chi rows */
#endif
#ifndef LASTTRICK
#define LASTTRICK 1      /* 10-gate rows also in the last (four-output) round */
#endif
#ifndef NOTFOLD
#define NOTFOLD 0        /* NOT of a NOT node = its operand */
#endif
#ifndef OPTIT
#define OPTIT 600000000
#endif
#ifndef CHAIN
#define CHAIN 1          /* acyclic chained trick masks in the row tables */
#endif
#ifndef OUTNOT
#define OUTNOT 1
#endif
#ifndef F1MASK
#define F1MASK 1
#endif
#ifndef PCAP
#define PCAP 100
#endif
#ifndef TOPK
#define TOPK 1           /* trials carried from the cheap selection to the full build */
#endif
#ifndef R1SAIT
#define R1SAIT 100000
#endif
#ifndef R1SWEEPS
#define R1SWEEPS 3
#endif

/* ---------- node ring (one round) and pinned state planes ---------- */
#define W 8192
#define PIN 8192             /* ids PIN..PIN+1599: the 1,600 state planes of the previous round */
#define NC 0xFFFF            /* constant marker */
#define NOUSE 0xFFFF
enum { O_IN=0, O_XOR=1, O_AND=2, O_OR=3, O_NOT=4 };
#define F_OPM 7
#define F_K 8                /* physical constant of a linear node */
#define F_LIVE 16
#define F_LIN 32
#define F_ST 64              /* a state plane: its uses continue in the next round */
#define F_OUT 128            /* a digest plane */
static u8 nf[W];
static u16 na[W], nb[W], nlast[W], nreg[W], linid[W];
static int nn;
static u8 pfl[1600]; static u16 preg[1600], plast[1600]; static int npin;
static u16 pord[1600];       /* ring index of the plane's node in its own round (operand order as in node order) */
static int okey(int n){ return n>=PIN? pord[n-PIN] : n+W; }
#define CH 8192
static u16 ch[CH];           /* cons hash: ring index+1 */
#ifndef MAXF
#define MAXF 3600
#endif
static u64 form[MAXF][4]; static u16 formnode[MAXF]; static int nform, maxform;
#define FH 8192
static int designx;          /* optmode 8..10: design X embedding (credited derivative of mpjunior92 11565cb4), planning as optmode-3 */
static u16 fh[FH];           /* form hash: form index+1 */

typedef struct { u16 n; u8 p; } V;
static V K_(int c){ V v; v.n=NC; v.p=(u8)c; return v; }
static V MK(int n,int p){ V v; v.n=(u16)n; v.p=(u8)p; return v; }
static u8 NF(int n){ return n>=PIN? pfl[n-PIN] : nf[n]; }

static u32 hmix(u32 x){ x^=x>>16; x*=0x7feb352dU; x^=x>>15; x*=0x846ca68bU; x^=x>>16; return x; }
static int maxring;
static int newnode(int op,int a,int b){ if(nn>=W) die("ring overflow"); nf[nn]=(u8)op; na[nn]=(u16)a; nb[nn]=(u16)b; linid[nn]=0xFFFF; nlast[nn]=NOUSE;
  if(nn+1>maxring) maxring=nn+1; return nn++; }
static int cons(int op,int a,int b){
  if(op!=O_NOT && okey(a)>okey(b)){ int t=a;a=b;b=t; }
  u32 h=hmix((u32)op*0x9E3779B1u ^ (u32)a*0x85EBCA77u ^ (u32)b*0xC2B2AE3Du)&(CH-1);
  for(;;){ u16 e=ch[h]; if(!e) break; int m=e-1; if((nf[m]&F_OPM)==op && na[m]==a && nb[m]==b) return m; h=(h+1)&(CH-1); }
  int m=newnode(op,a,b); ch[h]=(u16)(m+1); return m;
}
static int isk(int n){ return (NF(n)&F_K)?1:0; }
static int islin(int n){ return (NF(n)&F_LIN)?1:0; }
static u32 fhash(const u64 *m){ return hmix((u32)(m[0]^m[0]>>32^m[1]*3^m[2]*5^m[3]*7^(m[1]>>29)^(m[3]>>31))); }
static int flookup(const u64 *m){ u32 h=fhash(m)&(FH-1); for(;;){ u16 e=fh[h]; if(!e) return -1; int f=e-1; if(form[f][0]==m[0]&&form[f][1]==m[1]&&form[f][2]==m[2]&&form[f][3]==m[3]) return f; h=(h+1)&(FH-1);} }
static int fadd(const u64 *m,int node){ if(nform>=MAXF) die("form overflow"); int f=nform++; if(nform>maxform) maxform=nform; for(int i=0;i<4;i++) form[f][i]=m[i]; formnode[f]=(u16)node;
  u32 h=fhash(m)&(FH-1); while(fh[h]) h=(h+1)&(FH-1); fh[h]=(u16)(f+1); return f; }

static long cnt_emit; /* ops created (pre-DCE) */

static V xorv(V a,V b){
  if(a.n==NC) return MK(b.n==NC?NC:b.n, b.p^a.p);
  if(b.n==NC) return MK(a.n, a.p^b.p);
  if(a.n==b.n) return K_(a.p^b.p);
  if(islin(a.n)&&islin(b.n)){
    const u64 *fa=form[linid[a.n]], *fb=form[linid[b.n]]; u64 m[4];
    for(int i=0;i<4;i++) m[i]=fa[i]^fb[i];
    int kk=isk(a.n)^isk(b.n);
    if(!(m[0]|m[1]|m[2]|m[3])) return K_(kk^a.p^b.p);
    int f=flookup(m);
    if(f>=0){ int n3=formnode[f]; return MK(n3, kk^a.p^b.p^isk(n3)); }
    int n=newnode(O_XOR,a.n<b.n?a.n:b.n,a.n<b.n?b.n:a.n); nf[n]|=F_LIN|(kk?F_K:0);
    linid[n]=(u16)fadd(m,n); cnt_emit++; return MK(n,a.p^b.p);
  }
  int before=nn; int n=cons(O_XOR,a.n,b.n); if(nn>before) cnt_emit++;
  return MK(n,a.p^b.p);
}
static V notv(V a){ /* physical complement, logical value unchanged */
  if(a.n==NC) return a;
#if NOTFOLD
  if(a.n<PIN && (nf[a.n]&F_OPM)==O_NOT && !(nf[a.n]&F_LIN)) return MK(na[a.n], a.p^1);
#endif
  int before=nn; int n=cons(O_NOT,a.n,0);
  if(nn>before){ cnt_emit++; if(islin(a.n)){ nf[n]|=F_LIN|(isk(a.n)?0:F_K); linid[n]=linid[a.n]; } }
  return MK(n,a.p^1);
}
static int curmix_sel, curmix_flag;
static V and2(V a,V b){ /* logical a AND b */
  if(a.n==NC) return a.p? b : K_(0);
  if(b.n==NC) return b.p? a : K_(0);
  if(a.n==b.n) return a.p==b.p? a : K_(0);
  int before=nn;
  if(a.p==0&&b.p==0){ int n=cons(O_AND,a.n,b.n); if(nn>before) cnt_emit++; return MK(n,0); }
  if(a.p==1&&b.p==1){ int n=cons(O_OR,a.n,b.n); if(nn>before) cnt_emit++; return MK(n,1); }
  /* A & ~B with A the pol-0 operand: A ^ (A & B), or (NOT A) OR B (the complement, output polarity 1) */
  int A=a.p==0?a.n:b.n, B=a.p==0?b.n:a.n;
  curmix_flag=1;
  if(curmix_sel){ V na_=notv(MK(A,0)); int before2=nn; int n=cons(O_OR,na_.n,B); if(nn>before2) cnt_emit++; return MK(n,1); }
  int t=cons(O_AND,A,B); if(nn>before) cnt_emit++;
  return xorv(MK(A,0),MK(t,0));
}
static V andnot(V b1,V b2){ b1.p^=1; return and2(b1,b2); } /* (~b1) & b2 */

/* cost estimate of (~b1)&b2 given polarities */
static int cost_term(V b1,V b2){ if(b1.n==NC||b2.n==NC||b1.n==b2.n) return 0; return ((b1.p^1)==b2.p)?1:2; }

/* ---------- chi row decision ---------- */
static int mixfree;          /* optmode >= 2: the output polarity of a two-operation term is free */
static int row_choose(const V *b,int needmask,int *bj_out,int *bc_out){
  int best=-1,bc=1<<30,bj=-1;
  int distinct=1; for(int X=0;X<5;X++){ if(b[X].n==NC) distinct=0; for(int Y=X+1;Y<5;Y++) if(b[X].n==b[Y].n) distinct=0; }
  int jmax=(TRICK&&distinct)?5:0;
  for(int j=-1;j<jmax;j++){
    if(j>=0){ int k=(j+1)%5; if(!((needmask>>j)&1)||!((needmask>>k)&1)) continue; if(needmask!=0x1F && !LASTTRICK) continue; }
    for(int s=0;s<32;s++){
      int c=0; V bb[5];
      for(int X=0;X<5;X++){ bb[X]=b[X]; if(s>>X&1){ if(b[X].n==NC){ c=1<<29; } else { bb[X].p^=1; c++; } } }
      for(int X=0;X<5;X++) if(needmask>>X&1){
        if(X==j){ int k=(j+1)%5; V p1=bb[(k+1)%5], p2=bb[(k+2)%5];
          if((p1.p^1)==p2.p){ int orc=((p1.p^1)==1); V bk=bb[k]; bk.p^=orc; c+=cost_term(bk,bb[(X+2)%5]); }
          else if(mixfree) c+=1;
          else c+=cost_term(bb[k],bb[(X+2)%5]);
        }
        else c+=cost_term(bb[(X+1)%5],bb[(X+2)%5]);
      }
      if(c<bc){ bc=c; best=s; bj=j; }
    }
  }
  *bj_out=bj; if(bc_out) *bc_out=bc; return best;
}
/* table for rows with five distinct variable inputs: decision by the 5-bit polarity pattern */
static signed char tS[2][2][32], tJ[2][2][32]; static int tC[2][2][32];   /* [last][mixfree][pattern] */
static void mk_tables(void){
  for(int L=0;L<2;L++) for(int mf=0;mf<2;mf++) for(int p=0;p<32;p++){
    V b[5]; for(int X=0;X<5;X++) b[X]=MK(X,(p>>X)&1);
    int sv=mixfree; mixfree=mf; int bj,bc; int s=row_choose(b,L?0x0F:0x1F,&bj,&bc); mixfree=sv;
    tS[L][mf][p]=(signed char)s; tJ[L][mf][p]=(signed char)bj; tC[L][mf][p]=bc; }
}

/* ---------- the step ---------- */
static V S[25][64], NS[25][64], Cc[5][64], Dd[5][64], Dd2[5][64];
/* ---------- polarity plan ----------
 * Per round r (2..NR-1): choose physical complements (NOT) on theta column parities C[x][z] (each toggles 10 chi
 * inputs) and on D[x][z] (each toggles 5 chi inputs, one in each of 5 rows), and the output polarity of the free
 * two-operation terms of round r-1, so that the sum over the rows of the exact row cost (table tC) plus the number of
 * these NOTs is minimal. Simulated annealing, deterministic xorshift, OPTIT iterations per round. */
static int optmode=1;
static u8 phib[NR][200], mixb[NR][200]; /* bit (l*64+z): output polarity choice / free-term flag of plane (l,z) */
#define GETB(a,r,l,z) ((a[r][((l)*64+(z))>>3]>>(((l)*64+(z))&7))&1)
#define TGLB(a,r,l,z) (a[r][((l)*64+(z))>>3]^=(u8)(1<<(((l)*64+(z))&7)))
#define SETB(a,r,l,z,v) (a[r][((l)*64+(z))>>3]=(u8)((a[r][((l)*64+(z))>>3]&~(1<<(((l)*64+(z))&7)))|((v)<<(((l)*64+(z))&7))))
static u8 FMb[NR][320], GGb[NR][40]; static u8 decided[NR]; static int curpass;
#define GB(a,i) ((a[(i)>>3]>>((i)&7))&1)
static u8 F1[5][64], G1[5][64];
static u8 fflip[5][64], gflip[5][64];
static long pol_pred[NR], pol_nots[NR], pol_phi[NR];
static u64 prs;
static double mexp(double x){ if(x<-40) return 0; double y=x/64; double e=1+y+y*y/2+y*y*y/6+y*y*y*y/24; for(int i=0;i<6;i++) e*=e; return e; }
static u64 pxs(void){ prs^=prs<<13; prs^=prs>>7; prs^=prs<<17; return prs; }

static void polopt(int r,int last){
  static u8 pS[25][64]; static u16 vrow[5][64][5]; static u8 vbit[5][64][5]; static u8 pat[320];
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if((v.n==NC && !designx)||(v.n!=NC && islin(v.n))) return; pS[l][z]=v.p; }   /* design X: a constant plane enters as its value */
  static u8 pC[5][64], pD[5][64];
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ int p=0; for(int y=0;y<5;y++) p^=pS[x+5*y][z]; pC[x][z]=(u8)p; }
  for(int x=0;x<5;x++) for(int z=0;z<64;z++) pD[x][z]=pC[(x+4)%5][z]^pC[(x+1)%5][(z+63)&63];
  for(int i=0;i<320;i++) pat[i]=0;
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++){
    int Y=(2*(x-y)+10)%5, z=(zz+ROT[x][y])&63; int row=Y*64+z;
    vrow[x][zz][y]=(u16)row; vbit[x][zz][y]=(u8)(1<<y);
    if(pS[x+5*y][zz]^pD[x][zz]) pat[row]|=(u8)(1<<y);
  }
  const int *rt0=tC[0][mixfree], *rtL=tC[1][mixfree];
  #define RT(i,p) (last? ((i)<64? rtL[p]:0) : rt0[p])
  static u16 fv[1600]; int nfv=0; static u8 phic[25][64]; memset(phic,0,sizeof phic);
  for(int l=0;l<25;l++) for(int z=0;z<64;z++) if(GETB(mixb,r-1,l,z)) fv[nfv++]=(u16)(l*64+z);
  long cost=0; for(int i=0;i<320;i++) cost+=RT(i,pat[i]);
  static u8 bestf[5][64], bestg[5][64]; long best=cost; int nfl=0;
  memset(fflip,0,sizeof fflip); memset(gflip,0,sizeof gflip); memcpy(bestf,fflip,sizeof fflip); memcpy(bestg,gflip,sizeof gflip);
  prs=0x2545F4914F6CDD1DUL ^ (u64)r*0x9E3779B97F4A7C15UL;
  #define TOGD(x,zz) for(int k=0;k<5;k++){ int rw=vrow[x][zz][k]; cost-=RT(rw,pat[rw]); pat[rw]^=vbit[x][zz][k]; cost+=RT(rw,pat[rw]); }
  #define TOGV(x,y,zz) { int rw=vrow[x][zz][y]; cost-=RT(rw,pat[rw]); pat[rw]^=vbit[x][zz][y]; cost+=RT(rw,pat[rw]); }
  static u8 bestp[25][64]; memcpy(bestp,phic,sizeof phic);
  double T0=1.2;
  for(long it=0; it<OPTIT; it++){
    double T=T0*mexp(-3.1780538303479458*(double)it/(double)OPTIT);
    u64 rv=pxs(); int mv=(int)(rv%3); int x=(int)((rv>>2)%5); int zz=(int)((rv>>8)&63);
    int pl=0, py=0;
    if(mv==2){ if(!nfv) mv=(int)(rv>>20)&1; else { int q=fv[(rv>>20)%nfv]; pl=q>>6; zz=q&63; x=pl%5; py=pl/5; } }
    int isg=mv;
    long c0=cost; int nf0=nfl;
    if(mv==0){ TOGD(x,zz); fflip[x][zz]^=31; nfl+= fflip[x][zz]?1:-1; }
    else if(mv==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGD(x1,zz); TOGD(x2,z2); gflip[x][zz]^=1; nfl+= gflip[x][zz]?1:-1; }
    else { int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGV(x,py,zz); TOGD(x1,zz); TOGD(x2,z2); phic[pl][zz]^=1; }
    long d=(cost+nfl)-(c0+nf0);
    int acc= d<=0;
    if(!acc){ double u=(double)((pxs()>>11)&((1UL<<53)-1))/(double)(1UL<<53); acc= u < mexp(-(double)d/T); }
    if(acc){ if(cost+nfl<best){ best=cost+nfl; memcpy(bestf,fflip,sizeof fflip); memcpy(bestg,gflip,sizeof gflip); memcpy(bestp,phic,sizeof phic); } }
    else {
      if(isg==0){ TOGD(x,zz); fflip[x][zz]^=31; nfl+= fflip[x][zz]?1:-1; }
      else if(isg==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGD(x1,zz); TOGD(x2,z2); gflip[x][zz]^=1; nfl+= gflip[x][zz]?1:-1; }
      else { int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGV(x,py,zz); TOGD(x1,zz); TOGD(x2,z2); phic[pl][zz]^=1; }
    }
  }
  memcpy(fflip,bestf,sizeof fflip); memcpy(gflip,bestg,sizeof gflip);
  long n=0; for(int x=0;x<5;x++) for(int z=0;z<64;z++) n+=(fflip[x][z]!=0)+gflip[x][z];
  pol_pred[r]=best-n; pol_nots[r]=n;
  long np=0; for(int l=0;l<25;l++) for(int z=0;z<64;z++) if(bestp[l][z]){ TGLB(phib,r-1,l,z); np++; }
  pol_phi[r]=np;
}


/* ---------- optmode 4: rolling-horizon plan (this round's output polarities chosen with a one-round lookahead) ---------- */
#ifndef SEEDX
#define SEEDX 0x1234567UL
#endif
#ifndef SC
#define SC 16
#endif
#ifndef WLOOK
#define WLOOK 3          /* lookahead weight in quarters */
#endif
#ifndef T0ROLL
#define T0ROLL 4.8
#endif
static signed char ROWCt[32][32]; static u16 ARGt[32][32]; static u8 ARGE[32][32]; static int ROWMIN[32];
static u16 dec[NR][320]; static u8 decE[NR][320]; static u8 decd[NR];
/* CHAIN: trick mask T (bit X: output X reads the finished output X+1; acyclic, T != 31). Mixed terms take the form bits of mc
 * in evaluation order. Evaluation order: chain bases (X not in T with X-1 in T) first, then X = 0..4 (an X in T after X+1). */
static void eval_row(int pat,int s,int T,int mc,int *cost,int *out,int *sel){
  int bb[5]; for(int X=0;X<5;X++) bb[X]=((pat>>X)&1)^((s>>X)&1);
  int c=0; for(int X=0;X<5;X++) c+=(s>>X)&1;
  int NSp[5]={0,0,0,0,0}; int bit=0, done=0;
  for(int X=0;X<5;X++) sel[X]=0;
  int ord[5], no=0;
  for(int X=0;X<5;X++) if(((T>>((X+4)%5))&1) && !((T>>X)&1)){ ord[no++]=X; done|=1<<X; }
  for(int X=0;X<5;X++){ int st[5],ns=0,Y=X; while(!((done>>Y)&1)){ st[ns++]=Y; if(!((T>>Y)&1)) break; Y=(Y+1)%5; }
    while(ns){ int Z=st[--ns]; if(!((done>>Z)&1)){ ord[no++]=Z; done|=1<<Z; } } }
  for(int i=0;i<5;i++){ int X=ord[i]; int a=(((T>>X)&1)? NSp[(X+1)%5] : bb[(X+1)%5])^1, b=bb[(X+2)%5], tp;
    if(a==b){ c+=1; tp=a; } else { int ch=(mc>>(bit++))&1; c+=2; tp=ch; sel[X]=ch; } NSp[X]=bb[X]^tp; }
  int o=0; for(int X=0;X<5;X++) o|=NSp[X]<<X;
  *cost=c; *out=o;
}
static void row_order(int T,int *ord){ int done=0,no=0;
  for(int X=0;X<5;X++) if(((T>>((X+4)%5))&1) && !((T>>X)&1)){ ord[no++]=X; done|=1<<X; }
  for(int X=0;X<5;X++){ int st[5],ns=0,Y=X; while(!((done>>Y)&1)){ st[ns++]=Y; if(!((T>>Y)&1)) break; Y=(Y+1)%5; }
    while(ns){ int Z=st[--ns]; if(!((done>>Z)&1)){ ord[no++]=Z; done|=1<<Z; } } } }
static void mk_tables2(void){
  for(int p=0;p<32;p++) for(int o=0;o<32;o++){ ROWCt[p][o]=99; ARGt[p][o]=0; ARGE[p][o]=0; }
  for(int pass=0;pass<(OUTNOT?2:1);pass++)
  for(int p=0;p<32;p++) for(int T=0;T<31;T++) for(int s=0;s<32;s++) for(int mc=0;mc<32;mc++){
    if(!CHAIN && T && (T&(T-1))) continue;
    int c,o,sel[5]; eval_row(p,s,T,mc,&c,&o,sel);
    if(pass==0){ if(c<ROWCt[p][o]){ ROWCt[p][o]=(signed char)c; ARGt[p][o]=(u16)(s|(T<<5)|(mc<<10)); ARGE[p][o]=0; } }
    else for(int E=1;E<32;E++){ int pc=(E&1)+((E>>1)&1)+((E>>2)&1)+((E>>3)&1)+((E>>4)&1); int c2=c+pc, o2=o^E;
      if(c2<ROWCt[p][o2]){ ROWCt[p][o2]=(signed char)c2; ARGt[p][o2]=(u16)(s|(T<<5)|(mc<<10)); ARGE[p][o2]=(u8)E; } } }
  for(int p=0;p<32;p++){ int m=99; for(int o=0;o<32;o++) if(ROWCt[p][o]<m) m=ROWCt[p][o]; ROWMIN[p]=m; }
}
static void polopt2(int r){
  static u8 pS[25][64], pC[5][64], pD[5][64];
  static u16 vrow[5][64][5]; static u8 vbit[5][64][5];
  static u8 pat0[320], pat1[320], outv[320];
  static u8 bf[5][64], bg[5][64], bo[320];
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if((v.n==NC && !designx)||(v.n!=NC && islin(v.n))) return; pS[l][z]=v.p; }   /* design X: a constant plane enters as its value */
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ int p=0; for(int y=0;y<5;y++) p^=pS[x+5*y][z]; pC[x][z]=(u8)p; }
  for(int x=0;x<5;x++) for(int z=0;z<64;z++) pD[x][z]=pC[(x+4)%5][z]^pC[(x+1)%5][(z+63)&63];
  for(int i=0;i<320;i++) pat0[i]=0;
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++){
    int Y=(2*(x-y)+10)%5, z=(zz+ROT[x][y])&63; int row=Y*64+z;
    vrow[x][zz][y]=(u16)row; vbit[x][zz][y]=(u8)(1<<y);
    if(pS[x+5*y][zz]^pD[x][zz]) pat0[row]|=(u8)(1<<y); }
  /* initial outputs: the cheapest output vector of each row */
  for(int i=0;i<320;i++){ int bo_=0,bc=99; for(int o=0;o<32;o++) if(ROWCt[pat0[i]][o]<bc){ bc=ROWCt[pat0[i]][o]; bo_=o; } outv[i]=(u8)bo_; }
  /* next-round patterns from the output polarities (iota on lane 0) */
  static u8 q[25][64], qC[5][64], qD[5][64];
  for(int Y=0;Y<5;Y++) for(int z=0;z<64;z++) for(int X=0;X<5;X++) q[X+5*Y][z]=(outv[Y*64+z]>>X)&1;
  for(int z=0;z<64;z++) q[0][z]^=(u8)((RC[r]>>z)&1);
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ int p=0; for(int y=0;y<5;y++) p^=q[x+5*y][z]; qC[x][z]=(u8)p; }
  for(int x=0;x<5;x++) for(int z=0;z<64;z++) qD[x][z]=qC[(x+4)%5][z]^qC[(x+1)%5][(z+63)&63];
  for(int i=0;i<320;i++) pat1[i]=0;
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++) if(q[x+5*y][zz]^qD[x][zz]) pat1[vrow[x][zz][y]]|=(u8)(1<<y);
  int nextlast=(r+1==NR-1);
  const int *rtL=tC[1][mixfree];
  #define F0(i) ((ROWCt[pat0[i]][outv[i]]>=90)? 1000 : (int)ROWCt[pat0[i]][outv[i]])
  #define F1(i) (nextlast? ((i)<64? rtL[pat1[i]] : 0) : ROWMIN[pat1[i]]+5)
  long A0=0,A1=0; for(int i=0;i<320;i++){ A0+=F0(i); A1+=F1(i); }
  long nfl=0; int npart=0; memset(fflip,0,sizeof fflip); memset(gflip,0,sizeof gflip);
  long cost=SC*A0+(long)WLOOK*A1, best=cost;
  memcpy(bf,fflip,sizeof bf); memcpy(bg,gflip,sizeof bg); memcpy(bo,outv,sizeof bo);
  prs=0x2545F4914F6CDD1DUL ^ (u64)r*0x9E3779B97F4A7C15UL ^ SEEDX;
  #define T0ROW(rw,b) { cost-=SC*F0(rw); pat0[rw]^=(u8)(b); cost+=SC*F0(rw); }
  #define TOGD0(x,zz) for(int k=0;k<5;k++){ int rw=vrow[x][zz][k]; T0ROW(rw,vbit[x][zz][k]); }
  #define T1ROW(rw,b) { cost-=(long)WLOOK*F1(rw); pat1[rw]^=(u8)(b); cost+=(long)WLOOK*F1(rw); }
  #define TOGD1(x,zz) for(int k=0;k<5;k++){ int rw=vrow[x][zz][k]; T1ROW(rw,vbit[x][zz][k]); }
  double T0=T0ROLL*SC/4.0;
  for(long it=0; it<OPTIT; it++){
    double T=T0*mexp(-3.1780538303479458*(double)it/(double)OPTIT);
    u64 rv=pxs(); int mv=(int)(rv%5); int x=(int)((rv>>3)%5); int zz=(int)((rv>>8)&63); int yy=(int)((rv>>16)%5);
    if(mv>=2) mv=2;     /* 3/5 of the moves flip an output polarity */
    int dm= ((rv>>24)&1)? (int)(1+((rv>>28)%31)) : (1<<x);
    long c0=cost; int mvold=0;
    #define DOMOVE() \
      if(mv==0){ int om=fflip[x][zz]; int nm= ((rv>>40)&1)? (om ^ (1<<yy)) : (int)((rv>>44)%32); mvold=om; int df=om^nm; for(int k=0;k<5;k++) if(df>>k&1){ int rw=vrow[x][zz][k]; T0ROW(rw,vbit[x][zz][k]); } fflip[x][zz]=(u8)nm; nfl+=(nm!=0)-(om!=0); cost+=SC*((nm!=0)-(om!=0)); npart+=(nm!=0&&nm!=31)-(om!=0&&om!=31); } \
      else if(mv==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGD0(x1,zz); TOGD0(x2,z2); gflip[x][zz]^=1; nfl+= gflip[x][zz]?1:-1; cost+= gflip[x][zz]?SC:-SC; } \
      else { int Y=yy; int rw=Y*64+zz; \
        cost-=SC*F0(rw); outv[rw]^=(u8)dm; cost+=SC*F0(rw); \
        for(int X=0;X<5;X++) if(dm>>X&1){ int x1=(X+1)%5, x2=(X+4)%5, z2=(zz+1)&63; int rw1=vrow[X][zz][Y]; T1ROW(rw1,vbit[X][zz][Y]); TOGD1(x1,zz); TOGD1(x2,z2); } }
    DOMOVE();
    long d=cost-c0;
    int acc= d<=0;
    if(!acc){ double u=(double)((pxs()>>11)&((1UL<<53)-1))/(double)(1UL<<53); acc= u < mexp(-(double)d/T); }
    if(npart>PCAP) acc=0;
    if(acc){ if(cost<best){ best=cost; memcpy(bf,fflip,sizeof bf); memcpy(bg,gflip,sizeof bg); memcpy(bo,outv,sizeof bo); } }
    else { /* undo: the move is an involution; re-apply it */
      if(mv==0){ int nm=mvold; int om=fflip[x][zz]; int df=om^nm; for(int k=0;k<5;k++) if(df>>k&1){ int rw=vrow[x][zz][k]; T0ROW(rw,vbit[x][zz][k]); } fflip[x][zz]=(u8)nm; nfl+=(nm!=0)-(om!=0); cost+=SC*((nm!=0)-(om!=0)); npart+=(nm!=0&&nm!=31)-(om!=0&&om!=31); }
      else if(mv==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGD0(x1,zz); TOGD0(x2,z2); gflip[x][zz]^=1; nfl+= gflip[x][zz]?1:-1; cost+= gflip[x][zz]?SC:-SC; }
      else { int Y=yy; int rw=Y*64+zz;
        cost-=SC*F0(rw); outv[rw]^=(u8)dm; cost+=SC*F0(rw);
        for(int X=0;X<5;X++) if(dm>>X&1){ int x1=(X+1)%5, x2=(X+4)%5, z2=(zz+1)&63; int rw1=vrow[X][zz][Y]; T1ROW(rw1,vbit[X][zz][Y]); TOGD1(x1,zz); TOGD1(x2,z2); } }
    }
  }
  memcpy(fflip,bf,sizeof fflip); memcpy(gflip,bg,sizeof gflip);
  /* decisions from the best state */
  for(int i=0;i<320;i++) pat0[i]=0;
  for(int x=0;x<5;x++) for(int z=0;z<64;z++) for(int y=0;y<5;y++) if(pS[x+5*y][z]^pD[x][z]) pat0[vrow[x][z][y]]|=(u8)(1<<y);
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ for(int k=0;k<5;k++) if(fflip[x][z]>>k&1) pat0[vrow[x][z][k]]^=vbit[x][z][k];
    if(gflip[x][z]){ int x1=(x+1)%5,x2=(x+4)%5,z2=(z+1)&63; for(int k=0;k<5;k++){ pat0[vrow[x1][z][k]]^=vbit[x1][z][k]; pat0[vrow[x2][z2][k]]^=vbit[x2][z2][k]; } } }
  long n=0,c0t=0; for(int x=0;x<5;x++) for(int z=0;z<64;z++) n+=(fflip[x][z]!=0)+gflip[x][z];
  for(int i=0;i<320;i++){ int o=bo[i]; if(ROWCt[pat0[i]][o]>=90) die("polopt2: infeasible row"); dec[r][i]=ARGt[pat0[i]][o]; decE[r][i]=ARGE[pat0[i]][o]; c0t+=ROWCt[pat0[i]][o]; }
  decd[r]=1; pol_pred[r]=c0t; pol_nots[r]=n; pol_phi[r]=0;
}


/* ---------- optmode 5: round-1 output polarities planned with a lookahead to round 2 (the round-1 / round-2 interface) ---------- */
static u8 rec_p[320], rec_d[320], rec_o[320]; static int recmode;
#ifndef R1ROW
#define R1ROW 0          /* design X: sweeps of the exact round-1 row search (complement subset, chained link, term forms) */
#endif
static u8 r1ov[320], r1cur[320], r1cm[320], r1nd[320], r1E[320]; static int r1ov_on; static long r1rgain;
static void polopt1(void){
  const int r=1;
  static u16 vrow[5][64][5]; static u8 vbit[5][64][5];
  static u8 pat0[320], pat1[320], outv[320], bo[320];
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++){
    int Y=(2*(x-y)+10)%5, z=(zz+ROT[x][y])&63; int row=Y*64+z; vrow[x][zz][y]=(u16)row; vbit[x][zz][y]=(u8)(1<<y); }
  for(int i=0;i<320;i++){ pat0[i]=rec_p[i]; outv[i]=rec_o[i]; }
  for(int i=0;i<320;i++) if(rec_d[i]){ int bo_=0,bc=99; for(int o=0;o<32;o++) if(ROWCt[pat0[i]][o]<bc){ bc=ROWCt[pat0[i]][o]; bo_=o; } outv[i]=(u8)bo_; }
  static u8 q[25][64], qC[5][64], qD[5][64];
  for(int Y=0;Y<5;Y++) for(int z=0;z<64;z++) for(int X=0;X<5;X++) q[X+5*Y][z]=(outv[Y*64+z]>>X)&1;
  for(int z=0;z<64;z++) q[0][z]^=(u8)((RC[r]>>z)&1);
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ int p=0; for(int y=0;y<5;y++) p^=q[x+5*y][z]; qC[x][z]=(u8)p; }
  for(int x=0;x<5;x++) for(int z=0;z<64;z++) qD[x][z]=qC[(x+4)%5][z]^qC[(x+1)%5][(z+63)&63];
  for(int i=0;i<320;i++) pat1[i]=0;
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++) if(q[x+5*y][zz]^qD[x][zz]) pat1[vrow[x][zz][y]]|=(u8)(1<<y);
  int nextlast=(r+1==NR-1);
  const int *rtL=tC[1][mixfree];
  #define G0(i) (!rec_d[i]? 0 : ((ROWCt[pat0[i]][outv[i]]>=90)? 1000 : (int)ROWCt[pat0[i]][outv[i]]))
  #define G1(i) (nextlast? ((i)<64? rtL[pat1[i]] : 0) : ROWMIN[pat1[i]]+5)
  long A0=0,A1=0; for(int i=0;i<320;i++){ A0+=G0(i); A1+=G1(i); }
  long cost=SC*A0+(long)WLOOK*A1, best=cost;
  memcpy(bo,outv,sizeof bo);
  prs=0x2545F4914F6CDD1DUL ^ (u64)r*0x9E3779B97F4A7C15UL ^ SEEDX ^ 0x51ED270B0B0B0B0BUL;
  #define U1ROW(rw,b) { cost-=(long)WLOOK*G1(rw); pat1[rw]^=(u8)(b); cost+=(long)WLOOK*G1(rw); }
  #define UOGD1(x,zz) for(int k=0;k<5;k++){ int rw=vrow[x][zz][k]; U1ROW(rw,vbit[x][zz][k]); }
  double T0=T0ROLL*SC/4.0;
  long it1=0;
  for(long it=0; it<OPTIT; it++){
    double T=T0*mexp(-3.1780538303479458*(double)it/(double)OPTIT);
    u64 rv=pxs(); int x=(int)((rv>>3)%5); int zz=(int)((rv>>8)&63); int yy=(int)((rv>>16)%5);
    int dm= ((rv>>24)&1)? (int)(1+((rv>>28)%31)) : (1<<x);
    int Y=yy; int rw=Y*64+zz; if(!rec_d[rw]) continue;
    long c0=cost;
    cost-=SC*G0(rw); outv[rw]^=(u8)dm; cost+=SC*G0(rw);
    for(int X=0;X<5;X++) if(dm>>X&1){ int x1=(X+1)%5, x2=(X+4)%5, z2=(zz+1)&63; int rw1=vrow[X][zz][Y]; U1ROW(rw1,vbit[X][zz][Y]); UOGD1(x1,zz); UOGD1(x2,z2); }
    long d=cost-c0;
    int acc= d<=0;
    if(!acc){ double u=(double)((pxs()>>11)&((1UL<<53)-1))/(double)(1UL<<53); acc= u < mexp(-(double)d/T); }
    if(acc){ if(cost<best){ best=cost; memcpy(bo,outv,sizeof bo); } }
    else {
      cost-=SC*G0(rw); outv[rw]^=(u8)dm; cost+=SC*G0(rw);
      for(int X=0;X<5;X++) if(dm>>X&1){ int x1=(X+1)%5, x2=(X+4)%5, z2=(zz+1)&63; int rw1=vrow[X][zz][Y]; U1ROW(rw1,vbit[X][zz][Y]); UOGD1(x1,zz); UOGD1(x2,z2); }
    }
    it1++;
  }
  long c0t=0;
  for(int i=0;i<320;i++) if(rec_d[i]){ int o=bo[i]; if(ROWCt[pat0[i]][o]>=90) die("polopt1: infeasible row"); dec[1][i]=ARGt[pat0[i]][o]; decE[1][i]=ARGE[pat0[i]][o]; c0t+=ROWCt[pat0[i]][o]; }
  decd[1]=1; pol_pred[1]=c0t; pol_nots[1]=0; pol_phi[1]=0;
}


/* ---------- optmode 6: global annealing of all rounds' output polarities and theta NOTs, exact objective ---------- */
#ifndef GIT
#define GIT 1000000000L
#endif
#ifndef GT0
#define GT0 1.2
#endif
#ifndef GLN
#define GLN 3.1780538303479458
#endif
static u8 g_pat[NR][320], g_o[NR][320], g_ff[NR][5][64], g_gg[NR][5][64];
static u16 g_vrow[5][64][5]; static u8 g_vbit[5][64][5];
static long g_cost; static const int *g_rtL;
static inline int gcst(int r,int i){ if(r==NR-1) return i<64? g_rtL[g_pat[r][i]] : 0; if(r==1 && !rec_d[i]) return 0; return ROWCt[g_pat[r][i]][g_o[r][i]]; }
#define GROW(r,i,bits) { g_cost-=gcst(r,i); g_pat[r][i]^=(u8)(bits); g_cost+=gcst(r,i); }
#define GTOGD(r,x,zz) for(int k=0;k<5;k++){ int rw=g_vrow[x][zz][k]; GROW(r,rw,g_vbit[x][zz][k]); }
static void g_compute_pat(int r){   /* pattern of round r (r >= 2) from o[r-1], iota, and the round-r flips */
  static u8 q[25][64], qC[5][64], qD[5][64];
  for(int Y=0;Y<5;Y++) for(int z=0;z<64;z++) for(int X=0;X<5;X++) q[X+5*Y][z]=(g_o[r-1][Y*64+z]>>X)&1;
  for(int z=0;z<64;z++) q[0][z]^=(u8)((RC[r-1]>>z)&1);
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ int p=0; for(int y=0;y<5;y++) p^=q[x+5*y][z]; qC[x][z]=(u8)p; }
  for(int x=0;x<5;x++) for(int z=0;z<64;z++) qD[x][z]=qC[(x+4)%5][z]^qC[(x+1)%5][(z+63)&63]^g_ff[r][x][z]^g_gg[r][(x+4)%5][z]^g_gg[r][(x+1)%5][(z+63)&63];
  for(int i=0;i<320;i++) g_pat[r][i]=0;
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++) if(q[x+5*y][zz]^qD[x][zz]) g_pat[r][g_vrow[x][zz][y]]|=(u8)(1<<y);
}
static long g_total(void){ long c=0; for(int r=1;r<NR;r++){ for(int i=0;i<320;i++) c+=gcst(r,i); if(r>=2) for(int x=0;x<5;x++) for(int z=0;z<64;z++) c+=g_ff[r][x][z]+g_gg[r][x][z]; } return c; }
static void g_outflip(int r,int Y,int zz,int dm){
  int i=Y*64+zz; g_cost-=gcst(r,i); g_o[r][i]^=(u8)dm; g_cost+=gcst(r,i);
  if(r+1<NR) for(int X=0;X<5;X++) if(dm>>X&1){ int x1=(X+1)%5, x2=(X+4)%5, z2=(zz+1)&63;
    GROW(r+1,g_vrow[X][zz][Y],g_vbit[X][zz][Y]); GTOGD(r+1,x1,zz); GTOGD(r+1,x2,z2); }
}
static void pack_fg(int r);
static void unpack_fg(int r);
static void polopt_global(int frompl){
  static u8 bo[NR][320], bff[NR][5][64], bgg[NR][5][64];
  const int RL=NR-1; g_rtL=tC[1][mixfree];
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++){
    int Y=(2*(x-y)+10)%5, z=(zz+ROT[x][y])&63; g_vrow[x][zz][y]=(u16)(Y*64+z); g_vbit[x][zz][y]=(u8)(1<<y); }
  memset(g_ff,0,sizeof g_ff); memset(g_gg,0,sizeof g_gg);
  if(frompl){
    for(int i=0;i<320;i++) g_pat[1][i]=rec_p[i];
    for(int r=1;r<=RL;r++){
      if(r>=2){ unpack_fg(r); for(int x=0;x<5;x++) for(int z=0;z<64;z++){ g_ff[r][x][z]=fflip[x][z]; g_gg[r][x][z]=gflip[x][z]; } g_compute_pat(r); }
      if(r<RL) for(int i=0;i<320;i++){
        if(r==1 && !rec_d[i]){ g_o[r][i]=rec_o[i]; continue; }
        int dd=dec[r][i], c_, o_, sel_[5]; eval_row(g_pat[r][i],dd&31,(dd>>5)&31,dd>>10,&c_,&o_,sel_); g_o[r][i]=(u8)o_; }
    }
  } else {
  for(int i=0;i<320;i++){ g_pat[1][i]=rec_p[i]; g_o[1][i]=rec_o[i]; }
  for(int i=0;i<320;i++) if(rec_d[i]){ int b=0,bc=99; for(int o=0;o<32;o++) if(ROWCt[g_pat[1][i]][o]<bc){ bc=ROWCt[g_pat[1][i]][o]; b=o; } g_o[1][i]=(u8)b; }
  for(int r=2;r<=RL;r++){ g_compute_pat(r);
    if(r<RL) for(int i=0;i<320;i++){ int b=0,bc=99; for(int o=0;o<32;o++) if(ROWCt[g_pat[r][i]][o]<bc){ bc=ROWCt[g_pat[r][i]][o]; b=o; } g_o[r][i]=(u8)b; } }
  /* the initial outputs of round r change round r+1 patterns: recompute in order */
  for(int r=2;r<=RL;r++){ g_compute_pat(r); if(r<RL) for(int i=0;i<320;i++){ int b=0,bc=99; for(int o=0;o<32;o++) if(ROWCt[g_pat[r][i]][o]<bc){ bc=ROWCt[g_pat[r][i]][o]; b=o; } g_o[r][i]=(u8)b; } }
  for(int r=2;r<=RL;r++) g_compute_pat(r);
  }
  g_cost=g_total(); long best=g_cost;
  memcpy(bo,g_o,sizeof bo); memcpy(bff,g_ff,sizeof bff); memcpy(bgg,g_gg,sizeof bgg);
  prs=0x2545F4914F6CDD1DUL ^ SEEDX ^ 0x7777777777777777UL;
  const double LN=GLN;
  for(long it=0; it<GIT; it++){
    double T=GT0*mexp(-LN*(double)it/(double)GIT);
    u64 rv=pxs(); int r=1+(int)(rv%(u64)RL); int type=(int)((rv>>8)%5); int x=(int)((rv>>12)%5); int zz=(int)((rv>>16)&63); int yy=(int)((rv>>24)%5);
    int dm= ((rv>>32)&1)? (int)(1+((rv>>36)%31)) : (1<<x);
    if(r==RL){ type=type&1; } else if(r==1){ type=2; } else if(type>2) type=2;
    if(type==2 && r==1 && !rec_d[yy*64+zz]) continue;
    long c0=g_cost;
    #define DO() \
      if(type==0){ GTOGD(r,x,zz); g_ff[r][x][zz]^=1; g_cost+= g_ff[r][x][zz]?1:-1; } \
      else if(type==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; GTOGD(r,x1,zz); GTOGD(r,x2,z2); g_gg[r][x][zz]^=1; g_cost+= g_gg[r][x][zz]?1:-1; } \
      else { g_outflip(r,yy,zz,dm); }
    DO();
    long d=g_cost-c0; int acc= d<=0;
    if(!acc){ double u=(double)((pxs()>>11)&((1UL<<53)-1))/(double)(1UL<<53); acc= u < mexp(-(double)d/T); }
    if(acc){ if(g_cost<best){ best=g_cost; memcpy(bo,g_o,sizeof bo); memcpy(bff,g_ff,sizeof bff); memcpy(bgg,g_gg,sizeof bgg); } }
    else { DO(); }
  }
  memcpy(g_o,bo,sizeof bo); memcpy(g_ff,bff,sizeof bff); memcpy(g_gg,bgg,sizeof bgg);
  for(int r=2;r<=RL;r++) g_compute_pat(r);
  long chk=g_total(); if(chk!=best) die("polopt_global: cost mismatch");
  for(int r=1;r<RL;r++){ long c=0;
    for(int i=0;i<320;i++){ if(r==1 && !rec_d[i]) continue; if(ROWCt[g_pat[r][i]][g_o[r][i]]>=90) die("polopt_global: infeasible"); dec[r][i]=ARGt[g_pat[r][i]][g_o[r][i]]; decE[r][i]=ARGE[g_pat[r][i]][g_o[r][i]]; c+=ROWCt[g_pat[r][i]][g_o[r][i]]; }
    decd[r]=1; pol_pred[r]=c; pol_nots[r]=0; pol_phi[r]=0;
    if(r>=2 && r<RL){ for(int x=0;x<5;x++) for(int z=0;z<64;z++){ fflip[x][z]=g_ff[r][x][z]; gflip[x][z]=g_gg[r][x][z]; pol_nots[r]+=g_ff[r][x][z]+g_gg[r][x][z]; } pack_fg(r); decided[r]=1; } }
  decided[RL]=0;
}

static u64 KL[25];          /* lane constants of the absorbed state (var lanes: offset) */
static u64 PD[4];
static long nnot_rows, ntrick, nforced;


/* ---------- per-round finish: dead-code removal, counts, register allocation, emission, pinning ---------- */
static long cnt[5]; static long rcum[64];
#define NREG 2304
static u16 freestk[NREG]; static int nfree; static u8 regbusy[NREG];
static long live, maxlive, maxreg, ninstr;
static int g_r; static u8 nhi[W]; static long outdef[256]; static int fdp=-1; static u8 eb[4000]; static int el; static u64 eacc; static int enb;   /* bit packer: enb (< 8) pending bits in eacc */
static int emitting;
static void alloc_init(void){
  memset(regbusy,0,sizeof regbusy);
  nfree=0; for(int r=NREG-1;r>=256;r--) freestk[nfree++]=(u16)r;
  live=0; maxlive=0; maxreg=0; ninstr=0; el=0; eacc=0; enb=0;
}
static void freereg(int r){ if(!regbusy[r]) die("free of a free register"); regbusy[r]=0; live--; }
static u16 pinq[W]; static long npinsh, npinsh_r1;
static void pin_state(void){
  for(int q=0;q<1600;q++){ preg[q]=0xFFFF; plast[q]=NOUSE; pfl[q]=0; }
  npin=0; npinsh=0; if(g_r==1) npinsh_r1=0;
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC) continue;
    if(v.n>=PIN) die("state plane from an earlier round");
    if((nf[v.n]&F_LIN) && !designx) die("linear state plane");
    if(v.n<256 && !designx) die("input plane as state plane");
    if(nlast[v.n]==0xFFFE){ if(!designx) die("two state planes share a node"); S[l][z].n=(u16)(PIN+pinq[v.n]); npinsh++; if(g_r==1) npinsh_r1=npinsh; continue; }  /* design X: one pin, two planes */
    int q=l*64+z; pord[q]=v.n; pfl[q]=(u8)(nf[v.n]&F_OPM); preg[q]= emitting? nreg[v.n] : 0; npin++;
    nlast[v.n]=0xFFFE; pinq[v.n]=(u16)q; S[l][z].n=(u16)(PIN+q); }
}
/* ---------- straight-line cuts of rounds 0..1 (applied once, after the liveness of round 1; node order kept) ----------
 * (a) NOT(NOT x) = x and a second NOT of one value are one node;
 * (b) p XOR (p AND q) = p AND NOT q and p XOR (p OR q) = NOT p AND q, when the AND (OR) has no other use: the XOR node becomes
 *     an AND node on p and a NOT node N of the other operand; N is the operand of that operand when it is a NOT, an
 *     existing live NOT node defined before the XOR, or else the AND (OR) node itself rewritten as a NOT.  Dead nodes are dropped. */
#define CUTS 1
static void cut_pass(int lo){
  static u16 rp[W], nt[W], uc[W];
  for(int i=0;i<nn;i++){ rp[i]=(u16)i; nt[i]=0; uc[i]=0; }
  for(int i=lo;i<nn;i++) if(nf[i]&F_LIVE){ int op=nf[i]&F_OPM; uc[na[i]]++; if(op!=O_NOT) uc[nb[i]]++; }
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n!=NC) uc[v.n]+=100; }
  for(int i=lo;i<nn;i++){
    if(!(nf[i]&F_LIVE)) continue;
    int op=nf[i]&F_OPM; na[i]=rp[na[i]]; if(op!=O_NOT) nb[i]=rp[nb[i]];
    if(op==O_NOT){
      int x=na[i];
      if(x>=lo && (nf[x]&F_OPM)==O_NOT && (nf[x]&F_LIVE)){ rp[i]=na[x]; nf[i]&=(u8)~F_LIVE; continue; }
      if(nt[x] && (nf[nt[x]-1]&F_LIVE)){ rp[i]=(u16)(nt[x]-1); nf[i]&=(u8)~F_LIVE; continue; }
      nt[x]=(u16)(i+1); continue;
    }
    if(op!=O_XOR) continue;
    for(int k=0;k<2;k++){
      int p= k? nb[i]:na[i], j= k? na[i]:nb[i];
      if(j<lo || !(nf[j]&F_LIVE)) continue;
      int jop=nf[j]&F_OPM; if(jop!=O_AND && jop!=O_OR) continue;
      if(na[j]!=p && nb[j]!=p) continue;
      if(uc[j]!=1) continue;
      int q= na[j]==p? nb[j]:na[j];
      int rr= jop==O_AND? q:p, oo= jop==O_AND? p:q;     /* rr: the operand to complement, oo: the other */
      int nq;
      if(rr>=lo && (nf[rr]&F_OPM)==O_NOT){ nq=na[rr]; nf[j]&=(u8)~F_LIVE; }
      else if(nt[rr] && nt[rr]-1<i && (nf[nt[rr]-1]&F_LIVE)){ nq=nt[rr]-1; nf[j]&=(u8)~F_LIVE; }
      else { nf[j]=(u8)((nf[j]&~F_OPM)|O_NOT); na[j]=(u16)rr; nb[j]=0; nt[rr]=(u16)(j+1); nq=j; }
      nf[i]=(u8)((nf[i]&~F_OPM)|O_AND);
      if(jop==O_AND){ na[i]=(u16)oo; nb[i]=(u16)nq; } else { na[i]=(u16)nq; nb[i]=(u16)oo; }
      break;
    }
  }
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n!=NC) S[l][z].n=rp[v.n]; }
}
static void mark_live(int last,int lo){
  for(int i=0;i<nn;i++) nf[i]&=(u8)~(F_LIVE|F_ST|F_OUT);
  for(int i=0;i<nn;i++) nf[i]&=(u8)~(F_LIVE|F_ST|F_OUT);
  if(!last){
    for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC) continue; if(v.n>=PIN) die("state plane from an earlier round"); nf[v.n]|=F_LIVE|F_ST; }
    memset(nhi,0,sizeof nhi); if(g_r==NR-2) for(int l=0;l<25;l+=6) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n!=NC) nhi[v.n]=1; }   /* lanes 0,6,12,18,24 feed the digest row */
  } else {
    for(int j=0;j<256;j++){ V v=S[j>>6][j&63]; if(v.n==NC||v.n>=PIN||v.n<lo) die("digest plane constant, input or old");
      if(nf[v.n]&F_OUT) die("shared digest node"); nf[v.n]|=F_LIVE|F_OUT; nreg[v.n]=(u16)j; PD[j>>6]|=(u64)v.p<<(j&63); }
  }
  for(int i=nn-1;i>=lo;i--) if(nf[i]&F_LIVE){ int op=nf[i]&F_OPM; int a=na[i], b=nb[i];
    if(a<PIN) nf[a]|=F_LIVE; if(op!=O_NOT && b<PIN) nf[b]|=F_LIVE; }
}
static void finish_round(int last,int prefix){
  int lo= prefix? 256 : 0;
  mark_live(last,lo);
#if CUTS
  if(prefix && !last){ cut_pass(lo); mark_live(last,lo); }
#endif
  for(int i=lo;i<nn;i++) if(nf[i]&F_LIVE) cnt[nf[i]&F_OPM]++;
  rcum[g_r]=cnt[1]+cnt[2]+cnt[3]+cnt[4];
  if(emitting){
    for(int i=lo;i<nn;i++) if(nf[i]&F_LIVE){ int op=nf[i]&F_OPM; int a=na[i], b=nb[i];
      if(a>=PIN) plast[a-PIN]=(u16)i; else nlast[a]=(u16)i;
      if(op!=O_NOT){ if(b>=PIN) plast[b-PIN]=(u16)i; else nlast[b]=(u16)i; } }
    if(prefix){ for(int j=0;j<256;j++){ nreg[j]=(u16)j; if(nlast[j]!=NOUSE || (nf[j]&F_ST)){ regbusy[j]=1; live++; } } if(live>maxlive) maxlive=live; }
    else { for(int q=0;q<1600;q++) if(preg[q]!=0xFFFF && plast[q]==NOUSE) die("state plane without use"); }
    if(last){ for(int r=0;r<256;r++) outdef[r]=-1; for(int i=lo;i<nn;i++) if((nf[i]&F_LIVE) && (nf[i]&F_OUT)) outdef[nreg[i]]=i; }
    for(int i=lo;i<nn;i++){
      if(!(nf[i]&F_LIVE)) continue;
      int op=nf[i]&F_OPM; int a=na[i], b=(op==O_NOT)?a:nb[i];
      int ra= a>=PIN? preg[a-PIN] : nreg[a];
      int rb= op==O_NOT? 0 : (b>=PIN? preg[b-PIN] : nreg[b]);
      int ops[2]={a,b}; int dy[2]; int ndy=0;   /* dy: registers of the operands that die here */
      for(int k=0;k<2;k++){ int o=ops[k]; if(k==1&&o==a) break;
        if(o>=PIN){ if(plast[o-PIN]==i){ dy[ndy++]=preg[o-PIN]; freereg(preg[o-PIN]); preg[o-PIN]=0xFFFF; npin--; } }
        else if(!(nf[o]&(F_ST|F_OUT)) && nlast[o]==i){ dy[ndy++]=nreg[o]; freereg(nreg[o]); } }
      int dst;
      if(nf[i]&F_OUT){ dst=nreg[i]; if(regbusy[dst]) die("output register busy"); }
      else { /* lowest free register; 0..255 only for values that die before the last round (B35 allocation) */
        int lowany= !last && !nhi[i]; dst=-1;
        for(int k=0;k<ndy;k++){ int r=dy[k]; if((r>=256 || lowany || (last && outdef[r]>=nlast[i])) && (dst<0 || r<dst)) dst=r; }   /* dying operand first: dst = a */
        if(dst<0) for(int r=0;r<NREG;r++) if(!regbusy[r] && (r>=256 || lowany || (last && outdef[r]>=nlast[i]))){ dst=r; break; }
        if(dst<0){ die("out of registers"); dst=0; } }
      if(!(nf[i]&(F_ST|F_OUT)) && nlast[i]==NOUSE) die("live node without use");
      regbusy[dst]=1; live++; nreg[i]=(u16)dst; if(live>maxlive) maxlive=live; if(dst+1>maxreg) maxreg=dst+1;
      int code= op==O_XOR?0: op==O_AND?1: op==O_OR?2: 3;
      if(dst>=2048||ra>=2048||rb>=2048) die("register above 2047 (11-bit field)");
      u64 w; int nbits;   /* two-address encoding: 2-bit op, 1-bit t (t=1: dst = a), then the register fields */
      if(code==3){ if(dst==ra){ w=3|4|(u64)ra<<3; nbits=14; } else { w=3|(u64)dst<<3|(u64)ra<<14; nbits=25; } }
      else { if(dst==rb && dst!=ra){ int t_=ra; ra=rb; rb=t_; }   /* XOR, AND, OR commute */
        if(dst==ra){ w=(u64)code|4|(u64)ra<<3|(u64)rb<<14; nbits=25; } else { w=(u64)code|(u64)dst<<3|(u64)ra<<14|(u64)rb<<25; nbits=36; } }
      eacc|=w<<enb; enb+=nbits; while(enb>=8){ eb[el++]=(u8)eacc; eacc>>=8; enb-=8; }
      if(el>=3995){ sc3(1,fdp,(i64)eb,el); el=0; }
      ninstr++;
    }
    if(!prefix && npin!=0) die("state plane not freed");
  }
  if(!last) pin_state();
}

static int stop_prefix; static long prefix_ops;
static void unpack_fg(int r){ for(int i=0;i<320;i++){ fflip[i/64][i%64]=FMb[r][i]; gflip[i/64][i%64]=GB(GGb[r],i); } }
static void pack_fg(int r){ memset(GGb[r],0,40);
  for(int i=0;i<320;i++){ FMb[r][i]=fflip[i/64][i%64]; GGb[r][i>>3]|=(u8)(gflip[i/64][i%64]<<(i&7)); } }

static void build(void){
  nn=0; nform=0; cnt_emit=0; nnot_rows=0; ntrick=0; nforced=0; npin=0;
  for(int k=0;k<5;k++) cnt[k]=0;
  memset(fh,0,sizeof fh); memset(ch,0,sizeof ch);
  for(int q=0;q<1600;q++){ preg[q]=0xFFFF; plast[q]=NOUSE; pfl[q]=0; }
  PD[0]=PD[1]=PD[2]=PD[3]=0;
  if(emitting) alloc_init();
  for(int j=0;j<256;j++){ int n=newnode(O_IN,0,0); u64 m[4]={0,0,0,0}; m[j>>6]=1UL<<(j&63); nf[n]|=F_LIN; linid[n]=(u16)fadd(m,n); }
  for(int l=0;l<25;l++) for(int z=0;z<64;z++) S[l][z]=K_((KL[l]>>z)&1);
  if(designx){   /* design X: lanes x and 10+x carry v_x (xor K); v_0..v_3 = u_0..u_3, v_4 = XOR_(x<4) rotr(u_x,(39-ROT[x][2]) mod 64) */
    for(int x=0;x<4;x++) for(int z=0;z<64;z++){ S[x][z]=MK(64*x+z,(KL[x]>>z)&1); S[10+x][z]=MK(64*x+z,(KL[10+x]>>z)&1); }
    for(int z=0;z<64;z++){ V v=K_(0); for(int x=0;x<4;x++){ int s=(39-ROT[x][2]+64)&63; v=xorv(v,MK(64*x+((z+s)&63),0)); }
      S[4][z]=xorv(v,K_((KL[4]>>z)&1)); S[14][z]=xorv(v,K_((KL[14]>>z)&1)); }
  } else
  for(int z=0;z<64;z++){
    S[1][z]=MK(z,(KL[1]>>z)&1); S[6][z]=MK(64+z,(KL[6]>>z)&1);
    S[4][z]=MK(128+z,(KL[4]>>z)&1); S[9][z]=MK(192+z,(KL[9]>>z)&1);
  }
  if(!designx) for(int z=0;z<64;z++){
    S[11][z]=xorv(xorv(MK(z,0),MK(64+z,0)),K_((KL[11]>>z)&1));
    S[14][z]=xorv(xorv(MK(128+z,0),MK(192+z,0)),K_((KL[14]>>z)&1));
  }
  for(int r=0;r<NR;r++){
    int last=(r==NR-1);
    memset(fflip,0,sizeof fflip); memset(gflip,0,sizeof gflip);
    if(r==1 && optmode>=3){ for(int x=0;x<5;x++) for(int z=0;z<64;z++) fflip[x][z]=F1[x][z]; memcpy(gflip,G1,sizeof gflip); }
    if(optmode && r>=2){
      if(decided[r]) unpack_fg(r);
      else if(r==curpass){ if(optmode>=4 && !last) polopt2(r); else polopt(r,last); pack_fg(r); decided[r]=1; return; }
    }
    if(r>=2){ nn=0; memset(ch,0,sizeof ch); }      /* the ring holds one round (rounds 0 and 1 together) */
    /* theta: C[.][63] first, then per z: C[.][z], D[.][z] (keeps few C live) */
    for(int x=0;x<5;x++){ V s=S[x][63]; for(int y=1;y<5;y++) s=xorv(s,S[x+5*y][63]); Cc[x][63]= gflip[x][63]? notv(s) : s; }
    for(int z=0;z<64;z++){
      if(z<63) for(int x=0;x<5;x++){ V s=S[x][z]; for(int y=1;y<5;y++) s=xorv(s,S[x+5*y][z]); Cc[x][z]= gflip[x][z]? notv(s) : s; }
      for(int x=0;x<5;x++){ Dd[x][z]=xorv(Cc[(x+4)%5][z],Cc[(x+1)%5][(z+63)&63]); Dd2[x][z]=Dd[x][z]; if(fflip[x][z]) Dd2[x][z]=notv(Dd[x][z]); }
    }
    int nY=last?1:5, needmask=last?0x0F:0x1F;
    for(int Y=0;Y<nY;Y++) for(int z=0;z<64;z++){
      V b[5];
      for(int X=0;X<5;X++){ int y=X, x=(3*Y+X)%5; int zz=(z-ROT[x][y]+64)&63; b[X]=xorv(S[x+5*y][zz], ((fflip[x][zz]>>y)&1)? Dd2[x][zz] : Dd[x][zz]); }
      int distinct=1; for(int X=0;X<5;X++){ if(b[X].n==NC) distinct=0; for(int X2=X+1;X2<5;X2++) if(b[X].n==b[X2].n) distinct=0; }
      int best,bj;
      int havesel=0, rsel[5]={0,0,0,0,0}, Tm=0, rowE=0;
      if(recmode && r==1){ int pp=0; for(int X=0;X<5;X++) pp|=b[X].p<<X; rec_p[Y*64+z]=(u8)pp; rec_d[Y*64+z]=(u8)distinct; }
      if(distinct && optmode>=4 && (r>=2 || (r==1 && optmode>=5)) && !last && decd[r]){ int p=0; for(int X=0;X<5;X++) p|=b[X].p<<X;
        u16 dd=dec[r][Y*64+z]; rowE=decE[r][Y*64+z]; best=dd&31; Tm=(dd>>5)&31; bj=-1; int cc,oo; eval_row(p,best,Tm,dd>>10,&cc,&oo,rsel); havesel=1; }
      else if(distinct){ int p=0; for(int X=0;X<5;X++) p|=b[X].p<<X; best=tS[last][mixfree][p]; bj=tJ[last][mixfree][p]; }
      else { best=row_choose(b,needmask,&bj,0);
        if(r==1){ int i_=Y*64+z, cm_=0; for(int X=0;X<5;X++) if(b[X].n==NC) cm_|=1<<X; r1cm[i_]=(u8)cm_; r1nd[i_]=1;
          if(r1ov_on && r1ov[i_]!=0xFF){ best=r1ov[i_]&31; bj=(int)(r1ov[i_]>>5)-1; }
          r1cur[i_]=(u8)(best|((bj+1)<<5)); } }
      for(int X=0;X<5;X++) if(best>>X&1){ b[X]=notv(b[X]); nnot_rows++; }
      if(havesel){
        if(Tm) ntrick++;
        int ord[5]; row_order(Tm,ord);
        for(int i=0;i<5;i++){ int X=ord[i]; if(!(needmask>>X&1)) continue; int pl=X+5*Y;
          curmix_sel=rsel[X]; curmix_flag=0;
          V t= ((Tm>>X)&1)? andnot(NS[(X+1)%5+5*Y][z],b[(X+2)%5]) : andnot(b[(X+1)%5],b[(X+2)%5]);
          SETB(mixb,r,pl,z,(mixfree? curmix_flag : 0)); curmix_sel=0;
          NS[pl][z]=xorv(b[X],t); }
        for(int X=0;X<5;X++) if((rowE>>X)&1){ int pl=X+5*Y; NS[pl][z]=notv(NS[pl][z]); }
        continue;
      }
      int k=(bj+1)%5;
      if(bj>=0){
        ntrick++;
        int pl=k+5*Y; V p1=b[(k+1)%5], p2=b[(k+2)%5];
        int mixed=((p1.p^1)!=p2.p), forced=-1;
        if(mixed && mixfree){ forced=(b[(bj+2)%5].p^1)^b[k].p; nforced++; }
        curmix_sel= havesel? rsel[k] : (forced>=0? forced : (mixfree? GETB(phib,r,pl,z) : 0)); curmix_flag=0;
        V t=andnot(b[(k+1)%5],b[(k+2)%5]);
        SETB(mixb,r,pl,z,((mixfree && forced<0)? curmix_flag : 0)); curmix_sel=0;
        NS[pl][z]=xorv(b[k],t);
      }
      for(int X=0;X<5;X++) if(needmask>>X&1){
        if(bj>=0 && X==k) continue;
        int pl=X+5*Y;
        curmix_sel= havesel? rsel[X] : (mixfree? GETB(phib,r,pl,z) : 0); curmix_flag=0;
        V t= (X==bj)? andnot(NS[k+5*Y][z],b[(X+2)%5]) : andnot(b[(X+1)%5],b[(X+2)%5]);
        SETB(mixb,r,pl,z,(mixfree? curmix_flag : 0)); curmix_sel=0;
        NS[pl][z]=xorv(b[X],t);
      }
      if(r==1 && r1ov_on && r1E[Y*64+z]) for(int X=0;X<5;X++) if((r1E[Y*64+z]>>X)&1){ int pl=X+5*Y; NS[pl][z]=notv(NS[pl][z]); }   /* design X: round-1 output complements */
    }
    if(recmode && r==1){ for(int Y=0;Y<5;Y++) for(int z=0;z<64;z++){ int o=0; for(int X=0;X<5;X++) o|=(NS[X+5*Y][z].p&1)<<X; rec_o[Y*64+z]=(u8)o; } return; }
    for(int z=0;z<64;z++) NS[0][z].p^=(RC[r]>>z)&1;   /* iota */
    for(int l=0;l<25;l++) for(int z=0;z<64;z++) S[l][z]=NS[l][z];
    if(r==0) continue;
    g_r=r; finish_round(last, r==1);
    if(r==1 && stop_prefix){ prefix_ops=cnt[1]+cnt[2]+cnt[3]+cnt[4]; return; }
  }
}

#include "kbasis.h"
static u64 rs;
static u64 xs(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static int use_r; static u64 force_r;
static void set_consts(int trial){
  for(int l=0;l<25;l++) KL[l]=0;
  KL[16]=0x8000000000000006UL;
  if(designx){   /* K_0..K_4 by xorshift from the trial; K_(10+x) = K_x ^ 0x55..55 (^ the padding lane for x = 1); lanes 5..9 all-ones; 15 zero */
    rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs();
    for(int x=0;x<5;x++){ KL[x]=xs(); KL[10+x]=KL[x]^0x5555555555555555UL; KL[5+x]=~0UL; }
    KL[11]^=KL[16]; KL[15]=0; return; }
  if(use_r){ static const int fl2[12]={0,2,3,5,7,8,10,12,13,15,11,14}; u64 r=force_r; for(int i=0;i<12;i++){ u64 k=KB0[i]; for(int j=0;j<64;j++) if((r>>j)&1) k^=KBV[j][i]; KL[fl2[i]]=k; } return; }
  if(trial>=1000){ static const int fl2[12]={0,2,3,5,7,8,10,12,13,15,11,14}; /* S3-04: a structured set, r from the trial seed */
    rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs(); u64 r=xs();
    for(int i=0;i<12;i++){ u64 k=KB0[i]; for(int j=0;j<64;j++) if((r>>j)&1) k^=KBV[j][i]; KL[fl2[i]]=k; } return; }
  if(trial>0){ rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs();
    static const int fl[12]={0,2,3,5,7,8,10,12,13,15,11,14};
    for(int i=0;i<12;i++) KL[fl[i]]=xs(); }
}

static long r1gain;
#ifndef R1OUTE
#define R1OUTE 0         /* with R1LOOK: also search the round-1 output complements (one NOT each) */
#endif
#ifndef R1LOOK
#define R1LOOK 0         /* weight of the round-2 lookahead (row minima of the round-2 input patterns); rounds 0..1 weigh SC */
#endif
static long r1look(void){
  static u8 pS[25][64], pC[5][64], pD[5][64], pat[320];
  for(int l=0;l<25;l++) for(int z=0;z<64;z++) pS[l][z]=S[l][z].p;
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ int q=0; for(int y=0;y<5;y++) q^=pS[x+5*y][z]; pC[x][z]=(u8)q; }
  for(int x=0;x<5;x++) for(int z=0;z<64;z++) pD[x][z]=pC[(x+4)%5][z]^pC[(x+1)%5][(z+63)&63];
  memset(pat,0,sizeof pat);
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++){ int Y=(2*(x-y)+10)%5, z=(zz+ROT[x][y])&63; if(pS[x+5*y][zz]^pD[x][zz]) pat[Y*64+z]|=(u8)(1<<y); }
  long c=0; for(int i=0;i<320;i++) c+=ROWMIN[pat[i]]; return c;
}
#define R1OBJ() (r1rbuilds++, (long)SC*prefix_ops + (R1LOOK? (long)R1LOOK*r1look() : 0))
static long r1rlook0, r1rlook1, r1rp0, r1rp1, r1rbuilds, r1rbuilds_plan;
static void r1rowopt(void){   /* exact: every candidate decision of a row is built and the rounds-0..1 count (+ lookahead) compared */
  memset(r1nd,0,sizeof r1nd); memset(r1ov,0xFF,sizeof r1ov); memset(r1E,0,sizeof r1E); r1ov_on=1; curpass=99; stop_prefix=1; build(); long best=R1OBJ(), b0=prefix_ops; r1rlook0=r1look();
  for(int i=0;i<320;i++) if(r1nd[i]) r1ov[i]=r1cur[i];
  for(int sw=0;sw<R1ROW;sw++){ int imp=0;
    for(int i=0;i<320;i++){ if(!r1nd[i]) continue; int Y=i/64, z=i%64;
      u8 old=r1ov[i], bm=old; long bc=best;
      for(int j=-1;j<5;j++) for(int sm=0;sm<32;sm++){ if(sm&r1cm[i]) continue; u8 v=(u8)(sm|((j+1)<<5)); if(v==old) continue;
        r1ov[i]=v; build(); long o_=R1OBJ(); if(o_<bc){ bc=o_; bm=v; } }
      r1ov[i]=bm; if(bc<best){ best=bc; imp=1; }
      for(int X=0;X<5;X++){ TGLB(phib,1,X+5*Y,z); build(); long o_=R1OBJ(); if(o_<best){ best=o_; imp=1; } else TGLB(phib,1,X+5*Y,z); }
      if(R1LOOK && R1OUTE){ u8 e0=r1E[i], eb=e0; for(int e=0;e<32;e++){ if(e==e0) continue; r1E[i]=(u8)e; build(); long o_=R1OBJ(); if(o_<best){ best=o_; eb=(u8)e; imp=1; } } r1E[i]=eb; }
    }
    if(!imp) break; }
  build(); r1rp0=b0; r1rp1=prefix_ops; r1rlook1=r1look(); stop_prefix=0; r1rbuilds_plan=r1rbuilds+1; r1rbuilds=0;
}
static void r1greedy(void){
  /* round 1: physical complements on C and D (linear forms), kept when the live ops of rounds 0..1 drop */
  memset(F1,0,sizeof F1); memset(G1,0,sizeof G1);
  memset(phib,0,sizeof phib); memset(mixb,0,sizeof mixb); memset(decided,0,sizeof decided); curpass=99;
  stop_prefix=1; build(); long best=prefix_ops, b0=best;
  for(int sw=0;sw<R1SWEEPS;sw++){ int imp=0;
    for(int v=0;v<640;v++){
      if(v<320 && F1MASK){ u8 *p=&F1[v/64][v%64]; u8 old=*p, bm=old; long bc2=best;
        for(int m=0;m<32;m++){ if(m==old) continue; *p=(u8)m; build(); long c=prefix_ops; if(c<bc2){ bc2=c; bm=(u8)m; } }
        *p=bm; if(bm!=old){ best=bc2; imp=1; } continue; }
      u8 *p= v<320? &F1[v/64][v%64] : &G1[(v-320)/64][v%64];
      if(v<320) *p^=31; else *p^=1; build(); long c=prefix_ops;
      if(c<best){ best=c; imp=1; } else { if(v<320) *p^=31; else *p^=1; } }
    if(!imp) break; }
#ifdef R1SA
  { u64 sv=prs; prs=0x9E3779B97F4A7C15UL ^ (u64)R1SA; static u8 bf1[5][64], bg1[5][64]; memcpy(bf1,F1,sizeof F1); memcpy(bg1,G1,sizeof G1); long cur=best;
    for(long it=0; it<R1SAIT; it++){
      double T= 1.5*(1.0-(double)it/(double)R1SAIT);
      int k1=(int)(pxs()%640), k2= (pxs()&1)? (int)(pxs()%640) : -1;
      u8 *p1= k1<320? &F1[k1/64][k1%64] : &G1[(k1-320)/64][k1%64]; *p1^=1;
      u8 *p2=0; if(k2>=0 && k2!=k1){ p2= k2<320? &F1[k2/64][k2%64] : &G1[(k2-320)/64][k2%64]; *p2^=1; }
      build(); long c=prefix_ops; long d=c-cur;
      int acc= d<=0; if(!acc && T>0.01){ double u=(double)((pxs()>>11)&((1UL<<53)-1))/(double)(1UL<<53); acc= u<mexp(-(double)d/T); }
      if(acc){ cur=c; if(c<best){ best=c; memcpy(bf1,F1,sizeof F1); memcpy(bg1,G1,sizeof G1); } }
      else { *p1^=1; if(p2) *p2^=1; }
    }
    memcpy(F1,bf1,sizeof F1); memcpy(G1,bg1,sizeof G1); prs=sv; }
#endif
  stop_prefix=0; r1gain=b0-best;
}
static void fullplan(void){
  memset(decd,0,sizeof decd); memset(dec,0,sizeof dec); memset(decE,0,sizeof decE);
  r1ov_on=0;   /* every plan starts without round-1 row decisions (the plan of a trial does not depend on the trials built before it) */
  if(optmode>=3) r1greedy();
  memset(phib,0,sizeof phib); memset(mixb,0,sizeof mixb); memset(decided,0,sizeof decided); memset(decd,0,sizeof decd);
  memset(pol_phi,0,sizeof pol_phi); memset(pol_pred,0,sizeof pol_pred); memset(pol_nots,0,sizeof pol_nots);
  r1ov_on=0; if(designx && R1ROW) r1rowopt();
  if(optmode==5){ recmode=1; curpass=99; build(); recmode=0; polopt1(); }
  if(optmode==6){ recmode=1; curpass=99; build(); recmode=0; polopt_global(0); }
  if(optmode>=7){ recmode=1; curpass=99; build(); recmode=0; polopt1(); }
  if(optmode){ for(int k=2;k<NR;k++){ curpass=k; build(); } }
  if(optmode>=7){ polopt_global(1); curpass=NR-1; build(); }
  curpass=99;
}
static int work(int argc,char **argv);
/* The work runs in a forked child: its own signal struct starts with ru_maxrss 0, so the
   parent's wait4 rusage gives the worker's peak RSS without the high-water mark that Linux
   carries over from the shell across fork+execve. */
int cmain(long *sp){
  int argc=(int)sp[0]; char **argv=(char**)(sp+1);
  i64 pid=sc3(57,0,0,0);
  if(pid==0){ int rc=work(argc,argv); oflush(); sc3(60,rc,0,0); }
  if(pid<0) die("fork");
  struct { long ut[2], st[2]; long maxrss, rest[14]; } ru; int status=0;
  { i64 r; register i64 r10 __asm__("r10")=(i64)&ru; __asm__ volatile("syscall":"=a"(r):"a"(61L),"D"(pid),"S"((i64)&status),"d"(0L),"r"(r10):"rcx","r11","memory"); }
  for(int pass=1;pass<2;pass++){ fd_out=1;
    os("worker peak RSS (getrusage via wait4, worker forked from the 1-page parent) "); ou(ru.maxrss); os(" KiB = "); ou(ru.maxrss*1024); os(" bytes (limit 1048576)\n"); oflush(); }
  return ((status>>8)&255);
}
static void hexbytes(const u8 *p,int n){ for(int i=0;i<n;i++) ox8(p[i]); }
static long vmhwm(void){
  long hwm=-1; static char st[4096]; int fd=(int)sc3(2,(i64)"/proc/self/status",0,0);
  if(fd>=0){ long n=sc3(0,fd,(i64)st,sizeof st-1); fclose_(fd); if(n>0){ st[n]=0;
    for(long i=0;i+6<n;i++) if(st[i]=='V'&&st[i+1]=='m'&&st[i+2]=='H'&&st[i+3]=='W'&&st[i+4]=='M'){ long j=i+6,v=0; while(st[j]==' '||st[j]==9) j++; while(st[j]>='0'&&st[j]<='9') v=v*10+(st[j++]-'0'); hwm=v; break; } } }
  return hwm;
}
static int work(int argc,char **argv){
  mk_tables(); mk_tables2();
  int ntr= argc>1? atoi_(argv[1]) : 1; if(ntr<1) ntr=1;
  int t0= argc>2? atoi_(argv[2]) : 0;
  if(argc>3) optmode=atoi_(argv[3]);
  if(optmode>=8){ designx=1; optmode-=3; }   /* 8: design X + optmode 5 planning */
  if(argc>5){ u64 v=0; const char *q=argv[5]; while(*q){ int d= (*q>='0'&&*q<='9')? *q-'0' : (*q>='a'&&*q<='f')? *q-'a'+10 : -1; if(d<0) break; v=v*16+d; q++; } use_r=1; force_r=v; }
  if(argc>1 && argv[1][0]=='S'){ /* S seed iters maxflip : local search of r on the cheap count */
    u64 sd= atoi_(argv[2]); int iters=atoi_(argv[3]); int mf= argc>4? atoi_(argv[4]):3; optmode=0; mixfree=0; emitting=0; curpass=99; memset(decided,0,sizeof decided); use_r=1;
    rs=0x9E3779B97F4A7C15UL*(sd+7)+1; for(int i=0;i<10;i++) xs();
    u64 cur=xs(); force_r=cur; set_consts(0); build(); long cc=cnt[1]+cnt[2]+cnt[3]+cnt[4];
    os("start r "); ox(cur); os(" ops "); ou(cc); oc(10); oflush();
    long best=cc;
    for(int it=0;it<iters;it++){
      u64 c2=cur; int nf_=1+(int)(xs()%mf); for(int k=0;k<nf_;k++) c2^=1UL<<(xs()%64);
      force_r=c2; set_consts(0); build(); long t=cnt[1]+cnt[2]+cnt[3]+cnt[4];
      if(t<=cc){ cur=c2; cc=t; if(t<best){ best=t; os("it "); ou(it); os(" r "); ox(cur); os(" ops "); ou(t); oc(10); oflush(); } }
    }
    os("final r "); ox(cur); os(" ops "); ou(cc); oc(10); oflush(); return 0; }
  int insp= argc>4 && argv[4][0]=='i';   /* inspection command (a check run) only: also writes meta.txt and plan.txt */
  int om=optmode;
  int bestt=t0; long bestc=1L<<60;
  if(ntr>1){
    /* stage 1: cheap build (optmode 0) of every trial; keep the TOPK lowest counts (ties: lower trial first) */
    static long kc[TOPK]; static int kt[TOPK]; int nk=0;
    optmode=0; mixfree=0; emitting=0; curpass=99; memset(decided,0,sizeof decided);
    for(int t=t0;t<t0+ntr;t++){ set_consts(t); build(); long tot=cnt[1]+cnt[2]+cnt[3]+cnt[4];
      os("trial "); ou(t); os(" ops "); ou(tot); oc('\n');
      int pos=nk; while(pos>0 && kc[pos-1]>tot) pos--;
      if(pos<TOPK){ for(int i=(nk<TOPK?nk:TOPK-1);i>pos;i--){ kc[i]=kc[i-1]; kt[i]=kt[i-1]; } kc[pos]=tot; kt[pos]=t; if(nk<TOPK) nk++; } }
    oflush();
    /* stage 2: the full build (optmode) of each kept trial, counted; the lowest count wins (ties: earlier in the list) */
    optmode=om; mixfree= optmode>=2;
    for(int i=0;i<nk;i++){ set_consts(kt[i]); emitting=0; fullplan(); build(); long tot=cnt[1]+cnt[2]+cnt[3]+cnt[4];
      os("plan trial "); ou(kt[i]); os(" cheap "); ou(kc[i]); os(" full "); ou(tot); oc('\n'); oflush();
      if(tot<bestc){ bestc=tot; bestt=kt[i]; } }
  }
  optmode=om; mixfree= optmode>=2;
  set_consts(bestt);
  emitting=0; fullplan();
  fdp=fopen_w("prog.bin"); if(fdp<0) die("open prog.bin");
  emitting=1; build();
  if(enb){ eb[el++]=(u8)eacc; eacc=0; enb=0; }
  if(el) sc3(1,fdp,(i64)eb,el); el=0; fclose_(fdp);
  long pre=cnt_emit;
  long tot=cnt[1]+cnt[2]+cnt[3]+cnt[4];
  if(ninstr!=tot) die("instr count mismatch");
  long hwm=vmhwm();
  /* meta.txt */
  if(insp){
  fd_out=fopen_w("meta.txt");
  os("trial "); ou(bestt); oc('\n');
  for(int l=0;l<25;l++){ os("lane "); ou(l); oc(' '); ox(KL[l]); oc('\n'); }
  if(designx) os("designx 1 ; lanes x and 10+x = v_x ^ K ; v_0..v_3 = u_0..u_3 ; v_4 = XOR_(x<4) rotr(u_x,(39-ROT[x][2]) mod 64)\n");
  else os("varlanes 1 6 4 9 ; lane11 = u0^u1^K11 ; lane14 = u2^u3^K14\n");
  os("pd "); for(int i=0;i<4;i++){ ox(PD[i]); oc(i<3?' ':'\n'); }
  os("ninstr "); ou(ninstr); oc('\n');
  oflush(); fclose_(fd_out);
  }
  /* plan.txt: every decision of the build, for the Python port */
  if(insp){
  fd_out=fopen_w("plan.txt");
  os("trial "); ou(bestt); oc('\n');
  os("nr "); ou(NR); os(" optmode "); ou(optmode); os(" trick "); ou(TRICK); os(" lasttrick "); ou(LASTTRICK); os(" notfold "); ou(NOTFOLD); oc('\n');
  { u8 g[40]; memset(g,0,40); for(int i=0;i<320;i++){ g[i>>3]|=(u8)(G1[i/64][i%64]<<(i&7)); }
    os("F1 "); hexbytes(F1[0],320); oc('\n'); os("G1 "); hexbytes(g,40); oc('\n'); }
  for(int r=2;r<NR;r++){ os("FG "); ou(r); oc(' '); hexbytes(FMb[r],320); oc(' '); hexbytes(GGb[r],40); oc('\n'); }
  for(int r=0;r<NR;r++){ os("PHI "); ou(r); oc(' '); hexbytes(phib[r],200); oc('\n'); }
  for(int r=1;r<NR;r++) if(decd[r]){ u8 d[640]; for(int i=0;i<320;i++){ d[2*i]=(u8)(dec[r][i]&255); d[2*i+1]=(u8)(dec[r][i]>>8); } os("DEC "); ou(r); oc(' '); hexbytes(d,640); oc('\n'); os("DECE "); ou(r); oc(' '); hexbytes(decE[r],320); oc('\n'); }
  if(designx && r1ov_on){ os("R1OV "); hexbytes(r1ov,320); oc('\n'); os("R1E "); hexbytes(r1E,320); oc('\n'); }   /* design X: round-1 row search decisions */
  oflush(); fclose_(fd_out);
  }
  /* ledger: standard output only */
  for(int pass=1;pass<2;pass++){
    fd_out=1;
    os("LS1 step ledger (256 lanes, one chain step, "); ou(NR); os(" rounds), streaming generator gen3\n");
    os("XOR "); ou(cnt[O_XOR]); oc('\n');
    os("AND "); ou(cnt[O_AND]); oc('\n');
    os("OR  "); ou(cnt[O_OR]); oc('\n');
    os("NOT "); ou(cnt[O_NOT]); os("  (row complements chosen pre-DCE: "); ou(nnot_rows); os(")\n");
    os("LOAD 0\nSTORE 0\nTOTAL "); ou(tot); oc('\n');
    os("TRICKROWS "); ou(ntrick); os(" ; forced term polarities "); ou(nforced); oc('\n');
    os("feed NOTs 0 (digest polarity folded into the chain function: F(u)=H(m(u))^PD)\n");
    os("nodes created pre-DCE "); ou(pre); os(" ; ring peak "); ou(maxring); os(" of "); ou(W); os(" ; linear forms "); ou(maxform); os(" of "); ou(MAXF); oc('\n');
    os("max live values "); ou(maxlive); os(" ; registers used "); ou(maxreg); os(" (limit 2304)\n");
    os("constants trial "); ou(bestt); os(" of "); ou(ntr); os(" ; optmode "); ou(optmode); os(" ; designx "); ou(designx); os(" ; shared round-1 pins "); ou(npinsh_r1); os(" ; round-1 greedy gain "); ou(r1gain); os(" ; round-1 row search rounds 0..1 "); ou(r1rp0); os(" -> "); ou(r1rp1); os(" ; r2 lookahead "); ou(r1rlook0); os(" -> "); ou(r1rlook1); oc(10); os("round-1 row search builds per plan "); ou(r1rbuilds_plan); oc('\n');
    os("annealing iterations per round "); ou(OPTIT); oc('\n');
    os("trials carried to the plan build "); ou(TOPK); oc('\n');
    for(int r=2;r<NR;r++){ os("plan r"); ou(r); os(" predicted row cost "); ou(pol_pred[r]); os(" theta NOTs "); ou(pol_nots[r]); os(" free polarities set "); ou(pol_phi[r]); oc('\n'); }
    for(int r=1;r<NR;r++){ os("cum after round "); ou(r); os(" "); ou(rcum[r]); oc(10); }
    os("generator peak RSS (VmHWM, this process image) "); ou(hwm); os(" KiB = "); ou(hwm*1024); os(" bytes (limit 1048576)\n");
    oflush();
  }
  if(maxreg>NREG) return 2;
  return 0;
}
```

kbasis.h (compiled in; design X does not read it, Section 2):

```c
/* S3-04 structured constants: the solutions of the 704 round-0 chi neighbour conditions (rank 704) are
   KB0 xor sum of KBV[i] over the set bits i of a 64-bit word r (free dimension 64); lanes 0,2,3,5,7,8,10,12,13,15,11,14 */
static const u64 KB0[12]={0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0xffffffffffffffffUL,0x0000000000000000UL,0x0000000000000000UL,0xffffffffffffffffUL,0x0000000000000000UL,0x0000000000000000UL,0xffffffffffffffffUL,0x8000000000000006UL,0xffffffffffffffffUL};
static const u64 KBV[64][12]={
{0x0000000000000000UL,0x0000000000000001UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x2000000000000000UL,0x0000000000000000UL,0x4000000000000000UL,0x8000000000000000UL},
{0x0000000000000000UL,0x0000000000000002UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x4000000000000000UL,0x0000000000000000UL,0x8000000000000000UL,0x0000000000000001UL},
{0x0000000000000000UL,0x0000000000000004UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x8000000000000000UL,0x0000000000000000UL,0x0000000000000001UL,0x0000000000000002UL},
{0x0000000000000000UL,0x0000000000000008UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000001UL,0x0000000000000000UL,0x0000000000000002UL,0x0000000000000004UL},
{0x0000000000000000UL,0x0000000000000010UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000002UL,0x0000000000000000UL,0x0000000000000004UL,0x0000000000000008UL},
{0x0000000000000000UL,0x0000000000000020UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000004UL,0x0000000000000000UL,0x0000000000000008UL,0x0000000000000010UL},
{0x0000000000000000UL,0x0000000000000040UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000008UL,0x0000000000000000UL,0x0000000000000010UL,0x0000000000000020UL},
{0x0000000000000000UL,0x0000000000000080UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000010UL,0x0000000000000000UL,0x0000000000000020UL,0x0000000000000040UL},
{0x0000000000000000UL,0x0000000000000100UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000020UL,0x0000000000000000UL,0x0000000000000040UL,0x0000000000000080UL},
{0x0000000000000000UL,0x0000000000000200UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000040UL,0x0000000000000000UL,0x0000000000000080UL,0x0000000000000100UL},
{0x0000000000000000UL,0x0000000000000400UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000080UL,0x0000000000000000UL,0x0000000000000100UL,0x0000000000000200UL},
{0x0000000000000000UL,0x0000000000000800UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000100UL,0x0000000000000000UL,0x0000000000000200UL,0x0000000000000400UL},
{0x0000000000000000UL,0x0000000000001000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000200UL,0x0000000000000000UL,0x0000000000000400UL,0x0000000000000800UL},
{0x0000000000000000UL,0x0000000000002000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000400UL,0x0000000000000000UL,0x0000000000000800UL,0x0000000000001000UL},
{0x0000000000000000UL,0x0000000000004000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000800UL,0x0000000000000000UL,0x0000000000001000UL,0x0000000000002000UL},
{0x0000000000000000UL,0x0000000000008000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000001000UL,0x0000000000000000UL,0x0000000000002000UL,0x0000000000004000UL},
{0x0000000000000000UL,0x0000000000010000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000002000UL,0x0000000000000000UL,0x0000000000004000UL,0x0000000000008000UL},
{0x0000000000000000UL,0x0000000000020000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000004000UL,0x0000000000000000UL,0x0000000000008000UL,0x0000000000010000UL},
{0x0000000000000000UL,0x0000000000040000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000008000UL,0x0000000000000000UL,0x0000000000010000UL,0x0000000000020000UL},
{0x0000000000000000UL,0x0000000000080000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000010000UL,0x0000000000000000UL,0x0000000000020000UL,0x0000000000040000UL},
{0x0000000000000000UL,0x0000000000100000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000020000UL,0x0000000000000000UL,0x0000000000040000UL,0x0000000000080000UL},
{0x0000000000000000UL,0x0000000000200000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000040000UL,0x0000000000000000UL,0x0000000000080000UL,0x0000000000100000UL},
{0x0000000000000000UL,0x0000000000400000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000080000UL,0x0000000000000000UL,0x0000000000100000UL,0x0000000000200000UL},
{0x0000000000000000UL,0x0000000000800000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000100000UL,0x0000000000000000UL,0x0000000000200000UL,0x0000000000400000UL},
{0x0000000000000000UL,0x0000000001000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000200000UL,0x0000000000000000UL,0x0000000000400000UL,0x0000000000800000UL},
{0x0000000000000000UL,0x0000000002000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000400000UL,0x0000000000000000UL,0x0000000000800000UL,0x0000000001000000UL},
{0x0000000000000000UL,0x0000000004000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000800000UL,0x0000000000000000UL,0x0000000001000000UL,0x0000000002000000UL},
{0x0000000000000000UL,0x0000000008000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000001000000UL,0x0000000000000000UL,0x0000000002000000UL,0x0000000004000000UL},
{0x0000000000000000UL,0x0000000010000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000002000000UL,0x0000000000000000UL,0x0000000004000000UL,0x0000000008000000UL},
{0x0000000000000000UL,0x0000000020000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000004000000UL,0x0000000000000000UL,0x0000000008000000UL,0x0000000010000000UL},
{0x0000000000000000UL,0x0000000040000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000008000000UL,0x0000000000000000UL,0x0000000010000000UL,0x0000000020000000UL},
{0x0000000000000000UL,0x0000000080000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000010000000UL,0x0000000000000000UL,0x0000000020000000UL,0x0000000040000000UL},
{0x0000000000000000UL,0x0000000100000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000020000000UL,0x0000000000000000UL,0x0000000040000000UL,0x0000000080000000UL},
{0x0000000000000000UL,0x0000000200000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000040000000UL,0x0000000000000000UL,0x0000000080000000UL,0x0000000100000000UL},
{0x0000000000000000UL,0x0000000400000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000080000000UL,0x0000000000000000UL,0x0000000100000000UL,0x0000000200000000UL},
{0x0000000000000000UL,0x0000000800000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000100000000UL,0x0000000000000000UL,0x0000000200000000UL,0x0000000400000000UL},
{0x0000000000000000UL,0x0000001000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000200000000UL,0x0000000000000000UL,0x0000000400000000UL,0x0000000800000000UL},
{0x0000000000000000UL,0x0000002000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000400000000UL,0x0000000000000000UL,0x0000000800000000UL,0x0000001000000000UL},
{0x0000000000000000UL,0x0000004000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000800000000UL,0x0000000000000000UL,0x0000001000000000UL,0x0000002000000000UL},
{0x0000000000000000UL,0x0000008000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000001000000000UL,0x0000000000000000UL,0x0000002000000000UL,0x0000004000000000UL},
{0x0000000000000000UL,0x0000010000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000002000000000UL,0x0000000000000000UL,0x0000004000000000UL,0x0000008000000000UL},
{0x0000000000000000UL,0x0000020000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000004000000000UL,0x0000000000000000UL,0x0000008000000000UL,0x0000010000000000UL},
{0x0000000000000000UL,0x0000040000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000008000000000UL,0x0000000000000000UL,0x0000010000000000UL,0x0000020000000000UL},
{0x0000000000000000UL,0x0000080000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000010000000000UL,0x0000000000000000UL,0x0000020000000000UL,0x0000040000000000UL},
{0x0000000000000000UL,0x0000100000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000020000000000UL,0x0000000000000000UL,0x0000040000000000UL,0x0000080000000000UL},
{0x0000000000000000UL,0x0000200000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000040000000000UL,0x0000000000000000UL,0x0000080000000000UL,0x0000100000000000UL},
{0x0000000000000000UL,0x0000400000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000080000000000UL,0x0000000000000000UL,0x0000100000000000UL,0x0000200000000000UL},
{0x0000000000000000UL,0x0000800000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000100000000000UL,0x0000000000000000UL,0x0000200000000000UL,0x0000400000000000UL},
{0x0000000000000000UL,0x0001000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000200000000000UL,0x0000000000000000UL,0x0000400000000000UL,0x0000800000000000UL},
{0x0000000000000000UL,0x0002000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000400000000000UL,0x0000000000000000UL,0x0000800000000000UL,0x0001000000000000UL},
{0x0000000000000000UL,0x0004000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000800000000000UL,0x0000000000000000UL,0x0001000000000000UL,0x0002000000000000UL},
{0x0000000000000000UL,0x0008000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0001000000000000UL,0x0000000000000000UL,0x0002000000000000UL,0x0004000000000000UL},
{0x0000000000000000UL,0x0010000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0002000000000000UL,0x0000000000000000UL,0x0004000000000000UL,0x0008000000000000UL},
{0x0000000000000000UL,0x0020000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0004000000000000UL,0x0000000000000000UL,0x0008000000000000UL,0x0010000000000000UL},
{0x0000000000000000UL,0x0040000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0008000000000000UL,0x0000000000000000UL,0x0010000000000000UL,0x0020000000000000UL},
{0x0000000000000000UL,0x0080000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0010000000000000UL,0x0000000000000000UL,0x0020000000000000UL,0x0040000000000000UL},
{0x0000000000000000UL,0x0100000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0020000000000000UL,0x0000000000000000UL,0x0040000000000000UL,0x0080000000000000UL},
{0x0000000000000000UL,0x0200000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0040000000000000UL,0x0000000000000000UL,0x0080000000000000UL,0x0100000000000000UL},
{0x0000000000000000UL,0x0400000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0080000000000000UL,0x0000000000000000UL,0x0100000000000000UL,0x0200000000000000UL},
{0x0000000000000000UL,0x0800000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0100000000000000UL,0x0000000000000000UL,0x0200000000000000UL,0x0400000000000000UL},
{0x0000000000000000UL,0x1000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0200000000000000UL,0x0000000000000000UL,0x0400000000000000UL,0x0800000000000000UL},
{0x0000000000000000UL,0x2000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0400000000000000UL,0x0000000000000000UL,0x0800000000000000UL,0x1000000000000000UL},
{0x0000000000000000UL,0x4000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0800000000000000UL,0x0000000000000000UL,0x1000000000000000UL,0x2000000000000000UL},
{0x0000000000000000UL,0x8000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x1000000000000000UL,0x0000000000000000UL,0x2000000000000000UL,0x4000000000000000UL},
};
```

The self-test (compiled with `-DRR=23`; `selftest kat` prints 300 known answers, compared with hashlib and the organizer's verifier/keccak.py; `selftest run 4 [seed]` runs the chained check):

```c
/* selftest.c - checks the emitted LS1 straight line (prog.bin + meta.txt) against a plain
 * lane-wise Keccak reference written here (rounds 0..R-1, SHA3 padding, 136-byte rate).
 *   selftest kat            : prints "hexmsg digest24 digest6" for 300 deterministic messages
 *                             (lengths 0..299) for comparison with hashlib / the organizer reference
 *   selftest run [nbatch]   : nbatch x 256 random points, 4 chained steps each; counts mismatches
 *                             of the program output against F(u) = SHA3-256-r8(m(u)) ^ PD.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef uint64_t u64;
#ifndef RR
#define RR 8
#endif

static const u64 RC[24]={0x0000000000000001ULL,0x0000000000008082ULL,0x800000000000808aULL,0x8000000080008000ULL,
 0x000000000000808bULL,0x0000000080000001ULL,0x8000000080008081ULL,0x8000000000008009ULL,0x000000000000008aULL,
 0x0000000000000088ULL,0x0000000080008009ULL,0x000000008000000aULL,0x000000008000808bULL,0x800000000000008bULL,
 0x8000000000008089ULL,0x8000000000008003ULL,0x8000000000008002ULL,0x8000000000000080ULL,0x000000000000800aULL,
 0x800000008000000aULL,0x8000000080008081ULL,0x8000000000008080ULL,0x0000000080000001ULL,0x8000000080008008ULL};
static const int RHO[25]={0,1,62,28,27, 36,44,6,55,20, 3,10,43,25,39, 41,45,15,21,8, 18,2,61,56,14}; /* index x+5y */
static u64 rotl(u64 v,int r){ return r? (v<<r)|(v>>(64-r)) : v; }

static void keccakf(u64 A[25], int rounds){
  for(int r=0;r<rounds;r++){
    u64 C[5],D[5],B[25];
    for(int x=0;x<5;x++) C[x]=A[x]^A[x+5]^A[x+10]^A[x+15]^A[x+20];
    for(int x=0;x<5;x++) D[x]=C[(x+4)%5]^rotl(C[(x+1)%5],1);
    for(int i=0;i<25;i++) A[i]^=D[i%5];
    for(int x=0;x<5;x++) for(int y=0;y<5;y++) B[y+5*((2*x+3*y)%5)]=rotl(A[x+5*y],RHO[x+5*y]);
    for(int y=0;y<5;y++) for(int x=0;x<5;x++) A[x+5*y]=B[x+5*y]^((~B[(x+1)%5+5*y])&B[(x+2)%5+5*y]);
    A[0]^=RC[r];
  }
}
static void sha3_256r(const uint8_t *m, size_t len, int rounds, uint8_t out[32]){
  u64 A[25]; memset(A,0,sizeof A);
  uint8_t blk[136]; size_t off=0;
  for(;;){
    size_t rem=len-off;
    if(rem>=136){ memcpy(blk,m+off,136); off+=136; }
    else { memset(blk,0,136); memcpy(blk,m+off,rem); blk[rem]^=0x06; blk[135]^=0x80; off=len+1; }
    for(int i=0;i<17;i++){ u64 w=0; for(int k=0;k<8;k++) w|=(u64)blk[8*i+k]<<(8*k); A[i]^=w; }
    keccakf(A,rounds);
    if(off>len) break;
  }
  for(int i=0;i<32;i++) out[i]=(uint8_t)(A[i/8]>>(8*(i%8)));
}

static u64 KL[25], PD[4]; static long ninstr; static int dx;
static uint8_t *prog;

static long progbytes; static uint8_t *pop; static uint16_t *pdd, *pda, *pdb;
static u64 getb_(long pos, int n){ const uint8_t *p=prog+(pos>>3); u64 w=0; for(int k=0;k<6;k++) w|=(u64)p[k]<<(8*k); return (w>>(pos&7))&((1ULL<<n)-1); }
static void decode_prog(void){   /* two-address encoding: 2-bit op, 1-bit t (t=1: d = a), 11-bit registers; NOT has no b */
  pop=malloc(ninstr); pdd=malloc(2*ninstr); pda=malloc(2*ninstr); pdb=malloc(2*ninstr); long pos=0;
  for(long i=0;i<ninstr;i++){ int op=(int)getb_(pos,2), t=(int)getb_(pos+2,1); pos+=3; int d,a,b=0;
    if(t){ a=(int)getb_(pos,11); pos+=11; d=a; } else { d=(int)getb_(pos,11); a=(int)getb_(pos+11,11); pos+=22; }
    if(op!=3){ b=(int)getb_(pos,11); pos+=11; }
    pop[i]=(uint8_t)op; pdd[i]=(uint16_t)d; pda[i]=(uint16_t)a; pdb[i]=(uint16_t)b; }
  if((pos+7)/8!=progbytes){ fprintf(stderr,"prog.bin length %ld != decoded %ld\n",progbytes,(pos+7)/8); exit(2); }
}
static void load(void){
  FILE *f=fopen("meta.txt","r"); if(!f){ perror("meta.txt"); exit(2); }
  char line[512];
  while(fgets(line,sizeof line,f)){
    int l; unsigned long long v,a,b,c,d;
    if(sscanf(line,"lane %d %llx",&l,&v)==2) KL[l]=v;
    else if(sscanf(line,"pd %llx %llx %llx %llx",&a,&b,&c,&d)==4){ PD[0]=a;PD[1]=b;PD[2]=c;PD[3]=d; }
    else if(sscanf(line,"ninstr %ld",&ninstr)==1){}
    else if(!strncmp(line,"designx 1",9)) dx=1;
  }
  fclose(f);
  f=fopen("prog.bin","rb"); if(!f){ perror("prog.bin"); exit(2); }
  fseek(f,0,SEEK_END); progbytes=ftell(f); fseek(f,0,SEEK_SET);
  prog=calloc(progbytes+8,1); if(fread(prog,1,progbytes,f)!=(size_t)progbytes){ fprintf(stderr,"short prog\n"); exit(2); } fclose(f);
  decode_prog();
}
/* message m(u): 128 bytes = lanes 0..15 */
static void msg_of(const u64 u[4], uint8_t m[128]){
  u64 L[16]; for(int i=0;i<16;i++) L[i]=KL[i];
  if(dx){ /* design X (11565cb4): lanes x and 10+x = v_x ^ K; v_4 = XOR_(x<4) rotr(u_x,(39-ROT[x][2]) mod 64) */
    static const int R2[4]={3,10,43,25}; u64 v[5]; for(int x=0;x<4;x++) v[x]=u[x]; v[4]=0;
    for(int x=0;x<4;x++){ int s=(39-R2[x]+64)&63; v[4]^= s? (u[x]>>s)|(u[x]<<(64-s)) : u[x]; }
    for(int x=0;x<5;x++){ L[x]=v[x]^KL[x]; L[10+x]=v[x]^KL[10+x]; }
    for(int i=0;i<128;i++) m[i]=(uint8_t)(L[i/8]>>(8*(i%8))); return; }
  L[1]=u[0]; L[6]=u[1]; L[11]=u[0]^u[1]^KL[11];
  L[4]=u[2]; L[9]=u[3]; L[14]=u[2]^u[3]^KL[14];
  for(int i=0;i<128;i++) m[i]=(uint8_t)(L[i/8]>>(8*(i%8)));
}
static void Fref(const u64 u[4], u64 o[4]){
  uint8_t m[128], d[32]; msg_of(u,m); sha3_256r(m,128,RR,d);
  for(int i=0;i<4;i++){ u64 w=0; for(int k=0;k<8;k++) w|=(u64)d[8*i+k]<<(8*k); o[i]=w^PD[i]; }
}
typedef struct { u64 w[4]; } W256;
static W256 R[2304];
static void run_prog(void){
  for(long i=0;i<ninstr;i++){
    int op=pop[i], d=pdd[i], a=pda[i], b=pdb[i]; W256 t;
    for(int k=0;k<4;k++){ u64 x=R[a].w[k], y=R[b].w[k];
      t.w[k]= op==0? x^y : op==1? x&y : op==2? x|y : ~x; }
    if(op>3 || d>=2304){ fprintf(stderr,"bad instr %ld\n",i); exit(3); }
    R[d]=t;
  }
}
static u64 rs=0x0123456789abcdefULL;
static u64 xr(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

int main(int argc,char **argv){
  if(argc>1 && !strcmp(argv[1],"kat")){
    for(int len=0;len<300;len++){
      uint8_t m[300],d24[32],d6[32]; for(int i=0;i<len;i++) m[i]=(uint8_t)xr();
      sha3_256r(m,len,24,d24); sha3_256r(m,len,RR,d6);
      for(int i=0;i<len;i++) printf("%02x",m[i]); printf(" ");
      for(int i=0;i<32;i++) printf("%02x",d24[i]); printf(" ");
      for(int i=0;i<32;i++) printf("%02x",d6[i]); printf("\n");
    }
    return 0;
  }
  int nb= argc>2? atoi(argv[2]) : 2;
  if(argc>3) rs=strtoull(argv[3],0,0);
  load();
  long mism=0, evals=0;
  for(int bt=0;bt<nb;bt++){
    static u64 U[256][4];
    for(int t=0;t<256;t++) for(int i=0;i<4;i++) U[t][i]=xr();
    for(int j=0;j<256;j++) for(int k=0;k<4;k++){ u64 w=0; for(int b=0;b<64;b++){ int t=64*k+b; w|=((U[t][j>>6]>>(j&63))&1)<<b; } R[j].w[k]=w; }
    for(int step=0;step<4;step++){
      run_prog();
      for(int t=0;t<256;t++){
        u64 o[4], g[4]={0,0,0,0}; Fref(U[t],o);
        for(int j=0;j<256;j++) g[j>>6]|=((R[j].w[t>>6]>>(t&63))&1)<<(j&63);
        if(memcmp(o,g,32)) { if(mism<5) fprintf(stderr,"mismatch batch %d step %d trail %d\n",bt,step,t); mism++; }
        evals++;
        memcpy(U[t],o,32);   /* chain on the reference value */
      }
    }
  }
  printf("selftest%s: %ld chained evaluations (%d batches x 256 trails x 4 steps), %ld mismatches, %ld instructions\n",dx?" (design X)":"",evals,nb,mism,ninstr);
  return mism?1:0;
}
```

Output of the run (the ledger, standard output) and of the self-test:

```
LS1 step ledger (256 lanes, one chain step, 23 rounds), streaming generator gen3
XOR 100288
AND 18704
OR  14509
NOT 3161  (row complements chosen pre-DCE: 299)
LOAD 0
STORE 0
TOTAL 136662
TRICKROWS 6396 ; forced term polarities 4
feed NOTs 0 (digest polarity folded into the chain function: F(u)=H(m(u))^PD)
nodes created pre-DCE 136869 ; ring peak 6847 of 8192 ; linear forms 1813 of 2048
max live values 2025 ; registers used 2025 (limit 2304)
constants trial 1106 of 512 ; optmode 5 ; designx 1 ; shared round-1 pins 0 ; round-1 greedy gain 105 ; round-1 row search rounds 0..1 3238 -> 3187 ; r2 lookahead 1930 -> 1821
round-1 row search builds per plan 63714
annealing iterations per round 150000000
trials carried to the plan build 1
plan r2 predicted row cost 1652 theta NOTs 112 free polarities set 0
plan r3 predicted row cost 1644 theta NOTs 102 free polarities set 0
plan r4 predicted row cost 1651 theta NOTs 111 free polarities set 0
plan r5 predicted row cost 1639 theta NOTs 105 free polarities set 0
plan r6 predicted row cost 1644 theta NOTs 111 free polarities set 0
plan r7 predicted row cost 1644 theta NOTs 95 free polarities set 0
plan r8 predicted row cost 1638 theta NOTs 109 free polarities set 0
plan r9 predicted row cost 1641 theta NOTs 108 free polarities set 0
plan r10 predicted row cost 1643 theta NOTs 112 free polarities set 0
plan r11 predicted row cost 1642 theta NOTs 105 free polarities set 0
plan r12 predicted row cost 1637 theta NOTs 113 free polarities set 0
plan r13 predicted row cost 1646 theta NOTs 103 free polarities set 0
plan r14 predicted row cost 1639 theta NOTs 115 free polarities set 0
plan r15 predicted row cost 1641 theta NOTs 111 free polarities set 0
plan r16 predicted row cost 1645 theta NOTs 109 free polarities set 0
plan r17 predicted row cost 1645 theta NOTs 110 free polarities set 0
plan r18 predicted row cost 1640 theta NOTs 103 free polarities set 0
plan r19 predicted row cost 1649 theta NOTs 109 free polarities set 0
plan r20 predicted row cost 1643 theta NOTs 113 free polarities set 0
plan r21 predicted row cost 1646 theta NOTs 96 free polarities set 0
plan r22 predicted row cost 261 theta NOTs 13 free polarities set 8
cum after round 1 3187
cum after round 2 9747
cum after round 3 16293
cum after round 4 22855
cum after round 5 29399
cum after round 6 35954
cum after round 7 42493
cum after round 8 49040
cum after round 9 55589
cum after round 10 62144
cum after round 11 68691
cum after round 12 75241
cum after round 13 81790
cum after round 14 88344
cum after round 15 94896
cum after round 16 101450
cum after round 17 108005
cum after round 18 114548
cum after round 19 121106
cum after round 20 127662
cum after round 21 134204
cum after round 22 136662
generator peak RSS (VmHWM, this process image) 456 KiB = 466944 bytes (limit 1048576)
kat messages 300 (lengths 0..299): 24-round vs hashlib mismatches 0; 23-round vs organizer verifier mismatches 0
seed 0x0123456789abcdef: selftest (design X): 65536 chained evaluations (64 batches x 256 trails x 4 steps), 0 mismatches, 136662 instructions
seed 0x1234567: selftest (design X): 65536 chained evaluations (64 batches x 256 trails x 4 steps), 0 mismatches, 136662 instructions
seed 0x9e3779b97f4a7c15: selftest (design X): 65536 chained evaluations (64 batches x 256 trails x 4 steps), 0 mismatches, 136662 instructions
```

## Appendix C. The measured check of H_rand (hrand_test.c)

```c
/* hrand_test.c - measured checks of the premise H_rand for the LS1 chain function F (prog.bin + meta.txt).
 * Executes the emitted straight line (256 lanes per step) and counts, among M = 2^24 evaluations,
 * the pairs of images that agree on a 32-bit window (low bits 0..31, bits 128..159, top bits 224..255):
 *   A: uniform random inputs (independent images expected: C(M,2)/2^32 pairs, Poisson)
 *   B: structured inputs R + i, i < M (the start pattern of the search: consecutive integers)
 *   C: iterates: 256 chains of 65,536 chained steps from random starts (the points a walk evaluates)
 * and D: single-bit input differences: for each of the 256 input bits j, 4,096 random u, the count of output bit k
 *   flipping in F(u) ^ F(u ^ e_j), for all 65,536 (j,k) cells; reports the largest |z| (binomial 4096, 1/2).
 * Usage: hrand_test [seed]   (reads prog.bin and meta.txt from the current directory) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
typedef uint64_t u64;
static long ninstr; static uint8_t *prog;

static long progbytes; static uint8_t *pop; static uint16_t *pdd, *pda, *pdb;
static u64 getb_(long pos, int n){ const uint8_t *p=prog+(pos>>3); u64 w=0; for(int k=0;k<6;k++) w|=(u64)p[k]<<(8*k); return (w>>(pos&7))&((1ULL<<n)-1); }
static void decode_prog(void){   /* two-address encoding: 2-bit op, 1-bit t (t=1: d = a), 11-bit registers; NOT has no b */
  pop=malloc(ninstr); pdd=malloc(2*ninstr); pda=malloc(2*ninstr); pdb=malloc(2*ninstr); long pos=0;
  for(long i=0;i<ninstr;i++){ int op=(int)getb_(pos,2), t=(int)getb_(pos+2,1); pos+=3; int d,a,b=0;
    if(t){ a=(int)getb_(pos,11); pos+=11; d=a; } else { d=(int)getb_(pos,11); a=(int)getb_(pos+11,11); pos+=22; }
    if(op!=3){ b=(int)getb_(pos,11); pos+=11; }
    pop[i]=(uint8_t)op; pdd[i]=(uint16_t)d; pda[i]=(uint16_t)a; pdb[i]=(uint16_t)b; }
  if((pos+7)/8!=progbytes){ fprintf(stderr,"prog.bin length %ld != decoded %ld\n",progbytes,(pos+7)/8); exit(2); }
}
typedef struct { u64 w[4]; } W256;
static W256 R[2304];
static void load(void){
  FILE *f=fopen("meta.txt","r"); char line[512];
  while(fgets(line,sizeof line,f)) sscanf(line,"ninstr %ld",&ninstr);
  fclose(f); f=fopen("prog.bin","rb"); fseek(f,0,SEEK_END); progbytes=ftell(f); fseek(f,0,SEEK_SET);
  prog=calloc(progbytes+8,1); if(fread(prog,1,progbytes,f)!=(size_t)progbytes) exit(2); fclose(f);
  decode_prog();
}
static void run_prog(void){
  for(long i=0;i<ninstr;i++){
    int op=pop[i], d=pdd[i], a=pda[i], b=pdb[i];
    W256 *x=&R[a],*y=&R[b],t;
    switch(op){ case 0: for(int k=0;k<4;k++) t.w[k]=x->w[k]^y->w[k]; break;
                case 1: for(int k=0;k<4;k++) t.w[k]=x->w[k]&y->w[k]; break;
                case 2: for(int k=0;k<4;k++) t.w[k]=x->w[k]|y->w[k]; break;
                default: for(int k=0;k<4;k++) t.w[k]=~x->w[k]; }
    R[d]=t;
  }
}
static u64 sm;
static u64 rnd(void){ u64 z=(sm+=0x9E3779B97F4A7C15ULL); z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31); }
/* set lane t (0..255) of the 256 input planes to point u[4] */
static void set_point(int t,const u64 u[4]){ for(int j=0;j<256;j++){ u64 bit=(u[j>>6]>>(j&63))&1; u64 m=1ULL<<(t&63); R[j].w[t>>6]=(R[j].w[t>>6]&~m)|(bit<<(t&63)); } }
static void get_point(int t,u64 o[4]){ o[0]=o[1]=o[2]=o[3]=0; for(int j=0;j<256;j++) o[j>>6]|=((R[j].w[t>>6]>>(t&63))&1)<<(j&63); }
static uint32_t window(int t,int lo){ uint32_t v=0; for(int j=0;j<32;j++) v|=(uint32_t)((R[lo+j].w[t>>6]>>(t&63))&1)<<j; return v; }
static int cmpu(const void*a,const void*b){ uint32_t x=*(const uint32_t*)a,y=*(const uint32_t*)b; return x<y?-1:x>y; }
static double pairs(uint32_t *k,long M){ qsort(k,M,4,cmpu); double p=0; long i=0; while(i<M){ long j=i; while(j<M&&k[j]==k[i]) j++; double c=j-i; p+=c*(c-1)/2; i=j; } return p; }
#define LM 24
static uint32_t *K0,*K1,*K2;
static void report(const char *name,long M){
  double E=(double)M*(M-1)/2/4294967296.0;
  double p0=pairs(K0,M),p1=pairs(K1,M),p2=pairs(K2,M);
  printf("%s: M=2^%d, pairs agreeing on 32 bits: low %.0f, mid %.0f, top %.0f; expected %.1f each (sd %.1f); ratios %.4f %.4f %.4f; z %.2f %.2f %.2f\n",
    name,LM,p0,p1,p2,E,sqrt(E),p0/E,p1/E,p2/E,(p0-E)/sqrt(E),(p1-E)/sqrt(E),(p2-E)/sqrt(E));
}
int main(int argc,char**argv){
  sm= argc>1? strtoull(argv[1],0,0) : 0x15c0ffee;
  load();
  long M=1L<<LM, S=M/256;
  K0=malloc(M*4); K1=malloc(M*4); K2=malloc(M*4);
  /* A: uniform random inputs */
  for(long s=0;s<S;s++){
    for(int j=0;j<256;j++) for(int k=0;k<4;k++) R[j].w[k]=rnd();
    run_prog();
    for(int t=0;t<256;t++){ long e=s*256+t; K0[e]=window(t,0); K1[e]=window(t,128); K2[e]=window(t,224); }
  }
  report("A uniform inputs",M);
  /* B: consecutive inputs R0 + i */
  u64 R0[4]={rnd(),rnd(),rnd(),rnd()};
  for(long s=0;s<S;s++){
    for(int t=0;t<256;t++){ u64 i=(u64)(s*256+t), u[4]; u[0]=R0[0]+i; u64 c=u[0]<R0[0]; for(int k=1;k<4;k++){ u[k]=R0[k]+c; c=c&&u[k]==0; } set_point(t,u); }
    run_prog();
    for(int t=0;t<256;t++){ long e=s*256+t; K0[e]=window(t,0); K1[e]=window(t,128); K2[e]=window(t,224); }
  }
  report("B consecutive inputs R+i",M);
  /* C: iterates of 256 chains */
  for(int j=0;j<256;j++) for(int k=0;k<4;k++) R[j].w[k]=rnd();
  for(long s=0;s<S;s++){
    run_prog();
    for(int t=0;t<256;t++){ long e=s*256+t; K0[e]=window(t,0); K1[e]=window(t,128); K2[e]=window(t,224); }
  }
  report("C chained iterates (256 chains x 65536 steps)",M);
  /* D: single-bit input differences */
  static uint32_t cnt[256][256]; memset(cnt,0,sizeof cnt);
  int NS=4096;
  for(int j=0;j<256;j++){
    for(int s=0;s<NS/128;s++){
      u64 u[128][4];
      for(int t=0;t<128;t++){ for(int k=0;k<4;k++) u[t][k]=rnd(); u64 v[4]; memcpy(v,u[t],32); set_point(t,v); v[j>>6]^=1ULL<<(j&63); set_point(128+t,v); }
      run_prog();
      for(int t=0;t<128;t++){ u64 a[4],b[4]; get_point(t,a); get_point(128+t,b); for(int k=0;k<256;k++) cnt[j][k]+=((a[k>>6]^b[k>>6])>>(k&63))&1; }
    }
  }
  double zmax=0; int jm=0,km=0; double sum=0;
  for(int j=0;j<256;j++) for(int k=0;k<256;k++){ double z=(cnt[j][k]-NS/2.0)/sqrt(NS/4.0); sum+=z*z; if(fabs(z)>zmax){ zmax=fabs(z); jm=j; km=k; } }
  printf("D single-bit differences: 65536 cells x %d pairs, max |z| %.2f at input bit %d output bit %d (largest of 65536 normal cells is about 4.4); mean z^2 %.4f (expected 1)\n",NS,zmax,jm,km,sum/65536);
  return 0;
}
```

## Appendix D. The other code (other4.py), its tests (other4_test.py) and their results

### D.1 other4.py: the other code, the machine and the counts

`params.json` of this package:

```
{"NR": 23, "HF": 111, "DPLO": 145, "DK": 10, "DT": 584, "S": 15424, "U": 77120, "SB": 14, "W": 633825300114114700748351602688, "J": 77207, "LRC": 48935749945910453700677982188732416, "Tb": 1326663716884019821919338815169757184, "HMAX": 54118035032196129959512860308537345, "PFLO": 240, "PFN": 16}
```

```python
#!/usr/bin/env python3
# other4.py - the non-straight-line code of LS1 (setup, loop control, hit handler, DP handler with the packed table,
# restart, replay, final output), written as real instructions of the machine of proof.md Section 3.5,
# plus the machine (an interpreter that executes the emitted bytes) and the counting of the operations.
#
#   python3 other4.py build [meta.txt]    reads params.json (NR, S, U, SB, LRC, Tb, HMAX, DPLO, DK, DT, PFLO, PFN), writes other.bin
#                                          (8-byte instruction words and the literal pool), pf.bin (the 15 prefilter ORs, two-address encoding), data.bin
#                                          (the 16-word data image from meta.txt) and counts.txt (instruction counts and the
#                                          operation count of every routine, read from the emitted code)
#   other4_test.py                         routine tests and end-to-end runs of the emitted program (reduced width)
#
# Table: S words of 256 bits, five slots of 51 bits per word (slot k = bits 51 k .. 51 k + 50, bit 255 unused); the trail
#   number names its slot: trail number t = w | (51 k) << SB is slot k of word w (trails are numbered in the order w = 0, 1,
#   ..., S - 1 with k = 0, then k = 1, ...).  A written slot is 1 | (bits 0..KEYB-1 of the trail's end) << 1, KEYB = 50; an
#   unwritten slot is zero.  The trail number is not stored.  A DP compares its record with every slot of all S words (one
#   XOR with the record repeated in the five slots, then a shift, mask and zero test per slot); with no equal slot, it writes
#   the record into the slot of its own trail.
# Distinguished point (DP): the point x (256-bit value, bit j = plane j) is a DP when x < THR, THR = DT << (DPLO - DK):
#   the planes DPLO..255 are zero and the DK planes below them, read as a number, are less than DT.  theta = DT 2^-(256-DPLO+DK).
#   No trail is cut: a walk runs until its DP; the replay refuses trails of more than LRC evaluations.
# Walk words: WK[l] = LST[l] | LID[l] << 128 (the first step of the trail of walk l and its trail number), one word per walk.
# Replay: the stored trail a is walked to its DP keeping a_i in table word i / G when G divides i (G = ceil(LRC / (S - 1)),
#   the table is not needed after a match); the new trail b is walked once, aligned (a_i with b_(i - la + lb)), and compared
#   with the checkpoints; the lock step runs only through the segment where the two trails merge.
#
# Machine (collision-frontier-v5 256-bit word RAM, the declared register file of RB0 + 11 registers R0..R(RB0+10), RB0 = the registers the straight line names):
#   every instruction below costs one word operation, except PERM, which costs one unit (UNIT = 271 NR operations, the model's
#   rule: one selected-round sponge permutation is one unit).  Straight-line instructions (two-address encoding, 14, 25 or 36
#   bits, packed: XOR AND OR NOT on registers) cost one operation each.  Other instructions are 8-byte words: op(5) L(1) d(11)
#   a(11) b(11) imm(25); L = 1: the immediate is literal number imm of the literal pool (32-byte words after the code).
#   Words are 256 bits, arithmetic is mod 2^256, shifts take amount R[b] & 255 (or an immediate), compares give 0 or 1,
#   a conditional branch tests a register for zero and is always the instruction right after the compare that set it
#   (audited below), memory M[] is word addressed with address R[a] + imm, PERM a applies Keccak-f rounds 0..NR-1 to the
#   25 lanes in R[a]..R[a+6] (lane l = bits 64 (l mod 4) .. +63 of word R[a + l div 4]).
#   The straight-line block sits in code memory in front of instruction SLPOS: it is entered by fall-through or by a
#   jump to it, has no branches, and control leaves it by fall-through into instruction SLPOS.
import sys, struct, hashlib, os, json

M256 = (1 << 256) - 1
M64 = (1 << 64) - 1
PARAMS = json.load(open(os.environ.get('LS1_PARAMS', 'params.json')))
NR = PARAMS['NR']                                  # rounds of the target
UNIT = 271 * NR                                    # the cost model's price of one NR-round permutation (word operations)
RB, RPW = 51, 5                                    # slot width; slots per word (255 of the 256 bits)
RM = (1 << RB) - 1


def keyb(Pm): return RB - 1                        # key bits of a slot: 1 + KEYB = 51


def tnum(i, Pm): return (i % Pm['S']) | (RB * (i // Pm['S'])) << Pm['SB']   # the number of the i-th trail (i = 0, 1, ...)


def thr(Pm): return Pm['DT'] << (Pm['DPLO'] - Pm['DK'])    # the DP is x < THR (DK = 0: DT = 1)

# ---- ISA ----
XOR, AND, OR, NOT, ADD, SUB, SHL, SHR, EQ, LT, MOV = range(11)
ADDI, SUBI, SHLI, SHRI, ANDI, EQI, LTI, MOVI = range(11, 19)
LD, ST, LDA, BNZ, BZ, JMP, JAL, JR, RND, PERM, HALT = range(19, 30)
NAMES = 'XOR AND OR NOT ADD SUB SHL SHR EQ LT MOV ADDI SUBI SHLI SHRI ANDI EQI LTI MOVI LD ST LDA BNZ BZ JMP JAL JR RND PERM HALT'.split()
CMPOPS = (EQ, LT, EQI, LTI)

# ---- registers ----
DESIGNX = True   # design X message embedding (credited derivative of mpjunior92 11565cb4): evalF and m_of build its state
RB0 = 2025   # the registers the straight line names (generator ledger: registers used)
C, NXT, IDN, RHO, ONES, PF, H, LR, LR2, ZERO = range(RB0, RB0 + 10)   # state (RB0..RB0+9; RB0+10 spare)
(L, DPM, C1, ACC, TT, REC, SLOT, TR, F, X, Y, LV, NP, NM, ONEB, V, MN, E, PTR, SS, ID, STV) = range(256, 278)
NXC, IA = 278, 279                                                    # replay: next checkpoint (measuring walk); a-index of P
(P, Q, N, MM, LA, LB, UU, FF, PDR, X0, X1, X2, X3, TQ, FP) = range(280, 295)
NX, PT2, QW = 297, 298, 299                                           # replay: next checkpoint a-index, its table word, b's walk
Z = 295
LSTB = 128                                                            # walk word: LST in bits 0..127, LID in bits 128..255
M128 = (1 << LSTB) - 1


def gap(Pm):
    """the checkpoint gap of the replay: G = ceil(LRC / (S - 1)), so a trail of at most LRC evaluations has at most S checkpoints"""
    return -(-Pm['LRC'] // (Pm['S'] - 1))
REP = 296                                                             # the DP record repeated in the five slots
W0 = 300                                                              # W0..W6, the 1600-bit state of evalF
NREGS = RB0 + 11


class Asm:
    def __init__(s):
        s.ins = []; s.lab = {}; s.fix = []

    def pc(s): return len(s.ins)

    def label(s, n):
        assert n not in s.lab, n
        s.lab[n] = len(s.ins)

    def e(s, op, d=0, a=0, b=0, imm=0, tgt=None):
        s.ins.append([op, d, a, b, imm])
        if tgt is not None: s.fix.append((len(s.ins) - 1, tgt))

    def resolve(s):
        for i, t in s.fix: s.ins[i][4] = s.lab[t]
        for x in s.ins: assert 0 <= x[4] < 1 << 192 and max(x[1:4]) < NREGS

    # plain instructions
    def xor(s, d, a, b): s.e(XOR, d, a, b)
    def and_(s, d, a, b): s.e(AND, d, a, b)
    def or_(s, d, a, b): s.e(OR, d, a, b)
    def not_(s, d, a): s.e(NOT, d, a)
    def add(s, d, a, b): s.e(ADD, d, a, b)
    def sub(s, d, a, b): s.e(SUB, d, a, b)
    def shl(s, d, a, b): s.e(SHL, d, a, b)
    def shr(s, d, a, b): s.e(SHR, d, a, b)
    def mov(s, d, a): s.e(MOV, d, a)
    def addi(s, d, a, i): s.e(ADDI, d, a, 0, i)
    def subi(s, d, a, i): s.e(SUBI, d, a, 0, i)
    def shli(s, d, a, i): s.e(SHLI, d, a, 0, i)
    def shri(s, d, a, i): s.e(SHRI, d, a, 0, i)
    def andi(s, d, a, i): s.e(ANDI, d, a, 0, i)
    def movi(s, d, i): s.e(MOVI, d, 0, 0, i)
    def ld(s, d, a, i): s.e(LD, d, a, 0, i)
    def st(s, a, i, b): s.e(ST, 0, a, b, i)
    def lda(s, d, i): s.e(LDA, d, 0, 0, i)
    def rnd(s, d): s.e(RND, d)
    def permute(s, a): s.e(PERM, 0, a)
    def halt(s, code): s.e(HALT, 0, 0, 0, code)
    def jmp(s, t): s.e(JMP, tgt=t)
    def jal(s, d, t): s.e(JAL, d, tgt=t)
    def jr(s, a): s.e(JR, 0, a)

    # compare + branch pairs (a branch is always right after its compare)
    def _br(s, brop, t): s.e(brop, 0, F, 0, 0, t)
    def jeq(s, a, b, t): s.e(EQ, F, a, b); s._br(BNZ, t)
    def jne(s, a, b, t): s.e(EQ, F, a, b); s._br(BZ, t)
    def jeqi(s, a, i, t): s.e(EQI, F, a, 0, i); s._br(BNZ, t)
    def jnei(s, a, i, t): s.e(EQI, F, a, 0, i); s._br(BZ, t)
    def jlt(s, a, b, t): s.e(LT, F, a, b); s._br(BNZ, t)
    def jge(s, a, b, t): s.e(LT, F, a, b); s._br(BZ, t)
    def jlti(s, a, i, t): s.e(LTI, F, a, 0, i); s._br(BNZ, t)
    def jgei(s, a, i, t): s.e(LTI, F, a, 0, i); s._br(BZ, t)


def build_state(A, MISC):
    if DESIGNX: return build_state_dx(A, MISC)
    return build_state_ls1(A, MISC)


def build_state_dx(A, MISC):
    """design X (11565cb4): W0..W6 := the state of m(u): lanes x and 10+x = v_x ^ K, v_0..v_3 = u_0..u_3,
    v_4 = XOR_(x<4) rotr(u_x, (39 - ROT[x][2]) mod 64) (43 instructions)."""
    V4, T1 = 307, 308
    for i in range(7): A.lda(W0 + i, MISC + i)
    A.xor(W0, W0, UU)                                        # lanes 0..3 = u0..u3
    A.andi(X0, UU, M64); A.shri(X1, UU, 64); A.andi(X1, X1, M64); A.shri(X2, UU, 128); A.andi(X2, X2, M64); A.shri(X3, UU, 192)
    for k, (Xk, sh) in enumerate(((X0, 36), (X1, 29), (X2, 60), (X3, 14))):
        if k == 0: A.shri(V4, Xk, sh)
        else: A.shri(T1, Xk, sh); A.xor(V4, V4, T1)
        A.shli(T1, Xk, 64 - sh); A.andi(T1, T1, M64); A.xor(V4, V4, T1)
    A.xor(W0 + 1, W0 + 1, V4)                                # lane 4  = v4
    A.shli(T1, X0, 128); A.xor(W0 + 2, W0 + 2, T1)           # lane 10 = u0
    A.shli(T1, X1, 192); A.xor(W0 + 2, W0 + 2, T1)           # lane 11 = u1
    A.xor(W0 + 3, W0 + 3, X2)                                # lane 12 = u2
    A.shli(T1, X3, 64); A.xor(W0 + 3, W0 + 3, T1)            # lane 13 = u3
    A.shli(T1, V4, 128); A.xor(W0 + 3, W0 + 3, T1)           # lane 14 = v4


def build_state_ls1(A, MISC):
    """W0..W6 := the 1600-bit state of the one-block message m(u), u in UU (26 instructions)."""
    for i in range(7): A.lda(W0 + i, MISC + i)
    A.andi(X0, UU, M64); A.shri(X1, UU, 64); A.andi(X1, X1, M64); A.shri(X2, UU, 128); A.andi(X2, X2, M64); A.shri(X3, UU, 192)
    A.shli(TQ, X0, 64); A.xor(W0, W0, TQ)                    # lane 1  = u0
    A.shli(TQ, X1, 128); A.xor(W0 + 1, W0 + 1, TQ)           # lane 6  = u1
    A.xor(W0 + 1, W0 + 1, X2)                                # lane 4  = u2
    A.shli(TQ, X3, 64); A.xor(W0 + 2, W0 + 2, TQ)            # lane 9  = u3
    A.xor(TQ, X0, X1); A.shli(TQ, TQ, 192); A.xor(W0 + 2, W0 + 2, TQ)   # lane 11 = u0 ^ u1 ^ K11
    A.xor(TQ, X2, X3); A.shli(TQ, TQ, 128); A.xor(W0 + 3, W0 + 3, TQ)   # lane 14 = u2 ^ u3 ^ K14


def program(Pm):
    """Pm: S (table words), U (trail limit), SB (bits of a word index, S < 2^SB), LRC (replay cap), Tb, HMAX, DPLO, DK, DT,
    PFLO, PFN, WTEST (None or width)."""
    S, U, SB, LRC, Tb, HMAX = Pm['S'], Pm['U'], Pm['SB'], Pm['LRC'], Pm['Tb'], Pm['HMAX']
    DPLO, DK, DT, PFLO, PFN, WT = Pm['DPLO'], Pm['DK'], Pm['DT'], Pm['PFLO'], Pm['PFN'], Pm.get('WTEST')
    KEYB = keyb(Pm); THR = thr(Pm)
    assert S < 1 << SB and S >= 264 and S % 8 == 0 and PFLO > DPLO + 1 and U <= RPW * S and (WT or DPLO - DK > KEYB)
    ULIM = tnum(U, Pm)                                       # the number the U-th restart would give: the trail limit
    assert (DK == 0 and DT == 1) or (DK >= 1 and 0 < DT < 1 << DK and DPLO >= DK)
    WK, MISC = S, S + 256                                    # WK[l]: the walk word of walk l, LST | LID << 128
    OUT = MISC + 8
    G = gap(Pm)
    assert Tb < 1 << LSTB and ULIM < 1 << (256 - LSTB) and (S - 1) * G >= LRC
    A = Asm()
    # ---------------- setup ----------------
    A.label('start')
    A.rnd(RHO); A.movi(IDN, 256); A.movi(H, 0); A.movi(C, 0); A.movi(ZERO, 0); A.not_(ONES, ZERO)
    A.movi(PTR, 0)
    A.label('clr')                                           # TAB := 0, eight words per pass
    for k in range(8): A.st(PTR, k, ZERO)
    A.addi(PTR, PTR, 8); A.jlti(PTR, S, 'clr')
    A.movi(L, 0)
    A.label('iw')                                            # for l < 256: WK[l] := l << 128 (LID l, LST 0); lane l := rho + l
    A.add(NP, RHO, L); A.shli(TT, L, LSTB); A.st(L, WK, TT); A.jal(LR, 'setwalk')
    A.addi(L, L, 1); A.jlti(L, 256, 'iw')
    # ---------------- the loop: the straight line (SLPOS) then the tests ----------------
    A.label('loop')
    A.jeq(PF, ONES, 'cont')                                  # prefilter test (2)
    # ---------------- hit: some walk has planes PFLO..PFLO+PFN-1 zero ----------------
    A.label('hit')
    A.addi(H, H, 1); A.jlti(H, HMAX + 1, 'h1'); A.halt(10); A.label('h1')      # hit counter and abort (F5)
    A.or_(SS, DPLO, DPLO + 1)
    for j in range(DPLO + 2, PFLO): A.or_(SS, SS, j)         # OR of the planes DPLO..PFLO-1
    A.or_(DPM, PF, SS); A.not_(DPM, DPM)                     # DPM: walks with planes DPLO..255 zero
    if DK:                                                   # keep the walks whose planes DPLO-1 .. DPLO-DK, as a number, are < DT
        bits = [(DT >> (DK - 1 - i)) & 1 for i in range(DK)]  # most significant first: plane DPLO - 1 - i
        last1 = max(i for i in range(DK) if bits[i]); first = True
        for i in range(last1 + 1):
            p = DPLO - 1 - i
            A.not_(X, p)
            if bits[i]:
                if first: A.and_(Y, DPM, X); first = False   # lt := eq and not p
                else: A.and_(X, DPM, X); A.or_(Y, Y, X)      # lt := lt or (eq and not p)
                if i < last1: A.and_(DPM, DPM, p)            # eq := eq and p
            else: A.and_(DPM, DPM, X)                        # eq := eq and not p
        A.mov(DPM, Y)                                        # DPM := lt
    A.addi(C1, C, 1)                                         # steps completed including this one
    A.label('dpl')
    A.jeqi(DPM, 0, 'cont')
    A.label('dp1')                                           # ---- one DP walk: l := lowest set bit of DPM ----
    A.movi(L, 0); A.mov(X, DPM)
    for i, sh in enumerate((128, 64, 32, 16, 8, 4, 2, 1)):
        A.andi(Y, X, (1 << sh) - 1); A.jnei(Y, 0, 'ct%d' % i); A.shri(X, X, sh); A.addi(L, L, sh); A.label('ct%d' % i)
    A.subi(Y, DPM, 1); A.and_(DPM, DPM, Y)                   # clear that bit
    A.label('gather')                                        # ACC := end bits 0..KEYB-1 of walk l (bit j = plane j, bit l); the record reads only these
    A.shr(ACC, 0, L); A.andi(ACC, ACC, 1)
    for j in range(1, KEYB):
        A.shr(TT, j, L); A.andi(TT, TT, 1); A.shli(TT, TT, j); A.or_(ACC, ACC, TT)
    A.label('record')                                        # REC := 1 | (end bits 0..KEYB-1) << 1; REP := REC in each of the five slots
    A.andi(REC, ACC, (1 << KEYB) - 1); A.shli(REC, REC, 1); A.addi(REC, REC, 1)
    A.mov(REP, REC)
    for k in range(1, RPW): A.shli(X, REC, RB * k); A.or_(REP, REP, X)
    A.movi(SLOT, 0); A.label('sl_ok')
    A.label('probe')                                         # one table word: XOR with REP, then each slot tested for zero
    A.ld(TR, SLOT, 0); A.xor(TR, TR, REP)
    for k in range(RPW):
        if k: A.shri(Y, TR, RB * k); A.andi(X, Y, RM)
        else: A.andi(X, TR, RM)
        A.jeqi(X, 0, 'match%d' % k)                          # slot k equals the record (an unwritten slot never does: REC has bit 0 set)
    A.label('pnext')
    A.addi(SLOT, SLOT, 1); A.jnei(SLOT, S, 'probe')
    A.label('insert')                                        # no slot equals the record: write it into the slot of trail LID[l]
    A.ld(ID, L, WK); A.shri(ID, ID, LSTB); A.andi(SLOT, ID, (1 << SB) - 1); A.shri(Y, ID, SB); A.shl(X, REC, Y)
    A.ld(TR, SLOT, 0); A.or_(TR, TR, X); A.st(SLOT, 0, TR)
    A.label('ins')
    A.mov(LV, C1); A.jal(LR, 'restart'); A.jmp('dpl')
    for k in range(RPW):                                     # slot k of word SLOT holds the same KEYB end bits: X := its trail number
        A.label('match%d' % k)
        A.movi(X, (RB * k) << SB); A.or_(X, X, SLOT); A.jmp('match')
    # ---------------- end of iteration ----------------
    A.label('cont')
    A.addi(C, C, 1); A.jnei(C, Tb, 'loop')                   # counter (3 with the compare and branch)
    A.label('dl')
    A.halt(12)                                               # c = Tb: the attempt failed
    # ---------------- restart(l) and the insertion of a point into lane l ----------------
    A.label('restart')                                       # in: L, LV; link LR
    A.jnei(IDN, ULIM, 'rs1'); A.halt(11); A.label('rs1')
    A.shli(X, IDN, LSTB); A.or_(X, X, LV); A.st(L, WK, X); A.add(NP, RHO, IDN); A.addi(IDN, IDN, 1)   # WK[l] := LV | idn << 128
    A.andi(X, IDN, (1 << SB) - 1); A.jnei(X, S, 'rs2'); A.addi(IDN, IDN, (RB << SB) - S); A.label('rs2')   # past word S - 1: slot k + 1 of word 0
    A.label('setwalk')                                       # in: L, NP; link LR
    A.movi(ONEB, 1); A.shl(ONEB, ONEB, L); A.not_(NM, ONEB)
    A.label('sw_planes')
    for j in range(256):
        A.and_(X, j, NM)
        if j: A.shri(Y, NP, j); A.andi(Y, Y, 1)
        else: A.andi(Y, NP, 1)
        A.shl(Y, Y, L); A.or_(j, X, Y)
    A.label('sw_end')
    A.jr(LR)
    # ---------------- the evaluation of F on one point with the permutation ----------------
    A.label('evalF')                                         # in: UU; out: FF; link LR2
    build_state(A, MISC)
    A.label('ef_perm')
    A.permute(W0); A.lda(PDR, MISC + 7); A.xor(FF, W0, PDR)
    if WT: A.andi(FF, FF, (1 << WT) - 1)                     # test builds only: F truncated to the low WT bits
    A.jr(LR2)
    A.label('outm')                                          # in: UU; out: W0..W3 = the 128-byte message m(UU); link LR2
    build_state(A, MISC)
    A.jr(LR2)
    # ---------------- replay ----------------
    A.label('match')                                         # in: X (stored trail a), L (walk of trail b), C1
    A.ld(LB, L, WK); A.shri(Y, LB, LSTB); A.andi(LB, LB, M128); A.sub(LB, C1, LB)   # trail b: its number and its length lb = c1 - LST[l]
    A.jgei(LB, LRC + 1, 'rfail')                             # lb > LRC: the replay refuses it
    A.add(P, RHO, X); A.add(Q, RHO, Y)
    A.mov(UU, P); A.movi(LA, 0); A.movi(PTR, 0); A.movi(NXC, 0)
    A.label('meas')                                          # la := evaluations of trail a from its start to its first DP;
    A.jne(LA, NXC, 'ms1')                                    #   the point a_i (i = LA) is kept as checkpoint i / G in the
    A.st(PTR, 0, UU); A.addi(PTR, PTR, 1); A.addi(NXC, NXC, G)   #   table (its words are no longer needed) when G divides i
    A.label('ms1')
    A.jal(LR2, 'evalF'); A.addi(LA, LA, 1); A.jlti(FF, THR, 'measd')       # the image is a DP when FF < THR
    A.jgei(LA, LRC, 'rfail'); A.mov(UU, FF); A.jmp('meas')
    A.label('measd')                                         # aligned pairs (a_i, b_(i-d)), d = la - lb
    A.jlt(LA, LB, 'bl')
    A.sub(N, LA, LB); A.movi(IA, 0); A.movi(PT2, 0)          # d >= 0: the last checkpoint at or below d
    A.label('al1')
    A.addi(TQ, IA, G); A.jlt(N, TQ, 'al2'); A.mov(IA, TQ); A.addi(PT2, PT2, 1); A.jmp('al1')
    A.label('al2')
    A.ld(P, PT2, 0); A.addi(PT2, PT2, 1); A.addi(NX, IA, G); A.sub(N, N, IA)   # P := a_IA; then d - IA evaluations to a_d
    A.label('al3')
    A.jeqi(N, 0, 'al4'); A.mov(UU, P); A.jal(LR2, 'evalF'); A.mov(P, FF); A.subi(N, N, 1); A.jmp('al3')
    A.label('al4')
    A.sub(IA, LA, LB); A.jmp('walk0')                        # P = a_d, Q = b_0
    A.label('bl')                                            # d < 0: Q := b_(lb - la), P = a_0
    A.sub(N, LB, LA); A.movi(IA, 0); A.movi(NX, G); A.movi(PT2, 1)
    A.label('bl1')
    A.jeqi(N, 0, 'walk0'); A.mov(UU, Q); A.jal(LR2, 'evalF'); A.mov(Q, FF); A.subi(N, N, 1); A.jmp('bl1')
    A.label('walk0')
    A.jeq(P, Q, 'rfail')                                     # the start of one trail lies on the other: no pair
    A.label('seg')                                           # P = a_IA, Q = b_(IA-d), P != Q; NX = IA rounded up to the next checkpoint
    A.jge(NX, LA, 'last')
    A.sub(MM, NX, IA); A.mov(N, MM); A.mov(QW, Q)
    A.label('sw')                                            # QW := b_(NX-d)
    A.mov(UU, QW); A.jal(LR2, 'evalF'); A.mov(QW, FF); A.subi(N, N, 1); A.jnei(N, 0, 'sw')
    A.ld(TQ, PT2, 0); A.jeq(TQ, QW, 'lloop')                 # equal at the checkpoint: the trails merge in this segment
    A.mov(P, TQ); A.mov(Q, QW); A.mov(IA, NX); A.addi(NX, NX, G); A.addi(PT2, PT2, 1); A.jmp('seg')
    A.label('last')                                          # no checkpoint before the DP: lock step to the end
    A.sub(MM, LA, IA)
    A.label('lloop')
    A.jeqi(MM, 0, 'rfail')
    A.mov(UU, P); A.jal(LR2, 'evalF'); A.mov(FP, FF); A.mov(UU, Q); A.jal(LR2, 'evalF')
    A.jeq(FP, FF, 'found')
    A.mov(P, FP); A.mov(Q, FF); A.subi(MM, MM, 1); A.jmp('lloop')
    A.label('found')                                         # output m(p), m(q): words W0..W3 of the built states
    A.mov(UU, P); A.jal(LR2, 'outm')
    for i in range(4): A.st(ZERO, OUT + i, W0 + i)
    A.mov(UU, Q); A.jal(LR2, 'outm')
    for i in range(4): A.st(ZERO, OUT + 4 + i, W0 + i)
    A.halt(1)
    A.label('rfail')
    A.halt(13)
    A.label('end')
    A.resolve()
    return A


def audit(A):
    """every conditional branch follows the compare that sets its register; every label inside range"""
    for i, x in enumerate(A.ins):
        if x[0] in (BNZ, BZ):
            p = A.ins[i - 1]
            assert p[0] in CMPOPS and p[1] == x[2], ('branch without compare', i)
            assert x[4] < len(A.ins)
        if x[0] in (JMP, JAL): assert x[4] < len(A.ins)


# ---------------- encoding ----------------
def enc_all(ins):
    """other.bin: one 8-byte word per instruction (bits 0-4 op, bit 5 L, 6-16 d, 17-27 a, 28-38 b, 39-63 imm), then the literal
    pool: the distinct immediates of 2^25 or more, 32 bytes each, in order of first use; an instruction with L = 1 has its
    immediate in literal number imm."""
    lits, words = [], []
    for op, d, a, b, imm in ins:
        assert 0 <= op < 32 and max(d, a, b) < 2048 and 0 <= imm < 1 << 256
        if imm < 1 << 25: L, f = 0, imm
        else:
            if imm not in lits: lits.append(imm)
            L, f = 1, lits.index(imm)
        words.append(op | L << 5 | d << 6 | a << 17 | b << 28 | f << 39)
    return b''.join(w.to_bytes(8, 'little') for w in words) + b''.join(v.to_bytes(32, 'little') for v in lits)


def dec_all(bs, n):
    """the n instructions of other.bin (enc_all)"""
    assert len(bs) >= 8 * n and (len(bs) - 8 * n) % 32 == 0
    out = []
    for i in range(n):
        w = int.from_bytes(bs[8 * i:8 * i + 8], 'little')
        op, L, d, a, b, f = w & 31, (w >> 5) & 1, (w >> 6) & 2047, (w >> 17) & 2047, (w >> 28) & 2047, w >> 39
        imm = int.from_bytes(bs[8 * n + 32 * f:8 * n + 32 * f + 32], 'little') if L else f
        out.append((op, d, a, b, imm))
    return out


def read_ninstr(path='meta.txt'):
    for line in open(path):
        t = line.split()
        if t and t[0] == 'ninstr': return int(t[1])
    raise Exception('ninstr missing')


def ta_word(code, d, a, b):
    """one straight-line instruction in the two-address encoding: (word, bits).  Bits 0-1 op (0 XOR, 1 AND, 2 OR, 3 NOT),
    bit 2 t; t = 1: the destination is operand a, then a and (XOR/AND/OR) b; t = 0: d, a and (XOR/AND/OR) b; registers 11 bits.
    A binary instruction whose destination is its second operand is written with the operands swapped (XOR, AND, OR commute)."""
    assert max(d, a, b) < 2048 and 0 <= code <= 3
    if code == 3:
        return (3 | 4 | a << 3, 14) if d == a else (3 | d << 3 | a << 14, 25)
    if d == b and d != a: a, b = b, a
    return (code | 4 | a << 3 | b << 14, 25) if d == a else (code | d << 3 | a << 14 | b << 25, 36)


def pack_ta(instrs):
    """(code, d, a, b) instructions -> the packed bytes (little-endian bit stream), the last byte padded with zero bits"""
    out = bytearray(); acc = nb = 0
    for x in instrs:
        w, k = ta_word(*x)
        acc |= w << nb; nb += k
        while nb >= 8: out.append(acc & 255); acc >>= 8; nb -= 8
    if nb: out.append(acc)
    return bytes(out)


def unpack_ta(bs, n=None):
    """the instructions (code, d, a, b) of a packed block: n of them, or (n None) as many as the block holds (padding < 8 bits)"""
    out, pos = dec_ta(bs, n)
    assert (pos + 7) // 8 == len(bs), ('block length', pos, len(bs))
    return out


def dec_ta(bs, n=None):
    """decodes n instructions (or all) from the start of bs: (instructions, bits used)"""
    v = int.from_bytes(bs, 'little'); pos = 0; out = []; tot = 8 * len(bs)
    g = lambda p, k: (v >> p) & ((1 << k) - 1)
    while (len(out) < n) if n is not None else (pos + 14 <= tot):
        op, t = g(pos, 2), g(pos + 2, 1); pos += 3
        if t: a = g(pos, 11); d = a; pos += 11
        else: d, a = g(pos, 11), g(pos + 11, 11); pos += 22
        b = 0
        if op != 3: b = g(pos, 11); pos += 11
        out.append((op, d, a, b))
    return out, pos


def sl_bytes(prog, PFLO, PFN):
    """the straight-line block: prog.bin, then the prefilter PF := OR of planes PFLO..PFLO+PFN-1 (PFN-1 ORs, pf.bin), each a
    packed two-address block padded to whole bytes"""
    pf = [(2, PF, PFLO, PFLO + 1)] + [(2, PF, PF, j) for j in range(PFLO + 2, PFLO + PFN)]
    return bytes(prog) + pack_ta(pf)


# ---------------- Keccak ----------------
RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808a, 0x8000000080008000, 0x000000000000808b, 0x0000000080000001,
      0x8000000080008081, 0x8000000000008009, 0x000000000000008a, 0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
      0x000000008000808b, 0x800000000000008b, 0x8000000000008089, 0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
      0x000000000000800a, 0x800000008000000a, 0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
ROTC = [0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43, 25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14]


def rotl(v, r): return ((v << r) | (v >> (64 - r))) & M64 if r else v


def keccak_f(A, rounds):
    A = list(A)
    for r in range(rounds):
        Cc = [A[x] ^ A[x + 5] ^ A[x + 10] ^ A[x + 15] ^ A[x + 20] for x in range(5)]
        D = [Cc[(x + 4) % 5] ^ rotl(Cc[(x + 1) % 5], 1) for x in range(5)]
        A = [A[i] ^ D[i % 5] for i in range(25)]
        B = [0] * 25
        for x in range(5):
            for y in range(5): B[y + 5 * ((2 * x + 3 * y) % 5)] = rotl(A[x + 5 * y], ROTC[x + 5 * y])
        A = [B[x + 5 * y] ^ ((~B[(x + 1) % 5 + 5 * y] & M64) & B[(x + 2) % 5 + 5 * y]) for y in range(5) for x in range(5)]
        A[0] ^= RC[r]
    return A


def sha3_256_r(msg, rounds):
    A = [0] * 25
    off = 0
    while True:
        rem = len(msg) - off
        if rem >= 136: blk = msg[off:off + 136]; off += 136
        else:
            blk = bytearray(msg[off:] + bytes(136 - rem)); blk[rem] ^= 6; blk[135] ^= 0x80; off = len(msg) + 1
        for i in range(17): A[i] ^= int.from_bytes(blk[8 * i:8 * i + 8], 'little')
        A = keccak_f(A, rounds)
        if off > len(msg): break
    return b''.join(A[i].to_bytes(8, 'little') for i in range(4))


# ---------------- constants of the target from meta.txt ----------------
def read_meta(path):
    KL = [0] * 25; PD = [0] * 4
    for line in open(path):
        t = line.split()
        if t and t[0] == 'lane': KL[int(t[1])] = int(t[2], 16)
        elif t and t[0] == 'pd': PD = [int(x, 16) for x in t[1:5]]
    return KL, PD


def data_image(KL, PD):
    """16 words: KW[0..6] (lane constants of the absorbed state, the lanes of u zero), PD, then 8 output words"""
    KW = []
    for w in range(7):
        v = 0
        for i in range(4):
            l = 4 * w + i
            if l < 25: v |= KL[l] << (64 * i)
        KW.append(v)
    pd = PD[0] | PD[1] << 64 | PD[2] << 128 | PD[3] << 192
    return KW + [pd] + [0] * 8


def m_of(u, KL):
    Ls = list(KL[:16])
    u0, u1, u2, u3 = [(u >> (64 * i)) & M64 for i in range(4)]
    if DESIGNX:   # design X (11565cb4): lanes x and 10+x = v_x ^ K, v_4 = XOR_(x<4) rotr(u_x, (39 - ROT[x][2]) mod 64)
        rr = lambda v, s: ((v >> s) | (v << (64 - s))) & M64 if s else v
        v = [u0, u1, u2, u3]; v.append(rr(u0, 36) ^ rr(u1, 29) ^ rr(u2, 60) ^ rr(u3, 14))
        for x in range(5): Ls[x] ^= v[x]; Ls[10 + x] ^= v[x]
        return b''.join(x.to_bytes(8, 'little') for x in Ls)
    Ls[1] = u0; Ls[6] = u1; Ls[11] = u0 ^ u1 ^ KL[11]; Ls[4] = u2; Ls[9] = u3; Ls[14] = u2 ^ u3 ^ KL[14]
    return b''.join(x.to_bytes(8, 'little') for x in Ls)


def F_plain(u, KL, PD, rounds=NR):
    d = sha3_256_r(m_of(u, KL), rounds)
    pd = PD[0] | PD[1] << 64 | PD[2] << 128 | PD[3] << 192
    return int.from_bytes(d, 'little') ^ pd


# ---------------- the machine ----------------
def compile_sl(slb, nprog, hookW=None):
    """Python function executing the straight-line block (prog.bin then pf.bin, two-address encoding) on a register list (the
    planes 0..255 and PF are the only live ends); nprog = instructions of prog.bin.
    hookW (test builds only): set the planes hookW..255 to zero after the first nprog instructions (the F of the program
    truncated to hookW bits, as in the organizer experiment rho-w22)."""
    src = ['def sl(R):']
    for j in range(256): src.append(' r%d=R[%d]' % (j, j))
    head, pos = dec_ta(slb, nprog); LP = (pos + 7) // 8
    for i, (op, d, a, b) in enumerate(head + unpack_ta(slb[LP:])):
        if i == nprog and hookW:
            for j in range(hookW, 256): src.append(' r%d=0' % j)
        if op == 0: src.append(' r%d=r%d^r%d' % (d, a, b))
        elif op == 1: src.append(' r%d=r%d&r%d' % (d, a, b))
        elif op == 2: src.append(' r%d=r%d|r%d' % (d, a, b))
        else: src.append(' r%d=r%d^%d' % (d, a, M256))
    for j in range(256): src.append(' R[%d]=r%d' % (j, j))
    src.append(' R[%d]=r%d' % (PF, PF))
    ns = {}
    exec(compile('\n'.join(src), 'sl', 'exec'), ns)
    return ns['sl']


class VM:
    def load(s, code, sl, nsl, slpos, memwords, data, MISC, rng):
        s.code = code; s.sl = sl; s.nsl = nsl; s.slpos = slpos
        s.R = [0] * NREGS; s.M = [0] * memwords
        for i, v in enumerate(data): s.M[MISC + i] = v
        s.rng = rng; s.units = 0; s.slsteps = 0; s.halt = None
        s.cnt = [0] * (len(code) + 1)
        return s

    def run(s, pc=0, stop=None):
        code, R, M, cnt = s.code, s.R, s.M, s.cnt
        sl, slpos = s.sl, s.slpos
        while True:
            if pc == slpos and sl is not None:
                sl(R); s.slsteps += 1
            if stop is not None and pc == stop: return pc
            op, d, a, b, imm = code[pc]
            cnt[pc] += 1
            pc += 1
            if op == XOR: R[d] = R[a] ^ R[b]
            elif op == AND: R[d] = R[a] & R[b]
            elif op == OR: R[d] = R[a] | R[b]
            elif op == NOT: R[d] = R[a] ^ M256
            elif op == ADD: R[d] = (R[a] + R[b]) & M256
            elif op == SUB: R[d] = (R[a] - R[b]) & M256
            elif op == SHL: R[d] = (R[a] << (R[b] & 255)) & M256
            elif op == SHR: R[d] = R[a] >> (R[b] & 255)
            elif op == EQ: R[d] = 1 if R[a] == R[b] else 0
            elif op == LT: R[d] = 1 if R[a] < R[b] else 0
            elif op == MOV: R[d] = R[a]
            elif op == ADDI: R[d] = (R[a] + imm) & M256
            elif op == SUBI: R[d] = (R[a] - imm) & M256
            elif op == SHLI: R[d] = (R[a] << imm) & M256
            elif op == SHRI: R[d] = R[a] >> imm
            elif op == ANDI: R[d] = R[a] & imm
            elif op == EQI: R[d] = 1 if R[a] == imm else 0
            elif op == LTI: R[d] = 1 if R[a] < imm else 0
            elif op == MOVI: R[d] = imm
            elif op == LD: R[d] = M[R[a] + imm]
            elif op == ST: M[R[a] + imm] = R[b]
            elif op == LDA: R[d] = M[imm]
            elif op == BNZ:
                if R[a]: pc = imm
            elif op == BZ:
                if not R[a]: pc = imm
            elif op == JMP: pc = imm
            elif op == JAL: R[d] = pc; pc = imm
            elif op == JR: pc = R[a]
            elif op == RND: R[d] = s.rng.getrandbits(256)
            elif op == PERM:
                lanes = []
                for w in range(7):
                    v = R[a + w]
                    for i in range(4): lanes.append((v >> (64 * i)) & M64)
                lanes = keccak_f(lanes[:25], NR)
                lanes += [0, 0, 0]
                for w in range(7): R[a + w] = sum(lanes[4 * w + i] << (64 * i) for i in range(4))
                s.units += 1
            elif op == HALT:
                s.halt = imm; return None
            else: raise Exception('bad op')


# ---------------- counting ----------------
FULL = {k: PARAMS[k] for k in ('S', 'U', 'SB', 'LRC', 'Tb', 'HMAX', 'DPLO', 'DK', 'DT', 'PFLO', 'PFN')}


def counts(A, Pm):
    """Worst-case operation counts of every routine, from the lengths of the emitted code (an instruction is one
    operation, PERM is UNIT).  seg(a, b) = number of instructions between two labels."""
    I = A.lab
    def seg(a, b): return I[b] - I[a]
    S, U, LRC = Pm['S'], Pm['U'], Pm['LRC']
    c = {}
    c['n_instr'] = len(A.ins)
    c['setwalk'] = seg('setwalk', 'sw_end') + 1                                  # with the return
    c['restart'] = (seg('restart', 'rs1') - 1) + seg('rs1', 'setwalk') + c['setwalk']   # the cap check passes (no HALT)
    c['restart_halt'] = seg('restart', 'rs1') - 1 + 1                           # the last call: compare, branch not taken, HALT
    c['hit'] = (seg('hit', 'h1') - 1) + seg('h1', 'dpl') + 2                     # per processed hit, no DP walk
    c['ctz_clear'] = seg('dp1', 'gather')
    c['gather'] = seg('gather', 'record')
    c['record_slot'] = seg('record', 'sl_ok')
    c['probe_word'] = seg('probe', 'insert')                                     # load, XOR, five slot tests without a match, next word
    c['insert'] = seg('insert', 'ins')
    c['dp_fixed'] = 2 + c['ctz_clear'] + c['gather'] + c['record_slot'] + c['insert'] + 3   # + move, call, jump back
    c['dp_max'] = c['dp_fixed'] + c['probe_word'] * S                            # every DP passes all S words (no match)
    c['dl_final'] = seg('dl', 'restart')                                         # c = Tb: the HALT (the compare and branch are in the iteration's 3)
    c['e_eval'] = seg('evalF', 'outm') - 1 + UNIT                                # one evaluation of F with the permutation, with the return
    c['e_outm'] = seg('outm', 'match')                                           # the message builder, with the return
    e = c['e_eval']
    c['match_entry'] = 3 + seg('match', 'meas')                                  # trail number from the record (3), entry (with the lb test 2)
    c['meas_iter'] = e + 10                                                      # one measuring evaluation without the DP
    c['meas_last'] = e + 6                                                       # the evaluation that lands on the DP
    c['ckpt'] = 3                                                                # storing a checkpoint
    c['adv_iter'] = e + 7                                                        # one alignment evaluation (al3, bl1)
    c['bwalk_iter'] = e + 6                                                      # one evaluation of trail b between checkpoints (sw)
    c['seg_iter'] = 2 + 3 + 3 + 6                                                # a segment without a merge, besides its evaluations
    c['replay_iter'] = 13 + 2 * e                                                # one lock-step iteration (not found)
    c['replay_gap'] = gap(Pm)
    c['replay_rate'] = c['meas_iter'] + c['adv_iter']
    c['replay_g'] = c['replay_iter'] + c['adv_iter']
    c['replay_nck'] = c['ckpt'] + c['seg_iter']
    # Worst case (proof.md Section 4.2), la, lb <= LRC, d = la - lb, nc = floor((la - 1) / G) + 1 checkpoints:
    #   (the alignment counts include the test d < 0)
    #   d >= 0: 15 + (la - 1)(e + 10) + (e + 6) + 3 nc + (16 + 6 K + r (e + 7)) + 2 + 14 ns + 8 + (b evaluations <= lb - 1)(e + 6)
    #           + (k - 1)(2e + 13) + (2e + 9) + 2 e_outm + 13, with K + ns <= nc - 1, r < G, k <= G
    #           <= (2e + 16) LRC + (3e + 20)(G - 1) + 17 nck + e + 2 e_outm + 39
    #   d < 0:  15 + la (e + 10) - 4 + 3 nc + 8 + (lb - la)(e + 7) + 2 + (la - 1)(e + 7) + 14 (nc - 1) + 8 + (G - 1)(2e + 13) + 2e + 2 e_outm + 22
    #           <= (2e + 17) LRC + (2e + 13)(G - 1) + 17 nck + e + 2 e_outm + 30
    #   (the exhausted lock step, m (2e + 13) + 3, and every refusal cost less)
    #   so replay <= (2e + 17) LRC + (3e + 20) G + 17 nck + e + 2 e_outm + 39, nck = floor((LRC - 1) / G) + 1 (e_outm: the message
    #   builder with its return, 44 instructions with the design X state; the success exit is two builds, 8 stores and the halt: 2 e_outm + 13).
    assert c['match_entry'] == 15
    c['replay_const'] = c['match_entry'] + 24 + 2 * c['e_outm'] + e
    G = c['replay_gap']; NCK = (LRC - 1) // G + 1
    c['replay_max'] = c['replay_rate'] * LRC + c['replay_g'] * G + c['replay_nck'] * NCK + c['replay_const']
    c['setup'] = seg('start', 'clr') + (S // 8) * 11 + 1 + 256 * (7 + c['setwalk'])
    return c


def pf_bytes(PFLO, PFN):
    return sl_bytes(b'', PFLO, PFN)


def build_cli(argv):
    if len(argv) > 1 and argv[1] == 'build':
        meta = argv[2] if len(argv) > 2 else 'meta.txt'
        KL, PD = read_meta(meta)
        A = program(FULL); audit(A)
        other = enc_all(A.ins)
        assert dec_all(other, len(A.ins)) == [tuple(x) for x in A.ins]
        open('other.bin', 'wb').write(other)
        open('pf.bin', 'wb').write(pf_bytes(FULL['PFLO'], FULL['PFN']))
        open('data.bin', 'wb').write(b''.join(w.to_bytes(32, 'little') for w in data_image(KL, PD)))
        c = counts(A, FULL)
        I = A.lab
        out = []
        NLIT = (len(other) - 8 * len(A.ins)) // 32
        out.append('other code: %d instructions x 8 bytes + %d literals x 32 bytes = %d bytes (other.bin sha256 %s)' % (len(A.ins), NLIT, len(other), hashlib.sha256(other).hexdigest()))
        NP = read_ninstr(meta); pfb = open('pf.bin', 'rb').read(); progb = open('prog.bin', 'rb').read()
        assert len(unpack_ta(progb, NP)) == NP and len(unpack_ta(pfb)) == FULL['PFN'] - 1
        out.append('prefilter: %d instructions, two-address encoding, %d bytes (pf.bin sha256 %s); the straight-line block = prog.bin (%d instructions, %d bytes) then pf.bin, %d instructions, sits in front of instruction %d (label loop)' %
                   (FULL['PFN'] - 1, len(pfb), hashlib.sha256(pfb).hexdigest(), NP, len(progb), NP + FULL['PFN'] - 1, I['loop']))
        out.append('data image: 16 words x 32 bytes = 512 bytes (data.bin sha256 %s): KW[0..6], PD, 8 output words' % hashlib.sha256(open('data.bin', 'rb').read()).hexdigest())
        out.append('memory map (words): TAB 0..%d, WK (walk words, LST | LID << 128) %d..%d, data %d..%d' % (FULL['S'] - 1, FULL['S'], FULL['S'] + 255, FULL['S'] + 256, FULL['S'] + 271))
        out.append('replay checkpoint gap G = ceil(LRC / (S - 1)) = %d, at most %d checkpoints' % (c['replay_gap'], (FULL['LRC'] - 1) // c['replay_gap'] + 1))
        out.append('routine entry points (instruction index): ' + ', '.join('%s %d' % (k, I[k]) for k in ('start', 'loop', 'hit', 'dpl', 'dp1', 'gather', 'record', 'probe', 'insert', 'ins', 'match0', 'cont', 'dl', 'restart', 'setwalk', 'evalF', 'outm', 'match', 'meas', 'measd', 'bl', 'walk0', 'seg', 'last', 'lloop', 'found', 'end')))
        for k, v in c.items(): out.append('%-18s %d' % (k, v))
        for k, v in (('other_bytes', len(other)), ('other_literals', NLIT), ('prog_bytes', len(progb)), ('pf_bytes', len(pfb)), ('sl_bytes', len(progb) + len(pfb))): out.append('%-18s %d' % (k, v))
        bybase = {}
        for x in A.ins: bybase[NAMES[x[0]]] = bybase.get(NAMES[x[0]], 0) + 1
        out.append('static opcode mix: ' + ' '.join('%s %d' % kv for kv in sorted(bybase.items(), key=lambda kv: -kv[1])))
        out.append('highest register named: %d (file of %d)' % (max(max(x[1], x[2], x[3]) for x in A.ins), NREGS))
        open('counts.txt', 'w').write(chr(10).join(out) + chr(10))
        print(chr(10).join(out))
    else:
        print(__doc__ if __doc__ else 'usage: other3.py build [meta.txt]')


if __name__ == '__main__':
    build_cli(sys.argv)
```

### D.2 Output of `python3 other4.py build meta.txt`

```
other code: 1955 instructions x 8 bytes + 11 literals x 32 bytes = 15992 bytes (other.bin sha256 5d294e3f513f97796c250be21663b4d57bf86afce9868609e0da85ba9add949a)
prefilter: 15 instructions, two-address encoding, 49 bytes (pf.bin sha256 8b0405c9870c5de287d7797b355ee12b97ecc07eeaf96ba8caed3e8d9b16ae93); the straight-line block = prog.bin (136662 instructions, 464959 bytes) then pf.bin, 136677 instructions, sits in front of instruction 26 (label loop)
data image: 16 words x 32 bytes = 512 bytes (data.bin sha256 2c3ebe318ee06cb0d87e50a077b1969c83fedad8eac0deff38a49bce593c8da8): KW[0..6], PD, 8 output words
memory map (words): TAB 0..15423, WK (walk words, LST | LID << 128) 15424..15679, data 15680..15695
replay checkpoint gap G = ceil(LRC / (S - 1)) = 3172907342664232231127405964387, at most 15423 checkpoints
routine entry points (instruction index): start 0, loop 26, hit 28, dpl 148, dp1 150, gather 194, record 392, probe 405, insert 429, ins 437, match0 440, cont 455, dl 458, restart 459, setwalk 471, evalF 1754, outm 1801, match 1845, meas 1857, measd 1870, bl 1894, walk0 1905, seg 1907, last 1927, lloop 1928, found 1941, end 1955
n_instr            1955
setwalk            1283
restart            1294
restart_halt       3
hit                121
ctz_clear          44
gather             198
record_slot        13
probe_word         24
insert             8
dp_fixed           268
dp_max             370444
dl_final           1
e_eval             6279
e_outm             44
match_entry        15
meas_iter          6289
meas_last          6285
ckpt               3
adv_iter           6286
bwalk_iter         6285
seg_iter           14
replay_iter        12571
replay_gap         3172907342664232231127405964387
replay_rate        12575
replay_g           18857
replay_nck         17
replay_const       6406
replay_max         615426887083584574713207995517580845456
setup              351456
other_bytes        15992
other_literals     11
prog_bytes         464959
pf_bytes           49
sl_bytes           465008
static opcode mix: OR 413 ANDI 337 SHRI 284 AND 266 SHL 258 SHLI 72 SHR 50 XOR 30 ADDI 26 MOV 25 MOVI 22 EQI 22 ST 20 BNZ 19 BZ 17 LDA 15 JMP 13 NOT 10 JAL 10 SUB 7 LTI 6 LD 6 EQ 5 HALT 5 SUBI 5 ADD 4 JR 3 LT 3 RND 1 PERM 1
highest register named: 2034 (file of 2036)
```

### D.3 other4_test.py

```python
#!/usr/bin/env python3
# other4_test.py - checks of the emitted program of other4.py.
#   1. routine tests: each routine run on constructed states; its executed operations must equal the counted worst case
#   2. end-to-end runs of the whole emitted program (setup, loop, hit handler, DP handler, restart, deadlines, replay,
#      output) at reduced width: the straight line of prog.bin is truncated to W bits after every step (test hook), the
#      replay's F is truncated alike (one extra ANDI in evalF, test builds only); the output pair is checked with an
#      independent Keccak.  The totals of every run are compared with the counted bounds.
#   usage: other4_test.py [nseeds] [pyseed]   (params.json, meta.txt and prog.bin of the row in the working directory)
import random, sys, time
from other4 import *

KL, PD = read_meta('meta.txt')
prog = open('prog.bin', 'rb').read(); NPROG = read_ninstr('meta.txt')
data = data_image(KL, PD)
FAILS = []; NCHK = [0]


def check(cond, msg):
    NCHK[0] += 1
    if not cond:
        FAILS.append(msg); print('FAIL', msg)


def mk(Pm, seed=1, with_sl=False):
    A = program(Pm); audit(A)
    code = dec_all(enc_all(A.ins), len(A.ins))
    S = Pm['S']
    slb = sl_bytes(prog, Pm['PFLO'], Pm['PFN'])
    sl = compile_sl(slb, NPROG, Pm.get('WTEST')) if with_sl else None
    vm = VM().load(code, sl, NPROG + Pm['PFN'] - 1, A.lab['loop'], S + 272, data, S + 256, random.Random(seed))
    return A, vm, NPROG + Pm['PFN'] - 1


def nonsl_ops(vm):
    return sum(vm.cnt) - vm.units + vm.units * UNIT


def ops_of(vm, f):
    a = nonsl_ops(vm); f(); return nonsl_ops(vm) - a


# ------------------------------------------------------------------ 1. routine tests
def sl_test():
    """the straight line + prefilter as compiled from the two-address block: 2 x 256 points, every lane, 3 chained steps, against F_plain"""
    sl = compile_sl(sl_bytes(prog, 240, 16), NPROG)
    for rep_ in range(2):
        us = [random.getrandbits(256) for _ in range(256)]
        R = [0] * NREGS
        for step in range(3):
            for j in range(256): R[j] = sum(((us[l] >> j) & 1) << l for l in range(256))
            sl(R)
            for l in range(256):
                o = sum(((R[j] >> l) & 1) << j for j in range(256))
                us[l] = F_plain(us[l], KL, PD)
                if o != us[l]: check(False, 'straight line lane %d' % l); break
            else: continue
            break
        pfw = R[PF]
        check(all(((pfw >> l) & 1) == (0 if sum(((R[j] >> l) & 1) << (j - 240) for j in range(240, 256)) == 0 else 1) for l in range(256)), 'prefilter word')
    check(True, 'straight line')


def routine_tests():
    sl_test()
    Pm = dict(FULL)
    A, vm, nsl = mk(Pm)
    c = counts(A, Pm); I = A.lab; R = vm.R; END = I['end']
    S = Pm['S']; WKA = S; KB = keyb(Pm); DPL, DKK = Pm['DPLO'], Pm['DK']
    # setwalk
    R[IDN] = 300; R[RHO] = 12345; R[LR] = END
    planes = [random.getrandbits(256) for _ in range(256)]
    for j in range(256): R[j] = planes[j]
    l = 201; np_ = random.getrandbits(256); R[L] = l; R[NP] = np_
    n = ops_of(vm, lambda: vm.run(I['setwalk'], stop=END))
    check(n == c['setwalk'], 'setwalk ops %d vs %d' % (n, c['setwalk']))
    ok = all(((R[j] >> l) & 1) == ((np_ >> j) & 1) and (R[j] & ~(1 << l)) == (planes[j] & ~(1 << l)) for j in range(256))
    check(ok, 'setwalk effect')
    # restart
    R[LR] = END; R[L] = 7; R[LV] = 99; R[IDN] = 4321
    n = ops_of(vm, lambda: vm.run(I['restart'], stop=END))
    check(n == c['restart'] - 1, 'restart ops %d vs %d' % (n, c['restart'] - 1))   # no wrap: the ADDI after the compare is skipped
    check(vm.M[WKA + 7] == 99 | 4321 << LSTB and R[IDN] == 4322, 'restart effect')
    R[LR] = END; R[L] = 8; R[LV] = 98; R[IDN] = tnum(2 * S - 1, Pm)                     # the last slot-1 trail: next is slot 2 of word 0
    n = ops_of(vm, lambda: vm.run(I['restart'], stop=END))
    check(n == c['restart'] and R[IDN] == tnum(2 * S, Pm) == (2 * RB) << Pm['SB'], 'restart wrap ops %d vs %d' % (n, c['restart']))
    check(all(tnum(i, Pm) != tnum(i2, Pm) for i, i2 in ((0, S), (S - 1, 2 * S - 1), (1, 4 * S + 1))), 'trail numbers distinct')
    R[IDN] = tnum(Pm['U'], Pm); R[LR] = END
    n = ops_of(vm, lambda: vm.run(I['restart'], stop=END))
    check(vm.halt == 11 and n == c['restart_halt'], 'restart halt %d %s' % (n, vm.halt))
    vm.halt = None
    # evalF and outm
    u = random.getrandbits(256); R[UU] = u; R[LR2] = END
    n = ops_of(vm, lambda: vm.run(I['evalF'], stop=END))
    check(n == c['e_eval'] and R[FF] == F_plain(u, KL, PD), 'evalF ops %d vs %d' % (n, c['e_eval']))
    R[UU] = u; R[LR2] = END
    n = ops_of(vm, lambda: vm.run(I['outm'], stop=END))
    check(n == c['e_outm'], 'outm ops %d' % n)
    check(b''.join(R[W0 + i].to_bytes(32, 'little') for i in range(4)) == m_of(u, KL), 'outm message')
    # setup
    vm2 = mk(Pm)[1]; vm2.M[0] = 5
    n = ops_of(vm2, lambda: vm2.run(0, stop=I['loop']))
    check(n == c['setup'], 'setup ops %d vs %d' % (n, c['setup']))
    check(all(vm2.M[i] == 0 for i in range(S)) and all(vm2.M[WKA + i] == i << LSTB for i in range(256)), 'setup effect')
    check(vm2.R[IDN] == 256 and vm2.R[C] == 0 and vm2.R[H] == 0 and vm2.R[ONES] == M256, 'setup state')
    rho = vm2.R[RHO]
    check(all(sum(((vm2.R[j] >> l) & 1) << j for j in range(256)) == (rho + l) & M256 for l in range(0, 256, 17)), 'setup lanes')
    # hit, no DP: planes DPLO..PFLO-1 nonzero
    A, vm, nsl = mk(Pm); R = vm.R
    for j in range(256): R[j] = M256
    R[PF] = 5; R[H] = 0; R[C] = 3
    n = ops_of(vm, lambda: vm.run(I['hit'], stop=I['cont']))
    check(n == c['hit'], 'hit ops %d vs %d' % (n, c['hit']))
    # hit abort
    R[H] = Pm['HMAX']; n = ops_of(vm, lambda: vm.run(I['hit'], stop=I['cont']))
    check(vm.halt == 10 and n == 4, 'hit abort %s %d' % (vm.halt, n)); vm.halt = None
    # DP handler path (the same for every DP without a match): walk 255 alone at a DP; every slot of the S words written
    # with another key except the slot of trail LID[255]; the record goes into that slot
    KM = (1 << KB) - 1
    SBm = Pm['SB']
    def dp_state(vm, lid):
        R = vm.R
        for j in range(256): R[j] = M256
        for j in range(DPL - DKK, 256): R[j] = M256 ^ (1 << 255)
        R[PF] = M256 ^ (1 << 255); R[ONES] = M256; R[H] = 0; R[C] = 777; R[RHO] = 31337; R[IDN] = 5000; R[LR] = END
        vm.M[WKA + 255] = 700 | lid << LSTB
        for j in range(60): R[j] = (R[j] & ~(1 << 255)) | (random.getrandbits(1) << 255)
        return sum(((R[j] >> 255) & 1) << j for j in range(256))
    def other_rec(pt):
        while True:
            key = random.getrandbits(KB)
            if key != pt & KM: return 1 | key << 1
    for i_own in (255, 3 * S + 17, 5 * S - 1):
        A, vm, nsl = mk(Pm); M = vm.M
        pt = dp_state(vm, tnum(i_own, Pm))
        w_own, k_own = i_own % S, i_own // S
        for w in range(S):
            M[w] = sum(other_rec(pt) << (q * RB) for q in range(RPW) if (w, q) != (w_own, k_own))
        before = M[w_own]
        n = ops_of(vm, lambda: vm.run(I['hit'], stop=I['cont']))
        exp = c['hit'] + c['dp_fixed'] + c['restart'] - 1 + c['probe_word'] * S
        check(n == exp, 'DP path (trail %d) ops %d vs %d (halt %s)' % (i_own, n, exp, vm.halt))
        check(M[w_own] == before | (1 | (pt & KM) << 1) << (RB * k_own) and (M[w_own] >> 255) == 0, 'DP record (trail %d)' % i_own)
        check(vm.M[WKA + 255] == 778 | 5000 << LSTB and vm.R[IDN] == 5001, 'DP restart')
    # a match in each of the five slots, in a first, middle and last word: X := the number of that slot's trail
    for w in (0, 100, S - 1):
        for pos in range(RPW):
            A, vm, nsl = mk(Pm); M = vm.M; R = vm.R
            pt = dp_state(vm, 255)
            M[w] = sum((other_rec(pt) if q != pos else 1 | (pt & KM) << 1) << (RB * q) for q in range(RPW))
            if w != 100: M[100] = sum(other_rec(pt) << (RB * q) for q in range(RPW))
            n = ops_of(vm, lambda: vm.run(I['hit'], stop=I['match']))
            check(R[X] == tnum(pos * S + w, Pm) and R[L] == 255 and n == c['hit'] - 2 + 2 + c['ctz_clear'] + c['gather'] + c['record_slot']
                  + c['probe_word'] * w + 2 + 3 + 4 * pos + 3, 'match at word %d slot %d (ops %d)' % (w, pos, n))
            vm.run(I['match'], stop=I['meas'])
            check(R[Y] == 255 and R[LB] == 778 - 700, 'match entry at word %d slot %d' % (w, pos))
    # the DP mask of the hit handler: walks with the top planes zero and the DK planes below them < DT
    DT = Pm['DT']; THRm = thr(Pm); tested = [0, 0]
    for trial in range(4):
        A, vm, nsl = mk(Pm); R = vm.R
        xs = []
        for l in range(256):
            kind = random.randrange(6)
            if kind == 0: x = random.randrange(THRm)                                          # a DP
            elif kind == 1: x = random.randrange(THRm, 1 << DPL)                              # a candidate that is not a DP (x >= THR)
            elif kind == 2: x = THRm - 1 - random.randrange(3)                                # at the threshold, below
            elif kind == 3: x = THRm + random.randrange(3)                                    # at the threshold
            elif kind == 4: x = random.getrandbits(256)
            else: x = random.getrandbits(256 - 240) << 240 | random.getrandbits(240)          # 16 top planes random
            xs.append(max(x, 0) & M256)
        for j in range(256): R[j] = sum(((xs[l] >> j) & 1) << l for l in range(256))
        R[PF] = sum((1 if (xs[l] >> 240) else 0) << l for l in range(256))
        R[ONES] = M256; R[H] = 0; R[C] = 3
        vm.run(I['hit'], stop=I['dpl'])
        want = sum((1 << l) for l in range(256) if xs[l] < THRm)
        check(R[DPM] == want, 'DP mask (trial %d)' % trial)
        tested[0] += bin(want).count('1'); tested[1] += sum(1 for x in xs if (x >> DPL) == 0 and x >= THRm)
    check(tested[0] > 100 and tested[1] > 100, 'DP mask coverage %s' % tested)
    # c = Tb: the iteration's counter and compare, then the HALT
    A, vm, nsl = mk(Pm); R = vm.R
    R[C] = Pm['Tb'] - 1
    n = ops_of(vm, lambda: vm.run(I['cont']))
    check(vm.halt == 12 and n == 3 + c['dl_final'], 'Tb halt %s %d' % (vm.halt, n))
    A, vm, nsl = mk(Pm); R = vm.R
    R[C] = 5
    n = ops_of(vm, lambda: vm.run(I['cont'], stop=I['loop']))
    check(vm.halt is None and n == 3 and R[C] == 6, 'counter ops %d' % n)


def pred_replay(ta, tb, Ft, e, G):
    """operations of the replay from label match (the 3 that take the trail number from the record are counted with the DP
    walk), from the per-step costs of proof.md Section 4.2: (ops, halt code, pair); ta, tb: the trails a, b (start .. DP)"""
    la, lb = len(ta) - 1, len(tb) - 1
    ops = 12 + (la - 1) * (e + 10) + (e + 6) + 3 * ((la - 1) // G + 1)       # entry, measuring walk, checkpoints
    d = la - lb
    if d >= 0:
        K = d // G; ops += 2 + 3 + 6 * K + 3 + 4 + (d - K * G) * (e + 7) + 2 + 2; IA, NX = d, (K + 1) * G
    else:
        ops += 2 + 4 + (-d) * (e + 7) + 2; IA, NX = 0, G
    ops += 2
    if ta[IA] == tb[IA - d]: return ops + 1, 13, None
    while True:
        ops += 2
        if NX >= la: ops += 1; MM = la - IA; break
        m = NX - IA; ops += 3 + m * (e + 6) + 3
        if ta[NX] == tb[NX - d]: MM = m; break
        ops += 6; IA, NX = NX, NX + G
    p, q = ta[IA], tb[IA - d]
    for k in range(1, MM + 1):
        if Ft(p) == Ft(q): return ops + (k - 1) * (2 * e + 13) + 2 * e + 9 + 2 * E_OUTM + 13, 1, (p, q)   # success exit: two message builds (e_outm each), 8 stores, the halt
        p, q = Ft(p), Ft(q)
    return ops + MM * (2 * e + 13) + 3, 13, None


def replay_bound(c, la, lb, G):
    """the worst-case bound of Section 4.2 with LRC replaced by max(la, lb)"""
    m = max(la, lb)
    return c['replay_rate'] * m + c['replay_g'] * G + c['replay_nck'] * ((m - 1) // G + 1) + c['replay_const']


def replay_tests(ntrials=60, S=400, LRC=200):
    """the replay on pairs of trails of the 12-bit truncation of F with a DP of about 1 in 21 (x < 192): the measuring walk
    with its checkpoints, alignment, segments, lock step; pairs with the same end (found / p = q) and with different ends
    (exhausted: a false key match).  G = ceil(LRC / (S - 1))."""
    Pm = dict(S=S, U=S, SB=9, LRC=LRC, Tb=900, HMAX=10 ** 9, DPLO=8, DK=2, DT=3, PFLO=10, PFN=2, WTEST=12)
    THRm = thr(Pm)
    mask = (1 << 12) - 1
    Ft = lambda u: F_plain(u, KL, PD) & mask
    A, vm0, nsl = mk(Pm); I = A.lab; c = counts(A, Pm); e = c['e_eval']; globals()['E_OUTM'] = c['e_outm']; END = I['end']; S = Pm['S']; G = gap(Pm)
    seen = {1: 0, 13: 0, 'diff': 0, 'dneg': 0, 'dpos': 0}
    done = 0
    while done < ntrials:
        rho = random.getrandbits(256)
        trails = {}
        for a in range(256, 400):
            u = (rho + a) & M256; pts = [u]
            for i in range(Pm['LRC']):
                u = Ft(u); pts.append(u)
                if u < THRm: break
            if pts[-1] < THRm: trails[a] = pts
        ends = {}
        for a, t in trails.items(): ends.setdefault(t[-1], []).append(a)
        pairs = [(v[0], v[1]) for v in ends.values() if len(v) > 1][:3]
        pairs += [(v[1], v[0]) for v in ends.values() if len(v) > 1][:2]
        keys = list(trails)
        pairs.append(tuple(random.sample(keys, 2)))
        for a, b in pairs:
            if done >= ntrials: break
            ta, tb = trails[a], trails[b]
            la, lb = len(ta) - 1, len(tb) - 1
            A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
            R[RHO] = rho; R[LR2] = END; R[L] = 9; M[S + 9] = (5000 - lb) | b << LSTB; R[C1] = 5000; R[X] = a
            ops = ops_of(vm, lambda: vm.run(I['match']))
            pops, phalt, ppair = pred_replay(ta, tb, Ft, e, G)
            check(R[LA] == la and R[LB] == lb, 'replay lengths %d %d vs %d %d' % (R[LA], R[LB], la, lb))
            check(vm.halt == phalt and ops == pops, 'replay ops %d vs %d, halt %s vs %s (la %d lb %d G %d)' % (ops, pops, vm.halt, phalt, la, lb, G))
            if ta[-1] != tb[-1]:
                check(phalt == 13, 'different ends merged'); seen['diff'] += 1
            elif phalt == 13: seen[13] += 1
            else:
                seen[1] += 1; seen['dneg' if la < lb else 'dpos'] += 1
                out = M[S + 264:S + 272]
                ma = b''.join(out[x].to_bytes(32, 'little') for x in range(4)); mb = b''.join(out[4 + x].to_bytes(32, 'little') for x in range(4))
                check(ma != mb and (int.from_bytes(sha3_256_r(ma, NR), 'little') & mask) == (int.from_bytes(sha3_256_r(mb, NR), 'little') & mask), 'replay pair')
                check(ma == m_of(ppair[0], KL) and mb == m_of(ppair[1], KL), 'replay pair = the first merge')
            check(ops <= replay_bound(c, la, lb, G) and ops <= c['replay_max'], 'replay bound')
            done += 1
    # p = q: the start of trail b is a point of trail a (b = a_j - rho), or the reverse: halt 13 after the alignment
    for a, ta in list(trails.items())[:12]:
        if len(ta) < 4: continue
        for j, rev in ((1, 0), (len(ta) - 2, 0), (2, 1)):
            tb = ta[j:]; bnum = (ta[j] - rho) & M256
            x_, y_, tx, ty = (a, bnum, ta, tb) if not rev else (bnum, a, tb, ta)
            A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
            R[RHO] = rho; R[LR2] = END; R[L] = 9; M[S + 9] = (5000 - (len(ty) - 1)) | y_ << LSTB; R[C1] = 5000; R[X] = x_
            ops = ops_of(vm, lambda: vm.run(I['match']))
            pops, phalt, _ = pred_replay(tx, ty, Ft, e, G)
            check(phalt == 13 and vm.halt == 13 and ops == pops, 'replay p=q ops %d vs %d (j %d rev %d)' % (ops, pops, j, rev))
            seen[13] += 1
    check(seen[13] >= 6, 'p=q coverage')
    # a stored trail without a DP within LRC (checks the guard): halt 13
    A, vm, nsl = mk(dict(Pm, LRC=1)); R = vm.R; M = vm.M
    for a in range(256, 400):
        if Ft((5 + a) & M256) >= THRm:
            R[RHO] = 5; R[LR2] = END; R[L] = 9; M[S + 9] = 9 | 300 << LSTB; R[C1] = 10; R[X] = a
            vm.run(A.lab['match']); check(vm.halt == 13 and R[LA] == 1, 'measure guard'); break
    # the length guard of the new trail: lb = LRC + 1 is refused at once (7 operations), lb = LRC goes on
    for lbv, want in ((Pm['LRC'] + 1, 13), (Pm['LRC'], None)):
        A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
        R[RHO] = 5; R[LR2] = A.lab['end']; R[L] = 9; M[S + 9] = (10 ** 6 - lbv) | 300 << LSTB; R[C1] = 10 ** 6; R[X] = 256
        n = ops_of(vm, lambda: vm.run(A.lab['match'], stop=A.lab['meas'] if want is None else None))
        check((vm.halt == 13 and n == 7) if want else (vm.halt is None and R[LB] == lbv and R[Y] == 300), 'lb guard %d' % lbv)
    print('replay tests (G %d): found %d (d >= 0: %d, d < 0: %d), p=q %d, different ends %d' % (G, seen[1], seen['dpos'], seen['dneg'], seen[13], seen['diff']))
    check(seen[1] > 0 and seen['diff'] > 0, 'replay coverage G %d' % G)


# ------------------------------------------------------------------ 2. end-to-end
def check_pair(vm, Pm, W):
    S = Pm['S']; out = vm.M[S + 264:S + 272]
    ma = b''.join(out[i].to_bytes(32, 'little') for i in range(4)); mb = b''.join(out[4 + i].to_bytes(32, 'little') for i in range(4))
    da, db = sha3_256_r(ma, NR), sha3_256_r(mb, NR)
    mask = (1 << W) - 1
    return ma != mb and len(ma) == 128 and (int.from_bytes(da, 'little') & mask) == (int.from_bytes(db, 'little') & mask)


def e2e(name, Pm, seeds, expect=None, W=26):
    A = None; res = {}
    for sd in seeds:
        A, vm, nsl = mk(Pm, sd, True)
        t0 = time.time(); vm.run(0); dt = time.time() - t0
        c = counts(A, Pm); I = A.lab; cnt = vm.cnt
        steps = vm.slsteps
        hits = cnt[I['hit']]; dps = cnt[I['dp1']]; rest = cnt[I['rs1']]; dl = cnt[I['dl']]      # dl: 1 when Tb is reached
        # exact group checks
        calls = cnt[I['setwalk']]
        check(sum(cnt[I['setwalk']:I['sw_end'] + 1]) == (c['setwalk']) * calls, 'setwalk group %d calls' % calls)
        check(sum(cnt[I['gather']:I['record']]) == c['gather'] * dps, 'gather group')
        check(cnt[I['loop']] == steps and cnt[I['cont']] in (steps, steps - 1), 'loop counts')
        # totals against the counted bounds
        nonsl = nonsl_ops(vm)
        replay_ops = sum(cnt[I['evalF']:I['end']]) - vm.units + vm.units * UNIT
        bound = (c['setup'] + 5 * steps + hits * c['hit'] + dps * c['dp_max'] + (rest + 1) * (c['restart'] + 3)
                 + c['dl_final'] + c['restart_halt'] + c['replay_max'])
        check(nonsl <= bound, '%s seed %d: ops %d > bound %d' % (name, sd, nonsl, bound))
        # exact accounting of what is not data dependent
        base = c['setup'] + 5 * steps
        res[sd] = (vm.halt, steps, hits, dps, rest, dl, replay_ops)
        if vm.halt == 1:
            check(check_pair(vm, Pm, W), '%s seed %d: output pair invalid' % (name, sd))
        if replay_ops:
            # exact replay operations for the observed trails (rebuilt from rho + X and rho + Y with F truncated to W bits)
            la, lb = vm.R[LA], vm.R[LB]
            e = c['e_eval']; G = gap(Pm); maskW = (1 << W) - 1; THRm = thr(Pm); globals()['E_OUTM'] = c['e_outm']
            FtW = lambda u: F_plain(u, KL, PD) & maskW
            def trail(u, n):
                pts = [u]
                for _ in range(n): pts.append(FtW(pts[-1]))
                return pts
            ta = trail((vm.R[RHO] + vm.R[X]) & M256, la); tb = trail((vm.R[RHO] + vm.R[Y]) & M256, lb)
            if 1 <= la and lb <= Pm['LRC'] and ta[-1] < THRm and all(x >= THRm for x in ta[1:-1]):
                pops, phalt, _ = pred_replay(ta, tb, FtW, e, G)
                check(replay_ops == pops and vm.halt == phalt, '%s seed %d: replay ops %d vs %d (la %d lb %d G %d)' % (name, sd, replay_ops, pops, la, lb, G))
            check(replay_ops <= replay_bound(c, la, lb, G), 'replay bound')
        print('%-10s seed %3d halt %2s steps %5d hits %5d dp %4d restarts %4d tb %4d replay_ops %7d  total %d' %
              (name, sd, vm.halt, steps, hits, dps, rest, dl, replay_ops, nonsl + steps * nsl))
        if expect is not None: check(vm.halt in expect, '%s seed %d: halt %s not in %s' % (name, sd, vm.halt, expect))
    return res


def main():
    ns = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    routine_tests()
    replay_tests()
    replay_tests(40, S=264, LRC=2000)
    replay_tests(40, S=264, LRC=6000)
    print('routine tests done, failures so far:', len(FAILS))
    base = dict(S=3000, U=3000, SB=12, LRC=17 << 8, Tb=3000, HMAX=10 ** 9, DPLO=18, DK=2, DT=3, PFLO=22, PFN=4, WTEST=26)
    seeds = list(range(1, ns + 1))
    e2e('base', base, seeds, expect=(1, 13))
    # width 32, DP of 10 bits and a comparator, prefilter of 6 planes; trails of mean length ~1000 steps against a replay cap of 400:
    # a colliding trail longer than the cap is refused (halt 13)
    w32 = dict(S=3000, U=3000, SB=12, LRC=400, Tb=60000, HMAX=10 ** 9, DPLO=22, DK=3, DT=5, PFLO=26, PFN=6, WTEST=32)
    e2e('w32cap', w32, seeds[:3], expect=(1, 11, 12, 13), W=32)
    small = dict(base, S=400, U=400, SB=9, LRC=2000, Tb=4000)             # small table: U exhaustion possible
    e2e('smalltab', small, seeds, expect=(1, 11, 12, 13))
    abort = dict(base, HMAX=3)                                            # hit counter abort
    e2e('abort', abort, seeds[:3], expect=(10,))
    tb = dict(base, LRC=3, Tb=5)                                          # Tb reached
    e2e('tb5', tb, seeds[:2], expect=(12,))
    uex = dict(base, S=264, U=264, SB=9, Tb=100000)                        # trail limit reached
    e2e('u264', uex, seeds[:3], expect=(11, 1, 13))
    packed = dict(base, S=264, U=1320, SB=9, LRC=2000, Tb=8000)            # U = 5 S: every word fills its five slots
    e2e('packed', packed, seeds[:4], expect=(1, 11, 12, 13))
    nocmp = dict(base, DK=0, DT=1)                                        # no comparator (theta = 2^-H)
    e2e('nocmp', nocmp, seeds[:2], expect=(1, 13))
    print('checks run: %d, failures: %d' % (NCHK[0], len(FAILS)))
    return len(FAILS)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
```

### D.4 Output of `python3 other4_test.py 2 7`

```
replay tests (G 1): found 50 (d >= 0: 24, d < 0: 26), p=q 36, different ends 10
replay tests (G 8): found 34 (d >= 0: 16, d < 0: 18), p=q 33, different ends 6
replay tests (G 23): found 35 (d >= 0: 17, d < 0: 18), p=q 33, different ends 5
routine tests done, failures so far: 0
base       seed   1 halt  1 steps   107 hits   107 dp   67 restarts   66 tb    0 replay_ops  836546  total 20655129
base       seed   2 halt  1 steps   135 hits   135 dp   87 restarts   86 tb    0 replay_ops 1440875  total 26555622
w32cap     seed   1 halt 13 steps   490 hits   484 dp   73 restarts   72 tb    0 replay_ops       7  total 72612344
w32cap     seed   2 halt 13 steps   498 hits   487 dp   79 restarts   78 tb    0 replay_ops       7  total 74149730
smalltab   seed   1 halt  1 steps   107 hits   107 dp   67 restarts   66 tb    0 replay_ops  836410  total 16533018
smalltab   seed   2 halt  1 steps   135 hits   135 dp   87 restarts   86 tb    0 replay_ops 1465491  total 21210263
abort      seed   1 halt 10 steps     4 hits     4 dp    2 restarts    2 tb    0 replay_ops       0  total 1028218
abort      seed   2 halt 10 steps     4 hits     4 dp    3 restarts    3 tb    0 replay_ops       0  total 1101765
tb5        seed   1 halt 12 steps     5 hits     5 dp    2 restarts    2 tb    1 replay_ops       0  total 1164924
tb5        seed   2 halt 12 steps     5 hits     5 dp    3 restarts    3 tb    1 replay_ops       0  total 1238471
u264       seed   1 halt 11 steps    16 hits    16 dp    9 restarts    8 tb    0 replay_ops       0  total 2587325
u264       seed   2 halt 11 steps    17 hits    17 dp    9 restarts    8 tb    0 replay_ops       0  total 2724001
packed     seed   1 halt  1 steps    98 hits    98 dp   63 restarts   62 tb    0 replay_ops  471816  total 14691012
packed     seed   2 halt  1 steps   135 hits   135 dp   82 restarts   81 tb    0 replay_ops 1490566  total 20915003
nocmp      seed   1 halt  1 steps    68 hits    68 dp   52 restarts   51 tb    0 replay_ops  704762  total 14086554
nocmp      seed   2 halt  1 steps   135 hits   135 dp  123 restarts  122 tb    0 replay_ops 1440875  total 29202613
checks run: 967, failures: 0
```

### D.5 scan.c (the parameter scan P) and its table scan_tab.h

```c
/* scan.c - freestanding C port of `cert4.py --scan` (the parameter scan P): reads ledger.txt and counts.txt,
 * writes params.json and scan_counts.txt.  Variant switch: "ta" (fac_ta/cert4.py: rep_rate = meas_iter + replay_iter,
 * walk state 512 words) or "st" (fac_st/cert4.py: rep_rate = replay_rate + (replay_g + replay_nck) / (S - 1),
 * checkpoint gap G, walk words 256).
 * Float model: IEEE doubles in the order of the Python/numpy expressions (numpy's pairwise sum emulated); exp
 * table-driven (128 entries), expm1 by series, log table-driven (129 entries), each at most 30 double operations;
 * the grid's best point by least N (cert4.py: least log2(N / UNIT), the same order).
 * Exact part: the Decimal(80 digits) exponentials and logarithms of success() replaced by signed fixed point with
 * 448 fraction bits (about 134 digits); integers (Tb, LRC, HMAX) exact in 512-bit words.
 * No libc; static arrays only; the work runs in a forked child, the parent reports its peak RSS (wait4 ru_maxrss),
 * the child reports its own VmHWM.  Usage: scan ledger.txt counts.txt params.json scan_counts.txt ta|st [S] */
typedef unsigned long u64; typedef long i64; typedef unsigned char u8; typedef unsigned __int128 u128;
__asm__(".global _start\n_start:\n xor %rbp,%rbp\n mov %rsp,%rdi\n and $-16,%rsp\n call cmain\n mov %rax,%rdi\n mov $60,%rax\n syscall\n");
static i64 sc3(i64 n, i64 a, i64 b, i64 c){ i64 r; __asm__ volatile("syscall":"=a"(r):"a"(n),"D"(a),"S"(b),"d"(c):"rcx","r11","memory"); return r; }
void *memset(void *d, int c, unsigned long n){ u8 *p=d; while(n--) *p++=(u8)c; return d; }
void *memcpy(void *d, const void *s, unsigned long n){ u8 *p=d; const u8 *q=s; while(n--) *p++=*q++; return d; }
static int fd_out=1; static char obuf[512]; static int olen;
static void oflush(void){ if(olen){ sc3(1,fd_out,(i64)obuf,olen); olen=0; } }
static void oc(char c){ if(olen==512) oflush(); obuf[olen++]=c; }
static void os(const char *s){ while(*s) oc(*s++); }
static void ou(u64 v){ char t[24]; int n=0; do{ t[n++]='0'+v%10; v/=10; }while(v); while(n) oc(t[--n]); }
static void die(const char *m){ oflush(); fd_out=2; os("scan: "); os(m); oc('\n'); oflush(); sc3(60,1,0,0); }
#define CHECK(c,m) do{ if(!(c)) die(m); }while(0)

/* ================= 512-bit words: unsigned integers (B) and signed fixed point (F, value = word / 2^448) ================= */
#define NL 8
#define FB 448
typedef struct { u64 w[NL]; } B;
static B b_u(u64 v){ B r; memset(&r,0,sizeof r); r.w[0]=v; return r; }
static int b_zero(B a){ for(int i=0;i<NL;i++) if(a.w[i]) return 0; return 1; }
static B b_add(B a, B b){ B r; u64 c=0; for(int i=0;i<NL;i++){ u128 s=(u128)a.w[i]+b.w[i]+c; r.w[i]=(u64)s; c=(u64)(s>>64); } return r; }
static B b_sub(B a, B b){ B r; u64 br=0; for(int i=0;i<NL;i++){ u128 s=(u128)a.w[i]-b.w[i]-br; r.w[i]=(u64)s; br=(u64)(s>>64)&1; } return r; }
static int b_cmp(B a, B b){ for(int i=NL-1;i>=0;i--){ if(a.w[i]!=b.w[i]) return a.w[i]<b.w[i]?-1:1; } return 0; }
static B b_shl(B a, int s){ B r; memset(&r,0,sizeof r); int q=s/64, t=s%64;
  for(int i=NL-1;i>=q;i--){ r.w[i]=a.w[i-q]<<t; if(t && i-q-1>=0) r.w[i]|=a.w[i-q-1]>>(64-t); } return r; }
static B b_shr(B a, int s){ B r; memset(&r,0,sizeof r); int q=s/64, t=s%64;
  for(int i=0;i+q<NL;i++){ r.w[i]=a.w[i+q]>>t; if(t && i+q+1<NL) r.w[i]|=a.w[i+q+1]<<(64-t); } return r; }
static B b_mul(B a, B b){ u64 t[2*NL]; memset(t,0,sizeof t);
  for(int i=0;i<NL;i++){ if(!a.w[i]) continue; u64 c=0; for(int j=0;j<NL;j++){ u128 p=(u128)a.w[i]*b.w[j]+t[i+j]+c; t[i+j]=(u64)p; c=(u64)(p>>64); } t[i+NL]=c; }
  for(int i=NL;i<2*NL;i++) CHECK(!t[i],"integer overflow");
  B r; memcpy(r.w,t,sizeof r.w); return r; }
static B b_mulu(B a, u64 m){ return b_mul(a,b_u(m)); }
static B b_divu(B a, u64 d, u64 *rem){ B q; u128 r=0; for(int i=NL-1;i>=0;i--){ r=(r<<64)|a.w[i]; q.w[i]=(u64)(r/d); r%=d; } if(rem) *rem=(u64)r; return q; }
static int b_bitlen(B a){ for(int i=NL-1;i>=0;i--) if(a.w[i]) return 64*i+64-__builtin_clzl(a.w[i]); return 0; }
static void b_dec(B a, char *out){ char t[160]; int n=0; do{ u64 r; a=b_divu(a,10,&r); t[n++]='0'+(char)r; }while(!b_zero(a)); int k=0; while(n) out[k++]=t[--n]; out[k]=0; }

typedef B F;
static int f_neg_p(F a){ return (int)(a.w[NL-1]>>63); }
static F f_neg(F a){ return b_sub(b_u(0),a); }
static F f_abs(F a){ return f_neg_p(a)? f_neg(a) : a; }
static F f_int(i64 v){ F r=b_shl(b_u((u64)(v<0?-v:v)),FB); return v<0? f_neg(r) : r; }
static int f_cmp(F a, F b){ int na=f_neg_p(a), nb=f_neg_p(b); if(na!=nb) return na? -1 : 1; return b_cmp(a,b); }
static F f_sar(F a, int s){ if(!f_neg_p(a)) return b_shr(a,s); return f_neg(b_shr(f_neg(a),s)); }   /* magnitude truncation */
static F f_shl(F a, int s){ F m=f_abs(a); CHECK(b_bitlen(m)+s<=8*64-1,"fixed overflow (shl)"); m=b_shl(m,s); return f_neg_p(a)? f_neg(m) : m; }
static F f_mul(F a, F b){
  int ng=f_neg_p(a)^f_neg_p(b); F x=f_abs(a), y=f_abs(b); u64 t[2*NL]; memset(t,0,sizeof t);
  for(int i=0;i<NL;i++){ if(!x.w[i]) continue; u64 c=0; for(int j=0;j<NL;j++){ u128 p=(u128)x.w[i]*y.w[j]+t[i+j]+c; t[i+j]=(u64)p; c=(u64)(p>>64); } t[i+NL]=c; }
  CHECK(!t[15] && !(t[14]>>63),"fixed overflow (mul)");
  F r; for(int i=0;i<NL;i++) r.w[i]=t[i+7]; return ng? f_neg(r) : r; }
static F f_mulu(F a, u64 m){ F x=f_abs(a); u64 c=0; for(int i=0;i<NL;i++){ u128 p=(u128)x.w[i]*m+c; x.w[i]=(u64)p; c=(u64)(p>>64); }
  CHECK(!c && !(x.w[NL-1]>>63),"fixed overflow (mulu)"); return f_neg_p(a)? f_neg(x) : x; }
static F f_divu(F a, u64 d){ F q=b_divu(f_abs(a),d,0); return f_neg_p(a)? f_neg(q) : q; }

/* double <-> fixed */
typedef union { double d; u64 u; } DU;
static double d_bits(u64 u){ DU x; x.u=u; return x.d; }
static u64 d_u(double d){ DU x; x.d=d; return x.u; }
static double d_pow2(int e){            /* 2^e, -1074 <= e <= 1023 */
  if(e>=-1022) return d_bits((u64)(e+1023)<<52);
  return d_bits(1UL<<(e+1074)); }
static double d_ldexp(double x, int e){ while(e>1000){ x*=d_pow2(1000); e-=1000; } while(e<-1000){ x*=d_pow2(-1000); e+=1000; } return x*d_pow2(e); }
static F f_dbl(double d){                /* exact for |d| < 2^63 with bits >= 2^-448; lower bits truncated */
  u64 u=d_u(d); int s=(int)(u>>63), ex=(int)((u>>52)&2047); u64 m=u&((1UL<<52)-1);
  if(ex==0) return b_u(0); m|=1UL<<52; int e=ex-1075+FB;   /* value = m 2^(ex-1075) */
  F r= e>=0? f_shl(b_u(m),e) : (e>-64? b_u(m>>(-e)) : b_u(0)); return s? f_neg(r) : r; }
static double f_to_d(F a){               /* round to nearest, ties to even */
  int ng=f_neg_p(a); F m=f_abs(a); int p=b_bitlen(m); if(!p) return 0.0;
  u64 top; int round=0, sticky=0;
  if(p<=53){ top=m.w[0]; }
  else { B t=b_shr(m,p-53); top=t.w[0]; int rb=p-54; round=(int)((m.w[rb/64]>>(rb%64))&1);
    for(int i=0;i<rb/64;i++) if(m.w[i]) sticky=1; if(m.w[rb/64]&((1UL<<(rb%64))-1)) sticky=1;
    if(round && (sticky || (top&1))) top++; }
  int sh= p<=53? 0 : p-53;               /* value = top 2^(sh - 448) */
  double r=d_ldexp((double)top, sh-FB); return ng? -r : r; }

/* constants (ln 2, 1/ln 2, 1/n!, the exp and log tables): computed by the TABGEN build of this file with the 448-bit
 * routines below and embedded in scan_tab.h as bit patterns, so the scan run itself computes none of them */
#define NTAY 26
static F LN2, INVLN2, IFACT[NTAY+1], ONE, HALF;
static double ET[128], LT[129], E_INV, E_HI, E_LO, E_LN2, C_[14];
static double m_log(double x);
static F f_exp(F x){                    /* x < 43: 42 fixed-point multiplications */
  F q=f_mul(x,INVLN2); q=b_add(q,HALF); i64 k=(i64)q.w[NL-1];   /* k = floor(x/ln2 + 1/2) */
  F r=b_sub(x, k>=0? f_mulu(LN2,(u64)k) : f_neg(f_mulu(LN2,(u64)-k)));
  if(k<-FB-2) return b_u(0);
  CHECK(k<62,"exp overflow");
  r=f_sar(r,16);
  F p=IFACT[NTAY]; for(int n=NTAY-1;n>=0;n--) p=b_add(f_mul(p,r),IFACT[n]);
  for(int i=0;i<16;i++) p=f_mul(p,p);
  return k>=0? f_shl(p,(int)k) : b_shr(p,(int)-k);
}
#ifdef TABGEN
static double dlog0(double x){
  u64 u=d_u(x); int e=(int)((u>>52)&2047)-1023; double m=d_bits((u&((1UL<<52)-1))|(1023UL<<52));
  if(m>1.4142135623730951){ m*=0.5; e++; }
  double s=(m-1)/(m+1), s2=s*s, t=0, pw=s; for(int k=0;k<14;k++){ t+=pw/(2*k+1); pw*=s2; }
  return 2*t + e*0.6931471805599453; }
#define NEWTON 6
#define GUESS(v) dlog0(v)
#else
#define NEWTON 4
#define GUESS(v) m_log(v)
#endif
static F f_ln(F y){                      /* y > 0: Newton x <- x + y exp(-x) - 1 from the double logarithm, 4 exps */
  CHECK(!f_neg_p(y) && !b_zero(y),"ln of non-positive");
  F x=f_dbl(GUESS(f_to_d(y)));
  for(int i=0;i<NEWTON;i++) x=b_sub(b_add(x,f_mul(y,f_exp(f_neg(x)))),ONE);
  return x; }

/* double exp (128-entry table), expm1 (series, else exp - 1), log (129-entry table and the series of log1p),
 * log1p for |x| < 2^-30: each at most 30 double operations */
static double e_exp(double x){
  if(x==0) return 1.0; if(x<-745.2) return 0.0;
  double z=x*E_INV; double kd=(z+6755399441055744.0)-6755399441055744.0; i64 k=(i64)kd;
  double r=(x-kd*E_HI)-kd*E_LO;
  double q=r+r*r*(0.5+r*(0.16666666666666666+r*(0.041666666666666664+r*(0.008333333333333333+r*0.001388888888888889))));
  int i=(int)(k&127); i64 e=k>>7; double t=ET[i]; double v=t+t*q;
  if(e>=-1022) return v*d_bits((u64)(e+1023)<<52);
  return (v*d_pow2(-1000))*d_pow2((int)e+1000); }
static double e_expm1(double x){         /* x <= 0 */
  double a=x<0?-x:x;
  if(a<0.34657359027997264){ double p=C_[13]; for(int n=12;n>=2;n--) p=C_[n]+x*p; return x+x*x*p; }
  return e_exp(x)-1.0; }
static double m_log(double x){
  u64 u=d_u(x); int e=(int)((u>>52)&2047)-1023; CHECK(e>-1023 && e<1024 && x>0,"log domain");
  double m=d_bits((u&((1UL<<52)-1))|(1023UL<<52));
  double kd=((m-1)*128+6755399441055744.0)-6755399441055744.0; int i=(int)kd;
  double c=1+kd*0.0078125, r=(m-c)/c;
  double p=r*(1+r*(-0.5+r*(0.3333333333333333+r*(-0.25+r*(0.2+r*(-0.16666666666666666+r*(0.14285714285714285+r*-0.125)))))));
  return (LT[i]+p)+(double)e*E_LN2; }
static double m_log1p(double x){ double a=x<0?-x:x; CHECK(a<9.313225746154785e-10,"log1p range"); return x-(x*x)*0.5; }
#define m_exp e_exp
#define m_expm1 e_expm1

#ifdef TABGEN
static void wF(const char *nm, F v){ os("{"); for(int i=0;i<NL;i++){ os("0x"); for(int k=60;k>=0;k-=4) oc("0123456789abcdef"[(v.w[i]>>k)&15]); os("UL"); if(i<NL-1) oc(','); } os("}"); (void)nm; }
static void wD(double d){ u64 v=d_u(d); os("0x"); for(int k=60;k>=0;k-=4) oc("0123456789abcdef"[(v>>k)&15]); os("UL"); }
static int tabgen(void){
  ONE=f_int(1); HALF=b_shl(b_u(1),FB-1);
  F s=b_u(0); for(int k=1;k<=470;k++){ F t=b_divu(b_shr(ONE,k),(u64)k,0); s=b_add(s,t); }   /* ln 2 = sum 1/(k 2^k) */
  LN2=s;
  F x=f_dbl(1.4426950408889634); for(int i=0;i<6;i++) x=f_mul(x,b_sub(f_int(2),f_mul(LN2,x)));   /* 1/ln 2, Newton */
  INVLN2=x;
  IFACT[0]=ONE; for(int n=1;n<=NTAY;n++) IFACT[n]=f_divu(IFACT[n-1],(u64)n);
  os("/* scan_tab.h - written by the TABGEN build of scan.c (448-bit fixed point; doubles rounded to nearest) */\n");
  os("static const u64 T_LN2[8]="); wF("",LN2); os(";\nstatic const u64 T_INVLN2[8]="); wF("",INVLN2); os(";\n");
  os("static const u64 T_IFACT[][8]={\n"); for(int n=0;n<=NTAY;n++){ wF("",IFACT[n]); os(n<NTAY? ",\n" : "};\n"); }
  os("static const u64 T_ET[128]={\n"); for(int i=0;i<128;i++){ wD(f_to_d(f_exp(f_divu(f_mulu(LN2,(u64)i),128)))); os(i<127? (i%4==3? ",\n" : ",") : "};\n"); }
  os("static const u64 T_LT[129]={\n"); for(int i=0;i<=128;i++){ wD(i? f_to_d(f_ln(b_add(ONE,f_divu(f_int(i),128)))) : 0.0); os(i<128? (i%4==3? ",\n" : ",") : "};\n"); }
  F l=f_divu(LN2,128); double h=f_to_d(l); double hi=d_bits(d_u(h)&~((1UL<<20)-1));
  os("static const u64 T_E[4]={"); wD(f_to_d(f_mulu(INVLN2,128))); oc(','); wD(hi); oc(','); wD(f_to_d(b_sub(l,f_dbl(hi)))); oc(','); wD(f_to_d(LN2)); os("};\n");
  os("static const u64 T_C[14]={\n"); for(int n=0;n<14;n++){ wD(f_to_d(IFACT[n])); os(n<13? (n%4==3? ",\n" : ",") : "};\n"); }
  oflush(); return 0; }
static void c_load(void){ }
#else
#include "scan_tab.h"
static void c_load(void){
  ONE=f_int(1); HALF=b_shl(b_u(1),FB-1);
  memcpy(LN2.w,T_LN2,64); memcpy(INVLN2.w,T_INVLN2,64); for(int n=0;n<=NTAY;n++) memcpy(IFACT[n].w,T_IFACT[n],64);
  for(int i=0;i<128;i++) ET[i]=d_bits(T_ET[i]); for(int i=0;i<=128;i++) LT[i]=d_bits(T_LT[i]);
  E_INV=d_bits(T_E[0]); E_HI=d_bits(T_E[1]); E_LO=d_bits(T_E[2]); E_LN2=d_bits(T_E[3]); for(int n=0;n<14;n++) C_[n]=d_bits(T_C[n]); }
#endif

/* numpy pairwise sum of a contiguous float64 array (loops_utils.h, PW_BLOCKSIZE 128) */
static double pw_sum(const double *a, long n){
  if(n<8){ double r=0.; for(long i=0;i<n;i++) r+=a[i]; return r; }
  if(n<=128){ double r[8]; for(int j=0;j<8;j++) r[j]=a[j]; long i;
    for(i=8;i<n-(n%8);i+=8) for(int j=0;j<8;j++) r[j]+=a[i+j];
    double res=((r[0]+r[1])+(r[2]+r[3]))+((r[4]+r[5])+(r[6]+r[7])); for(;i<n;i++) res+=a[i]; return res; }
  long n2=n/2; n2-=n2%8; return pw_sum(a,n2)+pw_sum(a+n2,n-n2); }

/* ================= inputs ================= */
static char led[8192], cnt[8192];
static void slurp(const char *p, char *buf, long cap){ int fd=(int)sc3(2,(i64)p,0,0); if(fd<0) die("open input");
  long n=0, k; while((k=sc3(0,fd,(i64)(buf+n),cap-1-n))>0) n+=k; sc3(3,fd,0,0); CHECK(n>0 && n<cap-1,"read input"); buf[n]=0; }
static long slen(const char *s){ long n=0; while(s[n]) n++; return n; }
static int startsw(const char *s, const char *p){ while(*p) if(*s++!=*p++) return 0; return 1; }
/* value after "^KEY<spaces>" at a line start; 0 if absent */
static int linekey(const char *buf, const char *key, u64 *v, int strict_eol){
  int n=0; while(key[n]) n++;
  for(const char *s=buf; *s; ){ const char *t=s; while(*t==' '||*t=='\t') t++;
    if(startsw(t,key) && (t[n]==' '||t[n]=='\t')){ const char *q=t+n; while(*q==' '||*q=='\t') q++;
      if(*q>='0'&&*q<='9'){ u64 x=0; int dig=0; while(*q>='0'&&*q<='9'){ x=x*10+(u64)(*q++-'0'); dig++; }
        while(*q==' '||*q=='\t'||*q=='\r') q++;
        if(!strict_eol || *q=='\n' || !*q){ CHECK(dig<=19,"count too large"); *v=x; return 1; } } }
    while(*s && *s!='\n') s++; if(*s) s++; }
  return 0; }
static u64 need(const char *buf, const char *key, int strict){ u64 v; if(!linekey(buf,key,&v,strict)){ os("missing: "); os(key); oc('\n'); die("input key"); } return v; }
static u64 ledkey(const char *key){   /* ledger: ^KEY\s+(\d+) */
  for(const char *s=led; *s; ){ if(startsw(s,key)){ const char *q=s; while(*q && *q!=' ' && *q!='\t') q++;
      if(q-s==slen(key)){ while(*q==' '||*q=='\t') q++; u64 x=0; while(*q>='0'&&*q<='9') x=x*10+(u64)(*q++-'0'); return x; } }
    while(*s && *s!='\n') s++; if(*s) s++; }
  die("ledger key"); return 0; }

/* ================= the scan ================= */
static int ST; static i64 NR, BSTEP, UNIT; static i64 S, U, KK=50;
static double REP; static u64 HIT, REPI_TA;  /* rep_rate: float (st) or int (ta) */
static u64 CNT_FE, CNT_FB, CNT_EE, CNT_EB;
#define L_ 256
static double vbuf[4096];

static double P257;
static double fsucc(double Tb, double th, u64 w_i, long J, int HF){
  CNT_FE++; CNT_FB+=(u64)J;
  double W=d_pow2((int)w_i);             /* w = 2^w_i, exact as a double */
  static double cth=-1, clq; if(th!=cth){ cth=th; clq=m_log1p(-th); } double lq=clq;   /* log1p(-th) depends on th only */
  double mu=(L_*Tb)*th; double k=(double)(U-L_);
  if(k<=mu) return -1;                    /* (the bin sum is skipped: it does not change the result) */
  double s=0.0, c1=lq*W, eprev=e_exp(c1*0.0);
  for(long a=1;a<=J;a+=4096){
    long b= a+4096<J+1? a+4096 : J+1; long n=b-a;
    for(long i=0;i<n;i++){ double j=(double)(a+i);
      double ej=e_exp(c1*j); double pj=eprev-ej; eprev=ej;
      double ee=L_*(Tb-j*W); if(!(ee>0)) ee= (ee!=ee)? ee : 0.0;  /* np.maximum(x, 0) */
      double x=-(ee*ee)/P257;
      vbuf[i]=pj*-e_expm1(x); }
    s+=pw_sum(vbuf,n); }
  double E=L_*Tb; double LRC=(double)J*W;
  double f6=((2*-m_expm1(-E*E/d_pow2(257)))*m_exp(LRC*lq))*(1+LRC*th);
  double e2=m_exp(-mu+k*(1+m_log(mu/k)));
  double e3=(double)U/((th*th)*d_pow2(256));
  double e4=(double)((u64)U*(u64)U)*d_pow2(-(int)(KK+1));
  return s-((((f6+e2)+e3)+d_pow2(-90))+e4);
}
static int ftb(double th, u64 w_i, long J, int HF, double *out){
  double cap=((double)(U-L_)/(L_*th))*0.999; double t=1.4142135623730951*d_pow2(119) /* = 2.0**119.5 */; double lo=0; int have=0;
  double lim= cap<d_pow2(121)? cap : d_pow2(121);
  for(;;){ if(!(t<=lim)) return 0;
    if(fsucc(t,th,w_i,J,HF)>=0.3902) break;
    lo=t; have=1; t*=1.005; }
  double hi=t; if(!have || lo==0) lo=t/1.005;
  for(int i=0;i<50;i++){ double mid=(lo+hi)/2; if(fsucc(mid,th,w_i,J,HF)>=0.3902) hi=mid; else lo=mid; }
  *out=hi; return 1; }
static i64 pyround(double x){ double r=(x+4503599627370496.0)-4503599627370496.0; CHECK(x>=0 && x<4503599627370496.0,"round range"); return (i64)r; }

/* exact success (Decimal in cert4.py) */
static F F039;
static int success(B Tb, int HF, int DK, i64 DT, int wsh, long J, F *pout){
  CNT_EE++; CNT_EB+=(u64)J;
  int tsh=HF+DK;
  F theta=b_shl(b_u((u64)DT),FB-tsh);
  F lq=f_ln(b_sub(ONE,theta));
  F mu=b_shl(b_mulu(b_mulu(Tb,(u64)DT),256),FB-tsh);
  i64 k=U-L_;
  if(f_cmp(f_int(k),mu)<=0){ *pout=f_int(-1); return 0; }
  F s=b_u(0), qprev=ONE;
  for(long j=1;j<=J;j++){
    F arg=f_shl(f_mulu(lq,(u64)j),wsh);
    F qj=f_exp(arg);
    B jw=b_shl(b_u((u64)j),wsh);
    if(b_cmp(Tb,jw)<=0) break;           /* e <= 0 from here on: no further terms */
    B e=b_shl(b_sub(Tb,jw),8);
    B ee=b_mul(e,b_sub(e,b_u(1)));
    CHECK(b_bitlen(ee)+FB-257<=8*64-2,"e range");
    F xf=b_shl(ee,FB-257+0);            /* e(e-1)/(2 n), n = 2^256: shift by 448-257 = 191 */
    s=b_add(s,f_mul(b_sub(qprev,qj),b_sub(ONE,f_exp(f_neg(xf)))));
    qprev=qj; }
  B E=b_shl(Tb,8);
  F lrclq=f_shl(f_mulu(lq,(u64)J),wsh);
  F lrcth=b_shl(b_u((u64)J*(u64)DT),FB+wsh-tsh);
  F G6=f_mul(f_exp(lrclq),b_add(ONE,lrcth));
  F a=b_shl(b_mul(E,E),FB-257);
  F En=b_shl(E,FB-256);                  /* E / n */
  F b3=f_divu(f_mul(a,En),3); b3=b_shl(b3,1);   /* E^3/(3 n^2) = (E^2/(2n)) (E/n) 2/3 */
  F Ghi=b_sub(ONE,f_exp(f_neg(b_add(a,b3))));
  F infl=f_exp(f_neg(f_mulu(f_ln(b_sub(ONE,En)),(u64)U)));
  F e6=f_shl(f_mul(f_mul(G6,Ghi),infl),1);
  F mk=f_divu(mu,(u64)k);
  F e2a=b_add(f_neg(mu),f_mulu(b_add(ONE,f_ln(mk)),(u64)k));
  F e2= f_cmp(e2a,f_int(-320))<0? b_u(0) : f_exp(e2a);
  int sh3=FB+2*tsh-256; F e3=b_divu(b_shl(b_u((u64)U),sh3),(u64)(DT*DT),0);
  F e4=b_add(b_shl(b_u(1),FB-90),b_shl(b_u((u64)U*(u64)U),FB-(int)(KK+1)));
  F e60=b_shl(b_u(1),FB-60);              /* e5 = 2^-1000 lies below the fixed-point resolution */
  F p=b_sub(s,b_add(b_add(b_add(b_add(e2,e3),e4),e6),e60));
  *pout=p; return f_cmp(p,F039)>=0;
}
static B b_dbl_trunc(double d){         /* int(d), d >= 0 */
  u64 u=d_u(d); int ex=(int)((u>>52)&2047); if(ex<1023) return b_u(0); u64 m=(u&((1UL<<52)-1))|(1UL<<52); int e=ex-1075;
  return e>=0? b_shl(b_u(m),e) : b_u(m>>(-e)); }
static B b_floorG(B x, int g){ return b_shl(b_shr(x,g),g); }

static char jbuf[4096]; static int jl;
static void js(const char *s){ while(*s) jbuf[jl++]=*s++; }
static void ju(u64 v){ char t[24]; int n=0; do{ t[n++]='0'+v%10; v/=10; }while(v); while(n) jbuf[jl++]=t[--n]; }
static void jkv(const char *k, u64 v, int last){ js(" \""); js(k); js("\": "); ju(v); js(last? "\n" : ",\n"); }
static void jkb(const char *k, B v, int last){ char d[170]; b_dec(v,d); js(" \""); js(k); js("\": "); js(d); js(last? "\n" : ",\n"); }
static void wfile(const char *p, const char *b, long n){ int fo=(int)sc3(2,(i64)p,01|0100|01000,0644); if(fo<0) die("open out"); sc3(1,fo,(i64)b,n); sc3(3,fo,0,0); }

static long vmhwm(void){
  long hwm=-1; static char st[2048]; int fd=(int)sc3(2,(i64)"/proc/self/status",0,0);
  if(fd>=0){ long n=sc3(0,fd,(i64)st,sizeof st-1); sc3(3,fd,0,0); if(n>0){ st[n]=0;
    for(long i=0;i+6<n;i++) if(st[i]=='V'&&st[i+1]=='m'&&st[i+2]=='H'&&st[i+3]=='W'&&st[i+4]=='M'){ long j=i+6,v=0; while(st[j]==' '||st[j]==9) j++; while(st[j]>='0'&&st[j]<='9') v=v*10+(st[j++]-'0'); hwm=v; break; } } }
  return hwm; }

#ifndef REGS
#define REGS 1936   /* the declared register file: the registers the straight line names + 11 */
#endif
static int work(int argc, char **argv){
  CHECK(argc>=6,"usage: scan ledger.txt counts.txt params.json scan_counts.txt ta|st [S]");
  ST= argv[5][0]=='s' && argv[5][1]=='t'; CHECK(ST || (argv[5][0]=='t'&&argv[5][1]=='a'),"variant: ta or st");
  slurp(argv[1],led,sizeof led); slurp(argv[2],cnt,sizeof cnt);
  c_load(); P257=d_pow2(257);
  { F t=b_divu(b_mulu(ONE,39),100,0); F039=t; }
  /* ledger: one chain step */
  { const char *p=led; const char *key="one chain step, "; int hit=0; for(;*p;p++) if(startsw(p,key)){ p+=16; i64 v=0; while(*p>='0'&&*p<='9') v=v*10+(*p++-'0'); NR=v; hit=1; break; } CHECK(hit,"ledger rounds"); }
  i64 XOR=(i64)ledkey("XOR"), AND=(i64)ledkey("AND"), OR=(i64)ledkey("OR"), NOT=(i64)ledkey("NOT"), TOT=(i64)ledkey("TOTAL");
  i64 LINE=XOR+AND+OR+NOT; CHECK(LINE==TOT,"ledger total");
  BSTEP=LINE+15+2+3; UNIT=271*NR;
  /* counts */
  u64 sl=need(cnt,"sl_bytes",1), ob=need(cnt,"other_bytes",1); HIT=need(cnt,"hit",1);
  i64 fixed=32*REGS+(i64)sl+(i64)ob+0+(ST? 32*256 : 32*512)+32*16;
  S=(1048576-fixed)/32/8*8;
  while(S+100 >= (1L<<(64-__builtin_clzl((u64)S)))) S-=8;
  if(argc>6){ i64 v=0; for(const char *q=argv[6];*q;q++) v=v*10+(*q-'0'); if(v) S=v; }
  U=5*S;
  if(ST){ u64 rr=need(cnt,"replay_rate",1), rg=need(cnt,"replay_g",1), rn=need(cnt,"replay_nck",1);
    REP=(double)rr+(double)(rg+rn)/(double)(S-1); }
  else { REPI_TA=need(cnt,"meas_iter",1)+need(cnt,"replay_iter",1); }
  const int DK=10;
  /* coarse grid */
  double bestl=0; int bHF=0; i64 bDT=0; long bJ=0; double btb=0; int have=0;
  for(int HF=109;HF<117;HF++){ int wsh=HF-8; double w=d_pow2(wsh);
    for(i64 DT=(1<<(DK-1))+16; DT<(1<<DK); DT+=32){ double th=(double)DT/d_pow2(HF+DK);
      for(int kap2=16;kap2<28;kap2++){
        long J=(long)pyround((((double)kap2/2)/th)/w);
        double tb; if(!ftb(th,(u64)wsh,J,HF,&tb)) continue;
        double N1=tb*(double)BSTEP, N2;
        if(ST) N2=(REP*(double)J)*w; else N2=(double)(REPI_TA*(u64)J)*w;
        double N=(N1+N2)+(tb/256)*(double)HIT;
        double l2=N;   /* cert4.py sorts by log2(N / UNIT): the same order, ties then by HF, DT, J, tb */
        int better=!have || l2<bestl || (l2==bestl && (HF<bHF || (HF==bHF && (DT<bDT || (DT==bDT && (J<bJ || (J==bJ && tb<btb)))))));
        if(better){ bestl=l2; bHF=HF; bDT=DT; bJ=J; btb=tb; have=1; } } } }
  CHECK(have,"no feasible grid point");
  /* refine */
  int HF=bHF; int wsh=HF-12; double w=d_pow2(wsh);
  double kap0=(((double)bJ*d_pow2(HF-8))*(double)bDT)/d_pow2(HF+DK);
  double bN=0; i64 DT=0; long J=0; double tbf=0; have=0;
  i64 dlo=(1<<(DK-1))+1; if(bDT-24>dlo) dlo=bDT-24; i64 dhi=(1<<DK)-1; if(bDT+24<dhi) dhi=bDT+24;
  long k4=(long)(4*kap0);
  for(i64 dt=dlo; dt<=dhi; dt+=2){ double th=(double)dt/d_pow2(HF+DK);
    for(long kap4=k4-4; kap4<k4+5; kap4++){
      long j=(long)pyround((((double)kap4/4)/th)/w);
      double tb; if(!ftb(th,(u64)wsh,j,HF,&tb)) continue;
      double N1=tb*(double)BSTEP, N2;
      if(ST) N2=(REP*(double)j)*w; else N2=(double)(REPI_TA*(u64)j)*w;
      double N=(N1+N2)+(tb/256)*(double)HIT;
      if(!have || N<bN){ bN=N; DT=dt; J=j; tbf=tb; have=1; } } }
  CHECK(have,"no feasible refine point");
  /* exact Tb */
  int g=HF-20; F p;
  B lo=b_floorG(b_dbl_trunc(tbf*0.9995),g), hi=b_floorG(b_dbl_trunc(tbf*1.0005),g);
  while(!success(hi,HF,DK,DT,wsh,J,&p)) hi=b_add(hi,b_sub(hi,lo));
  while(success(lo,HF,DK,DT,wsh,J,&p)) lo=b_sub(lo,b_sub(hi,lo));
  lo=b_floorG(lo,g); hi=b_floorG(hi,g);
  B Gb=b_shl(b_u(1),g);
  while(b_cmp(b_sub(hi,lo),Gb)>0){ B mid=b_floorG(b_shr(b_add(lo,hi),1),g); if(success(mid,HF,DK,DT,wsh,J,&p)) hi=mid; else lo=mid; }
  B TB=hi;
  B Wb=b_shl(b_u(1),wsh); B LRC=b_mulu(Wb,(u64)J);
  B HMAX=b_add(b_add(b_shr(b_mulu(TB,(1UL<<20)+1),28),b_u(1)),LRC);
  int SB=64-__builtin_clzl((u64)S);
  jl=0; js("{\n");
  jkv("NR",(u64)NR,0); jkv("HF",(u64)HF,0); jkv("DPLO",(u64)(256-HF),0); jkv("DK",(u64)DK,0); jkv("DT",(u64)DT,0);
  jkv("S",(u64)S,0); jkv("U",(u64)U,0); jkv("SB",(u64)SB,0); jkb("W",Wb,0); jkv("J",(u64)J,0); jkb("LRC",LRC,0);
  jkb("Tb",TB,0); jkb("HMAX",HMAX,0); jkv("PFLO",240,0); jkv("PFN",16,1); js("}");
  wfile(argv[3],jbuf,jl);
  jl=0; js("float_evals "); ju(CNT_FE); js("\nfloat_bins "); ju(CNT_FB); js("\nexact_evals "); ju(CNT_EE); js("\nexact_bins "); ju(CNT_EB); js("\n");
  wfile(argv[4],jbuf,jl);
  os("scan ("); os(ST? "st" : "ta"); os("): HF "); ou((u64)HF); os(" DT "); ou((u64)DT); os(" J "); ou((u64)J); os(" S "); ou((u64)S);
  os(" Tb/2^"); ou((u64)g); os(" "); { char d[170]; b_dec(b_shr(TB,g),d); os(d); }
  os("; float evaluations "); ou(CNT_FE); os(" bins "); ou(CNT_FB); os(", exact evaluations "); ou(CNT_EE); os(" bins "); ou(CNT_EB); oc('\n');
  os("scan peak RSS (VmHWM, this process image) "); ou((u64)vmhwm()); os(" KiB\n"); oflush();
  return 0;
}
int cmain(long *sp){
  int argc=(int)sp[0]; char **argv=(char**)(sp+1);
#ifdef TABGEN
  (void)argc; (void)argv; return tabgen();
#endif
  i64 pid=sc3(57,0,0,0);
  if(pid==0){ int rc=work(argc,argv); oflush(); sc3(60,rc,0,0); }
  if(pid<0) die("fork");
  struct { long ut[2], st[2]; long maxrss, rest[14]; } ru; int status=0;
  { i64 r; register i64 r10 __asm__("r10")=(i64)&ru; __asm__ volatile("syscall":"=a"(r):"a"(61L),"D"(pid),"S"((i64)&status),"d"(0L),"r"(r10):"rcx","r11","memory"); (void)r; }
  os("worker peak RSS (getrusage via wait4, worker forked from the 1-page parent) "); ou((u64)ru.maxrss); os(" KiB = "); ou((u64)ru.maxrss*1024); os(" bytes (limit 1048576)\n"); oflush();
  return ((status>>8)&255);
}
```

```c
/* scan_tab.h - written by the TABGEN build of scan.c (448-bit fixed point; doubles rounded to nearest) */
static const u64 T_LN2[8]={0xed2eae35c1382070UL,0x559552fb4afa1b10UL,0xe7b876206debac98UL,0x8a0d175b8baafa2bUL,0x40f343267298b62dUL,0xc9e3b39803f2f6afUL,0xb17217f7d1cf79abUL,0x0000000000000000UL};
static const u64 T_INVLN2[8]={0xd52173cc189522faUL,0x49b25eeb82d7c167UL,0xbc3887eeaa2ed9acUL,0x164a2cd9a342648fUL,0xd6aef551bad2b4b1UL,0x7d0ffda0d23a7d11UL,0x71547652b82fe177UL,0x0000000000000001UL};
static const u64 T_IFACT[][8]={
{0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000001UL},
{0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000001UL},
{0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x0000000000000000UL,0x8000000000000000UL,0x0000000000000000UL},
{0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0x2aaaaaaaaaaaaaaaUL,0x0000000000000000UL},
{0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0xaaaaaaaaaaaaaaaaUL,0x0aaaaaaaaaaaaaaaUL,0x0000000000000000UL},
{0x2222222222222222UL,0x2222222222222222UL,0x2222222222222222UL,0x2222222222222222UL,0x2222222222222222UL,0x2222222222222222UL,0x0222222222222222UL,0x0000000000000000UL},
{0xb05b05b05b05b05bUL,0x5b05b05b05b05b05UL,0x05b05b05b05b05b0UL,0xb05b05b05b05b05bUL,0x5b05b05b05b05b05UL,0x05b05b05b05b05b0UL,0x005b05b05b05b05bUL,0x0000000000000000UL},
{0xd00d00d00d00d00dUL,0x0d00d00d00d00d00UL,0x00d00d00d00d00d0UL,0xd00d00d00d00d00dUL,0x0d00d00d00d00d00UL,0x00d00d00d00d00d0UL,0x000d00d00d00d00dUL,0x0000000000000000UL},
{0x1a01a01a01a01a01UL,0x01a01a01a01a01a0UL,0xa01a01a01a01a01aUL,0x1a01a01a01a01a01UL,0x01a01a01a01a01a0UL,0xa01a01a01a01a01aUL,0x0001a01a01a01a01UL,0x0000000000000000UL},
{0xe671f5583911ca00UL,0x1ca002e3bc74aad8UL,0x4aad8e671f558391UL,0x583911ca002e3bc7UL,0xe3bc74aad8e671f5UL,0x671f5583911ca002UL,0x00002e3bc74aad8eUL,0x0000000000000000UL},
{0x4a3e9888d281c766UL,0x82dccd16c60baaafUL,0x21115b0a4feef38eUL,0x559f4e943337d2c7UL,0xe392d8777c170b65UL,0xd71cbbc05b4fa999UL,0x0000049f93edde27UL,0x0000000000000000UL},
{0xc0ee6af52a68e394UL,0x232b58766f185555UL,0x8ea47ca3d8b8a1c7UL,0xaab1643c04a7fbe3UL,0x71c7880adcbc46daUL,0x138e3f9d1f92e0dfUL,0x0000006b99159fd5UL,0x0000000000000000UL},
{0xd013de3f18de12f7UL,0xed98f209de975c71UL,0xf68db50da764b825UL,0xe38ec85a55b8aa52UL,0xf425f600e7ba5b3cUL,0x6c4bdaa26d4c3d67UL,0x00000008f76c77fcUL,0x0000000000000000UL},
{0x7277aea2645fda13UL,0x25f8129e4c33071cUL,0x12f7354fd1ccabb4UL,0x38e3994206980d1aUL,0xd7b4269d9babdfa2UL,0x43684be51c198e91UL,0x00000000b092309dUL,0x0000000000000000UL},
{0x75e3fa302bbdb425UL,0xde2401547328375dUL,0x93a3f185b38e9e8cUL,0xbaebaf84b75400efUL,0xfd1f2754668c46d4UL,0x603e4e905d6f8a2eUL,0x000000000c9cba54UL,0x0000000000000000UL},
{0xb286aa477a61faf1UL,0xa868cce37f24d07dUL,0xc5937680614dc64dUL,0x83ed943c0c38ccdcUL,0x774657f48f5eaf63UL,0x399dc0f88ec32b58UL,0x0000000000d73f9fUL,0x0000000000000000UL},
{0xdb286aa477a61fafUL,0xda868cce37f24d07UL,0xcc5937680614dc64UL,0x383ed943c0c38ccdUL,0x8774657f48f5eaf6UL,0xf399dc0f88ec32b5UL,0x00000000000d73f9UL,0x0000000000000000UL},
{0xfdd533731618d4afUL,0x855335758ad20487UL,0x938cc7061e79b29cUL,0xd621d08b83cf4484UL,0xcbbb8d7ff53ba468UL,0x3b81856a53593028UL,0x000000000000ca96UL,0x0000000000000000UL},
{0xc6fd9f4d813a44b4UL,0xeaf6668687b65595UL,0x24a443f21e233496UL,0xef73a807c0362e79UL,0x4435161554bc33ccUL,0x3c31dcbecbbdd802UL,0x0000000000000b41UL,0x0000000000000000UL},
{0x76433e47729746fcUL,0x2750563cf9ab47dfUL,0x88aa546b0f0f539cUL,0xa0d03143c6bf7bb5UL,0xf61dbdcb3a5abf5bUL,0xa4da340a0ab92650UL,0x0000000000000097UL,0x0000000000000000UL},
{0x5f835cb6c5bac38cUL,0x685d9de972e229feUL,0xe06eea9ef3f3f761UL,0xc80a68dcfd232c95UL,0x72b4afe3c2eaeff7UL,0x950ae900808941eaUL,0x0000000000000007UL,0x0000000000000000UL},
{0x291ea2e421cbf0eeUL,0x8b10a5feed16f5cfUL,0x7866ce3854c2797eUL,0x21e81d5fdb4ad15cUL,0xbc51bf3b9b914861UL,0x5c6e3bdb73d5c62fUL,0x0000000000000000UL,0x0000000000000000UL},
{0xdef5c19601894522UL,0x1d98078b9669c55aUL,0x4b4a7dbcbe08d6faUL,0xdea1d2ca2ce07de1UL,0x143242dfcce3b1d5UL,0x04338e5b6dfe14a5UL,0x0000000000000000UL,0x0000000000000000UL},
{0xe84d77b89be493b3UL,0x6575ea11330fbaaaUL,0xcb9f1098e6defe37UL,0x09adfe08ca4c8b09UL,0xb2f70e09bafec4f3UL,0x002ec368262c7033UL,0x0000000000000000UL,0x0000000000000000UL},
{0x74588fa7b1298627UL,0x4ee4e9c0b775fd1cUL,0x687bf6065ef3f542UL,0x20673feb086ddb20UL,0x7cca4b4067ca9d8aUL,0x0001f2cf01972f57UL,0x0000000000000000UL,0x0000000000000000UL},
{0xa87e6c256d7c8a7cUL,0x2c1da2f33a89d6ecUL,0x4bdbff99dad68eeeUL,0x0b893fff294c1301UL,0xa8d4e44a419776f1UL,0x000013f3ccdd165fUL,0x0000000000000000UL,0x0000000000000000UL},
{0x9053a1b2ab987b7aUL,0x3cc6101d0c18fe6bUL,0x3425fffc12435444UL,0x0a4a33b132d1b1f6UL,0x72cd1c790285d358UL,0x000000c4742fe352UL,0x0000000000000000UL,0x0000000000000000UL}};
static const u64 T_ET[128]={
0x3ff0000000000000UL,0x3ff0163da9fb3335UL,0x3ff02c9a3e778061UL,0x3ff04315e86e7f85UL,
0x3ff059b0d3158574UL,0x3ff0706b29ddf6deUL,0x3ff0874518759bc8UL,0x3ff09e3ecac6f383UL,
0x3ff0b5586cf9890fUL,0x3ff0cc922b7247f7UL,0x3ff0e3ec32d3d1a2UL,0x3ff0fb66affed31bUL,
0x3ff11301d0125b51UL,0x3ff12abdc06c31ccUL,0x3ff1429aaea92de0UL,0x3ff15a98c8a58e51UL,
0x3ff172b83c7d517bUL,0x3ff18af9388c8deaUL,0x3ff1a35beb6fcb75UL,0x3ff1bbe084045cd4UL,
0x3ff1d4873168b9aaUL,0x3ff1ed5022fcd91dUL,0x3ff2063b88628cd6UL,0x3ff21f49917ddc96UL,
0x3ff2387a6e756238UL,0x3ff251ce4fb2a63fUL,0x3ff26b4565e27cddUL,0x3ff284dfe1f56381UL,
0x3ff29e9df51fdee1UL,0x3ff2b87fd0dad990UL,0x3ff2d285a6e4030bUL,0x3ff2ecafa93e2f56UL,
0x3ff306fe0a31b715UL,0x3ff32170fc4cd831UL,0x3ff33c08b26416ffUL,0x3ff356c55f929ff1UL,
0x3ff371a7373aa9cbUL,0x3ff38cae6d05d866UL,0x3ff3a7db34e59ff7UL,0x3ff3c32dc313a8e5UL,
0x3ff3dea64c123422UL,0x3ff3fa4504ac801cUL,0x3ff4160a21f72e2aUL,0x3ff431f5d950a897UL,
0x3ff44e086061892dUL,0x3ff46a41ed1d0057UL,0x3ff486a2b5c13cd0UL,0x3ff4a32af0d7d3deUL,
0x3ff4bfdad5362a27UL,0x3ff4dcb299fddd0dUL,0x3ff4f9b2769d2ca7UL,0x3ff516daa2cf6642UL,
0x3ff5342b569d4f82UL,0x3ff551a4ca5d920fUL,0x3ff56f4736b527daUL,0x3ff58d12d497c7fdUL,
0x3ff5ab07dd485429UL,0x3ff5c9268a5946b7UL,0x3ff5e76f15ad2148UL,0x3ff605e1b976dc09UL,
0x3ff6247eb03a5585UL,0x3ff6434634ccc320UL,0x3ff6623882552225UL,0x3ff68155d44ca973UL,
0x3ff6a09e667f3bcdUL,0x3ff6c012750bdabfUL,0x3ff6dfb23c651a2fUL,0x3ff6ff7df9519484UL,
0x3ff71f75e8ec5f74UL,0x3ff73f9a48a58174UL,0x3ff75feb564267c9UL,0x3ff780694fde5d3fUL,
0x3ff7a11473eb0187UL,0x3ff7c1ed0130c132UL,0x3ff7e2f336cf4e62UL,0x3ff80427543e1a12UL,
0x3ff82589994cce13UL,0x3ff8471a4623c7adUL,0x3ff868d99b4492edUL,0x3ff88ac7d98a6699UL,
0x3ff8ace5422aa0dbUL,0x3ff8cf3216b5448cUL,0x3ff8f1ae99157736UL,0x3ff9145b0b91ffc6UL,
0x3ff93737b0cdc5e5UL,0x3ff95a44cbc8520fUL,0x3ff97d829fde4e50UL,0x3ff9a0f170ca07baUL,
0x3ff9c49182a3f090UL,0x3ff9e86319e32323UL,0x3ffa0c667b5de565UL,0x3ffa309bec4a2d33UL,
0x3ffa5503b23e255dUL,0x3ffa799e1330b358UL,0x3ffa9e6b5579fdbfUL,0x3ffac36bbfd3f37aUL,
0x3ffae89f995ad3adUL,0x3ffb0e07298db666UL,0x3ffb33a2b84f15fbUL,0x3ffb59728de5593aUL,
0x3ffb7f76f2fb5e47UL,0x3ffba5b030a1064aUL,0x3ffbcc1e904bc1d2UL,0x3ffbf2c25bd71e09UL,
0x3ffc199bdd85529cUL,0x3ffc40ab5fffd07aUL,0x3ffc67f12e57d14bUL,0x3ffc8f6d9406e7b5UL,
0x3ffcb720dcef9069UL,0x3ffcdf0b555dc3faUL,0x3ffd072d4a07897cUL,0x3ffd2f87080d89f2UL,
0x3ffd5818dcfba487UL,0x3ffd80e316c98398UL,0x3ffda9e603db3285UL,0x3ffdd321f301b460UL,
0x3ffdfc97337b9b5fUL,0x3ffe264614f5a129UL,0x3ffe502ee78b3ff6UL,0x3ffe7a51fbc74c83UL,
0x3ffea4afa2a490daUL,0x3ffecf482d8e67f1UL,0x3ffefa1bee615a27UL,0x3fff252b376bba97UL,
0x3fff50765b6e4540UL,0x3fff7bfdad9cbe14UL,0x3fffa7c1819e90d8UL,0x3fffd3c22b8f71f1UL};
static const u64 T_LT[129]={
0x0000000000000000UL,0x3f7fe02a6b106789UL,0x3f8fc0a8b0fc03e4UL,0x3f97b91b07d5b11bUL,
0x3f9f829b0e783300UL,0x3fa39e87b9febd60UL,0x3fa77458f632dcfcUL,0x3fab42dd711971bfUL,
0x3faf0a30c01162a6UL,0x3fb16536eea37ae1UL,0x3fb341d7961bd1d1UL,0x3fb51b073f06183fUL,
0x3fb6f0d28ae56b4cUL,0x3fb8c345d6319b21UL,0x3fba926d3a4ad563UL,0x3fbc5e548f5bc743UL,
0x3fbe27076e2af2e6UL,0x3fbfec9131dbeabbUL,0x3fc0d77e7cd08e59UL,0x3fc1b72ad52f67a0UL,
0x3fc29552f81ff523UL,0x3fc371fc201e8f74UL,0x3fc44d2b6ccb7d1eUL,0x3fc526e5e3a1b438UL,
0x3fc5ff3070a793d4UL,0x3fc6d60fe719d21dUL,0x3fc7ab890210d909UL,0x3fc87fa06520c911UL,
0x3fc9525a9cf456b4UL,0x3fca23bc1fe2b563UL,0x3fcaf3c94e80bff3UL,0x3fcbc286742d8cd6UL,
0x3fcc8ff7c79a9a22UL,0x3fcd5c216b4fbb91UL,0x3fce27076e2af2e6UL,0x3fcef0adcbdc5936UL,
0x3fcfb9186d5e3e2bUL,0x3fd0402594b4d041UL,0x3fd0a324e27390e3UL,0x3fd1058bf9ae4ad5UL,
0x3fd1675cababa60eUL,0x3fd1c898c16999fbUL,0x3fd22941fbcf7966UL,0x3fd2895a13de86a3UL,
0x3fd2e8e2bae11d31UL,0x3fd347dd9a987d55UL,0x3fd3a64c556945eaUL,0x3fd404308686a7e4UL,
0x3fd4618bc21c5ec2UL,0x3fd4be5f957778a1UL,0x3fd51aad872df82dUL,0x3fd5767717455a6cUL,
0x3fd5d1bdbf5809caUL,0x3fd62c82f2b9c795UL,0x3fd686c81e9b14afUL,0x3fd6e08eaa2ba1e4UL,
0x3fd739d7f6bbd007UL,0x3fd792a55fdd47a2UL,0x3fd7eaf83b82afc3UL,0x3fd842d1da1e8b17UL,
0x3fd89a3386c1425bUL,0x3fd8f11e873662c7UL,0x3fd947941c2116fbUL,0x3fd99d958117e08bUL,
0x3fd9f323ecbf984cUL,0x3fda484090e5bb0aUL,0x3fda9cec9a9a084aUL,0x3fdaf1293247786bUL,
0x3fdb44f77bcc8f63UL,0x3fdb9858969310fbUL,0x3fdbeb4d9da71b7cUL,0x3fdc3dd7a7cdad4dUL,
0x3fdc8ff7c79a9a22UL,0x3fdce1af0b85f3ebUL,0x3fdd32fe7e00ebd5UL,0x3fdd83e7258a2f3eUL,
0x3fddd46a04c1c4a1UL,0x3fde24881a7c6c26UL,0x3fde744261d68788UL,0x3fdec399d2468cc0UL,
0x3fdf128f5faf06edUL,0x3fdf6123fa7028acUL,0x3fdfaf588f78f31fUL,0x3fdffd2e0857f498UL,
0x3fe02552a5a5d0ffUL,0x3fe04bdf9da926d2UL,0x3fe0723e5c1cdf40UL,0x3fe0986f4f573521UL,
0x3fe0be72e4252a83UL,0x3fe0e44985d1cc8cUL,0x3fe109f39e2d4c97UL,0x3fe12f719593efbcUL,
0x3fe154c3d2f4d5eaUL,0x3fe179eabbd899a1UL,0x3fe19ee6b467c96fUL,0x3fe1c3b81f713c25UL,
0x3fe1e85f5e7040d0UL,0x3fe20cdcd192ab6eUL,0x3fe23130d7bebf43UL,0x3fe2555bce98f7cbUL,
0x3fe2795e1289b11bUL,0x3fe29d37fec2b08bUL,0x3fe2c0e9ed448e8cUL,0x3fe2e47436e40268UL,
0x3fe307d7334f10beUL,0x3fe32b1339121d71UL,0x3fe34e289d9ce1d3UL,0x3fe37117b54747b6UL,
0x3fe393e0d3562a1aUL,0x3fe3b68449fffc23UL,0x3fe3d9026a7156fbUL,0x3fe3fb5b84d16f42UL,
0x3fe41d8fe84672aeUL,0x3fe43f9fe2f9ce67UL,0x3fe4618bc21c5ec2UL,0x3fe48353d1ea88dfUL,
0x3fe4a4f85db03ebbUL,0x3fe4c679afccee3aUL,0x3fe4e7d811b75bb1UL,0x3fe50913cc01686bUL,
0x3fe52a2d265bc5abUL,0x3fe54b2467999498UL,0x3fe56bf9d5b3f399UL,0x3fe58cadb5cd7989UL,
0x3fe5ad404c359f2dUL,0x3fe5cdb1dc6c1765UL,0x3fe5ee02a9241675UL,0x3fe60e32f44788d9UL,
0x3fe62e42fefa39efUL};
static const u64 T_E[4]={0x40671547652b82feUL,0x3f762e42fef00000UL,0x3d6473de6af278edUL,0x3fe62e42fefa39efUL};
static const u64 T_C[14]={
0x3ff0000000000000UL,0x3ff0000000000000UL,0x3fe0000000000000UL,0x3fc5555555555555UL,
0x3fa5555555555555UL,0x3f81111111111111UL,0x3f56c16c16c16c17UL,0x3f2a01a01a01a01aUL,
0x3efa01a01a01a01aUL,0x3ec71de3a556c734UL,0x3e927e4fb7789f5cUL,0x3e5ae64567f544e4UL,
0x3e21eed8eff8d898UL,0x3de6124613a86d09UL};
```

### D.6 other_dx.c (the assembly O, compiled with -DDESIGNX)

```c
/* other.c - freestanding C port of other4.py build (the assembler O): reads params.json, writes other.bin
 * (8-byte instruction words, bits 0-4 op, 5 L, 6-16 d, 17-27 a, 28-38 b, 39-63 imm; then the literal pool,
 * distinct immediates >= 2^25 as 32-byte little-endian words in order of first use).
 * No libc; static arrays only; the work runs in a forked child, the parent reports its peak RSS (wait4 ru_maxrss),
 * the child reports its own VmHWM.  Usage: other [params.json] [other.bin] */
typedef unsigned long u64; typedef long i64; typedef unsigned char u8;
__asm__(".global _start\n_start:\n xor %rbp,%rbp\n mov %rsp,%rdi\n and $-16,%rsp\n call cmain\n mov %rax,%rdi\n mov $60,%rax\n syscall\n");
static i64 sc3(i64 n, i64 a, i64 b, i64 c){ i64 r; __asm__ volatile("syscall":"=a"(r):"a"(n),"D"(a),"S"(b),"d"(c):"rcx","r11","memory"); return r; }
void *memset(void *d, int c, unsigned long n){ u8 *p=d; while(n--) *p++=(u8)c; return d; }
void *memcpy(void *d, const void *s, unsigned long n){ u8 *p=d; const u8 *q=s; while(n--) *p++=*q++; return d; }
static int fd_out=1; static char obuf[512]; static int olen;
static void oflush(void){ if(olen){ sc3(1,fd_out,(i64)obuf,olen); olen=0; } }
static void oc(char c){ if(olen==512) oflush(); obuf[olen++]=c; }
static void os(const char *s){ while(*s) oc(*s++); }
static void ou(u64 v){ char t[24]; int n=0; do{ t[n++]='0'+v%10; v/=10; }while(v); while(n) oc(t[--n]); }
static void die(const char *m){ oflush(); fd_out=2; os("other: "); os(m); oc('\n'); oflush(); sc3(60,1,0,0); }

/* ---- 256-bit values ---- */
typedef struct { u64 w[4]; } U;
static U u_small(u64 v){ U r={{v,0,0,0}}; return r; }
static U u_shl(U a, int s){ U r={{0,0,0,0}}; for(int i=3;i>=0;i--){ int q=s/64, b=s%64; if(i-q<0) continue;
  r.w[i]=a.w[i-q]<<b; if(b && i-q-1>=0) r.w[i]|=a.w[i-q-1]>>(64-b); } return r; }
static U u_add(U a, U b){ U r; u64 c=0; for(int i=0;i<4;i++){ u64 s=a.w[i]+c; c=s<c; r.w[i]=s+b.w[i]; c+=r.w[i]<s; } return r; }
static U u_sub(U a, U b){ U r; u64 br=0; for(int i=0;i<4;i++){ u64 t=a.w[i]-b.w[i]; u64 b1=a.w[i]<b.w[i]; r.w[i]=t-br; u64 b2=t<br; br=b1|b2; } return r; }
static U u_mask(int k){ return u_sub(u_shl(u_small(1),k),u_small(1)); }  /* 2^k - 1, k < 256 */
static int u_eq(U a, U b){ return a.w[0]==b.w[0]&&a.w[1]==b.w[1]&&a.w[2]==b.w[2]&&a.w[3]==b.w[3]; }
static U u_div1(U a, u64 d, u64 *rem){ U q; unsigned __int128 r=0; for(int i=3;i>=0;i--){ r=(r<<64)|a.w[i]; q.w[i]=(u64)(r/d); r%=d; } *rem=(u64)r; return q; }
static int u_big(U a){ return a.w[1]||a.w[2]||a.w[3]||a.w[0]>=(1UL<<25); }

/* ---- params.json ---- */
static char pj[4096];
static U getp(const char *k){
  int n=0; while(k[n]) n++;
  for(int i=0;pj[i];i++){ if(pj[i]!='"') continue; int j=0; while(j<n && pj[i+1+j]==k[j]) j++;
    if(j==n && pj[i+1+n]=='"'){ int p=i+2+n; while(pj[p]==':'||pj[p]==' ') p++; U v=u_small(0);
      while(pj[p]>='0'&&pj[p]<='9'){ U t=u_add(u_shl(v,3),u_shl(v,1)); v=u_add(t,u_small((u64)(pj[p++]-'0'))); } return v; } }
  die("param missing"); return u_small(0);
}

/* ---- assembler ---- */
enum { XOR, AND, OR, NOT, ADD, SUB, SHL, SHR, EQ, LT, MOV, ADDI, SUBI, SHLI, SHRI, ANDI, EQI, LTI, MOVI,
       LD, ST, LDA, BNZ, BZ, JMP, JAL, JR, RND, PERM, HALT };
#ifndef RB0
#define RB0 1925   /* the registers the straight line names (ledger: registers used); the search state takes RB0..RB0+9 */
#endif
enum { C_=RB0, NXT, IDN, RHO, ONES, PF, H, LR, LR2, ZERO };
enum { L_=256, DPM, C1, ACC, TT, REC, SLOT, TR, F_, X_, Y_, LV, NP, NM, ONEB, V_, MN, E_, PTR, SS, ID, STV };
enum { P_=280, Q_, N_, MM, LA, LB, UU, FF, PDR, X0, X1, X2, X3, TQ, FP };
enum { Z_=295, REP=296, W0=300 };
enum { l_start, l_clr, l_iw, l_loop, l_hit, l_h1, l_dpl, l_dp1, l_ct0, l_gather=l_ct0+8, l_record, l_sl_ok, l_probe,
       l_match0, l_pnext=l_match0+5, l_insert, l_ins, l_cont, l_dl, l_restart, l_rs1, l_rs2, l_setwalk, l_sw_planes,
       l_sw_end, l_evalF, l_ef_perm, l_outm, l_match, l_meas, l_measd, l_advp, l_advq, l_advq2, l_lock, l_lloop,
       l_found, l_rfail, l_end, l_ms1, l_al1, l_al2, l_al3, l_al4, l_bl, l_bl1, l_walk0, l_seg, l_sw, l_last, NLAB };
static int STM;  /* 1: the checkpoint-replay variant (fac_st/other4.py): walk words WK = LST | LID << 128 */
enum { NXC=278, IA=279, NX=297, PT2=298, QW=299, LSTB=128 };
#define MAXI 4096
static u64 code[MAXI]; static int ni;
static U lits[64]; static int nlit;
static int lab[NLAB]; static int fixi[1024], fixl[1024]; static int nfix;
static void label(int n){ lab[n]=ni; }
static void eU(int op, int d, int a, int b, U imm, int tgt){
  if(ni>=MAXI) die("code full");
  u64 L=0, f;
  if(u_big(imm)){ int k=0; while(k<nlit && !u_eq(lits[k],imm)) k++; if(k==nlit){ if(nlit==64) die("lits"); lits[nlit++]=imm; } L=1; f=(u64)k; }
  else f=imm.w[0];
  code[ni]=(u64)op | L<<5 | (u64)d<<6 | (u64)a<<17 | (u64)b<<28 | f<<39;
  if(tgt>=0){ fixi[nfix]=ni; fixl[nfix++]=tgt; }
  ni++;
}
static void e(int op, int d, int a, int b, u64 imm){ eU(op,d,a,b,u_small(imm),-1); }
#define xor_(d,a,b) e(XOR,d,a,b,0)
#define and_(d,a,b) e(AND,d,a,b,0)
#define or_(d,a,b) e(OR,d,a,b,0)
#define not_(d,a) e(NOT,d,a,0,0)
#define add_(d,a,b) e(ADD,d,a,b,0)
#define sub_(d,a,b) e(SUB,d,a,b,0)
#define shl_(d,a,b) e(SHL,d,a,b,0)
#define shr_(d,a,b) e(SHR,d,a,b,0)
#define mov_(d,a) e(MOV,d,a,0,0)
#define addi(d,a,i) e(ADDI,d,a,0,i)
#define subi(d,a,i) e(SUBI,d,a,0,i)
#define shli(d,a,i) e(SHLI,d,a,0,i)
#define shri(d,a,i) e(SHRI,d,a,0,i)
#define andi(d,a,i) e(ANDI,d,a,0,i)
#define andiU(d,a,u) eU(ANDI,d,a,0,u,-1)
#define movi(d,i) e(MOVI,d,0,0,i)
#define ld(d,a,i) e(LD,d,a,0,i)
#define st(a,i,b) e(ST,0,a,b,i)
#define lda(d,i) e(LDA,d,0,0,i)
#define halt(c) e(HALT,0,0,0,c)
static void jmp(int t){ eU(JMP,0,0,0,u_small(0),t); }
static void jal(int d,int t){ eU(JAL,d,0,0,u_small(0),t); }
static void br(int op,int t){ eU(op,0,F_,0,u_small(0),t); }
static void jeq(int a,int b,int t){ e(EQ,F_,a,b,0); br(BNZ,t); }
static void jne(int a,int b,int t){ e(EQ,F_,a,b,0); br(BZ,t); }
static void jeqi(int a,U i,int t){ eU(EQI,F_,a,0,i,-1); br(BNZ,t); }
static void jnei(int a,U i,int t){ eU(EQI,F_,a,0,i,-1); br(BZ,t); }
static void jlt(int a,int b,int t){ e(LT,F_,a,b,0); br(BNZ,t); }
static void jlti(int a,U i,int t){ eU(LTI,F_,a,0,i,-1); br(BNZ,t); }
static void jgei(int a,U i,int t){ eU(LTI,F_,a,0,i,-1); br(BZ,t); }
#define S_(v) u_small(v)
static void jge(int a,int b,int t){ e(LT,F_,a,b,0); br(BZ,t); }

static void build_state(u64 MISC){
  for(int i=0;i<7;i++) lda(W0+i,MISC+i);
  U M64=u_mask(64);
#ifdef DESIGNX   /* design X (11565cb4): lanes x and 10+x = v_x ^ K, v_0..v_3 = u_0..u_3, v_4 = XOR_(x<4) rotr(u_x,(39-ROT[x][2]) mod 64); 43 instructions */
  { const int V4=307, T1=308; const int Xs[4]={X0,X1,X2,X3}, sh[4]={36,29,60,14};
    xor_(W0,W0,UU);
    andiU(X0,UU,M64); shri(X1,UU,64); andiU(X1,X1,M64); shri(X2,UU,128); andiU(X2,X2,M64); shri(X3,UU,192);
    for(int k=0;k<4;k++){ if(k==0) shri(V4,Xs[k],sh[k]); else { shri(T1,Xs[k],sh[k]); xor_(V4,V4,T1); }
      shli(T1,Xs[k],64-sh[k]); andiU(T1,T1,M64); xor_(V4,V4,T1); }
    xor_(W0+1,W0+1,V4);
    shli(T1,X0,128); xor_(W0+2,W0+2,T1);
    shli(T1,X1,192); xor_(W0+2,W0+2,T1);
    xor_(W0+3,W0+3,X2);
    shli(T1,X3,64); xor_(W0+3,W0+3,T1);
    shli(T1,V4,128); xor_(W0+3,W0+3,T1);
    return; }
#endif
  andiU(X0,UU,M64); shri(X1,UU,64); andiU(X1,X1,M64); shri(X2,UU,128); andiU(X2,X2,M64); shri(X3,UU,192);
  shli(TQ,X0,64); xor_(W0,W0,TQ);
  shli(TQ,X1,128); xor_(W0+1,W0+1,TQ);
  xor_(W0+1,W0+1,X2);
  shli(TQ,X3,64); xor_(W0+2,W0+2,TQ);
  xor_(TQ,X0,X1); shli(TQ,TQ,192); xor_(W0+2,W0+2,TQ);
  xor_(TQ,X2,X3); shli(TQ,TQ,128); xor_(W0+3,W0+3,TQ);
}

static void program(void){
  const int RB=51, RPW=5, KEYB=50;
  u64 S=getp("S").w[0], Uu=getp("U").w[0], SB=getp("SB").w[0];
  U LRC=getp("LRC"), Tb=getp("Tb"), HMAX=getp("HMAX");
  int DPLO=(int)getp("DPLO").w[0], DK=(int)getp("DK").w[0], PFLO=(int)getp("PFLO").w[0];
  u64 DT=getp("DT").w[0];
  U THR=u_shl(S_(DT),DPLO-DK);
  if(!(S<(1UL<<SB) && S>=264 && S%8==0 && PFLO>DPLO+1 && Uu<=RPW*S && DPLO-DK>KEYB)) die("assert params");
  if(!((DK==0&&DT==1)||(DK>=1&&DT>0&&DT<(1UL<<DK)&&DPLO>=DK))) die("assert DT");
  U ULIM=S_((Uu%S) | ((u64)RB*(Uu/S))<<SB);
  u64 LID=S, LST=S+256, MISC=S+512, WK=S;
  U Gg=S_(0);
  if(STM){ MISC=S+256; u64 rem; Gg=u_div1(LRC,S-1,&rem); if(rem) Gg=u_add(Gg,S_(1));
    if(Tb.w[2]||Tb.w[3]||(ULIM.w[2]||ULIM.w[3])) die("assert st"); }
  u64 OUT=MISC+8;
  label(l_start);
  e(RND,RHO,0,0,0); movi(IDN,256); movi(H,0); movi(C_,0); movi(ZERO,0); not_(ONES,ZERO);
  movi(PTR,0);
  label(l_clr);
  for(int k=0;k<8;k++) st(PTR,k,ZERO);
  addi(PTR,PTR,8); jlti(PTR,S_(S),l_clr);
  movi(L_,0);
  label(l_iw);
  if(STM){ add_(NP,RHO,L_); shli(TT,L_,LSTB); st(L_,WK,TT); jal(LR,l_setwalk); }
  else { add_(NP,RHO,L_); st(L_,LID,L_); st(L_,LST,ZERO); jal(LR,l_setwalk); }
  addi(L_,L_,1); jlti(L_,S_(256),l_iw);
  label(l_loop);
  jeq(PF,ONES,l_cont);
  label(l_hit);
  addi(H,H,1); jlti(H,u_add(HMAX,S_(1)),l_h1); halt(10); label(l_h1);
  or_(SS,DPLO,DPLO+1);
  for(int j=DPLO+2;j<PFLO;j++) or_(SS,SS,j);
  or_(DPM,PF,SS); not_(DPM,DPM);
  if(DK){
    int bits[64], last1=-1, first=1;
    for(int i=0;i<DK;i++){ bits[i]=(int)((DT>>(DK-1-i))&1); if(bits[i]) last1=i; }
    for(int i=0;i<=last1;i++){
      int p=DPLO-1-i;
      not_(X_,p);
      if(bits[i]){
        if(first){ and_(Y_,DPM,X_); first=0; }
        else { and_(X_,DPM,X_); or_(Y_,Y_,X_); }
        if(i<last1) and_(DPM,DPM,p);
      } else and_(DPM,DPM,X_);
    }
    mov_(DPM,Y_);
  }
  addi(C1,C_,1);
  label(l_dpl);
  jeqi(DPM,S_(0),l_cont);
  label(l_dp1);
  movi(L_,0); mov_(X_,DPM);
  { static const int shs[8]={128,64,32,16,8,4,2,1};
    for(int i=0;i<8;i++){ andiU(Y_,X_,u_mask(shs[i])); jnei(Y_,S_(0),l_ct0+i); shri(X_,X_,shs[i]); addi(L_,L_,shs[i]); label(l_ct0+i); } }
  subi(Y_,DPM,1); and_(DPM,DPM,Y_);
  label(l_gather);
  shr_(ACC,0,L_); andi(ACC,ACC,1);
  for(int j=1;j<KEYB;j++){ shr_(TT,j,L_); andi(TT,TT,1); shli(TT,TT,j); or_(ACC,ACC,TT); }
  label(l_record);
  andiU(REC,ACC,u_mask(KEYB)); shli(REC,REC,1); addi(REC,REC,1);
  mov_(REP,REC);
  for(int k=1;k<RPW;k++){ shli(X_,REC,RB*k); or_(REP,REP,X_); }
  movi(SLOT,0); label(l_sl_ok);
  label(l_probe);
  ld(TR,SLOT,0); xor_(TR,TR,REP);
  for(int k=0;k<RPW;k++){
    if(k){ shri(Y_,TR,RB*k); andiU(X_,Y_,u_mask(RB)); } else andiU(X_,TR,u_mask(RB));
    jeqi(X_,S_(0),l_match0+k);
  }
  label(l_pnext);
  addi(SLOT,SLOT,1); jnei(SLOT,S_(S),l_probe);
  label(l_insert);
  if(STM){ ld(ID,L_,WK); shri(ID,ID,LSTB); } else ld(ID,L_,LID);
  andiU(SLOT,ID,u_mask((int)SB)); shri(Y_,ID,SB); shl_(X_,REC,Y_);
  ld(TR,SLOT,0); or_(TR,TR,X_); st(SLOT,0,TR);
  label(l_ins);
  mov_(LV,C1); jal(LR,l_restart); jmp(l_dpl);
  for(int k=0;k<RPW;k++){ label(l_match0+k); movi(X_,((u64)RB*k)<<SB); or_(X_,X_,SLOT); jmp(l_match); }
  label(l_cont);
  addi(C_,C_,1); jnei(C_,Tb,l_loop);
  label(l_dl);
  halt(12);
  label(l_restart);
  jnei(IDN,ULIM,l_rs1); halt(11); label(l_rs1);
  if(STM){ shli(X_,IDN,LSTB); or_(X_,X_,LV); st(L_,WK,X_); } else { st(L_,LID,IDN); st(L_,LST,LV); }
  add_(NP,RHO,IDN); addi(IDN,IDN,1);
  andiU(X_,IDN,u_mask((int)SB)); jnei(X_,S_(S),l_rs2); addi(IDN,IDN,((u64)RB<<SB)-S); label(l_rs2);
  label(l_setwalk);
  movi(ONEB,1); shl_(ONEB,ONEB,L_); not_(NM,ONEB);
  label(l_sw_planes);
  for(int j=0;j<256;j++){
    and_(X_,j,NM);
    if(j){ shri(Y_,NP,j); andi(Y_,Y_,1); } else andi(Y_,NP,1);
    shl_(Y_,Y_,L_); or_(j,X_,Y_);
  }
  label(l_sw_end);
  e(JR,0,LR,0,0);
  label(l_evalF);
  build_state(MISC);
  label(l_ef_perm);
  e(PERM,0,W0,0,0); lda(PDR,MISC+7); xor_(FF,W0,PDR);
  e(JR,0,LR2,0,0);
  label(l_outm);
  build_state(MISC);
  e(JR,0,LR2,0,0);
  label(l_match);
  if(STM){ ld(LB,L_,WK); shri(Y_,LB,LSTB); andiU(LB,LB,u_mask(LSTB)); sub_(LB,C1,LB); }
  else { ld(Y_,L_,LID); ld(LB,L_,LST); sub_(LB,C1,LB); }
  jgei(LB,u_add(LRC,S_(1)),l_rfail);
  add_(P_,RHO,X_); add_(Q_,RHO,Y_);
  mov_(UU,P_); movi(LA,0);
  if(STM){ movi(PTR,0); movi(NXC,0); }
  label(l_meas);
  if(STM){ jne(LA,NXC,l_ms1); st(PTR,0,UU); addi(PTR,PTR,1); eU(ADDI,NXC,NXC,0,Gg,-1); label(l_ms1); }
  jal(LR2,l_evalF); addi(LA,LA,1); jlti(FF,THR,l_measd);
  jgei(LA,LRC,l_rfail); mov_(UU,FF); jmp(l_meas);
  label(l_measd);
  if(STM){
  jlt(LA,LB,l_bl);
  sub_(N_,LA,LB); movi(IA,0); movi(PT2,0);
  label(l_al1);
  eU(ADDI,TQ,IA,0,Gg,-1); jlt(N_,TQ,l_al2); mov_(IA,TQ); addi(PT2,PT2,1); jmp(l_al1);
  label(l_al2);
  ld(P_,PT2,0); addi(PT2,PT2,1); eU(ADDI,NX,IA,0,Gg,-1); sub_(N_,N_,IA);
  label(l_al3);
  jeqi(N_,S_(0),l_al4); mov_(UU,P_); jal(LR2,l_evalF); mov_(P_,FF); subi(N_,N_,1); jmp(l_al3);
  label(l_al4);
  sub_(IA,LA,LB); jmp(l_walk0);
  label(l_bl);
  sub_(N_,LB,LA); movi(IA,0); eU(MOVI,NX,0,0,Gg,-1); movi(PT2,1);
  label(l_bl1);
  jeqi(N_,S_(0),l_walk0); mov_(UU,Q_); jal(LR2,l_evalF); mov_(Q_,FF); subi(N_,N_,1); jmp(l_bl1);
  label(l_walk0);
  jeq(P_,Q_,l_rfail);
  label(l_seg);
  jge(NX,LA,l_last);
  sub_(MM,NX,IA); mov_(N_,MM); mov_(QW,Q_);
  label(l_sw);
  mov_(UU,QW); jal(LR2,l_evalF); mov_(QW,FF); subi(N_,N_,1); jnei(N_,S_(0),l_sw);
  ld(TQ,PT2,0); jeq(TQ,QW,l_lloop);
  mov_(P_,TQ); mov_(Q_,QW); mov_(IA,NX); eU(ADDI,NX,NX,0,Gg,-1); addi(PT2,PT2,1); jmp(l_seg);
  label(l_last);
  sub_(MM,LA,IA);
  } else {
  jlt(LA,LB,l_advq);
  sub_(N_,LA,LB); mov_(MM,LB);
  label(l_advp);
  jeqi(N_,S_(0),l_lock); mov_(UU,P_); jal(LR2,l_evalF); mov_(P_,FF); subi(N_,N_,1); jmp(l_advp);
  label(l_advq);
  sub_(N_,LB,LA); mov_(MM,LA);
  label(l_advq2);
  jeqi(N_,S_(0),l_lock); mov_(UU,Q_); jal(LR2,l_evalF); mov_(Q_,FF); subi(N_,N_,1); jmp(l_advq2);
  label(l_lock);
  jeq(P_,Q_,l_rfail);
  }
  label(l_lloop);
  jeqi(MM,S_(0),l_rfail);
  mov_(UU,P_); jal(LR2,l_evalF); mov_(FP,FF); mov_(UU,Q_); jal(LR2,l_evalF);
  jeq(FP,FF,l_found);
  mov_(P_,FP); mov_(Q_,FF); subi(MM,MM,1); jmp(l_lloop);
  label(l_found);
  mov_(UU,P_); jal(LR2,l_outm);
  for(int i=0;i<4;i++) st(ZERO,OUT+i,W0+i);
  mov_(UU,Q_); jal(LR2,l_outm);
  for(int i=0;i<4;i++) st(ZERO,OUT+4+i,W0+i);
  halt(1);
  label(l_rfail);
  halt(13);
  label(l_end);
  (void)jne;
  for(int i=0;i<nfix;i++) code[fixi[i]]|=(u64)lab[fixl[i]]<<39;
  /* audit: every conditional branch follows the compare that sets its register */
  for(int i=0;i<ni;i++){ int op=(int)(code[i]&31);
    if(op==BNZ||op==BZ){ int pop=(int)(code[i-1]&31); if(!(pop==EQ||pop==LT||pop==EQI||pop==LTI) || ((code[i-1]>>6)&2047)!=((code[i]>>17)&2047)) die("audit"); } }
}

static long vmhwm(void){
  long hwm=-1; static char st[2048]; int fd=(int)sc3(2,(i64)"/proc/self/status",0,0);
  if(fd>=0){ long n=sc3(0,fd,(i64)st,sizeof st-1); sc3(3,fd,0,0); if(n>0){ st[n]=0;
    for(long i=0;i+6<n;i++) if(st[i]=='V'&&st[i+1]=='m'&&st[i+2]=='H'&&st[i+3]=='W'&&st[i+4]=='M'){ long j=i+6,v=0; while(st[j]==' '||st[j]==9) j++; while(st[j]>='0'&&st[j]<='9') v=v*10+(st[j++]-'0'); hwm=v; break; } } }
  return hwm;
}
static int work(int argc, char **argv){
  const char *pin= argc>1? argv[1] : "params.json"; const char *pout= argc>2? argv[2] : "other.bin";
  STM= argc>3 && argv[3][0]=='s' && argv[3][1]=='t';
  int fd=(int)sc3(2,(i64)pin,0,0); if(fd<0) die("open params");
  long n=sc3(0,fd,(i64)pj,sizeof pj-1); sc3(3,fd,0,0); if(n<=0) die("read params"); pj[n]=0;
  program();
  int fo=(int)sc3(2,(i64)pout,01|0100|01000,0644); if(fo<0) die("open out");
  /* code words then literals, little-endian (x86-64 native order) */
  sc3(1,fo,(i64)code,(i64)ni*8); sc3(1,fo,(i64)lits,(i64)nlit*32); sc3(3,fo,0,0);
  os("other code: "); ou((u64)ni); os(" instructions x 8 bytes + "); ou((u64)nlit); os(" literals x 32 bytes = ");
  ou((u64)ni*8+(u64)nlit*32); os(" bytes\n");
  os("assembler peak RSS (VmHWM, this process image) "); ou((u64)vmhwm()); os(" KiB\n"); oflush();
  return 0;
}
int cmain(long *sp){
  int argc=(int)sp[0]; char **argv=(char**)(sp+1);
  i64 pid=sc3(57,0,0,0);
  if(pid==0){ int rc=work(argc,argv); oflush(); sc3(60,rc,0,0); }
  if(pid<0) die("fork");
  struct { long ut[2], st[2]; long maxrss, rest[14]; } ru; int status=0;
  { i64 r; register i64 r10 __asm__("r10")=(i64)&ru; __asm__ volatile("syscall":"=a"(r):"a"(61L),"D"(pid),"S"((i64)&status),"d"(0L),"r"(r10):"rcx","r11","memory"); (void)r; }
  os("worker peak RSS (getrusage via wait4, worker forked from the 1-page parent) "); ou((u64)ru.maxrss); os(" KiB = "); ou((u64)ru.maxrss*1024); os(" bytes (limit 1048576)\n"); oflush();
  return ((status>>8)&255);
}
```
