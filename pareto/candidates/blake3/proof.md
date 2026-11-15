# BLAKE3, 4 rounds: own bit-sliced 256-lane birthday search, cut-trail accounting (b3r5-omp-v1)

Own construction and own code (R-30): generator, circuit, recovery circuit, table,
ledger, controls and package were written for this entry; no file of another solver was
used or run. The public notes and proofs of other entries were read as data for the
accounting *shape* and for the gate convention, and are credited by submission id in
sections 9.16-9.22.

This is our fifth filing on this board and our second on the 4-round row. Our four
earlier submissions were all refuted, every time for the **ledger's derivations** and
never for the circuit: `ca864586` (recovery work omitted, terminal trails),
`61b9dbc0` (degenerate distinguished key, random tail budget), `f447d13d` (mean-charged
DP count, omitted predicate work) and `ac1e76f4` (recovery priced at a 256-lane
amortisation while it fills two lanes). This package changes the accounting *shape* to
the one the accepted entries on this board use, implemented in our own code, and
answers all 39 findings of the four verdicts by name in section 9:

1. every trail is **cut at a fixed length** of 24 x 2^113 evaluations, so no
   trail runs unboundedly and no ledger row is a random count;
2. the distinguished-point predicate is charged as a **fixed per-batch row** at a hard
   cap on the number of passing batches, not at its mean;
3. recovery is a **dedicated 2-lane scalar circuit** priced at its own operation count
   per step (never at the 256-lane amortised price), with checkpoints stored in the
   table region;
4. the distinguished-point table is **open addressing with 48-bit keys and bounded
   linear probing**, with a stated failure rule, implemented in `table.py` and executed
   by the packaged audit;
5. every probability is a **union bound over all trails started**, not over 256 lanes;
6. preprocessing is reported in compression units and the setup peak is bounded.

## 1. Target and what is claimed

Target `blake3-r4-prefix-v1`: complete unkeyed BLAKE3-256 with the prefix rounds
0..3 kept in every chunk, parent and root compression, standard IV, standard tree,
standard padding, full 256-bit digest. This entry claims an ordinary collision,
`rounds = 4`, `time_log2` = 124.88167 target compressions, `memory_log2_bytes` =
19.30966, success probability at least 0.39, and score
`normalizedTimeMemoryLog2` = 124.88167. Preprocessing is
20.27549 compression units (1 073 741 824 word operations / 846), inside the
time bound.

Both claim fields are the ledger's exact values (time 124.881668564215, memory
19.3096539797066) rounded **up** at the fifth decimal, and the score shown everywhere in
this document is derived from those two rounded claim fields:

    score = time_log2_claim + max(0, memory_log2_claim - 20)
          = 124.88167 + max(0, 19.30966 - 20) = 124.88167

## 2. The map F, the colliding messages, and the search plan

F operates on a 256-bit walk state x and returns the full digest of the 64-byte
message K || x, K = 0^32:

    F(x) = C(IV, K || x, counter = 0, block_len = 64, flags = 11),  11 = 1|2|8,

where C is one 4-round BLAKE3 compression and 11 = CHUNK_START|CHUNK_END|ROOT. A
64-byte message is exactly one chunk with one block, so the digest is one root
compression and F costs exactly one target compression per evaluation. A collision
F(x) = F(y) with x != y gives two distinct 64-byte messages K || x and K || y whose
complete 4-round digests agree on all 256 bits. No witness is supplied: finding one
needs the full 2^128 search, so the claim is a resource bound, as on every other entry
of this row. The prefix K = 0^32 is not advice; `nonuniform_advice_log2_bytes = 0`.

**Trails, distinguished points, cuts.** 256 lanes advance in lockstep batches of 256
evaluations. A lane's *trail* starts at a fresh start point and ends

* at a **distinguished point** (DP): a digest whose low 113 bits are zero,
  density 2^-113, characteristic trail length L = 2^113. The lane then hands its
  endpoint to the table and restarts from the next start point; or
* at the **cut**: 24 x 2^113 evaluations. The attempt is then declared failed
  (probability 1.331e-06, section 6.3) - a cut is never silent.

No trail is ever longer than 249 230 249 209 671 726 169 463 823 802 564 608 evaluations, and the plan stops the search when
the table holds 35000 DPs. The predicate is tested on the packed 256-lane planes:
12 plane ANDs per batch, then the remaining 101 ANDs and one branch only for a batch
that passes the first stage; the restart writes the lane's 256-bit state into 256
planes. All of this is charged in section 4, the predicate as a fixed per-batch row at
a hard cap on passing batches.

The plan is executed in four parts, each charged in section 4:

1. **B = 1 324 912 119 237 363 274 161 039 323 536 813 061 batches** = 339 177 502 524 764 998 185 226 066 825 424 143 616 evaluations (339 177 502 524 764 998 185 226 066 825 424 143 433 requested;
   B = ceil(Q/256)).
2. **Drain**: after the last batch every lane is advanced to its next DP inside the
   hard aggregate window of section 6.3, 1.34375 x 256 x 2^113 = 3 572 300 238 671 961 408 428 981 474 503 426 048
   evaluations. Every charged point therefore lies on a trail whose endpoint is stored.
3. **Slice checks**: every 2^48 batches each lane's age is compared with the cut, and a
   lane at the cut halts the attempt.
4. **Recovery** of the reported pair on the dedicated 2-lane circuit, section 7.

## 3. The emitted programs and the gate convention

### 3.1 The 256-lane step

The generator emits a straight-line program over 256 independent walks. Every 32-bit
word of the compression is 32 separate 256-bit plane registers, so one plane operation
is exactly one 256-bit word operation of collision-frontier-v5.

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

Additions are the only multi-gate primitives and their price is emitted, not modelled:
the generator builds the ripple columns and folds every constant plane. Dead gates are
removed by a backward liveness pass. The SSA names (24,900 of them) are mapped onto
772 physical registers by `bsgen.allocate`, a linear scan; the allocated program is
executed in control (n) and agrees with the SSA program lane for lane.

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

Gate mix: xor 12146, and 8175, or 4075, not 248; 24644 instructions. Program
sha256 (canonical JSON of the instruction list, reproduced inside the packaged audit
program) = `0409d6c14b9ad19377982c44647c19f0f3df277a078738e93bafdf72bc3d959e`. Peak live plane registers: 772; no spill, so the main loop
has no loads or stores. The eight output words of one batch are the message words of
the next batch, so chaining costs no moves.

### 3.2 The 2-lane recovery circuit

