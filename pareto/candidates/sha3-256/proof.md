# SHA3-256 with 17 prefix rounds: a message embedding that keeps one column of round 1 constant (design X), on the LS1 distinguished-point collision search; a 97,242-operation bit-sliced step, time_log2 124.40009

## 1. Claim

Target `sha3-256-r17-prefix-v1`: SHA3-256 (FIPS 202) with Keccak-f rounds 0 to 16 in the single permutation call, zero initial state, rate 136 bytes, suffix 0x06 with pad10*1, and the full 256-bit digest. The algorithm outputs two distinct 128-byte one-block messages with equal complete digests (an ordinary collision).

| Quantity | Value |
|---|---|
| time_log2 (collision-frontier-v5, unit 4,607 word operations, rounded up) | 124.40009 (Sections 4 and 5, certificate in Appendix A) |
| memory | at most 1,048,523 bytes <= 2^20 (margin 53 bytes), memory_log2_bytes = 20 (Section 6) |
| normalizedTimeMemoryLog2 = time_log2 + max(0, memory_log2_bytes - 20) | 124.40009 |
| success probability | at least 0.39 for one attempt, under the premise H_rand (Section 5) |
| preprocessing | the generator run `gen4 512 1000 5 i`, the parameter scan and the assembly of the other code (Section 3.7), charged 661,063,426,650,368 word operations inside N; preprocessing_log2 = 38; no advice |

The method is a distinguished-point parallel collision search (van Oorschot-Wiener) on a chain function F, with 256 walks per step. It is the search, step design, ledger and success bound of Jbenisek's entry a767dfcf (LS1, sha3-256 Pareto round 7, 124.11222), the declared dependency of this package, with a new message embedding:

1. **Embedding (new: design X, Section 2).** The 256-bit point fills ten message lanes, two in each column (rows y = 0 and y = 2), with one 64-bit linear relation, and the remaining message lanes take fixed values (lanes 5 to 9 all-ones, lane 15 zero). Then every column parity of the absorbed state is the same constant, round 0 is affine in the point, and after round 0 the columns x = 3 and x = 4 are constant while the parity of column 2 is constant by the relation. So the D of column 3 in round 1 is constant and every chi row of round 1 has a constant input (the lane of column 3). A chi row with one constant input needs about 6 gates instead of 10 (Section 3.2); this is where the saving comes from. In the embedding of a767dfcf (six lanes in two columns) all 1,600 chi inputs of round 1 are variable.
2. **Step program.** One step of the 256 walks is a bit-sliced straight line of 97,242 register operations, built by gen4.c: the generator gen3.c of a767dfcf (lazy theta per chi row, complement subsets, chained 10-gate chi rows, the polarity plan with one round of lookahead, D masks and output complements, dead-code elimination, last-use register allocation, streaming emission) with the embedding of Section 2, a cost table for rows with one constant input and the planning of those rows in round 1 (Sections 3.2, 3.3). Rounds 0 and 1 cost 3,208 operations here.
3. **Search.** The search of a767dfcf unchanged in its rules (Section 4): lockstep walks with a restart on each distinguished point, a positional five-slot table, a checkpoint replay of the colliding pair, and the success bound of Section 5. Its parameters (the DP threshold, the replay cap, the table size, Tb) were chosen again by the same parameter scan for the memory this step leaves.

claim.json declares three heuristics. H_rand (Section 5) is the one score-critical premise. H_reg (register file) and H_code (code-memory encoding) are machine conventions of the cost model with role supporting (Section 3.6); they are the conventions of a767dfcf.

## 2. The function F and the encoding

Let u be a 256-bit point with little-endian 64-bit lanes u0, u1, u2, u3. Write rotl(w, k) and rotr(w, k) for the rotations of a 64-bit lane and R_x = ROT[x][2] = 3, 10, 43, 25, 39 (x = 0..4) for the rho offsets of the lanes (x, 2). Define five 64-bit values

    v_x = u_x (x = 0, 1, 2, 3),   v_4 = rotr(u0, 36) xor rotr(u1, 29) xor rotr(u2, 60) xor rotr(u3, 14),

where the rotation of u_x is (R_4 - R_x) mod 64; equivalently **rotl(v_0, 3) xor rotl(v_1, 10) xor rotl(v_2, 43) xor rotl(v_3, 25) xor rotl(v_4, 39) = 0** (the relation (V)). The message m(u) has 128 bytes, the 16 lanes 0 to 15 of the absorbed state (lane index x + 5y):

- lane x = v_x xor K_x (row y = 0, x = 0..4);
- lane 10 + x = v_x xor K_(10+x) (row y = 2, x = 0..4), with K_(10+x) = K_x xor 0x5555555555555555 xor (lane 16 when x = 1, else 0);
- lanes 5 to 9 (row y = 1) all-ones; lane 15 zero.

With the SHA3 padding, byte 128 is 0x06 and byte 135 is 0x80: one absorbed block, lane 16 = L16 = 0x8000000000000006, lanes 17 to 24 zero. Rounds 0 to 16 are applied and the digest is lanes 0 to 3 of the result (32 bytes). Define

    F(u) = SHA3-256-r17(m(u)) xor PD

where PD is a fixed 256-bit mask (the polarity of the program's digest planes, Section 3.4). The map u -> m(u) is injective (lanes 0 to 3 are u0 to u3 xored with constants), so F(a) = F(b) with a != b gives two distinct messages m(a), m(b) with equal complete digests. XOR with a fixed mask is a bijection of the range, so F is a fixed function from 256 bits to 256 bits like the plain digest map.

Constants (hexadecimal; K_0 to K_4 are the offsets of trial 1301, drawn by xorshift from the trial number, one of 512 trials; the selection run is charged in N as preprocessing, Section 3.7):

```
K0  8c5ba0e07b73a272  K1  b8150696204f99b6  K2  82c394a5bad5ab05  K3  eac66eec338c6113  K4  99ccd6ee3ef35d11
K10 d90ef5b52e26f727  K11 6d4053c3751acce5  K12 d796c1f0ef80fe50  K13 bf933bb966d93446  K14 cc9983bb6ba60844
lanes 5..9 ffffffffffffffff   lane 15 0000000000000000   lane 16 (padding) 8000000000000006
PD (lanes 0..3) 92089fdf7ffc3330 47af7800935226fa e9f6602080024cc9 ac50002000014805
```

**Round 0 is affine.** Let a(x, y) be the lane (x, y) of the absorbed state and L3 = (0, L16, 0, 0, 0) the row y = 3.
- *Theta.* Column x has parity C0[x] = (v_x ^ K_x) ^ 1...1 ^ (v_x ^ K_x ^ 5...5 ^ L3[x]) ^ L3[x] ^ 0 = 0xaaaaaaaaaaaaaaaa for every x: the variable parts cancel in pairs. Hence D0[x] = C0[x-1] ^ rotl(C0[x+1], 1) = 0xaaaa...aa ^ 0x5555...55 = all-ones, and theta complements every lane.
- *Rho, pi.* Chi row y' of round 0 reads at its position x' the lane (3y' + x' mod 5, x') after theta (rotated by rho): position 0 a lane of row 0 (variable), position 1 a lane of row 1 (all-ones, complemented: 0), position 2 a lane of row 2 (variable), position 3 a lane of row 3 (capacity lanes and lane 15: all-ones after theta; in row y' = 1 it is lane 16: rotl(not L16, 45)), position 4 a capacity lane of row 4 (all-ones). So in every row b1 = 0 and b4 = all-ones, and b3 is all-ones except three bits of row y' = 1 (the three zero bits of not L16).
- *Chi.* out0 = b0 ^ (not b1 & b2) = b0 ^ b2; out1 = b1 ^ (not b2 & b3) = not b2 & b3; out2 = b2 ^ (not b3 & b4) = b2 ^ not b3; out3 = b3 ^ (not b4 & b0) = b3; out4 = b4 ^ (not b0 & b1) = all-ones. Every product has a constant factor: round 0 is affine in u, iota adds a constant.

**Round 1 has a constant column.** After round 0 the lanes of column 3 (out3 = b3) and column 4 (all-ones) are constants. The parity of column 2 is C1[2] = XOR over the five rows of out2 = XOR_x rotl(v_x, R_x) ^ (a constant) = a constant, by the relation (V) (out2 of row y' is rotl(v_x ^ K_(10+x) ^ 1...1, R_x) ^ not b3 with x = 3y' + 2 mod 5, and the five rows take the five x). Hence D1[3] = C1[2] ^ rotl(C1[4], 1) is constant, and every lane of column 3 stays constant through the theta of round 1. Chi row Y of round 1 reads lane (3Y + X mod 5, X) at position X; the column x = 3 lane is at position X = 3 - 3Y mod 5, one position in each row. So every chi row of round 1 has a constant input. The other inputs are affine forms in u. In this build 317 of the 320 rows have one constant and four distinct variable inputs; three rows (row 2 at z = 50, 52, 53) have a second constant input, a consequence of the three zero bits of not L16 in round 0. The generator checks all of this itself: it tracks every value of rounds 0 and 1 as a GF(2) affine form in the 256 input bits and folds constants, so no property of this paragraph is assumed by the program.

**Degrees of freedom.** The ten variable lanes carry 640 bits; the column parities of round 0 use 320 of them (the pairs cancel), the relation (V) another 64, and the 256 bits of u remain. The constants are fixed by the requirement D0 = all-ones (lanes 5 to 9 and the pattern 0x5555...55 of the pair offsets; the equation C0[x-1] ^ rotl(C0[x+1], 1) = all-ones for all x has the solutions C0 = 0xaaaa...aa and its complement in every column), except the offsets K_0 to K_4, which the trials draw.

**What the round-1 constants give.** A chi row with the constant c at position k computes out[k] = c ^ (not b[k+1] & b[k+2]), out[k-1] = b[k-1] ^ (not c & b[k+1]) and out[k-2] = b[k-2] ^ (not b[k-1] & c): two of these products are a variable or zero, and only the three products not b[k+1] & b[k+2], not b[k+2] & b[k+3], not b[k+3] & b[k+4] need a gate. With polarities that fit, the row costs 3 AND/OR and 3 XOR (one of out[k-1], out[k-2] is a free copy of an input), against 5 and 5 for a row with five variable inputs (Section 3.2). Round 1 of this program has 3,208 operations for rounds 0 and 1 together.

The search uses no algebraic property of F: F is only evaluated. The embedding only decides which bit-sliced program computes F and how long it is.

## 3. One step of 256 walks: the straight line

### 3.1 Planes, polarity, gates

A batch is 256 walks. Plane (lane, z) is one 256-bit word whose bit t is bit z of that lane for walk t. The rotations of rho and the moves of pi rename planes and cost nothing.

Each value is held as a register and a polarity p: the logical value is the register word xor p, all-ones or zero. NOT and XOR with a constant flip p for free; constants are folded and never stored. The operations, each one word operation, are:
- XOR: one operation;
- logical a AND b: one AND when both polarities are 0, one OR with output polarity 1 when both are 1, and two operations otherwise, either A xor (A and B) (output polarity 0) or (not A) or B (output polarity 1);
- NOT: one operation, used for the row complements of 3.2 and the theta and output complements of 3.3.

Equal operands fold, and a binary operation on the same pair of registers is emitted once (hash-consing). In rounds 0 and 1 every value is also tracked as a GF(2) affine form in the 256 input bits; a form that already exists is reused, and a form that is constant is a constant.

### 3.2 Rounds

For each round r = 0..16, with the round constant of the profile:

1. Column sums C[x][z] (the five planes of the column, folded) and D[x][z] = C[x-1][z] xor C[x+1][z-1], computed slice by slice with C[.][63] first, so that few C values are live at once.
2. The chi rows, in order Y = 0..4 and z = 0..63. Each row XORs D into its five inputs b[X] = A[x][y][z - rho(x,y)] xor D[x][z - rho(x,y)] (x = 3Y + X mod 5, y = X) when the row is computed (lazy theta).
3. **Row decision.** chi computes out[X] = b[X] xor ((not b[X+1]) and b[X+2]). Before it, the generator may NOT some of the inputs (a complement subset s, one operation each), and an output j may read the finished output out[j+1] in place of b[j+1] (the **10-gate row**): wherever b[j+2] = 1, out[j+1] = b[j+1]; wherever b[j+2] = 0 both sides below are 0; so (not out[j+1]) and b[j+2] = (not b[j+1]) and b[j+2]. The polarity of out[j+1] is set by its own term, so the odd five-cycle of equal polarities, which forces a two-operation term in a plain row, is broken. Any acyclic set T of such links (a chain) is allowed; the outputs are computed in an order where out[j+1] is finished before out[j] reads it. For rows with five distinct variable inputs the decision is read from a table made once (`mk_tables2`, `eval_row`; a767dfcf): for each of the 32 input polarity patterns and each of the 32 output polarity vectors, the cheapest (s, T, term polarities, output complement E), E being a subset of outputs complemented after they are computed (one NOT each).
4. **Rows with one constant input (new).** For a row whose input k is a constant (bit k of the pattern is its value) and whose other four inputs are distinct variables, `mk_tablesc` builds the same table with `eval_rowc`: it evaluates the row abstractly exactly as the build folds it (a product with a constant factor is the other factor or zero, an XOR with a constant flips a polarity, a copy costs nothing), for every k, pattern, complement subset of the variable inputs, chain T, term polarities and E, and keeps for each requested output vector the cheapest decision (ROWCc, ARGc, ARGEc). A table entry is only an estimate of the build; the program that is counted is the one the build emits (3.5). In round 1 of design X these rows cost 6 or 7 operations where a five-variable row costs 10 or 11.
5. Other rows (in this program: rounds 0 and 1, the rows with more constants) evaluate the 32 subsets and the six 10-gate choices and keep the first cheapest (`row_choose`).
6. iota flips the polarity of the lane-0 planes where the round constant has a 1.

**The last round** computes only row Y = 0 and the outputs X = 0..3 (the digest lanes); the 10-gate form is used there when both outputs j and j + 1 are needed. In this program 4,593 rows use a 10-gate link.

**Dead-code elimination** removes every operation on which no state plane of the next round (no digest plane, in the last round) depends. **The cut pass** of a767dfcf (after round 1: NOT(NOT x) = x, and p XOR (p AND q) = p AND NOT q, p XOR (p OR q) = NOT p AND q when the AND/OR has no other use) is applied unchanged.

**State planes after round 1 (new).** In design X some outputs of round 1 are affine (for example a row output that is a copy of an input), so two state planes may be the same node, and a state plane may be an input plane. The generator then pins both planes to one register (the second plane reads the first plane's pin, `pq_of`), and an input plane that is a state plane keeps its register until its last use in round 2. The self-test and the Python port check the program that results (3.8).

### 3.3 Polarity plan

With AND, OR and XOR, the polarity of every value follows from the operations that built it, so the row costs depend on NOTs placed earlier. Four kinds of choices move polarities at a known cost (a767dfcf, unchanged):
- a NOT on a column sum C[x][z] (one operation) flips the 10 chi inputs it reaches through D;
- the D of a lane (x, z) reaches five chi inputs; a 5-bit mask F[x][z] chooses which of them read D' = NOT D (one NOT for the lane when the mask is not 0); at most 100 lanes of a round have a mask other than 0 and 31;
- a two-operation term has a free output polarity;
- an output complement E of a planned row (one NOT per output).

**The last round** is planned alone by simulated annealing (600,000,000 iterations) against the exact cost table of its four-output row. **Rounds 2 to 15**: one round of lookahead (`polopt2`): an annealing of the C NOTs, the D masks and the output polarity vector of each chi row, minimising 16 x (row costs + NOTs of the round) + 3 x (the least row cost of each row of the next round that those outputs give, plus 5), 600,000,000 iterations per round; each row then takes the table's decision for its pattern and chosen outputs. In design X a few state planes after round 1 can be constants (outputs of the rows with two constant inputs); the planner of round 2 takes their polarity as their value (gen3.c skipped the plan of a round whose input has a constant plane; that never happened in a767dfcf's embedding).

**Round 1.** First a greedy pass over the 5-bit D masks and the C complements of rounds 0 and 1 (`r1greedy`, three sweeps at most, counted by full builds of rounds 0 and 1; gain 118 operations here). Then `polopt1` anneals the output vectors of the rows of round 1 with the lookahead of round 2 (600,000,000 iterations). New in design X: `polopt1` plans the rows with one constant input with the table of 3.2 (item 4), as it plans five-variable rows with the table of item 3 (the record of the round-1 rows, rec_d, marks a row 1 for five variables and 2 + k for one constant at position k); the build then applies the chosen decision (complement subset, chain, term polarities, E) to each such row. The three rows with two constants keep the row_choose decision.

The build is multi-pass: pass 1 plans round 1, pass k plans round k on the state the earlier passes built, and the final build writes the program. Every decision is written to plan.txt and read by the experiment program. The ledger counts the program that is built, not the plan's prediction:

```
plan r2 predicted row cost 1643 theta NOTs 93 free polarities set 0
plan r3 predicted row cost 1643 theta NOTs 94 free polarities set 0
plan r4 predicted row cost 1638 theta NOTs 96 free polarities set 0
plan r5 predicted row cost 1646 theta NOTs 103 free polarities set 0
plan r6 predicted row cost 1643 theta NOTs 93 free polarities set 0
plan r7 predicted row cost 1647 theta NOTs 95 free polarities set 0
plan r8 predicted row cost 1643 theta NOTs 98 free polarities set 0
plan r9 predicted row cost 1649 theta NOTs 90 free polarities set 0
plan r10 predicted row cost 1651 theta NOTs 110 free polarities set 0
plan r11 predicted row cost 1635 theta NOTs 101 free polarities set 0
plan r12 predicted row cost 1647 theta NOTs 100 free polarities set 0
plan r13 predicted row cost 1643 theta NOTs 102 free polarities set 0
plan r14 predicted row cost 1653 theta NOTs 100 free polarities set 0
plan r15 predicted row cost 1637 theta NOTs 90 free polarities set 0
plan r16 predicted row cost 261 theta NOTs 14 free polarities set 5
```

### 3.4 Chain feed

Digest plane j is written into register j, which held input plane j. The physical digest word is the next point: F folds the digest polarity PD into the function (Section 2). There is no copy and no NOT between steps.

### 3.5 The ledger of one step

Printed by the generator (Appendix B):

| operation | count |
|---|---:|
| XOR | 71,480 |
| AND | 13,243 |
| OR | 10,370 |
| NOT | 2,149 |
| load / store | 0 / 0 |
| **total** | **97,242** |

Operations after each round (cumulative): round 1: 3,208, round 2: 9,740, round 3: 16,277, round 4: 22,811, round 5: 29,360, round 6: 35,896, round 7: 42,438, round 8: 48,979, round 9: 55,518, round 10: 62,079, round 11: 68,615, round 12: 75,162, round 13: 81,707, round 14: 88,260, round 15: 94,787, round 16: 97,242. A full middle round costs 6,532, 6,537, 6,534, 6,549, 6,536, 6,542, 6,541, 6,539, 6,561, 6,536, 6,547, 6,545, 6,553, 6,527 (rounds 2 to 15), the last round 2,455. That is 379.85 word operations per evaluation of F, 0.0825 of the reference cost 4,607 per evaluation.

### 3.6 Registers and code encoding (machine conventions H_reg and H_code)

**Registers.** As in a767dfcf: values are allocated to registers in program order and a register is freed at the last use of its value. Input and digest plane j use register j. Every other value takes the lowest-numbered register of an operand that dies at its instruction, when the value may use that register (the short form of the encoding below); otherwise the lowest-numbered free register it may use. Registers 0 to 255 are open to each value that dies before the last round, except the state planes of lanes 0, 6, 12, 18 and 24 after round 15 (they feed the digest row); in the last round, register j < 256 is open to a value whose last use is not after the instruction that defines digest plane j. The program uses registers 0 to 2,023 (2,024 registers, equal to the 2,024 values live at once at the peak), so every register number of the straight line is below 2^11. The search keeps its state in registers 2,024 to 2,033 (the step counter, a spare word, the next trail number, rho, the hit counter, the all-ones word, the prefilter word, two return addresses, a zero word); register 2,034 is spare. The handlers of Section 4.3 use registers 256 to 2,023 as temporaries: their contents are dead between two steps. The step has no loads or stores.

**H_reg (declared machine convention, role supporting).** The cost model and the target profile fix no register count. This package uses the 256-bit word RAM of collision-frontier-v5 with a declared file of 2,035 registers of 256 bits. An operation on register operands costs one word operation, with no load or store. Every load and store of the other code is a charged word operation (Section 4). The file's 65,120 bytes are counted as memory (Section 6). This is the convention of a767dfcf (after jungjipdo's 67f781f8).

