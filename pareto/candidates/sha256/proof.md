# SHA-256, 64 rounds: bounded-restart bitsliced collision search with an integrated detection-delay bound

This package claims an ordinary 256-bit collision construction for the complete 64-round SHA-256 hash (64 is
the full SHA-256 round count) with total time `2^124.31538` target compressions, memory `2^19.97916`
bytes and success probability at least 0.39. Memory is below one mebibyte, so the normalized objective
`normalizedTimeMemoryLog2 = timeLog2 + max(0, memoryLog2Bytes - 20)` equals **124.31538**.

It is the algorithm, machine declaration and probability argument of our BLAKE3 round-7 submission
`09fe5fcd-5614-4329-8b7d-48957c238fac` (C4, 124.96952), carried to SHA-256 round 64: the search program, the
register-file machine, the integrated detection-delay success bound and the bitsliced kernel generator are
unchanged in structure, while the kernel computes the SHA-256 compression of a one-block message, the
distinguished predicate is a plain 112-zero-bit test, and the parameters are re-planned for this target. Every
assumption inherited from the BLAKE3 entry is audited against the exact SHA-256 target in Section 1.3. No
complete collision is exhibited and the attack is not executed at full scale.

| Quantity | Value | Basis |
| --- | --- | --- |
| rounds | 64 | target profile `sha256-r64-prefix-v1` |
| time_log2 | 124.31538 | Section L; exact `log2 T = 124.315375328623`, rounded up |
| memory_log2_bytes | 19.97916 | Section L.4; 1,033,536 bytes |
| normalizedTimeMemoryLog2 | 124.31538 | memory below `2^20` adds zero |
| success_probability | 0.39 | Section P (random-function bound 0.390036155778183, rounded down) and H1 |
| preprocessing_log2 | 0 | the fixed program image is the algorithm (Section M.5) |
| nonuniform_advice_log2_bytes | 0 | uniform program; no stored search results |

Declared heuristics: **H1** (transfer of the random-function bound to the fixed target, score-critical),
**H-machine** (the declared 1,024-register file, score-critical; Section L.6 quantifies the two declared
accounting conventions) and **H-kernel** (kernel correctness on all inputs, score-critical for the success
probability).

The sections are numbered 1 to 3 and 8 to 11, with the lettered sections M (the machine program), L (the
resource ledger), P (the probability argument) and H (the fixed-target premise) between them. The lettering is
inherited from the predecessor; no section is missing, and every cross-reference in this document names its
section rather than a number in a sequence.

## 1. Target, message encoding and the walk

### 1.1 The target and the two messages

The target is standard SHA-256 (FIPS 180-4) with the standard fixed IV, the standard message schedule and
constants at their original indices, the standard length padding, the standard feed-forward and all 256
output bits, executing compression rounds 0 through 63 on every padded block, per the organizer profile
`sha256-r64-prefix-v1`. Sixty-four is the complete SHA-256 round count, so the target is the unreduced hash.

A point is a 256-bit integer `u`. Its message is the 52-byte string

    M(u) = P || BE256(u),

where `P` is the fixed 20-byte prefix of five big-endian words, and the 32 bytes carrying `u` are the eight
32-bit words `u_j = (u >> 32j) mod 2^32` for `j = 0, ..., 7`, each encoded big-endian and placed in that
order, so `u_0` lands in message word `W5` and `u_7` in `W12`. (Only injectivity of `u -> M(u)` is used, but
the order is stated because the kernel constant-folds against it, so a reimplementation must use the same
one.) `M(u)` has 416 bits, so FIPS 180-4 padding appends `0x80`, three zero bytes and the 64-bit big-endian
length 416, giving exactly one padded block with message words

    W0..W4 = P,   W(5+j) = u_j for j = 0..7,   W13 = 0x80000000,   W14 = 0,   W15 = 416.

The map `u -> M(u)` is injective and every `M(u)` lies in the message domain (52 bytes, far below `2^64`
bits). Distinct points therefore give distinct messages, as the relation requires.

The prefix `P` is a fixed public constant, chosen once so that the working state after step 4 has
`a = b = d = e = f = 0`; this only lets the early steps fold into constants in the kernel and has no effect on
the target, the relation or the probability argument. It is not advice: it is five published constants of the
program image, derived from the standard IV by inverting the first five steps, and the program would be
correct, only larger, with `P = 0`.