Recovery walks exactly two trails, so it does not use the 256-lane step: a batch of
that step costs 24659 operations whatever it holds. `bsgen.build_recovery`
emits a separate scalar straight-line circuit - one 32-bit register per word, constants
as immediates, the same prices (1 per add, xor, rotate) - that advances **both** lanes
one compression each per step. Its measured size is **792
operations per step for two lanes**, plus 27 per-step control
operations (step counter, the 113-bit test of two lanes, the two-lane equality
test, the checkpoint countdown): **819 operations per step**, i.e.
819 / 2 = 409.5 operations per evaluation. The circuit is checked
against the scalar reference in control (rec) (0 lane differences at full 256-bit
width) and a corrupted copy is rejected.

## 4. Ledger: every row of N

All rows are computed by `ledger.py` from the emitted programs. Every row is a fixed
integer hard bound; the failure probabilities that make them hard bounds are in
section 6.3.

| row | value |
| --- | --- |
| gates per 256-lane batch | 24644 |
| per-batch control (counter, branch, 12-plane first-stage filter, branch) | 15 |
| operations per batch | 24659 |
| operations per F-evaluation in the search | 96.324219 |
| evaluations in the B batches | 339 177 502 524 764 998 185 226 066 825 424 143 616 (log2 127.99530809) |
| batches B | 1 324 912 119 237 363 274 161 039 323 536 813 061 |
| main loop, B x 24659 | 32 671 007 948 274 140 977 537 068 679 094 273 271 199 |
| second-stage DP test, passing-batch cap 80360264961710192455907226985624269 x 102 | 8196747026094439630502537152533675438 |
| drain to distinguished points, 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations | 344 099 029 630 515 220 197 071 305 389 765 558 272 |
| DP handlers and lane restarts, 35000 entries x (8 + 65536 x 4 + 256) | 9 184 280 000 |
| recovery on the 2-lane circuit, 155 768 905 756 044 828 855 914 889 876 602 880 steps x 819 | 127 839 476 303 805 379 402 349 873 789 865 164 800 |
| slice checks (age vs the cut), ceil(B / 2^48) x 1300 | 6 119 143 431 990 083 060 190 300 |
| start-point generation, 35 257 starts x 1 compression | 29 827 422 |
| setup: generator, folding, allocation, verification runs (bound) | 1 073 741 824 |
| **total N (word operations)** | **33 151 143 201 234 562 135 910 424 385 519 785 709 255** |
| reference operation cost C (blake3-r4) | 846 |
| **time_log2 = log2(N / C)** | **124.88167**, claim 124.88167 |

C = 846 is the organizer counter's own count for one 4-round compression
(`pareto.targets.reference_cost('blake3', 4)`); `dpcheck.py` obtains the same number from
that function rather than from `ledger.py`. 80-digit decimal arithmetic gives
time_log2 = 124.88166856421509244485177956124202754177307632579720088372422253886953593706768. The second-stage row is charged at the hard cap
80360264961710192455907226985624269 = (1 + 2^-10) x 80281864703210962999852683349540669.323 + 64 on the number of passing batches (failure
0.000e+00); at the mean it would be 8188750199727518225984973701653148271, so the cap is the honest row.

### 4.1 Lane audit: how many lanes each row fills, and at what price

The defect of our submission 4 was a row priced at the 256-lane amortised cost while it
filled two lanes. Every row is therefore listed with the number of lanes it actually
fills, the price used, and why that price applies.

| ledger row | lanes filled | price used | why this price |
| --- | ---: | --- | --- |
| main loop | 256 | 24659 ops per batch = 96.324219 per evaluation | all 256 lanes hold a live walk, one evaluation each per batch |
| second-stage DP test | 256 | 1 op per plane AND (102 per passing batch) | a plane AND covers all 256 lanes; the row is per passing batch, not per evaluation |
| drain | 256 | 24659 / 256 per evaluation | all 256 lanes are advanced during the drain |
| DP handler / lane restart | per event | 8 + 65536 x 4 + 256 ops per event | the 256-plane rewrite is 256 plane writes at 1 op each (256 lanes); the probe is scalar at 4 ops per slot, charged at the structural bound of the table |
| **recovery** | **2** | **819 ops per step for 2 lanes (409.5 per evaluation)** | **its own 2-lane circuit; the 256-lane amortised price (96.324219) is NOT used** |
| slice checks | 256 | 1300 ops per check (256 ages x 4 + counters) | one age compare per lane |
| start generation | 1 per start | 846 ops per start (one compression) | scalar regeneration of a start point |
| setup | - | 1 073 741 824 word operations (bound) | generator, folding, allocation, verification |

No row that fills fewer than 256 lanes is priced at the 256-lane amortised cost: the
only sub-256-lane row is recovery, and it carries its own circuit's count. This table is
the stop rule of this package: a row using fewer than 256 lanes at a 256-lane price
would invalidate the entry, and there is none.

## 5. Memory, the table, and the setup peak (findings F4, F3, LC-TABLE-1, LC-PROB-3)

| item | bytes |
| --- | ---: |
| code: 24644 allocated gate records x 4 | 98 576 |
| distinguished-point table: 65 536 slots x 8 | 524 288 |
| registers: 772 planes x 32 | 24 704 |
| lane state: 256 birth ages x 8 | 2 048 |
| counters, limits, trail pointers | 64 |
| stage-1 hit mask (256 bits) | 32 |
| advice: P and K | 96 |
| **total** | **649 808 = 2^19.30965**, claim 19.30966 |

The memory term is max(0, 19.30966 - 20) = 0.00000, so the score is the
time row alone.

**Slot layout.** A slot is 8 bytes, little endian: `(key << 16) | trail_id`.

* The *trail id* is a 16-bit counter incremented for every trail started. The plan
  starts at most 35 257 trails (one per stored DP, 256 initial trails and one
  cut trail), which is below the reserved value 0xFFFF, so ids never collide with the
  empty marker and **distinct entries always carry distinct trail ids**. The id is
  injective by construction, not by assumption.
* The *start point* of trail i is regenerated, not stored: s_i = the i-th 256-bit block
  of SHAKE256(seed), the 256-bit algorithmic coin of section 6.1.
* The *key* is bits 113..160 of the endpoint's digest, i.e. the 48
  bits **immediately above the distinguished-point test**. The low 113 bits are
  zero for every stored endpoint by definition, so a key taken from them would be the
  constant 0 (the defect of our submission 2, section 9.7).
* Reconstruction of an entry (key, id): regenerate s_id, walk F to the DP, check that
  its bits 113..160 equal `key`. The map entry -> (trail, endpoint) is a
  function of the stored bytes and the public seed, and it is injective on trail ids.

**The table algorithm, as implemented (LC-TABLE-1, F-EVAL-1).** `table.py` is shipped,
is embedded verbatim in the packaged audit, and is what the search and the audit both
execute:

1. `home(key) = ((key * 0x9E3779B97F4A7C15) mod 2^48) >> 32`, i.e. the top 16 bits of a
   48-bit multiplicative hash, so the home slot is a uniform function of the key.
2. `insert(key, id)`: visit the home slot, then slots +1, +2, ... modulo 2^16 (linear
   probing). At each slot: if it is empty (trail id 0xFFFF) write `(key, id)` and stop;
   if it holds the same key, return the id already stored there - **that duplicate is
   the merge report**; otherwise continue.
3. `lookup(key)`: the same scan, returning the id stored under `key` or "not present".
4. **Failure rule**: (a) the search stops when the table holds 35000 entries
   (capacity rule; the event "the realised number of DPs exceeds 35000" is bounded in
   6.3); (b) the probe is bounded by the table size, 65536 slots (the scan wraps
   modulo 65 536). Since the table never holds more than 35000 < 65 536
   keys, at least one slot is empty and the scan therefore always terminates within that
   bound: **the bound can never bind, the event has probability 0, and no probability
   estimate is needed** - the row charges the bound, it does not assume it. A smaller
   bound is a parameter of `table.py`; reaching it raises `ProbeExhausted` and the
   attempt is declared failed, which control (p) exercises on a deliberately tiny table.
   Measured on the real fill: the longest probe over 35 000 inserted keys is
   26.
5. Occupancy 35 000 entries in 65 536 slots, load 0.534058; the plan refuses
   an entry only above 3/4 load (49 152 entries), which is far above the expected
   count 33005, so no entry is dropped in practice (`dpcheck.py` re-derives it).

**Memory as implemented, not assumed (F3).** The emitted program is SSA with 24,900
names, so a 10-bit register field needs a real allocation step: `bsgen.allocate` renames
the program onto **exactly 772 physical registers** (772-1 = 771 is rejected,
control (n)), and the allocated program reproduces the SSA outputs with 0 differences.
The audit builds the claimed 4-byte image (98 576 B), fills the shipped table with
35 000 real 48-bit keys and looks every one of them up **by key** (524 288 B,
0 misses), recomputes the peak plane count, and sums the components above: the result is
649 808 B, equal to the ledger row, and the audit reports `memory_match = 1`. A
3-byte record cannot hold the image and is rejected.

**Setup peak, bounded explicitly (LC-MEMORY-SETUP-PEAK-GAP).** The setup phase holds the
code image at its final size (98 576) + the allocator's SSA-to-physical map
(49 800 = 24,900 names x 2 B) + the generator's constant tables and records
(4,096) + the register file it fills (24 704) + counters (64) +
advice (96) = **177 336 B < 649 808 B**. The packaged audit
recomputes that sum from the measured image and the program's register count and requires
equality with the ledger row. The recovery phase reuses the dead table region for the
checkpoints (524 288 B = 2 x 8192 x 32), so code + registers +
checkpoints + counters + lane state = 649,680 B is also below the search-phase total.

## 6. Probability space and success probability (findings F5 and F2)

### 6.1 The algorithmic coins (F5)

The target F is fixed. The only randomness of the algorithm is the **seed**, a uniformly
random 256-bit string sampled once per attempt, from which every start point is derived
deterministically: s_i = block i of SHAKE256(seed). A lane restart takes the next unused
s_i, so the whole run - start points, restarts, trail ids, cuts, the drain - is a
deterministic function of `seed`. The probability in the claim is over the uniform
`seed`, for the fixed target. Generating the start points is charged in the ledger (one
compression per start, 29 827 422 word operations).

### 6.2 The birthday count actually charged (F2)

The search succeeds when two evaluated points coincide; their two predecessors are then
distinct inputs with equal images (section 7). Under H1 the number of such repeats among
n evaluated points of a random mapping on 2^256 points is Poisson with mean
n(n-1)/2^257, so P(n) = 1 - exp(-n(n-1)/2^257). Q = 339 177 502 524 764 998 185 226 066 825 424 143 433 is the least integer
with P(Q) >= 0.39 + 0.0015, which gives P(Q) = 0.391500000000.

**The point count used for P is the charged point count**, n = B x 256 + drain =
342 749 802 763 436 959 593 655 048 299 927 569 664: the batches contribute 339 177 502 524 764 998 185 226 066 825 424 143 616 points and the drain contributes
3 572 300 238 671 961 408 428 981 474 503 426 048, and every point of both parts lies on a trail whose endpoint is stored,
because a lane is never stopped in mid-trail - it is either at a DP or it is drained to
one, and the drain is a hard window (below). P(n) = 0.397867303429.

The loss this row removes, and its price:

* A lane stopped after a random number of steps has a residual geometric tail of mean
  2^113, so the 256 lanes leave 256 x 2^113 unfinished points on average - 0.78% of the
  birthday count, which is the arithmetic of `F2-terminal-trail-success-loss`. A mean is
  not a bound, so the plan does not use one: the drain is a **hard aggregate window** of
  1.34375 x 256 x 2^113 = 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations (1.053224% of the batch
  points, 0.01512 bit), and a lane still unfinished when the window closes is
  truncated and the attempt is declared failed (probability 4.282e-06).
* Without that row the effective count would be 339 177 502 524 764 998 185 226 066 825 424 143 616 - 3 572 300 238 671 961 408 428 981 474 503 426 048, whose repeat
  probability is 0.385133132568 - **below 0.39**, exactly the judge's
  finding. It is not a rounding problem: 0.0015 of margin cannot cover a 1.56% loss of
  collision intensity.
* Two honest repairs exist: charge the drain (this ledger: the loss disappears, cost
  0.01512 bit), or leave the plan and raise the batch count by 1/(1 - 1.053224
  /100) = 1.010644, which costs 0.01528 bit and leaves the 1.56% loss in the
  model. This entry takes the first.
* Nothing in the success probability is left to the 0.0015 margin: the DP count, the
  drain window, the cut, the passing-batch count, the recovery cap (two tails), the
  false key report and the start-boundary case are separate hard caps with their own
  bounded failure probabilities, total 1.758e-5 (section 6.3).

### 6.3 The hard caps and the failure budget (union bounds over all trails started)

Every row of the ledger is a deterministic integer, so the time claim needs no
concentration argument for work; what remains is the probability that a hard bound is
too small for the realised run. Each such event is a failed attempt and is subtracted
from the success probability. The union bounds are over **all trails started**
(35 257 of them), not over the 256 lanes: a trail that restarts is a new
trail, and a cycle entered by an earlier trail is an event of the trail that entered it.

