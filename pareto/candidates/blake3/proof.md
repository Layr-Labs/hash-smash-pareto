# BLAKE3 round 7: bounded-restart bitsliced search with re-optimized search parameters (C2)

This package claims an ordinary 256-bit collision construction for the
complete seven-round BLAKE3 hash (the full BLAKE3 round count) with total time
2^125.06299 target compressions, memory 2^19.75094 bytes and success
probability at least 0.39. It is the algorithm, machine and evidence of our
submission 616120b2 (C1, 125.18448 on a declared 1,024-register file) with
re-optimized search parameters: distinguished density 2^-112, a 47-bit key,
a 72,237-entry table of 64-bit slots and a shorter completion allowance,
chosen by exact rational optimization of the same success bound (Section P).
The machine is unchanged: a fixed file of 1,024 registers of 256 bits (its
bytes included in the memory bound as storage), with every computed-address
access a charged load or store (Section 3). The success bound is a random-function
theorem (Section P) transferred to the fixed target by the declared
heuristic H1, supported by exact-law experiments on 512 slices of the target
(Section H). No complete collision is exhibited.

| Quantity | Value | Basis |
| --- | --- | --- |
| rounds | 7 | target profile `blake3-r7-prefix-v1` |
| time_log2 | 125.06299 | Section L; exact log2 T = 125.062988236942, rounded up |
| memory_log2_bytes | 19.75094 | Section L; 882,317 bytes |
| normalizedTimeMemoryLog2 | 125.06299 | memory below 2^20 adds zero |
| success_probability | 0.39 | Section P (random-function bound 0.390152, rounded down) and H1 |
| preprocessing_log2 | 0 | the fixed program image is the algorithm (Section M.5) |
| nonuniform_advice_log2_bytes | 0 | uniform program; no stored search results |

Declared heuristics: H1 (fixed-target transfer, score-critical), H-machine
(declared 1,024-register file, score-critical; the time bound for 32, 64,
128 and 256 registers is given in Section L.6) and H-kernel (all-input kernel
correctness, score-critical for the success probability).

## 1. Target, message encoding and walk

The target is standard unkeyed BLAKE3 with the standard IV, the first seven
compression rounds (rounds 0 through 6) and all 256 output bits, per the
organizer profile. A point is a 256-bit integer u. Its message is the 64-byte
string M(u) = 0^32 || LE256(u): block words m[0..7] = 0 and m[8+j] = bits
32j..32j+31 of u. M(u) is one chunk of one block, so its complete hash is one
root compression with input chaining value IV, counter 0, block length 64 and
flags CHUNK_START | CHUNK_END | ROOT = 11. D(u) is the 32-byte digest read as
a little-endian integer. The map u -> M(u) is injective, and every M(u) lies
in the message domain.

The walk is f(u) = D(u) XOR PD, where PD is the fixed integer

    PD = 0x6bb321f265b2e13c7d821a3d58156f9ad7b24ec8d0fc0f0e088e963e14a7dbc1

written as a conventional big-endian hexadecimal integer; bit i of PD is the
output polarity of kernel plane i. (The historical draft printed the same
digit string but labeled it little-endian, which is a different integer; the
integer above is the one the kernel generator produces and the experiment
asserts.) Because XOR with a constant is a bijection, f(u) = f(v) holds if and
only if D(u) = D(v). Distinct u != v with f(u) = f(v) therefore give two
distinct complete messages with equal 256-bit digests.

## 2. Frozen algorithm

### 2.1 Parameters

| Symbol | Value | Meaning |
| --- | --- | --- |
| lanes | 256 | one bitsliced word holds one bit of 256 points |
| d | 112 | distinguished: bits 0..111 of f(u) are zero; L = 2^112 |
| k | 47 | endpoint key: bits 112..158 of f(u) |
| B | 1079 x 2^110 + 2 = 269.75L + 2 | batch horizon (B0 = 258L analysis batches, h = 47L/4, 2 guard batches) |
| R | 47 x 2^111 + 4 = 23.5L + 4 | per-trail age cap (2h + 4) |
| U | 72,237 | table capacity, never evicted |
| IDL | 131,072 | identifier limit; start t is rho + t mod 2^256 |
| rho | one uniform 256-bit word | the only randomness |

Derived deterministic ceilings (all executions, all functions): Q = 256B lane
evaluations; at most floor(Q/R) = 2,938 cuts (each cut lane has used R
evaluations since its own restart, disjoint from other cuts); at most U
insertions; at most U + 1 endpoint handlers (every non-terminal handler
inserts); at most 256 + U + 2,938 = 75,431 < IDL allocated identifiers, so the
identifier guard cannot fire before another stop.

### 2.2 State

Lane l holds its current point (bit j in plane register P_j, lane bit l),
identifier LID[l] and birth batch BIRTH[l]. Global state: batch counter b,
next identifier NID, table count CNT, the earliest-cut batch NEXTCUT, rho and
the table: one array of 64-bit slots, four per 256-bit word; slot e (bits
64(e mod 4) .. 64(e mod 4) + 63 of word floor(e/4)) holds the 47-bit key in
its low 47 bits and the 17-bit start identifier in its high 17 bits.

