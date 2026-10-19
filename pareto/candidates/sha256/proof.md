# SHA-256, 46 rounds: bounded-restart bitsliced collision search with a tail-truncated walk

This package claims an ordinary 256-bit collision construction for SHA-256 reduced to its first 46 of 64 steps (standard IV, schedule, constants, padding and feed-forward after step 45) with total time
`2^124.15436` target compressions, memory `2^19.77015` bytes and success probability at least 0.39.
Memory is below one mebibyte, so the normalized objective
`normalizedTimeMemoryLog2 = timeLog2 + max(0, memoryLog2Bytes - 20)` equals **124.15436**.

It is lamb356's 64-round entry `3642e1cd-e391-41a7-81e0-456c02e4becd` (124.31538), itself TheTradoor's `55783d22-ce7f-4830-bfb5-4836ad4fb6e8` with a cheaper
kernel, carried to round count 46 with one new lever: **the walk is taken through a fixed public bijection `B` of the
final working state (Section 1.2) that lets the kernel stop early.** Collisions of the new walk are exactly the
collisions of the digest (Lemma 0), but the last five steps no longer form `T2`, the new `a` words, the final `e`
word or most of the last two `T1` sums. The search program, the machine declaration, the parameters and the
success argument are the predecessor's, unchanged; the kernel and the `COMP` charge change. No complete collision is
exhibited and the attack is not executed at full scale.

| Quantity | Value | Basis |
| --- | --- | --- |
| rounds | 46 | target profile `sha256-r46-prefix-v1` |
| time_log2 | 124.15436 | Section L; exact `log2 T = 124.154359230576`, rounded up |
| memory_log2_bytes | 19.77015 | Section L.4; 894,144 bytes |
| normalizedTimeMemoryLog2 | 124.15436 | memory below `2^20` adds zero |
| success_probability | 0.39 | Section P (random-function bound 0.390036155778183, rounded down) and H1 |
| preprocessing_log2 | 0 | the fixed program image is the algorithm (Section M.4) |
| nonuniform_advice_log2_bytes | 0 | uniform program; no stored search results |

Declared heuristics: **H1** (transfer of the random-function bound to the fixed target, score-critical),
**H-machine** (the declared 1,024-register file and uncharged instruction fetch, score-critical; Section L.6) and
**H-kernel** (kernel correctness on all inputs, score-critical for the success probability).

Sections are numbered 1 to 3 and 8 to 11 with the lettered sections M (machine program), L (ledger), P (probability)
and H (fixed-target premise) between them, as in the predecessor; every cross-reference names its section.

## 1. Target, message encoding and the walk

### 1.1 The target and the two messages

The target is SHA-256 (FIPS 180-4) with the standard IV, message schedule and constants at their original indices,
standard padding, the standard feed-forward and all 256 output bits, executing compression steps 0 through 45
on every padded block, per the organizer profile `sha256-r46-prefix-v1`. The target is SHA-256 reduced to its first 46 steps; everything else (IV, schedule, constants at their original indices, padding, feed-forward, all 256 output bits) is standard.

A point is a 256-bit integer `u`. Its message is the 52-byte string `M(u) = P || BE256(u)`, where `P` is the fixed
20-byte prefix of five big-endian words and the 32 bytes carrying `u` are the eight 32-bit words
`u_j = (u >> 32j) mod 2^32` for `j = 0..7`, each big-endian, in that order (`u_0` is `W5`, `u_7` is `W12`).
`M(u)` has 416 bits, so padding gives exactly one block with `W0..W4 = P`, `W(5+j) = u_j`, `W13 = 0x80000000`,
`W14 = 0`, `W15 = 416`. The map `u -> M(u)` is injective and every `M(u)` lies in the message domain, so distinct
points give distinct messages.

The prefix `P = (0x03F777B3, 0xEEC88896, 0xE8EBDB1C, 0x1B70C247, 0x177C95E3)` is the predecessor's: the unique
words that make the working state after step 4 have `a = b = d = e = f = 0` (Section M.4). It only lets the early
steps fold into constants and has no effect on the relation or the probability argument.

### 1.2 The walk, the map B and Lemma 0

Write `a_t, e_t` for the words formed at step `t` (so after step `t` the working state is
`(a_t, a_(t-1), a_(t-2), a_(t-3), e_t, e_(t-1), e_(t-2), e_(t-3))`), `T1_t = e_(t-4) + Sigma1(e_(t-1)) +
Ch(e_(t-1), e_(t-2), e_(t-3)) + K_t + W_t` and `T2_t = Sigma0(a_(t-1)) + Maj(a_(t-1), a_(t-2), a_(t-3))`, so
`a_t = T1_t + T2_t` and `e_t = a_(t-4) + T1_t` (all modulo `2^32`). Let `S(u)` be the working state after step
`45` and write `r = 46`. The eight output words of the walk are

| word | value | role |
| --- | --- | --- |
| 0 | `e_(r-4)` | the state word `h` (digest word 7 minus `IV_7`) |
| 1 | `e_(r-3)` | the state word `g` |
| 2 | `a_(r-8)` | |
| 3 | `a_(r-7)` | |
| 4 | `Q = T1_(r-6) + Maj(a_(r-7), a_(r-8), a_(r-9))` | `a_(r-6) - Sigma0(a_(r-7))` |
| 5 | `T1_(r-5)` | |
| 6 | `X = e_(r-6) + Ch(e_(r-3), e_(r-4), e_(r-5)) + W_(r-2)` | `e_(r-2) - a_(r-6) - Sigma1(e_(r-3)) - K_(r-2)` |
| 7 | `Y = e_(r-5) + W_(r-1)` | `T1_(r-1) - Sigma1(e_(r-2)) - Ch(e_(r-2), e_(r-3), e_(r-4)) - K_(r-1)` |

and the walk is `f(u) = B(S(u)) XOR PD` with `PD` the fixed output polarity of the kernel planes (asserted by the
experiment; `PD = 0x6da08bd78df41863588bbf63d5ffe11f6012d5bb35418f14e9665eb86b6ab500`), word `j` at bits `32j..32j+31`.

**The map B.** `B` sends the working state `S = (A, B', C', D', E, F', G, H)` after step `r-1` to the table above
using only `S` and the constants `K_(r-2)`, `K_(r-1)`:
`T1_(r-1) = A - T2(B', C', D')`, `a_(r-5) = E - T1_(r-1)`, `T1_(r-2) = B' - T2(C', D', a_(r-5))`,
`a_(r-6) = F' - T1_(r-2)`, `T1_(r-3) = C' - T2(D', a_(r-5), a_(r-6))`, `a_(r-7) = G - T1_(r-3)`,
`T1_(r-4) = D' - T2(a_(r-5), a_(r-6), a_(r-7))`, `a_(r-8) = H - T1_(r-4)`,
`T1_(r-5) = a_(r-5) - T2(a_(r-6), a_(r-7), a_(r-8))`, `Q = a_(r-6) - Sigma0(a_(r-7))`, and `X`, `Y` as in the right
column (here `T2(x, y, z) = Sigma0(x) + Maj(x, y, z)`). Its inverse is explicit: from the outputs,
`a_(r-6) = Q + Sigma0(a_(r-7))`, `a_(r-5) = T1_(r-5) + T2(a_(r-6), a_(r-7), a_(r-8))`,
`D' = (H - a_(r-8)) + T2(a_(r-5), a_(r-6), a_(r-7))`, `C' = (G - a_(r-7)) + T2(D', a_(r-5), a_(r-6))`,
`F' = X + K_(r-2) + Sigma1(G) + a_(r-6)`, `B' = (F' - a_(r-6)) + T2(C', D', a_(r-5))`,
`T1_(r-1) = Y + K_(r-1) + Sigma1(F') + Ch(F', G, H)`, `A = T1_(r-1) + T2(B', C', D')`, `E = a_(r-5) + T1_(r-1)`.
So `B` is a bijection of 256-bit states. Both directions are `tail_map` and `tail_inverse` in
`experiments/sha256_machine.py`; the experiment checks `tail_inverse(tail_map(S)) = S` and that `tail_map(S(u))`
equals the words read off the step loop (`tail_words`) on 74 inputs.

