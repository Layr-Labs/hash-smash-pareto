# Orchard Poseidon, r = 7: up to two random centres on the two-round line, value-domain Montgomery powering, worst-case count (time_log2 39.23926)

## 0. What is claimed, and what is not

Target `poseidon-orchard-r7-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, partial rounds 4..10, full
rounds 60-63, state [nk, rho, 2^65], digest = the whole first state element). Cost model `orchard-field-ram-v2`,
C(7) = 216 + 21 * 7 = 363.

This entry is an algorithm with a worst-case operation count and a success probability that follows from one declared premise.
**No collision was executed or found at this round count; the certificate manifest is empty.** The algorithm draws one centre
uniformly from the field, builds the odd part g_c of the line polynomial (degree m = 610,351,562), computes S^((p-1)/2) mod g_c by
value-domain Montgomery squaring, takes gcd(g_c, S^((p-1)/2) - 1) with a counted half-gcd, isolates the roots when there are
between 1 and 16 of them, and maps one back to two distinct inputs with equal digests, checked with two reference hashes
before output. Otherwise the attempt fails. It makes at most two such attempts, each with a fresh centre, and stops at the first success; the count W charges both attempts at their caps (the setup once).

Claim: `time_log2` = 39.23926 (the worst-case count W of primitive operations of the algorithm, every cap charged, divided once
by 363), `memory_log2_bytes` = 36.65175, `success_probability` = 0.50999 (over the algorithm's fresh random words, for
the fixed target, given premise H-ONE), preprocessing 0 (every constant is computed inside W), no advice. Normalized cost
55.89101.

Premises (claim.json): H-ONE (score-critical; Section 6, evidence Section 7): at least a fraction 0.30 of centres c have
between 1 and 16 nonzero-square roots of g_c. H-NORMAL (score-critical for the time bound; Section 5): the remainder sequence of
(g_c, Y - 1) is normal, so the half-gcd executes the schedule charged in Section 5; the time claim is conditional on it.
H2 (supporting, cost convention; Section 3.0): the register-file and pricing convention. The pipeline is the one of our
executed r = 1 and r = 2 entries, which certified collisions with it (on the line with lane 2 constant); here it is applied
without execution.


## 1. Target, line and odd part

Orchard P128Pow5T3 over F_p, p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001, width 3, S-box x^5,
deployed round constants rc[i] and MDS matrix M (pinned in `orchard-pallas-constants.json`). The reduced permutation applies
full rounds 0-3, partial rounds 4..10 (S-box on lane 0 only) and full rounds 60-63; the hash of (nk, rho) is lane 0 of the
permutation of [nk, rho, 2^65], the whole field element. x -> x^5 is a bijection of F_p (gcd(5, p - 1) = 1) with inverse
x -> x^e5. p - 1 = 2^32 * 3 * 463 * (two large primes), so F_p has roots of unity of every order 3 * 2^k and 2^k, k <= 32.

**Lemma 1 (line).** Let k = 0 be the lane whose round-1 S-box input is made constant and (i, j) = (1, 2) the other two. With
c0 = rc[0], c1 = rc[1], K5 = (2^65 + c0[2])^5, A = (nk + c0[0])^5, B = (rho + c0[1])^5, the round-1 S-box inputs are
u_t = M[t][0] A + M[t][1] B + M[t][2] K5 + c1[t]. Put mu5 = -M[0][0] / M[0][1] and let (A0, B0) solve
M[t][0] A0 + M[t][1] B0 + M[t][2] K5 + c1[t] = 0 for t = 1, 2 (the 2x2 minor of the MDS matrix is invertible). On the line
A = T + A0, B = mu5 T + B0 the inputs are u_0 = kappa (a constant) and u_t = a_t T (t = 1, 2, a_t = M[t][0] + M[t][1] mu5,
nonzero), so the round-1 S-box outputs are affine in T' = T^5, and T' -> (nk, rho) = (A^e5 - c0[0], B^e5 - c0[1]) is injective.
This is the line on which round 1's first S-box input is constant, the line "j = 0" of the published entries of Jbenisek
(767cdef0-485d-443a-92ec-652ee8166c4a and later); the line is unique as a set (two linear conditions on (A, B) and one free
direction), and the count k(c) of Section 2 over uniform centres does not change under an affine reparametrization of its
parameter. (Our executed r = 1, 2, 3 entries used the line with lane 2 constant; the method is the same.)

**Lemma 2 (degree).** Applying rounds 2, 3, 4..10, 60..63 to the affine state after round 1 and taking lane 0 gives a
polynomial F(T') of degree exactly D = 5^(6+7) = 1,220,703,125 with leading coefficient a_D != 0 (the program `lead_coefficient` follows
(degree, leading coefficient) of each lane through every round and asserts that no leading coefficient cancels), and
H(nk(T), rho(T)) = F(T^5).

**Lemma 3 (odd part).** For a centre c, F(c + s) - F(c - s) = 2 s a_D g_c(s^2) with g_c monic of degree m = (D - 1)/2 = 610,351,562. If S
is a root of g_c that is a nonzero square and s^2 = S, then W1 = c + s != W2 = c - s and F(W1) = F(W2); by Lemma 1 the two
inputs are distinct canonical pairs with equal reduced hash. The roots of g_c that are nonzero squares are exactly the roots of
G = gcd(g_c, S^((p-1)/2) - 1) (Euler's criterion; S^((p-1)/2) - 1 splits into distinct linear factors), and k(c) := deg G.

As a polynomial in c, g_c(x) has degree exactly D - 1 for every fixed x (its x^0 coefficient is F'(c), of degree D - 1 with
leading coefficient D a_D != 0, and the other coefficients have lower degree in c), so for any fixed set of n points
P(g_c vanishes at one of them) <= n (D - 1) / p over a uniform centre (Schwartz-Zippel).


## 2. The algorithm (up to two centres)

Sizes: D = 1,220,703,125, m = 610,351,562, n = 805,306,368 (the least 3 * 2^k or 2^k above m), omega a primitive n-th root of unity, psi a primitive
2n-th root with psi^2 = omega, O1 = {omega^i}, O2 = {psi omega^i}.

1. Centre. Draw 255-bit random words until one is below p (at most 64 draws; each draw is one random word, a mask, a comparison
   and a branch); c is that word, uniform on F_p. If 64 draws fail, the attempt fails.
2. Values of g_c on O1. For t = 0..n-1 in transform order, s_t = psi^e(t) and G1[t] = (F(c + s_t) - F(c - s_t)) (2 a_D s_t)^-1
   = g_c(omega^e(t)), by 2n line evaluations (affine state after round 1, then the remaining 6 + 7 rounds) and two
   prefix-product point generators (`attack_mont.build_G1`, `mont.point_stream`).
3. Montgomery stage: Y = S^((p-1)/2) mod g_c by value-domain Montgomery squaring with R = X^n - 1 on O1 and O2 (`mont.py`;
   the stage C of bradcush 1aa56884-8e68-4aa8-87c7-ed38d0a3e65b and 4bcabff8-2863-4d70-a0d3-401da0cbe5fb, reimplemented):
   interpolation of g_c, the start X^a R mod g_c from one Newton inverse and one cyclic product, the batch inversion of G1 (if
   the product of the G1[t] is 0, i.e. g_c has a root on O1, the attempt fails), the tables on O2, 226 squarings (45 with the
   multiplication by X) at four transforms of length n each, and the final conversion, which returns Y fully reduced.
4. G = gcd(g_c, Y - 1) by the counted half-gcd (`halfgcd.py`, top-level reduction n0/12, base case below 48, wrapped
   matrix-vector steps and shared matrix products on transforms whose length is the least 3 * 2^k or 2^k that holds them).
   If deg G = 0 or deg G > 16, the attempt fails.
5. Roots of G by equal-degree splitting with random shifts: a shift a is drawn from one random word (low 254 bits), and
   gcd(G, (X + a)^((p-1)/2) - 1) splits G unless all roots r_i + a have the same quadratic character; at most 64 draws per call
   and at most 2 deg G - 1 calls; if a call exhausts its draws, the attempt fails.
6. Finish. For one root S (S != 0 since S is a root of S^((p-1)/2) - 1): s = sqrt(S) by Tonelli-Shanks (p - 1 = 2^32 t),
   W1 = c + s, W2 = c - s, the inputs of both by the inverse line map (three fifth roots each), both reduced hashes, and their
   comparison; output the two inputs.

7. If the attempt failed and it was the first, return to step 1 with a fresh centre (the setup is kept); after the second attempt, stop.

Every loop has an explicit cap, so the count of Section 4 bounds every execution, successful or not.


## 3. Operation charges

3.0 Convention (the claim). Prices follow `orchard-field-ram-v2`, applied as the executed-count entries on
this board apply it (Jbenisek 767cdef0-485d-443a-92ec-652ee8166c4a, bradcush 4bcabff8-2863-4d70-a0d3-401da0cbe5fb):
  - one unit per field addition, subtraction or multiplication;
  - two units per 256-bit load or store: the access and one address operation (index arithmetic);
  - loops: a loop over e elements written eight elements per iteration costs 3 per iteration (index update,
    comparison, branch) plus 2 on exit, LP(e) = 3 ceil(e/8) + 2; a loop that is not unrolled costs 3 per
    iteration plus 2 on exit; every other comparison, branch or bit operation (trailing-zero counts, degree
    tests) one unit ('ctl');
  - register file: at most 16 words of 256 bits. Values held there (the running twiddle and twist factors,
    the eight elements and three twiddles of one radix-8 transform block, the line state of one evaluation,
    loop-invariant scalars such as h = -1/2 and 1/n) are operands, not loads. The register file is inside
    the 1 MiB code allowance of Section 4.
  - inversion 380 units (a round-up of the 330-unit ladder for x^(p-2), registers only); a fifth root x^e5
    is 253 squarings and 124 multiplications, 377 units; exponentiations are binary ladders of
    (bits - 1) squarings plus (popcount - 1) multiplications; a reduced permutation evaluated as a
    reference hash in the finish is one target-compression unit, C(r) operations.
Every kernel records its loads, stores, arithmetic, control and loops separately (`ntt.Counter`), so the
same run is also priced under the looser rule of our earlier entries (one unit per load or store, 1/2 unit
of loop control per element of a streaming loop). That second figure is reported only for comparison
(the loose figures quoted in 3.2 and 3.3); the claim uses the convention above, which is the larger.

3.1 Transforms. For n = 3*2^k the forward transform is decimation-in-frequency and the inverse is
decimation-in-time, so pointwise steps act on the permuted order and no bit-reversal pass exists; the
radix-3 stage is innermost and untwiddled. Twiddles come from a running product in a register (one
multiplication per butterfly), so there is no twiddle table. Radix-2 levels run in register-blocked passes
of three levels (one radix-8 block of eight elements is loaded, three levels of butterflies are applied in
registers, the block is stored), so each element costs 1/3 load and 1/3 store per level; the radix-3 level
is one pass with one load and one store per element. Per radix-2 level: n/2 butterflies of 4 field
operations (twiddle update, twiddle product, addition, subtraction), 2n/3 accesses, and LP(n/2) loop
charge; the radix-3 level: n/3 blocks of 8 field operations, 2n accesses, LP(n/3):
  T_strict(n) = k (4 (n/2) + 2 (2n/3) + LP(n/2)) + (8 (n/3) + 4n + LP(n/3)),
For n = 2^k there is no radix-3 level; the k radix-2 levels are followed by one closing load/store pass for the k mod 3
leftover levels: T_strict(n) = k (4 (n/2) + 2 (2n/3) + LP(n/2)) + 4n + LP(n), loose n (35k/12 + 5/2).
T_strict(805,306,368) = 84,859,158,586 (loose rule: 69,659,000,832). The transform constants are the roots of unity of orders 3 * 2^i and 2^i
(i <= 31; psi, of order 2n, is among them) and their inverses, which give every per-level twiddle step of every length used (a step of a level is such a root), plus
1/N for each length used: fewer than 440 constants, each an exponentiation of at most 400 units (the largest ladder among these exponents, (p - 1)/N and
(p - 1) - (p - 1)/N for every order N used, is 400 squarings plus multiplications, for psi), plus an address operation for each
of their at most 440 stores, charged once in the setup (176,000 + 440). The closed forms are asserted equal to the instrumented
kernels (Appendix A) at the lengths listed in their self-tests in both conventions, and the convolution is checked against schoolbook multiplication.

3.2 Build (step 2 of Section 2): 2n line evaluations; one evaluation is 6 + 27*6 + 21*7 = 315 field
operations (affine state after round 1: 3 multiplications and 3 additions; six full rounds at 27: three
constant additions, three x^5 at 3 multiplications, the MDS at 9 multiplications and 6 additions; 7 partial rounds at
21) and 6 + 12 (6 + 7) = 162 constant loads (6 affine coefficients, then 3 round constants and the 9
MDS entries per round; the three-lane state stays in registers): 639 units strict. Per position:
c + s_t and c - s_t (2), the difference and the product with the factor (2), one store; the loop over
positions is not unrolled (3 per iteration, 2 on exit). Point generator (`point_stream`, closed form `PG`):
a stack of k + 1 prefix products over the bits of the block index (k + 1 initial stores); per block one loop
iteration with the trailing-zero count and branch (5 ctl), recomputation of one prefix (two loads, one
multiplication, one store), straight-line stores of the prefixes below the changed bit (over all blocks
n/3 - k - 1 stores), two multiplications for the cube-root companions of the block's point; 2 on exit. Build
charge per trial: 1,045,019,230,200 units (loose 781,147,176,958). Peak: the n words of G1.

3.3 Montgomery stage (step 3 of Section 2), closed forms of `mont.py` (functions TV, TW, PASS, STEP, SINV, BINV, SETUP_POWER),
each asserted equal to the instrumented execution in the self-test against FLINT (m = 20..370 on 3 * 2^k lengths and
m = 60..250 on 2^k lengths) and, at r = 1 and 2, in our executed runs, which recorded the per-phase marks in both conventions. A streaming pass over e elements
with a field operations, l loads and s stores per element costs e (a + 2 l + 2 s) + LP(e):
  - interpolation of g_c: scaled copy of G1 (1 load, 1 multiplication, 1 store per word) and one inverse
    transform: 89,187,680,316;
  - start residue: Newton inverse of rev(g_c) to precision L at steps m -> m2 = min(2m, L), length N = least
    3*2^i >= m2, d = m2 - m: copy-and-pad of rev(g_c) (min(m2, m+1) loads, N stores) and of the current
    inverse (m loads, N stores), 5 transforms, two pointwise products (2 loads, 2 multiplications, 1 store per
    point), copy of d words, zero padding of N - d words, and the update (load, subtraction, store per word);
    then the reversed copy into the n-word buffer with padding, a forward transform, the pointwise product with
    G1 and the factor -1/n, an inverse transform and the zeroing of positions m..n-1: 814,572,058,769;
  - batch inversion of G1 into Ginv1 = -1/(n G1) (Montgomery's trick; prefix products in a scratch buffer;
    one inversion; the factor -1/n folded into the inverted product): 11,072,962,939;
  - tables: start values on O2 (copy with twist and a forward transform), on O1 (one forward transform in
    place), G2h (twist with c0 = -1/2 and a forward transform): 264,845,131,954;
  - powering: per squaring 4 transforms, the twist and the untwist (1 load, 2 multiplications, 1 store per
    word), the pass U1 = A1^2 Ginv1 (2 loads, 2 multiplications, 1 store), the pass B2 = A2^2 h + U2 G2h (3 loads,
    3 multiplications, 1 addition, 2 stores into A2 and the work buffer): 368,025,010,416 (loose 297,963,356,160); with the
    multiplication by X add one multiplication per point and one point generator: 373,125,284,075; 226 squarings,
    45 of them with X: 83,403,164,668,671;
  - finish: half-step (U1 pass, inverse, twist, forward, B2 pass), interpolation on O2 (inverse, untwist) and the
    recovery of g_c (inverse, untwist): 369,937,613,042.
  Stage total per trial: 84,952,780,115,691 units strict (loose 68,776,300,524,206). Buffers: A1, A2, Ginv1, G2h of n words each
  (4n); during the Newton step G1, g_c, the two Newton buffers (2 N <= n) and the growing inverse (<= L words):
  at most 2n + max(2N + m2). Peak of the stage: 3,221,225,472 words.

3.4 Setup, once: the constants of Lemma 1 (two inversions, fifth powers, products and sums) as a flat 4,000
units (twice the 2,000 of our earlier entries), the transform constants (176,000 + 440), the
leading-coefficient recursion of Lemma 2 with the inversion of 2 a_D (bounded by 24 (8 + r) + 381 = 741),
the Tonelli-Shanks constant 5^t (267), and a bound of 20,000 for writing the output (two pairs, the digest):
201,448 units. Per trial: the centre (1 unit) and forming Y - 1 (load, subtraction, store: 5 units).

3.5 Centre draw, root stage and finish (caps). Centre: at most 64 draws of 4 units (random word, mask, comparison, branch):
256. Root stage for deg G <= 16 (`gcd_mock.roots_bound_strict`, strict prices): at most 2 deg G - 1 = 31 calls, each at most 64
draws, a draw being one shift word, (X + a)^((p-1)/2) mod G by 253 schoolbook squarings and multiplications by X + a with the
bit loop over the exponent (shift, mask test and branch per bit: 3 * 254 = 762 units per exponentiation), the constant
subtraction, a classical Euclid of at most deg G divisions and a monic normalisation, and each call one exact division:
2,064,757,683. Finish (registers only): Tonelli-Shanks at its worst case (the exponentiation S^((t-1)/2), 2 multiplications, at most 32
outer iterations of at most 1 + 5 * 31 + 6 units), the two line points (2), the inputs of both sides (2 (3 * 377 + 8)), two
reduced hashes (2 * 363) and the comparison (8): 8,467. Y - 1: 5.


## 4. Worst-case ledger, memory and declared bounds

Every row is a closed form of Section 3 evaluated at the sizes of Section 2 (`heur.py`, Appendix A), each at its cap:

| row | units |
|---|---:|
| setup (line constants, transform constants, leading coefficient, Tonelli-Shanks constant, output bound; 3.4) | 201,448 |
| centre draw: 64 x 4 (3.5) | 256 |
| values of g_c on O1: 2n line evaluations + point generators (3.2) | 1,045,019,230,200 |
| Montgomery stage: interpolation, start residue, batch inversion, tables, 226 squarings, finish (3.3) | 84,952,780,115,691 |
| Y - 1 (3.4) | 5 |
| half-gcd, normal schedule, top-level n0/12, 2^k wrapped lengths allowed, strict (Section 5) | 31,779,740,740,682 1/3 |
| root stage, deg G <= 16, 64 draws per call (3.5) | 2,064,757,683 |
| finish: Tonelli-Shanks worst case, line points, inputs, two hashes, comparison (3.5) | 8,467 |
| second attempt (every row above except the setup, at its cap) | 117,779,604,852,984 1/3 |
| **total W** | **235,559,209,907,416 2/3** |

W = 235,559,209,907,416 2/3 operations; T = W / 363; log2 T = 39.239257, submitted as `time_log2` = 39.23926 (ceiling at five decimals;
W^100000 <= 2^3923926 * 363^100000 checked in exact integer arithmetic by `gen_heur.py`).

Memory (live words of 32 bytes at the peak of each stage, plus a fixed 2^20-byte allowance for code, constants, the 16-word
register file and the stack):

| stage | peak live words |
|---|---:|
| values of g_c on O1 (build) | 805,306,432 |
| Montgomery stage (4n: A1, A2, Ginv1, G2h; the Newton step needs at most 2n + 2N + L) | 3,221,225,472 |
| half-gcd (memory model of Section 5, normal schedule) | 3,373,813,366 |
| **peak** | **3,373,813,366** |

Total 107,963,076,288 bytes; log2 = 36.651747, submitted as `memory_log2_bytes` = 36.65175 (ceiling at five decimals; checked in
exact arithmetic). Normalized cost 39.23926 + (36.65175 - 20) = 55.89101.

Declared bounds against the true values: time and memory as above, on every control path of the algorithm (all caps charged),
given H-NORMAL for the gcd stage (Section 5);
`success_probability` 0.50999 <= the bound of Section 6 under H-ONE; `preprocessing_log2` 0: every constant of the algorithm (the
line constants, the leading coefficient a_D, the transform roots and twiddle steps, the Tonelli-Shanks non-residue power) is
computed inside the attempt and charged in the setup row; the algorithm's fixed design choices (the top-level fraction n0/12,
the rule for transform lengths, the caps) are constants of its description, chosen once by the authors from closed forms, not
work the attack performs; no advice. Preprocessing memory: there is no work before the attempt; the setup (line constants,
leading coefficient, transform constants, a few dozen words) runs inside the first attempt before the build and below the peak of
the table above.


## 5. The half-gcd charge on a normal remainder sequence (H-NORMAL)

The gcd stage is the counted half-gcd of our executed entries (`halfgcd.py`; the charges of 5.2 and the strict re-pricing of
5.2s of those entries, reproduced in `halfgcd_charge.py`, Appendix A). Its executed schedule depends on the degrees of the
remainder sequence of (g_c, Y - 1) only. For a normal sequence (every quotient of degree 1, down to deg G) every degree in
the recursion is determined by m, and `gcd_mock.py` runs the unchanged control flow of `halfgcd.fast_gcd` on polynomials that
carry only their degree, with the cancellations of the remainder sequence stated explicitly (a wrapped matrix-vector step
returns degrees n_h and n_h - 1), memoizing a sub-call by (deg r0, deg r1, k). Its histogram feeds the same charge functions.

Memory model (as in our executed entries): the half-gcd counter adds the live coefficient words of every polynomial held by an
active frame of the recursion (the inputs g_c and Y - 1 at the top, the cofactor matrices, the remainders) and the transform
scratch of each step (2N for a transform product, 4N for a wrapped matrix-vector step, 6N for a shared matrix product); the
peak of Section 4 is the maximum of that sum.

Validation (logs in Appendix B), with the charged configuration (n0/12, 2^k wrapped lengths allowed) and with the default one:
on pseudo-random instances of degree 300 to 39062 whose executed sequence was normal (gcd of degree 0), the mock histogram and
memory peak equal those of the executed counted run exactly; where gcd(g, S^((p-1)/2) - 1) had degree 1 or 2, and on 15
further instances of degree 300, 1000 and 5000 built with prescribed square roots so that deg G is 3 to 9 (`--selftest-degG`),
the executed gcd-plus-root charge was at most the mock charge plus the root-stage bound of Section 3 and the executed memory
peak at most the mock peak; the memoized mock equals the plain mock (histogram, charge, peak) at degree up to 195312.

**H-NORMAL (score-critical for the time bound).** For each centre drawn by the algorithm, the remainder sequence of (g_c, Y - 1) is normal
down to deg G, so the gcd stage executes at most the schedule charged here. Scope: this target and line. Evidence: the
organizer experiments `hone-layers2a/2b/2c`, `hone-layers3a/3b/3c` and their replicates (Section 7), which report for every computed centre
whether the remainder sequence of (g_c, Y - 1) on this line at two and three S-box layers is normal (pre-run: emulated in the pinned organizer image with the organizer runner and its public seed protocol (hashsmash-public-seed-v1; in-container compute per run from 2.54 to 4.12 s at one CPU (separate timing runs of the same program, container start excluded); docker run seconds per run, container start included, from 3.80 to 5.59; parts a, b, c of each layer count combined): 2 layers: normal on 1024 of 1024 centres (largest degree drop 1); 3 layers: normal on 24 of 24 centres (largest degree drop 1));
the validation above; our executed r = 1, 2 and 3 runs (degrees 39062, 195312 and 976562) recorded normal sequences (every
division of degree n by n - 1 and every wrapped step with a degree drop of 1). Limitation: a non-normal
sequence is possible with probability of order m / p per step under the random-polynomial heuristic; on such a sequence the
algorithm still returns the correct gcd but its schedule, hence its cost, differs from the one charged.


## 6. Success probability (premise H-ONE)

**H-ONE (score-critical).** The number of centres c in F_p with 1 <= k(c) <= 16 is at least 0.30 p, where k(c) is the number of
nonzero squares S with g_c(S) = 0 (the degree of the gcd of step 4).

Role: score-critical, the only score-critical premise for the success probability (H-NORMAL, Section 5, is score-critical for the time bound). Scope: the fixed target poseidon-orchard-r7-prefix-v1, this line,
centres uniform on the field. Extrapolation: from the law below and from the measurements of Section 7 at smaller degrees to
degree m = 610,351,562. Limitations: false for permutation polynomials and for decomposable F with imprimitive monodromy; not proved
at this degree.

**Bound.** Given H-ONE, the attempt succeeds unless (a) the centre draw fails (probability (1 - p / 2^255)^64 < 2^-64, since
p > 2^254), (b) g_c has a root on O1 (probability at most n (D - 1) / p over the uniform centre, Section 1), or (c) a root-isolation
call exhausts its 64 draws. For a split G with at least two distinct roots and a shift a, the roots r_1 + a and r_2 + a have the same
quadratic character with probability at most 1/2 + 3/p for a uniform a (the character sum of (X + r_1)(X + r_2) is at most 1 in
absolute value), and our shifts are the low 254 bits of a random word, which changes any probability by at most (p - 2^254) / 2^254 <
2^-125; at most 2 * 16 - 1 calls give (c) <= 31 (1/2 + 2^-124)^64. Every other step is deterministic and correct by Lemma 3
(Section 1), Section 3 and the correctness of the gcd. Hence

  P(one attempt succeeds) >= 0.30 - 2^-64 - n (D - 1) / p - 31 (1/2 + 2^-124)^64 = 0.29999999999999999826, and the two attempts use
  independent fresh random words, so P(success) >= 1 - (1 - 0.29999999999999999826)^2 = 0.50999999999999999757,

and the claim files `success_probability` = 0.50999. The probability is over the algorithm's fresh random words for the fixed
target; it is not a frequency and not a probability over targets.

Where the number comes from. The roots of G(c, t) = g_c(t^2) come in pairs +-t_i, so the Galois group of the generic fibre lies in
the hyperoctahedral group B_m, and k(c) counts the positive fixed points of the Frobenius element at c; for the full group B_m this
count is asymptotically Poisson(1/2), so P(k >= 1) = 1 - e^(-1/2) = 0.39347 and P(k > 16) is below 1e-15. H-ONE asks for 0.30, well below that value. The two-attempt design and the value 0.30 were fixed after we had seen the organizer-run counts of Section 7 (this and our other packages); those counts are therefore not an independent test of this value. 0.30 is a round value below the one-sided 99% Wilson lower bound of each of our packages that use it (r5 0.332, r6c 0.330, r7b 0.391; r8, a one-attempt package at 0.3901, 0.304) and of the four pooled (0.364); the law (0.39347) and our own FLINT samples (Section 7) do not depend on that choice. A holdout rerun of the declared experiments would test it afresh. Our premise is a weaker form (0.30 instead of 0.3901) of the premise of Jbenisek's entries 813d502d-91bb-4a81-8c58-553cab9e7684 and 17a75731-701c-41ed-a6f0-52122fe72aec at r = 7 and r = 13 (stated on the same
line); it is stated here for this round count and we do not reuse their computations as evidence for it.


## 7. Evidence for H-ONE and for the method

- Declared organizer experiments `hone-layers2a`, `2b`, `2c` and `hone-layers3a`, `3b`, `3c`, with pre-declared
  replicates `-rep2`, `-rep3`, `-rep4` of each two-layer part and `-rep2` of `3a` (a replicate is the same computation on the
  fresh organizer seeds of its own id; 16 experiments, the manifest maximum) (one program,
  `experiments/hone_layers.py`, standard library, generated by `mk_hone_exp.py` from `hone_layers_src.py` with the pinned
  constants of rounds 0-7 embedded; the work is split over parts so that each run stays well inside the 20 s limit; measured run times are quoted in the pre-run below): for each
  organizer seed in the part a uniform centre c, the odd part g_c of the line polynomial after two (degree 25; parts 2a, 2b, 2c
  take the trials of index 0, 1, 2 mod 3, so together every trial) or three (degree 125; trial indices 0-5, 6-11, 12-17) S-box
  layers, k(c) = deg gcd(g_c, S^((p-1)/2) - 1) computed exactly, and whether the remainder sequence is normal (for H-NORMAL);
  both are reported as observations (no message pair is returned).
  These are the two- and three-layer copies on which H-ONE's law can be checked directly; the line polynomial of the program equals the one interpolated from the permutation, and k(c) and the normal flag agree
  with FLINT on every computed trial of the emulation (`hone_flint_check.py`, log in Appendix B). Pre-run: emulated in the pinned organizer image with the organizer runner and its public seed protocol (hashsmash-public-seed-v1; in-container compute per run from 2.54 to 4.12 s at one CPU (separate timing runs of the same program, container start excluded); docker run seconds per run, container start included, from 3.80 to 5.59; parts a, b, c of each layer count combined): 2 layers: 1024 centres, k = 0, 1, 2, >= 3 in 591, 333, 90, 10; fraction with 1 <= k <= 16 = 0.4229; 3 layers: 24 centres, k = 0, 1, 2, >= 3 in 11, 13, 0, 0; fraction with 1 <= k <= 16 = 0.5417; pooled over both layer counts: 446 of 1048 = 0.4256, +2.13 standard errors from the law value 0.39347 (standard error 0.0151). Under the law of Section 6 a fraction over n centres has mean 0.39347 and standard error sqrt(0.39347 * 0.60653 / n)
  (0.0216 at n = 512).

- Large samples of our own on the same line polynomial at two and three layers (`kc_line_sample.py`, FLINT, centres from
  SHA-256 of a fixed label; log in Appendix B): 2 layers: 100000 centres, k = 0, 1, 2, >= 3 in 60299, 30402, 7780, 1519; fraction with 1 <= k <= 16 = 0.39701 (standard error 0.0015; +2.29 standard errors from the law value 0.39347, +62.70 from the premise value 0.30); 3 layers: 20000 centres, k = 0, 1, 2, >= 3 in 12138, 6067, 1510, 285; fraction with 1 <= k <= 16 = 0.39310 (standard error 0.0035; -0.11 standard errors from the law value 0.39347, +26.96 from the premise value 0.30). The two-layer sample lies above the law value by 2.29 standard errors (a measured excess; at m = 12 the finite-degree distribution need not equal its Poisson limit); an excess does not weaken the success bound. The two-layer organizer fraction of this package (433 of 1024 = 0.4229) differs from our two-layer sample by +1.67 standard errors of the difference.
- k(c) on this line at r = 0 (m = 7812) and r = 1 (m = 39062), supplementary runs of our own: `kc_stats.py` builds g_c by the
  same build and FLINT computes gcd(g_c, S^((p-1)/2) - 1) for consecutive centres c = 1, 2, ...:
  r = 0, centres 1..200: k = 0, 1, 2, >= 3 in 115, 58, 25, 2; fraction with 1 <= k <= 16: 0.4250
  r = 1, centres 1..39: k = 0, 1, 2, >= 3 in 16, 17, 5, 1; fraction with 1 <= k <= 16: 0.5897
  Poisson(1/2) gives P(k = 0, 1, 2, >= 3) = 0.607, 0.303, 0.076, 0.014 and P(1 <= k <= 16) = 0.3935.
- Executed runs of the same pipeline (our r = 1 and 2 entries, line with lane 2 constant, centres c = 1, 2, ...): r = 1: centre c = 1 gave deg G = 1 (collision certified); r = 2: centre c = 1 gave deg G = 1 (collision certified); r = 3: c = 1: deg G = 2 (certified).
- The mock schedule of Section 5 and its validation logs (Appendix B).
Reading of the organizer experiments of this package (emulated in the pinned organizer image with the organizer runner and the public seed protocol; the organizer run reproduces these counts exactly unless it adds a holdout nonce, which draws different centres): two layers combined: 433 of 1024 = 0.4229 (+1.92 standard errors from the law value, +7.96 from the premise value 0.30); three layers combined: 13 of 24 = 0.5417 (exact binomial tail P(X >= 13) = 0.102 under the law value); all experiments pooled: 446 of 1048 = 0.4256 (+2.13 standard errors from the law value, +8.22 from the premise value 0.30). By experiment set: 2 layers set 1: 117 of 256 = 0.4570 (+2.08 standard errors from the law value, +5.04 from the premise value 0.30); 2 layers set 2: 100 of 256 = 0.3906 (-0.09 standard errors from the law value, +2.97 from the premise value 0.30); 2 layers set 3: 106 of 256 = 0.4141 (+0.67 standard errors from the law value, +3.71 from the premise value 0.30); 2 layers set 4: 110 of 256 = 0.4297 (+1.19 standard errors from the law value, +4.19 from the premise value 0.30); 3 layers set 1: 11 of 18 = 0.6111 (exact binomial tail P(X >= 11) = 0.051 under the law value); 3 layers set 2: 2 of 6 = 0.3333 (exact binomial tail P(X <= 2) = 0.558 under the law value). Measured excess: the pooled figure lies above the law value by more than two standard errors (or its exact tail is below 0.023); an excess means more centres with 1 <= k(c) <= 16 than the premise needs, so it does not weaken the success bound. Measured excess: 2-layer set 1 lies above the law value by more than two standard errors (or its exact tail is below 0.023); an excess means more centres with 1 <= k(c) <= 16 than the premise needs, so it does not weaken the success bound. Against the premise value 0.30: the pooled organizer fraction of this package is above it, and so is its one-sided 99% lower confidence bound (Wilson) 0.3905; pooled over all our packages (1311 of 3418 = 0.3836, +10.05 standard errors from 0.30, lower bound 0.3644) the counts lie above it as well; the organizer-run counts support the premise value at the degrees they test. Pooled with the emulated experiments of our other packages (r5, r6c, r8; the same computation on the same line polynomials at two and three layers with the organizer seeds of each target; the program file of r8 differs only in its replicate-id handling): 1311 of 3418 = 0.3836, -1.19 standard errors from the law value. These are measurements at small degree and small counts; they lie far above the premise value 0.30 but test degrees 12 and 62 only. The premise is extrapolated to m = 610,351,562.


## 8. Limitations and credits

No collision was executed at this round count; the claim is a worst-case count of the stated algorithm with a success
probability conditional on H-ONE, and a gcd cost conditional on H-NORMAL. The counts rest on the closed forms and the
listings of Appendix A; the organizer does not run them. The 1 MiB allowance for code, constants, registers and stack is a
declared bound.

Credits: Bariant, Bouvier, Leurent and Perrin (ToSC 2022(3)) for the two-round bypass; tanctl
(b257d730-1bdf-4078-88c1-15e0d4657031) for the line on this board; Jbenisek for the odd-part reduction, the
one-centre algorithm and the premise H-ONE (767cdef0-485d-443a-92ec-652ee8166c4a, 813d502d-91bb-4a81-8c58-553cab9e7684,
17a75731-701c-41ed-a6f0-52122fe72aec); 0xshikhar (86ebd942-5d22-4786-b065-332ba3180792, edd943c9-0e58-4dab-99b5-62ec51e39fbd) for the
odd-part pipeline at r = 2 and 3; bradcush (1aa56884-8e68-4aa8-87c7-ed38d0a3e65b, 4bcabff8-2863-4d70-a0d3-401da0cbe5fb) for the
value-domain Montgomery stage C; our own kernels and executed entries (3a5f5d55-804a-4fd4-94eb-c915593d3dca,
186052af-551a-4146-962f-245da3bcefbe). No code of another participant was copied.

## Appendix A. Program listings

Standard library plus python-flint for the self-tests. `python heur.py 7 12` prints the ledger of Section 4;
`python ntt.py` and `python mont.py` run the kernel self-tests; `python gcd_mock.py --selftest`, `--selftest-pow2` and `--selftest-degG` run the validation of
Section 5; `attack_v4_ref.py` provides the line (`Target`, with k = 0 here) and its `run` is not used.

### heur.py

```python
"""heur.py - worst-case strict ledger of the ONE-CENTRE algorithm (not executed) at round r.
Stages (all strict, proof 4.0 convention): setup; centre draw (<= 64 rejection draws of a 255-bit word);
build (2n line evaluations); Montgomery stage (closed forms, mont.py); Y - 1; half-gcd on a normal remainder
sequence (gcd_mock.py: the executed control flow on degrees, equal to executed runs where sequences are normal);
root stage bounded for deg G <= 16 with <= 64 splitting draws per call; finish bounded (Tonelli-Shanks worst
case, inverse map, two reference hashes). Memory = max of the stage peaks + 1 MiB.
Usage: python heur.py <r> [fractions ...]   -> JSON with the per-stage charges, time, memory and score."""
import sys, json, math
from fractions import Fraction
from ntt import P, mont_length
from mont import SETUP_POWER, PEAK_WORDS, V
from gcd_mock import run_mock, roots_bound_strict
from halfgcd_charge import charge_strict
from attack_mont import BUILD, SETUP, EXP_COST, ROOT5_COST, TS_T

