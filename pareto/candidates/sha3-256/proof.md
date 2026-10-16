# SHA3-256 with 8 prefix rounds: distinguished-point collision search with a linear-structure message embedding and a 42,482-operation bit-sliced step, time_log2 124.34902

## 1. Claim

Target `sha3-256-r8-prefix-v1`. This is SHA3-256 (FIPS 202) with Keccak-f rounds 0 to 7 in the single permutation call, zero initial state, rate 136 bytes, suffix 0x06 with pad10*1, and the full 256-bit digest. The algorithm outputs two distinct 128-byte one-block messages with equal complete digests (an ordinary collision).

| Quantity | Value |
|---|---|
| time_log2 (collision-frontier-v5, unit 2168 word operations, rounded up) | 124.34902 (Sections 4 and 5, certificate in Appendix A) |
| memory | at most 999,903 bytes <= 2^20 (margin 48,673 bytes), memory_log2_bytes = 20 (Section 6) |
| score S = time_log2 + max(0, memory_log2 - 20) | 124.34902 |
| success probability | at least 0.39 for one attempt, under the premise H_rand (Section 5) |
| preprocessing | the constant-selection run `gen 512` (512 constant sets, the best rebuilt), charged 513 x 2^32 + 512 x 2^10 + 2^12 operations (the 2^12 is the data step, Section 3.6); preprocessing_log2 = 30 (Section 3.6); no advice |

The method is a generic distinguished-point search (van Oorschot-Wiener) on a chain function F with 256 walks per step. It is the method of our earlier entry 2d74a370 (sha3-256-r6), with the same table, restart rule, deadlines, replay and success bound, and this package is the eight-round port of our seven-round package f4f7b40e of the same design (Section 11). Two things are new relative to 2d74a370.

1. **The message embedding.** The 256-bit point is placed in six message lanes so that round 0 of the permutation and the theta step of round 1 are linear in the point. This is a one-round linear structure in the sense of Guo, Liu and Song (2016). With constants folded, those steps cost a few hundred word operations instead of several thousand.
2. **The step program.** It is a bit-sliced straight line of 42,482 register operations, built by a generator written for this entry (Appendix B). It follows the step design of jungjipdo's entry 67f781f8: theta evaluated lazily per chi row, a per-row complement subset, dead-code elimination, last-use register allocation, the digest written in place of the input, and a declared register file. We read 67f781f8's text as a description and wrote everything here ourselves; none of its code is used.

Three declarations are made in claim.json. H_rand (Section 5) is the score-critical premise on the function. H_reg (register file) and H_code (code-memory encoding) are machine conventions of the cost model, role supporting, in Section 3.5. Both conventions move the score, and Section 8 prices each one.

## 2. The function F and the encoding

Let u be a 256-bit point with little-endian 64-bit lanes u0, u1, u2, u3. The message m(u) has 128 bytes, the 16 lanes 0 to 15 of the absorbed state (lane index x + 5y):

- lane 1 = u0, lane 6 = u1, lane 11 = u0 xor u1 xor K11 (column x = 1, rows y = 0, 1, 2);
- lane 4 = u2, lane 9 = u3, lane 14 = u2 xor u3 xor K14 (column x = 4, rows y = 0, 1, 2);
- every other lane l in 0..15 holds the constant K_l (the table below).

With the SHA3 padding, byte 128 is 0x06 and byte 135 is 0x80. So the message is one absorbed block, lane 16 = 0x8000000000000006, and lanes 17 to 24 are zero. Rounds 0 to 7 are applied, and the digest is lanes 0 to 3 of the result (32 bytes). Define

    F(u) = SHA3-256-r8(m(u)) xor PD