**Lemma 0.** For all `u, v`: `f(u) = f(v)` if and only if the complete digests of `M(u)` and `M(v)` are equal.

*Proof.* XOR with `PD` and `B` are bijections, so `f(u) = f(v)` iff `S(u) = S(v)`. The digest of a one-block
message is `IV_j + S(u)_j mod 2^32` for `j = 0..7`, serialized big-endian, and each `x -> IV_j + x` is a bijection on
32-bit words. QED

Why it is cheaper: the kernel only has to produce the eight words of the table. In the last steps it therefore never
forms `T2_t` or `a_t` for `t >= r-5`, never forms `e_(r-1)` or `e_(r-2)`, forms only `T1_(r-6) + Maj` at step `r-6`
(no `Sigma0(a_(r-7))`, one adder fewer), forms `X` with two adders instead of `T1_(r-2)` plus `e_(r-2)` (no `Sigma1`,
no `K`, three adders fewer) and forms `Y` with one adder instead of the four-adder `T1_(r-1)`, `Sigma1`, `Ch`, `T2` and
the two final adders. At this round count that removes 3,646 of the 63,750 gates of the
predecessor's kernel (Section M.1).

### 1.3 What was checked about the encoding

The declared experiment recomputes the working state of 74 inputs (zero, all-ones, eight single-word patterns and
64 seed-derived points) by the explicit step loop run for all 64 steps and by the canonical library
`hashlib.sha256` of the same message with the feed-forward undone word by word; agreement pins the message encoding,
word order, padding words and feed-forward against an implementation this package did not write. The reduced-round
reference is the same loop stopped after step `45`. On the same 74 inputs it checks `B`, its inverse, its
word program (Section 3.1) and the step-loop composition against each other. The organizer itself hashes both
messages of every returned pair with its own `46`-step SHA-256 and checks the declared event on digest word 7.
Relative to the predecessor the digest event of the experiments moves from the low bits of digest word 0 to the low
bits of digest word 7, because output word 0 of the walk is now the state word `h` rather than `a`.

## 2. The frozen algorithm

### 2.1 Parameters

| Symbol | Value | Meaning |
| --- | --- | --- |
| lanes | 256 | one bitsliced word holds one bit of 256 points |
| d | 112 | distinguished: bits `0..111` of `f(u)` are zero; density `theta = 2^-112`, `L = 1/theta = 2^112` |
| s1 | 32 | stage-1 planes: a batch is examined further only if some lane has bits `0..31` zero |
| k | 47 | endpoint key: bits `116..162` of `f(u)` |
| B | 1,328,585,296,930,600,160,597,248,231,755,218,944 (about `2^119.9993`) | batch horizon; `Q = 256B = 2^127.9993` lane evaluations |
| R | 51,922,968,585,348,276,285,304,963,292,200,960 = `10 L` | per-trail age cap |
| U | 71,316 | table capacity, never evicted |
| IDL | 131,072 | identifier limit; start `t` is `rho + t mod 2^256` |
| E2MAX | 237,569,564,032,065,897,094,711,345,152 = `3Q/2^32` | budget of stage-2 batches |
| rho | one uniform 256-bit word | the only randomness |

Derived deterministic ceilings, valid for every execution and every function: at most `Q` lane evaluations; at
most `floor(Q/R) = 6,550` cuts (each cut lane has used `R` evaluations since its own restart, disjoint
from other cuts); at most `U` insertions; at most `U + 1` endpoint handlers (every non-terminal handler
inserts); at most `256 + U + 6,550 = 78,122 < IDL` allocated identifiers, so the identifier
guard cannot fire before another stop.

Because `theta` is the exact power `2^-112`, the predicate is a plain test of 112 zero bits and no four-bit
window is needed; the window branch of the predecessor is retained in the program only as a parameter
(`win`), exercised by the fixtures, and is absent from the full-width program.

### 2.2 State

Lane `l` holds its current point (bit `j` in plane register `P_j`, lane bit `l`), its identifier `LID[l]` and
its birth batch `BIRTH[l]`. Global state: the batch counter `b`, the next identifier `NID`, the table count
`CNT`, the earliest-cut batch `NEXTCUT`, the stage-2 counter `H2`, `rho`, and the table: one array of 64-bit
slots, four per 256-bit word, where slot `e` holds the 47-bit key in its low 47 bits and the 17-bit start
identifier in bits 47..63.

### 2.3 Control flow

1. **Setup.** `rho = RAND`. Clear the table and metadata words. For `l = 0..255`, restart lane `l`
   (identifier `l`, birth 0). Set `b = 1`, `NEXTCUT = R`, `H2 = 0`.
2. **Batch b.** Evaluate `f` on all 256 lane inputs at once (the kernel). All 256 evaluations are charged even
   if a handler later stops in this batch.
3. **Stage 1.** `D = OR` of planes `0..31`: bit `l` of `D` is zero iff lane `l`'s low 32 bits are zero. If `D`
   is all-ones, skip to step 5.
4. **Stage 2.** `H2 = H2 + 1`; if `H2 > E2MAX` stop with failure (budget). `D = D OR` planes `32..111`: bit
   `l` of `D` is now zero iff lane `l` is distinguished. If `D` is all-ones, skip to step 5. Otherwise run the
   endpoint handlers in ascending lane order for each distinguished lane `l`: extract its 47-bit key; scan
   entries `0..CNT-1` for that key. On a match stop and run recovery (Section 2.4). Otherwise, if `CNT = U`,
   stop with failure (capacity). Otherwise write the key and `LID[l]` at entry `CNT`, increment `CNT` and
   restart lane `l` with birth `b`.
5. **Age cap.** If `b >= NEXTCUT`, scan lanes `0..255`: every lane with `b - BIRTH[l] >= R` is restarted with
   birth `b` (a cut). Distinguished lanes were restarted in step 4, so endpoint handling takes precedence over
   the cap. Then `NEXTCUT = min_l BIRTH[l] + R`. There is no global cut limit.
6. If `b = B` stop with failure (horizon); otherwise `b = b + 1` and go to 2.

Restart of lane `l`: if `NID = IDL` stop with failure (identifier guard; unreachable for these parameters).
Otherwise set `LID[l] = NID`, `BIRTH[l] = b`, write the point `rho + NID mod 2^256` into lane `l` of all 256
planes, and increment `NID`.

Stage 1 loses no distinguished lane (a distinguished point has its low 32 bits zero, and `32 <= d`), and
stage 2 computes exactly the predicate of Section 2.1, so the endpoint handlers see the same lanes a
single-stage test would; the split changes only the operation count and adds the budget stop. `NEXTCUT` never
exceeds `min BIRTH + R` because births only increase, so a lane reaching the cap always triggers the scan.

### 2.4 Recovery (at most once)

On a key match between stored entry `e` (identifier `s1`) and the current lane (identifier `s2`, length
`l2 = b - BIRTH <= R`, current endpoint `E` extracted from the planes):

1. **Reconstruct.** `x = rho + s1`; step `x = f(x)` until `x` is distinguished, counting `l1` steps; if `R`
   steps pass without an endpoint, stop with failure. If `x != E` stop with failure (a false short-key match).
2. **Align.** `a = rho + s1`, `c = rho + s2`; advance the start with the longer trail by `|l1 - l2|` steps. If
   `a = c` stop with failure (one start lies on the other trail).
3. **Paired walk** for at most `min(l1, l2)` steps: if `f(a) = f(c)` go to 4; otherwise `a, c = f(a), f(c)`.
4. **Final check.** Require `a != c` and recompute `f(a) = f(c)`, equivalently `S(a) = S(c)`. Output `M(a)`,
   `M(c)`. Any other outcome is failure.

Every scalar `f` evaluation in recovery is one target compression, the 185 word operations of the map `B` (Section 3.1) and one XOR. Reconstruction, alignment and
the paired walk use at most `l1 + |l1 - l2| + 2 min(l1, l2) <= 3R` compressions; the final check uses 2. The
recovery path returns a pair only after recomputing the collision, so a kernel error cannot produce a false
output; it could only cause a missed or spurious endpoint, which is why kernel correctness is declared as
H-kernel for the probability argument rather than for the validity of an output.

