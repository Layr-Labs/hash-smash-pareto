# Orchard r=1: centre differencing on the two-round line, value-domain Montgomery powering, counted executed run

## 1. Target

Profile `poseidon-orchard-r1-prefix-v1`: Orchard P128Pow5T3 over the Pallas field
F_p, p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001 (255 bits),
width 3, S-box x -> x^5, deployed round constants rc[i] (i = 0..63) and the deployed 3x3
MDS matrix M, both pinned in `orchard-pallas-constants.json`. The reduced permutation
applies the original full rounds 0, 1, 2, 3, the original partial rounds 4..4
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
C(1) = 216 + 21*1 = 237 units per reduced permutation.
Normalized time T = W / C(1), `time_log2` = log2 T. Memory in bytes, including code.

Notation. x^5 is a bijection of F_p because gcd(5, p-1) = 1; its inverse is x -> x^e5 with
e5 = 5^-1 mod (p-1), so "the fifth root" is a single well-defined field element. We write
H(nk, rho) for the reduced hash. p-1 = 2^32 * 3 * 463 * (two large primes), so F_p contains
primitive roots of unity of every order 3 * 2^k with k <= 32; all transforms below are cyclic
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
affine function of T' by Lemma 1. Applying rounds 2, 3 (full), 4..4 (partial) and 60..63
(full) to s(T') and taking lane 0 defines a polynomial F in F_p[T'] of degree exactly
D = 5^(6+1) = 78,125, with leading coefficient a_D, and H(nk(T), rho(T)) = F(T^5) for every T.

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
m = (D - 1)/2 = 39,062. The leading coefficient of G_c is h_D = a_D (D is odd), independent of c.
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

All arithmetic is over F_p. D = 78,125, m = 39,062, n = 49,152 (the least 3*2^k > m), omega a
primitive n-th root of unity, psi a primitive 2n-th root with psi^2 = omega (so psi^n = -1),
O1 = {omega^i} and O2 = {psi omega^i}. The procedure is deterministic and reads no random coins.
It runs trials i = 1, 2, 3, ... with centre c_i = i, stopping at the first trial that yields a
collision, with a finite cap of 64 trials (exit without output if reached; not reached). Every
trial that runs is charged in full. It was executed from trial 1 on the fixed target (Section 7 lists every execution); it
stopped at trial 1 (trial 1 (c = 1): deg G = 1).

Step 1 (values of g_c on O1). Transform order: `ntt_forward` (4.1) returns the values of its
input at the points omega^e(t) at output position t, where t = 3B + s', s' in {0, 1, 2}, and
e(t) = rev_k(B) + 2^k s' (rev_k reverses the k bits of the block index B); Appendix A asserts this
against the transform of X at every length 3..768. For t = 0..n-1 put s_t = psi^e(t), so
s_t^2 = omega^e(t), and compute
  G1[t] = (F(c + s_t) - F(c - s_t)) * (2 a_D s_t)^-1 = g_c(omega^e(t))
