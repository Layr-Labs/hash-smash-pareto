# SHA3-256 with 12 prefix rounds: distinguished-point collision search with a linear-structure message embedding, a 66,105-operation bit-sliced step and an index-file table of five key slots per word, time_log2 124.34897

## 1. Claim

Target `sha3-256-r12-prefix-v1`: SHA3-256 (FIPS 202) with Keccak-f rounds 0 to 11 in the single permutation call, zero initial state, rate 136 bytes, suffix 0x06 with pad10*1, and the full 256-bit digest. The algorithm outputs two distinct 128-byte one-block messages with equal complete digests (an ordinary collision).

| Quantity | Value |
|---|---|
| time_log2 (collision-frontier-v5, unit 3252 word operations, rounded up) | 124.34897 (Sections 4 and 5, certificate in Appendix A) |
| memory | at most 1,047,967 bytes <= 2^20 (margin 609 bytes), memory_log2_bytes = 20 (Section 6) |
| score S = time_log2 + max(0, memory_log2 - 20) | 124.34897 |
| success probability | at least 0.39 for one attempt, under the premise H_rand (Section 5) |
| preprocessing | the generator run `gen3 512 1000 4`, the constant basis, the parameter scan and the assembly of the other code (Section 3.7), charged 221,768,377,805,824 word operations inside N; preprocessing_log2 = 36; no advice |

The method is a distinguished-point parallel collision search (van Oorschot-Wiener) on a chain function F, with 256 walks per step. It has three parts.

1. **Embedding.** The 256-bit point is placed in six message lanes so that round 0 of the permutation and the theta step of round 1 are affine in the point (a one-round linear structure in the sense of Guo, Liu and Song, 2016). With constants folded, those steps cost a few thousand word operations instead of one round each.
2. **Step program.** One step of the 256 walks is a bit-sliced straight line of 66,105 register operations. It follows the step design of jungjipdo's entry 67f781f8 (theta evaluated lazily per chi row, per-row complement subsets, dead-code elimination, last-use register allocation, the digest written over the input, a declared register file and its 39-bit instruction format) and adds four things of ours (Section 3): a 10-gate chi row, a polarity plan for the NOTs, structured constants for round 0 (Section 2), and a generator that writes the program round by round as it builds it, so that its own memory stays far below 2^20.
3. **Search.** The search is the one of our entries c7ff4942 (SHA3R12C, sha3-256 Pareto round 12) and ac0b6304 (S304R12, round 12, 124.36065): lockstep walks with a restart on each distinguished point, a replay of the colliding pair, and the success bound of Section 5. The search keeps from ac0b6304: a distinguished-point probability theta that is not a power of two (Section 4), no trail cut with the replay refusing trails of more than LRC evaluations (failure term F6, Section 5) and the replay. This package changes two things of ac0b6304, which already draws its message constants from the structured set S3-04 (Section 2): the polarity plan of each round looks one round ahead (Section 3.3), and the straight line is stored packed at 39 bits per instruction instead of 5 bytes (Section 3.6), which frees 8,265 bytes for a larger table (18,072 words). The straight line drops from 66,457 to 66,105 operations. The table layout is new (Section 4): the slot of a trail is fixed by its trail number, so the number is not stored and a slot holds only a written bit and 50 end bits (51 bits, five slots per 256-bit word instead of four 64-bit records); every distinguished point compares its record with all slots, and 18,072 words hold U = 90,360 trails (the index layout of Hong, Lee and Ma, eprint 2011/387, Section 2; Trimoska, Ionica and Dequen, eprint 2017/581). The failure term F6 is bounded at the first coincidence of images instead of by a union over all pairs (Section 5). The DP handler reads only the 50 key planes of a DP walk's point, since the record holds nothing else (Section 4), which shortens the other code to 1,884 instructions.

claim.json declares three heuristics. H_rand (Section 5) is the one score-critical premise. H_reg (register file) and H_code (code-memory encoding) are machine conventions of the cost model with role supporting (Section 3.6).

## 2. The function F and the encoding

Let u be a 256-bit point with little-endian 64-bit lanes u0, u1, u2, u3. The message m(u) has 128 bytes, the 16 lanes 0 to 15 of the absorbed state (lane index x + 5y):

- lane 1 = u0, lane 6 = u1, lane 11 = u0 xor u1 xor K11 (column x = 1, rows y = 0, 1, 2);
- lane 4 = u2, lane 9 = u3, lane 14 = u2 xor u3 xor K14 (column x = 4, rows y = 0, 1, 2);
- every other lane l in 0..15 holds the constant K_l (below).

With the SHA3 padding, byte 128 is 0x06 and byte 135 is 0x80: one absorbed block, lane 16 = 0x8000000000000006, lanes 17 to 24 zero. Rounds 0 to 11 are applied and the digest is lanes 0 to 3 of the result (32 bytes). Define

    F(u) = SHA3-256-r12(m(u)) xor PD

