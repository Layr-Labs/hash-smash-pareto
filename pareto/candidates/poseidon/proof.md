# Orchard Poseidon, r = 1: parity collision on a two-round-skip line, two attempts

## 1. Target and result

Target `poseidon-orchard-r1-prefix-v1`, attack class ordinary collision, lane exploratory.
`digest(nk, rho) = permute((nk, rho, 2^65), 1)[0]` (reference `verifier/poseidon.py:digest`):
round indices 0, 1, 2, 3 (full), 4 (partial), 60, 61, 62, 63 (full). Round i adds RC[i],
applies x -> x^5 to all three coordinates (full) or to coordinate 0 (partial), then multiplies
by the deployed dense 3x3 MDS matrix M. The input is 64 bytes: two canonical 32-byte
little-endian field elements nk, rho < p. The output is the complete first coordinate.
Constants, MDS, capacity value 2^65 and output are unchanged.

| Quantity | Value |
|---|---|
| Total charged work, two attempts | 11 786 354 310 primitive operations |
| T = work / C(1), C(1) = 237 | 49 731 452.78 target-compressions |
| `time_log2` (exact / claimed) | 25.567655 / **25.58** |
| Peak memory | 8 044 800 bytes, log2 = 22.939625 |
| `memory_log2_bytes` (claimed) | **22.94** |
| Normalized cost 25.58 + max(0, 22.94 - 20) | **28.52** |
| Success probability (claimed) | **0.40** (>= 0.4327 under H1w; >= 0.6074 under H1p; >= 0.6318 under H1) |
| `preprocessing_log2`, `nonuniform_advice_log2_bytes` | 0, 0 (no separate category, Section 6.4) |
| Certificates | 16 verified r = 1 collisions, 5 or more per line (Section 11) |

`baseline_improved` is the organizer reference identifier. This package makes no claim to
improve on any qualified result. It claims only the bound above for the algorithm below.

## 2. Construction

Notation. p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001,
F = F_p. p - 1 = 2^32 * 3 * q' with q' odd and gcd(5, p - 1) = 1, so x -> x^5 is a
bijection of F with inverse x -> x^e5, e5 = 5^(-1) mod (p - 1). M^(-1) is the inverse MDS
matrix; a = (a_0, a_1, a_2) is its row 2 (0-based); all three are nonzero:
a_0 = 0x2fcbba6f9159a219723a63a0c09dab26aef9112e952fdbb52a418d8d73a7c908,
a_1 = 0x1ec7372574f3851bb4ddd4b4d6452256c5e4960d7424cd3776efab42d4fba90b,
a_2 = 0x0d0c2efd6472f12a3c26fa4b7d25b1e487a7435d30f8be81adc8933c6f3c72ee.

### 2.1 Round 0 and the reachable plane

Round 0 maps (nk, rho, 2^65) to the S-box output (u, v, K): u = (nk + RC[0][0])^5,
v = (rho + RC[0][1])^5, K = (2^65 + RC[0][2])^5 (a constant). (nk, rho) -> (u, v) is a
bijection of F^2. The round-1 S-box input is z = M (u, v, K)^T + RC[1]. As (nk, rho) ranges
over F^2, z ranges over the plane Pi = { z : a . (z - RC[1]) = K }, and every z in Pi has
exactly one preimage (nk, rho).

### 2.2 The line L_j and the map back

Fix j in {0, 1, 2} and let k0 < k1 be the other two indices. Put
mu_j = -a_k0 / a_k1 and c_j = (K + a_k0 RC[1][k0] + a_k1 RC[1][k1]) / a_j + RC[1][j].
For every s in F the point z(s) with z_j = c_j, z_k0 = s, z_k1 = mu_j s lies in Pi.
Round 1 is a full round, so its S-box output is (s^5, mu_j^5 s^5, c_j^5) at positions
(k0, k1, j). With w := s^5 this output is affine in w. After M and RC[2] the round-2 S-box
input is A_j + B_j w with B_j = M (e_k0 + mu_j^5 e_k1) and A_j = M (c_j^5 e_j) + RC[2].

Map back (w -> message): s = w^e5; z = z(s); (u, v, K)^T = M^(-1) (z - RC[1]);
nk = u^e5 - RC[0][0], rho = v^e5 - RC[0][1] (reduced mod p, hence canonical). Each step is
injective (w -> s is a bijection, s -> z(s) is injective because z_k0 = s, z -> (u, v) is
injective on Pi, (u, v) -> (nk, rho) is a bijection). So distinct w give distinct messages.
`inputs_from_s` and `affine_AB` (Appendix C.1) implement it; `affine_AB` checks affinity at a
third point for each j.

### 2.3 The univariate collision function

Let F_j(w) be the digest of the message mapped back from w. It equals output coordinate 0
after round indices 2, 3 (full), 4 (partial), 60-63 (full) applied to A_j + B_j w (round 2
adds no further constant; RC[2] is inside A_j). Each S-box layer multiplies the maximal
coordinate degree by 5: 5, 25 (rounds 2, 3), 125 (round 4 raises coordinate 0 to 125; the
MDS mixes it into all coordinates), then x 5^4 (rounds 60-63). So F_j is a polynomial of
degree at most D = 5^7 = 78 125. Exact degree D holds for every j: tracking (degree, leading
coefficient) through each layer, the leading sum is nonzero at every step (Appendix D), so
f_D != 0 (values in Section 2.5). The 900 runs agree (deg G = 78 125). D is odd.

### 2.4 Parity collisions

Fix a midpoint w0 in F and put G(h) = F_j(w0 + h) = sum_k g_k h^k (deg G = D, g_D = f_D).
Then G(h) - G(-h) = 2 h R(h^2) with

    R(y) = sum_{i=0}^{m} g_{2i+1} y^i,   m = (D - 1)/2 = 39 062,   deg R = m.

If y1 != 0 is a root of R and a square, y1 = h^2 with h != 0, then G(h) = G(-h), that is
F_j(w0 + h) = F_j(w0 - h), and w0 + h != w0 - h because p is odd. Define

    N(w0) = #{ y in F* : R_{w0}(y) = 0 and y is a square }   (distinct roots).

By Euler's criterion y^((p-1)/2) - 1 = prod over nonzero squares c of (y - c), a squarefree
polynomial. Hence g := gcd(R, Y - 1), with Y = y^((p-1)/2) mod R, is the product of (y - y_i)
over the distinct nonzero square roots y_i of R, and deg g = N(w0). The root y = 0 never
divides g (0^((p-1)/2) - 1 = -1).

### 2.5 Line constants (r = 1)

K = 0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c. Computed from the formulas of Section 2.2 (Appendix D).

j = 0 (k0 = 1, k1 = 2):
    mu  = 0x1120a68e20978faeab08bbfc217086a572b15c72a2a2cf045ded5872c7acffd7
    c   = 0x2a78890d8503b228bfa6bd9b312401c7af4e02a6376ceebb003ef1138f67c72c
    A[0] = 0x8b150eaa2fddc275bcb9c98b7787deaa5fb191064f6e678d00439b92e0bcf44
    A[1] = 0x7f9fbca63a66eb7a4b209de95f42e64c04297fc31fdfe5890cc4004ac78c3a5
    A[2] = 0x38d780df43c6a7489a58baea2c5232b91bc81187421195e772e86486533170e6
    B[0] = 0x1b98f5e7e046a44802a45c1799fff1de9be095b226d9c1c62370aa3f77742a4c
    B[1] = 0x2b841caabbc09b624af9842f7dc14e801d4dc71cd1ad0a1bccd2c6c7845b0fce
    B[2] = 0x2090099a84943bc37f000f8581b2375665b647d25ca1b16679e7930dd85a0e2e
    f_D  = 0x34d5ef2a23749e3b46d9289ff2726171551ccaf082d3a6cec73b63ebcf82e613

j = 1 (k0 = 0, k1 = 2):
    mu  = 0x37b4be86719df1fd43fbbe6bfc9db81a7e5049a5f90c0f49b4280f6334df8c0a
    c   = 0x56ca88352495e3b531f6639906f2a46f1123cf5ea8ca2ead4467a8cc69282fa
    A[0] = 0x379d74dfddcd5331a4ddfae80624857b53f24b3f780f6ea3d2c2aae56df92146
    A[1] = 0x3b2c8ec8c1bbc2ce939c2d473d3df52a368b36ffd829cb800259316bdac9c066
    A[2] = 0x9ca346ec33cfbe7da09b8d775e8c280a27bb87fedc100cfc3cce2d07b867a69
    B[0] = 0x35994a7837d9e3f3723e0248761443544c614ee9d4d04527565e02f6ee7b1f21
    B[1] = 0x3bf3be5c7daff3a549865476bea0ff678be18e06ce1c1e0d46435b312942e1c7
    B[2] = 0x12f605b60c3f87cbf0b0a18369d93aedccbc429f0b4bf54ed355e2f8a518398f
    f_D  = 0x21ddf354f88750a3a25e2d5b7bebdbcc418554419b3ad94c5e28405cde0458fb

j = 2 (k0 = 0, k1 = 1):
    mu  = 0x366c064e11b723c27198f3231eef4007d313b2c9cf936bf376889f3c40ba5534
    c   = 0x9b2d7e67acf680114704863d53135870423bf02a5b6414ddd79da0955bb7210
    A[0] = 0x25e5a2eaa09cea2b8ce5bf7dbc4f041c0ff623e000e6bc1b95f4ebeec6b43e03
    A[1] = 0x34ab8ed4e9bf805625da14ba5085f74d8a61aa18a8b04b0d3098124e83550b16
    A[2] = 0x232cb1957cbefa3cac4b57a2633f066cabc7a5a22e165793cad77e55c8685df0
    B[0] = 0x7424ce5970fab0c82eeb355a3a97b3c8d3da9fb9c971fb3afdda85400d3a9b1
    B[1] = 0x2bd9983ef41983168e7d1eae7a62fffceca9934d9724caf9c0c7c2c2822a3d5a
    B[2] = 0x1f370b04f75523a8c7b80ab1bdc195567cbb65a6fff3e5dc2c44764d0bc8103a
    f_D  = 0x1524e1d1e988e6162dcc14799e23a3570522f326892802bd9e4102bdf6ed703f

## 3. Algorithm

### 3.1 One attempt