### 2.3 Control flow

1. Setup. rho = RAND. Clear the table and metadata words. For l = 0..255,
   restart lane l (identifier l, birth 0). Set b = 1, NEXTCUT = R.
2. Batch b. Evaluate f on all 256 lane inputs at once (the kernel). All 256
   evaluations are charged even if a handler later stops in this batch.
3. Distinguished test. D = OR of planes 0..d-1. Lane l is distinguished iff
   bit l of D is zero. If D is all-ones, skip to step 5.
4. Endpoint handlers, ascending lane order, for each distinguished lane l:
   extract its k-bit key; scan entries 0..CNT-1 for that key. On a match stop
   and run recovery (Section 2.4). Otherwise, if CNT = U, stop with failure
   (capacity). Otherwise write the key and LID[l] at entry CNT, increment CNT
   and restart lane l with birth b.
5. Age cap. If b >= NEXTCUT, scan lanes 0..255: every lane with
   b - BIRTH[l] >= R is restarted with birth b (a cut). Distinguished lanes
   were restarted in step 4, so endpoint handling takes precedence over the
   cap. Then NEXTCUT = min_l BIRTH[l] + R. There is no global cut limit.
6. If b = B stop with failure (horizon); otherwise b = b + 1 and go to 2.

Restart of lane l: if NID = IDL stop with failure (identifier guard; not
reachable for these parameters). Otherwise set LID[l] = NID, BIRTH[l] = b, write
the point rho + NID mod 2^256 into lane l of all 256 planes, NID = NID + 1.

NEXTCUT never exceeds min BIRTH + R, because births only increase. Hence a lane
reaching the cap always triggers the scan in step 5, and the scan exactly
reproduces the reference rule "after the endpoint handlers, cut every
non-distinguished lane whose age is at least R".

### 2.4 Recovery (at most once)

On a key match between stored entry e (identifier s1) and the current lane
(identifier s2, length l2 = b - BIRTH ≤ R, current endpoint E extracted from
the planes):

1. Reconstruct: x = rho + s1; step x = f(x) until x is distinguished, counting
   l1 steps; if R steps pass without an endpoint stop with failure. If x != E
   stop with failure (a false short-key match).
2. Align: a = rho + s1, c = rho + s2; advance the start with the longer trail
   by |l1 - l2| steps. If a = c stop with failure (one start lies on the
   other trail).
3. Paired walk for at most min(l1, l2) steps: if f(a) = f(c) go to 4;
   otherwise a, c = f(a), f(c).
4. Final check: require a != c and recompute f(a) = f(c) (equivalently D(a)
   = D(c)). Output M(a), M(c). Any other outcome is failure.

Every scalar f evaluation in recovery is one target compression plus one XOR.
Reconstruction, alignment and the paired walk use at most l1 + |l1 - l2| +
2min(l1, l2) ≤ 3R compressions; the final check uses 2.

### 2.5 Termination codes

1 collision returned; 2 false short-key match; 3 start overlap; 4 table
capacity; 5 identifier guard; 6 horizon; 8 recovery inconsistency (cannot
occur for a true endpoint match; retained as an explicit guard).

### 2.6 Inconsistencies resolved by this freeze

- Search: the bounded-restart first-collision design (no global cut halt,
  per-lane age cap R, B = B0 + h + 2) replaces the historical
  "third cut halts" search with B = 2^119.9994 and H = 111.
- Distinguished predicate and key: low 112 bits of f, then bits 112..158
  (C1 used 113 and 64 bits; Section P re-optimizes these);
  replaces the historical "last output word" predicate and 48/56-bit keys.
- Table layout: one 64-bit slot per entry (47-bit key, 17-bit identifier),
  capacity 72,237;
  replaces the 9- and 24-byte entry variants and the identifier width that
  could not represent the required identifiers.
- Lengths: not stored; recovery reconstructs the stored trail (≤ R steps).
- Recovery evaluates f with the scalar target compression, not with the
  bitsliced kernel, and checks complete digests explicitly.
- PD: the integer of Section 1 (the label in the historical appendix was wrong).
- Randomness: one RAND word; seed expansion appears only in the diagnostic.
- The historical figures 124.97996, 0.3900000143, 84,750 entries and
  1,029,908 bytes are not used.

## 3. Machine model (H-machine)

### 3.1 Word RAM with a declared register file

The cost model specifies a classical 256-bit word RAM, prices "256-bit load
or store" separately from word operations, counts working state and code in
memory, and fixes no register count. This entry declares a load/store
machine with a fixed file of NREG = 1,024 registers of 256 bits. Definitions:

- A register is one of the 1,024 words of the file. Registers are named
  statically by instruction fields and are never addressed by a computed
  address. The file's 32,768 bytes are included in memory_log2_bytes as
  storage; registers are not memory-addressable, and a register operand is
  not a load or store.
- Memory is every other word. Memory is reached only by LD and ST through an
  address held in a register; every such access is one charged operation.
  The table (keys and identifiers), the lane metadata (births and
  identifiers) and the COMP working state are memory.
- An operation on registers costs its primitive operation(s); a register
  operand is not a memory access.

