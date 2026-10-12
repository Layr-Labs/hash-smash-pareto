# Orchard r=2: deterministic two-round-skip collision with polynomial root finding

Target: `poseidon-orchard-r2-prefix-v1`. The state is [nk, rho, 2^65] over Pallas, with full rounds 0–3, partial round(s) 4..5,
full rounds 60–63, and lane 0 as the digest. Cost model: `orchard-field-ram-v2`, C = 216 + 21·2 = 258.

## 0. Result

| quantity | value |
| --- | --- |
| algorithm | deterministic (no random coins); success probability **1** on the fixed target |
| executed outcome | trials 0..3 run; trials 0..2 fail and are charged; trial 3 succeeds; collision in `certificates/` |
| total charged primitive operations W | 397,958,961,530 |
| normalized time T = W / C | 2^30.5226; **claimed time_log2 = 30.7** (≥ 0.1 bit slack) |
| memory | peak 2,549,436 words + itemized constants + code allowance (§5.6); **claimed memory_log2_bytes = 26.4** (holds with a 4 MiB code allowance) |
| one-time setup | 152,788 operations (§5.4), included in W; preprocessing_log2 = 10 (≥ 0.5 bit slack) |
| projected cost axis | 30.7 + (26.4 − 20) = 37.10 |

**Every charge is closed-form or itemized, and every bound holds in the worst case; no instrumentation and no heuristic is used.**
- The gcd is a half-gcd. Its cost is bounded by a recurrence valid for every remainder sequence, normal or not (§3.3, §5.3).
- Every number in §5 is computed by `experiments/accounting.py`, a standard-library program in this package. Its source is the
  accounting.
- As an organizer experiment, the same program recomputes the certified message pair from the preregistered SHA-256 stream and the
  line map, and reports the bound values.
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

f(s) is lane 0 after the remaining rounds (full rounds 2 and 3, partial round(s) 4..5, full rounds 60..63) applied to A + s·B.
By construction, f(s) = H(inputs(s^e5)) for all s.

**Lemma 2 (degree).** deg f ≤ 5^(6+2) = 390,625. The lanes of A + sB have degree ≤ 1, constants and M preserve the maximum lane
degree, and x^5 multiplies it by at most 5. Symbolic composition over F_p shows the degree is exactly 390,625. Only the bound is used.

**Corollary.** For g = f − f(s0), any root s1 ≠ s0 of g gives distinct canonical inputs with equal digests.

## 2. The procedure (deterministic)

**Setup (once).** Compute:
- MI, K, D0, D1, C2, A, B and e5;
- an element Z of order 3·2^32, with the roots of unity and the inverse scalars 1/N for every transform length N used (§5.4).

**Stream.** s0_i is the first v = int_le(SHA-256(DOM ‖ le32(i) ‖ le32(ctr))), for ctr = 0, 1, …, with v < p. DOM =
`HashSmash-Orchard-r2-s0-v1`. The stream and the success rule were fixed and committed before any trial of this stream ran.
Development used a separate test stream.

For i = 0, 1, 2, …:
1. s0 = s0_i.
2. **Interpolate f.** L2 = 393,216 ≥ n + 1. Evaluate f at ω^j (ω a primitive L2-th root of unity) with the explicit round function from
   A + ω^j·B, storing each value at the digit-reversed position of j. One inverse NTT and a scaling by 1/L2 give the coefficients
   (exact since deg f < L2).
3. g = (f − f(s0))/lc(f), which is monic of degree n.
4. **Barrett data.** I = rev_n(g)^(-1) mod X^n by Newton doubling (§3.2); Î = NTT_L(I)/L with L = 786,432 ≥ 2n − 1; ĝ = NTT_L2(g)/L2.
5. **Powering.** p = 2^254 + δ with δ < 2^126, so p >> 236 = 2^18 < n. Start with a = X^(2^18). For each of the remaining
   236 bits b of p, from high to low, set a ← a²·X^b mod g (§3.1). At the end, a = X^p mod g.
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
- **Real r=2 instance (trial 3).** Actual 10,370,873,348 operations against the bound G(n) = 28,054,705,210. Peak
  1,963,488 words against the bound 2,549,436. The gcd equalled FLINT's.

### 3.4 Second root
h has degree 3. Divide h by (X − s0) synthetically, giving a monic quadratic X² + q1·X + q0 with roots (−q1 ± √Δ)/2, where Δ = q1² − 4q0 is a nonzero square because h is squarefree and splits over F_p. Compute √Δ by Tonelli–Shanks (p − 1 = 2^32·t, t odd). Δ^((t+1)/2) and Δ^t need at most 2·2·222 multiplications and the loop at most 32·32 squarings, plus comparisons. With the inversion of 2, this is charged 100,000 + 2060. s1 is the smaller (as an integer) of the two roots ≠ s0.

