# Ordinary collision for Orchard Poseidon with one partial round: round-0 absorption, degree 5^8 - 1, counted fast gcd

## 0. Summary

- **Target.** `poseidon-orchard-r1-prefix-v1`: Orchard P128Pow5T3 over Pallas, input state `[nk, rho, 2^65]`,
  full rounds 0-3, partial round 4, full rounds 60-63, deployed constants and MDS, output coordinate 0.
- **Result.** Two distinct canonical inputs with the same complete output, in `certificates/`:
  `(nk, rho) = (a, 0)` and `(a, 1)` with
  a = 21295018245332138659184472221807390184989200179957268241054586399316369967481,
  common digest `b4fd8d123c3495d91a90a26c29f9034076c2548fd1dd3765c7a5a3b8eccebd30`. The organizer checker hashes both.
- **Construction (Section 2).** With rho fixed, the state after round 0 is an affine function of the single
  variable t = (nk + c_{0,0})^5 (Lemma 1). The difference of the two outputs is a polynomial D(t) of degree
  5^8 - 1 = 390,624 (Lemma 2), five times smaller than the degree 5^9 - 5 in the variable nk. A root t of D in
  F_p gives nk = t^(1/5) - c_{0,0} (x -> x^5 is a bijection of F_p) and a collision (Lemma 3).
- **Algorithm (Section 3).** X^p mod D by 254 squarings with transform-based multiplication and a precomputed
  Newton inverse, then gcd(D, X^p - X) by a recursive half-gcd, then the root. Deterministic: no coins.
- **Cost (Section 5).** The algorithm is a counted program (Appendix): every kernel adds an itemized charge of
  field operations, 256-bit loads/stores, address arithmetic and loop control to a counter. The executed total
  is 438,774,246,867 operations; with a 2^20 allowance for setup and output, 438,775,295,443. Divided by
  C(1) = 237: T = 1,851,372,554.6 units, log2 T = 30.78595; **time_log2 = 30.79**.
- **Memory (Section 6).** Peak of all allocated arrays, tracked by the program's allocator: 250,662,624 bytes;
  with 2 MiB for code, constants and stack, 252,759,776 bytes = 2^27.913; **memory_log2_bytes = 27.92**.
- **Success probability 1** (Section 4): the procedure is deterministic on the fixed target and its execution
  returned a gcd of degree 1 and the pair above. Normalized cost 30.79 + (27.92 - 20) = 38.71.

## 1. Target and notation

p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001. The permutation acts on three field
elements. Round i adds the round constants c_{i,0..2}, applies x -> x^5 to all three coordinates (full rounds
0-3 and 60-63) or to coordinate 0 only (partial round 4), and multiplies by the 3x3 MDS matrix M. The hash of a
canonical input (nk, rho) is coordinate 0 of the permutation of [nk, rho, 2^65] through the index list
(0, 1, 2, 3, 4, 60, 61, 62, 63) (repository `verifier/poseidon.py`, rounds = 1). Constants and MDS are the
pinned deployed values (`pareto/orchard-pallas-constants.json`). Cost model `orchard-field-ram-v2`: one field
addition, subtraction or multiplication, or one 256-bit word operation (load, store, add, bitwise, shift,
comparison, branch) costs 1/C, C(1) = 216 + 21 = 237; inversion and exponentiation are charged by their
constituent operations.

## 2. The polynomial

**Lemma 1 (round 0 is absorbed).** Fix rho. For every nk, the state after round 0 is
s_r = M_{r,0} t + k_r (r = 0, 1, 2), with t = (nk + c_{0,0})^5 and constants
k_r = M_{r,1} (rho + c_{0,1})^5 + M_{r,2} (2^65 + c_{0,2})^5.

*Proof.* Round 0 is full: it adds the constants, raises each coordinate to the fifth power and applies M.
Coordinates 1 and 2 of the input are the constants rho and 2^65, so after the S-box they are the constants
(rho + c_{0,1})^5 and (2^65 + c_{0,2})^5, and coordinate 0 is t. M is linear. QED.

So the output for (nk, rho) is F_rho(t), where F_rho is the polynomial obtained by running rounds
1, 2, 3, 4, 60, 61, 62, 63 on the affine state of Lemma 1 symbolically in t. Each full round raises the degree
of every coordinate to five times the largest degree; the partial round raises coordinate 0 to the fifth power
and the MDS spreads it. Starting from degree 1: rounds 1, 2, 3 give 5, 25, 125; round 4 gives 625; rounds
60-63 give 3,125, 15,625, 78,125 and 390,625 = 5^8.

