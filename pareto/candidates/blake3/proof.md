# BLAKE3 round 7: bounded-restart bitsliced search (exploratory)

This package claims an ordinary 256-bit collision construction for the
complete seven-round BLAKE3 hash (the full BLAKE3 round count) with total time
2^125.18367 target compressions, memory 2^19.41421 bytes and success
probability at least 0.39. One algorithm is frozen (Section 2), implemented as
a serialized machine image (Sections 3 and M) and accounted worst-case from
that image (Section L). The success bound is a random-function theorem
(Section P) transferred to the fixed target by the declared heuristic H1,
supported by exact-law experiments on 512 independent slices of the target
(Section H). No complete collision is exhibited; the attack is not executed at
full scale.

| Quantity | Value | Basis |
| --- | --- | --- |
| rounds | 7 | target profile `blake3-r7-prefix-v1` |
| time_log2 | 125.18367 | Section L; exact log2 T = 125.183664494825, rounded up |
| memory_log2_bytes | 19.41421 | Section L; 698,645 bytes |
| normalizedTimeMemoryLog2 | 125.18367 | memory below 2^20 adds zero |
| success_probability | 0.39 | Section P (random-function bound above 0.41393) and H1 |
| preprocessing_log2 | 0 | the fixed program image is the algorithm (Section M.5) |
| nonuniform_advice_log2_bytes | 0 | uniform program; no stored search results |

Declared heuristics: H1 (fixed-target transfer, score-critical), H-machine
(word-RAM and encoding convention, score-critical) and H-kernel (all-input
kernel correctness, score-critical for the success probability). Section L.6 states which conventions the
comparison with other published entries depends on.

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
| d | 113 | distinguished: bits 0..112 of f(u) are zero; L = 2^113 |
| k | 64 | endpoint key: bits 113..176 of f(u) |
| B | 146L + 2 | batch horizon (B0 = 136L analysis batches, h = 10L, 2 guard batches) |
| R | 20L + 4 | per-trail age cap (2h + 4) |
| U | 40,000 | table capacity, never evicted |
| IDL | 65,536 | identifier limit; start t is rho + t mod 2^256 |
| rho | one uniform 256-bit word | the only randomness |

Derived deterministic ceilings (all executions, all functions): Q = 256B lane
evaluations; at most floor(Q/R) = 1,868 cuts (each cut lane has used R
evaluations since its own restart, disjoint from other cuts); at most U
insertions; at most U + 1 endpoint handlers (every non-terminal handler
inserts); at most 256 + U + 1,868 = 42,124 < IDL allocated identifiers, so the
identifier guard cannot fire before another stop.

### 2.2 State

Lane l holds its current point (bit j in plane register P_j, lane bit l),
identifier LID[l] and birth batch BIRTH[l]. Global state: batch counter b,
next identifier NID, table count CNT, the earliest-cut batch NEXTCUT, rho and
the table: key word array KEY (four 64-bit keys per 256-bit word) and
identifier array ID (sixteen 16-bit identifiers per word). Entry e occupies
key slot e mod 4 of word floor(e/4) and identifier slot e mod 16 of word
floor(e/16).

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
  per-lane age cap R, B = 146L + 2) replaces the historical
  "third cut halts" search with B = 2^119.9994 and H = 111.
- Distinguished predicate and key: low 113 bits of f, then bits 113..176;
  replaces the historical "last output word" predicate and 48/56-bit keys.
- Table layout: packed 64-bit keys and 16-bit identifiers, capacity 40,000;
  replaces the 9- and 24-byte entry variants and the identifier width that
  could not represent the required identifiers.
- Lengths: not stored; recovery reconstructs the stored trail (≤ R steps).
- Recovery evaluates f with the scalar target compression, not with the
  bitsliced kernel, and checks complete digests explicitly.
- PD: the integer of Section 1 (the label in the historical appendix was wrong).
- Randomness: one RAND word; seed expansion appears only in the diagnostic.
- The historical figures 124.97996, 0.3900000143, 84,750 entries and
  1,029,908 bytes are not used.

## 3. Machine model and declared convention (H-machine)

### 3.1 Word RAM with direct addressing