The file size is the entry's declared, score-critical convention: the
contract neither forbids nor fixes it, and Section L.6 gives the bound for
smaller files. The program uses 822 of the 1,024 registers: 776 for the
kernel (planes of u and f(u) in registers 0..255 and temporaries) and 46
control registers (constants, counters, rho, recovery state).

| Instruction | Semantics | Charge |
| --- | --- | --- |
| XOR, AND, OR d,a,b; NOT, MOV d,a | bitwise on registers (MOV = OR a,a) | 1 |
| ADD, SUB d,a,b; ADDI d,a,imm | modulo 2^256 | 1 |
| SHL, SHR d,a,b; SHLI, SHRI d,a,imm | shift by register or immediate | 1 |
| LDI d,imm | load a 256-bit constant into a register | 1 |
| LD d,a; ST a,s | load/store a memory word at the address held in register a | 1 |
| BEQ, BNE, BLT, BGE a,b,target | unsigned comparison plus conditional branch | 2 |
| JMP target | unconditional branch | 1 |
| RAND d | independent uniform 256-bit word | 1 |
| COMP d,a | complete 7-round BLAKE3 digest of M(a) | one compression unit + 64 |
| OUT a,b | store the two output points | 2 |
| HALT n | stop with code n | 1 |

COMP is one target compression of the block M(a), charged 64 additional word
operations as an upper allowance for preparing its input and output: 16 to
split the point into eight message words (shift and mask), 24 stores of the
16 block words and the counter, length and flags, 16 loads of the IV and
constant state words, and 8 to recombine the output words (64 in total). The
cost model prices one selected-round compression at one unit and every other
primitive word operation at 1/C; the main loop does not invoke the
compression primitive but evaluates 256 root compressions per batch by
explicit word operations, each charged 1/C, so every compression is charged
(through its operations) and none is charged twice. The program is the machine's finite
control; instruction fetch is not a primitive operation of the cost model
and is not charged.

### 3.2 Program image

The program is a byte image with three instruction formats, fixed by opcode:

| Format | Layout (little-endian bit fields) | Bytes |
| --- | --- | --- |
| kernel | opcode 1..5 (8) / three 10-bit register fields | 5 |
| control | opcode 16..38 (8) / three 10-bit register fields / 24-bit immediate or branch byte offset | 8 |
| constant | opcode 64 (8) / register (10) / 256-bit value | 40 |

Ten-bit fields name all 1,024 registers. Every immediate of the 8-byte
format fits in 24 bits (the largest is 18,572) and every branch target is a
byte offset into the 253,197-byte image. Control code uses only the 8- and
40-byte formats, so instruction boundaries follow from the opcode byte. The
experiment encodes every program it runs, decodes the image, asserts the
round trip and the image size, and executes only the decoded program.

## M. The machine program

The complete program is emitted by `build_program` in
`experiments/bounded_machine.py` for any parameter set. At the full-width
parameters it consists of the 46,113-instruction kernel plus 2,761 control
instructions, uses 822 registers and 18,572 memory words.

### M.1 Kernel

The kernel computes planes of f(u) from planes of u in place in registers
0..255. A constant-folding Boolean DAG builder maps BLAKE3's modular
additions to ripple-carry full adders (at most five gates per bit; constants
fold), rotations to plane relabelings, and output constants to the stored
polarity PD; the DAG has 46,111 gates (37,898 XOR, 2,511 AND, 5,539 OR, 163
NOT; the experiment asserts this split). In-place register allocation in
creation order needs 776 registers and two output moves: 46,113 operations
per batch with no memory access. The experiment asserts these sizes and PD.

Correctness argument (H-kernel). (1) Every gate-construction rule (XOR with
constant folding and polarity, AND/OR selection with stored polarities and
shared complements, the pivot full adder, ripple-carry addition of words with
constant, inverted and polarity-flipped operands) is checked exhaustively on
all operand classes by the experiment: 6,191 cases, each over all input
assignments in bit-parallel form. (2) The word-level composition in
`build_listing` follows the BLAKE3 specification line for line (eight G calls
per round with rotations 16, 12, 8, 7, the message permutation, and the
feed-forward v[i] XOR v[i+8]), mirroring the scalar reference `digest_int`.
(3) A static check proves that the register-allocated listing computes the
DAG for every input: it tracks which DAG node each register holds and
verifies every operand reference and the final output placement. (4) Sampled
full-digest agreement with scalar BLAKE3 cross-checks the whole chain. Step
(2) is established by inspection, not mechanically; the claim is therefore
declared as the score-critical heuristic H-kernel.

### M.2 Main loop (per batch)

    LOOP:  KERNEL                         46,113
           OR D,P0,P1; OR D,D,Pj (j=2..111)  111
           BNE D,ONES,EPB                    2
    EPD:   BGE B,NEXTCUT,CUTB                2
    CUTD:  BEQ B,BMAX,FAIL6                  2
           ADDI B,B,1; JMP LOOP              2

Per batch: KLEN + d + 7 = 46,232 operations.

### M.3 Handlers

