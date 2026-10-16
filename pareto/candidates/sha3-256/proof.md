# Full SHA3-256 (24 rounds): distinguished-point collision search with a linear-structure message embedding on a 1,024-register machine with every transfer charged, time_log2 124.85522

## 1. Claim

Target `sha3-256-r24-prefix-v1` (the Pareto lane sha3-256, round count 24 = the full Keccak-f[1600]; target profile, baseline `sha3-256-r24-nominal-v2` and unit read from the organizer contract: `pareto_candidate.py --family sha3-256 --rounds 24 --show-contract`, reference_operation_cost 6504 = 24 x 271). This is SHA3-256 (FIPS 202) with Keccak-f rounds 0 to 23 in the single permutation call, zero initial state, rate 136 bytes, suffix 0x06 with pad10*1, and the full 256-bit digest. The algorithm outputs two distinct 128-byte one-block messages with equal complete digests (an ordinary collision).

| Quantity | Value |
|---|---|
| time_log2 (collision-frontier-v5; unit 6504 word operations; rounded up) | 124.85522 (Sections 3 and 4, integer certificate in Appendix A) |
| memory | at most 1,028,576 bytes <= 2^20 (log2 19.9722), memory_log2_bytes = 20 (Section 6) |
| success probability | at least 0.39 for one attempt, a probability over the random word rho for the fixed target, under the declared premise H_rand (Section 5) |
| preprocessing | `gen 512` and `gen_s24ls`, charged 513 x 2^32 + 512 x 2^10 + 2^34 operations; preprocessing_log2 = 29 (Section 3.6); no advice |

The method is a distinguished-point search (van Oorschot-Wiener) on a chain function F with 256 walks per step, run bit-sliced: one step of the program evaluates F for 256 walks at once. Its parts:

1. **The message embedding** (Section 2). The 256-bit point is placed in six message lanes so that round 0 and the theta step of round 1 are affine in the point (a one-round linear structure of Guo, Liu and Song, 2016); that part of the step is one affine map of 2,200 operations.
2. **The step program** (Section 3), printed by a C generator and executed: rounds 1 to 22 are one code body per buffer direction (GB GA repeated eleven times); chi is computed with stored polarities and no NOT, in 10 operations for a row whose plan reuses a finished output of the same row (Section 3.1).
3. **The machine** (Section 3.2, declared convention H_machine): a register file of **1,024 words** of 256 bits; every load, store and register move is an instruction and is charged; code is counted at **32 bytes per instruction**.
4. **The search** (Section 4): distinguished points of 114 zero bits, a table of 5,847 words with three 85-bit records per word (key, used bit, trail number; no length field), the length of a stored trail rebuilt by replaying it when its record is matched, the replay of the two merging trails with a looped one-walk program of F of 5,562 operations, all parameters fixed (Lc = 17 x 2^114 - 2, U = 17,540, Tb = 16965265 x 2^96).
5. **The bound** (Section 5): success at least 0.39 in the random-function model, computed exactly, and the transfer premise H_rand.

Declared heuristics (claim.json): H_rand (Section 5), the one score-critical premise; H_machine (Section 3.2), a supporting declared convention. Everything else in the time, memory and success bound is counted or proved here.

## 2. The function F and the encoding

Let u be a 256-bit point with little-endian 64-bit lanes u0, u1, u2, u3. The message m(u) has 128 bytes, the 16 lanes 0 to 15 of the absorbed state (lane index x + 5y):

- lane 1 = u0, lane 6 = u1, lane 11 = u0 xor u1 xor K11 (column x = 1, rows y = 0, 1, 2);
- lane 4 = u2, lane 9 = u3, lane 14 = u2 xor u3 xor K14 (column x = 4, rows y = 0, 1, 2);
- every other lane l in 0..15 holds the constant K_l (below).

With the SHA3 padding, byte 128 is 0x06 and byte 135 is 0x80. The message is one absorbed block, lane 16 = 0x8000000000000006, and lanes 17 to 24 are zero. Rounds 0 to 23 are applied, and the digest is lanes 0 to 3 of the result (32 bytes). Define

    F(u) = SHA3-256-r24(m(u)) xor PD

where PD is a fixed 256-bit mask: the stored polarity of the four output lanes of the program (Section 3.1), with the round-23 constant folded in. The map u -> m(u) is injective (lanes 1, 6, 4, 9 are u). Hence F(a) = F(b) with a != b gives two distinct messages m(a), m(b) with equal complete digests. XOR with a fixed mask is a bijection of the range, so F is a fixed function from 256 bits to 256 bits like the plain digest map.

Constants (hexadecimal). They are trial 192 of the selection run `gen 512` (Section 3.6), chosen there for the six-round step and kept unchanged: round 0 stays affine for every constant set, so they remain valid at 24 rounds (not re-optimised):

```
K0  c9a9d386ab38e13a  K2  9be65c0f48819e78  K3  a42df10543300344  K5  9d9a486de15a3242
K7  62628f16871056a6  K8  8d7196f55bc91f8b  K10 793ea2677e200f74  K11 7e8d7d4cce830045
K12 fe58db5a1de5126a  K13 1b571a79774b02ce  K14 8a2d82f8f9dcb705  K15 f01a6a80f9aae74b
K1 = K4 = K6 = K9 = 0;  K16 = 8000000000000006 (padding)
PD (lanes 0..3) 7fffffff7fff7ff7 ffffffffffffffff 0000000000000000 0000000000000000
```

**Why round 0 is affine.**
- *Theta of round 0.* The column sums of columns 1 and 4 are constants: u0 xor u1 xor (u0 xor u1 xor K11) xor lane 16 xor lane 21 = K11 xor 0x8000000000000006, and u2 xor u3 xor (u2 xor u3 xor K14) xor lane 19 xor lane 24 = K14. Theta adds only constants to every lane.
- *Chi of round 0.* After rho and pi, no two of the six message lanes are adjacent inside a chi row, so every product of chi has a constant factor and chi of round 0 is affine in u. The generator checks this for every product (it stops with "round 0 not linear" otherwise).
- *Round 1 theta.* A linear map of affine values is affine.

The search uses no algebraic property of F: F is only evaluated. (The 23 nonlinear rounds after the affine round 0 are executed in full.)

## 3. One step of 256 walks: the program

### 3.1 Planes, polarity and the four sections

A batch is 256 walks. Plane (lane, z) is one 256-bit word whose bit t is bit z of that lane for walk t. The rotations of rho and the moves of pi rename planes (the addresses and register numbers are immediates) and cost nothing.

**Stored polarity.** Some planes are stored complemented, by a polarity pattern Q (bit X + 5Y for the chi output (X, Y)); the lane complementing transform of the Keccak designers is the origin of this device. chi of a row is x xor (not y and z); with the stored polarities of y and z different, an AND or an OR of the stored planes gives the term or its complement with no NOT, and the stored polarity of the result absorbs the complement. Q is a fixed point of a whole round: the stored polarity of every plane of the next round equals that of this round. The plan of a row may also compute one output X from the finished output X+1 of the same row: for chi output y' = y xor (not z and w), not y' and z = not y and z (where z = 1, y' = y), so the term of X reads y' in place of y. y' has the stored polarity of its plan, so the five terms no longer form an odd cycle of polarity conditions and a row can be done without a complement (10 operations instead of 11). The generator takes this choice only where it is cheaper (`plan_row_t`, Appendix B); the polarity candidates below are still selected with the plain plan. The generator selects Q = 3228195 (Section 3.4).

The step has four sections. The listing of the program (Appendix B prints the generator; the listing has SHA-256 07a1035fc2a8849629fc42be8f8d4f5169a220bcd9df18c6a79812c574d78ed0) gives, per section:

| section | role | xor | and | or | shr | sub | ld (round constant) | mov of a plane value | ld | st | mov (allocation) | total |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AFF | round 0 and theta of round 1: the affine map u -> 1600 planes | 1,808 | | | | | | 392 | 0 | 625 | 259 | 3,084 |
| GB | one generic round, buffer 1 -> buffer 0 | 4,999 | 775 | 832 | 7 | 7 | 1 | | 625 | 625 | 0 | 7,871 |
| GA | one generic round, buffer 0 -> buffer 1 | 4,999 | 775 | 832 | 7 | 7 | 1 | | 625 | 625 | 427 | 8,298 |
| R23 | round 23, row 0 only, the four output lanes | 320 | 128 | 128 | | | | | 125 | 0 | 0 | 701 |

- **AFF.** Each output plane of theta-1 is an affine form in the 256 input bits. The generator tracks the forms, emits one XOR for each new form (forms computed once are reused), adds D of round 1 once per (x, z) and stores the 1,600 planes of buffer 1 with the stored polarity of the generic round. A plane equal to an existing value is a counted `mov`.
- **GB and GA.** The generic round reads planes T = A xor D (theta already added) and writes the planes T' of the next round, slice by slice: for slice z and each row it takes the five planes of B = pi(rho(T)), computes the five chi outputs with the polarity plan of the row, XORs them into the column sums C'[x][z], and adds D'[x][z] = C'[x-1][z] xor C'[x+1][z-1] when the slice is done; slice 0 is finished last (it needs C' of slice 63). Iota: the round constant is one memory word (its complement) loaded once per round; at the 7 positions z in {0, 1, 3, 7, 15, 31, 63} it is shifted, masked and turned into 0 or all-ones (shr, and, sub), then XORed. GB and GA are the same round with the buffers exchanged; rounds 1 to 22 run GB GA GB GA ... GB GA, GB eleven times and GA eleven times, each as one code body.
- **R23.** Row 0 of round 23 and the outputs x = 0..3 (the digest lanes). Its output planes are the next step's input: digest plane j of the walks is input plane j of the next step (no copy).

### 3.2 The machine (declared heuristic H_machine)

The 256-bit word RAM of collision-frontier-v5 with:

- **A register file of 1,024 words of 256 bits.** 1,018 registers hold program values; 6 hold the loop state (round-constant pointer, step counter c, next deadline nxt, next trail number idn, the address of rho, one temporary). The file is counted as memory (32,768 bytes, Section 6).
- **Every transfer is an instruction and is charged.** `ld r, addr` (register from a memory word at an immediate address), `st r, addr`, and `mov r, s` (register to register) are one word operation each, like `xor`, `and`, `or`, `shr`, `sub`. No instruction reads memory except `ld`; none writes memory except `st`. A NOT is an XOR with the all-ones immediate. There is no fused operation.
- **Code at 32 bytes per instruction.** Every instruction of every routine is counted as one 32-byte word of memory (Section 6). There is no compact encoding, no interpreter and no decode convention: the program is straight-line native code with immediate register numbers and addresses, so the instructions above are all that is executed.

This is the convention under which our entry 0a9640ed (blake3-r3) was accepted by review (a 1,024-word register file, all transfers charged everywhere). It is stated as a heuristic only because the cost model fixes no register count; nothing in the time or memory ledger is free.

### 3.3 Register allocation with shared section code

The generator first builds each section as a program over plane names (the planes of buffers 0, 1 and 2, and temporaries), then allocates it to the 1,018 program registers. The allocation must let GB and GA each be one code body used twice, so it fixes what is in registers at each section boundary:

- **Boundary sets.** S1 = the first KB planes of buffer 1 in the order of their first use by GB; S0 = the first KB planes of buffer 0 in the order of their first use by GA (KB = 975, Section 3.4). Plane number i of S1 lives in register i at every buffer-1 boundary (AFF -> GB, GA -> GB and GA -> R23: round 23 reads buffer 1, left by the eleventh GA). The registers of S0 at the buffer-0 boundary (GB -> GA) are wherever GB leaves them; the code of GA is built from that map. At the loop boundary (R23 -> AFF) the 256 output planes are in the registers where R23 leaves them, and AFF's code reads them there. Every other live plane at a boundary is in memory.
- **Inside a section** the allocator walks the instructions in order. An operand not in a register is loaded (`ld`). A free register is taken if one exists (the lowest one not reserved for a boundary plane); otherwise the register value whose next use is furthest is evicted (ties: the smaller plane name, then version), with a `st` if the value is still needed and not already in memory. A value that is never read again is dropped; an output plane not in the exit set is stored when it is dropped. A boundary plane is written into its fixed register; if another live value is there, that value is first moved to a free register (`mov`). At the end of the section, exit-set planes not in their registers are loaded or moved there.
- **Counts.** The allocation adds 625 + 259 (AFF), 1,250 (GB), 1,250 + 427 (GA) and 125 (R23) transfers. The program uses the 1,018 registers 0..1,017 and 1,250 memory cells for spilled planes.

The program is self-consistent by construction (GB is entered from AFF and from GA in the same state, GA from GB, R23 from GA), and it is checked by execution (Section 3.7).

### 3.4 Selections made by the generator

The generator `gen_s24ls` (Appendix B) makes two selections before it writes the program. Both are part of the preprocessing, charged and measured (Section 3.6).

- **Polarity pattern.** For every q < 2^25: compute the stored polarities pT of the round inputs from q, and for each of the five rows the cheapest plan (complement subset and AND/OR choice, `plan_row`) whose chi outputs have the stored polarities of q; q is a candidate when the five plans exist with total cost at most 7 (a fixed point of a round). There are 66 candidates. For each candidate the generator builds the load/store forms of AFF, GA and R23 and counts AFF + 22 x GA + R23 (22 generic rounds); the smallest wins, ties to the smaller q. Result: q = 3228195 with 221,978.
- **Boundary size.** For each KB in {930, 945, 960, 975, 990, 1000, 1012} the generator allocates the four sections as in 3.3 (without writing) and computes the step; the smallest wins, ties to the smaller KB. The steps are 182,528, 181,992, 181,713, **181,705**, 182,057, 182,559 and 182,572 (sections and loop control, without the prefilter hit counter): KB = 975.

