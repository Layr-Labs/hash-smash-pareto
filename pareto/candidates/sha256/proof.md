# SHA-256 r64: a constant-folded bit-sliced distinguished-point birthday walk

Target sha256-r64-prefix-v1 on the Pareto lane sha256, round count 64 of 64.
This package is a construction and a total-work ledger. It does not exhibit a
colliding pair: the expected work is 2^124.4622 target compressions, so no
execution of the attack is possible. The certificate manifest is retained and is
empty because the target relation is an existential statement about two messages
and this attack delivers a pair only on success.

All integers below are exact. Logs are base 2.

## 1. Target and relation

The executed function is FIPS 180-4 SHA-256 restricted to its first 64 rounds --
that is, all rounds. Concretely, for a byte string M with bit length below 2^64:

* Pad M with the byte 0x80, then zero bytes until the length is 56 mod 64, then
  the 64-bit BIG-ENDIAN bit length (FIPS 180-4, Section 5.1.1). The padded string
  is a whole number of 512-bit blocks.
* Start from the standard fixed IV H0 = (6a09e667, bb67ae85, 3c6ef372, a54ff53a,
  510e527f, 9b05688c, 1f83d9ab, 5be0cd19).
* For each padded block, in order, run the standard message schedule (standard
  sigma0/sigma1 expansion at the original indices, the 64 standard round
  constants), execute step indices 0 through 63 inclusive, then add the eight
  working words to the incoming chaining value modulo 2^32 (feed-forward).
* Serialise the final chaining value big-endian, words in standard order: all 256
  digest bits.

This is exactly the profile relation: message domain all finite byte strings with
bit length below 2^64, standard fixed IV, standard schedule, FIPS padding,
feed-forward, full 256-bit digest, rounds 0..63 on every padded block. No chosen
IV, no free-start state, no compression-only relation, no truncation.

The claim is the existence of two DISTINCT byte strings M != M' in that domain
with equal 256-bit digests.

## 2. Message family and the reduction

Take eight fixed 32-bit words

    c0..c7 = 5a827999, 6ed9eba1, 8f1bbcdc, ca62c1d6, 9b05688c, 1f83d9ab, 5be0cd19, 3c6ef372

(any eight fixed words work; this choice just reuses well-known constants). For a
256-bit value x with big-endian words x0..x7, define the 64-byte string M(x) to be
the concatenation of the sixteen big-endian 32-bit words

    W0..W7 = c0..c7,   W8..W15 = x0..x7.

The map x -> M(x) is a bijection from {0,1}^256 onto the set of 64-byte strings
whose first eight words are c0..c7, so x != y implies M(x) != M(y).

Every M(x) is 64 bytes, so pad(M(x)) is exactly two 512-bit blocks: block 1 is
M(x) itself, and block 2 is the SAME 64 bytes for every x -- the byte 0x80, 55
zero bytes, and the big-endian 64-bit length 512. Each M(x) has bit length 512,
which is below 2^64, so every M(x) lies in the profile message domain.

Let sigma(x) be the block-1 working state after step 63 -- the eight words
a,b,c,d,e,f,g,h before feed-forward -- serialised big-endian as a 256-bit value.
The chaining value handed to block 2 is cv1(x) = H0 + sigma(x) mod 2^32, word by
word. Therefore if sigma(x) = sigma(y) then cv1(x) = cv1(y); block 2 is then
compressed from the same input block with the same chaining value, and the two
complete digests are equal.

So the search problem find x != y with sigma(x) = sigma(y) implies the target
relation. The converse is not claimed and is not needed.

What this saves, and what it does not: the SEARCH never evaluates block 2, because
the reduction only needs equality of block-1 working states. The delivered pair,
on success, is a pair of complete two-block messages whose COMPLETE digests agree.
Nothing about block 2 is approximated and the target is not weakened.

## 3. The walk

sigma is a function {0,1}^256 -> {0,1}^256, and the attack searches for a collision
of sigma itself by a distinguished-point walk. Put g = sigma, and call
z in {0,1}^256 DISTINGUISHED when z = 0 mod 2^116, i.e. when the low 116 bits of
the state are zero (all 32 bits of h, all 32 bits of g, all 32 bits of f, and the
low 20 bits of e, in the standard state order). For a random-looking z this has
probability theta = 2^-116.