### 1.2 The walk and Lemma 0

Let `S(u)` be the working state `(a, b, c, d, e, f, g, h)` after step 63 of the single compression of `M(u)`,
read as a 256-bit integer with word `j` at bits `32j .. 32j+31`. The walk is

    f(u) = S(u) XOR PD,   PD = 0xb1e786e05a68a3358a2b7026266d0043bd4e2fb6b48ea98f1d6e63d09fe31034,

where `PD` is the fixed output polarity of the kernel planes (the experiment asserts this value).

**Lemma 0.** For all `u, v`: `f(u) = f(v)` if and only if the complete SHA-256 digests of `M(u)` and `M(v)`
are equal.

*Proof.* XOR with the constant `PD` is a bijection, so `f(u) = f(v)` iff `S(u) = S(v)`. The digest of a
one-block message is the feed-forward `IV_j + S(u)_j mod 2^32` for `j = 0..7`, serialized big-endian. For each
`j` the map `x -> IV_j + x mod 2^32` is a bijection on 32-bit words, so the eight digest words are equal iff
the eight state words are equal. QED

Hence distinct `u != v` with `f(u) = f(v)` yield two distinct messages with equal complete 256-bit digests:
an ordinary collision for the selected target.

### 1.3 Audit of the assumptions inherited from the BLAKE3 entry

The predecessor C4 attacked BLAKE3 round 7. Each of its target-specific assumptions was re-derived here; the
differences are material and are listed in full.

| Item | BLAKE3 r7 (C4) | SHA-256 r64 (this entry) | How it is checked |
| --- | --- | --- | --- |
| message | `0^32 \|\| LE256(u)`, 64 bytes, one chunk and one block | `P \|\| BE256(u)`, 52 bytes, one padded block | 74 encoding checks and the organizer's own digest verification of every returned pair |
| word order | little-endian message words and little-endian digest | big-endian message words and big-endian digest | same |
| padding | block-length field and flags; no length block | `0x80`, zero bytes, 64-bit big-endian length 416 as `W13..W15` | same |
| feed-forward | `v[i] XOR v[i+8]`, so the walk uses an XOR of halves | `IV_j + S_j mod 2^32`, so the walk uses the state before a modular addition | Lemma 0 and the canonical cross-check |
| compressions per message | chunk, parent and root compressions must all be charged | exactly one compression per message | Section L.3 charges one per evaluation |
| digest event mask | low bits of a little-endian digest | low bits of the big-endian first digest word | the organizer recomputes the event on every returned pair |
| distinguished predicate | 111 zero bits and a 4-bit window below 11, density `11 x 2^-115` | 112 zero bits, density exactly `2^-112`, no window test | the declared experiment and the probes |
| recovery step cost | 76 operations (window test present) | 72 operations (no window test) | measured by the probes and asserted equal to the closed form |
| kernel | 45,974 instructions, 771 registers | 97,218 instructions, 907 registers | asserted in the executor |

Two checks make the encoding audit organizer-executed rather than self-reported. First, the declared
experiment recomputes the working state of 74 inputs (zero, all-ones, eight single-word patterns and 64
seed-derived points) by two independent routes: this package's explicit round loop, and the canonical library
SHA-256 of the same message with the feed-forward undone word by word. Agreement pins the message encoding,
the word order, the three padding words and the feed-forward against an implementation this package did not
write. Second, the organizer itself hashes both messages of every returned pair with its own SHA-256 and checks the
declared event. In our runs of the organizer's harness and pinned image it performed 33, 239 and 109 digest
evaluations on the implementation experiment and the two slice experiments: one sizing probe each, plus two per
returned pair, for 16, 119 and 54 returned pairs. A wrong prefix, padding word, byte order or feed-forward
would fail these, and the official evaluation repeats them independently.

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

Every scalar `f` evaluation in recovery is one target compression plus one XOR. Reconstruction, alignment and
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
operations, counts working state and code in memory, and fixes no register count. This entry declares a
load/store machine with a fixed file of `NREG = 1,024` registers of 256 bits.