| cap | hard value | failure event | probability |
| --- | ---: | --- | ---: |
| drain window | 1.34375 x 256 x 2^113 | the sum of 256 residuals exceeds it | 4.282e-06 |
| distinguished-point count | 35000 entries (mean 33005) | the realised count exceeds the cap | 2.122e-26 |
| passing batches | 80360264961710192455907226985624269 (mean 80281864703210962999852683349540669.323) | the realised count exceeds the cap | 0.000e+00 |
| trail cut | 24 x 2^113 evaluations | some started trail reaches the cut | 1.331e-06 |
| recovery cap, two tails | 15 x 2^113 steps per trail | a merge-conditioned trail is longer | 9.789e-06 |
| false key report | 35000 keys, 48 bits | a non-merge key match (lambda = 2.18e-06) | 2.176e-06 |
| recovery start boundary (LC-COLL-1) | first aligned equality at a trail start | equal starts, or one start on the other trail | 2.690e-42 |

* drain window: for a sum of 256 iid exponentials of mean 2^113 the Chernoff exponent is
  256 (c - 1 - ln c) with c = 1.34375, which gives 4.282e-06;
* DP count: multiplicative Chernoff for a sum of indicators, P(N > 1.060445 lambda)
  <= exp(-lambda ((1.060445) ln(1.060445) - (1.060445 - 1))) = 2.122e-26;
* passing batches: the same Chernoff at 80360264961710192455907226985624269 = (1 + 2^-10) x 80281864703210962999852683349540669.323 + 64, which
  gives 0.000e+00 (it underflows the printed double; the exponent is -3.6e22);
* **cut**: a trail's length is geometric with mean 2^113 under H1, so
  P(one trail reaches 24 x 2^113) = e^-24 = 3.775e-11; the union bound
  over all 35 257 trails started gives 1.331e-06. The cut is also what makes
  the DP-free-cycle case of `LC-PROB-2` a bounded failure: a trail inside a cycle that
  contains no DP reaches the cut, the attempt fails, and the event is in this row
  (there is no separate orbit window and no per-lane shortcut);
* recovery: length is conditioned on producing a merge, which biases it upwards, so the
  row uses the size-biased bound P(L > c x 2^113 | merge) <= (c + 1) e^-c =
  4.894e-06 at c = 15, **once per trail** (both trails of the report,
  the finding LC-PROB-4), total 9.789e-06;
* false key report: distinct endpoints share a 48-bit key with probability 2^-48; over
  the plan the expected number of false reports is C(35 000,2) x 2^-48 =
  2.18e-06, and a false report is resolved by the same recovery walk and then fails
  the attempt: 2.176e-06;
* start boundary: if the first aligned equality is at the start of either trail (equal
  starts, or one start on the other trail), recovery has no predecessors to output, so
  it returns "no pair" and the attempt fails: 2 x TRAIL_CAP x 2^-256 = 2.690e-42,
  charged as 2.690e-42.

Total failure budget 1.758e-5 < 1e-4. The margin is 0.0015, so the plan's success
probability is at least P(n) - 1.758e-5 = 0.397849725886 > 0.39. No
amplification is claimed: one attempt, one seed.

## 7. Recovery of the colliding pair (findings F1, F4, LC-PROB-1, LC-COLL-1)

A table report gives two trail ids with equal 48-bit keys. Recovery uses the **2-lane
circuit of section 3.2** - two lanes, one step per batch - and the checkpoints that
`F1-recovery-work-omitted` asked for:

1. **Pass 1 (measurement, with checkpoints).** Regenerate both starts, walk the two
   trails together, one circuit step per batch. After every step number that is a
   multiple of D = ceil(TRAIL_CAP / 8192) = 19 014 759 003 423 441 022 450 548 080 640, store both
   current points as a checkpoint pair in the table region (the table is dead after the
   search: 524 288 B, inside the 524 288-byte table). Each lane stops at
   its first DP; the step counts are L_A, L_B, and because both trails end at the same
   DP the difference d = |L_A - L_B| is the merge-time offset. The walk is capped at
   TRAIL_CAP = 15 x 2^113 = 155 768 905 756 044 828 855 914 889 876 602 880 steps (failure probability
   4.894e-06 per trail, section 6.3).
2. **Pass 2 (bisection).** For the longer trail A and the shorter B, the predicate
   "A(j) = B(j - d)" is false up to the merge and true from it on, so the merge index j
   is found by bisection over the checkpoint grid: at most 17 probes, each re-walking at
   most D steps from the nearest checkpoint of each trail. The predecessors are
   x = A(j-1), y = B(j-d-1); they are distinct and F(x) = F(y). If the first true index
   is j = d (B's start lies on A's trail) or j = 0 (equal starts), there are no
   predecessors: recovery returns "no pair", the attempt is a failed one, and the event
   is charged at 2.690e-42 (LC-COLL-1; control (lc-coll-1) exercises all three
   cases).
3. **Charge.** The row is fixed:
   TRAIL_CAP x 819 + 8192 x 80 + 17 x D x 819
   = 127 839 476 303 805 379 402 349 873 789 865 164 800 word operations (0.00555 bit of the score). 1
   report is resolved; a false report costs the same walk and then fails the attempt
   (2.176e-06).

Nothing here is priced at the 256-lane amortisation: the circuit fills 2 lanes and the
row uses that circuit's own count (section 4.1). Submission 1 charged 2^34 operations
here, which was far too small; submission 4 divided the 256-lane batch price by 256 for a
2-lane walk, which is the fatal of `ac1e76f4`. The checkpoint/bisection procedure and the
cap c_r = 12.4 L convention are credited to the public proof of `33f00b84` (section 9.17).

## 8. Controls, all run on this machine

(a) Emitted program vs a plain scalar 4-round reference (section 2 formula, written
independently of the generator), 4096 chains x 16 chained steps:

    (a) emitted net vs plain 4-round reference: lanes 256 steps 4 evaluations 1024 lane-diffs 0
    (a2) emitted net vs plain 4-round reference: chains 4096 x 16 steps evaluations 65536 lane-diffs 0

(b) The same reference and the emitted program against the repository verifier
(`verifier/blake3.py`, rounds = 4) on complete messages K || x:

    (b) own scalar reference vs repo verifier/blake3.py (rounds=4): messages 512 diffs 0
    (b2) emitted net vs repo verifier/blake3.py (rounds=4): lanes 256 diffs 0

(c) Regeneration and ledger determinism: three independent builds give the same program
sha256, and three ledger runs are byte-identical:

    (c1) program regeneration: 3 builds sha256 equal True 0409d6c14b9ad19377982c44647c19f0f3df277a078738e93bafdf72bc3d959e
    (c2) ledger regeneration: 3 runs byte-identical True sha256 6acb75550f2840d34ac7698afd1dbfc147e5dfaa0a8b98fea8b49bc28d4de66f

(d) The score is re-derived from the rounded claim with the repository's own scoring
code, `pareto.scoring.normalized_score('blake3', metrics)`: 124.88167; the ledger and
the claim agree, and the claim is never below the recomputed exact values.