A TRAIL is the sequence s, g(s), g(g(s)), ... started from a uniform
s in {0,1}^256 and stopped at the first distinguished point. Its length is
geometric with mean 1/theta = 2^116. Each finished trail contributes its
distinguished endpoint to a table; when an endpoint equals a stored endpoint the
two trails have merged and a collision of g is recovered from them.

Lemma 1 (detection). If two distinct evaluated points p != q satisfy
g(p) = g(q), then the trails containing p and q have the same distinguished
endpoint, so the merge is detected by the table.

Proof. The successor sequences of p and q coincide from the first step:
g^i(p) = g^i(q) for every i >= 1. A trail stops only at its own first
distinguished point, and p and q are evaluated, so each lies at an index at most
the length of its trail. Hence both trails run through the same suffix sequence
and stop at the same distinguished value. QED

Recovery from two trails with known starts s1, s2 and the same endpoint v is
deterministic and cheap. Re-walk trail 1 counting steps to its distinguished
point to obtain its length L1, likewise L2; assume L1 >= L2; advance s1 by L1-L2
steps to u; then step u and s2 in lockstep. At each step compare the two values
before applying g; the first time the successors agree, the two current points are
distinct (otherwise the trails coincided from the start and L1 = L2) and have equal
images, hence equal block-1 working states and colliding messages. The number of
steps is at most (L1-L2) + L2 for the arrival, plus at most L2 lockstep pairs, and
each lockstep pair costs two evaluations: at most 3 L1 + 2 L2 <= 6 L_max
evaluations.

## 4. The bit-sliced body and its exact gate ledger

The compression is evaluated for 256 points at once by bit-slicing: one 256-bit
word holds bit j of a given 32-bit word for all 256 points, for one fixed j. The
data layout is 8 state words x 32 bit-planes = 256 registers of 256 bits, plus the
32 bit-planes of the current message addend u_t = W_t + K_t.

Rotations are free: a rotation of a 32-bit word is a permutation of the 32
bit-plane registers, i.e. a renaming, costing zero word operations. A shift by a
constant with zero fill is free up to constant planes. XOR, AND and OR are one
word operation each. A full adder over bit-planes computes sum and carry in one
pass: for inputs a,b,c set t = a XOR b, s = t XOR c, and carry = (a AND b) OR
(c AND t). That is 5 word operations and yields the redundant pair (s, carry) with
the carry position implicitly moved one plane down, which is free. A
carry-propagate add of two numbers uses the same recurrence without the second
operand pair: 5 word operations per bit-plane slice (two XOR for the sum bit, two
AND and one OR for the carry bit). No operation is charged for the carry
position.

One round, over its 32 bit-planes:

| item | gates per bit-plane | word operations |
|---|---:|---:|
| Sigma1(e) = rotr6 e XOR rotr11 e XOR rotr25 e | 2 | 64 |
| Ch(e,f,g) = g XOR (e AND (f XOR g)) | 3 | 96 |
| Sigma0(a) = rotr2 a XOR rotr13 a XOR rotr22 a | 2 | 64 |
| Maj(a,b,c) = c XOR ((a XOR c) AND (b XOR c)) | 4 | 128 |
| u_t = W_t + K_t, constant add (2 gates, charged as 3) | 3 | 96 |
| T1 = h + Sigma1 + Ch + u_t: 4 numbers, 2 full adders + 1 carry-propagate add | 15 | 480 |
| T2 = Sigma0 + Maj: carry-propagate add | 5 | 160 |
| e' = d + T1: carry-propagate add | 5 | 160 |
| a' = T1 + T2: carry-propagate add | 5 | 160 |
| ROUND TOTAL | 44 | 1,408 |

One message-schedule step W_t = sigma1(W_t-2) + W_t-7 + sigma0(W_t-15) + W_t-16
costs two XOR for sigma0, two XOR for sigma1, and a four-number add (2 full
adders + 1 carry-propagate add) of 15: ROUND TOTAL 19 gates per bit-plane, 608 word
operations per 256-point batch.

CONSTANT FOLDING OF ROUNDS 0 TO 7. In the family of Section 2 the words W0..W7 are
constants, and so are the IV, the round constants, and therefore u_0..u_7.
Consequently the working state after step 7 is one fixed 256-bit constant, the
same for every x. The body starts from that folded constant state and rounds 0 to
7 contribute zero gates. Their cost is paid once, in preprocessing (Section 7).

