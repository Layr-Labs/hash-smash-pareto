# Orchard r=2: two-round line, radix-16/3·2^k transforms, fused powering and a memory-lean half-gcd: an executed collision at time 2^28.60, memory 2^26.36

## 0. Summary

- **Result.** An ordinary collision of the complete selected-round Orchard hash `poseidon-orchard-r2-prefix-v1`
  (P128Pow5T3 over Pallas, input `[nk, rho, 2^65]`, full rounds 0-3, partial rounds 4 and 5, full rounds 60-63, deployed
  constants and MDS, output coordinate 0). The two canonical inputs are in `certificates/` with their common digest
  `577b6b5f0c9749439979d550d49c2ce70cb079096537c7b7d56c9fbbcec3ad07`; the organizer recomputes it.
- **Construction (Sections 2-4).** The two-round line of entry 1942e47d (tanctl): on the line u(t) = (t D0, t D1, C2) of
  round-1 S-box inputs, the state after round 1 is affine in sigma = t^5, so the digest is a polynomial f(sigma) of degree
  exactly 5^8 = 390,625. For a public sigma0, every root sigma1 of h = (f - f(sigma0)) / (X - sigma0) gives a collision.
- **Root finding (Sections 5-6).** X^p mod h by 254 fused Barrett squarings at transform lengths 786,432 = 3 * 2^18 and
  393,216 = 3 * 2^17; then gcd(h, X^p - X) by a memory-lean half-gcd whose matrix products are cyclic at lengths fixed by
  the half-gcd degree relations (Lemma H, Lemma C), with a blocked in-place remainder; then the root. Transforms have no
  bit-reversal pass and no twiddle table (radix 16/8/4/2 decimation in frequency and in time, plus one radix-3 stage).
- **Trials and probability (Section 7).** The stream sigma0_i = i + 1 was fixed in writing before any full-size trial. Trial 0
  succeeds, which follows from the verified certificate itself (Section 7). The procedure is deterministic, has no coins and
  was executed on the fixed target: success probability 1. No heuristic is used.
- **Cost (Section 8).** Every primitive is charged by an itemized per-item charge tied to the loop bodies of the program
  (Section 8.1, Appendix A). The claimed time is a closed-form worst-case bound (Appendix B) under a schedule that is at
  least the program's counter: 102,050,379,006 primitive operations, / C(2) = 258: 2^28.55926, claimed 28.60. The gcd
  phase is bounded over every remainder sequence. The executed count of the same program, 82,699,733,035, lies below it.
- **Memory (Section 9).** Worst-case live bytes of all arrays over all phases (Appendix B) plus an 8 MiB allowance:
  83,886,080 bytes, 2^26.32193, claimed 26.36. The executed peak of live arrays was 75,497,472 bytes; the resident peak
  of the run (code and libraries included) 79,036,416 bytes.
- **Projected cost axis:** 28.60 + (26.36 - 20) = 34.96 at r = 2 (entry 0aed4072: 37.10; entry 1942e47d: 41.00).

## 1. Target, cost model, notation

Target (repository `verifier/poseidon.py`, `rounds = 2`): the state `[nk, rho, 2^65]` of three Pallas elements passes rounds
with indices 0, 1, 2, 3 (full), 4, 5 (partial) and 60, 61, 62, 63 (full). A round adds its three round constants RC_i, applies
x -> x^5 to all three coordinates (full) or to coordinate 0 only (partial), and multiplies by the 3x3 MDS matrix M. The digest is
coordinate 0 of the final state, encoded canonically. p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001.
Inputs are canonical (each < p); the two messages must differ.

Cost model `orchard-field-ram-v2`: one field addition, subtraction or multiplication, and one primitive 256-bit word operation
(load, store, modular add/sub, bitwise, shift, comparison, conditional branch, random word) cost 1/C(r) target units,
C(2) = 216 + 21*2 = 258. Inversion and exponentiation are charged by their constituent operations. Memory: all stored bytes,
projected as max(0, log2(bytes) - 20) on the cost axis.

Since gcd(5, p - 1) = 1, x -> x^5 is a bijection of F_p with inverse x -> x^e5, e5 = 5^-1 mod (p - 1) =
0x333333333333333333333333333333334e9ee0c9a10a60e2e0f0f3f0cccccccd.

## 2. The two-round line (entry 1942e47d)

Write X = (nk + RC_0[0])^5, Y = (rho + RC_0[1])^5 and K = (2^65 + RC_0[2])^5 (a constant). After round 0 the state is
M (X, Y, K); the round-1 S-box input is u = M (X, Y, K) + RC_1. As (nk, rho) ranges over F_p^2, (X, Y) ranges over F_p^2
bijectively, so u ranges exactly over the plane

    Pi = { u : w . (u - RC_1) = K },   w = third row of M^-1.

All three entries of w are nonzero for the deployed M. Put D0 = w[1], D1 = -w[0], C2 = (K + w . RC_1) / w[2]:

    D0 = 0x1ec7372574f3851bb4ddd4b4d6452256c5e4960d7424cd3776efab42d4fba90b
    D1 = 0x103445906ea65de68dc59c5f3f6254d9734d87cd741d1d666eeba35f8c5836f9
    C2 = 0x09b2d7e67acf680114704863d53135870423bf02a5b6414ddd79da0955bb7210
    K  = 0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c

**Lemma 1 (the line lies in Pi).** For every t in F_p, u(t) = (t D0, t D1, C2) is in Pi.
*Proof.* w . (u(t) - RC_1) = t (w0 D0 + w1 D1) + w2 C2 - w . RC_1 = t (w0 w1 - w1 w0) + K = K. QED.

**Lemma 2 (inputs of a line point).** For t in F_p let (X, Y, Z) = M^-1 (u(t) - RC_1). Then Z = K, and the canonical inputs
nk = X^e5 - RC_0[0], rho = Y^e5 - RC_0[1] produce the round-1 S-box input u(t). The map t -> (nk, rho) is injective.
*Proof.* Z = w . (u(t) - RC_1) = K by Lemma 1. (nk + RC_0[0])^5 = X and (rho + RC_0[1])^5 = Y, so the state after round 0 is
M (X, Y, K) and the round-1 S-box input is M (X, Y, K) + RC_1 = u(t). Two values of t with equal inputs have equal u(t), and
t D0 determines t (D0 != 0). QED.

**Lemma 3 (two rounds become affine).** Along the line, the state after round 1 is S(sigma) = M (sigma D0^5, sigma D1^5, C2^5)
with sigma = t^5, an affine function of sigma; the map t -> sigma is a bijection.
*Proof.* The round-1 S-box maps u(t) to (t^5 D0^5, t^5 D1^5, C2^5); round 1 then multiplies by M. QED.

## 3. The polynomial f and the collision equation

Applying rounds 2, 3 (full), 4, 5 (partial) and 60, 61, 62, 63 (full) to S(sigma), with polynomial arithmetic, gives the digest
as a polynomial f(sigma) in F_p[sigma] for sigma = t^5. Each full round raises the degree of every coordinate by a factor 5 and
the MDS keeps every coordinate at the maximum degree; each partial round does the same through coordinate 0. Hence
deg f <= 5^(2 + 2 + 4) = 5^8 = 390,625, and the program computes deg f = 390,625 exactly (trial line of Section 7).

**Lemma 4 (roots give collisions).** Fix sigma0. If sigma1 != sigma0 is a root of h = (f - f(sigma0)) / (X - sigma0), then the
inputs of sigma0 and sigma1 (Lemma 2, with t = sigma^e5) are two distinct canonical messages with the same selected-round digest.
*Proof.* f(sigma1) = f(sigma0) and f is the digest along the line (Lemma 3). The inputs differ by injectivity (Lemma 2). QED.

The roots of h in F_p are exactly the roots of gcd(h, X^p - X), since X^p - X is the product of all X - a, a in F_p.

## 4. The algorithm

    fixed in advance: the stream sigma0_i = i + 1 (i = 0, 1, ...)
    setup: M^-1 (adjugate, one inversion), D0, D1, C2, K; roots of unity of orders 2^k and 3 * 2^k
    for i = 0, 1, ...:
        f    <- digest polynomial along the line (Section 6.2)
        f0   <- f(sigma0_i)                                  (Horner)
        h    <- (f - f0) / (X - sigma0_i), made monic        (synthetic division, one inversion)
        A    <- X^p mod h                                    (Section 6.3)
        g    <- gcd(h, A - X)                                (Section 6.4)
        if deg g >= 1: sigma1 <- a root of g (Section 6.5); output the inputs of sigma0_i and sigma1 (Lemma 2); halt

The program is `attack_g.c` with `gcd2.h`, `poly.h`, `ntt3.h` and `field.h` (Appendix A; hashes in FROZEN.txt, Section 7).

## 5. Exactness of the steps

- f is computed exactly in F_p (transform products are exact cyclic convolutions over F_p, Section 6.1, at lengths
  exceeding the product degree).
- Synthetic division by X - sigma0 is exact (remainder f(sigma0) - f0 = 0, checked by the program).
- X^p mod h: each step computes the exact remainder of A^2 X^b by h (Lemma 6).
- The gcd: every step is exact (Lemmas H, C, W, Q of Section 6.4); the gcd is unique up to a unit and is made monic. The root
  of a degree-1 gcd X - s is s.
Any correct implementation of these steps gives the same trial outcomes: they depend only on f, sigma0_i and gcds.

## 6. The subroutines

### 6.1 Transforms
Number-theoretic transforms over F_p of length L = 2^k or L = 3 * 2^k. Since p - 1 = 2^32 * 3 * (odd), F_p contains
roots of unity of order 3 * 2^32. The program takes ROOT[32] = 5^((p-1)/2^32) and ROOT3[32] = 5^((p-1)/(3 * 2^32)) and
squares them down: ROOT[k] has order 2^k and ROOT3[k] has order 3 * 2^k. At start-up it checks that ROOT[1] = -1,
ROOT[0] = 1, W3 = ROOT3[0] != 1 with W3^3 = 1, and ROOT3[k]^3 = ROOT[k] for every k.

