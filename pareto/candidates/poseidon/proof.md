# Orchard r=1: deterministic two-round-skip collision with polynomial root finding

Target: `poseidon-orchard-r1-prefix-v1`. The state is [nk, rho, 2^65] over Pallas, with full rounds 0–3, partial
round(s) 4, full rounds 60–63 and digest lane 0. Cost model: `orchard-field-ram-v2`, so C = 216 + 21·1 = 237.

## 0. Result

| quantity | value |
| --- | --- |
| algorithm | deterministic (no random coins); success probability **1** |
| executed outcome | trial 0..0 run; trial 0 outputs the collision in `certificates/` |
| total charged primitive operations W | 19,302,457,333 (2^34.1681) |
| normalized time T = W / C | 8.144497e+07 = 2^26.279322; **claimed time_log2 = 26.28** |
| memory | ≤ 589,824 field words · 32 bytes + 1 MiB = 19,922,944 bytes = 2^24.2479; **claimed memory_log2_bytes = 24.25** |
| projected cost axis | time_log2 + max(0, memory_log2 − 20) = 30.53 |

The claim is fully explicit, with no heuristic. All work is charged, including all failed trials and a factor-2
safety allowance on the gcd count. The certificate collision has been checked against the
reference `verifier/poseidon.py:digest`.

## 1. A univariate line through the first two full rounds

Notation: RC_i are the round constants of round i, M is the deployed MDS matrix, and MI = M^(-1). Every
field element is canonical in [0, p). Since gcd(5, p − 1) = 1, x ↦ x^5 is a bijection of F_p, with inverse
x ↦ x^e5 where e5 = 5^(-1) mod (p − 1).

**Round 0.** It adds RC_0, applies x^5 to all lanes, then applies M. Lane 2 is fixed to 2^65, so its S-box output is the constant
K = (2^65 + RC_0[2])^5 = 0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c.
Write X0 = (nk + RC_0[0])^5 and X1 = (rho + RC_0[1])^5. Then the round-0 output is Y = M·(X0, X1, K)ᵀ.
The map (nk, rho) ↦ (X0, X1) is a bijection of F_p².

**Round 1.** The round-1 S-box input is u = Y + RC_1. A vector u arises from some (nk, rho) if and only if the third
coordinate of MI·(u − RC_1) equals K. If so, (nk, rho) is unique:
X = MI·(u − RC_1), nk = X0^e5 − RC_0[0], rho = X1^e5 − RC_0[1].

**The line.** Take u(t) = (t·D0, t·D1, C2) with
- D0 = MI[2][1] = 0x1ec7372574f3851bb4ddd4b4d6452256c5e4960d7424cd3776efab42d4fba90b,
- D1 = −MI[2][0] = 0x103445906ea65de68dc59c5f3f6254d9734d87cd741d1d666eeba35f8c5836f9,
- C2 = (K + Σ_j MI[2][j]·RC_1[j]) / MI[2][2] = 0x09b2d7e67acf680114704863d53135870423bf02a5b6414ddd79da0955bb7210.

MI[2][2] = 0x0d0c2efd6472f12a3c26fa4b7d25b1e487a7435d30f8be81adc8933c6f3c72ee ≠ 0. Then
MI[2][0]·tD0 + MI[2][1]·tD1 = 0 for every t, so the third coordinate of MI·(u(t) − RC_1) is −Σ_j MI[2][j]RC_1[j] +
MI[2][2]·C2 = K. Hence every t ∈ F_p gives a valid input pair inputs(t) = (nk(t), rho(t)).

**Lemma 1 (injectivity).** t ↦ inputs(t) is injective. u(t) is injective because D0 ≠ 0. u ↦ X is affine and
invertible, and X ↦ (nk, rho) is a bijection. So distinct t give distinct canonical pairs.

