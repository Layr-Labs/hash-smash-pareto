# BLAKE3 round 7: bounded-restart bitsliced search with an organizer-certified success bound (C5)

This package claims an ordinary 256-bit collision construction for the
complete seven-round BLAKE3 hash (the full BLAKE3 round count) with total time
2^124.96851 target compressions, memory 2^19.99536 bytes and success
probability at least 0.39. It is the algorithm, machine and kernel of our
submission 09fe5fcd (C4, 124.96952 on a declared 1,024-register file) with
five changes: the exact checker of the success bound is a declared
experiment, so the organizer's executor reproduces every loss term and the
certified bound from the submitted source (Section P); the distinguished
density is 23 x 2^-116 through a five-bit window instead of 11 x 2^-115
through a four-bit one; the first stage of the distinguished test reads 16
planes instead of 32; the age-cap and horizon checks are merged into one
per-batch comparison; and the horizon is the least multiple of 2^100 that the
exact certification accepts. The machine is unchanged: a fixed file of 1,024
registers of 256 bits (its bytes included in the memory bound as storage),
with every computed-address access a charged load or store (Section 3). The
success bound is a random-function theorem (Section P) transferred to the
fixed target by the declared heuristic H1, supported by exact-law
experiments on 512 slices of the target (Section H). No complete collision is
exhibited.

| Quantity | Value | Basis |
| --- | --- | --- |
| rounds | 7 | target profile `blake3-r7-prefix-v1` |
| time_log2 | 124.96851 | Section L; exact log2 T = 124.968507383997, rounded up |
| memory_log2_bytes | 19.99536 | Section L; 1,045,208 bytes |
| normalizedTimeMemoryLog2 | 124.96851 | memory below 2^20 adds zero |
| success_probability | 0.39 | Section P (random-function bound 0.390000171520, rounded down, certified by experiment `blake3-r7-success-bound-v1`) and H1 |
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

    PD = 0x556aab8650f00b0204eefd1af8507c4dad1a08a430a609d996866a637669004d

written as a conventional big-endian hexadecimal integer; bit i of PD is the
output polarity of kernel plane i (unchanged from C4; the experiment asserts
the value). Because XOR with a constant is a bijection, f(u) = f(v) holds if
and only if D(u) = D(v). Distinct u != v with f(u) = f(v) therefore give two
distinct complete messages with equal 256-bit digests.

## 2. Frozen algorithm

### 2.1 Parameters

| Symbol | Value | Meaning |
| --- | --- | --- |
| lanes | 256 | one bitsliced word holds one bit of 256 points |
| d | 111 | distinguished: bits 0..110 of f(u) are zero and the five-bit window at bits 111..115 is below 23; density theta = 23 x 2^-116, L = 1/theta = 2^116/23 (about 2^111.48) |
| s1 | 16 | stage-1 planes: a batch is examined further only if some lane has bits 0..15 zero |
| k | 47 | endpoint key: bits 116..162 of f(u) |
| B | 1,045,778 x 2^100 (about 2^119.9961) | batch horizon; Q = 256B = 1,045,778 x 2^108 lane evaluations |
| R | ceil(12L) = 43,344,391,166,899,430,638,167,621,530,880,802 | per-trail age cap (12L + 14/23) |
| U | 98,400 | table capacity, never evicted |
| IDL | 131,072 | identifier limit; start t is rho + t mod 2^256 |
| E2MAX | 3Q/2^16 = 15,535,325,500,845,436,957,481,475,992,715,264 | budget of stage-2 batches |
| rho | one uniform 256-bit word | the only randomness |

Derived deterministic ceilings (all executions, all functions): Q = 256B lane
evaluations; at most floor(Q/R) = 7,829 cuts (each cut lane has used R
evaluations since its own restart, disjoint from other cuts); at most U
insertions; at most U + 1 endpoint handlers (every non-terminal handler
inserts); at most 256 + U + 7,829 = 106,485 < IDL allocated identifiers, so
the identifier guard cannot fire before another stop; at most E2MAX + 1
stage-2 entries (the last one halts).

### 2.2 State

Lane l holds its current point (bit j in plane register P_j, lane bit l),
identifier LID[l] and birth batch BIRTH[l]. Global state: batch counter b,
next identifier NID, table count CNT, the earliest-cut batch NEXTCUT, the
next event batch EVT = min(NEXTCUT, B), the stage-2 counter H2, rho and the
table: one array of 64-bit slots, four per 256-bit word; slot e (bits
64(e mod 4) .. 64(e mod 4) + 63 of word floor(e/4)) holds the 47-bit key in
its low 47 bits and the 17-bit start identifier in bits 47..63.

### 2.3 Control flow

1. Setup. rho = RAND. Clear the table and metadata words. For l = 0..255,
   restart lane l (identifier l, birth 0). Set b = 0, NEXTCUT = R,
   EVT = min(R, B), H2 = 0.
2. Batch. Evaluate f on all 256 lane inputs at once (the kernel), then set
   b = b + 1 (b is the index of this batch). All 256 evaluations are charged
   even if a handler later stops in this batch.
3. Stage 1. D = OR of planes 0..15: bit l of D is zero iff lane l's low 16
   bits are zero. If D is all-ones, skip to step 5.
4. Stage 2. H2 = H2 + 1; if H2 > E2MAX stop with failure (budget). D = D OR
   planes 16..110 OR (plane 115 AND (plane 114 OR (plane 113 AND plane 112
   AND plane 111))): bit l of D is now zero iff lane l's low 111 bits are
   zero and its five-bit window value is below 23 (lane l is distinguished).
   If D is all-ones, skip to step 5. Otherwise run the endpoint handlers in
   ascending lane order for each distinguished lane l: extract its 47-bit
   key; scan entries 0..CNT-1 for that key. On a match stop and run recovery
   (Section 2.4). Otherwise, if CNT = U, stop with failure (capacity).
   Otherwise write the key and LID[l] at entry CNT, increment CNT and restart
   lane l with birth b.
5. Event test. If b != EVT go to 2. Otherwise: (age cap) if b >= NEXTCUT,
   scan lanes 0..255: every lane with b - BIRTH[l] >= R is restarted with
   birth b (a cut); distinguished lanes were restarted in step 4, so
   endpoint handling takes precedence over the cap; then NEXTCUT = min_l
   BIRTH[l] + R and EVT = min(NEXTCUT, B). There is no global cut limit.
   (Horizon) if b = B stop with failure; otherwise go to 2.

Restart of lane l: if NID = IDL stop with failure (identifier guard; not
reachable for these parameters). Otherwise set LID[l] = NID, BIRTH[l] = b, write
the point rho + NID mod 2^256 into lane l of all 256 planes, NID = NID + 1.