where PD is a fixed 256-bit mask (the polarity of the program's digest planes, Section 3.4). The map u -> m(u) is injective (lanes 1, 6, 4, 9 are u), so F(a) = F(b) with a != b gives two distinct messages m(a), m(b) with equal complete digests. XOR with a fixed mask is a bijection of the range, so F is a fixed function from 256 bits to 256 bits like the plain digest map.

Constants (hexadecimal). The generator chose them as trial 1214, one of 512 constant sets drawn from the structured set S3-04 below; the selection run is charged in N as preprocessing (Section 3.7):

```
K0  0000000000000000  K2  b8191f77d89d59d3  K3  0000000000000000  K5  ffffffffffffffff
K7  0000000000000000  K8  0000000000000000  K10 ffffffffffffffff  K11 6e0647ddf6275672
K12 0000000000000000  K13 770323eefb13ab3a  K14 23f3704413b15316  K15 ffffffffffffffff
PD (lanes 0..3) efd1cb26d276e587 040c7c982821f8f3 102e34d9ad891a72 1022004185880200
```

**Why round 0 is affine.**
- *Theta of round 0.* The column sums of columns 1 and 4 are constants: u0 xor u1 xor (u0 xor u1 xor K11) xor lane 16 xor lane 21 = K11 xor 0x8000000000000006, and u2 xor u3 xor (u2 xor u3 xor K14) xor lane 19 xor lane 24 = K14. So theta adds only constants to every lane.
- *Chi of round 0.* After rho and pi, the six message lanes land in positions where no two are adjacent inside a chi row. Each product of chi has at least one constant factor, so chi of round 0 is affine in u.
- *Round 1 theta.* It is a linear map of affine values, so it is affine too.

**Structured constants (set S3-04).** In a chi row, a variable lane at position x also makes out[x-1] = B[x-1] xor (not B[x] and B[x+1]) and out[x-2] = B[x-2] xor (not B[x-1] and B[x]) variable, unless its right neighbour B[x+1] is the zero lane (then out[x-1] is constant) and its left neighbour B[x-1] is the all-ones lane (then out[x-2] is constant). The six variable lanes give 12 neighbour lanes, 768 bit conditions. After theta, rho and pi each neighbour lane is a GF(2)-affine function of the 12 constant lanes K0, K2, K3, K5, K7, K8, K10, K12, K13, K15, K11, K14 (768 bits) and the fixed padding, so the conditions are a linear system. 704 of the 768 conditions are consistent; the other 64 (the all-ones left neighbour of the variable lane at x = 2, y = 3) conflict with them and are not needed, since the output they protect, out[0] of row y = 3, is itself a variable lane. The solutions of the 704 form an affine space of dimension 64 over GF(2), written KB0 xor (sum of KBV[j] over the set bits j of a 64-bit word r) in kbasis.h (Appendix B). Trial t takes r from the xorshift generator seeded with t. The constants above satisfy all 704 conditions (checked by recomputing theta, rho and pi of round 0 from them). Round-0 chi then leaves exactly the six variable lanes variable (384 variable bits), round-1 theta mixes fewer variable lanes, and the straight line gets shorter. The set changes the constants only; the embedding, F and the argument of this section are unchanged.

The generator tracks each value as a GF(2) affine form in the 256 input bits as long as it is affine, emits an operation only when the form is new, and stops tracking forms at the first nonlinear operation (chi of round 1). The search uses no algebraic property: F is only evaluated.

## 3. One step of 256 walks: the straight line

### 3.1 Planes, polarity, gates

A batch is 256 walks. Plane (lane, z) is one 256-bit word whose bit t is bit z of that lane for walk t. The rotations of rho and the moves of pi rename planes and cost nothing.

Each value is held as a register and a polarity p: the logical value is the register word xor p, all-ones or zero. NOT and XOR with a constant flip p for free; constants are folded and never stored. The operations, each one word operation, are:
- XOR: one operation;
- logical a AND b: one AND when both polarities are 0, one OR with output polarity 1 when both are 1, and two operations otherwise, either A xor (A and B) (output polarity 0) or (not A) or B (output polarity 1);
- NOT: one operation, used for the row complements of 3.2 and the theta complements of 3.3.

Equal operands fold, and a binary operation on the same pair of registers is emitted once (hash-consing).

### 3.2 Rounds

For each round r = 0..11, with the round constant of the profile:

1. Column sums C[x][z] (the five planes of the column, folded) and D[x][z] = C[x-1][z] xor C[x+1][z-1], computed slice by slice with C[.][63] first, so that few C values are live at once.
2. The chi rows, in order Y = 0..4 and z = 0..63. Each row XORs D into its five inputs b[X] = A[x][y][z - rho(x,y)] xor D[x][z - rho(x,y)] (x = 3Y + X mod 5, y = X) when the row is computed (lazy theta).
3. **Row decision.** chi computes out[X] = b[X] xor ((not b[X+1]) and b[X+2]). Before it, the generator may NOT some of the five inputs (a complement subset s, one operation each), and it may compute one output j from the finished output k = j + 1 of the same row (the **10-gate row**): wherever b[k+1] = 1, out[k] = b[k] xor ((not 1) and b[k+2]) = b[k]; wherever b[k+1] = 0 both sides below are 0; so

        (not out[k]) and b[k+1] = (not b[k]) and b[k+1],

   and the term of output j may read out[k] in place of b[k]. The polarity of out[k] is set by its own term, so the odd five-cycle of equal polarities, which forces at least one two-operation term in a plain row, is broken. The generator evaluates the 32 subsets and the six choices j in (none, 0..4) and keeps the first cheapest (Appendix B, `row_choose`; for rows with five distinct variable inputs the decision depends only on the five polarities and is read from a 32-entry table made by the same function). In this program 2,871 rows use the 10-gate form.
4. iota flips the polarity of the lane-0 planes where the round constant has a 1.

**The last round** computes only row Y = 0 and the outputs X = 0..3 (the digest lanes); the 10-gate form is used there when both outputs j and j + 1 are needed.

**Dead-code elimination** removes every operation on which no state plane of the next round (no digest plane, in the last round) depends.

### 3.3 Polarity plan

With AND, OR and XOR, the polarity of every value follows from the operations that built it, so the row costs of 3.2 depend on NOTs placed earlier. Three kinds of choices move polarities at a known cost:

- a NOT on a column sum C[x][z] costs one operation and flips the polarity of the 10 chi inputs it reaches through D;
- a NOT on D[x][z] costs one operation and flips 5 chi inputs, one in each of 5 rows;
- a two-operation term has a free output polarity (A xor (A and B) or (not A) or B, two operations either way), which flips its output plane and, through the theta of the next round, 11 chi inputs there.

For each round r >= 2 the generator chooses these by simulated annealing (deterministic xorshift, 600,000,000 iterations per round) against the exact cost table of the row decision of 3.2 (the cheapest decision for each of the 32 input-polarity patterns, made by the same function the build uses), minimising the sum of the row costs plus the theta NOTs. The build is multi-pass: pass k fixes the choices of round k and the free output polarities of round k - 1, and the next pass rebuilds with them. The plan places 0 to 77 theta NOTs per round. Round 1, whose inputs are affine, is handled by a greedy pass over its 640 C and D complements, each kept when the operation count of rounds 0 and 1 drops (three sweeps; it saves 75 operations here). A free polarity that a 10-gate row needs is fixed by that row and is not offered to the plan.

**One round of lookahead (this package).** The plan above prices round r alone. In every round r >= 2 except the last, this generator (optmode 4, `polopt2` in Appendix B) anneals a larger state: the C and D NOTs of round r and, for each of the 320 chi rows of round r, the polarity vector of its five outputs. The cost is 16 x (the row costs of round r for the chosen outputs + the NOTs) + 3 x (for each row of round r + 1, the least row cost over its input-polarity pattern, which the chosen outputs fix through iota and theta, plus 5; in the last round, the exact cost of its four needed outputs). Row costs come from a table made once by the same row function: for each of the 32 input patterns and each of the 32 output vectors, the cheapest complement subset, 10-gate position and term polarities that give those outputs. A move flips a C NOT, a D NOT, or bits of one row's output vector (with probability 3/5); the run is 600,000,000 iterations per round (deterministic xorshift, temperature 19.2 x e^(-3.178 i / 600,000,000) at iteration i). The build then gives each row of round r the table's decision for its pattern and its chosen outputs. Rows of round r + 1 see the polarities this produced, and the plan of round r + 1 is made on the built state, so the lookahead changes decisions, never the function computed: the self-test, the KAT and the experiment program (which reads the decisions from plan.txt) check the program that is built.

The ledger counts the program that is built, not the plan's prediction.

### 3.4 Chain feed

Digest plane j is written into register j, which held input plane j. The physical digest word is the next point: F folds the digest polarity PD into the function (Section 2). There is no copy and no NOT between steps.

### 3.5 The ledger of one step

Printed by the generator (Appendix B):

| operation | count |
|---|---:|
| XOR | 48,112 |
| AND | 9,567 |
| OR | 6,689 |
| NOT | 1,737 |
| load / store | 0 / 0 |
| **total** | **66,105** |

That is 258.22 word operations per evaluation of F, 0.0794 of the reference cost 3252 per evaluation.

### 3.6 Registers and code encoding (machine conventions H_reg and H_code)

**Registers.** Values are allocated to registers in program order, and a register is freed at the last use of its value. Input and digest plane j use register j; the allocator never gives register j < 256 to another value. The program uses registers 0 to 2,180 (2,181 registers, at most 1,925 values live at once). The search keeps its state in registers 2,181 to 2,190 (the step counter, a spare word, the next trail number, rho, the hit counter, the all-ones word, the prefilter word, two return addresses, a zero word); register 2,191 is spare. The handlers of Section 4.3 use registers 256 to 2,180 as temporaries: their contents are dead between two steps, because every straight-line value is defined before it is used and only the planes 0 to 255 are carried from one step to the next. The step has no loads or stores.

**H_reg (declared machine convention, role supporting in claim.json).** The cost model and the target profile fix no register count. This package uses the 256-bit word RAM of collision-frontier-v5 with a declared file of 2,192 registers of 256 bits. An operation on register operands costs one word operation, with no load or store. Every load and store of the other code is a charged word operation (Section 4). The file's 70,144 bytes are counted as memory (Section 6). This is the convention of 67f781f8 (a declared file of 2,304 registers), credited in Section 8.

**H_code (declared code-memory charging convention, role supporting in claim.json).** The cost model and the target profile fix no code encoding.
- **Encoding.** Each straight-line instruction has only register operands. It is 39 bits: a 3-bit opcode (0 XOR, 1 AND, 2 OR, 3 NOT) and three 12-bit register numbers (destination, a, b), in little-endian order. The instructions are packed with no padding: instruction i is bits 39 i to 39 i + 38 of the block (bit k of the block is bit k mod 8 of byte k div 8). The memory table charges the straight line at 39 bits per instruction, rounded up to whole bytes once for the block.
- **Other code.** All other code (setup, loop control, hit handler, DP handler, restart, replay, output) is real code of one machine, written out in Appendix D and assembled: 1,884 instructions of 32 bytes (60,288 bytes), measured from the assembled file. An instruction has an opcode byte, three 16-bit register numbers and a 192-bit immediate. Each costs one word operation, except PERM, which applies the 12-round permutation to the 1,600-bit state held in seven registers and costs one unit (3252 operations), the cost model's own price of one permutation. The other instructions are the model's primitives: register-register and register-immediate XOR, AND, NOT, addition, subtraction, shifts, a compare that writes 0 or 1, a conditional branch on that register (always right after its compare, checked by the assembler), jumps, load and store with address register plus immediate, and the random word.
- **Time ledger.** Each instruction is charged as the one word operation it performs; there is no separate charge for fetching or decoding.

The program file is 322,262 bytes. Its SHA-256 is 09507bcd9ac37099eba6b6f925005c18ce7e5c6c653017c8515df5c82ca07d1f.

### 3.7 Generation and constant selection (preprocessing)

**The generator writes the program as it builds it.** gen3.c (Appendix B) is a freestanding C program without libc, with static arrays only. Its nodes live in a ring of 8,192 slots that holds one round (rounds 0 and 1 share it; this build needs at most 6,852 slots and 1,088 of the 1,920 affine-form slots). When a round is built, the generator removes its dead nodes (liveness from the state planes, or from the digest planes in the last round), gives every value its last use (every use of a value lies in its own round or, for a state plane, in the next round), allocates registers in node order and writes the round's instructions to prog.bin at once. It then keeps only the 1,600 state planes (register and flags) and reuses the ring for the next round. The program is never held in the generator's memory. With the 10-gate rows and the plan switched off, this generator writes the same instructions, instruction for instruction, as a whole-program build of the same algorithm (checked at rounds 9 and 22, with the 5-byte records of the earlier entries); with the 10-gate rows alone, and with the plan alone, it reproduces two further whole-program builds at round 8, instruction for instruction.

**The run `gen3 512 1000 4`** is the preprocessing:
1. for each of the 512 structured constant sets of trials 1000 to 1511 (Section 2: r from the xorshift generator seeded with t) it builds the straight line without the plan and counts its operations (trial 1000 gives 68,089; the lowest is 67,945);
2. the trial with the lowest count is built with the plan of 3.3 and counted: trial 1214: 66,105;
3. that trial, 1214, is built again and written out (prog.bin; the ledger goes to standard output).

The check run `gen3 1 1214 4 i` rebuilds trial 1214 alone and writes the identical prog.bin (compared byte for byte), meta.txt (constants and PD) and plan.txt (the decisions of the plan, embedded in the experiment program); like the self-test, it is a verification run, and the search uses none of its output.

- **Time.** The ledger charges every build 2^32 word operations and every annealing iteration 2^12 (a move and its undo update at most 2 x 56 rows of the cost tables, with one exponential), the plan's row tables 2^32 once: at most 4,376 builds (512 trial builds, then for each of the two plan runs the round-1 greedy builds, one pass per round and the counting or writing build) and 12,000,000,000 iterations, plus 2^10 per trial for its constants, count and comparison: G = 67,951,072,378,880. The 512-set scan of the constants is step 1 of this run and is inside G; no other generator run's output is used. PRE = G + K + P + O = 221,768,377,805,824 = 2^47.66 word operations, part of N (Section 4.4), with K, P and O below. Since 2^35 < PRE / 3252 <= 2^36, preprocessing_log2 is 36. The generator run took 2071.9 s of user time on one core of an AMD Ryzen 9 7900X (at most 5.6 GHz): at most 8 retired instructions per cycle gives below 2^46.4 machine instructions, below the charge.
- **Memory.** Measured with `size`: text 52,038 bytes, data 12 bytes, BSS 266,816 bytes, an image of 318,866 bytes. `gen3 512 1000 4` was run under `nice -n 10 prlimit --as=1048576 --stack=16384` (an address-space limit of 2^20 bytes and a 16,384-byte stack) and completed. Its peak resident memory, read by the program from /proc/self/status VmHWM, is 315,392 bytes. Section 6 charges the image, a 16,384-byte stack reserve and the whole program file, as if the program were held.

**The other preprocessing steps.** Every other step whose output the search uses is charged in PRE (pre_ops() in Appendix A). Each is deterministic, runs once, alone, before the search, and holds less than the generator bound of Section 6.

- *K, the constant basis (kbasis.h).* Gaussian elimination of the 704 conditions of Section 2 over the 768 constant bits, rows of 769 bits in four words. Each of at most 768 pivot steps tests at most 704 rows (3 operations each), swaps two rows (8) and clears the column in at most 703 rows (a bit test and four XORs, 7): at most 7,041 operations. Building the 704 equations (each at most 11 constant bits through theta, rho and pi) and reading off KB0 and KBV costs less than 2^20. K = 2^24 > 768 x 7,041 + 2^20. Memory: 704 rows of four words and the basis, 96,352 bytes.
- *P, the parameter scan (`cert4.py --scan`, which wrote params.json).* A coarse grid of 8 octaves of theta x 16 thresholds x 12 replay caps (1,536 points), then 25 thresholds x 9 caps around the best. For each point, the least Tb with model success at least 0.3902: at most 210 geometric steps and 50 bisection steps of a float model of the bound of Section 5. Then the exact least Tb with the Decimal bound of Appendix A. Counted in the run: 157,829 float evaluations over 2,005,556,545 bins and 21 exact evaluations over 1,332,618 bins. Charges: a double-precision operation costs at most 2^9 word operations (53-step shift-and-add multiplication or restoring division, with unpacking, normalisation and rounding). exp, expm1, log and log1p cost at most 2^14 each (range reduction and at most 30 such operations). A float bin (three of these functions and 12 operations) is charged 2^16, and the fixed part of a float evaluation (four functions and 20 operations) 2^17. An 80-digit Decimal is an integer below 2^340 (two words) with an exponent. A multiplication or division costs at most 2^13, exp at most 2^9 of these (2^22), and ln at most four exps. An exact bin (two exps and 10 operations) is charged 2^24, and the fixed part of an exact evaluation (two lns, two exps, two integer powers and 30 operations, below 2^25) 2^27. The grid records and their sort are charged 2^20. P = 153,817,280,348,160 = 2^47.13. The scan took 231.67 s of user time on the same machine, below 2^43.2 machine instructions, far below P. Memory: the bins in chunks of 4,096 (at most ten arrays of 4,096 doubles, 327,680 bytes), the 1,536 grid records of five numbers (61,440 bytes) and scalars: below 2^19 bytes.
- *O, the assembly (`other4.py build`, Appendix D).* It emits the 1,884 instructions, resolves the jump targets, checks every branch, encodes each instruction in 32 bytes, and writes other.bin, the 74-byte prefilter pf.bin and the 16-word data image. It hashes the three files with SHA-256 (954 blocks) for counts.txt. Charged 2^8 per instruction, 2^13 per SHA-256 block (64 rounds of at most 48 operations and the schedule) and 2^12 for the data image: O = 8,301,568. Memory: the instruction list and other.bin at 32 bytes per instruction, the jump fixups at 8 bytes, and the files read and written (below 2^13 bytes): below 2^18 bytes.

### 3.8 Correctness of the step (checked by execution)

- `selftest` (our C program, Appendix B) executes the program file, decoded from its packed 39-bit encoding, on 4 x 256 uniform points for four chained steps each, and compares every output with F computed by a plain lane-wise 12-round implementation: 4,096 chained evaluations, run twice with different seeds, 0 mismatches.
- That reference matches hashlib.sha3_256 at 24 rounds on 300 messages of lengths 0 to 299, and the organizer's verifier/keccak.py sha3_256(m, rounds=12) on the same messages: 0 mismatches.
- The experiment program regenerates the same straight line in Python from the generator's decisions (plan.txt, embedded) and refuses to run unless its encoding hashes to the SHA-256 above. Before its trials it checks two chained full-width steps against the plain implementation.

## 4. The search

Parameters:
- L = 256 walks.
- Distinguished point (DP): the 256-bit image x of F (bit j = plane j) is a DP when x < THR = 694 x 2^135: the planes 145 to 255 are zero and the 10 planes 144 down to 135, read as a number, are less than 694. The probability of a DP for a uniform image is theta = 694 x 2^-121 (H = -log2 theta = 111.5612); it is a rational number, exactly this, and is not a power of two.
- Replay cap LRC = 63,458 x 2^99 = 40,221,285,894,641,490,680,088,896,003,375,104 steps = 10.50 / theta. No trail is cut; the replay refuses a trail of more than LRC evaluations.
- U = 90,360: the limit on trails started in one attempt.
- S = 18,072 table words, five slots each (90,360 slots, one per trail: U = 5 S); 2^15 = 32,768 > S.
- Tb = 1326064821300054183508427017256173568 = 535593316 x 2^91 = 0.99762029 x 2^120 steps of 256 walks per attempt.
- HMAX = floor(Tb (1 + 2^-20) / 2^8) + 1 + LRC = 45401231542821241255142274482831361: the cap on prefilter hits; the attempt aborts at hit HMAX + 1.

State:
- in registers: the 256 input planes (registers 0 to 255); the step counter c, the next trail number idn, rho, the hit counter h, the all-ones word, the prefilter word and the return addresses (registers 2,181 to 2,190);
- in memory (word addressed): the table TAB of S words; LID[l] and LST[l] for each walk l (its trail number, and the number of the first step of its trail); a data image of 16 words: the 7 words of lane constants of the absorbed state (K, with the lanes of u zero), PD, and 8 words for the output pair.

A table word holds five slots of 51 bits (slot k = bits 51 k to 51 k + 50, k = 0 to 4; bit 255 is unused). Trail i (i = 0, 1, ..., U - 1, in the order the trails start) has the trail number t(i) = (i mod S) + 51 floor(i / S) x 2^15 and owns slot floor(i / S) of word i mod S: the low 15 bits of t(i) are the word, the bits above them the slot's bit offset. The numbers t(i) are distinct, so the starts rho + t(i) are distinct points, and t(l) = l for l < 256 <= S. A written slot is

    1 | (bits 0 to 49 of the trail's end) << 1,

never zero; an unwritten slot is zero. Neither the trail number nor the trail's length is stored: the slot's place gives the number, and the replay measures the length.

```
setup: rho := random word; idn := 256; h := 0; c := 0; TAB := 0; for l < 256: LID[l] := l; LST[l] := 0; lane l of the input planes := rho + l
loop:
  the straight line (66,105): the input planes become F of the 256 walks
  pf := OR of the 16 planes 240..255 (15 ORs)
  if pf != all-ones (compare, branch):          -- some walk has planes 240..255 zero (probability 2^-16 each)
      h += 1; if h > HMAX: halt, the attempt failed   -- hit counter and abort (F5)
      dp := complement of (pf OR (OR of the planes 145..239))      -- the walks with the top 111 planes zero; c1 := c + 1 = steps completed including this one
      dp := dp AND (the walks whose planes 144..135, read as a number, are < 694)      -- bit-parallel comparison with the constant 694: the walks at a DP
      while dp != 0: l := the lowest set bit of dp; clear it;
          key := the 50-bit value with bit j = bit l of plane j, j = 0..49 (only the key planes are read)
          record := 1 | key << 1;  rep := the record in each of the five slots
          for each word w = 0 .. S - 1: load it and XOR rep; for its slots k = 0 .. 4 in order (shift, mask) test for zero:
             zero: slot k of word w equals the record (an unwritten slot never does): REPLAY(w + 51 k 2^15, walk l, c1);
                if it returns a != b, output m(a), m(b) and stop; otherwise halt, the attempt failed
          no slot equals the record: t := LID[l]; word (t mod 2^15) := word OR (record << (t >> 15)); restart(l, c1); next DP walk
  c += 1; if c != Tb goto loop
  halt, the attempt failed                           -- c = Tb
restart(l, s): if idn = t(U): halt, the attempt failed
               LID[l] := idn; LST[l] := s; lane l of the input planes := rho + idn; idn += 1;
               if idn mod 2^15 = S: idn += 51 x 2^15 - S      -- so idn = t(i) for the i-th trail
REPLAY(trail a, walk l of trail b, c1):
  b := LID[l]; lb := c1 - LST[l]                       -- the new trail's length is known; if lb > LRC: return nothing
  la := the number of evaluations from rho + a to the first DP (stop with failure if LRC are passed)
  p := rho + a, q := rho + b; the longer trail is advanced by |la - lb| evaluations of F
  if p = q return nothing; repeat min(la, lb) times: if F(p) = F(q) return (p, q); p := F(p); q := F(q)
  return nothing
```

No trail is cut: a walk runs until its DP, however long that takes, and only the replay refuses a trail of more than LRC evaluations (the entry test lb <= LRC, and the measuring walk of trail a stops with failure after LRC evaluations without a DP). A trail restarted inside step c (at a DP) starts at step c + 1, hence LST[l] := c1. A trail is recorded at its first DP, so walking it from its start to its first DP gives its length; the walk of the replay stops at that DP. The DP test of the replay is x < THR on the image, the test of the loop above.

### 4.1 One iteration of the loop

An iteration costs the straight line (66,105), the prefilter (15), its test (2) and the counter (3: add, compare, branch): **BSTEP = 66,125 operations**, the instructions at the labels `loop` and `cont` of Appendix D around the straight-line block. No other operation runs in an iteration without a prefilter hit.

### 4.2 The replay

The replay evaluates F on one point at a time with the permutation, one unit (3252 operations) per call. The routine `evalF` (Appendix D) loads the 7 words of lane constants, places the four 64-bit limbs of the point in the lanes 1, 6, 4, 9 and, XORed in pairs, 11 and 14, calls PERM, loads PD and XORs it into the first state word: one evaluation with its return costs **e = 3281** operations.

Counted from the emitted code:
- taking the trail number from the place of the matching slot costs 3 (move, or, jump) and the entry (trail b, lb, the test lb <= LRC 2, the two starts) 9;
- a measuring evaluation of trail a costs e + 8 (call, add, the DP test of the image x < THR 2, the cap test 2, move, jump), e + 4 for the one that lands on the DP;
- an advance step costs e + 7, a lock-step iteration 2e + 13, the success exit 67 (two message builds of 27 with their calls and moves, 8 stores, the halt).

With la, lb <= LRC, the replay costs at most 12 + (e + 8) LRC - 4 + (2e + 13) LRC + 71, that is **(3289 + 6575) LRC + 79** (largest for la = lb = LRC with the pair found at the last iteration; an advance step is cheaper than a lock-step iteration, so |la - lb| + min(la, lb) <= LRC iterations of at most 2e + 13 bound the rest). At most one replay runs per attempt: the attempt stops after it, with the pair or with failure.

### 4.3 Rare operations

Every routine is real code of the machine of Section 3.6 (Appendix D). The counts, each for the longest path, are read from the emitted code (`other4.py build`, D.2):

| routine | operations |
|---|---:|
| a prefilter hit with no DP walk (counter 3; OR of the planes 145..239; combine and complement 2; the comparison of the planes 144..135 with 694, at most 4 per plane, and a move; c1; test of the DP mask 2) | **131** |
| one DP walk without a match, without its restart: DP-mask test 2, lowest set bit and clearing 44, gather of the point 198, the record, its five copies and the word index 12, the insertion into the trail's slot 7, move, call and jump back 3; and 24 for each of the S words (load, XOR, five slot tests of 3 or 4, next word 3) | 266 + 24 S |
| restart(l, s) with its return: cap check 2, two stores, add and increment 4, the wrap test 3 and its add 1 (charged on every restart), the insertion of the new point into lane l and the return | **1,293** (the call that halts at idn = t(U): 3) |
| the event c = Tb: the HALT after the iteration's counter, compare and branch | 1 |
| setup: clearing TAB (eight words per pass), the 256 starts | **355,097** |

The numbers of events. At most HMAX + 1 prefilter hits are processed in every execution, and the ledger charges that number. The counter idn runs through t(256), t(257), ..., t(U), one value per completed restart, so at most U - 256 restarts complete; each DP walk except the last is followed by a completed restart, so at most U - 255 DP walks are processed (the last stores its record and halts at idn = t(U), or starts the replay of 4.2). A DP walk without a match passes all S words, so it costs exactly 266 + 24 S; a match ends the scan earlier and starts the replay. The event c = Tb happens once.

R = (HMAX + 1) x 131 + (U - 255) x (266 + 24 S) + (U - 256) x (1,293 + 3) + 3 + 1 + 355,097 = 5,947,561,332,109,582,604,423,637,996,473,067,677.

### 4.4 Total

N = Tb x 66,125 + replay + R + PRE = **88,088,726,633,862,936,131,167,557,246,006,620,083,436** word operations (Appendix A).

| part | operations | share |
|---|---:|---:|
| main loop, Tb x 66,125 | 87,686,036,308,466,082,884,494,736,516,064,477,184,000 | 0.99543 |
| replay, (3289 + 6575) LRC + 79 | 396,742,764,064,743,664,068,396,870,177,292,025,935 | 0.00450 |
| rare operations R and preprocessing PRE | 5,947,561,332,109,582,604,423,637,996,473,067,677 + 221,768,377,805,824 | 6.75e-05 |

time_log2 = log2(N / 3252) rounded up at the fifth decimal = **124.34897**, checked in exact integer arithmetic:

    3252^100000 * 2^12434896 < N^100000 <= 3252^100000 * 2^12434897

## 5. Success probability and the premise H_rand

**Premise H_rand (our theory): over the algorithm's coins, the program run on the fixed SHA3-256-r12 target succeeds with probability at least the probability computed below for a uniformly random function F.** The target is fixed: F of Section 2, with its fixed constants K and PD, is one deterministic function, and the only randomness of the algorithm is the random word rho. That transfer is the premise, and it is the one score-critical premise of this package. In claim.json it has four fields: the statement above; role score-critical; scope, the fixed function F of Section 2 on the points of one attempt; limitations, our theory with no proof. Everything else in this section is computed in the random-function model M: F is a uniformly random function from 256 bits to 256 bits (values at distinct inputs independent and uniform) and rho is uniform and independent of F. In M:

- (i) the first coincidence of images among e evaluations has probability 1 - prod_(k<e)(1 - k/n) >= 1 - exp(-e(e-1)/(2n)) =: G(e), where n = 2^256;
- (ii) the point reached just after a coincidence is uniform, so the number l of further evaluations of a trail until its DP satisfies P(l >= j) = (1 - theta)^j, independently of when the coincidence happened;
- (iii) F is realised by lazy sampling: a fresh evaluation draws a new independent uniform value, so given the whole history of the run it equals one given earlier output with probability 2^-256, whatever inputs the adaptive program chose. This is a property of M, not a claim about the fixed target, for which the run given rho is deterministic.

The first coincidence is a stopping time over all evaluations in their execution order (step by step, walk by walk). Under (i) and (iii), when k earlier images are distinct the next fresh evaluation coincides with an earlier image with conditional probability exactly k/n, so G(e) of (i) is the probability that the first e fresh evaluations contain a coincidence; no fixed-size birthday product over a random set and no conditioning on which trails finish is used.

**The coincidence.** Let e* be the first evaluation whose image equals an earlier image, at step b* = ceil(e*/256). The trail B of that evaluation and the earlier trail A have equal points from then on and both end at the same DP after l further evaluations of B. B is recorded at step b* + l at the latest; A reached the same point no later, so A was recorded before, or in the same step in a lower walk, and the later record finds the earlier one.

The search succeeds if all of these hold: (a) b* + l <= Tb; (b) both trails have at most LRC evaluations; (c) fewer than U trails are started; (d) the coincidence is between two different trails; (e) no record of a different end has the same 50 stored end bits, and the replay finds the merge.

Split l into bins of w = 2^(111 - 12) steps: bin j holds l in [(j - 1) w, j w - 1], j = 1 .. J = 63,458, J w = LRC, with probability p_j = (1 - theta)^((j-1) w) - (1 - theta)^(j w). If l is in bin j, (a) holds when e* <= 256 (Tb - j w). By (ii),

    Pr[(a)] >= sum_j p_j G(256 (Tb - j w)).

The failure events the sum does not cover:

- **F6**, the colliding pair has a trail of more than LRC evaluations. No trail is cut; the replay refuses such a pair, and this term bounds the probability that the pair of the first coincidence is such a pair. Write q = 1 - theta and E = 256 Tb, the number of evaluations of an attempt at most. The age of an evaluation is its place in its trail: the number of evaluations of the trail up to and including it. Until the first coincidence every input is fresh and the DP indicators xi of the evaluations are independent Bernoulli(theta) (as in F2); an evaluation of age at least a has the a - 1 earlier evaluations of its walk all non-DP, so P(age >= a) <= q^(a - 1) for every evaluation. Take evaluations s < t. By (iii), given the history before t, t has the image of s with probability 1/n, and the ages a_s and a_t, which depend only on evaluations before s and before t, are then fixed. By (ii) the number l of further evaluations to the DP has P(l >= j) = q^j independently of the history, and la = a_s + l, lb = a_t + l. The replay needs la <= LRC and lb <= LRC, so it fails when l >= LRC + 1 - max(a_s, a_t), with probability g(max(a_s, a_t)) <= g(a_s) + g(a_t), where g(a) = min(1, q^(LRC + 1 - a)). The function g does not decrease, g(1) = q^LRC, and g(a) - g(a - 1) = q^(LRC + 1 - a) (1 - q) for 2 <= a <= LRC + 1, g(a) = 1 beyond. By summation by parts, for any evaluation u, E[g(age_u)] = g(1) + sum over a >= 2 of (g(a) - g(a - 1)) P(age_u >= a) <= q^LRC + LRC (1 - q) q^LRC = q^LRC (1 + LRC theta). Call this G6 = q^LRC (1 + LRC theta); it holds for the ages computed from the DP indicators alone (each walk restarting after its DPs), which are the true ages before the first coincidence. Only the pair of the first coincidence matters. Write pi_m = prod_(i<m)(1 - i/n), and let t be the first coincidence: the images V_1, ..., V_(t-1) of F2's lazy sampling are distinct (event D) and V_t equals V_s for some s < t, probability 1/n for each s given the history. Given the DP indicators of the m = t - 1 evaluations before t, k of them DPs, those images are independent and uniform on the DP points and on the other points, so P(D | indicators) <= prod_(i<m-k)(1 - i/((1 - theta) n)) <= pi_(m-k) <= pi_m (1 - E/n)^-k, and k < U outside F2. The ages before t are functions of these indicators. So the first coincidence is at t and the replay refuses it with probability at most (1/n) pi_(t-1) (1 - E/n)^-U sum_(s<t) E[g(a_s) + g(a_t)] <= 2 G6 (1 - E/n)^-U (t - 1) pi_(t-1) / n. Since (t - 1) pi_(t-1) / n = pi_(t-1) - pi_t, the sum over t = 1, ..., E is 1 - pi_E, and ln(1 - x) >= -x - x^2 (0 <= x <= 1/2) gives pi_E >= exp(-E^2/(2n) - E^3/(3n^2)). So F6 = 2 G6 (1 - exp(-E^2/(2n) - E^3/(3n^2))) (1 - E/n)^-U = 2.483e-4. This covers (b) outside F2 and F4, whose terms follow.
- **F2**, more than U - 256 restarts after a DP (a fact proved here). Realise F by lazy sampling with independent uniform values V_1, ..., V_(256 Tb), one per evaluation index in execution order: the t-th evaluation returns V_t if its input is fresh and the stored value otherwise. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(theta), so N1 = xi_1 + ... + xi_(256 Tb) is binomial with mean mu = 256 Tb theta. A DP output at a fresh input is a position with xi_t = 1. A DP output at a repeated input never causes a restart: the value is the stored output of the first evaluation of that input, whose trail ended there and was recorded with another trail number, and the scan of the S words finds that record, so the attempt goes to REPLAY and stops. Hence the restarts after a DP are at most N1. The halt at idn = U needs N1 >= U - 255, and the Chernoff bound e^-mu (e mu / (U - 256))^(U - 256) >= P(N1 >= U - 256) gives 4.346e-6. This covers (c).
- **F3**, the coincidence lies inside one trail: at most U / (theta^2 n) = 1.145e-5. This covers (d).
- **F4**, 2^-90 + U^2 2^-51 = 3.626e-6. This covers (e): a start rho + t(i) equal to a point of another trail (U starts, about 2^128 images: below 2^-113); and two different ends with the same 50 stored bits: in M the ends are uniform on the bits below the 10 comparison planes, so a pair agrees with probability 2^-50, and there are fewer than U^2 / 2 pairs.
- **F5**, the hit counter aborts the attempt before it stops: below 2^-1000. Call a walk's input at a step fresh if F was not evaluated at it before in the attempt, and let X' count the steps at which some walk with a fresh input lands on planes 240..255 zero. Given the past, each step adds to X' with conditional probability at most 1 - (1 - 2^-16)^256 < 2^-8 (in M). A hit not counted in X' needs a walk at a repeated input; outside F4 these occur only after the first image coincidence, and a successful attempt outside F6 stops at step b* + l with l <= LRC. So h <= X' + LRC on success, and an abort needs X' >= floor(Tb (1 + d) 2^-8) + 2 > (1 + d) mu, with d = 2^-20 and mu = Tb 2^-8. The Chernoff bound for indicators with conditional probabilities at most 2^-8 (supermartingale exp(s X'_t - (e^s - 1) t 2^-8)) gives at most exp(-d^2 mu / (2 + d)) = exp(-2,355,563,191,584,363,937,892) < 2^-1000, checked in exact rationals in Appendix A.

With a further 2^-60 for rounding, the success probability of one attempt is at least 0.3900000002 at Tb, and 0.3899999991 at Tb - 2^91: Tb is the least multiple of 2^91 that reaches 0.39 (Appendix A, 80-digit decimals). In evaluations, 256 Tb = 0.997620 x 2^128; the birthday point for success 0.39 is 0.9943 x 2^128, and the wait for the DPs of the last trails, 256 / theta evaluations, is most of the difference.

A failed attempt can be repeated with a fresh rho at the same cost. The claim is one attempt with success 0.39, a probability over the algorithm's coin rho for the fixed target, under the premise H_rand.

## 6. Memory

The search, at its peak:

| region | bytes |
|---|---:|
| register file, 2,192 words of 32 bytes (H_reg) | 70,144 |
| straight line plus prefilter, 66,120 instructions x 39 bits, packed (H_code) | 322,335 |
| other code (Appendix D), 1,884 instructions x 32 bytes, measured | 60,288 |
| table, 18,072 words of five slots | 578,304 |
| LID and LST of the 256 walks, 512 words | 16,384 |
| data image (lane constants K of the absorbed state, PD, output pair), 16 words | 512 |
| **total** | **1,047,967** |

The preprocessing `gen3 512 1000 4` runs before the search and ends before it starts:

| `gen3 512 1000 4` | bytes |
|---|---:|
| image (text, data, BSS; all arrays static) | 318,866 |
| stack reserve (the run completes with a 16,384-byte stack limit) | 16,384 |
| the program it writes, prog.bin (written out round by round, counted here in full) | 322,262 |
| **bound used** | **657,512** |
| measured peak resident memory (VmHWM) | 315,392 |

The basis, the scan and the assembly (Section 3.7) each run alone and hold less than this bound. The claimed memory covers both phases, the preprocessing included: peak = max(search 1,047,967, preprocessing 657,512) = 1,047,967, since the two phases do not overlap; 1,047,967 <= 1,048,576 = 2^20: memory_log2_bytes = 20 and the memory term of the score is 0. The margin to 2^20 is 609 bytes (search phase 609, preprocessing 391,064).

The declared experiments and the C checks of Sections 3.8 and 7 are verification runs; they build nothing the search uses.

## 7. Evidence for the step and for H_rand

### 7.1 Organizer experiments (experiments/manifest.json, program experiments/ls1.py)

Both experiments regenerate the straight line in Python from the generator's decisions (the encoding must hash to the SHA-256 of Section 3.6), check it against the plain 12-round implementation, and execute it on Python integers, all trials side by side.

- **rho-w22** runs the search of Section 4 end to end at width 22. The planes 22 to 255 are set to zero after every step. Parameters: a DP is an image whose 4 low bits are zero and whose 3 bits above them, as a number, are less than 5 (theta = 5/128), replay cap 256, no trail cut, 3,000 trails and 400 steps per attempt; the table keeps the trail number of each end and the replay measures the stored trail by walking it to its DP and refuses trails of more than 256 evaluations, as in Section 4. Every trial returns two messages whose 12-round digests agree on the 22 low bits. At this width a start often lies on another trail, so a replay that returns nothing restarts the walk instead of ending the attempt (the full-size rule halts, as F4 accounts). An ideal-function control (F replaced by a lazily sampled random function on 22 bits, the same rules) needs 20.47 steps to the pair on average (20,000 trials, standard deviation 7.91). Our own run of 256 trials (our seeds): 256 of 256 pairs, mean 19.75 steps; 20.0 s on one core here.
- **proj-w256** runs eight chained full-width steps from 256 uniform points per trial and finds the first two distinct evaluated inputs whose images agree on the 22 low bits; a random function gives success probability 0.3934 per trial, 100.7 of 256 (standard deviation 7.8). Our own run of 256 trials: 103 of 256; four further seed sets of 256 trials gave 99, 89, 103, 93, 487 of 1,280 trials in all (model 503.6, standard deviation 17.5); 11.7 s here.

### 7.2 Measured checks of H_rand on this program (our runs, not organizer runs)

The embedding makes round 0 affine, so F has one nonlinear round fewer than the plain digest map. hrand_test.c (Appendix C) executes the program file of this package and measures the quantity the search depends on, the rate of image coincidences among evaluated points, on three 32-bit windows (bits 0-31, 128-159 and 224-255; the top window lies inside the DP bits), for uniform inputs (A), consecutive starts rho + i (B; the starts rho + t(i) of the search are five runs of S consecutive values) and chained iterates (C), and the output differences of single-bit input differences (D):

```
A uniform inputs: M=2^24, pairs agreeing on 32 bits: low 32707, mid 32656, top 32898; expected 32768.0 each (sd 181.0); ratios 0.9981 0.9966 1.0040; z -0.34 -0.62 0.72
B consecutive inputs R+i: M=2^24, pairs agreeing on 32 bits: low 32557, mid 32807, top 32777; expected 32768.0 each (sd 181.0); ratios 0.9936 1.0012 1.0003; z -1.17 0.22 0.05
C chained iterates (256 chains x 65536 steps): M=2^24, pairs agreeing on 32 bits: low 32607, mid 33143, top 33023; expected 32768.0 each (sd 181.0); ratios 0.9951 1.0114 1.0078; z -0.89 2.07 1.41
D single-bit differences: 65536 cells x 4096 pairs, max |z| 4.22 at input bit 161 output bit 130 (largest of 65536 normal cells is about 4.4); mean z^2 0.9934 (expected 1)
```

The coincidence rates lie within |z| <= 2.07 of the random-function values. If the real pair-coincidence rate is (1 - eps) of the random value, the same success needs about 0.5 log2(1/(1 - eps)) more bits of time, 0.0073 bit for eps = 0.01.

Further evidence on the same embedding from earlier builds (other constants or another digest mask PD; GPU, F checked against a CPU reference on 20,000 points with 0 mismatches): the length of a rho walk on F truncated to w bits has mean ratio to the random-function value 1.0017 (CI95 0.9977 to 1.0057) at w = 44 and 1.0039 (0.9958 to 1.0120) at w = 48 for the 8-round F, and 1.0041 (1.0001 to 1.0081) at w = 44, 0.9939 (0.9859 to 1.0019) at w = 48 for the 12-round F. These test the embedding and the truncation in rho length only.

### 7.3 The emitted program, executed (our runs, not organizer runs)

other4_test.py (Appendix D) executes the assembled bytes: other.bin decoded from its 32-byte encoding, and the straight line (prog.bin and the 15 prefilter instructions) decoded from its packed 39-bit encoding and compiled to Python integer operations (D.3, D.4).
- **Routines, at the full-size immediates of this package.** The straight line against the plain 12-round implementation on every lane (2 x 256 points, 3 chained steps) and the prefilter word; setup, setwalk, restart and its halting call, evalF and the message builder against the plain implementation; a hit with no DP walk and the hit-counter abort; restart across a word wrap (t(2S - 1) to t(2S)); the DP handler on its path over all S words of a full table, writing the record into the slot of trail 255, 3 S + 17 and 5 S - 1; a match in each of the five slots of the first, a middle and the last word, with the trail number it yields and its operation count; the DP mask of the hit handler against the comparison x < THR on 1,024 constructed walks, and the iteration that reaches Tb. Each executed count equals the count of Section 4.3.
- **Replay.** Pairs of trails of the 12-bit truncation of F with a 4-bit DP: 45 pairs with the same end (the replay measures la, aligns, finds the pair; the executed count equals 9 + (la - 1)(e + 8) + (e + 4) + 2 + 2 + n (e + 7) + 2 + 2 + (k - 1)(2e + 13) + (9 + 2e) + 67 exactly, and the pair is checked with an independent Keccak) and 15 pairs with different ends (a false key match: the replay exhausts and the attempt halts), and the cap guard of the measuring walk.
- **End to end at reduced width.** The whole emitted program (setup, loop, straight line, hit handler, DP handler, restart, replay, output) runs with the planes W..255 set to zero after each step and the replay's F truncated alike (one extra ANDI in evalF, test builds only), the other immediates reduced; instruction for instruction it is the program of the full-size build. 16 runs on eight parameter sets (W = 26; W = 32 with a replay cap that refuses long colliding trails; a table of 400 words; a hit cap of 3; Tb = 5; U = 264; a table of 264 words with U = 1,320, so that every word fills its five slots; no comparison planes). Every pair found was checked with an independent Keccak, the executed operations were at or below the counted bounds of Section 4.3, and the sub-counts (setwalk, gather, loop, replay) matched exactly: 444 checks, 0 failures.

## 8. Credits and literature

A credit is not an endorsement; nobody named here has reviewed this package.

- **jungjipdo, entry 67f781f8 (sha3-256-r6).** Its Section 3 describes the step design this package follows: theta evaluated lazily per chi row, per-row complement subsets, dead-code elimination, the digest written over the input register, last-use allocation into a declared register file, and the straight-line instruction format (3-bit opcode, three 12-bit registers, stored there in 5 bytes, packed here at 39 bits); the register-file convention of Section 3.6 is its convention. We read its proof as a description; the generator, self-test, ledger, search code and text are our own, and none of its code was run, imported or compiled. It is on another challenge, so it is credited here and not declared as a dependency.
- **mitchuski, entry c9a7e62c (sha3-256 Pareto round 24).** Its search uses a distinguished-point threshold DT that is not a power of two, a replay cap in place of a trail cut, and four records per table word; this package keeps the first two from ac0b6304 (Section 4) and replaces the table layout; credited for them. It is on another challenge, so it is credited here and not declared as a dependency. None of its code was run, imported or compiled.
- **Kepler** (a research assistant working with Jbenisek) proposed the structured constants S3-04 of Section 2; the conditions, the basis and the checks are ours.
- **Our entries ac0b6304 (S304R12, sha3-256 Pareto round 12, 124.36065) and c7ff4942 (SHA3R12C, sha3-256 Pareto round 12, 124.89966)**, the declared dependencies. ac0b6304 is the entry of this round of this design: its step program, generator, self-test, experiment program, search and other code are the base of this package, and what changed is the polarity plan of Section 3.3 and the packed straight line of Section 3.6 with its larger table. c7ff4942 is the generic entry of this round; the search, replay, success bound and rare-operation accounting follow it.
- **J. Guo, M. Liu, L. Song, Linear Structures: Applications to Cryptanalysis of Round-Reduced Keccak, ASIACRYPT 2016.** The linear-structure placement of message lanes that keeps round 0 affine (Section 2).
- **P. C. van Oorschot and M. J. Wiener, Parallel collision search with cryptanalytic applications, J. Cryptology 12 (1999); J. M. Pollard (1975).** The distinguished-point and rho methods.
- **G. Bertoni, J. Daemen, M. Peeters, G. Van Assche, Keccak implementation overview.** The lane complementing transform, applied plane by plane in Sections 3.2 and 3.3.

## Appendix A. The exact ledger

This program (cert4.py, with the inputs of this row written into it) computes the step count, the success bound of Section 5, N, the memory table and the integer certificate. It uses integers and Fractions; Decimal with 80 digits is used only for the exponentials and logarithms of the success bound. The constants of the rare operations and of the replay are the counts of Section 4.3, printed by `other4.py build` (D.2). H, kappa, S, U and Tb were chosen by the parameter scan, charged in PRE as P from its counted evaluations (scan_counts.txt, Section 3.7); the run below re-checks that Tb is the least multiple of 2^91 with success at least 0.39.

```python
INLINE = {
"ledger.txt": "LS1 step ledger (256 lanes, one chain step, 12 rounds), streaming generator gen3\nXOR 48112\nAND 9567\nOR  6689\nNOT 1737  (row complements chosen pre-DCE: 1328)\nLOAD 0\nSTORE 0\nTOTAL 66105\nTRICKROWS 2871 ; forced term polarities 45\nfeed NOTs 0 (digest polarity folded into the chain function: F(u)=H(m(u))^PD)\nnodes created pre-DCE 66105 ; ring peak 6852 of 8192 ; linear forms 1088 of 1920\nmax live values 1925 ; registers used 2181 (limit 2304)\nconstants trial 1214 of 512 ; optmode 4 ; round-1 greedy gain 75\nannealing iterations per round 600000000\ntrials carried to the plan build 1\nplan r2 predicted row cost 1781 theta NOTs 77 free polarities set 0\nplan r3 predicted row cost 1776 theta NOTs 16 free polarities set 0\nplan r4 predicted row cost 1769 theta NOTs 16 free polarities set 0\nplan r5 predicted row cost 1779 theta NOTs 15 free polarities set 0\nplan r6 predicted row cost 1772 theta NOTs 18 free polarities set 0\nplan r7 predicted row cost 1779 theta NOTs 13 free polarities set 0\nplan r8 predicted row cost 1778 theta NOTs 9 free polarities set 0\nplan r9 predicted row cost 1786 theta NOTs 15 free polarities set 0\nplan r10 predicted row cost 1773 theta NOTs 12 free polarities set 0\nplan r11 predicted row cost 260 theta NOTs 0 free polarities set 0\ngenerator peak RSS (VmHWM, this process image) 308 KiB = 315392 bytes (limit 1048576)\n",
"size.txt": "   text\t   data\t    bss\t    dec\t    hex\tfilename\n  52038\t     12\t 266816\t 318866\t  4dd92\tgen3\n",
"counts.txt": "other code: 1884 instructions x 32 bytes = 60288 bytes (other.bin sha256 784f789a0c6316a545e763885762ebc663421fec76879138af030b4d3d2a8d25)\nprefilter: 15 instructions x 39 bits, packed (pf.bin sha256 972ca2f8bdd7fee3a6bf994d75a2e11c8992993e89b113ffe70df543de4a2a5e); the straight-line block = prog.bin then pf.bin, 66120 instructions, sits in front of instruction 26 (label loop)\ndata image: 16 words x 32 bytes = 512 bytes (data.bin sha256 9b26fdee8d7bddc59a0d3bee6fdf0dee29d0065a6f5b17c34a6d08cd3cbbffe7): KW[0..6], PD, 8 output words\nmemory map (words): TAB 0..18071, LID 18072..18327, LST 18328..18583, data 18584..18599\nroutine entry points (instruction index): start 0, loop 26, hit 28, dpl 158, dp1 160, gather 204, record 402, probe 414, insert 438, ins 445, match0 448, cont 463, dl 466, restart 467, setwalk 478, evalF 1761, outm 1791, match 1818, meas 1827, end 1884\nn_instr            1884\nsetwalk            1283\nrestart            1293\nrestart_halt       3\nhit                131\nctz_clear          44\ngather             198\nrecord_slot        12\nprobe_word         24\ninsert             7\ndp_fixed           266\ndp_max             433994\ndl_final           1\ne_eval             3281\ne_outm             27\nmatch_entry        12\nmeas_iter          3289\nmeas_last          3285\nreplay_iter        6575\nreplay_const       79\nreplay_max         396742764064743664068396870177292025935\nsetup              355097\nstatic opcode mix: OR 415 ANDI 327 SHRI 274 AND 271 SHL 258 SHLI 64 SHR 50 ST 21 EQI 21 MOV 19 ADDI 18 XOR 18 BNZ 17 MOVI 15 LDA 15 BZ 14 NOT 12 JMP 10 JAL 9 LTI 6 HALT 5 LD 5 ADD 4 SUBI 4 EQ 3 JR 3 SUB 3 RND 1 PERM 1 LT 1\nhighest register named: 2190 (file of 2192)\n",
"params.json": "{\n \"NR\": 12,\n \"HF\": 111,\n \"DPLO\": 145,\n \"DK\": 10,\n \"DT\": 694,\n \"S\": 18072,\n \"U\": 90360,\n \"SB\": 15,\n \"W\": 633825300114114700748351602688,\n \"J\": 63458,\n \"LRC\": 40221285894641490680088896003375104,\n \"Tb\": 1326064821300054183508427017256173568,\n \"HMAX\": 45401231542821241255142274482831361,\n \"PFLO\": 240,\n \"PFN\": 16\n}",
"stack.txt": "16384\n",
"scan_counts.txt": "float_evals 157829\nfloat_bins 2005556545\nexact_evals 21\nexact_bins 1332618\n"
}
# cert4.py - LS1 exact ledger at SHA3-256 round count NR: step count, success bound, N, memory, integer certificate
# (integers and Fractions; Decimal with 80 digits only for the exponentials and logarithms of the success bound).
#   python3 cert4.py            exact ledger of the row in this directory: ledger.txt (generator counts), size.txt
#                               (generator image), counts.txt (other code), params.json (search parameters)
#   python3 cert4.py --scan     chooses the DP threshold, the replay cap, S, U, Tb for this row (float model, then the exact Tb) -> params.json
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
REGUSED = int(re.search(r'registers used (\d+)', led).group(1)); assert REGUSED <= 2181
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

# ---- memory (Section 6) ----
REGS = 2192                                      # registers 0..2,180 by the straight line, 2,181..2,190 search state, 2,191 spare
sz = rd('size.txt').split('\n')[1].split()
GEN_IMAGE = int(sz[0]) + int(sz[1]) + int(sz[2])  # gen3: text + data + BSS, size(1); all arrays are static
GEN_STACK = int(rd('stack.txt')) if (INLINE or os.path.exists('stack.txt')) else 8192                                 # stack reserve; the run completes with the stack limited to this value (stack.txt, written by row4.sh)
GEN_HWM = int(re.search(r'VmHWM, this process image\) \d+ KiB = (\d+) bytes', led).group(1))
MARGIN = 0


def mem_search(S, NI):
    return {'register file, 2,192 words': 32 * REGS,
            'straight line incl. prefilter, %d instructions x 39 bits, packed' % (LINE + PF): (39 * (LINE + PF) + 7) // 8,
            'other code (setup, loop, handlers, restart, replay), %d instructions x 32 bytes' % NI: 32 * NI,
            'table, %d words (five slots each)' % S: 32 * S,
            'LID and LST of the 256 walks, 512 words': 32 * 512,
            'data image (lane constants K, PD, output pair), 16 words': 32 * 16}


def mem_pre():
    return max(GEN_HWM, GEN_IMAGE + GEN_STACK) + (39 * LINE + 7) // 8   # the generator (image and stack) plus the program it writes


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
    p = s - (e2 + e3 + e4 + e5 + e6 + D(2) ** -60)
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
def ledger(TB, S, U, LRC, c, NI):
    replay = (c['meas_iter'] + c['replay_iter']) * LRC + c['replay_const']   # at most one replay per attempt, lengths <= LRC
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
    P: the parameter scan (cert4.py --scan; counts in scan_counts.txt): float-model bins and evaluations 2^16 and 2^17 each,
       exact bins and evaluations 2^24 and 2^27 each, grid bookkeeping 2^20;
    O: `other4.py build`: 2^8 per emitted instruction, 2^13 per SHA-256 block of other.bin, pf.bin and data.bin, data image 2^12."""
    SWEEPS = 3; TOPK = int(re.search(r'^trials carried to the plan build (\d+)', led, re.M).group(1)); OPTIT = int(re.search(r'^annealing iterations per round (\d+)', led, re.M).group(1))
    plan_builds = 1 + SWEEPS * 640 + (NR - 2)                # round-1 greedy (prefix builds counted as full) and the passes
    B = 512 + TOPK * (plan_builds + 1) + (plan_builds + 1)
    A = (TOPK + 1) * (NR - 2) * OPTIT
    G = B * 2 ** 32 + A * 2 ** 12 + 512 * 2 ** 10 + 2 ** 32   # + the plan's row tables (mk_tables2), one build's charge
    K = 2 ** 24
    sc = {l.split()[0]: int(l.split()[1]) for l in rd('scan_counts.txt').split(chr(10)) if l.strip()}
    P_ = (sc['float_bins'] << 16) + (sc['float_evals'] << 17) + (sc['exact_bins'] << 24) + (sc['exact_evals'] << 27) + 2 ** 20
    HB = sha_blocks(32 * NI) + sha_blocks((39 * PF + 7) // 8) + sha_blocks(32 * 16)
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
replay, HMAX, Rr, EXPO = ledger(TB, S, U, LRC, c, NI)
assert HMAX == P['HMAX']
print('hit counter: HMAX =', HMAX, '; P[abort before the stop on success] <= exp(-%d) < 2^-1000' % (EXPO.numerator // EXPO.denominator))
print('replay: (%d + %d) LRC + %d = %d (measuring walk e + 8, lock step 2e + 13, e = %d)' % (c['meas_iter'], c['replay_iter'], c['replay_const'], replay, c['e_eval']))
assert c['e_eval'] == UNIT + 29
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
print('search memory', run_total, '; preprocessing (gen3): image', GEN_IMAGE, '+ stack', GEN_STACK, '+ program', (39 * LINE + 7) // 8, '=', pre_total, '(measured resident peak %d)' % GEN_HWM)
mem = max(run_total, pre_total)
assert mem <= 2 ** 20 - MARGIN
print('memory', mem, '<= 2^20 = 1048576 with a margin of', 2 ** 20 - mem, 'bytes (search phase', 2 ** 20 - run_total, ', preprocessing', 2 ** 20 - pre_total, '): memory_log2_bytes = 20')
K, e = cert(N)
print('certificate: %d^%d * 2^%d < N^%d <= %d^%d * 2^%d' % (UNIT, K, e - 1, K, UNIT, K, e))
print('time_log2 = %d.%05d' % divmod(e, K))
print('score = time_log2 + max(0, memory_log2 - 20) = %d.%05d' % divmod(e, K))
```

Output:

```
rounds 12, unit 3252 word operations
step of 256 walks: straight line 66105 (xor 48112 and 9567 or 6689 not 1737) + prefilter 15 + test 2 + counter 3 = 66125
parameters: DP = planes 145..255 zero and the 10 planes below them < 694 (theta = 694 x 2^-121 = 2^-111.561208), replay cap LRC = 63458 x 633825300114114700748351602688 = 10.4999 / theta, U 90360 trails, S 18072 table words (90360 slots), key bits 50
Tb = 1326064821300054183508427017256173568 = 535593316 * 2^91 = 0.99762029 * 2^120, evaluations 0.997620 * 2^128
failure terms: F6 2.483e-4  F2 4.346e-6  F3 1.145e-5  F4 3.626e-6  success bound 0.3900000002  (2^91 steps fewer: 0.3899999991)
hit counter: HMAX = 45401231542821241255142274482831361 ; P[abort before the stop on success] <= exp(-2355563191584363937892) < 2^-1000
replay: (3289 + 6575) LRC + 79 = 396742764064743664068396870177292025935 (measuring walk e + 8, lock step 2e + 13, e = 3281)
main 87686036308466082884494736516064477184000  replay 396742764064743664068396870177292025935  rare 5947561332109582604423637996473067677  preprocessing 221768377805824 (builds 4376, annealing iterations 12000000000)
preprocessing parts: generator 67951072378880 basis 16777216 scan 153817280348160 assembly 8301568 (scan: float evaluations 157829 bins 2005556545, exact evaluations 21 bins 1332618; SHA-256 blocks 954)
preprocessing_log2: 2^35 < PRE / 3252 <= 2^36, declared 36
N = 88088726633862936131167557246006620083436
shares: main 0.99543 replay 0.00450 other 6.75e-05
      70144  register file, 2,192 words
     322335  straight line incl. prefilter, 66120 instructions x 39 bits, packed
      60288  other code (setup, loop, handlers, restart, replay), 1884 instructions x 32 bytes
     578304  table, 18072 words (five slots each)
      16384  LID and LST of the 256 walks, 512 words
        512  data image (lane constants K, PD, output pair), 16 words
search memory 1047967 ; preprocessing (gen3): image 318866 + stack 16384 + program 322262 = 657512 (measured resident peak 315392)
memory 1047967 <= 2^20 = 1048576 with a margin of 609 bytes (search phase 609 , preprocessing 391064 ): memory_log2_bytes = 20
certificate: 3252^100000 * 2^12434896 < N^100000 <= 3252^100000 * 2^12434897
time_log2 = 124.34897
score = time_log2 + max(0, memory_log2 - 20) = 124.34897
```

## Appendix B. The generator (gen3.c) and the self-test (selftest.c)

Compiled with `gcc -O2 -static -nostdlib -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns -fno-stack-protector -fno-pie -no-pie -DNR=12`; run as `gen3 512 1000 4`.

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
 *
 * STREAMING: nodes live in a ring of W slots that holds ONE round (rounds 0 and 1 together). When a round is built,
 * its dead nodes are removed (liveness from the state planes, or from the digest planes in the last round), every
 * value gets its last use (all uses of a value lie in its own round or, for a state plane, in the next round), the
 * registers are allocated in node order and the instructions are written to prog.bin at once. The 1,600 state planes
 * are then pinned (register and flags) and the ring is reused for the next round. The program is never held.
 * Register j (j < 256) holds input plane j and receives digest plane j (free chain feed).
 *
 * Outputs of the charged run (gen3 512 1000 4): the file prog.bin (39 bits/instr, packed: 3-bit op, 12-bit dst, a, b; instruction i is bits 39i..39i+38 of the file, little-endian) and the ledger on
 * standard output. No other file is written. The separate inspection command (gen3 1 TRIAL 4 inspect), a check run, writes
 * meta.txt and plan.txt (the decisions of the plan, read by the Python port); the search does not run it.
 * Usage: gen3 ntrials first optmode.  ntrials > 1: the cheap build (optmode 0) of trials first..first+ntrials-1, the
 * full build (optmode) of the TOPK lowest of them, and the lowest full count wins.  The search runs "gen3 512 1000 4". SC = 16, WLOOK = 3.
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
#define OPTIT 200000000
#endif
#ifndef TOPK
#define TOPK 1           /* trials carried from the cheap selection to the full build */
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
#define MAXF 1920
static u64 form[MAXF][4]; static u16 formnode[MAXF]; static int nform, maxform;
#define FH 2048
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
static V S[25][64], NS[25][64], Cc[5][64], Dd[5][64];
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
static u8 FFb[NR][40], GGb[NR][40]; static u8 decided[NR]; static int curpass;
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
    if(mv==0){ TOGD(x,zz); fflip[x][zz]^=1; nfl+= fflip[x][zz]?1:-1; }
    else if(mv==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGD(x1,zz); TOGD(x2,z2); gflip[x][zz]^=1; nfl+= gflip[x][zz]?1:-1; }
    else { int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGV(x,py,zz); TOGD(x1,zz); TOGD(x2,z2); phic[pl][zz]^=1; }
    long d=(cost+nfl)-(c0+nf0);
    int acc= d<=0;
    if(!acc){ double u=(double)((pxs()>>11)&((1UL<<53)-1))/(double)(1UL<<53); acc= u < mexp(-(double)d/T); }
    if(acc){ if(cost+nfl<best){ best=cost+nfl; memcpy(bestf,fflip,sizeof fflip); memcpy(bestg,gflip,sizeof gflip); memcpy(bestp,phic,sizeof phic); } }
    else {
      if(isg==0){ TOGD(x,zz); fflip[x][zz]^=1; nfl+= fflip[x][zz]?1:-1; }
      else if(isg==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGD(x1,zz); TOGD(x2,z2); gflip[x][zz]^=1; nfl+= gflip[x][zz]?1:-1; }
      else { int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGV(x,py,zz); TOGD(x1,zz); TOGD(x2,z2); phic[pl][zz]^=1; }
    }
  }
  memcpy(fflip,bestf,sizeof fflip); memcpy(gflip,bestg,sizeof gflip);
  long n=0; for(int x=0;x<5;x++) for(int z=0;z<64;z++) n+=fflip[x][z]+gflip[x][z];
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
static signed char ROWCt[32][32]; static u16 ARGt[32][32]; static int ROWMIN[32];
static u16 dec[NR][320]; static u8 decd[NR];
static void eval_row(int pat,int s,int j,int mc,int *cost,int *out,int *sel){
  int bb[5]; for(int X=0;X<5;X++) bb[X]=((pat>>X)&1)^((s>>X)&1);
  int c=0; for(int X=0;X<5;X++) c+=(s>>X)&1;
  int NSp[5]={0,0,0,0,0}; int bit=0; int k=(j+1)%5;
  for(int X=0;X<5;X++) sel[X]=0;
  for(int X=0;X<5;X++){ if(X==j) continue; int a=bb[(X+1)%5]^1, b=bb[(X+2)%5], tp;
    if(a==b){ c+=1; tp=a; } else { int ch=(mc>>(bit++))&1; c+=2; tp=ch; sel[X]=ch; } NSp[X]=bb[X]^tp; }
  if(j>=0){ int a=NSp[k]^1, b=bb[(j+2)%5], tp;
    if(a==b){ c+=1; tp=a; } else { int ch=(mc>>(bit++))&1; c+=2; tp=ch; sel[j]=ch; } NSp[j]=bb[j]^tp; }
  int o=0; for(int X=0;X<5;X++) o|=NSp[X]<<X;
  *cost=c; *out=o;
}
static void mk_tables2(void){
  for(int p=0;p<32;p++) for(int o=0;o<32;o++){ ROWCt[p][o]=99; ARGt[p][o]=0; }
  for(int p=0;p<32;p++) for(int j=-1;j<5;j++) for(int s=0;s<32;s++) for(int mc=0;mc<64;mc++){
    int c,o,sel[5]; eval_row(p,s,j,mc,&c,&o,sel);
    if(c<ROWCt[p][o]){ ROWCt[p][o]=(signed char)c; ARGt[p][o]=(u16)(s|((j+1)<<5)|(mc<<8)); } }
  for(int p=0;p<32;p++){ int m=99; for(int o=0;o<32;o++) if(ROWCt[p][o]<m) m=ROWCt[p][o]; ROWMIN[p]=m; }
}
static void polopt2(int r){
  static u8 pS[25][64], pC[5][64], pD[5][64];
  static u16 vrow[5][64][5]; static u8 vbit[5][64][5];
  static u8 pat0[320], pat1[320], outv[320];
  static u8 bf[5][64], bg[5][64], bo[320];
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC||islin(v.n)) return; pS[l][z]=v.p; }
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
  long nfl=0; memset(fflip,0,sizeof fflip); memset(gflip,0,sizeof gflip);
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
    long c0=cost;
    #define DOMOVE() \
      if(mv==0){ TOGD0(x,zz); fflip[x][zz]^=1; nfl+= fflip[x][zz]?1:-1; cost+= fflip[x][zz]?SC:-SC; } \
      else if(mv==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGD0(x1,zz); TOGD0(x2,z2); gflip[x][zz]^=1; nfl+= gflip[x][zz]?1:-1; cost+= gflip[x][zz]?SC:-SC; } \
      else { int Y=yy; int rw=Y*64+zz; \
        cost-=SC*F0(rw); outv[rw]^=(u8)dm; cost+=SC*F0(rw); \
        for(int X=0;X<5;X++) if(dm>>X&1){ int x1=(X+1)%5, x2=(X+4)%5, z2=(zz+1)&63; int rw1=vrow[X][zz][Y]; T1ROW(rw1,vbit[X][zz][Y]); TOGD1(x1,zz); TOGD1(x2,z2); } }
    DOMOVE();
    long d=cost-c0;
    int acc= d<=0;
    if(!acc){ double u=(double)((pxs()>>11)&((1UL<<53)-1))/(double)(1UL<<53); acc= u < mexp(-(double)d/T); }
    if(acc){ if(cost<best){ best=cost; memcpy(bf,fflip,sizeof bf); memcpy(bg,gflip,sizeof bg); memcpy(bo,outv,sizeof bo); } }
    else { /* undo: the move is an involution; re-apply it */
      if(mv==0){ TOGD0(x,zz); fflip[x][zz]^=1; nfl+= fflip[x][zz]?1:-1; cost+= fflip[x][zz]?SC:-SC; }
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
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ if(fflip[x][z]) for(int k=0;k<5;k++) pat0[vrow[x][z][k]]^=vbit[x][z][k];
    if(gflip[x][z]){ int x1=(x+1)%5,x2=(x+4)%5,z2=(z+1)&63; for(int k=0;k<5;k++){ pat0[vrow[x1][z][k]]^=vbit[x1][z][k]; pat0[vrow[x2][z2][k]]^=vbit[x2][z2][k]; } } }
  long n=0,c0t=0; for(int x=0;x<5;x++) for(int z=0;z<64;z++) n+=fflip[x][z]+gflip[x][z];
  for(int i=0;i<320;i++){ int o=bo[i]; if(ROWCt[pat0[i]][o]>=90) die("polopt2: infeasible row"); dec[r][i]=ARGt[pat0[i]][o]; c0t+=ROWCt[pat0[i]][o]; }
  decd[r]=1; pol_pred[r]=c0t; pol_nots[r]=n; pol_phi[r]=0;
}

static u64 KL[25];          /* lane constants of the absorbed state (var lanes: offset) */
static u64 PD[4];
static long nnot_rows, ntrick, nforced;


/* ---------- per-round finish: dead-code removal, counts, register allocation, emission, pinning ---------- */
static long cnt[5];
#define NREG 2304
static u16 freestk[NREG]; static int nfree; static u8 regbusy[NREG];
static long live, maxlive, maxreg, ninstr;
static int fdp=-1; static u8 eb[4000]; static int el; static u64 eacc; static int enb;   /* bit packer: enb (< 8) pending bits in eacc */
static int emitting;
static void alloc_init(void){
  memset(regbusy,0,sizeof regbusy);
  nfree=0; for(int r=NREG-1;r>=256;r--) freestk[nfree++]=(u16)r;
  live=0; maxlive=0; maxreg=0; ninstr=0; el=0; eacc=0; enb=0;
}
static void freereg(int r){ if(!regbusy[r]) die("free of a free register"); regbusy[r]=0; live--; if(r>=256) freestk[nfree++]=(u16)r; }
static void pin_state(void){
  for(int q=0;q<1600;q++){ preg[q]=0xFFFF; plast[q]=NOUSE; pfl[q]=0; }
  npin=0;
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC) continue;
    if(v.n>=PIN) die("state plane from an earlier round");
    if(nf[v.n]&F_LIN) die("linear state plane");
    if(nlast[v.n]==0xFFFE) die("two state planes share a node");
    int q=l*64+z; pord[q]=v.n; pfl[q]=(u8)(nf[v.n]&F_OPM); preg[q]= emitting? nreg[v.n] : 0; npin++;
    nlast[v.n]=0xFFFE; S[l][z].n=(u16)(PIN+q); }
}
static void finish_round(int last,int prefix){
  int lo= prefix? 256 : 0;
  for(int i=0;i<nn;i++) nf[i]&=(u8)~(F_LIVE|F_ST|F_OUT);
  if(!last){
    for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC) continue; if(v.n>=PIN) die("state plane from an earlier round"); nf[v.n]|=F_LIVE|F_ST; }
  } else {
    for(int j=0;j<256;j++){ V v=S[j>>6][j&63]; if(v.n==NC||v.n>=PIN||v.n<lo) die("digest plane constant, input or old");
      if(nf[v.n]&F_OUT) die("shared digest node"); nf[v.n]|=F_LIVE|F_OUT; nreg[v.n]=(u16)j; PD[j>>6]|=(u64)v.p<<(j&63); }
  }
  for(int i=nn-1;i>=lo;i--) if(nf[i]&F_LIVE){ int op=nf[i]&F_OPM; int a=na[i], b=nb[i];
    if(a<PIN) nf[a]|=F_LIVE; if(op!=O_NOT && b<PIN) nf[b]|=F_LIVE; }
  for(int i=lo;i<nn;i++) if(nf[i]&F_LIVE) cnt[nf[i]&F_OPM]++;
  if(emitting){
    for(int i=lo;i<nn;i++) if(nf[i]&F_LIVE){ int op=nf[i]&F_OPM; int a=na[i], b=nb[i];
      if(a>=PIN) plast[a-PIN]=(u16)i; else nlast[a]=(u16)i;
      if(op!=O_NOT){ if(b>=PIN) plast[b-PIN]=(u16)i; else nlast[b]=(u16)i; } }
    if(prefix){ for(int j=0;j<256;j++){ nreg[j]=(u16)j; if(nlast[j]!=NOUSE){ regbusy[j]=1; live++; } } if(live>maxlive) maxlive=live; }
    else { for(int q=0;q<1600;q++) if(preg[q]!=0xFFFF && plast[q]==NOUSE) die("state plane without use"); }
    for(int i=lo;i<nn;i++){
      if(!(nf[i]&F_LIVE)) continue;
      int op=nf[i]&F_OPM; int a=na[i], b=(op==O_NOT)?a:nb[i];
      int ra= a>=PIN? preg[a-PIN] : nreg[a];
      int rb= op==O_NOT? 0 : (b>=PIN? preg[b-PIN] : nreg[b]);
      int ops[2]={a,b};
      for(int k=0;k<2;k++){ int o=ops[k]; if(k==1&&o==a) break;
        if(o>=PIN){ if(plast[o-PIN]==i){ freereg(preg[o-PIN]); preg[o-PIN]=0xFFFF; npin--; } }
        else if(!(nf[o]&(F_ST|F_OUT)) && nlast[o]==i) freereg(nreg[o]); }
      int dst;
      if(nf[i]&F_OUT){ dst=nreg[i]; if(regbusy[dst]) die("output register busy"); }
      else if(nfree>0) dst=freestk[--nfree];
      else { die("out of registers"); dst=0; }
      if(!(nf[i]&(F_ST|F_OUT)) && nlast[i]==NOUSE) die("live node without use");
      regbusy[dst]=1; live++; nreg[i]=(u16)dst; if(live>maxlive) maxlive=live; if(dst+1>maxreg) maxreg=dst+1;
      int code= op==O_XOR?0: op==O_AND?1: op==O_OR?2: 3;
      u64 w=(u64)code | (u64)dst<<3 | (u64)ra<<15 | (u64)rb<<27;
      eacc|=w<<enb; enb+=39; while(enb>=8){ eb[el++]=(u8)eacc; eacc>>=8; enb-=8; }
      if(el>=3995){ sc3(1,fdp,(i64)eb,el); el=0; }
      ninstr++;
    }
    if(!prefix && npin!=0) die("state plane not freed");
  }
  if(!last) pin_state();
}