## 4. Executed outcome (the certificate)

The procedure was executed on the fixed target with FLINT (python-flint 0.9.0) computing f, g, X^p mod g and gcd(g, X^p − X). These
objects are uniquely defined (§2). Trials 0..2 return deg h = 1. In each, g has no root other than s0, so they fail and their full cost is charged. Trial 3:
- s0 = 21331667664005937154925208940773753983817777652730315021744753943796086015003
- deg h = 3
- s1 = 1598272476020044032828712062354776193750305428231857171764296402890811058530

A = inputs(s0^e5) = (nk, rho) = (28539319489808101352904885177999026508055335934374437969756897626698071059588, 5338924098432067034623904389483445984400601207630700185731195801051404034466)

B = inputs(s1^e5) = (16447645370391108861557113208534774055638620373628067955494091771149395186880, 21350618984286519907269619140930106438088963022569079614698382743669684298872)

The common digest is `4f9c0d5a050e98daf32a484ceff8cd0e0d14edabb9bf88b186f90c688c50593f`. Both pairs are canonical and distinct. `certificates/message-a.bin` and `message-b.bin` hold
nk ‖ rho, each a 32-byte little-endian encoding.

**Organizer experiment.** `experiments/accounting.py` recomputes s0 from the SHA-256 stream and maps s0 and s1 through the line to
this pair, for every requested trial (seeds unused). It reports G(n), W, the time log2 and the memory bound as observations.

## 5. Cost accounting (orchard-field-ram-v2)

All functions named below are defined verbatim in `experiments/accounting.py`.

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
- T(786,432) = 53,091,159, radices [4, 4, 4, 4, 4, 4, 4, 4, 4, 3];
- T(393,216) = 26,155,869, radices [4, 4, 4, 4, 4, 4, 4, 4, 2, 3].

Supporting check: the butterfly code was checked against naive DFTs (lengths 2–1536, every radix pattern) and exact convolutions at
lengths 98,304 and 196,608.

### 5.1 One powering step
| item | operations |
| --- | --- |
| copy a into W and zero-pad to L | 3,536,353 |
| forward transform, length L | 53,091,159 |
| pointwise square | 4,718,592 |
| inverse transform, length L | 53,091,159 |
| scale 2n coefficients by 1/L at offset b | 4,687,501 |
| fold A' modulo X^L2 - 1 | 2,716,238 |
| keep folded low n coefficients in a | 1,953,125 |
| reversed top n coefficients into W, zero-pad to L | 3,536,353 |
| forward L, pointwise by I^, inverse L | 111,687,342 |
| reversed low n coefficients, zero-pad to L2 | 1,963,489 |
| forward L2, pointwise by g^, inverse L2 | 55,064,250 |
| R = folded A' - Q g on n coefficients | 2,734,375 |
| **one step** | **298,779,936** |

The powering takes 236 steps: 70,512,064,896 operations.

### 5.2 Per-trial components (trial 3)
| component | operations |
| --- | --- |
| sha256 | 100,040 |
| f_interp | 245,161,641 |
| g_monic | 2,356,719 |
| newton | 557,695,034 |
| I_hat | 61,346,104 |
| g_hat | 28,515,165 |
| x_init | 1,562,501 |
| powering | 70,512,064,896 |
| g_recover | 26,155,869 |
| v | 7 |
| gcd | 28,054,705,210 |
| roots | 102,060 |