**H_code (declared code-memory charging convention, role supporting).** The cost model and the target profile fix no code encoding.
- **Encoding.** Each straight-line instruction has only register operands, in a two-address encoding: bits 0-1 the opcode (0 XOR, 1 AND, 2 OR, 3 NOT), bit 2 a flag t; with t = 1 the destination is the first operand and the instruction continues with the first operand and, for XOR, AND and OR, the second (11-bit register numbers); with t = 0 it continues with the destination, the first operand and, for XOR, AND and OR, the second. A NOT is 14 or 25 bits, an XOR, AND or OR 25 or 36 bits; an instruction whose destination is its second operand is written with its operands swapped. The instructions are packed with no padding in a little-endian bit stream; prog.bin holds the 97,242 instructions of the step (349 of 14 bits, 76,663 of 25 bits, 20,230 of 36 bits; 75,212 with t = 1, 77.3%), 331,218 bytes, and pf.bin the 15 prefilter ORs, 49 bytes. The memory table charges the two files at their measured sizes.
- **Other code.** All other code (setup, loop control, hit handler, DP handler, restart, replay, output) is real code of one machine, written out in Appendix D and assembled: 1,953 instructions of 8 bytes and a literal pool of 11 words of 32 bytes (15,976 bytes), measured from the assembled file. An instruction word has a 5-bit opcode, a flag L, three 11-bit register numbers and a 25-bit immediate field; with L = 1 the immediate is literal number imm of the pool. Each instruction costs one word operation, except PERM, which applies the 17-round permutation to the 1,600-bit state held in seven registers and costs one unit (4,607 operations), the cost model's own price of one permutation. The other instructions are the model's primitives: register-register and register-immediate XOR, AND, OR, NOT, addition, subtraction, shifts, a compare that writes 0 or 1, a conditional branch on that register (always right after its compare, checked by the assembler), jumps, load and store with address register plus immediate, and the random word.
- **Time ledger.** Each instruction is charged as the one word operation it performs; there is no separate charge for fetching or decoding.

The program file is 331,218 bytes. Its SHA-256 is c460716550a7fbbdb7a856225d067fe13e929db65da0b026fc2d0a479df8489f.

### 3.7 Generation and constant selection (preprocessing)

**The generator writes the program as it builds it.** gen4.c (Appendix B) is a freestanding C program without libc, with static arrays only. Its nodes live in a ring of 8,192 slots that holds one round (rounds 0 and 1 share it; this build needs at most 6,847 slots and 1,813 of the 3,840 affine-form slots). When a round is built, the generator removes its dead nodes, gives every value its last use, allocates registers in node order and writes the round's instructions to prog.bin at once; it then keeps only the 1,600 state planes and reuses the ring. The program is never held in the generator's memory.

**The run `gen4 512 1000 5 i`** is the preprocessing:
1. for each of the 512 trials 1000 to 1511 (the offsets K_0 to K_4 from the xorshift generator seeded with the trial number, Section 2) it builds the straight line without the plan and counts its operations (the lowest is 100,890, trial 1301);
2. the 2 trials with the lowest counts are built with the plan of 3.3 and counted: trial 1301: 97,242; trial 1106: 97,266;
3. the best, trial 1301, is planned again and written out (prog.bin; the ledger goes to standard output) with meta.txt and plan.txt.

The flag `i` makes the charged run also write meta.txt (the constants and PD) and plan.txt (every decision of the plan, embedded in the experiment program) for the winning trial; these two small files are written after prog.bin and are used only by the verification runs (self-test, experiments), not by the search.

- **Time.** The ledger charges every build 2^32 word operations and every annealing iteration 2^12, the row tables of a767dfcf 2^32 once and the new table of rows with one constant input (`mk_tablesc`: five positions, 32 patterns, 16 complement subsets, 31 chains, 32 term choices and 32 output complements; below 2^27 row evaluations of fewer than 2^7 operations) 2^34 once: at most 92,729 builds and 28,800,000,000 iterations, plus 2^10 per trial for its constants, count and comparison: G = 516,254,297,751,552. PRE = G + P + O = 661,063,426,650,368 word operations, part of N (Section 4.4), with P and O below; there is no constant basis (K = 0): the constants of Section 2 are a closed form. Since 2^37 < PRE / 4,607 <= 2^38, preprocessing_log2 is 38. The generator run took 3389 s of user time on one core of this machine.
- **Memory.** Measured with `size`: text 59,426 bytes, data 12 bytes, BSS 510,752 bytes, an image of 570,190 bytes. `gen4 512 1000 5 i` was run under `nice -n 10 prlimit --as=1048576 --stack=16384` (an address-space limit of 2^20 bytes and a 16,384-byte stack) and completed. Its peak resident memory, read by the program from /proc/self/status VmHWM, is 466,944 bytes. Section 6 charges the image, a 16,384-byte stack reserve and the whole program file, as if the program were held.

**The other preprocessing steps** (as in a767dfcf). Every other step whose output the search uses is charged in PRE (pre_ops() in Appendix A); each is deterministic, runs once, alone, before the search, and holds less than the generator bound of Section 6.
- *P, the parameter scan* (the native program scan.c, D.5, which wrote params.json and scan_counts.txt): a coarse grid of DP thresholds x replay caps, then a fine grid around the best; for each point the least Tb with model success at least 0.3902, then the exact least Tb with the Decimal bound of Appendix A. Counted in the run: 159,726 float evaluations over 1,880,291,996 bins and 21 exact evaluations over 1,284,990 bins, charged 2^16 per float bin, 2^17 per float evaluation, 2^24 per exact bin, 2^27 per exact evaluation and 2^20 for the grid: P = 144,809,126,264,832. Memory: at most 126,976 bytes (the whole process, under a 2^20-byte address-space limit).
- *O, the assembly* (`other4.py build`, Appendix D): 2^8 per emitted instruction, 2^13 per SHA-256 block of the hashed files and 2^12 for the data image: O = 2,633,984. The native port other.c (D.6) writes the identical other.bin.

### 3.8 Correctness of the step (checked by execution)

- `selftest` (Appendix B) executes the program file, decoded from its two-address encoding, on 4 x 256 uniform points for four chained steps each, and compares every output with F computed by a plain lane-wise 17-round implementation with the message m(u) of Section 2: 4096 chained evaluations (4 batches x 256 trails x 4 steps), 0 mismatches, 97242 instructions; run twice with different seeds.
- That reference against hashlib.sha3_256 at 24 rounds and against the organizer's verifier/keccak.py sha3_256(m, rounds=17) on 300 messages of lengths 0 to 299: 24-round vs hashlib mismatches 0; 17-round vs organizer verifier mismatches 0.
- The experiment program regenerates the same straight line in Python from the generator's decisions (plan.txt, embedded) and refuses to run unless its encoding hashes to the SHA-256 above. Before its trials it checks two chained full-width steps against the plain implementation.

## 4. The search

The rules are those of a767dfcf; the parameters are this row's (params.json, chosen by the scan of 3.7).

Parameters:
- L = 256 walks.
- Distinguished point (DP): the 256-bit image x of F (bit j = plane j) is a DP when x < THR = 754 x 2^135: the planes 145 to 255 are zero and the 10 planes 144 down to 135, read as a number, are less than 754. The probability of a DP for a uniform image is theta = 754 x 2^-121 (H = -log2 theta = 111.441579); it is a rational number, exactly this, and is not a power of two.
- Replay cap LRC = 61,190 x 2^99 = 38,783,770,113,982,678,538,791,634,568,478,720 steps = 11.0000 / theta. No trail is cut; the replay refuses a trail of more than LRC evaluations.
- U = 98,040: the limit on trails started in one attempt.
- S = 19,608 table words, five slots each (98,040 slots, one per trail: U = 5 S); 2^15 = 32,768 > S.
- Tb = 1,325,551,670,394,969,607,676,875,832,282,841,088 = 535,386,056 x 2^91 = 0.99723424 x 2^120 steps of 256 walks per attempt.
- HMAX = floor(Tb (1 + 2^-20) / 2^8) + 1 + LRC = 43,961,711,264,527,806,401,144,495,397,666,817: the cap on prefilter hits; the attempt aborts at hit HMAX + 1.

State:
- in registers: the 256 input planes (registers 0 to 255); the step counter c, the next trail number idn, rho, the hit counter h, the all-ones word, the prefilter word and the return addresses (registers 2,024 to 2,033);
- in memory (word addressed): the table TAB of S words; the walk word WK[l] of each walk l, which holds LST[l], the number of the first step of its trail, in bits 0 to 127 and LID[l], its trail number, in bits 128 to 255; a data image of 16 words: the 7 words of lane constants of the absorbed state (the constants K, with the offsets K_x and K_(10+x) in the ten variable lanes), PD, and 8 words for the output pair.

