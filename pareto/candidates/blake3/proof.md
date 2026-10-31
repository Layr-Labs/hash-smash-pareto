# Three-round BLAKE3: plain distinguished-point collision search, fully priced

## 1. What this entry is

This candidate is a generic birthday-bound collision search against the
`blake3-r3-prefix-v1` target, priced completely under the
`collision-frontier-v5` word-RAM cost contract. It claims time 2^128.06
target-compressions at success probability at least 0.40 with at most 2^20.25
bytes of memory, no preprocessing and no advice.

The field `baseline_improved` names `blake3-r3-nominal-v2` because the claim
schema requires a reference identifier. This entry does not improve the
nominal 128-bit display reference. The nominal entry is a security claim, not
an established attack, and this entry is not an attack on the round-reduced
function in the cryptanalytic sense. It is a fully specified, auditable cost
point: every operation the search performs is charged, every loss of success
probability is bounded, and the single modelling assumption is isolated as
heuristic H1 and tested by organizer-executed experiments.

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

* theta = 2^-115: a point y is distinguished when its low 115 bits (bits 0 to
  114 of the 256-bit integer of Section 2, bit 0 the least significant) are
  zero.
* Trail cap L_max = 2^119 = 16 / theta steps.
* Fresh-evaluation budget M = 2^128.03 steps for trail building.
* Total step budget B = M + 3 * 2^119 (trail building, the overrun of the
  last trail, and the walk-back of Section 3, step 5).
* Table of S = 2^14 = 16,384 slots with open addressing and linear probing.
  The home slot of a distinguished value y is idx(y) = (y >> 115) AND (2^14 - 1),
  that is bits 115 to 128 of y, the 14 bits just above its 115 zero bits.

Steps:

1. Setup. Load the code, zero the table and the counters.
2. Start a trail. Draw one independent uniformly random 256-bit word s and set
   x = s, length = 0.
3. Extend. If the fresh count (evaluations made in this step since the start
   of the run, over all trails) has reached M,
   stop and report failure. Otherwise replace x by F(x), increment length and
   the fresh count. If x is distinguished, go to step 4. If length reached
   L_max, abandon this trail and go to step 2.
4. Distinguished point. Probe slots idx(x), idx(x) + 1, idx(x) + 2, ... modulo
   S in turn. At each slot: if it is empty, store (x, s, length) there and go
   to step 2; if its stored value equals x, read its (x, s0, length0) and go to
   step 5; otherwise move to the next slot. If all S slots are occupied and
   none matches (full table), stop and report failure.
5. Walk back. Re-walk both trails from s0 and s in lockstep after discarding
   the leading steps of the longer trail, until the next points agree. If the
   two current points are equal before the next points agree, the shorter trail
   started on the other trail (same input, not a collision); discard the new
   trail and go to step 2. Otherwise the two current points a != b satisfy
   F(a) = F(b). Every evaluation of this step counts toward the total step
   budget B; if the total reaches B, stop and report failure.
6. Collision check. Recompute the digests of (0^32 || a) and (0^32 || b) with
   two further target compressions, compare the full 256-bit digests for
   equality and the two 64-byte messages for inequality, and output the pair.

The experiment program of Section 8 (`experiments/dp_budget_r3.py`)
implements steps 1 to 6 on a truncated output with the same rule for M and
the same two budgets, with one stated difference: it keeps the stored
distinguished points in a growable map instead of the fixed table of S slots,
so it never reports the full-table failure. At full width that failure has
probability below 10^-1000 (Section 6.2, loss (d)), so the two procedures have
the same success probability to that precision. The program is the executable
reference for every other step.

## 4. Data structures and memory ledger

Memory, in bytes, counts everything retained at any moment of the run.

| Item | Bytes | Note |
| --- | --- | --- |
| Table: 16,384 slots x (distinguished value 32 + start 32 + length 8) | 1,179,648 | fixed size; home slot idx(y) = bits 115 to 128 of y, linear probing |
| Working state: current point, start, counters, loop variables, two messages, two digests | 1,024 | upper bound; the live state is under 400 bytes |
| Code | 65,536 | upper bound; the experiment program of Section 8 is under 10 KiB |
| Total | 1,246,208 | = 2^20.249 bytes, claimed as 2^20.25 |

