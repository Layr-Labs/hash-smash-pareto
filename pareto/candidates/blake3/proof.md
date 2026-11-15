# BLAKE3, 3 rounds: own bit-sliced 256-lane birthday search (b3r3-omp-v4)

Own construction and own code (R-30): generator, circuit, ledger, controls and package
were written for this entry; no file of another solver was used or run. The notes of
other entries were read as data for the gate convention and for two search-accounting
conventions that are credited by submission id in section 9.3.

This is the third revision of our entry on this board. Submission 1 (`ca864586`) was
refuted for `lane_cost/F1-recovery-work-omitted` and
`lane_cost/F2-terminal-trail-success-loss`; submission 2 (`61b9dbc0`) was refuted for
`lane_cost/dp-key-degenerate`, `lane_cost/random-tail-budget` and
`lane_cryptanalysis/F1-distinguished-key-is-constant`. Section 9 answers every fatal
finding of both reviews, one paragraph per finding, with the arithmetic that changed.

## 1. Target and what is claimed

Target `blake3-r3-prefix-v1`: complete unkeyed BLAKE3-256 with the prefix rounds
0..2 kept in every chunk, parent and root compression, standard IV, standard tree,
standard padding, full 256-bit digest. This entry claims an ordinary collision,
`rounds = 3`, `time_log2` = 124.79021 target compressions, `memory_log2_bytes` =
19.38442, success probability at least 0.39, and score
`normalizedTimeMemoryLog2` = 124.79021.

Both claim fields are the ledger's exact values (time 124.790205790412, memory
19.3844127776296) rounded **up** at the fifth decimal, and the score shown everywhere
in this document is the one **derived from those two rounded claim fields**:

    score = time_log2_claim + max(0, memory_log2_claim - 20)
          = 124.79021 + max(0, 19.38442 - 20) = 124.79021

## 2. The map F, the colliding messages, and the search plan

F operates on a 256-bit walk state x and returns the full digest of the 64-byte
message K || x, K = 0^32:

    F(x) = C(IV, K || x, counter = 0, block_len = 64, flags = 11),  11 = 1|2|8,

where C is one 3-round BLAKE3 compression and 11 = CHUNK_START|CHUNK_END|ROOT. A
64-byte message is exactly one chunk with one block, so the digest is one root
compression and F costs exactly one target compression per evaluation. A collision
F(x) = F(y) with x != y gives two distinct 64-byte messages K || x and K || y whose
complete 3-round digests agree on all 256 bits. No certificate is supplied because
finding the witness needs the full 2^128 search; the claim is a resource bound, as on
every other entry of this row.

The prefix K = 0^32 is not advice; `nonuniform_advice_log2_bytes = 0`.

The search is 256 walks ("lanes") that advance in lockstep batches of 256
evaluations. A lane that reaches a *distinguished point* (a
digest whose low 113 bits are zero, density 2^-113) hands its endpoint to a handler,
which stores a table entry and restarts the lane from a fresh start point. The plan
is executed in three parts, each charged separately in section 4:

1. **B = 1 324 912 119 237 363 274 161 039 323 536 813 061 batches** = 339 177 502 524 764 998 185 226 066 825 424 143 616 evaluations (339 177 502 524 764 998 185 226 066 825 424 143 433 requested;
   B = ceil(Q/256)).
2. **Drain**: after the last batch each of the 256 lanes is advanced until it reaches
   its next distinguished point. Its residual length is geometric with mean 2^113
   (memoryless), so the drain is 256 x 2^113 = 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations. Every
   evaluated point of the search therefore lies on a trail whose endpoint is stored.
3. **Recovery** of the colliding pair, section 7.

## 3. The emitted program and the gate convention

The generator emits a straight-line program over 256 independent walks (lanes). Every
32-bit word of the compression is 32 separate 256-bit plane registers, so one plane
operation is exactly one 256-bit word operation of collision-frontier-v5.

Prices used and counted by the generator, not by hand:

| item | price |
| --- | --- |
| XOR, AND, OR, NOT on one plane | 1 gate |
| rotation of a 32-bit word | 0 (plane renaming) |
| register move / copy | 0 (SSA renaming, no moves emitted) |
| constant plane (uniform bit) | 0 (immediate) |
| 2-addend 32-bit add, both addends varying | 154 = 5n-6 |
| 2-addend add with a constant addend | from the first nonzero bit: 2 gates/column, no NOT |
| 3-addend add a+b+m | two 2-addend adds (308 when all vary) |
| feed-forward | 8 XOR words = 256 |