CODE = 1 << 20
DRAW_CAP = 64
DRAW = 4                     # one random word, mask to 255 bits, compare with p, branch


def ts_worst():
    """Tonelli-Shanks worst case (p - 1 = 2^32 t): the exponentiation, 2 multiplications, then at most 32 outer
    iterations; iteration with M, i: 1 + 5 i + 4 (M - i - 1) + 6 <= 1 + 5 (M - 1) + 6; final test 1."""
    tot = EXP_COST((TS_T - 1) // 2) + 2
    M = 32
    for _ in range(32):
        tot += 1 + 5 * (M - 1) + 6
    return tot + 1


def ledger(r, fractions=(8, 12, 16, 24)):
    D = 5 ** (6 + r); m = (D - 1) // 2; n = mont_length(m + 1); C = 216 + 21 * r
    E = (P - 1) // 2
    ph, inf = SETUP_POWER(m, E)
    power = sum(ph.values(), V())
    best = None
    for fr, p2 in [(f, q) for f in fractions for q in (False, True)]:
        mk = run_mock(m, fr, pow2=p2)
        g = charge_strict(mk['trace'])
        peak = max(n + 64, PEAK_WORDS(m), mk['peak_words'])
        rows = {'setup': SETUP(r).s, 'centre_draw': DRAW_CAP * DRAW, 'build': BUILD(n, r).s, 'montgomery': power.s,
                'y_minus_1': 5, 'half_gcd': g, 'roots_deg16': roots_bound_strict(16),
                'finish': 1 + ts_worst() + 2 + 2 * (3 * ROOT5_COST + 8) + 2 * C + 8}
        W = sum(rows.values(), Fraction(0))
        t = math.log2(W / C); mm = math.log2(peak * 32 + CODE)
        rec = {'r': r, 'm': m, 'n': n, 'C': C, 'top_fraction': fr, 'pow2': p2, 'rows': {k: float(v) for k, v in rows.items()},
               'rows_exact': {k: str(v) for k, v in rows.items()}, 'W': str(W), 'time_log2': t,
               'peaks': {'build': n + 64, 'montgomery': PEAK_WORDS(m), 'half_gcd': mk['peak_words']},
               'peak_words': peak, 'memory_log2_bytes': mm, 'score': t + max(0, mm - 20),
               'squarings': inf['n_squarings'], 'mulx': inf['n_mulx'], 'j': inf['j'], 'L': inf['L']}
        print(json.dumps({k: rec[k] for k in ('r', 'top_fraction', 'pow2', 'time_log2', 'memory_log2_bytes', 'score', 'peaks')}), flush=True)
        if best is None or rec['score'] < best['score']:
            best = rec
    return best


def refresh(best):
    """re-price every row except the half-gcd (the cached output of the mock, which depends on m, the fraction and pow2 only)
    with the current charge functions, and recompute W, time and score."""
    r, n, C = best['r'], best['n'], best['C']
    ph, inf = SETUP_POWER(best['m'], (P - 1) // 2)
    power = sum(ph.values(), V())
    rows = {'setup': SETUP(r).s, 'centre_draw': DRAW_CAP * DRAW, 'build': BUILD(n, r).s, 'montgomery': power.s,
            'y_minus_1': 5, 'half_gcd': Fraction(best['rows_exact']['half_gcd']), 'roots_deg16': roots_bound_strict(16),
            'finish': 1 + ts_worst() + 2 + 2 * (3 * ROOT5_COST + 8) + 2 * C + 8}
    W = sum(rows.values(), Fraction(0))
    best = dict(best)
    best['rows'] = {k: float(v) for k, v in rows.items()}; best['rows_exact'] = {k: str(v) for k, v in rows.items()}
    best['W'] = str(W); best['time_log2'] = math.log2(W / C)
    best['score'] = best['time_log2'] + max(0, best['memory_log2_bytes'] - 20)
    return best


if __name__ == '__main__':
    r = int(sys.argv[1])
    fr = tuple(int(x) for x in sys.argv[2:]) or (8, 12, 16, 24)
    b = ledger(r, fr)
    print('BEST', json.dumps(b))
```

### gen_heur.py

```python
"""gen_heur.py <r> <outdir>: the one-centre (not executed) package for round r: proof.md, claim.json, empty certificate manifest.
Ledger from heur.py (strict closed forms, normal-sequence half-gcd schedule from gcd_mock.py); every declared bound checked."""
import json, os, sys, math, glob
from decimal import Decimal, getcontext
from fractions import Fraction
getcontext().prec = 60
from ntt import P, T, T_S, mont_length
from mont import SETUP_POWER, PEAK_WORDS, V
import heur
from attack_mont import BUILD, EVAL, EVAL_ARITH, EVAL_LOADS, LEAD_BOUND, EXP_COST, TS_T, SETUP
from gcd_mock import roots_bound_strict
NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.join(HERE, '..')


def EX(v):
    v = Fraction(str(v)); w = v.numerator // v.denominator; rest = v - w
    return f'{w:,}' if rest == 0 else (f'{w:,}.5' if rest == Fraction(1, 2) else f'{w:,} {rest}')


def ceil5(x):
    return math.ceil(x * 100000 - 1e-9) / 100000




ATTEMPTS = {'r5': (2, '0.30'), 'r6c': (2, '0.30'), 'r7b': (2, '0.30'), 'r9': (2, '0.30')}   # package -> (attempts t, premise fraction q0); default (1, '0.3901')
LAW = 0.39347


def _binom_tail(h, n, q, upper):
    from math import comb
    rng = range(h, n + 1) if upper else range(0, h + 1)
    return sum(comb(n, i) * q ** i * (1 - q) ** (n - i) for i in rng)


def _fig(h, n, q0, q0s):
    """one figure: count, fraction, distance from the law (z for n >= 100, exact binomial tail otherwise), distance from q0"""
    f = h / n
    if n >= 100:
        z = (f - LAW) / (LAW * (1 - LAW) / n) ** 0.5
        zf = (f - q0) / (f * (1 - f) / n) ** 0.5
        flag = 'excess' if z >= 2 else 'deficit' if z <= -2 else ''
        return '%d of %d = %.4f (%+.2f standard errors from the law value, %+.2f from the premise value %s)' % (h, n, f, z, zf, q0s), flag
    up = f >= LAW
    t = _binom_tail(h, n, LAW, up)
    flag = ('excess' if up else 'deficit') if t < 0.023 else ''
    return '%d of %d = %.4f (exact binomial tail %s = %.3f under the law value)' % (h, n, f, ('P(X >= %d)' % h) if up else ('P(X <= %d)' % h), t), flag


def _ks(rep, pred=lambda e: True):
    return [t['untrusted_participant_observations']['k_c'] for e in rep['experiments'] if pred(e)
            for t in e['checked_trials'] if 'k_c' in t['untrusted_participant_observations']]


def _hit(ks):
    return sum(1 for x in ks if 1 <= x <= 16)


def hone_reading(pkg):
    """plain statement of the emulated organizer H-ONE counts, from ledger/exp_report_<pkg>.json"""
    t_att, q0s = ATTEMPTS.get(pkg, (1, '0.3901')); q0 = float(q0s)
    rp = os.path.join(WAVE, 'ledger', f'exp_report_{pkg}.json')
    if not os.path.exists(rp):
        return 'Reading of the organizer experiments: not yet run for this package.'
    rep = json.load(open(rp))
    by = {}
    for e in rep['experiments']:
        L_ = 2 if e['id'].startswith('hone-layers2') else 3
        setn = e['id'].split('-rep')[1] if '-rep' in e['id'] else '1'
        by.setdefault((L_, setn), []).extend(_ks({'experiments': [e]}))
    figs, flags = [], []
    for L_, word in ((2, 'two'), (3, 'three')):
        ks = [x for (l, _), v in by.items() if l == L_ for x in v]
        fs, fl = _fig(_hit(ks), len(ks), q0, q0s)
        figs.append('%s layers combined: %s' % (word, fs))
        if fl:
            flags.append(('the %s-layer combined figure' % word, fl, _hit(ks), len(ks)))
    allk = [x for v in by.values() for x in v]
    H, N = _hit(allk), len(allk)
    fs, fl = _fig(H, N, q0, q0s)
    figs.append('all experiments pooled: ' + fs)
    if fl:
        flags.append(('the pooled figure', fl, H, N))
    sets = []
    for (L_, sn), ks in sorted(by.items()):
        fs_, fl_ = _fig(_hit(ks), len(ks), q0, q0s)
        sets.append('%d layers set %s: %s' % (L_, sn, fs_))
        if fl_:
            flags.append(('%d-layer set %s' % (L_, sn), fl_, _hit(ks), len(ks)))
    txt = ('Reading of the organizer experiments of this package (emulated in the pinned organizer image with the organizer runner and the '
           'public seed protocol; the organizer run reproduces these counts exactly unless it adds a holdout nonce, which draws different '
           'centres): %s. By experiment set: %s.' % ('; '.join(figs), '; '.join(sets)))
    for what, fl, fh, fn in flags:
        if fl == 'excess':
            txt += (' Measured excess: %s lies above the law value by more than two standard errors (or its exact tail is below 0.023); an'
                    ' excess means more centres with 1 <= k(c) <= 16 than the premise needs, so it does not weaken the success bound.' % what)
        else:
            ff = fh / fn
            txt += ' Measured deficit: %s lies below the law value by more than two standard errors (or its exact tail is below 0.023)' % what
            txt += ('; it stays above the premise value %s by %.2f standard errors.' % (q0s, (ff - q0) / (ff * (1 - ff) / fn) ** 0.5)) if ff > q0 else ('; it is below the premise value %s.' % q0s)
    f = H / N
    se = (f * (1 - f) / N) ** 0.5
    zc = 2.326
    lo = (f + zc ** 2 / (2 * N) - zc * ((f * (1 - f) + zc ** 2 / (4 * N)) / N) ** 0.5) / (1 + zc ** 2 / N)
    def wilson(f_, n_):
        return (f_ + zc ** 2 / (2 * n_) - zc * ((f_ * (1 - f_) + zc ** 2 / (4 * n_)) / n_) ** 0.5) / (1 + zc ** 2 / n_)
    sib_all = []
    for sp in ('r5', 'r6c', 'r7b', 'r8', 'r9'):
        rp2 = os.path.join(WAVE, 'ledger', f'exp_report_{sp}.json')
        if sp != pkg and os.path.exists(rp2):
            sib_all += _ks(json.load(open(rp2)))
    na = len(sib_all) + N
    ha = _hit(sib_all) + H
    fa = ha / na
    loa = wilson(fa, na)
    zfa = (fa - q0) / (fa * (1 - fa) / na) ** 0.5
    if lo >= q0 and loa >= q0:
        txt += (' Against the premise value %s: the pooled organizer fraction of this package is above it, and so is its one-sided 99%%'
                ' lower confidence bound (Wilson) %.4f; pooled over all our packages (%d of %d = %.4f, %+.2f standard errors from %s, lower'
                ' bound %.4f) the counts lie above it as well; the organizer-run counts support the premise value at the degrees they test.'
                % (q0s, lo, ha, na, fa, zfa, q0s, loa))
    elif lo >= q0:
        txt += (' Against the premise value %s: the counts of this package lie above it (one-sided 99%% lower confidence bound, Wilson,'
                ' %.4f); pooled over all our packages they do not (%d of %d = %.4f, %+.2f standard errors from %s, lower bound %.4f). The'
                ' organizer-run counts therefore do not establish the premise value; its support rests on the law of Section 6 and on our'
                ' own larger samples (Section 7).' % (q0s, lo, ha, na, fa, zfa, q0s, loa))
    elif f >= q0:
        txt += (' Against the premise value %s: the pooled organizer fraction is above it, but its one-sided 99%% lower confidence bound'
                ' (Wilson) %.4f is below it.' % (q0s, lo))
    else:
        txt += (' Against the premise value %s: the pooled organizer fraction is below it by %.2f standard errors, so the organizer runs'
                ' alone do not establish the premise at this value; the support then rests on the law of Section 6 and on our own larger'
                ' samples (Section 7).' % (q0s, (q0 - f) / se))
    sib, tot, hit_ = [], 0, 0
    for sp in ('r5', 'r6c', 'r7b', 'r8', 'r9'):
        rp2 = os.path.join(WAVE, 'ledger', f'exp_report_{sp}.json')
        if sp == pkg or not os.path.exists(rp2):
            continue
        ks = _ks(json.load(open(rp2)))
        sib.append(sp); tot += len(ks); hit_ += _hit(ks)
    if sib:
        se2 = (LAW * (1 - LAW) / (tot + N)) ** 0.5
        txt += (' Pooled with the emulated experiments of our other packages (%s; the same computation on the same line polynomials at two'
                ' and three layers with the organizer seeds of each target; the program file of r8 differs only in its replicate-id handling):'
                ' %d of %d = %.4f, %+.2f standard errors from the law value.'
                % (', '.join(sib), hit_ + H, tot + N, (hit_ + H) / (tot + N), ((hit_ + H) / (tot + N) - LAW) / se2))
    return txt


def kcline_text(pkg):
    t_att, q0s = ATTEMPTS.get(pkg, (1, '0.3901')); q0 = float(q0s)
    out = []
    for L_ in (2, 3):
        d = json.load(open(os.path.join(WAVE, 'ledger', f'kc_line_L{L_}.json')))
        se = (d['frac'] * (1 - d['frac']) / d['N']) ** 0.5
        out.append('%d layers: %d centres, k = 0, 1, 2, >= 3 in %d, %d, %d, %d; fraction with 1 <= k <= 16 = %.5f (standard error %.4f; %+.2f'
                   ' standard errors from the law value 0.39347, %+.2f from the premise value %s)'
                   % (L_, d['N'], d['k0'], d['k1'], d['k2'], d['k3plus'], d['frac'], se, d['z'], (d['frac'] - q0) / se, q0s))
    d2 = json.load(open(os.path.join(WAVE, 'ledger', 'kc_line_L2.json')))
    txt = '; '.join(out) + '.'
    if d2['z'] >= 2:
        txt += (' The two-layer sample lies above the law value by %.2f standard errors (a measured excess; at m = 12 the finite-degree'
                ' distribution need not equal its Poisson limit); an excess does not weaken the success bound.' % d2['z'])
    rp = os.path.join(WAVE, 'ledger', f'exp_report_{pkg}.json')
    if os.path.exists(rp):
        ks = _ks(json.load(open(rp)), lambda e: e['id'].startswith('hone-layers2'))
        h, n_ = _hit(ks), len(ks)
        f = h / n_
        zd = (f - d2['frac']) / (f * (1 - f) / n_ + d2['frac'] * (1 - d2['frac']) / d2['N']) ** 0.5
        txt += (' The two-layer organizer fraction of this package (%d of %d = %.4f) differs from our two-layer sample by %+.2f standard'
                ' errors of the difference%s.' % (h, n_, f, zd, '; we state the difference as measured' if abs(zd) >= 2 else ''))
    return txt


def main(r, outdir, fractions=(12,)):
    PKG = os.path.basename(os.path.normpath(outdir))
    cache = os.path.join(WAVE, 'ledger', f'heur_r{r}.json')
    if os.path.exists(cache):
        best = json.load(open(cache))
    else:
        best = heur.ledger(r, fractions)
        json.dump(best, open(cache, 'w', newline=NL), indent=1)
    best = heur.refresh(best)   # the mock output (half-gcd row, peaks) is cached; every other row is re-priced now
    D, m, n, C = 5 ** (6 + r), best['m'], best['n'], best['C']
    E = (P - 1) // 2
    phs, inf = SETUP_POWER(m, E)
    power = sum(phs.values(), V())
    b = BUILD(n, r)
    T_ATT, Q0S = ATTEMPTS.get(PKG, (1, '0.3901'))
    W1 = Fraction(best['W'])                              # one attempt, setup included
    W = Fraction(best['rows_exact']['setup']) + T_ATT * (W1 - Fraction(best['rows_exact']['setup']))
    Wi = -(-W.numerator // W.denominator)          # ceiling: the count is charged up to the next integer
    tl = math.log2(Wi) - math.log2(C); tcl = ceil5(tl); T5 = round(tcl * 100000)
    assert Wi ** 100000 <= (1 << T5) * C ** 100000
    mem = best['peak_words'] * 32 + (1 << 20); mcl = ceil5(math.log2(mem)); M5 = round(mcl * 100000)
    assert mem ** 100000 <= 1 << M5
    pa = Decimal(Q0S) - Decimal(2) ** -64 - Decimal(n * (D - 1)) / Decimal(P) - 31 * (Decimal('0.5') + Decimal(2) ** -124) ** 64
    pb = 1 - (1 - pa) ** T_ATT
    pcl = float((pb * 100000).to_integral_value(rounding="ROUND_FLOOR") / 100000)
    assert Decimal(str(pcl)) <= pb and pcl >= 0.39
    score = tcl + max(0, mcl - 20)
    rows = best['rows_exact']
    names = {'setup': 'setup (line constants, transform constants, leading coefficient, Tonelli-Shanks constant, output bound; 3.4)',
             'centre_draw': 'centre draw: 64 x 4 (3.5)', 'build': 'values of g_c on O1: 2n line evaluations + point generators (3.2)',
             'montgomery': 'Montgomery stage: interpolation, start residue, batch inversion, tables, %d squarings, finish (3.3)' % inf['n_squarings'],
             'y_minus_1': 'Y - 1 (3.4)', 'half_gcd': 'half-gcd, normal schedule, top-level n0/%d%s, strict (Section 5)' % (best['top_fraction'], ', 2^k wrapped lengths allowed' if best['pow2'] else ''),
             'roots_deg16': 'root stage, deg G <= 16, 64 draws per call (3.5)', 'finish': 'finish: Tonelli-Shanks worst case, line points, inputs, two hashes, comparison (3.5)'}
    ledger = '| row | units |' + NL + '|---|---:|' + NL + NL.join(f'| {names[k]} | {EX(v)} |' for k, v in rows.items()) + NL + (f'| second attempt (every row above except the setup, at its cap) | {EX(W - W1)} |' + NL if T_ATT == 2 else '') + f'| **total W** | **{EX(W)}** |'
    # k(c) statistics
    kc = []
    for fn in sorted(glob.glob(os.path.join(WAVE, 'ledger', 'kc_stats_r*_k0.jsonl'))):
        rs = [json.loads(l) for l in open(fn)]
        if not rs:
            continue
        from collections import Counter
        cnt = Counter(min(x['k_c'], 3) for x in rs)
        rr = rs[0]['r']; tot = len(rs)
        kc.append(f'  r = {rr}, centres 1..{tot}: k = 0, 1, 2, >= 3 in {cnt[0]}, {cnt[1]}, {cnt[2]}, {cnt[3]}; fraction with 1 <= k <= 16: {sum(1 for x in rs if 1 <= x["k_c"] <= 16) / tot:.4f}')
    ex = ['r = 1: centre c = 1 gave deg G = 1 (collision certified)', 'r = 2: centre c = 1 gave deg G = 1 (collision certified)']
    r3 = os.path.join(WAVE, 'runs', 'r3s', 'ledger_r3.json')
    if os.path.exists(r3):
        L3 = json.load(open(r3))
        ex.append('r = 3: ' + '; '.join(f"c = {t['centre']}: deg G = {t['deg_G']}" for t in L3['trials']) + ' (certified)')
    sub = {'R': r, 'LASTP': 3 + r, 'C': C, 'D': f'{D:,}', 'M': f'{m:,}', 'N': f'{n:,}', 'NSQ': inf['n_squarings'], 'NMX': inf['n_mulx'],
           'FRAC': best['top_fraction'], 'J': inf['j'], 'A': f'{1 << inf["j"]:,}', 'L': f'{inf["L"]:,}', 'TN': EX(T_S(n)), 'TNL': EX(T(n)),
           'EVALA': EVAL_ARITH(r), 'EVALL': EVAL_LOADS(r), 'EVAL': EX(EVAL(r).s), 'RPART': f'{r} partial rounds',
           'BUILD': EX(b.s), 'BUILDL': EX(b.l), 'PH_G': EX(phs['g_values'].s), 'PH_S': EX(phs['start_residue'].s), 'PH_B': EX(phs['batch_inverse'].s),
           'PH_T': EX(phs['tables'].s), 'STEP': EX(inf['step_plain'].s), 'STEPL': EX(inf['step_plain'].l), 'STEPX': EX(inf['step_mulx'].s),
           'PH_P': EX(phs['powering'].s), 'PH_F': EX(phs['finish'].s), 'POWER': EX(power.s), 'POWERL': EX(power.l), 'PEAKPOW': f'{PEAK_WORDS(m):,}',
           'LEADB': f'{LEAD_BOUND(r):,}', 'TSC': f'{EXP_COST(TS_T):,}', 'SETUP': EX(SETUP(r).s), 'ROOTB': EX(roots_bound_strict(16)),
           'FINB': EX(Fraction(rows['finish'])), 'LEDGER': ledger, 'W': EX(W), 'TLOG2': f'{tl:.6f}', 'TCLAIM': f'{tcl:.5f}', 'T5': str(T5),
           'PK_BUILD': f"{best['peaks']['build']:,}", 'PK_POWER': f"{best['peaks']['montgomery']:,}", 'PK_GCD': f"{best['peaks']['half_gcd']:,}",
           'PEAK': f"{best['peak_words']:,}", 'MEMBYTES': f'{mem:,}', 'MEMLOG2': f'{math.log2(mem):.6f}', 'MCLAIM': f'{mcl:.5f}',
           'HONEPRE': (open(os.path.join(WAVE, 'ledger', f'hone_prerun_{PKG}.txt'), encoding='utf-8').read().strip() if os.path.exists(os.path.join(WAVE, 'ledger', f'hone_prerun_{PKG}.txt')) else 'not yet run for this package'),
           'HONEREADING': hone_reading(PKG),
           'KCLINE': kcline_text(PKG),
           'NORMALPRE': (open(os.path.join(WAVE, 'ledger', f'normal_prerun_{PKG}.txt'), encoding='utf-8').read().strip() if os.path.exists(os.path.join(WAVE, 'ledger', f'normal_prerun_{PKG}.txt')) else 'not yet run for this package'),
           'SCORE': f'{score:.5f}', 'PCLAIM': f'{pcl:.5f}', 'PBOUND': str(pb)[:22], 'PATT': str(pa)[:22], 'Q0': Q0S,
           'JBPREFIX': ('This is the premise of' if T_ATT == 1 else 'Our premise is a weaker form (' + Q0S + ' instead of 0.3901) of the premise of'),
           'ATTHEAD': ('one centre' if T_ATT == 1 else 'up to two centres'),
           'MARGINTXT': ('they cannot resolve the 0.86% margin of the premise to the law.' if T_ATT == 1 else 'they lie far above the premise value ' + Q0S + ' but test degrees 12 and 62 only.'),
           'ATTTITLE': ('one random centre' if T_ATT == 1 else 'up to two random centres'),
           'ATTCLAIM': ('' if T_ATT == 1 else ' It makes at most two such attempts, each with a fresh centre, and stops at the first success; the count W charges both attempts at their caps (the setup once).'),
           'ATTALG': ('' if T_ATT == 1 else NL + '7. If the attempt failed and it was the first, return to step 1 with a fresh centre (the setup is kept); after the second attempt, stop.' + NL),
           'ATTBOUND': ('  P(success) >= ' + Q0S + ' - 2^-64 - n (D - 1) / p - 31 (1/2 + 2^-124)^64 = ' + str(pb)[:22] if T_ATT == 1 else
                        '  P(one attempt succeeds) >= ' + Q0S + ' - 2^-64 - n (D - 1) / p - 31 (1/2 + 2^-124)^64 = ' + str(pa)[:22] + ', and the two attempts use' + NL +
                        '  independent fresh random words, so P(success) >= 1 - (1 - ' + str(pa)[:22] + ')^2 = ' + str(pb)[:22]),
           'Q0WHY': ('H-ONE asks for 0.3901, 0.86% below that value.' if T_ATT == 1 else
                     'H-ONE asks for ' + Q0S + ', well below that value. The two-attempt design and the value ' + Q0S + ' were fixed after we had seen the organizer-run counts of Section 7 (this and our other packages); those counts are therefore not an independent test of this value. ' + Q0S + ' is a round value below the one-sided 99% Wilson lower bound of each of our packages that use it (r5 0.332, r6c 0.330, r7b 0.391; r8, a one-attempt package at 0.3901, 0.304) and of the four pooled (0.364); the law (0.39347) and our own FLINT samples (Section 7) do not depend on that choice. A holdout rerun of the declared experiments would test it afresh.'), 'KCSTATS': NL.join(kc), 'EXECRUNS': '; '.join(ex)}
    parts = sorted(glob.glob(os.path.join(HERE, 'heur_parts', '*.md')))
    text = NL.join(open(p, encoding='utf-8').read() for p in parts)
    for k, v in sub.items():
        text = text.replace(f'@@{k}@@', str(v))
    left = sorted(set(text.split('@@')[1::2]))
    assert not left, left
    lines = text.split(NL)

    def sec(title):
        i = next(j for j, l in enumerate(lines) if l.startswith(title)) + 1
        k = next((j for j in range(i, len(lines)) if lines[j].startswith('## ')), len(lines))
        k = min(k, len(lines) - (1 if lines and lines[-1] == '' else 0))
        return f'proof:{i}-{k}'
    APP = ['heur.py', 'gen_heur.py', 'attack_mont.py', 'attack_v4_ref.py', 'ntt.py', 'mont.py', 'halfgcd.py', 'halfgcd_charge.py', 'gcd_mock.py', 'gcd_stage.py', 'roots.py', 'kc_stats.py', 'mk_hone_exp.py', 'hone_layers_src.py', 'hone_flint_check.py', 'kc_line_sample.py']
    app = ['', '## Appendix A. Program listings', '',
           'Standard library plus python-flint for the self-tests. `python heur.py ' + str(r) + ' 12` prints the ledger of Section 4;',
           '`python ntt.py` and `python mont.py` run the kernel self-tests; `python gcd_mock.py --selftest`, `--selftest-pow2` and `--selftest-degG` run the validation of',
           'Section 5; `attack_v4_ref.py` provides the line (`Target`, with k = 0 here) and its `run` is not used.', '']
    for fn in APP:
        app += [f'### {fn}', '', '```python', open(os.path.join(HERE, fn), encoding='utf-8').read().rstrip(), '```', '']
    app += ['## Appendix B. Logs', '']
    for fn, title in (('gcd_mock_selftest.txt', 'gcd_mock.py --selftest (mock against executed runs, default configuration)'),
                      ('gcd_mock_selftest_pow2.txt', 'gcd_mock.py --selftest-pow2 (mock against executed runs, the charged configuration: n0/12, 2^k wrapped lengths)'),
                      ('gcd_mock_selftest_degG.txt', 'gcd_mock.py --selftest-degG (charged configuration; instances with deg G from 3 to 9)'),
                      ('gcd_mock_memo_check.txt', 'memoized mock against plain mock'),
                      ('kc_line_L2.json', 'python kc_line_sample.py 2 100000 poseidon_mage_kcline_L2'),
                      ('kc_line_L3.json', 'python kc_line_sample.py 3 20000 poseidon_mage_kcline_L3'),
                      (f'hone_flint_check_{PKG}.txt', f'hone_flint_check.py {PKG} (FLINT recomputation of every computed trial of the emulated experiments)')):
        p_ = os.path.join(WAVE, 'ledger', fn)
        if os.path.exists(p_):
            app += [f'`{title}`:', '', '```', open(p_, encoding='utf-8').read().rstrip(), '```', '']
    for fn in sorted(glob.glob(os.path.join(WAVE, 'ledger', 'kc_stats_r*_k0.jsonl'))):
        app += [f'`{os.path.basename(fn)}`:', '', '```', open(fn, encoding='utf-8').read().rstrip(), '```', '']
    text = text + NL.join(app)
    lines[:] = text.split(NL)
    claim = {"schema_version": 3, "submission_state": "ready", "target_profile": f"poseidon-orchard-r{r}-prefix-v1",
             "attack_class": "ordinary-collision", "rounds": r,
             "claim": {"time_log2": tcl, "time_unit": "target-compressions", "memory_log2_bytes": mcl, "preprocessing_log2": 0,
                       "success_probability": pcl, "nonuniform_advice_log2_bytes": 0},
             "restrictions": [], "baseline_improved": f"poseidon-orchard-r{r}-nominal-v2",
             "certificate_manifest": "certificates/manifest.json", "lane": "exploratory",
             "heuristics": [
                 {"id": "H-ONE", "statement": "The number of centres c in F_p with 1 <= k(c) <= 16 is at least " + Q0S + " p, where k(c) is the number of nonzero squares S with g_c(S) = 0 (the degree of gcd(g_c, S^((p-1)/2) - 1)), for the line of proof Section 1 at this round count.",
                  "role": "score-critical", "scope": f"poseidon-orchard-r{r}-prefix-v1, the line of proof Section 1 (lane 0 constant at the round-1 S-box input), centres uniform on F_p.",
                  "extrapolation": "From the hyperoctahedral Poisson(1/2) law (P(k >= 1) = 0.39347) and from k(c) counts at small degree on this line to degree m of this round count.",
                  "evidence_ids": [sec('## 6.'), sec('## 7.')],
                  "limitations": "Not proved at this degree; false for permutation polynomials and decomposable F with imprimitive monodromy; " + ("the small-degree counts cannot resolve the 0.86% margin." if T_ATT == 1 else "the small-degree counts test degrees 12 and 62 only.") + ""},
                 {"id": "H-NORMAL", "statement": "The remainder sequence of (g_c, Y - 1) is normal down to deg G, so the half-gcd executes at most the schedule charged in proof Section 5; the time bound is conditional on it.",
                  "role": "score-critical", "scope": "The cost of the gcd stage of this package.",
                  "extrapolation": "From the normal-sequence observations of the organizer experiments on this line at two and three S-box layers (degrees 12 and 62), the mock-versus-executed validation at degrees up to 39062 (including instances with deg G from 3 to 9) and the executed r = 1, 2, 3 runs to degree m.",
                  "evidence_ids": [sec('## 5.'), sec('## Appendix B.')], "limitations": "On a non-normal sequence the gcd is still correct but its cost differs from the charged schedule."},
                 {"id": "H2-cost-convention", "statement": "Prices of proof Section 3.0: field operations 1, loads and stores 2 (access and address), loops 3 per iteration (unrolled by 8 where streaming) plus 2 per exit, a declared 16-word register file, and a 1 MiB allowance for code, constants, registers and stack.",
                  "role": "supporting", "scope": "The time and memory claims of this package.", "extrapolation": "None; a declared convention.",
                  "evidence_ids": [sec('## 3.'), sec('## 4.')], "limitations": "The contract fixes no register count or code-size rule; the allowance is a declared bound, not a measured binary."}]}
    import subprocess
    os.makedirs(os.path.join(outdir, 'experiments'), exist_ok=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'mk_hone_exp.py'), os.path.join(outdir, 'experiments', 'hone_layers.py')], check=True)
    ev = {'kind': 'digest-xor-mask', 'mask_hex': '01' + '00' * 31, 'expected_hex': '00' * 32}
    EXPS = []
    for part, res in zip('abc', ('0', '1', '2')):
        EXPS.append({'id': 'hone-layers2' + part, 'kind': 'python-message-pairs-v1',
                     'scope': 'The line of proof Section 1 with two S-box layers after it (rounds 2 and 3 of the target permutation; degree 25, m = 12); one uniform centre for each organizer seed of trial index ' + res + ' mod 3 (the other trials are reported as skipped; parts a, b, c together cover every trial).',
                     'hypothesis': 'Premise H-ONE at two layers: the fraction of centres with 1 <= k(c) <= 16 is close to the hyperoctahedral value 0.39347; premise H-NORMAL at two layers: the remainder sequence of (g_c, Y - 1) is normal (observation normal = 1). Both are reported per trial as observations; no message pair is returned, so the organizer success count is 0 by design.',
                     'program': 'experiments/hone_layers.py', 'event': ev})
    for part, lo in zip('abc', (0, 6, 12)):
        EXPS.append({'id': 'hone-layers3' + part, 'kind': 'python-message-pairs-v1',
                     'scope': 'The same line with three S-box layers (rounds 2, 3 and partial round 4; degree 125, m = 62); one uniform centre for each organizer seed of trial index %d to %d (the rest reported as skipped, for the time limit).' % (lo, lo + 5),
                     'hypothesis': 'Premises H-ONE and H-NORMAL at three layers, as above; k(c) and normal are observations; no message pair is returned.',
                     'program': 'experiments/hone_layers.py', 'event': ev})
    base = list(EXPS)
    for e, k in [(e, k) for k in (2, 3, 4) for e in base if e['id'].startswith('hone-layers2')] + [(base[3], 2)]:
        rep = dict(e); rep['id'] = e['id'] + '-rep%d' % k
        rep['scope'] = 'Pre-declared replicate %d of ' % k + e['id'] + ': the same program and computation on the fresh organizer seeds of this id. ' + e['scope']
        EXPS.append(rep)
    assert len(EXPS) == 16
    man = {'schema_version': 1, 'experiments': EXPS}
    json.dump(man, open(os.path.join(outdir, 'experiments', 'manifest.json'), 'w', newline=NL), indent=1)
    claim['experiment_manifest'] = 'experiments/manifest.json'
    claim['heuristics'][0]['evidence_ids'] += ['experiment:' + e['id'] for e in EXPS]
    claim['heuristics'][1]['evidence_ids'] += ['experiment:' + e['id'] for e in EXPS]
    os.makedirs(os.path.join(outdir, 'certificates'), exist_ok=True)
    open(os.path.join(outdir, 'proof.md'), 'w', encoding='utf-8', newline=NL).write(text)
    json.dump(claim, open(os.path.join(outdir, 'claim.json'), 'w', newline=NL), indent=2)
    json.dump({'schema_version': 2, 'certificates': []}, open(os.path.join(outdir, 'certificates', 'manifest.json'), 'w', newline=NL), indent=1)
    print(json.dumps({'r': r, 'time_log2': tcl, 'memory_log2_bytes': mcl, 'score': score, 'success': pcl, 'fraction': best['top_fraction'],
                      'pow2': best['pow2'], 'proof_bytes': len(text.encode())}))


if __name__ == '__main__':
    if os.path.exists(os.path.join(WAVE, 'PAUSE')):
        sys.exit('paused: remove WAVE/PAUSE to resume')
    main(int(sys.argv[1]), sys.argv[2])
```

### attack_mont.py

```python
"""attack_mont.py - counted, executed collision search on the reduced Orchard hash (r partial rounds).

Procedure (fixed before the first execution; centres c_i = i, i = 1, 2, 3, ..., every trial charged):
  line   two-round bypass (Bariant-Bouvier-Leurent-Perrin 2022): F(T') = lane-0 digest along the line,
         degree D = 5^(6+r) in the round-1 S-box output parameter T' (Target in attack_v4_ref.py).
  build  g_c(S) monic of degree m = (D-1)/2 with F(c+s) - F(c-s) = 2 a_D s g_c(s^2): its values on
         O1 = H_n (n = the least 3*2^k or 2^k > m) in transform order, from 2n line evaluations F(c +- s_t),
         s_t = psi^e(t) (psi a primitive 2n-th root), G1[t] = (F(c+s_t) - F(c-s_t)) / (2 a_D s_t).
  power  Y = S^((p-1)/2) mod g_c by value-domain Montgomery squaring on O1, O2 = psi H_n (mont.py).
  gcd    G = gcd(g_c, Y - 1) by the counted half-gcd (halfgcd.py, gcd_stage.py); roots of G (roots.py).
  finish for each root S: s = sqrt(S) (Tonelli-Shanks, counted), W1 = c + s, W2 = c - s, inputs of
         both by the line's inverse map, two reference hashes, digest comparison.
Usage: python attack_mont.py <constants.json> <r> <outdir> [--max-trials N] [--top-fraction F (default 12)]
"""
import json, sys, os, math, time
from fractions import Fraction
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
from ntt import P, T, Counter, root_of_unity, nice_length, log2_k, mont_length
import mont
from mont import point_stream, PG, PEAK_WORDS, SETUP_POWER
from attack_v4_ref import Target, E5, EXP_COST, ROOT5_COST

CODE_BYTES = 1 << 20
E = (P - 1) // 2
TS_S = 32
TS_T = (P - 1) >> 32
NONRES = 5                                   # quadratic non-residue mod p (checked)
INV = 380


def eval_line(t, Tp):
    """lane-0 digest at line parameter T' (rounds 2.. of the reduced permutation from the affine
    round-1 output). Charged EVAL(r) = 6 + 27*6 + 21*r + 1 per call."""
    M, RC = t.M, t.RC
    sb = [(t.sb_lin[c] * Tp + t.sb_const[c]) % P for c in range(3)]
    s = [sum(M[row][c] * sb[c] for c in range(3)) % P for row in range(3)]
    for i in [2, 3, *range(4, 4 + t.r), *range(60, 64)]:
        s = [(x + c) % P for x, c in zip(s, RC[i])]
        for col in (range(3) if i < 4 or i >= 60 else range(1)):
            s[col] = pow(s[col], 5, P)
        s = [sum(M[row][c] * s[c] for c in range(3)) % P for row in range(3)]
    return s[0]


def EVAL_ARITH(r):
    """field operations of one line evaluation: affine state after round 1 (3 mul + 3 add), six full rounds
    (3 constant additions, 3 x 3 multiplications for x^5, MDS 9 mul + 6 add = 27), r partial rounds (21)."""
    return 6 + 27 * 6 + 21 * r


def EVAL_LOADS(r):
    """constant loads of one line evaluation: the 6 affine coefficients, then per remaining round 3 round
    constants and 9 MDS entries (the state stays in registers)."""
    return 6 + 12 * (6 + r)


def EVAL(r):
    from mont import OPS
    return OPS(arith=EVAL_ARITH(r), load=EVAL_LOADS(r))


def lead_coefficient(t):
    """leading coefficient a_D of F(T') by tracking (degree, leading coefficient) of each lane."""
    M, RC = t.M, t.RC
    lanes = [(1, t.sb_lin[c]) if t.sb_lin[c] else (0, t.sb_const[c]) for c in range(3)]

    def mds(l):
        out = []
        for row in range(3):
            d = max(x[0] for x in l)
            lc = sum(M[row][c] * l[c][1] for c in range(3) if l[c][0] == d) % P
            assert lc, 'leading cancellation'
            out.append((d, lc))
        return out
    lanes = mds(lanes)
    for i in [2, 3, *range(4, 4 + t.r), *range(60, 64)]:
        for col in (range(3) if i < 4 or i >= 60 else range(1)):
            d, lc = lanes[col]
            lanes[col] = (5 * d, pow(lc, 5, P)) if d else (0, pow((lc + RC[i][col]) % P, 5, P))
        lanes = mds(lanes)
    assert lanes[0][0] == 5 ** (6 + t.r)
    return lanes[0][1]


def LEAD_BOUND(r):
    return 24 * (8 + r) + INV + 1


def build_G1(t, c, n, aD, ctr):
    """values of monic g_c on O1 in transform order (counted; evaluations charged EVAL each)."""
    psi = root_of_unity(2 * n)
    z0 = pow(2 * aD % P, P - 2, P)
    sp = point_stream(n, psi, 1, ctr)
    zp = point_stream(n, pow(psi, P - 2, P), z0, ctr)
    G1 = [0] * n
    for i in range(n):
        s = next(sp)
        z = next(zp)
        fp = eval_line(t, (c + s) % P)
        fm = eval_line(t, (c - s) % P)
        G1[i] = (fp - fm) * z % P
    ctr.add(add=n, sub=2 * n, mul=n, store=n, ctl=3 * n + 2)    # c +- s, difference, product, store; loop
    ctr.add(mul=2 * n * EVAL_ARITH(t.r), load=2 * n * EVAL_LOADS(t.r))   # the 2n line evaluations
    return G1


def BUILD(n, r):
    from mont import OPS
    return 2 * PG(n) + OPS(arith=4 * n, store=n, ctl=3 * n + 2) + (2 * n) * EVAL(r)


def sqrt_counted(a, ctr):
    """Tonelli-Shanks for p - 1 = 2^32 t; z = NONRES^t is a setup constant. Every multiplication,
    comparison and loop iteration counted."""
    z = pow(NONRES, TS_T, P)
    w = pow(a, (TS_T - 1) // 2, P)
    ctr.add(mul=EXP_COST((TS_T - 1) // 2))
    x = a * w % P
    b = x * w % P
    ctr.add(mul=2)
    Mv, cz = TS_S, z
    while True:
        ctr.add(ctl=1)                                   # compare b == 1
        if b == 1:
            break
        i, bb = 0, b
        while bb != 1:
            bb = bb * bb % P
            i += 1
            ctr.add(mul=1, ctl=4)                       # square, compare, counter, branch
        cc = cz
        for _ in range(Mv - i - 1):
            cc = cc * cc % P
            ctr.add(mul=1, ctl=3)
        x = x * cc % P
        cz = cc * cc % P
        b = b * cz % P
        Mv = i
        ctr.add(mul=3, ctl=3)
    assert x * x % P == a
    return x


def SETUP(r):
    """setup charge in both conventions: Lemma 1 constants (2,000 loose, doubled strict), transform constants
    (roots of unity of orders 3*2^i and 2^i, i <= 31 (psi of order 2n among them), their inverses and 1/N per length used: fewer than 440 constants of at
    most 400 units (the largest ladder among these exponents is 400 squarings plus multiplications), 176,000 plus, strict, an address operation for each of their at most 440 stores), the leading-coefficient
    recursion with the inversion of 2 a_D, the Tonelli-Shanks constant, and the output bound (10,000 loose,
    doubled strict)."""
    from mont import V
    base = LEAD_BOUND(r) + EXP_COST(TS_T)
    return V(2000 + 176000 + base + 10000, 4000 + 176000 + 440 + base + 20000)


def run(cpath, r, outdir, max_trials=64, top_fraction=12, cutoff=48):
    from mont import V, ctrV, PHASES
    t = Target(cpath, r)
    D = 5 ** (6 + r); m = (D - 1) // 2; n = mont_length(m + 1); C = t.Cnorm
    assert pow(NONRES, (P - 1) // 2, P) == P - 1
    aD = lead_coefficient(t)
    for Tp in (3, 5, 77):
        assert eval_line(t, Tp) == t.H(*t.inputs(Tp))
    S = SETUP(r)
    L = {'method': 'odd-part line + value-domain Montgomery powering', 'r': r, 'D': D, 'm': m, 'n': n, 'C': C,
         'centres': 'c_i = i, i = 1, 2, ...', 'gcd_params': {'cutoff': cutoff, 'top_fraction': top_fraction},
         'setup': {'loose': S.l, 'strict': S.s}, 'trials': []}
    pctx = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)); X = pctx.gen()
    from gcd_stage import gcd_stage
    from halfgcd_charge import gcd_overhead, charge_strict
    os.makedirs(outdir, exist_ok=True)
    result = None
    for i in range(1, max_trials + 1):
        c = i
        tr = {'trial': i, 'centre': c}
        t0 = time.time()
        cb = Counter()
        G1 = build_G1(t, c, n, aD, cb)
        assert ctrV(cb) == BUILD(n, r), (ctrV(cb), BUILD(n, r))
        tr['build'] = {'loose': cb.total(), 'strict': cb.strict(), 'counters': dict(cb.c), 'lp': cb.lps}
        tr['t_build_s'] = round(time.time() - t0, 1)
        print(f'trial {i}: build {tr["t_build_s"]}s', flush=True)
        t0 = time.time()
        cp = Counter()
        Y, gc, info = mont.setup_and_power(G1, m, E, cp)
        tr['t_power_s'] = round(time.time() - t0, 1)
        phs, inf = SETUP_POWER(m, E)
        mk = info['marks']; prev = mk['start']; tr['power_phases'] = {}
        for nm in PHASES:
            got = V(mk[nm][0] - prev[0], mk[nm][1] - prev[1])
            assert got == phs[nm], (nm, got, phs[nm])
            tr['power_phases'][nm] = {'loose': got.l, 'strict': got.s}; prev = mk[nm]
        tr['power'] = {'loose': cp.total(), 'strict': cp.strict(), 'counters': dict(cp.c), 'lp': cp.lps}
        tr['power_info'] = {k: v for k, v in info.items() if k != 'marks'}
        g = pctx(gc); Yp = pctx(Y)
        assert Yp == X.pow_mod(E, g), 'powering disagrees with FLINT'
        for s in (11, 12345):
            lhs = (t.H(*t.inputs((c + s) % P)) - t.H(*t.inputs((c - s) % P))) % P
            assert lhs == 2 * aD * s % P * int(g(s * s % P)) % P
        print(f'trial {i}: power {tr["t_power_s"]}s loose {float(cp.total()):.4g} strict {float(cp.strict()):.4g}', flush=True)
        t0 = time.time()
        Gg, roots, led = gcd_stage(g, Yp - 1, r, cutoff=cutoff, top_fraction=top_fraction)
        tr['t_gcd_s'] = round(time.time() - t0, 1)
        trace = led.get('trace') or {}
        json.dump(trace, open(os.path.join(outdir, f'gcd_trace_r{r}_t{i}.json'), 'w', newline=chr(10)), separators=(',', ':'))
        tr['gcd'] = {'loose': led['ops'] + gcd_overhead(trace), 'loose_ops': led['ops'], 'loose_overhead': gcd_overhead(trace),
                     'strict': charge_strict(trace), 'peak_words': led['peak_words'],
                     'detail': {k: v for k, v in led.items() if k != 'trace'}}
        tr['small'] = {'loose': 3, 'strict': 6}      # centre (1); Y - 1: load, sub, store (2 loose, 5 strict)
        tr['deg_G'] = Gg.degree(); tr['roots_S'] = [str(x) for x in roots]
        print(f'trial {i}: gcd {tr["t_gcd_s"]}s deg G = {Gg.degree()} loose {float(tr["gcd"]["loose"]):.4g} '
              f'strict {float(tr["gcd"]["strict"]):.4g} peak {led["peak_words"]}', flush=True)
        pairs = []
        cf = Counter()
        if Gg.degree() >= 1:
            for S_ in roots:
                S_ = int(S_)
                cf.add(ctl=1)                                       # test S != 0
                if S_ == 0:
                    continue
                s = sqrt_counted(S_, cf)
                W1, W2 = (c + s) % P, (c - s) % P
                cf.add(add=1, sub=1)
                a = t.inputs(W1); b = t.inputs(W2)
                cf.add(mul=2 * (3 * ROOT5_COST + 8))                # inputs of both sides (3 fifth roots + affine)
                ya, yb = t.H(*a), t.H(*b)
                cf.add(mul=2 * C, ctl=8)                            # two reference hashes (units), digest comparison
                assert a != b and ya == yb
                pairs.append({'S': str(S_), 's': str(s), 'W1': str(W1), 'W2': str(W2),
                              'a': [str(x) for x in a], 'b': [str(x) for x in b], 'digest': ya.to_bytes(32, 'little').hex()})
        tr['finish'] = {'loose': cf.total(), 'strict': cf.strict()}
        for conv in ('loose', 'strict'):
            tr['total_' + conv] = sum(tr[k][conv] for k in ('small', 'build', 'power', 'gcd', 'finish'))
        tr['pairs'] = pairs
        L['trials'].append(tr)
        if pairs:
            result = tr
            break
    assert result, 'no trial succeeded within the cap'
    L['memory_words'] = {'build': n + 64, 'power': PEAK_WORDS(m), 'gcd': max(x['gcd']['peak_words'] for x in L['trials'])}
    L['peak_words'] = max(L['memory_words'].values())
    L['memory_bytes'] = L['peak_words'] * 32 + CODE_BYTES
    L['memory_log2_bytes'] = math.log2(L['memory_bytes'])
    for conv in ('loose', 'strict'):
        W = L['setup'][conv] + sum(x['total_' + conv] for x in L['trials'])
        L['total_' + conv] = W
        L['time_log2_' + conv] = math.log2(W / C)
        L['score_' + conv] = L['time_log2_' + conv] + max(0, L['memory_log2_bytes'] - 20)
    L['claim_convention'] = 'strict'
    L['lead_aD'] = str(aD)

    def jd(o):
        if isinstance(o, Fraction):
            return int(o) if o.denominator == 1 else str(o)
        raise TypeError(type(o))
    json.dump(L, open(os.path.join(outdir, f'ledger_r{r}.json'), 'w', newline=chr(10)), indent=1, default=jd)
    cdir = os.path.join(outdir, 'package', 'certificates'); os.makedirs(cdir, exist_ok=True)
    enc = lambda u, v: int(u).to_bytes(32, 'little') + int(v).to_bytes(32, 'little')
    certs = []
    for k, pr in enumerate(result['pairs']):
        sa, sb = ('message-a.bin', 'message-b.bin') if k == 0 else (f'message-a{k}.bin', f'message-b{k}.bin')
        open(os.path.join(cdir, sa), 'wb').write(enc(*pr['a']))
        open(os.path.join(cdir, sb), 'wb').write(enc(*pr['b']))
        certs.append({'id': f'orchard-r{r}-pair-{k}', 'type': 'hash-collision-witness-v2', 'message_a': f'certificates/{sa}',
                      'message_b': f'certificates/{sb}', 'expected_digest': pr['digest'], 'target_profile': f'poseidon-orchard-r{r}-prefix-v1'})
    json.dump({'schema_version': 2, 'certificates': certs}, open(os.path.join(cdir, 'manifest.json'), 'w', newline=chr(10)), indent=1)
    print(json.dumps({k: (float(v) if isinstance(v, Fraction) else v) for k, v in L.items() if k in
                      ('total_loose', 'total_strict', 'time_log2_loose', 'time_log2_strict', 'peak_words', 'memory_words',
                       'memory_log2_bytes', 'score_loose', 'score_strict')}, indent=1))
    return L


if __name__ == '__main__':
    a = sys.argv
    mt = int(a[a.index('--max-trials') + 1]) if '--max-trials' in a else 64
    fr = int(a[a.index('--top-fraction') + 1]) if '--top-fraction' in a else 12
    run(a[1], int(a[2]), a[3], mt, fr)
```

### attack_v4_ref.py

```python
"""poseidon_mage counted attack driver. Charges follow proof sections 4 and 5.
Executes the two-round-bypass univariate collision search at r partial rounds, charges every
phase as stated in the proof, writes ledger_r<r>.json and a candidate package directory.
Usage: python attack.py <constants.json> <r> <outdir> [--max-trials N]
"""
import json, sys, hashlib, math, os, time
from fractions import Fraction
def _jd(o):
    if isinstance(o, Fraction): return int(o) if o.denominator == 1 else float(o)
    raise TypeError(str(type(o)))
def JI(x):
    return int(x) if (isinstance(x, Fraction) and x.denominator == 1) or isinstance(x, int) else x
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
CODE_BYTES = 1 << 20
E5 = pow(5, -1, P - 1)                       # fifth-root exponent
EXP_COST = lambda e: (e.bit_length() - 1) + (bin(e).count('1') - 1)   # sq + mul of a binary ladder
INV_COST = EXP_COST(P - 2)                   # 330: 254 squarings + 76 multiplications
ROOT5_COST = EXP_COST(E5)

def n3(x):
    """smallest 3*2^k >= x"""
    k = 0
    while 3 << k < x: k += 1
    return 3 << k
from ntt import T                              # transform charge, validated in ntt.py

class Target:
    def __init__(self, cpath, r, k=2):
        C = json.load(open(cpath)); self.r = r; self.k = k
        self.RC = [[int(x, 16) for x in row] for row in C['round_constants']]
        self.M = [[int(x, 16) for x in row] for row in C['mds']]
        self.CAP = 1 << 65; self.Cnorm = 216 + 21 * r
        self.idx = [*range(4), *range(4, 4 + r), *range(60, 64)]
        self.ctx = fmpz_mod_ctx(P); self.pctx = fmpz_mod_poly_ctx(self.ctx)
        self._line()
    def perm(self, s):
        s = list(s); M, RC = self.M, self.RC
        for i in self.idx:
            s = [(x + c) % P for x, c in zip(s, RC[i])]
            for col in (range(3) if i < 4 or i >= 60 else range(1)): s[col] = pow(s[col], 5, P)
            s = [sum(c * x for c, x in zip(row, s)) % P for row in M]
        return s
    def H(self, x0, x1): return self.perm((x0, x1, self.CAP))[0]
    def _line(self):
        M, RC, k = self.M, self.RC, self.k; inv = lambda x: pow(x, P - 2, P)
        K5 = pow((self.CAP + RC[0][2]) % P, 5, P); self.K5 = K5
        i, j = [t for t in range(3) if t != k]
        lam5 = 1; mu5 = (-M[k][0] * inv(M[k][1])) % P
        a, b, e = M[i][0], M[i][1], (-(M[i][2] * K5 + RC[1][i])) % P
        c, d, f = M[j][0], M[j][1], (-(M[j][2] * K5 + RC[1][j])) % P
        det = (a * d - b * c) % P; di = inv(det)
        A0 = ((e * d - b * f) * di) % P; B0 = ((a * f - e * c) * di) % P
        self.lam5, self.mu5, self.A0, self.B0 = lam5, mu5, A0, B0
        self.slope = [(M[t][0] * lam5 + M[t][1] * mu5) % P for t in range(3)]
        self.constk = (M[k][0] * A0 + M[k][1] * B0 + M[k][2] * K5 + RC[1][k]) % P
        assert self.slope[k] == 0 and all(self.slope[t] for t in (i, j))
        for t in (i, j): assert (M[t][0] * A0 + M[t][1] * B0 + M[t][2] * K5 + RC[1][t]) % P == 0
        # state after round-1 S-box as affine functions of T' : lane t = sb_lin[t]*T' + sb_const[t]
        self.sb_lin = [0 if t == k else pow(self.slope[t], 5, P) for t in range(3)]
        self.sb_const = [pow(self.constk, 5, P) if t == k else 0 for t in range(3)]
    def inputs(self, Tp):
        T_ = pow(Tp, E5, P); A = (self.lam5 * T_ + self.A0) % P; B = (self.mu5 * T_ + self.B0) % P
        return (pow(A, E5, P) - self.RC[0][0]) % P, (pow(B, E5, P) - self.RC[0][1]) % P
    def build_f(self):
        """lane-0 output as a polynomial in T' (composition, FLINT). Uniquely defined; charged as
        evaluation at the N1 roots of unity + one inverse transform (proof 4.4)."""
        pc = self.pctx; M, RC = self.M, self.RC
        st = [sum((pc([M[row][col]]) * pc([self.sb_const[col], self.sb_lin[col]]) for col in range(3)), pc([0])) for row in range(3)]
        for i in [2, 3, *range(4, 4 + self.r), *range(60, 64)]:
            st = [x + pc([c]) for x, c in zip(st, RC[i])]
            for col in (range(3) if i < 4 or i >= 60 else range(1)): st[col] = st[col] ** 5
            st = [sum((pc([M[row][col]]) * st[col] for col in range(3)), pc([0])) for row in range(3)]
        f = st[0]; assert f.degree() == 5 ** (6 + self.r)
        for Tp in (1, 2, 12345):     # consistency with the permutation
            assert int(f(self.ctx(Tp))) == self.H(*self.inputs(Tp))
        return f

STREAM = "seq"                                   # start points s_n = n + 1 (the board convention)
STREAM_COST = {"seq": 1}                         # one addition
def stream(r, n): return n + 1

def run(cpath, r, outdir, max_trials=None):
    t = Target(cpath, r); D = 5 ** (6 + r); N1 = n3(D); N2 = n3(2 * D - 1); C = t.Cnorm
    ledger = {'stream': STREAM, 'r': r, 'D': D, 'N1': N1, 'N2': N2, 'C': C, 'phases': {}, 'memory_words': {}, 'trials': []}
    ph, mem = ledger['phases'], ledger['memory_words']
    t0 = time.time(); f = t.build_f(); t_build = time.time() - t0
    # charge: N1 evaluations (affine start 6 + 6 full rounds*27 + r partial*21 + 1 store) + IFFT_N1 + scaling
    # setup (Lemma 1 constants: two inversions, a handful of fifth powers, products and sums) charged as a flat 2,000
    # Lemma 1 constants (2,000) + transform constants: for each of at most 20 lengths, the root of unity, at most
    # 20 per-level twiddle steps and N^-1, each an exponentiation of at most 380 units: 20 * 22 * 380 = 167,200
    # (earlier driver, kept for Target and its constants; this run() is not called by the current entries, whose setup is
    #  attack_mont.SETUP: fewer than 440 constants of at most 400 units, the largest ladder being 400)
    ph['setup'] = 2000 + 167200
    # build of f, charged once per trial (f is discarded after q is formed and rebuilt on a retry):
    # N1 evaluations + IFFT_N1 + N1 scaling + evaluation points omega^i by running product (1 mul + 1 store each)
    BUILD = JI(N1 * (6 + 27 * 6 + 21 * r + 1) + T(N1) + N1 + 2 * N1 + 3 * N1)   # + permutation of the points into the transform order
    ph['build_f_per_trial'] = BUILD
    mem['build_f'] = 2 * N1 + 8        # evaluation points, evaluation buffer (becomes f), state
    mem['form_q'] = 2 * D + 8          # f and q live together during the synthetic division
    X = t.pctx.gen()
    from powering import execute_frobenius     # Frobenius powering (proof 4.2-4.3)
    from gcd_stage import gcd_stage            # counted half-gcd and roots (proof 5)
    from halfgcd_charge import gcd_overhead
    result = None
    for n in range(max_trials or 10 ** 9):          # retries until a trial succeeds
        s0 = stream(r, n); x0, x1 = t.inputs(s0); y = t.H(x0, x1)
        assert int(f(t.ctx(s0))) == y
        q, rem = divmod(f - t.pctx([y]), X - t.pctx([s0])); assert rem == 0 and q.degree() == D - 1
        lead = int(q[D - 1]); q = q * t.pctx([pow(lead, P - 2, P)]); assert int(q[D - 1]) == 1
        trial = {'n': n, 's0': str(s0), 'inputs0': [str(x0), str(x1)], 'y': str(y)}
        # charges: build of f; start-point draw (one addition); inputs: 3 fifth roots; y: one
        # permutation; synthetic division 4D; monic: inversion + 4D; forming h - X later: 4
        trial['ops_build'] = BUILD
        trial['ops_prepare'] = STREAM_COST[STREAM] + 3 * ROOT5_COST + C + 4 * D + INV_COST + 4 * D + 4
        t1 = time.time(); h, led_pow = execute_frobenius(q, r, cache_qn1=False); trial['t_pow'] = time.time() - t1
        trial['ops_powering'] = JI(led_pow['ops']['total']); trial['mem_powering'] = led_pow['peak_words']['max']
        trial['powering'] = {k: v for k, v in led_pow.items() if k not in ('time_log2', 'memory_log2', 'score_contribution', 'memory_bytes')}
        t2 = time.time(); g, roots, led_gcd = gcd_stage(q, h - X, r); trial['t_gcd'] = time.time() - t2
        trial['ops_gcd'] = led_gcd['ops']; trial['mem_gcd'] = led_gcd['peak_words']; trial['gcd'] = {k: v for k, v in led_gcd.items() if k != 'trace'}
        trial['gcd_trace'] = led_gcd.get('trace')
        trial['ops_gcd_overhead'] = gcd_overhead(led_gcd.get('trace') or {})   # proof 5.2: copy loops, load/store, bookkeeping
        trial['deg_g'] = g.degree(); trial['roots'] = [str(int(x)) for x in roots]
        trial['ops_total'] = trial['ops_build'] + trial['ops_prepare'] + trial['ops_powering'] + trial['ops_gcd'] + trial['ops_gcd_overhead']
        ledger['trials'].append(trial)
        print(f"trial {n}: deg g = {g.degree()} pow {trial['t_pow']:.0f}s gcd {trial['t_gcd']:.0f}s ops {trial['ops_total']:.4g}")
        if g.degree() >= 1:
            pairs = []
            for rt in roots:
                s1 = int(rt); u0, u1 = t.inputs(s1)
                assert (u0, u1) != (x0, x1) and t.H(u0, u1) == y
                pairs.append({'s1': str(s1), 'inputs': [str(u0), str(u1)]})
            # charge: per root 3 fifth roots + 1 verifying permutation + 8 for the digest comparison; plus the s0 digest
            trial['ops_finish'] = len(roots) * (3 * ROOT5_COST + C + 8) + C
            trial['ops_total'] += trial['ops_finish']
            result = (trial, pairs, y); break
    assert result, "no trial succeeded"
    trial, pairs, y = result
    total = JI(ph['setup'] + sum(tr['ops_total'] for tr in ledger['trials']))
    peak = max(mem['build_f'], mem['form_q'], max(max(tr['mem_powering'], tr['mem_gcd']) for tr in ledger['trials']))
    ledger['total_ops'] = total; ledger['time_log2'] = math.log2(total / C)
    ledger['peak_words'] = peak; ledger['memory_bytes'] = peak * 32 + CODE_BYTES
    ledger['memory_log2_bytes'] = math.log2(ledger['memory_bytes'])
    ledger['score'] = ledger['time_log2'] + max(0, ledger['memory_log2_bytes'] - 20)
    ledger['digest'] = y.to_bytes(32, 'little').hex(); ledger['pairs'] = pairs; ledger['t_build'] = t_build
    os.makedirs(outdir, exist_ok=True)
    for tr_ in ledger['trials']:
        if tr_.get('gcd_trace') is not None:
            json.dump(tr_['gcd_trace'], open(os.path.join(outdir, f'gcd_trace_r{r}_t{tr_["n"]}.json'), 'w', newline=chr(10)), separators=(',', ':'))
        tr_.pop('gcd_trace', None)
    json.dump(ledger, open(os.path.join(outdir, f'ledger_r{r}.json'), 'w', newline=chr(10)), indent=1, default=_jd)
    # certificates
    cdir = os.path.join(outdir, f'package_r{r}', 'certificates'); os.makedirs(cdir, exist_ok=True)
    enc = lambda a, b: int(a).to_bytes(32, 'little') + int(b).to_bytes(32, 'little')
    x0, x1 = map(int, trial['inputs0']); open(os.path.join(cdir, 'message-a.bin'), 'wb').write(enc(x0, x1))
    certs = []
    for i, pr in enumerate(pairs):
        name = f'message-b{i}.bin' if i else 'message-b.bin'
        open(os.path.join(cdir, name), 'wb').write(enc(*pr['inputs']))
        certs.append({'id': f'orchard-r{r}-pair-{i}', 'type': 'hash-collision-witness-v2', 'message_a': 'certificates/message-a.bin',
                      'message_b': f'certificates/{name}', 'expected_digest': ledger['digest'], 'target_profile': f'poseidon-orchard-r{r}-prefix-v1'})
    json.dump({'schema_version': 2, 'certificates': certs}, open(os.path.join(cdir, 'manifest.json'), 'w', newline=chr(10)))
    print(json.dumps({k: ledger[k] for k in ('total_ops', 'time_log2', 'peak_words', 'memory_log2_bytes', 'score', 'digest')}, indent=1, default=_jd))
    return ledger

if __name__ == '__main__':
    a = sys.argv; mt = int(a[a.index('--max-trials') + 1]) if '--max-trials' in a else None
    run(a[1], int(a[2]), a[3], mt)
```

### ntt.py

```python
"""ntt.py - instrumented number-theoretic transform over the Pallas field, N = 3*2^k or N = 2^k.
(The description below is for N = 3*2^k; for N = 2^k there is no radix-3 stage, the radix-2 levels run down to length 2,
and the leftover radix-2 levels after the passes of three are closed by one more load/store pass; see T and T_S.)

Forward = decimation in frequency (radix-2 levels, lengths N, N/2, ..., 6, then one
untwiddled 3-point DFT on each contiguous block of 3).  Inverse = exact reversal
(3-point inverse DFT, then decimation-in-time levels 6, 12, ..., N) and returns N*a.
Outputs of the forward transform are in a fixed permuted order; pointwise products are
order-free, so no bit-reversal permutation exists anywhere.  Twiddles are generated on the
fly by a running product (one multiplication per butterfly), so there is NO twiddle table:
the charge per radix-2 butterfly is 2 mul + 1 add + 1 sub + 1/2 loop = 4.5.

The radix-3 stage is innermost and needs no twiddles, so a radix-3 butterfly is one 3-point DFT
= 1 mul + 7 add/sub + 1/2 loop = 8.5.  T(N) below is the closed form for this algorithm.

Memory traffic: register-blocked passes of three radix-2 levels: (1 load + 1 store)/3 per
element per radix-2 level; the radix-3 level is one pass: 1 load + 1 store per element.
Pass schedule: levels are grouped into passes of three radix-2 levels; the k mod 3 leftover
levels are merged with the radix-3 level into one final pass, so the actual traffic is
2N*(floor(k/3)+1) <= (2/3)Nk + 2N for every k (equality at k = 15 and k = 18).  The
instrumented kernel does not model passes; it charges the closed form per level.
Loop control: a radix-8 pass processes 8 elements = 12 butterflies per iteration (one index
add + one compare + one branch = 3 units per 12 butterflies), so 1/2 per butterfly is
conservative.

T(N) = (N/2)*k*(9/2) + (2/3)*N*k + (N/3)*(17/2) + 2N  =  N*(35/12*k + 29/6),  k = log2(N/3).
"""
from fractions import Fraction

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
_FACTORS = (2, 3, 463, 539204044132271846773, 8999194758858563409123804352480028797519453)


def _generator():
    g = 2
    while True:
        if all(pow(g, (P - 1) // f, P) != 1 for f in _FACTORS):
            return g
        g += 1


GEN = _generator()


def root_of_unity(N):
    assert (P - 1) % N == 0
    return pow(GEN, (P - 1) // N, P)


def log2_k(N):
    """N = 3*2^k -> k (radix-3 innermost stage), or N = 2^k -> k (radix-2 only)."""
    if N % 3 == 0:
        assert N // 3 > 0 and (N // 3) & (N // 3 - 1) == 0, N
        return (N // 3).bit_length() - 1
    assert N > 1 and N & (N - 1) == 0, N
    return N.bit_length() - 1


def radix3(N):
    return N % 3 == 0


def mont_length(x):
    """least n >= x of the form 3*2^k or 2^k (the Montgomery length; products elsewhere keep 3*2^k)."""
    a = nice_length(x)
    b = 2
    while b < x:
        b *= 2
    return min(a, b)


def nice_length(n):
    """Smallest 3*2^k >= n."""
    N = 3
    while N < n:
        N *= 2
    return N


class Counter:
    """Charge counter for both conventions.
    loose  (our earlier entries): every category below counts 1 per unit; 'loop' holds 1/2 unit per element
           of an unrolled streaming loop.
    strict (the convention of the executed-C entries on this board): field op 1, load/store 1 + 1 address
           operation = 2, a loop of e elements unrolled by 8 costs 3 per iteration + 2 on exit
           (3*ceil(e/8) + 2, recorded by lp(e)), 'ctl' (explicit control: non-unrolled loop iterations at 3,
           trailing-zero counts, branches) counts the same in both.
    """
    CATS = ('mul', 'add', 'sub', 'load', 'store', 'loop', 'ctl')

    def __init__(self):
        self.c = {k: Fraction(0) for k in self.CATS}
        self.lps = Fraction(0)

    def add(self, **kw):
        for k, v in kw.items():
            self.c[k] += Fraction(v)

    def lp(self, e):
        if e:
            self.lps += 3 * (-(-e // 8)) + 2

    def total(self):
        return sum(self.c.values())

    def strict(self):
        c = self.c
        return c['mul'] + c['add'] + c['sub'] + c['ctl'] + 2 * (c['load'] + c['store']) + self.lps

    def snapshot(self):
        return dict(self.c)

    def __repr__(self):
        return 'Counter(total=%s, strict=%s, %s)' % (self.total(), self.strict(), {k: str(v) for k, v in self.c.items()})


def LP(e):
    """strict loop charge of a loop over e elements unrolled by 8."""
    return 3 * (-(-e // 8)) + 2 if e else 0


# closed-form charges -----------------------------------------------------------------
R2_BUTTERFLY = Fraction(9, 2)      # 2 mul + 1 add + 1 sub + 1/2 loop
R3_BUTTERFLY = Fraction(17, 2)     # 1 mul + 3 add + 4 sub + 1/2 loop
MEM_R2_LEVEL = Fraction(2, 3)      # per element per radix-2 level (load+store, radix-8 passes)
MEM_R3_LEVEL = 2                   # per element


def T(N):
    """Charged operations of one forward or inverse transform of length N = 3*2^k (or 2^k: no radix-3
    stage; one closing load/store pass for the k mod 3 leftover levels)."""
    k = log2_k(N)
    if not radix3(N):
        return Fraction(N, 2) * k * R2_BUTTERFLY + MEM_R2_LEVEL * N * k + 2 * N + Fraction(N, 2)
    return Fraction(N, 2) * k * R2_BUTTERFLY + MEM_R2_LEVEL * N * k + Fraction(N, 3) * R3_BUTTERFLY + MEM_R3_LEVEL * N


def _r2_charge(ctr, nb, N):
    ctr.add(mul=2 * nb, add=nb, sub=nb, loop=Fraction(nb, 2), load=Fraction(N, 3), store=Fraction(N, 3))
    ctr.lp(nb)


def _r1_charge(ctr, N):
    """closing pass of a 2^k transform (leftover levels): one load and one store per element."""
    ctr.add(load=N, store=N, loop=Fraction(N, 2))
    ctr.lp(N)


def _r3_charge(ctr, nb, N):
    ctr.add(mul=nb, add=3 * nb, sub=4 * nb, loop=Fraction(nb, 2), load=N, store=N)
    ctr.lp(nb)


def T_S(N):
    """strict charge of one transform of length N = 3*2^k or 2^k (same passes as T)."""
    k = log2_k(N)
    if not radix3(N):
        return k * (4 * Fraction(N, 2) + 2 * Fraction(2 * N, 3) + LP(N // 2)) + 4 * N + LP(N)
    return k * (4 * Fraction(N, 2) + 2 * Fraction(2 * N, 3) + LP(N // 2)) + (8 * Fraction(N, 3) + 4 * N + LP(N // 3))


def ntt_forward(a, ctr):
    """In place DIF transform of list a (length N = 3*2^k or 2^k) with instrumented charges."""
    N = len(a)
    k = log2_k(N)
    wN = root_of_unity(N)
    length = N
    for _ in range(k):
        half = length // 2
        wstep = pow(wN, N // length, P)
        nb = 0
        for start in range(0, N, length):
            w = 1
            for j in range(start, start + half):
                u = a[j]
                v = a[j + half]
                a[j] = (u + v) % P
                a[j + half] = ((u - v) * w) % P
                w = (w * wstep) % P
                nb += 1
        _r2_charge(ctr, nb, N)
        length = half
    if not radix3(N):
        assert length == 1
        _r1_charge(ctr, N)
        return a
    assert length == 3
    w3 = pow(wN, N // 3, P)
    nb = 0
    for s in range(0, N, 3):
        a0, a1, a2 = a[s], a[s + 1], a[s + 2]
        t = (a1 + a2) % P
        d = (a1 - a2) % P
        m = (w3 * d) % P
        a[s] = (a0 + t) % P
        a[s + 1] = (a0 - a2 + m) % P
        a[s + 2] = (a0 - a1 - m) % P
        nb += 1
    _r3_charge(ctr, nb, N)
    return a


def ntt_inverse(a, ctr):
    """In place DIT inverse of ntt_forward; returns N * (original vector) (unscaled)."""
    N = len(a)
    k = log2_k(N)
    wN = root_of_unity(N)
    if not radix3(N):
        _r1_charge(ctr, N)
    w3i = pow(wN, N - N // 3, P) if radix3(N) else None
    nb = 0
    for s in (range(0, N, 3) if radix3(N) else ()):
        a0, a1, a2 = a[s], a[s + 1], a[s + 2]
        t = (a1 + a2) % P
        d = (a1 - a2) % P
        m = (w3i * d) % P
        a[s] = (a0 + t) % P
        a[s + 1] = (a0 - a2 + m) % P
        a[s + 2] = (a0 - a1 - m) % P
        nb += 1
    if radix3(N):
        _r3_charge(ctr, nb, N)
    length = 3 if radix3(N) else 1
    for _ in range(k):
        half = length
        length *= 2
        wstep = pow(wN, N - N // length, P)
        nb = 0
        for start in range(0, N, length):
            w = 1
            for j in range(start, start + half):
                u = a[j]
                v = (a[j + half] * w) % P
                a[j] = (u + v) % P
                a[j + half] = (u - v) % P
                w = (w * wstep) % P
                nb += 1
        _r2_charge(ctr, nb, N)
    assert length == N
    return a


def _selftest():
    import random
    rng = random.Random(1)
    for N in (3, 6, 12, 24, 48, 96, 192, 384, 768, 1536, 3072, 2, 4, 8, 16, 64, 256, 1024, 4096):
        a = [rng.randrange(P) for _ in range(N)]
        b = [rng.randrange(P) for _ in range(N)]
        c1, c2 = Counter(), Counter()
        A = ntt_forward(list(a), c1)
        B = ntt_forward(list(b), Counter())
        assert c1.total() == T(N), (N, c1.total(), T(N))
        assert c1.strict() == T_S(N), (N, c1.strict(), T_S(N))
        back = ntt_inverse(list(A), c2)
        assert c2.total() == T(N), (N, c2.total(), T(N))
        assert [(x * pow(N, P - 2, P)) % P for x in back] == a
        C = [(x * y) % P for x, y in zip(A, B)]
        conv = ntt_inverse(C, Counter())
        invN = pow(N, P - 2, P)
        conv = [(x * invN) % P for x in conv]
        ref = [0] * N
        for i in range(N):
            for j in range(N):
                ref[(i + j) % N] = (ref[(i + j) % N] + a[i] * b[j]) % P
        assert conv == ref, N
        print('N=%5d k=%2d T(N)=%s ok' % (N, log2_k(N), T(N)))


if __name__ == '__main__':
    _selftest()
```

### mont.py

```python
"""mont.py - value-domain Montgomery powering S^e mod g on two cosets (counted kernels, two conventions).

Reconstruction of the stage-C method of bradcush (first in 1aa56884 at r = 21, then 4bcabff8 at r = 3):
value-domain Montgomery squaring with R = X^n - 1 on O1 = H_n and O2 = psi*H_n, where R = -2; written from
scratch on the poseidon_mage transform kernels (ntt.py).

Charges are recorded on ntt.Counter in both conventions (see its docstring): 'strict' = field op 1,
load/store 2 (one address operation each), loops unrolled by 8 at 3 per iteration + 2 on exit, explicit
control 'ctl'; 'loose' = our earlier entries' rules. Register file: at most 16 words of 256 bits (operands
held there are not loads). Every closed form below returns V(loose, strict) and the self-test asserts both
against the instrumented execution.

Objects: g monic of degree m, n = 3*2^k > m, omega = primitive n-th root, psi = primitive 2n-th root
(psi^2 = omega, psi^n = -1). R = X^n - 1 is invertible mod g when g has no root on O1 (checked).
Montgomery form of x: x~ = x R mod g, kept as an unreduced representative of degree < n.
A polynomial A (deg < n) is held as its values A1 on O1 and A2 on O2 (DIF output order of ntt.py).

One squaring (mont_step): Mont(A, A) = (A^2 + U g) / R with U = -A^2 g^-1 mod R:
  P1  U1 = A1^2 * Ginv1, Ginv1 = -1/(n g) on O1                 (U/n on O1; 1/n folded)
  inverse transform on O1 -> U coefficients; twist by psi^j; forward transform -> U on O2
  P2  B2 = A2^2 * h + U2 * G2h, h = -1/2, G2h = -g/2 on O2        (= Mont(A, A) on O2, deg <= n-2)
      [for a 1-bit of e: B2 *= point (psi omega^e(t)), generated in transform order: deg <= n-1]
      store B2 into A2 and into the work buffer A1
  inverse transform of A1 on O2; untwist by psi^-j / n; forward transform on O1 -> new A1.
Four transforms of length n per step, four buffers of n words (A1, A2, Ginv1, G2h).
"""
from fractions import Fraction
from ntt import P, T, T_S, LP, Counter, ntt_forward, ntt_inverse, root_of_unity, log2_k, nice_length, radix3, mont_length

H = Fraction(1, 2)
INV_COST = 380          # field inversion charge (>= the 330-unit ladder; registers only)


class V:
    """a charge in both conventions."""
    __slots__ = ('l', 's')

    def __init__(self, l=0, s=0):
        self.l = Fraction(l); self.s = Fraction(s)

    def __add__(self, o):
        return V(self.l + o.l, self.s + o.s)

    __radd__ = lambda self, o: self if o == 0 else self.__add__(o)

    def __mul__(self, k):
        return V(self.l * k, self.s * k)

    __rmul__ = __mul__

    def __eq__(self, o):
        return isinstance(o, V) and self.l == o.l and self.s == o.s

    def __repr__(self):
        return 'V(loose=%s, strict=%s)' % (self.l, self.s)


def ctrV(c):
    return V(c.total(), c.strict())


def TV(N):
    return V(T(N), T_S(N))


def PASS(e, arith=0, load=0, store=0):
    """a streaming loop over e elements with the given totals."""
    return V(arith + load + store + Fraction(e, 2), arith + 2 * (load + store) + LP(e))


def OPS(arith=0, load=0, store=0, ctl=0):
    """straight-line work (no loop charge)."""
    return V(arith + load + store + ctl, arith + 2 * (load + store) + ctl)


def cpass(ctr, e, **kw):
    """charge a streaming pass on the counter (loose 1/2 per element, strict LP(e))."""
    ctr.add(loop=Fraction(e, 2), **kw)
    ctr.lp(e)


def inv(x):
    return pow(x, P - 2, P)


# ---------------------------------------------------------------- point generator (transform order)
def point_exponents(n):
    """exponent e(t) of the evaluation point omega^e(t) at output position t of ntt_forward (length n)."""
    k = log2_k(n)
    bs = 3 if radix3(n) else 1
    out = []
    for B in range(n // bs):
        rb = int(format(B, '0%db' % k)[::-1], 2) if k else 0
        for s in range(bs):
            out.append(rb + (s << k))
    return out


def point_stream(n, base, mult, ctr):
    """yield mult * base^e(t) for t = 0..n-1 (e(t) as point_exponents).
    Prefix stack pre[0..k] (registers if k + 1 <= 8, else memory: charged as memory always),
    pre[i] = mult * prod_{j<=i} base^(b_j 2^(j-1)) over the MSB-first bits of the block index B.
    Charges: k + 1 initial stores; per block a non-unrolled loop iteration (3) + trailing-zero count (1)
    + branch (1) = 5 ctl, recompute one prefix (2 loads: pre[j-1] and the constant, 1 mul, 1 store),
    straight-line stores of the copied prefixes (the copies below the changed bit), 2 multiplications
    for the cube-root companions; loop exit 2 ctl."""
    k = log2_k(n)
    bs = 3 if radix3(n) else 1
    cst = [pow(base, 1 << i, P) for i in range(k)]
    w3 = pow(base, n // 3, P) if bs == 3 else 1
    w3b = w3 * w3 % P
    pre = [mult] * (k + 1)
    ctr.add(store=k + 1, ctl=2)
    for B in range(n // bs):
        if B:
            tz = (B & -B).bit_length() - 1
            j = k - tz
            pre[j] = pre[j - 1] * cst[j - 1] % P
            for i in range(j + 1, k + 1):
                pre[i] = pre[j]
            ctr.add(load=2, mul=1, store=1 + (k - j))
        ctr.add(ctl=5, mul=bs - 1)
        x = pre[k]
        yield x
        if bs == 3:
            yield x * w3 % P
            yield x * w3b % P


def PG(n):
    """closed form of point_stream (sum over blocks of the copied prefixes = n/3 - k - 1)."""
    k = log2_k(n)
    bs = 3 if radix3(n) else 1
    nb = n // bs
    tz_sum = nb - k - 1
    return OPS(store=k + 1, ctl=2) + OPS(arith=nb - 1, load=2 * (nb - 1), store=(nb - 1) + tz_sum) + OPS(arith=(bs - 1) * nb, ctl=5 * nb)


# ---------------------------------------------------------------- streaming passes
def twist(buf, c0, step, ctr):
    """buf[j] *= c0 * step^j (running product in a register): load, 2 mul, store per element."""
    w = c0
    for j in range(len(buf)):
        buf[j] = buf[j] * w % P
        w = w * step % P
    n = len(buf)
    cpass(ctr, n, load=n, mul=2 * n, store=n)


def TW(n):
    return PASS(n, arith=2 * n, load=n, store=n)


def mont_step(A1, A2, Ginv1, G2h, psi, ctr, mulx=False):
    n = len(A1)
    for i in range(n):                                       # P1
        a = A1[i]
        A1[i] = a * a % P * Ginv1[i] % P
    cpass(ctr, n, load=2 * n, mul=2 * n, store=n)
    ntt_inverse(A1, ctr)                                     # U coefficients (exact)
    twist(A1, 1, psi, ctr)
    ntt_forward(A1, ctr)                                     # U on O2
    h = (P - 1) * inv(2) % P
    if mulx:
        pts = point_stream(n, root_of_unity(n), psi, ctr)
    for i in range(n):                                       # P2 (+ store into both buffers)
        a = A2[i]
        b = (a * a % P * h + A1[i] * G2h[i]) % P
        if mulx:
            b = b * next(pts) % P
        A2[i] = b
        A1[i] = b
    cpass(ctr, n, load=3 * n, mul=3 * n, add=n, store=2 * n)
    if mulx:
        ctr.add(mul=n)
    ntt_inverse(A1, ctr)                                     # n * psi^j * coefficients
    twist(A1, inv(n), inv(psi), ctr)
    ntt_forward(A1, ctr)                                     # new A1


def STEP(n, mulx=False):
    s = 4 * TV(n) + 2 * TW(n) + PASS(n, arith=2 * n, load=2 * n, store=n) + PASS(n, arith=4 * n, load=3 * n, store=2 * n)
    if mulx:
        s = s + OPS(arith=n) + PG(n)
    return s


# ---------------------------------------------------------------- setup and finish
def copy_scaled(dst, src, c, ctr):
    for i in range(len(src)):
        dst[i] = src[i] * c % P
    n = len(src)
    cpass(ctr, n, load=n, mul=n, store=n)


def batch_invert(buf, scratch, c, ctr):
    """buf[i] <- c / buf[i] (Montgomery's trick; prefix products in scratch)."""
    n = len(buf)
    run = 1
    for i in range(n):
        run = run * buf[i] % P
        scratch[i] = run
    cpass(ctr, n, load=n, mul=n, store=n)
    run = inv(run) * c % P
    ctr.add(mul=INV_COST + 1)
    for i in range(n - 1, 0, -1):
        x = buf[i]
        buf[i] = run * scratch[i - 1] % P
        run = run * x % P
    buf[0] = run
    cpass(ctr, n - 1, load=2 * (n - 1), mul=2 * (n - 1), store=n - 1)
    ctr.add(store=1)


def BINV(n):
    return PASS(n, arith=n, load=n, store=n) + OPS(arith=INV_COST + 1) + PASS(n - 1, arith=2 * (n - 1), load=2 * (n - 1), store=n - 1) + OPS(store=1)


def _pm(dst, src, N, ctr):
    invN = inv(N)
    for i in range(N):
        dst[i] = dst[i] * src[i] % P * invN % P
    cpass(ctr, N, load=2 * N, mul=2 * N, store=N)


def series_inverse(f, L, ctr):
    """g = f^-1 mod X^L for f[0] = 1 (f a list, zero beyond its length), Newton doubling with transforms
    of length nice(m2)."""
    g = [1]
    m = 1
    while m < L:
        m2 = min(2 * m, L)
        N = nice_length(m2)
        lf = min(m2, len(f))
        F = [f[i] for i in range(lf)] + [0] * (N - lf)
        cpass(ctr, N, load=lf, store=N)
        G = list(g) + [0] * (N - m)
        cpass(ctr, N, load=m, store=N)
        ntt_forward(F, ctr)
        ntt_forward(G, ctr)
        _pm(F, G, N, ctr)
        ntt_inverse(F, ctr)
        hh = F[m:m2]
        for i in range(m2 - m):
            F[i] = hh[i]
        cpass(ctr, m2 - m, load=m2 - m, store=m2 - m)
        for i in range(m2 - m, N):
            F[i] = 0
        cpass(ctr, N - (m2 - m), store=N - (m2 - m))
        ntt_forward(F, ctr)
        _pm(F, G, N, ctr)
        ntt_inverse(F, ctr)
        g = g + [(-F[i]) % P for i in range(m2 - m)]
        cpass(ctr, m2 - m, load=m2 - m, sub=m2 - m, store=m2 - m)
        m = m2
    return g


def SINV(L, lenf):
    tot = V()
    m = 1
    while m < L:
        m2 = min(2 * m, L)
        N = nice_length(m2)
        lf = min(m2, lenf)
        d = m2 - m
        tot = tot + PASS(N, load=lf, store=N) + PASS(N, load=m, store=N) + 5 * TV(N) \
            + 2 * PASS(N, arith=2 * N, load=2 * N, store=N) + PASS(d, load=d, store=d) + PASS(N - d, store=N - d) \
            + PASS(d, arith=d, load=d, store=d)
        m = m2
    return tot


def SINV_PEAK(L, lenf):
    """F (N) + G (N) + g (m2) at the largest step (f itself is the caller's buffer)."""
    best = 0
    m = 1
    while m < L:
        m2 = min(2 * m, L)
        best = max(best, 2 * nice_length(m2) + m2)
        m = m2
    return best


def start_plan(n, m):
    """largest a = 2^j with L = n + a - m + 1, nice(L) <= n/2 (the Newton buffers fit in one n-word
    buffer) and a < m. Returns (j, L)."""
    j = 0
    while True:
        a = 1 << (j + 1)
        L = n + a - m + 1
        if a >= m or nice_length(L) > n // 2:
            break
        j += 1
    return j, n + (1 << j) - m + 1


def setup_and_power(G1, m, e, ctr, verbose=False):
    """G1: values of monic g (degree m) on O1 in transform order, as delivered by the build stage
    (buffer B0). Executes the counted stage: interpolation of g, Newton start residue, batch inversion,
    O2 tables, the powering, and the final conversion. Returns (Y coefficients (deg < m), g, info).
    Buffers: B0 (G1 -> Ginv1), B1 (g -> G2h -> g), B2 (Newton F|G -> prefixes -> A2), B3 (ginv/q -> A1)."""
    n = mont_length(m + 1)
    assert len(G1) == n
    omega = root_of_unity(n)
    psi = root_of_unity(2 * n)
    assert pow(psi, 2, P) == omega and pow(psi, n, P) == P - 1
    info = {'n': n, 'm': m}
    marks = {}

    def mark(name):
        marks[name] = (ctr.total(), ctr.strict())

    mark('start')
    B0 = G1
    assert all(B0), 'g has a root on O1'
    B1 = [0] * n
    copy_scaled(B1, B0, inv(n), ctr)
    ntt_inverse(B1, ctr)
    assert B1[m] == 1 and not any(B1[m + 1:]), 'g is not monic of degree m'
    gc = B1[:m + 1]
    mark('g_values')
    j, L = start_plan(n, m)
    f = [gc[m - i] for i in range(m + 1)]               # rev(g): read through reversed indexing (no copy)
    ginv = series_inverse(f, L, ctr)
    q = ginv[::-1] + [0] * (n - L)
    cpass(ctr, n, load=L, store=n)                      # reversed copy + pad into B3
    ntt_forward(q, ctr)
    mi = (P - inv(n)) % P
    for i in range(n):
        q[i] = q[i] * B0[i] % P * mi % P
    cpass(ctr, n, load=2 * n, mul=2 * n, store=n)
    ntt_inverse(q, ctr)
    for i in range(m, n):
        q[i] = 0
    cpass(ctr, n - m, store=n - m)
    start = q
    mark('start_residue')
    B2 = [0] * n
    batch_invert(B0, B2, mi, ctr)
    mark('batch_inverse')
    A2 = [0] * n
    w = 1
    for i in range(n):
        A2[i] = start[i] * w % P
        w = w * psi % P
    cpass(ctr, n, load=n, mul=2 * n, store=n)
    ntt_forward(A2, ctr)
    A1 = start
    ntt_forward(A1, ctr)
    twist(B1, (P - 1) * inv(2) % P, psi, ctr)
    ntt_forward(B1, ctr)
    G2h = B1
    mark('tables')
    K = e.bit_length() - 1
    for b in range(K - 1, K - 1 - j, -1):
        assert not (e >> b) & 1
    nmx = 0
    for b in range(K - 1 - j, -1, -1):
        bit = (e >> b) & 1
        mont_step(A1, A2, B0, G2h, psi, ctr, mulx=bool(bit))
        nmx += bit
    info.update({'j': j, 'L': L, 'n_squarings': K - j, 'n_mulx': nmx})
    mark('powering')
    for i in range(n):
        A1[i] = A1[i] * B0[i] % P
    cpass(ctr, n, load=2 * n, mul=n, store=n)
    ntt_inverse(A1, ctr)
    twist(A1, 1, psi, ctr)
    ntt_forward(A1, ctr)
    h = (P - 1) * inv(2) % P
    for i in range(n):
        A1[i] = (A2[i] * h + A1[i] * G2h[i]) % P
    cpass(ctr, n, load=3 * n, mul=2 * n, add=n, store=n)
    ntt_inverse(A1, ctr)
    twist(A1, inv(n), inv(psi), ctr)
    Y = A1[:m]
    assert all(x == 0 for x in A1[m:]), 'final value not reduced'
    ntt_inverse(G2h, ctr)
    twist(G2h, (P - 2) * inv(n) % P, inv(psi), ctr)
    assert G2h[:m + 1] == list(gc) and not any(G2h[m + 1:])
    mark('finish')
    info['marks'] = marks
    return Y, gc, info


PHASES = ['g_values', 'start_residue', 'batch_inverse', 'tables', 'powering', 'finish']


def SETUP_POWER(m, e):
    """closed forms of setup_and_power per phase (V values)."""
    n = mont_length(m + 1)
    j, L = start_plan(n, m)
    K = e.bit_length() - 1
    ph = {}
    ph['g_values'] = PASS(n, arith=n, load=n, store=n) + TV(n)
    ph['start_residue'] = SINV(L, m + 1) + PASS(n, load=L, store=n) + TV(n) + PASS(n, arith=2 * n, load=2 * n, store=n) \
        + TV(n) + PASS(n - m, store=n - m)
    ph['batch_inverse'] = BINV(n)
    ph['tables'] = PASS(n, arith=2 * n, load=n, store=n) + 3 * TV(n) + TW(n)
    bits = [(e >> b) & 1 for b in range(K - 1 - j, -1, -1)]
    nmx = sum(bits)
    ph['powering'] = (len(bits) - nmx) * STEP(n) + nmx * STEP(n, True)
    ph['finish'] = PASS(n, arith=n, load=2 * n, store=n) + 2 * TV(n) + TW(n) + PASS(n, arith=3 * n, load=3 * n, store=n) \
        + TV(n) + TW(n) + TV(n) + TW(n)
    return ph, {'n': n, 'j': j, 'L': L, 'n_squarings': len(bits), 'n_mulx': nmx,
                'step_plain': STEP(n), 'step_mulx': STEP(n, True)}


def PEAK_WORDS(m):
    """live words of setup_and_power: max over its phases."""
    n = mont_length(m + 1)
    j, L = start_plan(n, m)
    newton = 2 * n + SINV_PEAK(L, m + 1)        # B0 (G1), B1 (g; rev(g) read in place), F + G + ginv
    return max(4 * n, newton)


def _selftest():
    import random
    from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
    ctx = fmpz_mod_ctx(P)
    pctx = fmpz_mod_poly_ctx(ctx)
    X = pctx.gen()
    rng = random.Random(5)
    for n in (3, 6, 12, 24, 48, 96, 192, 384, 768, 2, 4, 16, 128, 1024):
        c = Counter()
        pts = list(point_stream(n, root_of_unity(n), 7, c))
        ex = point_exponents(n)
        om = root_of_unity(n)
        assert pts == [7 * pow(om, x, P) % P for x in ex]
        vx = ntt_forward([0, 1] + [0] * (n - 2), Counter())
        assert vx == [pow(om, x, P) for x in ex]
        assert ctrV(c) == PG(n), (n, ctrV(c), PG(n))
    e = (P - 1) // 2
    for m in (20, 40, 90, 180, 370, 60, 120, 250):
        g = [rng.randrange(P) for _ in range(m)] + [1]
        c = Counter()
        n = mont_length(m + 1)
        G1 = ntt_forward(list(g) + [0] * (n - m - 1), Counter())
        Y, g2, info = setup_and_power(G1, m, e, c)
        assert g2 == g
        ref = X.pow_mod(e, pctx(g))
        assert pctx(Y) == ref, 'powering wrong'
        ph, inf2 = SETUP_POWER(m, e)
        mk = info['marks']
        prev = mk['start']
        for nm in PHASES:
            got = V(mk[nm][0] - prev[0], mk[nm][1] - prev[1])
            assert got == ph[nm], (m, nm, got, ph[nm])
            prev = mk[nm]
        print('m=%d n=%d j=%d L=%d sq=%d mx=%d loose=%s strict=%s ok' % (m, info['n'], info['j'], info['L'],
              info['n_squarings'], info['n_mulx'], c.total(), c.strict()))


if __name__ == '__main__':
    _selftest()
```

### halfgcd.py

```python
"""Counted half-gcd over F_p (python-flint arithmetic; every charge an exact Fraction).

Prices (orchard-field-ram-v2): field add/sub/mul, 256-bit load/store, compare/branch, shift/mask: 1 each.
Loop control: 1/2 per inner iteration (loops unrolled 8 per iteration, the convention of proof 4.1).
  T(N)   transform of length N = 3*2^k (ntt.py): N*(35k/12 + 29/6); only these lengths are used.
  transform product of lengths m1, m2, N = nice_length(m1+m2-1):
         3 T(N) + 5 N (pointwise: 2 loads, 2 muls with 1/N folded, 1 store) + 2 (m1+m2) (copy both inputs
         into padded buffers) + (N-m1) + (N-m2) (padding stores) + N/2 (loop control)
  classical product: 4 m1 m2 + m1 m2 / 2 + 2 (m1+m2-1); each product uses the cheaper rule.
  add/sub of length m: 4 m + m/2.   copy/shift/truncate of length m: 2 m + m/2.
  field inversion: 380 (a round-up of the 330-unit ladder for x^(p-2): 254 squarings + 76 multiplications).   monic: 380 + m + m/2.
  division of degree n by degree m, L = n-m+1: the cheaper of
         classical 380 + L (4 (m+1) + 2) + L (m+1)/2 + 2 (n+1) + (n+1)/2
         Newton    newton_inv(L) + product(L, L) + product(L, m+1) + 4 (m+1) + (m+1)/2 + 2 (n+1) + (n+1)/2
  newton_inv(L) = 380 + sum over doubling precisions m -> m2 = min(2m, L), N = nice_length(m2):
         (m2+N) + (m+N) + 5 T(N) + 10 N + 2 (m2-m) + (N-(m2-m)) + 3 (m2-m)      (modsq.NEWTON step)
LEAN mode (default; proof 5.1, memory-lean execution):
  views: a truncation r >> t handed to a child hgcd is a read-only pointer into the parent's buffer: no
         copy, no charge, no words (the child never writes its inputs; the parent keeps the buffer alive).
  matvec_wrap (R (a, b) with R = cofactor matrix from hgcd on the top part of (a, b)): one cyclic transform
         length N = nice_length(n_h + 1), n_h = deg a - deg R11 = deg of the first output (degree relation,
         asserted at run time together with deg of both outputs < N).  Charge, la/lb input lengths, l_ij the
         lengths of the entries (0 = absent):
           load(l)  = 5/2 min(l,N) + 9/2 max(0, l-N) (fold) + 3/2 max(0, N-l) (pad)       for a and b
           loadR(l) = 7/2 l (load, mul by 1/N, store, loop) + 3/2 (N-l)                    per nonzero entry
           T(N) per transformed input (a, b, each nonzero entry) and per nonzero output row (inverse);
           pointwise per row: 9/2 N for its first term (2 loads, mul, store, loop), 13/2 N for a second
           term (3 loads, mul, add, store, loop).
         Memory: 4 buffers of N words (a^, b^, X, Y) at the peak; the top level frees a, b once copied.
  matmul_shared (S P, 2x2): every entry transformed once at N = nice_length(max_{i,l,j} len S_il + len P_lj - 1)
         (linear, no wrap): P entries loadR, S entries load (5/2 l + 3/2 (N-l)), T(N) each nonzero entry, per
         row an in-place 2x2 pointwise pass 29/2 N (6 loads, 4 mul, 2 add, 2 stores, loop), T(N) per nonzero
         output entry.  Memory: 4 N (P^) + 2 N (one row of S^, overwritten by the row's outputs).
  Each wrapped/shared step is taken only when its charge is below the plain product-by-product charge.
Memory model: live coefficient words of every polynomial owned by an active frame of the recursion plus
transform scratch (2 N words for a transform product, m1+m2-1 for a classical one, (n+1)+L (+2N) for a division,
the buffer counts above for matvec_wrap / matmul_shared).
"""
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx

from fractions import Fraction
from ntt import T, nice_length   # T(N) for N = 3*2^k (and 2^k for wrapped steps when POW2), proof 4.1 / 3.1

LEAN = True            # views + wrapped matvec + top-level input freeing
SHARED_MATMUL = True   # shared-transform 2x2 matrix product inside hgcd (LEAN only)

POW2 = False   # wrapped matrix-vector steps and shared matrix products may use 2^k lengths when shorter (r >= 3)


def wrap_len(m):
    """transform length of a wrapped matrix-vector step or shared matrix product (its N is recorded in the trace)."""
    from ntt import mont_length
    return mont_length(max(m, 3)) if POW2 else ntt_len(m)


def ntt_len(m):
    """transform length for a product of total length m: smallest 3*2^k >= m."""
    return nice_length(max(m, 3))

def product_charge(m1, m2):
    if m1 == 0 or m2 == 0: return Fraction(0), 'zero', 0
    classical = Fraction(4 * m1 * m2) + Fraction(m1 * m2, 2) + 2 * (m1 + m2 - 1)
    N = ntt_len(m1 + m2 - 1)
    transform = 3 * T(N) + 5 * N + 2 * (m1 + m2) + (N - m1) + (N - m2) + Fraction(N, 2)
    if classical <= transform: return classical, 'classical', m1 + m2 - 1
    return transform, 'ntt', 2 * N

def newton_inv_charge(L):
    """inverse series to precision L (modsq.NEWTON step formula, proof 4.3), plus the constant-term inversion."""
    ops = Fraction(380); m = 1
    while m < L:
        m2 = min(2 * m, L); N = nice_length(max(m2, 3))
        ops += (m2 + N) + (m + N) + 5 * T(N) + 10 * N + 2 * (m2 - m) + (N - (m2 - m)) + 3 * (m2 - m)
        m = m2
    return ops

def division_charge(n, m):
    L = n - m + 1
    classical = Fraction(380 + L * (4 * (m + 1) + 2) + 2 * (n + 1)) + Fraction(L * (m + 1), 2) + Fraction(n + 1, 2)
    newton = newton_inv_charge(L) + product_charge(L, L)[0] + product_charge(L, m + 1)[0] + 4 * (m + 1) + Fraction(m + 1, 2) + 2 * (n + 1) + Fraction(n + 1, 2)
    return (classical, 'classical') if classical <= newton else (newton, 'newton')

# ---- lean kinds: charges (halfgcd_charge.py reproduces these independently) ----
def _load(l, N): return Fraction(5 * min(l, N), 2) + Fraction(9 * max(0, l - N), 2) + Fraction(3 * max(0, N - l), 2)
def _loadR(l, N): return Fraction(7 * l, 2) + Fraction(3 * (N - l), 2)
def _loadS(l, N): return Fraction(5 * l, 2) + Fraction(3 * (N - l), 2)

def matvec_wrap_charge(la, lb, l00, l01, l10, l11, N):
    ops = _load(la, N) + _load(lb, N) + 2 * T(N)
    for l in (l00, l01, l10, l11):
        if l: ops += _loadR(l, N) + T(N)
    for x, y in ((l00, l01), (l10, l11)):
        terms = (x > 0) + (y > 0)
        if terms: ops += Fraction(9 * N, 2) + (terms - 1) * Fraction(13 * N, 2) + T(N)
    return ops

def matmul_shared_charge(s, pm, N):
    """s = (s00, s01, s10, s11), pm = (p00, p01, p10, p11) entry lengths."""
    ops = Fraction(0)
    for l in pm:
        if l: ops += _loadR(l, N) + T(N)
    for l in s:
        if l: ops += _loadS(l, N) + T(N)
    for i in range(2):
        ops += Fraction(29 * N, 2)
        for j in range(2):
            if (s[2 * i] and pm[j]) or (s[2 * i + 1] and pm[2 + j]): ops += T(N)
    return ops

class Counter:
    """ops ledger + live-memory model: polynomials owned by active frames + transform scratch."""
    def __init__(self):
        self.ops = Fraction(0); self.peak = 0; self.frames = []; self.hist = {}; self.peak_where = None
        self.n_products = {'classical': 0, 'ntt': 0, 'zero': 0}; self.n_div = {'classical': 0, 'newton': 0}
        self.n_lean = {'matvec_wrap': 0, 'matmul_shared': 0}
    def charge(self, x, kind=None, key=None):
        self.ops += x
        if kind is not None:
            h = self.hist.setdefault(kind, {}); h[key] = h.get(key, 0) + 1
    def push(self): f = {}; self.frames.append(f); return f
    def pop(self): self.frames.pop()
    def live(self): return sum(p.length() for f in self.frames for p in f.values())
    def mark(self, v, where=None):
        if v > self.peak: self.peak = v; self.peak_where = where
    def scratch(self, w, where=None): self.mark(self.live() + w, where)

class Arith:
    """python-flint arithmetic with charges."""
    def __init__(self, pctx, C):
        self.p = pctx; self.C = C; self.zero = pctx([0]); self.one = pctx([1])
    @staticmethod
    def L(a): return a.length()
    def mul(self, a, b):
        ops, kind, scratch = product_charge(self.L(a), self.L(b))
        self.C.charge(ops, 'product_' + kind, '%d,%d' % (self.L(a), self.L(b))); self.C.n_products[kind] += 1; self.C.scratch(scratch, 'product')
        return a * b
    def add(self, a, b): self.C.charge(Fraction(9 * max(self.L(a), self.L(b)), 2), 'addsub', str(max(self.L(a), self.L(b)))); self.C.scratch(max(self.L(a), self.L(b)), 'add'); return a + b
    def sub(self, a, b): self.C.charge(Fraction(9 * max(self.L(a), self.L(b)), 2), 'addsub', str(max(self.L(a), self.L(b)))); self.C.scratch(max(self.L(a), self.L(b)), 'sub'); return a - b
    def shift_right(self, a, t):
        if t <= 0: return a
        self.C.charge(Fraction(5 * max(0, self.L(a) - t), 2), 'copy', str(max(0, self.L(a) - t))); self.C.scratch(max(0, self.L(a) - t), 'copy'); return a.right_shift(t)
    def view(self, a, t):
        """read-only pointer to the coefficients of a from index t on (LEAN): no copy, no charge, no words."""
        return a.right_shift(t) if t > 0 else a
    def divmod(self, a, b):
        n, m = a.degree(), b.degree(); assert m >= 0
        if n < m: self.C.charge(Fraction(5 * self.L(a), 2), 'copy', str(self.L(a))); return self.zero, a
        ops, kind = division_charge(n, m)
        self.C.charge(ops, 'division_' + kind, '%d,%d' % (n, m)); self.C.n_div[kind] += 1
        self.C.scratch((n + 1) + (n - m + 1) + (2 * ntt_len(2 * (n - m + 1)) if kind == 'newton' else 0), 'division')
        return divmod(a, b)
    def monic(self, a): self.C.charge(380 + Fraction(3 * self.L(a), 2), 'monic', str(self.L(a))); return a.monic()

def mat_apply(A, R, a, b):
    F = A.C.push()
    try:
        out = []
        for i in range(2):
            F['t0'] = A.mul(R[i][0], a); F['t1'] = A.mul(R[i][1], b)
            F['r%d' % i] = A.add(F['t0'], F['t1']); del F['t0'], F['t1']
        return F['r0'], F['r1']
    finally: A.C.pop()

def mat_apply_charge(A, R, a, b):
    ops = Fraction(0)
    for i in range(2):
        m = []
        for j, v in ((0, a), (1, b)):
            ops += product_charge(A.L(R[i][j]), A.L(v))[0]
            m.append(A.L(R[i][j]) + A.L(v) - 1 if A.L(R[i][j]) and A.L(v) else 0)
        ops += Fraction(9 * max(m), 2)
    return ops

def is_identity(A, R): return R[0][0] == A.one and R[1][1] == A.one and R[0][1].is_zero() and R[1][0].is_zero()

def matvec(A, R, a, b, owner=None, consume_R=False):
    """(a', b') = R (a, b), R = hgcd matrix computed from the top part of (a, b).
    owner = (frame, key_a, key_b): a, b are owned by that frame and are freed once copied into the transform buffers.
    consume_R: the caller's frame holds R under 'R..' and does not need it afterwards (R00 freed once loaded)."""
    C = A.C
    if not LEAN: return mat_apply(A, R, a, b)
    n0 = a.degree(); n_h = n0 - R[1][1].degree()           # degree relation: deg r_h = deg r0 - deg t_{h+1}
    N = wrap_len(n_h + 1)
    ls = [A.L(R[i][j]) for i in range(2) for j in range(2)]
    la, lb = A.L(a), A.L(b)
    assert max(ls) <= N, (ls, N)
    wrap = matvec_wrap_charge(la, lb, *ls, N)
    if wrap >= mat_apply_charge(A, R, a, b):
        return mat_apply(A, R, a, b)
    C.charge(wrap, 'matvec_wrap', '%d,%d,%d,%d,%d,%d,%d' % (la, lb, *ls, N)); C.n_lean['matvec_wrap'] += 1
    base = C.live()
    if owner is not None:
        C.mark(base + N, 'matvec_wrap load a'); base -= la
        C.mark(base + 2 * N, 'matvec_wrap load b'); base -= lb
    if consume_R: base -= ls[0]
    C.mark(base + 4 * N, 'matvec_wrap 4N')
    a2 = R[0][0] * a + R[0][1] * b; b2 = R[1][0] * a + R[1][1] * b
    # cyclic shortcut is exact iff both outputs have degree < N (asserted), and N was fixed in advance by n_h
    assert a2.degree() == n_h and a2.degree() < N and b2.degree() < n_h, (a2.degree(), n_h, b2.degree(), N)
    if owner is not None:
        F, ka, kb = owner; del F[ka], F[kb]
    return a2, b2

def mat_mul(A, S, R):
    F = A.C.push()
    try:
        out = [[None, None], [None, None]]
        for i in range(2):
            for j in range(2):
                F['t0'] = A.mul(S[i][0], R[0][j]); F['t1'] = A.mul(S[i][1], R[1][j])
                out[i][j] = F['o%d%d' % (i, j)] = A.add(F['t0'], F['t1']); del F['t0'], F['t1']
        return out
    finally: A.C.pop()

def mat_mul_lean(A, S, P):
    C = A.C
    s = [A.L(S[i][j]) for i in range(2) for j in range(2)]; pm = [A.L(P[i][j]) for i in range(2) for j in range(2)]
    if LEAN and is_identity(A, S): return P                    # second recursion made no step: S P = P
    if not (LEAN and SHARED_MATMUL): return mat_mul(A, S, P)
    mx = max([s[2 * i + l] + pm[2 * l + j] - 1 for i in range(2) for j in range(2) for l in range(2) if s[2 * i + l] and pm[2 * l + j]] + [1])
    N = wrap_len(mx)
    sh = matmul_shared_charge(s, pm, N)
    plain = Fraction(0)
    for i in range(2):
        for j in range(2):
            plain += product_charge(s[2 * i], pm[j])[0] + product_charge(s[2 * i + 1], pm[2 + j])[0]
            plain += Fraction(9 * max(s[2 * i] + pm[j] - 1 if s[2 * i] and pm[j] else 0, s[2 * i + 1] + pm[2 + j] - 1 if s[2 * i + 1] and pm[2 + j] else 0), 2)
    if sh >= plain: return mat_mul(A, S, P)
    C.charge(sh, 'matmul_shared', ','.join(map(str, s + pm + [N]))); C.n_lean['matmul_shared'] += 1
    out = [[S[i][0] * P[0][j] + S[i][1] * P[1][j] for j in range(2)] for i in range(2)]
    for i in range(2):
        for j in range(2): assert out[i][j].degree() < N
    base = C.live()
    C.mark(base + 6 * N, 'matmul_shared row 0')
    C.mark(base + 6 * N + A.L(out[0][0]) + A.L(out[0][1]), 'matmul_shared row 1')
    return out

def q_apply(A, q, R):
    """Q*R with Q = [[0,1],[1,-q]]"""
    F = A.C.push()
    try:
        u = []
        for j in range(2):
            F['t'] = A.mul(q, R[1][j]); F['u%d' % j] = A.sub(R[0][j], F['t']); del F['t']; u.append(F['u%d' % j])
        return [[R[1][0], R[1][1]], [u[0], u[1]]]
    finally: A.C.pop()

CUTOFF = 48    # degree-drop k below which the classical base case runs (chosen by a sweep of cutoffs 32..128)
FIRST_FRACTION = None   # optional larger first top-level reduction (memory lever at large degree)
TOP_FRACTION = 4   # top level reduces the degree by n0/TOP_FRACTION per hgcd call (memory/ops trade)

def identity(A): return [[A.one, A.zero], [A.zero, A.one]]

def hold_matrix(F, name, R):
    for i in range(2):
        for j in range(2): F['%s%d%d' % (name, i, j)] = R[i][j]
def drop_matrix(F, name):
    for i in range(2):
        for j in range(2): F.pop('%s%d%d' % (name, i, j), None)

def euclid_matrix(A, r0, r1, k):
    """classical base case. Frame slots 'x', 'y' hold the current pair only when owned by this frame
    (LEAN: the inputs are views of the caller's buffers and are not counted again)."""
    F = A.C.push()
    try:
        n0 = r0.degree(); R = identity(A)
        x, y = r0, r1
        if not LEAN: F['x'], F['y'] = x, y
        while not y.is_zero() and n0 - y.degree() <= k:
            F['q'], F['rem'] = A.divmod(x, y)
            R = q_apply(A, F['q'], R); hold_matrix(F, 'R', R); del F['q']
            F.pop('x', None)
            if 'y' in F: F['x'] = F.pop('y')
            x, y = y, F.pop('rem'); F['y'] = y
        return R
    finally: A.C.pop()

def hgcd(A, r0, r1, k):
    """R with R(r0,r1) = (r_h, r_{h+1}), h = max{j : deg r0 - deg r_j <= k}. r0, r1 are held by the caller."""
    C = A.C; n0 = r0.degree()
    if r1.is_zero() or k < n0 - r1.degree(): return identity(A)
    if k <= CUTOFF: return euclid_matrix(A, r0, r1, k)
    F = C.push()
    try:
        d = (k + 1) // 2; t = n0 - 2 * d
        if LEAN:
            R = hgcd(A, A.view(r0, t), A.view(r1, t), d); hold_matrix(F, 'R', R)
            if is_identity(A, R): a, b = r0, r1                        # views of the caller's buffers
            else: F['a'], F['b'] = a, b = matvec(A, R, r0, r1)
        else:
            F['r0s'] = A.shift_right(r0, t); F['r1s'] = A.shift_right(r1, t)
            R = hgcd(A, F['r0s'], F['r1s'], d); del F['r0s'], F['r1s']; hold_matrix(F, 'R', R)
            F['a'], F['b'] = a, b = mat_apply(A, R, r0, r1)
        if b.is_zero() or k < n0 - b.degree(): return R
        F['q'], F['c'] = A.divmod(a, b); F.pop('a', None)
        dstar = k - (n0 - b.degree()); t2 = b.degree() - 2 * dstar
        if LEAN:
            S = hgcd(A, A.view(b, t2), A.view(F['c'], t2), dstar); F.pop('b', None); del F['c']; hold_matrix(F, 'S', S)
        else:
            F['bs'] = A.shift_right(b, t2); F['cs'] = A.shift_right(F['c'], t2)
            S = hgcd(A, F['bs'], F['cs'], dstar); del F['bs'], F['cs'], F['b'], F['c']; hold_matrix(F, 'S', S)
        QR = q_apply(A, F['q'], R); del F['q']; drop_matrix(F, 'R'); hold_matrix(F, 'QR', QR)
        return mat_mul_lean(A, S, QR)
    finally: C.pop()

def fast_gcd(A, a, b):
    """monic gcd(a,b) with every operation charged; the top level only applies half-size matrices."""
    C = A.C; F = C.push()
    try:
        if a.degree() < b.degree(): a, b = b, a
        F['a'], F['b'] = a, b
        first = True
        while not F['b'].is_zero() and F['b'].degree() > CUTOFF:
            fr = FIRST_FRACTION if (first and FIRST_FRACTION) else TOP_FRACTION
            first = False
            n0 = F['a'].degree(); d = (n0 + fr - 1) // fr
            if LEAN:
                t = n0 - 2 * d
                R = hgcd(A, A.view(F['a'], t), A.view(F['b'], t), d); hold_matrix(F, 'R', R)
                if not is_identity(A, R):
                    a2, b2 = matvec(A, R, F['a'], F['b'], owner=(F, 'a', 'b'), consume_R=True)
                    drop_matrix(F, 'R'); F['a'], F['b'] = a2, b2
                drop_matrix(F, 'R')
            else:
                R = hgcd(A, F['a'], F['b'], d); hold_matrix(F, 'R', R)
                F['a2'], F['b2'] = mat_apply(A, R, F['a'], F['b']); drop_matrix(F, 'R')
                F['a'], F['b'] = F['a2'], F['b2']; del F['a2'], F['b2']
            if F['b'].is_zero(): break
            q, F['rem'] = A.divmod(F['a'], F['b']); F['a'], F['b'] = F['b'], F['rem']; del F['rem']
        while not F['b'].is_zero():
            q, F['rem'] = A.divmod(F['a'], F['b']); F['a'], F['b'] = F['b'], F['rem']; del F['rem']
        return A.monic(F['a'])
    finally: C.pop()

def make(p):
    pctx = fmpz_mod_poly_ctx(fmpz_mod_ctx(p)); return pctx, Arith(pctx, Counter())
```

### halfgcd_charge.py

```python
"""Standard-library reproduction of the gcd-stage charge from its trace histogram.
usage: python halfgcd_charge.py gcd_ledger_r1.json   (self-check: recomputed ops == ledger ops_exact)
Rules: see halfgcd.py / roots.py docstrings. Transform T from ntt.py (stdlib)."""
import json, sys
from fractions import Fraction
from ntt import T, nice_length

def ntt_len(m): return nice_length(max(m, 3))
def product_classical(m1, m2): return Fraction(4 * m1 * m2) + Fraction(m1 * m2, 2) + 2 * (m1 + m2 - 1)
def product_ntt(m1, m2):
    N = ntt_len(m1 + m2 - 1); return 3 * T(N) + 5 * N + 2 * (m1 + m2) + (N - m1) + (N - m2) + Fraction(N, 2)
def newton_inv(L):
    ops = Fraction(380); m = 1
    while m < L:
        m2 = min(2 * m, L); N = nice_length(max(m2, 3))
        ops += (m2 + N) + (m + N) + 5 * T(N) + 10 * N + 2 * (m2 - m) + (N - (m2 - m)) + 3 * (m2 - m); m = m2
    return ops
def load_ab(l, N): return Fraction(5 * min(l, N), 2) + Fraction(9 * max(0, l - N), 2) + Fraction(3 * max(0, N - l), 2)
def load_R(l, N): return Fraction(7 * l, 2) + Fraction(3 * (N - l), 2)
def load_S(l, N): return Fraction(5 * l, 2) + Fraction(3 * (N - l), 2)
def matvec_wrap(la, lb, l00, l01, l10, l11, N):
    """R (a, b) mod X^N - 1: a, b and each nonzero R entry transformed once, per row pointwise 9/2 N + 13/2 N
    for a second term, one inverse per nonzero row."""
    tot = load_ab(la, N) + load_ab(lb, N) + 2 * T(N)
    for l in (l00, l01, l10, l11):
        if l: tot += load_R(l, N) + T(N)
    for x, y in ((l00, l01), (l10, l11)):
        n = (x > 0) + (y > 0)
        if n: tot += Fraction(9 * N, 2) + (n - 1) * Fraction(13 * N, 2) + T(N)
    return tot
def matmul_shared(s00, s01, s10, s11, p00, p01, p10, p11, N):
    """S P (2x2) at linear length N: every nonzero entry transformed once, in-place 2x2 pointwise per row
    29/2 N, one inverse per nonzero output entry."""
    s = (s00, s01, s10, s11); pm = (p00, p01, p10, p11); tot = Fraction(0)
    for l in pm:
        if l: tot += load_R(l, N) + T(N)
    for l in s:
        if l: tot += load_S(l, N) + T(N)
    for i in range(2):
        tot += Fraction(29 * N, 2)
        for j in range(2):
            if (s[2 * i] and pm[j]) or (s[2 * i + 1] and pm[2 + j]): tot += T(N)
    return tot
def product_min(m1, m2):
    if m1 == 0 or m2 == 0: return Fraction(0)
    return min(product_classical(m1, m2), product_ntt(m1, m2))
def division_classical(n, m):
    L = n - m + 1; return Fraction(380 + L * (4 * (m + 1) + 2) + 2 * (n + 1)) + Fraction(L * (m + 1), 2) + Fraction(n + 1, 2)
def division_newton(n, m):
    L = n - m + 1
    return newton_inv(L) + product_min(L, L) + product_min(L, m + 1) + 4 * (m + 1) + Fraction(m + 1, 2) + 2 * (n + 1) + Fraction(n + 1, 2)
POP = bin((0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001 - 1) // 2).count('1')
def mulmod(d): return Fraction(4 * d * d + (d - 1) * (4 * d + 2)) + Fraction(d * d + (d - 1) * d, 2)
def mulx(d): return Fraction(4 * d + (d - 1) * (4 * d + 2)) + Fraction(d + (d - 1) * d, 2)

def charge_from_trace(hist):
    return sum(charge_by_kind(hist).values(), Fraction(0))

def charge_by_kind(hist):
    out = {}
    for kind, table in hist.items():
        total = Fraction(0)
        for key, cnt in table.items():
            k = [int(x) for x in key.split(',')] if key != '' else []
            if kind == 'product_classical': c = product_classical(*k)
            elif kind == 'product_ntt': c = product_ntt(*k)
            elif kind == 'product_zero': c = Fraction(0)
            elif kind == 'division_classical': c = division_classical(*k)
            elif kind == 'division_newton': c = division_newton(*k)
            elif kind == 'matvec_wrap': c = matvec_wrap(*k)
            elif kind == 'matmul_shared': c = matmul_shared(*k)
            elif kind == 'addsub': c = Fraction(9 * k[0], 2)
            elif kind == 'copy': c = Fraction(5 * k[0], 2)
            elif kind == 'monic': c = 380 + Fraction(3 * k[0], 2)
            elif kind == 'inversion': c = Fraction(380)
            elif kind == 'edf_draw': c = Fraction(1)
            elif kind == 'edf_powmod': c = Fraction(253 * mulmod(k[0]) + (POP - 1) * mulx(k[0]))
            elif kind == 'edf_constsub': c = Fraction(9 * k[0], 2)
            elif kind == 'root_linear': c = Fraction(1)
            else: raise ValueError(kind)
            total += c * cnt
        out[kind] = total
    return out

def gcd_overhead(hist):
    """Explicit charge for work the per-operation rules leave implicit (proof 5.2, last item):
    +N per transform product (1/2 loop on each of the two copy/pad loops), +2m per monic normalisation
    (load and store per coefficient), +5N per wrapped matrix-vector step and +10N per shared-transform
    matrix product (output compaction into coefficient-length buffers, 2.5 units per word), and +5 per
    recorded operation (degree scans and recursion bookkeeping)."""
    total = Fraction(0)
    for kind, table in hist.items():
        for key, cnt in table.items():
            k = [int(x) for x in key.split(',')] if key != '' else []
            if kind == 'product_ntt': c = Fraction(ntt_len(k[0] + k[1] - 1))
            elif kind == 'monic': c = Fraction(2 * k[0])
            elif kind == 'matvec_wrap': c = Fraction(5 * k[-1])
            elif kind == 'matmul_shared': c = Fraction(10 * k[-1])
            else: c = Fraction(0)
            total += (c + 5) * cnt
    return int(total) if total.denominator == 1 else int(total) + 1

if __name__ == '__main__':
    led = json.load(open(sys.argv[1]))
    tr = led['trace'] if 'trace' in led else json.load(open(sys.argv[2]))
    got = charge_from_trace(tr)
    print('recomputed', got, '| ledger ops', led['ops'], 'exact', led.get('ops_exact'))
    assert str(got) == led.get('ops_exact', str(led['ops'])), 'MISMATCH'
    print('SELF-CHECK OK; histogram JSON bytes:', len(json.dumps(tr, separators=(',', ':'))))


# ---------------------------------------------------------------------------------------------------
# Strict re-pricing of the same executed schedule (histogram) under the convention of the executed-C
# entries: field op 1; load/store 1 + 1 address operation = 2; a loop over e elements unrolled by 8 costs
# LP(e) = 3 ceil(e/8) + 2; non-unrolled loop iterations 3 + 2 on exit; registers (<= 16 words) not loads.
# Each formula below restates the loose rule's work item by item (same loads, stores, arithmetic,
# same product/division choices) with these prices.
from ntt import T_S, LP


def _pst(e, arith, loads, stores):
    """streaming pass over e elements: per element arith + loads + stores."""
    return e * (arith + 2 * (loads + stores)) + LP(e)


def s_product_classical(m1, m2):
    out = m1 + m2 - 1
    tot = Fraction(6 * m1 * m2) + out * 2 + 3 * out + 2          # terms (2 loads, mul, add), output stores, outer loop
    for k in range(out):
        e = min(k, m1 - 1, m2 - 1, out - 1 - k) + 1
        tot += LP(e)
    return tot


def s_product_ntt(m1, m2):
    N = ntt_len(m1 + m2 - 1)
    return 3 * T_S(N) + _pst(N, 2, 2, 1) + 2 * (m1 + N) + LP(N) + 2 * (m2 + N) + LP(N)


def s_product_choice(m1, m2):
    """the executed choice (by the loose rule), priced strictly."""
    if m1 == 0 or m2 == 0:
        return Fraction(0)
    return s_product_classical(m1, m2) if product_classical(m1, m2) <= product_ntt(m1, m2) else s_product_ntt(m1, m2)


def s_newton_inv(L):
    ops = Fraction(380); m = 1
    while m < L:
        m2 = min(2 * m, L); N = nice_length(max(m2, 3)); d = m2 - m
        ops += 2 * (m2 + N) + LP(N) + 2 * (m + N) + LP(N) + 5 * T_S(N) + 2 * _pst(N, 2, 2, 1) \
            + 4 * d + LP(d) + 2 * (N - d) + LP(N - d) + 5 * d + LP(d)
        m = m2
    return ops


def s_division_classical(n, m):
    L = n - m + 1
    return Fraction(380) + _pst(n + 1, 0, 1, 1) + L * (5 + 8 * (m + 1) + LP(m + 1) + 3) + 2


def s_division_newton(n, m):
    L = n - m + 1
    return s_newton_inv(L) + s_product_choice(L, L) + s_product_choice(L, m + 1) + _pst(m + 1, 1, 2, 1) + _pst(n + 1, 0, 1, 1)


def _s_load_ab(l, N):
    c, f, pd = min(l, N), max(0, l - N), max(0, N - l)
    return 4 * c + LP(c) + 7 * f + LP(f) + 2 * pd + LP(pd)


def _s_load_R(l, N):
    return 5 * l + LP(l) + 2 * (N - l) + LP(N - l)


def _s_load_S(l, N):
    return 4 * l + LP(l) + 2 * (N - l) + LP(N - l)


def s_matvec_wrap(la, lb, l00, l01, l10, l11, N):
    tot = _s_load_ab(la, N) + _s_load_ab(lb, N) + 2 * T_S(N)
    for l in (l00, l01, l10, l11):
        if l: tot += _s_load_R(l, N) + T_S(N)
    for x, y in ((l00, l01), (l10, l11)):
        t = (x > 0) + (y > 0)
        if t: tot += 7 * N + LP(N) + (t - 1) * (10 * N + LP(N)) + T_S(N)
    return tot


def s_matmul_shared(s00, s01, s10, s11, p00, p01, p10, p11, N):
    s = (s00, s01, s10, s11); pm = (p00, p01, p10, p11); tot = Fraction(0)
    for l in pm:
        if l: tot += _s_load_R(l, N) + T_S(N)
    for l in s:
        if l: tot += _s_load_S(l, N) + T_S(N)
    for i in range(2):
        tot += 22 * N + LP(N)
        for j in range(2):
            if (s[2 * i] and pm[j]) or (s[2 * i + 1] and pm[2 + j]): tot += T_S(N)
    return tot


def s_mulmod(d):
    out = 2 * d - 1
    prod = Fraction(6 * d * d) + out * 5 + 2 + sum(LP(min(k, d - 1, out - 1 - k) + 1) for k in range(out))
    red = (d - 1) * (2 + 8 * d + LP(d) + 3) + 2
    return prod + red


def s_mulx(d):
    return 8 * (d + 1) + LP(d + 1) + 2 + 8 * d + LP(d)


def charge_by_kind_strict(hist):
    out = {}
    for kind, table in hist.items():
        total = Fraction(0)
        for key, cnt in table.items():
            k = [int(x) for x in key.split(',')] if key != '' else []
            if kind == 'product_classical': c = s_product_classical(*k)
            elif kind == 'product_ntt': c = s_product_ntt(*k)
            elif kind == 'product_zero': c = Fraction(0)
            elif kind == 'division_classical': c = s_division_classical(*k)
            elif kind == 'division_newton': c = s_division_newton(*k)
            elif kind == 'matvec_wrap': c = s_matvec_wrap(*k)
            elif kind == 'matmul_shared': c = s_matmul_shared(*k)
            elif kind == 'addsub': c = 7 * k[0] + LP(k[0])
            elif kind == 'copy': c = 4 * k[0] + LP(k[0])
            elif kind == 'monic': c = 380 + 5 * k[0] + LP(k[0])
            elif kind == 'inversion': c = Fraction(380)
            elif kind == 'edf_draw': c = Fraction(1)
            elif kind == 'edf_powmod': c = 253 * s_mulmod(k[0]) + (POP - 1) * s_mulx(k[0])
            elif kind == 'edf_constsub': c = 7 * k[0] + LP(k[0])
            elif kind == 'root_linear': c = Fraction(3)
            else: raise ValueError(kind)
            total += c * cnt
        out[kind] = total
    return out


def gcd_overhead_strict(hist):
    """strict counterpart of gcd_overhead: output compaction of wrapped steps (two outputs) and shared
    products (four entries) at load + store per word with their loops, and 10 per recorded operation for
    degree scans and recursion bookkeeping (the loose rule's 5, doubled). The loose +N per transform product
    and +2m per monic are inside the strict formulas above."""
    total = Fraction(0)
    for kind, table in hist.items():
        for key, cnt in table.items():
            k = [int(x) for x in key.split(',')] if key != '' else []
            if kind == 'matvec_wrap': c = 2 * (4 * k[-1] + LP(k[-1]))
            elif kind == 'matmul_shared': c = 4 * (4 * k[-1] + LP(k[-1]))
            else: c = Fraction(0)
            total += (c + 10) * cnt
    return total


def charge_strict(hist):
    return sum(charge_by_kind_strict(hist).values(), Fraction(0)) + gcd_overhead_strict(hist)
```

### gcd_mock.py

```python
"""gcd_mock.py - the half-gcd schedule of halfgcd.py on a NORMAL remainder sequence, run on degrees only.

A normal remainder sequence of (a, b), deg a = m, deg b = m - 1, has every quotient of degree 1 and every
remainder one degree lower than its divisor, down to degree 0 (gcd 1). For such a sequence every degree in the
half-gcd recursion (views, cofactor matrices, wrapped matrix-vector outputs, divisions) is determined by m, so
the executed schedule, its histogram and its memory model are functions of m alone. This module runs the
unchanged control flow of halfgcd.fast_gcd on polynomials that carry only a degree (MockPoly), with the
cancellations of the remainder sequence stated explicitly (matrix-vector outputs of degree n_h and n_h - 1),
and returns the histogram and the peak in the same format as gcd_stage.

Validation (self-test): on pseudo-random instances of several degrees, where the executed sequence is normal,
the mock histogram and peak equal those of the executed counted run exactly.
Usage: python gcd_mock.py <m> <top_fraction>      (prints strict and loose charges and the peak)
       python gcd_mock.py --selftest
"""
import sys, json, copy
from fractions import Fraction
import halfgcd
from halfgcd import Arith, Counter, fast_gcd, product_charge, ntt_len, matvec_wrap_charge, mat_apply_charge, wrap_len


class MockPoly:
    __slots__ = ('d',)

    def __init__(self, d):
        self.d = d

    def degree(self): return self.d
    def length(self): return self.d + 1
    def is_zero(self): return self.d < 0
    def right_shift(self, t): return MockPoly(max(self.d - t, -1))
    def monic(self): return MockPoly(self.d)

    def __mul__(self, o):
        return MockPoly(-1 if self.d < 0 or o.d < 0 else self.d + o.d)

    def __add__(self, o): return MockPoly(max(self.d, o.d))
    __sub__ = __add__

    def __divmod__(self, o):
        """normal sequence: quotient of degree deg a - deg b, remainder of degree deg b - 1."""
        assert o.d >= 0 and self.d >= o.d
        return MockPoly(self.d - o.d), MockPoly(o.d - 1)


class MockArith(Arith):
    def __init__(self, C):
        self.p = None; self.C = C; self.zero = MockPoly(-1); self.one = MockPoly(0)


def _matvec(A, R, a, b, owner=None, consume_R=False):
    C = A.C
    n0 = a.degree(); n_h = n0 - R[1][1].degree()
    if not halfgcd.LEAN:
        return _mat_apply(A, R, a, b)
    N = wrap_len(n_h + 1)
    ls = [A.L(R[i][j]) for i in range(2) for j in range(2)]
    la, lb = A.L(a), A.L(b)
    assert max(ls) <= N
    wrap = matvec_wrap_charge(la, lb, *ls, N)
    if wrap >= mat_apply_charge(A, R, a, b):
        return _mat_apply(A, R, a, b)
    C.charge(wrap, 'matvec_wrap', '%d,%d,%d,%d,%d,%d,%d' % (la, lb, *ls, N)); C.n_lean['matvec_wrap'] += 1
    base = C.live()
    if owner is not None:
        C.mark(base + N, 'matvec_wrap load a'); base -= la
        C.mark(base + 2 * N, 'matvec_wrap load b'); base -= lb
    if consume_R: base -= ls[0]
    C.mark(base + 4 * N, 'matvec_wrap 4N')
    if owner is not None:
        F, ka, kb = owner; del F[ka], F[kb]
    return MockPoly(n_h), MockPoly(n_h - 1)


def _mat_apply(A, R, a, b):
    n_h = a.degree() - R[1][1].degree()
    F = A.C.push()
    try:
        for i in range(2):
            F['t0'] = A.mul(R[i][0], a); F['t1'] = A.mul(R[i][1], b)
            F['r%d' % i] = A.add(F['t0'], F['t1']); del F['t0'], F['t1']
        return MockPoly(n_h), MockPoly(n_h - 1)
    finally: A.C.pop()


EDF_CAP = 64      # equal-degree splitting draws per call (a call failing 64 times stops the trial; prob <= 2^-64 per call)


EXPCTL = 3 * 254   # bit loop of the exponentiation by (p-1)/2: shift, mask test and branch per exponent bit


def roots_bound_strict(d):
    """strict upper bound of the root stage of roots.py on a split polynomial of degree d <= 16 with at most EDF_CAP
    draws per call: at most 2d - 1 calls, each draw = shift (1) + (X + c)^((p-1)/2) mod G + constant subtraction +
    classical Euclid (at most d divisions of degree <= d) + monic, each call one exact division; 3 per linear root."""
    from halfgcd_charge import s_mulmod, s_mulx, s_division_classical, POP
    from ntt import LP
    if d <= 1:
        return Fraction(3 * d)
    draw = EXPCTL + 1 + 253 * s_mulmod(d) + (POP - 1) * s_mulx(d) + 7 * d + LP(d) + d * s_division_classical(d, d - 1) + 380 + 5 * d + LP(d)
    return (2 * d - 1) * (EDF_CAP * draw + s_division_classical(d, 1)) + 3 * d


def _merge(dst, src, times=1):
    for kind, table in src.items():
        d = dst.setdefault(kind, {})
        for key, cnt in table.items():
            d[key] = d.get(key, 0) + cnt * times


class _Node:
    __slots__ = ('own', 'ops', 'children')

    def __init__(self):
        self.own = {}; self.ops = Fraction(0); self.children = {}


def _memo_hgcd(orig, C):
    """hgcd on a normal sequence depends only on (deg r0, deg r1, k). Each distinct call is executed once; repeated calls
    are recorded as a multiplicity on the caller's node, and the histogram is expanded once at the end (expand()).
    The memory peak of a repeated call is replayed relative to the live words at its entry."""
    memo = {}
    root = _Node()
    stack = [root]
    orig_charge = C.charge

    def charge(x, kind=None, key=None):
        node = stack[-1]
        node.ops += x
        if kind is not None:
            t = node.own.setdefault(kind, {}); t[key] = t.get(key, 0) + 1
    C.charge = charge

    def hgcd(A, r0, r1, k):
        key = (r0.degree(), r1.degree(), k)
        base = C.live()
        parent = stack[-1]
        if key in memo:
            rel, R = memo[key][1], memo[key][2]
            parent.children[key] = parent.children.get(key, 0) + 1
            C.mark(base + rel, 'memo')
            return R
        node = _Node(); stack.append(node)
        outer_peak, outer_where = C.peak, C.peak_where
        C.peak = base
        R = orig(A, r0, r1, k)
        rel = C.peak - base
        stack.pop()
        memo[key] = (node, rel, R)
        parent.children[key] = parent.children.get(key, 0) + 1
        C.peak, C.peak_where = outer_peak, outer_where
        C.mark(base + rel, 'memo-first')
        return R

    def expand():
        tot = {}
        def total(key):
            if key in tot:
                return tot[key]
            node = memo[key][0]
            h = {}; _merge(h, node.own); ops = node.ops
            for ck, cnt in node.children.items():
                ch, cops = total(ck)
                _merge(h, ch, cnt); ops += cops * cnt
            tot[key] = (h, ops)
            return tot[key]
        import sys as _s
        _s.setrecursionlimit(100000)
        h = {}; _merge(h, root.own); ops = root.ops
        for ck, cnt in root.children.items():
            ch, cops = total(ck)
            _merge(h, ch, cnt); ops += cops * cnt
        C.charge = orig_charge
        return h, ops
    return hgcd, expand


def run_mock(m, top_fraction, cutoff=48, memo=True, pow2=False, first=None):
    halfgcd.FIRST_FRACTION = first; halfgcd.POW2 = pow2; halfgcd.CUTOFF = cutoff; halfgcd.TOP_FRACTION = top_fraction; halfgcd.LEAN = True; halfgcd.SHARED_MATMUL = True
    saved = (halfgcd.matvec, halfgcd.mat_apply, halfgcd.hgcd)
    halfgcd.matvec, halfgcd.mat_apply = _matvec, _mat_apply
    A = MockArith(Counter())
    if memo:
        halfgcd.hgcd, expand = _memo_hgcd(saved[2], A.C)
    try:
        g = fast_gcd(A, MockPoly(m), MockPoly(m - 1))
        assert g.degree() == 0
        if memo:
            h, ops = expand()
            return {'ops': ops, 'peak_words': int(A.C.peak), 'trace': json.loads(json.dumps(h))}
        return {'ops': A.C.ops, 'peak_words': int(A.C.peak), 'trace': json.loads(json.dumps(A.C.hist))}
    finally:
        halfgcd.matvec, halfgcd.mat_apply, halfgcd.hgcd = saved


def _selftest(pow2=False):
    import hashlib
    from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
    from ntt import P
    from gcd_stage import gcd_stage
    from halfgcd_charge import charge_from_trace, gcd_overhead, charge_strict
    pctx = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)); X = pctx.gen()
    for m, fr in (((300, 4), (1000, 12), (5000, 12), (39062, 12), (39062, 4)) if not pow2 else ((300, 12), (1000, 12), (5000, 12), (39062, 12))):
        co = [int.from_bytes(hashlib.sha256(f'poseidon_mage mock test {m} {i}'.encode()).digest(), 'little') % P for i in range(m)] + [1]
        g = pctx(co)
        hb = pctx([int.from_bytes(hashlib.sha256(f'poseidon_mage mock test b {m} {i}'.encode()).digest(), 'little') % P for i in range(m)])
        Y1 = X.pow_mod((P - 1) // 2, g) - 1
        mk = run_mock(m, fr, pow2=pow2)
        ml, ms = charge_from_trace(mk['trace']) + gcd_overhead(mk['trace']), charge_strict(mk['trace'])
        for name, b in (('random b', hb), ('S^((p-1)/2) - 1', Y1)):
            G, rts, led = gcd_stage(g, b, 1, cutoff=48, top_fraction=fr, pow2=pow2)
            h = led['trace']
            el, es = charge_from_trace(h) + gcd_overhead(h), charge_strict(h)
            line = (f'm={m} n0/{fr} pow2={pow2} b={name}: deg G={G.degree()} executed strict {float(es):.6g} peak {led["peak_words"]} | '
                    f'mock strict {float(ms):.6g} peak {mk["peak_words"]}')
            if G.degree() == 0:
                same = mk['trace'] == {k: v for k, v in h.items() if k != 'root_linear'} and mk['peak_words'] == led['peak_words']
                print(line + f' | histograms equal: {same}', flush=True); assert same
            else:
                rb = roots_bound_strict(G.degree())
                print(line + f' | executed <= mock + roots bound ({float(rb):.4g}): {es <= ms + rb}', flush=True)
                assert es <= ms + rb and led['peak_words'] <= mk['peak_words']


def _selftest_degG(pow2=True):
    """instances with prescribed squares among the roots of g: g = prod_{i<k} (X - s_i^2) * h, h pseudo-random of degree
    m - k, b = S^((p-1)/2) - 1 mod g; deg G >= k. Checks executed charge <= mock + roots bound and executed peak <= mock peak."""
    import hashlib
    from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
    from ntt import P
    from gcd_stage import gcd_stage
    from halfgcd_charge import charge_strict
    pctx = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)); X = pctx.gen()
    H = lambda s: int.from_bytes(hashlib.sha256(s.encode()).digest(), 'little') % P
    for m in (300, 1000, 5000):
        mk = run_mock(m, 12, pow2=pow2)
        ms = charge_strict(mk['trace'])
        for k in (3, 4, 5, 6, 8):
            g = pctx([H(f'poseidon_mage degG test h {m} {k} {i}') for i in range(m - k)] + [1])
            for i in range(k):
                g = g * (X - H(f'poseidon_mage degG test s {m} {k} {i}') ** 2)
            Y1 = X.pow_mod((P - 1) // 2, g) - 1
            G, rts, led = gcd_stage(g, Y1, 1, cutoff=48, top_fraction=12, pow2=pow2)
            es = charge_strict(led['trace'])
            rb = roots_bound_strict(G.degree()) if G.degree() <= 16 else None
            ok = rb is not None and es <= ms + rb and led['peak_words'] <= mk['peak_words']
            print(f'm={m} n0/12 pow2={pow2} prescribed square roots {k}: deg G={G.degree()} executed strict {float(es):.6g} peak '
                  f'{led["peak_words"]} | mock strict {float(ms):.6g} peak {mk["peak_words"]} | executed <= mock + roots bound '
                  f'({float(rb):.4g}) and peak <= mock peak: {ok}', flush=True)
            assert ok


if __name__ == '__main__':
    if sys.argv[1] == '--selftest-degG':
        _selftest_degG()
    elif sys.argv[1] == '--selftest':
        _selftest()
    elif sys.argv[1] == '--selftest-pow2':
        _selftest(pow2=True)
    else:
        from halfgcd_charge import charge_from_trace, gcd_overhead, charge_strict
        m, fr = int(sys.argv[1]), int(sys.argv[2])
        mk = run_mock(m, fr)
        h = mk['trace']
        print(json.dumps({'m': m, 'top_fraction': fr, 'loose': float(charge_from_trace(h) + gcd_overhead(h)),
                          'strict': float(charge_strict(h)), 'peak_words': mk['peak_words']}))
```

### gcd_stage.py

```python
"""gcd_stage(q, hX, r) -> (g, roots, ledger). q monic of degree D; hX = (X^p mod q) - X; r = round count
(labels the preregistered EDF stream). ledger: 'ops' (int, gcd + roots), 'ops_exact' (str Fraction),
'peak_words', 'trace' (JSON histogram keyed by (kind, sizes)), and the breakdown."""
import json
import halfgcd
from halfgcd import Arith, Counter, fast_gcd
from roots import find_roots

def gcd_stage(q, hX, r, cutoff=None, top_fraction=None, lean=None, shared_matmul=None, pow2=False):
    halfgcd.POW2 = pow2
    if lean is not None: halfgcd.LEAN = lean
    if shared_matmul is not None: halfgcd.SHARED_MATMUL = shared_matmul
    if cutoff is not None: halfgcd.CUTOFF = cutoff
    if top_fraction is not None: halfgcd.TOP_FRACTION = top_fraction
    pctx = q.context()
    A = Arith(pctx, Counter())
    g = fast_gcd(A, q, hX)
    gcd_ops = A.C.ops; gp = dict(A.C.n_products); gd = dict(A.C.n_div)
    import copy; hist0 = copy.deepcopy(A.C.hist)
    def diff(kind): return sum(A.C.hist.get(kind, {}).values()) - sum(hist0.get(kind, {}).values())
    rts = find_roots(g, r, pctx, A.C)
    total = A.C.ops
    return g, rts, {
        'ops': int(total) if total.denominator == 1 else int(total) + 1, 'ops_exact': str(total),
        'peak_words': int(A.C.peak), 'gcd_degree': g.degree(), 'roots': [str(x) for x in rts],
        'cutoff': halfgcd.CUTOFF, 'top_fraction': halfgcd.TOP_FRACTION,
        'gcd_ops': str(gcd_ops), 'roots_ops': str(total - gcd_ops), 'roots_draws': getattr(A.C, 'draws', 0),
        'gcd_products': gp, 'gcd_divisions': gd, 'gcd_lean': dict(A.C.n_lean), 'lean': halfgcd.LEAN,
        'shared_matmul': halfgcd.SHARED_MATMUL, 'peak_where': A.C.peak_where,
        'roots_divisions': {'classical': diff('division_classical'), 'newton': diff('division_newton')},
        'roots_products': {k: A.C.n_products[k] - gp[k] for k in gp}, 'roots_monic': diff('monic'), 'roots_powmod': diff('edf_powmod'),
        'trace': json.loads(json.dumps(A.C.hist)),
    }
```

### roots.py

```python
"""Roots in F_p of a fully-split polynomial g (deg d <= 16) by equal-degree splitting,
charged with schoolbook arithmetic on polynomials of degree < d.

Charges (every item 1 op):
  mulmod(d): schoolbook product of two length-d polys 4*d*d (load, load, mul, add/store)
             + reduction of a length-(2d-1) poly modulo monic g: (d-1)*(4*d+2)
             + loop control 1/2 per inner iteration: (d*d + (d-1)*d)/2; add/sub 4d + d/2; monic 380 + m + m/2
  squaring charged as mulmod (conservative). Shifted exponentiation (X+c)^((p-1)/2) mod g:
  253 squarings + popcount((p-1)/2)-1 multiplications by (X+c) (each charged 4*d + reduction).
  gcd of two degree-<d polynomials: classical Euclid, each division charged as halfgcd.division_charge.
  shift draw: 1 op (c_n = n + 1).
Deterministic: shifts are c_n = n + 1, n = 0,1,2,... (no hash).
"""
from fractions import Fraction
from halfgcd import division_charge
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
E = (P - 1) // 2
POP = bin(E).count('1')

class RootCounter:
    """standalone counter (the driver passes the halfgcd Counter instead so one histogram holds both)"""
    def __init__(self): self.ops = 0; self.draws = 0; self.hist = {}
    def charge(self, x, kind=None, key=None):
        self.ops += x
        if kind is not None:
            h = self.hist.setdefault(kind, {}); h[key] = h.get(key, 0) + 1

def mulmod_charge(d): return Fraction(4 * d * d + (d - 1) * (4 * d + 2)) + Fraction(d * d + (d - 1) * d, 2)
def mulx_charge(d): return Fraction(4 * d + (d - 1) * (4 * d + 2)) + Fraction(d + (d - 1) * d, 2)
def powmod_shift_charge(d): return 253 * mulmod_charge(d) + (POP - 1) * mulx_charge(d)

def find_roots(g, r, pctx, C: RootCounter, stream_index=None):
    """g monic, splits completely over F_p (a gcd with X^p - X). Returns sorted list of int roots."""
    if stream_index is None: stream_index = [0]
    d = g.degree()
    X = pctx.gen()
    if d == 0: return []
    if d == 1:
        C.charge(1, 'root_linear', ''); return [int(-g[0])]
    if d == 2:
        # quadratic: roots via the EDF below as well (keeps one method); fallthrough
        pass
    while True:
        n = stream_index[0]; stream_index[0] += 1
        c = n + 1
        C.charge(1, 'edf_draw', ''); C.draws = getattr(C, 'draws', 0) + 1
        # h = (X + c)^E mod g
        h = (X + pctx([c])).pow_mod(E, g); C.charge(powmod_shift_charge(d), 'edf_powmod', str(d))
        u = (h - pctx([1])).gcd(g); C.charge(Fraction(9 * d, 2), 'edf_constsub', str(d))
        # Euclid charge for gcd of (g, h-1): simulate degree sequence with real division charges
        a, b = g, (h - pctx([1]))
        if b.is_zero(): continue
        while not b.is_zero():
            if a.degree() < b.degree(): a, b = b, a; continue
            ops, kind = division_charge(a.degree(), b.degree()); C.charge(ops, 'division_' + kind, '%d,%d' % (a.degree(), b.degree()))
            a, b = b, a % b
        C.charge(380 + Fraction(3 * (a.degree() + 1), 2), 'monic', str(a.degree() + 1))
        if 0 < u.degree() < d:
            v = g // u; dc, dk = division_charge(d, u.degree()); C.charge(dc, 'division_' + dk, '%d,%d' % (d, u.degree()))
            return sorted(find_roots(u.monic(), r, pctx, C, stream_index) + find_roots(v.monic(), r, pctx, C, stream_index))

if __name__ == '__main__':
    import random
    from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
    pctx = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)); X = pctx.gen(); rnd = random.Random(5)
    for d in (1, 2, 3, 4, 5, 8, 12, 16):
        for _ in range(3):
            rts = sorted({rnd.randrange(P) for _ in range(d)})
            g = pctx([1])
            for s in rts: g = g * (X - pctx([s]))
            C = RootCounter()
            got = find_roots(g, 1, pctx, C)
            assert got == rts, (d, got, rts)
            print(f"d={len(rts)}: ok ops={C.ops:.4g} draws={C.draws}")
    print("roots ALL OK")
```

### kc_stats.py

```python
"""kc_stats.py <r> <line k> <first centre> <count> : k(c) = number of nonzero-square roots of g_c for consecutive centres.
Evidence for the one-centre premise (fraction of centres with 1 <= k(c) <= 16). Builds g_c by the counted build
(2n line evaluations, interpolation), then FLINT: Y = S^((p-1)/2) mod g_c, G = gcd(g_c, Y - 1), k(c) = deg G.
Prints one JSON line per centre."""
import sys, json, time
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
from ntt import P, Counter, ntt_inverse, mont_length
from attack_mont import Target, build_G1, lead_coefficient

r, k, c0, cnt = (int(x) for x in sys.argv[1:5])
t = Target('../../pareto/orchard-pallas-constants.json', r, k=k)
D = 5 ** (6 + r); m = (D - 1) // 2; n = mont_length(m + 1)
aD = lead_coefficient(t)
pctx = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)); X = pctx.gen()
invn = pow(n, P - 2, P)
for c in range(c0, c0 + cnt):
    t0 = time.time()
    G1 = build_G1(t, c, n, aD, Counter())
    ntt_inverse(G1, Counter())
    g = pctx([x * invn % P for x in G1[:m + 1]])
    assert int(g[m]) == 1
    Y = X.pow_mod((P - 1) // 2, g)
    G = g.gcd(Y - 1)
    print(json.dumps({'r': r, 'line_k': k, 'c': c, 'k_c': G.degree(), 's': round(time.time() - t0, 1)}), flush=True)
```

### mk_hone_exp.py

```python
"""mk_hone_exp.py <out.py>: embed the pinned constants into hone_layers_src.py."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, '..', '..', 'pareto', 'orchard-pallas-constants.json')))
src = open(os.path.join(HERE, 'hone_layers_src.py'), encoding='utf-8').read()
emb = json.dumps({'round_constants': C['round_constants'][:8], 'mds': C['mds']})
assert 'CONST = None' in src
src = src.replace('CONST = None   # replaced by the generator: {\'round_constants\': [...], \'mds\': [...]}', 'CONST = ' + emb + '   # rounds 0..7 of the pinned constants')
assert 'CONST = None' not in src
open(sys.argv[1], 'w', encoding='utf-8', newline='\n').write(src)
print(sys.argv[1], len(src.encode()))
```

### hone_layers_src.py

```python
"""hone_layers.py - organizer experiment (python-message-pairs-v1) bearing on premise H-ONE.

The line of proof Section 1 (round-1 S-box input of lane 0 constant). F_L(T') = lane 0 of the state after rounds 2..(1 + L)
of the target permutation, started from the affine state after round 1 (L = 2: rounds 2, 3, degree 25, m = 12;
L = 3: adds partial round 4, degree 125, m = 62). For each organizer seed, a centre c is drawn uniformly from F_p
(rejection sampling of 255-bit words derived from SHA-256(seed)), g_c is the monic odd part of F_L about c (degree m), and
k(c) = deg gcd(g_c, S^((p-1)/2) - 1) is computed exactly (Kronecker-packed products over F_p, reduction modulo g_c by a
precomputed reciprocal of its reversal). To stay well inside the time limit the work is split over experiments that share
this program: 'hone-layers2a', '2b', '2c' compute L = 2 for the trials of index 0, 1, 2 mod 3 respectively (all trials
together), and 'hone-layers3a', '3b', '3c' compute L = 3 for trial indices 0-5, 6-11 and 12-17; every other trial is
reported as skipped. Experiments with a suffix '-rep2', '-rep3', '-rep4' are pre-declared replicates: the same computation on the fresh
organizer seeds that a different experiment id receives. No message pair is claimed: every trial returns null
messages, and k(c) is reported as an observation (H-ONE asks P(1 <= k(c) <= 16) to be at least the premise value of the package; the hyperoctahedral law gives
0.39347). Each computed trial also reports `normal` (bearing on premise H-NORMAL): 1 if the remainder sequence of
(g_c, Y - 1) is normal down to deg G, that is deg(Y - 1) = m - 1 and every Euclid step lowers the degree by exactly 1 until
the remainder is 0, else 0; and `max_drop`, the largest degree drop seen.
"""
import sys, json, hashlib
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
E = (P - 1) // 2
E5 = pow(5, -1, P - 1)
inv = lambda x: pow(x % P, P - 2, P)
CONST = None   # replaced by the generator: {'round_constants': [...], 'mds': [...]}


SLOT = 65   # bytes per Kronecker slot: 520 bits > log2(126 * p^2) = 515.0, enough for every product here (degree <= 125)


def pack(a):
    return int.from_bytes(b''.join(x.to_bytes(SLOT, 'little') for x in a), 'little')


def unpack(C, n):
    raw = (C & ((1 << (8 * SLOT * n)) - 1)).to_bytes(n * SLOT, 'little')
    return [int.from_bytes(raw[i * SLOT:(i + 1) * SLOT], 'little') % P for i in range(n)]


def pmul(a, b):
    """product of coefficient lists (low degree first), Kronecker packing with 520-bit slots (SLOT bytes)."""
    if not a or not b:
        return []
    if a is b:
        A = pack(a); return unpack(A * A, 2 * len(a) - 1)
    return unpack(pack(a) * pack(b), len(a) + len(b) - 1)


def pmod(a, g):
    """a mod monic g."""
    a = list(a)
    dg = len(g) - 1
    for i in range(len(a) - 1, dg - 1, -1):
        c = a[i]
        if c:
            for j in range(dg + 1):
                a[i - dg + j] = (a[i - dg + j] - c * g[j]) % P
    a = a[:dg]
    while a and a[-1] == 0:
        a.pop()
    return a


def padd(a, b):
    n = max(len(a), len(b))
    out = [((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % P for i in range(n)]
    while out and out[-1] == 0:
        out.pop()
    return out


def pscal(a, c):
    return [x * c % P for x in a]


def pgcd_deg(a, b):
    """(deg gcd, normal flag, largest degree drop) of the remainder sequence a, b, a mod b, ..."""
    degs = [len(a) - 1, len(b) - 1]
    while b:
        lb = inv(b[-1])
        b = pscal(b, lb)
        a = pmod(a, b) if len(a) >= len(b) else a
        a, b = b, a
        if b:
            degs.append(len(b) - 1)
    drops = [degs[i] - degs[i + 1] for i in range(len(degs) - 1)]
    return len(a) - 1, (1 if all(x == 1 for x in drops) else 0), max(drops) if drops else 0


def reducer(g):
    """reduction modulo monic g (degree d) of polynomials of degree <= 2d - 2, by the reciprocal of the reversal of g."""
    d = len(g) - 1
    rg = g[::-1]
    R = [1]                                   # rg^-1 mod x^(d-1), rg[0] = 1
    for i in range(1, max(d - 1, 1)):
        s = 0
        for j in range(1, min(i, d) + 1):
            s += rg[j] * R[i - j]
        R.append((-s) % P)

    PR, PG = pack(R), pack(g)
    MASK = (1 << (8 * SLOT * (d - 1))) - 1

    def red(a):
        if len(a) <= d:
            return a
        a = a + [0] * (2 * d - 1 - len(a))
        qr = unpack((pack(a[::-1][:d - 1]) * PR) & MASK, d - 1)
        q = qr[::-1]
        qg = unpack(pack(q) * PG, d)
        out = [(a[i] - qg[i]) % P for i in range(d)]
        while out and out[-1] == 0:
            out.pop()
        return out
    return red


def line_poly(L):
    RC = [[int(x, 16) for x in row] for row in CONST['round_constants']]
    M = [[int(x, 16) for x in row] for row in CONST['mds']]
    CAP = 1 << 65; k = 0; i, j = 1, 2
    K5 = pow((CAP + RC[0][2]) % P, 5, P)
    mu5 = (-M[k][0] * inv(M[k][1])) % P
    a, b, e = M[i][0], M[i][1], (-(M[i][2] * K5 + RC[1][i])) % P
    c, d, f = M[j][0], M[j][1], (-(M[j][2] * K5 + RC[1][j])) % P
    det = (a * d - b * c) % P; di = inv(det)
    A0 = ((e * d - b * f) * di) % P; B0 = ((a * f - e * c) * di) % P
    slope = [(M[t][0] + M[t][1] * mu5) % P for t in range(3)]
    constk = (M[k][0] * A0 + M[k][1] * B0 + M[k][2] * K5 + RC[1][k]) % P
    assert slope[k] == 0 and slope[i] and slope[j]
    sb = [[pow(constk, 5, P)] if t == k else [0, pow(slope[t], 5, P)] for t in range(3)]
    st = [[] for _ in range(3)]
    for row in range(3):
        acc = []
        for col in range(3):
            acc = padd(acc, pscal(sb[col], M[row][col]))
        st[row] = acc
    for rr in range(2, 2 + L):
        st = [padd(x, [RC[rr][t]]) for t, x in enumerate(st)]
        for col in (range(3) if rr < 4 else range(1)):
            x = st[col]; x2 = pmul(x, x); x4 = pmul(x2, x2); st[col] = pmul(x4, x)
        new = []
        for row in range(3):
            acc = []
            for col in range(3):
                acc = padd(acc, pscal(st[col], M[row][col]))
            new.append(acc)
        st = new
    return st[0]


def taylor(F, c):
    """coefficients of F(c + s) in s (Horner on polynomials)."""
    out = []
    for coef in reversed(F):
        out = padd(pmul(out, [c, 1]) if out else [], [coef])
    return out


def kc(F, c):
    h = taylor(F, c)
    D = len(F) - 1
    g = [h[2 * j + 1] if 2 * j + 1 < len(h) else 0 for j in range((D - 1) // 2 + 1)]
    g = pscal(g, inv(g[-1]))
    # Y = S^E mod g, left-to-right
    red = reducer(g)
    y = [1]
    for bit in bin(E)[2:]:
        y = red(pmul(y, y)) if y else y
        if bit == '1':
            y = pmod([0] + y, g)
    y1 = padd(y, [P - 1])
    return pgcd_deg(list(g), y1) if y1 else (len(g) - 1, 0, 0)


def centre(seed):
    for j in range(64):
        w = int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), 'little') & ((1 << 255) - 1)
        if w < P:
            return w
    return None


def main():
    req = json.loads(sys.stdin.read())
    eid = req.get('experiment_id', '').split('-rep')[0]     # '-rep2' marks a pre-declared replicate (fresh organizer seeds)
    part = 'abc'.index(eid[-1]) if eid[-1:] in ('a', 'b', 'c') else 0
    if eid.startswith('hone-layers3'):
        L, todo = 3, lambda idx: 6 * part <= idx < 6 * part + 6
    else:
        L, todo = 2, lambda idx: idx % 3 == part
    F = line_poly(L)
    out = []
    for idx, t in enumerate(req['trials']):
        obs = {}
        if todo(idx):
            c = centre(bytes.fromhex(t['seed']))
            if c is None:
                obs['centre_draw_failed'] = 1
            else:
                obs['k_c'], obs['normal'], obs['max_drop'] = kc(F, c)
                obs['in_range'] = 1 if 1 <= obs['k_c'] <= 16 else 0
        else:
            obs['skipped'] = 1
        out.append({'trial': t['trial'], 'message_a_hex': None, 'message_b_hex': None, 'observations': obs})
    sys.stdout.write(json.dumps({'schema_version': 1, 'trials': out}, separators=(',', ':')))


if __name__ == '__main__':
    main()
```

### hone_flint_check.py

```python
"""hone_flint_check.py <pkg> - independent FLINT check of the organizer experiments of a package (written by a critic of our r8
package, kept as evidence): interpolates the line polynomial from the permutation with the pinned constants and compares it with
line_poly(L) of the experiment program; recomputes, for every computed trial of the emulated report (organizer seed protocol),
the centre, g_c, k(c) = deg gcd(g_c, S^((p-1)/2) - 1) and the normal flag with FLINT, and counts mismatches."""
import json, hashlib, sys, importlib.util
sys.dont_write_bytecode = True   # the package must not gain a __pycache__ directory
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
import os
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')+'/'
PKG=sys.argv[1]
spec=importlib.util.spec_from_file_location('hl', W+'packages/'+PKG+'/experiments/hone_layers.py'); hl=importlib.util.module_from_spec(spec); spec.loader.exec_module(hl)
K=json.load(open(W+'../pareto/orchard-pallas-constants.json'))
P=hl.P; RC=[[int(x,16) for x in r] for r in K['round_constants']]; M=[[int(x,16) for x in r] for r in K['mds']]
assert [[int(x,16) for x in r] for r in hl.CONST['round_constants']]==RC[:8] and [[int(x,16) for x in r] for r in hl.CONST['mds']]==M
ctx=fmpz_mod_ctx(P); pc=fmpz_mod_poly_ctx(ctx); X=pc.gen()
inv=lambda x: pow(x,P-2,P); e5=pow(5,-1,P-1)
def perm(st, last):
    for r in range(last+1):
        st=[(st[t]+RC[r][t])%P for t in range(3)]
        st=[pow(x,5,P) if (r<4 or t==0) else x for t,x in enumerate(st)]
        st=[sum(M[i][j]*st[j] for j in range(3))%P for i in range(3)]
    return st
# line constants independently
CAP=1<<65; K5=pow(CAP+RC[0][2],5,P)
mu5=(-M[0][0]*inv(M[0][1]))%P
a,b,e=M[1][0],M[1][1],(-(M[1][2]*K5+RC[1][1]))%P; c,d,f=M[2][0],M[2][1],(-(M[2][2]*K5+RC[1][2]))%P
di=inv((a*d-b*c)%P); A0=((e*d-b*f)*di)%P; B0=((a*f-e*c)*di)%P
def Fval(Tp, L):
    T=pow(Tp,e5,P); A=(T+A0)%P; B=(mu5*T+B0)%P
    nk=(pow(A,e5,P)-RC[0][0])%P; rho=(pow(B,e5,P)-RC[0][1])%P
    return perm([nk,rho,CAP],1+L)[0]
def interp(xs,ys):
    # Newton divided differences
    n=len(xs); coef=list(ys)
    for j in range(1,n):
        for i in range(n-1,j-1,-1):
            coef[i]=(coef[i]-coef[i-1])*inv((xs[i]-xs[i-j])%P)%P
    poly=pc([coef[-1]])
    for i in range(n-2,-1,-1): poly=poly*(X-xs[i])+coef[i]
    return poly
rep=json.load(open(W+'ledger/exp_report_'+PKG+'.json'))
can=lambda v: json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
sm=can({"domain":"hashsmash-experiments-v1","seed":"hashsmash-public-seed-v1","holdout_nonce":None,"target_config_sha256":rep['target_config_sha256']})
for L in (2,3):
    D=5**L; xs=list(range(1,D+2)); F=interp(xs,[Fval(x,L) for x in xs])
    assert F.degree()==D
    Fp=hl.line_poly(L); assert [int(x) for x in F.coeffs()]==Fp, 'line_poly mismatch'
    # extra random point check
    import random; random.seed(L)
    for _ in range(5):
        t=random.randrange(P); assert int(F(t))==Fval(t,L)
    print('L',L,'line_poly matches the permutation, degree',D)
    mism=0; tot=0
    for ex in rep['experiments']:
        if not ex['id'].startswith('hone-layers%d'%L): continue
        for tr in ex['checked_trials']:
            o=tr['untrusted_participant_observations']
            if 'k_c' not in o: continue
            seed=hashlib.sha256(sm+can([ex['id'],tr['trial']])).hexdigest()
            cc=hl.centre(bytes.fromhex(seed))
            h=F.compose(X+cc)-F.compose(cc-X)   # = 2 s a g(s^2)
            hc=[int(x) for x in h.coeffs()]
            assert all(hc[i]==0 for i in range(0,len(hc),2))
            g=pc([hc[2*j+1] for j in range((len(hc))//2)]); g=g.monic()
            y=pow(X,(P-1)//2,g) if False else X.pow_mod((P-1)//2,g)
            y1=y-1; G=g.gcd(y1)
            degs=[g.degree(), y1.degree()]; r0,r1=g,y1
            while not r1.is_zero():
                r0,r1=r1,r0%r1
                if not r1.is_zero(): degs.append(r1.degree())
            norm=int(all(degs[i]-degs[i+1]==1 for i in range(len(degs)-1)))
            tot+=1
            if (G.degree(),norm)!=(o['k_c'],o['normal']): mism+=1; print('MISMATCH',ex['id'],tr['trial'],G.degree(),norm,o)
    print('L',L,'checked',tot,'mismatches',mism)
```

### kc_line_sample.py

```python
"""kc_line_sample.py <L> <count> <seed-label> - our own large sample (FLINT) of k(c) = deg gcd(g_c, S^((p-1)/2) - 1) on the line of the
proof at L S-box layers (the same line polynomial as the organizer experiments, line_poly(L) of hone_layers_src.py), centres from
SHA-256 of a label; prints the counts of k and the fraction with 1 <= k <= 16 with its distance from 0.39347 in standard errors."""
import sys, json, hashlib, math, importlib.util, os
sys.dont_write_bytecode = True
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('hl', os.path.join(HERE, 'hone_layers_src.py')); hl = importlib.util.module_from_spec(spec); spec.loader.exec_module(hl)
C = json.load(open(os.path.join(HERE, '..', '..', 'pareto', 'orchard-pallas-constants.json')))
hl.CONST = {'round_constants': C['round_constants'][:8], 'mds': C['mds']}
L, N, lab = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
P = hl.P; pc = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)); X = pc.gen()
F = pc(hl.line_poly(L))
from collections import Counter
cnt = Counter(); hit = 0
for i in range(N):
    c = int.from_bytes(hashlib.sha256(f'{lab} {i}'.encode()).digest(), 'little') % P
    h = F.compose(X + c) - F.compose(c - X)
    hc = [int(x) for x in h.coeffs()]
    g = pc([hc[2 * j + 1] for j in range(len(hc) // 2)]).monic()
    k = g.gcd(X.pow_mod((P - 1) // 2, g) - 1).degree()
    cnt[min(k, 3)] += 1; hit += 1 <= k <= 16
q = 0.39347; se = math.sqrt(q * (1 - q) / N)
print(json.dumps({'L': L, 'N': N, 'label': lab, 'k0': cnt[0], 'k1': cnt[1], 'k2': cnt[2], 'k3plus': cnt[3], 'frac': hit / N, 'z': (hit / N - q) / se}))
```

## Appendix B. Logs

`gcd_mock.py --selftest (mock against executed runs, default configuration)`:

```
m=300 n0/4 pow2=False b=random b: deg G=0 executed strict 1.15093e+06 peak 1762 | mock strict 1.15093e+06 peak 1762 | histograms equal: True
m=300 n0/4 pow2=False b=S^((p-1)/2) - 1: deg G=0 executed strict 1.15093e+06 peak 1762 | mock strict 1.15093e+06 peak 1762 | histograms equal: True
m=1000 n0/12 pow2=False b=random b: deg G=0 executed strict 7.64536e+06 peak 6397 | mock strict 7.64536e+06 peak 6397 | histograms equal: True
m=1000 n0/12 pow2=False b=S^((p-1)/2) - 1: deg G=1 executed strict 7.64494e+06 peak 6397 | mock strict 7.64536e+06 peak 6397 | executed <= mock + roots bound (3): True
m=5000 n0/12 pow2=False b=random b: deg G=0 executed strict 5.97292e+07 peak 25828 | mock strict 5.97292e+07 peak 25828 | histograms equal: True
m=5000 n0/12 pow2=False b=S^((p-1)/2) - 1: deg G=2 executed strict 5.97533e+07 peak 25828 | mock strict 5.97292e+07 peak 25828 | executed <= mock + roots bound (4.933e+06): True
m=39062 n0/12 pow2=False b=random b: deg G=0 executed strict 7.15883e+08 peak 206377 | mock strict 7.15883e+08 peak 206377 | histograms equal: True
m=39062 n0/12 pow2=False b=S^((p-1)/2) - 1: deg G=1 executed strict 7.15882e+08 peak 206377 | mock strict 7.15883e+08 peak 206377 | executed <= mock + roots bound (3): True
m=39062 n0/4 pow2=False b=random b: deg G=0 executed strict 6.21906e+08 peak 225907 | mock strict 6.21906e+08 peak 225907 | histograms equal: True
m=39062 n0/4 pow2=False b=S^((p-1)/2) - 1: deg G=1 executed strict 6.21905e+08 peak 225907 | mock strict 6.21906e+08 peak 225907 | executed <= mock + roots bound (3): True
```

`gcd_mock.py --selftest-pow2 (mock against executed runs, the charged configuration: n0/12, 2^k wrapped lengths)`:

```
m=300 n0/12 pow2=True b=random b: deg G=0 executed strict 1.3118e+06 peak 1612 | mock strict 1.3118e+06 peak 1612 | histograms equal: True
m=300 n0/12 pow2=True b=S^((p-1)/2) - 1: deg G=0 executed strict 1.3118e+06 peak 1612 | mock strict 1.3118e+06 peak 1612 | histograms equal: True
m=1000 n0/12 pow2=True b=random b: deg G=0 executed strict 6.82405e+06 peak 4349 | mock strict 6.82405e+06 peak 4349 | histograms equal: True
m=1000 n0/12 pow2=True b=S^((p-1)/2) - 1: deg G=1 executed strict 6.82362e+06 peak 4349 | mock strict 6.82405e+06 peak 4349 | executed <= mock + roots bound (3): True
m=5000 n0/12 pow2=True b=random b: deg G=0 executed strict 5.30911e+07 peak 25828 | mock strict 5.30911e+07 peak 25828 | histograms equal: True
m=5000 n0/12 pow2=True b=S^((p-1)/2) - 1: deg G=2 executed strict 5.31152e+07 peak 25828 | mock strict 5.30911e+07 peak 25828 | executed <= mock + roots bound (4.933e+06): True
m=39062 n0/12 pow2=True b=random b: deg G=0 executed strict 6.19972e+08 peak 206377 | mock strict 6.19972e+08 peak 206377 | histograms equal: True
m=39062 n0/12 pow2=True b=S^((p-1)/2) - 1: deg G=1 executed strict 6.19972e+08 peak 206377 | mock strict 6.19972e+08 peak 206377 | executed <= mock + roots bound (3): True
```

`gcd_mock.py --selftest-degG (charged configuration; instances with deg G from 3 to 9)`:

```
m=300 n0/12 pow2=True prescribed square roots 3: deg G=3 executed strict 1.38494e+06 peak 1612 | mock strict 1.3118e+06 peak 1612 | executed <= mock + roots bound (1.607e+07) and peak <= mock peak: True
m=300 n0/12 pow2=True prescribed square roots 4: deg G=5 executed strict 1.60041e+06 peak 1612 | mock strict 1.3118e+06 peak 1612 | executed <= mock + roots bound (6.949e+07) and peak <= mock peak: True
m=300 n0/12 pow2=True prescribed square roots 5: deg G=5 executed strict 1.64731e+06 peak 1612 | mock strict 1.3118e+06 peak 1612 | executed <= mock + roots bound (6.949e+07) and peak <= mock peak: True
m=300 n0/12 pow2=True prescribed square roots 6: deg G=7 executed strict 2.00691e+06 peak 1612 | mock strict 1.3118e+06 peak 1612 | executed <= mock + roots bound (1.827e+08) and peak <= mock peak: True
m=300 n0/12 pow2=True prescribed square roots 8: deg G=8 executed strict 2.1593e+06 peak 1612 | mock strict 1.3118e+06 peak 1612 | executed <= mock + roots bound (2.687e+08) and peak <= mock peak: True
m=1000 n0/12 pow2=True prescribed square roots 3: deg G=5 executed strict 7.28038e+06 peak 4349 | mock strict 6.82405e+06 peak 4349 | executed <= mock + roots bound (6.949e+07) and peak <= mock peak: True
m=1000 n0/12 pow2=True prescribed square roots 4: deg G=4 executed strict 7.02544e+06 peak 4349 | mock strict 6.82405e+06 peak 4349 | executed <= mock + roots bound (3.668e+07) and peak <= mock peak: True
m=1000 n0/12 pow2=True prescribed square roots 5: deg G=6 executed strict 7.25613e+06 peak 4349 | mock strict 6.82405e+06 peak 4349 | executed <= mock + roots bound (1.172e+08) and peak <= mock peak: True
m=1000 n0/12 pow2=True prescribed square roots 6: deg G=6 executed strict 7.16608e+06 peak 4349 | mock strict 6.82405e+06 peak 4349 | executed <= mock + roots bound (1.172e+08) and peak <= mock peak: True
m=1000 n0/12 pow2=True prescribed square roots 8: deg G=8 executed strict 7.61166e+06 peak 4349 | mock strict 6.82405e+06 peak 4349 | executed <= mock + roots bound (2.687e+08) and peak <= mock peak: True
m=5000 n0/12 pow2=True prescribed square roots 3: deg G=3 executed strict 5.31638e+07 peak 25828 | mock strict 5.30911e+07 peak 25828 | executed <= mock + roots bound (1.607e+07) and peak <= mock peak: True
m=5000 n0/12 pow2=True prescribed square roots 4: deg G=5 executed strict 5.33076e+07 peak 25828 | mock strict 5.30911e+07 peak 25828 | executed <= mock + roots bound (6.949e+07) and peak <= mock peak: True
m=5000 n0/12 pow2=True prescribed square roots 5: deg G=5 executed strict 5.33072e+07 peak 25828 | mock strict 5.30911e+07 peak 25828 | executed <= mock + roots bound (6.949e+07) and peak <= mock peak: True
m=5000 n0/12 pow2=True prescribed square roots 6: deg G=6 executed strict 5.34567e+07 peak 25828 | mock strict 5.30911e+07 peak 25828 | executed <= mock + roots bound (1.172e+08) and peak <= mock peak: True
m=5000 n0/12 pow2=True prescribed square roots 8: deg G=9 executed strict 5.38597e+07 peak 25828 | mock strict 5.30911e+07 peak 25828 | executed <= mock + roots bound (3.853e+08) and peak <= mock peak: True
```

`memoized mock against plain mock`:

```
m=300 n0/4: memoized == plain: histogram True, charge True, peak 1762 == 1762
m=5000 n0/12: memoized == plain: histogram True, charge True, peak 25828 == 25828
m=39062 n0/4: memoized == plain: histogram True, charge True, peak 225907 == 225907
m=39062 n0/12: memoized == plain: histogram True, charge True, peak 206377 == 206377
m=195312 n0/12: memoized == plain: histogram True, charge True, peak 835261 == 835261
```

`python kc_line_sample.py 2 100000 poseidon_mage_kcline_L2`:

```
{"L": 2, "N": 100000, "label": "poseidon_mage_kcline_L2", "k0": 60299, "k1": 30402, "k2": 7780, "k3plus": 1519, "frac": 0.39701, "z": 2.291507621494599}
```

`python kc_line_sample.py 3 20000 poseidon_mage_kcline_L3`:

```
{"L": 3, "N": 20000, "label": "poseidon_mage_kcline_L3", "k0": 12138, "k1": 6067, "k2": 1510, "k3plus": 285, "frac": 0.3931, "z": -0.10711117065929948}
```

`hone_flint_check.py r7b (FLINT recomputation of every computed trial of the emulated experiments)`:

```
L 2 line_poly matches the permutation, degree 25
L 2 checked 1024 mismatches 0
L 3 line_poly matches the permutation, degree 125
L 3 checked 24 mismatches 0
```

`kc_stats_r0_k0.jsonl`:

```
{"r": 0, "line_k": 0, "c": 1, "k_c": 1, "s": 19.6}
{"r": 0, "line_k": 0, "c": 2, "k_c": 0, "s": 15.6}
{"r": 0, "line_k": 0, "c": 3, "k_c": 1, "s": 14.8}
{"r": 0, "line_k": 0, "c": 4, "k_c": 1, "s": 15.9}
{"r": 0, "line_k": 0, "c": 5, "k_c": 1, "s": 16.8}
{"r": 0, "line_k": 0, "c": 6, "k_c": 1, "s": 15.1}
{"r": 0, "line_k": 0, "c": 7, "k_c": 2, "s": 18.7}
{"r": 0, "line_k": 0, "c": 8, "k_c": 0, "s": 19.1}
{"r": 0, "line_k": 0, "c": 9, "k_c": 2, "s": 41.8}
{"r": 0, "line_k": 0, "c": 10, "k_c": 2, "s": 40.2}
{"r": 0, "line_k": 0, "c": 11, "k_c": 2, "s": 35.9}
{"r": 0, "line_k": 0, "c": 12, "k_c": 0, "s": 34.0}
{"r": 0, "line_k": 0, "c": 13, "k_c": 1, "s": 34.7}
{"r": 0, "line_k": 0, "c": 14, "k_c": 0, "s": 21.0}
{"r": 0, "line_k": 0, "c": 15, "k_c": 0, "s": 32.4}
{"r": 0, "line_k": 0, "c": 16, "k_c": 1, "s": 31.9}
{"r": 0, "line_k": 0, "c": 17, "k_c": 0, "s": 34.4}
{"r": 0, "line_k": 0, "c": 18, "k_c": 1, "s": 34.9}
{"r": 0, "line_k": 0, "c": 19, "k_c": 2, "s": 27.6}
{"r": 0, "line_k": 0, "c": 20, "k_c": 1, "s": 37.0}
{"r": 0, "line_k": 0, "c": 21, "k_c": 0, "s": 40.0}
{"r": 0, "line_k": 0, "c": 22, "k_c": 2, "s": 37.2}
{"r": 0, "line_k": 0, "c": 23, "k_c": 1, "s": 45.1}
{"r": 0, "line_k": 0, "c": 24, "k_c": 0, "s": 37.5}
{"r": 0, "line_k": 0, "c": 25, "k_c": 0, "s": 31.3}
{"r": 0, "line_k": 0, "c": 26, "k_c": 1, "s": 38.5}
{"r": 0, "line_k": 0, "c": 27, "k_c": 1, "s": 38.6}
{"r": 0, "line_k": 0, "c": 28, "k_c": 1, "s": 43.0}
{"r": 0, "line_k": 0, "c": 29, "k_c": 1, "s": 19.6}
{"r": 0, "line_k": 0, "c": 30, "k_c": 0, "s": 19.2}
{"r": 0, "line_k": 0, "c": 31, "k_c": 2, "s": 18.5}
{"r": 0, "line_k": 0, "c": 32, "k_c": 0, "s": 19.9}
{"r": 0, "line_k": 0, "c": 33, "k_c": 1, "s": 17.3}
{"r": 0, "line_k": 0, "c": 34, "k_c": 0, "s": 33.0}
{"r": 0, "line_k": 0, "c": 35, "k_c": 0, "s": 46.4}
{"r": 0, "line_k": 0, "c": 36, "k_c": 0, "s": 44.3}
{"r": 0, "line_k": 0, "c": 37, "k_c": 0, "s": 46.3}
{"r": 0, "line_k": 0, "c": 38, "k_c": 1, "s": 41.8}
{"r": 0, "line_k": 0, "c": 39, "k_c": 1, "s": 27.7}
{"r": 0, "line_k": 0, "c": 40, "k_c": 0, "s": 16.4}
{"r": 0, "line_k": 0, "c": 41, "k_c": 0, "s": 16.0}
{"r": 0, "line_k": 0, "c": 42, "k_c": 1, "s": 14.8}
{"r": 0, "line_k": 0, "c": 43, "k_c": 1, "s": 14.7}
{"r": 0, "line_k": 0, "c": 44, "k_c": 0, "s": 16.6}
{"r": 0, "line_k": 0, "c": 45, "k_c": 1, "s": 21.2}
{"r": 0, "line_k": 0, "c": 46, "k_c": 0, "s": 17.1}
{"r": 0, "line_k": 0, "c": 47, "k_c": 0, "s": 30.0}
{"r": 0, "line_k": 0, "c": 48, "k_c": 0, "s": 30.4}
{"r": 0, "line_k": 0, "c": 49, "k_c": 0, "s": 38.8}
{"r": 0, "line_k": 0, "c": 50, "k_c": 2, "s": 55.0}
{"r": 0, "line_k": 0, "c": 51, "k_c": 2, "s": 28.0}
{"r": 0, "line_k": 0, "c": 52, "k_c": 0, "s": 21.1}
{"r": 0, "line_k": 0, "c": 53, "k_c": 1, "s": 16.8}
{"r": 0, "line_k": 0, "c": 54, "k_c": 1, "s": 15.7}
{"r": 0, "line_k": 0, "c": 55, "k_c": 1, "s": 33.7}
{"r": 0, "line_k": 0, "c": 56, "k_c": 2, "s": 46.0}
{"r": 0, "line_k": 0, "c": 57, "k_c": 0, "s": 23.3}
{"r": 0, "line_k": 0, "c": 58, "k_c": 0, "s": 21.3}
{"r": 0, "line_k": 0, "c": 59, "k_c": 0, "s": 20.9}
{"r": 0, "line_k": 0, "c": 60, "k_c": 0, "s": 49.5}
{"r": 0, "line_k": 0, "c": 61, "k_c": 1, "s": 35.7}
{"r": 0, "line_k": 0, "c": 62, "k_c": 2, "s": 45.1}
{"r": 0, "line_k": 0, "c": 63, "k_c": 0, "s": 17.5}
{"r": 0, "line_k": 0, "c": 64, "k_c": 1, "s": 17.0}
{"r": 0, "line_k": 0, "c": 65, "k_c": 0, "s": 17.3}
{"r": 0, "line_k": 0, "c": 66, "k_c": 0, "s": 16.8}
{"r": 0, "line_k": 0, "c": 67, "k_c": 0, "s": 17.1}
{"r": 0, "line_k": 0, "c": 68, "k_c": 1, "s": 17.6}
{"r": 0, "line_k": 0, "c": 69, "k_c": 0, "s": 47.0}
{"r": 0, "line_k": 0, "c": 70, "k_c": 0, "s": 57.2}
{"r": 0, "line_k": 0, "c": 71, "k_c": 0, "s": 36.6}
{"r": 0, "line_k": 0, "c": 72, "k_c": 0, "s": 19.5}
{"r": 0, "line_k": 0, "c": 73, "k_c": 0, "s": 19.1}
{"r": 0, "line_k": 0, "c": 74, "k_c": 1, "s": 28.3}
{"r": 0, "line_k": 0, "c": 75, "k_c": 0, "s": 20.3}
{"r": 0, "line_k": 0, "c": 76, "k_c": 0, "s": 33.9}
{"r": 0, "line_k": 0, "c": 77, "k_c": 0, "s": 32.9}
{"r": 0, "line_k": 0, "c": 78, "k_c": 2, "s": 25.3}
{"r": 0, "line_k": 0, "c": 79, "k_c": 1, "s": 45.0}
{"r": 0, "line_k": 0, "c": 80, "k_c": 1, "s": 29.2}
{"r": 0, "line_k": 0, "c": 81, "k_c": 2, "s": 28.3}
{"r": 0, "line_k": 0, "c": 82, "k_c": 2, "s": 18.0}
{"r": 0, "line_k": 0, "c": 83, "k_c": 0, "s": 25.1}
{"r": 0, "line_k": 0, "c": 84, "k_c": 0, "s": 47.7}
{"r": 0, "line_k": 0, "c": 85, "k_c": 0, "s": 20.2}
{"r": 0, "line_k": 0, "c": 86, "k_c": 0, "s": 17.6}
{"r": 0, "line_k": 0, "c": 87, "k_c": 0, "s": 40.5}
{"r": 0, "line_k": 0, "c": 88, "k_c": 0, "s": 24.9}
{"r": 0, "line_k": 0, "c": 89, "k_c": 0, "s": 17.4}
{"r": 0, "line_k": 0, "c": 90, "k_c": 1, "s": 16.7}
{"r": 0, "line_k": 0, "c": 91, "k_c": 0, "s": 16.4}
{"r": 0, "line_k": 0, "c": 92, "k_c": 1, "s": 16.4}
{"r": 0, "line_k": 0, "c": 93, "k_c": 1, "s": 28.8}
{"r": 0, "line_k": 0, "c": 94, "k_c": 3, "s": 18.4}
{"r": 0, "line_k": 0, "c": 95, "k_c": 0, "s": 23.1}
{"r": 0, "line_k": 0, "c": 96, "k_c": 0, "s": 21.3}
{"r": 0, "line_k": 0, "c": 97, "k_c": 2, "s": 20.0}
{"r": 0, "line_k": 0, "c": 98, "k_c": 0, "s": 18.6}
{"r": 0, "line_k": 0, "c": 99, "k_c": 0, "s": 18.2}
{"r": 0, "line_k": 0, "c": 100, "k_c": 1, "s": 20.0}
{"r": 0, "line_k": 0, "c": 101, "k_c": 1, "s": 19.5}
{"r": 0, "line_k": 0, "c": 102, "k_c": 1, "s": 17.8}
{"r": 0, "line_k": 0, "c": 103, "k_c": 0, "s": 18.3}
{"r": 0, "line_k": 0, "c": 104, "k_c": 0, "s": 18.8}
{"r": 0, "line_k": 0, "c": 105, "k_c": 1, "s": 19.0}
{"r": 0, "line_k": 0, "c": 106, "k_c": 1, "s": 19.0}
{"r": 0, "line_k": 0, "c": 107, "k_c": 0, "s": 55.8}
{"r": 0, "line_k": 0, "c": 108, "k_c": 0, "s": 43.2}
{"r": 0, "line_k": 0, "c": 109, "k_c": 1, "s": 55.6}
{"r": 0, "line_k": 0, "c": 110, "k_c": 0, "s": 43.7}
{"r": 0, "line_k": 0, "c": 111, "k_c": 0, "s": 36.2}
{"r": 0, "line_k": 0, "c": 112, "k_c": 0, "s": 41.6}
{"r": 0, "line_k": 0, "c": 113, "k_c": 0, "s": 41.2}
{"r": 0, "line_k": 0, "c": 114, "k_c": 0, "s": 20.3}
{"r": 0, "line_k": 0, "c": 115, "k_c": 1, "s": 16.5}
{"r": 0, "line_k": 0, "c": 116, "k_c": 4, "s": 26.6}
{"r": 0, "line_k": 0, "c": 117, "k_c": 0, "s": 52.8}
{"r": 0, "line_k": 0, "c": 118, "k_c": 0, "s": 55.3}
{"r": 0, "line_k": 0, "c": 119, "k_c": 0, "s": 57.9}
{"r": 0, "line_k": 0, "c": 120, "k_c": 1, "s": 44.9}
{"r": 0, "line_k": 0, "c": 121, "k_c": 2, "s": 19.0}
{"r": 0, "line_k": 0, "c": 122, "k_c": 0, "s": 18.0}
{"r": 0, "line_k": 0, "c": 123, "k_c": 0, "s": 18.3}
{"r": 0, "line_k": 0, "c": 124, "k_c": 0, "s": 17.4}
{"r": 0, "line_k": 0, "c": 125, "k_c": 1, "s": 18.1}
{"r": 0, "line_k": 0, "c": 126, "k_c": 0, "s": 25.3}
{"r": 0, "line_k": 0, "c": 127, "k_c": 0, "s": 41.7}
{"r": 0, "line_k": 0, "c": 128, "k_c": 2, "s": 16.3}
{"r": 0, "line_k": 0, "c": 129, "k_c": 0, "s": 41.9}
{"r": 0, "line_k": 0, "c": 130, "k_c": 0, "s": 19.1}
{"r": 0, "line_k": 0, "c": 131, "k_c": 2, "s": 41.8}
{"r": 0, "line_k": 0, "c": 132, "k_c": 0, "s": 60.2}
{"r": 0, "line_k": 0, "c": 133, "k_c": 0, "s": 59.0}
{"r": 0, "line_k": 0, "c": 134, "k_c": 1, "s": 57.2}
{"r": 0, "line_k": 0, "c": 135, "k_c": 0, "s": 62.4}
{"r": 0, "line_k": 0, "c": 136, "k_c": 0, "s": 58.1}
{"r": 0, "line_k": 0, "c": 137, "k_c": 1, "s": 38.8}
{"r": 0, "line_k": 0, "c": 138, "k_c": 0, "s": 15.0}
{"r": 0, "line_k": 0, "c": 139, "k_c": 1, "s": 15.4}
{"r": 0, "line_k": 0, "c": 140, "k_c": 0, "s": 17.3}
{"r": 0, "line_k": 0, "c": 141, "k_c": 0, "s": 17.3}
{"r": 0, "line_k": 0, "c": 142, "k_c": 0, "s": 16.5}
{"r": 0, "line_k": 0, "c": 143, "k_c": 0, "s": 17.0}
{"r": 0, "line_k": 0, "c": 144, "k_c": 0, "s": 16.8}
{"r": 0, "line_k": 0, "c": 145, "k_c": 0, "s": 16.9}
{"r": 0, "line_k": 0, "c": 146, "k_c": 0, "s": 17.0}
{"r": 0, "line_k": 0, "c": 147, "k_c": 1, "s": 16.8}
{"r": 0, "line_k": 0, "c": 148, "k_c": 0, "s": 16.4}
{"r": 0, "line_k": 0, "c": 149, "k_c": 0, "s": 16.8}
{"r": 0, "line_k": 0, "c": 150, "k_c": 0, "s": 16.3}
{"r": 0, "line_k": 0, "c": 151, "k_c": 0, "s": 16.8}
{"r": 0, "line_k": 0, "c": 152, "k_c": 0, "s": 16.7}
{"r": 0, "line_k": 0, "c": 153, "k_c": 1, "s": 16.6}
{"r": 0, "line_k": 0, "c": 154, "k_c": 2, "s": 16.0}
{"r": 0, "line_k": 0, "c": 155, "k_c": 0, "s": 15.9}
{"r": 0, "line_k": 0, "c": 156, "k_c": 0, "s": 15.6}
{"r": 0, "line_k": 0, "c": 157, "k_c": 1, "s": 15.8}
{"r": 0, "line_k": 0, "c": 158, "k_c": 0, "s": 17.0}
{"r": 0, "line_k": 0, "c": 159, "k_c": 0, "s": 16.0}
{"r": 0, "line_k": 0, "c": 160, "k_c": 0, "s": 15.3}
{"r": 0, "line_k": 0, "c": 161, "k_c": 0, "s": 14.5}
{"r": 0, "line_k": 0, "c": 162, "k_c": 0, "s": 14.9}
{"r": 0, "line_k": 0, "c": 163, "k_c": 1, "s": 15.3}
{"r": 0, "line_k": 0, "c": 164, "k_c": 2, "s": 14.3}
{"r": 0, "line_k": 0, "c": 165, "k_c": 0, "s": 15.4}
{"r": 0, "line_k": 0, "c": 166, "k_c": 1, "s": 15.3}
{"r": 0, "line_k": 0, "c": 167, "k_c": 2, "s": 15.5}
{"r": 0, "line_k": 0, "c": 168, "k_c": 0, "s": 14.9}
{"r": 0, "line_k": 0, "c": 169, "k_c": 0, "s": 14.0}
{"r": 0, "line_k": 0, "c": 170, "k_c": 0, "s": 13.9}
{"r": 0, "line_k": 0, "c": 171, "k_c": 0, "s": 13.6}
{"r": 0, "line_k": 0, "c": 172, "k_c": 0, "s": 13.8}
{"r": 0, "line_k": 0, "c": 173, "k_c": 1, "s": 13.7}
{"r": 0, "line_k": 0, "c": 174, "k_c": 0, "s": 14.6}
{"r": 0, "line_k": 0, "c": 175, "k_c": 0, "s": 14.1}
{"r": 0, "line_k": 0, "c": 176, "k_c": 2, "s": 14.8}
{"r": 0, "line_k": 0, "c": 177, "k_c": 1, "s": 14.0}
{"r": 0, "line_k": 0, "c": 178, "k_c": 0, "s": 13.4}
{"r": 0, "line_k": 0, "c": 179, "k_c": 1, "s": 14.3}
{"r": 0, "line_k": 0, "c": 180, "k_c": 0, "s": 14.6}
{"r": 0, "line_k": 0, "c": 181, "k_c": 0, "s": 14.3}
{"r": 0, "line_k": 0, "c": 182, "k_c": 1, "s": 14.3}
{"r": 0, "line_k": 0, "c": 183, "k_c": 0, "s": 15.0}
{"r": 0, "line_k": 0, "c": 184, "k_c": 1, "s": 15.9}
{"r": 0, "line_k": 0, "c": 185, "k_c": 0, "s": 16.3}
{"r": 0, "line_k": 0, "c": 186, "k_c": 0, "s": 15.2}
{"r": 0, "line_k": 0, "c": 187, "k_c": 0, "s": 15.6}
{"r": 0, "line_k": 0, "c": 188, "k_c": 1, "s": 16.3}
{"r": 0, "line_k": 0, "c": 189, "k_c": 1, "s": 15.4}
{"r": 0, "line_k": 0, "c": 190, "k_c": 2, "s": 15.5}
{"r": 0, "line_k": 0, "c": 191, "k_c": 0, "s": 15.8}
{"r": 0, "line_k": 0, "c": 192, "k_c": 0, "s": 16.1}
{"r": 0, "line_k": 0, "c": 193, "k_c": 0, "s": 16.9}
{"r": 0, "line_k": 0, "c": 194, "k_c": 1, "s": 15.9}
{"r": 0, "line_k": 0, "c": 195, "k_c": 2, "s": 16.4}
{"r": 0, "line_k": 0, "c": 196, "k_c": 0, "s": 16.9}
{"r": 0, "line_k": 0, "c": 197, "k_c": 0, "s": 16.7}
{"r": 0, "line_k": 0, "c": 198, "k_c": 0, "s": 16.2}
{"r": 0, "line_k": 0, "c": 199, "k_c": 1, "s": 16.7}
{"r": 0, "line_k": 0, "c": 200, "k_c": 2, "s": 16.9}
```

`kc_stats_r1_k0.jsonl`:

```
{"r": 1, "line_k": 0, "c": 1, "k_c": 1, "s": 89.2}
{"r": 1, "line_k": 0, "c": 2, "k_c": 1, "s": 85.0}
{"r": 1, "line_k": 0, "c": 3, "k_c": 1, "s": 93.1}
{"r": 1, "line_k": 0, "c": 4, "k_c": 1, "s": 92.6}
{"r": 1, "line_k": 0, "c": 5, "k_c": 1, "s": 95.4}
{"r": 1, "line_k": 0, "c": 6, "k_c": 0, "s": 93.1}
{"r": 1, "line_k": 0, "c": 7, "k_c": 0, "s": 92.2}
{"r": 1, "line_k": 0, "c": 8, "k_c": 1, "s": 131.9}
{"r": 1, "line_k": 0, "c": 9, "k_c": 0, "s": 94.7}
{"r": 1, "line_k": 0, "c": 10, "k_c": 2, "s": 123.2}
{"r": 1, "line_k": 0, "c": 11, "k_c": 2, "s": 96.7}
{"r": 1, "line_k": 0, "c": 12, "k_c": 0, "s": 96.7}
{"r": 1, "line_k": 0, "c": 13, "k_c": 0, "s": 93.6}
{"r": 1, "line_k": 0, "c": 14, "k_c": 0, "s": 97.2}
{"r": 1, "line_k": 0, "c": 15, "k_c": 1, "s": 95.5}
{"r": 1, "line_k": 0, "c": 16, "k_c": 3, "s": 96.2}
{"r": 1, "line_k": 0, "c": 17, "k_c": 1, "s": 96.8}
{"r": 1, "line_k": 0, "c": 18, "k_c": 1, "s": 88.1}
{"r": 1, "line_k": 0, "c": 19, "k_c": 0, "s": 91.8}
{"r": 1, "line_k": 0, "c": 20, "k_c": 1, "s": 94.9}
{"r": 1, "line_k": 0, "c": 21, "k_c": 1, "s": 96.3}
{"r": 1, "line_k": 0, "c": 22, "k_c": 0, "s": 104.4}
{"r": 1, "line_k": 0, "c": 23, "k_c": 0, "s": 193.9}
{"r": 1, "line_k": 0, "c": 24, "k_c": 2, "s": 207.1}
{"r": 1, "line_k": 0, "c": 25, "k_c": 2, "s": 308.8}
{"r": 1, "line_k": 0, "c": 26, "k_c": 1, "s": 319.8}
{"r": 1, "line_k": 0, "c": 27, "k_c": 0, "s": 302.9}
{"r": 1, "line_k": 0, "c": 28, "k_c": 0, "s": 258.9}
{"r": 1, "line_k": 0, "c": 29, "k_c": 0, "s": 238.6}
{"r": 1, "line_k": 0, "c": 30, "k_c": 1, "s": 238.0}
{"r": 1, "line_k": 0, "c": 31, "k_c": 2, "s": 217.4}
{"r": 1, "line_k": 0, "c": 32, "k_c": 0, "s": 229.3}
{"r": 1, "line_k": 0, "c": 33, "k_c": 0, "s": 230.4}
{"r": 1, "line_k": 0, "c": 34, "k_c": 1, "s": 267.3}
{"r": 1, "line_k": 0, "c": 35, "k_c": 1, "s": 302.9}
{"r": 1, "line_k": 0, "c": 36, "k_c": 0, "s": 322.6}
{"r": 1, "line_k": 0, "c": 37, "k_c": 1, "s": 282.7}
{"r": 1, "line_k": 0, "c": 38, "k_c": 1, "s": 282.2}
{"r": 1, "line_k": 0, "c": 39, "k_c": 0, "s": 266.6}
```
