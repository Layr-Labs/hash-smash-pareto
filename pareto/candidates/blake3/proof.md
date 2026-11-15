# BLAKE3, 3 rounds: own bit-sliced 256-lane birthday search (b3r3-omp-v1)

Own construction and own code (R-30): generator, circuit, ledger, controls and package
were written for this entry; no file of another solver was used or run. The notes of
other entries were read as data for the gate convention only (see section 3).

## 1. Target and what is claimed

Target `blake3-r3-prefix-v1`: complete unkeyed BLAKE3-256 with the prefix rounds
0..2 kept in every chunk, parent and root compression, standard IV, standard tree,
standard padding, full 256-bit digest. This entry claims an ordinary collision,
`rounds = 3`, `time_log2` = 124.78037 target compressions (the ledger's 124.78036,
rounded up at the fifth decimal), `memory_log2_bytes` =
19.38539 (the ledger's unrounded 19.38538, rounded up at the fifth
decimal), success probability at least 0.39 and score
`normalizedTimeMemoryLog2` = 124.78036.

The construction is a generic birthday search on the complete digest. No differential
or structural property of the three rounds is used.

## 2. The map F and the colliding messages

F operates on a 256-bit walk state x and returns the full digest of the 64-byte
message K || x, K = 0^32:

    F(x) = C(IV, K || x, counter = 0, block_len = 64, flags = 11),  11 = 1|2|8,

where C is one 3-round BLAKE3 compression and 11 = CHUNK_START|CHUNK_END|ROOT. A
64-byte message is exactly one chunk with one block, so the digest is one root
compression and F costs exactly one target compression per evaluation. The walk is
x[i+1] = F(x[i]). A collision F(x) = F(y) with x != y gives two distinct 64-byte
messages with equal complete digests, which is the claimed relation: messages
K || x and K || y are distinct, both in the domain, and their complete 3-round
digests agree on all 256 bits. No certificate is supplied because finding the
witness needs the full 2^128 search; the claim is the resource bound, as in every
other entry on this row.

The prefix K = 0^32 is not advice: it is a fixed part of the declaration, so
`nonuniform_advice_log2_bytes = 0`.

## 3. The emitted program and the gate convention

The generator emits a straight-line program over 256 independent walks (lanes).
Every 32-bit word of the compression is 32 separate 256-bit plane registers, so one
plane operation is exactly one 256-bit word operation of collision-frontier-v5.

Prices used and counted by the generator, not by hand:

| item | price |
| --- | --- |
| XOR, AND, OR, NOT on one plane | 1 gate |
| rotation of a 32-bit word | 0 (plane renaming) |
| register move / copy | 0 (SSA renaming, no moves emitted) |
| constant plane (uniform bit) | 0 (immediate) |
| 2-addend 32-bit add, both addends varying | 154 = 5n-6 (half adder at bit 0, full adders, top carry discarded) |
| 2-addend add with a constant addend | only the columns from the first nonzero bit: ~2 gates/column |
| 3-addend add a+b+m | two 2-addend adds (308 when all vary; one ripple when m is a constant) |
| feed-forward | 8 XOR words = 256 |

Every gate is a 1-bit-wide, 256-lane Boolean operation, i.e. one 32-byte register
operation, the same unit the organizer counter uses for one 32-bit word operation
in the scalar reference. Additions are the only multi-gate primitives; their price
is emitted, not modelled: the generator builds the ripple columns (2 gates at bit
0, 5 per full-adder column, no top carry) and folds every constant plane. Dead
gates (the discarded carry columns of an add, unused fold products) are removed by
a backward liveness pass before the program is counted.

Round 0 of F runs on constants only: the initial state is
IV(0..7) || IV(0..3) || counter || block_len || flags, all constant, and the four
diagonal G calls use the constant message words K = 0^32. Those four calls fold to
zero gates. The four column calls of round 0 add the variable walk words to
constant-derived state words; round 0 as a whole (four free diagonal calls plus
those four column calls) costs 2951 gates. Rounds 1 and 2 cost 7184
and 7184 gates.

| round | gates |
| --- | ---: |
| 0 | 2951 |
| 1 | 7184 |
| 2 | 7184 |
| feed-forward | 256 |
| **step, 256 lanes** | **17575** |

The generator is round-parametric: at seven rounds it emits 46311 gates
(xor 22778, and 15610, or 7675, not 248) and that net reproduces
`verifier/blake3.py` at rounds = 7 on 256 lanes with 0 differences, so nothing is
tuned to three rounds. Placing the adder census beside the published r7 step of the
row's reference program (44,266 gates, same 154 / 308 prices and the same count of
all-variable three-addend adds) leaves a residual of about 4.6% per step, which the
note of that entry attributes to its 9-gate three-addend column; this generator does
not implement that column.