- A register is one of the 1,024 words of the file. Registers are named statically by instruction fields and
  are never reached by a computed address. The file's 32,768 bytes are included in
  `memory_log2_bytes` as storage; registers are not memory-addressable, and a register operand is not a load
  or a store.
- Memory is every other word, reached only by `LD` and `ST` through an address held in a register; every such
  access is one charged operation. The table, the lane metadata and the `COMP` working state are memory.
- An operation on registers costs its primitive operation(s).

The file size is this entry's declared, score-critical convention: the contract neither forbids nor fixes it.
Section L.6 states what is and is not quantified about smaller files. The program uses 957 of the 1,024 registers:
907 for the kernel (the planes of `u` and `f(u)` in registers `0..255` and temporaries) and 50 control
registers (constants including the all-ones word, counters, `rho`, recovery state).

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
| COMP d,a | the complete 64-round SHA-256 state of `M(a)` | one compression unit + 64 |
| OUT a,b | store the two output points | 2 |
| HALT n | stop with code n | 1 |

`COMP` is one target compression of the single block of `M(a)`, charged 64 additional word operations as an
upper allowance for preparing its input and output: 16 to split the point into eight message words, 24 stores
of the 16 block words and the padding words, 16 loads of the IV and constant state words, and 8 to recombine
the output. The cost model prices one selected-round compression at one unit and every other primitive word
operation at `1/C`; the main loop does not invoke the compression primitive but evaluates 256 compressions per
batch by explicit word operations, each charged `1/C`, so every compression is charged through its operations
and none is charged twice. The program is the machine's finite control; instruction fetch is not a primitive
operation of the cost model and is not charged (Section L.6 gives its cost if it were).

### 3.2 Program image

The program is a byte image with three formats fixed by opcode: an 8-byte control format (opcode, three
10-bit register fields, a 24-bit immediate or branch byte offset), a 4-byte kernel word (opcode, three 10-bit
register fields) and a 40-byte constant format. The kernel is a block of 97,218 4-byte words introduced by
the 8-byte `KERNEL` control instruction whose immediate holds the block length, so the image is decodable
without a tag bit. Ten-bit fields name all 1,024 registers; every non-branch immediate and every branch
offset fits in 24 bits (the image is 411,680 bytes). The declared experiment encodes
the full-width program, decodes the image, asserts that the decoded program equals the generated one and that
the image length equals the ledger's code size, and executes only the decoded program.

## M. The machine program

The program is emitted by `build_program` in `experiments/sha256_machine.py` for any parameter set.

### M.1 Kernel

The kernel computes the planes of `f(u)` from the planes of `u` in place in registers `0..255`. A
constant-folding Boolean DAG builder maps SHA-256's modular additions to ripple-carry full adders (at most
five gates per bit; constants fold), the rotations and shifts of `Sigma0`, `Sigma1`, `sigma0` and `sigma1` to
plane relabelings and constant-zero fills, the choice function `Ch(e,f,g)` to a three-operation multiplexer,
the majority `Maj(a,b,c)` to `mux(b XOR c, a, b)`, and the output constants to the stored polarity `PD`.
The DAG has 97,218 gates (77,406 XOR, 7,476 AND, 12,336 OR and no NOT); in-place register allocation in
creation order, with each output's home register reserved once its input dies and a freed home borrowed as
scratch only when the borrower dies before its output, needs 907 registers and 0 output moves, giving 97,218
instructions per batch with no memory access. The experiment asserts the instruction count, the gate split,
the register count and `PD`.

Full adders with three variable inputs use `mux(a XOR b, c, a)` when `a XOR b` reassociates with an existing XOR
(reusing `h_t XOR g_t = f_{t-1} XOR g_{t-1}` in `h + Ch`), and otherwise the pivot rule (two polarities agree;
`u = q XOR p`, `v = r XOR p`, `sum = u XOR r`, `carry = (u AND v) XOR p`). Constant-input adders absorb bit-0
carry-ins and form the carry without a complement gate (in one gate via De Morgan when `k = 1`). The multiplexer
`Ch` is `y XOR (s AND (x XOR y))` or `x XOR ((NOT s) AND (x XOR y))`, whichever keeps its AND unmixed, so `Ch` and
`Maj` (reusing `b_t XOR c_t = a_{t-1} XOR b_{t-1}`) cost three operations per bit and no complement.