(e) Negative control: a single gate of the emitted program is changed (xor <-> and) at
three positions; the comparison that reports 0 differences above then reports
differences and rejects the program:

    (neg) single-gate corruptions at 3 positions: lane-diffs [430, 320, 420] rejected True

(f) Independent re-derivation: `dpcheck.py` does not import the ledger module. It
recounts the emitted instruction lists, solves the success equation by integer
bisection, re-prices the drain, DP-test, handler, recovery, slice and generation rows
from the plan, checks the table and trail-id bounds, recomputes the F2 conditional and
the whole failure budget, and recomputes the score from the rounded claim:

    gates 24644 ops/batch 24659 ops/eval 96.324219
    Q 339177502524764998185226066825424143433 (P = 0.391500000000 >= 0.3915) log2 Q 127.99530809
    batches 1324912119237363274161039323536813061
    rows: main 32671007948274140977537068679094273271199 dp_test 8196747026094439630502537152533675438 (pmax 80360264961710192455907226985624269) drain 344099029630515220197071305389765558272 handler 9184280000 recovery 127839476303805379402349873789865164800 (2-lane circuit 792 + 27 per step, 155768905756044828855914889876602880 steps) slices 6119143431990083060190300 gen 29827422 setup 1073741824
    total 33151143201234562135910424385519785709255
    time_log2 124.88167 (claim 124.88167)  memory_log2 19.30965 (claim 19.30966) term 0.00000
    memory: image 98576 + table 524288 (probe_max 26) + registers 24704 + counters 64 + lane ages 2048 + mask 32 + advice 96 = 649808 B; setup peak 177336 B < 649808 B
    F2: drain 3572300238671961408428981474503426048 = 1.05322% of 339177502524764998185226066825424143616; P(all charged points) 0.397867303429; P without the drain row 0.385133132568 (< 0.39)
    union bounds over 35257 trails: cut 24 x 2^113 -> 1.331e-06; recovery cap 15 x 2^113, two tails -> 9.789e-06; false key reports lambda 2.176e-06; drain 4.282e-06; DP cap 35000 vs mean 33005 -> 2.122e-26; passing batches cap 80360264961710192455907226985624269 -> 0.000e+00; start boundary 2.690e-42; budget 1.758e-05
    reference cost C 846 (blake3 r4)
    memory as implemented: allocated image 98576 B (4 B x 24644, physical regs 772 < 1024), table probe 524288 B (35000 entries round-trip), total 649808 B
    key: bits 113..160 of the endpoint (above the DP test), 48 bits
    table: 35000 keys in 65536 slots (load 0.5341), linear probing bounded at 65536; trail ids 35257 < 65535 -> True
    score from rounded claim 124.88167
    score(repo scalar_score) 124.88167  display(claim) 124.88167
    DP accounting re-derived independently: OK

(g) Toy-width end-to-end run of the search itself (walk, cut, distinguished-point table,
restarts, checkpointed recovery on the emitted 2-lane circuit) driven by the emitted
256-lane net, every recovered pair rechecked against the repository verifier:

    toy width 18 dp_low 4 lanes 256 trials 64 pairs 54 bad 0 aborted 10 evaluations 106240 evals/trial 1660 expected 642 table max_probe 4 recovery circuit steps 1394
    toy width 20 dp_low 4 lanes 256 trials 64 pairs 50 bad 0 aborted 14 evaluations 164352 evals/trial 2568 expected 1283 table max_probe 3 recovery circuit steps 1809

Aborted trials are the cut failures, trials with no report and reports whose recovery
found no merge (`LC-COLL-1`); they are counted, not hidden. At toy width the DP lag is a
large fraction of the birthday length, which is why evaluations per trial exceed the
ideal 1.25 x 2^(n/2); at width 256 the same lag is 2^-113 against 2^128 and the terminal
part of it is the drain row.

(h) Constant-prefix scan: 65536 seeds for K priced with the emitter's constant rule never
beat K = 0^32; the 24644 gates are the K = 0 build.

(i) Round parametricity: the same generator at rounds = 7 emits 46196 gates (xor
22778, and 15495, or 7675, not 248) and matches `verifier/blake3.py` at
rounds = 7 for 256 lanes, 0 differences.

(j) Adder verification, independent of the compression (`verify_adder.py`), on the
emitted bit-sliced net of each adder:

    (v0) fused 8-gate column: failing cases 3 [(1, 1, 1, 1, 1), (15, 1, 1, 1, 1), (30, 1, 1, 1, 1)] all-sum-to-4 True
    (v2) three-addend adder (two ripple adders) vs integer arithmetic: triples 1048576 bad 0
    (v3) two-addend adder vs integer arithmetic: pairs 1048576 bad 0
    (v4) constant adder vs integer arithmetic: constants 4134 pairs 1058304 bad 0 (flags out of the adder 65891)
    ADDER VERIFICATION CLEAN (fused column fails only on sum 4, as documented)

(l) Package integrity: `mkpackage.py --check` refuses a claim below the recomputed
ledger. Tampering time_log2 to 124.0 is rejected, and so is any claim below the
recomputed rows.

(m) Adder enumeration (`adder_enum.py`), independent of the compression: every
AND/OR/XOR program over the column inputs is enumerated (unbounded fanout; NOT and the
constants 0/1 granted free), so the column prices of section 3 are proved, not assumed:

    (m1) full-adder column: no program with <=4 gates = True; least gates = 5
    (m2) half-adder column (a,b)->(sum,carry): least gates = 2
    (m3) top column (a,b,cin)->sum: least gates = 2
    (m4) three-addend one-carry column: unsound at input bits 1111 (a=b=c=cin=1, sum 4): one carry bit cannot represent it, for every carry function
    (m5) closed form 2 + 5*(32-2) + 2 = 154 = 5n-6; emitted two-addend 32-bit add = 154 gates

The one-carry three-addend column is impossible for every carry function (sum 4 needs
two carry bits), which is why `wadd3` uses two ripple adders (308 gates).

(n) Memory as implemented (F3, LC-MEMORY-SETUP-PEAK-GAP). `bsgen.allocate` renames the
24,900 SSA registers onto physical registers by linear scan; the allocated program is
executed against the SSA program, the packed 4-byte image is built from the allocated
instructions, the shipped table is filled with 35 000 real 48-bit keys and looked
up by key, and the setup peak is recomputed:

    (f3) allocated image 98576 B (4 B x 24644, physical regs 772), allocated net equals SSA True, 771-register file rejected True, key table 524288 B (lookup misses 0, max probe 26), total 649 808 B = ledger 649 808 -> True; setup peak 177 336 B < 649 808 B; 3-byte record total 625164 B rejected True

