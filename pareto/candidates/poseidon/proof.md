# Orchard r=1: deterministic two-round-skip collision with polynomial root finding

Target: `poseidon-orchard-r1-prefix-v1`. The state is [nk, rho, 2^65] over Pallas, with full rounds 0–3, partial round(s) 4,
full rounds 60–63, and lane 0 as the digest. Cost model: `orchard-field-ram-v2`, C = 216 + 21·1 = 237.

## 0. Result

| quantity | value |
| --- | --- |
| algorithm | deterministic (no random coins); success probability **1** on the fixed target |
| executed outcome | trial 0 run and succeeded; collision in `certificates/` |
| total charged primitive operations W | 77,485,156,480 |
| normalized time T = W / C | 3.269416e+08 = 2^28.2845; **claimed time_log2 = 28.4** |
| memory | peak 569,645 words + itemized constants + code allowance (§5.5); **claimed memory_log2_bytes = 24.5**, which holds even with a 4 MiB code allowance |
| one-time setup | 46,868 operations (§5.4), included in W; preprocessing_log2 = 9 |
| projected cost axis | 28.4 + (24.5 − 20) = 32.90 |

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

Define f(s) as lane 0 after applying the remaining rounds (full rounds 2 and 3, partial round(s) 4, full rounds 60..63) to A + s·B. By
construction, f(s) = H(inputs(s^e5)) for every s ∈ F_p, where H is the r=1 digest.

**Lemma 2 (degree).** deg f ≤ 5^(6+1) = 78,125. Lanes of A + sB have degree ≤ 1. Constant addition and M do not raise the maximum
lane degree, and x^5 multiplies it by at most 5. The rounds 2 and 3, the 1 partial round(s) and the 4 final rounds give 5^(2+1+4).
Symbolic composition over F_p shows that the degree is exactly 78,125. Only the bound is used: with a smaller degree, the same
procedure runs with smaller n.

**Corollary.** For s0 ∈ F_p and g = f − f(s0), any root s1 ≠ s0 of g gives distinct canonical inputs inputs(s1^e5) ≠ inputs(s0^e5)
with equal digests. That is a collision.

## 2. The procedure (deterministic)

**Setup (once).** Compute MI, K, D0, D1, C2, A, B, e5, an element Z of order 3·2^32, and the roots of unity ω_N = Z^(3·2^32/N) for the
transform lengths used (§5.4).

**Stream.** s0_i is the first v = int_le(SHA-256(DOM ‖ le32(i) ‖ le32(ctr))), for ctr = 0, 1, …, with v < p. DOM =
`HashSmash-Orchard-r1-s0-v1`. The stream and its success rule were fixed and committed before any of its trials ran. Earlier
development used a separate test stream. This stream is the only one used for the claim.

For i = 0, 1, 2, …:
1. Compute s0 = s0_i.
2. **Interpolate f.** L2 = 98,304 ≥ n + 1. Evaluate f at ω^j (ω = ω_L2, j < L2) by the explicit round function from
   A + ω^j·B, storing each value at the digit-reversed position of j. One inverse NTT and scaling by 1/L2 give the coefficients of f.
   This is exact because deg f < L2.
3. c = f(s0) by one evaluation; g = (f − c)/lc(f), which is monic of degree n.
4. **Barrett data.** I = rev_n(g)^(-1) mod X^n by Newton doubling (§3.2). Store Î = NTT_L(I)/L with L = 196,608 ≥ 2n − 1, and ĝ = NTT_L2(g)/L2.
5. **Powering.** p = 2^254 + δ with δ < 2^126, so p >> 238 = 2^16, and 2^16 < n. Start with a = X^(2^16). For each of the
   remaining 238 bits b of p, from high to low, set a ← a²·X^b mod g (§3.1). The result is a = X^p mod g.
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
are [2, 6, 12, 24, 48, 96, 192, 384, 768, 1536, 3072, 6144, 12288, 24576, 49152, 98304, 196608].

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
h has degree 2: h = X² + h1·X + h0 with roots s0 and s1, so s1 = −h1 − s0.

## 4. Executed outcome (the certificate)

The procedure was executed on the fixed target with FLINT (python-flint 0.9.0) computing f, g, X^p mod g and gcd(g, X^p − X). The
uniquely defined objects of §2 do not depend on the implementation. Trial 0 has:

- s0 = 4766703137400488083754110162745305822677275183126808187356602193040276619021
- deg h = 2, roots ≠ s0: 13834604379169323874622223502465088293112971940967906188773023811204797909611
- s1 = 13834604379169323874622223502465088293112971940967906188773023811204797909611

A = inputs(s0^e5) = (nk, rho) = (10282377930700709955331863829808625809742269793488616908110496813216137010678, 9242264967822723892815813252653473580510300412200602754015911816695904633482)

B = inputs(s1^e5) = (9929006709084423418434499777465267004141677663080324177561129659131724493461, 23598064575810107403865759625209663882872134837538481415646749312217549501322)

