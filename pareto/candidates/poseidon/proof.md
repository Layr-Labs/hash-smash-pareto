# Full-round Orchard Poseidon: a distribution-free finite collision budget

## 1. Exact target, claim, and limitations

This is an ordinary-collision construction for the protected target
`poseidon-orchard-r56-prefix-v1`: Orchard P128Pow5T3 over the Pallas
field, with all 56 partial rounds AND all eight full rounds. The numeral
56 in the claim counts partial rounds, not total permutation rounds.
Use the fixed prime

    p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001.

In particular 2^254 < p < 2^255. An input is exactly two canonical field
elements (nk,rho), each serialized into 32 little-endian bytes. A value
at least p is rejected, not silently reduced. Initialize the permutation
state to [nk,rho,2^65], preserve the organizer's deployed round constants
and dense 3-by-3 MDS, and return the ENTIRE final coordinate zero in its
canonical 32-byte encoding. There is no free IV, chosen capacity, output
truncation, modular alias, raw-permutation collision, or replacement of
the Orchard hash by the complete nullifier construction.

The algorithm below has a finite, worst-case budget T <= 2^135 selected
target-compression equivalents in `orchard-field-ram-v2`, and succeeds
with probability at least 0.5 using fresh independent algorithmic coins.
Peak memory is at most 2^137 bytes. Preprocessing is included in T and
is conservatively bounded by 2^135 units as well. Searched nonuniform
advice is zero, reported as log2(max(1,advice_bytes))=0. All computation
is classical. These are proved upper bounds for an abstract algorithm,
not measured times, hardware availability, an actual executed collision,
a practical break, or claims of a best-known attack.

The protected model has primitive 256-bit words and Pallas field
operations. We use that exact model, not the 64-bit model of a different
challenge. Raw time and raw memory are separate fields. The successor
Pareto projection would be [56, 135 + (137-20)] = [56,252] if the
complete claim qualifies. That calculation is not an official score or
a claim that the result is on the frontier.

This is a generic birthday-style sampling and sorting analysis. Its
probability proof applies to ANY fixed function on the specified finite
input set, including nonuniform or structurally biased Poseidon outputs.
No random-oracle model, pseudorandom-generator assumption, heuristic
independence of outputs beyond independent inputs, or experimental
extrapolation is used. The only random primitive is the independent
uniform 256-bit word explicitly included in the protected cost model.

## 2. Concrete finite algorithm

Let t=2^128 and B=2^254. The internally selected sampling set is

    D = {0,...,B-1} x {0,...,B-1}, with |D|=N=2^508.

Every tuple in D is a legal target input because B<p. Choosing this
sampling set is an algorithmic choice within the ordinary-collision
domain; it does not change the target, demand a restricted challenge,
or require any promise about a preselected pair of inputs.

Allocate two arrays A and Z, each of t records. A record occupies four
256-bit words (128 bytes): the full output y, input nk, input rho, and
a zero padding word. No sample index or seed is needed to recover a
message, since both input elements are retained exactly.

1. Initialize both record arrays. For each i=0,...,t-1, draw two fresh
   independent uniform 256-bit words R_i,S_i, and set
   nk_i=R_i AND (2^254-1), rho_i=S_i AND (2^254-1). Evaluate the exact
   target H(nk_i,rho_i) using the schedule in Section 3 and store the
   record (H(nk_i,rho_i),nk_i,rho_i,0) in A.
2. Sort all t records by their entire field output using bottom-up
   merge sort and the second array as scratch. There are exactly 128
   passes. Equal-output records remain in one consecutive run. Sorting
   stability is not required, because the full inputs are stored.
3. Scan the sorted array once. At the start of each new output run,
   retain its first record as anchor. Compare the two input words of
   every following record in that run with the anchor. If they agree,
   skip the duplicate input; if they differ, retain the two input
   tuples and end the scan. If a new output value begins, replace the
   anchor. If the scan ends with no distinct-input match, return failure.
4. For a retained pair, re-encode both input tuples canonically, check
   that the tuples differ, recompute BOTH complete hashes, and compare
   the entire output field element. If these checks pass, return the
   two 64-byte messages. Otherwise return failure. No retry occurs.