### 2.5 Termination codes

1 collision returned; 2 false short-key match; 3 start overlap; 4 table capacity; 5 identifier guard;
6 horizon; 8 recovery inconsistency (cannot occur for a true endpoint match, as Section P Step 3 establishes;
retained as an explicit guard);
9 stage-2 budget exhausted. Code 7 is unused: it belonged to a halt of the predecessor that this program does
not have, and the codes were not renumbered so that the fixtures and the reference keep their meanings.

## 3. Machine model (declared convention H-machine)

### 3.1 Word RAM with a declared register file

The cost model specifies a classical 256-bit word RAM, prices a 256-bit load or store separately from word
operations, counts working state and code in memory, and fixes no register count. As in the predecessor this entry
declares a load/store machine with a fixed file of `NREG = 1,024` registers of 256 bits, named statically by
instruction fields, never reached by a computed address, and counted in memory (32,768 bytes). Memory is every other
word, reached only by charged `LD` and `ST`. The program uses 957 of the 1,024 registers: 907 for the kernel (the
planes of `u` and `f(u)` in registers `0..255` and temporaries) and 50 control registers; `COMP` uses
16 further registers as scratch for the map `B` (Section 3.1 below), so 973 of the 1,024 are named
in all (asserted by the checks experiment).

| Instruction | Semantics | Charge |
| --- | --- | --- |
| XOR, AND, OR d,a,b; NOT, MOV d,a | bitwise on registers (MOV = OR a,a) | 1 |
| ADD, SUB d,a,b; ADDI d,a,imm | modulo `2^256` | 1 |
| SHL, SHR d,a,b; SHLI, SHRI d,a,imm | shift by register or immediate | 1 |
| LDI d,imm | load a 256-bit constant | 1 |
| LD d,a; ST a,s | load or store a memory word at the address in register a | 1 |
| BEQ, BNE, BLT, BGE a,b,target | unsigned comparison and conditional branch | 2 |
| JMP target | unconditional branch | 1 |
| RAND d | independent uniform 256-bit word | 1 |
| COMP d,a | `B(S(a))`: the 46-step state of `M(a)` mapped by `B` | one compression unit + 249 |
| OUT a,b | store the two output points | 2 |
| HALT n | stop with code n | 1 |

`COMP` is one target compression of the single block of `M(a)`, charged 64 word operations of allowance for
preparing its input and output (as in the predecessor: 16 to split the point, 24 stores of the block words, 16 loads
of the IV and constants, 8 to recombine) **plus the 185 word operations of the map `B`**, executed as the
fixed straight-line program `tail_program()` on 256-bit words (3 `LDI`, 15 extractions, the `Sigma0`, `Maj`, `Sigma1`,
`Ch`, addition and subtraction steps of Section 1.2 with a 32-bit mask after every modular step, 14 operations to
repack, one move). The experiment executes that program on the packed state and asserts its result equals `B(S)`,
and the interpreter charges `64 + 185 = 249` per `COMP`. The program keeps every value in registers: at
most 16 words are live at once (the packed state, the temporaries and the result; counted by `tail_regs()` and
asserted), and they use 16 registers of the declared file that neither the kernel nor the control code names, so
`B` performs no load or store and its 185 operations are its whole charge (a straight-line program can
always be register-allocated with exactly as many registers as its liveness peak, here 16). Its code, 1,576 bytes in the
image formats of Section 3.2 (3 `LDI` at 40 bytes and 182 other instructions at 8 bytes), is counted in memory
(Section L.4). The main loop does not invoke the
compression primitive; it evaluates 256 walk values per batch by explicit word operations, each charged `1/C`.
Instruction fetch is not a primitive operation of the cost model and is not charged (Section L.6).

### 3.2 Program image

The image format is the predecessor's: an 8-byte control format (opcode, three 10-bit register fields, a 24-bit
immediate or branch offset), a 4-byte kernel word (opcode, three 10-bit register fields) and a 40-byte constant
format; the kernel is a block of 60,104 4-byte words behind the 8-byte `KERNEL` instruction whose immediate holds
the block length. Every instruction of every class is charged its format's bytes, with no exception:

| Class | Count | Bytes each | Bytes |
| --- | ---: | ---: | ---: |
| `KERNEL` | 1 | 8 + 4 x 60,104 | 240,424 |
| `LDI` | 20 | 40 | 800 |
| `ADD` | 5 | 8 | 40 |
| `ADDI` | 19 | 8 | 152 |
| `AND` | 821 | 8 | 6,568 |
| `BEQ` | 15 | 8 | 120 |
| `BGE` | 3 | 8 | 24 |
| `BLT` | 2 | 8 | 16 |
| `BNE` | 9 | 8 | 72 |
| `COMP` | 7 | 8 | 56 |
| `HALT` | 8 | 8 | 64 |
| `JMP` | 12 | 8 | 96 |
| `LD` | 6 | 8 | 48 |
| `MOV` | 21 | 8 | 168 |
| `NOT` | 2 | 8 | 16 |
| `OR` | 672 | 8 | 5,376 |
| `OUT` | 1 | 8 | 8 |
| `RAND` | 1 | 8 | 8 |
| `SHL` | 258 | 8 | 2,064 |
| `SHLI` | 306 | 8 | 2,448 |
| `SHR` | 305 | 8 | 2,440 |
| `SHRI` | 259 | 8 | 2,072 |
| `ST` | 4 | 8 | 32 |
| `SUB` | 7 | 8 | 56 |
| `XOR` | 7 | 8 | 56 |
| **image** | | | **263,224** |

so the image is 263,224 bytes (SHA-256 `77299d66ed654b8c2332ac2c969b5dd15c42e1d350b63f3c70854a492b032ab4`). Every immediate (shift amounts, `ADDI` constants,
`HALT` codes, the `KERNEL` length) and every branch byte offset fits the 24-bit field, and every 256-bit constant uses
the 40-byte `LDI` format; `encode` asserts both. The checks experiment encodes the full-width program, decodes it,
asserts the round trip and that the length equals this sum, and the search experiment executes only the decoded
program.

## M. The machine program

The program is emitted by `build_program` in `experiments/sha256_machine.py` (unchanged from the predecessor).

### M.1 Kernel

The kernel computes the planes of `f(u)` from the planes of `u` in place in registers `0..255`. The
constant-folding Boolean DAG builder `Net` is the predecessor's, unchanged: modular additions are ripple-carry
full adders (at most five gates per bit, constants fold, bit-0 carry-ins absorbed, complement-free carries,
one-gate De Morgan carries for constant-one pivots), rotations and shifts are plane relabelings, `Ch` is a
three-gate multiplexer, `Maj` is `mux(b XOR c, a, b)` reusing `b_t XOR c_t = a_(t-1) XOR b_(t-1)`, and full adders
reassociate `h_t XOR g_t = f_(t-1) XOR g_(t-1)`. What changes is the word-level composition in `build_listing`:
steps `0..r-7` are FIPS 180-4 steps exactly as before; steps `r-6..r-1` form only the words of Section 1.2
(`TAIL = True`; with `TAIL = False` the same file builds the predecessor's untruncated kernel, 63,750 gates
at this round count, which is how the lever is measured).

