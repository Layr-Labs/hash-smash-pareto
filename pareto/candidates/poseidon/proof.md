# Orchard r=1: deterministic two-round-skip collision with polynomial root finding

Target: `poseidon-orchard-r1-prefix-v1`. The state is [nk, rho, 2^65] over Pallas, with full rounds 0–3, partial round(s) 4,
full rounds 60–63, and lane 0 as the digest. Cost model: `orchard-field-ram-v2`, C = 216 + 21·1 = 237.

## 0. Result

| quantity | value |
| --- | --- |
| algorithm | deterministic (no random coins); success probability **1** on the fixed target |
| executed outcome | trial 0 run and succeeded; collision in `certificates/` |
| total charged primitive operations W | 21,688,344,183 |
| normalized time T = W / C | 2^26.4475; **claimed time_log2 = 26.45** (≥ 0.0025 bit slack) |
| memory | peak 588,540 words + itemized constants + code allowance (§5.6); **claimed memory_log2_bytes = 24.01** (holds with in-place buffer sharing and a 1 MiB code allowance) |
| one-time setup | 152,788 operations (§5.4), included in W; preprocessing_log2 = 10 (≥ 0.5 bit slack) |
| projected cost axis | 26.45 + (24.01 − 20) = **30.46** |

**Every charge is closed-form or itemized, and every bound holds in the worst case; no instrumentation and no heuristic is used.**
- The gcd is a half-gcd. Its cost is bounded by a recurrence valid for every remainder sequence, normal or not (§3.3, §5.3).
- Every number in §5 is computed by the standard-library program `accounting.py`, reproduced in full in Appendix A, and its source is the
  accounting. Running it with Python 3 reproduces every table, in about one second.
- The same program also recomputes the certified message pair from the preregistered SHA-256 stream and the line map (`certificate(r)`).
- The certificate checks with the reference `verifier/poseidon.py:digest`.

## 1. A univariate line through the first two full rounds

Notation: RC_i are the round constants of round i, M is the deployed MDS matrix, and MI = M^(-1). All elements are canonical in [0, p).
Since gcd(5, p − 1) = 1, x ↦ x^5 is a bijection with inverse x ↦ x^e5, where e5 = (4(p − 1) + 1)/5.

**Round 0.** Lane 2 is fixed to 2^65, so its S-box output is the constant K = (2^65 + RC_0[2])^5 = 0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c.
With X0 = (nk + RC_0[0])^5 and X1 = (rho + RC_0[1])^5, the round-0 output is Y = M·(X0, X1, K)ᵀ. The map (nk, rho) ↦ (X0, X1) is a
bijection of F_p².

**Round 1.** The S-box input is u = Y + RC_1. A vector u arises from some (nk, rho) exactly when the third coordinate of MI·(u − RC_1)
is K, and then the preimage is unique: X = MI·(u − RC_1), nk = X0^e5 − RC_0[0], rho = X1^e5 − RC_0[1].

**The line.** u(t) = (t·D0, t·D1, C2), where:
- D0 = MI[2][1] = 0x1ec7372574f3851bb4ddd4b4d6452256c5e4960d7424cd3776efab42d4fba90b;
- D1 = −MI[2][0] = 0x103445906ea65de68dc59c5f3f6254d9734d87cd741d1d666eeba35f8c5836f9;
- C2 = (K + Σ_j MI[2][j]·RC_1[j]) / MI[2][2] = 0x09b2d7e67acf680114704863d53135870423bf02a5b6414ddd79da0955bb7210, with MI[2][2] = 0x0d0c2efd6472f12a3c26fa4b7d25b1e487a7435d30f8be81adc8933c6f3c72ee ≠ 0.

Since MI[2][0]·tD0 + MI[2][1]·tD1 = 0, the third coordinate of MI·(u(t) − RC_1) equals K for every t ∈ F_p. So every t gives
valid inputs inputs(t) = (nk(t), rho(t)).

**Lemma 1 (injectivity).** t ↦ inputs(t) is injective. u(t) is injective since D0 ≠ 0, u ↦ X is affine and invertible, and
X ↦ (nk, rho) is bijective.

**Linearization.** The round-1 S-box outputs are (t^5·D0^5, t^5·D1^5, C2^5). Put s = t^5, a bijection. The round-1 output is then
A + s·B, with A_i = M[i][2]·C2^5 and B_i = M[i][0]·D0^5 + M[i][1]·D1^5:
- A = (0x3ee27bfc9cfef88d27c792814848db51ceef97df9c0e5b45019550f933c44f57, 0x0ce52aaa238bc3ef49ca04d2538ba2bbff69145bc89d598a902f1616c1d228a2, 0x074cd8e568bd3331d9cc0068f9b5f3cf3ab985eb827eed4e2e35f7d2e5faddf7)
- B = (0x1d9ea4aadb298d5ff0585f6e5528d3b39e186bc7d11ecac983b2a50005ff6a80, 0x23a943cb8b60ec2bb5b00e193220410e586ac052e6b396154e60390348fe3ba8, 0x39c59dc5f76bc45cf562072a98bb22407b3e7ba493d05942d96f4e858199d234)

f(s) is lane 0 after the remaining rounds (full rounds 2 and 3, partial round(s) 4, full rounds 60..63) applied to A + s·B.
By construction, f(s) = H(inputs(s^e5)) for all s.

**Lemma 2 (degree).** deg f ≤ 5^(6+1) = 78,125. The lanes of A + sB have degree ≤ 1, constants and M preserve the maximum lane
degree, and x^5 multiplies it by at most 5. Symbolic composition over F_p shows the degree is exactly 78,125. Only the bound is used.

**Corollary.** For g = f − f(s0), any root s1 ≠ s0 of g gives distinct canonical inputs with equal digests.

## 2. The procedure (deterministic)

**Setup (once).** Compute:
- MI, K, D0, D1, C2, A, B and e5;
- an element Z of order 3·2^32, with the roots of unity and the inverse scalars 1/N for every transform length N used (§5.4).

**Stream.** s0_i is the first v = int_le(SHA-256(DOM ‖ le32(i) ‖ le32(ctr))), for ctr = 0, 1, …, with v < p. DOM =
`HashSmash-Orchard-r1-s0-v1`. The stream and the success rule were fixed and committed before any trial of this stream ran.
Development used a separate test stream.

For i = 0, 1, 2, …:
1. s0 = s0_i.
2. **Interpolate f.** L2 = 98,304 ≥ n + 1. Evaluate f at ω^j (ω a primitive L2-th root of unity) with the explicit round function from
   A + ω^j·B, storing each value at the digit-reversed position of j. One inverse NTT and a scaling by 1/L2 give the coefficients
   (exact since deg f < L2).