where PD is a fixed 256-bit mask (the polarity of the program's digest planes, below). The map u -> m(u) is injective (lanes 1, 6, 4, 9 are u). Hence F(a) = F(b) with a != b gives two distinct messages m(a), m(b) with equal complete digests. XOR with a fixed mask is a bijection of the range, so F is a fixed function from 256 bits to 256 bits like the plain digest map.

Constants (hexadecimal, lane: value). They were chosen by the generator as trial 192 of 512 pseudo-random constant sets, the one with the fewest operations:

```
K0  c9a9d386ab38e13a  K2  9be65c0f48819e78  K3  a42df10543300344  K5  9d9a486de15a3242
K7  62628f16871056a6  K8  8d7196f55bc91f8b  K10 793ea2677e200f74  K11 7e8d7d4cce830045
K12 fe58db5a1de5126a  K13 1b571a79774b02ce  K14 8a2d82f8f9dcb705  K15 f01a6a80f9aae74b
PD (lanes 0..3) 24f656c2fa1ed933 6904c91114984100 0208100054184301 4208393c51796705
```

**Why round 0 is linear.**
- *Theta of round 0.* The column sums of columns 1 and 4 are constants: u0 xor u1 xor (u0 xor u1 xor K11) xor lane 16 xor lane 21 = K11 xor 0x8000000000000006, and u2 xor u3 xor (u2 xor u3 xor K14) xor lane 19 xor lane 24 = K14. So theta adds only constants to every lane.
- *Chi of round 0.* After rho and pi, the six message lanes land in positions where no two are adjacent inside a chi row. Each product of chi has at least one constant factor, so chi of round 0 is affine in u.
- *Round 1 theta.* It is a linear map of affine values, so it is affine too.

The generator tracks each value as a GF(2) affine form in the 256 input bits as long as it is affine. It emits an operation only when the form is new, so it reuses a form computed once. It stops tracking forms at the first nonlinear operation (chi of round 1). This choice is credited to Guo-Liu-Song's linear structures. The search uses no algebraic property: F is only evaluated.

## 3. One step of 256 walks: the straight line

### 3.1 Planes, polarity, gates

A batch is 256 walks. Plane (lane, z) is one 256-bit word whose bit t is bit z of that lane for walk t. Rotations of rho and the moves of pi rename planes and cost nothing.

Each value is held as a register and a polarity p: the logical value is the register word xor p, all-ones or zero. NOT and XOR with a constant flip p for free. Constant values are folded and never stored.

The operations, each one word operation, are:
- XOR: one operation;
- logical a AND b: one AND when both polarities are 0, one OR with output polarity 1 when both are 1, and two operations (A xor (A and B)) otherwise;
- NOT: one operation, used only for the row complements of 3.2.

Equal operands fold. A binary operation on the same pair of registers is emitted once (hash-consing).

### 3.2 Rounds

For each round r = 0..7 with the round constant of the profile:

1. Column sums C[x][z] (the five planes of the column, folded) and D[x][z] = C[x-1][z] xor C[x+1][z-1]. These are computed slice by slice, with C[.][63] first, so that few C values are live at once.
2. The chi rows, in order Y = 0..4 and z = 0..63. Each row XORs D into its five inputs b[X] = A[x][y][z - rho(x,y)] xor D[x][z - rho(x,y)] (x = 3Y + X mod 5, y = X) only when the row is computed (lazy theta).
3. **Row complement subset.** Before chi, the generator may NOT some of the five inputs. Over the 32 subsets it takes the first one that minimises NOTs plus the number of chi terms that need two operations. In a five-cycle the number of equal adjacent polarities is odd, so at least one extra operation per row remains.
4. chi: out[X] = b[X] xor ((not b[X+1]) and b[X+2]). iota flips the polarity of the lane-0 planes where the round constant has a 1.

**Round 7** computes only row Y = 0 and the outputs X = 0..3 (the digest lanes).

**Dead-code elimination** then removes every operation that no digest plane depends on.

### 3.3 Chain feed

Digest plane j is written into register j, which held input plane j. The physical digest word is the next point: F folds the digest polarity PD into the function (Section 2). There is no copy and no NOT between steps.

### 3.4 The ledger of one step

Printed by the generator (`gen 512`, Appendix B):

| operation | count |
|---|---:|
| XOR | 31,201 |
| AND | 5,917 |
| OR | 3,939 |
| NOT | 1,425 |
| load / store | 0 / 0 |
| **total** | **42,482** |

That is 165.95 word operations per evaluation of F, 0.0765 of the reference cost 2168 per evaluation.

The linear part is round 0 plus the theta of round 1, with 1,709 distinct affine forms tracked. A generic round of this program costs about 7,000 operations (the eighth round adds 6,965 to the 35,517 of the seven-round program of Section 11).

### 3.5 Registers and code encoding (machine conventions H_reg and H_code)

**Registers.** The values are allocated to registers in program order. A register is freed at the last use of its value. Input and digest plane j use register j; the allocator never gives register j < 256 to a value that would still be live when digest plane j is written. The program uses registers 0 to 2,180 (2,181 registers, at most 1,925 values live at once; the same as at six and seven rounds). The search keeps its own state in registers 2,181 to 2,190 (the step counter, the next deadline, the next trail number, rho, the hit counter, the all-ones word, the prefilter word, two return addresses and a zero word); register 2,191 is spare. The handlers of Section 4.3 also use registers 256 to 2,180 as temporaries: their contents are dead between two steps, because every straight-line value is defined before it is used and only the planes 0 to 255 are carried from one step to the next (the compiled straight line of Appendix D raises an error on a read before a write). The step has no loads or stores.

**H_reg (declared machine convention, role supporting in claim.json).** The cost model and the target profile fix no register count. This package uses the 256-bit word RAM of collision-frontier-v5 with a declared file of 2,192 registers of 256 bits. An operation on register operands costs one word operation, with no load or store. All transfers are charged as stated: the step has no loads or stores, and every load and store of the other code is a charged word operation in Section 4. The file's 70,144 bytes are counted as memory (Section 6). This is the same convention as 67f781f8 (a declared file of 2,304 registers), which is credited in Section 9 (it is on another challenge, so it is not a declared dependency), and as our blake3 entry 0a9640ed. Section 8 states what is priced for these alternatives: for round 8 they are not computed.

**H_code (declared code-memory charging convention, role supporting in claim.json).** The cost model and the target profile fix no code encoding.
- **Encoding.** Each straight-line instruction has only register operands and no immediate. It is stored in 5 bytes: a 3-bit opcode (0 XOR, 1 AND, 2 OR, 3 NOT) and three 12-bit register numbers (destination, a, b), 39 bits in little-endian order. The memory table charges the straight line at 5 bytes per instruction (Section 6).
- **Other code.** All other code (setup, loop control, hit handler, DP handler, restart, deadline scan, replay, output) is real code of one machine, written out in Appendix D and assembled: 2,656 instructions of 32 bytes (84,992 bytes), measured from the assembled file. An instruction has an opcode byte, three 16-bit register numbers and a 192-bit immediate. Each costs one word operation, except PERM, which applies the selected-round permutation to the 1,600-bit state held in seven registers and costs one unit (2168 operations), the cost model's own price of a sponge permutation. The ordinary instructions are the model's primitives: register-register and register-immediate XOR, AND, NOT, addition, subtraction, shifts by an immediate or by a register, a compare that writes 0 or 1, a conditional branch on that register (always the instruction right after its compare, audited by the assembler), jumps, load and store with address register plus immediate, and the random word. The immediate is part of the 32-byte instruction and has no operation of its own. This is a declared convention under H_code, as the 5-byte encoding is.
- **Time ledger.** Each straight-line instruction is charged as the one word operation it performs (Sections 3.4 and 4.1). The ledger has no separate line for fetching or decoding instructions.
- **Sensitivity.** Section 8: the 32-byte-per-instruction straight line is not computed for round 8.

Both conventions move the score (Section 8). The role "supporting" in claim.json is the role of a declared convention and is not a statement that the premise is small. The checks of Section 3.7 and the organizer experiments validate the function of the program, decoded from its 5-byte encoding in software, with this allocation. They do not measure the cost of register access or of instruction execution, and no claim rests on such a measurement.

The program file is 212,410 bytes. Its SHA-256 is 1b12fba20713a805309b07eb3f563770745b1dc44b85086c7e4f26bb3170be69.

### 3.6 Generation and constant selection (preprocessing)

The preprocessing is one run of the selection program `gen 512` (Appendix B), a freestanding C program without libc. For each of 512 constant sets (trial 0: all constants zero; trial t > 0: xorshift constants from seed t) it builds the straight line (about 42,700 symbolic nodes, the row subset search, dead-code elimination) and counts its operations. It keeps the trial with the fewest operations (trial 192, 42,482; trial 0 gives 42,684), rebuilds it, allocates the registers and writes prog.bin, meta.txt and ledger.txt. `gen 1 192` writes the identical file (checked byte for byte). The attack runs `gen 512`, and that run is charged.

- **Time.** The run of 512 trial builds and one rebuild took 1.3 to 1.5 s of user time on one core of an AMD Ryzen 9 7900X (at most 5.6 GHz): at most 8.4 x 10^9 cycles and, at most 8 retired instructions per cycle, below 2^36 machine instructions. The ledger charges each of the 513 builds 2^32 word operations, and each trial a further 2^10 for its constants, the sum of the four counts, the comparison, the update of the best and its printed line, and the data step (`other8.py build`, Appendix D) a further 2^12 for reading the 16 numbers of meta.txt and writing the 16-word data image data.bin (the lane constants of the absorbed state and PD, Section 4.2): PRE = 513 x 2^32 + 512 x 2^10 + 2^12 = 2,203,318,751,232 word operations, part of N (Section 4.4). Since 2^29 < PRE / 2168 <= 2^30, preprocessing_log2 is declared as 30.
- **Memory.** The program is static and freestanding, and all its arrays are static (Appendix B, `MAXN = 45312`, `MAXF = 4096`). Measured with `size`: text 17,985 bytes, data 4 bytes and BSS 736,736 bytes, an image of 754,725 bytes.
  - `gen 512` was run under `nice -n 10 prlimit --as=1048576 --stack=16384`: an address-space limit of 2^20 bytes and a 16,384-byte stack. It completes, five times out of five, with prog.bin (SHA-256 1b12fba2... as above), meta.txt, the 512 trial lines and the ledger identical in every run. The array sizes `MAXN` and `MAXF` only bound the node store and the table of linear forms; the program stops with a message if either is exceeded, and no trial of the 512 does. `gen 1 192` writes the identical prog.bin and meta.txt.
  - The smallest address-space limit under which `gen 512` completes with identical output is 901,120 bytes (binary search in 4,096-byte steps).
  - The peak resident memory, measured by the program itself from /proc/self/status VmHWM, is at most 618,496 bytes (five runs of the final build, 596 to 604 KiB). The work runs in a forked child; getrusage of that child, read by the parent through wait4, gives 540,672 bytes.

### 3.7 Correctness of the step (checked by execution)

- `selftest` (our C program) executes the program file, decoded from its 5-byte encoding, on 4 x 256 uniform points for four chained steps each. It compares every output with F computed by a plain lane-wise eight-round implementation. Result: 4,096 chained evaluations (4 batches of 256 points, four chained steps; run twice with different seeds), 0 mismatches.
- That reference matches hashlib.sha3_256 at 24 rounds on 300 messages of lengths 0 to 299, and the organizer's verifier/keccak.py sha3_256(m, rounds=8) on the same messages: 0 mismatches.
- The experiment program regenerates the same straight line in Python and refuses to run unless its encoding hashes to the SHA-256 above. Before its trials it checks two chained full-width steps against the plain implementation.
- The organizer experiments then recompute every returned pair with the trusted digest (Section 7).

## 4. The search

Parameters:
- L = 256 walks.
- Distinguished point (DP): the planes 142 to 255 of F are zero (H = 114 bits, theta = 2^-114).
- Trail cap Lc = 17 x 2^114 steps.
- U = 19,000: the limit on trails started in one attempt, and the number of table words S.
- Tb = 1,344,270,650,860,686,671,361,005,282,410,889,216 = 67,868,324 x 2^94 = 1.01131684 x 2^120 steps of 256 walks per attempt.
- HMAX = floor(Tb (1 + 2^-20) / 2^8) + 1 + Lc = 358,327,248,618,091,250,208,476,601,149,030,401: the cap on prefilter hits. The attempt aborts at hit HMAX + 1.

State:
- in registers: the 256 input planes (registers 0 to 255); the step counter c (the number of steps completed before the current step), the next deadline nxt, the next trail number idn, rho, the hit counter h, the all-ones word, the prefilter word and the return addresses (registers 2,181 to 2,190);
- in memory (word addressed): the table TAB of S words; LID[l] and LST[l] for each walk l (its trail number, and the number of the first step of its trail); a data image of 16 words: the 7 words of lane constants of the absorbed state (K, with the lanes of u zero), PD, and 8 words for the output pair.

A table word holds a record:
- bits 0 to 121: bits 0 to 121 of the trail's end (122 of the 142 bits a DP leaves free);
- bits 122 to 136: the trail number (15 bits);
- bits 137 to 255: the length (119 bits; Lc < 2^119).

A record is nonzero; an empty slot is zero.

```
setup: rho := random word; idn := 256; h := 0; c := 0; TAB := 0; for l < 256: LID[l] := l; LST[l] := 0; lane l of the input planes := rho + l
       nxt := min(Tb, Lc) = Lc
loop:
  the straight line (42,482): the input planes become F of the 256 walks
  pf := OR of the 16 planes 240..255 (15 ORs)
  if pf != all-ones (compare, branch):          -- some walk has planes 240..255 zero (probability 2^-16 each)
      h += 1; if h > HMAX: halt, the attempt failed   -- hit counter and abort (F5)
      dp := complement of (pf OR (OR of the planes 142..239))      -- the walks at a DP; c1 := c + 1 = steps completed including this one
      while dp != 0: l := the lowest set bit of dp; clear it;
          point := the 256-bit value with bit j = bit l of plane j
          record := (bits 0..121 of the point) | LID[l] << 122 | (c1 - LST[l]) << 137
          probe TAB from slot (low 15 bits of the point, minus S if >= S), linear probing, wrap at S:
             empty slot: store the record; restart(l, c1)
             a record with the same 122 end bits (its trail number is another one): REPLAY(that record, this record);
                if it returns a != b, output m(a), m(b) and stop; otherwise halt, the attempt failed
  c += 1; if c != nxt goto loop
  if c = Tb: halt, the attempt failed
  m := Tb; for each walk l = 0..255: if c - LST[l] = Lc: restart(l, c);  m := min(m, LST[l] + Lc)     -- no DP within Lc steps
  nxt := m; goto loop
restart(l, s): if idn = U: halt, the attempt failed
               LID[l] := idn; LST[l] := s; lane l of the input planes := rho + idn; idn += 1
REPLAY(trail a of length la, trail b of length lb, the same end):
  p := rho + a, q := rho + b; the longer trail is advanced by |la - lb| evaluations of F
  if p = q return nothing; repeat min(la, lb) times: if F(p) = F(q) return (p, q); p := F(p); q := F(q)
  return nothing
```

A DP walk's trail has at most Lc evaluations: a trail is cut when c - LST[l] = Lc, after the DP test of that same step. The trail of a restart made inside step c (a DP) starts at step c + 1, hence LST[l] := c1 and the length c1' - LST[l] at its own DP. The deadline nxt may be earlier than the earliest real deadline (a DP restart moves a walk's deadline later without recomputing nxt); the scan at nxt then finds nothing to cut and moves nxt on.

### 4.1 One iteration of the loop

An iteration costs:
- the straight line, 42,482;
- the prefilter, 15;
- its test, 2;
- the counter, 3 (add, compare, branch).

**BSTEP = 42,502 operations.** These are the instructions at the labels `loop` (compare, branch) and `cont` (add, compare, branch) of Appendix D, around the straight-line block. No other operation runs in an iteration without a prefilter hit or a deadline.

### 4.2 The replay

The replay evaluates F on one point at a time with the permutation of the selected rounds, which is one unit (2168 operations) per call. The routine `evalF` (Appendix D, 30 instructions) loads the 7 words of lane constants, places the four 64-bit limbs of the point in the lanes 1, 6, 4, 9 and, XORed in pairs, 11 and 14 (19 operations), calls PERM, loads PD and XORs it into the first state word (the digest lanes). One evaluation, with its return, costs **e = 26 + 2168 + 2 + 1 = 2,197** operations.

The costs, counted from the emitted code:
- an advance step (one evaluation of one trail) costs e + 7 (loop test 2, move, call, move, decrement, jump);
- a lock-step iteration costs 2e + 13 (loop test 2, two moves and two calls 4, two evaluations, a move 1, the equality test of two words 2, two moves 2, decrement and jump 2);
- the entry (decoding the two records, rho + a and rho + b, the comparison of the lengths) costs 9, the alignment 4, the test p = q 2, the success exit 67 (two message builds of 27 with their calls and moves, 8 stores, the halt).

With both lengths at most Lc, the replay costs at most (e + 7)(max - min) + (2e + 13) min + 78, at most **(2e + 13) Lc + 78 = 4,407 Lc + 78** (largest for equal lengths Lc with the pair found at the last iteration). At most one replay runs per attempt: the attempt stops after it, with the pair or (if the replay returns nothing, an event inside F4) with failure. The tests of Section 7.3 compare the executed count of the replay with this formula on 31 constructed pairs of trails, exactly.

### 4.3 Rare operations

Our first filing of this port (a286eaf9) was ruled not evaluable on the reason H_othercode_bound, because the 4,096-instruction bound for the other code and the 704,000-operation setup allowance were asserted and not backed by code; every routine below is now real code of the machine of Section 3.5 (Appendix D: assembler, 2,656 instructions, interpreter), its size is the measured 84,992 bytes, its counts are read from the lengths of the emitted code, and the tests of Section 7.3 execute each routine and compare its executed operations with its count.

The counts, each for the longest path (`other8.py build` prints them, Appendix D.2):

| routine | operations |
|---|---:|
| a prefilter hit (counter 3: add, compare, branch; OR of the planes 142..239, 97; combine and complement 2; c1, 1; test of the DP mask 2) | **105** |
| one DP walk, without its restart: DP-mask test 2, lowest set bit and clearing 44 (2 + eight stages of at most 5 + 2), gather of the point 1,022 (2 + 255 x 4), record and slot 12, probe 10 per occupied slot passed (load 1, empty test 2, xor and mask 2, match test 2, increment and wrap test 3), wrap 2, empty slot 3, store, move, call, jump 4 | 1,089 + 10 (S - 1) = **191,079** |
| restart(l, s) with its return: cap check 2, two stores, add, increment 4, the insertion of the new point into lane l (3 + 1,279: 5 per plane, 4 for plane 0) and the return | **1,289** (3 more for a restart made by the deadline scan: move, call, move); the call that halts at idn = U: 3 |
| one deadline event (c = nxt): test of c = Tb 2, nxt start 2, 256 walks at 11 each (load, subtract, test 2; add, compare, branch, move; loop 3), end 2 | **2,822**; the event c = Tb: 3 |
| setup: 7 + 11 S/8 (clearing TAB, eight words per pass) + 1 + 256 x 1,290 (the 256 starts, each 7 + the 1,283 of the insertion) + 1 | **356,374** |
| final output (two message builds, 8 stores) | inside the replay constant 78 |

The numbers of events. The hit counter caps the prefilter hits: at most HMAX + 1 are processed in every execution, and the ledger charges that number. The counter idn goes from 256 to U, one per completed restart, so at most U - 256 restarts complete; each DP walk except the last is followed by a completed restart, so at most U - 255 DP walks are processed (the last stores its record and halts at idn = U, or starts the replay, which is counted in 4.2). A probe passes at most S - 1 occupied slots, since at most U - 255 < S records are ever stored. Deadline events fall at distinct step numbers, each a start step plus Lc, and there are at most U - 255 start steps (the setup and one per completed restart) plus the event c = Tb: at most U - 254.

R = (HMAX + 1) x 105 + (U - 255) x 191,079 + (U - 256) x 1,292 + 3 + (U - 254) x 2,822 + 3 + 356,374 = 37,624,361,104,899,581,271,890,043,124,307,442,905.

The terms other than the hits add up to about 3.7 x 10^9 operations, below 2^-100 of N: only the hit term, (HMAX + 1) x 105, matters.

### 4.4 Total

N = Tb x 42,502 + ((2 e + 13) Lc + 78) + R + PRE = **58,727,822,317,364,087,491,864,841,576,310,601,141,543** word operations (Appendix A).

| part | operations | share |
|---|---:|---:|
| main loop, Tb x 42,502 | 57,134,191,202,880,904,906,185,446,513,027,613,458,432 | 0.97286 |
| replay, (2 e + 13) Lc + 78 | 1,556,006,753,378,283,004,407,505,017,955,361,488,974 | 0.02650 |
| rare operations R | 37,624,361,104,899,581,271,890,043,124,307,442,905 | 6.41e-04 |
| selection run `gen 512` and the data step (preprocessing), PRE | 2,203,318,751,232 | 4e-29 |

time_log2 = log2(N / 2168) rounded up at the fifth decimal = **124.34902**, checked in exact integer arithmetic:

    2168^100000 * 2^12434901 < N^100000 <= 2168^100000 * 2^12434902

## 5. Success probability and the premise H_rand

This section is the analysis of 2d74a370 (Section 6 there) with the parameters of Section 4, plus the abort term F5.

**Premise H_rand (an assumption, not proved): over the algorithm's coins, the program run on the fixed SHA3-256-r8 target succeeds with probability at least the probability computed below for a uniformly random function F.** The target is fixed: F of Section 2, with its fixed constants K and PD, is one deterministic function, and the only randomness of the algorithm is the random word rho. Nothing below proves, for the fixed target, that the success probability over rho is the random-function value: that transfer is the premise, and it is the one score-critical premise of this package. Four fields in claim.json: statement, as above; role, score-critical; scope, the fixed function F of Section 2 on the points of one attempt; limitations, an assumption with no proof known to us, see Section 10. Everything in the rest of this section is computed in the random-function model M: F is a uniformly random function from 256 bits to 256 bits (the values of F at distinct inputs are independent and uniform) and rho is uniform and independent of F. In M the following hold:

- (i) the first coincidence of images among e evaluations has probability 1 - prod_{k<e}(1 - k/n) >= 1 - exp(-e(e-1)/(2n)) =: G(e), where n = 2^256;
- (ii) the point reached just after a coincidence is uniform, so the number l of further evaluations of a trail until its DP satisfies P(l >= j) = (1 - theta)^j, independently of when the coincidence happened;
- (iii) **adaptivity, a property of M and not a claim about the fixed target**: the program chooses its next inputs, and which trails restart, are cut or abort, from earlier outputs of F. In M, F is realised by lazy sampling: a fresh evaluation draws a new independent uniform value, so for every fresh evaluation, given the whole history of the run, the output equals one given earlier output with probability 2^-256 by construction. For the fixed target no such statement is made: given rho and the target the whole run is deterministic, and a fresh evaluation then coincides with probability 0 or 1. What is assumed for the fixed target is only the transfer premise H_rand above.

**Where (iii) is used (in M), and what is not used.** The bound below uses no fixed-size birthday product over a random set of evaluations on finished trails, and no conditioning on which trails finish. The first coincidence is a stopping time over ALL evaluations in their execution order (step by step, walk by walk); the number of evaluations before the stop is the deterministic schedule. Under (i) and (iii) in M, when k earlier images are distinct, the next fresh evaluation coincides with an earlier image with conditional probability exactly k/n given the whole history, whatever inputs the adaptive program chose; so the probability of no coincidence among e evaluations is prod_{k<e}(1 - k/n) exactly, and G(e) of (i) is the probability that the first e fresh evaluations contain a coincidence. The same device, with conditional probability at most 2^-8 per step, is the F5 argument below. Sensitivity: a hazard (1 - eps)/n instead of 1/n costs the same as a deficit eps of the coincidence rate, 0.0073 bit for eps = 0.01.

**The coincidence.** Evaluations are numbered step by step and, inside a step, by walk. Let e* be the first evaluation whose image equals an earlier image, at step b* = ceil(e*/256). The trail B of that evaluation and the earlier trail A have equal points from then on, and both end at the same DP after l further evaluations of B. B is recorded at step b* + l at the latest. A reached the same point no later, so A was recorded before, or in the same step in a lower walk; the later record finds the earlier one.

The search succeeds if all of these hold:
- (a) b* + l <= Tb;
- (b) both trails have at most Lc evaluations;
- (c) fewer than U trails are started;
- (d) the coincidence is between two different trails;
- (e) the 122 stored end bits are those of the real ends, and the replay finds the merge.

Split l into bins of w = 2^102 steps: bin j holds l in [(j - 1) w, j w - 1], for j = 1 .. Lc / w = 17 x 2^12, with probability p_j = (1 - theta)^((j-1) w) - (1 - theta)^(j w). If l is in bin j, (a) holds when e* <= 256 (Tb - j w). By (ii),

    Pr[(a)] >= sum_j p_j G(256 (Tb - j w)).

The failure events that the sum does not cover:

- **F1**, some trail of the attempt has no DP within Lc steps: at most U (1 - theta)^Lc <= U e^-17 = 7.866e-04. This covers (b).
- **F2**, more than U - 256 restarts after a DP. A stated fact, proved here, not a heuristic. Realise the random function by lazy sampling with independent uniform values V_1, ..., V_(256 Tb), one per evaluation index in execution order (step by step, walk by walk): the t-th evaluation returns V_t if its input is fresh and the stored value otherwise. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(2^-114) variables by construction, for every t, fresh or not, so N1 = xi_1 + ... + xi_(256 Tb) is exactly binomial with mean mu = 256 Tb theta = 16,569.4 (one line: the V_t are independent and uniform and xi_t is a function of V_t alone). A DP output at a fresh input is a position with xi_t = 1. A DP output at a repeated input never causes a restart: the value is the stored output of the first evaluation of that input, whose trail ended there and was recorded (trail numbers are never reused, so the record carries a different number), and the probe finds that record, so the attempt goes to REPLAY and stops. Hence the restarts after a DP are at most N1, whatever the walks do after they coalesce: the repeated inputs and their correlated DP indicators are not counted by N1 and end the attempt at their first DP. With the cap restarts in F1, the halt at idn = U needs N1 >= U - 255, and the Chernoff bound e^-mu (e mu / (U - 256))^(U - 256) >= P(N1 >= U - 256) gives 3.7e-60. This covers (c).
- **F3**, the coincidence lies inside one trail: at most U 2^(2H) / n = 7.078e-05. This covers (d).
- **F4**, 2^-90. This covers (e). It includes:
  - a start rho + i equal to a point of another trail (U starts, about 2^128 images: below 2^-113);
  - two different ends with the same 122 stored bits (below U^2 2^-123 < 2^-94).
- **F5**, the hit counter aborts the attempt before it stops: below 2^-1000. Call a walk's input at a step fresh if F was not evaluated at it before in the attempt, and let X' count the steps at which some walk with a fresh input lands on planes 240..255 zero. Given the past, the images of the fresh inputs are independent and uniform (in M), so each step adds to X' with conditional probability at most 1 - (1 - 2^-16)^256 < 2^-8. A hit not counted in X' needs a walk at a repeated input. Outside F4 no start is a point of a trail, so repeated inputs occur only after the first image coincidence (step b*), and a successful attempt outside F1 stops at step b* + l with l <= Lc. On success, therefore, h <= X' + Lc, and an abort needs X' >= floor(Tb (1 + d) 2^-8) + 2 > (1 + d) mu, with d = 2^-20 and mu = Tb 2^-8. The Chernoff bound for indicators with conditional probabilities at most 2^-8 (supermartingale exp(s X'_t - (e^s - 1) t 2^-8)) gives probability at most exp(-d^2 mu / (2 + d)) = exp(-2.39 x 10^21) < 2^-1000. cert.py checks the exponent in exact rationals and subtracts 2^-1000 from the success bound. This is not sampled.

With a further 2^-60 for rounding, the success probability of one attempt, with the abort, is at least 0.3900000017 at Tb. It is 0.3899999926 at Tb - 2^94, so Tb is the least multiple of 2^94 that reaches 0.39. Appendix A computes both with 80-digit decimals.

In evaluations, 256 Tb = 1.011317 x 2^128. Most of this is the birthday point for success 0.39, which is 0.9943 x 2^128. The wait for the DPs of the last trails, 256 x 2^114 = 2^122 evaluations, is the main reason the count is above it.

A failed attempt (probability up to 0.61 in M, and under the premise H_rand for the fixed target) can be repeated with a fresh rho at the same cost. The claim is one attempt with success 0.39, a probability over the algorithm's coin rho for the fixed target, under the premise H_rand.

## 6. Memory

The search, at its peak:

| region | bytes |
|---|---:|
| register file, 2,192 words of 32 bytes (H_reg) | 70,144 |
| straight line plus prefilter, 42,497 instructions x 5 bytes (H_code) | 212,485 |
| other code (Appendix D: setup, loop, hit handler, DP handler, restart, deadline scan, replay, output), measured 2,656 instructions x 32 bytes | 84,992 |
| table, 19,000 words | 608,000 |
| LID and LST of the 256 walks, 512 words | 16,384 |
| data image (lane constants K of the absorbed state, PD, output pair), 16 words | 512 |
| **total** | **992,517** |

The other code is the assembled file other.bin, 2,656 x 32 = 84,992 bytes, not a bound. The first version of this table carried an allowance of 4,096 instructions (131,072 bytes), which left a margin of 251 bytes; the margin of the search phase is now 56,059 bytes. The table is unchanged at 19,000 words: the memory freed is not used to enlarge it.

**Preprocessing.** The selection run `gen 512` runs before the search and ends before it starts (Section 3.6).

| `gen 512` | bytes |
|---|---:|
| text | 17,985 |
| static arrays, data plus BSS (`MAXN = 45312`, `MAXF = 4096`) | 736,740 |
| image (text, data, BSS) | 754,725 |
| stack reserve (the run completes with a 16,384-byte stack limit) | 32,768 |
| the program it writes, prog.bin (streamed through a 4,000-byte buffer, counted here in full) | 212,410 |
| **bound used** | **999,903** |
| measured peak resident memory (VmHWM), at most | 618,496 |
| smallest address-space limit under which it completes | 901,120 |

The working memory of the generator is released before the table is filled.

**Total.** The two phases do not overlap, so the peak is the larger of the two, 999,903 <= 1,048,576 = 2^20. So memory_log2_bytes = 20 and the memory term of the score is 0. If the generator's measured peak is added to the search's instead (Section 8), the total is about 2^20.62; with its image, stack and output instead, about 2^20.93. Peak = max(search 992,517; preprocessing 999,903) = 999,903. The margin to 2^20 is 48,673 bytes (the preprocessing phase is the larger).

**The declared experiments are verification runs.** They run in Python at reduced width (rho-w22) or on 2,048 points per trial (proj-w256), as evidence of correctness and of the behaviour of the function.

They build nothing the attack uses: the attack of Sections 4 and 6 is the straight line, the search code and the table, whose bytes are listed above.

The C programs used for the checks of Sections 3.7 and 7.3 are likewise verification only.




## 7. Evidence for the step and for H_rand

### 7.1 Organizer experiments (declared in experiments/manifest.json, program experiments/ls1.py)

Both experiments regenerate the straight line in Python with the generator's algorithm and node order (the encoding must hash to the SHA-256 of Section 3.5), check it against the plain eight-round implementation, and execute it on Python integers, all trials side by side.

- **rho-w22** runs the search of Section 4 end to end at width 22. The planes 22 to 255 are set to zero after every step. The parameters are a DP of 4 low image bits zero, cap 128, 3,000 trails and 400 steps per attempt. Every trial returns two messages whose eight-round digests agree on the 22 low bits.
  - At this width a start often lies on another trail, so a replay that returns nothing restarts the walk instead of ending the attempt. The full-size rule of Section 4 halts, as the failure term F4 accounts.
  - Our ideal-function control runs the same search with F replaced by a lazily sampled random function on 22 bits (the control does not depend on the round count): 17.94 steps to the pair (20,000 trials, standard deviation 7.05). Organizer run on the public seed (256 trials): 256 of 256 trials returned a pair that the organizer's recomputation confirms. Our own runs on our own seeds (four requests of 256 trials): mean steps 17.86 (per request 17.53, 17.73, 18.32, 17.84; standard error about 0.22), against 17.94 for the ideal function.
- **proj-w256** runs eight chained full-width steps from 256 uniform points per trial and finds the first two distinct evaluated inputs whose images agree on the 22 low bits. The model gives success probability 0.3934 per trial, 100.7 of 256.
  - Organizer run on the public seed: 112 of 256 successes (0.438; z = +1.4). Our own runs on our own seeds (four requests of 256): 93, 89, 96, 92, 370 of 1,024 (0.361; z = -2.1). All 1,280 trials together: 482 (0.377; z = -1.2). Both sets are reported as run; this is a check of the program, not an estimate of the success probability.
  - The same trial in C at scale (Section 7.2): 0.3921 in 262,144 trials (z = -1.28).

### 7.2 Our measured checks of H_rand under the linear round 0 (not organizer runs)

The linear embedding makes round 0 affine, so F has one fewer nonlinear round than the plain digest map (seven nonlinear rounds here). These checks were re-run on the eight-round program file of this package. We measured whether that shows in the quantity the search depends on: the rate of image coincidences among the points it evaluates. hrand_test.c and proj_test.c (Appendix C) execute the program file itself. Results (AMD Ryzen 9 7900X, seeds in the sources):

```
A uniform inputs: M=2^24, pairs agreeing on 32 bits: low 32402, mid 32542, top 32632; expected 32768.0 each (sd 181.0); ratios 0.9888 0.9931 0.9958; z -2.02 -1.25 -0.75
B consecutive inputs R+i: M=2^24, pairs agreeing on 32 bits: low 32914, mid 32687, top 33111; expected 32768.0 each (sd 181.0); ratios 1.0045 0.9975 1.0105; z 0.81 -0.45 1.89
C chained iterates (256 chains x 65536 steps): M=2^24, pairs agreeing on 32 bits: low 32614, mid 32906, top 32687; expected 32768.0 each (sd 181.0); ratios 0.9953 1.0042 0.9975; z -0.85 0.76 -0.45
D single-bit differences: 65536 cells x 4096 pairs, max |z| 4.47 at input bit 103 output bit 196 (largest of 65536 normal cells is about 4.4); mean z^2 1.0080 (expected 1)
proj at scale: 262144 trials, 102799 successes = 0.3921; model 0.3934; z -1.28
```

What these show:
- **Windows A to C.** The windows are bits 0-31, 128-159 and 224-255. The top window lies inside the bits that define a distinguished point. In each window, pair-coincidence rates among 2^24 images match the random-function value within 1.2 percent (one standard deviation is 0.55 percent; the largest deviations are -1.12 percent, z = -2.02, in the low window of the uniform inputs, and +1.05 percent, z = +1.89, in the top window of the consecutive starts; among nine cells, one or two with |z| near 2 is expected). This holds for uniform inputs (A), for the consecutive starts rho + i the search uses (B), and for the chained iterates a walk evaluates (C).
- **Single-bit differences (D).** The output difference of single-bit input differences shows no bias: the largest |z| over 65,536 cells is 4.47, in line with independent cells (the largest of 65,536 normal cells is about 4.4, and 4.47 or more occurs with probability about 0.4), and the mean z^2 is 1.0080 (the standard deviation of that mean is 0.0055 for independent cells, so +1.5 standard deviations).

What they do not show: a deficit of a fraction of a percent, or any effect that appears only for 256-bit coincidences. The premise remains a premise. Additional evidence, not an organizer run (GPU, seed 20261016, 8-round F checked against the CPU reference on 20,000 points, 0 mismatches): the length of a rho walk on F truncated to w bits has mean ratio to the random-function value 1.0017 (CI95 0.9977 to 1.0057) at w = 44 (65,536 starts), 1.0039 (0.9958 to 1.0120) at w = 48 (16,384 starts) and 0.9892 (0.9565 to 1.0220) at w = 52 (1,024 starts), with sd/mean 0.521, 0.526 and 0.541 against 0.523 predicted by theory; the seven-round function gave 1.0011, 1.0032 and 1.0044 at the same widths. This tests the embedding and the truncation to w bits in rho length only; it does not test the full 256-bit chain, other output windows or the exact prefix-v1 event, and a rho of about 2^26 steps cannot show a deviation at the entry's real size.

If the real pair-coincidence rate is (1 - eps) of the random value, the same success needs about 0.5 log2(1/(1 - eps)) more bits of time. That is 0.0073 bit for eps = 0.01.

### 7.3 The emitted program, executed (our own runs, not organizer runs)

other8_test.py (Appendix D) executes the assembled bytes: other.bin decoded from its 32-byte encoding, and the straight line (prog.bin and the 15 prefilter instructions) decoded from its 5-byte encoding and compiled to Python integer operations. The results are in D.4.
- **Routines, at the full-size immediates (S = U = 19,000, DP planes 142..255).** The straight line against the plain eight-round implementation on every lane (2 x 256 points, 3 chained steps) and the prefilter word; setup (356,374 operations, TAB cleared, the 256 starts rho + l in the planes), setwalk (1,283), restart (1,289, and the halting call 3), evalF (2,197) and the message builder (27) against the plain implementation, a hit with no DP walk (105), the hit-counter abort, the DP handler with its longest path (walk 255 alone, all eight stages of the bit scan, the subtraction of S) with 0 and 5 occupied slots and with a wrap over 7 slots, the record and the restart it makes, the deadline scan with no expiry and strictly decreasing LST (2,822) and with three expired walks (2,822 - 255 + 3 x 1,292, as only the first walk lowers the running minimum). Each executed count equals the count of Section 4.3.
- **Replay.** 31 constructed pairs of trails (12-bit truncation of F, lengths la, lb with the merge placed before the end, la > lb, la < lb and la = lb): the replay finds the pair, the executed count equals 9 + 2 + n (e + 7) + 4 + (k - 1)(2e + 13) + (9 + 2e) + 67 with n = |la - lb| and k the lock-step iteration, exactly, and the pair is checked with an independent Keccak. The exits "p = q" and "m exhausted" were run on constructed registers.
- **End to end at reduced width.** The whole emitted program (setup, loop, straight line, hit handler, DP handler, restart, deadlines, replay, output) runs with the planes W..255 set to zero after each step (as the organizer's rho-w22) and the replay's F truncated alike (one extra ANDI in evalF, in test builds only), the other immediates reduced (table, caps, DP planes, prefilter planes); instruction for instruction it is the program of the full-size build. 27 runs on six parameter sets: W = 26 with a DP of 8 bits (8 seeds); W = 32 with a DP of 10 bits and a cap of 400 steps, so that trails are cut and the deadline scan runs (3 seeds, 34 to 347 deadline events each); a table of 400 words (8 seeds); a hit cap of 3 (3 seeds); Tb = 5 (2 seeds); U = 264 (3 seeds). They ended as the parameters dictate: a pair found in 15 runs, the hit abort in 3, U reached in 7, Tb reached in 2. Every pair found (m(a), m(b), distinct 128-byte messages) was checked with an independent Keccak: the eight-round digests agree on the W low bits. In every run the executed operations were at or below the counted bound of Section 4.3, and the sub-counts (setwalk, gather, loop, replay) matched exactly. The test was run twice and the two outputs are identical (336 checks, 0 failures).

What was not run: the full-size search (2^120 steps) and a full-size replay (up to 17 x 2^114 evaluations); the counts at those sizes are the counts of the same instructions times their trip counts, as in Section 4.3.

## 8. Sensitivity

| change | effect | score |
|---|---|---:|
| as claimed (H_reg 2,192 registers, H_code 5 bytes per instruction) | | 124.34902 |
| 1,024 registers, every load and store charged (Belady eviction) | not computed for r8 | not computed for r8 |
| 512 registers | not computed for r8 | not computed for r8 |
| 256 registers | not computed for r8 | not computed for r8 |
| 64 registers | not computed for r8 | not computed for r8 |
| straight line stored at 32 bytes per instruction | not computed for r8 | not computed for r8 |
| generator peak added to the search's memory instead of the larger of the two | not computed for r8 | not computed for r8 |

For round 7 the same rows were computed (1,024 registers 124.706, 512 registers 124.908, 256 registers 125.058, 64 registers 125.209, 32-byte code about 125.03, summed memory about 124.95). None of them was re-run or re-optimised for round 8, whose straight line is longer (42,482 operations against 35,517; the register use is the same, 2,181 registers with at most 1,925 live). We state the round-8 rows as not computed, and do not carry the round-7 numbers over to round 8.

- **Register rows and approximate rows.** None is computed for round 8; nothing in the claim rests on them.
- **H_rand.** A pair-coincidence deficit eps costs about 0.5 log2(1/(1 - eps)) bits (Section 7.2).
- **Same premises as 67f781f8.** Entry 67f781f8 uses the same register and 5-byte conventions. Under each row above it moves in the same direction; by its own Section 10, it is at 124.923 for 1,024 registers at six rounds. For round 8 no such row is computed here.

## 9. Relation to other entries, credits and literature

A credit is not an endorsement; nobody named here has reviewed this package.

- **jungjipdo, entry 67f781f8 (sha3-256-r6, 124.46633).** Its Section 3 describes the step design this package follows:
  - theta evaluated lazily per chi row and the per-row complement subsets;
  - dead-code elimination and the digest written over the input register;
  - last-use allocation into a declared register file;
  - the 5-byte straight-line encoding.

  We read its proof as a description. The generator, the self-test, the ledger, the search code and this text are our own, and none of its code was run, imported or compiled. The entry is on the six-round exploratory board, and this package is on the Pareto sha3-256 lane, which accepts only dependencies from its own challenge; so 67f781f8 is credited here and not declared as a dependency. This package uses the same register-file and code-encoding conventions (Section 3.5).
- **Our entry 2d74a370 (sha3-256-r6, 125.19730), our entries aa2e6be6 (S6LS, sha3-256-r6) and 4fe20ada (sha3-256 Pareto, round 8, 124.79004).** They supply the search: the lockstep distinguished-point walks with restart on a DP, the table, deadlines, the replay, the success bound of Section 5 and the rare-operation accounting. Those are reused here with new parameters. 4fe20ada is the eight-round Pareto entry whose step program this package replaces. Our entry f4f7b40e (LS1R7, sha3-256 Pareto, round 7, 124.28591) is the seven-round package of this exact design; this package is its port, and it is credited here and not declared as a dependency.
- **J. Guo, M. Liu, L. Song, Linear Structures: Applications to Cryptanalysis of Round-Reduced Keccak, ASIACRYPT 2016.** This is the linear-structure placement of message lanes that keeps round 0 linear, used in Section 2 as an embedding of the chain's points.
- **P. C. van Oorschot and M. J. Wiener, Parallel collision search with cryptanalytic applications, J. Cryptology 12 (1999); J. M. Pollard (1975).** These are the distinguished-point and rho methods.
- **G. Bertoni, J. Daemen, M. Peeters, G. Van Assche, Keccak implementation overview.** This is the source of the lane complementing transform, applied plane by plane in Section 3.2.

## 10. Limits

- **H_rand.** An assumption, not proved: that over the algorithm's coin rho the program on the fixed target succeeds with at least the random-function probability of Section 5. It is not tested at 256 bits; no run reaches 2^128 and no full collision is claimed. The checks of Section 7 work at 22, 32 and 44 to 52 bits, and the 32-bit checks were re-run on the eight-round program.
- **H_reg and H_code.** These are declared machine conventions, role supporting in claim.json (Section 3.5). The cost model fixes no register count and no code encoding. Both move the score; Section 8 states that their round-8 prices are not computed.
- **What is executed, and what is bounded.**
  - The straight line is executed and compared with the plain permutation.
  - The search runs at width 22 in the experiment.
  - The routines of Section 4.3 are generated, assembled and executed (Appendix D). Their counts are the lengths of the emitted code on the longest path times the stated trip counts; no full-size run exists (the executed runs of Section 7.3 are at reduced width and parameters, the same instructions with other immediates).
  - The size of the other code is the measured 2,656 instructions (84,992 bytes).
  - The instruction set of the other code (immediates in the 32-byte word, shifts by a register, PERM at one unit) is our declaration under H_code; the cost model fixes none.
- **Replay cost.** The replay is charged one unit per permutation call, plus the stated per-call operations.

## 11. The six- and seven-round versions of this design

The same design at six rounds (generator, search and ledger identical in method) was filed as 3ff7e687 and again, with the wording of H_reg and H_code as declared conventions of role supporting (as in Section 3.5), as e1c05beb, at time_log2 124.19636. At seven rounds it was filed as f4f7b40e (LS1R7), at time_log2 124.28591. This package is the eight-round port of f4f7b40e: NROUNDS 8 in the generator, one more generic round in the step program (6,965 operations), the unit 2168 of the eight-round target, the self-test unchanged at 4,096 evaluations, and the table cut from 20,000 to 19,000 words so that the longer straight line fits the memory bound (the success bound is recomputed in Appendix A). The other code of this version is written out and measured (Section 4.3, Appendix D). The ruling on that first filing (a286eaf9) named these material findings: F-other-code-margin and F-ancillary-ledger are answered in Section 4.3 and Appendix D; F-reg-model-gap (the H_reg convention) and F-fullscale-success-transfer, F-HRAND-SCALE, F-EXP-SCALE-1 and F-EXP-STAT-1 (the transfer of H_rand and the scale of the experiments) are not answered by new evidence in this version: H_reg is declared as in Section 3.5, H_rand stays the stated premise of Section 5, and Sections 7, 8 and 10 state what was not tested and not priced. Its minor findings F-memory-label-typo and F-r7-source-comment are fixed (the row label in Appendix A, the comment of gen.c). The statement of H_rand is restated as the transfer premise of Section 5 (an assumption, not proved), and the proof of the F2 fact is the lazy-sampling argument of Section 5. The convention statements and the evidence of Section 7.2 are recomputed for the eight-round program, not carried over; the sensitivity rows of Section 8 are not.

## Appendix A. The exact ledger

This program (cert.py) computes the step count, the success bound of Section 5, N, the memory table and the integer certificate. It uses integers and Fractions; Decimal with 80 digits is used only for the exponentials and logarithms of the success bound. It runs in about 30 seconds. Tb was found with `cert.py --search 66000000 69500000`, and the run below re-checks that Tb is the least multiple of 2^94 with success at least 0.39. The constants of the rare operations and of the replay are the counts of Section 4.3, printed by `other8.py build` (D.2).

```python
# LS1 exact ledger: step count, success bound, N, memory, integer certificate (integers and Fractions; Decimal with 80
# digits only for the exponentials and logarithms of the success bound).
import sys
from fractions import Fraction as Fr
from decimal import Decimal as D, getcontext, ROUND_CEILING
getcontext().prec = 80
ceil = lambda v: int(v.to_integral_value(rounding=ROUND_CEILING)) if isinstance(v, D) else -((-v.numerator) // v.denominator)

# ---- one step of 256 walks (Section 3; counts printed by the generator gen.c, ledger.txt) ----
XOR, AND, OR, NOT = 31201, 5917, 3939, 1425
LINE = XOR + AND + OR + NOT                      # the straight line, no loads or stores (registers, H_reg)
assert LINE == 42482
PF = 15                                          # prefilter: OR of the 16 planes 240..255
BSTEP = LINE + PF + 2 + 3                        # + compare pf with all-ones and branch; c += 1, compare with nxt, branch
print('step of 256 walks: straight line', LINE, '(xor %d and %d or %d not %d) + prefilter %d + test 2 + counter 3 =' % (XOR, AND, OR, NOT, PF), BSTEP)

# ---- parameters of the search (Section 4) ----
L, H, U = 256, 114, 19000                        # walks; distinguished point: planes 142..255 zero (theta = 2^-H); trail limit
S = U                                            # table words
KAPPA = 17
Lc = KAPPA * 2 ** H                              # cap on the length of a trail, in steps
n = D(2) ** 256
theta = D(2) ** -H
BINS = 12                                        # bins of w = 2^(H-12) steps for the remaining trail length
w = 2 ** (H - BINS)
J = Lc // w
lq = (1 - theta).ln()


def success(Tb):
    """Lower bound on the success probability of one attempt of Tb steps (Section 5)."""
    s, qprev = D(0), D(1)
    for j in range(1, J + 1):
        qj = (w * j * lq).exp()
        e = L * (Tb - j * w)
        if e > 1:
            s += (qprev - qj) * (1 - (-D(e) * (e - 1) / (2 * n)).exp())
        qprev = qj
    e1 = U * (-D(Lc) * theta).exp()                          # F1: some trail has no distinguished point within Lc steps
    mu, k = D(L * Tb) * theta, U - L
    e2 = (-mu + k * (1 + (mu / k).ln())).exp()               # F2: more than U - L distinguished points (Chernoff, k > mu)
    assert k > mu
    e3 = D(U) * D(2) ** (2 * H) / n                          # F3: a coincidence inside one trail
    e4 = D(2) ** -90                                         # F4: starts, end-key matches, replay
    e5 = D(2) ** -1000                                       # F5: the hit counter passes HMAX (abort); bound proved below
    return s - (e1 + e2 + e3 + e4 + e5 + D(2) ** -60), (e1, e2, e3, e4)


GRAN = 2 ** (H - 20)
if len(sys.argv) > 1 and sys.argv[1] == '--search':
    lo, hi = int(sys.argv[2]) * GRAN, int(sys.argv[3]) * GRAN
    assert success(hi)[0] >= D('0.39') > success(lo)[0]
    while hi - lo > GRAN:
        mid = (lo + hi) // 2 // GRAN * GRAN
        if success(mid)[0] >= D('0.39'): hi = mid
        else: lo = mid
    print('TB = %d * 2^%d' % (hi // GRAN, H - 20)); sys.exit()

TB = 67868324 * GRAN                                          # least multiple of 2^94 with success >= 0.39 (checked below)
p, (e1, e2, e3, e4) = success(TB)
p_less, _ = success(TB - GRAN)
assert p >= D('0.39') > p_less
print('Tb = %d = %.8f * 2^120, evaluations %.6f * 2^128' % (TB, D(TB) / D(2) ** 120, D(L * TB) / D(2) ** 128))
print('failure terms: F1 %.3e  F2 %.3e  F3 %.3e  F4 %.3e  success bound %s  (2^94 steps fewer: %s)' % (e1, e2, e3, e4, str(p)[:12], str(p_less)[:12]))

# ---- replay (Section 4.2): counted from the emitted code (other8.py build, counts.txt) ----
UNIT = 2168
E_EVAL = UNIT + 29                                           # evalF: state build 26 + permutation (one unit) + load PD, xor 2 + return 1
REPLAY_ITER = 2 * E_EVAL + 13                                # one lock-step iteration (4,407); an advance step costs E_EVAL + 7
REPLAY_CONST = 78                                            # entry, alignment, the two message builds, the 8 stores, HALT (largest path)
replay = REPLAY_ITER * Lc + REPLAY_CONST                     # at most max(la, lb) <= Lc iterations of cost at most REPLAY_ITER

# ---- prefilter hit counter and abort (Sections 4 and 5, F5) ----
DELTA = Fr(1, 2 ** 20)
HMAX = (TB * (1 + DELTA)) // 2 ** 8 + 1 + Lc                 # the driver aborts (attempt failed) when hit number HMAX + 1 occurs
# F5: abort => X' > (1 + DELTA) Tb 2^-8, X' = steps with a hit among walks at fresh inputs (conditional prob. <= 2^-8 each,
# H_rand); steps with a walk at a repeated input lie after the first coincidence and number at most Lc before the stop.
# Chernoff for adapted indicators: P[X' >= (1 + d) mu] <= exp(-d^2 mu / (2 + d)), mu = Tb 2^-8.
MU = Fr(TB, 2 ** 8)
EXPO = DELTA ** 2 * MU / (2 + DELTA)                         # P[F5] <= exp(-EXPO)
assert EXPO > 1000 * Fr(6932, 10000)                         # ln 2 < 0.6932, so P[F5] < 2^-1000 (the e5 of success())
print('hit counter: HMAX =', HMAX, '; P[abort before the stop on success] <= exp(-%d) < 2^-1000' % (EXPO.numerator // EXPO.denominator))

# ---- rare operations (Section 4.3): every constant is the operation count of the emitted code (other8.py counts()) ----
hits = HMAX + 1                                              # at most HMAX + 1 hits are processed in every execution
C_hit = 105                                                  # counter 3 + OR of planes 142..239 (97) + combine and NOT (2) + c1 (1) + test of the DP mask (2)
C_dp_fixed, C_slot = 1089, 10                                # one DP walk without the probe: 2 + 44 + 1,022 + 12 + 3 + 2 + 4; 10 per occupied slot passed
C_dp = C_dp_fixed + C_slot * (S - 1)                         # the table has at most S - 1 occupied slots to pass
C_restart, C_restart_halt = 1289, 3                          # restart(l) with the 256 planes; the call that halts at idn = U
C_dl, C_dl_final = 2822, 3                                   # deadline event: scan of the 256 walks (11 each) and nxt; the event c = Tb
C_setup = 356374                                             # setup: 7 + 11 S/8 + 1 + 256 x 1,290 + 1
N_DP, N_RESTART, N_DL = U - 255, U - 256, U - 254            # events: each DP event but the last is followed by a completed restart (idn goes from 256 to U);
                                                             # deadline events lie at distinct start times + Lc, one per start time, plus c = Tb
R = hits * C_hit + N_DP * C_dp + N_RESTART * (C_restart + 3) + C_restart_halt + N_DL * C_dl + C_dl_final + C_setup
PRE = 513 * 2 ** 32 + 512 * 2 ** 10 + 2 ** 12                          # preprocessing = the selection run `gen 512`: 512 trial builds and the
                                                             # rebuild of the best, 2^32 each, + 2^12 for the data step (meta.txt -> data.bin), + per trial at most 2^10 for the
                                                             # constants, the total, the comparison, the best update and the line
N = TB * BSTEP + replay + R + PRE
print('main', TB * BSTEP, ' replay', replay, ' rare', R, ' preprocessing', PRE)
pl = 30
assert (UNIT << (pl - 1)) < PRE <= (UNIT << pl)
print('preprocessing_log2: 2^%d < PRE / 2168 <= 2^%d, declared %d' % (pl - 1, pl, pl))
print('N =', N)
print('shares: main %.5f replay %.5f other %.2e' % (TB * BSTEP / N, replay / N, (R + PRE) / N))

# ---- memory (Section 6) ----
REGS = 2192                                                  # 2,181 used by the straight line + the search state in 2,181..2,190 (2,191 spare)
mem_run = {
    'register file, 2,192 words': 32 * REGS,
    'straight line incl. prefilter, 42,497 instructions x 5 bytes': 5 * (LINE + PF),
    'other code (setup, loop, handlers, restart, deadline scan, replay), measured 2,656 instructions x 32 bytes': 32 * 2656,
    'table, %d words' % S: 32 * S,
    'LID and LST of the 256 walks, 512 words': 32 * 512,
    'data image (lane constants K, PD, output pair), 16 words': 32 * 16,
}
run_total = sum(mem_run.values())
GEN_PEAK = 618496                                            # bound on the measured VmHWM of `gen 512` (resident; 5 runs 596 to 604 KiB = 610,304 to 618,496 B)
GEN_IMAGE = 17985 + 4 + 736736                               # gen (MAXN = 45312, MAXF = 4096): text 17,985 + data 4 + BSS 736,736, size(1); all arrays are static
GEN_STACK = 32768                                            # stack reserve; `gen 512` completes with the stack limited to 16,384 bytes
pre_total = max(GEN_PEAK, GEN_IMAGE + GEN_STACK) + 5 * LINE  # generator (declared image and stack) plus the program it writes
for k, v in mem_run.items(): print('  %9d  %s' % (v, k))
print('search memory', run_total, '; preprocessing (gen 512): image', GEN_IMAGE, '+ stack', GEN_STACK, '+ program', 5 * LINE, '=', pre_total, '(measured resident peak %d)' % GEN_PEAK)
mem = max(run_total, pre_total)
assert mem <= 2 ** 20
assert 2 ** 20 - mem >= 4096                                  # margin of at least 4 KiB
print('memory', mem, '<= 2^20 = 1048576 with a margin of', 2 ** 20 - mem, 'bytes (search phase', 2 ** 20 - run_total, '): memory_log2_bytes = 20')

K = 100000
e = ceil(K * (D(N) / UNIT).ln() / D(2).ln())
while N ** K > (UNIT ** K) << e: e += 1
while N ** K <= (UNIT ** K) << (e - 1): e -= 1
print('certificate: 2168^%d * 2^%d < N^%d <= 2168^%d * 2^%d' % (K, e - 1, K, K, e))
print('time_log2 = %d.%05d' % divmod(e, K))
print('score = time_log2 + max(0, memory_log2 - 20) = %d.%05d' % divmod(e, K))
```

Output:

```
step of 256 walks: straight line 42482 (xor 31201 and 5917 or 3939 not 1425) + prefilter 15 + test 2 + counter 3 = 42502
Tb = 1344270650860686671361005282410889216 = 1.01131684 * 2^120, evaluations 1.011317 * 2^128
failure terms: F1 7.866e-04  F2 3.745e-60  F3 7.078e-05  F4 8.078e-28  success bound 0.3900000017  (2^94 steps fewer: 0.3899999926)
hit counter: HMAX = 358327248618091250208476601149030401 ; P[abort before the stop on success] <= exp(-2387903226020418597917) < 2^-1000
main 57134191202880904906185446513027613458432  replay 1556006753378283004407505017955361488974  rare 37624361104899581271890043124307442905  preprocessing 2203318751232
preprocessing_log2: 2^29 < PRE / 2168 <= 2^30, declared 30
N = 58727822317364087491864841576310601141543
shares: main 0.97286 replay 0.02650 other 6.41e-04
      70144  register file, 2,192 words
     212485  straight line incl. prefilter, 42,497 instructions x 5 bytes
      84992  other code (setup, loop, handlers, restart, deadline scan, replay), measured 2,656 instructions x 32 bytes
     608000  table, 19000 words
      16384  LID and LST of the 256 walks, 512 words
        512  data image (lane constants K, PD, output pair), 16 words
search memory 992517 ; preprocessing (gen 512): image 754725 + stack 32768 + program 212410 = 999903 (measured resident peak 618496)
memory 999903 <= 2^20 = 1048576 with a margin of 48673 bytes (search phase 56059 ): memory_log2_bytes = 20
certificate: 2168^100000 * 2^12434901 < N^100000 <= 2168^100000 * 2^12434902
time_log2 = 124.34902
score = time_log2 + max(0, memory_log2 - 20) = 124.34902
```

so N = 58727822317364087491864841576310601141543 word operations and time_log2 = 124.34902.

## Appendix B. The generator (gen.c) and the self-test (selftest.c)

Build: `gcc -O2 -static -nostdlib -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns -fno-stack-protector -fno-pie -no-pie -o gen gen.c`; run `gen 512` (writes prog.bin, meta.txt, ledger.txt; `gen 1 192` writes the same files). `selftest run 4` checks prog.bin as in Section 3.7; `selftest kat` prints the reference digests compared with hashlib and the organizer reference.

```c
/* gen.c - LS1 step generator for sha3-256-r8 (8 prefix rounds of Keccak-f[1600]).
 * Freestanding (no libc) so the measured peak RSS is the generator's own working set.
 *
 * Chain function on physical 256-bit points u (4 lanes u0..u3):
 *   message m(u) = 128 bytes = lanes 0..15 of the absorbed state:
 *     lane 1 = u0, lane 6 = u1, lane 11 = u0^u1^K[11]   (column x=1, rows 0,1,2)
 *     lane 4 = u2, lane 9 = u3, lane 14 = u2^u3^K[14]   (column x=4, rows 0,1,2)
 *     other lanes 0..15 = constants K[l]; lane 16 = 0x8000000000000006 (SHA3 pad);
 *   F(u) = SHA3-256-r8(m(u)) XOR PD   (PD = fixed digest polarity mask of the program).
 * Column parities of the message lanes are constant, so round-0 theta adds only
 * constants; no two message lanes are chi-adjacent after rho/pi, so round 0 is
 * linear in u and round-1 theta stays linear (Guo-Liu-Song 2016 linear structure).
 *
 * Representation: plane (lane,z) is one 256-bit word (bit t = trail t). A value is
 * (node, polarity): logical = physical(node) XOR p. Constants folded. Linear nodes
 * carry their GF(2) form over the 256 input bits, deduplicated by form.
 * Lazy theta: C, D per round; each chi row XORs D into its five planes when computed.
 * Per-row complement subset (32 candidates) minimizing NOTs + two-op terms.
 * Dead-code elimination, last-use register allocation; digest plane j written to
 * register j (= input register j of the next step: free chain feed).
 * Outputs: prog.bin (5 bytes/instr: 3-bit op, 12-bit dst, a, b), meta.txt, ledger.txt.
 * Usage: gen [ntrials] [first]  (trial 0: all constants 0; trial t>0: xorshift constants seed t).
 * The preprocessing of the attack is the selection run "gen 512": 512 trial builds, the best (trial 192) rebuilt and written.
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
static int fopen_w(const char *p){ return (int)sc3(2,(i64)p,01|0100|01000,0644); } /* O_WRONLY|O_CREAT|O_TRUNC */
static void fclose_(int fd){ sc3(3,fd,0,0); }
static void die(const char *m){ oflush(); fd_out=2; os("gen: "); os(m); oc('\n'); oflush(); sc3(60,1,0,0); }
static int atoi_(const char *s){ int v=0; while(*s>='0'&&*s<='9') v=v*10+(*s++-'0'); return v; }

/* ---------- Keccak constants ---------- */
static const u64 RC[24]={0x0000000000000001UL,0x0000000000008082UL,0x800000000000808aUL,0x8000000080008000UL,
 0x000000000000808bUL,0x0000000080000001UL,0x8000000080008081UL,0x8000000000008009UL,0x000000000000008aUL,
 0x0000000000000088UL,0x0000000080008009UL,0x000000008000000aUL,0x000000008000808bUL,0x800000000000008bUL,
 0x8000000000008089UL,0x8000000000008003UL,0x8000000000008002UL,0x8000000000000080UL,0x000000000000800aUL,
 0x800000008000000aUL,0x8000000080008081UL,0x8000000000008080UL,0x0000000080000001UL,0x8000000080008008UL};
static const int ROT[5][5]={{0,36,3,41,18},{1,44,10,45,2},{62,6,43,15,61},{28,55,25,21,56},{27,20,39,8,14}}; /* ROT[x][y] */
#define NROUNDS 8

/* ---------- node store ---------- */
#define MAXN 45312           /* r8: node store sized for the selected build */
#define NC 0xFFFF            /* constant marker */
enum { O_IN=0, O_XOR=1, O_AND=2, O_OR=3, O_NOT=4 };
#define F_OPM 7
#define F_K 8                /* physical constant of a linear node */
#define F_LIVE 16
#define F_LIN 32
static u8 nf[MAXN];          /* op | flags */
static u16 na[MAXN], nb[MAXN];
static u16 linid[MAXN];      /* form index for linear nodes; reused as reg[] */
#define MAXF 4096
static u64 form[MAXF][4]; static u16 formnode[MAXF]; static int nform;
#define FH 8192
static u16 fh[FH];           /* form hash: form index+1 */
#define CH 65536
static u16 ch[CH];           /* cons hash: node+1; reused as lastuse[] */
static int nn;

typedef struct { u16 n; u8 p; } V;
static V K_(int c){ V v; v.n=NC; v.p=(u8)c; return v; }
static V MK(int n,int p){ V v; v.n=(u16)n; v.p=(u8)p; return v; }

static u32 hmix(u32 x){ x^=x>>16; x*=0x7feb352dU; x^=x>>15; x*=0x846ca68bU; x^=x>>16; return x; }
static int newnode(int op,int a,int b){ if(nn>=MAXN-1) die("node overflow"); nf[nn]=(u8)op; na[nn]=(u16)a; nb[nn]=(u16)b; linid[nn]=0xFFFF; return nn++; }
static int cons(int op,int a,int b){
  if(op!=O_NOT && a>b){ int t=a;a=b;b=t; }
  u32 h=hmix((u32)op*0x9E3779B1u ^ (u32)a*0x85EBCA77u ^ (u32)b*0xC2B2AE3Du)&(CH-1);
  for(;;){ u16 e=ch[h]; if(!e) break; int m=e-1; if((nf[m]&F_OPM)==op && na[m]==a && nb[m]==b) return m; h=(h+1)&(CH-1); }
  int m=newnode(op,a,b); ch[h]=(u16)(m+1); return m;
}
static int isk(int n){ return (nf[n]&F_K)?1:0; }
static int islin(int n){ return (nf[n]&F_LIN)?1:0; }
static u32 fhash(const u64 *m){ return hmix((u32)(m[0]^m[0]>>32^m[1]*3^m[2]*5^m[3]*7^(m[1]>>29)^(m[3]>>31))); }
static int flookup(const u64 *m){ u32 h=fhash(m)&(FH-1); for(;;){ u16 e=fh[h]; if(!e) return -1; int f=e-1; if(form[f][0]==m[0]&&form[f][1]==m[1]&&form[f][2]==m[2]&&form[f][3]==m[3]) return f; h=(h+1)&(FH-1);} }
static int fadd(const u64 *m,int node){ if(nform>=MAXF) die("form overflow"); int f=nform++; for(int i=0;i<4;i++) form[f][i]=m[i]; formnode[f]=(u16)node;
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
  int before=nn; int n=cons(O_NOT,a.n,0);
  if(nn>before){ cnt_emit++; if(islin(a.n)){ nf[n]|=F_LIN|(isk(a.n)?0:F_K); linid[n]=linid[a.n]; } }
  return MK(n,a.p^1);
}
static V and2(V a,V b){ /* logical a AND b */
  if(a.n==NC) return a.p? b : K_(0);
  if(b.n==NC) return b.p? a : K_(0);
  if(a.n==b.n) return a.p==b.p? a : K_(0);
  int before=nn;
  if(a.p==0&&b.p==0){ int n=cons(O_AND,a.n,b.n); if(nn>before) cnt_emit++; return MK(n,0); }
  if(a.p==1&&b.p==1){ int n=cons(O_OR,a.n,b.n); if(nn>before) cnt_emit++; return MK(n,1); }
  /* A & ~B with A the pol-0 operand: A ^ (A & B) */
  int A=a.p==0?a.n:b.n, B=a.p==0?b.n:a.n;
  int t=cons(O_AND,A,B); if(nn>before) cnt_emit++;
  return xorv(MK(A,0),MK(t,0));
}
static V andnot(V b1,V b2){ b1.p^=1; return and2(b1,b2); } /* (~b1) & b2 */

/* cost estimate of (~b1)&b2 given polarities */
static int cost_term(V b1,V b2){ if(b1.n==NC||b2.n==NC||b1.n==b2.n) return 0; return ((b1.p^1)==b2.p)?1:2; }

/* ---------- the step ---------- */
static V S[25][64], NS[25][64], Cc[5][64], Dd[5][64];
static u64 KL[25];          /* lane constants of the absorbed state (var lanes: offset) */
static int outnode[256];
static u64 PD[4];
static long nnot_rows;

static void build(void){
  nn=0; nform=0; cnt_emit=0; nnot_rows=0;
  memset(fh,0,sizeof fh); memset(ch,0,sizeof ch);
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
  for(int r=0;r<NROUNDS;r++){
    int last=(r==NROUNDS-1);
    /* theta: C[.][63] first, then per z: C[.][z], D[.][z] (keeps few C live) */
    for(int x=0;x<5;x++){ V s=S[x][63]; for(int y=1;y<5;y++) s=xorv(s,S[x+5*y][63]); Cc[x][63]=s; }
    for(int z=0;z<64;z++){
      if(z<63) for(int x=0;x<5;x++){ V s=S[x][z]; for(int y=1;y<5;y++) s=xorv(s,S[x+5*y][z]); Cc[x][z]=s; }
      for(int x=0;x<5;x++) Dd[x][z]=xorv(Cc[(x+4)%5][z],Cc[(x+1)%5][(z+63)&63]);
    }
    int nY=last?1:5, needmask=last?0x0F:0x1F;
    for(int Y=0;Y<nY;Y++) for(int z=0;z<64;z++){
      V b[5];
      for(int X=0;X<5;X++){ int y=X, x=(3*Y+X)%5; int zz=(z-ROT[x][y]+64)&63; b[X]=xorv(S[x+5*y][zz],Dd[x][zz]); }
      /* complement subset */
      int best=-1,bc=1<<30;
      for(int s=0;s<32;s++){
        int c=0; V bb[5];
        for(int X=0;X<5;X++){ bb[X]=b[X]; if(s>>X&1){ if(b[X].n==NC){ c=1<<29; } else { bb[X].p^=1; c++; } } }
        for(int X=0;X<5;X++) if(needmask>>X&1) c+=cost_term(bb[(X+1)%5],bb[(X+2)%5]);
        if(c<bc){ bc=c; best=s; }
      }
      for(int X=0;X<5;X++) if(best>>X&1){ b[X]=notv(b[X]); nnot_rows++; }
      for(int X=0;X<5;X++) if(needmask>>X&1){
        V t=andnot(b[(X+1)%5],b[(X+2)%5]);
        NS[X+5*Y][z]=xorv(b[X],t);
      }
    }
    for(int z=0;z<64;z++) NS[0][z].p^=(RC[r]>>z)&1;   /* iota */
    for(int l=0;l<25;l++) for(int z=0;z<64;z++) S[l][z]=NS[l][z];
  }
  PD[0]=PD[1]=PD[2]=PD[3]=0;
  for(int j=0;j<256;j++){ V v=S[j>>6][j&63]; if(v.n==NC||v.n<256) die("digest plane constant or input"); outnode[j]=v.n; PD[j>>6]|=(u64)v.p<<(j&63); }
  for(int j=0;j<256;j++) for(int k=j+1;k<256;k++) if(outnode[j]==outnode[k]) die("shared digest node");
}

static long cnt[5], nlive, maxlive, maxreg;
static void dce(void){
  for(int i=0;i<nn;i++) nf[i]&=~F_LIVE;
  for(int j=0;j<256;j++) nf[outnode[j]]|=F_LIVE;
  for(int i=nn-1;i>=256;i--) if(nf[i]&F_LIVE){ int op=nf[i]&F_OPM; nf[na[i]]|=F_LIVE; if(op!=O_NOT) nf[nb[i]]|=F_LIVE; }
  for(int k=0;k<5;k++) cnt[k]=0; nlive=0;
  for(int i=256;i<nn;i++) if(nf[i]&F_LIVE){ cnt[nf[i]&F_OPM]++; nlive++; }
}

/* register allocation; writes prog.bin when emit */
#define NREG 2304
static u16 freestk[NREG]; static int nfree;
static u16 outdef[256];
static int alloc_emit(int emit){
  u16 *last=ch, *reg=linid;     /* reuse */
  for(int i=0;i<nn;i++) last[i]=0;
  for(int i=256;i<nn;i++) if(nf[i]&F_LIVE){ last[na[i]]=(u16)i; if((nf[i]&F_OPM)!=O_NOT) last[nb[i]]=(u16)i; }
  for(int j=0;j<256;j++){ last[outnode[j]]=0xFFFF; outdef[j]=(u16)outnode[j]; }
  static u8 outof[MAXN/8+1]; memset(outof,0,sizeof outof);
  static u8 regbusy[NREG]; memset(regbusy,0,sizeof regbusy);
  static short outj[MAXN];  /* only touched for out nodes */
  for(int j=0;j<256;j++){ outof[outnode[j]>>3]|=1<<(outnode[j]&7); outj[outnode[j]]=(short)j; }
  nfree=0; for(int r=NREG-1;r>=256;r--) freestk[nfree++]=(u16)r;
  long live=0; maxlive=0; maxreg=0;
  for(int j=0;j<256;j++){ reg[j]=(u16)j; if(last[j]){ regbusy[j]=1; live++; } }
  if(live>maxlive) maxlive=live;
  int fd=-1; if(emit){ fd=fopen_w("prog.bin"); if(fd<0) die("open prog.bin"); }
  static u8 eb[4000]; int el=0; long ninstr=0;
  for(int i=256;i<nn;i++){
    if(!(nf[i]&F_LIVE)) continue;
    int op=nf[i]&F_OPM; int a=na[i], b=(op==O_NOT)?a:nb[i];
    /* free operands whose last use is here */
    int ops[2]={a,b};
    for(int k=0;k<2;k++){ int o=ops[k]; if(k==1&&o==a) break; if(last[o]==i){ int r=reg[o]; regbusy[r]=0; live--; if(r>=256) freestk[nfree++]=(u16)r; } }
    int dst;
    if(outof[i>>3]>>(i&7)&1){ dst=outj[i]; if(regbusy[dst]) die("output register busy"); }
    else if(nfree>0) dst=freestk[--nfree];
    else { dst=-1; for(int r=0;r<256;r++) if(!regbusy[r] && outdef[r]>=last[i]) { dst=r; break; } if(dst<0) die("out of registers"); }
    regbusy[dst]=1; live++; reg[i]=(u16)dst; if(live>maxlive) maxlive=live; if(dst+1>maxreg) maxreg=dst+1;
    if(last[i]==0){ /* dead value (cannot happen after DCE) */ die("live node without use"); }
    if(emit){
      int code= op==O_XOR?0: op==O_AND?1: op==O_OR?2: 3;
      u64 w=(u64)code | (u64)dst<<3 | (u64)reg[a]<<15 | (u64)(op==O_NOT?0:reg[nb[i]])<<27;
      for(int k=0;k<5;k++) eb[el++]=(u8)(w>>(8*k));
      if(el>=3995){ sc3(1,fd,(i64)eb,el); el=0; }
    }
    ninstr++;
  }
  if(emit){ if(el) sc3(1,fd,(i64)eb,el); fclose_(fd); }
  return (int)ninstr;
}

static u64 rs;
static u64 xs(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static void set_consts(int trial){
  for(int l=0;l<25;l++) KL[l]=0;
  KL[16]=0x8000000000000006UL;
  if(trial>0){ rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs();
    static const int fl[12]={0,2,3,5,7,8,10,12,13,15,11,14};
    for(int i=0;i<12;i++) KL[fl[i]]=xs(); }
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
  int fd=(int)sc3(2,(i64)"ledger.txt",01|02000,0);
  for(int pass=0;pass<2;pass++){ fd_out= pass?1:fd;
    os("worker peak RSS (getrusage via wait4, worker forked from the 1-page parent) "); ou(ru.maxrss); os(" KiB = "); ou(ru.maxrss*1024); os(" bytes (limit 1048576)\n"); oflush(); }
  fclose_(fd);
  return ((status>>8)&255);
}
static int work(int argc,char **argv){
  int ntr= argc>1? atoi_(argv[1]) : 1; if(ntr<1) ntr=1;
  int t0= argc>2? atoi_(argv[2]) : 0;   /* gen <ntrials> [first trial]; the attack runs "gen 512" */
  int bestt=t0; long bestc=1L<<60;
  for(int t=t0;t<t0+ntr;t++){ set_consts(t); build(); dce(); long tot=cnt[1]+cnt[2]+cnt[3]+cnt[4];
    if(ntr>1){ os("trial "); ou(t); os(" ops "); ou(tot); oc('\n'); }
    if(tot<bestc){ bestc=tot; bestt=t; } }
  oflush();
  set_consts(bestt); build(); dce();
  long pre=cnt_emit;
  int ninstr=alloc_emit(1);
  long tot=cnt[1]+cnt[2]+cnt[3]+cnt[4];
  if(ninstr!=tot) die("instr count mismatch");
  struct { long ut[2], st[2]; long maxrss, ixrss, idrss, isrss, minflt, majflt, nswap, inblock, oublock, msgsnd, msgrcv, nsignals, nvcsw, nivcsw; } ru;
  sc3(98,0,(i64)&ru,0);
  /* VmHWM from /proc/self/status: peak RSS of this process image only (ru_maxrss on Linux
     can carry over the parent's high-water mark across fork+execve) */
  long hwm=-1; { static char st[4096]; int fd=(int)sc3(2,(i64)"/proc/self/status",0,0);
    if(fd>=0){ long n=sc3(0,fd,(i64)st,sizeof st-1); fclose_(fd); if(n>0){ st[n]=0;
      for(long i=0;i+6<n;i++) if(st[i]=='V'&&st[i+1]=='m'&&st[i+2]=='H'&&st[i+3]=='W'&&st[i+4]=='M'){ long j=i+6,v=0; while(st[j]==' '||st[j]=='	') j++; while(st[j]>='0'&&st[j]<='9') v=v*10+(st[j++]-'0'); hwm=v; break; } } } }
  /* meta.txt */
  fd_out=fopen_w("meta.txt");
  os("trial "); ou(bestt); oc('\n');
  for(int l=0;l<25;l++){ os("lane "); ou(l); oc(' '); ox(KL[l]); oc('\n'); }
  os("varlanes 1 6 4 9 ; lane11 = u0^u1^K11 ; lane14 = u2^u3^K14\n");
  os("pd "); for(int i=0;i<4;i++){ ox(PD[i]); oc(i<3?' ':'\n'); }
  os("ninstr "); ou(ninstr); oc('\n');
  oflush(); fclose_(fd_out);
  /* ledger.txt + stdout */
  for(int pass=0;pass<2;pass++){
    fd_out= pass? 1 : fopen_w("ledger.txt");
    os("LS1 step ledger (256 lanes, one chain step, 8 rounds)\n");
    os("XOR "); ou(cnt[O_XOR]); oc('\n');
    os("AND "); ou(cnt[O_AND]); oc('\n');
    os("OR  "); ou(cnt[O_OR]); oc('\n');
    os("NOT "); ou(cnt[O_NOT]); os("  (row complements chosen pre-DCE: "); ou(nnot_rows); os(")\n");
    os("LOAD 0\nSTORE 0\nTOTAL "); ou(tot); oc('\n');
    os("feed NOTs 0 (digest polarity folded into the chain function: F(u)=H(m(u))^PD)\n");
    os("nodes created pre-DCE "); ou(pre); os(" ; nodes "); ou(nn); os(" ; linear forms "); ou(nform); oc('\n');
    os("max live values "); ou(maxlive); os(" ; registers used "); ou(maxreg); os(" (limit 2304)\n");
    os("constants trial "); ou(bestt); os(" of "); ou(ntr); oc('\n');
    os("generator peak RSS (VmHWM, this process image) "); ou(hwm); os(" KiB = "); ou(hwm*1024); os(" bytes (limit 1048576)\n");
    os("getrusage ru_maxrss "); ou(ru.maxrss); os(" KiB (Linux carries the parent's high-water mark across fork+execve)\n");
    oflush(); if(!pass) fclose_(fd_out);
  }
  if(maxreg>NREG) return 2;
  return 0;
}
```

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
  uint8_t m[128], d[32]; msg_of(u,m); sha3_256r(m,128,8,d);
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
      sha3_256r(m,len,24,d24); sha3_256r(m,len,8,d6);
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

## Appendix C. Programs of the measured checks (Section 7)

hrand_test.c (Section 7.2, tests A to D), proj_test.c (the proj-w256 trial at scale; it shares the loader and executor of hrand_test.c, of which only main differs and is shown), ideal_rho.py (the ideal-function control of rho-w22).

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
  fclose(f); f=fopen("prog.bin","rb"); prog=malloc(ninstr*5);
  if(fread(prog,5,ninstr,f)!=(size_t)ninstr) exit(2); fclose(f);
}
static void run_prog(void){
  const uint8_t *p=prog;
  for(long i=0;i<ninstr;i++,p+=5){
    u64 w=(u64)p[0]|(u64)p[1]<<8|(u64)p[2]<<16|(u64)p[3]<<24|(u64)p[4]<<32;
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

```c
/* proj_test: the proj-w256 trial at scale: NT trials of 256 random points and 8 chained full-width steps each;
   a trial succeeds when two of its 2,048 evaluated inputs have images agreeing on the 22 low bits. */
int main(int argc,char**argv){
  sm= argc>1? strtoull(argv[1],0,0) : 0x9e1f;
  long NT= argc>2? atol(argv[2]) : 16384;
  load();
  static uint32_t key[2048]; long succ=0;
  for(long tr=0;tr<NT;tr++){
    for(int j=0;j<256;j++) for(int k=0;k<4;k++) R[j].w[k]=rnd();
    for(int s=0;s<8;s++){ run_prog(); for(int t=0;t<256;t++){ uint32_t v=0; for(int j=0;j<22;j++) v|=(uint32_t)((R[j].w[t>>6]>>(t&63))&1)<<j; key[s*256+t]=v; } }
    qsort(key,2048,4,cmpu); int hit=0; for(int i=1;i<2048;i++) if(key[i]==key[i-1]){ hit=1; break; }
    succ+=hit;
  }
  double p=0.39337; /* 1-prod_{i<2048}(1-i/2^22) */
  printf("proj at scale: %ld trials, %ld successes = %.4f; model %.4f; z %.2f\n",NT,succ,(double)succ/NT,p,(succ-NT*p)/sqrt(NT*p*(1-p)));
  return 0;
}
```

```python
# Ideal-function control for rho-w22 (our own run, not organizer): the search of ls1.py rho_w with the same parameters
# (W=22, H=4, LC=128, U=3000, TB=400, 256 walks, starts rho+i, restarts, same event order), f replaced by a lazily
# sampled uniform random function on 22 bits. Prints the mean and quantiles of the steps to the first replayed pair.
import random, sys
W, H, LC, U, TB = 22, 4, 128, 3000, 400
mask = (1 << W) - 1


def trial(rng):
    fmap = {}
    def f(x):
        v = fmap.get(x)
        if v is None: v = fmap[x] = rng.getrandbits(W)
        return v
    c0 = 0
    while True:                                  # attempts
        rho = rng.getrandbits(W)
        pts = [(rho + l) & mask for l in range(256)]
        lid = list(range(256)); lst = [c0] * 256; nid = 256; table = {}
        c = c0
        while c - c0 < TB:
            c += 1
            pts = [f(x) for x in pts]
            events = sorted([(l, 1) for l in range(256) if pts[l] & ((1 << H) - 1) == 0] +
                            [(l, 2) for l in range(256) if c - lst[l] == LC and pts[l] & ((1 << H) - 1) != 0])
            for l, kind in events:
                if kind == 1:
                    x, ln = pts[l], c - lst[l]
                    if x in table:
                        ida, la = table[x]
                        if ida != lid[l]:
                            a, b = (rho + ida) & mask, (rho + lid[l]) & mask
                            for _ in range(abs(la - ln)):
                                if la > ln: a = f(a)
                                else: b = f(b)
                            if a != b:
                                for _ in range(min(la, ln) + 1):
                                    if f(a) == f(b): return c
                                    a, b = f(a), f(b)
                    else:
                        table[x] = (lid[l], ln)
                if nid >= U: break
                lid[l] = nid; lst[l] = c; pts[l] = (rho + nid) & mask; nid += 1
            if nid >= U: break
        c0 = c


rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
st = sorted(trial(rng) for _ in range(n))
m = sum(st) / n; sd = (sum((v - m) ** 2 for v in st) / (n - 1)) ** 0.5
print("ideal-function control: %d trials, mean steps %.3f (sd %.2f), median %d, 90%% %d, max %d" % (n, m, sd, st[n // 2], st[9 * n // 10], st[-1]))
```

## Appendix D. The other code (other8.py), its tests (other8_test.py) and their results

Run in the directory of prog.bin and meta.txt (`gen 512` output): `python3 other8.py build meta.txt` writes other.bin, pf.bin, data.bin and counts.txt; `python3 other8_test.py 8 7` runs the tests of Section 7.3. The straight-line block in code memory is prog.bin followed by pf.bin, in front of instruction 27 (label `loop`).

### D.1 other8.py: the other code, the machine and the counts

```python
#!/usr/bin/env python3
# other8.py - the non-straight-line code of LS1R8b (setup, loop control, hit handler, DP handler, restart, deadline
# scan, replay, final output), written as real instructions of the machine of proof.md Section 3.5, plus the machine
# (an interpreter that executes the emitted bytes) and the counting of the operations.
#
#   python3 other8.py build [meta.txt]    writes other.bin (the 32-byte instructions), pf.bin (the 15 prefilter ORs, 5 bytes
#                                          each), data.bin (the 16-word data image from meta.txt) and counts.txt (instruction
#                                          counts and the operation count of every routine, read from the emitted code)
#   other8_test.py                         routine tests and end-to-end runs of the emitted program (reduced width)
#
# Machine (collision-frontier-v5 256-bit word RAM, the declared register file of 2,192 registers R0..R2191):
#   every instruction below costs one word operation, except PERM, which costs one unit (2168 operations, the model's
#   rule: one selected-round sponge permutation is one unit).  Straight-line instructions (5 bytes: XOR AND OR NOT on
#   registers) cost one operation each.  Other instructions are 32 bytes: op(1) d(2) a(2) b(2) 0(1) imm(24, 192 bits).
#   Words are 256 bits, arithmetic is mod 2^256, shifts take amount R[b] & 255 (or an immediate), compares give 0 or 1,
#   a conditional branch tests a register for zero and is always the instruction right after the compare that set it
#   (audited below), memory M[] is word addressed with address R[a] + imm, PERM a applies Keccak-f rounds 0..7 to the
#   25 lanes in R[a]..R[a+6] (lane l = bits 64 (l mod 4) .. +63 of word R[a + l div 4]).
#   The straight-line block sits in code memory in front of instruction SLPOS: it is entered by fall-through or by a
#   jump to it, has no branches, and control leaves it by fall-through into instruction SLPOS.
import sys, struct, hashlib, os

M256 = (1 << 256) - 1
M64 = (1 << 64) - 1
UNIT = 2168

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
    """Pm: S (table words), U (trail limit), SB (slot bits), Lc, Tb, HMAX, DPLO, PFLO, PFN, WTEST (None or width)."""
    S, U, SB, Lc, Tb, HMAX = Pm['S'], Pm['U'], Pm['SB'], Pm['Lc'], Pm['Tb'], Pm['HMAX']
    DPLO, PFLO, PFN, WT = Pm['DPLO'], Pm['PFLO'], Pm['PFN'], Pm.get('WTEST')
    assert (1 << SB) <= 2 * S and S % 8 == 0 and PFLO > DPLO + 1
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
    A.movi(NXT, Lc)
    # ---------------- the loop: the straight line (SLPOS) then the tests ----------------
    A.label('loop')
    A.jeq(PF, ONES, 'cont')                                  # prefilter test (2)
    # ---------------- hit: some walk has planes PFLO..PFLO+PFN-1 zero ----------------
    A.label('hit')
    A.addi(H, H, 1); A.jlti(H, HMAX + 1, 'h1'); A.halt(10); A.label('h1')      # hit counter and abort (F5)
    A.or_(SS, DPLO, DPLO + 1)
    for j in range(DPLO + 2, PFLO): A.or_(SS, SS, j)         # OR of the planes DPLO..PFLO-1
    A.or_(DPM, PF, SS); A.not_(DPM, DPM)                     # DPM: walks with planes DPLO..255 zero
    A.addi(C1, C, 1)                                         # steps completed including this one
    A.label('dpl')
    A.jeqi(DPM, 0, 'cont')
    A.label('dp1')                                           # ---- one DP walk: l := lowest set bit of DPM ----
    A.movi(L, 0); A.mov(X, DPM)
    for i, sh in enumerate((128, 64, 32, 16, 8, 4, 2, 1)):
        A.andi(Y, X, (1 << sh) - 1); A.jnei(Y, 0, 'ct%d' % i); A.shri(X, X, sh); A.addi(L, L, sh); A.label('ct%d' % i)
    A.subi(Y, DPM, 1); A.and_(DPM, DPM, Y)                   # clear that bit
    A.label('gather')                                        # ACC := the 256-bit point of walk l (bit j = plane j, bit l)
    A.shr(ACC, 0, L); A.andi(ACC, ACC, 1)
    for j in range(1, 256):
        A.shr(TT, j, L); A.andi(TT, TT, 1); A.shli(TT, TT, j); A.or_(ACC, ACC, TT)
    A.label('record')
    A.andi(REC, ACC, (1 << 122) - 1); A.ld(ID, L, LID); A.shli(ID, ID, 122); A.ld(STV, L, LST); A.sub(STV, C1, STV)
    A.shli(STV, STV, 137); A.or_(REC, REC, ID); A.or_(REC, REC, STV)
    A.andi(SLOT, ACC, (1 << SB) - 1); A.jlti(SLOT, S, 'sl_ok'); A.subi(SLOT, SLOT, S); A.label('sl_ok')
    A.label('probe')
    A.ld(TR, SLOT, 0)
    A.jeqi(TR, 0, 'empty')
    A.xor(X, TR, REC); A.andi(X, X, (1 << 122) - 1); A.jeqi(X, 0, 'match')
    A.addi(SLOT, SLOT, 1); A.jnei(SLOT, S, 'probe')
    A.movi(SLOT, 0); A.jmp('probe')
    A.label('empty')
    A.st(SLOT, 0, REC); A.mov(LV, C1); A.jal(LR, 'restart'); A.jmp('dpl')
    # ---------------- end of iteration ----------------
    A.label('cont')
    A.addi(C, C, 1); A.jne(C, NXT, 'loop')                   # counter (3 with the compare and branch)
    # ---------------- deadline ----------------
    A.label('dl')
    A.jnei(C, Tb, 'dl1'); A.halt(12); A.label('dl1')
    A.movi(MN, Tb); A.movi(L, 0)
    A.label('scan')                                          # restart the walks at the cap; nxt := min(Tb, min LST + Lc)
    A.ld(V, L, LST); A.sub(X, C, V); A.jnei(X, Lc, 'noexp')
    A.mov(LV, C); A.jal(LR, 'restart'); A.mov(V, C)
    A.label('noexp')
    A.addi(E, V, Lc); A.jge(E, MN, 'nomin'); A.mov(MN, E); A.label('nomin')
    A.addi(L, L, 1); A.jlti(L, 256, 'scan')
    A.label('dl_end')
    A.mov(NXT, MN); A.jmp('loop')
    # ---------------- restart(l) and the insertion of a point into lane l ----------------
    A.label('restart')                                       # in: L, LV; link LR
    A.jnei(IDN, U, 'rs1'); A.halt(11); A.label('rs1')
    A.st(L, LID, IDN); A.st(L, LST, LV); A.add(NP, RHO, IDN); A.addi(IDN, IDN, 1)
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
    A.label('match')                                         # in: TR (stored record), REC (new record), L
    A.shri(LA, TR, 137); A.shri(LB, REC, 137); A.shri(X, TR, 122); A.andi(X, X, 0x7FFF); A.ld(Y, L, LID)
    A.add(P, RHO, X); A.add(Q, RHO, Y)
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


def sl_bytes(prog, PFLO, PFN):
    """prog.bin + the prefilter: PF := OR of planes PFLO..PFLO+PFN-1 (PFN-1 ORs), 5-byte instructions"""
    out = bytearray(prog)
    def w(code, d, a, b): return (code | d << 3 | a << 15 | b << 27).to_bytes(5, 'little')
    out += w(2, PF, PFLO, PFLO + 1)
    for j in range(PFLO + 2, PFLO + PFN): out += w(2, PF, PF, j)
    return bytes(out)


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


def F_plain(u, KL, PD, rounds=8):
    d = sha3_256_r(m_of(u, KL), rounds)
    pd = PD[0] | PD[1] << 64 | PD[2] << 128 | PD[3] << 192
    return int.from_bytes(d, 'little') ^ pd


# ---------------- the machine ----------------
def compile_sl(slb, nprog, hookW=None):
    """Python function executing the 5-byte block on a register list (the planes 0..255 and PF are the only live ends).
    hookW (test builds only): set the planes hookW..255 to zero after the first nprog instructions (the F of the program
    truncated to hookW bits, as in the organizer experiment rho-w22)."""
    src = ['def sl(R):']
    for j in range(256): src.append(' r%d=R[%d]' % (j, j))
    for i in range(0, len(slb), 5):
        if i // 5 == nprog and hookW:
            for j in range(hookW, 256): src.append(' r%d=0' % j)
        w = int.from_bytes(slb[i:i + 5], 'little')
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
                lanes = keccak_f(lanes[:25], 8)
                lanes += [0, 0, 0]
                for w in range(7): R[a + w] = sum(lanes[4 * w + i] << (64 * i) for i in range(4))
                s.units += 1
            elif op == HALT:
                s.halt = imm; return None
            else: raise Exception('bad op')


# ---------------- counting ----------------
FULL = dict(S=19000, U=19000, SB=15, Lc=17 << 114, Tb=67868324 << 94, HMAX=358327248618091250208476601149030401,
            DPLO=142, PFLO=240, PFN=16)


def counts(A, Pm):
    """Worst-case operation counts of every routine, from the lengths of the emitted code (an instruction is one
    operation, PERM is UNIT).  seg(a, b) = number of instructions between two labels."""
    I = A.lab
    def seg(a, b): return I[b] - I[a]
    S, U, Lc = Pm['S'], Pm['U'], Pm['Lc']
    c = {}
    c['n_instr'] = len(A.ins)
    c['setwalk'] = seg('setwalk', 'sw_end') + 1                                  # with the return
    c['restart'] = (seg('restart', 'rs1') - 1) + seg('rs1', 'setwalk') + c['setwalk']   # the cap check passes (no HALT)
    c['restart_halt'] = seg('restart', 'rs1') - 1 + 1                           # the last call: compare, branch not taken, HALT
    c['hit'] = (seg('hit', 'h1') - 1) + seg('h1', 'dpl') + 2                     # per processed hit, no DP walk
    c['ctz_clear'] = seg('dp1', 'gather')
    c['gather'] = seg('gather', 'record')
    c['record_slot'] = seg('record', 'sl_ok')
    c['probe_slot'] = seg('probe', 'empty') - 2                                  # per non-matching occupied slot
    c['probe_wrap'] = 2
    c['probe_end'] = 3                                                           # load, test, branch at the empty slot
    c['empty_tail'] = seg('empty', 'cont')                                       # store, move, call, jump back
    c['dp_fixed'] = 2 + c['ctz_clear'] + c['gather'] + c['record_slot'] + c['probe_end'] + c['probe_wrap'] + c['empty_tail']
    c['dp_max'] = c['dp_fixed'] + c['probe_slot'] * (S - 1)                      # at most S - 1 occupied slots passed
    c['dl_event'] = (seg('dl', 'dl1') - 1) + seg('dl1', 'scan') + 256 * (seg('scan', 'noexp') - 3 + seg('noexp', 'dl_end')) + seg('dl_end', 'restart')
    c['dl_expired_extra'] = 3                                                    # move, call, move (the restart body is counted apart)
    c['dl_final'] = seg('dl', 'dl1') - 1 + 1                                     # c = Tb: compare, branch not taken, HALT
    c['e_eval'] = seg('evalF', 'outm') - 1 + UNIT                                # one evaluation of F with the permutation, with the return
    c['e_outm'] = seg('outm', 'match')                                           # the message builder, with the return
    e = c['e_eval']
    c['replay_iter'] = 13 + 2 * e                                                # one lock-step iteration (not found)
    # success after k lock-step iterations: 9 entry + 2 + 2 (alignment loop test) + n (7 + e) + 2 (p = q test) + (k - 1) (13 + 2e)
    #   + (9 + 2e) + 67 (two message builds, 8 stores, HALT); exhaustion: ... + m (13 + 2e) + 3.  Largest at n = 0, m = k = Lc:
    c['replay_const'] = 9 + 2 + 2 + 2 + 9 + 67 - 13
    c['replay_max'] = c['replay_iter'] * Lc + c['replay_const']
    c['setup'] = seg('start', 'clr') + (S // 8) * 11 + 1 + 256 * (7 + c['setwalk']) + 1
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
        out.append('prefilter: %d instructions x 5 bytes (pf.bin sha256 %s); the straight-line block = prog.bin then pf.bin, %d instructions, sits in front of instruction %d (label loop)' %
                   (FULL['PFN'] - 1, hashlib.sha256(open('pf.bin', 'rb').read()).hexdigest(), os.path.getsize('prog.bin') // 5 + FULL['PFN'] - 1, I['loop']))
        out.append('data image: 16 words x 32 bytes = 512 bytes (data.bin sha256 %s): KW[0..6], PD, 8 output words' % hashlib.sha256(open('data.bin', 'rb').read()).hexdigest())
        out.append('memory map (words): TAB 0..%d, LID %d..%d, LST %d..%d, data %d..%d' % (FULL['S'] - 1, FULL['S'], FULL['S'] + 255, FULL['S'] + 256, FULL['S'] + 511, FULL['S'] + 512, FULL['S'] + 527))
        out.append('routine entry points (instruction index): ' + ', '.join('%s %d' % (k, I[k]) for k in ('start', 'loop', 'hit', 'dpl', 'dp1', 'gather', 'record', 'probe', 'empty', 'cont', 'dl', 'scan', 'restart', 'setwalk', 'evalF', 'outm', 'match', 'end')))
        for k, v in c.items(): out.append('%-18s %d' % (k, v))
        bybase = {}
        for x in A.ins: bybase[NAMES[x[0]]] = bybase.get(NAMES[x[0]], 0) + 1
        out.append('static opcode mix: ' + ' '.join('%s %d' % kv for kv in sorted(bybase.items(), key=lambda kv: -kv[1])))
        out.append('highest register named: %d (file of %d)' % (max(max(x[1], x[2], x[3]) for x in A.ins), NREGS))
        open('counts.txt', 'w').write(chr(10).join(out) + chr(10))
        print(chr(10).join(out))
    else:
        print(__doc__ if __doc__ else 'usage: other8.py build [meta.txt]')


if __name__ == '__main__':
    build_cli(sys.argv)
```

### D.2 Output of `python3 other8.py build meta.txt`

```
other code: 2656 instructions x 32 bytes = 84992 bytes (other.bin sha256 baaae310be054751c5180084c3997e6379a80a7b8248536ee0d16697489f7790)
prefilter: 15 instructions x 5 bytes (pf.bin sha256 7d01825e1754a115fd593386cbd91d120baff96ff46f5ea6472a7326662ddfbc); the straight-line block = prog.bin then pf.bin, 42497 instructions, sits in front of instruction 27 (label loop)
data image: 16 words x 32 bytes = 512 bytes (data.bin sha256 4ffde65da18baeac92c27169e94d3af98a89e6f0877ec78bf399f27130b2ffa7): KW[0..6], PD, 8 output words
memory map (words): TAB 0..18999, LID 19000..19255, LST 19256..19511, data 19512..19527
routine entry points (instruction index): start 0, loop 27, hit 29, dpl 133, dp1 135, gather 179, record 1201, probe 1213, empty 1225, cont 1229, dl 1232, scan 1237, restart 1253, setwalk 1260, evalF 2543, outm 2573, match 2600, end 2656
n_instr            2656
setwalk            1283
restart            1289
restart_halt       3
hit                105
ctz_clear          44
gather             1022
record_slot        12
probe_slot         10
probe_wrap         2
probe_end          3
empty_tail         4
dp_fixed           1089
dp_max             191079
dl_event           2822
dl_expired_extra   3
dl_final           3
e_eval             2197
e_outm             27
replay_iter        4407
replay_const       78
replay_max         1556006753378283004407505017955361488974
setup              356374
static opcode mix: OR 611 ANDI 530 SHRI 272 SHLI 267 AND 257 SHL 257 SHR 256 ST 21 MOV 19 EQI 18 XOR 18 ADDI 17 BNZ 15 LDA 15 BZ 14 MOVI 12 JAL 9 JMP 6 LTI 5 HALT 5 SUBI 5 LD 5 ADD 4 EQ 4 SUB 4 NOT 3 JR 3 LT 2 RND 1 PERM 1
highest register named: 2190 (file of 2192)
```

### D.3 other8_test.py

```python
#!/usr/bin/env python3
# other8_test.py - checks of the emitted program of other8.py.
#   1. routine tests: each routine run on constructed states; its executed operations must equal the counted worst case
#   2. end-to-end runs of the whole emitted program (setup, loop, hit handler, DP handler, restart, deadlines, replay,
#      output) at reduced width: the straight line of prog.bin is truncated to W bits after every step (test hook), the
#      replay's F is truncated alike (one extra ANDI in evalF, test builds only); the output pair is checked with an
#      independent Keccak.  The totals of every run are compared with the counted bounds.
#   usage: other8_test.py [nseeds] [pyseed]
import random, sys, time
from other8 import *

KL, PD = read_meta('meta.txt')
prog = open('prog.bin', 'rb').read(); NPROG = len(prog) // 5
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
    vm = VM().load(code, sl, len(slb) // 5, A.lab['loop'], S + 528, data, S + 512, random.Random(seed))
    return A, vm, len(slb) // 5


def nonsl_ops(vm):
    return sum(vm.cnt) - vm.units + vm.units * UNIT


def ops_of(vm, f):
    a = nonsl_ops(vm); f(); return nonsl_ops(vm) - a


# ------------------------------------------------------------------ 1. routine tests
def sl_test():
    """the straight line + prefilter as compiled from the 5-byte bytes: 2 x 256 points, every lane, 3 chained steps, against F_plain"""
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
    S = Pm['S']; LID, LST = S, S + 256
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
    check(n == c['restart'], 'restart ops %d vs %d' % (n, c['restart']))
    check(vm.M[LID + 7] == 4321 and vm.M[LST + 7] == 99 and R[IDN] == 4322, 'restart effect')
    R[IDN] = Pm['U']; R[LR] = END
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
    check(vm2.R[IDN] == 256 and vm2.R[NXT] == Pm['Lc'] and vm2.R[C] == 0 and vm2.R[H] == 0 and vm2.R[ONES] == M256, 'setup state')
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
    # DP handler worst path: walk 255 alone at a DP; k occupied non-matching slots in the probe path, with and without wrap
    for k, wrap in ((0, False), (5, False), (7, True)):
        A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
        for j in range(256): R[j] = M256
        for j in range(Pm['DPLO'], 256): R[j] = M256 ^ (1 << 255)
        R[PF] = M256 ^ (1 << 255); R[ONES] = M256; R[H] = 0; R[C] = 777; R[RHO] = 31337; R[IDN] = 5000; R[LR] = END
        M[LST + 255] = 700; M[LID + 255] = 255
        val = (S - 3) if wrap else (S + 100)                 # low 15 bits of the point: slot S - 3, or S + 100 -> 100 after the subtraction
        for j in range(15): R[j] = (R[j] & ~(1 << 255)) | (((val >> j) & 1) << 255)
        pt = sum(((R[j] >> 255) & 1) << j for j in range(256))
        slot = (S - 3) if wrap else 100
        for i in range(k): M[(slot + i) % S] = (1 << 200) | ((i + 1) << 122)
        n = ops_of(vm, lambda: vm.run(I['hit'], stop=I['cont']))
        exp = c['hit'] + c['dp_fixed'] + c['restart'] + c['probe_slot'] * k - (0 if wrap else c['probe_wrap']) - (1 if wrap else 0)
        check(n == exp, 'DP worst (k=%d wrap=%s) ops %d vs %d (halt %s)' % (k, wrap, n, exp, vm.halt))
        rec = M[(slot + k) % S]
        check((rec & ((1 << 122) - 1)) == (pt & ((1 << 122) - 1)) and (rec >> 122) & 0x7FFF == 255 and rec >> 137 == 78, 'DP record')
        check(M[LID + 255] == 5000 and M[LST + 255] == 778 and R[IDN] == 5001, 'DP restart')
    # deadline scan: no expiry, strictly decreasing LST (the min is updated every walk); expiry of three walks
    A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
    R[C] = 10 ** 6; R[RHO] = 5; R[IDN] = 1000; R[LR] = END
    for l in range(256): M[LST + l] = 10 ** 6 - 1000 - l
    n = ops_of(vm, lambda: vm.run(I['dl'], stop=I['loop']))
    check(n == c['dl_event'], 'deadline ops %d vs %d' % (n, c['dl_event']))
    check(R[NXT] == 10 ** 6 - 1000 - 255 + Pm['Lc'], 'deadline nxt')
    A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
    R[C] = Pm['Lc'] + 50; R[RHO] = 5; R[IDN] = 1000; R[LR] = END
    for l in range(256): M[LST + l] = 1000 + l
    for l in (3, 50, 77): M[LST + l] = 50
    n = ops_of(vm, lambda: vm.run(I['dl'], stop=I['loop']))
    exp = c['dl_event'] - 255 + 3 * (c['dl_expired_extra'] + c['restart'])      # only the first walk lowers the running minimum
    check(n == exp, 'deadline expiry ops %d vs %d' % (n, exp))
    check(all(M[LST + l] == Pm['Lc'] + 50 for l in (3, 50, 77)) and R[IDN] == 1003, 'deadline restarts')


def replay_tests(ntrials=60):
    """the replay on synthetic pairs of trails of the 12-bit truncation of F: alignment, lock step, found / p = q / exhausted"""
    Pm = dict(S=400, U=400, SB=9, Lc=500, Tb=900, HMAX=10 ** 9, DPLO=2, PFLO=8, PFN=4, WTEST=12)
    mask = (1 << 12) - 1
    Ft = lambda u: F_plain(u, KL, PD) & mask
    A, vm0, nsl = mk(Pm); I = A.lab; c = counts(A, Pm); e = c['e_eval']; END = I['end']; S = Pm['S']
    seen = {1: 0, 13: 0}
    for t in range(ntrials):
        A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
        rho = random.getrandbits(256); a, b = random.sample(range(256, 400), 2)
        p0, q0 = (rho + a) & M256, (rho + b) & M256
        sp, tq = [p0], [q0]
        for _ in range(70): sp.append(Ft(sp[-1])); tq.append(Ft(tq[-1]))
        best = None
        for i in range(61):
            for j in range(61):
                if sp[i] == tq[j] and (best is None or i + j < best[0] + best[1]): best = (i, j)
        if best is None: continue
        i, j = best; u = random.randrange(0, 4)
        la, lb = i + u, j + u
        if la < 1 or lb < 1: continue
        endpt = sp[la]
        assert endpt == tq[lb]
        R[RHO] = rho; R[LR2] = END; R[L] = 9; M[S + 9] = b
        R[TR] = (endpt & ((1 << 122) - 1)) | a << 122 | la << 137
        R[REC] = (endpt & ((1 << 122) - 1)) | b << 122 | lb << 137
        ops = ops_of(vm, lambda: vm.run(I['match']))
        n_, m_ = abs(la - lb), min(la, lb)
        if i == 0 or j == 0:
            check(vm.halt == 13, 'replay p=q expected halt 13, got %s (i %d j %d u %d)' % (vm.halt, i, j, u))
            pred = 9 + 2 + n_ * (7 + e) + 2 + 2 + 1
            check(ops == pred, 'replay p=q ops %d vs %d' % (ops, pred)); seen[13] += 1
        else:
            check(vm.halt == 1, 'replay expected halt 1, got %s (i %d j %d u %d la %d lb %d)' % (vm.halt, i, j, u, la, lb))
            kk = vm.cnt[I['lloop']]
            pred = 9 + 2 + n_ * (7 + e) + 2 + 2 + (kk - 1) * (13 + 2 * e) + (9 + 2 * e) + 67
            check(ops == pred, 'replay found ops %d vs %d (k %d)' % (ops, pred, kk))
            out = M[S + 520:S + 528]
            ma = b''.join(out[x].to_bytes(32, 'little') for x in range(4)); mb = b''.join(out[4 + x].to_bytes(32, 'little') for x in range(4))
            ua = int.from_bytes(ma, 'little'); ub = int.from_bytes(mb, 'little')
            check(ma != mb and (int.from_bytes(sha3_256_r(ma, 8), 'little') & mask) == (int.from_bytes(sha3_256_r(mb, 8), 'little') & mask), 'replay pair')
            check(kk == m_ - u, 'replay lock-step iterations %d vs %d' % (kk, m_ - u))
            seen[1] += 1
    # exhausted: two different points whose images never agree within m steps
    A, vm, nsl = mk(Pm); R = vm.R; END = I['end']
    R[P] = 3; R[Q] = 4; R[MM] = 0; R[LR2] = END
    ops = ops_of(vm, lambda: vm.run(I['lock']))
    check(vm.halt == 13 and ops == 2 + 2 + 1, 'exhausted m=0 ops %d' % ops)
    A, vm, nsl = mk(Pm); R = vm.R
    R[P] = 5; R[Q] = 5; R[MM] = 3; R[LR2] = END
    ops = ops_of(vm, lambda: vm.run(I['lock']))
    check(vm.halt == 13 and ops == 3, 'p==q ops %d' % ops)
    print('replay tests: found %d, p=q %d' % (seen[1], seen[13]))


# ------------------------------------------------------------------ 2. end-to-end
def check_pair(vm, Pm, W):
    S = Pm['S']; out = vm.M[S + 520:S + 528]
    ma = b''.join(out[i].to_bytes(32, 'little') for i in range(4)); mb = b''.join(out[4 + i].to_bytes(32, 'little') for i in range(4))
    da, db = sha3_256_r(ma, 8), sha3_256_r(mb, 8)
    mask = (1 << W) - 1
    return ma != mb and len(ma) == 128 and (int.from_bytes(da, 'little') & mask) == (int.from_bytes(db, 'little') & mask)


def e2e(name, Pm, seeds, expect=None, W=26):
    A = None; res = {}
    for sd in seeds:
        A, vm, nsl = mk(Pm, sd, True)
        t0 = time.time(); vm.run(0); dt = time.time() - t0
        c = counts(A, Pm); I = A.lab; cnt = vm.cnt
        steps = vm.slsteps
        hits = cnt[I['hit']]; dps = cnt[I['dp1']]; rest = cnt[I['rs1']]; dl = cnt[I['dl']]
        # exact group checks
        calls = cnt[I['setwalk']]
        check(sum(cnt[I['setwalk']:I['sw_end'] + 1]) == (c['setwalk']) * calls, 'setwalk group %d calls' % calls)
        check(sum(cnt[I['gather']:I['record']]) == c['gather'] * dps, 'gather group')
        check(cnt[I['loop']] == steps and cnt[I['cont']] in (steps, steps - 1), 'loop counts')
        # totals against the counted bounds
        nonsl = nonsl_ops(vm)
        replay_ops = sum(cnt[I['evalF']:I['end']]) - vm.units + vm.units * UNIT
        bound = (c['setup'] + 5 * steps + hits * c['hit'] + dps * c['dp_max'] + (rest + 1) * (c['restart'] + 3)
                 + dl * c['dl_event'] + c['dl_final'] + c['restart_halt'] + c['replay_max'])
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
                pred = 9 + 2 + n_ * (7 + e) + 2 + 2 + (k - 1) * (13 + 2 * e) + (9 + 2 * e) + 67 + 0
                check(replay_ops == pred, '%s seed %d: replay ops %d vs %d (la %d lb %d k %d)' % (name, sd, replay_ops, pred, la, lb, k))
            check(replay_ops <= c['replay_iter'] * max(la, lb) + c['replay_const'], 'replay bound')
        print('%-10s seed %3d halt %2s steps %5d hits %5d dp %4d restarts %4d deadlines %4d replay_ops %7d  total %d' %
              (name, sd, vm.halt, steps, hits, dps, rest, dl, replay_ops, nonsl + steps * nsl))
        if expect is not None: check(vm.halt in expect, '%s seed %d: halt %s not in %s' % (name, sd, vm.halt, expect))
    return res


def main():
    ns = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    routine_tests()
    replay_tests()
    print('routine tests done, failures so far:', len(FAILS))
    base = dict(S=3000, U=3000, SB=12, Lc=17 << 8, Tb=3000, HMAX=10 ** 9, DPLO=18, PFLO=22, PFN=4, WTEST=26)
    seeds = list(range(1, ns + 1))
    e2e('base', base, seeds, expect=(1, 13))
    # width 32, DP of 10 bits, prefilter of 6 planes; trails of mean length 1024 steps against a cap of 400: deadline restarts
    w32 = dict(S=3000, U=3000, SB=12, Lc=400, Tb=60000, HMAX=10 ** 9, DPLO=22, PFLO=26, PFN=6, WTEST=32)
    e2e('w32cap', w32, seeds[:3], expect=(1, 11, 12, 13), W=32)
    small = dict(base, S=400, U=400, SB=9, Lc=2000, Tb=4000)             # small table: long probe runs, wraps; U exhaustion possible
    e2e('smalltab', small, seeds, expect=(1, 11, 12, 13))
    abort = dict(base, HMAX=3)                                            # hit counter abort
    e2e('abort', abort, seeds[:3], expect=(10,))
    tb = dict(base, Lc=3, Tb=5)                                           # Tb reached
    e2e('tb5', tb, seeds[:2], expect=(12,))
    uex = dict(base, S=264, U=264, SB=8, Tb=100000)                        # trail limit reached
    e2e('u264', uex, seeds[:3], expect=(11, 1, 13))
    print('checks run: %d, failures: %d' % (NCHK[0], len(FAILS)))
    return len(FAILS)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
```

### D.4 Output of `python3 other8_test.py 8 7` (run twice, identical)

```
replay tests: found 31, p=q 0
routine tests done, failures so far: 0
base       seed   1 halt  1 steps   149 hits   149 dp  146 restarts  145 deadlines    0 replay_ops  330825  total 7342226
base       seed   2 halt  1 steps    65 hits    65 dp   67 restarts   66 deadlines    0 replay_ops   83850  total 3338058
base       seed   3 halt  1 steps    49 hits    49 dp   55 restarts   54 deadlines    0 replay_ops  145585  total 2691437
base       seed   4 halt  1 steps   161 hits   161 dp  166 restarts  165 deadlines    0 replay_ops  328601  total 7897339
base       seed   5 halt  1 steps   149 hits   149 dp  151 restarts  150 deadlines    0 replay_ops   50784  total 7073991
base       seed   6 halt  1 steps   167 hits   167 dp  167 restarts  166 deadlines    0 replay_ops  238196  total 8064333
base       seed   7 halt  1 steps   103 hits   103 dp  103 restarts  102 deadlines    0 replay_ops  216121  total 5170622
base       seed   8 halt  1 steps    67 hits    67 dp   82 restarts   81 deadlines    0 replay_ops  183072  total 3557821
w32cap     seed   1 halt  1 steps   586 hits   574 dp  115 restarts  335 deadlines   34 replay_ops  709965  total 26594859
w32cap     seed   2 halt  1 steps   771 hits   760 dp  180 restarts  415 deadlines   51 replay_ops 1490329  total 35455379
w32cap     seed   3 halt  1 steps  1772 hits  1748 dp  422 restarts 1251 deadlines  347 replay_ops  319789  total 78932019
smalltab   seed   1 halt 11 steps   147 hits   147 dp  145 restarts  144 deadlines    0 replay_ops       0  total 6921143
smalltab   seed   2 halt  1 steps    65 hits    65 dp   67 restarts   66 deadlines    0 replay_ops   83850  total 3334540
smalltab   seed   3 halt  1 steps    49 hits    49 dp   55 restarts   54 deadlines    0 replay_ops  145585  total 2687879
smalltab   seed   4 halt 11 steps   145 hits   145 dp  145 restarts  144 deadlines    0 replay_ops       0  total 6835699
smalltab   seed   5 halt 11 steps   142 hits   142 dp  145 restarts  144 deadlines    0 replay_ops       0  total 6708447
smalltab   seed   6 halt 11 steps   141 hits   141 dp  145 restarts  144 deadlines    0 replay_ops       0  total 6666109
smalltab   seed   7 halt  1 steps   103 hits   103 dp  103 restarts  102 deadlines    0 replay_ops  216121  total 5167173
smalltab   seed   8 halt  1 steps    67 hits    67 dp   82 restarts   81 deadlines    0 replay_ops  183072  total 3554280
abort      seed   1 halt 10 steps     4 hits     4 dp    5 restarts    5 deadlines    0 replay_ops       0  total 516198
abort      seed   2 halt 10 steps     4 hits     4 dp    5 restarts    5 deadlines    0 replay_ops       0  total 516202
abort      seed   3 halt 10 steps     4 hits     4 dp    7 restarts    7 deadlines    0 replay_ops       0  total 520942
tb5        seed   1 halt 12 steps     5 hits     5 dp    8 restarts  261 deadlines    3 replay_ops       0  total 897818
tb5        seed   2 halt 12 steps     5 hits     5 dp    8 restarts  261 deadlines    3 replay_ops       0  total 897833
u264       seed   1 halt 11 steps     8 hits     8 dp    9 restarts    8 deadlines    0 replay_ops       0  total 690629
u264       seed   2 halt 11 steps     6 hits     6 dp    9 restarts    8 deadlines    0 replay_ops       0  total 605639
u264       seed   3 halt 11 steps     7 hits     7 dp    9 restarts    8 deadlines    0 replay_ops       0  total 648154
checks run: 336, failures: 0
```