The DAG has 60,104 gates (47,700 XOR, 4,882 AND, 7,522 OR, no NOT).
In-place register allocation (the predecessor's allocator, unchanged) needs 907 registers and 0 output moves, so a
batch runs 60,104 kernel instructions with no memory access. The experiment asserts the instruction count, the gate
split, the register count and `PD`.

Correctness argument (**H-kernel**). (1) Every gate-construction rule is checked exhaustively on all operand classes
by the declared experiment. (2) The word-level composition follows FIPS 180-4 for steps `0..r-7` and the table of
Section 1.2 for the tail, mirroring the scalar `tail_words`, which the experiment checks against `B(S)` computed from
the full reference state. (3) A static check proves that the allocated listing computes the gate DAG for every
input. (4) Sampled kernel lanes are compared with the scalar reference on all 256 output bits in every trial.
Step (2) is established by inspection and sampling, which is why H-kernel is declared.

### M.2 Main loop, stage 2 and the handlers

Per batch: `KERNEL` header 1 plus 60,104 kernel words, 31 ORs for stage 1, a comparison and branch (2) and six
control operations, in total 60,144 operations. The control code is the predecessor's, unchanged, so every
handler closed form is the predecessor's except those containing `COMP`: stage-2 entry 85 (86 on a stage-1 miss),
endpoint-batch lane scan 1,795, key extraction 189, table scan 13 per entry and insertion `20 + 13c`, restart
1,292 / 1,294 / 1,295, cut scan 2,564 plus at most 256 minimum updates and 3 per cut, recovery 1046 fixed,
**257 per reconstruction step, 254 per alignment step, 508 per non-final paired
step and 1008 for the final paired step and check** (each `COMP` now 249), output and halt 3, setup
405,422. Every closed form is measured at the full-width parameters under lane-wise test functions and asserted
by the declared experiment.

### M.3 Storage layout

Every byte the program or `COMP` can touch is in one of these regions (256-bit words are 32 bytes):

| Region | Bytes |
| --- | ---: |
| program image (Section 3.2 class sum) | 263,224 |
| B program code (Section 3.1) | 1,576 |
| register file, 1,024 x 32 | 32,768 |
| table slots ceil(U/4) = 17,829 words + BIRTH 256 + LID 256, 18,341 x 32 | 586,912 |
| COMP message schedule W0..W63, 64 x 32 | 2,048 |
| COMP round constants K0..K63, 64 x 32 | 2,048 |
| COMP IV, 8 x 32 | 256 |
| COMP working state a..h, 8 x 32 | 256 |
| COMP block assembly: 16 block words + 8 split words, 24 x 32 | 768 |
| output area: two points (2 words) and two 52-byte messages (2 words each), 6 x 32 | 192 |
| slack (unassigned reserve) | 4,096 |
| **total** | **894,144** |

`COMP` is itemised in full: the expanded message schedule, the round-constant table, the IV, the working state and
the block-assembly words (the 16 block words and the 8 words of the split point) each have their own region, sized
at one 256-bit word per 32-bit value although they would pack eight to a word; the map `B` runs in registers
(Section 3.1) and needs no memory. The slack line is an unassigned reserve that only enlarges the bound.

### M.4 The fixed program image is the algorithm

The algorithm is the fixed image of Section 3.2. It is a deterministic, uniform function of the public target
and parameters, contains no search results or other target-specific advice, and is counted in memory in full.
No program generation is performed during the charged computation: the attack begins with the image loaded, as
any algorithm begins with its code. The generator in the experiment source is provenance and reproducibility
tooling; the experiment regenerates the image and checks it, but its own time and workspace are not part of
the attack. Hence `preprocessing_log2 = 0` and `nonuniform_advice_log2_bytes = 0`. The parameter selection that
produced the literals of Section 2.1 is a search over accounting constants only, reported in Section P; it
reads only the public target and the memory ceiling, stores nothing, and changes no charged row.

The prefix `P` of Section 1.1 involves no search either. Requiring `a = b = d = e = f = 0` after step 4 forces
`Sigma0(c) = IV_0`, and `Sigma0` has full rank 32 over GF(2), so `c` is the unique preimage and each of the
five words follows by one subtraction. It is an `O(1)` inversion of five steps, not a search, and the program
would be correct with `P = 0`.

Two accounting positions are stated here rather than hidden. First, `preprocessing_log2 = 0` rests on the
argument above and is not declared as a heuristic; an adjudicator who holds that building the program image
must be charged should read Section L.6's convention discussion in the same spirit. Second, the reference cost
`C = 3,400` is the organizer's `reference_operation_cost` for this round count; it is also recoverable from the benchmark's own
cost model, whose word-operation weight is exactly `1/3,400`.

## L. Resource ledger

### L.1 Worst-case event counts

| Event | Bound | Reason |
| --- | --- | --- |
| batches | `B = 1,328,585,296,930,600,160,597,248,231,755,218,944` | horizon |
| stage-2 entries | `E2MAX + 1` | budget halt |
| endpoint batches, handlers | `U + 1 = 71,317` | each endpoint batch contains at least one handler |
| insertions, endpoint restarts | `U = 71,316` | capacity |
| cuts | `floor(Q/R) = 6,550` | disjoint `R`-evaluation blocks |
| cut scans | `6,550 + U = 77,866` | |
| recovery | 1 | terminal |

### L.2 Word-operation terms (exact integers)

| Term | Operations |
| --- | ---: |
| setup | 405,422 |
| main batches: B x (kernel + 40) | 79,906,434,098,594,016,058,960,897,650,685,888,167,936 |
| stage-2 batches: E2MAX x 86 + 3 | 20,430,982,506,757,667,150,145,175,683,075 |
| endpoint-batch lane scans: (U+1) x 1795 | 128,014,015 |
| key extraction: (U+1) x 189 | 13,478,913 |
| table scans and insertions | 33,059,779,830 |
| terminal handler: 13U + 5 | 927,113 |
| endpoint restarts: U x 1294 | 92,282,904 |
| age-cap scans: (cuts + U) x 2820 | 219,582,120 |
| cuts: floor(Q/R) x 1298 | 8,501,900 |
| recovery: 1046 + found + (rec_step + pair_step) R - pair_step | 39,721,070,967,791,431,358,258,296,918,533,735,946 |
| output and halt | 3 |
| **W (sum)** | **79,946,155,189,992,789,997,076,823,097,783,120,559,177** |

The recovery row is `rec_fixed + found + (rec_step + pair_step) R - pair_step` with the closed forms of M.2, the
maximum of `rec_step l1 + align_step |l1 - l2| + pair_step (min(l1, l2) - 1)` at `l1 = l2 = R`. Compressions:
`H <= 3R + 2 = 155,768,905,756,044,828,855,914,889,876,602,882`.

### L.3 Total time

    T = H + W/C,   C = 3,400
    log2 T = 124.154359230576        claim time_log2 = 124.15436

`C = 3,400` is the round-46 `reference_operation_cost` printed by the organizer's
`pareto_candidate.py --family sha256 --rounds 46 --show-contract`. The main loop is 99.293 percent
of `T`; the main batches alone are `log2 = 124.144116438692`. The bound holds for every function and every `rho`,
including failed attempts; there is one attempt and no amplification.

### L.4 Memory

    M = 263,224
      + 1,576
      + 32,768
      + 586,912
      + 2,048
      + 2,048
      + 256
      + 256
      + 768
      + 192
      + 4,096
      = 894,144 bytes,  log2 M = 19.770147667541,  claim memory_log2_bytes = 19.77015

The terms are the regions of Section M.3 in order. The claim is the least five-decimal value whose power of two is at
least `M`, checked exactly (`M^100000 <= 2^1977015`); `2^19.77015` exceeds `M` by
1.4 bytes, on top of the 4,096-byte slack line. Memory is below `2^20` bytes by
154,432 bytes, so it adds nothing to the normalized score.

**Bound audit.** Each declared bound is recomputed from the shipped files and is not below its true value:
`time_log2 = 124.15436` >= `log2 T = 124.154359230576` (Section L.3, every row an exact integer from closed forms that the
checks experiment asserts against the executing program); `memory_log2_bytes = 19.77015` >= `log2 894,144`
(above); `success_probability = 0.39` <= the certified 0.390036155778183 under H1 (Section P, recomputed by the
bound experiment); `preprocessing_log2 = 0` because the program image is the algorithm and is counted in memory and
nothing is computed before the run (Section M.4); `nonuniform_advice_log2_bytes = 0` because the image contains only
public constants and code.

### L.5 What is asserted by execution, and by whom

The declared experiments run only in the organizer's isolated executor. Asserted there: the kernel size, gate split,
register count and the static proof of the listing; the 74 encoding checks and the checks of `B`; the length and
result of the `B` program; the image round trip and size; every per-handler closed form at full width; and
outcome-level equivalence of the program and the scalar reference at reduced width. Established mathematically: the
event bounds of L.1 and the arithmetic of L.2 to L.4, recomputed by Appendix A (time and memory) from the printed integers.
Established by the bound-checker experiment: Section P. Assumed: H-machine, H-kernel and H1.

### L.6 Sensitivity

| change to the declared convention | result |
| --- | ---: |
| instruction fetch charged at one 256-bit load per 32 bytes of kernel code (`ceil(60,104 x 4 / 32) = 7,513` operations per batch) | 124.32305 |
| `COMP` charged 64 as in the predecessor (that is, `B` free) | 124.15385 |

The fetch convention is the predecessor's and its comparators'; an adjudicator who rejects it should reject it for
every entry at this target. Charging the map `B` with every recovery compression costs
0.00051 bits, because recovery is about 0.71 percent of the ledger.

## P. Success probability in the random-function model

**Model.** `F` is a uniformly random function on 256-bit strings and `rho` is uniform and independent of `F`
(the bound in fact holds for every fixed `rho`). The bound below is a theorem in this model; its application
to the fixed SHA-256 target is the heuristic H1 of Section H. It assumes that the main-loop kernel computes
`F` exactly (H-kernel).

The argument below is the integrated detection-delay bound. Its shape follows the public proof of submission
`76ab339a` (Jbenisek, Lemma 2) and TheTradoor's entry `09fe5fcd` (C4, Section P), carried unchanged into `55783d22` and `3642e1cd`; all are credited in Section 10; it
is restated here in full, with every term derived, because a reviewer cannot fetch either document. The two
ideas it rests on are a lottery coupling, which draws the coins deciding whether a value is distinguished
before and independently of the values within their class, and the observation that the first plain collision
may occur at any slot of the run, so the detection delay must be integrated against the distribution of that
slot rather than reserved as a fixed allowance.

**Notation.** The run evaluates `Q = 256B` slots, numbered `t = 1, ..., Q` batch by batch and lane by lane
within a batch; `b(t) = ceil(t/256)` is the batch of slot `t`. `N = 2^256`; the distinguished class has
exactly `theta N = 2^144` values and the plain class `N' = N - 2^144`; `L = 1/theta = 2^112`;
`q = Q theta`; `PP = Q(Q-1)/(2N')`; `p = e^(-R theta)`; `p2 = e^(-(R-2) theta)(1 + (R-1) theta)`;
`Pi_m = prod_(i<m) (1 - i/N')`. A trail is one lane's run of evaluations between two restarts, and its age
`a(t)` at slot `t` is the number of its earlier evaluations. A trail finishes when an evaluation returns a
distinguished value (its endpoint, handled in that batch), is cut when its age reaches `R` at the end of a
batch without an endpoint, and is open when the run halts first. An evaluation is fresh when its input has
not been evaluated before; a collision is a fresh evaluation whose value equals an earlier value or a start.

**Step 1 (lazy sampling with a lottery).** Realize `F` lazily: draw independent coins `xi_t ~ Bernoulli(theta)`,
one per slot, and independent values `V_t`, uniform on the distinguished class when `xi_t = 1` and on the plain
class otherwise; the `t`-th evaluation returns `V_t` if its input is fresh and the stored value of that input
otherwise. This is a correct lazy sampling of a uniformly random function for every adaptive choice of inputs.
Four facts are used. (L1) Given the whole lottery and the history before `t`, a fresh plain slot has
`P(V_t = v) = 1/N'` for every plain `v`. (L2) Whether slot `t` is fresh, and its input, batch, age and trail
boundaries, are determined by the history before `t`. (L3) The coins of one lane are independent and
identically distributed, different lanes are independent, and reading coin positions in stopping-time order
yields an i.i.d. sequence. (L4) `N1`, the total number of coins equal to one, is exactly `Binomial(Q, theta)`
with mean `q = 65504.3`; the Chernoff form `e^-q (e q / k)^k` is at most `2^-40` at `k = 67,420`, and
`k` is the least value for which that **Chernoff bound** holds. (The true binomial tail reaches `2^-40` at a
smaller `k`; using the larger `k` is conservative in every term it enters, namely `shift`, the false-key term
and the distinguished-class term, so the bound below is valid as stated.) (L5) The run up to a stopping time
is determined by the values and coins up to it, and later coins are independent of that past.

Two global events are excluded and charged. `E1`: some value of the run equals a start `rho + s` with
`s < IDL`. Each fresh value is uniform on all `N` values before its coin is conditioned on and there are
`IDL` starts, so `P(E1) <= Q IDL / N`. `E2`: some fresh distinguished value equals an earlier distinguished
value; on `N1 <= k - 1` each fresh distinguished value is uniform on `theta N` values with at most `k - 1`
earlier ones, so `P(E2) <= k^2 L / N`. Outside `E1` and `E2`, a non-fresh evaluation exists only after a
plain collision.

**Step 2 (the free run and the first plain collision).** Given the coins, the free run, in which every
evaluation is fresh, has trail boundaries, ages, endpoints and cuts that are functions of the coins alone: a
trail finishes at its lane's next coin equal to one and is cut when `R` consecutive zero coins follow its
start. The lottery is extended beyond the run by further independent coins, used only in the analysis. For a
slot `y` let `sigma(y)` be the number of slots on `y`'s lane after `y` up to and including the first with coin
one, and `g(t)` the number of consecutive zero coins on `t`'s lane immediately before `t`; in the free run
`a(t) <= g(t)`. Let `tau` be the first plain slot whose value equals the value of an earlier plain slot.
Outside `E1` and `E2` the real run coincides with the free run up to `tau`. Writing `n0(t)` for the number of
plain slots up to `t`, (L1) and (L2) give, for every plain `y < t`,

    P(tau = t, V_t = V_y | coins) = Pi_(n0(t)-1) / N',     P(tau <= Q | coins) = 1 - Pi_(n0(Q)).

On `N1 <= k - 1` we have `n0(t) - 1 >= t - k`, and `Pi_(t-k) <= shift x Pi_(t-1)` with
`shift = 1/(1 - kQ/N')`, because `Pi_(t-1)` is `Pi_(t-k)` times at most `k - 1` factors each at least
`1 - Q/N'`. Hence `P(tau <= Q, N1 <= k - 1) >= 1 - shift x Pi_Q - 2^-40`, which is the first and the
third-to-last rows of the table. The checker encloses `Pi_m` between
`exp(-m(m-1)/(2N') - (m-1)m(2m-1)/(6N'^2))` and `exp(-m(m-1)/(2N'))`.

**Step 3 (a good undisturbed first collision is output).** Let `tau = t` with partner `y`, let `X` be the
trail of `t` and `Y` the trail of `y`. Call the pair good when (G1) `y` is not on `X`; (G2) `b(y) < b(t)`;
(G3) `Y` is not long, so it finishes at its endpoint after at most `R - 1` earlier evaluations and is never
cut; and (G4) `b(t) + sigma(y) <= B` and `a(t) + sigma(y) <= R - 1`. Call it undisturbed when no fresh
evaluation of `Y` after slot `t`, up to and including its endpoint, is itself a collision.

On a good undisturbed pair, outside `E1`, `E2` and the halts of Step 5, the program outputs a pair. The input
of `X` after `t` is `V_t = V_y`, the input of `Y` after `y`, so `X`'s evaluations after `t` repeat `Y`'s after
`y`. `Y` is never cut by (G3) and its evaluations after `t` are fresh non-collisions, so its coins decide: its
endpoint is its `sigma(y)`-th evaluation after `y`, in batch `b(y) + sigma(y) < b(t) + sigma(y) <= B` by (G2)
and (G4), inside the run, and the endpoint handler stores `Y`'s key and restarts it. `X` repeats the same
points and reaches the same endpoint in batch `b(t) + sigma(y) <= B`; before that evaluation `X` has made
`a(t) + sigma(y) <= R - 1` evaluations, so no cut scan removed it. `X`'s handler finds the stored key and runs
recovery on two different trails, by (G1), that end at the same endpoint from different starts, and whose
colliding inputs differ because `t` is fresh. Section 2.4 then outputs a pair: reconstruction takes at most
`R` steps, the aligned starts differ outside `E1`, and the paired walk meets at the first pair of distinct
inputs with equal values, which exists because the two paths merge at `V_t = V_y` and nowhere earlier.

**Step 4 (the failure terms).** Work on `N1 <= k - 1`, outside `E1` and `E2`. By Step 2,
`P(tau = t, V_t = V_y | coins) <= 1/N'` for every pair, and on `N1 <= k - 1` also
`<= shift x Pi_(t-1)/N'`. Each failure is bounded by the expected number of pairs of its kind times that
hazard.

- *(G1) fails (own trail).* Then `y` is one of `X`'s `a(t)` earlier evaluations. Averaged over the slots of
  the run, the age of a trail of length `min(Geom(theta), R)` has mean `E[len(len-1)]/(2 E[len])`, which for
  `R = 10L` equals `L (1 - 11 e^-10)/(1 - e^-10) = 0.999546 L`, at most `L`. So the expected number of
  same-trail pairs is at most `Q L` and the loss is at most `Q L / N'`. The slot average, not the maximum
  age `R`, is the right quantity here, because the bound counts pairs over the slots of the run; a reader who
  substituted the age cap `R` would get a figure ten times larger, which exceeds the margin and would defeat
  the claim, so the renewal computation is stated rather than assumed. The finite horizon only strengthens it:
  a lane starts at age zero and its last trail is truncated, so the realized slot average over the run's `Q`
  slots is below the stationary one.
- *(G2) fails (same batch).* Then `y` lies in `t`'s batch before `t`, at most 255 choices per `t`, giving
  `255 Q / N'`.
- *(G3) fails (long earlier trail).* A long trail has at most `R` evaluations. Scan each lane in trials of `R`
  coins from the current position, a trial succeeding when all `R` coins are zero; the long trails of a lane
  are at most the successes, the failures are at most `N1 + 256` with expectation at most `q + 256`, and the
  trials are independent with success probability `(1 - theta)^R <= p`. By Wald's identity the expected
  number of long trails is at most `p (q + 256)/(1 - p)`, each contributing at most `R` points, each pairing
  with at most `Q` slots at hazard `1/N'`. The loss is at most `R Q p (q + 256)/((1 - p) N')`.
- *(G4) fails, first part (detection delay).* `b(t) + sigma(y) > B` requires the `B - b(t)` coins after `y` on
  `y`'s lane to be zero, which has probability at most `e^(-theta (B - b(t)))` and is independent of the
  values. Summing `1/N'` over `y < t` gives `(t-1)/N'`, and `(t-1) Pi_(t-1)/N' = Pi_(t-1) - Pi_t`, so the loss
  telescopes into `shift` times a sum of `(Pi_a - Pi_b) e^(-theta (B - ceil(b/256)))` over a partition of
  `[0, Q]` into bins `(a, b]`. **The bin schedule is part of the bound and is stated here:** the interval is
  split at `split = max(1, Q - 150 x 256 x (L + 1))`, with 2000 equal bins below `split` and 20000 equal
  bins above it, 22000 in all; the exponential is evaluated at each bin's **upper** endpoint `b`, which
  is where `B - b(t)` is smallest and the factor therefore largest, so the bin value dominates every slot in
  the bin. (The upper endpoint is the binding one because the residual delay is counted from the later of the
  two slots, which is the second occurrence of the first collision; the earlier trail's endpoint lies before
  it.) The checker uses the upper enclosure of `Pi_a` and the lower enclosure of `Pi_b`, so each bin's
  contribution is an upper bound.
- *(G4) fails, second part (later-trail age).* `a(t) + sigma(y) >= R` requires `g(t) + sigma(y) >= R`. On
  different lanes `g(t)` and `sigma(y) - 1` are dominated by independent geometric variables, and their sum
  reaches `R - 1` only if one i.i.d. coin sequence has at most one coin equal to one among `R - 1` coins,
  which has probability at most `(1 - theta)^(R-1) + (R-1) theta (1 - theta)^(R-2)`. Both powers are at most
  `e^(-(R-2) theta)`, so this is at most `p2 = e^(-(R-2) theta)(1 + (R-1) theta)`, which is what the checker
  evaluates. Writing `e^(-(R-1) theta)` instead would not dominate `(1 - theta)^(R-2)` and so would not be a
  valid enclosure, by a relative `1.8 x 10^-34`. On the same lane,
  with (G1) and (G3), `y` lies on an earlier short trail of that lane and the two counts are determined by
  disjoint coin sets dominated by the same pair of geometrics. With at most `Q(Q-1)/2` pairs at hazard
  `1/N'`, the loss is at most `PP p2`.
- *(e) Disturbance.* For a good pair, the fresh evaluations of `Y` after slot `t` up to its endpoint number at
  most the count of `y`'s lane coins after `t` up to and including the next one, which is dominated by a
  geometric of mean `L` and is independent of the past at the stopping time `t` by (L5). Each plain one is a
  collision with conditional probability at most `(Q + IDL)/N'`; the final distinguished evaluation is
  covered by `E2`. The events `(tau = t, V_t = V_y)` are disjoint with total probability at most `PP`, so the
  loss is at most `PP L (Q + IDL)/N'`.

**Step 5 (halts before the pair is output).** Outside `E1` and `E2`, every distinguished evaluation is either
fresh, and so counted in `N1`, or a repeat of a stored endpoint, which is a true key match that ends the run.
Insertions are therefore at most `N1 <= k - 1 < U = 71,316`, so the capacity halt (code 4) cannot occur. A
false short-key halt (code 2) needs a fresh distinguished value whose 47-bit key equals a stored key, at most
`k U / 2^47`. The identifier guard (code 5) is unreachable because 78,122 identifiers are
allocated at most and `IDL = 131,072`. The horizon halt (code 6) does not occur on a good pair by Step 3.
For the stage-2 budget (code 9), a batch is counted when some lane's low 32 bits are zero. Fresh
evaluations with that property are dominated by a binomial with mean `mu = Q 2^-32 = 2^95.9993`, and the
multiplicative Chernoff bound gives `P(count >= 3 mu) <= exp(-mu (3 ln 3 - 2))`, whose exponent is
`2^96.3732`, so the probability is below `2^-90` by more than thirty orders of magnitude. Non-fresh
evaluations occur only on trails that have already collided; each repeats at most `R` points of an earlier
path whose values were fresh outputs with hit hazard at most `2^-32`, and the number of such trails is itself
bounded by the plain-collision count, so their contribution is dominated by the same tail. The count therefore
stays below `E2MAX = 3Q/2^32` except with probability far below `2^-90`.

The outward rounding of the checker's enclosures is bounded separately and by the same figure: each of the
22000 bins contributes at most the absolute slack `10^-58` of the rounding helpers, and their relative
slack is `10^-40` on quantities below one, so the total rounding slack is below `10^-42`. The single
`stage-2 budget and rounding` row charges `2^-90` and covers both, each of which is individually far smaller.

**Step 6 (the bound).** The attempt succeeds unless no plain collision occurs by `Q`, or `N1 >= k`, or the
first plain collision is not good or is disturbed, or `E1`, `E2` or a halt of Step 5 occurs. Therefore

    P_F >= 1 - sum of the losses below.

| Term | Bound | Upper value |
| --- | --- | ---: |
| no plain collision | `shift x Pi_Q` | 0.606823925074904 |
| detection delay | `shift x sum over bins (Pi_a - Pi_b) e^(-theta (B - ceil(b/256)))` | 0.002378073789528 |
| own trail | `Q L / N'` | 0.000015251411242 |
| long earlier trail | `R Q p (q + 256) / ((1 - p) N'), p = e^(-R theta)` | 0.000455353625049 |
| later-trail age | `PP p2` | 0.000249458206112 |
| disturbed suffix | `PP L (Q + IDL) / N'` | 0.000007618333150 |
| same-batch pair | `255 Q / N'` | 7.490e-37 |
| start hit | `Q IDL / N` | 3.850e-34 |
| distinguished-class duplicate | `k^2 L / N` | 2.038e-34 |
| count tail N1 >= k | `2^-40` | 9.095e-13 |
| false 47-bit key | `k U / 2^47` | 0.000034163780925 |
| stage-2 budget and rounding | `2^-90` | 8.078e-28 |
| **sum of losses** | | **0.609963844221817** |

The certified lower bound is `P_F >= 0.390036155778183` (rounded down), a margin of 0.000036155778 above 0.39. Two
deliberate conservatisms sit inside that figure and are disclosed rather than spent: the detection-delay sum
evaluates each bin at its upper endpoint, which overstates that term by roughly 0.4 percent of itself, about a
quarter of the stated margin; and the distinguished-class and false-key index sets are each counted about
twice over. A finer bin schedule would raise the certified bound, and the upper endpoint is kept because it is
what makes the discretization an upper bound at any resolution. `B` is a
multiple of `2^100` at which the exact checker certifies with that margin; it is **not** the least such
multiple. An exact bisection over the multiplier shows that multiples down to about `1048007 x 2^100` also
certify; taking one would lower the time bound by about 0.00009 bits and leave a margin near `4 x 10^-7`. That
trade is not taken, and the margin is deliberately left at 0.000036155778. The declared experiment `sha256-r46-success-bound-v1` recomputes all of
these values from the frozen literals in 60-digit decimal arithmetic, with every exponential rounded in the
direction that weakens the bound and exact rationals elsewhere, so the arithmetic is checked by the organizer
rather than only by us; an administrative tool outside this package reproduces the identical
values from a separate copy of the same formulas, which guards against transcription error but not against an
error in a formula; the formulas are therefore derived above rather than cited. The
parameters were chosen by a float exploration of this bound over the density, the age cap, the key width and
the table size under the `2^20`-byte memory ceiling: the density `2^-112` is the largest power of two whose
certified count `k` fits the largest table the memory budget allows, `R = 10 L` balances the long-trail and
age losses against the recovery cost, and the key width of 47 bits is the widest the 64-bit slot admits beside
the 17-bit identifier. (Throughout this section `k` denotes the count tail 67,420 of the paragraph above; the
key width is always written as a number of bits.)

### P.1 Review against the implemented program

The authors of the predecessor re-checked the argument item by item against the decoded machine program, and we
repeated that check against this entry's program, whose control code is unchanged and whose only difference on
these items is the evaluated function. This is a self-report, not an organizer-executed result. The items were: the
serialization of a batch before any handler and of handlers in ascending lane order; freshness of a
continuing lane's input and of a restarted lane's start; exactness of the age cap (`NEXTCUT` never exceeds
`min BIRTH + R`); uniqueness of table keys and the absence of eviction; recovery of any true match; and the
identity of the counted quantities with the program's values (`Q = 256B`, 78,122 identifiers
below `IDL = 131,072`, `U = 71,316 > k = 67,420`, 47 key bits disjoint from the 112 bits the predicate
reads, and `R` and `E2MAX` as declared). The reduced-width fixtures and the full-width probes of the declared
experiment check the control flow and the handler costs that these items assume. A valid random-function
bound does not imply a bound for every function, which is why the transfer is declared as H1.