Correctness argument (**H-kernel**). (1) Every gate-construction rule, including the `Ch` multiplexer and the
majority carry, is checked exhaustively on all operand classes by the declared experiment (12,023 cases,
each over all input assignments in bit-parallel form).
(2) The word-level composition in `build_listing` follows FIPS 180-4 line for line (message schedule for
`t >= 16`, `Sigma1`, `Ch`, the five-term `T1`, `Sigma0`, `Maj`, `T2`, and the state rotation), mirroring the
explicit scalar reference `state_words`. (3) A static check proves that the register-allocated listing
computes the gate DAG for every input: it tracks which DAG node each register holds and verifies every operand
reference and the final output placement. (4) The scalar reference is itself pinned to the canonical library
SHA-256 on 74 inputs (Section 1.3), and sampled kernel lanes are compared with it on all 256 output bits in
every trial. Step (2) is established by inspection within this package, which is why the claim is declared as
the score-critical heuristic H-kernel.

### M.2 Main loop, stage 2 and the handlers

Per batch: `KERNEL` header 1 plus 97,218 kernel words, 31 ORs for stage 1, a comparison and branch (2) and
six control operations, in total 97,258 operations. A stage-2 entry costs
`d - s1 + 5 = 85` operations when a lane is distinguished and one more when the stage-1 hit was not
(the window operations of the predecessor are absent). The endpoint-batch lane scan costs 1,795; key
extraction `1 + 4k = 189`; a table scan 13 per non-matching entry and an insertion at count `c`
costs `20 + 13c`; a restart 1,292, 1,294 or 1,295 depending on the return; a cut scan 2,564 plus at most 256
minimum updates and 3 per cut; recovery 1,046 fixed, 72 per reconstruction step, 69 per alignment step, 138
per non-final paired step and 268 for the final paired step and check; output and halt 3. Setup is
405,422 operations. Every one of these closed forms is measured at the full-width parameters under
lane-wise test functions and asserted equal by the declared experiment, which fails if any of them differs.

### M.3 Storage layout

Memory words: table slots `ceil(U/4) = 17,829`, `BIRTH` 256 and `LID` 256, in total 18,341 words
(586,912 bytes). Register file 32,768 bytes. Code
411,680 bytes. The `COMP` working state receives a 2,048-byte
allowance. Setup uses the same storage as the search.

### M.5 The fixed program image is the algorithm

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
`C = 4,912` is quoted from the organizer's contract printout; it is also recoverable from the benchmark's own
cost model, whose word-operation weight is exactly `1/4,912`.

## L. Resource ledger

### L.1 Worst-case event counts

| Event | Bound | Reason |
| --- | --- | --- |
| batches | `B = 1,328,585,296,930,600,160,597,248,231,755,218,944` | horizon |
| stage-2 entries | `E2MAX + 1` | budget halt (the last entry performs 3 operations) |
| endpoint batches, handlers | `U + 1 = 71,317` | each endpoint batch contains at least one handler |
| insertions, endpoint restarts | `U = 71,316` | capacity |
| cuts | `floor(Q/R) = 6,550` | disjoint `R`-evaluation blocks |
| cut scans | `6,550 + U = 77,866` | a scan that cuts nothing requires an endpoint restart since the previous scan |
| recovery | 1 | terminal |

### L.2 Word-operation terms (exact integers)

| Term | Operations |
| --- | ---: |
| setup (constants, randomness, memory clear, 256 initial lanes) | 405,422 |
| main batches: B x (kernel + stage-1 test + loop control) | 129,215,548,808,876,310,419,367,168,524,049,084,055,552 |
| stage-2 batches: E2MAX x stage2_miss + halting entry | 20,430,982,506,757,667,150,145,175,683,075 |
| endpoint-batch lane scans: (U+1) x epscan | 128,014,015 |
| key extraction: (U+1) x key | 13,478,913 |
| table scans and insertions: sum_{c<U} (insert + per_entry c) | 33,059,779,830 |
| terminal handler: scan of at most U entries | 927,113 |
| endpoint restarts: U x restart | 92,282,904 |
| age-cap scans: (cuts + U) x (scan + min updates) | 219,582,120 |
| cuts: floor(Q/R) x (cut bookkeeping + restart) | 8,501,900 |
| recovery operations: rec_fixed + found + (rec_step + pair_step) R - pair_step | 10,903,823,402,923,138,019,914,042,291,362,202,776 |
| output and halt | 3 |
| **W (sum)** | **129,226,452,652,710,216,064,144,749,716,519,144,913,623** |