by two line evaluations (start from the affine state of Lemma 1 and apply the 6 + 1 remaining
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
Start (Montgomery form of X^(2^j)): with a = 2^j = 8,192, L = n + a - m + 1 = 18,283, the quotient
of X^(n+a) by g_c is quot = rev_{L-1}(rev(g_c)^-1 mod X^L) (Newton iteration, 4.3); since
quot g_c = X^(n+a) - r with deg r < m, the cyclic product c = quot g_c mod (X^n - 1) satisfies
c_i = -r_i + [i = a] for i < m and c_i = 0 for m <= i < n (because a < m < n), so
-c = r - X^a = X^a (X^n - 1) mod g_c = X^a R mod g_c, the Montgomery form of X^a, of degree < m.
j = 13 is the largest power with a < m and L at most n/2 (so the Newton buffers fit in one
n-word buffer). The exponent (p-1)/2 has its top bit at position 253 followed by 128 zero bits,
so after X^a the remaining 240 bits each cost one Montgomery squaring, 45 of them with the
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
T_strict(49,152) = 2,756,638 (loose rule: n (35k/12 + 29/6) = 2,244,608). The transform constants (at most 20 lengths,
22 constants each, 380 units each, plus an address operation for each of their at most 440 stores) are
charged once in the setup. The closed forms are asserted equal to the instrumented kernels (Appendix A) at
every length 3..3072 in both conventions, and the convolution is checked against schoolbook multiplication.

4.2 Build (Step 1), per trial: 2n line evaluations; one evaluation is 6 + 27*6 + 21*1 = 189 field
operations (affine state after round 1: 3 multiplications and 3 additions; six full rounds at 27: three
constant additions, three x^5 at 3 multiplications, the MDS at 9 multiplications and 6 additions; 1 partial round at
21) and 6 + 12 (6 + 1) = 90 constant loads (6 affine coefficients, then 3 round constants and the 9
MDS entries per round; the three-lane state stays in registers): 369 units strict. Per position:
c + s_t and c - s_t (2), the difference and the product with the factor (2), one store; the loop over
positions is not unrolled (3 per iteration, 2 on exit). Point generator (`point_stream`, closed form `PG`):
a stack of k + 1 prefix products over the bits of the block index (k + 1 initial stores); per block one loop
iteration with the trailing-zero count and branch (5 ctl), recomputation of one prefix (two loads, one
multiplication, one store), straight-line stores of the prefixes below the changed bit (over all blocks
n/3 - k - 1 stores), two multiplications for the cube-root companions of the block's point; 2 on exit. Build
charge per trial: 37,240,824 units (loose 28,213,246). Peak: the n words of G1.

4.3 Montgomery stage (Step 2), closed forms of `mont.py` (functions TV, TW, PASS, STEP, SINV, BINV, SETUP_POWER),
each asserted equal to the instrumented execution in the run itself (the ledger records the per-phase marks
in both conventions) and in the self-test against FLINT at m = 20..370. A streaming pass over e elements
with a field operations, l loads and s stores per element costs e (a + 2 l + 2 s) + LP(e):
  - interpolation of g_c: scaled copy of G1 (1 load, 1 multiplication, 1 store per word) and one inverse
    transform: 3,020,832;
  - start residue: Newton inverse of rev(g_c) to precision L at steps m -> m2 = min(2m, L), length N = least
    3*2^i >= m2, d = m2 - m: copy-and-pad of rev(g_c) (min(m2, m+1) loads, N stores) and of the current
    inverse (m loads, N stores), 5 transforms, two pointwise products (2 loads, 2 multiplications, 1 store per
    point), copy of d words, zero padding of N - d words, and the update (load, subtraction, store per word);
    then the reversed copy into the n-word buffer with padding, a forward transform, the pointwise product with
    G1 and the factor -1/n, an inverse transform and the zeroing of positions m..n-1: 26,677,717;
  - batch inversion of G1 into Ginv1 = -1/(n G1) (Montgomery's trick; prefix products in a scratch buffer;
    one inversion; the factor -1/n folded into the inverted product): 676,219;
  - tables: start values on O2 (copy with twist and a forward transform), on O1 (one forward transform in
    place), G2h (twist with c0 = -1/2 and a forward transform): 8,896,606;
  - powering: per squaring 4 transforms, the twist and the untwist (1 load, 2 multiplications, 1 store per
    word), the pass U1 = A1^2 Ginv1 (2 loads, 2 multiplications, 1 store), the pass B2 = A2^2 h + U2 G2h (3 loads,
    3 multiplications, 1 addition, 2 stores into A2 and the work buffer): 12,771,456 (loose 10,158,080); with the
    multiplication by X add one multiplication per point and one point generator: 13,082,747; 240 squarings,
    45 of them with X: 3,079,157,535;
  - finish: half-step (U1 pass, inverse, twist, forward, B2 pass), interpolation on O2 (inverse, untwist) and the
    recovery of g_c (inverse, untwist): 12,888,194.
  Stage total per trial: 3,131,317,103 units strict (loose 2,490,483,790). Buffers: A1, A2, Ginv1, G2h of n words each
  (4n); during the Newton step G1, g_c, the two Newton buffers (2 N <= n) and the growing inverse (<= L words):
  at most 2n + max(2N + m2). Peak of the stage: 196,608 words.

4.4 Setup, once: the constants of Lemma 1 (two inversions, fifth powers, products and sums) as a flat 4,000
units (twice the 2,000 of our earlier entries), the transform constants (167,200 + 440), the
leading-coefficient recursion of Lemma 2 with the inversion of 2 a_D (bounded by 24 (8 + r) + 381 = 597),
the Tonelli-Shanks constant 5^t (267), and a bound of 20,000 for writing the output (two pairs, the digest):
192,504 units. Per trial: the centre (1 unit) and forming Y - 1 (load, subtraction, store: 5 units).

4.5 Finish (Step 4), per root S, all in registers: the zero test (1), Tonelli-Shanks as executed (the
exponentiation S^((t-1)/2), 2 multiplications, then per loop iteration of the classical algorithm: squarings
5 units each including compare and counter, the repeated squaring of the running non-residue power 4 units
each, three multiplications and 3 units of loop control), W1 and W2 (2), the inputs of both sides
(2 (3 * 377 + 8)), two reduced hashes (2 * 237) and the comparison (8): 4,825 units on this run. The finish is
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
  on both factors. On this instance deg G = 1, so the splitting branch was not executed.
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

5.3 Executed count. On this instance (trial 1, deg g_c = 39,062) the stage performed
77,520 classical and 203 transform products, 39,061 classical and 0 Newton divisions in the half-gcd (top-level reduction n0/12 per call, base case below 48) and charged 523,934,321.5 units under the loose rules with a peak of 206,377 live words; the
charge of the root stage was 1 (together 523,934,322.5), and the explicit overhead added
9,156,543. Strict re-pricing of the whole stage (5.2s, overhead included): 715,882,165 units. The remainder sequence was normal: every division in the histogram is of degree n by n - 1 and every wrapped step has deg a - deg b = 1. 1,151 products had a zero operand and were charged 0. Charge by kind (each row recomputed by `halfgcd_charge.py`
from the histogram of Appendix B):

| kind | strict units | loose units |
|---|---:|---:|
| matvec_wrap | 445,709,418 | 349,804,165.5 |
| matmul_shared | 129,275,295 | 100,554,192 |
| division_classical | 73,599,362 | 46,395,246.5 |
| product_classical | 38,040,770 | 19,316,258.5 |
| addsub | 12,224,470 | 7,298,721 |
| product_ntt | 765,310 | 565,355 |
| monic | 395 | 383 |
| root_linear | 3 | 1 |
| total (before overhead) | 699,615,023 | 523,934,322.5 |

Appendix B reproduces `gcd_trace_r1_t1.json`, the
histogram of every charged operation by kind and size; `halfgcd_charge.py` (Appendix A,
standard library only) recomputes the charge from that histogram and the rules above.


## 6. Totals

Strict convention of 4.0 (the claim), with the loose rule of our earlier entries beside it for comparison:

| phase | strict units (claim) | loose units | peak live words |
|---|---:|---:|---:|
| setup (4.4) | 192,504 | 180,064 | |
| trial 1: centre c = 1 and Y - 1 (4.4) | 6 | 3 | |
| trial 1: build, values of g_c on O1 (4.2) | 37,240,824 | 28,213,246 | 49,216 |
| trial 1: interpolation of g_c (4.3) | 3,020,832 | 2,416,640 | |
| trial 1: start residue (Newton, cyclic product) (4.3) | 26,677,717 | 21,218,095.5 | |
| trial 1: batch inversion Ginv1 (4.3) | 676,219 | 442,744.5 | |
| trial 1: start values on O1, O2; G2h (4.3) | 8,896,606 | 7,176,192 | |
| trial 1: 240 Montgomery squarings (45 with X) (4.3) | 3,079,157,535 | 2,448,998,310 | 196,608 |
| trial 1: final conversion, interpolation, recovery of g_c (4.3) | 12,888,194 | 10,231,808 | |
| trial 1: half-gcd, roots and overhead (5.2, 5.2s) | 715,882,165 | 533,090,866 | 206,377 |
| trial 1: finish (4.5) | 4,825 | 4,825 | |
| **total** | **3,884,637,427** | **3,051,972,794** | **206,377** |

Total W = 3,884,637,427 units; T = W / 237 = 16,390,875.22; `time_log2` = log2 T = 23.966390, submitted as
23.96639 (ceiling at five decimals; never a downward rounding). Under the loose rule the same run is
3,051,972,794 units, `time_log2` 23.618352; the strict figure is the larger and is the one claimed.
Trials executed: trial 1 (c = 1): deg G = 1. `accounting.py` (Appendix A, standard library only) recomputes every row of
this table in both conventions from the sizes, the closed forms, the gcd histograms of Appendix B and the
recorded roots, and recomputes the pair(s) with a pure-Python permutation.

## 7. Success probability and the trial budget

The procedure reads no random coins; its only inputs are the pinned constants and the fixed centre order
c_i = i. Executed on this fixed target it performed exactly the operations charged above and returned the
certified pair at trial 1; a deterministic procedure that returns a pair on its only control path
has success probability 1 on this target. Every trial that ran is charged, including trials whose G had
degree 0. No expectation, extrapolation or heuristic enters the claim (`heuristics` is empty). The centre
order was fixed before the first execution and the run was made from trial 1; no centre was skipped or
selected. An earlier execution of the procedure used the top-level reduction n0/4 in the half-gcd (same centres,
same g_c, Y, G and pair; strict 26.91184, gcd peak 225,907 words). The top-level reduction n0/12 was chosen
by a sweep on an independent instance of the same degree (a pseudo-random monic polynomial of degree 39,062, not a
line polynomial; `gcd_sweep_indep.py` in Appendix A, its log in Appendix B); every fraction returns the same G on
the target, so the choice does not depend on the target. The kernels were also executed on the unadmitted r = 0
instance during development.

Context only, not used by the claim: under the usual random-polynomial model the number of roots of g_c
that are nonzero squares is close to Poisson(1/2), so a centre succeeds with probability about
1 - e^(-1/2) = 0.39. Sensitivity: the half-gcd stage is 18.4% of W; tripling it would raise
`time_log2` to 24.4191.

## 8. Certificate

`certificates/message-a.bin` and `certificates/message-b.bin` encode the inputs of W1 = c + s and
W2 = c - s (nk then rho, 32 little-endian bytes each). The expected digest in
`certificates/manifest.json` is the common reduced hash c6891e5992ad847ab001d1bbc1f1d1c63d577831ee73eaf7a317420c0b74da06. Both inputs are canonical and the files
differ. The organizer checker recomputes the reduced permutation on each file; that check is independent of
every count above. A reader can also check from the certificate alone that both pairs lie on the line of
Lemma 1 with W1 + W2 = 2c.

## 9. Memory

Peak live storage is the maximum over the phases of the run: build 49,216 words, Montgomery stage
196,608 words, gcd stage 206,377 words (the half-gcd memory model of 5.2, executed on this
instance), so 206,377 words of 32 bytes, plus a fixed 2^20-byte allowance for code, constants, the
16-word register file of 4.0 and the stack (the kernels are a few thousand machine instructions; the
transform constants are at most 20 * 22 words; the pinned permutation constants at most 201 words; the prefix
stacks of the point generators 2 (k + 1) words; the recursion stack at most 20 frames of a few dozen words).
Total 7,652,640 bytes; log2 = 22.867526, submitted as `memory_log2_bytes` = 22.86753 (ceiling at five
decimals). The normalized cost axis with the submitted bounds is `time_log2` + max(0, `memory_log2_bytes` - 20)
= 26.83392; the claim keeps the two raw bounds separate.

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
control per streamed element) prices the same run at `time_log2` 23.618352, normalized 26.48588.

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
`python accounting.py orchard-pallas-constants.json ledger_r1.json <dir>` with the gcd traces of Appendix B in
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
    (167,200 plus, strict, an address operation for each of their at most 440 stores), the leading-coefficient
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
from ntt import T, nice_length   # T(N) = N*(35k/12 + 29/6), N = 3*2^k only (proof 4.1)