## H. The fixed-target heuristic H1 and its evidence

**Statement.** For the fixed walk `f(u) = B(S(u)) XOR PD` at SHA-256 reduced to its first 46 of 64 steps (standard IV, schedule, constants, padding and feed-forward after step 45), the success probability of this
algorithm over its uniform offset `rho` is at least the random-function bound of Section P, hence at least 0.39.

**What is assumed.** Section P is a theorem over a random function `F`, for every fixed `rho`. H1 exchanges the
quantifiers: for the one fixed `f`, the average over `rho` is at least 0.39. Nothing here proves that exchange. All
starts are `rho + i` for consecutive `i`, so as messages they differ only in `W5` of a single block, and H1 is asked
to hold for that structured start set. `B` does not change the question: it is a fixed public permutation applied
after `S`, and composing a function with a fixed permutation of its outputs maps collisions to collisions and fresh
uniform answers to fresh uniform answers.

**Why the random-function model is the relevant model.** The algorithm is generic and uses no property of SHA-256
beyond evaluating it; the proof uses only that answers to fresh queries are uniform and independent of the history.
At 46 steps no public property of reduced SHA-256 is known that would bias a generic walk of this kind on single-block messages; the strongest collision attacks we know of on step-reduced SHA-256, including the cryptanalytic 39-step entry on this board, stop at 39 steps and give no generic-search deficit at this round count.
The margin above 0.39 is 0.000036155778, so any fixed-target deficit larger than that would defeat the claim. The
support for H1 is the genericity of the algorithm, the absence of any known property of the target that would bias such
a walk, and the organizer-executed slice experiments below, which exercise the first-duplicate mechanism on the fixed
walk; none of them can bound a deficit as small as the margin.