No message is retained beyond the current pair. No table, advice or
precomputed data exists before the run, so `preprocessing_log2 = 0` and
`nonuniform_advice_log2_bytes = 0`; the setup of step 1 is charged in time
(Section 7).

Table occupancy: the expected number of stored distinguished points is
M * theta = 2^13.03 = 8364, a load of 0.51 on 16,384 slots. For a uniformly
random function evaluated at distinct inputs each of the at most M fresh
outputs is distinguished independently with probability theta, so the stored
count is dominated by a Binomial(M, theta) variable; a Chernoff bound with
mu = 8364 and relative excess delta = (16384 - 8364) / 8364 = 0.959 gives
P[count >= 16384] <= exp(-delta^2 mu / 3) = exp(-2563) < 10^-1000. H1 carries
this bound to F as loss (d) of Section 6.2. If the table ever fills, the run
stops with failure, charged in Section 6.

## 5. Stopping rule, collision check and success event

The run stops at the first of: a pair output in step 6 (success), the fresh
evaluation count reaching M in step 3 (failure), the total step counter
reaching B (failure), or a full table (failure). It is a single
attempt with no restart; `success_probability` is the probability of the
success event in one run.

Success event: two 64-byte messages that differ (they differ in their last 32
bytes because a != b) and whose full 256-bit three-round digests are equal,
confirmed by the two recomputations of step 6. A repeated input is excluded by
the test in step 5. Because the digests are recomputed from the messages, no
property of the search is trusted for the final check.

## 6. Success probability

