# Three-round BLAKE3: plain distinguished-point collision search, fully priced

## 1. What this entry is

This candidate is a generic birthday-bound collision search against the
`blake3-r3-prefix-v1` target, priced completely under the
`collision-frontier-v5` word-RAM cost contract. It claims time 2^128.06
target-compressions at success probability at least 0.40 with at most 2^19.5
bytes of memory, no preprocessing and no advice.

The field `baseline_improved` names `blake3-r3-nominal-v2` because the claim
schema requires a reference identifier. This entry does not improve the
nominal 128-bit display reference. The nominal entry is a security claim, not
an established attack, and this entry is not an attack on the round-reduced
function in the cryptanalytic sense. It is a fully specified, auditable cost
point: every operation the search performs is charged, every loss of success
probability is bounded, and the single modelling assumption is isolated as
heuristic H1 and tested by an organizer-executed experiment.

## 2. Target and message family

The target hashes a finite byte string with three rounds of the BLAKE3
compression function in every compression, standard IV, no key, standard
padding and flags, and compares the full 256-bit digest.

Every message in this search is exactly 64 bytes long: 32 zero bytes followed
by the 32-byte little-endian encoding of a 256-bit value x. A 64-byte message
is one chunk holding one block, so its digest is a single compression call
with chaining value IV, the 16 message words of the block, counter 0, block
length 64 and flags CHUNK_START | CHUNK_END | ROOT = 11, with the 256-bit
digest read as the first eight output words. The hash computation of a message
of this family is therefore exactly one target compression; nothing else is
hashed.

Define F(x) = three-round digest of (0^32 || x), read as a 256-bit value
(little-endian). Two distinct values x != x' give two distinct messages,
because the message encodes x injectively. A pair x != x' with F(x) = F(x') is
a collision of two distinct 64-byte messages with identical full digests,
which is exactly the success event of the target profile.

## 3. Algorithm

The search is the sequential distinguished-point method (van Oorschot and
Wiener) applied to F, with the following fixed parameters.

* theta = 2^-115: a point y is distinguished when its low 115 bits are zero.
* Trail cap L_max = 2^119 = 16 / theta steps.
* Fresh-evaluation budget M = 2^128.03 steps for trail building.
* Total step budget B = M + 3 * 2^119 (trail building, the overrun of the
  last trail, and the walk-back of Section 3, step 5).
* Table of 9216 slots indexed by the distinguished value.

Steps:

1. Setup. Load the code, zero the table and the counters.
2. Start a trail. Draw one independent uniformly random 256-bit word s and set
   x = s, length = 0.
3. Extend. Replace x by F(x) and increment length. If x is distinguished, go to
   step 4. If length reached L_max, abandon this trail and go to step 2.
   If the global step counter reached B, stop and report failure.
4. Distinguished point. If the table has no entry for x, store (x, s, length)
   and go to step 2. If the table has an entry (x, s0, length0), go to step 5.
5. Walk back. Re-walk both trails from s0 and s in lockstep after discarding
   the leading steps of the longer trail, until the next points agree. If the
   two current points are equal before the next points agree, the shorter trail
   started on the other trail (same input, not a collision); discard the new
   trail and go to step 2. Otherwise the two current points a != b satisfy
   F(a) = F(b).
6. Collision check. Recompute the digests of (0^32 || a) and (0^32 || b) with
   two further target compressions, compare the full 256-bit digests for
   equality and the two 64-byte messages for inequality, and output the pair.

The experiment program of Section 8 implements this algorithm literally on a
truncated output and is the executable reference for every step above.

## 4. Data structures and memory ledger

Memory, in bytes, counts everything retained at any moment of the run.

| Item | Bytes | Note |
| --- | --- | --- |
| Table: 9216 slots x (distinguished value 32 + start 32 + length 8) | 663,552 | fixed size, direct addressing by low bits of the value |
| Working state: current point, start, counters, loop variables, two messages, two digests | 1,024 | upper bound; the live state is under 400 bytes |
| Code | 65,536 | upper bound; the experiment program of Section 8 is 5 KiB |
| Total | 730,112 | = 2^19.48 bytes, claimed as 2^19.5 |

No message is retained beyond the current pair. No table, advice or
precomputed data exists before the run, so `preprocessing_log2 = 0` and
`nonuniform_advice_log2_bytes = 0`; the setup of step 1 is charged in time
(Section 7).