The common digest (lane 0, 32-byte little-endian) is `82e3468ef09761522153585dbd4474552b2223900adf10f9835bfbff4facbe13`. Both pairs are canonical and distinct.
`certificates/message-a.bin` and `message-b.bin` are the 64-byte encodings nk ‖ rho, each 32-byte little-endian.

## 5. Cost accounting (orchard-field-ram-v2)

**Unit charges.** Each field add, subtract or multiply costs 1, as does each 256-bit load, store, compare, branch, shift or pointer
update. A simple loop iteration costs LOOP = 3 (increment, compare, branch). Per element:
- copy: 5
- zero-fill: 4
- scale or square (load, multiply, store): 6
- pointwise product or add/subtract (two loads, operation, store): 7

**Exponentiation.** Left-to-right square-and-multiply with a k-bit exponent is charged 8 per exponent bit:
- one squaring;
- one (conditional) multiplication, charged even when the bit is 0;
- a shift and a mask to extract the bit;
- a branch;
- loop increment, compare and branch.

That is 8k + 20 in total, with 20 for setup and return. An inversion is Fermat's a^(p−2) with a 255-bit exponent: INV = 8·255 + 20 = 2060.
This also covers the fifth root a^e5.

**NTT.** The forward transform is an in-place mixed-radix (4/2/3) decimation-in-frequency NTT, natural to digit-reversed order. The inverse is
its transposed decimation-in-time form, digit-reversed to natural order and unscaled. Pointwise products do not depend on the order.
Per butterfly, including loads, stores, address arithmetic and loop control:
- radix-4: 4 ld + 4 st + 4 mul (√−1 and three twiddles) + 8 add/sub + 6 = 26
- radix-2: 2 ld + 2 st + 1 mul + 2 add/sub + 4 = 11
- radix-3: 3 ld + 3 st + 3 mul (ζ₃ and two twiddles) + 7 add/sub + 5 = 21

Twiddles are generated incrementally per pass, with no table: 6, 4 or 5 operations per twiddle index (radix 4, 2 or 3).
T0(N) = Σ_passes (BF·N/f + TW·(twiddle indices)).

Each transform is also charged NTT_OVH = 7000 for its per-pass root powers: ≤ 11 passes, each with two powers of ≤ 21-bit
exponents (≤ 2·188), plus the one inversion of ω in the inverse transform (2,060). That totals ≤ 6,196 ≤ 7,000.

T(N) = T0(N) + 7000:
- T(196,608) = 12,000,087, radices [4, 4, 4, 4, 4, 4, 4, 4, 3]
- T(98,304) = 5,905,245, radices [4, 4, 4, 4, 4, 4, 4, 2, 3]

**Supporting check (not score-critical).** The butterfly implementation was checked against naive DFTs (lengths 2–1536, every radix
pattern) and as exact convolutions at lengths 98,304 and 196,608.

### 5.1 One powering step
| item | operations |
| --- | --- |
| copy a into W (n·5) and zero-pad to L ((L−n)·4) | 864,557 |
| forward transform, length L | 12,000,087 |
| pointwise square (L·6) | 1,179,648 |
| inverse transform, length L | 12,000,087 |
| scale 2n coefficients by 1/L, written at offset b (2n·6 + 1) | 937,501 |
| fold A' modulo X^L2 − 1 ((2n − L2)·7) | 405,622 |
| keep folded low n coefficients in a (n·5) | 390,625 |
| H = reversed top n coefficients into W, zero-pad to L (n·5 + (L−n)·4) | 864,557 |
| forward L, pointwise ·Î (L·7), inverse L | 25,376,430 |
| Q = reversed low n coefficients, zero-pad to L2 (n·5 + (L2−n)·4) | 471,341 |
| forward L2, pointwise ·ĝ (L2·7), inverse L2 | 12,498,618 |
| R = folded A' − Q·g on n coefficients (n·7) | 546,875 |
| **one step** | **67,535,948** |

There are 238 steps, costing 16,073,555,624.

### 5.2 Per-trial components (trial 0; trials differ only in the SHA count and the root step)
| component | operations |
| --- | --- |
| sha256 | 40,016 |
| f_interp | 56,412,797 |
| g_monic | 552,029 |
| newton | 126,912,634 |
| I_hat | 14,046,352 |
| g_hat | 6,497,129 |
| x_init | 312,501 |
| powering | 16,073,555,624 |
| g_recover | 5,905,245 |
| v | 7 |
| euclid | 61,200,861,442 |
| roots | 28 |

Formulas:
- **sha256:** (ctr + 1) compressions × (20000 + 8). 20,000 bounds one single-block SHA-256 (64 rounds of 32-bit operations plus message schedule).
- **f_interp:** L2·15 to generate ω^j and its digit-reversed index: mul, store and loop, plus 10 for the index. A mixed-radix
  reversed counter performs at most L2 digit carries over the whole count from 0 to L2 − 1 (Σ_k L2/(f_1⋯f_k) ≤ L2), each ≤ 5
  operations, plus ≤ 5 per step. Then add L2·(2C + 20) evaluations,
  plus T(L2) + (n + 1)·6 + INV.
  - One evaluation does 189 arithmetic operations: A + sB, then rounds 2, 3, the partial round(s) and 60–63.
  - It also does 90 constant loads: 12 per round, plus A and B.
  - That is 279 < 2C + 20 = 494.
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