**Lemma 2.** D(t) = F_0(t) - F_1(t) has degree 390,624. *Proof (computational, in the program).* The leading
coefficient of F_rho does not depend on rho (the coefficient of t^(5^8) is a product of entries of M and does
not involve k_r), so the top terms cancel; the program builds D and reports its degree, 390,624 (Section 7).
The degree drives only the cost; soundness does not depend on it.

**Lemma 3 (soundness).** If t in F_p satisfies D(t) = 0, then nk = t^(1/5) - c_{0,0}, where
1/5 = 5^(-1) mod (p - 1) (gcd(5, p - 1) = 1), gives H(nk, 0) = H(nk, 1), and the inputs (nk, 0) and (nk, 1)
are distinct canonical inputs. *Proof.* (nk + c_{0,0})^5 = t, so by Lemma 1 both inputs reach the affine states
of t for rho = 0 and rho = 1, and their outputs are F_0(t) = F_1(t). The second coordinates differ. Both
values are reduced below p. QED. The organizer checker confirms the equality by hashing the two files.

## 3. The algorithm

Input: the fixed target. No coins.

1. **Build D.** For rho in {0, 1}: form the affine state of Lemma 1 (degree-1 polynomials in t); for each of
   the rounds 1, 2, 3, 4, 60, 61, 62, 63, add the round constants to the constant coefficients, raise the
   affected coordinates to the fifth power by one forward and one inverse number-theoretic transform (NTT) at
   the first power of two at least 5 d + 1, with three pointwise multiplications, and apply M (only row 0 in
   the last round). D = F_0 - F_1, made monic by one inversion.
2. **X^p mod D.** n = deg D. Precompute iD = rev(D)^(-1) mod x^(n-1) by Newton iteration
   g <- g (2 - rev(D) g) with doubling precision. Starting from A = X, for each of the 254 bits of p below the
   top bit: A <- A^2 mod D (product by NTT of length 2^20; quotient q = rev(rev(A^2)_top iD mod x^qn), product
   q D by NTT, remainder A^2 - q D), and when the bit is 1, A <- X A mod D (shift, then subtract the leading
   coefficient times D).
3. **gcd.** R = A - X. g = gcd(D, R) by the recursive half-gcd of Section 3.1, finished by Euclidean steps
   with fast division, and made monic.
4. **Root.** If deg g = 1, t = -g_0. (If deg g >= 2, the program splits g by gcd(g, (X + delta)^((p-1)/2) - 1),
   delta = 0, 1, ...; if deg g = 0 it would report failure. Neither branch ran.) nk = t^(1/5) - c_{0,0} by one
   exponentiation. Output (nk, 0) and (nk, 1), check their digests.

**3.1 Half-gcd.** For deg a > deg b, `hgcd(a, b)` returns a 2x2 polynomial matrix M with (c, d) = M (a, b),
deg c >= m > deg d, m = ceil(deg a / 2): if deg b < m return I; recurse on (a div x^m, b div x^m) giving R;
(c, d) = R (a, b); if deg d < m return R; one division c = q d + e and Q = [[0, 1], [1, -q]]; if deg e < m
return Q R; with k = 2 m - deg d, recurse on (d div x^k, e div x^k) giving S; return S Q R. Products use the
NTT above 48 coefficients and schoolbook below; divisions use Newton inverses above 48 coefficients. The
whole computation is exact arithmetic over F_p; the gcd it returns is the unique monic gcd, whatever the
order of operations.

## 4. Success probability

The procedure reads no random words; on the fixed target every execution performs the same operations and
returns the same result. Its execution (Section 7) returned deg g = 1 and the root t, and the pair above, whose
digests the organizer checker recomputes. A deterministic procedure that outputs a pair on its only executed
path succeeds with probability 1. No trial, restart or search over rho is used. The degree-1 outcome is the
result of the exact gcd computation; Lemma 3 makes the output a collision independently of it.

**Uniqueness and relation to entry 94e9246a.** gcd(D, X^p - X) is the product of (X - t) over the roots t of
D in F_p. Degree 1 means D has exactly one root in F_p, so H(nk, 0) = H(nk, 1) has exactly one solution nk.
Entry 94e9246a (Th0rgal, cost 51) solved the same equation with nk as the variable and found the same nk; the
pair is therefore necessarily the same pair. This package does not claim a new pair. It claims a cheaper
construction of it: degree 5^8 - 1 instead of 5^9 - 5 (Lemma 1), a quasi-linear half-gcd instead of an
O(n^2) Euclidean algorithm, and an executed operation count.

