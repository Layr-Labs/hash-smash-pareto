# Orchard r=3: centre differencing on the two-round line, value-domain Montgomery powering, counted executed run

## 1. Target

Profile `poseidon-orchard-r3-prefix-v1`: Orchard P128Pow5T3 over the Pallas field
F_p, p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001 (255 bits),
width 3, S-box x -> x^5, deployed round constants rc[i] (i = 0..63) and the deployed 3x3
MDS matrix M, both pinned in `orchard-pallas-constants.json`. The reduced permutation
applies the original full rounds 0, 1, 2, 3, the original partial rounds 4..6
(S-box on lane 0 only), and the original full rounds 60, 61, 62, 63. Each round adds
rc[i], applies the S-box layer, then multiplies by M. The hash of (nk, rho) is lane 0
of the permutation of the state [nk, rho, 2^65]; both inputs are canonical (below p) and
the output is the entire field element, 32 little-endian bytes.

Claim: an ordinary collision, two distinct canonical pairs with equal reduced hash, found
by a deterministic procedure, executed on the fixed target from its first trial (Section 7 lists
every execution), whose complete primitive-operation count and peak memory are
stated below. Cost model `orchard-field-ram-v2`, applied as stated in 4.0: one unit per field
addition, subtraction or multiplication and per comparison, branch or bit operation, two per 256-bit
load or store (the access and its address operation), 3 per loop iteration (eight elements per
iteration where the loop is unrolled) and 2 per loop exit, a declared register file of 16 words;
C(3) = 216 + 21*3 = 279 units per reduced permutation.
Normalized time T = W / C(3), `time_log2` = log2 T. Memory in bytes, including code.

Notation. x^5 is a bijection of F_p because gcd(5, p-1) = 1; its inverse is x -> x^e5 with
e5 = 5^-1 mod (p-1), so "the fifth root" is a single well-defined field element. We write
H(nk, rho) for the reduced hash. p-1 = 2^32 * 3 * 463 * (two large primes), so F_p contains
primitive roots of unity of every order 3 * 2^k and 2^k with k <= 32; all transforms below are cyclic
number-theoretic transforms of such lengths.

### 1.1 The input line that bypasses rounds 0 and 1

Write c0 = rc[0], c1 = rc[1], K5 = (2^65 + c0[2])^5 (a constant). For an input (nk, rho)
put A = (nk + c0[0])^5 and B = (rho + c0[1])^5. After the round-0 S-box layer the state is
(A, B, K5); after the round-0 MDS and the round-1 constants, the round-1 S-box inputs are

  u_t = M[t][0]*A + M[t][1]*B + M[t][2]*K5 + c1[t],   t = 0, 1, 2.

**Lemma 1 (line).** Fix k = 2 and let mu5 = -M[2][0] / M[2][1] (M[2][1] is nonzero, M being
MDS). Let (A0, B0) be the unique solution of the two linear equations

  M[t][0]*A0 + M[t][1]*B0 + M[t][2]*K5 + c1[t] = 0,   t = 0, 1

(unique because the minor M[0][0]M[1][1] - M[0][1]M[1][0] of an MDS matrix is nonzero).
For a parameter T in F_p define the line A = T + A0, B = mu5*T + B0 and the input
nk(T) = A^e5 - c0[0], rho(T) = B^e5 - c0[1]. Then along the line u_2 is the constant
kappa := M[2][0]A0 + M[2][1]B0 + M[2][2]K5 + c1[2], and u_0 = a_0*T, u_1 = a_1*T with
a_t = M[t][0] + M[t][1]*mu5 (both nonzero, checked on the deployed matrix). Consequently the
round-1 S-box outputs are (a_0^5 T', a_1^5 T', kappa^5) with T' := T^5, which is affine in T'.