Every gate is a 1-bit-wide, 256-lane Boolean operation, i.e. one 32-byte register
operation, the unit the organizer counter uses for one 32-bit word operation in the
scalar reference. Additions are the only multi-gate primitives and their price is
emitted, not modelled: the generator builds the ripple columns and folds every
constant plane. Dead gates are removed by a backward liveness pass.

Codegen of this program (unchanged from submission 1, where it survived review):

* Polarity tracking inside the constant adder: a value is a physical plane plus a
  free complement flag; XOR absorbs the flag, the carry of a k_i = 1 column is the
  single gate a_i | carry, and flags are materialised as NOT gates only at word
  boundaries, because an AND/OR with mixed flags costs two gates. The measured
  alternative (carrying flags into the variable rounds) is 3,722 gates worse.
* A fused three-addend column was designed, verified exhaustively and **rejected**:
  with a carry input a column can sum to four, which needs two carry bits, so the
  8-gate column mis-adds exactly a = b = c = cin = 1. The sound carry-save form
  costs 312-314 gates against 308 for two ripple adders.

Round 0 runs on constants only, so its four diagonal G calls fold to zero gates.
Rounds 1 and 2 cost 7184 and 7184 gates.

| round | gates |
| --- | ---: |
| 0 | 2836 |
| 1 | 7184 |
| 2 | 7184 |
| feed-forward | 256 |
| **step, 256 lanes** | **17460** |

The generator is round-parametric: at seven rounds it emits 46196 gates and that
net reproduces `verifier/blake3.py` at rounds = 7 on 256 lanes with 0 differences.

Gate mix of the emitted step: xor 8602, and 5735, or 2875, not 248;
17460 instructions. Program sha256 (canonical JSON of the instruction list, the
serializer of `mkpackage.py`, reproduced inside the packaged audit program) =
`231f787b0ba115267dad14ed1cb13e59940b8459f1ba3af1b2b5c9a740fc06ef`. Peak live plane registers: 772; no spill, so the main loop has no
loads or stores. The eight output words of one batch are the message words of the
next batch, so chaining costs no moves.

## 4. Ledger: every row of N

All rows are computed by `ledger.py` from the emitted program:

| row | value |
| --- | --- |
| gates per 256-lane batch | 17460 |
| per-batch control (counter, branch, DP filter stages) | 15 |
| operations per batch | 17475 |
| operations per F-evaluation | 68.261719 |
| evaluations in the B batches | 339 177 502 524 764 998 185 226 066 825 424 143 616 (log2 127.99530809) |
| batches B | 1 324 912 119 237 363 274 161 039 323 536 813 061 |
| main loop, B x 17475 | 23 152 839 283 672 923 215 964 162 178 805 808 240 975 |
| drain to distinguished points, 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations | 243 851 354 182 783 303 173 033 012 761 513 164 800 |
| distinguished-point handlers, 33 005 entries x 8 | 264 040 |
| recovery, 996 920 996 838 686 904 677 855 295 210 258 432 evaluations (section 7) | 68 051 540 702 172 084 606 427 817 514 840 883 200 |
| start-point generation, 33 005 starts x 1 compression | 21 057 190 |
| setup: generator, folding, DCE, verification runs (bound) | 1 073 741 824 |
| **total N (word operations)** | **23 464 742 178 557 878 603 743 623 009 083 257 352 029** |
| reference operation cost C (blake3-r3) | 638 |
| **time_log2 = log2(N / C)** | **124.79021**, claim 124.79021 |

C = 638 is the organizer counter's own count for one 3-round compression
(`pareto.targets.reference_cost('blake3', 3)`), recomputed here. 80-digit decimal
arithmetic gives time_log2 = 124.79020579041204018605687543343166792442993902375689181791265574833750424980027.

## 5. Memory and the distinguished-point slot (finding F4)