Constants in the code: p, RC, M, M^(-1) row 2, e5, (p-1)/2, a primitive 2^32-th root of
unity. Transform lengths n = 81 920 = 2^16 + 2^14 and n2 = 40 960 = 2^15 + 2^13 (Section 7.1).

    ATTEMPT():
     1. Sample j uniform in {0,1,2} (2-bit words, reject 3) and w0 uniform in F (256-bit words
        masked to 255 bits, reject values >= p; acceptance >= 1/2); at most 128 tries each,
        failure probability <= 2^-128 + 2^-256 < 2^-127 in total.
        Compute mu_j, c_j, A_j, B_j (Section 2.2) and the twiddle tables.
     2. Interpolation. For each of the 81 920 roots h' of Q(h) = (h^65536 - 1)(h^16384 - zeta),
        zeta a primitive 8th root of unity, evaluate G(h') = F_j(w0 + h') from the affine state
        A_j + B_j (w0 + h'). One inverse transform modulo Q gives g_0, ..., g_81919
        (exact, because deg G = 78 125 < 81 920).
     3. R <- odd-index coefficients of G (Section 2.4); make R monic (one inversion).
     4. I <- rev_m(R)^(-1) mod y^m by Newton iteration; I~ <- rev_{m-1}(I);
        J <- T_n(I~)/n; RN <- T_n2(R)/n2. Release R (it is recoverable from RN).
     5. Exponentiation. Write (p-1)/2 = sum_{i=0}^{253} e_i 2^i (e_253 = 1). a <- y.
        For i = 252 down to 0: a <- y^(e_i) * a^2 mod R (one fused step, Section 7.2).
        Y <- a.
     6. R <- T_n2^(-1)(RN) (exact, deg R = m < n2); W <- Y - 1.
     7. g <- gcd(R, W) by half-gcd (Section 7.3), made monic. If a remainder step has a
        quotient of degree >= 2 (abnormal sequence, heuristic HG), return FAIL.
     8. If deg g = 0 or deg g > 12, return FAIL.
     9. Root extraction (equal-degree splitting). tries <- 0.
        While deg g > 1 and tries < 30: b <- random word masked to 254 bits; V <- (y + b)^((p-1)/2) mod g;
        g1 <- monic gcd(g, V - 1); if 0 < deg g1 < deg g, g <- the factor of smaller degree
        among g1 and g/g1; tries <- tries + 1.
        If deg g > 1, return FAIL. Else y1 <- -g(0).
    10. h <- square root of y1 (Tonelli-Shanks; y1 is a nonzero square, so h exists, h != 0).
    11. w1 <- w0 + h, w2 <- w0 - h. Map both back to messages m1, m2 (Section 2.2).
    12. Check digest(m1, 1) = digest(m2, 1) and m1 != m2 (two reference permutations).
        Return (m1, m2).

Every loop has a fixed upper bound, so one attempt has a fixed worst-case cost (Section 7).

### 3.2 Two attempts (the submitted algorithm)

    MAIN():
     for t in 1, 2:
         result <- ATTEMPT() with fresh independent random coins
         if result != FAIL: return result
     return FAIL

The charged budget is two complete attempts. Stopping after a first success only reduces
the actual work. Attempts run sequentially and reuse the same buffers, so peak memory is
the peak of one attempt.

## 4. Correctness

Each returned pair is a valid ordinary collision on the exact target:

1. Canonical inputs: nk and rho are computed and stored as reduced residues in [0, p) and
   encoded as 32-byte little-endian integers (64 bytes in total).
2. Distinct: h != 0 and p odd give w1 != w2, and the map back is injective (Section 2.2).
3. Equal digests: digest(m_i, 1) = F_j(w_i), and F_j(w0 + h) - F_j(w0 - h) = G(h) - G(-h)
   = 2 h R(h^2) = 2 h R(y1) = 0. Step 12 also checks the equality directly, so a returned
   pair is valid independently of the analysis.
4. Complete output: the equality is of the full first coordinate (one field element, all
   256 bits of its canonical encoding). No truncation, alias or free-start is used.

## 5. Success probability

### 5.1 Random experiment and success event

The coins of one attempt are j, w0 (uniform, independent), the shifts b of step 9 and the
rejection-sampling words. Attempt t succeeds on the event
S_t = {1 <= N(w0) <= 12} and {half-gcd sequence normal} and {step 9 isolates a root within
30 tries} and {sampling succeeds}. On S_t the attempt returns a valid collision (Section 4).
The two attempts use independent coins and have the same distribution, so with
P1 := Pr[S_t] the algorithm fails with probability (1 - P1)^2 and succeeds with
probability P = 1 - (1 - P1)^2. All bounds below hold for each fixed j in {0, 1, 2} (the
hypotheses are stated per j), hence also for j uniform.

### 5.2 Theorems used (exact forms)

- T1 (Bonferroni, pointwise). For every integer N >= 1 and K >= 1,
  sum_{k=1}^{K} (-1)^(k+1) C(N, k) = 1 - (-1)^K C(N - 1, K). Hence for even K and all N >= 0,
  1[N >= 1] >= sum_{k=1}^{K} (-1)^(k+1) C(N, k). We use K = 2 (1[N>=1] >= N - C(N,2)) and K = 4.
- T2 (Hasse-Weil). For a smooth projective geometrically irreducible curve W~ of genus g
  over F_p: |#W~(F_p) - (p + 1)| <= 2 g sqrt(p).
- T3 (Riemann-Hurwitz, tame). For a finite separable morphism phi: W~ -> P^1 of degree n from
  a smooth projective geometrically irreducible curve, with every ramification index prime
  to p: 2g - 2 = -2n + sum_P (e_P - 1). Over each point b of P^1, sum_{P over b} (e_P - 1)
  <= n - 1, and this sum is 0 unless b is a branch point.
- T4 (discriminant degree). If P(h) has degree d in h, a constant nonzero leading
  coefficient, and other coefficients in F[w0] of degree <= D, then disc_h(P) is a
  polynomial in w0 of degree <= (2d - 2) D (it is homogeneous of degree 2d - 2 in the
  coefficients).
- T5 (Jacobsthal). For y_a != y_b in F and chi the quadratic character,
  sum_{b in F} chi((b + y_a)(b + y_b)) = -1.

### 5.3 Factorial moments as point counts

For k >= 1 define the affine curve over F_p

    X_k = { (w0, h_1, ..., h_k) : R_{w0}(h_i^2) = 0, h_i != 0, h_i^2 != h_l^2 for i != l }.

For fixed w0 in F the fibre consists of ordered k-tuples of distinct nonzero square roots
y_i of R_{w0} and a sign choice for each h_i = +-sqrt(y_i). So the fibre has
2^k N(N-1)...(N-k+1) points, and

    S_k := E_{w0}[ C(N(w0), k) ] = #X_k(F_p) / (2^k k! p).

### 5.4 Error terms

Put P(h) = R_{w0}(h^2): degree 2m in h, constant leading coefficient f_D != 0, other
coefficients of degree <= D in w0. By T4, Delta(w0) := disc_h P has degree <= B := (4m - 2) D.
Delta = Delta_j is not the zero polynomial: at the certificate midpoint (j = 0, Section 11)
and at each of the 900 sampled w0 (all three j, Section 10), R_{w0} was squarefree with
R_{w0}(0) != 0, so P had distinct roots there (code: Appendix C.2). Outside the <= B zeros of
Delta, P has 2m distinct nonzero roots +-h_i, and X_k -> A^1 is etale of degree
n_k = prod_{i<k} (2m - 2i).

Lemma 1. Let c_k be the number of absolutely irreducible components of the Zariski closure
of X_k that are defined over F_p. Then

    | #X_k(F_p) - c_k p | <= E_k := (B + 1) n_k ceil(sqrt(p)) + (B + 2) n_k.

Proof. Let W_1, ..., W_t be the geometric components, of degrees d_i over A^1
(sum d_i = n_k), with smooth projective models W~_i -> P^1. These maps are unramified
outside the zeros of Delta and the point at infinity (<= B + 1 branch points). Every
e_P <= n_k <= n_4 < 2^66 < p, so T3 applies: g_i <= (B + 1) d_i / 2 and
sum g_i <= (B + 1) n_k / 2. Over each w0 in F that is not a branch point, X_k is smooth, so an
F_p-point lies on exactly one geometric component, which is then Frobenius-stable (defined
over F_p); there the F_p-points of X_k and of the c_k models W~_i defined over F_p coincide.
Over such a w0 the closure of X_k adds no points (X_k is finite and etale there, hence closed
in the fibre). A component defined over F_p is a geometric component, so it is geometrically
irreducible, as T2 requires.
Over the <= B + 1 branch points each side has at most n_k points. T2 for each of the c_k
components gives |#X_k(F_p) - c_k (p + 1)| <= 2 sqrt(p) sum g_i + (B + 1) n_k, and c_k <= n_k.

Appendix B evaluates log2(E_k / p) = -77.24, -60.99, -44.73, -28.48 for k = 1, 2, 3, 4.
Therefore S_k = (c_k + eps_k) / (2^k k!) with |eps_k| <= E_k / p, and c_k is an integer.
If X_k is absolutely irreducible, c_k = 1.

### 5.5 Per-attempt bound

Fix a line j and write c_1, c_2 for its integers of Lemma 1. T1 with K = 2 gives

    Pr[N >= 1] >= S_1 - S_2 >= (c_1 - 2^-77)/2 - (c_2 + 2^-60)/8.

The other terms of S_t:

- Pr[N >= 13] <= S_2 / C(13, 2) = S_2 / 78 (Markov on C(N, 2)).
- Step 9: for any two distinct roots y_a, y_b of the current g, a try splits g nontrivially
  when chi(y_a + b) != chi(y_b + b) with both nonzero. By T5 this holds for (p - 1)/2 values
  of b; b is uniform on [0, 2^254), at statistical distance < 2^-128 from uniform on F, so
  each try succeeds with probability >= (p - 1)/(2p) - 2^-128, independently of the past
  (fresh b). Each success at least halves deg g (keep the smaller factor: 12 -> 6 -> 3 -> 1),
  so 3 successes suffice for deg g <= 12. Pr[fewer than 3 successes in 30 tries] < 4.4e-7.
- Abnormal half-gcd step: <= m/p < 2^-238 under HG. Sampling failure (step 1): < 2^-127.

Bounds per line (Appendix B; each also subtracts the three small terms above):

| Hypothesis on line j | Pr[N >= 1] >= | Pr[N >= 13] <= | P1 >= |
|---|---|---|---|
| H1w: c_1 >= 1, c_2 <= 2 | 1/2 - 2/8 = 0.25 | 0.25/78 = 0.0032 | 0.246794 |
| H1p: c_1 = c_2 = 1 | 1/2 - 1/8 = 0.375 | 0.125/78 = 0.0016 | 0.373397 |
| H1: c_k = 1, k <= 4 (K = 4) | 151/384 - 2^-36 | S_4/715 <= 3.7e-6 | 0.393225 |

### 5.6 Two attempts and the claimed value

j is uniform and independent in each attempt, so P1 is the average of the per-line bounds
and P = 1 - (1 - P1)^2:

| Lines with c_2 = 2 (others c_2 = 1; c_1 >= 1 on all) | P1 >= | P >= |
|---|---|---|
| 0 (H1p on all lines) | 0.373397 | 0.607369 |
| 1 | 0.331196 | 0.552701 |
| 2 | 0.288995 | 0.494472 |
| 3 (H1w only) | 0.246794 | 0.432681 |

Under H1 on all lines P >= 0.631824. The claimed `success_probability` is **0.40**. It needs only H1w (P >= 0.432681): c_1 >= 1
and c_2 <= 2 on every line. P >= 0.40 needs P1 >= 0.2254, so the claim absorbs an additional
per-attempt loss (from HG or any other failure not modelled) of up to 0.0214 under H1w alone
and 0.148 under H1p. P >= 0.39 needs P1 >= 0.2190. The claim is independently supported by the
direct one-sided binomial bound of Section 5.7 (P >= 0.5503 at 99.9 %).

### 5.7 Empirical check (untrusted local evidence, Section 10)

900 complete single-midpoint runs at full size (r = 1, 300 per j) had 341 successes
(P1 = 0.3789). The success indicator is a bounded statistic, so exact binomial bounds apply
(given independent uniform midpoints). One-sided Clopper-Pearson lower bounds:
P1 >= 0.3521 (95 %), 0.3413 (99 %), 0.3294 (99.9 %), that is two-attempt P >= 0.5802,
0.5661, 0.5503. If P1 were 0.2254 (the value at which P = 0.40), 341 or more successes would
occur with probability 2.6e-25. These runs used the NTL implementation and the event N >= 1;
they are consistency evidence for the analysis, not organizer-verified execution.

## 6. Cost model and machine assumptions

### 6.1 Units

Model `orchard-field-ram-v2`. Each field addition, subtraction or multiplication, each
256-bit load or store, and each word operation (address/index arithmetic, comparison,
branch, one random 256-bit word) costs 1. The complete operation count is divided once by
C(1) = 216 + 21 = 237. Inversion and exponentiation are expanded into multiplications:

- inversion x^(p-2): straight-line addition chain, 254 squarings + 76 multiplications = 330,
  charged INV = 400 (70 for operand moves and a zero test);
- x^e5 (fifth root): 253 squarings + 124 multiplications = 377, charged 381;
- Tonelli-Shanks (2-adicity 32): <= 254 squarings + 127 multiplications, then <= 528
  squarings + 64 multiplications, + 200 loop operations: 1 173.

### 6.2 Machine

One sequential processor; total work equals the charged count (no parallel discount is
used). Register file: 32 registers of 256 bits (the 16 data words of a radix-16 butterfly,
a twiddle factor, the constants omega_16^k, zeta, temporaries). All other data is in RAM and
every RAM load and store is charged. Addresses: one index operation per element per pass
(the address serves both its load and its store) plus 4 per butterfly (loop counter, branch,
twiddle index). Loads and stores use base + offset addressing, so this index charge is an
upper bound. The reference C(1) = 237 itself charges no loads; the count below is stricter.

One evaluation of F_j in step 2 costs 6 (affine state) + 6 x 27 (full rounds 2, 3, 60-63:
9 multiplications for S-boxes, 9 multiplications and 6 additions for M, 3 constant
additions) + 21 (partial round 4) = 189 field operations, plus <= 36 loads of constants:
<= 225 <= 237. It is charged 237 = one target-compression unit.

### 6.3 Finite budget

Every phase has a fixed worst-case count (fixed exponent, degree-bounded half-gcd,
<= 30 splitting tries, <= 128 sampling tries, <= 32 Tonelli-Shanks iterations). The
charged budget is two complete attempts at worst-case cost. No expected-time argument is
used.

### 6.4 Preprocessing and advice

There is no input-independent precomputation reused across runs. Line constants, twiddle
tables, interpolation, the Newton inverse and the transform tables are computed inside
each attempt and are charged in `time_log2`. The code holds only the public target
definition (p, RC, M) and fixed exponents; it is charged in memory (Section 8). So the
`preprocessing_log2` and `nonuniform_advice_log2_bytes` categories are absent; the
nonnegative log fields record an absent category as 0 (log2 of the unit bound 1).

## 7. Operation count

Appendix A (`count_r1.py`) computes every number in this section from the formulas
stated here. m = 39 062, D = 78 125.

### 7.1 Transforms

Lengths: 2^a, 3 * 2^a, or n1 + n2 with n1 = 2^a, n2 = 2^b, b <= a - 2. For the last form,
products are computed modulo Q(y) = (y^n1 - 1)(y^n2 - zeta), zeta a primitive 2^(a-b+1)-th
root of unity (it exists because 2^32 | p - 1). zeta^(n1/n2) = -1, so the factors are coprime
and y^n1 = -1 mod (y^n2 - zeta). Forward: fold the input modulo both factors, twist
coefficient i by theta^i (theta^n2 = zeta), then NTT_n1 and NTT_n2. Inverse: inverse NTTs,
untwist, CRT x = x1 + (y^n1 - 1) c with c = (x2 - (x1 mod (y^n2 - zeta))) / (-2).
Any product of degree < n1 + n2 is exact. Used here: n = L(2m - 1) = 65 536 + 16 384 = 81 920
and n2 = L(m) = 32 768 + 8 192 = 40 960 (zeta of order 8 in both).

NTT_N: decimation in time, in place, radix-16 passes and one pass for the remaining bits.
Twiddles omega^j = T1[j mod 2^c] * T2[j div 2^c] from a two-level table (1 multiplication).
Per radix-2^s butterfly: multiplications (2^(s+1) - 2) + s 2^(s-1) - 2^s + 1 (twiddle powers,
twiddle application, internal stages without trivial factors), additions s 2^s, loads
2^s + 2, stores 2^s, index/loop 2^s + 4. Pointwise passes: one load per operand, one store,
one index operation per element, plus the arithmetic (5 per element for one product).

Forward transform of an input of l coefficients to length n1 + n2 (exact charges):
- part 1 (residue mod y^n1 - 1; copy, zero padding, fold): l loads, max(0, l - n1) additions,
  n1 stores, n1 + max(0, l - n1) index operations; then NTT_n1;
- part 2 (residue mod y^n2 - zeta, then twist by theta^i): l loads, max(0, l - n2)
  multiplications by zeta^t and as many additions, 2 n2 multiplications (theta^i generated
  and applied), n2 stores, n2 + max(0, l - n2) index operations; then NTT_n2.
Inverse transform (exact): NTT_n1^(-1), NTT_n2^(-1); untwist (2 n2 multiplications, n2
loads, n2 stores, n2 index); CRT: fold x1 mod (y^n2 - zeta) ((n1 - n2) multiplications by
zeta^t, n1 - n2 additions), c = (x2 - fold) * (-1/2) (n2 subtractions, n2 multiplications),
x_i <- x1_i - c_i for i < n2 (n2 subtractions); loads n1 + 4 n2, stores 3 n2, index n1 + 3 n2.
Pure lengths 2^a or 3 * 2^a have part 1 only and no CRT. Each formula charges every
arithmetic operation and memory access of the stated pass, so it is an upper bound.
Results: fwd_n(l = m) = 3 688 174, inv_n = 3 820 544, fwd_n2(l = m) = 1 913 370,
inv_n2 = 1 869 312.

### 7.2 Fused modular squaring step: a -> y^b a^2 mod R, b in {0, 1}, deg a < m

Tables (step 4): I = rev_m(R)^(-1) mod y^m, I~ = rev_{m-1}(I), J = T_n(I~)/n, RN = T_n2(R)/n2;
here "/n" means the inverse-transform scaling per part (1/n1 on the n1-part values, 1/n2 on
the n2-part values), so the unscaled inverse transforms in steps 5 and 6 return exact
coefficients. Step 2 applies the same per-part scaling in its pointwise pass (one more
multiplication per element, no extra load or store).

    1. X <- T_n(a)                                                    fwd_n(m)        3 688 174
    2. X <- (X o X) scaled per part; X <- T_n^(-1)(X) = A = a^2     6n + inv_n      4 312 064
    3. A' = y^b A (index offset only, deg <= 2m-1);
       E <- A' mod Q2 in the coefficient domain (folds mod both factors of Q2, CRT)   735 284
    4. X <- T_n(A'_hi), A'_hi = (A'_m, ..., A'_{2m-1})                fwd_n(m)        3 688 174
    5. X <- X o J; X <- T_n^(-1)(X); q <- coefficients m-1..2m-2      5n + inv_n      4 230 144
    6. X <- T_n2(q); X <- X o RN; X <- T_n2^(-1)(X) = qR mod Q2       fwd_n2(m) + 5 n2 + inv_n2
                                                                                      3 987 482
    7. remainder <- E - X (coefficient domain, m coefficients)       5m                195 310

Step 5 is the Barrett identity rev_{m-1}(q) = rev_{2m-1}(A') rev_m(R)^(-1) mod y^m for
q = floor(A'/R) (deg q <= m - 1); the product A'_hi I~ has degree <= 2m - 2 < n, so it is
exact. Steps 6-7: the inverse transform is linear, so E - X = (A' - qR) mod Q2, and
A' - qR has degree < m <= n2, so it equals its residue: the result is the exact remainder.
Bit b of the exponent costs nothing extra: y A only shifts the read offset in steps 3, 4.
Step 3 in detail (l = 2m, Q2 = (y^32768 - 1)(y^8192 - zeta2)): fold A' modulo each factor
(l loads per fold, l - 32768 additions; l - 8192 multiplications and additions), then the
CRT of the inverse transform without untwist; it is charged by the same formulas.
In-place data layout: step 4 writes its transform with the n2-part first (all sources lie
above their destinations, so an ascending copy is safe); step 5 then leaves q at positions
[55 445, 81 920) and [0, 12 587) of X; steps 6-7 work in the unused window [12 587, 53 547)
of X. J and RN are stored in the matching layouts. No buffer is added (Section 8).
Per step: 20 836 632 operations (mul 5 459 694, add 6 790 470, load 3 153 672, store
2 267 286, index 3 165 510). Exponentiation: 253 steps + 2 = 5 271 667 898.

### 7.3 gcd(R, W) by half-gcd

Notation: U(n, d) applies a 2x2 matrix to a pair of degree n when the results are known to
have degree <= d. It works modulo Q_L, L = L(d + 1) (exact because the results have degree
< L): 2 forward transforms of the operands (input length n + 1, folded by the transform),
4 forward transforms of the matrix entries (charged at input length L, an upper bound),
2 inverse transforms, 4L pointwise multiplications and 2L additions, L scaling
multiplications, each with its loads, stores and index operations. Buffers: FA, FM, ACC1,
ACC2.

HGCD(a, b), n = deg a > deg b, returns M with entries of degree <= n/2:
(i) M1 <- HGCD(top halves, degree ceil(n/2)); (ii) (a1, b1) <- M1 (a, b) by U(n, 3n/4 + 1);
(iii) one Euclid step with a degree-1 quotient (4n multiplications, 4n subtractions, 8n
loads, 4n stores, 4n index, 2 INV); (iv) M2 <- HGCD(top halves of the new pair);
(v) U(n, n/2 + 1); (vi) M = M2 E M1 by 8 forward (input length L) and 4 inverse transforms of
length L(2 ceil(n/4) + 1), 8L multiplications, 4L additions, L scalings.
Base case n <= 32: classical Euclid, ceil(n/2) steps, each charged INV + 18n + 4. At step i
the pair has degree <= n - i and the two updated matrix entries have <= i + 2 coefficients;
each coefficient costs 2 multiplications, 2 subtractions, 3 loads, 1 store, 1 index; the
quotient costs 4: 9(n - i) + 18(i + 2) + 4 <= 18n + 4 for n >= 6 and i < n/2.

    hgcd(n) = 2 hgcd(ceil(n/2)) + U(n, floor(3n/4) + 1) + U(n, ceil(n/2) + 1) + step(n) + MP(n)
    gcd(n)  = hgcd(n) + U(n, ceil(n/2) + 1) + step(n) + gcd(ceil(n/2)),
    gcd(n <= 32) = n (9n + 4 + INV).

Each step of the remainder sequence of (R, W) is executed once, at some level of the
recursion. The count charges (v), (vi) and a gcd-level update at every level although the
top-level call only needs the reduced pair (Section 8); these terms are an upper bound and
also cover making g monic (one inversion, <= 12 multiplications) and the degree test of step 8.
Total: gcd(39 062) = 530 220 628 operations (9.00 % of an attempt). Heuristic HG (all
quotients of degree 1) is used; an abnormal step ends the attempt with FAIL (Section 5.5).

### 7.4 All phases, one attempt

| Phase (step) | Formula | Operations |
|---|---|---|
| sampling, line constants, twiddle tables (1) | 4 INV + 3 x 1 088 + 1 536 | 6 400 |
| interpolation evaluations (2) | 81 920 x (237 + 4) | 19 742 720 |
| inverse transform + 1/N scaling (2) | inv_n + 5 x 81 920 | 4 230 144 |
| odd part, make monic (3) | 5 (m + 1) + INV | 195 715 |
| Newton inverse (4) | 4 M(m) + 6m, M(m) = 2 fwd_n(m) + inv_n + 2 x 5n | 48 298 740 |
| tables J, RN (4) | fwd_n(m) + 5n + fwd_n2(m + 1) + 5 n2 | 6 215 951 |
| exponentiation (5) | 253 x 20 836 632 + 2 | 5 271 667 898 |
| recover R, W = Y - 1 (6) | inv_n2 + 5 n2 + 4 | 2 074 116 |
| half-gcd (7) | Section 7.3 | 530 220 628 |
| root extraction (9) | 30 x (298 x 8 x 12^2 + 12 (9 x 12 + 4 + INV) + 8 x 12^2 + 100) | 10 520 760 |
| Tonelli-Shanks (10) | Section 6.1 | 1 173 |
| map back, 6 fifth roots (11) | 6 x 381 + 100 | 2 386 |
| verification (12) | 2 x 237 + 50 | 524 |
| **one attempt** | | **5 893 177 155** |

Notes. Step 1: 3 inversions (det M, a_k1, a_j), 1 088 table entries at 3 operations each,
<= 1 024 for sampling, <= 400 for the 2-power root of unity, one more
exponentiation (INV, <= 400) for a primitive cube root of unity (lengths 3 * 2^a), <= 112 for A_j, B_j. Newton: each
precision doubling t -> 2t uses two products of transform length at most that of size 2t;
the per-element NTT cost does not decrease with length, so the sum over t <= m is at most
4 M(m). Root extraction: per try 253 squarings and 45 multiplications by (y + b) modulo g
(deg g <= 12), each charged 8 x 12^2 (schoolbook product and reduction, <= 529 field
operations plus memory traffic); one classical gcd; one exact division; 100 for b.

### 7.5 Total and log2

    work = 2 x 5 893 177 155 = 11 786 354 310
    T = 11 786 354 310 / 237 = 49 731 452.78
    log2 T = 25.567655  ->  claimed time_log2 = 25.58 (rounded up; 25.57 would also cover it)

The exponentiation is 89.5 % of the work and the half-gcd 9.0 %. The claim exceeds the
count by 101.3 million operations (0.86 %).

## 8. Memory

32 bytes per field element. Phases run sequentially and reuse buffers; the second attempt
reuses the buffers of the first. Peak = maximum over phases.

| Exponentiation phase (step 5) | elements | bytes |
|---|---|---|
| J = T_n(I~)/n | 81 920 | 2 621 440 |
| RN = T_n2(R)/n2 (R itself is not stored) | 40 960 | 1 310 720 |
| X (working transform) | 81 920 | 2 621 440 |
| E (residue modulo Q2; holds a between steps) | 40 960 | 1 310 720 |
| twiddle tables (2 x 512) + zeta, theta powers (64) | 1 088 | 34 816 |
| scalars, constants, code (bound) | 2 048 | 65 536 |
| total | 248 896 | 7 964 672 |

| Half-gcd, top-level step (ii) (step 7) | elements | bytes |
|---|---|---|
| a = R, b = W | 78 126 | 2 500 032 |
| M1 (4 entries, degree <= m/4) | 39 066 | 1 250 112 |
| FA, FM, ACC1, ACC2 (L = 32 768) | 131 072 | 4 194 304 |
| tables, scalars, code | 3 136 | 100 352 |
| total (peak) | 251 400 | 8 044 800 |

Schedule of the half-gcd that attains this peak: the top-level call returns the reduced
pair (it needs no matrix), so R and W are released after (ii); (a1, b1) stay in ACC1, ACC2;
recursive calls read the top halves of the caller's pair in place and return matrices.
Appendix A evaluates the other stages with the recursive working-memory bound W(k). In the
terms for (i) and (iv) W(k) adds the data a level holds during its recursive call to the
callee's own bound, so simultaneously live levels are summed, not maximized:
top-level (i) 195 950, (iv) 183 360, (v) 189 658, Newton phase 245 100, tables phase
204 141, interpolation 124 119 elements (all including tables and code). Root extraction
and map back use fewer than 1 000 elements.

Peak 8 044 800 bytes, log2 = 22.939625, claimed `memory_log2_bytes` = 22.94.
Normalized cost (assignment rule: time_log2 + log2(M'), M' = max(1, memory / 1 MiB) in
fractional MiB without rounding; equivalently time_log2 + max(0, memory_log2_bytes - 20)):
25.58 + (22.94 - 20) = 28.52.

## 9. Heuristics

The cost (Sections 7, 8) uses no heuristic except HG. The claimed probability uses H1w;
H1p and H1 are stronger statements that give larger bounds.

**H1w (score-critical).** For each j in {0, 1, 2}: c_1 >= 1 and c_2 <= 2 (Lemma 1: c_k is the
number of absolutely irreducible components of X_k defined over F_p).
Consequence: P1 >= 0.246794 on every line and P >= 0.432681 (Sections 5.5-5.6).
Evidence. (a) c_1 >= 1, from a bounded statistic: if c_1 = 0 then Pr[N >= 1] <= E[N] < 2^-77
(Markov), and 300 uniform midpoints would show a success with probability < 2^-68; each line
had at least 105 successes in 300 runs. (b) c_2 <= 2: c_2 = 3 means E[C(N, 2)] = 0.375; the
observed values are 0.107, 0.140, 0.103 (j = 0, 1, 2), with one-sided 99.9 % Wald upper
bounds 0.181, 0.235, 0.173. (c) Independently of Lemma 1, the success indicator gives
exact one-sided bounds: P >= 0.5503 at 99.9 % (Section 5.7), above 0.40.
Scope: r = 1, all three j, exact degree m = 39 062, uniformly sampled midpoints.
Extrapolation: from 900 sampled midpoints to the average over all p midpoints, through the
integrality in Lemma 1 for (a)-(b) and directly for (c). No extrapolation in rounds or degree.
Limitations: (b) uses a Wald test on the unbounded statistic C(N, 2), which is not
conservative: an unobserved tail can carry the moment (for example mass 5.7e-4 at N = 30 adds
0.25 to E[C(N, 2)] and gives 0.17 expected hits in 300 runs). Route (c) has no such gap but
uses local, untrusted runs (NTL implementation, seeded pseudorandom midpoints, j = seed mod
3 stratified); no organizer experiment (Section 10.1).

**H1p (supporting).** For each j: c_1 = c_2 = 1, i.e. each of X_1 and X_2 (Section 5.3) has
exactly one absolutely irreducible component defined over F_p. This holds if X_1 and X_2 are
absolutely irreducible, equivalently if the geometric monodromy group of P(h) = R_{w0}(h^2)
over the algebraic closure of F_p(w0) is transitive on the 2m roots and on ordered pairs
(h_1, h_2) with h_2 != +-h_1; the full signed permutation group C_2 wr S_m has both
properties. Consequence: P >= 0.607369; with c_2 = 2 on one line 0.552701, on two lines
0.494472 (Section 5.6). Evidence: E[N] = 0.463 +- 0.039, 0.537 +- 0.042, 0.443 +- 0.039 and
E[C(N, 2)] = 0.107 +- 0.024, 0.140 +- 0.031, 0.103 +- 0.023 (j = 0, 1, 2; Section 10.3);
c_2 = 2 (0.25) is rejected by one-sided Wald tests with z = 5.9, 3.6, 6.5; reduced degree
D = 125 gives the same integers (Section 10.4). Limitations: the tail caveat of H1w (b)
applies (for example mass 2.9e-4 at N = 30 adds 0.125 with 0.09 expected hits in 300 runs);
six per-line tests. Not needed for the claimed 0.40.

**H1 (supporting).** c_k = 1 for k <= 4 and each j (implied by absolute irreducibility of
X_1, ..., X_4). Consequence: P1 >= 0.393225, P >= 0.6318. Not needed for the claim.
Evidence: as for H1p; also E[C(N, 3)] = 14/900 = 0.0156 (prediction 1/48 = 0.0208) and
E[C(N, 4)] = 1/900 (prediction 1/384 = 0.0026), small counts consistent with c_3 = c_4 = 1.
Limitations: the third and fourth moments are estimated from 11 and 1 events.

**H2 (supporting; exact computation).** deg F_j = D = 78 125 exactly (f_D != 0) for each j.
It fixes m and the transform lengths. Evidence: exact (degree, leading coefficient) tracking
with no cancellation at any layer (Appendix D, f_D in Section 2.5); every one of the 900 runs
computed deg G = 78 125 and deg R = 39 062. This is a deterministic computation, not a
statistical estimate. A lower degree would only reduce the work.

**HG (supporting).** The Euclidean remainder sequence of (R, W) is normal: every quotient
has degree 1. It is used for the half-gcd count (Section 7.3). An abnormal step ends the
attempt with FAIL and is charged to the failure probability (model: probability 1/p per
step, total <= m/p < 2^-238). Evidence (Section 10.5): classical Euclid on (R, Y - 1) for 30
new r = 1 midpoints (10 per line) ran 1 171 849 steps, all with degree-1 quotients.
Scope: r = 1, all three lines, 30 midpoints. Extrapolation: to the two random midpoints of
the attack. Limitations: seeded midpoints; local, untrusted runs; the Euclid steps use NTL
DivRem. Sensitivity: the 0.40 claim tolerates a per-attempt loss of 0.0214 under H1w alone
(0.148 under H1p).

**HS (supporting).** Root-extraction losses: Pr[N >= 13] <= 0.0032 (Markov on C(N, 2), under
H1w; 0.0016 under H1p) and splitting failure < 4.4e-7 (T5). These follow from H1w and T5;
they are listed so that every probability loss in Section 5.5 is visible. Evidence: the
largest observed N was 4 in 900 runs.

## 10. Local evidence (untrusted; not executed by the organizer)

### 10.1 Status

No experiment manifest is declared. The organizer executor (stdlib Python, 1 CPU, 128 MiB,
20 s) cannot run one full-size attempt. The results below come from local runs by the
submitter. They are reported data, not organizer-verified execution evidence. The 16
collision certificates (Section 11) are checked by the organizer verifier.

### 10.2 Implementation

Python driver and a C++ engine on NTL 11.6.0 (Appendix C). The engine computes G(h) =
F_j(w0 + h) by symbolic composition of the rounds from the affine state, R = odd part,
y^((p-1)/2) mod R (NTL PowerXMod), gcd(R, Y^2 - 1) and gcd with Y - 1 (NTL GCD), and the
roots (NTL FindRoots). The driver keeps the square roots, takes square roots, maps back and
verifies each pair with `verifier.poseidon.digest(m, 1)`. It also tests squarefreeness of R
and evaluates G at two random points against the reference digest (diagnostics only).
NTL uses its own multi-modular FFT arithmetic. It computes the same mathematical objects as
the priced algorithm (interpolation, NTT/Barrett exponentiation, half-gcd), so the runs
validate the construction and the probability, not the operation count or the memory.
Measured on one idle core (i7-13700HX): 15.5 s per attempt (polynomial 0.26 s, squarefree
test 1.25 s, exponentiation 12.72 s, gcd 1.29 s); peak RSS 74 MB (NTL representation and
process overhead; the priced buffers are in Section 8).

### 10.3 Full-size runs (r = 1, seeds 1..900, w0 = random.Random(seed).randrange(p), j = seed mod 3)

Design: seeds 1..900 were fixed before the run (300 per line, j = seed mod 3, stratified);
no adaptive stopping (one interim tally at 303 runs did not change the stopping point); all
900 runs are reported, with 0 errors. Tallies: `analyze.py` (Appendix C.4).

| | all | j = 0 | j = 1 | j = 2 |
|---|---|---|---|---|
| runs | 900 | 300 | 300 | 300 |
| success (N >= 1) | 341 (0.3789) | 111 (0.370) | 125 (0.417) | 105 (0.350) |
| 95 % Wilson | [0.3478, 0.4110] | [0.317, 0.426] | [0.362, 0.473] | [0.298, 0.406] |
| E[N] +- s.e. | 0.481 +- 0.023 | 0.463 +- 0.039 | 0.537 +- 0.042 | 0.443 +- 0.039 |
| E[C(N,2)] +- s.e. | 0.117 +- 0.015 | 0.107 +- 0.024 | 0.140 +- 0.031 | 0.103 +- 0.023 |

| N (nonzero square roots of R) | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| observed | 559 | 261 | 69 | 10 | 1 |
| 900 x Poisson(1/2) | 545.9 | 272.9 | 68.2 | 11.4 | 1.4 |

chi^2 = 1.14 (3 d.o.f., p = 0.77). All nonzero roots of R (squares and non-squares): mean
0.963, histogram 343/333/153/58/11/2 vs 900 x Poisson(1) 331.1/331.1/165.6/55.2/13.8/2.8
(chi^2 = 2.51, 4 d.o.f., p = 0.64). Anomalies: none (R squarefree with R(0) != 0 in all runs,
deg G = 78 125 in all runs, all evaluation cross-checks passed). Every square root gave a
verified collision: 433 collisions, 433 distinct pairs, re-verified with the reference
digest. Two-attempt estimate: P = 1 - (1 - 0.3789)^2 = 0.6142, interval [0.5746, 0.6531].

### 10.4 Reduced degree (E3)

Same field, constants and line (j = 0), function truncated after round indices 2, 3, 4
(D = 125, m = 62), 4 000 random midpoints: N histogram 2399/1249/296/47/8/1 vs
4000 x Poisson(1/2) 2426/1213/303/51/6/1 (chi^2 about 2.5, 4 d.o.f.); E[N] = 0.5048,
E[N(N-1)] = 0.2475. This is a shape check of the same mechanism at lower degree, not a
run of the target. A D = 625 run did not complete; no result is claimed for it.

### 10.5 Remainder-sequence check (HG)

30 new midpoints (seeds 2001..2030, 10 per line, same seeding as Section 10.3): classical
Euclid on (R, Y - 1) (Appendix C.5) ran to completion every time; 1 171 849 quotients in
total, all of degree 1, none of degree >= 2. deg R = 39 062 and deg(Y - 1) = 39 061 every
time. The final gcd degree equals N from the pipeline and the NTL half-gcd degree in all 30
cases (N = 0: 20, N = 1: 9, N = 2: 1; all 11 resulting collisions verified).

### 10.6 Out-of-target check (r = 2, supporting only)

The same mechanism at r = 2 (D = 390 625, a different target): 241 full runs, success
92/241 = 0.382 (95 % Wilson [0.323, 0.445]), mean N = 0.515 (Poisson(1/2) prediction 0.5).
This is not evidence for the r = 1 target; it only shows that the behaviour persists at a
five times larger degree.

## 11. Certificate

`certificates/manifest.json`. First certificate, id `r1-parity-collision`, from run seed 3 (j = 0):
w0 = 0x3cadc94f9a9a80fdea7b5bf55eb561a4216363698b529b4a97b750923ceb3ffd,
h  = 0x3a334d0c9fcbb8e0e61bb5c68ba457d836afbbf28c659f76de4390da32737fbb.

    m1: nk = 0x06b090731eae96d5aa9f1c316ea531ebf7f5faf09323c0e952b91247152f9a96
        rho = 0x322dfc8389b0024229aefaacf21195be810fe5b95023f98015dc0f46a0bfdbb6
    m2: nk = 0x3003e7a4e42e4b475f40b5e319fd5073daf073989d414dbca8f8a5c47a124c33
        rho = 0x36ac72421d16167ad1bcdacb87262f2a3e95895c8ed1fc6b20ee97e163e1d320
    digest(m1, 1) = digest(m2, 1) = 420b80f34695ccf6a5b97c1ad3d63d94bc44315abc1ef790dc10271f6088c025
                                    (32 little-endian bytes)

Both inputs are canonical (< p) and distinct. The digests differ for r = 0 and r = 2,
as expected.

All 16 certificates (5 more per line, from the smallest successful seeds of each line other
than seed 3) are listed below. For each, m1 and m2 are the map back (Section 2.2) of
w0 + h and w0 - h on line j; this was rechecked independently with the formulas of
Section 2.2 and the reference digest. The certificates show that the construction works on
all three lines; they are not evidence of the cost or of the success probability.

| id | j | seed | w0 | h |
|---|---|---|---|---|
| r1-parity-collision | 0 | 3 | 0x3cadc94f9a9a80fdea7b5bf55eb561a4216363698b529b4a97b750923ceb3ffd | 0x3a334d0c9fcbb8e0e61bb5c68ba457d836afbbf28c659f76de4390da32737fbb |
| r1-j0-s6 | 0 | 6 | 0x4b69b9b42f9a039c320a4737c2b3abe14a03569d26b949692e5dfe8cb1855fe | 0x34c3b5ecd2d520bf41888fde76ea634fc1f95162f1701cbc07a05d6e2d1a2c12 |
| r1-j0-s18 | 0 | 18 | 0x3f306f98d5f61954c18fd63fdf8d53b0e44a6fc9ad7785adcf7dd28333adb83c | 0x1384ae2775d67d5549a7b4490e608d8a011818a49b1f6332bcaf6de632ccaef5 |
| r1-j0-s24 | 0 | 24 | 0x156b0eaaff8f735c37e06c7b2ebe57949530fcd9d6fd1d9b62032801b65c1c28 | 0x35177d92e3048c6a5c98f06782dcd439e77891e2f2809056385624076240d090 |
| r1-j0-s27 | 0 | 27 | 0x9772969324779614935b675f501084146f7c9eab38cf45a7ad98a70a603e9e1 | 0x221f4d2c83737d766d263bf4fa632d35b59dcc554c0e7f5dd6a2bcd2d4d9f096 |
| r1-j0-s39 | 0 | 39 | 0x222dd49e4cbf8791949a68ae836bf80c644154acde0836d218dc13e4c0954361 | 0x6d9e282edc977e12b475695a14020e59d3799b24fe6a9d49ee8bf42b42a74ac |
| r1-j1-s10 | 1 | 10 | 0x3b35d68334c2da8003cc0f2793fdcab87b89296c6dcbac5008577eb1924770d3 | 0x1fd78cc30f394ea6a7f4dfa35f85fea28e386133a78277ad6bb903bd6dff3258 |
| r1-j1-s34 | 1 | 34 | 0x3d40ca4e60d93473ab434fed7e439fe07158ab795f381835b6913cd87684f34 | 0xe63a97c54931435f279af1c5cf472d433e5527762fe1d1ea9a6691cc0eba4e9 |
| r1-j1-s37 | 1 | 37 | 0x3807ed8e5e85d8b3fbd5a293a18bb42f0912b8e383d833a9a269d132d5a5167b | 0x323dffb00afae938d7dfebd92f289770354ab67240048bb9fa1d4cb574ce26f3 |
| r1-j1-s52 | 1 | 52 | 0x3843c1ea5899f364f71af8d72ee2d18cd49f93bd69b906e3cc798bc1fea9e9ff | 0x2758f0740f1ebe042456548fa399e83f5871b435d8c2c11f01e75efa030dd1bf |
| r1-j1-s55 | 1 | 55 | 0x26be7b9fbd47607bffb72cb3266480ae323d3ab0f35cb8a9fce5e9d717208331 | 0xd7d07ad98208bc732bac068cbb8b6672ee4b9f7b165b48a534e5102bec21ce6 |
| r1-j2-s5 | 2 | 5 | 0x2f96ecbf1cfb10f62827688de6a16a3b0d464138a62332553fc1ea36f17fd374 | 0x7e21a07ba4993a8acc03c0e0d5cdbfff05a96e69243425f966953afa41d1658 |
| r1-j2-s11 | 2 | 11 | 0x39d5a43b7734d7c1c7fde805ec99108ddb5b5fab8f4d3e27dda1494c73cf256d | 0x366f08d5443c9c0afa1bcc7ec11e9ffac18e296cfb4218cd90efc27adc50fa0a |
| r1-j2-s14 | 2 | 14 | 0x1f9b930bf0baef3a86f0ce2ea6ec39c1c15521b1b3dca50a9daa37e51b591d75 | 0x2ed907b15aa9ea735ca6c4c478b38ec0507f1e400041e3ccd3c7925d221a4da4 |
| r1-j2-s20 | 2 | 20 | 0x135ab1d8e794ee14e1454c40c439f34ac963cfe0afae5a3bb9096a04e7d80068 | 0x395352d14495eaf8f5273d6b930c79f9bdcf6d25e204213bc01a197a2b72e46d |
| r1-j2-s23 | 2 | 23 | 0x22f90ed156393d8d46375dce47682e64a37fa2df2d7d40fc7859faeecc3f80c | 0x8c8d8ae39aace3d5eef0e3d0424bba2999dd410711f87c96a1ffee723d4a322 |

## 12. Alternatives considered and rejected

- One midpoint: P1 >= 0.3932 needs H1 (k <= 4) with margin 0.003; two attempts cost
  +1.0 in time_log2 and reach 0.4327 under the much weaker H1w.
- Non-parity root search (roots of (F(w) - F(w0))/(w - w0), degree 2m): expected one
  root, but transforms of double length; about twice the cost of one parity attempt.
- Three-round skip (a further affine layer): needs two independent equations on fixed
  constants with no free parameter; it fails for all three j. Curves of degree d > 1 in
  the plane multiply the degree by d. So D = 5^7 is the minimum for this family.
- Avoiding the gcd (trace or Cayley-Hamilton tricks): each reduces to a modular
  composition or a bivariate resultant, not cheaper than half-gcd here.
- Several midpoints from one interpolation: the interpolation is 0.3 % of an attempt.
- Recomputing J in each step to save memory: +19 % time for -0.32 in memory log2; the net
  normalized gain is below 0.1. Classical Euclid: more work than the exponentiation.

## 13. Limitations

- The 0.40 success probability rests on H1w (Section 9; bound 0.4327). Its part c_2 <= 2 is supported by a
  moment test with a tail caveat; the direct binomial bound (Section 5.7) uses local,
  untrusted runs. Neither is a proof.
- The operation count is an explicit count for a specified algorithm in the stated machine
  model (Section 6.2); it was not measured on an implementation of that algorithm. The local
  implementation uses NTL and validates only the mathematics and probability.
- Code size is bounded by 64 KiB (2 048 elements in Section 8); this is an assumption on a
  compact implementation of the transforms, half-gcd and field arithmetic.
- The claim exceeds the count by 0.86 %; an omitted term larger than 101.3 million operations
  would raise time_log2 by 0.01.

## Appendix A. Operation-count and memory script (`count_r1.py`, Python 3 standard library)

Run `python3 count_r1.py`. Output is reproduced after the listing.

```python
#!/usr/bin/env python3
"""Operation count and memory, Orchard Poseidon r = 1, parity collision, TWO independent attempts.
Unit: field mul/add/sub, 256-bit load/store, index op, branch = 1 each. 32 bytes per field element."""
import math
p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
SQ = ((p - 1) // 2).bit_length() - 1      # 253 squaring steps of the exponent (p-1)/2
INV = 400                                 # one inversion: x^(p-2), 254 sq + 76 mul = 330, bounded by 400
R1, C, ATTEMPTS = 1, 237, 2
Dg = 5 ** (6 + R1); m = (Dg - 1) // 2     # D = 78125, m = 39062

def ntt_pow(n):                           # length 2^k or 3*2^k, radix-16 DIT passes
    c = dict(mul=0, add=0, load=0, store=0, idx=0); k, t = 0, n
    while t % 2 == 0: t //= 2; k += 1
    assert t in (1, 3); left = k
    while left > 0:
        s = min(4, left); left -= s; B = n >> s
        c['mul'] += B * ((2 << s) - 2 + s * (1 << (s - 1)) - (1 << s) + 1)
        c['add'] += B * (s << s); c['load'] += B * ((1 << s) + 2)
        c['store'] += B * (1 << s); c['idx'] += B * ((1 << s) + 4)
    if t == 3:
        G = n // 3; c['mul'] += 6*G; c['add'] += 6*G; c['load'] += 5*G; c['store'] += 3*G; c['idx'] += 7*G
    return c
def D(**k): d = dict(mul=0, add=0, load=0, store=0, idx=0); d.update(k); return d
def tot(d): return sum(d.values())
def add(*ds):
    o = D()
    for d in ds:
        for k in o: o[k] += d[k]
    return o
def sc(d, f): return {k: v * f for k, v in d.items()}
def vec(n, **k): return {kk: n * v for kk, v in D(**k).items()}
def ptw(n, nmul=1, nadd=0): return vec(n, mul=nmul, add=nadd, load=nmul + nadd + 1, store=1, idx=1)

LENGTHS = []
for a in range(4, 24):
    LENGTHS += [(1 << a, (1 << a, 0)), (3 << a, (3 << a, 0))]
    LENGTHS += [((1 << a) + (1 << b), (1 << a, 1 << b)) for b in range(2, a - 1)]
LENGTHS.sort()
def tr_len(x): return next((Lx, pr) for Lx, pr in LENGTHS if Lx >= x)
def L(x): return tr_len(x)[0]
def fwd(l, x):                            # forward transform of an input of l coefficients, length L(x)
    _, (n1, n2) = tr_len(x); e1 = max(0, l - n1)  # part 1: copy/fold mod y^n1 - 1, zero padding
    out = add(ntt_pow(n1), D(load=l, add=e1, store=n1, idx=n1 + e1))
    if n2:                                # part 2: fold mod y^n2 - zeta (zeta^t mults), twist (theta^i: 2 mults)
        e2 = max(0, l - n2)
        out = add(out, ntt_pow(n2), D(load=l, mul=e2 + 2*n2, add=e2, store=n2, idx=n2 + e2))
    return out
def crt(n1, n2):                          # c = (x2 - (x1 mod y^n2 - zeta)) / (-2); x_i -= c_i for i < n2
    return add(D(load=n1 + n2, mul=(n1 - n2) + n2, add=n1, store=n2, idx=n1 + n2),
               D(add=n2, load=2*n2, store=n2, idx=n2))
def inv(x):                               # inverse transform of length L(x), coefficient output
    _, (n1, n2) = tr_len(x)
    if not n2: return ntt_pow(n1)
    return add(ntt_pow(n1), ntt_pow(n2), D(mul=2*n2, load=n2, store=n2, idx=n2), crt(n1, n2))
def reduce_q(l, x):                       # coefficient-domain residue of l coefficients mod Q_L(x)
    _, (n1, n2) = tr_len(x)
    return add(D(load=l, add=l - n1, store=n1, idx=l), D(load=l, mul=l - n2, add=l - n2, store=n2, idx=l), crt(n1, n2))

n, n2 = L(2*m - 1), L(m)                  # 81920 = 65536 + 16384, 40960 = 32768 + 8192
SQ_STEPS = [('fwd_n(a)', fwd(m, 2*m - 1)), ('pointwise square, 1/n scaling', vec(n, mul=2, load=2, store=1, idx=1)), ('inv_n -> A', inv(2*m - 1)),
            ('E = y^b A mod Q2 (coefficients)', reduce_q(2*m, m)),
            ('fwd_n(A_hi)', fwd(m, 2*m - 1)), ('pointwise x J', ptw(n, 1)), ('inv_n -> q', inv(2*m - 1)),
            ('fwd_n2(q)', fwd(m, m)), ('pointwise x RN', ptw(n2, 1)), ('inv_n2 -> qR mod Q2', inv(m)),
            ('remainder = E - qR mod Q2', vec(m, add=1, load=2, store=1, idx=1))]
sq = add(*[s[1] for s in SQ_STEPS])

def update(nn, degout):                   # apply a 2x2 matrix to a pair of degree nn, results of degree <= degout
    Lx = L(degout + 1)
    return add(sc(fwd(nn + 1, degout + 1), 2), sc(fwd(Lx, degout + 1), 4), sc(inv(degout + 1), 2),
               ptw(Lx, 4, 2), vec(Lx, mul=1, load=1, store=1, idx=1))
def euclid_step(nn): return tot(vec(nn, mul=4, add=4, load=8, store=4, idx=4)) + 2*INV
_memo = {}
def hgcd(nn):
    if nn in _memo: return _memo[nn]
    if nn <= 32:                          # classical: ceil(nn/2) steps, each 1 inversion + pair + 2 matrix entries
        v = ((nn + 1) // 2) * (18*nn + 4 + INV)
    else:
        h, q = (nn + 1) // 2, (nn + 3) // 4; Lm = L(2*q + 1)
        matprod = add(sc(fwd(Lm, 2*q + 1), 8), sc(inv(2*q + 1), 4), ptw(Lm, 8, 4), vec(Lm, mul=1, load=1, store=1, idx=1))
        v = 2*hgcd(h) + tot(update(nn, 3*nn//4 + 1)) + tot(update(nn, h + 1)) + euclid_step(nn) + tot(matprod)
    _memo[nn] = v; return v
def gcd(nn):
    if nn <= 32: return nn * (9*nn + 4 + INV)
    h = (nn + 1) // 2
    return hgcd(nn) + tot(update(nn, h + 1)) + euclid_step(nn) + gcd(h)

Ni = L(Dg + 1)
DG, EDF_TRIES = 12, 30
rows = [
    ('sample j, w0; line constants; twiddle tables', 4*INV + 3*1088 + 1536),
    ('interpolation: %d evaluations x 1 unit + points' % Ni, Ni*C + tot(vec(Ni, mul=1, add=1, store=1, idx=1))),
    ('inverse transform + 1/N scaling', tot(inv(Dg + 1)) + tot(ptw(Ni, 1))),
    ('odd coefficients -> R, make monic', tot(vec(m + 1, mul=1, load=2, store=1, idx=1)) + INV),
    ('Newton inverse I mod y^m (<= 4 M(m))',
     4*tot(add(sc(fwd(m, 2*m - 1), 2), inv(2*m - 1), ptw(n, 1), ptw(n, 1))) + tot(vec(m, add=2, load=2, store=1, idx=1))),
    ('tables J = T_n(I~)/n, RN = T_n2(R)/n2', tot(fwd(m, 2*m - 1)) + tot(ptw(n, 1)) + tot(fwd(m + 1, m)) + tot(ptw(n2, 1))),
    ('exponentiation: %d fused square[-and-shift] steps' % SQ, SQ*tot(sq) + 2),
    ('recover R = T_n2^-1(RN), W = Y - 1', tot(inv(m)) + tot(ptw(n2, 1)) + 4),
    ('gcd(R, W): half-gcd, wraparound updates', gcd(m)),
    ('root of gcd: %d EDF tries, deg <= %d' % (EDF_TRIES, DG),
     EDF_TRIES * ((SQ + 45) * 8*DG*DG + DG*(9*DG + 4 + INV) + 8*DG*DG + 100)),
    ('Tonelli-Shanks square root', 381 + 528 + 64 + 200),
    ('6 fifth roots, affine maps', 6*381 + 100),
    ('verification: 2 permutations', 2*C + 50)]
per = sum(v for _, v in rows); total = ATTEMPTS * per; T = total / C
if __name__ == '__main__':
    print(f"r={R1} C={C} D={Dg} m={m} n={n} {tr_len(2*m-1)[1]} n2={n2} {tr_len(m)[1]} N_interp={Ni}")
    print(f"fwd_n(m) {tot(fwd(m, 2*m-1)):,}  inv_n {tot(inv(2*m-1)):,}  fwd_n2(m) {tot(fwd(m, m)):,}  inv_n2 {tot(inv(m)):,}")
    for name, d in SQ_STEPS: print(f"   {name:32s} {tot(d):>12,}")
    print(f"   per squaring step: {tot(sq):,} = {sq}")
    for name, v in rows: print(f"{name:52s} {v:>16,} {100*v/per:6.2f}%")
    print(f"per attempt {per:,}; attempts {ATTEMPTS}; TOTAL {total:,}")
    print(f"T = {T:,.2f}; log2 T = {math.log2(T):.6f}")
    tab = 2 * (1 << math.ceil(math.log2(n) / 2)) + 64
    L1 = L(3*m//4 + 2)
    me = 32 * (n + n2 + n + n2 + tab + 2048)
    mg = 32 * ((2*m + 2) + (m + 4) + 4*L1 + tab + 2048)
    def Wm(k):                            # working memory of a recursive (matrix) half-gcd on degree k
        if k <= 32: return 4*(k//2 + 2) + 2*(k + 1)
        h, La, Lv, Lm = (k+1)//2, L(3*k//4 + 2), L((k+1)//2 + 2), L(2*((k+3)//4) + 1)
        return max(Wm(h), (k+4) + 4*La, (k+4) + 2*La + Wm(h), (k+4) + 2*La + (k+4) + 4*Lv, 8*Lm + 2*La)
    h = (m+1)//2; Lv = L(h + 2); extra = tab + 2048
    stages = {'top (i)': 2*m + 2 + Wm(h), 'top (ii)': 2*m + 2 + (m + 4) + 4*L1, 'top (iv)': 2*L1 + Wm(h),
              'top (v)': 2*L1 + (m + 4) + 4*Lv, 'Newton': 2*n + 2*m, 'tables': (m + 1) + m + n + n2,
              'interpolation': Ni + (m + 1)}
    print("gcd/other stages (elements incl. tables+code):", {k: v + extra for k, v in stages.items()})
    mem = max(me, mg, 32*(max(stages.values()) + extra)); lm = math.log2(mem)
    print(f"memory: exponentiation {me:,} B, gcd {mg:,} B, peak {mem:,} B, log2 {lm:.6f}")
    print(f"normalized = {math.log2(T):.6f} + {max(0, lm - 20):.6f} = {math.log2(T) + max(0, lm - 20):.6f}")
    print(f"claimed 25.58 + 22.94 - 20 = {25.58 + 22.94 - 20:.2f}; slack ops {2**25.58*C - total:,.0f}")
```

Output:

```text
r=1 C=237 D=78125 m=39062 n=81920 (65536, 16384) n2=40960 (32768, 8192) N_interp=81920
fwd_n(m) 3,688,174  inv_n 3,820,544  fwd_n2(m) 1,913,370  inv_n2 1,869,312
   fwd_n(a)                            3,688,174
   pointwise square, 1/n scaling         491,520
   inv_n -> A                          3,820,544
   E = y^b A mod Q2 (coefficients)       735,284
   fwd_n(A_hi)                         3,688,174
   pointwise x J                         409,600
   inv_n -> q                          3,820,544
   fwd_n2(q)                           1,913,370
   pointwise x RN                        204,800
   inv_n2 -> qR mod Q2                 1,869,312
   remainder = E - qR mod Q2             195,310
   per squaring step: 20,836,632 = {'mul': 5459694, 'add': 6790470, 'load': 3153672, 'store': 2267286, 'idx': 3165510}
sample j, w0; line constants; twiddle tables                    6,400   0.00%
interpolation: 81920 evaluations x 1 unit + points         19,742,720   0.34%
inverse transform + 1/N scaling                             4,230,144   0.07%
odd coefficients -> R, make monic                             195,715   0.00%
Newton inverse I mod y^m (<= 4 M(m))                       48,298,740   0.82%
tables J = T_n(I~)/n, RN = T_n2(R)/n2                       6,215,951   0.11%
exponentiation: 253 fused square[-and-shift] steps      5,271,667,898  89.45%
recover R = T_n2^-1(RN), W = Y - 1                          2,074,116   0.04%
gcd(R, W): half-gcd, wraparound updates                   530,220,628   9.00%
root of gcd: 30 EDF tries, deg <= 12                       10,520,760   0.18%
Tonelli-Shanks square root                                      1,173   0.00%
6 fifth roots, affine maps                                      2,386   0.00%
verification: 2 permutations                                      524   0.00%
per attempt 5,893,177,155; attempts 2; TOTAL 11,786,354,310
T = 49,731,452.78; log2 T = 25.567655
gcd/other stages (elements incl. tables+code): {'top (i)': 195950, 'top (ii)': 251400, 'top (iv)': 183360, 'top (v)': 189658, 'Newton': 245100, 'tables': 204141, 'interpolation': 124119}
memory: exponentiation 7,964,672 B, gcd 8,044,800 B, peak 8,044,800 B, log2 22.939625
normalized = 25.567655 + 2.939625 = 28.507280
claimed 25.58 + 22.94 - 20 = 28.52; slack ops 101,285,429
```

## Appendix B. Probability script (`prob_r1.py`)

```python
#!/usr/bin/env python3
"""Error terms E_k (Lemma 1), success bounds (Section 5) and one-sided bounds (Section 10), r = 1."""
from fractions import Fraction as Fr
from math import comb, factorial, log2, isqrt, lgamma, log, exp
p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
D = 5**7; m = (D - 1)//2; B = (4*m - 2)*D           # finite branch points of X_k -> A^1
E, n = {}, {}
for k in range(1, 5):
    n[k] = 1
    for i in range(k): n[k] *= 2*m - 2*i
    E[k] = (B + 1)*n[k]*(isqrt(p) + 1) + (B + 2)*n[k]  # |#X_k(F_p) - c_k p| <= E_k
    print(f"k={k}: n_k = 2^{log2(n[k]):.2f}, log2(E_k/p) = {log2(E[k]/p):.2f}")
def S(k, c, sign): return (c + sign*Fr(E[k], p)) / (2**k * factorial(k))   # S_k = (c_k + eps_k)/(2^k k!)
split_fail = Fr(1 + 30 + 435, 2**30) * Fr(p + 1, p)**30  # P(Bin(30, (p-1)/2p) <= 2), upper bound
other = split_fail + Fr(m, p) + Fr(1, 2**127)         # splitting, abnormal half-gcd (HG), sampling
def P1_K2(c2): return S(1, 1, -1) - S(2, c2, +1) - S(2, c2, +1)/comb(13, 2) - other   # c_1 >= 1, c_2 given
P1_h1 = S(1, 1, -1) - S(2, 1, +1) + S(3, 1, -1) - S(4, 1, +1) - S(4, 1, +1)/comb(13, 4) - other
two = lambda q: 1 - (1 - q)**2
for name, q in [("H1w (c1 >= 1, c2 <= 2), K = 2", P1_K2(2)), ("H1p (c1 = c2 = 1), K = 2", P1_K2(1)),
                ("H1 (c_k = 1, k <= 4), K = 4", P1_h1)]:
    print(f"{name}: P1 >= {float(q):.6f}; two attempts P >= {float(two(q)):.6f}")
for bad in range(4):                                  # j uniform: per-attempt bound is the average over lines
    q = (bad*P1_K2(2) + (3 - bad)*P1_K2(1)) / 3
    print(f"c2 = 2 on {bad} line(s), c2 = 1 elsewhere: P1 >= {float(q):.6f}, P >= {float(two(q)):.6f}")
need = 1 - 0.6**0.5                                   # per-attempt success needed for P >= 0.40
print(f"P1 needed: {need:.4f} for P >= 0.40, {1 - 0.61**0.5:.4f} for P >= 0.39")
print(f"tolerance of the 0.40 claim (per-attempt loss): {float(P1_K2(2)) - need:.4f} under H1w, {float(P1_K2(1)) - need:.4f} under H1p")
def binom_sf(k, N, q):                                # P(Bin(N, q) >= k), exact sum in log space
    return sum(exp(lgamma(N + 1) - lgamma(i + 1) - lgamma(N - i + 1) + i*log(q) + (N - i)*log(1 - q)) for i in range(k, N + 1))
def cp_lower(k, N, alpha):                            # one-sided Clopper-Pearson lower bound
    lo, hi = 0.0, k / N
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if binom_sf(k, N, mid) < alpha else (lo, mid)
    return lo
for conf in (0.95, 0.99, 0.999):
    q = cp_lower(341, 900, 1 - conf)
    print(f"one-sided {conf:.3f} Clopper-Pearson: P1 >= {q:.4f}, two attempts P >= {two(q):.4f}")
print(f"P(Bin(900, {need:.4f}) >= 341) = {binom_sf(341, 900, need):.2e}")
```

Output:

```text
k=1: n_k = 2^16.25, log2(E_k/p) = -77.24
k=2: n_k = 2^32.51, log2(E_k/p) = -60.99
k=3: n_k = 2^48.76, log2(E_k/p) = -44.73
k=4: n_k = 2^65.01, log2(E_k/p) = -28.48
H1w (c1 >= 1, c2 <= 2), K = 2: P1 >= 0.246794; two attempts P >= 0.432681
H1p (c1 = c2 = 1), K = 2: P1 >= 0.373397; two attempts P >= 0.607369
H1 (c_k = 1, k <= 4), K = 4: P1 >= 0.393225; two attempts P >= 0.631824
c2 = 2 on 0 line(s), c2 = 1 elsewhere: P1 >= 0.373397, P >= 0.607369
c2 = 2 on 1 line(s), c2 = 1 elsewhere: P1 >= 0.331196, P >= 0.552701
c2 = 2 on 2 line(s), c2 = 1 elsewhere: P1 >= 0.288995, P >= 0.494472
c2 = 2 on 3 line(s), c2 = 1 elsewhere: P1 >= 0.246794, P >= 0.432681
P1 needed: 0.2254 for P >= 0.40, 0.2190 for P >= 0.39
tolerance of the 0.40 claim (per-attempt loss): 0.0214 under H1w, 0.1480 under H1p
one-sided 0.950 Clopper-Pearson: P1 >= 0.3521, two attempts P >= 0.5802
one-sided 0.990 Clopper-Pearson: P1 >= 0.3413, two attempts P >= 0.5661
one-sided 0.999 Clopper-Pearson: P1 >= 0.3294, two attempts P >= 0.5503
P(Bin(900, 0.2254) >= 341) = 2.60e-25
```

## Appendix C. Essential code of the local implementation

This is the NTL-based implementation used for Section 10, not the priced algorithm of
Sections 3 and 7. It computes the same mathematical objects. Excerpts, unchanged except
that blank lines, the module docstring and diagnostic output are removed; the repository
path in `sys.path` is the local organizer checkout.

### C.1 Line construction and map back (`poseidon_line.py`; same as `check_skip2.py`)

```python
import sys
sys.path.insert(0, '/home/di/hashsmash/hashsmash-pareto')
from verifier.poseidon import digest, parameters, P  # noqa: E402
RC, MDS = parameters()
INV5 = pow(5, -1, P - 1)
def matinv(m):
    a, b, c = m[0]; d, e, f = m[1]; g, h, i = m[2]
    det = (a*(e*i-f*h) - b*(d*i-f*g) + c*(d*h-e*g)) % P
    di = pow(det, -1, P)
    adj = [[e*i-f*h, c*h-b*i, b*f-c*e], [f*g-d*i, a*i-c*g, c*d-a*f], [d*h-e*g, b*g-a*h, a*e-b*d]]
    return [[x * di % P for x in row] for row in adj]
MINV = matinv(MDS)
K = pow((1 << 65) + RC[0][2], 5, P)          # round-0 S-box output, coordinate 2
def inputs_from_s(s, j):
    """Copied from work/check_skip2.py: round-1 S-box input z with z[j] constant,
    the other two coordinates (s, mu*s); returns the message (nk, rho)."""
    a = MINV[2]
    others = [k for k in range(3) if k != j]
    k0, k1 = others
    mu = (-a[k0] * pow(a[k1], -1, P)) % P
    rc = RC[1]
    c = ((K + a[k0]*rc[k0] + a[k1]*rc[k1]) * pow(a[j], -1, P) + rc[j]) % P
    z = [0, 0, 0]
    z[k0], z[k1], z[j] = s % P, mu * s % P, c
    x = [sum(MINV[r][t] * (z[t] - rc[t]) for t in range(3)) % P for r in range(3)]
    assert x[2] == K, 'plane constraint failed'
    nk = (pow(x[0], INV5, P) - RC[0][0]) % P
    rho = (pow(x[1], INV5, P) - RC[0][1]) % P
    return nk, rho
def round2_input(nk, rho):
    """State after rounds 0, 1 and the addition of RC[2] (round-2 S-box input)."""
    st = [nk, rho, 1 << 65]
    for idx in (0, 1):
        st = [(x + c) % P for x, c in zip(st, RC[idx])]
        st = [pow(x, 5, P) for x in st]
        st = [sum(m * x for m, x in zip(row, st)) % P for row in MDS]
    return [(x + c) % P for x, c in zip(st, RC[2])]
def message_from_w(w, j):
    s = pow(w, INV5, P)
    return inputs_from_s(s, j)
def encode(nk, rho):
    return nk.to_bytes(32, 'little') + rho.to_bytes(32, 'little')
def affine_AB(j):
    """Round-2 S-box input as A + B*w, derived from two points on the line and
    checked at a third point (fixed s values, deterministic)."""
    pts = []
    for s in (2, 3, 7):
        w = pow(s, 5, P)
        pts.append((w, round2_input(*inputs_from_s(s, j))))
    (w1, y1), (w2, y2), (w3, y3) = pts
    inv = pow(w2 - w1, -1, P)
    B = [(y2[i] - y1[i]) * inv % P for i in range(3)]
    A = [(y1[i] - B[i] * w1) % P for i in range(3)]
    assert all((A[i] + B[i] * w3 - y3[i]) % P == 0 for i in range(3)), 'not affine in w'
    return A, B
def schedule(r):
    """Rounds after the round-2 S-box input: (round index, full?, add RC?)."""
    out = [(2, True, False), (3, True, True)]
    out += [(i, False, True) for i in range(4, 4 + r)]
    out += [(i, True, True) for i in range(60, 64)]
    return out
def F_fast(w, j, r, AB=None):
    A, B = AB if AB is not None else affine_AB(j)
    st = [(A[i] + B[i] * w) % P for i in range(3)]
    for idx, full, addrc in schedule(r):
        if addrc:
            st = [(x + c) % P for x, c in zip(st, RC[idx])]
        for col in (range(3) if full else range(1)):
            st[col] = pow(st[col], 5, P)
        st = [sum(m * x for m, x in zip(row, st)) % P for row in MDS]
    return st[0]
```

### C.2 Engine core (`trial_ntl.cpp`, NTL 11.6.0): G, R, Y, gcd, roots

Input: p; the affine state A_j + B_j w0 and B_j; the round schedule of `schedule(1)`; M.

```cpp
static void pow5(ZZ_pX &x)
{
    ZZ_pX x2, x4;
    sqr(x2, x);
    sqr(x4, x2);
    mul(x, x4, x);
}
    for (int i = 0; i < 3; i++) { SetCoeff(S[i], 0, a[i]); SetCoeff(S[i], 1, b[i]); }
    for (long k = 0; k < nr; k++) {
        if (addrc[k])
            for (int i = 0; i < 3; i++) S[i] += rc[3 * k + i];
        for (int i = 0; i < (full[k] ? 3 : 1); i++) pow5(S[i]);
        int rows = (k == nr - 1) ? 1 : 3;     // last round: only output coordinate 0
        ZZ_pX T[3], u;
        for (int i = 0; i < rows; i++) {
            for (int t = 0; t < 3; t++) { mul(u, S[t], M[i][t]); T[i] += u; }
        }
        for (int i = 0; i < rows; i++) S[i] = T[i];
    }
    ZZ_pX G = S[0];
    for (int i = 1; i < 3; i++) S[i].kill();
    long D = deg(G);
    ZZ_pX R;
    long n = (D - 1) / 2;
    R.SetLength(n + 1);
    for (long k = 0; k <= n; k++) R[k] = coeff(G, 2 * k + 1);
    R.normalize();
    G.kill();
    int r0zero = IsZero(coeff(R, 0));             // R(0) = 0 would put the root y = 0 in P
    MakeMonic(R);
    ZZ_pX dR, sq;                                 // squarefree test (diagnostic): deg gcd(R, R') = 0
    diff(dR, R);
    GCD(sq, R, dR);
    ZZ e = (p - 1) / 2;
    ZZ_pXModulus F(R);
    ZZ_pX g, g2;
    PowerXMod(g, e, F);
    SqrMod(g2, g, F);
    g2 -= 1;
    ZZ_pX Qall, Q;
    GCD(Qall, R, g2);
    long nroots = deg(Qall);
    Q = Qall;
    if (nroots > 0) {
        ZZ_pX gq;
        rem(gq, g, Qall);
        gq -= 1;
        GCD(Q, Qall, gq);
    }
    if (nroots > 0) {
        vec_ZZ_p roots;
        FindRoots(roots, Qall);
    }
```

(The engine prints every root of `Qall`; the driver keeps the squares. `deg(Q)` equals N.)

### C.3 Driver: from roots to verified collisions (`trial.py`)

```python
def run_trial(r, seed):
    rng = random.Random(seed)
    w0 = rng.randrange(P)
    j = seed % 3
    checks = [rng.randrange(P) for _ in range(2)]
    AB = get_AB(j)
    # e <- parsed output of trial_ntl on engine_input(w0, j, r, checks, AB); e['roots'] = roots of Qall
    square_roots, collisions = [], []
    for z in sorted(e['roots']):
        h = sqrt_mod(z)
        if h is None:
            continue
        square_roots.append(z)
        w1, w2 = (w0 + h) % P, (w0 - h) % P
        m1, m2 = message_from_w(w1, j), message_from_w(w2, j)
        d1, d2 = digest(encode(*m1), r), digest(encode(*m2), r)
        if d1 == d2 and m1 != m2:
            collisions.append({'z': hex(z), 'h': hex(h), 'w1': hex(w1), 'w2': hex(w2),
                               'nk_a': hex(m1[0]), 'rho_a': hex(m1[1]),
                               'nk_b': hex(m2[0]), 'rho_b': hex(m2[1]),
                               'digest_bytes_le': d1.hex(),
                               'digest_field': hex(int.from_bytes(d1, 'little'))})
        else:
            anomalies.append(f'square root z={hex(z)} did not verify')
```

### C.4 Tally of the 900 runs (`analyze.py`, excerpt of `summarize`)

```python
def summarize(path):
    recs = [json.loads(l) for l in open(path)]
    errors = [r for r in recs if 'error' in r]
    recs = sorted((r for r in recs if 'error' not in r), key=lambda r: r['seed'])
    n = len(recs)
    succ = sum(1 for r in recs if r['n_collisions'] > 0)
    lo, hi = wilson(succ, n)
    out['per_j'] = {}
    for j in range(3):
        sub = [r for r in recs if r['j'] == j]
        sj = sum(1 for r in sub if r['n_collisions'] > 0)
        out['per_j'][j] = {'n': len(sub), 'successes': sj, 'rate': sj / len(sub) if sub else None,
                           'wilson95': wilson(sj, len(sub))}
    nroots = [r['n_roots_nonzero'] for r in recs]
    nsq = [r['n_square_roots'] for r in recs]
    out['anomalies'] = {
        'non_squarefree': sum(1 for r in recs if not r['squarefree']),
        'R0_zero': sum(1 for r in recs if r['R0_zero']),
        'deg_G_mismatch': sum(1 for r in recs if r['deg_G'] != 5 ** (6 + r['r'])),
        'crosscheck_fail': sum(1 for r in recs if not r['checks_ok']),
        'unverified_square_roots': sum(r['n_square_roots'] - r['n_collisions'] for r in recs),
        'deg_Q_mismatch': sum(1 for r in recs if r['deg_Q'] != r['n_square_roots'])}
```

(`out` is initialized with the totals; the omitted lines build Poisson tables and the CSV.)

### C.5 Remainder-sequence check (`hg_ntl.cpp`, core loop)

```cpp
    PowerXMod(Y, e, F);                           // Y = y^((p-1)/2) mod R
    Y -= 1;
    // Classical Euclid: (A, B) -> (B, A mod B) until B = 0.
    ZZ_pX A = R, B = Y, q, r;
    long step = 0, ndeg1 = 0, nge2 = 0;
    while (!IsZero(B)) {
        DivRem(q, r, A, B);
        step++;
        long dq = deg(q);
        if (dq == 1) ndeg1++;
        else { nge2 += (dq >= 2); printf("q %ld %ld\n", step, dq); }
        swap(A, B);
        swap(B, r);
    }
    printf("n_steps %ld\nn_deg1 %ld\nn_deg_ge2 %ld\ndeg_gcd_euclid %ld\n", step, ndeg1, nge2, deg(A));
```

## Appendix D. Exact degree check (`degree_check.py`, run from the repository root)

```python
#!/usr/bin/env python3
"""Exact degree and leading coefficient of F_j (r = 1) by (degree, leading coefficient) tracking.
Run from the repository root (uses the pinned constants of verifier/poseidon.py)."""
import sys; sys.path.insert(0, '.')
from verifier.poseidon import parameters, P
RC, M = parameters()
a, b, c, d, e, f, g, h, i = [x for row in M for x in row]
det_inv = pow((a*(e*i-f*h) - b*(d*i-f*g) + c*(d*h-e*g)) % P, -1, P)
av = [(d*h-e*g)*det_inv % P, (b*g-a*h)*det_inv % P, (a*e-b*d)*det_inv % P]   # row 2 of M^-1
K = pow((1 << 65) + RC[0][2], 5, P)
for j in range(3):
    k0, k1 = [k for k in range(3) if k != j]
    mu = -av[k0] * pow(av[k1], -1, P) % P
    cj = ((K + av[k0]*RC[1][k0] + av[k1]*RC[1][k1]) * pow(av[j], -1, P) + RC[1][j]) % P
    v = [0, 0, 0]; v[k0] = 1; v[k1] = pow(mu, 5, P)
    B = [sum(M[r][t]*v[t] for t in range(3)) % P for r in range(3)]          # w-coefficient of A_j + B_j w
    st, ok = [(1, x) for x in B], all(B)
    for full in (1, 1, 0, 1, 1, 1, 1):                                        # rounds 2, 3, 4 (partial), 60-63
        st = [(5*dd, pow(l, 5, P)) if (full or k == 0) else (dd, l) for k, (dd, l) in enumerate(st)]
        dm = max(dd for dd, _ in st)
        st = [(dm, sum(M[r][t]*st[t][1] for t in range(3) if st[t][0] == dm) % P) for r in range(3)]
        ok = ok and all(l != 0 for _, l in st)
    print(f"j={j}: deg F_j = {st[0][0]}, f_D = {hex(st[0][1])}, no cancellation: {ok}")
```

Output:

```text
j=0: deg F_j = 78125, f_D = 0x34d5ef2a23749e3b46d9289ff2726171551ccaf082d3a6cec73b63ebcf82e613, no cancellation: True
j=1: deg F_j = 78125, f_D = 0x21ddf354f88750a3a25e2d5b7bebdbcc418554419b3ad94c5e28405cde0458fb, no cancellation: True
j=2: deg F_j = 78125, f_D = 0x1524e1d1e988e6162dcc14799e23a3570522f326892802bd9e4102bdf6ed703f, no cancellation: True
```