Proof. Substituting the line into u_t gives u_t = a_t*T + (M[t][0]A0 + M[t][1]B0 + M[t][2]K5 + c1[t]);
the bracket vanishes for t = 0, 1 by the choice of (A0, B0), and a_2 = 0 by the choice of mu5.
Raising a_t*T to the fifth power gives a_t^5 T^5. Since T -> T' = T^5 is a bijection of F_p,
every T' in F_p is reached by exactly one line point, and the map T' -> (nk, rho) is injective
(A and B determine nk and rho uniquely, and A is determined by T' = T^5 through T). QED

Every quantity in Lemma 1 was recomputed from the pinned constants by the program in
Appendix A; the two bracket conditions and a_2 = 0 are asserted there, and the identity
H(nk(T), rho(T)) = F(T^5) below is asserted at three parameter values.



**Lemma 2 (degree and leading coefficient).** Let s(T') denote the state after the round-1 MDS, an
affine function of T' by Lemma 1. Applying rounds 2, 3 (full), 4..6 (partial) and 60..63
(full) to s(T') and taking lane 0 defines a polynomial F in F_p[T'] of degree exactly
D = 5^(6+3) = 1,953,125, with leading coefficient a_D, and H(nk(T), rho(T)) = F(T^5) for every T.

Proof. Track for each lane the pair (degree, leading coefficient). Adding constants leaves it
unchanged unless the degree is 0; the S-box maps (d, l) to (5d, l^5) for d >= 1; the MDS maps the
three lanes to (d_max, sum of M[row][col] l_col over the lanes of degree d_max). Starting from the
affine lanes of Lemma 1 this recursion is a finite computation on the pinned constants; the program
(`lead_coefficient`, Appendix A) executes it, asserts that no leading coefficient cancels, and
obtains degree D for lane 0 and a_D != 0 (its value is in the ledger, Appendix B). Since the
recursion only follows the top-degree terms, which cannot cancel when the asserted sums are
nonzero, deg F = D. The identity with H follows from Lemma 1. QED

## 2. Centre differencing (odd part)

**Lemma 3 (odd part).** For a centre c in F_p put h_c(s) = F(c + s) = sum_i h_i s^i. Then
F(c + s) - F(c - s) = 2 sum_{i odd} h_i s^i = 2 s G_c(s^2) with G_c(S) = sum_{j=0..m} h_{2j+1} S^j,
m = (D - 1)/2 = 976,562. The leading coefficient of G_c is h_D = a_D (D is odd), independent of c.
Put g_c = G_c / a_D, monic of degree m.

**Lemma 4 (collision from a root).** If S is a root of g_c that is a nonzero square in F_p and
s is either square root of S, then W1 = c + s and W2 = c - s are distinct (s != 0, p odd) and
F(W1) = F(W2). By Lemma 1 the parameters T_i = W_i^e5 give two distinct canonical input pairs
(nk(T_i), rho(T_i)) with equal reduced hash. Proof: F(c + s) - F(c - s) = 2 s a_D g_c(S) = 0.
Distinctness: W1 - W2 = 2s != 0 and T' -> (nk, rho) is injective (Lemma 1). QED

The roots of g_c that are nonzero squares are exactly the roots of G = gcd(g_c, S^((p-1)/2) - 1)
(Euler's criterion: S^((p-1)/2) = 1 iff S is a nonzero square; S^((p-1)/2) - 1 splits into
distinct linear factors over F_p). Working with g_c instead of F itself halves the degree of every
polynomial in the procedure. This odd-part reduction is the one used on this board by Jbenisek
(767cdef0-485d-443a-92ec-652ee8166c4a) at r = 1 and 0xshikhar (86ebd942-5d22-4786-b065-332ba3180792) at r = 2; it is reimplemented here.

## 3. The procedure

All arithmetic is over F_p. D = 1,953,125, m = 976,562, n = 1,048,576 (the least 3*2^k or 2^k above m), omega a
primitive n-th root of unity, psi a primitive 2n-th root with psi^2 = omega (so psi^n = -1),
O1 = {omega^i} and O2 = {psi omega^i}. The procedure is deterministic and reads no random coins.
It runs trials i = 1, 2, 3, ... with centre c_i = i, stopping at the first trial that yields a
collision, with a finite cap of 64 trials (exit without output if reached; not reached). Every
trial that runs is charged in full. It was executed from trial 1 on the fixed target (Section 7 lists every execution); it
stopped at trial 1 (trial 1 (c = 1): deg G = 2).

Step 1 (values of g_c on O1). Transform order: `ntt_forward` (4.1) returns the values of its
input at the points omega^e(t) at output position t, where for n = 3 * 2^k, t = 3B + s', s' in {0, 1, 2}, and
e(t) = rev_k(B) + 2^k s' (rev_k reverses the k bits of the block index B), and for n = 2^k, e(t) = rev_k(t); Appendix A
asserts this against the transform of X at the lengths 3..768 and 2..1024 of its self-test. For t = 0..n-1 put s_t = psi^e(t), so
s_t^2 = omega^e(t), and compute
  G1[t] = (F(c + s_t) - F(c - s_t)) * (2 a_D s_t)^-1 = g_c(omega^e(t))
by two line evaluations (start from the affine state of Lemma 1 and apply the 6 + 3 remaining
rounds). The points s_t and the factors (2 a_D)^-1 psi^-e(t) are produced in transform order by
a prefix-product generator over the bits of B (4.2). G1 is the vector of values of g_c on O1 in
the order the transforms use; it is all that the next step needs.

Step 2 (Montgomery stage: Y = S^((p-1)/2) mod g_c; the stage C of bradcush, 1aa56884-8e68-4aa8-87c7-ed38d0a3e65b
and 4bcabff8-2863-4d70-a0d3-401da0cbe5fb, reimplemented). Let R = X^n - 1. If g_c has no root on O1
(asserted: every G1[t] != 0), R is invertible modulo g_c. The Montgomery product of A, B
(deg < n) is Mont(A, B) = (A B + U g_c) / R with U = -A B g_c^-1 mod R; it is a polynomial,
congruent to A B R^-1 modulo g_c, of degree at most n - 2 (because deg(AB + U g_c) <= 2n - 2 and
R divides it, the quotient by a degree-n polynomial has degree <= n - 2; it needs deg A, deg B < n
and m < n). A polynomial A of degree < n is held as its value vectors A1 on O1 and A2 on O2.
Because R = 0 on O1 and R = -2 on O2:
  - U mod R is determined by its values on O1, which are -A1 B1 / G1 pointwise;
  - Mont(A, B) has degree < n and its values on O2 are (A2 B2 + U2 G2) / (-2), where U2, G2 are
    the values of U and g_c on O2.
So one Montgomery squaring is: U1 = A1^2 * Ginv1 with Ginv1 = -1/(n G1) (the 1/n of the inverse
transform folded in); U = inverse transform of U1 (exact coefficients); twist U_j <- U_j psi^j and
forward transform (values on O2); B2 = A2^2 h + U2 G2h with h = -1/2 and G2h = -G2/2; then B2 is
the new A2, and the new A1 is obtained by the inverse transform of B2, the untwist by psi^-j / n,
and a forward transform. Four transforms of length n per squaring and no coefficient-domain
product. For a set bit of the exponent the new A2 is B2 multiplied pointwise by the point
psi omega^e(t) (multiplication by X; the degree stays <= n - 1 < n), before the move to O1.
Start (Montgomery form of X^(2^j)): with a = 2^j = 262,144, L = n + a - m + 1 = 334,159, the quotient
of X^(n+a) by g_c is quot = rev_{L-1}(rev(g_c)^-1 mod X^L) (Newton iteration, 4.3); since
quot g_c = X^(n+a) - r with deg r < m, the cyclic product c = quot g_c mod (X^n - 1) satisfies
c_i = -r_i + [i = a] for i < m and c_i = 0 for m <= i < n (because a < m < n), so
-c = r - X^a = X^a (X^n - 1) mod g_c = X^a R mod g_c, the Montgomery form of X^a, of degree < m.
j = 18 is the largest power with a < m and L at most n/2 (so the Newton buffers fit in one
n-word buffer). The exponent (p-1)/2 has its top bit at position 253 followed by 128 zero bits,
so after X^a the remaining 235 bits each cost one Montgomery squaring, 45 of them with the
multiplication by X. Finish: Mont(Y~, 1) = Y~ R^-1 mod g_c has degree < m (deg(Y~ + U g_c) <= n - 1 + m,
divided by R), so it is the fully reduced Y = X^((p-1)/2) mod g_c; it is obtained by one more
half-step (U from Y~1 Ginv1, moved to O2, B2 = Y~2 h + U2 G2h) and an interpolation on O2.
The coefficients of g_c are recovered from G2h by one inverse transform with untwist (they were
not kept during the powering). The program asserts that the result is reduced, that the
recovered g_c is the interpolated one, and that Y equals the FLINT value pow_mod(X, (p-1)/2, g_c).

Step 3 (gcd). G = gcd(g_c, Y - 1) by the counted half-gcd of Section 5; its roots by the root stage
of Section 5. If deg G = 0 the trial fails and the next centre runs.

Step 4 (finish). For each root S != 0 of G: s = sqrt(S) by Tonelli-Shanks (p - 1 = 2^32 t, the
non-residue 5, every multiplication, comparison and loop iteration counted), W1 = c + s, W2 = c - s,
the inputs of both by the inverse line map (three fifth roots each), both reduced hashes, and the
digest comparison.

## 4. Operation charges

4.0 Convention (the claim). Prices follow `orchard-field-ram-v2`, applied as the executed-count entries on
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
    the 1 MiB code allowance of Section 9.
  - inversion 380 units (a round-up of the 330-unit ladder for x^(p-2), registers only); a fifth root x^e5
    is 253 squarings and 124 multiplications, 377 units; exponentiations are binary ladders of
    (bits - 1) squarings plus (popcount - 1) multiplications; a reduced permutation evaluated as a
    reference hash in the finish is one target-compression unit, C(r) operations.
Every kernel records its loads, stores, arithmetic, control and loops separately (`ntt.Counter`), so the
same run is also priced under the looser rule of our earlier entries (one unit per load or store, 1/2 unit
of loop control per element of a streaming loop). That second figure is reported only for comparison
(Section 6); the claim uses the convention above, which is the larger.

4.1 Transforms. For n = 3*2^k the forward transform is decimation-in-frequency and the inverse is
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
T_strict(1,048,576) = 78,424,788 2/3 (loose rule: 63,788,373 1/3). The transform constants are the roots of unity of orders 3 * 2^i and 2^i
(i <= 30) and their inverses, which give every per-level twiddle step of every length used, plus 1/N for each length used:
fewer than 440 constants, each an exponentiation of at most 380 units, plus an address operation for each of their at most 440
stores, charged once in the setup (167,200 + 440). The closed forms are asserted equal to the instrumented kernels (Appendix A)
at the lengths listed in their self-tests (3 * 2^k up to 3072 and 2^k up to 4096) in both conventions, and the convolution is checked against schoolbook multiplication.

4.2 Build (Step 1), per trial: 2n line evaluations; one evaluation is 6 + 27*6 + 21*3 = 231 field
operations (affine state after round 1: 3 multiplications and 3 additions; six full rounds at 27: three
constant additions, three x^5 at 3 multiplications, the MDS at 9 multiplications and 6 additions; 3 partial rounds at
21) and 6 + 12 (6 + 3) = 114 constant loads (6 affine coefficients, then 3 round constants and the 9
MDS entries per round; the three-lane state stays in registers): 459 units strict. Per position:
c + s_t and c - s_t (2), the difference and the product with the factor (2), one store; the loop over
positions is not unrolled (3 per iteration, 2 on exit). Point generator (`point_stream`, closed form `PG`):
a stack of k + 1 prefix products over the bits of the block index (k + 1 initial stores); per block one loop
iteration with the trailing-zero count and branch (5 ctl), recomputation of one prefix (two loads, one
multiplication, one store), straight-line stores of the prefixes below the changed bit (over all blocks
n/3 - k - 1 stores), two multiplications for the cube-root companions of the block's point; 2 on exit. For n = 2^k a
block is one point: n - k - 1 copied-prefix stores in all and no companions. Build charge per trial: 1,001,390,072 units
(loose 752,877,566). Peak: the n words of G1 plus 64 words of constants and stacks (n + 64 in the ledger).

4.3 Montgomery stage (Step 2), closed forms of `mont.py` (functions TV, TW, PASS, STEP, SINV, BINV, SETUP_POWER),
each asserted equal to the instrumented execution in the run itself (the ledger records the per-phase marks
in both conventions) and in the self-test against FLINT at m = 20..370. A streaming pass over e elements
with a field operations, l loads and s stores per element costs e (a + 2 l + 2 s) + LP(e):
  - interpolation of g_c: scaled copy of G1 (1 load, 1 multiplication, 1 store per word) and one inverse
    transform: 84,060,886 2/3;
  - start residue: Newton inverse of rev(g_c) to precision L at steps m -> m2 = min(2m, L), length N = least
    3*2^i >= m2, d = m2 - m: copy-and-pad of rev(g_c) (min(m2, m+1) loads, N stores) and of the current
    inverse (m loads, N stores), 5 transforms, two pointwise products (2 loads, 2 multiplications, 1 store per
    point), copy of d words, zero padding of N - d words, and the update (load, subtraction, store per word);
    then the reversed copy into the n-word buffer with padding, a forward transform, the pointwise product with
    G1 and the factor -1/n, an inverse transform and the zeroing of positions m..n-1: 581,605,938 1/3;
  - batch inversion of G1 into Ginv1 = -1/(n G1) (Montgomery's trick; prefix products in a scratch buffer;
    one inversion; the factor -1/n folded into the inverted product): 14,418,299;
  - tables: start values on O2 (copy with twist and a forward transform), on O1 (one forward transform in
    place), G2h (twist with c0 = -1/2 and a forward transform): 248,643,714;
  - powering: per squaring 4 transforms, the twist and the untwist (1 load, 2 multiplications, 1 store per
    word), the pass U1 = A1^2 Ginv1 (2 loads, 2 multiplications, 1 store), the pass B2 = A2^2 h + U2 G2h (3 loads,
    3 multiplications, 1 addition, 2 stores into A2 and the work buffer): 350,923,610 2/3 (loose 280,319,317 1/3); with the
    multiplication by X add one multiplication per point and one point generator: 366,652,245 2/3; 235 squarings,
    45 of them with X: 83,174,837,081 2/3;
  - finish: half-step (U1 pass, inverse, twist, forward, B2 pass), interpolation on O2 (inverse, untwist) and the
    recovery of g_c (inverse, untwist): 353,413,980 2/3.
  Stage total per trial: 84,456,979,900 1/3 units strict (loose 67,419,698,712 2/3). Buffers: A1, A2, Ginv1, G2h of n words each
  (4n); during the Newton step G1, g_c, the two Newton buffers (2 N <= n) and the growing inverse (<= L words):
  at most 2n + max(2N + m2). Peak of the stage: 4,194,304 words.

4.4 Setup, once: the constants of Lemma 1 (two inversions, fifth powers, products and sums) as a flat 4,000
units (twice the 2,000 of our earlier entries), the transform constants (167,200 + 440), the
leading-coefficient recursion of Lemma 2 with the inversion of 2 a_D (bounded by 24 (8 + r) + 381 = 645),
the Tonelli-Shanks constant 5^t (267), and a bound of 20,000 for writing the output (two pairs, the digest):
192,552 units. Per trial: the centre (1 unit) and forming Y - 1 (load, subtraction, store: 5 units).

4.5 Finish (Step 4), per root S, all in registers: the zero test (1), Tonelli-Shanks as executed (the
exponentiation S^((t-1)/2), 2 multiplications, then per loop iteration of the classical algorithm: squarings
5 units each including compare and counter, the repeated squaring of the running non-residue power 4 units
each, three multiplications and 3 units of loop control), W1 and W2 (2), the inputs of both sides
(2 (3 * 377 + 8)), two reduced hashes (2 * 279) and the comparison (8): 8,709 units on this run. The finish is
priced the same under both conventions: its values stay in registers and no constant loads are charged for it
(the line coefficients of the inverse map, the Tonelli-Shanks constant, the constants inside the two reference
hashes, which are charged as C(r) units each); charging those loads would add about 360 units.

## 5. The gcd stage and root extraction

5.1 Algorithm. G = gcd(g_c, Y - 1) is computed by a half-gcd in the shape of von zur Gathen
and Gerhard (Modern Computer Algebra, 11.4): hgcd(r0, r1, k) returns the 2x2 cofactor matrix
R with R*(r0, r1) = (r_j, r_{j+1}) where j is the last index with deg r0 - deg r_j <= k; it
recurses on the top 2d coefficients with d = ceil(k/2), applies the matrix, performs one
division, recurses again with the remaining budget, and composes the two matrices and the
quotient. Below k <= 48 the classical Euclidean algorithm runs on the truncated inputs. The
top level (fast_gcd) repeatedly calls hgcd on the top 2d+1 coefficients of (a, b) with
d = ceil(deg a / 4), applies the half-size matrix, performs one division, and finishes with
classical Euclid once deg b <= 48; it never composes a full-size matrix. All degree bookkeeping
is exact, so non-normal remainder sequences are handled by the degree tests.

Memory-lean execution (three devices, each charged and inside the memory model):
(i) Views. The truncated top part handed to a child hgcd is a read-only pointer into the
parent's buffer, which stays owned by a live frame until the child returns; no copy is made.
(ii) Wrapped matrix-vector step. (a', b') = R (a, b) is computed modulo X^N - 1 with
N = the least 3*2^j >= n_h + 1, n_h = deg a - deg R11, fixed before any arithmetic. Degree
argument: for the remainder sequence of (a, b) with cofactors s_i a + t_i b = r_i, t_0 = 0,
t_1 = 1, t_{i+1} = t_{i-1} - q_i t_i, induction gives deg t_{i+1} = n0 - n_i (non-normal sequences
included). hgcd returns R = [[s_h, t_h], [s_{h+1}, t_{h+1}]], whose first h quotients agree with
those of (a, b), so a' = r_h has degree exactly n0 - deg R11 = n_h < N and deg b' < n_h.
Reduction modulo X^N - 1 is linear, so R00 a + R01 b mod (X^N - 1) = r_h exactly even though
the individual products alias; likewise for b'. Inputs longer than N are folded while being
copied. The program asserts deg a' = n_h < N and deg b' < n_h at every such step (all passed).
Four buffers of N words are live; at the top level a and b are freed once copied.
(iii) Shared-transform 2x2 matrix products inside hgcd: each nonzero entry is transformed once
at the least length covering every one of the eight products (linear, no wrap; asserted), with
one in-place 2x2 pointwise pass per row.
Each device is used only when its charge is below the product-by-product charge; the choice is
a deterministic function of the sizes and is recorded in the histogram.
The implementation was checked against an independent library gcd on random pairs of degree
50..5000, on nontrivial gcds of degrees 1, 2, 3, 7, 40, on twelve adversarial pairs built
backwards from prescribed quotient sequences with non-normal steps and quotient degrees up to
199, and on sequences of 3000 normal steps (Appendix A, test listing).

5.2 Charges. The program records every operation it performs, by kind and size, in a histogram (Appendix B),
and charges it first under the rules of our earlier entries (loose; they also fix which product and division
algorithm runs, by the cheaper loose charge):
- a product of polynomials of lengths m1, m2: the cheaper of classical (4 m1 m2 for load, load,
  multiply, add per coefficient pair, plus m1 m2 / 2 loop control and 2(m1+m2-1) for zeroing and
  storing the output) and transform (3 T(N) + 5N + 2(m1+m2) + (N-m1) + (N-m2) + N/2: two forward
  and one inverse transform, the scaled pointwise product, copying both inputs into their padded
  buffers, the padding stores and loop control, N the least 3*2^j >= m1+m2-1, T from 4.1), the
  choice being recorded;
- addition/subtraction of length m: 4m + m/2; copy, shift or truncation: 2m + m/2; field inversion
  380 (a conservative round-up of the 330-unit ladder); monic normalisation 380 + m + m/2;
  division inner loops carry the same 1/2 unit per coefficient iteration;
- division of degree n by degree m, L = n-m+1: the cheaper of classical
  380 + L(4(m+1) + 2) + L(m+1)/2 + 2(n+1) + (n+1)/2 and Newton division (inverse of the reversed divisor at precision
  L as in 4.3, two products, 4(m+1) + 2(n+1)); the choice is recorded per division in the histogram;
- wrapped matrix-vector step at length N (inputs of lengths la, lb, entries of lengths l_ij):
  loading a and b 5/2 min(l,N) + 9/2 max(0,l-N) + 3/2 max(0,N-l) each; per nonzero entry 7/2 l
  (load, scale by 1/N, store, loop) + 3/2 (N-l) + T(N); 2 T(N) for the transforms of a and b; per
  nonzero output row 9/2 N for the first pointwise term and 13/2 N for the second; one inverse
  T(N) per row;
- shared-transform 2x2 matrix product at length N: per nonzero entry of the right factor
  7/2 l + 3/2 (N-l) + T(N), of the left factor 5/2 l + 3/2 (N-l) + T(N); per row one pointwise
  pass of 29/2 N (six loads, four multiplications, two additions, two stores, loop); T(N) per
  nonzero output entry.
- Roots of G: when deg G = 1 the root is -G_0 of the monic G (1 unit). When deg G >= 2 the
  program splits G by equal-degree factorisation with shifts c_n = n + 1 (1 unit each);
  (X + c)^((p-1)/2) mod G is charged as 253 schoolbook modular squarings
  (4d^2 + (d-1)(4d+2) + (d^2 + (d-1)d)/2 each) and popcount((p-1)/2) - 1 multiplications by X + c
  (4d + (d-1)(4d+2) + (d + (d-1)d)/2 each), the gcd with G by classical Euclid as above, recursing
  on both factors. On this instance deg G = 2 and the splitting branch was executed as charged.
- explicit overhead, charged per trial from the histogram by `gcd_overhead`: +N per transform
  product (the 1/2 loop unit of each of its two copy/pad loops), +2m per monic normalisation (load
  and store per coefficient), +5N per wrapped matrix-vector step and +10N per shared-transform
  matrix product (compaction of outputs into coefficient-length buffers, 5/2 per word), and +5 per
  recorded operation (degree scans and recursion bookkeeping).
Memory: the live coefficient words of every polynomial held by an active frame of the
recursion (inputs, matrix entries, remainders; views add none) plus scratch: 2N words for a
transform product, m1+m2-1 for a classical one, (n+1) + L for a division, 4N for a wrapped
matrix-vector step, and for a shared-transform matrix product 4N (right-factor transforms) + 2N
(the row's left-factor transforms, overwritten by its outputs) + the first row's outputs while the
second row runs.

5.2s Strict re-pricing (the claim). The same histogram, with the same algorithm choices, is priced under the
convention of 4.0 by `charge_strict` in `halfgcd_charge.py` (Appendix A), item by item:
- transform product: 3 T_strict(N) + the pointwise pass (2 loads, 2 multiplications, 1 store per point, LP(N))
  + for each input a copy-and-pad loop (m_i loads and N stores at 2 each, LP(N));
- classical product: 6 per coefficient pair (two loads at 2, multiplication, addition), 2 per output store,
  3 per output iteration plus 2 on exit, and LP(e_k) for the inner loop of output k over its e_k terms;
- classical division of degree n by m, L = n - m + 1: inversion 380, copy of the dividend (4 per word, LP),
  per quotient coefficient 5 (load of the top coefficient, multiplication, store of the quotient) + 3 (loop)
  + the update of m + 1 words (two loads, multiplication, subtraction, store: 8 per word, LP(m + 1)), 2 on exit;
- Newton division: the series inverse step by step as in 4.3, the two products as above, the remainder pass
  (two loads, subtraction, store: 7 per word, LP) and the copy of the dividend;
- wrapped matrix-vector step: loading a and b (copy 4 per word, fold 7 per word, pad 2 per word, each with its
  LP), per nonzero matrix entry 5 per word (load, scale, store) + 2 per pad word + LPs + T_strict(N), 2 T_strict(N)
  for a and b, per nonzero output row a pass of 7 per point for its first term and 10 per point for a second,
  one inverse T_strict(N);
- shared-transform matrix product: right-factor entries as matrix entries above, left-factor entries 4 per word
  + 2 per pad word + LPs, T_strict(N) per entry, per row a pass of 22 per point (six loads, four
  multiplications, two additions, two stores) and T_strict(N) per nonzero output entry;
- addition/subtraction 7 per word + LP, copy 4 per word + LP, monic normalisation 380 + 5 per word + LP, a
  linear root 3 (load, negation, register); the splitting branch (deg G >= 2) by the same item rules;
- overhead: output compaction of each wrapped step (two outputs) and shared product (four entries) at 4 per
  word + LP, and 10 per recorded operation for degree scans and recursion bookkeeping (twice the loose 5).

5.3 Executed count. On this instance (trial 1, deg g_c = 976,562) the stage performed
1,937,489 classical and 2,979 transform products, 976,560 classical and 0 Newton divisions in the half-gcd (top-level reduction n0/12 per call, base case below 48) and charged 21,970,487,735 units under the loose rules with a peak of 6,535,600 live words; the
charge of the root stage was 9,451 (together 21,970,497,186), and the explicit overhead added
343,438,047. Strict re-pricing of the whole stage (5.2s, overhead included): 29,290,849,460 units. The remainder sequence was normal: every division in the histogram is of degree n by n - 1 and every wrapped step has deg a - deg b = 1. 28,668 products had a zero operand and were charged 0. Charge by kind (each row recomputed by `halfgcd_charge.py`
from the histogram of Appendix B):

| kind | strict units | loose units |
|---|---:|---:|
| matvec_wrap | 17,887,474,383 | 14,148,489,058.5 |
| matmul_shared | 7,467,105,001 | 5,874,092,884 |
| division_classical | 1,972,969,287 | 1,232,284,973 |
| product_classical | 1,010,040,517 | 507,107,071.5 |
| addsub | 334,709,575 | 200,217,667.5 |
| product_ntt | 11,230,830 | 8,296,515 |
| edf_powmod | 23,592 | 8,237 |
| monic | 795 | 767.5 |
| edf_constsub | 19 | 9 |
| root_linear | 6 | 2 |
| edf_draw | 1 | 1 |
| total (before overhead) | 28,683,554,006 | 21,970,497,186 |

Appendix B reproduces `gcd_trace_r3_t1.json`, the
histogram of every charged operation by kind and size; `halfgcd_charge.py` (Appendix A,
standard library only) recomputes the charge from that histogram and the rules above.


## 6. Totals

Strict convention of 4.0 (the claim), with the loose rule of our earlier entries beside it for comparison:

| phase | strict units (claim) | loose units | peak live words |
|---|---:|---:|---:|
| setup (4.4) | 192,552 | 180,112 | |
| trial 1: centre c = 1 and Y - 1 (4.4) | 6 | 3 | |
| trial 1: build, values of g_c on O1 (4.2) | 1,001,390,072 | 752,877,566 | 1,048,640 |
| trial 1: interpolation of g_c (4.3) | 84,060,886 2/3 | 67,458,389 1/3 | |
| trial 1: start residue (Newton, cyclic product) (4.3) | 581,605,938 1/3 | 466,023,674 1/6 | |
| trial 1: batch inversion Ginv1 (4.3) | 14,418,299 | 9,437,560.5 | |
| trial 1: start values on O1, O2; G2h (4.3) | 248,643,714 | 200,802,304 | |
| trial 1: 235 Montgomery squarings (45 with X) (4.3) | 83,174,837,081 2/3 | 66,394,084,603 1/3 | 4,194,304 |
| trial 1: final conversion, interpolation, recovery of g_c (4.3) | 353,413,980 2/3 | 281,892,181 1/3 | |
| trial 1: half-gcd, roots and overhead (5.2, 5.2s) | 29,290,849,460 | 22,313,935,233 | 6,535,600 |
| trial 1: finish (4.5) | 8,709 | 8,709 | |
| **total** | **114,749,420,699 1/3** | **90,486,700,335 2/3** | **6,535,600** |

Total W = 114,749,420,699 1/3 units; T = W / 279 = 411,288,246.23; `time_log2` = log2 T = 28.615575, submitted as
28.61558 (ceiling at five decimals; never a downward rounding). Under the loose rule the same run is
90,486,700,335 2/3 units, `time_log2` 28.272865; the strict figure is the larger and is the one claimed.
Trials executed: trial 1 (c = 1): deg G = 2.

6.1 Declared bounds. Declared bounds against the true values, checked in exact integer arithmetic (gen_proof_mont.py): time: W^100000 <= 2^2861558 * 279^100000, i.e. log2(W / 279) = 28.615574602 <= 28.61558, holds; memory: 210,187,776^100000 <= 2^2764711, i.e. log2(210,187,776) = 27.647103527 <= 27.64711, holds; preprocessing 0: every constant (Lemma 1, the transform roots and twiddle steps, the leading coefficient, the Tonelli-Shanks constant) is computed inside the run and charged in the setup row of W, nothing is computed before it; success probability 1: the procedure is deterministic and its executed run on the fixed target returned the certified pair (Section 7); no advice.
 `accounting.py` (Appendix A, standard library only) recomputes every row of
this table in both conventions from the sizes, the closed forms, the gcd histograms of Appendix B and the
recorded roots, and recomputes the pair(s) with a pure-Python permutation.

## 7. Success probability and the trial budget

The procedure reads no random coins; its only inputs are the pinned constants and the fixed centre order
c_i = i. Executed on this fixed target it performed exactly the operations charged above and returned the
certified pair at trial 1; a deterministic procedure that returns a pair on its only control path
has success probability 1 on this target. Every trial that ran is charged, including trials whose G had
degree 0. No expectation, extrapolation or heuristic enters the claim (`heuristics` is empty). The centre
order was fixed before the first execution and the run was made from trial 1; no centre was skipped or
selected. No other execution of this procedure at r = 3 was made; its gcd stage was later executed a second time on the same g_c and Y with 2^k wrapped lengths allowed, which is filed as a separate entry. The top-level reduction n0/12 was fixed before this run from the independent-instance sweeps at the degrees of r = 1 and r = 2, where it was the best fraction; at this degree the degrees-only schedule of `gcd_mock.py` (instance-free, validated against executed runs) gives strict half-gcd charges 2.658e10, 2.929e10 and 3.190e10 with peaks 6,657,670, 6,535,600 and 6,474,565 words for n0/8, n0/12 and n0/16, so n0/8 would have been about 0.008 bits cheaper on the normalized axis; this entry charges the run as executed, with n0/12. Every fraction returns the same G. The kernels were also executed on the unadmitted r = 0
instance during development.

Context only, not used by the claim: under the usual random-polynomial model the number of roots of g_c
that are nonzero squares is close to Poisson(1/2), so a centre succeeds with probability about
1 - e^(-1/2) = 0.39. Sensitivity: the half-gcd stage is 25.5% of W; tripling it would raise
`time_log2` to 29.2106.

## 8. Certificate

`certificates/message-a.bin` and `certificates/message-b.bin` encode the inputs of W1 = c + s and
W2 = c - s (nk then rho, 32 little-endian bytes each); further roots give message-a<k>.bin / message-b<k>.bin. The expected digest in
`certificates/manifest.json` is the common reduced hash 8e4912f5228858f90e46cbb635589e9c01383777416b05d3aa2d66e55752790f (pair 1: 79144d3d82b554a371b526c55f436564664ba8459b5355215730f4d0027ac124). Both inputs are canonical and the files
differ. The organizer checker recomputes the reduced permutation on each file; that check is independent of
every count above. A reader can also check from the certificate alone that both pairs lie on the line of
Lemma 1 with W1 + W2 = 2c.

## 9. Memory

Peak live storage is the maximum over the phases of the run: build 1,048,640 words, Montgomery stage
4,194,304 words, gcd stage 6,535,600 words (the half-gcd memory model of 5.2, executed on this
instance), so 6,535,600 words of 32 bytes, plus a fixed 2^20-byte allowance for code, constants, the
16-word register file of 4.0 and the stack (the kernels are a few thousand machine instructions; the
transform constants are at most 20 * 22 words; the pinned permutation constants at most 201 words; the prefix
stacks of the point generators 2 (k + 1) words; the recursion stack at most 20 frames of a few dozen words).
Total 210,187,776 bytes; log2 = 27.647104, submitted as `memory_log2_bytes` = 27.64711 (ceiling at five
decimals). The normalized cost axis with the submitted bounds is `time_log2` + max(0, `memory_log2_bytes` - 20)
= 36.26269; the claim keeps the two raw bounds separate.

## 10. Limitations, relation to prior entries and credits

The time bound is an operation count of the stated algorithm under the organizer's prices, not a wall-clock
measurement. The build stage and the whole Montgomery stage were executed by the instrumented kernels
themselves (pure Python, every pass counted in both conventions, compared phase by phase with the closed
forms during the run), and the result was compared with FLINT. The half-gcd was executed by the counted
program on the real instance (FLINT supplies the coefficient arithmetic of its leaf operations; the charge
is the executed schedule priced by the rules of 5.2 and 5.2s). The judge does not execute candidate code; the
certificate is the organizer-checked evidence of the outcome, and Appendix A reproduces every number. Every
self-test, cross-check and histogram is participant-produced.

Accounting convention. The claim uses the convention of 4.0: an address operation with every load and store,
3 per loop iteration (eight elements per iteration where unrolled) and 2 per loop exit, a declared 16-word
register file, which is how the executed-count entries on this board charge. For comparison only, the
looser rule of our earlier entries (one unit per load or store, no address operation, 1/2 unit of loop
control per streamed element) prices the same run at `time_log2` 28.272865, normalized 35.91997.

Credits. The two-round bypass line is the trick of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3);
tanctl (b86575d7-dc88-474d-a337-ccfaba496743, b257d730-1bdf-4078-88c1-15e0d4657031) brought the linearizing
line to this board, and Th0rgal (94e9246a-86ac-451b-b92b-0d14aa7345ea) and hecmas
(a18c0d0a-1112-426d-9e4f-829b57654284) the univariate root finding with an executed deterministic outcome.
The odd-part reduction F(c + s) - F(c - s) = 2 s G_c(s^2) and the deterministic centre order with every trial
charged are the methods of Jbenisek (767cdef0-485d-443a-92ec-652ee8166c4a) at r = 1 and 0xshikhar
(86ebd942-5d22-4786-b065-332ba3180792) at r = 2. The value-domain Montgomery squaring on O1 = H_n and
O2 = psi H_n (R = X^n - 1, R = -2 on O2, four transforms per step) and the Montgomery start residue are the
stage-C method of bradcush, introduced in 1aa56884-8e68-4aa8-87c7-ed38d0a3e65b (r = 21) and used at r = 3 in
4bcabff8-2863-4d70-a0d3-401da0cbe5fb. No code was reused from any of them; the kernels here are our own
(poseidon_mage, entries 186052af-551a-4146-962f-245da3bcefbe and 3a5f5d55-804a-4fd4-94eb-c915593d3dca) extended
with the point generator, the Montgomery step, the start residue, the batch inversion, the odd-part build and
the strict pricing. The half-gcd and root stage are those of our earlier entries, applied to g_c.

## Appendix A. Program listings

The executed driver (`attack_mont.py`; it uses `Target` and the cost constants of `attack_v4_ref.py`, the
driver of our earlier entries, whose `run` function is not used here), the instrumented transform and
Montgomery kernels with their closed forms in both conventions and self-tests (`ntt.py`, `mont.py`), the
counted half-gcd and root stage (`halfgcd.py`, `gcd_stage.py`, `roots.py`), the trace charge with its strict
re-pricing (`halfgcd_charge.py`), the standard-library reproduction (`accounting.py`), the generator of this
document (`gen_proof_mont.py`) and the closed-form comparisons quoted in the note (`levers_calc.py`; it also
imports the Barrett kernels `modsq.py` of our earlier entries, listed last). Run
`python accounting.py orchard-pallas-constants.json ledger_r3.json <dir>` with the gcd traces of Appendix B in
<dir> to recompute Section 6 and the pair; `python ntt.py` and `python mont.py` run the kernel self-tests
(the latter against FLINT).


### attack_mont.py

```python
"""attack_mont.py - counted, executed collision search on the reduced Orchard hash (r partial rounds).

Procedure (fixed before the first execution; centres c_i = i, i = 1, 2, 3, ..., every trial charged):
  line   two-round bypass (Bariant-Bouvier-Leurent-Perrin 2022): F(T') = lane-0 digest along the line,
         degree D = 5^(6+r) in the round-1 S-box output parameter T' (Target in attack_v4_ref.py).
  build  g_c(S) monic of degree m = (D-1)/2 with F(c+s) - F(c-s) = 2 a_D s g_c(s^2): its values on
         O1 = H_n (n = 3*2^k > m) in transform order, from 2n line evaluations F(c +- s_t),
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
    (roots of unity of orders 3*2^i and 2^i, i <= 30, their inverses and 1/N per length used: fewer than 440 constants of at
    most 380 units, 167,200 plus, strict, an address operation for each of their at most 440 stores), the leading-coefficient
    recursion with the inversion of 2 a_D, the Tonelli-Shanks constant, and the output bound (10,000 loose,
    doubled strict)."""
    from mont import V
    base = LEAD_BOUND(r) + EXP_COST(TS_T)
    return V(2000 + 167200 + base + 10000, 4000 + 167200 + 440 + base + 20000)


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
"""ntt.py - instrumented number-theoretic transform over the Pallas field, N = 3*2^k.

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
    """strict charge of one transform of length N = 3*2^k (same passes as T)."""
    k = log2_k(N)
    if not radix3(N):
        return k * (4 * Fraction(N, 2) + 2 * Fraction(2 * N, 3) + LP(N // 2)) + 4 * N + LP(N)
    return k * (4 * Fraction(N, 2) + 2 * Fraction(2 * N, 3) + LP(N // 2)) + (8 * Fraction(N, 3) + 4 * N + LP(N // 3))


def ntt_forward(a, ctr):
    """In place DIF transform of list a (length N = 3*2^k) with instrumented charges."""
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


def roots_bound_strict(d):
    """strict upper bound of the root stage of roots.py on a split polynomial of degree d <= 16 with at most EDF_CAP
    draws per call: at most 2d - 1 calls, each draw = shift (1) + (X + c)^((p-1)/2) mod G + constant subtraction +
    classical Euclid (at most d divisions of degree <= d) + monic, each call one exact division; 3 per linear root."""
    from halfgcd_charge import s_mulmod, s_mulx, s_division_classical, POP
    from ntt import LP
    if d <= 1:
        return Fraction(3 * d)
    draw = 1 + 253 * s_mulmod(d) + (POP - 1) * s_mulx(d) + 7 * d + LP(d) + d * s_division_classical(d, d - 1) + 380 + 5 * d + LP(d)
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


if __name__ == '__main__':
    if sys.argv[1] == '--selftest':
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


### accounting.py

```python
"""accounting.py - standard-library reproduction of every charged number of a ledger_r<r>.json written by
attack_mont.py (both conventions; the claim uses the strict one), and of the certified pair(s).
Usage: python accounting.py <orchard-pallas-constants.json> <ledger_r<r>.json> <dir with gcd_trace_r<r>_t<i>.json>
Needs ntt.py, mont.py, halfgcd_charge.py beside it (standard library only).
Recomputes: the setup; per trial the build BUILD(n, r), the six phases of the Montgomery stage (closed forms of
mont.py, equated to the instrumented kernels in its self-test and during the run), the half-gcd and root charge
from the trace histogram (loose rules and their strict re-pricing), the Tonelli-Shanks count and the finish;
totals, time_log2, memory and score; then each pair from (c, S) with a pure-Python permutation, and the
certificate bytes if present.
"""
import json, sys, os, math
from fractions import Fraction
from ntt import P, nice_length, mont_length
from mont import SETUP_POWER, PEAK_WORDS, PG, V, OPS
from halfgcd_charge import charge_from_trace, gcd_overhead, charge_strict

E = (P - 1) // 2
E5 = pow(5, -1, P - 1)
EXP = lambda e: (e.bit_length() - 1) + (bin(e).count('1') - 1)
ROOT5 = EXP(E5)
TS_T = (P - 1) >> 32
CODE_BYTES = 1 << 20


def EVAL(r): return OPS(arith=6 + 27 * 6 + 21 * r, load=6 + 12 * (6 + r))
def BUILD(n, r): return 2 * PG(n) + OPS(arith=4 * n, store=n, ctl=3 * n + 2) + (2 * n) * EVAL(r)
def LEAD_BOUND(r): return 24 * (8 + r) + 380 + 1
def SETUP(r):
    base = LEAD_BOUND(r) + EXP(TS_T)
    return V(2000 + 167200 + base + 10000, 4000 + 167200 + 440 + base + 20000)


def ts_count(a):
    """operation count of attack_mont.sqrt_counted on input a (registers only: same in both conventions)."""
    ops = EXP((TS_T - 1) // 2) + 2
    z = pow(5, TS_T, P); w = pow(a, (TS_T - 1) // 2, P); x = a * w % P; b = x * w % P
    Mv, cz = 32, z
    while True:
        ops += 1
        if b == 1:
            break
        i, bb = 0, b
        while bb != 1:
            bb = bb * bb % P; i += 1; ops += 5
        cc = cz
        for _ in range(Mv - i - 1):
            cc = cc * cc % P; ops += 4
        x = x * cc % P; cz = cc * cc % P; b = b * cz % P; Mv = i; ops += 6
    assert x * x % P == a
    return ops, x


def F(x): return Fraction(str(x))


def main(cpath, lpath, tdir):
    K = json.load(open(cpath)); L = json.load(open(lpath)); r = L['r']
    RC = [[int(x, 16) for x in row] for row in K['round_constants']]; M = [[int(x, 16) for x in row] for row in K['mds']]
    D = 5 ** (6 + r); m = (D - 1) // 2; n = mont_length(m + 1); C = 216 + 21 * r
    assert (D, m, n, C) == (L['D'], L['m'], L['n'], L['C'])
    S = SETUP(r)
    assert (F(L['setup']['loose']), F(L['setup']['strict'])) == (S.l, S.s)
    tot = {'loose': S.l, 'strict': S.s}
    phs, inf = SETUP_POWER(m, E)
    power = sum(phs.values(), V())
    print(f'r={r} D={D} m={m} n={n} C={C}; Montgomery stage: j={inf["j"]} L={inf["L"]} squarings={inf["n_squarings"]} '
          f'({inf["n_mulx"]} with X); step loose {inf["step_plain"].l} strict {inf["step_plain"].s}')
    print(f'setup: loose {S.l}, strict {S.s}')
    for tr in L['trials']:
        i = tr['trial']
        b = BUILD(n, r)
        assert (F(tr['build']['loose']), F(tr['build']['strict'])) == (b.l, b.s)
        assert (F(tr['power']['loose']), F(tr['power']['strict'])) == (power.l, power.s)
        for k, v in phs.items():
            assert (F(tr['power_phases'][k]['loose']), F(tr['power_phases'][k]['strict'])) == (v.l, v.s)
        hist = json.load(open(os.path.join(tdir, f'gcd_trace_r{r}_t{i}.json')))
        gch = charge_from_trace(hist); gi = int(gch) if gch.denominator == 1 else int(gch) + 1
        gl = gi + gcd_overhead(hist); gs = charge_strict(hist)
        assert (F(tr['gcd']['loose']), F(tr['gcd']['strict'])) == (gl, gs), (tr['gcd']['loose'], gl, tr['gcd']['strict'], gs)
        fin = 0
        if tr['deg_G'] >= 1:
            for Sx in tr['roots_S']:
                Sx = int(Sx); fin += 1
                if Sx == 0:
                    continue
                o, _ = ts_count(Sx)
                fin += o + 2 + 2 * (3 * ROOT5 + 8) + 2 * C + 8
        assert F(tr['finish']['loose']) == fin and F(tr['finish']['strict']) == fin
        row = {'loose': 3 + b.l + power.l + gl + fin, 'strict': 6 + b.s + power.s + gs + fin}
        for cv in row:
            assert row[cv] == F(tr['total_' + cv]), (cv, row[cv], tr['total_' + cv])
            tot[cv] += row[cv]
        print(f'  trial {i} (c = {tr["centre"]}): deg G = {tr["deg_G"]}')
        for name, lv, sv in (('centre, Y - 1', 3, 6), ('build', b.l, b.s), ('Montgomery stage', power.l, power.s),
                             ('half-gcd + roots + overhead', gl, gs), ('finish', fin, fin)):
            print(f'    {name:30s} loose {float(lv):>18,.1f}   strict {float(sv):>18,.1f}')
    peak = max(n + 64, PEAK_WORDS(m), max(tr['gcd']['peak_words'] for tr in L['trials']))
    assert peak == L['peak_words']
    mm = math.log2(peak * 32 + CODE_BYTES)
    assert abs(mm - L['memory_log2_bytes']) < 1e-12
    for cv in ('loose', 'strict'):
        assert tot[cv] == F(L['total_' + cv])
        t = math.log2(tot[cv] / C)
        assert abs(t - L['time_log2_' + cv]) < 1e-9
        print(f'{cv:6s}: W = {tot[cv]} ({float(tot[cv]):,.1f}); time_log2 {t:.6f}; memory_log2 {mm:.6f} '
              f'({peak:,} words + 1 MiB); score {t + max(0, mm - 20):.6f}')
    k = 2; CAP = 1 << 65; inv = lambda x: pow(x, P - 2, P); K5 = pow((CAP + RC[0][2]) % P, 5, P)
    i_, j_ = 0, 1; mu5 = (-M[k][0] * inv(M[k][1])) % P
    a, b_, e = M[i_][0], M[i_][1], (-(M[i_][2] * K5 + RC[1][i_])) % P
    c, d, f = M[j_][0], M[j_][1], (-(M[j_][2] * K5 + RC[1][j_])) % P
    det = (a * d - b_ * c) % P; di = inv(det); A0 = ((e * d - b_ * f) * di) % P; B0 = ((a * f - e * c) * di) % P

    def inputs(Tp):
        T_ = pow(Tp, E5, P); A = (T_ + A0) % P; B = (mu5 * T_ + B0) % P
        return (pow(A, E5, P) - RC[0][0]) % P, (pow(B, E5, P) - RC[0][1]) % P

    def H(x0, x1):
        s = [x0, x1, CAP]
        for idx in (*range(4), *range(4, 4 + r), *range(60, 64)):
            s = [(x + cc) % P for x, cc in zip(s, RC[idx])]
            for col in (range(3) if idx < 4 or idx >= 60 else range(1)):
                s[col] = pow(s[col], 5, P)
            s = [sum(cc * x for cc, x in zip(row, s)) % P for row in M]
        return s[0]
    last = L['trials'][-1]; cpkg = os.path.join(os.path.dirname(lpath), 'package', 'certificates')
    for kk, pr in enumerate(last['pairs']):
        Sx = int(pr['S']); _, s = ts_count(Sx); cc = last['centre']
        assert str(s) == pr['s']
        u, v = inputs((cc + s) % P), inputs((cc - s) % P)
        assert u != v and H(*u) == H(*v) and H(*u).to_bytes(32, 'little').hex() == pr['digest']
        enc = lambda x: int(x[0]).to_bytes(32, 'little') + int(x[1]).to_bytes(32, 'little')
        sa, sb = ('message-a.bin', 'message-b.bin') if kk == 0 else (f'message-a{kk}.bin', f'message-b{kk}.bin')
        if os.path.exists(os.path.join(cpkg, sa)):
            assert open(os.path.join(cpkg, sa), 'rb').read() == enc(u) and open(os.path.join(cpkg, sb), 'rb').read() == enc(v)
        print(f'pair {kk}: c = {cc}, W1 = c + s, W2 = c - s with s^2 = S; digest {pr["digest"]} (recomputed)')


if __name__ == '__main__':
    main(*sys.argv[1:4])
```


### gen_proof_mont.py

```python
"""Assemble proof.md + claim.json for <outdir>/package from ledger_r<r>.json, gcd traces and proof_parts/*.md.
The claim uses the strict convention (proof 4.0). Usage: python gen_proof_mont.py <r> <outdir>"""
import json, sys, os, math, glob
from fractions import Fraction
from ntt import T, T_S
from mont import SETUP_POWER, PEAK_WORDS, V
NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
E = (P - 1) // 2


def F(v):
    return Fraction(str(v))


def EX(v):
    v = F(v)
    whole = v.numerator // v.denominator
    rest = v - whole
    if rest == 0:
        return f'{whole:,}'
    if rest == Fraction(1, 2):
        return f'{whole:,}.5'
    return f'{whole:,} {rest}'


def ceil5(x):
    return math.ceil(x * 100000 - 1e-9) / 100000


r = int(sys.argv[1]); out = sys.argv[2]; VARIANT = sys.argv[3] if len(sys.argv) > 3 else ''
L = json.load(open(os.path.join(out, f'ledger_r{r}.json')))
last = L['trials'][-1]; D, m, n, C = L['D'], L['m'], L['n'], L['C']
phs, inf = SETUP_POWER(m, E)
power = sum(phs.values(), V())
from attack_mont import BUILD, EVAL, EVAL_ARITH, EVAL_LOADS, LEAD_BOUND, EXP_COST, TS_T
b = BUILD(n, r)
sub = {'R': r, 'LASTP': 3 + r, 'C': C, 'D': f'{D:,}', 'M': f'{m:,}', 'N': f'{n:,}', 'LASTTRIAL': last['trial'],
       'TRIAL': last['trial'], 'FRAC': L['gcd_params']['top_fraction'],
       'WRAPN': ('the least 3*2^j or 2^j' if (VARIANT == 'b' or L['gcd_params'].get('pow2')) else 'the least 3*2^j') + ' (also for the shared matrix products)' if (VARIANT == 'b' or L['gcd_params'].get('pow2')) else 'the least 3*2^j',
       'FRACTEXT': (('The top-level reduction n0/%d was chosen by a sweep on an independent instance of the same degree (a pseudo-random monic polynomial of degree %s, not a line polynomial; `gcd_sweep_indep.py` in Appendix A, its log in Appendix B); every fraction returns the same G on the target, so the choice does not depend on the target.' % (L['gcd_params']['top_fraction'], f"{L['m']:,}")) if r in (1, 2) else
                    ('The top-level reduction n0/%d was fixed before this run from the independent-instance sweeps at the degrees of r = 1 and r = 2, where it was the best fraction; at this degree the degrees-only schedule of `gcd_mock.py` (instance-free, validated against executed runs) gives strict half-gcd charges 2.658e10, 2.929e10 and 3.190e10 with peaks 6,657,670, 6,535,600 and 6,474,565 words for n0/8, n0/12 and n0/16, so n0/8 would have been about 0.008 bits cheaper on the normalized axis; this entry charges the run as executed, with n0/12. Every fraction returns the same G.' % L['gcd_params']['top_fraction'])),
       'EARLIER': {1: 'An earlier execution of the procedure used the top-level reduction n0/4 in the half-gcd (same centres, same g_c, Y, G and pair; strict 26.91184, gcd peak 225,907 words).',
                   2: 'One earlier execution of this procedure at r = 2, under the looser pricing, was stopped during the powering stage before any gcd was computed; no result of it is used.',
                   3: 'No other execution of this procedure at r = 3 was made; its gcd stage was later executed a second time on the same g_c and Y with 2^k wrapped lengths allowed, which is filed as a separate entry.'}.get(r, '') if VARIANT != 'b' else
                  ('The build and the Montgomery stage charged here are those of the single executed run of this procedure at r = 3 (they are deterministic and their counts are recorded in the ledger of that run). Its gcd stage was executed first with 3 * 2^k wrapped lengths (strict charge 2.929e10, peak 6,535,600 words; that execution is filed as our separate r = 3 entry) and then a second time, on the same g_c and Y rebuilt by the same build and confirmed by identical roots, with 2^k wrapped lengths allowed; that second execution is the one charged here.'), 'A': f'{1 << inf["j"]:,}', 'J': inf['j'], 'L': f'{inf["L"]:,}', 'NSQ': inf['n_squarings'],
       'NMX': inf['n_mulx'], 'TN': EX(T_S(n)), 'TNL': EX(T(n)), 'EVALA': EVAL_ARITH(r), 'EVALL': EVAL_LOADS(r),
       'EVAL': EX(EVAL(r).s), 'RPART': '1 partial round' if r == 1 else f'{r} partial rounds',
       'BUILD': EX(b.s), 'BUILDL': EX(b.l), 'PH_G': EX(phs['g_values'].s), 'PH_S': EX(phs['start_residue'].s),
       'PH_B': EX(phs['batch_inverse'].s), 'PH_T': EX(phs['tables'].s), 'STEP': EX(inf['step_plain'].s),
       'STEPL': EX(inf['step_plain'].l), 'STEPX': EX(inf['step_mulx'].s), 'PH_P': EX(phs['powering'].s),
       'PH_F': EX(phs['finish'].s), 'POWER': EX(power.s), 'POWERL': EX(power.l), 'PEAKPOW': f'{PEAK_WORDS(m):,}',
       'LEADB': f'{LEAD_BOUND(r):,}', 'TSC': f'{EXP_COST(TS_T):,}', 'SETUP': EX(L['setup']['strict']),
       'FINISH': EX(last['finish']['strict']), 'DIGEST': last['pairs'][0]['digest'], 'DIGEST2': ''.join(f' (pair {k}: {pr["digest"]})' for k, pr in enumerate(last['pairs']) if k),
       'EXTRACERT': ('' if len(last['pairs']) == 1 else '; further roots give message-a<k>.bin / message-b<k>.bin')}
sub['TRIALLIST'] = '; '.join(f"trial {t['trial']} (c = {t['centre']}): deg G = {t['deg_G']}" for t in L['trials'])
rows = [('setup (4.4)', L['setup'], '')]
for t in L['trials']:
    i = t['trial']
    rows.append((f'trial {i}: centre c = {t["centre"]} and Y - 1 (4.4)', t['small'], ''))
    rows.append((f'trial {i}: build, values of g_c on O1 (4.2)', t['build'], L['memory_words']['build']))
    for k, lab in (('g_values', 'interpolation of g_c'), ('start_residue', 'start residue (Newton, cyclic product)'),
                   ('batch_inverse', 'batch inversion Ginv1'), ('tables', 'start values on O1, O2; G2h'),
                   ('powering', f'{inf["n_squarings"]} Montgomery squarings ({inf["n_mulx"]} with X)'),
                   ('finish', 'final conversion, interpolation, recovery of g_c')):
        rows.append((f'trial {i}: {lab} (4.3)', t['power_phases'][k], L['memory_words']['power'] if k == 'powering' else ''))
    rows.append((f'trial {i}: half-gcd, roots and overhead (5.2, 5.2s)', t['gcd'], t['gcd']['peak_words']))
    rows.append((f'trial {i}: finish (4.5)', t['finish'], ''))
tbl = '| phase | strict units (claim) | loose units | peak live words |' + NL + '|---|---:|---:|---:|' + NL + NL.join(
    f"| {a} | {EX(v['strict'])} | {EX(v['loose'])} | {c:,} |" if c != '' else f"| {a} | {EX(v['strict'])} | {EX(v['loose'])} | |"
    for a, v, c in rows)
tbl += NL + f"| **total** | **{EX(L['total_strict'])}** | **{EX(L['total_loose'])}** | **{L['peak_words']:,}** |"
W = F(L['total_strict'])
tcl = ceil5(L['time_log2_strict']); mcl = ceil5(L['memory_log2_bytes'])
sub.update({'TOTALS': tbl, 'TOTALOPS': EX(W), 'TNORM': f'{float(W) / C:,.2f}', 'TLOG2': f"{L['time_log2_strict']:.6f}",
            'TCLAIM': f'{tcl:.5f}', 'TOTALOPSL': EX(L['total_loose']), 'TLOG2L': f"{L['time_log2_loose']:.6f}",
            'SCOREL': f"{L['score_loose']:.5f}",
            'MEM_BUILD': f"{L['memory_words']['build']:,}", 'MEM_POWER': f"{L['memory_words']['power']:,}",
            'MEM_GCD': f"{L['memory_words']['gcd']:,}", 'PEAKWORDS': f"{L['peak_words']:,}", 'MEMBYTES': f"{L['memory_bytes']:,}",
            'MEMLOG2': f"{L['memory_log2_bytes']:.6f}", 'MCLAIM': f'{mcl:.5f}', 'SCORE': f'{tcl + max(0, mcl - 20):.5f}'})
# declared bounds versus the true values, exact integer arithmetic (claims carry five decimals)
T5 = round(tcl * 100000); M5 = round(mcl * 100000)
Wi = F(L['total_strict']); Wi = -(-Wi.numerator // Wi.denominator)   # ceiling of the exact count
okT = Wi ** 100000 <= (1 << T5) * C ** 100000
okM = L['memory_bytes'] ** 100000 <= 1 << M5
assert okT and okM
sub['BOUNDS'] = (f"Declared bounds against the true values, checked in exact integer arithmetic (gen_proof_mont.py): "
                 f"time: W^100000 <= 2^{T5} * {C}^100000, i.e. log2(W / {C}) = {L['time_log2_strict']:.9f} <= {tcl:.5f}, holds; "
                 f"memory: {L['memory_bytes']:,}^100000 <= 2^{M5}, i.e. log2({L['memory_bytes']:,}) = {L['memory_log2_bytes']:.9f} <= {mcl:.5f}, holds; "
                 f"preprocessing 0: every constant (Lemma 1, the transform roots and twiddle steps, the leading coefficient, the "
                 f"Tonelli-Shanks constant) is computed inside the run and charged in the setup row of W, nothing is computed before it; "
                 f"success probability 1: the procedure is deterministic and its executed run on the fixed target returned the certified "
                 f"pair (Section 7); no advice.")
gsum = sum(F(t['gcd']['strict']) for t in L['trials'])
sub['GCDSHARE'] = f'{float(gsum / W) * 100:.1f}%'
sub['GCDX3'] = f'{math.log2(float(W + 2 * gsum) / C):.4f}'
gc = last['gcd']['detail']
sub.update({'GCDOPS': EX(F(gc.get('gcd_ops', 0))), 'GCDPEAK': f"{int(gc.get('peak_words', 0)):,}",
            'ROOTOPS': EX(F(gc.get('roots_ops', 0))), 'GCDPLUSROOT': EX(F(gc.get('gcd_ops', 0)) + F(gc.get('roots_ops', 0))),
            'GCDOVER': EX(last['gcd']['loose_overhead']), 'GCDSTRICT': EX(last['gcd']['strict']),
            'GCDSUMMARY': (f"{gc.get('gcd_products', {}).get('classical', 0):,} classical and {gc.get('gcd_products', {}).get('ntt', 0):,} transform products, "
                           f"{gc.get('gcd_divisions', {}).get('classical', 0):,} classical and {gc.get('gcd_divisions', {}).get('newton', 0):,} Newton divisions in the half-gcd "
                           f"(top-level reduction n0/{L['gcd_params']['top_fraction']} per call, base case below {L['gcd_params']['cutoff']})")})
gd = last['deg_G']
sub['ROOTBRANCH'] = ('On this instance deg G = 1, so the splitting branch was not executed.' if gd == 1 else
                     f'On this instance deg G = {gd} and the splitting branch was executed as charged.')
from halfgcd_charge import charge_by_kind, charge_by_kind_strict
h = json.load(open(os.path.join(out, f'gcd_trace_r{r}_t{last["trial"]}.json')))
kl, ks = charge_by_kind(h), charge_by_kind_strict(h)
krows = sorted(((k, ks[k], kl[k]) for k in kl if kl[k] or ks[k]), key=lambda x: -x[1])
sub['GCDKINDS'] = ('| kind | strict units | loose units |' + NL + '|---|---:|---:|' + NL + NL.join(f'| {k} | {EX(s)} | {EX(l)} |' for k, s, l in krows)
                   + NL + f'| total (before overhead) | {EX(sum(ks.values(), Fraction(0)))} | {EX(sum(kl.values(), Fraction(0)))} |')
divs = h.get('division_classical', {}); mv = h.get('matvec_wrap', {})
normal = all(int(k.split(',')[0]) - int(k.split(',')[1]) == 1 for k in divs) and all(int(k.split(',')[0]) - int(k.split(',')[1]) == 1 for k in mv)
zero = sum(h.get('product_zero', {}).values())
sub['GCDNORMAL'] = (('The remainder sequence was normal: every division in the histogram is of degree n by n - 1 and every wrapped step has deg a - deg b = 1. ' if normal else '')
                    + f'{zero:,} products had a zero operand and were charged 0.')
parts = sorted(glob.glob(os.path.join(HERE, 'proof_parts', '*.md')))
text = NL.join(open(p, encoding='utf-8').read() for p in parts)
for k, v in sub.items():
    text = text.replace(f'@@{k}@@', str(v))
left = sorted(set(w for w in text.split('@@')[1::2]))
assert not left, ('UNFILLED', left)
APP = ['attack_mont.py', 'attack_v4_ref.py', 'ntt.py', 'mont.py', 'halfgcd.py', 'gcd_stage.py', 'roots.py', 'halfgcd_charge.py', 'gcd_mock.py',
       'accounting.py', 'gen_proof_mont.py', 'levers_calc.py', 'gcd_sweep_indep.py', 'modsq.py']
app = ['', '## Appendix A. Program listings', '',
       'The executed driver (`attack_mont.py`; it uses `Target` and the cost constants of `attack_v4_ref.py`, the',
       'driver of our earlier entries, whose `run` function is not used here), the instrumented transform and',
       'Montgomery kernels with their closed forms in both conventions and self-tests (`ntt.py`, `mont.py`), the',
       'counted half-gcd and root stage (`halfgcd.py`, `gcd_stage.py`, `roots.py`), the trace charge with its strict',
       're-pricing (`halfgcd_charge.py`), the standard-library reproduction (`accounting.py`), the generator of this',
       'document (`gen_proof_mont.py`) and the closed-form comparisons quoted in the note (`levers_calc.py`; it also',
       'imports the Barrett kernels `modsq.py` of our earlier entries, listed last). Run',
       f'`python accounting.py orchard-pallas-constants.json ledger_r{r}.json <dir>` with the gcd traces of Appendix B in',
       '<dir> to recompute Section 6 and the pair; `python ntt.py` and `python mont.py` run the kernel self-tests',
       '(the latter against FLINT).', '']
for fn in APP:
    src = open(os.path.join(HERE, fn), encoding='utf-8').read()
    app += ['', f'### {fn}', '', '```python', src.rstrip(), '```', '']
app += ['', '## Appendix B. Ledger and gcd trace histograms', '', f'`ledger_r{r}.json`:', '', '```json',
        open(os.path.join(out, f'ledger_r{r}.json'), encoding='utf-8').read().rstrip(), '```', '']
sw = os.path.join(HERE, '..', 'ledger', f'gcd_sweep_indep_r{r}.jsonl')
if os.path.exists(sw):
    app += [f'`gcd_sweep_indep_r{r}.jsonl` (the independent-instance sweep that fixed the top-level reduction, Section 7):', '', '```json',
            open(sw, encoding='utf-8').read().rstrip(), '```', '']
for t in L['trials']:
    tpp = os.path.join(out, f'gcd_trace_r{r}_t{t["trial"]}.json')
    app += [f'`gcd_trace_r{r}_t{t["trial"]}.json` (trial {t["trial"]}):', '', '```json', open(tpp, encoding='utf-8').read().rstrip(), '```', '']
text += NL.join(app)
pk = os.path.join(out, 'package'); os.makedirs(pk, exist_ok=True)
open(os.path.join(pk, 'proof.md'), 'w', encoding='utf-8', newline=NL).write(text)
claim = {"schema_version": 3, "submission_state": "ready", "target_profile": f"poseidon-orchard-r{r}-prefix-v1",
         "attack_class": "ordinary-collision", "rounds": r,
         "claim": {"time_log2": tcl, "time_unit": "target-compressions", "memory_log2_bytes": mcl, "preprocessing_log2": 0,
                   "success_probability": 1, "nonuniform_advice_log2_bytes": 0},
         "restrictions": [], "baseline_improved": f"poseidon-orchard-r{r}-nominal-v2",
         "certificate_manifest": "certificates/manifest.json", "lane": "exploratory", "heuristics": []}
json.dump(claim, open(os.path.join(pk, 'claim.json'), 'w', newline=NL), indent=2)
print('wrote', pk, 'proof bytes', len(text.encode()), 'claim', claim['claim'], 'score', round(tcl + max(0, mcl - 20), 5))
```


### levers_calc.py

```python
"""levers_calc.py - closed-form comparisons (loose rule on both sides, so Barrett and Montgomery are priced alike) behind the lever ledger (standard library + kit kernels).
Prints JSON: per r, the Barrett pipeline of our earlier entries at modulus degree D-1 (full line
polynomial) and at m (odd part), the Montgomery value-domain stage at m, and the memory variants."""
import json, math
from fractions import Fraction
from ntt import T, nice_length
from modsq import SQ, MULX, NEWTON, CACHE, sizes
from mont import SETUP_POWER, PEAK_WORDS
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
E = (P - 1) // 2


def barrett_stage(Dq, nsq, nmx):
    """our earlier Barrett powering at modulus degree Dq (INVQ cached, QN1 transient): ops, peak words."""
    N1, N2 = sizes(Dq)
    ops = NEWTON(Dq) + CACHE(Dq - 1, N2) + nsq * SQ(Dq, False) + nmx * MULX(Dq)
    peak = Dq + 1 + N1 + N2 + N2
    return ops, peak


out = {}
for r in (1, 2, 3, 4, 5):
    D = 5 ** (6 + r); m = (D - 1) // 2; C = 216 + 21 * r
    k0f = (D - 1).bit_length() - 1
    full = barrett_stage(D - 1, 254 - k0f, 60) if r <= 2 else None
    k0h = m.bit_length() - 1
    half = barrett_stage(m, 253 - k0h, 45)
    ph, inf = SETUP_POWER(m, E)
    mont = sum((v.l for v in ph.values()), Fraction(0))
    n = inf['n']
    row = {'D': D, 'm': m, 'n': n,
           'barrett_half_ops': float(half[0]), 'barrett_half_peak_words': half[1],
           'barrett_half_step': float(SQ(m, False)),
           'mont_ops': float(mont), 'mont_step': float(inf['step_plain'].l), 'mont_peak_words': PEAK_WORDS(m),
           'step_ratio_barrett_over_mont': float(SQ(m, False) / inf['step_plain'].l),
           'time_bits_saved_by_mont': math.log2(float(half[0] / mont)),
           'mem_bits_saved_by_mont': math.log2((half[1] * 32 + 2 ** 20) / (PEAK_WORDS(m) * 32 + 2 ** 20)),
           # variant: recompute Ginv1 and G2h every step from g (keep g, m words): +2T + 13n per step
           'variant_recompute_tables_time_bits': math.log2(float((mont + inf['n_squarings'] * (2 * T(n) + 13 * n)) / mont)),
           'variant_recompute_tables_mem_bits': math.log2((PEAK_WORDS(m) * 32 + 2 ** 20) / ((2 * n + m) * 32 + 2 ** 20)),
           # variant: drop A2 (3 buffers), recompute A2 by inverse+forward each step: +2T per step
           'variant_drop_A2_time_bits': math.log2(float((mont + inf['n_squarings'] * 2 * T(n)) / mont)),
           'variant_drop_A2_mem_bits': math.log2((4 * n * 32 + 2 ** 20) / (3 * n * 32 + 2 ** 20))}
    if full:
        row.update({'barrett_full_ops': float(full[0]), 'barrett_full_peak_words': full[1],
                    'time_bits_saved_by_odd_part': math.log2(float(full[0] / half[0])),
                    'mem_bits_saved_by_odd_part': math.log2((full[1] * 32 + 2 ** 20) / (half[1] * 32 + 2 ** 20))})
    out[r] = row
print(json.dumps(out, indent=1))
```


### gcd_sweep_indep.py

```python
"""gcd_sweep_indep.py <m> <seed> <fractions...>: choose the half-gcd top-level reduction on an INDEPENDENT instance.
The instance is a pseudo-random monic polynomial g of degree m over F_p (coefficients from SHA-256 of
"poseidon_mage gcd sweep <seed> <i>"), not a line polynomial, and Y = X^((p-1)/2) mod g. For each top-level
fraction the counted half-gcd of (g, Y - 1) is run and its strict charge and memory peak are printed, together
with the normalized cost they would give beside a fixed Montgomery stage of degree m (peak 4n words) and a
fixed rest (all strict). Nothing here reads the target's line polynomial."""
import sys, json, math, hashlib
from fractions import Fraction
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
from ntt import P, mont_length
from mont import SETUP_POWER, PEAK_WORDS, V
from gcd_stage import gcd_stage
from halfgcd_charge import charge_strict

m = int(sys.argv[1]); seed = sys.argv[2]; fracs = [int(x) for x in sys.argv[3:]]
pctx = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)); X = pctx.gen()
co = [int.from_bytes(hashlib.sha256(f'poseidon_mage gcd sweep {seed} {i}'.encode()).digest(), 'little') % P for i in range(m)] + [1]
g = pctx(co); Y = X.pow_mod((P - 1) // 2, g)
ph, inf = SETUP_POWER(m, (P - 1) // 2)
power = sum(ph.values(), V()).s
fixed_peak = PEAK_WORDS(m)
C = 237
for fr in fracs:
    G, rts, led = gcd_stage(g, Y - 1, 1, cutoff=48, top_fraction=fr)
    gs = charge_strict(led['trace'])
    W = power + gs
    peak = max(fixed_peak, led['peak_words'])
    t = math.log2(float(W) / C); mm = math.log2(peak * 32 + 2 ** 20)
    print(json.dumps({'instance': f'random monic degree {m}, seed {seed}', 'top_fraction': fr, 'cutoff': 48, 'deg_G': G.degree(),
                      'gcd_strict': float(gs), 'gcd_peak_words': led['peak_words'], 'power_strict': float(power),
                      'score_power_plus_gcd': round(t + max(0, mm - 20), 5)}), flush=True)
```


### modsq.py

```python
"""modsq.py - counted Barrett modular squaring (wrap trick), Newton inverse, X-multiply.

Loop control: every per-element loop (pointwise, padding, copies, folds, subtraction,
reversal, X-multiply, Newton linear work, cache build) is charged 1/2 unit per element:
loops are unrolled 8 elements per iteration, one index add + one compare + one branch =
3 units per 8 elements, charged as 1/2 per element (conservative).

Polynomials are Python lists (coefficient i at index i) over the Pallas field.  q is monic
of degree D (list of D+1 entries), n = D-1, inv = rev(q)^-1 mod X^n (list of n entries).
N1 = smallest 3*2^k >= D, N2 = smallest 3*2^k >= 2D-1 (= 2*N1 for every D used here).

barrett_square (proof 4.2, S1-S3) on buffers Q (D+1), R (N1: holds a / a2f / rem), A (N2),
cached INVQ (N2, unscaled transform of inv) and optionally QN1 (N1, unscaled transform
of q).  Every store/load/field operation is charged on the Counter; closed forms SQ, NEWTON
and MULX reproduce the instrumented totals exactly (asserted in _selftest).
"""
from fractions import Fraction
from ntt import P, T, nice_length, ntt_forward, ntt_inverse, Counter


def sizes(D):
    N1, N2 = nice_length(D), nice_length(2 * D - 1)
    assert N2 == 2 * N1, (D, N1, N2)
    return N1, N2


def _pad(buf, lo, hi, ctr):
    for i in range(lo, hi):
        buf[i] = 0
    ctr.add(store=hi - lo, loop=Fraction(hi - lo, 2))


def _pointwise_mul(dst, src, N, ctr):
    """dst[i] = dst[i]*src[i]/N : 2 loads, 2 muls, 1 store."""
    invN = pow(N, P - 2, P)
    for i in range(N):
        dst[i] = (dst[i] * src[i] % P) * invN % P
    ctr.add(load=2 * N, mul=2 * N, store=N, loop=Fraction(N, 2))


def _pointwise_sq(dst, N, ctr):
    """dst[i] = dst[i]^2/N : 1 load, 2 muls, 1 store."""
    invN = pow(N, P - 2, P)
    for i in range(N):
        dst[i] = (dst[i] * dst[i] % P) * invN % P
    ctr.add(load=N, mul=2 * N, store=N, loop=Fraction(N, 2))


def transform_cache(coeffs, N, ctr):
    """Unscaled forward transform of coeffs padded to N (copy: load+store each; pad stores;
    one loop of N elements)."""
    buf = list(coeffs) + [0] * (N - len(coeffs))
    ctr.add(load=len(coeffs), store=N, loop=Fraction(N, 2))
    ntt_forward(buf, ctr)
    return buf


def CACHE(length, N):
    return 2 * length + (N - length) + Fraction(N, 2) + T(N)


def barrett_square(a, q, caches, ctr):
    """Return a^2 mod q (list of D coefficients); a has D entries, q is monic with D+1."""
    D = len(q) - 1
    n = D - 1
    N1, N2 = sizes(D)
    INVQ = caches['INVQ']
    # S1: A = a padded to N2, square via transform, a2 = a^2 exact (degree <= 2D-2).
    A = list(a) + [0] * (N2 - D)
    ctr.add(load=D, store=N2, loop=Fraction(N2, 2))   # copy a (D) + zero pad (N2-D), one loop
    ntt_forward(A, ctr)
    _pointwise_sq(A, N2, ctr)
    ntt_inverse(A, ctr)
    # fold a2 onto N1 into R: a2f[i] = a2[i] + a2[i+N1] for i < 2D-1-N1, else a2[i].
    nf = max(0, 2 * D - 1 - N1)
    R = A[:N1]
    ctr.add(load=N1, store=N1, loop=Fraction(N1, 2))
    for i in range(nf):
        R[i] = (R[i] + A[i + N1]) % P
    ctr.add(load=2 * nf, add=nf, store=nf, loop=Fraction(nf, 2))
    # S2: hi = reversed top n coefficients (indices D..2D-2) moved to A[0:n], rest zero.
    hi = [A[2 * D - 2 - t] for t in range(n)]
    for t in range(n):
        A[t] = hi[t]
    ctr.add(load=n, store=n, loop=Fraction(n, 2))
    _pad(A, n, N2, ctr)
    ntt_forward(A, ctr)
    _pointwise_mul(A, INVQ, N2, ctr)
    ntt_inverse(A, ctr)                   # A[0:n] = rev(quot)
    for t in range(n // 2):               # reverse in place: 2 loads + 2 stores per pair
        A[t], A[n - 1 - t] = A[n - 1 - t], A[t]
    ctr.add(load=2 * (n // 2), store=2 * (n // 2), loop=n // 2)   # 1/2 per element moved
    # S3: prod = quot * q mod (X^N1 - 1); rem = a2f - prod (first D coefficients).
    _pad(A, n, N1, ctr)                   # quot padded to N1 in A[0:N1]
    if 'QN1' in caches:
        QN1 = caches['QN1']
    else:                                 # transient transform of q into A[N1:N2]
        QN1 = transform_cache(q, N1, ctr)
    Af = A[:N1]
    ntt_forward(Af, ctr)
    _pointwise_mul(Af, QN1, N1, ctr)
    ntt_inverse(Af, ctr)                  # prod
    rem = [0] * D
    for i in range(D):
        rem[i] = (R[i] - Af[i]) % P
    ctr.add(load=2 * D, sub=D, store=D, loop=Fraction(D, 2))
    assert all((R[i] - Af[i]) % P == 0 for i in range(D, N1)), 'remainder tail must vanish'
    return rem


def SQ(D, cache_qn1=True):
    """Closed-form charge of one barrett_square."""
    n = D - 1
    N1, N2 = sizes(D)
    nf = max(0, 2 * D - 1 - N1)
    h = Fraction(1, 2)
    s1 = (D + N2 + h * N2) + 2 * T(N2) + (4 * N2 + h * N2) + (2 * N1 + h * N1) + (4 * nf + h * nf)
    s2 = (2 * n + h * n) + (N2 - n) * (1 + h) + 2 * T(N2) + (5 * N2 + h * N2) + 5 * (n // 2)
    s3 = (N1 - n) * (1 + h) + 2 * T(N1) + (5 * N1 + h * N1) + (4 * D + h * D)
    if not cache_qn1:
        s3 += CACHE(D + 1, N1)
    return s1 + s2 + s3


def newton_steps(D):
    """Yield (m, m2, N): precision m -> m2 = min(2m, n) using transform length N >= m2."""
    n = D - 1
    m = 1
    while m < n:
        m2 = min(2 * m, n)
        yield m, m2, nice_length(m2)
        m = m2


def newton_inverse(q, ctr):
    """inv = rev(q)^-1 mod X^(D-1) by Newton iteration with transforms of length N(m).

    Step m -> m2: F = rev(q) mod X^m2 (padded), G = g_m (padded); h = coefficients m..m2-1
    of F*G (cyclic length N >= m2 is exact there); g_m2 = g_m - X^m * (g_m * h mod X^(m2-m)).
    """
    D = len(q) - 1
    n = D - 1
    f = [q[D - i] for i in range(D + 1)]        # rev(q), f[0] = 1
    g = [1]
    for m, m2, N in newton_steps(D):
        F = [f[i] for i in range(m2)] + [0] * (N - m2)
        ctr.add(load=m2, store=N, loop=Fraction(N, 2))         # copy m2 + pad N-m2, one loop
        G = list(g) + [0] * (N - m)
        ctr.add(load=m, store=N, loop=Fraction(N, 2))          # copy m + pad N-m, one loop
        ntt_forward(F, ctr)
        ntt_forward(G, ctr)
        _pointwise_mul(F, G, N, ctr)
        ntt_inverse(F, ctr)                                    # F[m:m2] = h
        h = F[m:m2]
        for i in range(m2 - m):
            F[i] = h[i]
        ctr.add(load=m2 - m, store=m2 - m, loop=Fraction(m2 - m, 2))
        _pad(F, m2 - m, N, ctr)
        ntt_forward(F, ctr)
        _pointwise_mul(F, G, N, ctr)
        ntt_inverse(F, ctr)                                    # F[0:m2-m] = g*h mod X^(m2-m)
        g = g + [(-F[i]) % P for i in range(m2 - m)]
        ctr.add(load=m2 - m, sub=m2 - m, store=m2 - m, loop=Fraction(m2 - m, 2))
    assert len(g) == n
    return g


def NEWTON(D):
    total = Fraction(0)
    for m, m2, N in newton_steps(D):
        h = Fraction(1, 2)
        d = m2 - m
        total += (m2 + N + h * N) + (m + N + h * N) + 5 * T(N) + 2 * (5 * N + h * N)             + (2 * d + h * d) + (N - d) * (1 + h) + (3 * d + h * d)
    return total


def newton_peak_words(D):
    """q (D+1) + F (N) + G (N) + g (m2) at the largest step."""
    return max(D + 1 + 2 * N + m2 for _, m2, N in newton_steps(D))


def mulx(acc, q, ctr):
    """acc <- acc * X mod q in place; charged 6D + D/2 loop (one merged pass needs 5D + D/2)."""
    D = len(q) - 1
    lead = acc[D - 1]
    new = [0] + acc[:D - 1]
    for i in range(D):
        new[i] = (new[i] - lead * q[i]) % P
    acc[:] = new
    ctr.add(load=3 * D, store=D, mul=D, sub=D, loop=Fraction(D, 2))


def MULX(D):
    return 6 * D + Fraction(D, 2)


def _selftest():
    import random
    from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
    ctx = fmpz_mod_ctx(P)
    pctx = fmpz_mod_poly_ctx(ctx)
    rng = random.Random(7)
    for D in (125, 625, 3125):
        N1, N2 = sizes(D)
        q = [rng.randrange(P) for _ in range(D)] + [1]
        a = [rng.randrange(P) for _ in range(D)]
        c = Counter()
        inv = newton_inverse(q, c)
        assert c.total() == NEWTON(D), (D, c.total(), NEWTON(D))
        fq = pctx(q)
        revq = pctx([q[D - i] for i in range(D + 1)])
        prod = revq * pctx(inv)
        assert [int(prod[i]) for i in range(D - 1)] == [1] + [0] * (D - 2), 'newton inverse wrong'
        c1, c2 = Counter(), Counter()
        caches = {'INVQ': transform_cache(inv, N2, c1), 'QN1': transform_cache(q, N1, c2)}
        assert c1.total() == CACHE(D - 1, N2) and c2.total() == CACHE(D + 1, N1)
        for cache_qn1 in (True, False):
            cc = dict(caches) if cache_qn1 else {'INVQ': caches['INVQ']}
            c = Counter()
            rem = barrett_square(a, q, cc, c)
            assert c.total() == SQ(D, cache_qn1), (D, cache_qn1, c.total(), SQ(D, cache_qn1))
            ref = (pctx(a) * pctx(a)) % fq
            assert [int(ref[i]) for i in range(D)] == rem, 'barrett square wrong'
        c = Counter()
        acc = list(a)
        mulx(acc, q, c)
        ref = (pctx(a) * pctx([0, 1])) % fq
        assert [int(ref[i]) for i in range(D)] == acc and c.total() == MULX(D)
        print('D=%d N1=%d N2=%d NEWTON=%s SQ(cached)=%s SQ(uncached)=%s ok'
              % (D, N1, N2, NEWTON(D), SQ(D), SQ(D, False)))


if __name__ == '__main__':
    _selftest()
```


## Appendix B. Ledger and gcd trace histograms

`ledger_r3.json`:

```json
{
 "method": "odd-part line + value-domain Montgomery powering",
 "r": 3,
 "D": 1953125,
 "m": 976562,
 "n": 1048576,
 "C": 279,
 "centres": "c_i = i, i = 1, 2, ...",
 "gcd_params": {
  "cutoff": 48,
  "top_fraction": 12
 },
 "setup": {
  "loose": 180112,
  "strict": 192552
 },
 "trials": [
  {
   "trial": 1,
   "centre": 1,
   "build": {
    "loose": 752877566,
    "strict": 1001390072,
    "counters": {
     "mul": 487587838,
     "add": 1048576,
     "sub": 2097152,
     "load": 243269628,
     "store": 5242878,
     "loop": 0,
     "ctl": 13631494
    },
    "lp": 0
   },
   "t_build_s": 274.5,
   "t_power_s": 19114.6,
   "power_phases": {
    "g_values": {
     "loose": "202375168/3",
     "strict": "252182660/3"
    },
    "start_residue": {
     "loose": "2796142045/6",
     "strict": "1744817815/3"
    },
    "batch_inverse": {
     "loose": "18875121/2",
     "strict": 14418299
    },
    "tables": {
     "loose": 200802304,
     "strict": 248643714
    },
    "powering": {
     "loose": "199182253810/3",
     "strict": "249524511245/3"
    },
    "finish": {
     "loose": "845676544/3",
     "strict": "1060241942/3"
    }
   },
   "power": {
    "loose": "202259096138/3",
    "strict": "253370939701/3",
    "counters": {
     "mul": 22357999963,
     "add": 10263003136,
     "sub": 10017839433,
     "load": "28554899038/3",
     "store": "27061425937/3",
     "loop": 6006151499,
     "ctl": 235929690
    },
    "lp": 4504657695
   },
   "power_info": {
    "n": 1048576,
    "m": 976562,
    "j": 18,
    "L": 334159,
    "n_squarings": 235,
    "n_mulx": 45
   },
   "t_gcd_s": 482.7,
   "gcd": {
    "loose": 22313935233,
    "loose_ops": 21970497186,
    "loose_overhead": 343438047,
    "strict": 29290849460,
    "peak_words": 6535600,
    "detail": {
     "ops": 21970497186,
     "ops_exact": "21970497186",
     "peak_words": 6535600,
     "gcd_degree": 2,
     "roots": [
      "6350756120365531446699362883935434981386175007944985934070962846611323986188",
      "20800164752613949356536136794170786941868161818977435243312951265073715531642"
     ],
     "cutoff": 48,
     "top_fraction": 12,
     "gcd_ops": "21970487735",
     "roots_ops": "9451",
     "roots_draws": 1,
     "gcd_products": {
      "classical": 1937489,
      "ntt": 2979,
      "zero": 28668
     },
     "gcd_divisions": {
      "classical": 976560,
      "newton": 0
     },
     "gcd_lean": {
      "matvec_wrap": 28655,
      "matmul_shared": 26523
     },
     "lean": true,
     "shared_matmul": true,
     "peak_where": "matvec_wrap 4N",
     "roots_divisions": {
      "classical": 2,
      "newton": 0
     },
     "roots_products": {
      "classical": 0,
      "ntt": 0,
      "zero": 0
     },
     "roots_monic": 1,
     "roots_powmod": 1
    }
   },
   "small": {
    "loose": 3,
    "strict": 6
   },
   "deg_G": 2,
   "roots_S": [
    "6350756120365531446699362883935434981386175007944985934070962846611323986188",
    "20800164752613949356536136794170786941868161818977435243312951265073715531642"
   ],
   "finish": {
    "loose": 8709,
    "strict": 8709
   },
   "total_loose": "271459560671/3",
   "total_strict": "344247684442/3",
   "pairs": [
    {
     "S": "6350756120365531446699362883935434981386175007944985934070962846611323986188",
     "s": "17420250904943681438929888530914970157322586939839037680185222477806522967828",
     "W1": "17420250904943681438929888530914970157322586939839037680185222477806522967829",
     "W2": "11527771404385367416962857721257006806040469542102523035769454286543444662510",
     "a": [
      "927958055700944382445914868976575075479590180945702800660501179462091225840",
      "6930273144074389837054362021731591494550487099696675376244192085705239355871"
     ],
     "b": [
      "18583821805059136913829411981658571500260030617991470236662183155247647650744",
      "26347193088170882617471192662617604700412960056697991947720856795391630251658"
     ],
     "digest": "8e4912f5228858f90e46cbb635589e9c01383777416b05d3aa2d66e55752790f"
    },
    {
     "S": "20800164752613949356536136794170786941868161818977435243312951265073715531642",
     "s": "20580086113405596490938688532071087514489660972192117822613224065571682098030",
     "W1": "20580086113405596490938688532071087514489660972192117822613224065571682098031",
     "W2": "8367936195923452364954057720100889448873395509749442893341452698778285532308",
     "a": [
      "16618717281111257110493702762800614571873633125951671326000534245123785725603",
      "20000350598549233069061443984924127125821691995508999843533635033953485218121"
     ],
     "b": [
      "16681994104526109509070288402682727766927337607098083349981803731572818702028",
      "28115460049742470371225033854719217568841330495004515699523802149729176092772"
     ],
     "digest": "79144d3d82b554a371b526c55f436564664ba8459b5355215730f4d0027ac124"
    }
   ]
  }
 ],
 "memory_words": {
  "build": 1048640,
  "power": 4194304,
  "gcd": 6535600
 },
 "peak_words": 6535600,
 "memory_bytes": 210187776,
 "memory_log2_bytes": 27.647103527271547,
 "total_loose": "271460101007/3",
 "time_log2_loose": 28.272865398634956,
 "score_loose": 35.9199689259065,
 "total_strict": "344248262098/3",
 "time_log2_strict": 28.615574602291503,
 "score_strict": 36.26267812956305,
 "claim_convention": "strict",
 "lead_aD": "25209871089050154929315544992875247178311254155329174551879393624479531736827"
}
```

`gcd_trace_r3_t1.json` (trial 1):

```json
{"division_classical":{"80,79":4957,"79,78":5030,"78,77":6529,"77,76":6319,"76,75":8353,"75,74":8366,"74,73":8646,"73,72":9119,"72,71":10004,"71,70":10003,"70,69":11366,"69,68":11366,"68,67":12696,"67,66":12696,"66,65":14063,"65,64":14064,"64,63":15425,"63,62":15425,"62,61":17093,"61,60":17093,"60,59":18463,"59,58":18463,"58,57":19869,"57,56":19868,"56,55":21818,"55,54":21818,"54,53":23183,"53,52":23183,"52,51":25388,"51,50":25387,"50,49":26826,"49,48":26826,"48,47":28111,"47,46":27472,"46,45":27265,"45,44":26637,"44,43":26501,"43,42":25845,"42,41":25161,"41,40":24573,"120,119":205,"40,39":23698,"238,237":204,"117,116":681,"39,38":22335,"477,476":77,"118,117":645,"237,236":311,"954,953":34,"475,474":127,"235,234":335,"115,114":478,"38,37":20970,"1908,1907":13,"952,951":43,"474,473":150,"3816,3815":2,"1906,1905":21,"951,950":62,"7630,7629":2,"3813,3812":10,"1905,1904":21,"15259,15258":2,"3814,3813":11,"7627,7626":6,"3811,3810":9,"1903,1902":9,"949,948":31,"472,471":84,"234,233":136,"30519,30518":1,"7629,7628":5,"15258,15257":3,"61036,61035":1,"30516,30515":1,"15256,15255":2,"7626,7625":3,"122071,122070":1,"30517,30516":1,"61033,61032":1,"30514,30513":1,"15255,15254":1,"895181,895180":1,"109,108":446,"37,36":20008,"36,35":18652,"219,218":143,"108,107":672,"438,437":35,"217,216":302,"106,105":684,"35,34":17289,"874,873":35,"435,434":143,"216,215":333,"1749,1748":13,"436,435":108,"873,872":44,"3498,3497":3,"1747,1746":22,"871,870":64,"433,432":124,"214,213":197,"105,104":238,"6994,6993":3,"3495,3494":11,"1746,1745":21,"13987,13986":3,"3496,3495":10,"6991,6990":5,"3493,3492":8,"1744,1743":10,"870,869":34,"27975,27974":1,"6993,6992":5,"13986,13985":2,"55950,55949":1,"27973,27972":2,"13984,13983":3,"6990,6989":3,"111898,111897":1,"55947,55946":1,"27972,27971":1,"820581,820580":1,"100,99":407,"34,33":15960,"33,32":14593,"201,200":110,"99,98":675,"402,401":10,"199,198":297,"97,96":685,"32,31":13231,"802,801":10,"399,398":140,"198,197":336,"1603,1602":10,"400,399":100,"799,798":57,"397,396":147,"196,195":228,"96,95":340,"3205,3204":10,"801,800":43,"1600,1599":21,"798,797":55,"6411,6410":5,"1602,1601":22,"3204,3203":11,"12822,12821":2,"6409,6408":5,"3202,3201":11,"1599,1598":15,"25644,25643":1,"12820,12819":3,"6408,6407":6,"51286,51285":1,"25641,25640":2,"12819,12818":3,"102573,102572":1,"25642,25641":1,"51285,51284":1,"752198,752197":1,"93,92":786,"31,30":11563,"184,183":80,"90,89":2695,"30,29":10194,"367,366":80,"91,90":2016,"181,180":336,"88,87":2754,"29,28":8789,"735,734":31,"183,182":293,"366,365":137,"1470,1469":10,"733,732":49,"364,363":156,"180,179":259,"2938,2937":10,"1467,1466":21,"732,731":63,"5877,5876":4,"1468,1467":21,"2937,2936":10,"11754,11753":2,"5875,5874":6,"2935,2934":11,"1465,1464":18,"730,729":43,"363,362":87,"23506,23505":2,"11751,11750":3,"5874,5873":5,"47013,47012":1,"11752,11751":2,"23505,23504":1,"94026,94025":1,"47011,47010":1,"23503,23502":1,"11749,11748":1,"5872,5871":1,"2934,2933":1,"689513,689512":1,"85,84":2847,"28,27":6840,"169,168":39,"82,81":4762,"27,26":5475,"337,336":39,"84,83":4102,"166,165":333,"81,80":4722,"673,672":39,"168,167":277,"334,333":155,"165,164":300,"1347,1346":18,"336,335":122,"672,671":56,"2694,2693":7,"1345,1344":21,"670,669":66,"333,332":125,"5388,5387":2,"2692,2691":11,"1344,1343":23,"10774,10773":2,"5385,5384":5,"2691,2690":10,"21547,21546":2,"5386,5385":5,"10771,10770":3,"5383,5382":4,"2689,2688":4,"1342,1341":15,"669,668":36,"43095,43094":1,"10773,10772":2,"21546,21545":1,"86190,86189":1,"43093,43092":1,"21544,21543":1,"10770,10769":1,"632052,632051":1,"26,25":3272,"154,153":210,"25,24":1833,"309,308":70,"153,152":328,"618,617":21,"307,306":140,"151,150":341,"24,23":481,"1234,1233":21,"615,614":66,"306,305":162,"2469,2468":11,"616,615":49,"1233,1232":22,"4938,4937":5,"2467,2466":10,"1231,1230":27,"613,612":53,"304,303":96,"150,149":131,"9876,9875":3,"4936,4935":6,"2466,2465":11,"19752,19751":1,"9874,9873":2,"4935,4934":5,"39504,39503":1,"19750,19749":2,"9873,9872":3,"79006,79005":1,"39501,39500":1,"19749,19748":1,"579380,579379":1,"95,94":67,"94,93":714,"92,91":1387,"89,88":2016,"87,86":2208,"86,85":2808,"83,82":3492,"142,141":54,"283,282":55,"139,138":339,"567,566":9,"141,140":300,"282,281":139,"1132,1131":9,"564,563":64,"280,279":161,"138,137":285,"2263,2262":9,"565,564":45,"1129,1128":24,"562,561":66,"279,278":113,"4527,4526":4,"1131,1130":21,"2262,2261":11,"9054,9053":1,"4525,4524":5,"2260,2259":10,"1128,1127":23,"18106,18105":1,"9051,9050":2,"4524,4523":5,"36211,36210":1,"9052,9051":3,"18103,18102":2,"9049,9048":2,"4522,4521":2,"2259,2258":2,"72423,72422":1,"18105,18104":1,"36210,36209":1,"531097,531096":1,"130,129":92,"259,258":92,"127,126":339,"519,518":33,"129,128":317,"258,257":152,"1038,1037":12,"517,516":59,"256,255":166,"126,125":248,"2076,2075":1,"1036,1035":21,"516,515":72,"4150,4149":1,"2073,2072":10,"1035,1034":27,"8299,8298":1,"2074,2073":11,"4147,4146":6,"2071,2070":10,"1033,1032":20,"514,513":46,"255,254":76,"16597,16596":1,"4149,4148":5,"8296,8295":2,"4146,4145":4,"33193,33192":1,"8298,8297":3,"16594,16593":2,"8295,8294":2,"66387,66386":1,"16596,16595":1,"33192,33191":1,"486838,486837":1,"1902,1901":9,"3804,3803":4,"1900,1899":11,"948,947":31,"7608,7607":1,"3802,3801":5,"1899,1898":10,"15214,15213":1,"7605,7604":2,"3801,3800":5,"30427,30426":1,"7606,7605":3,"15211,15210":2,"7603,7602":2,"3799,3798":2,"1897,1896":3,"946,945":14,"471,470":39,"60855,60854":1,"15213,15212":1,"30426,30425":1,"446267,446266":1,"3487,3486":2,"1741,1740":10,"868,867":30,"432,431":56,"6973,6972":2,"1743,1742":11,"3484,3483":6,"1740,1739":9,"13947,13946":1,"3486,3485":5,"6972,6971":3,"27892,27891":1,"13944,13943":1,"6970,6969":2,"3483,3482":3,"55783,55782":1,"13945,13944":1,"27889,27888":1,"13942,13941":1,"6969,6968":1,"409077,409076":1,"3196,3195":4,"1596,1595":11,"796,795":32,"396,395":66,"6393,6392":1,"1597,1596":10,"3195,3194":5,"12784,12783":1,"6390,6389":2,"3193,3192":5,"1594,1593":8,"795,794":20,"25567,25566":1,"6391,6390":3,"12781,12780":2,"6388,6387":2,"3192,3191":2,"51135,51134":1,"12783,12782":1,"25566,25565":1,"374986,374985":1,"2931,2930":1,"1464,1463":11,"5860,5859":1,"2928,2927":5,"1462,1461":10,"729,728":28,"11719,11718":1,"2929,2928":5,"5857,5856":3,"2926,2925":5,"1461,1460":9,"23437,23436":1,"5859,5858":2,"11716,11715":1,"5856,5855":2,"46873,46872":1,"11718,11717":1,"23434,23433":1,"11715,11714":1,"343736,343735":1,"2686,2685":2,"1341,1340":10,"5371,5370":2,"2683,2682":6,"1339,1338":12,"667,666":24,"331,330":47,"163,162":66,"10743,10742":1,"2685,2684":5,"5370,5369":3,"21484,21483":1,"10740,10739":1,"5368,5367":2,"2682,2681":3,"42967,42966":1,"10741,10740":1,"21481,21480":1,"10738,10737":1,"5367,5366":1,"315090,315089":1,"2463,2462":1,"1230,1229":11,"4924,4923":1,"2460,2459":6,"1228,1227":12,"612,611":30,"9847,9846":1,"2461,2460":5,"4921,4920":2,"2458,2457":4,"1227,1226":9,"19693,19692":1,"4923,4922":3,"9844,9843":2,"4920,4919":2,"39387,39386":1,"9846,9845":1,"19692,19691":1,"288831,288830":1,"2257,2256":2,"1126,1125":11,"561,560":34,"4513,4512":2,"2254,2253":5,"1125,1124":13,"9027,9026":1,"2256,2255":6,"4512,4511":3,"18052,18051":1,"9024,9023":2,"4510,4509":3,"2253,2252":3,"36105,36104":1,"9025,9024":1,"18051,18050":1,"264760,264759":1,"2068,2067":6,"1032,1031":14,"4137,4136":3,"2067,2066":5,"8274,8273":2,"4135,4134":3,"2065,2064":5,"1030,1029":10,"513,512":22,"16548,16547":1,"8272,8271":1,"4134,4133":2,"33096,33095":1,"16546,16545":1,"8271,8270":1,"242695,242694":1,"3793,3792":1,"1894,1893":5,"945,944":15,"7585,7584":1,"1896,1895":5,"3790,3789":3,"1893,1892":5,"15169,15168":1,"3792,3791":2,"7582,7581":1,"3789,3788":2,"30337,30336":1,"7584,7583":1,"15166,15165":1,"7581,7580":1,"222469,222468":1,"1738,1737":4,"867,866":14,"3477,3476":1,"1737,1736":5,"6952,6951":1,"3474,3473":3,"1735,1734":6,"865,864":12,"430,429":26,"213,212":41,"13905,13904":1,"3475,3474":3,"6951,6950":2,"27808,27807":1,"13902,13901":1,"6949,6948":1,"3472,3471":1,"1734,1733":2,"203929,203928":1,"3187,3186":1,"1591,1590":6,"793,792":15,"394,393":30,"195,194":45,"6373,6372":1,"1593,1592":5,"3184,3183":2,"1590,1589":4,"12745,12744":1,"3186,3185":3,"6370,6369":2,"3183,3182":2,"25491,25490":1,"6372,6371":1,"12744,12743":1,"186934,186933":1,"2922,2921":1,"1459,1458":5,"727,726":16,"361,360":32,"178,177":48,"5842,5841":1,"2919,2918":2,"1458,1457":5,"11683,11682":1,"2920,2919":3,"5839,5838":2,"2917,2916":2,"1456,1455":4,"726,725":10,"23367,23366":1,"5841,5840":1,"11682,11681":1,"171355,171354":1,"2677,2676":3,"1336,1335":6,"666,665":15,"5355,5354":2,"1338,1337":5,"2676,2675":3,"10710,10709":1,"5353,5352":1,"2674,2673":2,"1335,1334":4,"21420,21419":1,"10708,10707":1,"5352,5351":1,"157074,157073":1,"2455,2454":1,"1225,1224":6,"610,609":17,"303,302":31,"4909,4908":1,"2452,2451":2,"1224,1223":6,"9817,9816":1,"2454,2453":3,"4906,4905":2,"2451,2450":2,"19635,19634":1,"4908,4907":1,"9816,9815":1,"143983,143982":1,"2250,2249":3,"1123,1122":6,"559,558":18,"277,276":33,"136,135":42,"4500,4499":1,"2248,2247":2,"1122,1121":7,"9000,8999":1,"4498,4497":2,"2247,2246":3,"17998,17997":1,"8997,8996":1,"4497,4496":1,"131983,131982":1,"2062,2061":3,"1029,1028":6,"4125,4124":1,"2061,2060":2,"8250,8249":1,"4123,4122":2,"2059,2058":3,"1027,1026":6,"511,510":13,"253,252":20,"124,123":27,"16498,16497":1,"8247,8246":1,"4122,4121":1,"120983,120982":1,"1891,1890":1,"943,942":7,"469,468":18,"232,231":30,"114,113":38,"3781,3780":1,"1888,1887":2,"942,941":7,"7561,7560":1,"1890,1889":3,"3778,3777":2,"1887,1886":2,"15123,15122":1,"3780,3779":1,"7560,7559":1,"110900,110899":1,"3466,3465":1,"1731,1730":2,"864,863":8,"6931,6930":1,"1732,1731":3,"3463,3462":2,"1729,1728":2,"862,861":4,"429,428":12,"13863,13862":1,"3465,3464":1,"6930,6929":1,"101657,101656":1,"1588,1587":3,"792,791":9,"3177,3176":2,"1587,1586":3,"6354,6353":1,"3175,3174":1,"1585,1584":2,"790,789":5,"393,392":11,"12708,12707":1,"6352,6351":1,"3174,3173":1,"93184,93183":1,"2913,2912":1,"1455,1454":3,"5824,5823":1,"2910,2909":2,"1453,1452":3,"724,723":6,"360,359":13,"11649,11648":1,"2911,2910":1,"5823,5822":1,"85417,85416":1,"2670,2669":1,"1333,1332":3,"664,663":8,"330,329":16,"5338,5337":1,"2667,2666":2,"1332,1331":3,"10677,10676":1,"2668,2667":1,"5337,5336":1,"78298,78297":1,"2448,2447":1,"1222,1221":3,"609,608":9,"4894,4893":1,"2445,2444":1,"1221,1220":3,"9787,9786":1,"2446,2445":1,"4891,4890":1,"2443,2442":1,"1219,1218":2,"607,606":4,"301,300":8,"148,147":13,"71772,71771":1,"2244,2243":1,"1120,1119":3,"558,557":9,"4486,4485":1,"2241,2240":1,"1119,1118":3,"8971,8970":1,"2242,2241":1,"4483,4482":1,"2239,2238":1,"1117,1116":2,"556,555":4,"276,275":8,"65790,65789":1,"2056,2055":1,"1026,1025":4,"4113,4112":1,"2055,2054":2,"8224,8223":1,"4110,4109":1,"2053,2052":1,"1024,1023":2,"510,509":5,"60306,60305":1,"1885,1884":1,"940,939":3,"468,467":9,"3769,3768":1,"1882,1881":2,"939,938":3,"7539,7538":1,"1884,1883":1,"3768,3767":1,"55279,55278":1,"1728,1727":1,"3456,3455":1,"1726,1725":2,"861,860":5,"6910,6909":1,"3453,3452":1,"1725,1724":1,"50671,50670":1,"1584,1583":1,"3168,3167":1,"1582,1581":2,"789,788":4,"6334,6333":1,"3165,3164":1,"1581,1580":1,"46447,46446":1,"1452,1451":1,"2904,2903":1,"1450,1449":2,"723,722":4,"5806,5805":1,"2901,2900":1,"1449,1448":1,"42575,42574":1,"1330,1329":2,"663,662":5,"2661,2660":1,"1329,1328":1,"5322,5321":1,"2659,2658":1,"1327,1326":1,"661,660":3,"328,327":4,"162,161":8,"39026,39025":1,"2440,2439":1,"1218,1217":1,"4879,4878":1,"2437,2436":1,"1216,1215":2,"606,605":3,"35772,35771":1,"2236,2235":1,"1116,1115":1,"4471,4470":1,"2233,2232":1,"1114,1113":2,"555,554":4,"32790,32789":1,"2050,2049":1,"1023,1022":1,"4099,4098":1,"2047,2046":1,"1021,1020":2,"508,507":3,"252,251":6,"30056,30055":1,"1879,1878":1,"937,936":1,"466,465":4,"231,230":7,"3757,3756":1,"1876,1875":1,"936,935":2,"27550,27549":1,"1722,1721":1,"859,858":1,"427,426":4,"211,210":8,"103,102":8,"3444,3443":1,"1720,1719":1,"858,857":2,"25253,25252":1,"1579,1578":1,"787,786":2,"391,390":4,"193,192":8,"3157,3156":1,"1576,1575":1,"786,785":1,"23147,23146":1,"1447,1446":1,"721,720":2,"358,357":3,"177,176":8,"2893,2892":1,"1444,1443":1,"720,719":1,"21217,21216":1,"1326,1325":1,"2652,2651":1,"1324,1323":1,"660,659":1,"19448,19447":1,"2431,2430":1,"1213,1212":1,"604,603":2,"300,299":4,"17826,17825":1,"2229,2228":1,"1113,1112":1,"16339,16338":1,"2043,2042":1,"1020,1019":1,"14976,14975":1,"1872,1871":1,"934,933":1,"465,464":2,"13727,13726":1,"1716,1715":1,"856,855":1,"426,425":3,"12582,12581":1,"1573,1572":1,"784,783":1,"390,389":3,"11532,11531":1,"1441,1440":1,"718,717":2,"357,356":3,"10570,10569":1,"1321,1320":1,"658,657":2,"327,326":3,"9688,9687":1,"1212,1211":1,"8879,8878":1,"1110,1109":1,"553,552":2,"274,273":3,"135,134":3,"8138,8137":1,"1018,1017":1,"507,506":2,"7458,7457":1,"933,932":1,"6835,6834":1,"855,854":1,"6264,6263":1,"783,782":1,"5741,5740":1,"5261,5260":1,"4821,4820":1,"603,602":1,"4418,4417":1,"4048,4047":1,"3709,3708":1,"463,462":1,"229,228":1,"112,111":1,"3399,3398":1,"3114,3113":1,"2853,2852":1,"2614,2613":1,"2395,2394":1,"2194,2193":1,"2010,2009":1,"1841,1840":1,"1686,1685":1,"1544,1543":1,"1414,1413":1,"1295,1294":1,"1186,1185":1,"1086,1085":1,"994,993":1,"910,909":1,"833,832":1,"762,761":1,"697,696":1,"638,637":1,"583,582":1,"533,532":1,"487,486":1,"445,444":1,"407,406":1,"372,371":1,"340,339":1,"310,309":1,"23,22":8,"22,21":8,"21,20":8,"20,19":8,"19,18":8,"18,17":9,"17,16":8,"16,15":9,"161,160":1,"15,14":8,"146,145":1,"14,13":8,"132,131":1,"13,12":7,"12,11":9,"11,10":8,"10,9":9,"9,8":7,"8,7":6,"7,6":5,"6,5":3,"5,4":1,"4,3":1,"3,2":1,"2,1":2},"product_zero":{"2,0":28668},"addsub":{"1":28668,"2":57336,"3":57336,"4":57336,"5":57336,"6":57334,"7":57330,"8":57327,"9":57325,"10":57322,"11":57319,"12":57317,"13":57316,"14":57315,"15":57313,"16":57311,"17":57310,"18":57309,"19":57307,"20":57306,"21":57305,"22":57304,"23":57303,"24":56829,"25":55004,"26":53368,"27":50604,"28":46596,"29":43694,"30":39718,"31":36933,"32":34509,"33":30478,"34":28399,"35":25828,"36":22022,"37":20251,"38":18131,"39":14487,"40":12473,"41":11044,"42":8421,"81":849,"82":204,"80":811,"160":438,"161":204,"319":170,"320":77,"159":291,"637":64,"638":34,"318":138,"1273":32,"1274":13,"636":50,"1272":19,"2545":13,"2546":2,"79":174,"2544":14,"5088":7,"5089":2,"5087":6,"10174":4,"10175":2,"2543":3,"10173":2,"20347":2,"20348":1,"5086":1,"20346":1,"40692":1,"40693":1,"74":974,"75":445,"147":410,"148":143,"73":578,"146":349,"293":143,"294":35,"292":172,"584":66,"585":35,"1167":32,"1168":13,"583":52,"1166":19,"2333":13,"2334":3,"291":90,"2332":13,"4664":8,"4665":3,"4663":5,"9326":4,"9327":3,"2331":3,"18651":2,"18652":1,"9325":1,"18650":1,"37301":1,"37302":1,"68":971,"69":408,"135":397,"136":110,"67":616,"134":383,"269":110,"270":10,"268":187,"536":53,"537":10,"267":122,"535":68,"1070":32,"1071":10,"1069":22,"2138":16,"2139":10,"534":44,"4275":8,"4276":5,"2137":6,"8549":4,"8550":2,"4274":3,"8548":2,"17097":2,"17098":1,"17096":1,"34192":1,"34193":1,"63":709,"64":80,"62":937,"124":373,"125":80,"123":412,"246":186,"247":80,"61":315,"491":70,"492":31,"245":150,"490":60,"981":31,"982":10,"980":22,"1960":16,"1961":10,"122":135,"3919":8,"3920":4,"1959":6,"3918":4,"7837":4,"7838":2,"7836":2,"15672":2,"15673":2,"979":7,"31343":1,"31344":1,"58":649,"59":39,"57":976,"114":316,"115":39,"56":375,"113":449,"226":161,"227":39,"225":182,"450":77,"451":39,"112":192,"899":32,"900":18,"449":60,"1797":16,"1798":7,"898":16,"1796":9,"3593":7,"3594":2,"224":83,"3592":6,"7184":4,"7185":2,"7183":2,"14366":2,"14367":2,"3591":1,"28731":1,"28732":1,"51":2374,"52":1902,"53":1089,"49":2388,"50":2560,"54":210,"104":468,"105":210,"48":2212,"207":189,"208":70,"103":297,"206":166,"413":70,"414":21,"412":72,"824":32,"825":21,"1647":16,"1648":11,"823":17,"3293":8,"3294":5,"1646":5,"6585":4,"6586":3,"3292":3,"13169":2,"13170":1,"6584":1,"13168":1,"26337":1,"26338":1,"43":6575,"44":5891,"45":4915,"46":3497,"47":2423,"96":355,"97":54,"95":447,"190":184,"191":54,"189":182,"379":54,"380":9,"94":157,"378":79,"756":30,"757":9,"755":25,"1510":16,"1511":9,"377":53,"3019":8,"3020":4,"1509":7,"3018":4,"6037":4,"6038":1,"754":15,"6036":3,"12072":2,"12073":1,"12071":1,"24142":1,"24143":1,"88":409,"89":92,"87":413,"174":210,"175":92,"347":80,"348":33,"173":153,"693":32,"694":12,"346":71,"692":26,"1385":12,"1386":1,"86":103,"1384":15,"2768":6,"2769":1,"1383":4,"2767":7,"5534":4,"5535":1,"2766":2,"5533":3,"11066":2,"11067":1,"11065":1,"22130":1,"22131":1,"635":33,"317":67,"1269":16,"1270":9,"634":23,"2537":8,"2538":4,"1268":7,"2536":4,"5073":4,"5074":1,"158":71,"5072":3,"10144":2,"10145":1,"10143":1,"20286":1,"20287":1,"145":98,"582":34,"1164":13,"1165":2,"581":24,"1163":14,"2326":7,"2327":2,"2325":6,"4650":4,"4651":2,"1162":3,"4649":2,"9299":2,"9300":1,"2324":1,"9298":1,"18596":1,"18597":1,"133":111,"533":30,"1067":14,"1068":4,"1066":12,"2132":8,"2133":4,"266":49,"2131":4,"4263":4,"4264":1,"1065":3,"4262":3,"8524":2,"8525":1,"8523":1,"17046":1,"17047":1,"489":35,"978":16,"244":60,"977":10,"1955":6,"1956":1,"488":23,"1954":7,"3908":3,"3909":1,"1953":2,"3907":3,"7814":2,"7815":1,"3906":1,"7813":1,"15626":1,"15627":1,"448":33,"897":13,"896":14,"1792":7,"1793":2,"1791":6,"3582":4,"3583":2,"895":6,"3581":2,"7163":2,"7164":1,"1790":1,"7162":1,"14324":1,"14325":1,"411":38,"822":16,"205":60,"821":11,"1643":6,"1644":1,"410":24,"1642":7,"3284":4,"3285":1,"1641":2,"3283":3,"6566":2,"6567":1,"6565":1,"13130":1,"13131":1,"188":65,"376":29,"753":14,"1506":8,"1507":2,"1505":6,"3010":4,"3011":2,"752":8,"3009":2,"6019":2,"6020":1,"6018":1,"12036":1,"12037":1,"345":36,"691":16,"690":13,"1380":8,"1381":6,"172":43,"2759":4,"2760":3,"1379":2,"5517":2,"5518":2,"2758":1,"11033":1,"11034":1,"316":32,"633":16,"1266":6,"1267":1,"632":11,"1265":7,"2530":3,"2531":1,"1264":2,"2529":3,"5058":2,"5059":1,"2528":1,"5057":1,"10114":1,"10115":1,"290":38,"580":16,"1160":8,"1161":4,"72":49,"1159":4,"2319":4,"2320":1,"2318":3,"4636":2,"4637":1,"579":9,"4635":1,"9271":1,"9272":1,"66":52,"532":18,"1064":6,"531":12,"1063":7,"2126":4,"2127":1,"1062":2,"2125":3,"4250":2,"4251":1,"4249":1,"8498":1,"8499":1,"975":8,"976":4,"487":15,"974":4,"1949":4,"1950":1,"243":22,"1948":3,"3896":2,"3897":1,"3895":1,"7790":1,"7791":1,"223":31,"447":18,"894":8,"893":5,"1786":4,"1787":3,"446":12,"3571":2,"3572":2,"1785":1,"7141":1,"7142":1,"102":43,"820":6,"409":14,"819":7,"1638":4,"1639":1,"818":4,"1637":3,"3274":2,"3275":1,"3273":1,"6546":1,"6547":1,"751":8,"375":15,"1501":4,"1502":3,"750":5,"3001":2,"3002":1,"1500":1,"3000":1,"6001":1,"6002":1,"344":18,"689":8,"688":6,"1376":4,"1377":3,"2751":2,"2752":1,"1375":1,"2750":1,"5501":1,"5502":1,"315":14,"631":8,"1262":4,"1263":1,"630":6,"1261":3,"2522":2,"2523":1,"2521":1,"5042":1,"5043":1,"289":18,"578":7,"1157":4,"1158":1,"144":19,"1156":3,"2312":2,"2313":1,"2311":1,"4622":1,"4623":1,"265":20,"530":8,"1060":4,"1061":3,"132":18,"2119":2,"2120":2,"1059":1,"4237":1,"4238":1,"486":9,"972":4,"973":2,"121":19,"971":2,"1943":2,"1944":1,"1942":1,"3884":1,"3885":1,"111":23,"891":4,"892":2,"445":7,"890":2,"1781":2,"1782":1,"1780":1,"3560":1,"3561":1,"204":18,"817":4,"408":8,"816":3,"1633":2,"1634":1,"1632":1,"3264":1,"3265":1,"187":19,"749":4,"374":8,"748":3,"1497":2,"1498":1,"93":11,"1496":1,"2992":1,"2993":1,"343":9,"687":4,"686":4,"1372":2,"1373":1,"171":10,"1371":1,"2743":1,"2744":1,"157":17,"314":7,"629":4,"1258":2,"1259":1,"1257":1,"2514":1,"2515":1,"577":4,"288":9,"1153":2,"1154":1,"576":3,"1152":1,"2305":1,"2306":1,"529":5,"264":8,"1057":2,"1058":1,"528":3,"1056":1,"2113":1,"2114":1,"485":5,"242":9,"969":2,"970":1,"484":3,"968":1,"1937":1,"1938":1,"222":11,"444":4,"888":2,"889":2,"55":9,"1775":1,"1776":1,"407":4,"815":2,"203":6,"814":1,"1628":1,"1629":1,"373":4,"747":2,"186":6,"746":1,"1492":1,"1493":1,"342":5,"685":2,"85":7,"684":1,"1368":1,"1369":1,"78":8,"628":2,"313":4,"627":1,"1254":1,"1255":1,"575":2,"287":4,"1149":1,"1150":1,"263":3,"527":2,"1054":1,"1055":1,"60":7,"241":3,"483":2,"966":1,"967":1,"443":3,"221":3,"885":1,"886":1,"101":4,"406":2,"812":1,"813":1,"372":2,"744":1,"745":1,"341":2,"682":1,"683":1,"156":3,"625":1,"626":1,"143":3,"573":1,"574":1,"131":3,"526":1,"120":3,"482":1,"110":3,"442":1,"405":1,"371":1,"170":2,"312":1,"286":1,"262":1,"202":1,"253":1,"254":1,"230":1,"231":1,"141":1,"142":1,"128":1,"129":1,"116":1,"117":1,"106":1,"107":1,"76":1,"77":1,"70":1},"product_classical":{"2,1":57336,"2,2":57336,"2,3":57336,"2,4":57336,"2,5":57334,"2,6":57330,"2,7":57327,"2,8":57325,"2,9":57322,"2,10":57319,"2,11":57317,"2,12":57316,"2,13":57315,"2,14":57313,"2,15":57311,"2,16":57310,"2,17":57309,"2,18":57307,"2,19":57306,"2,20":57305,"2,21":57304,"2,22":57303,"2,23":56829,"2,24":55004,"2,25":53368,"2,26":50604,"2,27":46596,"2,28":43694,"2,29":39718,"2,30":36933,"2,31":34509,"2,32":30478,"2,33":28399,"2,34":25828,"2,35":22022,"2,36":20251,"2,37":18131,"2,38":14487,"2,39":12473,"2,40":11044,"2,41":8421,"2,80":849,"2,81":204,"2,79":811,"2,159":438,"2,160":204,"2,318":170,"2,319":77,"2,158":291,"2,636":64,"2,637":34,"2,317":138,"2,1272":32,"2,1273":13,"2,635":50,"2,1271":19,"2,2544":13,"2,2545":2,"2,78":174,"2,2543":14,"2,5087":7,"2,5088":2,"2,5086":6,"2,10173":4,"2,10174":2,"2,2542":3,"2,10172":2,"2,20346":2,"2,20347":1,"2,5085":1,"2,20345":1,"2,40691":1,"2,40692":1,"2,73":974,"2,74":445,"2,146":410,"2,147":143,"2,72":578,"2,145":349,"2,292":143,"2,293":35,"2,291":172,"2,583":66,"2,584":35,"2,1166":32,"2,1167":13,"2,582":52,"2,1165":19,"2,2332":13,"2,2333":3,"2,290":90,"2,2331":13,"2,4663":8,"2,4664":3,"2,4662":5,"2,9325":4,"2,9326":3,"2,2330":3,"2,18650":2,"2,18651":1,"2,9324":1,"2,18649":1,"2,37300":1,"2,37301":1,"2,67":971,"2,68":407,"2,134":397,"2,135":110,"2,66":616,"2,133":383,"2,268":110,"2,269":10,"2,267":187,"2,535":53,"2,536":10,"2,266":122,"2,534":68,"2,1069":32,"2,1070":10,"2,1068":22,"2,2137":16,"2,2138":10,"2,533":44,"2,4274":8,"2,4275":5,"2,2136":6,"2,8548":4,"2,8549":2,"2,4273":3,"2,8547":2,"2,17096":2,"2,17097":1,"2,17095":1,"2,34191":1,"2,34192":1,"2,62":709,"2,63":80,"2,61":936,"2,123":373,"2,124":80,"2,122":412,"2,245":186,"2,246":80,"2,60":314,"2,490":70,"2,491":31,"2,244":150,"2,489":60,"2,980":31,"2,981":10,"2,979":22,"2,1959":16,"2,1960":10,"2,121":135,"2,3918":8,"2,3919":4,"2,1958":6,"2,3917":4,"2,7836":4,"2,7837":2,"2,7835":2,"2,15671":2,"2,15672":2,"2,978":7,"2,31342":1,"2,31343":1,"2,57":649,"2,58":39,"2,56":976,"2,113":316,"2,114":39,"2,55":374,"2,112":449,"2,225":161,"2,226":39,"2,224":182,"2,449":77,"2,450":39,"2,111":192,"2,898":32,"2,899":18,"2,448":60,"2,1796":16,"2,1797":7,"2,897":16,"2,1795":9,"2,3592":7,"2,3593":2,"2,223":83,"2,3591":6,"2,7183":4,"2,7184":2,"2,7182":2,"2,14365":2,"2,14366":2,"2,3590":1,"2,28730":1,"2,28731":1,"24,26":2716,"25,27":1771,"24,27":2703,"25,28":879,"25,26":892,"26,27":210,"26,28":210,"23,25":1155,"2,52":879,"2,53":210,"23,27":1142,"24,28":669,"2,51":813,"2,103":468,"2,104":210,"22,25":473,"22,26":473,"2,206":189,"2,207":70,"2,102":297,"2,205":166,"2,412":70,"2,413":21,"2,411":72,"2,823":32,"2,824":21,"2,50":144,"2,1646":16,"2,1647":11,"2,822":17,"2,3292":8,"2,3293":5,"2,1645":5,"2,6584":4,"2,6585":3,"2,3291":3,"2,13168":2,"2,13169":1,"2,6583":1,"2,13167":1,"2,26336":1,"2,26337":1,"2,42":6575,"2,43":5891,"2,44":4915,"2,45":3497,"2,46":2423,"2,47":1739,"2,48":760,"2,49":54,"2,95":354,"2,96":54,"2,94":446,"2,189":184,"2,190":54,"2,188":182,"2,378":54,"2,379":9,"2,93":157,"2,377":79,"2,755":30,"2,756":9,"2,754":25,"2,1509":16,"2,1510":9,"2,376":53,"2,3018":8,"2,3019":4,"2,1508":7,"2,3017":4,"2,6036":4,"2,6037":1,"2,753":15,"2,6035":3,"2,12071":2,"2,12072":1,"2,12070":1,"2,24141":1,"2,24142":1,"2,87":409,"2,88":92,"2,86":413,"2,173":210,"2,174":92,"2,346":80,"2,347":33,"2,172":153,"2,692":32,"2,693":12,"2,345":71,"2,691":26,"2,1384":12,"2,1385":1,"2,85":102,"2,1383":15,"2,2767":6,"2,2768":1,"2,1382":4,"2,2766":7,"2,5533":4,"2,5534":1,"2,2765":2,"2,5532":3,"2,11065":2,"2,11066":1,"2,11064":1,"2,22129":1,"2,22130":1,"2,634":33,"2,316":67,"2,1268":16,"2,1269":9,"2,633":23,"2,2536":8,"2,2537":4,"2,1267":7,"2,2535":4,"2,5072":4,"2,5073":1,"2,157":70,"2,5071":3,"2,10143":2,"2,10144":1,"2,10142":1,"2,20285":1,"2,20286":1,"2,144":98,"2,581":34,"2,1163":13,"2,1164":2,"2,580":24,"2,1162":14,"2,2325":7,"2,2326":2,"2,2324":6,"2,4649":4,"2,4650":2,"2,1161":3,"2,4648":2,"2,9298":2,"2,9299":1,"2,2323":1,"2,9297":1,"2,18595":1,"2,18596":1,"2,132":111,"2,532":30,"2,1066":14,"2,1067":4,"2,1065":12,"2,2131":8,"2,2132":4,"2,265":49,"2,2130":4,"2,4262":4,"2,4263":1,"2,1064":3,"2,4261":3,"2,8523":2,"2,8524":1,"2,8522":1,"2,17045":1,"2,17046":1,"2,488":35,"2,977":16,"2,243":60,"2,976":10,"2,1954":6,"2,1955":1,"2,487":23,"2,1953":7,"2,3907":3,"2,3908":1,"2,1952":2,"2,3906":3,"2,7813":2,"2,7814":1,"2,3905":1,"2,7812":1,"2,15625":1,"2,15626":1,"2,447":33,"2,896":13,"2,895":14,"2,1791":7,"2,1792":2,"2,1790":6,"2,3581":4,"2,3582":2,"2,894":6,"2,3580":2,"2,7162":2,"2,7163":1,"2,1789":1,"2,7161":1,"2,14323":1,"2,14324":1,"2,410":38,"2,821":16,"2,204":60,"2,820":11,"2,1642":6,"2,1643":1,"2,409":24,"2,1641":7,"2,3283":4,"2,3284":1,"2,1640":2,"2,3282":3,"2,6565":2,"2,6566":1,"2,6564":1,"2,13129":1,"2,13130":1,"2,187":65,"2,375":29,"2,752":14,"2,1505":8,"2,1506":2,"2,1504":6,"2,3009":4,"2,3010":2,"2,751":8,"2,3008":2,"2,6018":2,"2,6019":1,"2,6017":1,"2,12035":1,"2,12036":1,"2,344":36,"2,690":16,"2,689":13,"2,1379":8,"2,1380":6,"2,171":43,"2,2758":4,"2,2759":3,"2,1378":2,"2,5516":2,"2,5517":2,"2,2757":1,"2,11032":1,"2,11033":1,"2,315":32,"2,632":16,"2,1265":6,"2,1266":1,"2,631":11,"2,1264":7,"2,2529":3,"2,2530":1,"2,1263":2,"2,2528":3,"2,5057":2,"2,5058":1,"2,2527":1,"2,5056":1,"2,10113":1,"2,10114":1,"2,289":38,"2,579":16,"2,1159":8,"2,1160":4,"2,71":49,"2,1158":4,"2,2318":4,"2,2319":1,"2,2317":3,"2,4635":2,"2,4636":1,"2,578":9,"2,4634":1,"2,9270":1,"2,9271":1,"2,65":52,"2,531":18,"2,1063":6,"2,530":12,"2,1062":7,"2,2125":4,"2,2126":1,"2,1061":2,"2,2124":3,"2,4249":2,"2,4250":1,"2,4248":1,"2,8497":1,"2,8498":1,"2,974":8,"2,975":4,"2,486":15,"2,973":4,"2,1948":4,"2,1949":1,"2,242":22,"2,1947":3,"2,3895":2,"2,3896":1,"2,3894":1,"2,7789":1,"2,7790":1,"2,222":31,"2,446":18,"2,893":8,"2,892":5,"2,1785":4,"2,1786":3,"2,445":12,"2,3570":2,"2,3571":2,"2,1784":1,"2,7140":1,"2,7141":1,"2,101":43,"2,819":6,"2,408":14,"2,818":7,"2,1637":4,"2,1638":1,"2,817":4,"2,1636":3,"2,3273":2,"2,3274":1,"2,3272":1,"2,6545":1,"2,6546":1,"2,750":8,"2,374":15,"2,1500":4,"2,1501":3,"2,749":5,"2,3000":2,"2,3001":1,"2,1499":1,"2,2999":1,"2,6000":1,"2,6001":1,"2,343":18,"2,688":8,"2,687":6,"2,1375":4,"2,1376":3,"2,2750":2,"2,2751":1,"2,1374":1,"2,2749":1,"2,5500":1,"2,5501":1,"2,314":14,"2,630":8,"2,1261":4,"2,1262":1,"2,629":6,"2,1260":3,"2,2521":2,"2,2522":1,"2,2520":1,"2,5041":1,"2,5042":1,"2,288":18,"2,577":7,"2,1156":4,"2,1157":1,"2,143":19,"2,1155":3,"2,2311":2,"2,2312":1,"2,2310":1,"2,4621":1,"2,4622":1,"2,264":20,"2,529":8,"2,1059":4,"2,1060":3,"2,131":18,"2,2118":2,"2,2119":2,"2,1058":1,"2,4236":1,"2,4237":1,"2,485":9,"2,971":4,"2,972":2,"2,120":19,"2,970":2,"2,1942":2,"2,1943":1,"2,1941":1,"2,3883":1,"2,3884":1,"2,110":23,"2,890":4,"2,891":2,"2,444":7,"2,889":2,"2,1780":2,"2,1781":1,"2,1779":1,"2,3559":1,"2,3560":1,"2,203":18,"2,816":4,"2,407":8,"2,815":3,"2,1632":2,"2,1633":1,"2,1631":1,"2,3263":1,"2,3264":1,"2,186":19,"2,748":4,"2,373":8,"2,747":3,"2,1496":2,"2,1497":1,"2,92":11,"2,1495":1,"2,2991":1,"2,2992":1,"2,342":9,"2,686":4,"2,685":4,"2,1371":2,"2,1372":1,"2,170":10,"2,1370":1,"2,2742":1,"2,2743":1,"2,156":16,"2,313":7,"2,628":4,"2,1257":2,"2,1258":1,"2,1256":1,"2,2513":1,"2,2514":1,"2,576":4,"2,287":9,"2,1152":2,"2,1153":1,"2,575":3,"2,1151":1,"2,2304":1,"2,2305":1,"2,528":5,"2,263":8,"2,1056":2,"2,1057":1,"2,527":3,"2,1055":1,"2,2112":1,"2,2113":1,"2,484":5,"2,241":9,"2,968":2,"2,969":1,"2,483":3,"2,967":1,"2,1936":1,"2,1937":1,"2,221":11,"2,443":4,"2,887":2,"2,888":2,"2,54":8,"2,1774":1,"2,1775":1,"2,406":4,"2,814":2,"2,202":6,"2,813":1,"2,1627":1,"2,1628":1,"2,372":4,"2,746":2,"2,185":6,"2,745":1,"2,1491":1,"2,1492":1,"2,341":5,"2,684":2,"2,84":6,"2,683":1,"2,1367":1,"2,1368":1,"2,77":8,"2,627":2,"2,312":4,"2,626":1,"2,1253":1,"2,1254":1,"2,574":2,"2,286":4,"2,1148":1,"2,1149":1,"2,262":3,"2,526":2,"2,1053":1,"2,1054":1,"2,59":7,"2,240":3,"2,482":2,"2,965":1,"2,966":1,"2,442":3,"2,220":3,"2,884":1,"2,885":1,"2,100":4,"2,405":2,"2,811":1,"2,812":1,"2,371":2,"2,743":1,"2,744":1,"2,340":2,"2,681":1,"2,682":1,"2,155":3,"2,624":1,"2,625":1,"2,142":3,"2,572":1,"2,573":1,"2,130":3,"2,525":1,"2,119":3,"2,481":1,"2,109":3,"2,441":1,"2,404":1,"2,370":1,"2,169":2,"2,311":1,"2,285":1,"2,261":1,"2,201":1,"19,235":1,"20,234":1,"20,235":1,"21,234":1,"17,214":1,"18,213":1,"18,214":1,"19,213":1,"12,146":1,"13,145":1,"13,146":1,"14,145":1,"10,132":1,"11,131":1,"11,132":1,"12,131":1,"9,120":1,"10,119":1,"10,120":1,"11,119":1,"8,109":1,"9,108":1,"9,109":1,"10,108":1,"8,99":1,"9,98":1,"9,99":1,"10,98":1,"7,89":1,"8,88":1,"8,89":1,"9,88":1,"6,80":1,"7,79":1,"7,80":1,"8,79":1,"5,72":1,"6,71":1,"6,72":1,"7,71":1,"5,65":1,"6,64":1,"6,65":1,"7,64":1,"4,58":1,"5,57":1,"5,58":1,"6,57":1,"4,52":1,"5,51":1,"5,52":1,"6,51":1},"matvec_wrap":{"161,160,39,40,40,41,192":204,"319,318,79,80,80,81,384":204,"157,156,38,39,39,40,192":681,"637,636,158,159,159,160,768":77,"159,158,39,40,40,41,192":645,"317,316,78,79,79,80,384":311,"1273,1272,317,318,318,319,1536":34,"635,634,158,159,159,160,768":127,"315,314,78,79,79,80,384":334,"155,154,38,39,39,40,192":478,"2545,2544,635,636,636,637,3072":13,"1271,1270,317,318,318,319,1536":43,"633,632,157,158,158,159,768":150,"5089,5088,1271,1272,1272,1273,6144":2,"2543,2542,635,636,636,637,3072":21,"1269,1268,316,317,317,318,1536":62,"10175,10174,2543,2544,2544,2545,12288":2,"5085,5084,1270,1271,1271,1272,6144":10,"2541,2540,634,635,635,636,3072":21,"20347,20346,5086,5087,5087,5088,24576":2,"5087,5086,1271,1272,1272,1273,6144":11,"10171,10170,2542,2543,2543,2544,12288":6,"5083,5082,1270,1271,1271,1272,6144":9,"2539,2538,634,635,635,636,3072":9,"1267,1266,316,317,317,318,1536":31,"631,630,157,158,158,159,768":84,"313,312,77,78,78,79,384":136,"40693,40692,10172,10173,10173,10174,49152":1,"10173,10172,2542,2543,2543,2544,12288":5,"20345,20344,5085,5086,5086,5087,24576":3,"81383,81382,20345,20346,20346,20347,98304":1,"40689,40688,10171,10172,10172,10173,49152":1,"20343,20342,5085,5086,5086,5087,24576":2,"10169,10168,2541,2542,2542,2543,12288":3,"162763,162762,40690,40691,40691,40692,196608":1,"40691,40690,10172,10173,10173,10174,49152":1,"81379,81378,20344,20345,20345,20346,98304":1,"40687,40686,10171,10172,10172,10173,49152":1,"20341,20340,5084,5085,5085,5086,24576":1,"976563,976562,81380,81381,81381,81382,1572864":1,"147,146,36,37,37,38,192":445,"293,292,72,73,73,74,384":143,"145,144,35,36,36,37,192":672,"585,584,145,146,146,147,768":35,"291,290,72,73,73,74,384":302,"143,142,35,36,36,37,192":684,"1167,1166,291,292,292,293,1536":35,"581,580,144,145,145,146,768":143,"289,288,71,72,72,73,384":333,"2333,2332,582,583,583,584,3072":13,"583,582,145,146,146,147,768":108,"1165,1164,290,291,291,292,1536":44,"4665,4664,1165,1166,1166,1167,6144":3,"2331,2330,582,583,583,584,3072":22,"1163,1162,290,291,291,292,1536":64,"579,578,144,145,145,146,768":124,"287,286,71,72,72,73,384":196,"141,140,34,35,35,36,192":238,"9327,9326,2331,2332,2332,2333,12288":3,"4661,4660,1164,1165,1165,1166,6144":11,"2329,2328,581,582,582,583,3072":21,"18651,18650,4662,4663,4663,4664,24576":3,"4663,4662,1165,1166,1166,1167,6144":10,"9323,9322,2330,2331,2331,2332,12288":5,"4659,4658,1164,1165,1165,1166,6144":8,"2327,2326,581,582,582,583,3072":10,"1161,1160,289,290,290,291,1536":34,"37301,37300,9324,9325,9325,9326,49152":1,"9325,9324,2330,2331,2331,2332,12288":5,"18649,18648,4661,4662,4662,4663,24576":2,"74601,74600,18649,18650,18650,18651,98304":1,"37299,37298,9324,9325,9325,9326,49152":2,"18647,18646,4661,4662,4662,4663,24576":3,"9321,9320,2329,2330,2330,2331,12288":3,"149199,149198,37299,37300,37300,37301,196608":1,"74597,74596,18648,18649,18649,18650,98304":1,"37297,37296,9323,9324,9324,9325,49152":1,"895181,895180,74598,74599,74599,74600,1572864":1,"135,134,33,34,34,35,192":407,"269,268,66,67,67,68,384":110,"133,132,32,33,33,34,192":674,"537,536,133,134,134,135,768":10,"267,266,66,67,67,68,384":297,"131,130,32,33,33,34,192":685,"1071,1070,267,268,268,269,1536":10,"533,532,132,133,133,134,768":140,"265,264,65,66,66,67,384":336,"2139,2138,534,535,535,536,3072":10,"535,534,133,134,134,135,768":100,"1067,1066,266,267,267,268,1536":57,"531,530,132,133,133,134,768":147,"263,262,65,66,66,67,384":228,"129,128,31,32,32,33,192":273,"4275,4274,1068,1069,1069,1070,6144":10,"1069,1068,266,267,267,268,1536":43,"2135,2134,533,534,534,535,3072":21,"1065,1064,265,266,266,267,1536":55,"8549,8548,2136,2137,2137,2138,12288":5,"2137,2136,533,534,534,535,3072":22,"4273,4272,1067,1068,1068,1069,6144":11,"17097,17096,4273,4274,4274,4275,24576":2,"8547,8546,2136,2137,2137,2138,12288":5,"4271,4270,1067,1068,1068,1069,6144":11,"2133,2132,532,533,533,534,3072":15,"34193,34192,8547,8548,8548,8549,49152":1,"17095,17094,4273,4274,4274,4275,24576":3,"8545,8544,2135,2136,2136,2137,12288":6,"68383,68382,17095,17096,17096,17097,98304":1,"34189,34188,8546,8547,8547,8548,49152":2,"17093,17092,4272,4273,4273,4274,24576":3,"136765,136764,34190,34191,34191,34192,196608":1,"34191,34190,8547,8548,8548,8549,49152":1,"68381,68380,17094,17095,17095,17096,98304":1,"820581,820580,68381,68382,68382,68383,786432":1,"125,124,30,31,31,32,96":80,"247,246,61,62,62,63,192":80,"121,120,29,30,30,31,96":680,"491,490,122,123,123,124,384":80,"123,122,30,31,31,32,96":629,"243,242,60,61,61,62,192":336,"119,118,29,30,30,31,96":602,"981,980,244,245,245,246,768":31,"245,244,60,61,61,62,192":293,"489,488,121,122,122,123,384":137,"1961,1960,489,490,490,491,1536":10,"979,978,244,245,245,246,768":49,"487,486,121,122,122,123,384":156,"241,240,59,60,60,61,192":259,"3919,3918,979,980,980,981,3072":10,"1957,1956,488,489,489,490,1536":21,"977,976,243,244,244,245,768":63,"7837,7836,1958,1959,1959,1960,6144":4,"1959,1958,489,490,490,491,1536":21,"3917,3916,978,979,979,980,3072":10,"15673,15672,3917,3918,3918,3919,12288":2,"7835,7834,1958,1959,1959,1960,6144":6,"3915,3914,978,979,979,980,3072":11,"1955,1954,488,489,489,490,1536":18,"975,974,243,244,244,245,768":43,"485,484,120,121,121,122,384":87,"31343,31342,7835,7836,7836,7837,24576":2,"15669,15668,3916,3917,3917,3918,12288":3,"7833,7832,1957,1958,1958,1959,6144":5,"62685,62684,15670,15671,15671,15672,49152":1,"15671,15670,3917,3918,3918,3919,12288":2,"31341,31340,7834,7835,7835,7836,24576":1,"125369,125368,31341,31342,31342,31343,98304":1,"62683,62682,15670,15671,15671,15672,49152":1,"31339,31338,7834,7835,7835,7836,24576":1,"15667,15666,3916,3917,3917,3918,12288":1,"7831,7830,1957,1958,1958,1959,6144":1,"3913,3912,977,978,978,979,3072":1,"752198,752197,62683,62684,62684,62685,786432":1,"115,114,28,29,29,30,96":39,"227,226,56,57,57,58,192":39,"111,110,27,28,28,29,96":682,"451,450,112,113,113,114,384":39,"113,112,27,28,28,29,96":610,"223,222,55,56,56,57,192":333,"109,108,26,27,27,28,96":642,"899,898,224,225,225,226,768":39,"225,224,55,56,56,57,192":277,"447,446,111,112,112,113,384":155,"221,220,54,55,55,56,192":300,"1797,1796,448,449,449,450,1536":18,"449,448,111,112,112,113,384":122,"897,896,223,224,224,225,768":56,"3593,3592,897,898,898,899,3072":7,"1795,1794,448,449,449,450,1536":21,"895,894,223,224,224,225,768":66,"445,444,110,111,111,112,384":125,"7185,7184,1795,1796,1796,1797,6144":2,"3591,3590,897,898,898,899,3072":11,"1793,1792,447,448,448,449,1536":23,"14367,14366,3591,3592,3592,3593,12288":2,"7181,7180,1794,1795,1795,1796,6144":5,"3589,3588,896,897,897,898,3072":10,"28731,28730,7182,7183,7183,7184,24576":2,"7183,7182,1795,1796,1796,1797,6144":5,"14363,14362,3590,3591,3591,3592,12288":3,"7179,7178,1794,1795,1795,1796,6144":4,"3587,3586,896,897,897,898,3072":4,"1791,1790,447,448,448,449,1536":15,"893,892,222,223,223,224,768":36,"57461,57460,14364,14365,14365,14366,49152":1,"14365,14364,3590,3591,3591,3592,12288":2,"28729,28728,7181,7182,7182,7183,24576":1,"114921,114920,28729,28730,28730,28731,98304":1,"57459,57458,14364,14365,14365,14366,49152":1,"28727,28726,7181,7182,7182,7183,24576":1,"14361,14360,3589,3590,3590,3591,12288":1,"689513,689512,57459,57460,57460,57461,786432":1,"105,104,25,26,26,27,96":210,"207,206,51,52,52,53,192":210,"101,100,24,25,25,26,96":682,"413,412,102,103,103,104,384":70,"103,102,25,26,26,27,96":669,"205,204,50,51,51,52,192":328,"825,824,205,206,206,207,768":21,"411,410,102,103,103,104,384":140,"203,202,50,51,51,52,192":341,"99,98,24,25,25,26,96":473,"1647,1646,411,412,412,413,1536":21,"821,820,204,205,205,206,768":66,"409,408,101,102,102,103,384":162,"3293,3292,822,823,823,824,3072":11,"823,822,205,206,206,207,768":49,"1645,1644,410,411,411,412,1536":22,"6585,6584,1645,1646,1646,1647,6144":5,"3291,3290,822,823,823,824,3072":10,"1643,1642,410,411,411,412,1536":27,"819,818,204,205,205,206,768":53,"407,406,101,102,102,103,384":96,"201,200,49,50,50,51,192":131,"13169,13168,3291,3292,3292,3293,12288":3,"6583,6582,1645,1646,1646,1647,6144":6,"3289,3288,821,822,822,823,3072":11,"26337,26336,6583,6584,6584,6585,24576":1,"13167,13166,3291,3292,3292,3293,12288":2,"6581,6580,1644,1645,1645,1646,6144":5,"52673,52672,13167,13168,13168,13169,49152":1,"26335,26334,6583,6584,6584,6585,24576":2,"13165,13164,3290,3291,3291,3292,12288":3,"105343,105342,26335,26336,26336,26337,98304":1,"52669,52668,13166,13167,13167,13168,49152":1,"26333,26332,6582,6583,6583,6584,24576":1,"632052,632051,52670,52671,52671,52672,786432":1,"191,190,47,48,48,49,192":54,"379,378,94,95,95,96,384":54,"187,186,46,47,47,48,192":339,"757,756,188,189,189,190,768":9,"189,188,46,47,47,48,192":300,"377,376,93,94,94,95,384":139,"1511,1510,377,378,378,379,1536":9,"753,752,187,188,188,189,768":64,"375,374,93,94,94,95,384":161,"185,184,45,46,46,47,192":285,"3019,3018,754,755,755,756,3072":9,"755,754,188,189,189,190,768":45,"1507,1506,376,377,377,378,1536":24,"751,750,187,188,188,189,768":66,"373,372,92,93,93,94,384":113,"6037,6036,1508,1509,1509,1510,6144":4,"1509,1508,376,377,377,378,1536":21,"3017,3016,753,754,754,755,3072":11,"12073,12072,3017,3018,3018,3019,12288":1,"6035,6034,1508,1509,1509,1510,6144":5,"3015,3014,753,754,754,755,3072":10,"1505,1504,375,376,376,377,1536":23,"24143,24142,6035,6036,6036,6037,24576":1,"12069,12068,3016,3017,3017,3018,12288":2,"6033,6032,1507,1508,1508,1509,6144":5,"48283,48282,12070,12071,12071,12072,49152":1,"12071,12070,3017,3018,3018,3019,12288":3,"24139,24138,6034,6035,6035,6036,24576":2,"12067,12066,3016,3017,3017,3018,12288":2,"6031,6030,1507,1508,1508,1509,6144":2,"3013,3012,752,753,753,754,3072":2,"96565,96564,24140,24141,24141,24142,98304":1,"24141,24140,6034,6035,6035,6036,24576":1,"48281,48280,12069,12070,12070,12071,49152":1,"579380,579379,48281,48282,48282,48283,786432":1,"175,174,43,44,44,45,192":92,"347,346,86,87,87,88,384":92,"171,170,42,43,43,44,192":339,"693,692,172,173,173,174,768":33,"173,172,42,43,43,44,192":317,"345,344,85,86,86,87,384":151,"1385,1384,345,346,346,347,1536":12,"691,690,172,173,173,174,768":59,"343,342,85,86,86,87,384":166,"169,168,41,42,42,43,192":248,"2769,2768,691,692,692,693,3072":1,"1383,1382,345,346,346,347,1536":21,"689,688,171,172,172,173,768":72,"5535,5534,1383,1384,1384,1385,6144":1,"2765,2764,690,691,691,692,3072":10,"1381,1380,344,345,345,346,1536":27,"11067,11066,2766,2767,2767,2768,12288":1,"2767,2766,691,692,692,693,3072":11,"5531,5530,1382,1383,1383,1384,6144":6,"2763,2762,690,691,691,692,3072":10,"1379,1378,344,345,345,346,1536":20,"687,686,171,172,172,173,768":46,"341,340,84,85,85,86,384":76,"22131,22130,5532,5533,5533,5534,24576":1,"5533,5532,1382,1383,1383,1384,6144":5,"11063,11062,2765,2766,2766,2767,12288":2,"5529,5528,1381,1382,1382,1383,6144":4,"44259,44258,11064,11065,11065,11066,49152":1,"11065,11064,2765,2766,2766,2767,12288":3,"22127,22126,5531,5532,5532,5533,24576":2,"11061,11060,2764,2765,2765,2766,12288":2,"88517,88516,22128,22129,22129,22130,98304":1,"22129,22128,5531,5532,5532,5533,24576":1,"44257,44256,11063,11064,11064,11065,49152":1,"531097,531096,44257,44258,44258,44259,786432":1,"2537,2536,633,634,634,635,3072":9,"5073,5072,1267,1268,1268,1269,6144":4,"2535,2534,633,634,634,635,3072":11,"1265,1264,315,316,316,317,1536":31,"10145,10144,2535,2536,2536,2537,12288":1,"5071,5070,1267,1268,1268,1269,6144":5,"2533,2532,632,633,633,634,3072":10,"20287,20286,5071,5072,5072,5073,24576":1,"10141,10140,2534,2535,2535,2536,12288":2,"5069,5068,1266,1267,1267,1268,6144":5,"40571,40570,10142,10143,10143,10144,49152":1,"10143,10142,2535,2536,2536,2537,12288":3,"20283,20282,5070,5071,5071,5072,24576":2,"10139,10138,2534,2535,2535,2536,12288":2,"5067,5066,1266,1267,1267,1268,6144":2,"2531,2530,632,633,633,634,3072":3,"1263,1262,315,316,316,317,1536":14,"629,628,156,157,157,158,768":39,"81141,81140,20284,20285,20285,20286,98304":1,"20285,20284,5070,5071,5071,5072,24576":1,"40569,40568,10141,10142,10142,10143,49152":1,"486838,486837,40569,40570,40570,40571,786432":1,"4651,4650,1162,1163,1163,1164,6144":2,"2323,2322,580,581,581,582,3072":10,"1159,1158,289,290,290,291,1536":30,"577,576,143,144,144,145,768":56,"9299,9298,2324,2325,2325,2326,12288":2,"2325,2324,580,581,581,582,3072":11,"4647,4646,1161,1162,1162,1163,6144":6,"2321,2320,579,580,580,581,3072":9,"18597,18596,4648,4649,4649,4650,24576":1,"4649,4648,1161,1162,1162,1163,6144":5,"9297,9296,2323,2324,2324,2325,12288":3,"37191,37190,9297,9298,9298,9299,49152":1,"18593,18592,4647,4648,4648,4649,24576":1,"9295,9294,2323,2324,2324,2325,12288":2,"4645,4644,1160,1161,1161,1162,6144":3,"74379,74378,18594,18595,18595,18596,98304":1,"18595,18594,4648,4649,4649,4650,24576":1,"37187,37186,9296,9297,9297,9298,49152":1,"18591,18590,4647,4648,4648,4649,24576":1,"9293,9292,2322,2323,2323,2324,12288":1,"446267,446266,37188,37189,37189,37190,786432":1,"4263,4262,1065,1066,1066,1067,6144":4,"2129,2128,531,532,532,533,3072":11,"1063,1062,265,266,266,267,1536":32,"529,528,131,132,132,133,768":66,"8525,8524,2130,2131,2131,2132,12288":1,"2131,2130,532,533,533,534,3072":10,"4261,4260,1064,1065,1065,1066,6144":5,"17047,17046,4261,4262,4262,4263,24576":1,"8521,8520,2129,2130,2130,2131,12288":2,"4259,4258,1064,1065,1065,1066,6144":5,"2127,2126,531,532,532,533,3072":8,"1061,1060,264,265,265,266,1536":20,"34091,34090,8522,8523,8523,8524,49152":1,"8523,8522,2130,2131,2131,2132,12288":3,"17043,17042,4260,4261,4261,4262,24576":2,"8519,8518,2129,2130,2130,2131,12288":2,"4257,4256,1063,1064,1064,1065,6144":2,"68181,68180,17044,17045,17045,17046,98304":1,"17045,17044,4260,4261,4261,4262,24576":1,"34089,34088,8521,8522,8522,8523,49152":1,"409077,409076,34089,34090,34090,34091,393216":1,"3909,3908,976,977,977,978,3072":1,"1953,1952,487,488,488,489,1536":11,"7815,7814,1953,1954,1954,1955,6144":1,"3905,3904,975,976,976,977,3072":5,"1951,1950,487,488,488,489,1536":10,"973,972,242,243,243,244,768":28,"15627,15626,3906,3907,3907,3908,12288":1,"3907,3906,976,977,977,978,3072":5,"7811,7810,1952,1953,1953,1954,6144":3,"3903,3902,975,976,976,977,3072":5,"1949,1948,486,487,487,488,1536":9,"31251,31250,7812,7813,7813,7814,24576":1,"7813,7812,1952,1953,1953,1954,6144":2,"15623,15622,3905,3906,3906,3907,12288":1,"7809,7808,1951,1952,1952,1953,6144":2,"62499,62498,15624,15625,15625,15626,49152":1,"15625,15624,3905,3906,3906,3907,12288":1,"31247,31246,7811,7812,7812,7813,24576":1,"15621,15620,3904,3905,3905,3906,12288":1,"374986,374985,31248,31249,31249,31250,393216":1,"3583,3582,895,896,896,897,3072":2,"1789,1788,446,447,447,448,1536":10,"7163,7162,1790,1791,1791,1792,6144":2,"3579,3578,894,895,895,896,3072":6,"1787,1786,446,447,447,448,1536":12,"891,890,222,223,223,224,768":24,"443,442,110,111,111,112,384":47,"219,218,54,55,55,56,192":66,"107,106,26,27,27,28,96":74,"14325,14324,3580,3581,3581,3582,12288":1,"3581,3580,894,895,895,896,3072":5,"7161,7160,1789,1790,1790,1791,6144":3,"28647,28646,7161,7162,7162,7163,24576":1,"14321,14320,3579,3580,3580,3581,12288":1,"7159,7158,1789,1790,1790,1791,6144":2,"3577,3576,893,894,894,895,3072":3,"57291,57290,14322,14323,14323,14324,49152":1,"14323,14322,3580,3581,3581,3582,12288":1,"28643,28642,7160,7161,7161,7162,24576":1,"14319,14318,3579,3580,3580,3581,12288":1,"7157,7156,1788,1789,1789,1790,6144":1,"343736,343735,28644,28645,28645,28646,393216":1,"3285,3284,820,821,821,822,3072":1,"1641,1640,409,410,410,411,1536":11,"6567,6566,1641,1642,1642,1643,6144":1,"3281,3280,819,820,820,821,3072":6,"1639,1638,409,410,410,411,1536":12,"817,816,203,204,204,205,768":30,"13131,13130,3282,3283,3283,3284,12288":1,"3283,3282,820,821,821,822,3072":5,"6563,6562,1640,1641,1641,1642,6144":2,"3279,3278,819,820,820,821,3072":4,"1637,1636,408,409,409,410,1536":9,"26259,26258,6564,6565,6565,6566,24576":1,"6565,6564,1640,1641,1641,1642,6144":3,"13127,13126,3281,3282,3282,3283,12288":2,"6561,6560,1639,1640,1640,1641,6144":2,"52517,52516,13128,13129,13129,13130,49152":1,"13129,13128,3281,3282,3282,3283,12288":1,"26257,26256,6563,6564,6564,6565,24576":1,"315090,315089,26257,26258,26258,26259,393216":1,"3011,3010,752,753,753,754,3072":2,"1503,1502,375,376,376,377,1536":11,"749,748,186,187,187,188,768":34,"6019,6018,1504,1505,1505,1506,6144":2,"3007,3006,751,752,752,753,3072":5,"1501,1500,374,375,375,376,1536":13,"12037,12036,3008,3009,3009,3010,12288":1,"3009,3008,751,752,752,753,3072":6,"6017,6016,1503,1504,1504,1505,6144":3,"24071,24070,6017,6018,6018,6019,24576":1,"12033,12032,3007,3008,3008,3009,12288":2,"6015,6014,1503,1504,1504,1505,6144":3,"3005,3004,750,751,751,752,3072":3,"48141,48140,12034,12035,12035,12036,49152":1,"12035,12034,3008,3009,3009,3010,12288":1,"24069,24068,6016,6017,6017,6018,24576":1,"288831,288830,24069,24070,24070,24071,393216":1,"2759,2758,689,690,690,691,3072":6,"1377,1376,343,344,344,345,1536":14,"5517,5516,1378,1379,1379,1380,6144":3,"2757,2756,688,689,689,690,3072":5,"11033,11032,2757,2758,2758,2759,12288":2,"5515,5514,1378,1379,1379,1380,6144":3,"2755,2754,688,689,689,690,3072":5,"1375,1374,343,344,344,345,1536":10,"685,684,170,171,171,172,768":22,"22065,22064,5515,5516,5516,5517,24576":1,"11031,11030,2757,2758,2758,2759,12288":1,"5513,5512,1377,1378,1378,1379,6144":2,"44129,44128,11031,11032,11032,11033,49152":1,"22063,22062,5515,5516,5516,5517,24576":1,"11029,11028,2756,2757,2757,2758,12288":1,"264760,264759,22063,22064,22064,22065,393216":1,"5059,5058,1264,1265,1265,1266,6144":1,"2527,2526,631,632,632,633,3072":5,"1261,1260,314,315,315,316,1536":15,"10115,10114,2528,2529,2529,2530,12288":1,"2529,2528,631,632,632,633,3072":5,"5055,5054,1263,1264,1264,1265,6144":3,"2525,2524,630,631,631,632,3072":5,"20227,20226,5056,5057,5057,5058,24576":1,"5057,5056,1263,1264,1264,1265,6144":2,"10111,10110,2527,2528,2528,2529,12288":1,"5053,5052,1262,1263,1263,1264,6144":2,"40451,40450,10112,10113,10113,10114,49152":1,"10113,10112,2527,2528,2528,2529,12288":1,"20223,20222,5055,5056,5056,5057,24576":1,"10109,10108,2526,2527,2527,2528,12288":1,"242695,242694,20224,20225,20225,20226,393216":1,"2319,2318,579,580,580,581,3072":4,"1157,1156,288,289,289,290,1536":14,"4637,4636,1158,1159,1159,1160,6144":1,"2317,2316,578,579,579,580,3072":5,"9271,9270,2317,2318,2318,2319,12288":1,"4633,4632,1157,1158,1158,1159,6144":3,"2315,2314,578,579,579,580,3072":6,"1155,1154,288,289,289,290,1536":12,"575,574,143,144,144,145,768":26,"285,284,70,71,71,72,384":41,"18541,18540,4634,4635,4635,4636,24576":1,"4635,4634,1158,1159,1159,1160,6144":3,"9269,9268,2316,2317,2317,2318,12288":2,"37079,37078,9269,9270,9270,9271,49152":1,"18537,18536,4633,4634,4634,4635,24576":1,"9267,9266,2316,2317,2317,2318,12288":1,"4631,4630,1157,1158,1158,1159,6144":1,"2313,2312,577,578,578,579,3072":2,"222469,222468,18538,18539,18539,18540,393216":1,"4251,4250,1062,1063,1063,1064,6144":1,"2123,2122,530,531,531,532,3072":6,"1059,1058,264,265,265,266,1536":15,"527,526,131,132,132,133,768":30,"261,260,64,65,65,66,384":44,"8499,8498,2124,2125,2125,2126,12288":1,"2125,2124,530,531,531,532,3072":5,"4247,4246,1061,1062,1062,1063,6144":2,"2121,2120,529,530,530,531,3072":4,"16995,16994,4248,4249,4249,4250,24576":1,"4249,4248,1061,1062,1062,1063,6144":3,"8495,8494,2123,2124,2124,2125,12288":2,"4245,4244,1060,1061,1061,1062,6144":2,"33989,33988,8496,8497,8497,8498,49152":1,"8497,8496,2123,2124,2124,2125,12288":1,"16993,16992,4247,4248,4248,4249,24576":1,"203929,203928,16993,16994,16994,16995,196608":1,"3897,3896,973,974,974,975,3072":1,"1947,1946,486,487,487,488,1536":5,"971,970,242,243,243,244,768":16,"483,482,120,121,121,122,384":32,"239,238,59,60,60,61,192":48,"117,116,28,29,29,30,96":56,"7791,7790,1947,1948,1948,1949,6144":1,"3893,3892,972,973,973,974,3072":2,"1945,1944,485,486,486,487,1536":5,"15579,15578,3894,3895,3895,3896,12288":1,"3895,3894,973,974,974,975,3072":3,"7787,7786,1946,1947,1947,1948,6144":2,"3891,3890,972,973,973,974,3072":2,"1943,1942,485,486,486,487,1536":4,"969,968,241,242,242,243,768":10,"31157,31156,7788,7789,7789,7790,24576":1,"7789,7788,1946,1947,1947,1948,6144":1,"15577,15576,3893,3894,3894,3895,12288":1,"186934,186933,15577,15578,15578,15579,196608":1,"3571,3570,892,893,893,894,3072":3,"1783,1782,445,446,446,447,1536":6,"889,888,221,222,222,223,768":15,"7141,7140,1784,1785,1785,1786,6144":2,"1785,1784,445,446,446,447,1536":5,"3569,3568,891,892,892,893,3072":3,"14281,14280,3569,3570,3570,3571,12288":1,"7139,7138,1784,1785,1785,1786,6144":1,"3567,3566,891,892,892,893,3072":2,"1781,1780,444,445,445,446,1536":4,"28561,28560,7139,7140,7140,7141,24576":1,"14279,14278,3569,3570,3570,3571,12288":1,"7137,7136,1783,1784,1784,1785,6144":1,"171355,171354,14279,14280,14280,14281,196608":1,"3275,3274,818,819,819,820,3072":1,"1635,1634,408,409,409,410,1536":6,"815,814,203,204,204,205,768":17,"405,404,100,101,101,102,384":31,"6547,6546,1636,1637,1637,1638,6144":1,"3271,3270,817,818,818,819,3072":2,"1633,1632,407,408,408,409,1536":6,"13091,13090,3272,3273,3273,3274,12288":1,"3273,3272,817,818,818,819,3072":3,"6543,6542,1635,1636,1636,1637,6144":2,"3269,3268,816,817,817,818,3072":2,"26181,26180,6544,6545,6545,6546,24576":1,"6545,6544,1635,1636,1636,1637,6144":1,"13089,13088,3271,3272,3272,3273,12288":1,"157074,157073,13089,13090,13090,13091,196608":1,"3001,3000,749,750,750,751,3072":3,"1499,1498,374,375,375,376,1536":6,"747,746,186,187,187,188,768":18,"371,370,92,93,93,94,384":33,"183,182,45,46,46,47,192":42,"6001,6000,1499,1500,1500,1501,6144":1,"2999,2998,749,750,750,751,3072":2,"1497,1496,373,374,374,375,1536":7,"12001,12000,2999,3000,3000,3001,12288":1,"5999,5998,1499,1500,1500,1501,6144":2,"2997,2996,748,749,749,750,3072":3,"23999,23998,5999,6000,6000,6001,24576":1,"11997,11996,2998,2999,2999,3000,12288":1,"5997,5996,1498,1499,1499,1500,6144":1,"143983,143982,11998,11999,11999,12000,196608":1,"2751,2750,687,688,688,689,3072":3,"1373,1372,342,343,343,344,1536":6,"5501,5500,1374,1375,1375,1376,6144":1,"2749,2748,686,687,687,688,3072":2,"11001,11000,2749,2750,2750,2751,12288":1,"5499,5498,1374,1375,1375,1376,6144":2,"2747,2746,686,687,687,688,3072":3,"1371,1370,342,343,343,344,1536":6,"683,682,170,171,171,172,768":13,"339,338,84,85,85,86,384":20,"167,166,41,42,42,43,192":27,"21999,21998,5499,5500,5500,5501,24576":1,"10997,10996,2748,2749,2749,2750,12288":1,"5497,5496,1373,1374,1374,1375,6144":1,"131983,131982,10998,10999,10999,11000,196608":1,"2523,2522,630,631,631,632,3072":1,"1259,1258,314,315,315,316,1536":7,"627,626,156,157,157,158,768":18,"311,310,77,78,78,79,384":30,"153,152,37,38,38,39,192":38,"5043,5042,1260,1261,1261,1262,6144":1,"2519,2518,629,630,630,631,3072":2,"1257,1256,313,314,314,315,1536":7,"10083,10082,2520,2521,2521,2522,12288":1,"2521,2520,629,630,630,631,3072":3,"5039,5038,1259,1260,1260,1261,6144":2,"2517,2516,628,629,629,630,3072":2,"20165,20164,5040,5041,5041,5042,24576":1,"5041,5040,1259,1260,1260,1261,6144":1,"10081,10080,2519,2520,2520,2521,12288":1,"120983,120982,10081,10082,10082,10083,196608":1,"4623,4622,1155,1156,1156,1157,6144":1,"2309,2308,576,577,577,578,3072":2,"1153,1152,287,288,288,289,1536":8,"9243,9242,2310,2311,2311,2312,12288":1,"2311,2310,577,578,578,579,3072":3,"4619,4618,1154,1155,1155,1156,6144":2,"2307,2306,576,577,577,578,3072":2,"1151,1150,287,288,288,289,1536":4,"573,572,142,143,143,144,768":12,"18485,18484,4620,4621,4621,4622,24576":1,"4621,4620,1154,1155,1155,1156,6144":1,"9241,9240,2309,2310,2310,2311,12288":1,"110900,110899,9241,9242,9242,9243,196608":1,"2119,2118,529,530,530,531,3072":3,"1057,1056,263,264,264,265,1536":9,"4237,4236,1058,1059,1059,1060,6144":2,"2117,2116,528,529,529,530,3072":3,"8473,8472,2117,2118,2118,2119,12288":1,"4235,4234,1058,1059,1059,1060,6144":1,"2115,2114,528,529,529,530,3072":2,"1055,1054,263,264,264,265,1536":5,"525,524,130,131,131,132,768":11,"16945,16944,4235,4236,4236,4237,24576":1,"8471,8470,2117,2118,2118,2119,12288":1,"4233,4232,1057,1058,1058,1059,6144":1,"101657,101656,8471,8472,8472,8473,98304":1,"3885,3884,970,971,971,972,3072":1,"1941,1940,484,485,485,486,1536":3,"7767,7766,1941,1942,1942,1943,6144":1,"3881,3880,969,970,970,971,3072":2,"1939,1938,484,485,485,486,1536":3,"967,966,241,242,242,243,768":6,"481,480,119,120,120,121,384":13,"15533,15532,3882,3883,3883,3884,12288":1,"3883,3882,970,971,971,972,3072":1,"7765,7764,1940,1941,1941,1942,6144":1,"93184,93183,7765,7766,7766,7767,98304":1,"3561,3560,889,890,890,891,3072":1,"1779,1778,444,445,445,446,1536":3,"887,886,221,222,222,223,768":8,"441,440,109,110,110,111,384":16,"7119,7118,1779,1780,1780,1781,6144":1,"3557,3556,888,889,889,890,3072":2,"1777,1776,443,444,444,445,1536":3,"14237,14236,3558,3559,3559,3560,12288":1,"3559,3558,889,890,890,891,3072":1,"7117,7116,1778,1779,1779,1780,6144":1,"85417,85416,7117,7118,7118,7119,98304":1,"3265,3264,815,816,816,817,3072":1,"1631,1630,407,408,408,409,1536":3,"813,812,202,203,203,204,768":9,"6527,6526,1631,1632,1632,1633,6144":1,"3261,3260,814,815,815,816,3072":1,"1629,1628,406,407,407,408,1536":3,"13051,13050,3262,3263,3263,3264,12288":1,"3263,3262,815,816,816,817,3072":1,"6523,6522,1630,1631,1631,1632,6144":1,"3259,3258,814,815,815,816,3072":1,"1627,1626,406,407,407,408,1536":2,"811,810,202,203,203,204,768":4,"403,402,100,101,101,102,384":8,"199,198,49,50,50,51,192":13,"78298,78297,6524,6525,6525,6526,98304":1,"2993,2992,747,748,748,749,3072":1,"1495,1494,373,374,374,375,1536":3,"745,744,185,186,186,187,768":9,"5983,5982,1495,1496,1496,1497,6144":1,"2989,2988,746,747,747,748,3072":1,"1493,1492,372,373,373,374,1536":3,"11963,11962,2990,2991,2991,2992,12288":1,"2991,2990,747,748,748,749,3072":1,"5979,5978,1494,1495,1495,1496,6144":1,"2987,2986,746,747,747,748,3072":1,"1491,1490,372,373,373,374,1536":2,"743,742,185,186,186,187,768":4,"369,368,91,92,92,93,384":8,"71772,71771,5980,5981,5981,5982,98304":1,"2743,2742,685,686,686,687,3072":1,"1369,1368,341,342,342,343,1536":4,"5485,5484,1370,1371,1371,1372,6144":1,"2741,2740,684,685,685,686,3072":2,"10967,10966,2741,2742,2742,2743,12288":1,"5481,5480,1369,1370,1370,1371,6144":1,"2739,2738,684,685,685,686,3072":1,"1367,1366,341,342,342,343,1536":2,"681,680,169,170,170,171,768":5,"65790,65789,5482,5483,5483,5484,98304":1,"2515,2514,628,629,629,630,3072":1,"1255,1254,313,314,314,315,1536":3,"625,624,155,156,156,157,768":9,"5027,5026,1256,1257,1257,1258,6144":1,"2511,2510,627,628,628,629,3072":2,"1253,1252,312,313,313,314,1536":3,"10053,10052,2512,2513,2513,2514,12288":1,"2513,2512,627,628,628,629,3072":1,"5025,5024,1255,1256,1256,1257,6144":1,"60306,60305,5025,5026,5026,5027,98304":1,"2305,2304,575,576,576,577,3072":1,"4609,4608,1151,1152,1152,1153,6144":1,"2303,2302,575,576,576,577,3072":2,"1149,1148,286,287,287,288,1536":5,"9215,9214,2303,2304,2304,2305,12288":1,"4605,4604,1150,1151,1151,1152,6144":1,"2301,2300,574,575,575,576,3072":1,"55279,55278,4606,4607,4607,4608,98304":1,"2113,2112,527,528,528,529,3072":1,"4225,4224,1055,1056,1056,1057,6144":1,"2111,2110,527,528,528,529,3072":2,"1053,1052,262,263,263,264,1536":4,"8447,8446,2111,2112,2112,2113,12288":1,"4221,4220,1054,1055,1055,1056,6144":1,"2109,2108,526,527,527,528,3072":1,"50671,50670,4222,4223,4223,4224,49152":1,"1937,1936,483,484,484,485,1536":1,"3873,3872,967,968,968,969,3072":1,"1935,1934,483,484,484,485,1536":2,"965,964,240,241,241,242,768":4,"7743,7742,1935,1936,1936,1937,6144":1,"3869,3868,966,967,967,968,3072":1,"1933,1932,482,483,483,484,1536":1,"46447,46446,3870,3871,3871,3872,49152":1,"1775,1774,443,444,444,445,1536":2,"885,884,220,221,221,222,768":5,"3549,3548,886,887,887,888,3072":1,"1773,1772,442,443,443,444,1536":1,"7097,7096,1773,1774,1774,1775,6144":1,"3547,3546,886,887,887,888,3072":1,"1771,1770,442,443,443,444,1536":1,"883,882,220,221,221,222,768":3,"439,438,109,110,110,111,384":4,"217,216,53,54,54,55,192":8,"42575,42574,3547,3548,3548,3549,49152":1,"3255,3254,813,814,814,815,3072":1,"1625,1624,405,406,406,407,1536":1,"6507,6506,1626,1627,1627,1628,6144":1,"3251,3250,812,813,813,814,3072":1,"1623,1622,405,406,406,407,1536":2,"809,808,201,202,202,203,768":3,"39026,39025,3252,3253,3253,3254,49152":1,"2983,2982,745,746,746,747,3072":1,"1489,1488,371,372,372,373,1536":1,"5963,5962,1490,1491,1491,1492,6144":1,"2979,2978,744,745,745,746,3072":1,"1487,1486,371,372,372,373,1536":2,"741,740,184,185,185,186,768":4,"35772,35771,2980,2981,2981,2982,49152":1,"2735,2734,683,684,684,685,3072":1,"1365,1364,340,341,341,342,1536":1,"5467,5466,1366,1367,1367,1368,6144":1,"2731,2730,682,683,683,684,3072":1,"1363,1362,340,341,341,342,1536":2,"679,678,169,170,170,171,768":3,"337,336,83,84,84,85,384":6,"32790,32789,2732,2733,2733,2734,49152":1,"2507,2506,626,627,627,628,3072":1,"1251,1250,312,313,313,314,1536":1,"623,622,155,156,156,157,768":4,"309,308,76,77,77,78,384":7,"5011,5010,1252,1253,1253,1254,6144":1,"2503,2502,625,626,626,627,3072":1,"1249,1248,311,312,312,313,1536":2,"30056,30055,2504,2505,2505,2506,49152":1,"2297,2296,573,574,574,575,3072":1,"1147,1146,286,287,287,288,1536":1,"571,570,142,143,143,144,768":4,"283,282,70,71,71,72,384":8,"139,138,34,35,35,36,192":8,"4593,4592,1147,1148,1148,1149,6144":1,"2295,2294,573,574,574,575,3072":1,"1145,1144,285,286,286,287,1536":2,"27550,27549,2295,2296,2296,2297,49152":1,"2107,2106,526,527,527,528,3072":1,"1051,1050,262,263,263,264,1536":2,"523,522,130,131,131,132,768":4,"259,258,64,65,65,66,384":8,"127,126,31,32,32,33,96":8,"4211,4210,1052,1053,1053,1054,6144":1,"2103,2102,525,526,526,527,3072":1,"1049,1048,261,262,262,263,1536":1,"25253,25252,2104,2105,2105,2106,24576":1,"1931,1930,482,483,483,484,1536":1,"963,962,240,241,241,242,768":2,"479,478,119,120,120,121,384":3,"237,236,58,59,59,60,192":7,"3859,3858,964,965,965,966,3072":1,"1927,1926,481,482,482,483,1536":1,"961,960,239,240,240,241,768":1,"23147,23146,1928,1929,1929,1930,24576":1,"1769,1768,441,442,442,443,1536":1,"3537,3536,883,884,884,885,3072":1,"1767,1766,441,442,442,443,1536":1,"881,880,219,220,220,221,768":1,"21217,21216,1767,1768,1768,1769,24576":1,"3243,3242,810,811,811,812,3072":1,"1619,1618,404,405,405,406,1536":1,"807,806,201,202,202,203,768":2,"401,400,99,100,100,101,384":4,"19448,19447,1620,1621,1621,1622,24576":1,"2973,2972,742,743,743,744,3072":1,"1485,1484,370,371,371,372,1536":1,"17826,17825,1485,1486,1486,1487,24576":1,"2725,2724,680,681,681,682,3072":1,"1361,1360,339,340,340,341,1536":1,"16339,16338,1361,1362,1362,1363,24576":1,"2497,2496,623,624,624,625,3072":1,"1247,1246,311,312,312,313,1536":1,"621,620,154,155,155,156,768":2,"14976,14975,1247,1248,1248,1249,24576":1,"2289,2288,571,572,572,573,3072":1,"1143,1142,285,286,286,287,1536":1,"569,568,141,142,142,143,768":3,"13727,13726,1143,1144,1144,1145,24576":1,"2099,2098,524,525,525,526,3072":1,"1047,1046,261,262,262,263,1536":1,"521,520,129,130,130,131,768":3,"12582,12581,1048,1049,1049,1050,12288":1,"1923,1922,480,481,481,482,1536":1,"959,958,239,240,240,241,768":2,"477,476,118,119,119,120,384":3,"11532,11531,960,961,961,962,12288":1,"1763,1762,440,441,441,442,1536":1,"879,878,219,220,220,221,768":2,"437,436,108,109,109,110,384":3,"10570,10569,880,881,881,882,12288":1,"1617,1616,403,404,404,405,1536":1,"9688,9687,807,808,808,809,12288":1,"1481,1480,369,370,370,371,1536":1,"739,738,184,185,185,186,768":2,"367,366,91,92,92,93,384":3,"181,180,44,45,45,46,192":3,"8879,8878,739,740,740,741,12288":1,"1359,1358,339,340,340,341,1536":1,"677,676,168,169,169,170,768":2,"8138,8137,678,679,679,680,12288":1,"1245,1244,310,311,311,312,1536":1,"7458,7457,621,622,622,623,12288":1,"1141,1140,284,285,285,286,1536":1,"6835,6834,569,570,570,571,12288":1,"1045,1044,260,261,261,262,1536":1,"6264,6263,521,522,522,523,6144":1,"5741,5740,478,479,479,480,6144":1,"5261,5260,438,439,439,440,6144":1,"805,804,200,201,201,202,768":1,"4821,4820,401,402,402,403,6144":1,"4418,4417,368,369,369,370,6144":1,"4048,4047,337,338,338,339,6144":1,"619,618,154,155,155,156,768":1,"307,306,76,77,77,78,384":1,"151,150,37,38,38,39,192":1,"3709,3708,308,309,309,310,6144":1,"3399,3398,283,284,284,285,6144":1,"3114,3113,259,260,260,261,3072":1,"2853,2852,237,238,238,239,3072":1,"2614,2613,217,218,218,219,3072":1,"2395,2394,199,200,200,201,3072":1,"2194,2193,182,183,183,184,3072":1,"2010,2009,167,168,168,169,3072":1,"1841,1840,153,154,154,155,3072":1,"1686,1685,140,141,141,142,3072":1,"1544,1543,128,129,129,130,1536":1,"1414,1413,117,118,118,119,1536":1,"1295,1294,107,108,108,109,1536":1,"1186,1185,98,99,99,100,1536":1,"1086,1085,90,91,91,92,1536":1,"994,993,82,83,83,84,1536":1,"910,909,75,76,76,77,1536":1,"833,832,69,70,70,71,768":1,"762,761,63,64,64,65,768":1,"697,696,57,58,58,59,768":1,"638,637,53,54,54,55,768":1,"583,582,48,49,49,50,768":1,"533,532,44,45,45,46,768":1,"487,486,40,41,41,42,768":1,"445,444,36,37,37,38,768":1,"407,406,33,34,34,35,384":1,"372,371,30,31,31,32,384":1,"340,339,28,29,29,30,384":1,"310,309,25,26,26,27,384":1,"283,282,23,24,24,25,384":1,"258,257,21,22,22,23,384":1,"195,194,16,17,17,18,192":1,"177,176,14,15,15,16,192":1,"161,160,13,14,14,15,192":1},"matmul_shared":{"38,39,39,40,40,41,41,42,96":204,"37,38,38,39,39,40,40,41,96":681,"77,78,78,79,80,81,81,82,192":204,"37,38,38,39,40,41,41,42,96":645,"77,78,78,79,79,80,80,81,192":311,"157,158,158,159,159,160,160,161,384":77,"36,37,37,38,39,40,40,41,96":478,"76,77,77,78,79,80,80,81,192":334,"156,157,157,158,159,160,160,161,384":127,"316,317,317,318,318,319,319,320,768":34,"156,157,157,158,158,159,159,160,384":150,"315,316,316,317,318,319,319,320,768":43,"634,635,635,636,636,637,637,638,1536":13,"315,316,316,317,317,318,318,319,768":62,"633,634,634,635,636,637,637,638,1536":21,"1270,1271,1271,1272,1272,1273,1273,1274,3072":2,"633,634,634,635,635,636,636,637,1536":21,"1269,1270,1270,1271,1271,1272,1272,1273,3072":10,"2541,2542,2542,2543,2544,2545,2545,2546,6144":2,"1269,1270,1270,1271,1272,1273,1273,1274,3072":11,"76,77,77,78,78,79,79,80,192":136,"155,156,156,157,158,159,159,160,384":84,"314,315,315,316,317,318,318,319,768":31,"632,633,633,634,635,636,636,637,1536":9,"1268,1269,1269,1270,1271,1272,1272,1273,3072":9,"2540,2541,2541,2542,2543,2544,2544,2545,6144":6,"5084,5085,5085,5086,5087,5088,5088,5089,12288":2,"2541,2542,2542,2543,2543,2544,2544,2545,6144":5,"5084,5085,5085,5086,5086,5087,5087,5088,12288":3,"10171,10172,10172,10173,10173,10174,10174,10175,24576":1,"2540,2541,2541,2542,2542,2543,2543,2544,6144":3,"5083,5084,5084,5085,5086,5087,5087,5088,12288":2,"10170,10171,10171,10172,10172,10173,10173,10174,24576":1,"20343,20344,20344,20345,20346,20347,20347,20348,49152":1,"10170,10171,10171,10172,10173,10174,10174,10175,24576":1,"5083,5084,5084,5085,5085,5086,5086,5087,12288":1,"10169,10170,10170,10171,10172,10173,10173,10174,24576":1,"20342,20343,20343,20344,20345,20346,20346,20347,49152":1,"40688,40689,40689,40690,40691,40692,40692,40693,98304":1,"34,35,35,36,37,38,38,39,96":445,"34,35,35,36,36,37,37,38,96":672,"71,72,72,73,73,74,74,75,192":143,"33,34,34,35,36,37,37,38,96":684,"70,71,71,72,73,74,74,75,192":302,"144,145,145,146,146,147,147,148,384":35,"70,71,71,72,72,73,73,74,192":333,"143,144,144,145,145,146,146,147,384":143,"289,290,290,291,292,293,293,294,768":35,"143,144,144,145,146,147,147,148,384":108,"289,290,290,291,291,292,292,293,768":44,"581,582,582,583,583,584,584,585,1536":13,"33,34,34,35,35,36,36,37,96":238,"69,70,70,71,72,73,73,74,192":196,"142,143,143,144,145,146,146,147,384":124,"288,289,289,290,291,292,292,293,768":64,"580,581,581,582,583,584,584,585,1536":22,"1164,1165,1165,1166,1166,1167,1167,1168,3072":3,"580,581,581,582,582,583,583,584,1536":21,"1163,1164,1164,1165,1165,1166,1166,1167,3072":11,"2329,2330,2330,2331,2332,2333,2333,2334,6144":3,"1163,1164,1164,1165,1166,1167,1167,1168,3072":10,"288,289,289,290,290,291,291,292,768":34,"579,580,580,581,582,583,583,584,1536":10,"1162,1163,1163,1164,1165,1166,1166,1167,3072":8,"2328,2329,2329,2330,2331,2332,2332,2333,6144":5,"4660,4661,4661,4662,4663,4664,4664,4665,12288":3,"2329,2330,2330,2331,2331,2332,2332,2333,6144":5,"4660,4661,4661,4662,4662,4663,4663,4664,12288":2,"9323,9324,9324,9325,9325,9326,9326,9327,24576":1,"2328,2329,2329,2330,2330,2331,2331,2332,6144":3,"4659,4660,4660,4661,4662,4663,4663,4664,12288":3,"9322,9323,9323,9324,9325,9326,9326,9327,24576":2,"18648,18649,18649,18650,18650,18651,18651,18652,49152":1,"9322,9323,9323,9324,9324,9325,9325,9326,24576":1,"18647,18648,18648,18649,18649,18650,18650,18651,49152":1,"37297,37298,37298,37299,37300,37301,37301,37302,98304":1,"31,32,32,33,34,35,35,36,96":407,"31,32,32,33,33,34,34,35,96":674,"65,66,66,67,67,68,68,69,192":110,"30,31,31,32,33,34,34,35,96":685,"64,65,65,66,67,68,68,69,192":297,"132,133,133,134,134,135,135,136,384":10,"64,65,65,66,66,67,67,68,192":336,"131,132,132,133,133,134,134,135,384":140,"265,266,266,267,268,269,269,270,768":10,"131,132,132,133,134,135,135,136,384":100,"30,31,31,32,32,33,33,34,96":273,"63,64,64,65,66,67,67,68,192":228,"130,131,131,132,133,134,134,135,384":147,"264,265,265,266,267,268,268,269,768":57,"532,533,533,534,535,536,536,537,1536":10,"265,266,266,267,267,268,268,269,768":43,"264,265,265,266,266,267,267,268,768":55,"531,532,532,533,534,535,535,536,1536":21,"1066,1067,1067,1068,1069,1070,1070,1071,3072":10,"532,533,533,534,534,535,535,536,1536":22,"1066,1067,1067,1068,1068,1069,1069,1070,3072":11,"2135,2136,2136,2137,2137,2138,2138,2139,6144":5,"531,532,532,533,533,534,534,535,1536":15,"1065,1066,1066,1067,1068,1069,1069,1070,3072":11,"2134,2135,2135,2136,2137,2138,2138,2139,6144":5,"4272,4273,4273,4274,4274,4275,4275,4276,12288":2,"2134,2135,2135,2136,2136,2137,2137,2138,6144":6,"4271,4272,4272,4273,4274,4275,4275,4276,12288":3,"8546,8547,8547,8548,8548,8549,8549,8550,24576":1,"4271,4272,4272,4273,4273,4274,4274,4275,12288":3,"8545,8546,8546,8547,8547,8548,8548,8549,24576":2,"17093,17094,17094,17095,17096,17097,17097,17098,49152":1,"8545,8546,8546,8547,8548,8549,8549,8550,24576":1,"17093,17094,17094,17095,17095,17096,17096,17097,49152":1,"34189,34190,34190,34191,34191,34192,34192,34193,98304":1,"29,30,30,31,31,32,32,33,96":80,"28,29,29,30,30,31,31,32,96":680,"59,60,60,61,62,63,63,64,192":80,"28,29,29,30,31,32,32,33,96":629,"27,28,28,29,30,31,31,32,96":602,"58,59,59,60,61,62,62,63,192":336,"120,121,121,122,123,124,124,125,384":80,"59,60,60,61,61,62,62,63,192":293,"120,121,121,122,122,123,123,124,384":137,"243,244,244,245,245,246,246,247,768":31,"58,59,59,60,60,61,61,62,192":259,"119,120,120,121,122,123,123,124,384":156,"242,243,243,244,245,246,246,247,768":49,"488,489,489,490,490,491,491,492,1536":10,"242,243,243,244,244,245,245,246,768":63,"487,488,488,489,489,490,490,491,1536":21,"977,978,978,979,980,981,981,982,3072":10,"487,488,488,489,490,491,491,492,1536":21,"977,978,978,979,979,980,980,981,3072":10,"1957,1958,1958,1959,1959,1960,1960,1961,6144":4,"119,120,120,121,121,122,122,123,384":87,"241,242,242,243,244,245,245,246,768":43,"486,487,487,488,489,490,490,491,1536":18,"976,977,977,978,979,980,980,981,3072":11,"1956,1957,1957,1958,1959,1960,1960,1961,6144":6,"3916,3917,3917,3918,3918,3919,3919,3920,12288":2,"1956,1957,1957,1958,1958,1959,1959,1960,6144":5,"3915,3916,3916,3917,3917,3918,3918,3919,12288":3,"7833,7834,7834,7835,7836,7837,7837,7838,24576":2,"3915,3916,3916,3917,3918,3919,3919,3920,12288":2,"7833,7834,7834,7835,7835,7836,7836,7837,24576":1,"15669,15670,15670,15671,15671,15672,15672,15673,49152":1,"976,977,977,978,978,979,979,980,3072":1,"1955,1956,1956,1957,1958,1959,1959,1960,6144":1,"3914,3915,3915,3916,3917,3918,3918,3919,12288":1,"7832,7833,7833,7834,7835,7836,7836,7837,24576":1,"15668,15669,15669,15670,15671,15672,15672,15673,49152":1,"31340,31341,31341,31342,31342,31343,31343,31344,98304":1,"26,27,27,28,29,30,30,31,96":39,"25,26,26,27,28,29,29,30,96":682,"54,55,55,56,57,58,58,59,192":39,"26,27,27,28,28,29,29,30,96":610,"25,26,26,27,27,28,28,29,96":642,"53,54,54,55,56,57,57,58,192":333,"110,111,111,112,113,114,114,115,384":39,"54,55,55,56,56,57,57,58,192":277,"53,54,54,55,55,56,56,57,192":300,"109,110,110,111,112,113,113,114,384":155,"222,223,223,224,225,226,226,227,768":39,"110,111,111,112,112,113,113,114,384":122,"222,223,223,224,224,225,225,226,768":56,"447,448,448,449,449,450,450,451,1536":18,"109,110,110,111,111,112,112,113,384":125,"221,222,222,223,224,225,225,226,768":66,"446,447,447,448,449,450,450,451,1536":21,"896,897,897,898,898,899,899,900,3072":7,"446,447,447,448,448,449,449,450,1536":23,"895,896,896,897,898,899,899,900,3072":11,"1794,1795,1795,1796,1796,1797,1797,1798,6144":2,"895,896,896,897,897,898,898,899,3072":10,"1793,1794,1794,1795,1795,1796,1796,1797,6144":5,"3589,3590,3590,3591,3592,3593,3593,3594,12288":2,"1793,1794,1794,1795,1796,1797,1797,1798,6144":5,"221,222,222,223,223,224,224,225,768":36,"445,446,446,447,448,449,449,450,1536":15,"894,895,895,896,897,898,898,899,3072":4,"1792,1793,1793,1794,1795,1796,1796,1797,6144":4,"3588,3589,3589,3590,3591,3592,3592,3593,12288":3,"7180,7181,7181,7182,7183,7184,7184,7185,24576":2,"3589,3590,3590,3591,3591,3592,3592,3593,12288":2,"7180,7181,7181,7182,7182,7183,7183,7184,24576":1,"14363,14364,14364,14365,14365,14366,14366,14367,49152":1,"3588,3589,3589,3590,3590,3591,3591,3592,12288":1,"7179,7180,7180,7181,7182,7183,7183,7184,24576":1,"14362,14363,14363,14364,14365,14366,14366,14367,49152":1,"28728,28729,28729,28730,28730,28731,28731,28732,98304":1,"49,50,50,51,52,53,53,54,192":210,"49,50,50,51,51,52,52,53,192":328,"101,102,102,103,103,104,104,105,384":70,"48,49,49,50,51,52,52,53,192":341,"100,101,101,102,103,104,104,105,384":140,"204,205,205,206,206,207,207,208,768":21,"100,101,101,102,102,103,103,104,384":162,"203,204,204,205,205,206,206,207,768":66,"409,410,410,411,412,413,413,414,1536":21,"203,204,204,205,206,207,207,208,768":49,"409,410,410,411,411,412,412,413,1536":22,"821,822,822,823,823,824,824,825,3072":11,"48,49,49,50,50,51,51,52,192":131,"99,100,100,101,102,103,103,104,384":96,"202,203,203,204,205,206,206,207,768":53,"408,409,409,410,411,412,412,413,1536":27,"820,821,821,822,823,824,824,825,3072":10,"1644,1645,1645,1646,1646,1647,1647,1648,6144":5,"820,821,821,822,822,823,823,824,3072":11,"1643,1644,1644,1645,1646,1647,1647,1648,6144":6,"3290,3291,3291,3292,3292,3293,3293,3294,12288":3,"1643,1644,1644,1645,1645,1646,1646,1647,6144":5,"3289,3290,3290,3291,3292,3293,3293,3294,12288":2,"6582,6583,6583,6584,6584,6585,6585,6586,24576":1,"3289,3290,3290,3291,3291,3292,3292,3293,12288":3,"6581,6582,6582,6583,6584,6585,6585,6586,24576":2,"13166,13167,13167,13168,13168,13169,13169,13170,49152":1,"6581,6582,6582,6583,6583,6584,6584,6585,24576":1,"13165,13166,13166,13167,13167,13168,13168,13169,49152":1,"26333,26334,26334,26335,26336,26337,26337,26338,98304":1,"45,46,46,47,48,49,49,50,96":54,"44,45,45,46,47,48,48,49,96":339,"92,93,93,94,95,96,96,97,192":54,"45,46,46,47,47,48,48,49,96":300,"92,93,93,94,94,95,95,96,192":139,"187,188,188,189,189,190,190,191,384":9,"44,45,45,46,46,47,47,48,96":285,"91,92,92,93,94,95,95,96,192":161,"186,187,187,188,188,189,189,190,384":64,"375,376,376,377,378,379,379,380,768":9,"186,187,187,188,189,190,190,191,384":45,"91,92,92,93,93,94,94,95,192":113,"185,186,186,187,188,189,189,190,384":66,"374,375,375,376,377,378,378,379,768":24,"752,753,753,754,755,756,756,757,1536":9,"375,376,376,377,377,378,378,379,768":21,"752,753,753,754,754,755,755,756,1536":11,"1507,1508,1508,1509,1509,1510,1510,1511,3072":4,"374,375,375,376,376,377,377,378,768":23,"751,752,752,753,754,755,755,756,1536":10,"1506,1507,1507,1508,1509,1510,1510,1511,3072":5,"3016,3017,3017,3018,3018,3019,3019,3020,6144":1,"1506,1507,1507,1508,1508,1509,1509,1510,3072":5,"3015,3016,3016,3017,3017,3018,3018,3019,6144":2,"6033,6034,6034,6035,6036,6037,6037,6038,12288":1,"3015,3016,3016,3017,3018,3019,3019,3020,6144":3,"751,752,752,753,753,754,754,755,1536":2,"1505,1506,1506,1507,1508,1509,1509,1510,3072":2,"3014,3015,3015,3016,3017,3018,3018,3019,6144":2,"6032,6033,6033,6034,6035,6036,6036,6037,12288":2,"12068,12069,12069,12070,12071,12072,12072,12073,24576":1,"6033,6034,6034,6035,6035,6036,6036,6037,12288":1,"12068,12069,12069,12070,12070,12071,12071,12072,24576":1,"24139,24140,24140,24141,24141,24142,24142,24143,49152":1,"41,42,42,43,44,45,45,46,96":92,"40,41,41,42,43,44,44,45,96":339,"84,85,85,86,87,88,88,89,192":92,"41,42,42,43,43,44,44,45,96":317,"84,85,85,86,86,87,87,88,192":151,"171,172,172,173,173,174,174,175,384":33,"40,41,41,42,42,43,43,44,96":248,"83,84,84,85,86,87,87,88,192":166,"170,171,171,172,173,174,174,175,384":59,"344,345,345,346,346,347,347,348,768":12,"170,171,171,172,172,173,173,174,384":72,"343,344,344,345,346,347,347,348,768":21,"690,691,691,692,692,693,693,694,1536":1,"343,344,344,345,345,346,346,347,768":27,"689,690,690,691,691,692,692,693,1536":10,"1381,1382,1382,1383,1384,1385,1385,1386,3072":1,"689,690,690,691,692,693,693,694,1536":11,"83,84,84,85,85,86,86,87,192":76,"169,170,170,171,172,173,173,174,384":46,"342,343,343,344,345,346,346,347,768":20,"688,689,689,690,691,692,692,693,1536":10,"1380,1381,1381,1382,1383,1384,1384,1385,3072":6,"2764,2765,2765,2766,2767,2768,2768,2769,6144":1,"1381,1382,1382,1383,1383,1384,1384,1385,3072":5,"1380,1381,1381,1382,1382,1383,1383,1384,3072":4,"2763,2764,2764,2765,2766,2767,2767,2768,6144":2,"5530,5531,5531,5532,5533,5534,5534,5535,12288":1,"2764,2765,2765,2766,2766,2767,2767,2768,6144":3,"2763,2764,2764,2765,2765,2766,2766,2767,6144":2,"5529,5530,5530,5531,5532,5533,5533,5534,12288":2,"11062,11063,11063,11064,11065,11066,11066,11067,24576":1,"5530,5531,5531,5532,5532,5533,5533,5534,12288":1,"11062,11063,11063,11064,11064,11065,11065,11066,24576":1,"22127,22128,22128,22129,22129,22130,22130,22131,49152":1,"632,633,633,634,634,635,635,636,1536":9,"314,315,315,316,316,317,317,318,768":31,"631,632,632,633,634,635,635,636,1536":11,"1266,1267,1267,1268,1268,1269,1269,1270,3072":4,"631,632,632,633,633,634,634,635,1536":10,"1265,1266,1266,1267,1268,1269,1269,1270,3072":5,"2534,2535,2535,2536,2536,2537,2537,2538,6144":1,"1265,1266,1266,1267,1267,1268,1268,1269,3072":5,"2533,2534,2534,2535,2535,2536,2536,2537,6144":2,"5069,5070,5070,5071,5072,5073,5073,5074,12288":1,"2533,2534,2534,2535,2536,2537,2537,2538,6144":3,"155,156,156,157,157,158,158,159,384":39,"313,314,314,315,316,317,317,318,768":14,"630,631,631,632,633,634,634,635,1536":3,"1264,1265,1265,1266,1267,1268,1268,1269,3072":2,"2532,2533,2533,2534,2535,2536,2536,2537,6144":2,"5068,5069,5069,5070,5071,5072,5072,5073,12288":2,"10140,10141,10141,10142,10143,10144,10144,10145,24576":1,"5069,5070,5070,5071,5071,5072,5072,5073,12288":1,"10140,10141,10141,10142,10142,10143,10143,10144,24576":1,"20283,20284,20284,20285,20285,20286,20286,20287,49152":1,"142,143,143,144,144,145,145,146,384":56,"287,288,288,289,290,291,291,292,768":30,"578,579,579,580,581,582,582,583,1536":10,"1160,1161,1161,1162,1163,1164,1164,1165,3072":2,"579,580,580,581,581,582,582,583,1536":11,"578,579,579,580,580,581,581,582,1536":9,"1159,1160,1160,1161,1162,1163,1163,1164,3072":6,"2322,2323,2323,2324,2325,2326,2326,2327,6144":2,"1160,1161,1161,1162,1162,1163,1163,1164,3072":5,"2322,2323,2323,2324,2324,2325,2325,2326,6144":3,"4647,4648,4648,4649,4649,4650,4650,4651,12288":1,"1159,1160,1160,1161,1161,1162,1162,1163,3072":3,"2321,2322,2322,2323,2324,2325,2325,2326,6144":2,"4646,4647,4647,4648,4648,4649,4649,4650,12288":1,"9295,9296,9296,9297,9298,9299,9299,9300,24576":1,"4646,4647,4647,4648,4649,4650,4650,4651,12288":1,"2321,2322,2322,2323,2323,2324,2324,2325,6144":1,"4645,4646,4646,4647,4648,4649,4649,4650,12288":1,"9294,9295,9295,9296,9297,9298,9298,9299,24576":1,"18592,18593,18593,18594,18595,18596,18596,18597,49152":1,"130,131,131,132,132,133,133,134,384":66,"263,264,264,265,266,267,267,268,768":32,"530,531,531,532,532,533,533,534,1536":11,"1063,1064,1064,1065,1066,1067,1067,1068,3072":4,"530,531,531,532,533,534,534,535,1536":10,"1063,1064,1064,1065,1065,1066,1066,1067,3072":5,"2129,2130,2130,2131,2131,2132,2132,2133,6144":1,"263,264,264,265,265,266,266,267,768":20,"529,530,530,531,532,533,533,534,1536":8,"1062,1063,1063,1064,1065,1066,1066,1067,3072":5,"2128,2129,2129,2130,2130,2131,2131,2132,6144":2,"4259,4260,4260,4261,4262,4263,4263,4264,12288":1,"2128,2129,2129,2130,2131,2132,2132,2133,6144":3,"1062,1063,1063,1064,1064,1065,1065,1066,3072":2,"2127,2128,2128,2129,2130,2131,2131,2132,6144":2,"4258,4259,4259,4260,4261,4262,4262,4263,12288":2,"8520,8521,8521,8522,8523,8524,8524,8525,24576":1,"4259,4260,4260,4261,4261,4262,4262,4263,12288":1,"8520,8521,8521,8522,8522,8523,8523,8524,24576":1,"17043,17044,17044,17045,17045,17046,17046,17047,49152":1,"486,487,487,488,488,489,489,490,1536":11,"975,976,976,977,977,978,978,979,3072":1,"241,242,242,243,243,244,244,245,768":28,"485,486,486,487,488,489,489,490,1536":10,"974,975,975,976,976,977,977,978,3072":5,"1951,1952,1952,1953,1954,1955,1955,1956,6144":1,"974,975,975,976,977,978,978,979,3072":5,"485,486,486,487,487,488,488,489,1536":9,"973,974,974,975,976,977,977,978,3072":5,"1950,1951,1951,1952,1953,1954,1954,1955,6144":3,"3904,3905,3905,3906,3907,3908,3908,3909,12288":1,"1951,1952,1952,1953,1953,1954,1954,1955,6144":2,"1950,1951,1951,1952,1952,1953,1953,1954,6144":2,"3903,3904,3904,3905,3906,3907,3907,3908,12288":1,"7810,7811,7811,7812,7813,7814,7814,7815,24576":1,"3904,3905,3905,3906,3906,3907,3907,3908,12288":1,"3903,3904,3904,3905,3905,3906,3906,3907,12288":1,"7809,7810,7810,7811,7812,7813,7813,7814,24576":1,"15622,15623,15623,15624,15625,15626,15626,15627,49152":1,"445,446,446,447,447,448,448,449,1536":10,"893,894,894,895,896,897,897,898,3072":2,"24,25,25,26,27,28,28,29,96":74,"52,53,53,54,55,56,56,57,192":66,"108,109,109,110,111,112,112,113,384":47,"220,221,221,222,223,224,224,225,768":24,"444,445,445,446,447,448,448,449,1536":12,"892,893,893,894,895,896,896,897,3072":6,"1788,1789,1789,1790,1791,1792,1792,1793,6144":2,"893,894,894,895,895,896,896,897,3072":5,"1788,1789,1789,1790,1790,1791,1791,1792,6144":3,"3579,3580,3580,3581,3581,3582,3582,3583,12288":1,"892,893,893,894,894,895,895,896,3072":3,"1787,1788,1788,1789,1790,1791,1791,1792,6144":2,"3578,3579,3579,3580,3580,3581,3581,3582,12288":1,"7159,7160,7160,7161,7162,7163,7163,7164,24576":1,"3578,3579,3579,3580,3581,3582,3582,3583,12288":1,"1787,1788,1788,1789,1789,1790,1790,1791,6144":1,"3577,3578,3578,3579,3580,3581,3581,3582,12288":1,"7158,7159,7159,7160,7161,7162,7162,7163,24576":1,"14320,14321,14321,14322,14323,14324,14324,14325,49152":1,"408,409,409,410,410,411,411,412,1536":11,"819,820,820,821,821,822,822,823,3072":1,"202,203,203,204,204,205,205,206,768":30,"407,408,408,409,410,411,411,412,1536":12,"818,819,819,820,820,821,821,822,3072":6,"1639,1640,1640,1641,1642,1643,1643,1644,6144":1,"818,819,819,820,821,822,822,823,3072":5,"407,408,408,409,409,410,410,411,1536":9,"817,818,818,819,820,821,821,822,3072":4,"1638,1639,1639,1640,1641,1642,1642,1643,6144":2,"3280,3281,3281,3282,3283,3284,3284,3285,12288":1,"1639,1640,1640,1641,1641,1642,1642,1643,6144":3,"1638,1639,1639,1640,1640,1641,1641,1642,6144":2,"3279,3280,3280,3281,3282,3283,3283,3284,12288":2,"6562,6563,6563,6564,6565,6566,6566,6567,24576":1,"3280,3281,3281,3282,3282,3283,3283,3284,12288":1,"6562,6563,6563,6564,6564,6565,6565,6566,24576":1,"13127,13128,13128,13129,13129,13130,13130,13131,49152":1,"185,186,186,187,187,188,188,189,384":34,"373,374,374,375,376,377,377,378,768":11,"750,751,751,752,753,754,754,755,1536":2,"373,374,374,375,375,376,376,377,768":13,"749,750,750,751,752,753,753,754,1536":5,"1502,1503,1503,1504,1505,1506,1506,1507,3072":2,"750,751,751,752,752,753,753,754,1536":6,"1502,1503,1503,1504,1504,1505,1505,1506,3072":3,"3007,3008,3008,3009,3009,3010,3010,3011,6144":1,"749,750,750,751,751,752,752,753,1536":3,"1501,1502,1502,1503,1504,1505,1505,1506,3072":3,"3006,3007,3007,3008,3008,3009,3009,3010,6144":2,"6015,6016,6016,6017,6018,6019,6019,6020,12288":1,"3006,3007,3007,3008,3009,3010,3010,3011,6144":1,"6015,6016,6016,6017,6017,6018,6018,6019,12288":1,"12033,12034,12034,12035,12035,12036,12036,12037,24576":1,"342,343,343,344,344,345,345,346,768":14,"687,688,688,689,690,691,691,692,1536":6,"687,688,688,689,689,690,690,691,1536":5,"1377,1378,1378,1379,1379,1380,1380,1381,3072":3,"169,170,170,171,171,172,172,173,384":22,"341,342,342,343,344,345,345,346,768":10,"686,687,687,688,689,690,690,691,1536":5,"1376,1377,1377,1378,1379,1380,1380,1381,3072":3,"2756,2757,2757,2758,2758,2759,2759,2760,6144":2,"1376,1377,1377,1378,1378,1379,1379,1380,3072":2,"2755,2756,2756,2757,2758,2759,2759,2760,6144":1,"5514,5515,5515,5516,5516,5517,5517,5518,12288":1,"2755,2756,2756,2757,2757,2758,2758,2759,6144":1,"5513,5514,5514,5515,5516,5517,5517,5518,12288":1,"11030,11031,11031,11032,11032,11033,11033,11034,24576":1,"313,314,314,315,315,316,316,317,768":15,"629,630,630,631,632,633,633,634,1536":5,"1262,1263,1263,1264,1265,1266,1266,1267,3072":1,"630,631,631,632,632,633,633,634,1536":5,"629,630,630,631,631,632,632,633,1536":5,"1261,1262,1262,1263,1264,1265,1265,1266,3072":3,"2526,2527,2527,2528,2529,2530,2530,2531,6144":1,"1262,1263,1263,1264,1264,1265,1265,1266,3072":2,"1261,1262,1262,1263,1263,1264,1264,1265,3072":2,"2525,2526,2526,2527,2528,2529,2529,2530,6144":1,"5054,5055,5055,5056,5057,5058,5058,5059,12288":1,"2526,2527,2527,2528,2528,2529,2529,2530,6144":1,"2525,2526,2526,2527,2527,2528,2528,2529,6144":1,"5053,5054,5054,5055,5056,5057,5057,5058,12288":1,"10110,10111,10111,10112,10113,10114,10114,10115,24576":1,"287,288,288,289,289,290,290,291,768":14,"577,578,578,579,580,581,581,582,1536":4,"577,578,578,579,579,580,580,581,1536":5,"1157,1158,1158,1159,1159,1160,1160,1161,3072":1,"69,70,70,71,71,72,72,73,192":41,"141,142,142,143,144,145,145,146,384":26,"286,287,287,288,289,290,290,291,768":12,"576,577,577,578,579,580,580,581,1536":6,"1156,1157,1157,1158,1158,1159,1159,1160,3072":3,"2315,2316,2316,2317,2318,2319,2319,2320,6144":1,"1156,1157,1157,1158,1159,1160,1160,1161,3072":3,"2315,2316,2316,2317,2317,2318,2318,2319,6144":2,"4633,4634,4634,4635,4635,4636,4636,4637,12288":1,"576,577,577,578,578,579,579,580,1536":2,"1155,1156,1156,1157,1158,1159,1159,1160,3072":1,"2314,2315,2315,2316,2317,2318,2318,2319,6144":1,"4632,4633,4633,4634,4634,4635,4635,4636,12288":1,"9267,9268,9268,9269,9270,9271,9271,9272,24576":1,"63,64,64,65,65,66,66,67,192":44,"129,130,130,131,132,133,133,134,384":30,"262,263,263,264,265,266,266,267,768":15,"528,529,529,530,531,532,532,533,1536":6,"1060,1061,1061,1062,1063,1064,1064,1065,3072":1,"529,530,530,531,531,532,532,533,1536":5,"528,529,529,530,530,531,531,532,1536":4,"1059,1060,1060,1061,1062,1063,1063,1064,3072":2,"2122,2123,2123,2124,2125,2126,2126,2127,6144":1,"1060,1061,1061,1062,1062,1063,1063,1064,3072":3,"1059,1060,1060,1061,1061,1062,1062,1063,3072":2,"2121,2122,2122,2123,2124,2125,2125,2126,6144":2,"4246,4247,4247,4248,4249,4250,4250,4251,12288":1,"2122,2123,2123,2124,2124,2125,2125,2126,6144":1,"4246,4247,4247,4248,4248,4249,4249,4250,12288":1,"8495,8496,8496,8497,8497,8498,8498,8499,24576":1,"27,28,28,29,29,30,30,31,96":56,"57,58,58,59,60,61,61,62,192":48,"118,119,119,120,121,122,122,123,384":32,"240,241,241,242,243,244,244,245,768":16,"484,485,485,486,487,488,488,489,1536":5,"972,973,973,974,974,975,975,976,3072":1,"484,485,485,486,486,487,487,488,1536":5,"971,972,972,973,973,974,974,975,3072":2,"1945,1946,1946,1947,1948,1949,1949,1950,6144":1,"971,972,972,973,974,975,975,976,3072":3,"240,241,241,242,242,243,243,244,768":10,"483,484,484,485,486,487,487,488,1536":4,"970,971,971,972,973,974,974,975,3072":2,"1944,1945,1945,1946,1947,1948,1948,1949,6144":2,"3892,3893,3893,3894,3895,3896,3896,3897,12288":1,"1945,1946,1946,1947,1947,1948,1948,1949,6144":1,"3892,3893,3893,3894,3894,3895,3895,3896,12288":1,"7787,7788,7788,7789,7789,7790,7790,7791,24576":1,"220,221,221,222,222,223,223,224,768":15,"443,444,444,445,446,447,447,448,1536":6,"890,891,891,892,893,894,894,895,3072":3,"444,445,445,446,446,447,447,448,1536":5,"890,891,891,892,892,893,893,894,3072":3,"1783,1784,1784,1785,1785,1786,1786,1787,6144":2,"443,444,444,445,445,446,446,447,1536":4,"889,890,890,891,892,893,893,894,3072":2,"1782,1783,1783,1784,1785,1786,1786,1787,6144":1,"3568,3569,3569,3570,3570,3571,3571,3572,12288":1,"1782,1783,1783,1784,1784,1785,1785,1786,6144":1,"3567,3568,3568,3569,3570,3571,3571,3572,12288":1,"7138,7139,7139,7140,7140,7141,7141,7142,24576":1,"99,100,100,101,101,102,102,103,384":31,"201,202,202,203,204,205,205,206,768":17,"406,407,407,408,409,410,410,411,1536":6,"816,817,817,818,819,820,820,821,3072":1,"406,407,407,408,408,409,409,410,1536":6,"815,816,816,817,818,819,819,820,3072":2,"1634,1635,1635,1636,1637,1638,1638,1639,6144":1,"816,817,817,818,818,819,819,820,3072":3,"815,816,816,817,817,818,818,819,3072":2,"1633,1634,1634,1635,1636,1637,1637,1638,6144":2,"3270,3271,3271,3272,3273,3274,3274,3275,12288":1,"1634,1635,1635,1636,1636,1637,1637,1638,6144":1,"3270,3271,3271,3272,3272,3273,3273,3274,12288":1,"6543,6544,6544,6545,6545,6546,6546,6547,24576":1,"43,44,44,45,46,47,47,48,96":42,"90,91,91,92,93,94,94,95,192":33,"184,185,185,186,187,188,188,189,384":18,"372,373,373,374,375,376,376,377,768":6,"748,749,749,750,750,751,751,752,1536":3,"372,373,373,374,374,375,375,376,768":7,"747,748,748,749,750,751,751,752,1536":2,"1498,1499,1499,1500,1500,1501,1501,1502,3072":1,"747,748,748,749,749,750,750,751,1536":3,"1497,1498,1498,1499,1500,1501,1501,1502,3072":2,"2998,2999,2999,3000,3000,3001,3001,3002,6144":1,"1497,1498,1498,1499,1499,1500,1500,1501,3072":1,"2997,2998,2998,2999,2999,3000,3000,3001,6144":1,"5997,5998,5998,5999,6000,6001,6001,6002,12288":1,"341,342,342,343,343,344,344,345,768":6,"685,686,686,687,688,689,689,690,1536":3,"685,686,686,687,687,688,688,689,1536":2,"1373,1374,1374,1375,1375,1376,1376,1377,3072":1,"39,40,40,41,42,43,43,44,96":27,"82,83,83,84,85,86,86,87,192":20,"168,169,169,170,171,172,172,173,384":13,"340,341,341,342,343,344,344,345,768":6,"684,685,685,686,687,688,688,689,1536":3,"1372,1373,1373,1374,1375,1376,1376,1377,3072":2,"2748,2749,2749,2750,2750,2751,2751,2752,6144":1,"1372,1373,1373,1374,1374,1375,1375,1376,3072":1,"2747,2748,2748,2749,2749,2750,2750,2751,6144":1,"5497,5498,5498,5499,5500,5501,5501,5502,12288":1,"36,37,37,38,38,39,39,40,96":38,"75,76,76,77,78,79,79,80,192":30,"154,155,155,156,157,158,158,159,384":18,"312,313,313,314,315,316,316,317,768":7,"628,629,629,630,631,632,632,633,1536":1,"312,313,313,314,314,315,315,316,768":7,"627,628,628,629,630,631,631,632,1536":2,"1258,1259,1259,1260,1261,1262,1262,1263,3072":1,"628,629,629,630,630,631,631,632,1536":3,"627,628,628,629,629,630,630,631,1536":2,"1257,1258,1258,1259,1260,1261,1261,1262,3072":2,"2518,2519,2519,2520,2521,2522,2522,2523,6144":1,"1258,1259,1259,1260,1260,1261,1261,1262,3072":1,"2518,2519,2519,2520,2520,2521,2521,2522,6144":1,"5039,5040,5040,5041,5041,5042,5042,5043,12288":1,"286,287,287,288,288,289,289,290,768":8,"575,576,576,577,577,578,578,579,1536":2,"1153,1154,1154,1155,1156,1157,1157,1158,3072":1,"575,576,576,577,578,579,579,580,1536":3,"141,142,142,143,143,144,144,145,384":12,"285,286,286,287,288,289,289,290,768":4,"574,575,575,576,577,578,578,579,1536":2,"1152,1153,1153,1154,1155,1156,1156,1157,3072":2,"2308,2309,2309,2310,2311,2312,2312,2313,6144":1,"1153,1154,1154,1155,1155,1156,1156,1157,3072":1,"2308,2309,2309,2310,2310,2311,2311,2312,6144":1,"4619,4620,4620,4621,4621,4622,4622,4623,12288":1,"262,263,263,264,264,265,265,266,768":9,"527,528,528,529,530,531,531,532,1536":3,"527,528,528,529,529,530,530,531,1536":3,"1057,1058,1058,1059,1059,1060,1060,1061,3072":2,"129,130,130,131,131,132,132,133,384":11,"261,262,262,263,264,265,265,266,768":5,"526,527,527,528,529,530,530,531,1536":2,"1056,1057,1057,1058,1059,1060,1060,1061,3072":1,"2116,2117,2117,2118,2118,2119,2119,2120,6144":1,"1056,1057,1057,1058,1058,1059,1059,1060,3072":1,"2115,2116,2116,2117,2118,2119,2119,2120,6144":1,"4234,4235,4235,4236,4236,4237,4237,4238,12288":1,"483,484,484,485,485,486,486,487,1536":3,"969,970,970,971,971,972,972,973,3072":1,"118,119,119,120,120,121,121,122,384":13,"239,240,240,241,242,243,243,244,768":6,"482,483,483,484,485,486,486,487,1536":3,"968,969,969,970,970,971,971,972,3072":2,"1939,1940,1940,1941,1942,1943,1943,1944,6144":1,"968,969,969,970,971,972,972,973,3072":1,"1939,1940,1940,1941,1941,1942,1942,1943,6144":1,"3881,3882,3882,3883,3883,3884,3884,3885,12288":1,"108,109,109,110,110,111,111,112,384":16,"219,220,220,221,222,223,223,224,768":8,"442,443,443,444,445,446,446,447,1536":3,"888,889,889,890,890,891,891,892,3072":1,"442,443,443,444,444,445,445,446,1536":3,"887,888,888,889,889,890,890,891,3072":2,"1777,1778,1778,1779,1780,1781,1781,1782,6144":1,"887,888,888,889,890,891,891,892,3072":1,"1777,1778,1778,1779,1779,1780,1780,1781,6144":1,"3557,3558,3558,3559,3559,3560,3560,3561,12288":1,"201,202,202,203,203,204,204,205,768":9,"405,406,406,407,408,409,409,410,1536":3,"814,815,815,816,816,817,817,818,3072":1,"405,406,406,407,407,408,408,409,1536":3,"813,814,814,815,815,816,816,817,3072":1,"1629,1630,1630,1631,1632,1633,1633,1634,6144":1,"813,814,814,815,816,817,817,818,3072":1,"47,48,48,49,50,51,51,52,192":13,"98,99,99,100,101,102,102,103,384":8,"200,201,201,202,203,204,204,205,768":4,"404,405,405,406,407,408,408,409,1536":2,"812,813,813,814,815,816,816,817,3072":1,"1628,1629,1629,1630,1631,1632,1632,1633,6144":1,"3260,3261,3261,3262,3263,3264,3264,3265,12288":1,"184,185,185,186,186,187,187,188,384":9,"371,372,372,373,374,375,375,376,768":3,"746,747,747,748,748,749,749,750,1536":1,"371,372,372,373,373,374,374,375,768":3,"745,746,746,747,747,748,748,749,1536":1,"1493,1494,1494,1495,1496,1497,1497,1498,3072":1,"745,746,746,747,748,749,749,750,1536":1,"90,91,91,92,92,93,93,94,192":8,"183,184,184,185,186,187,187,188,384":4,"370,371,371,372,373,374,374,375,768":2,"744,745,745,746,747,748,748,749,1536":1,"1492,1493,1493,1494,1495,1496,1496,1497,3072":1,"2988,2989,2989,2990,2991,2992,2992,2993,6144":1,"340,341,341,342,342,343,343,344,768":4,"683,684,684,685,686,687,687,688,1536":1,"683,684,684,685,685,686,686,687,1536":2,"1369,1370,1370,1371,1371,1372,1372,1373,3072":1,"168,169,169,170,170,171,171,172,384":5,"339,340,340,341,342,343,343,344,768":2,"682,683,683,684,685,686,686,687,1536":1,"1368,1369,1369,1370,1370,1371,1371,1372,3072":1,"2739,2740,2740,2741,2742,2743,2743,2744,6144":1,"154,155,155,156,156,157,157,158,384":9,"311,312,312,313,314,315,315,316,768":3,"626,627,627,628,629,630,630,631,1536":1,"311,312,312,313,313,314,314,315,768":3,"625,626,626,627,628,629,629,630,1536":2,"1254,1255,1255,1256,1257,1258,1258,1259,3072":1,"626,627,627,628,628,629,629,630,1536":1,"1254,1255,1255,1256,1256,1257,1257,1258,3072":1,"2511,2512,2512,2513,2513,2514,2514,2515,6144":1,"574,575,575,576,576,577,577,578,1536":1,"285,286,286,287,287,288,288,289,768":5,"573,574,574,575,576,577,577,578,1536":2,"1150,1151,1151,1152,1152,1153,1153,1154,3072":1,"573,574,574,575,575,576,576,577,1536":1,"1149,1150,1150,1151,1151,1152,1152,1153,3072":1,"2301,2302,2302,2303,2304,2305,2305,2306,6144":1,"526,527,527,528,528,529,529,530,1536":1,"261,262,262,263,263,264,264,265,768":4,"525,526,526,527,528,529,529,530,1536":2,"1054,1055,1055,1056,1056,1057,1057,1058,3072":1,"525,526,526,527,527,528,528,529,1536":1,"1053,1054,1054,1055,1055,1056,1056,1057,3072":1,"2109,2110,2110,2111,2112,2113,2113,2114,6144":1,"482,483,483,484,484,485,485,486,1536":1,"239,240,240,241,241,242,242,243,768":4,"481,482,482,483,484,485,485,486,1536":2,"966,967,967,968,968,969,969,970,3072":1,"481,482,482,483,483,484,484,485,1536":1,"965,966,966,967,967,968,968,969,3072":1,"1933,1934,1934,1935,1936,1937,1937,1938,6144":1,"219,220,220,221,221,222,222,223,768":5,"441,442,442,443,444,445,445,446,1536":2,"441,442,442,443,443,444,444,445,1536":1,"885,886,886,887,887,888,888,889,3072":1,"52,53,53,54,54,55,55,56,192":8,"107,108,108,109,110,111,111,112,384":4,"218,219,219,220,221,222,222,223,768":3,"440,441,441,442,443,444,444,445,1536":1,"884,885,885,886,887,888,888,889,3072":1,"1772,1773,1773,1774,1774,1775,1775,1776,6144":1,"404,405,405,406,406,407,407,408,1536":1,"811,812,812,813,814,815,815,816,3072":1,"200,201,201,202,202,203,203,204,768":3,"403,404,404,405,406,407,407,408,1536":2,"810,811,811,812,813,814,814,815,3072":1,"1624,1625,1625,1626,1627,1628,1628,1629,6144":1,"370,371,371,372,372,373,373,374,768":1,"743,744,744,745,746,747,747,748,1536":1,"183,184,184,185,185,186,186,187,384":4,"369,370,370,371,372,373,373,374,768":2,"742,743,743,744,745,746,746,747,1536":1,"1488,1489,1489,1490,1491,1492,1492,1493,3072":1,"339,340,340,341,341,342,342,343,768":1,"681,682,682,683,684,685,685,686,1536":1,"82,83,83,84,84,85,85,86,192":6,"167,168,168,169,170,171,171,172,384":3,"338,339,339,340,341,342,342,343,768":2,"680,681,681,682,683,684,684,685,1536":1,"1364,1365,1365,1366,1367,1368,1368,1369,3072":1,"75,76,76,77,77,78,78,79,192":7,"153,154,154,155,156,157,157,158,384":4,"310,311,311,312,313,314,314,315,768":1,"624,625,625,626,627,628,628,629,1536":1,"310,311,311,312,312,313,313,314,768":2,"623,624,624,625,626,627,627,628,1536":1,"1250,1251,1251,1252,1253,1254,1254,1255,3072":1,"32,33,33,34,35,36,36,37,96":8,"68,69,69,70,71,72,72,73,192":8,"140,141,141,142,143,144,144,145,384":4,"284,285,285,286,287,288,288,289,768":1,"572,573,573,574,574,575,575,576,1536":1,"284,285,285,286,286,287,287,288,768":2,"571,572,572,573,574,575,575,576,1536":1,"1146,1147,1147,1148,1148,1149,1149,1150,3072":1,"29,30,30,31,32,33,33,34,96":8,"62,63,63,64,65,66,66,67,192":8,"128,129,129,130,131,132,132,133,384":4,"260,261,261,262,263,264,264,265,768":2,"524,525,525,526,527,528,528,529,1536":1,"260,261,261,262,262,263,263,264,768":1,"523,524,524,525,526,527,527,528,1536":1,"1050,1051,1051,1052,1053,1054,1054,1055,3072":1,"57,58,58,59,59,60,60,61,192":7,"117,118,118,119,120,121,121,122,384":3,"238,239,239,240,241,242,242,243,768":2,"480,481,481,482,483,484,484,485,1536":1,"238,239,239,240,240,241,241,242,768":1,"479,480,480,481,482,483,483,484,1536":1,"962,963,963,964,965,966,966,967,3072":1,"440,441,441,442,442,443,443,444,1536":1,"218,219,219,220,220,221,221,222,768":1,"439,440,440,441,442,443,443,444,1536":1,"882,883,883,884,884,885,885,886,3072":1,"98,99,99,100,100,101,101,102,384":4,"199,200,200,201,202,203,203,204,768":2,"402,403,403,404,405,406,406,407,1536":1,"808,809,809,810,811,812,812,813,3072":1,"369,370,370,371,371,372,372,373,768":1,"741,742,742,743,743,744,744,745,1536":1,"338,339,339,340,340,341,341,342,768":1,"679,680,680,681,681,682,682,683,1536":1,"153,154,154,155,155,156,156,157,384":2,"309,310,310,311,312,313,313,314,768":1,"622,623,623,624,624,625,625,626,1536":1,"140,141,141,142,142,143,143,144,384":3,"283,284,284,285,286,287,287,288,768":1,"570,571,571,572,572,573,573,574,1536":1,"128,129,129,130,130,131,131,132,384":3,"259,260,260,261,262,263,263,264,768":1,"522,523,523,524,525,526,526,527,1536":1,"117,118,118,119,119,120,120,121,384":3,"237,238,238,239,240,241,241,242,768":2,"478,479,479,480,481,482,482,483,1536":1,"107,108,108,109,109,110,110,111,384":3,"217,218,218,219,220,221,221,222,768":2,"438,439,439,440,441,442,442,443,1536":1,"402,403,403,404,404,405,405,406,1536":1,"43,44,44,45,45,46,46,47,96":3,"89,90,90,91,92,93,93,94,192":3,"182,183,183,184,185,186,186,187,384":2,"368,369,369,370,370,371,371,372,768":1,"167,168,168,169,169,170,170,171,384":2,"337,338,338,339,340,341,341,342,768":1,"309,310,310,311,311,312,312,313,768":1,"283,284,284,285,285,286,286,287,768":1,"259,260,260,261,261,262,262,263,768":1,"199,200,200,201,201,202,202,203,768":1,"35,36,36,37,38,39,39,40,96":1,"74,75,75,76,77,78,78,79,192":1,"152,153,153,154,155,156,156,157,384":1},"product_ntt":{"23,26":2297,"24,25":682},"monic":{"3":1,"2":1},"edf_draw":{"":1},"edf_powmod":{"2":1},"edf_constsub":{"2":1},"root_linear":{"":2}}
```