This always stops within the fixed loops, whether successful or not.
The same stored tuple can be sampled more than once, but it is never
reported as a collision against itself. If any output run contains
two distinct tuples, at least one tuple in that run differs from its
anchor, and the scan finds a valid pair. Every returned pair therefore
has distinct canonical encodings and exactly equal complete target
outputs. Re-evaluation is charged even though it is redundant in an
ideal error-free run. The proof of success below counts genuine pairs,
not repeated sampling of one message.

No target evaluation, table generation, sorting of cryptographic data,
or collision search has been executed for this submission. This finite
algorithm is mathematical evidence only. The certificate manifest is
explicitly empty, and no experimental program or result is declared.

## 3. Fully specified hash evaluation

The constants are the immutable organizer profile's deployed halo2
Poseidon constants and MDS, in
`pareto/orchard-pallas-constants.json` at challenge source commit
4ae50b1f4dcc5e0504430e5ba47077b4657575e8. They are public target parameters,
not searched advice, and are never regenerated or tuned by this algorithm.
The organizer's `verifier/poseidon.py:digest` states the same operation.

For indices 0 through 63, add that index's three round constants to the
state modulo p. At indices 0..3 and 60..63 replace each of the three
coordinates x by x^5. At indices 4..59 replace only coordinate zero by
its fifth power. Compute x^5 by x2=x*x, x4=x2*x2, x5=x4*x, so it needs
three field multiplications rather than a new exponentiation primitive.
Multiply the state by the fixed dense 3-by-3 MDS using canonical field
operations. Do not update a coordinate in place before the other rows
have consumed the old state; use a three-element scratch array. Return
canonical state[0]. Coordinate two is initialized once to 2^65 and
thereafter evolves with the full state in every round; it is not held
constant or reset. There is no additional variable capacity.

Only the given 56-partial-round profile is claimed. All additions,
multiplications, loads, stores and control in this evaluation are counted
in Section 6. The reference normalization denominator is

    C = 216 + 21*56 = 1392.

We charge the implementation's expanded primitive operations and divide
once by C. We do NOT charge one permutation unit and then add its
internal field arithmetic a second time. No inversion, matrix solver,
algebraic estimate involving omega, or square-root routine is used.

## 4. A distribution-free birthday bound

Let U_1,...,U_t be the independent uniform samples from D, and Y_i=H(U_i).
Because H is fixed, the Y_i are independent samples from a fixed
distribution q=(q_1,...,q_p) over the p canonical field outputs. Some
q_j may be zero or much larger than 1/p. The argument does not assume
that H is balanced on D.

For a probability vector q and 2<=t<=p, define the elementary symmetric
polynomial e_t(q)=sum over t-element index subsets J of product(q_j,j in J).
The exact probability that all Y_i are different is t!*e_t(q).

Lemma. Subject to q_j>=0 and sum q_j=1,

    e_t(q) <= binom(p,t)/p^t.

Proof. The finite-dimensional simplex is compact, and e_t is continuous,
so it attains a maximum. Among its maximizers, choose one minimizing
sum q_j^2, which again exists by compactness. For any two coordinates
u,v, keep their sum a fixed and all other coordinates fixed. The
polynomial can be written

    e_t = E_t + a*E_(t-1) + u*v*E_(t-2),

where E_k is the corresponding elementary symmetric polynomial of the
remaining coordinates, with E_0=1 and out-of-range E_k=0. Every coefficient
is nonnegative. Replacing unequal u,v by a/2,a/2 increases u*v, so it
cannot decrease e_t. At a global maximum it must preserve the maximum
(or would contradict maximality). But it strictly decreases u^2+v^2,
contradicting the selected minimum. Hence all coordinates of that
maximizer are equal, namely 1/p. Substitution proves the lemma. This
proof covers zero coordinates and all finite p; it performs no search
over q and requires no access to the actual output distribution. QED.

Consequently

    Pr(all Y_i distinct)
      <= (p)_t/p^t
       = product_(j=0)^(t-1) (1-j/p)
      <= exp(-t(t-1)/(2p)).

