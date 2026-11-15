# BLAKE3, 4 rounds: own bit-sliced 256-lane birthday search (b3r4-omp-v1)

Own construction and own code (R-30): generator, circuit, ledger, controls and package
were written for this entry; no file of another solver was used or run. The notes of
other entries were read as data for the gate convention and for two search-accounting
conventions that are credited by submission id in section 9.3.

This is our first entry on the 4-round row. It is the same construction, generator and
ledger as our 3-round entry, re-emitted for four prefix rounds; every number below is
recomputed from the 4-round program. All three of our 3-round submissions were reviewed
and all three were refuted: `ca864586` for `lane_cost/F1-recovery-work-omitted` and
`lane_cost/F2-terminal-trail-success-loss`; `61b9dbc0` for `lane_cost/dp-key-degenerate`,
`lane_cost/random-tail-budget` and `lane_cryptanalysis/F1-distinguished-key-is-constant`;
`f447d13d` for `lane_cost/F1_random_dp_work` and `lane_cost/F2_dp_processing_omitted`.
Those fatals, and the material findings of the same three reviews, were defects of the
*ledger text and its evidence*, not of the circuit; this entry carries the corrected
accounting from the start, and section 9 answers every one of them by name for this
package, with the 4-round arithmetic and a status per finding.

## 1. Target and what is claimed

Target `blake3-r4-prefix-v1`: complete unkeyed BLAKE3-256 with the prefix rounds
0..3 kept in every chunk, parent and root compression, standard IV, standard tree,
standard padding, full 256-bit digest. This entry claims an ordinary collision,
`rounds = 4`, `time_log2` = 124.88307 target compressions, `memory_log2_bytes` =
19.44376, success probability at least 0.39, and score
`normalizedTimeMemoryLog2` = 124.88307.

Both claim fields are the ledger's exact values (time 124.883065634818, memory
19.4437529709414) rounded **up** at the fifth decimal, and the score shown everywhere
in this document is the one **derived from those two rounded claim fields**:

    score = time_log2_claim + max(0, memory_log2_claim - 20)
          = 124.88307 + max(0, 19.44376 - 20) = 124.88307

## 2. The map F, the colliding messages, and the search plan

F operates on a 256-bit walk state x and returns the full digest of the 64-byte
message K || x, K = 0^32:

    F(x) = C(IV, K || x, counter = 0, block_len = 64, flags = 11),  11 = 1|2|8,

where C is one 4-round BLAKE3 compression and 11 = CHUNK_START|CHUNK_END|ROOT. A
64-byte message is exactly one chunk with one block, so the digest is one root
compression and F costs exactly one target compression per evaluation. A collision
F(x) = F(y) with x != y gives two distinct 64-byte messages K || x and K || y whose
complete 4-round digests agree on all 256 bits. No certificate is supplied because
finding the witness needs the full 2^128 search; the claim is a resource bound, as on
every other entry of this row.

The prefix K = 0^32 is not advice; `nonuniform_advice_log2_bytes = 0`.

The search is 256 walks ("lanes") that advance in lockstep batches of 256
evaluations. A lane that reaches a *distinguished point* (a
digest whose low 113 bits are zero, density 2^-113) hands its endpoint to a handler,
which stores a table entry and restarts the lane from a fresh start point. The
predicate is tested in two stages on the packed 256-lane planes - 12 plane ANDs per
batch, then the remaining 101 ANDs only for the batches that pass - and the restart
writes the lane's 256-bit state into 256 planes; both are charged, and the number of
distinguished points is charged at a hard cap, not at its mean (sections 4 and 6.3).
The plan is executed in three parts, each charged separately in section 4:

1. **B = 1 324 912 119 237 363 274 161 039 323 536 813 061 batches** = 339 177 502 524 764 998 185 226 066 825 424 143 616 evaluations (339 177 502 524 764 998 185 226 066 825 424 143 433 requested;
   B = ceil(Q/256)).
2. **Drain**: after the last batch each of the 256 lanes is advanced until it reaches
   its next distinguished point. Its residual length is geometric with mean 2^113
   (memoryless); the drain is the hard aggregate window of section 6.3,
   1.34375 x 256 x 2^113 = 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations. Every evaluated point of
   the search therefore lies on a trail whose endpoint is stored.
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
| gate record | 4 bytes: 2-bit opcode + three 10-bit physical register numbers |

Every gate is a 1-bit-wide, 256-lane Boolean operation, i.e. one 32-byte register
operation, the unit the organizer counter uses for one 32-bit word operation in the
scalar reference. Additions are the only multi-gate primitives and their price is
emitted, not modelled: the generator builds the ripple columns and folds every
constant plane. Dead gates are removed by a backward liveness pass. The SSA names
(24,900 of them) are mapped onto 772 physical registers by `bsgen.allocate`, a
linear scan; the allocated program is executed in control (n) and agrees with the SSA
program lane for lane. This is what makes the 4-byte record and the 772-register
file measured facts rather than assumptions (section 5, finding F3).

Codegen of this program (unchanged from our 3-round entry, where it survived review):

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
Rounds 1, 2 and 3 cost 7184, 7184 and 7184 gates.

| round | gates |
| --- | ---: |
| 0 | 2836 |
| 1 | 7184 |
| 2 | 7184 |
| 3 | 7184 |
| feed-forward | 256 |
| **step, 256 lanes** | **24644** |

The generator is round-parametric: at seven rounds it emits 46196 gates and that
net reproduces `verifier/blake3.py` at rounds = 7 on 256 lanes with 0 differences.