Gate mix of the emitted step (printed by the generator): xor 8602, and 5850,
or 2875, not 248; 17575 instructions. Program sha256 (canonical JSON of the
instruction list) = `a05d88c2acd44cb303ff34a1090c078d28281fefa2d1d5e44f9e9fa5ea074f89`. Peak live plane registers: 772. Registers are
allocated by liveness; no spill is needed, so the main loop contains no loads and
no stores. The eight output words of one batch are the message words of the next
batch, so chaining costs no moves.

## 4. Ledger: total work and time_log2

All rows are computed by `ledger.py` from the emitted program:

| row | value |
| --- | --- |
| gates per 256-lane batch | 17575 |
| per-batch control (counter, branch, DP filter stages) | 15 |
| operations per batch | 17590 |
| operations per F-evaluation | 68.710938 |
| evaluations charged, Q | 339 177 502 524 764 998 185 226 066 825 424 143 433 (log2 127.99530809) |
| batches B = ceil(Q/256) | 1 324 912 119 237 363 274 161 039 323 536 813 061 |
| main loop, B x 17590 | 23 305 204 177 385 219 992 492 681 701 012 541 742 990 |
| distinguished-point handlers | 261 288 |
| recovery and trail alignment (bound) | 17 179 869 184 |
| setup: generator, folding, DCE, verification runs (bound) | 1 073 741 824 |
| **total N (word operations)** | **23 305 204 177 385 219 992 492 681 701 030 795 615 286** |
| reference operation cost C (blake3-r3) | 638 |
| **time_log2 = log2(N / C)** | **124.78036** |

N is an integer; the decimal value above is obtained by dividing by C = 638 (the
organizer counter's own count for one 3-round compression, recomputed here as
`pareto.targets.reference_cost('blake3', 3)` = 638) and taking log2 with 80-digit
decimal arithmetic: 124.78036333414352379856525203758480111139863940837206974822492467245996290372375.

## 5. Memory account

| item | bytes |
| --- | ---: |
| code: 17575 gate records x 4 | 70 300 |
| distinguished-point table: 2^16 slots x 8 (50-bit key + 14-bit trail) | 524 288 |
| registers: 772 planes x 32 | 24 704 |
| counters, limits, trail bookkeeping | 65 536 |
| **total** | **684 828 = 2^19.38538** |

The memory term of the score is max(0, 19.38538 - 20) = 0.00000.

## 6. Success probability

The search is 256 interleaved walks of the map, so it evaluates Q points in total.
It succeeds when two evaluated points coincide, i.e. when a walk closes a cycle: the
two predecessors of the closing point are then distinct map inputs with equal
images, which the recovery step extracts. For a random mapping on 2^256 points the
probability that Q evaluations contain such a repeat is 1 - exp(-Q(Q-1)/2^257), and
the same law is what the 256-walk union uses under the independence part of H1. The charged Q is the least integer that
reaches 0.39 plus a 0.0015 margin for the losses listed below, and gives
P = 0.391500000000 > 0.39. A distinguished point is a point whose 113 low
digest bits are all zero (density 2^-113). Two trails that meet anywhere
continue identically, so the merge is seen at the next distinguished point on both
trails. The table holds Q x 2^-113 = 32 661 entries in 2^16 slots (load
0.4984), i.e. every distinguished point of the search is stored, so no merge is
missed; 8-byte keys truncated to 50 bits can cause false matches, which the recovery
row pays for. Restarts, unfinished trails and the DP filter's branch are charged in
the per-batch control row and in the recovery bound. The 0.0015 margin covers
trails that end before reaching a distinguished point, repeats inside one trail and
truncated-key false matches. No amplification is needed or claimed.

## 7. Controls, all run on this machine

(a) Emitted program vs a plain scalar 3-round reference (section 2 formula,
written independently of the generator): 4096 chains x 16 chained steps =
65536 evaluations, 4096 lanes per batch x 16 batches, 0 lane differences.

    (a) emitted net vs plain 3-round reference: lanes 256 steps 4 evaluations 1024 lane-diffs 0
    (a2) emitted net vs plain 3-round reference: chains 4096 x 16 steps evaluations 65536 lane-diffs 0

(b) The same reference and the emitted program against the repository verifier
(`verifier/blake3.py`, rounds = 3) on complete messages K || x:

    (b) own scalar reference vs repo verifier/blake3.py (rounds=3): messages 512 diffs 0
    (b2) emitted net vs repo verifier/blake3.py (rounds=3): lanes 256 diffs 0

(c) Regeneration and ledger determinism: three independent builds give the same
program sha256, and three ledger runs are byte-identical:

    (c1) program regeneration: 3 builds sha256 equal True a05d88c2acd44cb303ff34a1090c078d28281fefa2d1d5e44f9e9fa5ea074f89
    (c2) ledger regeneration: 3 runs byte-identical True sha256 beae259bf7819514ee524e0079bd442178a9625d7fde3faa303ac111658932f4