Endpoint batch (EPB): NOT ND,D; MOV LANE,0; then for each of the 256 lanes
SHR/AND/BEQ on ND (4) and ADDI/BNE (3); final JMP: 1,795 operations.

Key extraction per endpoint: MOV KEY,0 and, for each key bit j, SHR from plane
d+j by LANE, AND 1, SHLI j, OR into KEY: 1 + 4k = 189.

Table scan per non-matching entry: BEQ EIDX,CNT; SHRI, ADDI, LD, AND, SHLI, SHR
(slot word shifted into place), AND with the key mask into a scratch register;
BEQ against KEY; ADDI; JMP: 13. Insertion at count c: MOV EIDX (1), 13c,
terminating BEQ (2), capacity BEQ (2), slot value (identifier load 2, SHLI 47,
OR with KEY: 4), one read-modify-write of the slot word (SHRI, ADDI, LD, AND,
SHLI, SHL, OR, ST: 8), ADDI CNT, LDI RR, JMP (3): 20 + 13c. A terminal handler
costs at most 13U + 5 (capacity) or 13e + 12 ≤ 13U - 1 (match at entry e).

Restart: guard BEQ (2), two address/store pairs (4), ADD start, ADDI NID (2),
SHL/NOT lane mask (2), and per plane SHRI, AND, SHL, AND, OR (5 x 256 = 1,280),
then a return dispatch on RR: 1,292, 1,294 or 1,295 operations for returns to
setup, endpoint and cut.

Cut scan (CUTB): MOV, MOV (2); per lane ADDI, LD, SUB, BLT (5), BGE on the
running minimum (2), ADDI, BNE (3); final ADD, JMP (2): 2,564, plus at most
256 minimum updates (MOV) and, per cut, LDI RR, JMP and MOV after return (3)
plus one restart (1,295).