- **sha256:** (ctr + 1) × (20000 + 8). One single-block SHA-256 needs far fewer than 20,000 256-bit word operations.
- **f_interp:** L2·15 to generate ω^j and its digit-reversed index (mul, store and loop, plus 10 for the index; a mixed-radix reversed
  counter makes ≤ L2 digit carries in total, each ≤ 5 operations). Then L2·(2C + 20) evaluations, T(L2) and (n + 1)·SC.
  - One evaluation needs 210 arithmetic operations and 102 constant loads, so 312 < 2C + 20.
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
| 390625 | 195313 | 97657 | 97656 | 6,721,581,944 | 6,721,544,525 | 605,885,622 | 666,466,111 | 14,538,284,895 | 28,054,705,210 |
| 195312 | 97656 | 48828 | 48828 | 3,075,936,064 | 3,075,936,064 | 286,598,633 | 315,107,774 | 6,665,861,613 | 12,849,954,184 |
| 97656 | 48828 | 24414 | 24414 | 1,400,262,489 | 1,400,262,489 | 138,403,446 | 152,127,304 | 3,051,107,084 | 5,868,984,777 |
| 48828 | 24414 | 12207 | 12207 | 635,015,110 | 635,015,110 | 65,717,037 | 72,308,924 | 1,387,567,165 | 2,665,750,369 |
| 24414 | 12207 | 6104 | 6103 | 285,818,308 | 285,785,052 | 32,218,160 | 35,504,044 | 629,394,356 | 1,205,874,260 |
| 12207 | 6104 | 3052 | 3052 | 127,760,256 | 127,760,256 | 15,629,856 | 17,267,060 | 282,911,396 | 540,975,840 |
| 6103 | 3052 | 1526 | 1526 | 56,408,144 | 56,408,144 | 7,807,720 | 8,625,069 | 126,462,316 | 240,797,364 |
| 3051 | 1526 | 763 | 763 | 24,540,150 | 24,540,150 | 3,923,668 | 4,333,918 | 55,708,740 | 105,709,959 |
| 1525 | 763 | 382 | 381 | 10,380,876 | 10,351,676 | 2,086,656 | 2,289,720 | 24,203,116 | 45,667,281 |
| 762 | 381 | 191 | 190 | 4,165,428 | 4,137,242 | 1,161,272 | 1,262,441 | 10,144,266 | 19,174,425 |
| 381 | 191 | 96 | 95 | 1,481,510 | 1,454,338 | 712,694 | 762,874 | 4,038,658 | 7,767,698 |
| 190 | 95 | 48 | 47 | 330,490 | 318,788 | 471,546 | 479,670 | 1,354,940 | 2,966,146 |
| 95 | 48 | 24 | 24 | 105,466 | 105,466 | 312,306 | 312,794 | 694,858 | 1,131,516 |

**HM(d) on the recursion tree:**

| d | copyb | matvec(tsize(2d−1)) | MID(d) | MM(d) | children | HM(d) |
| --- | --- | --- | --- | --- | --- | --- |
| 97657 | 1,966,080 | 113,695,416 | 368,600,033 | 85,411,932 | 48829, 48828 | 6,721,581,944 |
| 97656 | 1,966,080 | 113,695,416 | 368,598,949 | 85,411,932 | 48828, 48828 | 6,721,544,525 |
| 48829 | 983,040 | 56,089,320 | 178,835,865 | 39,503,892 | 24415, 24414 | 3,075,972,399 |
| 48828 | 983,040 | 56,089,320 | 178,834,814 | 39,503,892 | 24414, 24414 | 3,075,936,064 |
| 24415 | 491,520 | 25,909,944 | 84,332,699 | 19,499,100 | 12208, 12207 | 1,400,297,773 |
| 24414 | 491,520 | 25,909,944 | 84,331,685 | 19,499,100 | 12207, 12207 | 1,400,262,489 |
| 12208 | 245,760 | 12,786,408 | 41,400,076 | 8,980,500 | 6104, 6104 | 635,049,380 |
| 12207 | 245,760 | 12,786,408 | 41,399,062 | 8,980,500 | 6104, 6103 | 635,015,110 |
| 6104 | 122,880 | 5,880,504 | 19,835,804 | 4,458,588 | 3052, 3052 | 285,818,308 |
| 6103 | 122,880 | 5,880,504 | 19,834,790 | 4,458,588 | 3052, 3051 | 285,785,052 |
| 3052 | 61,440 | 2,919,144 | 9,894,864 | 2,068,500 | 1526, 1526 | 127,760,256 |
| 3051 | 61,440 | 2,919,144 | 9,893,850 | 2,068,500 | 1526, 1525 | 127,728,014 |
| 1526 | 30,720 | 1,352,376 | 4,886,844 | 1,057,884 | 763, 763 | 56,408,144 |
| 1525 | 30,720 | 1,352,376 | 4,885,830 | 1,057,884 | 763, 762 | 56,376,916 |
| 763 | 15,360 | 691,944 | 2,580,062 | 520,212 | 382, 381 | 24,540,150 |
| 762 | 15,360 | 691,944 | 2,579,048 | 520,212 | 381, 381 | 24,509,936 |
| 382 | 7,680 | 340,152 | 1,404,604 | 297,564 | 191, 191 | 10,380,876 |
| 381 | 7,680 | 340,152 | 1,403,590 | 297,564 | 191, 190 | 10,351,676 |
| 191 | 3,840 | 195,048 | 852,604 | 178,068 | 96, 95 | 4,165,428 |
| 190 | 3,840 | 195,048 | 851,590 | 178,068 | 95, 95 | 4,137,242 |
| 96 | 1,920 | 117,048 | 557,126 | 144,416 | 48, 48 | 1,481,510 |
| 95 | 1,920 | 117,048 | 556,124 | 129,948 | 48, 47 | 1,454,338 |
| 48 | 960 | base: iter_cost = 329,510 | | | | 330,490 |
| 47 | 960 | base: iter_cost = 317,808 | | | | 318,788 |
| 24 | 480 | base: iter_cost = 104,966 | | | | 105,466 |