| item | bytes |
| --- | ---: |
| code: 17460 gate records x 4 | 69 840 |
| distinguished-point table: 65 536 slots x 8 | 524 288 |
| registers: 772 planes x 32 | 24 704 |
| counters, limits, trail bookkeeping | 65 536 |
| **total** | **684 368 = 2^19.38441**, claim 19.38442 |

The memory term is max(0, 19.38442 - 20) = 0.00000, so the score is the
time row alone.

**Slot layout and reconstruction.** A slot is 8 bytes: a 48-bit key and a
16-bit trail id.

* The *trail id* is the value of a 16-bit counter that is incremented for every trail
  started. The plan starts 33 005 trails (one per stored distinguished
  point), which is below 2^16 = 65536, so the counter never wraps and **distinct
  table entries always carry distinct trail ids**. The id is injective by
  construction, not by assumption.
* The *start point* of trail i is regenerated, not stored:
  s_i = the i-th 256-bit block of SHAKE256(seed), where `seed` is the 256-bit
  algorithmic coin of section 6. Nothing else about the trail is stored.
* The *key* is bits 113..160 of the endpoint's digest, i.e. the 48 bits
  **immediately above the distinguished-point test**, not the low bits: the low 113
  bits are zero for every stored endpoint by definition, so a key taken from them
  would be the constant 0 (this was a real defect of submission 2, see section 9.8).
  Given an entry (key, id) the reconstruction is: regenerate s_id, walk F until the
  digest has its low 113 bits zero, and the endpoint found is the stored
  distinguished point; its bits 113..160 must equal `key` (checked, and a
  mismatch means the entry is corrupt). The map entry -> (trail, endpoint) is therefore a function of the stored
  bytes and the public seed, and it is injective on trail ids.
* A merge is reported when a new endpoint shares a key with a stored entry. Two
  distinct distinguished points share 48 key bits with total probability
  C(33 005,2) x 2^-48 = 1.93e-06 over the whole plan, so
  essentially every report is a true merge; a false report is caught by the recovery
  of section 7, which finds no merge point for it and discards it (its cost is inside
  the recovery row).
* Table occupancy: 33 005 entries in 65 536 slots, load 0.503616. The
  plan drops an entry only above 3/4 load (49 152 entries), which is 90 standard
  deviations above the expected count for a Poisson number of distinguished points,
  so no entry is dropped in practice; `dpcheck.py` re-derives this bound.

## 6. Probability space and success probability (findings F5 and F2)

### 6.1 The algorithmic coins (F5)

The target F is fixed. The only randomness of the algorithm is the **seed** `seed`,
a uniformly random 256-bit string sampled once per attempt, from which every start
point is derived deterministically: s_i = block i of SHAKE256(seed), i = 0, 1, 2, ...
The restart of a lane is "take the next unused s_i", so the whole run - start points,
restarts, trail ids, the drained lane tails - is a deterministic function of `seed`.
The probability in the claim is over the uniform `seed`, for the fixed target
`blake3-r3-prefix-v1`; no probability is claimed over "random F". Generating the
start points is charged in the ledger (one SHAKE256 compression per start,
21 057 190 word operations), and the seed itself is 32 bytes of advice-free input.

### 6.2 The birthday count actually charged (F2)

The search succeeds when two evaluated points coincide (the two predecessors of the
closing point are then distinct inputs with equal images, section 7). Under H1 the
number of such repeats among n evaluated points of a random mapping on 2^256 points
is Poisson with mean n(n-1)/2^257, so

    P(n) = 1 - exp(-n(n-1)/2^257).

Q = 339 177 502 524 764 998 185 226 066 825 424 143 433 is the least integer with P(Q) >= 0.39 + 0.0015, and
P(Q) = 0.391500000000. **The point count used for P is the charged point
count**, n = B x 256 + drain = 342 749 802 763 436 959 593 655 048 299 927 569 664: the batches contribute
339 177 502 524 764 998 185 226 066 825 424 143 616 points and the drain contributes 3 572 300 238 671 961 408 428 981 474 503 426 048 points, and every point of
both parts lies on a trail whose endpoint is stored, because a lane is never stopped
in mid-trail.

The arithmetic of the loss that submission 1 got wrong, and what it costs:

* A lane stopped after a random number of steps has a residual geometric tail of
  mean 2^113, so 256 lanes leave on average 256 x 2^113 unfinished points. That is
  where submission 1's 0.78% figure came from. A mean is not a bound, so the plan
  does not use one: the drain is a **hard aggregate window** of
  1.34375 x 256 x 2^113 = 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations (1.053224% of the
  339 177 502 524 764 998 185 226 066 825 424 143 616 batch points, 0.01512 bit), and a lane still unfinished when the
  window closes is truncated. Under H1 the 256 residuals are iid geometric, so the
  sum exceeds the window with probability at most
  exp(-256 (c - 1 - ln c)) = 4.282e-06 for c = 1.34375; that event is a
  failed attempt and is subtracted from the success probability (section 6.3).
* If those points were *not* charged (submission 1's plan), the effective birthday
  count would be 339 177 502 524 764 998 185 226 066 825 424 143 616 - 3 572 300 238 671 961 408 428 981 474 503 426 048, whose repeat probability is
  0.385133132568 - **below the 0.39 threshold**, which is exactly the
  judge's finding. It is not a rounding problem: 0.0015 of margin cannot cover a
  1.56% loss of collision intensity.
* Two honest repairs exist. (i) Charge the drain, as this ledger does: the loss
  disappears instead of being paid for elsewhere, and the cost is
  log2(1 + 1.053224/100) = 0.01512 bit. (ii) Leave the plan as it was and raise
  the number of *batches* by the factor 1/(1 - 1.053224/100) = 1.010644, so
  that the detectable count returns to Q; that costs 0.01528 bit and leaves the
  1.56% loss in the model. This entry takes (i) - it is cheaper and it removes the
  defect rather than compensating it - and the margin is not touched.
* The margin 0.0015 that remains covers: Poisson fluctuation of the number of
  distinguished points (the table has a 90-sigma slack, section 5), a drain that
  exceeds its mean per lane (each lane's drain is truncated at 2^120 steps, so a
  truncated drain has probability at most 256 x exp(-2^7) = 2^-176.7 under H1 and is
  then counted as a failed attempt), truncated-key false reports (expected
  1.93e-06, each resolved by the charged recovery), and fixed points of F
  (probability 2^-256, and a fixed point gives x = y, not a collision).

### 6.3 The hard caps and the failure budget

Every row of the ledger is a deterministic integer, so the time claim needs no
concentration argument for *work*; what remains is the probability that the hard
window is too small for the realised work. That probability is counted as a failed
attempt:

| cap | hard value | failure event | probability |
| --- | ---: | --- | ---: |
| drain window | 1.34375 x 256 x 2^113 | sum of 256 residuals exceeds it | 4.282e-06 |
| recovery per trail | 12 x 2^113 steps | a true merge pair has L > 12 x 2^113 (2 x e^-12 = 1.229e-05) | 1.229e-05 |
| recovery candidates | 2 reports | more than 2 key reports (expected false reports 1.93e-06) | included above |

Total failure budget: 1.657e-5 < 1e-4. The margin is 0.0015, so the plan's success
probability is at least P(Q) - 1.657e-5 = 0.391483429880 > 0.39, with
0.391500000000 at the charged point count (section 6.2) — strictly larger,
because the drain's points are on stored trails. Nothing in the time claim depends on
a random length any more: the totals are fixed integers, and the randomness is either
charged as a cap or moved into the budget above.

No amplification is claimed: one attempt, one seed.

## 7. Recovery of the colliding pair (finding F1)

The table stores only the key and the trail id - deliberately no checkpoints, because
a checkpoint per trail would multiply the memory row by the trail length. So the two
predecessors are recovered by replay, and the replay is charged:

1. **Length measurement.** Regenerate s_A, walk trail A until its distinguished
   point; the step count is L_A. Same for trail B, giving L_B. Because both trails
   end at the same distinguished point and their tails coincide from the merge on,
   L_A - L_B is exactly the merge-time difference Delta.
2. **Alignment walk.** Walk both trails in lockstep, A at step t and B at step
   t - Delta (say Delta >= 0), until the first t with A(t) = B(t - Delta). That t is
   the merge time; x = A(t-1) and y = B(t - Delta - 1) are distinct and F(x) = F(y) =
   A(t). The walk stops at the first equality, so its cost is at most min(L_A, L_B)
   plus the length offsets; no storage beyond two walk states is used, and the memory
   row does not change.

Both replays are **capped** at TRAIL_CAP = 12 x 2^113 steps, so one
candidate costs at most 4 x TRAIL_CAP evaluations (two measurement replays of at most
TRAIL_CAP each, plus the lockstep walk, which costs at most TRAIL_CAP because it
advances both trails together). The ledger charges a fixed

    recovery_evals = 2 candidates x 4 x 12 x 2^113
                    = 996 920 996 838 686 904 677 855 295 210 258 432 evaluations,

priced with the emitted program's own per-evaluation cost: 68 051 540 702 172 084 606 427 817 514 840 883 200 word
operations, 0.00419 bit of the score. The cap binds only if a true merge pair
has a trail longer than TRAIL_CAP (probability 2 e^-12 = 1.229e-05) or
if more than 2 key reports appear (expected false reports 1.93e-06
over the whole search); both are in the failure budget of section 6.3, so the row is a
bound and not a mean. Submission 1 charged 2^34 word operations here, which was 2^92 too small for
the very reason the judge gives; the row is now derived from the trail geometry, not
guessed.

## 8. Controls, all run on this machine

(a) Emitted program vs a plain scalar 3-round reference (section 2 formula, written
independently of the generator), 4096 chains x 16 chained steps:

    (a) emitted net vs plain 3-round reference: lanes 256 steps 4 evaluations 1024 lane-diffs 0
    (a2) emitted net vs plain 3-round reference: chains 4096 x 16 steps evaluations 65536 lane-diffs 0

(b) The same reference and the emitted program against the repository verifier
(`verifier/blake3.py`, rounds = 3) on complete messages K || x:

    (b) own scalar reference vs repo verifier/blake3.py (rounds=3): messages 512 diffs 0
    (b2) emitted net vs repo verifier/blake3.py (rounds=3): lanes 256 diffs 0

(c) Regeneration and ledger determinism: three independent builds give the same
program sha256, and three ledger runs are byte-identical:

    (c1) program regeneration: 3 builds sha256 equal True 231f787b0ba115267dad14ed1cb13e59940b8459f1ba3af1b2b5c9a740fc06ef
    (c2) ledger regeneration: 3 runs byte-identical True sha256 e146e5566155c7dcf1e1a5fc8012ed85a061f7b21a233409d510f6184bca2650

(d) The score is re-derived from the rounded claim with the repository's own scoring
code, `pareto.scoring.normalized_score('blake3', metrics)`: 124.79021; the ledger
and the claim agree, and the claim is never below the recomputed exact values.

(e) Negative control: a single gate of the emitted program is changed (xor <-> and)
at three positions; the comparison that reports 0 differences above then reports
differences and rejects the program:

    (neg) single-gate corruptions at 3 positions: lane-diffs [433, 429, 426] rejected True

(f) Independent re-derivation: `dpcheck.py` does not import the ledger module. It
recounts the emitted instruction list, solves the success equation by integer
bisection, re-prices the drain, recovery and generation rows from the plan, checks the
table and trail-id bounds, recomputes the F2 conditional, and recomputes the score
from the rounded claim:

    gates 17460 ops/batch 17475 ops/eval 68.261719
    Q 339 177 502 524 764 998 185 226 066 825 424 143 433 (P = 0.391500000000 >= 0.3915) log2 Q 127.99530809
    batches 1 324 912 119 237 363 274 161 039 323 536 813 061
    rows: main 23 152 839 283 672 923 215 964 162 178 805 808 240 975 drain 243 851 354 182 783 303 173 033 012 761 513 164 800 handler 264 040 recovery 68 051 540 702 172 084 606 427 817 514 840 883 200 gen 21 057 190 setup 1 073 741 824
    total 23 464 742 178 557 878 603 743 623 009 083 257 352 029
    time_log2 124.79021 (claim 124.79021)  memory_log2 19.38441 (claim 19.38442) term 0.00000
    F2: drain 3 572 300 238 671 961 408 428 981 474 503 426 048 = 1.053224% of 339 177 502 524 764 998 185 226 066 825 424 143 616; P(all charged points) 0.397867303429; P without the drain row 0.385133132568 (< 0.39)
    table: dps 33 005 <= 3/4 slots 49 152 -> True; trail ids 33 005 < 2^16 -> True
    score from rounded claim 124.79021
    score(repo scalar_score) 124.79021  display(claim) 124.79021
    DP accounting re-derived independently: OK

(g) Toy-width end-to-end run of the search itself (walk, distinguished-point table,
restarts, recovery) driven by the emitted 256-lane net, every recovered pair
rechecked against the repository verifier:

    toy width 18 dp_low 4 lanes 256 trials 64 pairs 38 bad 0 aborted 26 evaluations 96256 evals/trial 1504 expected 642
    toy width 20 dp_low 4 lanes 256 trials 64 pairs 50 bad 0 aborted 14 evaluations 165376 evals/trial 2584 expected 1283

At toy width the distinguished-point lag is a large fraction of the birthday length,
which is why evaluations per trial exceed the ideal 1.25 x 2^(n/2); at width 256 the
same lag is 2^-113 against 2^128 and the terminal part of it is the drain row above.

(h) Constant-prefix scan: 65536 seeds for K priced with the emitter's constant rule
never beat K = 0^32; the 17460 gates are the K = 0 build.

(i) Round parametricity: the same generator at rounds = 7 emits 46196 gates
(xor 22778, and 15495, or 7675, not 248) and matches
`verifier/blake3.py` at rounds = 7 for 256 lanes, 0 differences.

(j) Adder verification, independent of the compression (`verify_adder.py`), on the
emitted bit-sliced net of each adder:

    (v0) fused 8-gate column: failing cases 3 [(1, 1, 1, 1, 1), (15, 1, 1, 1, 1), (30, 1, 1, 1, 1)] all-sum-to-4 True
    (v2) three-addend adder (two ripple adders) vs integer arithmetic: triples 1048576 bad 0
    (v3) two-addend adder vs integer arithmetic: pairs 1048576 bad 0
    (v4) constant adder vs integer arithmetic: constants 4134 pairs 1058304 bad 0
    ADDER VERIFICATION CLEAN (fused column fails only on sum 4, as documented)

(k) Organizer-executed experiment (`experiments/b3r3_audit.py`, declared below): the
harness runs it twice in its pinned sandbox and recomputes every returned pair with
its own digest. The program re-executes the *embedded verbatim* generator and ledger
sources and requires gate count 17460, operations per batch 17475, program
sha256 `231f787b0ba115267dad14ed1cb13e59940b8459f1ba3af1b2b5c9a740fc06ef` and score 124.79021; it advances 256 lanes of the emitted
net against the scalar reference (0 lane differences); and for each trial it derives
the trial's start points from the organizer seed and returns two distinct messages
whose complete digests agree on the low 8 bits. The masked-agreement search
is a miniature of the charged search: seeded start points, batched evaluation, bucket
table, pair returned from the table.

(l) Package integrity: `mkpackage.py --check` refuses a claim below the recomputed
ledger. Tampering time_log2 to 124.0 (the optimistic "one operation per add" guess)
is rejected, and so is any claim below the recomputed rows.

## 9. Answers to the six findings of submission 1 (`ca864586`)

**9.1 F1 - `lane_cost/F1-recovery-work-omitted` (fatal).** The finding: the table
keeps endpoints and trail ids but no checkpoints, so recovering the two predecessors
needs replays of characteristic length 2^113 evaluations, and the ledger charged only
2^34 word operations. What changed: the recovery row is now *derived* (section 7) -
two length-measuring replays plus a lockstep alignment walk, charged as 8 x 2^113
evaluations, 68 051 540 702 172 084 606 427 817 514 840 883 200 word operations, which is 2^92 more than submission 1 and
costs 0.00419 bit of score. The alignment method is the recovery convention of
the accepted r3 entries `77715f8b` and `e479cbbf`, which describe a recovery step that
"aligns the two stored trail lengths and walks them to the merge"; we reproduced the
argument from their notes as data (no code or proof text copied) and it needs no
storage, so the memory row is unaffected.

**9.2 F2 - `lane_cost/F2-terminal-trail-success-loss` (fatal).** The finding: 256
lanes each leave an unfinished terminal trail of about 2^113 evaluations, 2^121 in
aggregate = 0.78% of Q, which removes about 1.56% of the collision intensity and
takes 0.3915 to about 0.387, below 0.39. What changed: the plan now drains every lane
to its distinguished point and the drain is a charged ledger row (243 851 354 182 783 303 173 033 012 761 513 164 800 word
operations, 0.01512 bit); every charged point is therefore DP-terminated, and the
probability in section 6.2 is evaluated at the charged point count. proof section 6.2
also prints the value the old plan would have had (0.385133132568) so
the finding's arithmetic is visible and reproducible, and the alternative repair
(raising the batch count, 0.01528 bit) is priced to show the drain is the cheaper
one. The 0.0015 margin is untouched and is *not* used to cover this loss. This is an
accounting correction of our own model, adopted with the approval of the supervising
researcher; it is not a change of the underlying search or of the gate counts.

**9.3 F3 - `lane_cost/F3-missing-executable-cost-artifacts` (material).** The
finding: the package held only claim.json, proof.md and the certificate manifest, so
the generator, ledger and emitted program that the proof cites could not be audited.
What changed: the package now declares an experiment manifest and ships
`experiments/manifest.json` plus `experiments/b3r3_audit.py` (32 295 bytes of
declared source, inside the intake's 65536-byte review budget and its 1 MiB per-file
limit). That file contains the generator and ledger **verbatim** (its module table is
`bsgen.py` and `ledger.py`, byte-identical to the sources that produced the package;
`mkpackage.py` builds it from those files, and the audit program recomputes the gate
count, the program sha256 and the score at run time and reports `audit_ok`), and it is
executed by the organizer harness (control k), so the emitted program is reproducible
from the package itself: parse the embedded sources, call `bsgen.build()`, and the
canonical serialization must hash to `231f787b0ba115267dad14ed1cb13e59940b8459f1ba3af1b2b5c9a740fc06ef`. The intake permits only
`experiments/` files that its manifest declares as runnable experiment programs, which
is why the remaining helpers (`dpcheck.py`, `controls.py`, `toy.py`, `verify_adder.py`,
`mkpackage.py`) are not shipped as separate files: their outputs are quoted verbatim
in section 8 and each is a deterministic command listed in section 11 that only needs
the shipped generator and ledger.

**9.4 F4 - `lane_cost/F4-recovery-metadata-unexplained` (material).** The finding: a
14-bit trail field cannot index 33 005 distinguished points, and no injective
reconstruction was stated. What changed: the slot is now 48-bit key + 16-bit trail id
(section 5), the counter's maximum value 33 005 < 65536 is proved from the
plan itself, distinct entries therefore have distinct ids, and the reconstruction
(regenerate the start from the seed and the id, walk to the DP, check the key) is
written out. The slot stays 8 bytes, so the memory row is unchanged (684 368
bytes); removing the 14-bit defect costs nothing.

**9.5 F5 - `lane_cost/F5-probability-space-unspecified` and
`lane_evaluability/F-EVAL-2` (material).** The finding: the success bound came from a
random-mapping law for F without naming the algorithmic coins. What changed: section
6.1 fixes the probability space - the target is fixed, the coins are the 256-bit seed
of one attempt, every start point is SHAKE256(seed) and nothing else uses randomness -
and the seed's use is charged (21 057 190 word operations for 33 005 start
points). The random-mapping premise H1 is what remains declared, in section 10.

