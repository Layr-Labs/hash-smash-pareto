# Orchard r=1: executed two-round-bypass collision with a counted operation ledger

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
by a deterministic procedure whose complete primitive-operation count and peak memory are
stated below. Cost model `orchard-field-ram-v2`: every field addition, subtraction or
multiplication, every 256-bit load or store, comparison, branch, shift or boolean word
operation costs one unit; C(1) = 216 + 21*1 = 237 units per reduced permutation.
Normalized time T = W / C(1), `time_log2` = log2 T. Memory in bytes, including code.

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
of T' by Lemma 1. Applying rounds 2, 3 (full), 4..4 (partial) and 60..63 (full) to
s(T') and taking lane 0 defines a polynomial f in F_p[T'] of degree at most
D = 5^(6+1) = 78125, and H(nk(T), rho(T)) = f(T^5) for every T.

Proof. Each S-box multiplies the degree of the lane it acts on by at most 5 and the linear
layers do not raise degrees; two bypassed rounds leave 6 full rounds and 1 partial rounds,
hence degree at most 5^(6+1). (Equality holds generically and is verified computationally:
the program in Appendix A constructs f by composition and asserts deg f = 78125; the procedure
only needs deg f < N1.) The identity with H follows from Lemma 1. QED

**Lemma 3 (soundness of the certificate).** If T'_0 != T'_1 satisfy f(T'_0) = f(T'_1), the
two inputs (nk(T_0), rho(T_0)) and (nk(T_1), rho(T_1)) with T_i = (T'_i)^e5 are distinct
canonical pairs with equal reduced hash. Proof: injectivity in Lemma 1 and Lemma 2. The
organizer checker recomputes both hashes from the certificate bytes; it does not depend on
any statement below.

## 3. The procedure

All polynomial arithmetic is over F_p. D = 78125, N1 = 98304 (the least 3*2^k >= D) and
N2 = 196608 (the least 3*2^k >= 2D-1). The procedure is deterministic: its only "random"
inputs are the preregistered stream values s_n = SHA-256("poseidon_mage r=1 trial n")
read as a little-endian integer and reduced modulo p; the certificate came from trial
n = 0, and every trial from 0 to 0 is charged. No other stream label was ever run on this
target: the label was fixed before the first execution, and the prototype and the counted run used it unchanged.

Step 1 (f, once per trial). Evaluate f at the N1 points omega^i, i < N1, omega a primitive N1-th root of
unity: each evaluation starts from the affine state s(T') of Lemma 1 and applies the
6 + 1 remaining rounds. One inverse transform of length N1 then yields the coefficients of
f, exactly, because deg f = D < N1. (Appendix A constructs f by composition instead; both
produce the same uniquely defined polynomial, and the appendix asserts agreement with the
permutation at three points.) f is discarded once q has been formed in Step 2, so it is not live
during Steps 3-5; a retry rebuilds it, and the rebuild is charged to every trial.

Step 2 (trial n). s0 = s_n; (x0, x1) = (nk(T), rho(T)) for T = s0^e5; y = H(x0, x1), which
equals f(s0). q = (f - y) / (X - s0) by synthetic division, of degree Dq := D - 1 = 78124, made monic by one
field inversion. In 4.2 and 4.3 the modulus degree is this Dq (written D there for brevity), and
N1, N2 are the least lengths 3*2^k >= Dq and >= 2 Dq - 1, which coincide with those for D. The polynomial q has as roots exactly the parameters T' != s0 with
f(T') = y.

Step 3 (Frobenius). h = X^p mod q by left-to-right binary exponentiation: with
k0 = floor(log2 Dq) = 16, the top k0+1 bits of p encode 2^k0 (p = 2^254 + c with
c < 2^126), so the running value starts as X^(2^k0), of degree below Dq, without any
reduction; the remaining 254 - k0 = 238 bits each cost one modular squaring and, for the
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

T(98304) = 4,775,936 and T(196608) = 10,125,312. The 1/N scaling of an inverse transform is folded
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
  Charge SQ = 59,391,098 units at modulus degree 78124, itemized in Appendix A and asserted equal to the
  instrumented kernel (results checked against an independent library) at D = 125, 625, 3125.
Multiplication by X modulo q: 13D/2 units (shift: 2D loads, D stores; subtraction of the leading
coefficient times q: D multiplications, D subtractions, D loads; 1/2 loop unit per coefficient).

4.3 Newton inverse of rev(q) modulo X^n: precision doubling m -> m2 = min(2m, n), each step two
products at the least length N(m) = 3*2^j >= m2 charged (m2+N) + (m+N) + 5 T(N) + 10 N +
2(m2-m) + (N-(m2-m)) + 3(m2-m) units; total NEWTON = 74,034,757.5 units. The cached transform
INVQ costs CACHE(n, N2) = 2n + (N2-n) + T(N2) once per trial. Powering start: acc = X^(2^k0)
is written directly (D stores).

4.4 Evaluation of f: N1 evaluations at 6 + 27*6 + 21*1 + 1 = 190 units each (affine
start, six full rounds at 27 units, 1 partial rounds at 21 units, one store), one inverse
transform T(N1) with N1 scaling multiplications, and the evaluation points omega^i produced by a
running product (one multiplication and one store each, 2 N1 units): 23,748,608 units. Peak live
words in this phase: the N1 points and the N1 evaluations.

4.5 Trial preparation: one stream draw (one SHA-256 compression, priced at 1,024 word
operations), three fifth roots (3 x 377), one reduced permutation for y (237), synthetic
division (4 units per coefficient), one inversion (330), the monic scaling (4 units per
coefficient) and forming h - X (4): 627,726 units per trial. Setup, once: the constants of
Lemma 1 (two inversions, a few fifth powers, products and sums), charged as a flat 2,000 units.

4.6 Finish: per root three fifth roots, one verifying permutation and an 8-unit digest
comparison, plus one permutation for the first input: 2,989 units.

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
  SHA-256("poseidon_mage r=1 edf n") mod p (64 per draw); (X + c)^((p-1)/2) mod g is charged
  as 253 schoolbook modular squarings (4d^2 + (d-1)(4d+2) each) and popcount((p-1)/2) - 1
  multiplications by X + c (4d + (d-1)(4d+2) each), the gcd with g by classical Euclid as above,
  recursing on both factors.
Memory: the live coefficient words of every polynomial held by an active frame of the
recursion (inputs, truncated copies, matrix entries, remainders) plus transform scratch
(2N words for a transform product, m1+m2-1 for a classical one, (n+1) + L for a division).

5.3 Executed count. On this instance (trial 0, deg q = 78124) the stage performed
155,135 classical and 10,244 transform products, 78,122 classical and 0 Newton divisions in the half-gcd (the root stage adds its own, listed in the histogram) and charged 2,140,715,944 units with a peak of 587,230 live words; the
root stage charged 9,514 units. Appendix B reproduces `gcd_trace_r1.json`, the
histogram of every charged operation by kind and size; `halfgcd_charge.py` (Appendix A,
standard library only) recomputes the charge from that histogram and the rules above.

## 6. Totals

| phase | units | peak live words |
|---|---:|---:|
| setup (Lemma 1 constants) | 2,000 | |
| trial 0: build f (4.4) | 23,748,608 | 196,616 |
| trial 0: preparation (4.5) | 627,726 | 156,258 |
| trial 0: Newton inverse + cached INVQ | 84,533,104 | 352,856 |
| trial 0: 238 squarings x 59,391,098 + 117,186 start stores with loop control | 14,135,198,510 | 569,645 |
| trial 0: 46 multiplications by X | 23,359,076 | |
| trial 0: half-gcd + roots (5.3) | 2,140,725,458 | 587,230 |
| trial 0: finish (4.6) | 2,989 | |
| **total** | **16,408,197,472** | **587,230** |

Total W = 16,408,197,472 units; T = W / 237 = 69,232,900.72; `time_log2` = log2 T = 26.044954,
submitted as 26.05 (ceiling at two decimals; not a downward rounding).

Executed trials of the stream (context): trial 0: deg g = 2.

## 7. Success probability and the trial budget

The procedure reads no random coins: its inputs are the pinned constants and the
preregistered SHA-256 stream. Executed on this fixed target it performed exactly the
operations charged above and returned the certified pair at trial 0; a deterministic
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
in `certificates/manifest.json` is the common reduced hash c3bb22318263dc1fc4b1b5aafb11f4e44e0eafbb8879826b0c2edf63de39c03e (32 little-endian
bytes). All inputs are canonical and the files differ. The organizer checker recomputes
the reduced permutation on each file; that check is independent of every count above.

## 9. Memory

Peak live storage is the maximum over the phases (Section 6, table): words of 32 bytes,
plus a fixed 2^20-byte allowance for code, constants, the stream state and the stack.
log2 of that total is 24.241904, submitted as `memory_log2_bytes` = 24.25 (ceiling at
two decimals). f is not live after Step 2 (Section 3). The normalized cost axis is
`time_log2` + max(0, `memory_log2_bytes` - 20) = 30.30 with the submitted bounds; the claim
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
Run `python accounting.py orchard-pallas-constants.json ledger_r1.json <dir with the gcd_trace files>` to recompute
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

`ledger_r1.json` (every phase count, sizes, flags, the stream indices, the root(s) and the pair):

```json
{
 "r": 1,
 "D": 78125,
 "N1": 98304,
 "N2": 196608,
 "C": 237,
 "phases": {
  "setup": 2000,
  "build_f_per_trial": 23748608
 },
 "memory_words": {
  "build_f": 196616,
  "form_q": 156258
 },
 "trials": [
  {
   "n": 0,
   "s0": "16311481932888599730541675533284848162292633904991545526689034879658717755557",
   "inputs0": [
    "14866640318450707025069991772096995134930310330600685798149946949960076607844",
    "9869130765422249800945935326033051166465704525110723119376179516603979551581"
   ],
   "y": "28383030643767620791373214070774973378465569058152501832070749357566597446595",
   "ops_build": 23748608,
   "ops_prepare": 627726,
   "t_pow": 187.66272377967834,
   "ops_powering": 14243090690.5,
   "mem_powering": 569645,
   "powering": {
    "D": 78124,
    "r": 1,
    "C": 237,
    "N1": 98304,
    "N2": 196608,
    "k0": 16,
    "cache_qn1": false,
    "n_squarings": 238,
    "n_mulx": 46,
    "ops": {
     "newton": 74034757.5,
     "cache_build": 10498347,
     "init": 117186,
     "squaring_each": 59391098,
     "squarings": 14135081324,
     "mulx_each": 507806,
     "mulx_total": 23359076,
     "total": 14243090690.5
    },
    "T_N1": 4775936,
    "T_N2": 10125312,
    "live_words_squaring": {
     "Q": 78125,
     "R": 98304,
     "A": 196608,
     "INVQ": 196608
    },
    "peak_words": {
     "powering": 569645,
     "newton": 352856,
     "cache_build": 352856,
     "max": 569645
    },
    "memory_bytes": 19277216,
    "time_log2": 25.840799938979004,
    "memory_log2": 24.200393377967842,
    "score_contribution": 30.041193316946845
   },
   "t_gcd": 21.970085382461548,
   "ops_gcd": 2140725458,
   "mem_gcd": 587230,
   "gcd": {
    "ops": 2140725458,
    "ops_exact": "2140725458",
    "peak_words": 587230,
    "gcd_degree": 2,
    "roots": [
     "8808682683813916034870093651879040429742937811014878359274884002135283673954",
     "25572977977132461306442565066351836957110148620779027991126511445093628096120"
    ],
    "cutoff": 128,
    "top_fraction": 4,
    "gcd_ops": "2140715944",
    "roots_ops": "9514",
    "roots_draws": 1,
    "gcd_products": {
     "classical": 155135,
     "ntt": 10244,
     "zero": 869
    },
    "gcd_divisions": {
     "classical": 78122,
     "newton": 0
    },
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
   },
   "deg_g": 2,
   "roots": [
    "8808682683813916034870093651879040429742937811014878359274884002135283673954",
    "25572977977132461306442565066351836957110148620779027991126511445093628096120"
   ],
   "ops_total": 16408195471.5,
   "ops_finish": 2989
  }
 ],
 "total_ops": 16408197471.5,
 "time_log2": 26.044954459743373,
 "peak_words": 587230,
 "memory_bytes": 19839936,
 "memory_log2_bytes": 24.241904036073848,
 "score": 30.28685849581722,
 "digest": "c3bb22318263dc1fc4b1b5aafb11f4e44e0eafbb8879826b0c2edf63de39c03e",
 "pairs": [
  {
   "s1": "8808682683813916034870093651879040429742937811014878359274884002135283673954",
   "inputs": [
    "5839686960175649321301144535106340675708687134663784130020240653571636848023",
    "26140441042393280102750807645601586003963485375961958058369640042959305343354"
   ]
  },
  {
   "s1": "25572977977132461306442565066351836957110148620779027991126511445093628096120",
   "inputs": [
    "3779324894948220275739142424341668093781597263555558406096835223928338034375",
    "14685211329835515429919656774200516059451657547876604352088463176358014914326"
   ]
  }
 ],
 "t_build": 0.786017894744873
}
```

`gcd_trace_r1_t0.json` (trial 0: histogram of every charged half-gcd and root operation by kind and size; `halfgcd_charge.py` recomputes the stage charge from it):

```json
{"copy":{"19533":1,"19532":1,"9767":1,"9766":1,"4885":1,"4884":1,"2443":4,"2442":4,"1223":4,"1222":4,"613":4,"612":4,"307":27,"306":27,"155":28,"154":28,"151":87,"150":87,"305":43,"304":43,"153":88,"152":88,"609":22,"608":22,"303":43,"302":43,"149":60,"148":60,"1219":10,"1218":10,"611":21,"610":21,"607":17,"606":17,"301":17,"300":17,"2441":5,"2440":5,"1221":11,"1220":11,"4881":3,"4880":3,"2439":6,"2438":6,"1217":7,"1216":7,"9765":2,"9764":2,"4883":3,"4882":3,"19529":1,"19528":1,"9763":1,"9762":1,"4879":1,"4878":1,"2437":1,"2436":1,"14649":1,"14648":1,"7325":2,"7324":2,"3663":3,"3662":3,"1833":3,"1832":3,"917":8,"916":8,"459":19,"458":19,"231":21,"230":21,"227":42,"226":42,"457":21,"456":21,"229":44,"228":44,"915":11,"914":11,"455":22,"454":22,"225":24,"224":24,"1829":6,"1828":6,"913":11,"912":11,"3661":3,"3660":3,"1831":5,"1830":5,"7323":1,"7322":1,"3659":2,"3658":2,"1827":2,"1826":2,"911":2,"910":2,"453":2,"452":2,"14647":1,"14646":1,"7321":1,"7320":1,"10987":1,"10986":1,"5495":1,"5494":1,"2749":1,"2748":1,"1375":4,"1374":4,"689":4,"688":4,"345":15,"344":15,"173":38,"172":38,"171":43,"170":43,"343":22,"342":22,"169":43,"168":43,"685":11,"684":11,"341":21,"340":21,"1373":5,"1372":5,"687":10,"686":10,"2745":2,"2744":2,"1371":5,"1370":5,"683":7,"682":7,"339":7,"338":7,"167":7,"166":7,"5491":2,"5490":2,"2747":3,"2746":3,"2743":2,"2742":2,"1369":2,"1368":2,"10985":1,"10984":1,"5493":1,"5492":1,"8241":1,"8240":1,"4121":1,"4120":1,"2061":3,"2060":3,"1031":5,"1030":5,"517":5,"516":5,"259":17,"258":17,"131":18,"130":18,"127":17,"126":17,"257":21,"256":21,"513":11,"512":11,"255":22,"254":22,"1029":6,"1028":6,"515":11,"514":11,"2059":2,"2058":2,"1027":5,"1026":5,"511":5,"510":5,"253":5,"252":5,"4119":2,"4118":2,"2057":3,"2056":3,"8237":1,"8236":1,"4117":1,"4116":1,"6181":1,"6180":1,"3091":1,"3090":1,"1547":1,"1546":1,"775":1,"774":1,"389":1,"388":1,"195":12,"194":12,"193":22,"192":22,"385":11,"384":11,"191":22,"190":22,"771":5,"770":5,"387":11,"386":11,"383":9,"382":9,"189":9,"188":9,"1543":3,"1542":3,"773":6,"772":6,"769":4,"768":4,"3089":2,"3088":2,"1545":3,"1544":3,"6177":1,"6176":1,"3087":1,"3086":1,"1541":1,"1540":1,"4635":1,"4634":1,"2319":1,"2318":1,"1161":1,"1160":1,"581":4,"580":4,"291":9,"290":9,"147":10,"146":10,"143":22,"142":22,"289":11,"288":11,"145":22,"144":22,"579":5,"578":5,"287":10,"286":10,"141":12,"140":12,"1157":2,"1156":2,"577":5,"576":5,"2315":2,"2314":2,"1159":3,"1158":3,"1155":2,"1154":2,"575":2,"574":2,"285":2,"284":2,"4633":1,"4632":1,"2317":1,"2316":1,"3477":1,"3476":1,"1739":2,"1738":2,"871":2,"870":2,"437":2,"436":2,"219":7,"218":7,"217":11,"216":11,"433":5,"432":5,"215":10,"214":10,"867":3,"866":3,"435":5,"434":5,"431":4,"430":4,"213":4,"212":4,"1737":1,"1736":1,"869":2,"868":2,"3475":1,"3474":1,"1735":1,"1734":1,"865":1,"864":1,"2607":1,"2606":1,"1305":1,"1304":1,"653":2,"652":2,"327":5,"326":5,"165":5,"164":5,"161":10,"160":10,"325":5,"324":5,"163":11,"162":11,"651":3,"650":3,"323":6,"322":6,"159":6,"158":6,"1301":2,"1300":2,"649":3,"648":3,"2605":1,"2604":1,"1303":1,"1302":1,"1957":1,"1956":1,"979":1,"978":1,"491":1,"490":1,"247":1,"246":1,"243":5,"242":5,"487":3,"486":3,"245":6,"244":6,"241":4,"240":4,"977":2,"976":2,"489":3,"488":3,"1953":1,"1952":1,"975":1,"974":1,"485":1,"484":1,"1467":1,"1466":1,"735":1,"734":1,"369":1,"368":1,"185":4,"184":4,"183":5,"182":5,"365":2,"364":2,"181":5,"180":5,"731":2,"730":2,"367":3,"366":3,"363":2,"362":2,"179":2,"178":2,"1465":1,"1464":1,"733":1,"732":1,"1101":1,"1100":1,"551":1,"550":1,"277":1,"276":1,"139":4,"138":4,"137":5,"136":5,"273":3,"272":3,"135":6,"134":6,"549":2,"548":2,"275":3,"274":3,"1097":1,"1096":1,"547":1,"546":1,"271":1,"270":1,"133":1,"132":1,"825":1,"824":1,"413":2,"412":2,"207":3,"206":3,"205":3,"204":3,"411":1,"410":1,"203":2,"202":2,"823":1,"822":1,"409":1,"408":1,"619":1,"618":1,"311":1,"310":1,"157":1,"156":1,"617":1,"616":1,"309":1,"308":1,"465":1,"464":1,"233":1,"232":1,"461":1,"460":1,"349":1,"348":1,"175":1,"174":1,"261":1,"260":1,"129":1,"128":1,"197":1,"196":1},"division_classical":{"154,153":512,"153,152":512,"152,151":600,"151,150":600,"150,149":687,"149,148":687,"148,147":747,"147,146":747,"146,145":757,"145,144":757,"144,143":779,"143,142":779,"142,141":801,"141,140":801,"140,139":813,"139,138":813,"138,137":817,"137,136":817,"136,135":822,"135,134":822,"134,133":828,"133,132":828,"132,131":829,"131,130":829,"130,129":847,"129,128":847,"128,127":827,"127,126":805,"126,125":817,"125,124":817,"124,123":817,"123,122":816,"122,121":810,"121,120":805,"120,119":801,"119,118":801,"118,117":801,"117,116":801,"116,115":800,"115,114":779,"114,113":735,"113,112":693,"112,111":669,"111,110":669,"110,109":669,"109,108":662,"108,107":651,"107,106":641,"106,105":637,"105,104":637,"104,103":637,"103,102":634,"102,101":631,"101,100":629,"100,99":629,"99,98":629,"98,97":628,"97,96":616,"96,95":594,"95,94":572,"94,93":563,"93,92":563,"92,91":559,"91,90":554,"90,89":549,"89,88":547,"88,87":547,"87,86":546,"86,85":508,"85,84":465,"84,83":422,"83,82":415,"82,81":410,"81,80":399,"80,79":389,"79,78":383,"78,77":382,"229,228":114,"77,76":354,"76,75":266,"459,458":4,"228,227":174,"916,915":4,"456,455":22,"226,225":216,"75,74":179,"1831,1830":4,"457,456":21,"913,912":10,"454,453":17,"225,224":190,"3663,3662":1,"915,914":11,"1830,1829":5,"7324,7323":1,"3660,3659":3,"1828,1827":6,"912,911":7,"14649,14648":1,"3661,3660":3,"7323,7322":2,"68358,68357":1,"14646,14645":1,"7321,7320":1,"3658,3657":1,"1827,1826":1,"58593,58592":1,"230,229":87,"227,226":131,"224,223":197,"223,222":197,"222,221":197,"221,220":197,"220,219":197,"219,218":197,"218,217":204,"217,216":213,"216,215":226,"215,214":215,"214,213":235,"213,212":227,"212,211":229,"211,210":229,"210,209":229,"209,208":229,"208,207":229,"207,206":230,"206,205":232,"205,204":235,"204,203":238,"203,202":235,"202,201":238,"201,200":237,"200,199":237,"199,198":237,"198,197":237,"197,196":237,"196,195":238,"195,194":239,"194,193":250,"193,192":267,"192,191":272,"191,190":272,"190,189":294,"189,188":294,"188,187":303,"187,186":303,"186,185":303,"185,184":303,"184,183":307,"183,182":307,"182,181":312,"181,180":312,"180,179":317,"179,178":317,"178,177":319,"177,176":319,"176,175":319,"175,174":319,"174,173":320,"173,172":320,"172,171":358,"171,170":358,"170,169":401,"169,168":401,"168,167":444,"167,166":444,"166,165":451,"165,164":451,"164,163":456,"163,162":456,"162,161":467,"161,160":467,"160,159":477,"159,158":477,"158,157":483,"157,156":483,"156,155":484,"155,154":484,"343,342":20,"687,686":8,"342,341":22,"1374,1373":3,"685,684":11,"340,339":23,"2746,2745":3,"1371,1370":6,"684,683":11,"5493,5492":2,"1372,1371":5,"2745,2744":3,"10986,10985":1,"5491,5490":1,"2743,2742":2,"1369,1368":2,"682,681":2,"339,338":3,"51268,51267":1,"10984,10983":1,"5490,5489":1,"43944,43943":1,"258,257":16,"516,515":4,"256,255":44,"1030,1029":4,"513,512":11,"255,254":43,"2061,2060":1,"514,513":10,"1029,1028":5,"4120,4119":1,"2058,2057":2,"1027,1026":5,"511,510":7,"253,252":51,"8239,8238":1,"2059,2058":3,"4117,4116":2,"2056,2055":2,"1026,1025":2,"38450,38449":1,"4119,4118":1,"8238,8237":1,"32957,32956":1,"74,73":119,"73,72":109,"72,71":87,"71,70":65,"70,69":53,"69,68":49,"68,67":44,"67,66":38,"66,65":37,"65,64":19,"64,63":18,"387,386":6,"254,253":44,"252,251":49,"251,250":49,"250,249":49,"249,248":49,"248,247":49,"247,246":49,"246,245":50,"245,244":50,"244,243":61,"243,242":61,"242,241":61,"241,240":67,"240,239":65,"239,238":65,"238,237":65,"237,236":65,"236,235":65,"235,234":65,"234,233":65,"233,232":65,"232,231":67,"231,230":67,"772,771":5,"384,383":12,"1545,1544":3,"385,384":12,"771,770":6,"3090,3089":1,"1543,1542":2,"769,768":5,"382,381":6,"6180,6179":1,"3088,3087":2,"1542,1541":3,"28836,28835":1,"6177,6176":1,"3087,3086":1,"24717,24716":1,"291,290":2,"580,579":1,"288,287":12,"1159,1158":1,"289,288":12,"577,576":5,"286,285":10,"2317,2316":1,"579,578":6,"1156,1155":3,"576,575":4,"4635,4634":1,"1158,1157":3,"2316,2315":2,"21626,21625":1,"4632,4631":1,"2314,2313":1,"1155,1154":1,"18537,18536":1,"435,434":5,"870,869":1,"433,432":6,"1738,1737":1,"867,866":2,"432,431":6,"3475,3474":1,"868,867":3,"1735,1734":2,"865,864":2,"430,429":3,"16219,16218":1,"1737,1736":1,"3474,3473":1,"13902,13901":1,"327,326":3,"652,651":2,"324,323":6,"1303,1302":2,"325,324":6,"649,648":3,"322,321":5,"2607,2606":1,"651,650":2,"1302,1301":1,"12163,12162":1,"2605,2604":1,"1300,1299":1,"648,647":1,"10425,10424":1,"489,488":2,"978,977":1,"487,486":3,"1954,1953":1,"975,974":2,"486,485":3,"9121,9120":1,"976,975":1,"1953,1952":1,"7818,7817":1,"367,366":2,"733,732":1,"364,363":4,"1467,1466":1,"366,365":4,"732,731":2,"6839,6838":1,"1464,1463":1,"730,729":1,"363,362":2,"5862,5861":1,"276,275":2,"550,549":1,"273,272":3,"1099,1098":1,"274,273":4,"547,546":2,"271,270":3,"5128,5127":1,"549,548":1,"1098,1097":1,"4395,4394":1,"412,411":2,"825,824":1,"411,410":3,"3844,3843":1,"822,821":1,"409,408":2,"3295,3294":1,"309,308":3,"618,617":1,"307,306":2,"2882,2881":1,"616,615":1,"306,305":2,"2470,2469":1,"463,462":1,"2160,2159":1,"462,461":1,"1851,1850":1,"348,347":2,"1618,1617":1,"345,344":2,"1387,1386":1,"261,260":2,"1212,1211":1,"1039,1038":1,"908,907":1,"778,777":1,"679,678":1,"582,581":1,"508,507":1,"434,433":1,"431,430":1,"429,428":1,"428,427":1,"427,426":1,"426,425":1,"425,424":1,"424,423":1,"423,422":1,"422,421":1,"421,420":1,"420,419":1,"419,418":1,"418,417":1,"417,416":1,"416,415":1,"415,414":1,"414,413":1,"413,412":1,"410,409":1,"408,407":1,"407,406":1,"406,405":1,"405,404":1,"404,403":1,"403,402":1,"402,401":1,"401,400":1,"400,399":1,"399,398":1,"398,397":1,"397,396":1,"396,395":1,"395,394":1,"394,393":1,"393,392":1,"392,391":1,"391,390":1,"390,389":1,"389,388":1,"388,387":1,"386,385":1,"383,382":1,"381,380":1,"380,379":1,"379,378":1,"378,377":1,"377,376":1,"376,375":1,"375,374":1,"374,373":1,"373,372":1,"372,371":1,"371,370":1,"370,369":1,"369,368":1,"368,367":1,"365,364":1,"362,361":1,"361,360":1,"360,359":1,"359,358":1,"358,357":1,"357,356":1,"356,355":1,"355,354":1,"354,353":1,"353,352":1,"352,351":1,"351,350":1,"350,349":1,"349,348":1,"347,346":1,"346,345":1,"344,343":1,"341,340":1,"338,337":1,"337,336":1,"336,335":1,"335,334":1,"334,333":1,"333,332":1,"332,331":1,"331,330":1,"330,329":1,"329,328":1,"328,327":1,"326,325":1,"323,322":1,"321,320":1,"320,319":1,"319,318":1,"318,317":1,"317,316":1,"316,315":1,"315,314":1,"314,313":1,"313,312":1,"312,311":1,"311,310":1,"310,309":1,"308,307":1,"305,304":1,"304,303":1,"303,302":1,"302,301":1,"301,300":1,"300,299":1,"299,298":1,"298,297":1,"297,296":1,"296,295":1,"295,294":1,"294,293":1,"293,292":1,"292,291":1,"290,289":1,"287,286":1,"285,284":1,"284,283":1,"283,282":1,"282,281":1,"281,280":1,"280,279":1,"279,278":1,"278,277":1,"277,276":1,"275,274":1,"272,271":1,"270,269":1,"269,268":1,"268,267":1,"267,266":1,"266,265":1,"265,264":1,"264,263":1,"263,262":1,"262,261":1,"260,259":1,"259,258":1,"257,256":1,"63,62":1,"62,61":1,"61,60":1,"60,59":1,"59,58":1,"58,57":1,"57,56":1,"56,55":1,"55,54":1,"54,53":1,"53,52":1,"52,51":1,"51,50":1,"50,49":1,"49,48":1,"48,47":1,"47,46":1,"46,45":1,"45,44":1,"44,43":1,"43,42":1,"42,41":1,"41,40":1,"40,39":1,"39,38":1,"38,37":1,"37,36":1,"36,35":1,"35,34":1,"34,33":1,"33,32":1,"32,31":1,"31,30":1,"30,29":1,"29,28":1,"28,27":1,"27,26":1,"26,25":1,"25,24":1,"24,23":1,"23,22":1,"22,21":1,"21,20":1,"20,19":1,"19,18":1,"18,17":1,"17,16":1,"16,15":1,"15,14":1,"14,13":1,"13,12":1,"12,11":1,"11,10":1,"10,9":1,"9,8":1,"8,7":1,"7,6":1,"6,5":1,"5,4":1,"4,3":1,"3,2":1,"2,1":2},"product_zero":{"2,0":869},"addsub":{"1":869,"2":1738,"3":1738,"4":1738,"5":1738,"6":1738,"7":1738,"8":1738,"9":1738,"10":1738,"11":1738,"12":1738,"13":1738,"14":1738,"15":1738,"16":1738,"17":1738,"18":1738,"19":1738,"20":1738,"21":1738,"22":1738,"23":1738,"24":1738,"25":1738,"26":1738,"27":1738,"28":1738,"29":1738,"30":1738,"31":1738,"32":1738,"33":1738,"34":1738,"35":1737,"36":1736,"37":1736,"38":1736,"39":1736,"40":1736,"41":1736,"42":1736,"43":1736,"44":1736,"45":1736,"46":1735,"47":1734,"48":1734,"49":1734,"50":1734,"51":1734,"52":1734,"53":1734,"54":1734,"55":1734,"56":1734,"57":1734,"58":1734,"59":1734,"60":1734,"61":1734,"62":1733,"63":1732,"64":1715,"65":1697,"66":1696,"67":1677,"68":1652,"69":1645,"70":1640,"71":1620,"72":1584,"73":1561,"74":1537,"75":1446,"76":1306,"77":1217,"78":1112,"382":27,"383":31,"79":998,"152":156,"153":137,"154":94,"764":4,"765":4,"379":43,"380":43,"151":146,"155":29,"305":75,"306":57,"307":30,"1527":4,"1528":4,"759":22,"760":22,"377":43,"378":43,"150":77,"303":57,"304":82,"308":7,"610":40,"611":31,"612":20,"3052":4,"3053":4,"762":21,"763":21,"1522":10,"1523":10,"757":17,"758":17,"374":17,"375":17,"149":17,"302":18,"608":27,"609":41,"613":5,"1220":22,"1221":17,"1222":13,"6104":1,"6105":1,"1524":11,"1525":11,"3049":5,"3050":5,"1219":20,"1223":5,"2441":10,"2442":8,"2443":5,"12207":1,"12208":1,"6099":3,"6100":3,"3047":6,"3048":6,"1519":7,"1520":7,"607":10,"1218":9,"2439":6,"2440":11,"2444":2,"4882":6,"4883":5,"4884":3,"24414":1,"24415":1,"6102":3,"6103":3,"12204":2,"12205":2,"4881":4,"4885":1,"9765":2,"9766":2,"9767":2,"87889":1,"87890":1,"24409":1,"24410":1,"12202":1,"12203":1,"6097":1,"6098":1,"3044":1,"3045":1,"1217":2,"2438":1,"4880":1,"9763":1,"9764":2,"9768":1,"19530":1,"19531":2,"19532":1,"97654":1,"97655":1,"80":963,"81":946,"82":935,"83":923,"84":900,"85":845,"86":787,"87":743,"88":677,"89":639,"90":636,"91":629,"92":623,"93":618,"94":610,"95":597,"96":566,"97":542,"98":520,"99":488,"100":475,"101":474,"102":472,"103":468,"104":465,"105":461,"106":458,"107":454,"108":440,"109":428,"110":416,"111":399,"112":392,"113":368,"114":304,"115":261,"116":214,"572":19,"573":19,"117":150,"228":83,"229":73,"230":53,"1144":8,"1145":8,"569":21,"570":21,"227":67,"231":21,"457":44,"458":38,"459":25,"2289":3,"2290":3,"1142":11,"1143":11,"567":22,"568":22,"226":26,"456":35,"460":9,"915":20,"916":16,"917":12,"4577":3,"4578":3,"2284":6,"2285":6,"1139":11,"1140":11,"455":17,"913":12,"914":20,"918":4,"1830":12,"1831":10,"1832":8,"9154":2,"9155":2,"2287":5,"2288":5,"4574":3,"4575":3,"1829":8,"1833":4,"3661":5,"3662":5,"3663":4,"18309":1,"18310":1,"9152":1,"9153":1,"4572":2,"4573":2,"2282":2,"2283":2,"1137":2,"1138":2,"564":2,"565":2,"225":3,"454":4,"912":4,"1828":2,"3660":3,"3664":2,"7323":3,"7324":3,"7325":2,"65915":1,"65916":1,"18307":1,"18308":1,"9149":1,"9150":1,"3659":1,"7322":1,"7326":2,"14647":1,"14648":2,"14649":1,"73239":1,"73240":1,"429":15,"430":15,"171":80,"172":70,"173":48,"859":4,"860":4,"427":22,"428":22,"170":71,"174":16,"343":40,"344":31,"345":19,"1717":4,"1718":4,"854":11,"855":11,"424":21,"425":21,"169":35,"341":25,"342":42,"346":5,"686":19,"687":18,"688":13,"3434":1,"3435":1,"857":10,"858":10,"1714":5,"1715":5,"685":19,"689":4,"1373":9,"1374":9,"1375":6,"6867":1,"6868":1,"3429":2,"3430":2,"1712":5,"1713":5,"852":7,"853":7,"422":7,"423":7,"168":8,"340":10,"684":11,"1371":6,"1372":9,"1376":1,"2746":5,"2747":4,"2748":3,"13732":1,"13733":1,"3432":3,"3433":3,"6862":2,"6863":2,"3427":2,"3428":2,"1709":2,"1710":2,"683":3,"1370":3,"2744":2,"2745":5,"2749":1,"5492":4,"5493":4,"5494":2,"49435":1,"49436":1,"6864":1,"6865":1,"13729":1,"13730":1,"5491":1,"5495":1,"10985":1,"10986":2,"10987":1,"54928":1,"54929":1,"322":17,"323":20,"128":81,"129":72,"130":51,"644":5,"645":5,"118":129,"119":128,"120":128,"121":124,"122":116,"123":111,"124":104,"125":97,"126":96,"127":91,"131":18,"257":38,"258":32,"259":22,"1287":5,"1288":5,"639":11,"640":11,"255":21,"256":38,"260":7,"514":24,"515":21,"516":13,"2574":3,"2575":3,"642":11,"643":11,"1284":6,"1285":6,"513":17,"517":5,"1029":11,"1030":10,"1031":7,"5149":1,"5150":1,"2572":2,"2573":2,"1282":5,"1283":5,"637":5,"638":5,"254":5,"512":6,"1028":9,"1032":3,"2059":6,"2060":5,"2061":3,"10299":1,"10300":1,"5147":2,"5148":2,"2569":3,"2570":3,"1027":4,"2058":4,"2062":1,"4119":2,"4120":2,"4121":2,"37075":1,"37076":1,"10294":1,"10295":1,"5144":1,"5145":1,"2057":1,"4117":2,"4118":3,"4122":1,"8238":1,"8239":2,"8240":1,"41194":1,"41195":1,"484":1,"485":1,"193":38,"194":29,"195":15,"967":1,"968":1,"479":11,"480":11,"191":29,"192":42,"196":2,"386":19,"387":16,"388":9,"1932":1,"1933":1,"482":11,"483":11,"962":5,"963":5,"477":9,"478":9,"190":9,"384":14,"385":21,"389":1,"772":11,"773":9,"774":5,"3862":1,"3863":1,"964":6,"965":6,"1927":3,"1928":3,"959":4,"960":4,"770":6,"771":10,"775":1,"1544":6,"1545":5,"1546":3,"7724":1,"7725":1,"1929":3,"1930":3,"3859":2,"3860":2,"1543":4,"1547":1,"3089":2,"3090":2,"3091":2,"27805":1,"27806":1,"7719":1,"7720":1,"3857":1,"3858":1,"1924":1,"1925":1,"769":2,"1542":1,"3087":2,"3088":2,"3092":1,"6178":1,"6179":2,"6180":1,"30894":1,"30895":1,"362":9,"363":9,"144":41,"145":37,"146":27,"724":4,"725":4,"359":11,"360":11,"143":33,"147":10,"289":19,"290":17,"291":12,"1449":1,"1450":1,"722":5,"723":5,"357":10,"358":10,"142":14,"288":17,"292":4,"579":10,"580":9,"581":5,"2897":1,"2898":1,"1444":2,"1445":2,"719":5,"720":5,"287":9,"577":6,"578":9,"582":1,"1158":5,"1159":4,"1160":3,"5792":1,"5793":1,"1447":3,"1448":3,"2892":2,"2893":2,"1442":2,"1443":2,"717":2,"718":2,"354":2,"355":2,"141":2,"286":2,"576":2,"1156":2,"1157":5,"1161":1,"2316":3,"2317":3,"2318":2,"20852":1,"20853":1,"2894":1,"2895":1,"5789":1,"5790":1,"2315":1,"2319":1,"4633":1,"4634":2,"4635":1,"23169":1,"23170":1,"544":2,"545":2,"217":18,"218":15,"219":9,"1087":2,"1088":2,"539":5,"540":5,"215":13,"216":19,"220":2,"434":10,"435":9,"436":6,"2172":2,"2173":2,"542":6,"543":6,"1082":3,"1083":3,"537":4,"538":4,"214":4,"432":5,"433":9,"437":2,"868":5,"869":5,"870":4,"4344":1,"4345":1,"1084":2,"1085":2,"2169":1,"2170":1,"867":3,"871":2,"1737":3,"1738":3,"1739":2,"15638":1,"15639":1,"4342":1,"4343":1,"2167":1,"2168":1,"1079":1,"1080":1,"431":1,"866":1,"1736":1,"1740":1,"3475":1,"3476":2,"3477":1,"17376":1,"17377":1,"407":5,"408":5,"162":21,"163":18,"164":13,"814":2,"815":2,"404":6,"405":6,"161":17,"165":5,"325":12,"326":9,"327":6,"1629":1,"1630":1,"812":3,"813":3,"402":6,"403":6,"160":6,"324":10,"328":2,"651":5,"652":4,"653":4,"3257":1,"3258":1,"1624":2,"1625":2,"809":3,"810":3,"649":2,"650":5,"654":2,"1302":3,"1303":3,"1304":2,"11726":1,"11727":1,"1627":1,"1628":1,"3254":1,"3255":1,"1301":1,"1305":1,"2605":1,"2606":2,"2607":1,"13029":1,"13030":1,"244":10,"245":8,"246":5,"242":5,"243":10,"247":1,"488":6,"489":5,"490":3,"2445":1,"487":4,"491":1,"977":2,"978":2,"979":2,"8794":1,"8795":1,"604":1,"605":1,"241":1,"486":1,"975":1,"976":2,"980":1,"1954":1,"1955":2,"1956":1,"9771":1,"9772":1,"183":9,"184":8,"185":5,"181":6,"182":9,"186":1,"366":5,"367":4,"368":3,"452":2,"453":2,"180":2,"364":2,"365":5,"369":1,"732":3,"733":3,"734":2,"6593":1,"6594":1,"731":1,"735":1,"1465":1,"1466":2,"1467":1,"7327":1,"137":10,"138":8,"139":5,"339":3,"135":5,"136":10,"140":1,"274":6,"275":5,"276":3,"273":4,"277":1,"549":2,"550":2,"551":2,"4943":1,"4944":1,"1369":1,"682":1,"337":1,"338":1,"134":1,"272":1,"547":1,"548":2,"552":1,"1098":1,"1099":2,"1100":1,"205":5,"206":5,"207":4,"204":3,"208":2,"411":3,"412":3,"413":2,"3705":1,"3706":1,"509":1,"510":1,"203":1,"410":1,"414":1,"823":1,"824":2,"825":1,"156":3,"157":1,"309":3,"310":2,"2777":1,"2778":1,"311":1,"617":1,"618":2,"619":1,"3086":1,"232":2,"233":2,"2081":1,"2082":1,"574":1,"575":1,"234":1,"462":1,"463":2,"464":1,"2312":1,"2313":1,"175":2,"1559":1,"1560":1,"176":1,"347":2,"348":1,"1732":1,"1733":1,"1167":1,"1168":1,"132":1,"261":1,"1297":1,"1298":1,"874":1,"875":1,"971":1,"972":1,"726":1,"727":1,"224":1,"167":1},"product_classical":{"2,1":1738,"2,2":1738,"2,3":1738,"2,4":1738,"2,5":1738,"2,6":1738,"2,7":1738,"2,8":1738,"2,9":1738,"2,10":1738,"2,11":1738,"2,12":1738,"2,13":1738,"2,14":1738,"2,15":1738,"2,16":1738,"2,17":1738,"2,18":1738,"2,19":1738,"2,20":1738,"2,21":1738,"2,22":1738,"2,23":1738,"2,24":1738,"2,25":1738,"2,26":1738,"2,27":1738,"2,28":1738,"2,29":1738,"2,30":1738,"2,31":1738,"2,32":1738,"2,33":1738,"2,34":1737,"2,35":1736,"2,36":1736,"2,37":1736,"2,38":1736,"2,39":1736,"2,40":1736,"2,41":1736,"2,42":1736,"2,43":1736,"2,44":1736,"2,45":1735,"2,46":1734,"2,47":1734,"2,48":1734,"2,49":1734,"2,50":1734,"2,51":1734,"2,52":1734,"2,53":1734,"2,54":1734,"2,55":1734,"2,56":1734,"2,57":1734,"2,58":1734,"2,59":1734,"2,60":1734,"2,61":1733,"2,62":1732,"2,63":1715,"2,64":1697,"2,65":1696,"2,66":1677,"2,67":1652,"2,68":1645,"2,69":1640,"2,70":1620,"2,71":1584,"2,72":1561,"2,73":1537,"2,74":1446,"2,75":1306,"2,76":1217,"2,77":1112,"2,78":998,"2,153":64,"2,154":26,"2,152":39,"2,306":25,"2,307":4,"2,305":28,"2,611":15,"2,612":4,"2,610":12,"2,1221":8,"2,1222":4,"2,304":7,"2,1220":4,"2,2442":4,"2,2443":1,"2,2441":3,"2,4883":2,"2,4884":1,"2,609":1,"2,4882":1,"2,9766":1,"2,9767":1,"2,79":963,"2,80":946,"2,81":935,"2,82":923,"2,83":900,"2,84":845,"2,85":787,"2,86":743,"2,87":677,"2,88":639,"2,89":636,"2,90":629,"2,91":623,"2,92":618,"2,93":610,"2,94":597,"2,95":566,"2,96":542,"2,97":520,"2,98":488,"2,99":475,"2,100":474,"2,101":472,"2,102":468,"2,103":465,"2,104":461,"2,105":458,"2,106":454,"2,107":440,"2,108":428,"2,109":416,"2,110":399,"2,111":392,"2,112":368,"2,113":304,"2,114":261,"2,115":214,"2,116":150,"2,229":32,"2,230":19,"2,458":16,"2,459":8,"2,228":13,"2,457":8,"2,916":8,"2,917":3,"2,915":5,"2,1831":4,"2,1832":3,"2,3662":2,"2,3663":2,"2,1830":1,"2,7324":1,"2,7325":1,"2,172":32,"2,173":14,"2,171":18,"2,344":14,"2,345":4,"2,343":12,"2,687":8,"2,688":4,"2,686":4,"2,1374":4,"2,1375":1,"2,342":2,"2,1373":3,"2,2747":2,"2,2748":1,"2,2746":1,"2,5493":1,"2,5494":1,"2,117":129,"2,118":128,"2,119":128,"2,120":124,"2,121":116,"2,122":111,"2,123":104,"2,124":97,"2,125":96,"2,126":91,"2,127":64,"2,128":37,"2,129":32,"2,130":17,"2,258":16,"2,259":5,"2,257":11,"2,515":8,"2,516":5,"2,1030":4,"2,1031":3,"2,514":3,"2,2060":2,"2,2061":1,"2,1029":1,"2,2059":1,"2,4120":1,"2,4121":1,"2,194":12,"2,195":1,"2,193":15,"2,387":7,"2,388":1,"2,192":4,"2,386":7,"2,773":4,"2,774":1,"2,772":3,"2,1545":2,"2,1546":1,"2,385":1,"2,1544":1,"2,3090":1,"2,3091":1,"2,145":16,"2,146":9,"2,290":8,"2,291":4,"2,144":7,"2,289":4,"2,580":4,"2,581":1,"2,579":3,"2,1159":2,"2,1160":1,"2,1158":1,"2,2317":1,"2,2318":1,"2,218":7,"2,219":2,"2,217":6,"2,435":4,"2,436":2,"2,434":2,"2,869":2,"2,870":2,"2,216":1,"2,1738":1,"2,1739":1,"2,163":8,"2,164":5,"2,326":4,"2,327":2,"2,162":3,"2,325":2,"2,652":2,"2,653":1,"2,651":1,"2,1303":1,"2,1304":1,"2,245":4,"2,246":1,"2,244":3,"2,489":2,"2,490":1,"2,488":1,"2,978":1,"2,979":1,"2,184":4,"2,185":1,"2,183":3,"2,367":2,"2,368":1,"2,366":1,"2,733":1,"2,734":1,"2,138":4,"2,139":1,"2,137":3,"2,275":2,"2,276":1,"2,274":1,"2,550":1,"2,551":1,"2,206":2,"2,207":2,"2,412":1,"2,413":1,"2,155":2,"2,156":1,"2,309":1,"2,310":1,"2,232":1,"2,233":1,"2,174":1,"2,175":1,"2,131":1},"product_ntt":{"76,307":27,"77,306":27,"77,307":27,"78,306":27,"74,77":173,"75,78":142,"74,78":70,"75,79":28,"75,77":174,"76,78":73,"76,79":30,"152,613":4,"153,612":4,"153,613":4,"154,612":4,"75,305":43,"76,304":43,"76,305":43,"77,304":43,"74,76":120,"75,76":60,"76,77":44,"151,153":86,"152,154":52,"151,154":85,"152,155":27,"152,153":26,"153,154":5,"153,155":7,"305,1223":4,"306,1222":4,"306,1223":4,"307,1222":4,"151,609":22,"152,608":22,"152,609":22,"153,608":22,"75,303":43,"76,302":43,"76,303":43,"77,302":43,"73,76":60,"73,77":43,"150,152":39,"150,153":77,"151,152":22,"303,306":42,"304,307":29,"303,307":14,"304,308":4,"304,306":43,"305,307":15,"305,308":4,"610,2443":4,"611,2442":4,"611,2443":4,"612,2442":4,"152,611":21,"153,610":21,"153,611":21,"154,610":21,"150,154":38,"151,155":21,"304,1219":10,"305,1218":10,"305,1219":10,"306,1218":10,"151,607":17,"152,606":17,"152,607":17,"153,606":17,"74,301":17,"75,300":17,"75,301":17,"76,300":17,"73,75":18,"74,75":17,"149,152":17,"149,153":17,"302,305":17,"302,306":10,"303,305":35,"608,611":22,"609,612":19,"608,612":10,"609,613":4,"609,611":21,"610,612":9,"610,613":4,"1220,4885":1,"1221,4884":1,"1221,4885":1,"1222,4884":1,"304,1221":11,"305,1220":11,"305,1221":11,"306,1220":11,"304,305":18,"305,306":11,"609,2441":5,"610,2440":5,"610,2441":5,"611,2440":5,"608,610":13,"609,610":6,"610,611":5,"1219,1221":11,"1220,1222":8,"1219,1222":11,"1220,1223":4,"1220,1221":4,"1221,1222":1,"1221,1223":1,"2441,9767":1,"2442,9766":1,"2442,9767":1,"2443,9766":1,"1219,4881":3,"1220,4880":3,"1220,4881":3,"1221,4880":3,"609,2439":6,"610,2438":6,"610,2439":6,"611,2438":6,"303,1217":7,"304,1216":7,"304,1217":7,"305,1216":7,"302,304":7,"303,304":7,"607,610":7,"607,611":6,"1218,1220":4,"1218,1221":8,"1219,1220":3,"2439,2442":5,"2440,2443":5,"2439,2443":2,"2440,2444":1,"2440,2442":6,"2441,2443":3,"2441,2444":1,"4882,19533":1,"4883,19532":1,"4883,19533":1,"4884,19532":1,"1220,4883":3,"1221,4882":3,"1221,4883":3,"1222,4882":3,"1218,1222":4,"1219,1223":3,"2440,9765":2,"2441,9764":2,"2441,9765":2,"2442,9764":2,"2439,2441":3,"2440,2441":2,"2441,2442":2,"4881,4883":3,"4882,4884":3,"4881,4884":2,"4882,4885":1,"4882,4883":2,"4883,4884":1,"4883,4885":1,"9765,78125":1,"9766,78124":1,"9766,78125":1,"9767,78124":1,"4881,19529":1,"4882,19528":1,"4882,19529":1,"4883,19528":1,"2440,9763":1,"2441,9762":1,"2441,9763":1,"2442,9762":1,"1219,4879":1,"1220,4878":1,"1220,4879":1,"1221,4878":1,"608,2437":1,"609,2436":1,"609,2437":1,"610,2436":1,"607,609":1,"608,609":1,"1217,1220":1,"1217,1221":1,"2438,2441":1,"2438,2442":1,"4880,4882":1,"4880,4883":1,"4881,4882":1,"9763,9766":1,"9764,9767":2,"9763,9767":1,"9764,9768":1,"9764,9766":1,"9765,9767":1,"9765,9768":1,"19530,78125":1,"19531,78124":1,"19531,78125":1,"19532,78124":1,"114,459":19,"115,458":19,"115,459":19,"116,458":19,"112,115":86,"113,116":82,"112,116":41,"113,117":19,"113,115":86,"114,116":43,"114,117":21,"228,917":8,"229,916":8,"229,917":8,"230,916":8,"113,457":21,"114,456":21,"114,457":21,"115,456":21,"112,114":47,"113,114":23,"114,115":22,"227,229":43,"228,230":38,"227,230":43,"228,231":19,"228,229":19,"229,230":8,"229,231":8,"457,1833":3,"458,1832":3,"458,1833":3,"459,1832":3,"228,915":11,"229,914":11,"229,915":11,"230,914":11,"113,455":22,"114,454":22,"114,455":22,"115,454":22,"111,114":24,"111,115":22,"226,229":26,"226,230":13,"227,231":11,"456,458":22,"457,459":17,"456,459":21,"457,460":8,"457,458":9,"458,459":3,"458,460":3,"915,3663":3,"916,3662":3,"916,3663":3,"917,3662":3,"456,1829":6,"457,1828":6,"457,1829":6,"458,1828":6,"227,913":11,"228,912":11,"228,913":11,"229,912":11,"226,228":13,"227,228":11,"455,457":8,"455,458":15,"456,457":6,"913,916":10,"914,917":11,"913,917":5,"914,918":3,"914,916":11,"915,917":6,"915,918":3,"1830,7325":2,"1831,7324":2,"1831,7325":2,"1832,7324":2,"457,1831":5,"458,1830":5,"458,1831":5,"459,1830":5,"455,459":7,"456,460":5,"914,3661":3,"915,3660":3,"915,3661":3,"916,3660":3,"913,915":5,"914,915":3,"915,916":3,"1829,1831":5,"1830,1832":6,"1829,1832":5,"1830,1833":3,"1830,1831":3,"1831,1832":2,"1831,1833":2,"3661,14649":1,"3662,14648":1,"3662,14649":1,"3663,14648":1,"1830,7323":1,"1831,7322":1,"1831,7323":1,"1832,7322":1,"914,3659":2,"915,3658":2,"915,3659":2,"916,3658":2,"456,1827":2,"457,1826":2,"457,1827":2,"458,1826":2,"227,911":2,"228,910":2,"228,911":2,"229,910":2,"112,453":2,"113,452":2,"113,453":2,"114,452":2,"111,113":2,"112,113":2,"225,228":2,"225,229":2,"454,457":2,"454,458":2,"912,915":2,"912,916":2,"1828,1831":2,"1828,1832":1,"1829,1833":1,"3660,3662":2,"3661,3663":3,"3660,3663":3,"3661,3664":2,"3661,3662":1,"3662,3663":1,"3662,3664":1,"7323,58593":1,"7324,58592":1,"7324,58593":1,"7325,58592":1,"3661,14647":1,"3662,14646":1,"3662,14647":1,"3663,14646":1,"1829,7321":1,"1830,7320":1,"1830,7321":1,"1831,7320":1,"1828,1830":1,"1829,1830":1,"3659,3662":1,"3659,3663":1,"3660,3664":1,"7322,7324":1,"7323,7325":2,"7322,7325":1,"7323,7326":1,"7323,7324":1,"7324,7325":1,"7324,7326":1,"14647,58593":1,"14648,58592":1,"14648,58593":1,"14649,58592":1,"85,345":15,"86,344":15,"86,345":15,"87,344":15,"84,86":86,"85,87":74,"84,87":87,"85,88":38,"85,86":36,"86,87":16,"86,88":17,"171,689":4,"172,688":4,"172,689":4,"173,688":4,"85,343":22,"86,342":22,"86,343":22,"87,342":22,"83,86":57,"83,87":29,"84,88":22,"170,172":43,"171,173":29,"170,173":42,"171,174":15,"171,172":15,"172,173":4,"172,174":5,"343,1375":4,"344,1374":4,"344,1375":4,"345,1374":4,"170,685":11,"171,684":11,"171,685":11,"172,684":11,"84,341":21,"85,340":21,"85,341":21,"86,340":21,"83,85":28,"84,85":21,"169,171":18,"169,172":35,"170,171":11,"341,344":21,"342,345":18,"341,345":9,"342,346":4,"342,344":21,"343,345":9,"343,346":4,"686,2749":1,"687,2748":1,"687,2749":1,"688,2748":1,"171,687":10,"172,686":10,"172,687":10,"173,686":10,"169,173":17,"170,174":10,"342,1373":5,"343,1372":5,"343,1373":5,"344,1372":5,"341,343":14,"342,343":7,"343,344":5,"685,687":10,"686,688":7,"685,688":11,"686,689":4,"686,687":3,"687,688":1,"687,689":1,"1373,5495":1,"1374,5494":1,"1374,5495":1,"1375,5494":1,"685,2745":2,"686,2744":2,"686,2745":2,"687,2744":2,"342,1371":5,"343,1370":5,"343,1371":5,"344,1370":5,"170,683":7,"171,682":7,"171,683":7,"172,682":7,"84,339":7,"85,338":7,"85,339":7,"86,338":7,"82,85":7,"82,86":7,"168,171":7,"168,172":7,"340,343":7,"340,344":5,"684,686":4,"684,687":9,"685,686":2,"1371,1374":6,"1372,1375":5,"1371,1375":3,"1372,1376":1,"1372,1374":5,"1373,1375":2,"1373,1376":1,"2746,10987":1,"2747,10986":1,"2747,10987":1,"2748,10986":1,"686,2747":3,"687,2746":3,"687,2747":3,"688,2746":3,"684,688":5,"685,689":3,"1372,5491":2,"1373,5490":2,"1373,5491":2,"1374,5490":2,"685,2743":2,"686,2742":2,"686,2743":2,"687,2742":2,"341,1369":2,"342,1368":2,"342,1369":2,"343,1368":2,"340,342":2,"341,342":2,"683,686":2,"683,687":2,"1370,1373":2,"1370,1374":2,"1371,1373":3,"2744,2747":2,"2745,2748":3,"2744,2748":1,"2745,2749":1,"2745,2747":3,"2746,2748":2,"2746,2749":1,"5492,43944":1,"5493,43943":1,"5493,43944":1,"5494,43943":1,"1372,5493":1,"1373,5492":1,"1373,5493":1,"1374,5492":1,"1372,1373":1,"1373,1374":1,"2745,10985":1,"2746,10984":1,"2746,10985":1,"2747,10984":1,"2744,2746":1,"2745,2746":1,"2746,2747":1,"5491,5493":1,"5492,5494":2,"5491,5494":1,"5492,5495":1,"5492,5493":1,"5493,5494":1,"5493,5495":1,"10985,43944":1,"10986,43943":1,"10986,43944":1,"10987,43943":1,"64,259":17,"65,258":17,"65,259":17,"66,258":17,"62,65":17,"63,66":35,"62,66":17,"63,67":17,"63,65":18,"64,66":19,"64,67":18,"128,517":5,"129,516":5,"129,517":5,"130,516":5,"127,129":43,"128,130":33,"127,130":43,"128,131":17,"128,129":16,"129,130":6,"129,131":7,"257,1031":5,"258,1030":5,"258,1031":5,"259,1030":5,"127,513":11,"128,512":11,"128,513":11,"129,512":11,"126,128":16,"126,129":32,"127,128":11,"255,258":21,"256,259":21,"255,259":10,"256,260":5,"256,258":22,"257,259":11,"257,260":5,"514,2061":3,"515,2060":3,"515,2061":3,"516,2060":3,"128,515":11,"129,514":11,"129,515":11,"130,514":11,"126,130":16,"127,131":11,"256,1029":6,"257,1028":6,"257,1029":6,"258,1028":6,"255,257":11,"256,257":6,"257,258":6,"513,515":11,"514,516":11,"513,516":10,"514,517":5,"514,515":6,"515,516":3,"515,517":3,"1029,4121":1,"1030,4120":1,"1030,4121":1,"1031,4120":1,"514,2059":2,"515,2058":2,"515,2059":2,"516,2058":2,"256,1027":5,"257,1026":5,"257,1027":5,"258,1026":5,"127,511":5,"128,510":5,"128,511":5,"129,510":5,"125,128":5,"125,129":5,"254,257":5,"254,258":5,"512,515":5,"512,516":2,"513,517":2,"1028,1030":5,"1029,1031":5,"1028,1031":6,"1029,1032":3,"1029,1030":2,"1030,1031":1,"1030,1032":1,"2059,8241":1,"2060,8240":1,"2060,8241":1,"2061,8240":1,"1029,4119":2,"1030,4118":2,"1030,4119":2,"1031,4118":2,"513,2057":3,"514,2056":3,"514,2057":3,"515,2056":3,"512,514":3,"513,514":3,"1027,1030":3,"1027,1031":2,"1028,1032":2,"2058,2060":3,"2059,2061":3,"2058,2061":2,"2059,2062":1,"2059,2060":2,"2060,2061":1,"2060,2062":1,"4119,32957":1,"4120,32956":1,"4120,32957":1,"4121,32956":1,"2058,8237":1,"2059,8236":1,"2059,8237":1,"2060,8236":1,"1028,4117":1,"1029,4116":1,"1029,4117":1,"1030,4116":1,"1027,1029":1,"1028,1029":1,"2057,2059":1,"2057,2060":1,"2058,2059":1,"4117,4120":1,"4118,4121":2,"4117,4121":1,"4118,4122":1,"4118,4120":1,"4119,4121":1,"4119,4122":1,"8238,32957":1,"8239,32956":1,"8239,32957":1,"8240,32956":1,"96,389":1,"97,388":1,"97,389":1,"98,388":1,"95,97":43,"96,98":25,"95,98":44,"96,99":14,"96,97":12,"97,98":1,"97,99":2,"193,775":1,"194,774":1,"194,775":1,"195,774":1,"95,385":11,"96,384":11,"96,385":11,"97,384":11,"94,96":20,"94,97":40,"95,96":11,"191,194":21,"192,195":13,"191,195":6,"192,196":1,"192,194":22,"193,195":7,"193,196":1,"386,1547":1,"387,1546":1,"387,1547":1,"388,1546":1,"96,387":11,"97,386":11,"97,387":11,"98,386":11,"94,98":20,"95,99":12,"192,771":5,"193,770":5,"193,771":5,"194,770":5,"95,383":9,"96,382":9,"96,383":9,"97,382":9,"93,96":9,"93,97":9,"190,193":9,"190,194":5,"191,193":19,"384,387":11,"385,388":8,"384,388":4,"385,389":1,"385,387":11,"386,388":4,"386,389":1,"772,3091":1,"773,3090":1,"773,3091":1,"774,3090":1,"192,773":6,"193,772":6,"193,773":6,"194,772":6,"192,193":10,"193,194":6,"385,1543":3,"386,1542":3,"386,1543":3,"387,1542":3,"191,769":4,"192,768":4,"192,769":4,"193,768":4,"190,192":4,"191,192":4,"383,386":4,"383,387":3,"384,386":8,"770,773":5,"771,774":5,"770,774":2,"771,775":1,"771,773":6,"772,774":3,"772,775":1,"1544,6181":1,"1545,6180":1,"1545,6181":1,"1546,6180":1,"385,1545":3,"386,1544":3,"386,1545":3,"387,1544":3,"385,386":4,"386,387":3,"771,3089":2,"772,3088":2,"772,3089":2,"773,3088":2,"770,772":3,"771,772":2,"772,773":2,"1543,1545":3,"1544,1546":3,"1543,1546":2,"1544,1547":1,"1544,1545":2,"1545,1546":1,"1545,1547":1,"3089,24717":1,"3090,24716":1,"3090,24717":1,"3091,24716":1,"1543,6177":1,"1544,6176":1,"1544,6177":1,"1545,6176":1,"771,3087":1,"772,3086":1,"772,3087":1,"773,3086":1,"384,1541":1,"385,1540":1,"385,1541":1,"386,1540":1,"383,385":1,"384,385":1,"769,772":1,"769,773":1,"1542,1544":1,"1542,1545":1,"1543,1544":1,"3087,3090":1,"3088,3091":2,"3087,3091":1,"3088,3092":1,"3088,3090":1,"3089,3091":1,"3089,3092":1,"6178,24717":1,"6179,24716":1,"6179,24717":1,"6180,24716":1,"72,291":9,"73,290":9,"73,291":9,"74,290":9,"70,73":42,"71,74":40,"70,74":19,"71,75":9,"71,73":44,"72,74":22,"72,75":10,"144,581":4,"145,580":4,"145,581":4,"146,580":4,"71,289":11,"72,288":11,"72,289":11,"73,288":11,"70,72":25,"71,72":13,"72,73":12,"143,145":21,"144,146":18,"143,146":21,"144,147":9,"144,145":9,"145,146":4,"145,147":4,"289,1161":1,"290,1160":1,"290,1161":1,"291,1160":1,"144,579":5,"145,578":5,"145,579":5,"146,578":5,"71,287":10,"72,286":10,"72,287":10,"73,286":10,"69,72":12,"69,73":10,"142,145":14,"142,146":7,"143,147":5,"288,290":10,"289,291":7,"288,291":11,"289,292":4,"289,290":3,"290,291":1,"290,292":1,"579,2319":1,"580,2318":1,"580,2319":1,"581,2318":1,"288,1157":2,"289,1156":2,"289,1157":2,"290,1156":2,"143,577":5,"144,576":5,"144,577":5,"145,576":5,"142,144":7,"143,144":5,"287,289":4,"287,290":9,"288,289":2,"577,580":6,"578,581":5,"577,581":3,"578,582":1,"578,580":5,"579,581":2,"579,582":1,"1158,4635":1,"1159,4634":1,"1159,4635":1,"1160,4634":1,"289,1159":3,"290,1158":3,"290,1159":3,"291,1158":3,"287,291":5,"288,292":3,"578,2315":2,"579,2314":2,"579,2315":2,"580,2314":2,"288,1155":2,"289,1154":2,"289,1155":2,"290,1154":2,"143,575":2,"144,574":2,"144,575":2,"145,574":2,"70,285":2,"71,284":2,"71,285":2,"72,284":2,"69,71":3,"70,71":2,"141,144":2,"141,145":2,"286,289":2,"286,290":2,"576,579":2,"576,580":2,"577,579":3,"1156,1159":2,"1157,1160":3,"1156,1160":1,"1157,1161":1,"1157,1159":3,"1158,1160":2,"1158,1161":1,"2316,18537":1,"2317,18536":1,"2317,18537":1,"2318,18536":1,"578,2317":1,"579,2316":1,"579,2317":1,"580,2316":1,"578,579":1,"579,580":1,"1157,4633":1,"1158,4632":1,"1158,4633":1,"1159,4632":1,"1156,1158":1,"1157,1158":1,"1158,1159":1,"2315,2317":1,"2316,2318":2,"2315,2318":1,"2316,2319":1,"2316,2317":1,"2317,2318":1,"2317,2319":1,"4633,18537":1,"4634,18536":1,"4634,18537":1,"4635,18536":1,"108,437":2,"109,436":2,"109,437":2,"110,436":2,"107,109":21,"108,110":14,"107,110":21,"108,111":7,"108,109":7,"109,110":2,"109,111":2,"217,871":2,"218,870":2,"218,871":2,"219,870":2,"107,433":5,"108,432":5,"108,433":5,"109,432":5,"106,108":9,"106,109":18,"107,108":5,"215,218":11,"216,219":9,"215,219":5,"216,220":2,"216,218":10,"217,219":4,"217,220":2,"434,1739":2,"435,1738":2,"435,1739":2,"436,1738":2,"108,435":6,"109,434":6,"109,435":6,"110,434":6,"106,110":9,"107,111":5,"216,867":3,"217,866":3,"217,867":3,"218,866":3,"107,431":4,"108,430":4,"108,431":4,"109,430":4,"105,108":4,"105,109":4,"214,217":4,"214,218":3,"215,217":7,"432,435":5,"433,436":6,"432,436":3,"433,437":2,"433,435":5,"434,436":3,"434,437":2,"868,3477":1,"869,3476":1,"869,3477":1,"870,3476":1,"216,869":2,"217,868":2,"217,869":2,"218,868":2,"216,217":3,"217,218":2,"433,1737":1,"434,1736":1,"434,1737":1,"435,1736":1,"432,434":2,"433,434":1,"434,435":1,"867,869":2,"868,870":3,"867,870":3,"868,871":2,"868,869":1,"869,870":1,"869,871":1,"1737,13902":1,"1738,13901":1,"1738,13902":1,"1739,13901":1,"868,3475":1,"869,3474":1,"869,3475":1,"870,3474":1,"433,1735":1,"434,1734":1,"434,1735":1,"435,1734":1,"215,865":1,"216,864":1,"216,865":1,"217,864":1,"214,216":1,"215,216":1,"431,434":1,"431,435":1,"866,869":1,"866,870":1,"867,871":1,"1736,1738":1,"1737,1739":2,"1736,1739":1,"1737,1740":1,"1737,1738":1,"1738,1739":1,"1738,1740":1,"3475,13902":1,"3476,13901":1,"3476,13902":1,"3477,13901":1,"81,327":5,"82,326":5,"82,327":5,"83,326":5,"79,82":22,"80,83":21,"79,83":11,"80,84":5,"80,82":21,"81,83":10,"81,84":5,"162,653":2,"163,652":2,"163,653":2,"164,652":2,"80,325":6,"81,324":6,"81,325":6,"82,324":6,"79,81":11,"80,81":5,"81,82":5,"161,163":11,"162,164":10,"161,164":11,"162,165":5,"162,163":5,"163,164":2,"163,165":2,"325,1305":1,"326,1304":1,"326,1305":1,"327,1304":1,"162,651":3,"163,650":3,"163,651":3,"164,650":3,"80,323":6,"81,322":6,"81,323":6,"82,322":6,"78,81":6,"78,82":6,"160,163":6,"160,164":3,"161,165":3,"324,326":6,"325,327":5,"324,327":5,"325,328":2,"325,326":3,"326,327":1,"326,328":1,"651,2607":1,"652,2606":1,"652,2607":1,"653,2606":1,"324,1301":2,"325,1300":2,"325,1301":2,"326,1300":2,"161,649":3,"162,648":3,"162,649":3,"163,648":3,"160,162":3,"161,162":3,"323,325":2,"323,326":3,"324,325":2,"649,652":2,"650,653":3,"649,653":1,"650,654":1,"650,652":3,"651,653":2,"651,654":1,"1302,10425":1,"1303,10424":1,"1303,10425":1,"1304,10424":1,"325,1303":1,"326,1302":1,"326,1303":1,"327,1302":1,"323,327":1,"324,328":1,"650,2605":1,"651,2604":1,"651,2605":1,"652,2604":1,"649,651":1,"650,651":1,"651,652":1,"1301,1303":1,"1302,1304":2,"1301,1304":1,"1302,1305":1,"1302,1303":1,"1303,1304":1,"1303,1305":1,"2605,10425":1,"2606,10424":1,"2606,10425":1,"2607,10424":1,"122,491":1,"123,490":1,"123,491":1,"124,490":1,"120,123":11,"121,124":8,"120,124":4,"121,125":1,"121,123":11,"122,124":4,"122,125":1,"244,979":1,"245,978":1,"245,979":1,"246,978":1,"121,487":3,"122,486":3,"122,487":3,"123,486":3,"119,122":4,"119,123":3,"120,122":8,"242,245":5,"243,246":5,"242,246":2,"243,247":1,"243,245":6,"244,246":3,"244,247":1,"488,1957":1,"489,1956":1,"489,1957":1,"490,1956":1,"121,489":3,"122,488":3,"122,489":3,"123,488":3,"121,122":4,"122,123":3,"243,977":2,"244,976":2,"244,977":2,"245,976":2,"242,244":3,"243,244":2,"244,245":2,"487,489":3,"488,490":3,"487,490":2,"488,491":1,"488,489":2,"489,490":1,"489,491":1,"977,7818":1,"978,7817":1,"978,7818":1,"979,7817":1,"487,1953":1,"488,1952":1,"488,1953":1,"489,1952":1,"243,975":1,"244,974":1,"244,975":1,"245,974":1,"120,485":1,"121,484":1,"121,485":1,"122,484":1,"119,121":1,"120,121":1,"241,244":1,"241,245":1,"486,488":1,"486,489":1,"487,488":1,"975,978":1,"976,979":2,"975,979":1,"976,980":1,"976,978":1,"977,979":1,"977,980":1,"1954,7818":1,"1955,7817":1,"1955,7818":1,"1956,7817":1,"91,369":1,"92,368":1,"92,369":1,"93,368":1,"90,92":10,"91,93":7,"90,93":11,"91,94":4,"91,92":3,"92,93":1,"92,94":1,"183,735":1,"184,734":1,"184,735":1,"185,734":1,"90,365":2,"91,364":2,"91,365":2,"92,364":2,"89,91":4,"89,92":9,"90,91":2,"181,184":6,"182,185":5,"181,185":3,"182,186":1,"182,184":5,"183,185":2,"183,186":1,"366,1467":1,"367,1466":1,"367,1467":1,"368,1466":1,"91,367":3,"92,366":3,"92,367":3,"93,366":3,"89,93":5,"90,94":3,"182,731":2,"183,730":2,"183,731":2,"184,730":2,"90,363":2,"91,362":2,"91,363":2,"92,362":2,"88,91":2,"88,92":2,"180,183":2,"180,184":2,"181,183":3,"364,367":2,"365,368":3,"364,368":1,"365,369":1,"365,367":3,"366,368":2,"366,369":1,"732,5862":1,"733,5861":1,"733,5862":1,"734,5861":1,"182,733":1,"183,732":1,"183,733":1,"184,732":1,"182,183":1,"183,184":1,"365,1465":1,"366,1464":1,"366,1465":1,"367,1464":1,"364,366":1,"365,366":1,"366,367":1,"731,733":1,"732,734":2,"731,734":1,"732,735":1,"732,733":1,"733,734":1,"733,735":1,"1465,5862":1,"1466,5861":1,"1466,5862":1,"1467,5861":1,"68,277":1,"69,276":1,"69,277":1,"70,276":1,"67,69":11,"68,70":8,"67,70":11,"68,71":4,"68,69":4,"69,70":1,"137,551":1,"138,550":1,"138,551":1,"139,550":1,"67,273":3,"68,272":3,"68,273":3,"69,272":3,"66,68":4,"66,69":8,"67,68":3,"135,138":5,"136,139":5,"135,139":2,"136,140":1,"136,138":6,"137,139":3,"137,140":1,"274,1101":1,"275,1100":1,"275,1101":1,"276,1100":1,"68,275":3,"69,274":3,"69,275":3,"70,274":3,"66,70":4,"67,71":3,"136,549":2,"137,548":2,"137,549":2,"138,548":2,"135,137":3,"136,137":2,"137,138":2,"273,275":3,"274,276":3,"273,276":2,"274,277":1,"274,275":2,"275,276":1,"275,277":1,"549,4395":1,"550,4394":1,"550,4395":1,"551,4394":1,"273,1097":1,"274,1096":1,"274,1097":1,"275,1096":1,"136,547":1,"137,546":1,"137,547":1,"138,546":1,"67,271":1,"68,270":1,"68,271":1,"69,270":1,"65,68":1,"65,69":1,"134,137":1,"134,138":1,"272,274":1,"272,275":1,"273,274":1,"547,550":1,"548,551":2,"547,551":1,"548,552":1,"548,550":1,"549,551":1,"549,552":1,"1098,4395":1,"1099,4394":1,"1099,4395":1,"1100,4394":1,"102,413":2,"103,412":2,"103,413":2,"104,412":2,"101,103":5,"102,104":6,"101,104":5,"102,105":3,"102,103":3,"103,104":2,"103,105":2,"205,825":1,"206,824":1,"206,825":1,"207,824":1,"102,411":1,"103,410":1,"103,411":1,"104,410":1,"100,103":2,"100,104":1,"101,105":1,"204,206":2,"205,207":3,"204,207":3,"205,208":2,"205,206":1,"206,207":1,"206,208":1,"411,3295":1,"412,3294":1,"412,3295":1,"413,3294":1,"205,823":1,"206,822":1,"206,823":1,"207,822":1,"101,409":1,"102,408":1,"102,409":1,"103,408":1,"100,102":1,"101,102":1,"203,206":1,"203,207":1,"204,208":1,"410,412":1,"411,413":2,"410,413":1,"411,414":1,"411,412":1,"412,413":1,"412,414":1,"823,3295":1,"824,3294":1,"824,3295":1,"825,3294":1,"77,311":1,"78,310":1,"78,311":1,"79,310":1,"76,80":1,"77,79":2,"77,80":1,"154,619":1,"155,618":1,"155,619":1,"156,618":1,"153,156":3,"152,156":1,"153,157":1,"154,156":2,"154,157":1,"308,2470":1,"309,2469":1,"309,2470":1,"310,2469":1,"76,309":1,"77,308":1,"77,309":1,"78,308":1,"77,78":1,"153,617":1,"154,616":1,"154,617":1,"155,616":1,"154,155":1,"307,309":1,"308,310":2,"307,310":1,"308,311":1,"308,309":1,"309,310":1,"309,311":1,"617,2470":1,"618,2469":1,"618,2470":1,"619,2469":1,"115,465":1,"116,464":1,"116,465":1,"117,464":1,"115,117":3,"115,118":1,"115,116":2,"116,117":1,"116,118":1,"231,1851":1,"232,1850":1,"232,1851":1,"233,1850":1,"114,461":1,"115,460":1,"115,461":1,"116,460":1,"229,232":1,"230,233":2,"229,233":1,"230,234":1,"230,232":1,"231,233":1,"231,234":1,"462,1851":1,"463,1850":1,"463,1851":1,"464,1850":1,"86,349":1,"87,348":1,"87,349":1,"88,348":1,"86,89":1,"87,88":1,"87,89":1,"173,1387":1,"174,1386":1,"174,1387":1,"175,1386":1,"172,175":2,"171,175":1,"172,176":1,"173,175":1,"173,176":1,"346,1387":1,"347,1386":1,"347,1387":1,"348,1386":1,"64,261":1,"65,260":1,"65,261":1,"66,260":1,"64,65":1,"65,66":1,"65,67":1,"129,1039":1,"130,1038":1,"130,1039":1,"131,1038":1,"129,132":1,"130,131":1,"130,132":1,"259,1039":1,"260,1038":1,"260,1039":1,"261,1038":1,"97,778":1,"98,777":1,"98,778":1,"99,777":1,"96,100":1,"97,100":1,"194,778":1,"195,777":1,"195,778":1,"196,777":1,"72,582":1,"73,581":1,"73,582":1,"74,581":1,"73,74":1,"145,582":1,"146,581":1,"146,582":1,"147,581":1,"60,243":1,"61,242":1,"61,243":1,"62,242":1,"44,181":1,"45,180":1,"45,181":1,"46,180":1,"33,135":1,"34,134":1,"34,135":1,"35,134":1},"monic":{"3":1,"2":1},"edf_draw":{"":1},"edf_powmod":{"2":1},"edf_constsub":{"2":1},"root_linear":{"":2}}
```