The recovery row uses `72 l1 + 69 |l1 - l2| + 138 (min(l1, l2) - 1)`, maximised at `l1 = l2 = R`, giving
`(72 + 138) R - 138`. Compressions: `H <= 3R + 2 = 155,768,905,756,044,828,855,914,889,876,602,882`.

### L.3 Total time

    T = H + W/C,   C = 4,912
    log2 T = 124.315375328623        claim time_log2 = 124.31538

`C = 4,912` is the round-64 `reference_operation_cost` printed by the organizer's
`pareto_candidate.py --family sha256 --rounds 64 --show-contract`. The main loop is
99.403 percent of `T`; the kernel alone is `log2 = 124.306143258698`. The bound holds for every
function and every `rho`, including failed attempts; there is one attempt and no amplification. Every message
of the construction is one padded block, so one compression per evaluation is both charged and sufficient.

### L.4 Memory

    code 411,680 + register file 32,768
      + memory words 586,912 + COMP state 2,048
      + output area 128 = 1,033,536 bytes
    log2 = 19.979157210741        claim memory_log2_bytes = 19.97916

Memory includes code, the whole declared register file, the table, the lane metadata, the `COMP` working
state and the output area that `OUT` writes (four 256-bit words: the two colliding points and the two 52-byte
messages, which the cost model counts under "messages" and "working state"). There is no advice and no
precomputed data. Memory is below `2^20` bytes by
15,040 bytes, so it adds nothing to the normalized score.

### L.5 What is asserted by execution, and by whom

The declared experiments run only in the organizer's isolated executor. The statements below are what those
experiments assert when they run, and every one of them was observed to hold in our own runs of the
organizer's harness and its pinned image; the official evaluation executes them again independently, and this
package claims no result from a run it performed itself. Asserted by the experiment, and so established once
it runs: the
kernel size, gate split and register count and the static proof that the allocated listing computes the DAG;
the agreement of the explicit scalar reference with the canonical library SHA-256 on 74 inputs; the image
round trip and size; every per-handler closed form, measured at the full-width parameters; and outcome-level
equivalence of the program and the scalar reference at reduced width, including the budget stop. Established
mathematically: the event bounds of L.1 and the arithmetic of L.2-L.4, which Appendix A recomputes from the
integers printed in this package; an administrative calculator outside the package agrees, but the appendix is
the check that travels with the submission. Established by the declared checker experiment: the exact
success bound of Section P. Assumed: the declared register file (H-machine), the specification-following
composition of the kernel (H-kernel) and the premise H1.

### L.6 Sensitivity

Each figure below is the complete ledger recomputed with the stated change, not a ratio of one row.

| change to the declared convention | result |
| --- | ---: |
| instruction fetch charged at one 256-bit load per 32 bytes of kernel code (`ceil(97,218 x 4 / 32) = 12,153` operations per batch) | time and normalized 124.48429, that is **+0.1689 bits** |
| every instruction charged 36 bytes of code instead of the declared formats | memory 4,221,460 bytes = `2^22.00932`, normalized 126.32470 |

Both are disclosed because they are material: at +0.1689 bits the entry would score
124.48429, which is **above both comparators of Section 11**, so this entry's advantage depends on
the declared convention that instruction fetch is not a primitive operation of the cost model. The comparators
at this target declare the same convention (Section 10), which is why Section 11 compares under it; an
adjudicator who rejects the convention should reject it for the comparators too.

Smaller register files require spill code in the kernel and raise the time bound. No numeric value for smaller
files is claimed: the predecessor's measured spill curve was taken on a BLAKE3 gate network and does not
transfer to this one, and we did not re-measure it here. The bound is conditional on the declared file.

## P. Success probability in the random-function model

**Model.** `F` is a uniformly random function on 256-bit strings and `rho` is uniform and independent of `F`
(the bound in fact holds for every fixed `rho`). The bound below is a theorem in this model; its application
to the fixed SHA-256 target is the heuristic H1 of Section H. It assumes that the main-loop kernel computes
`F` exactly (H-kernel).