Hence the body for r = 64 executes rounds 8..63 (56 rounds) and schedule steps
16..63 (48 steps):

    56 * 44 + 48 * 19 = 2464 + 912 = 3376 gates per bit-plane,
    3376 * 32 = 108,032 word operations per batch of 256 points.

Per batch the attack also pays the distinguished-point test on the low 116 bits of
the state (115 OR operations on bit-planes, plus one comparison and branch = 116)
and 16 loop-control operations: 108,164 word operations per batch, that is
108,164/256 = 422.5 word operations per evaluated point.

The body is a straight-line data-independent program of 3,376 bit-plane gate
records, so the per-batch count is exact and not an expectation.

## 5. The search plan

The attack is ONE attempt. Parameters:

* 256 lanes, one point per lane, advanced in lockstep by one body execution.
* Batches B = 2^120, so the number of point evaluations is Q = 256*B = 2^128.
* Distinguished probability theta = 2^-116; expected finished trails and stored
  endpoints Q*theta = 2^12 = 4096.
* Table capacity 2^13 = 8192 entries of 256 bits. The distinguished value is
  stored in full, so a table match is a true equality and never a filter false
  positive. Trail starts are stored too, 2^13 entries of 256 bits.
* Every finished trail is scanned against the stored entries (bounded by
  8192*8 word operations), inserted when new, and its lane restarted from a fresh
  value produced by the attempt seed expansion. On the first exact match the
  attempt recovers the colliding pair (Lemma 1 and Section 3) and stops.

There is one attempt and no restart, so no success amplification is charged beyond
the single attempt count.

## 6. Success probability

Work in the random-function model H1 of Section 9: on the evaluated point set, g
behaves as a uniformly random function, with independent uniform images on
distinct domain points. Let Q = 2^128 be the number of evaluated points and let E
be the event that two distinct evaluated points have equal images.

Proposition 1. Pr[E] >= 0.3932291666... > 0.39.

Proof. For distinct domain points the images are independent and uniform on
{0,1}^256, so

    Pr[not E] = product over i = 1..Q-1 of (1 - i/2^256)
              <= exp( - Q(Q-1) / (2 * 2^256) ).

With Q = 2^128, Q(Q-1)/(2*2^256) = (2^256 - 2^128)/2^257 = 1/2 - 2^-129 =: x.
For x in [0,1] the alternating series for exp(-x) truncated after the x^4/4! term
is an upper bound, because the terms decrease in absolute value and the first
omitted term is negative. Hence

    exp(-x) <= exp(-1/2) * exp(2^-129)
            <= (1 - 1/2 + 1/8 - 1/48 + 1/384) * (1 + 2^-129 + 2^-258)
            < 0.606771,

using exp(t) <= 1 + t + t^2 for 0 <= t <= 1. The bracket is exactly
233/384 = 0.6067708333... . Therefore Pr[not E] < 0.606771 and
Pr[E] >= 0.393229166... > 0.39. QED

Proposition 2 (detection and capacity). Conditioned on E, the attempt returns a
colliding pair except with probability at most 2^-100.

Proof sketch. By Lemma 1 every collision among evaluated points produces equal
distinguished endpoints and therefore a table match. The number of stored trails
is binomial with mean 4096 and the capacity is 8192, so a Chernoff bound gives
Pr[capacity exceeded] <= exp(-4096/3) < 2^-1900; a capacity overflow halts the
attempt without an answer only if no match has occurred. Full 256-bit comparison
makes a match exact. Recovery succeeds by Section 3 whenever the two starts are
distinct. QED

Combining, the algorithmic success probability of the single attempt is at least
0.393229 > 0.39, the value declared in claim.json. This bound is a comparison with
a random function, not a bound for SHA-256; that comparison is heuristic H1 and is
score-critical.

## 7. Total work ledger

All quantities are word operations on the cost model 256-bit RAM, summed over all
processors (the attack is defined as a sequential bit-sliced evaluation;
parallelism would change wall clock only and is not claimed). The deliverable is
divided by the organizer reference operation cost for this round count,
C = 4912 for sha256-r64.