The program runs on the cost model's classical 256-bit word RAM. Its first 823
memory words are addressed directly by instruction operand fields; in the
classical RAM of Cook and Reckhow (1973) every instruction names its operand
cells directly and costs one step, and that is the convention used here. These
cells are called registers below only for brevity: they are ordinary memory
words, all 823 are counted in memory at 32 bytes each, and no separate
register file is assumed free. The remaining 13,012 data words (table and lane
metadata) are reached by indirect addressing (LD/ST through an address held in
a directly addressed word); each such access is charged one load or store.
Each instruction below is one primitive operation of `collision-frontier-v5`,
charged 1/C with C = 1470, except as noted:

| Instruction | Semantics | Charge |
| --- | --- | --- |
| XOR, AND, OR d,a,b; NOT, MOV d,a | bitwise on words (MOV = OR a,a) | 1 |
| ADD, SUB d,a,b; ADDI d,a,imm | modulo 2^256 | 1 |
| SHL, SHR d,a,b; SHLI, SHRI d,a,imm | shift by word value or immediate | 1 |
| LDI d,imm | load a 256-bit constant | 1 |
| LD d,a; ST a,s | indirect load/store at the address held in word a | 1 |
| BEQ, BNE, BLT, BGE a,b,target | unsigned comparison plus conditional branch | 2 |
| JMP target | unconditional branch | 1 |
| RAND d | independent uniform 256-bit word | 1 |
| COMP d,a | complete 7-round BLAKE3 digest of M(a) (one root compression) | 1 compression unit |
| OUT a,b | store the two output points | 2 |
| HALT n | stop with code n | 1 |

COMP takes the point word directly; the block layout, counter and flags of
M(a) are fixed, so it is exactly one target compression. A stricter charge of
64 word operations per COMP for block assembly changes log2 T by less than
0.001 (Section L.6).

### 3.2 Program image

The program is a byte image with three instruction formats, fixed by opcode:

| Format | Layout (little-endian bit fields) | Bytes |
| --- | --- | --- |
| kernel | opcode 1..5 (8) / d (10) / a (10) / b (10) | 5 |
| control | opcode 16..38 (8) / three 10-bit word fields / 24-bit immediate or branch byte offset | 8 |
| constant | opcode 64 (8) / d (10) / 256-bit value | 40 |

Ten-bit fields address all 823 directly addressed words; 24-bit fields hold
every immediate used (at most 13,012) and every branch target as a byte offset
into the 253,877-byte image. Control code uses only the 8- and 40-byte formats,
so instruction boundaries are determined by the opcode byte. The experiment
encodes every program it runs, decodes the image, asserts that the decoded
program and kernel equal the generated ones and that the image length equals
the ledger's code size, and then executes only the decoded program. The
full-width image has SHA-256
`22c2838aff244eeb07ac1af323543a801ae5c8d3c34f444b4dabe3b90e3cfd99`.


## M. The machine program

The complete program is emitted by `build_program` in
`experiments/bounded_machine.py` for any parameter set. At the full-width
parameters it consists of the 46,113-instruction kernel plus 2,842 control
instructions, 823 registers (776 kernel registers, 47 control registers) and
13,012 data words.

### M.1 Kernel

The kernel is a straight-line register program computing planes of f(u) from
planes of u in place in registers 0..255. It is generated by a constant-folding
Boolean DAG builder: BLAKE3's modular additions become ripple-carry full adders
(at most five gates per bit; constants fold), rotations are plane relabelings,
and output constants are absorbed into the stored polarity PD. The generator
emits 46,111 Boolean instructions (37,898 XOR, 2,511 AND, 5,539 OR, 163 NOT, as
reported by the original generator) and two output MOV instructions after
in-place register allocation, using 776 registers. The experiment asserts the
46,113 total, the 776 registers and PD on every run.

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
DAG for every input: it tracks which DAG node each word holds and verifies
every operand reference and the final output placement. (4) Sampled
full-digest agreement with scalar BLAKE3 cross-checks the whole chain.
Step (2) is established by inspection, not mechanically; the claim is
therefore declared as the score-critical heuristic H-kernel.

### M.2 Main loop (per batch)

    LOOP:  KERNEL                         46,113
           OR D,P0,P1; OR D,D,Pj (j=2..112)  112
           BNE D,ONES,EPB                    2
    EPD:   BGE B,NEXTCUT,CUTB                2
    CUTD:  BEQ B,BMAX,FAIL6                  2
           ADDI B,B,1; JMP LOOP              2