**Diagnostic experiments.** For each organizer trial a separate slice `g(u) = f(c | u) mod 2^n` is taken (`c`
seed-derived, low `n` bits cleared); 256 lane walks start at consecutive slice values, evaluated by the same kernel
and serialized as in the search. The model probability of a returned pair is exact under the random-function model.
The organizer verifies every returned pair on the low `n` bits of digest word 7.

| Experiment | n | slots | model P(pair) | model expectation of 256 | observed (organizer executor, public seed) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `sha256-r46-slice-first-collision-w20-v1` | 20 | 1,280 | 0.448648 | 114.85 | 135 of 256 |
| `sha256-r46-slice-first-collision-w22-v1` | 22 | 1,536 | 0.230668 | 59.05 | 61 of 256 |
| `sha256-r46-slice-first-collision-w22-rep1-v1` | 22 | 1,536 | 0.230668 | 59.05 | 59 of 256 |
| `sha256-r46-slice-first-collision-w22-rep2-v1` | 22 | 1,536 | 0.230668 | 59.05 | 59 of 256 |
| `sha256-r46-slice-first-collision-w22-rep3-v1` | 22 | 1,536 | 0.230668 | 59.05 | 65 of 256 |
| all four width-22 runs | 22 | 1,536 | 0.230668 | 236.20 of 1,024 | 244 of 1,024 |