The argument below is the integrated detection-delay bound. Its shape follows the public proof of submission
`76ab339a` (Jbenisek, Lemma 2) and our own entry `09fe5fcd` (C4, Section P), both credited in Section 10; it
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
trade is not taken, and the margin is deliberately left at 0.000036155778. The declared experiment `sha256-r64-success-bound-v1` recomputes all of
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

The authors re-checked the argument item by item against the decoded machine program. This is a self-report,
not an organizer-executed result. The items were: the
serialization of a batch before any handler and of handlers in ascending lane order; freshness of a
continuing lane's input and of a restarted lane's start; exactness of the age cap (`NEXTCUT` never exceeds
`min BIRTH + R`); uniqueness of table keys and the absence of eviction; recovery of any true match; and the
identity of the counted quantities with the program's values (`Q = 256B`, 78,122 identifiers
below `IDL = 131,072`, `U = 71,316 > k = 67,420`, 47 key bits disjoint from the 112 bits the predicate
reads, and `R` and `E2MAX` as declared). The reduced-width fixtures and the full-width probes of the declared
experiment check the control flow and the handler costs that these items assume. A valid random-function
bound does not imply a bound for every function, which is why the transfer is declared as H1.

## H. The fixed-target heuristic H1 and its evidence

**Statement.** For the fixed walk `f(u) = S(u) XOR PD` at the complete 64-round SHA-256, the success
probability of this algorithm over its uniform offset `rho` is at least the random-function bound of
Section P, hence at least 0.39.

**What exactly is being assumed.** Section P proves a statement whose probability is over the random function
`F`, and it holds for every fixed `rho`. The benchmark's probability space is the opposite one: the target is
fixed and the probability is over the algorithm's own coins, of which this algorithm draws exactly one, the
256-bit word `rho`. H1 is therefore not an approximation of one number by another; it is the exchange of those
two quantifiers, from "for every `rho`, the average over `F` is at least 0.390036" to "for the one fixed `f`,
the average over `rho` is at least 0.39". Nothing in this package proves that exchange, and no concentration
argument over `F` is offered for it. It is assumed, declared score-critical, and the entry is exactly as
strong as it. One structural feature of the algorithm is worth naming in that light: all 78,122
starts are `rho + i` for consecutive `i`, so as messages they differ only in the low word `W5` of a single
block, and the premise is being asked to hold for that highly structured start set rather than for
independent uniform starts.

**Why the random-function model is the relevant model.** Sixty-four rounds is the full round count of
SHA-256, so the target is the complete, unreduced hash on single-block messages. The algorithm is generic: it
uses no property of SHA-256 beyond evaluating it. The proof uses only that answers to fresh queries along the
search are uniform and independent of the history, which is the standard model for generic collision search
against an unbroken 256-bit hash. The parameters leave a margin of only 0.000036155778 above 0.39, so any
fixed-target deficit larger than that would defeat the claim. We know of no property of full SHA-256 that
would produce such a deficit against a generic procedure of this kind, and none is known publicly; that is
the whole of the support, and it is an absence of evidence rather than evidence of absence.

**Diagnostic experiments, and what they are not.** Two declared experiments exercise the mechanism that
carries the bound (the first duplicate among lane-serialized fresh queries from consecutive starts) on the
fixed target itself. For each organizer trial a separate slice `g(u) = f(c | u) mod 2^n` is taken, with `c` a
seed-derived point whose low `n` bits are cleared, so different trials probe different parts of the fixed
function. 256 lane walks start at 256 consecutive slice values and are evaluated by the same bitsliced kernel,
serialized in batch and lane order exactly as in the search. Under the random-function model every query
before the first event is fresh and the first-event law is exact, which fixes the model probability of a
returned pair before execution. The organizer verifies every returned pair on the declared low digest bits.

| Experiment | n | slots | model P(pair) | model expectation of 256 | observed |
| --- | ---: | ---: | ---: | ---: | ---: |
| `sha256-r64-slice-first-collision-w20-v1` | 20 | 1,280 | 0.448648 | 114.85 | 119 |
| `sha256-r64-slice-first-collision-w24-v1` | 24 | 3,072 | 0.237789 | 60.87 | 54 |

