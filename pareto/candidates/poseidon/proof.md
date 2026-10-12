# Orchard r=2: deterministic two-round-skip collision with polynomial root finding

Target: `poseidon-orchard-r2-prefix-v1`. The state is [nk, rho, 2^65] over Pallas, with full rounds 0–3, partial round(s) 4..5,
full rounds 60–63, and lane 0 as the digest. Cost model: `orchard-field-ram-v2`, C = 216 + 21·2 = 258.

## 0. Result

| quantity | value |
| --- | --- |
| algorithm | deterministic (no random coins); success probability **1** on the fixed target |
| executed outcome | trials 0..3 run; trials 0..2 fail and are charged; trial 3 succeeds; collision in `certificates/` |
| total charged primitive operations W | 6,391,438,768,050 |
| normalized time T = W / C | 2.477302e+10 = 2^34.5281; **claimed time_log2 = 34.6** |
| memory | peak 2,356,705 words + itemized constants + code allowance (§5.5); **claimed memory_log2_bytes = 26.3**, which holds even with a 4 MiB code allowance |
| one-time setup | 32,940 operations (§5.4), included in W; preprocessing_log2 = 7 |
| projected cost axis | 34.6 + (26.3 − 20) = 40.90 |

**All charges are closed-form or itemized; no instrumentation and no heuristic is used.** The gcd is the classical
Euclidean algorithm with a worst-case bound valid for every remainder sequence (§3.3, §5.3). The certificate was checked
with the reference `verifier/poseidon.py:digest`.

## 1. A univariate line through the first two full rounds

Notation: RC_i are the round constants of round i, M is the deployed MDS matrix, and MI = M^(-1). All field elements are canonical in [0, p).
Since gcd(5, p − 1) = 1, the map x ↦ x^5 is a bijection of F_p with inverse x ↦ x^e5, where e5 = 5^(-1) mod (p − 1) = (4(p − 1) + 1)/5.

**Round 0.** Round 0 adds RC_0, applies x^5 to all lanes, then M. Lane 2 is fixed to 2^65, so its S-box output is the constant
K = (2^65 + RC_0[2])^5 = 0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c.
With X0 = (nk + RC_0[0])^5 and X1 = (rho + RC_0[1])^5, the round-0 output is Y = M·(X0, X1, K)ᵀ. The map (nk, rho) ↦ (X0, X1) is a bijection of F_p².

**Round 1.** The round-1 S-box input is u = Y + RC_1. A vector u arises from some (nk, rho) if and only if the third coordinate of
MI·(u − RC_1) equals K. When it does, the preimage is unique: X = MI·(u − RC_1), nk = X0^e5 − RC_0[0], rho = X1^e5 − RC_0[1].

**The line.** Take u(t) = (t·D0, t·D1, C2) with

- D0 = MI[2][1] = 0x1ec7372574f3851bb4ddd4b4d6452256c5e4960d7424cd3776efab42d4fba90b
- D1 = −MI[2][0] = 0x103445906ea65de68dc59c5f3f6254d9734d87cd741d1d666eeba35f8c5836f9
- C2 = (K + Σ_j MI[2][j]·RC_1[j]) / MI[2][2] = 0x09b2d7e67acf680114704863d53135870423bf02a5b6414ddd79da0955bb7210

Here MI[2][2] = 0x0d0c2efd6472f12a3c26fa4b7d25b1e487a7435d30f8be81adc8933c6f3c72ee ≠ 0. Since MI[2][0]·tD0 + MI[2][1]·tD1 = 0 for every t, the third coordinate of MI·(u(t) − RC_1)
is −Σ_j MI[2][j]RC_1[j] + MI[2][2]·C2 = K. Hence every t ∈ F_p gives a valid input pair inputs(t) = (nk(t), rho(t)).

**Lemma 1 (injectivity).** t ↦ inputs(t) is injective. u(t) is injective because D0 ≠ 0, u ↦ X is affine and invertible,
and X ↦ (nk, rho) is a bijection.

**Linearization.** The round-1 S-box outputs are (t^5·D0^5, t^5·D1^5, C2^5). Put s = t^5, which is a bijection with t = s^e5.
The round-1 output is then the affine function A + s·B, with A_i = M[i][2]·C2^5 and B_i = M[i][0]·D0^5 + M[i][1]·D1^5:

- A = (0x3ee27bfc9cfef88d27c792814848db51ceef97df9c0e5b45019550f933c44f57, 0x0ce52aaa238bc3ef49ca04d2538ba2bbff69145bc89d598a902f1616c1d228a2, 0x074cd8e568bd3331d9cc0068f9b5f3cf3ab985eb827eed4e2e35f7d2e5faddf7)
- B = (0x1d9ea4aadb298d5ff0585f6e5528d3b39e186bc7d11ecac983b2a50005ff6a80, 0x23a943cb8b60ec2bb5b00e193220410e586ac052e6b396154e60390348fe3ba8, 0x39c59dc5f76bc45cf562072a98bb22407b3e7ba493d05942d96f4e858199d234)

Define f(s) as lane 0 after applying the remaining rounds (full rounds 2 and 3, partial round(s) 4..5, full rounds 60..63) to A + s·B. By
construction, f(s) = H(inputs(s^e5)) for every s ∈ F_p, where H is the r=2 digest.

**Lemma 2 (degree).** deg f ≤ 5^(6+2) = 390,625. Lanes of A + sB have degree ≤ 1. Constant addition and M do not raise the maximum
lane degree, and x^5 multiplies it by at most 5. The rounds 2 and 3, the 2 partial round(s) and the 4 final rounds give 5^(2+2+4).
Symbolic composition over F_p shows that the degree is exactly 390,625. Only the bound is used: with a smaller degree, the same
procedure runs with smaller n.

**Corollary.** For s0 ∈ F_p and g = f − f(s0), any root s1 ≠ s0 of g gives distinct canonical inputs inputs(s1^e5) ≠ inputs(s0^e5)
with equal digests. That is a collision.

## 2. The procedure (deterministic)

**Setup (once).** Compute MI, K, D0, D1, C2, A, B, e5, an element Z of order 3·2^32, and the roots of unity ω_N = Z^(3·2^32/N) for the
transform lengths used (§5.4).

**Stream.** s0_i is the first v = int_le(SHA-256(DOM ‖ le32(i) ‖ le32(ctr))), for ctr = 0, 1, …, with v < p. DOM =
`HashSmash-Orchard-r2-s0-v1`. The stream and its success rule were fixed and committed before any of its trials ran. Earlier
development used a separate test stream. This stream is the only one used for the claim.

For i = 0, 1, 2, …:
1. Compute s0 = s0_i.
2. **Interpolate f.** L2 = 393,216 ≥ n + 1. Evaluate f at ω^j (ω = ω_L2, j < L2) by the explicit round function from
   A + ω^j·B, storing each value at the digit-reversed position of j. One inverse NTT and scaling by 1/L2 give the coefficients of f.
   This is exact because deg f < L2.
3. c = f(s0) by one evaluation; g = (f − c)/lc(f), which is monic of degree n.
4. **Barrett data.** I = rev_n(g)^(-1) mod X^n by Newton doubling (§3.2). Store Î = NTT_L(I)/L with L = 786,432 ≥ 2n − 1, and ĝ = NTT_L2(g)/L2.
5. **Powering.** p = 2^254 + δ with δ < 2^126, so p >> 236 = 2^18, and 2^18 < n. Start with a = X^(2^18). For each of the
   remaining 236 bits b of p, from high to low, set a ← a²·X^b mod g (§3.1). The result is a = X^p mod g.
6. Recover g = NTT_L2^(-1)(ĝ) (exact, because ĝ contains the factor 1/L2), and set V = a − X in place.
7. **gcd.** h = gcd(g, V) by the classical Euclidean algorithm, then made monic (§3.3). h = ∏(X − z) over the distinct roots z ∈ F_p of g,
   and s0 is always one of them.
8. If deg h = 1, continue with i + 1. Otherwise extract s1 ≠ s0 (§3.4), output (inputs(s0^e5), inputs(s1^e5)) and halt.

Every step is exact F_p arithmetic, and every intermediate result is uniquely defined: f, g, X^p mod g and the monic gcd h. The trial
outcome is therefore a function of i alone, the same for every correct implementation.

## 3. Correctness of the subroutines