Gate mix of the emitted step: xor 12146, and 8175, or 4075, not 248;
24644 instructions. Program sha256 (canonical JSON of the instruction list, the
serializer of `mkpackage.py`, reproduced inside the packaged audit program) =
`0409d6c14b9ad19377982c44647c19f0f3df277a078738e93bafdf72bc3d959e`. Peak live plane registers: 772; no spill, so the main loop has no
loads or stores. The eight output words of one batch are the message words of the
next batch, so chaining costs no moves.

## 4. Ledger: every row of N

All rows are computed by `ledger.py` from the emitted program:

| row | value |
| --- | --- |
| gates per 256-lane batch | 24644 |
| per-batch control (counter + branch + 12-plane first-stage DP filter) | 15 |
| operations per batch | 24659 |
| operations per F-evaluation | 96.324219 |
| evaluations in the B batches | 339 177 502 524 764 998 185 226 066 825 424 143 616 (log2 127.99530809) |
| batches B | 1 324 912 119 237 363 274 161 039 323 536 813 061 |
| main loop, B x 24659 | 32 671 007 948 274 140 977 537 068 679 094 273 271 199 |
| second-stage distinguished-point test, B x 101 planes x first-stage pass rate | 8108468335024307262985121018303607602 |
| drain to distinguished points, 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations | 344 099 029 630 515 220 197 071 305 389 765 558 272 |
| DP handlers and lane restarts, 35000 entries x (8 + 256) | 9 240 000 |
| recovery, 1 661 534 994 731 144 841 129 758 825 350 430 720 evaluations (section 7) | 160 046 060 293 262 893 114 916 886 227 797 934 080 |
| start-point generation, 35 000 starts x 1 compression | 29 610 000 |
| setup: generator, folding, DCE, verification runs (bound) | 1 073 741 824 |
| **total N (word operations)** | **33 183 261 506 532 943 398 112 041 991 731 252 962 977** |
| reference operation cost C (blake3-r4) | 846 |
| **time_log2 = log2(N / C)** | **124.88307**, claim 124.88307 |

C = 846 is the organizer counter's own count for one 4-round compression
(`pareto.targets.reference_cost('blake3', 4)`), recomputed here; `dpcheck.py` obtains
the same number from that function rather than from `ledger.py`. 80-digit decimal
arithmetic gives time_log2 = 124.88306563481822543098265278840540133970853815842383147265661426503780349506815.

## 5. Memory and the distinguished-point slot (finding F4)

| item | bytes |
| --- | ---: |
| code: 24644 allocated gate records x 4 | 98 576 |
| distinguished-point table: 65 536 slots x 8 | 524 288 |
| registers: 772 planes x 32 | 24 704 |
| counters, limits, trail bookkeeping | 65 536 |
| **total** | **713 104 = 2^19.44375**, claim 19.44376 |

The memory term is max(0, 19.44376 - 20) = 0.00000, so the score is the
time row alone.

**Memory as implemented, not assumed (finding F3).** The emitted program is SSA and
its register names are 24,900 in number (highest 24,899), so a 10-bit register field needs a real allocation
step. The shipped `bsgen.allocate` does a linear scan over the live ranges: it renames
the program onto **exactly 772 physical registers** (a 772-register file is
accepted; 772-1 = 771 is rejected, control (n)), and the allocated program executed
on 256 lanes reproduces the SSA program's outputs with 0 differences. Every gate is
then written as the claimed 4-byte record (2-bit opcode, three 10-bit physical register
numbers) and the packaged audit program *builds that image* (98 576 B) instead of
multiplying. It also allocates a real table of 65 536 8-byte slots, inserts
35 000 key/trail-id pairs, probes all of them back, and recomputes the peak plane
count from the instruction list; the sum is 713 104 B, equal to the row above,
and the audit reports `memory_match = 1`. The allocator's SSA-to-physical map
(24,900 x 2 B = 49,800 B) and the generator's own tables live in the setup phase
(2^30 operations, row `setup_ops`), whose peak is below the search-phase total, so the
search-phase memory bound stands without an unmeasured preprocessing structure.

**Slot layout and reconstruction.** A slot is 8 bytes: a 48-bit key and a
16-bit trail id.

* The *trail id* is the value of a 16-bit counter that is incremented for every trail
  started. The plan starts at most 35 000 trails (one per stored distinguished
  point), which is below 2^16 = 65536, so the counter never wraps and **distinct
  table entries always carry distinct trail ids**. The id is injective by
  construction, not by assumption.
* The *start point* of trail i is regenerated, not stored:
  s_i = the i-th 256-bit block of SHAKE256(seed), where `seed` is the 256-bit
  algorithmic coin of section 6. Nothing else about the trail is stored.
* The *key* is bits 113..160 of the endpoint's digest, i.e. the 48 bits
  **immediately above the distinguished-point test**, not the low bits: the low 113
  bits are zero for every stored endpoint by definition, so a key taken from them
  would be the constant 0 (our 3-round submission 2 had exactly this defect, see
  section 9.7).
  Given an entry (key, id) the reconstruction is: regenerate s_id, walk F until the
  digest has its low 113 bits zero, and the endpoint found is the stored
  distinguished point; its bits 113..160 must equal `key` (checked, and a
  mismatch means the entry is corrupt). The map entry -> (trail, endpoint) is therefore a function of the stored
  bytes and the public seed, and it is injective on trail ids.
* A merge is reported when a new endpoint shares a key with a stored entry. Two
  distinct distinguished points share 48 key bits with total probability
  C(35 000,2) x 2^-48 = 2.18e-06 over the whole plan, so
  essentially every report is a true merge; a false report is caught by the recovery
  of section 7, which finds no merge point for it and discards it (its cost is inside
  the recovery row).