Per batch: KLEN + d + 7 = 46,233 operations.

### M.3 Handlers

Endpoint batch (EPB): NOT ND,D; MOV LANE,0; then for each of the 256 lanes
SHR/AND/BEQ on ND (4) and ADDI/BNE (3); final JMP: 1,795 operations.

Key extraction per endpoint: MOV KEY,0 and, for each key bit j, SHR from plane
d+j by LANE, AND 1, SHLI j, OR into KEY: 1 + 4k = 257.

Table scan per non-matching entry: BEQ EIDX,CNT; SHRI, ADDI, LD, AND, SHLI, SHR,
AND (key slot); BEQ against KEY; ADDI; JMP: 13. Insertion at count c: MOV EIDX
(1), 13c, terminating BEQ (2), capacity BEQ (2), key read-modify-write (8),
identifier load (2), identifier read-modify-write (8), ADDI CNT, LDI RR, JMP
(3): 26 + 13c. A terminal handler costs at most 13U + 5 (capacity) or
13e + 12 ≤ 13U - 1 (match at entry e).

Restart: guard BEQ (2), two address/store pairs (4), ADD start, ADDI NID (2),
SHL/NOT lane mask (2), and per plane SHRI, AND, SHL, AND, OR (5 x 256 = 1,280),
then a return dispatch on RR: 1,292, 1,294 or 1,295 operations for returns to
setup, endpoint and cut.

Cut scan (CUTB): MOV, MOV (2); per lane ADDI, LD, SUB, BLT (5), BGE on the
running minimum (2), ADDI, BNE (3); final ADD, JMP (2): 2,564, plus at most
256 minimum updates (MOV) and, per cut, LDI RR, JMP and MOV after return (3)
plus one restart (1,295).

Recovery: identifier field extraction (7), current identifier and length (5),
endpoint extraction MOV + 4 x 256 (1,025), start and counter (2): 1,039. Each
reconstruction step: BEQ guard, COMP, XOR PD, ADDI, MOV, AND, BNE: 8 operations
and one compression. Post-reconstruction checks and branch selection: 12.
Each alignment step: BEQ, COMP, XOR, SUB, JMP: 5 operations and one
compression. Each non-final paired step: BEQ, COMP, XOR, COMP, XOR, BEQ, MOV,
MOV, SUB, JMP: 10 operations and two compressions. Final paired step and final
check: 12 operations and four compressions. OUT and HALT: 3.

Setup: 14 LDI constants and RAND (15); memory clear MOV, LDI and 13,012 x (ST,
ADDI, BNE) (2 + 4 x 13,012); four MOV; 256 x (LDI RR, JMP, restart 1,292,
ADDI, BNE); ADDI B, MOV NEXTCUT: 384,103 operations in total.

### M.4 Storage layout

Data words: KEY 10,000; ID 2,500; BIRTH 256; LID 256; total 13,012 words
(416,384 bytes). Only entries below CNT are read. Registers: 776 kernel and 47
control registers (constants, counters, rho, recovery state), 26,336 bytes.
Code: 46,113 x 5 kernel bytes plus 23,312 control bytes (2,842 instructions,
of which the 18 LDI instructions take 40 bytes), 253,877 bytes. COMP working
state (message block, 16-word compression state and scratch) receives a
2,048-byte allowance. Setup uses the same storage as the search; there is no
separate setup phase layout.

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
| batches | B = 146L + 2 | horizon |
| endpoint batches | U + 1 | each contains at least one handler; handlers ≤ U + 1 |
| insertions, endpoint restarts | U | capacity |
| cuts | floor(256B/R) = 1,868 | disjoint R-evaluation blocks |
| cut scans | 1,868 + U = 41,868 | a scan that cuts nothing requires an endpoint restart since the previous scan (otherwise NEXTCUT is exact and the minimum-birth lane is cut) |
| recovery | 1 | terminal |

### L.2 Word-operation terms (exact integers)