**Linearization.** The round-1 S-box outputs are (t^5·D0^5, t^5·D1^5, C2^5). Put s = t^5, a bijection with t = s^e5. Then
the round-1 output is the affine function A + s·B with A_i = M[i][2]·C2^5 and B_i = M[i][0]·D0^5 + M[i][1]·D1^5:
- A = (0x3ee27bfc9cfef88d27c792814848db51ceef97df9c0e5b45019550f933c44f57, 0x0ce52aaa238bc3ef49ca04d2538ba2bbff69145bc89d598a902f1616c1d228a2, 0x074cd8e568bd3331d9cc0068f9b5f3cf3ab985eb827eed4e2e35f7d2e5faddf7),
- B = (0x1d9ea4aadb298d5ff0585f6e5528d3b39e186bc7d11ecac983b2a50005ff6a80, 0x23a943cb8b60ec2bb5b00e193220410e586ac052e6b396154e60390348fe3ba8, 0x39c59dc5f76bc45cf562072a98bb22407b3e7ba493d05942d96f4e858199d234).

Define f(s) as lane 0 after applying the remaining rounds (full 2, 3, partial 4, full 60..63) to the state A + s·B.
By construction, f(s) = H(inputs(s^e5)) for every s ∈ F_p, where H is the r=1 digest.

**Lemma 2 (degree).** deg f ≤ 5^(6+1) = 78,125. Each lane of A + sB has degree ≤ 1. Constant addition and M preserve
the maximum lane degree, and x^5 multiplies it by at most 5. Rounds 2, 3, the 1 partial round(s) and the 4 final rounds give
5^(2+1+4). Composing the rounds symbolically over F_p confirms that the degree is exactly 78,125 (nonzero leading coefficient).
Only the upper bound is used below. If the degree were smaller, the same procedure would run with smaller n.

**Corollary.** Let s0 ∈ F_p and g(X) = f(X) − f(s0). Any root s1 ≠ s0 of g gives H(inputs(s1^e5)) = H(inputs(s0^e5))
with distinct canonical inputs (Lemma 1 and bijectivity of s ↦ s^e5). That is a collision for the target.

## 2. The procedure (deterministic)

Fixed stream: s0_i is the first value v = int_le(SHA-256(DOM ‖ le32(i) ‖ le32(ctr))), ctr = 0, 1, …, with v < p.
Here DOM = `HashSmash-Orchard-r1-s0-v1` (ASCII). The stream and its success criterion were fixed and committed before any of its trials
was run. Earlier development runs used a separate test stream; this preregistered stream is the only one used for the claim.

For i = 0, 1, 2, …:
1. Compute s0 = s0_i.
2. **Interpolate f.** Let L2 = 98,304 ≥ n + 1 and let ω be a primitive L2-th root of unity (3·2^32 divides p − 1). Evaluate f at ω^j for
   j < L2 using the explicit round function from the state A + ω^j·B. The value for ω^j is stored at the digit-reversed position of j,
   which is the order the forward transform produces and the inverse consumes. Then one inverse NTT of length L2 and a scaling by 1/L2
   give the coefficients of f. This is exact because deg f < L2.
3. Compute c = f(s0) by one evaluation of the round function. Set g = (f − c)/lc(f), which is monic of degree n.
4. **Barrett precomputation.** Compute I = rev_n(g)^(-1) mod X^n by Newton doubling from I = 1 (§3.2). Store
   Î = NTT_L(I)/L with L = 196,608 ≥ 2n − 1, and ĝ = NTT_L2(g)/L2.
5. **Powering.** The binary expansion of p is 1 followed by 0 bits down to bit 126. p >> 238 = 2^16 and 2^16 < n.
   So start with a = X^(2^16) (a monomial, already reduced). For each of the remaining 238 bits b of p, from high to low, set
   a ← (a²·X^b) mod g using the Barrett step of §3.1. At the end, a = X^p mod g.