Stage 1 loses no distinguished lane (a distinguished point has its low 16
bits zero) and stage 2 computes exactly the predicate of Section 2.1, so the
endpoint handlers see the same lanes as a single-stage test would; the split
changes only the operation count and adds the budget stop. NEXTCUT never
exceeds min BIRTH + R, because births only increase, and b reaches every
integer in turn, so the event test with EVT = min(NEXTCUT, B) runs the
age-cap scan in exactly the batches in which b >= NEXTCUT first holds and
stops at the horizon exactly after batch B; the scan reproduces the
reference rule "after the endpoint handlers, cut every non-distinguished
lane whose age is at least R".

### 2.4 Recovery (at most once)

On a key match between stored entry e (identifier s1) and the current lane
(identifier s2, length l2 = b - BIRTH <= R, current endpoint E extracted from
the planes):

1. Reconstruct: x = rho + s1; step x = f(x) until x is distinguished (low d
   bits zero and window below 23), counting l1 steps; if R steps pass without
   an endpoint stop with failure. If x != E stop with failure (a false
   short-key match).
2. Align: a = rho + s1, c = rho + s2; advance the start with the longer trail
   by |l1 - l2| steps. If a = c stop with failure (one start lies on the
   other trail).
3. Paired walk for at most min(l1, l2) steps: if f(a) = f(c) go to 4;
   otherwise a, c = f(a), f(c).
4. Final check: require a != c and recompute f(a) = f(c) (equivalently D(a)
   = D(c)). Output M(a), M(c). Any other outcome is failure.

Every scalar f evaluation in recovery is one target compression plus one XOR.
Reconstruction, alignment and the paired walk use at most l1 + |l1 - l2| +
2min(l1, l2) <= 3R compressions; the final check uses 2.

### 2.5 Termination codes

1 collision returned; 2 false short-key match; 3 start overlap; 4 table
capacity; 5 identifier guard; 6 horizon; 8 recovery inconsistency (cannot
occur for a true endpoint match; retained as an explicit guard); 9 stage-2
budget exhausted.

### 2.6 Changes against C4 and earlier entries