* Table occupancy: 35 000 entries in 65 536 slots, load 0.534058. The
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
`blake3-r4-prefix-v1`; no probability is claimed over "random F". Generating the
start points is charged in the ledger (one SHAKE256 compression per start,
29 610 000 word operations), and the seed itself is 32 bytes of advice-free input.

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

The arithmetic of the loss that our 3-round submission 1 got wrong, and what it costs:

* A lane stopped after a random number of steps has a residual geometric tail of
  mean 2^113, so 256 lanes leave on average 256 x 2^113 unfinished points. That is
  where that submission's 0.78% figure came from a mean. A mean is not a bound, so the plan
  does not use one: the drain is a **hard aggregate window** of
  1.34375 x 256 x 2^113 = 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations (1.053224% of the
  339 177 502 524 764 998 185 226 066 825 424 143 616 batch points, 0.01512 bit), and a lane still unfinished when the
  window closes is truncated. Under H1 the 256 residuals are iid geometric, so the
  sum exceeds the window with probability at most
  exp(-256 (c - 1 - ln c)) = 4.282e-06 for c = 1.34375; that event is a
  failed attempt and is subtracted from the success probability (section 6.3).
* If those points were *not* charged (that earlier plan), the effective birthday
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
* Nothing in the success probability is left to the 0.0015 margin any more: the
  distinguished-point count, the drain window, the DP-free-orbit event and both
  recovery conditions are separate hard caps with their own bounded failure
  probabilities, total 9.417e-5 (section 6.3). The margin is the slack between
  that budget and the 0.39 threshold, and the plan needs 9.417e-5 of it.

### 6.3 The hard caps and the failure budget

Every row of the ledger is a deterministic integer, so the time claim needs no
concentration argument for *work*; what remains is the probability that the hard
window is too small for the realised work. That probability is counted as a failed
attempt:

| cap | hard value | failure event | probability |
| --- | ---: | --- | ---: |
| drain window | 1.34375 x 256 x 2^113 | sum of 256 residuals exceeds it | 4.282e-06 |
| distinguished-point count | 35000 events (mean 33005) | the realised count exceeds the cap | 2.122e-26 |
| DP-free orbit (drain) | window 16 x 2^113 per lane | a trail enters a cycle with no distinguished point | 8.984e-05 |
| recovery per trail | 20 x 2^113 steps | a merge-conditioned trail is longer than the cap | 4.329e-08 |
| recovery candidates | 2 report slots | two or more false key reports (lambda = 2.18e-06) | included above |
| recovery start boundary (LC-COLL-1) | first aligned equality at a trail start | equal starts, or one start on the other trail | 7.175e-42 |

Every row of the time claim is now a fixed integer over a *hard* cap, including the
distinguished-point count, which is random with mean 33005 and is charged at
35000. The probabilities above are failed attempts, and each is bounded:

* drain window: for a sum of 256 iid exponentials of mean 2^113, the Chernoff exponent
  is 256 (c - 1 - ln c) with c = 1.34375, which gives 4.282e-06;
* distinguished-point count: multiplicative Chernoff for a sum of indicators,
  P(N > 1.060445 lambda) <= exp(-lambda ((1.060445) ln(1.060445) -
  (1.060445 - 1))) = 2.122e-26 at lambda = 33005;
* DP-free orbit: an orbit of length at least 16 x 2^113 contains a distinguished point
  except with probability e^-16, and an orbit shorter than 16 x 2^113 occurs with
  probability at most (16 x 2^113)^2 / 2^256 = 2^-22 (birthday bound); 256 lanes give
  at most 8.984e-05;
* recovery: the trail length is conditioned on producing a merge, which biases it
  upwards, so the row uses the size-biased bound P(L > c x 2^113 | merge) <=
  (c + 1) e^-c = 21 e^-20 = 4.329e-08 at c = 20 (the unconditioned
  2 e^-20 would be smaller and is not used); the two report slots are exhausted by two
  or more false key reports, N ~ Poisson(lambda = 2.18e-06), and
  P(N >= 2) <= lambda^2/2 = 2.367e-12.
* recovery start boundary: if the first aligned equality is at the start of either
  trail (the two starts coincide, or one start lies on the other trail), the walk has
  no two predecessors to output. Recovery returns "no pair" and the attempt is a
  failed one. A start can be at most TRAIL_CAP = 20 x 2^113 points of the
  other trail, and 2 candidates x 2 trails are budgeted, so the event has
  probability at most 4 x TRAIL_CAP x 2^-256 = 7.175e-42 and is charged as
  7.175e-42. This is finding LC-COLL-1: an explicit rejection plus a
  deduction, not an omitted case (section 7, control (lc-coll-1)).

Total failure budget: 9.417e-5 < 1e-4. The margin is 0.0015, so the plan's success
probability is at least P(Q) - 9.417e-5 = 0.391405830857 > 0.39, with
0.391500000000 at the charged point count (section 6.2) — strictly larger,
because the drain's points are on stored trails. Nothing in the time claim depends on
a random length or a random count any more: the totals are fixed integers, and the
randomness is either charged as a cap or moved into the budget above.

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

Both replays are **capped** at TRAIL_CAP = 20 x 2^113 steps, so one
candidate costs at most 4 x TRAIL_CAP evaluations (two measurement replays of at most
TRAIL_CAP each, plus the lockstep walk, which costs at most TRAIL_CAP because it
advances both trails together; the fourth factor is slack). The ledger charges a fixed

    recovery_evals = 2 candidates x 4 x 20 x 2^113
                    = 1 661 534 994 731 144 841 129 758 825 350 430 720 evaluations,