The last step uses 1-z<=exp(-z) for z>=0; it follows, for example, from
the derivative of exp(-z)-(1-z), which is nonnegative after zero. Here
t<p, so all factors are nonnegative. Define lambda=t(t-1)/(2p).
Since t=2^128 and p<2^255,

    lambda > (2^256-2^128)/2^256 = 1-2^-128 > 3/4.

The exponential series gives exp(3/4)>1+3/4+(3/4)^2/2=65/32.
Thus Pr(some equal outputs)>1-32/65=33/65.

## 5. Excluding repeated messages and proving the stated probability

Independently of the hash, any particular sampled-input pair is equal
with probability 1/N=2^-508. By the union bound,

    Pr(some repeated input) <= binom(t,2)/N < 2^-253.

Whenever equal outputs occur and all inputs are distinct, the algorithm
finds a genuine ordinary collision. We subtract the larger event of ANY
repeated input, even if a genuine collision also occurs; this is a safe
lower bound, not an independence assumption between those events:

    Pr(success) >= Pr(some equal outputs)-Pr(some repeated input)
                 > 33/65 - 2^-253
                 > 1/2.

For the final inequality, 33/65-1/2=1/130 and 2^-253<1/130. The claim
therefore conservatively states success_probability=0.5, strictly above
the required 0.39. It does not replace algorithmic success by reviewer
confidence. All coins are consumed in the one finite trial of size t;
there is no unspecified seed expansion, expected waiting time, hidden
restart distribution, or uncharged amplification.

The proof applies to the actual fixed hash, not a random hash ensemble.
The uniform-output case is used only as a proved extremum giving the
LOWEST collision probability. No theorem about Poseidon's mixing or
cryptographic security is required.

## 6. Concrete primitive-work certificate

One field or word occupies 256 bits, exactly as the protected Orchard
field-RAM model specifies. Every table byte offset is below 2^137,
so it fits in one 256-bit word. Counters for t=2^128, record addressing,
merge widths, shifts and endpoints fit as well. No address grows past
the model's word width, and no arbitrary-width arithmetic is assigned
unit cost. This is an abstract RAM bound, not an AArch64 implementation.

Each table record is four words. Reading or moving a record uses four
loads and four stores plus fixed pointer/index additions. Reserve 16
primitive operations for a record move; a comparator reads the two
full output words and uses a full-word comparison, branch and address
operations within another allowance of 16. A comparison is on the entire
field element, not a digest fragment or an assumed free sorting key.

For hash evaluation, even a simple fixed loop uses at most 30 canonical
field arithmetic operations per full round and 24 per partial round:
three constant additions, up to nine fifth-power multiplications, nine
MDS products and nine accumulation additions (starting each row from
zero). The extra accumulation additions are intentionally charged even
though the organizer reference uses a slightly cheaper sum. Allow eight
primitive operations per such arithmetic step, including operands,
loads, store, arithmetic, fixed indexing and loop control. That is at
most 240 operations per round. An additional 272 per round covers
state-buffer swaps, branch selection, constant traversal and fixed
round control, for at most 512 per round.

All 64 rounds therefore cost at most 32768 operations. Reserve another
32768 for initializing state/capacity, canonical input/output handling,
temporary copying and call control. This gives a generous finite bound
E=2^16 primitive operations per complete H evaluation. Constants consist
of 192 round elements and nine MDS elements, and their loads are included.
No full-size or toy execution is used to infer this count.

Sampling and writing one record cost at most an additional 512 primitive
operations: two independent random-word draws, two masks, canonical
checks, stores, loop increments, address arithmetic and ordinary control.
The padding word is explicitly written. The generation phase costs

    R_gen <= t*(65536+512).

Initialize both entire arrays and their padding: at most eight word
stores per sample plus bounded control; charge R_init<=512*t. Code and
public-parameter installation are charged separately below.

Bottom-up mergesort has exactly 128 passes. In each pass there are at
most t comparisons and 2t record moves, and allow 128t extra primitive
operations for copying tails, advancing indices, segment lengths, buffer
selection and end checks. Thus each pass costs at most
t*(16+2*16+128)=176t<=256t, plus 4096 fixed control operations per pass.
The total is

    R_sort <= 32768*t + 2^19.