A table word holds five slots of 51 bits (slot k = bits 51 k to 51 k + 50, k = 0 to 4; bit 255 is unused). Trail i (i = 0, 1, ..., U - 1, in the order the trails start) has the trail number t(i) = (i mod S) + 51 floor(i / S) x 2^15 and owns slot floor(i / S) of word i mod S. The numbers t(i) are distinct, so the starts rho + t(i) are distinct points, and t(l) = l for l < 256 <= S. A written slot is 1 | (bits 0 to 49 of the trail's end) << 1, never zero; an unwritten slot is zero. Neither the trail number nor the trail's length is stored: the slot's place gives the number, and the replay measures the length.

```
setup: rho := random word; idn := 256; h := 0; c := 0; TAB := 0; for l < 256: WK[l] := l << 128 (LID[l] = l, LST[l] = 0); lane l of the input planes := rho + l
loop:
  the straight line (97,242): the input planes become F of the 256 walks
  pf := OR of the 16 planes 240..255 (15 ORs)
  if pf != all-ones (compare, branch):          -- some walk has planes 240..255 zero (probability 2^-16 each)
      h += 1; if h > HMAX: halt, the attempt failed   -- hit counter and abort (F5)
      dp := complement of (pf OR (OR of the planes 145..239))      -- the walks with the top 111 planes zero; c1 := c + 1
      dp := dp AND (the walks whose planes 144..135, read as a number, are < 754)      -- bit-parallel comparison: the walks at a DP
      while dp != 0: l := the lowest set bit of dp; clear it;
          end := the 50-bit value with bit j = bit l of plane j, j = 0..49
          record := 1 | end << 1;  rep := the record in each of the five slots
          for each word w = 0 .. S - 1: load it and XOR rep; for its slots k = 0 .. 4 in order (shift, mask) test for zero:
             zero: slot k of word w equals the record: REPLAY(w + 51 k 2^15, walk l, c1);
                if it returns a != b, output m(a), m(b) and stop; otherwise halt, the attempt failed
          no slot equals the record: t := LID[l]; word (t mod 2^15) := word OR (record << (t >> 15)); restart(l, c1); next DP walk
  c += 1; if c != Tb goto loop
  halt, the attempt failed                           -- c = Tb
restart(l, s): if idn = t(U): halt, the attempt failed
               WK[l] := s | idn << 128; lane l of the input planes := rho + idn; idn += 1;
               if idn mod 2^15 = S: idn += 51 x 2^15 - S      -- so idn = t(i) for the i-th trail
REPLAY(trail a, walk l of trail b, c1):
  b := LID[l]; lb := c1 - LST[l]                       -- the new trail's length; if lb > LRC: return nothing
  walk trail a from a_0 = rho + a to its first DP: la := the number of evaluations (stop with failure if LRC are passed);
      when G divides i, the point a_i is stored in TAB[i / G]      -- checkpoints, G = ceil(LRC / (S - 1))
  d := la - lb; i := max(d, 0)                          -- aligned pairs (a_i, b_(i-d))
  p := a_i (from TAB[floor(i / G)], i mod G evaluations); q := b_(i-d) (from b_0, max(-d, 0) evaluations)
  if p = q return nothing
  repeat: n := the least multiple of G above i
      if n >= la: m := la - i; leave
      q' := b_(n-d) (n - i evaluations from q)
      if q' = TAB[n / G]: m := n - i; leave            -- the trails merge inside this segment
      p := TAB[n / G]; q := q'; i := n
  repeat m times: if F(p) = F(q) return (p, q); p := F(p); q := F(q)
  return nothing
```

No trail is cut: a walk runs until its DP, and only the replay refuses a trail of more than LRC evaluations. A trail restarted inside step c starts at step c + 1, hence LST[l] := c1. A trail is recorded at its first DP, so walking it from its start to its first DP gives its length. The replay is the last routine of an attempt, so the table words are free for the checkpoints; a stored trail has at most floor((LRC - 1) / G) + 1 = 19,607 <= S checkpoints (G = 1,978,057,332,278,404,576,875,178,995,690). Two trails with the same DP agree from their merge on, so the first checkpoint with equal points bounds the merge to its segment, and the lock step from the last unequal pair finds the first F(p) = F(q) with p != q.

### 4.1 One iteration of the loop

An iteration costs the straight line (97,242), the prefilter (15), its test (2) and the counter (3: add, compare, branch): **BSTEP = 97,262 operations**. No other operation runs in an iteration without a prefilter hit.

### 4.2 The replay

The replay evaluates F on one point at a time with the permutation, one unit (4,607 operations) per call. The routine `evalF` (Appendix D) loads the 7 words of lane constants, XORs the point into lanes 0 to 3 and 10 to 13 (three shifts and XORs of the whole word u), computes v_4 from the four limbs (rotations by shifts, an OR of the doubled limb, one final mask), XORs it into lanes 4 and 14, calls PERM, loads PD and XORs it into the first state word: one evaluation with its return costs **e = 4,647** operations (UNIT + 40). The message builder `outm` costs 38 with its return.

Counted from the emitted code (as in a767dfcf, with this e):
- taking the trail number from the place of the matching slot costs 3 and the entry 12;
- a measuring evaluation of trail a costs e + 10, e + 6 for the one that lands on the DP, and 3 more when it stores a checkpoint;
- the alignment: for d >= 0, 16 + 6 K + r (e + 7) with K checkpoints passed and r < G evaluations of a; for d < 0, 8 + (lb - la)(e + 7);
- the test p = q 2; a segment without a merge 14 + m (e + 6), the segment with the merge 8 + m (e + 6), the last segment 3;
- a lock-step iteration 2e + 13, the success exit X = 2 x 38 + 13 = 89 (two message builds with their calls and moves, 8 stores, the halt).

With la, lb <= LRC, the replay costs at most (2e + 17) LRC + (3e + 20) G + 17 nck + e + 26 + X = **9311 LRC + 13961 G + 17 nck + 4762** (e = 4647, G = 1,978,057,332,278,404,576,875,178,995,690, nck = 19,607); an exhausted lock step and every refusal cost less. At most one replay runs per attempt.

### 4.3 Rare operations

Every routine is real code of the machine of Section 3.6 (Appendix D). The counts, each for the longest path, are read from the emitted code (`other4.py build`, D.2):

| routine | operations |
|---|---:|
| a prefilter hit with no DP walk (counter, OR of the planes 145..239, combine and complement, the comparison with 754, c1, test) | **131** |
| one DP walk without a match, without its restart | 268 + 24 S |
| restart(l, s) with its return | **1,294** (the call that halts at idn = t(U): 3) |
| the event c = Tb | 1 |
| setup: clearing TAB, the 256 starts | **357,209** |

At most HMAX + 1 prefilter hits are processed in every execution, at most U - 255 DP walks and U - 256 completed restarts (a767dfcf, Section 4.3):

R = (HMAX + 1) x 131 + (U - 255) x (268 + 24 S) + (U - 256) x (1,294 + 3) + 3 + 1 + 357,209 = 5,758,984,175,653,142,638,549,928,943,264,581,319.

### 4.4 Total

N = Tb x 97,262 + replay + R + PRE = **129,292,708,849,320,895,783,187,834,453,341,445,660,834** word operations (Appendix A).

| part | operations | share |
|---|---:|---:|
| main loop, Tb x 97,262 | 128,925,806,565,955,533,981,868,297,199,493,689,901,056 | 0.99716 |
| replay | 361,143,299,189,708,658,680,986,663,841,064,528,091 | 0.00279 |
| rare operations R and preprocessing PRE | 5,758,984,175,653,142,638,549,928,943,264,581,319 + 661,063,426,650,368 | 4.45e-05 |

time_log2 = log2(N / 4,607) rounded up at the fifth decimal = **124.40009**, checked in exact integer arithmetic:

    4607^100000 * 2^12440008 < N^100000 <= 4607^100000 * 2^12440009

## 5. Success probability and the premise H_rand

This section is the success argument of a767dfcf with the parameters of this row; the computation is Appendix A.

**Premise H_rand (our theory): over the algorithm's coins, the program run on the fixed SHA3-256-r17 target succeeds with probability at least the probability computed below for a uniformly random function F.** The target is fixed: F of Section 2, with its fixed constants K and PD, is one deterministic function, and the only randomness of the algorithm is the random word rho. That transfer is the premise, and it is the one score-critical premise of this package. In claim.json it has four fields: the statement above; role score-critical; scope, the fixed function F of Section 2 on the points of one attempt; limitations, our theory with no proof. The organizer runs of Section 7.1 are not used in this section: the success bound assumes nothing about the organizer-seeded trials (no independence or identical distribution of the trials is used). Everything else in this section is computed in the random-function model M: F is a uniformly random function from 256 bits to 256 bits (values at distinct inputs independent and uniform) and rho is uniform and independent of F. In M:

- (i) the first coincidence of images among e evaluations has probability 1 - prod_(k<e)(1 - k/n) >= 1 - exp(-e(e-1)/(2n)) =: G(e), where n = 2^256;
- (ii) after the first coincidence e* (partner s), the number l of further evaluations of the trail until its DP satisfies P(l >= j | e*, s, history) <= (1 - theta)^j (1 + 2^-108) for every j: a lemma derived from (iii), not a premise;
- (iii) F is realised by lazy sampling: a fresh evaluation draws a new independent uniform value, so given the whole history of the run it equals one given earlier output with probability 2^-256, whatever inputs the adaptive program chose. This is a property of M, not a claim about the fixed target.

The first coincidence is a stopping time over all evaluations in their execution order (step by step, walk by walk). Under (i) and (iii), when k earlier images are distinct the next fresh evaluation coincides with an earlier image with conditional probability exactly k/n, so G(e) is the probability that the first e fresh evaluations contain a coincidence.

**Lemma (ii), derived.** Write q = 1 - theta and E = 256 Tb. Realise F by lazy sampling: one uniform value V_t per evaluation index t, xi_t = 1 when V_t is a DP, the xi_t independent Bernoulli(theta). The walks run in lockstep, so the evaluations of a walk sit at fixed indices 256 apart. Let e* = t with partner s < t (V_t = V_s), s on trail A. B's next input is the input A evaluated at s + 256, and A evaluates every later point of the common path first: l is the first k >= 1 with xi_(s + 256 k) = 1. By (iii), P(V_t = V_s | past) = 1/n exactly, whatever the indicators are; the event (e* = t, partner s) depends on them only through the event D that V_1, ..., V_(t-1) are distinct. Given the m = t - 1 indicators before t, k < U of them DPs, P(D | indicators) lies in [pi_m (1 - delta), pi_m (1 - E/n)^-U] with delta <= U E/n + E^2 theta/(2n) + U^2/(2 theta n); here U E/n = 2^-111.4, E^2 theta/(2n) = 2^-112.4, U^2/(2 theta n) = 2^-112.4, delta < 2^-109, (1 - E/n)^-U / (1 - delta) = 1 + 2^-109.8. By Bayes, the law of the indicators along A's walk after s is within a factor (1 - E/n)^-U / (1 - delta) <= 1 + 2^-108 of the iid law, under which P(l >= j) = q^j; merges with a third trail are again fresh coincidences of probability exactly 1/n given the past, so by induction P(l >= j | e*, s, history) <= q^j (1 + 2^-108). The bin sum and F6 use this tail with weights at most 1: the term FL = 2^-108 (1 + F6) = 3.082e-33.

**The coincidence.** Let e* be the first evaluation whose image equals an earlier image, at step b* = ceil(e*/256). The trail B of that evaluation and the earlier trail A have equal points from then on and both end at the same DP after l further evaluations of B; B is recorded at step b* + l at the latest, and the later record finds the earlier one.

The search succeeds if: (a) b* + l <= Tb; (b) both trails have at most LRC evaluations; (c) fewer than U trails are started; (d) the coincidence is between two different trails; (e) no record of a different end has the same 50 stored end bits, and the replay finds the merge.

Split l into bins of w = 2^99 steps: bin j holds l in [(j - 1) w, j w - 1], j = 1 .. J = 61,190, J w = LRC, with probability p_j = (1 - theta)^((j-1) w) - (1 - theta)^(j w). If l is in bin j, (a) holds when e* <= 256 (Tb - j w). By lemma (ii),

    Pr[(a)] >= sum_j p_j G(256 (Tb - j w)).

The failure events the sum does not cover:

- **F6**, the colliding pair has a trail of more than LRC evaluations (the replay refuses it). With g(a) = min(1, q^(LRC + 1 - a)) and the age of an evaluation (its place in its trail), E[g(age)] <= q^LRC (1 + LRC theta) =: G6 by summation by parts, and the first coincidence at t with partner s is refused with probability at most (1/n) pi_(t-1) (1 - E/n)^-U sum_(s<t) E[g(a_s) + g(a_t)]; summed over t, F6 = 2 G6 (1 - exp(-E^2/(2n) - E^3/(3n^2))) (1 - E/n)^-U = 1.570e-4. This covers (b) outside F2 and F4.
- **F2**, more than U - 256 restarts after a DP (a fact proved here): the restarts after a DP are at most N1, the number of DP values among the lazily sampled values, binomial with mean mu = 256 Tb theta (a DP output at a repeated input finds its earlier record and goes to the replay); the Chernoff bound gives 4.841e-6. This covers (c).
- **F3**, the coincidence lies inside one trail: at most U / (theta^2 n) = 1.053e-5. This covers (d).
- **F4**, 2^-90 + U^2 2^-51 = 4.269e-6: a start equal to a point of another trail (at most U E / n, about 2^-111, inside the 2^-90), and two different ends with the same 50 stored bits (in M the ends are uniform on the bits below the 10 comparison planes; fewer than U^2 / 2 pairs). This covers (e).
- **F5**, the hit counter aborts the attempt before it stops: below 2^-1000. Each step adds to the count X' of fresh hits with conditional probability below 2^-8; hits at repeated inputs occur only after the first coincidence and number at most LRC on success; the abort needs X' >= floor(Tb (1 + 2^-20) 2^-8) + 2, and the supermartingale Chernoff bound gives at most exp(-2,354,651,652,899,128,039,112) < 2^-1000 (exact rationals, Appendix A).

With FL and a further 2^-60 for rounding, the success probability of one attempt is at least 0.3900000007 at Tb and 0.3899999996 at Tb - 2^91: Tb is the least multiple of 2^91 that reaches 0.39 (Appendix A, 80-digit decimals). In evaluations, 256 Tb = 0.997234 x 2^128; the birthday point for success 0.39 is 0.9943 x 2^128, and the wait for the DPs of the last trails, 256 / theta evaluations, is most of the difference.

A failed attempt can be repeated with a fresh rho at the same cost. The claim is one attempt with success 0.39, a probability over the algorithm's coin rho for the fixed target, under the premise H_rand.

## 6. Memory

The search, at its peak:

| region | bytes |
|---|---:|
| register file, 2,035 words of 32 bytes (H_reg) | 65,120 |
| straight line plus prefilter, 97,257 instructions, two-address encoding, prog.bin + pf.bin (H_code) | 331,267 |
| other code (Appendix D), 1,953 instructions x 8 bytes + 11 literals x 32 bytes, measured | 15,976 |
| table, 19,608 words of five slots | 627,456 |
| walk words of the 256 walks (LST and LID), 256 words | 8,192 |
| data image (lane constants K of the absorbed state, PD, output pair), 16 words | 512 |
| **total** | **1,048,523** |

The preprocessing `gen4 512 1000 5 i` runs before the search and ends before it starts:

| `gen4 512 1000 5 i` | bytes |
|---|---:|
| image (text, data, BSS; all arrays static) | 570,190 |
| stack reserve (the run completes with a 16,384-byte stack limit) | 16,384 |
| the program it writes, prog.bin (written out round by round, counted here in full) | 331,218 |
| **bound used** | **917,792** |
| measured peak resident memory (VmHWM) | 466,944 |

The scan and the assembly of Section 3.7 each run alone, below this bound. The claimed memory covers both phases: peak = max(search 1,048,523, preprocessing 917,792) = 1,048,523, since the two phases do not overlap; 1,048,523 <= 1,048,576 = 2^20: memory_log2_bytes = 20, and the normalized cost axis adds max(0, 20 - 20) = 0. The margin to 2^20 is 53 bytes.

The declared experiments and the checks of Sections 3.8 and 7 are verification runs; they build nothing the search uses.

## 7. Evidence for the step and for H_rand

### 7.1 Organizer experiments (experiments/manifest.json, program experiments/ls1.py)

Both experiments regenerate the straight line in Python from the generator's decisions (plan.txt, embedded zlib-compressed in base64 so that the source stays within the 64 KiB review budget; the encoding must hash to the SHA-256 of Section 3.6), check it against the plain 17-round implementation, and execute it on Python integers, all trials side by side. Every trial seed is prefixed by the 16-byte salt of ls1.py (constant SALT). The runs are witnesses of what they execute (the regenerated line equals the plain implementation; the search works at width 22; chained full-width steps give recomputed 22-bit matches). They do not test a complete collision, 2^128 evaluations or the distinguished-point rate at full size, and their frequencies carry no statistical weight in this package: the success bound assumes nothing about the organizer-seeded trials.

- **rho-w22** runs the search of Section 4 end to end at width 22. The planes 22 to 255 are set to zero after every step. Parameters: a DP is an image whose 4 low bits are zero and whose 3 bits above them, as a number, are less than 5, replay cap 256, no trail cut, 3,000 trails and 400 steps per attempt; the table keeps the trail number of each end and the replay measures the stored trail by walking it to its DP, keeping every 16th point as a checkpoint, walks the new trail once and lock-steps the segment of the merge. Every trial returns two messages whose 17-round digests agree on the 22 low bits. An ideal-function control (a767dfcf, the same rules) needs 20.47 steps to the pair on average. Our own runs (5 sets of 256 trials, our seeds, every pair checked with verifier/keccak.py): 256 of 256, 256 of 256, 256 of 256, 256 of 256, 256 of 256 pairs, mean steps 20.58, 20.42, 20.62, 20.15, 19.76.
- **proj-w256** runs eight chained full-width steps from 256 uniform points per trial and finds the first two distinct evaluated inputs whose images agree on the 22 low bits; a random function gives success probability 0.3934 per trial, 100.7 of 256 (standard deviation 7.8). Our own runs (5 sets of 256 trials): 107, 105, 96, 96, 97, 501 of 1280 in all (model 503.6).

### 7.2 Measured checks of H_rand on this program (our runs, not organizer runs)

The embedding makes round 0 affine and leaves one constant input in every chi row of round 1, so F has fewer than 17 full nonlinear rounds; the remaining 16 rounds with nonlinear rows are what the premise rests on. hrand_test.c (Appendix C, unchanged from a767dfcf) executes the program file of this package and measures the rate of image coincidences among evaluated points on three 32-bit windows (bits 0-31, 128-159 and 224-255), for uniform inputs (A), consecutive starts rho + i (B) and chained iterates (C), and the output differences of single-bit input differences (D):

```
A uniform inputs: M=2^24, pairs agreeing on 32 bits: low 32485, mid 32764, top 32941; expected 32768.0 each (sd 181.0); ratios 0.9914 0.9999 1.0053; z -1.56 -0.02 0.96
B consecutive inputs R+i: M=2^24, pairs agreeing on 32 bits: low 32642, mid 32536, top 32715; expected 32768.0 each (sd 181.0); ratios 0.9962 0.9929 0.9984; z -0.70 -1.28 -0.29
C chained iterates (256 chains x 65536 steps): M=2^24, pairs agreeing on 32 bits: low 33281, mid 32663, top 32948; expected 32768.0 each (sd 181.0); ratios 1.0157 0.9968 1.0055; z 2.83 -0.58 0.99
D single-bit differences: 65536 cells x 4096 pairs, max |z| 4.38 at input bit 7 output bit 55 (largest of 65536 normal cells is about 4.4); mean z^2 1.0061 (expected 1)
```

If the real pair-coincidence rate is (1 - eps) of the random value, the success at this Tb falls by about 0.3 eps (the bound has no slack: Tb is the least multiple of 2^91 reaching 0.39), and reaching 0.39 again needs about 0.5 log2(1/(1 - eps)) more bits of time, 0.0073 bit for eps = 0.01. F is not a random function in every sense: with round 0 affine it has algebraic degree at most 2^16 in the 256 input bits (zero-sum distinguishers exist), the same bound as for the embedding of a767dfcf, whose round 0 is also affine (the constant column of design X lowers the number of gates of round 1, not its degree, which stays 2). H_rand concerns only the coincidence and distinguished-point statistics that the search uses.

### 7.3 The emitted program, executed (our runs, not organizer runs)

other4_test.py (Appendix D) executes the assembled bytes: other.bin decoded from its 8-byte words and literal pool, and the straight line (prog.bin and the 15 prefilter instructions) decoded from its two-address encoding and compiled to Python integer operations (D.3, D.4). It runs the routine tests at the full-size immediates of this package (the straight line against the plain implementation on every lane, setup, setwalk, restart, evalF and the message builder against the plain implementation of Section 2, the hit and DP handlers, the table slots, the counter), the replay on pairs of trails of a 12-bit truncation of F for three checkpoint gaps (the executed count equals the per-step counts of Section 4.2 summed along the path, including the success exit X), and the whole emitted program end to end at reduced width on eight parameter sets: checks run: 971, failures: 0.

## 8. Credits and literature

A credit is not an endorsement; nobody named here has reviewed this package.

- **Jbenisek, entry a767dfcf (sha3-256 Pareto round 7, 124.11222), the declared dependency.** Everything in this package except the embedding of Section 2 and the handling of the rows it creates is that entry's work, used as published in its proof.md: the generator gen3.c (here gen4.c, with the changes listed in its header and in Sections 2, 3.2, 3.3), the self-test, the hrand check, the search and the other code (other4.py, other.c), the parameter scan (scan.c), the exact ledger and certificate (cert4.py), the success bound, the experiment program and its two experiments, and the structure and much of the text of this document. Its own credits carry over: jungjipdo's 67f781f8 (step design, register-file convention), 0xplemonade's 4ea0966b and d9d43ff8 (the chained-chi row form), mitchuski's c9a7e62c (a DP threshold that is not a power of two, a replay cap), Jbenisek's d9517c7b and 0dc77160 (search, success bound, rare-operation accounting) and Kepler (a research assistant working with Jbenisek; the structured constants S3-04 of a767dfcf, which this package replaces).
- **This package (Claude Opus 5.5 in Claude Code).** The design-X embedding (Section 2: ten lanes in rows 0 and 2 with the relation (V), constants with D0 = all-ones, the constant column of round 1), the table and planning of rows with one constant input (`eval_rowc`, `mk_tablesc`, polopt1 and build changes), the pin sharing of round-1 state planes, the adaptation of every program to the embedding (gen4.c, selftest.c, other4.py evalF and m_of, other.c, other4_test.py, cert4.py, ls1.py), and every run reported here.
- **J. Guo, M. Liu, L. Song, Linear Structures: Applications to Cryptanalysis of Round-Reduced Keccak, ASIACRYPT 2016.** Linear structures: message lanes placed in pairs of a column so that theta of round 0 adds constants and chi of round 0 stays linear. Design X uses this idea and adds the constant column of round 1 from a constant column parity (the relation (V)).
- **P. C. van Oorschot and M. J. Wiener, Parallel collision search with cryptanalytic applications, J. Cryptology 12 (1999); J. M. Pollard (1975).** The distinguished-point and rho methods.
- **G. Bertoni, J. Daemen, M. Peeters, G. Van Assche, Keccak implementation overview.** The lane complementing transform, applied plane by plane in Sections 3.2 and 3.3.

## Appendix A. The exact ledger

This program (cert4.py of a767dfcf with the design-X changes: e = UNIT + 40, the success exit read from the counts, no constant basis, the charge 2^34 for the new row table; with the inputs of this row written into it) computes the step count, the success bound of Section 5, N, the memory table and the integer certificate. It uses integers and Fractions; Decimal with 80 digits is used only for the exponentials and logarithms of the success bound. The constants of the rare operations and of the replay are the counts of Section 4.3, printed by `other4.py build` (D.2). The DP threshold, the replay cap, S, U and Tb were chosen by the parameter scan, charged in PRE as P; the run below re-checks that Tb is the least multiple of 2^91 with success at least 0.39.

```python
INLINE = {
"ledger.txt": "LS1 step ledger (256 lanes, one chain step, 17 rounds), streaming generator gen3\nXOR 71480\nAND 13243\nOR  10370\nNOT 2149  (row complements chosen pre-DCE: 207)\nLOAD 0\nSTORE 0\nTOTAL 97242\nTRICKROWS 4593 ; forced term polarities 0\nfeed NOTs 0 (digest polarity folded into the chain function: F(u)=H(m(u))^PD)\nnodes created pre-DCE 97372 ; ring peak 6847 of 8192 ; linear forms 1813 of 3840\nmax live values 2024 ; registers used 2024 (limit 2304)\nconstants trial 1301 of 512 ; optmode 5 ; round-1 greedy gain 118\nannealing iterations per round 600000000\ntrials carried to the plan build 2\nplan r2 predicted row cost 1643 theta NOTs 93 free polarities set 0\nplan r3 predicted row cost 1643 theta NOTs 94 free polarities set 0\nplan r4 predicted row cost 1638 theta NOTs 96 free polarities set 0\nplan r5 predicted row cost 1646 theta NOTs 103 free polarities set 0\nplan r6 predicted row cost 1643 theta NOTs 93 free polarities set 0\nplan r7 predicted row cost 1647 theta NOTs 95 free polarities set 0\nplan r8 predicted row cost 1643 theta NOTs 98 free polarities set 0\nplan r9 predicted row cost 1649 theta NOTs 90 free polarities set 0\nplan r10 predicted row cost 1651 theta NOTs 110 free polarities set 0\nplan r11 predicted row cost 1635 theta NOTs 101 free polarities set 0\nplan r12 predicted row cost 1647 theta NOTs 100 free polarities set 0\nplan r13 predicted row cost 1643 theta NOTs 102 free polarities set 0\nplan r14 predicted row cost 1653 theta NOTs 100 free polarities set 0\nplan r15 predicted row cost 1637 theta NOTs 90 free polarities set 0\nplan r16 predicted row cost 261 theta NOTs 14 free polarities set 5\ncum after round 1 3208\ncum after round 2 9740\ncum after round 3 16277\ncum after round 4 22811\ncum after round 5 29360\ncum after round 6 35896\ncum after round 7 42438\ncum after round 8 48979\ncum after round 9 55518\ncum after round 10 62079\ncum after round 11 68615\ncum after round 12 75162\ncum after round 13 81707\ncum after round 14 88260\ncum after round 15 94787\ncum after round 16 97242\ngenerator peak RSS (VmHWM, this process image) 456 KiB = 466944 bytes (limit 1048576)\n",
"size.txt": "   text\t   data\t    bss\t    dec\t    hex\tfilename\n  59426\t     12\t 510752\t 570190\t  8b34e\tgen4\n",
"counts.txt": "other code: 1953 instructions x 8 bytes + 11 literals x 32 bytes = 15976 bytes (other.bin sha256 63a8c35c37070ff697bc7ac864c18b68648a3f74a0fb149a2aea61de796d753b)\nprefilter: 15 instructions, two-address encoding, 49 bytes (pf.bin sha256 17505f8bc5711b8e2d7b413737a35a2fdd5dda5ad9070f89cbb9a4b4a5d41374); the straight-line block = prog.bin (97242 instructions, 331218 bytes) then pf.bin, 97257 instructions, sits in front of instruction 26 (label loop)\ndata image: 16 words x 32 bytes = 512 bytes (data.bin sha256 35551aae06a46cee1ba101f615e7b0170564c77e84ad9feeb490eb38c1fdbb66): KW[0..6], PD, 8 output words\nmemory map (words): TAB 0..19607, WK (walk words, LST | LID << 128) 19608..19863, data 19864..19879\nreplay checkpoint gap G = ceil(LRC / (S - 1)) = 1978057332278404576875178995690, at most 19607 checkpoints\nroutine entry points (instruction index): start 0, loop 26, hit 28, dpl 158, dp1 160, gather 204, record 402, probe 415, insert 439, ins 447, match0 450, cont 465, dl 468, restart 469, setwalk 481, evalF 1764, outm 1805, match 1843, meas 1855, measd 1868, bl 1892, walk0 1903, seg 1905, last 1925, lloop 1926, found 1939, end 1953\nn_instr            1953\nsetwalk            1283\nrestart            1294\nrestart_halt       3\nhit                131\nctz_clear          44\ngather             198\nrecord_slot        13\nprobe_word         24\ninsert             8\ndp_fixed           268\ndp_max             470860\ndl_final           1\ne_eval             4647\ne_outm             38\nmatch_entry        15\nmeas_iter          4657\nmeas_last          4653\nckpt               3\nadv_iter           4654\nbwalk_iter         4653\nseg_iter           14\nreplay_iter        9307\nreplay_gap         1978057332278404576875178995690\nreplay_rate        9311\nreplay_g           13961\nreplay_nck         17\nexit_found         89\nreplay_const       4762\nreplay_max         361143299189708658680986663841064528091\nsetup              357209\nother_bytes        15976\nother_literals     11\nprog_bytes         331218\npf_bytes           49\nsl_bytes           331267\nstatic opcode mix: OR 424 ANDI 331 SHRI 286 AND 271 SHL 258 SHLI 68 SHR 50 ADDI 26 MOV 25 MOVI 22 EQI 22 ST 20 BNZ 19 XOR 18 BZ 17 LDA 15 JMP 13 NOT 12 JAL 10 SUB 7 LTI 6 LD 6 EQ 5 HALT 5 SUBI 5 ADD 4 JR 3 LT 3 RND 1 PERM 1\nhighest register named: 2033 (file of 2035)\n",
"params.json": "{\n \"NR\": 17,\n \"HF\": 111,\n \"DPLO\": 145,\n \"DK\": 10,\n \"DT\": 754,\n \"S\": 19608,\n \"U\": 98040,\n \"SB\": 15,\n \"W\": 633825300114114700748351602688,\n \"J\": 61190,\n \"LRC\": 38783770113982678538791634568478720,\n \"Tb\": 1325551670394969607676875832282841088,\n \"HMAX\": 43961711264527806401144495397666817,\n \"PFLO\": 240,\n \"PFN\": 16\n}",
"stack.txt": "16384\n",
"scan_counts.txt": "float_evals 159726\nfloat_bins 1880291996\nexact_evals 21\nexact_bins 1284990\n"
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

# ---- one step of 256 walks (Section 3; counts printed by the generator gen4.c, ledger.txt) ----
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
GEN_IMAGE = int(sz[0]) + int(sz[1]) + int(sz[2])  # gen4: text + data + BSS, size(1); all arrays are static
GEN_STACK = int(rd('stack.txt')) if (INLINE or os.path.exists('stack.txt')) else 8192                                 # stack reserve; the run completes with the stack limited to this value (stack.txt, written by row.sh)
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
    G: the run `gen4 512 1000 5`: build count B (2^32 operations each),
       annealing iterations A (2^12 each, the rolling-horizon move and its undo), per trial 2^10 (constants, count, comparison, line)
       and 2^32 for the plan's row tables;
    K: none (design X: the constants are the closed form of proof.md Section 2; each trial's offsets are inside G's 2^10 per trial);
    P: the parameter scan (scan.c; counts in scan_counts.txt): float-model bins and evaluations 2^16 and 2^17 each,
       exact bins and evaluations 2^24 and 2^27 each, grid bookkeeping 2^20;
    O: `other4.py build`: 2^8 per emitted instruction, 2^13 per SHA-256 block of other.bin, pf.bin and data.bin, data image 2^12."""
    SWEEPS = 3; TOPK = int(re.search(r'^trials carried to the plan build (\d+)', led, re.M).group(1)); OPTIT = int(re.search(r'^annealing iterations per round (\d+)', led, re.M).group(1))
    plan_builds = 1 + SWEEPS * (320 * 31 + 320) + (NR - 1) + 1                # round-1 greedy (prefix builds counted as full) and the passes
    B = 512 + TOPK * (plan_builds + 1) + (plan_builds + 1)
    A = (TOPK + 1) * (NR - 1) * OPTIT
    G = B * 2 ** 32 + A * 2 ** 12 + 512 * 2 ** 10 + 2 ** 32 + 2 ** 34   # + the plan's row tables (mk_tables2 2^32, mk_tablesc 2^34)
    K = 0
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
assert c['e_eval'] == UNIT + 40
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
print('search memory', run_total, '; preprocessing (gen4): image', GEN_IMAGE, '+ stack', GEN_STACK, '+ program', CB['prog_bytes'], '=', pre_total, '(measured resident peak %d)' % GEN_HWM)
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
rounds 17, unit 4607 word operations
step of 256 walks: straight line 97242 (xor 71480 and 13243 or 10370 not 2149) + prefilter 15 + test 2 + counter 3 = 97262
parameters: DP = planes 145..255 zero and the 10 planes below them < 754 (theta = 754 x 2^-121 = 2^-111.441579), replay cap LRC = 61190 x 633825300114114700748351602688 = 11.0000 / theta, U 98040 trails, S 19608 table words (98040 slots), key bits 50
Tb = 1325551670394969607676875832282841088 = 535386056 * 2^91 = 0.99723424 * 2^120, evaluations 0.997234 * 2^128
failure terms: F6 1.570e-4  F2 4.841e-6  F3 1.053e-5  F4 4.269e-6  success bound 0.3900000007  (2^91 steps fewer: 0.3899999996)
lemma (ii): U E/n = 2^-111.4, E^2 theta/(2n) = 2^-112.4, U^2/(2 theta n) = 2^-112.4, delta < 2^-109, (1 - E/n)^-U / (1 - delta) = 1 + 2^-109.8, FL = 3.082e-33
hit counter: HMAX = 43961711264527806401144495397666817 ; P[abort before the stop on success] <= exp(-2354651652899128039112) < 2^-1000
replay: 9311 LRC + 13961 G + 17 nck + 4762 = 361143299189708658680986663841064528091 (G = 1978057332278404576875178995690, nck = 19607; measuring walk e + 10, walk of b e + 7, lock step 2e + 13, e = 4647)
main 128925806565955533981868297199493689901056  replay 361143299189708658680986663841064528091  rare 5758984175653142638549928943264581319  preprocessing 661063426650368 (builds 92729, annealing iterations 28800000000)
preprocessing parts: generator 516254297751552 basis 0 scan 144809126264832 assembly 2633984 (scan: float evaluations 159726 bins 1880291996, exact evaluations 21 bins 1284990; SHA-256 blocks 260)
preprocessing_log2: 2^37 < PRE / 4607 <= 2^38, declared 38
N = 129292708849320895783187834453341445660834
shares: main 0.99716 replay 0.00279 other 4.45e-05
      65120  register file, 2035 words
     331267  straight line incl. prefilter, 97257 instructions, two-address encoding (prog.bin + pf.bin)
      15976  other code (setup, loop, handlers, restart, replay), 1953 instructions x 8 bytes + 11 literals x 32 bytes
     627456  table, 19608 words (five slots each)
       8192  walk words of the 256 walks (LST | LID << 128), 256 words
        512  data image (lane constants K, PD, output pair), 16 words
search memory 1048523 ; preprocessing (gen4): image 570190 + stack 16384 + program 331218 = 917792 (measured resident peak 466944)
memory 1048523 <= 2^20 = 1048576 with a margin of 53 bytes (search phase 53 , preprocessing 130784 ): memory_log2_bytes = 20
certificate: 4607^100000 * 2^12440008 < N^100000 <= 4607^100000 * 2^12440009
time_log2 = 124.40009
score = time_log2 (memory reviewed separately) = 124.40009
```

## Appendix B. The generator (gen4.c) and the self-test (selftest.c)

Compiled with `gcc -O2 -static -nostdlib -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns -fno-stack-protector -fno-pie -no-pie -DNR=17 -DDESIGNX=1 -DTOPK=2`; run as `gen4 512 1000 5 i` under `nice -n 10 prlimit --as=1048576 --stack=16384`. (The source keeps the S3-04 code of gen3.c under `#if !DESIGNX`; its kbasis.h is not part of this build.)

```c
/* gen4.c - LS1 step generator for sha3-256-rNR (NR prefix rounds of Keccak-f[1600]), streaming version, design X.
 * This is gen3.c of entry a767dfcf (Jbenisek) with a new message embedding and the planning of the rows it creates; compiled with
 * -DDESIGNX=1 (the S3-04 code paths of gen3.c remain under #if !DESIGNX and are not used).  Program strings ("gen3") are kept.
 * Freestanding (no libc, static arrays only) so the measured peak resident memory is the generator's own working set.
 *
 * Chain function on physical 256-bit points u (4 lanes u0..u3), design X:
 *   v_x = u_x (x = 0..3), v_4 = XOR_(x<4) rotr(u_x, (ROT[4][2] - ROT[x][2]) mod 64), so XOR_x rotl(v_x, ROT[x][2]) = 0;
 *   message m(u) = 128 bytes = lanes 0..15 of the absorbed state:
 *     lane x = v_x ^ K[x] (row y = 0), lane 10+x = v_x ^ K[10+x] (row y = 2), x = 0..4;
 *     lanes 5..9 = all-ones, lane 15 = 0, lane 16 = 0x8000000000000006 (SHA3 pad); K[10+x] = K[x] ^ 0x5555..55 ^ (lane 16 if x = 1);
 *   F(u) = SHA3-256-rNR(m(u)) XOR PD   (PD = fixed digest polarity mask of the program).
 * Every column parity of the absorbed state is 0xaaaa..aa, so round-0 theta adds all-ones to every lane; round 0 is affine in u;
 * after round 0 the columns x = 3 and 4 are constant and C[2] = XOR_x rotl(v_x, ROT[x][2]) ^ const is constant, so D[3] of round 1
 * is constant: every chi row of round 1 has exactly one constant input (the lane of column 3) and four affine inputs.
 * Design-X additions to gen3.c: set_consts (the constants above), the build's input embedding, the table of rows with one
 * constant input (eval_rowc, mk_tablesc: ROWCc, ARGc, ARGEc), polopt1 planning those rows (rec_d = 2 + k), the build path that
 * applies their decisions, state planes of round 1 that share one node (pin sharing, pq_of) or are input nodes, MAXF 3840,
 * and polopt2 taking a constant state plane (two of them after round 1) by its value instead of skipping the round.
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
 * optmode 5 (polarity masks and output complements; the plan of this entry): (a) the D NOT of a lane (x,z) is a 5-bit mask
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
 * Outputs of the charged run (gen3 512 1000 5): the file prog.bin (two-address encoding, packed little-endian: 2-bit op, 1-bit t;
 * t=1: dst = a, then a and (not NOT) b; t=0: dst, a and (not NOT) b; registers 11 bits; 14, 25 or 36 bits) and the ledger on
 * standard output. No other file is written. The separate inspection command (gen3 1 TRIAL 5 inspect), a check run, writes
 * meta.txt and plan.txt (the decisions of the plan, read by the Python port); the search does not run it.
 * Usage: gen3 ntrials first optmode.  ntrials > 1: the cheap build (optmode 0) of trials first..first+ntrials-1, the
 * full build (optmode) of the TOPK lowest of them, and the lowest full count wins.  The search runs "gen3 512 1000 5". SC = 16, WLOOK = 3, OPTIT = 600,000,000, PCAP = 100.
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
#define MAXF 3840
static u64 form[MAXF][4]; static u16 formnode[MAXF]; static int nform, maxform;
#define FH 8192
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
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC||islin(v.n)) return; pS[l][z]=v.p; }
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
/* design X: rows with one constant input (position k, value = bit k of pat) and four distinct variable inputs.
   Abstract evaluation mirroring and2/xorv/notv: a value is a constant (id -1, pol = value) or a node id with a polarity. */
typedef struct { int id; int p; } AV;
static void eval_rowc(int k,int pat,int s,int T,int mc,int *cost,int *out,int *sel){
  AV bb[5]; int nid=5, c=0;
  for(int X=0;X<5;X++){ if(X==k){ bb[X].id=-1; bb[X].p=(pat>>X)&1; } else { bb[X].id=X; bb[X].p=((pat>>X)&1)^((s>>X)&1); if((s>>X)&1){ c++; bb[X].id=nid++; } } }
  AV NSp[5]; int bit=0; int ord[5]; row_order(T,ord);
  for(int X=0;X<5;X++) sel[X]=0;
  for(int i=0;i<5;i++){ int X=ord[i];
    AV a= ((T>>X)&1)? NSp[(X+1)%5] : bb[(X+1)%5]; a.p^=1; AV b=bb[(X+2)%5]; AV t;
    if(a.id<0) t= a.p? b : (AV){-1,0};
    else if(b.id<0) t= b.p? a : (AV){-1,0};
    else if(a.id==b.id) t= (a.p==b.p)? a : (AV){-1,0};
    else if(a.p==0&&b.p==0){ c+=1; t.id=nid++; t.p=0; }
    else if(a.p==1&&b.p==1){ c+=1; t.id=nid++; t.p=1; }
    else { int ch=(mc>>(bit++))&1; c+=2; sel[X]=ch; t.id=nid++; t.p=ch; }
    AV o; AV x=bb[X];
    if(t.id<0){ o=x; o.p^=t.p; }
    else if(x.id<0){ o=t; o.p^=x.p; }
    else if(x.id==t.id){ o.id=-1; o.p=x.p^t.p; }
    else { c+=1; o.id=nid++; o.p=x.p^t.p; }
    NSp[X]=o; }
  int o=0; for(int X=0;X<5;X++){ if(NSp[X].id<0){ *cost=99; *out=0; return; } o|=NSp[X].p<<X; }
  *cost=c; *out=o;
}
static signed char ROWCc[5][32][32]; static u16 ARGc[5][32][32]; static u8 ARGEc[5][32][32]; static int ROWMINc[5][32];
static void mk_tablesc(void){
  for(int k=0;k<5;k++) for(int p=0;p<32;p++) for(int o=0;o<32;o++){ ROWCc[k][p][o]=99; ARGc[k][p][o]=0; ARGEc[k][p][o]=0; }
  for(int k=0;k<5;k++) for(int pass=0;pass<2;pass++)
  for(int p=0;p<32;p++) for(int T=0;T<31;T++) for(int s=0;s<32;s++){ if((s>>k)&1) continue;
    for(int mc=0;mc<32;mc++){
      int c,o,sel[5]; eval_rowc(k,p,s,T,mc,&c,&o,sel);
      if(c>=99) continue;
      if(pass==0){ if(c<ROWCc[k][p][o]){ ROWCc[k][p][o]=(signed char)c; ARGc[k][p][o]=(u16)(s|(T<<5)|(mc<<10)); ARGEc[k][p][o]=0; } }
      else for(int E=1;E<32;E++){ int pc=(E&1)+((E>>1)&1)+((E>>2)&1)+((E>>3)&1)+((E>>4)&1); int c2=c+pc, o2=o^E;
        if(c2<ROWCc[k][p][o2]){ ROWCc[k][p][o2]=(signed char)c2; ARGc[k][p][o2]=(u16)(s|(T<<5)|(mc<<10)); ARGEc[k][p][o2]=(u8)E; } }
    } }
  for(int k=0;k<5;k++) for(int p=0;p<32;p++){ int m=99; for(int o=0;o<32;o++) if(ROWCc[k][p][o]<m) m=ROWCc[k][p][o]; ROWMINc[k][p]=m; }
}
static void polopt2(int r){
  static u8 pS[25][64], pC[5][64], pD[5][64];
  static u16 vrow[5][64][5]; static u8 vbit[5][64][5];
  static u8 pat0[320], pat1[320], outv[320];
  static u8 bf[5][64], bg[5][64], bo[320];
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; pS[l][z]=v.p; }   /* design X: a constant state plane (round 2) enters by its value */
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
#define RCT1(i,o) (rec_d[i]==1? ROWCt[pat0[i]][o] : ROWCc[rec_d[i]-2][pat0[i]][o])
#define ARG1(i,o) (rec_d[i]==1? ARGt[pat0[i]][o] : ARGc[rec_d[i]-2][pat0[i]][o])
#define ARGE1(i,o) (rec_d[i]==1? ARGE[pat0[i]][o] : ARGEc[rec_d[i]-2][pat0[i]][o])
static void polopt1(void){
  const int r=1;
  static u16 vrow[5][64][5]; static u8 vbit[5][64][5];
  static u8 pat0[320], pat1[320], outv[320], bo[320];
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++){
    int Y=(2*(x-y)+10)%5, z=(zz+ROT[x][y])&63; int row=Y*64+z; vrow[x][zz][y]=(u16)row; vbit[x][zz][y]=(u8)(1<<y); }
  for(int i=0;i<320;i++){ pat0[i]=rec_p[i]; outv[i]=rec_o[i]; }
  for(int i=0;i<320;i++) if(rec_d[i]){ int bo_=0,bc=99; for(int o=0;o<32;o++) if(RCT1(i,o)<bc){ bc=RCT1(i,o); bo_=o; } outv[i]=(u8)bo_; }
  static u8 q[25][64], qC[5][64], qD[5][64];
  for(int Y=0;Y<5;Y++) for(int z=0;z<64;z++) for(int X=0;X<5;X++) q[X+5*Y][z]=(outv[Y*64+z]>>X)&1;
  for(int z=0;z<64;z++) q[0][z]^=(u8)((RC[r]>>z)&1);
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ int p=0; for(int y=0;y<5;y++) p^=q[x+5*y][z]; qC[x][z]=(u8)p; }
  for(int x=0;x<5;x++) for(int z=0;z<64;z++) qD[x][z]=qC[(x+4)%5][z]^qC[(x+1)%5][(z+63)&63];
  for(int i=0;i<320;i++) pat1[i]=0;
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++) if(q[x+5*y][zz]^qD[x][zz]) pat1[vrow[x][zz][y]]|=(u8)(1<<y);
  int nextlast=(r+1==NR-1);
  const int *rtL=tC[1][mixfree];
  #define G0(i) (!rec_d[i]? 0 : ((RCT1(i,outv[i])>=90)? 1000 : (int)RCT1(i,outv[i])))
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
  for(int i=0;i<320;i++) if(rec_d[i]){ int o=bo[i]; if(RCT1(i,o)>=90) die("polopt1: infeasible row"); dec[1][i]=ARG1(i,o); decE[1][i]=ARGE1(i,o); c0t+=RCT1(i,o); }
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
static u16 pq_of[W]; static long nshare;
static void pin_state(void){
  for(int q=0;q<1600;q++){ preg[q]=0xFFFF; plast[q]=NOUSE; pfl[q]=0; }
  npin=0;
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC) continue;
    if(v.n>=PIN) die("state plane from an earlier round");
    /* design X: a round-1 output may be linear (a row with a constant input) */
    if(nlast[v.n]==0xFFFE){ S[l][z].n=(u16)(PIN+pq_of[v.n]); nshare++; continue; }   /* design X: planes with one node share its pin */
    int q=l*64+z; pord[q]=v.n; pfl[q]=(u8)(nf[v.n]&F_OPM); preg[q]= emitting? nreg[v.n] : 0; npin++;
    nlast[v.n]=0xFFFE; pq_of[v.n]=(u16)q; S[l][z].n=(u16)(PIN+q); }
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
#if DESIGNX
  /* design X: v_x = u_x (x<4), v_4[w] = XOR_{x<4} v_x[w+R4-Rx] (so XOR_x rotl(v_x,ROT[x][2]) = 0);
     lane x = v_x ^ KL[x], lane 10+x = v_x ^ KL[10+x] */
  { static V vv[5][64];
    for(int x=0;x<4;x++) for(int z=0;z<64;z++) vv[x][z]=MK(64*x+z,0);
    for(int w=0;w<64;w++){ V a=K_(0); for(int x=0;x<4;x++) a=xorv(a,vv[x][(w+ROT[4][2]-ROT[x][2]+128)&63]); vv[4][w]=a; }
    for(int x=0;x<5;x++) for(int z=0;z<64;z++){ S[x][z]=xorv(vv[x][z],K_((KL[x]>>z)&1)); S[10+x][z]=xorv(vv[x][z],K_((KL[10+x]>>z)&1)); }
  }
#else
  for(int z=0;z<64;z++){
    S[1][z]=MK(z,(KL[1]>>z)&1); S[6][z]=MK(64+z,(KL[6]>>z)&1);
    S[4][z]=MK(128+z,(KL[4]>>z)&1); S[9][z]=MK(192+z,(KL[9]>>z)&1);
  }
  for(int z=0;z<64;z++){
    S[11][z]=xorv(xorv(MK(z,0),MK(64+z,0)),K_((KL[11]>>z)&1));
    S[14][z]=xorv(xorv(MK(128+z,0),MK(192+z,0)),K_((KL[14]>>z)&1));
  }
#endif
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
      int onec=-1;
#if DESIGNX
      if(!distinct){ int nk=0, kk=-1, dv=1; for(int X=0;X<5;X++){ if(b[X].n==NC){ nk++; kk=X; } else for(int X2=X+1;X2<5;X2++) if(b[X2].n!=NC && b[X].n==b[X2].n) dv=0; } if(nk==1 && dv) onec=kk; }
#endif
      int best,bj;
      int havesel=0, rsel[5]={0,0,0,0,0}, Tm=0, rowE=0;
      if(recmode && r==1){ int pp=0; for(int X=0;X<5;X++) pp|=b[X].p<<X; rec_p[Y*64+z]=(u8)pp; rec_d[Y*64+z]=(u8)(distinct? 1 : onec>=0? 2+onec : 0); }
      if(distinct && optmode>=4 && (r>=2 || (r==1 && optmode>=5)) && !last && decd[r]){ int p=0; for(int X=0;X<5;X++) p|=b[X].p<<X;
        u16 dd=dec[r][Y*64+z]; rowE=decE[r][Y*64+z]; best=dd&31; Tm=(dd>>5)&31; bj=-1; int cc,oo; eval_row(p,best,Tm,dd>>10,&cc,&oo,rsel); havesel=1; }
      else if(onec>=0 && r==1 && optmode>=5 && !last && decd[r]){ int p=0; for(int X=0;X<5;X++) p|=b[X].p<<X;
        u16 dd=dec[r][Y*64+z]; rowE=decE[r][Y*64+z]; best=dd&31; Tm=(dd>>5)&31; bj=-1; int cc,oo; eval_rowc(onec,p,best,Tm,dd>>10,&cc,&oo,rsel); havesel=1; }
      else if(distinct){ int p=0; for(int X=0;X<5;X++) p|=b[X].p<<X; best=tS[last][mixfree][p]; bj=tJ[last][mixfree][p]; }
      else best=row_choose(b,needmask,&bj,0);
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
    }
    if(recmode && r==1){ for(int Y=0;Y<5;Y++) for(int z=0;z<64;z++){ int o=0; for(int X=0;X<5;X++) o|=(NS[X+5*Y][z].p&1)<<X; rec_o[Y*64+z]=(u8)o; } return; }
    for(int z=0;z<64;z++) NS[0][z].p^=(RC[r]>>z)&1;   /* iota */
    for(int l=0;l<25;l++) for(int z=0;z<64;z++) S[l][z]=NS[l][z];
    if(r==0) continue;
    g_r=r; finish_round(last, r==1);
    if(r==1 && stop_prefix){ prefix_ops=cnt[1]+cnt[2]+cnt[3]+cnt[4]; return; }
  }
}

static u64 rs;
static u64 xs(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static int use_r; static u64 force_r;
#if DESIGNX
/* design X constants (proof.md Section 2): lanes 5..9 all-ones, lane 15 zero, lane 16 the padding; lane x = c_x and lane 10+x =
   c_x ^ K_x with K_x = 0x5555...55 ^ (lane 15 for x = 0, lane 16 for x = 1), so that every column parity of the absorbed state is
   0xaaaa...aa ^ (its variable part, which is zero) and D of round 0 is all-ones; trial t draws the offsets c_0..c_4 from xorshift. */
static void set_consts(int trial){
  const u64 P5=0x5555555555555555UL;
  for(int l=0;l<25;l++) KL[l]=0;
  KL[16]=0x8000000000000006UL; KL[15]=0;
  rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs();
  for(int x=0;x<5;x++){ u64 c=xs(); u64 K=P5 ^ (x==0? KL[15] : x==1? KL[16] : 0); KL[x]=c; KL[10+x]=c^K; KL[5+x]=~0UL; }
}
#else
#include "kbasis.h"
static void set_consts(int trial){
  for(int l=0;l<25;l++) KL[l]=0;
  KL[16]=0x8000000000000006UL;
  if(use_r){ static const int fl2[12]={0,2,3,5,7,8,10,12,13,15,11,14}; u64 r=force_r; for(int i=0;i<12;i++){ u64 k=KB0[i]; for(int j=0;j<64;j++) if((r>>j)&1) k^=KBV[j][i]; KL[fl2[i]]=k; } return; }
  if(trial>=1000){ static const int fl2[12]={0,2,3,5,7,8,10,12,13,15,11,14}; /* S3-04: a structured set, r from the trial seed */
    rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs(); u64 r=xs();
    for(int i=0;i<12;i++){ u64 k=KB0[i]; for(int j=0;j<64;j++) if((r>>j)&1) k^=KBV[j][i]; KL[fl2[i]]=k; } return; }
  if(trial>0){ rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs();
    static const int fl[12]={0,2,3,5,7,8,10,12,13,15,11,14};
    for(int i=0;i<12;i++) KL[fl[i]]=xs(); }
}

#endif
static long r1gain;
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
  if(optmode>=3) r1greedy();
  memset(phib,0,sizeof phib); memset(mixb,0,sizeof mixb); memset(decided,0,sizeof decided); memset(decd,0,sizeof decd);
  memset(pol_phi,0,sizeof pol_phi); memset(pol_pred,0,sizeof pol_pred); memset(pol_nots,0,sizeof pol_nots);
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
  mk_tables(); mk_tables2(); mk_tablesc();
  int ntr= argc>1? atoi_(argv[1]) : 1; if(ntr<1) ntr=1;
  int t0= argc>2? atoi_(argv[2]) : 0;
  if(argc>3) optmode=atoi_(argv[3]);
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
  #if DESIGNX
  os("design X: lane x = v_x ^ K_x, lane 10+x = v_x ^ K_(10+x) (x = 0..4); v_x = u_x (x < 4); v_4 = XOR_(x<4) rotr(u_x, (ROT[4][2]-ROT[x][2]) mod 64)\n");
#else
  os("varlanes 1 6 4 9 ; lane11 = u0^u1^K11 ; lane14 = u2^u3^K14\n");
#endif
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
    os("constants trial "); ou(bestt); os(" of "); ou(ntr); os(" ; optmode "); ou(optmode); os(" ; round-1 greedy gain "); ou(r1gain); oc('\n');
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

The self-test (compiled with `gcc -O2 -DRR=17 -DDESIGNX=1`; `selftest kat` prints 300 known answers, compared with hashlib and the organizer's verifier/keccak.py by kat_check.py; `selftest run 4 [seed]` runs the chained check):

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

static u64 KL[25], PD[4]; static long ninstr;
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
  }
  fclose(f);
  f=fopen("prog.bin","rb"); if(!f){ perror("prog.bin"); exit(2); }
  fseek(f,0,SEEK_END); progbytes=ftell(f); fseek(f,0,SEEK_SET);
  prog=calloc(progbytes+8,1); if(fread(prog,1,progbytes,f)!=(size_t)progbytes){ fprintf(stderr,"short prog\n"); exit(2); } fclose(f);
  decode_prog();
}
/* message m(u): 128 bytes = lanes 0..15 */
static const int ROT2[5]={3,10,43,25,39}; /* ROT[x][2] */
static u64 bitrot(u64 v,int r){ r&=63; return r? (v<<r)|(v>>(64-r)) : v; }
static void msg_of(const u64 u[4], uint8_t m[128]){
  u64 L[16]; for(int i=0;i<16;i++) L[i]=KL[i];
#if DESIGNX
  /* v_4[w] = XOR_{x<4} u_x[w+R4-Rx]  <=>  v_4 = XOR_{x<4} rotr(u_x, R4-Rx) */
  u64 v[5]; for(int x=0;x<4;x++) v[x]=u[x];
  v[4]=0; for(int x=0;x<4;x++) v[4]^=bitrot(u[x],64-((ROT2[4]-ROT2[x]+128)%64));
  for(int x=0;x<5;x++){ L[x]=v[x]^KL[x]; L[10+x]=v[x]^KL[10+x]; }
#else
  L[1]=u[0]; L[6]=u[1]; L[11]=u[0]^u[1]^KL[11];
  L[4]=u[2]; L[9]=u[3]; L[14]=u[2]^u[3]^KL[14];
#endif
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
  printf("selftest: %ld chained evaluations (%d batches x 256 trails x 4 steps), %ld mismatches, %ld instructions\n",evals,nb,mism,ninstr);
  return mism?1:0;
}
```

```python
# kat_check.py NR < kat.txt : compares the self-test KAT lines with hashlib (24 rounds) and the organizer's verifier (NR rounds)
import sys, hashlib
sys.path.insert(0, sys.argv[2])
from verifier import keccak
NR = int(sys.argv[1]); n = m24 = mnr = 0
for line in sys.stdin:
    m, d24, dnr = line.split() if len(line.split()) == 3 else ('',) + tuple(line.split())
    msg = bytes.fromhex(m)
    n += 1
    m24 += hashlib.sha3_256(msg).hexdigest() != d24
    mnr += keccak.sha3_256(msg, rounds=NR).hex() != dnr
print('kat messages %d (lengths 0..%d): 24-round vs hashlib mismatches %d; %d-round vs organizer verifier mismatches %d' % (n, n - 1, m24, NR, mnr))
```

Output of the run (the ledger, standard output), of the check run and of the self-test:

```
trial 1000 ops 101076
trial 1001 ops 101103
trial 1002 ops 101112
trial 1003 ops 101085
trial 1004 ops 101050
trial 1005 ops 101103
trial 1006 ops 101008
trial 1007 ops 101084
trial 1008 ops 100991
trial 1009 ops 101081
trial 1010 ops 101136
trial 1011 ops 101002
trial 1012 ops 101032
trial 1013 ops 101100
trial 1014 ops 101056
trial 1015 ops 101117
trial 1016 ops 101099
trial 1017 ops 101171
trial 1018 ops 101025
trial 1019 ops 100994
trial 1020 ops 101042
trial 1021 ops 101147
trial 1022 ops 101049
trial 1023 ops 101127
trial 1024 ops 101039
trial 1025 ops 101063
trial 1026 ops 101046
trial 1027 ops 101142
trial 1028 ops 101156
trial 1029 ops 101017
trial 1030 ops 101032
trial 1031 ops 101019
trial 1032 ops 101058
trial 1033 ops 101079
trial 1034 ops 101160
trial 1035 ops 101064
trial 1036 ops 100971
trial 1037 ops 101041
trial 1038 ops 101027
trial 1039 ops 101142
trial 1040 ops 101137
trial 1041 ops 101163
trial 1042 ops 100982
trial 1043 ops 101112
trial 1044 ops 101137
trial 1045 ops 101147
trial 1046 ops 101106
trial 1047 ops 101032
trial 1048 ops 101010
trial 1049 ops 100992
trial 1050 ops 101107
trial 1051 ops 101044
trial 1052 ops 101060
trial 1053 ops 101066
trial 1054 ops 101138
trial 1055 ops 101038
trial 1056 ops 101143
trial 1057 ops 101121
trial 1058 ops 101003
trial 1059 ops 101011
trial 1060 ops 100997
trial 1061 ops 101159
trial 1062 ops 101027
trial 1063 ops 101009
trial 1064 ops 101103
trial 1065 ops 101120
trial 1066 ops 101046
trial 1067 ops 101071
trial 1068 ops 101037
trial 1069 ops 101050
trial 1070 ops 101108
trial 1071 ops 100990
trial 1072 ops 101112
trial 1073 ops 101038
trial 1074 ops 101069
trial 1075 ops 101057
trial 1076 ops 101127
trial 1077 ops 101129
trial 1078 ops 100974
trial 1079 ops 101116
trial 1080 ops 101090
trial 1081 ops 101044
trial 1082 ops 101188
trial 1083 ops 101075
trial 1084 ops 100998
trial 1085 ops 100983
trial 1086 ops 100968
trial 1087 ops 101127
trial 1088 ops 101052
trial 1089 ops 101002
trial 1090 ops 101035
trial 1091 ops 101028
trial 1092 ops 101046
trial 1093 ops 101009
trial 1094 ops 100980
trial 1095 ops 101087
trial 1096 ops 101074
trial 1097 ops 101138
trial 1098 ops 101083
trial 1099 ops 101091
trial 1100 ops 101009
trial 1101 ops 100935
trial 1102 ops 101129
trial 1103 ops 101126
trial 1104 ops 101085
trial 1105 ops 101077
trial 1106 ops 100909
trial 1107 ops 101062
trial 1108 ops 101006
trial 1109 ops 101004
trial 1110 ops 101071
trial 1111 ops 101074
trial 1112 ops 101133
trial 1113 ops 101085
trial 1114 ops 101104
trial 1115 ops 101084
trial 1116 ops 100984
trial 1117 ops 101094
trial 1118 ops 101055
trial 1119 ops 101027
trial 1120 ops 101075
trial 1121 ops 101004
trial 1122 ops 101070
trial 1123 ops 101075
trial 1124 ops 101001
trial 1125 ops 101061
trial 1126 ops 101110
trial 1127 ops 101041
trial 1128 ops 101062
trial 1129 ops 100954
trial 1130 ops 101059
trial 1131 ops 101035
trial 1132 ops 101203
trial 1133 ops 101069
trial 1134 ops 101079
trial 1135 ops 101121
trial 1136 ops 101110
trial 1137 ops 101076
trial 1138 ops 101045
trial 1139 ops 101115
trial 1140 ops 101102
trial 1141 ops 101129
trial 1142 ops 100987
trial 1143 ops 101072
trial 1144 ops 101007
trial 1145 ops 101038
trial 1146 ops 101089
trial 1147 ops 101156
trial 1148 ops 101089
trial 1149 ops 101074
trial 1150 ops 101092
trial 1151 ops 101158
trial 1152 ops 101097
trial 1153 ops 100990
trial 1154 ops 101126
trial 1155 ops 101017
trial 1156 ops 101094
trial 1157 ops 101046
trial 1158 ops 101033
trial 1159 ops 100978
trial 1160 ops 101116
trial 1161 ops 101029
trial 1162 ops 101034
trial 1163 ops 101076
trial 1164 ops 101020
trial 1165 ops 101096
trial 1166 ops 101062
trial 1167 ops 101123
trial 1168 ops 100963
trial 1169 ops 101152
trial 1170 ops 101034
trial 1171 ops 101039
trial 1172 ops 101086
trial 1173 ops 100974
trial 1174 ops 101009
trial 1175 ops 101066
trial 1176 ops 101101
trial 1177 ops 101102
trial 1178 ops 101020
trial 1179 ops 101057
trial 1180 ops 101041
trial 1181 ops 101097
trial 1182 ops 101081
trial 1183 ops 100980
trial 1184 ops 101035
trial 1185 ops 101050
trial 1186 ops 101124
trial 1187 ops 101080
trial 1188 ops 101034
trial 1189 ops 101090
trial 1190 ops 101140
trial 1191 ops 101148
trial 1192 ops 100999
trial 1193 ops 101071
trial 1194 ops 101024
trial 1195 ops 100979
trial 1196 ops 101047
trial 1197 ops 101066
trial 1198 ops 101028
trial 1199 ops 101129
trial 1200 ops 101008
trial 1201 ops 101062
trial 1202 ops 101095
trial 1203 ops 100938
trial 1204 ops 101050
trial 1205 ops 101124
trial 1206 ops 101145
trial 1207 ops 101059
trial 1208 ops 101026
trial 1209 ops 101075
trial 1210 ops 100998
trial 1211 ops 101042
trial 1212 ops 101160
trial 1213 ops 101078
trial 1214 ops 101020
trial 1215 ops 101004
trial 1216 ops 101131
trial 1217 ops 101080
trial 1218 ops 100977
trial 1219 ops 101218
trial 1220 ops 101136
trial 1221 ops 101090
trial 1222 ops 101034
trial 1223 ops 101099
trial 1224 ops 101094
trial 1225 ops 101050
trial 1226 ops 101093
trial 1227 ops 101181
trial 1228 ops 101044
trial 1229 ops 101115
trial 1230 ops 101015
trial 1231 ops 101090
trial 1232 ops 101078
trial 1233 ops 100989
trial 1234 ops 101174
trial 1235 ops 101038
trial 1236 ops 101117
trial 1237 ops 101070
trial 1238 ops 100979
trial 1239 ops 101052
trial 1240 ops 100993
trial 1241 ops 101061
trial 1242 ops 101153
trial 1243 ops 101049
trial 1244 ops 101117
trial 1245 ops 101152
trial 1246 ops 101082
trial 1247 ops 101068
trial 1248 ops 101015
trial 1249 ops 101028
trial 1250 ops 101096
trial 1251 ops 101039
trial 1252 ops 101016
trial 1253 ops 101022
trial 1254 ops 101024
trial 1255 ops 101090
trial 1256 ops 101089
trial 1257 ops 101018
trial 1258 ops 101106
trial 1259 ops 101050
trial 1260 ops 101136
trial 1261 ops 100924
trial 1262 ops 101048
trial 1263 ops 101057
trial 1264 ops 101103
trial 1265 ops 101065
trial 1266 ops 101006
trial 1267 ops 101118
trial 1268 ops 100968
trial 1269 ops 101067
trial 1270 ops 101032
trial 1271 ops 101101
trial 1272 ops 101076
trial 1273 ops 101061
trial 1274 ops 101049
trial 1275 ops 101092
trial 1276 ops 100987
trial 1277 ops 100978
trial 1278 ops 100997
trial 1279 ops 101128
trial 1280 ops 101019
trial 1281 ops 101066
trial 1282 ops 101136
trial 1283 ops 101166
trial 1284 ops 100962
trial 1285 ops 101069
trial 1286 ops 101135
trial 1287 ops 101136
trial 1288 ops 101024
trial 1289 ops 100997
trial 1290 ops 101074
trial 1291 ops 101075
trial 1292 ops 101087
trial 1293 ops 101128
trial 1294 ops 101133
trial 1295 ops 101117
trial 1296 ops 101132
trial 1297 ops 101042
trial 1298 ops 101007
trial 1299 ops 101041
trial 1300 ops 101010
trial 1301 ops 100890
trial 1302 ops 101113
trial 1303 ops 101057
trial 1304 ops 100951
trial 1305 ops 100992
trial 1306 ops 100979
trial 1307 ops 101038
trial 1308 ops 101106
trial 1309 ops 101099
trial 1310 ops 101129
trial 1311 ops 101008
trial 1312 ops 101109
trial 1313 ops 101041
trial 1314 ops 101082
trial 1315 ops 100996
trial 1316 ops 101064
trial 1317 ops 101106
trial 1318 ops 101044
trial 1319 ops 101035
trial 1320 ops 101056
trial 1321 ops 101055
trial 1322 ops 101171
trial 1323 ops 101092
trial 1324 ops 101051
trial 1325 ops 100987
trial 1326 ops 101139
trial 1327 ops 101022
trial 1328 ops 101090
trial 1329 ops 101062
trial 1330 ops 101177
trial 1331 ops 101125
trial 1332 ops 101027
trial 1333 ops 101090
trial 1334 ops 101111
trial 1335 ops 100975
trial 1336 ops 101141
trial 1337 ops 101024
trial 1338 ops 101086
trial 1339 ops 101020
trial 1340 ops 101127
trial 1341 ops 101019
trial 1342 ops 101125
trial 1343 ops 101089
trial 1344 ops 101035
trial 1345 ops 101040
trial 1346 ops 101031
trial 1347 ops 101044
trial 1348 ops 101139
trial 1349 ops 101035
trial 1350 ops 101106
trial 1351 ops 101120
trial 1352 ops 101078
trial 1353 ops 101102
trial 1354 ops 101052
trial 1355 ops 101189
trial 1356 ops 101116
trial 1357 ops 101105
trial 1358 ops 101117
trial 1359 ops 101015
trial 1360 ops 101045
trial 1361 ops 101011
trial 1362 ops 101005
trial 1363 ops 101075
trial 1364 ops 101100
trial 1365 ops 101060
trial 1366 ops 100976
trial 1367 ops 101073
trial 1368 ops 101060
trial 1369 ops 101101
trial 1370 ops 101069
trial 1371 ops 101140
trial 1372 ops 101103
trial 1373 ops 101061
trial 1374 ops 101046
trial 1375 ops 101090
trial 1376 ops 101043
trial 1377 ops 100992
trial 1378 ops 101068
trial 1379 ops 101076
trial 1380 ops 101109
trial 1381 ops 101087
trial 1382 ops 101046
trial 1383 ops 101033
trial 1384 ops 101084
trial 1385 ops 100997
trial 1386 ops 101068
trial 1387 ops 101058
trial 1388 ops 101071
trial 1389 ops 101084
trial 1390 ops 101166
trial 1391 ops 101058
trial 1392 ops 101151
trial 1393 ops 101013
trial 1394 ops 101067
trial 1395 ops 101048
trial 1396 ops 101084
trial 1397 ops 101169
trial 1398 ops 101123
trial 1399 ops 101068
trial 1400 ops 101046
trial 1401 ops 101104
trial 1402 ops 101113
trial 1403 ops 101108
trial 1404 ops 101053
trial 1405 ops 100989
trial 1406 ops 101151
trial 1407 ops 101129
trial 1408 ops 101077
trial 1409 ops 101027
trial 1410 ops 101063
trial 1411 ops 101000
trial 1412 ops 101169
trial 1413 ops 101041
trial 1414 ops 101052
trial 1415 ops 101036
trial 1416 ops 101152
trial 1417 ops 101063
trial 1418 ops 101090
trial 1419 ops 101017
trial 1420 ops 101108
trial 1421 ops 101153
trial 1422 ops 101090
trial 1423 ops 101079
trial 1424 ops 101097
trial 1425 ops 101027
trial 1426 ops 101050
trial 1427 ops 101066
trial 1428 ops 101106
trial 1429 ops 101179
trial 1430 ops 101079
trial 1431 ops 101008
trial 1432 ops 101121
trial 1433 ops 101004
trial 1434 ops 101113
trial 1435 ops 101146
trial 1436 ops 101044
trial 1437 ops 100998
trial 1438 ops 101041
trial 1439 ops 101011
trial 1440 ops 101182
trial 1441 ops 101063
trial 1442 ops 101039
trial 1443 ops 101054
trial 1444 ops 101118
trial 1445 ops 101072
trial 1446 ops 101068
trial 1447 ops 101011
trial 1448 ops 101054
trial 1449 ops 100963
trial 1450 ops 101043
trial 1451 ops 101035
trial 1452 ops 101104
trial 1453 ops 101003
trial 1454 ops 101152
trial 1455 ops 101056
trial 1456 ops 101117
trial 1457 ops 101066
trial 1458 ops 101019
trial 1459 ops 100999
trial 1460 ops 101137
trial 1461 ops 100984
trial 1462 ops 100970
trial 1463 ops 101153
trial 1464 ops 101103
trial 1465 ops 101024
trial 1466 ops 101093
trial 1467 ops 100985
trial 1468 ops 101070
trial 1469 ops 101036
trial 1470 ops 101053
trial 1471 ops 100988
trial 1472 ops 101043
trial 1473 ops 101086
trial 1474 ops 101100
trial 1475 ops 101073
trial 1476 ops 101052
trial 1477 ops 101054
trial 1478 ops 101090
trial 1479 ops 101116
trial 1480 ops 101035
trial 1481 ops 100989
trial 1482 ops 100998
trial 1483 ops 101032
trial 1484 ops 101098
trial 1485 ops 101052
trial 1486 ops 101064
trial 1487 ops 100988
trial 1488 ops 101132
trial 1489 ops 101082
trial 1490 ops 101064
trial 1491 ops 101095
trial 1492 ops 101120
trial 1493 ops 101036
trial 1494 ops 101064
trial 1495 ops 101052
trial 1496 ops 100969
trial 1497 ops 100921
trial 1498 ops 101134
trial 1499 ops 101062
trial 1500 ops 101089
trial 1501 ops 100974
trial 1502 ops 101105
trial 1503 ops 101025
trial 1504 ops 101056
trial 1505 ops 101068
trial 1506 ops 101120
trial 1507 ops 101021
trial 1508 ops 100992
trial 1509 ops 101049
trial 1510 ops 101029
trial 1511 ops 101040
plan trial 1301 cheap 100890 full 97242
plan trial 1106 cheap 100909 full 97266
LS1 step ledger (256 lanes, one chain step, 17 rounds), streaming generator gen3
XOR 71480
AND 13243
OR  10370
NOT 2149  (row complements chosen pre-DCE: 207)
LOAD 0
STORE 0
TOTAL 97242
TRICKROWS 4593 ; forced term polarities 0
feed NOTs 0 (digest polarity folded into the chain function: F(u)=H(m(u))^PD)
nodes created pre-DCE 97372 ; ring peak 6847 of 8192 ; linear forms 1813 of 3840
max live values 2024 ; registers used 2024 (limit 2304)
constants trial 1301 of 512 ; optmode 5 ; round-1 greedy gain 118
annealing iterations per round 600000000
trials carried to the plan build 2
plan r2 predicted row cost 1643 theta NOTs 93 free polarities set 0
plan r3 predicted row cost 1643 theta NOTs 94 free polarities set 0
plan r4 predicted row cost 1638 theta NOTs 96 free polarities set 0
plan r5 predicted row cost 1646 theta NOTs 103 free polarities set 0
plan r6 predicted row cost 1643 theta NOTs 93 free polarities set 0
plan r7 predicted row cost 1647 theta NOTs 95 free polarities set 0
plan r8 predicted row cost 1643 theta NOTs 98 free polarities set 0
plan r9 predicted row cost 1649 theta NOTs 90 free polarities set 0
plan r10 predicted row cost 1651 theta NOTs 110 free polarities set 0
plan r11 predicted row cost 1635 theta NOTs 101 free polarities set 0
plan r12 predicted row cost 1647 theta NOTs 100 free polarities set 0
plan r13 predicted row cost 1643 theta NOTs 102 free polarities set 0
plan r14 predicted row cost 1653 theta NOTs 100 free polarities set 0
plan r15 predicted row cost 1637 theta NOTs 90 free polarities set 0
plan r16 predicted row cost 261 theta NOTs 14 free polarities set 5
cum after round 1 3208
cum after round 2 9740
cum after round 3 16277
cum after round 4 22811
cum after round 5 29360
cum after round 6 35896
cum after round 7 42438
cum after round 8 48979
cum after round 9 55518
cum after round 10 62079
cum after round 11 68615
cum after round 12 75162
cum after round 13 81707
cum after round 14 88260
cum after round 15 94787
cum after round 16 97242
generator peak RSS (VmHWM, this process image) 456 KiB = 466944 bytes (limit 1048576)
worker peak RSS (getrusage via wait4, worker forked from the 1-page parent) 256 KiB = 262144 bytes (limit 1048576)
the charged run wrote prog.bin, meta.txt and plan.txt
selftest: 4096 chained evaluations (4 batches x 256 trails x 4 steps), 0 mismatches, 97242 instructions
selftest: 4096 chained evaluations (4 batches x 256 trails x 4 steps), 0 mismatches, 97242 instructions
kat messages 300 (lengths 0..299): 24-round vs hashlib mismatches 0; 17-round vs organizer verifier mismatches 0
```

## Appendix C. The measured check of H_rand (hrand_test.c)

Unchanged from a767dfcf; compiled with `gcc -O2 hrand_test.c -lm`, run in the directory of prog.bin and meta.txt (output in Section 7.2).

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
{"NR": 17, "HF": 111, "DPLO": 145, "DK": 10, "DT": 754, "S": 19608, "U": 98040, "SB": 15, "W": 633825300114114700748351602688, "J": 61190, "LRC": 38783770113982678538791634568478720, "Tb": 1325551670394969607676875832282841088, "HMAX": 43961711264527806401144495397666817, "PFLO": 240, "PFN": 16}
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
RB0 = 2024   # the registers the straight line names (generator ledger: registers used)
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


ROT2 = [3, 10, 43, 25, 39]                                             # ROT[x][2], x = 0..4 (rho offsets of lanes 10..14)


def build_state(A, MISC):
    """W0..W6 := the 1600-bit state of the one-block message m(u), u in UU (37 instructions).  Design X (proof.md Section 2):
    lane x = v_x ^ K_x and lane 10 + x = v_x ^ K_(10+x), v_x = u_x (x < 4), v_4 = XOR_(x<4) rotr(u_x, (ROT[4][2] - ROT[x][2]) mod 64);
    the data image holds every K_l (the offsets of the variable lanes included)."""
    for i in range(7): A.lda(W0 + i, MISC + i)
    A.xor(W0, W0, UU)                                        # lanes 0..3  ^= u0..u3
    A.shli(TQ, UU, 128); A.xor(W0 + 2, W0 + 2, TQ)           # lanes 10, 11 ^= u0, u1
    A.shri(TQ, UU, 128); A.xor(W0 + 3, W0 + 3, TQ)           # lanes 12, 13 ^= u2, u3
    for x in range(4):                                       # X2 := v_4 (bits 0..63; bits above cleared at the end)
        d = (ROT2[4] - ROT2[x]) % 64
        if x == 0: A.andi(X0, UU, M64)
        elif x < 3: A.shri(X0, UU, 64 * x); A.andi(X0, X0, M64)
        else: A.shri(X0, UU, 192)
        A.shli(X1, X0, 64); A.or_(X0, X0, X1)                 # u_x in bits 0..63 and 64..127
        if x == 0: A.shri(X2, X0, d)                         # bits 0..63 = rotr(u_x, d)
        else: A.shri(X0, X0, d); A.xor(X2, X2, X0)
    A.andi(X2, X2, M64)
    A.xor(W0 + 1, W0 + 1, X2)                                # lane 4 ^= v_4
    A.shli(TQ, X2, 128); A.xor(W0 + 3, W0 + 3, TQ)           # lane 14 ^= v_4


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
    """16 words: KW[0..6] (lane constants K of the absorbed state; for the ten variable lanes their offsets), PD, then 8 output words"""
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
    v = [(u >> (64 * i)) & M64 for i in range(4)]
    v.append(0)
    for x in range(4):
        d = (ROT2[4] - ROT2[x]) % 64
        v[4] ^= ((v[x] >> d) | (v[x] << (64 - d))) & M64
    for x in range(5): Ls[x] ^= v[x]; Ls[10 + x] ^= v[x]
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
    # Worst case (proof.md Section 4.2), la, lb <= LRC, d = la - lb, nc = floor((la - 1) / G) + 1 checkpoints, X = the success exit
    #   (two message builds e_outm with their calls and moves, 8 stores, the halt: X = 2 e_outm + 13):
    #   (the alignment counts include the test d < 0)
    #   d >= 0: 15 + (la - 1)(e + 10) + (e + 6) + 3 nc + (16 + 6 K + r (e + 7)) + 2 + 14 ns + 8 + (b evaluations <= lb - 1)(e + 6)
    #           + (k - 1)(2e + 13) + (2e + 9) + X, with K + ns <= nc - 1, r < G, k <= G
    #           <= (2e + 16) LRC + (3e + 20)(G - 1) + 17 nck + e + 26 + X
    #   d < 0:  15 + la (e + 10) - 4 + 3 nc + 8 + (lb - la)(e + 7) + 2 + (la - 1)(e + 7) + 14 (nc - 1) + 8 + (G - 1)(2e + 13) + 2e + 9 + X
    #           <= (2e + 17) LRC + (2e + 13)(G - 1) + 17 nck + e + 17 + X
    #   (the exhausted lock step, m (2e + 13) + 3, and every refusal cost less)
    #   so replay <= (2e + 17) LRC + (3e + 20) G + 17 nck + e + 26 + X, nck = floor((LRC - 1) / G) + 1.
    assert c['match_entry'] == 15
    c['exit_found'] = 2 * c['e_outm'] + 13
    c['replay_const'] = c['match_entry'] + 11 + c['exit_found'] + e
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
other code: 1953 instructions x 8 bytes + 11 literals x 32 bytes = 15976 bytes (other.bin sha256 63a8c35c37070ff697bc7ac864c18b68648a3f74a0fb149a2aea61de796d753b)
prefilter: 15 instructions, two-address encoding, 49 bytes (pf.bin sha256 17505f8bc5711b8e2d7b413737a35a2fdd5dda5ad9070f89cbb9a4b4a5d41374); the straight-line block = prog.bin (97242 instructions, 331218 bytes) then pf.bin, 97257 instructions, sits in front of instruction 26 (label loop)
data image: 16 words x 32 bytes = 512 bytes (data.bin sha256 35551aae06a46cee1ba101f615e7b0170564c77e84ad9feeb490eb38c1fdbb66): KW[0..6], PD, 8 output words
memory map (words): TAB 0..19607, WK (walk words, LST | LID << 128) 19608..19863, data 19864..19879
replay checkpoint gap G = ceil(LRC / (S - 1)) = 1978057332278404576875178995690, at most 19607 checkpoints
routine entry points (instruction index): start 0, loop 26, hit 28, dpl 158, dp1 160, gather 204, record 402, probe 415, insert 439, ins 447, match0 450, cont 465, dl 468, restart 469, setwalk 481, evalF 1764, outm 1805, match 1843, meas 1855, measd 1868, bl 1892, walk0 1903, seg 1905, last 1925, lloop 1926, found 1939, end 1953
n_instr            1953
setwalk            1283
restart            1294
restart_halt       3
hit                131
ctz_clear          44
gather             198
record_slot        13
probe_word         24
insert             8
dp_fixed           268
dp_max             470860
dl_final           1
e_eval             4647
e_outm             38
match_entry        15
meas_iter          4657
meas_last          4653
ckpt               3
adv_iter           4654
bwalk_iter         4653
seg_iter           14
replay_iter        9307
replay_gap         1978057332278404576875178995690
replay_rate        9311
replay_g           13961
replay_nck         17
exit_found         89
replay_const       4762
replay_max         361143299189708658680986663841064528091
setup              357209
other_bytes        15976
other_literals     11
prog_bytes         331218
pf_bytes           49
sl_bytes           331267
static opcode mix: OR 424 ANDI 331 SHRI 286 AND 271 SHL 258 SHLI 68 SHR 50 ADDI 26 MOV 25 MOVI 22 EQI 22 ST 20 BNZ 19 XOR 18 BZ 17 LDA 15 JMP 13 NOT 12 JAL 10 SUB 7 LTI 6 LD 6 EQ 5 HALT 5 SUBI 5 ADD 4 JR 3 LT 3 RND 1 PERM 1
highest register named: 2033 (file of 2035)
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


def pred_replay(ta, tb, Ft, e, G, X):
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
        if Ft(p) == Ft(q): return ops + (k - 1) * (2 * e + 13) + 2 * e + 9 + X, 1, (p, q)
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
    A, vm0, nsl = mk(Pm); I = A.lab; c = counts(A, Pm); e = c['e_eval']; END = I['end']; S = Pm['S']; G = gap(Pm)
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
            pops, phalt, ppair = pred_replay(ta, tb, Ft, e, G, c['exit_found'])
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
            pops, phalt, _ = pred_replay(tx, ty, Ft, e, G, c['exit_found'])
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
            e = c['e_eval']; G = gap(Pm); maskW = (1 << W) - 1; THRm = thr(Pm)
            FtW = lambda u: F_plain(u, KL, PD) & maskW
            def trail(u, n):
                pts = [u]
                for _ in range(n): pts.append(FtW(pts[-1]))
                return pts
            ta = trail((vm.R[RHO] + vm.R[X]) & M256, la); tb = trail((vm.R[RHO] + vm.R[Y]) & M256, lb)
            if 1 <= la and lb <= Pm['LRC'] and ta[-1] < THRm and all(x >= THRm for x in ta[1:-1]):
                pops, phalt, _ = pred_replay(ta, tb, FtW, e, G, c['exit_found'])
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
replay tests (G 1): found 51 (d >= 0: 27, d < 0: 24), p=q 36, different ends 9
replay tests (G 8): found 34 (d >= 0: 22, d < 0: 12), p=q 36, different ends 6
replay tests (G 23): found 35 (d >= 0: 19, d < 0: 16), p=q 33, different ends 5
routine tests done, failures so far: 0
base       seed   1 halt  1 steps   137 hits   137 dp   98 restarts   97 tb    0 replay_ops  917920  total 21713034
base       seed   2 halt  1 steps   125 hits   125 dp   82 restarts   81 tb    0 replay_ops  656954  total 19113764
w32cap     seed   1 halt 13 steps   872 hits   858 dp  143 restarts  142 tb    0 replay_ops 1864411  total 97471234
w32cap     seed   2 halt 13 steps   559 hits   555 dp   90 restarts   89 tb    0 replay_ops       7  total 61258939
smalltab   seed   1 halt  1 steps   137 hits   137 dp   98 restarts   97 tb    0 replay_ops  945484  total 15684223
smalltab   seed   2 halt  1 steps   125 hits   125 dp   82 restarts   81 tb    0 replay_ops  694038  total 14092873
abort      seed   1 halt 10 steps     4 hits     4 dp    1 restarts    1 tb    0 replay_ops       0  total 796985
abort      seed   2 halt 10 steps     4 hits     4 dp    4 restarts    4 tb    0 replay_ops       0  total 1017644
tb5        seed   1 halt 12 steps     5 hits     5 dp    2 restarts    2 tb    1 replay_ops       0  total 967826
tb5        seed   2 halt 12 steps     5 hits     5 dp    5 restarts    5 tb    1 replay_ops       0  total 1188483
u264       seed   1 halt 11 steps    18 hits    18 dp    9 restarts    8 tb    0 replay_ops       0  total 2151145
u264       seed   2 halt 11 steps    12 hits    12 dp    9 restarts    8 tb    0 replay_ops       0  total 1567539
packed     seed   1 halt  1 steps   137 hits   137 dp   99 restarts   98 tb    0 replay_ops  945442  total 15375272
packed     seed   2 halt  1 steps   125 hits   125 dp   90 restarts   89 tb    0 replay_ops  694024  total 13891431
nocmp      seed   1 halt  1 steps   141 hits   141 dp  140 restarts  139 tb    0 replay_ops  945727  total 25218650
nocmp      seed   2 halt  1 steps   112 hits   112 dp  108 restarts  107 tb    0 replay_ops  549869  total 19653991
checks run: 971, failures: 0
```

### D.5 scan.c (the parameter scan P) and its table scan_tab.h

Compiled with `gcc -O2 -static -nostdlib -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns -fno-stack-protector -fno-pie -no-pie -DREGS=2035 scan.c -lgcc`; run as `scan ledger.txt counts.txt params.json scan_counts.txt st`, alternating with `other4.py build` until params.json and counts.txt no longer change. Output of the last run: `scan (st): HF 111 DT 754 J 61190 S 19608 Tb/2^91 535386056; float evaluations 159726 bins 1880291996, exact evaluations 21 bins 1284990`.

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

### D.6 other.c (the assembly O)

Compiled with the flags of D.5 and `-DRB0=2024`; run as `other params.json other.bin st`: other code: 1953 instructions x 8 bytes + 11 literals x 32 bytes = 15976 bytes other.c reproduces other.bin.

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

static const int ROT2[5]={3,10,43,25,39};   /* ROT[x][2] */
static void build_state(u64 MISC){   /* design X (other4.py build_state) */
  for(int i=0;i<7;i++) lda(W0+i,MISC+i);
  U M64=u_mask(64);
  xor_(W0,W0,UU);
  shli(TQ,UU,128); xor_(W0+2,W0+2,TQ);
  shri(TQ,UU,128); xor_(W0+3,W0+3,TQ);
  for(int x=0;x<4;x++){ int d=((ROT2[4]-ROT2[x])%64+64)%64;
    if(x==0) andiU(X0,UU,M64); else if(x<3){ shri(X0,UU,64*x); andiU(X0,X0,M64); } else shri(X0,UU,192);
    shli(X1,X0,64); or_(X0,X0,X1);
    if(x==0) shri(X2,X0,d); else { shri(X0,X0,d); xor_(X2,X2,X0); } }
  andiU(X2,X2,M64);
  xor_(W0+1,W0+1,X2);
  shli(TQ,X2,128); xor_(W0+3,W0+3,TQ);
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