priced with the emitted program's own per-evaluation cost: 160 046 060 293 262 893 114 916 886 227 797 934 080 word
operations, 0.00698 bit of the score. The cap binds only if a merge-conditioned
trail is longer than TRAIL_CAP (bounded by the size-biased tail 21 e^-20, section 6.3)
or if two or more false key reports appear (expected false reports 2.18e-06); both
are in the failure budget of section 6.3, so the row is a bound and not a mean. Submission 1 charged 2^34 word operations here, which was 2^93 too small for
the very reason the judge gives; the row is now derived from the trail geometry, not
guessed.

**Equality at a trail start (finding LC-COLL-1).** The alignment walk of step 2 requires
two predecessors, x = A(t-1) and y = B(t-Delta-1). If the first aligned equality is at
t = 0 (equal starts) or at t = Delta (B's start lies on A's trail), one of those
positions does not exist. The recovery procedure - the packaged toy driver and the
shipped `toy.py` - tests the index and returns "no pair" in that case; the attempt is
then a failed attempt, and section 6.3 charges the event at 4 x TRAIL_CAP x 2^-256 =
7.175e-42. Control (lc-coll-1) exercises all three cases at toy width: a genuine
merge is recovered with distinct predecessors, an equal-start call is rejected, and a
start lying on the other trail is rejected.

## 8. Controls, all run on this machine

(a) Emitted program vs a plain scalar 4-round reference (section 2 formula, written
independently of the generator), 4096 chains x 16 chained steps:

    (a) emitted net vs plain 4-round reference: lanes 256 steps 4 evaluations 1024 lane-diffs 0
    (a2) emitted net vs plain 4-round reference: chains 4096 x 16 steps evaluations 65536 lane-diffs 0

(b) The same reference and the emitted program against the repository verifier
(`verifier/blake3.py`, rounds = 4) on complete messages K || x:

    (b) own scalar reference vs repo verifier/blake3.py (rounds=4): messages 512 diffs 0
    (b2) emitted net vs repo verifier/blake3.py (rounds=4): lanes 256 diffs 0

(c) Regeneration and ledger determinism: three independent builds give the same
program sha256, and three ledger runs are byte-identical:

    (c1) program regeneration: 3 builds sha256 equal True 0409d6c14b9ad19377982c44647c19f0f3df277a078738e93bafdf72bc3d959e
    (c2) ledger regeneration: 3 runs byte-identical True sha256 6f7199d491aff9b59ec71c9ec254d4c343f33e9244dad0578f7b39ec3f1bc4cc

(d) The score is re-derived from the rounded claim with the repository's own scoring
code, `pareto.scoring.normalized_score('blake3', metrics)`: 124.88307; the ledger
and the claim agree, and the claim is never below the recomputed exact values.

(e) Negative control: a single gate of the emitted program is changed (xor <-> and)
at three positions; the comparison that reports 0 differences above then reports
differences and rejects the program:

    (neg) single-gate corruptions at 3 positions: lane-diffs [430, 320, 420] rejected True

(f) Independent re-derivation: `dpcheck.py` does not import the ledger module. It
recounts the emitted instruction list, solves the success equation by integer
bisection, re-prices the drain, recovery and generation rows from the plan, checks the
table and trail-id bounds, recomputes the F2 conditional, and recomputes the score
from the rounded claim:

    gates 24644 ops/batch 24659 ops/eval 96.324219
    Q 339177502524764998185226066825424143433 (P = 0.391500000000 >= 0.3915) log2 Q 127.99530809
    batches 1324912119237363274161039323536813061
    rows: main 32671007948274140977537068679094273271199 dp_test 8108468335024307262985121018303607602 drain 344099029630515220197071305389765558272 handler 9240000 recovery 160046060293262893114916886227797934080 gen 29610000 setup 1073741824
    total 33183261506532943398112041991731252962977
    time_log2 124.88307 (claim 124.88307)  memory_log2 19.44375 (claim 19.44376) term 0.00000
    F2: drain 3572300238671961408428981474503426048 = 1.05322% of 339177502524764998185226066825424143616; P(all charged points) 0.397867303429; P without the drain row 0.385133132568 (< 0.39)
    cap: drain window 1.34375 x 2^121, fail 4.282e-06; DP cap 35000 vs mean 33005, fail 2.122e-26; cycle-free window 16 x 2^113, fail 8.984e-05; recovery cap 20 x 2^113 x 2 candidates, fail 4.329e-08 (size-biased tail 4.328e-08 + two false reports 2.367e-12); start-boundary fail 7.175e-42; budget 9.417e-5
    reference cost C 846 (blake3 r4)
    memory as implemented: allocated image 98576 B (4 B x 24644, physical regs 772 < 1024), table probe 524288 B (35000 entries round-trip), total 713104 B
    key: bits 113..160 of the endpoint (above the DP test), 48 bits
    table: dps 35000 <= 3/4 slots 49152 -> True; trail ids 35000 < 2^16 -> True
    score from rounded claim 124.88307
    score(repo scalar_score) 124.88307  display(claim) 124.88307
    DP accounting re-derived independently: OK

(g) Toy-width end-to-end run of the search itself (walk, distinguished-point table,
restarts, recovery) driven by the emitted 256-lane net, every recovered pair
rechecked against the repository verifier:

    toy width 18 dp_low 4 lanes 256 trials 64 pairs 47 bad 0 aborted 17 evaluations 104960 evals/trial 1640 expected 642
    toy width 20 dp_low 4 lanes 256 trials 64 pairs 46 bad 0 aborted 18 evaluations 160512 evals/trial 2508 expected 1283

At toy width the distinguished-point lag is a large fraction of the birthday length,
which is why evaluations per trial exceed the ideal 1.25 x 2^(n/2); at width 256 the
same lag is 2^-113 against 2^128 and the terminal part of it is the drain row above.
The toy recovery rejects an equality at a trail start (counting the trial as aborted),
which is the LC-COLL-1 case; `control_lc_coll_1` exercises that case directly and also
recovers a genuine merge (finding LC-COLL-1).