(d) The normalized score is re-derived with the repository's own scoring code,
`pareto.scoring.normalized_score('blake3', metrics)` with metrics timeLog2 =
124.78036, memoryLog2Bytes = 19.38538: 124.78036.

(e) Negative control: a single gate of the emitted program is changed (xor <-> and)
at three positions; the same comparison that reports 0 differences above then
reports differences and rejects the program:

    (neg) single-gate corruptions at 3 positions: lane-diffs [433, 338, 426] rejected True

(f) Independent re-derivation: `dpcheck.py` does not import the ledger module. It
recounts the emitted instruction list, solves the success-probability equation by
integer bisection on 60-digit decimal arithmetic, checks the table bound and
recomputes the score with the repository's `scalar_score`:

    gates 17575 ops/batch 17590 ops/eval 68.7109
    Q 339177502524764998185226066825424143433 (P = 0.391500000000 >= 0.3915) log2 Q 127.99530809
    batches 1324912119237363274161039323536813061 total 23305204177385219992492681701030795615286
    time_log2 124.78036  memory_log2 19.38538  term 0.00000
    table: dps 32661 <= slots/2 32768 -> True
    score(own) 124.78036 score(repo scalar_score) 124.78036
    DP accounting re-derived independently: OK

(g) Toy-width end-to-end run of the search itself (walk, distinguished-point table,
restarts, recovery) driven by the emitted 256-lane net, every recovered pair
rechecked against the repository verifier:

    toy width 18 dp_low 4 lanes 256 trials 64 pairs 38 bad 0 aborted 26 evaluations 96256 evals/trial 1504 expected 642
    toy width 20 dp_low 4 lanes 256 trials 64 pairs 50 bad 0 aborted 14 evaluations 165376 evals/trial 2584 expected 1283

At toy width the distinguished-point lag is a large fraction of the birthday length
(2^4 against 2^9..2^10), which is why the evaluations per trial exceed the ideal
1.25 x 2^(n/2); at width 256 with density 2^-113 the same lag is 2^-113 relative to
2^128 and is inside the charged Q.

(h) Negative codegen result, kept for the record: a random scan of the constant
prefix K (65536 candidates, priced with the emitter's own constant rule) never beats
K = 0^32 - every nonzero K pays the two later rounds' constant ripples, and the
round-0 constant work of a random K is not lower. The generator's 17,575 gates are
therefore the K = 0 build; the row leader's lower round-0 constants come from a
2^40-scale scan with a per-column option search that this generator does not
implement.

(i) Round parametricity: the same generator at rounds = 7 emits 46311 gates and
matches `verifier/blake3.py` at rounds = 7 for 256 lanes, 0 differences.

A tampered claim is rejected too: `mkpackage.py --check` recomputes the ledger and
refuses any claim whose time_log2 or memory_log2_bytes is below the recomputed
value; a claim with time_log2 = 124.0 (the optimistic guess that ignores the adder
price, i.e. charging one operation per add) fails that check.

## 8. Premises, scope and limits

H1 (score-critical, declared, not proved): the 3-round chain F behaves as a random
mapping on 2^256 points for the quantities the search uses: no exploitable
collision or cycle structure, trails merge like independent random paths, and
distinguished points are independent events. This cannot be tested at width 256;
the controls above test the program, not the premise. If the real pair-merge rate
were lower than the model, the deficit costs 0.5 log2(1/(1-eps)) bits, i.e. 0.00725
bit at eps = 0.01 and 0.0760 bit at eps = 0.10.

H3 (supporting, declared): the machine convention of section 3 - 256-bit plane
registers, gate prices, 154-gate two-addend adders, free plane-renaming rotations,
SSA with no moves, a 772-plane register file, no loads or stores in the main
loop, 4-byte gate records. With a register file of fewer than about 40 planes the
loop would need spills and the bound would rise.

Limits of this entry: the circuit is not claimed minimal; the row leader
(33f00b84, [3, 124.68326]) is lower by 0.09711 bit, because its generator finds a
cheaper adder family and a scanned constant block that this generator does not
implement. No differential attack is claimed: at 3 rounds only the generic
birthday bound is available to us. No witness pair is provided; the claim is a
resource bound, as on the rest of this row.

## 9. Reproduce

    python3 bsgen.py --gates          # emitted step: gate count and mix
    python3 controls.py               # (a), (a2), (b), (b2), (c1), (neg)
    python3 ledger.py                 # every row of section 4, 5 and 6
    python3 dpcheck.py                # independent re-derivation of (d) and (f)
    python3 toy.py                    # (g), toy-width search on the emitted net
    python3 scan_key.py 65536         # (h), constant-prefix scan
    python3 mkpackage.py --check      # claim vs recomputed ledger, then the repo checker

The generator is deterministic: no randomness enters the program.