## 5. Charged time

**Machine and counting.** The program (Appendix) runs on 256-bit words and Pallas field elements, and keeps a
counter OPS. Every kernel adds, per call, an itemized charge per processed item plus a fixed 64 per call
(setup, size computations, branches, return). The per-item charges are upper bounds on the operations of the
loop bodies as written, each counting field operations, 256-bit loads and stores, address computations and
loop control (increment, comparison, branch) at weight 1:

| kernel | charge per item | composition |
| --- | ---: | --- |
| NTT butterfly | 16 | 3 loads (u, v, twiddle), 1 mul, 1 add, 1 sub, 2 stores, 4 address operations (2 adds, a shift for the power-of-two stride, an add), 3 loop, 1 spare |
| bit-reversal permutation, per index | 20 | incremental reverse counter (amortized at most 2 inner steps of and, branch, xor, shift, plus the final xor: at most 9), comparison and branch, swap (2 loads, 2 stores, 2 addresses), 3 loop; plus 64 x 8 x log2 L per call for the 64 block starts |
| inverse-transform scaling | 8 | load, mul, store, 2 address, 3 loop |
| pointwise product | 10 | 2 loads, mul, store, 3 address, 3 loop |
| pointwise square | 8 | load, mul, store, 2 address, 3 loop |
| pointwise fifth power | 10 | load, 3 mul, store, 2 address, 3 loop |
| copy | 7 | load, store, 2 address, 3 loop |
| zero fill | 5 | store, address, 3 loop |
| vector add/sub | 12 | 2 loads, add or sub, store, 3 address, 2 length tests, 3 loop |
| scaled add (axpy) | 13 | 2 loads, mul, add or sub, store, 3 address, 2 length tests, 3 loop |
| schoolbook term | 12 | 3 loads, mul, add, store, 3 address, 3 loop |
| field inversion | 1,546 | exponentiation by p - 2: at most 255 squarings and 255 multiplications, 3 per step with loop |
| trailing-zero trim | 4 per removed coefficient + 2 | load, test, branch, decrement |

A transform of length L costs (L / 2) log2 L butterflies, L bit-reversal steps and, for the inverse, L scalings
and one exponentiation for 1/L. The twiddle tables (2^19 entries each for transforms up to 2^20) are built once
and charged. The program counts what it executes: the item counts are the actual loop lengths of each call.

**Executed totals** (Section 7):

| phase | operations |
| --- | ---: |
| build D (both rho, all rounds, monic) | 1,543,278,986 |
| X^p mod D (Newton inverse and 254 squarings with reductions) | 389,126,971,630 |
| gcd, root and fifth root | 48,103,994,579 |
| **counted total** | **438,774,246,867** |
| allowance: reading the 201 constants, Montgomery conversions, writing and hashing the two messages (two permutations = 474 operations), program setup | 1,048,576 |
| **charged total** | **438,775,295,443** |

T = 438,775,295,443 / 237 = 1,851,372,554.61 units; log2 T = 30.785948. Submitted time_log2 = 30.79, an
upper bound: 438,775,295,443^100 < 2^3079 * 237^100 (checked in integers), and it is not rounded down.

## 6. Memory

The program allocates every array through one function that adds its size to a running total and keeps the
peak (`xalloc`; `xfree` subtracts). Peak over the run: 250,662,624 bytes. It is reached during the squarings of
step 2 (D, its Newton inverse, the current power, transform buffers of 2^20 elements of 32 bytes, and the
twiddle tables of 2 x 2^19 elements). Adding 1 MiB for code and constants and 1 MiB for stack and
bookkeeping: 252,759,776 bytes = 2^27.9132; submitted memory_log2_bytes = 27.92. There is no stored
advice: the pair is the output of the procedure, not an input. Normalized cost: 30.79 + 7.92 = 38.71.

## 7. Execution record

The Appendix sources (SHA-256: attack.c a7a10699f1b376eda5a64fdd8c32364d0619c038472fadfdc64e88b9c988c1d4,
poly.h 7cd30a675978ae761c2ec85e43639907ca6f2306a6c2c03d6852ccb3ab0e9d3c,
field.h 40ed7163f0041831b8c06291a5e9ec31e75a4d5be8403b7dc319a73e81c3ab78) were compiled with
`cc -O3 -march=native -o attack attack.c` and run as
`./attack consts.txt 0,1,2,3,4,60,61,62,63 0 1 20`, where consts.txt lists the 64 x 3 round constants and the
3 x 3 MDS of `orchard-pallas-constants.json` in hexadecimal (SHA-256
48c2b6ed216545d8a5d850b3d0c37a4969e05f84630c097a31c59fd768bc1494). Output:

```text
degree_D 390624
gcd_degree 1
root_t 15555c40fe90542acff180e72ff587052e545b862ecba0d51f02ea363233bb6a
ops_build 1543278986
ops_powmod 389126971630
ops_gcd 48103994579
ops_total 438774246867
mem_peak_bytes 250662624
```

Wall time 175 seconds on a 12-core laptop. Two earlier runs of the same program before a change to the
bit-reversal loop (the code now walks the incremental counter that the charge assumes) returned the same
root. nk = t^(1/5) - c_{0,0} was formed and both messages were hashed with the repository's
`verifier/poseidon.py` (rounds = 1): equal digests b4fd8d12...bd30.

The program was also checked on reduced index lists, where it produced collisions verified by an independent
Python implementation of the permutation: (0, 60), (0, 1, 60), (0, 4, 60), (0, 1, 61), (0, 1, 2, 60),
(0, 1, 2, 3, 60), (0, 1, 2, 3, 4, 60) and (0, 1, 2, 3, 4, 60, 61), with D of degrees 4, 24, 24, 24, 124, 624,
3,124 and 15,624; on the last two, some rho pairs gave gcd degree 0 or 2 (the degree-2 case was split by step 4
and also gave a verified collision). Field arithmetic was checked against Python integers on 2,003 products,
sums and differences.

## 8. Limitations

- The charges are itemized upper bounds per loop body of the listed code, not a count of machine instructions
  of a compiled binary; the parallel split of loops (macOS dispatch) is an implementation choice and does not
  change the counted work, which is the sequential total.
- The organizer does not rerun the 175-second computation; the record above, the sources and the certificate
  are the evidence. The certificate is checked by the organizer.
- Only r = 1 is claimed here.

## 9. Credit

Th0rgal (entry 94e9246a, r = 1, cost 51) introduced this line on the track: fix rho in {0, 1}, form the
difference polynomial in nk and take gcd with X^p - X, executed, with the same pair as its output. This
package keeps that approach and adds the round-0 absorption, the half-gcd, and the counted program. Written
by Claude Opus 5.5 in Claude Code.

## Appendix A. attack.c

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

// ---------- X^p mod D (D monic, degree n) ----------
static poly powmod_xp(const poly *D) {
    long n = deg(D);
    // precompute inverse of reversed D modulo x^(n-1) for quotients of degree <= n-2
    poly rD = poly_rev(D, D->n);
    poly iD = poly_inv_series(&rD, n - 1);
    poly_free(&rD);
    poly A = poly_new(2); A.c[1] = ONE; A.n = 2;   // X
    if (n == 1) { poly q, r; poly_divmod(&A, D, &q, &r); poly_free(&A); poly_free(&q); A = r; }
    fe pm = P;
    int top = 255; while (!((pm.v[top / 64] >> (top % 64)) & 1)) top--;
    long done = 0; double t0 = now();
    for (int b = top - 1; b >= 0; b--) {
        // square and reduce: A2 = A^2 (deg <= 2n-2); q = rev(rev(A2) * iD mod x^(n-1)); A = A2 - q D
        poly A2 = poly_sqr(&A);
        poly_free(&A);
        if (A2.n > n) {
            long qn = A2.n - n;    // quotient length (<= n-1)
            poly rA = poly_rev(&A2, A2.n); poly rAt = poly_trunc(&rA, qn);
            poly iDt = poly_trunc(&iD, qn);
            poly t = poly_mul(&rAt, &iDt); poly tt = poly_trunc(&t, qn);
            poly q = poly_rev(&tt, qn);
            poly qD = poly_mul(&q, D);
            A = poly_sub(&A2, &qD);
            poly_free(&rA); poly_free(&rAt); poly_free(&iDt); poly_free(&t); poly_free(&tt); poly_free(&q); poly_free(&qD); poly_free(&A2);
        } else A = A2;
        if ((pm.v[b / 64] >> (b % 64)) & 1) {
            // A = X*A mod D: shift, then subtract lead * D if degree reached n
            poly S = poly_new(A.n + 1); S.n = A.n + 1; S.c[0] = (fe){{0,0,0,0}};
            memcpy(S.c + 1, A.c, sizeof(fe) * A.n); OPS += (unsigned long long)CH_COPY * A.n + CH_CALL;
            poly_free(&A);
            if (S.n - 1 == n) { fe l = S.c[n]; poly T = poly_axpy(&S, fe_neg(l), D); poly_free(&S); A = T; }
            else A = S;
        }
        done++;
        if (done % 32 == 0) { fprintf(stderr, "  powmod bit %d/%d  %.1fs  ops=%.3e  peak=%.1fMB\n", b, top, now() - t0, (double)OPS, MEM_PEAK / 1048576.0); }
    }
    poly_free(&iD);
    return A;
}