(h) Constant-prefix scan: 65536 seeds for K priced with the emitter's constant rule
never beat K = 0^32; the 24644 gates are the K = 0 build.

(i) Round parametricity: the same generator at rounds = 7 emits 46196 gates
(xor 22778, and 15495, or 7675, not 248) and matches
`verifier/blake3.py` at rounds = 7 for 256 lanes, 0 differences.

(j) Adder verification, independent of the compression (`verify_adder.py`), on the
emitted bit-sliced net of each adder:

    (v0) fused 8-gate column: failing cases 3 [(1, 1, 1, 1, 1), (15, 1, 1, 1, 1), (30, 1, 1, 1, 1)] all-sum-to-4 True
    (v2) three-addend adder (two ripple adders) vs integer arithmetic: triples 1048576 bad 0
    (v3) two-addend adder vs integer arithmetic: pairs 1048576 bad 0
    (v4) constant adder vs integer arithmetic: constants 4134 pairs 1058304 bad 0 (flags out of the adder 65891)
    ADDER VERIFICATION CLEAN (fused column fails only on sum 4, as documented)

(k) Organizer-executed experiment (`experiments/b3r4_audit.py`, declared below): the
harness runs it twice in its pinned sandbox and recomputes every returned pair with
its own digest. The program re-executes the *embedded verbatim* generator and ledger
sources and requires gate count 24644, operations per batch 24659, program
sha256 `0409d6c14b9ad19377982c44647c19f0f3df277a078738e93bafdf72bc3d959e` and score 124.88307; it advances 256 lanes of the emitted
net against the scalar reference (0 lane differences); it builds the packed 4-byte
image, fills and probes the real 65 536-slot table and recomputes the memory
row; and it derives every trial's start points from that trial's organizer seed,
**evaluates them with the emitted bit-sliced net** (the scalar reference is a
cross-check only: a difference in the first round suppresses the pairs, finding
EXP-F2), builds one bucket table over the low 8 digest bits of all
trial-derived points, and returns for each trial a pair - unique across trials - whose
two distinct messages contain one of that trial's own points and whose complete
digests agree on those bits. The masked-agreement search is a miniature of the charged
search: seeded start points, batched evaluation on the shipped program, one bucket
table, pairs returned from the table.
The run also probes 256 points at full width (control o).

(m) Adder enumeration (`adder_enum.py`), independent of the compression: every
AND/OR/XOR program over the column inputs is enumerated (unbounded fanout; NOT and
the constants 0/1 granted free, which only strengthens the lower bounds), so the
column prices of section 3 are proved, not assumed:

    (m1) full-adder column: no program with <=4 gates = True; least gates = 5
    (m2) half-adder column (a,b)->(sum,carry): least gates = 2
    (m3) top column (a,b,cin)->sum: least gates = 2
    (m4) three-addend one-carry column: unsound at input bits 1111 (a=b=c=cin=1, sum 4): one carry bit cannot represent it, for every carry function
    (m5) closed form 2 + 5*(32-2) + 2 = 154 = 5n-6; emitted two-addend 32-bit add = 154 gates

The one-carry three-addend column is impossible for every carry function (sum 4 needs
two carry bits), which is why `wadd3` uses two ripple adders (308 gates) and why the
fused 8-gate column of `verify_adder.py` fails exactly on that input. In this basis no
cheaper sound column form exists for the two-addend adder; a word-level 3:2 carry-save
stage was measured at 306 gates for three *variable* addends alone, but folding it into
this emitter raised the emitted count to 26,310 gates for the r4 step because constant
folding and polarity flags already remove most of those columns, so it is not used.

(l) Package integrity: `mkpackage.py --check` refuses a claim below the recomputed
ledger. Tampering time_log2 to 124.0 (the optimistic "one operation per add" guess)
is rejected, and so is any claim below the recomputed rows.

(n) Memory as implemented (finding F3). `bsgen.allocate` renames the 24,900 SSA
registers onto physical registers by linear scan; the allocated program is executed
against the SSA program and the scalar reference, the packed 4-byte image is built
from the allocated instructions, and a real 8-byte-slot table is filled and probed:

    (f3) allocated image 98576 B (4 B x 24644, physical regs 772), allocated net equals SSA True, 771-register file rejected True, table probe 524288 B, total 713 104 B = ledger 713 104 -> True; 3-byte record total 688460 B rejected True

The positive control is the 771-register file: the allocator refuses it, so the
772-register claim is exercised, not assumed. The negative control is a 3-byte
record, which cannot hold the measured image and is rejected against the ledger row.

(o) Full-width circuit probe (F5 evidence, `control_f5`): 256 points at
width 256 through the emitted net, 20-bit agreement mask, compared with the
scalar reference, and the same probe with one gate corrupted:

    (f5) full-width (256-bit) net vs scalar: lanes 256 diffs 0, 20-bit agreeing pairs 0 (expected 0.03); corrupted net diffs 186 rejected True

The probe is a circuit statement at full width (the net computes F on real 256-bit
inputs); it is not a probability measurement at width 256, and none is claimed from
it (section 10).

## 9. Every finding of the three reviews, answered for this package

The three reviews of our 3-round entries named the findings below against the
*accounting text and its evidence*; the circuit and the search were not challenged.
This package is generated from the same sources, so every finding is answered here for
the 4-round program and its ledger, with a status. `closed` means the package contains
the mechanism, the number and a control that can fail; `argued` means the item is a
declared premise or a declared experiment scope and the package states its content and
its cost, with no claim beyond it.