Probability space. The only random choices in a run are the independent,
uniformly random 256-bit start words drawn in step 2. The function F, the
target and all parameters are fixed. The success probability of one run is
therefore a definite number p(F) = Pr over the start words [a pair is output].
(In the experiments of Section 8 the start words are instead derived from the
organizer's seed; heuristic H2 there covers that substitution.)
Nobody can compute p(F) exactly; what is computed below is the success
probability p_rand of the same algorithm, with the same budgets, run on a
uniformly random function from 256-bit words to 256-bit words. Heuristic H1
(Section 8) is the statement that p(F) is at least p_rand, and nothing in this
section uses any other property of F than H1. The time and memory ledgers
(Sections 4 and 7) do not depend on H1 or on any random choice.

6.1 Birthday bound. Before the first collision, the M fresh evaluations of
step 3 are made at M distinct inputs (a repeat would be a collision or a start
on an existing trail). For a uniformly random function the probability that no
collision occurs among M evaluations at distinct inputs is
prod_{i<M} (1 - i / 2^256) <= exp(-M (M-1) / 2^257). With M = 2^128.03,
M^2 / 2^257 = 2^-0.94 = 0.5213, so a collision occurs within the M evaluations
with probability at least 1 - exp(-0.5213) = 0.4062.

6.2 Losses. A collision that occurs is detected and output unless one of the
following happens. Each is bounded for a uniformly random function.

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
  over at most 1.2 * 8364 = 10,037 starts this is at most 10,037 * 2^128.03 /
  2^256 = 2^-114.7, about 3 * 10^-35.
* (d) Full table: below 10^-1000 by Section 4.
* (e) Detection lag. A collision between the current trail and a stored
  trail is detected only when the current trail reaches its distinguished
  point, on average 1 / theta steps later. If the fresh budget runs out first,
  the collision is lost. Each fresh evaluation collides with one of the at most
  M earlier points with probability at most M / 2^256, so the probability
  that the first collision falls within the expected lag of the end of the
  budget is at most (M / 2^256) * (1 / theta) = 2^-127.97 * 2^115 = 2^-12.97 =
  1.3 * 10^-4. At the small widths of Section 8 this term and term (b) are
  the dominant losses, which is why the measured frequencies there sit
  below 0.4062.
* (f) Step budget. The allowance 3 * 2^119 beyond M covers the overrun of the
  last trail (at most L_max) and the walk-back of step 5 (at most 2 L_max
  steps), so the budget never cuts off a collision found within the M fresh
  evaluations.

6.3 Bound. p_rand >= 0.4062 - 1.13 * 10^-3 - 1.5 * 10^-4 - 3 * 10^-35 - 10^-1000 -
1.3 * 10^-4 >= 0.4047. Under H1, p(F) >= p_rand >= 0.4047. The claim states 0.40,
above the 0.39 floor of the contract.

6.4 Sensitivity. If F had collision density kappa times that of a random
function, the birthday term would be 1 - exp(-0.5213 kappa) and the bound of
6.3 that term minus 0.0014: kappa = 0.96 gives 0.392, kappa = 0.95 gives 0.389
and kappa = 0.9 gives 0.373. The 0.39 floor is crossed at kappa = 0.953, so
the claim needs H1 to hold to within about 4 percent on collision density at
full width. Section 8 states what the experiments can and cannot say about
this.

## 7. Time ledger

Unit: one three-round target compression on a 64-byte message = 1. Every other
primitive 256-bit word operation (load, store, add, logic, shift, compare,
branch, independent random word) costs 1 / C with C = 638, the
`reference_operation_cost` the contract computes for `blake3-r3`. All charges
below are upper bounds; parallelism is not used (one sequential processor).

| Component | Count | Word ops each | Compressions each | Cost in units |
| --- | --- | --- | --- | --- |
| Setup: load code, zero 147,456 table words, init counters | 1 | <= 2^20 | 0 | 2^20 / 638 = 1643.6 |
| Trail steps (steps 3 and 5): form the message word pair, compress, test the low 115 bits (AND, compare), increment length, test the cap, test the budget, loop | B = 2^128.0383 | <= 8 | 1 | B * (1 + 8 / 638) |
| Distinguished-point events (step 4): index (shift, AND), per probed slot load and compare (<= 4 word ops, at most S = 16,384 probes), store three words, draw new start, reset counters, bookkeeping | <= 16,385 (at most S stores plus the matching event) | <= 32 + 4 * 16,384 | 0 | <= 16,385 * 65,568 / 638 = 1.68 * 10^6 = 2^20.7 worst case; under 1,200 expected at load 0.51 |
| Collision check (step 6) | 1 | <= 32 | 2 | 2.05 |

Total <= 2^128.0383 * (1 + 8 / 638) + 1643.6 + 1.68 * 10^6 + 2.05 = 2^128.0383 *
1.012539 + 2^20.7 = 2^128.05623 (the additive terms are 2^-107 of the first). The claim states `time_log2 = 128.06`. The
constants are deliberately loose: the dominant term is B, and the 8 word
operations per step are an over-count of what steps 3 and 5 need (two for the
distinguished test, two for the two counters, two branches, and two spare).

The budget B is a hard stop, so the time bound holds for every run, including
failed runs; the time claim is not an expectation but a worst case.

## 8. Heuristic H1 and its evidence

H1 (score-critical, exact statement). Let A(M, theta, L_max) be the algorithm
of Section 3 with fresh-evaluation budget M, distinguished-point density theta
and trail cap L_max, run on a function G from n-bit words to n-bit words, and
let p_G be its success probability over the uniformly random start words. H1
states: for F : x -> three-round digest of (0^32 || x) at n = 256 with the
parameters of Section 3, p_F >= p_rand, where p_rand is the same probability
for a uniformly random function. Section 6 computes p_rand >= 0.4047 from two
properties of a random function only: among M evaluations at distinct inputs a
collision occurs with probability at least 1 - exp(-M (M - 1) / 2^(n+1)), and
trail lengths are geometric with parameter theta. H1 says F has at least the
first property and the second to within the loss ledger of 6.2. No other
heuristic enters the claimed time, memory or success probability; H2 to H4
below concern only how the organizer-executed experiments relate to H1. The time ledger (Section 7) and the
memory ledger (Section 4) are hard budgets and do not depend on H1.

What would refute H1. A function with fewer collisions than a random one on
the family 0^32 || x (collision density kappa < 1 in the sense of 6.4), or with
cycle structure that makes trails abandon or merge far more often than the
geometric model, lowers p_F below p_rand. By 6.4 the claim survives kappa down
to about 0.953; below that the 0.39 floor is crossed. Structure that makes
collisions more frequent than random makes this search succeed sooner, not
later, so it cannot refute H1 as stated.

Supporting heuristics used only by the experiments. The experiments cannot
run at the claimed parameters, so three substitutions stand between them and
H1. Each is declared in claim.json with role supporting; none enters any
claimed number.

* H2 (seeded starts). The organizer executor supplies one 32-byte seed per
  trial; the program derives start words as the target hash of seed || counter
  (32-byte big-endian counter), truncated to w bits. H2: for the success
  frequency measured over 256 trials these starts behave as independent
  uniform coins. Evidence: the author's reference values q_w below were
  measured with the same derivation from hashed labels, so any bias is shared
  by the reference; the open run dp-open-r3-w16 reached a collision in 256 of
  256 trials with mean 346.9 steps against about 345 predicted for uniform
  starts.
* H3 (restricted, truncated function). F_w, the function F restricted to
  x < 2^w and truncated to w digest bits, stands in for F at n = 256 for the
  purpose of refuting H1. Only message word 8 and the low bits of word 9 vary,
  and only the first digest word is read. Evidence: none beyond the three
  widths themselves; this is the gap named in the limitations.
* H4 (unscaled parameters). theta_w = 2^-2 with 16 to 130 trails per run
  stands in for theta = 2^-115 with 8364 trails. The collision-density
  property that H1 guards does not depend on theta; the trail-structure
  property does, and the experiments test it only at theta = 2^-2. Evidence:
  the deficits 0.4062 - q_w follow the theta-dependent loss bounds given
  below the table.

Tested regime. The program `experiments/dp_budget_r3.py` runs A(M_w, 2^-2, 64)
on F_w, the function F restricted to inputs x < 2^w and truncated to its first
w digest bits (the top w bits of the first four digest bytes read big-endian;
Section 2 reads the full digest little-endian, and which bits are kept is
immaterial for a random function), with M_w = ceil(sqrt(1.0426 * 2^w)). This
gives M_w^2 / 2^(w+1) = 0.5317, 0.5237, 0.5217 at w = 12, 16, 18 against 0.5213
at full width, the difference being the rounding of M_w up to an integer. The
total step budget is B_w = M_w + 3 * 64. A trial outputs a pair only if the algorithm finds one
within the budget; otherwise it returns no pair. The host checks each returned
pair against the mask of the first w bits, so the organizer-verified success
count out of 256 is a direct measurement of p_(F_w) at claim-shaped budgets.
The reference value q_w is the success frequency of the same program on a
uniformly random function of the same width, measured by the author with a
fresh SHA-256-keyed random function per trial over 10,000 trials (the
"ensemble" column). Because a single random function of 2^w points is itself
one random instance, the author also ran 20 fixed random instances of 2,000
trials each and reports their mean, standard deviation and range (the
"instances" columns). The author's own run of the shipped program on F_w with
256 seeds is the last column; the organizer's seeds differ, so its count will
differ by sampling noise.

| experiment | w | M_w | B_w | q_w ensemble (99% CI) | instances mean +- sd [min, max] | F_w author 10k (99% CI) | predicted of 256 | refutes H1 at w if below | author 256 |
|---|---|---|---|---|---|---|---|---|---|
| dp-budget-r3-w12 | 12 | 66 | 258 | 0.3357 [0.3236, 0.3480] | 0.3360 +- 0.0377 [0.2825, 0.4125] | 0.3230 [0.3111, 0.3352] | 85.9 | 67 | 83 |
| dp-budget-r3-w16 | 16 | 262 | 454 | 0.3863 [0.3738, 0.3989] | 0.3919 +- 0.0134 [0.3675, 0.4200] | 0.3920 [0.3795, 0.4046] | 98.9 | 79 | 104 |
| dp-budget-r3-w18 | 18 | 523 | 715 | 0.3924 [0.3799, 0.4050] | 0.3993 +- 0.0150 [0.3715, 0.4300] | 0.4085 [0.3959, 0.4212] | 100.5 | 81 | 113 |

"Refutes H1 at w if below" is the 0.5 percent quantile of Binomial(256, q_w):
an organizer count below it has probability under 0.5 percent if F_w behaved
as a random function, and would show that F_w has fewer detectable collisions
than random at that width. A count at or above it is consistent with H1 at
that width; it does not establish H1, at that width or at full width.

Why q_w is below 0.4062 at small widths. Two loss terms of 6.2 that are
negligible at full width are not negligible here: (b), a trail repeating one
of its own points before reaching a distinguished point, and (e), the
collision falling within the detection lag of the end of the fresh budget.
At the tested parameters each is bounded above by about 4 M_w / 2^w =
M_w / (theta_w 2^w): 0.064 at w = 12, 0.016 at w = 16, 0.008 at w = 18. The
measured deficits 0.4062 - q_w are 0.071, 0.020 and 0.014, below the sum of
the two bounds at every width. The bounds fall by a factor 2 per 2 bits of
width because M_w grows as 2^(w/2) while theta_w = 2^-2 is held fixed; theta
and the trail count are not scaled across the experiments (heuristic H4). At
w = 256 with theta = 2^-115 the same two terms are 1.5 * 10^-4 and 1.3 * 10^-4
(Section 6.2), bounded there by the geometric trail-length model rather than
by M / 2^w.

Reading of the author's measurements. At w = 16 the 10,000-trial frequency
of F_16 (0.3920) is inside the 99 percent interval of the ensemble value and
0.01 instance standard deviations from the instance mean. At w = 18 the
frequency of F_18 (0.4085) is above the ensemble interval [0.3799, 0.4050] and
0.61 instance standard deviations above the instance mean, inside the
instance range; F_18 abandoned 6 trails in 10,000 trials against 66 for
the ensemble, so on this instance long trails are rarer than typical, which
helps the search. At w = 12 the frequency of F_12 (0.3230) is
0.35 instance standard deviations below the instance mean (0.3360),
inside the range [0.2825, 0.4125] of the 20 random instances; its
abandoned-trail count (122 against 53 for the ensemble) is high for a random
instance and means that more walks on this particular 4,096-point function
enter a cycle that contains no distinguished point. A 4,096-point function has visible cycle
structure in any case (expected rho length about 80), so width 12 is reported
as the least representative of the three widths, not dropped. None of the
three measurements is below the instance range of a random function, and none
is evidence for H1 at width 256.

Experiment `dp-open-r3-w16`. The same program with no budget below the hard
stop of 2^20 steps, at w = 16, returns a pair in every trial unless the
function has a defect that stops the search (a pair is always found on a
finite function). In the author's run all 256 trials returned a host-checkable
pair with mean 346.9 total steps (prediction for a random function:
sqrt(pi * 2^16 / 2) = 321 fresh evaluations plus distinguished-point tails of
mean 2 / theta = 8 per trail, about 345), median 331 and maximum 1,029. The
observation fields (steps, fresh, trails, stored points, abandoned, merges)
are participant counters and are not verified by the host; they are reported
for comparison only.

What the experiments do not show. They test F_w for w <= 18 bits, 238 bits
short of the claim, through the substitutions H2 to H4. The truncation to a prefix of the digest exercises part of
the state of a three-round compression with weak diffusion in its last round.
A sample of 256 trials has a standard deviation of about 0.03 in frequency and
cannot distinguish kappa = 0.95 from kappa = 1 even at the tested width. The
intervals above do not establish p_F >= 0.4047 at any width; the sample does
not discharge the obligation to believe H1 at n = 256. That obligation is the
one every birthday-bound entry on this lane carries. What the experiments can
do is refute H1 at the tested widths, with the thresholds stated, and they
report, in advance, the exact number the organizer's count is compared with.

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
  their time caps. Nothing from that work is claimed here. The birthday-bound filing is a
  deliberate choice made after that search failed.