*Power-of-two length.* The forward transform is decimation in frequency: natural order in, bit-reversed order out. The
inverse is decimation in time: bit-reversed order in, natural order out, followed by the scaling by L^-1. Both are
exact (see below), so there is no bit-reversal pass and no twiddle table. The lg = log2 L levels are grouped into
stages of radix R in {16, 8, 4, 2}, each covering 4, 3, 2 or 1 levels. A stage of radix R works on blocks of R h
elements. For each j < h it loads the R elements x[j + c h] (c < R), applies the stage's log2 R butterfly levels
(half-sizes R h / 2, ..., h) and stores them once. The forward butterfly at half-size H is

    (u, v) -> (u + v, (u - v) w_{2H}^j')

and the inverse butterfly is (u, v) -> (u + v w_{2H}^-j', u - v w_{2H}^-j'). All twiddles of an iteration are powers
of t = w_{Rh}^j times fixed roots of order 16, 8 and 4. t advances by one multiplication per j; the others are
products of t, t^2, t^4 and t^8 with w_16, w_8 and w_4.

The radices come from `ntt_plan(lg)`, which chooses the cover of lg levels with the least kernel charge per element and
puts the largest radices at the top. For lg >= 6 the cover uses only radices 16 and 8; for example lg = 18 gives
(16, 16, 16, 8, 8). The inverse runs the same stages in reverse order with inverse roots.

*Exactness.* Each inverse butterfly with the inverse twiddle maps the forward butterfly's output (u + v, (u - v) w)
back to (2u, 2v). Running the inverse stages in reverse order therefore returns 2^lg = L times the input, and the
final scaling by L^-1 restores it exactly. The forward map is the DFT at the L-th roots of unity (standard
Gentleman–Sande decimation in frequency) with its outputs bit-reversed. A pointwise product of two forward transforms
followed by the inverse is therefore the cyclic convolution mod x^L - 1. Transforms are used only this way; no step
reads an output by its frequency index.

*Length 3M (M = 2^k).* The forward transform is one radix-3 decimation-in-frequency stage over the M index triples
(j, j + M, j + 2M):

    y_0 = a_0 + a_1 + a_2
    y_1 = (a_0 - a_2 + W3 (a_1 - a_2)) w^j
    y_2 = (a_0 - a_1 - W3 (a_1 - a_2)) w^2j      with w = ROOT3[k]

It is followed by the three length-M transforms of the blocks, run as one batch (`ntt_batch`: the same stages applied
to 3M consecutive elements). Block s then holds the values at w^(3i+s), i < M. This uses W3 = w^M and ROOT3[k]^3 =
ROOT[k], so the block transforms run at w^3.

The inverse runs the batch of inverse length-M transforms, then the inverse radix-3 stage:

    z_0 = y_0 / 3,  z_1 = y_1 w^-j / 3,  z_2 = y_2 w^-2j / 3
    a_0 = z_0 + z_1 + z_2
    a_1 = z_0 - z_2 + W3^-1 (z_1 - z_2)
    a_2 = z_0 - z_1 - W3^-1 (z_1 - z_2)

This is the inverse 3-point DFT. With the M^-1 of the block inverses it gives exactly the input back. The result is
again exact evaluation at all L-th roots, so cyclic products mod x^L - 1 hold as for powers of two.

*Length choice.* `pick_len(n)` is the smallest admissible length >= n. Lengths 3 * 2^k are admitted only from
6,144 on, because below that the radix-3 stage and its parallel blocks cost more than the next power of two.

*Parallel execution.* Batches of at most 4,096 elements, and data-parallel loops of at most 4,096 items, run
sequentially. Longer ones split their kernel iterations, taken in (group, j) order, into 64 contiguous ranges. A range
starting inside a group starts its twiddle at w^j0 by square-and-multiply.

*Products.* A product of sizes a, b with min(a, b) > 12 (`MUL_SCHOOL`) loads both operands zero-padded to
L = pick_len(a + b - 1), applies two forward transforms, a pointwise product and one inverse, and keeps the result in
place, shrunk to a + b - 1. Smaller products use the schoolbook product. (The threshold is 12, not 48, because the
bound's monotone envelope prices a product with a small operand at the schoolbook rate for every size of the large
one; at 12 this stays below the transform charge.)

### 6.2 The polynomial f
S(sigma) has degree 1. Each round adds RC_i to the constant terms and raises the affected coordinates to the fifth
power. The fifth power uses one forward transform of length pick_len(5(n-1)+1), a pointwise fifth power and one
inverse transform. The round then applies M (only row 0 in round 63). f is rebuilt in every trial rather than stored.

### 6.3 X^p mod h (fused Barrett powering)
Let n = deg h = 390,624. Let L2 = pick_len(2n) = 786,432 = 3 * 2^18 and L1 = pick_len(n + 1) = 393,216 = 3 * 2^17.
These satisfy L2 >= 2n and L1 >= n + 1.

Precomputation:
- iD = rev(h)^-1 mod x^n by Newton iteration (Section 6.6), and its transform at L2;
- the transform of h at L1.

After this h is freed. It is recovered exactly from its transform at the end, since L1 > deg h.

Two working buffers hold the state: B (L2 elements) and E (L1 elements). E holds the residue A between bits. Start
from A = X, and for each bit b of p below the top one:

1. **Square.** Copy A into B, zero-padded. One forward transform at L2, a pointwise square, one inverse transform.
   If b = 1, shift up by one coefficient. This gives S = A^2 X^b with a2n <= 2n coefficients.
2. **Reduce, if a2n > n.** Let qn = a2n - n.
   (a) Fold into E: E[i] = S_i + S_{i + L1} for i < n. Since a2n <= 2 L1, these are the first n coefficients of
       S mod (x^L1 - 1).
   (b) Write rev(S)_top into B: B[i] = S_{a2n-1-i} for i < qn. This reads B[n..a2n) and writes B[0..qn), which are
       disjoint because qn <= n. Zero B[qn..L2).
   (c) Quotient: one forward transform at L2, a pointwise product with the stored transform of iD, one inverse.
       Reversing B[0..qn) in place gives q.
   (d) Remainder product: zero B[qn..L1). One forward transform at L1, a pointwise product with the stored transform
       of h, one inverse. B[0..L1) now holds q h mod (x^L1 - 1).
   (e) E[i] -= B[i] for i < n.
3. If a2n <= n, copy S into E instead.

Finally, strip leading zeros.

**Lemma 6.** After step 2, E[0..n) = S mod h.

*Proof.*
- **The quotient.** rev(S) = rev(q) rev(h) + x^qn (...), and rev(h) is invertible mod x^qn. So rev(q) =
  rev(S)_top iD mod x^qn: the low qn coefficients of a product of two operands of at most n coefficients each.
  That product has at most 2n - 1 <= L2 coefficients, so the cyclic product at L2 has no wrap.
- **The remainder.** r = S - q h has degree < n < L1, so it equals its own reduction mod x^L1 - 1. That reduction is
  fold_L1(S) - (q h mod (x^L1 - 1)). q h has at most 2n coefficients <= 2 L1, so its reduction is the cyclic
  product at L1.

QED.

### 6.4 gcd(h, X^p - X): memory-lean half-gcd (`gcd2.h`)

The gcd loop (`poly_gcd2`) takes (a, b) = (h, R) with R = (X^p mod h) - X, deg R < deg h. While b != 0: if
deg a > deg b and b has more than 48 coefficients, it replaces (a, b) by the reduced pair of `hgcd2(a, b)` (pair
output), then by (b, a mod b), the remainder formed by `poly_rem_blocked`. At the end it makes a monic. Every function
of `gcd2.h` consumes the polynomials passed to it and releases each one as soon as it is no longer read; every
polynomial passed between steps is fitted to its length.

`hgcd2(a, b, want_m, want_p)` is the half-gcd: with N = deg a and m = ceil(N / 2) it returns
the matrix M (want_m) and/or the reduced pair (c, d) = M (a, b) with deg c >= m > deg d (want_p). Its steps:

1. a0 = a div x^m, b0 = b div x^m; R = hgcd2(a0, b0) (matrix output).
2. (c, d) = R (a, b). If R = I this is a move. If every entry of R has at most 8 coefficients, it is a schoolbook
   accumulation into c and d. Otherwise it is cyclic at L = pick_len(N + 1): a, b and the four entries of R are
   transformed once each (each source is released as soon as it is transformed); c^ = R00^ a^ + R01^ b^ and
   d^ = R11^ b^ + R10^ a^ pointwise; two inverse transforms. Four buffers of length L at most.
3. If deg d < m: return. Otherwise the division c = q d + e (`poly_divmod2`, below). When want_m = 1, R is kept until
   Q R = [[R10, R11], [R00 - q R10, R01 - q R11]] has been formed (two products and two subtractions, `mat_qmul`).
4. If deg e < m: return (d, e) and/or Q R. Otherwise l = deg d, k = 2 m - l, S = hgcd2(d div x^k, e div x^k).
5. Pair output: (c2, d2) = S (d, e), cyclic at L = pick_len(l + 1) (or direct or a move, as in step 2). Matrix
   output: S (Q R), cyclic at L = pick_len(rn), rn = floor(N / 2) + 1. The four entries of S are transformed once;
   each column of Q R is transformed and combined in place, (x, y) <- (S00 x + S01 y, S10 x + S11 y); four inverse
   transforms, each kept to rn coefficients. Direct (schoolbook products) when S or Q R has entries of at most 8
   coefficients.

`poly_divmod2(c, d)` (dividend na, divisor nb, quotient length m = na - nb + 1): schoolbook when nb <= 48 or m <= 48;
otherwise the quotient from the top m coefficients of c and the first min(m, nb) coefficients of rev(d) (Newton inverse
to m coefficients, low product at pick_len(2 m - 1), reversal), and the remainder from the product d q formed cyclically
at L = pick_len(max(nb, m)) with the wrapped part read from c (Lemma W).

`poly_rem_blocked(a, b)` (gcd loop, remainder only, in place in a's buffer): with m = a.n - b.n + 1 and
K = min(m, b.n), schoolbook in place when b.n <= 48 or K <= 48; otherwise I = rev(b)^-1 mod x^K once, b transformed
once at L = pick_len(b.n), and rounds that each take the top window of t <= K + b.n - 1 coefficients, compute its
quotient block from its top t coefficients and I (low product), and replace the window by its remainder, formed
cyclically at L (Lemma W). Each round lowers the length of a by t = min(K, a.n - b.n + 1); there are at most
ceil(m / K) rounds.

**Half-gcd invariants.** Let hgcd(a, b) with N = deg a > deg b, m = ceil(N / 2), N1 = N - m, m1 = ceil(N1 / 2).
(i) The matrix R returned by the recursive call on (a div x^m, b div x^m) has entries of degree at most
N1 - deg c' <= N1 - m1 = floor(N1 / 2), where (c', d') is the reduced pair of that call (deg c' >= m1).
(ii) (c, d) = R (a, b) = x^m R (a div x^m, b div x^m) + R (a mod x^m, b mod x^m), so deg d <= max(m + deg d',
floor(N1 / 2) + m - 1) <= m + m1 - 1, and deg c <= N.
(iii) The division of c by d has quotient length at most N - m + 1 and divisor size at least m + 1.
(iv) With k = 2 m - deg d, the second recursive call has input degree deg d - k = 2 deg d - 2 m <= 2 m1 - 2 <= N1 - 1,
and its matrix entries have degree at most floor((N1 - 1) / 2).
(v) The gcd loop calls hgcd2 with pair output, leaving deg b < m, then one division; the next iteration starts from
degree at most m - 1. Below 49 coefficients it performs at most (deg + 1) schoolbook divisions.
These relations are proved by the following lemma, which uses only steps 1 to 5 above (`hgcd2` in `gcd2.h`,
Appendix A) and not the correctness theory of the half-gcd.

**Lemma H.** For deg a = n > deg b (or b = 0), the call hgcd(a, b) returns a matrix R that is a product of matrices
[[0, 1], [1, -q]] (the identity for an empty product), with (c, d) = R (a, b) satisfying: (a) every entry of R has degree at
most n - deg c; (b) d = 0 or deg d < ceil(n / 2); (c) if R is not the identity, deg c >= ceil(n / 2). In particular every
entry of R has degree at most floor(n / 2).

*Proof.* Strong induction on n; m = ceil(n / 2). If the first early return is taken (deg b < m), R = I and (a) to (c) hold.
Otherwise write a = x^m a0 + a1, b = x^m b0 + b1 with deg a1, deg b1 < m, so deg a0 = N1 = n - m and deg b0 < N1. Let R1
and (c', d') = R1 (a0, b0) be the recursive result. By induction, entries of R1 have degree at most N1 - deg c', and
deg d' < m1 = ceil(N1 / 2). Then (c, d) = R1 (a, b) = x^m (c', d') + R1 (a1, b1), where the second term has degree at most
(N1 - deg c') + m - 1. If R1 = I then (c, d) = (a, b) and deg c = n. Otherwise deg c' >= m1 >= N1 / 2, so
(N1 - deg c') + m - 1 < m + deg c' and deg c = m + deg c' exactly; hence N1 - deg c' = n - deg c, which is (a) for R1.
Also deg d <= max(m + deg d', (N1 - deg c') + m - 1) <= m + m1 - 1. Hence deg d < deg c (when R1 = I, deg d = deg b < n). This proves (i) and (ii) (with R = R1). If the second
early return is taken, deg d < m gives (b), and deg c = m + deg c' >= m when R1 != I, or
deg c = n >= m when R1 = I, which gives (c). Otherwise deg d >= m, the division gives c = q d + e with deg q = deg c - deg d,
so Q = [[0, 1], [1, -q]] and QR1 have entries of degree at most (n - deg c) + (deg c - deg d) = n - deg d; this is (iii)
(quotient length deg c - deg d + 1 <= n - m + 1, divisor size deg d + 1 >= m + 1). If the third early return is taken,
(d, e) is the output: deg e < m is (b), deg d >= m is (c), and (a) was just shown. Otherwise let l = deg d, k = 2m - l
(1 <= k <= m since m <= l <= m + m1 - 1 < 2m), d = x^k d0 + d1, e = x^k e0 + e1 with deg e0 < deg d0 = n2 = l - k = 2l - 2m
<= 2 m1 - 2 <= N1 - 1. The second recursive call returns S and (c2', d2') = S (d0, e0) with, by induction, entries of S of
degree at most n2 - deg c2' <= floor(n2 / 2) <= floor((N1 - 1) / 2), and deg d2' < ceil(n2 / 2) = l - m; this is (iv). Here
S != I: deg e >= m gives deg e0 >= m - k = l - m = ceil(n2 / 2), so the recursive call does not take its first return, and
only that return yields I. As above, (c2, d2) = S (d, e) = x^k (c2', d2') + S (d1, e1) with deg c2' >= ceil(n2 / 2) gives
deg c2 = k + deg c2', so entries of S have degree at most n2 - deg c2' = l - deg c2, and
deg d2 <= max(k + l - m - 1, (n2 - deg c2') + k - 1) <= m - 1, which is (b). The final matrix S Q R1 has entries of degree
at most (l - deg c2) + (n - l) = n - deg c2, which is (a), and deg c2 >= k + ceil(n2 / 2) = m, which is (c). The bound floor(n / 2) follows from (a) and (c), or is 0 for
R = I. QED.

Every matrix [[0, 1], [1, -q]] is invertible over F_p[x], so (c, d) = R (a, b) has gcd(c, d) = gcd(a, b): the gcd loop
returns gcd(h, X^p - X) up to a unit, which it normalizes. For (v): after hgcd with pair output, deg d < ceil(n / 2) by (b),
and one division leaves the next pair at degree at most ceil(n / 2) - 1. The tool's sizes follow: entries of R have at most
floor(N1 / 2) + 1 coefficients, d at most m + m1, the quotient at most n - m + 1, entries of S at most floor((N1 - 1) / 2) + 1,
and entries of Q R1 at most (n - m + 1) + (floor(N1 / 2) + 1) - 1 coefficients.

**Consequences used below.** Lemma H concerns the values of steps 1 to 5; the order in which the products are
evaluated, and the release of operands, do not change them (each product is exact by Lemma C). In particular: deg c <= N and
deg d < deg c after step 2; deg c2 <= l and deg d2 < m <= l after step 5; every entry of Q R has degree at most
N - deg d <= N - m and every entry of S Q R at most N - deg c2 <= N - m, i.e. at most floor(N / 2); every entry of S has degree at most floor(n2 / 2) with n2 = 2 (l - m).

**Lemma C (cyclic products are exact).** Let L be an admissible length (2^k or 3 * 2^k) and u_1, v_1, ..., u_s, v_s
polynomials of at most L coefficients each. Transforming each, forming the pointwise sum of products and transforming
back returns U = sum_j u_j v_j mod (x^L - 1). If deg U < L, it returns U.
*Proof.* The forward transform evaluates its input at the L distinct L-th roots of unity, in a fixed order that is the
same for every input of length L (Section 6.1); pointwise operations act on the values at each root; the inverse
transform interpolates in the same order. Polynomials of degree < L are determined by their values at the L-th roots,
and a polynomial and its residue mod x^L - 1 take the same values there. QED.

Uses, with the degree facts that make them exact (all inputs have at most L coefficients; the program checks this and
stops otherwise):
- step 2: L = pick_len(N + 1) > N >= deg c > deg d;
- step 5, pair: L = pick_len(l + 1) > l >= deg c2 > deg d2;
- step 5, matrix: L = pick_len(rn) >= rn > floor(N / 2) >= the degree of every entry of S Q R; only rn coefficients are
  kept;
- low products (`poly_mullow`): the full product has fewer than L coefficients; it is truncated after. (The Newton
  steps use their own wrap argument, Section 6.6.)

**Lemma W (wrapped remainder).** Let A have w coefficients, b have nb coefficients, and P = b Q with r = A - P of
degree < nb - 1, where P has at most w coefficients. Let L >= nb and 2 L >= w, and C = P mod (x^L - 1). Then for
0 <= i < nb - 1: r_i = A_i - C_i + A_{i+L}, with A_{i+L} = 0 when i + L >= w.
*Proof.* Since P has at most w <= 2 L coefficients, C_i = P_i + P_{i+L}. Since i + L >= L >= nb > nb - 2 >= deg r, the
coefficient of r at i + L is 0, so P_{i+L} = A_{i+L}. Hence A_i - C_i + A_{i+L} = A_i - P_i = r_i. QED.

Uses: `poly_divmod2` (A = c, w = na, L = pick_len(max(nb, m)), so 2 L >= nb + m > na); each round of `poly_rem_blocked`
(A = the window, w = t + nb - 1, L = pick_len(nb) >= nb >= t, so 2 L >= w). C is formed by Lemma C, since the
transform length L is at least the number of coefficients of b and of the quotient block.

**Lemma Q (quotient from the top).** If A has w coefficients and b has nb <= w coefficients with b_{nb-1} != 0, the
quotient Q of A by b has t = w - nb + 1 coefficients and rev_t(Q) = rev_t(A) rev(b)^{-1} mod x^t, where rev_t(A) is the
top t coefficients of A in reverse order and only the first t coefficients of rev(b) enter. (The reversal identity of
Lemma 6.) In `poly_rem_blocked` the window has t + nb - 1 coefficients, so its quotient block has t <= K coefficients
and I = rev(b)^{-1} mod x^K, truncated to t, is the inverse needed. Subtracting x^s Q_t b from a leaves a mod b
unchanged and makes the window's top t coefficients zero; the loop ends when fewer than nb coefficients remain, so the
result is a mod b.

The gcd loop preserves gcd(a, b): hgcd2 replaces (a, b) by M (a, b) with M a product of the invertible matrices
[[0, 1], [1, -q]], and (a, b) -> (b, a mod b) preserves the gcd. It returns the monic gcd of h and X^p - X.

### 6.5 Root extraction
A degree-1 monic gcd X - s gives s directly (the executed case). For degree >= 2 the program splits g with
gcd(g, (X + delta)^((p-1)/2) - 1), delta = 0, 1, ...; this branch was not executed and is not charged.

### 6.6 Newton inverse
g_0 = a_0^-1. Each step from cur to m = min(2 cur, k) coefficients computes

    g <- g - x^cur (g h_hi mod x^(m-cur)),   with h = (a mod x^m) g.

Both products use transforms of length pick_len(m) >= m:
- The first product is cyclic. Its operands have at most m and cur coefficients, so the product has fewer than
  m + cur coefficients. Its wrapped part lands below cur, where h = 1, 0, ..., 0 is known.
- The second product has fewer than m coefficients, so it has no wrap.

Steps with m <= 48 use schoolbook products.

## 7. The trial stream and the executed run

The canonical stream is sigma0_i = i + 1 (i = 0, 1, 2, ...), field elements in this order, with the stopping rule "first trial
whose gcd has degree >= 1". It was written down before any full-size trial (`STREAM.txt`, verbatim; the program hashes in it
are those of the first program of this campaign):

    Orchard r=2 (and later r=1) two-round-line campaign, fixed before any real-size trial.
    sigma0 stream: sigma0_i = i + 1 (i = 0, 1, 2, ...), as Pallas field elements; trials run in that order; every trial charged; stop at the first trial whose gcd has degree >= 1.
    program: attack_line.c sha256 b275dbc20fdd48dae5d31aba7fc8cb79910e3e70919e1e4963eb2b9724219f3c
    poly.h sha256 4a104a650cf7b50195d5a47344dc84ad785520cf463fc6345016266be0ddce6f
    field.h sha256 40ed7163f0041831b8c06291a5e9ec31e75a4d5be8403b7dc319a73e81c3ab78
    recorded 2026-10-12T11:54:15Z

The program has since been rewritten for lower charged time and memory (transforms, powering, gcd). The claimed run is the
final program's, frozen before the run (`FROZEN.txt`, verbatim except that the local directory of the allocator shim is
replaced by `<shim directory>`):

    FROZEN: final r=2 two-round-line program (transform layer m3 + gcd2), run of 2026-10-12T13:43:10Z
    attack_g.c f8d7c6008a6be80cf04d9e05c5265837766177e21248338413bd8ee7978d9a2f
    gcd2.h     f8d4724d2c508e6b781eefaa3395edb7b9a0aeac639231d0b76cf15a84f4559c
    poly.h     bb4d6d39cc79fc33d0636a774cc96096b440d4a0b014b198196826cc9a68e484
    ntt3.h     546ae548a0b26287a630d6144c30b25d8a9a8d1d227ee27effedd3ca89fdfdc0
    field.h    40ed7163f0041831b8c06291a5e9ec31e75a4d5be8403b7dc319a73e81c3ab78
    consts.txt 48c2b6ed216545d8a5d850b3d0c37a4969e05f84630c097a31c59fd768bc1494
    bound/gcdbound.py      8e62991cc9e04fb4bd3429930abab90c79357c3bd2e4358ac705ccc0da9c40a5
    bound/gcdbound2.py     e24f2576311bf3d1dda1f6bf75704249062d049901016032eaaf708f872d7b72
    bound/orchard_bound.py 0342f7759a75e92711f50649650231626e34212b82bb451f402a9c3423b9ca59
    bound/checks.py        d9c6c57243df4e298217074f47df6c98e9f0e928f0a61f71440b374fda91d533
    stream: sigma0_i = i + 1 (canonical stream of STREAM.txt, fixed 2026-10-12T11:54:15Z before any real-size trial; unchanged)
    build: clang -O3 -march=native -o attack_g attack_g.c
    run:   launch ./attack_g consts.txt 0,1,2,3,4,5,60,61,62,63 20 1   (launch + pageshim.dylib: <shim directory>)
    result: trial 0, gcd_degree 1, same pair as the certificate (nk/rho identical to certificates/message-a.bin, message-b.bin)
    executed: ops_total 82,699,733,035; build 248,137,113; powmod 71,773,270,652; tracked peak 75,497,472 B; child maxrss 79,036,416 B
    bound (python3 orchard_bound.py 2 1 1): build 264,521,182; powmod 74,414,845,704; gcd 27,344,355,655; total 102,050,379,006
      time_log2 28.559263; mem_bytes 83,886,080 (powmod 75,497,472 + 8 MiB); mem_log2 26.321928
    recommended claim: time_log2 28.58 (1.45% above bound), memory_log2_bytes 26.33 (0.56% above), normalized 34.91
    collision verified independently with the organizer constants (python reference permutation): True

The "recommended claim" line is the recording session's suggestion; this package claims 28.60 and 26.36, with more slack
above the same bound. The run's output:

    trial 0 sigma0 1 deg_f 390625 deg_h 390624 gcd_degree 1 ops 82699608981  (55.0s, peak 72.0MB)
    sigma0 0000000000000000000000000000000000000000000000000000000000000001
    sigma1 277707bf2058ffaea9e6cd53121d695a138a816213d4e52d5757638be3864950
    nk0 037111ab0ba1db0c1e5613a8bf91b666f4b5c76f90628662b98300105ed711b5
    rho0 28b8b9e06caf5ff12d95bb14ad07ff7a63b6dc763822d67938d7e64d064c9c7b
    nk1 38f5b3a815665a62d863e6f35e6d30a8e062fa4ce3265baf43cb5125a2301594
    rho1 0ab79b56b2356294142a57fe327a3f943c00545fc5d47c16ae7816e44830b468
    line_check 1 1
    trials 1
    ops_total 82699733035
    mem_peak_bytes 75497472

The first program of the campaign (frozen at 11:56:56Z, same stream) found the identical sigma1 and messages at trial 0; that
is necessarily so, since the trial outcome depends only on f, sigma0_0 and gcds (Section 5).

**Success probability 1.** The procedure reads no random words; its control path on the fixed target is determined, and its
execution returned the pair above at trial 0. A deterministic procedure that outputs a collision on its only control path
succeeds with probability 1. The time bound charges the trials up to and including the successful one (one trial), with no
allowance for spare trials.

**Trial 0 succeeds: checkable from the certificate alone.** The two certificate messages are the inputs of sigma0 = 1 and of
sigma1 under Lemma 2 (both are printed above; anyone can recompute them from the round-0/1 constants and M). The organizer
checks that they are distinct, canonical and collide on the selected target. Since equal sigma gives equal messages, distinct
messages give sigma1 != 1. By Lemma 3 the digest of the message of sigma is f(sigma), so f(sigma1) = f(1), and sigma1 is a root in
F_p of h_0 = (f - f(1)) / (X - 1). Hence X - sigma1 divides both h_0 and X^p - X, gcd(h_0, X^p - X) has degree >= 1 at trial 0,
and the stopping rule fires at trial 0. The trial count 1 used by the bound is a consequence of the verified certificate.

**The gcd degree on success (1) is a participant-executed outcome.** The argument above shows it is at least 1; that it equals
1 rests on the run (`gcd_degree 1`). It enters only root extraction: with degree 1 the root is read off the monic linear gcd.

## 8. Charged time

### 8.1 Per-item charges and the code
Each kernel adds, per item it processes, a fixed charge that bounds the primitive operations of its loop body in this RAM
model: every 256-bit load and store, every field addition, subtraction and multiplication, address arithmetic, and three
operations of loop control per iteration (increment, comparison, branch). Address arithmetic is counted as pointer advances: one
operation per pointer that a loop advances per iteration (accesses at a fixed offset from an advanced pointer share it); each
address entry below is at least the number of such advances. Constants are instruction immediates. The charges are constants in
`poly.h`, `ntt3.h` and `gcd2.h` (Appendix A), added to the counter `OPS` by the kernel that executes the loop.

| Charge | Per | Loop body it bounds |
| --- | ---: | --- |
| CH_HEX = 170 | 16 elements, 4 levels | 16 loads, 16 stores, 32 data multiplications, 15 twiddle multiplications (advance; 7 for t w_16^c; t^2 and 3 for t^2 w_8^c; t^4, t^4 w_4, t^8), 64 additions/subtractions, 16 addresses, 3 loop; 8 spare |
| CH_OCT = 76 | 8 elements, 3 levels | 8 loads, 8 stores, 12 data multiplications, 7 twiddle multiplications (advance, t^2, t^4, t w_8, t w_4, t w_8 w_4, t^2 w_4), 24 additions/subtractions, 8 addresses, 3 loop; 6 spare |
| CH_QUAD = 34 | 4 elements, 2 levels | 4 loads, 4 stores, 4 data multiplications, 3 twiddle multiplications (advance, t^2, t w_4), 8 additions/subtractions, 4 addresses, 3 loop; 4 spare |
| CH_BFLY = 16 | 2 elements, 1 level | 2 loads, 2 stores, 2 multiplications (product, advance), 2 additions/subtractions, 3 addresses, 3 loop; 2 spare |
| CH_R3F = 28 | 3 elements, forward radix-3 | 3 loads, 3 stores, 5 multiplications (W3 d, two twiddles, two advances), 7 additions/subtractions, 3 addresses, 3 loop; 4 spare |
| CH_R3I = 30 | 3 elements, inverse radix-3 | 3 loads, 3 stores, 6 multiplications (three scaled twiddles, W3^-1 d, two advances), 7 additions/subtractions, 3 addresses, 3 loop; 5 spare |
| block starts | parallel stage | 64 blocks x (8 log2 h + 16) for the starting twiddle; radix-3 stage 64 x (16 log2 M + 40) (two starting twiddles) |
| CH_SCALE = 8 | element | load, multiplication, store, 2 addresses, 3 loop |
| CH_PMUL = 10 | element | 2 loads, multiplication, store, 3 addresses, 3 loop |
| CH_PSQR = 8 | element | load, multiplication, store, 2 addresses, 3 loop |
| CH_PPOW5 = 10 | element | load, 3 multiplications, store, 2 addresses, 3 loop |
| CH_COPY = 7 | element | load, store, 2 addresses, 3 loop |
| CH_ZERO = 5 | element | store, address, 3 loop |
| CH_ADDV = 12 | element | 2 loads, add/sub, store, 3 addresses, 2 length tests, 3 loop |
| CH_AXPY = 13 | element | 2 loads, multiplication, add/sub, store, 3 addresses, 2 length tests, 3 loop |
| CH_SCHOOL = 12 | term of a schoolbook product | 3 loads, multiplication, addition, store, 3 addresses, 3 loop |
| CH_PMAC = 15 | element (gcd2.h) | T = T A + U B: 4 loads, 2 multiplications, addition, store, 4 addresses, 3 loop |
| CH_PMACC = 13 | element (gcd2.h) | U = U + V A: 3 loads, multiplication, addition, store, 3 addresses, 3 loop |
| CH_MAT2 = 24 | element (gcd2.h) | (x, y) <- (S00 x + S01 y, S10 x + S11 y): 6 loads, 4 multiplications, 2 additions, 2 stores, 6 addresses, 3 loop; 1 spare |
| CH_REM = 15 | element (gcd2.h) | r_i = a_i - x_i + a_{i+L}: 3 loads, 2 additions/subtractions, store, 4 addresses, length test (2), 3 loop |
| CH_OUTER_C = 6 | outer iteration (gcd2.h) | schoolbook outer loop: counter, compare, branch, row pointer, multiplier load; 1 spare |
| CH_CALL = 64 | kernel call | size computations, setup, branches, return |
| inversion | each | 255 squarings and 255 multiplications at 3 each (6 per exponent bit), plus 16 |
| trim | each | 2, plus 4 per stripped zero coefficient |

The parallel form of a stage also advances a group counter in every iteration: increment, compare, branch, and two
operations to recompute the base pointer. These 5 operations are covered by the spare of CH_HEX (8) and CH_OCT (6).
Those are the only radices of parallel stages: a parallel batch has more than 4,096 elements, hence M >= 2,048,
lg >= 11, and the plan uses radices 16 and 8 only.

**Registers.** The radix-16 kernel keeps its 16 operands, its 15 twiddles, the stage roots (w_Rh, w_16, w_8, w_4) and
two temporaries in machine registers: a constant register file of at most 40 256-bit words. Every access to an array is a charged load or store. The RAM
model charges primitive operations and loads and stores of memory words and has no register-count parameter. A
constant number of word registers is part of any RAM machine. The program needs no more
than these 40 (the radix-8 kernel uses about 21).

Exponentiations (roots of unity, L^-1, 3^-1, inversions, fifth roots of the two inputs) are counted by the program at 6 per
exponent bit. A full square-and-multiply step also tests a bit and keeps its operands in memory, about 12 operations per bit;
the bound of Section 8.3 charges 16 per bit (4,160 per exponentiation). The parallel execution charges each block's start and
nothing else, since the cost model sums work over processors.

**Allocation.** Time: the bound charges 128 per kernel call and per release of unused capacity, 64 more than the program's
counter for a call; the surplus pays for constant-time requests and releases. Memory: Section 9 counts the peak of
simultaneously live array bytes (the working state) plus an allowance; this is the space of a bump allocator over virtual
addresses that returns the pages of a released array (and the tail pages of a shrunk one) to the operating system. Appendix C
gives such an allocator as a shim loaded at run time (the program is unchanged); the claimed run used it.

### 8.2 Executed count
The program adds every charge as it runs (the counter `OPS`); the run of Section 7 counted 82,699,733,035 operations for setup,
the one trial and the recovery of both inputs: everything before the powering (build of f, Horner, synthetic division, monic
scaling) 248,137,113; the powering 71,773,270,652; R = A - X and the gcd 10,678,201,216; setup and the recovery of the
inputs 124,054.

### 8.3 The claimed bound
The claimed time is not the executed count: it is the value of a closed-form upper bound for the stated algorithm at the
executed sizes and trial count, computed by `orchard_bound.py` with `gcdbound.py` and `gcdbound2.py` (Appendix B; standard
library, integer arithmetic). Its schedule is at least the program's counter for every loop body (the per-item charges of
Section 8.1 are its floor) and also prices what the counter leaves out (outer group loops, the 64 parallel blocks of every
data-parallel loop, allocation per kernel call, length tests, trims at higher rates, exponentiations at 16 per exponent bit).
The data-independent phases are charged at their exact sizes; the gcd phase by a worst-case bound over every remainder sequence
of the given degree. The only run outcomes it takes as inputs are the number of trials (1; implied by the verified certificate,
Section 7) and the gcd degree of the successful trial (1; participant-executed). A 2^20 allowance covers constants, Montgomery
conversions, output and the two digest checks.

`python3 orchard_bound.py 2 1 1` prints:

    C 258
    deg_f 390625
    deg_h 390624
    build 264521182
    powmod 74414845704
    gcd 27344355655
    per_trial 102048726964
    total 102050379006
    time_log2 28.55926332875894
    mem_bytes 83886080
    mem_log2 26.32192809488736
    peaks {'build': 75000192, 'powmod': 75497472, 'gcd': 68761088}

The total is setup 578,426 (line setup, transform-root initialization), one trial 102,048,726,964 (build of f 264,521,182;
Horner, synthetic division, monic scaling and R = A - X 25,004,423; powering 74,414,845,704; gcd 27,344,355,655), the
recovery of both inputs 25,040, and the allowance 1,048,576. So T <= 102,050,379,006 / 258 target units, log2 T = 28.55926;
claimed time_log2 = 28.60 (integer check: 102050379006^100 < 2^2860 * 258^100), 2.9 per cent above the bound.
Executed against bound, per phase: build and the steps before the powering 248,137,113 <= 264,521,182 + 17,191,809 (the per-trial steps other than
R = A - X); powering
71,773,270,652 <= 74,414,845,704; R = A - X and the gcd 10,678,201,216 <= 27,352,168,269.

**The data-independent phases.** The transform charges in the bound (`gcdbound.py`: `ntt_plan`, `_stage`, `ntt_batch`, `ntt_any`) mirror the program
stage by stage. On top of the counter they price:
- the outer group loop (12 per group);
- for a parallel stage, its 64 blocks (24 each) and its block starts at 16 per exponent bit, `64 * (16 log2 h + 16)`;
- for the radix-3 stage, `64 * (32 log2 M + 48)`;
- the inverse scaling with an exponentiation of 4,160.

The bound program checks that these charges are nondecreasing over all admissible lengths up to 2^22.

Powering, per bit with residue size an = min(e + 1, n) for A = X^e:
- copy and zero at L2;
- two transforms at L2 and the pointwise square, with its parallel blocks;
- the shift;
- when a2n > n: the fold (CH_ADDV n), the reversal and zeroing at L2, two transforms at L2 and the pointwise
  product, the reversal and zeroing at L1, two transforms at L1 and the pointwise product, and the subtraction
  (CH_ADDV n);
- the trim.

Precomputation: rev(h), the Newton inverse of length n, and the two transforms. At the end, recovery of h by one
inverse transform at L1.

**The gcd phase (`gcdbound2.py`).** The gcd phase is charged by `gcdbound2.py` (Appendix B; standard library, integer arithmetic), which mirrors every kernel
of `gcd2.h` and takes its transform, product, Newton-inverse and charge definitions unchanged from `gcdbound.py`
(Section 6.1). Its schedule is at least the program's counter for every loop body: the gcd2.h per-item charges
(CH_PMAC 15, CH_PMACC 13, CH_MAT2 24, CH_REM 15, CH_OUTER 6; Section 8.1) plus 64 parallel blocks (CH_PAR) for every
data-parallel loop, 128 per kernel call and per release of unused capacity (poly_fit), trims at 6 + 6 per coefficient,
and exponentiations at 16 per exponent bit.

**Majorants of the kernels.** Each kernel's charge is bounded by a function of upper bounds of its sizes that is
nondecreasing in each of them:
- `poly_divmod2` (divmod2_ub(na, qmax, nbmax)): the transform branch only when qmax > 48 and nbmax > 48; each of its
  terms depends on one size (the quotient length for the reversals, the Newton inverse and the low product; the divisor
  for the remainder loop) and is evaluated at its maximum; the remainder transform length pick_len(max(nb, q)) is at
  most pick_len(min(na, max(nbmax, qmax))). The schoolbook branch is evaluated at its two extreme shapes.
- `poly_rem_blocked` (rem_blocked_ub(na, nbmax)): the exact maximum over every divisor size nb <= nbmax (enumerated)
  of the charge at dividend na, which is nondecreasing in na for fixed nb; ceil(m / K) rounds at the round charge of
  K, trims over all rounds removing at most na coefficients in total.
- matrix application: direct when the largest entry of R has at most 8 coefficients (charged at entry size
  min(e, 8)), cyclic otherwise; matrix product: direct when S or Q R has largest entry of at most 8 coefficients. When
  the entry bounds rule a branch out it is not charged; otherwise the bound is the larger of the two branches.

**hgcd2.** For deg a <= N, the bound T_{m,p}(N) charges the fixed part (two shifts, the first recursive call at N1 =
floor(N / 2), the copy of R when want_m, the application of R at L = pick_len(N + 1)) and then the part after it, which
depends on l = deg d. On the full path m <= l <= m + m1 - 1 (Lemma H), and given l: the quotient has at most N - l + 1
coefficients, the divisor l + 1, the second call has degree 2 (l - m), the entries of S at most l - m + 1 coefficients,
the vectors of S (d, e) at most l + 1 (at L = pick_len(l + 1)), the entries of Q R and of the result at most rn. The
offsets l - m are split into the intervals {0}, [1, 1], [2, 3], [4, 7], ... (capped at m1 - 1); on each interval every
term is bounded at the end that maximizes it (the quotient and Q R at the low end, all others at the high end), and
T takes the largest interval. A large middle quotient therefore forces a small second call, instead of both being
charged at their maxima. Early returns are prefixes of the path charged. The per-level table below gives the values.

**Monotonicity.** T_{m,p}(N) is nondecreasing in N: m, N1, eR, rn and the interval ends m + hi, N1 - lo + 1 are
nondecreasing in N; the set of intervals only grows with m1; every kernel majorant is nondecreasing in its sizes and
transform charges are nondecreasing over admissible lengths (`checks.py`); induction on N for the recursive terms. The
tool also checks T(N) <= T(N + 1) for every N < 6,000 in both call modes. Hence evaluating T at the upper bounds of
Lemma H bounds every actual call.

**The loop.** Level n (deg a <= n) charges max(T_{0,1}(n), 48 small divisions on 48 coefficients) plus
rem_blocked_ub(n + 1, n), and the next level has degree ceil(n / 2) - 1 (Lemma H (b) and one remainder). If the loop
skips hgcd2 because b has at most 48 coefficients, the remainder is charged at that level and every later step works on
at most 48 coefficients: at most 48 divisions, charged in place of the skipped hgcd2. Below 49 coefficients the Euclid
tail performs at most n + 1 divisions on at most n + 1 coefficients; then the monic scaling.

**Memory.** `gcdbound2.py` replays the allocations and releases of the code step by step (class Live): every object
is allocated and released at the same upper bound of its size, and recursive calls contribute their own peak, which
includes their inputs and outputs. At every instant the live set of the program is a subset of the replayed live set,
each object with a size at most its replayed size, so the replayed peak bounds the live peak. The cyclic matrix
application peaks at four buffers of length L plus the remaining entries; the division at its Newton or product
buffers; the blocked remainder adds O(K + L) to the dividend it reduces in place. At level 1 the inputs are h
(n + 1 coefficients) and R (n).

**Checks.** On 126 executed gcd computations (degrees 60 to 100,000; random pairs; a first quotient of degree N / 2;
two families of backwards-built remainder sequences with quotient degrees up to 2,000 (non-normal); divisors of 60
coefficients and of N / 10 coefficients, which exercise the multi-round remainder; planted gcds of degree 0, 3 and 40),
every gcd was correct, and executed charge and peak memory were at most the bounds: charge at most 0.37 of the bound,
memory at most 1.00 (on degree 100,000 the bound exceeds the executed peak by 64 bytes). On the full-size r = 2
instance R = A - X and the gcd charged 10,678,201,216 operations against their bound 27,352,168,269 (the gcd
27,344,355,655 plus 7,812,614 for R = A - X).

**Per-level table** (`python3 gcd2_table.py`, from `gcdbound2.py` with the same functions; every level's sum equals the
tool's total):

    gcd loop levels: hgcd2 with pair output, then the blocked remainder
      deg  390624: hgcd2   14,045,702,342   remainder    395,103,781   hgcd2 memory  2,148,784 coeff
      deg  195311: hgcd2    6,627,208,614   remainder    185,357,243   hgcd2 memory  1,074,562 coeff
      deg   97655: hgcd2    3,134,117,322   remainder     92,329,931   hgcd2 memory    537,456 coeff
      deg   48827: hgcd2    1,477,119,572   remainder     45,889,365   hgcd2 memory    268,904 coeff
      deg   24413: hgcd2      693,770,413   remainder     21,984,156   hgcd2 memory    134,640 coeff
      deg   12206: hgcd2      323,811,028   remainder     10,501,790   hgcd2 memory     67,502 coeff
      deg    6102: hgcd2      151,430,952   remainder      5,341,102   hgcd2 memory     33,930 coeff
      deg    3050: hgcd2       70,290,794   remainder      2,671,584   hgcd2 memory     18,673 coeff
      deg    1524: hgcd2       32,451,471   remainder      1,355,907   hgcd2 memory      9,338 coeff
      deg     761: hgcd2       14,852,747   remainder        696,474   hgcd2 memory      4,669 coeff
      deg     380: hgcd2        6,766,939   remainder        357,239   hgcd2 memory      2,336 coeff
      deg     189: hgcd2        3,009,357   remainder        192,440   hgcd2 memory      1,168 coeff
      deg      94: hgcd2        1,339,084   remainder         40,458   hgcd2 memory        584 coeff
      Euclid tail at deg 46 and normalization: 663,550
      total 27,344,355,655 (gcd_bound2 = 27,344,355,655); memory gcd_mem2 = 2,148,784 coefficients

    hgcd2 with matrix output: fixed part and the largest interval of l - m
          N             rec1        apply R    worst l-m            div           Q R             rec2           S QR             T(N)
     195312    3,152,517,221    104,882,028 (32768, 48827)    109,087,538    55,060,644    3,152,468,520     91,411,720    6,670,214,777
     195311    3,152,469,274    104,882,028 (32768, 48827)    109,087,524    55,060,540    3,152,468,520     91,410,784    6,670,165,734
      97656    1,486,532,399     52,445,036 (16384, 24413)     54,546,662    24,405,084    1,486,484,794     45,708,712    3,152,517,221
      97655    1,486,485,548     52,445,036 (16384, 24413)     54,546,648    24,404,980    1,486,484,794     45,707,776    3,152,469,274
      97654    1,486,485,548     52,445,036 (16384, 24413)     54,545,908    24,404,980    1,486,484,794     45,707,776    3,152,468,520
      48828      698,473,132     26,066,796 (8192, 12206)     27,276,224    12,234,168      698,426,623     22,857,208    1,486,532,399
      48827      698,427,377     26,066,796 (8192, 12206)     27,276,210    12,234,064      698,426,623     22,856,272    1,486,485,548
      48826      698,427,377     26,066,796 (8192, 12206)     27,275,470    12,234,064      698,426,623     22,856,272    1,486,484,794
      24414      326,819,206     13,053,804 (4096, 6103)     13,641,368     6,108,748      326,818,452     11,431,456      698,473,132
      24413      326,818,452     13,053,804 (4096, 6102)     13,640,628     6,108,696      326,775,207     11,430,520      698,427,377
      24412      326,818,452     13,053,804 (4096, 6102)     13,639,888     6,108,696      326,775,207     11,430,520      698,426,623
      12207      152,497,962      5,888,876 (2048, 3051)      6,823,940     3,092,092      152,497,208      5,718,112      326,819,206
      12206      152,497,962      5,888,876 (2048, 3051)      6,823,200     3,092,092      152,497,208      5,718,112      326,818,452
      12205      152,497,208      5,888,876 (2048, 3050)      6,822,460     3,092,040      152,457,227      5,717,176      326,775,961
       6103       70,851,156      3,103,596 (1024, 1525)      3,414,856     1,265,044       70,850,402      2,861,440      152,497,962
       6102       70,851,156      3,103,596 (1024, 1525)      3,414,116     1,265,044       70,850,402      2,861,440      152,497,208
       6101       70,850,402      3,103,596 (1024, 1524)      3,413,376     1,264,992       70,813,685      2,860,504      152,457,981
       3051       32,732,085      1,531,564   (512, 762)      1,710,314       636,064       32,731,331      1,433,104       70,851,156
       3050       32,732,085      1,531,564   (512, 762)      1,709,574       636,064       32,731,331      1,433,104       70,850,402
       3049       32,731,331      1,531,564   (512, 761)      1,708,834       636,012       32,697,878      1,432,168       70,814,439

## 9. Memory
Memory is all stored bytes. The bound program evaluates the worst-case live bytes of every phase with lifetimes that follow the
code (Appendix B):

- **Build of f:** 75,000,192 bytes.
- **X^p mod h:** 75,497,472 bytes. These are the buffers B and the transform of iD (786,432 elements each) and E and
  the transform of h (393,216 elements each), 2,359,296 elements in all. h is held only as its transform during the
  powering; the residue lives in E. The program's tracked peak during the powering was exactly 75,497,472 bytes.
- **gcd:** 68,761,088 bytes (2,148,784 coefficients; worst case over all remainder sequences by the replay of Section 8.3,
  inputs h and R included).

With 4 coefficients of scalar state and an 8 MiB allowance, the bound is 83,886,080 bytes: log2 = 26.32193, claimed
memory_log2_bytes = 26.36 (83886080^100 < 2^2636), 2.7 per cent above the bound. The allowance covers the code
(the executable is about 150 KiB; the C library and libdispatch code it calls), the constants (67 rows of 256-bit words and
the root tables), the stacks of the main thread and of up to 12 workers (recursion depth below 50 frames of a few hundred bytes;
parallel loop bodies keep no arrays on the stack) and allocator metadata. The executed peak of live arrays, tracked by the
program over all allocations, was 75,497,472 bytes (the powering). The run used the page-returning allocator of Appendix C; its
peak resident set size (getrusage ru_maxrss of the child, which includes code, shared libraries, stacks and allocator metadata)
was 79,036,416 bytes, below the claim. No stored table between phases, no advice: preprocessing_log2 = 0 (the setup is part of
the charged time) and nonuniform_advice_log2_bytes = 0.

**Projected cost axis:** 28.60 + (26.36 - 20) = 34.96 at r = 2.

## 10. Evidence
- **Certificate.** `certificates/message-a.bin` and `message-b.bin` (canonical 64-byte encodings of (nk0, rho0) and (nk1, rho1));
  the organizer recomputes both digests. Checked locally with `verifier/poseidon.py`, and with an independent Python
  permutation using the organizer constants: equal digests, distinct, canonical.
- **Line replay.** Both messages are the Lemma 2 inputs of sigma0 = 1 and sigma1 (Section 7): recomputable from the round-0/1
  constants and M alone, and both points satisfy Z = K.
- **Bound programs.** Appendix B prints `gcdbound.py`, `gcdbound2.py`, `orchard_bound.py` and `checks.py` in full with their
  SHA-256 (as in FROZEN.txt). They use the standard library only and run in seconds. No organizer experiment is declared: the
  experiment runner sizes the digest with `digest_fn(b"")`, which the Orchard digest rejects (it requires exactly 64 bytes), so
  python experiments cannot currently run on this track. `checks.py` output:

    candidate exactness: bad 0
    divmod_ub monotone violations 0
    hgcd monotone violations 0
    hgcd_peak monotone violations 0
    transform charge monotone violations 0
    gcd_bound2 monotone violations (N<3000) 0
    gcd_mem2 monotone violations (N<3000) 0
    8e62991cc9e04fb4bd3429930abab90c79357c3bd2e4358ac705ccc0da9c40a5  gcdbound.py
    e24f2576311bf3d1dda1f6bf75704249062d049901016032eaaf708f872d7b72  gcdbound2.py
    0342f7759a75e92711f50649650231626e34212b82bb451f402a9c3423b9ca59  orchard_bound.py
    d9c6c57243df4e298217074f47df6c98e9f0e928f0a61f71440b374fda91d533  checks.py
- **gcd checks (participant).** 126 executed gcd computations (Section 8.3): every gcd correct, executed charge at most 0.37 of
  the bound and peak memory at most the bound.
- **Transform and arithmetic checks (participant).** Round trips at every admissible length up to 2^21 (powers of two and
  3 * 2^k); products, squares, fifth powers, Newton inverses and divisions against schoolbook references up to 524,288 x 500,000;
  field arithmetic against Python big integers.
- **Full run.** Section 7: the same pair as the certificate, line check 1 1.

## 11. Limitations
- The time is a charged bound in the stated machine model, not a wall-clock measurement (the run took 55 s on a 12-core laptop).
- Per-item charges are upper bounds for the written loops in this RAM model (Section 8.1); a different implementation could
  charge differently. The bound of Section 8.3 is a function of operand sizes only and does not depend on the run, except for
  the trial count and the gcd degree.
- Memory is the peak of live array bytes plus an allowance. It is realized physically by the page-returning allocator of
  Appendix C (resident peak 79,036,416 bytes); the default macOS allocator keeps released blocks resident for reuse and
  peaked at 229,851,136 bytes on the same run.
- The stream was fixed by us; trial 0 succeeded. A different public stream could need more trials; the bound charges the
  executed number.

## 12. Credits
The two-round line is entry 1942e47d's (tanctl), as is the convention of a written, fixed sigma0 stream. Univariate root finding
with gcd(g, X^p - X) and the deterministic executed-outcome argument on this board come from Th0rgal's entries (94e9246a).
Entry 0aed4072 (tanctl) described, for the same line, a worst-case-bounded half-gcd with transform lengths 3 * 2^k, cyclic
matrix-vector products exact at the working length and blocked Newton division; we read its note before designing the
corresponding parts here (lengths 3 * 2^k, the cyclic matrix products, the blocked remainder), which are our own
implementations with their own proofs and bounds. New here: the counted transform layer (radix 16/8/4/2 without bit reversal,
the radix-3 stage), the fused 3 * 2^k powering with its exact memory, the consuming half-gcd with in-place matrix products,
the truncated-reversal division, the l-interval worst-case time bound and the step-by-step memory replay. The work was done
by two Claude Code sessions of the same submitter.

## Appendix A. Program sources
The executed program, frozen before the claimed run (FROZEN.txt), byte for byte, so its hashes match the executed build.
The header comment and usage line of `attack_g.c` are stale: they describe an earlier variant of the same file (fixed rho,
two values of beta), and the file also keeps unused earlier functions (`build_out`, `powmod_ref`). The code that runs is
main() at the end of `attack_g.c`: the two-round line of Sections 2-7. Compile: `cc -O3 -march=native -o attack_g attack_g.c`
(macOS; libdispatch for the parallel loops; the charges do not depend on the parallel split). Run:
`./attack_g consts.txt 0,1,2,3,4,5,60,61,62,63 20 1` (round list, transform table limit, maximum trials), with `consts.txt`
(SHA-256 48c2b6ed216545d8a5d850b3d0c37a4969e05f84630c097a31c59fd768bc1494) = `orchard-pallas-constants.json` written as its 64 `round_constants` rows
followed by its 3 `mds` rows, one row per line, the row's three hex strings separated by single spaces:

    python3 -c "import json; d = json.load(open('orchard-pallas-constants.json')); print(''.join(' '.join(r) + '\n' for r in d['round_constants'] + d['mds']), end='')" > consts.txt

### A.1 `field.h` (SHA-256 40ed7163f0041831b8c06291a5e9ec31e75a4d5be8403b7dc319a73e81c3ab78)

```c
// Pallas base field arithmetic, Montgomery form with R = 2^256, four 64-bit limbs.
// p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
#pragma once
#include <stdint.h>
#include <string.h>
#include <stdio.h>

typedef unsigned __int128 u128;
typedef struct { uint64_t v[4]; } fe;

static const fe P = {{0x992d30ed00000001ULL, 0x224698fc094cf91bULL, 0x0000000000000000ULL, 0x4000000000000000ULL}};
static const uint64_t PINV = 0x992d30ecffffffffULL; // -p^{-1} mod 2^64
static fe R2;      // 2^512 mod p (Montgomery conversion), set by fe_init
static fe ONE;     // Montgomery form of 1

static inline int fe_geq_p(const fe *a) {
    for (int i = 3; i >= 0; i--) {
        if (a->v[i] > P.v[i]) return 1;
        if (a->v[i] < P.v[i]) return 0;
    }
    return 1;
}
static inline void fe_sub_p(fe *a) {
    u128 b = 0;
    for (int i = 0; i < 4; i++) {
        u128 d = (u128)a->v[i] - P.v[i] - b;
        a->v[i] = (uint64_t)d; b = (d >> 64) & 1;
    }
}
static inline fe fe_add(fe a, fe b) {
    fe r; u128 c = 0;
    for (int i = 0; i < 4; i++) { c += (u128)a.v[i] + b.v[i]; r.v[i] = (uint64_t)c; c >>= 64; }
    if (fe_geq_p(&r)) fe_sub_p(&r);   // p < 2^255 so no overflow of 256 bits
    return r;
}
static inline fe fe_sub(fe a, fe b) {
    fe r; u128 bw = 0;
    for (int i = 0; i < 4; i++) { u128 d = (u128)a.v[i] - b.v[i] - bw; r.v[i] = (uint64_t)d; bw = (d >> 64) & 1; }
    if (bw) { u128 c = 0; for (int i = 0; i < 4; i++) { c += (u128)r.v[i] + P.v[i]; r.v[i] = (uint64_t)c; c >>= 64; } }
    return r;
}
static inline fe fe_neg(fe a) { fe z = {{0,0,0,0}}; return fe_sub(z, a); }
static inline fe fe_mul(fe a, fe b) {   // CIOS Montgomery multiplication
    uint64_t t[6] = {0};
    for (int i = 0; i < 4; i++) {
        u128 c = 0;
        for (int j = 0; j < 4; j++) { c += (u128)a.v[j] * b.v[i] + t[j]; t[j] = (uint64_t)c; c >>= 64; }
        c += t[4]; t[4] = (uint64_t)c; t[5] = (uint64_t)(c >> 64);
        uint64_t m = t[0] * PINV;
        c = (u128)m * P.v[0] + t[0]; c >>= 64;
        for (int j = 1; j < 4; j++) { c += (u128)m * P.v[j] + t[j]; t[j-1] = (uint64_t)c; c >>= 64; }
        c += t[4]; t[3] = (uint64_t)c; c >>= 64; t[4] = t[5] + (uint64_t)c;
    }
    fe r = {{t[0], t[1], t[2], t[3]}};
    if (t[4] || fe_geq_p(&r)) fe_sub_p(&r);
    return r;
}
static inline int fe_is_zero(fe a) { return (a.v[0] | a.v[1] | a.v[2] | a.v[3]) == 0; }
static inline int fe_eq(fe a, fe b) { return memcmp(&a, &b, sizeof a) == 0; }

// plain (non-Montgomery) 256-bit from hex string
static fe fe_plain_from_hex(const char *h) {
    fe r = {{0,0,0,0}};
    if (h[0] == '0' && (h[1] == 'x' || h[1] == 'X')) h += 2;
    size_t n = strlen(h);
    for (size_t k = 0; k < n; k++) {
        char c = h[n - 1 - k]; uint64_t d = (c <= '9') ? c - '0' : (c | 32) - 'a' + 10;
        r.v[k / 16] |= d << (4 * (k % 16));
    }
    return r;
}
static inline fe fe_to_mont(fe a) { return fe_mul(a, R2); }
static inline fe fe_from_mont(fe a) { fe one = {{1,0,0,0}}; return fe_mul(a, one); }
static fe fe_from_u64(uint64_t x) { fe a = {{x,0,0,0}}; return fe_to_mont(a); }
static fe fe_from_hex(const char *h) { return fe_to_mont(fe_plain_from_hex(h)); }
static void fe_print(const char *label, fe a) {
    fe b = fe_from_mont(a);
    printf("%s%016llx%016llx%016llx%016llx\n", label, (unsigned long long)b.v[3], (unsigned long long)b.v[2],
           (unsigned long long)b.v[1], (unsigned long long)b.v[0]);
}
static fe fe_pow_plain_exp(fe base, fe e) {     // e plain integer
    fe r = ONE;
    for (int i = 255; i >= 0; i--) {
        r = fe_mul(r, r);
        if ((e.v[i / 64] >> (i % 64)) & 1) r = fe_mul(r, base);
    }
    return r;
}
static void fe_init(void) {
    // R2 = 2^512 mod p computed by repeated doubling of 1 (plain), then that value IS 2^512 mod p in plain.
    fe x = {{1,0,0,0}};
    for (int i = 0; i < 512; i++) { x = (fe){{x.v[0], x.v[1], x.v[2], x.v[3]}};
        u128 c = 0; fe y; for (int k = 0; k < 4; k++) { c += (u128)x.v[k] * 2; y.v[k] = (uint64_t)c; c >>= 64; }
        if (fe_geq_p(&y)) fe_sub_p(&y); x = y; }
    R2 = x;
    fe one = {{1,0,0,0}}; ONE = fe_mul(one, R2);
}
```

### A.2 `poly.h` (SHA-256 bb4d6d39cc79fc33d0636a774cc96096b440d4a0b014b198196826cc9a68e484)

```c
// Counted polynomial arithmetic over the Pallas field.
// Every kernel adds its charged operations (orchard-field-ram-v2: field add/sub/mul, 256-bit load/store,
// word operations, comparisons and branches each weigh 1) to the global counter OPS, by documented
// per-item charges (CH_* below), computed from the item counts of the call.
#pragma once
#include "field.h"
#include <stdlib.h>
#include <dispatch/dispatch.h>

// ---------- charges per item (upper bounds for the loop bodies written below) ----------
#define CH_BFLY    16  // 2 loads (u, v), 2 mul (product, twiddle step), add, sub, 2 stores, 3 address ops, 3 loop; +2 spare
#define CH_QUAD    34  // per 4 elements, 2 stages: 4 loads, 4 stores, 4 data mul, 3 twiddle mul (t^2, t*I, step), 8 add/sub, 4 address, 3 loop; +4 spare
#define CH_BREV    20  // incremental reverse counter (amortized <= 8), compare, branch, swap (2 loads, 2 stores, 2 addresses), 3 loop
#define CH_SCALE    8  // load, mul, store, 2 address, 3 loop
#define CH_PMUL    10  // 2 loads, mul, store, 3 address, 3 loop
#define CH_PSQR     8  // load, mul, store, 2 address, 3 loop
#define CH_PPOW5   10  // load, 3 mul, store, 2 address, 3 loop
#define CH_COPY     7  // load, store, 2 address, 3 loop
#define CH_ZERO     5  // store, 1 address, 3 loop
#define CH_ADDV    12  // 2 loads, add/sub, store, 3 address, 2 length tests, 3 loop
#define CH_AXPY    13  // 2 loads, mul, add/sub, store, 3 address, 2 length tests, 3 loop
#define CH_SCHOOL  12  // per term: 3 loads (a_i, b_j, acc), mul, add, store, 3 address, 3 loop
#define CH_CALL    64  // fixed per kernel call: setup, size computations, branches, returns

static unsigned long long OPS = 0;
static long long MEM_CUR = 0, MEM_PEAK = 0;
static void *xalloc(size_t bytes) {
    void *p = malloc(bytes ? bytes : 1);
    if (!p) { fprintf(stderr, "out of memory\n"); exit(1); }
    MEM_CUR += bytes; if (MEM_CUR > MEM_PEAK) MEM_PEAK = MEM_CUR;
    return p;
}
static void xfree(void *p, size_t bytes) { free(p); MEM_CUR -= bytes; }
static void *xshrink(void *p, size_t old, size_t now) { void *q = realloc(p, now ? now : 1); if (!q) q = p; MEM_CUR -= (long long)(old - now); return q; }

typedef struct { fe *c; long n; long cap; } poly;   // n = number of coefficients (deg+1); 0 = zero poly
static poly poly_new(long cap) { poly p; p.cap = cap > 0 ? cap : 1; p.c = xalloc(sizeof(fe) * p.cap); p.n = 0; return p; }
static void poly_free(poly *p) { if (p->c) xfree(p->c, sizeof(fe) * p->cap); p->c = NULL; p->n = p->cap = 0; }
static void poly_trim(poly *p) { while (p->n > 0 && fe_is_zero(p->c[p->n - 1])) { p->n--; OPS += 4; } OPS += 2; }
static long deg(const poly *p) { return p->n - 1; }
static poly poly_copy(const poly *a) { poly r = poly_new(a->n); memcpy(r.c, a->c, sizeof(fe) * a->n); r.n = a->n; OPS += CH_COPY * a->n + CH_CALL; return r; }
static poly poly_from(const fe *c, long n) { poly r = poly_new(n); memcpy(r.c, c, sizeof(fe) * n); r.n = n; OPS += CH_COPY * n + CH_CALL; poly_trim(&r); return r; }

// ---------- NTT ----------
// No twiddle table: stage h uses w_h, a primitive (2h)-th root of unity (ROOT[k], k = log2(2h)), and each
// butterfly advances its twiddle by one multiplication (replacing a twiddle load). Parallel blocks that
// start inside a group start from w_h^j0 (one short exponentiation per block, charged).
static int LOGMAX = 0; static long LMAX = 0;
static fe ROOT[33], IROOT[33];       // ROOT[k] primitive 2^k-th root of unity, IROOT[k] its inverse
static void ntt3_init(void);
static void ntt_init(int logmax) {
    LOGMAX = logmax; LMAX = 1L << logmax;
    fe e = P; e.v[0] -= 1;
    fe q = {{ (e.v[0] >> 32) | (e.v[1] << 32), (e.v[1] >> 32) | (e.v[2] << 32), (e.v[2] >> 32) | (e.v[3] << 32), e.v[3] >> 32 }};
    ROOT[32] = fe_pow_plain_exp(fe_from_u64(5), q);           // 5 generates the 2-Sylow part (checked below)
    for (int k = 31; k >= 0; k--) ROOT[k] = fe_mul(ROOT[k + 1], ROOT[k + 1]);
    if (!fe_eq(ROOT[1], fe_neg(ONE)) || !fe_eq(ROOT[0], ONE)) { fprintf(stderr, "root of unity check failed\n"); exit(1); }
    for (int k = 0; k <= 32; k++) IROOT[k] = fe_pow_plain_exp(ROOT[k], (fe){{P.v[0] - 2, P.v[1], P.v[2], P.v[3]}});
    OPS += 33 * 2 * 256 * 3 + 2000;
    ntt3_init();
}
#define NTT_SEQ_MAX 4096   // transforms of at most this length run sequentially (no parallel blocks)
// parallel pointwise helpers
#define PAR_FOR(L, body) do { if ((L) <= NTT_SEQ_MAX) { for (long i = 0; i < (L); i++) { body; } } else \
    dispatch_apply(64, DISPATCH_APPLY_AUTO, ^(size_t blk__) { \
        long lo__ = (long)blk__ * ((L) / 64), hi__ = (blk__ == 63) ? (L) : lo__ + (L) / 64; \
        for (long i = lo__; i < hi__; i++) { body; } }); } while (0)

static fe fe_pow_u64(fe b, uint64_t e) { fe r = ONE; while (e) { if (e & 1) r = fe_mul(r, b); b = fe_mul(b, b); e >>= 1; } return r; }
// Forward transform: decimation in frequency (natural order in, bit-reversed order out); inverse: decimation in
// time (bit-reversed order in, natural order out), each inverse butterfly undoing the forward one up to a factor 2,
// then scaling by L^-1. No bit-reversal pass: transforms are only used for pointwise products (cyclic convolution).
// Levels are grouped in stages of radix 16, 8, 4 or 2 (four to one levels over blocks of R h) by ntt_plan, the
// largest radices at the top; the inverse runs the same stages in reverse order. Twiddles: t = w_{Rh}^j advanced by one multiplication per j.
#define CH_OCT     76  // per 8 elements, 3 levels: 8 loads, 8 stores, 12 data mul, 7 twiddle mul (step, t^2, t^4, t w8, t I4, t w8 I4, t^2 I4), 24 add/sub, 8 address, 3 loop; +6 spare
#define DIF(p, q, w) { u = p; v = q; p = fe_add(u, v); q = fe_mul(fe_sub(u, v), w); }
#define DIT(p, q, w) { u = p; v = fe_mul(q, w); p = fe_add(u, v); q = fe_sub(u, v); }
static inline void kern8(fe *x, long j, long h, fe t, fe w8, fe I4, int inv) {
    fe a0 = x[j], a1 = x[j + h], a2 = x[j + 2 * h], a3 = x[j + 3 * h], a4 = x[j + 4 * h], a5 = x[j + 5 * h], a6 = x[j + 6 * h], a7 = x[j + 7 * h];
    fe t2 = fe_mul(t, t), t4 = fe_mul(t2, t2), tw1 = fe_mul(t, w8), tw2 = fe_mul(t, I4), tw3 = fe_mul(tw1, I4), s1 = fe_mul(t2, I4);
    fe u, v;
    if (!inv) {
        DIF(a0, a4, t) DIF(a1, a5, tw1) DIF(a2, a6, tw2) DIF(a3, a7, tw3)            // half-size 4h
        DIF(a0, a2, t2) DIF(a1, a3, s1) DIF(a4, a6, t2) DIF(a5, a7, s1)              // half-size 2h
        DIF(a0, a1, t4) DIF(a2, a3, t4) DIF(a4, a5, t4) DIF(a6, a7, t4)              // half-size h
    } else {
        DIT(a0, a1, t4) DIT(a2, a3, t4) DIT(a4, a5, t4) DIT(a6, a7, t4)
        DIT(a0, a2, t2) DIT(a1, a3, s1) DIT(a4, a6, t2) DIT(a5, a7, s1)
        DIT(a0, a4, t) DIT(a1, a5, tw1) DIT(a2, a6, tw2) DIT(a3, a7, tw3)
    }
    x[j] = a0; x[j + h] = a1; x[j + 2 * h] = a2; x[j + 3 * h] = a3; x[j + 4 * h] = a4; x[j + 5 * h] = a5; x[j + 6 * h] = a6; x[j + 7 * h] = a7;
}
#define CH_HEX    170  // per 16 elements, 4 levels: 16 loads, 16 stores, 32 data mul, 15 twiddle mul (step, 7 for t w16^c, t^2 and 3 for t^2 w8^c, t^4, t^4 I4, t^8), 64 add/sub, 16 address, 3 loop; +8 spare
static inline void kern16(fe *x, long j, long h, fe t, fe w16, fe w8, fe I4, int inv) {
    fe a[16], u, v;
    for (int c = 0; c < 16; c++) a[c] = x[j + c * h];
    fe tw[8], s8[4], s4[2], t8;
    tw[0] = t; for (int c = 1; c < 8; c++) tw[c] = fe_mul(tw[c - 1], w16);
    s8[0] = fe_mul(t, t); for (int c = 1; c < 4; c++) s8[c] = fe_mul(s8[c - 1], w8);
    s4[0] = fe_mul(s8[0], s8[0]); s4[1] = fe_mul(s4[0], I4);
    t8 = fe_mul(s4[0], s4[0]);
    if (!inv) {
        for (int c = 0; c < 8; c++) DIF(a[c], a[c + 8], tw[c])
        for (int b = 0; b < 16; b += 8) for (int c = 0; c < 4; c++) DIF(a[b + c], a[b + c + 4], s8[c])
        for (int b = 0; b < 16; b += 4) for (int c = 0; c < 2; c++) DIF(a[b + c], a[b + c + 2], s4[c])
        for (int b = 0; b < 16; b += 2) DIF(a[b], a[b + 1], t8)
    } else {
        for (int b = 0; b < 16; b += 2) DIT(a[b], a[b + 1], t8)
        for (int b = 0; b < 16; b += 4) for (int c = 0; c < 2; c++) DIT(a[b + c], a[b + c + 2], s4[c])
        for (int b = 0; b < 16; b += 8) for (int c = 0; c < 4; c++) DIT(a[b + c], a[b + c + 4], s8[c])
        for (int c = 0; c < 8; c++) DIT(a[c], a[c + 8], tw[c])
    }
    for (int c = 0; c < 16; c++) x[j + c * h] = a[c];
}
static inline void kern4(fe *x, long j, long h, fe t, fe I4, int inv) {
    fe a0 = x[j], a1 = x[j + h], a2 = x[j + 2 * h], a3 = x[j + 3 * h];
    fe t2 = fe_mul(t, t), tw1 = fe_mul(t, I4);
    fe u, v;
    if (!inv) { DIF(a0, a2, t) DIF(a1, a3, tw1) DIF(a0, a1, t2) DIF(a2, a3, t2) }
    else { DIT(a0, a1, t2) DIT(a2, a3, t2) DIT(a0, a2, t) DIT(a1, a3, tw1) }
    x[j] = a0; x[j + h] = a1; x[j + 2 * h] = a2; x[j + 3 * h] = a3;
}
static inline void kern2(fe *x, long j, long h, fe t, int inv) {
    fe a0 = x[j], a1 = x[j + h], u, v;
    if (!inv) DIF(a0, a1, t) else DIT(a0, a1, t)
    x[j] = a0; x[j + h] = a1;
}
#undef DIF
#undef DIT
static inline void kern(int R, fe *x, long j, long h, fe t, fe w16, fe w8, fe I4, int inv) {
    if (R == 16) kern16(x, j, h, t, w16, w8, I4, inv); else if (R == 8) kern8(x, j, h, t, w8, I4, inv);
    else if (R == 4) kern4(x, j, h, t, I4, inv); else kern2(x, j, h, t, inv);
}
// stage plan for 2^lg: radices (16, 8, 4, 2) from the top, minimizing the kernel charge per element
// (CH_HEX / 16, CH_OCT / 8, CH_QUAD / 4, CH_BFLY / 2 per stage), ties to fewer stages; returns the stage count
static int ntt_plan(int lg, int *R) {
    static const int lr[4] = {4, 3, 2, 1}; const long ch[4] = {CH_HEX * 2, CH_OCT * 4, CH_QUAD * 8, CH_BFLY * 16};   // per 32 elements
    long best[40]; int cnt[40], pick[40]; best[0] = 0; cnt[0] = 0;
    for (int l = 1; l <= lg; l++) {
        best[l] = -1;
        for (int k = 0; k < 4; k++) if (lr[k] <= l && best[l - lr[k]] >= 0) {
            long c = best[l - lr[k]] + ch[k]; int n = cnt[l - lr[k]] + 1;
            if (best[l] < 0 || c < best[l] || (c == best[l] && n < cnt[l])) { best[l] = c; cnt[l] = n; pick[l] = k; }
        }
    }
    int n = 0; for (int l = lg; l > 0; l -= lr[pick[l]]) R[n++] = 1 << lr[pick[l]];
    // largest radices first (top stages)
    for (int i = 0; i < n; i++) for (int j2 = i + 1; j2 < n; j2++) if (R[j2] > R[i]) { int t = R[i]; R[i] = R[j2]; R[j2] = t; }
    return n;
}
// one stage of radix R in {2, 4, 8} over blocks of R h, on Lt elements (nb consecutive transforms of the same
// length are one batch); wR = w_{Rh} (or its inverse). In parallel mode the groups * h kernel iterations, taken in
// order (group, j), are split into 64 contiguous ranges; a range starting inside a group starts its twiddle at
// wR^j0 by one short exponentiation, and the twiddle restarts at 1 at every group boundary.
static void ntt_stage(fe *a, long Lt, int R, long h, fe wR, fe w16, fe w8, fe I4, int inv) {
    long groups = Lt / (R * h), T = groups * h;
    int lh = 0; while ((1L << lh) < h) lh++;
    if (Lt <= NTT_SEQ_MAX) {
        for (long g = 0; g < groups; g++) { fe *x = a + g * R * h; fe t = ONE; for (long j = 0; j < h; j++) { kern(R, x, j, h, t, w16, w8, I4, inv); t = fe_mul(t, wR); } }
    } else {
        dispatch_apply(64, DISPATCH_APPLY_AUTO, ^(size_t bi) {
            long i0 = (long)bi * (T / 64), i1 = (bi == 63) ? T : i0 + T / 64;
            long g = i0 / h, j = i0 % h;
            fe t = j ? fe_pow_u64(wR, (uint64_t)j) : ONE;
            for (long i = i0; i < i1; i++) {
                kern(R, a + g * R * h, j, h, t, w16, w8, I4, inv);
                if (++j == h) { j = 0; g++; t = ONE; } else t = fe_mul(t, wR);
            }
        });
        OPS += 64ULL * (8 * lh + 16);                 // block starts
    }
    OPS += (unsigned long long)(R == 16 ? CH_HEX * (Lt / 16) : R == 8 ? CH_OCT * (Lt / 8) : R == 4 ? CH_QUAD * (Lt / 4) : CH_BFLY * (Lt / 2)) + CH_CALL;
}
// nb consecutive transforms of length M = 2^logM each (the inverse includes the scaling by M^-1)
static void ntt_batch(fe *a, long M, long nb, int inverse) {
    if (M > LMAX) { fprintf(stderr, "transform length %ld exceeds LMAX %ld\n", M, LMAX); exit(3); }
    int logM = 0; while ((1L << logM) < M) logM++;
    long Lt = M * nb;
    const fe *RT = inverse ? IROOT : ROOT;
    int R[40], ns = ntt_plan(logM, R), lb[40];
    for (int i = 0, l = logM; i < ns; i++) { lb[i] = l; l -= (R[i] == 16 ? 4 : R[i] == 8 ? 3 : R[i] == 4 ? 2 : 1); }   // block size 2^lb[i]
    fe w16 = RT[4], w8 = RT[3], I4 = RT[2];
    if (!inverse) {
        for (int i = 0; i < ns; i++) ntt_stage(a, Lt, R[i], (1L << lb[i]) / R[i], RT[lb[i]], w16, w8, I4, 0);
    } else {
        for (int i = ns - 1; i >= 0; i--) ntt_stage(a, Lt, R[i], (1L << lb[i]) / R[i], RT[lb[i]], w16, w8, I4, 1);
        fe linv = fe_pow_plain_exp(fe_from_u64((uint64_t)M), (fe){{P.v[0] - 2, P.v[1], P.v[2], P.v[3]}});
        PAR_FOR(Lt, a[i] = fe_mul(a[i], linv));
        OPS += (unsigned long long)CH_SCALE * Lt + 2 * 256 * 3 + CH_CALL;
    }
}
static void ntt(fe *a, long L, int inverse) { ntt_batch(a, L, 1, inverse); }
static long pow2ceil(long x) { long L = 1; while (L < x) L <<= 1; return L; }
#include "ntt3.h"

// load a into buffer of length L (zero padded); charges copy + zero
static fe *ntt_load(const poly *a, long L) {
    fe *b = xalloc(sizeof(fe) * L);
    memcpy(b, a->c, sizeof(fe) * a->n); memset(b + a->n, 0, sizeof(fe) * (L - a->n));
    OPS += (unsigned long long)CH_COPY * a->n + (unsigned long long)CH_ZERO * (L - a->n) + CH_CALL;
    return b;
}

// schoolbook product (small sizes)
static poly poly_mul_school(const poly *a, const poly *b) {
    if (a->n == 0 || b->n == 0) { OPS += CH_CALL; return poly_new(1); }
    poly r = poly_new(a->n + b->n - 1); r.n = a->n + b->n - 1;
    memset(r.c, 0, sizeof(fe) * r.n);
    for (long i = 0; i < a->n; i++) for (long j = 0; j < b->n; j++) r.c[i + j] = fe_add(r.c[i + j], fe_mul(a->c[i], b->c[j]));
    OPS += (unsigned long long)CH_SCHOOL * a->n * b->n + (unsigned long long)CH_ZERO * r.n + CH_CALL;
    poly_trim(&r); return r;
}
#define SCHOOL_MAX 48   // schoolbook below this size: Newton steps, divisions (divisor or quotient), plain Euclid
#define MUL_SCHOOL 12   // poly_mul: schoolbook iff the smaller operand has at most this many coefficients
static poly poly_mul(const poly *a, const poly *b) {
    if (a->n == 0 || b->n == 0) { OPS += CH_CALL; return poly_new(1); }
    long m = a->n < b->n ? a->n : b->n;
    if (m <= MUL_SCHOOL) return poly_mul_school(a, b);
    long rn = a->n + b->n - 1, L = pick_len(rn);
    fe *x = ntt_load(a, L), *y = ntt_load(b, L);
    ntt_any(x, L, 0); ntt_any(y, L, 0);
    PAR_FOR(L, x[i] = fe_mul(x[i], y[i]));
    OPS += (unsigned long long)CH_PMUL * L;
    xfree(y, sizeof(fe) * L);
    ntt_any(x, L, 1);
    poly r; r.c = xshrink(x, sizeof(fe) * L, sizeof(fe) * rn); r.n = rn; r.cap = rn;   // result in place
    poly_trim(&r); return r;
}
static poly poly_sqr(const poly *a) {
    if (a->n == 0) { OPS += CH_CALL; return poly_new(1); }
    if (a->n <= SCHOOL_MAX) return poly_mul_school(a, a);
    long rn = 2 * a->n - 1, L = pick_len(rn);
    fe *x = ntt_load(a, L); ntt_any(x, L, 0);
    PAR_FOR(L, x[i] = fe_mul(x[i], x[i])); OPS += (unsigned long long)CH_PSQR * L;
    ntt_any(x, L, 1);
    poly r; r.c = xshrink(x, sizeof(fe) * L, sizeof(fe) * rn); r.n = rn; r.cap = rn; poly_trim(&r); return r;
}
// fifth power via one forward and one inverse transform
static poly poly_pow5(const poly *a) {
    if (a->n <= 1) { poly r = poly_new(1); if (a->n == 1) { fe s = fe_mul(a->c[0], a->c[0]); s = fe_mul(s, s); r.c[0] = fe_mul(s, a->c[0]); r.n = 1; } OPS += CH_CALL + 8; return r; }
    long rn = 5 * (a->n - 1) + 1, L = pick_len(rn);
    fe *x = ntt_load(a, L); ntt_any(x, L, 0);
    PAR_FOR(L, { fe s = fe_mul(x[i], x[i]); s = fe_mul(s, s); x[i] = fe_mul(s, x[i]); });
    OPS += (unsigned long long)CH_PPOW5 * L;
    ntt_any(x, L, 1);
    poly r; r.c = xshrink(x, sizeof(fe) * L, sizeof(fe) * rn); r.n = rn; r.cap = rn; poly_trim(&r); return r;
}
// r = a + s*b (s scalar), new poly
static poly poly_axpy(const poly *a, fe s, const poly *b) {
    long n = a->n > b->n ? a->n : b->n;
    poly r = poly_new(n); r.n = n;
    for (long i = 0; i < n; i++) {
        fe x = i < a->n ? a->c[i] : (fe){{0,0,0,0}};
        fe y = i < b->n ? fe_mul(s, b->c[i]) : (fe){{0,0,0,0}};
        r.c[i] = fe_add(x, y);
    }
    OPS += (unsigned long long)CH_AXPY * n + CH_CALL; poly_trim(&r); return r;
}
static poly poly_sub(const poly *a, const poly *b) {
    long n = a->n > b->n ? a->n : b->n;
    poly r = poly_new(n); r.n = n;
    for (long i = 0; i < n; i++) {
        fe x = i < a->n ? a->c[i] : (fe){{0,0,0,0}};
        fe y = i < b->n ? b->c[i] : (fe){{0,0,0,0}};
        r.c[i] = fe_sub(x, y);
    }
    OPS += (unsigned long long)CH_ADDV * n + CH_CALL; poly_trim(&r); return r;
}
static poly poly_add(const poly *a, const poly *b) {
    long n = a->n > b->n ? a->n : b->n;
    poly r = poly_new(n); r.n = n;
    for (long i = 0; i < n; i++) {
        fe x = i < a->n ? a->c[i] : (fe){{0,0,0,0}};
        fe y = i < b->n ? b->c[i] : (fe){{0,0,0,0}};
        r.c[i] = fe_add(x, y);
    }
    OPS += (unsigned long long)CH_ADDV * n + CH_CALL; poly_trim(&r); return r;
}
static poly poly_scale(const poly *a, fe s) {
    poly r = poly_new(a->n); r.n = a->n;
    for (long i = 0; i < a->n; i++) r.c[i] = fe_mul(a->c[i], s);
    OPS += (unsigned long long)CH_SCALE * a->n + CH_CALL; poly_trim(&r); return r;
}
static fe fe_inv(fe a) { OPS += 255 * 2 * 3 + 16; return fe_pow_plain_exp(a, (fe){{P.v[0] - 2, P.v[1], P.v[2], P.v[3]}}); }
// a div x^k (shift down)
static poly poly_shr(const poly *a, long k) {
    if (a->n <= k) { OPS += CH_CALL; return poly_new(1); }
    poly r = poly_new(a->n - k); r.n = a->n - k; memcpy(r.c, a->c + k, sizeof(fe) * r.n);
    OPS += (unsigned long long)CH_COPY * r.n + CH_CALL; return r;
}
// a mod x^k (truncate)
static poly poly_trunc(const poly *a, long k) {
    long n = a->n < k ? a->n : k; poly r = poly_new(n); r.n = n; memcpy(r.c, a->c, sizeof(fe) * n);
    OPS += (unsigned long long)CH_COPY * n + CH_CALL; poly_trim(&r); return r;
}
// reverse of a padded to length m (coefficients i -> m-1-i)
static poly poly_rev(const poly *a, long m) {
    poly r = poly_new(m); r.n = m;
    for (long i = 0; i < m; i++) r.c[i] = (m - 1 - i < a->n) ? a->c[m - 1 - i] : (fe){{0,0,0,0}};
    OPS += (unsigned long long)CH_COPY * m + CH_CALL; poly_trim(&r); return r;
}
// inverse of a modulo x^k (a(0) != 0). Newton step from cur to m = min(2 cur, k) coefficients:
// h = (a mod x^m) * g computed cyclically mod x^Lc - 1, Lc = pick_len(m) (only coefficients cur..m-1 are
// used; the wrapped part lands below cur, where h = 1, 0, ..., 0 is known); then g += -x^cur (g * h_hi mod x^(m-cur)),
// the product g * h_hi (degree < m - 1) again at length Lc with no wrap. Two buffers of length Lc.
static poly poly_inv_series(const poly *a, long k) {
    poly g = poly_new(k); g.c[0] = fe_inv(a->c[0]); g.n = 1;
    long cur = 1;
    while (cur < k) {
        long m = 2 * cur < k ? 2 * cur : k, Lc = pick_len(m);
        if (m <= SCHOOL_MAX) {   // small sizes: schoolbook step
            poly at = poly_trunc(a, m); poly ag = poly_mul_school(&at, &g);
            poly hh = poly_new(m - cur); hh.n = m - cur;
            for (long i = cur; i < m; i++) hh.c[i - cur] = i < ag.n ? ag.c[i] : (fe){{0,0,0,0}};
            OPS += (unsigned long long)CH_COPY * (m - cur); poly_trim(&hh);
            poly gh = poly_mul_school(&g, &hh);
            for (long i = cur; i < m; i++) g.c[i] = (i - cur < gh.n) ? fe_neg(gh.c[i - cur]) : (fe){{0,0,0,0}};
            OPS += (unsigned long long)CH_COPY * (m - cur); g.n = m;
            poly_free(&at); poly_free(&ag); poly_free(&hh); poly_free(&gh);
        } else {
            fe *x = xalloc(sizeof(fe) * Lc), *y = xalloc(sizeof(fe) * Lc);
            long an = a->n < m ? a->n : m;
            memcpy(x, a->c, sizeof(fe) * an); memset(x + an, 0, sizeof(fe) * (Lc - an));
            memcpy(y, g.c, sizeof(fe) * g.n); memset(y + g.n, 0, sizeof(fe) * (Lc - g.n));
            OPS += (unsigned long long)CH_COPY * (an + g.n) + (unsigned long long)CH_ZERO * (2 * Lc - an - g.n);
            ntt_any(x, Lc, 0); ntt_any(y, Lc, 0);
            PAR_FOR(Lc, x[i] = fe_mul(x[i], y[i])); OPS += (unsigned long long)CH_PMUL * Lc;
            ntt_any(x, Lc, 1);
            // x <- h_hi (coefficients cur..m-1) at the bottom, zero padded; y keeps NTT(g)
            for (long i = 0; i < m - cur; i++) x[i] = x[cur + i];
            memset(x + (m - cur), 0, sizeof(fe) * (Lc - (m - cur)));
            OPS += (unsigned long long)CH_COPY * (m - cur) + (unsigned long long)CH_ZERO * (Lc - (m - cur));
            ntt_any(x, Lc, 0);
            PAR_FOR(Lc, x[i] = fe_mul(x[i], y[i])); OPS += (unsigned long long)CH_PMUL * Lc;
            ntt_any(x, Lc, 1);
            for (long i = cur; i < m; i++) g.c[i] = fe_neg(x[i - cur]);
            OPS += (unsigned long long)CH_SCALE * (m - cur); g.n = m;
            xfree(x, sizeof(fe) * Lc); xfree(y, sizeof(fe) * Lc);
        }
        cur = m; OPS += CH_CALL;
    }
    poly_trim(&g);
    return g;
}
// quotient and remainder of a by b (b != 0)
static void poly_divmod(const poly *a, const poly *b, poly *q, poly *r) {
    if (a->n < b->n) { *q = poly_new(1); *r = poly_copy(a); return; }
    long m = a->n - b->n + 1;   // quotient length
    if (b->n <= SCHOOL_MAX || m <= SCHOOL_MAX) {
        poly rr = poly_copy(a); poly qq = poly_new(m); qq.n = m;
        fe li = fe_inv(b->c[b->n - 1]);
        for (long i = m - 1; i >= 0; i--) {
            fe c = fe_mul(rr.c[i + b->n - 1], li); qq.c[i] = c;
            for (long j = 0; j < b->n; j++) rr.c[i + j] = fe_sub(rr.c[i + j], fe_mul(c, b->c[j]));
        }
        OPS += (unsigned long long)CH_AXPY * m * b->n + (unsigned long long)(CH_PMUL) * m + CH_CALL;
        rr.n = b->n - 1; poly_trim(&rr); poly_trim(&qq); *q = qq; *r = rr; return;
    }
    poly ra = poly_rev(a, a->n), rb = poly_rev(b, b->n);
    poly ib = poly_inv_series(&rb, m);
    poly rat = poly_trunc(&ra, m);
    poly t = poly_mul(&rat, &ib); poly tt = poly_trunc(&t, m);
    poly qq = poly_rev(&tt, m);
    poly bq = poly_mul(b, &qq);
    poly rr = poly_sub(a, &bq);
    poly_free(&ra); poly_free(&rb); poly_free(&ib); poly_free(&rat); poly_free(&t); poly_free(&tt); poly_free(&bq);
    *q = qq; *r = rr;
}
```

### A.3 `ntt3.h` (SHA-256 546ae548a0b26287a630d6144c30b25d8a9a8d1d227ee27effedd3ca89fdfdc0)

```c
// Transforms of length L = 2^k or 3 * 2^k (Pallas: 3 * 2^32 divides p - 1).
// A length 3M transform (M = 2^k) is one radix-3 decimation-in-frequency stage over blocks of M followed by
// the three length-M transforms of the blocks as one batch (ntt_batch); block s then holds the values at
// w_L^(3k+s), k < M, in the (bit-reversed) order of ntt.
// The inverse runs the batch of three inverse length-M transforms and then the inverse radix-3 stage, which also
// multiplies by 3^-1 (ntt already multiplies by M^-1). Pointwise products only need the same layout on
// both operands, and the transform is exact evaluation at all L-th roots of unity, so cyclic products
// mod x^L - 1 behave as for powers of two.
// Included from poly.h after ntt, PAR_FOR and pow2ceil.
#pragma once

#define CH_R3F     28  // per 3 elements: 3 loads, 3 stores, 5 mul (w3*d, 2 twiddles, 2 twiddle steps), 7 add/sub, 3 address, 3 loop; +4 spare
#define CH_R3I     30  // per 3 elements: 3 loads, 3 stores, 6 mul (+ the 3^-1 of z0), 7 add/sub, 3 address, 3 loop; +5 spare

static fe ROOT3[33], IROOT3[33];   // ROOT3[k] primitive (3 * 2^k)-th root of unity, IROOT3[k] its inverse
static fe W3, W3I, INV3;           // W3 = ROOT3[0], a primitive cube root; W3I = W3^-1; INV3 = 3^-1
static void ntt3_init(void) {
    ROOT3[32] = fe_pow_plain_exp(fe_from_u64(5), fe_plain_from_hex("000000001555555555555555555555555555555560c232feadc45309330f104f"));   // (p-1) / (3 * 2^32)
    for (int k = 31; k >= 0; k--) ROOT3[k] = fe_mul(ROOT3[k + 1], ROOT3[k + 1]);
    fe pm2 = {{P.v[0] - 2, P.v[1], P.v[2], P.v[3]}};
    for (int k = 0; k <= 32; k++) IROOT3[k] = fe_pow_plain_exp(ROOT3[k], pm2);
    W3 = ROOT3[0]; W3I = IROOT3[0]; INV3 = fe_pow_plain_exp(fe_from_u64(3), pm2);
    // checks: W3 has order 3, ROOT3[k]^3 = ROOT[k] (so the block transforms use w_L^3)
    if (fe_eq(W3, ONE) || !fe_eq(fe_mul(fe_mul(W3, W3), W3), ONE)) { fprintf(stderr, "cube root check failed\n"); exit(1); }
    for (int k = 0; k <= 32; k++) if (!fe_eq(fe_mul(fe_mul(ROOT3[k], ROOT3[k]), ROOT3[k]), ROOT[k])) { fprintf(stderr, "root3 check failed\n"); exit(1); }
    OPS += 34ULL * 2 * 256 * 3 + 2 * 256 * 3 + 2000;
}
// smallest admissible transform length >= n
// (3 * 2^k only from 6144 on: below that the three short block transforms cost more than one of length 2^(k+2))
#define LEN3_MIN 6144
static long pick_len(long n) {
    long a = pow2ceil(n), b = 3 * pow2ceil((n + 2) / 3);
    return (b >= LEN3_MIN && b < a) ? b : a;
}
static void rad3_stage(fe *a, long M, int k, int inverse) {
    fe w = inverse ? IROOT3[k] : ROOT3[k], w3 = inverse ? W3I : W3, s0 = inverse ? INV3 : ONE;
    fe w2 = fe_mul(w, w);
    dispatch_apply(64, DISPATCH_APPLY_AUTO, ^(size_t blk) {
        long lo = (long)blk * (M / 64), hi = (blk == 63) ? M : lo + M / 64; if (M < 64) { if (blk) return; lo = 0; hi = M; }
        fe t1 = fe_mul(fe_pow_u64(w, (uint64_t)lo), s0), t2 = fe_mul(fe_pow_u64(w2, (uint64_t)lo), s0);
        fe *x0 = a, *x1 = a + M, *x2 = a + 2 * M;
        if (!inverse) {
            for (long j = lo; j < hi; j++) {
                fe a0 = x0[j], a1 = x1[j], a2 = x2[j];
                fe m = fe_mul(w3, fe_sub(a1, a2));
                x0[j] = fe_add(a0, fe_add(a1, a2));
                x1[j] = fe_mul(fe_add(fe_sub(a0, a2), m), t1);
                x2[j] = fe_mul(fe_sub(fe_sub(a0, a1), m), t2);
                t1 = fe_mul(t1, w); t2 = fe_mul(t2, w2);
            }
        } else {
            for (long j = lo; j < hi; j++) {
                fe z0 = fe_mul(x0[j], s0), z1 = fe_mul(x1[j], t1), z2 = fe_mul(x2[j], t2);
                fe m = fe_mul(w3, fe_sub(z1, z2));
                x0[j] = fe_add(z0, fe_add(z1, z2));
                x1[j] = fe_add(fe_sub(z0, z2), m);
                x2[j] = fe_sub(fe_sub(z0, z1), m);
                t1 = fe_mul(t1, w); t2 = fe_mul(t2, w2);
            }
        }
    });
    OPS += (unsigned long long)(inverse ? CH_R3I : CH_R3F) * M + 64ULL * (16 * k + 40) + CH_CALL;   // pass + the 64 block starts
}
// transform of any admissible length
static void ntt_any(fe *a, long L, int inverse) {
    if ((L & (L - 1)) == 0) { ntt(a, L, inverse); return; }
    long M = L / 3; int k = 0; while ((1L << k) < M) k++;
    if (3 * M != L || (1L << k) != M) { fprintf(stderr, "inadmissible transform length %ld\n", L); exit(3); }
    if (!inverse) { rad3_stage(a, M, k, 0); ntt_batch(a, M, 3, 0); }
    else { ntt_batch(a, M, 3, 1); rad3_stage(a, M, k, 1); }
}
```

### A.4 `gcd2.h` (SHA-256 f8d4724d2c508e6b781eefaa3395edb7b9a0aeac639231d0b76cf15a84f4559c)

```c
// Memory-lean half-gcd and gcd (after poly.h). Every function here CONSUMES the polynomials passed by pointer
// unless marked const. Products whose true degree is known to be below the transform length are formed
// cyclically mod x^L - 1, which is exact; the degree facts used are those of Lemma H (proof.md, Section 8.3).
#pragma once
#include "poly.h"
#ifndef CYC_MIN
#define CYC_MIN 8
#endif

#define CH_PMAC   15  // T = T*A + U*B: 4 loads, 2 mul, add, store, 4 address, 3 loop
#define CH_PMACC  13  // U = U + V*A: 3 loads, mul, add, store, 3 address, 3 loop
#define CH_MAT2   24  // (x, y) <- (S00 x + S01 y, S10 x + S11 y): 6 loads, 4 mul, 2 add, 2 stores, 6 address, 3 loop; +1
#define CH_OUTER_C 6   // schoolbook outer loop: counter, compare, branch, row pointer, load of the multiplier, 1 spare
#define CH_REM    15  // r_i = a_i - x_i + a_{i+L}: 3 loads, 2 add/sub, store, 4 address, length test (2), 3 loop

typedef struct { poly m[2][2]; } mat;



static void poly_fit(poly *p) {          // release unused capacity (after trimming)
    long n = p->n > 0 ? p->n : 1;
    if (p->cap > n) { p->c = xshrink(p->c, sizeof(fe) * p->cap, sizeof(fe) * n); p->cap = n; }
}
static poly poly_zero(void) { poly z = poly_new(1); return z; }
static poly poly_one(void) { poly z = poly_new(1); z.c[0] = ONE; z.n = 1; return z; }
static mat mat_id(void) {
    mat M; M.m[0][0] = poly_one(); M.m[0][1] = poly_zero(); M.m[1][0] = poly_zero(); M.m[1][1] = poly_one();
    OPS += CH_CALL; return M;
}
static void mat_free(mat *M) { for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) poly_free(&M->m[i][j]); }
static int mat_is_id(const mat *M) {
    return M->m[0][1].n == 0 && M->m[1][0].n == 0 && M->m[0][0].n == 1 && M->m[1][1].n == 1 &&
           fe_eq(M->m[0][0].c[0], ONE) && fe_eq(M->m[1][1].c[0], ONE);
}
// load p (n <= L) into a fresh length-L buffer, zero padded, transform it, and free p
static fe *load_fwd(poly *p, long L) {
    if (p->n > L) { fprintf(stderr, "load_fwd: %ld > %ld\n", p->n, L); exit(4); }
    fe *x = ntt_load(p, L); poly_free(p); ntt_any(x, L, 0); return x;
}
// inverse transform x (length L) and keep its first n coefficients as a fitted polynomial
static poly unload_inv(fe *x, long L, long n) {
    ntt_any(x, L, 1);
    poly r; r.c = xshrink(x, sizeof(fe) * L, sizeof(fe) * (n > 0 ? n : 1)); r.cap = n > 0 ? n : 1; r.n = n;
    poly_trim(&r); poly_fit(&r); OPS += CH_CALL; return r;
}

// (c, d) = R (a, b), consuming R, a, b. L must exceed deg c and deg d and be at least every input size.
// Buffers: A, B, T, U (4 L); a, b and the entries of R are released as soon as they are transformed.
static void mat_apply_dir(mat *R, poly *a, poly *b, poly *c, poly *d);
static long mat_maxn(const mat *M);
static void mat_apply_cyc(mat *R, poly *a, poly *b, long L, poly *c, poly *d) {
    if (mat_is_id(R)) {
        mat_free(R); *c = *a; *d = *b; OPS += CH_CALL; return; }
    if (mat_maxn(R) <= CYC_MIN) {
        mat_apply_dir(R, a, b, c, d); return; }
    fe *A = load_fwd(a, L), *B = load_fwd(b, L);
    fe *T = load_fwd(&R->m[0][0], L), *U = load_fwd(&R->m[0][1], L);
    PAR_FOR(L, T[i] = fe_add(fe_mul(T[i], A[i]), fe_mul(U[i], B[i]))); OPS += (unsigned long long)CH_PMAC * L;
    xfree(U, sizeof(fe) * L);
    U = load_fwd(&R->m[1][1], L);
    PAR_FOR(L, U[i] = fe_mul(U[i], B[i])); OPS += (unsigned long long)CH_PMUL * L;
    xfree(B, sizeof(fe) * L);
    fe *V = load_fwd(&R->m[1][0], L);
    PAR_FOR(L, U[i] = fe_add(U[i], fe_mul(V[i], A[i]))); OPS += (unsigned long long)CH_PMACC * L;
    xfree(V, sizeof(fe) * L); xfree(A, sizeof(fe) * L);
    *c = unload_inv(T, L, L); *d = unload_inv(U, L, L);
    OPS += CH_CALL;
}


// direct (c, d) = R (a, b) for entries of at most 48 coefficients, by schoolbook accumulation into c and d (no
// temporaries), consuming R, a, b
static void mat_apply_dir(mat *R, poly *a, poly *b, poly *c, poly *d) {
    long e = 0; for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) if (R->m[i][j].n > e) e = R->m[i][j].n;
    long nv = a->n > b->n ? a->n : b->n, n = nv + (e > 0 ? e : 1) - 1;
    poly *src[2] = {a, b}; poly *out[2] = {c, d};
    for (int i = 0; i < 2; i++) {
        poly o = poly_new(n); o.n = n; memset(o.c, 0, sizeof(fe) * n); OPS += (unsigned long long)CH_ZERO * n + CH_CALL;
        for (int j = 0; j < 2; j++) {
            const poly *r = &R->m[i][j], *v = src[j];
            for (long k = 0; k < r->n; k++) for (long t = 0; t < v->n; t++) o.c[k + t] = fe_add(o.c[k + t], fe_mul(r->c[k], v->c[t]));
            OPS += (unsigned long long)CH_SCHOOL * r->n * v->n + (unsigned long long)CH_OUTER_C * r->n;
        }
        poly_trim(&o); *out[i] = o;
    }
    mat_free(R); poly_free(a); poly_free(b); poly_fit(c); poly_fit(d);
}
static mat mat_mul_dir(mat *A, mat *B) {
    mat C;
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {
        poly x = poly_mul(&A->m[i][0], &B->m[0][j]), y = poly_mul(&A->m[i][1], &B->m[1][j]);
        C.m[i][j] = poly_add(&x, &y); poly_free(&x); poly_free(&y); poly_fit(&C.m[i][j]);
    }
    mat_free(A); mat_free(B); return C;
}
static long mat_maxn(const mat *M) { long e = 0; for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) if (M->m[i][j].n > e) e = M->m[i][j].n; return e; }

// Q R for Q = [[0, 1], [1, -q]], consuming R (not q): [[R10, R11], [R00 - q R10, R01 - q R11]]
static mat mat_qmul(const poly *q, mat *R) {
    mat O; O.m[0][0] = R->m[1][0]; O.m[0][1] = R->m[1][1];
    for (int j = 0; j < 2; j++) {
        poly t = poly_mul(q, &O.m[0][j]);
        O.m[1][j] = poly_sub(&R->m[0][j], &t); poly_free(&t); poly_free(&R->m[0][j]); poly_fit(&O.m[1][j]);
    }
    OPS += CH_CALL; return O;
}

// S QR cyclically at length L (L must exceed the degree of every entry of the product and be at least
// every input size), consuming S and QR. S is transformed once; QR column by column, combined in place.
static mat mat_mul_dir(mat *A, mat *B);
static mat mat_mul_cyc(mat *S, mat *QR, long L, long rn) {
    if (mat_maxn(S) <= CYC_MIN || mat_maxn(QR) <= CYC_MIN) return mat_mul_dir(S, QR);
    fe *Sh[2][2];
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) Sh[i][j] = load_fwd(&S->m[i][j], L);
    mat O;
    for (int j = 0; j < 2; j++) {
        fe *X = load_fwd(&QR->m[0][j], L), *Y = load_fwd(&QR->m[1][j], L);
        fe *s00 = Sh[0][0], *s01 = Sh[0][1], *s10 = Sh[1][0], *s11 = Sh[1][1];
        PAR_FOR(L, { fe x = X[i]; fe y = Y[i]; X[i] = fe_add(fe_mul(s00[i], x), fe_mul(s01[i], y));
                     Y[i] = fe_add(fe_mul(s10[i], x), fe_mul(s11[i], y)); });
        OPS += (unsigned long long)CH_MAT2 * L;
        O.m[0][j] = unload_inv(X, L, rn); O.m[1][j] = unload_inv(Y, L, rn);
    }
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) xfree(Sh[i][j], sizeof(fe) * L);
    OPS += CH_CALL; return O;
}

// low k coefficients of a * b (const inputs)
static poly poly_mullow(const poly *a, const poly *b, long k) {
    long na = a->n < k ? a->n : k, nb = b->n < k ? b->n : k;
    if (na == 0 || nb == 0) { OPS += CH_CALL; return poly_new(1); }
    if (na <= MUL_SCHOOL || nb <= MUL_SCHOOL) {
        poly at = poly_trunc(a, k), bt = poly_trunc(b, k);
        poly t = poly_mul_school(&at, &bt); poly_free(&at); poly_free(&bt);
        if (t.n > k) t.n = k;
        poly_trim(&t); poly_fit(&t); return t;
    }
    long rn = na + nb - 1, L = pick_len(rn);
    fe *x = xalloc(sizeof(fe) * L), *y = xalloc(sizeof(fe) * L);
    memcpy(x, a->c, sizeof(fe) * na); memset(x + na, 0, sizeof(fe) * (L - na));
    memcpy(y, b->c, sizeof(fe) * nb); memset(y + nb, 0, sizeof(fe) * (L - nb));
    OPS += (unsigned long long)CH_COPY * (na + nb) + (unsigned long long)CH_ZERO * (2 * L - na - nb) + CH_CALL;
    ntt_any(x, L, 0); ntt_any(y, L, 0);
    PAR_FOR(L, x[i] = fe_mul(x[i], y[i])); OPS += (unsigned long long)CH_PMUL * L;
    xfree(y, sizeof(fe) * L);
    return unload_inv(x, L, k < rn ? k : rn);
}

// quotient (if want_q) and remainder of a by b (const inputs, b != 0)
static void poly_divmod2(const poly *a, const poly *b, int want_q, poly *q, poly *r) {
    long na = a->n, nb = b->n;
    if (na < nb) { *q = poly_new(1); *r = poly_copy(a); poly_fit(r); return; }
    long m = na - nb + 1;
    if (nb <= SCHOOL_MAX || m <= SCHOOL_MAX) {
        poly_divmod(a, b, q, r); poly_fit(r); poly_fit(q);
        if (!want_q) { poly_free(q); *q = poly_new(1); }
        return;
    }
    // quotient from the top m coefficients: rev(q) = rev(a)_m * rev(b)^-1 mod x^m
    poly rat = poly_new(m); rat.n = m;
    for (long i = 0; i < m; i++) rat.c[i] = a->c[na - 1 - i];
    long kb = m < nb ? m : nb;
    poly rbt = poly_new(kb); rbt.n = kb;
    for (long i = 0; i < kb; i++) rbt.c[i] = b->c[nb - 1 - i];
    OPS += (unsigned long long)CH_COPY * (m + kb) + 2 * CH_CALL;
    poly_trim(&rbt);
    poly ib = poly_inv_series(&rbt, m); poly_free(&rbt);
    poly tt = poly_mullow(&rat, &ib, m); poly_free(&rat); poly_free(&ib);
    poly qq = poly_new(m); qq.n = m;
    for (long i = 0; i < m; i++) qq.c[i] = (m - 1 - i < tt.n) ? tt.c[m - 1 - i] : (fe){{0,0,0,0}};
    OPS += (unsigned long long)CH_COPY * m + CH_CALL;
    poly_free(&tt);
    // remainder: r = a - b q has degree < nb - 1. The product b q (na coefficients) is formed mod x^L - 1 with
    // L >= max(nb, m), so 2 L >= na: coefficient i < nb - 1 receives b q_i + b q_{i+L}, and b q_{i+L} = a_{i+L}
    // because i + L >= nb - 1 lies above the remainder's degree.
    long L = pick_len(nb > m ? nb : m);
    fe *X = ntt_load(b, L); ntt_any(X, L, 0);
    fe *Y = ntt_load(&qq, L); ntt_any(Y, L, 0);
    PAR_FOR(L, X[i] = fe_mul(X[i], Y[i])); OPS += (unsigned long long)CH_PMUL * L;
    xfree(Y, sizeof(fe) * L);
    ntt_any(X, L, 1);
    if (want_q) { poly_trim(&qq); *q = qq; } else { poly_free(&qq); *q = poly_new(1); }
    poly rr = poly_new(nb - 1); rr.n = nb - 1;
    for (long i = 0; i < nb - 1; i++) {
        fe v = fe_sub(a->c[i], X[i]);
        rr.c[i] = (i + L < na) ? fe_add(v, a->c[i + L]) : v;
    }
    OPS += (unsigned long long)CH_REM * (nb - 1) + CH_CALL;
    xfree(X, sizeof(fe) * L);
    poly_trim(&rr); poly_fit(&rr); *r = rr;
}


// remainder of a by b (b != 0), CONSUMING a and working in place in its buffer. The quotient is produced in blocks
// of t <= K = min(m, nb) coefficients from the top: each block is the exact quotient of the current top window
// (t + nb - 1 coefficients) by b, from its top t coefficients and I = rev(b)^-1 mod x^K; the window's remainder
// is formed cyclically at L = pick_len(nb) (L >= nb >= t, 2 L >= t + nb - 1, wrapped part known from the window).
static poly poly_rem_blocked(poly *a, const poly *b) {
    long nb = b->n; poly r = *a; a->c = NULL; a->n = a->cap = 0;
    OPS += CH_CALL;
    if (r.n < nb) { poly_fit(&r); return r; }
    long m = r.n - nb + 1, K = m < nb ? m : nb;
    if (nb <= SCHOOL_MAX || K <= SCHOOL_MAX) {         // schoolbook, in place
        fe li = fe_inv(b->c[nb - 1]);
        for (long i = m - 1; i >= 0; i--) {
            fe cq = fe_mul(r.c[i + nb - 1], li);
            for (long j = 0; j < nb; j++) r.c[i + j] = fe_sub(r.c[i + j], fe_mul(cq, b->c[j]));
        }
        OPS += (unsigned long long)CH_AXPY * m * nb + (unsigned long long)CH_PMUL * m;
        r.n = nb - 1; poly_trim(&r); poly_fit(&r); return r;
    }
    poly rbt = poly_new(K); rbt.n = K;
    for (long i = 0; i < K; i++) rbt.c[i] = b->c[nb - 1 - i];
    OPS += (unsigned long long)CH_COPY * K + CH_CALL;
    poly_trim(&rbt);
    poly I = poly_inv_series(&rbt, K); poly_free(&rbt);
    long L = pick_len(nb);
    fe *Bh = ntt_load(b, L); ntt_any(Bh, L, 0);
    while (r.n >= nb) {
        long t = r.n - nb + 1; if (t > K) t = K;
        long s = r.n - nb - t + 1, w = t + nb - 1;    // window r[s .. r.n - 1], w coefficients
        poly top = poly_new(t); top.n = t;
        for (long i = 0; i < t; i++) top.c[i] = r.c[r.n - 1 - i];
        OPS += (unsigned long long)CH_COPY * t + CH_CALL;
        poly qb = poly_mullow(&top, &I, t); poly_free(&top);
        fe *Y = xalloc(sizeof(fe) * L);
        for (long i = 0; i < t; i++) Y[i] = (t - 1 - i < qb.n) ? qb.c[t - 1 - i] : (fe){{0,0,0,0}};
        memset(Y + t, 0, sizeof(fe) * (L - t));
        OPS += (unsigned long long)CH_COPY * t + (unsigned long long)CH_ZERO * (L - t) + CH_CALL;
        poly_free(&qb);
        ntt_any(Y, L, 0);
        PAR_FOR(L, Y[i] = fe_mul(Y[i], Bh[i])); OPS += (unsigned long long)CH_PMUL * L;
        ntt_any(Y, L, 1);
        fe *W = r.c + s;
        for (long i = 0; i < nb - 1; i++) {
            fe v = fe_sub(W[i], Y[i]);
            W[i] = (i + L < w) ? fe_add(v, W[i + L]) : v;
        }
        OPS += (unsigned long long)CH_REM * (nb - 1) + CH_CALL;
        xfree(Y, sizeof(fe) * L);
        r.n = s + nb - 1; poly_trim(&r);
    }
    xfree(Bh, sizeof(fe) * L); poly_free(&I);
    poly_fit(&r); return r;
}

// Half-gcd, consuming a and b (deg a > deg b, or b = 0). m = ceil(deg a / 2). Returns the matrix (want_m) and/or
// the reduced pair (want_p) with (c, d) = M (a, b), deg c >= m > deg d (Lemma H).
static void hgcd2(poly *a, poly *b, int want_m, int want_p, mat *Mo, poly *co, poly *do_) {
    long da = deg(a), m = (da + 1) / 2;
    OPS += CH_CALL;
    if (b->n == 0 || deg(b) < m) {
        if (want_m) *Mo = mat_id();
        if (want_p) { *co = *a; *do_ = *b; } else { poly_free(a); poly_free(b); }
        return;
    }
    poly a0 = poly_shr(a, m), b0 = poly_shr(b, m);
    mat R; hgcd2(&a0, &b0, 1, 0, &R, NULL, NULL);
    poly c, d;
    if (want_m) {                                         // R is still needed: apply a copy
        mat Rc; for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) Rc.m[i][j] = poly_copy(&R.m[i][j]);
        mat_apply_cyc(&Rc, a, b, pick_len(da + 1), &c, &d);
    } else mat_apply_cyc(&R, a, b, pick_len(da + 1), &c, &d);
    if (d.n == 0 || deg(&d) < m) {
        if (want_m) *Mo = R;
        if (want_p) { *co = c; *do_ = d; } else { poly_free(&c); poly_free(&d); }
        return;
    }
    poly q, e; poly_divmod2(&c, &d, want_m, &q, &e); poly_free(&c);
    mat QR;
    if (want_m) { QR = mat_qmul(&q, &R); }
    poly_free(&q);
    if (e.n == 0 || deg(&e) < m) {
        if (want_m) *Mo = QR;
        if (want_p) { *co = d; *do_ = e; } else { poly_free(&d); poly_free(&e); }
        return;
    }
    long l = deg(&d), k = 2 * m - l;
    poly d0 = poly_shr(&d, k), e0 = poly_shr(&e, k);
    mat S;
    hgcd2(&d0, &e0, 1, 0, &S, NULL, NULL);
    if (want_p && want_m) {
        mat Sc; for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) Sc.m[i][j] = poly_copy(&S.m[i][j]);
        mat_apply_cyc(&Sc, &d, &e, pick_len(l + 1), co, do_);
    } else if (want_p) {
        mat_apply_cyc(&S, &d, &e, pick_len(l + 1), co, do_);
    } else { poly_free(&d); poly_free(&e); }
    if (want_m) { long rn = da / 2 + 1; *Mo = mat_mul_cyc(&S, &QR, pick_len(rn), rn); }
}

static poly poly_gcd2(poly a, poly b) {   // consumes a, b
    if (a.n < b.n) { poly t = a; a = b; b = t; }
    while (b.n > 0) {
        if (deg(&a) > deg(&b) && b.n > SCHOOL_MAX) {
            poly c, d; hgcd2(&a, &b, 0, 1, NULL, &c, &d);
            a = c; b = d;
            if (b.n == 0) break;
        }
        poly r = poly_rem_blocked(&a, &b); a = b; b = r;
    }
    poly_free(&b);
    fe li = fe_inv(a.c[a.n - 1]); poly g = poly_scale(&a, li); poly_free(&a); return g;
}
```

### A.5 `attack_g.c` (SHA-256 f8d7c6008a6be80cf04d9e05c5265837766177e21248338413bd8ee7978d9a2f)

```c
// Univariate root-finding collision attack on reduced Orchard Poseidon (P128Pow5T3, Pallas).
// State after round 0 is affine in t = (a + c0)^5 (beta fixed); D(t) = H_beta1(t) - H_beta2(t);
// a root t of D gives a = t^(1/5) - c0 and the colliding inputs (a, beta1), (a, beta2).
// Usage: attack <constants.json-derived file> <idx list comma-separated> <beta1> <beta2>
#include "poly.h"
#include <time.h>

static fe RC[64][3], MDS[3][3];
static int nidx; static int IDX[80];
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
static int is_full(int i) { return i < 4 || i >= 60; }

static void load_constants(const char *path) {
    FILE *f = fopen(path, "r"); if (!f) { perror(path); exit(1); }
    char h[100];
    for (int i = 0; i < 64; i++) for (int j = 0; j < 3; j++) { if (fscanf(f, "%99s", h) != 1) exit(2); RC[i][j] = fe_from_hex(h); }
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) { if (fscanf(f, "%99s", h) != 1) exit(2); MDS[i][j] = fe_from_hex(h); }
    fclose(f);
}
// output coordinate 0 of the reduced permutation as a polynomial in t, for second input beta
static poly build_out(fe beta) {
    int i0 = IDX[0];
    fe two65 = fe_from_hex("20000000000000000");
    fe k1 = fe_add(beta, RC[i0][1]); { fe s = fe_mul(k1, k1); s = fe_mul(s, s); k1 = fe_mul(s, k1); }
    fe k2 = fe_add(two65, RC[i0][2]); { fe s = fe_mul(k2, k2); s = fe_mul(s, s); k2 = fe_mul(s, k2); }
    OPS += 2 * 8 + 32;
    poly s[3];
    for (int r = 0; r < 3; r++) {
        s[r] = poly_new(2); s[r].n = 2;
        s[r].c[1] = MDS[r][0];
        s[r].c[0] = fe_add(fe_mul(MDS[r][1], k1), fe_mul(MDS[r][2], k2));
        OPS += 8;
    }
    for (int k = 1; k < nidx; k++) {
        int i = IDX[k], last = (k == nidx - 1);
        for (int r = 0; r < 3; r++) { s[r].c[0] = fe_add(s[r].c[0], RC[i][r]); OPS += 4; }
        for (int r = 0; r < (is_full(i) ? 3 : 1); r++) { poly t = poly_pow5(&s[r]); poly_free(&s[r]); s[r] = t; }
        int rows = last ? 1 : 3;
        poly ns[3];
        for (int r = 0; r < rows; r++) {
            poly a0 = poly_scale(&s[0], MDS[r][0]);
            poly a1 = poly_axpy(&a0, MDS[r][1], &s[1]);
            ns[r] = poly_axpy(&a1, MDS[r][2], &s[2]);
            poly_free(&a0); poly_free(&a1);
        }
        for (int r = 0; r < 3; r++) poly_free(&s[r]);
        for (int r = 0; r < rows; r++) s[r] = ns[r];
        for (int r = rows; r < 3; r++) s[r] = poly_new(1);
    }
    poly_free(&s[1]); poly_free(&s[2]);
    return s[0];
}

// ---------- the two-round line ----------
// Round-1 S-box input u = M (X, Y, K) + RC1 with X = (nk + RC0_0)^5, Y = (rho + RC0_1)^5 free and K = (2^65 + RC0_2)^5.
// With w the third row of M^-1, u is valid iff w.(u - RC1) = K. The line u(t) = (t D0, t D1, C2), D0 = w1, D1 = -w0,
// C2 = (K + w.RC1) / w2, satisfies it for every t; after the round-1 S-box the state is (sigma D0^5, sigma D1^5, C2^5),
// sigma = t^5, so the state after round 1 is affine in sigma and the digest is f(sigma) of degree 5^(#remaining S-box layers).
static fe MINV[3][3], LD0, LD1, LC2, LK;
static fe E5;   // 5^-1 mod (p-1), plain integer exponent
static void line_setup(void) {
    // inverse of the 3x3 MDS by the adjugate
    fe c[3][3];
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) {
        int r0 = (j + 1) % 3, r1 = (j + 2) % 3, c0 = (i + 1) % 3, c1 = (i + 2) % 3;
        c[i][j] = fe_sub(fe_mul(MDS[r0][c0], MDS[r1][c1]), fe_mul(MDS[r0][c1], MDS[r1][c0]));   // cofactor, transposed
    }
    fe det = fe_add(fe_add(fe_mul(MDS[0][0], c[0][0]), fe_mul(MDS[0][1], c[1][0])), fe_mul(MDS[0][2], c[2][0]));
    fe di = fe_inv(det);
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) MINV[i][j] = fe_mul(c[i][j], di);
    OPS += 9 * 3 + 6 + 9 + 64;
    fe two65 = fe_from_hex("20000000000000000");
    LK = fe_add(two65, RC[0][2]); { fe s = fe_mul(LK, LK); s = fe_mul(s, s); LK = fe_mul(s, LK); }
    LD0 = MINV[2][1]; LD1 = fe_neg(MINV[2][0]);
    fe wrc = fe_add(fe_add(fe_mul(MINV[2][0], RC[1][0]), fe_mul(MINV[2][1], RC[1][1])), fe_mul(MINV[2][2], RC[1][2]));
    LC2 = fe_mul(fe_add(LK, wrc), fe_inv(MINV[2][2]));
    OPS += 40;
    // check: M^-1 M = I
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) {
        fe s = fe_add(fe_add(fe_mul(MINV[i][0], MDS[0][j]), fe_mul(MINV[i][1], MDS[1][j])), fe_mul(MINV[i][2], MDS[2][j]));
        if (!fe_eq(s, i == j ? ONE : (fe){{0,0,0,0}})) { fprintf(stderr, "MDS inverse check failed\n"); exit(5); }
    }
}
static fe p5(fe x) { fe s = fe_mul(x, x); s = fe_mul(s, s); return fe_mul(s, x); }
// f(sigma): IDX[0] = 0 and IDX[1] = 1 are absorbed by the line; rounds IDX[2..] are applied to polynomials
static poly build_f(void) {
    fe d05 = p5(LD0), d15 = p5(LD1), c25 = p5(LC2);
    poly s[3];
    for (int r = 0; r < 3; r++) {
        s[r] = poly_new(2); s[r].n = 2;
        s[r].c[1] = fe_add(fe_mul(MDS[r][0], d05), fe_mul(MDS[r][1], d15));
        s[r].c[0] = fe_mul(MDS[r][2], c25);
    }
    OPS += 3 * 8 + 3 * 6 + 32;
    for (int k = 2; k < nidx; k++) {
        int i = IDX[k], last = (k == nidx - 1);
        for (int r = 0; r < 3; r++) { s[r].c[0] = fe_add(s[r].c[0], RC[i][r]); OPS += 4; }
        for (int r = 0; r < (is_full(i) ? 3 : 1); r++) { poly t = poly_pow5(&s[r]); poly_free(&s[r]); s[r] = t; }
        int rows = last ? 1 : 3;
        poly ns[3];
        for (int r = 0; r < rows; r++) {
            poly a0 = poly_scale(&s[0], MDS[r][0]);
            poly a1 = poly_axpy(&a0, MDS[r][1], &s[1]);
            ns[r] = poly_axpy(&a1, MDS[r][2], &s[2]);
            poly_free(&a0); poly_free(&a1);
        }
        for (int r = 0; r < 3; r++) poly_free(&s[r]);
        for (int r = 0; r < rows; r++) s[r] = ns[r];
        for (int r = rows; r < 3; r++) s[r] = poly_new(1);
    }
    poly_free(&s[1]); poly_free(&s[2]);
    return s[0];
}
// inputs (nk, rho) of the point sigma of the line
static void line_inputs(fe sigma, fe *nk, fe *rho, int *ok) {
    fe t = fe_pow_plain_exp(sigma, E5);
    fe u[3] = { fe_sub(fe_mul(t, LD0), RC[1][0]), fe_sub(fe_mul(t, LD1), RC[1][1]), fe_sub(LC2, RC[1][2]) };
    fe x[3];
    for (int i = 0; i < 3; i++) x[i] = fe_add(fe_add(fe_mul(MINV[i][0], u[0]), fe_mul(MINV[i][1], u[1])), fe_mul(MINV[i][2], u[2]));
    *ok = fe_eq(x[2], LK);
    *nk = fe_sub(fe_pow_plain_exp(x[0], E5), RC[0][0]);
    *rho = fe_sub(fe_pow_plain_exp(x[1], E5), RC[0][1]);
    OPS += 3 * (256 * 8) + 40;
}

// ---------- X^p mod D (D monic, degree n) ----------
// Square-and-multiply on the bits of p, multiplication by X fused into the squaring: S = A^2 * X^bit (at most
// 2n coefficients) by a length-L2 transform, L2 = pick_len(2n); quotient q = rev(rev(S)_top * iD mod x^qn) with
// iD = rev(D)^-1 mod x^n transformed once at length L2; the remainder S - qD has degree < n <= L1 and is computed
// cyclically mod x^L1 - 1, L1 = pick_len(n + 1), with D transformed once at length L1. Buffers: B (L2), which holds
// S, then the quotient product, then q and qD in its first L1 entries; E (L1), which holds A between bits.
// D is not kept during the loop; it is recovered exactly from its transform at the end (L1 >= n + 1).
static poly powmod_xp(poly *D) {
    long n = deg(D);
    long L2 = pick_len(2 * n), L1 = pick_len(n + 1);
    poly rD = poly_rev(D, D->n);
    poly iD = poly_inv_series(&rD, n);
    poly_free(&rD);
    fe *iDhat = ntt_load(&iD, L2); poly_free(&iD); ntt_any(iDhat, L2, 0);
    fe *Dhat = ntt_load(D, L1); poly_free(D); ntt_any(Dhat, L1, 0);
    fe *B = xalloc(sizeof(fe) * L2), *E = xalloc(sizeof(fe) * L1);
    E[1] = ONE; E[0] = (fe){{0,0,0,0}}; long an = 2;     // A = X
    fe pm = P;
    int top = 255; while (!((pm.v[top / 64] >> (top % 64)) & 1)) top--;
    long done = 0; double t0 = now();
    for (int b = top - 1; b >= 0; b--) {
        memcpy(B, E, sizeof(fe) * an); memset(B + an, 0, sizeof(fe) * (L2 - an));
        OPS += (unsigned long long)CH_COPY * an + (unsigned long long)CH_ZERO * (L2 - an) + CH_CALL;
        ntt_any(B, L2, 0);
        PAR_FOR(L2, B[i] = fe_mul(B[i], B[i])); OPS += (unsigned long long)CH_PSQR * L2;
        ntt_any(B, L2, 1);
        long a2n = 2 * an - 1;
        if ((pm.v[b / 64] >> (b % 64)) & 1) {         // times X: shift up by one
            for (long i = a2n; i >= 1; i--) B[i] = B[i - 1];
            B[0] = (fe){{0,0,0,0}}; a2n++;
            OPS += (unsigned long long)CH_COPY * a2n + CH_CALL;
        }
        if (a2n > n) {
            long qn = a2n - n;                         // <= n
            // E <- S mod (x^L1 - 1), first n coefficients (the rest cancel against qD below)
            PAR_FOR(n, E[i] = (i + L1 < a2n) ? fe_add(B[i], B[i + L1]) : B[i]); OPS += (unsigned long long)CH_ADDV * n;
            // B <- rev(S)_top: reads B[n .. a2n), writes B[0 .. qn), disjoint since qn <= n
            for (long i = 0; i < qn; i++) B[i] = B[a2n - 1 - i];
            memset(B + qn, 0, sizeof(fe) * (L2 - qn));
            OPS += (unsigned long long)CH_COPY * qn + (unsigned long long)CH_ZERO * (L2 - qn);
            ntt_any(B, L2, 0);
            PAR_FOR(L2, B[i] = fe_mul(B[i], iDhat[i])); OPS += (unsigned long long)CH_PMUL * L2;
            ntt_any(B, L2, 1);
            // q = rev of B[0 .. qn) in place, then qD mod (x^L1 - 1) in B[0 .. L1)
            for (long i = 0, j = qn - 1; i < j; i++, j--) { fe t = B[i]; B[i] = B[j]; B[j] = t; }
            memset(B + qn, 0, sizeof(fe) * (L1 - qn));
            OPS += (unsigned long long)CH_COPY * qn + (unsigned long long)CH_ZERO * (L1 - qn);
            ntt_any(B, L1, 0);
            PAR_FOR(L1, B[i] = fe_mul(B[i], Dhat[i])); OPS += (unsigned long long)CH_PMUL * L1;
            ntt_any(B, L1, 1);
            PAR_FOR(n, E[i] = fe_sub(E[i], B[i])); OPS += (unsigned long long)CH_ADDV * n;
            an = n;
        } else {
            memcpy(E, B, sizeof(fe) * a2n); an = a2n; OPS += (unsigned long long)CH_COPY * a2n;
        }
        while (an > 0 && fe_is_zero(E[an - 1])) { an--; OPS += 4; } OPS += 2;   // trim
        done++;
        if (done % 32 == 0) { fprintf(stderr, "  powmod bit %d/%d  %.1fs  ops=%.3e  peak=%.1fMB\n", b, top, now() - t0, (double)OPS, MEM_PEAK / 1048576.0); }
    }
    xfree(iDhat, sizeof(fe) * L2); xfree(B, sizeof(fe) * L2);
    poly A; A.c = xshrink(E, sizeof(fe) * L1, sizeof(fe) * (n > 0 ? n : 1)); A.n = an; A.cap = n > 0 ? n : 1;
    ntt_any(Dhat, L1, 1);                             // recover D
    D->c = xshrink(Dhat, sizeof(fe) * L1, sizeof(fe) * (n + 1)); D->n = n + 1; D->cap = n + 1;
    OPS += 2 * CH_CALL;
    return A;
}

static poly powmod_ref(const poly *D) {
    poly A = poly_new(2); A.c[1] = ONE; A.c[0] = (fe){{0,0,0,0}}; A.n = 2;
    fe pm = P; int top = 255; while (!((pm.v[top / 64] >> (top % 64)) & 1)) top--;
    for (int b = top - 1; b >= 0; b--) {
        poly S = poly_sqr(&A); poly q, r; poly_divmod(&S, D, &q, &r); poly_free(&S); poly_free(&q); poly_free(&A); A = r;
        if ((pm.v[b / 64] >> (b % 64)) & 1) {
            poly X = poly_new(2); X.c[1] = ONE; X.c[0] = (fe){{0,0,0,0}}; X.n = 2;
            poly M = poly_mul(&A, &X); poly q2, r2; poly_divmod(&M, D, &q2, &r2); poly_free(&M); poly_free(&q2); poly_free(&X); poly_free(&A); A = r2;
        }
    }
    return A;
}

#include "gcd2.h"
#define poly_gcd poly_gcd2

// (X + delta)^e mod g for small-degree g, e a plain 256-bit exponent
static poly powmod_lin(fe delta, fe e, const poly *g) {
    poly r = poly_new(1); r.c[0] = ONE; r.n = 1;
    poly base = poly_new(2); base.c[0] = delta; base.c[1] = ONE; base.n = 2;
    { poly q, t; poly_divmod(&base, g, &q, &t); poly_free(&q); poly_free(&base); base = t; }
    for (int i = 255; i >= 0; i--) {
        poly s = poly_mul(&r, &r); poly q, t; poly_divmod(&s, g, &q, &t); poly_free(&s); poly_free(&q); poly_free(&r); r = t;
        if ((e.v[i / 64] >> (i % 64)) & 1) { poly m = poly_mul(&r, &base); poly q2, t2; poly_divmod(&m, g, &q2, &t2); poly_free(&m); poly_free(&q2); poly_free(&r); r = t2; }
    }
    poly_free(&base); return r;
}
// one root of a monic g that splits into distinct linear factors (g | X^p - X), deg g >= 1
static fe find_root(poly g) {
    fe half = P; half.v[0] -= 1;   // (p-1)/2
    half.v[0] = (half.v[0] >> 1) | (half.v[1] << 63); half.v[1] = (half.v[1] >> 1) | (half.v[2] << 63);
    half.v[2] = (half.v[2] >> 1) | (half.v[3] << 63); half.v[3] >>= 1;
    uint64_t delta = 0;
    while (deg(&g) > 1) {
        poly h = powmod_lin(fe_from_u64(delta), half, &g);
        poly one = poly_new(1); one.c[0] = ONE; one.n = 1;
        poly h1 = poly_sub(&h, &one); poly_free(&h); poly_free(&one);
        poly gc = poly_copy(&g);
        poly f = poly_gcd(gc, h1);
        if (deg(&f) >= 1 && deg(&f) < deg(&g)) { poly_free(&g); g = f; } else poly_free(&f);
        delta++; OPS += CH_CALL;
    }
    fe r = fe_neg(g.c[0]); poly_free(&g); return r;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: attack consts idxlist(starting 0,1) logmax maxtrials\n"); return 1; }
    fe_init(); load_constants(argv[1]);
    { char *s = argv[2]; nidx = 0; while (*s) { IDX[nidx++] = (int)strtol(s, &s, 10); if (*s == ',') s++; } }
    if (IDX[0] != 0 || IDX[1] != 1) { fprintf(stderr, "the line needs rounds 0 and 1 first\n"); return 1; }
    ntt_init(atoi(argv[3]));
    int maxtrials = atoi(argv[4]);
    E5 = fe_plain_from_hex("333333333333333333333333333333334e9ee0c9a10a60e2e0f0f3f0cccccccd");
    double t0 = now();
    line_setup();
    for (int trial = 0; trial < maxtrials; trial++) {
        unsigned long long ops0 = OPS;
        fe s0 = fe_from_u64((uint64_t)trial + 1);        // the public stream sigma0_i = i + 1, fixed before any run
        poly f = build_f();
        long n = deg(&f);
        // f0 = f(s0) by Horner; g = f - f0; h = g / (X - s0) exactly (synthetic division), made monic
        fe f0 = f.c[f.n - 1];
        for (long i = f.n - 2; i >= 0; i--) f0 = fe_add(fe_mul(f0, s0), f.c[i]);
        OPS += (unsigned long long)CH_AXPY * f.n;
        poly h = poly_new(n); h.n = n;
        fe carry = f.c[n];
        h.c[n - 1] = carry;
        for (long i = n - 1; i >= 1; i--) { carry = fe_add(f.c[i], fe_mul(carry, s0)); h.c[i - 1] = carry; }
        fe rem = fe_sub(fe_add(f.c[0], fe_mul(carry, s0)), f0);
        OPS += (unsigned long long)CH_AXPY * n;
        poly_free(&f);
        if (!fe_is_zero(rem)) { fprintf(stderr, "synthetic division remainder nonzero\n"); return 6; }
        fe li = fe_inv(h.c[h.n - 1]); poly hm = poly_scale(&h, li); poly_free(&h); h = hm;
        long degh = deg(&h);
        unsigned long long ops_pm = OPS;
        poly A = powmod_xp(&h);
        fprintf(stderr, "  phase: before powmod %llu, powmod %llu, peak %lld\n", ops_pm - ops0, OPS - ops_pm, MEM_PEAK);
        poly X = poly_new(2); X.c[1] = ONE; X.c[0] = (fe){{0,0,0,0}}; X.n = 2;
        poly R = poly_sub(&A, &X); poly_free(&A); poly_free(&X);
        poly g = poly_gcd(h, R);
        long dg = deg(&g);
        printf("trial %d sigma0 %d deg_f %ld deg_h %ld gcd_degree %ld ops %llu  (%.1fs, peak %.1fMB)\n", trial, trial + 1, n, degh, dg, OPS - ops0, now() - t0, MEM_PEAK / 1048576.0);
        fflush(stdout);
        if (dg >= 1) {
            fe s1 = find_root(g);
            int ok0, ok1; fe nk0, rho0, nk1, rho1;
            line_inputs(s0, &nk0, &rho0, &ok0); line_inputs(s1, &nk1, &rho1, &ok1);
            fe_print("sigma0 ", s0); fe_print("sigma1 ", s1);
            fe_print("nk0 ", nk0); fe_print("rho0 ", rho0); fe_print("nk1 ", nk1); fe_print("rho1 ", rho1);
            printf("line_check %d %d\n", ok0, ok1);
            printf("trials %d\nops_total %llu\nmem_peak_bytes %lld\n", trial + 1, OPS, MEM_PEAK);
            return 0;
        }
        poly_free(&g);
    }
    printf("no success within %d trials\nops_total %llu\nmem_peak_bytes %lld\n", maxtrials, OPS, MEM_PEAK);
    return 0;
}
```


## Appendix B. The bound programs
Run from one directory: `python3 orchard_bound.py 2 1 1` (totals), `python3 checks.py` (checks), `python3 gcd2_table.py`
(the per-level table of Section 8.3). `gcdbound2.py` imports the transform, product and charge definitions of
`gcdbound.py` unchanged; `orchard_bound.py` imports both.

### B.gcdbound.py (SHA-256 8e62991cc9e04fb4bd3429930abab90c79357c3bd2e4358ac705ccc0da9c40a5)

```python
#!/usr/bin/env python3
"""Worst-case operation bound for the gcd phase of the Orchard univariate attack.

Mirrors the charge formulas of the counted C program (poly.h / attack.c): every primitive's charge is an exact
integer function of its operand sizes (coefficient counts), nondecreasing in each size (or replaced by a
nondecreasing envelope). hgcd and the gcd loop are evaluated at the worst-case sizes allowed by the half-gcd
invariants, so the result bounds the charged work of every remainder sequence, not only the executed one.
Standard library only; integer arithmetic only. Usage: python3 gcdbound.py N   (N = degree of the modulus)
"""
import sys
from functools import lru_cache

# Conservative charge schedule of this bound. Each per-item charge is at least the C program's own charge for the
# same loop body (poly.h CH_*), and the schedule adds work the C counter leaves out:
#   - EXP: an exponentiation (inversion, L^-1, fifth root) at 16 operations per exponent bit over 256 bits plus 64:
#     squaring, conditional multiplication, bit test (shift, AND), branch, operand loads and stores and loop control per bit;
#   - CH_CALL: 128 per kernel call (setup, sizes, branches, return, and one allocation and one release of a
#     bump allocator for the call's result and buffers);
#   - CH_PAR: 64 parallel blocks per data-parallel loop, 24 operations each for the block bounds, the empty-block
#     test and the dispatch (charged per call even where a sequential loop would need none);
#   - CH_GROUP: 12 per outer group iteration of a transform stage (group counter, compare, branch, base pointer,
#     twiddle reset, inner-loop entry and exit);
#   - length tests in add/sub and axpy at 2 operations each (compare and branch), trim at 6 per removed
#     coefficient plus 6 per call, reversal at 9 per coefficient, schoolbook outer loop at 6 per outer iteration.
CH_BFLY, CH_QUAD, CH_BREV, CH_SCALE, CH_PMUL, CH_PSQR = 16, 34, 20, 8, 10, 8
CH_COPY, CH_ZERO, CH_ADDV, CH_AXPY, CH_SCHOOL, CH_CALL = 7, 5, 14, 15, 12, 128
CH_PAR, CH_GROUP, CH_REV, CH_OUTER = 64 * 24, 12, 9, 6
SCHOOL_MAX = 48                    # poly_gcd: below this many coefficients plain Euclid, no hgcd
MUL_SCHOOL = 12                    # poly_mul: schoolbook iff the smaller operand has at most this many coefficients
INV_SCHOOL = 48                    # poly_inv_series: schoolbook Newton step iff m <= this
DIV_SCHOOL_Q = 48                  # poly_divmod: schoolbook iff quotient length <= DIV_SCHOOL_Q
DIV_SCHOOL_B = 48                  #   or divisor size <= DIV_SCHOOL_B
EXP = 256 * 16 + 64                # one exponentiation (inversion, L^-1, fifth root), 16 per exponent bit
FE_INV = EXP

def pow2ceil(x):
    L = 1
    while L < x: L <<= 1
    return L

LEN3_MIN = 6144                    # ntt3.h: lengths 3 * 2^k are used from 6144 on
NTT_SEQ_MAX = 4096                 # poly.h: transforms of at most this length run sequentially

def pick_len(n):                   # ntt3.h pick_len: smallest admissible transform length >= n
    a = pow2ceil(n); b = 3 * pow2ceil((n + 2) // 3)
    return b if (b >= LEN3_MIN and b < a) else a

def admissible(limit):             # every admissible length up to limit, increasing
    out = set()
    k = 1
    while k <= limit:
        out.add(k)
        if LEN3_MIN <= 3 * k <= limit: out.add(3 * k)
        k <<= 1
    return sorted(out)

def log2i(L):
    return L.bit_length() - 1

def trim(n):                       # poly_trim worst case: every coefficient removed
    return 6 + 6 * n

CH_OCT, CH_HEX = 76, 170           # radix-8 kernel per 8 elements, radix-16 kernel per 16 elements (poly.h)

@lru_cache(maxsize=None)
def ntt_plan(lg):
    """poly.h ntt_plan: radices from {16, 8, 4, 2} covering lg levels with the least kernel charge per element (ties
    to fewer stages), largest first."""
    lr = (4, 3, 2, 1); ch = (CH_HEX * 2, CH_OCT * 4, CH_QUAD * 8, CH_BFLY * 16)
    best = [(0, 0, None)] + [None] * lg
    for l in range(1, lg + 1):
        for k in range(4):
            if lr[k] <= l and best[l - lr[k]] is not None:
                c = best[l - lr[k]][0] + ch[k]; n = best[l - lr[k]][1] + 1
                if best[l] is None or c < best[l][0] or (c == best[l][0] and n < best[l][1]): best[l] = (c, n, k)
    R = []; l = lg
    while l > 0:
        k = best[l][2]; R.append(1 << lr[k]); l -= lr[k]
    return tuple(sorted(R, reverse=True))

def _stage(Lt, R, h, par):
    """One transform stage of radix R over blocks of R h on Lt elements: kernel charge, outer group loop, and when
    parallel the 64 contiguous blocks, each starting its twiddle by an exponentiation of at most log2(h) bits
    (charged for all 64 blocks at 16 per bit, plus 16)."""
    groups = Lt // (R * h)
    assert not par or R >= 8, 'parallel stages use radix 16 or 8 only (their spare covers the group counter)'
    c = {16: CH_HEX * (Lt // 16), 8: CH_OCT * (Lt // 8), 4: CH_QUAD * (Lt // 4), 2: CH_BFLY * (Lt // 2)}[R] + CH_CALL + CH_GROUP * groups
    if par:
        c += CH_PAR + 64 * (16 * log2i(h) + 16)
    return c

@lru_cache(maxsize=None)
def ntt_batch(M, nb, inverse):
    """Charge of ntt_batch(a, M, nb, inverse): nb transforms of length M = 2^lg as one batch of Lt = nb M elements:
    the stages of ntt_plan(lg) (forward decimation in frequency, inverse decimation in time; no bit-reversal pass),
    and for the inverse
    the scaling by M^-1 with its exponentiation. Batches of at most NTT_SEQ_MAX elements run sequentially."""
    lg = log2i(M); Lt = nb * M; par = Lt > NTT_SEQ_MAX
    c = 0; lb = lg
    for R in ntt_plan(lg):
        c += _stage(Lt, R, (1 << lb) // R, par); lb -= log2i(R)
    if inverse:
        c += CH_SCALE * Lt + EXP + CH_CALL + (CH_PAR if par else 0)
    return c

def ntt(L, inverse):
    return ntt_batch(L, 1, inverse)

def ntt_load(L):                   # copy n <= L coefficients, zero the rest: at most CH_COPY * L
    return CH_COPY * L + CH_CALL

CH_R3F, CH_R3I = 28, 30           # radix-3 stage per 3 elements (ntt3.h)

@lru_cache(maxsize=None)
def ntt_any(L, inverse):
    """Charge of ntt_any(a, L, inverse): for L = 3M (M = 2^k) one radix-3 stage over M triples (its 64 blocks,
    each starting with two exponentiations of at most k bits at 16 per bit, plus two multiplications) and the
    batch of three length-M transforms; for L = 2^k the transform ntt(L)."""
    if L & (L - 1) == 0: return ntt(L, inverse)
    M = L // 3; k = log2i(M)
    return ntt_batch(M, 3, inverse) + (CH_R3I if inverse else CH_R3F) * M + CH_PAR + 64 * (32 * k + 48) + CH_CALL

def mul_school(na, nb):
    if na == 0 or nb == 0: return CH_CALL
    rn = na + nb - 1
    return CH_SCHOOL * na * nb + CH_OUTER * na + CH_ZERO * rn + CH_CALL + trim(rn)

def mul_ntt(na, nb):
    rn = na + nb - 1; L = pick_len(rn)
    return 2 * ntt_load(L) + 2 * ntt_any(L, 0) + CH_PMUL * L + CH_PAR + ntt_any(L, 1) + trim(rn)

def mul(na, nb):
    """Nondecreasing envelope of poly_mul over all operand sizes up to (na, nb)."""
    if na == 0 or nb == 0: return CH_CALL
    lo, hi = min(na, nb), max(na, nb)
    best = mul_school(min(lo, MUL_SCHOOL), hi)       # schoolbook branch: smaller operand <= MUL_SCHOOL
    if lo > MUL_SCHOOL:
        best = max(best, mul_ntt(na, nb))
    return best

def addsub(na, nb):
    n = max(na, nb); return CH_ADDV * n + CH_CALL + trim(n)

def copy(n): return CH_COPY * n + CH_CALL
def shr(n, k): return CH_COPY * max(n - k, 0) + CH_CALL
def trunc(n, k): m = min(n, k); return CH_COPY * m + CH_CALL + trim(m)
def rev(m): return CH_REV * m + CH_CALL + trim(m)
def scale(n): return CH_SCALE * n + CH_CALL + trim(n)

@lru_cache(maxsize=None)
def inv_series(k):
    """poly_inv_series(a, k): Newton doubling; each step at most the larger of its two branches."""
    c = FE_INV + trim(k)
    cur = 1
    while cur < k:
        m = min(2 * cur, k); Lc = pick_len(m)
        school = (trunc(m, m) + mul_school(m, cur) + CH_COPY * (m - cur) + trim(m - cur)
                  + mul_school(cur, m - cur) + CH_COPY * (m - cur))
        fast = (CH_COPY * 2 * Lc + 2 * ntt_any(Lc, 0) + CH_PMUL * Lc + CH_PAR + ntt_any(Lc, 1) + CH_COPY * Lc
                + ntt_any(Lc, 0) + CH_PMUL * Lc + CH_PAR + ntt_any(Lc, 1) + CH_SCALE * (m - cur) + 2 * CH_CALL)
        c += fast if m > INV_SCHOOL else school   # poly_inv_series: schoolbook step only when m <= INV_SCHOOL
        c += CH_CALL
        cur = m
    return c

def divmod_exact(na, nb):
    """poly_divmod(a, b) charge for dividend size na and divisor size nb (1 <= nb <= na)."""
    if na < nb: return copy(na) + CH_CALL
    m = na - nb + 1
    if nb <= DIV_SCHOOL_B or m <= DIV_SCHOOL_Q:
        return copy(na) + FE_INV + CH_AXPY * m * nb + CH_PMUL * m + CH_CALL + trim(nb) + trim(m)
    return (rev(na) + rev(nb) + inv_series(m) + trunc(na, m) + mul(m, m) + trunc(2 * m, m) + rev(m)
            + mul(nb, m) + addsub(na, nb + m))

def divmod_env(na, q):
    """Envelope of poly_divmod over all dividend sizes na' <= na with quotient length q (divisor na' - q + 1).

    For fixed q every term of each branch is nondecreasing in the dividend size; the branch is the schoolbook one
    when the divisor has at most 48 coefficients (dividend <= q + 47) or q <= 48, the transform one otherwise. The
    envelope is the larger of the transform charge at na (when that branch is reachable) and the schoolbook charge at
    the largest dividend for which the schoolbook branch is taken. It is nondecreasing in na for fixed q."""
    if q < 1 or na < q: return copy(max(na, 1)) + CH_CALL
    best = 0
    if q <= DIV_SCHOOL_Q:
        best = divmod_exact(na, na - q + 1)                     # schoolbook for every na
    else:
        top = min(na, q + DIV_SCHOOL_B - 1)                     # schoolbook while divisor <= DIV_SCHOOL_B
        if top >= q: best = divmod_exact(top, top - q + 1)
        if na - q + 1 > DIV_SCHOOL_B: best = max(best, divmod_exact(na, na - q + 1))
    return best

@lru_cache(maxsize=None)
def divmod_ub(na, nb_lo):
    """Bound on poly_divmod for any dividend of at most na coefficients and quotient length at most
    qmax = na - nb_lo + 1 (equivalently, divisor at least nb_lo when the dividend is na). Nondecreasing in na and
    in qmax: it is the maximum of divmod_env(na, q) over 1 <= q <= qmax, and divmod_env is nondecreasing in na.

    divmod_env(na, q) is a step function of q (through pick_len(q), pick_len(2q - 1) and the schoolbook switch)
    plus terms affine in q between steps, so the maximum over q is attained at a segment end; the candidates are
    every segment end and the full schoolbook range."""
    qmax = na - max(nb_lo, 1) + 1
    if qmax < 1: return copy(na) + CH_CALL
    S = max(DIV_SCHOOL_Q, DIV_SCHOOL_B, MUL_SCHOOL, INV_SCHOOL)
    cand = set(range(1, min(qmax, 2 * S + 2) + 1)) | set(range(max(1, qmax - 2 * S - 2), qmax + 1))
    for k in admissible(4 * na):                               # steps of pick_len(q) and pick_len(2q - 1)
        for q in (k - 2, k - 1, k, k + 1, k + 2, (k + 1) // 2 - 1, (k + 1) // 2, (k + 1) // 2 + 1):
            if 1 <= q <= qmax: cand.add(q)
    for q in list(cand):                                        # schoolbook switch points of the envelope
        for d in (na - DIV_SCHOOL_B - 1, na - DIV_SCHOOL_B, na - DIV_SCHOOL_B + 1, na - MUL_SCHOOL - 1, na - MUL_SCHOOL, na - MUL_SCHOOL + 1):
            if 1 <= d <= qmax: cand.add(d)
    return max(divmod_env(na, q) for q in cand)

def mat_apply(e, n):               # 4 products (matrix entry <= e coefficients) x (vector entry <= n) and 2 sums
    return 4 * mul(e, n) + 2 * addsub(e + n - 1, e + n - 1)

def mat_mul(x, y):                 # 8 products and 4 sums
    return 8 * mul(x, y) + 4 * addsub(x + y - 1, x + y - 1)

@lru_cache(maxsize=None)
def hgcd(N, want_m, want_p):
    """Upper bound on the charge of hgcd(a, b, want_m, want_p) for deg a <= N (all paths)."""
    if N <= 0:
        return CH_CALL + (copy(N + 1) * 2 if want_p else 0)
    m = (N + 1) // 2
    base = CH_CALL + (2 * copy(N + 1) if want_p else 0)
    N1 = N - m                                   # deg a0
    eR = N1 // 2 + 1                             # coefficients of an entry of R
    c = CH_CALL + 2 * shr(N + 1, m)
    c += hgcd(N1, 1, 0) if N1 > 0 else CH_CALL
    c += mat_apply(eR, N + 1)
    # early return after R: (c, d) handed back, no further charge
    qn = N - m + 1                               # quotient coefficients at most
    c += divmod_ub(N + 1, m + 1)
    if want_m:
        c += addsub(1, qn) + mat_mul(qn, eR)     # Q = [[0,1],[1,-q]] and Q R
    m1 = (N1 + 1) // 2
    dn = m + m1                                  # deg d < m + m1, so d has at most m + m1 coefficients
    N2 = max(N1 - 1, 0)                          # deg d0 <= N1 - 1
    c += 2 * shr(dn, 0)
    c += hgcd(N2, 1, 0) if N2 > 0 else CH_CALL
    eS = N2 // 2 + 1
    if want_p:
        c += mat_apply(eS, dn)
    if want_m:
        c += mat_mul(eS, qn + eR - 1)
    return max(c, base)

def gcd_bound(N):
    """poly_gcd(a, b), deg a = N > deg b: hgcd steps with pair output, one division after each, then small Euclid."""
    total = 0; n = N
    while n + 1 > SCHOOL_MAX:
        total += hgcd(n, 0, 1)
        m = (n + 1) // 2
        total += divmod_ub(n + 1, 1) + 100      # one division, loop control and progress print
        n = m - 1                                # new deg a < m
    # small Euclid: at most n + 1 divisions on at most n + 1 coefficients
    total += (n + 1) * (divmod_ub(max(n + 1, 1), 1) + 100)
    total += FE_INV + scale(n + 1)
    return total

if __name__ == '__main__':
    N = int(sys.argv[1])
    b = gcd_bound(N)
    print(f"gcd bound for degree {N}: {b} operations (2^{b.bit_length() - 1}..)")
```

### B.gcdbound2.py (SHA-256 e24f2576311bf3d1dda1f6bf75704249062d049901016032eaaf708f872d7b72)

```python
#!/usr/bin/env python3
"""Replayable worst-case bound on the charged time and the live memory of poly_gcd2 (gcd2.h): the memory-lean
half-gcd with cyclic matrix products, truncated-reversal division and transform lengths 2^k or 3 * 2^k.

Time: a conservative charge schedule, at least the C program's counter for every loop body (poly.h, ntt3.h, gcd2.h
CH_* are the floor), plus what the counter leaves out (listed at the constants). Memory: live coefficients, every
object counted at an upper bound of its allocated size from allocation to release, replayed step by step in the
order of the code. Every bound is evaluated at upper bounds of its sizes and is nondecreasing in each of them.
Standard library only, integer arithmetic only.
Usage: python3 gcdbound2.py N   (bounds for poly_gcd2 on deg a = N > deg b)
"""
import sys
from functools import lru_cache

# ---- transforms, products and charges: imported unchanged from gcdbound.py (one definition) -------------------------
from gcdbound import (CH_BFLY, CH_QUAD, CH_BREV, CH_SCALE, CH_PMUL, CH_PSQR, CH_COPY, CH_ZERO, CH_ADDV, CH_AXPY,
                      CH_SCHOOL, CH_CALL, CH_PAR, CH_GROUP, CH_REV, CH_OUTER, SCHOOL_MAX, MUL_SCHOOL, EXP, FE_INV, pow2ceil,
                      pick_len, log2i, trim, ntt, ntt_any, ntt_load, mul_school, mul_ntt, mul, addsub, copy, shr,
                      trunc, scale, inv_series)
CH_PMAC, CH_PMACC, CH_MAT2, CH_REM = 15, 13, 24, 15   # gcd2.h per-element charges
FIT = CH_CALL                      # poly_fit: release of unused capacity
CYC_MIN = 8                        # gcd2.h: matrices with entries of at most 8 coefficients are applied directly

# ---- time of the gcd2.h kernels --------------------------------------------------------------------------------------
def load_fwd(L): return ntt_load(L) + CH_CALL + ntt_any(L, 0)
def unload_inv(L): return ntt_any(L, 1) + trim(L) + FIT + CH_CALL

def apply_dir(e, n):               # entries <= e <= 48, vectors <= n: schoolbook accumulation into c and d
    no = n + e - 1
    return 2 * (CH_ZERO * no + CH_CALL + 2 * (CH_SCHOOL * e * n + CH_OUTER * e) + trim(no) + FIT) + 4 * CH_CALL

def apply_cyc(e, n, L):
    """mat_apply_cyc with matrix entries <= e and vector entries <= n coefficients at length L: the larger of the
    direct branch (entries <= 48) and the cyclic branch; plus the identity and size tests."""
    d = apply_dir(min(e, CYC_MIN), n)
    if e <= CYC_MIN: return d + 64                             # the cyclic branch needs an entry above 48
    cyc = (6 * load_fwd(L) + (CH_PMAC + CH_PMUL + CH_PMACC) * L + 3 * CH_PAR + 2 * unload_inv(L) + CH_CALL)
    return max(cyc, d) + 64

def matmul_dir(x, y):              # 8 products (one side <= 48) and 4 sums, fits
    return 8 * mul(x, y) + 4 * addsub(x + y - 1, x + y - 1) + 4 * FIT + 8 * CH_CALL

def matmul_cyc(eS, eQ, L):
    d = max(matmul_dir(min(eS, CYC_MIN), eQ), matmul_dir(eS, min(eQ, CYC_MIN)))
    if eS <= CYC_MIN or eQ <= CYC_MIN: return d + 64          # the cyclic branch needs entries above 48 in both
    cyc = 8 * load_fwd(L) + 2 * (CH_MAT2 * L + CH_PAR) + 4 * unload_inv(L) + CH_CALL
    return max(cyc, d) + 64

def qmul(qn, e):                   # Q R: two products q R1j and two subtractions, fits
    return 2 * (mul(qn, e) + addsub(e, qn + e - 1) + FIT) + CH_CALL

def mullow(k):                     # low k coefficients of a product of two operands of at most k coefficients
    L = pick_len(2 * k - 1)
    fast = 2 * CH_COPY * L + CH_CALL + 2 * ntt_any(L, 0) + CH_PMUL * L + CH_PAR + unload_inv(L)
    school = 2 * trunc(k, k) + mul_school(min(k, MUL_SCHOOL), k) + trim(2 * k) + FIT
    return (max(fast, school) if k > MUL_SCHOOL else school) + CH_CALL

def divmod_school(na, q, nb):      # poly_divmod's schoolbook branch (copy of a, q steps over nb coefficients)
    return copy(na) + FE_INV + CH_AXPY * q * nb + CH_PMUL * q + CH_CALL + trim(nb) + trim(q) + 2 * FIT

def divmod2_ub(na, qmax, nbmax):
    """poly_divmod2 for any dividend of at most na coefficients, quotient length at most qmax and divisor of at most
    nbmax coefficients. Each term is nondecreasing in the one size it depends on and is evaluated at its maximum;
    the remainder transform length pick_len(max(nb, q)) is at most pick_len(min(na, max(nbmax, qmax)))."""
    qmax = min(qmax, na); nbmax = min(nbmax, na)
    school = max(divmod_school(na, min(qmax, SCHOOL_MAX), nbmax), divmod_school(na, qmax, min(nbmax, SCHOOL_MAX)))
    if qmax <= SCHOOL_MAX or nbmax <= SCHOOL_MAX: return school + copy(na) + 64
    m = qmax; L = pick_len(min(na, max(nbmax, qmax)))
    fast = (CH_COPY * 2 * m + 2 * CH_CALL + trim(m) + inv_series(m) + mullow(m) + CH_COPY * m + CH_CALL
            + 2 * (ntt_load(L) + ntt_any(L, 0)) + CH_PMUL * L + CH_PAR + ntt_any(L, 1)
            + CH_REM * nbmax + CH_CALL + trim(nbmax) + FIT + trim(m) + 3 * CH_CALL)
    return max(fast, school) + copy(na) + 64

def sizes(N):
    m = (N + 1) // 2; N1 = N - m; m1 = (N1 + 1) // 2; N2 = max(N1 - 1, 0)
    return dict(m=m, N1=N1, m1=m1, N2=N2, eR=N1 // 2 + 1, eS=N2 // 2 + 1, qn=N - m + 1, dn=m + m1, rn=N // 2 + 1)

def l_intervals(m1):
    """Offsets l - m of deg d = l (m <= l <= m + m1 - 1) split as {0}, [1, 1], [2, 3], [4, 7], ..., capped at m1 - 1."""
    out = [(0, 0)]; lo = 1
    while lo <= m1 - 1:
        hi = min(2 * lo - 1, m1 - 1); out.append((lo, hi)); lo = hi + 1
    return out

@lru_cache(maxsize=None)
def hgcd2(N, want_m, want_p):
    """Upper bound on the charge of hgcd2(a, b, want_m, want_p) for deg a <= N (all paths; early returns are
    prefixes of the path charged here). Sizes from Lemma H: entries of R <= eR, deg c <= N, deg d = l with
    m <= l <= m + m1 - 1 on the full path. Given l: quotient length <= N - l + 1, divisor l + 1, second call on degree
    2 (l - m), entries of S <= l - m + 1, vectors of S (d, e) <= l + 1, entries of Q R and of the result
    <= N // 2 + 1. The part after the division is bounded on each interval of l - m (l_intervals) with every term at
    the interval end that maximizes it (each term is monotone in l), and the maximum over the intervals is taken."""
    base = CH_CALL + 2 * CH_CALL + 2 * CH_CALL               # call, mat_id or the moves, the frees
    if N <= 0: return base
    s = sizes(N); m, m1, eR, rn = s['m'], s['m1'], s['eR'], s['rn']
    c = base + 2 * shr(N + 1, m)
    c += hgcd2(s['N1'], 1, 0)
    if want_m: c += 4 * copy(eR) + CH_CALL
    c += apply_cyc(eR, N + 1, pick_len(N + 1))
    tail = 0
    for lo, hi in l_intervals(m1):
        qmax = N - (m + lo) + 1; nbmax = m + hi + 1; n2 = 2 * hi
        eS = n2 // 2 + 1
        t = divmod2_ub(N + 1, qmax, nbmax) + CH_CALL
        if want_m: t += qmul(qmax, eR)
        t += 2 * shr(nbmax, 0) + CH_CALL                     # d0, e0
        t += hgcd2(n2, 1, 0) if n2 > 0 else base
        if want_p:
            if want_m: t += 4 * copy(eS) + CH_CALL
            t += apply_cyc(eS, nbmax, pick_len(nbmax))
        if want_m: t += matmul_cyc(eS, rn, pick_len(rn))
        tail = max(tail, t)
    return c + tail

def small_div(n):                  # one division step of the Euclid tail on at most n coefficients
    return rem_blocked_ub(n, n) + 100

@lru_cache(maxsize=None)
def gcd_bound2(N):
    """poly_gcd2(a, b), deg a = N > deg b. Per level: hgcd2 with pair output, or (when b has at most 48 coefficients)
    the direct path, whose at most 48 small divisions on at most 48 coefficients are charged in place of the hgcd;
    then one division (a <= n + 1, b <= ceil(n / 2) coefficients); then the Euclid tail and the normalization."""
    total = 0; n = N
    while n + 1 > SCHOOL_MAX:
        m = (n + 1) // 2
        total += max(hgcd2(n, 0, 1), SCHOOL_MAX * small_div(SCHOOL_MAX))
        total += rem_blocked_ub(n + 1, n) + 100                  # c / d (d < m), or a / b directly (b <= 48)
        n = m - 1
    total += (n + 1) * small_div(n + 1)
    total += FE_INV + scale(n + 1) + CH_CALL
    return total

# ---- memory (live coefficients) -------------------------------------------------------------------------------------
class Live:
    """Replays allocations and releases; every object is allocated and released at the same upper bound of its size."""
    def __init__(self, cur=0): self.cur = cur; self.peak = cur
    def a(self, s): self.cur += s; self.peak = max(self.peak, self.cur)
    def f(self, s): self.cur -= s
    def sub(self, inner_peak): self.peak = max(self.peak, self.cur + inner_peak)

def inv_series_mem(k):             # g (k) and the two Newton buffers of the last step (schoolbook steps: <= 400)
    return k + max(2 * pick_len(k), 400)

def mullow_mem(k):                 # peak above its inputs, and the size kept
    if k <= MUL_SCHOOL: return 4 * k + 2, k
    return max(2 * pick_len(2 * k - 1), 2 * k + 2 * MUL_SCHOOL + 2), k

def divmod2_mem(na, qmax, nbmax, want_q):
    """Peak live coefficients allocated by poly_divmod2 above its inputs (outputs included), any dividend <= na,
    quotient <= qmax, divisor <= nbmax coefficients. Returns (peak, kept)."""
    qmax = min(qmax, na); nbmax = min(nbmax, na)
    m = qmax; L = pick_len(min(na, max(nbmax, qmax)))
    school = na + m                                            # copy of a and the quotient, before fitting
    fast = max(m + m + inv_series_mem(m),                      # rat, rbt, ib with the Newton buffers
               m + m + mullow_mem(m)[0],                       # rat, ib, product buffers
               m + m,                                          # tt, qq
               m + 2 * L,                                      # qq, X, Y
               m + L + nbmax)                                  # qq, X, r
    kept = nbmax + (m if want_q else 0)
    if qmax <= SCHOOL_MAX or nbmax <= SCHOOL_MAX: return max(school, na), kept
    return max(school, fast, na), kept

def mul_mem(na, nb):               # poly_mul: peak above inputs, size kept
    rn = na + nb - 1
    if min(na, nb) <= SCHOOL_MAX: return rn, rn
    return 2 * pick_len(rn), rn

def apply_mem(e, na, nb, L, out_c, out_d):
    """mat_apply_cyc consuming a (na), b (nb) and four entries (e): (peak, kept) relative to the moment before the
    call, inputs included in the starting level (they are part of the caller's live set and released here)."""
    v = Live(na + nb + 4 * e)
    # cyclic branch
    v.a(L); v.f(na); v.a(L); v.f(nb); v.a(L); v.f(e); v.a(L); v.f(e); v.f(L); v.a(L); v.f(e); v.f(L); v.a(L); v.f(e)
    v.f(L); v.f(L)                                             # V, A; now T, U
    v.f(L - out_c); v.f(L - out_d)                             # c, d fitted to their lengths
    cyc_peak = v.peak
    # direct branch (entries <= 48): c and d accumulated in place, then R, a, b released and c, d fitted
    e2 = min(e, CYC_MIN); rn = e2 + max(na, nb) - 1
    dir_peak = na + nb + 4 * e + 2 * rn if e > 0 else 0
    return max(cyc_peak, dir_peak), out_c + out_d

def qmul_mem(qn, e):               # Q R from R (4 e) and q (qn): peak above (R + q), size of Q R kept
    rn = qn + e - 1
    v = Live(0)
    for _ in range(2):
        pk, kept = mul_mem(qn, e); v.sub(pk); v.a(kept); v.a(max(e, rn)); v.f(kept); v.f(e)
    return v.peak, None

def matmul_mem(eS, eQ, L, rn):     # S (4 eS) and QR (4 eQ) consumed; result 4 rn: peak above the inputs' level
    v = Live(4 * eS + 4 * eQ)
    for _ in range(4): v.a(L); v.f(eS)
    for _ in range(2):
        v.a(L); v.f(eQ); v.a(L); v.f(eQ)
        v.f(L - rn); v.f(L - rn)
    v.f(4 * L)
    cyc = v.peak
    prn = max(min(eS, CYC_MIN) + eQ - 1, eS + min(eQ, CYC_MIN) - 1)
    w = Live(4 * eS + 4 * eQ)
    for _ in range(4): w.a(prn); w.a(prn); w.a(prn); w.f(2 * prn)
    return max(cyc, w.peak)


def rem_round(t, L, nb):           # one block of poly_rem_blocked: t quotient coefficients, transform length L
    return (CH_COPY * t + CH_CALL + mullow(t) + CH_COPY * L + CH_CALL + ntt_any(L, 0) + CH_PMUL * L + CH_PAR
            + ntt_any(L, 1) + CH_REM * nb + CH_CALL + 6 + 2 * CH_CALL)

def rem_school(na, nb):            # in-place schoolbook branch: m = na - nb + 1 quotient steps over nb coefficients
    m = na - nb + 1
    return FE_INV + CH_AXPY * m * nb + CH_PMUL * m + CH_OUTER * m + trim(nb) + FIT + 2 * CH_CALL

@lru_cache(maxsize=None)
def rem_blocked_ub(na, nbmax):
    """poly_rem_blocked for a dividend of at most na coefficients and a divisor of at most nbmax coefficients:
    the maximum over every divisor size nb <= nbmax (enumerated) of the charge at dividend na, which is
    nondecreasing in na for fixed nb. Trims over all rounds remove at most na coefficients in total."""
    best = 0
    for nb in range(1, min(nbmax, na) + 1):
        m = na - nb + 1; K = min(m, nb)
        if nb <= SCHOOL_MAX or K <= SCHOOL_MAX:
            c = rem_school(na, nb)
        else:
            L = pick_len(nb); rounds = -(-m // K)
            c = (CH_COPY * K + CH_CALL + trim(K) + inv_series(K) + ntt_load(L) + ntt_any(L, 0)
                 + rounds * rem_round(K, L, nb) + 6 * na + FIT + 3 * CH_CALL)
        best = max(best, c)
    return best + CH_CALL + 64

def rem_blocked_mem(na, nbmax):
    """Peak live coefficients allocated by poly_rem_blocked above its operands (the dividend is reduced in place):
    rbt and the inverse with its Newton buffers; then I, B^, and per round the window copy and the low product, or
    the quotient block and its transform buffer. Majorant at K <= min(nbmax, ceil(na / 2)), L = pick_len(nbmax)."""
    K = min(nbmax, (na + 1) // 2)
    if K <= SCHOOL_MAX: return 0
    L = pick_len(nbmax)
    return max(K + inv_series_mem(K), K + L + K + mullow_mem(K)[0], K + L + K + L)

@lru_cache(maxsize=None)
def hgcd2_mem(N, want_m, want_p):
    """Peak live coefficients of hgcd2 on deg a <= N, its inputs (a <= N + 1, b <= N coefficients) and outputs
    included, replaying the code: the inputs are released as they are transformed."""
    if N <= 0: return 2 * (N + 1) + 4
    s = sizes(N); m, N1, N2, eR, eS, qn, dn, rn = s['m'], s['N1'], s['N2'], s['eR'], s['eS'], s['qn'], s['dn'], s['rn']
    v = Live(2 * N + 1)                                        # a, b
    v.sub(hgcd2_mem(N1, 1, 0))                                 # a0, b0 inside, released by the call
    v.a(4 * eR)                                                # R
    if want_m: v.a(4 * eR)                                     # the copy applied
    c_sz, d_sz = N + 1, dn                                     # deg c <= N, deg d <= m + m1 - 1 (Lemma H)
    pk, kept = apply_mem(eR, N + 1, N, pick_len(N + 1), c_sz, d_sz)
    v.f(2 * N + 1 + 4 * eR); v.sub(pk); v.a(kept)              # a, b and the applied entries -> c, d
    pk, kept = divmod2_mem(N + 1, qn, dn, want_m); v.sub(pk); v.a(kept)
    e_sz = dn                                                  # e: at most nb - 1 < dn coefficients
    v.f(c_sz)                                                  # c released; d, q, e (kept) live
    if want_m:
        pk, _ = qmul_mem(qn, eR); v.sub(pk); v.a(4 * rn); v.f(4 * eR)   # R consumed into Q R
    if want_m: v.f(qn)                                         # q released
    v.a(2 * N1)                                                # d0, e0
    v.sub(hgcd2_mem(N2, 1, 0) - 2 * N1) if N2 > 0 else None    # the call holds d0, e0 (counted in its own peak)
    v.f(2 * N1); v.a(4 * eS)                                   # S
    if want_p:
        if want_m: v.a(4 * eS)
        pk, kept = apply_mem(eS, d_sz, e_sz, pick_len(dn), dn, m)
        v.f(d_sz + e_sz + 4 * eS); v.sub(pk); v.a(kept)
    else:
        v.f(d_sz + e_sz)                                       # d, e released
    if want_m:
        v.f(4 * eS + 4 * rn); v.sub(matmul_mem(eS, rn, pick_len(rn), rn)); v.a(4 * rn)
    return v.peak

@lru_cache(maxsize=None)
def gcd_mem2(N, in_level=None):
    """Peak live coefficients of poly_gcd2 on deg a = N > deg b, inputs included (in_level: their size at level 1,
    default 2 N + 1). Every polynomial handed between steps is fitted to its length, so sizes are degree bounds."""
    n = N; inputs = 2 * N + 1 if in_level is None else in_level
    peak = 0
    while n + 1 > SCHOOL_MAX:
        m = (n + 1) // 2
        peak = max(peak, inputs - (2 * n + 1) + hgcd2_mem(n, 0, 1))
        peak = max(peak, inputs + rem_blocked_mem(n + 1, SCHOOL_MAX))   # direct path when b has <= 48 coefficients
        peak = max(peak, (n + 1) + m + rem_blocked_mem(n + 1, m))       # c (<= n + 1), d (<= m) and the remainder
        inputs = m + m; n = m - 1
    peak = max(peak, inputs + rem_blocked_mem(n + 1, n + 1) + n + 1)
    return peak

if __name__ == '__main__':
    N = int(sys.argv[1])
    print(f"gcd2 time bound for degree {N}: {gcd_bound2(N):,}")
    print(f"gcd2 memory bound for degree {N}: {gcd_mem2(N):,} coefficients ({32 * gcd_mem2(N):,} bytes)")
```

### B.orchard_bound.py (SHA-256 0342f7759a75e92711f50649650231626e34212b82bb451f402a9c3423b9ca59)

```python
#!/usr/bin/env python3
"""Replayable upper bound on the charged time and memory of the two-round-line Orchard attack (attack_line.c).

Mirrors the charges of the counted C program kernel by kernel. Data-independent phases (line setup, build of f,
Horner, synthetic division, X^p mod h) are charged at their exact sizes, or at the upper bound of the residue
size where the program trims; the gcd phase is charged by the worst-case half-gcd bound of gcdbound.py, valid for
every input of the given degree. Inputs that are outcomes of the deterministic run: the number of trials and the
gcd degree of the successful trial. Standard library only, integer arithmetic only.
Usage: python3 orchard_bound.py r trials gcd_degree_on_success
"""
import sys, math, os
from functools import lru_cache
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcdbound as G
import gcdbound2 as G2
from gcdbound import (CH_COPY, CH_ZERO, CH_ADDV, CH_AXPY, CH_SCALE, CH_PMUL, CH_PSQR, CH_CALL, FE_INV, CH_PAR, EXP, CH_REV,
                      pow2ceil, pick_len, ntt, ntt_any, admissible, trim, inv_series, gcd_bound, divmod_ub, mul)
CH_PPOW5 = 10
FE = 32                                    # bytes per field element
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001

def rounds_after_line(r):                  # IDX[2..]: full rounds 2, 3, partial 4..3+r, full 60..63
    return [2, 3] + list(range(4, 4 + r)) + [60, 61, 62, 63]

def is_full(i): return i < 4 or i >= 60

def pow5_cost(n):                          # poly_pow5 on n coefficients
    if n <= 1: return CH_CALL + 8, 1, 0
    rn = 5 * (n - 1) + 1; L = pick_len(rn)
    c = CH_COPY * n + CH_ZERO * (L - n) + CH_CALL + ntt_any(L, 0) + CH_PPOW5 * L + CH_PAR + ntt_any(L, 1) + trim(rn)
    return c, rn, L

def build_f(r):
    """Charge and peak live coefficients of build_f()."""
    ops = 3 * 8 + 3 * 6 + 32
    s = [2, 2, 2]; peak = sum(s)
    idx = rounds_after_line(r)
    for k, i in enumerate(idx):
        last = (k == len(idx) - 1)
        ops += 12
        for c in (range(3) if is_full(i) else range(1)):
            cost, rn, L = pow5_cost(s[c]); ops += cost
            peak = max(peak, sum(s) + L)                 # buffer of length L while the old coordinate is live
            s[c] = rn
        rows = 1 if last else 3
        n = max(s); ns = []
        for row in range(rows):
            ops += CH_SCALE * s[0] + CH_CALL + trim(s[0])
            ops += 2 * (CH_AXPY * n + CH_CALL + trim(n))
            peak = max(peak, sum(s) + sum(ns) + s[0] + 2 * n)   # s, earlier rows, a0, a1 and the new row
            ns.append(n)
        s = ns + [1] * (3 - rows)
    return ops, s[0], peak

def powmod(nh):
    """Charge and peak live coefficients of powmod_xp(h) for deg h = nh (h has nh + 1 coefficients)."""
    n = nh; L2 = pick_len(2 * n); L1 = pick_len(n + 1)
    ops = CH_REV * (n + 1) + CH_CALL + trim(n + 1)                      # rev(D)
    ops += inv_series(n)
    Lc = pick_len(n)
    peak = (n + 1) + (n + 1) + n + 2 * Lc                                # D, rD, g, two Newton buffers
    ops += CH_COPY * n + CH_ZERO * (L2 - n) + CH_CALL + ntt_any(L2, 0)  # iDhat
    peak = max(peak, (n + 1) + n + L2)
    ops += CH_COPY * (n + 1) + CH_ZERO * (L1 - n - 1) + CH_CALL + ntt_any(L1, 0)   # Dhat, then D freed
    peak = max(peak, L2 + (n + 1) + L1)
    peak = max(peak, L2 + L1 + L2 + L1)                                  # iDhat, Dhat, B, E during the loop
    e = 1                                                                # A = X
    bits = bin(P)[3:]                                                    # bits below the top bit: 254
    for b in bits:
        an = min(e + 1, n)                                               # A = X^e, reduced once e >= n
        ops += CH_COPY * an + CH_ZERO * (L2 - an) + CH_CALL
        ops += ntt_any(L2, 0) + CH_PSQR * L2 + CH_PAR + ntt_any(L2, 1)
        a2n = 2 * an - 1
        if b == '1':
            a2n += 1; ops += CH_COPY * a2n + CH_CALL
        if a2n > n:
            qn = a2n - n
            ops += CH_ADDV * n + CH_PAR                                  # E <- S mod (x^L1 - 1)
            ops += CH_COPY * qn + CH_ZERO * (L2 - qn)
            ops += ntt_any(L2, 0) + CH_PMUL * L2 + CH_PAR + ntt_any(L2, 1)
            ops += CH_COPY * qn + CH_ZERO * (L1 - qn) + ntt_any(L1, 0) + CH_PMUL * L1 + CH_PAR + ntt_any(L1, 1)
            ops += CH_ADDV * n + CH_PAR
        else:
            ops += CH_COPY * a2n
        ops += trim(min(a2n, n))
        e = 2 * e + int(b)
    ops += ntt_any(L1, 1) + 2 * CH_CALL                                  # recover D
    return ops, peak

# ---------- worst-case live memory of the gcd phase (coefficients) ----------
# Lifetimes follow the C code: a product holds two transform buffers of length L, frees one, and keeps the
# other shrunk to the product length; a division frees all its temporaries at its end; hgcd frees its shifted
# inputs after each recursive call and its intermediate pairs as soon as the code does.
def mul_peak(na, nb):                      # (peak during the call, size kept)
    if na == 0 or nb == 0: return 1, 1
    rn = na + nb - 1
    if min(na, nb) <= G.MUL_SCHOOL: return rn, rn
    return 2 * pick_len(rn), rn

def divmod_peak(na, nb):
    """Peak of poly_divmod's own allocations (inputs excluded; quotient and remainder included)."""
    m = na - nb + 1
    if m < 1: return na
    if nb <= G.DIV_SCHOOL_B or m <= G.DIV_SCHOOL_Q: return na + m
    Lc = pick_len(m)
    held = na + nb                         # ra, rb
    p = held + m + 2 * Lc                  # ib (cap m) and the two Newton buffers
    held += m + m                          # ib, rat
    pk, kept = mul_peak(m, m); p = max(p, held + pk); held += kept
    held += m + m                          # tt, qq
    pk, kept = mul_peak(nb, m); p = max(p, held + pk); held += kept
    held += na                             # rr
    return max(p, held)

def divmod_peak_env(na, q):
    """Envelope of divmod_peak over dividends na' <= na with quotient length q (nondecreasing in na)."""
    if q < 1 or na < q: return na
    best = 0
    if q <= G.DIV_SCHOOL_Q:
        best = divmod_peak(na, na - q + 1)
    else:
        top = min(na, q + G.DIV_SCHOOL_B - 1)
        if top >= q: best = divmod_peak(top, top - q + 1)
        if na - q + 1 > G.DIV_SCHOOL_B: best = max(best, divmod_peak(na, na - q + 1))
    return best

@lru_cache(maxsize=None)
def divmod_peak_ub(na, nb_lo):
    """Peak bound of poly_divmod for dividends of at most na coefficients and quotient length at most
    na - nb_lo + 1: maximum of divmod_peak_env over q, which is a step function of q (pick_len(q), pick_len(2q - 1),
    the schoolbook switch) plus affine terms, so the maximum is at a segment end; all segment ends are evaluated."""
    qmax = na - max(nb_lo, 1) + 1
    if qmax < 1: return na
    S = max(G.DIV_SCHOOL_Q, G.DIV_SCHOOL_B, G.MUL_SCHOOL, G.INV_SCHOOL)
    cand = set(range(1, min(qmax, 2 * S + 2) + 1)) | set(range(max(1, qmax - 2 * S - 2), qmax + 1))
    for k in admissible(4 * na):
        for q in (k - 2, k - 1, k, k + 1, k + 2, (k + 1) // 2 - 1, (k + 1) // 2, (k + 1) // 2 + 1):
            if 1 <= q <= qmax: cand.add(q)
    for d in (na - G.DIV_SCHOOL_B - 1, na - G.DIV_SCHOOL_B, na - G.DIV_SCHOOL_B + 1, na - G.MUL_SCHOOL - 1, na - G.MUL_SCHOOL, na - G.MUL_SCHOOL + 1):
        if 1 <= d <= qmax: cand.add(d)
    return max(divmod_peak_env(na, q) for q in cand)

def apply_peak(e, n):                      # mat_apply: x, y products, sum c; then x, y again, sum d
    pk, rn = mul_peak(e, n)
    c = rn
    return max(pk, rn + pk, 2 * rn + c, c + pk, c + rn + pk, c + 2 * rn + c), 2 * c

def matmul_peak(x, y):                     # mat_mul: four entries, each from two products and a sum
    pk, rn = mul_peak(x, y)
    out = 0; peak = 0
    for _ in range(4):
        peak = max(peak, out + pk, out + rn + pk, out + 3 * rn)
        out += rn
    return peak, out

@lru_cache(maxsize=None)
def hgcd_peak(N, want_m, want_p):
    """Peak live coefficients allocated by hgcd on degree N (its inputs excluded, its outputs included)."""
    if N <= 0: return 4 + (2 * (N + 1) if want_p else 0)
    m = (N + 1) // 2; N1 = N - m; eR = N1 // 2 + 1; qn = N - m + 1; m1 = (N1 + 1) // 2; dn = m + m1
    N2 = max(N1 - 1, 0); eS = N2 // 2 + 1
    R = 4 * eR
    p = (2 * N1 + 1) + hgcd_peak(N1, 1, 0)                     # a0, b0 and the recursive call (R inside)
    ap, cd = apply_peak(eR, N + 1); p = max(p, R + ap)        # (c, d) = R (a, b)
    c = d = N + eR
    p = max(p, R + c + d + divmod_peak_ub(c, m + 1))          # q, e = divmod(c, d)
    live = R + d + qn + d                                     # c freed; R, d, q, e
    QR = 0
    if want_m:
        mp, QR = matmul_peak(qn, eR)
        p = max(p, live + (qn + 3) + mp)                      # Q and Q R
    live = d + d + QR                                         # R, Q, q freed: d, e, QR
    p = max(p, live + 2 * N1 + hgcd_peak(N2, 1, 0))           # d0, e0 and the second call (S inside)
    S = 4 * eS
    if want_p:
        ap, out = apply_peak(eS, dn); p = max(p, live + S + ap)
        live = live - 2 * d + out                             # d, e freed after the pair is formed
    else:
        live = live - 2 * d
    if want_m:
        mp, out = matmul_peak(eS, qn + eR - 1); p = max(p, live + S + mp)
    return p

def hgcd_out_cap(n):
    """Capacity (allocated coefficients) of each polynomial of the pair returned by hgcd(a, b, 0, 1) on degree n, over
    all return paths: copies of the inputs (n + 1), R (a, b) (products of n + 1 by eR coefficients, kept at product
    length, and their sums: n + eR), (d, e) after the division (d as before, e of the dividend's length <= n + 1), or
    S (d, e) (eS + dn - 1)."""
    if n <= 0: return n + 1
    m = (n + 1) // 2; N1 = n - m; eR = N1 // 2 + 1; m1 = (N1 + 1) // 2; dn = m + m1
    N2 = max(N1 - 1, 0); eS = N2 // 2 + 1
    return max(n + 1, n + eR, eS + dn - 1)

def gcd_mem(N):
    """Peak live coefficients of poly_gcd(a, b), deg a = N > deg b, inputs included. Arrays are counted at their
    allocated capacity, which trimming never shrinks: after a level, a = d keeps the capacity of hgcd's output and
    b = r the capacity of the dividend's length."""
    peak = 0; n = N
    in_cap = 2 * n + 1                                  # h and R = A - X at level 1
    while n + 1 > G.SCHOOL_MAX:
        peak = max(peak, in_cap + divmod_peak_ub(n + 1, 1))         # the loop may skip hgcd (b.n <= 48) and divide
        peak = max(peak, in_cap + hgcd_peak(n, 0, 1))               # hgcd with its inputs live
        co = hgcd_out_cap(n)
        peak = max(peak, 2 * co + divmod_peak_ub(n + 1, 1))         # inputs freed; division of c by d
        in_cap = co + (n + 1)                                       # a = d, b = r
        n = (n + 1) // 2 - 1
    peak = max(peak, in_cap + divmod_peak_ub(n + 1, 1))             # small Euclid; capacities never grow
    return peak

def bound(r, trials, gdeg):
    C = 216 + 21 * r
    setup = (9 * 3 + 6 + 9 + 64) + FE_INV + 40 + FE_INV + 200 + (33 * 2 * EXP + 2000) + (34 * 2 * EXP + 2 * EXP + 2000)   # line_setup (with its check), ntt_init
    per_trial = 0; mem = 0
    bops, nf, bpeak = build_f(r)
    nh = nf - 1 - 1                                    # deg f = nf - 1; deg h = deg f - 1
    trial = bops
    trial += CH_AXPY * nf + CH_AXPY * (nf - 1) + FE_INV + CH_SCALE * (nh + 1) + CH_CALL + trim(nh + 1)
    pops, ppeak = powmod(nh); trial += pops
    trial += CH_ADDV * nh + CH_CALL + trim(nh)         # R = A - X
    gops = G2.gcd_bound2(nh); trial += gops
    total = setup + trials * trial
    if gdeg > 1:                                       # find_root splitting: bounded by gdeg splits of its own cost
        total += gdeg * 256 * 2 * (2 * mul(gdeg, gdeg) + 2 * divmod_ub(2 * gdeg, 1) + 200) + gdeg * G2.gcd_bound2(gdeg)
    total += 2 * (3 * EXP + 40)                         # line_inputs of the two points
    allowance = 2 ** 20                                # constants, Montgomery conversions, output, two digest checks
    total += allowance
    mem_coeffs = max(bpeak + 2, nf + 2 * nh, ppeak, G2.gcd_mem2(nh) + 4)
    mem_bytes = mem_coeffs * FE + 8 * 2 ** 20          # 8 MiB: code with libraries, constants, 12 worker stacks, allocator metadata
    return dict(C=C, deg_f=nf - 1, deg_h=nh, build=bops, powmod=pops, gcd=gops, per_trial=trial, total=total,
                time_log2=math.log2(total / C), mem_bytes=mem_bytes, mem_log2=math.log2(mem_bytes),
                peaks=dict(build=bpeak * FE, powmod=ppeak * FE, gcd=G2.gcd_mem2(nh) * FE))

if __name__ == '__main__':
    r, trials, gdeg = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    b = bound(r, trials, gdeg)
    for k, v in b.items(): print(k, v)
```

### B.checks.py (SHA-256 d9c6c57243df4e298217074f47df6c98e9f0e928f0a61f71440b374fda91d533)

```python
"""Consistency checks of the bound tools: candidate-set exactness and monotonicity."""
import sys, random, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcdbound as G, orchard_bound as O
random.seed(5); bad = 0
for _ in range(150):                                   # divmod_ub candidate set against full enumeration
    na = random.randint(2, 4000); lo = random.randint(1, na)
    full = max(G.divmod_env(na, q) for q in range(1, na - lo + 2))
    if full != G.divmod_ub(na, lo): bad += 1; print('divmod_ub mismatch', na, lo)
    fullm = max(O.divmod_peak_env(na, q) for q in range(1, na - lo + 2))
    if fullm != O.divmod_peak_ub(na, lo): bad += 1; print('divmod_peak_ub mismatch', na, lo)
print('candidate exactness: bad', bad)
v = sum(G.divmod_ub(n, 1) < G.divmod_ub(n - 1, 1) for n in range(2, 3000)); print('divmod_ub monotone violations', v)
v = sum(G.hgcd(n, w1, w2) < G.hgcd(n - 1, w1, w2) for n in range(1, 6000) for (w1, w2) in ((0, 1), (1, 0))); print('hgcd monotone violations', v)
v = sum(O.hgcd_peak(n, w1, w2) < O.hgcd_peak(n - 1, w1, w2) for n in range(1, 4000) for (w1, w2) in ((0, 1), (1, 0))); print('hgcd_peak monotone violations', v)
Ls = G.admissible(1 << 22)
v = sum(G.ntt_any(Ls[i], inv) < G.ntt_any(Ls[i - 1], inv) for i in range(1, len(Ls)) for inv in (0, 1)); print('transform charge monotone violations', v)
```

### B.gcd2_table.py (SHA-256 3d2038cb204cd0cf40f29c3d57040771a7ee7dce8c1ebf5274dc8571ed0d5537)

```python
"""Per-level breakdown of gcdbound2.py (time and memory) at deg h = 390624, for the proof. Imports gcdbound2 read-only."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcdbound2 as G

N = int(sys.argv[1]) if len(sys.argv) > 1 else 390624
print("gcd loop levels: hgcd2 with pair output, then the blocked remainder")
n = N; tot = 0
while n + 1 > G.SCHOOL_MAX:
    h = max(G.hgcd2(n, 0, 1), G.SCHOOL_MAX * G.small_div(G.SCHOOL_MAX)); r = G.rem_blocked_ub(n + 1, n) + 100
    print(f"  deg {n:>7}: hgcd2 {h:>16,}   remainder {r:>14,}   hgcd2 memory {G.hgcd2_mem(n, 0, 1):>10,} coeff")
    tot += h + r; n = (n + 1) // 2 - 1
tail = (n + 1) * G.small_div(n + 1) + G.FE_INV + G.scale(n + 1) + G.CH_CALL
tot += tail
print(f"  Euclid tail at deg {n} and normalization: {tail:,}")
print(f"  total {tot:,} (gcd_bound2 = {G.gcd_bound2(N):,}); memory gcd_mem2 = {G.gcd_mem2(N):,} coefficients")
print()
print("hgcd2 with matrix output: fixed part and the largest interval of l - m")
print(f"{'N':>7} {'rec1':>16} {'apply R':>14} {'worst l-m':>12} {'div':>14} {'Q R':>13} {'rec2':>16} {'S QR':>14} {'T(N)':>16}")
seen = set(); level = [N // 2, N // 2 - 1]
while level:
    nxt = []
    for M in level:
        if M < 2000 or M in seen: continue
        seen.add(M); s = G.sizes(M)
        best = None
        for lo, hi in G.l_intervals(s['m1']):
            qmax = M - (s['m'] + lo) + 1; nbmax = s['m'] + hi + 1; n2 = 2 * hi; eS = n2 // 2 + 1
            parts = (G.divmod2_ub(M + 1, qmax, nbmax) + G.CH_CALL, G.qmul(qmax, s['eR']), G.hgcd2(n2, 1, 0) if n2 > 0 else 0,
                     G.matmul_cyc(eS, s['rn'], G.pick_len(s['rn'])))
            t = sum(parts) + 2 * G.shr(nbmax, 0) + G.CH_CALL + (0 if n2 > 0 else 5 * G.CH_CALL)
            if best is None or t > best[0]: best = (t, (lo, hi), parts)
        rec1 = G.hgcd2(s['N1'], 1, 0); ap = G.apply_cyc(s['eR'], M + 1, G.pick_len(M + 1))
        print(f"{M:>7} {rec1:>16,} {ap:>14,} {str(best[1]):>12} {best[2][0]:>14,} {best[2][1]:>13,} {best[2][2]:>16,} {best[2][3]:>14,} {G.hgcd2(M, 1, 0):>16,}")
        nxt += [s['N1'], s['N1'] - 1]
    level = sorted(set(nxt), reverse=True)
```


## Appendix C. Measurement allocator (not part of the algorithm)
Used for the claimed run and its resident-size measurement (Section 9). Build: `cc -O2 -dynamiclib -o pageshim.dylib pageshim.c`,
`cc -O2 -o launch launch.c`; run: `DYLD_INSERT_LIBRARIES=./pageshim.dylib ./launch ./attack_g consts.txt 0,1,2,3,4,5,60,61,62,63 20 1`
(the launcher is needed because macOS strips DYLD variables for system binaries such as /usr/bin/time).

### `pageshim.c` (SHA-256 d4512daf9ae5baab05edbcf3564b62d13dcfd393d728a6dfc39da8c1da85095b)

```c
// Allocator shim for measurement only (the frozen program is unchanged): arrays of >= 64 KiB are placed by a bump
// pointer in a reserved virtual range that is never reused, and their pages are returned to the OS on free (and the
// tail pages on a shrinking realloc). Physical memory then tracks the live large arrays page by page. Smaller requests
// go to the system allocator.
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/mman.h>
#include <pthread.h>
#include <malloc/malloc.h>
#define BIG (64u << 10)
#define PG 16384u
#define RESERVE (1ull << 40)
static uint8_t *base, *top;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
typedef struct { size_t len; size_t pad[7]; } hdr;           // 64-byte header just before the user pointer
static int ours(void *p) { return base && (uint8_t *)p >= base && (uint8_t *)p < base + RESERVE; }
static void init(void) {
    if (base) return;
    void *r = mmap(NULL, RESERVE, PROT_NONE, MAP_ANON | MAP_PRIVATE | MAP_NORESERVE, -1, 0);
    if (r == MAP_FAILED) abort();
    base = top = r;
}
static size_t rnd(size_t n) { return (n + PG - 1) / PG * PG; }
static void *big_alloc(size_t n) {
    pthread_mutex_lock(&mu); init();
    size_t len = rnd(n + sizeof(hdr)); uint8_t *p = top; top += len;
    pthread_mutex_unlock(&mu);
    if (mmap(p, len, PROT_READ | PROT_WRITE, MAP_ANON | MAP_PRIVATE | MAP_FIXED, -1, 0) == MAP_FAILED) abort();
    ((hdr *)p)->len = len; return p + sizeof(hdr);
}
static void big_free(void *q) {
    uint8_t *p = (uint8_t *)q - sizeof(hdr); size_t len = ((hdr *)p)->len;
    mmap(p, len, PROT_NONE, MAP_ANON | MAP_PRIVATE | MAP_FIXED, -1, 0);   // discards the pages
}
static void *my_malloc(size_t n) { return n >= BIG ? big_alloc(n) : malloc(n); }
static void my_free(void *q) { if (!q) return; if (ours(q)) big_free(q); else free(q); }
static void *my_calloc(size_t a, size_t b) { size_t n = a * b; if (n >= BIG) return big_alloc(n); return calloc(a, b); }
static void *my_realloc(void *q, size_t n) {
    if (!q) return my_malloc(n);
    if (!ours(q)) {
        if (n < BIG) return realloc(q, n);
        size_t old = malloc_size(q); void *r = big_alloc(n); memcpy(r, q, old < n ? old : n); free(q); return r;
    }
    uint8_t *p = (uint8_t *)q - sizeof(hdr); size_t len = ((hdr *)p)->len, need = rnd(n + sizeof(hdr));
    if (need <= len) {                                            // shrink in place: release the tail pages
        if (need < len) mmap(p + need, len - need, PROT_NONE, MAP_ANON | MAP_PRIVATE | MAP_FIXED, -1, 0);
        ((hdr *)p)->len = need; return q;
    }
    void *r = my_malloc(n); memcpy(r, q, len - sizeof(hdr)); big_free(q); return r;
}
static void *my_aligned(size_t al, size_t n) { if (n >= BIG && al <= 64) return big_alloc(n); return aligned_alloc(al, n); }
#include <stdio.h>
__attribute__((constructor)) static void shim_loaded(void) { fputs("pageshim loaded\n", stderr); }
#define INTERPOSE(rep, orig) __attribute__((used)) static struct { const void *r; const void *o; } \
    _ip_##orig __attribute__((section("__DATA,__interpose"))) = { (const void *)(unsigned long)&rep, (const void *)(unsigned long)&orig };
INTERPOSE(my_malloc, malloc)
INTERPOSE(my_free, free)
INTERPOSE(my_calloc, calloc)
INTERPOSE(my_realloc, realloc)
INTERPOSE(my_aligned, aligned_alloc)
```

### `launch.c` (SHA-256 5390f70a3a1616f35f611fcd22a59ff91870f05e332ecd959f4016d737ee4c1d)

```c
// fork/exec argv[1..], wait, print the child's peak resident set size (bytes, macOS ru_maxrss)
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/resource.h>
int main(int argc, char **argv) {
    pid_t p = fork();
    if (p == 0) { execv(argv[1], argv + 1); perror("exec"); _exit(127); }
    int st; struct rusage ru; wait4(p, &st, 0, &ru);
    fprintf(stderr, "child_maxrss_bytes %ld status %d\n", (long)ru.ru_maxrss, WEXITSTATUS(st));
    return 0;
}
```