### 3.1 Barrett step
Let g be monic of degree n, deg a < n, and A' = a²·X^b, so deg A' ≤ 2n − 1. Write A' = Q·g + R with deg R < n and deg Q ≤ n − 1.
Then rev_{2n−1}(A') = rev_{n−1}(Q)·rev_n(g) + X^n·rev_{n−1}(R), hence rev_{n−1}(Q) ≡ H·I (mod X^n), where
H = rev_{n−1}(A' div X^n).

Transform lengths:
- a² and H·I are products of two n-coefficient polynomials of degree ≤ 2n − 2 < L, so length-L cyclic convolution is exact.
- R = A' − Q·g has degree < n ≤ L2. So coefficients 0..n−1 of (A' mod (X^L2 − 1)) − (Q·g mod (X^L2 − 1)) are exactly R.
- The fold touches only indices ≤ 2n − 1 − L2 < n.

The buffers are a (n words) and W (L words). The order of work is:
1. a → W; forward; square; inverse.
2. Scale; fold; copy the low n coefficients to a.
3. Reversed top n coefficients → W; forward; multiply by Î; inverse.
4. Reversed low n coefficients, zero-padded to L2; forward L2; multiply by ĝ; inverse.
5. a ← a − W[0..n).

**Supporting check (not score-critical).** These identities, with the transform lengths emulated exactly as products mod X^L − 1, were
compared with FLINT's (a²X^b) mod g. Every n in {5, 6, 7, 64, 125, 625, 1000, 3125, 15625} used 3 random monic g with both b. Each of
n ∈ {78125, 390625} used 1 random g with both b. Python `random` was unseeded. All comparisons matched.

### 3.2 Newton inverse
I_1 = 1, because rev_n(g)(0) = lc(g) = 1. Step k → k' = min(2k, n), with F = rev_n(g) mod X^k':
- e = F·I_k is a product of lengths k' and k, exact at cyclic length L_j = tsize(k' + k − 1). Its coefficients 0..k−1 are (1, 0, …, 0).
- E is coefficients k..k'−1 of e, and I_k' = I_k − X^k·(I_k·E mod X^(k'−k)). This product of lengths k and k' − k is exact at the same L_j.

This is the standard iteration I_k' ≡ I_k(2 − F·I_k) mod X^k'. Here tsize(l) is the least 2^j or 3·2^(j−2) that is ≥ l. The lengths used
are [2, 6, 12, 24, 48, 96, 192, 384, 768, 1536, 3072, 6144, 12288, 24576, 49152, 98304, 196608, 393216, 786432].

### 3.3 Classical Euclid and its worst-case bound
Let U = g (degree n) and V = X^p − X mod g (degree < n). Repeat: if V = 0, stop; otherwise replace U by U mod V by schoolbook long
division, in place in U's buffer, then swap the roles of U and V. Finally make U monic. This computes the monic gcd for any input.

**Bound.** Let the successive divisor degrees be d_1 > d_2 > … > d_m (all < n), with d_0 = n. Division i divides a polynomial of degree
d_(i−1) by one of degree d_i. Its quotient has d_(i−1) − d_i + 1 coefficients, and each quotient coefficient updates at most d_i + 1
coefficients of the dividend, so the division makes at most (d_(i−1) − d_i)(d_i + 1) + (d_i + 1) updates.

- **First term.** Each of its d_(i−1) − d_i factors d_i + 1 is ≤ every integer j in (d_i, d_(i−1)]. So the first term is at most the sum of
  those j. These ranges are disjoint subsets of [1, n], so the first terms total ≤ n(n+1)/2.
- **Second term.** The d_i are distinct integers in [0, n − 1], so the second terms total ≤ Σ_(j=0)^(n−1)(j + 1) = n(n+1)/2.

Hence **total coefficient updates ≤ n(n+1)** for every remainder sequence. Also m ≤ n, Σ(d_(i−1) − d_i + 1) ≤ 2n quotient coefficients, and
the leading-zero scans total ≤ 2n.

### 3.4 Second root
h has degree 3. Divide h by (X − s0) synthetically to get a monic quadratic X² + q1·X + q0. Its roots are (−q1 ± √Δ)/2 with Δ = q1² − 4q0, a nonzero square because h is squarefree and splits over F_p. √Δ is computed by Tonelli–Shanks (p − 1 = 2^32·t, t odd): Δ^((t+1)/2) and Δ^t cost at most 2·2·222 multiplications, and the loop at most 32·32 squarings, with comparisons. Together with the inversion of 2, this is charged 100,000 + 1340 primitive operations, well above the ≈ 2,000 multiplications plus control actually needed. s1 is the smaller, as an integer, of the two roots ≠ s0.

## 4. Executed outcome (the certificate)

The procedure was executed on the fixed target with FLINT (python-flint 0.9.0) computing f, g, X^p mod g and gcd(g, X^p − X). The
uniquely defined objects of §2 do not depend on the implementation. Trials 0..2 return deg h = 1: g has no root other than s0, so they fail. Their full cost is charged. Trial 3 has:

- s0 = 21331667664005937154925208940773753983817777652730315021744753943796086015003
- deg h = 3, roots ≠ s0: 1598272476020044032828712062354776193750305428231857171764296402890811058530, 16585984983978259219322117997105424113817278039301620486520257850184862830988
- s1 = 1598272476020044032828712062354776193750305428231857171764296402890811058530

A = inputs(s0^e5) = (nk, rho) = (28539319489808101352904885177999026508055335934374437969756897626698071059588, 5338924098432067034623904389483445984400601207630700185731195801051404034466)

B = inputs(s1^e5) = (16447645370391108861557113208534774055638620373628067955494091771149395186880, 21350618984286519907269619140930106438088963022569079614698382743669684298872)

The common digest (lane 0, 32-byte little-endian) is `4f9c0d5a050e98daf32a484ceff8cd0e0d14edabb9bf88b186f90c688c50593f`. Both pairs are canonical and distinct.
`certificates/message-a.bin` and `message-b.bin` are the 64-byte encodings nk ‖ rho, each 32-byte little-endian.

## 5. Cost accounting (orchard-field-ram-v2)

**Unit charges.** Each field add, subtract or multiply costs 1, as does each 256-bit load, store, compare, branch, shift or pointer
update. A simple loop iteration costs LOOP = 3 (increment, compare, branch). Per element:
- copy: 5
- zero-fill: 4
- scale or square (load, multiply, store): 6
- pointwise product or add/subtract (two loads, operation, store): 7

An inversion is charged INV = 4·(254 + 76) + 20 = 1340. Fermat a^(p−2) by square-and-multiply: p − 2 has 255 bits and Hamming
weight 77, so it takes 254 squarings and 76 multiplications, each charged 4 (multiply, bit test, branch, loop). A power with a ≤ k-bit
exponent is charged 8k + 20.

**NTT.** The forward transform is an in-place mixed-radix (4/2/3) decimation-in-frequency NTT, natural to digit-reversed order. The inverse is
its transposed decimation-in-time form, digit-reversed to natural order and unscaled. Pointwise products do not depend on the order.
Per butterfly, including loads, stores, address arithmetic and loop control:
- radix-4: 4 ld + 4 st + 4 mul (√−1 and three twiddles) + 8 add/sub + 6 = 26
- radix-2: 2 ld + 2 st + 1 mul + 2 add/sub + 4 = 11
- radix-3: 3 ld + 3 st + 3 mul (ζ₃ and two twiddles) + 7 add/sub + 5 = 21

Twiddles are generated incrementally per pass, with no table: 6, 4 or 5 operations per twiddle index (radix 4, 2 or 3).
T0(N) = Σ_passes (BF·N/f + TW·(twiddle indices)).

Each transform is also charged NTT_OVH = 6000 for its per-pass root powers: ≤ 11 passes, each with two powers of ≤ 21-bit
exponents (≤ 2·188), plus the one inversion of ω in the inverse transform (1,340). That totals ≤ 5,476.

T(N) = T0(N) + 6000:
- T(786,432) = 53,090,159, radices [4, 4, 4, 4, 4, 4, 4, 4, 4, 3]
- T(393,216) = 26,154,869, radices [4, 4, 4, 4, 4, 4, 4, 4, 2, 3]

**Supporting check (not score-critical).** The butterfly implementation was checked against naive DFTs (lengths 2–1536, every radix
pattern) and as exact convolutions at lengths 98,304 and 196,608.

### 5.1 One powering step
| item | operations |
| --- | --- |
| copy a into W (n·5) and zero-pad to L ((L−n)·4) | 3,536,353 |
| forward transform, length L | 53,090,159 |
| pointwise square (L·6) | 4,718,592 |
| inverse transform, length L | 53,090,159 |
| scale 2n coefficients by 1/L, written at offset b (2n·6 + 1) | 4,687,501 |
| fold A' modulo X^L2 − 1 ((2n − L2)·7) | 2,716,238 |
| keep folded low n coefficients in a (n·5) | 1,953,125 |
| H = reversed top n coefficients into W, zero-pad to L (n·5 + (L−n)·4) | 3,536,353 |
| forward L, pointwise ·Î (L·7), inverse L | 111,685,342 |
| Q = reversed low n coefficients, zero-pad to L2 (n·5 + (L2−n)·4) | 1,963,489 |
| forward L2, pointwise ·ĝ (L2·7), inverse L2 | 55,062,250 |
| R = folded A' − Q·g on n coefficients (n·7) | 2,734,375 |
| **one step** | **298,773,936** |

There are 236 steps, costing 70,510,648,896.

### 5.2 Per-trial components (trial 3; trials differ only in the SHA count and the root step)
| component | operations |
| --- | --- |
| sha256 | 100,040 |
| f_interp | 245,161,981 |
| g_monic | 2,355,999 |
| newton | 557,625,494 |
| I_hat | 61,346,444 |
| g_hat | 28,515,505 |
| x_init | 1,562,501 |
| powering | 70,510,648,896 |
| g_recover | 26,154,869 |
| v | 7 |
| euclid | 1,526,426,173,222 |
| roots | 101,340 |

Formulas:
- **sha256:** (ctr + 1) compressions × (20000 + 8). 20,000 bounds one single-block SHA-256 (64 rounds of 32-bit operations plus message schedule).
- **f_interp:** L2·15 to generate ω^j and its digit-reversed index (mul, store, loop, 10 for the index), plus L2·(2C + 20) evaluations,
  plus T(L2) + (n + 1)·6 + INV.
  - One evaluation does 210 arithmetic operations: A + sB, then rounds 2, 3, the partial round(s) and 60–63.
  - It also does 102 constant loads: 12 per round, plus A and B.
  - That is 312 < 2C + 20 = 536.
- **g_monic:** one evaluation (2C + 20) + a subtraction + INV + (n + 1)·6 + zero-padding.
- **newton:** each doubling step uses 5 transforms of length L_j, 2·L_j·7 pointwise operations, loads and zero-pads, and scalings, plus INV per distinct L_j.
- **I_hat:** n·5 + (L − n)·4 + T(L) + L·6 + INV.
- **g_hat:** T(L2) + L2·6 + INV.
- **x_init:** n·4 + 1.
- **g_recover:** T(L2).
- **v:** one subtraction.
- **roots:** §3.4.

### 5.3 Euclid charge (closed form, §3.3)
- Each coefficient update is charged 10: load the dividend coefficient, load the divisor coefficient, multiply by the quotient digit
  held in a register, subtract, store, advance two pointers, then increment, compare and branch.
- Each quotient coefficient is charged 8: load the leading coefficient, multiply by the inverse, test, and loop.
- Each division is charged INV + 20 for the inverse of the divisor's leading coefficient plus swap bookkeeping.
- Each leading-zero scan step is charged 4.
- The final monic step is charged INV + 7·(n + 1).

euclid(n) = 10·n(n+1) + 8·2n + (INV + 20)·n + 4·2n + INV + 7(n+1) = **1,526,426,173,222** per trial. This is an upper bound for every
remainder sequence, so it does not depend on any property of the executed run.

### 5.4 One-time setup
| item | operations |
| --- | --- |
| MI = M^-1 by adjugate: determinant, 9 cofactors, one inversion, 9 scalings | 1,540 |
| K = (2^65 + RC_0[2])^5; D0, D1; C2 (one inversion); D0^5, D1^5, C2^5; A; B | 1,540 |
| e5 = (4(p−1) + 1)/5 by 256-bit long division with shifts/compares (≤ 256 iterations × 8) and the k-search mod 5 | 8,692 |
| Z of order 3·2^32: candidates 2, 3, 4, 5 (the first that works is 5), each one 221-bit and two ≤ 34-bit powers | 9,488 |
| primitive N-th roots ω_N = Z^(3·2^32/N) for every transform length used (≤ 40), ≤ 34-bit exponents | 11,680 |
| **setup** | **32,940** (= 2^7.00 target compressions; claimed preprocessing_log2 = 7, included in time) |

### 5.5 Total
| trial i | s0_i | SHA calls | deg h | charged trial total |
| --- | --- | --- | --- | --- |
| 0 | 14170770556788064952821125735403794677938040117312294831550240135846445405333 | 6 | 1 | 1,597,859,664,976 |
| 1 | 12716965322766905445027577449356050213734086104615833821016328675479559218172 | 7 | 1 | 1,597,859,684,984 |
| 2 | 19270957370833204487052246725688018379709187995537611376513784471566266721882 | 4 | 1 | 1,597,859,624,960 |
| 3 | 21331667664005937154925208940773753983817777652730315021744753943796086015003 | 5 | 3 | 1,597,859,746,298 |

Output mapping uses 3 fifth-root powers per input, each ≤ 2060, plus 200. Re-checking both digests costs 2C + 50 each. Together that is 13,892.

**W = setup + trials + output = 6,391,438,768,050.** T = W/C = 2.477302e+10, log2 T = 34.528051 ≤ **34.6**.

### 5.6 Memory (32-byte words)
Peak field words by phase (L = 786,432, L2 = 393,216, n = 390,625):

| phase | buffers | words |
| --- | --- | --- |
| interpolation | one L2 buffer (values → coefficients in place → g) | 393,216 |
| Newton | g (L2) + I (n) + two work buffers of the largest L_j | 2,356,705 |
| powering | Î (L) + ĝ (L2) + W (L) + a (n) | 2,356,705 |
| Euclid | U = g in its L2 buffer, V in a's n buffer (division in place) | 783,841 |

The peak is 2,356,705 words = 75,414,560 bytes. It is reached in the powering phase. Î, W and I are released before Euclid.

Itemized constants and scalars total ≤ 366 words = 11,712 bytes:
- all 64·3 round constants;
- M and MI;
- A and B;
- D0, D1, C2 and K;
- Z and e5;
- ≤ 40 roots of unity and ≤ 40 inverse scalars 1/N;
- 64 words of loop and recursion-free scalar state.

SHA-256 working state (8 words, 64 schedule words of 32 bits and a 64-byte block) uses ≤ 512 bytes.

The code is a fixed program with loops (SHA-256, the round function, three butterfly kernels, Barrett step, Newton, Euclid,
Tonelli–Shanks, square-and-multiply), with an allowance of 1 MiB:
- **with the 1 MiB allowance:** total ≤ 76,475,360 bytes = 2^26.1885;
- **with a 4 MiB allowance:** 79,621,088 bytes = 2^26.2466.

The claimed memory_log2_bytes = **26.3** covers both, so the bound does not depend on a tight code-size estimate.
There is no nonuniform advice: all constants are computed in the charged setup.

## 6. Success probability

The procedure uses no random coins. On the fixed target it halts at trial 3 with the certified collision, so its success probability
is 1. Its work is the finite charged budget W, which includes every executed trial. No restart or tail argument is needed.

Context only, not used for the claim: for r=2, trials 0..5 of this stream gave deg h = [1, 1, 1, 3, 1, 1], so 1 of 6 would succeed; every success produced a verified collision. The r=2 campaign was stopped after these trials to free compute.

## 7. Limitations and credits

- The time bound is an explicit operation count for the stated algorithm, not a wall-clock measurement. The executed run used FLINT for
  speed. The trial outcome depends only on uniquely defined objects (§2).
- Credits: Th0rgal's Orchard submissions introduced the univariate-slice gcd(g, X^p − X) root finding and the deterministic
  executed-outcome success argument. This submission follows both, and its Euclid bound has the same form as theirs. The new part is the
  two-round linearizing line (§1), which lowers the degree from about 5^(8+r) to 5^(6+r). Barrett and Newton reduction are textbook
  (von zur Gathen & Gerhard, *Modern Computer Algebra*, ch. 9).