**These results are diagnostic, not a calibrated confirmation of H1, and this entry does not present them as
one.** The organizer seed material is public and fixed, and we chose the widths, the slot counts and the two
experiments ourselves; there is no holdout nonce and no pre-registration, so the comparison of the observed
counts with the model values carries no advertised coverage, no confidence statement and no calibrated
false-alarm rate. What the two runs show is the absence of a gross departure from random-function behaviour in
this mechanism at widths 20 and 24: the observed counts, 119 and 54 of 256, sit near the
model expectations 114.85 and 60.87 of 256. The deficit that would matter at full width is
0.000036155778; no experiment of this kind, at any feasible width, can detect a deficit of that size, and a failure
would not by itself distinguish a kernel error from non-randomness. H1 is therefore plausible rather than
established, and the entry's claim is exactly as strong as H1.

**Scope and limitations.** The slice experiments test uniformity and freshness of the fixed target along
lane-serialized walks from consecutive starts, with the search's lane serialization and consecutive-start
structure but with the high input bits fixed by a seed constant, at widths 20 and 24 on 512 slices. They do
not test the `2^128`-query regime, the full-width distinguished-point and key events, or the full function
rather than its slices, and they cannot exclude a property that appears only at full scale. The third
declared experiment (the implementation diagnostic) and the fourth (the exact bound checker) carry no
information about the fixed target at all: the first is control-flow and cost evidence, the second is
arithmetic.

## 8. Declared experiments

Four experiments are declared, each to be run by the organizer in its isolated executor. The statements below
are what each experiment asserts and would fail on; where a count observed in our own runs of the organizer's
harness is quoted, it is marked as such. This package reports no result from a run it performed itself.

1. `sha256-r64-bounded-machine-w16-v1` regenerates the kernel and asserts its instruction count, gate split,
   register count and `PD` and that all statically named registers fit the declared file; checks the explicit
   scalar reference against the canonical library SHA-256 on 74 inputs; proves statically that the allocated
   listing computes the gate DAG; checks all 12,023 gate-rule cases exhaustively; encodes, decodes and asserts
   the round trip and size of the full-width image; runs sixteen deterministic control-flow fixtures against
   the scalar reference, including the window and no-window predicates and the budget halt; measures every
   handler cost at the full-width parameters and asserts the closed forms; and, for each of 256 organizer
   trials, runs a 16-bit projected search on the real target with the real kernel, compares every outcome
   field with the scalar reference, and compares sampled kernel lanes with the scalar reference on all 256
   output bits. The projected search uses the deployed window-free predicate (`win = 16`), so the stage-2 and
   recovery paths it exercises are the ones the full-width program contains; the window variant is covered
   separately by the fixtures, which run both. Its success frequency is control-flow coverage, not a
   probability estimate, and the projection is a 16-bit slice of the target rather than the target itself.
2. `sha256-r64-slice-first-collision-w20-v1` and 3. `-w24-v1`: the diagnostic slice runs of Section H.
4. `sha256-r64-success-bound-v1`: the exact success bound of Section P, recomputed in the executor. It
   returns no message pairs and makes no claim about the fixed target.

Not established by any organizer-executed experiment: kernel correctness on all `2^256` inputs, the
full-width success probability, or independence beyond the stated model.

## 9. Heuristics and limitations

**H1** (score-critical, plausible): Section H. **H-machine** (score-critical): Section 3; the time bound is
conditional on the declared 1,024-register file and on instruction fetch not being charged. **H-kernel**
(score-critical for the success probability): Section M.1.

Other limitations: the probability argument has been reviewed by its authors and an advisory critic only; no
complete collision is produced; the margin above 0.39 is 0.000036155778, so the claim is exactly as strong as H1.

## 10. Provenance and credits

The search is the van Oorschot-Wiener parallel collision search with distinguished points (Journal of
Cryptology 12(1), 1999). Material sources among published HashSmash submissions, declared as dependencies:

- `09fe5fcd-5614-4329-8b7d-48957c238fac` (ours, C4, BLAKE3 r7): the direct source of this package. The search
  program, the bounded-restart control flow, the register-file machine declaration and image format, the
  interpreter, the fixtures and probes, the integrated detection-delay success bound and the bitsliced DAG
  builder with its pivot and complement-free adder rules are taken from it unchanged in structure. This entry
  changes the target, the message encoding and its Lemma 0, the kernel, the distinguished predicate and all
  parameters, and adds the canonical-reference encoding audit and the declared bound checker.