euclid(n) = 10·n(n+1) + 8·2n + (INV + 20)·n + 4·2n + INV + 7(n+1) = **61,200,861,442** per trial. This is an upper bound for every
remainder sequence, so it does not depend on any property of the executed run.

### 5.4 One-time setup
| item | operations |
| --- | --- |
| MI = M^-1 by adjugate: determinant, 9 cofactors, one inversion, 9 scalings | 2,260 |
| K = (2^65 + RC_0[2])^5; D0, D1; C2 (one inversion); D0^5, D1^5, C2^5; A; B | 2,260 |
| e5 = (4(p−1) + 1)/5 by binary long division: 256 iterations × 20 (shift the remainder and bring in a bit, compare, conditional subtract, set a quotient bit, loop), ×4 for the k-search mod 5 | 20,980 |
| Z of order 3·2^32: candidates 2, 3, 4, 5 (the first that works is 5), each with one 221-bit and two ≤ 34-bit powers plus comparisons | 9,688 |
| primitive N-th roots ω_N = Z^(3·2^32/N) for every transform length used (≤ 40), ≤ 34-bit exponents | 11,680 |
| **setup** | **46,868** (= 2^7.63 target compressions; claimed preprocessing_log2 = 9, ≥ 0.5 bit slack; included in time) |

### 5.5 Total
| trial i | s0_i | SHA calls | deg h | charged trial total |
| --- | --- | --- | --- | --- |
| 0 | 4766703137400488083754110162745305822677275183126808187356602193040276619021 | 2 | 2 | 77,485,095,804 |

Output mapping uses 3 fifth-root powers per input, each ≤ 2060, plus 200. Re-checking both digests costs 2C + 50 each. Together that is 13,808.

**W = setup + trials + output = 77,485,156,480.** T = W/C = 3.269416e+08, log2 T = 28.284458. The claimed **28.4** leaves ≥ 0.1 bit (≥ 7%) of slack.

### 5.6 Memory (32-byte words)
Peak field words by phase (L = 196,608, L2 = 98,304, n = 78,125):

| phase | buffers | words |
| --- | --- | --- |
| interpolation | one L2 buffer (values → coefficients in place → g) | 98,304 |
| Newton | g (L2) + I (n) + two work buffers of the largest L_j | 569,645 |
| powering | Î (L) + ĝ (L2) + W (L) + a (n) | 569,645 |
| Euclid | U = g in its L2 buffer, V in a's n buffer (division in place) | 176,429 |

The peak is 569,645 words = 18,228,640 bytes. It is reached in the powering phase. Î, W and I are released before Euclid.

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
- **with the 1 MiB allowance:** total ≤ 19,289,440 bytes = 2^24.2013;
- **with a 4 MiB allowance:** 22,435,168 bytes = 2^24.4193.

The claimed memory_log2_bytes = **24.5** covers both, so the bound does not depend on a tight code-size estimate.
There is no nonuniform advice: all constants are computed in the charged setup.

## 6. Success probability

The procedure uses no random coins. On the fixed target it halts at trial 0 with the certified collision, so its success probability
is 1. Its work is the finite charged budget W, which includes every executed trial. No restart or tail argument is needed.

Context only, not used for the claim: for r=1, trials 0..119 of this stream gave deg h = [2, 1, 1, 3, 2, 1, 2, 4, 3, 1, 2, 2, 2, 1, 2, 2, 4, 1, 5, 4, 2, 2, 2, 3, 3, 4, 1, 1, 1, 1, 3, 2, 2, 1, 3, 1, 2, 2, 3, 1, 3, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 2, 3, 1, 2, 2, 1, 1, 1, 1, 1, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 3, 2, 3, 2, 3, 1, 1, 4, 5, 1, 1, 1, 1, 3, 2, 2, 1, 3, 4, 1, 2, 2, 4, 2, 1, 2, 1, 1, 1, 2, 2, 1, 1, 3, 1, 2, 3, 4, 1, 4, 2, 3, 2, 2, 1, 1, 2], so 74 of 120 would succeed; every success produced a verified collision.

## 7. Limitations and credits

- The time bound is an explicit operation count for the stated algorithm, not a wall-clock measurement. The executed run used FLINT for
  speed. The trial outcome depends only on uniquely defined objects (§2).
- Credits: Th0rgal's Orchard submissions introduced the univariate-slice gcd(g, X^p − X) root finding and the deterministic
  executed-outcome success argument. This submission follows both, and its Euclid bound has the same form as theirs. The new part is the
  two-round linearizing line (§1), which lowers the degree from about 5^(8+r) to 5^(6+r). Barrett and Newton reduction are textbook
  (von zur Gathen & Gerhard, *Modern Computer Algebra*, ch. 9).