| Term | Operations |
| --- | --- |
| setup | 384,103 |
| main batches: B x 46,233 | 70,096,194,512,907,080,238,956,327,542,339,148,015,922 |
| endpoint-batch scans: 40,001 x 1,795 | 71,801,795 |
| key extraction: 40,001 x 257 | 10,280,257 |
| table scans and insertions: sum over c < U of (26 + 13c) | 10,400,780,000 |
| terminal handler: 13U + 5 | 520,005 |
| endpoint restarts: U x 1,294 | 51,760,000 |
| cut scans: 41,868 x (2,564 + 256) | 118,067,760 |
| cuts: 1,868 x (3 + 1,295) | 2,424,664 |
| recovery: 1,051 + 12 + 18R - 10 | 3,738,453,738,145,075,892,541,957,357,038,470,245 |
| output and halt | 3 |

The recovery operation term uses 8l1 + 5|l1 - l2| + 10(min(l1, l2) - 1) =
13 max + 5 min - 10 when l1 ≥ l2 and the symmetric form otherwise, at most
18R - 10 for l1, l2 ≤ R. Compressions: H ≤ 3R + 2 =
623,075,623,024,179,315,423,659,559,506,411,534.

### L.3 Total time

    T = H + W/C,   W = sum of Section L.2,   C = 1470
    log2 T = 125.183664494825        claim time_log2 = 125.18367

The main loop is 98.705 percent of T (log2 125.164859); the kernel alone is
log2 125.161110. Recovery compressions are 2^118.907 units. Handler, table,
cut and setup terms together are below 2^-80 of T. The time bound holds for
every function and every rho, including failed attempts; there is one attempt
and no amplification.

### L.4 Memory

    code 253,877 + words 26,336 + data 416,384 + COMP state 2,048 = 698,645 bytes
    log2 = 19.414200        claim memory_log2_bytes = 19.41421

Memory includes code, the directly addressed words (including rho, constants,
output points and recovery state), the table, lane metadata and the COMP
working state. There is no advice or precomputed data.

### L.5 Established counts versus assumptions

Established by the program text and asserted by the declared experiment
(the organizer's isolated executor runs it; a failed assertion fails the
experiment): the kernel count and register count; every per-handler formula
above, measured at the full-width parameter set under test functions and
asserted equal to the closed forms; the image round trip and size;
transition-level equivalence of the program and the scalar reference at
reduced width. Established mathematically: the event bounds of
L.1 and the arithmetic of L.2-L.4, reproduced by the administrative ledger
calculator. Assumed: the H-machine convention (Section 3); the specification-following
composition of the kernel (H-kernel, Section M.1); the premise H1. The
probability argument of Section P is a theorem in the random-function model,
reviewed by its authors.

### L.6 Sensitivity

- Encoding: at 36 bytes per instruction (a convention used by other
  published entries, for example a2e94df7), code is 1,762,380 bytes and
  memory 2,207,148 bytes = 2^21.07376; the normalized score becomes 126.25743. This is worse than
  the published reference value 125.29113, so the improvement depends on the
  declared compact encoding.
- Register operands: if every kernel instruction were charged two operand
  loads and one result store in addition to the operation (four operations),
  the time bound would be 2^127.16679. This convention-free fallback is still
  below the nominal 128; only the comparison with other published entries
  depends on the direct-addressing part of H-machine.
- COMP block assembly: charging even 64 word operations per recovery
  compression changes log2 T by less than 0.001.
- Parameters were taken unchanged from the proposed probability argument; a
  joint re-optimization of L, U and the completion allowance was not attempted.

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
reserved start set S = {rho + t : t < 65,536}, every query input is fresh: a
continuing lane's input is its own previous unique output, and a restarted
lane uses a new reserved start. Couple the answers to independent uniform
lottery values for the first Q0 = 17 x 2^124 = 256 B0 slots. With
lambda = Q0(Q0 - 1)/2^257, a duplicate among them occurs with probability at
least 1 - exp(-lambda) ≥ lambda - lambda^2/2 + lambda^3/6 - lambda^4/24 >
0.4308930007.

**Excluded events (union bounds, not independence).** Write i < j for the
first duplicate pair.