The final run scan, including all duplicated-input checks and anchor
updates, costs at most R_scan=512*t. Store the anchor in fixed scratch;
there is no hash-index dictionary or stored unpriced answer.

Reserve an additional 2^22 operations for finite code/constant setup,
array-base setup, output pair encoding, two extra H evaluations and
their full-output comparison, all remaining fixed bookkeeping, and
failure/output flags. For example, the two extra evaluations cost
2^17, leaving ample explicit room for fewer than 256 public constants,
two 64-byte outputs and a fixed program of fewer than 16384 words.
There is at most one such final pair verification. The algorithm halts
on its unexpected failure instead of adding an unbounded retry.

Summing the NONOVERLAPPING work bounds gives

    R <= (65536+512+512+32768+512)*t + 2^19 + 2^22
       = 99840*t + 2^19 + 2^22
       < 131072*t = 2^145.

The last comparison is exact: t=2^128 and the remaining coefficient
slack 31232*t exceeds both fixed terms. Divide once by C=1392>2^10:

    T = R/1392 < 2^135.

Thus time_log2=135 is a conservative finite upper bound, never rounded
down. It includes unsuccessful samples, initialization, all random
draws, sorting, memory access, collision recovery and final verification.
No separate H reference calls are added because their operations are
already in R. This avoids double counting while pricing every operation.

## 7. Storage, preprocessing, and the normalized cost axis

Two t-record buffers use exactly 2*t*128=2^136 bytes. A fixed 1 MiB
reserve holds code, all public constants, six state/scratch field values,
scalar counters, array endpoints, the scan anchor, the output pair, and
temporary random words. The fixed algorithm consists of short nested
loops; it is not an exponentially unrolled program. A conservative
budget of 16384 program words occupies 524288 bytes, while 201 field
constants occupy 6432 bytes, leaving ample space for the bounded data
and control state. The complete peak satisfies

    M <= 2^136 + 2^20 < 2^137 bytes.

The sampled inputs themselves are retained in the records and counted
in M. Raw random words can be discarded immediately after masking, so
there is no uncounted tape of 2t random words. Both sorting buffers stay
charged throughout, even while one is temporarily unused.

The time budget charges both tables, generation and sorting afresh for
this single run. If all sample generation were classified as
preprocessing rather than attack work, the same T bound still includes
it. The claim conservatively bounds total preprocessing by 2^135 units,
since it is a subset of total work. No precomputed collision or sampled
table is embedded as free advice. Public target parameters and the
fixed algorithm are the only constants; searched nonuniform advice is
zero and is reported by the required logarithmic convention as zero.

For the current successor policy, memory above one MiB adds
memory_log2_bytes-20. The submitted RAW fields remain time_log2=135 and
memory_log2_bytes=137. Their policy projection is 135+117=252, paired
with rounds=56. This is only the arithmetic projection of the claims;
qualification, official publication and human acceptance are separate.
The old cost-model phrase about memory as supplementary does not
override the successor's explicit time-memory policy.

## 8. Evidence status and provenance

There are no submitted experiments, sampled collision witnesses, or
certificate files apart from the required empty manifest. The proof
gives a generic finite-budget randomized construction, not a claimed
precomputed pair. No candidate code is executed locally. A large-scale
attack run is neither supplied nor needed for the finite probability
and analytic resource argument.

Sampling/sorting and the birthday phenomenon are classical techniques.
The elementary-symmetric-polynomial extremal proof and the repeated-input
subtraction above are included so the reviewer can assess the COMPLETE
success claim without fetching a cited theorem. No prior participant
submission, participant code, or submission-specific cryptanalytic
improvement was used. Public metadata was inspected only to establish
that full-round submissions already exist and that this generic control
should not be advertised as a new record.

`baseline_improved` is the organizer's required nominal reference ID,
not an assertion of improvement. This candidate does not beat the
nominal birthday exponent or current leading research. Its contribution
is an explicit full-round, distribution-free, finite-success and
complete-field-RAM accounting certificate. Historical novelty is not
claimed. AI qualification does not imply formal mathematical truth,
independent human approval, a practical attack, points, or a prize.