- Success bound: the same integrated detection-delay argument as C4; the
  exact checker is now the declared experiment `blake3-r7-success-bound-v1`
  (its source is in the package and the organizer's executor reports every
  term), and B is the least multiple of 2^100 that the exact certification
  accepts (C4's B was chosen by a float planning bound).
- Distinguished predicate: 111 zero bits and a five-bit window below 23
  (density 23/2^116, 4.5 percent denser than C4's 11/2^115), which shortens
  the detection delay; the key moves to bits 116..162. Any denser predicate
  does not fit: the certified count of distinguished values would exceed
  the largest table under 2^20 bytes.
- Distinguished test: stage 1 reads 16 planes (15 ORs) instead of 32; the
  stage-2 budget is 3Q/2^16 and its worst-case cost stays below 2^-14 of the
  total.
- Loop control: one comparison per batch against EVT = min(NEXTCUT, B)
  replaces the separate age-cap and horizon comparisons (3 instead of 6
  control operations per batch).
- Kernel, machine, table layout, recovery, identifiers and slice experiments
  are unchanged from C4; the kernel listing and PD are identical.
- Historical items resolved by earlier freezes (search structure, slot
  layout, recovery by scalar compressions, the PD label) are as in C3 and
  C4; the historical figures 124.97996, 0.3900000143, 84,750 entries and
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
smaller files. The program uses 822 of the 1,024 registers: 771 for the
kernel (planes of u and f(u) in registers 0..255 and temporaries) and 51
control registers (constants including the all-ones word ONES, counters,
the event batch EVT, rho, recovery state).

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
(through its operations) and none is charged twice. The program is the
machine's finite control; instruction fetch is not a primitive operation of
the cost model and is not charged.

The experiment sources of this package (`experiments/*.py`) are evidence
executed by the organizer's harness, which treats them as inert, untrusted
material under a 64 KiB total source budget (organizer documentation,
`docs/HEURISTIC_EXPERIMENTS.md`); they are not the algorithm's stored
program and are not part of the attack's code, working state or time
(Section M.5). The attack's code is the fixed image of Section 3.2 only.

### 3.2 Program image

The program is a byte image with three instruction formats, fixed by opcode:

| Format | Layout (little-endian bit fields) | Bytes |
| --- | --- | --- |
| control | opcode 16..39 (8) / three 10-bit register fields / 24-bit immediate or branch byte offset | 8 |
| kernel word | opcode 1..3 (2) / three 10-bit register fields (30) | 4 |
| constant | opcode 64 (8) / register (10) / 256-bit value | 40 |

The kernel is a block of 45,974 4-byte words introduced by the 8-byte KERNEL
control instruction, whose immediate holds the block length; this makes the
image decodable without a tag bit in the 32-bit kernel word. Kernel words are
three-operand XOR, AND or OR (the kernel of this entry contains no NOT and no
MOV; the encoder would express them as XOR d,a,ONES and OR d,a,a). Ten-bit
fields name all 1,024 registers. Every non-branch immediate of the 8-byte
format fits in 24 bits (the largest is 45,974), and every branch target is a
byte offset into the 206,808-byte image, also below 2^24. The experiment
encodes every program it runs, decodes the image, asserts that the decoded
program equals the generated one and that the image length equals the
ledger's code size, and executes only the decoded program.

## M. The machine program

The complete program is emitted by `build_program` in
`experiments/bounded_machine.py` for any parameter set. At the full-width
parameters it consists of the 45,974-instruction kernel, the 8-byte KERNEL
block header and 2,783 control instructions (2,784 instructions in the 8- and
40-byte formats), uses 822 registers and 25,112 memory words.

### M.1 Kernel

The kernel is identical to C4's. It computes planes of f(u) from planes of u
in place in registers 0..255. A constant-folding Boolean DAG builder maps
BLAKE3's modular additions to ripple-carry full adders (at most five gates
per bit; constants fold), rotations to plane relabelings, and output
constants to the stored polarity PD; the DAG has 45,974 gates (37,924 XOR,
2,653 AND, 5,397 OR, no NOT; the experiment asserts this split). In-place
register allocation in creation order, with each output's home register
reserved once its input dies, needs 771 registers and no output moves:
45,974 operations per batch with no memory access. The experiment asserts
these sizes and PD.

Full adders with three variable inputs use the pivot rule (two of the three
polarities agree; with p the third, u = q XOR p, v = r XOR p, sum = u XOR r,
carry = (u AND v) XOR p, and u, v have equal polarity so the AND is one
gate). With one constant input k and variable operands q, r of different
polarity, the carry maj(q, r, k) is formed from t = q XOR r (already needed
for the sum) as xx AND NOT t for k = 0 and as xx XOR (NOT xx AND other) for
k = 1, where xx is the operand whose polarity equals that of NOT t; both AND
inputs then have equal polarity, so no complement gate is emitted. This
rule is re-implemented from the public text of submission 76ab339a (credited
in Section 10).

Correctness argument (H-kernel). (1) Every gate-construction rule (XOR with
constant folding and polarity, AND/OR selection with stored polarities and
shared complements, the pivot full adder including the complement-free
constant cases, ripple-carry addition of words with constant, inverted and
polarity-flipped operands) is checked exhaustively on all operand classes by
the experiment: 6,191 cases, each over all input assignments in bit-parallel
form. (2) The word-level composition in `build_listing` follows the BLAKE3
specification line for line (eight G calls per round with rotations 16, 12,
8, 7, the message permutation, and the feed-forward v[i] XOR v[i+8]),
mirroring the scalar reference `digest_int`. (3) A static check proves that
the register-allocated listing computes the DAG for every input: it tracks
which DAG node each register holds and verifies every operand reference and
the final output placement. (4) Sampled full-digest agreement with scalar
BLAKE3 cross-checks the whole chain. Step (2) is established by inspection,
not mechanically, within this package; the claim is therefore declared as the
score-critical heuristic H-kernel. The authors' mechanical cut-point
equivalence check of this listing against the organizer reference (Section
8) is archived outside the package: with the program source at 54 KiB, the
checker (19 KiB without comments) and the organizer reference text do not
fit the 64 KiB total source budget of declared experiments, and the stripped
program would still exceed it, so the check is not organizer-executed.

### M.2 Main loop (per batch), event and stage 2

    LOOP:  KERNEL (block header 1 + 45,974 words)   45,975
           ADDI B,B,1                                    1
           OR D,P0,P1; OR D,D,Pj (j=2..15)              15
           BNE D,ONES,S2                                 2
    EPD:   BNE B,EVT,LOOP                                2

Per batch: KLEN + s1 + 5 = 45,995 operations.

    (fallthrough: event after batch B)
           BGE B,NEXTCUT,CUTB                            2
    CUTD:  BEQ B,BMAX,FAIL6                              2
           JMP LOOP                                      1

    S2:    ADDI H2,H2,1; BGE H2,E2LIM,FAIL9              3
           OR D,D,Pj (j=16..110)                        95
           AND T0,P112,P111; AND T0,T0,P113;
           OR T0,T0,P114; AND T0,T0,P115; OR D,D,T0      5
           BNE D,ONES,EPB                                2
           JMP EPD                                       1

Per event: 5 operations plus the scan of M.3 when B >= NEXTCUT; the final
horizon event costs 4 (BGE not taken, BEQ taken). Per stage-2 entry:
d - s1 + 10 = 105 operations when a lane is distinguished (the BNE falls
through to the endpoint batch) and 106 when the stage-1 hit was not
distinguished (the JMP returns to the loop). E2LIM = E2MAX + 1. The window
term is all-ones exactly for the lanes whose five-bit window value is at
least 23 (23 = 10111 in binary: bit 4 set and either bit 3 set or bits 2,
1, 0 all set).

### M.3 Handlers

Endpoint batch (EPB): NOT ND,D; MOV LANE,0; then for each of the 256 lanes
SHR/AND/BEQ on ND (4) and ADDI/BNE (3); final JMP: 1,795 operations.

Key extraction per endpoint: MOV KEY,0 and, for each key bit j, SHR from plane
d+5+j by LANE, AND 1, SHLI j, OR into KEY: 1 + 4k = 189.

Table scan per non-matching entry: BEQ EIDX,CNT; SHRI, ADDI, LD, AND, SHLI, SHR
(slot word shifted into place), AND with the key mask into a scratch register;
BEQ against KEY; ADDI; JMP: 13. Insertion at count c: MOV EIDX (1), 13c,
terminating BEQ (2), capacity BEQ (2), slot value (identifier load 2, SHLI 47,
OR with KEY: 4), one read-modify-write of the slot word (SHRI, ADDI, LD, AND,
SHLI, SHL, OR, ST: 8), ADDI CNT, LDI RR, JMP (3): 20 + 13c. A terminal handler
costs at most 13U + 5 (capacity) or 13e + 12 <= 13U - 1 (match at entry e).

Restart: guard BEQ (2), two address/store pairs (4), ADD start, ADDI NID (2),
SHL/NOT lane mask (2), and per plane SHRI, AND, SHL, AND, OR (5 x 256 = 1,280),
then a return dispatch on RR: 1,292, 1,294 or 1,295 operations for returns to
setup, endpoint and cut.

Cut scan (CUTB): MOV, MOV (2); per lane ADDI, LD, SUB, BLT (5), BGE on the
running minimum (2), ADDI, BNE (3); final ADD NEXTCUT, MOV EVT, BLT
NEXTCUT,BMAX (4, with MOV EVT,BMAX and JMP added when NEXTCUT >= BMAX):
2,566 (2,568 in the worst case), plus at most 256 minimum updates (MOV) and,
per cut, LDI RR, JMP and MOV after return (3) plus one restart (1,295).

Recovery: stored identifier from the shifted slot word already in a register
(SHRI 47, AND: 2), current identifier and length (5), endpoint extraction
MOV + 4 x 256 (1,025), start and counter (2), post-reconstruction checks,
branch selection and alignment exits (12): 1,046 fixed. Each reconstruction
step: at most 76 operations (loop guard BEQ 2, COMP 64, XOR 1, ADDI 1, MOV 1,
the low-bits AND 1 and BNE 2, and, when the low d bits are zero, SHRI 1, AND 1
and BGE 2 for the five-bit window) and one compression. Each alignment step:
69 operations and one compression. Each non-final paired step: 138 operations
and two compressions. Final paired step and final check: 268 operations and
four compressions. OUT and HALT: 3.

Setup: 16 LDI constants and RAND (17); memory clear MOV, LDI and 25,112 x (ST,
ADDI, BNE) (2 + 4 x 25,112); five MOV; 256 x (LDI RR, JMP, restart 1,292,
ADDI, BNE); MOV NEXTCUT, MOV EVT, BLT RCAP,BMAX (4): 432,508 operations in
total.

### M.4 Storage layout

Memory words: table slots ceil(98,400/4) = 24,600; BIRTH 256; LID 256; total
25,112 words (803,584 bytes). Only entries below CNT are read. Register file:
1,024 x 32 = 32,768 bytes (822 registers used: 771 kernel, 51 control). Code:
45,974 x 4 kernel bytes plus 22,912 control bytes (the KERNEL header and
2,783 control instructions, 2,784 in all, of which the 20 LDI instructions
take 40 bytes and the rest 8), 206,808 bytes. COMP working state receives a
2,048-byte allowance. Setup uses the same storage as the search.

### M.5 The fixed program image is the algorithm

The algorithm is the fixed image of Section 3.2. It is a deterministic,
uniform function of the public target and parameters, contains no search
results or other target-specific advice, and is counted in memory in full.
No program generation is performed during the charged computation: the
attack begins with the image loaded, as any algorithm begins with its code.
The generator in `experiments/bounded_machine.py` and the checker in
`experiments/success_bound.py` are provenance, reproducibility and
verification tooling executed by the organizer as evidence; their own time
and workspace are not part of the attack and are not claimed to be bounded.
Hence preprocessing_log2 = 0 and nonuniform_advice_log2_bytes = 0.

## L. Resource ledger

### L.1 Worst-case event counts

| Event | Bound | Reason |
| --- | --- | --- |
| batches | B = 1,045,778 x 2^100 | horizon |
| stage-2 entries | E2MAX + 1 = 3Q/2^16 + 1 | budget halt (the last entry performs 3 operations) |
| endpoint batches | U + 1 | each contains at least one handler; handlers <= U + 1 |
| insertions, endpoint restarts | U | capacity |
| cuts | floor(Q/R) = 7,829 | disjoint R-evaluation blocks |
| age-cap events and scans | 7,829 + U = 106,229 | an event with a scan that cuts nothing requires an endpoint restart since the previous scan (otherwise NEXTCUT is exact and the minimum-birth lane is cut); every age-cap event runs a scan |
| horizon event | 1 | terminal |
| recovery | 1 | terminal |

### L.2 Word-operation terms (exact integers)

| Term | Operations |
| --- | --- |
| setup | 432,508 |
| main batches: B x 45,995 | 60,974,702,627,104,927,817,332,095,000,314,757,775,360 |
| stage-2 entries: E2MAX x 106 + 3 | 1,646,744,503,089,616,317,493,036,455,227,817,987 |
| endpoint-batch scans: 98,401 x 1,795 | 176,629,795 |
| key extraction: 98,401 x 189 | 18,597,789 |
| table scans and insertions: sum over c < U of (20 + 13c) | 62,937,968,400 |
| terminal handler: 13U + 5 | 1,279,205 |
| endpoint restarts: U x 1,294 | 127,329,600 |
| age-cap events and scans: 106,229 x (5 + 2,568 + 256) | 300,521,841 |
| cuts: 7,829 x (3 + 1,295) | 10,162,042 |
| recovery: 1,046 + 268 + 214R - 138 | 9,275,699,709,716,478,156,567,871,007,608,492,804 |
| horizon event, output and halt | 7 |

W = 60,985,625,071,317,733,911,806,155,907,841,167,007,338. The recovery term
uses 76l1 + 69|l1 - l2| + 138(min(l1, l2) - 1), at most 214R - 138 for
l1, l2 <= R. Compressions: H <= 3R + 2 =
130,033,173,500,698,291,914,502,864,592,642,408.

### L.3 Total time

    T = H + W/C,   W = sum of Section L.2,   C = 1470
    (C is the round-7 reference_operation_cost printed by the organizer's
    `pareto_candidate.py --family blake3 --rounds 7 --show-contract`)
    log2 T = 124.968507383997        claim time_log2 = 124.96851

The main loop is 99.670 percent of T (log2 124.963734); the kernel alone is
log2 124.963075. Recovery compressions are 2^116.646 units. Stage-2,
handler, table, cut and setup terms together are below 2^-14 of T (the
stage-2 term alone is 2^-15.2 of T). The bound holds for every function and
every rho, including failed attempts; there is one attempt and no
amplification.

### L.4 Memory

    code 206,808 + register file 32,768 + memory words 803,584
      + COMP state 2,048 = 1,045,208 bytes
    log2 = 19.995359        claim memory_log2_bytes = 19.99536

Memory includes code, the whole register file (including rho, constants,
output points and recovery state), the table, lane metadata and the COMP
working state. There is no advice or precomputed data. Memory is below 2^20
bytes (3,368 bytes of margin), so it adds nothing to the normalized score.

### L.5 Established counts versus assumptions

Established by the program text and asserted by the declared experiment
(the organizer's isolated executor runs it; a failed assertion fails the
experiment): the kernel size, gate split, register count (822 of 1,024) and
its static correctness proof with respect to the DAG; the per-handler closed
forms, measured at the full-width parameter set under test functions (setup,
batch, stage-2 entry on a hit and on a miss, event, endpoint scans at table
counts 0..3, insertion,
a cut scan with 256 cuts, a cut scan with one minimum update, the capacity
terminal, a match at entry 0, and recovery for four length pairs) and
asserted equal; the image round trip and size; outcome-level equivalence of
the program and the scalar reference at reduced width, including the budget
stop. Established by the declared experiment `blake3-r7-success-bound-v1`:
the arithmetic of Section P (every loss term and the certified bound).
Established mathematically: the event bounds of L.1 and the arithmetic of
L.2-L.4 (reproduced by the administrative ledger calculator). Assumed: the
declared register file (Section 3.1); the specification-following
composition of the kernel (H-kernel); the premise H1. The probability
argument of Section P is a theorem in the random-function model, reviewed by
its authors and by fresh-context advisory critics (C4 and this entry).

### L.6 Sensitivity to the register file

The same algorithm with smaller files needs spill loads and stores in the
kernel (measured with a furthest-next-use allocator in creation order on this
entry's gate network; the fully implemented 32-register program is our
submission 56b4da71 with C1's parameters, 125.92167):

| Registers | Kernel operations per batch | time_log2 |
| --- | --- | --- |
| 32 | 76,696 | 125.70467 |
| 64 | 70,180 | 125.57688 |
| 128 | 60,540 | 125.36428 |
| 256 | 54,756 | 125.21984 |
| 1,024 (this entry) | 45,974 | 124.96851 |

The values for 32-256 registers are derived from the measured kernel sizes
with this entry's parameters and are not separately implemented. Other
sensitivities: instruction fetch, if charged at one load per 32 bytes of
kernel code, adds 5,747 operations per batch (125.13784); at 36 bytes per
instruction memory would be 2,593,688 bytes = 2^21.31, adding 1.31 to the
normalized score. Section H gives the time cost of absorbing a fixed-target
probability deficit. Against our C4 (09fe5fcd, 124.96952) under identical
machine assumptions this entry saves 0.00101 bits (exact ledger difference
124.969513627026 - 124.968507383997 = 0.001006). Applying the changes in
order, the 16-plane first stage and the merged loop control (19 fewer
operations per batch, at this entry's horizon) account for 0.00059 and the
denser distinguished predicate together with the exactly minimal horizon for
0.00041 (of which the horizon rounding is about 0.00006); the components are
order-dependent, the total is a measured ledger difference, not an estimate.

## P. Success probability in the random-function model

**Model.** F is a uniformly random function on 256-bit strings and rho is
uniform and independent of F (the bound in fact holds for every fixed rho).
The bound below is a theorem in this model; its application to the fixed
target is the heuristic H1 (Section H). It assumes that the main-loop kernel
computes F exactly (H-kernel). The structure of the argument, in particular
the lottery coupling that separates the distinguished coins from the values
and the integration of the detection delay over the first-collision
distribution, follows the public proof of submission 76ab339a (Lemma 2); it
is re-derived here for this program's restart rule, table and halts, as in
our C4.

**Notation.** The run evaluates Q = 256B slots, numbered t = 1, ..., Q batch
by batch and lane by lane within a batch; b(t) = ceil(t/256) is the batch of
slot t. N = 2^256; the distinguished class has exactly theta N = 23 x 2^140
values and the plain class N' = N - 23 x 2^140 values. A trail is the run of
one lane's evaluations between two restarts; its age a(t) at slot t is the
number of its earlier evaluations. A trail finishes when an evaluation
returns a distinguished value (its endpoint, handled in that batch), is cut
when its age reaches R at the end of a batch without an endpoint (step 5),
and is open when the run halts first. An evaluation is fresh when its input
has not been evaluated before; a collision is a fresh evaluation whose value
equals an earlier value (an output or a start). The declared experiment
`blake3-r7-success-bound-v1` (`experiments/success_bound.py`; 60-digit
decimals with outward rounding, exact rationals elsewhere) evaluates every
bound below in the organizer's executor and reports each term rounded up at
the twelfth decimal and the result rounded down; the values quoted here are
those it reports.

**Step 1 (lazy sampling with a lottery).** Realize F lazily: draw independent
coins xi_t ~ Bernoulli(theta), one per slot, and independent values V_t,
uniform on the distinguished class when xi_t = 1 and on the plain class
otherwise; the t-th evaluation returns V_t if it is fresh and the stored
value of its input otherwise. This is a correct lazy sampling of a uniformly
random function for every adaptive choice of inputs. Facts used:

- (L1) Given the whole lottery of coins and the history before t, a fresh
  plain slot t has P(V_t = v) = 1/N' for every plain value v.
- (L2) Whether slot t is fresh, its input, batch, age and the trail
  boundaries before t are determined by the history before t.
- (L3) The coins of one lane are i.i.d.; different lanes are independent;
  reading coin positions in stopping-time order yields an i.i.d. sequence.
- (L4) N1 = sum of all coins is exactly Binomial(Q, theta), q = Q theta =
  93,956.62; with k = 96,249, P(N1 >= k) <= e^-q (eq/k)^k <= 2^-40.
- (L5) The run up to a stopping time is determined by the values and coins up
  to it; the coins after a stopping time are independent of that past.

Two global events are excluded and charged: E1, some value of the run equals
a start rho + s, s < IDL: each fresh value is uniform on all N values before
its coin is conditioned on, and there are IDL starts, so at most Q IDL/N; E2,
some fresh distinguished value equals an earlier distinguished value: on
N1 <= k - 1 at most k^2 L/N (each fresh distinguished value is uniform on
theta N values and at most k - 1 earlier ones exist). Outside E1 and E2 a
non-fresh evaluation exists only after a plain collision.

**Step 2 (the free run and the first plain collision).** Given the coins,
the free run (every evaluation fresh) has trail boundaries, ages, endpoints
and cuts that are functions of the coins alone: a trail finishes at its
lane's next coin 1 and is cut when R consecutive coins from its start are 0
(a long trail). The lottery is extended beyond the run by further
independent coins, used only in the analysis, so the quantities below are
always defined. For a slot y let sigma(y) be the number of lane(y) slots
after y up to and including the first with coin 1, and g(t) the number of
consecutive coin-0 slots on lane(t) immediately before t; in the free run
a(t) <= g(t). Let tau be the first plain slot t whose value equals the value
V_y of an earlier plain slot y (the first plain collision). Outside E1 and E2
the real run coincides with the free run up to tau. With Pi_m = prod_{i<m}
(1 - i/N') and n0(t) the number of plain slots up to t,

    P(tau = t, V_t = V_y | coins) = Pi_(n0(t)-1) / N'   for every plain y < t,
    P(tau <= Q | coins) = 1 - Pi_(n0(Q)).

On N1 <= k - 1, n0(t) - 1 >= t - k and Pi_(t-k) <= shift x Pi_(t-1) with
shift = 1/(1 - kQ/N') (Pi_(t-1) is Pi_(t-k) times at most k - 1 factors, each
at least 1 - Q/N'), so P(tau <= Q, N1 <= k - 1) >= 1 - shift Pi_Q - 2^-40.
Enclosures used by the checker: exp(-m(m-1)/(2N') - (m-1)m(2m-1)/(6N'^2))
<= Pi_m <= exp(-m(m-1)/(2N')).

**Step 3 (a good undisturbed first collision is output).** Let tau = t with
partner y (V_t = V_y, y < t plain), X the trail of t and Y the trail of y.
Call the pair good when

- (G1) y is not on X;
- (G2) b(y) < b(t);
- (G3) Y is not long (its first R coins are not all 0), so Y finishes at its
  endpoint after a(y) + sigma(y) <= R - 1 earlier evaluations and is never
  cut;
- (G4) b(t) + sigma(y) <= B and a(t) + sigma(y) <= R - 1;

and undisturbed when no fresh evaluation of Y after slot t, up to and
including its endpoint, is a collision. Claim: on a good undisturbed pair,
outside E1, E2 and the halts of Step 5, the program outputs a pair. Proof.
The input of X after t is V_t = V_y, the input of Y after y, so X's
evaluations after t repeat Y's evaluations after y: the j-th of them in batch
b(t) + j for X and b(y) + j for Y. Y is never cut (G3), and its evaluations
after t are fresh non-collisions (undisturbed; before t they are not
collisions because tau is the first), so its lane's coins decide: its
endpoint is its sigma(y)-th evaluation after y, in batch b(y) + sigma(y) <
b(t) + sigma(y) <= B (G2, G4), inside the run, and the endpoint handler
stores Y's key (the table is not full, Step 5) and restarts Y. X repeats the
same points (non-fresh) and reaches the same endpoint in batch b(t) +
sigma(y) <= B; before that evaluation X has done a(t) + sigma(y) <= R - 1
evaluations, so no cut scan removed it (a lane is cut only when its age at
the end of a batch is at least R, and the event test of step 5 runs the scan
in exactly those batches). X's handler finds the stored key (an earlier
entry with the same key but a different endpoint is a false-key stop, Step
5) and runs recovery with two different trails (G1) that end at the same
endpoint, started at different starts, whose colliding inputs differ (t is
fresh). Section 2.4 then outputs a pair: reconstruction of Y takes
a(y) + sigma(y) + 1 <= R steps, the aligned starts differ outside E1 (equal
aligned starts mean a start equals an iterate computed in the run), and the
paired walk meets at the first pair of distinct inputs with equal values,
which exists because the two paths merge at V_t = V_y and nowhere earlier
(tau is the first plain collision). QED.

**Step 4 (pairs that are not good; the disturbance).** Let W(t, y) be the
event (tau = t, V_t = V_y), and work on N1 <= k - 1 outside E1 and E2. By
Step 2, P(W(t, y) | coins) = Pi_(n0(t)-1)/N' <= 1/N' for every pair (used in
(a), (b), (c), the second part of (d) and (e)), and on N1 <= k - 1 also
<= shift Pi_(t-1)/N' (used in the first part of (d)); for fixed y the sum
over t of P(W(t, y) | coins) is at most Q/N'. Each failure below is bounded
by the expected number of pairs of its kind times the hazard.

- (a) (G1) fails: y is one of X's a(t) <= g(t) earlier evaluations; E g(t) <=
  sum_{i>=1} (1 - theta)^i <= L - 1. Loss at most Q L/N' (own trail).
- (b) (G2) fails: y is in t's batch before t, at most 255 per t: 255 Q/N'.
- (c) (G3) fails: y lies on a long trail. A long trail has at most R
  evaluations (it is cut at age R). Scan each lane in trials of R coins from
  the current position (a trial succeeds if all R coins are 0 and fails at
  its first 1): the long trails of a lane are at most the successes, the
  failures are at most N1 + 256 (expectation at most q + 256), and trials are
  independent with success probability (1 - theta)^R <= p = e^(-R theta); by
  Wald's identity the expected number of long trails is at most
  p (q + 256)/(1 - p). Each of their at most R points pairs with at most Q
  slots t at hazard 1/N'. Loss at most R Q p (q + 256)/((1 - p) N') (long
  earlier trail).
- (d) (G4) fails, first part: b(t) + sigma(y) > B means that the B - b(t)
  coins after y on lane(y) are all 0 (these positions lie inside the run
  because b(y) < b(t)): probability (1 - theta)^(B - b(t)) <= e^(-theta
  (B - b(t))) for each y, independent of the values. With P(W(t, y) | coins)
  <= shift Pi_(t-1)/N' and sum over y < t of 1/N' giving (t - 1)/N', and
  (t - 1) Pi_(t-1)/N' = Pi_(t-1) - Pi_t, the loss is at most
  shift x sum over bins (a, b] of [0, Q] of (Pi_a - Pi_b) e^(-theta (B -
  ceil(b/256))) (detection delay; the exponential is evaluated at the bin's
  right end, where B - b(t) is smallest, and the checker uses the upper
  enclosure of Pi_a and the lower enclosure of Pi_b in 22,000 bins, 20,000 of
  them over the last 150 x 256 L slots).
  Second part: a(t) + sigma(y) >= R requires g(t) + sigma(y) >= R. On
  different lanes g(t) and sigma(y) - 1 are dominated by independent
  geometric variables on {0, 1, ...} (coins before t on lane(t), coins after
  y on lane(y)); their sum is at least R - 1 only if one i.i.d. sequence has
  at most one 1 among R - 1 coins: probability at most (1 - theta)^(R-1) +
  (R - 1) theta (1 - theta)^(R-2) <= p2 = e^(-(R-1) theta) (1 + (R - 1)
  theta), where (1 - theta)^(R-2) <= e^(-(R-1) theta) because ln(1 - theta)
  <= -theta - theta^2/2 and (R - 2) theta >= 2 (here 12.0). On the same lane
  with (G1) and (G3), y lies on an earlier short trail of the lane, which
  ended with a coin 1 before X started; (g(t), sigma(y) - 1) is then
  determined by disjoint coin sets whose sum is stochastically dominated by
  the sum of two independent geometric variables (the exact same-lane
  probability is (1 - theta)^(R-1) (1 + (R - 1) theta) minus a positive
  term), so the same bound holds. At most Q(Q - 1)/2 pairs at hazard 1/N':
  loss at most PP p2 with PP = Q(Q - 1)/(2N') (later-trail age).
- (e) Disturbance. For a good pair, the fresh evaluations of Y after slot t
  up to its endpoint number at most r', the number of lane(y) coins after t
  up to and including the next 1, dominated by a geometric variable of mean
  L and independent of the past at the stopping time t (L5). Each plain one
  is a collision with conditional probability at most (Q + IDL)/N' (an
  earlier value or a start); the final, distinguished evaluation is covered
  by E2, and counting it in r' only overcounts. The events W(t, y) are
  disjoint (values before tau are distinct), with total probability at most
  sum_t (t - 1)/N' <= PP. Loss at most PP L (Q + IDL)/N' (disturbed suffix).

**Step 5 (halts before the pair is output).** Outside E1 and E2 every
distinguished evaluation is either fresh (counted in N1) or a repeat of a
stored endpoint, which is a true key match that ends the run; so insertions
are at most N1 <= k - 1 < U and the capacity stop does not occur. A false
short-key stop needs a fresh distinguished value whose 47 key bits (uniform
on 2^47 values, independent of the stored keys) equal a stored key: at most
k U/2^47. The identifier guard is unreachable (106,485 < IDL). The horizon
stop does not occur on a good pair (Step 3). The stage-2 budget: a batch is
counted when some lane's low 16 bits are zero. Fresh evaluations with that
property are at most the plain ones, each with conditional probability at
most 2^-16 given the past (Binomial-dominated; Chernoff gives P(more than
2 Q/2^16) <= e^(-Q/(3 x 2^16))), plus N1. Non-fresh evaluations exist only on
trails that collided; each such trail repeats at most R values of one
functional-graph path from its collision target, and the number of plain
collisions in the run exceeds 60 with probability at most exp(-120 +
(e^2 - 1) Hs), Hs = (Q(Q - 1)/2 + IDL Q)/N', because each fresh plain
evaluation is a collision with conditional probability at most (t - 1 +
IDL)/N'. Every value on such a path was a fresh output with hit hazard at
most 2^-16, so the hits on the at most 60 paths exceed 2 x 60 R/2^16 with
probability below Q e^(-R/(3 x 2^16)) (a union bound over the possible path
starts). Hence the number of stage-2 batches is below 3 Q/2^16 = E2MAX
except with probability below 2^-90, which is charged together with the
rounding of the checker's enclosures.

**Step 6 (the bound).** The attempt succeeds unless no plain collision occurs
by Q, or N1 >= k, or the first plain collision is not good or is disturbed,
or E1, E2 or a halt of Step 5 occurs. Therefore

    P_F >= 1 - shift Pi_Q - 2^-40 - [own] - [same batch] - [long] - [delay]
           - [age] - [disturbed] - P(E1) - P(E2) - [false key] - [budget and rounding].

| Term (observation name in the experiment) | Bound | Upper value |
| --- | --- | --- |
| no plain collision (`no_duplicate`) | shift Pi_Q | 0.608149110598 |
| detection delay (`detection_delay`, Step 4 d) | shift sum_bins (Pi_a - Pi_b) e^(-theta (B - ceil(b/256))) | 0.001654309170 |
| own trail (`own_trail`, G1) | Q L/N' | 0.000010586486 |
| long earlier trail (`long_earlier_trail`, G3) | R Q p (q + 256)/((1 - p) N'), p = e^(-R theta) | 0.000073537863 |
| later-trail age (`later_trail_age`, G4 second part) | PP p2 | 0.000039724529 |
| disturbed suffix (`disturbed_suffix`) | PP L (Q + IDL)/N' | 0.000005265032 |
| same-batch pair (`same_batch_pair`, G2) | 255 Q/N' | 1e-12 |
| start hit E1 (`start_hit`) | Q IDL/N | 1e-12 |
| distinguished-class duplicate E2 (`distinguished_class_duplicate`) | k^2 L/N | 1e-12 |
| N1 >= k (`count_tail_N1`) | 2^-40 | 1e-12 |
| false 47-bit key (`false_key`) | k U/2^47 | 0.000067294804 |
| stage-2 budget and rounding (`stage2_budget_and_rounding`) | | 1e-12 |
| sum of losses | | 0.609999828480 |

The result is P_F >= 0.390000171520 (rounded down; observation
`success_lower_bound`), a margin of 1.7 x 10^-7 above 0.39. B is the least
multiple of 2^100 for which the exact certification is at least 0.39
(bisection of the certification itself; the next smaller multiple gives
0.3899999...). R theta = 12 + 14 theta/23 and p, p2 are evaluated at that R.
The parameters were chosen by a float exploration of this bound over the
density, the age cap, the key width and the table size under the 2^20-byte
memory ceiling (`tools/optimize_c4_integrated.py` of our repository): a
density above 23/2^116 does not fit (the certified count k would exceed the
largest table), R near 12L balances the long-trail and age losses against
the recovery cost, and k = 47 is the widest key the 64-bit slot admits beside
the 17-bit identifier.

**What the organizer's execution of the checker establishes.** The
experiment runs the same source that produced the table above and reports
each term; a reviewer can compare the reported values with this section
without trusting any number quoted by the authors. It does not establish the
event cover (Steps 1-5), which is a mathematical argument, nor anything about
the fixed target (H1).

### P.1 Review against the implemented program

The argument was re-checked against the decoded machine program, item by item.

1. *Serialization.* The program computes all 256 outputs of a batch before
   any handler, then runs stage 1, stage 2 and the endpoint handlers in
   ascending lane order, then the event test and the age-cap scan. Handlers
   change only next-batch inputs, and a lane's key and endpoint are read
   before that lane is restarted, so revealing answers in lane order with
   virtual handlers yields the same executions. Stage 1 flags every
   distinguished lane and stage 2 computes the exact predicate (Section 2.3).
2. *Freshness.* Before the first collision or start hit, a continuing lane's
   input is its own previous output and a restarted lane's input is a start
   with an unused identifier (starts are distinct because 106,485 < 2^256);
   an earlier query of either value would itself be a collision or a start
   hit. This holds within a batch as well.
3. *The age cap is exact.* NEXTCUT never exceeds min BIRTH + R and EVT =
   min(NEXTCUT, B) is recomputed whenever NEXTCUT changes, so the scan runs
   in exactly the batches in which b >= NEXTCUT first holds, and every lane
   whose age reaches R at the end of a batch is cut in that batch, exactly as
   Steps 3 and 4 assume (a trail with a(t) + sigma(y) <= R - 1 evaluations
   before its endpoint evaluation survives every scan; a long trail is cut
   after exactly R evaluations). Conversely no lane is cut earlier, and an
   endpoint at age exactly R is handled as an endpoint. The horizon stop
   occurs exactly after batch B.
4. *Table semantics.* Keys in the table are unique (insertion only after an
   unsuccessful scan) and entries are never evicted. A repeated answer that is
   distinguished reproduces an endpoint whose key is already stored, giving a
   true match; a fresh distinguished value whose key is stored for a different
   endpoint is the false-key stop of Step 5.
5. *Recovery of any true match.* For stored and current trails with the same
   first endpoint and lengths l1, l2 <= R, the aligned states are equal only if
   one start equals a positive iterate of the other start; that iterate was
   computed during the main search, so this is E1. Otherwise the paired walk
   meets at distinct inputs within min(l1, l2) steps. Recovery revisits only
   values already computed and creates no new fresh answers.
6. *Counted quantities match the program.* Q = 256B, the identifier bound
   106,485 < IDL = 131,072 (so the identifier guard never fires), the start
   set of 131,072 values, U = 98,400 > k = 96,249, 47 key bits (bits
   116..162) disjoint from the 116 bits read by the distinguished predicate,
   R and E2MAX are the program's values and the checker's constants. The
   identifier field of a table slot holds 17 bits, enough for every
   identifier below IDL. The recovery loop applies the same two-part
   distinguished test as stage 2 and the scalar reference.
7. *Budget semantics.* The reference and the machine count the same batches
   (those with a lane whose low 16 bits are zero after the batch) and halt
   with code 9 when the count exceeds E2MAX before doing any stage-2 work;
   two fixtures exercise the halt and a run just inside the budget, and a
   third a stage-1 hit that stage 2 rejects.

The event cover of C2 was reviewed by one independent fresh-context agent
(no missing event found); the integrated argument of C4 was reviewed by a
fresh-context advisory critic, which verified Steps 1-6 against the program
and found no defect; this entry's changes (density, stage-1 width, event
test, horizon) were reviewed the same way before submission. None of this is
independent validation. A valid random-function bound does not imply a bound
for every function (for a permutation the algorithm never succeeds), which
is why the transfer to the fixed target is declared as H1.

## H. Fixed-target heuristic H1 and its evidence

**Statement.** For the fixed walk f(u) = LE256(BLAKE3_r7(M(u))) XOR PD, the
success probability of this algorithm over a uniform rho is at least the
random-function bound of Section P, hence at least 0.39.

**Why the random-function model is the relevant model.** Seven rounds is the
full round count of BLAKE3, so the target is the complete, unreduced hash
applied to single-block messages. The algorithm is generic: it uses no
property of BLAKE3 beyond evaluating it. The proof uses only that answers to
fresh queries along the search are uniform and independent of the history
(including the independence of the distinguished coins from the values
within their class), which is the standard model for generic collision
search against an unbroken 256-bit hash. The parameters are tuned so that
the random-function bound is 0.390000172, only 1.7 x 10^-7 above the
required 0.39: any fixed-target deficit larger than that would defeat the
claim. A deficit of that size would be a structural property of full BLAKE3
visible to this generic procedure (a systematic shortfall of collisions or
of distinguished points along walks); we know of no such property, but this
is an argument from the design and public analysis of BLAKE3, not a proof.
Sensitivity: absorbing a deficit eps in the fixed-target success probability
by lengthening the horizon costs 0.0024 bits for eps = 0.001 and
0.0236 bits for eps = 0.01 (same bound, same density; the table of
98,400 entries still certifies); eps = 0.05 does not fit under 1 MiB at this
density.

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
width is 1.7 x 10^-7 (Section P); no feasible experiment of this kind can
detect a deficit of that size. A pass therefore shows the absence of gross
non-randomness in this mechanism, not a measured full-width probability. A
failure would not distinguish kernel errors from non-randomness, but the
kernel is checked separately (Section M.1).

**Scope and limitations.** These experiments test uniformity and freshness
of the fixed target along lane-serialized walks from consecutive starts, with
the search's lane serialization and consecutive-start structure but with the
high input bits fixed by a seed constant (the search's inputs are full
256-bit values), at widths 20 and 24 on 512 slices. They do not test the
2^128-query regime, the full-width distinguished-point and key events, or
the full function rather than its slices, and they cannot exclude a property
that appears only at full scale. The loss terms of Section P that involve
distinguished points are each below 0.002 under the model; the margin above
0.39 is 1.7 x 10^-7. H1 is therefore plausible rather than established.

## 8. Evidence

Four declared experiments run in the organizer's isolated executor:
`blake3-r7-bounded-machine-w16-v3` and the two slice experiments execute
`experiments/bounded_machine.py`; `blake3-r7-success-bound-v1` executes
`experiments/success_bound.py`. The two source files total about 60.6 KiB
(62,103 bytes) of the 64 KiB budget for declared experiment sources.

`blake3-r7-bounded-machine-w16-v3` (implementation) in one execution:

1. regenerates the kernel and asserts 45,974 instructions, 771 kernel
   registers, the gate split and PD, and that all 822 statically named
   registers fit the declared 1,024-register file; proves statically that the
   register-allocated listing computes the gate DAG; checks all 6,191
   gate-rule cases exhaustively (the reported `fixtures_passed` counts these
   plus the thirteen fixtures, 6,204); serializes every program it runs into
   its image, decodes it, asserts the round trip and the image size, and
   executes only decoded code;
2. runs thirteen deterministic fixtures through both the complete machine
   program (with the kernel and COMP replaced lane-wise by small test
   functions) and the scalar reference: direct merge, false short key, start
   overlap, empty capacity, endpoint exactly at the age cap, repeated cuts
   without a global halt, same-batch capacity ordering, identifier
   exhaustion, a later-lane match within one batch, alignment over unequal
   lengths, the stage-2 budget halt, a run just inside the budget, and a
   stage-1 hit whose window value 23 is not distinguished; all
   outcome fields (termination code, pair, insertions, cuts, stage-2 batches,
   starts, batches, compressions) must agree and each expected termination
   code must occur;
3. builds the full-width program and measures, under test functions, the setup
   cost, the per-batch cost, the stage-2 entry cost on a distinguished lane
   and on a stage-1 hit that is not distinguished, the event cost, endpoint
   handlers at table counts 0..3, a cut scan with 256 cuts, a cut scan with
   one minimum update, the capacity terminal, a match at entry 0 and recovery
   for four (l1, l2) shapes; every measurement must equal the closed form of
   Section M;
4. for each of 256 organizer trials, runs a 16-bit projected search
   (d = 3, stage 1 on planes 0..2, five-bit window at bits 3..7, k = 8,
   U = 256, R = 2, B = 48, IDL = 4,096, E2MAX = 4,608) on the real target with
   the real kernel, compares it with the scalar reference on termination
   code, returned pair, insertions, cuts, stage-2 batches, starts, batches
   and compressions, compares four kernel lanes per batch with scalar BLAKE3
   on all 256 output bits, and checks eight lanes of one full-width random
   batch the same way.

The 16-bit projection zeroes planes 16..255 after the kernel and masks scalar
values; these diagnostic-only operations exist only in the reduced program.
Its success frequency is control-flow coverage, not a probability estimate
(with an 8-bit key most projected runs end in a false short-key match after a
few batches; the age cap of 2 makes cuts occur in the trials).

`blake3-r7-success-bound-v1` (probability arithmetic) certifies the bound of
Section P from the submitted source and reports the twelve loss terms, the
bound, the certification flag, the Chernoff count and the horizon as
observations in every trial row; it returns no pairs and uses no target
evaluation. It establishes the arithmetic of Section P, not the event cover
and not H1.

`blake3-r7-slice-first-collision-w20-v1` and `-w24-v1` (H1 evidence) are
described in Section H; they use the kernel decoded from the full-width
image. Their identifiers, procedure, predictions and sampled walk are
unchanged from C4 (same kernel, same PD).

Not established by any organizer-executed experiment: kernel correctness on
all 2^256 inputs (the construction argument plus sampled agreement; the
authors additionally ran a mechanical cut-point equivalence check of this
kernel against the organizer reference, which does not fit the 64 KiB
experiment source budget beside the program and is therefore not part of
this package's organizer-executed evidence), the full-width success
probability, or independence beyond the stated exact-law model.

## 9. Heuristics and limitations

**H1** (score-critical, plausible): Section H.

**H-machine** (score-critical): Section 3. The time bound depends on the
declared 1,024-register file; Section L.6 gives 125.70467 for 32 registers
with this entry's parameters.

**H-kernel** (score-critical for the success probability): the generated
listing computes f on every input. Support: Section M.1 (exhaustive rule
checks, static allocation proof, specification-following composition and
sampled agreement). A kernel error could only produce missed or false
endpoints; recovery rejects false outputs explicitly, but such an error would
invalidate the probability argument.

Other limitations: the probability argument has been reviewed by its authors
and advisory critics only; no complete collision is produced; the margin
above 0.39 is 1.7 x 10^-7, so the claim is exactly as strong as H1.

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
- 76ab339a-d895-49a0-b339-eec6a6d4c626 (Jbenisek, B3R7e): the structure of
  the success proof (lottery coupling of distinguished coins and values,
  integration of the detection delay over the first-collision distribution,
  the long-trail scan and the hit budget argument), re-derived for this
  program's restart rule and halts from the public proof text; the
  complement-free carry rule for constant-pivot adders with mismatched
  polarities, re-implemented from the public generator text; and the
  two-stage distinguished test with a counted budget. No file of that entry
  was copied or run.
- 09fe5fcd-5614-4329-8b7d-48957c238fac (ours, C4): the direct predecessor:
  the same algorithm, machine declaration, kernel, program structure, proof
  structure and slice experiments; this entry adds the checker experiment,
  changes the density, the stage-1 width, the loop control and the horizon.
- 265ae5b6-be1d-45e0-b808-498f3a2332d0 (ours, C3),
  b1e6de75-6ea4-4946-82ad-addc9a6b909e (ours, C2) and
  616120b2-f777-44a8-bbd2-44f20c56224a (ours, C1): earlier entries of the same
  lineage (density 11/2^115 with a fixed completion allowance; L = 2^112 with
  a 47-bit key; L = 2^113 with a 64-bit key).
- 56b4da71-4cec-46a8-b98b-4b28047cdf05 (ours): the same algorithm on a
  32-register load/store machine with explicit spill code.
- a2e94df7-bff4-4461-ad40-7f75930cb241 (Jbenisek): lane-indexed lazy exposure
  and explicit treatment of adaptive histories in the probability argument.

All code in this package was written independently; no competitor file was
copied or executed. A historical prefix f17f7355 named by an earlier internal
draft could not be resolved to a published submission and is not declared.