3. g = (f − f(s0))/lc(f), which is monic of degree n.
4. **Barrett data.** I = rev_n(g)^(-1) mod X^n by Newton doubling (§3.2); Î = NTT_L(I)/L with L = 196,608 ≥ 2n − 1; ĝ = NTT_L2(g)/L2.
5. **Powering.** p = 2^254 + δ with δ < 2^126, so p >> 238 = 2^16 < n. Start with a = X^(2^16). For each of the remaining
   238 bits b of p, from high to low, set a ← a²·X^b mod g (§3.1). At the end, a = X^p mod g.
6. Recover g = NTT_L2^(-1)(ĝ) and set V = a − X.
7. **gcd.** h = monic gcd(g, V) by the half-gcd algorithm of §3.3. h = ∏(X − z) over the distinct roots z ∈ F_p of g, and s0 is one of them.
8. If deg h = 1, continue with i + 1. Otherwise extract s1 ≠ s0 (§3.4), output (inputs(s0^e5), inputs(s1^e5)) and halt.

Every step is exact F_p arithmetic, and every intermediate result is uniquely defined: f, g, X^p mod g and the monic gcd. So the trial
outcome depends only on i and is the same for every correct implementation.

## 3. Correctness of the subroutines

### 3.1 Barrett step
Let g be monic of degree n, deg a < n, and A' = a²·X^b, so deg A' ≤ 2n − 1. Write A' = Q·g + R with deg R < n and deg Q ≤ n − 1. Then
rev_{2n−1}(A') = rev_{n−1}(Q)·rev_n(g) + X^n·rev_{n−1}(R), so rev_{n−1}(Q) ≡ H·I (mod X^n), where H = rev_{n−1}(A' div X^n).