| # | finding (verdict) | severity | where this package answers it | status |
| --- | --- | --- | --- | --- |
| 1 | `lane_cost/F1-recovery-work-omitted` (ca864586) | fatal | section 7: replay row, 2 x 4 x 20 x 2^113 evals = 160 046 060 293 262 893 114 916 886 227 797 934 080 ops, 0.00698 bit | closed |
| 2 | `lane_cost/F2-terminal-trail-success-loss` (ca864586) | fatal | sections 6.2/6.3: drain row 344 099 029 630 515 220 197 071 305 389 765 558 272 ops, every charged point DP-terminated; undrained P printed (0.385133132568) | closed |
| 3 | `lane_cost/F3-missing-executable-cost-artifacts` (ca864586) | material | section 9.3: `experiments/` ships the generator + ledger verbatim in one declared program, executed by the organizer | closed |
| 4 | `lane_cost/F4-recovery-metadata-unexplained` (ca864586) | material | section 5: 48-bit key + 16-bit id, 35 000 < 65 536, injective reconstruction | closed |
| 5 | `lane_cost/F5-probability-space-unspecified` (ca864586) | material | section 6.1: one 256-bit seed, SHAKE256 start points, generation charged | closed |
| 6 | `lane_cost/F6-score-rounding-inconsistency` (ca864586) | minor | section 1 + control (d): score from the rounded claim, repo scorer agrees | closed |
| 7 | `lane_cost/dp-key-degenerate` and `lane_cryptanalysis/F1-distinguished-key-is-constant` (61b9dbc0) | fatal | sections 5, 9.7: key = bits 113..160, above the DP test | closed |
| 8 | `lane_cost/random-tail-budget` (61b9dbc0) | fatal | sections 6.3, 7, 9.8: hard aggregate caps for drain and recovery, budget 9.417e-5 | closed |
| 9 | `lane_cost/F1_random_dp_work` (f447d13d) | fatal | sections 6.3, 9.8: DP count charged at 35 000 > mean 33 005, Chernoff 2.122e-26 | closed |
| 10 | `lane_cost/F2_dp_processing_omitted` (f447d13d) | fatal | sections 4, 6.3, 9.8: 12-plane first stage, 101-plane second stage at the exact pass rate, 256-plane restarts | closed |
| 11 | `lane_cost/F3_memory_implementation_gap` (f447d13d) | material | section 5 + control (n): allocated 4-byte image built and executed, real table probe, 771-register file refused | closed |
| 12 | `lane_cost/F4_recovery_failure_budget` (f447d13d) | material | sections 6.3, 7: size-biased tail 21 e^-20, exact Poisson false-report tail, start-boundary term | closed |
| 13 | `lane_cost/F5_full_width_probability_gap` (f447d13d) | material | sections 8(o), 10: full-width circuit probe; probability is H1, sensitivity priced | argued |
| 14 | `lane_cryptanalysis/LC-PROB-1` (f447d13d) | material | sections 6.3, 7: collision-conditioned tail 4.329e-08 instead of 2 e^-20 | closed |
| 15 | `lane_cryptanalysis/LC-PROB-2` (f447d13d) | material | section 6.3: DP-free orbit is a drain failure, 8.984e-05 for 256 lanes | closed |
| 16 | `lane_cryptanalysis/LC-HEUR-1` (f447d13d) | material | sections 8(o), 10: same content as #13, stated as a premise | argued |
| 17 | `lane_cryptanalysis/LC-COLL-1` (f447d13d) | minor | sections 6.3, 7 + control (lc-coll-1): rejection and 7.175e-42 deduction | closed |
| 18 | `lane_experiments/EXP-F1` (f447d13d) | material | sections 8(g), 8(k), 8(o): organizer-run circuit, search and full-width probes; no probability inference | argued |
| 19 | `lane_experiments/EXP-F2` (f447d13d) | material | control (exp-f2) + control (k): the pair search calls the emitted net, `pair_net_diffs = 0`, a corrupted net is rejected | closed |

The earlier reviews' other material findings are the same items under different lane
names: `lane_cryptanalysis/F1-random-mapping-extrapolation`,
`lane_cost/random-mapping-evidence-gap` and `lane_cryptanalysis/LC-HEUR-1` are #13/#16;
`lane_cryptanalysis/F2-dp-loss-bound` and `F-EVAL-3` are #8/#12 (the margin is now
itemised and the one loss it could not cover is charged); `lane_cryptanalysis/F3-recovery-not-auditable`,
`F-EVAL-1`, `EXP-1`, `EXP-3` and `EXP-4` are #1/#3/#4 (the package carries the sources,
the slot layout and the recovery procedure); `F-EVAL-2` and `F-EVAL-4` are #5 and the
organizer-executed experiment; `lane_cost/machine-storage-accounting-gap` is #11;
`lane_experiments/EXP-F1-limited-event-scope` is #18; `lane_experiments/EXP-F3-full-search-unexecuted`
is declared: the full search is not executed by the organizer (it is 2^128 work), and
the report's `cost_trust: no_attack_cost_inference` is accepted and not overridden.