(o) Full-width circuit probe of the **shipped** net (local control, `control_f5`):
256 points at width 256 through the emitted net, compared with the scalar
reference on every one of the 256 bits, and the same probe with one gate corrupted:

    (f5) full-width (256-bit) net vs scalar: lanes 256 diffs 0, 20-bit agreeing pairs 0 (expected 0.03); corrupted net diffs 186 rejected True

This runs on this machine only; it is **not** part of the organizer execution and is not
described as such. It is a circuit statement at full width, not a probability
measurement, and none is claimed from it (section 10).

(p) The table (LC-TABLE-1, F-EVAL-1), positive and negative:

    (tbl) 48-bit keys 35000 in 65536 slots, lookup misses 0, absent key found False, max probe 26 <= 65536; cluster of 65 keys raises ProbeExhausted True; insert at capacity raises TableFull True

(q) The 2-lane recovery circuit (findings F1, LC-COST-RECOVERY-LANE-AMORTIZATION):

    (rec) 2-lane recovery circuit: ops 792 per step for 2 lanes, compressions 64 lane-diffs 0; corrupted gate rejected True

(r) Organizer-executed experiment (`experiments/b3r5_audit.py`, declared below): the
harness runs it twice in its pinned sandbox and recomputes every returned pair with its
own digest. The program re-executes the *embedded verbatim* generator, ledger and table
sources and requires gate count 24644, operations per batch 24659, program
sha256 `0409d6c14b9ad19377982c44647c19f0f3df277a078738e93bafdf72bc3d959e`, total N and score 124.88167; it compares **all 256 lanes of
the first round at full 256-bit width** with the scalar reference; it builds the packed
4-byte image, fills and looks up the shipped 65 536-slot table by key, recomputes
the memory and setup-peak rows; and it derives every trial's start points from that
trial's organizer seed, evaluates them with the emitted bit-sliced net, and detects the
shared key **through the shipped table** (`insert` returns the duplicate id), returning
for each trial a pair, unique across trials, whose two distinct messages contain one of
that trial's own points and whose complete digests agree on the low 8 bits.
The masked-agreement search is a miniature of the charged search: seeded start points,
batched evaluation on the shipped program, the shipped table as the detector.
The declared experiment source is 56 129 bytes (review budget 65,536). What it
does **not** do: it does not run 2^128 evaluations, it does not measure the width-256
collision or DP statistics, and its 256 masked successes are not used for any
probability or cost inference (the organizer report's own
`probability_inference: none`, `cost_trust: no_attack_cost_inference` are quoted, not
overridden).

## 9. Every finding of the four reviews, answered for this package

All four of our earlier submissions were refuted on the *accounting text and its
evidence*; the circuit and the search were never challenged. `closed` means the package
contains the mechanism, the number and a control that can fail; `argued` means the item
is a declared premise or a declared experiment scope, whose content and cost are stated
with no claim beyond it.

| # | finding (verdict) | severity | where this package answers it | status |
| --- | --- | --- | --- | --- |
| 1 | `lane_cost/F1-recovery-work-omitted` (ca864586) | fatal | sections 4.1, 7: 2-lane circuit row 127 839 476 303 805 379 402 349 873 789 865 164 800 ops, checkpoints, cap 15 x 2^113 | closed |
| 2 | `lane_cost/F2-terminal-trail-success-loss` (ca864586) | fatal | 6.2/6.3: drain row 344 099 029 630 515 220 197 071 305 389 765 558 272 ops, every charged point DP-terminated; undrained P printed | closed |
| 3 | `lane_cost/F3-missing-executable-cost-artifacts` (ca864586) | material | 9.3: `experiments/` ships generator + ledger + table verbatim in one declared program, executed by the organizer | closed |
| 4 | `lane_cost/F4-recovery-metadata-unexplained` (ca864586) | material | section 5: 48-bit key + 16-bit id, 35 257 < 65535, injective reconstruction, checkpoints | closed |
| 5 | `lane_cost/F5-probability-space-unspecified` (ca864586) | material | 6.1: one 256-bit seed, SHAKE256 start points, generation charged | closed |
| 6 | `lane_cost/F6-score-rounding-inconsistency` (ca864586) | minor | section 1 + control (d): score from the rounded claim, repo scorer agrees | closed |
| 7 | `lane_cost/dp-key-degenerate` (61b9dbc0) | fatal | 9.7: key = bits 113..160, above the DP test | closed |
| 8 | `lane_cryptanalysis/F1-distinguished-key-is-constant` (61b9dbc0) | fatal | 9.7: same; a merge forces equal keys because the endpoints coincide | closed |
| 9 | `lane_cost/random-tail-budget` (61b9dbc0) | fatal | 6.3, 7: hard aggregate caps for drain and recovery, budget 1.758e-5 | closed |
| 10 | `lane_cost/F1_random_dp_work` (f447d13d) | fatal | 6.3: DP count charged at 35000 > mean 33005, Chernoff 2.122e-26 | closed |
| 11 | `lane_cost/F2_dp_processing_omitted` (f447d13d) | fatal | section 4, 6.3: per-batch first stage, second stage at the hard passing-batch cap 80360264961710192455907226985624269, 256-plane restarts | closed |
| 12 | `lane_cost/F3_memory_implementation_gap` (f447d13d) | material | section 5 + control (n): packed image built and executed, key table filled and looked up, 771-register file refused, setup peak bounded | closed |
| 13 | `lane_cost/F4_recovery_failure_budget` (f447d13d) | material | 6.3, 7: size-biased tail per trail, false-report Poisson term, start-boundary term | closed |
| 14 | `lane_cost/F5_full_width_probability_gap` (f447d13d) | material | 8(o), 10: full-width circuit probe; probability is H1, sensitivity priced | argued |
| 15 | `lane_cryptanalysis/LC-PROB-1` (f447d13d) | material | 6.3, 7: collision-conditioned tail 9.789e-06 over both trails | closed |
| 16 | `lane_cryptanalysis/LC-PROB-2` (f447d13d) | material | 6.3: the cut makes a DP-free orbit a bounded failed attempt, 1.331e-06 unioned over trails | closed |
| 17 | `lane_cryptanalysis/LC-HEUR-1` (f447d13d) | material | 8(o), 10: same content as #14, stated as a premise | argued |
| 18 | `lane_cryptanalysis/LC-COLL-1` (f447d13d) | minor | 6.3, 7 + control (lc-coll-1): rejection and 2.690e-42 deduction | closed |
| 19 | `lane_experiments/EXP-F1` (f447d13d) | material | 8(g), 8(o), 8(r): circuit and search probes; no probability inference | argued |
| 20 | `lane_experiments/EXP-F2` (f447d13d) | material | controls (exp-f2), (r): the pair search calls the emitted net and the shipped table; a corrupted net is rejected | closed |
| 21 | `lane_cost/LC-COST-RECOVERY-LANE-AMORTIZATION` (ac1e76f4) | fatal | 4.1 lane audit, 3.2, 7: recovery is its own 2-lane circuit at 819 ops per step; the 256-lane price is not used | closed |
| 22 | `lane_cost/LC-MEMORY-SETUP-PEAK-GAP` (ac1e76f4) | material | section 5: setup peak 177 336 B, itemised and recomputed by the audit | closed |
| 23 | `lane_cost/LC-TABLE-1` (ac1e76f4) | material | section 5: home slot, linear probing, bounded at 65536, failure rule, capacity rule; audit looks keys up | closed |
| 24 | `lane_cost/LC-PROB-3` (ac1e76f4) | material | 6.3: every union bound is over 35 257 trails started, not over 256 lanes | closed |
| 25 | `lane_cost/F-EVAL-1-table-algorithm-unspecified` (ac1e76f4) | material | section 5 + controls (p), (r): the shipped table is the one the audit executes | closed |
| 26 | `lane_cost/F-EVAL-2-random-mapping-support-gap` (ac1e76f4) | material | 8(r), 10: H1 declared; organizer evidence is circuit/search only | argued |
| 27 | `lane_experiments/EXP-FULLWIDTH-CROSSCHECK-OVERSTATED` (ac1e76f4) | material | 8(r): the audit compares all 256 lanes of the first round at full 256-bit width; the proof says only that, and the local probe is labelled local | closed |
| 28 | `lane_experiments/EXP-NO-RANDOM-MAPPING-STATISTICS` (ac1e76f4) | material | 8(r), 10: no statistics are claimed from the organizer run | argued |
| 29 | `lane_cost/LC-PREPROCESSING-UNIT-LABEL` (ac1e76f4) | minor | sections 1, 4: preprocessing reported as 20.27549 compression units, not 2^30 | closed |
| 30 | `lane_cost/LC-PROB-4` (ac1e76f4) | minor | 6.3: the size-biased cap tail is charged once per trail, 9.789e-06 | closed |