- `76ab339a-d895-49a0-b339-eec6a6d4c626` (Jbenisek, BLAKE3): the structure of the success proof, re-derived in
  C4 from its public proof text and carried here; and the complement-free carry rule for constant-pivot
  adders.
- `4e278a64-abbf-4736-8ce5-cb9625595078` (Jbenisek, SHA-256 r64, 124.39014) and
  `879df22f-b8e8-4f22-b21e-af6fb3b6f856` (elviric, SHA-256 r64, 124.38558): the public entries at this
  target and round count, and the comparators of Section 11. They establish the generic bitsliced
  distinguished-point approach for SHA-256 at this round count, including the one-block message family with a
  constant prefix, the walk taken before the final IV addition and the declared large register file counted in
  memory. We read their public notes as descriptions; no file of either package was copied or executed.
- `0a9640ed-558a-4f0a-aba8-45e89ffcfd7c`, `e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca` and
  `a2e94df7-bff4-4461-ad40-7f75930cb241` (Jbenisek) and `6ae36351-5836-4a46-ad34-227688264123` (jungjipdo):
  the bitsliced kernel approach, the declared register-file convention counted in memory, the polarity mask
  walk, the pivot full adder and the lane-indexed treatment of adaptive histories, all inherited through C4.

Credit is not endorsement; none of the authors named has reviewed this package. All code here was written
independently; no competitor file was copied or executed.

## 11. Comparator

At the same target and round count, at the same contract-minimum success probability 0.39, and with memory at
or below `2^20` bytes in every case:

| Entry | Author | normalized | note |
| --- | --- | ---: | --- |
| this entry | ours | **124.31538** | 124.31538 time, 19.97916 memory |
| `879df22f` | elviric | 124.38558 | the current best scored 64-round entry |
| `4e278a64` | Jbenisek | 124.39014 | its declared predecessor |

The improvement over `879df22f` is 0.07020 bits and decomposes into about 0.0269
bits from the integrated detection-delay bound, which certifies 0.39 at `Q = 2^127.9993` where the
comparators use about `2^128.026`, and about 0.0437 bits from the cheaper kernel: 97,218 kernel
instructions here against the comparator's 100,205 body records, that is `log2(100205 / 97218) = 0.0437`. Our
charged per-batch figure is 97,258 operations, which adds the stage-1 test and the loop control to the
kernel; the comparator's corresponding per-batch figure is 100,242. Both components are at equal success probability and under the same declared
register-file convention that the comparators also use; neither comes from a probability margin, a different
memory accounting or a different machine. No claim is made about human acceptance of any entry.

## Appendix A. Recomputation of the ledger and the score

The rows of Section L.2 and the total are reproduced by this script, which uses only the integers printed in
that table.

```python
from math import log2, ceil
C = 4912
rows = {
    'setup (constants, randomness, memory clear, 256 initial lanes)': 405422,
    'main batches: B x (kernel + stage-1 test + loop control)': 129215548808876310419367168524049084055552,
    'stage-2 batches: E2MAX x stage2_miss + halting entry': 20430982506757667150145175683075,
    'endpoint-batch lane scans: (U+1) x epscan': 128014015,
    'key extraction: (U+1) x key': 13478913,
    'table scans and insertions: sum_{c<U} (insert + per_entry c)': 33059779830,
    'terminal handler: scan of at most U entries': 927113,
    'endpoint restarts: U x restart': 92282904,
    'age-cap scans: (cuts + U) x (scan + min updates)': 219582120,
    'cuts: floor(Q/R) x (cut bookkeeping + restart)': 8501900,
    'recovery operations: rec_fixed + found + (rec_step + pair_step) R - pair_step': 10903823402923138019914042291362202776,
    'output and halt': 3,
}
H = 155768905756044828855914889876602882
W = sum(rows.values())
T = H + W / C
print('W', W)
print('log2 T = %.6f' % log2(T))
print('claim %.5f' % (ceil(log2(T) * 100000) / 100000))
```