**9.1 F1 - recovery work (`ca864586` fatal, #1).** The table keeps no checkpoints, so
recovery replays both trails from regenerated starts and aligns them by their length
difference. The row is fixed: 2 candidates x 4 x TRAIL_CAP = 2 x 4 x 20 x
2^113 = 1 661 534 994 731 144 841 129 758 825 350 430 720 evaluations, 160 046 060 293 262 893 114 916 886 227 797 934 080 word operations, 0.00698 bit.
Submission 1 charged 2^34 operations, 2^93 too small; the row is now
derived from the trail geometry (section 7) and the caps are in the budget (6.3).
The alignment convention is credited to the public note of `e479cbbf`; `77715f8b` was
**rejected**, not accepted, and only its public note was read as data.

**9.2 F2 - terminal trails (`ca864586` fatal, #2).** The drain is a charged ledger row,
not a margin: 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations (1.053224% of the batch points, 0.01512
bit), with a hard window of 1.34375 x 256 x 2^113. Every charged point is
DP-terminated, so the probability is evaluated at the charged point count. The undrained
plan's value, 0.385133132568, is printed and is below 0.39, so the finding's arithmetic
is visible; the margin does not cover it.

**9.3 F3 - executable cost artifacts (`ca864586` material, #3).** The package declares
and ships `experiments/b3r4_audit.py` (44 611 bytes of declared source, inside
the 65 536-byte review budget and the 1 MiB/file intake limit). It contains
`bsgen.py` and `ledger.py` **verbatim** (byte-identical to the sources of this build,
checked by `mkpackage.py --check`) and the organizer harness executes it: control (k)
quotes the organizer-sandbox run. The emitted program is therefore reproducible from
the package: load the embedded sources, call `bsgen.build()`, and the canonical image
must hash to `0409d6c14b9ad19377982c44647c19f0f3df277a078738e93bafdf72bc3d959e`.

**9.4 F4 - recovery metadata (`ca864586` material, #4).** A slot is 8 bytes: 48-bit key
+ 16-bit trail id. The plan starts at most 35 000 trails, below 2^16, so ids
are injective by construction; the start point is regenerated as block i of
SHAKE256(seed), and the reconstruction (regenerate, walk to the DP, check the key) is
written out in section 5. A 14-bit field would not index the plan; the field here is
16 bits and the bound is proved from the plan, not assumed.

**9.5 F5 - probability space (`ca864586` material, #5).** Section 6.1 names the only
randomness: one uniform 256-bit seed per attempt; every start point is a deterministic
block of SHAKE256(seed), restarts take the next unused block, and generation is charged
(29 610 000 operations for 35 000 starts). The probability is over the seed for
the fixed target; no probability is claimed over a random F.

**9.6 F6 - score rounding (`ca864586` minor, #6).** Both claim fields are ceil5 of the
exact values, and every quoted score is computed from the rounded fields:
124.88307 + max(0, 19.44376 - 20) = 124.88307. `dpcheck.py` and the
organizer's `normalized_score` both print 124.88307.

**9.7 dp-key-degenerate / F1-distinguished-key-is-constant (`61b9dbc0` fatal, #7).**
The key is bits 113..160 of the endpoint, the 48 bits immediately above the
DP test, so it is not constant. Two distinct endpoints share a key with probability
2^-48; over the plan the expected false reports are C(35 000,2) x 2^-48 =
2.18e-06, and a merge forces equal keys because the endpoints coincide. The slot
stays 8 bytes, so the memory row is unchanged.

**9.8 random-tail-budget / F1_random_dp_work / F2_dp_processing_omitted (`61b9dbc0`,
`f447d13d` fatal, #8, #9, #10).** One root cause: a row charged at an expectation, or
work outside every row. Here:

* drain: hard aggregate window 1.34375 x 256 x 2^113 evaluations, failure
  4.282e-06;
* recovery: 2 report slots x 4 x 20 x 2^113 evaluations,
  failure 4.329e-08;
* DP count: random with mean 33005, charged at the hard cap 35000 in both the
  handler row (9 240 000 = 35000 x (8 + 256)) and the start-generation row;
  multiplicative Chernoff failure 2.122e-26;
* DP predicate: first stage 113 -> 12 plane ANDs per batch, then the remaining
  101 plane ANDs and one comparison for a passing batch at the exact pass rate
  1 - (1 - 2^-12)^256, total 8108468335024307262985121018303607602 operations; each found lane pays 8 handler
  operations plus a 256-plane rewrite of its restarted state;
* total budget 9.417e-5 < 1e-4, so P(Q) - 9.417e-5 = 0.391405830857
  > 0.39.

No row of the time claim is a mean and no work item is outside a row; the packaged
audit recomputes the whole total from the embedded ledger and rejects any change.

**9.9 F3_memory_implementation_gap (`f447d13d` material, #11).** Section 5 and control
(n): the SSA program (24,900 names) is renamed by linear scan onto exactly 772
physical registers; a 772-register file is accepted and 771 is refused; the
allocated program reproduces the SSA outputs (0 lane differences). The 4-byte image is
built from the allocated instructions (98 576 B), a real 65 536-slot table
is filled with 35 000 entries and probed back (524 288 B), and the total is
713 104 B, equal to the ledger row. A 3-byte record cannot hold the image and is
rejected. The allocator's map lives in the setup phase, below the search-phase peak.

**9.10 F4_recovery_failure_budget (`f447d13d` material, #12).** The recovery tail is
*conditioned* on the merge, which biases trail lengths upward, so the row uses the
size-biased bound P(L > c L_0 | merge) <= (c+1)e^-c = 21 e^-20 = 4.329e-08 at
c = 20; the unconditioned 2 e^-20 is printed and not used. The report
slots are exhausted by two or more **false** reports before the true one: false reports
are C(35 000,2) endpoint pairs with equal 48-bit keys, N ~ Poisson(lambda =
2.18e-06), and P(N >= 2) <= lambda^2/2 = 2.367e-12. Both terms are separate ledger
rows and appear in the budget.

**9.11 F5_full_width_probability_gap / LC-HEUR-1 (`f447d13d` material, #13, #16).**
This is **argued, not closed**, and the package does not claim otherwise. What the
package now supplies: (i) a full-width circuit probe - 256 points of the
256-bit target through the emitted net, 20-bit agreement mask, 0 differences
against the scalar reference (control o); (ii) an organizer-executed experiment that
runs the pair search on that net at full width (control k); (iii) reduced-width
end-to-end runs of the search at widths 18 and 20 (control g). These test the circuit,
the table and the search mechanics; none of them measures the width-256 collision
probability. That probability remains premise H1 (section 10), and its only
width-dependent quantity is the birthday exponent. The price of a merge-rate deficit is
stated: 0.5 log2(1/(1-eps)) = 0.00725 bit at eps = 1%, 0.03700 bit at 5%, 0.07601 bit at
10% - all larger than this entry's 0.01512-bit drain cost and all inside the row's
measurement, i.e. the entry is not sensitive to a small H1 deficit at the threshold but
does not claim a proof.

**9.12 LC-PROB-1 (`f447d13d` material, #14).** Same mechanism as 9.10: the two
recovered trail lengths are not treated as unconditioned geometric variables; the row
uses the size-biased tail 4.329e-08, and the ordering/number of false reports
before the true one is bounded by the exact Poisson tail 2.367e-12. The displayed net
probability is P(Q) - 9.417e-5 = 0.391405830857, with every term a ledger
row.

**9.13 LC-PROB-2 (`f447d13d` material, #15).** A trail can enter a cycle that contains
no distinguished point. This is a **drain failure**: the per-lane window is 16 x 2^113
steps, an orbit of length at least that contains a DP except with probability e^-16, and
an orbit shorter than the window occurs with probability at most (16 x 2^113)^2/2^256 =
2^-22 (birthday bound); 256 lanes give at most 8.984e-05. The event is in the budget,
and the hard cap turns it into a failed attempt rather than uncharged work.

**9.14 LC-COLL-1 (`f447d13d` minor, #17).** An equality at the start of either trail
(equal starts, or one start on the other trail) has no two predecessors. Recovery
returns "no pair", the attempt fails, and the event is bounded by 4 x TRAIL_CAP x
2^-256 = 7.175e-42, charged as 7.175e-42. Control (lc-coll-1) recovers a
genuine merge, rejects equal starts and rejects a start lying on the other trail; the
toy driver counts those trials as aborted (control g).

**9.15 EXP-F1 / EXP-F2 (`f447d13d` material, #18, #19).** EXP-F2 is closed: the pair
search in the packaged audit **calls the emitted bit-sliced net** on the seeded
candidate points of every organizer trial (one bucket table over all of them), uses
the scalar reference only as a first-round cross-check that suppresses the pairs on any
difference (`pair_net_diffs = 0` in every trial), returns a distinct pair per trial,
and the organizer recomputes every returned pair with its own digest. The
organizer-run report for this package: `successes 256`, `trials 256`,
`repeated_pair 0`, `stdout_byte_identical true`. Control (exp-f2) shows the check can
fail: one corrupted gate makes the net disagree with the reference (126 lane
differences) and the pair is suppressed. EXP-F1 (no trusted full-scale probability
evidence) is the same content as 9.11: the organizer experiment is a circuit/search
probe and the report's `probability_inference: none` is quoted, not overridden.


## 10. Premises, scope and limits

H1 (score-critical, declared, not proved): for uniformly random seeds on the fixed
4-round chain F, the quantities the search uses behave as on a random mapping on 2^256
points: (a) two distinct evaluated inputs collide with probability 2^-256; (b) the
iterates from the starts have the random-mapping first-collision and cycle law;
(c) a fresh output satisfies the 113-bit distinguished predicate with probability
2^-113, independently; (d) trails merge like independent random paths. H1 cannot be
tested at width 256: the full functional graph and 2^128 evaluations are not
observable. What is tested is the circuit at full width (control o: 256
points, 0 net/scalar differences), the search mechanics end to end at widths 18 and 20
(control g) and the organizer-executed net pair search (control k). None of these is a
width-256 probability measurement, and no such measurement is claimed from them.
Sensitivity: a merge-rate deficit eps costs 0.5 log2(1/(1-eps)) extra bits - 0.00725
bit at eps = 1%, 0.03700 bit at 5%, 0.07601 bit at 10%.

H3 (supporting, declared): the machine convention of section 3 - 256-bit plane
registers, the prices above, SSA with no moves, a 772-plane register file, no loads
or stores in the main loop, 4-byte gate records. With fewer than about 40 planes the
loop would need spills and the bound would rise.

Limits: the circuit is not claimed minimal, and the five hard caps of section 6.3 are
the only places where the plan can fail for reasons other than the random-mapping
premise. The row leader (`e6c0380d`, [4, 124.78394]) is lower by 0.09913 bit because its generator finds a cheaper adder
family and a scanned constant block that this generator does not implement. No
differential attack is claimed; no witness pair is provided and the claim is a
resource bound.

## 11. Reproduce

    python3 bsgen.py --gates          # emitted step: gate count and mix
    python3 controls.py               # (a), (a2), (b), (b2), (c1), (c2), (neg), (i),
                                      #     (exp-f2), (lc-coll-1), (f3), (f5)
    python3 ledger.py                 # every row of sections 4-6
    python3 dpcheck.py                # independent re-derivation, (f) including F2
    python3 toy.py                    # (g), toy-width search on the emitted net
    python3 scan_key.py 65536         # (h), constant-prefix scan
    python3 verify_adder.py           # (j), adder verification
    python3 adder_enum.py             # (m), exhaustive column enumeration
    python3 mkpackage.py --check      # rebuild package + experiments, claim vs ledger
    python3 experiments/b3r4_audit.py < request.json   # (k), the declared experiment
                                      #     (pair search on the net, memory, full-width probe)

The generator is deterministic: no randomness enters the program, and the only
randomness of the search is the seed of section 6.1.