The message constants were selected before by `gen 512` (Section 3.6). The search parameters H, U, Lc and Tb are fixed numbers of the algorithm (Section 4); Tb is the least multiple of 2^96 that reaches the success bound.

### 3.5 The ledger of one step

| part | operations |
|---|---:|
| AFF | 3,084 |
| GB, eleven times | 86,581 |
| GA, eleven times | 91,278 |
| R23 | 701 |
| loop control (pointer initialisation, 22 pointer steps for rounds 1 to 22, 11 exit tests of 2 after the eleven GB, 11 jumps after the eleven GA) | 56 |
| prefilter word: OR of the 16 output planes 0..15 of lane 3 (15), compare and branch (2) | 17 |
| step counter (add, compare with nxt, branch) | 3 |
| **BSTEP** | **181,720** |

That is 709.84 word operations per evaluation of F, 0.1091 of the reference cost 6504 per evaluation. Of these, 33,206 are loads, stores and moves added by the allocation (18.3 percent): 884 in AFF, 11 x 1,250 in GB, 11 x 1,677 in GA, 125 in R23.

### 3.6 Preprocessing: the two programs, their time and memory

The attack runs two programs before the search. Both are our own freestanding C (no libc), printed in Appendices B and C.

1. **`gen 512`** (Appendix C, the LS1 generator of our team with `MAXN` 32768). For each of 512 constant sets (trial 0: all constants zero; trial t > 0: xorshift constants from seed t) it builds a bit-sliced straight line of the step and counts its operations, and keeps the trial with the fewest (trial 192). Only the constants K of the chosen trial are used here.
   - Time: charged 513 x 2^32 + 512 x 2^10 word operations (each build at most 2^32; the run takes 0.56 s of user time).
   - Memory: peak resident set (VmHWM, measured by the program) 552,960 bytes; its whole static image (text, data and bss, all counted whether touched or not) is 795,909 bytes. Run inside our 1 MiB WebAssembly sandbox (linear memory capped at 16 pages, the declared static span counted), it fits in 13 pages and picks trial 192.
2. **`gen_s24ls`** (Appendix B). It selects Q and KB (Section 3.4) and writes the program: every instruction is written as a 32-byte word into a code region of 655,360 bytes, and its text listing to the output.
   - Time: inside the sandbox, 15,557,642,556 executed WebAssembly instructions (2^33.86) for the whole run (both selections and the writing); natively 3.1 s. Charged 2^34 word operations.
   - Memory: VmHWM of the native static build, **at most 1,028,096 bytes (1,004 KiB; three runs under `prlimit --data=1048576`, where it runs to completion and writes the same listing, gave 1,000, 1,004 and 1,004 KiB), including the code region it writes** and its own code and stack. The work arrays of the generation phase and of the allocation phase share one region; the affine-form store of AFF (210,176 bytes) lives in the tail of the code region before code is written there. Inside the sandbox the run fits in 16 pages (1,048,576 bytes, the declared static span plus stack counted) and writes the byte-identical listing.
   - The generator's listing and the Python generator of the experiment (Section 3.7) are byte-identical.

PRE = 513 x 2^32 + 512 x 2^10 + 2^34 = 2,220,498,616,320 word operations, part of N (Section 4.4). PRE / 6504 = 2^28.35, so preprocessing_log2 = 29. The two programs run one after the other and before the search, so memory is the maximum of the phases (Section 6).

### 3.7 Correctness of the step (checked by execution)

- The Python form of the generator (the functions of experiments/s24ls.py) builds the four sections, allocates them and executes the allocated program (22 generic rounds, GB and GA alternating) on a 1,018-register file and the memory cells, for 2 x 256 points and two chained steps each: 1,024 evaluations of F, every lane compared, 0 mismatches against a plain 24-round implementation with the profile's padding. The C generator and the Python generator write byte-identical listings.
- experiments/s24ls.py regenerates the program, refuses to run unless its listing hashes to the SHA-256 of Section 3.1 and its step count is 181,705 (sections and loop), and checks two chained full-width steps against the plain implementation before every request.
- The plain implementation is the full permutation and matches hashlib.sha3_256 (checked by the experiment at start); it agrees with the organizer's reference digest (verifier keccak.py, rounds=24) on all 2 x 1,280 messages returned by the local runs; the organizer recomputes every returned pair with the trusted digest (Section 7.1).

## 4. The search