The observed column is our run of the organizer's executor (`experiments/runner.py`, pinned image, public seed
`hashsmash-public-seed-v1`, no holdout) in a Linux checkout of the challenge repository, so the trial seeds are the
ones the official evaluation derives from the track's target-configuration hash; the official evaluation runs it again.

The three replicates differ from the primary width-22 experiment only in the experiment id, so the organizer gives
each 256 fresh seeds. They were declared in every package of the round-40 to round-60 rebuild, under one rule and before any organizer-seeded executor run of this package or any computation of a replicate count. The rule
was set after the primary width-22 run of our round-61 package returned 81 of 256 (+3.26 standard deviations). The
diagnosis that found that result had already computed this round's primary slice counts with the organizer's seeds,
outside the executor, so those counts were known when the rule was set; no replicate count was, and the rule is the
same for every round whatever its primary counts.

Width 20 returned 135 of 256 against 114.85 expected (+2.53 standard deviations). The primary width-22 run returned
61 of 256 against 59.05 (+0.29); the replicates returned 59, 59 and 65 (183 of 768 against 177.15, +0.50), and all
four width-22 runs together return 244 of 1,024 against 236.20 expected (0.2383 per trial, +0.58 standard deviations).
The width-20 count is an excess of returned pairs of 2.53 standard deviations (one-sided binomial tail 0.0069).
The width-20 experiment has no replicate; its count is reported as observed, and an excess of returned pairs is
the direction that does not weaken the success bound.
Taken together they show no persistent departure from random-function behaviour in this mechanism at widths 20
and 22.

**These are diagnostic, not a calibrated confirmation of H1**: the seeds are public and fixed, we chose the widths,
slot counts and experiments, the replicate rule was set after a result at another round was seen, and no coverage,
confidence statement or false-alarm rate is claimed. Every declared run is reported. They cannot detect a deficit of
0.000036, and they do not reach the full-width distinguished-point and key events.