| term | exact count | log2 |
|---|---:|---:|
| body and per-batch work, 2^120 * 108,164 | 143774616936079640476767386868163190718464 | 136.7228609 |
| table scans and insertions, <= 8192*8192*8 | 536870912 | 29.0 |
| recovery, 4*2^116 evaluations at 423 word operations | 140565860554254853559577596624646438912 | 126.7245139 |
| setup (table clear, lane and trail-start initialisation) | 1048576 | 20.0 |
| preprocessing (folded rounds 0..7 and the one-time body image) | 16777216 | 24.0 |
| TOTAL N | 143915182796633895330326964464788391854080 | 136.7242707 |

No ledger term is charged twice and the body dominates, so the exact total is the
integer N above with log2 N = 136.724270692... . Then

    T = N / C = N / 4912,
    log2 T = 136.724270692 - 12.2620239... = 124.4621758...

The claim rounds UP to time_log2 = 124.4622, conservative by 2.4e-5 bits.

Completeness of the ledger:

* Failed trials: charged in full. All 2^128 evaluations are the attempt, and the
  single attempt is charged whether or not it succeeds. A trail that merges is
  reported by the table scan term; a lane that has not reached a distinguished
  point when the batch budget ends is inside the body count.
* Randomness: the fresh lane starts are about Q*theta = 4096 words plus the
  attempt seed. The model charges a fresh uniform 256-bit word as one primitive
  operation, the same unit as a body gate, and the 2^20 setup term covers it by
  many orders of magnitude.
* Sorting and lookup: the table is scanned linearly, and every scan is charged at
  the full capacity rather than at the realised occupancy.
* Recovery: charged at six mean trail lengths, a large margin over the
  3*L1 + 2*L2 of Section 3.
* Success amplification: not used. The single-attempt probability already exceeds
  0.39.
* Memory operations: the body reads and writes registers only; each gate is one
  register-to-register word operation and is counted once. Table words are charged
  in the table term. Model loads and stores are not otherwise used.
* Code fetch, control flow and interpreter: the body is a straight-line register
  program, so control flow is the 16 charged operations per batch. A per-gate
  native instruction-fetch charge is NOT included; that exclusion is heuristic H2
  and is score-critical.

## 8. Memory

Peak simultaneous storage, in bytes:

| item | bytes |
|---|---:|
| body code image, 3376 bit-plane records at 8 bytes per record | 27008 |
| round constants and folded-state constants | 512 |
| data registers, 9 words x 32 bit-planes x 32 bytes | 9216 |
| distinguished table, 2^13 entries x 32 bytes | 262144 |
| trail starts, 2^13 entries x 32 bytes | 262144 |
| trail lengths and lane bookkeeping, 2^13 * 8 | 65536 |
| scanning and recovery scratch | 1024 |
| seed expansion state | 256 |
| PEAK | 627840 |

627,840 < 2^20 = 1,048,576, so the declared memory_log2_bytes = 20.0 is an upper
bound and the memory term max(0, 20 - 20) = 0 contributes nothing to the
normalised score. With one record per 256-bit word instead of a packed image the
total is 3376*32 + 590,832 = 698,864 bytes, still below 2^20.

## 9. Heuristics, scope, extrapolation, limitations

H1 (random-function model) -- score-critical. On the evaluated point set the walk
function g behaves as a uniformly random function: distinct evaluated domain points
have independent uniform images in {0,1}^256, so the pairwise collision hazard is
exactly 2^-256 and the birthday computation of Section 6 applies. Scope: the fixed
sha256-r64-prefix-v1 target restricted to the 64-byte family of Section 2, one
attempt of 2^128 evaluations over 256 lanes. Extrapolation: this is the classical
van Oorschot-Wiener parallel-collision-search premise transported to a
reduced-round iterated hash. The walk is iterated rather than freshly sampled, so
the premise also asserts that iterates from trail starts behave as draws from a
random mapping and that the distinguished-point filter is independent of collision
events. Evidence: the reduction of Section 2 is exact and does not depend on H1;
H1 is used only for the 0.39 success statement and for the expected trail count.
Limitations: no experiment here measures the full-width collision hazard, and none
can, because it is a 2^128-scale event. Nothing here shows that the 64-round
compression behaves randomly. A structural property of the full 64 rounds would
invalidate this model, and could only make the attack cheaper than claimed.