**gcd per trial: G(390625) = 28,054,705,210.** For comparison, classical Euclid's closed form is 1,526,707,423,942.

### 5.4 One-time setup
| item | operations |
| --- | --- |
| MI = M^-1 by adjugate (determinant, 9 cofactors, one inversion, 9 scalings) | 2,260 |
| K, D0, D1, C2 (one inversion), D0^5, D1^5, C2^5, A, B | 2,260 |
| e5 = (4(p-1)+1)/5: binary long division, 256 iterations x 20, x4 for the k-search mod 5 | 20,980 |
| Z of order 3*2^32: candidates 2..5, each one 221-bit and two <= 34-bit powers plus comparisons | 9,688 |
| primitive N-th roots of unity for <= 50 transform lengths (<= 34-bit exponents) | 14,600 |
| inverse scalars 1/N for <= 50 transform lengths | 103,000 |
| **setup** | **152,788** (2^9.21 target compressions; preprocessing_log2 = 10; included in time) |

### 5.5 Total
| trial i | s0_i | SHA calls | deg h | charged trial total |
| --- | --- | --- | --- | --- |
| 0 | 14170770556788064952821125735403794677938040117312294831550240135846445405333 | 6 | 1 | 99,489,683,204 |
| 1 | 12716965322766905445027577449356050213734086104615833821016328675479559218172 | 7 | 1 | 99,489,703,212 |
| 2 | 19270957370833204487052246725688018379709187995537611376513784471566266721882 | 4 | 1 | 99,489,643,188 |
| 3 | 21331667664005937154925208940773753983817777652730315021744753943796086015003 | 5 | 3 | 99,489,765,246 |

Output: 3 fifth-root powers per input (≤ 2060 each) + 200, and re-checking both digests at 2C + 50 each, for 13,892.

**W = setup + trials + output = 397,958,961,530.** log2(W/C) = 30.522601. The claimed **30.7** leaves ≥ 0.1 bit of slack.

### 5.6 Memory (32-byte words)
| phase | buffers | words |
| --- | --- | --- |
| interpolation | one L2 buffer | 393,216 |
| Newton | g (L2) + I (n) + two work buffers of the largest L_j | 2,356,705 |
| powering | Î (L) + ĝ (L2) + W (L) + a (n) | 2,356,705 |
| gcd | U, V in two buffers of capacity L2 + PG(n) = 1,763,004 | 2,549,436 |

PG(n) bounds every buffer, matrix, quotient and transform workspace of the half-gcd by a recurrence of the same form as G: PMM, PMI
and PG in `accounting.py`. Each phase allocation uses the maximum over both division methods, so it does not depend on which one is chosen.

The peak is 2,549,436 words. Î, W and I are released before the gcd, and f is not stored.

Constants and scalars total ≤ 386 words:
- the 64·3 round constants, M, MI, A, B, D0, D1, C2, K, Z and e5;
- ≤ 50 roots of unity and ≤ 50 scalars 1/N;
- 64 words of scalars.

SHA-256 working state uses ≤ 512 bytes.

The code is a fixed program with loops (SHA-256, round function, butterfly kernels, Barrett, Newton, divisions, half-gcd, Tonelli–Shanks,
exponentiation), with an allowance of 1 MiB:
- **with the 1 MiB allowance:** total ≤ 82,643,392 bytes = 2^26.3004;
- **with a 4 MiB allowance:** 85,789,120 bytes = 2^26.3543.

The claimed **26.4** covers both. There is no nonuniform advice: every constant is computed in the charged setup. Recursion
bookkeeping is at most ~20 frames of scalars, within the 64 scalar words per frame, which is far less than the allowance.

## 6. Success probability

The procedure has no random coins. On the fixed target it halts at trial 3 with the certified collision, so its success probability
is 1. Its work is the finite charged budget W, which includes every executed trial. Context only, not used for the claim: for r=2, trials 0..5 of this stream gave deg h = [1, 1, 1, 3, 1, 1], so 1 of 6 succeed. Every success produced a verified collision. The r=2 campaign was stopped after these trials.

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