| Event | Bound | Upper value |
| --- | --- | --- |
| first duplicate on one physical lane | 256 choose(B0, 2)/2^256 | 0.002204895020 |
| some trail cut before the first duplicate | A(1 - 1/L)^R ≤ A/480,000,000, A = 42,125 | 0.000087760417 |
| either relevant trail older than h + 1 at the duplicate | 4 lambda e^-10 ≤ 4 lambda/22,000 | 0.000102627841 |
| earlier trail's exposed suffix or stored endpoint farther than m = 5L | 2 lambda e^-5 ≤ 2 lambda/148 | 0.007627744933 |
| fresh suffix of m answers with no endpoint | e^-5 ≤ 1/148 | 0.006756756757 |
| fresh suffix meets an exposed point, start or pending input | m(Q + 65,536 + 256 + m)/2^256 | 0.000174068846 |
| some fresh answer lies in S | Q x 65,536/2^256 | 1e-12 |
| false 64-bit key match | Q U/(L 2^64) | 8.2e-11 |
| more than U endpoints (Binomial(Q, 1/L) tail) | 2^-100 | 1e-12 |
| sum of losses | | 0.016953853894 |

Values are exact rationals rounded upward at the twelfth decimal; the birthday
term is rounded downward (0.430893000757). The suffix-intersection term
conservatively uses the total query count Q for the forbidden set, although
the exposure is made at the first duplicate, when at most Q0 points are
exposed. The resulting lower bound is 0.413939146864 (rounded downward).

Each age or suffix event contains a fixed block of h, h or m slot values with
no distinguished output; conditioning on X_i = X_j removes at most one degree
of freedom, giving the pairwise bounds summed over all pairs. The fresh
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
nine losses exceeds 0.41393 > 0.39.

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
   with an unused identifier (starts are distinct because 42,124 < 2^256);
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
   42,124 < IDL = 65,536 (so the identifier guard never fires), the start set
   of 65,536 values, U = 40,000 and 64 key bits disjoint from the 113
   distinguished bits are the program's values.

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
256-bit hash. A fixed-target deficit large enough to lower the success
probability from above 0.4139 to below 0.39 would be a structural property of
full BLAKE3 visible to this generic procedure; we know of no such property.
This is an argument from the design and public analysis of BLAKE3, not a
proof.

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
0.07-0.08 in the pair probability, far larger than the 0.024 deficit that
would matter at full width. A pass therefore shows the absence of gross
non-randomness in this mechanism, not a measured full-width probability. A
failure would not distinguish kernel errors from non-randomness, but the
kernel is checked separately (Section M.1).

**Scope and limitations.** These experiments test uniformity and freshness
of the fixed target along lane-serialized walks from consecutive starts, the
same input structure the search uses, at widths 20 and 24 on 512 slices. They
do not test the 2^128-query regime, the full-width distinguished-point and
key events, or the full function rather than its slices, and they cannot
exclude a property that appears only at full scale. The loss terms of
Section P that involve distinguished points are each below 0.008 under the
model; the margin above 0.39 is 0.02393. H1 is therefore plausible rather
than established.

## 8. Evidence

Three declared experiments run `experiments/bounded_machine.py` in the
organizer's isolated executor.

`blake3-r7-bounded-machine-w14-v1` (implementation) in one execution:

1. regenerates the kernel and asserts 46,113 instructions, 776 kernel words
   and PD; proves statically that the allocated listing computes the gate DAG;
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
   with 256 cuts and recovery for four (l1, l2) shapes; every measurement must
   equal the closed form of Section M.3;
4. for each of 256 organizer trials, runs a 14-bit projected search
   (d = 4, k = 9, U = 256, R = 2, B = 48, IDL = 4,096) on the real target with
   the real kernel, compares it with the scalar reference on termination
   code, returned pair, insertions, cuts, starts, batches and compressions,
   compares four kernel lanes per batch with scalar BLAKE3 on all 256 output
   bits, and checks two lanes of one full-width random batch the same way.

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

**H-machine** (score-critical): Section 3. The comparison with other
published entries depends on it (Section L.6).

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
  64-bit key window; 5-byte straight-line encoding with longer formats for
  other code; recovery by scalar compressions.
- 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c and e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca
  (Jbenisek): the 256-lane bitsliced BLAKE3 kernel approach for the message
  family 0^32 || x and the charged register-file convention.
- a2e94df7-bff4-4461-ad40-7f75930cb241 (Jbenisek): lane-indexed lazy exposure
  and explicit treatment of adaptive histories in the probability argument,
  and the round-7 encoding sensitivity discussed in Section L.6.

All code in this package was written independently; no competitor file was
copied or executed. A historical prefix f17f7355 named by an earlier internal
draft could not be resolved to a published submission and is not declared.