Table occupancy: the expected number of stored distinguished points is
M * theta = 2^13.03 = 8364. Under H1 the count is a sum of independent
indicators of trail terminations; a Chernoff bound with mu = 8364 and relative
excess delta = 852 / 8364 = 0.102 gives P[count >= 9216] <= exp(-delta^2 mu / 3)
= exp(-29.0) < 3 * 10^-13. If the table ever fills, the run stops with failure;
this event is charged to the success budget in Section 6.

## 5. Stopping rule, collision check and success event

The run stops at the first of: a pair output in step 6 (success), the total
step counter reaching B (failure), or a full table (failure). It is a single
attempt with no restart; `success_probability` is the probability of the
success event in one run.

Success event: two 64-byte messages that differ (they differ in their last 32
bytes because a != b) and whose full 256-bit three-round digests are equal,
confirmed by the two recomputations of step 6. A repeated input is excluded by
the test in step 5. Because the digests are recomputed from the messages, no
property of the search is trusted for the final check.

## 6. Success probability

Probability space: the independent random start words of step 2. The function
F is fixed. Heuristic H1 (Section 8) states that F behaves, for collision and
trail-length statistics, like a uniformly random function on 256-bit words.

6.1 Birthday bound. Before the first collision, the M steps of trail building
evaluate F at M distinct inputs (a repeat would be a collision or a start on an
existing trail). Under H1, the probability that no collision occurs among M
evaluations at distinct inputs is prod_{i<M} (1 - i / 2^256) <= exp(-M (M-1) / 2^257).
With M = 2^128.03, M^2 / 2^257 = 2^-0.94 = 0.5213, so a collision occurs within
the M evaluations with probability at least 1 - exp(-0.5213) = 0.4062.

6.2 Losses. A collision that occurs is detected and output unless one of the
following happens. Each is bounded under H1.

* (a) Abandoned trail. Trail length is geometric with parameter theta, so a
  trail exceeds L_max = 16 / theta with probability (1 - theta)^(2^119) <= e^-16
  = 1.13 * 10^-7. The expected number of trails is at most 1.2 * 8364 (the
  factor 1.2 absorbs the variance of the count), so the expected number of
  abandoned trails, and hence the probability that the colliding point lies on
  one, is at most 1.2 * 8364 * 1.13 * 10^-7 = 1.13 * 10^-3.
* (b) Self-collision (rho on one trail). A trail of length L repeats one of its
  own points with probability at most L^2 / 2^257. With E[L^2] = 2 / theta^2 for
  a geometric length, the expected number of such events over at most
  1.2 * 8364 trails is at most 1.2 * 8364 * 2 * 2^230 / 2^257 = 1.5 * 10^-4.
  Such a repeat is also a collision of F but is not stored and is lost.
* (c) Start on an existing trail. A new start word equals one of the at most
  M points already on trails with probability at most M / 2^256 per start;
  over at most 1.2 * 8364 starts this is below 2^-242.
* (d) Full table: below 3 * 10^-13 by Section 4.
* (e) Step budget. The budget B exceeds M by 3 * 2^119, which covers the
  overrun of the last trail (at most L_max) and the walk-back of step 5 (at
  most 2 L_max steps), so the budget is never the cause of a missed collision
  found within the M fresh evaluations.

6.3 Bound. P[success] >= 0.4062 - 1.13 * 10^-3 - 1.5 * 10^-4 - 2^-242 - 3 * 10^-13
>= 0.4049. The claim states 0.40, above the 0.39 floor of the contract.

## 7. Time ledger

Unit: one three-round target compression on a 64-byte message = 1. Every other
primitive 256-bit word operation (load, store, add, logic, shift, compare,
branch, independent random word) costs 1 / C with C = 638, the
`reference_operation_cost` the contract computes for `blake3-r3`. All charges
below are upper bounds; parallelism is not used (one sequential processor).

| Component | Count | Word ops each | Compressions each | Cost in units |
| --- | --- | --- | --- | --- |
| Setup: load code, zero 27,648 table words, init counters | 1 | <= 2^20 | 0 | 2^20 / 638 = 1643.6 |
| Trail steps (steps 3 and 5): form the message word pair, compress, test the low 115 bits (AND, compare), increment length, test the cap, test the budget, loop | B = 2^128.0383 | <= 8 | 1 | B * (1 + 8 / 638) |
| Distinguished-point events (step 4): index (shift, AND), load slot, compare, store three words, draw new start, reset counters, bookkeeping | <= 9216 | <= 32 | 0 | 9216 * 32 / 638 = 462.3 |
| Collision check (step 6) | 1 | <= 32 | 2 | 2.05 |