H2 (straight-line accounting) -- score-critical. The ledger charges one word
operation per body gate, one per constant-add gate, one per distinguished-point bit
OR, and 16 per batch for loop control, and charges no instruction fetch, decode or
interpreter step for the body. The claim is that a realisable implementation of
Section 4 performs no other work: the body is a straight-line register program over
256-bit words and every charged item is executed. Scope: the exact plan of Section
5, including initialisation, every recurring path, the table, recovery and
preprocessing. Extrapolation: the body count is exact because the body is
straight-line and data independent, and the batch count is an exact declared
parameter; only recovery and preprocessing are bounded rather than counted exactly,
and both carry large margins. Limitations: if an implementation needs a per-gate
fetch and decode step, the body term grows by a constant factor, and a factor of two
would give log2 T about 125.46; if the code image does not fit the layout of
Section 8, memory could exceed 2^20. An undercounted recurring operation invalidates
the time bound. H2 does not repair H1 and is not repaired by it.

H3 (distinguished-point halting) -- supporting. Every trail terminates at its first
distinguished point, and no trail is truncated by the batch budget: 2^120 batches
advance each lane up to 2^120 steps while the mean trail length is 2^116, and a
geometric tail exceeds 2^119 with probability below exp(-8). A truncation would
lose one trail and would not invalidate the ledger, because its evaluations are
already charged.

H4 (exact table equality) -- supporting. Storing the full 256-bit distinguished
value makes table matches exact, so recovery runs only on genuine merges and the
table scan bound covers all lookups.

WHAT IS AND IS NOT ESTABLISHED. Established, given H1: two distinct 64-byte
messages with equal complete 64-round SHA-256 digests are found with probability at
least 0.393229 by an algorithm whose total work is 2^124.4622 target compressions
with peak memory below one mebibyte. The reduction of Section 2 is unconditional:
any full-width collision of sigma yields a genuine collision of complete digests.
Not established: any actual colliding pair. Since 2^124.5 compressions is not
executable, no pair is produced, verified or claimed. This is a complexity claim
under a stated cost model, an exhaustive ledger and declared heuristics. It says
nothing about SHA-256 security beyond the observation that the normalised unit
rewards bit-slicing.

Consistency with the required checks: the attack is classical, the message domain is
respected, the round count is uniform across every padded block, the digest
comparison uses all 256 bits, no near-collision or free-start relaxation is used,
memory is reported in bytes, and the single-attempt success probability exceeds
0.39 without amplification.

## 10. Attribution and position

The target, its relation, the message domain, the cost model C = 4912, the
reference operation count and the scoring policy are organizer material from this
repository and are used unchanged.

The construction is a textbook parallel collision search (van Oorschot and Wiener,
distinguished points) applied to the block-1 working state of a two-block message
family whose second block is constant padding, so that equal block-1 working states
force equal complete digests. That reduction is the same one used by every generic
entry at rounds 40 to 64 on this lane. The structural design -- constant prefix
words W0..W7 that fold rounds 0..7, a straight-line XOR/AND/OR bit-sliced body
charged one word operation per gate, and a distinguished-point table -- follows the
publicly documented design of a531b41b-1771-4cdb-99e0-f2d6ed1a725b (0xplemonade,
round 40) and c31fe915-4f3a-4dd2-8247-54a554490279 (newjordan, round 64). No source
file, generated kernel, gate stream, table representation, parameter triple,
measured quantity, probability certificate or numeric result of those or of any
other submission is reused. The gate ledger of Section 4, the parameters of Section
5, the certificate of Section 6 and the memory layout of Section 8 were derived
here and differ in every instance: this body is 3,376 bit-plane records against the
published 43,541-record body of the round-64 row, and its ledger is correspondingly
worse.

POSITION. This package is NOT an improvement. The current round-64 row is 124.12385
and this construction is 124.4622, which is 0.338 bits worse; the same gap appears
at every round in the admitted range, so the package fills no gap on the frontier.
It is submitted as a complete, self-contained, exactly-ledgered construction at the
maximum round count, not as a row improvement.

The package contains no certificates, because there is no pair to certify, and no
experiments: every quantity is either an exact integer fixed by the plan of Section
5 or a bound proved in Section 6, so no participant program is needed to reproduce
the arithmetic. The empty certificates/manifest.json is retained as the declared
certificate manifest.