static int stop_prefix; static long prefix_ops;
static void unpack_fg(int r){ for(int i=0;i<320;i++){ fflip[i/64][i%64]=GB(FFb[r],i); gflip[i/64][i%64]=GB(GGb[r],i); } }
static void pack_fg(int r){ memset(FFb[r],0,40); memset(GGb[r],0,40);
  for(int i=0;i<320;i++){ FFb[r][i>>3]|=(u8)(fflip[i/64][i%64]<<(i&7)); GGb[r][i>>3]|=(u8)(gflip[i/64][i%64]<<(i&7)); } }

static void build(void){
  nn=0; nform=0; cnt_emit=0; nnot_rows=0; ntrick=0; nforced=0; npin=0;
  for(int k=0;k<5;k++) cnt[k]=0;
  memset(fh,0,sizeof fh); memset(ch,0,sizeof ch);
  for(int q=0;q<1600;q++){ preg[q]=0xFFFF; plast[q]=NOUSE; pfl[q]=0; }
  PD[0]=PD[1]=PD[2]=PD[3]=0;
  if(emitting) alloc_init();
  for(int j=0;j<256;j++){ int n=newnode(O_IN,0,0); u64 m[4]={0,0,0,0}; m[j>>6]=1UL<<(j&63); nf[n]|=F_LIN; linid[n]=(u16)fadd(m,n); }
  for(int l=0;l<25;l++) for(int z=0;z<64;z++) S[l][z]=K_((KL[l]>>z)&1);
  for(int z=0;z<64;z++){
    S[1][z]=MK(z,(KL[1]>>z)&1); S[6][z]=MK(64+z,(KL[6]>>z)&1);
    S[4][z]=MK(128+z,(KL[4]>>z)&1); S[9][z]=MK(192+z,(KL[9]>>z)&1);
  }
  for(int z=0;z<64;z++){
    S[11][z]=xorv(xorv(MK(z,0),MK(64+z,0)),K_((KL[11]>>z)&1));
    S[14][z]=xorv(xorv(MK(128+z,0),MK(192+z,0)),K_((KL[14]>>z)&1));
  }
  for(int r=0;r<NR;r++){
    int last=(r==NR-1);
    memset(fflip,0,sizeof fflip); memset(gflip,0,sizeof gflip);
    if(r==1 && optmode>=3){ memcpy(fflip,F1,sizeof fflip); memcpy(gflip,G1,sizeof gflip); }
    if(optmode && r>=2){
      if(decided[r]) unpack_fg(r);
      else if(r==curpass){ if(optmode>=4 && !last) polopt2(r); else polopt(r,last); pack_fg(r); decided[r]=1; return; }
    }
    if(r>=2){ nn=0; memset(ch,0,sizeof ch); }      /* the ring holds one round (rounds 0 and 1 together) */
    /* theta: C[.][63] first, then per z: C[.][z], D[.][z] (keeps few C live) */
    for(int x=0;x<5;x++){ V s=S[x][63]; for(int y=1;y<5;y++) s=xorv(s,S[x+5*y][63]); Cc[x][63]= gflip[x][63]? notv(s) : s; }
    for(int z=0;z<64;z++){
      if(z<63) for(int x=0;x<5;x++){ V s=S[x][z]; for(int y=1;y<5;y++) s=xorv(s,S[x+5*y][z]); Cc[x][z]= gflip[x][z]? notv(s) : s; }
      for(int x=0;x<5;x++){ Dd[x][z]=xorv(Cc[(x+4)%5][z],Cc[(x+1)%5][(z+63)&63]); if(fflip[x][z]) Dd[x][z]=notv(Dd[x][z]); }
    }
    int nY=last?1:5, needmask=last?0x0F:0x1F;
    for(int Y=0;Y<nY;Y++) for(int z=0;z<64;z++){
      V b[5];
      for(int X=0;X<5;X++){ int y=X, x=(3*Y+X)%5; int zz=(z-ROT[x][y]+64)&63; b[X]=xorv(S[x+5*y][zz],Dd[x][zz]); }
      int distinct=1; for(int X=0;X<5;X++){ if(b[X].n==NC) distinct=0; for(int X2=X+1;X2<5;X2++) if(b[X].n==b[X2].n) distinct=0; }
      int best,bj;
      int havesel=0, rsel[5]={0,0,0,0,0};
      if(distinct && optmode>=4 && r>=2 && !last && decd[r]){ int p=0; for(int X=0;X<5;X++) p|=b[X].p<<X;
        u16 dd=dec[r][Y*64+z]; best=dd&31; bj=((dd>>5)&7)-1; int cc,oo; eval_row(p,best,bj,dd>>8,&cc,&oo,rsel); havesel=1; }
      else if(distinct){ int p=0; for(int X=0;X<5;X++) p|=b[X].p<<X; best=tS[last][mixfree][p]; bj=tJ[last][mixfree][p]; }
      else best=row_choose(b,needmask,&bj,0);
      for(int X=0;X<5;X++) if(best>>X&1){ b[X]=notv(b[X]); nnot_rows++; }
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
    for(int z=0;z<64;z++) NS[0][z].p^=(RC[r]>>z)&1;   /* iota */
    for(int l=0;l<25;l++) for(int z=0;z<64;z++) S[l][z]=NS[l][z];
    if(r==0) continue;
    finish_round(last, r==1);
    if(r==1 && stop_prefix){ prefix_ops=cnt[1]+cnt[2]+cnt[3]+cnt[4]; return; }
  }
}

#include "kbasis.h"
static u64 rs;
static u64 xs(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static void set_consts(int trial){
  for(int l=0;l<25;l++) KL[l]=0;
  KL[16]=0x8000000000000006UL;
  if(trial>=1000){ static const int fl2[12]={0,2,3,5,7,8,10,12,13,15,11,14}; /* S3-04: a structured set, r from the trial seed */
    rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs(); u64 r=xs();
    for(int i=0;i<12;i++){ u64 k=KB0[i]; for(int j=0;j<64;j++) if((r>>j)&1) k^=KBV[j][i]; KL[fl2[i]]=k; } return; }
  if(trial>0){ rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs();
    static const int fl[12]={0,2,3,5,7,8,10,12,13,15,11,14};
    for(int i=0;i<12;i++) KL[fl[i]]=xs(); }
}

static long r1gain;
static void r1greedy(void){
  /* round 1: physical complements on C and D (linear forms), kept when the live ops of rounds 0..1 drop */
  memset(F1,0,sizeof F1); memset(G1,0,sizeof G1);
  memset(phib,0,sizeof phib); memset(mixb,0,sizeof mixb); memset(decided,0,sizeof decided); curpass=99;
  stop_prefix=1; build(); long best=prefix_ops, b0=best;
  for(int sw=0;sw<R1SWEEPS;sw++){ int imp=0;
    for(int v=0;v<640;v++){ u8 *p= v<320? &F1[v/64][v%64] : &G1[(v-320)/64][v%64];
      *p^=1; build(); long c=prefix_ops;
      if(c<best){ best=c; imp=1; } else *p^=1; }
    if(!imp) break; }
  stop_prefix=0; r1gain=b0-best;
}
static void fullplan(void){
  if(optmode>=3) r1greedy();
  memset(phib,0,sizeof phib); memset(mixb,0,sizeof mixb); memset(decided,0,sizeof decided); memset(decd,0,sizeof decd);
  memset(pol_phi,0,sizeof pol_phi); memset(pol_pred,0,sizeof pol_pred); memset(pol_nots,0,sizeof pol_nots);
  if(optmode){ for(int k=2;k<NR;k++){ curpass=k; build(); } }
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
  os("varlanes 1 6 4 9 ; lane11 = u0^u1^K11 ; lane14 = u2^u3^K14\n");
  os("pd "); for(int i=0;i<4;i++){ ox(PD[i]); oc(i<3?' ':'\n'); }
  os("ninstr "); ou(ninstr); oc('\n');
  oflush(); fclose_(fd_out);
  }
  /* plan.txt: every decision of the build, for the Python port */
  if(insp){
  fd_out=fopen_w("plan.txt");
  os("trial "); ou(bestt); oc('\n');
  os("nr "); ou(NR); os(" optmode "); ou(optmode); os(" trick "); ou(TRICK); os(" lasttrick "); ou(LASTTRICK); os(" notfold "); ou(NOTFOLD); oc('\n');
  { u8 a[40], g[40]; memset(a,0,40); memset(g,0,40); for(int i=0;i<320;i++){ a[i>>3]|=(u8)(F1[i/64][i%64]<<(i&7)); g[i>>3]|=(u8)(G1[i/64][i%64]<<(i&7)); }
    os("F1 "); hexbytes(a,40); oc('\n'); os("G1 "); hexbytes(g,40); oc('\n'); }
  for(int r=2;r<NR;r++){ os("FG "); ou(r); oc(' '); hexbytes(FFb[r],40); oc(' '); hexbytes(GGb[r],40); oc('\n'); }
  for(int r=0;r<NR;r++){ os("PHI "); ou(r); oc(' '); hexbytes(phib[r],200); oc('\n'); }
  for(int r=2;r<NR;r++) if(decd[r]){ u8 d[640]; for(int i=0;i<320;i++){ d[2*i]=(u8)(dec[r][i]&255); d[2*i+1]=(u8)(dec[r][i]>>8); } os("DEC "); ou(r); oc(' '); hexbytes(d,640); oc('\n'); }
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
    os("generator peak RSS (VmHWM, this process image) "); ou(hwm); os(" KiB = "); ou(hwm*1024); os(" bytes (limit 1048576)\n");
    oflush();
  }
  if(maxreg>NREG) return 2;
  return 0;
}
```

kbasis.h (the structured set S3-04 of Section 2):

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

The self-test (compiled with `-DRR=12`; `selftest kat` prints 300 known answers, compared with hashlib and the organizer's verifier/keccak.py; `selftest run 4 [seed]` runs the chained check):

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
  prog=malloc(ninstr*5); if(fread(prog,5,ninstr,f)!=(size_t)ninstr){ fprintf(stderr,"short prog\n"); exit(2); } fclose(f);
}
/* message m(u): 128 bytes = lanes 0..15 */
static void msg_of(const u64 u[4], uint8_t m[128]){
  u64 L[16]; for(int i=0;i<16;i++) L[i]=KL[i];
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
  const uint8_t *p=prog;
  for(long i=0;i<ninstr;i++,p+=5){
    u64 w=(u64)p[0]|(u64)p[1]<<8|(u64)p[2]<<16|(u64)p[3]<<24|(u64)p[4]<<32;
    int op=w&7, d=(w>>3)&4095, a=(w>>15)&4095, b=(w>>27)&4095; W256 t;
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

Output of the run (the ledger, standard output) and of the self-test:

```
LS1 step ledger (256 lanes, one chain step, 12 rounds), streaming generator gen3
XOR 48112
AND 9567
OR  6689
NOT 1737  (row complements chosen pre-DCE: 1328)
LOAD 0
STORE 0
TOTAL 66105
TRICKROWS 2871 ; forced term polarities 45
feed NOTs 0 (digest polarity folded into the chain function: F(u)=H(m(u))^PD)
nodes created pre-DCE 66105 ; ring peak 6852 of 8192 ; linear forms 1088 of 1920
max live values 1925 ; registers used 2181 (limit 2304)
constants trial 1214 of 512 ; optmode 4 ; round-1 greedy gain 75
annealing iterations per round 600000000
trials carried to the plan build 1
plan r2 predicted row cost 1781 theta NOTs 77 free polarities set 0
plan r3 predicted row cost 1776 theta NOTs 16 free polarities set 0
plan r4 predicted row cost 1769 theta NOTs 16 free polarities set 0
plan r5 predicted row cost 1779 theta NOTs 15 free polarities set 0
plan r6 predicted row cost 1772 theta NOTs 18 free polarities set 0
plan r7 predicted row cost 1779 theta NOTs 13 free polarities set 0
plan r8 predicted row cost 1778 theta NOTs 9 free polarities set 0
plan r9 predicted row cost 1786 theta NOTs 15 free polarities set 0
plan r10 predicted row cost 1773 theta NOTs 12 free polarities set 0
plan r11 predicted row cost 260 theta NOTs 0 free polarities set 0
generator peak RSS (VmHWM, this process image) 308 KiB = 315392 bytes (limit 1048576)
kat messages 300 (lengths 0..299): 24-round vs hashlib mismatches 0; 12-round vs organizer verifier mismatches 0
selftest: 4096 chained evaluations (4 batches x 256 trails x 4 steps), 0 mismatches, 66105 instructions
selftest: 4096 chained evaluations (4 batches x 256 trails x 4 steps), 0 mismatches, 66105 instructions
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
typedef struct { u64 w[4]; } W256;
static W256 R[2304];
static void load(void){
  FILE *f=fopen("meta.txt","r"); char line[512];
  while(fgets(line,sizeof line,f)) sscanf(line,"ninstr %ld",&ninstr);
  fclose(f); f=fopen("prog.bin","rb"); prog=calloc((ninstr*39+7)/8+8,1);   /* packed: instruction i is bits 39i..39i+38, little-endian */
  if(fread(prog,1,(ninstr*39+7)/8,f)!=(size_t)((ninstr*39+7)/8)) exit(2); fclose(f);
}
static void run_prog(void){
  for(long i=0;i<ninstr;i++){
    const uint8_t *p=prog+(39*i)/8; int s=(int)((39*i)%8);
    u64 w=((u64)p[0]|(u64)p[1]<<8|(u64)p[2]<<16|(u64)p[3]<<24|(u64)p[4]<<32|(u64)p[5]<<40)>>s;
    int op=w&7, d=(w>>3)&4095, a=(w>>15)&4095, b=(w>>27)&4095;
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
{"NR": 12, "HF": 111, "DPLO": 145, "DK": 10, "DT": 694, "S": 18072, "U": 90360, "SB": 15, "W": 633825300114114700748351602688, "J": 63458, "LRC": 40221285894641490680088896003375104, "Tb": 1326064821300054183508427017256173568, "HMAX": 45401231542821241255142274482831361, "PFLO": 240, "PFN": 16}
```

```python
#!/usr/bin/env python3
# other4.py - the non-straight-line code of LS1 (setup, loop control, hit handler, DP handler with the packed table,
# restart, replay, final output), written as real instructions of the machine of proof.md Section 3.5,
# plus the machine (an interpreter that executes the emitted bytes) and the counting of the operations.
#
#   python3 other4.py build [meta.txt]    reads params.json (NR, S, U, SB, LRC, Tb, HMAX, DPLO, DK, DT, PFLO, PFN), writes other.bin
#                                          (the 32-byte instructions), pf.bin (the 15 prefilter ORs, 39 bits each, packed), data.bin
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
#
# Machine (collision-frontier-v5 256-bit word RAM, the declared register file of 2,192 registers R0..R2191):
#   every instruction below costs one word operation, except PERM, which costs one unit (UNIT = 271 NR operations, the model's
#   rule: one selected-round sponge permutation is one unit).  Straight-line instructions (39 bits, packed: XOR AND OR NOT on
#   registers) cost one operation each.  Other instructions are 32 bytes: op(1) d(2) a(2) b(2) 0(1) imm(24, 192 bits).
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
C, NXT, IDN, RHO, ONES, PF, H, LR, LR2, ZERO = range(2181, 2191)   # state (2,181..2,190; 2,191 spare)
(L, DPM, C1, ACC, TT, REC, SLOT, TR, F, X, Y, LV, NP, NM, ONEB, V, MN, E, PTR, SS, ID, STV) = range(256, 278)
(P, Q, N, MM, LA, LB, UU, FF, PDR, X0, X1, X2, X3, TQ, FP) = range(280, 295)
Z = 295
REP = 296                                                             # the DP record repeated in the five slots
W0 = 300                                                              # W0..W6, the 1600-bit state of evalF
NREGS = 2192


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
        for x in s.ins: assert 0 <= x[4] < 1 << 192 and max(x[1:4]) < 2192

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
    LID, LST, MISC = S, S + 256, S + 512
    OUT = MISC + 8
    A = Asm()
    # ---------------- setup ----------------
    A.label('start')
    A.rnd(RHO); A.movi(IDN, 256); A.movi(H, 0); A.movi(C, 0); A.movi(ZERO, 0); A.not_(ONES, ZERO)
    A.movi(PTR, 0)
    A.label('clr')                                           # TAB := 0, eight words per pass
    for k in range(8): A.st(PTR, k, ZERO)
    A.addi(PTR, PTR, 8); A.jlti(PTR, S, 'clr')
    A.movi(L, 0)
    A.label('iw')                                            # for l < 256: LID[l] := l; LST[l] := 0; lane l := rho + l
    A.add(NP, RHO, L); A.st(L, LID, L); A.st(L, LST, ZERO); A.jal(LR, 'setwalk')
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
    A.label('gather')                                        # ACC := bits 0..KEYB-1 of the point of walk l (bit j = plane j, bit l):
    A.shr(ACC, 0, L); A.andi(ACC, ACC, 1)                    # only the KEYB key planes are read (the record holds nothing else)
    for j in range(1, KEYB):
        A.shr(TT, j, L); A.andi(TT, TT, 1); A.shli(TT, TT, j); A.or_(ACC, ACC, TT)
    A.label('record')                                        # REC := 1 | (end bits 0..KEYB-1) << 1; REP := REC in each of the five slots
    A.shli(REC, ACC, 1); A.addi(REC, REC, 1)
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
    A.ld(ID, L, LID); A.andi(SLOT, ID, (1 << SB) - 1); A.shri(Y, ID, SB); A.shl(X, REC, Y)
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
    A.st(L, LID, IDN); A.st(L, LST, LV); A.add(NP, RHO, IDN); A.addi(IDN, IDN, 1)
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
    A.ld(Y, L, LID); A.ld(LB, L, LST); A.sub(LB, C1, LB)     # trail b: its number and its length lb = c1 - LST[l]
    A.jgei(LB, LRC + 1, 'rfail')                             # lb > LRC: the replay refuses it
    A.add(P, RHO, X); A.add(Q, RHO, Y)
    A.mov(UU, P); A.movi(LA, 0)
    A.label('meas')                                          # la := evaluations of trail a from its start to its first DP
    A.jal(LR2, 'evalF'); A.addi(LA, LA, 1); A.jlti(FF, THR, 'measd')       # the image is a DP when FF < THR
    A.jgei(LA, LRC, 'rfail'); A.mov(UU, FF); A.jmp('meas')
    A.label('measd')
    A.jlt(LA, LB, 'advq')
    A.sub(N, LA, LB); A.mov(MM, LB)
    A.label('advp')
    A.jeqi(N, 0, 'lock'); A.mov(UU, P); A.jal(LR2, 'evalF'); A.mov(P, FF); A.subi(N, N, 1); A.jmp('advp')
    A.label('advq')
    A.sub(N, LB, LA); A.mov(MM, LA)
    A.label('advq2')
    A.jeqi(N, 0, 'lock'); A.mov(UU, Q); A.jal(LR2, 'evalF'); A.mov(Q, FF); A.subi(N, N, 1); A.jmp('advq2')
    A.label('lock')
    A.jeq(P, Q, 'rfail')
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
def enc(x):
    op, d, a, b, imm = x
    return struct.pack('<BHHHB', op, d, a, b, 0) + imm.to_bytes(24, 'little')


def dec(bs):
    out = []
    for i in range(0, len(bs), 32):
        op, d, a, b, z = struct.unpack('<BHHHB', bs[i:i + 8])
        out.append((op, d, a, b, int.from_bytes(bs[i + 8:i + 32], 'little')))
    return out


def unpack39(bs):
    """the instruction words of a packed straight-line block: instruction i is bits 39 i .. 39 i + 38 (little-endian)"""
    n = len(bs) * 8 // 39; p = bytes(bs) + bytes(6); out = []
    for i in range(n):
        o, s = divmod(39 * i, 8)
        out.append((int.from_bytes(p[o:o + 6], 'little') >> s) & (2 ** 39 - 1))
    return out


def pack39(ws):
    """instruction words (39 bits each) -> the packed bytes, the last byte padded with zero bits"""
    out = bytearray(); acc = nb = 0
    for w in ws:
        acc |= w << nb; nb += 39
        while nb >= 8: out.append(acc & 255); acc >>= 8; nb -= 8
    if nb: out.append(acc)
    return bytes(out)


def sl_bytes(prog, PFLO, PFN):
    """prog.bin + the prefilter: PF := OR of planes PFLO..PFLO+PFN-1 (PFN-1 ORs), one block of 39-bit instructions, packed"""
    ws = unpack39(prog)
    def w(code, d, a, b): return code | d << 3 | a << 15 | b << 27
    ws.append(w(2, PF, PFLO, PFLO + 1))
    for j in range(PFLO + 2, PFLO + PFN): ws.append(w(2, PF, PF, j))
    return pack39(ws)


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
    Ls[1] = u0; Ls[6] = u1; Ls[11] = u0 ^ u1 ^ KL[11]; Ls[4] = u2; Ls[9] = u3; Ls[14] = u2 ^ u3 ^ KL[14]
    return b''.join(x.to_bytes(8, 'little') for x in Ls)


def F_plain(u, KL, PD, rounds=NR):
    d = sha3_256_r(m_of(u, KL), rounds)
    pd = PD[0] | PD[1] << 64 | PD[2] << 128 | PD[3] << 192
    return int.from_bytes(d, 'little') ^ pd


# ---------------- the machine ----------------
def compile_sl(slb, nprog, hookW=None):
    """Python function executing the packed 39-bit block on a register list (the planes 0..255 and PF are the only live ends).
    hookW (test builds only): set the planes hookW..255 to zero after the first nprog instructions (the F of the program
    truncated to hookW bits, as in the organizer experiment rho-w22)."""
    src = ['def sl(R):']
    for j in range(256): src.append(' r%d=R[%d]' % (j, j))
    for i, w in enumerate(unpack39(slb)):
        if i == nprog and hookW:
            for j in range(hookW, 256): src.append(' r%d=0' % j)
        op, d, a, b = w & 7, (w >> 3) & 4095, (w >> 15) & 4095, (w >> 27) & 4095
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
    c['match_entry'] = 3 + seg('match', 'meas')                                  # trail number from the record (3), entry (9: with the lb test 2)
    c['meas_iter'] = e + 8                                                       # one measuring evaluation without the DP
    c['meas_last'] = e + 4                                                       # the evaluation that lands on the DP
    c['replay_iter'] = 13 + 2 * e                                                # one lock-step iteration (not found)
    # success after k lock-step iterations, la measured: 12 + (la - 1)(e + 8) + (e + 4) + 2 + 2 + n (7 + e) + 2 + 2
    #   + (k - 1)(13 + 2e) + (9 + 2e) + 67; exhaustion: ... + m (13 + 2e) + 3.  Largest at la = lb = k = LRC:
    #   (e + 8 + 13 + 2e) LRC + 12 - 4 + 2 + 2 + 2 + 2 - 13 + 9 + 67
    c['replay_const'] = c['match_entry'] - 4 + 2 + 2 + 2 + 2 - 13 + 9 + 67
    c['replay_max'] = (c['meas_iter'] + c['replay_iter']) * LRC + c['replay_const']
    c['setup'] = seg('start', 'clr') + (S // 8) * 11 + 1 + 256 * (7 + c['setwalk'])
    return c


def pf_bytes(PFLO, PFN):
    return sl_bytes(b'', PFLO, PFN)


def build_cli(argv):
    if len(argv) > 1 and argv[1] == 'build':
        meta = argv[2] if len(argv) > 2 else 'meta.txt'
        KL, PD = read_meta(meta)
        A = program(FULL); audit(A)
        other = b''.join(enc(x) for x in A.ins)
        open('other.bin', 'wb').write(other)
        open('pf.bin', 'wb').write(pf_bytes(FULL['PFLO'], FULL['PFN']))
        open('data.bin', 'wb').write(b''.join(w.to_bytes(32, 'little') for w in data_image(KL, PD)))
        c = counts(A, FULL)
        I = A.lab
        out = []
        out.append('other code: %d instructions x 32 bytes = %d bytes (other.bin sha256 %s)' % (len(A.ins), len(other), hashlib.sha256(other).hexdigest()))
        out.append('prefilter: %d instructions x 39 bits, packed (pf.bin sha256 %s); the straight-line block = prog.bin then pf.bin, %d instructions, sits in front of instruction %d (label loop)' %
                   (FULL['PFN'] - 1, hashlib.sha256(open('pf.bin', 'rb').read()).hexdigest(), os.path.getsize('prog.bin') * 8 // 39 + FULL['PFN'] - 1, I['loop']))
        out.append('data image: 16 words x 32 bytes = 512 bytes (data.bin sha256 %s): KW[0..6], PD, 8 output words' % hashlib.sha256(open('data.bin', 'rb').read()).hexdigest())
        out.append('memory map (words): TAB 0..%d, LID %d..%d, LST %d..%d, data %d..%d' % (FULL['S'] - 1, FULL['S'], FULL['S'] + 255, FULL['S'] + 256, FULL['S'] + 511, FULL['S'] + 512, FULL['S'] + 527))
        out.append('routine entry points (instruction index): ' + ', '.join('%s %d' % (k, I[k]) for k in ('start', 'loop', 'hit', 'dpl', 'dp1', 'gather', 'record', 'probe', 'insert', 'ins', 'match0', 'cont', 'dl', 'restart', 'setwalk', 'evalF', 'outm', 'match', 'meas', 'end')))
        for k, v in c.items(): out.append('%-18s %d' % (k, v))
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
other code: 1884 instructions x 32 bytes = 60288 bytes (other.bin sha256 784f789a0c6316a545e763885762ebc663421fec76879138af030b4d3d2a8d25)
prefilter: 15 instructions x 39 bits, packed (pf.bin sha256 972ca2f8bdd7fee3a6bf994d75a2e11c8992993e89b113ffe70df543de4a2a5e); the straight-line block = prog.bin then pf.bin, 66120 instructions, sits in front of instruction 26 (label loop)
data image: 16 words x 32 bytes = 512 bytes (data.bin sha256 9b26fdee8d7bddc59a0d3bee6fdf0dee29d0065a6f5b17c34a6d08cd3cbbffe7): KW[0..6], PD, 8 output words
memory map (words): TAB 0..18071, LID 18072..18327, LST 18328..18583, data 18584..18599
routine entry points (instruction index): start 0, loop 26, hit 28, dpl 158, dp1 160, gather 204, record 402, probe 414, insert 438, ins 445, match0 448, cont 463, dl 466, restart 467, setwalk 478, evalF 1761, outm 1791, match 1818, meas 1827, end 1884
n_instr            1884
setwalk            1283
restart            1293
restart_halt       3
hit                131
ctz_clear          44
gather             198
record_slot        12
probe_word         24
insert             7
dp_fixed           266
dp_max             433994
dl_final           1
e_eval             3281
e_outm             27
match_entry        12
meas_iter          3289
meas_last          3285
replay_iter        6575
replay_const       79
replay_max         396742764064743664068396870177292025935
setup              355097
static opcode mix: OR 415 ANDI 327 SHRI 274 AND 271 SHL 258 SHLI 64 SHR 50 ST 21 EQI 21 MOV 19 ADDI 18 XOR 18 BNZ 17 MOVI 15 LDA 15 BZ 14 NOT 12 JMP 10 JAL 9 LTI 6 HALT 5 LD 5 ADD 4 SUBI 4 EQ 3 JR 3 SUB 3 RND 1 PERM 1 LT 1
highest register named: 2190 (file of 2192)
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
prog = open('prog.bin', 'rb').read(); NPROG = len(prog) * 8 // 39
data = data_image(KL, PD)
FAILS = []; NCHK = [0]


def check(cond, msg):
    NCHK[0] += 1
    if not cond:
        FAILS.append(msg); print('FAIL', msg)


def mk(Pm, seed=1, with_sl=False):
    A = program(Pm); audit(A)
    code = dec(b''.join(enc(x) for x in A.ins))
    S = Pm['S']
    slb = sl_bytes(prog, Pm['PFLO'], Pm['PFN'])
    sl = compile_sl(slb, NPROG, Pm.get('WTEST')) if with_sl else None
    vm = VM().load(code, sl, len(slb) * 8 // 39, A.lab['loop'], S + 528, data, S + 512, random.Random(seed))
    return A, vm, len(slb) * 8 // 39


def nonsl_ops(vm):
    return sum(vm.cnt) - vm.units + vm.units * UNIT


def ops_of(vm, f):
    a = nonsl_ops(vm); f(); return nonsl_ops(vm) - a


# ------------------------------------------------------------------ 1. routine tests
def sl_test():
    """the straight line + prefilter as compiled from the packed 39-bit block: 2 x 256 points, every lane, 3 chained steps, against F_plain"""
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
    S = Pm['S']; LID, LST = S, S + 256; KB = keyb(Pm); DPL, DKK = Pm['DPLO'], Pm['DK']
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
    check(vm.M[LID + 7] == 4321 and vm.M[LST + 7] == 99 and R[IDN] == 4322, 'restart effect')
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
    check(all(vm2.M[i] == 0 for i in range(S)) and all(vm2.M[LID + i] == i and vm2.M[LST + i] == 0 for i in range(256)), 'setup effect')
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
        vm.M[LST + 255] = 700; vm.M[LID + 255] = lid
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
        check(vm.M[LID + 255] == 5000 and vm.M[LST + 255] == 778 and vm.R[IDN] == 5001, 'DP restart')
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


def replay_tests(ntrials=60):
    """the replay on pairs of trails of the 12-bit truncation of F with a 4-bit DP (planes 8..11 zero): the measuring walk,
    alignment, lock step; pairs with the same end (found / p = q) and with different ends (exhausted: a false key match)"""
    Pm = dict(S=400, U=400, SB=9, LRC=200, Tb=900, HMAX=10 ** 9, DPLO=8, DK=2, DT=3, PFLO=10, PFN=2, WTEST=12)
    THRm = thr(Pm)
    mask = (1 << 12) - 1
    Ft = lambda u: F_plain(u, KL, PD) & mask
    A, vm0, nsl = mk(Pm); I = A.lab; c = counts(A, Pm); e = c['e_eval']; END = I['end']; S = Pm['S']
    seen = {1: 0, 13: 0, 'diff': 0}
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
        keys = list(trails)
        pairs.append(tuple(random.sample(keys, 2)))
        for a, b in pairs:
            if done >= ntrials: break
            ta, tb = trails[a], trails[b]
            la, lb = len(ta) - 1, len(tb) - 1
            A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
            R[RHO] = rho; R[LR2] = END; R[L] = 9; M[S + 9] = b; R[C1] = 5000; M[S + 256 + 9] = 5000 - lb; R[X] = a
            ops = ops_of(vm, lambda: vm.run(I['match']))
            n_, m_ = abs(la - lb), min(la, lb)
            p, q = (ta[n_], tb[0]) if la >= lb else (ta[0], tb[n_])
            meas = (la - 1) * (e + 8) + (e + 4)
            base = 9 + meas + 2 + 2 + n_ * (7 + e) + 2
            check(R[LA] == la and R[LB] == lb, 'replay lengths %d %d vs %d %d' % (R[LA], R[LB], la, lb))
            if ta[-1] != tb[-1]:
                k = 0
                while k < m_ and Ft(p) != Ft(q): p, q = Ft(p), Ft(q); k += 1
                if k < m_:                       # different ends cannot merge inside the trails
                    check(False, 'different ends merged')
                check(vm.halt == 13 and ops == base + (2 if p != q else 0) + (m_ * (13 + 2 * e) + 3 if p != q else 1) - (0 if p != q else 0), 'replay different ends ops %d (halt %s)' % (ops, vm.halt))
                seen['diff'] += 1
            elif p == q:
                check(vm.halt == 13 and ops == base + 2 + 1, 'replay p=q ops %d halt %s' % (ops, vm.halt)); seen[13] += 1
            else:
                k = 1
                while Ft(p) != Ft(q): p, q = Ft(p), Ft(q); k += 1
                check(vm.halt == 1, 'replay expected halt 1, got %s (la %d lb %d)' % (vm.halt, la, lb))
                pred = base + 2 + (k - 1) * (13 + 2 * e) + (9 + 2 * e) + 67
                check(ops == pred and vm.cnt[I['lloop']] == k, 'replay found ops %d vs %d (k %d)' % (ops, pred, k))
                out = M[S + 520:S + 528]
                ma = b''.join(out[x].to_bytes(32, 'little') for x in range(4)); mb = b''.join(out[4 + x].to_bytes(32, 'little') for x in range(4))
                check(ma != mb and (int.from_bytes(sha3_256_r(ma, NR), 'little') & mask) == (int.from_bytes(sha3_256_r(mb, NR), 'little') & mask), 'replay pair')
                seen[1] += 1
            check(ops <= c['replay_max'], 'replay bound')
            done += 1
    # a stored trail without a DP within LRC (checks the guard): halt 13
    A, vm, nsl = mk(dict(Pm, LRC=1)); R = vm.R; M = vm.M
    c1 = counts(A, dict(Pm, LRC=1))
    for a in range(256, 400):
        if Ft((5 + a) & M256) >= THRm:
            R[RHO] = 5; R[LR2] = END; R[L] = 9; M[S + 9] = 300; R[C1] = 10; M[S + 256 + 9] = 9; R[X] = a
            vm.run(A.lab['match']); check(vm.halt == 13 and R[LA] == 1, 'measure guard'); break
    # the length guard of the new trail: lb = LRC + 1 is refused at once (6 operations), lb = LRC goes on
    for lbv, want in ((Pm['LRC'] + 1, 13), (Pm['LRC'], None)):
        A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
        R[RHO] = 5; R[LR2] = A.lab['end']; R[L] = 9; M[S + 9] = 300; R[C1] = 10 ** 6; M[S + 256 + 9] = 10 ** 6 - lbv; R[X] = 256
        n = ops_of(vm, lambda: vm.run(A.lab['match'], stop=A.lab['meas'] if want is None else None))
        check((vm.halt == 13 and n == 6) if want else (vm.halt is None and R[LB] == lbv), 'lb guard %d' % lbv)
    print('replay tests: found %d, p=q %d, different ends %d' % (seen[1], seen[13], seen['diff']))


# ------------------------------------------------------------------ 2. end-to-end
def check_pair(vm, Pm, W):
    S = Pm['S']; out = vm.M[S + 520:S + 528]
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
            # exact replay formula for the observed lengths
            la, lb, k = vm.R[LA], vm.R[LB], cnt[I['lloop']]
            n_, m_ = abs(la - lb), min(la, lb)
            e = c['e_eval']
            if vm.halt == 1:
                # the 3 instructions that take the trail number from the record lie before evalF (counted with the DP walk)
                pred = 9 + (la - 1) * (e + 8) + (e + 4) + 2 + 2 + n_ * (7 + e) + 2 + 2 + (k - 1) * (13 + 2 * e) + (9 + 2 * e) + 67
                check(replay_ops == pred, '%s seed %d: replay ops %d vs %d (la %d lb %d k %d)' % (name, sd, replay_ops, pred, la, lb, k))
            check(replay_ops <= (c['meas_iter'] + c['replay_iter']) * max(la, lb) + c['replay_const'], 'replay bound')
        print('%-10s seed %3d halt %2s steps %5d hits %5d dp %4d restarts %4d tb %4d replay_ops %7d  total %d' %
              (name, sd, vm.halt, steps, hits, dps, rest, dl, replay_ops, nonsl + steps * nsl))
        if expect is not None: check(vm.halt in expect, '%s seed %d: halt %s not in %s' % (name, sd, vm.halt, expect))
    return res


def main():
    ns = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    routine_tests()
    replay_tests()
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
replay tests: found 45, p=q 0, different ends 15
routine tests done, failures so far: 0
base       seed   1 halt  1 steps   156 hits   156 dp  125 restarts  124 tb    0 replay_ops  822345  total 20593695
base       seed   2 halt  1 steps    78 hits    78 dp   67 restarts   66 tb    0 replay_ops  440836  total 10792806
w32cap     seed   1 halt 13 steps   756 hits   742 dp  101 restarts  100 tb    0 replay_ops       6  total 57688420
w32cap     seed   2 halt 13 steps   753 hits   738 dp  132 restarts  131 tb    0 replay_ops       6  total 59769097
smalltab   seed   1 halt  1 steps   156 hits   156 dp  125 restarts  124 tb    0 replay_ops  822345  total 12852520
smalltab   seed   2 halt  1 steps    78 hits    78 dp   67 restarts   66 tb    0 replay_ops  440836  total 6670831
abort      seed   1 halt 10 steps     4 hits     4 dp    4 restarts    4 tb    0 replay_ops       0  total 893070
abort      seed   2 halt 10 steps     4 hits     4 dp    2 restarts    2 tb    0 replay_ops       0  total 745978
tb5        seed   1 halt 12 steps     5 hits     5 dp    5 restarts    5 tb    1 replay_ops       0  total 1032767
tb5        seed   2 halt 12 steps     5 hits     5 dp    7 restarts    7 tb    1 replay_ops       0  total 1179879
u264       seed   1 halt 11 steps    10 hits    10 dp    9 restarts    8 tb    0 replay_ops       0  total 1061587
u264       seed   2 halt 11 steps     7 hits     7 dp    9 restarts    8 tb    0 replay_ops       0  total 863206
packed     seed   1 halt  1 steps   156 hits   156 dp  136 restarts  135 tb    0 replay_ops  822345  total 12534338
packed     seed   2 halt  1 steps    78 hits    78 dp   69 restarts   68 tb    0 replay_ops  440836  total 6470983
nocmp      seed   1 halt  1 steps   155 hits   155 dp  164 restarts  163 tb    0 replay_ops  822345  total 23394943
nocmp      seed   2 halt  1 steps    77 hits    77 dp   88 restarts   87 tb    0 replay_ops  440836  total 12270698
checks run: 444, failures: 0
```