// ---------- half-gcd ----------
typedef struct { poly m[2][2]; } mat;
static mat mat_id(void) { mat M; for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) { M.m[i][j] = poly_new(1); if (i == j) { M.m[i][j].c[0] = ONE; M.m[i][j].n = 1; } } return M; }
static void mat_free(mat *M) { for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) poly_free(&M->m[i][j]); }
static poly padd(const poly *a, const poly *b) { return poly_add(a, b); }
static mat mat_mul(const mat *A, const mat *B) {
    mat C;
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {
        poly x = poly_mul(&A->m[i][0], &B->m[0][j]), y = poly_mul(&A->m[i][1], &B->m[1][j]);
        C.m[i][j] = padd(&x, &y); poly_free(&x); poly_free(&y);
    }
    return C;
}
// (c, d) = M (a, b)
static void mat_apply(const mat *M, const poly *a, const poly *b, poly *c, poly *d) {
    poly x = poly_mul(&M->m[0][0], a), y = poly_mul(&M->m[0][1], b);
    *c = padd(&x, &y); poly_free(&x); poly_free(&y);
    x = poly_mul(&M->m[1][0], a); y = poly_mul(&M->m[1][1], b);
    *d = padd(&x, &y); poly_free(&x); poly_free(&y);
}
// Q = [[0,1],[1,-q]]
static mat mat_q(const poly *q) {
    mat Q; Q.m[0][0] = poly_new(1); Q.m[0][1] = poly_new(1); Q.m[0][1].c[0] = ONE; Q.m[0][1].n = 1;
    Q.m[1][0] = poly_new(1); Q.m[1][0].c[0] = ONE; Q.m[1][0].n = 1;
    poly z = poly_new(1); Q.m[1][1] = poly_sub(&z, q); poly_free(&z); return Q;
}
// deg a > deg b >= 0 or b = 0; returns M with (c,d) = M(a,b), deg c >= m > deg d, m = ceil(deg a / 2)
static mat hgcd(const poly *a, const poly *b) {
    long da = deg(a), m = (da + 1) / 2;
    OPS += CH_CALL;
    if (b->n == 0 || deg(b) < m) return mat_id();
    poly a0 = poly_shr(a, m), b0 = poly_shr(b, m);
    mat R = hgcd(&a0, &b0); poly_free(&a0); poly_free(&b0);
    poly c, d; mat_apply(&R, a, b, &c, &d);
    if (d.n == 0 || deg(&d) < m) { poly_free(&c); poly_free(&d); return R; }
    poly q, e; poly_divmod(&c, &d, &q, &e);
    mat Q = mat_q(&q); mat QR = mat_mul(&Q, &R); mat_free(&Q); mat_free(&R); poly_free(&q); poly_free(&c);
    if (e.n == 0 || deg(&e) < m) { poly_free(&d); poly_free(&e); return QR; }
    long l = deg(&d), k = 2 * m - l;
    poly d0 = poly_shr(&d, k), e0 = poly_shr(&e, k);
    poly_free(&d); poly_free(&e);
    mat S = hgcd(&d0, &e0); poly_free(&d0); poly_free(&e0);
    mat SQR = mat_mul(&S, &QR); mat_free(&S); mat_free(&QR);
    return SQR;
}
static poly poly_gcd(poly a, poly b) {   // consumes a, b
    if (a.n < b.n) { poly t = a; a = b; b = t; }
    while (b.n > 0) {
        if (deg(&a) > deg(&b) && b.n > SCHOOL_MAX) {
            mat M = hgcd(&a, &b); poly c, d; mat_apply(&M, &a, &b, &c, &d); mat_free(&M);
            poly_free(&a); poly_free(&b); a = c; b = d;
            if (b.n == 0) break;
        }
        poly q, r; poly_divmod(&a, &b, &q, &r); poly_free(&q); poly_free(&a); a = b; b = r;
        fprintf(stderr, "  gcd step: deg a=%ld deg b=%ld ops=%.3e\n", deg(&a), deg(&b), (double)OPS);
    }
    poly_free(&b);
    fe li = fe_inv(a.c[a.n - 1]); poly g = poly_scale(&a, li); poly_free(&a); return g;
}


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
    if (argc < 6) { fprintf(stderr, "usage: attack consts idxlist beta1 beta2 logmax\n"); return 1; }
    fe_init(); load_constants(argv[1]);
    { char *s = argv[2]; nidx = 0; while (*s) { IDX[nidx++] = (int)strtol(s, &s, 10); if (*s == ',') s++; } }
    fe b1 = fe_from_u64(strtoull(argv[3], 0, 10)), b2 = fe_from_u64(strtoull(argv[4], 0, 10));
    ntt_init(atoi(argv[5]));
    double t0 = now();
    poly o1 = build_out(b1), o2 = build_out(b2);
    poly D0 = poly_sub(&o1, &o2); poly_free(&o1); poly_free(&o2);
    fe li = fe_inv(D0.c[D0.n - 1]); poly D = poly_scale(&D0, li); poly_free(&D0);
    unsigned long long ops_build = OPS;
    fprintf(stderr, "D: degree %ld  build ops %.4e  %.1fs\n", deg(&D), (double)OPS, now() - t0);
    poly A = powmod_xp(&D);
    unsigned long long ops_pow = OPS;
    fprintf(stderr, "X^p mod D done: ops %.4e  %.1fs\n", (double)OPS, now() - t0);
    // R = X^p - X mod D
    poly X = poly_new(2); X.c[1] = ONE; X.n = 2;
    poly R = poly_sub(&A, &X); poly_free(&A); poly_free(&X);
    poly Dc = poly_copy(&D);
    poly g = poly_gcd(Dc, R);
    unsigned long long ops_gcd = OPS;
    fprintf(stderr, "gcd degree %ld  ops %.4e  %.1fs\n", deg(&g), (double)OPS, now() - t0);
    printf("degree_D %ld\n", deg(&D));
    printf("gcd_degree %ld\n", deg(&g));
    if (deg(&g) >= 1) {
        fe t = find_root(poly_copy(&g));
        // a = t^(1/5) - c0 with 1/5 = 5^-1 mod (p-1): one exponentiation, charged below
        OPS += 255 * 2 * 3 + 64;
        fe_print("root_t ", t);
    }
    printf("ops_build %llu\nops_powmod %llu\nops_gcd %llu\nops_total %llu\nmem_peak_bytes %lld\n",
           ops_build, ops_pow - ops_build, ops_gcd - ops_pow, OPS, MEM_PEAK);
    return 0;
}
```

## Appendix B. poly.h

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
#define CH_BFLY    16  // 3 loads (u, v, twiddle), mul, add, sub, 2 stores, 4 address ops (2 adds, shift, add), 3 loop; +1 spare
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

typedef struct { fe *c; long n; long cap; } poly;   // n = number of coefficients (deg+1); 0 = zero poly
static poly poly_new(long cap) { poly p; p.cap = cap > 0 ? cap : 1; p.c = xalloc(sizeof(fe) * p.cap); p.n = 0; return p; }
static void poly_free(poly *p) { if (p->c) xfree(p->c, sizeof(fe) * p->cap); p->c = NULL; p->n = p->cap = 0; }
static void poly_trim(poly *p) { while (p->n > 0 && fe_is_zero(p->c[p->n - 1])) { p->n--; OPS += 4; } OPS += 2; }
static long deg(const poly *p) { return p->n - 1; }
static poly poly_copy(const poly *a) { poly r = poly_new(a->n); memcpy(r.c, a->c, sizeof(fe) * a->n); r.n = a->n; OPS += CH_COPY * a->n + CH_CALL; return r; }
static poly poly_from(const fe *c, long n) { poly r = poly_new(n); memcpy(r.c, c, sizeof(fe) * n); r.n = n; OPS += CH_COPY * n + CH_CALL; poly_trim(&r); return r; }

// ---------- NTT ----------
static int LOGMAX = 0; static long LMAX = 0;
static fe *TW = NULL, *ITW = NULL;    // TW[k] = w^k, ITW[k] = w^-k, k < LMAX/2, w primitive LMAX-th root
static fe W2_32;                      // primitive 2^32-th root of unity
static void ntt_init(int logmax) {
    LOGMAX = logmax; LMAX = 1L << logmax;
    // generator 5 of the multiplicative group (Pallas, 2-adicity 32): w32 = 5^((p-1)/2^32)
    fe e = P; e.v[0] -= 1;               // p-1 (no borrow: low limb is ...0001)
    // (p-1) >> 32
    fe q = {{ (e.v[0] >> 32) | (e.v[1] << 32), (e.v[1] >> 32) | (e.v[2] << 32), (e.v[2] >> 32) | (e.v[3] << 32), e.v[3] >> 32 }};
    W2_32 = fe_pow_plain_exp(fe_from_u64(5), q);
    fe w = W2_32; for (int i = logmax; i < 32; i++) w = fe_mul(w, w);
    // check order exactly LMAX: w^(LMAX/2) = -1
    fe t = w; for (int i = 0; i < logmax - 1; i++) t = fe_mul(t, t);
    if (!fe_eq(t, fe_neg(ONE))) { fprintf(stderr, "root of unity check failed\n"); exit(1); }
    fe wi = fe_pow_plain_exp(w, (fe){{LMAX - 1, 0, 0, 0}});
    TW = xalloc(sizeof(fe) * (LMAX / 2)); ITW = xalloc(sizeof(fe) * (LMAX / 2));
    TW[0] = ONE; ITW[0] = ONE;
    for (long k = 1; k < LMAX / 2; k++) { TW[k] = fe_mul(TW[k-1], w); ITW[k] = fe_mul(ITW[k-1], wi); }
    OPS += (unsigned long long)(LMAX / 2) * 2 * (CH_AXPY) + 2000;   // table build (load, mul, store, loop), w setup
}
static void bitrev(fe *a, long L, int logL) {
    // Incremental reverse counter: going from i to i+1, clear the leading ones of j from the top and set the
    // next bit. Over a block the inner loop runs at most twice per index on average. Each of the 64 blocks
    // (a parallel split of the same sequential pass) starts from j = rev(lo), computed bit by bit.
    dispatch_apply((size_t)64, DISPATCH_APPLY_AUTO, ^(size_t blk) {
        long lo = (long)blk * (L / 64), hi = lo + L / 64; if (L < 64) { if (blk) return; lo = 0; hi = L; }
        long j = 0, x = lo; for (int b = 0; b < logL; b++) { j = (j << 1) | (x & 1); x >>= 1; }
        for (long i = lo; i < hi; i++) {
            if (i < j) { fe t = a[i]; a[i] = a[j]; a[j] = t; }
            long bit = L >> 1;
            while (j & bit) { j ^= bit; bit >>= 1; }
            j ^= bit;
        }
    });
    OPS += (unsigned long long)CH_BREV * L + CH_CALL + 64ULL * 8 * logL;   // pass + the 64 block starts
}
static void ntt(fe *a, long L, int inverse) {
    if (L > LMAX) { fprintf(stderr, "transform length %ld exceeds LMAX %ld\n", L, LMAX); exit(3); }
    int logL = 0; while ((1L << logL) < L) logL++;
    bitrev(a, L, logL);
    const fe *tw = inverse ? ITW : TW;
    for (long h = 1; h < L; h <<= 1) {
        long stride = LMAX / (2 * h);
        long groups = L / (2 * h);
        long nb = groups >= 256 ? 256 : groups;
        dispatch_apply((size_t)nb, DISPATCH_APPLY_AUTO, ^(size_t bi) {
            long g0 = (long)bi * groups / nb, g1 = (long)(bi + 1) * groups / nb;
            for (long g = g0; g < g1; g++) {
                fe *x = a + g * 2 * h;
                if (h >= 64 && groups < 256) {
                    // few large groups: parallelize inside handled below
                }
                for (long j = 0; j < h; j++) {
                    fe u = x[j], v = fe_mul(x[j + h], tw[j * stride]);
                    x[j] = fe_add(u, v); x[j + h] = fe_sub(u, v);
                }
            }
        });
        OPS += (unsigned long long)CH_BFLY * (L / 2) + CH_CALL;
    }
    if (inverse) {
        fe linv = fe_pow_plain_exp(fe_from_u64((uint64_t)L), (fe){{P.v[0] - 2, P.v[1], P.v[2], P.v[3]}});
        dispatch_apply(64, DISPATCH_APPLY_AUTO, ^(size_t blk) {
            long lo = (long)blk * (L / 64), hi = lo + L / 64; if (L < 64) { if (blk) return; lo = 0; hi = L; }
            for (long i = lo; i < hi; i++) a[i] = fe_mul(a[i], linv);
        });
        OPS += (unsigned long long)CH_SCALE * L + 2 * 256 * 3 + CH_CALL;   // scaling; L^-1 by exponentiation (2 x 255 mul + loop)
    }
}
// parallel pointwise helpers
#define PAR_FOR(L, body) dispatch_apply(64, DISPATCH_APPLY_AUTO, ^(size_t blk__) { \
        long lo__ = (long)blk__ * ((L) / 64), hi__ = lo__ + (L) / 64; \
        if ((L) < 64) { if (blk__) return; lo__ = 0; hi__ = (L); } \
        for (long i = lo__; i < hi__; i++) { body; } })

static long pow2ceil(long x) { long L = 1; while (L < x) L <<= 1; return L; }

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
#define SCHOOL_MAX 48
static poly poly_mul(const poly *a, const poly *b) {
    if (a->n == 0 || b->n == 0) { OPS += CH_CALL; return poly_new(1); }
    long m = a->n < b->n ? a->n : b->n;
    if (m <= SCHOOL_MAX) return poly_mul_school(a, b);
    long rn = a->n + b->n - 1, L = pow2ceil(rn);
    fe *x = ntt_load(a, L), *y = ntt_load(b, L);
    ntt(x, L, 0); ntt(y, L, 0);
    PAR_FOR(L, x[i] = fe_mul(x[i], y[i]));
    OPS += (unsigned long long)CH_PMUL * L;
    ntt(x, L, 1);
    xfree(y, sizeof(fe) * L);
    poly r = poly_new(rn); memcpy(r.c, x, sizeof(fe) * rn); r.n = rn; OPS += (unsigned long long)CH_COPY * rn;
    xfree(x, sizeof(fe) * L);
    poly_trim(&r); return r;
}
static poly poly_sqr(const poly *a) {
    if (a->n == 0) { OPS += CH_CALL; return poly_new(1); }
    if (a->n <= SCHOOL_MAX) return poly_mul_school(a, a);
    long rn = 2 * a->n - 1, L = pow2ceil(rn);
    fe *x = ntt_load(a, L); ntt(x, L, 0);
    PAR_FOR(L, x[i] = fe_mul(x[i], x[i])); OPS += (unsigned long long)CH_PSQR * L;
    ntt(x, L, 1);
    poly r = poly_new(rn); memcpy(r.c, x, sizeof(fe) * rn); r.n = rn; OPS += (unsigned long long)CH_COPY * rn;
    xfree(x, sizeof(fe) * L); poly_trim(&r); return r;
}
// fifth power via one forward and one inverse transform
static poly poly_pow5(const poly *a) {
    if (a->n <= 1) { poly r = poly_new(1); if (a->n == 1) { fe s = fe_mul(a->c[0], a->c[0]); s = fe_mul(s, s); r.c[0] = fe_mul(s, a->c[0]); r.n = 1; } OPS += CH_CALL + 8; return r; }
    long rn = 5 * (a->n - 1) + 1, L = pow2ceil(rn);
    fe *x = ntt_load(a, L); ntt(x, L, 0);
    PAR_FOR(L, { fe s = fe_mul(x[i], x[i]); s = fe_mul(s, s); x[i] = fe_mul(s, x[i]); });
    OPS += (unsigned long long)CH_PPOW5 * L;
    ntt(x, L, 1);
    poly r = poly_new(rn); memcpy(r.c, x, sizeof(fe) * rn); r.n = rn; OPS += (unsigned long long)CH_COPY * rn;
    xfree(x, sizeof(fe) * L); poly_trim(&r); return r;
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
// inverse of a modulo x^k (a(0) != 0), Newton iteration g <- g (2 - a g)
static poly poly_inv_series(const poly *a, long k) {
    poly g = poly_new(1); g.c[0] = fe_inv(a->c[0]); g.n = 1;
    long cur = 1;
    while (cur < k) {
        long nxt = 2 * cur < k ? 2 * cur : k;
        poly at = poly_trunc(a, nxt);
        poly ag = poly_mul(&at, &g); poly agt = poly_trunc(&ag, nxt);
        // e = 2 - a g
        poly two = poly_new(1); two.c[0] = fe_add(ONE, ONE); two.n = 1;
        poly e = poly_sub(&two, &agt);
        poly ng = poly_mul(&g, &e); poly ngt = poly_trunc(&ng, nxt);
        poly_free(&at); poly_free(&ag); poly_free(&agt); poly_free(&two); poly_free(&e); poly_free(&ng); poly_free(&g);
        g = ngt; cur = nxt; OPS += CH_CALL;
    }
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

## Appendix C. field.h

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