LEAN = True            # views + wrapped matvec + top-level input freeing
SHARED_MATMUL = True   # shared-transform 2x2 matrix product inside hgcd (LEAN only)

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
    N = ntt_len(n_h + 1)
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
    N = ntt_len(mx)
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
        while not F['b'].is_zero() and F['b'].degree() > CUTOFF:
            n0 = F['a'].degree(); d = (n0 + TOP_FRACTION - 1) // TOP_FRACTION
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

def gcd_stage(q, hX, r, cutoff=None, top_fraction=None, lean=None, shared_matmul=None):
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


r = int(sys.argv[1]); out = sys.argv[2]
L = json.load(open(os.path.join(out, f'ledger_r{r}.json')))
last = L['trials'][-1]; D, m, n, C = L['D'], L['m'], L['n'], L['C']
phs, inf = SETUP_POWER(m, E)
power = sum(phs.values(), V())
from attack_mont import BUILD, EVAL, EVAL_ARITH, EVAL_LOADS, LEAD_BOUND, EXP_COST, TS_T
b = BUILD(n, r)
sub = {'R': r, 'LASTP': 3 + r, 'C': C, 'D': f'{D:,}', 'M': f'{m:,}', 'N': f'{n:,}', 'LASTTRIAL': last['trial'],
       'TRIAL': last['trial'], 'FRAC': L['gcd_params']['top_fraction'], 'A': f'{1 << inf["j"]:,}', 'J': inf['j'], 'L': f'{inf["L"]:,}', 'NSQ': inf['n_squarings'],
       'NMX': inf['n_mulx'], 'TN': EX(T_S(n)), 'TNL': EX(T(n)), 'EVALA': EVAL_ARITH(r), 'EVALL': EVAL_LOADS(r),
       'EVAL': EX(EVAL(r).s), 'RPART': '1 partial round' if r == 1 else f'{r} partial rounds',
       'BUILD': EX(b.s), 'BUILDL': EX(b.l), 'PH_G': EX(phs['g_values'].s), 'PH_S': EX(phs['start_residue'].s),
       'PH_B': EX(phs['batch_inverse'].s), 'PH_T': EX(phs['tables'].s), 'STEP': EX(inf['step_plain'].s),
       'STEPL': EX(inf['step_plain'].l), 'STEPX': EX(inf['step_mulx'].s), 'PH_P': EX(phs['powering'].s),
       'PH_F': EX(phs['finish'].s), 'POWER': EX(power.s), 'POWERL': EX(power.l), 'PEAKPOW': f'{PEAK_WORDS(m):,}',
       'LEADB': f'{LEAD_BOUND(r):,}', 'TSC': f'{EXP_COST(TS_T):,}', 'SETUP': EX(L['setup']['strict']),
       'FINISH': EX(last['finish']['strict']), 'DIGEST': last['pairs'][0]['digest'],
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
APP = ['attack_mont.py', 'attack_v4_ref.py', 'ntt.py', 'mont.py', 'halfgcd.py', 'gcd_stage.py', 'roots.py', 'halfgcd_charge.py',
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

`ledger_r1.json`:

```json
{
 "method": "odd-part line + value-domain Montgomery powering",
 "r": 1,
 "D": 78125,
 "m": 39062,
 "n": 49152,
 "C": 237,
 "centres": "c_i = i, i = 1, 2, ...",
 "gcd_params": {
  "cutoff": 48,
  "top_fraction": 12
 },
 "setup": {
  "loose": 180064,
  "strict": 192504
 },
 "trials": [
  {
   "trial": 1,
   "centre": 1,
   "build": {
    "loose": 28213246,
    "strict": 37240824,
    "counters": {
     "mul": 18726910,
     "add": 49152,
     "sub": 98304,
     "load": 8912892,
     "store": 114686,
     "loop": 0,
     "ctl": 311302
    },
    "lp": 0
   },
   "t_build_s": 6.7,
   "t_power_s": 640.6,
   "power_phases": {
    "g_values": {
     "loose": 2416640,
     "strict": 3020832
    },
    "start_residue": {
     "loose": "42436191/2",
     "strict": 26677717
    },
    "batch_inverse": {
     "loose": "885489/2",
     "strict": 676219
    },
    "tables": {
     "loose": 7176192,
     "strict": 8896606
    },
    "powering": {
     "loose": 2448998310,
     "strict": 3079157535
    },
    "finish": {
     "loose": 10231808,
     "strict": 12888194
    }
   },
   "power": {
    "loose": 2490483790,
    "strict": 3131317103,
    "counters": {
     "mul": 799867227,
     "add": 395907072,
     "sub": 400095077,
     "load": 357326138,
     "store": 333500051,
     "loop": 200101735,
     "ctl": 3686490
    },
    "lp": 150108859
   },
   "power_info": {
    "n": 49152,
    "m": 39062,
    "j": 13,
    "L": 18283,
    "n_squarings": 240,
    "n_mulx": 45
   },
   "t_gcd_s": 15.8,
   "gcd": {
    "loose": 533090866,
    "loose_ops": 523934323,
    "loose_overhead": 9156543,
    "strict": 715882165,
    "peak_words": 206377,
    "detail": {
     "ops": 523934323,
     "ops_exact": "1047868645/2",
     "peak_words": 206377,
     "gcd_degree": 1,
     "roots": [
      "8211592263700648355153845322262465523014571840032995416865989503420410474923"
     ],
     "cutoff": 48,
     "top_fraction": 12,
     "gcd_ops": "1047868643/2",
     "roots_ops": "1",
     "roots_draws": 0,
     "gcd_products": {
      "classical": 77520,
      "ntt": 203,
      "zero": 1151
     },
     "gcd_divisions": {
      "classical": 39061,
      "newton": 0
     },
     "gcd_lean": {
      "matvec_wrap": 1138,
      "matmul_shared": 960
     },
     "lean": true,
     "shared_matmul": true,
     "peak_where": "matvec_wrap 4N",
     "roots_divisions": {
      "classical": 0,
      "newton": 0
     },
     "roots_products": {
      "classical": 0,
      "ntt": 0,
      "zero": 0
     },
     "roots_monic": 0,
     "roots_powmod": 0
    }
   },
   "small": {
    "loose": 3,
    "strict": 6
   },
   "deg_G": 1,
   "roots_S": [
    "8211592263700648355153845322262465523014571840032995416865989503420410474923"
   ],
   "finish": {
    "loose": 4825,
    "strict": 4825
   },
   "total_loose": 3051792730,
   "total_strict": 3884444923,
   "pairs": [
    {
     "S": "8211592263700648355153845322262465523014571840032995416865989503420410474923",
     "s": "20207478098499093028815817790308049074535474374329900434429142058997034423287",
     "W1": "20207478098499093028815817790308049074535474374329900434429142058997034423288",
     "W2": "8740544210829955827076928461863927888827582107611660281525534705352933207051",
     "a": [
      "12941391690195211253787396055278317414090256115287666397768949726577714733217",
      "16713513992334649970128081704475340944631690484025691362997195722179362842056"
     ],
     "b": [
      "400746338219878451246824796404147894169820982317077000444226029921088790410",
      "530322421043498149799310801928189727521807171954748273752411595810898024590"
     ],
     "digest": "c6891e5992ad847ab001d1bbc1f1d1c63d577831ee73eaf7a317420c0b74da06"
    }
   ]
  }
 ],
 "memory_words": {
  "build": 49216,
  "power": 196608,
  "gcd": 206377
 },
 "peak_words": 206377,
 "memory_bytes": 7652640,
 "memory_log2_bytes": 22.867526102471828,
 "total_loose": 3051972794,
 "time_log2_loose": 23.618351706796414,
 "score_loose": 26.485877809268242,
 "total_strict": 3884637427,
 "time_log2_strict": 23.966389555927098,
 "score_strict": 26.833915658398926,
 "claim_convention": "strict",
 "lead_aD": "18653193895048279516470692955929650894065018955965880129679370593623936737605"
}
```

`gcd_sweep_indep_r1.jsonl` (the independent-instance sweep that fixed the top-level reduction, Section 7):

```json
{"instance": "random monic degree 39062, seed A", "top_fraction": 4, "cutoff": 48, "deg_G": 0, "gcd_strict": 621905859.0, "gcd_peak_words": 225907, "power_strict": 3131317103.0, "score_power_plus_gcd": 26.89752}
{"instance": "random monic degree 39062, seed A", "top_fraction": 5, "cutoff": 48, "deg_G": 0, "gcd_strict": 622273768.0, "gcd_peak_words": 220048, "power_strict": 3131317103.0, "score_power_plus_gcd": 26.86461}
{"instance": "random monic degree 39062, seed A", "top_fraction": 6, "cutoff": 48, "deg_G": 0, "gcd_strict": 630215397.0, "gcd_peak_words": 216142, "power_strict": 3131317103.0, "score_power_plus_gcd": 26.84519}
{"instance": "random monic degree 39062, seed A", "top_fraction": 8, "cutoff": 48, "deg_G": 0, "gcd_strict": 648587932.0, "gcd_peak_words": 211258, "power_strict": 3131317103.0, "score_power_plus_gcd": 26.82363}
{"instance": "random monic degree 39062, seed A", "top_fraction": 12, "cutoff": 48, "deg_G": 0, "gcd_strict": 715882594.0, "gcd_peak_words": 206377, "power_strict": 3131317103.0, "score_power_plus_gcd": 26.81994}
{"instance": "random monic degree 39062, seed A", "top_fraction": 16, "cutoff": 48, "deg_G": 0, "gcd_strict": 796317075.0, "gcd_peak_words": 203935, "power_strict": 3131317103.0, "score_power_plus_gcd": 26.83499}
{"instance": "random monic degree 39062, seed A", "top_fraction": 24, "cutoff": 48, "deg_G": 0, "gcd_strict": 970492430.0, "gcd_peak_words": 201493, "power_strict": 3131317103.0, "score_power_plus_gcd": 26.88263}
```

`gcd_trace_r1_t1.json` (trial 1):

```json
{"division_classical":{"52,51":914,"51,50":913,"50,49":1016,"49,48":1016,"48,47":1081,"47,46":1059,"46,45":1062,"45,44":1018,"44,43":999,"43,42":972,"42,41":930,"41,40":888,"40,39":868,"39,38":828,"38,37":784,"37,36":746,"36,35":711,"35,34":671,"34,33":628,"33,32":585,"32,31":544,"31,30":495,"30,29":449,"29,28":406,"28,27":344,"27,26":301,"76,75":384,"26,25":229,"25,24":126,"153,152":11,"75,74":396,"306,305":3,"151,150":20,"73,72":434,"24,23":51,"610,609":3,"303,302":11,"150,149":22,"1221,1220":2,"304,303":8,"609,608":4,"2442,2441":1,"1219,1218":1,"607,606":4,"301,300":6,"148,147":10,"96,95":31,"95,94":10,"94,93":38,"93,92":32,"92,91":73,"91,90":78,"90,89":137,"89,88":118,"88,87":158,"87,86":154,"86,85":164,"85,84":164,"84,83":211,"83,82":206,"82,81":268,"81,80":269,"80,79":270,"79,78":286,"78,77":309,"77,76":309,"74,73":391,"72,71":428,"71,70":427,"70,69":467,"69,68":467,"68,67":511,"67,66":511,"66,65":554,"65,64":555,"64,63":595,"63,62":595,"62,61":644,"61,60":644,"60,59":691,"59,58":691,"58,57":735,"57,56":734,"56,55":797,"55,54":797,"54,53":840,"53,52":840,"4884,4883":1,"2440,2439":1,"1218,1217":2,"35806,35805":1,"141,140":3,"280,279":3,"138,137":21,"559,558":3,"139,138":19,"277,276":10,"136,135":17,"1119,1118":2,"279,278":9,"558,557":4,"2238,2237":1,"1117,1116":1,"556,555":5,"276,275":6,"4476,4475":1,"2236,2235":1,"1116,1115":2,"32821,32820":1,"129,128":6,"256,255":6,"126,125":20,"513,512":3,"127,126":21,"255,254":10,"1026,1025":1,"511,510":3,"253,252":11,"124,123":16,"2052,2051":1,"1024,1023":2,"510,509":6,"4102,4101":1,"2049,2048":1,"1023,1022":2,"30085,30084":1,"118,117":5,"235,234":6,"115,114":20,"471,470":1,"117,116":20,"234,233":9,"940,939":1,"468,467":5,"232,231":11,"114,113":18,"1881,1880":1,"469,468":4,"939,938":2,"3760,3759":1,"1878,1877":1,"937,936":2,"466,465":3,"231,230":6,"27577,27576":1,"108,107":13,"216,215":5,"106,105":23,"432,431":1,"214,213":9,"105,104":20,"862,861":1,"429,428":4,"213,212":11,"1723,1722":1,"430,429":4,"859,858":3,"427,426":3,"211,210":7,"103,102":7,"3447,3446":1,"861,860":1,"1722,1721":1,"25278,25277":1,"99,98":15,"198,197":5,"97,96":22,"396,395":1,"196,195":9,"790,789":1,"393,392":5,"195,194":12,"1581,1580":1,"394,393":4,"789,788":2,"3160,3159":1,"1578,1577":1,"787,786":2,"391,390":3,"193,192":6,"23170,23169":1,"181,180":5,"363,362":1,"180,179":9,"724,723":1,"360,359":5,"178,177":11,"1449,1448":1,"361,360":4,"723,722":2,"2896,2895":1,"1446,1445":1,"721,720":2,"358,357":3,"177,176":7,"21238,21237":1,"166,165":5,"333,332":1,"165,164":9,"664,663":1,"330,329":4,"163,162":11,"1327,1326":1,"331,330":4,"661,660":3,"328,327":4,"162,161":6,"2655,2654":1,"663,662":1,"1326,1325":1,"19467,19466":1,"2434,2433":1,"1215,1214":1,"606,605":2,"17843,17842":1,"2230,2229":1,"1113,1112":1,"555,554":1,"16355,16354":1,"2044,2043":1,"1020,1019":1,"508,507":1,"252,251":4,"14991,14990":1,"1875,1874":1,"936,935":1,"13740,13739":1,"1717,1716":1,"856,855":2,"426,425":3,"12594,12593":1,"1575,1574":1,"786,785":1,"11543,11542":1,"1443,1442":1,"720,719":1,"10580,10579":1,"1323,1322":1,"660,659":1,"9697,9696":1,"1212,1211":1,"604,603":2,"300,299":3,"8888,8887":1,"1111,1110":1,"553,552":2,"274,273":3,"135,134":3,"8146,8145":1,"1018,1017":1,"507,506":2,"7466,7465":1,"934,933":1,"465,464":2,"6842,6841":1,"6270,6269":1,"784,783":1,"390,389":2,"5746,5745":1,"718,717":1,"357,356":2,"5266,5265":1,"658,657":1,"327,326":2,"4826,4825":1,"4422,4421":1,"4052,4051":1,"3713,3712":1,"3402,3401":1,"3117,3116":1,"2856,2855":1,"2617,2616":1,"2398,2397":1,"2197,2196":1,"2013,2012":1,"1844,1843":1,"1689,1688":1,"1547,1546":1,"1417,1416":1,"1298,1297":1,"1188,1187":1,"1088,1087":1,"996,995":1,"912,911":1,"835,834":1,"764,763":1,"699,698":1,"639,638":1,"584,583":1,"534,533":1,"488,487":1,"446,445":1,"407,406":1,"372,371":1,"340,339":1,"310,309":1,"283,282":1,"258,257":1,"23,22":8,"22,21":8,"21,20":8,"20,19":8,"19,18":8,"18,17":9,"17,16":8,"16,15":9,"161,160":1,"15,14":8,"146,145":1,"14,13":8,"132,131":1,"13,12":7,"12,11":9,"120,119":1,"11,10":8,"109,108":1,"10,9":9,"9,8":7,"8,7":6,"7,6":5,"6,5":3,"5,4":1,"4,3":1,"3,2":1,"2,1":1},"product_zero":{"2,0":1151},"addsub":{"1":1151,"2":2302,"3":2302,"4":2302,"5":2302,"6":2300,"7":2296,"8":2293,"9":2291,"10":2288,"11":2285,"12":2283,"13":2282,"14":2281,"15":2279,"16":2277,"17":2276,"18":2275,"19":2273,"20":2272,"21":2271,"22":2270,"23":2269,"24":2225,"25":2107,"26":2015,"27":1870,"28":1706,"50":160,"51":137,"52":94,"49":161,"53":31,"48":145,"103":28,"104":11,"102":20,"205":11,"206":3,"204":12,"408":5,"409":3,"29":1594,"30":1467,"31":1393,"32":1285,"33":1181,"34":1128,"35":1014,"36":921,"37":881,"38":780,"39":680,"40":636,"41":562,"42":459,"43":406,"44":364,"45":281,"46":193,"47":146,"815":2,"816":2,"407":3,"1629":1,"1630":1,"95":23,"96":4,"94":28,"188":12,"189":3,"187":12,"374":5,"375":3,"93":9,"747":2,"748":2,"373":4,"1493":1,"1494":1,"87":27,"88":6,"86":26,"172":13,"173":6,"343":5,"344":3,"171":9,"685":2,"686":1,"342":4,"684":2,"1369":1,"1370":1,"80":25,"81":5,"79":26,"158":14,"159":5,"157":11,"315":5,"316":1,"314":6,"628":2,"629":1,"78":6,"627":2,"1255":1,"1256":1,"73":31,"74":13,"145":12,"146":5,"72":18,"144":10,"289":5,"290":1,"288":6,"576":2,"577":1,"575":2,"1150":1,"1151":1,"67":31,"68":14,"133":13,"134":5,"66":17,"132":10,"265":5,"266":1,"264":6,"528":2,"529":1,"527":2,"1055":1,"1056":1,"62":26,"63":5,"61":27,"122":13,"123":5,"121":10,"243":5,"244":1,"242":6,"484":2,"485":1,"60":6,"483":2,"967":1,"968":1,"57":25,"58":5,"56":27,"112":13,"113":5,"111":10,"223":5,"224":1,"55":7,"222":6,"444":2,"445":1,"443":2,"886":1,"887":1,"203":4,"406":2,"813":1,"814":1,"186":3,"372":2,"745":1,"746":1,"85":5,"341":2,"683":1,"313":2,"626":1,"143":3,"287":2,"574":1,"263":2,"526":1,"241":2,"482":1,"221":2,"442":1,"101":3,"405":1,"170":2,"156":2,"131":2,"120":2,"110":2,"253":1,"254":1,"230":1,"231":1,"141":1,"142":1,"128":1,"129":1,"116":1,"117":1,"106":1,"107":1,"76":1,"77":1,"69":1,"70":1},"product_classical":{"2,1":2302,"2,2":2302,"2,3":2302,"2,4":2302,"2,5":2300,"2,6":2296,"2,7":2293,"2,8":2291,"2,9":2288,"2,10":2285,"2,11":2283,"2,12":2282,"2,13":2281,"2,14":2279,"2,15":2277,"2,16":2276,"2,17":2275,"2,18":2273,"2,19":2272,"2,20":2271,"2,21":2270,"2,22":2269,"2,23":2225,"2,24":2107,"2,25":2015,"2,26":1870,"2,27":1706,"24,27":148,"23,27":74,"24,28":31,"24,26":160,"25,27":74,"25,28":31,"23,25":86,"25,26":43,"2,51":63,"2,52":31,"22,25":43,"22,26":43,"2,102":28,"2,103":11,"2,50":32,"2,101":20,"2,204":11,"2,205":3,"2,203":12,"2,407":5,"2,408":3,"2,28":1594,"2,29":1467,"2,30":1393,"2,31":1285,"2,32":1181,"2,33":1128,"2,34":1014,"2,35":921,"2,36":881,"2,37":780,"2,38":680,"2,39":636,"2,40":562,"2,41":459,"2,42":406,"2,43":364,"2,44":281,"2,45":193,"2,46":146,"2,47":102,"2,48":32,"2,814":2,"2,815":2,"2,406":3,"2,1628":1,"2,1629":1,"2,94":22,"2,95":3,"2,93":28,"2,187":12,"2,188":3,"2,186":12,"2,373":5,"2,374":3,"2,92":9,"2,746":2,"2,747":2,"2,372":4,"2,1492":1,"2,1493":1,"2,86":27,"2,87":6,"2,85":25,"2,171":13,"2,172":6,"2,342":5,"2,343":3,"2,170":9,"2,684":2,"2,685":1,"2,341":4,"2,683":2,"2,1368":1,"2,1369":1,"2,79":25,"2,80":5,"2,78":26,"2,157":13,"2,158":5,"2,156":10,"2,314":5,"2,315":1,"2,313":6,"2,627":2,"2,628":1,"2,77":6,"2,626":2,"2,1254":1,"2,1255":1,"2,72":31,"2,73":13,"2,144":12,"2,145":5,"2,71":18,"2,143":10,"2,288":5,"2,289":1,"2,287":6,"2,575":2,"2,576":1,"2,574":2,"2,1149":1,"2,1150":1,"2,66":31,"2,67":14,"2,132":13,"2,133":5,"2,65":17,"2,131":10,"2,264":5,"2,265":1,"2,263":6,"2,527":2,"2,528":1,"2,526":2,"2,1054":1,"2,1055":1,"2,61":25,"2,62":5,"2,60":26,"2,121":13,"2,122":5,"2,120":10,"2,242":5,"2,243":1,"2,241":6,"2,483":2,"2,484":1,"2,59":6,"2,482":2,"2,966":1,"2,967":1,"2,56":25,"2,57":5,"2,55":26,"2,111":13,"2,112":5,"2,110":10,"2,222":5,"2,223":1,"2,54":6,"2,221":6,"2,443":2,"2,444":1,"2,442":2,"2,885":1,"2,886":1,"2,202":4,"2,405":2,"2,812":1,"2,813":1,"2,185":3,"2,371":2,"2,744":1,"2,745":1,"2,84":4,"2,340":2,"2,682":1,"2,312":2,"2,625":1,"2,142":3,"2,286":2,"2,573":1,"2,262":2,"2,525":1,"2,240":2,"2,481":1,"2,220":2,"2,441":1,"2,100":3,"2,404":1,"2,169":2,"2,155":2,"2,130":2,"2,119":2,"2,109":2,"19,235":1,"20,234":1,"20,235":1,"21,234":1,"17,214":1,"18,213":1,"18,214":1,"19,213":1,"12,146":1,"13,145":1,"13,146":1,"14,145":1,"10,132":1,"11,131":1,"11,132":1,"12,131":1,"9,120":1,"10,119":1,"10,120":1,"11,119":1,"8,109":1,"9,108":1,"9,109":1,"10,108":1,"8,99":1,"9,98":1,"9,99":1,"10,98":1,"7,89":1,"8,88":1,"8,89":1,"9,88":1,"6,80":1,"7,79":1,"7,80":1,"8,79":1,"5,72":1,"6,71":1,"6,72":1,"7,71":1,"5,65":1,"6,64":1,"6,65":1,"7,64":1,"4,58":1,"5,57":1,"5,58":1,"6,57":1,"4,52":1,"5,51":1,"5,52":1,"6,51":1},"matvec_wrap":{"103,102,25,26,26,27,96":31,"205,204,50,51,51,52,192":11,"101,100,24,25,25,26,96":43,"409,408,101,102,102,103,384":3,"203,202,50,51,51,52,192":20,"99,98,24,25,25,26,96":43,"815,814,203,204,204,205,768":3,"405,404,100,101,101,102,384":11,"201,200,49,50,50,51,192":22,"1629,1628,406,407,407,408,1536":2,"407,406,101,102,102,103,384":8,"813,812,202,203,203,204,768":4,"3257,3256,813,814,814,815,3072":1,"1627,1626,406,407,407,408,1536":1,"811,810,202,203,203,204,768":4,"403,402,100,101,101,102,384":6,"199,198,49,50,50,51,192":10,"6513,6512,1627,1628,1628,1629,6144":1,"3255,3254,813,814,814,815,3072":1,"1625,1624,405,406,406,407,1536":2,"39063,39062,3255,3256,3256,3257,49152":1,"189,188,46,47,47,48,192":3,"375,374,93,94,94,95,384":3,"185,184,45,46,46,47,192":21,"747,746,186,187,187,188,768":3,"187,186,46,47,47,48,192":19,"371,370,92,93,93,94,384":10,"183,182,45,46,46,47,192":17,"1493,1492,372,373,373,374,1536":2,"373,372,92,93,93,94,384":9,"745,744,185,186,186,187,768":4,"2985,2984,745,746,746,747,3072":1,"1491,1490,372,373,373,374,1536":1,"743,742,185,186,186,187,768":5,"369,368,91,92,92,93,384":6,"5969,5968,1491,1492,1492,1493,6144":1,"2983,2982,745,746,746,747,3072":1,"1489,1488,371,372,372,373,1536":2,"35806,35805,2983,2984,2984,2985,49152":1,"173,172,42,43,43,44,192":6,"343,342,85,86,86,87,384":6,"169,168,41,42,42,43,192":20,"685,684,170,171,171,172,768":3,"171,170,42,43,43,44,192":21,"341,340,84,85,85,86,384":10,"1369,1368,341,342,342,343,1536":1,"683,682,170,171,171,172,768":3,"339,338,84,85,85,86,384":11,"167,166,41,42,42,43,192":16,"2737,2736,683,684,684,685,3072":1,"1367,1366,341,342,342,343,1536":2,"681,680,169,170,170,171,768":6,"5471,5470,1367,1368,1368,1369,6144":1,"2733,2732,682,683,683,684,3072":1,"1365,1364,340,341,341,342,1536":2,"32821,32820,2734,2735,2735,2736,49152":1,"159,158,39,40,40,41,192":5,"315,314,78,79,79,80,384":5,"155,154,38,39,39,40,192":20,"629,628,156,157,157,158,768":1,"157,156,38,39,39,40,192":20,"313,312,77,78,78,79,384":9,"1255,1254,313,314,314,315,1536":1,"625,624,155,156,156,157,768":5,"311,310,77,78,78,79,384":11,"153,152,37,38,38,39,192":18,"2509,2508,626,627,627,628,3072":1,"627,626,156,157,157,158,768":4,"1253,1252,312,313,313,314,1536":2,"5015,5014,1253,1254,1254,1255,6144":1,"2505,2504,625,626,626,627,3072":1,"1251,1250,312,313,313,314,1536":2,"623,622,155,156,156,157,768":3,"309,308,76,77,77,78,384":6,"30085,30084,2506,2507,2507,2508,49152":1,"145,144,35,36,36,37,192":13,"289,288,71,72,72,73,384":5,"143,142,35,36,36,37,192":23,"577,576,143,144,144,145,768":1,"287,286,71,72,72,73,384":8,"141,140,34,35,35,36,192":20,"1151,1150,287,288,288,289,1536":1,"573,572,142,143,143,144,768":4,"285,284,70,71,71,72,384":11,"2299,2298,574,575,575,576,3072":1,"575,574,143,144,144,145,768":4,"1147,1146,286,287,287,288,1536":3,"571,570,142,143,143,144,768":3,"283,282,70,71,71,72,384":7,"139,138,34,35,35,36,192":7,"4597,4596,1148,1149,1149,1150,6144":1,"1149,1148,286,287,287,288,1536":1,"2297,2296,573,574,574,575,3072":1,"27577,27576,2297,2298,2298,2299,49152":1,"133,132,32,33,33,34,192":14,"265,264,65,66,66,67,384":5,"131,130,32,33,33,34,192":22,"529,528,131,132,132,133,768":1,"263,262,65,66,66,67,384":9,"129,128,31,32,32,33,192":21,"1055,1054,263,264,264,265,1536":1,"525,524,130,131,131,132,768":5,"261,260,64,65,65,66,384":11,"2109,2108,526,527,527,528,3072":1,"527,526,131,132,132,133,768":4,"1053,1052,262,263,263,264,1536":2,"4215,4214,1053,1054,1054,1055,6144":1,"2105,2104,525,526,526,527,3072":1,"1051,1050,262,263,263,264,1536":2,"523,522,130,131,131,132,768":3,"259,258,64,65,65,66,384":6,"127,126,31,32,32,33,96":6,"25278,25277,2106,2107,2107,2108,24576":1,"123,122,30,31,31,32,96":5,"243,242,60,61,61,62,192":5,"119,118,29,30,30,31,96":21,"485,484,120,121,121,122,384":1,"121,120,29,30,30,31,96":20,"241,240,59,60,60,61,192":9,"967,966,241,242,242,243,768":1,"481,480,119,120,120,121,384":5,"239,238,59,60,60,61,192":11,"117,116,28,29,29,30,96":17,"1933,1932,482,483,483,484,1536":1,"483,482,120,121,121,122,384":4,"965,964,240,241,241,242,768":2,"3863,3862,965,966,966,967,3072":1,"1929,1928,481,482,482,483,1536":1,"963,962,240,241,241,242,768":2,"479,478,119,120,120,121,384":3,"237,236,58,59,59,60,192":6,"23170,23169,1930,1931,1931,1932,24576":1,"113,112,27,28,28,29,96":5,"223,222,55,56,56,57,192":5,"109,108,26,27,27,28,96":21,"445,444,110,111,111,112,384":1,"111,110,27,28,28,29,96":20,"221,220,54,55,55,56,192":9,"887,886,221,222,222,223,768":1,"441,440,109,110,110,111,384":4,"219,218,54,55,55,56,192":11,"107,106,26,27,27,28,96":17,"1771,1770,442,443,443,444,1536":1,"443,442,110,111,111,112,384":4,"883,882,220,221,221,222,768":3,"439,438,109,110,110,111,384":4,"217,216,53,54,54,55,192":6,"3541,3540,884,885,885,886,3072":1,"885,884,220,221,221,222,768":1,"1769,1768,441,442,442,443,1536":1,"21238,21237,1769,1770,1770,1771,24576":1,"3247,3246,811,812,812,813,3072":1,"1621,1620,404,405,405,406,1536":1,"809,808,201,202,202,203,768":2,"19467,19466,1622,1623,1623,1624,24576":1,"2975,2974,743,744,744,745,3072":1,"1485,1484,370,371,371,372,1536":1,"741,740,184,185,185,186,768":1,"17843,17842,1486,1487,1487,1488,24576":1,"2727,2726,681,682,682,683,3072":1,"1361,1360,339,340,340,341,1536":1,"679,678,169,170,170,171,768":1,"337,336,83,84,84,85,384":4,"16355,16354,1362,1363,1363,1364,24576":1,"2501,2500,624,625,625,626,3072":1,"1249,1248,311,312,312,313,1536":1,"14991,14990,1249,1250,1250,1251,24576":1,"2291,2290,572,573,573,574,3072":1,"1143,1142,285,286,286,287,1536":2,"569,568,141,142,142,143,768":3,"13740,13739,1144,1145,1145,1146,24576":1,"2101,2100,524,525,525,526,3072":1,"1049,1048,261,262,262,263,1536":1,"12594,12593,1049,1050,1050,1051,12288":1,"1925,1924,480,481,481,482,1536":1,"961,960,239,240,240,241,768":1,"11543,11542,961,962,962,963,12288":1,"1765,1764,440,441,441,442,1536":1,"881,880,219,220,220,221,768":1,"10580,10579,881,882,882,883,12288":1,"1617,1616,403,404,404,405,1536":1,"807,806,201,202,202,203,768":2,"401,400,99,100,100,101,384":3,"9697,9696,807,808,808,809,12288":1,"1483,1482,370,371,371,372,1536":1,"739,738,184,185,185,186,768":2,"367,366,91,92,92,93,384":3,"181,180,44,45,45,46,192":3,"8888,8887,740,741,741,742,12288":1,"1359,1358,339,340,340,341,1536":1,"677,676,168,169,169,170,768":2,"8146,8145,678,679,679,680,12288":1,"1247,1246,311,312,312,313,1536":1,"621,620,154,155,155,156,768":2,"7466,7465,622,623,623,624,12288":1,"6842,6841,570,571,571,572,12288":1,"1047,1046,261,262,262,263,1536":1,"521,520,129,130,130,131,768":2,"6270,6269,522,523,523,524,6144":1,"959,958,239,240,240,241,768":1,"477,476,118,119,119,120,384":2,"5746,5745,478,479,479,480,6144":1,"879,878,219,220,220,221,768":1,"437,436,108,109,109,110,384":2,"5266,5265,438,439,439,440,6144":1,"4826,4825,402,403,403,404,6144":1,"4422,4421,368,369,369,370,6144":1,"4052,4051,337,338,338,339,6144":1,"3713,3712,309,310,310,311,6144":1,"3402,3401,283,284,284,285,6144":1,"3117,3116,259,260,260,261,3072":1,"2856,2855,237,238,238,239,3072":1,"2617,2616,217,218,218,219,3072":1,"2398,2397,199,200,200,201,3072":1,"2197,2196,182,183,183,184,3072":1,"2013,2012,167,168,168,169,3072":1,"1844,1843,153,154,154,155,3072":1,"1689,1688,140,141,141,142,3072":1,"1547,1546,128,129,129,130,1536":1,"1417,1416,117,118,118,119,1536":1,"1298,1297,108,109,109,110,1536":1,"1188,1187,98,99,99,100,1536":1,"1088,1087,90,91,91,92,1536":1,"996,995,82,83,83,84,1536":1,"912,911,75,76,76,77,1536":1,"835,834,69,70,70,71,768":1,"764,763,63,64,64,65,768":1,"699,698,58,59,59,60,768":1,"639,638,53,54,54,55,768":1,"584,583,48,49,49,50,768":1,"534,533,44,45,45,46,768":1,"488,487,40,41,41,42,768":1,"446,445,37,38,38,39,768":1,"407,406,33,34,34,35,384":1,"372,371,30,31,31,32,384":1,"340,339,28,29,29,30,384":1,"310,309,25,26,26,27,384":1,"283,282,23,24,24,25,384":1,"258,257,21,22,22,23,384":1,"195,194,16,17,17,18,192":1,"177,176,14,15,15,16,192":1,"161,160,13,14,14,15,192":1},"product_ntt":{"23,26":160,"24,25":43},"matmul_shared":{"49,50,50,51,51,52,52,53,192":11,"48,49,49,50,51,52,52,53,192":20,"100,101,101,102,102,103,103,104,384":3,"48,49,49,50,50,51,51,52,192":22,"99,100,100,101,101,102,102,103,384":11,"201,202,202,203,204,205,205,206,768":3,"99,100,100,101,102,103,103,104,384":8,"201,202,202,203,203,204,204,205,768":4,"405,406,406,407,407,408,408,409,1536":2,"47,48,48,49,50,51,51,52,192":10,"98,99,99,100,101,102,102,103,384":6,"200,201,201,202,203,204,204,205,768":4,"404,405,405,406,407,408,408,409,1536":1,"812,813,813,814,814,815,815,816,3072":1,"404,405,405,406,406,407,407,408,1536":2,"811,812,812,813,814,815,815,816,3072":1,"1626,1627,1627,1628,1628,1629,1629,1630,6144":1,"45,46,46,47,47,48,48,49,96":3,"44,45,45,46,46,47,47,48,96":21,"91,92,92,93,94,95,95,96,192":3,"44,45,45,46,47,48,48,49,96":19,"43,44,44,45,46,47,47,48,96":17,"90,91,91,92,93,94,94,95,192":10,"184,185,185,186,187,188,188,189,384":3,"91,92,92,93,93,94,94,95,192":9,"184,185,185,186,186,187,187,188,384":4,"371,372,372,373,373,374,374,375,768":2,"90,91,91,92,92,93,93,94,192":6,"183,184,184,185,186,187,187,188,384":5,"370,371,371,372,373,374,374,375,768":1,"744,745,745,746,746,747,747,748,1536":1,"370,371,371,372,372,373,373,374,768":2,"743,744,744,745,746,747,747,748,1536":1,"1490,1491,1491,1492,1492,1493,1493,1494,3072":1,"41,42,42,43,43,44,44,45,96":6,"40,41,41,42,42,43,43,44,96":20,"83,84,84,85,86,87,87,88,192":6,"40,41,41,42,43,44,44,45,96":21,"83,84,84,85,85,86,86,87,192":10,"169,170,170,171,171,172,172,173,384":3,"39,40,40,41,42,43,43,44,96":16,"82,83,83,84,85,86,86,87,192":11,"168,169,169,170,171,172,172,173,384":3,"340,341,341,342,342,343,343,344,768":1,"168,169,169,170,170,171,171,172,384":6,"339,340,340,341,342,343,343,344,768":2,"682,683,683,684,684,685,685,686,1536":1,"339,340,340,341,341,342,342,343,768":2,"681,682,682,683,683,684,684,685,1536":1,"1365,1366,1366,1367,1368,1369,1369,1370,3072":1,"37,38,38,39,40,41,41,42,96":5,"36,37,37,38,39,40,40,41,96":20,"76,77,77,78,79,80,80,81,192":5,"37,38,38,39,39,40,40,41,96":20,"76,77,77,78,78,79,79,80,192":9,"155,156,156,157,157,158,158,159,384":1,"36,37,37,38,38,39,39,40,96":18,"75,76,76,77,78,79,79,80,192":11,"154,155,155,156,156,157,157,158,384":5,"311,312,312,313,314,315,315,316,768":1,"154,155,155,156,157,158,158,159,384":4,"311,312,312,313,313,314,314,315,768":2,"625,626,626,627,627,628,628,629,1536":1,"75,76,76,77,77,78,78,79,192":6,"153,154,154,155,156,157,157,158,384":3,"310,311,311,312,313,314,314,315,768":2,"624,625,625,626,626,627,627,628,1536":1,"1251,1252,1252,1253,1254,1255,1255,1256,3072":1,"34,35,35,36,36,37,37,38,96":13,"33,34,34,35,36,37,37,38,96":23,"70,71,71,72,72,73,73,74,192":5,"33,34,34,35,35,36,36,37,96":20,"69,70,70,71,72,73,73,74,192":8,"142,143,143,144,144,145,145,146,384":1,"69,70,70,71,71,72,72,73,192":11,"141,142,142,143,143,144,144,145,384":4,"285,286,286,287,288,289,289,290,768":1,"141,142,142,143,144,145,145,146,384":4,"32,33,33,34,35,36,36,37,96":7,"68,69,69,70,71,72,72,73,192":7,"140,141,141,142,143,144,144,145,384":3,"284,285,285,286,287,288,288,289,768":3,"572,573,573,574,575,576,576,577,1536":1,"285,286,286,287,287,288,288,289,768":1,"572,573,573,574,574,575,575,576,1536":1,"1147,1148,1148,1149,1149,1150,1150,1151,3072":1,"31,32,32,33,33,34,34,35,96":14,"30,31,31,32,33,34,34,35,96":22,"64,65,65,66,66,67,67,68,192":5,"30,31,31,32,32,33,33,34,96":21,"63,64,64,65,66,67,67,68,192":9,"130,131,131,132,132,133,133,134,384":1,"63,64,64,65,65,66,66,67,192":11,"129,130,130,131,131,132,132,133,384":5,"261,262,262,263,264,265,265,266,768":1,"129,130,130,131,132,133,133,134,384":4,"261,262,262,263,263,264,264,265,768":2,"525,526,526,527,527,528,528,529,1536":1,"29,30,30,31,32,33,33,34,96":6,"62,63,63,64,65,66,66,67,192":6,"128,129,129,130,131,132,132,133,384":3,"260,261,261,262,263,264,264,265,768":2,"524,525,525,526,526,527,527,528,1536":1,"1051,1052,1052,1053,1054,1055,1055,1056,3072":1,"28,29,29,30,31,32,32,33,96":5,"27,28,28,29,30,31,31,32,96":21,"58,59,59,60,61,62,62,63,192":5,"28,29,29,30,30,31,31,32,96":20,"58,59,59,60,60,61,61,62,192":9,"119,120,120,121,121,122,122,123,384":1,"27,28,28,29,29,30,30,31,96":17,"57,58,58,59,60,61,61,62,192":11,"118,119,119,120,120,121,121,122,384":5,"239,240,240,241,242,243,243,244,768":1,"118,119,119,120,121,122,122,123,384":4,"239,240,240,241,241,242,242,243,768":2,"481,482,482,483,483,484,484,485,1536":1,"57,58,58,59,59,60,60,61,192":6,"117,118,118,119,120,121,121,122,384":3,"238,239,239,240,241,242,242,243,768":2,"480,481,481,482,482,483,483,484,1536":1,"963,964,964,965,966,967,967,968,3072":1,"26,27,27,28,28,29,29,30,96":5,"25,26,26,27,27,28,28,29,96":21,"53,54,54,55,56,57,57,58,192":5,"25,26,26,27,28,29,29,30,96":20,"53,54,54,55,55,56,56,57,192":9,"109,110,110,111,111,112,112,113,384":1,"24,25,25,26,27,28,28,29,96":17,"52,53,53,54,55,56,56,57,192":11,"108,109,109,110,110,111,111,112,384":4,"219,220,220,221,222,223,223,224,768":1,"108,109,109,110,111,112,112,113,384":4,"52,53,53,54,54,55,55,56,192":6,"107,108,108,109,110,111,111,112,384":4,"218,219,219,220,221,222,222,223,768":3,"440,441,441,442,443,444,444,445,1536":1,"219,220,220,221,221,222,222,223,768":1,"440,441,441,442,442,443,443,444,1536":1,"883,884,884,885,885,886,886,887,3072":1,"200,201,201,202,202,203,203,204,768":2,"403,404,404,405,405,406,406,407,1536":1,"809,810,810,811,812,813,813,814,3072":1,"183,184,184,185,185,186,186,187,384":1,"369,370,370,371,371,372,372,373,768":1,"741,742,742,743,744,745,745,746,1536":1,"82,83,83,84,84,85,85,86,192":4,"167,168,168,169,170,171,171,172,384":1,"338,339,339,340,340,341,341,342,768":1,"679,680,680,681,682,683,683,684,1536":1,"310,311,311,312,312,313,313,314,768":1,"623,624,624,625,625,626,626,627,1536":1,"140,141,141,142,142,143,143,144,384":3,"283,284,284,285,286,287,287,288,768":2,"570,571,571,572,573,574,574,575,1536":1,"260,261,261,262,262,263,263,264,768":1,"523,524,524,525,525,526,526,527,1536":1,"238,239,239,240,240,241,241,242,768":1,"479,480,480,481,481,482,482,483,1536":1,"218,219,219,220,220,221,221,222,768":1,"439,440,440,441,441,442,442,443,1536":1,"98,99,99,100,100,101,101,102,384":3,"199,200,200,201,202,203,203,204,768":2,"402,403,403,404,404,405,405,406,1536":1,"43,44,44,45,45,46,46,47,96":3,"89,90,90,91,92,93,93,94,192":3,"182,183,183,184,185,186,186,187,384":2,"368,369,369,370,371,372,372,373,768":1,"167,168,168,169,169,170,170,171,384":2,"337,338,338,339,340,341,341,342,768":1,"153,154,154,155,155,156,156,157,384":2,"309,310,310,311,312,313,313,314,768":1,"128,129,129,130,130,131,131,132,384":2,"259,260,260,261,262,263,263,264,768":1,"117,118,118,119,119,120,120,121,384":2,"237,238,238,239,240,241,241,242,768":1,"107,108,108,109,109,110,110,111,384":2,"217,218,218,219,220,221,221,222,768":1},"monic":{"2":1},"root_linear":{"":1}}
```