Recovery: stored identifier from the shifted slot word already in a register
(SHRI 47, AND: 2), current identifier and length (5), endpoint extraction
MOV + 4 x 256 (1,025), start and counter (2), post-reconstruction checks,
branch selection and alignment exits (12): 1,046 fixed. Each reconstruction step: 72 operations (including COMP's 64) and one
compression. Each alignment step: 69 operations and one compression. Each
non-final paired step: 138 operations and two compressions. Final paired
step and final check: 268 operations and four compressions. OUT and HALT: 3.

Setup: 13 LDI constants and RAND (14); memory clear MOV, LDI and 18,572 x (ST,
ADDI, BNE) (2 + 4 x 18,572); four MOV; 256 x (LDI RR, JMP, restart 1,292,
ADDI, BNE); ADDI B, MOV NEXTCUT: 406,342 operations in total.

### M.4 Storage layout

Memory words: table slots ceil(72,237/4) = 18,060; BIRTH 256; LID 256; total
18,572 words (594,304 bytes). Only entries below CNT are read. Register file:
1,024 x 32 = 32,768 bytes (822 registers used: 776 kernel, 46 control). Code:
46,113 x 5 kernel bytes plus 22,632 control bytes (2,761 instructions, of
which the 17 LDI instructions take 40 bytes), 253,197 bytes. COMP working state receives a 2,048-byte allowance.
Setup uses the same storage as the search.

### M.5 The fixed program image is the algorithm

The algorithm is the fixed image of Section 3.2. It is a deterministic,
uniform function of the public target and parameters, contains no search
results or other target-specific advice, and is counted in memory in full.
No program generation is performed during the charged computation: the
attack begins with the image loaded, as any algorithm begins with its code.
The generator in `experiments/bounded_machine.py` is provenance and
reproducibility tooling; the experiment regenerates the image and checks it,
but its own time and workspace are not part of the attack and are not claimed
to be bounded. Hence preprocessing_log2 = 0 and nonuniform_advice_log2_bytes = 0.

## L. Resource ledger

### L.1 Worst-case event counts

| Event | Bound | Reason |
| --- | --- | --- |
| batches | B = 269.75L + 2 | horizon |
| endpoint batches | U + 1 | each contains at least one handler; handlers ≤ U + 1 |
| insertions, endpoint restarts | U | capacity |
| cuts | floor(256B/R) = 2,938 | disjoint R-evaluation blocks |
| cut scans | 2,938 + U = 75,175 | a scan that cuts nothing requires an endpoint restart since the previous scan (otherwise NEXTCUT is exact and the minimum-birth lane is cut) |
| recovery | 1 | terminal |

### L.2 Word-operation terms (exact integers)

| Term | Operations |
| --- | --- |
| setup | 406,342 |
| main batches: B x 46,232 | 64,753,559,891,130,235,211,269,359,222,402,813,356,336 |
| endpoint-batch scans: 72,238 x 1,795 | 129,667,210 |
| key extraction: 72,238 x 189 | 13,652,982 |
| table scans and insertions: sum over c < U of (20 + 13c) | 33,919,172,298 |
| terminal handler: 13U + 5 | 939,086 |
| endpoint restarts: U x 1,294 | 93,474,678 |
| cut scans: 75,175 x (2,564 + 256) | 211,993,500 |
| cuts: 2,938 x (3 + 1,295) | 3,813,524 |
| recovery: 1,046 + 268 + 210R - 138 | 25,623,984,996,869,374,346,797,999,384,701,175,776 |
| output and halt | 3 |

The recovery term uses 72l1 + 69|l1 - l2| + 138(min(l1, l2) - 1), at most
210R - 138 for l1, l2 ≤ R. Compressions: H ≤ 3R + 2 =
366,056,928,526,705,347,811,399,991,210,016,782.

### L.3 Total time

    T = H + W/C,   W = sum of Section L.2,   C = 1470
    (C is the round-7 reference_operation_cost printed by the organizer's
    `pareto_candidate.py --family blake3 --rounds 7 --show-contract`)
    log2 T = 125.062988236942        claim time_log2 = 125.06299

The main loop is 99.137 percent of T (log2 125.050483); the kernel alone is
log2 125.046765. Recovery compressions are 2^118.140 units. Handler, table,
cut and setup terms together are below 2^-80 of T. The bound holds for every
function and every rho, including failed attempts; there is one attempt and
no amplification.

### L.4 Memory

    code 253,197 + register file 32,768 + memory words 594,304
      + COMP state 2,048 = 882,317 bytes
    log2 = 19.750938        claim memory_log2_bytes = 19.75094

Memory includes code, the whole register file (including rho, constants,
output points and recovery state), the table, lane metadata and the COMP
working state. There is no advice or precomputed data. Memory is below 2^20
bytes, so it adds nothing to the normalized score.

### L.5 Established counts versus assumptions

Established by the program text and asserted by the declared experiment
(the organizer's isolated executor runs it; a failed assertion fails the
experiment): the kernel size, gate split, register count (822 of 1,024) and
its static correctness proof with respect to the DAG; the per-handler closed
forms, measured at the full-width parameter set under test functions (setup,
batch, endpoint scans at table counts 0..3, insertion, a cut scan with 256
cuts, a cut scan with one minimum update, the capacity terminal, a match at
entry 0, and recovery for four length pairs) and asserted equal; the image
round trip and size; outcome-level equivalence of the program and the scalar
reference at reduced width. Established mathematically: the event bounds of
L.1 and the arithmetic of L.2-L.4 (reproduced by the administrative ledger
calculator). Assumed: the declared register file
(Section 3.1); the specification-following composition of the kernel
(H-kernel); the premise H1. The probability argument of Section P is a
theorem in the random-function model, reviewed by its authors.

### L.6 Sensitivity to the register file

The same algorithm with smaller files needs spill loads and stores in the
kernel (measured with a furthest-next-use allocator in creation order; for
32 registers this is the fully implemented and submitted entry 56b4da71):

| Registers | Kernel operations per batch | time_log2 |
| --- | --- | --- |
| 32 | 77,020 | 125.79656 (the fully implemented 32-register program is submission 56b4da71 with C1's parameters, 125.92167) |
| 64 | 70,338 | 125.66656 |
| 128 | 60,692 | 125.45545 |
| 256 | 54,908 | 125.31225 |
| 1,024 (this entry) | 46,113 | 125.06299 |

The values for 32-256 registers are derived from the measured kernel sizes
with this entry's parameters and are not separately implemented. Other
sensitivities: instruction fetch, if charged at one load per 32 bytes of
kernel code, adds 7,206 operations per batch (125.27029); at 36 bytes per
instruction memory would be 2,388,584 bytes = 2^21.19, adding 1.19 to the
normalized score. Section H gives the time cost of absorbing a fixed-target
probability deficit.

## P. Success probability in the random-function model

**Model.** F is a uniformly random function on 256-bit strings and rho is
uniform and independent of F (the bound in fact holds for every fixed rho).
The bound below is a theorem in this model; its application to the fixed
target is the heuristic H1 (Section H). It assumes that the main-loop kernel
computes F exactly (H-kernel).

**First-duplicate coupling.** Freeze each batch's inputs and reveal answers in
ascending lane order, applying endpoint handlers virtually in that order;
deferring cut handling to the end of the batch gives the same next-batch
inputs. Before the first duplicate output or the first output inside the
reserved start set S = {rho + t : t < 131,072}, every query input is fresh: a
continuing lane's input is its own previous unique output, and a restarted
lane uses a new reserved start. Couple the answers to independent uniform
lottery values for the first Q0 = 256 B0 = 66,048 x 2^112 slots (B0 = 258L).
With lambda = Q0(Q0 - 1)/2^257 = 0.507843 (rounded down), a duplicate among
them occurs with probability at least 1 - exp(-lambda) ≥ lambda - lambda^2/2
+ lambda^3/6 - lambda^4/24 > 0.397948473710.

**Excluded events (union bounds, not independence).** Write i < j for the
first duplicate pair.

| Event | Bound | Upper value |
| --- | --- | --- |
| first duplicate on one physical lane | 256 choose(B0, 2)/2^256 | 0.001983761788 |
| some trail cut before the first duplicate | A(1 - 1/L)^R ≤ A e^(-R/L), A = 75,432 | 0.000004694997 |
| either relevant trail older than h + 1 at the duplicate | 4 lambda e^(-h/L) = 4 lambda e^(-11.75) | 0.000016026155 |
| earlier trail's exposed suffix or stored endpoint farther than m = 47L/8 | 2 lambda e^(-m/L) = 2 lambda e^(-5.875) | 0.002852853040 |
| fresh suffix of m answers with no endpoint | e^(-5.875) | 0.002808794195 |
| fresh suffix meets an exposed point, start or pending input | m(Q + 131,072 + 256 + m)/2^256 | 0.000094468360 |
| some fresh answer lies in S | Q x 131,072/2^256 | 1e-12 |
| false 47-bit key match | Q U/(L 2^47) | 0.000035444702 |
| more than U endpoints (Binomial(Q, 1/L) tail, (U - mu)^2/(2U) ≥ 70 with mu = 69,056) | 2^-100 | 1e-12 |
| sum of losses | | 0.007796043234 |

Values are exact rationals rounded upward at the twelfth decimal; the birthday
term is rounded downward. Each e^(-x) is bounded above by the reciprocal of a
positive Taylor partial sum of e^x. The suffix-intersection term
conservatively uses the total query count Q for the forbidden set, although
the exposure is made at the first duplicate, when at most Q0 points are
exposed. The resulting lower bound is 0.390152430477 (rounded downward),
a margin of 0.000152 above 0.39. The parameters were chosen by exact rational
optimization of this bound (an administrative script scanning L, m/L, k, the
identifier width and B0 under the 2^20-byte memory ceiling); the C1
parameters (L = 2^113, m = 5L, U = 40,000, 64-bit key, B0 = 136L) gave
0.413939 at a horizon 2^0.12 longer.

Derivation of the pairwise bounds. Fix a pair of slots i < j with lanes a
(earlier) and b (later), and let theta = 1/L. Each age or known-suffix event
is contained in the event "X_i = X_j and every slot of a fixed block is
non-distinguished", where the block is determined by (i, j) and the lane
geometry alone, not by the random values: an age above h + 1 for the later
trail means no restart in the h + 1 lane-b slots preceding j, hence no
distinguished output in the h lane-b slots of the h batches before j's batch;
an age above h + 1 for the still-active earlier trail means the same for the
h lane-a slots preceding lane a's last processed slot before j; a known
suffix or finished endpoint farther than m from X_i means the m lane-a slots
following i are non-distinguished. None of these blocks contains slot j. A
block may contain slot i, whose value is identified with X_j by the
conditioning; dropping that one slot leaves at least h - 1 (respectively
m - 1) lottery variables independent of (X_i, X_j), each non-distinguished
with probability 1 - theta. Hence each pair contributes at most
N^-1 (1 - theta)^(h - 1), N^-1 (1 - theta)^(h - 1) and N^-1 (1 - theta)^(m - 1)
to the three events. Summing over all choose(Q0, 2) pairs gives
lambda (1 - theta)^(h - 1) per age event and lambda (1 - theta)^(m - 1) for
the known suffix, since choose(Q0, 2)/N = lambda. Using (1 - theta)^(n - 1)
≤ e^(-n theta) e^theta and e^theta < 2 gives the displayed constants: 2 x 2
lambda e^(-h/L) for the two age events together and 2 lambda e^(-m/L) for the
known suffix. Blocks that would extend before the first slot make the event
impossible. The fresh
suffix uses a stopped exposure: the earlier trail's frontier at j is
unqueried (otherwise there was an earlier duplicate or start hit), and its
next m answers are revealed until an endpoint or an intersection with the
forbidden set; the joint event "m non-distinguished answers and no
intersection" has probability at most (1 - 1/L)^m by induction on surviving
prefixes, and intersections are bounded separately. No geometric law for a
collision-selected trail and no independence between merged trails is used.

**Completion.** Outside these events both relevant trails are at most h + 1 old
at the duplicate; the later trail reaches the common endpoint within 2m = h
further steps and the earlier active trail within m. Their ages before
endpoint handling are at most 2h + 2 < R, so neither is cut first, and both
endpoint handlers run by batch B0 + h + 2 = B. Other lanes cannot change this
path's values; any earlier stop is a true endpoint match (recovery succeeds
outside the start event, Section 2.4), a false key or a capacity stop, each
bounded above. The exact rational difference of the birthday bound and the
nine losses exceeds 0.390152 > 0.39.

### P.1 Review against the implemented program

The argument was re-checked against the decoded machine program, item by item.
No counterexample or missing event was found; the following points were
implicit in the earlier text and are made explicit here.

1. *Serialization.* The program computes all 256 outputs of a batch before
   any handler, then runs endpoint handlers in ascending lane order, then the
   age-cap scan. Handlers change only next-batch inputs, and a lane's key and
   endpoint are read before that lane is restarted, so revealing answers in
   lane order with virtual handlers yields the same executions.
2. *Freshness.* Before the first duplicate or start hit, a continuing lane's
   input is its own previous output and a restarted lane's input is a start
   with an unused identifier (starts are distinct because 75,431 < 2^256);
   an earlier query of either value would itself be a duplicate or a start
   hit. This holds within a batch as well.
3. *The age cap is exact.* NEXTCUT never exceeds min BIRTH + R, so every lane
   whose age reaches R is cut in that batch, exactly as the analysis assumes.
   Conversely no lane is cut earlier, and an endpoint at age exactly R is
   handled as an endpoint.
4. *Table semantics.* Keys in the table are unique (insertion only after an
   unsuccessful scan) and entries are never evicted. A true endpoint E can
   therefore be pre-empted by a different endpoint with the same key only if
   that endpoint's key was inserted first, in which case E's first arrival
   was already a false-key stop, which is counted. A repeated answer that is
   distinguished reproduces an endpoint whose key is already stored, giving a
   true match rather than a false one.
5. *Recovery of any true match.* For stored and current trails with the same
   first endpoint and lengths l1, l2 ≤ R (an endpoint at age R is handled
   before the cap), the aligned states are equal only if one start equals a
   positive iterate of the other start. That iterate was computed during the
   main search, so this is a main-search output in the start set, which is
   counted. Otherwise the paired walk meets at distinct inputs within
   min(l1, l2) steps. Recovery revisits only values already computed and
   creates no new fresh answers.
6. *Completion bookkeeping.* With both relevant ages at most h + 1 at the
   first duplicate and the common endpoint at most 2m = h further steps from
   the later occurrence, both trails reach it at age at most 2h + 2 < R and
   by batch B0 + h + 2 = B; the earlier trail, being ahead on the same path,
   reaches it first or in the same batch, where ascending lane order inserts
   before matching.
7. *Counted quantities match the program.* Q = 256B, the identifier bound
   75,431 < IDL = 131,072 (so the identifier guard never fires), the start
   set of 131,072 values, U = 72,237 and 47 key bits (bits 112..158) disjoint
   from the 112 distinguished bits are the program's values. The identifier
   field of a table slot holds 17 bits, enough for every identifier below IDL.

The arithmetic is reproduced exactly by administrative checkers using rational
arithmetic. The event
cover has been reviewed by its authors only; it has not been independently
validated. A valid random-function bound does not imply a bound for every
function (for a permutation the algorithm never succeeds), which is why the
transfer to the fixed target is declared as H1.

## H. Fixed-target heuristic H1 and its evidence

**Statement.** For the fixed walk f(u) = LE256(BLAKE3_r7(M(u))) XOR PD, the
success probability of this algorithm over a uniform rho is at least the
random-function bound of Section P, hence at least 0.39.

**Why the random-function model is the relevant model.** Seven rounds is the
full round count of BLAKE3, so the target is the complete, unreduced hash
applied to single-block messages. The algorithm is generic: it uses no
property of BLAKE3 beyond evaluating it. The proof uses only that answers to
fresh queries along the search are uniform and independent of the history,
which is the standard model for generic collision search against an unbroken
256-bit hash. The parameters are tuned so that the random-function bound is
0.390152, only 0.000152 above the required 0.39: any fixed-target deficit
larger than that would defeat the claim. A deficit of that size would be a
structural property of full BLAKE3 visible to this generic procedure (a
systematic shortfall of collisions or of distinguished points along walks);
we know of no such property, but this is an argument from the design and
public analysis of BLAKE3, not a proof. Sensitivity: absorbing a deficit eps
in the fixed-target success probability by lengthening the horizon costs
0.0020 bits for eps = 0.001, 0.0224 bits for eps = 0.01 and 0.1102 bits for
eps = 0.05 (same tuning method; the last point uses a 77,888-entry table and
928,181 bytes).

**Experiments with an exact prediction.** Two declared experiments test the
mechanism that carries the bound (the first duplicate among lane-serialized
fresh queries from consecutive starts) on the fixed target itself. For each
organizer trial a separate slice g(u) = f(c | u) mod 2^n is taken, with c a
seed-derived point whose low n bits are cleared, so different trials probe
different parts of the fixed function. 256 lane walks start at 256
consecutive slice values and are evaluated by the same bitsliced kernel,
serialized in batch and lane order exactly as in the search. For a uniformly
random g every query before the first event is fresh, so the first-event law
is exact: P(collision first at slot i) = (i/N) prod_{k<i}(1 - (k + 256)/N).
A trial returns the colliding messages only when the first event is a
collision; the organizer verifies every returned pair on the low n digest bits.

| Experiment | n | slots | P(pair) | expected of 256 | 99 percent interval |
| --- | --- | --- | --- | --- | --- |
| blake3-r7-slice-first-collision-w20-v1 | 20 | 1,280 | 0.448648 | 114.85 | 94-136 |
| blake3-r7-slice-first-collision-w24-v1 | 24 | 3,072 | 0.237789 | 60.87 | 43-79 |

The predictions are fixed before execution, from exact rational arithmetic.
Decision rule: a returned-pair count outside either interval counts as
evidence against H1; with two tests the family-wise false-alarm probability
under the model is about 1.3 percent. The organizer verifies every returned
pair; the resulting counts are part of the organizer's experiment report.
Power is limited: with 256 trials the intervals detect shifts of roughly
0.07-0.08 in the pair probability. The deficit that would matter at full
width is 0.000152 (Section P); no feasible experiment of this kind can detect
a deficit of that size. A pass therefore shows the absence of gross
non-randomness in this mechanism, not a measured full-width probability. A
failure would not distinguish kernel errors from non-randomness, but the
kernel is checked separately (Section M.1).

**Scope and limitations.** These experiments test uniformity and freshness
of the fixed target along lane-serialized walks from consecutive starts, with
the search's lane serialization and consecutive-start structure but with the
high input bits fixed by a seed constant (the search's inputs are full
256-bit values), at widths 20 and 24 on 512 slices. They
do not test the 2^128-query regime, the full-width distinguished-point and
key events, or the full function rather than its slices, and they cannot
exclude a property that appears only at full scale. The loss terms of
Section P that involve distinguished points are each below 0.008 under the
model; the margin above 0.39 is 0.000152. H1 is therefore plausible rather
than established.

## 8. Evidence

Three declared experiments run `experiments/bounded_machine.py` in the
organizer's isolated executor.

`blake3-r7-bounded-machine-w14-v2` (implementation) in one execution:

1. regenerates the kernel and asserts 46,113 instructions, 776 kernel
   registers, the gate split and PD, and that all 822 statically named
   registers fit the declared 1,024-register file; proves statically that the
   register-allocated listing computes the gate DAG;
   checks all 6,191 gate-rule cases exhaustively (the reported
   `fixtures_passed` counts these plus the ten fixtures, 6,201); serializes
   every program it runs into its image, decodes it, asserts the round trip
   and the image size, and executes only decoded code;
2. runs ten deterministic fixtures through both the complete machine program
   (with the kernel and COMP replaced lane-wise by small test functions) and
   the scalar reference: direct merge, false short key, start overlap, empty
   capacity, endpoint exactly at the age cap, repeated cuts without a global
   halt, same-batch capacity ordering, identifier exhaustion, a later-lane
   match within one batch, and alignment over unequal lengths; all outcome
   fields must agree and each expected termination code must occur;
3. builds the full-width program and measures, under test functions, the setup
   cost, the per-batch cost, endpoint handlers at table counts 0..3, a cut scan
   with 256 cuts, a cut scan with one minimum update, the capacity terminal,
   a match at entry 0 and recovery for four (l1, l2) shapes; every measurement
   must equal the closed form of Section M.3;
4. for each of 256 organizer trials, runs a 14-bit projected search
   (d = 4, k = 9, U = 256, R = 2, B = 48, IDL = 4,096) on the real target with
   the real kernel, compares it with the scalar reference on termination
   code, returned pair, insertions, cuts, starts, batches and compressions,
   compares four kernel lanes per batch with scalar BLAKE3 on all 256 output
   bits, and checks eight lanes of one full-width random batch the same way.

The 14-bit projection zeroes planes 14..255 after the kernel and masks scalar
values; these diagnostic-only operations exist only in the reduced program.
Its success frequency is control-flow coverage, not a probability estimate.

`blake3-r7-slice-first-collision-w20-v1` and `-w24-v1` (H1 evidence) are
described in Section H; they use the kernel decoded from the full-width image.

Not established by any experiment: kernel correctness on all 2^256 inputs (the
construction argument plus sampled agreement), the full-width success
probability, or independence beyond the stated exact-law model.

## 9. Heuristics and limitations

**H1** (score-critical, plausible): Section H.

**H-machine** (score-critical): Section 3. The time bound depends on the
declared 1,024-register file; Section L.6 gives 125.79656 for 32 registers
with this entry's parameters.

**H-kernel** (score-critical for the success probability): the generated
listing computes f on every input. Support: Section M.1 (exhaustive rule
checks, static allocation proof, specification-following composition and
sampled agreement). A kernel error could only produce missed or false
endpoints; recovery rejects false outputs explicitly, but such an error would
invalidate the probability argument.

Other limitations: the probability argument has been reviewed by its authors
only; no complete collision is produced; parameters were taken from the
probability analysis without joint optimization.

## 10. Provenance and credits

The search is the van Oorschot-Wiener parallel collision search with
distinguished points (Journal of Cryptology 12(1), 1999). Material sources
among published HashSmash submissions, declared as dependencies:

- 6ae36351-5836-4a46-ad34-227688264123 (jungjipdo): the pivot full adder and
  the polarity mask walk f = D XOR PD; distinguished planes followed by a
  64-bit key window; recovery by scalar compressions.
- 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c and e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca
  (Jbenisek): the 256-lane bitsliced BLAKE3 kernel approach for the message
  family 0^32 || x and the declared register-file convention counted in
  memory (also used by 6ae36351).
- 616120b2-f777-44a8-bbd2-44f20c56224a (ours, C1): the same algorithm,
  machine declaration, proof structure and experiments; this entry changes
  the search parameters and the table layout only.
- 56b4da71-4cec-46a8-b98b-4b28047cdf05 (ours): the same algorithm on a
  32-register load/store machine with explicit spill code.
- a2e94df7-bff4-4461-ad40-7f75930cb241 (Jbenisek): lane-indexed lazy exposure
  and explicit treatment of adaptive histories in the probability argument.

All code in this package was written independently; no competitor file was
copied or executed. A historical prefix f17f7355 named by an earlier internal
draft could not be resolved to a published submission and is not declared.