## 8. Declared experiments

1. `sha256-r46-machine-checks-v1` (no pairs) regenerates the kernel and asserts its instruction count, gate split, register count and
   `PD`, and that the kernel, control and `B` scratch registers fit the declared file; checks the explicit reference
   against `hashlib.sha256` on 74 inputs and `B`, its inverse, its word program, the packed `walk_table` and the
   step-loop composition on the same inputs; proves statically that the allocated listing computes the gate DAG;
   checks all gate-rule cases exhaustively; encodes, decodes and asserts the round trip and the image size of
   Section 3.2; runs sixteen control-flow fixtures; and measures every handler cost at full width and asserts the
   closed forms of Section M.2 (with `COMP` at 249). It reports these figures in its first rows (256 of 256
   rows in our run, every assert passed).
2. `sha256-r46-bounded-machine-w16-v1` regenerates and asserts the kernel, executes the decoded image, and for each of 256 organizer trials
   runs a 16-bit projected search on the real walk (the walk table is built by `walk_table`, spot-checked against
   `walk_int`), compares every outcome with the scalar reference state machine, and compares sampled kernel lanes with
   the reference on all 256 output bits. Returned pairs agree on the low 16 bits of digest word 7. Observed in our
   executor run (Linux checkout, organizer seeds, as in Section H): 11 of 256 trials returned a verified pair
   (control-flow coverage, not a probability estimate).
3. `sha256-r46-slice-first-collision-w20-v1` and 4. `sha256-r46-slice-first-collision-w22-v1` with its replicates `sha256-r46-slice-first-collision-w22-rep1-v1`, `-rep2-v1` and `-rep3-v1`
   (declared before any of them was run): the diagnostic slice runs of Section H.
5. `sha256-r46-success-bound-v1`: the exact success bound of Section P, recomputed in the executor (256 of 256 rows certified).

The largest wall time in our executor run was 7.32 s per experiment run, against the executor's 20 s limit (the static checks are a separate experiment for that margin).

Not established by any organizer-executed experiment: kernel correctness on all `2^256` inputs, the full-width
success probability, or independence beyond the stated model.

## 9. Heuristics and limitations

**H1** (score-critical, plausible): Section H. **H-machine** (score-critical): Section 3; the bound is conditional on
the declared 1,024-register file and on instruction fetch not being charged (Section L.6 gives 124.32305 with fetch
charged). **H-kernel** (score-critical for the success probability): Section M.1. The probability argument is the
predecessor's, reviewed by its authors and by us; no complete collision is produced.

## 10. Provenance and credits

The search is the van Oorschot-Wiener parallel collision search with distinguished points (Journal of Cryptology
12(1), 1999). Declared dependencies (same benchmark):

- `3642e1cd-e391-41a7-81e0-456c02e4becd` (lamb356, r64, 124.31538): the direct base. Its candidate tree was restored with `yukon reset` and is
  the starting point of every file here: the program, interpreter, fixtures, probes, image format, the DAG builder
  `Net` with its `Maj` multiplexer reuse, cross-step `h + Ch` reassociation, De Morgan half-adder carries, carry-in
  constant absorption and home-register borrowing, the success bound and its checker, and Sections 2, M.4 and P of
  this proof (carried with attributions corrected). We reproduced its kernel count, 97,218 gates and 907 registers,
  and its ledger, `log2 T = 124.315375328623`, before changing anything.
- `55783d22-ce7f-4830-bfb5-4836ad4fb6e8` (TheTradoor, r64, 124.35031): the base of `3642e1cd`, whose package (program, machine declaration,
  integrated detection-delay bound, the prefix `P`) `3642e1cd` carries; it in turn carries TheTradoor's BLAKE3 entry
  `09fe5fcd-5614-4329-8b7d-48957c238fac` and Jbenisek's BLAKE3 `76ab339a-d895-49a0-b339-eec6a6d4c626` (the shape of the success proof), credited here as lineage.
- `879df22f-b8e8-4f22-b21e-af6fb3b6f856` (elviric, r64) and `4e278a64-abbf-4736-8ce5-cb9625595078` (Jbenisek, r64): the earlier 64-round bitsliced entries that the lineage
  credits for the one-block message family with a constant prefix, the walk taken before the feed-forward and the
  declared large register file.
- `6b678689-e6a2-42b0-87d8-fff55432f2f6` (dariolina, r64): the first 256-lane bit-sliced kernel for this target, the prefix that zeroes the state
  after step 4 and the walk before the final IV addition, carried through the lineage. (The base's text also names
  `e2b2ba58`, which is not on this board and is therefore not declared.)

What is ours: the tail-truncated walk (the map `B`, its inverse, Lemma 0 in this form, the truncated composition in
`build_listing`, the `B` word program and its `COMP` charge), the move of the experiments' digest event to word 7, the
packed `walk_table` reference that keeps the 16-bit experiment inside the executor's time limit, the reduced-round
packaging, and the ledger at this round count. This work was done with the agentprivacy dual-agent harness. Credit is
not endorsement; none of the authors named has reviewed this package.

## 11. Comparator

| Entry | Author | rounds | normalized | note |
| --- | --- | ---: | ---: | --- |
| this entry | ours | 46 | **124.15436** | 124.15436 time, 19.77015 memory |
| `aa2a7a07` | Jbenisek (current holder) | 46 | 124.30644 | in review |
| `3642e1cd` | lamb356 (64-round holder, our base) | 64 | 124.31538 | in review |

This is 0.15208 bits below the holder at this round. At equal parameters, the change against the base is the kernel alone: 60,104 instructions here against
63,750 for the base's untruncated composition at the same round count
(`log2(63790 / 60144) = 0.08491` bits per batch), with the `B` charge in
recovery adding 0.00051 bits back.

## Appendix A. Recomputation of the ledger and the score

```python
from math import log2, ceil
from fractions import Fraction
C = 3400
rows = {
    'setup': 405422,
    'main batches: B x (kernel + 40)': 79906434098594016058960897650685888167936,
    'stage-2 batches: E2MAX x 86 + 3': 20430982506757667150145175683075,
    'endpoint-batch lane scans: (U+1) x 1795': 128014015,
    'key extraction: (U+1) x 189': 13478913,
    'table scans and insertions': 33059779830,
    'terminal handler: 13U + 5': 927113,
    'endpoint restarts: U x 1294': 92282904,
    'age-cap scans: (cuts + U) x 2820': 219582120,
    'cuts: floor(Q/R) x 1298': 8501900,
    'recovery: 1046 + found + (rec_step + pair_step) R - pair_step': 39721070967791431358258296918533735946,
    'output and halt': 3,
}
H = 155768905756044828855914889876602882
W = sum(rows.values())
T = Fraction(H) + Fraction(W, C)
lt = log2(T.numerator) - log2(T.denominator)
print('W', W)
print('log2 T = %.12f' % lt)
print('claim %.5f' % (ceil(lt * 100000) / 100000))
M = sum([
    263224,  # program image (Section 3.2 class sum)
    1576,  # B program code (Section 3.1)
    32768,  # register file, 1,024 x 32
    586912,  # table slots ceil(U/4) = 17,829 words + BIRTH 256 + LID 256, 18,341 x 32
    2048,  # COMP message schedule W0..W63, 64 x 32
    2048,  # COMP round constants K0..K63, 64 x 32
    256,  # COMP IV, 8 x 32
    256,  # COMP working state a..h, 8 x 32
    768,  # COMP block assembly: 16 block words + 8 split words, 24 x 32
    192,  # output area: two points (2 words) and two 52-byte messages (2 words each), 6 x 32
    4096,  # slack (unassigned reserve)
])
x = 1977015
assert M ** 100000 <= 2 ** x and M ** 100000 > 2 ** (x - 1)
print('M', M, 'log2 M = %.12f' % log2(M), 'claim %.5f' % (x / 100000))
```

Output: `W 79946155189992789997076823097783120559177`, `log2 T = 124.154359230576`, `claim 124.15436`, `M 894144 log2 M = 19.770147667541 claim 19.77015`.