The earlier reviews' other findings are aliases of the rows above:
`lane_cryptanalysis/F1-random-mapping-extrapolation` and
`lane_cost/random-mapping-evidence-gap` are #14/#17; `lane_cryptanalysis/F2-dp-loss-bound`
and `lane_evaluability/F-EVAL-3` are #9/#13; `lane_cryptanalysis/F3-recovery-not-auditable`,
`F-EVAL-1`, `EXP-1`, `EXP-3`, `EXP-4` are #1/#3/#4 (the package carries the sources, the
slot layout, the table and the recovery procedure); `F-EVAL-2` and `F-EVAL-4` are #5 and
the organizer-executed experiment; `lane_cost/machine-storage-accounting-gap` is #12;
`lane_experiments/EXP-F1-limited-event-scope` is #19;
`lane_experiments/EXP-F3-full-search-unexecuted` is declared: the full search is not
executed by the organizer (it is 2^128 work), and the report's
`cost_trust: no_attack_cost_inference` is accepted and not overridden.

**9.1 F1 - recovery work (`ca864586`, #1).** The table now stores checkpoints during
recovery, and recovery is a dedicated 2-lane circuit: the row is
TRAIL_CAP x 819 + 8192 x 80 + 17 D x 819 =
127 839 476 303 805 379 402 349 873 789 865 164 800 operations (0.00555 bit), with the trail cap and both tails in the
budget. Submission 1's 2^34 row was a guess; this row is derived from the trail geometry
and from the circuit that executes it.

**9.2 F2 - terminal trails (`ca864586`, #2).** The drain is a charged ledger row, not a
margin: 3 572 300 238 671 961 408 428 981 474 503 426 048 evaluations (1.053224% of the batch points, 0.01512 bit),
hard window 1.34375 x 256 x 2^113. Every charged point is DP-terminated, so P is
evaluated at the charged point count; the undrained plan's value 0.385133132568 is
printed and is below 0.39.

**9.3 F3 - executable cost artifacts (`ca864586`, #3).** The package declares and ships
`experiments/b3r5_audit.py` (56 129 bytes, inside the 65,536-byte review
budget). It contains `bsgen.py`, `ledger.py` and `table.py` **verbatim** (byte-identical
to the sources of this build, checked by `mkpackage.py --check`), and the organizer
harness executes it (control (r)). The emitted programs are therefore reproducible from
the package: load the embedded sources, call `bsgen.build()` and `bsgen.build_recovery()`,
and the canonical image must hash to `0409d6c14b9ad19377982c44647c19f0f3df277a078738e93bafdf72bc3d959e`.

**9.4 F4 - recovery metadata (`ca864586`, #4).** A slot is 8 bytes: 48-bit key + 16-bit
trail id; the plan starts at most 35 257 trails, below the reserved id, so ids
are injective by construction. Start points are regenerated as blocks of SHAKE256(seed);
recovery checkpoints are 524 288 B in the dead table region; the reconstruction
(regenerate, walk to the DP, check the key) is written out in section 5.

**9.5 F5 - probability space (`ca864586`, #5).** One uniform 256-bit seed per attempt;
every start point is a deterministic SHAKE256 block, restarts take the next unused block,
generation is charged (29 827 422 operations). The probability is over the seed for the
fixed target.

**9.6 F6 - score rounding (`ca864586`, #6).** Both claim fields are ceil5 of the exact
values and every quoted score is computed from the rounded fields:
124.88167 + max(0, 19.30966 - 20) = 124.88167; `dpcheck.py` and the
organizer's `normalized_score` both print 124.88167.

**9.7 degenerate key (`61b9dbc0`, #7, #8).** The key is bits 113..160 of the
endpoint, the 48 bits immediately above the DP test, so it is not constant. Two distinct
endpoints share a key with probability 2^-48; over the plan the expected false reports are
2.18e-06, and a merge forces equal keys because the endpoints coincide. The slot stays
8 bytes.

**9.8 random tail budget / mean DP count / omitted predicate (`61b9dbc0`, `f447d13d`,
#9, #10, #11).** One root cause: a row charged at an expectation, or work outside every
row. Here the drain is a hard window (4.282e-06), the DP count is charged at
35000 > mean 33005 (2.122e-26), the passing-batch count at 80360264961710192455907226985624269
(0.000e+00), recovery at two capped tails (9.789e-06), and the predicate is a fixed
per-batch row: 12 plane ANDs every batch, 102 operations per passing batch, 8 handler
operations + 65536 x 4 probe operations + 256 plane writes per event. No row of the
time claim is a mean.

**9.9 memory implementation gap (`f447d13d`, #12).** Section 5 and control (n): the SSA
program is renamed onto exactly 772 physical registers (772-1 = 771 refused); the
allocated program reproduces the SSA outputs; the 4-byte image is built (98 576 B);
the shipped table is filled with 35 000 keys and looked up (524 288 B); the
total is 649 808 B = the ledger row; a 3-byte record is rejected. The setup peak is
bounded explicitly at 177 336 B.

**9.10 recovery failure budget (`f447d13d`, #13, #15).** The recovery tail is conditioned
on the merge, so the row uses the size-biased bound (c + 1) e^-c = 4.894e-06 at
c = 15, once per trail (9.789e-06). A false 48-bit report is resolved by the
same walk and then fails the attempt: 2.176e-06. Both are separate ledger terms.

**9.11 full-width probability gap / LC-HEUR-1 (`f447d13d`, #14, #17).** **Argued, not
closed**, and the package does not claim otherwise. Supplied: a full-width circuit probe
(256 points, 0 differences, local only), an organizer-executed experiment that
compares the first round at full width and runs the search on that net, and reduced-width
end-to-end runs at widths 18 and 20. None measures the width-256 collision probability,
which remains premise H1, with its price stated: 0.00725 bit at 1%, 0.03700 at 5%,
0.07601 at 10% merge-rate deficit.

**9.12 LC-COLL-1 (`f447d13d`, #18).** An equality at the start of either trail has no two
predecessors: recovery returns "no pair", the attempt fails, and the event is charged at
2.690e-42. Control (lc-coll-1) recovers a genuine merge, rejects equal starts and
rejects a start on the other trail; the toy driver counts those trials as aborted.

**9.13 recovery lane amortisation (`ac1e76f4`, #21, the fatal of our submission 4).** The
defect was exactly as stated: the row divided a 256-lane batch price by 256 while recovery
fills two lanes. This package has a dedicated 2-lane circuit (792
operations per step for two lanes plus 27 control operations),
executed in control (q), and the row uses 409.5 operations per evaluation - 4.25x the
search's 96.324219, as a two-lane scalar circuit should be. Section 4.1 lists every
row with its lane count and price; recovery is the only sub-256-lane row and it does not
use the amortised price.

**9.14 table algorithm (`ac1e76f4`, #23, #25; `61b9dbc0`'s probe concern).** `table.py` is
shipped, embedded verbatim in the audit, and executed by it: home slot from a 48-bit
multiplicative hash, linear probing bounded at 65536, duplicate key = merge report,
`ProbeExhausted` and `TableFull` as declared failure events with their probabilities.
Control (p) shows each rule firing; the audit's pair search detects its duplicate through
this table (`pair_source_table = 1`, 0 lookup misses over 35 000 keys).

**9.15 union bounds over trails (`ac1e76f4`, #24).** The DP-free-cycle term is no longer
"256 lanes": a trail that enters a cycle without a DP reaches the cut, and the cut is a
failed attempt unioned over all 35 257 trails started (1.331e-06). The recovery
tails are charged per trail (9.789e-06), and the probe bound is per event over
35000 events.

**9.16 preprocessing units (`ac1e76f4`, #29).** `preprocessing_log2` in the claim is
20.27549 compression units = 1 073 741 824 / 846, not 2^30 units. It is inside
the time bound, as stated in section 1.

**9.17 credits (read as data, no code used).** The cut-trail shape, the fixed per-batch
predicate row, the checkpoint/bisection recovery with c_r = 12.4 L, and the "union over
trails" discipline follow the public proof of `33f00b84` (mpjunior92, [3, 124.68326]) and
its references `2a5ed60e`/`e6c0380d`; the 2^48-batch slice check and the hard-cap style
also appear there. The alignment walk and the start-on-trail deduction follow the public
note of `e479cbbf` (Jbenisek). `77715f8b` was **rejected**, not accepted; only its public
note was read. Every line of the generator, the recovery circuit, the table, the ledger
and the checks in this package was written for this entry; no other solver's program was
downloaded, read as code, or run.

## 10. Premises, scope and limits

H1 (score-critical, declared, not proved): for uniformly random seeds on the fixed
4-round chain F, the quantities the search uses behave as on a random mapping on 2^256
points: (a) two distinct evaluated inputs collide with probability 2^-256; (b) the
iterates from the starts have the random-mapping first-collision and cycle law; (c) a
fresh output satisfies the 113-bit distinguished predicate with probability
2^-113, independently; (d) trails merge like independent random paths. H1 cannot be
tested at width 256. What is tested is the circuit at full width (control (o), local
only), the search mechanics end to end at widths 18 and 20 (control (g)) and the
organizer-executed net pair search through the shipped table (control (r)). None of these
is a width-256 probability measurement, and no such measurement is claimed from them.
Sensitivity: a merge-rate deficit eps costs 0.5 log2(1/(1-eps)) extra bits - 0.00725 bit
at eps = 1%, 0.03700 bit at 5%, 0.07601 bit at 10%.

H3 (supporting, declared): the machine convention of section 3 - 256-bit plane
registers for the search, 32-bit registers for the 2-lane recovery circuit, the prices
above, SSA with no moves, a 772-plane register file, no loads or stores in the main
loop, 4-byte gate records and 8-byte table slots. With fewer than about 40 planes the
loop would need spills and the bound would rise.

Limits: neither circuit is claimed minimal; the seven hard caps of section 6.3 are the
only places where the plan can fail for reasons other than H1. The row leader
(`e6c0380d`, [4, 124.78394]) is lower by 0.09773 bit because its generator finds a cheaper
adder family and a scanned constant block that this generator does not implement. No
differential attack is claimed; no witness is provided and the claim is a resource bound.

## 11. Reproduce

    python3 bsgen.py --gates          # emitted step: gate count and mix
    python3 controls.py               # (a), (a2), (b), (b2), (c1), (c2), (neg), (i),
                                      # (tbl), (rec), (exp-f2), (lc-coll-1), (f3), (f5)
    python3 table.py                  # the shipped table: fill, probe, max probe
    python3 ledger.py                 # every row of sections 4-6
    python3 dpcheck.py                # independent re-derivation (f)
    python3 toy.py                    # (g), toy-width search + checkpointed recovery
    python3 scan_key.py 65536         # (h), constant-prefix scan
    python3 verify_adder.py           # (j), adder verification
    python3 adder_enum.py             # (m), exhaustive column enumeration
    python3 mkpackage.py --check      # rebuild package + experiments, claim vs ledger
    python3 experiments/b3r5_audit.py < request.json   # (r), the declared experiment

The generator is deterministic: no randomness enters the programs, and the only
randomness of the search is the seed of section 6.1.