Total <= 2^128.0383 * (1 + 8 / 638) + 1643.6 + 462.3 + 2.05 = 2^128.0383 *
1.012539 + 2108 = 2^128.05623. The claim states `time_log2 = 128.06`. The
constants are deliberately loose: the dominant term is B, and the 8 word
operations per step are an over-count of what steps 3 and 5 need (two for the
distinguished test, two for the two counters, two branches, and two spare).

The budget B is a hard stop, so the time bound holds for every run, including
failed runs; the time claim is not an expectation but a worst case.

## 8. Heuristic H1 and its evidence

H1 (score-critical). For the message family 0^32 || x, the map
F : x -> three-round digest of (0^32 || x) behaves, for collision statistics
and distinguished-point trail-length statistics, like a uniformly random
function on 256-bit words. H1 is used only in Section 6 (the birthday bound
6.1 and the loss bounds 6.2) and in the table occupancy bound of Section 4. It
is not used in the time ledger, which is a hard budget, nor in the memory
ledger, which is a fixed allocation.

Scope and extrapolation. H1 is the standard random-mapping assumption behind
every generic collision search. Three rounds of BLAKE3 do not reach full
diffusion, and dedicated differential attacks on round-reduced BLAKE3 exist in
the literature; such structure could make collisions cheaper than the birthday
bound but does not make the birthday-bound search fail: a structured function
with more collisions than a random one is found faster by this search, not
slower. The failure mode H1 guards against is the opposite one, a function with
fewer collisions or with trail statistics (cycle structure) far from a random
mapping, which would lower the success probability of Section 6.

Experiment `dp-search-r3-w16` (organizer-executed, `python-message-pairs-v1`).
The program `experiments/dp_search_r3_w16.py` runs the exact algorithm of
Section 3 on F truncated to its first 16 bits (the first two digest bytes),
with theta = 2^-4, trail cap 256 and a hard stop at 2^20 steps, seeded only by
the organizer's per-trial seed. Each trial returns the two 64-byte messages of
the family 0^32 || x whose three-round digests agree on the first two bytes, and
the event `digest-xor-mask` with mask `ffff` followed by 60 zero hex digits and
expected all-zero checks this on the host. Observations report the number of
F evaluations, trails and stored points per trial; they are untrusted internal
counts and are reported for comparison with the birthday prediction
sqrt(pi * 2^16 / 2) = 321 evaluations plus the distinguished-point tails.

What the experiment supports. A success rate of 256 of 256 trials with
evaluation counts whose mean is within a small factor of the birthday
prediction is consistent with H1 at width 16; a large shortfall of the success
rate under the hard stop, or a mean far from the prediction, would refute H1 at
that width. In the author's own run with 256 fresh seeds (not the organizer's),
all 256 trials returned a verified pair, the mean was 348 evaluations, the
median 340 and the maximum 918, and the program produced byte-identical output
on a second run.

Limitations. A width-16 check tests the truncated function, and the step from
16 to 256 bits is an extrapolation, not a proof; the three-round compression has
weak diffusion in its last round, so the truncation to two bytes exercises only
part of the state. No full-width evidence for H1 is possible to produce; this is
the remaining proof obligation for the judge, and it is the same obligation
carried by every birthday-bound entry on this lane.

## 9. Limits and remarks

* This entry is dominated on time by the existing round-3 entries on the lane,
  which price a bit-sliced evaluation of the compression function at a fraction
  of a unit. It is filed as a fully priced, independently checkable reference
  point with the plain unit convention: one compression call, one unit.
* No restart or success amplification is used; the claim is a single run.
* The author also searched for a differential route to beat the birthday bound
  at three rounds. Relaxation bounds on local-collision trail weights over the
  last two rounds stayed far below what a two-block attack at this width would
  need, and direct trail searches at weights up to 124 found no trail within
  their time caps. Nothing from that work is claimed here; it is mentioned so
  the reviewer knows the birthday-bound filing is a choice, not an oversight.