6. Recover g = NTT_L2^(-1)(ĝ) (exact: ĝ already contains the 1/L2 scaling). Set V = a − X.
7. **Half-gcd.** Compute h = gcd(g, V) = gcd(g, X^p − X), monic (§3.3). h is the product of (X − z) over the distinct roots z ∈ F_p of g.
   s0 is always one of them.
8. If deg h = 1, trial i fails; continue with i + 1. Otherwise extract a second root s1 (§3.4), output
   (inputs(s0^e5), inputs(s1^e5)), and halt.

Every step is exact arithmetic over F_p. Its output is a uniquely defined mathematical object: the coefficients of f and g,
X^p mod g, and the monic gcd h. So the trial outcome, deg h and its roots, is a function of i alone. Any correct
implementation produces the same outcome.

## 3. Correctness of the subroutines

### 3.1 Barrett step (one squaring)
Let g be monic of degree n and deg a < n. Let A' = a²·X^b, so deg A' ≤ 2n − 1. Write A' = Q·g + R with deg R < n and deg Q ≤ n − 1.
Reversal gives rev_{2n−1}(A') = rev_{n−1}(Q)·rev_n(g) + X^n·rev_{n−1}(R). Hence rev_{n−1}(Q) ≡ H·I (mod X^n), where
H = rev_{n−1}(A' div X^n) is the top n coefficients of A' reversed.

Cyclic lengths:
- a² and H·I are products of two polynomials with n coefficients, of degree ≤ 2n − 2 < L. Length-L cyclic convolution is
  therefore exact.
- Q·g − A' = −R has degree < n ≤ L2. So the coefficients 0..n−1 of (A' mod X^L2 − 1) − (Q·g mod X^L2 − 1) are exactly R.
  The fold of A' touches only indices j ≤ 2n − 1 − L2 < n.

The step stores a (n words) and works in one buffer W of length L. The schedule is:
1. a → W, forward, square, inverse.
2. Scale; fold the top into indices < n; copy the low n to a.
3. Move the reversed top n into W[0..n), forward, multiply by Î, inverse.
4. Reverse the low n into W[0..n), zero-pad to L2, forward L2, multiply by ĝ, inverse.
5. a ← a − W[0..n).

These identities and lengths were checked exactly for every n in {5, 6, 7, 64, 125, 625, 1000, 3125, 15625, 78125,
390625}, with random monic g, random a and b ∈ {0, 1}. Each cyclic convolution was emulated as a product mod X^L − 1, and every result
matched FLINT's (a²X^b) mod g.

### 3.2 Newton inverse
I_1 = 1, because rev_n(g)(0) = lc(g) = 1. Step k → k' = min(2k, n) with F = rev_n(g) mod X^k':
- e = F·I_k is a product of lengths k' and k, exact with cyclic length L_j = tsize(k' + k − 1). Its coefficients 0..k−1 are 1, 0, …, 0.
- Let E be coefficients k..k'−1 of e. Then I_k' = I_k − X^k·(I_k·E mod X^(k'−k)), a product of lengths k and k' − k, exact at
  the same L_j.

This is the standard quadratically convergent iteration I_k' ≡ I_k(2 − F·I_k) mod X^k'. It was checked exactly together with §3.1.
Here tsize(l) is the least 2^j or 3·2^(j−2) that is ≥ l.

### 3.3 Half-gcd
The gcd uses the classical half-gcd recursion in the structure of Shoup's NTL `HalfGCD`, with base case d_red ≤ 48 by classical steps.
- `half_gcd_M(U, V, d)` returns the 2×2 polynomial matrix of the first remainder steps that reduce deg U by d.
- It recurses (with d1 = ⌈d/2⌉) on the shifted inputs (U >> m, V >> m) with m = max(deg U − 2d + 2, 0). It applies the returned
  matrix to the shifted pair with a matrix–vector product, performs one division, recurses again (with the remaining reduction
  d2), and multiplies the two matrices.
- `fast_gcd` repeats half_gcd + one division until deg U ≤ 48, then finishes with classical Euclid, then makes the gcd monic.

It is deterministic and exact for all inputs (any degree pattern). The instrumented implementation computed the same h as FLINT's
`gcd` on the exact (g, V) of every executed trial. All remainder sequences were normal (each division had quotient degree 1).

### 3.4 Second root
h has degree 2, so s1 = −h1 − s0, where h = X² + h1·X + h0.

## 4. Executed outcome (the certificate)

The procedure was executed on the fixed target. f, g and X^p mod g were computed with FLINT (python-flint 0.9.0), and the gcd with
FLINT and with the instrumented half-gcd (identical results). Trial 0 has

- s0 = 4766703137400488083754110162745305822677275183126808187356602193040276619021
- deg h = 2, with roots ≠ s0: 13834604379169323874622223502465088293112971940967906188773023811204797909611
- s1 = 13834604379169323874622223502465088293112971940967906188773023811204797909611

A = inputs(s0^e5) = (nk, rho) = (10282377930700709955331863829808625809742269793488616908110496813216137010678, 9242264967822723892815813252653473580510300412200602754015911816695904633482)

B = inputs(s1^e5) = (9929006709084423418434499777465267004141677663080324177561129659131724493461, 23598064575810107403865759625209663882872134837538481415646749312217549501322)

Common digest (32-byte little-endian lane 0): `82e3468ef09761522153585dbd4474552b2223900adf10f9835bfbff4facbe13`. Both pairs are canonical (< p) and distinct.
`certificates/message-a.bin` and `message-b.bin` are the 64-byte encodings nk ‖ rho (32-byte little-endian each).

## 5. Cost accounting (orchard-field-ram-v2)

**Unit charges.** Every field add/sub/mul and every 256-bit load, store, compare, branch or pointer increment costs 1. A simple loop
iteration is charged LOOP = 3 (increment, compare, branch). Per element:
- copy 2 + 3 = 5;
- zero-fill 1 + 3 = 4;
- scale or square (load, mul, store) 3 + 3 = 6;
- pointwise product or add/sub (two loads, op, store) 4 + 3 = 7.

An inversion is charged INV_OPS = 4·(254 + 76) + 20 = 1340: Fermat a^(p−2) by left-to-right square-and-multiply. p − 2 has 255 bits and
Hamming weight 77, so this is 254 squarings + 76 multiplications, each charged 4 (multiply, bit extraction, branch, loop), plus 20.
The instrumented half-gcd run priced every division's leading-coefficient inversion at 622. Its counts are re-priced here by adding
(divisions + 1)·(1340 − 622).

**NTT.** The transform is an in-place mixed-radix (4/2/3) NTT: decimation-in-frequency forward (natural order to digit-reversed),
transposed decimation-in-time inverse (digit-reversed order to natural, unscaled), with no reordering. Pointwise products do not
depend on order. Per butterfly, including loads, stores, address arithmetic and loop control:
- radix-4: 4 ld + 4 st + 4 mul (√−1 and three twiddles) + 8 add/sub + 6 = **26**;
- radix-2: 2 ld + 2 st + 1 mul + 2 add/sub + 4 = **11**;
- radix-3: 3 ld + 3 st + 3 mul (ζ₃, two twiddles) + 7 add/sub + 5 = **21**.

Twiddles are generated on the fly (no table): per twiddle index of a pass, 6 / 4 / 5 operations. For length N with radix sequence
f_1…f_m, T(N) = Σ_passes (BF[f]·N/f + TW[f]·N/(f_1⋯f_k)). The implementation computing exactly these butterflies was checked against
naive DFTs.
- T(196,608) = 11,993,087 (radices [4, 4, 4, 4, 4, 4, 4, 4, 3]);
- T(98,304) = 5,898,245 (radices [4, 4, 4, 4, 4, 4, 4, 2, 3]).

### 5.1 One powering step
| item | primitive operations |
| --- | --- |
| copy a into W (n·5) and zero-pad to L ((L−n)·4) | 864,557 |
| forward transform, length L | 11,993,087 |
| pointwise square (L·6) | 1,179,648 |
| inverse transform, length L | 11,993,087 |
| scale 2n coefficients by 1/L, writing at offset b (2n·6 + 1) | 937,501 |
| fold A' modulo X^L2 − 1 ((2n − L2)·7) | 405,622 |
| keep folded low n coefficients in a (n·5) | 390,625 |
| H = reversed top n coefficients, zero-pad to L (n·5 + (L−n)·4) | 864,557 |
| forward L, pointwise ·Î (L·7), inverse L | 25,362,430 |
| Q = reversed low n coefficients, zero-pad to L2 (n·5 + (L2−n)·4) | 471,341 |
| forward L2, pointwise ·ĝ (L2·7), inverse L2 | 12,484,618 |
| R = folded A' − Qg on n coefficients (n·7) | 546,875 |
| **one squaring step** | **67,493,948** |

238 steps: 16,063,559,624.

### 5.2 Per-trial components (trial 0 shown; other trials differ only in the SHA count and the gcd)
| component | primitive operations |
| --- | --- |
| sha256 | 40,016 |
| f_interp | 56,405,077 |
| g_monic | 551,309 |
| newton | 126,305,394 |
| I_hat | 14,038,632 |
| g_hat | 6,489,409 |
| x_init | 312,501 |
| powering | 16,063,559,624 |
| g_recover | 5,898,245 |
| v | 471,348 |
| gcd | 3,028,372,062 |
| roots | 28 |

Component formulas:
- `sha256`: (ctr + 1) SHA-256 compressions, each charged 20000 256-bit word ops (a generous bound for 64 rounds of 32-bit operations on one block),
  plus 8 for comparisons.
- `f_interp`: L2·(generate ω^j in natural order and store it at its digit-reversed position, which is the input order of the inverse
  transform: mul + store + loop + 10 for the incremental digit-reversed index = 15) + L2·(2C + 20) round-function evaluations + T(L2) + (n + 1)·6 + one inversion. The round function from A + sB
  performs 6 + 27·6 + 21·r = 189 arithmetic operations: A + sB, then rounds 2, 3, the partial round(s) and 60..63. Loading
  12 round constants and MDS entries per round plus A and B adds 78 + 12·r = 90 loads. That is 279 < 2C + 20 = 494,
  covering the result store and loop control.
- `g_monic`: one more evaluation (2C + 20), a subtraction, one inversion, (n + 1)·6, and zero-padding to L2.
- `newton`: Σ over the doubling steps of [loads/zero-pads + 5·T(L_j) + 2·L_j·7 + scalings], plus one inversion per distinct L_j
  ([2, 6, 12, 24, 48, 96, 192, 384, 768, 1536, 3072, 6144, 12288, 24576, 49152, 98304, 196608]).
- `I_hat`: n·5 + (L − n)·4 + T(L) + L·6 + inversion.
- `g_hat`: T(L2) + L2·6 + inversion.
- `x_init`: n·4 + 1.
- `g_recover`: T(L2).
- `v`: n·5 + (L2 − n)·4 + 1 subtraction.
- `gcd`: 2 × the instrumented half-gcd count of §5.3 (factor-2 allowance for recursion bookkeeping and degree tracking).
- `roots`: §3.4.

### 5.3 Half-gcd charges
Every polynomial operation of the recursion is charged by the following formulas, with L = tsize(·) and T as above:
- product of lengths l1, l2: min(3T(L) + 8L + 10L, 5·l1·l2 + 5·(l1 + l2)) with L = tsize(l1 + l2 − 1);
- subtraction: 7 per coefficient;
- division with quotient length lq and divisor length lb: 1340 + lq·(8·lb + 2);
- matrix–vector update (U, V) ← M·(U, V) with result length Lres: cyclic length L = tsize(Lres). This is exact because both results
  have degree < Lres. Charge (4 + #nonzero entries)·T(L) + 36L + 5L·#entries;
- 2×2 matrix product: L = tsize(la + lb − 1), 8 forward + 4 inverse transforms, charged 12·T(L) + 72L + 40L;
- working copies of the shifted inputs (U >> m, V >> m) at each recursion level: 5 per copied coefficient, plus 4 per slot of each of
  the two working buffers of capacity tsize(len U1). In the base case (d ≤ 48), 5 per copied coefficient;
- base case (d ≤ 48): classical steps with the division/product charges above;
- final monic: 1340 + 7·deg.

Results on the exact inputs:

| trial i | s0_i | SHA calls | deg h | divisions | instrumented gcd ops (re-priced inversions) | charged trial total (gcd ×2) |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 4766703137400488083754110162745305822677275183126808187356602193040276619021 | 2 | 2 | 78,123 | 1,514,186,031 | 19,302,443,645 |

Mapping s0 and s1 to inputs (3 fifth-root exponentiations each, ≤ 2040 ops each, plus 200) and re-evaluating both digests
(2C + 50 each, covering the full permutation's arithmetic and constant loads): 13,688.

**Total** W = 19,302,457,333 primitive operations. T = W/C = 8.144497e+07 target compressions, log2 T = 26.279322 ≤ **26.28**.

### 5.4 Memory (32-byte words)
Peak by phase, with L = 196,608, L2 = 98,304, n = 78,125:
- **interpolation:** one L2 buffer, values → coefficients in place → g;
- **Newton:** g (L2) + I (n) + two work buffers ≤ L each, so ≤ 2L + L2 + n;
- **powering:** Î (L) + ĝ (L2) + W (L) + a (n), so 2L + L2 + n;
- **gcd:** U, V in two buffers of capacity L2, plus the instrumented peak of matrices, working copies and transform buffers
  (274,732 words on the executed inputs), so 471,340.

All are ≤ 2L + 2L2 = 589,824 words. Constants (64·3 round constants, MDS, A, B, D0, D1, C2), SHA-256 state, scalars,
recursion bookkeeping and code are covered by an additional 1 MiB. Total ≤ 19,922,944 bytes = 2^24.2479, claimed **24.25**.
No nonuniform advice and no precomputation outside the charged procedure.

## 6. Success probability

The procedure uses no random coins. The target is fixed, and on it the procedure halts at trial 0 with the collision above. Its
success probability is therefore 1 and its work is exactly the finite charged budget W. No restart or tail argument is needed: the
budget covers every executed trial, including the failed ones.

Context only, not used for the claim: if a trial's second root count behaves like a Poisson(1) variable, a trial succeeds with probability about
1 − e^(−1) ≈ 0.63. On the same streams, executed with FLINT: for r=1, trials 0..26 gave deg h = [2, 1, 1, 3, 2, 1, 2, 4, 3, 1, 2, 2, 2, 1, 2, 2, 4, 1, 5, 4, 2, 2, 2, 3, 3, 4, 1], so 20 of 27 succeeded. Every success produced a collision verified against the reference digest.

## 7. Limitations and credits

- The cost is an explicit count for the stated algorithm, not a wall-clock measurement. The gcd count comes from an instrumented
  implementation of the stated recursion, multiplied by 2. The powering count is analytic (§5.1).
- The executed run used FLINT for speed. Correctness rests on uniqueness of the computed objects (§2), not on FLINT internals.
- Credits: Th0rgal's Orchard submissions used the univariate-slice + gcd(g, X^p − X) root-finding strategy and the deterministic,
  executed-outcome success argument. This submission follows that strategy. The new part is the two-round linearizing line (§1), which
  lowers the degree from about 5^(8+r) to 5^(6+r), together with subquadratic (half-gcd) and NTT/Barrett accounting. Half-gcd follows
  Shoup's NTL structure. Barrett/Newton reduction is textbook (von zur Gathen & Gerhard, *Modern Computer Algebra*, ch. 9 and 11).
