# Orchard r=2: executed two-round-bypass collision with a counted operation ledger

## 1. Target

Profile `poseidon-orchard-r2-prefix-v1`: Orchard P128Pow5T3 over the Pallas field
F_p, p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001 (255 bits),
width 3, S-box x -> x^5, deployed round constants rc[i] (i = 0..63) and the deployed 3x3
MDS matrix M, both pinned in `orchard-pallas-constants.json`. The reduced permutation
applies the original full rounds 0, 1, 2, 3, the original partial rounds 4..5
(S-box on lane 0 only), and the original full rounds 60, 61, 62, 63. Each round adds
rc[i], applies the S-box layer, then multiplies by M. The hash of (nk, rho) is lane 0
of the permutation of the state [nk, rho, 2^65]; both inputs are canonical (below p) and
the output is the entire field element, 32 little-endian bytes.

Claim: an ordinary collision, two distinct canonical pairs with equal reduced hash, found
by a deterministic procedure whose complete primitive-operation count and peak memory are
stated below. Cost model `orchard-field-ram-v2`: every field addition, subtraction or
multiplication, every 256-bit load or store, comparison, branch, shift or boolean word
operation costs one unit; C(2) = 216 + 21*2 = 258 units per reduced permutation.
Normalized time T = W / C(2), `time_log2` = log2 T. Memory in bytes, including code.

Notation. x^5 is a bijection of F_p because gcd(5, p-1) = 1; its inverse is x -> x^e5 with
e5 = 5^-1 mod (p-1), so "the fifth root" is a single well-defined field element. We write
H(nk, rho) for the reduced hash. p-1 = 2^32 * 3 * 463 * (two large primes), so F_p contains
primitive roots of unity of every order 3 * 2^k with k <= 32; all transforms below are cyclic
number-theoretic transforms of such lengths.

## 2. The input line that bypasses rounds 0 and 1

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
H(nk(T), rho(T)) = f(T^5) below is asserted at three parameter values.

**Lemma 2 (degree).** Let s(T') denote the state after the round-1 MDS, an affine function
of T' by Lemma 1. Applying rounds 2, 3 (full), 4..5 (partial) and 60..63 (full) to
s(T') and taking lane 0 defines a polynomial f in F_p[T'] of degree at most
D = 5^(6+2) = 390625, and H(nk(T), rho(T)) = f(T^5) for every T.

Proof. Each S-box multiplies the degree of the lane it acts on by at most 5 and the linear
layers do not raise degrees; two bypassed rounds leave 6 full rounds and 2 partial rounds,
hence degree at most 5^(6+2). (Equality holds generically and is verified computationally:
the program in Appendix A constructs f by composition and asserts deg f = 390625; the procedure
only needs deg f < N1.) The identity with H follows from Lemma 1. QED

**Lemma 3 (soundness of the certificate).** If T'_0 != T'_1 satisfy f(T'_0) = f(T'_1), the
two inputs (nk(T_0), rho(T_0)) and (nk(T_1), rho(T_1)) with T_i = (T'_i)^e5 are distinct
canonical pairs with equal reduced hash. Proof: injectivity in Lemma 1 and Lemma 2. The
organizer checker recomputes both hashes from the certificate bytes; it does not depend on
any statement below.

## 3. The procedure

All polynomial arithmetic is over F_p. D = 390625, N1 = 393216 (the least 3*2^k >= D) and
N2 = 786432 (the least 3*2^k >= 2D-1). The procedure is deterministic: its only "random"
inputs are the preregistered stream values s_n = SHA-256("poseidon_mage r=2 trial n")
read as a little-endian integer and reduced modulo p; the certificate came from trial
n = 2, and every trial from 0 to 2 is charged. No other stream label was ever run on this
target: the label was fixed before the first execution, and the prototype and the counted run used it unchanged.

Step 1 (f, once per trial). Evaluate f at the N1 points omega^i, i < N1, omega a primitive N1-th root of
unity: each evaluation starts from the affine state s(T') of Lemma 1 and applies the
6 + 2 remaining rounds. One inverse transform of length N1 then yields the coefficients of
f, exactly, because deg f = D < N1. (Appendix A constructs f by composition instead; both
produce the same uniquely defined polynomial, and the appendix asserts agreement with the
permutation at three points.) f is discarded once q has been formed in Step 2, so it is not live
during Steps 3-5; a retry rebuilds it, and the rebuild is charged to every trial.

Step 2 (trial n). s0 = s_n; (x0, x1) = (nk(T), rho(T)) for T = s0^e5; y = H(x0, x1), which
equals f(s0). q = (f - y) / (X - s0) by synthetic division, of degree Dq := D - 1 = 390624, made monic by one
field inversion. In 4.2 and 4.3 the modulus degree is this Dq (written D there for brevity), and
N1, N2 are the least lengths 3*2^k >= Dq and >= 2 Dq - 1, which coincide with those for D. The polynomial q has as roots exactly the parameters T' != s0 with
f(T') = y.

Step 3 (Frobenius). h = X^p mod q by left-to-right binary exponentiation: with
k0 = floor(log2 Dq) = 18, the top k0+1 bits of p encode 2^k0 (p = 2^254 + c with
c < 2^126), so the running value starts as X^(2^k0), of degree below Dq, without any
reduction; the remaining 254 - k0 = 236 bits each cost one modular squaring and, for the
46 set bits among them, one multiplication by X modulo q.

Step 4 (gcd). g = gcd(q, h - X). Since X^p - X = prod_{a in F_p} (X - a), g is the product of
X - a over the F_p-roots a of q. g is computed by the half-gcd algorithm of Section 5, whose
charged operations are the ones it executed on this instance.

Step 5 (roots). deg g = 2. The roots of g are recovered by the small root finder of
Section 5 and each root T'_1 gives a second input through Lemma 1; the pair is verified by
two reduced-hash evaluations. If deg g were 0 the trial would fail and trial n+1 would run.

## 4. Operation charges

Prices follow `orchard-field-ram-v2`: one unit for every field add/sub/mul, every
256-bit load/store, comparison, branch, shift or boolean word operation. Field inversion is
x^(p-2) by a binary ladder: 254 squarings and 76 multiplications, 330 units; a fifth root
x^e5 is 254 squarings and 123 multiplications, 377 units. Nothing is free: zero-padding
stores, folding adds, copies and loop control are itemized where they occur.

4.1 Transforms. For N = 3*2^k the forward transform is decimation-in-frequency and the
inverse is decimation-in-time, so that pointwise products act on the permuted order and no
bit-reversal pass exists; the radix-3 stage is innermost and untwiddled. Twiddles are produced
by a running product (one multiplication per butterfly), so there is no twiddle table.
A radix-2 butterfly is charged 9/2 units: the twiddle update multiplication, the twiddle
product, one addition, one subtraction and one half unit of loop/address work (two
butterflies per compare-and-branch). A radix-3 butterfly (3-point DFT on three elements) is
charged 17/2 units: one multiplication, three additions, four subtractions and the half unit.
Loop control: a radix-8 pass processes eight elements, twelve butterflies, per loop iteration
(one index update, one comparison, one branch: 3 units per 12 butterflies), so 1/2 unit per
butterfly is conservative; every other per-element loop (pointwise steps, padding, copies,
folds, remainders, shifts) is unrolled eight elements per iteration and charged 1/2 unit per
element. Memory traffic: radix-2 levels run in register-blocked passes of three levels, one
load and one store per element per pass, i.e. 2/3 unit per element per level; the k mod 3
leftover levels are merged with the radix-3 level into one final pass, charged one load and one
store per element. The actual traffic is therefore 2N(floor(k/3) + 1) <= (2/3)Nk + 2N for every
k (equality at N1 = 98,304, k = 15). Hence

  T(N) = (N/2)*k*(9/2) + (2/3)*N*k + (N/3)*(17/2) + 2N = N*(35k/12 + 29/6),

T(393216) = 21,397,504 and T(786432) = 45,088,768. The 1/N scaling of an inverse transform is folded
into the preceding pointwise step as one extra multiplication per point: a pointwise square
costs 4 units (load, two multiplications, store) plus the 1/2 loop unit, a pointwise product
with a cached unscaled transform 5 units (two loads, two multiplications, store) plus 1/2; zero
padding is one store plus 1/2 per zero; a copy is one load and one store plus 1/2. These closed forms are exact rationals and are asserted
equal to the instrumented kernels of Appendix A for every N = 3*2^k from 3 to 3072, and the
transform's convolution is checked against schoolbook multiplication there.

4.2 Modular squaring of a (deg a < D) modulo the monic q of degree D (Appendix A, `SQ`), with
n = D-1, N1 >= D, N2 = 2*N1 >= 2D-1:
  S1  copy a into the length-N2 buffer A and pad (D + N2 units); A = FFT_N2(A); square
      pointwise with scaling (4 units per point); a2 = IFFT_N2(A). Since deg a^2 <= 2D-2 < N2,
      a2 = a^2 exactly. Copy a2[0:N1] to R (2*N1) and fold a2f[i] = a2[i] + a2[i+N1] for
      i < 2D-1-N1 (4 units each).
  S2  move the top n coefficients of a2 in reversed order to A[0:n] (2n), pad (N2-n), FFT_N2,
      multiply pointwise (5 units per point) by the cached transform INVQ of
      inv = rev(q)^-1 mod X^n, IFFT_N2; the low n coefficients, reversed in place (4 units per
      pair), are the quotient quot = floor(a^2 / q) (Barrett division, exact because q is monic).
  S3  pad quot to N1 (N1-n), FFT_N1, multiply pointwise (5 units) by FFT_N1(q), which is
      computed transiently into A[N1:N2] at CACHE(D+1, N1) = 2(D+1) + (N1-D-1) + T(N1) units
      (not cached, to keep the live set small), IFFT_N1 giving prod = quot*q modulo X^N1 - 1;
      rem[i] = a2f[i] - prod[i] for i < D (4 units each). Correctness: quot*q = a^2 - rem with
      deg rem < D <= N1, so reducing both sides modulo X^N1 - 1 gives prod = a2f - rem.
  Charge SQ = 264,163,016 units at modulus degree 390624, itemized in Appendix A and asserted equal to the
  instrumented kernel (results checked against an independent library) at D = 125, 625, 3125.
Multiplication by X modulo q: 13D/2 units (shift: 2D loads, D stores; subtraction of the leading
coefficient times q: D multiplications, D subtractions, D loads; 1/2 loop unit per coefficient).

4.3 Newton inverse of rev(q) modulo X^n: precision doubling m -> m2 = min(2m, n), each step two
products at the least length N(m) = 3*2^j >= m2 charged (m2+N) + (m+N) + 5 T(N) + 10 N +
2(m2-m) + (N-(m2-m)) + 3(m2-m) units; total NEWTON = 330,975,267.5 units. The cached transform
INVQ costs CACHE(n, N2) = 2n + (N2-n) + T(N2) once per trial. Powering start: acc = X^(2^k0)
is written directly (D stores).

4.4 Evaluation of f: N1 evaluations at 6 + 27*6 + 21*2 + 1 = 211 units each (affine
start, six full rounds at 27 units, 2 partial rounds at 21 units, one store), one inverse
transform T(N1) with N1 scaling multiplications, and the evaluation points omega^i produced by a
running product (one multiplication and one store each, 2 N1 units): 105,545,728 units. Peak live
words in this phase: the N1 points and the N1 evaluations.

4.5 Trial preparation: one stream draw (one SHA-256 compression, priced at 1,024 word
operations), three fifth roots (3 x 377), one reduced permutation for y (258), synthetic
division (4 units per coefficient), one inversion (330), the monic scaling (4 units per
coefficient) and forming h - X (4): 3,127,747 units per trial. Setup, once: the constants of
Lemma 1 (two inversions, a few fifth powers, products and sums), charged as a flat 2,000 units.

4.6 Finish: per root three fifth roots, one verifying permutation and an 8-unit digest
comparison, plus one permutation for the first input: 3,052 units.

## 5. The gcd stage and root extraction

5.1 Algorithm. g = gcd(q, h - X) is computed by a half-gcd in the shape of von zur Gathen
and Gerhard (Modern Computer Algebra, 11.4): hgcd(r0, r1, k) returns the 2x2 cofactor matrix
R with R*(r0, r1) = (r_j, r_{j+1}) where j is the last index with deg r0 - deg r_j <= k; it
recurses on the top 2d coefficients with d = ceil(k/2), applies the matrix, performs one
division, recurses again with the remaining budget, and composes the two matrices and the
quotient. Below k <= 128 the classical Euclidean algorithm runs on the truncated inputs. The
top level (fast_gcd) repeatedly calls hgcd(a, b, ceil(deg a / 4)), applies the half-size matrix,
performs one division, and finishes with classical Euclid once deg b <= 128; it never composes
a full-size matrix (this fraction 1/4 was chosen for its lower peak memory). All degree
bookkeeping is exact, so non-normal remainder sequences are handled by the degree tests.
The implementation was checked against an independent library gcd on random pairs of degree
50..5000, on nontrivial gcds of degrees 1, 2, 3, 7, 40, on twelve adversarial pairs built
backwards from prescribed quotient sequences with non-normal steps and quotient degrees up to
199, and on sequences of 3000 normal steps (Appendix A, test listing).

5.2 Charges. The program charges every operation it performs at its actual sizes:
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
  380 + L(4(m+1) + 2) + 2(n+1) and Newton division (inverse of the reversed divisor at precision
  L as in 4.3, two products, 4(m+1) + 2(n+1)); on this instance every division was classical.
- Roots of g (degree d <= 16): equal-degree splitting with shifts c drawn from
  SHA-256("poseidon_mage r=2 edf n") mod p (64 per draw); (X + c)^((p-1)/2) mod g is charged
  as 253 schoolbook modular squarings (4d^2 + (d-1)(4d+2) each) and popcount((p-1)/2) - 1
  multiplications by X + c (4d + (d-1)(4d+2) each), the gcd with g by classical Euclid as above,
  recursing on both factors.
Memory: the live coefficient words of every polynomial held by an active frame of the
recursion (inputs, truncated copies, matrix entries, remainders) plus transform scratch
(2N words for a transform product, m1+m2-1 for a classical one, (n+1) + L for a division).

5.3 Executed count. On this instance (trial 2, deg q = 390624) the stage performed
776,554 classical and 52,620 transform products, 390,622 classical and 0 Newton divisions in the half-gcd (the root stage adds its own, listed in the histogram) and charged 14,794,876,460 units with a peak of 3,525,986 live words; the
root stage charged 18,612 units. Appendix B reproduces `gcd_trace_r2.json`, the
histogram of every charged operation by kind and size; `halfgcd_charge.py` (Appendix A,
standard library only) recomputes the charge from that histogram and the rules above.

## 6. Totals

| phase | units | peak live words |
|---|---:|---:|
| setup (Lemma 1 constants) | 2,000 | |
| trial 0: build f (4.4) | 105,545,728 | 786,440 |
| trial 0: preparation (4.5) | 3,127,747 | 781,258 |
| trial 0: Newton inverse + cached INVQ | 377,634,306 | 1,567,680 |
| trial 0: 236 squarings x 264,163,016 + 585,936 start stores with loop control | 62,343,057,712 | 2,356,705 |
| trial 0: 46 multiplications by X | 116,796,576 | |
| trial 0: half-gcd + roots (5.3) | 14,794,877,264 | 3,525,986 |
| trial 1: build f (4.4) | 105,545,728 | 786,440 |
| trial 1: preparation (4.5) | 3,127,747 | 781,258 |
| trial 1: Newton inverse + cached INVQ | 377,634,306 | 1,567,680 |
| trial 1: 236 squarings x 264,163,016 + 585,936 start stores with loop control | 62,343,057,712 | 2,356,705 |
| trial 1: 46 multiplications by X | 116,796,576 | |
| trial 1: half-gcd + roots (5.3) | 14,794,877,264 | 3,525,986 |
| trial 2: build f (4.4) | 105,545,728 | 786,440 |
| trial 2: preparation (4.5) | 3,127,747 | 781,258 |
| trial 2: Newton inverse + cached INVQ | 377,634,306 | 1,567,680 |
| trial 2: 236 squarings x 264,163,016 + 585,936 start stores with loop control | 62,343,057,712 | 2,356,705 |
| trial 2: 46 multiplications by X | 116,796,576 | |
| trial 2: half-gcd + roots (5.3) | 14,794,895,072 | 3,525,986 |
| trial 2: finish (4.6) | 3,052 | |
| **total** | **233,223,140,860** | **3,525,986** |

Total W = 233,223,140,860 units; T = W / 258 = 903,965,662.25; `time_log2` = log2 T = 29.751693,
submitted as 29.76 (ceiling at two decimals; not a downward rounding).

Executed trials of the stream (context): trial 0: deg g = 0; trial 1: deg g = 0; trial 2: deg g = 2.

## 7. Success probability and the trial budget

The procedure reads no random coins: its inputs are the pinned constants and the
preregistered SHA-256 stream. Executed on this fixed target it performed exactly the
operations charged above and returned the certified pair at trial 2; a deterministic
procedure that returns a pair on its only control path has success probability 1. The
budget charges every trial that was executed, including trials whose gcd had degree 0.
No expectation, extrapolation or heuristic enters the claim: `heuristics` is empty. The stream
label is the only one that was ever run on this target (Section 3), so no trial is hidden.

Context only, not used by the claim: for a value y = f(s0), the cofactor q has, by the
usual random-polynomial model, an F_p-root count close to Poisson(1), so a single trial
succeeds with probability about 1 - 1/e; the executed trials of this stream are listed in
Section 6 for the record.

## 8. Certificate

`certificates/message-a.bin` encodes (x0, x1) = the inputs of parameter s0 and
`certificates/message-b.bin` the inputs of the root T'_1; the further files message-b<i>.bin encode the other roots. The expected digest
in `certificates/manifest.json` is the common reduced hash 9b9abd1e25f451b4d11f80cbc0dba9df81c7728f0ac05ba367a1fc66122fbf33 (32 little-endian
bytes). All inputs are canonical and the files differ. The organizer checker recomputes
the reduced permutation on each file; that check is independent of every count above.

## 9. Memory

Peak live storage is the maximum over the phases (Section 6, table): words of 32 bytes,
plus a fixed 2^20-byte allowance for code, constants, the stream state and the stack.
log2 of that total is 26.762941, submitted as `memory_log2_bytes` = 26.77 (ceiling at
two decimals). f is not live after Step 2 (Section 3). The normalized cost axis is
`time_log2` + max(0, `memory_log2_bytes` - 20) = 36.53 with the submitted bounds; the claim
keeps the two raw bounds separate.

## 10. Limitations and relation to prior entries

The time bound is an operation count of the stated algorithm under the organizer's
prices, not a wall-clock measurement. The executed run used the FLINT library for the
polynomial arithmetic whose results are uniquely defined objects (the polynomial f, the
residue X^p mod q, the gcd and its roots); the half-gcd stage was executed by the counted
program itself on the real instance, so its charge is the instance's executed count. The
transform charges are closed forms validated against an instrumented implementation at
lengths 3..3072 (Appendix A, self-test). The judge does not execute candidate code; the
certificate is the organizer-checked evidence of the outcome, the executed run took a few
minutes with the library arithmetic, and Appendix A reproduces every number from the recorded
sizes, trace histograms and roots. Every kernel self-test, library cross-check and histogram is
participant-produced.

Credits. The univariate root-finding of the lane-0 output with gcd(., X^p - X) and the
deterministic executed-outcome argument were introduced on this board by Th0rgal
(94e9246a); hecmas (a18c0d0a) added round-0 absorption, NTT Barrett powering and a counted
half-gcd; tanctl (b86575d7, b257d730, 0aed4072) introduced the two-round linearizing line
and worst-case fast-gcd accounting. The two-round bypass itself is the trick of Bariant,
Bouvier, Leurent and Perrin (ToSC 2022/3) for SPN CICO problems. What this package adds is
its accounting: closed forms validated against instrumented kernels, no bit-reversal passes,
scaling folded into the pointwise step, the N1-fold remainder, the transiently recomputed
FFT_N1(q), an executed and histogram-reproducible half-gcd, and f discarded after q is formed.

## Appendix A. Program listings

The executed driver (`attack.py`), the instrumented kernels with their closed forms and self-tests
(`ntt.py`, `modsq.py`, `powering.py`), the counted half-gcd and root stage (`halfgcd.py`, `gcd_stage.py`,
`roots.py`), the trace charge (`halfgcd_charge.py`) and the standard-library reproduction (`accounting.py`).
Run `python accounting.py orchard-pallas-constants.json ledger_r2.json <dir with the gcd_trace files>` to recompute
every number of Section 6 and the pair; `python ntt.py`, `python modsq.py`, `python powering.py` run the
kernel self-tests. The ledger and the trace histogram are reproduced verbatim in Appendix B.


### attack.py

```python
"""poseidon_mage counted attack driver (v1). See SPEC.md.
Executes the two-round-bypass univariate collision search at r partial rounds, charges every
phase per SPEC, writes ledger_r<r>.json and a candidate package directory.
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
        evaluation at the N1 roots of unity + one inverse transform (SPEC)."""
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

def stream(r, n): return int.from_bytes(hashlib.sha256(f"poseidon_mage r={r} trial {n}".encode()).digest(), 'little') % P

def run(cpath, r, outdir, max_trials=4):
    t = Target(cpath, r); D = 5 ** (6 + r); N1 = n3(D); N2 = n3(2 * D - 1); C = t.Cnorm
    ledger = {'r': r, 'D': D, 'N1': N1, 'N2': N2, 'C': C, 'phases': {}, 'memory_words': {}, 'trials': []}
    ph, mem = ledger['phases'], ledger['memory_words']
    t0 = time.time(); f = t.build_f(); t_build = time.time() - t0
    # charge: N1 evaluations (affine start 6 + 6 full rounds*27 + r partial*21 + 1 store) + IFFT_N1 + scaling
    # setup (Lemma 1 constants: two inversions, a handful of fifth powers, products and sums) charged as a flat 2,000
    ph['setup'] = 2000
    # build of f, charged once per trial (f is discarded after q is formed and rebuilt on a retry):
    # N1 evaluations + IFFT_N1 + N1 scaling + evaluation points omega^i by running product (1 mul + 1 store each)
    BUILD = JI(N1 * (6 + 27 * 6 + 21 * r + 1) + T(N1) + N1 + 2 * N1)
    ph['build_f_per_trial'] = BUILD
    mem['build_f'] = 2 * N1 + 8        # evaluation points, evaluation buffer (becomes f), state
    mem['form_q'] = 2 * D + 8          # f and q live together during the synthetic division
    X = t.pctx.gen()
    from powering import execute_frobenius     # fork A
    from gcd_stage import gcd_stage            # fork B
    result = None
    for n in range(max_trials):
        s0 = stream(r, n); x0, x1 = t.inputs(s0); y = t.H(x0, x1)
        assert int(f(t.ctx(s0))) == y
        q, rem = divmod(f - t.pctx([y]), X - t.pctx([s0])); assert rem == 0 and q.degree() == D - 1
        lead = int(q[D - 1]); q = q * t.pctx([pow(lead, P - 2, P)]); assert int(q[D - 1]) == 1
        trial = {'n': n, 's0': str(s0), 'inputs0': [str(x0), str(x1)], 'y': str(y)}
        # charges: build of f; stream draw (SHA-256 priced at 1,024 word operations); inputs: 3 fifth roots; y: one
        # permutation; synthetic division 4D; monic: inversion + 4D; forming h - X later: 4
        trial['ops_build'] = BUILD
        trial['ops_prepare'] = 1024 + 3 * ROOT5_COST + C + 4 * D + INV_COST + 4 * D + 4
        t1 = time.time(); h, led_pow = execute_frobenius(q, r, cache_qn1=False); trial['t_pow'] = time.time() - t1
        trial['ops_powering'] = JI(led_pow['ops']['total']); trial['mem_powering'] = led_pow['peak_words']['max']; trial['powering'] = led_pow
        t2 = time.time(); g, roots, led_gcd = gcd_stage(q, h - X, r); trial['t_gcd'] = time.time() - t2
        trial['ops_gcd'] = led_gcd['ops']; trial['mem_gcd'] = led_gcd['peak_words']; trial['gcd'] = {k: v for k, v in led_gcd.items() if k != 'trace'}
        trial['gcd_trace'] = led_gcd.get('trace')
        trial['deg_g'] = g.degree(); trial['roots'] = [str(int(x)) for x in roots]
        trial['ops_total'] = trial['ops_build'] + trial['ops_prepare'] + trial['ops_powering'] + trial['ops_gcd']
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
    a = sys.argv; mt = int(a[a.index('--max-trials') + 1]) if '--max-trials' in a else 4
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
the charge per radix-2 butterfly is 2 mul + 1 add + 1 sub + 1/2 loop = 4.5, the same total as
SPEC's (1 mul + 1 twiddle load + 1 add + 1 sub + 1/2 loop).

DEVIATION from SPEC (documented): the radix-3 stage is innermost and needs no twiddles, so a
radix-3 butterfly is one 3-point DFT = 1 mul + 7 add/sub + 1/2 loop = 8.5 (SPEC: 12.5 with two
twiddle multiplications and loads).  T(N) below is the closed form for THIS algorithm.

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
    """N = 3*2^k -> k."""
    assert N % 3 == 0 and N // 3 > 0 and (N // 3) & (N // 3 - 1) == 0, N
    return (N // 3).bit_length() - 1


def nice_length(n):
    """Smallest 3*2^k >= n."""
    N = 3
    while N < n:
        N *= 2
    return N


class Counter:
    CATS = ('mul', 'add', 'sub', 'load', 'store', 'loop')

    def __init__(self):
        self.c = {k: Fraction(0) for k in self.CATS}

    def add(self, **kw):
        for k, v in kw.items():
            self.c[k] += Fraction(v)

    def total(self):
        return sum(self.c.values())

    def snapshot(self):
        return dict(self.c)

    def __repr__(self):
        return 'Counter(total=%s, %s)' % (self.total(), {k: str(v) for k, v in self.c.items()})


# closed-form charges -----------------------------------------------------------------
R2_BUTTERFLY = Fraction(9, 2)      # 2 mul + 1 add + 1 sub + 1/2 loop
R3_BUTTERFLY = Fraction(17, 2)     # 1 mul + 3 add + 4 sub + 1/2 loop
MEM_R2_LEVEL = Fraction(2, 3)      # per element per radix-2 level (load+store, radix-8 passes)
MEM_R3_LEVEL = 2                   # per element


def T(N):
    """Charged operations of one forward or inverse transform of length N = 3*2^k."""
    k = log2_k(N)
    return Fraction(N, 2) * k * R2_BUTTERFLY + MEM_R2_LEVEL * N * k + Fraction(N, 3) * R3_BUTTERFLY + MEM_R3_LEVEL * N


def _r2_charge(ctr, nb, N):
    ctr.add(mul=2 * nb, add=nb, sub=nb, loop=Fraction(nb, 2), load=Fraction(N, 3), store=Fraction(N, 3))


def _r3_charge(ctr, nb, N):
    ctr.add(mul=nb, add=3 * nb, sub=4 * nb, loop=Fraction(nb, 2), load=N, store=N)


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
    w3i = pow(wN, N - N // 3, P)
    nb = 0
    for s in range(0, N, 3):
        a0, a1, a2 = a[s], a[s + 1], a[s + 2]
        t = (a1 + a2) % P
        d = (a1 - a2) % P
        m = (w3i * d) % P
        a[s] = (a0 + t) % P
        a[s + 1] = (a0 - a2 + m) % P
        a[s + 2] = (a0 - a1 - m) % P
        nb += 1
    _r3_charge(ctr, nb, N)
    length = 3
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
    for N in (3, 6, 12, 24, 48, 96, 192, 384, 768, 1536, 3072):
        a = [rng.randrange(P) for _ in range(N)]
        b = [rng.randrange(P) for _ in range(N)]
        c1, c2 = Counter(), Counter()
        A = ntt_forward(list(a), c1)
        B = ntt_forward(list(b), Counter())
        assert c1.total() == T(N), (N, c1.total(), T(N))
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

barrett_square (SPEC S1-S3) on buffers Q (D+1), R (N1: holds a / a2f / rem), A (N2),
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


### powering.py

```python
"""powering.py - exact charged ledger of X^p mod q (Frobenius) for the stated algorithm,
plus a thin python-flint executor (the value X^p mod q is algorithm-independent).

Algorithm (SPEC): k0 = floor(log2 D); acc = X^(2^k0) (degree < D, written directly);
then for each of the 254-k0 remaining bits of p (bits 253-k0 .. 0): acc <- acc^2 mod q by
barrett_square, and acc <- acc*X mod q when the bit is set.  Setup: Newton inverse of
rev(q) mod X^(D-1), cached transform INVQ (length N2) and optionally QN1 (length N1).

Live buffers during a squaring: Q (D+1), R (N1, a / a2f / rem), A (N2), INVQ (N2),
[QN1 (N1) if cached].  Newton: Q (D+1), F (N), G (N), g (m2).  Peak = max of both.
"""
from fractions import Fraction
import math
from ntt import P, T
from modsq import sizes, SQ, NEWTON, MULX, CACHE, newton_peak_words

CODE_BYTES = 1 << 20
WORD = 32


def C_of(r):
    return 216 + 21 * r


def bit_plan(D):
    """(k0, number of squarings, number of X-multiplies) for X^p mod q with deg q = D."""
    k0 = D.bit_length() - 1                      # 2^k0 <= D-1 < 2^(k0+1)  (so deg 2^k0 < D)
    if (1 << k0) >= D:
        k0 -= 1
    assert (1 << k0) < D
    top = P >> (254 - k0)
    assert top == 1 << k0, 'top k0+1 bits of p are 1 followed by zeros'
    rest = P & ((1 << (254 - k0)) - 1)
    return k0, 254 - k0, bin(rest).count('1')


def frobenius_ledger(D, r, cache_qn1=True):
    N1, N2 = sizes(D)
    k0, nsq, nmulx = bit_plan(D)
    C = C_of(r)
    newton = NEWTON(D)
    cache = CACHE(D - 1, N2) + (CACHE(D + 1, N1) if cache_qn1 else 0)
    init = D + Fraction(D, 2)                    # write acc = X^(2^k0): D stores + loop
    sq = SQ(D, cache_qn1)
    mulx = MULX(D)
    total = newton + cache + init + nsq * sq + nmulx * mulx
    live = {'Q': D + 1, 'R': N1, 'A': N2, 'INVQ': N2}
    if cache_qn1:
        live['QN1'] = N1
    pow_peak = sum(live.values())
    newton_peak = newton_peak_words(D)
    cache_build_peak = D + 1 + (D - 1) + N2 + (N1 if cache_qn1 else 0)   # inv + its padded buffer (+QN1)
    peak = max(pow_peak, newton_peak, cache_build_peak)
    mem_bytes = peak * WORD + CODE_BYTES
    t = math.log2(total / C)
    m = math.log2(mem_bytes)
    return {
        'D': D, 'r': r, 'C': C, 'N1': N1, 'N2': N2, 'k0': k0, 'cache_qn1': cache_qn1,
        'n_squarings': nsq, 'n_mulx': nmulx,
        'ops': {'newton': newton, 'cache_build': cache, 'init': init, 'squaring_each': sq,
                'squarings': nsq * sq, 'mulx_each': mulx, 'mulx_total': nmulx * mulx, 'total': total},
        'T_N1': T(N1), 'T_N2': T(N2),
        'live_words_squaring': live, 'peak_words': {'powering': pow_peak, 'newton': newton_peak,
                                                     'cache_build': cache_build_peak, 'max': peak},
        'memory_bytes': mem_bytes, 'time_log2': t, 'memory_log2': m,
        'score_contribution': t + max(0.0, m - 20),
    }


def execute_frobenius(q, r, cache_qn1=True):
    """q: python-flint fmpz_mod_poly (monic, degree D). Returns (X^p mod q, ledger)."""
    D = q.degree()
    x = q.context().gen() if hasattr(q, 'context') else None
    if x is None:
        from flint import fmpz_mod_poly_ctx, fmpz_mod_ctx
        x = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)).gen()
    res = x.pow_mod(P, q)
    return res, frobenius_ledger(D, r, cache_qn1)


def table():
    rows = []
    print('%-2s %-14s %18s %9s %12s %9s %9s %8s' % ('r', 'caches', 'ops', 'log2 t', 'peak words', 'log2 mem', 'score', 'nsq/nmx'))
    for r in (1, 2):
        D = 5 ** (6 + r) - 1
        for cache_qn1, name in ((True, 'INVQ+QN1'), (False, 'INVQ only')):
            L = frobenius_ledger(D, r, cache_qn1)
            print('%-2d %-14s %18.1f %9.4f %12d %9.4f %9.4f %4d/%-3d' % (
                r, name, L['ops']['total'], L['time_log2'], L['peak_words']['max'], L['memory_log2'],
                L['score_contribution'], L['n_squarings'], L['n_mulx']))
            rows.append(L)
    return rows


if __name__ == '__main__':
    for r in (1, 2):
        L = frobenius_ledger(5 ** (6 + r) - 1, r, False)
        print('r=%d D=%d N1=%d N2=%d k0=%d squarings=%d mulx=%d T(N1)=%s T(N2)=%s SQ=%s NEWTON=%s' % (
            r, L['D'], L['N1'], L['N2'], L['k0'], L['n_squarings'], L['n_mulx'], L['T_N1'], L['T_N2'],
            L['ops']['squaring_each'], L['ops']['newton']))
        print('   live words during a squaring:', L['live_words_squaring'], 'peaks:', L['peak_words'])
    table()
```


### halfgcd.py

```python
"""Counted half-gcd over F_p (python-flint arithmetic; every charge an exact Fraction).

Prices (orchard-field-ram-v2): field add/sub/mul, 256-bit load/store, compare/branch, shift/mask: 1 each.
Loop control: 1/2 per inner iteration (loops unrolled 8 per iteration, same convention as Fork A).
  T(N)   transform of length N = 3*2^k (ntt.py): N*(35k/12 + 29/6); only these lengths are used.
  transform product of lengths m1, m2, N = nice_length(m1+m2-1):
         3 T(N) + 5 N (pointwise: 2 loads, 2 muls with 1/N folded, 1 store) + 2 (m1+m2) (copy both inputs
         into padded buffers) + (N-m1) + (N-m2) (padding stores) + N/2 (loop control)
  classical product: 4 m1 m2 + m1 m2 / 2 + 2 (m1+m2-1); each product uses the cheaper rule.
  add/sub of length m: 4 m + m/2.   copy/shift/truncate of length m: 2 m + m/2.
  field inversion: 380 (x^(p-2): 254 squarings + 125 multiplications + 1).   monic: 380 + m + m/2.
  division of degree n by degree m, L = n-m+1: the cheaper of
         classical 380 + L (4 (m+1) + 2) + L (m+1)/2 + 2 (n+1) + (n+1)/2
         Newton    newton_inv(L) + product(L, L) + product(L, m+1) + 4 (m+1) + (m+1)/2 + 2 (n+1) + (n+1)/2
  newton_inv(L) = 380 + sum over doubling precisions m -> m2 = min(2m, L), N = nice_length(m2):
         (m2+N) + (m+N) + 5 T(N) + 10 N + 2 (m2-m) + (N-(m2-m)) + 3 (m2-m)      (modsq.NEWTON step)
Memory model: live coefficient words of every polynomial held by an active frame of the recursion plus
transform scratch (2 N words for a transform product, m1+m2-1 for a classical one, (n+1)+L (+2N) for a division).
"""
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx

from fractions import Fraction
from ntt import T, nice_length   # Fork A: T(N) = N*(35k/12 + 29/6), N = 3*2^k only

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
    """inverse series to precision L (modsq.NEWTON step formula, Fork A), plus the constant-term inversion."""
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

class Counter:
    """ops ledger + live-memory model: polynomials held by active frames + transform scratch."""
    def __init__(self):
        self.ops = Fraction(0); self.peak = 0; self.frames = []; self.hist = {}
        self.n_products = {'classical': 0, 'ntt': 0, 'zero': 0}; self.n_div = {'classical': 0, 'newton': 0}
    def charge(self, x, kind=None, key=None):
        self.ops += x
        if kind is not None:
            h = self.hist.setdefault(kind, {}); h[key] = h.get(key, 0) + 1
    def push(self): f = {}; self.frames.append(f); return f
    def pop(self): self.frames.pop()
    def live(self): return sum(p.length() for f in self.frames for p in f.values())
    def scratch(self, w):
        v = self.live() + w
        if v > self.peak: self.peak = v

class Arith:
    """python-flint arithmetic with charges."""
    def __init__(self, pctx, C):
        self.p = pctx; self.C = C; self.zero = pctx([0]); self.one = pctx([1])
    @staticmethod
    def L(a): return a.length()
    def mul(self, a, b):
        ops, kind, scratch = product_charge(self.L(a), self.L(b))
        self.C.charge(ops, 'product_' + kind, '%d,%d' % (self.L(a), self.L(b))); self.C.n_products[kind] += 1; self.C.scratch(scratch)
        return a * b
    def add(self, a, b): self.C.charge(Fraction(9 * max(self.L(a), self.L(b)), 2), 'addsub', str(max(self.L(a), self.L(b)))); self.C.scratch(max(self.L(a), self.L(b))); return a + b
    def sub(self, a, b): self.C.charge(Fraction(9 * max(self.L(a), self.L(b)), 2), 'addsub', str(max(self.L(a), self.L(b)))); self.C.scratch(max(self.L(a), self.L(b))); return a - b
    def shift_right(self, a, t):
        if t <= 0: return a
        self.C.charge(Fraction(5 * max(0, self.L(a) - t), 2), 'copy', str(max(0, self.L(a) - t))); self.C.scratch(max(0, self.L(a) - t)); return a.right_shift(t)
    def divmod(self, a, b):
        n, m = a.degree(), b.degree(); assert m >= 0
        if n < m: self.C.charge(Fraction(5 * self.L(a), 2), 'copy', str(self.L(a))); return self.zero, a
        ops, kind = division_charge(n, m)
        self.C.charge(ops, 'division_' + kind, '%d,%d' % (n, m)); self.C.n_div[kind] += 1
        self.C.scratch((n + 1) + (n - m + 1) + (2 * ntt_len(2 * (n - m + 1)) if kind == 'newton' else 0))
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

def mat_size(A, R): return sum(A.L(R[i][j]) for i in range(2) for j in range(2))

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

def q_apply(A, q, R):
    """Q*R with Q = [[0,1],[1,-q]]"""
    F = A.C.push()
    try:
        u = []
        for j in range(2):
            F['t'] = A.mul(q, R[1][j]); F['u%d' % j] = A.sub(R[0][j], F['t']); del F['t']; u.append(F['u%d' % j])
        return [[R[1][0], R[1][1]], [u[0], u[1]]]
    finally: A.C.pop()

CUTOFF = 128   # degree-drop k below which the classical base case runs
TOP_FRACTION = 4   # top level reduces the degree by n0/TOP_FRACTION per hgcd call (memory/ops trade)

def identity(A): return [[A.one, A.zero], [A.zero, A.one]]

def hold_matrix(F, name, R):
    for i in range(2):
        for j in range(2): F['%s%d%d' % (name, i, j)] = R[i][j]
def drop_matrix(F, name):
    for i in range(2):
        for j in range(2): F.pop('%s%d%d' % (name, i, j), None)

def euclid_matrix(A, r0, r1, k):
    F = A.C.push()
    try:
        n0 = r0.degree(); R = identity(A); F['r0'], F['r1'] = r0, r1
        while not F['r1'].is_zero() and n0 - F['r1'].degree() <= k:
            F['q'], F['rem'] = A.divmod(F['r0'], F['r1'])
            R = q_apply(A, F['q'], R); hold_matrix(F, 'R', R); del F['q']
            F['r0'], F['r1'] = F['r1'], F['rem']; del F['rem']
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
        F['r0s'] = A.shift_right(r0, t); F['r1s'] = A.shift_right(r1, t)
        R = hgcd(A, F['r0s'], F['r1s'], d); del F['r0s'], F['r1s']; hold_matrix(F, 'R', R)
        F['a'], F['b'] = mat_apply(A, R, r0, r1)
        if F['b'].is_zero() or k < n0 - F['b'].degree(): return R
        F['q'], F['c'] = A.divmod(F['a'], F['b']); del F['a']
        dstar = k - (n0 - F['b'].degree()); t2 = F['b'].degree() - 2 * dstar
        F['bs'] = A.shift_right(F['b'], t2); F['cs'] = A.shift_right(F['c'], t2)
        S = hgcd(A, F['bs'], F['cs'], dstar); del F['bs'], F['cs'], F['b'], F['c']; hold_matrix(F, 'S', S)
        QR = q_apply(A, F['q'], R); del F['q']; drop_matrix(F, 'R'); hold_matrix(F, 'QR', QR)
        return mat_mul(A, S, QR)
    finally: C.pop()

def fast_gcd(A, a, b):
    """monic gcd(a,b) with every operation charged; the top level only applies half-size matrices."""
    C = A.C; F = C.push()
    try:
        if a.degree() < b.degree(): a, b = b, a
        F['a'], F['b'] = a, b
        while not F['b'].is_zero() and F['b'].degree() > CUTOFF:
            n0 = F['a'].degree(); d = (n0 + TOP_FRACTION - 1) // TOP_FRACTION
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

def gcd_stage(q, hX, r, cutoff=None, top_fraction=None):
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
        'gcd_products': gp, 'gcd_divisions': gd,
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
  stream draw: 64 ops (SHA-256 of a short string, reduced mod p).
Deterministic: shifts c come from SHA256("poseidon_mage r=<r> edf <n>") mod p, n = 0,1,2,...
"""
import hashlib
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
        c = int.from_bytes(hashlib.sha256(f"poseidon_mage r={r} edf {n}".encode()).digest(), 'little') % P
        C.charge(64, 'edf_draw', ''); C.draws = getattr(C, 'draws', 0) + 1
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
    total = Fraction(0)
    for kind, table in hist.items():
        for key, cnt in table.items():
            k = [int(x) for x in key.split(',')] if key != '' else []
            if kind == 'product_classical': c = product_classical(*k)
            elif kind == 'product_ntt': c = product_ntt(*k)
            elif kind == 'product_zero': c = Fraction(0)
            elif kind == 'division_classical': c = division_classical(*k)
            elif kind == 'division_newton': c = division_newton(*k)
            elif kind == 'addsub': c = Fraction(9 * k[0], 2)
            elif kind == 'copy': c = Fraction(5 * k[0], 2)
            elif kind == 'monic': c = 380 + Fraction(3 * k[0], 2)
            elif kind == 'inversion': c = Fraction(380)
            elif kind == 'edf_draw': c = Fraction(64)
            elif kind == 'edf_powmod': c = Fraction(253 * mulmod(k[0]) + (POP - 1) * mulx(k[0]))
            elif kind == 'edf_constsub': c = Fraction(9 * k[0], 2)
            elif kind == 'root_linear': c = Fraction(1)
            else: raise ValueError(kind)
            total += c * cnt
    return total

if __name__ == '__main__':
    led = json.load(open(sys.argv[1]))
    tr = led['trace'] if 'trace' in led else json.load(open(sys.argv[2]))
    got = charge_from_trace(tr)
    print('recomputed', got, '| ledger ops', led['ops'], 'exact', led.get('ops_exact'))
    assert str(got) == led.get('ops_exact', str(led['ops'])), 'MISMATCH'
    print('SELF-CHECK OK; histogram JSON bytes:', len(json.dumps(tr, separators=(',', ':'))))
```


### accounting.py

```python
"""accounting.py - standard-library reproduction of every charged number (Appendix A driver).
Usage: python accounting.py <constants.json> <ledger_r<r>.json> [dir holding gcd_trace_r<r>_t<n>.json]
Recomputes: T(N), SQ, NEWTON, CACHE, MULX, the powering total, build/prepare/finish charges,
the half-gcd charge from the recorded trace, totals, log2 values, memory; then recomputes the
certified pair from the recorded root with a pure-Python permutation and checks the digest.
Requires ntt.py, modsq.py, powering.py, halfgcd_charge.py beside it (all standard library).
"""
import json, sys, math, hashlib, os
from ntt import T
from modsq import sizes, SQ, NEWTON, MULX, CACHE
from powering import frobenius_ledger, bit_plan
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
E5 = pow(5, -1, P - 1); EXP = lambda e: (e.bit_length() - 1) + (bin(e).count('1') - 1)
INV_COST, ROOT5_COST = EXP(P - 2), EXP(E5)
CODE_BYTES = 1 << 20

def main(cpath, lpath, trace_dir=None):
    C_ = json.load(open(cpath)); L = json.load(open(lpath)); r = L['r']; D = 5 ** (6 + r); C = 216 + 21 * r
    RC = [[int(x, 16) for x in row] for row in C_['round_constants']]; M = [[int(x, 16) for x in row] for row in C_['mds']]
    N1, N2 = sizes(D - 1); assert (N1, N2) == (L['N1'], L['N2']) and D == L['D'] and C == L['C']
    build = N1 * (6 + 27 * 6 + 21 * r + 1) + T(N1) + N1 + 2 * N1
    assert build == L['phases']['build_f_per_trial'] and L['phases']['setup'] == 2000
    total = L['phases']['setup']; ok = True
    for tr in L['trials']:
        prep = 1024 + 3 * ROOT5_COST + C + 4 * D + INV_COST + 4 * D + 4
        pw = frobenius_ledger(D - 1, r, cache_qn1=tr['powering']['cache_qn1'])   # modulus q has degree D-1
        assert prep == tr['ops_prepare'] and pw['ops']['total'] == tr['ops_powering']
        if trace_dir:
            from halfgcd_charge import charge_from_trace
            g = charge_from_trace(json.load(open(os.path.join(trace_dir, f"gcd_trace_r{r}_t{tr['n']}.json"))))
            gi = int(g) if g.denominator == 1 else int(g) + 1
            assert gi == tr['ops_gcd'], (gi, tr['ops_gcd'])
            print(f"  gcd+roots charge recomputed from the trace histogram: {gi:,}")
        fin = tr.get('ops_finish', 0)
        if fin: assert fin == len(tr['roots']) * (3 * ROOT5_COST + C + 8) + C
        assert tr['ops_build'] == build
        total += build + prep + tr['ops_powering'] + tr['ops_gcd'] + fin
    assert total == L['total_ops'], (total, L['total_ops'])
    t = math.log2(total / C); m = math.log2(L['peak_words'] * 32 + CODE_BYTES)
    print(f"r={r} D={D} N1={N1} N2={N2} C={C}\ntotal ops {total:,}  time_log2 {t:.6f}  memory_log2 {m:.6f}  score {t + max(0, m - 20):.6f}")
    assert abs(t - L['time_log2']) < 1e-9 and abs(m - L['memory_log2_bytes']) < 1e-9
    # recompute the pair from the recorded parameters (pure Python)
    k = 2; CAP = 1 << 65; inv = lambda x: pow(x, P - 2, P); K5 = pow((CAP + RC[0][2]) % P, 5, P)
    i, j = [t_ for t_ in range(3) if t_ != k]; lam5 = 1; mu5 = (-M[k][0] * inv(M[k][1])) % P
    a, b, e = M[i][0], M[i][1], (-(M[i][2] * K5 + RC[1][i])) % P; c, d, f = M[j][0], M[j][1], (-(M[j][2] * K5 + RC[1][j])) % P
    det = (a * d - b * c) % P; di = inv(det); A0 = ((e * d - b * f) * di) % P; B0 = ((a * f - e * c) * di) % P
    def inputs(Tp):
        T_ = pow(Tp, E5, P); A = (lam5 * T_ + A0) % P; B = (mu5 * T_ + B0) % P
        return (pow(A, E5, P) - RC[0][0]) % P, (pow(B, E5, P) - RC[0][1]) % P
    def H(x0, x1):
        s = [x0, x1, CAP]
        for idx in (*range(4), *range(4, 4 + r), *range(60, 64)):
            s = [(x + cc) % P for x, cc in zip(s, RC[idx])]
            for col in (range(3) if idx < 4 or idx >= 60 else range(1)): s[col] = pow(s[col], 5, P)
            s = [sum(cc * x for cc, x in zip(row, s)) % P for row in M]
        return s[0]
    tr = L['trials'][-1]; n = tr['n']
    s0 = int.from_bytes(hashlib.sha256(f"poseidon_mage r={r} trial {n}".encode()).digest(), 'little') % P
    assert str(s0) == tr['s0']; x0, x1 = inputs(s0); assert [str(x0), str(x1)] == tr['inputs0']
    y = H(x0, x1); assert y.to_bytes(32, 'little').hex() == L['digest']
    for pr in L['pairs']:
        u0, u1 = inputs(int(pr['s1'])); assert [str(u0), str(u1)] == pr['inputs'] and (u0, u1) != (x0, x1) and H(u0, u1) == y
    print(f"pair(s) recomputed from the stream and the recorded root(s): {len(L['pairs'])} collision(s) on digest {L['digest']}")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
```


## Appendix B. Ledger and gcd trace histograms

`ledger_r2.json` (every phase count, sizes, flags, the stream indices, the root(s) and the pair):

```json
{
 "r": 2,
 "D": 390625,
 "N1": 393216,
 "N2": 786432,
 "C": 258,
 "phases": {
  "setup": 2000,
  "build_f_per_trial": 105545728
 },
 "memory_words": {
  "build_f": 786440,
  "form_q": 781258
 },
 "trials": [
  {
   "n": 0,
   "s0": "1645442543066552363305467509155580542641350305816557600709588043221114589506",
   "inputs0": [
    "16872136246087636640354229570373321372567965137229268522506958597440009196881",
    "12510585749214607508676342910471497470800819987414806439103674953329825618083"
   ],
   "y": "26506168113144590967069148303588876912957776399195228637355906821721161064917",
   "ops_build": 105545728,
   "ops_prepare": 3127747,
   "t_pow": 698.3161978721619,
   "ops_powering": 62837488594.5,
   "mem_powering": 2356705,
   "powering": {
    "D": 390624,
    "r": 2,
    "C": 258,
    "N1": 393216,
    "N2": 786432,
    "k0": 18,
    "cache_qn1": false,
    "n_squarings": 236,
    "n_mulx": 46,
    "ops": {
     "newton": 330975267.5,
     "cache_build": 46659039,
     "init": 585936,
     "squaring_each": 264163016,
     "squarings": 62342471776,
     "mulx_each": 2539056,
     "mulx_total": 116796576,
     "total": 62837488594.5
    },
    "T_N1": 21397504,
    "T_N2": 45088768,
    "live_words_squaring": {
     "Q": 390625,
     "R": 393216,
     "A": 786432,
     "INVQ": 786432
    },
    "peak_words": {
     "powering": 2356705,
     "newton": 1567680,
     "cache_build": 1567680,
     "max": 2356705
    },
    "memory_bytes": 76463136,
    "time_log2": 27.859679215510504,
    "memory_log2": 26.18826103517757,
    "score_contribution": 34.04794025068807
   },
   "t_gcd": 113.97486734390259,
   "ops_gcd": 14794877264,
   "mem_gcd": 3525986,
   "gcd": {
    "ops": 14794877264,
    "ops_exact": "14794877264",
    "peak_words": 3525986,
    "gcd_degree": 0,
    "roots": [],
    "cutoff": 128,
    "top_fraction": 4,
    "gcd_ops": "14794877264",
    "roots_ops": "0",
    "roots_draws": 0,
    "gcd_products": {
     "classical": 776554,
     "ntt": 52620,
     "zero": 4404
    },
    "gcd_divisions": {
     "classical": 390624,
     "newton": 0
    },
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
   },
   "deg_g": 0,
   "roots": [],
   "ops_total": 77741039333.5
  },
  {
   "n": 1,
   "s0": "19858568290029182989619581245386926527056154783152235610047967884939993348964",
   "inputs0": [
    "19170364111830859773083013351512814444160198338467249464482623945863688372965",
    "99770591724421408910603398875641040529735467254480369891993273439890098266"
   ],
   "y": "2814908808032590176576552034482168640531468369681951504224781134974910999517",
   "ops_build": 105545728,
   "ops_prepare": 3127747,
   "t_pow": 730.2430076599121,
   "ops_powering": 62837488594.5,
   "mem_powering": 2356705,
   "powering": {
    "D": 390624,
    "r": 2,
    "C": 258,
    "N1": 393216,
    "N2": 786432,
    "k0": 18,
    "cache_qn1": false,
    "n_squarings": 236,
    "n_mulx": 46,
    "ops": {
     "newton": 330975267.5,
     "cache_build": 46659039,
     "init": 585936,
     "squaring_each": 264163016,
     "squarings": 62342471776,
     "mulx_each": 2539056,
     "mulx_total": 116796576,
     "total": 62837488594.5
    },
    "T_N1": 21397504,
    "T_N2": 45088768,
    "live_words_squaring": {
     "Q": 390625,
     "R": 393216,
     "A": 786432,
     "INVQ": 786432
    },
    "peak_words": {
     "powering": 2356705,
     "newton": 1567680,
     "cache_build": 1567680,
     "max": 2356705
    },
    "memory_bytes": 76463136,
    "time_log2": 27.859679215510504,
    "memory_log2": 26.18826103517757,
    "score_contribution": 34.04794025068807
   },
   "t_gcd": 123.77531838417053,
   "ops_gcd": 14794877264,
   "mem_gcd": 3525986,
   "gcd": {
    "ops": 14794877264,
    "ops_exact": "14794877264",
    "peak_words": 3525986,
    "gcd_degree": 0,
    "roots": [],
    "cutoff": 128,
    "top_fraction": 4,
    "gcd_ops": "14794877264",
    "roots_ops": "0",
    "roots_draws": 0,
    "gcd_products": {
     "classical": 776554,
     "ntt": 52620,
     "zero": 4404
    },
    "gcd_divisions": {
     "classical": 390624,
     "newton": 0
    },
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
   },
   "deg_g": 0,
   "roots": [],
   "ops_total": 77741039333.5
  },
  {
   "n": 2,
   "s0": "15866665379159260546923309459469152280151687642143003549780074267389020655379",
   "inputs0": [
    "11259176566695619471650127415825827204375385307095419279867428605303555850230",
    "5722744797669390771556825047507704519116726094737562517963762333369111235096"
   ],
   "y": "23405747945322376284075677486108475670983785174935383197097397291508588976795",
   "ops_build": 105545728,
   "ops_prepare": 3127747,
   "t_pow": 779.5452492237091,
   "ops_powering": 62837488594.5,
   "mem_powering": 2356705,
   "powering": {
    "D": 390624,
    "r": 2,
    "C": 258,
    "N1": 393216,
    "N2": 786432,
    "k0": 18,
    "cache_qn1": false,
    "n_squarings": 236,
    "n_mulx": 46,
    "ops": {
     "newton": 330975267.5,
     "cache_build": 46659039,
     "init": 585936,
     "squaring_each": 264163016,
     "squarings": 62342471776,
     "mulx_each": 2539056,
     "mulx_total": 116796576,
     "total": 62837488594.5
    },
    "T_N1": 21397504,
    "T_N2": 45088768,
    "live_words_squaring": {
     "Q": 390625,
     "R": 393216,
     "A": 786432,
     "INVQ": 786432
    },
    "peak_words": {
     "powering": 2356705,
     "newton": 1567680,
     "cache_build": 1567680,
     "max": 2356705
    },
    "memory_bytes": 76463136,
    "time_log2": 27.859679215510504,
    "memory_log2": 26.18826103517757,
    "score_contribution": 34.04794025068807
   },
   "t_gcd": 133.77261424064636,
   "ops_gcd": 14794895072,
   "mem_gcd": 3525986,
   "gcd": {
    "ops": 14794895072,
    "ops_exact": "14794895072",
    "peak_words": 3525986,
    "gcd_degree": 2,
    "roots": [
     "240509988820890884781024290074016771339081740195921957296790927727582285292",
     "23403637005312374678700485156766769702849536820972648798669567025877564282322"
    ],
    "cutoff": 128,
    "top_fraction": 4,
    "gcd_ops": "29589752919/2",
    "roots_ops": "37225/2",
    "roots_draws": 2,
    "gcd_products": {
     "classical": 776554,
     "ntt": 52620,
     "zero": 4404
    },
    "gcd_divisions": {
     "classical": 390622,
     "newton": 0
    },
    "roots_divisions": {
     "classical": 3,
     "newton": 0
    },
    "roots_products": {
     "classical": 0,
     "ntt": 0,
     "zero": 0
    },
    "roots_monic": 2,
    "roots_powmod": 2
   },
   "deg_g": 2,
   "roots": [
    "240509988820890884781024290074016771339081740195921957296790927727582285292",
    "23403637005312374678700485156766769702849536820972648798669567025877564282322"
   ],
   "ops_total": 77741060193.5,
   "ops_finish": 3052
  }
 ],
 "total_ops": 233223140860.5,
 "time_log2": 29.75169273102862,
 "peak_words": 3525986,
 "memory_bytes": 113880128,
 "memory_log2_bytes": 26.76294077886584,
 "score": 36.51463350989446,
 "digest": "9b9abd1e25f451b4d11f80cbc0dba9df81c7728f0ac05ba367a1fc66122fbf33",
 "pairs": [
  {
   "s1": "240509988820890884781024290074016771339081740195921957296790927727582285292",
   "inputs": [
    "20834728090844308818668958997876562173174154111480156638069073277386948771601",
    "4992524740912056664423768020451142185380896709641787766677619446001666102205"
   ]
  },
  {
   "s1": "23403637005312374678700485156766769702849536820972648798669567025877564282322",
   "inputs": [
    "18678053155263738658756578753738966522118087358018010533490951024109537491905",
    "20976781307306742908346874810655927376647915278682990214294645476252815015018"
   ]
  }
 ],
 "t_build": 4.464470624923706
}
```

`gcd_trace_r2_t0.json` (trial 0: histogram of every charged half-gcd and root operation by kind and size; `halfgcd_charge.py` recomputes the stage charge from it):

```json
{"copy":{"97657":1,"97656":1,"48829":2,"48828":2,"24415":3,"24414":3,"12209":3,"12208":3,"6105":8,"6104":8,"3053":19,"3052":19,"1527":40,"1526":40,"765":40,"764":40,"383":130,"382":130,"193":137,"192":137,"189":345,"188":345,"381":170,"380":170,"191":351,"190":351,"761":85,"760":85,"379":171,"378":171,"187":216,"186":216,"1525":43,"1524":43,"763":86,"762":86,"3051":21,"3050":21,"1523":43,"1522":43,"759":45,"758":45,"377":45,"376":45,"6103":11,"6102":11,"3049":22,"3048":22,"12205":6,"12204":6,"6101":11,"6100":11,"24413":3,"24412":3,"12207":5,"12206":5,"48827":1,"48826":1,"24411":2,"24410":2,"12203":2,"12202":2,"6099":2,"6098":2,"3047":2,"3046":2,"1521":2,"1520":2,"97655":1,"97654":1,"48825":1,"48824":1,"73243":1,"73242":1,"36623":1,"36622":1,"18313":1,"18312":1,"9157":4,"9156":4,"4579":9,"4578":9,"2291":9,"2290":9,"1147":9,"1146":9,"575":9,"574":9,"289":15,"288":15,"145":191,"144":191,"143":352,"142":352,"285":170,"284":170,"141":346,"140":346,"571":86,"570":86,"287":176,"286":176,"283":162,"282":162,"139":164,"138":164,"1143":42,"1142":42,"573":85,"572":85,"569":76,"568":76,"2287":22,"2286":22,"1145":43,"1144":43,"1141":34,"1140":34,"4577":11,"4576":11,"2289":21,"2288":21,"9155":5,"9154":5,"4575":10,"4574":10,"2285":12,"2284":12,"18309":2,"18308":2,"9153":5,"9152":5,"36619":2,"36618":2,"18311":3,"18310":3,"18307":2,"18306":2,"9151":2,"9150":2,"4573":2,"4572":2,"73241":1,"73240":1,"36621":1,"36620":1,"54933":1,"54932":1,"27467":1,"27466":1,"13735":1,"13734":1,"6869":1,"6868":1,"3435":7,"3434":7,"1719":7,"1718":7,"861":7,"860":7,"431":50,"430":50,"217":54,"216":54,"213":172,"212":172,"429":86,"428":86,"215":177,"214":177,"857":43,"856":43,"427":85,"426":85,"211":121,"210":121,"1715":21,"1714":21,"859":42,"858":42,"855":36,"854":36,"425":36,"424":36,"3433":10,"3432":10,"1717":21,"1716":21,"6865":5,"6864":5,"3431":11,"3430":11,"1713":15,"1712":15,"13731":3,"13730":3,"6867":6,"6866":6,"6863":4,"6862":4,"3429":4,"3428":4,"27465":2,"27464":2,"13733":3,"13732":3,"54929":1,"54928":1,"27463":1,"27462":1,"13729":1,"13728":1,"41199":1,"41198":1,"20601":1,"20600":1,"10301":2,"10300":2,"5151":5,"5150":5,"2577":5,"2576":5,"1289":16,"1288":16,"645":37,"644":37,"323":82,"322":82,"163":85,"162":85,"159":173,"158":173,"321":85,"320":85,"161":176,"160":176,"643":43,"642":43,"319":85,"318":85,"157":92,"156":92,"1287":21,"1286":21,"641":42,"640":42,"2573":10,"2572":10,"1285":21,"1284":21,"5149":5,"5148":5,"2575":11,"2574":11,"10299":3,"10298":3,"5147":6,"5146":6,"2571":6,"2570":6,"1283":6,"1282":6,"639":6,"638":6,"317":6,"316":6,"20597":2,"20596":2,"10297":3,"10296":3,"41197":1,"41196":1,"20599":1,"20598":1,"30901":1,"30900":1,"15451":1,"15450":1,"7727":1,"7726":1,"3865":1,"3864":1,"1933":7,"1932":7,"967":17,"966":17,"485":17,"484":17,"243":62,"242":62,"241":87,"240":87,"481":43,"480":43,"239":86,"238":86,"965":22,"964":22,"483":43,"482":43,"1931":10,"1930":10,"963":21,"962":21,"479":25,"478":25,"237":25,"236":25,"3861":5,"3860":5,"1929":11,"1928":11,"7723":3,"7722":3,"3863":6,"3862":6,"3859":4,"3858":4,"1927":4,"1926":4,"961":4,"960":4,"15449":2,"15448":2,"7725":3,"7724":3,"30897":1,"30896":1,"15447":1,"15446":1,"7721":1,"7720":1,"23175":1,"23174":1,"11589":1,"11588":1,"5795":2,"5794":2,"2899":2,"2898":2,"1451":2,"1450":2,"727":2,"726":2,"365":3,"364":3,"183":48,"182":48,"181":87,"180":87,"361":43,"360":43,"179":87,"178":87,"723":21,"722":21,"363":44,"362":44,"359":40,"358":40,"177":40,"176":40,"1447":11,"1446":11,"725":22,"724":22,"721":19,"720":19,"2895":5,"2894":5,"1449":11,"1448":11,"1445":8,"1444":8,"5793":3,"5792":3,"2897":6,"2896":6,"11585":2,"11584":2,"5791":3,"5790":3,"2893":3,"2892":3,"23173":1,"23172":1,"11587":1,"11586":1,"17381":1,"17380":1,"8691":2,"8690":2,"4347":2,"4346":2,"2175":2,"2174":2,"1089":2,"1088":2,"545":12,"544":12,"273":36,"272":36,"137":79,"136":79,"135":89,"134":89,"271":42,"270":42,"133":85,"132":85,"543":22,"542":22,"269":43,"268":43,"1085":11,"1084":11,"541":21,"540":21,"2171":5,"2170":5,"1087":10,"1086":10,"1083":9,"1082":9,"539":9,"538":9,"267":9,"266":9,"131":20,"130":20,"4343":3,"4342":3,"2173":5,"2172":5,"2169":4,"2168":4,"8689":1,"8688":1,"4345":2,"4344":2,"17379":1,"17378":1,"8687":1,"8686":1,"4341":1,"4340":1,"13037":1,"13036":1,"6519":1,"6518":1,"3261":1,"3260":1,"1631":4,"1630":4,"817":4,"816":4,"409":15,"408":15,"205":37,"204":37,"203":44,"202":44,"407":21,"406":21,"201":42,"200":42,"813":10,"812":10,"405":21,"404":21,"1629":5,"1628":5,"815":11,"814":11,"3257":3,"3256":3,"1627":6,"1626":6,"811":7,"810":7,"403":7,"402":7,"199":7,"198":7,"6517":2,"6516":2,"3259":3,"3258":3,"13033":1,"13032":1,"6515":1,"6514":1,"3255":1,"3254":1,"1625":1,"1624":1,"9777":1,"9776":1,"4889":2,"4888":2,"2445":3,"2444":3,"1223":6,"1222":6,"613":6,"612":6,"307":17,"306":17,"155":17,"154":17,"151":44,"150":44,"305":22,"304":22,"153":44,"152":44,"609":11,"608":11,"303":21,"302":21,"149":26,"148":26,"1221":5,"1220":5,"611":10,"610":10,"2443":3,"2442":3,"1219":5,"1218":5,"607":5,"606":5,"301":5,"300":5,"4887":1,"4886":1,"2441":2,"2440":2,"9775":1,"9774":1,"4885":1,"4884":1,"7333":1,"7332":1,"3667":1,"3666":1,"1835":1,"1834":1,"919":1,"918":1,"461":1,"460":1,"231":12,"230":12,"229":22,"228":22,"457":11,"456":11,"227":22,"226":22,"915":5,"914":5,"459":11,"458":11,"455":9,"454":9,"225":9,"224":9,"1831":3,"1830":3,"917":6,"916":6,"913":4,"912":4,"3665":2,"3664":2,"1833":3,"1832":3,"7329":1,"7328":1,"3663":1,"3662":1,"1829":1,"1828":1,"5499":1,"5498":1,"2751":1,"2750":1,"1377":1,"1376":1,"689":4,"688":4,"345":9,"344":9,"173":20,"172":20,"171":22,"170":22,"343":11,"342":11,"169":21,"168":21,"687":5,"686":5,"341":10,"340":10,"1373":2,"1372":2,"685":5,"684":5,"2747":2,"2746":2,"1375":3,"1374":3,"1371":2,"1370":2,"683":2,"682":2,"339":2,"338":2,"167":2,"166":2,"5497":1,"5496":1,"2749":1,"2748":1,"4125":1,"4124":1,"2063":2,"2062":2,"1033":2,"1032":2,"517":4,"516":4,"259":10,"258":10,"127":10,"126":10,"257":10,"256":10,"515":6,"514":6,"255":11,"254":11,"1029":3,"1028":3,"513":5,"512":5,"2061":1,"2060":1,"1031":2,"1030":2,"4123":1,"4122":1,"2059":1,"2058":1,"1027":1,"1026":1,"511":1,"510":1,"253":1,"252":1,"3093":1,"3092":1,"1547":2,"1546":2,"775":2,"774":2,"389":2,"388":2,"195":7,"194":7,"385":5,"384":5,"771":3,"770":3,"387":5,"386":5,"1545":1,"1544":1,"773":2,"772":2,"3091":1,"3090":1,"1543":1,"1542":1,"769":1,"768":1,"2321":1,"2320":1,"1161":1,"1160":1,"581":3,"580":3,"291":5,"290":5,"147":5,"146":5,"579":2,"578":2,"1159":2,"1158":2,"577":3,"576":3,"2317":1,"2316":1,"1157":1,"1156":1,"1741":1,"1740":1,"871":1,"870":1,"437":1,"436":1,"219":4,"218":4,"433":3,"432":3,"869":2,"868":2,"435":3,"434":3,"1737":1,"1736":1,"867":1,"866":1,"1305":1,"1304":1,"653":2,"652":2,"327":3,"326":3,"165":3,"164":3,"325":3,"324":3,"651":1,"650":1,"1303":1,"1302":1,"649":1,"648":1,"979":1,"978":1,"491":1,"490":1,"247":1,"246":1,"487":2,"486":2,"245":3,"244":3,"977":1,"976":1,"489":1,"488":1,"735":1,"734":1,"369":1,"368":1,"185":2,"184":2,"731":1,"730":1,"367":1,"366":1,"551":1,"550":1,"277":1,"276":1,"549":1,"548":1,"275":1,"274":1,"413":1,"412":1,"207":2,"206":2,"411":1,"410":1,"311":1,"310":1,"233":1,"232":1,"175":1,"174":1,"129":1,"128":1},"division_classical":{"192,191":1157,"191,190":1157,"190,189":1508,"189,188":1508,"188,187":1853,"187,186":1853,"186,185":2069,"185,184":2069,"184,183":2071,"183,182":2071,"182,181":2119,"181,180":2119,"180,179":2206,"179,178":2206,"178,177":2293,"177,176":2293,"176,175":2333,"175,174":2333,"174,173":2334,"173,172":2334,"172,171":2354,"171,170":2354,"170,169":2376,"169,168":2376,"168,167":2397,"167,166":2397,"166,165":2399,"165,164":2399,"164,163":2402,"163,162":2402,"162,161":2487,"161,160":2487,"160,159":2663,"159,158":2663,"158,157":2836,"157,156":2836,"156,155":2928,"155,154":2928,"154,153":2945,"153,152":2945,"152,151":2989,"151,150":2989,"150,149":3033,"149,148":3033,"148,147":3059,"147,146":3059,"146,145":3064,"145,144":3064,"144,143":3255,"143,142":3255,"142,141":3607,"141,140":3607,"140,139":3953,"139,138":3953,"138,137":4117,"137,136":4117,"136,135":4196,"135,134":4196,"134,133":4285,"133,132":4285,"132,131":4370,"131,130":4370,"130,129":4390,"129,128":4390,"128,127":4381,"127,126":4370,"126,125":4379,"125,124":4379,"124,123":4379,"123,122":4378,"122,121":4375,"121,120":4313,"120,119":4226,"119,118":4140,"118,117":4115,"117,116":4115,"116,115":4114,"115,114":4102,"114,113":4080,"113,112":4058,"112,111":4049,"111,110":4049,"110,109":4049,"109,108":4045,"108,107":3991,"107,106":3814,"106,105":3642,"105,104":3521,"104,103":3521,"103,102":3519,"102,101":3482,"101,100":3438,"100,99":3396,"99,98":3389,"98,97":3389,"97,96":3382,"286,285":131,"96,95":3245,"95,94":2894,"573,572":40,"285,284":171,"1144,1143":40,"570,569":85,"283,282":172,"94,93":2549,"2289,2288":19,"571,570":86,"1143,1142":43,"4578,4577":8,"2287,2286":21,"1141,1140":43,"568,567":45,"282,281":46,"9156,9155":3,"4576,4575":11,"2286,2285":22,"18310,18309":3,"9153,9152":6,"4575,4574":11,"36621,36620":2,"9154,9153":5,"18309,18308":3,"73242,73241":1,"36619,36618":1,"18307,18306":2,"9151,9150":2,"4573,4572":2,"2284,2283":2,"1140,1139":2,"341796,341795":1,"73240,73239":1,"36618,36617":1,"292968,292967":1,"93,92":2333,"92,91":2331,"91,90":2283,"90,89":2196,"89,88":2109,"88,87":2069,"87,86":2068,"86,85":2048,"85,84":2026,"84,83":2005,"83,82":2003,"82,81":2000,"81,80":1915,"80,79":1739,"79,78":1566,"78,77":1474,"77,76":1457,"76,75":1413,"75,74":1369,"74,73":1343,"73,72":1338,"216,215":426,"72,71":1147,"430,429":9,"213,212":758,"71,70":795,"859,858":9,"214,213":764,"427,426":86,"211,210":922,"70,69":449,"1717,1716":9,"429,428":85,"856,855":42,"426,425":76,"3433,3432":9,"858,857":43,"1714,1713":22,"855,854":34,"6867,6866":4,"1716,1715":21,"3432,3431":11,"13734,13733":1,"6865,6864":5,"3430,3429":10,"1713,1712":12,"27466,27465":1,"13731,13730":2,"6864,6863":5,"54931,54930":1,"13732,13731":3,"27463,27462":2,"13729,13728":2,"6862,6861":2,"3429,3428":2,"256346,256345":1,"27465,27464":1,"54930,54929":1,"219725,219724":1,"215,214":411,"212,211":760,"210,209":881,"209,208":881,"208,207":881,"207,206":882,"206,205":883,"205,204":884,"204,203":956,"203,202":920,"202,201":1006,"201,200":1007,"200,199":1006,"199,198":1015,"198,197":1013,"197,196":1013,"196,195":1013,"195,194":1013,"194,193":1020,"193,192":1030,"322,321":51,"645,644":7,"321,320":87,"1288,1287":7,"642,641":43,"319,318":86,"2575,2574":7,"643,642":42,"1285,1284":21,"640,639":36,"318,317":37,"5151,5150":1,"1287,1286":21,"2574,2573":10,"10300,10299":1,"5148,5147":5,"2572,2571":11,"1284,1283":15,"20599,20598":1,"5149,5148":6,"10297,10296":3,"5146,5145":4,"2571,2570":4,"41199,41198":1,"10299,10298":3,"20598,20597":2,"192258,192257":1,"41196,41195":1,"20596,20595":1,"10296,10295":1,"164793,164792":1,"241,240":171,"483,482":37,"240,239":261,"966,965":16,"481,480":43,"238,237":347,"1932,1931":5,"964,963":21,"480,479":42,"3862,3861":5,"1929,1928":10,"963,962":21,"7725,7724":2,"1930,1929":11,"3861,3860":5,"15450,15449":1,"7723,7722":3,"3859,3858":6,"1927,1926":6,"961,960":6,"478,477":6,"237,236":268,"30898,30897":1,"15447,15446":2,"7722,7721":3,"144193,144192":1,"15448,15447":1,"30897,30896":1,"123594,123593":1,"242,241":89,"239,238":176,"236,235":287,"235,234":287,"234,233":287,"233,232":287,"232,231":289,"231,230":288,"230,229":300,"229,228":317,"228,227":344,"227,226":322,"226,225":365,"225,224":349,"224,223":353,"223,222":353,"222,221":353,"221,220":353,"220,219":353,"219,218":353,"218,217":357,"217,216":362,"363,362":18,"724,723":17,"360,359":44,"1449,1448":7,"361,360":44,"723,722":22,"2898,2897":1,"1447,1446":10,"721,720":21,"358,357":26,"5794,5793":1,"2895,2894":5,"1446,1445":11,"11587,11586":1,"2896,2895":6,"5791,5790":3,"2893,2892":4,"1444,1443":4,"720,719":4,"23175,23174":1,"5793,5792":3,"11586,11585":2,"108143,108142":1,"23172,23171":1,"11584,11583":1,"5790,5789":1,"92694,92693":1,"273,272":4,"544,543":2,"270,269":44,"1087,1086":2,"271,270":45,"541,540":21,"268,267":41,"2173,2172":2,"543,542":22,"1084,1083":11,"540,539":19,"4345,4344":2,"1086,1085":11,"2170,2169":5,"1083,1082":8,"8691,8690":1,"2172,2171":6,"4344,4343":3,"17380,17379":1,"8688,8687":2,"4342,4341":3,"2169,2168":3,"81106,81105":1,"8689,8688":1,"17379,17378":1,"69519,69518":1,"69,68":285,"68,67":206,"408,407":12,"67,66":117,"816,815":2,"406,405":22,"1630,1629":2,"813,812":11,"405,404":21,"3259,3258":2,"814,813":10,"1627,1626":5,"811,810":9,"403,402":9,"66,65":32,"6517,6516":2,"1629,1628":5,"3256,3255":3,"1626,1625":4,"13035,13034":1,"3258,3257":2,"6516,6515":1,"60828,60827":1,"13033,13032":1,"6514,6513":1,"3255,3254":1,"52138,52137":1,"306,305":16,"612,611":4,"304,303":22,"1222,1221":4,"609,608":10,"303,302":22,"2445,2444":1,"610,609":11,"1221,1220":5,"4888,4887":1,"2442,2441":3,"1219,1218":6,"607,606":7,"301,300":8,"9777,9776":1,"2443,2442":3,"4887,4886":2,"45619,45618":1,"9774,9773":1,"4885,4884":1,"2440,2439":1,"1218,1217":1,"39102,39101":1,"459,458":6,"916,915":6,"456,455":11,"1833,1832":3,"457,456":10,"915,914":5,"3666,3665":2,"1831,1830":3,"913,912":5,"454,453":5,"7332,7331":1,"3664,3663":1,"1830,1829":2,"34213,34212":1,"7330,7329":1,"3663,3662":1,"29325,29324":1,"345,344":2,"688,687":1,"342,341":12,"1375,1374":1,"343,342":12,"685,684":5,"340,339":10,"2749,2748":1,"687,686":6,"1372,1371":3,"684,683":4,"5499,5498":1,"1374,1373":3,"2748,2747":2,"25658,25657":1,"5496,5495":1,"2746,2745":1,"1371,1370":1,"21993,21992":1,"258,257":10,"516,515":4,"256,255":22,"1032,1031":1,"514,513":5,"255,254":21,"2062,2061":1,"1029,1028":2,"513,512":5,"4123,4122":1,"1030,1029":3,"2059,2058":2,"1027,1026":2,"511,510":2,"253,252":24,"19243,19242":1,"2061,2060":1,"4122,4121":1,"16494,16493":1,"65,64":12,"64,63":11,"387,386":5,"254,253":22,"252,251":23,"251,250":23,"250,249":23,"249,248":23,"248,247":23,"247,246":23,"246,245":24,"245,244":24,"244,243":30,"243,242":30,"774,773":2,"385,384":7,"1546,1545":2,"771,770":3,"384,383":6,"3093,3092":1,"772,771":2,"1545,1544":1,"14431,14430":1,"3091,3090":1,"1543,1542":1,"769,768":1,"382,381":2,"12369,12368":1,"291,290":3,"580,579":2,"288,287":6,"1159,1158":2,"289,288":6,"577,576":3,"2319,2318":1,"579,578":2,"1158,1157":1,"10822,10821":1,"2317,2316":1,"1156,1155":1,"576,575":1,"9276,9275":1,"435,434":3,"870,869":1,"433,432":2,"1740,1739":1,"868,867":2,"432,431":3,"8115,8114":1,"1737,1736":1,"867,866":1,"6956,6955":1,"327,326":2,"652,651":1,"324,323":4,"1305,1304":1,"325,324":4,"651,650":2,"6085,6084":1,"1302,1301":1,"649,648":1,"5216,5215":1,"489,488":2,"978,977":1,"487,486":1,"4563,4562":1,"976,975":1,"486,485":1,"3911,3910":1,"367,366":2,"733,732":1,"364,363":3,"3421,3420":1,"366,365":2,"732,731":1,"2932,2931":1,"276,275":2,"550,549":1,"2564,2563":1,"274,273":2,"547,546":1,"2198,2197":1,"412,411":1,"1922,1921":1,"411,410":1,"1647,1646":1,"309,308":2,"1440,1439":1,"307,306":2,"1234,1233":1,"1078,1077":1,"924,923":1,"807,806":1,"692,691":1,"604,603":1,"518,517":1,"452,451":1,"386,385":1,"383,382":1,"381,380":1,"380,379":1,"379,378":1,"378,377":1,"377,376":1,"376,375":1,"375,374":1,"374,373":1,"373,372":1,"372,371":1,"371,370":1,"370,369":1,"369,368":1,"368,367":1,"365,364":1,"362,361":1,"359,358":1,"357,356":1,"356,355":1,"355,354":1,"354,353":1,"353,352":1,"352,351":1,"351,350":1,"350,349":1,"349,348":1,"348,347":1,"347,346":1,"346,345":1,"344,343":1,"341,340":1,"339,338":1,"338,337":1,"337,336":1,"336,335":1,"335,334":1,"334,333":1,"333,332":1,"332,331":1,"331,330":1,"330,329":1,"329,328":1,"328,327":1,"326,325":1,"323,322":1,"320,319":1,"317,316":1,"316,315":1,"315,314":1,"314,313":1,"313,312":1,"312,311":1,"311,310":1,"310,309":1,"308,307":1,"305,304":1,"302,301":1,"300,299":1,"299,298":1,"298,297":1,"297,296":1,"296,295":1,"295,294":1,"294,293":1,"293,292":1,"292,291":1,"290,289":1,"287,286":1,"284,283":1,"281,280":1,"280,279":1,"279,278":1,"278,277":1,"277,276":1,"275,274":1,"272,271":1,"269,268":1,"267,266":1,"266,265":1,"265,264":1,"264,263":1,"263,262":1,"262,261":1,"261,260":1,"260,259":1,"259,258":1,"257,256":1,"63,62":1,"62,61":1,"61,60":1,"60,59":1,"59,58":1,"58,57":1,"57,56":1,"56,55":1,"55,54":1,"54,53":1,"53,52":1,"52,51":1,"51,50":1,"50,49":1,"49,48":1,"48,47":1,"47,46":1,"46,45":1,"45,44":1,"44,43":1,"43,42":1,"42,41":1,"41,40":1,"40,39":1,"39,38":1,"38,37":1,"37,36":1,"36,35":1,"35,34":1,"34,33":1,"33,32":1,"32,31":1,"31,30":1,"30,29":1,"29,28":1,"28,27":1,"27,26":1,"26,25":1,"25,24":1,"24,23":1,"23,22":1,"22,21":1,"21,20":1,"20,19":1,"19,18":1,"18,17":1,"17,16":1,"16,15":1,"15,14":1,"14,13":1,"13,12":1,"12,11":1,"11,10":1,"10,9":1,"9,8":1,"8,7":1,"7,6":1,"6,5":1,"5,4":1,"4,3":1,"3,2":1,"2,1":1,"1,0":1},"product_zero":{"2,0":4404},"addsub":{"1":4404,"2":8808,"3":8808,"4":8808,"5":8808,"6":8808,"7":8808,"8":8808,"9":8808,"10":8808,"11":8808,"12":8808,"13":8808,"14":8808,"15":8808,"16":8808,"17":8808,"18":8808,"19":8808,"20":8808,"21":8808,"22":8808,"23":8808,"24":8808,"25":8808,"26":8808,"27":8808,"28":8808,"29":8808,"30":8808,"31":8808,"32":8808,"33":8808,"34":8808,"35":8808,"36":8808,"37":8808,"38":8808,"39":8808,"40":8808,"41":8807,"42":8806,"43":8806,"44":8806,"45":8806,"46":8806,"47":8806,"48":8806,"49":8806,"50":8806,"51":8806,"52":8806,"53":8806,"54":8806,"55":8805,"56":8804,"57":8804,"58":8804,"59":8804,"60":8804,"61":8804,"62":8804,"63":8804,"64":8794,"65":8783,"66":8773,"67":8668,"68":8535,"69":8445,"70":8152,"71":7564,"72":7196,"73":6843,"74":6319,"75":6097,"76":6027,"77":5982,"78":5933,"79":5782,"80":5506,"81":5326,"82":5144,"83":4889,"84":4799,"85":4773,"86":4742,"87":4720,"88":4688,"89":4627,"90":4499,"91":4408,"92":4320,"93":4189,"94":3924,"95":3406,"96":3051,"97":2653,"477":130,"478":130,"98":2174,"190":641,"191":565,"192":401,"954":40,"955":40,"474":170,"475":170,"189":557,"193":144,"381":299,"382":271,"383":184,"1907":40,"1908":40,"949":85,"950":85,"472":171,"473":171,"188":261,"379":197,"380":323,"384":45,"762":179,"763":157,"764":110,"3814":19,"3815":19,"952":86,"953":86,"1904":43,"1905":43,"761":131,"765":46,"1525":88,"1526":72,"1527":57,"7629":8,"7630":8,"3812":21,"3813":21,"1902":43,"1903":43,"947":45,"948":45,"469":45,"470":45,"187":45,"378":66,"760":58,"1524":72,"1528":25,"3051":41,"3052":38,"3053":27,"15259":3,"15260":3,"7627":11,"7628":11,"3809":22,"3810":22,"1523":31,"3050":37,"3054":11,"6103":19,"6104":17,"6105":12,"30517":3,"30518":3,"15254":6,"15255":6,"7624":11,"7625":11,"3049":17,"6101":10,"6102":19,"6106":3,"12206":11,"12207":10,"12208":7,"61034":2,"61035":2,"15257":5,"15258":5,"30514":3,"30515":3,"12205":7,"12209":3,"24413":5,"24414":5,"24415":4,"122069":1,"122070":1,"61032":1,"61033":1,"30512":2,"30513":2,"15252":2,"15253":2,"7622":2,"7623":2,"3807":2,"3808":2,"1899":2,"1900":2,"759":13,"1522":7,"3048":2,"6100":2,"12204":2,"24412":3,"24416":2,"48827":3,"48828":3,"48829":2,"439451":1,"439452":1,"122067":1,"122068":1,"61029":1,"61030":1,"24411":1,"48826":1,"48830":1,"97655":1,"97656":2,"97657":1,"488279":1,"488280":1,"359":35,"360":75,"143":613,"144":458,"145":208,"717":9,"718":9,"354":170,"355":170,"141":494,"142":678,"146":22,"286":299,"287":225,"288":111,"1432":9,"1433":9,"357":176,"358":176,"712":86,"713":86,"352":162,"353":162,"140":163,"284":238,"285":333,"289":19,"572":160,"573":127,"574":62,"2862":9,"2863":9,"714":85,"715":85,"1427":42,"1428":42,"709":76,"710":76,"283":76,"570":121,"571":161,"575":10,"1144":81,"1145":68,"1146":39,"5722":9,"5723":9,"1429":43,"1430":43,"2857":22,"2858":22,"1424":34,"1425":34,"569":45,"1142":51,"1143":82,"1147":10,"2288":44,"2289":39,"2290":28,"11444":4,"11445":4,"2859":21,"2860":21,"5719":11,"5720":11,"2287":36,"2291":9,"4577":20,"4578":18,"4579":14,"22889":1,"22890":1,"11442":5,"11443":5,"5717":10,"5718":10,"2854":12,"2855":12,"1141":12,"2286":14,"4576":17,"4580":6,"9155":9,"9156":8,"9157":5,"45777":1,"45778":1,"22884":2,"22885":2,"11439":5,"11440":5,"4575":9,"9153":6,"9154":9,"9158":1,"18310":5,"18311":4,"18312":3,"91552":1,"91553":1,"22887":3,"22888":3,"45772":2,"45773":2,"22882":2,"22883":2,"11437":2,"11438":2,"5714":2,"5715":2,"2285":3,"4574":2,"9152":2,"18308":2,"18309":5,"18313":1,"36620":3,"36621":3,"36622":2,"329587":1,"329588":1,"45774":1,"45775":1,"91549":1,"91550":1,"36619":1,"36623":1,"73241":1,"73242":2,"73243":1,"366208":1,"366209":1,"99":2031,"100":2017,"101":1968,"102":1910,"103":1865,"104":1800,"105":1762,"106":1639,"107":1382,"108":1204,"109":990,"537":50,"538":50,"110":765,"214":307,"215":268,"216":187,"1074":7,"1075":7,"534":86,"535":86,"213":292,"217":59,"429":158,"430":122,"431":56,"2147":7,"2148":7,"1069":43,"1070":43,"532":85,"533":85,"212":157,"427":126,"428":175,"432":8,"858":79,"859":64,"860":39,"4292":7,"4293":7,"1072":42,"1073":42,"2142":21,"2143":21,"1067":36,"1068":36,"529":36,"530":36,"211":36,"426":36,"856":51,"857":83,"861":7,"1716":38,"1717":36,"1718":26,"8584":1,"8585":1,"2144":21,"2145":21,"4289":10,"4290":10,"1715":38,"1719":8,"3433":21,"3434":16,"3435":9,"17167":1,"17168":1,"8579":5,"8580":5,"4287":11,"4288":11,"2139":15,"2140":15,"855":20,"1714":21,"3431":13,"3432":22,"3436":1,"6866":10,"6867":8,"6868":5,"34332":1,"34333":1,"8582":6,"8583":6,"17162":3,"17163":3,"8577":4,"8578":4,"4284":4,"4285":4,"1713":6,"3430":4,"6864":5,"6865":10,"6869":2,"13732":6,"13733":5,"13734":3,"68664":1,"68665":1,"17164":3,"17165":3,"34329":2,"34330":2,"13731":4,"13735":1,"27465":2,"27466":2,"27467":2,"247189":1,"247190":1,"68659":1,"68660":1,"34327":1,"34328":1,"17159":1,"17160":1,"6863":1,"13730":1,"27463":1,"27464":2,"27468":1,"54930":1,"54931":2,"54932":1,"274654":1,"274655":1,"402":82,"403":82,"160":337,"161":300,"162":219,"804":37,"805":37,"399":85,"400":85,"159":261,"163":90,"321":165,"322":154,"323":112,"1609":16,"1610":16,"802":43,"803":43,"397":85,"398":85,"158":97,"320":133,"324":40,"643":85,"644":73,"645":52,"3219":5,"3220":5,"1607":21,"1608":21,"799":42,"800":42,"319":54,"642":75,"646":17,"1287":39,"1288":34,"1289":23,"6437":5,"6438":5,"3214":10,"3215":10,"1604":21,"1605":21,"641":33,"1285":25,"1286":37,"1290":7,"2574":22,"2575":19,"2576":13,"12874":2,"12875":2,"3217":11,"3218":11,"6434":5,"6435":5,"2573":18,"2577":7,"5149":11,"5150":9,"5151":6,"25749":1,"25750":1,"12872":3,"12873":3,"6432":6,"6433":6,"3212":6,"3213":6,"1602":6,"1603":6,"797":6,"798":6,"394":6,"395":6,"157":7,"318":6,"640":11,"1284":9,"2572":7,"5148":9,"5152":3,"10299":5,"10300":4,"10301":3,"51497":1,"51498":1,"25744":2,"25745":2,"12869":3,"12870":3,"5147":3,"10297":2,"10298":5,"10302":1,"20598":3,"20599":3,"20600":2,"185390":1,"185391":1,"25747":1,"25748":1,"51494":1,"51495":1,"20597":1,"20601":1,"41197":1,"41198":2,"41199":1,"205989":1,"205990":1,"111":708,"112":704,"113":695,"114":664,"115":640,"116":618,"117":586,"118":573,"119":547,"120":436,"121":331,"122":242,"604":17,"605":17,"123":112,"241":150,"242":126,"243":82,"1207":17,"1208":17,"599":43,"600":43,"239":93,"240":154,"244":22,"482":88,"483":77,"484":51,"2414":7,"2415":7,"602":43,"603":43,"1204":22,"1205":22,"481":68,"485":19,"965":40,"966":33,"967":25,"4829":1,"4830":1,"2412":10,"2413":10,"1202":21,"1203":21,"597":25,"598":25,"238":25,"480":34,"964":38,"968":9,"1931":19,"1932":17,"1933":10,"9657":1,"9658":1,"4824":5,"4825":5,"2409":11,"2410":11,"963":22,"1929":14,"1930":21,"1934":1,"3862":11,"3863":9,"3864":6,"19312":1,"19313":1,"4827":6,"4828":6,"9652":3,"9653":3,"4822":4,"4823":4,"2407":4,"2408":4,"1199":4,"1200":4,"479":9,"962":7,"1928":5,"3860":5,"3861":10,"3865":2,"7724":6,"7725":5,"7726":3,"38624":1,"38625":1,"9654":3,"9655":3,"19309":2,"19310":2,"7723":4,"7727":1,"15449":2,"15450":2,"15451":2,"139042":1,"139043":1,"38619":1,"38620":1,"19307":1,"19308":1,"9649":1,"9650":1,"3859":1,"7722":1,"15447":1,"15448":2,"15452":1,"30898":1,"30899":2,"30900":1,"154491":1,"154492":1,"454":3,"455":7,"181":153,"182":113,"183":51,"907":2,"908":2,"449":43,"450":43,"179":123,"180":170,"184":6,"362":80,"363":61,"364":27,"1812":2,"1813":2,"452":44,"453":44,"902":21,"903":21,"447":40,"448":40,"178":40,"361":83,"365":4,"724":41,"725":32,"726":15,"3622":2,"3623":2,"904":22,"905":22,"1807":11,"1808":11,"899":19,"900":19,"722":29,"723":43,"727":2,"1448":21,"1449":17,"1450":11,"7242":2,"7243":2,"1809":11,"1810":11,"3617":5,"3618":5,"1804":8,"1805":8,"721":8,"1446":11,"1447":21,"1451":2,"2896":11,"2897":9,"2898":6,"14484":1,"14485":1,"3619":6,"3620":6,"7239":3,"7240":3,"2895":10,"2899":3,"5793":5,"5794":4,"5795":3,"28967":1,"28968":1,"14479":2,"14480":2,"7237":3,"7238":3,"3614":3,"3615":3,"1445":4,"2894":4,"5791":2,"5792":5,"5796":1,"11586":3,"11587":3,"11588":2,"104279":1,"104280":1,"14482":1,"14483":1,"28964":1,"28965":1,"11585":1,"11589":1,"23173":1,"23174":2,"23175":1,"115866":1,"115867":1,"339":36,"340":38,"135":163,"136":145,"137":103,"679":12,"680":12,"337":42,"338":42,"134":137,"138":38,"271":77,"272":66,"273":45,"1359":2,"1360":2,"677":22,"678":22,"334":43,"335":43,"133":61,"270":73,"274":15,"543":40,"544":29,"545":15,"2717":2,"2718":2,"1354":11,"1355":11,"674":21,"675":21,"269":40,"541":29,"542":44,"546":2,"1086":18,"1087":16,"1088":10,"5432":2,"5433":2,"1357":10,"1358":10,"2712":5,"2713":5,"1352":9,"1353":9,"672":9,"673":9,"332":9,"333":9,"132":9,"268":10,"540":12,"1084":15,"1085":21,"1089":2,"2172":9,"2173":8,"2174":7,"10862":2,"10863":2,"2714":5,"2715":5,"5427":3,"5428":3,"2709":4,"2710":4,"1083":5,"2170":6,"2171":9,"2175":3,"4344":5,"4345":5,"4346":4,"21724":1,"21725":1,"5429":2,"5430":2,"10859":1,"10860":1,"4343":3,"4347":2,"8689":3,"8690":3,"8691":2,"78207":1,"78208":1,"21722":1,"21723":1,"10857":1,"10858":1,"5424":1,"5425":1,"2169":2,"4342":1,"8688":1,"8692":1,"17379":1,"17380":2,"17381":1,"86897":1,"86898":1,"509":15,"510":15,"203":78,"204":69,"205":50,"1019":4,"1020":4,"507":21,"508":21,"202":70,"206":18,"407":40,"408":34,"409":19,"2037":4,"2038":4,"1014":10,"1015":10,"504":21,"505":21,"201":35,"405":27,"406":38,"410":4,"814":22,"815":19,"816":12,"4074":1,"4075":1,"1017":11,"1018":11,"2034":5,"2035":5,"813":19,"817":4,"1629":11,"1630":9,"1631":5,"8147":1,"8148":1,"4069":3,"4070":3,"2032":6,"2033":6,"1012":7,"1013":7,"502":7,"503":7,"200":8,"404":10,"812":9,"1627":6,"1628":11,"1632":1,"3258":6,"3259":5,"3260":3,"16294":1,"16295":1,"4072":3,"4073":3,"8144":2,"8145":2,"3257":4,"3261":1,"6517":2,"6518":3,"6519":3,"58654":1,"58655":1,"16289":1,"16290":1,"8142":1,"8143":1,"4067":1,"4068":1,"2029":1,"2030":1,"811":1,"1626":1,"3256":1,"6515":1,"6516":2,"6520":1,"13034":1,"13035":2,"13036":1,"65171":1,"65172":1,"152":82,"153":72,"154":50,"151":69,"155":18,"305":37,"306":32,"307":22,"377":21,"150":31,"303":21,"304":37,"308":7,"610":22,"611":19,"612":15,"3055":3,"609":16,"613":7,"1221":11,"1222":11,"1223":8,"6109":2,"6110":2,"757":5,"758":5,"374":5,"375":5,"149":5,"302":5,"608":7,"1220":8,"1224":3,"2443":5,"2444":5,"2445":4,"12219":1,"12220":1,"6107":1,"6108":1,"1219":3,"2442":3,"2446":2,"4887":4,"4888":4,"4889":2,"43988":1,"43989":1,"12217":1,"12218":1,"2441":1,"4886":1,"4890":1,"9775":1,"9776":2,"9777":1,"48876":1,"48877":1,"229":38,"230":29,"231":15,"1148":1,"227":29,"228":42,"232":2,"458":20,"459":16,"460":9,"2292":1,"2293":1,"567":9,"568":9,"226":9,"456":13,"457":21,"461":1,"916":10,"917":9,"918":6,"4582":1,"4583":1,"1139":4,"1140":4,"914":5,"915":10,"919":1,"1832":6,"1833":5,"1834":3,"9164":1,"9165":1,"1831":4,"1835":1,"3665":2,"3666":2,"3667":2,"32989":1,"32990":1,"9159":1,"9160":1,"2284":1,"913":2,"1830":1,"3663":2,"3664":3,"3668":1,"7330":1,"7331":2,"7332":1,"36654":1,"36655":1,"171":41,"172":37,"173":27,"170":33,"174":10,"343":20,"344":18,"345":13,"1720":1,"424":10,"425":10,"169":14,"342":18,"346":4,"687":10,"688":9,"689":5,"3437":1,"3438":1,"854":5,"341":9,"685":7,"686":9,"690":1,"1374":5,"1375":4,"1376":3,"6872":1,"6873":1,"1712":2,"852":2,"853":2,"422":2,"423":2,"168":2,"684":3,"1372":2,"1373":5,"1377":1,"2748":3,"2749":3,"2750":2,"24740":1,"24741":1,"6870":1,"2747":2,"2751":1,"5497":1,"5498":2,"5499":1,"27489":1,"27490":1,"128":41,"129":37,"130":28,"124":49,"125":45,"126":44,"127":43,"131":11,"257":21,"258":18,"259":12,"256":17,"260":4,"515":10,"516":8,"517":6,"2578":2,"639":5,"255":7,"513":6,"514":10,"518":2,"1030":5,"1031":5,"1032":4,"5154":1,"5155":1,"1029":3,"1033":2,"2061":3,"2062":3,"2063":2,"18554":1,"18555":1,"5153":1,"1282":1,"1283":1,"637":1,"638":1,"254":1,"512":2,"1028":1,"2060":1,"2064":1,"4123":1,"4124":2,"4125":1,"20616":1,"20617":1,"194":15,"195":9,"196":2,"386":9,"387":9,"388":7,"385":9,"389":2,"772":5,"773":5,"774":4,"771":3,"775":2,"1545":3,"1546":3,"1547":2,"13913":1,"13914":1,"1927":1,"959":1,"960":1,"770":1,"1544":1,"1548":1,"3091":1,"3092":2,"3093":1,"15459":1,"15460":1,"147":5,"290":9,"291":7,"292":3,"579":6,"580":5,"581":4,"2900":1,"719":3,"720":3,"578":4,"582":2,"1159":2,"1160":2,"1161":2,"10434":1,"10435":1,"1444":1,"577":1,"1157":1,"1158":2,"1162":1,"2318":1,"2319":2,"2320":1,"11593":1,"11594":1,"218":8,"219":5,"539":3,"220":1,"434":6,"435":5,"436":3,"433":4,"437":1,"869":2,"870":2,"871":2,"7824":1,"7825":1,"1082":1,"867":1,"868":2,"872":1,"1738":1,"1739":2,"1740":1,"8693":1,"8694":1,"164":7,"165":3,"325":5,"326":5,"327":4,"328":2,"651":3,"652":3,"653":2,"5866":1,"5867":1,"809":1,"810":1,"650":1,"654":1,"1303":1,"1304":2,"1305":1,"245":4,"246":3,"607":2,"247":1,"488":3,"489":3,"490":2,"4398":1,"4399":1,"487":1,"491":1,"977":1,"978":2,"979":1,"185":3,"186":1,"366":2,"367":2,"368":2,"3297":1,"3298":1,"912":1,"369":1,"732":1,"733":2,"734":1,"139":3,"275":3,"276":2,"2471":1,"2472":1,"277":1,"549":1,"550":2,"551":1,"2746":1,"207":2,"1851":1,"1852":1,"208":1,"411":1,"412":2,"413":1,"2057":1,"2058":1,"156":2,"1387":1,"1388":1,"309":2,"310":1,"1541":1,"1542":1,"1038":1,"1039":1,"1153":1,"1154":1,"777":1,"778":1,"863":1,"864":1,"647":1,"199":1},"product_classical":{"2,1":8808,"2,2":8808,"2,3":8808,"2,4":8808,"2,5":8808,"2,6":8808,"2,7":8808,"2,8":8808,"2,9":8808,"2,10":8808,"2,11":8808,"2,12":8808,"2,13":8808,"2,14":8808,"2,15":8808,"2,16":8808,"2,17":8808,"2,18":8808,"2,19":8808,"2,20":8808,"2,21":8808,"2,22":8808,"2,23":8808,"2,24":8808,"2,25":8808,"2,26":8808,"2,27":8808,"2,28":8808,"2,29":8808,"2,30":8808,"2,31":8808,"2,32":8808,"2,33":8808,"2,34":8808,"2,35":8808,"2,36":8808,"2,37":8808,"2,38":8808,"2,39":8808,"2,40":8807,"2,41":8806,"2,42":8806,"2,43":8806,"2,44":8806,"2,45":8806,"2,46":8806,"2,47":8806,"2,48":8806,"2,49":8806,"2,50":8806,"2,51":8806,"2,52":8806,"2,53":8806,"2,54":8805,"2,55":8804,"2,56":8804,"2,57":8804,"2,58":8804,"2,59":8804,"2,60":8804,"2,61":8804,"2,62":8804,"2,63":8794,"2,64":8783,"2,65":8773,"2,66":8668,"2,67":8535,"2,68":8445,"2,69":8152,"2,70":7564,"2,71":7196,"2,72":6843,"2,73":6319,"2,74":6097,"2,75":6027,"2,76":5982,"2,77":5933,"2,78":5782,"2,79":5506,"2,80":5326,"2,81":5144,"2,82":4889,"2,83":4799,"2,84":4773,"2,85":4742,"2,86":4720,"2,87":4688,"2,88":4627,"2,89":4499,"2,90":4408,"2,91":4320,"2,92":4189,"2,93":3924,"2,94":3406,"2,95":3051,"2,96":2653,"2,97":2174,"2,191":256,"2,192":127,"2,190":130,"2,382":126,"2,383":40,"2,381":88,"2,763":64,"2,764":40,"2,1526":32,"2,1527":19,"2,762":24,"2,3052":16,"2,3053":8,"2,1525":13,"2,3051":8,"2,6104":8,"2,6105":3,"2,6103":5,"2,12207":4,"2,12208":3,"2,380":2,"2,24414":2,"2,24415":2,"2,12206":1,"2,48828":1,"2,48829":1,"2,144":183,"2,145":17,"2,143":247,"2,287":94,"2,288":9,"2,142":76,"2,286":119,"2,573":52,"2,574":9,"2,285":34,"2,572":55,"2,1145":30,"2,1146":9,"2,1144":23,"2,2289":16,"2,2290":9,"2,571":12,"2,4578":8,"2,4579":4,"2,2288":7,"2,4577":4,"2,9156":4,"2,9157":1,"2,1143":2,"2,9155":3,"2,18311":2,"2,18312":1,"2,18310":1,"2,36621":1,"2,36622":1,"2,98":2031,"2,99":2017,"2,100":1968,"2,101":1910,"2,102":1865,"2,103":1800,"2,104":1762,"2,105":1639,"2,106":1382,"2,107":1204,"2,108":990,"2,109":765,"2,215":128,"2,216":49,"2,214":79,"2,430":49,"2,431":7,"2,429":57,"2,859":28,"2,860":7,"2,858":25,"2,1717":16,"2,1718":7,"2,428":15,"2,1716":9,"2,3434":7,"2,3435":1,"2,857":4,"2,3433":7,"2,6867":4,"2,6868":1,"2,6866":3,"2,13733":2,"2,13734":1,"2,3432":1,"2,13732":1,"2,27466":1,"2,27467":1,"2,161":128,"2,162":81,"2,322":64,"2,323":37,"2,160":48,"2,644":32,"2,645":16,"2,321":27,"2,643":16,"2,1288":16,"2,1289":5,"2,1287":11,"2,2575":8,"2,2576":5,"2,5150":4,"2,5151":2,"2,2574":3,"2,5149":2,"2,10300":2,"2,10301":1,"2,10299":1,"2,20599":1,"2,20600":1,"2,110":708,"2,111":704,"2,112":695,"2,113":664,"2,114":640,"2,115":618,"2,116":586,"2,117":573,"2,118":547,"2,119":436,"2,120":331,"2,121":242,"2,122":112,"2,242":60,"2,243":17,"2,241":47,"2,483":32,"2,484":17,"2,966":16,"2,967":7,"2,482":15,"2,965":9,"2,1932":7,"2,1933":1,"2,240":4,"2,1931":7,"2,3863":4,"2,3864":1,"2,3862":3,"2,7725":2,"2,7726":1,"2,1930":1,"2,7724":1,"2,15450":1,"2,15451":1,"2,182":45,"2,183":3,"2,181":62,"2,363":24,"2,364":2,"2,180":19,"2,362":30,"2,725":13,"2,726":2,"2,361":8,"2,724":14,"2,1449":8,"2,1450":2,"2,1448":6,"2,2897":4,"2,2898":2,"2,723":3,"2,2896":2,"2,5794":2,"2,5795":1,"2,5793":1,"2,11587":1,"2,11588":1,"2,136":64,"2,137":35,"2,272":32,"2,273":12,"2,135":30,"2,271":20,"2,544":12,"2,545":2,"2,543":14,"2,1087":7,"2,1088":2,"2,542":4,"2,1086":6,"2,2173":4,"2,2174":2,"2,2172":2,"2,4345":2,"2,4346":2,"2,1085":1,"2,8690":1,"2,8691":1,"2,204":32,"2,205":15,"2,203":17,"2,408":15,"2,409":4,"2,407":12,"2,815":8,"2,816":4,"2,814":4,"2,1630":4,"2,1631":1,"2,1629":3,"2,3259":2,"2,3260":1,"2,406":1,"2,3258":1,"2,6518":1,"2,6519":1,"2,153":32,"2,154":16,"2,152":16,"2,306":16,"2,307":6,"2,305":10,"2,611":8,"2,612":6,"2,1222":4,"2,1223":3,"2,610":2,"2,2444":2,"2,2445":2,"2,1221":1,"2,4888":1,"2,4889":1,"2,230":12,"2,231":1,"2,229":15,"2,459":7,"2,460":1,"2,228":4,"2,458":7,"2,917":4,"2,918":1,"2,916":3,"2,1833":2,"2,1834":1,"2,457":1,"2,1832":1,"2,3666":1,"2,3667":1,"2,172":16,"2,173":9,"2,344":8,"2,345":4,"2,171":7,"2,343":4,"2,688":4,"2,689":1,"2,687":3,"2,1375":2,"2,1376":1,"2,1374":1,"2,2749":1,"2,2750":1,"2,123":49,"2,124":45,"2,125":44,"2,126":43,"2,127":31,"2,128":16,"2,129":16,"2,130":10,"2,258":8,"2,259":4,"2,257":4,"2,516":4,"2,517":2,"2,515":2,"2,1031":2,"2,1032":2,"2,2062":1,"2,2063":1,"2,194":7,"2,195":2,"2,193":6,"2,387":4,"2,388":2,"2,386":2,"2,773":2,"2,774":2,"2,1546":1,"2,1547":1,"2,146":5,"2,290":4,"2,291":3,"2,580":2,"2,581":1,"2,289":1,"2,579":1,"2,1160":1,"2,1161":1,"2,218":4,"2,219":1,"2,217":3,"2,435":2,"2,436":1,"2,434":1,"2,870":1,"2,871":1,"2,163":4,"2,164":3,"2,326":2,"2,327":2,"2,652":1,"2,653":1,"2,245":2,"2,246":1,"2,244":1,"2,489":1,"2,490":1,"2,184":2,"2,185":1,"2,367":1,"2,368":1,"2,138":2,"2,139":1,"2,275":1,"2,276":1,"2,206":1,"2,207":1,"2,155":1,"2,156":1,"39,161":1,"40,160":1,"40,161":1,"41,160":1},"product_ntt":{"95,383":130,"96,382":130,"96,383":130,"97,382":130,"93,96":687,"94,97":611,"93,97":301,"94,98":135,"94,96":691,"95,97":317,"95,98":147,"190,765":40,"191,764":40,"191,765":40,"192,764":40,"94,381":170,"95,380":170,"95,381":170,"96,380":170,"93,95":431,"94,95":215,"95,96":175,"189,191":341,"190,192":252,"189,192":342,"190,193":130,"190,191":125,"191,192":41,"191,193":47,"381,1527":40,"382,1526":40,"382,1527":40,"383,1526":40,"189,761":85,"190,760":85,"190,761":85,"191,760":85,"94,379":171,"95,378":171,"95,379":171,"96,378":171,"92,95":216,"92,96":171,"188,190":130,"188,191":261,"189,190":85,"379,382":171,"380,383":166,"379,383":83,"380,384":40,"380,382":171,"381,383":83,"381,384":40,"762,3053":19,"763,3052":19,"763,3053":19,"764,3052":19,"190,763":86,"191,762":86,"191,763":86,"192,762":86,"188,192":131,"189,193":86,"380,1525":43,"381,1524":43,"381,1525":43,"382,1524":43,"379,381":90,"380,381":45,"381,382":43,"761,763":86,"762,764":81,"761,764":85,"762,765":40,"762,763":41,"763,764":19,"763,765":19,"1525,6105":8,"1526,6104":8,"1526,6105":8,"1527,6104":8,"762,3051":21,"763,3050":21,"763,3051":21,"764,3050":21,"380,1523":43,"381,1522":43,"381,1523":43,"382,1522":43,"189,759":45,"190,758":45,"190,759":45,"191,758":45,"93,377":45,"94,376":45,"94,377":45,"95,376":45,"92,94":46,"93,94":45,"187,190":45,"187,191":45,"378,381":45,"378,382":43,"760,763":47,"760,764":23,"761,765":21,"1524,1526":43,"1525,1527":38,"1524,1527":43,"1525,1528":19,"1525,1526":19,"1526,1527":8,"1526,1528":8,"3051,12209":3,"3052,12208":3,"3052,12209":3,"3053,12208":3,"1525,6103":11,"1526,6102":11,"1526,6103":11,"1527,6102":11,"761,3049":22,"762,3048":22,"762,3049":22,"763,3048":22,"760,762":24,"761,762":22,"1523,1526":26,"1523,1527":13,"1524,1528":11,"3050,3052":22,"3051,3053":17,"3050,3053":21,"3051,3054":8,"3051,3052":9,"3052,3053":3,"3052,3054":3,"6103,24415":3,"6104,24414":3,"6104,24415":3,"6105,24414":3,"3050,12205":6,"3051,12204":6,"3051,12205":6,"3052,12204":6,"1524,6101":11,"1525,6100":11,"1525,6101":11,"1526,6100":11,"1523,1525":13,"1524,1525":11,"3049,3051":8,"3049,3052":15,"3050,3051":6,"6101,6104":10,"6102,6105":11,"6101,6105":5,"6102,6106":3,"6102,6104":11,"6103,6105":6,"6103,6106":3,"12206,48829":2,"12207,48828":2,"12207,48829":2,"12208,48828":2,"3051,12207":5,"3052,12206":5,"3052,12207":5,"3053,12206":5,"3049,3053":7,"3050,3054":5,"6102,24413":3,"6103,24412":3,"6103,24413":3,"6104,24412":3,"6101,6103":5,"6102,6103":3,"6103,6104":3,"12205,12207":5,"12206,12208":6,"12205,12208":5,"12206,12209":3,"12206,12207":3,"12207,12208":2,"12207,12209":2,"24413,97657":1,"24414,97656":1,"24414,97657":1,"24415,97656":1,"12206,48827":1,"12207,48826":1,"12207,48827":1,"12208,48826":1,"6102,24411":2,"6103,24410":2,"6103,24411":2,"6104,24410":2,"3050,12203":2,"3051,12202":2,"3051,12203":2,"3052,12202":2,"1524,6099":2,"1525,6098":2,"1525,6099":2,"1526,6098":2,"761,3047":2,"762,3046":2,"762,3047":2,"763,3046":2,"379,1521":2,"380,1520":2,"380,1521":2,"381,1520":2,"378,380":2,"379,380":2,"759,762":2,"759,763":2,"1522,1525":2,"1522,1526":2,"3048,3051":2,"3048,3052":2,"6100,6103":2,"6100,6104":2,"12204,12207":2,"12204,12208":1,"12205,12209":1,"24412,24414":2,"24413,24415":3,"24412,24415":3,"24413,24416":2,"24413,24414":1,"24414,24415":1,"24414,24416":1,"48827,390625":1,"48828,390624":1,"48828,390625":1,"48829,390624":1,"24413,97655":1,"24414,97654":1,"24414,97655":1,"24415,97654":1,"12205,48825":1,"12206,48824":1,"12206,48825":1,"12207,48824":1,"12204,12206":1,"12205,12206":1,"24411,24414":1,"24411,24415":1,"24412,24416":1,"48826,48828":1,"48827,48829":2,"48826,48829":1,"48827,48830":1,"48827,48828":1,"48828,48829":1,"48828,48830":1,"97655,390625":1,"97656,390624":1,"97656,390625":1,"97657,390624":1,"71,289":16,"72,288":16,"72,289":16,"73,288":16,"70,72":693,"71,73":381,"70,73":704,"71,74":201,"71,72":185,"72,73":15,"72,74":20,"143,575":9,"144,574":9,"144,575":9,"145,574":9,"70,285":170,"71,284":170,"71,285":170,"72,284":170,"69,71":333,"69,72":670,"70,71":170,"141,144":342,"142,145":194,"141,145":95,"142,146":11,"142,144":344,"143,145":105,"143,146":19,"286,1147":9,"287,1146":9,"287,1147":9,"288,1146":9,"71,287":176,"72,286":176,"72,287":176,"73,286":176,"69,73":338,"70,74":181,"142,571":86,"143,570":86,"143,571":86,"144,570":86,"70,283":162,"71,282":162,"71,283":162,"72,282":162,"68,71":164,"68,72":162,"140,143":162,"140,144":86,"141,143":323,"284,287":170,"285,288":103,"284,288":51,"285,289":9,"285,287":171,"286,288":52,"286,289":9,"572,2291":9,"573,2290":9,"573,2291":9,"574,2290":9,"142,573":85,"143,572":85,"143,573":85,"144,572":85,"142,143":161,"143,144":88,"285,1143":42,"286,1142":42,"286,1143":42,"287,1142":42,"141,569":76,"142,568":76,"142,569":76,"143,568":76,"140,142":76,"141,142":76,"283,286":76,"283,287":42,"284,286":153,"570,573":86,"571,574":61,"570,574":31,"571,575":9,"571,573":85,"572,574":30,"572,575":9,"1144,4579":9,"1145,4578":9,"1145,4579":9,"1146,4578":9,"285,1145":43,"286,1144":43,"286,1145":43,"287,1144":43,"285,286":77,"286,287":43,"571,2287":22,"572,2286":22,"572,2287":22,"573,2286":22,"284,1141":34,"285,1140":34,"285,1141":34,"286,1140":34,"283,285":34,"284,285":34,"569,572":34,"569,573":22,"570,572":67,"1142,1145":42,"1143,1146":39,"1142,1146":19,"1143,1147":9,"1143,1145":43,"1144,1146":20,"1144,1147":9,"2288,9157":4,"2289,9156":4,"2289,9157":4,"2290,9156":4,"571,2289":21,"572,2288":21,"572,2289":21,"573,2288":21,"571,572":33,"572,573":21,"1143,4577":11,"1144,4576":11,"1144,4577":11,"1145,4576":11,"1142,1144":25,"1143,1144":13,"1144,1145":11,"2287,2289":21,"2288,2290":18,"2287,2290":21,"2288,2291":9,"2288,2289":9,"2289,2290":4,"2289,2291":4,"4577,18313":1,"4578,18312":1,"4578,18313":1,"4579,18312":1,"2288,9155":5,"2289,9154":5,"2289,9155":5,"2290,9154":5,"1143,4575":10,"1144,4574":10,"1144,4575":10,"1145,4574":10,"570,2285":12,"571,2284":12,"571,2285":12,"572,2284":12,"569,571":12,"570,571":12,"1141,1144":12,"1141,1145":10,"2286,2289":14,"2286,2290":7,"2287,2291":5,"4576,4578":10,"4577,4579":7,"4576,4579":11,"4577,4580":4,"4577,4578":3,"4578,4579":1,"4578,4580":1,"9155,36623":1,"9156,36622":1,"9156,36623":1,"9157,36622":1,"4576,18309":2,"4577,18308":2,"4577,18309":2,"4578,18308":2,"2287,9153":5,"2288,9152":5,"2288,9153":5,"2289,9152":5,"2286,2288":7,"2287,2288":5,"4575,4577":4,"4575,4578":9,"4576,4577":2,"9153,9156":6,"9154,9157":5,"9153,9157":3,"9154,9158":1,"9154,9156":5,"9155,9157":2,"9155,9158":1,"18310,73243":1,"18311,73242":1,"18311,73243":1,"18312,73242":1,"4577,18311":3,"4578,18310":3,"4578,18311":3,"4579,18310":3,"4575,4579":5,"4576,4580":3,"9154,36619":2,"9155,36618":2,"9155,36619":2,"9156,36618":2,"4576,18307":2,"4577,18306":2,"4577,18307":2,"4578,18306":2,"2287,9151":2,"2288,9150":2,"2288,9151":2,"2289,9150":2,"1142,4573":2,"1143,4572":2,"1143,4573":2,"1144,4572":2,"1141,1143":2,"1142,1143":2,"2285,2288":2,"2285,2289":2,"4574,4577":2,"4574,4578":2,"9152,9155":2,"9152,9156":2,"9153,9155":3,"18308,18311":2,"18309,18312":3,"18308,18312":1,"18309,18313":1,"18309,18311":3,"18310,18312":2,"18310,18313":1,"36620,292968":1,"36621,292967":1,"36621,292968":1,"36622,292967":1,"9154,36621":1,"9155,36620":1,"9155,36621":1,"9156,36620":1,"9154,9155":1,"9155,9156":1,"18309,73241":1,"18310,73240":1,"18310,73241":1,"18311,73240":1,"18308,18310":1,"18309,18310":1,"18310,18311":1,"36619,36621":1,"36620,36622":2,"36619,36622":1,"36620,36623":1,"36620,36621":1,"36621,36622":1,"36621,36623":1,"73241,292968":1,"73242,292967":1,"73242,292968":1,"73243,292967":1,"107,431":50,"108,430":50,"108,431":50,"109,430":50,"105,108":342,"106,109":277,"105,109":135,"106,110":53,"106,108":346,"107,109":146,"107,110":60,"214,861":7,"215,860":7,"215,861":7,"216,860":7,"106,429":86,"107,428":86,"107,429":86,"108,428":86,"105,107":243,"106,107":122,"107,108":89,"213,215":171,"214,216":99,"213,216":170,"214,217":50,"214,215":50,"215,216":7,"215,217":10,"429,1719":7,"430,1718":7,"430,1719":7,"431,1718":7,"213,857":43,"214,856":43,"214,857":43,"215,856":43,"106,427":85,"107,426":85,"107,427":85,"108,426":85,"104,107":121,"104,108":85,"212,214":79,"212,215":157,"213,214":43,"427,430":85,"428,431":56,"427,431":28,"428,432":7,"428,430":85,"429,431":28,"429,432":7,"858,3435":7,"859,3434":7,"859,3435":7,"860,3434":7,"214,859":42,"215,858":42,"215,859":42,"216,858":42,"212,216":78,"213,217":42,"428,1715":21,"429,1714":21,"429,1715":21,"430,1714":21,"213,855":36,"214,854":36,"214,855":36,"215,854":36,"105,425":36,"106,424":36,"106,425":36,"107,424":36,"104,106":36,"105,106":36,"211,214":36,"211,215":36,"426,429":36,"426,430":21,"427,429":72,"856,859":43,"857,860":35,"856,860":18,"857,861":7,"857,859":42,"858,860":17,"858,861":7,"1716,6869":1,"1717,6868":1,"1717,6869":1,"1718,6868":1,"428,1717":21,"429,1716":21,"429,1717":21,"430,1716":21,"428,429":36,"429,430":21,"857,3433":10,"858,3432":10,"858,3433":10,"859,3432":10,"856,858":29,"857,858":14,"858,859":10,"1715,1717":21,"1716,1718":13,"1715,1718":22,"1716,1719":7,"1716,1717":6,"1717,1718":1,"1717,1719":1,"3433,13735":1,"3434,13734":1,"3434,13735":1,"3435,13734":1,"1715,6865":5,"1716,6864":5,"1716,6865":5,"1717,6864":5,"857,3431":11,"858,3430":11,"858,3431":11,"859,3430":11,"427,1713":15,"428,1712":15,"428,1713":15,"429,1712":15,"426,428":15,"427,428":15,"855,858":15,"855,859":11,"1714,1716":9,"1714,1717":19,"1715,1716":5,"3431,3434":11,"3432,3435":8,"3431,3435":4,"3432,3436":1,"3432,3434":11,"3433,3435":4,"3433,3436":1,"6866,27467":1,"6867,27466":1,"6867,27467":1,"6868,27466":1,"1716,6867":6,"1717,6866":6,"1717,6867":6,"1718,6866":6,"1714,1718":10,"1715,1719":6,"3432,13731":3,"3433,13730":3,"3433,13731":3,"3434,13730":3,"1715,6863":4,"1716,6862":4,"1716,6863":4,"1717,6862":4,"856,3429":4,"857,3428":4,"857,3429":4,"858,3428":4,"855,857":4,"856,857":4,"1713,1716":4,"1713,1717":4,"3430,3433":4,"3430,3434":3,"3431,3433":8,"6864,6867":5,"6865,6868":5,"6864,6868":2,"6865,6869":1,"6865,6867":6,"6866,6868":3,"6866,6869":1,"13732,54933":1,"13733,54932":1,"13733,54933":1,"13734,54932":1,"3432,13733":3,"3433,13732":3,"3433,13733":3,"3434,13732":3,"3432,3433":4,"3433,3434":3,"6865,27465":2,"6866,27464":2,"6866,27465":2,"6867,27464":2,"6864,6866":3,"6865,6866":2,"6866,6867":2,"13731,13733":3,"13732,13734":3,"13731,13734":2,"13732,13735":1,"13732,13733":2,"13733,13734":1,"13733,13735":1,"27465,219725":1,"27466,219724":1,"27466,219725":1,"27467,219724":1,"13731,54929":1,"13732,54928":1,"13732,54929":1,"13733,54928":1,"6865,27463":1,"6866,27462":1,"6866,27463":1,"6867,27462":1,"3431,13729":1,"3432,13728":1,"3432,13729":1,"3433,13728":1,"3430,3432":1,"3431,3432":1,"6863,6866":1,"6863,6867":1,"13730,13732":1,"13730,13733":1,"13731,13732":1,"27463,27466":1,"27464,27467":2,"27463,27467":1,"27464,27468":1,"27464,27466":1,"27465,27467":1,"27465,27468":1,"54930,219725":1,"54931,219724":1,"54931,219725":1,"54932,219724":1,"80,323":82,"81,322":82,"81,323":82,"82,322":82,"78,81":343,"79,82":340,"78,82":167,"79,83":85,"79,81":346,"80,82":176,"80,83":91,"160,645":37,"161,644":37,"161,645":37,"162,644":37,"79,321":85,"80,320":85,"80,321":85,"81,320":85,"78,80":182,"79,80":91,"80,81":88,"159,161":170,"160,162":160,"159,162":171,"160,163":82,"160,161":79,"161,162":38,"161,163":42,"321,1289":16,"322,1288":16,"322,1289":16,"323,1288":16,"160,643":43,"161,642":43,"161,643":43,"162,642":43,"79,319":85,"80,318":85,"80,319":85,"81,318":85,"77,80":92,"77,81":85,"158,161":97,"158,162":49,"159,163":43,"320,322":85,"321,323":74,"320,323":85,"321,324":37,"321,322":37,"322,323":16,"322,324":16,"643,2577":5,"644,2576":5,"644,2577":5,"645,2576":5,"321,1287":21,"322,1286":21,"322,1287":21,"323,1286":21,"159,641":42,"160,640":42,"160,641":42,"161,640":42,"158,160":48,"159,160":42,"319,322":54,"319,323":27,"320,324":21,"642,644":42,"643,645":31,"642,645":43,"643,646":16,"643,644":15,"644,645":5,"644,646":5,"1287,5151":5,"1288,5150":5,"1288,5151":5,"1289,5150":5,"642,2573":10,"643,2572":10,"643,2573":10,"644,2572":10,"320,1285":21,"321,1284":21,"321,1285":21,"322,1284":21,"319,321":27,"320,321":21,"641,643":16,"641,644":33,"642,643":10,"1285,1288":22,"1286,1289":21,"1285,1289":11,"1286,1290":5,"1286,1288":21,"1287,1289":10,"1287,1290":5,"2574,10301":2,"2575,10300":2,"2575,10301":2,"2576,10300":2,"643,2575":11,"644,2574":11,"644,2575":11,"645,2574":11,"641,645":17,"642,646":11,"1286,5149":5,"1287,5148":5,"1287,5149":5,"1288,5148":5,"1285,1287":11,"1286,1287":5,"1287,1288":5,"2573,2575":11,"2574,2576":10,"2573,2576":11,"2574,2577":5,"2574,2575":5,"2575,2576":2,"2575,2577":2,"5149,20601":1,"5150,20600":1,"5150,20601":1,"5151,20600":1,"2574,10299":3,"2575,10298":3,"2575,10299":3,"2576,10298":3,"1286,5147":6,"1287,5146":6,"1287,5147":6,"1288,5146":6,"642,2571":6,"643,2570":6,"643,2571":6,"644,2570":6,"320,1283":6,"321,1282":6,"321,1283":6,"322,1282":6,"159,639":6,"160,638":6,"160,639":6,"161,638":6,"78,317":6,"79,316":6,"79,317":6,"80,316":6,"77,79":7,"78,79":6,"157,160":6,"157,161":6,"318,321":6,"318,322":6,"640,643":6,"640,644":6,"1284,1287":6,"1284,1288":6,"2572,2575":6,"2572,2576":3,"2573,2577":3,"5148,5150":6,"5149,5151":5,"5148,5151":5,"5149,5152":2,"5149,5150":3,"5150,5151":1,"5150,5152":1,"10299,41199":1,"10300,41198":1,"10300,41199":1,"10301,41198":1,"5148,20597":2,"5149,20596":2,"5149,20597":2,"5150,20596":2,"2573,10297":3,"2574,10296":3,"2574,10297":3,"2575,10296":3,"2572,2574":3,"2573,2574":3,"5147,5149":2,"5147,5150":3,"5148,5149":2,"10297,10300":2,"10298,10301":3,"10297,10301":1,"10298,10302":1,"10298,10300":3,"10299,10301":2,"10299,10302":1,"20598,164793":1,"20599,164792":1,"20599,164793":1,"20600,164792":1,"5149,20599":1,"5150,20598":1,"5150,20599":1,"5151,20598":1,"5147,5151":1,"5148,5152":1,"10298,41197":1,"10299,41196":1,"10299,41197":1,"10300,41196":1,"10297,10299":1,"10298,10299":1,"10299,10300":1,"20597,20599":1,"20598,20600":2,"20597,20600":1,"20598,20601":1,"20598,20599":1,"20599,20600":1,"20599,20601":1,"41197,164793":1,"41198,164792":1,"41198,164793":1,"41199,164792":1,"120,485":17,"121,484":17,"121,485":17,"122,484":17,"119,121":171,"120,122":123,"119,122":173,"120,123":66,"120,121":60,"121,122":18,"121,123":22,"241,967":17,"242,966":17,"242,967":17,"243,966":17,"119,481":43,"120,480":43,"120,481":43,"121,480":43,"118,120":68,"118,121":136,"119,120":43,"239,242":85,"240,243":77,"239,243":38,"240,244":17,"240,242":86,"241,243":39,"241,244":17,"482,1933":7,"483,1932":7,"483,1933":7,"484,1932":7,"120,483":43,"121,482":43,"121,483":43,"122,482":43,"118,122":68,"119,123":45,"240,965":22,"241,964":22,"241,965":22,"242,964":22,"239,241":51,"240,241":26,"241,242":22,"481,483":43,"482,484":35,"481,484":42,"482,485":17,"482,483":18,"483,484":7,"483,485":7,"965,3865":1,"966,3864":1,"966,3865":1,"967,3864":1,"482,1931":10,"483,1930":10,"483,1931":10,"484,1930":10,"240,963":21,"241,962":21,"241,963":21,"242,962":21,"119,479":25,"120,478":25,"120,479":25,"121,478":25,"117,120":25,"117,121":25,"238,241":25,"238,242":21,"480,483":29,"480,484":14,"481,485":10,"964,966":21,"965,967":13,"964,967":22,"965,968":7,"965,966":6,"966,967":1,"966,968":1,"1931,7727":1,"1932,7726":1,"1932,7727":1,"1933,7726":1,"964,3861":5,"965,3860":5,"965,3861":5,"966,3860":5,"481,1929":11,"482,1928":11,"482,1929":11,"483,1928":11,"480,482":15,"481,482":11,"963,965":9,"963,966":19,"964,965":5,"1929,1932":11,"1930,1933":8,"1929,1933":4,"1930,1934":1,"1930,1932":11,"1931,1933":4,"1931,1934":1,"3862,15451":1,"3863,15450":1,"3863,15451":1,"3864,15450":1,"965,3863":6,"966,3862":6,"966,3863":6,"967,3862":6,"963,967":10,"964,968":6,"1930,7723":3,"1931,7722":3,"1931,7723":3,"1932,7722":3,"964,3859":4,"965,3858":4,"965,3859":4,"966,3858":4,"481,1927":4,"482,1926":4,"482,1927":4,"483,1926":4,"239,961":4,"240,960":4,"240,961":4,"241,960":4,"238,240":4,"239,240":4,"479,482":4,"479,483":4,"962,965":4,"962,966":4,"1928,1931":4,"1928,1932":3,"1929,1931":8,"3860,3863":5,"3861,3864":5,"3860,3864":2,"3861,3865":1,"3861,3863":6,"3862,3864":3,"3862,3865":1,"7724,30901":1,"7725,30900":1,"7725,30901":1,"7726,30900":1,"1930,7725":3,"1931,7724":3,"1931,7725":3,"1932,7724":3,"1930,1931":4,"1931,1932":3,"3861,15449":2,"3862,15448":2,"3862,15449":2,"3863,15448":2,"3860,3862":3,"3861,3862":2,"3862,3863":2,"7723,7725":3,"7724,7726":3,"7723,7726":2,"7724,7727":1,"7724,7725":2,"7725,7726":1,"7725,7727":1,"15449,123594":1,"15450,123593":1,"15450,123594":1,"15451,123593":1,"7723,30897":1,"7724,30896":1,"7724,30897":1,"7725,30896":1,"3861,15447":1,"3862,15446":1,"3862,15447":1,"3863,15446":1,"1929,7721":1,"1930,7720":1,"1930,7721":1,"1931,7720":1,"1928,1930":1,"1929,1930":1,"3859,3862":1,"3859,3863":1,"7722,7724":1,"7722,7725":1,"7723,7724":1,"15447,15450":1,"15448,15451":2,"15447,15451":1,"15448,15452":1,"15448,15450":1,"15449,15451":1,"15449,15452":1,"30898,123594":1,"30899,123593":1,"30899,123594":1,"30900,123593":1,"90,365":3,"91,364":3,"91,365":3,"92,364":3,"89,91":173,"90,92":95,"89,92":175,"90,93":50,"90,91":46,"91,92":4,"91,93":6,"181,727":2,"182,726":2,"182,727":2,"183,726":2,"89,361":43,"90,360":43,"90,361":43,"91,360":43,"88,90":83,"88,91":167,"89,90":43,"179,182":85,"180,183":48,"179,183":23,"180,184":3,"180,182":86,"181,183":25,"181,184":5,"362,1451":2,"363,1450":2,"363,1451":2,"364,1450":2,"90,363":44,"91,362":44,"91,363":44,"92,362":44,"88,92":84,"89,93":45,"180,723":21,"181,722":21,"181,723":21,"182,722":21,"89,359":40,"90,358":40,"90,359":40,"91,358":40,"87,90":40,"87,91":40,"178,181":40,"178,182":21,"179,181":81,"360,363":43,"361,364":26,"360,364":13,"361,365":2,"361,363":43,"362,364":13,"362,365":2,"724,2899":2,"725,2898":2,"725,2899":2,"726,2898":2,"180,725":22,"181,724":22,"181,725":22,"182,724":22,"180,181":41,"181,182":22,"361,1447":11,"362,1446":11,"362,1447":11,"363,1446":11,"179,721":19,"180,720":19,"180,721":19,"181,720":19,"178,180":19,"179,180":19,"359,362":19,"359,363":11,"360,362":38,"722,725":21,"723,726":15,"722,726":7,"723,727":2,"723,725":22,"724,726":8,"724,727":2,"1448,5795":2,"1449,5794":2,"1449,5795":2,"1450,5794":2,"361,1449":11,"362,1448":11,"362,1449":11,"363,1448":11,"361,362":19,"362,363":11,"723,2895":5,"724,2894":5,"724,2895":5,"725,2894":5,"360,1445":8,"361,1444":8,"361,1445":8,"362,1444":8,"359,361":8,"360,361":8,"721,724":8,"721,725":5,"722,724":17,"1446,1449":11,"1447,1450":10,"1446,1450":5,"1447,1451":2,"1447,1449":11,"1448,1450":5,"1448,1451":2,"2896,11589":1,"2897,11588":1,"2897,11589":1,"2898,11588":1,"723,2897":6,"724,2896":6,"724,2897":6,"725,2896":6,"723,724":9,"724,725":6,"1447,5793":3,"1448,5792":3,"1448,5793":3,"1449,5792":3,"1446,1448":6,"1447,1448":3,"1448,1449":3,"2895,2897":6,"2896,2898":5,"2895,2898":5,"2896,2899":2,"2896,2897":3,"2897,2898":1,"2897,2899":1,"5793,23175":1,"5794,23174":1,"5794,23175":1,"5795,23174":1,"2895,11585":2,"2896,11584":2,"2896,11585":2,"2897,11584":2,"1447,5791":3,"1448,5790":3,"1448,5791":3,"1449,5790":3,"722,2893":3,"723,2892":3,"723,2893":3,"724,2892":3,"721,723":3,"722,723":3,"1445,1448":3,"1445,1449":3,"2894,2896":2,"2894,2897":3,"2895,2896":2,"5791,5794":2,"5792,5795":3,"5791,5795":1,"5792,5796":1,"5792,5794":3,"5793,5795":2,"5793,5796":1,"11586,92694":1,"11587,92693":1,"11587,92694":1,"11588,92693":1,"2896,11587":1,"2897,11586":1,"2897,11587":1,"2898,11586":1,"2894,2898":1,"2895,2899":1,"5792,23173":1,"5793,23172":1,"5793,23173":1,"5794,23172":1,"5791,5793":1,"5792,5793":1,"5793,5794":1,"11585,11587":1,"11586,11588":2,"11585,11588":1,"11586,11589":1,"11586,11587":1,"11587,11588":1,"11587,11589":1,"23173,92694":1,"23174,92693":1,"23174,92694":1,"23175,92693":1,"67,273":36,"68,272":36,"68,273":36,"69,272":36,"66,68":173,"67,69":159,"66,69":173,"67,70":81,"67,68":79,"68,69":37,"68,70":39,"135,545":12,"136,544":12,"136,545":12,"137,544":12,"67,271":42,"68,270":42,"68,271":42,"69,270":42,"65,68":103,"65,69":51,"66,70":43,"134,136":85,"135,137":68,"134,137":86,"135,138":36,"135,136":33,"136,137":13,"136,138":15,"271,1089":2,"272,1088":2,"272,1089":2,"273,1088":2,"135,543":22,"136,542":22,"136,543":22,"137,542":22,"66,269":43,"67,268":43,"67,269":43,"68,268":43,"65,67":53,"66,67":43,"133,136":61,"133,137":31,"134,138":22,"270,272":43,"271,273":25,"270,273":42,"271,274":12,"271,272":13,"272,273":2,"272,274":2,"543,2175":2,"544,2174":2,"544,2175":2,"545,2174":2,"270,1085":11,"271,1084":11,"271,1085":11,"272,1084":11,"134,541":21,"135,540":21,"135,541":21,"136,540":21,"133,135":30,"134,135":21,"269,271":20,"269,272":39,"270,271":11,"541,544":21,"542,545":14,"541,545":7,"542,546":2,"542,544":21,"543,545":7,"543,546":2,"1086,4347":2,"1087,4346":2,"1087,4347":2,"1088,4346":2,"271,1087":10,"272,1086":10,"272,1087":10,"273,1086":10,"269,273":19,"270,274":10,"542,2171":5,"543,2170":5,"543,2171":5,"544,2170":5,"270,1083":9,"271,1082":9,"271,1083":9,"272,1082":9,"134,539":9,"135,538":9,"135,539":9,"136,538":9,"66,267":9,"67,266":9,"67,267":9,"68,266":9,"64,67":20,"64,68":9,"132,135":9,"132,136":9,"268,271":9,"268,272":9,"540,543":9,"540,544":5,"541,543":18,"1084,1087":11,"1085,1088":9,"1084,1088":5,"1085,1089":2,"1085,1087":10,"1086,1088":4,"1086,1089":2,"2172,8691":2,"2173,8690":2,"2173,8691":2,"2174,8690":2,"542,2173":5,"543,2172":5,"543,2173":5,"544,2172":5,"542,543":9,"543,544":5,"1085,4343":3,"1086,4342":3,"1086,4343":3,"1087,4342":3,"541,2169":4,"542,2168":4,"542,2169":4,"543,2168":4,"540,542":4,"541,542":4,"1083,1086":4,"1083,1087":3,"1084,1086":7,"2170,2173":5,"2171,2174":6,"2170,2174":3,"2171,2175":2,"2171,2173":5,"2172,2174":3,"2172,2175":2,"4344,17381":1,"4345,17380":1,"4345,17381":1,"4346,17380":1,"1085,4345":2,"1086,4344":2,"1086,4345":2,"1087,4344":2,"1085,1086":3,"1086,1087":2,"2171,8689":1,"2172,8688":1,"2172,8689":1,"2173,8688":1,"2170,2172":2,"2171,2172":1,"2172,2173":1,"4343,4345":2,"4344,4346":3,"4343,4346":3,"4344,4347":2,"4344,4345":1,"4345,4346":1,"4345,4347":1,"8689,69519":1,"8690,69518":1,"8690,69519":1,"8691,69518":1,"4344,17379":1,"4345,17378":1,"4345,17379":1,"4346,17378":1,"2171,8687":1,"2172,8686":1,"2172,8687":1,"2173,8686":1,"1084,4341":1,"1085,4340":1,"1085,4341":1,"1086,4340":1,"1083,1085":1,"1084,1085":1,"2169,2172":1,"2169,2173":1,"4342,4345":1,"4342,4346":1,"4343,4347":1,"8688,8690":1,"8689,8691":2,"8688,8691":1,"8689,8692":1,"8689,8690":1,"8690,8691":1,"8690,8692":1,"17379,69519":1,"17380,69518":1,"17380,69519":1,"17381,69518":1,"101,409":15,"102,408":15,"102,409":15,"103,408":15,"100,102":85,"101,103":74,"100,103":86,"101,104":39,"101,102":36,"102,103":16,"102,104":18,"203,817":4,"204,816":4,"204,817":4,"205,816":4,"101,407":21,"102,406":21,"102,407":21,"103,406":21,"99,102":56,"99,103":28,"100,104":22,"202,204":42,"203,205":29,"202,205":43,"203,206":15,"203,204":14,"204,205":4,"204,206":5,"407,1631":4,"408,1630":4,"408,1631":4,"409,1630":4,"202,813":10,"203,812":10,"203,813":10,"204,812":10,"100,405":21,"101,404":21,"101,405":21,"102,404":21,"99,101":28,"100,101":21,"201,203":17,"201,204":35,"202,203":10,"405,408":22,"406,409":19,"405,409":10,"406,410":4,"406,408":21,"407,409":9,"407,410":4,"814,3261":1,"815,3260":1,"815,3261":1,"816,3260":1,"203,815":11,"204,814":11,"204,815":11,"205,814":11,"201,205":18,"202,206":11,"406,1629":5,"407,1628":5,"407,1629":5,"408,1628":5,"405,407":13,"406,407":6,"407,408":5,"813,815":11,"814,816":8,"813,816":11,"814,817":4,"814,815":4,"815,816":1,"815,817":1,"1629,6519":1,"1630,6518":1,"1630,6519":1,"1631,6518":1,"813,3257":3,"814,3256":3,"814,3257":3,"815,3256":3,"406,1627":6,"407,1626":6,"407,1627":6,"408,1626":6,"202,811":7,"203,810":7,"203,811":7,"204,810":7,"100,403":7,"101,402":7,"101,403":7,"102,402":7,"98,101":7,"98,102":7,"200,203":7,"200,204":7,"404,407":7,"404,408":6,"812,814":4,"812,815":8,"813,814":3,"1627,1630":5,"1628,1631":5,"1627,1631":2,"1628,1632":1,"1628,1630":6,"1629,1631":3,"1629,1632":1,"3258,13037":1,"3259,13036":1,"3259,13037":1,"3260,13036":1,"814,3259":3,"815,3258":3,"815,3259":3,"816,3258":3,"812,816":4,"813,817":3,"1628,6517":2,"1629,6516":2,"1629,6517":2,"1630,6516":2,"1627,1629":3,"1628,1629":2,"1629,1630":2,"3257,3259":3,"3258,3260":3,"3257,3260":2,"3258,3261":1,"3258,3259":2,"3259,3260":1,"3259,3261":1,"6517,52138":1,"6518,52137":1,"6518,52138":1,"6519,52137":1,"3257,13033":1,"3258,13032":1,"3258,13033":1,"3259,13032":1,"1628,6515":1,"1629,6514":1,"1629,6515":1,"1630,6514":1,"813,3255":1,"814,3254":1,"814,3255":1,"815,3254":1,"405,1625":1,"406,1624":1,"406,1625":1,"407,1624":1,"404,406":1,"405,406":1,"811,814":1,"811,815":1,"1626,1629":1,"1626,1630":1,"3256,3258":1,"3256,3259":1,"3257,3258":1,"6515,6518":1,"6516,6519":2,"6515,6519":1,"6516,6520":1,"6516,6518":1,"6517,6519":1,"6517,6520":1,"13034,52138":1,"13035,52137":1,"13035,52138":1,"13036,52137":1,"76,307":17,"77,306":17,"77,307":17,"78,306":17,"74,77":86,"75,78":78,"74,78":38,"75,79":18,"75,77":87,"76,78":40,"76,79":19,"152,613":6,"153,612":6,"153,613":6,"154,612":6,"75,305":22,"76,304":22,"76,305":22,"77,304":22,"74,76":53,"75,76":27,"76,77":22,"151,153":43,"152,154":33,"151,154":42,"152,155":17,"152,153":17,"153,154":6,"153,155":7,"305,1223":6,"306,1222":6,"306,1223":6,"307,1222":6,"151,609":11,"152,608":11,"152,609":11,"153,608":11,"75,303":21,"76,302":21,"76,303":21,"77,302":21,"73,76":26,"73,77":21,"150,152":16,"150,153":31,"151,152":11,"303,306":21,"304,307":22,"303,307":11,"304,308":6,"304,306":21,"305,307":11,"305,308":6,"610,2445":3,"611,2444":3,"611,2445":3,"612,2444":3,"152,611":10,"153,610":10,"153,611":10,"154,610":10,"150,154":15,"151,155":10,"304,1221":5,"305,1220":5,"305,1221":5,"306,1220":5,"303,305":10,"304,305":5,"305,306":5,"609,611":10,"610,612":11,"609,612":11,"610,613":6,"610,611":5,"611,612":3,"611,613":3,"1221,4889":2,"1222,4888":2,"1222,4889":2,"1223,4888":2,"610,2443":3,"611,2442":3,"611,2443":3,"612,2442":3,"304,1219":5,"305,1218":5,"305,1219":5,"306,1218":5,"151,607":5,"152,606":5,"152,607":5,"153,606":5,"74,301":5,"75,300":5,"75,301":5,"76,300":5,"73,75":5,"74,75":5,"149,152":5,"149,153":5,"302,305":5,"302,306":5,"608,611":5,"608,612":3,"609,613":3,"1220,1222":5,"1221,1223":6,"1220,1223":5,"1221,1224":3,"1221,1222":3,"1222,1223":2,"1222,1224":2,"2443,9777":1,"2444,9776":1,"2444,9777":1,"2445,9776":1,"1221,4887":1,"1222,4886":1,"1222,4887":1,"1223,4886":1,"609,2441":2,"610,2440":2,"610,2441":2,"611,2440":2,"608,610":2,"609,610":2,"1219,1222":2,"1219,1223":1,"1220,1224":1,"2442,2444":2,"2443,2445":3,"2442,2445":3,"2443,2446":2,"2443,2444":1,"2444,2445":1,"2444,2446":1,"4887,39102":1,"4888,39101":1,"4888,39102":1,"4889,39101":1,"2443,9775":1,"2444,9774":1,"2444,9775":1,"2445,9774":1,"1220,4885":1,"1221,4884":1,"1221,4885":1,"1222,4884":1,"1219,1221":1,"1220,1221":1,"2441,2444":1,"2441,2445":1,"2442,2446":1,"4886,4888":1,"4887,4889":2,"4886,4889":1,"4887,4890":1,"4887,4888":1,"4888,4889":1,"4888,4890":1,"9775,39102":1,"9776,39101":1,"9776,39102":1,"9777,39101":1,"114,461":1,"115,460":1,"115,461":1,"116,460":1,"113,115":43,"114,116":25,"113,116":44,"114,117":14,"114,115":12,"115,116":1,"115,117":2,"229,919":1,"230,918":1,"230,919":1,"231,918":1,"113,457":11,"114,456":11,"114,457":11,"115,456":11,"112,114":20,"112,115":40,"113,114":11,"227,230":21,"228,231":13,"227,231":6,"228,232":1,"228,230":22,"229,231":7,"229,232":1,"458,1835":1,"459,1834":1,"459,1835":1,"460,1834":1,"114,459":11,"115,458":11,"115,459":11,"116,458":11,"112,116":20,"113,117":12,"228,915":5,"229,914":5,"229,915":5,"230,914":5,"113,455":9,"114,454":9,"114,455":9,"115,454":9,"111,114":9,"111,115":9,"226,229":9,"226,230":5,"227,229":19,"456,459":11,"457,460":8,"456,460":4,"457,461":1,"457,459":11,"458,460":4,"458,461":1,"916,3667":1,"917,3666":1,"917,3667":1,"918,3666":1,"228,917":6,"229,916":6,"229,917":6,"230,916":6,"228,229":10,"229,230":6,"457,1831":3,"458,1830":3,"458,1831":3,"459,1830":3,"227,913":4,"228,912":4,"228,913":4,"229,912":4,"226,228":4,"227,228":4,"455,458":4,"455,459":3,"456,458":8,"914,917":5,"915,918":5,"914,918":2,"915,919":1,"915,917":6,"916,918":3,"916,919":1,"1832,7333":1,"1833,7332":1,"1833,7333":1,"1834,7332":1,"457,1833":3,"458,1832":3,"458,1833":3,"459,1832":3,"457,458":4,"458,459":3,"915,3665":2,"916,3664":2,"916,3665":2,"917,3664":2,"914,916":3,"915,916":2,"916,917":2,"1831,1833":3,"1832,1834":3,"1831,1834":2,"1832,1835":1,"1832,1833":2,"1833,1834":1,"1833,1835":1,"3665,29325":1,"3666,29324":1,"3666,29325":1,"3667,29324":1,"1831,7329":1,"1832,7328":1,"1832,7329":1,"1833,7328":1,"915,3663":1,"916,3662":1,"916,3663":1,"917,3662":1,"456,1829":1,"457,1828":1,"457,1829":1,"458,1828":1,"455,457":1,"456,457":1,"913,916":1,"913,917":1,"1830,1832":1,"1830,1833":1,"1831,1832":1,"3663,3666":1,"3664,3667":2,"3663,3667":1,"3664,3668":1,"3664,3666":1,"3665,3667":1,"3665,3668":1,"7330,29325":1,"7331,29324":1,"7331,29325":1,"7332,29324":1,"85,345":9,"86,344":9,"86,345":9,"87,344":9,"84,86":42,"85,87":40,"84,87":44,"85,88":22,"85,86":19,"86,87":9,"86,88":10,"171,689":4,"172,688":4,"172,689":4,"173,688":4,"85,343":11,"86,342":11,"86,343":11,"87,342":11,"83,86":25,"83,87":13,"84,88":12,"170,172":21,"171,173":18,"170,173":21,"171,174":9,"171,172":9,"172,173":4,"172,174":4,"343,1377":1,"344,1376":1,"344,1377":1,"345,1376":1,"171,687":5,"172,686":5,"172,687":5,"173,686":5,"84,341":10,"85,340":10,"85,341":10,"86,340":10,"83,85":12,"84,85":10,"169,172":14,"169,173":7,"170,174":5,"342,344":10,"343,345":7,"342,345":11,"343,346":4,"343,344":3,"344,345":1,"344,346":1,"687,2751":1,"688,2750":1,"688,2751":1,"689,2750":1,"342,1373":2,"343,1372":2,"343,1373":2,"344,1372":2,"170,685":5,"171,684":5,"171,685":5,"172,684":5,"169,171":7,"170,171":5,"341,343":4,"341,344":9,"342,343":2,"685,688":6,"686,689":5,"685,689":3,"686,690":1,"686,688":5,"687,689":2,"687,690":1,"1374,5499":1,"1375,5498":1,"1375,5499":1,"1376,5498":1,"343,1375":3,"344,1374":3,"344,1375":3,"345,1374":3,"341,345":5,"342,346":3,"686,2747":2,"687,2746":2,"687,2747":2,"688,2746":2,"342,1371":2,"343,1370":2,"343,1371":2,"344,1370":2,"170,683":2,"171,682":2,"171,683":2,"172,682":2,"84,339":2,"85,338":2,"85,339":2,"86,338":2,"82,85":2,"82,86":2,"168,171":2,"168,172":2,"340,343":2,"340,344":2,"684,687":2,"684,688":2,"685,687":3,"1372,1375":2,"1373,1376":3,"1372,1376":1,"1373,1377":1,"1373,1375":3,"1374,1376":2,"1374,1377":1,"2748,21993":1,"2749,21992":1,"2749,21993":1,"2750,21992":1,"686,2749":1,"687,2748":1,"687,2749":1,"688,2748":1,"686,687":1,"687,688":1,"1373,5497":1,"1374,5496":1,"1374,5497":1,"1375,5496":1,"1372,1374":1,"1373,1374":1,"1374,1375":1,"2747,2749":1,"2748,2750":2,"2747,2750":1,"2748,2751":1,"2748,2749":1,"2749,2750":1,"2749,2751":1,"5497,21993":1,"5498,21992":1,"5498,21993":1,"5499,21992":1,"64,259":10,"65,258":10,"65,259":10,"66,258":10,"62,65":10,"63,66":21,"62,66":10,"63,67":10,"63,65":11,"64,66":12,"128,517":4,"129,516":4,"129,517":4,"130,516":4,"127,129":21,"128,130":19,"127,130":22,"128,131":10,"128,129":9,"129,130":4,"129,131":4,"257,1033":2,"258,1032":2,"258,1033":2,"259,1032":2,"128,515":6,"129,514":6,"129,515":6,"130,514":6,"126,129":13,"126,130":7,"127,131":6,"256,258":11,"257,259":9,"256,259":10,"257,260":4,"257,258":5,"258,259":2,"258,260":2,"515,2063":2,"516,2062":2,"516,2063":2,"517,2062":2,"256,1029":3,"257,1028":3,"257,1029":3,"258,1028":3,"127,513":5,"128,512":5,"128,513":5,"129,512":5,"126,128":6,"127,128":5,"255,257":4,"255,258":7,"256,257":3,"513,516":5,"514,517":6,"513,517":3,"514,518":2,"514,516":5,"515,517":3,"515,518":2,"1030,4125":1,"1031,4124":1,"1031,4125":1,"1032,4124":1,"257,1031":2,"258,1030":2,"258,1031":2,"259,1030":2,"255,259":3,"256,260":2,"514,2061":1,"515,2060":1,"515,2061":1,"516,2060":1,"513,515":2,"514,515":1,"515,516":1,"1029,1031":2,"1030,1032":3,"1029,1032":3,"1030,1033":2,"1030,1031":1,"1031,1032":1,"1031,1033":1,"2061,16494":1,"2062,16493":1,"2062,16494":1,"2063,16493":1,"1030,4123":1,"1031,4122":1,"1031,4123":1,"1032,4122":1,"514,2059":1,"515,2058":1,"515,2059":1,"516,2058":1,"256,1027":1,"257,1026":1,"257,1027":1,"258,1026":1,"127,511":1,"128,510":1,"128,511":1,"129,510":1,"125,128":1,"125,129":1,"254,257":1,"254,258":1,"512,515":1,"512,516":1,"1028,1031":1,"1028,1032":1,"1029,1033":1,"2060,2062":1,"2061,2063":2,"2060,2063":1,"2061,2064":1,"2061,2062":1,"2062,2063":1,"2062,2064":1,"4123,16494":1,"4124,16493":1,"4124,16494":1,"4125,16493":1,"96,389":2,"97,388":2,"97,389":2,"98,388":2,"96,98":14,"96,99":7,"96,97":7,"97,98":2,"97,99":2,"193,775":2,"194,774":2,"194,775":2,"195,774":2,"95,385":5,"96,384":5,"96,385":5,"97,384":5,"191,194":11,"192,195":9,"191,195":5,"192,196":2,"192,194":10,"193,195":4,"193,196":2,"386,1547":2,"387,1546":2,"387,1547":2,"388,1546":2,"96,387":6,"97,386":6,"97,387":6,"98,386":6,"95,99":5,"192,771":3,"193,770":3,"193,771":3,"194,770":3,"190,194":3,"384,387":5,"385,388":6,"384,388":3,"385,389":2,"385,387":5,"386,388":3,"386,389":2,"772,3093":1,"773,3092":1,"773,3093":1,"774,3092":1,"192,773":2,"193,772":2,"193,773":2,"194,772":2,"192,193":3,"193,194":2,"385,1545":1,"386,1544":1,"386,1545":1,"387,1544":1,"384,386":2,"385,386":1,"386,387":1,"771,773":2,"772,774":3,"771,774":3,"772,775":2,"772,773":1,"773,774":1,"773,775":1,"1545,12369":1,"1546,12368":1,"1546,12369":1,"1547,12368":1,"772,3091":1,"773,3090":1,"773,3091":1,"774,3090":1,"385,1543":1,"386,1542":1,"386,1543":1,"387,1542":1,"191,769":1,"192,768":1,"192,769":1,"193,768":1,"383,386":1,"383,387":1,"770,773":1,"770,774":1,"771,775":1,"1544,1546":1,"1545,1547":2,"1544,1547":1,"1545,1548":1,"1545,1546":1,"1546,1547":1,"1546,1548":1,"3091,12369":1,"3092,12368":1,"3092,12369":1,"3093,12368":1,"72,291":5,"73,290":5,"73,291":5,"74,290":5,"71,75":5,"72,75":5,"144,581":3,"145,580":3,"145,581":3,"146,580":3,"144,146":11,"144,147":5,"144,145":6,"145,146":3,"145,147":3,"289,1161":1,"290,1160":1,"290,1161":1,"291,1160":1,"144,579":2,"145,578":2,"145,579":2,"146,578":2,"143,147":2,"288,290":5,"289,291":5,"288,291":6,"289,292":3,"289,290":2,"290,291":1,"290,292":1,"579,2321":1,"580,2320":1,"580,2321":1,"581,2320":1,"289,1159":2,"290,1158":2,"290,1159":2,"291,1158":2,"143,577":3,"144,576":3,"144,577":3,"145,576":3,"287,290":3,"287,291":2,"288,292":2,"578,580":3,"579,581":3,"578,581":2,"579,582":1,"579,580":2,"580,581":1,"580,582":1,"1159,9276":1,"1160,9275":1,"1160,9276":1,"1161,9275":1,"578,2317":1,"579,2316":1,"579,2317":1,"580,2316":1,"288,1157":1,"289,1156":1,"289,1157":1,"290,1156":1,"287,289":1,"288,289":1,"577,579":1,"577,580":1,"578,579":1,"1157,1160":1,"1158,1161":2,"1157,1161":1,"1158,1162":1,"1158,1160":1,"1159,1161":1,"1159,1162":1,"2318,9276":1,"2319,9275":1,"2319,9276":1,"2320,9275":1,"108,437":1,"109,436":1,"109,437":1,"110,436":1,"108,110":8,"108,111":4,"108,109":4,"109,110":1,"109,111":1,"217,871":1,"218,870":1,"218,871":1,"219,870":1,"107,433":3,"108,432":3,"108,433":3,"109,432":3,"215,218":5,"216,219":5,"215,219":2,"216,220":1,"216,218":6,"217,219":3,"217,220":1,"434,1741":1,"435,1740":1,"435,1741":1,"436,1740":1,"108,435":3,"109,434":3,"109,435":3,"110,434":3,"107,111":3,"216,869":2,"217,868":2,"217,869":2,"218,868":2,"216,217":2,"217,218":2,"433,435":3,"434,436":3,"433,436":2,"434,437":1,"434,435":2,"435,436":1,"435,437":1,"869,6956":1,"870,6955":1,"870,6956":1,"871,6955":1,"433,1737":1,"434,1736":1,"434,1737":1,"435,1736":1,"216,867":1,"217,866":1,"217,867":1,"218,866":1,"214,218":1,"432,434":1,"432,435":1,"433,434":1,"867,870":1,"868,871":2,"867,871":1,"868,872":1,"868,870":1,"869,871":1,"869,872":1,"1738,6956":1,"1739,6955":1,"1739,6956":1,"1740,6955":1,"81,327":3,"82,326":3,"82,327":3,"83,326":3,"80,84":3,"81,83":6,"81,84":3,"162,653":2,"163,652":2,"163,653":2,"164,652":2,"80,325":3,"81,324":3,"81,325":3,"82,324":3,"81,82":3,"162,164":6,"161,164":5,"162,165":3,"162,163":3,"163,164":2,"163,165":2,"325,1305":1,"326,1304":1,"326,1305":1,"327,1304":1,"162,651":1,"163,650":1,"163,651":1,"164,650":1,"160,164":1,"161,165":1,"324,326":2,"325,327":3,"324,327":3,"325,328":2,"325,326":1,"326,327":1,"326,328":1,"651,5216":1,"652,5215":1,"652,5216":1,"653,5215":1,"325,1303":1,"326,1302":1,"326,1303":1,"327,1302":1,"161,649":1,"162,648":1,"162,649":1,"163,648":1,"323,326":1,"323,327":1,"324,328":1,"650,652":1,"651,653":2,"650,653":1,"651,654":1,"651,652":1,"652,653":1,"652,654":1,"1303,5216":1,"1304,5215":1,"1304,5216":1,"1305,5215":1,"122,491":1,"123,490":1,"123,491":1,"124,490":1,"121,124":5,"120,124":3,"121,125":1,"122,124":2,"122,125":1,"244,979":1,"245,978":1,"245,979":1,"246,978":1,"121,487":2,"122,486":2,"122,487":2,"123,486":2,"242,245":2,"243,246":3,"242,246":1,"243,247":1,"243,245":3,"244,246":2,"244,247":1,"488,3911":1,"489,3910":1,"489,3911":1,"490,3910":1,"121,489":1,"122,488":1,"122,489":1,"123,488":1,"122,123":1,"243,977":1,"244,976":1,"244,977":1,"245,976":1,"242,244":1,"243,244":1,"244,245":1,"487,489":1,"488,490":2,"487,490":1,"488,491":1,"488,489":1,"489,490":1,"489,491":1,"977,3911":1,"978,3910":1,"978,3911":1,"979,3910":1,"91,369":1,"92,368":1,"92,369":1,"93,368":1,"91,94":2,"92,93":1,"183,735":1,"184,734":1,"184,735":1,"185,734":1,"182,185":3,"181,185":2,"182,186":1,"182,184":2,"183,185":1,"183,186":1,"366,2932":1,"367,2931":1,"367,2932":1,"368,2931":1,"91,367":1,"92,366":1,"92,367":1,"93,366":1,"90,94":1,"182,731":1,"183,730":1,"183,731":1,"184,730":1,"364,367":1,"365,368":2,"364,368":1,"365,369":1,"365,367":1,"366,368":1,"366,369":1,"732,2932":1,"733,2931":1,"733,2932":1,"734,2931":1,"68,277":1,"69,276":1,"69,277":1,"70,276":1,"69,70":1,"137,551":1,"138,550":1,"138,551":1,"139,550":1,"136,139":3,"135,139":1,"136,140":1,"137,139":2,"137,140":1,"274,2198":1,"275,2197":1,"275,2198":1,"276,2197":1,"68,275":1,"69,274":1,"69,275":1,"70,274":1,"67,71":1,"136,549":1,"137,548":1,"137,549":1,"138,548":1,"137,138":1,"273,275":1,"274,276":2,"273,276":1,"274,277":1,"274,275":1,"275,276":1,"275,277":1,"549,2198":1,"550,2197":1,"550,2198":1,"551,2197":1,"102,413":1,"103,412":1,"103,413":1,"104,412":1,"102,105":2,"103,104":1,"103,105":1,"205,1647":1,"206,1646":1,"206,1647":1,"207,1646":1,"102,411":1,"103,410":1,"103,411":1,"104,410":1,"101,105":1,"205,207":2,"204,207":1,"205,208":1,"205,206":1,"206,207":1,"206,208":1,"411,1647":1,"412,1646":1,"412,1647":1,"413,1646":1,"77,311":1,"78,310":1,"78,311":1,"79,310":1,"76,80":1,"154,1234":1,"155,1233":1,"155,1234":1,"156,1233":1,"153,156":2,"152,156":1,"153,157":1,"154,156":1,"154,157":1,"308,1234":1,"309,1233":1,"309,1234":1,"310,1233":1,"115,924":1,"116,923":1,"116,924":1,"117,923":1,"114,118":1,"115,118":1,"230,924":1,"231,923":1,"231,924":1,"232,923":1,"86,692":1,"87,691":1,"87,692":1,"88,691":1,"85,89":1,"86,89":1,"172,692":1,"173,691":1,"173,692":1,"174,691":1,"64,518":1,"65,517":1,"65,518":1,"66,517":1,"64,65":1,"65,66":1,"129,518":1,"130,517":1,"130,518":1,"131,517":1,"53,216":1,"54,215":1,"54,216":1,"55,215":1},"monic":{"1":1}}
```

`gcd_trace_r2_t1.json` (trial 1: histogram of every charged half-gcd and root operation by kind and size; `halfgcd_charge.py` recomputes the stage charge from it):

```json
{"copy":{"97657":1,"97656":1,"48829":2,"48828":2,"24415":3,"24414":3,"12209":3,"12208":3,"6105":8,"6104":8,"3053":19,"3052":19,"1527":40,"1526":40,"765":40,"764":40,"383":130,"382":130,"193":137,"192":137,"189":345,"188":345,"381":170,"380":170,"191":351,"190":351,"761":85,"760":85,"379":171,"378":171,"187":216,"186":216,"1525":43,"1524":43,"763":86,"762":86,"3051":21,"3050":21,"1523":43,"1522":43,"759":45,"758":45,"377":45,"376":45,"6103":11,"6102":11,"3049":22,"3048":22,"12205":6,"12204":6,"6101":11,"6100":11,"24413":3,"24412":3,"12207":5,"12206":5,"48827":1,"48826":1,"24411":2,"24410":2,"12203":2,"12202":2,"6099":2,"6098":2,"3047":2,"3046":2,"1521":2,"1520":2,"97655":1,"97654":1,"48825":1,"48824":1,"73243":1,"73242":1,"36623":1,"36622":1,"18313":1,"18312":1,"9157":4,"9156":4,"4579":9,"4578":9,"2291":9,"2290":9,"1147":9,"1146":9,"575":9,"574":9,"289":15,"288":15,"145":191,"144":191,"143":352,"142":352,"285":170,"284":170,"141":346,"140":346,"571":86,"570":86,"287":176,"286":176,"283":162,"282":162,"139":164,"138":164,"1143":42,"1142":42,"573":85,"572":85,"569":76,"568":76,"2287":22,"2286":22,"1145":43,"1144":43,"1141":34,"1140":34,"4577":11,"4576":11,"2289":21,"2288":21,"9155":5,"9154":5,"4575":10,"4574":10,"2285":12,"2284":12,"18309":2,"18308":2,"9153":5,"9152":5,"36619":2,"36618":2,"18311":3,"18310":3,"18307":2,"18306":2,"9151":2,"9150":2,"4573":2,"4572":2,"73241":1,"73240":1,"36621":1,"36620":1,"54933":1,"54932":1,"27467":1,"27466":1,"13735":1,"13734":1,"6869":1,"6868":1,"3435":7,"3434":7,"1719":7,"1718":7,"861":7,"860":7,"431":50,"430":50,"217":54,"216":54,"213":172,"212":172,"429":86,"428":86,"215":177,"214":177,"857":43,"856":43,"427":85,"426":85,"211":121,"210":121,"1715":21,"1714":21,"859":42,"858":42,"855":36,"854":36,"425":36,"424":36,"3433":10,"3432":10,"1717":21,"1716":21,"6865":5,"6864":5,"3431":11,"3430":11,"1713":15,"1712":15,"13731":3,"13730":3,"6867":6,"6866":6,"6863":4,"6862":4,"3429":4,"3428":4,"27465":2,"27464":2,"13733":3,"13732":3,"54929":1,"54928":1,"27463":1,"27462":1,"13729":1,"13728":1,"41199":1,"41198":1,"20601":1,"20600":1,"10301":2,"10300":2,"5151":5,"5150":5,"2577":5,"2576":5,"1289":16,"1288":16,"645":37,"644":37,"323":82,"322":82,"163":85,"162":85,"159":173,"158":173,"321":85,"320":85,"161":176,"160":176,"643":43,"642":43,"319":85,"318":85,"157":92,"156":92,"1287":21,"1286":21,"641":42,"640":42,"2573":10,"2572":10,"1285":21,"1284":21,"5149":5,"5148":5,"2575":11,"2574":11,"10299":3,"10298":3,"5147":6,"5146":6,"2571":6,"2570":6,"1283":6,"1282":6,"639":6,"638":6,"317":6,"316":6,"20597":2,"20596":2,"10297":3,"10296":3,"41197":1,"41196":1,"20599":1,"20598":1,"30901":1,"30900":1,"15451":1,"15450":1,"7727":1,"7726":1,"3865":1,"3864":1,"1933":7,"1932":7,"967":17,"966":17,"485":17,"484":17,"243":62,"242":62,"241":87,"240":87,"481":43,"480":43,"239":86,"238":86,"965":22,"964":22,"483":43,"482":43,"1931":10,"1930":10,"963":21,"962":21,"479":25,"478":25,"237":25,"236":25,"3861":5,"3860":5,"1929":11,"1928":11,"7723":3,"7722":3,"3863":6,"3862":6,"3859":4,"3858":4,"1927":4,"1926":4,"961":4,"960":4,"15449":2,"15448":2,"7725":3,"7724":3,"30897":1,"30896":1,"15447":1,"15446":1,"7721":1,"7720":1,"23175":1,"23174":1,"11589":1,"11588":1,"5795":2,"5794":2,"2899":2,"2898":2,"1451":2,"1450":2,"727":2,"726":2,"365":3,"364":3,"183":48,"182":48,"181":87,"180":87,"361":43,"360":43,"179":87,"178":87,"723":21,"722":21,"363":44,"362":44,"359":40,"358":40,"177":40,"176":40,"1447":11,"1446":11,"725":22,"724":22,"721":19,"720":19,"2895":5,"2894":5,"1449":11,"1448":11,"1445":8,"1444":8,"5793":3,"5792":3,"2897":6,"2896":6,"11585":2,"11584":2,"5791":3,"5790":3,"2893":3,"2892":3,"23173":1,"23172":1,"11587":1,"11586":1,"17381":1,"17380":1,"8691":2,"8690":2,"4347":2,"4346":2,"2175":2,"2174":2,"1089":2,"1088":2,"545":12,"544":12,"273":36,"272":36,"137":79,"136":79,"135":89,"134":89,"271":42,"270":42,"133":85,"132":85,"543":22,"542":22,"269":43,"268":43,"1085":11,"1084":11,"541":21,"540":21,"2171":5,"2170":5,"1087":10,"1086":10,"1083":9,"1082":9,"539":9,"538":9,"267":9,"266":9,"131":20,"130":20,"4343":3,"4342":3,"2173":5,"2172":5,"2169":4,"2168":4,"8689":1,"8688":1,"4345":2,"4344":2,"17379":1,"17378":1,"8687":1,"8686":1,"4341":1,"4340":1,"13037":1,"13036":1,"6519":1,"6518":1,"3261":1,"3260":1,"1631":4,"1630":4,"817":4,"816":4,"409":15,"408":15,"205":37,"204":37,"203":44,"202":44,"407":21,"406":21,"201":42,"200":42,"813":10,"812":10,"405":21,"404":21,"1629":5,"1628":5,"815":11,"814":11,"3257":3,"3256":3,"1627":6,"1626":6,"811":7,"810":7,"403":7,"402":7,"199":7,"198":7,"6517":2,"6516":2,"3259":3,"3258":3,"13033":1,"13032":1,"6515":1,"6514":1,"3255":1,"3254":1,"1625":1,"1624":1,"9777":1,"9776":1,"4889":2,"4888":2,"2445":3,"2444":3,"1223":6,"1222":6,"613":6,"612":6,"307":17,"306":17,"155":17,"154":17,"151":44,"150":44,"305":22,"304":22,"153":44,"152":44,"609":11,"608":11,"303":21,"302":21,"149":26,"148":26,"1221":5,"1220":5,"611":10,"610":10,"2443":3,"2442":3,"1219":5,"1218":5,"607":5,"606":5,"301":5,"300":5,"4887":1,"4886":1,"2441":2,"2440":2,"9775":1,"9774":1,"4885":1,"4884":1,"7333":1,"7332":1,"3667":1,"3666":1,"1835":1,"1834":1,"919":1,"918":1,"461":1,"460":1,"231":12,"230":12,"229":22,"228":22,"457":11,"456":11,"227":22,"226":22,"915":5,"914":5,"459":11,"458":11,"455":9,"454":9,"225":9,"224":9,"1831":3,"1830":3,"917":6,"916":6,"913":4,"912":4,"3665":2,"3664":2,"1833":3,"1832":3,"7329":1,"7328":1,"3663":1,"3662":1,"1829":1,"1828":1,"5499":1,"5498":1,"2751":1,"2750":1,"1377":1,"1376":1,"689":4,"688":4,"345":9,"344":9,"173":20,"172":20,"171":22,"170":22,"343":11,"342":11,"169":21,"168":21,"687":5,"686":5,"341":10,"340":10,"1373":2,"1372":2,"685":5,"684":5,"2747":2,"2746":2,"1375":3,"1374":3,"1371":2,"1370":2,"683":2,"682":2,"339":2,"338":2,"167":2,"166":2,"5497":1,"5496":1,"2749":1,"2748":1,"4125":1,"4124":1,"2063":2,"2062":2,"1033":2,"1032":2,"517":4,"516":4,"259":10,"258":10,"127":10,"126":10,"257":10,"256":10,"515":6,"514":6,"255":11,"254":11,"1029":3,"1028":3,"513":5,"512":5,"2061":1,"2060":1,"1031":2,"1030":2,"4123":1,"4122":1,"2059":1,"2058":1,"1027":1,"1026":1,"511":1,"510":1,"253":1,"252":1,"3093":1,"3092":1,"1547":2,"1546":2,"775":2,"774":2,"389":2,"388":2,"195":7,"194":7,"385":5,"384":5,"771":3,"770":3,"387":5,"386":5,"1545":1,"1544":1,"773":2,"772":2,"3091":1,"3090":1,"1543":1,"1542":1,"769":1,"768":1,"2321":1,"2320":1,"1161":1,"1160":1,"581":3,"580":3,"291":5,"290":5,"147":5,"146":5,"579":2,"578":2,"1159":2,"1158":2,"577":3,"576":3,"2317":1,"2316":1,"1157":1,"1156":1,"1741":1,"1740":1,"871":1,"870":1,"437":1,"436":1,"219":4,"218":4,"433":3,"432":3,"869":2,"868":2,"435":3,"434":3,"1737":1,"1736":1,"867":1,"866":1,"1305":1,"1304":1,"653":2,"652":2,"327":3,"326":3,"165":3,"164":3,"325":3,"324":3,"651":1,"650":1,"1303":1,"1302":1,"649":1,"648":1,"979":1,"978":1,"491":1,"490":1,"247":1,"246":1,"487":2,"486":2,"245":3,"244":3,"977":1,"976":1,"489":1,"488":1,"735":1,"734":1,"369":1,"368":1,"185":2,"184":2,"731":1,"730":1,"367":1,"366":1,"551":1,"550":1,"277":1,"276":1,"549":1,"548":1,"275":1,"274":1,"413":1,"412":1,"207":2,"206":2,"411":1,"410":1,"311":1,"310":1,"233":1,"232":1,"175":1,"174":1,"129":1,"128":1},"division_classical":{"192,191":1157,"191,190":1157,"190,189":1508,"189,188":1508,"188,187":1853,"187,186":1853,"186,185":2069,"185,184":2069,"184,183":2071,"183,182":2071,"182,181":2119,"181,180":2119,"180,179":2206,"179,178":2206,"178,177":2293,"177,176":2293,"176,175":2333,"175,174":2333,"174,173":2334,"173,172":2334,"172,171":2354,"171,170":2354,"170,169":2376,"169,168":2376,"168,167":2397,"167,166":2397,"166,165":2399,"165,164":2399,"164,163":2402,"163,162":2402,"162,161":2487,"161,160":2487,"160,159":2663,"159,158":2663,"158,157":2836,"157,156":2836,"156,155":2928,"155,154":2928,"154,153":2945,"153,152":2945,"152,151":2989,"151,150":2989,"150,149":3033,"149,148":3033,"148,147":3059,"147,146":3059,"146,145":3064,"145,144":3064,"144,143":3255,"143,142":3255,"142,141":3607,"141,140":3607,"140,139":3953,"139,138":3953,"138,137":4117,"137,136":4117,"136,135":4196,"135,134":4196,"134,133":4285,"133,132":4285,"132,131":4370,"131,130":4370,"130,129":4390,"129,128":4390,"128,127":4381,"127,126":4370,"126,125":4379,"125,124":4379,"124,123":4379,"123,122":4378,"122,121":4375,"121,120":4313,"120,119":4226,"119,118":4140,"118,117":4115,"117,116":4115,"116,115":4114,"115,114":4102,"114,113":4080,"113,112":4058,"112,111":4049,"111,110":4049,"110,109":4049,"109,108":4045,"108,107":3991,"107,106":3814,"106,105":3642,"105,104":3521,"104,103":3521,"103,102":3519,"102,101":3482,"101,100":3438,"100,99":3396,"99,98":3389,"98,97":3389,"97,96":3382,"286,285":131,"96,95":3245,"95,94":2894,"573,572":40,"285,284":171,"1144,1143":40,"570,569":85,"283,282":172,"94,93":2549,"2289,2288":19,"571,570":86,"1143,1142":43,"4578,4577":8,"2287,2286":21,"1141,1140":43,"568,567":45,"282,281":46,"9156,9155":3,"4576,4575":11,"2286,2285":22,"18310,18309":3,"9153,9152":6,"4575,4574":11,"36621,36620":2,"9154,9153":5,"18309,18308":3,"73242,73241":1,"36619,36618":1,"18307,18306":2,"9151,9150":2,"4573,4572":2,"2284,2283":2,"1140,1139":2,"341796,341795":1,"73240,73239":1,"36618,36617":1,"292968,292967":1,"93,92":2333,"92,91":2331,"91,90":2283,"90,89":2196,"89,88":2109,"88,87":2069,"87,86":2068,"86,85":2048,"85,84":2026,"84,83":2005,"83,82":2003,"82,81":2000,"81,80":1915,"80,79":1739,"79,78":1566,"78,77":1474,"77,76":1457,"76,75":1413,"75,74":1369,"74,73":1343,"73,72":1338,"216,215":426,"72,71":1147,"430,429":9,"213,212":758,"71,70":795,"859,858":9,"214,213":764,"427,426":86,"211,210":922,"70,69":449,"1717,1716":9,"429,428":85,"856,855":42,"426,425":76,"3433,3432":9,"858,857":43,"1714,1713":22,"855,854":34,"6867,6866":4,"1716,1715":21,"3432,3431":11,"13734,13733":1,"6865,6864":5,"3430,3429":10,"1713,1712":12,"27466,27465":1,"13731,13730":2,"6864,6863":5,"54931,54930":1,"13732,13731":3,"27463,27462":2,"13729,13728":2,"6862,6861":2,"3429,3428":2,"256346,256345":1,"27465,27464":1,"54930,54929":1,"219725,219724":1,"215,214":411,"212,211":760,"210,209":881,"209,208":881,"208,207":881,"207,206":882,"206,205":883,"205,204":884,"204,203":956,"203,202":920,"202,201":1006,"201,200":1007,"200,199":1006,"199,198":1015,"198,197":1013,"197,196":1013,"196,195":1013,"195,194":1013,"194,193":1020,"193,192":1030,"322,321":51,"645,644":7,"321,320":87,"1288,1287":7,"642,641":43,"319,318":86,"2575,2574":7,"643,642":42,"1285,1284":21,"640,639":36,"318,317":37,"5151,5150":1,"1287,1286":21,"2574,2573":10,"10300,10299":1,"5148,5147":5,"2572,2571":11,"1284,1283":15,"20599,20598":1,"5149,5148":6,"10297,10296":3,"5146,5145":4,"2571,2570":4,"41199,41198":1,"10299,10298":3,"20598,20597":2,"192258,192257":1,"41196,41195":1,"20596,20595":1,"10296,10295":1,"164793,164792":1,"241,240":171,"483,482":37,"240,239":261,"966,965":16,"481,480":43,"238,237":347,"1932,1931":5,"964,963":21,"480,479":42,"3862,3861":5,"1929,1928":10,"963,962":21,"7725,7724":2,"1930,1929":11,"3861,3860":5,"15450,15449":1,"7723,7722":3,"3859,3858":6,"1927,1926":6,"961,960":6,"478,477":6,"237,236":268,"30898,30897":1,"15447,15446":2,"7722,7721":3,"144193,144192":1,"15448,15447":1,"30897,30896":1,"123594,123593":1,"242,241":89,"239,238":176,"236,235":287,"235,234":287,"234,233":287,"233,232":287,"232,231":289,"231,230":288,"230,229":300,"229,228":317,"228,227":344,"227,226":322,"226,225":365,"225,224":349,"224,223":353,"223,222":353,"222,221":353,"221,220":353,"220,219":353,"219,218":353,"218,217":357,"217,216":362,"363,362":18,"724,723":17,"360,359":44,"1449,1448":7,"361,360":44,"723,722":22,"2898,2897":1,"1447,1446":10,"721,720":21,"358,357":26,"5794,5793":1,"2895,2894":5,"1446,1445":11,"11587,11586":1,"2896,2895":6,"5791,5790":3,"2893,2892":4,"1444,1443":4,"720,719":4,"23175,23174":1,"5793,5792":3,"11586,11585":2,"108143,108142":1,"23172,23171":1,"11584,11583":1,"5790,5789":1,"92694,92693":1,"273,272":4,"544,543":2,"270,269":44,"1087,1086":2,"271,270":45,"541,540":21,"268,267":41,"2173,2172":2,"543,542":22,"1084,1083":11,"540,539":19,"4345,4344":2,"1086,1085":11,"2170,2169":5,"1083,1082":8,"8691,8690":1,"2172,2171":6,"4344,4343":3,"17380,17379":1,"8688,8687":2,"4342,4341":3,"2169,2168":3,"81106,81105":1,"8689,8688":1,"17379,17378":1,"69519,69518":1,"69,68":285,"68,67":206,"408,407":12,"67,66":117,"816,815":2,"406,405":22,"1630,1629":2,"813,812":11,"405,404":21,"3259,3258":2,"814,813":10,"1627,1626":5,"811,810":9,"403,402":9,"66,65":32,"6517,6516":2,"1629,1628":5,"3256,3255":3,"1626,1625":4,"13035,13034":1,"3258,3257":2,"6516,6515":1,"60828,60827":1,"13033,13032":1,"6514,6513":1,"3255,3254":1,"52138,52137":1,"306,305":16,"612,611":4,"304,303":22,"1222,1221":4,"609,608":10,"303,302":22,"2445,2444":1,"610,609":11,"1221,1220":5,"4888,4887":1,"2442,2441":3,"1219,1218":6,"607,606":7,"301,300":8,"9777,9776":1,"2443,2442":3,"4887,4886":2,"45619,45618":1,"9774,9773":1,"4885,4884":1,"2440,2439":1,"1218,1217":1,"39102,39101":1,"459,458":6,"916,915":6,"456,455":11,"1833,1832":3,"457,456":10,"915,914":5,"3666,3665":2,"1831,1830":3,"913,912":5,"454,453":5,"7332,7331":1,"3664,3663":1,"1830,1829":2,"34213,34212":1,"7330,7329":1,"3663,3662":1,"29325,29324":1,"345,344":2,"688,687":1,"342,341":12,"1375,1374":1,"343,342":12,"685,684":5,"340,339":10,"2749,2748":1,"687,686":6,"1372,1371":3,"684,683":4,"5499,5498":1,"1374,1373":3,"2748,2747":2,"25658,25657":1,"5496,5495":1,"2746,2745":1,"1371,1370":1,"21993,21992":1,"258,257":10,"516,515":4,"256,255":22,"1032,1031":1,"514,513":5,"255,254":21,"2062,2061":1,"1029,1028":2,"513,512":5,"4123,4122":1,"1030,1029":3,"2059,2058":2,"1027,1026":2,"511,510":2,"253,252":24,"19243,19242":1,"2061,2060":1,"4122,4121":1,"16494,16493":1,"65,64":12,"64,63":11,"387,386":5,"254,253":22,"252,251":23,"251,250":23,"250,249":23,"249,248":23,"248,247":23,"247,246":23,"246,245":24,"245,244":24,"244,243":30,"243,242":30,"774,773":2,"385,384":7,"1546,1545":2,"771,770":3,"384,383":6,"3093,3092":1,"772,771":2,"1545,1544":1,"14431,14430":1,"3091,3090":1,"1543,1542":1,"769,768":1,"382,381":2,"12369,12368":1,"291,290":3,"580,579":2,"288,287":6,"1159,1158":2,"289,288":6,"577,576":3,"2319,2318":1,"579,578":2,"1158,1157":1,"10822,10821":1,"2317,2316":1,"1156,1155":1,"576,575":1,"9276,9275":1,"435,434":3,"870,869":1,"433,432":2,"1740,1739":1,"868,867":2,"432,431":3,"8115,8114":1,"1737,1736":1,"867,866":1,"6956,6955":1,"327,326":2,"652,651":1,"324,323":4,"1305,1304":1,"325,324":4,"651,650":2,"6085,6084":1,"1302,1301":1,"649,648":1,"5216,5215":1,"489,488":2,"978,977":1,"487,486":1,"4563,4562":1,"976,975":1,"486,485":1,"3911,3910":1,"367,366":2,"733,732":1,"364,363":3,"3421,3420":1,"366,365":2,"732,731":1,"2932,2931":1,"276,275":2,"550,549":1,"2564,2563":1,"274,273":2,"547,546":1,"2198,2197":1,"412,411":1,"1922,1921":1,"411,410":1,"1647,1646":1,"309,308":2,"1440,1439":1,"307,306":2,"1234,1233":1,"1078,1077":1,"924,923":1,"807,806":1,"692,691":1,"604,603":1,"518,517":1,"452,451":1,"386,385":1,"383,382":1,"381,380":1,"380,379":1,"379,378":1,"378,377":1,"377,376":1,"376,375":1,"375,374":1,"374,373":1,"373,372":1,"372,371":1,"371,370":1,"370,369":1,"369,368":1,"368,367":1,"365,364":1,"362,361":1,"359,358":1,"357,356":1,"356,355":1,"355,354":1,"354,353":1,"353,352":1,"352,351":1,"351,350":1,"350,349":1,"349,348":1,"348,347":1,"347,346":1,"346,345":1,"344,343":1,"341,340":1,"339,338":1,"338,337":1,"337,336":1,"336,335":1,"335,334":1,"334,333":1,"333,332":1,"332,331":1,"331,330":1,"330,329":1,"329,328":1,"328,327":1,"326,325":1,"323,322":1,"320,319":1,"317,316":1,"316,315":1,"315,314":1,"314,313":1,"313,312":1,"312,311":1,"311,310":1,"310,309":1,"308,307":1,"305,304":1,"302,301":1,"300,299":1,"299,298":1,"298,297":1,"297,296":1,"296,295":1,"295,294":1,"294,293":1,"293,292":1,"292,291":1,"290,289":1,"287,286":1,"284,283":1,"281,280":1,"280,279":1,"279,278":1,"278,277":1,"277,276":1,"275,274":1,"272,271":1,"269,268":1,"267,266":1,"266,265":1,"265,264":1,"264,263":1,"263,262":1,"262,261":1,"261,260":1,"260,259":1,"259,258":1,"257,256":1,"63,62":1,"62,61":1,"61,60":1,"60,59":1,"59,58":1,"58,57":1,"57,56":1,"56,55":1,"55,54":1,"54,53":1,"53,52":1,"52,51":1,"51,50":1,"50,49":1,"49,48":1,"48,47":1,"47,46":1,"46,45":1,"45,44":1,"44,43":1,"43,42":1,"42,41":1,"41,40":1,"40,39":1,"39,38":1,"38,37":1,"37,36":1,"36,35":1,"35,34":1,"34,33":1,"33,32":1,"32,31":1,"31,30":1,"30,29":1,"29,28":1,"28,27":1,"27,26":1,"26,25":1,"25,24":1,"24,23":1,"23,22":1,"22,21":1,"21,20":1,"20,19":1,"19,18":1,"18,17":1,"17,16":1,"16,15":1,"15,14":1,"14,13":1,"13,12":1,"12,11":1,"11,10":1,"10,9":1,"9,8":1,"8,7":1,"7,6":1,"6,5":1,"5,4":1,"4,3":1,"3,2":1,"2,1":1,"1,0":1},"product_zero":{"2,0":4404},"addsub":{"1":4404,"2":8808,"3":8808,"4":8808,"5":8808,"6":8808,"7":8808,"8":8808,"9":8808,"10":8808,"11":8808,"12":8808,"13":8808,"14":8808,"15":8808,"16":8808,"17":8808,"18":8808,"19":8808,"20":8808,"21":8808,"22":8808,"23":8808,"24":8808,"25":8808,"26":8808,"27":8808,"28":8808,"29":8808,"30":8808,"31":8808,"32":8808,"33":8808,"34":8808,"35":8808,"36":8808,"37":8808,"38":8808,"39":8808,"40":8808,"41":8807,"42":8806,"43":8806,"44":8806,"45":8806,"46":8806,"47":8806,"48":8806,"49":8806,"50":8806,"51":8806,"52":8806,"53":8806,"54":8806,"55":8805,"56":8804,"57":8804,"58":8804,"59":8804,"60":8804,"61":8804,"62":8804,"63":8804,"64":8794,"65":8783,"66":8773,"67":8668,"68":8535,"69":8445,"70":8152,"71":7564,"72":7196,"73":6843,"74":6319,"75":6097,"76":6027,"77":5982,"78":5933,"79":5782,"80":5506,"81":5326,"82":5144,"83":4889,"84":4799,"85":4773,"86":4742,"87":4720,"88":4688,"89":4627,"90":4499,"91":4408,"92":4320,"93":4189,"94":3924,"95":3406,"96":3051,"97":2653,"477":130,"478":130,"98":2174,"190":641,"191":565,"192":401,"954":40,"955":40,"474":170,"475":170,"189":557,"193":144,"381":299,"382":271,"383":184,"1907":40,"1908":40,"949":85,"950":85,"472":171,"473":171,"188":261,"379":197,"380":323,"384":45,"762":179,"763":157,"764":110,"3814":19,"3815":19,"952":86,"953":86,"1904":43,"1905":43,"761":131,"765":46,"1525":88,"1526":72,"1527":57,"7629":8,"7630":8,"3812":21,"3813":21,"1902":43,"1903":43,"947":45,"948":45,"469":45,"470":45,"187":45,"378":66,"760":58,"1524":72,"1528":25,"3051":41,"3052":38,"3053":27,"15259":3,"15260":3,"7627":11,"7628":11,"3809":22,"3810":22,"1523":31,"3050":37,"3054":11,"6103":19,"6104":17,"6105":12,"30517":3,"30518":3,"15254":6,"15255":6,"7624":11,"7625":11,"3049":17,"6101":10,"6102":19,"6106":3,"12206":11,"12207":10,"12208":7,"61034":2,"61035":2,"15257":5,"15258":5,"30514":3,"30515":3,"12205":7,"12209":3,"24413":5,"24414":5,"24415":4,"122069":1,"122070":1,"61032":1,"61033":1,"30512":2,"30513":2,"15252":2,"15253":2,"7622":2,"7623":2,"3807":2,"3808":2,"1899":2,"1900":2,"759":13,"1522":7,"3048":2,"6100":2,"12204":2,"24412":3,"24416":2,"48827":3,"48828":3,"48829":2,"439451":1,"439452":1,"122067":1,"122068":1,"61029":1,"61030":1,"24411":1,"48826":1,"48830":1,"97655":1,"97656":2,"97657":1,"488279":1,"488280":1,"359":35,"360":75,"143":613,"144":458,"145":208,"717":9,"718":9,"354":170,"355":170,"141":494,"142":678,"146":22,"286":299,"287":225,"288":111,"1432":9,"1433":9,"357":176,"358":176,"712":86,"713":86,"352":162,"353":162,"140":163,"284":238,"285":333,"289":19,"572":160,"573":127,"574":62,"2862":9,"2863":9,"714":85,"715":85,"1427":42,"1428":42,"709":76,"710":76,"283":76,"570":121,"571":161,"575":10,"1144":81,"1145":68,"1146":39,"5722":9,"5723":9,"1429":43,"1430":43,"2857":22,"2858":22,"1424":34,"1425":34,"569":45,"1142":51,"1143":82,"1147":10,"2288":44,"2289":39,"2290":28,"11444":4,"11445":4,"2859":21,"2860":21,"5719":11,"5720":11,"2287":36,"2291":9,"4577":20,"4578":18,"4579":14,"22889":1,"22890":1,"11442":5,"11443":5,"5717":10,"5718":10,"2854":12,"2855":12,"1141":12,"2286":14,"4576":17,"4580":6,"9155":9,"9156":8,"9157":5,"45777":1,"45778":1,"22884":2,"22885":2,"11439":5,"11440":5,"4575":9,"9153":6,"9154":9,"9158":1,"18310":5,"18311":4,"18312":3,"91552":1,"91553":1,"22887":3,"22888":3,"45772":2,"45773":2,"22882":2,"22883":2,"11437":2,"11438":2,"5714":2,"5715":2,"2285":3,"4574":2,"9152":2,"18308":2,"18309":5,"18313":1,"36620":3,"36621":3,"36622":2,"329587":1,"329588":1,"45774":1,"45775":1,"91549":1,"91550":1,"36619":1,"36623":1,"73241":1,"73242":2,"73243":1,"366208":1,"366209":1,"99":2031,"100":2017,"101":1968,"102":1910,"103":1865,"104":1800,"105":1762,"106":1639,"107":1382,"108":1204,"109":990,"537":50,"538":50,"110":765,"214":307,"215":268,"216":187,"1074":7,"1075":7,"534":86,"535":86,"213":292,"217":59,"429":158,"430":122,"431":56,"2147":7,"2148":7,"1069":43,"1070":43,"532":85,"533":85,"212":157,"427":126,"428":175,"432":8,"858":79,"859":64,"860":39,"4292":7,"4293":7,"1072":42,"1073":42,"2142":21,"2143":21,"1067":36,"1068":36,"529":36,"530":36,"211":36,"426":36,"856":51,"857":83,"861":7,"1716":38,"1717":36,"1718":26,"8584":1,"8585":1,"2144":21,"2145":21,"4289":10,"4290":10,"1715":38,"1719":8,"3433":21,"3434":16,"3435":9,"17167":1,"17168":1,"8579":5,"8580":5,"4287":11,"4288":11,"2139":15,"2140":15,"855":20,"1714":21,"3431":13,"3432":22,"3436":1,"6866":10,"6867":8,"6868":5,"34332":1,"34333":1,"8582":6,"8583":6,"17162":3,"17163":3,"8577":4,"8578":4,"4284":4,"4285":4,"1713":6,"3430":4,"6864":5,"6865":10,"6869":2,"13732":6,"13733":5,"13734":3,"68664":1,"68665":1,"17164":3,"17165":3,"34329":2,"34330":2,"13731":4,"13735":1,"27465":2,"27466":2,"27467":2,"247189":1,"247190":1,"68659":1,"68660":1,"34327":1,"34328":1,"17159":1,"17160":1,"6863":1,"13730":1,"27463":1,"27464":2,"27468":1,"54930":1,"54931":2,"54932":1,"274654":1,"274655":1,"402":82,"403":82,"160":337,"161":300,"162":219,"804":37,"805":37,"399":85,"400":85,"159":261,"163":90,"321":165,"322":154,"323":112,"1609":16,"1610":16,"802":43,"803":43,"397":85,"398":85,"158":97,"320":133,"324":40,"643":85,"644":73,"645":52,"3219":5,"3220":5,"1607":21,"1608":21,"799":42,"800":42,"319":54,"642":75,"646":17,"1287":39,"1288":34,"1289":23,"6437":5,"6438":5,"3214":10,"3215":10,"1604":21,"1605":21,"641":33,"1285":25,"1286":37,"1290":7,"2574":22,"2575":19,"2576":13,"12874":2,"12875":2,"3217":11,"3218":11,"6434":5,"6435":5,"2573":18,"2577":7,"5149":11,"5150":9,"5151":6,"25749":1,"25750":1,"12872":3,"12873":3,"6432":6,"6433":6,"3212":6,"3213":6,"1602":6,"1603":6,"797":6,"798":6,"394":6,"395":6,"157":7,"318":6,"640":11,"1284":9,"2572":7,"5148":9,"5152":3,"10299":5,"10300":4,"10301":3,"51497":1,"51498":1,"25744":2,"25745":2,"12869":3,"12870":3,"5147":3,"10297":2,"10298":5,"10302":1,"20598":3,"20599":3,"20600":2,"185390":1,"185391":1,"25747":1,"25748":1,"51494":1,"51495":1,"20597":1,"20601":1,"41197":1,"41198":2,"41199":1,"205989":1,"205990":1,"111":708,"112":704,"113":695,"114":664,"115":640,"116":618,"117":586,"118":573,"119":547,"120":436,"121":331,"122":242,"604":17,"605":17,"123":112,"241":150,"242":126,"243":82,"1207":17,"1208":17,"599":43,"600":43,"239":93,"240":154,"244":22,"482":88,"483":77,"484":51,"2414":7,"2415":7,"602":43,"603":43,"1204":22,"1205":22,"481":68,"485":19,"965":40,"966":33,"967":25,"4829":1,"4830":1,"2412":10,"2413":10,"1202":21,"1203":21,"597":25,"598":25,"238":25,"480":34,"964":38,"968":9,"1931":19,"1932":17,"1933":10,"9657":1,"9658":1,"4824":5,"4825":5,"2409":11,"2410":11,"963":22,"1929":14,"1930":21,"1934":1,"3862":11,"3863":9,"3864":6,"19312":1,"19313":1,"4827":6,"4828":6,"9652":3,"9653":3,"4822":4,"4823":4,"2407":4,"2408":4,"1199":4,"1200":4,"479":9,"962":7,"1928":5,"3860":5,"3861":10,"3865":2,"7724":6,"7725":5,"7726":3,"38624":1,"38625":1,"9654":3,"9655":3,"19309":2,"19310":2,"7723":4,"7727":1,"15449":2,"15450":2,"15451":2,"139042":1,"139043":1,"38619":1,"38620":1,"19307":1,"19308":1,"9649":1,"9650":1,"3859":1,"7722":1,"15447":1,"15448":2,"15452":1,"30898":1,"30899":2,"30900":1,"154491":1,"154492":1,"454":3,"455":7,"181":153,"182":113,"183":51,"907":2,"908":2,"449":43,"450":43,"179":123,"180":170,"184":6,"362":80,"363":61,"364":27,"1812":2,"1813":2,"452":44,"453":44,"902":21,"903":21,"447":40,"448":40,"178":40,"361":83,"365":4,"724":41,"725":32,"726":15,"3622":2,"3623":2,"904":22,"905":22,"1807":11,"1808":11,"899":19,"900":19,"722":29,"723":43,"727":2,"1448":21,"1449":17,"1450":11,"7242":2,"7243":2,"1809":11,"1810":11,"3617":5,"3618":5,"1804":8,"1805":8,"721":8,"1446":11,"1447":21,"1451":2,"2896":11,"2897":9,"2898":6,"14484":1,"14485":1,"3619":6,"3620":6,"7239":3,"7240":3,"2895":10,"2899":3,"5793":5,"5794":4,"5795":3,"28967":1,"28968":1,"14479":2,"14480":2,"7237":3,"7238":3,"3614":3,"3615":3,"1445":4,"2894":4,"5791":2,"5792":5,"5796":1,"11586":3,"11587":3,"11588":2,"104279":1,"104280":1,"14482":1,"14483":1,"28964":1,"28965":1,"11585":1,"11589":1,"23173":1,"23174":2,"23175":1,"115866":1,"115867":1,"339":36,"340":38,"135":163,"136":145,"137":103,"679":12,"680":12,"337":42,"338":42,"134":137,"138":38,"271":77,"272":66,"273":45,"1359":2,"1360":2,"677":22,"678":22,"334":43,"335":43,"133":61,"270":73,"274":15,"543":40,"544":29,"545":15,"2717":2,"2718":2,"1354":11,"1355":11,"674":21,"675":21,"269":40,"541":29,"542":44,"546":2,"1086":18,"1087":16,"1088":10,"5432":2,"5433":2,"1357":10,"1358":10,"2712":5,"2713":5,"1352":9,"1353":9,"672":9,"673":9,"332":9,"333":9,"132":9,"268":10,"540":12,"1084":15,"1085":21,"1089":2,"2172":9,"2173":8,"2174":7,"10862":2,"10863":2,"2714":5,"2715":5,"5427":3,"5428":3,"2709":4,"2710":4,"1083":5,"2170":6,"2171":9,"2175":3,"4344":5,"4345":5,"4346":4,"21724":1,"21725":1,"5429":2,"5430":2,"10859":1,"10860":1,"4343":3,"4347":2,"8689":3,"8690":3,"8691":2,"78207":1,"78208":1,"21722":1,"21723":1,"10857":1,"10858":1,"5424":1,"5425":1,"2169":2,"4342":1,"8688":1,"8692":1,"17379":1,"17380":2,"17381":1,"86897":1,"86898":1,"509":15,"510":15,"203":78,"204":69,"205":50,"1019":4,"1020":4,"507":21,"508":21,"202":70,"206":18,"407":40,"408":34,"409":19,"2037":4,"2038":4,"1014":10,"1015":10,"504":21,"505":21,"201":35,"405":27,"406":38,"410":4,"814":22,"815":19,"816":12,"4074":1,"4075":1,"1017":11,"1018":11,"2034":5,"2035":5,"813":19,"817":4,"1629":11,"1630":9,"1631":5,"8147":1,"8148":1,"4069":3,"4070":3,"2032":6,"2033":6,"1012":7,"1013":7,"502":7,"503":7,"200":8,"404":10,"812":9,"1627":6,"1628":11,"1632":1,"3258":6,"3259":5,"3260":3,"16294":1,"16295":1,"4072":3,"4073":3,"8144":2,"8145":2,"3257":4,"3261":1,"6517":2,"6518":3,"6519":3,"58654":1,"58655":1,"16289":1,"16290":1,"8142":1,"8143":1,"4067":1,"4068":1,"2029":1,"2030":1,"811":1,"1626":1,"3256":1,"6515":1,"6516":2,"6520":1,"13034":1,"13035":2,"13036":1,"65171":1,"65172":1,"152":82,"153":72,"154":50,"151":69,"155":18,"305":37,"306":32,"307":22,"377":21,"150":31,"303":21,"304":37,"308":7,"610":22,"611":19,"612":15,"3055":3,"609":16,"613":7,"1221":11,"1222":11,"1223":8,"6109":2,"6110":2,"757":5,"758":5,"374":5,"375":5,"149":5,"302":5,"608":7,"1220":8,"1224":3,"2443":5,"2444":5,"2445":4,"12219":1,"12220":1,"6107":1,"6108":1,"1219":3,"2442":3,"2446":2,"4887":4,"4888":4,"4889":2,"43988":1,"43989":1,"12217":1,"12218":1,"2441":1,"4886":1,"4890":1,"9775":1,"9776":2,"9777":1,"48876":1,"48877":1,"229":38,"230":29,"231":15,"1148":1,"227":29,"228":42,"232":2,"458":20,"459":16,"460":9,"2292":1,"2293":1,"567":9,"568":9,"226":9,"456":13,"457":21,"461":1,"916":10,"917":9,"918":6,"4582":1,"4583":1,"1139":4,"1140":4,"914":5,"915":10,"919":1,"1832":6,"1833":5,"1834":3,"9164":1,"9165":1,"1831":4,"1835":1,"3665":2,"3666":2,"3667":2,"32989":1,"32990":1,"9159":1,"9160":1,"2284":1,"913":2,"1830":1,"3663":2,"3664":3,"3668":1,"7330":1,"7331":2,"7332":1,"36654":1,"36655":1,"171":41,"172":37,"173":27,"170":33,"174":10,"343":20,"344":18,"345":13,"1720":1,"424":10,"425":10,"169":14,"342":18,"346":4,"687":10,"688":9,"689":5,"3437":1,"3438":1,"854":5,"341":9,"685":7,"686":9,"690":1,"1374":5,"1375":4,"1376":3,"6872":1,"6873":1,"1712":2,"852":2,"853":2,"422":2,"423":2,"168":2,"684":3,"1372":2,"1373":5,"1377":1,"2748":3,"2749":3,"2750":2,"24740":1,"24741":1,"6870":1,"2747":2,"2751":1,"5497":1,"5498":2,"5499":1,"27489":1,"27490":1,"128":41,"129":37,"130":28,"124":49,"125":45,"126":44,"127":43,"131":11,"257":21,"258":18,"259":12,"256":17,"260":4,"515":10,"516":8,"517":6,"2578":2,"639":5,"255":7,"513":6,"514":10,"518":2,"1030":5,"1031":5,"1032":4,"5154":1,"5155":1,"1029":3,"1033":2,"2061":3,"2062":3,"2063":2,"18554":1,"18555":1,"5153":1,"1282":1,"1283":1,"637":1,"638":1,"254":1,"512":2,"1028":1,"2060":1,"2064":1,"4123":1,"4124":2,"4125":1,"20616":1,"20617":1,"194":15,"195":9,"196":2,"386":9,"387":9,"388":7,"385":9,"389":2,"772":5,"773":5,"774":4,"771":3,"775":2,"1545":3,"1546":3,"1547":2,"13913":1,"13914":1,"1927":1,"959":1,"960":1,"770":1,"1544":1,"1548":1,"3091":1,"3092":2,"3093":1,"15459":1,"15460":1,"147":5,"290":9,"291":7,"292":3,"579":6,"580":5,"581":4,"2900":1,"719":3,"720":3,"578":4,"582":2,"1159":2,"1160":2,"1161":2,"10434":1,"10435":1,"1444":1,"577":1,"1157":1,"1158":2,"1162":1,"2318":1,"2319":2,"2320":1,"11593":1,"11594":1,"218":8,"219":5,"539":3,"220":1,"434":6,"435":5,"436":3,"433":4,"437":1,"869":2,"870":2,"871":2,"7824":1,"7825":1,"1082":1,"867":1,"868":2,"872":1,"1738":1,"1739":2,"1740":1,"8693":1,"8694":1,"164":7,"165":3,"325":5,"326":5,"327":4,"328":2,"651":3,"652":3,"653":2,"5866":1,"5867":1,"809":1,"810":1,"650":1,"654":1,"1303":1,"1304":2,"1305":1,"245":4,"246":3,"607":2,"247":1,"488":3,"489":3,"490":2,"4398":1,"4399":1,"487":1,"491":1,"977":1,"978":2,"979":1,"185":3,"186":1,"366":2,"367":2,"368":2,"3297":1,"3298":1,"912":1,"369":1,"732":1,"733":2,"734":1,"139":3,"275":3,"276":2,"2471":1,"2472":1,"277":1,"549":1,"550":2,"551":1,"2746":1,"207":2,"1851":1,"1852":1,"208":1,"411":1,"412":2,"413":1,"2057":1,"2058":1,"156":2,"1387":1,"1388":1,"309":2,"310":1,"1541":1,"1542":1,"1038":1,"1039":1,"1153":1,"1154":1,"777":1,"778":1,"863":1,"864":1,"647":1,"199":1},"product_classical":{"2,1":8808,"2,2":8808,"2,3":8808,"2,4":8808,"2,5":8808,"2,6":8808,"2,7":8808,"2,8":8808,"2,9":8808,"2,10":8808,"2,11":8808,"2,12":8808,"2,13":8808,"2,14":8808,"2,15":8808,"2,16":8808,"2,17":8808,"2,18":8808,"2,19":8808,"2,20":8808,"2,21":8808,"2,22":8808,"2,23":8808,"2,24":8808,"2,25":8808,"2,26":8808,"2,27":8808,"2,28":8808,"2,29":8808,"2,30":8808,"2,31":8808,"2,32":8808,"2,33":8808,"2,34":8808,"2,35":8808,"2,36":8808,"2,37":8808,"2,38":8808,"2,39":8808,"2,40":8807,"2,41":8806,"2,42":8806,"2,43":8806,"2,44":8806,"2,45":8806,"2,46":8806,"2,47":8806,"2,48":8806,"2,49":8806,"2,50":8806,"2,51":8806,"2,52":8806,"2,53":8806,"2,54":8805,"2,55":8804,"2,56":8804,"2,57":8804,"2,58":8804,"2,59":8804,"2,60":8804,"2,61":8804,"2,62":8804,"2,63":8794,"2,64":8783,"2,65":8773,"2,66":8668,"2,67":8535,"2,68":8445,"2,69":8152,"2,70":7564,"2,71":7196,"2,72":6843,"2,73":6319,"2,74":6097,"2,75":6027,"2,76":5982,"2,77":5933,"2,78":5782,"2,79":5506,"2,80":5326,"2,81":5144,"2,82":4889,"2,83":4799,"2,84":4773,"2,85":4742,"2,86":4720,"2,87":4688,"2,88":4627,"2,89":4499,"2,90":4408,"2,91":4320,"2,92":4189,"2,93":3924,"2,94":3406,"2,95":3051,"2,96":2653,"2,97":2174,"2,191":256,"2,192":127,"2,190":130,"2,382":126,"2,383":40,"2,381":88,"2,763":64,"2,764":40,"2,1526":32,"2,1527":19,"2,762":24,"2,3052":16,"2,3053":8,"2,1525":13,"2,3051":8,"2,6104":8,"2,6105":3,"2,6103":5,"2,12207":4,"2,12208":3,"2,380":2,"2,24414":2,"2,24415":2,"2,12206":1,"2,48828":1,"2,48829":1,"2,144":183,"2,145":17,"2,143":247,"2,287":94,"2,288":9,"2,142":76,"2,286":119,"2,573":52,"2,574":9,"2,285":34,"2,572":55,"2,1145":30,"2,1146":9,"2,1144":23,"2,2289":16,"2,2290":9,"2,571":12,"2,4578":8,"2,4579":4,"2,2288":7,"2,4577":4,"2,9156":4,"2,9157":1,"2,1143":2,"2,9155":3,"2,18311":2,"2,18312":1,"2,18310":1,"2,36621":1,"2,36622":1,"2,98":2031,"2,99":2017,"2,100":1968,"2,101":1910,"2,102":1865,"2,103":1800,"2,104":1762,"2,105":1639,"2,106":1382,"2,107":1204,"2,108":990,"2,109":765,"2,215":128,"2,216":49,"2,214":79,"2,430":49,"2,431":7,"2,429":57,"2,859":28,"2,860":7,"2,858":25,"2,1717":16,"2,1718":7,"2,428":15,"2,1716":9,"2,3434":7,"2,3435":1,"2,857":4,"2,3433":7,"2,6867":4,"2,6868":1,"2,6866":3,"2,13733":2,"2,13734":1,"2,3432":1,"2,13732":1,"2,27466":1,"2,27467":1,"2,161":128,"2,162":81,"2,322":64,"2,323":37,"2,160":48,"2,644":32,"2,645":16,"2,321":27,"2,643":16,"2,1288":16,"2,1289":5,"2,1287":11,"2,2575":8,"2,2576":5,"2,5150":4,"2,5151":2,"2,2574":3,"2,5149":2,"2,10300":2,"2,10301":1,"2,10299":1,"2,20599":1,"2,20600":1,"2,110":708,"2,111":704,"2,112":695,"2,113":664,"2,114":640,"2,115":618,"2,116":586,"2,117":573,"2,118":547,"2,119":436,"2,120":331,"2,121":242,"2,122":112,"2,242":60,"2,243":17,"2,241":47,"2,483":32,"2,484":17,"2,966":16,"2,967":7,"2,482":15,"2,965":9,"2,1932":7,"2,1933":1,"2,240":4,"2,1931":7,"2,3863":4,"2,3864":1,"2,3862":3,"2,7725":2,"2,7726":1,"2,1930":1,"2,7724":1,"2,15450":1,"2,15451":1,"2,182":45,"2,183":3,"2,181":62,"2,363":24,"2,364":2,"2,180":19,"2,362":30,"2,725":13,"2,726":2,"2,361":8,"2,724":14,"2,1449":8,"2,1450":2,"2,1448":6,"2,2897":4,"2,2898":2,"2,723":3,"2,2896":2,"2,5794":2,"2,5795":1,"2,5793":1,"2,11587":1,"2,11588":1,"2,136":64,"2,137":35,"2,272":32,"2,273":12,"2,135":30,"2,271":20,"2,544":12,"2,545":2,"2,543":14,"2,1087":7,"2,1088":2,"2,542":4,"2,1086":6,"2,2173":4,"2,2174":2,"2,2172":2,"2,4345":2,"2,4346":2,"2,1085":1,"2,8690":1,"2,8691":1,"2,204":32,"2,205":15,"2,203":17,"2,408":15,"2,409":4,"2,407":12,"2,815":8,"2,816":4,"2,814":4,"2,1630":4,"2,1631":1,"2,1629":3,"2,3259":2,"2,3260":1,"2,406":1,"2,3258":1,"2,6518":1,"2,6519":1,"2,153":32,"2,154":16,"2,152":16,"2,306":16,"2,307":6,"2,305":10,"2,611":8,"2,612":6,"2,1222":4,"2,1223":3,"2,610":2,"2,2444":2,"2,2445":2,"2,1221":1,"2,4888":1,"2,4889":1,"2,230":12,"2,231":1,"2,229":15,"2,459":7,"2,460":1,"2,228":4,"2,458":7,"2,917":4,"2,918":1,"2,916":3,"2,1833":2,"2,1834":1,"2,457":1,"2,1832":1,"2,3666":1,"2,3667":1,"2,172":16,"2,173":9,"2,344":8,"2,345":4,"2,171":7,"2,343":4,"2,688":4,"2,689":1,"2,687":3,"2,1375":2,"2,1376":1,"2,1374":1,"2,2749":1,"2,2750":1,"2,123":49,"2,124":45,"2,125":44,"2,126":43,"2,127":31,"2,128":16,"2,129":16,"2,130":10,"2,258":8,"2,259":4,"2,257":4,"2,516":4,"2,517":2,"2,515":2,"2,1031":2,"2,1032":2,"2,2062":1,"2,2063":1,"2,194":7,"2,195":2,"2,193":6,"2,387":4,"2,388":2,"2,386":2,"2,773":2,"2,774":2,"2,1546":1,"2,1547":1,"2,146":5,"2,290":4,"2,291":3,"2,580":2,"2,581":1,"2,289":1,"2,579":1,"2,1160":1,"2,1161":1,"2,218":4,"2,219":1,"2,217":3,"2,435":2,"2,436":1,"2,434":1,"2,870":1,"2,871":1,"2,163":4,"2,164":3,"2,326":2,"2,327":2,"2,652":1,"2,653":1,"2,245":2,"2,246":1,"2,244":1,"2,489":1,"2,490":1,"2,184":2,"2,185":1,"2,367":1,"2,368":1,"2,138":2,"2,139":1,"2,275":1,"2,276":1,"2,206":1,"2,207":1,"2,155":1,"2,156":1,"39,161":1,"40,160":1,"40,161":1,"41,160":1},"product_ntt":{"95,383":130,"96,382":130,"96,383":130,"97,382":130,"93,96":687,"94,97":611,"93,97":301,"94,98":135,"94,96":691,"95,97":317,"95,98":147,"190,765":40,"191,764":40,"191,765":40,"192,764":40,"94,381":170,"95,380":170,"95,381":170,"96,380":170,"93,95":431,"94,95":215,"95,96":175,"189,191":341,"190,192":252,"189,192":342,"190,193":130,"190,191":125,"191,192":41,"191,193":47,"381,1527":40,"382,1526":40,"382,1527":40,"383,1526":40,"189,761":85,"190,760":85,"190,761":85,"191,760":85,"94,379":171,"95,378":171,"95,379":171,"96,378":171,"92,95":216,"92,96":171,"188,190":130,"188,191":261,"189,190":85,"379,382":171,"380,383":166,"379,383":83,"380,384":40,"380,382":171,"381,383":83,"381,384":40,"762,3053":19,"763,3052":19,"763,3053":19,"764,3052":19,"190,763":86,"191,762":86,"191,763":86,"192,762":86,"188,192":131,"189,193":86,"380,1525":43,"381,1524":43,"381,1525":43,"382,1524":43,"379,381":90,"380,381":45,"381,382":43,"761,763":86,"762,764":81,"761,764":85,"762,765":40,"762,763":41,"763,764":19,"763,765":19,"1525,6105":8,"1526,6104":8,"1526,6105":8,"1527,6104":8,"762,3051":21,"763,3050":21,"763,3051":21,"764,3050":21,"380,1523":43,"381,1522":43,"381,1523":43,"382,1522":43,"189,759":45,"190,758":45,"190,759":45,"191,758":45,"93,377":45,"94,376":45,"94,377":45,"95,376":45,"92,94":46,"93,94":45,"187,190":45,"187,191":45,"378,381":45,"378,382":43,"760,763":47,"760,764":23,"761,765":21,"1524,1526":43,"1525,1527":38,"1524,1527":43,"1525,1528":19,"1525,1526":19,"1526,1527":8,"1526,1528":8,"3051,12209":3,"3052,12208":3,"3052,12209":3,"3053,12208":3,"1525,6103":11,"1526,6102":11,"1526,6103":11,"1527,6102":11,"761,3049":22,"762,3048":22,"762,3049":22,"763,3048":22,"760,762":24,"761,762":22,"1523,1526":26,"1523,1527":13,"1524,1528":11,"3050,3052":22,"3051,3053":17,"3050,3053":21,"3051,3054":8,"3051,3052":9,"3052,3053":3,"3052,3054":3,"6103,24415":3,"6104,24414":3,"6104,24415":3,"6105,24414":3,"3050,12205":6,"3051,12204":6,"3051,12205":6,"3052,12204":6,"1524,6101":11,"1525,6100":11,"1525,6101":11,"1526,6100":11,"1523,1525":13,"1524,1525":11,"3049,3051":8,"3049,3052":15,"3050,3051":6,"6101,6104":10,"6102,6105":11,"6101,6105":5,"6102,6106":3,"6102,6104":11,"6103,6105":6,"6103,6106":3,"12206,48829":2,"12207,48828":2,"12207,48829":2,"12208,48828":2,"3051,12207":5,"3052,12206":5,"3052,12207":5,"3053,12206":5,"3049,3053":7,"3050,3054":5,"6102,24413":3,"6103,24412":3,"6103,24413":3,"6104,24412":3,"6101,6103":5,"6102,6103":3,"6103,6104":3,"12205,12207":5,"12206,12208":6,"12205,12208":5,"12206,12209":3,"12206,12207":3,"12207,12208":2,"12207,12209":2,"24413,97657":1,"24414,97656":1,"24414,97657":1,"24415,97656":1,"12206,48827":1,"12207,48826":1,"12207,48827":1,"12208,48826":1,"6102,24411":2,"6103,24410":2,"6103,24411":2,"6104,24410":2,"3050,12203":2,"3051,12202":2,"3051,12203":2,"3052,12202":2,"1524,6099":2,"1525,6098":2,"1525,6099":2,"1526,6098":2,"761,3047":2,"762,3046":2,"762,3047":2,"763,3046":2,"379,1521":2,"380,1520":2,"380,1521":2,"381,1520":2,"378,380":2,"379,380":2,"759,762":2,"759,763":2,"1522,1525":2,"1522,1526":2,"3048,3051":2,"3048,3052":2,"6100,6103":2,"6100,6104":2,"12204,12207":2,"12204,12208":1,"12205,12209":1,"24412,24414":2,"24413,24415":3,"24412,24415":3,"24413,24416":2,"24413,24414":1,"24414,24415":1,"24414,24416":1,"48827,390625":1,"48828,390624":1,"48828,390625":1,"48829,390624":1,"24413,97655":1,"24414,97654":1,"24414,97655":1,"24415,97654":1,"12205,48825":1,"12206,48824":1,"12206,48825":1,"12207,48824":1,"12204,12206":1,"12205,12206":1,"24411,24414":1,"24411,24415":1,"24412,24416":1,"48826,48828":1,"48827,48829":2,"48826,48829":1,"48827,48830":1,"48827,48828":1,"48828,48829":1,"48828,48830":1,"97655,390625":1,"97656,390624":1,"97656,390625":1,"97657,390624":1,"71,289":16,"72,288":16,"72,289":16,"73,288":16,"70,72":693,"71,73":381,"70,73":704,"71,74":201,"71,72":185,"72,73":15,"72,74":20,"143,575":9,"144,574":9,"144,575":9,"145,574":9,"70,285":170,"71,284":170,"71,285":170,"72,284":170,"69,71":333,"69,72":670,"70,71":170,"141,144":342,"142,145":194,"141,145":95,"142,146":11,"142,144":344,"143,145":105,"143,146":19,"286,1147":9,"287,1146":9,"287,1147":9,"288,1146":9,"71,287":176,"72,286":176,"72,287":176,"73,286":176,"69,73":338,"70,74":181,"142,571":86,"143,570":86,"143,571":86,"144,570":86,"70,283":162,"71,282":162,"71,283":162,"72,282":162,"68,71":164,"68,72":162,"140,143":162,"140,144":86,"141,143":323,"284,287":170,"285,288":103,"284,288":51,"285,289":9,"285,287":171,"286,288":52,"286,289":9,"572,2291":9,"573,2290":9,"573,2291":9,"574,2290":9,"142,573":85,"143,572":85,"143,573":85,"144,572":85,"142,143":161,"143,144":88,"285,1143":42,"286,1142":42,"286,1143":42,"287,1142":42,"141,569":76,"142,568":76,"142,569":76,"143,568":76,"140,142":76,"141,142":76,"283,286":76,"283,287":42,"284,286":153,"570,573":86,"571,574":61,"570,574":31,"571,575":9,"571,573":85,"572,574":30,"572,575":9,"1144,4579":9,"1145,4578":9,"1145,4579":9,"1146,4578":9,"285,1145":43,"286,1144":43,"286,1145":43,"287,1144":43,"285,286":77,"286,287":43,"571,2287":22,"572,2286":22,"572,2287":22,"573,2286":22,"284,1141":34,"285,1140":34,"285,1141":34,"286,1140":34,"283,285":34,"284,285":34,"569,572":34,"569,573":22,"570,572":67,"1142,1145":42,"1143,1146":39,"1142,1146":19,"1143,1147":9,"1143,1145":43,"1144,1146":20,"1144,1147":9,"2288,9157":4,"2289,9156":4,"2289,9157":4,"2290,9156":4,"571,2289":21,"572,2288":21,"572,2289":21,"573,2288":21,"571,572":33,"572,573":21,"1143,4577":11,"1144,4576":11,"1144,4577":11,"1145,4576":11,"1142,1144":25,"1143,1144":13,"1144,1145":11,"2287,2289":21,"2288,2290":18,"2287,2290":21,"2288,2291":9,"2288,2289":9,"2289,2290":4,"2289,2291":4,"4577,18313":1,"4578,18312":1,"4578,18313":1,"4579,18312":1,"2288,9155":5,"2289,9154":5,"2289,9155":5,"2290,9154":5,"1143,4575":10,"1144,4574":10,"1144,4575":10,"1145,4574":10,"570,2285":12,"571,2284":12,"571,2285":12,"572,2284":12,"569,571":12,"570,571":12,"1141,1144":12,"1141,1145":10,"2286,2289":14,"2286,2290":7,"2287,2291":5,"4576,4578":10,"4577,4579":7,"4576,4579":11,"4577,4580":4,"4577,4578":3,"4578,4579":1,"4578,4580":1,"9155,36623":1,"9156,36622":1,"9156,36623":1,"9157,36622":1,"4576,18309":2,"4577,18308":2,"4577,18309":2,"4578,18308":2,"2287,9153":5,"2288,9152":5,"2288,9153":5,"2289,9152":5,"2286,2288":7,"2287,2288":5,"4575,4577":4,"4575,4578":9,"4576,4577":2,"9153,9156":6,"9154,9157":5,"9153,9157":3,"9154,9158":1,"9154,9156":5,"9155,9157":2,"9155,9158":1,"18310,73243":1,"18311,73242":1,"18311,73243":1,"18312,73242":1,"4577,18311":3,"4578,18310":3,"4578,18311":3,"4579,18310":3,"4575,4579":5,"4576,4580":3,"9154,36619":2,"9155,36618":2,"9155,36619":2,"9156,36618":2,"4576,18307":2,"4577,18306":2,"4577,18307":2,"4578,18306":2,"2287,9151":2,"2288,9150":2,"2288,9151":2,"2289,9150":2,"1142,4573":2,"1143,4572":2,"1143,4573":2,"1144,4572":2,"1141,1143":2,"1142,1143":2,"2285,2288":2,"2285,2289":2,"4574,4577":2,"4574,4578":2,"9152,9155":2,"9152,9156":2,"9153,9155":3,"18308,18311":2,"18309,18312":3,"18308,18312":1,"18309,18313":1,"18309,18311":3,"18310,18312":2,"18310,18313":1,"36620,292968":1,"36621,292967":1,"36621,292968":1,"36622,292967":1,"9154,36621":1,"9155,36620":1,"9155,36621":1,"9156,36620":1,"9154,9155":1,"9155,9156":1,"18309,73241":1,"18310,73240":1,"18310,73241":1,"18311,73240":1,"18308,18310":1,"18309,18310":1,"18310,18311":1,"36619,36621":1,"36620,36622":2,"36619,36622":1,"36620,36623":1,"36620,36621":1,"36621,36622":1,"36621,36623":1,"73241,292968":1,"73242,292967":1,"73242,292968":1,"73243,292967":1,"107,431":50,"108,430":50,"108,431":50,"109,430":50,"105,108":342,"106,109":277,"105,109":135,"106,110":53,"106,108":346,"107,109":146,"107,110":60,"214,861":7,"215,860":7,"215,861":7,"216,860":7,"106,429":86,"107,428":86,"107,429":86,"108,428":86,"105,107":243,"106,107":122,"107,108":89,"213,215":171,"214,216":99,"213,216":170,"214,217":50,"214,215":50,"215,216":7,"215,217":10,"429,1719":7,"430,1718":7,"430,1719":7,"431,1718":7,"213,857":43,"214,856":43,"214,857":43,"215,856":43,"106,427":85,"107,426":85,"107,427":85,"108,426":85,"104,107":121,"104,108":85,"212,214":79,"212,215":157,"213,214":43,"427,430":85,"428,431":56,"427,431":28,"428,432":7,"428,430":85,"429,431":28,"429,432":7,"858,3435":7,"859,3434":7,"859,3435":7,"860,3434":7,"214,859":42,"215,858":42,"215,859":42,"216,858":42,"212,216":78,"213,217":42,"428,1715":21,"429,1714":21,"429,1715":21,"430,1714":21,"213,855":36,"214,854":36,"214,855":36,"215,854":36,"105,425":36,"106,424":36,"106,425":36,"107,424":36,"104,106":36,"105,106":36,"211,214":36,"211,215":36,"426,429":36,"426,430":21,"427,429":72,"856,859":43,"857,860":35,"856,860":18,"857,861":7,"857,859":42,"858,860":17,"858,861":7,"1716,6869":1,"1717,6868":1,"1717,6869":1,"1718,6868":1,"428,1717":21,"429,1716":21,"429,1717":21,"430,1716":21,"428,429":36,"429,430":21,"857,3433":10,"858,3432":10,"858,3433":10,"859,3432":10,"856,858":29,"857,858":14,"858,859":10,"1715,1717":21,"1716,1718":13,"1715,1718":22,"1716,1719":7,"1716,1717":6,"1717,1718":1,"1717,1719":1,"3433,13735":1,"3434,13734":1,"3434,13735":1,"3435,13734":1,"1715,6865":5,"1716,6864":5,"1716,6865":5,"1717,6864":5,"857,3431":11,"858,3430":11,"858,3431":11,"859,3430":11,"427,1713":15,"428,1712":15,"428,1713":15,"429,1712":15,"426,428":15,"427,428":15,"855,858":15,"855,859":11,"1714,1716":9,"1714,1717":19,"1715,1716":5,"3431,3434":11,"3432,3435":8,"3431,3435":4,"3432,3436":1,"3432,3434":11,"3433,3435":4,"3433,3436":1,"6866,27467":1,"6867,27466":1,"6867,27467":1,"6868,27466":1,"1716,6867":6,"1717,6866":6,"1717,6867":6,"1718,6866":6,"1714,1718":10,"1715,1719":6,"3432,13731":3,"3433,13730":3,"3433,13731":3,"3434,13730":3,"1715,6863":4,"1716,6862":4,"1716,6863":4,"1717,6862":4,"856,3429":4,"857,3428":4,"857,3429":4,"858,3428":4,"855,857":4,"856,857":4,"1713,1716":4,"1713,1717":4,"3430,3433":4,"3430,3434":3,"3431,3433":8,"6864,6867":5,"6865,6868":5,"6864,6868":2,"6865,6869":1,"6865,6867":6,"6866,6868":3,"6866,6869":1,"13732,54933":1,"13733,54932":1,"13733,54933":1,"13734,54932":1,"3432,13733":3,"3433,13732":3,"3433,13733":3,"3434,13732":3,"3432,3433":4,"3433,3434":3,"6865,27465":2,"6866,27464":2,"6866,27465":2,"6867,27464":2,"6864,6866":3,"6865,6866":2,"6866,6867":2,"13731,13733":3,"13732,13734":3,"13731,13734":2,"13732,13735":1,"13732,13733":2,"13733,13734":1,"13733,13735":1,"27465,219725":1,"27466,219724":1,"27466,219725":1,"27467,219724":1,"13731,54929":1,"13732,54928":1,"13732,54929":1,"13733,54928":1,"6865,27463":1,"6866,27462":1,"6866,27463":1,"6867,27462":1,"3431,13729":1,"3432,13728":1,"3432,13729":1,"3433,13728":1,"3430,3432":1,"3431,3432":1,"6863,6866":1,"6863,6867":1,"13730,13732":1,"13730,13733":1,"13731,13732":1,"27463,27466":1,"27464,27467":2,"27463,27467":1,"27464,27468":1,"27464,27466":1,"27465,27467":1,"27465,27468":1,"54930,219725":1,"54931,219724":1,"54931,219725":1,"54932,219724":1,"80,323":82,"81,322":82,"81,323":82,"82,322":82,"78,81":343,"79,82":340,"78,82":167,"79,83":85,"79,81":346,"80,82":176,"80,83":91,"160,645":37,"161,644":37,"161,645":37,"162,644":37,"79,321":85,"80,320":85,"80,321":85,"81,320":85,"78,80":182,"79,80":91,"80,81":88,"159,161":170,"160,162":160,"159,162":171,"160,163":82,"160,161":79,"161,162":38,"161,163":42,"321,1289":16,"322,1288":16,"322,1289":16,"323,1288":16,"160,643":43,"161,642":43,"161,643":43,"162,642":43,"79,319":85,"80,318":85,"80,319":85,"81,318":85,"77,80":92,"77,81":85,"158,161":97,"158,162":49,"159,163":43,"320,322":85,"321,323":74,"320,323":85,"321,324":37,"321,322":37,"322,323":16,"322,324":16,"643,2577":5,"644,2576":5,"644,2577":5,"645,2576":5,"321,1287":21,"322,1286":21,"322,1287":21,"323,1286":21,"159,641":42,"160,640":42,"160,641":42,"161,640":42,"158,160":48,"159,160":42,"319,322":54,"319,323":27,"320,324":21,"642,644":42,"643,645":31,"642,645":43,"643,646":16,"643,644":15,"644,645":5,"644,646":5,"1287,5151":5,"1288,5150":5,"1288,5151":5,"1289,5150":5,"642,2573":10,"643,2572":10,"643,2573":10,"644,2572":10,"320,1285":21,"321,1284":21,"321,1285":21,"322,1284":21,"319,321":27,"320,321":21,"641,643":16,"641,644":33,"642,643":10,"1285,1288":22,"1286,1289":21,"1285,1289":11,"1286,1290":5,"1286,1288":21,"1287,1289":10,"1287,1290":5,"2574,10301":2,"2575,10300":2,"2575,10301":2,"2576,10300":2,"643,2575":11,"644,2574":11,"644,2575":11,"645,2574":11,"641,645":17,"642,646":11,"1286,5149":5,"1287,5148":5,"1287,5149":5,"1288,5148":5,"1285,1287":11,"1286,1287":5,"1287,1288":5,"2573,2575":11,"2574,2576":10,"2573,2576":11,"2574,2577":5,"2574,2575":5,"2575,2576":2,"2575,2577":2,"5149,20601":1,"5150,20600":1,"5150,20601":1,"5151,20600":1,"2574,10299":3,"2575,10298":3,"2575,10299":3,"2576,10298":3,"1286,5147":6,"1287,5146":6,"1287,5147":6,"1288,5146":6,"642,2571":6,"643,2570":6,"643,2571":6,"644,2570":6,"320,1283":6,"321,1282":6,"321,1283":6,"322,1282":6,"159,639":6,"160,638":6,"160,639":6,"161,638":6,"78,317":6,"79,316":6,"79,317":6,"80,316":6,"77,79":7,"78,79":6,"157,160":6,"157,161":6,"318,321":6,"318,322":6,"640,643":6,"640,644":6,"1284,1287":6,"1284,1288":6,"2572,2575":6,"2572,2576":3,"2573,2577":3,"5148,5150":6,"5149,5151":5,"5148,5151":5,"5149,5152":2,"5149,5150":3,"5150,5151":1,"5150,5152":1,"10299,41199":1,"10300,41198":1,"10300,41199":1,"10301,41198":1,"5148,20597":2,"5149,20596":2,"5149,20597":2,"5150,20596":2,"2573,10297":3,"2574,10296":3,"2574,10297":3,"2575,10296":3,"2572,2574":3,"2573,2574":3,"5147,5149":2,"5147,5150":3,"5148,5149":2,"10297,10300":2,"10298,10301":3,"10297,10301":1,"10298,10302":1,"10298,10300":3,"10299,10301":2,"10299,10302":1,"20598,164793":1,"20599,164792":1,"20599,164793":1,"20600,164792":1,"5149,20599":1,"5150,20598":1,"5150,20599":1,"5151,20598":1,"5147,5151":1,"5148,5152":1,"10298,41197":1,"10299,41196":1,"10299,41197":1,"10300,41196":1,"10297,10299":1,"10298,10299":1,"10299,10300":1,"20597,20599":1,"20598,20600":2,"20597,20600":1,"20598,20601":1,"20598,20599":1,"20599,20600":1,"20599,20601":1,"41197,164793":1,"41198,164792":1,"41198,164793":1,"41199,164792":1,"120,485":17,"121,484":17,"121,485":17,"122,484":17,"119,121":171,"120,122":123,"119,122":173,"120,123":66,"120,121":60,"121,122":18,"121,123":22,"241,967":17,"242,966":17,"242,967":17,"243,966":17,"119,481":43,"120,480":43,"120,481":43,"121,480":43,"118,120":68,"118,121":136,"119,120":43,"239,242":85,"240,243":77,"239,243":38,"240,244":17,"240,242":86,"241,243":39,"241,244":17,"482,1933":7,"483,1932":7,"483,1933":7,"484,1932":7,"120,483":43,"121,482":43,"121,483":43,"122,482":43,"118,122":68,"119,123":45,"240,965":22,"241,964":22,"241,965":22,"242,964":22,"239,241":51,"240,241":26,"241,242":22,"481,483":43,"482,484":35,"481,484":42,"482,485":17,"482,483":18,"483,484":7,"483,485":7,"965,3865":1,"966,3864":1,"966,3865":1,"967,3864":1,"482,1931":10,"483,1930":10,"483,1931":10,"484,1930":10,"240,963":21,"241,962":21,"241,963":21,"242,962":21,"119,479":25,"120,478":25,"120,479":25,"121,478":25,"117,120":25,"117,121":25,"238,241":25,"238,242":21,"480,483":29,"480,484":14,"481,485":10,"964,966":21,"965,967":13,"964,967":22,"965,968":7,"965,966":6,"966,967":1,"966,968":1,"1931,7727":1,"1932,7726":1,"1932,7727":1,"1933,7726":1,"964,3861":5,"965,3860":5,"965,3861":5,"966,3860":5,"481,1929":11,"482,1928":11,"482,1929":11,"483,1928":11,"480,482":15,"481,482":11,"963,965":9,"963,966":19,"964,965":5,"1929,1932":11,"1930,1933":8,"1929,1933":4,"1930,1934":1,"1930,1932":11,"1931,1933":4,"1931,1934":1,"3862,15451":1,"3863,15450":1,"3863,15451":1,"3864,15450":1,"965,3863":6,"966,3862":6,"966,3863":6,"967,3862":6,"963,967":10,"964,968":6,"1930,7723":3,"1931,7722":3,"1931,7723":3,"1932,7722":3,"964,3859":4,"965,3858":4,"965,3859":4,"966,3858":4,"481,1927":4,"482,1926":4,"482,1927":4,"483,1926":4,"239,961":4,"240,960":4,"240,961":4,"241,960":4,"238,240":4,"239,240":4,"479,482":4,"479,483":4,"962,965":4,"962,966":4,"1928,1931":4,"1928,1932":3,"1929,1931":8,"3860,3863":5,"3861,3864":5,"3860,3864":2,"3861,3865":1,"3861,3863":6,"3862,3864":3,"3862,3865":1,"7724,30901":1,"7725,30900":1,"7725,30901":1,"7726,30900":1,"1930,7725":3,"1931,7724":3,"1931,7725":3,"1932,7724":3,"1930,1931":4,"1931,1932":3,"3861,15449":2,"3862,15448":2,"3862,15449":2,"3863,15448":2,"3860,3862":3,"3861,3862":2,"3862,3863":2,"7723,7725":3,"7724,7726":3,"7723,7726":2,"7724,7727":1,"7724,7725":2,"7725,7726":1,"7725,7727":1,"15449,123594":1,"15450,123593":1,"15450,123594":1,"15451,123593":1,"7723,30897":1,"7724,30896":1,"7724,30897":1,"7725,30896":1,"3861,15447":1,"3862,15446":1,"3862,15447":1,"3863,15446":1,"1929,7721":1,"1930,7720":1,"1930,7721":1,"1931,7720":1,"1928,1930":1,"1929,1930":1,"3859,3862":1,"3859,3863":1,"7722,7724":1,"7722,7725":1,"7723,7724":1,"15447,15450":1,"15448,15451":2,"15447,15451":1,"15448,15452":1,"15448,15450":1,"15449,15451":1,"15449,15452":1,"30898,123594":1,"30899,123593":1,"30899,123594":1,"30900,123593":1,"90,365":3,"91,364":3,"91,365":3,"92,364":3,"89,91":173,"90,92":95,"89,92":175,"90,93":50,"90,91":46,"91,92":4,"91,93":6,"181,727":2,"182,726":2,"182,727":2,"183,726":2,"89,361":43,"90,360":43,"90,361":43,"91,360":43,"88,90":83,"88,91":167,"89,90":43,"179,182":85,"180,183":48,"179,183":23,"180,184":3,"180,182":86,"181,183":25,"181,184":5,"362,1451":2,"363,1450":2,"363,1451":2,"364,1450":2,"90,363":44,"91,362":44,"91,363":44,"92,362":44,"88,92":84,"89,93":45,"180,723":21,"181,722":21,"181,723":21,"182,722":21,"89,359":40,"90,358":40,"90,359":40,"91,358":40,"87,90":40,"87,91":40,"178,181":40,"178,182":21,"179,181":81,"360,363":43,"361,364":26,"360,364":13,"361,365":2,"361,363":43,"362,364":13,"362,365":2,"724,2899":2,"725,2898":2,"725,2899":2,"726,2898":2,"180,725":22,"181,724":22,"181,725":22,"182,724":22,"180,181":41,"181,182":22,"361,1447":11,"362,1446":11,"362,1447":11,"363,1446":11,"179,721":19,"180,720":19,"180,721":19,"181,720":19,"178,180":19,"179,180":19,"359,362":19,"359,363":11,"360,362":38,"722,725":21,"723,726":15,"722,726":7,"723,727":2,"723,725":22,"724,726":8,"724,727":2,"1448,5795":2,"1449,5794":2,"1449,5795":2,"1450,5794":2,"361,1449":11,"362,1448":11,"362,1449":11,"363,1448":11,"361,362":19,"362,363":11,"723,2895":5,"724,2894":5,"724,2895":5,"725,2894":5,"360,1445":8,"361,1444":8,"361,1445":8,"362,1444":8,"359,361":8,"360,361":8,"721,724":8,"721,725":5,"722,724":17,"1446,1449":11,"1447,1450":10,"1446,1450":5,"1447,1451":2,"1447,1449":11,"1448,1450":5,"1448,1451":2,"2896,11589":1,"2897,11588":1,"2897,11589":1,"2898,11588":1,"723,2897":6,"724,2896":6,"724,2897":6,"725,2896":6,"723,724":9,"724,725":6,"1447,5793":3,"1448,5792":3,"1448,5793":3,"1449,5792":3,"1446,1448":6,"1447,1448":3,"1448,1449":3,"2895,2897":6,"2896,2898":5,"2895,2898":5,"2896,2899":2,"2896,2897":3,"2897,2898":1,"2897,2899":1,"5793,23175":1,"5794,23174":1,"5794,23175":1,"5795,23174":1,"2895,11585":2,"2896,11584":2,"2896,11585":2,"2897,11584":2,"1447,5791":3,"1448,5790":3,"1448,5791":3,"1449,5790":3,"722,2893":3,"723,2892":3,"723,2893":3,"724,2892":3,"721,723":3,"722,723":3,"1445,1448":3,"1445,1449":3,"2894,2896":2,"2894,2897":3,"2895,2896":2,"5791,5794":2,"5792,5795":3,"5791,5795":1,"5792,5796":1,"5792,5794":3,"5793,5795":2,"5793,5796":1,"11586,92694":1,"11587,92693":1,"11587,92694":1,"11588,92693":1,"2896,11587":1,"2897,11586":1,"2897,11587":1,"2898,11586":1,"2894,2898":1,"2895,2899":1,"5792,23173":1,"5793,23172":1,"5793,23173":1,"5794,23172":1,"5791,5793":1,"5792,5793":1,"5793,5794":1,"11585,11587":1,"11586,11588":2,"11585,11588":1,"11586,11589":1,"11586,11587":1,"11587,11588":1,"11587,11589":1,"23173,92694":1,"23174,92693":1,"23174,92694":1,"23175,92693":1,"67,273":36,"68,272":36,"68,273":36,"69,272":36,"66,68":173,"67,69":159,"66,69":173,"67,70":81,"67,68":79,"68,69":37,"68,70":39,"135,545":12,"136,544":12,"136,545":12,"137,544":12,"67,271":42,"68,270":42,"68,271":42,"69,270":42,"65,68":103,"65,69":51,"66,70":43,"134,136":85,"135,137":68,"134,137":86,"135,138":36,"135,136":33,"136,137":13,"136,138":15,"271,1089":2,"272,1088":2,"272,1089":2,"273,1088":2,"135,543":22,"136,542":22,"136,543":22,"137,542":22,"66,269":43,"67,268":43,"67,269":43,"68,268":43,"65,67":53,"66,67":43,"133,136":61,"133,137":31,"134,138":22,"270,272":43,"271,273":25,"270,273":42,"271,274":12,"271,272":13,"272,273":2,"272,274":2,"543,2175":2,"544,2174":2,"544,2175":2,"545,2174":2,"270,1085":11,"271,1084":11,"271,1085":11,"272,1084":11,"134,541":21,"135,540":21,"135,541":21,"136,540":21,"133,135":30,"134,135":21,"269,271":20,"269,272":39,"270,271":11,"541,544":21,"542,545":14,"541,545":7,"542,546":2,"542,544":21,"543,545":7,"543,546":2,"1086,4347":2,"1087,4346":2,"1087,4347":2,"1088,4346":2,"271,1087":10,"272,1086":10,"272,1087":10,"273,1086":10,"269,273":19,"270,274":10,"542,2171":5,"543,2170":5,"543,2171":5,"544,2170":5,"270,1083":9,"271,1082":9,"271,1083":9,"272,1082":9,"134,539":9,"135,538":9,"135,539":9,"136,538":9,"66,267":9,"67,266":9,"67,267":9,"68,266":9,"64,67":20,"64,68":9,"132,135":9,"132,136":9,"268,271":9,"268,272":9,"540,543":9,"540,544":5,"541,543":18,"1084,1087":11,"1085,1088":9,"1084,1088":5,"1085,1089":2,"1085,1087":10,"1086,1088":4,"1086,1089":2,"2172,8691":2,"2173,8690":2,"2173,8691":2,"2174,8690":2,"542,2173":5,"543,2172":5,"543,2173":5,"544,2172":5,"542,543":9,"543,544":5,"1085,4343":3,"1086,4342":3,"1086,4343":3,"1087,4342":3,"541,2169":4,"542,2168":4,"542,2169":4,"543,2168":4,"540,542":4,"541,542":4,"1083,1086":4,"1083,1087":3,"1084,1086":7,"2170,2173":5,"2171,2174":6,"2170,2174":3,"2171,2175":2,"2171,2173":5,"2172,2174":3,"2172,2175":2,"4344,17381":1,"4345,17380":1,"4345,17381":1,"4346,17380":1,"1085,4345":2,"1086,4344":2,"1086,4345":2,"1087,4344":2,"1085,1086":3,"1086,1087":2,"2171,8689":1,"2172,8688":1,"2172,8689":1,"2173,8688":1,"2170,2172":2,"2171,2172":1,"2172,2173":1,"4343,4345":2,"4344,4346":3,"4343,4346":3,"4344,4347":2,"4344,4345":1,"4345,4346":1,"4345,4347":1,"8689,69519":1,"8690,69518":1,"8690,69519":1,"8691,69518":1,"4344,17379":1,"4345,17378":1,"4345,17379":1,"4346,17378":1,"2171,8687":1,"2172,8686":1,"2172,8687":1,"2173,8686":1,"1084,4341":1,"1085,4340":1,"1085,4341":1,"1086,4340":1,"1083,1085":1,"1084,1085":1,"2169,2172":1,"2169,2173":1,"4342,4345":1,"4342,4346":1,"4343,4347":1,"8688,8690":1,"8689,8691":2,"8688,8691":1,"8689,8692":1,"8689,8690":1,"8690,8691":1,"8690,8692":1,"17379,69519":1,"17380,69518":1,"17380,69519":1,"17381,69518":1,"101,409":15,"102,408":15,"102,409":15,"103,408":15,"100,102":85,"101,103":74,"100,103":86,"101,104":39,"101,102":36,"102,103":16,"102,104":18,"203,817":4,"204,816":4,"204,817":4,"205,816":4,"101,407":21,"102,406":21,"102,407":21,"103,406":21,"99,102":56,"99,103":28,"100,104":22,"202,204":42,"203,205":29,"202,205":43,"203,206":15,"203,204":14,"204,205":4,"204,206":5,"407,1631":4,"408,1630":4,"408,1631":4,"409,1630":4,"202,813":10,"203,812":10,"203,813":10,"204,812":10,"100,405":21,"101,404":21,"101,405":21,"102,404":21,"99,101":28,"100,101":21,"201,203":17,"201,204":35,"202,203":10,"405,408":22,"406,409":19,"405,409":10,"406,410":4,"406,408":21,"407,409":9,"407,410":4,"814,3261":1,"815,3260":1,"815,3261":1,"816,3260":1,"203,815":11,"204,814":11,"204,815":11,"205,814":11,"201,205":18,"202,206":11,"406,1629":5,"407,1628":5,"407,1629":5,"408,1628":5,"405,407":13,"406,407":6,"407,408":5,"813,815":11,"814,816":8,"813,816":11,"814,817":4,"814,815":4,"815,816":1,"815,817":1,"1629,6519":1,"1630,6518":1,"1630,6519":1,"1631,6518":1,"813,3257":3,"814,3256":3,"814,3257":3,"815,3256":3,"406,1627":6,"407,1626":6,"407,1627":6,"408,1626":6,"202,811":7,"203,810":7,"203,811":7,"204,810":7,"100,403":7,"101,402":7,"101,403":7,"102,402":7,"98,101":7,"98,102":7,"200,203":7,"200,204":7,"404,407":7,"404,408":6,"812,814":4,"812,815":8,"813,814":3,"1627,1630":5,"1628,1631":5,"1627,1631":2,"1628,1632":1,"1628,1630":6,"1629,1631":3,"1629,1632":1,"3258,13037":1,"3259,13036":1,"3259,13037":1,"3260,13036":1,"814,3259":3,"815,3258":3,"815,3259":3,"816,3258":3,"812,816":4,"813,817":3,"1628,6517":2,"1629,6516":2,"1629,6517":2,"1630,6516":2,"1627,1629":3,"1628,1629":2,"1629,1630":2,"3257,3259":3,"3258,3260":3,"3257,3260":2,"3258,3261":1,"3258,3259":2,"3259,3260":1,"3259,3261":1,"6517,52138":1,"6518,52137":1,"6518,52138":1,"6519,52137":1,"3257,13033":1,"3258,13032":1,"3258,13033":1,"3259,13032":1,"1628,6515":1,"1629,6514":1,"1629,6515":1,"1630,6514":1,"813,3255":1,"814,3254":1,"814,3255":1,"815,3254":1,"405,1625":1,"406,1624":1,"406,1625":1,"407,1624":1,"404,406":1,"405,406":1,"811,814":1,"811,815":1,"1626,1629":1,"1626,1630":1,"3256,3258":1,"3256,3259":1,"3257,3258":1,"6515,6518":1,"6516,6519":2,"6515,6519":1,"6516,6520":1,"6516,6518":1,"6517,6519":1,"6517,6520":1,"13034,52138":1,"13035,52137":1,"13035,52138":1,"13036,52137":1,"76,307":17,"77,306":17,"77,307":17,"78,306":17,"74,77":86,"75,78":78,"74,78":38,"75,79":18,"75,77":87,"76,78":40,"76,79":19,"152,613":6,"153,612":6,"153,613":6,"154,612":6,"75,305":22,"76,304":22,"76,305":22,"77,304":22,"74,76":53,"75,76":27,"76,77":22,"151,153":43,"152,154":33,"151,154":42,"152,155":17,"152,153":17,"153,154":6,"153,155":7,"305,1223":6,"306,1222":6,"306,1223":6,"307,1222":6,"151,609":11,"152,608":11,"152,609":11,"153,608":11,"75,303":21,"76,302":21,"76,303":21,"77,302":21,"73,76":26,"73,77":21,"150,152":16,"150,153":31,"151,152":11,"303,306":21,"304,307":22,"303,307":11,"304,308":6,"304,306":21,"305,307":11,"305,308":6,"610,2445":3,"611,2444":3,"611,2445":3,"612,2444":3,"152,611":10,"153,610":10,"153,611":10,"154,610":10,"150,154":15,"151,155":10,"304,1221":5,"305,1220":5,"305,1221":5,"306,1220":5,"303,305":10,"304,305":5,"305,306":5,"609,611":10,"610,612":11,"609,612":11,"610,613":6,"610,611":5,"611,612":3,"611,613":3,"1221,4889":2,"1222,4888":2,"1222,4889":2,"1223,4888":2,"610,2443":3,"611,2442":3,"611,2443":3,"612,2442":3,"304,1219":5,"305,1218":5,"305,1219":5,"306,1218":5,"151,607":5,"152,606":5,"152,607":5,"153,606":5,"74,301":5,"75,300":5,"75,301":5,"76,300":5,"73,75":5,"74,75":5,"149,152":5,"149,153":5,"302,305":5,"302,306":5,"608,611":5,"608,612":3,"609,613":3,"1220,1222":5,"1221,1223":6,"1220,1223":5,"1221,1224":3,"1221,1222":3,"1222,1223":2,"1222,1224":2,"2443,9777":1,"2444,9776":1,"2444,9777":1,"2445,9776":1,"1221,4887":1,"1222,4886":1,"1222,4887":1,"1223,4886":1,"609,2441":2,"610,2440":2,"610,2441":2,"611,2440":2,"608,610":2,"609,610":2,"1219,1222":2,"1219,1223":1,"1220,1224":1,"2442,2444":2,"2443,2445":3,"2442,2445":3,"2443,2446":2,"2443,2444":1,"2444,2445":1,"2444,2446":1,"4887,39102":1,"4888,39101":1,"4888,39102":1,"4889,39101":1,"2443,9775":1,"2444,9774":1,"2444,9775":1,"2445,9774":1,"1220,4885":1,"1221,4884":1,"1221,4885":1,"1222,4884":1,"1219,1221":1,"1220,1221":1,"2441,2444":1,"2441,2445":1,"2442,2446":1,"4886,4888":1,"4887,4889":2,"4886,4889":1,"4887,4890":1,"4887,4888":1,"4888,4889":1,"4888,4890":1,"9775,39102":1,"9776,39101":1,"9776,39102":1,"9777,39101":1,"114,461":1,"115,460":1,"115,461":1,"116,460":1,"113,115":43,"114,116":25,"113,116":44,"114,117":14,"114,115":12,"115,116":1,"115,117":2,"229,919":1,"230,918":1,"230,919":1,"231,918":1,"113,457":11,"114,456":11,"114,457":11,"115,456":11,"112,114":20,"112,115":40,"113,114":11,"227,230":21,"228,231":13,"227,231":6,"228,232":1,"228,230":22,"229,231":7,"229,232":1,"458,1835":1,"459,1834":1,"459,1835":1,"460,1834":1,"114,459":11,"115,458":11,"115,459":11,"116,458":11,"112,116":20,"113,117":12,"228,915":5,"229,914":5,"229,915":5,"230,914":5,"113,455":9,"114,454":9,"114,455":9,"115,454":9,"111,114":9,"111,115":9,"226,229":9,"226,230":5,"227,229":19,"456,459":11,"457,460":8,"456,460":4,"457,461":1,"457,459":11,"458,460":4,"458,461":1,"916,3667":1,"917,3666":1,"917,3667":1,"918,3666":1,"228,917":6,"229,916":6,"229,917":6,"230,916":6,"228,229":10,"229,230":6,"457,1831":3,"458,1830":3,"458,1831":3,"459,1830":3,"227,913":4,"228,912":4,"228,913":4,"229,912":4,"226,228":4,"227,228":4,"455,458":4,"455,459":3,"456,458":8,"914,917":5,"915,918":5,"914,918":2,"915,919":1,"915,917":6,"916,918":3,"916,919":1,"1832,7333":1,"1833,7332":1,"1833,7333":1,"1834,7332":1,"457,1833":3,"458,1832":3,"458,1833":3,"459,1832":3,"457,458":4,"458,459":3,"915,3665":2,"916,3664":2,"916,3665":2,"917,3664":2,"914,916":3,"915,916":2,"916,917":2,"1831,1833":3,"1832,1834":3,"1831,1834":2,"1832,1835":1,"1832,1833":2,"1833,1834":1,"1833,1835":1,"3665,29325":1,"3666,29324":1,"3666,29325":1,"3667,29324":1,"1831,7329":1,"1832,7328":1,"1832,7329":1,"1833,7328":1,"915,3663":1,"916,3662":1,"916,3663":1,"917,3662":1,"456,1829":1,"457,1828":1,"457,1829":1,"458,1828":1,"455,457":1,"456,457":1,"913,916":1,"913,917":1,"1830,1832":1,"1830,1833":1,"1831,1832":1,"3663,3666":1,"3664,3667":2,"3663,3667":1,"3664,3668":1,"3664,3666":1,"3665,3667":1,"3665,3668":1,"7330,29325":1,"7331,29324":1,"7331,29325":1,"7332,29324":1,"85,345":9,"86,344":9,"86,345":9,"87,344":9,"84,86":42,"85,87":40,"84,87":44,"85,88":22,"85,86":19,"86,87":9,"86,88":10,"171,689":4,"172,688":4,"172,689":4,"173,688":4,"85,343":11,"86,342":11,"86,343":11,"87,342":11,"83,86":25,"83,87":13,"84,88":12,"170,172":21,"171,173":18,"170,173":21,"171,174":9,"171,172":9,"172,173":4,"172,174":4,"343,1377":1,"344,1376":1,"344,1377":1,"345,1376":1,"171,687":5,"172,686":5,"172,687":5,"173,686":5,"84,341":10,"85,340":10,"85,341":10,"86,340":10,"83,85":12,"84,85":10,"169,172":14,"169,173":7,"170,174":5,"342,344":10,"343,345":7,"342,345":11,"343,346":4,"343,344":3,"344,345":1,"344,346":1,"687,2751":1,"688,2750":1,"688,2751":1,"689,2750":1,"342,1373":2,"343,1372":2,"343,1373":2,"344,1372":2,"170,685":5,"171,684":5,"171,685":5,"172,684":5,"169,171":7,"170,171":5,"341,343":4,"341,344":9,"342,343":2,"685,688":6,"686,689":5,"685,689":3,"686,690":1,"686,688":5,"687,689":2,"687,690":1,"1374,5499":1,"1375,5498":1,"1375,5499":1,"1376,5498":1,"343,1375":3,"344,1374":3,"344,1375":3,"345,1374":3,"341,345":5,"342,346":3,"686,2747":2,"687,2746":2,"687,2747":2,"688,2746":2,"342,1371":2,"343,1370":2,"343,1371":2,"344,1370":2,"170,683":2,"171,682":2,"171,683":2,"172,682":2,"84,339":2,"85,338":2,"85,339":2,"86,338":2,"82,85":2,"82,86":2,"168,171":2,"168,172":2,"340,343":2,"340,344":2,"684,687":2,"684,688":2,"685,687":3,"1372,1375":2,"1373,1376":3,"1372,1376":1,"1373,1377":1,"1373,1375":3,"1374,1376":2,"1374,1377":1,"2748,21993":1,"2749,21992":1,"2749,21993":1,"2750,21992":1,"686,2749":1,"687,2748":1,"687,2749":1,"688,2748":1,"686,687":1,"687,688":1,"1373,5497":1,"1374,5496":1,"1374,5497":1,"1375,5496":1,"1372,1374":1,"1373,1374":1,"1374,1375":1,"2747,2749":1,"2748,2750":2,"2747,2750":1,"2748,2751":1,"2748,2749":1,"2749,2750":1,"2749,2751":1,"5497,21993":1,"5498,21992":1,"5498,21993":1,"5499,21992":1,"64,259":10,"65,258":10,"65,259":10,"66,258":10,"62,65":10,"63,66":21,"62,66":10,"63,67":10,"63,65":11,"64,66":12,"128,517":4,"129,516":4,"129,517":4,"130,516":4,"127,129":21,"128,130":19,"127,130":22,"128,131":10,"128,129":9,"129,130":4,"129,131":4,"257,1033":2,"258,1032":2,"258,1033":2,"259,1032":2,"128,515":6,"129,514":6,"129,515":6,"130,514":6,"126,129":13,"126,130":7,"127,131":6,"256,258":11,"257,259":9,"256,259":10,"257,260":4,"257,258":5,"258,259":2,"258,260":2,"515,2063":2,"516,2062":2,"516,2063":2,"517,2062":2,"256,1029":3,"257,1028":3,"257,1029":3,"258,1028":3,"127,513":5,"128,512":5,"128,513":5,"129,512":5,"126,128":6,"127,128":5,"255,257":4,"255,258":7,"256,257":3,"513,516":5,"514,517":6,"513,517":3,"514,518":2,"514,516":5,"515,517":3,"515,518":2,"1030,4125":1,"1031,4124":1,"1031,4125":1,"1032,4124":1,"257,1031":2,"258,1030":2,"258,1031":2,"259,1030":2,"255,259":3,"256,260":2,"514,2061":1,"515,2060":1,"515,2061":1,"516,2060":1,"513,515":2,"514,515":1,"515,516":1,"1029,1031":2,"1030,1032":3,"1029,1032":3,"1030,1033":2,"1030,1031":1,"1031,1032":1,"1031,1033":1,"2061,16494":1,"2062,16493":1,"2062,16494":1,"2063,16493":1,"1030,4123":1,"1031,4122":1,"1031,4123":1,"1032,4122":1,"514,2059":1,"515,2058":1,"515,2059":1,"516,2058":1,"256,1027":1,"257,1026":1,"257,1027":1,"258,1026":1,"127,511":1,"128,510":1,"128,511":1,"129,510":1,"125,128":1,"125,129":1,"254,257":1,"254,258":1,"512,515":1,"512,516":1,"1028,1031":1,"1028,1032":1,"1029,1033":1,"2060,2062":1,"2061,2063":2,"2060,2063":1,"2061,2064":1,"2061,2062":1,"2062,2063":1,"2062,2064":1,"4123,16494":1,"4124,16493":1,"4124,16494":1,"4125,16493":1,"96,389":2,"97,388":2,"97,389":2,"98,388":2,"96,98":14,"96,99":7,"96,97":7,"97,98":2,"97,99":2,"193,775":2,"194,774":2,"194,775":2,"195,774":2,"95,385":5,"96,384":5,"96,385":5,"97,384":5,"191,194":11,"192,195":9,"191,195":5,"192,196":2,"192,194":10,"193,195":4,"193,196":2,"386,1547":2,"387,1546":2,"387,1547":2,"388,1546":2,"96,387":6,"97,386":6,"97,387":6,"98,386":6,"95,99":5,"192,771":3,"193,770":3,"193,771":3,"194,770":3,"190,194":3,"384,387":5,"385,388":6,"384,388":3,"385,389":2,"385,387":5,"386,388":3,"386,389":2,"772,3093":1,"773,3092":1,"773,3093":1,"774,3092":1,"192,773":2,"193,772":2,"193,773":2,"194,772":2,"192,193":3,"193,194":2,"385,1545":1,"386,1544":1,"386,1545":1,"387,1544":1,"384,386":2,"385,386":1,"386,387":1,"771,773":2,"772,774":3,"771,774":3,"772,775":2,"772,773":1,"773,774":1,"773,775":1,"1545,12369":1,"1546,12368":1,"1546,12369":1,"1547,12368":1,"772,3091":1,"773,3090":1,"773,3091":1,"774,3090":1,"385,1543":1,"386,1542":1,"386,1543":1,"387,1542":1,"191,769":1,"192,768":1,"192,769":1,"193,768":1,"383,386":1,"383,387":1,"770,773":1,"770,774":1,"771,775":1,"1544,1546":1,"1545,1547":2,"1544,1547":1,"1545,1548":1,"1545,1546":1,"1546,1547":1,"1546,1548":1,"3091,12369":1,"3092,12368":1,"3092,12369":1,"3093,12368":1,"72,291":5,"73,290":5,"73,291":5,"74,290":5,"71,75":5,"72,75":5,"144,581":3,"145,580":3,"145,581":3,"146,580":3,"144,146":11,"144,147":5,"144,145":6,"145,146":3,"145,147":3,"289,1161":1,"290,1160":1,"290,1161":1,"291,1160":1,"144,579":2,"145,578":2,"145,579":2,"146,578":2,"143,147":2,"288,290":5,"289,291":5,"288,291":6,"289,292":3,"289,290":2,"290,291":1,"290,292":1,"579,2321":1,"580,2320":1,"580,2321":1,"581,2320":1,"289,1159":2,"290,1158":2,"290,1159":2,"291,1158":2,"143,577":3,"144,576":3,"144,577":3,"145,576":3,"287,290":3,"287,291":2,"288,292":2,"578,580":3,"579,581":3,"578,581":2,"579,582":1,"579,580":2,"580,581":1,"580,582":1,"1159,9276":1,"1160,9275":1,"1160,9276":1,"1161,9275":1,"578,2317":1,"579,2316":1,"579,2317":1,"580,2316":1,"288,1157":1,"289,1156":1,"289,1157":1,"290,1156":1,"287,289":1,"288,289":1,"577,579":1,"577,580":1,"578,579":1,"1157,1160":1,"1158,1161":2,"1157,1161":1,"1158,1162":1,"1158,1160":1,"1159,1161":1,"1159,1162":1,"2318,9276":1,"2319,9275":1,"2319,9276":1,"2320,9275":1,"108,437":1,"109,436":1,"109,437":1,"110,436":1,"108,110":8,"108,111":4,"108,109":4,"109,110":1,"109,111":1,"217,871":1,"218,870":1,"218,871":1,"219,870":1,"107,433":3,"108,432":3,"108,433":3,"109,432":3,"215,218":5,"216,219":5,"215,219":2,"216,220":1,"216,218":6,"217,219":3,"217,220":1,"434,1741":1,"435,1740":1,"435,1741":1,"436,1740":1,"108,435":3,"109,434":3,"109,435":3,"110,434":3,"107,111":3,"216,869":2,"217,868":2,"217,869":2,"218,868":2,"216,217":2,"217,218":2,"433,435":3,"434,436":3,"433,436":2,"434,437":1,"434,435":2,"435,436":1,"435,437":1,"869,6956":1,"870,6955":1,"870,6956":1,"871,6955":1,"433,1737":1,"434,1736":1,"434,1737":1,"435,1736":1,"216,867":1,"217,866":1,"217,867":1,"218,866":1,"214,218":1,"432,434":1,"432,435":1,"433,434":1,"867,870":1,"868,871":2,"867,871":1,"868,872":1,"868,870":1,"869,871":1,"869,872":1,"1738,6956":1,"1739,6955":1,"1739,6956":1,"1740,6955":1,"81,327":3,"82,326":3,"82,327":3,"83,326":3,"80,84":3,"81,83":6,"81,84":3,"162,653":2,"163,652":2,"163,653":2,"164,652":2,"80,325":3,"81,324":3,"81,325":3,"82,324":3,"81,82":3,"162,164":6,"161,164":5,"162,165":3,"162,163":3,"163,164":2,"163,165":2,"325,1305":1,"326,1304":1,"326,1305":1,"327,1304":1,"162,651":1,"163,650":1,"163,651":1,"164,650":1,"160,164":1,"161,165":1,"324,326":2,"325,327":3,"324,327":3,"325,328":2,"325,326":1,"326,327":1,"326,328":1,"651,5216":1,"652,5215":1,"652,5216":1,"653,5215":1,"325,1303":1,"326,1302":1,"326,1303":1,"327,1302":1,"161,649":1,"162,648":1,"162,649":1,"163,648":1,"323,326":1,"323,327":1,"324,328":1,"650,652":1,"651,653":2,"650,653":1,"651,654":1,"651,652":1,"652,653":1,"652,654":1,"1303,5216":1,"1304,5215":1,"1304,5216":1,"1305,5215":1,"122,491":1,"123,490":1,"123,491":1,"124,490":1,"121,124":5,"120,124":3,"121,125":1,"122,124":2,"122,125":1,"244,979":1,"245,978":1,"245,979":1,"246,978":1,"121,487":2,"122,486":2,"122,487":2,"123,486":2,"242,245":2,"243,246":3,"242,246":1,"243,247":1,"243,245":3,"244,246":2,"244,247":1,"488,3911":1,"489,3910":1,"489,3911":1,"490,3910":1,"121,489":1,"122,488":1,"122,489":1,"123,488":1,"122,123":1,"243,977":1,"244,976":1,"244,977":1,"245,976":1,"242,244":1,"243,244":1,"244,245":1,"487,489":1,"488,490":2,"487,490":1,"488,491":1,"488,489":1,"489,490":1,"489,491":1,"977,3911":1,"978,3910":1,"978,3911":1,"979,3910":1,"91,369":1,"92,368":1,"92,369":1,"93,368":1,"91,94":2,"92,93":1,"183,735":1,"184,734":1,"184,735":1,"185,734":1,"182,185":3,"181,185":2,"182,186":1,"182,184":2,"183,185":1,"183,186":1,"366,2932":1,"367,2931":1,"367,2932":1,"368,2931":1,"91,367":1,"92,366":1,"92,367":1,"93,366":1,"90,94":1,"182,731":1,"183,730":1,"183,731":1,"184,730":1,"364,367":1,"365,368":2,"364,368":1,"365,369":1,"365,367":1,"366,368":1,"366,369":1,"732,2932":1,"733,2931":1,"733,2932":1,"734,2931":1,"68,277":1,"69,276":1,"69,277":1,"70,276":1,"69,70":1,"137,551":1,"138,550":1,"138,551":1,"139,550":1,"136,139":3,"135,139":1,"136,140":1,"137,139":2,"137,140":1,"274,2198":1,"275,2197":1,"275,2198":1,"276,2197":1,"68,275":1,"69,274":1,"69,275":1,"70,274":1,"67,71":1,"136,549":1,"137,548":1,"137,549":1,"138,548":1,"137,138":1,"273,275":1,"274,276":2,"273,276":1,"274,277":1,"274,275":1,"275,276":1,"275,277":1,"549,2198":1,"550,2197":1,"550,2198":1,"551,2197":1,"102,413":1,"103,412":1,"103,413":1,"104,412":1,"102,105":2,"103,104":1,"103,105":1,"205,1647":1,"206,1646":1,"206,1647":1,"207,1646":1,"102,411":1,"103,410":1,"103,411":1,"104,410":1,"101,105":1,"205,207":2,"204,207":1,"205,208":1,"205,206":1,"206,207":1,"206,208":1,"411,1647":1,"412,1646":1,"412,1647":1,"413,1646":1,"77,311":1,"78,310":1,"78,311":1,"79,310":1,"76,80":1,"154,1234":1,"155,1233":1,"155,1234":1,"156,1233":1,"153,156":2,"152,156":1,"153,157":1,"154,156":1,"154,157":1,"308,1234":1,"309,1233":1,"309,1234":1,"310,1233":1,"115,924":1,"116,923":1,"116,924":1,"117,923":1,"114,118":1,"115,118":1,"230,924":1,"231,923":1,"231,924":1,"232,923":1,"86,692":1,"87,691":1,"87,692":1,"88,691":1,"85,89":1,"86,89":1,"172,692":1,"173,691":1,"173,692":1,"174,691":1,"64,518":1,"65,517":1,"65,518":1,"66,517":1,"64,65":1,"65,66":1,"129,518":1,"130,517":1,"130,518":1,"131,517":1,"53,216":1,"54,215":1,"54,216":1,"55,215":1},"monic":{"1":1}}
```

`gcd_trace_r2_t2.json` (trial 2: histogram of every charged half-gcd and root operation by kind and size; `halfgcd_charge.py` recomputes the stage charge from it):

```json
{"copy":{"97657":1,"97656":1,"48829":2,"48828":2,"24415":3,"24414":3,"12209":3,"12208":3,"6105":8,"6104":8,"3053":19,"3052":19,"1527":40,"1526":40,"765":40,"764":40,"383":130,"382":130,"193":137,"192":137,"189":345,"188":345,"381":170,"380":170,"191":351,"190":351,"761":85,"760":85,"379":171,"378":171,"187":216,"186":216,"1525":43,"1524":43,"763":86,"762":86,"3051":21,"3050":21,"1523":43,"1522":43,"759":45,"758":45,"377":45,"376":45,"6103":11,"6102":11,"3049":22,"3048":22,"12205":6,"12204":6,"6101":11,"6100":11,"24413":3,"24412":3,"12207":5,"12206":5,"48827":1,"48826":1,"24411":2,"24410":2,"12203":2,"12202":2,"6099":2,"6098":2,"3047":2,"3046":2,"1521":2,"1520":2,"97655":1,"97654":1,"48825":1,"48824":1,"73243":1,"73242":1,"36623":1,"36622":1,"18313":1,"18312":1,"9157":4,"9156":4,"4579":9,"4578":9,"2291":9,"2290":9,"1147":9,"1146":9,"575":9,"574":9,"289":15,"288":15,"145":191,"144":191,"143":352,"142":352,"285":170,"284":170,"141":346,"140":346,"571":86,"570":86,"287":176,"286":176,"283":162,"282":162,"139":164,"138":164,"1143":42,"1142":42,"573":85,"572":85,"569":76,"568":76,"2287":22,"2286":22,"1145":43,"1144":43,"1141":34,"1140":34,"4577":11,"4576":11,"2289":21,"2288":21,"9155":5,"9154":5,"4575":10,"4574":10,"2285":12,"2284":12,"18309":2,"18308":2,"9153":5,"9152":5,"36619":2,"36618":2,"18311":3,"18310":3,"18307":2,"18306":2,"9151":2,"9150":2,"4573":2,"4572":2,"73241":1,"73240":1,"36621":1,"36620":1,"54933":1,"54932":1,"27467":1,"27466":1,"13735":1,"13734":1,"6869":1,"6868":1,"3435":7,"3434":7,"1719":7,"1718":7,"861":7,"860":7,"431":50,"430":50,"217":54,"216":54,"213":172,"212":172,"429":86,"428":86,"215":177,"214":177,"857":43,"856":43,"427":85,"426":85,"211":121,"210":121,"1715":21,"1714":21,"859":42,"858":42,"855":36,"854":36,"425":36,"424":36,"3433":10,"3432":10,"1717":21,"1716":21,"6865":5,"6864":5,"3431":11,"3430":11,"1713":15,"1712":15,"13731":3,"13730":3,"6867":6,"6866":6,"6863":4,"6862":4,"3429":4,"3428":4,"27465":2,"27464":2,"13733":3,"13732":3,"54929":1,"54928":1,"27463":1,"27462":1,"13729":1,"13728":1,"41199":1,"41198":1,"20601":1,"20600":1,"10301":2,"10300":2,"5151":5,"5150":5,"2577":5,"2576":5,"1289":16,"1288":16,"645":37,"644":37,"323":82,"322":82,"163":85,"162":85,"159":173,"158":173,"321":85,"320":85,"161":176,"160":176,"643":43,"642":43,"319":85,"318":85,"157":92,"156":92,"1287":21,"1286":21,"641":42,"640":42,"2573":10,"2572":10,"1285":21,"1284":21,"5149":5,"5148":5,"2575":11,"2574":11,"10299":3,"10298":3,"5147":6,"5146":6,"2571":6,"2570":6,"1283":6,"1282":6,"639":6,"638":6,"317":6,"316":6,"20597":2,"20596":2,"10297":3,"10296":3,"41197":1,"41196":1,"20599":1,"20598":1,"30901":1,"30900":1,"15451":1,"15450":1,"7727":1,"7726":1,"3865":1,"3864":1,"1933":7,"1932":7,"967":17,"966":17,"485":17,"484":17,"243":62,"242":62,"241":87,"240":87,"481":43,"480":43,"239":86,"238":86,"965":22,"964":22,"483":43,"482":43,"1931":10,"1930":10,"963":21,"962":21,"479":25,"478":25,"237":25,"236":25,"3861":5,"3860":5,"1929":11,"1928":11,"7723":3,"7722":3,"3863":6,"3862":6,"3859":4,"3858":4,"1927":4,"1926":4,"961":4,"960":4,"15449":2,"15448":2,"7725":3,"7724":3,"30897":1,"30896":1,"15447":1,"15446":1,"7721":1,"7720":1,"23175":1,"23174":1,"11589":1,"11588":1,"5795":2,"5794":2,"2899":2,"2898":2,"1451":2,"1450":2,"727":2,"726":2,"365":3,"364":3,"183":48,"182":48,"181":87,"180":87,"361":43,"360":43,"179":87,"178":87,"723":21,"722":21,"363":44,"362":44,"359":40,"358":40,"177":40,"176":40,"1447":11,"1446":11,"725":22,"724":22,"721":19,"720":19,"2895":5,"2894":5,"1449":11,"1448":11,"1445":8,"1444":8,"5793":3,"5792":3,"2897":6,"2896":6,"11585":2,"11584":2,"5791":3,"5790":3,"2893":3,"2892":3,"23173":1,"23172":1,"11587":1,"11586":1,"17381":1,"17380":1,"8691":2,"8690":2,"4347":2,"4346":2,"2175":2,"2174":2,"1089":2,"1088":2,"545":12,"544":12,"273":36,"272":36,"137":79,"136":79,"135":89,"134":89,"271":42,"270":42,"133":85,"132":85,"543":22,"542":22,"269":43,"268":43,"1085":11,"1084":11,"541":21,"540":21,"2171":5,"2170":5,"1087":10,"1086":10,"1083":9,"1082":9,"539":9,"538":9,"267":9,"266":9,"131":20,"130":20,"4343":3,"4342":3,"2173":5,"2172":5,"2169":4,"2168":4,"8689":1,"8688":1,"4345":2,"4344":2,"17379":1,"17378":1,"8687":1,"8686":1,"4341":1,"4340":1,"13037":1,"13036":1,"6519":1,"6518":1,"3261":1,"3260":1,"1631":4,"1630":4,"817":4,"816":4,"409":15,"408":15,"205":37,"204":37,"203":44,"202":44,"407":21,"406":21,"201":42,"200":42,"813":10,"812":10,"405":21,"404":21,"1629":5,"1628":5,"815":11,"814":11,"3257":3,"3256":3,"1627":6,"1626":6,"811":7,"810":7,"403":7,"402":7,"199":7,"198":7,"6517":2,"6516":2,"3259":3,"3258":3,"13033":1,"13032":1,"6515":1,"6514":1,"3255":1,"3254":1,"1625":1,"1624":1,"9777":1,"9776":1,"4889":2,"4888":2,"2445":3,"2444":3,"1223":6,"1222":6,"613":6,"612":6,"307":17,"306":17,"155":17,"154":17,"151":44,"150":44,"305":22,"304":22,"153":44,"152":44,"609":11,"608":11,"303":21,"302":21,"149":26,"148":26,"1221":5,"1220":5,"611":10,"610":10,"2443":3,"2442":3,"1219":5,"1218":5,"607":5,"606":5,"301":5,"300":5,"4887":1,"4886":1,"2441":2,"2440":2,"9775":1,"9774":1,"4885":1,"4884":1,"7333":1,"7332":1,"3667":1,"3666":1,"1835":1,"1834":1,"919":1,"918":1,"461":1,"460":1,"231":12,"230":12,"229":22,"228":22,"457":11,"456":11,"227":22,"226":22,"915":5,"914":5,"459":11,"458":11,"455":9,"454":9,"225":9,"224":9,"1831":3,"1830":3,"917":6,"916":6,"913":4,"912":4,"3665":2,"3664":2,"1833":3,"1832":3,"7329":1,"7328":1,"3663":1,"3662":1,"1829":1,"1828":1,"5499":1,"5498":1,"2751":1,"2750":1,"1377":1,"1376":1,"689":4,"688":4,"345":9,"344":9,"173":20,"172":20,"171":22,"170":22,"343":11,"342":11,"169":21,"168":21,"687":5,"686":5,"341":10,"340":10,"1373":2,"1372":2,"685":5,"684":5,"2747":2,"2746":2,"1375":3,"1374":3,"1371":2,"1370":2,"683":2,"682":2,"339":2,"338":2,"167":2,"166":2,"5497":1,"5496":1,"2749":1,"2748":1,"4125":1,"4124":1,"2063":2,"2062":2,"1033":2,"1032":2,"517":4,"516":4,"259":10,"258":10,"127":10,"126":10,"257":10,"256":10,"515":6,"514":6,"255":11,"254":11,"1029":3,"1028":3,"513":5,"512":5,"2061":1,"2060":1,"1031":2,"1030":2,"4123":1,"4122":1,"2059":1,"2058":1,"1027":1,"1026":1,"511":1,"510":1,"253":1,"252":1,"3093":1,"3092":1,"1547":2,"1546":2,"775":2,"774":2,"389":2,"388":2,"195":7,"194":7,"385":5,"384":5,"771":3,"770":3,"387":5,"386":5,"1545":1,"1544":1,"773":2,"772":2,"3091":1,"3090":1,"1543":1,"1542":1,"769":1,"768":1,"2321":1,"2320":1,"1161":1,"1160":1,"581":3,"580":3,"291":5,"290":5,"147":5,"146":5,"579":2,"578":2,"1159":2,"1158":2,"577":3,"576":3,"2317":1,"2316":1,"1157":1,"1156":1,"1741":1,"1740":1,"871":1,"870":1,"437":1,"436":1,"219":4,"218":4,"433":3,"432":3,"869":2,"868":2,"435":3,"434":3,"1737":1,"1736":1,"867":1,"866":1,"1305":1,"1304":1,"653":2,"652":2,"327":3,"326":3,"165":3,"164":3,"325":3,"324":3,"651":1,"650":1,"1303":1,"1302":1,"649":1,"648":1,"979":1,"978":1,"491":1,"490":1,"247":1,"246":1,"487":2,"486":2,"245":3,"244":3,"977":1,"976":1,"489":1,"488":1,"735":1,"734":1,"369":1,"368":1,"185":2,"184":2,"731":1,"730":1,"367":1,"366":1,"551":1,"550":1,"277":1,"276":1,"549":1,"548":1,"275":1,"274":1,"413":1,"412":1,"207":2,"206":2,"411":1,"410":1,"311":1,"310":1,"233":1,"232":1,"175":1,"174":1,"129":1,"128":1},"division_classical":{"192,191":1157,"191,190":1157,"190,189":1508,"189,188":1508,"188,187":1853,"187,186":1853,"186,185":2069,"185,184":2069,"184,183":2071,"183,182":2071,"182,181":2119,"181,180":2119,"180,179":2206,"179,178":2206,"178,177":2293,"177,176":2293,"176,175":2333,"175,174":2333,"174,173":2334,"173,172":2334,"172,171":2354,"171,170":2354,"170,169":2376,"169,168":2376,"168,167":2397,"167,166":2397,"166,165":2399,"165,164":2399,"164,163":2402,"163,162":2402,"162,161":2487,"161,160":2487,"160,159":2663,"159,158":2663,"158,157":2836,"157,156":2836,"156,155":2928,"155,154":2928,"154,153":2945,"153,152":2945,"152,151":2989,"151,150":2989,"150,149":3033,"149,148":3033,"148,147":3059,"147,146":3059,"146,145":3064,"145,144":3064,"144,143":3255,"143,142":3255,"142,141":3607,"141,140":3607,"140,139":3953,"139,138":3953,"138,137":4117,"137,136":4117,"136,135":4196,"135,134":4196,"134,133":4285,"133,132":4285,"132,131":4370,"131,130":4370,"130,129":4390,"129,128":4390,"128,127":4381,"127,126":4370,"126,125":4379,"125,124":4379,"124,123":4379,"123,122":4378,"122,121":4375,"121,120":4313,"120,119":4226,"119,118":4140,"118,117":4115,"117,116":4115,"116,115":4114,"115,114":4102,"114,113":4080,"113,112":4058,"112,111":4049,"111,110":4049,"110,109":4049,"109,108":4045,"108,107":3991,"107,106":3814,"106,105":3642,"105,104":3521,"104,103":3521,"103,102":3519,"102,101":3482,"101,100":3438,"100,99":3396,"99,98":3389,"98,97":3389,"97,96":3382,"286,285":131,"96,95":3245,"95,94":2894,"573,572":40,"285,284":171,"1144,1143":40,"570,569":85,"283,282":172,"94,93":2549,"2289,2288":19,"571,570":86,"1143,1142":43,"4578,4577":8,"2287,2286":21,"1141,1140":43,"568,567":45,"282,281":46,"9156,9155":3,"4576,4575":11,"2286,2285":22,"18310,18309":3,"9153,9152":6,"4575,4574":11,"36621,36620":2,"9154,9153":5,"18309,18308":3,"73242,73241":1,"36619,36618":1,"18307,18306":2,"9151,9150":2,"4573,4572":2,"2284,2283":2,"1140,1139":2,"341796,341795":1,"73240,73239":1,"36618,36617":1,"292968,292967":1,"93,92":2333,"92,91":2331,"91,90":2283,"90,89":2196,"89,88":2109,"88,87":2069,"87,86":2068,"86,85":2048,"85,84":2026,"84,83":2005,"83,82":2003,"82,81":2000,"81,80":1915,"80,79":1739,"79,78":1566,"78,77":1474,"77,76":1457,"76,75":1413,"75,74":1369,"74,73":1343,"73,72":1338,"216,215":426,"72,71":1147,"430,429":9,"213,212":758,"71,70":795,"859,858":9,"214,213":764,"427,426":86,"211,210":922,"70,69":449,"1717,1716":9,"429,428":85,"856,855":42,"426,425":76,"3433,3432":9,"858,857":43,"1714,1713":22,"855,854":34,"6867,6866":4,"1716,1715":21,"3432,3431":11,"13734,13733":1,"6865,6864":5,"3430,3429":10,"1713,1712":12,"27466,27465":1,"13731,13730":2,"6864,6863":5,"54931,54930":1,"13732,13731":3,"27463,27462":2,"13729,13728":2,"6862,6861":2,"3429,3428":2,"256346,256345":1,"27465,27464":1,"54930,54929":1,"219725,219724":1,"215,214":411,"212,211":760,"210,209":881,"209,208":881,"208,207":881,"207,206":882,"206,205":883,"205,204":884,"204,203":956,"203,202":920,"202,201":1006,"201,200":1007,"200,199":1006,"199,198":1015,"198,197":1013,"197,196":1013,"196,195":1013,"195,194":1013,"194,193":1020,"193,192":1030,"322,321":51,"645,644":7,"321,320":87,"1288,1287":7,"642,641":43,"319,318":86,"2575,2574":7,"643,642":42,"1285,1284":21,"640,639":36,"318,317":37,"5151,5150":1,"1287,1286":21,"2574,2573":10,"10300,10299":1,"5148,5147":5,"2572,2571":11,"1284,1283":15,"20599,20598":1,"5149,5148":6,"10297,10296":3,"5146,5145":4,"2571,2570":4,"41199,41198":1,"10299,10298":3,"20598,20597":2,"192258,192257":1,"41196,41195":1,"20596,20595":1,"10296,10295":1,"164793,164792":1,"241,240":171,"483,482":37,"240,239":261,"966,965":16,"481,480":43,"238,237":347,"1932,1931":5,"964,963":21,"480,479":42,"3862,3861":5,"1929,1928":10,"963,962":21,"7725,7724":2,"1930,1929":11,"3861,3860":5,"15450,15449":1,"7723,7722":3,"3859,3858":6,"1927,1926":6,"961,960":6,"478,477":6,"237,236":268,"30898,30897":1,"15447,15446":2,"7722,7721":3,"144193,144192":1,"15448,15447":1,"30897,30896":1,"123594,123593":1,"242,241":89,"239,238":176,"236,235":287,"235,234":287,"234,233":287,"233,232":287,"232,231":289,"231,230":288,"230,229":300,"229,228":317,"228,227":344,"227,226":322,"226,225":365,"225,224":349,"224,223":353,"223,222":353,"222,221":353,"221,220":353,"220,219":353,"219,218":353,"218,217":357,"217,216":362,"363,362":18,"724,723":17,"360,359":44,"1449,1448":7,"361,360":44,"723,722":22,"2898,2897":1,"1447,1446":10,"721,720":21,"358,357":26,"5794,5793":1,"2895,2894":5,"1446,1445":11,"11587,11586":1,"2896,2895":6,"5791,5790":3,"2893,2892":4,"1444,1443":4,"720,719":4,"23175,23174":1,"5793,5792":3,"11586,11585":2,"108143,108142":1,"23172,23171":1,"11584,11583":1,"5790,5789":1,"92694,92693":1,"273,272":4,"544,543":2,"270,269":44,"1087,1086":2,"271,270":45,"541,540":21,"268,267":41,"2173,2172":2,"543,542":22,"1084,1083":11,"540,539":19,"4345,4344":2,"1086,1085":11,"2170,2169":5,"1083,1082":8,"8691,8690":1,"2172,2171":6,"4344,4343":3,"17380,17379":1,"8688,8687":2,"4342,4341":3,"2169,2168":3,"81106,81105":1,"8689,8688":1,"17379,17378":1,"69519,69518":1,"69,68":285,"68,67":206,"408,407":12,"67,66":117,"816,815":2,"406,405":22,"1630,1629":2,"813,812":11,"405,404":21,"3259,3258":2,"814,813":10,"1627,1626":5,"811,810":9,"403,402":9,"66,65":32,"6517,6516":2,"1629,1628":5,"3256,3255":3,"1626,1625":4,"13035,13034":1,"3258,3257":2,"6516,6515":1,"60828,60827":1,"13033,13032":1,"6514,6513":1,"3255,3254":1,"52138,52137":1,"306,305":16,"612,611":4,"304,303":22,"1222,1221":4,"609,608":10,"303,302":22,"2445,2444":1,"610,609":11,"1221,1220":5,"4888,4887":1,"2442,2441":3,"1219,1218":6,"607,606":7,"301,300":8,"9777,9776":1,"2443,2442":3,"4887,4886":2,"45619,45618":1,"9774,9773":1,"4885,4884":1,"2440,2439":1,"1218,1217":1,"39102,39101":1,"459,458":6,"916,915":6,"456,455":11,"1833,1832":3,"457,456":10,"915,914":5,"3666,3665":2,"1831,1830":3,"913,912":5,"454,453":5,"7332,7331":1,"3664,3663":1,"1830,1829":2,"34213,34212":1,"7330,7329":1,"3663,3662":1,"29325,29324":1,"345,344":2,"688,687":1,"342,341":12,"1375,1374":1,"343,342":12,"685,684":5,"340,339":10,"2749,2748":1,"687,686":6,"1372,1371":3,"684,683":4,"5499,5498":1,"1374,1373":3,"2748,2747":2,"25658,25657":1,"5496,5495":1,"2746,2745":1,"1371,1370":1,"21993,21992":1,"258,257":10,"516,515":4,"256,255":22,"1032,1031":1,"514,513":5,"255,254":21,"2062,2061":1,"1029,1028":2,"513,512":5,"4123,4122":1,"1030,1029":3,"2059,2058":2,"1027,1026":2,"511,510":2,"253,252":24,"19243,19242":1,"2061,2060":1,"4122,4121":1,"16494,16493":1,"65,64":12,"64,63":11,"387,386":5,"254,253":22,"252,251":23,"251,250":23,"250,249":23,"249,248":23,"248,247":23,"247,246":23,"246,245":24,"245,244":24,"244,243":30,"243,242":30,"774,773":2,"385,384":7,"1546,1545":2,"771,770":3,"384,383":6,"3093,3092":1,"772,771":2,"1545,1544":1,"14431,14430":1,"3091,3090":1,"1543,1542":1,"769,768":1,"382,381":2,"12369,12368":1,"291,290":3,"580,579":2,"288,287":6,"1159,1158":2,"289,288":6,"577,576":3,"2319,2318":1,"579,578":2,"1158,1157":1,"10822,10821":1,"2317,2316":1,"1156,1155":1,"576,575":1,"9276,9275":1,"435,434":3,"870,869":1,"433,432":2,"1740,1739":1,"868,867":2,"432,431":3,"8115,8114":1,"1737,1736":1,"867,866":1,"6956,6955":1,"327,326":2,"652,651":1,"324,323":4,"1305,1304":1,"325,324":4,"651,650":2,"6085,6084":1,"1302,1301":1,"649,648":1,"5216,5215":1,"489,488":2,"978,977":1,"487,486":1,"4563,4562":1,"976,975":1,"486,485":1,"3911,3910":1,"367,366":2,"733,732":1,"364,363":3,"3421,3420":1,"366,365":2,"732,731":1,"2932,2931":1,"276,275":2,"550,549":1,"2564,2563":1,"274,273":2,"547,546":1,"2198,2197":1,"412,411":1,"1922,1921":1,"411,410":1,"1647,1646":1,"309,308":2,"1440,1439":1,"307,306":2,"1234,1233":1,"1078,1077":1,"924,923":1,"807,806":1,"692,691":1,"604,603":1,"518,517":1,"452,451":1,"386,385":1,"383,382":1,"381,380":1,"380,379":1,"379,378":1,"378,377":1,"377,376":1,"376,375":1,"375,374":1,"374,373":1,"373,372":1,"372,371":1,"371,370":1,"370,369":1,"369,368":1,"368,367":1,"365,364":1,"362,361":1,"359,358":1,"357,356":1,"356,355":1,"355,354":1,"354,353":1,"353,352":1,"352,351":1,"351,350":1,"350,349":1,"349,348":1,"348,347":1,"347,346":1,"346,345":1,"344,343":1,"341,340":1,"339,338":1,"338,337":1,"337,336":1,"336,335":1,"335,334":1,"334,333":1,"333,332":1,"332,331":1,"331,330":1,"330,329":1,"329,328":1,"328,327":1,"326,325":1,"323,322":1,"320,319":1,"317,316":1,"316,315":1,"315,314":1,"314,313":1,"313,312":1,"312,311":1,"311,310":1,"310,309":1,"308,307":1,"305,304":1,"302,301":1,"300,299":1,"299,298":1,"298,297":1,"297,296":1,"296,295":1,"295,294":1,"294,293":1,"293,292":1,"292,291":1,"290,289":1,"287,286":1,"284,283":1,"281,280":1,"280,279":1,"279,278":1,"278,277":1,"277,276":1,"275,274":1,"272,271":1,"269,268":1,"267,266":1,"266,265":1,"265,264":1,"264,263":1,"263,262":1,"262,261":1,"261,260":1,"260,259":1,"259,258":1,"257,256":1,"63,62":1,"62,61":1,"61,60":1,"60,59":1,"59,58":1,"58,57":1,"57,56":1,"56,55":1,"55,54":1,"54,53":1,"53,52":1,"52,51":1,"51,50":1,"50,49":1,"49,48":1,"48,47":1,"47,46":1,"46,45":1,"45,44":1,"44,43":1,"43,42":1,"42,41":1,"41,40":1,"40,39":1,"39,38":1,"38,37":1,"37,36":1,"36,35":1,"35,34":1,"34,33":1,"33,32":1,"32,31":1,"31,30":1,"30,29":1,"29,28":1,"28,27":1,"27,26":1,"26,25":1,"25,24":1,"24,23":1,"23,22":1,"22,21":1,"21,20":1,"20,19":1,"19,18":1,"18,17":1,"17,16":1,"16,15":1,"15,14":1,"14,13":1,"13,12":1,"12,11":1,"11,10":1,"10,9":1,"9,8":1,"8,7":1,"7,6":1,"6,5":1,"5,4":1,"4,3":1,"3,2":1,"2,0":1,"2,1":2},"product_zero":{"2,0":4404},"addsub":{"1":4404,"2":8808,"3":8808,"4":8808,"5":8808,"6":8808,"7":8808,"8":8808,"9":8808,"10":8808,"11":8808,"12":8808,"13":8808,"14":8808,"15":8808,"16":8808,"17":8808,"18":8808,"19":8808,"20":8808,"21":8808,"22":8808,"23":8808,"24":8808,"25":8808,"26":8808,"27":8808,"28":8808,"29":8808,"30":8808,"31":8808,"32":8808,"33":8808,"34":8808,"35":8808,"36":8808,"37":8808,"38":8808,"39":8808,"40":8808,"41":8807,"42":8806,"43":8806,"44":8806,"45":8806,"46":8806,"47":8806,"48":8806,"49":8806,"50":8806,"51":8806,"52":8806,"53":8806,"54":8806,"55":8805,"56":8804,"57":8804,"58":8804,"59":8804,"60":8804,"61":8804,"62":8804,"63":8804,"64":8794,"65":8783,"66":8773,"67":8668,"68":8535,"69":8445,"70":8152,"71":7564,"72":7196,"73":6843,"74":6319,"75":6097,"76":6027,"77":5982,"78":5933,"79":5782,"80":5506,"81":5326,"82":5144,"83":4889,"84":4799,"85":4773,"86":4742,"87":4720,"88":4688,"89":4627,"90":4499,"91":4408,"92":4320,"93":4189,"94":3924,"95":3406,"96":3051,"97":2653,"477":130,"478":130,"98":2174,"190":641,"191":565,"192":401,"954":40,"955":40,"474":170,"475":170,"189":557,"193":144,"381":299,"382":271,"383":184,"1907":40,"1908":40,"949":85,"950":85,"472":171,"473":171,"188":261,"379":197,"380":323,"384":45,"762":179,"763":157,"764":110,"3814":19,"3815":19,"952":86,"953":86,"1904":43,"1905":43,"761":131,"765":46,"1525":88,"1526":72,"1527":57,"7629":8,"7630":8,"3812":21,"3813":21,"1902":43,"1903":43,"947":45,"948":45,"469":45,"470":45,"187":45,"378":66,"760":58,"1524":72,"1528":25,"3051":41,"3052":38,"3053":27,"15259":3,"15260":3,"7627":11,"7628":11,"3809":22,"3810":22,"1523":31,"3050":37,"3054":11,"6103":19,"6104":17,"6105":12,"30517":3,"30518":3,"15254":6,"15255":6,"7624":11,"7625":11,"3049":17,"6101":10,"6102":19,"6106":3,"12206":11,"12207":10,"12208":7,"61034":2,"61035":2,"15257":5,"15258":5,"30514":3,"30515":3,"12205":7,"12209":3,"24413":5,"24414":5,"24415":4,"122069":1,"122070":1,"61032":1,"61033":1,"30512":2,"30513":2,"15252":2,"15253":2,"7622":2,"7623":2,"3807":2,"3808":2,"1899":2,"1900":2,"759":13,"1522":7,"3048":2,"6100":2,"12204":2,"24412":3,"24416":2,"48827":3,"48828":3,"48829":2,"439451":1,"439452":1,"122067":1,"122068":1,"61029":1,"61030":1,"24411":1,"48826":1,"48830":1,"97655":1,"97656":2,"97657":1,"488279":1,"488280":1,"359":35,"360":75,"143":613,"144":458,"145":208,"717":9,"718":9,"354":170,"355":170,"141":494,"142":678,"146":22,"286":299,"287":225,"288":111,"1432":9,"1433":9,"357":176,"358":176,"712":86,"713":86,"352":162,"353":162,"140":163,"284":238,"285":333,"289":19,"572":160,"573":127,"574":62,"2862":9,"2863":9,"714":85,"715":85,"1427":42,"1428":42,"709":76,"710":76,"283":76,"570":121,"571":161,"575":10,"1144":81,"1145":68,"1146":39,"5722":9,"5723":9,"1429":43,"1430":43,"2857":22,"2858":22,"1424":34,"1425":34,"569":45,"1142":51,"1143":82,"1147":10,"2288":44,"2289":39,"2290":28,"11444":4,"11445":4,"2859":21,"2860":21,"5719":11,"5720":11,"2287":36,"2291":9,"4577":20,"4578":18,"4579":14,"22889":1,"22890":1,"11442":5,"11443":5,"5717":10,"5718":10,"2854":12,"2855":12,"1141":12,"2286":14,"4576":17,"4580":6,"9155":9,"9156":8,"9157":5,"45777":1,"45778":1,"22884":2,"22885":2,"11439":5,"11440":5,"4575":9,"9153":6,"9154":9,"9158":1,"18310":5,"18311":4,"18312":3,"91552":1,"91553":1,"22887":3,"22888":3,"45772":2,"45773":2,"22882":2,"22883":2,"11437":2,"11438":2,"5714":2,"5715":2,"2285":3,"4574":2,"9152":2,"18308":2,"18309":5,"18313":1,"36620":3,"36621":3,"36622":2,"329587":1,"329588":1,"45774":1,"45775":1,"91549":1,"91550":1,"36619":1,"36623":1,"73241":1,"73242":2,"73243":1,"366208":1,"366209":1,"99":2031,"100":2017,"101":1968,"102":1910,"103":1865,"104":1800,"105":1762,"106":1639,"107":1382,"108":1204,"109":990,"537":50,"538":50,"110":765,"214":307,"215":268,"216":187,"1074":7,"1075":7,"534":86,"535":86,"213":292,"217":59,"429":158,"430":122,"431":56,"2147":7,"2148":7,"1069":43,"1070":43,"532":85,"533":85,"212":157,"427":126,"428":175,"432":8,"858":79,"859":64,"860":39,"4292":7,"4293":7,"1072":42,"1073":42,"2142":21,"2143":21,"1067":36,"1068":36,"529":36,"530":36,"211":36,"426":36,"856":51,"857":83,"861":7,"1716":38,"1717":36,"1718":26,"8584":1,"8585":1,"2144":21,"2145":21,"4289":10,"4290":10,"1715":38,"1719":8,"3433":21,"3434":16,"3435":9,"17167":1,"17168":1,"8579":5,"8580":5,"4287":11,"4288":11,"2139":15,"2140":15,"855":20,"1714":21,"3431":13,"3432":22,"3436":1,"6866":10,"6867":8,"6868":5,"34332":1,"34333":1,"8582":6,"8583":6,"17162":3,"17163":3,"8577":4,"8578":4,"4284":4,"4285":4,"1713":6,"3430":4,"6864":5,"6865":10,"6869":2,"13732":6,"13733":5,"13734":3,"68664":1,"68665":1,"17164":3,"17165":3,"34329":2,"34330":2,"13731":4,"13735":1,"27465":2,"27466":2,"27467":2,"247189":1,"247190":1,"68659":1,"68660":1,"34327":1,"34328":1,"17159":1,"17160":1,"6863":1,"13730":1,"27463":1,"27464":2,"27468":1,"54930":1,"54931":2,"54932":1,"274654":1,"274655":1,"402":82,"403":82,"160":337,"161":300,"162":219,"804":37,"805":37,"399":85,"400":85,"159":261,"163":90,"321":165,"322":154,"323":112,"1609":16,"1610":16,"802":43,"803":43,"397":85,"398":85,"158":97,"320":133,"324":40,"643":85,"644":73,"645":52,"3219":5,"3220":5,"1607":21,"1608":21,"799":42,"800":42,"319":54,"642":75,"646":17,"1287":39,"1288":34,"1289":23,"6437":5,"6438":5,"3214":10,"3215":10,"1604":21,"1605":21,"641":33,"1285":25,"1286":37,"1290":7,"2574":22,"2575":19,"2576":13,"12874":2,"12875":2,"3217":11,"3218":11,"6434":5,"6435":5,"2573":18,"2577":7,"5149":11,"5150":9,"5151":6,"25749":1,"25750":1,"12872":3,"12873":3,"6432":6,"6433":6,"3212":6,"3213":6,"1602":6,"1603":6,"797":6,"798":6,"394":6,"395":6,"157":7,"318":6,"640":11,"1284":9,"2572":7,"5148":9,"5152":3,"10299":5,"10300":4,"10301":3,"51497":1,"51498":1,"25744":2,"25745":2,"12869":3,"12870":3,"5147":3,"10297":2,"10298":5,"10302":1,"20598":3,"20599":3,"20600":2,"185390":1,"185391":1,"25747":1,"25748":1,"51494":1,"51495":1,"20597":1,"20601":1,"41197":1,"41198":2,"41199":1,"205989":1,"205990":1,"111":708,"112":704,"113":695,"114":664,"115":640,"116":618,"117":586,"118":573,"119":547,"120":436,"121":331,"122":242,"604":17,"605":17,"123":112,"241":150,"242":126,"243":82,"1207":17,"1208":17,"599":43,"600":43,"239":93,"240":154,"244":22,"482":88,"483":77,"484":51,"2414":7,"2415":7,"602":43,"603":43,"1204":22,"1205":22,"481":68,"485":19,"965":40,"966":33,"967":25,"4829":1,"4830":1,"2412":10,"2413":10,"1202":21,"1203":21,"597":25,"598":25,"238":25,"480":34,"964":38,"968":9,"1931":19,"1932":17,"1933":10,"9657":1,"9658":1,"4824":5,"4825":5,"2409":11,"2410":11,"963":22,"1929":14,"1930":21,"1934":1,"3862":11,"3863":9,"3864":6,"19312":1,"19313":1,"4827":6,"4828":6,"9652":3,"9653":3,"4822":4,"4823":4,"2407":4,"2408":4,"1199":4,"1200":4,"479":9,"962":7,"1928":5,"3860":5,"3861":10,"3865":2,"7724":6,"7725":5,"7726":3,"38624":1,"38625":1,"9654":3,"9655":3,"19309":2,"19310":2,"7723":4,"7727":1,"15449":2,"15450":2,"15451":2,"139042":1,"139043":1,"38619":1,"38620":1,"19307":1,"19308":1,"9649":1,"9650":1,"3859":1,"7722":1,"15447":1,"15448":2,"15452":1,"30898":1,"30899":2,"30900":1,"154491":1,"154492":1,"454":3,"455":7,"181":153,"182":113,"183":51,"907":2,"908":2,"449":43,"450":43,"179":123,"180":170,"184":6,"362":80,"363":61,"364":27,"1812":2,"1813":2,"452":44,"453":44,"902":21,"903":21,"447":40,"448":40,"178":40,"361":83,"365":4,"724":41,"725":32,"726":15,"3622":2,"3623":2,"904":22,"905":22,"1807":11,"1808":11,"899":19,"900":19,"722":29,"723":43,"727":2,"1448":21,"1449":17,"1450":11,"7242":2,"7243":2,"1809":11,"1810":11,"3617":5,"3618":5,"1804":8,"1805":8,"721":8,"1446":11,"1447":21,"1451":2,"2896":11,"2897":9,"2898":6,"14484":1,"14485":1,"3619":6,"3620":6,"7239":3,"7240":3,"2895":10,"2899":3,"5793":5,"5794":4,"5795":3,"28967":1,"28968":1,"14479":2,"14480":2,"7237":3,"7238":3,"3614":3,"3615":3,"1445":4,"2894":4,"5791":2,"5792":5,"5796":1,"11586":3,"11587":3,"11588":2,"104279":1,"104280":1,"14482":1,"14483":1,"28964":1,"28965":1,"11585":1,"11589":1,"23173":1,"23174":2,"23175":1,"115866":1,"115867":1,"339":36,"340":38,"135":163,"136":145,"137":103,"679":12,"680":12,"337":42,"338":42,"134":137,"138":38,"271":77,"272":66,"273":45,"1359":2,"1360":2,"677":22,"678":22,"334":43,"335":43,"133":61,"270":73,"274":15,"543":40,"544":29,"545":15,"2717":2,"2718":2,"1354":11,"1355":11,"674":21,"675":21,"269":40,"541":29,"542":44,"546":2,"1086":18,"1087":16,"1088":10,"5432":2,"5433":2,"1357":10,"1358":10,"2712":5,"2713":5,"1352":9,"1353":9,"672":9,"673":9,"332":9,"333":9,"132":9,"268":10,"540":12,"1084":15,"1085":21,"1089":2,"2172":9,"2173":8,"2174":7,"10862":2,"10863":2,"2714":5,"2715":5,"5427":3,"5428":3,"2709":4,"2710":4,"1083":5,"2170":6,"2171":9,"2175":3,"4344":5,"4345":5,"4346":4,"21724":1,"21725":1,"5429":2,"5430":2,"10859":1,"10860":1,"4343":3,"4347":2,"8689":3,"8690":3,"8691":2,"78207":1,"78208":1,"21722":1,"21723":1,"10857":1,"10858":1,"5424":1,"5425":1,"2169":2,"4342":1,"8688":1,"8692":1,"17379":1,"17380":2,"17381":1,"86897":1,"86898":1,"509":15,"510":15,"203":78,"204":69,"205":50,"1019":4,"1020":4,"507":21,"508":21,"202":70,"206":18,"407":40,"408":34,"409":19,"2037":4,"2038":4,"1014":10,"1015":10,"504":21,"505":21,"201":35,"405":27,"406":38,"410":4,"814":22,"815":19,"816":12,"4074":1,"4075":1,"1017":11,"1018":11,"2034":5,"2035":5,"813":19,"817":4,"1629":11,"1630":9,"1631":5,"8147":1,"8148":1,"4069":3,"4070":3,"2032":6,"2033":6,"1012":7,"1013":7,"502":7,"503":7,"200":8,"404":10,"812":9,"1627":6,"1628":11,"1632":1,"3258":6,"3259":5,"3260":3,"16294":1,"16295":1,"4072":3,"4073":3,"8144":2,"8145":2,"3257":4,"3261":1,"6517":2,"6518":3,"6519":3,"58654":1,"58655":1,"16289":1,"16290":1,"8142":1,"8143":1,"4067":1,"4068":1,"2029":1,"2030":1,"811":1,"1626":1,"3256":1,"6515":1,"6516":2,"6520":1,"13034":1,"13035":2,"13036":1,"65171":1,"65172":1,"152":82,"153":72,"154":50,"151":69,"155":18,"305":37,"306":32,"307":22,"377":21,"150":31,"303":21,"304":37,"308":7,"610":22,"611":19,"612":15,"3055":3,"609":16,"613":7,"1221":11,"1222":11,"1223":8,"6109":2,"6110":2,"757":5,"758":5,"374":5,"375":5,"149":5,"302":5,"608":7,"1220":8,"1224":3,"2443":5,"2444":5,"2445":4,"12219":1,"12220":1,"6107":1,"6108":1,"1219":3,"2442":3,"2446":2,"4887":4,"4888":4,"4889":2,"43988":1,"43989":1,"12217":1,"12218":1,"2441":1,"4886":1,"4890":1,"9775":1,"9776":2,"9777":1,"48876":1,"48877":1,"229":38,"230":29,"231":15,"1148":1,"227":29,"228":42,"232":2,"458":20,"459":16,"460":9,"2292":1,"2293":1,"567":9,"568":9,"226":9,"456":13,"457":21,"461":1,"916":10,"917":9,"918":6,"4582":1,"4583":1,"1139":4,"1140":4,"914":5,"915":10,"919":1,"1832":6,"1833":5,"1834":3,"9164":1,"9165":1,"1831":4,"1835":1,"3665":2,"3666":2,"3667":2,"32989":1,"32990":1,"9159":1,"9160":1,"2284":1,"913":2,"1830":1,"3663":2,"3664":3,"3668":1,"7330":1,"7331":2,"7332":1,"36654":1,"36655":1,"171":41,"172":37,"173":27,"170":33,"174":10,"343":20,"344":18,"345":13,"1720":1,"424":10,"425":10,"169":14,"342":18,"346":4,"687":10,"688":9,"689":5,"3437":1,"3438":1,"854":5,"341":9,"685":7,"686":9,"690":1,"1374":5,"1375":4,"1376":3,"6872":1,"6873":1,"1712":2,"852":2,"853":2,"422":2,"423":2,"168":2,"684":3,"1372":2,"1373":5,"1377":1,"2748":3,"2749":3,"2750":2,"24740":1,"24741":1,"6870":1,"2747":2,"2751":1,"5497":1,"5498":2,"5499":1,"27489":1,"27490":1,"128":41,"129":37,"130":28,"124":49,"125":45,"126":44,"127":43,"131":11,"257":21,"258":18,"259":12,"256":17,"260":4,"515":10,"516":8,"517":6,"2578":2,"639":5,"255":7,"513":6,"514":10,"518":2,"1030":5,"1031":5,"1032":4,"5154":1,"5155":1,"1029":3,"1033":2,"2061":3,"2062":3,"2063":2,"18554":1,"18555":1,"5153":1,"1282":1,"1283":1,"637":1,"638":1,"254":1,"512":2,"1028":1,"2060":1,"2064":1,"4123":1,"4124":2,"4125":1,"20616":1,"20617":1,"194":15,"195":9,"196":2,"386":9,"387":9,"388":7,"385":9,"389":2,"772":5,"773":5,"774":4,"771":3,"775":2,"1545":3,"1546":3,"1547":2,"13913":1,"13914":1,"1927":1,"959":1,"960":1,"770":1,"1544":1,"1548":1,"3091":1,"3092":2,"3093":1,"15459":1,"15460":1,"147":5,"290":9,"291":7,"292":3,"579":6,"580":5,"581":4,"2900":1,"719":3,"720":3,"578":4,"582":2,"1159":2,"1160":2,"1161":2,"10434":1,"10435":1,"1444":1,"577":1,"1157":1,"1158":2,"1162":1,"2318":1,"2319":2,"2320":1,"11593":1,"11594":1,"218":8,"219":5,"539":3,"220":1,"434":6,"435":5,"436":3,"433":4,"437":1,"869":2,"870":2,"871":2,"7824":1,"7825":1,"1082":1,"867":1,"868":2,"872":1,"1738":1,"1739":2,"1740":1,"8693":1,"8694":1,"164":7,"165":3,"325":5,"326":5,"327":4,"328":2,"651":3,"652":3,"653":2,"5866":1,"5867":1,"809":1,"810":1,"650":1,"654":1,"1303":1,"1304":2,"1305":1,"245":4,"246":3,"607":2,"247":1,"488":3,"489":3,"490":2,"4398":1,"4399":1,"487":1,"491":1,"977":1,"978":2,"979":1,"185":3,"186":1,"366":2,"367":2,"368":2,"3297":1,"3298":1,"912":1,"369":1,"732":1,"733":2,"734":1,"139":3,"275":3,"276":2,"2471":1,"2472":1,"277":1,"549":1,"550":2,"551":1,"2746":1,"207":2,"1851":1,"1852":1,"208":1,"411":1,"412":2,"413":1,"2057":1,"2058":1,"156":2,"1387":1,"1388":1,"309":2,"310":1,"1541":1,"1542":1,"1038":1,"1039":1,"1153":1,"1154":1,"777":1,"778":1,"863":1,"864":1,"647":1,"199":1},"product_classical":{"2,1":8808,"2,2":8808,"2,3":8808,"2,4":8808,"2,5":8808,"2,6":8808,"2,7":8808,"2,8":8808,"2,9":8808,"2,10":8808,"2,11":8808,"2,12":8808,"2,13":8808,"2,14":8808,"2,15":8808,"2,16":8808,"2,17":8808,"2,18":8808,"2,19":8808,"2,20":8808,"2,21":8808,"2,22":8808,"2,23":8808,"2,24":8808,"2,25":8808,"2,26":8808,"2,27":8808,"2,28":8808,"2,29":8808,"2,30":8808,"2,31":8808,"2,32":8808,"2,33":8808,"2,34":8808,"2,35":8808,"2,36":8808,"2,37":8808,"2,38":8808,"2,39":8808,"2,40":8807,"2,41":8806,"2,42":8806,"2,43":8806,"2,44":8806,"2,45":8806,"2,46":8806,"2,47":8806,"2,48":8806,"2,49":8806,"2,50":8806,"2,51":8806,"2,52":8806,"2,53":8806,"2,54":8805,"2,55":8804,"2,56":8804,"2,57":8804,"2,58":8804,"2,59":8804,"2,60":8804,"2,61":8804,"2,62":8804,"2,63":8794,"2,64":8783,"2,65":8773,"2,66":8668,"2,67":8535,"2,68":8445,"2,69":8152,"2,70":7564,"2,71":7196,"2,72":6843,"2,73":6319,"2,74":6097,"2,75":6027,"2,76":5982,"2,77":5933,"2,78":5782,"2,79":5506,"2,80":5326,"2,81":5144,"2,82":4889,"2,83":4799,"2,84":4773,"2,85":4742,"2,86":4720,"2,87":4688,"2,88":4627,"2,89":4499,"2,90":4408,"2,91":4320,"2,92":4189,"2,93":3924,"2,94":3406,"2,95":3051,"2,96":2653,"2,97":2174,"2,191":256,"2,192":127,"2,190":130,"2,382":126,"2,383":40,"2,381":88,"2,763":64,"2,764":40,"2,1526":32,"2,1527":19,"2,762":24,"2,3052":16,"2,3053":8,"2,1525":13,"2,3051":8,"2,6104":8,"2,6105":3,"2,6103":5,"2,12207":4,"2,12208":3,"2,380":2,"2,24414":2,"2,24415":2,"2,12206":1,"2,48828":1,"2,48829":1,"2,144":183,"2,145":17,"2,143":247,"2,287":94,"2,288":9,"2,142":76,"2,286":119,"2,573":52,"2,574":9,"2,285":34,"2,572":55,"2,1145":30,"2,1146":9,"2,1144":23,"2,2289":16,"2,2290":9,"2,571":12,"2,4578":8,"2,4579":4,"2,2288":7,"2,4577":4,"2,9156":4,"2,9157":1,"2,1143":2,"2,9155":3,"2,18311":2,"2,18312":1,"2,18310":1,"2,36621":1,"2,36622":1,"2,98":2031,"2,99":2017,"2,100":1968,"2,101":1910,"2,102":1865,"2,103":1800,"2,104":1762,"2,105":1639,"2,106":1382,"2,107":1204,"2,108":990,"2,109":765,"2,215":128,"2,216":49,"2,214":79,"2,430":49,"2,431":7,"2,429":57,"2,859":28,"2,860":7,"2,858":25,"2,1717":16,"2,1718":7,"2,428":15,"2,1716":9,"2,3434":7,"2,3435":1,"2,857":4,"2,3433":7,"2,6867":4,"2,6868":1,"2,6866":3,"2,13733":2,"2,13734":1,"2,3432":1,"2,13732":1,"2,27466":1,"2,27467":1,"2,161":128,"2,162":81,"2,322":64,"2,323":37,"2,160":48,"2,644":32,"2,645":16,"2,321":27,"2,643":16,"2,1288":16,"2,1289":5,"2,1287":11,"2,2575":8,"2,2576":5,"2,5150":4,"2,5151":2,"2,2574":3,"2,5149":2,"2,10300":2,"2,10301":1,"2,10299":1,"2,20599":1,"2,20600":1,"2,110":708,"2,111":704,"2,112":695,"2,113":664,"2,114":640,"2,115":618,"2,116":586,"2,117":573,"2,118":547,"2,119":436,"2,120":331,"2,121":242,"2,122":112,"2,242":60,"2,243":17,"2,241":47,"2,483":32,"2,484":17,"2,966":16,"2,967":7,"2,482":15,"2,965":9,"2,1932":7,"2,1933":1,"2,240":4,"2,1931":7,"2,3863":4,"2,3864":1,"2,3862":3,"2,7725":2,"2,7726":1,"2,1930":1,"2,7724":1,"2,15450":1,"2,15451":1,"2,182":45,"2,183":3,"2,181":62,"2,363":24,"2,364":2,"2,180":19,"2,362":30,"2,725":13,"2,726":2,"2,361":8,"2,724":14,"2,1449":8,"2,1450":2,"2,1448":6,"2,2897":4,"2,2898":2,"2,723":3,"2,2896":2,"2,5794":2,"2,5795":1,"2,5793":1,"2,11587":1,"2,11588":1,"2,136":64,"2,137":35,"2,272":32,"2,273":12,"2,135":30,"2,271":20,"2,544":12,"2,545":2,"2,543":14,"2,1087":7,"2,1088":2,"2,542":4,"2,1086":6,"2,2173":4,"2,2174":2,"2,2172":2,"2,4345":2,"2,4346":2,"2,1085":1,"2,8690":1,"2,8691":1,"2,204":32,"2,205":15,"2,203":17,"2,408":15,"2,409":4,"2,407":12,"2,815":8,"2,816":4,"2,814":4,"2,1630":4,"2,1631":1,"2,1629":3,"2,3259":2,"2,3260":1,"2,406":1,"2,3258":1,"2,6518":1,"2,6519":1,"2,153":32,"2,154":16,"2,152":16,"2,306":16,"2,307":6,"2,305":10,"2,611":8,"2,612":6,"2,1222":4,"2,1223":3,"2,610":2,"2,2444":2,"2,2445":2,"2,1221":1,"2,4888":1,"2,4889":1,"2,230":12,"2,231":1,"2,229":15,"2,459":7,"2,460":1,"2,228":4,"2,458":7,"2,917":4,"2,918":1,"2,916":3,"2,1833":2,"2,1834":1,"2,457":1,"2,1832":1,"2,3666":1,"2,3667":1,"2,172":16,"2,173":9,"2,344":8,"2,345":4,"2,171":7,"2,343":4,"2,688":4,"2,689":1,"2,687":3,"2,1375":2,"2,1376":1,"2,1374":1,"2,2749":1,"2,2750":1,"2,123":49,"2,124":45,"2,125":44,"2,126":43,"2,127":31,"2,128":16,"2,129":16,"2,130":10,"2,258":8,"2,259":4,"2,257":4,"2,516":4,"2,517":2,"2,515":2,"2,1031":2,"2,1032":2,"2,2062":1,"2,2063":1,"2,194":7,"2,195":2,"2,193":6,"2,387":4,"2,388":2,"2,386":2,"2,773":2,"2,774":2,"2,1546":1,"2,1547":1,"2,146":5,"2,290":4,"2,291":3,"2,580":2,"2,581":1,"2,289":1,"2,579":1,"2,1160":1,"2,1161":1,"2,218":4,"2,219":1,"2,217":3,"2,435":2,"2,436":1,"2,434":1,"2,870":1,"2,871":1,"2,163":4,"2,164":3,"2,326":2,"2,327":2,"2,652":1,"2,653":1,"2,245":2,"2,246":1,"2,244":1,"2,489":1,"2,490":1,"2,184":2,"2,185":1,"2,367":1,"2,368":1,"2,138":2,"2,139":1,"2,275":1,"2,276":1,"2,206":1,"2,207":1,"2,155":1,"2,156":1,"39,161":1,"40,160":1,"40,161":1,"41,160":1},"product_ntt":{"95,383":130,"96,382":130,"96,383":130,"97,382":130,"93,96":687,"94,97":611,"93,97":301,"94,98":135,"94,96":691,"95,97":317,"95,98":147,"190,765":40,"191,764":40,"191,765":40,"192,764":40,"94,381":170,"95,380":170,"95,381":170,"96,380":170,"93,95":431,"94,95":215,"95,96":175,"189,191":341,"190,192":252,"189,192":342,"190,193":130,"190,191":125,"191,192":41,"191,193":47,"381,1527":40,"382,1526":40,"382,1527":40,"383,1526":40,"189,761":85,"190,760":85,"190,761":85,"191,760":85,"94,379":171,"95,378":171,"95,379":171,"96,378":171,"92,95":216,"92,96":171,"188,190":130,"188,191":261,"189,190":85,"379,382":171,"380,383":166,"379,383":83,"380,384":40,"380,382":171,"381,383":83,"381,384":40,"762,3053":19,"763,3052":19,"763,3053":19,"764,3052":19,"190,763":86,"191,762":86,"191,763":86,"192,762":86,"188,192":131,"189,193":86,"380,1525":43,"381,1524":43,"381,1525":43,"382,1524":43,"379,381":90,"380,381":45,"381,382":43,"761,763":86,"762,764":81,"761,764":85,"762,765":40,"762,763":41,"763,764":19,"763,765":19,"1525,6105":8,"1526,6104":8,"1526,6105":8,"1527,6104":8,"762,3051":21,"763,3050":21,"763,3051":21,"764,3050":21,"380,1523":43,"381,1522":43,"381,1523":43,"382,1522":43,"189,759":45,"190,758":45,"190,759":45,"191,758":45,"93,377":45,"94,376":45,"94,377":45,"95,376":45,"92,94":46,"93,94":45,"187,190":45,"187,191":45,"378,381":45,"378,382":43,"760,763":47,"760,764":23,"761,765":21,"1524,1526":43,"1525,1527":38,"1524,1527":43,"1525,1528":19,"1525,1526":19,"1526,1527":8,"1526,1528":8,"3051,12209":3,"3052,12208":3,"3052,12209":3,"3053,12208":3,"1525,6103":11,"1526,6102":11,"1526,6103":11,"1527,6102":11,"761,3049":22,"762,3048":22,"762,3049":22,"763,3048":22,"760,762":24,"761,762":22,"1523,1526":26,"1523,1527":13,"1524,1528":11,"3050,3052":22,"3051,3053":17,"3050,3053":21,"3051,3054":8,"3051,3052":9,"3052,3053":3,"3052,3054":3,"6103,24415":3,"6104,24414":3,"6104,24415":3,"6105,24414":3,"3050,12205":6,"3051,12204":6,"3051,12205":6,"3052,12204":6,"1524,6101":11,"1525,6100":11,"1525,6101":11,"1526,6100":11,"1523,1525":13,"1524,1525":11,"3049,3051":8,"3049,3052":15,"3050,3051":6,"6101,6104":10,"6102,6105":11,"6101,6105":5,"6102,6106":3,"6102,6104":11,"6103,6105":6,"6103,6106":3,"12206,48829":2,"12207,48828":2,"12207,48829":2,"12208,48828":2,"3051,12207":5,"3052,12206":5,"3052,12207":5,"3053,12206":5,"3049,3053":7,"3050,3054":5,"6102,24413":3,"6103,24412":3,"6103,24413":3,"6104,24412":3,"6101,6103":5,"6102,6103":3,"6103,6104":3,"12205,12207":5,"12206,12208":6,"12205,12208":5,"12206,12209":3,"12206,12207":3,"12207,12208":2,"12207,12209":2,"24413,97657":1,"24414,97656":1,"24414,97657":1,"24415,97656":1,"12206,48827":1,"12207,48826":1,"12207,48827":1,"12208,48826":1,"6102,24411":2,"6103,24410":2,"6103,24411":2,"6104,24410":2,"3050,12203":2,"3051,12202":2,"3051,12203":2,"3052,12202":2,"1524,6099":2,"1525,6098":2,"1525,6099":2,"1526,6098":2,"761,3047":2,"762,3046":2,"762,3047":2,"763,3046":2,"379,1521":2,"380,1520":2,"380,1521":2,"381,1520":2,"378,380":2,"379,380":2,"759,762":2,"759,763":2,"1522,1525":2,"1522,1526":2,"3048,3051":2,"3048,3052":2,"6100,6103":2,"6100,6104":2,"12204,12207":2,"12204,12208":1,"12205,12209":1,"24412,24414":2,"24413,24415":3,"24412,24415":3,"24413,24416":2,"24413,24414":1,"24414,24415":1,"24414,24416":1,"48827,390625":1,"48828,390624":1,"48828,390625":1,"48829,390624":1,"24413,97655":1,"24414,97654":1,"24414,97655":1,"24415,97654":1,"12205,48825":1,"12206,48824":1,"12206,48825":1,"12207,48824":1,"12204,12206":1,"12205,12206":1,"24411,24414":1,"24411,24415":1,"24412,24416":1,"48826,48828":1,"48827,48829":2,"48826,48829":1,"48827,48830":1,"48827,48828":1,"48828,48829":1,"48828,48830":1,"97655,390625":1,"97656,390624":1,"97656,390625":1,"97657,390624":1,"71,289":16,"72,288":16,"72,289":16,"73,288":16,"70,72":693,"71,73":381,"70,73":704,"71,74":201,"71,72":185,"72,73":15,"72,74":20,"143,575":9,"144,574":9,"144,575":9,"145,574":9,"70,285":170,"71,284":170,"71,285":170,"72,284":170,"69,71":333,"69,72":670,"70,71":170,"141,144":342,"142,145":194,"141,145":95,"142,146":11,"142,144":344,"143,145":105,"143,146":19,"286,1147":9,"287,1146":9,"287,1147":9,"288,1146":9,"71,287":176,"72,286":176,"72,287":176,"73,286":176,"69,73":338,"70,74":181,"142,571":86,"143,570":86,"143,571":86,"144,570":86,"70,283":162,"71,282":162,"71,283":162,"72,282":162,"68,71":164,"68,72":162,"140,143":162,"140,144":86,"141,143":323,"284,287":170,"285,288":103,"284,288":51,"285,289":9,"285,287":171,"286,288":52,"286,289":9,"572,2291":9,"573,2290":9,"573,2291":9,"574,2290":9,"142,573":85,"143,572":85,"143,573":85,"144,572":85,"142,143":161,"143,144":88,"285,1143":42,"286,1142":42,"286,1143":42,"287,1142":42,"141,569":76,"142,568":76,"142,569":76,"143,568":76,"140,142":76,"141,142":76,"283,286":76,"283,287":42,"284,286":153,"570,573":86,"571,574":61,"570,574":31,"571,575":9,"571,573":85,"572,574":30,"572,575":9,"1144,4579":9,"1145,4578":9,"1145,4579":9,"1146,4578":9,"285,1145":43,"286,1144":43,"286,1145":43,"287,1144":43,"285,286":77,"286,287":43,"571,2287":22,"572,2286":22,"572,2287":22,"573,2286":22,"284,1141":34,"285,1140":34,"285,1141":34,"286,1140":34,"283,285":34,"284,285":34,"569,572":34,"569,573":22,"570,572":67,"1142,1145":42,"1143,1146":39,"1142,1146":19,"1143,1147":9,"1143,1145":43,"1144,1146":20,"1144,1147":9,"2288,9157":4,"2289,9156":4,"2289,9157":4,"2290,9156":4,"571,2289":21,"572,2288":21,"572,2289":21,"573,2288":21,"571,572":33,"572,573":21,"1143,4577":11,"1144,4576":11,"1144,4577":11,"1145,4576":11,"1142,1144":25,"1143,1144":13,"1144,1145":11,"2287,2289":21,"2288,2290":18,"2287,2290":21,"2288,2291":9,"2288,2289":9,"2289,2290":4,"2289,2291":4,"4577,18313":1,"4578,18312":1,"4578,18313":1,"4579,18312":1,"2288,9155":5,"2289,9154":5,"2289,9155":5,"2290,9154":5,"1143,4575":10,"1144,4574":10,"1144,4575":10,"1145,4574":10,"570,2285":12,"571,2284":12,"571,2285":12,"572,2284":12,"569,571":12,"570,571":12,"1141,1144":12,"1141,1145":10,"2286,2289":14,"2286,2290":7,"2287,2291":5,"4576,4578":10,"4577,4579":7,"4576,4579":11,"4577,4580":4,"4577,4578":3,"4578,4579":1,"4578,4580":1,"9155,36623":1,"9156,36622":1,"9156,36623":1,"9157,36622":1,"4576,18309":2,"4577,18308":2,"4577,18309":2,"4578,18308":2,"2287,9153":5,"2288,9152":5,"2288,9153":5,"2289,9152":5,"2286,2288":7,"2287,2288":5,"4575,4577":4,"4575,4578":9,"4576,4577":2,"9153,9156":6,"9154,9157":5,"9153,9157":3,"9154,9158":1,"9154,9156":5,"9155,9157":2,"9155,9158":1,"18310,73243":1,"18311,73242":1,"18311,73243":1,"18312,73242":1,"4577,18311":3,"4578,18310":3,"4578,18311":3,"4579,18310":3,"4575,4579":5,"4576,4580":3,"9154,36619":2,"9155,36618":2,"9155,36619":2,"9156,36618":2,"4576,18307":2,"4577,18306":2,"4577,18307":2,"4578,18306":2,"2287,9151":2,"2288,9150":2,"2288,9151":2,"2289,9150":2,"1142,4573":2,"1143,4572":2,"1143,4573":2,"1144,4572":2,"1141,1143":2,"1142,1143":2,"2285,2288":2,"2285,2289":2,"4574,4577":2,"4574,4578":2,"9152,9155":2,"9152,9156":2,"9153,9155":3,"18308,18311":2,"18309,18312":3,"18308,18312":1,"18309,18313":1,"18309,18311":3,"18310,18312":2,"18310,18313":1,"36620,292968":1,"36621,292967":1,"36621,292968":1,"36622,292967":1,"9154,36621":1,"9155,36620":1,"9155,36621":1,"9156,36620":1,"9154,9155":1,"9155,9156":1,"18309,73241":1,"18310,73240":1,"18310,73241":1,"18311,73240":1,"18308,18310":1,"18309,18310":1,"18310,18311":1,"36619,36621":1,"36620,36622":2,"36619,36622":1,"36620,36623":1,"36620,36621":1,"36621,36622":1,"36621,36623":1,"73241,292968":1,"73242,292967":1,"73242,292968":1,"73243,292967":1,"107,431":50,"108,430":50,"108,431":50,"109,430":50,"105,108":342,"106,109":277,"105,109":135,"106,110":53,"106,108":346,"107,109":146,"107,110":60,"214,861":7,"215,860":7,"215,861":7,"216,860":7,"106,429":86,"107,428":86,"107,429":86,"108,428":86,"105,107":243,"106,107":122,"107,108":89,"213,215":171,"214,216":99,"213,216":170,"214,217":50,"214,215":50,"215,216":7,"215,217":10,"429,1719":7,"430,1718":7,"430,1719":7,"431,1718":7,"213,857":43,"214,856":43,"214,857":43,"215,856":43,"106,427":85,"107,426":85,"107,427":85,"108,426":85,"104,107":121,"104,108":85,"212,214":79,"212,215":157,"213,214":43,"427,430":85,"428,431":56,"427,431":28,"428,432":7,"428,430":85,"429,431":28,"429,432":7,"858,3435":7,"859,3434":7,"859,3435":7,"860,3434":7,"214,859":42,"215,858":42,"215,859":42,"216,858":42,"212,216":78,"213,217":42,"428,1715":21,"429,1714":21,"429,1715":21,"430,1714":21,"213,855":36,"214,854":36,"214,855":36,"215,854":36,"105,425":36,"106,424":36,"106,425":36,"107,424":36,"104,106":36,"105,106":36,"211,214":36,"211,215":36,"426,429":36,"426,430":21,"427,429":72,"856,859":43,"857,860":35,"856,860":18,"857,861":7,"857,859":42,"858,860":17,"858,861":7,"1716,6869":1,"1717,6868":1,"1717,6869":1,"1718,6868":1,"428,1717":21,"429,1716":21,"429,1717":21,"430,1716":21,"428,429":36,"429,430":21,"857,3433":10,"858,3432":10,"858,3433":10,"859,3432":10,"856,858":29,"857,858":14,"858,859":10,"1715,1717":21,"1716,1718":13,"1715,1718":22,"1716,1719":7,"1716,1717":6,"1717,1718":1,"1717,1719":1,"3433,13735":1,"3434,13734":1,"3434,13735":1,"3435,13734":1,"1715,6865":5,"1716,6864":5,"1716,6865":5,"1717,6864":5,"857,3431":11,"858,3430":11,"858,3431":11,"859,3430":11,"427,1713":15,"428,1712":15,"428,1713":15,"429,1712":15,"426,428":15,"427,428":15,"855,858":15,"855,859":11,"1714,1716":9,"1714,1717":19,"1715,1716":5,"3431,3434":11,"3432,3435":8,"3431,3435":4,"3432,3436":1,"3432,3434":11,"3433,3435":4,"3433,3436":1,"6866,27467":1,"6867,27466":1,"6867,27467":1,"6868,27466":1,"1716,6867":6,"1717,6866":6,"1717,6867":6,"1718,6866":6,"1714,1718":10,"1715,1719":6,"3432,13731":3,"3433,13730":3,"3433,13731":3,"3434,13730":3,"1715,6863":4,"1716,6862":4,"1716,6863":4,"1717,6862":4,"856,3429":4,"857,3428":4,"857,3429":4,"858,3428":4,"855,857":4,"856,857":4,"1713,1716":4,"1713,1717":4,"3430,3433":4,"3430,3434":3,"3431,3433":8,"6864,6867":5,"6865,6868":5,"6864,6868":2,"6865,6869":1,"6865,6867":6,"6866,6868":3,"6866,6869":1,"13732,54933":1,"13733,54932":1,"13733,54933":1,"13734,54932":1,"3432,13733":3,"3433,13732":3,"3433,13733":3,"3434,13732":3,"3432,3433":4,"3433,3434":3,"6865,27465":2,"6866,27464":2,"6866,27465":2,"6867,27464":2,"6864,6866":3,"6865,6866":2,"6866,6867":2,"13731,13733":3,"13732,13734":3,"13731,13734":2,"13732,13735":1,"13732,13733":2,"13733,13734":1,"13733,13735":1,"27465,219725":1,"27466,219724":1,"27466,219725":1,"27467,219724":1,"13731,54929":1,"13732,54928":1,"13732,54929":1,"13733,54928":1,"6865,27463":1,"6866,27462":1,"6866,27463":1,"6867,27462":1,"3431,13729":1,"3432,13728":1,"3432,13729":1,"3433,13728":1,"3430,3432":1,"3431,3432":1,"6863,6866":1,"6863,6867":1,"13730,13732":1,"13730,13733":1,"13731,13732":1,"27463,27466":1,"27464,27467":2,"27463,27467":1,"27464,27468":1,"27464,27466":1,"27465,27467":1,"27465,27468":1,"54930,219725":1,"54931,219724":1,"54931,219725":1,"54932,219724":1,"80,323":82,"81,322":82,"81,323":82,"82,322":82,"78,81":343,"79,82":340,"78,82":167,"79,83":85,"79,81":346,"80,82":176,"80,83":91,"160,645":37,"161,644":37,"161,645":37,"162,644":37,"79,321":85,"80,320":85,"80,321":85,"81,320":85,"78,80":182,"79,80":91,"80,81":88,"159,161":170,"160,162":160,"159,162":171,"160,163":82,"160,161":79,"161,162":38,"161,163":42,"321,1289":16,"322,1288":16,"322,1289":16,"323,1288":16,"160,643":43,"161,642":43,"161,643":43,"162,642":43,"79,319":85,"80,318":85,"80,319":85,"81,318":85,"77,80":92,"77,81":85,"158,161":97,"158,162":49,"159,163":43,"320,322":85,"321,323":74,"320,323":85,"321,324":37,"321,322":37,"322,323":16,"322,324":16,"643,2577":5,"644,2576":5,"644,2577":5,"645,2576":5,"321,1287":21,"322,1286":21,"322,1287":21,"323,1286":21,"159,641":42,"160,640":42,"160,641":42,"161,640":42,"158,160":48,"159,160":42,"319,322":54,"319,323":27,"320,324":21,"642,644":42,"643,645":31,"642,645":43,"643,646":16,"643,644":15,"644,645":5,"644,646":5,"1287,5151":5,"1288,5150":5,"1288,5151":5,"1289,5150":5,"642,2573":10,"643,2572":10,"643,2573":10,"644,2572":10,"320,1285":21,"321,1284":21,"321,1285":21,"322,1284":21,"319,321":27,"320,321":21,"641,643":16,"641,644":33,"642,643":10,"1285,1288":22,"1286,1289":21,"1285,1289":11,"1286,1290":5,"1286,1288":21,"1287,1289":10,"1287,1290":5,"2574,10301":2,"2575,10300":2,"2575,10301":2,"2576,10300":2,"643,2575":11,"644,2574":11,"644,2575":11,"645,2574":11,"641,645":17,"642,646":11,"1286,5149":5,"1287,5148":5,"1287,5149":5,"1288,5148":5,"1285,1287":11,"1286,1287":5,"1287,1288":5,"2573,2575":11,"2574,2576":10,"2573,2576":11,"2574,2577":5,"2574,2575":5,"2575,2576":2,"2575,2577":2,"5149,20601":1,"5150,20600":1,"5150,20601":1,"5151,20600":1,"2574,10299":3,"2575,10298":3,"2575,10299":3,"2576,10298":3,"1286,5147":6,"1287,5146":6,"1287,5147":6,"1288,5146":6,"642,2571":6,"643,2570":6,"643,2571":6,"644,2570":6,"320,1283":6,"321,1282":6,"321,1283":6,"322,1282":6,"159,639":6,"160,638":6,"160,639":6,"161,638":6,"78,317":6,"79,316":6,"79,317":6,"80,316":6,"77,79":7,"78,79":6,"157,160":6,"157,161":6,"318,321":6,"318,322":6,"640,643":6,"640,644":6,"1284,1287":6,"1284,1288":6,"2572,2575":6,"2572,2576":3,"2573,2577":3,"5148,5150":6,"5149,5151":5,"5148,5151":5,"5149,5152":2,"5149,5150":3,"5150,5151":1,"5150,5152":1,"10299,41199":1,"10300,41198":1,"10300,41199":1,"10301,41198":1,"5148,20597":2,"5149,20596":2,"5149,20597":2,"5150,20596":2,"2573,10297":3,"2574,10296":3,"2574,10297":3,"2575,10296":3,"2572,2574":3,"2573,2574":3,"5147,5149":2,"5147,5150":3,"5148,5149":2,"10297,10300":2,"10298,10301":3,"10297,10301":1,"10298,10302":1,"10298,10300":3,"10299,10301":2,"10299,10302":1,"20598,164793":1,"20599,164792":1,"20599,164793":1,"20600,164792":1,"5149,20599":1,"5150,20598":1,"5150,20599":1,"5151,20598":1,"5147,5151":1,"5148,5152":1,"10298,41197":1,"10299,41196":1,"10299,41197":1,"10300,41196":1,"10297,10299":1,"10298,10299":1,"10299,10300":1,"20597,20599":1,"20598,20600":2,"20597,20600":1,"20598,20601":1,"20598,20599":1,"20599,20600":1,"20599,20601":1,"41197,164793":1,"41198,164792":1,"41198,164793":1,"41199,164792":1,"120,485":17,"121,484":17,"121,485":17,"122,484":17,"119,121":171,"120,122":123,"119,122":173,"120,123":66,"120,121":60,"121,122":18,"121,123":22,"241,967":17,"242,966":17,"242,967":17,"243,966":17,"119,481":43,"120,480":43,"120,481":43,"121,480":43,"118,120":68,"118,121":136,"119,120":43,"239,242":85,"240,243":77,"239,243":38,"240,244":17,"240,242":86,"241,243":39,"241,244":17,"482,1933":7,"483,1932":7,"483,1933":7,"484,1932":7,"120,483":43,"121,482":43,"121,483":43,"122,482":43,"118,122":68,"119,123":45,"240,965":22,"241,964":22,"241,965":22,"242,964":22,"239,241":51,"240,241":26,"241,242":22,"481,483":43,"482,484":35,"481,484":42,"482,485":17,"482,483":18,"483,484":7,"483,485":7,"965,3865":1,"966,3864":1,"966,3865":1,"967,3864":1,"482,1931":10,"483,1930":10,"483,1931":10,"484,1930":10,"240,963":21,"241,962":21,"241,963":21,"242,962":21,"119,479":25,"120,478":25,"120,479":25,"121,478":25,"117,120":25,"117,121":25,"238,241":25,"238,242":21,"480,483":29,"480,484":14,"481,485":10,"964,966":21,"965,967":13,"964,967":22,"965,968":7,"965,966":6,"966,967":1,"966,968":1,"1931,7727":1,"1932,7726":1,"1932,7727":1,"1933,7726":1,"964,3861":5,"965,3860":5,"965,3861":5,"966,3860":5,"481,1929":11,"482,1928":11,"482,1929":11,"483,1928":11,"480,482":15,"481,482":11,"963,965":9,"963,966":19,"964,965":5,"1929,1932":11,"1930,1933":8,"1929,1933":4,"1930,1934":1,"1930,1932":11,"1931,1933":4,"1931,1934":1,"3862,15451":1,"3863,15450":1,"3863,15451":1,"3864,15450":1,"965,3863":6,"966,3862":6,"966,3863":6,"967,3862":6,"963,967":10,"964,968":6,"1930,7723":3,"1931,7722":3,"1931,7723":3,"1932,7722":3,"964,3859":4,"965,3858":4,"965,3859":4,"966,3858":4,"481,1927":4,"482,1926":4,"482,1927":4,"483,1926":4,"239,961":4,"240,960":4,"240,961":4,"241,960":4,"238,240":4,"239,240":4,"479,482":4,"479,483":4,"962,965":4,"962,966":4,"1928,1931":4,"1928,1932":3,"1929,1931":8,"3860,3863":5,"3861,3864":5,"3860,3864":2,"3861,3865":1,"3861,3863":6,"3862,3864":3,"3862,3865":1,"7724,30901":1,"7725,30900":1,"7725,30901":1,"7726,30900":1,"1930,7725":3,"1931,7724":3,"1931,7725":3,"1932,7724":3,"1930,1931":4,"1931,1932":3,"3861,15449":2,"3862,15448":2,"3862,15449":2,"3863,15448":2,"3860,3862":3,"3861,3862":2,"3862,3863":2,"7723,7725":3,"7724,7726":3,"7723,7726":2,"7724,7727":1,"7724,7725":2,"7725,7726":1,"7725,7727":1,"15449,123594":1,"15450,123593":1,"15450,123594":1,"15451,123593":1,"7723,30897":1,"7724,30896":1,"7724,30897":1,"7725,30896":1,"3861,15447":1,"3862,15446":1,"3862,15447":1,"3863,15446":1,"1929,7721":1,"1930,7720":1,"1930,7721":1,"1931,7720":1,"1928,1930":1,"1929,1930":1,"3859,3862":1,"3859,3863":1,"7722,7724":1,"7722,7725":1,"7723,7724":1,"15447,15450":1,"15448,15451":2,"15447,15451":1,"15448,15452":1,"15448,15450":1,"15449,15451":1,"15449,15452":1,"30898,123594":1,"30899,123593":1,"30899,123594":1,"30900,123593":1,"90,365":3,"91,364":3,"91,365":3,"92,364":3,"89,91":173,"90,92":95,"89,92":175,"90,93":50,"90,91":46,"91,92":4,"91,93":6,"181,727":2,"182,726":2,"182,727":2,"183,726":2,"89,361":43,"90,360":43,"90,361":43,"91,360":43,"88,90":83,"88,91":167,"89,90":43,"179,182":85,"180,183":48,"179,183":23,"180,184":3,"180,182":86,"181,183":25,"181,184":5,"362,1451":2,"363,1450":2,"363,1451":2,"364,1450":2,"90,363":44,"91,362":44,"91,363":44,"92,362":44,"88,92":84,"89,93":45,"180,723":21,"181,722":21,"181,723":21,"182,722":21,"89,359":40,"90,358":40,"90,359":40,"91,358":40,"87,90":40,"87,91":40,"178,181":40,"178,182":21,"179,181":81,"360,363":43,"361,364":26,"360,364":13,"361,365":2,"361,363":43,"362,364":13,"362,365":2,"724,2899":2,"725,2898":2,"725,2899":2,"726,2898":2,"180,725":22,"181,724":22,"181,725":22,"182,724":22,"180,181":41,"181,182":22,"361,1447":11,"362,1446":11,"362,1447":11,"363,1446":11,"179,721":19,"180,720":19,"180,721":19,"181,720":19,"178,180":19,"179,180":19,"359,362":19,"359,363":11,"360,362":38,"722,725":21,"723,726":15,"722,726":7,"723,727":2,"723,725":22,"724,726":8,"724,727":2,"1448,5795":2,"1449,5794":2,"1449,5795":2,"1450,5794":2,"361,1449":11,"362,1448":11,"362,1449":11,"363,1448":11,"361,362":19,"362,363":11,"723,2895":5,"724,2894":5,"724,2895":5,"725,2894":5,"360,1445":8,"361,1444":8,"361,1445":8,"362,1444":8,"359,361":8,"360,361":8,"721,724":8,"721,725":5,"722,724":17,"1446,1449":11,"1447,1450":10,"1446,1450":5,"1447,1451":2,"1447,1449":11,"1448,1450":5,"1448,1451":2,"2896,11589":1,"2897,11588":1,"2897,11589":1,"2898,11588":1,"723,2897":6,"724,2896":6,"724,2897":6,"725,2896":6,"723,724":9,"724,725":6,"1447,5793":3,"1448,5792":3,"1448,5793":3,"1449,5792":3,"1446,1448":6,"1447,1448":3,"1448,1449":3,"2895,2897":6,"2896,2898":5,"2895,2898":5,"2896,2899":2,"2896,2897":3,"2897,2898":1,"2897,2899":1,"5793,23175":1,"5794,23174":1,"5794,23175":1,"5795,23174":1,"2895,11585":2,"2896,11584":2,"2896,11585":2,"2897,11584":2,"1447,5791":3,"1448,5790":3,"1448,5791":3,"1449,5790":3,"722,2893":3,"723,2892":3,"723,2893":3,"724,2892":3,"721,723":3,"722,723":3,"1445,1448":3,"1445,1449":3,"2894,2896":2,"2894,2897":3,"2895,2896":2,"5791,5794":2,"5792,5795":3,"5791,5795":1,"5792,5796":1,"5792,5794":3,"5793,5795":2,"5793,5796":1,"11586,92694":1,"11587,92693":1,"11587,92694":1,"11588,92693":1,"2896,11587":1,"2897,11586":1,"2897,11587":1,"2898,11586":1,"2894,2898":1,"2895,2899":1,"5792,23173":1,"5793,23172":1,"5793,23173":1,"5794,23172":1,"5791,5793":1,"5792,5793":1,"5793,5794":1,"11585,11587":1,"11586,11588":2,"11585,11588":1,"11586,11589":1,"11586,11587":1,"11587,11588":1,"11587,11589":1,"23173,92694":1,"23174,92693":1,"23174,92694":1,"23175,92693":1,"67,273":36,"68,272":36,"68,273":36,"69,272":36,"66,68":173,"67,69":159,"66,69":173,"67,70":81,"67,68":79,"68,69":37,"68,70":39,"135,545":12,"136,544":12,"136,545":12,"137,544":12,"67,271":42,"68,270":42,"68,271":42,"69,270":42,"65,68":103,"65,69":51,"66,70":43,"134,136":85,"135,137":68,"134,137":86,"135,138":36,"135,136":33,"136,137":13,"136,138":15,"271,1089":2,"272,1088":2,"272,1089":2,"273,1088":2,"135,543":22,"136,542":22,"136,543":22,"137,542":22,"66,269":43,"67,268":43,"67,269":43,"68,268":43,"65,67":53,"66,67":43,"133,136":61,"133,137":31,"134,138":22,"270,272":43,"271,273":25,"270,273":42,"271,274":12,"271,272":13,"272,273":2,"272,274":2,"543,2175":2,"544,2174":2,"544,2175":2,"545,2174":2,"270,1085":11,"271,1084":11,"271,1085":11,"272,1084":11,"134,541":21,"135,540":21,"135,541":21,"136,540":21,"133,135":30,"134,135":21,"269,271":20,"269,272":39,"270,271":11,"541,544":21,"542,545":14,"541,545":7,"542,546":2,"542,544":21,"543,545":7,"543,546":2,"1086,4347":2,"1087,4346":2,"1087,4347":2,"1088,4346":2,"271,1087":10,"272,1086":10,"272,1087":10,"273,1086":10,"269,273":19,"270,274":10,"542,2171":5,"543,2170":5,"543,2171":5,"544,2170":5,"270,1083":9,"271,1082":9,"271,1083":9,"272,1082":9,"134,539":9,"135,538":9,"135,539":9,"136,538":9,"66,267":9,"67,266":9,"67,267":9,"68,266":9,"64,67":20,"64,68":9,"132,135":9,"132,136":9,"268,271":9,"268,272":9,"540,543":9,"540,544":5,"541,543":18,"1084,1087":11,"1085,1088":9,"1084,1088":5,"1085,1089":2,"1085,1087":10,"1086,1088":4,"1086,1089":2,"2172,8691":2,"2173,8690":2,"2173,8691":2,"2174,8690":2,"542,2173":5,"543,2172":5,"543,2173":5,"544,2172":5,"542,543":9,"543,544":5,"1085,4343":3,"1086,4342":3,"1086,4343":3,"1087,4342":3,"541,2169":4,"542,2168":4,"542,2169":4,"543,2168":4,"540,542":4,"541,542":4,"1083,1086":4,"1083,1087":3,"1084,1086":7,"2170,2173":5,"2171,2174":6,"2170,2174":3,"2171,2175":2,"2171,2173":5,"2172,2174":3,"2172,2175":2,"4344,17381":1,"4345,17380":1,"4345,17381":1,"4346,17380":1,"1085,4345":2,"1086,4344":2,"1086,4345":2,"1087,4344":2,"1085,1086":3,"1086,1087":2,"2171,8689":1,"2172,8688":1,"2172,8689":1,"2173,8688":1,"2170,2172":2,"2171,2172":1,"2172,2173":1,"4343,4345":2,"4344,4346":3,"4343,4346":3,"4344,4347":2,"4344,4345":1,"4345,4346":1,"4345,4347":1,"8689,69519":1,"8690,69518":1,"8690,69519":1,"8691,69518":1,"4344,17379":1,"4345,17378":1,"4345,17379":1,"4346,17378":1,"2171,8687":1,"2172,8686":1,"2172,8687":1,"2173,8686":1,"1084,4341":1,"1085,4340":1,"1085,4341":1,"1086,4340":1,"1083,1085":1,"1084,1085":1,"2169,2172":1,"2169,2173":1,"4342,4345":1,"4342,4346":1,"4343,4347":1,"8688,8690":1,"8689,8691":2,"8688,8691":1,"8689,8692":1,"8689,8690":1,"8690,8691":1,"8690,8692":1,"17379,69519":1,"17380,69518":1,"17380,69519":1,"17381,69518":1,"101,409":15,"102,408":15,"102,409":15,"103,408":15,"100,102":85,"101,103":74,"100,103":86,"101,104":39,"101,102":36,"102,103":16,"102,104":18,"203,817":4,"204,816":4,"204,817":4,"205,816":4,"101,407":21,"102,406":21,"102,407":21,"103,406":21,"99,102":56,"99,103":28,"100,104":22,"202,204":42,"203,205":29,"202,205":43,"203,206":15,"203,204":14,"204,205":4,"204,206":5,"407,1631":4,"408,1630":4,"408,1631":4,"409,1630":4,"202,813":10,"203,812":10,"203,813":10,"204,812":10,"100,405":21,"101,404":21,"101,405":21,"102,404":21,"99,101":28,"100,101":21,"201,203":17,"201,204":35,"202,203":10,"405,408":22,"406,409":19,"405,409":10,"406,410":4,"406,408":21,"407,409":9,"407,410":4,"814,3261":1,"815,3260":1,"815,3261":1,"816,3260":1,"203,815":11,"204,814":11,"204,815":11,"205,814":11,"201,205":18,"202,206":11,"406,1629":5,"407,1628":5,"407,1629":5,"408,1628":5,"405,407":13,"406,407":6,"407,408":5,"813,815":11,"814,816":8,"813,816":11,"814,817":4,"814,815":4,"815,816":1,"815,817":1,"1629,6519":1,"1630,6518":1,"1630,6519":1,"1631,6518":1,"813,3257":3,"814,3256":3,"814,3257":3,"815,3256":3,"406,1627":6,"407,1626":6,"407,1627":6,"408,1626":6,"202,811":7,"203,810":7,"203,811":7,"204,810":7,"100,403":7,"101,402":7,"101,403":7,"102,402":7,"98,101":7,"98,102":7,"200,203":7,"200,204":7,"404,407":7,"404,408":6,"812,814":4,"812,815":8,"813,814":3,"1627,1630":5,"1628,1631":5,"1627,1631":2,"1628,1632":1,"1628,1630":6,"1629,1631":3,"1629,1632":1,"3258,13037":1,"3259,13036":1,"3259,13037":1,"3260,13036":1,"814,3259":3,"815,3258":3,"815,3259":3,"816,3258":3,"812,816":4,"813,817":3,"1628,6517":2,"1629,6516":2,"1629,6517":2,"1630,6516":2,"1627,1629":3,"1628,1629":2,"1629,1630":2,"3257,3259":3,"3258,3260":3,"3257,3260":2,"3258,3261":1,"3258,3259":2,"3259,3260":1,"3259,3261":1,"6517,52138":1,"6518,52137":1,"6518,52138":1,"6519,52137":1,"3257,13033":1,"3258,13032":1,"3258,13033":1,"3259,13032":1,"1628,6515":1,"1629,6514":1,"1629,6515":1,"1630,6514":1,"813,3255":1,"814,3254":1,"814,3255":1,"815,3254":1,"405,1625":1,"406,1624":1,"406,1625":1,"407,1624":1,"404,406":1,"405,406":1,"811,814":1,"811,815":1,"1626,1629":1,"1626,1630":1,"3256,3258":1,"3256,3259":1,"3257,3258":1,"6515,6518":1,"6516,6519":2,"6515,6519":1,"6516,6520":1,"6516,6518":1,"6517,6519":1,"6517,6520":1,"13034,52138":1,"13035,52137":1,"13035,52138":1,"13036,52137":1,"76,307":17,"77,306":17,"77,307":17,"78,306":17,"74,77":86,"75,78":78,"74,78":38,"75,79":18,"75,77":87,"76,78":40,"76,79":19,"152,613":6,"153,612":6,"153,613":6,"154,612":6,"75,305":22,"76,304":22,"76,305":22,"77,304":22,"74,76":53,"75,76":27,"76,77":22,"151,153":43,"152,154":33,"151,154":42,"152,155":17,"152,153":17,"153,154":6,"153,155":7,"305,1223":6,"306,1222":6,"306,1223":6,"307,1222":6,"151,609":11,"152,608":11,"152,609":11,"153,608":11,"75,303":21,"76,302":21,"76,303":21,"77,302":21,"73,76":26,"73,77":21,"150,152":16,"150,153":31,"151,152":11,"303,306":21,"304,307":22,"303,307":11,"304,308":6,"304,306":21,"305,307":11,"305,308":6,"610,2445":3,"611,2444":3,"611,2445":3,"612,2444":3,"152,611":10,"153,610":10,"153,611":10,"154,610":10,"150,154":15,"151,155":10,"304,1221":5,"305,1220":5,"305,1221":5,"306,1220":5,"303,305":10,"304,305":5,"305,306":5,"609,611":10,"610,612":11,"609,612":11,"610,613":6,"610,611":5,"611,612":3,"611,613":3,"1221,4889":2,"1222,4888":2,"1222,4889":2,"1223,4888":2,"610,2443":3,"611,2442":3,"611,2443":3,"612,2442":3,"304,1219":5,"305,1218":5,"305,1219":5,"306,1218":5,"151,607":5,"152,606":5,"152,607":5,"153,606":5,"74,301":5,"75,300":5,"75,301":5,"76,300":5,"73,75":5,"74,75":5,"149,152":5,"149,153":5,"302,305":5,"302,306":5,"608,611":5,"608,612":3,"609,613":3,"1220,1222":5,"1221,1223":6,"1220,1223":5,"1221,1224":3,"1221,1222":3,"1222,1223":2,"1222,1224":2,"2443,9777":1,"2444,9776":1,"2444,9777":1,"2445,9776":1,"1221,4887":1,"1222,4886":1,"1222,4887":1,"1223,4886":1,"609,2441":2,"610,2440":2,"610,2441":2,"611,2440":2,"608,610":2,"609,610":2,"1219,1222":2,"1219,1223":1,"1220,1224":1,"2442,2444":2,"2443,2445":3,"2442,2445":3,"2443,2446":2,"2443,2444":1,"2444,2445":1,"2444,2446":1,"4887,39102":1,"4888,39101":1,"4888,39102":1,"4889,39101":1,"2443,9775":1,"2444,9774":1,"2444,9775":1,"2445,9774":1,"1220,4885":1,"1221,4884":1,"1221,4885":1,"1222,4884":1,"1219,1221":1,"1220,1221":1,"2441,2444":1,"2441,2445":1,"2442,2446":1,"4886,4888":1,"4887,4889":2,"4886,4889":1,"4887,4890":1,"4887,4888":1,"4888,4889":1,"4888,4890":1,"9775,39102":1,"9776,39101":1,"9776,39102":1,"9777,39101":1,"114,461":1,"115,460":1,"115,461":1,"116,460":1,"113,115":43,"114,116":25,"113,116":44,"114,117":14,"114,115":12,"115,116":1,"115,117":2,"229,919":1,"230,918":1,"230,919":1,"231,918":1,"113,457":11,"114,456":11,"114,457":11,"115,456":11,"112,114":20,"112,115":40,"113,114":11,"227,230":21,"228,231":13,"227,231":6,"228,232":1,"228,230":22,"229,231":7,"229,232":1,"458,1835":1,"459,1834":1,"459,1835":1,"460,1834":1,"114,459":11,"115,458":11,"115,459":11,"116,458":11,"112,116":20,"113,117":12,"228,915":5,"229,914":5,"229,915":5,"230,914":5,"113,455":9,"114,454":9,"114,455":9,"115,454":9,"111,114":9,"111,115":9,"226,229":9,"226,230":5,"227,229":19,"456,459":11,"457,460":8,"456,460":4,"457,461":1,"457,459":11,"458,460":4,"458,461":1,"916,3667":1,"917,3666":1,"917,3667":1,"918,3666":1,"228,917":6,"229,916":6,"229,917":6,"230,916":6,"228,229":10,"229,230":6,"457,1831":3,"458,1830":3,"458,1831":3,"459,1830":3,"227,913":4,"228,912":4,"228,913":4,"229,912":4,"226,228":4,"227,228":4,"455,458":4,"455,459":3,"456,458":8,"914,917":5,"915,918":5,"914,918":2,"915,919":1,"915,917":6,"916,918":3,"916,919":1,"1832,7333":1,"1833,7332":1,"1833,7333":1,"1834,7332":1,"457,1833":3,"458,1832":3,"458,1833":3,"459,1832":3,"457,458":4,"458,459":3,"915,3665":2,"916,3664":2,"916,3665":2,"917,3664":2,"914,916":3,"915,916":2,"916,917":2,"1831,1833":3,"1832,1834":3,"1831,1834":2,"1832,1835":1,"1832,1833":2,"1833,1834":1,"1833,1835":1,"3665,29325":1,"3666,29324":1,"3666,29325":1,"3667,29324":1,"1831,7329":1,"1832,7328":1,"1832,7329":1,"1833,7328":1,"915,3663":1,"916,3662":1,"916,3663":1,"917,3662":1,"456,1829":1,"457,1828":1,"457,1829":1,"458,1828":1,"455,457":1,"456,457":1,"913,916":1,"913,917":1,"1830,1832":1,"1830,1833":1,"1831,1832":1,"3663,3666":1,"3664,3667":2,"3663,3667":1,"3664,3668":1,"3664,3666":1,"3665,3667":1,"3665,3668":1,"7330,29325":1,"7331,29324":1,"7331,29325":1,"7332,29324":1,"85,345":9,"86,344":9,"86,345":9,"87,344":9,"84,86":42,"85,87":40,"84,87":44,"85,88":22,"85,86":19,"86,87":9,"86,88":10,"171,689":4,"172,688":4,"172,689":4,"173,688":4,"85,343":11,"86,342":11,"86,343":11,"87,342":11,"83,86":25,"83,87":13,"84,88":12,"170,172":21,"171,173":18,"170,173":21,"171,174":9,"171,172":9,"172,173":4,"172,174":4,"343,1377":1,"344,1376":1,"344,1377":1,"345,1376":1,"171,687":5,"172,686":5,"172,687":5,"173,686":5,"84,341":10,"85,340":10,"85,341":10,"86,340":10,"83,85":12,"84,85":10,"169,172":14,"169,173":7,"170,174":5,"342,344":10,"343,345":7,"342,345":11,"343,346":4,"343,344":3,"344,345":1,"344,346":1,"687,2751":1,"688,2750":1,"688,2751":1,"689,2750":1,"342,1373":2,"343,1372":2,"343,1373":2,"344,1372":2,"170,685":5,"171,684":5,"171,685":5,"172,684":5,"169,171":7,"170,171":5,"341,343":4,"341,344":9,"342,343":2,"685,688":6,"686,689":5,"685,689":3,"686,690":1,"686,688":5,"687,689":2,"687,690":1,"1374,5499":1,"1375,5498":1,"1375,5499":1,"1376,5498":1,"343,1375":3,"344,1374":3,"344,1375":3,"345,1374":3,"341,345":5,"342,346":3,"686,2747":2,"687,2746":2,"687,2747":2,"688,2746":2,"342,1371":2,"343,1370":2,"343,1371":2,"344,1370":2,"170,683":2,"171,682":2,"171,683":2,"172,682":2,"84,339":2,"85,338":2,"85,339":2,"86,338":2,"82,85":2,"82,86":2,"168,171":2,"168,172":2,"340,343":2,"340,344":2,"684,687":2,"684,688":2,"685,687":3,"1372,1375":2,"1373,1376":3,"1372,1376":1,"1373,1377":1,"1373,1375":3,"1374,1376":2,"1374,1377":1,"2748,21993":1,"2749,21992":1,"2749,21993":1,"2750,21992":1,"686,2749":1,"687,2748":1,"687,2749":1,"688,2748":1,"686,687":1,"687,688":1,"1373,5497":1,"1374,5496":1,"1374,5497":1,"1375,5496":1,"1372,1374":1,"1373,1374":1,"1374,1375":1,"2747,2749":1,"2748,2750":2,"2747,2750":1,"2748,2751":1,"2748,2749":1,"2749,2750":1,"2749,2751":1,"5497,21993":1,"5498,21992":1,"5498,21993":1,"5499,21992":1,"64,259":10,"65,258":10,"65,259":10,"66,258":10,"62,65":10,"63,66":21,"62,66":10,"63,67":10,"63,65":11,"64,66":12,"128,517":4,"129,516":4,"129,517":4,"130,516":4,"127,129":21,"128,130":19,"127,130":22,"128,131":10,"128,129":9,"129,130":4,"129,131":4,"257,1033":2,"258,1032":2,"258,1033":2,"259,1032":2,"128,515":6,"129,514":6,"129,515":6,"130,514":6,"126,129":13,"126,130":7,"127,131":6,"256,258":11,"257,259":9,"256,259":10,"257,260":4,"257,258":5,"258,259":2,"258,260":2,"515,2063":2,"516,2062":2,"516,2063":2,"517,2062":2,"256,1029":3,"257,1028":3,"257,1029":3,"258,1028":3,"127,513":5,"128,512":5,"128,513":5,"129,512":5,"126,128":6,"127,128":5,"255,257":4,"255,258":7,"256,257":3,"513,516":5,"514,517":6,"513,517":3,"514,518":2,"514,516":5,"515,517":3,"515,518":2,"1030,4125":1,"1031,4124":1,"1031,4125":1,"1032,4124":1,"257,1031":2,"258,1030":2,"258,1031":2,"259,1030":2,"255,259":3,"256,260":2,"514,2061":1,"515,2060":1,"515,2061":1,"516,2060":1,"513,515":2,"514,515":1,"515,516":1,"1029,1031":2,"1030,1032":3,"1029,1032":3,"1030,1033":2,"1030,1031":1,"1031,1032":1,"1031,1033":1,"2061,16494":1,"2062,16493":1,"2062,16494":1,"2063,16493":1,"1030,4123":1,"1031,4122":1,"1031,4123":1,"1032,4122":1,"514,2059":1,"515,2058":1,"515,2059":1,"516,2058":1,"256,1027":1,"257,1026":1,"257,1027":1,"258,1026":1,"127,511":1,"128,510":1,"128,511":1,"129,510":1,"125,128":1,"125,129":1,"254,257":1,"254,258":1,"512,515":1,"512,516":1,"1028,1031":1,"1028,1032":1,"1029,1033":1,"2060,2062":1,"2061,2063":2,"2060,2063":1,"2061,2064":1,"2061,2062":1,"2062,2063":1,"2062,2064":1,"4123,16494":1,"4124,16493":1,"4124,16494":1,"4125,16493":1,"96,389":2,"97,388":2,"97,389":2,"98,388":2,"96,98":14,"96,99":7,"96,97":7,"97,98":2,"97,99":2,"193,775":2,"194,774":2,"194,775":2,"195,774":2,"95,385":5,"96,384":5,"96,385":5,"97,384":5,"191,194":11,"192,195":9,"191,195":5,"192,196":2,"192,194":10,"193,195":4,"193,196":2,"386,1547":2,"387,1546":2,"387,1547":2,"388,1546":2,"96,387":6,"97,386":6,"97,387":6,"98,386":6,"95,99":5,"192,771":3,"193,770":3,"193,771":3,"194,770":3,"190,194":3,"384,387":5,"385,388":6,"384,388":3,"385,389":2,"385,387":5,"386,388":3,"386,389":2,"772,3093":1,"773,3092":1,"773,3093":1,"774,3092":1,"192,773":2,"193,772":2,"193,773":2,"194,772":2,"192,193":3,"193,194":2,"385,1545":1,"386,1544":1,"386,1545":1,"387,1544":1,"384,386":2,"385,386":1,"386,387":1,"771,773":2,"772,774":3,"771,774":3,"772,775":2,"772,773":1,"773,774":1,"773,775":1,"1545,12369":1,"1546,12368":1,"1546,12369":1,"1547,12368":1,"772,3091":1,"773,3090":1,"773,3091":1,"774,3090":1,"385,1543":1,"386,1542":1,"386,1543":1,"387,1542":1,"191,769":1,"192,768":1,"192,769":1,"193,768":1,"383,386":1,"383,387":1,"770,773":1,"770,774":1,"771,775":1,"1544,1546":1,"1545,1547":2,"1544,1547":1,"1545,1548":1,"1545,1546":1,"1546,1547":1,"1546,1548":1,"3091,12369":1,"3092,12368":1,"3092,12369":1,"3093,12368":1,"72,291":5,"73,290":5,"73,291":5,"74,290":5,"71,75":5,"72,75":5,"144,581":3,"145,580":3,"145,581":3,"146,580":3,"144,146":11,"144,147":5,"144,145":6,"145,146":3,"145,147":3,"289,1161":1,"290,1160":1,"290,1161":1,"291,1160":1,"144,579":2,"145,578":2,"145,579":2,"146,578":2,"143,147":2,"288,290":5,"289,291":5,"288,291":6,"289,292":3,"289,290":2,"290,291":1,"290,292":1,"579,2321":1,"580,2320":1,"580,2321":1,"581,2320":1,"289,1159":2,"290,1158":2,"290,1159":2,"291,1158":2,"143,577":3,"144,576":3,"144,577":3,"145,576":3,"287,290":3,"287,291":2,"288,292":2,"578,580":3,"579,581":3,"578,581":2,"579,582":1,"579,580":2,"580,581":1,"580,582":1,"1159,9276":1,"1160,9275":1,"1160,9276":1,"1161,9275":1,"578,2317":1,"579,2316":1,"579,2317":1,"580,2316":1,"288,1157":1,"289,1156":1,"289,1157":1,"290,1156":1,"287,289":1,"288,289":1,"577,579":1,"577,580":1,"578,579":1,"1157,1160":1,"1158,1161":2,"1157,1161":1,"1158,1162":1,"1158,1160":1,"1159,1161":1,"1159,1162":1,"2318,9276":1,"2319,9275":1,"2319,9276":1,"2320,9275":1,"108,437":1,"109,436":1,"109,437":1,"110,436":1,"108,110":8,"108,111":4,"108,109":4,"109,110":1,"109,111":1,"217,871":1,"218,870":1,"218,871":1,"219,870":1,"107,433":3,"108,432":3,"108,433":3,"109,432":3,"215,218":5,"216,219":5,"215,219":2,"216,220":1,"216,218":6,"217,219":3,"217,220":1,"434,1741":1,"435,1740":1,"435,1741":1,"436,1740":1,"108,435":3,"109,434":3,"109,435":3,"110,434":3,"107,111":3,"216,869":2,"217,868":2,"217,869":2,"218,868":2,"216,217":2,"217,218":2,"433,435":3,"434,436":3,"433,436":2,"434,437":1,"434,435":2,"435,436":1,"435,437":1,"869,6956":1,"870,6955":1,"870,6956":1,"871,6955":1,"433,1737":1,"434,1736":1,"434,1737":1,"435,1736":1,"216,867":1,"217,866":1,"217,867":1,"218,866":1,"214,218":1,"432,434":1,"432,435":1,"433,434":1,"867,870":1,"868,871":2,"867,871":1,"868,872":1,"868,870":1,"869,871":1,"869,872":1,"1738,6956":1,"1739,6955":1,"1739,6956":1,"1740,6955":1,"81,327":3,"82,326":3,"82,327":3,"83,326":3,"80,84":3,"81,83":6,"81,84":3,"162,653":2,"163,652":2,"163,653":2,"164,652":2,"80,325":3,"81,324":3,"81,325":3,"82,324":3,"81,82":3,"162,164":6,"161,164":5,"162,165":3,"162,163":3,"163,164":2,"163,165":2,"325,1305":1,"326,1304":1,"326,1305":1,"327,1304":1,"162,651":1,"163,650":1,"163,651":1,"164,650":1,"160,164":1,"161,165":1,"324,326":2,"325,327":3,"324,327":3,"325,328":2,"325,326":1,"326,327":1,"326,328":1,"651,5216":1,"652,5215":1,"652,5216":1,"653,5215":1,"325,1303":1,"326,1302":1,"326,1303":1,"327,1302":1,"161,649":1,"162,648":1,"162,649":1,"163,648":1,"323,326":1,"323,327":1,"324,328":1,"650,652":1,"651,653":2,"650,653":1,"651,654":1,"651,652":1,"652,653":1,"652,654":1,"1303,5216":1,"1304,5215":1,"1304,5216":1,"1305,5215":1,"122,491":1,"123,490":1,"123,491":1,"124,490":1,"121,124":5,"120,124":3,"121,125":1,"122,124":2,"122,125":1,"244,979":1,"245,978":1,"245,979":1,"246,978":1,"121,487":2,"122,486":2,"122,487":2,"123,486":2,"242,245":2,"243,246":3,"242,246":1,"243,247":1,"243,245":3,"244,246":2,"244,247":1,"488,3911":1,"489,3910":1,"489,3911":1,"490,3910":1,"121,489":1,"122,488":1,"122,489":1,"123,488":1,"122,123":1,"243,977":1,"244,976":1,"244,977":1,"245,976":1,"242,244":1,"243,244":1,"244,245":1,"487,489":1,"488,490":2,"487,490":1,"488,491":1,"488,489":1,"489,490":1,"489,491":1,"977,3911":1,"978,3910":1,"978,3911":1,"979,3910":1,"91,369":1,"92,368":1,"92,369":1,"93,368":1,"91,94":2,"92,93":1,"183,735":1,"184,734":1,"184,735":1,"185,734":1,"182,185":3,"181,185":2,"182,186":1,"182,184":2,"183,185":1,"183,186":1,"366,2932":1,"367,2931":1,"367,2932":1,"368,2931":1,"91,367":1,"92,366":1,"92,367":1,"93,366":1,"90,94":1,"182,731":1,"183,730":1,"183,731":1,"184,730":1,"364,367":1,"365,368":2,"364,368":1,"365,369":1,"365,367":1,"366,368":1,"366,369":1,"732,2932":1,"733,2931":1,"733,2932":1,"734,2931":1,"68,277":1,"69,276":1,"69,277":1,"70,276":1,"69,70":1,"137,551":1,"138,550":1,"138,551":1,"139,550":1,"136,139":3,"135,139":1,"136,140":1,"137,139":2,"137,140":1,"274,2198":1,"275,2197":1,"275,2198":1,"276,2197":1,"68,275":1,"69,274":1,"69,275":1,"70,274":1,"67,71":1,"136,549":1,"137,548":1,"137,549":1,"138,548":1,"137,138":1,"273,275":1,"274,276":2,"273,276":1,"274,277":1,"274,275":1,"275,276":1,"275,277":1,"549,2198":1,"550,2197":1,"550,2198":1,"551,2197":1,"102,413":1,"103,412":1,"103,413":1,"104,412":1,"102,105":2,"103,104":1,"103,105":1,"205,1647":1,"206,1646":1,"206,1647":1,"207,1646":1,"102,411":1,"103,410":1,"103,411":1,"104,410":1,"101,105":1,"205,207":2,"204,207":1,"205,208":1,"205,206":1,"206,207":1,"206,208":1,"411,1647":1,"412,1646":1,"412,1647":1,"413,1646":1,"77,311":1,"78,310":1,"78,311":1,"79,310":1,"76,80":1,"154,1234":1,"155,1233":1,"155,1234":1,"156,1233":1,"153,156":2,"152,156":1,"153,157":1,"154,156":1,"154,157":1,"308,1234":1,"309,1233":1,"309,1234":1,"310,1233":1,"115,924":1,"116,923":1,"116,924":1,"117,923":1,"114,118":1,"115,118":1,"230,924":1,"231,923":1,"231,924":1,"232,923":1,"86,692":1,"87,691":1,"87,692":1,"88,691":1,"85,89":1,"86,89":1,"172,692":1,"173,691":1,"173,692":1,"174,691":1,"64,518":1,"65,517":1,"65,518":1,"66,517":1,"64,65":1,"65,66":1,"129,518":1,"130,517":1,"130,518":1,"131,517":1,"53,216":1,"54,215":1,"54,216":1,"55,215":1},"monic":{"3":1,"1":1,"2":1},"edf_draw":{"":2},"edf_powmod":{"2":2},"edf_constsub":{"2":2},"root_linear":{"":2}}
```