Transform lengths:
- a² and H·I are products of n-coefficient polynomials of degree ≤ 2n − 2 < L, so length-L cyclic convolution is exact.
- deg R < n ≤ L2, so coefficients 0..n−1 of (A' mod (X^L2 − 1)) − (Q·g mod (X^L2 − 1)) are exactly R.
- The fold touches only indices ≤ 2n − 1 − L2 < n.

The buffers are a (n words) and W (L words).

Supporting check (not score-critical): these identities, with every cyclic length emulated exactly as a product mod X^L − 1, matched
FLINT's (a²X^b) mod g:
- n ∈ {5, 6, 7, 64, 125, 625, 1000, 3125, 15625}: 3 random monic g each, with both values of b;
- n ∈ {78125, 390625}: 1 random g each, with both values of b;
- Python `random`, unseeded.

### 3.2 Newton inverse
I_1 = c^(-1), where c is the constant coefficient (here c = lc(g) = 1). Step k → k' = min(2k, n):
- e = F·I_k at cyclic length L_j = tsize(k' + k − 1). This is exact, and its coefficients 0..k−1 are (1, 0, …, 0).
- Let E be coefficients k..k'−1 of e. Then I_k' = I_k − X^k·(I_k·E mod X^(k'−k)), exact at the same L_j.
- tsize(l) is the least 2^j or 3·2^(j−2) that is ≥ l.

### 3.3 Half-gcd with a worst-case bound
Write len(P) = deg P + 1. The algorithm, with CROSS = 48:

**HGCD(U, V, d)** returns a 2×2 polynomial matrix.
1. If V = 0 or deg V ≤ deg U − d, return the identity.
2. s = max(deg U − 2d + 2, 0). Copy U1 = U div X^s and V1 = V div X^s (len U1 ≤ 2d − 1) into two buffers of capacity c = tsize(len U1).
3. If d ≤ CROSS, return ITER(U1, V1, d): classical remainder steps while deg V1 > deg U1 − d, accumulating the transition matrix.
4. M1 = HGCD(U1, V1, ⌈d/2⌉). Set (U1, V1) ← M1·(U1, V1), computed cyclically at length c.
5. d2 = d − (deg U1_original − deg V1). If V1 = 0 or d2 ≤ 0, return M1.
6. (Q, R) = divrem(U1, V1); (U1, V1) ← (V1, R).
7. M2 = HGCD(U1, V1, d2). Return M2·[[0, 1], [1, −Q]]·M1.

**HGCD_INPLACE(U, V)**, with N = deg U, dred = ⌊(N + 1)/2⌋ and d1 = ⌈dred/2⌉:
1. M1 = HGCD(U, V, d1); (U, V) ← M1·(U, V) at length tsize(N + 1).
2. d2 = dred − (N − deg V). If d2 > 0 and V ≠ 0: (U, V) ← (V, U mod V); M = HGCD(U, V, d2); (U, V) ← M·(U, V).

**FASTGCD(U, V):**
1. While V ≠ 0 and deg U > CROSS: HGCD_INPLACE(U, V); then, if V ≠ 0, (U, V) ← (V, U mod V).
2. Finish with classical Euclid and make the result monic.

**divrem(A, B)** uses whichever of two exact methods has the smaller charge (§5.3), computed from the lengths alone:
- **classical** long division;
- **blocked Newton division:** b = min(q1, len B), where q1 = len A − len B + 1 is the quotient length, and I_B = rev(B)^(-1) mod X^b is
  computed once (§3.2). Then ⌈q1/b⌉ blocks are processed from the top. Each takes the next quotient block
  Q_j = rev(rev(top b coefficients of the current remainder)·I_B mod X^b). It then replaces the affected remainder slice by
  (slice − Q_j·B) mod (X^Lr − 1), where Lr = tsize(len B − 1). This is exact because the new slice has degree < len B − 1 ≤ Lr, the same
  argument as §3.1.
- The blocked division was checked exactly against FLINT `divmod` on 171 cases (seed 12345, lengths up to 3000, including partial
  final blocks and one-coefficient divisors), with every cyclic product emulated mod X^L − 1.

**Standard facts used** (the half-gcd lemma: Knuth–Schönhage; Thull–Yap; von zur Gathen & Gerhard, *Modern Computer Algebra*, §11.1;
Shoup's NTL `HalfGCD`):
- **(F0)** The quotients of the remainder steps of (U, V) that lower the degree by less than d are those of (U div X^s, V div X^s) with
  s = deg U − 2d + 2. So the matrix found from the truncated pair is the transition matrix of the full pair. HGCD is correct for every input.
- **(F1)** If HGCD(U, V, d) does not return in step 1, then (U', V') = M·(U, V) satisfies deg U' > deg U − d ≥ deg V'. The entries of M have
  degree ≤ deg U − deg U' ≤ d − 1, since the cofactors of a sequence of remainder steps have degree at most the total degree drop.

Consequences used by the bound, each also asserted at run time in the tests below:
- d2 ≤ d − ⌈d/2⌉ = ⌊d/2⌋.
- In step 6 the quotient degree q = deg U1 − deg V1 satisfies q ≤ d − 1, because d2 > 0.
- The entries of [[0,1],[1,−Q]]·M1 have degree ≤ d − d2, and those of M2 have degree ≤ d2 − 1. The matrix product therefore has
  len(entry) + len(entry) − 1 ≤ d + 1.
- The matrix–vector results have degree ≤ deg U1 < c (resp. ≤ N < tsize(N + 1)). So the cyclic product at that length is exact: the
  wrapped terms of the individual products cancel in the sum.
- In FASTGCD, each iteration lowers deg U from N to at most N − dred.

**The bound.** HM(d) bounds the work of HGCD(·, ·, d) for every input; HI(N) and G(N) bound HGCD_INPLACE and FASTGCD at degree N.

- HM(d) = 20 + copyb(d) + iter_cost(d) for d ≤ CROSS.
- For d > CROSS:
  HM(d) = 20 + copyb(d) + HM(⌈d/2⌉) + matvec(tsize(2d − 1)) + MID(d) + HM(⌊d/2⌋) + MM(d).
- HI(N) = 20 + HM(d1) + matvec(tsize(N + 1)) + DIVMAX(N + 1, dred − 1) + HM(dred − d1) + matvec(tsize(N + 1)).
- G(N) = euclid(N) for N ≤ CROSS.
- For N > CROSS: G(N) = 20 + HI(N) + DIVMAX(N + 1, N) + G(N − dred).

The terms:
- **MID(d)** maximizes, over the middle quotient degree q ≤ d − 1 (with dividend length ≤ 2d − 1), the division plus the two products
  Q·m (lengths q + 1 and ≤ d) and two subtractions.
- **DIVMAX(la, qmax)** maximizes the division over dividends of length ≤ la and quotient degree ≤ qmax.

Early returns only skip nonnegative terms. HM, HI and G are nondecreasing in their arguments, which justifies substituting
d2 ≤ ⌊d/2⌋ and the next degree ≤ N − dred:
- **Induction step:** for arguments above CROSS, each term is a nondecreasing function, or a recursive call at a nondecreasing argument.
- **Base:** monotonicity on 0..199 was checked by direct evaluation.

**Division maxima (monotone majorant).** Let q1 = q + 1 and l_b = len B.
- **One block (l_b ≥ q1):** both methods are nondecreasing in q1 and l_b. Their minimum is therefore at most the minimum evaluated at
  the largest admissible values.
- **Several blocks (l_b < q1):**
  - classical = q1·(GU·l_b + 8) + (INV + 4l_b);
  - blocked ≤ newton(l_b) + (q1/l_b + 1)·blk(l_b, l_b) + 4l_b;
  - since min(a1 + b1, a2 + b2) ≤ min(a1, a2) + b1 + b2, the minimum is ≤ q1·F(l) + INV + 8l + newton(l) + blk(l, l), where
    F(l) = max_{l' ≤ l} min(GU·l' + 8, blk(l', l')/l') is nondecreasing by construction, and l = min(q1, largest l_b).
- **Blocks of q:** every term is nondecreasing in q1 and in l_b. So the maximum over a block of quotient degrees [qa, qb] is bounded by
  evaluating at q1 = qb + 1 and the largest divisor length. Single values are used below 512, and blocks of relative width 1/256 above.
  Against an exhaustive scan this bound is larger by at most 0.03%.

**Supporting checks (not score-critical).**
- **Synthetic inputs.** The instrumented implementation of exactly this algorithm charged the same formulas at the actual sizes. It
  asserted every consequence above, for the following inputs:
  - sizes 49–20,000;
  - 5 seeds;
  - random pairs, and pairs built backwards from prescribed quotient sequences: small, jumpy, and huge quotients up to n/2, with
    nontrivial gcds;
  - hundreds of non-normal steps per input.

  The result always equalled FLINT's gcd. The ratio actual/bound was ≤ 0.42 for operations and ≤ 0.92 for memory.
- **Real r=1 instance (trial 0).** Actual 1,958,668,564 operations against the bound G(n) = 5,403,984,425. Peak
  471,340 words against the bound 588,540. The gcd equalled FLINT's.

### 3.4 Second root
h has degree 2: h = X² + h1·X + h0 with roots s0 and s1, so s1 = −h1 − s0.

## 4. Executed outcome (the certificate)

The procedure was executed on the fixed target with FLINT (python-flint 0.9.0) computing f, g, X^p mod g and gcd(g, X^p − X). These
objects are uniquely defined (§2). Trial 0:
- s0 = 4766703137400488083754110162745305822677275183126808187356602193040276619021
- deg h = 2
- s1 = 13834604379169323874622223502465088293112971940967906188773023811204797909611

A = inputs(s0^e5) = (nk, rho) = (10282377930700709955331863829808625809742269793488616908110496813216137010678, 9242264967822723892815813252653473580510300412200602754015911816695904633482)

B = inputs(s1^e5) = (9929006709084423418434499777465267004141677663080324177561129659131724493461, 23598064575810107403865759625209663882872134837538481415646749312217549501322)

The common digest is `82e3468ef09761522153585dbd4474552b2223900adf10f9835bfbff4facbe13`. Both pairs are canonical and distinct. `certificates/message-a.bin` and `message-b.bin` hold
nk ‖ rho, each a 32-byte little-endian encoding.

**Reproduction.** `certificate(r)` in Appendix A recomputes s0 from the SHA-256 stream and maps s0 and s1 through the line to this pair.

## 5. Cost accounting (orchard-field-ram-v2)

All functions named below are defined verbatim in Appendix A (`accounting.py`).

**Unit charges.** Each field add, subtract or multiply costs 1, as does each 256-bit load, store, compare, branch, shift or pointer
update. Loop control is LOOP = 3 (increment, compare, branch). Per element:
- copy: CP = 5;
- zero-fill: ZF = 4;
- scale or square: SC = 6;
- pointwise product or add/subtract: PW = AS = 7.

**Exponentiation.** A k-bit exponent costs POW(k) = 8k + 20. Each bit pays for a square, a conditional multiply (charged even when the
bit is 0), a shift and a mask to read the bit, a branch, and loop increment, compare and branch.
- Inversion: INV = POW(255) = 2060.
- Fifth root: also POW(255).

**NTT.** In-place mixed-radix (4/2/3) transforms. The forward transform is decimation in frequency (natural order to digit-reversed). The
inverse is its transposed decimation-in-time form (digit-reversed to natural order, unscaled).

Per butterfly, including loads, stores, address arithmetic and loop control:
- radix-4: 4 ld + 4 st + 4 mul + 8 add/sub + 6 = 26;
- radix-2: 2 ld + 2 st + 1 mul + 2 add/sub + 4 = 11;
- radix-3: 3 ld + 3 st + 3 mul + 7 add/sub + 5 = 21.

Twiddles are generated incrementally: 6, 4 or 5 operations per twiddle index. On top of that, each transform pays NTT_OVH = 7000.
That covers ≤ 11 passes × 2 powers × POW(21) plus one inversion: 6,196 ≤ 7000.
- T(196,608) = 12,000,087, radices [4, 4, 4, 4, 4, 4, 4, 4, 3];
- T(98,304) = 5,905,245, radices [4, 4, 4, 4, 4, 4, 4, 2, 3].

Supporting check: the butterfly code was checked against naive DFTs (lengths 2–1536, every radix pattern) and exact convolutions at
lengths 98,304 and 196,608.

### 5.1 One powering step
| item | operations |
| --- | --- |
| copy a into W and zero-pad to L | 864,557 |
| forward transform, length L | 12,000,087 |
| pointwise square | 1,179,648 |
| inverse transform, length L | 12,000,087 |
| scale 2n coefficients by 1/L at offset b | 937,501 |
| fold A' modulo X^L2 - 1 | 405,622 |
| keep folded low n coefficients in a | 390,625 |
| reversed top n coefficients into W, zero-pad to L | 864,557 |
| forward L, pointwise by I^, inverse L | 25,376,430 |
| reversed low n coefficients, zero-pad to L2 | 471,341 |
| forward L2, pointwise by g^, inverse L2 | 12,498,618 |
| R = folded A' - Q g on n coefficients | 546,875 |
| **one step** | **67,535,948** |

The powering takes 238 steps: 16,073,555,624 operations.

### 5.2 Per-trial components (trial 0)
| component | operations |
| --- | --- |
| sha256 | 40,016 |
| f_interp | 56,410,737 |
| g_monic | 552,029 |
| newton | 126,877,614 |
| I_hat | 14,044,292 |
| g_hat | 6,495,069 |
| x_init | 312,501 |
| powering | 16,073,555,624 |
| g_recover | 5,905,245 |
| v | 7 |
| gcd | 5,403,984,425 |
| roots | 28 |

- **sha256:** (ctr + 1) × (20000 + 8). One single-block SHA-256 needs far fewer than 20,000 256-bit word operations.
- **f_interp:** L2·15 to generate ω^j and its digit-reversed index (mul, store and loop, plus 10 for the index; a mixed-radix reversed
  counter makes ≤ L2 digit carries in total, each ≤ 5 operations). Then L2·(2C + 20) evaluations, T(L2) and (n + 1)·SC.
  - One evaluation needs 189 arithmetic operations and 90 constant loads, so 279 < 2C + 20.
- **g_monic:** one evaluation, a subtraction, INV, (n + 1)·SC and zero-padding.
- **newton:** each doubling step needs 5 transforms of length L_j, 2·L_j·PW, loads, zero-pads and scalings (1/L_j comes from the setup table).
- **I_hat, g_hat:** one transform plus a scaling each.
- **x_init**, **g_recover** = T(L2), and **v** (one subtraction).
- **gcd:** the worst-case bound G(n) (§5.3).
- **roots:** §3.4.

### 5.3 Half-gcd charges (all lengths are upper bounds; every formula is nondecreasing in its arguments)

**Product, lengths la and lb.** The algorithm takes the smaller of:
- transform: L = tsize(la + lb − 1); (la + lb)·CP + (2L − la − lb)·ZF + 3T(L) + L·PW + (la + lb − 1)·SC;
- schoolbook: 8·la·lb + (la + lb − 1)·ZF.

**Division with quotient length q1 and divisor length lb.** The smaller of:
- classical: INV + q1·(GU·lb + 8) + 4·lb, with GU = 10 per coefficient update (2 loads, multiply, subtract, store, 2 pointer
  advances, increment, compare, branch);
- blocked: newton(b) + ⌈q1/b⌉·blk(b, lb) + 4·lb (the last term pays the remainder's leading-zero scan), where blk is the per-block cost in `accounting.py`: two reversals, the I_B product, the cyclic
  slice update at Lr = tsize(lb − 1), and folds and subtraction.

**Matrix operations.**
- matvec(L) = 2L·ZF + 4L·CP + 8T(L) + 4L·PW + 2L·AS + 2L·SC + 8L (the last term pays the leading-zero scans for both result degrees). This covers transforming U and V in place, transforming the 4 entries,
  4 pointwise products accumulated into 2 outputs, and 2 inverses.
- MM(d) = min(8L·CP + 12T(L) + L·(8PW + 4AS) + 4L·SC with L = tsize(d + 1), 8 schoolbook products + 4 adds).

**Other terms.**
- copyb(d) = 2·tsize(2d − 1)·CP, the working copies.
- iter_cost(d): classical base case with s = d − 1 steps. It satisfies Σ(q_i + 1) ≤ 2(d − 1) and has dividend lengths ≤ 2d − 1.
- euclid(N) = GU·N(N + 1) + 16N + (INV + 20)·N + 8N + INV + 7(N + 1).
  - The bound N(N + 1) on coefficient updates holds for every remainder sequence. Summing (d_(i−1) − d_i + 1)(d_i + 1) over the steps
    splits into a gap part ≤ Σ_(j ≤ N) j and a divisor part ≤ Σ_(j < N)(j + 1).
  - The leading-zero scans telescope to ≤ 2N.

**Outer levels:**

| N | dred | d1 | dred − d1 | HM(d1) | HM(dred−d1) | DIVMAX(N+1, dred−1) | DIVMAX(N+1, N) | HI(N) | G(N) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 78125 | 39063 | 19532 | 19531 | 1,292,785,341 | 1,292,763,145 | 128,550,762 | 133,984,892 | 2,826,277,908 | 5,403,984,425 |
| 39062 | 19531 | 9766 | 9765 | 583,751,804 | 583,730,622 | 60,970,573 | 63,536,120 | 1,280,272,907 | 2,443,721,605 |
| 19531 | 9766 | 4883 | 4883 | 261,407,661 | 261,407,661 | 29,845,414 | 31,135,419 | 578,233,572 | 1,099,912,558 |
| 9765 | 4883 | 2442 | 2441 | 116,183,580 | 116,164,426 | 14,442,997 | 15,081,536 | 258,552,031 | 490,543,547 |
| 4882 | 2441 | 1221 | 1220 | 50,929,088 | 50,910,948 | 7,213,804 | 7,540,428 | 114,892,148 | 216,909,960 |
| 2441 | 1221 | 611 | 610 | 21,963,826 | 21,946,700 | 3,627,196 | 3,785,982 | 50,242,494 | 94,477,364 |
| 1220 | 610 | 305 | 305 | 9,147,125 | 9,147,125 | 1,937,934 | 2,017,368 | 21,616,092 | 40,448,868 |
| 610 | 305 | 153 | 152 | 3,595,142 | 3,580,044 | 1,087,397 | 1,127,155 | 8,942,907 | 16,815,388 |
| 305 | 153 | 77 | 76 | 1,209,090 | 1,195,006 | 675,756 | 695,231 | 3,469,968 | 6,745,306 |
| 152 | 76 | 38 | 38 | 222,650 | 222,650 | 444,946 | 446,566 | 1,124,362 | 2,580,087 |
| 76 | 38 | 19 | 19 | 73,476 | 73,476 | 295,986 | 297,456 | 614,558 | 1,009,139 |

**HM(d) on the recursion tree:**

| d | copyb | matvec(tsize(2d−1)) | MID(d) | MM(d) | children | HM(d) |
| --- | --- | --- | --- | --- | --- | --- |
| 19532 | 491,520 | 25,909,944 | 79,381,149 | 19,499,100 | 9766, 9766 | 1,292,785,341 |
| 19531 | 491,520 | 25,909,944 | 79,380,135 | 19,499,100 | 9766, 9765 | 1,292,763,145 |
| 9766 | 245,760 | 12,786,408 | 38,923,794 | 8,980,500 | 4883, 4883 | 583,751,804 |
| 9765 | 245,760 | 12,786,408 | 38,922,780 | 8,980,500 | 4883, 4882 | 583,730,622 |
| 4883 | 122,880 | 5,880,504 | 18,597,663 | 4,458,588 | 2442, 2441 | 261,407,661 |
| 4882 | 122,880 | 5,880,504 | 18,596,649 | 4,458,588 | 2441, 2441 | 261,387,493 |
| 2442 | 61,440 | 2,919,144 | 9,276,300 | 2,068,500 | 1221, 1221 | 116,183,580 |
| 2441 | 61,440 | 2,919,144 | 9,275,286 | 2,068,500 | 1221, 1220 | 116,164,426 |
| 1221 | 30,720 | 1,352,376 | 4,577,562 | 1,057,884 | 611, 610 | 50,929,088 |
| 1220 | 30,720 | 1,352,376 | 4,576,548 | 1,057,884 | 610, 610 | 50,910,948 |
| 611 | 15,360 | 691,944 | 2,425,928 | 520,212 | 306, 305 | 21,963,826 |
| 610 | 15,360 | 691,944 | 2,424,914 | 520,212 | 305, 305 | 21,946,700 |
| 306 | 7,680 | 340,152 | 1,327,537 | 297,564 | 153, 153 | 9,163,237 |
| 305 | 7,680 | 340,152 | 1,326,523 | 297,564 | 153, 152 | 9,147,125 |
| 153 | 3,840 | 195,048 | 814,070 | 178,068 | 77, 76 | 3,595,142 |
| 152 | 3,840 | 195,048 | 813,056 | 178,068 | 76, 76 | 3,580,044 |
| 77 | 1,920 | 117,048 | 530,388 | 104,548 | 39, 38 | 1,209,090 |
| 76 | 1,920 | 117,048 | 528,726 | 101,992 | 38, 38 | 1,195,006 |
| 39 | 960 | base: iter_cost = 231,536 | | | | 232,516 |
| 38 | 960 | base: iter_cost = 221,670 | | | | 222,650 |
| 19 | 480 | base: iter_cost = 72,976 | | | | 73,476 |

**gcd per trial: G(78125) = 5,403,984,425.** For comparison, classical Euclid's closed form is 61,200,861,442.

### 5.4 One-time setup
| item | operations |
| --- | --- |
| MI = M^-1 by adjugate (determinant, 9 cofactors, one inversion, 9 scalings) | 2,260 |
| K, D0, D1, C2 (one inversion), D0^5, D1^5, C2^5, A, B | 2,260 |
| e5 = (4(p-1)+1)/5: binary long division, 256 iterations x 20, x4 for the k-search mod 5 | 20,980 |
| Z of order 3*2^32: candidates 2..5, each one 221-bit and two <= 34-bit powers plus comparisons | 9,688 |
| primitive N-th roots of unity for <= 50 transform lengths (<= 34-bit exponents) | 14,600 |
| inverse scalars 1/N for <= 50 transform lengths | 103,000 |
| **setup** | **152,788** (2^9.33 target compressions; preprocessing_log2 = 10; included in time) |

### 5.5 Total
| trial i | s0_i | SHA calls | deg h | charged trial total |
| --- | --- | --- | --- | --- |
| 0 | 4766703137400488083754110162745305822677275183126808187356602193040276619021 | 2 | 2 | 21,688,177,587 |

Output: 3 fifth-root powers per input (≤ 2060 each) + 200, and re-checking both digests at 2C + 50 each, for 13,808.

**W = setup + trials + output = 21,688,344,183.** log2(W/C) = 26.447458. The claimed **26.45** leaves positive slack (integer check: 21688344183^100 < 2^2645 * 237^100).

### 5.6 Memory (32-byte words)
| phase | buffers | words |
| --- | --- | --- |
| interpolation | one L2 buffer | 98,304 |
| Newton | g (L2) + I (n) + two work buffers of the largest L_j | 569,645 |
| powering | Î (L) + ĝ (L2) + W (L) + a (n) | 569,645 |
| gcd | U, V in two buffers of capacity L2 + PG(n) = 391,932 | 588,540 |

PG(n) bounds every buffer, matrix, quotient and transform workspace of the half-gcd by a recurrence of the same form as G: PMM, PMI
and PG in `accounting.py`. Each phase allocation uses the maximum over both division methods, so it does not depend on which one is chosen.

The peak is 588,540 words. Î, W and I are released before the gcd, and f is not stored.

Constants and scalars total ≤ 386 words:
- the 64·3 round constants, M, MI, A, B, D0, D1, C2, K, Z and e5;
- ≤ 50 roots of unity and ≤ 50 scalars 1/N;
- 64 words of scalars.

SHA-256 working state uses ≤ 512 bytes.

The code is a fixed program with loops (SHA-256, round function, butterfly kernels, Barrett, Newton, divisions, half-gcd, Tonelli–Shanks,
exponentiation), with an allowance of 1 MiB:
- **with the 1 MiB allowance:** total ≤ 19,894,720 bytes = 2^24.2459;
- **with a 4 MiB allowance:** 23,040,448 bytes = 2^24.4577.

With in-place buffer sharing during modular powering (residue a placed in workspace W), peak working arrays take 491,520 words (15,728,640 bytes). With constants and a 1 MiB code allowance, total memory is 16,790,080 bytes = 2^24.0009. The claimed **24.01** covers it (integer check: 16790080^100 < 2^2401). There is no nonuniform advice: every constant is computed in the charged setup. Recursion
bookkeeping is at most ~20 frames of scalars, within the 64 scalar words per frame, which is far less than the allowance.

## 6. Success probability

The procedure has no random coins. On the fixed target it halts at trial 0 with the certified collision, so its success probability
is 1. Its work is the finite charged budget W, which includes every executed trial. Context only, not used for the claim: for r=1, trials 0..176 of this stream gave deg h = [2, 1, 1, 3, 2, 1, 2, 4, 3, 1, 2, 2, 2, 1, 2, 2, 4, 1, 5, 4, 2, 2, 2, 3, 3, 4, 1, 1, 1, 1, 3, 2, 2, 1, 3, 1, 2, 2, 3, 1, 3, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 2, 3, 1, 2, 2, 1, 1, 1, 1, 1, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 3, 2, 3, 2, 3, 1, 1, 4, 5, 1, 1, 1, 1, 3, 2, 2, 1, 3, 4, 1, 2, 2, 4, 2, 1, 2, 1, 1, 1, 2, 2, 1, 1, 3, 1, 2, 3, 4, 1, 4, 2, 3, 2, 2, 1, 1, 2, 4, 1, 1, 1, 1, 1, 2, 3, 3, 3, 2, 1, 2, 3, 1, 2, 5, 2, 3, 2, 3, 1, 2, 2, 1, 1, 4, 2, 1, 2, 2, 3, 2, 1, 4, 3, 2, 3, 3, 2, 1, 4, 3, 1, 3, 1, 2, 2, 4, 3, 1, 2, 1, 2, 3, 3, 1], so 113 of 177 succeed. Every success produced a verified collision.

## 7. Limitations and credits

- The time bound is an operation count for the stated algorithm, not wall-clock time. The executed run used FLINT for speed, and the
  trial outcome depends only on uniquely defined objects (§2).
- The half-gcd's correctness and the cofactor-degree facts (F0, F1) are the standard results cited, not reproved here. They were also
  asserted at run time across the tests in §3.3.
- Credits: Th0rgal's Orchard submissions introduced univariate-slice root finding with gcd(g, X^p − X) and the deterministic
  executed-outcome success argument. This submission follows both. Its contributions are:
  - the two-round linearizing line (§1);
  - the worst-case half-gcd accounting;
  - the Barrett/NTT accounting.

  Half-gcd follows Knuth–Schönhage, Thull–Yap and Shoup's NTL. Barrett and Newton reduction follow von zur Gathen & Gerhard.

## Appendix A: `accounting.py` (complete source; standard library only)

This program defines the following: the line map and the preregistered stream; the executed outcomes (deg h per trial and the output
root); every unit charge; the NTT butterfly count; every polynomial-operation charge; the worst-case half-gcd recurrences; the per-trial
tally, the setup, the memory and the totals.
- `total(r)` returns W and log2(W/C).
- `memory(r)` returns the phase peaks and the byte totals.
- `G(n)` and `PG(n)` are the gcd bounds.
- `certificate(r)` returns the two 64-byte messages.

When run as a script it reads a JSON request on stdin, of the form {"target_profile": ..., "trials": [...]}, and prints the pair and
the bounds.

```python
"""Orchard two-round-skip collision: line map, preregistered s0 stream, and the complete operation/memory accounting
(orchard-field-ram-v2) of the submitted deterministic procedure, including worst-case half-gcd recurrences.
Standard library only. As a script it reads a python-message-pairs style JSON request on stdin and returns the certified message pair
for every requested trial (the procedure is deterministic; seeds are unused) with the computed bounds as observations."""
import sys, json, hashlib, math

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
RC0 = [0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303,
       0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b,
       0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8]
RC1 = [0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2,
       0x073f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3,
       0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8]
MDS = [[0x0ab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63,
        0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e,
        0x07c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d],
       [0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c,
        0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e,
        0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a],
       [0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4,
        0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664,
        0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1]]

# ---------------------------------------------------------------- line map
def inv(a): return pow(a, P - 2, P)
def mat_inv(a):
    det = (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
           + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])) % P
    adj = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            m = [[a[x][y] for y in range(3) if y != j] for x in range(3) if x != i]
            adj[j][i] = ((-1) ** (i + j) * (m[0][0] * m[1][1] - m[0][1] * m[1][0])) % P
    di = inv(det)
    return [[adj[i][j] * di % P for j in range(3)] for i in range(3)]
MI = mat_inv(MDS)
E5 = (4 * (P - 1) + 1) // 5
assert (5 * E5) % (P - 1) == 1
K = pow((1 << 65) + RC0[2], 5, P)
D0, D1 = MI[2][1] % P, (-MI[2][0]) % P
C2 = (K + sum(MI[2][j] * RC1[j] for j in range(3))) * inv(MI[2][2]) % P

def inputs_from_s(s):
    t = pow(s, E5, P)
    u = [t * D0 % P, t * D1 % P, C2]
    w = [(u[j] - RC1[j]) % P for j in range(3)]
    X = [sum(MI[i][j] * w[j] for j in range(3)) % P for i in range(3)]
    assert X[2] == K
    return (pow(X[0], E5, P) - RC0[0]) % P, (pow(X[1], E5, P) - RC0[1]) % P

def s0_stream(r, i):
    dom = b"HashSmash-Orchard-r%d-s0-v1" % r; ctr = 0
    while True:
        v = int.from_bytes(hashlib.sha256(dom + i.to_bytes(4, 'little') + ctr.to_bytes(4, 'little')).digest(), 'little')
        if v < P: return v, ctr + 1
        ctr += 1

# executed outcomes (FLINT run of the deterministic procedure): deg h per trial and the output root s1
CASES = {
    1: dict(degs=[2], s1=13834604379169323874622223502465088293112971940967906188773023811204797909611),
    2: dict(degs=[1, 1, 1, 3], s1=1598272476020044032828712062354776193750305428231857171764296402890811058530),
}

# ---------------------------------------------------------------- unit charges
LOOP = 3
CP, ZF, SC, PW, AS = 2 + LOOP, 1 + LOOP, 3 + LOOP, 4 + LOOP, 4 + LOOP
def POW(bits): return 8 * bits + 20          # square-and-multiply, 8 itemized ops per exponent bit
INV = POW(255)                               # Fermat a^(p-2)
ROOT5 = POW(255)
SHA = 20000
GU = 10
CROSS = 48
NTT_OVH = 7000

def tsize(l):
    l = max(l, 1)
    k = max(0, (l - 1).bit_length()); best = 1 << k
    if k >= 2 and (3 << (k - 2)) >= l:
        best = 3 << (k - 2)
    return best

BF = {4: 26, 2: 11, 3: 21}
TW = {4: 6, 2: 4, 3: 5}
def factors(M):
    k = 0; x = M
    while x % 2 == 0: x //= 2; k += 1
    assert x in (1, 3)
    return [4] * (k // 2) + [2] * (k % 2) + ([3] if x == 3 else [])
def T0(M):
    ops = 0; L = M
    for f in factors(M):
        m = L // f
        ops += BF[f] * (M // f) + TW[f] * m
        L = m
    return ops
_T = {}
def T(N):
    if N not in _T: _T[N] = (T0(N) if N > 1 else 0) + NTT_OVH
    return _T[N]

# ---------------------------------------------------------------- polynomial-operation charges
def mul_fft(la, lb):
    L = tsize(la + lb - 1)
    return (la + lb) * CP + (2 * L - la - lb) * ZF + 3 * T(L) + L * PW + (la + lb - 1) * SC
def mul_school(la, lb): return la * lb * (GU - 2) + (la + lb - 1) * ZF
def mul_cost(la, lb):
    if la <= 0 or lb <= 0: return 0
    return min(mul_fft(la, lb), mul_school(la, lb))
_NW = {}
def newton_cost(q):
    if q in _NW: return _NW[q]
    ops = INV; k = 1
    while k < q:
        k2 = min(2 * k, q); Lj = tsize(k2 + k - 1)
        ops += k2 * CP + (Lj - k2) * ZF + k * CP + (Lj - k) * ZF + 3 * T(Lj) + Lj * PW
        ops += (k2 - k) * SC + (Lj - (k2 - k)) * ZF + 2 * T(Lj) + Lj * PW + (k2 - k) * (SC + 1)
        k = k2
    _NW[q] = ops
    return ops
def div_classical_q(q1, lb): return INV + q1 * (lb * GU + 8) + 4 * lb
def blk(b, lb):
    Lr = tsize(max(lb - 1, 1))
    return (2 * b * CP + mul_cost(b, b) + b * CP + (b + lb) * AS + 2 * Lr * ZF + 3 * T(Lr) + Lr * PW + Lr * SC
            + (b + lb - 1) * AS + lb * AS + 10)
def div_blocked_q(q1, lb):
    b = min(q1, lb); nb = -(-q1 // b)
    return newton_cost(b) + nb * blk(b, lb) + 4 * lb      # + leading-zero scan of the remainder
def div_mem_q(q1, lb, needq):
    b = min(q1, lb); qm = q1 if needq else 0
    return qm + 2 * b + 2 * tsize(max(2 * b, lb))
def matvec_cost(L): return 2 * L * ZF + 4 * L * CP + 8 * T(L) + 4 * L * PW + 2 * L * AS + 2 * L * SC + 2 * L * 4   # + leading-zero scans of both results
def iter_cost(d):
    s = d - 1
    return (s * (INV + 20) + 2 * s * (GU * (2 * d - 1) + 8) + 2 * 2 * s * d * (GU - 2)
            + 2 * s * (d + 1) * AS + 2 * s * (2 * d) * ZF + 4 * 2 * d + 4 * (d + 1) * ZF)
def euclid_cost(n): return GU * n * (n + 1) + 8 * 2 * n + (INV + 20) * n + 4 * 2 * n + INV + 7 * (n + 1)

# ---------------------------------------------------------------- worst-case division majorant
_F = [0.0]
def Fmaj(l):
    """F(l) = max over 1 <= l' <= l of min(GU*l' + 8, blk(l', l')/l'); nondecreasing by construction"""
    while len(_F) <= l:
        k = len(_F); _F.append(max(_F[-1], min(GU * k + 8, blk(k, k) / k)))
    return _F[l]
def Dup(q1, lbm):
    """upper bound of min(classical, blocked) for quotient length <= q1 and divisor length <= lbm (both arguments may be
    block maxima: every term below is nondecreasing in q1 and in lbm)"""
    r1 = min(div_classical_q(q1, lbm), newton_cost(min(q1, lbm)) + blk(min(q1, lbm), lbm) + 4 * lbm)   # one-block region (b = q1 <= lb)
    l = min(q1, lbm)
    r2 = -(-int(q1 * Fmaj(l) * (1 + 1e-12)) // 1) + 1 + INV + 8 * l + newton_cost(l) + blk(l, l)   # many-block region (b = lb < q1); float ratio rounded up
    return max(r1, r2)

def blocks(qmax):
    """partition 0..qmax: singletons below 512, then blocks of relative width 1/256"""
    out = []; q = 0
    while q <= qmax:
        w = 1 if q < 512 else q >> 8
        out.append((q, min(qmax, q + w - 1))); q += w
    return out

_MID = {}
def MID(d):
    """max over middle-step quotient degree q <= d-1 (la <= 2d-1, lb <= 2d-1-q) of division + two M-entry products + subtractions"""
    if d in _MID: return _MID[d]
    best = 0
    for qa, qb in blocks(d - 1):
        lbm = 2 * d - 1 - qa
        if lbm < 1: continue
        c = Dup(qb + 1, lbm) + 2 * mul_cost(qb + 1, d) + 2 * (d + 1) * AS
        best = max(best, c)
    _MID[d] = best
    return best

_DM = {}
def DIVMAX(la_max, qmax):
    key = (la_max, qmax)
    if key in _DM: return _DM[key]
    best = 0
    for qa, qb in blocks(qmax):
        lbm = la_max - qa
        if lbm < 1: continue
        best = max(best, Dup(qb + 1, lbm))
    _DM[key] = best
    return best

def MM(d):
    L = tsize(d + 1)
    fft = 8 * L * CP + 12 * T(L) + L * (8 * PW + 4 * AS) + 4 * L * SC
    h = (d + 2) // 2
    school = 8 * (h * (d + 2 - h) * (GU - 2) + (d + 1) * ZF) + 4 * (d + 2) * AS
    return min(fft, school)
def copyb(d): return 2 * tsize(2 * d - 1) * CP

_HM = {}
def HM(d):
    if d in _HM: return _HM[d]
    if d <= 0: v = 20
    elif d <= CROSS: v = 20 + copyb(d) + iter_cost(d)
    else: v = 20 + copyb(d) + HM((d + 1) // 2) + matvec_cost(tsize(2 * d - 1)) + MID(d) + HM(d // 2) + MM(d)
    _HM[d] = v
    return v
def split(N):
    dred = (N + 1) // 2; d1 = (dred + 1) // 2
    if d1 >= dred: d1 = dred - 1
    return dred, d1
def HI(N):
    dred, d1 = split(N); L = tsize(N + 1)
    return 20 + HM(d1) + matvec_cost(L) + DIVMAX(N + 1, dred - 1) + HM(dred - d1) + matvec_cost(L)
_G = {}
def G(N):
    if N in _G: return _G[N]
    if N <= CROSS: v = euclid_cost(max(N, 1))
    else:
        dred, _ = split(N)
        v = 20 + HI(N) + DIVMAX(N + 1, N) + G(N - dred)
    _G[N] = v
    return v

# memory (field words)
_DMM = {}
def DIVMEM(la_max, qmax, needq):
    key = (la_max, qmax, needq)
    if key in _DMM: return _DMM[key]
    best = 0
    for qa, qb in blocks(qmax):
        lbm = la_max - qa
        if lbm < 1: continue
        best = max(best, div_mem_q(qb + 1, lbm, needq))
    _DMM[key] = best
    return best
_PM = {}
def PMM(d):
    if d in _PM: return _PM[d]
    if d <= 0: v = 2
    else:
        cap = tsize(2 * d - 1)
        if d <= CROSS: v = 2 * cap + 7 * (d + 1) + 4 * d
        else:
            d1, d2 = (d + 1) // 2, d // 2
            v = max(2 * cap + PMM(d1), 4 * cap + 4 * d1, 2 * cap + 4 * d1 + DIVMEM(2 * d - 1, d - 1, True),
                    2 * cap + 4 * d1 + d + PMM(d2), 4 * d1 + d + 4 * d2 + 2 * tsize(2 * d) + 2 * (d + 1),
                    4 * d2 + 4 * (d + 1) + 8 * tsize(d + 1) + 4 * d)
    _PM[d] = v
    return v
def PMI(N):
    dred, d1 = split(N); L = tsize(N + 1)
    return max(PMM(d1), 4 * d1 + 2 * L, DIVMEM(N + 1, dred - 1, False), PMM(dred - d1), 4 * (dred - d1) + 2 * L)
_PG = {}
def PG(N):
    if N in _PG: return _PG[N]
    if N <= CROSS: v = 0
    else:
        dred, _ = split(N)
        v = max(PMI(N), DIVMEM(N + 1, N, False), PG(N - dred))
    _PG[N] = v
    return v

# ---------------------------------------------------------------- the complete procedure
def params(r):
    n = 5 ** (6 + r); C = 216 + 21 * r
    L = tsize(2 * n - 1); L2 = tsize(n + 1)
    e0 = max(e for e in range(64) if (1 << e) < n)
    assert P >> (254 - e0) == 1 << e0 and P >> 254 == 1
    return n, C, L, L2, e0, 254 - e0

def newton_barrett(n):
    ops = 0; k = 1; sizes = []
    while k < n:
        k2 = min(2 * k, n); Lj = tsize(k2 + k - 1); sizes.append(Lj)
        ops += k2 * CP + (Lj - k2) * ZF + k * CP + (Lj - k) * ZF + 3 * T(Lj) + Lj * PW
        ops += (k2 - k) * SC + (Lj - (k2 - k)) * ZF + 2 * T(Lj) + Lj * PW + (k2 - k) * (SC + 1)
        k = k2
    return ops, sizes

def step_items(n, L, L2):
    return [
        ('copy a into W and zero-pad to L', n * CP + (L - n) * ZF),
        ('forward transform, length L', T(L)),
        ('pointwise square', L * SC),
        ('inverse transform, length L', T(L)),
        ('scale 2n coefficients by 1/L at offset b', 2 * n * SC + 1),
        ("fold A' modulo X^L2 - 1", (2 * n - L2) * AS),
        ('keep folded low n coefficients in a', n * CP),
        ('reversed top n coefficients into W, zero-pad to L', n * CP + (L - n) * ZF),
        ('forward L, pointwise by I^, inverse L', 2 * T(L) + L * PW),
        ('reversed low n coefficients, zero-pad to L2', n * CP + (L2 - n) * ZF),
        ('forward L2, pointwise by g^, inverse L2', 2 * T(L2) + L2 * PW),
        ("R = folded A' - Q g on n coefficients", n * AS),
    ]

def setup_items():
    return [
        ('MI = M^-1 by adjugate (determinant, 9 cofactors, one inversion, 9 scalings)', 200 + INV),
        ('K, D0, D1, C2 (one inversion), D0^5, D1^5, C2^5, A, B', 200 + INV),
        ('e5 = (4(p-1)+1)/5: binary long division, 256 iterations x 20, x4 for the k-search mod 5', 4 * 256 * 20 + 500),
        ('Z of order 3*2^32: candidates 2..5, each one 221-bit and two <= 34-bit powers plus comparisons', 4 * (POW(221) + 2 * POW(34) + 50)),
        ('primitive N-th roots of unity for <= 50 transform lengths (<= 34-bit exponents)', 50 * POW(34)),
        ('inverse scalars 1/N for <= 50 transform lengths', 50 * INV),
    ]

def trial_items(r, sha_calls, k):
    n, C, L, L2, e0, steps = params(r)
    nw, _ = newton_barrett(n)
    step = sum(v for _, v in step_items(n, L, L2))
    return [
        ('sha256', sha_calls * (SHA + 8)),
        ('f_interp', L2 * (1 + LOOP + 1 + 10) + L2 * (2 * C + 20) + T(L2) + (n + 1) * SC),
        ('g_monic', (2 * C + 20) + AS + INV + (n + 1) * SC + (L2 - n - 1) * ZF),
        ('newton', nw),
        ('I_hat', n * CP + (L - n) * ZF + T(L) + L * SC),
        ('g_hat', T(L2) + L2 * SC),
        ('x_init', n * ZF + 1),
        ('powering', steps * step),
        ('g_recover', T(L2)),
        ('v', AS),
        ('gcd', G(n)),
        ('roots', 4 * AS if k == 2 else (100000 + INV if k == 3 else 10)),
    ]

def memory(r):
    n, C, L, L2, e0, steps = params(r)
    _, nsizes = newton_barrett(n)
    phases = {
        'interpolation': L2,
        'Newton': L2 + n + max(nsizes),
        'powering': 2 * L + L2,
        'gcd': 2 * L2 + min(PG(n), 2 * L),
    }
    const_words = 64 * 3 + 9 + 9 + 3 + 3 + 4 + 1 + 1 + 50 + 50 + 64
    peak = max(phases.values())
    b1 = peak * 32 + const_words * 32 + 512 + (1 << 20)
    b4 = peak * 32 + const_words * 32 + 512 + (4 << 20)
    return phases, peak, const_words, b1, b4

def total(r):
    import math
    n, C, L, L2, e0, steps = params(r)
    case = CASES[r]; rows = []; W = sum(v for _, v in setup_items())
    for i, k in enumerate(case['degs']):
        s0, calls = s0_stream(r, i)
        items = trial_items(r, calls, k); s = sum(v for _, v in items); W += s
        rows.append((i, s0, calls, k, items, s))
    fin = 2 * (3 * ROOT5 + 200) + 2 * (2 * C + 50)
    W += fin
    tl = math.log2(W / C)
    return dict(W=W, rows=rows, fin=fin, time_log2=tl)

def certificate(r):
    case = CASES[r]; i = len(case['degs']) - 1
    s0, _ = s0_stream(r, i); s1 = case['s1']
    A, B = inputs_from_s(s0), inputs_from_s(s1)
    assert A != B and all(x < P for x in A + B)
    enc = lambda t: (t[0].to_bytes(32, 'little') + t[1].to_bytes(32, 'little')).hex()
    return enc(A), enc(B)

if __name__ == '__main__':
    req = json.loads(sys.stdin.read())
    r = int(req['target_profile'].split('-r')[1].split('-')[0])
    ma, mb = certificate(r)
    tot = total(r); n = params(r)[0]
    phases, peak, cw, b1, b4 = memory(r)
    obs = {'gcd_bound_ops': G(n), 'total_ops_W': tot['W'], 'time_log2_x1e6': int(tot['time_log2'] * 1e6),
           'peak_words': peak, 'memory_bytes_4mib_allowance': b4}
    out = {'schema_version': 1, 'trials': []}
    for t in req['trials']:
        out['trials'].append({'trial': t['trial'], 'message_a_hex': ma, 'message_b_hex': mb, 'observations': obs})
    sys.stdout.write(json.dumps(out))
```