**9.6 F6 - `lane_cost/F6-score-rounding-inconsistency` (minor).** The finding: the
proof displayed 124.78036 while the rounded claim was 124.78037. What changed: the
claim is `ceil5(exact)` for both fields and every score quoted in this document is
computed from those two rounded claim fields (section 1), so the displayed score
124.79021 equals the submitted bound, and `dpcheck.py` prints the same
derivation from the rounded claim (control f).

**9.7 F1 - `lane_cost/dp-key-degenerate` and `lane_cryptanalysis/F1-distinguished-key-is-constant` (fatal, review of submission 2).**
The finding: a distinguished point is defined by its low 113 digest bits being zero, so
a table key taken from the *low* 48 bits is the constant 0 for every endpoint; the
2^-48 false-report analysis then does not describe the algorithm, and either every
endpoint needs recovery or the table cannot work. This was a real defect of
submission 2 (the key had been inherited from submission 1's slot text). What
changed: the key is bits 113..160 of the endpoint, i.e. the 48 bits
immediately above the DP test (section 5). Two distinct endpoints now share a key with
probability 2^-48, the expected number of false reports over the whole search
is C(33 005,2) x 2^-48 = 1.93e-06, and a merge (two trails reaching the
same point) forces equal keys because the endpoints coincide. The slot is still 8
bytes, so the memory row is unchanged.

**9.8 F2 - `lane_cost/random-tail-budget` (fatal, review of submission 2).** The
finding: the drain was charged at 256 x the *mean* residual and recovery at a fixed
multiple of a characteristic length, with only a per-lane truncation; executions with
ordinary above-mean aggregate work exceed the claimed time, and stopping at the
charged total leaves trails undetectable. What changed: every row of the ledger is now
a deterministic integer built from hard caps - the drain is an aggregate window of
1.34375 x 256 x 2^113 evaluations, recovery is 2 candidates x 4 x
12 x 2^113 evaluations with a per-trail cap of 12 x 2^113
(sections 6.3 and 7). The probability that a cap binds is computed and *subtracted*
from the success probability: 4.282e-06 for the drain window and 1.229e-05 for
recovery, total 1.657e-5 < 1e-4, leaving P(Q) - 1.657e-5 = 0.391483429880
> 0.39. No row of the time claim is a mean any more.

**9.9 Remaining material findings of the same reviews that this package also
addresses.** `lane_cryptanalysis/F2-dp-loss-bound` and `F-EVAL-3` (the 0.0015 margin
was not justified): the margin's content is now itemised in section 6.2 and the one
loss that was not inside it (the terminal tails) is charged instead of being covered
by the margin. `F-EVAL-4` / `EXP-1..4` (the controls were not organizer-executed):
control (k) is an organizer-executed experiment declared in the package.
`lane_cryptanalysis/F1-random-mapping-extrapolation`,
`lane_cost/random-mapping-evidence-gap`, `lane_cost/machine-storage-accounting-gap`
and `lane_experiments/EXP-F1..F3` remain *declared premises and declared experiment
scope*, not discharged claims: no width-256 test exists (H1), the machine convention is
H3, and the organizer-run experiment tests the circuit, the ledger and the pair
mechanics at a 8-bit masked-agreement event, which by the harness's own
`probability_inference: none` and `cost_trust: no_attack_cost_inference` cannot support
the 0.39 success probability or the cost at width 256. We do not claim otherwise.

## 10. Premises, scope and limits

H1 (score-critical, declared, not proved): the 3-round chain F behaves as a random
mapping on 2^256 points for the quantities the search uses: no exploitable collision
or cycle structure, trails merge like independent random paths, distinguished points
are independent events. It cannot be tested at width 256 and the controls do not test
it. If the real merge rate were lower than the model, a deficit eps costs
0.5 log2(1/(1-eps)) extra bits: 0.00725 bit at eps = 0.01, 0.0760 bit at eps = 0.10.

H3 (supporting, declared): the machine convention of section 3 - 256-bit plane
registers, the prices above, SSA with no moves, a 772-plane register file, no loads
or stores in the main loop, 4-byte gate records. With fewer than about 40 planes the
loop would need spills and the bound would rise.

Limits: the circuit is not claimed minimal, and the two hard caps of section 6.3 are
the only places where the plan can fail for reasons other than the random-mapping
premise. The row leader (`33f00b84`, [3, 124.68326]) is lower by 0.10695 bit because its generator finds a cheaper adder
family and a scanned constant block that this generator does not implement. No
differential attack is claimed; no witness pair is provided and the claim is a
resource bound.

## 11. Reproduce

    python3 bsgen.py --gates          # emitted step: gate count and mix
    python3 controls.py               # (a), (a2), (b), (b2), (c1), (neg), (i)
    python3 ledger.py                 # every row of sections 4-6
    python3 dpcheck.py                # independent re-derivation, (f) including F2
    python3 toy.py                    # (g), toy-width search on the emitted net
    python3 scan_key.py 65536         # (h), constant-prefix scan
    python3 verify_adder.py           # (j), adder enumeration
    python3 mkpackage.py --check      # rebuild package + experiments, claim vs ledger
    python3 experiments/b3r3_audit.py < request.json   # (k), the declared experiment

The generator is deterministic: no randomness enters the program, and the only
randomness of the search is the seed of section 6.1.