Parameters:
- L = 256 walks.
- Distinguished point (DP): the 114 top bits of F are zero (lane 3 zero and the top 50 bits of lane 2 zero), theta = 2^-114.
- Trail cap Lc = 17 x 2^114 - 2 = 353,076,186,380,368,278,740,073,750,386,966,526 steps (kappa = Lc theta = 17 - 2^-113).
- U = 17,540: the limit on trails started in one attempt.
- Table TAB: SW = ceil(U / 3) = 5,847 words of 256 bits, three record fields of 85 bits per word (bits 85 k to 85 k + 84, k = 0, 1, 2), so 3 SW = 17,541 >= U fields. A record: bits 0 to 68 the key (the 69 low bits of the trail's end: lane 0 and the low 5 bits of lane 1, none of them forced to zero by the DP), bit 69 set (used), bits 70 to 84 the trail number (15 bits, U < 2^15). A used field is nonzero; an empty field is zero. There is no length field.
- Tb = 16965265 x 2^96 = 1,344,126,772,517,560,767,323,935,406,597,079,040 = 1.01120859 x 2^120 steps of 256 walks per attempt.
- HMAX = floor(Tb (1 + 2^-20) / 2^8) + 1 + Lc = 358,326,686,592,777,426,050,026,092,214,878,207: the cap on prefilter hits. The attempt aborts at hit HMAX + 1.

State:
- in registers: the 256 output planes of the last step (the input of the next one); the loop state (6 registers);
- in memory: the 1,250 spill cells of the program; LID[l] and LST[l] for each walk l (its trail number and the step at which it started); TAB; rho; the hit counter h and HMAX; the round constants.

```
rho := random word; idn := 256; h := 0; TAB := 0; for l < 256: LID[l] := l; LST[l] := 0; input plane bits of walk l := rho + l
c := 0; nxt := min(Tb, Lc)
loop:
  c += 1
  the step (Section 3): AFF, then GB and GA eleven times each in turn (rounds 1 to 22), then R23; the output planes are the next inputs
  pf := OR of the 16 planes 0..15 of lane 3 (15 ORs)
  if pf != all-ones:                                  -- some walk has the low 16 bits of lane 3 zero (probability 2^-16 each)
      h += 1; if h > HMAX: halt, the attempt failed   -- hit counter and abort (F5)
      slow test of the remaining 48 planes of lane 3 and the top 50 planes of lane 2 -> the walks l at a DP
      for each such walk l, in increasing order:
          key := the 69 low bits of the end of walk l; record := key | 1 << 69 | LID[l] << 70
          i := the low 13 bits of the key; if i >= SW: i := i - SW
          probe: for word i, i + 1, ... (wrap at SW), for field k = 0, 1, 2 of the word:
             an empty field: TAB[i] := TAB[i] OR record << 85 k (store), end of the probe
             a field with the same 70 low bits (key and used bit) and trail number a != LID[l]:
                REPLAY(a, LID[l], c - LST[l]); if it returns p != q, output m(p), m(q) and stop; otherwise halt, the attempt failed
          restart(l)
  if c = nxt:
      if c = Tb: halt, the attempt failed
      for each walk l with c - LST[l] = Lc: restart(l)        -- no DP within Lc steps
      nxt := min(Tb, min over l of LST[l] + Lc)
restart(l): if idn = U: halt, the attempt failed
            LID[l] := idn; LST[l] := c; input plane bits of walk l := rho + idn; idn += 1
REPLAY(trail a, trail b of length lb):
  p := rho + a; la := 0; repeat: p := F(p); la += 1 until p is a DP or la = Lc     -- rebuild the length of trail a
  p := rho + a, q := rho + b; the longer trail is advanced by |la - lb| evaluations of F
  if p = q return nothing; repeat min(la, lb) times: if F(p) = F(q) return (p, q); p := F(p); q := F(q)
  return nothing
```

A trail ends at its first DP (it is recorded and restarted in that step), so the rebuild of a recorded trail stops at its own end after exactly its length la <= Lc evaluations. The walks are independent walks of F; only the instruction stream is shared, and all 256 lanes always work. If two trails end at the same DP and neither start lies on the other trail, they merge at a first point; after the advance both are at the same distance d <= min(la, lb) from the common end, so the replay finds F(p) = F(q) with p != q within d iterations. Records are at most U, so the probe always finds an empty field or a match; linear probing over the SW words visits each word at most once.

### 4.1 One iteration of the loop

BSTEP = 181,720 operations (Section 3.5): the step, the prefilter and its test, the loop control and the step counter. No other operation runs in an iteration without a prefilter hit or a deadline.

### 4.2 The replay

The replay evaluates F on one point at a time with a one-walk program of F (lane-wise Keccak on 64-bit words in the 256-bit registers: XOR, AND, OR, shifts; a rotation is shl, shr, or, and). The program is a **loop** (unrolled it would take 5,472 code words, which the table uses instead): a prologue of 78 operations (round 0 with the affine part folded; eight constant lanes are loaded into their state registers), a body of two generic rounds of 486 operations (state registers A to B, then B back to A, no register move; each round loads its round constant from the constant table with one `ld`) executed 11 times (rounds 1 to 22), and an epilogue of 82 operations (round 23, lanes 0 to 3 only, the round constant and PD folded into one immediate). Loop control is charged as in the step: 1 pointer initialisation and, for each of the 11 iterations, 2 pointer steps, an exit test of 2 and a jump of 1, 56 operations in all. F = 78 + 11 x 486 + 82 + 56 = **5,562** operations and 646 instruction words of code (fops24_loop.py, Appendix D, executes the looped program on a register dictionary and checks 300 random points against the 24-round reference digest). The rebuild of the stored trail's length costs F + 11 per evaluation (4 moves; the DP test 4: shift of lane 2, OR with lane 3, compare, branch; counter 3) and runs at most Lc evaluations. An advance step costs F + 7 (4 moves, counter 3), a lock-step iteration 2F + 26 (two evaluations, 16 moves, the equality test of four lanes 9, a jump). With both lengths at most Lc the replay costs at most (F + 11) Lc + (F + 7)(max - min) + (2F + 26) min <= (3F + 37) Lc. At most one replay runs per attempt.

### 4.3 Rare operations

Each routine is straight-line code or a counted loop; its count is an upper bound on what it executes.

- **A prefilter hit: 207.** The hit counter is 6 (load h, add, store, load HMAX, compare, branch). The slow test is 201: 48 loads and 48 ORs (lane 3 planes 16 to 63), 50 loads and 49 ANDs (lane 2 planes 14 to 63), 2 to combine, a compare and a branch, a call and a return (a load of a plane held in a register is charged as a load all the same). The driver aborts at hit HMAX + 1, so every execution processes at most HMAX + 1 hits, and the ledger charges that number. The abort enters the success bound as F5 (Section 5).
- **A walk at a DP: 370 + 5 + (28 SW + 20) + 6 + 2,460 + 1,100 = 167,677**: gathering the 69 key planes (5 per plane, plus 25 for the polarity of lane 1 and the loop control), the record (5: the key mask, the used bit, the shift and OR of the trail number, one spare), the probe (at most 28 per word over at most SW words: per word a load, the pointer step, the wrap test and its branch; per field a shift, the 85-bit mask, the empty test and its branch, the 70-bit mask, the compare and its branch, one spare), the store (6: shift, OR, store, address), the restart of a walk (a 256-bit add, the new trail number, then for each of the 256 planes: shift/and for its bit, shift left, and, or, plus the polarity of two lanes), and the next deadline (a loop over the 256 LST words). It runs at most U + 1 times.
- **Deadline scans: 1,300**, at most U + 1 times.
- **Setup, replay entry (the trail number taken from the matched field) and final bookkeeping: 704,000.**

R = (HMAX + 1) x 207 + (U + 1)(167,677 + 1,300) + 704,000 = 74,173,624,124,704,927,192,355,401,091,444,518,613.

### 4.4 Total

N = Tb x 181,720 + (3F + 37) Lc + R + PRE = **250,233,383,790,854,746,290,668,150,817,854,387,498,031** word operations (Appendix A).

| part | operations | share |
|---|---:|---:|
| main loop, Tb x 181,720 | 244,254,717,101,891,142,638,105,542,086,821,203,148,800 | 0.97611 |
| replay, (3F + 37) Lc with F = 5,562 | 5,904,493,064,838,898,725,370,253,327,721,241,214,298 | 0.02360 |
| rare operations R | 74,173,624,124,704,927,192,355,401,091,444,518,613 | 2.96e-4 |
| preprocessing PRE | 2,220,498,616,320 | 9e-30 |

time_log2 = log2(N / 6504) rounded up at the fifth decimal = **124.85522**, checked in exact integer arithmetic:

    6504^100000 * 2^12485521 < N^100000 <= 6504^100000 * 2^12485522

## 5. Success probability and the premise H_rand

**The premise H_rand (the one score-critical premise, an assumption).**
- *Statement.* Over the algorithm's coin (the uniform random word rho), the program of Sections 3 and 4 run on the fixed function F of Section 2 succeeds in one attempt with probability at least the probability P computed below for a uniformly random function from 256 bits to 256 bits.
- *Role.* Score-critical: the claimed success 0.39 is P >= 0.39 carried to the fixed target by this premise.
- *Scope.* The fixed function F (the full 24-round permutation with the embedding of Section 2) on the points of one attempt: at most 256 Tb = 1.011209 x 2^128 evaluations in 256 lockstep walks from starts rho + i, i < U. Only the pair-coincidence rate among evaluated images and the distinguished-point rate enter the bound; the program, the cost, the memory and the failure terms are derived, not assumed.
- *Limitations.* Not proved: no proof is known that the fixed target behaves like a random function over rho, and no run reaches 2^128 evaluations or a full collision. Given rho the run on the fixed target is deterministic; no per-evaluation hazard is claimed for it. If the pair-coincidence rate of F were (1 - eps) of uniform, the same success would cost about 0.5 log2(1/(1 - eps)) more bits (0.0073 for eps = 0.01).

Everything below is computed in the random-function model M: F is a uniformly random function from 256 bits to 256 bits, realised by lazy sampling (a fresh evaluation draws a new independent uniform value), and rho is uniform and independent of F. In M:

- (i) the first coincidence of images among e evaluations has probability 1 - prod_{k<e}(1 - k/n) >= 1 - exp(-e(e-1)/(2n)) =: G(e), n = 2^256;
- (ii) the point reached just after a coincidence is uniform, so the number l of further evaluations of a trail until its DP satisfies P(l >= j) = (1 - theta)^j, independently of when the coincidence happened;
- (iii) the program chooses its next inputs, and which trails restart, are cut or abort, from earlier outputs; by lazy sampling, given the whole history, a fresh evaluation equals a given earlier output with probability 2^-256 whatever inputs were chosen.

**The coincidence.** Evaluations are numbered step by step and, inside a step, by walk. The first coincidence is a stopping time over all evaluations in this order: when k earlier images are distinct, the next fresh evaluation coincides with one of them with conditional probability exactly k/n given the history (iii), so prod_{j<k}(1 - j/n)^-1 x 1{no coincidence among the first k} is a martingale and P(no coincidence among e evaluations) = prod_{k<e}(1 - k/n) exactly; no set of finished trails is conditioned on. Let e* be the first evaluation whose image equals an earlier image, at step b* = ceil(e*/256). Its trail B and the earlier trail A have equal points from then on and both end at the same DP after l further evaluations of B. B is recorded at step b* + l at the latest; A reached the same point no later, so A was recorded before (or in the same step, in a lower walk), and the probe for B finds A's record (the same end, so the same key).

The search succeeds if (a) b* + l <= Tb, (b) both trails have at most Lc evaluations, (c) fewer than U trails are started, (d) the coincidence is between two different trails, and (e) the matched record is that of the real end and the replay finds the merge.

Split l into bins of w = 2^102 steps: bin j holds l in [(j - 1) w, j w - 1], j = 1 .. 17 x 2^12 - 1, with probability p_j = (1 - theta)^((j-1) w) - (1 - theta)^(j w). If l is in bin j, (a) holds when e* <= 256 (Tb - j w). By (ii),

    Pr[(a)] >= sum_j p_j G(256 (Tb - j w)).

The failure events that the sum does not cover:

- **F1**, some trail of the attempt has no DP within Lc steps: at most U (1 - theta)^Lc <= U e^-kappa = 7.261e-04. This covers (b).
- **F2**, more than U - 256 restarts after a DP. Realise F by lazy sampling with independent uniform values V_1, ..., V_(256 Tb), one per evaluation index in execution order: the t-th evaluation returns V_t if its input is fresh and the stored value otherwise. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(2^-114) variables for every t, fresh or not, so N1 = xi_1 + ... + xi_(256 Tb) is exactly binomial with mean mu = 256 Tb theta = 16567.6. A DP output at a fresh input is a position with xi_t = 1. A DP output at a repeated input never causes a restart: it is the stored output of the first evaluation of that input, whose trail ended there and was recorded with a different trail number (numbers are never reused), and the probe finds that record (the same end, so the same key), so the attempt goes to REPLAY and stops. Hence the restarts after a DP are at most N1. With the cap restarts in F1, the halt at idn = U needs N1 >= U - 255, and the Chernoff bound e^-mu (e mu / (U - 256))^(U - 256) >= P(N1 >= U - 256) gives 2.338e-07. This covers (c).
- **F3**, the coincidence lies inside one trail (a cycle or a self-merge): at most U 2^(2 x 114) / n = 6.534e-05. This covers (d).
- **F4**, 2^-40: a start rho + i equal to a point of another trail (U starts against at most 256 Tb < 2^129 images: 1.031e-34), and two different ends with the same 69-bit key among at most U records (U^2/2 pairs at 2^-69 each: 2.606e-13; such a match ends the attempt at REPLAY). If neither start lies on the other trail and the ends are equal, the rebuild returns the exact length of A (it stops at A's first DP, its end) and the replay finds the merge (Section 4). Appendix A checks the two terms in exact rationals (their sum is below 2^-41). This covers (e).
- **F5**, the hit counter aborts the attempt before it stops: below 2^-1000. Call a walk's input at a step fresh if F was not evaluated at it before in the attempt, and let X' count the steps at which some walk with a fresh input lands on planes 0..15 of lane 3 zero. Given the past, the images of the fresh inputs are independent and uniform, so each step adds to X' with conditional probability at most 1 - (1 - 2^-16)^256 < 2^-8. A hit not counted in X' needs a walk at a repeated input. Outside F4 no start is a point of a trail, so repeated inputs occur only after the first image coincidence (step b*), and an attempt that succeeds outside F1 stops at step b* + l with l <= Lc. On success, therefore, h <= X' + Lc, and an abort needs X' >= floor(Tb (1 + d) 2^-8) + 2 > (1 + d) mu', with d = 2^-20 and mu' = Tb 2^-8. The Chernoff bound for indicators with conditional probabilities at most 2^-8 (supermartingale exp(s X'_t - (e^s - 1) t 2^-8)) gives probability at most exp(-d^2 mu' / (2 + d)) = exp(-2,387,647,646,863,434,961,181) < 2^-1000, checked in exact rationals in Appendix A.

With a further 2^-60 for rounding, the success probability of one attempt in M, with the abort, is at least **0.3900000152** at Tb. It is 0.3899999791 at Tb - 2^96, so Tb is the least multiple of 2^96 that reaches 0.39. Appendix A computes both with 80-digit decimals.

In evaluations, 256 Tb = 1.011209 x 2^128; the birthday point for success 0.39 is 0.99430 x 2^128, and the wait for the DP of the last trails, about 256 x 2^114 = 2^122 evaluations, is the main reason the count is above it.

The claim is one attempt with success at least 0.39, a probability over the coin rho for the fixed target, under the premise H_rand.

## 6. Memory

The search, at its peak (32-byte words):

| region | words | bytes |
|---|---:|---:|
| register file (H_machine) | 1,024 | 32,768 |
| program sections AFF, GB, GA, R23 (every ld, st, mov included) | 19,954 | 638,528 |
| prefilter (17) | 17 | 544 |
| loop control, slow test, deadline, start and output routines | 435 | 13,920 |
| packed record, probe and store routines (three fields per word) | 64 | 2,048 |
| key gather (69 planes) and walk restart, unrolled over the output registers (register numbers are immediates) | 2,167 | 69,344 |
| one-walk looped program of F (78 + 486 + 82 = 646) and the replay loops, the rebuild loop included (140) | 786 | 25,152 |
| spill cells of the program | 1,250 | 40,000 |
| round constants (23 cells) | 23 | 736 |
| LID and LST of the 256 walks | 512 | 16,384 |
| table TAB (three records per word, at least U = 17,540 records) | 5,847 | 187,104 |
| scratch: rho, h, HMAX, replay state | 64 | 2,048 |
| **total** | **32,143** | **1,028,576** |

The code sizes of the program sections are the generator's counts; the other routines are counted by the stated bounds (Section 4.3).

**Preprocessing.** `gen 512` (peak 552,960 bytes, static image 795,909 bytes) and `gen_s24ls` (peak at most 1,028,096 bytes including the code region it writes) run one after the other and before the search; each releases its working memory before the next phase. Memory = max(search 1,028,576, gen_s24ls 1,028,096, gen 512 795,909) = 1,028,576 bytes = 2^19.9722 <= 2^20, so memory_log2_bytes = 20. Both generators also run inside a 1 MiB WebAssembly sandbox (13 and 16 pages) that counts everything they declare.

The declared experiments run in Python inside the organizer's sandbox as reduced-width program checks; the memory of the attack is the ledger above.

## 7. Evidence

### 7.1 Organizer experiments (declared in experiments/manifest.json, program experiments/s24ls.py)

Both experiments regenerate the program in Python (Section 3.7), check it, and execute it on Python integers, all trials side by side (one integer holds a plane for all trials of the request).

- **rho-w22** runs the search of Section 4 end to end at width 22: after every step the planes 22 to 255 are set to zero, DP = 4 low image bits zero, cap 128, 3,000 trails and 400 steps per attempt. The table is the packed table of Section 4 at this width: 1,000 words, three 85-bit fields per word (key = the 22-bit end, a used bit, the trail number; no length), linear probing over words; a matched record gives the trail number only, and the program rebuilds that trail's length by replaying it from its start to its first DP before the replay of Section 4.2. A replay that returns nothing ends the attempt (the halt rule of Section 4). Each trial runs one attempt and returns two messages whose 24-round digests agree on the 22 low bits, or nulls when its attempt halts. The program counts, per attempt, the restarts after a DP (R_dp) and at the deadline (K_cut), and asserts idn - 256 = R_dp + K_cut before it reports.
- **proj-w256** runs eight chained full-width steps from 256 uniform points per trial and finds the first two distinct evaluated inputs whose images agree on the 22 low bits; every returned pair is recomputed by the organizer.

Both are program checks: they show that the claimed program, table and replay run end to end and return pairs that the organizer recomputes with its trusted digest. No count, step mean or timing from them is used as an estimate of a probability or a cost. The organizer intake run (Docker sandbox, two runs each, 256 trials per request) passed: rho-w22 209 of 256 trials returned a valid pair (the other attempts halted, Section 4) in 13.6 s and 11.5 s, proj-w256 126 of 256 (program check, count not interpreted) in 5.8 s and 4.2 s, wall times including container start. Our local runs on other seeds (five requests of 256 trials each): rho-w22 returned 1,069 pairs, all 1,069 valid against the organizer's reference digest at 24 rounds; proj-w256 returned 492.

## 8. Credits and literature

A credit is not an endorsement; nobody named here has reviewed this package.

- **Our entries aa2e6be6 (sha3-256-r6, S6LS), 3183c941 (sha3-256-r7, SHA3R7P) and 606bcba0 (sha3-256-r24, SHA3R24).** The program, constants, machine and ledger method of this package are theirs; the step here has 22 generic rounds from the same two code bodies and the replay F is a loop (as in 606bcba0). From 606bcba0 it takes the adaptivity clause (iii) of the random-function model and the martingale statement of Section 5. Declared as dependencies (606bcba0 first, then 3183c941).
- **Our entry 2d74a370 (sha3-256-r6).** The lockstep distinguished-point search with restart on a DP, deadlines, the replay, the form of the success bound of Section 5 and the rare-operation accounting.
- **J. Guo, M. Liu, L. Song, Linear Structures: Applications to Cryptanalysis of Round-Reduced Keccak, ASIACRYPT 2016.** The linear-structure placement of message lanes that keeps round 0 affine (Section 2).
- **jungjipdo, entry 67f781f8 (sha3-256-r6).** The step program here does not use its design. What remains of its ideas is in the constant selection only: `gen 512` (Appendix C) is our LS1 generator, whose step design (lazy per-row theta, per-row complement subsets, last-use allocation) we took from 67f781f8's text as a description; it is used here only to choose the constants K. None of 67f781f8's code was run, imported or compiled.
- **P. C. van Oorschot and M. J. Wiener, Parallel collision search with cryptanalytic applications, J. Cryptology 12 (1999); J. M. Pollard (1975).** The distinguished-point and rho methods.
- **G. Bertoni, J. Daemen, M. Peeters, G. Van Assche, Keccak implementation overview.** The lane complementing transform, applied plane by plane (Section 3.1).
- **L. A. Belady (1966).** Furthest-next-use replacement, used by the allocator (Section 3.3).

## Appendix A. The exact ledger

Run with `python3 cert_s24ls.py [listing]` (with the listing argument it recounts the sections from the generator output). Output:

```
step of 256 walks: AFF 3084 + 11 x GB 7871 + 11 x GA 8298 + R23 701 + loop 56 + prefilter 17 + counter 3 = 181720
Tb = 1344126772517560767323935406597079040 = 1.01120859 * 2^120  evaluations = 1.011209 * 2^128
failure terms: F1 7.261e-04  F2 2.338e-07  F3 6.534e-05  F4 9.095e-13  F5 < 2^-1000  success bound 0.3900000152  (Tb - 2^96: 0.3899999791 )
F4 parts: starts 1.031e-34  key matches 2.606e-13  (sum < 2^-41)
hit counter: HMAX = 358326686592777426050026092214878207 ; P[abort before the stop on success] <= exp(-2387647646863434961181) < 2^-1000
main 244254717101891142638105542086821203148800  replay 5904493064838898725370253327721241214298  rare R 74173624124704927192355401091444518613  PRE 2220498616320
  share main    9.76108e-01
  share replay  2.35959e-02
  share rare    2.96418e-04
  share PRE     8.87371e-30
N = 250233383790854746290668150817854387498031
preprocessing_log2: PRE/6504 = 2^28.347; preprocessing_log2 = 29
search memory: code words 23423 data words 8720 bytes 1028576 ; generator peak 1028096 ; memory 1028576 log2 19.9722
certificate: 6504^100000 * 2^12485521 < N^100000 <= 6504^100000 * 2^12485522
time_log2 = 124.85522
S = time_log2 + max(0, memory_log2 - 20) = 124.85522
```

Program:

```python
# S24LS exact ledger (NOLEN: drop-length table, three records per word) (S6LS ported to twenty-four rounds; unit 6504 = the organizer reference operation cost of sha3-256-r24 = 24 x 271): step count, success bound, failure terms, hit cap, N, memory, integer certificate.
# Integers and Fractions; Decimal with 80 digits only for the exponentials and logarithms of the success bound.
import sys
from fractions import Fraction as Fr
from decimal import Decimal as D, getcontext, ROUND_CEILING
getcontext().prec = 80
ceil = lambda v: int(v.to_integral_value(rounding=ROUND_CEILING)) if isinstance(v, D) else -((-v.numerator) // v.denominator)

# ---- one step of 256 walks (Section 3; instruction counts of the program printed by gen_s6ls, Appendix B) ----
SEC = {'AFF': 3084, 'GB': 7871, 'GA': 8298, 'R23': 701}       # listing lines per section, every ld/st/mov included
if len(sys.argv) > 1:                                         # optional: recount from the listing file
    cnt, cur = {}, None
    for line in open(sys.argv[1]):
        if line.startswith('== '): cur = line[3:].strip(); cnt[cur] = 0
        else: cnt[cur] += 1
    assert cnt == SEC, cnt
loop = 1 + 22 + 11 * 2 + 11 * 1                                  # pointer init, twenty-two pointer steps (rounds 1..22), exit test after each of the 11 GB, jump after each of the 11 GA
PREF = 15 + 2                                                 # prefilter word: OR of 16 output planes of lane 3 (15), compare and branch (2)
CNT = 3                                                       # step counter: add, compare with nxt, branch
BSTEP = SEC['AFF'] + 11 * SEC['GB'] + 11 * SEC['GA'] + SEC['R23'] + loop + PREF + CNT
print('step of 256 walks: AFF %(AFF)d + 11 x GB %(GB)d + 11 x GA %(GA)d + R23 %(R23)d' % SEC, '+ loop', loop, '+ prefilter', PREF, '+ counter', CNT, '=', BSTEP)
F = 5562  # one-walk LOOPED program of F for the replay (fops24_loop.py: 78 + 11 x 486 + 82 + loop control 56)
FCODE = 646  # its code words (round 0, the two-round body, round 23: 78 + 486 + 82)

# ---- parameters of the search (Section 4) ----
L, Hb, U = 256, 114, 17540
KAPPA = 17
SW = -(-U // 3)                                                # table words: three 85-bit records per word (key 69 bits, used bit, trail number 15 bits; no length field)
assert U < 2 ** 15 and 3 * SW >= U
Lc = KAPPA * 2 ** Hb - 2
n = D(2) ** 256
theta = D(2) ** -Hb
J = KAPPA * 2 ** 12
w = 2 ** (Hb - 12)
lq = (1 - theta).ln()


def success(Tb):
    s = D(0)
    qprev = D(1)
    for j in range(1, J):
        qj = (w * j * lq).exp()
        e = L * (Tb - j * w)
        if e > 1:
            s += (qprev - qj) * (1 - (-D(e) * (e - 1) / (2 * n)).exp())
        qprev = qj
    kappa = D(Lc) * theta
    e1 = U * (-kappa).exp()                                  # F1: some trail without a DP within Lc steps
    mu, k = D(L * Tb) * theta, U - L
    e2 = (-mu + k * (1 + (mu / k).ln())).exp()               # F2: restarts after a DP <= N1, the lottery count, exactly Binomial(L Tb, theta) (Section 5); Chernoff
    e3 = D(U) * D(2) ** (2 * Hb) / n                         # F3: a coincidence inside one trail
    e4 = D(2) ** -40                                         # F4: starts on trails, key matches of different ends, failed replay (bounded below)
    e5 = D(2) ** -1000                                       # F5: the hit counter aborts (checked below)
    return s - (e1 + e2 + e3 + e4 + e5 + D(2) ** -60), (e1, e2, e3, e4)


TB = 16965265 * 2 ** 96
p, (e1, e2, e3, e4) = success(TB)
p_less, _ = success(TB - 2 ** 96)
assert p >= D('0.39') > p_less
print('Tb = %d = %.8f * 2^120' % (TB, D(TB) / D(2) ** 120), ' evaluations = %.6f * 2^128' % (D(L * TB) / D(2) ** 128))
print('failure terms: F1 %.3e  F2 %.3e  F3 %.3e  F4 %.3e  F5 < 2^-1000' % (e1, e2, e3, e4), ' success bound', str(p)[:12], ' (Tb - 2^96:', str(p_less)[:12], ')')

F4_START = Fr(U * 2 ** 129, 2 ** 256); F4_KEY = Fr(U * U, 2 * 2 ** 69)
assert L * TB < 2 ** 129 and F4_START + F4_KEY < Fr(1, 2 ** 41)
print('F4 parts: starts %.3e  key matches %.3e  (sum < 2^-41)' % (float(F4_START), float(F4_KEY)))

# ---- prefilter hit counter and abort (Sections 4 and 5, F5) ----
DELTA = Fr(1, 2 ** 20)
HMAX = (TB * (1 + DELTA)) // 2 ** 8 + 1 + Lc                 # the driver aborts (attempt failed) at hit number HMAX + 1
MU = Fr(TB, 2 ** 8)
EXPO = DELTA ** 2 * MU / (2 + DELTA)                         # P[F5] <= exp(-EXPO)
assert EXPO > 1000 * Fr(6932, 10000)                         # ln 2 < 0.6932: P[F5] < 2^-1000
print('hit counter: HMAX =', HMAX, '; P[abort before the stop on success] <= exp(-%d) < 2^-1000' % (EXPO.numerator // EXPO.denominator))

# ---- rare operations (Section 4.3) ----
C_hit = (2 * Hb - 27) + 6                                   # slow test 2 Hb - 27 (lane 3 planes 16..63: 48 ld + 48 or; lane 2 top Hb - 64 planes: Hb - 64 ld + Hb - 65 and; 6) + counter 6
C_dp = (5 * 69 + 25) + 5 + (28 * SW + 20) + 6 + 2460 + 1100     # gather the 69 key planes, record, probe (28 per word over at most SW words), store, restart, next deadline
R = (HMAX + 1) * C_hit + (U + 1) * C_dp + (U + 1) * 1300 + 704000
replay = (3 * F + 37) * Lc                                    # rebuild the stored length (F + 11 per evaluation), then advance (F + 7) and lock-step (2F + 26)
PRE = 513 * 2 ** 32 + 512 * 2 ** 10 + 2 ** 34                 # constant selection `gen 512` + the generator gen_s6ls (Section 3.6)
N = TB * BSTEP + replay + R + PRE
print('main', TB * BSTEP, ' replay', replay, ' rare R', R, ' PRE', PRE)
for nm_, v in (('main', TB * BSTEP), ('replay', replay), ('rare', R), ('PRE', PRE)):
    print('  share %-7s %.5e' % (nm_, D(v) / D(N)))
print('N =', N)
print('preprocessing_log2: PRE/6504 = 2^%.3f; preprocessing_log2 = %d' % (float((D(PRE) / 6504).ln() / D(2).ln()), ceil((D(PRE) / 6504).ln() / D(2).ln())))

# ---- memory (Section 6), 32-byte words ----
unroll = 69 * 5 + 10 + 256 * 7 + 20                            # key gather (69 planes) and walk restart, unrolled over the output registers
code = sum(SEC.values()) + 15 + 2 + 435 + 64 + unroll + (FCODE + 140)   # program sections, prefilter, routines, packed record/probe/store (64), unrolled routines, replay F and its loops (incl. the rebuild loop)
SLOTS = 1250                                                  # memory cells the program loads or stores (printed by the generator)
data = 1024 + SLOTS + 23 + 512 + SW + 64                       # register file, spill cells, round constants, LID/LST, table words, scratch
mem = 32 * (code + data)
GEN_PEAK = 1004 * 1024                                        # measured VmHWM of gen_s24ls (1000/1004/1004 KiB over three runs; the maximum), incl. the code region it writes
mtot = max(mem, GEN_PEAK)
mlog = D(mtot).ln() / D(2).ln()
print('search memory: code words', code, 'data words', data, 'bytes', mem, '; generator peak', GEN_PEAK, '; memory', mtot, 'log2 %.4f' % mlog)
assert mtot <= 2 ** 20

K = 100000
e = ceil(K * (D(N) / 6504).ln() / D(2).ln())
while N ** K > (6504 ** K) << e: e += 1
while N ** K <= (6504 ** K) << (e - 1): e -= 1
print('certificate: 6504^%d * 2^%d < N^%d <= 6504^%d * 2^%d' % (K, e - 1, K, K, e))
print('time_log2 = %d.%05d' % divmod(e, K))
print('S = time_log2 + max(0, memory_log2 - 20) = %d.%05d' % divmod(e, K))
```

## Appendix B. The generator gen_s24ls.c

Build and run as in its header (WSL, gcc). The listing on stdout has SHA-256 07a1035fc2a8849629fc42be8f8d4f5169a220bcd9df18c6a79812c574d78ed0 and 391727 bytes; stderr prints the selections, the counts and the measured peak.

```c
/* gen_s24ls.c - S24LS program generator for sha3-256-r24 (proof.md Section 3). Freestanding C (no libc).
   1. select_q: the polarity pattern q < 2^25 (round fixed points of row cost <= 7; fewest operations of AFF + 22 G + R23).
   2. select_kb: the boundary set size KB from a declared list (smallest step).
   3. Builds the sections AFF (round 0 and theta of round 1, affine in the point under the Guo-Liu-Song 2016 linear
      structure; constants of trial 192 of gen 512), GB/GA (generic round, buffers exchanged) and R23 (round 23, row 0),
      allocates them to 1,018 registers (6 more hold the loop state) with every load, store and move written out, shared
      GA/GB code and fixed boundary sets, writes each instruction as a 32-byte word into the code region and prints the
      listing to stdout. Counts, the step and the peak memory go to stderr.
   Build: gcc -O2 -static -nostdlib -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns -fno-stack-protector
          -fno-pie -no-pie -o gen_s24ls gen_s24ls.c -lgcc        (sandbox: clang --target=wasm32 ... -DVM) */
/* ---- freestanding runtime (no libc): Linux x86-64 syscalls, or the vm1mib host when built with -DVM ---- */
#include <stdarg.h>
#include <stdint.h>
typedef unsigned long size_t;
#ifndef VM
__asm__(".global _start\n_start:\n xor %rbp,%rbp\n mov %rsp,%rdi\n and $-16,%rsp\n call cmain\n mov %rax,%rdi\n mov $60,%rax\n syscall\n");
static long sc6(long n,long a,long b,long c,long d,long e,long f){ long r; register long r10 __asm__("r10")=d; register long r8 __asm__("r8")=e; register long r9 __asm__("r9")=f;
  __asm__ volatile("syscall":"=a"(r):"a"(n),"D"(a),"S"(b),"d"(c),"r"(r10),"r"(r8),"r"(r9):"rcx","r11","memory"); return r; }
static void wr(int fd,const void *p,long n){ sc6(1,fd,(long)p,n,0,0,0); }
static void exit(int c){ sc6(60,c,0,0,0,0,0); for(;;); }
#else
__attribute__((import_module("env"),import_name("host_write"))) int host_write(int,const void*,int);
__attribute__((import_module("env"),import_name("host_exit"))) void host_exit(int);
static void wr(int fd,const void *p,long n){ host_write(fd,p,(int)n); }
static void exit(int c){ host_exit(c); for(;;); }
#endif
void *memset(void *d,int c,size_t n){ unsigned char *p=d; while(n--) *p++=(unsigned char)c; return d; }
void *memcpy(void *d,const void *s,size_t n){ unsigned char *p=d; const unsigned char *q=s; while(n--) *p++=*q++; return d; }
int memcmp(const void *a,const void *b,size_t n){ const unsigned char *p=a,*q=b; for(;n--;p++,q++) if(*p!=*q) return *p-*q; return 0; }
static size_t strlen(const char *s){ size_t n=0; while(s[n]) n++; return n; }
static char *strcpy(char *d,const char *s){ char *o=d; while((*d++=*s++)); return o; }
static int strcmp(const char *a,const char *b){ while(*a && *a==*b){ a++; b++; } return (unsigned char)*a-(unsigned char)*b; }
static int strncmp(const char *a,const char *b,size_t n){ for(;n;n--,a++,b++){ if(*a!=*b) return (unsigned char)*a-(unsigned char)*b; if(!*a) return 0; } return 0; }
static int atoi(const char *s){ int v=0, ng=0; if(*s=='-'){ ng=1; s++; } while(*s>='0'&&*s<='9') v=v*10+(*s++-'0'); return ng?-v:v; }
/* vsnprintf for %s %d %ld %x only */
static int vsn(char *o,size_t cap,const char *f,va_list ap){
  size_t n=0;
  #define PUTC(c) do{ if(n+1<cap) o[n]=(c); n++; }while(0)
  for(;*f;f++){
    if(*f!='%'){ PUTC(*f); continue; }
    f++; int lng=0; if(*f=='l'){ lng=1; f++; }
    if(*f=='s'){ const char *t=va_arg(ap,const char*); while(*t) PUTC(*t++); }
    else if(*f=='x'){ unsigned long v= lng? va_arg(ap,unsigned long) : va_arg(ap,unsigned); char t[24]; int k=0; do{ t[k++]="0123456789abcdef"[v&15]; v>>=4; }while(v); while(k) PUTC(t[--k]); }
    else { long v= lng? va_arg(ap,long) : va_arg(ap,int); char t[24]; int k=0; unsigned long u= v<0? -(unsigned long)v : (unsigned long)v;
      do{ t[k++]='0'+u%10; u/=10; }while(u); if(v<0) PUTC('-'); while(k) PUTC(t[--k]); }
  }
  if(cap) o[n<cap?n:cap-1]=0;
  return (int)n;
}
static int snprintf(char *o,size_t cap,const char *f,...){ va_list ap; va_start(ap,f); int r=vsn(o,cap,f,ap); va_end(ap); return r; }
#define sprintf(o,...) snprintf(o,64,__VA_ARGS__)
static int eprintf(const char *f,...){ char b[256]; va_list ap; va_start(ap,f); int r=vsn(b,sizeof b,f,ap); va_end(ap); wr(2,b,r<255?r:255); return r; }
static long vm_hwm_kib(void){
#ifndef VM
  static char st[4096]; int fd=(int)sc6(2,(long)"/proc/self/status",0,0,0,0,0); long v=-1;
  if(fd>=0){ long n=sc6(0,fd,(long)st,sizeof st-1,0,0,0); sc6(3,fd,0,0,0,0,0);
    for(long i=0;i+6<n;i++) if(st[i]=='V'&&st[i+1]=='m'&&st[i+2]=='H'&&st[i+3]=='W'&&st[i+4]=='M'){ long j=i+6; v=0; while(st[j]==' '||st[j]=='\t') j++; while(st[j]>='0'&&st[j]<='9') v=v*10+(st[j++]-'0'); break; } }
  return v;
#else
  return -1;
#endif
}
#define NI 10100
enum { LD, ST, XOR, AND, OR, SHR, SUB };
static const char *KN[] = {"ld","st","xor","and","or","shr","sub"};
typedef struct { short k, d, a, b; } In;
static int n, nv;
#define KR 1018                        /* registers for the program; 6 more hold the loop state (1,024 in all) */
#define NNM 4900                      /* names: M<addr> = addr (< 4800), T<k> = 4800 + k */
#define MAXOP 7000
#define MAXV 8700
#define INFV 30000                    /* "no further use" (sections have fewer than 7,000 operations) */
struct GenPh { In ins_[NI]; short last_[NI], nameA_[NI], ldal_[NI], tmpn_[NI]; };
struct AlPh { short vname_[MAXV], U_[MAXOP][2], unu_[MAXOP][2], dnu_[MAXOP], nxt_[MAXV], curv_[NNM], entry_[2000], xreg_[MAXV], reg_[MAXV];
  unsigned char vver_[MAXV], UC_[MAXOP], verc_[NNM]; };
static union { struct GenPh g; struct AlPh a; } UU;
#define CODESZ 655360                 /* at most 20,480 instructions x 32 B: the four sections of the program */
static unsigned char CODE[CODESZ] __attribute__((aligned(4096)));
   /* generation phase, then allocation phase: one region */
#define ins (UU.g.ins_)
#define last (UU.g.last_)
#define nameA (UU.g.nameA_)
#define ldal (UU.g.ldal_)
#define tmpn (UU.g.tmpn_)
#define vname (UU.a.vname_)
#define vver (UU.a.vver_)
#define U (UU.a.U_)
#define UC (UU.a.UC_)
#define unu (UU.a.unu_)
#define dnu (UU.a.dnu_)
#define nxt (UU.a.nxt_)
#define curv (UU.a.curv_)
#define verc (UU.a.verc_)
#define entry (UU.a.entry_)
#define xreg (UU.a.xreg_)
#define reg (UU.a.reg_)
#define key (UU.a.nxt_)          /* after the backward pass nxt[] is the initial key: one array */
#define IALL (-100)
#define IMM(v) (-1 - (v))
#define RCA (-1000)
#define RCA0 0x1ULL
static const int ROT[5][5] = {{0,36,3,41,18},{1,44,10,45,2},{62,6,43,15,61},{28,55,25,21,56},{27,20,39,8,14}};
static long Q;                         /* polarity pattern, chosen by select_q() */
static int Qp[5][5], pC[5], pD[5], pT[5][5];
static int xmap(int X, int Y) { return (3*Y + X) % 5; }
static void pol(void) {
  for (int X=0;X<5;X++) for (int Y=0;Y<5;Y++) Qp[X][Y] = (Q >> (X+5*Y)) & 1;
  for (int X=0;X<5;X++) { int s=0; for (int Y=0;Y<5;Y++) s+=Qp[X][Y]; pC[X]=s%2; }
  for (int X=0;X<5;X++) pD[X] = pC[(X+4)%5] ^ pC[(X+1)%5];
  for (int X=0;X<5;X++) for (int Y=0;Y<5;Y++) pT[X][Y] = Qp[X][Y] ^ pD[X];
}
static int newv(void) { return nv++; }
static void put(int k,int d,int a,int b){ ins[n].k=k; ins[n].d=d; ins[n].a=a; ins[n].b=b; n++; }
static int ld(int addr){ int d=newv(); put(LD,d,addr,0); return d; }
static void st(int addr,int r){ put(ST,addr,r,0); }
static int op(int k,int a,int b){ int d=newv(); put(k,d,a,b); return d; }
static int not_(int a){ return op(XOR,a,IALL); }
static int addr(int buf,int lane,int z){ return buf*1600+lane*64+z; }
typedef struct { int cost, S; int v1[5], v2[5], isand[5], ri[5], qq[5]; int ok, tj; } Plan;
/* trick (10-gate chi row): with trick=1 the plan may also take output tj from the finished output k = tj+1 of the same row:
   not y and z == not (y xor (not z and w)) and z, so the term of tj reads output k (stored polarity qq[k]) in place of input k. */
static Plan plan_row_t(const int *pB, const int *qwant, const int *need, int nneed, int trick) {
  Plan best; memset(&best,0,sizeof best);
  int inneed[5]={0,0,0,0,0}; for (int i=0;i<nneed;i++) inneed[need[i]]=1;
  for (int tj=-1; tj<(trick?5:0); tj++) {
  if (tj>=0 && !(inneed[tj] && inneed[(tj+1)%5])) continue;
  for (int S=0; S<32; S++) {
    int cS = __builtin_popcount(S), c = cS, good = 1;
    Plan p; memset(&p,0,sizeof p);
    for (int i=0;i<=nneed && good;i++) {
      int X = i<nneed ? need[i] : tj; if (i<nneed ? X==tj : tj<0) continue;
      int a=(X+1)%5, b=(X+2)%5, minr=9, found=0, tr=(X==tj);
      for (int v1=0; v1<=((!tr&&((S>>a)&1))?1:0); v1++)
       for (int v2=0; v2<=(((S>>b)&1)?1:0); v2++) {
        int p1=(tr?p.qq[a]:pB[a])^v1, p2=pB[b]^v2;
        if (p1==p2) continue;
        int isand = (p1==1), flip = isand?0:1;
        for (int ri=0; ri<2; ri++) {
          int qq = pB[X]^flip^ri;
          if (qwant[X] < 0 || qq == qwant[X]) {
            if (ri < minr) { minr=ri; found=1; p.v1[X]=v1; p.v2[X]=v2; p.isand[X]=isand; p.ri[X]=ri; p.qq[X]=qq; }
          }
        }
       }
      if (!found) good=0; else c += minr;
    }
    if (!good) continue;
    if (!best.ok || c < best.cost) { p.cost=c; p.S=S; p.ok=1; p.tj=tj; best=p; }
  }
  }
  return best;
}
static Plan plan_row(const int *pB, const int *qwant, const int *need, int nneed) { return plan_row_t(pB,qwant,need,nneed,0); }
static void chi_row(const int *s, const Plan *pl, const int *need, int nneed, int *out) {
  int inv[5] = {-1,-1,-1,-1,-1};
  for (int j=0;j<5;j++) if ((pl->S>>j)&1) inv[j] = not_(s[j]);
  for (int i=0;i<=nneed;i++) {
    int X = i<nneed ? need[i] : pl->tj; if (i<nneed ? X==pl->tj : pl->tj<0) continue;
    int a=(X+1)%5, b=(X+2)%5;
    int e1 = X==pl->tj ? out[a] : pl->v1[X]?inv[a]:s[a], e2 = pl->v2[X]?inv[b]:s[b];
    int u = pl->isand[X]?op(AND,e1,e2):op(OR,e1,e2);
    if (pl->ri[X]) u = not_(u);
    out[X] = op(XOR,s[X],u);
  }
}
static const int ALLN[5]={0,1,2,3,4};
static int IOTA(int z){ return z==0||z==1||z==3||z==7||z==15||z==31||z==63; }
static void gen_G(int src,int dst){
  n=0; nv=0; Plan pl[5];
  for (int Y=0;Y<5;Y++){ int pB[5], qw[5]; for (int X=0;X<5;X++){ pB[X]=pT[xmap(X,Y)][X]; qw[X]=Qp[X][Y]; } pl[Y]=plan_row_t(pB,qw,ALLN,5,1); }
  int rcv = ld(RCA); int C0[5], Cprev[5];
  for (int z=0; z<64; z++){
    int o[5][5], Cc[5]={-1,-1,-1,-1,-1};
    for (int Y=0;Y<5;Y++){
      int s[5], res[5];
      for (int X=0;X<5;X++){ int x=xmap(X,Y); s[X]=ld(addr(src,x+5*X,((z-ROT[x][X])%64+64)%64)); }
      chi_row(s,&pl[Y],ALLN,5,res);
      for (int X=0;X<5;X++){
        int v=res[X];
        if (Y==0&&X==0&&IOTA(z)){ int m=op(SHR,rcv,IMM(z)); m=op(AND,m,IMM(1)); m=op(SUB,m,IMM(1)); v=op(XOR,v,m); }
        o[X][Y]=v;
        Cc[X] = Cc[X]<0 ? v : op(XOR,Cc[X],v);
      }
    }
    if (z==0){
      for (int Y=0;Y<5;Y++) for (int X=0;X<5;X++) st(addr(dst,X+5*Y,0),o[X][Y]);
      memcpy(C0,Cc,sizeof Cc);
    } else {
      int D[5]; for (int X=0;X<5;X++) D[X]=op(XOR,Cc[(X+4)%5],Cprev[(X+1)%5]);
      for (int Y=0;Y<5;Y++) for (int X=0;X<5;X++){ int t=op(XOR,o[X][Y],D[X]); st(addr(dst,X+5*Y,z),t); }
    }
    memcpy(Cprev,Cc,sizeof Cc);
  }
  int D[5]; for (int X=0;X<5;X++) D[X]=op(XOR,C0[(X+4)%5],Cprev[(X+1)%5]);
  for (int Y=0;Y<5;Y++) for (int X=0;X<5;X++){ int r=ld(addr(dst,X+5*Y,0)); int t=op(XOR,r,D[X]); st(addr(dst,X+5*Y,0),t); }
}
static int pOut[4];

/* ---- AFF: affine forms over u (bits 0..255 = u_l[z] at 64*l+z; word 4 bit 0 = constant 1) ---- */
typedef struct { uint64_t w[5]; } Fm;
static const uint64_t KL[25] = {0xc9a9d386ab38e13aULL,0,0x9be65c0f48819e78ULL,0xa42df10543300344ULL,0,0x9d9a486de15a3242ULL,0,
  0x62628f16871056a6ULL,0x8d7196f55bc91f8bULL,0,0x793ea2677e200f74ULL,0x7e8d7d4cce830045ULL,0xfe58db5a1de5126aULL,
  0x1b571a79774b02ceULL,0x8a2d82f8f9dcb705ULL,0xf01a6a80f9aae74bULL,0x8000000000000006ULL,0,0,0,0,0,0,0,0};
#define NC 2400
#define HT 4096
typedef struct { Fm SA[25][64], RW[5][64], CC[5][64]; uint64_t ck[NC][4]; int cr[NC], cp[NC], ht[HT], nk[1024], nvv[1024]; } AffMem;
static AffMem *AM;  /* mmapped for AFF only, unmapped before the G sections */
#define SA (AM->SA)
#define RW (AM->RW)
#define CC (AM->CC)
#define ck (AM->ck)
#define cr (AM->cr)
#define cp (AM->cp)
#define ht (AM->ht)
#define nk (AM->nk)
#define nvv (AM->nvv)
static void fx(Fm *d,const Fm *a,const Fm *b){ for(int i=0;i<5;i++) d->w[i]=a->w[i]^b->w[i]; }
static int isvar(const Fm *f){ return (f->w[0]|f->w[1]|f->w[2]|f->w[3])!=0; }
static void setbit(Fm *f,int b){ f->w[b>>6]^=1ULL<<(b&63); }
static void theta_f(Fm A[25][64]){
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ Fm t=A[x][z]; for(int y=1;y<5;y++) fx(&t,&t,&A[x+5*y][z]); CC[x][z]=t; }
  for(int i=0;i<25;i++) for(int z=0;z<64;z++){ int x=i%5; fx(&A[i][z],&A[i][z],&CC[(x+4)%5][z]); fx(&A[i][z],&A[i][z],&CC[(x+1)%5][(z+63)%64]); }
}
static void forms(void){
  memset(SA,0,sizeof SA);
  for(int i=0;i<25;i++) for(int z=0;z<64;z++){
    if((KL[i]>>z)&1) SA[i][z].w[4]=1;
    int us[2], nu=0;
    if(i==1){us[0]=0;nu=1;} if(i==6){us[0]=1;nu=1;} if(i==11){us[0]=0;us[1]=1;nu=2;}
    if(i==4){us[0]=2;nu=1;} if(i==9){us[0]=3;nu=1;} if(i==14){us[0]=2;us[1]=3;nu=2;}
    for(int j=0;j<nu;j++) setbit(&SA[i][z],64*us[j]+z);
  }
  theta_f(SA);
  /* rho and pi in place: lane x+5y (rotated) moves to y+5((2x+3y)%5); one lane buffer (RW[0]) per cycle */
  { int done[25]={0};
    for(int s0=0;s0<25;s0++){ if(done[s0]) continue;
      int i=s0; memcpy(RW[0],SA[i],sizeof RW[0]);
      for(;;){ int x=i%5, y=i/5, j=y+5*((2*x+3*y)%5);
        memcpy(RW[1],SA[j],sizeof RW[1]);
        for(int z=0;z<64;z++) SA[j][z]=RW[0][((z-ROT[x][y])%64+64)%64];
        done[i]=1; memcpy(RW[0],RW[1],sizeof RW[0]); i=j; if(i==s0) break; } } }
  for(int y=0;y<5;y++){
    for(int x=0;x<5;x++) memcpy(RW[x],SA[x+5*y],sizeof RW[x]);
    for(int x=0;x<5;x++) for(int z=0;z<64;z++){
      const Fm *nb=&RW[(x+1)%5][z], *c=&RW[(x+2)%5][z]; Fm p; memset(&p,0,sizeof p);
      if(!isvar(nb)){ if(!(nb->w[4]&1)) p=*c; }
      else if(!isvar(c)){ if(c->w[4]&1){ p=*nb; p.w[4]^=1; } }
      else { eprintf("round 0 not linear\n"); exit(1); }
      fx(&SA[x+5*y][z],&RW[x][z],&p);
    }
  }
  for(int z=0;z<64;z++) if((RCA0>>z)&1) SA[0][z].w[4]^=1;
}
static int nc;
static unsigned hsh(const uint64_t *m){ uint64_t h=m[0]*0x9E3779B97F4A7C15ULL^m[1]*0xC2B2AE3D27D4EB4FULL^m[2]*0x165667B19E3779F9ULL^m[3]*0x27D4EB2F165667C5ULL; return (unsigned)(h>>40)&(HT-1); }
static int cfind(const uint64_t *m){ unsigned h=hsh(m); while(ht[h]>=0){ int i=ht[h]; if(!memcmp(ck[i],m,32)) return i; h=(h+1)&(HT-1);} return -1; }
static int cadd(const uint64_t *m,int r,int p){ unsigned h=hsh(m); while(ht[h]>=0) h=(h+1)&(HT-1); if(nc>=NC){eprintf("NC\n");exit(1);} memcpy(ck[nc],m,32); cr[nc]=r; cp[nc]=p; ht[h]=nc; return nc++; }
static int var(const uint64_t *m){
  int i=cfind(m); if(i>=0) return i;
  int hi=-1, cnt=0; for(int b=0;b<256;b++) if((m[b>>6]>>(b&63))&1){ hi=b; cnt++; }
  if(cnt==1) return cadd(m, ld(addr(2,hi/64,hi%64)), 0);
  uint64_t r[4]; memcpy(r,m,32); r[hi>>6]^=1ULL<<(hi&63);
  uint64_t h1[4]={0,0,0,0}; h1[hi>>6]=1ULL<<(hi&63);
  int i1=var(r); int i2=var(h1);
  return cadd(m, op(XOR,cr[i1],cr[i2]), cp[i1]^cp[i2]);
}
static int xr(const Fm *f,const Fm *g){
  uint64_t m[4]; for(int k=0;k<4;k++) m[k]=f->w[k]^g->w[k];
  int i=cfind(m); if(i>=0) return i;
  int i1=cfind(f->w), i2=cfind(g->w);
  return cadd(m, op(XOR,cr[i1],cr[i2]), cp[i1]^cp[i2]);
}
static Fm C1(int x,int z){
  Fm f; memset(&f,0,sizeof f);
  for(int y=0;y<5;y++){ const Fm *g=&SA[x+5*y][z];
    if(isvar(g)){ var(g->w); if(isvar(&f)) xr(&f,g); }
    fx(&f,&f,g); }
  return f;
}
static void gen_aff(int dst){
  AM=(AffMem*)(CODE+((CODESZ-sizeof(AffMem))&~4095L));   /* the tail of the empty code region (AFF is generated first) */
  n=0; nv=0; nc=0; for(int i=0;i<HT;i++) ht[i]=-1;
  forms();
  int nnot=0;

  for(int zz=0;zz<64;zz++){
    int z=(zz+1)%64; Fm Cz[5], Cm[5];
    for(int x=0;x<5;x++) Cz[x]=C1(x,z);
    for(int x=0;x<5;x++) Cm[x]=C1(x,(z+63)%64);
    for(int x=0;x<5;x++){
      Fm d; fx(&d,&Cz[(x+4)%5],&Cm[(x+1)%5]);
      xr(&Cz[(x+4)%5],&Cm[(x+1)%5]);
      int cd=cfind(d.w), rd=cr[cd], pdd=cp[cd], nd=-1;   /* ~D made once per D value, when first needed */
      for(int q=0;q<nnot;q++) if(nk[q]==rd) nd=nvv[q];
      for(int pass=0;pass<2;pass++) for(int y=0;y<5;y++){
        const Fm *av=&SA[x+5*y][z]; if(isvar(av)!=pass) continue;
        int want=(int)((av->w[4]^d.w[4])&1)^pT[x][y];
        if(want!=pdd && nd<0){ if(nnot>=1024) exit(1); nd=not_(rd); nk[nnot]=rd; nvv[nnot]=nd; nnot++; }
        int dw = want==pdd ? rd : nd, r;
        if(pass){ int ca=var(av->w); r=op(XOR,cr[ca],dw); } else r=dw;
        st(addr(dst,x+5*y,z),r);
      }
    }
  }
}
static void gen_R23(int src){
  n=0; nv=0;
  int pB[5]; for (int X=0;X<5;X++) pB[X]=pT[xmap(X,0)][X];
  int qw[5]={-1,-1,-1,0,-1}; int need[4]={0,1,2,3};
  Plan pl=plan_row_t(pB,qw,need,4,1);
  for (int X=0;X<4;X++) pOut[X]=pl.qq[X];

  for (int z=0;z<64;z++){
    int s[5],res[5];
    for (int X=0;X<5;X++){ int x=xmap(X,0); s[X]=ld(addr(src,x+5*X,((z-ROT[x][X])%64+64)%64)); }
    chi_row(s,&pl,need,4,res);
    for (int X=0;X<4;X++){
      int v=res[X];
      /* iota of round 23 folded into PD */
      st(addr(2,X,z),v);
      /* the prefilter word is formed after the step from the output planes (proof.md Section 4.1) */
    }
  }
}
/* ---- resident allocation + streamed emission ---- */
static char obuf[1<<13]; static int olen;
static void flush(void){ wr(1,obuf,olen); olen=0; }
static int capmode=1;
static void capture(const char *s);
static void pr(const char *s){ if(capmode){ capture(s); return; } int l=strlen(s); if(olen+l>(int)sizeof obuf) flush(); memcpy(obuf+olen,s,l); olen+=l; }
static void fmt(char *b,int kind,int num){ /* kind 0 M,1 T,2 imm */
  if(kind==0) sprintf(b,"M%d",num); else if(kind==1) sprintf(b,"T%d",num);
  else if(num==IALL) strcpy(b,"#ALL"); else sprintf(b,"#%d",-1-num);
}
static void nm(int x,int *kind,int *num){
  if(x<0){ *kind=2; *num=x; return; }
  if(ldal[x]>=0){ *kind=0; *num=ldal[x]; return; }
  if(nameA[x]>=0){ *kind=0; *num=nameA[x]; return; }
  *kind=1; *num=tmpn[x];
}
static void resident(const char *name){
  char b[96], l1[40], l2[40], l3[40];
  for(int i=0;i<nv;i++){ last[i]=-1; nameA[i]=-1; ldal[i]=-1; tmpn[i]=-1; }
  for(int i=0;i<n;i++){ In *p=&ins[i];
    if(p->k==LD && p->a!=RCA) ldal[p->d]=p->a;
    if(p->k==ST && nameA[p->a]<0) nameA[p->a]=p->d; }
  for(int i=0;i<n;i++){ In *p=&ins[i];
    if(p->k==LD) continue;
    if(p->k==ST){ if(p->a>=0) last[p->a]=i; }
    else { if(p->a>=0) last[p->a]=i; if(p->b>=0) last[p->b]=i; } }
  unsigned long long freem=0; int nxtT=0; long cnt=0;
  snprintf(b,sizeof b,"== %s\n",name); pr(b);
  for(int i=0;i<n;i++){ In *p=&ins[i];
    int k=p->k;
    if(k==LD){
      if(p->a==RCA){
        int t; if(freem){ t=__builtin_ctzll(freem); freem&=~(1ULL<<t);} else t=nxtT;
        if(t==nxtT) nxtT++;
        tmpn[p->d]=t;
        snprintf(b,sizeof b,"ld T%d RC\n",t); pr(b); cnt++;
        if(last[p->d]<0) freem|=1ULL<<t;
      }
      continue;
    }
    if(k==ST){
      int ks,ns; nm(p->a,&ks,&ns);
      if(!(ks==0&&ns==p->d)){
        fmt(l1,0,p->d); fmt(l2,ks,ns); snprintf(b,sizeof b,"mov %s %s\n",l1,l2); pr(b); cnt++; }
      continue;
    }
    int srcs[2]={p->a,p->b};
    for(int j=0;j<2;j++){ int s=srcs[j]; if(s>=0 && tmpn[s]>=0 && last[s]==i && !(j==1&&srcs[0]==s)) freem|=1ULL<<tmpn[s]; }
    int d=p->d;
    if(nameA[d]<0){
      int t; if(freem){ t=__builtin_ctzll(freem); freem&=~(1ULL<<t);} else t=nxtT;
      if(t==nxtT) nxtT++;
      tmpn[d]=t;
      if(last[d]<0) freem|=1ULL<<t;
    }
    int kd,nd,ka,na,kb,nb; nm(d,&kd,&nd); nm(p->a,&ka,&na); nm(p->b,&kb,&nb);
    fmt(l1,kd,nd); fmt(l2,ka,na); fmt(l3,kb,nb);
    snprintf(b,sizeof b,"%s %s %s %s\n",KN[k],l1,l2,l3); pr(b); cnt++;
  }
  snprintf(b,sizeof b,"END %ld\n",cnt); pr(b);
}
/* ---- S24LS: capture of the resident sections, then the 1,024-register allocation with charged ld/st/mov ---- */
#define KBMAX 1024
static int KB;                         /* boundary set size, chosen by select_kb() */
enum { XLD, XST, XXOR, XAND, XOR_, XSHR, XSUB, XMOV };
static const char *XKN[] = {"ld","st","xor","and","or","shr","sub","mov"};
static unsigned char SK[1][MAXOP]; static short SD[1][MAXOP], SAo[1][MAXOP], SBo[1][MAXOP];   /* the one section being processed */ static int SN[4], cursec = -1;
static int parse_opnd(const char *t){
  if(t[0]=='M') return atoi(t+1);
  if(t[0]=='T') return 4800+atoi(t+1);
  if(!strcmp(t,"RC")) return -2;
  if(!strcmp(t,"#ALL")) return -3;
  if(t[0]=='#') return -(16+atoi(t+1));
  return -1;
}
static void capture(const char *s){
  char a[4][24]; int m=0, i=0;
  if(s[0]=='='){ const char *nmx=s+3; cursec = !strncmp(nmx,"AFF",3)?0: !strncmp(nmx,"GA",2)?1: !strncmp(nmx,"GB",2)?2:3; SN[cursec]=0; return; }
  if(s[0]=='E') return;
  while(*s && *s!='\n' && m<4){ while(*s==' ') s++; i=0; while(*s && *s!=' ' && *s!='\n' && i<23) a[m][i++]=*s++; a[m][i]=0; if(i) m++; }
  int k; for(k=0;k<8;k++) if(!strcmp(a[0],XKN[k])) break;
  int j=SN[cursec]++;
  SK[0][j]=k; SD[0][j]=parse_opnd(a[1]);
  SAo[0][j]= m>2? parse_opnd(a[2]) : -1; SBo[0][j]= m>3? parse_opnd(a[3]) : -1;
}
static void nmstr(char *b,int id){ if(id<4800) sprintf(b,"M%d",id); else sprintf(b,"T%d",id-4800); }
static int cmpname(int x,int y){ char a[16],b[16]; nmstr(a,x); nmstr(b,y); return strcmp(a,b); }

/* per-section working arrays */
static int nentry, nvals;
static unsigned char FL[MAXV];   /* bit 1 output, 2 in memory, 4 placed at exit */
static short occ[KR]; static char freef[KR], reserved[KR];
static short xord[2000]; static int nx;
static int cnt_ld, cnt_st, cnt_mov, emit_on; static long nlines, cnt_lines_all;
static short exitmap[NNM];
static short first_entry[3][2000]; static int nfirst[4];
static char slot_used[NNM];
static long ncode;
static void code_word(const char *s){   /* one 32-byte instruction record: the listing line, zero padded */
  if(ncode+32>CODESZ){ eprintf("code region full\n"); exit(3); }
  unsigned char *w=CODE+ncode; int i=0; for(;s[i] && s[i]!='\n' && i<32;i++) w[i]=(unsigned char)s[i]; for(;i<32;i++) w[i]=0; ncode+=32; }
static void out(const char *s){ if(emit_on){ pr(s); nlines++; code_word(s); } }
static void opnd(char *b,int x,int r){
  if(x==-2) strcpy(b,"RC"); else if(x==-1) strcpy(b,"-");
  else if(x==-3){ b[0]='#'; for(int i=0;i<64;i++) b[1+i]='f'; b[65]=0; }
  else if(x<=-16) sprintf(b,"#%x",-(x+16)); else sprintf(b,"r%d",r);
}
static void analyse(int s){
  int n=SN[s]; nvals=n; nentry=0;
  for(int i=0;i<NNM;i++){ curv[i]=-1; verc[i]=0; }
  for(int i=0;i<n;i++){
    UC[i]=0;
    if(SK[0][i]!=XLD){ int ops2[2]={SAo[0][i],SBo[0][i]};
      for(int j=0;j<2;j++){ int x=ops2[j]; if(x<0) continue;
        if(curv[x]<0){ vname[nvals]=x; vver[nvals]=0; curv[x]=nvals; entry[nentry++]=nvals; nvals++; }
        U[i][UC[i]++]=curv[x]; } }
    int d=SD[0][i]; vname[i]=d; vver[i]=++verc[d]; curv[d]=i;
  }
}
static int vless(int a,int b){ /* (name string, version) of a < of b */
  if(vname[a]!=vname[b]) return cmpname(vname[a],vname[b])<0;
  return vver[a]<vver[b];
}
static void emit_st(int v,int p){ char b[64],nb[16]; nmstr(nb,vname[v]); snprintf(b,sizeof b,"st r%d %s\n",p,nb); out(b); if(emit_on) slot_used[vname[v]]=1; }
static void emit_ld(int v,int p){ char b[64],nb[16]; nmstr(nb,vname[v]); snprintf(b,sizeof b,"ld r%d %s\n",p,nb); out(b); if(emit_on) slot_used[vname[v]]=1; }
static void emit_mov(int q,int p){ char b[64]; snprintf(b,sizeof b,"mov r%d r%d\n",q,p); out(b); }
static void release_(int p){ occ[p]=-1; freef[p]=1; }
static int free_reg(const int *prot,int np,int avoid){
  int best=-1;
  for(int p=0;p<KR;p++) if(freef[p]){ if(best<0) best=p; if(!avoid) break; if(!reserved[p]) return p; }
  if(best>=0) return best;
  int v=-1;
  for(int p=0;p<KR;p++){ int w=occ[p]; if(w<0 || reg[w]!=p) continue;
    int pr_=0; for(int j=0;j<np;j++) if(prot[j]==w) pr_=1; if(pr_) continue;
    if(v<0 || key[w]>key[v] || (key[w]==key[v] && vless(w,v))) v=w; }
  int p=reg[v]; reg[v]=-1; release_(p);
  if(!(FL[v]&2) && (key[v]<INFV || (FL[v]&1) || xreg[v]!=-1)){ cnt_st++; FL[v]|=2; emit_st(v,p); }
  return p;
}
static void put_(int v,int p,int k){ reg[v]=p; occ[p]=v; freef[p]=0; key[v]=k; }
static void drop_(int v){ int p=reg[v]; reg[v]=-1; release_(p);
  if((FL[v]&1) && xreg[v]==-1 && !(FL[v]&2)){ cnt_st++; FL[v]|=2; emit_st(v,p); } }
/* E: entry name -> register (or -1); X: list of names with forced register or -2 (natural); outs: M names written (or OUT) */
static void alloc_sec(int s,const short *Emap,const short *Xn,const short *Xr,int nX,int outs_out){
  analyse(s); int n=SN[s];
  for(int v=0;v<nvals;v++){ xreg[v]=-1; FL[v]=0; reg[v]=-1; nxt[v]=INFV; }
  nx=0; for(int j=0;j<nX;j++){ int v=curv[Xn[j]]; xreg[v]=Xr[j]; xord[nx++]=v; }
  for(int nm_=0;nm_<NNM;nm_++){ int v=curv[nm_]; if(v<0||v>=n) continue;   /* written name: final version */
    if(outs_out){ if(nm_>=3200 && nm_<3456) FL[v]|=1; } else if(nm_<4800) FL[v]|=1; }
  for(int j=0;j<nx;j++) nxt[xord[j]]=n;
  for(int i=n-1;i>=0;i--){
    for(int j=0;j<UC[i];j++) unu[i][j]=nxt[U[i][j]];
    dnu[i]=nxt[i]; nxt[i]=INFV;
    for(int j=0;j<UC[i];j++) nxt[U[i][j]]=i; }
  for(int p=0;p<KR;p++){ occ[p]=-1; freef[p]=1; reserved[p]=0; }
  for(int e=0;e<nentry;e++){ int v=entry[e], r=Emap[vname[v]];
    if(r>=0){ reg[v]=r; occ[r]=v; freef[r]=0; key[v]=nxt[v]; } else FL[v]|=2; }
  for(int j=0;j<nx;j++) if(xreg[xord[j]]>=0) reserved[xreg[xord[j]]]=1;
  cnt_ld=cnt_st=cnt_mov=0;
  char b[160],l2[80],l3[80];
  for(int i=0;i<n;i++){
    int u[2]={U[i][0],U[i][1]}, nu_=UC[i];
    for(int j=0;j<nu_;j++){ int v=u[j];
      if(reg[v]<0){ int p=xreg[v]>=0? xreg[v] : -1;
        if(p<0 || occ[p]>=0) p=free_reg(u,nu_,1);
        cnt_ld++; emit_ld(v,p); put_(v,p,unu[i][j]); }
      else key[v]=unu[i][j]; }
    int ureg[2]; for(int j=0;j<nu_;j++) ureg[j]=reg[u[j]];
    for(int j=0;j<nu_;j++){ int v=u[j]; if(unu[i][j]==INFV && reg[v]>=0) drop_(v); }
    int d=i, p;
    if(xreg[d]>=0){
      p=xreg[d];
      if(occ[p]>=0){
        int w=occ[p]; reg[w]=-1; release_(p); freef[p]=0;
        int hold[2], nh=0; for(int j=0;j<nu_;j++) if(freef[ureg[j]]){ int dup=0; for(int t=0;t<nh;t++) if(hold[t]==ureg[j]) dup=1; if(!dup){ hold[nh++]=ureg[j]; freef[ureg[j]]=0; } }
        int prot[3]; int np=0; for(int j=0;j<nu_;j++) prot[np++]=u[j]; prot[np++]=w;
        int q=free_reg(prot,np,1);
        for(int t=0;t<nh;t++) freef[hold[t]]=1;
        cnt_mov++; emit_mov(q,p);
        reg[w]=q; occ[q]=w; freef[q]=0; release_(p);
      }
    } else p=free_reg(u,nu_,1);
    if(emit_on){
      int k=SK[0][i], ri=0, a=SAo[0][i], bb=SBo[0][i];
      opnd(l2,a, a>=0? ureg[ri++] : 0); opnd(l3,bb, bb>=0? ureg[ri++] : 0);
      snprintf(b,sizeof b,"%s r%d %s %s\n",XKN[k],p,l2,l3); out(b);
    }
    put_(d,p,dnu[i]);
    if(dnu[i]==INFV) drop_(d);
  }
  for(int j=0;j<nx;j++){ int v=xord[j], p=xreg[v];
    if(p==-2){
      if(reg[v]<0){ int prot[2000], np=0; for(int t=0;t<nx;t++) if((FL[xord[t]]&4)) prot[np++]=xord[t];
        int q=free_reg(prot,np,0); cnt_ld++; reg[v]=q; occ[q]=v; freef[q]=0; emit_ld(v,q); }
      FL[v]|=4; continue; }
    if(reg[v]==p){ FL[v]|=4; continue; }
    if(occ[p]>=0){
      int w=occ[p]; release_(p); freef[p]=0;
      int prot[2002], np=0; prot[np++]=w; prot[np++]=v; for(int t=0;t<nx;t++) if((FL[xord[t]]&4)) prot[np++]=xord[t];
      int q=free_reg(prot,np,0); occ[q]=w; reg[w]=q; freef[q]=0; cnt_mov++; release_(p);
      emit_mov(q,p);
    }
    if(reg[v]>=0){ emit_mov(p,reg[v]); release_(reg[v]); cnt_mov++; }
    else { cnt_ld++; emit_ld(v,p); }
    reg[v]=p; occ[p]=v; freef[p]=0; FL[v]|=4;
  }
  /* remaining outputs in memory, in (name string, version) order */
  { short *ol=&UU.a.U_[0][0]; int no=0;   /* U is no longer needed here */
    for(int v=0;v<nvals;v++) if((FL[v]&1) && xreg[v]==-1 && !(FL[v]&2)) ol[no++]=v;
    for(int a=1;a<no;a++){ int t=ol[a], c=a; while(c>0 && vless(t,ol[c-1])){ ol[c]=ol[c-1]; c--; } ol[c]=t; }
    for(int t=0;t<no;t++){ cnt_st++; emit_st(ol[t],reg[ol[t]]); } }
  for(int i=0;i<NNM;i++) exitmap[i]=-1;
  for(int j=0;j<nx;j++) exitmap[vname[xord[j]]]=reg[xord[j]];
}
static short E1[NNM], E0[NNM], EO[NNM]; static short X1n[KBMAX], X1r[KBMAX], X0n[KBMAX], X0r[KBMAX], XOn[256], XOr[256];
static long stepcount, seclen[4];
static void gen_sec(int s){            /* (re)generate one resident section into SK/SD/SAo/SBo */
  capmode=1;
  if(s==0){ gen_aff(1); resident("AFF"); }
  if(s==1){ gen_G(0,1); resident("GA"); }
  if(s==2){ gen_G(1,0); resident("GB"); }
  if(s==3){ gen_R23(1); resident("R23"); }
  capmode=0;
}
static long eval_kb(int emit){
  /* sections: 0 AFF, 1 GA, 2 GB, 3 R23; boundary sets from the consumer's first-use order */
  for(int s=1;s<=2;s++){ gen_sec(s); analyse(s); nfirst[s]=nentry; for(int e=0;e<nentry;e++) first_entry[s][e]=vname[entry[e]]; }
  for(int i=0;i<NNM;i++) E1[i]=-1;
  int k1=0, k0=0;
  for(int e=0;e<nfirst[2] && k1<KB;e++){ int nm_=first_entry[2][e]; if(nm_>=1600&&nm_<3200){ X1n[k1]=nm_; X1r[k1]=k1; E1[nm_]=k1; k1++; } }
  for(int e=0;e<nfirst[1] && k0<KB;e++){ int nm_=first_entry[1][e]; if(nm_<1600){ X0n[k0]=nm_; X0r[k0]=-2; k0++; } }
  for(int l=0;l<4;l++) for(int z=0;z<64;z++){ XOn[l*64+z]=3200+l*64+z; XOr[l*64+z]=-2; }
  emit_on=0;
  gen_sec(2); alloc_sec(2,E1,X0n,X0r,KB,0); memcpy(E0,exitmap,sizeof E0);
  gen_sec(3); alloc_sec(3,E1,XOn,XOr,256,1); memcpy(EO,exitmap,sizeof EO);
  char b[32];
  int order[4]={0,2,1,3}; const char *nmS[4]={"AFF","GA","GB","R23"};
  stepcount=61;
  for(int t=0;t<4;t++){ int s=order[t]; long before=nlines;
    gen_sec(s); emit_on=emit;
    long l0=cnt_lines_all;
    if(emit){ snprintf(b,sizeof b,"== %s\n",nmS[s]); pr(b); }
    if(s==0) alloc_sec(0,EO,X1n,X1r,KB,0);
    if(s==2) alloc_sec(2,E1,X0n,X0r,KB,0);
    if(s==1) alloc_sec(1,E0,X1n,X1r,KB,0);
    if(s==3) alloc_sec(3,E1,XOn,XOr,256,1);
    emit_on=0; (void)before; (void)l0;
    seclen[s]=SN[s]+cnt_ld+cnt_st+cnt_mov; stepcount+= (s==2? 11 : s==1? 11 : 1)*seclen[s];
    if(emit) eprintf("%s ops %d ld %d st %d mov %d lines %ld\n",nmS[s],SN[s],cnt_ld,cnt_st,cnt_mov,seclen[s]);
  }
  if(emit){ int ns=0; for(int i=0;i<NNM;i++) ns+=slot_used[i];
    eprintf("step %ld spill slots %d code bytes written %ld\n",stepcount,ns,ncode); }
  return stepcount;
}
/* Selection 1: the polarity pattern. Every q < 2^25 whose five rows admit stored polarities equal to q (a fixed point of
   one round) at total row cost <= 7 is a candidate (row cost = plan_row cost); among the candidates the one with the
   fewest operations of the load/store sections AFF + 22 x G + R23 is taken, ties to the smaller q. */
static short tabq[32][32];
static void select_q(void){
  for(int pB=0;pB<32;pB++) for(int qr=0;qr<32;qr++){ int pb[5], qw[5]; for(int X=0;X<5;X++){ pb[X]=(pB>>X)&1; qw[X]=(qr>>X)&1; }
    Plan p=plan_row(pb,qw,ALLN,5); tabq[pB][qr]= p.ok? p.cost : 99; }
  static int cand[256]; int nc_=0; long ncand_all=0;
  for(long q=0;q<(1L<<25);q++){
    int qp[5][5], c5[5], d5[5], cost=0;
    for(int X=0;X<5;X++) for(int Y=0;Y<5;Y++) qp[X][Y]=(q>>(X+5*Y))&1;
    for(int X=0;X<5;X++){ int s=0; for(int Y=0;Y<5;Y++) s+=qp[X][Y]; c5[X]=s&1; }
    for(int X=0;X<5;X++) d5[X]=c5[(X+4)%5]^c5[(X+1)%5];
    for(int Y=0;Y<5 && cost<=7;Y++){ int pB=0, qr=0; for(int X=0;X<5;X++){ int x=xmap(X,Y); pB|=(qp[x][X]^d5[x])<<X; qr|=qp[X][Y]<<X; } cost+=tabq[pB][qr]; }
    if(cost<=7){ ncand_all++; if(nc_<256) cand[nc_++]=(int)q; }
  }
  long best=-1, bq=0;
  for(int i=0;i<nc_;i++){ Q=cand[i]; pol();
    gen_aff(1); long t=n; gen_G(0,1); t+=22L*n; gen_R23(1); t+=n;
    eprintf("q %ld ldst-sections %ld\n",(long)cand[i],t);
    if(best<0 || t<best){ best=t; bq=cand[i]; } }
  Q=bq; pol();
  eprintf("candidates %ld (kept %d); chosen q %ld with %ld operations\n",ncand_all,nc_,bq,best);
}
/* Selection 2: the boundary set size, over the declared list; the smallest step wins, ties to the smaller size. */
static const int KBS[7]={930,945,960,975,990,1000,1012};
static void select_kb(void){
  long best=-1; int bk=0;
  for(int i=0;i<7;i++){ KB=KBS[i]; long st_=eval_kb(0); eprintf("KB %d step %ld\n",KB,st_); if(best<0||st_<best){ best=st_; bk=KB; } }
  KB=bk; eprintf("chosen KB %d step %ld\n",bk,best);
}

int cmain(long *sp){
  (void)sp;
  select_q();
  select_kb();
  eval_kb(1);
  flush();
  eprintf("generator peak RSS (VmHWM, includes the written code region) %ld KiB\n", vm_hwm_kib());
  return 0;
}

#ifdef VM
__attribute__((export_name("run_s24ls"))) int run_s24ls(void){ return cmain(0); }
#endif
```

## Appendix C. The constant-selection program gen.c (run as `gen 512`)

Our LS1 generator with `#define MAXN 32768` (output identical to MAXN 65535: trial 192, prog.bin SHA-256 016bc4cd3465a74680fa0b1844e750dcff72945c0f10be80fde95c5b26cbec88). Build: `gcc -O2 -static -nostdlib -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns -fno-stack-protector -fno-pie -no-pie -o gen gen.c -lgcc`; the attack uses the constants of the trial it reports.

```c
/* gen.c - LS1 step generator for sha3-256-r6 (6 prefix rounds of Keccak-f[1600]).
 * Freestanding (no libc) so the measured peak RSS is the generator's own working set.
 *
 * Chain function on physical 256-bit points u (4 lanes u0..u3):
 *   message m(u) = 128 bytes = lanes 0..15 of the absorbed state:
 *     lane 1 = u0, lane 6 = u1, lane 11 = u0^u1^K[11]   (column x=1, rows 0,1,2)
 *     lane 4 = u2, lane 9 = u3, lane 14 = u2^u3^K[14]   (column x=4, rows 0,1,2)
 *     other lanes 0..15 = constants K[l]; lane 16 = 0x8000000000000006 (SHA3 pad);
 *   F(u) = SHA3-256-r6(m(u)) XOR PD   (PD = fixed digest polarity mask of the program).
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
#define NROUNDS 6

/* ---------- node store ---------- */
#define MAXN 32768
#define NC 0xFFFF            /* constant marker */
enum { O_IN=0, O_XOR=1, O_AND=2, O_OR=3, O_NOT=4 };
#define F_OPM 7
#define F_K 8                /* physical constant of a linear node */
#define F_LIVE 16
#define F_LIN 32
static u8 nf[MAXN];          /* op | flags */
static u16 na[MAXN], nb[MAXN];
static u16 linid[MAXN];      /* form index for linear nodes; reused as reg[] */
#define MAXF 8192
static u64 form[MAXF][4]; static u16 formnode[MAXF]; static int nform;
#define FH 16384
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
    os("LS1 step ledger (256 lanes, one chain step, 6 rounds)\n");
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

## Appendix D. The looped replay program fops24_loop.py

Runs with `python3 fops24_loop.py` next to s24ls.py (it imports the constants, the round constants and the message map from it). It prints the operation counts used in Section 4.2 and checks 300 random points against the 24-round reference.

```python
# Looped one-walk program of F(u) = SHA3-256-r24(m(u)) ^ PD for the replay (rolled round body), exact op count.
# Layout: PRO = round 0 (affine part folded), writes the 25 lanes into registers A0..A24;
#         LOOP x NIT = body of two generic rounds (A -> B, B -> A), each round loads its round constant from the constant table (1 ld);
#         (R odd: one more generic round A -> B after the loop, its round constant an immediate, 1 op less than a loop round);
#         EPI = round 23, lanes 0..3 only, with the constant and PD folded.
# Op model of the unrolled one-walk program (xor/and/or/shl/shr, rot = 4 ops); plus ld (1 op) for the round constant; loop control 1 + NIT x (2 pointer steps + 2 test + 1 jump).
import hashlib, sys
sys.path.insert(0, ".")
from s24ls import ROT, RC_ALL as RC, M64, K, VAR, msg_ls, pd_of, digest, gen_R23
R = 24
NIT = (R - 2) // 2          # iterations of the two-round body (rounds 1 .. 2 NIT)
ODD = (R - 2) % 2           # R odd: one more generic round (round R - 2) after the loop, constant as an immediate
class Blk:
    ops = None
    def tmp(s):
        s.n += 1; return '%s%d' % (s.pre, s.n)
    def emit(s, op, x, y, dst=None):
        d = dst or s.tmp(); s.ops.append((d, op, x, y)); return d
    def rot(s, v, r):
        if r == 0: return v
        return s.emit('and', s.emit('or', s.emit('shl', v, r), s.emit('shr', v, 64 - r)), M64)
def newb(pre):
    b = Blk(); b.ops = []; b.n = 0; b.pre = pre
    return b


def round_ops(b, a, dst, rc):
    """generic round on register names a[0..24]; chi output lane i written to dst[i]; rc: register name holding the constant, or an int immediate"""
    c = []
    for x in range(5):
        t = a[x]
        for y in range(1, 5): t = b.emit('xor', t, a[x + 5 * y])
        c.append(t)
    d = [b.emit('xor', c[(x + 4) % 5], b.rot(c[(x + 1) % 5], 1)) for x in range(5)]
    bb = [0] * 25
    for x in range(5):
        for y in range(5):
            bb[y + 5 * ((2 * x + 3 * y) % 5)] = b.rot(b.emit('xor', a[x + 5 * y], d[x]), ROT[x][y])
    out = [None] * 25
    for y in range(5):
        for x in range(5):
            nb = b.emit('xor', bb[(x + 1) % 5 + 5 * y], M64)
            out[x + 5 * y] = b.emit('xor', bb[x + 5 * y], b.emit('and', nb, bb[(x + 2) % 5 + 5 * y]), dst[x + 5 * y])
    out[0] = b.emit('xor', out[0], rc, dst[0])
    return out
def build(pd):
    # prologue: round 0 with folding, (re-implemented here: only round 0)
    pro = newb('p'); sig = {}
    def emit(op, x, y, mask=False):
        cx, cy = isinstance(x, int), isinstance(y, int)
        if cx and cy:
            return {'xor': lambda: x ^ y, 'and': lambda: x & y, 'or': lambda: x | y, 'shl': lambda: (x << y) & M64, 'shr': lambda: x >> y}[op]()
        if cx and op in ('xor', 'and', 'or'): x, y, cx, cy = y, x, cy, cx
        s = None
        if op == 'xor':
            sx = sig.get(x) if not cx else (frozenset(), x)
            sy = sig.get(y) if not cy else (frozenset(), y)
            if sx is not None and sy is not None:
                s = (sx[0] ^ sy[0], sx[1] ^ sy[1])
                if not s[0]: return s[1]
        if not mask:
            if op in ('xor', 'or') and cy and y == 0: return x
            if op == 'and' and cy and y == 0: return 0
            if op == 'and' and cy and y == M64: return x
            if op == 'or' and cy and y == M64: return M64
        name = pro.emit(op, x, y)
        if op == 'xor' and s is not None: sig[name] = s
        return name
    for j in range(4): sig['in%d' % j] = (frozenset([j]), 0)
    def rot(v, r):
        if r == 0: return v
        if isinstance(v, int): return ((v << r) | (v >> (64 - r))) & M64
        return emit('and', emit('or', emit('shl', v, r), emit('shr', v, 64 - r)), M64, True)
    a = list(K)
    for lane, us in VAR.items():
        v = a[lane]
        for j in us: v = emit('xor', 'in%d' % j, v)
        a[lane] = v
    cc = []
    for x in range(5):
        t = a[x]
        for y in range(1, 5): t = emit('xor', t, a[x + 5 * y])
        cc.append(t)
    d = [emit('xor', cc[(x + 4) % 5], rot(cc[(x + 1) % 5], 1)) for x in range(5)]
    bb = [0] * 25
    for x in range(5):
        for y in range(5):
            bb[y + 5 * ((2 * x + 3 * y) % 5)] = rot(emit('xor', a[x + 5 * y], d[x]), ROT[x][y])
    a = [0] * 25
    for y in range(5):
        for x in range(5):
            nb = emit('xor', bb[(x + 1) % 5 + 5 * y], M64)
            a[x + 5 * y] = emit('xor', bb[x + 5 * y], emit('and', nb, bb[(x + 2) % 5 + 5 * y]))
    a[0] = emit('xor', a[0], RC[0])
    # keep only what is needed; rename lane values to A_i (the register the loop reads); constants are loaded (1 op each)
    live = {v for v in a if isinstance(v, str)}
    kept = []
    for op in reversed(pro.ops):
        if op[0] in live:
            kept.append(op); live |= {v for v in op[2:4] if isinstance(v, str)}
    kept.reverse()
    ren = {}
    for i, v in enumerate(a):
        if isinstance(v, str):
            assert v not in ren; ren[v] = 'A%d' % i
    pr = [(ren.get(dd, dd), o, ren.get(x, x), ren.get(y, y)) for dd, o, x, y in kept]
    nconst = 0
    for i, v in enumerate(a):
        if isinstance(v, int):
            pr.append(('A%d' % i, 'xor', v, 0)); nconst += 1      # load immediate into the register (1 op)
    # loop body: two rounds, A -> Bk -> A ; constants from the table
    body = newb('q')
    Ar = ['A%d' % i for i in range(25)]; Br = ['B%d' % i for i in range(25)]
    body.emit('ld', 'rcA', None, 'RCR'); round_ops(body, Ar, Br, 'RCR')
    body.emit('ld', 'rcB', None, 'RCR'); round_ops(body, Br, Ar, 'RCR')
    # (R odd) one more generic round after the loop, A -> B, round constant RC[R - 2] as an immediate
    single = newb('s')
    if ODD: round_ops(single, Ar, Br, RC[R - 2])
    # epilogue: round R - 1, lanes 0..3, constants folded; reads A (R even) or B (R odd)
    Er = Br if ODD else Ar
    ep = newb('e'); outs = []
    c = []
    for x in range(5):
        t = Er[x]
        for y in range(1, 5): t = ep.emit('xor', t, Er[x + 5 * y])
        c.append(t)
    dd = [ep.emit('xor', c[(x + 4) % 5], ep.rot(c[(x + 1) % 5], 1)) for x in range(5)]
    bq = [0] * 25
    for x in range(5):
        for y in range(5):
            bq[y + 5 * ((2 * x + 3 * y) % 5)] = ep.rot(ep.emit('xor', Er[x + 5 * y], dd[x]), ROT[x][y])
    for x in range(4):
        nb = ep.emit('xor', bq[(x + 1) % 5], M64)
        v = ep.emit('xor', bq[x], ep.emit('and', nb, bq[(x + 2) % 5]))
        k = pd[x] ^ (RC[R - 1] if x == 0 else 0)
        outs.append(ep.emit('xor', v, k, 'O%d' % x))
    live = set(outs); kept = []
    for op in reversed(ep.ops):
        if op[0] in live:
            kept.append(op); live |= {v for v in op[2:4] if isinstance(v, str)}
    kept.reverse()
    return pr, body.ops, kept, outs, nconst, single.ops

def ev(env, op, x, y):
    g = lambda v: env[v] if isinstance(v, str) else v
    f = {'xor': lambda p, q: p ^ q, 'and': lambda p, q: p & q, 'or': lambda p, q: p | q, 'shl': lambda p, q: (p << q) & M64, 'shr': lambda p, q: p >> q}
    return f[op](g(x), g(y))
def run(pr, body, ep, outs, u, single=()):
    env = {'in%d' % j: u[j] for j in range(4)}
    for dd, o, x, y in pr: env[dd] = ev(env, o, x, y)
    for it in range(NIT):
        for dd, o, x, y in body:
            if o == 'ld': env['RCR'] = RC[1 + 2 * it + (0 if x == 'rcA' else 1)]
            else: env[dd] = ev(env, o, x, y)
    for dd, o, x, y in single: env[dd] = ev(env, o, x, y)
    for dd, o, x, y in ep: env[dd] = ev(env, o, x, y)
    return [env[o] for o in outs]

if __name__ == '__main__':
    _, pOut, _ = gen_R23(1, qwant=[None, None, None, 0], ls=True)
    pd = pd_of(pOut)
    pr, body, ep, outs, nconst, single = build(pd)
    m = msg_ls([1, 2, 3, 4])
    if R == 24: assert digest(m, rounds=24) == hashlib.sha3_256(m).digest()
    for i in range(300):
        u = [int.from_bytes(hashlib.sha256(b'f%d_%d' % (i, l)).digest()[:8], 'little') for l in range(4)]
        dg = digest(msg_ls(u))
        assert run(pr, body, ep, outs, u, single) == [int.from_bytes(dg[8*l:8*l+8], 'little') ^ pd[l] for l in range(4)]
    LOOPCTL = 1 + NIT * (2 + 2 + 1)
    F = len(pr) + NIT * len(body) + len(single) + len(ep) + LOOPCTL
    print('PRO', len(pr), '(of which', nconst, 'constant loads) BODY', len(body), 'x', NIT, 'SINGLE', len(single), 'EPI', len(ep), 'loop control', LOOPCTL)
    print('F ops', F, 'code words', len(pr) + len(body) + len(single) + len(ep), '(+ loop instructions inside the 120 replay words); 300 random u checked vs the %d-round reference' % R)
```
