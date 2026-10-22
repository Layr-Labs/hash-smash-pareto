# Orchard Poseidon r10: full union-machine derivation

## 1. Claim

This candidate targets `poseidon-orchard-r10-prefix-v1` under `orchard-field-ram-v2`. It uses the published line construction, evaluation recovery, exact value-domain Montgomery powering and inversion-free half-gcd. One centre is tried on one thread.

The complete ledger derives `N_max = 8,669,211,530,023,973` operations, giving `time_log2 = 44.21012` target-compression units after upward rounding at five decimals. The event walk and fixed regions derive `9,895,806,318,240` bytes, giving `memory_log2_bytes = 43.16996`. The normalized cost is `67.38008`. H-ONE, H-NORMAL, the success bound `0.39209` and all experiments are unchanged.

Every score-critical resource integer is generated in this package. No predecessor row, cap, operation total, arena peak or footprint is a ledger input. Jbenisek `c7ef0551` is credited for the 387-register, seven-layer, eight-position and twiddle-one machine construction; Jbenisek `56272e37` and `27fbfbe7` for running-twiddle product passes; cryptogakusei `1533f8f0` for the charged wide-register precedent. Jbenisek `3db5de78` is credited for the least-charge pass planner, delayed Stage-C lifetimes, chunked inversion, bounded omega tables, adaptive apply sizes and split pool placement, all re-derived below.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a
bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the
deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

### 2.1 Round 0

With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`.
`(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

### 2.2 Round 1

The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`.
The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant
`M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let
`(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, where
`d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i`
(the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

### 2.3 Digest polynomial

Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 (partial), 60, 61, 62, 63 (full) put sixteen S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^16 = D = 152,587,890,625`. The leading coefficient is obtained by
propagating leading coefficients through the sixteen layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x17599b3e1f896e6cec97db7882869a7227b0664565956716aded25bb1f47a0f3`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

### 2.4 Collision criterion

If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 76,293,945,312`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. At this r no transform of `H >= m + 1` points exists: `p - 1 = 2^32 * 3 * q'` has roots of unity of order `3 * 2^a` for `a <= 32` only, and `m + 1 = 76,293,945,313 > 3 * 2^32`. Let `B = 3 * 2^31 = 6,442,450,944`, `zeta` a primitive `2B`-th root of unity (`2B = 3 * 2^32` divides `p - 1`) and `omega = zeta^2`, a primitive `B`-th root. Let `kappa = ceil((m + 1) / B) = 12`, `v_k = 2^k` and `u_k = v_k^2 = 4^k` for `k < kappa`, and `z = 4^B`; the `kappa` numbers `n_k = u_k^B = z^k` form a geometric progression and are pairwise distinct, because the order of `z` exceeds `kappa` (`z^d != 1` for every divisor `d` of `p - 1` up to `2 * 10^8`, and `kappa < 2 * 10^8`). The evaluation points are `s_{k,i} = v_k zeta^i` for `k < kappa`, `i < B`, so that `S_{k,i} = s_{k,i}^2 = u_k omega^i`, and `g_c(S_{k,i}) = (F(c + s_{k,i}) - F(c - s_{k,i})) / (2 s_{k,i})`. Write `g_c(x) = sum_{t < kappa} x^{tB} h_t(x)` with `deg h_t < B`. For `y = omega^i` we have `y^B = 1`, hence `g_c(u_k y) = w_k(y)` with `w_k(y) = sum_t n_k^t h_t(u_k y)`, a polynomial of degree `< B`. One inverse transform of size `B` of the values `(g_c(S_{k,i}))_i` returns the coefficients `w_k[j] = u_k^j sum_t n_k^t h_t[j]`. After multiplication by `u_k^{-j}`, for every `j < B` the numbers `W_k[j] = sum_t n_k^t h_t[j]` (`k < kappa`) are the values of the polynomial `h^(j)(X) = sum_t h_t[j] X^t` at the nodes `z^k`, and its coefficients `h_t[j] = g_c[j + tB]` are recovered from them by two correlations of length `kappa` (Lagrange interpolation at geometric nodes, the chirp-z form). Let `M(X) = prod_k (X - z^k) = sum_i mu_i X^i`; the q-binomial theorem gives `mu_{kappa-j} = (-1)^j z^{j(j-1)/2} [kappa choose j]_z`, and `M'(z^k) = z^{k(k-1)/2 + k(kappa-1-k)} prod_{j <= k} (z^j - 1) prod_{j <= kappa-1-k} (1 - z^j)`. With `a_k = W_k[j] / M'(z^k)` and `A(i) = sum_k a_k z^{ki}` (`i < kappa`) we have `h_t[j] = sum_{i > t} mu_i A(i - t - 1)`. Since `z^{ki} = z^{C(k+i,2) - C(k,2) - C(i,2)}` with `C(n,2) = n(n-1)/2`, `A(i) z^{C(i,2)}` is the correlation of the sequence `a_k z^{-C(k,2)}` with the chirp `z^{C(n,2)}` (first correlation), and `h_t[j]` is the correlation of `A` with `(mu_1, ..., mu_kappa)` (second correlation). Each correlation is one cyclic convolution of length `S = 24` (the smallest `2^a` or `3 * 2^a` that is at least `2 kappa - 1`), done with the transform of length `S` (forward, pointwise product, inverse); the transforms of the fixed sequences (the chirp and `mu`) and the constants `mu_i`, `1/M'(z^k)`, `z^{-C(k,2)}` are computed once per trial and shared by the `B` positions `j`. The `2 kappa B = 154,618,822,656` evaluations of `F` are each charged as one target-compression unit (`C(10) = 426` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation. The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 s_{k,i})`, two multiplications for the recurrences of `s_{k,i}` and `1/s_{k,i}`, one store with its address operation, the loop control, the update of the row counter, and the executed shifts, masks, ors and loop control of the bit-reversed index, which are counted inside that function) and the solve (per `j`: two correlations, each two transforms of length `S` with `S/2 log2` butterflies at the charge of the model's own pass cost and `10 S` operations for the pointwise product and the scalings, and `14 kappa` operations for the chirp scalings, the division by `M'`, the loads and the stores) and its once-per-trial constants (`kappa` times two inversions, 40 operations per index, four transforms of length `S` and `10 S` operations) are charged on top.

## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (154,618,822,656 evaluations + 12 inverse NTTs of size 6,442,450,944 + the geometric solve of the 12 cosets (two correlations of length 24 per position) + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; value domain, section 4.6: from S^v, v = 2^33; 220 squaring steps, 45 of them also multiply by S, pointwise)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (426 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. After its leading one, its next 33 high bits are zero. The scan starts from the monomial residue `S^(2^33)`; `2^33 < m`, so this monomial is its own reduction. The remaining 220 bits cost one modular squaring each and 45 of them also multiply by `S`. No low exponent bit is discarded.

Stopping rule. The loop bound `K = 1` is a constant of the algorithm: one centre is tried. A trial is run to its end, or to an ABORT of stage D on an abnormal remainder sequence (6.3) or of stage C on a zero of g on O1 (4.6 step 5), which then resets the allocator and draws the next centre; the claim charges every trial at its maximum (stages E to G at their worst case, section 6), so a trial that fails early is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3, 4.4), the powering has a fixed number of steps, and the half-gcd has the fixed generated trace of section 4.2: cap `j=31`, exactly `72` outer steps, degree decrement `2^j` at a selected step, recursive base `j=6`, and classical tail degree `224`. Hence, with stage D charged for the normal remainder sequence and every other sequence ending its trial after a prefix of that work (section 6.3), the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success, by an ABORT of a trial (the next centre is then drawn), or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

The only randomness of the algorithm is the cost model's random-word primitive (fresh independent algorithmic coins): an independent uniform 256-bit word, each use returning a fresh word, uniform on `0..2^256-1` and independent of everything else, and costing one operation. **Probability space:** every probability of section 9 is over these words. A draw is one fresh word `y`; the draw is `x = y mod p`, computed by at most three steps `if y >= p then y := y - p` (`y < 2^256 < 4p`, so three steps bring `y` below `p`). Write `2^256 = 3p + s0` with `0 < s0 < p`: the residues below `s0` have exactly four preimages below `2^256` and the other `S3 = p - s0 = 4p - 2^256` residues have exactly three, so `P[x = z] = 4/2^256` or `3/2^256` for every residue `z`, every residue has probability at least `3/2^256`, and all but `S3` residues have probability `4/2^256`. The draw is within statistical distance `S3 (1/p - 3/2^256) = 1.574e-39 (2^-128.90) < 2^-128` of uniform on `F_p`. A draw costs 31 operations: for the word one random-word operation, one load, one store into the cell `y` and three control operations (two addresses, the increment of the word index), 6 in all; for the reduction three steps each of a comparison, a conditional branch and a field subtraction (9 operations), with the loop control of 3 per iteration and 2 on exit (11); one Montgomery conversion of `x` (1); the entry of the call (2) and the address of `y` (2). Draws are made once per trial for the centre and once per isolation round for the shift: at most `K (1 + Z) = 65` draws, `65` words. No word is used twice, and the number of words used before a draw depends only on earlier words, so each draw is independent of the earlier course of the algorithm.

#### 4.1.2 Stage E: isolating a root of G

`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). The roots `r` of `G` are the usable `S`. While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw `a` (a draw as in 4.1.1; if it is 0, `a := 1`, since the Taylor shift uses `1/a`; the zero test is 5 operations and the replacement 2, charged in every round), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds.

## 4.2 Machine model and finite charges

Every field operation, load, store, control operation and random word costs one primitive operation. One target compression costs `C(10) = 216 + 21*10 = 426`. The implementation is single-threaded. Runtime plan construction and comparisons are charged key by key in section 6.1.2; each long apply enumerates and compares its complete direct and fixed candidates.

The register file has 387 256-bit words: 256 field registers and 131 integer address registers. All `387*32 = 12,384` bytes are in section 7. Jbenisek `c7ef0551` supplies this seven-layer construction; cryptogakusei `1533f8f0` is the wide-register, fixed-instruction-width precedent.

An eight-position straight-line loop costs

    F(cnt) = 1 + 3 floor(cnt/8) + 2 + 3 (cnt mod 8) + 2.

The five terms are the initial bound, three controls per complete body, main-loop exit, three controls per remaining position and remainder-loop exit. A column kernel of `k=1,...,7` layers has constants `(5,6,10,18,34,139,269)` and position slopes `(11,20,52,128,304,704,1600)` before `F`. In particular, the six-layer constant is `2*63 + 3 + 2*(6-1) = 139` and its slope is `2*64 + 3*6*32 = 704`; the seven-layer values are `2*127 + 3 + 2*(7-1) = 269` and `2*128 + 3*7*64 = 1600`. The wrapper is `2*2^k+6` and the call loop is five operations.

Every product pass in stages C and D uses the running-twiddle construction credited to Jbenisek `56272e37` and `27fbfbe7`; neither stage allocates a product twiddle table. A width-`k` block costs

    B(k) = 2*2^k + 3k*2^(k-1) + 3.

These are its loads and stores, three-operation butterflies, two base updates and the conservative share of the four-block loop. A running chain costs `2^k+4`: root advance, `k-1` squarings, `2^k-1-k` constant multiplications and five controls. For a `2^a` row and a pass starting at layer `l0`, there are `2^(a-k)` blocks and `2^(a-l0-k)` positions. The forward charge is

    2^(a-k) B(k) + 2^(a-l0-k)(2^k+4) + 159k+19
      - 2^(a-l0-k)(2^k-1) + 3,

with 20 in place of 19 for an inverse. The subtraction is exact: in group zero, `2^k-1` butterflies per block have twiddle one and cost two rather than three operations; the straight-line variant costs three controls. For every run of `L` radix-2 layers, the exact-integer ledger enumerates every composition `k1+...+kr=L` with `1 <= ki <= 7`. At a boundary `l`, it substitutes `ki` into the independently derived forward and inverse pass charges of this section, adds the suffix optimum, and keeps the least `(charge,width-sequence)` pair. Lexicographic tie-breaking makes the plan a constant of the algorithm. For example, the 31-layer row selects `7,6,6,6,6`. The inverse uses the same generated boundaries. The ledger asserts that every selected width is in 1..7 and sums to the declared row depth.

Inside a half-gcd node, the ledger uses a larger per-block upper bound: every block pays a complete running chain. Each non-leaf node separately adds exactly 210 lower-order operations: 20 entry/exit, 16 split/degree tests, 50 child-frame operations, 8 return tests, 20 arena mark/release, 18 transform dispatches, 48 matrix-pointer operations, 18 row/sign selections and 12 normal-sequence tests. `NODE_FIXED_EVENTS` generates both displayed subtotals. This explicit finite count replaces the former percentage allowance; no cost margin is assumed.

Every outer apply constructs one `ApplyPlan` from its live degree and budget. It enumerates `N=3*2^e`, `2 <= e <= 32`, until `N` reaches the output length. At each size it prices both valid forms completely. Direct form requires `N >= lc`; fixed-slot form uses `B=N-h>0`, processes `ceil(lc/B)` slots in decreasing order, and proves the unread-input invariant. The selected plan owns its operation rows, four low-end matrix spectra, two high-end operand/output spectra, role transitions and frees. The 39 direct and 33 fixed plans are printed in section 6.2. The recursive bump reservation is released after its four-entry coefficient matrix is copied; the coefficient matrix is freed after the four matrix spectra are formed.

The Stage-D cap is `j=31` and the generated outer driver has `72` steps. At degree `n` it selects the largest admissible budget `2^j-1`, then the adaptive apply enumerates every declared `3*2^e` transform size and selects the least complete direct or descending fixed-slot charge. The degree decreases by exactly `2^j`. The last step leaves degree `224` for the classical tail, and the recursive base is `j=6`, budget 63.

### 4.3 Stage C: the powering schedule (cyclic form, below the block length; block mode in 4.5)

In this entry stage C runs in the value domain (section 4.6). This section and 4.5 define the transforms, the products and the Newton reciprocal that 4.6 uses for its set-up.

For the exponent `E` (here `(p-1)/2`), `m` the degree of the modulus, `N = 3 * 2^a >= 2m - 1` and `N' = 3 * 2^b >= m + 1`. A transform of size `3 * 2^a` is a twiddle-free radix-3 stage (Good-Thomas; each radix-3 leaf costs 8 operations) followed by three independent
rows of radix-2 transforms of length `2^a`, run as passes of at most seven layers (blocks of at most 128 data words in registers, the group twiddles held in registers: the block form of section 4.2). The state is `s = a / N` so no scaling is needed in the loop.
One step maps the residue `a` (`m` coefficients, stored in the buffer `Y` of `N` elements) to `a^2 mod g`:
```
Y := conv_sq(Y)                       square: forward transform, pointwise square fused with the first inverse pass, inverse transform
F[i] := Y[i] + Y[i+N'] (i < m)       fold of the low part modulo x^N' - 1 (saved in the buffer F of m elements)
Y[0..m-2] := Y[m..2m-2]               high part T1 of the square
Y := conv(Y, MU)                      quotient q (Barrett): MU = x^(N-m+2) * floor(x^(2m-2)/g) / (N N') stored compactly (m-1 elements)
Y := conv_N'(Y, g)                    (q * g) mod (x^N' - 1)
Y[i] := F[i] - Y[i] (i < m)           new residue; if the exponent bit is 1: shift by x and subtract lead * g (streaming)
```
In this cyclic form the spectra of `MU` and of `g` are not stored (block mode, section 4.5, keeps `MU` and `g` in coefficient form and makes their chunk forms at each use): for each multiplication the second operand is transformed one row of the Good-Thomas layout at a time into a buffer `tmp`, immediately multiplied into the corresponding row of `Y`, and discarded.
`MU` is computed once from `g` by Newton iteration with the same row-wise products. The leading exponent bits are absorbed by starting from the monomial `S^v` with `v < m`.
All charges of this stage depend only on `m` and the exponent, not on the coefficients.
### 4.4 Stage D: the half-gcd

Notation: a polynomial is stored as its coefficient array with the top coefficient nonzero (length = degree + 1). Euclid sequence of `(a, b)`, `deg a > deg b`: `r_0 = a`, `r_1 = b`, `r_{i-1} = q_i r_i + r_{i+1}`; `d_j = deg q_1 + ... + deg q_j`, so `deg r_j = deg a - d_j`;
`R_j = Q_1 ... Q_j` with `Q_i = [[q_i, 1], [1, 0]]` (entries of degree at most `d_j`; the first-row entries of degree exactly `d_j` for `r11`), and `(r_0, r_1)^T = R_j (r_j, r_{j+1})^T`.

`hgcd(a, b, k)` (`deg a = n`) returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` and, only when asked (the calls of the Euclid driver, below), the pair `(r_h, r_{h+1})`; the inner calls return the matrix only. The procedure: if `b = 0` or `n - deg b > k` return the identity. If `k <= 96`, plain Euclid (`poly_divrem_naive`) while the next quotient degree fits the remaining parameter; a division step whose quotient has two coefficients (the normal case) is one pass over the remainder, `r_k = a_k - q0 b_k - q1 b_(k-1)`, with `b_(k-1)` kept from the previous iteration and no copy of `a` (per element 2 loads, 2 multiplications, 2 subtractions, 1 store, each load and store with its address operation, the loop control of 3 and the test `if (k)` of 2 operations), and `R := R Q` for a two-coefficient quotient is likewise one pass per entry pair (`mul_add_q2`).
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`, evaluated cyclically on `3 * 2^j` points (the high coefficients of `c` and `d` cancel, so the cyclic result is exact); the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each of the four matrix entries are transformed once (six forward transforms of a row) and the two output rows are inverse transformed (`conv_bilin_otf`), the sign of each output being absorbed in the scale factor `1/N`; (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1`
(`d_1 = deg R1`) return `R1` and `(c, d)`; (4) divide `c = q d + e` (`divrem_any`); (5) `k3 = k - d_1 - deg q`, `s3 = deg d - 2 k3`; if `s3 > 0`, `R2 = hgcd(d quo x^s3, e quo x^s3, k3)` (the top `2 k3 + 1` coefficients of `d` and the coefficients of `e` of the same degrees, read in place, matrix wanted), otherwise the call runs on `(d, e)`; this is the same top-coefficient lemma that step (1) uses (the quotients of a pair whose degrees sum to at most `k3`, and the stopping test, depend only on those coefficients; von zur Gathen and Gerhard, Modern Computer Algebra, chapter 11; the same truncation as bradcush 1aa56884, its lemma 4.4), and 1aa56884 (its Appendix G.3) runs the node with and without it against plain Euclid; (6) only if the caller wants the pair, `(c', d') = R2^{-1} (d, e)` by `apply_inv`, each moved into an array of its own length; return `R1 Q R2` (matrix products by NTT, only if the matrix is wanted; the product of the two 2 x 2 matrices transforms each of the eight entries once per row, with the right-factor entries of one column pair held and the left-factor entries streamed, and inverse transforms the four outputs, `conv_bilin_otf` again).
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 224`: one outer step, which is the inversion-free half-gcd of 4.4.2 on the top window with its matrix applied to the whole pair while `(n - 1)/2 >= 127`, and `(c, d) = hgcd(a, b, floor((n+1)/2))` below, then one division `c = q d + e` and `(a, b) := (d, e)`; at or below 224 it runs classical Euclid; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). With `H-NORMAL` (9.5) stage D runs the normal-sequence procedure of bradcush (entry e6dcb600): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter ; a zero remainder met inside hgcd or in the division of the outer loop also ends the trial (ABORT); on any other case the trial ends (ABORT) and the next centre is drawn (section 6.3).

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

#### 4.4.1 The lean stage D (this entry; the stage D of bradcush 1aa56884, its section 4.4 and lemmas 4.4 and 4.8, credited)

This entry runs the half-gcd above (its last outer step, 4.4.2) with the changes below, all from 1aa56884 (credited in the dependencies and the note), charged by this model's rules of 4.2 and 4.5. They change where arrays live and which coefficients are formed, never a quotient: every quotient used is a quotient of the whole pair (lemma 4.4 above, and lemma 4.8 below).

1. *The base case in place.* For `k <= 96` the two remainders are two arrays and a division step with a quotient of two coefficients is one pass `r_k = a_k - q0 b_k - q1 b_(k-1)` written over the array of `a`; the roles of the two arrays swap. The four matrix entries are four arrays of `k + 2` elements allocated once, and `R := R Q` writes `r11 q + r12` over `r12`. No array is allocated or freed inside the loop.
2. *Matrix-only calls.* A call returns the reduced pair only when its caller wants it: the calls of the Euclid driver `poly_gcd_own` and, inside them, the second calls with `s3 <= 0`. Every call inside a first call, and every truncated second call, returns its matrix only.
3. *Windows.* In a node that wants its matrix only and has `s3 > 0`, the block products of `apply_inv` form only the top window of `c` and `d`: the coefficients of degree at least `s3 - 1` (lemma 4.8 (a)). Such a node tests that the coefficients of `c` and `d` at their normal leading degrees `la - h - 1` and `la - h - 2` are nonzero (2 tests, charged) and ABORTs otherwise, so it never reports a shorter remainder from a window.
4. *The two tests and the ABORT.* At every division the quotient test (the quotient has degree 1) and after every recursive call and every call of `poly_gcd_own` the return test (the call returned exactly its parameter as degree count; a zero remainder inside hgcd or in the outer-loop division also ABORTs), 2 operations each, charged wherever they execute. If a test fails the trial ABORTs: the allocator is reset to its state after initialisation (`1,000` operations, charged in section 6) and the next centre is drawn. On the normal remainder sequence neither test fails (6.3), so every division of stage D is the one-pass division by a quotient of two coefficients and the Newton division is never run.
5. *No pieces.* 1aa56884's top node on two pieces of `g` and `R` is not used: stage C leaves `g` and `R` as one array each, and the first step of `poly_gcd_own` is an outer step of 4.4.2 like the others.
6. *Adaptive direct and descending fixed-slot applies.* For a live outer step let `h=2^j-1`, operand length `la=n+1`, and output lengths `lc=n-h` and `lc-1`. The immutable plan enumerates every `N=3*2^e`, `2 <= e <= 32`, from the first size that holds the longest matrix entry through the first size with `N >= lc`. Eight plan actions are charged per tested size, followed by the exact comparison and cache insertion in section 6.1.2.

At one size the four matrix-entry lengths are `h+1,h,h,h-1`. A partial forward is six fixed actions, eight radix-3 input actions per live leaf, and three generated radix-2 row transforms. A partial inverse is three fixed actions, three inverse rows, and eight radix-3 output actions per requested leaf. Matrix copies and zero fills are charged separately as `7*l+5*(N-l)`.

The direct candidate exists when `N >= lc`. It folds each operand coefficient above `N` at ten actions, makes six forwards and two inverses, and executes the required 20-action fused point multiset: six addresses, six loads, four multiplications, two additions or subtractions and separate `c` and `d` stores. The stores reuse the charged operand addresses. Exact outputs are scaled and written at eight actions per coefficient plus call closure.

The fixed candidate exists when `B=N-h>0`. It sets `nb=ceil(lc/B)` and visits `nb-1,...,0`. Slot `i` reads exactly `[max(0,iB-h), min((i+1)B,lc))`; a product has fewer than `N` coefficients after the cyclic wrap is discarded. The fused point row is 24 actions per transform point and explicitly contains both output stores. Nonzero slots inverse-transform all `N` values; slot zero emits its live prefix. Both output blocks are scaled and placed separately. Before slot `i` writes `[iB,(i+1)B)`, every higher input block has already been read and every lower unread block lies below the destination.

The least complete candidate is selected. Its six arrays are the four matrix spectra on the low pool end and the two operand/output spectra on the high end. The coefficient matrix coexists with the recursive bump only during its generated handoff, the bump is released, four spectra are formed, the coefficient matrix is freed, and only then are the two operand/output spectra allocated. `operation_rows()` and `allocation_arrays()` of that same plan supply sections 6 and 7. No chunk form or accumulator exists.

**Lemma 4.8 (windows; 1aa56884's lemma 4.8 (a)).** (a) In a node that wants its matrix only, with `s3 > 0`, the rest of the node reads `c` only at degrees at least `s3` and `d` only at degrees at least `s3 - 1`.
*Proof.* (a) The stopping test and the quotient test use `deg c` and `deg d`; the quotient `q = q1 x + q0` uses the top two coefficients of `c` and of `d`; and `e_i = c_i - q0 d_i - q1 d_(i-1)`. The second call reads only `d quo x^s3` and `e quo x^s3`, that is `d_i` and `e_i` for `i >= s3`, hence `c_i` for `i >= s3` and `d_i` for `i >= s3 - 1`. After it the node needs only `R1`, `q` and `R2` (and `s3 - 1 <= deg d - 1`, so the top two coefficients are inside the window). QED

The charges of these steps use this model's rules in 4.2 and 4.5; their complete finite expansion is row D of section 6.

#### 4.4.2 The outer steps: the inversion-free half-gcd on three rows (bradcush `4bcabff8`)

Each outer step of `poly_gcd_own` with `(n - 1)/2 >= 127` runs bradcush's inversion-free half-gcd (entry `4bcabff8`, with the transform reuse of `b30de9bf`; read as text only, ported and charged in this cost model as in our r = 3 entry `bcf8e01c`). Matrices and remainders are kept up to nonzero scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside the recursion; the gcd is the same up to a scalar and is made monic at the end. A node of budget `k = 2^j - 1` makes two child calls of budget `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a power-of-two transform of `n` points in the block form of 4.2 after a twist, joined by a 3-row CRT for `(c, d) = adj(M1)(a, b)` on the top window; then the pseudo-division and the product `M = M1 [[Q, 1], [b^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and the scale of a step is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the row `Y - 1` values of each child's matrix are returned by the child, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The twists use roots of order `2n` and `4n` (`4n <= 2^32` divides `p - 1`, so `j <= 31`), from the squaring chain of the running twiddle factors of the row transform (4.2); the scales `1/2^a` (`a <= 30`) are a table of 31 words built at the entry of stage D (`1/2 = (p + 1)/2` an immediate, 29 multiplications). The base case (budget 63) runs two remainder steps per pass over its window. An outer step calls the node on the top window of the pair with `k = 2^j - 1` the largest with `k <= min(2^31 - 1, (n - 1)/2)` and applies `adj(M)` to the whole pair in place (`apply_inv` of 4.4.1 item 6: the selected adaptive direct or descending fixed-slot plan of 4.4.1 item 6), then makes one division with the quotient test; once no `j >= 7` satisfies the selection rule, at degree `224`, classical division steps finish. The node arrays are allocated and released by the generated recursive trace in section 7. On the normal sequence every length, budget and allocation is a function of `m` alone. Every division and pseudo-division tests that its quotient has degree 1 and every node tests on return that it removed exactly its budget (2 operations each), a zero remainder also ends the trial, and on any other case the trial ABORTs (6.3). The repetitions are listed in 6.2.

### 4.5 Stage-C product plans

Every Newton and Barrett product constructs one immutable `PolynomialProductPlan(left,right,output)`. When an admissible field transform length `N` is at least `left+right-1`, the plan selects the least complete charge among those lengths:

    2 T(N) + I(N)
    + 7(left+right) + 5(2N-left-right)
    + 10N + 4 output + F(output)
    + dispatch and call/return.

It allocates two `N`-word spectra. The left spectrum is overwritten by the pointwise product and then by the inverse output; the right spectrum is released after the pointwise loop. Section 7 prices those two lifetimes from the emitted allocator trace.

If no field transform is long enough, the fixed block-slot plan uses coefficient block `B=6,442,450,944` and transform length `N=12,884,901,888`. With `nl=ceil(left/B)`, `nr=ceil(right/B)` and `no=min(nl+nr-1,ceil(output/B))`, it charges

    (nl+nr) T(N) + no I(N),
    7(left+right) + 5((nl+nr)B-left-right),
    no*(7 min(B,output) + F(min(B,output))),
    nl*nr*(10N + F(N)),

plus one dispatch per input form and output slot and the call close. Its allocation schedule retains all `nl+nr` input spectra, then allocates, inverse transforms, places and frees one `N`-word output accumulator for each of the `no` slots. The exact allocator operations for those lifetimes come only from section 7. Section 6.1.1 prints every live plan and total; `operation_rows()` in Appendix X.2 expands the displayed formulas into named action rows. Section 7 consumes the allocation schedule from the same objects. Stage-D applies use the adaptive direct/fixed rule of 4.4.1 item 6 and do not reuse these product plans.

### 4.6 Stage C in the value domain

**Point sets and representation.** Let `H` be the subgroup of order `h=4,294,967,296`, `u_k=5^k`, `C_k=u_k H`, and `n_k=u_k^h`. The order check in section 10.3 makes the `2K=36` cosets below pairwise disjoint. Put `O1=C_0 union ... union C_{K-1}`, `O2=C_K union ... union C_{2K-1}`, `M(Y)=prod_{i<K}(Y-n_i)`, and `P1(X)=M(X^h)`. Thus `deg P1=n1=77,309,411,328 >= m+1=76,293,945,313`, `P1` is squarefree with root set O1, and P1 is the nonzero constant `M(n_k)` on C_k in O2.

Write `f=sum_{j<h} X^j F_j(X^h)`, `deg F_j<K`. Values on one point set are converted to the other by inverse inner transforms, the direct K-by-K Toeplitz sum at each of the h positions, and forward inner transforms. Both directions are exact Lagrange interpolation on the distinct nodes `n_k`.

**Montgomery lemma.** Let g be monic of degree m and nonzero on O1. If `R~` has degree at most m and u0 is the polynomial of degree below n1 with `u0(x)=-R~(x)^2/g(x)` on O1, then `R~^2+u0 g` vanishes on every root of P1. Hence `W=(R~^2+u0 g)/P1` is a polynomial of degree at most m-1 and `W=R~^2 P1^-1 mod g`. On O2 its values are `(R~^2+u0 g)/M(n_k)`. Multiplication by `X^b` for the next exponent bit preserves `R~_i=S^e_i P1 mod g`.

**Extension lemma.** For `deg F<K`, exact Lagrange interpolation gives

    F(z^(K+t))=M(z^(K+t)) sum_{i<K} F(z^i) z^-i / (M'(z^i)(z^(K+t-i)-1)).

Every denominator is nonzero because the nodes are distinct. This is the direct sum when K is small and the fixed-kernel correlation stated above otherwise.

**Eight executed steps and ledger bindings.** `VSHIFT_LOG=33` means the leading exponent bit and the next 33 following high zero bits are preloaded as `S^(2^33)`; `2^33<m`, so the monomial is its own reduction. No low bit is discarded. The remaining 220 bits contain 45 ones.

1. `newton_reciprocal` and `quotient_product`: form the reversed reciprocal to `ell=9,605,400,609` and `q=floor(X^v P1/g)`.
2. `g_geometric_evaluation`, `g_correlation_control`, and `g_inner_transforms`: evaluate g on O1 and O2 using `Le=64`.
3. `start_residue` and `q_correlation_control`: evaluate q using `Lq=24` and form `R~_0=X^v P1-qg` on O2.
4. `first_extension`: extend `R~_0` from O2 to O1.
5. `batch_inversion`: form `-1/g` on O1 in `2^16`-word chunks. Every prefix product is tested before inversion; zero executes the charged ABORT.
6. `powering_loop`: for each bit b, form `R1=R1^2 G1`, extend O1 to O2, form `R2=X^b(R2^2+R1 G2)/M(n_k)`, and extend O2 to O1.
7. `exit_montgomery`: replace the square by the linear numerator, perform the last extension, and obtain `R=S^((p-1)/2) mod g`.
8. `two_interpolations` and `interpolation_control`: inverse inner transforms followed by the declared correlations of length `Lx=48` return R and g in coefficient order for Stage D.

The rows `allocation_and_zero_control`, `zero_fills_allocations_and_control`, `tables_and_plans`, and `entry_exit` charge their named work around these eight steps. Section 6.1 expands every row into primitive-action coefficients.

**Delayed lifetimes and bounded tables.** Products 1 through 68 run with the Newton scratch. The trace then frees the two Newton-only scratch arrays, allocates the n1-word `R1` value destination and the `ell`-word quotient coefficient destination, and executes quotient product 69 while both destinations are live. After that product it releases the coefficient destination and the remaining reciprocal arrays, then allocates `R2` before step 2 and `G1` at the loop entry. These exact events, not a peak formula, produce section 7. Batch inversion uses one 2^16-word prefix array, reused chunk by chunk; `BATCH_COEFFICIENT_ACTIONS` has fourteen atomic actions and `BATCH_CHUNK_ACTIONS` has twenty around the 512-step inversion.

The b=1 boundary obtains each of its four row factors from two 2^16-entry tables. Per factor it charges two table loads and one multiplication, twelve actions per call, in `OMEGA_BOUNDARY_ACTIONS`. Each table entry is generated by the 25 named actions in `OMEGA_TABLE_ENTRY_ACTIONS`; there is no h-word omega table. The two tables, the group buffer, transform row, kernels and coset constants have separate allocation and free events.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Complete operation ledger

| row | operations |
| --- | ---: |
| init | 18,009 |
| setup | 4,906 |
| A | 1,228 |
| B | 148,386,783,813,197 |
| C | 5,937,454,131,022,267 |
| D | 2,583,370,481,286,514 |
| E | 129,546,477 |
| F | 45,948 |
| G | 6,195 |
| trial_loop | 1,012 |
| plan_misses | 78,043 |
| output | 4,063,392 |
| offline | 136,785 |
| **N_max** | **8,669,211,530,023,973** |

The exact raw time is `log2(N_max/426) = 44.2101125885211102140733528825393886665453556217726986468509296273130428943736230236497758`. Upward rounding at five decimals gives `time_log2 = 44.21012`. The normalized cost is reported separately in section 8. Every search is charged: the isolation cap is in E; this no-Graeffe family has one fixed square-root/back-map routine and no Stage-F candidate scan. The offline literal construction is charged at its exact 136,785 operations.

### 6.0.1 Every non-B/C/D row

| ledger row | generated component | operations |
| --- | --- | ---: |
| init | organizer constant words | 1,608 |
| init | four field inversions | 10,240 |
| init | six table pages | 6,144 |
| init | entry call and bounds | 17 |
| setup | three field inversions | 1,536 |
| setup | nine mds products | 2,304 |
| setup | three line solves | 963 |
| setup | calls branches and stores | 103 |
| A | random word and call | 2 |
| A | two field reductions | 1,024 |
| A | two sampler control paths | 194 |
| A | stores and exit | 8 |
| E | sixty four rounds | 129,545,216 |
| E | stage bookkeeping | 1,000 |
| F | stage bookkeeping | 1,000 |
| F | Tonelli control | 10,837 |
| F | root nonzero comparison and branch | 2 |
| F | field operations with memory | 34,010 |
| G | two target compressions | 852 |
| G | two reference wrappers | 5,160 |
| G | pair difference comparison and branch | 2 |
| trial_loop | sixty four field word transfers | 384 |
| trial_loop | forty eight integer word transfers | 192 |
| trial_loop | sixty four stage control steps | 256 |
| trial_loop | thirty two call edges | 64 |
| trial_loop | twenty six loop steps | 104 |
| trial_loop | trial counter load and address | 2 |
| trial_loop | counter increment | 1 |
| trial_loop | limit load and address | 2 |
| trial_loop | limit comparison | 1 |
| trial_loop | loop branch | 1 |
| trial_loop | close call and return | 2 |
| trial_loop | stage pointer updates | 3 |
| plan_misses | generated planner keys | 95,741 |
| output | two field serializations | 2,621,440 |
| output | two message copies | 1,048,576 |
| output | two digest copies | 393,216 |
| output | two output call paths | 160 |
| offline | input literal loops | 65,448 |
| offline | field literal operations and bit loops | 2,622 |
| offline | word literal operations | 270 |
| offline | output literal loops | 68,445 |

Each final row above is the sum of live component dictionaries. The AST audit rejects a numeric literal as a final row source and rejects any later reassignment.

| one Stage-E isolation round | operations |
| --- | ---: |
| fixed exponent schoolbook | 2,015,076 |
| split point actions | 2,312 |
| split point loop | 869 |
| round close | 64 |
| two classical gcds | 5,216 |
| shift coefficients | 512 |
| driver | 95 |

| Stage-F field-operation family | field operations |
| --- | ---: |
| power by q | 267 |
| power by q plus one over two | 266 |
| Tonelli steps | 592 |
| six inverse fifth powers | 2,262 |
| two back map affine updates | 12 |
| two antipodal point updates | 2 |

The Stage-F field-operation rows sum to 3,401. Each is charged by the ten primitive memory/field actions in 6.1.3; the separate Tonelli control dictionary, root test and stage bookkeeping complete row F.

### 6.1 Stage C expansion

| event family | operations |
| --- | ---: |
| tables and plans | 4,667,240 |
| newton reciprocal | 21,787,555,000,410 |
| quotient product | 6,426,834,963,221 |
| g geometric evaluation | 5,135,799,418,957 |
| g correlation control | 1,236,950,581,248 |
| g inner transforms | 9,002,970,663,084 |
| start residue | 8,529,124,467,870 |
| q correlation control | 4,638,564,679,680 |
| first extension | 12,967,615,547,912 |
| batch inversion | 1,114,366,279,685 |
| powering loop | 5,789,377,875,408,805 |
| exit montgomery | 14,465,485,392,397 |
| two interpolations | 23,846,679,628,427 |
| interpolation control | 28,346,784,153,600 |
| allocation and zero control | 9,924,595,679,237 |
| zero fills allocations and control | 652,924,459,731 |
| entry exit | 1,000 |
| allocator trace | 29,763 |
| **row C** | **5,937,454,131,022,267** |

Every Newton precision is generated by doubling from one to `ell`; each step charges both products. Each product enumerates admissible `2^a` and `3*2^a` lengths, or uses the stated block product when the field has no sufficiently long transform. The point-set extensions, fused boundaries, batch inversion, exit and interpolations are separate terms.

#### 6.1.1 Stage-C product plans

| plan | mode | left | right | output | transform points | left blocks | right blocks | output slots | total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | direct | 2 | 1 | 2 | 2 | 1 | 1 | 1 | 683 |
| 2 | direct | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 683 |
| 3 | direct | 4 | 2 | 4 | 8 | 1 | 1 | 1 | 1,912 |
| 4 | direct | 2 | 4 | 4 | 8 | 1 | 1 | 1 | 1,912 |
| 5 | direct | 8 | 4 | 8 | 16 | 1 | 1 | 1 | 2,796 |
| 6 | direct | 4 | 8 | 8 | 16 | 1 | 1 | 1 | 2,796 |
| 7 | direct | 16 | 8 | 16 | 32 | 1 | 1 | 1 | 4,180 |
| 8 | direct | 8 | 16 | 16 | 32 | 1 | 1 | 1 | 4,180 |
| 9 | direct | 32 | 16 | 32 | 64 | 1 | 1 | 1 | 6,615 |
| 10 | direct | 16 | 32 | 32 | 64 | 1 | 1 | 1 | 6,615 |
| 11 | direct | 64 | 32 | 64 | 128 | 1 | 1 | 1 | 11,296 |
| 12 | direct | 32 | 64 | 64 | 128 | 1 | 1 | 1 | 11,296 |
| 13 | direct | 128 | 64 | 128 | 192 | 1 | 1 | 1 | 21,549 |
| 14 | direct | 64 | 128 | 128 | 192 | 1 | 1 | 1 | 21,549 |
| 15 | direct | 256 | 128 | 256 | 384 | 1 | 1 | 1 | 37,364 |
| 16 | direct | 128 | 256 | 256 | 384 | 1 | 1 | 1 | 37,364 |
| 17 | direct | 512 | 256 | 512 | 768 | 1 | 1 | 1 | 75,513 |
| 18 | direct | 256 | 512 | 512 | 768 | 1 | 1 | 1 | 75,513 |
| 19 | direct | 1,024 | 512 | 1,024 | 1,536 | 1 | 1 | 1 | 146,576 |
| 20 | direct | 512 | 1,024 | 1,024 | 1,536 | 1 | 1 | 1 | 146,576 |
| 21 | direct | 2,048 | 1,024 | 2,048 | 3,072 | 1 | 1 | 1 | 293,895 |
| 22 | direct | 1,024 | 2,048 | 2,048 | 3,072 | 1 | 1 | 1 | 293,895 |
| 23 | direct | 4,096 | 2,048 | 4,096 | 6,144 | 1 | 1 | 1 | 600,350 |
| 24 | direct | 2,048 | 4,096 | 4,096 | 6,144 | 1 | 1 | 1 | 600,350 |
| 25 | direct | 8,192 | 4,096 | 8,192 | 12,288 | 1 | 1 | 1 | 1,238,901 |
| 26 | direct | 4,096 | 8,192 | 8,192 | 12,288 | 1 | 1 | 1 | 1,238,901 |
| 27 | direct | 16,384 | 8,192 | 16,384 | 24,576 | 1 | 1 | 1 | 2,568,716 |
| 28 | direct | 8,192 | 16,384 | 16,384 | 24,576 | 1 | 1 | 1 | 2,568,716 |
| 29 | direct | 32,768 | 16,384 | 32,768 | 49,152 | 1 | 1 | 1 | 5,337,507 |
| 30 | direct | 16,384 | 32,768 | 32,768 | 49,152 | 1 | 1 | 1 | 5,337,507 |
| 31 | direct | 65,536 | 32,768 | 65,536 | 98,304 | 1 | 1 | 1 | 11,783,507 |
| 32 | direct | 32,768 | 65,536 | 65,536 | 98,304 | 1 | 1 | 1 | 11,783,507 |
| 33 | direct | 131,072 | 65,536 | 131,072 | 196,608 | 1 | 1 | 1 | 24,375,738 |
| 34 | direct | 65,536 | 131,072 | 131,072 | 196,608 | 1 | 1 | 1 | 24,375,738 |
| 35 | direct | 262,144 | 131,072 | 262,144 | 393,216 | 1 | 1 | 1 | 50,423,633 |
| 36 | direct | 131,072 | 262,144 | 262,144 | 393,216 | 1 | 1 | 1 | 50,423,633 |
| 37 | direct | 524,288 | 262,144 | 524,288 | 786,432 | 1 | 1 | 1 | 104,250,600 |
| 38 | direct | 262,144 | 524,288 | 524,288 | 786,432 | 1 | 1 | 1 | 104,250,600 |
| 39 | direct | 1,048,576 | 524,288 | 1,048,576 | 1,572,864 | 1 | 1 | 1 | 215,332,895 |
| 40 | direct | 524,288 | 1,048,576 | 1,048,576 | 1,572,864 | 1 | 1 | 1 | 215,332,895 |
| 41 | direct | 2,097,152 | 1,048,576 | 2,097,152 | 3,145,728 | 1 | 1 | 1 | 444,571,062 |
| 42 | direct | 1,048,576 | 2,097,152 | 2,097,152 | 3,145,728 | 1 | 1 | 1 | 444,571,062 |
| 43 | direct | 4,194,304 | 2,097,152 | 4,194,304 | 6,291,456 | 1 | 1 | 1 | 916,983,437 |
| 44 | direct | 2,097,152 | 4,194,304 | 4,194,304 | 6,291,456 | 1 | 1 | 1 | 916,983,437 |
| 45 | direct | 8,388,608 | 4,194,304 | 8,388,608 | 12,582,912 | 1 | 1 | 1 | 1,974,941,709 |
| 46 | direct | 4,194,304 | 8,388,608 | 8,388,608 | 12,582,912 | 1 | 1 | 1 | 1,974,941,709 |
| 47 | direct | 16,777,216 | 8,388,608 | 16,777,216 | 25,165,824 | 1 | 1 | 1 | 4,059,512,228 |
| 48 | direct | 8,388,608 | 16,777,216 | 16,777,216 | 25,165,824 | 1 | 1 | 1 | 4,059,512,228 |
| 49 | direct | 33,554,432 | 16,777,216 | 33,554,432 | 50,331,648 | 1 | 1 | 1 | 8,338,405,179 |
| 50 | direct | 16,777,216 | 33,554,432 | 33,554,432 | 50,331,648 | 1 | 1 | 1 | 8,338,405,179 |
| 51 | direct | 67,108,864 | 33,554,432 | 67,108,864 | 100,663,296 | 1 | 1 | 1 | 17,115,605,618 |
| 52 | direct | 33,554,432 | 67,108,864 | 67,108,864 | 100,663,296 | 1 | 1 | 1 | 17,115,605,618 |
| 53 | direct | 134,217,728 | 67,108,864 | 134,217,728 | 201,326,592 | 1 | 1 | 1 | 35,122,802,697 |
| 54 | direct | 67,108,864 | 134,217,728 | 134,217,728 | 201,326,592 | 1 | 1 | 1 | 35,122,802,697 |
| 55 | direct | 268,435,456 | 134,217,728 | 268,435,456 | 402,653,184 | 1 | 1 | 1 | 72,029,193,632 |
| 56 | direct | 134,217,728 | 268,435,456 | 268,435,456 | 402,653,184 | 1 | 1 | 1 | 72,029,193,632 |
| 57 | direct | 536,870,912 | 268,435,456 | 536,870,912 | 805,306,368 | 1 | 1 | 1 | 147,625,604,727 |
| 58 | direct | 268,435,456 | 536,870,912 | 536,870,912 | 805,306,368 | 1 | 1 | 1 | 147,625,604,727 |
| 59 | direct | 1,073,741,824 | 536,870,912 | 1,073,741,824 | 1,610,612,736 | 1 | 1 | 1 | 313,183,330,295 |
| 60 | direct | 536,870,912 | 1,073,741,824 | 1,073,741,824 | 1,610,612,736 | 1 | 1 | 1 | 313,183,330,295 |
| 61 | direct | 2,147,483,648 | 1,073,741,824 | 2,147,483,648 | 3,221,225,472 | 1 | 1 | 1 | 640,409,147,790 |
| 62 | direct | 1,073,741,824 | 2,147,483,648 | 2,147,483,648 | 3,221,225,472 | 1 | 1 | 1 | 640,409,147,790 |
| 63 | direct | 4,294,967,296 | 2,147,483,648 | 4,294,967,296 | 6,442,450,944 | 1 | 1 | 1 | 1,308,903,312,581 |
| 64 | direct | 2,147,483,648 | 4,294,967,296 | 4,294,967,296 | 6,442,450,944 | 1 | 1 | 1 | 1,308,903,312,581 |
| 65 | direct | 8,589,934,592 | 4,294,967,296 | 8,589,934,592 | 12,884,901,888 | 1 | 1 | 1 | 2,674,870,686,300 |
| 66 | direct | 4,294,967,296 | 8,589,934,592 | 8,589,934,592 | 12,884,901,888 | 1 | 1 | 1 | 2,674,870,686,300 |
| 67 | block-slot | 9,605,400,609 | 8,589,934,592 | 9,605,400,609 | 12,884,901,888 | 2 | 2 | 2 | 5,502,633,031,084 |
| 68 | block-slot | 8,589,934,592 | 9,605,400,609 | 9,605,400,609 | 12,884,901,888 | 2 | 2 | 2 | 5,502,633,031,084 |
| 69 | block-slot | 9,605,400,609 | 9,605,400,609 | 19,210,801,217 | 12,884,901,888 | 2 | 2 | 3 | 6,336,784,332,504 |

For every row, `PolynomialProductPlan.operation_rows()` substitutes that row's live dimensions into the direct or block-slot formulas of 4.5 and asserts that their named sum equals the printed total. The same object supplies its section-7 allocation schedule. A direct plan allocates two spectra and overwrites the left spectrum with the output. A block-slot plan retains every input block spectrum, allocates one output accumulator per slot in sequence, inverse transforms and places it, then reuses that accumulator location for the next slot.

### 6.1.2 Planner keys

| family | exact key | operations |
| --- | --- | ---: |
| product | `(1, 2, 2)` | 1,789 |
| product | `(2, 1, 2)` | 1,789 |
| product | `(2, 4, 4)` | 1,750 |
| product | `(4, 2, 4)` | 1,750 |
| product | `(4, 8, 8)` | 1,690 |
| product | `(8, 4, 8)` | 1,690 |
| product | `(8, 16, 16)` | 1,630 |
| product | `(16, 8, 16)` | 1,630 |
| product | `(16, 32, 32)` | 1,570 |
| product | `(32, 16, 32)` | 1,570 |
| product | `(32, 64, 64)` | 1,531 |
| product | `(64, 32, 64)` | 1,531 |
| product | `(64, 128, 128)` | 1,471 |
| product | `(128, 64, 128)` | 1,471 |
| product | `(128, 256, 256)` | 1,411 |
| product | `(256, 128, 256)` | 1,411 |
| product | `(256, 512, 512)` | 1,351 |
| product | `(512, 256, 512)` | 1,351 |
| product | `(512, 1024, 1024)` | 1,312 |
| product | `(1024, 512, 1024)` | 1,312 |
| product | `(1024, 2048, 2048)` | 1,252 |
| product | `(2048, 1024, 2048)` | 1,252 |
| product | `(2048, 4096, 4096)` | 1,192 |
| product | `(4096, 2048, 4096)` | 1,192 |
| product | `(4096, 8192, 8192)` | 1,132 |
| product | `(8192, 4096, 8192)` | 1,132 |
| product | `(8192, 16384, 16384)` | 1,093 |
| product | `(16384, 8192, 16384)` | 1,093 |
| product | `(16384, 32768, 32768)` | 1,033 |
| product | `(32768, 16384, 32768)` | 1,033 |
| product | `(32768, 65536, 65536)` | 973 |
| product | `(65536, 32768, 65536)` | 973 |
| product | `(65536, 131072, 131072)` | 913 |
| product | `(131072, 65536, 131072)` | 913 |
| product | `(131072, 262144, 262144)` | 874 |
| product | `(262144, 131072, 262144)` | 874 |
| product | `(262144, 524288, 524288)` | 814 |
| product | `(524288, 262144, 524288)` | 814 |
| product | `(524288, 1048576, 1048576)` | 754 |
| product | `(1048576, 524288, 1048576)` | 754 |
| product | `(1048576, 2097152, 2097152)` | 694 |
| product | `(2097152, 1048576, 2097152)` | 694 |
| product | `(2097152, 4194304, 4194304)` | 655 |
| product | `(4194304, 2097152, 4194304)` | 655 |
| product | `(4194304, 8388608, 8388608)` | 595 |
| product | `(8388608, 4194304, 8388608)` | 595 |
| product | `(8388608, 16777216, 16777216)` | 535 |
| product | `(16777216, 8388608, 16777216)` | 535 |
| product | `(16777216, 33554432, 33554432)` | 475 |
| product | `(33554432, 16777216, 33554432)` | 475 |
| product | `(33554432, 67108864, 67108864)` | 436 |
| product | `(67108864, 33554432, 67108864)` | 436 |
| product | `(67108864, 134217728, 134217728)` | 376 |
| product | `(134217728, 67108864, 134217728)` | 376 |
| product | `(134217728, 268435456, 268435456)` | 316 |
| product | `(268435456, 134217728, 268435456)` | 316 |
| product | `(268435456, 536870912, 536870912)` | 256 |
| product | `(536870912, 268435456, 536870912)` | 256 |
| product | `(536870912, 1073741824, 1073741824)` | 217 |
| product | `(1073741824, 536870912, 1073741824)` | 217 |
| product | `(1073741824, 2147483648, 2147483648)` | 157 |
| product | `(2147483648, 1073741824, 2147483648)` | 157 |
| product | `(2147483648, 4294967296, 4294967296)` | 97 |
| product | `(4294967296, 2147483648, 4294967296)` | 97 |
| product | `(4294967296, 8589934592, 8589934592)` | 67 |
| product | `(8589934592, 4294967296, 8589934592)` | 67 |
| product | `(8589934592, 9605400609, 9605400609)` | 67 |
| product | `(9605400609, 8589934592, 9605400609)` | 67 |
| product | `(9605400609, 9605400609, 19210801217)` | 67 |
| transform | `(24,)` | 61 |
| transform | `(48,)` | 61 |
| transform | `(64,)` | 61 |
| transform | `(4294967296,)` | 61 |
| transform | `(6442450944,)` | 61 |
| adaptive-apply | `(352, 127, 384, 1)` | 89 |
| adaptive-apply | `(480, 127, 384, 1)` | 89 |
| adaptive-apply | `(736, 255, 768, 1)` | 100 |
| adaptive-apply | `(992, 255, 768, 1)` | 100 |
| adaptive-apply | `(1504, 511, 1536, 1)` | 90 |
| adaptive-apply | `(2016, 511, 1536, 1)` | 90 |
| adaptive-apply | `(3040, 1023, 3072, 1)` | 101 |
| adaptive-apply | `(4064, 1023, 3072, 1)` | 101 |
| adaptive-apply | `(6112, 2047, 6144, 1)` | 112 |
| adaptive-apply | `(10208, 4095, 6144, 1)` | 112 |
| adaptive-apply | `(14304, 4095, 12288, 1)` | 123 |
| adaptive-apply | `(22496, 8191, 24576, 1)` | 134 |
| adaptive-apply | `(30688, 8191, 24576, 1)` | 134 |
| adaptive-apply | `(47072, 16383, 49152, 1)` | 145 |
| adaptive-apply | `(79840, 32767, 49152, 1)` | 145 |
| adaptive-apply | `(145376, 65535, 98304, 1)` | 156 |
| adaptive-apply | `(210912, 65535, 196608, 1)` | 167 |
| adaptive-apply | `(341984, 131071, 393216, 1)` | 157 |
| adaptive-apply | `(604128, 262143, 393216, 1)` | 157 |
| adaptive-apply | `(1128416, 524287, 786432, 1)` | 168 |
| adaptive-apply | `(1652704, 524287, 1572864, 1)` | 179 |
| adaptive-apply | `(2701280, 1048575, 3145728, 1)` | 190 |
| adaptive-apply | `(3749856, 1048575, 3145728, 1)` | 190 |
| adaptive-apply | `(5847008, 2097151, 6291456, 1)` | 201 |
| adaptive-apply | `(7944160, 2097151, 6291456, 1)` | 201 |
| adaptive-apply | `(12138464, 4194303, 12582912, 1)` | 212 |
| adaptive-apply | `(16332768, 4194303, 12582912, 1)` | 212 |
| adaptive-apply | `(24721376, 8388607, 25165824, 1)` | 223 |
| adaptive-apply | `(41498592, 16777215, 25165824, 1)` | 223 |
| adaptive-apply | `(58275808, 16777215, 50331648, 1)` | 234 |
| adaptive-apply | `(91830240, 33554431, 100663296, 1)` | 224 |
| adaptive-apply | `(125384672, 33554431, 100663296, 1)` | 224 |
| adaptive-apply | `(192493536, 67108863, 201326592, 1)` | 235 |
| adaptive-apply | `(326711264, 134217727, 201326592, 1)` | 235 |
| adaptive-apply | `(595146720, 268435455, 402653184, 1)` | 246 |
| adaptive-apply | `(1132017632, 536870911, 805306368, 1)` | 257 |
| adaptive-apply | `(2205759456, 1073741823, 1610612736, 1)` | 268 |
| adaptive-apply | `(3279501280, 1073741823, 3221225472, 1)` | 279 |
| adaptive-apply | `(5426984928, 2147483647, 6442450944, 1)` | 290 |
| adaptive-apply | `(7574468576, 2147483647, 6442450944, 1)` | 290 |
| adaptive-apply | `(9721952224, 2147483647, 6442450944, 2)` | 301 |
| adaptive-apply | `(11869435872, 2147483647, 12884901888, 1)` | 301 |
| adaptive-apply | `(14016919520, 2147483647, 12884901888, 1)` | 301 |
| adaptive-apply | `(16164403168, 2147483647, 6442450944, 4)` | 301 |
| adaptive-apply | `(18311886816, 2147483647, 6442450944, 4)` | 301 |
| adaptive-apply | `(20459370464, 2147483647, 6442450944, 5)` | 301 |
| adaptive-apply | `(22606854112, 2147483647, 6442450944, 5)` | 301 |
| adaptive-apply | `(24754337760, 2147483647, 6442450944, 6)` | 301 |
| adaptive-apply | `(26901821408, 2147483647, 6442450944, 6)` | 301 |
| adaptive-apply | `(29049305056, 2147483647, 6442450944, 7)` | 301 |
| adaptive-apply | `(31196788704, 2147483647, 6442450944, 7)` | 301 |
| adaptive-apply | `(33344272352, 2147483647, 12884901888, 3)` | 301 |
| adaptive-apply | `(35491756000, 2147483647, 6442450944, 8)` | 301 |
| adaptive-apply | `(37639239648, 2147483647, 6442450944, 9)` | 301 |
| adaptive-apply | `(39786723296, 2147483647, 6442450944, 9)` | 301 |
| adaptive-apply | `(41934206944, 2147483647, 12884901888, 4)` | 301 |
| adaptive-apply | `(44081690592, 2147483647, 12884901888, 4)` | 301 |
| adaptive-apply | `(46229174240, 2147483647, 6442450944, 11)` | 301 |
| adaptive-apply | `(48376657888, 2147483647, 6442450944, 11)` | 301 |
| adaptive-apply | `(50524141536, 2147483647, 12884901888, 5)` | 301 |
| adaptive-apply | `(52671625184, 2147483647, 12884901888, 5)` | 301 |
| adaptive-apply | `(54819108832, 2147483647, 12884901888, 5)` | 301 |
| adaptive-apply | `(56966592480, 2147483647, 6442450944, 13)` | 301 |
| adaptive-apply | `(59114076128, 2147483647, 12884901888, 6)` | 301 |
| adaptive-apply | `(61261559776, 2147483647, 12884901888, 6)` | 301 |
| adaptive-apply | `(63409043424, 2147483647, 12884901888, 6)` | 301 |
| adaptive-apply | `(65556527072, 2147483647, 12884901888, 6)` | 301 |
| adaptive-apply | `(67704010720, 2147483647, 12884901888, 7)` | 301 |
| adaptive-apply | `(69851494368, 2147483647, 12884901888, 7)` | 301 |
| adaptive-apply | `(71998978016, 2147483647, 12884901888, 7)` | 301 |
| adaptive-apply | `(74146461664, 2147483647, 12884901888, 7)` | 301 |
| adaptive-apply | `(76293945312, 2147483647, 12884901888, 7)` | 301 |
| **planner total** | | **78,043** |

Each row charges key decoding, construction of every admissible length, comparisons, and insertion of the selected immutable plan. No plan-count allowance remains.

### 6.1.3 Offline literal generation

The offline row is generated by `offline_components()`: 202 input literals of 64 hexadecimal digits, the named field-operation and bit-step loops, the named word-operation loops, 211 output literals of 64 digits, and one 16-digit output. A hexadecimal digit is one input load, one table load, one shift, one OR and one loop control. The live components are printed in 6.0.1 and sum to 136,785.

### 6.1.4 Primitive-action manifest

| fixed or coefficient family | primitive action | operations per occurrence |
| --- | --- | ---: |
| pool request setup | loads with addresses | 24 |
| pool request setup | stores with addresses | 16 |
| pool request setup | pointer and address updates | 24 |
| pool request setup | comparisons | 12 |
| pool request setup | branches | 12 |
| pool request setup | call and return | 2 |
| pool request setup | alignment word operations | 8 |
| pool request setup | header size and tag operations | 10 |
| pool request setup | statistics counter updates | 8 |
| pool request setup | loop entry and exit | 4 |
| pool examined segment | header load and address | 2 |
| pool examined segment | size load and address | 2 |
| pool examined segment | live flag load and address | 2 |
| pool examined segment | comparisons | 2 |
| pool examined segment | selection branch | 1 |
| pool examined segment | next pointer load and address | 2 |
| pool examined segment | loop update and branch | 2 |
| pool free fixed | loads with addresses | 20 |
| pool free fixed | stores with addresses | 16 |
| pool free fixed | pointer and address updates | 20 |
| pool free fixed | comparisons | 12 |
| pool free fixed | branches | 12 |
| pool free fixed | merge metadata operations | 8 |
| pool free fixed | statistics counter updates | 8 |
| pool free fixed | call and return | 2 |
| pool free fixed | loop entry update and exit | 7 |
| slab request setup | class lookup and address | 2 |
| slab request setup | slot table pointer load and address | 2 |
| slab request setup | entry and size tests | 2 |
| slab request setup | call and return | 2 |
| slab examined slot | slot flag load and address | 2 |
| slab examined slot | free test and branch | 2 |
| slab examined slot | next slot update and branch | 2 |
| slab create slot | capacity test and branch | 2 |
| slab create slot | slot metadata store and address | 2 |
| slab create slot | class capacity update | 1 |
| slab free | class and slot decode | 2 |
| slab free | slot flag load and address | 2 |
| slab free | live test and branch | 2 |
| slab free | slot flag store and address | 2 |
| slab free | statistics update | 1 |
| slab free | call and return | 2 |
| stage bookkeeping | sixty four field word transfers | 384 |
| stage bookkeeping | forty eight integer word transfers | 192 |
| stage bookkeeping | sixty four stage control steps | 256 |
| stage bookkeeping | thirty two call edges | 64 |
| stage bookkeeping | twenty six loop steps | 104 |
| base entry | six remainder array bindings | 24 |
| base entry | four matrix array bindings | 16 |
| base entry | eight degree budget fields | 24 |
| base entry | six call frame fields | 18 |
| base entry | four entry tests | 8 |
| base step setup | eight quotient fields | 32 |
| base step setup | six remainder row fields | 24 |
| base step setup | five degree tests | 10 |
| base step setup | five call edges | 10 |
| base remainder coefficient | a load | 1 |
| base remainder coefficient | a address | 1 |
| base remainder coefficient | b load | 1 |
| base remainder coefficient | b address | 1 |
| base remainder coefficient | q0 multiplication | 1 |
| base remainder coefficient | q1 multiplication | 1 |
| base remainder coefficient | first subtraction | 1 |
| base remainder coefficient | second subtraction | 1 |
| base remainder coefficient | result store | 1 |
| base remainder coefficient | result address | 1 |
| base remainder coefficient | loop update | 1 |
| base remainder coefficient | loop test | 1 |
| base remainder coefficient | loop branch | 1 |
| base matrix coefficient | matrix load | 1 |
| base matrix coefficient | matrix address | 1 |
| base matrix coefficient | other entry load | 1 |
| base matrix coefficient | other entry address | 1 |
| base matrix coefficient | field multiplication | 1 |
| base matrix coefficient | field addition | 1 |
| base matrix coefficient | matrix store | 1 |
| base matrix coefficient | store address | 1 |
| base matrix coefficient | loop control | 1 |
| base step close | two close tests | 4 |
| base step close | two close calls | 4 |
| base final setup | five final field bindings | 15 |
| base final setup | five final tests | 10 |
| base final close | one final test | 2 |
| base final close | one final call | 2 |
| direct point | operand a address | 1 |
| direct point | operand a load | 1 |
| direct point | operand b address | 1 |
| direct point | operand b load | 1 |
| direct point | matrix r11 address | 1 |
| direct point | matrix r11 load | 1 |
| direct point | matrix r12 address | 1 |
| direct point | matrix r12 load | 1 |
| direct point | matrix r21 address | 1 |
| direct point | matrix r21 load | 1 |
| direct point | matrix r22 address | 1 |
| direct point | matrix r22 load | 1 |
| direct point | first field multiply | 1 |
| direct point | second field multiply | 1 |
| direct point | third field multiply | 1 |
| direct point | fourth field multiply | 1 |
| direct point | first output add subtract | 1 |
| direct point | second output add subtract | 1 |
| direct point | output c store | 1 |
| direct point | output d store | 1 |
| direct placement | source address | 1 |
| direct placement | source load | 1 |
| direct placement | destination address | 1 |
| direct placement | destination store | 1 |
| direct placement | destination pointer update | 1 |
| driver entry | sixty four field word transfers | 384 |
| driver entry | forty eight integer word transfers | 192 |
| driver entry | sixty four stage control steps | 256 |
| driver entry | thirty two call edges | 64 |
| driver entry | twenty six loop steps | 104 |
| driver entry | trial counter load and address | 2 |
| driver entry | counter increment | 1 |
| driver entry | limit load and address | 2 |
| driver entry | limit comparison | 1 |
| driver entry | loop branch | 1 |
| driver entry | close call and return | 2 |
| driver entry | stage pointer updates | 3 |
| driver exit | normalization field loads with addresses | 20 |
| driver exit | normalization field stores with addresses | 16 |
| driver exit | normalization field operations | 24 |
| driver exit | normalization pointer updates | 12 |
| driver exit | normalization comparisons | 8 |
| driver exit | normalization branches | 8 |
| driver exit | normalization calls and returns | 4 |
| driver exit | normalization loop updates tests and exit | 15 |
| plan dispatch | operand and output pointer bindings | 8 |
| plan dispatch | length and window loads | 6 |
| plan dispatch | plan tag tests and branches | 5 |
| plan dispatch | call and return | 4 |
| call close | entry and argument bindings | 12 |
| call close | length tests and branches | 10 |
| call close | pointer updates | 8 |
| call close | calls and returns | 8 |
| call close | closing tests | 4 |
| product fixed | plan operand and output pointer bindings | 8 |
| product fixed | plan length and window loads | 6 |
| product fixed | plan plan tag tests and branches | 5 |
| product fixed | plan call and return | 4 |
| product fixed | product call and return | 6 |
| g correlation | source row base and address | 2 |
| g correlation | destination row base and address | 2 |
| g correlation | chirp pointer and address | 2 |
| g correlation | kernel pointer and address | 2 |
| g correlation | source load and address | 2 |
| g correlation | destination store and address | 2 |
| g correlation | chirp load and multiply | 2 |
| g correlation | loop index and branch | 2 |
| q correlation | six row base address pairs | 12 |
| q correlation | four chirp kernel pointer pairs | 8 |
| q correlation | six source load address pairs | 12 |
| q correlation | six destination store address pairs | 12 |
| q correlation | four field multiply accumulates | 8 |
| q correlation | four index bound updates | 4 |
| q correlation | call return and tail tests | 4 |
| interpolation length | eight source load address pairs | 16 |
| interpolation length | eight destination store address pairs | 16 |
| interpolation length | six chirp field operations | 6 |
| interpolation length | four pointer updates | 4 |
| interpolation length | four loop controls | 4 |
| interpolation length | two calls and two returns | 4 |
| interpolation coset | eight source load address pairs | 16 |
| interpolation coset | eight destination store address pairs | 16 |
| interpolation coset | six chirp field operations | 6 |
| interpolation coset | four pointer updates | 4 |
| interpolation coset | four loop controls | 4 |
| interpolation coset | two calls and two returns | 4 |
| allocation/zero | sixteen zero store address pairs | 32 |
| allocation/zero | sixteen source load address pairs | 32 |
| allocation/zero | sixteen destination store address pairs | 32 |
| allocation/zero | eight allocator header updates | 8 |
| allocation/zero | eight pointer updates | 8 |
| allocation/zero | eight bound tests and branches | 8 |
| allocation/zero | four calls and four returns | 8 |
| stage-C misc | ten bookkeeping sixty four field word transfers | 3,840 |
| stage-C misc | ten bookkeeping forty eight integer word transfers | 1,920 |
| stage-C misc | ten bookkeeping sixty four stage control steps | 2,560 |
| stage-C misc | ten bookkeeping thirty two call edges | 640 |
| stage-C misc | ten bookkeeping twenty six loop steps | 1,040 |
| omega table entry | two source words | 4 |
| omega table entry | one power step | 1 |
| omega table entry | one destination | 2 |
| omega table entry | sixteen bit reversal steps | 16 |
| omega table entry | entry and loop close | 2 |
| omega boundary | four row factors | 12 |
| batch coefficient | prefix address | 1 |
| batch coefficient | prefix load | 1 |
| batch coefficient | value address | 1 |
| batch coefficient | value load | 1 |
| batch coefficient | prefix multiply | 1 |
| batch coefficient | prefix store | 1 |
| batch coefficient | backward prefix load | 1 |
| batch coefficient | backward value load | 1 |
| batch coefficient | first backward multiply | 1 |
| batch coefficient | second backward multiply | 1 |
| batch coefficient | field negation | 1 |
| batch coefficient | inverse store | 1 |
| batch coefficient | loop update | 1 |
| batch coefficient | loop branch | 1 |
| batch chunk | chunk entry and zero test | 3 |
| batch chunk | chunk bounds | 3 |
| batch chunk | chunk pointer setup | 6 |
| batch chunk | chunk inversion call | 4 |
| batch chunk | chunk close | 4 |
| adaptive copy coefficient | source address | 1 |
| adaptive copy coefficient | source load | 1 |
| adaptive copy coefficient | destination address | 1 |
| adaptive copy coefficient | destination store | 1 |
| adaptive copy coefficient | source pointer update | 1 |
| adaptive copy coefficient | destination pointer update | 1 |
| adaptive copy coefficient | loop update | 1 |
| adaptive zero coefficient | destination address | 1 |
| adaptive zero coefficient | destination store | 1 |
| adaptive zero coefficient | destination pointer update | 1 |
| adaptive zero coefficient | loop comparison | 1 |
| adaptive zero coefficient | loop branch | 1 |
| adaptive fold coefficient | source address | 1 |
| adaptive fold coefficient | source load | 1 |
| adaptive fold coefficient | destination address | 1 |
| adaptive fold coefficient | destination load | 1 |
| adaptive fold coefficient | field add | 1 |
| adaptive fold coefficient | destination store | 1 |
| adaptive fold coefficient | source pointer update | 1 |
| adaptive fold coefficient | destination pointer update | 1 |
| adaptive fold coefficient | loop comparison | 1 |
| adaptive fold coefficient | loop branch | 1 |
| adaptive fixed point | operand a address | 1 |
| adaptive fixed point | operand a load | 1 |
| adaptive fixed point | operand b address | 1 |
| adaptive fixed point | operand b load | 1 |
| adaptive fixed point | matrix r11 address | 1 |
| adaptive fixed point | matrix r11 load | 1 |
| adaptive fixed point | matrix r12 address | 1 |
| adaptive fixed point | matrix r12 load | 1 |
| adaptive fixed point | matrix r21 address | 1 |
| adaptive fixed point | matrix r21 load | 1 |
| adaptive fixed point | matrix r22 address | 1 |
| adaptive fixed point | matrix r22 load | 1 |
| adaptive fixed point | first field multiply | 1 |
| adaptive fixed point | second field multiply | 1 |
| adaptive fixed point | third field multiply | 1 |
| adaptive fixed point | fourth field multiply | 1 |
| adaptive fixed point | first output add subtract | 1 |
| adaptive fixed point | second output add subtract | 1 |
| adaptive fixed point | output c address | 1 |
| adaptive fixed point | output c store | 1 |
| adaptive fixed point | output d address | 1 |
| adaptive fixed point | output d store | 1 |
| adaptive fixed point | output c pointer update | 1 |
| adaptive fixed point | output d pointer update | 1 |
| adaptive placement coefficient | source address | 1 |
| adaptive placement coefficient | source load | 1 |
| adaptive placement coefficient | scale load | 1 |
| adaptive placement coefficient | field multiply | 1 |
| adaptive placement coefficient | destination address | 1 |
| adaptive placement coefficient | destination store | 1 |
| adaptive placement coefficient | destination pointer update | 1 |
| adaptive placement coefficient | loop update | 1 |
| adaptive placement close | counter load | 1 |
| adaptive placement close | comparison | 1 |
| adaptive placement close | branch | 1 |
| adaptive placement close | call | 1 |
| adaptive placement close | return | 1 |
| adaptive slot placement close | four output fragments | 20 |
| adaptive entry | ten entry records | 80 |
| adaptive scale plan | sixty four scale records | 448 |
| adaptive length check | eleven length checks | 22 |
| adaptive slot control | counter update | 1 |
| adaptive slot control | comparison | 1 |
| adaptive slot control | branch | 1 |
| adaptive call close | status load | 1 |
| adaptive call close | status store | 1 |
| adaptive call close | counter update | 1 |
| adaptive call close | comparison | 1 |
| adaptive call close | branch | 1 |
| adaptive call close | return | 1 |
| adaptive planner candidate | exponent load | 1 |
| adaptive planner candidate | point count compute | 1 |
| adaptive planner candidate | matrix limit load | 1 |
| adaptive planner candidate | matrix limit comparison | 1 |
| adaptive planner candidate | direct limit comparison | 1 |
| adaptive planner candidate | slot compute | 1 |
| adaptive planner candidate | candidate store | 1 |
| adaptive planner candidate | counter update | 1 |
| adaptive planner close | six winner records | 18 |
| adaptive allocator request | one request statement | 1 |
| adaptive allocator request | twelve request records | 120 |
| adaptive allocator segment | header address | 1 |
| adaptive allocator segment | header load | 1 |
| adaptive allocator segment | size address | 1 |
| adaptive allocator segment | size load | 1 |
| adaptive allocator segment | live flag address | 1 |
| adaptive allocator segment | live flag load | 1 |
| adaptive allocator segment | first comparison | 1 |
| adaptive allocator segment | second comparison | 1 |
| adaptive allocator segment | selection branch | 1 |
| adaptive allocator segment | next pointer address | 1 |
| adaptive allocator segment | next pointer load | 1 |
| adaptive allocator segment | loop update | 1 |
| adaptive allocator segment | loop branch | 1 |
| adaptive allocator free | fifteen free records | 105 |
| adaptive allocator find | header address | 1 |
| adaptive allocator find | header load | 1 |
| adaptive allocator find | name comparison | 1 |
| adaptive allocator find | live comparison | 1 |
| adaptive allocator find | pointer update | 1 |
| adaptive allocator find | branch | 1 |
| adaptive allocator merge | first header load | 1 |
| adaptive allocator merge | second header load | 1 |
| adaptive allocator merge | live comparison | 1 |
| adaptive allocator merge | size add | 1 |
| adaptive allocator merge | header store | 1 |
| adaptive allocator merge | pointer update | 1 |
| adaptive allocator merge | branch | 1 |
| adaptive allocator release | tail load | 1 |
| adaptive allocator release | live comparison | 1 |
| adaptive allocator release | extent store | 1 |
| adaptive allocator release | pointer update | 1 |
| adaptive allocator release | branch | 1 |
| outer division coefficient | two loads with addresses | 4 |
| outer division coefficient | two field multiplications | 2 |
| outer division coefficient | two field subtractions | 2 |
| outer division coefficient | one store with address | 2 |
| outer division coefficient | loop counter test and branch | 3 |
| outer division coefficient | if k test and branch | 2 |
| outer quotient test | quotient degree comparison | 1 |
| outer quotient test | abort branch | 1 |
| outer driver fixed | addressed pair and degree loads | 16 |
| outer driver fixed | addressed pair stores | 8 |
| outer driver fixed | pair pointer updates | 12 |
| outer driver fixed | comparisons | 4 |
| outer driver fixed | branches | 4 |
| outer driver fixed | calls and returns | 6 |
| outer driver fixed | two one item loop controls | 16 |
| schoolbook coefficient | four loads with addresses | 8 |
| schoolbook coefficient | two field multiplications | 2 |
| schoolbook coefficient | two field additions | 2 |
| schoolbook coefficient | accumulator load and store with addresses | 4 |
| schoolbook coefficient | two pointer updates | 2 |
| schoolbook coefficient | counter test and branch | 3 |
| schoolbook coefficient | coefficient bound test | 1 |
| schoolbook row | six loads with addresses | 12 |
| schoolbook row | two stores with addresses | 4 |
| schoolbook row | two pointer updates | 2 |
| schoolbook row | test and branch | 2 |
| schoolbook fixed | argument loads with addresses | 16 |
| schoolbook fixed | result pointer stores with addresses | 8 |
| schoolbook fixed | length and bound word operations | 12 |
| schoolbook fixed | comparisons | 8 |
| schoolbook fixed | branches | 8 |
| schoolbook fixed | call and return | 2 |
| schoolbook fixed | loop entry and exit | 10 |
| stage E point | three loads with addresses | 6 |
| stage E point | field multiplication | 1 |
| stage E point | store with address | 2 |
| stage E point | pointer update | 1 |
| stage E point | counter test and branch | 3 |
| stage E point | character and zero tests | 3 |
| stage E division fixed | coefficient and degree loads | 8 |
| stage E division fixed | quotient stores with addresses | 4 |
| stage E division fixed | field operations | 5 |
| stage E division fixed | pointer updates | 4 |
| stage E division fixed | comparisons and branches | 4 |
| stage E division fixed | calls and returns | 2 |
| stage E round close | split choice loads with addresses | 16 |
| stage E round close | split choice stores with addresses | 8 |
| stage E round close | degree and zero comparisons | 8 |
| stage E round close | branches | 8 |
| stage E round close | pointer updates | 8 |
| stage E round close | calls and returns | 4 |
| stage E round close | loop updates tests and exit | 12 |
| stage E shift | eight loads with addresses | 16 |
| stage E shift | eight stores with addresses | 16 |
| stage E driver | random word and reduction | 31 |
| stage E driver | zero replacement test and branch | 7 |
| stage E driver | three polynomial call pairs | 6 |
| stage E driver | degree selection loads with addresses | 12 |
| stage E driver | degree comparisons and branches | 12 |
| stage E driver | pointer updates | 12 |
| stage E driver | round counter update test branch | 3 |
| stage E driver | allocator mark updates | 8 |
| stage E driver | round entry and exit | 4 |
| field operation with memory | two operand loads with addresses | 4 |
| field operation with memory | field operation | 1 |
| field operation with memory | result store with address | 2 |
| field operation with memory | call and loop control | 3 |
| Tonelli control | thirty two outer rounds | 256 |
| Tonelli control | five hundred twenty eight scan steps | 4,224 |
| Tonelli control | four hundred ninety six update steps | 4,960 |
| Tonelli control | two hundred fifty three exponent steps | 1,265 |
| Tonelli control | thirty three table entries | 132 |
| reference verification | sixty four canonical input bytes | 1,024 |
| reference verification | sixty four message copy bytes | 768 |
| reference verification | three state words | 48 |
| reference verification | ten round wrapper steps | 340 |
| reference verification | thirty two digest bytes | 384 |
| reference verification | two final message checks | 16 |
| init close | loads with addresses | 4 |
| init close | stores with addresses | 4 |
| init close | pointer updates | 3 |
| init close | comparisons | 2 |
| init close | branches | 2 |
| init close | call and return | 2 |
| setup close | loads with addresses | 32 |
| setup close | stores with addresses | 24 |
| setup close | field operations | 16 |
| setup close | pointer updates | 12 |
| setup close | comparisons | 6 |
| setup close | branches | 6 |
| setup close | calls and returns | 2 |
| setup close | loop updates and exits | 5 |
| sampler control | word loads with addresses | 16 |
| sampler control | conditional subtraction field actions | 12 |
| sampler control | comparisons | 12 |
| sampler control | branches | 12 |
| sampler control | pointer updates | 12 |
| sampler control | counter updates | 8 |
| sampler control | calls and returns | 4 |
| sampler control | stores with addresses | 8 |
| sampler control | entry and exit | 13 |
| output call | loads with addresses | 20 |
| output call | stores with addresses | 16 |
| output call | encoding word operations | 16 |
| output call | pointer updates | 10 |
| output call | comparisons | 6 |
| output call | branches | 4 |
| output call | calls and returns | 4 |
| output call | loop updates and exits | 4 |
| offline hexadecimal digit | input load | 1 |
| offline hexadecimal digit | lookup table load | 1 |
| offline hexadecimal digit | shift | 1 |
| offline hexadecimal digit | or | 1 |
| offline hexadecimal digit | loop control | 1 |
| offline field operations | constant two | 1 |
| offline field operations | montgomery R squarings | 8 |
| offline field operations | montgomery R squared | 1 |
| offline field operations | organizer constant conversions | 201 |
| offline field operations | capacity constant | 8 |
| offline field operations | constant five | 2 |
| offline field operations | Tonelli generator power | 268 |
| offline bit steps | Tonelli generator exponent squarings | 222 |
| offline word operations | p minus one | 4 |
| offline word operations | odd part shift | 12 |
| offline word operations | q plus one over two | 16 |
| offline word operations | p minus one over two | 12 |
| offline word operations | p minus two | 4 |
| offline word operations | inverse fifth exponent | 26 |
| offline word operations | Montgomery word inverse | 16 |

Every coefficient and fixed row in sections 6.1 and 6.2 is a sum of the named primitive actions above. The ledger asserts the family sums before multiplying them by their live loop counts.

The following generated sweep checks the I/O actions of every fused or transform-point kernel used by stages B, C and D. Counts are per block, four-lane boundary, node point or apply output as named. The direct two-output row's two stores reuse the charged operand addresses. The active adaptive fixed row names six loads, two output stores and their separate addresses inside its own 24-action multiset.

| stage | kernel | primitive actions | loads | output stores |
| --- | --- | ---: | ---: | ---: |
| B/C/D | transform-block-width-1 | 10 | 2 | 2 |
| B/C/D | transform-block-width-2 | 23 | 4 | 4 |
| B/C/D | transform-block-width-3 | 55 | 8 | 8 |
| B/C/D | transform-block-width-4 | 131 | 16 | 16 |
| B/C/D | transform-block-width-5 | 307 | 32 | 32 |
| B/C/D | transform-block-width-6 | 707 | 64 | 64 |
| B/C/D | transform-block-width-7 | 1,603 | 128 | 128 |
| D | node-simple-point | 7 | 2 | 1 |
| D | node-extended-point | 10 | 3 | 1 |
| D | direct-two-output-point | 20 | 6 | 2 |
| C | O1-four-lane-boundary | 46 | 8 | 4 |
| C | O2-four-lane-boundary | 63 | 13 | 4 |
| C | product-point | 10 | 3 | 1 |
| Stage D | adaptive-fixed-two-output-point | 24 | 6 | 2 |

### 6.2 Stage D expansion and explicit lower-order count

| j | children | top rows | returned rows | apply pointwise | matrix pointwise | inverses | CRT | pseudo | arrays | fixed | node total |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 210,280 | 25,237 | 35,296 | 6,876 | 9,168 | 32,322 | 3,336 | 2,064 | 3,588 | 210 | 328,377 |
| 8 | 656,754 | 46,671 | 31,208 | 13,692 | 18,256 | 53,232 | 6,664 | 4,112 | 7,172 | 210 | 837,971 |
| 9 | 1,675,942 | 95,779 | 65,624 | 27,324 | 36,432 | 113,790 | 13,320 | 8,208 | 14,340 | 210 | 2,050,969 |
| 10 | 4,101,938 | 188,541 | 127,184 | 54,588 | 72,784 | 218,508 | 26,632 | 16,400 | 28,676 | 210 | 4,835,461 |
| 11 | 9,670,922 | 377,047 | 254,280 | 109,116 | 145,488 | 436,890 | 53,256 | 32,784 | 57,348 | 210 | 11,137,341 |
| 12 | 22,274,682 | 762,321 | 519,488 | 218,172 | 290,896 | 898,440 | 106,504 | 65,552 | 114,692 | 210 | 25,250,957 |
| 13 | 50,501,914 | 1,549,003 | 1,071,416 | 436,284 | 581,712 | 1,869,942 | 213,000 | 131,088 | 229,380 | 210 | 56,583,949 |
| 14 | 113,167,898 | 3,158,277 | 2,223,152 | 872,508 | 1,163,344 | 3,920,676 | 425,992 | 262,160 | 458,756 | 210 | 125,652,973 |
| 15 | 251,305,946 | 6,446,911 | 4,620,072 | 1,744,956 | 2,326,608 | 8,232,402 | 851,976 | 524,304 | 917,508 | 210 | 276,970,893 |
| 16 | 553,941,786 | 13,873,533 | 10,546,384 | 3,489,852 | 4,653,136 | 19,403,934 | 1,703,944 | 1,048,592 | 1,835,012 | 210 | 610,496,383 |
| 17 | 1,220,992,766 | 28,280,119 | 21,803,464 | 6,979,644 | 9,306,192 | 40,406,988 | 3,407,880 | 2,097,168 | 3,670,020 | 210 | 1,336,944,451 |
| 18 | 2,673,888,902 | 57,639,153 | 45,045,440 | 13,959,228 | 18,612,304 | 84,050,682 | 6,815,752 | 4,194,320 | 7,340,036 | 210 | 2,911,546,027 |
| 19 | 5,823,092,054 | 117,449,899 | 92,986,296 | 27,918,396 | 37,224,528 | 174,616,104 | 13,631,496 | 8,388,624 | 14,680,068 | 210 | 6,309,987,675 |
| 20 | 12,619,975,350 | 239,429,733 | 192,012,464 | 55,836,732 | 74,448,976 | 362,821,974 | 27,262,984 | 16,777,232 | 29,360,132 | 210 | 13,617,925,787 |
| 21 | 27,235,851,574 | 487,935,007 | 396,125,608 | 111,673,404 | 148,897,872 | 752,870,532 | 54,525,960 | 33,554,448 | 58,720,260 | 210 | 29,280,154,875 |
| 22 | 58,560,309,750 | 994,037,721 | 816,474,784 | 223,346,748 | 297,795,664 | 1,560,244,146 | 109,051,912 | 67,108,880 | 117,440,516 | 210 | 62,745,810,331 |
| 23 | 125,491,620,662 | 2,113,688,599 | 1,800,433,736 | 446,693,436 | 595,591,248 | 3,497,327,742 | 218,103,816 | 134,217,744 | 234,881,028 | 210 | 134,532,558,221 |
| 24 | 269,065,116,442 | 4,297,349,073 | 3,694,163,264 | 893,386,812 | 1,191,182,416 | 7,204,571,052 | 436,207,624 | 268,435,472 | 469,762,052 | 210 | 287,520,174,417 |
| 25 | 575,040,348,834 | 8,734,661,515 | 7,574,944,312 | 1,786,773,564 | 2,382,364,752 | 14,829,032,154 | 872,415,240 | 536,870,928 | 939,524,100 | 210 | 612,696,935,609 |
| 26 | 1,225,393,871,218 | 17,760,280,389 | 15,537,831,728 | 3,573,547,068 | 4,764,729,424 | 30,530,936,328 | 1,744,830,472 | 1,073,741,840 | 1,879,048,196 | 210 | 1,302,258,816,873 |
| 27 | 2,604,517,633,746 | 36,102,497,023 | 31,851,578,408 | 7,147,094,076 | 9,529,458,768 | 62,807,681,334 | 3,489,660,936 | 2,147,483,664 | 3,758,096,388 | 210 | 2,761,351,184,553 |
| 28 | 5,522,702,369,106 | 73,368,889,017 | 65,255,016,736 | 14,294,188,092 | 19,058,917,456 | 129,107,047,524 | 6,979,321,864 | 4,294,967,312 | 7,516,192,772 | 210 | 5,842,576,910,089 |
| 29 | 11,685,153,820,178 | 149,065,591,411 | 133,613,784,600 | 28,588,376,124 | 38,117,834,832 | 265,197,535,122 | 13,958,643,720 | 8,589,934,608 | 15,032,385,540 | 210 | 12,337,317,906,345 |
| 30 | 24,674,635,812,690 | 314,035,957,425 | 288,433,935,296 | 57,176,752,188 | 76,235,669,584 | 578,109,394,014 | 27,917,287,432 | 17,179,869,200 | 30,064,771,076 | 210 | 26,063,789,449,115 |
| 31 | 52,127,578,898,230 | 637,030,920,811 | 588,813,211,832 | 114,353,504,316 | 152,471,339,088 | 1,183,095,805,836 | 55,834,574,856 | 34,359,738,384 | 60,129,542,148 | 210 | 54,953,667,535,711 |

| step | degree | j | budget | node | apply points | apply | post-node length | linear division | quotient test | other driver | total |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 76,293,945,312 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 29,874,354,891,360 | 74,146,461,665 | 1,112,196,924,975 | 2 | 63,350,769,063 | 86,003,570,121,111 |
| 2 | 74,146,461,664 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 29,819,951,972,288 | 71,998,978,017 | 1,079,984,670,255 | 2 | 63,350,769,063 | 85,916,954,947,319 |
| 3 | 71,998,978,016 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 29,765,549,053,200 | 69,851,494,369 | 1,047,772,415,535 | 2 | 63,350,769,063 | 85,830,339,773,511 |
| 4 | 69,851,494,368 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 29,711,146,134,112 | 67,704,010,721 | 1,015,560,160,815 | 2 | 63,350,769,063 | 85,743,724,599,703 |
| 5 | 67,704,010,720 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 29,656,743,215,040 | 65,556,527,073 | 983,347,906,095 | 2 | 63,350,769,063 | 85,657,109,425,911 |
| 6 | 65,556,527,072 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 26,069,668,915,002 | 63,409,043,425 | 951,135,651,375 | 2 | 63,350,769,063 | 82,037,822,871,153 |
| 7 | 63,409,043,424 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 26,015,265,995,914 | 61,261,559,777 | 918,923,396,655 | 2 | 63,350,769,063 | 81,951,207,697,345 |
| 8 | 61,261,559,776 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 25,960,863,076,826 | 59,114,076,129 | 886,711,141,935 | 2 | 63,350,769,063 | 81,864,592,523,537 |
| 9 | 59,114,076,128 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 25,906,460,157,754 | 56,966,592,481 | 854,498,887,215 | 2 | 63,350,769,063 | 81,777,977,349,745 |
| 10 | 56,966,592,480 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 25,586,731,570,476 | 54,819,108,833 | 822,286,632,495 | 2 | 63,350,769,063 | 81,426,036,507,747 |
| 11 | 54,819,108,832 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 22,264,982,938,628 | 52,671,625,185 | 790,074,377,775 | 2 | 63,350,769,063 | 78,072,075,621,179 |
| 12 | 52,671,625,184 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 22,210,580,019,540 | 50,524,141,537 | 757,862,123,055 | 2 | 63,350,769,063 | 77,985,460,447,371 |
| 13 | 50,524,141,536 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 22,156,177,100,468 | 48,376,657,889 | 725,649,868,335 | 2 | 63,350,769,063 | 77,898,845,273,579 |
| 14 | 48,376,657,888 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 21,892,490,747,320 | 46,229,174,241 | 693,437,613,615 | 2 | 63,350,769,063 | 77,602,946,665,711 |
| 15 | 46,229,174,240 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 21,838,087,828,232 | 44,081,690,593 | 661,225,358,895 | 2 | 63,350,769,063 | 77,516,331,491,903 |
| 16 | 44,081,690,592 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 18,460,296,962,254 | 41,934,206,945 | 629,013,104,175 | 2 | 63,350,769,063 | 74,106,328,371,205 |
| 17 | 41,934,206,944 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 18,405,894,043,182 | 39,786,723,297 | 596,800,849,455 | 2 | 63,350,769,063 | 74,019,713,197,413 |
| 18 | 39,786,723,296 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 18,198,249,924,164 | 37,639,239,649 | 564,588,594,735 | 2 | 63,350,769,063 | 73,779,856,823,675 |
| 19 | 37,639,239,648 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 18,143,847,005,076 | 35,491,756,001 | 532,376,340,015 | 2 | 63,350,769,063 | 73,693,241,649,867 |
| 20 | 35,491,756,000 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 16,351,129,512,578 | 33,344,272,353 | 500,164,085,295 | 2 | 63,350,769,063 | 71,868,311,902,649 |
| 21 | 33,344,272,352 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 14,655,610,985,896 | 31,196,788,705 | 467,951,830,575 | 2 | 63,350,769,063 | 70,140,581,121,247 |
| 22 | 31,196,788,704 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 14,504,009,100,992 | 29,049,305,057 | 435,739,575,855 | 2 | 63,350,769,063 | 69,956,766,981,623 |
| 23 | 29,049,305,056 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 14,449,606,181,920 | 26,901,821,409 | 403,527,321,135 | 2 | 63,350,769,063 | 69,870,151,807,831 |
| 24 | 26,901,821,408 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 12,656,888,689,422 | 24,754,337,761 | 371,315,066,415 | 2 | 63,350,769,063 | 68,045,222,060,613 |
| 25 | 24,754,337,760 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 12,602,485,770,334 | 22,606,854,113 | 339,102,811,695 | 2 | 63,350,769,063 | 67,958,606,886,805 |
| 26 | 22,606,854,112 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 10,809,768,277,836 | 20,459,370,465 | 306,890,556,975 | 2 | 63,350,769,063 | 66,133,677,139,587 |
| 27 | 20,459,370,464 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 10,755,365,358,748 | 18,311,886,817 | 274,678,302,255 | 2 | 63,350,769,063 | 66,047,061,965,779 |
| 28 | 18,311,886,816 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 8,962,647,866,250 | 16,164,403,169 | 242,466,047,535 | 2 | 63,350,769,063 | 64,222,132,218,561 |
| 29 | 16,164,403,168 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 8,908,244,947,178 | 14,016,919,521 | 210,253,792,815 | 2 | 63,350,769,063 | 64,135,517,044,769 |
| 30 | 14,016,919,520 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 7,087,257,807,479 | 11,869,435,873 | 178,041,538,095 | 2 | 63,350,769,063 | 62,282,317,650,350 |
| 31 | 11,869,435,872 | 31 | 2,147,483,647 | 54,953,667,535,711 | 12,884,901,888 | 7,018,804,470,331 | 9,721,952,225 | 145,829,283,375 | 2 | 63,350,769,063 | 62,181,652,058,482 |
| 32 | 9,721,952,224 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 5,268,407,043,094 | 7,574,468,577 | 113,617,028,655 | 2 | 63,350,769,063 | 60,399,042,376,525 |
| 33 | 7,574,468,576 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 3,488,075,209,615 | 5,426,984,929 | 81,404,773,935 | 2 | 63,350,769,063 | 58,586,498,288,326 |
| 34 | 5,426,984,928 | 31 | 2,147,483,647 | 54,953,667,535,711 | 6,442,450,944 | 3,415,870,812,756 | 3,279,501,281 | 49,192,519,215 | 2 | 63,350,769,063 | 58,482,081,636,747 |
| 35 | 3,279,501,280 | 30 | 1,073,741,823 | 26,063,789,449,115 | 3,221,225,472 | 1,685,604,618,999 | 2,205,759,457 | 33,086,391,855 | 2 | 31,675,385,255 | 27,814,155,845,226 |
| 36 | 2,205,759,456 | 30 | 1,073,741,823 | 26,063,789,449,115 | 1,610,612,736 | 846,042,369,719 | 1,132,017,633 | 16,980,264,495 | 2 | 31,675,385,255 | 26,958,487,468,586 |
| 37 | 1,132,017,632 | 29 | 536,870,911 | 12,337,317,906,345 | 805,306,368 | 400,316,058,305 | 595,146,721 | 8,927,200,815 | 2 | 15,837,693,351 | 12,762,398,858,818 |
| 38 | 595,146,720 | 28 | 268,435,455 | 5,842,576,910,089 | 402,653,184 | 196,606,107,089 | 326,711,265 | 4,900,668,975 | 2 | 7,918,847,399 | 6,052,002,533,554 |
| 39 | 326,711,264 | 27 | 134,217,727 | 2,761,351,184,553 | 201,326,592 | 97,129,303,793 | 192,493,537 | 2,887,403,055 | 2 | 3,959,424,423 | 2,865,327,315,826 |
| 40 | 192,493,536 | 26 | 67,108,863 | 1,302,258,816,873 | 201,326,592 | 91,937,255,765 | 125,384,673 | 1,880,770,095 | 2 | 1,979,712,935 | 1,398,056,555,670 |
| 41 | 125,384,672 | 25 | 33,554,431 | 612,696,935,609 | 100,663,296 | 45,895,876,617 | 91,830,241 | 1,377,453,615 | 2 | 989,857,191 | 660,960,123,034 |
| 42 | 91,830,240 | 25 | 33,554,431 | 612,696,935,609 | 100,663,296 | 44,685,621,197 | 58,275,809 | 874,137,135 | 2 | 989,857,191 | 659,246,551,134 |
| 43 | 58,275,808 | 24 | 16,777,215 | 287,520,174,417 | 50,331,648 | 22,180,329,329 | 41,498,593 | 622,478,895 | 2 | 494,929,319 | 310,817,911,962 |
| 44 | 41,498,592 | 24 | 16,777,215 | 287,520,174,417 | 25,165,824 | 11,286,197,041 | 24,721,377 | 370,820,655 | 2 | 494,929,319 | 299,672,121,434 |
| 45 | 24,721,376 | 23 | 8,388,607 | 134,532,558,221 | 25,165,824 | 10,623,997,349 | 16,332,769 | 244,991,535 | 2 | 247,465,383 | 145,649,012,490 |
| 46 | 16,332,768 | 22 | 4,194,303 | 62,745,810,331 | 12,582,912 | 5,325,562,953 | 12,138,465 | 182,076,975 | 2 | 123,733,415 | 68,377,183,676 |
| 47 | 12,138,464 | 22 | 4,194,303 | 62,745,810,331 | 12,582,912 | 5,161,087,333 | 7,944,161 | 119,162,415 | 2 | 123,733,415 | 68,149,793,496 |
| 48 | 7,944,160 | 21 | 2,097,151 | 29,280,154,875 | 6,291,456 | 2,465,630,971 | 5,847,009 | 87,705,135 | 2 | 61,867,431 | 31,895,358,414 |
| 49 | 5,847,008 | 21 | 2,097,151 | 29,280,154,875 | 6,291,456 | 2,387,837,631 | 3,749,857 | 56,247,855 | 2 | 61,867,431 | 31,786,107,794 |
| 50 | 3,749,856 | 20 | 1,048,575 | 13,617,925,787 | 3,145,728 | 1,186,509,667 | 2,701,281 | 40,519,215 | 2 | 30,934,439 | 14,875,889,110 |
| 51 | 2,701,280 | 20 | 1,048,575 | 13,617,925,787 | 3,145,728 | 1,150,705,536 | 1,652,705 | 24,790,575 | 2 | 30,934,439 | 14,824,356,339 |
| 52 | 1,652,704 | 19 | 524,287 | 6,309,987,675 | 1,572,864 | 565,530,411 | 1,128,417 | 16,926,255 | 2 | 15,467,943 | 6,907,912,286 |
| 53 | 1,128,416 | 19 | 524,287 | 6,309,987,675 | 786,432 | 285,443,739 | 604,129 | 9,061,935 | 2 | 15,467,943 | 6,619,961,294 |
| 54 | 604,128 | 18 | 262,143 | 2,911,546,027 | 393,216 | 139,835,307 | 341,985 | 5,129,775 | 2 | 7,734,695 | 3,064,245,806 |
| 55 | 341,984 | 17 | 131,071 | 1,336,944,451 | 393,216 | 130,245,592 | 210,913 | 3,163,695 | 2 | 3,868,071 | 1,474,221,811 |
| 56 | 210,912 | 16 | 65,535 | 610,496,383 | 196,608 | 64,096,451 | 145,377 | 2,180,655 | 2 | 1,934,759 | 678,708,250 |
| 57 | 145,376 | 16 | 65,535 | 610,496,383 | 98,304 | 32,533,771 | 79,841 | 1,197,615 | 2 | 1,934,759 | 646,162,530 |
| 58 | 79,840 | 15 | 32,767 | 276,970,893 | 49,152 | 15,085,709 | 47,073 | 706,095 | 2 | 968,103 | 293,730,802 |
| 59 | 47,072 | 14 | 16,383 | 125,652,973 | 49,152 | 13,816,569 | 30,689 | 460,335 | 2 | 484,775 | 140,414,654 |
| 60 | 30,688 | 13 | 8,191 | 56,583,949 | 24,576 | 6,917,541 | 22,497 | 337,455 | 2 | 243,111 | 64,082,058 |
| 61 | 22,496 | 13 | 8,191 | 56,583,949 | 24,576 | 6,620,521 | 14,305 | 214,575 | 2 | 243,111 | 63,662,158 |
| 62 | 14,304 | 12 | 4,095 | 25,250,957 | 12,288 | 3,295,757 | 10,209 | 153,135 | 2 | 122,279 | 28,822,130 |
| 63 | 10,208 | 12 | 4,095 | 25,250,957 | 6,144 | 1,718,997 | 6,113 | 91,695 | 2 | 122,279 | 27,183,930 |
| 64 | 6,112 | 11 | 2,047 | 11,137,341 | 6,144 | 1,555,777 | 4,065 | 60,975 | 2 | 61,863 | 12,815,958 |
| 65 | 4,064 | 10 | 1,023 | 4,835,461 | 3,072 | 803,693 | 3,041 | 45,615 | 2 | 31,655 | 5,716,426 |
| 66 | 3,040 | 10 | 1,023 | 4,835,461 | 3,072 | 761,985 | 2,017 | 30,255 | 2 | 31,655 | 5,659,358 |
| 67 | 2,016 | 9 | 511 | 2,050,969 | 1,536 | 401,397 | 1,505 | 22,575 | 2 | 16,551 | 2,491,494 |
| 68 | 1,504 | 9 | 511 | 2,050,969 | 1,536 | 380,849 | 993 | 14,895 | 2 | 16,551 | 2,463,266 |
| 69 | 992 | 8 | 255 | 837,971 | 768 | 207,165 | 737 | 11,055 | 2 | 8,999 | 1,065,192 |
| 70 | 736 | 8 | 255 | 837,971 | 768 | 197,201 | 481 | 7,215 | 2 | 8,999 | 1,051,388 |
| 71 | 480 | 7 | 127 | 328,377 | 384 | 103,079 | 353 | 5,295 | 2 | 5,223 | 441,976 |
| 72 | 352 | 7 | 127 | 328,377 | 384 | 98,403 | 225 | 3,375 | 2 | 5,223 | 435,380 |

#### 6.2.1 Fixed-slot long-apply plans

| step | degree | budget | block B | transform N | operand blocks | output slots | matrix forwards | operand forwards | output inverses | block order | plan total |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 76,293,945,312 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 7 | 7 | 4 | 14 | 14 | `6..0` | 29,874,354,891,360 |
| 2 | 74,146,461,664 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 7 | 7 | 4 | 14 | 14 | `6..0` | 29,819,951,972,288 |
| 3 | 71,998,978,016 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 7 | 7 | 4 | 14 | 14 | `6..0` | 29,765,549,053,200 |
| 4 | 69,851,494,368 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 7 | 7 | 4 | 14 | 14 | `6..0` | 29,711,146,134,112 |
| 5 | 67,704,010,720 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 7 | 7 | 4 | 14 | 14 | `6..0` | 29,656,743,215,040 |
| 6 | 65,556,527,072 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 6 | 6 | 4 | 12 | 12 | `5..0` | 26,069,668,915,002 |
| 7 | 63,409,043,424 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 6 | 6 | 4 | 12 | 12 | `5..0` | 26,015,265,995,914 |
| 8 | 61,261,559,776 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 6 | 6 | 4 | 12 | 12 | `5..0` | 25,960,863,076,826 |
| 9 | 59,114,076,128 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 6 | 6 | 4 | 12 | 12 | `5..0` | 25,906,460,157,754 |
| 10 | 56,966,592,480 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 13 | 13 | 4 | 26 | 26 | `12..0` | 25,586,731,570,476 |
| 11 | 54,819,108,832 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 5 | 5 | 4 | 10 | 10 | `4..0` | 22,264,982,938,628 |
| 12 | 52,671,625,184 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 5 | 5 | 4 | 10 | 10 | `4..0` | 22,210,580,019,540 |
| 13 | 50,524,141,536 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 5 | 5 | 4 | 10 | 10 | `4..0` | 22,156,177,100,468 |
| 14 | 48,376,657,888 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 11 | 11 | 4 | 22 | 22 | `10..0` | 21,892,490,747,320 |
| 15 | 46,229,174,240 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 11 | 11 | 4 | 22 | 22 | `10..0` | 21,838,087,828,232 |
| 16 | 44,081,690,592 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 4 | 4 | 4 | 8 | 8 | `3..0` | 18,460,296,962,254 |
| 17 | 41,934,206,944 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 4 | 4 | 4 | 8 | 8 | `3..0` | 18,405,894,043,182 |
| 18 | 39,786,723,296 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 9 | 9 | 4 | 18 | 18 | `8..0` | 18,198,249,924,164 |
| 19 | 37,639,239,648 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 9 | 9 | 4 | 18 | 18 | `8..0` | 18,143,847,005,076 |
| 20 | 35,491,756,000 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 8 | 8 | 4 | 16 | 16 | `7..0` | 16,351,129,512,578 |
| 21 | 33,344,272,352 | 2,147,483,647 | 10,737,418,241 | 12,884,901,888 | 3 | 3 | 4 | 6 | 6 | `2..0` | 14,655,610,985,896 |
| 22 | 31,196,788,704 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 7 | 7 | 4 | 14 | 14 | `6..0` | 14,504,009,100,992 |
| 23 | 29,049,305,056 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 7 | 7 | 4 | 14 | 14 | `6..0` | 14,449,606,181,920 |
| 24 | 26,901,821,408 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 6 | 6 | 4 | 12 | 12 | `5..0` | 12,656,888,689,422 |
| 25 | 24,754,337,760 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 6 | 6 | 4 | 12 | 12 | `5..0` | 12,602,485,770,334 |
| 26 | 22,606,854,112 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 5 | 5 | 4 | 10 | 10 | `4..0` | 10,809,768,277,836 |
| 27 | 20,459,370,464 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 5 | 5 | 4 | 10 | 10 | `4..0` | 10,755,365,358,748 |
| 28 | 18,311,886,816 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 4 | 4 | 4 | 8 | 8 | `3..0` | 8,962,647,866,250 |
| 29 | 16,164,403,168 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 4 | 4 | 4 | 8 | 8 | `3..0` | 8,908,244,947,178 |
| 32 | 9,721,952,224 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 2 | 2 | 4 | 4 | 4 | `1..0` | 5,268,407,043,094 |
| 34 | 5,426,984,928 | 2,147,483,647 | 4,294,967,297 | 6,442,450,944 | 1 | 1 | 4 | 2 | 2 | `0..0` | 3,415,870,812,756 |
| 51 | 2,701,280 | 1,048,575 | 2,097,153 | 3,145,728 | 1 | 1 | 4 | 2 | 2 | `0..0` | 1,150,705,536 |
| 55 | 341,984 | 131,071 | 262,145 | 393,216 | 1 | 1 | 4 | 2 | 2 | `0..0` | 130,245,592 |

Every fixed winner above is one `ApplyPlan` selected after all declared transform sizes and both forms were priced. Its `operation_rows()` sum to its total; its six `allocation_arrays()` carry the low/low/low/low/high/high pool placement consumed by section 7. The slot count and decreasing order are fields of the same object.

#### 6.2.2 Direct whole-transform apply plans

| step | degree | budget | transform N | matrix length | operand length | output length | plan total |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 30 | 14,016,919,520 | 2,147,483,647 | 12,884,901,888 | 2,147,483,648 | 14,016,919,521 | 11,869,435,873 | 7,087,257,807,479 |
| 31 | 11,869,435,872 | 2,147,483,647 | 12,884,901,888 | 2,147,483,648 | 11,869,435,873 | 9,721,952,225 | 7,018,804,470,331 |
| 33 | 7,574,468,576 | 2,147,483,647 | 6,442,450,944 | 2,147,483,648 | 7,574,468,577 | 5,426,984,929 | 3,488,075,209,615 |
| 35 | 3,279,501,280 | 1,073,741,823 | 3,221,225,472 | 1,073,741,824 | 3,279,501,281 | 2,205,759,457 | 1,685,604,618,999 |
| 36 | 2,205,759,456 | 1,073,741,823 | 1,610,612,736 | 1,073,741,824 | 2,205,759,457 | 1,132,017,633 | 846,042,369,719 |
| 37 | 1,132,017,632 | 536,870,911 | 805,306,368 | 536,870,912 | 1,132,017,633 | 595,146,721 | 400,316,058,305 |
| 38 | 595,146,720 | 268,435,455 | 402,653,184 | 268,435,456 | 595,146,721 | 326,711,265 | 196,606,107,089 |
| 39 | 326,711,264 | 134,217,727 | 201,326,592 | 134,217,728 | 326,711,265 | 192,493,537 | 97,129,303,793 |
| 40 | 192,493,536 | 67,108,863 | 201,326,592 | 67,108,864 | 192,493,537 | 125,384,673 | 91,937,255,765 |
| 41 | 125,384,672 | 33,554,431 | 100,663,296 | 33,554,432 | 125,384,673 | 91,830,241 | 45,895,876,617 |
| 42 | 91,830,240 | 33,554,431 | 100,663,296 | 33,554,432 | 91,830,241 | 58,275,809 | 44,685,621,197 |
| 43 | 58,275,808 | 16,777,215 | 50,331,648 | 16,777,216 | 58,275,809 | 41,498,593 | 22,180,329,329 |
| 44 | 41,498,592 | 16,777,215 | 25,165,824 | 16,777,216 | 41,498,593 | 24,721,377 | 11,286,197,041 |
| 45 | 24,721,376 | 8,388,607 | 25,165,824 | 8,388,608 | 24,721,377 | 16,332,769 | 10,623,997,349 |
| 46 | 16,332,768 | 4,194,303 | 12,582,912 | 4,194,304 | 16,332,769 | 12,138,465 | 5,325,562,953 |
| 47 | 12,138,464 | 4,194,303 | 12,582,912 | 4,194,304 | 12,138,465 | 7,944,161 | 5,161,087,333 |
| 48 | 7,944,160 | 2,097,151 | 6,291,456 | 2,097,152 | 7,944,161 | 5,847,009 | 2,465,630,971 |
| 49 | 5,847,008 | 2,097,151 | 6,291,456 | 2,097,152 | 5,847,009 | 3,749,857 | 2,387,837,631 |
| 50 | 3,749,856 | 1,048,575 | 3,145,728 | 1,048,576 | 3,749,857 | 2,701,281 | 1,186,509,667 |
| 52 | 1,652,704 | 524,287 | 1,572,864 | 524,288 | 1,652,705 | 1,128,417 | 565,530,411 |
| 53 | 1,128,416 | 524,287 | 786,432 | 524,288 | 1,128,417 | 604,129 | 285,443,739 |
| 54 | 604,128 | 262,143 | 393,216 | 262,144 | 604,129 | 341,985 | 139,835,307 |
| 56 | 210,912 | 65,535 | 196,608 | 65,536 | 210,913 | 145,377 | 64,096,451 |
| 57 | 145,376 | 65,535 | 98,304 | 65,536 | 145,377 | 79,841 | 32,533,771 |
| 58 | 79,840 | 32,767 | 49,152 | 32,768 | 79,841 | 47,073 | 15,085,709 |
| 59 | 47,072 | 16,383 | 49,152 | 16,384 | 47,073 | 30,689 | 13,816,569 |
| 60 | 30,688 | 8,191 | 24,576 | 8,192 | 30,689 | 22,497 | 6,917,541 |
| 61 | 22,496 | 8,191 | 24,576 | 8,192 | 22,497 | 14,305 | 6,620,521 |
| 62 | 14,304 | 4,095 | 12,288 | 4,096 | 14,305 | 10,209 | 3,295,757 |
| 63 | 10,208 | 4,095 | 6,144 | 4,096 | 10,209 | 6,113 | 1,718,997 |
| 64 | 6,112 | 2,047 | 6,144 | 2,048 | 6,113 | 4,065 | 1,555,777 |
| 65 | 4,064 | 1,023 | 3,072 | 1,024 | 4,065 | 3,041 | 803,693 |
| 66 | 3,040 | 1,023 | 3,072 | 1,024 | 3,041 | 2,017 | 761,985 |
| 67 | 2,016 | 511 | 1,536 | 512 | 2,017 | 1,505 | 401,397 |
| 68 | 1,504 | 511 | 1,536 | 512 | 1,505 | 993 | 380,849 |
| 69 | 992 | 255 | 768 | 256 | 993 | 737 | 207,165 |
| 70 | 736 | 255 | 768 | 256 | 737 | 481 | 197,201 |
| 71 | 480 | 127 | 384 | 128 | 481 | 353 | 103,079 |
| 72 | 352 | 127 | 384 | 128 | 353 | 225 | 98,403 |

Each direct winner is the direct variant of the same `ApplyPlan` type. Its required 20-action point multiset, four low matrix spectra, two high operand/output spectra and output scaling are generated once and used by both ledgers.

| component | operations |
| --- | ---: |
| outer steps | 2,583,370,480,733,589 |
| classical euclid | 409,248 |
| normalization | 2,653 |
| entry | 1,012 |
| exit and frees | 107 |
| allocator trace | 139,905 |
| **row D** | **2,583,370,481,286,514** |





### 6.3 Normal-sequence trace and ABORT

Every division tests that its quotient has degree one before the priced division body, and every recursive return tests that the requested budget was removed. A zero remainder also ends the trial. On the normal sequence, degrees, budgets, product windows, and allocation sizes depend only on `m`. At the first failed quotient or return test, the trial performs the charged allocator reset and ABORTs. Therefore any abnormal trial executes a prefix of both the operation trace and allocation trace printed here. H-NORMAL affects only section 9.2's success probability, not either resource bound.

### 6.4 Generated reference deltas against 3db5de78

These tables are contextual comparisons. The reference-delta script parses the published Markdown ledger of `3db5de78` as text; it never imports or executes participant code. The parsed proof SHA-256 is `97e2848f7e830268b40be149e2df9325568fb2c664403a255d446f9d936a65aa`. Every current value comes from this package's live ledger. No reference value is an input to a current operation or memory row.

| row | current | 3db5de78 | current minus reference | source of difference |
| --- | ---: | ---: | ---: | --- |
| B | 148,386,783,813,197 | 97,164,545,020,466 | +51,222,238,792,731 | Least-charge row passes under the running-twiddle machine; no persistent transform twiddle table. |
| C | 5,937,454,131,022,267 | 6,203,834,714,659,050 | -266,380,583,636,783 | Eight-position column control and the accepted value-domain component formulas, with the new delayed lifetimes and omega tables. |
| D | 2,583,370,481,286,514 | 2,561,608,653,181,651 | +21,761,828,104,863 | Least-charge nodes plus adaptive direct/fixed plans under the package's atomic actions and matrix handoff. |
| rest | 133,901,995 | 17,350,519,675 | -17,216,617,680 | Named finite loops, exact planner keys and trace-priced allocator events. |
| N | 8,669,211,530,023,973 | 8,862,625,263,380,842 | -193,413,733,356,869 | Signed sum of all current rows; the reference total is comparison data only. |

| Stage-C component | current | 3db5de78 | delta | algorithm or charging change |
| --- | ---: | ---: | ---: | --- |
| tables and plans | 4,667,240 | 4,633,852 | +33,388 | Both integers are independently generated from the named component loops. |
| newton reciprocal | 21,787,555,000,410 | 18,060,840,801,479 | +3,726,714,198,931 | Both integers are independently generated from the named component loops. |
| quotient product | 6,426,834,963,221 | 5,429,417,913,149 | +997,417,050,072 | Both integers are independently generated from the named component loops. |
| g geometric evaluation | 6,372,750,000,205 | 11,735,876,501,760 | -5,363,126,501,555 | Both integers are independently generated from the named component loops. |
| g inner transforms | 9,002,970,663,084 | 9,491,206,635,536 | -488,235,972,452 | Both integers are independently generated from the named component loops. |
| start residue | 13,167,689,147,550 | 13,299,798,245,920 | -132,109,098,370 | Both integers are independently generated from the named component loops. |
| first extension | 12,967,615,547,912 | 13,113,730,531,616 | -146,114,983,704 | Both integers are independently generated from the named component loops. |
| batch inversion | 1,114,366,279,685 | 1,143,452,860,832 | -29,086,581,147 | Both integers are independently generated from the named component loops. |
| powering loop | 5,789,377,875,408,805 | 6,056,913,037,033,520 | -267,535,161,624,715 | Both integers are independently generated from the named component loops. |
| exit montgomery | 14,465,485,392,397 | 15,463,077,643,328 | -997,592,250,931 | Both integers are independently generated from the named component loops. |
| two interpolations | 52,193,463,782,027 | 59,174,071,304,484 | -6,980,607,522,457 | Both integers are independently generated from the named component loops. |
| allocation and control | 10,577,520,168,731 | 10,200,552,574 | +10,567,319,616,157 | Both integers are independently generated from the named component loops. |
| entry exit | 1,000 | 1,000 | +0 | Both integers are independently generated from the named component loops. |

| Stage-D component | current | 3db5de78 | delta | algorithm or charging change |
| --- | ---: | ---: | ---: | --- |
| pass | 1,944,960,717,485,692 | 1,911,368,880,939,492 | +33,591,836,546,200 | Least-charge half-gcd node passes versus the parsed reference node rows. |
| apply | 616,342,768,304,473 | 630,423,447,237,360 | -14,080,678,932,887 | The selected adaptive direct/fixed plan rows versus the parsed reference apply rows. |
| driver | 22,066,994,943,424 | 19,816,323,818,568 | +2,250,671,124,856 | Linear divisions, quotient tests, matrix handoffs and driver control, without allocator events. |
| allocator | 139,905 | 0 | +139,905 | Every current Stage-D first-fit and slab event is isolated from the driver; the reference does not publish a separable allocator row. |
| tail | 413,020 | 1,186,231 | -773,211 | Classical tail, normalization, entry and exit rows after the 72 outer repetitions. |

The D split is exact on both sides. For `3db5de78` the parser sums the node, apply and repetition-total columns of all 72 published outer rows; driver is their residual and tail is published row D minus those repetitions. For this package the same four categories come from the live `OuterStep` objects and the allocator-event owners.

| memory component | current bytes | 3db5de78 bytes | delta | cause |
| --- | ---: | ---: | ---: | --- |
| pool high-water | 9,895,604,650,368 | 9,964,324,127,040 | -68,719,476,672 | Current two-ended first-fit trace versus the reference's published trace. |
| slabs | 201,265,664 | 997,723,648 | -796,457,984 | Mechanically selected slab classes from all named small arrays. |
| arena | 9,895,805,916,160 | 9,965,321,867,712 | -69,515,951,552 | Pool, slabs and the 128-byte middle gap. |
| total footprint | 9,895,806,318,240 | 9,965,327,874,428 | -69,521,556,188 | Arena plus generated image, stack, register file and offline workspace. |

#### 6.4.1 Stage-C peak objects

The current witness is allocator event `328`. Each current member below comes from that event's generated live map. Reference families come from the named Stage-C peak objects in `3db5de78` sections 4.6 and 7. The object rows sum exactly to `-68,711,072,064` bytes.

| change | allocation family | current bytes | reference bytes | delta | current live objects | reference live objects | schedule explanation |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| resized | g representation | 2,473,901,162,688 | 2,473,901,162,560 | +128 | g-coefficients, g-value-padding | g | The current trace retains coefficient g and its value padding as two separately headed blocks. |
| unchanged | three residue arrays | 7,421,703,487,680 | 7,421,703,487,680 | +0 | R1-q-values, R2, G1 | R1, R2, G1 | Both schedules hold R1, R2 and G1 as n1-word arrays at the loop peak. |
| removed | persistent transform twiddle table | 0 | 68,719,476,800 | -68,719,476,800 | - | twiddle-table | Running-twiddle product passes form their chains in registers and retain no 2^31-word table. |
| resized | tables and small workspace | 16,822,272 | 8,417,664 | +8,404,608 | batch-inversion-prefix, omega-table-high, omega-table-low, stage-C-correlation-kernels, stage-C-coset-scalars, stage-C-group-buffer, stage-C-transform-row | tables-and-small-workspace | The current trace names the two omega tables, group buffer, transform row, kernels and coset scalars. |

#### 6.4.2 Stage-D peak objects

The current witness is allocator event `1172`. Reference families come from the named `3db5de78` Stage-D witness. These rows sum exactly to `-68,719,475,712` bytes.

| change | allocation family | current bytes | reference bytes | delta | current live objects | reference live objects | schedule explanation |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| resized | g representation | 2,473,901,162,688 | 2,473,901,162,560 | +128 | g-coefficients, g-value-padding | g | The current coefficient array and value padding have separate 64-byte headers. |
| unchanged | pair and six spectra | 4,947,802,325,440 | 4,947,802,325,440 | +0 | R2, D1-apply-matrix-r11-spectrum, D1-apply-matrix-r12-spectrum, D1-apply-matrix-r21-spectrum, D1-apply-matrix-r22-spectrum, D1-apply-operand-a-spectrum-output-c, D1-apply-operand-b-spectrum-output-d | pair, six apply spectra | Both schedules hold one n1-word pair row and six 3*2^32-word spectra at the first apply peak. |
| removed | persistent transform twiddle table | 0 | 68,719,476,800 | -68,719,476,800 | - | stage-D persistent twiddle table | The running-twiddle passes retain no 2^31-word table. |
| resized | scale table | 2,048 | 1,088 | +960 | scale-table-1-over-2-powers | 31-word scale table | The current slab class reserves 2,048 bytes; the reference live-set request is 1,088 bytes. |

#### 6.4.3 Pool high-water bridge

The two pool maxima occur at different stage witnesses. The following generated bridge reconciles the published pool delta exactly.

| family | delta bytes | allocator explanation |
| --- | ---: | --- |
| g representation | +128 | Two current pool blocks replace the reference's one g block and add one 64-byte header plus alignment. |
| pair and six spectra | +0 | The split low/high placement changes addresses but not the pool bytes reserved for these seven arrays. |
| persistent transform twiddle table | -68,719,476,800 | The current pool contains no persistent 2^31-word twiddle allocation. |
| scale table | +0 | Both scale-table requests use a slab class, outside the two-ended pool high-water. |


## 7. Event-by-event memory

Every top-level request has a 64-byte header and a payload rounded to 64 bytes. Requests at most `2^24` bytes use the mechanically selected power-of-two slab class; larger requests use the two-ended pool. Long-lived `g` is retained from stage B. Temporary Newton arrays are freed before the four value-domain arrays become live. Stage D allocates the 31-word scale table, one recursive bump reservation per outer step, six arrays for each fixed-slot or direct apply, and the two-word quotient. Every recursive subarray has its own 64-byte header inside the reservation. Stages E through G also appear in the trace. It ends with an empty live map.

Appendix X.2 materializes all `45,062` ordered allocation and free records as `ALLOCATOR_EVENTS`. Each record is the ten-tuple `(number, stage, action, array, side_or_bump_offset, rounded_bytes, live_bytes, low_extent, high_extent, reserved_arena_bytes)`. The last field includes both pool extents and every slab slot created so far; it is not merely the sum of the two pool extents. An allocation is appended only after its named block has been placed; a free is appended only after that exact block is removed. The allocator asserts unique top-level names, exact-size frees, no overlap, nonnegative extents, and an empty final live map. Bump suballocations assert disjoint offsets and mark/release order inside their one live top-level reservation. The canonical compact-JSON SHA-256 of that complete event stream is `5f50fa1b9be236987b6ed5d5008285d920191f8d8cc551ab08720549bcc696cb`. This digest is descriptive binding inside the proof; the memory claim is recomputed from the tuples, not inferred from the digest.

| stage partition | generated records | first record | last record | maximum reserved arena bytes |
| --- | ---: | ---: | ---: | ---: |
| B | 5 | 1 | 5 | 5,018,386,627,840 |
| C | 332 | 6 | 337 | 9,895,680,147,072 |
| D | 44,693 | 338 | 45031 | 9,071,046,426,432 |
| E | 14 | 45028 | 45044 | 7,421,904,748,096 |
| F | 8 | 45045 | 45057 | 201,265,664 |
| G | 10 | 45052 | 45062 | 201,265,664 |

The exact high-water witness is:

| # | stage | action | array | side or bump offset | rounded bytes | live bytes | low extent | high extent | reserved arena bytes |
| ---: | --- | --- | --- | :---: | ---: | ---: | ---: | ---: | ---: |
| 328 | C | alloc | batch-inversion-prefix | S22 | 4,194,304 | 9,895,621,472,640 | 4,947,802,325,248 | 4,947,802,325,120 | 9,895,680,147,072 |

| component | bytes |
| --- | ---: |
| stage B live peak | 5,018,386,627,840 |
| stage C live peak | 9,895,621,472,640 |
| stage D live peak | 7,421,703,490,176 |
| stage E live peak | 4,947,802,326,272 |
| stage F live peak | 2,944 |
| stage G live peak | 1,408 |
| pool high-water | 9,895,604,650,368 |
| slab classes | 201,265,664 |
| pool middle gap | 128 |
| arena = pool + slabs + gap | 9,895,805,916,160 |
| code and static data | 356,352 |
| 387-word register file | 12,384 |
| offline workspace | 576 |
| stack | 32,768 |
| **footprint** | **9,895,806,318,240** |

The time ledger prices this same top-level allocator trace. A pool request charges the exact number of address-ordered segments examined; a pool free charges its exact find, merge and tail-release walks. A slab request charges the exact slot flags examined and whether it creates a slot. Recursive suballocations use the node's already charged mark/release loops and do not call first-fit.

| stage | traced allocator operations |
| --- | ---: |
| B | 635 |
| C | 29,763 |
| D | 139,905 |
| E | 261 |
| F | 99 |
| G | 181 |

The maximum pool allocation walk examines `6` segments, and the maximum pool free find examines `7` segments. Both maxima are asserted against the emitted allocator-event list. No default live-block bound enters the time ledger.

The raw memory logarithm is `43.1699544026601753158918369089419082466522007345660469660905578106330579385405933948647203`. Upward rounding at five decimals gives `memory_log2_bytes = 43.16996`. No product twiddle table or nonuniform advice exists.

### 7.1 Slab classes and recursive/apply ranges

| class | created slots | peak live slots | bytes |
| --- | ---: | ---: | ---: |
| slab-class-7 | 2 | 2 | 256 |
| slab-class-8 | 5 | 5 | 1,280 |
| slab-class-9 | 2 | 2 | 1,024 |
| slab-class-10 | 6 | 6 | 6,144 |
| slab-class-11 | 2 | 2 | 4,096 |
| slab-class-12 | 2 | 2 | 8,192 |
| slab-class-13 | 2 | 2 | 16,384 |
| slab-class-14 | 6 | 6 | 98,304 |
| slab-class-15 | 6 | 6 | 196,608 |
| slab-class-16 | 6 | 6 | 393,216 |
| slab-class-17 | 6 | 6 | 786,432 |
| slab-class-18 | 6 | 6 | 1,572,864 |
| slab-class-19 | 6 | 6 | 3,145,728 |
| slab-class-20 | 6 | 6 | 6,291,456 |
| slab-class-21 | 6 | 6 | 12,582,912 |
| slab-class-22 | 6 | 6 | 25,165,824 |
| slab-class-23 | 6 | 6 | 50,331,648 |
| slab-class-24 | 6 | 6 | 100,663,296 |
| **slab total** | | | **201,265,664** |

Every class and slot count comes from the allocation stream; no slab dictionary or later-stage reserve is an input. The separate middle gap is 128 bytes.

The recursive node footprint is generated from the same levels as the Stage-D operation tree. At base level 6, four remainder, four matrix and four scratch arrays use `12*2^6` words. At a higher level with `n=2^(j-1)`, four `2n`-word coefficient-form matrix arrays and eight `n`-word top/apply/CRT arrays add `16n` words. Thus `pdmem(6)=12*2^6` and `pdmem(j)=pdmem(j-1)+16*2^(j-1)`. One top-level first-fit request reserves the root-to-leaf layout. The recursive code suballocates it with a cursor and nested marks. Sibling calls reuse locations only after release to the saved mark. The four root matrix subarrays remain reserved until the selected apply consumes them.

| node level | local words | root-to-leaf peak words |
| ---: | ---: | ---: |
| 6 | 768 | 768 |
| 7 | 1,024 | 1,792 |
| 8 | 2,048 | 3,840 |
| 9 | 4,096 | 7,936 |
| 10 | 8,192 | 16,128 |
| 11 | 16,384 | 32,512 |
| 12 | 32,768 | 65,280 |
| 13 | 65,536 | 130,816 |
| 14 | 131,072 | 261,888 |
| 15 | 262,144 | 524,032 |
| 16 | 524,288 | 1,048,320 |
| 17 | 1,048,576 | 2,096,896 |
| 18 | 2,097,152 | 4,194,048 |
| 19 | 4,194,304 | 8,388,352 |
| 20 | 8,388,608 | 16,776,960 |
| 21 | 16,777,216 | 33,554,176 |
| 22 | 33,554,432 | 67,108,608 |
| 23 | 67,108,864 | 134,217,472 |
| 24 | 134,217,728 | 268,435,200 |
| 25 | 268,435,456 | 536,870,656 |
| 26 | 536,870,912 | 1,073,741,568 |
| 27 | 1,073,741,824 | 2,147,483,392 |
| 28 | 2,147,483,648 | 4,294,967,040 |
| 29 | 4,294,967,296 | 8,589,934,336 |
| 30 | 8,589,934,592 | 17,179,868,928 |
| 31 | 17,179,869,184 | 34,359,738,112 |

| node level | named subarrays | payload words | bump-reservation payload bytes, including subarray headers |
| ---: | ---: | ---: | ---: |
| 6 | 12 | 768 | 25,408 |
| 7 | 28 | 1,792 | 59,200 |
| 8 | 44 | 3,840 | 125,760 |
| 9 | 60 | 7,936 | 257,856 |
| 10 | 76 | 16,128 | 521,024 |
| 11 | 92 | 32,512 | 1,046,336 |
| 12 | 108 | 65,280 | 2,095,936 |
| 13 | 124 | 130,816 | 4,194,112 |
| 14 | 140 | 261,888 | 8,389,440 |
| 15 | 156 | 524,032 | 16,779,072 |
| 16 | 172 | 1,048,320 | 33,557,312 |
| 17 | 188 | 2,096,896 | 67,112,768 |
| 18 | 204 | 4,194,048 | 134,222,656 |
| 19 | 220 | 8,388,352 | 268,441,408 |
| 20 | 236 | 16,776,960 | 536,877,888 |
| 21 | 252 | 33,554,176 | 1,073,749,824 |
| 22 | 268 | 67,108,608 | 2,147,492,672 |
| 23 | 284 | 134,217,472 | 4,294,977,344 |
| 24 | 300 | 268,435,200 | 8,589,945,664 |
| 25 | 316 | 536,870,656 | 17,179,881,280 |
| 26 | 332 | 1,073,741,568 | 34,359,751,488 |
| 27 | 348 | 2,147,483,392 | 68,719,490,880 |
| 28 | 364 | 4,294,967,040 | 137,438,968,640 |
| 29 | 380 | 8,589,934,336 | 274,877,923,136 |
| 30 | 396 | 17,179,868,928 | 549,755,831,104 |
| 31 | 412 | 34,359,738,112 | 1,099,511,646,016 |

The exact script emits every named recursive subarray, one bump-allocation and one bump-free record, with a 64-byte header and 64-byte payload rounding for each subarray. Product, fixed-slot and direct allocation schedules come from the same plan objects as their operation rows; no second memory-only plan exists.

| generated range family | instances | first record | last record | records in ranges |
| --- | ---: | ---: | ---: | ---: |
| Stage-C product plans | 69 | 11 | 316 | 304 |
| recursive node chains | 72 | 339 | 45011 | 43,608 |
| Stage-D direct applies | 39 | 25584 | 45024 | 507 |
| role changes | 875 | 1 | 875 | 875 |

### 7.2 Stack call graph and offline workspace

| frame | named field group | words | bytes |
| --- | --- | ---: | ---: |
| runtime | return pc | 1 | 32 |
| runtime | saved pool ends | 2 | 64 |
| runtime | target pointer | 1 | 32 |
| runtime | config pointer | 1 | 32 |
| runtime | stage counter | 1 | 32 |
| runtime | status | 1 | 32 |
| runtime | output pointer | 1 | 32 |
| line sampler | centre words | 4 | 128 |
| line sampler | line coordinates | 6 | 192 |
| line sampler | sampler counters | 4 | 128 |
| line sampler | pointers | 6 | 192 |
| stage c driver | four value array pointers | 4 | 128 |
| stage c driver | coset and length fields | 8 | 256 |
| stage c driver | scalar state | 8 | 256 |
| stage c driver | allocator marks | 4 | 128 |
| stage c driver | loop counters | 8 | 256 |
| transform | value pointers | 8 | 256 |
| transform | twiddle pointers | 4 | 128 |
| transform | offset pointers | 8 | 256 |
| transform | layer and loop fields | 8 | 256 |
| transform | saved register words | 4 | 128 |
| planner | three lengths | 3 | 96 |
| planner | candidate fields | 5 | 160 |
| planner | selected plan fields | 5 | 160 |
| planner | pointers | 3 | 96 |
| hgcd driver | pair pointers | 4 | 128 |
| hgcd driver | degree fields | 4 | 128 |
| hgcd driver | budget fields | 3 | 96 |
| hgcd driver | arena marks | 2 | 64 |
| hgcd driver | return fields | 3 | 96 |
| hgcd recursive | four matrix pointers | 4 | 128 |
| hgcd recursive | pair pointers | 4 | 128 |
| hgcd recursive | degree budget split | 5 | 160 |
| hgcd recursive | window fields | 3 | 96 |
| hgcd recursive | arena marks | 2 | 64 |
| hgcd recursive | return fields | 6 | 192 |
| allocator | request fields | 4 | 128 |
| allocator | list pointers | 4 | 128 |
| allocator | split fields | 4 | 128 |
| allocator | statistics | 4 | 128 |
| isolation | six polynomial pointers | 6 | 192 |
| isolation | degree fields | 4 | 128 |
| isolation | shift state | 4 | 128 |
| isolation | loop fields | 4 | 128 |
| encoding verify | two messages | 4 | 128 |
| encoding verify | two states | 6 | 192 |
| encoding verify | two digests | 2 | 64 |
| encoding verify | encoding fields | 4 | 128 |
| offline generator | sixteen field words | 16 | 512 |
| offline generator | digit buffer words | 2 | 64 |
| offline generator | loop fields | 4 | 128 |

| mutually exclusive call chain | frames | words | bytes |
| --- | --- | ---: | ---: |
| stage-B | 1x runtime; 1x line_sampler; 1x transform; 1x allocator | 76 | 2,432 |
| stage-C | 1x runtime; 1x stage_c_driver; 1x planner; 7x transform; 1x allocator | 296 | 9,472 |
| stage-D | 1x runtime; 1x hgcd_driver; 26x hgcd_recursive; 1x planner; 7x transform; 1x allocator | 904 | 28,928 |
| stage-E | 1x runtime; 1x isolation; 1x allocator | 42 | 1,344 |
| stage-FG | 1x runtime; 1x encoding_verify; 1x allocator | 40 | 1,280 |
| offline | 1x offline_generator | 22 | 704 |
| maximum live chain | | | 28,928 |
| **16-KiB-rounded stack bound** | | | **32,768** |

The offline generator handles one literal at a time: sixteen 32-byte field words plus one 64-byte digit buffer, exactly `576` bytes.

### 7.3 Emitted image manifest

| object | kind | offset | bytes | end | emitted-size formula |
| --- | --- | ---: | ---: | ---: | --- |
| block-forward-w1 | routine | 0 | 160 | 160 | 4-byte instructions * 4 unrolled blocks * B(1) |
| block-forward-group-zero-w1 | routine | 192 | 144 | 336 | 4-byte instructions * 4 blocks * twiddle-one body(1) |
| block-forward-w2 | routine | 384 | 368 | 752 | 4-byte instructions * 4 unrolled blocks * B(2) |
| block-forward-group-zero-w2 | routine | 768 | 320 | 1,088 | 4-byte instructions * 4 blocks * twiddle-one body(2) |
| block-forward-w3 | routine | 1,088 | 880 | 1,968 | 4-byte instructions * 4 unrolled blocks * B(3) |
| block-forward-group-zero-w3 | routine | 1,984 | 768 | 2,752 | 4-byte instructions * 4 blocks * twiddle-one body(3) |
| block-forward-w4 | routine | 2,752 | 2,096 | 4,848 | 4-byte instructions * 4 unrolled blocks * B(4) |
| block-forward-group-zero-w4 | routine | 4,864 | 1,856 | 6,720 | 4-byte instructions * 4 blocks * twiddle-one body(4) |
| block-forward-w5 | routine | 6,720 | 4,912 | 11,632 | 4-byte instructions * 4 unrolled blocks * B(5) |
| block-forward-group-zero-w5 | routine | 11,648 | 4,416 | 16,064 | 4-byte instructions * 4 blocks * twiddle-one body(5) |
| block-forward-w6 | routine | 16,064 | 11,312 | 27,376 | 4-byte instructions * 4 unrolled blocks * B(6) |
| block-forward-group-zero-w6 | routine | 27,392 | 10,304 | 37,696 | 4-byte instructions * 4 blocks * twiddle-one body(6) |
| block-forward-w7 | routine | 37,696 | 25,648 | 63,344 | 4-byte instructions * 4 unrolled blocks * B(7) |
| block-forward-group-zero-w7 | routine | 63,360 | 23,616 | 86,976 | 4-byte instructions * 4 blocks * twiddle-one body(7) |
| block-inverse-w1 | routine | 86,976 | 160 | 87,136 | 4-byte instructions * 4 unrolled blocks * B(1) |
| block-inverse-group-zero-w1 | routine | 87,168 | 144 | 87,312 | 4-byte instructions * 4 blocks * twiddle-one body(1) |
| block-inverse-w2 | routine | 87,360 | 368 | 87,728 | 4-byte instructions * 4 unrolled blocks * B(2) |
| block-inverse-group-zero-w2 | routine | 87,744 | 320 | 88,064 | 4-byte instructions * 4 blocks * twiddle-one body(2) |
| block-inverse-w3 | routine | 88,064 | 880 | 88,944 | 4-byte instructions * 4 unrolled blocks * B(3) |
| block-inverse-group-zero-w3 | routine | 88,960 | 768 | 89,728 | 4-byte instructions * 4 blocks * twiddle-one body(3) |
| block-inverse-w4 | routine | 89,728 | 2,096 | 91,824 | 4-byte instructions * 4 unrolled blocks * B(4) |
| block-inverse-group-zero-w4 | routine | 91,840 | 1,856 | 93,696 | 4-byte instructions * 4 blocks * twiddle-one body(4) |
| block-inverse-w5 | routine | 93,696 | 4,912 | 98,608 | 4-byte instructions * 4 unrolled blocks * B(5) |
| block-inverse-group-zero-w5 | routine | 98,624 | 4,416 | 103,040 | 4-byte instructions * 4 blocks * twiddle-one body(5) |
| block-inverse-w6 | routine | 103,040 | 11,312 | 114,352 | 4-byte instructions * 4 unrolled blocks * B(6) |
| block-inverse-group-zero-w6 | routine | 114,368 | 10,304 | 124,672 | 4-byte instructions * 4 blocks * twiddle-one body(6) |
| block-inverse-w7 | routine | 124,672 | 25,648 | 150,320 | 4-byte instructions * 4 unrolled blocks * B(7) |
| block-inverse-group-zero-w7 | routine | 150,336 | 23,616 | 173,952 | 4-byte instructions * 4 blocks * twiddle-one body(7) |
| column-w1 | routine | 173,952 | 352 | 174,304 | 4-byte instructions * 8 positions * 11 |
| column-w2 | routine | 174,336 | 640 | 174,976 | 4-byte instructions * 8 positions * 20 |
| column-w3 | routine | 174,976 | 1,664 | 176,640 | 4-byte instructions * 8 positions * 52 |
| column-w4 | routine | 176,640 | 4,096 | 180,736 | 4-byte instructions * 8 positions * 128 |
| column-w5 | routine | 180,736 | 9,728 | 190,464 | 4-byte instructions * 8 positions * 304 |
| column-w6 | routine | 190,464 | 22,528 | 212,992 | 4-byte instructions * 8 positions * 704 |
| column-w7 | routine | 212,992 | 51,200 | 264,192 | 4-byte instructions * 8 positions * 1600 |
| target-compression | routine | 264,192 | 1,704 | 265,896 | 4-byte instructions * C(10) |
| montgomery-mul | routine | 265,920 | 1,320 | 267,240 | 4-byte instructions * 330 |
| field-invert | routine | 267,264 | 9,240 | 276,504 | 4-byte instructions * 2310 |
| field-encode | routine | 276,544 | 2,048 | 278,592 | 4-byte instructions * 512 |
| allocator | routine | 278,592 | 804 | 279,396 | 4-byte instructions * maximum traced top-level allocator call |
| polynomial-driver | routine | 279,424 | 1,744 | 281,168 | 4-byte instructions * node, plan, and close actions |
| fixed-slot-two-output-pointwise | routine | 281,216 | 416 | 281,632 | 4-byte instructions * eight-position two-output spectral body |
| fixed-slot-overlap-add | routine | 281,664 | 256 | 281,920 | 4-byte instructions * eight-position scaled overlap body |
| direct-two-output-pointwise | routine | 281,920 | 672 | 282,592 | 4-byte instructions * eight addressed direct points |
| direct-output-placement | routine | 282,624 | 192 | 282,816 | 4-byte instructions * eight direct output placements |
| outer-linear-division | routine | 282,816 | 488 | 283,304 | 4-byte instructions * eight coefficients plus quotient test |
| half-gcd-base | routine | 283,328 | 2,048 | 285,376 | 4-byte instructions * conservative finite base-loop image |
| stage-c-driver | routine | 285,376 | 4,000 | 289,376 | 4-byte instructions * expanded Stage-C bookkeeping image |
| sampler-and-line-setup | routine | 289,408 | 4,912 | 294,320 | 4-byte instructions * charged sampler/line entry body |
| reference-verification-wrapper | routine | 294,336 | 10,320 | 304,656 | 4-byte instructions * expanded verification wrapper |
| stage-e-driver | routine | 304,704 | 380 | 305,084 | 4-byte instructions * named isolation driver actions |
| stage-f-driver | routine | 305,088 | 1,352 | 306,440 | 4-byte instructions * one Tonelli control body |
| pass-plan-table | data | 306,496 | 2,112 | 308,608 | two directions * 33 depths * one 32-byte plan word |
| literal-table | data | 308,608 | 6,784 | 315,392 | 212 field/word literals * 32 bytes |
| output-buffer | data | 315,392 | 8,192 | 323,584 | 256 words * 32 bytes |
| adaptive-apply-omega-and-pass-planner | routine | 323,584 | 32,768 | 356,352 | 2048 instructions * conservative 16-byte maximum |
| **aligned image end** | | | | **356,352** | |

## 8. Score and evaluation obligations

The time claim is `44.21012` and the memory claim is `43.16996`. Applying the stated lane formula gives `44.21012 + max(0,43.16996-20) = 67.38008`. This is a normalized cost, not a ranking model.

1. `target_defined`: sections 1 through 3 fix P128Pow5T3 over Pallas, the selected reduced-round target and full-field output.
2. `algorithm_defined`: sections 3 through 5 define the line, odd part, evaluation recovery, exact value-domain powering, inversion-free half-gcd, root isolation, lift and reference verification.
3. `resources_defined`: sections 4.2, 6, 7 and Appendices E and X expand every operation family, search, allocation and fixed memory region.
4. `probability_space_defined`: section 4.1.1 and section 9.2 define the fixed target and fresh independent random words.
5. `heuristics_disclosed`: claim.json and sections 9.1 and 9.5 retain H-ONE and H-NORMAL with their roles, evidence and limitations. The resource derivation has no heuristic.
6. `evidence_relevant`: section 10 and both manifests bind the unchanged experiments to the line construction, normality observation and final collision checks.

## Appendix E: generated dimensions

The exact-integer script asserts the target degree, odd degree, Stage-B priced point and evaluation counts, coset size, point-set size, Barrett precision, transform schedule, powering length and Hamming weight, half-gcd cap, every outer decrement, tail degree, allocator closure and both upward roundings. No earlier row, total, memory peak or score is an input.

The complete configuration binding is `{"block": 2147483648, "cosets": 18, "ell": 9605400609, "h": 4294967296, "hgcd_cap": 31, "kappa": 12, "le": 64, "lmax": 12884901888, "lq": 24, "lx": 48, "vshift": 8589934592}`. Every value is present in the prose and in Appendix X; `validate()` binds it to the live geometry before either resource claim is formed.

## Appendix X.1: union-machine core

```python
from __future__ import annotations
from dataclasses import dataclass
from functools import cache
PALLAS_P = 28948022309329048855892746252171976963363056481941560715954676764349967630337
COUNTED_UNIT_TOKENS = frozenset({'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'sixteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'hundred', 'thousand'})
PLURAL_UNIT_TOKENS = frozenset({'loads', 'stores', 'addresses', 'updates', 'tests', 'branches', 'calls', 'returns', 'operations', 'bindings', 'fields', 'words', 'pairs', 'edges', 'steps', 'rounds', 'entries', 'bytes', 'coefficients', 'pointers', 'arguments', 'results', 'messages', 'digests', 'arrays', 'rows', 'loops', 'counters'})

def validate_unit_action_name(name: str) -> None:
    assert name and '_and_' not in name and ('_or_' not in name), name
    tokens = set(name.split('_'))
    assert not tokens.intersection(COUNTED_UNIT_TOKENS), name
    assert not tokens.intersection(PLURAL_UNIT_TOKENS), name

def unit_action_rows(*names: str) -> dict[str, int]:
    assert names and len(names) == len(set(names))
    for name in names:
        validate_unit_action_name(name)
    return {name: 1 for name in names}

@dataclass(frozen=True)
class ActionLoop:
    name: str
    iterations: int
    actions: tuple[str, ...]

    @property
    def total(self) -> int:
        assert self.iterations >= 0 and self.actions
        for action in self.actions:
            validate_unit_action_name(action)
        return self.iterations * len(self.actions)

def action_loop_rows(*loops: ActionLoop) -> dict[str, int]:
    assert loops and len({loop.name for loop in loops}) == len(loops)
    return {loop.name: loop.total for loop in loops}
POOL_REQUEST_SETUP_ACTIONS = {'loads_with_addresses': 24, 'stores_with_addresses': 16, 'pointer_and_address_updates': 24, 'comparisons': 12, 'branches': 12, 'call_and_return': 2, 'alignment_word_operations': 8, 'header_size_and_tag_operations': 10, 'statistics_counter_updates': 8, 'loop_entry_and_exit': 4}
POOL_EXAMINED_BLOCK_ACTIONS = {'header_load_and_address': 2, 'size_load_and_address': 2, 'live_flag_load_and_address': 2, 'comparisons': 2, 'selection_branch': 1, 'next_pointer_load_and_address': 2, 'loop_update_and_branch': 2}
POOL_FREE_ACTIONS = {'loads_with_addresses': 20, 'stores_with_addresses': 16, 'pointer_and_address_updates': 20, 'comparisons': 12, 'branches': 12, 'merge_metadata_operations': 8, 'statistics_counter_updates': 8, 'call_and_return': 2, 'loop_entry_update_and_exit': 7}

def pool_request_charge(examined_segments: int) -> int:
    assert examined_segments >= 0
    return 1 + sum(POOL_REQUEST_SETUP_ACTIONS.values()) + examined_segments * sum(POOL_EXAMINED_BLOCK_ACTIONS.values())

def pool_free_charge(find_segments: int, merge_segments: int, released_tail_segments: int) -> int:
    assert min(find_segments, merge_segments, released_tail_segments) >= 0
    find_unit = 6
    merge_unit = 7
    tail_unit = 5
    return sum(POOL_FREE_ACTIONS.values()) + find_segments * find_unit + merge_segments * merge_unit + released_tail_segments * tail_unit
SLAB_REQUEST_SETUP_ACTIONS = {'class_lookup_and_address': 2, 'slot_table_pointer_load_and_address': 2, 'entry_and_size_tests': 2, 'call_and_return': 2}
SLAB_EXAMINED_SLOT_ACTIONS = {'slot_flag_load_and_address': 2, 'free_test_and_branch': 2, 'next_slot_update_and_branch': 2}
SLAB_CREATE_SLOT_ACTIONS = {'capacity_test_and_branch': 2, 'slot_metadata_store_and_address': 2, 'class_capacity_update': 1}
SLAB_FREE_ACTIONS = {'class_and_slot_decode': 2, 'slot_flag_load_and_address': 2, 'live_test_and_branch': 2, 'slot_flag_store_and_address': 2, 'statistics_update': 1, 'call_and_return': 2}

def slab_request_charge(examined_slots: int, created_slot: bool) -> int:
    assert examined_slots >= 0
    return sum(SLAB_REQUEST_SETUP_ACTIONS.values()) + examined_slots * sum(SLAB_EXAMINED_SLOT_ACTIONS.values()) + int(created_slot) * sum(SLAB_CREATE_SLOT_ACTIONS.values())

def slab_free_charge() -> int:
    return sum(SLAB_FREE_ACTIONS.values())
STAGE_BOOKKEEPING_ACTIONS = action_loop_rows(ActionLoop('sixty_four_field_word_transfers', 64, ('first_load', 'second_load', 'first_store', 'second_store', 'source_pointer_update', 'destination_pointer_update')), ActionLoop('forty_eight_integer_word_transfers', 48, ('first_load', 'second_load', 'first_store', 'second_store')), ActionLoop('sixty_four_stage_control_steps', 64, ('comparison', 'branch', 'allocator_header_update', 'scalar_field_operation')), ActionLoop('thirty_two_call_edges', 32, ('call', 'return')), ActionLoop('twenty_six_loop_steps', 26, ('first_counter_update', 'second_counter_update', 'loop_test', 'loop_exit_branch')))
DRIVER_ENTRY_ACTIONS = {**STAGE_BOOKKEEPING_ACTIONS, 'trial_counter_load_and_address': 2, 'counter_increment': 1, 'limit_load_and_address': 2, 'limit_comparison': 1, 'loop_branch': 1, 'close_call_and_return': 2, 'stage_pointer_updates': 3}
NORMALIZATION_RETURN_ACTIONS = {'field_loads_with_addresses': 20, 'field_stores_with_addresses': 16, 'field_operations': 24, 'pointer_updates': 12, 'comparisons': 8, 'branches': 8, 'calls_and_returns': 4, 'loop_updates_tests_and_exit': 15}
DRIVER_EXIT_ACTIONS = {**{f'normalization_{name}': value for name, value in NORMALIZATION_RETURN_ACTIONS.items()}}
PLAN_DISPATCH_ACTIONS = {'operand_and_output_pointer_bindings': 8, 'length_and_window_loads': 6, 'plan_tag_tests_and_branches': 5, 'call_and_return': 4}
CALL_CLOSE_ACTIONS = {'entry_and_argument_bindings': 12, 'length_tests_and_branches': 10, 'pointer_updates': 8, 'calls_and_returns': 8, 'closing_tests': 4}
PLAN_DISPATCH = sum(PLAN_DISPATCH_ACTIONS.values())
CALL_CLOSE = sum(CALL_CLOSE_ACTIONS.values())
PRODUCT_FIXED_ACTIONS = {**{f'plan_{name}': value for name, value in PLAN_DISPATCH_ACTIONS.items()}, 'product_call_and_return': 6}
PRODUCT_FIXED = sum(PRODUCT_FIXED_ACTIONS.values())
ODD_DEGREE = 0

def loop8(count: int) -> int:
    assert count >= 0
    return 1 + 3 * (count // 8) + 2 + 3 * (count % 8) + 2

def linear_loop(count: int) -> int:
    assert count >= 0
    return 3 * count + 2

def pass_schedule(layers: int) -> tuple[tuple[int, int], ...]:
    assert layers >= 1
    first = layers % 7 or 7
    result = [(0, first)]
    level = first
    while level < layers:
        result.append((level, 7))
        level += 7
    return tuple(result)

def block_body_components(width: int) -> dict[str, int]:
    assert 1 <= width <= 7
    radix = 1 << width
    return {'input_load': radix, 'output_store': radix, 'butterfly_field_operations': 3 * width * (radix // 2), 'base_and_block_control': 3}

def block_body(width: int) -> int:
    return sum(block_body_components(width).values())

def running_chain(width: int) -> int:
    assert 1 <= width <= 7
    return (1 << width) + 4

def shared_running_pass(layers: int, level: int, width: int, inverse: bool=False) -> int:
    assert 0 <= level and 1 <= width <= 7 and (level + width <= layers)
    blocks = 1 << layers - width
    positions = 1 << layers - level - width
    fixed = 159 * width + (20 if inverse else 19)
    twiddle_one = positions * ((1 << width) - 1)
    return blocks * block_body(width) + positions * running_chain(width) + fixed - twiddle_one + 3

def per_block_upper_pass(layers: int, level: int, width: int, inverse: bool=False) -> int:
    assert 0 <= level and 1 <= width <= 7 and (level + width <= layers)
    blocks = 1 << layers - width
    group_zero = 1 << layers - level - width
    fixed = 159 * width + (20 if inverse else 19)
    return blocks * (block_body(width) + running_chain(width)) + fixed - group_zero * ((1 << width) - 1) + 3

def row_transform(layers: int, inverse: bool=False, per_block: bool=False) -> int:
    primitive = per_block_upper_pass if per_block else shared_running_pass
    return sum((primitive(layers, level, width, inverse) for level, width in pass_schedule(layers)))

def transform(points: int, inverse: bool=False, per_block: bool=False) -> int:
    if points & points - 1 == 0:
        return row_transform(points.bit_length() - 1, inverse, per_block)
    assert points % 3 == 0
    row = points // 3
    assert row & row - 1 == 0
    return 8 * row + 3 * row_transform(row.bit_length() - 1, inverse, per_block)

def admissible_points(required: int) -> tuple[int, ...]:
    choices = []
    for layers in range(1, 33):
        for points in (1 << layers, 3 * (1 << layers)):
            if points >= required:
                choices.append(points)
    return tuple(sorted(set(choices)))

def copy_cost(length: int) -> int:
    return 4 * length + linear_loop(length)

def zero_cost(length: int) -> int:
    return 2 * length + linear_loop(length)

def access_cost(length: int, subtract: bool) -> int:
    return (7 + int(subtract)) * length + linear_loop(length)
NODE_SIMPLE_POINT_ACTIONS = unit_action_rows('left_load', 'right_load', 'field_multiply', 'output_store', 'left_pointer_update', 'right_pointer_update', 'output_pointer_update')
NODE_EXTENDED_POINT_ACTIONS = unit_action_rows('left_load', 'right_load', 'modifier_load', 'first_field_multiply', 'second_field_multiply', 'field_add_subtract', 'output_store', 'left_pointer_update', 'right_pointer_update', 'output_pointer_update')

def pointwise_cost(length: int, row: int) -> int:
    actions = NODE_SIMPLE_POINT_ACTIONS if row == 0 else NODE_EXTENDED_POINT_ACTIONS
    return sum(actions.values()) * length + loop8(length)
BASE_ENTRY_ACTIONS = action_loop_rows(ActionLoop('six_remainder_array_bindings', 6, ('pointer_load', 'address', 'length_load', 'pointer_store')), ActionLoop('four_matrix_array_bindings', 4, ('pointer_load', 'address', 'length_load', 'pointer_store')), ActionLoop('eight_degree_budget_fields', 8, ('field_load', 'comparison', 'field_store')), ActionLoop('six_call_frame_fields', 6, ('frame_load', 'frame_store', 'pointer_update')), ActionLoop('four_entry_tests', 4, ('comparison', 'branch')))
BASE_STEP_SETUP_ACTIONS = action_loop_rows(ActionLoop('eight_quotient_fields', 8, ('load', 'address', 'field_operation', 'store')), ActionLoop('six_remainder_row_fields', 6, ('load', 'address', 'pointer_update', 'store')), ActionLoop('five_degree_tests', 5, ('comparison', 'branch')), ActionLoop('five_call_edges', 5, ('call', 'return')))
BASE_REMAINDER_COEFFICIENT_ACTIONS = unit_action_rows('a_load', 'a_address', 'b_load', 'b_address', 'q0_multiplication', 'q1_multiplication', 'first_subtraction', 'second_subtraction', 'result_store', 'result_address', 'loop_update', 'loop_test', 'loop_branch')
BASE_MATRIX_COEFFICIENT_ACTIONS = unit_action_rows('matrix_load', 'matrix_address', 'other_entry_load', 'other_entry_address', 'field_multiplication', 'field_addition', 'matrix_store', 'store_address', 'loop_control')
BASE_STEP_CLOSE_ACTIONS = action_loop_rows(ActionLoop('two_close_tests', 2, ('comparison', 'branch')), ActionLoop('two_close_calls', 2, ('call', 'return')))
BASE_FINAL_SETUP_ACTIONS = action_loop_rows(ActionLoop('five_final_field_bindings', 5, ('load', 'address', 'store')), ActionLoop('five_final_tests', 5, ('comparison', 'branch')))
BASE_FINAL_CLOSE_ACTIONS = action_loop_rows(ActionLoop('one_final_test', 1, ('comparison', 'branch')), ActionLoop('one_final_call', 1, ('call', 'return')))

def base_node() -> int:
    total = sum(BASE_ENTRY_ACTIONS.values())
    for removed in range(0, 62, 2):
        length = 2 * (62 - removed) + 1
        total += sum(BASE_STEP_SETUP_ACTIONS.values()) + sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) * length + sum(BASE_MATRIX_COEFFICIENT_ACTIONS.values()) * (length - 2) + linear_loop(length) + 2 * (sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) * (removed + 2) + sum(BASE_MATRIX_COEFFICIENT_ACTIONS.values()) * (removed + 3) + linear_loop(removed + 3)) + sum(BASE_STEP_CLOSE_ACTIONS.values())
    removed = 62
    return total + sum(BASE_FINAL_SETUP_ACTIONS.values()) + sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) + linear_loop(1) + 2 * (sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) * (removed + 2) + linear_loop(removed + 2)) + sum(BASE_FINAL_CLOSE_ACTIONS.values())
NODE_FIXED_EVENTS = action_loop_rows(ActionLoop('entry_and_exit', 10, ('entry_action', 'exit_action')), ActionLoop('split_and_degree_tests', 8, ('comparison', 'branch')), ActionLoop('two_child_call_frames', 2, ('argument_load', 'argument_address') * 6 + ('frame_store',) * 4 + ('return_pc_store', 'call', 'return', 'mark_load', 'mark_store', 'budget_load', 'budget_store', 'degree_load', 'degree_store')), ActionLoop('two_return_tests', 2, ('degree_load', 'budget_load', 'comparison', 'branch')), ActionLoop('arena_mark_and_release', 2, ('mark_load', 'mark_store', 'cursor_load', 'cursor_store', 'limit_load', 'comparison', 'branch', 'statistics_update', 'call', 'return')), ActionLoop('six_transform_dispatches', 6, ('plan_load', 'call', 'return')), ActionLoop('matrix_pointer_bundles', 8, ('pointer_load', 'address', 'length_load', 'pointer_store', 'offset_update', 'bound_store')), ActionLoop('row_and_sign_selection', 6, ('row_load', 'sign_test', 'branch')), ActionLoop('normal_sequence_tests', 6, ('comparison', 'branch')))

@dataclass(frozen=True)
class NodeRow:
    children: int
    top_rows: int
    returned_rows: int
    apply_pointwise: int
    matrix_pointwise: int
    inverses: int
    crt: int
    pseudo_division: int
    arrays: int
    fixed: int

    @property
    def total(self) -> int:
        return sum((self.children, self.top_rows, self.returned_rows, self.apply_pointwise, self.matrix_pointwise, self.inverses, self.crt, self.pseudo_division, self.arrays, self.fixed))
NODE_ROWS: dict[int, NodeRow] = {}

@cache
def node_bf(level: int) -> int:
    if level == 6:
        return base_node()
    assert level > 6
    n = 1 << level - 1
    layers = level - 1
    forward = row_transform(layers, per_block=True)
    inverse = row_transform(layers, inverse=True, per_block=True)

    def row(length: int, row_index: int) -> int:
        return copy_cost(min(length, n)) + zero_cost(max(0, n - length)) + access_cost(max(0, length - n), row_index == 2) + 2 * n * int(row_index > 0) + forward
    top = sum((row(1 << level + 1, r) + row((1 << level + 1) - 1, r) for r in range(3)))
    returned = (0, 1) if level == 7 else (1,)
    returns = 8 * sum((row(n, r) for r in returned))
    apply = 6 * (pointwise_cost(n, 0) + pointwise_cost(n, 2))
    matrix = 8 * (pointwise_cost(n, 0) + pointwise_cost(n, 1))
    inverses = 6 * sum((inverse + (1 + int(r > 0)) * n for r in range(3)))
    crt = 4 * (10 * n + linear_loop(n))
    budget = (1 << level) - 1
    pseudo = 30 + 13 * budget + linear_loop(budget)
    arrays = 2 * (25 * n + linear_loop(n))
    fixed = sum(NODE_FIXED_EVENTS.values())
    result = NodeRow(2 * node_bf(level - 1), top, returns, apply, matrix, inverses, crt, pseudo, arrays, fixed)
    NODE_ROWS[level] = result
    return result.total

@dataclass(frozen=True)
class ApplyCharge:
    points: int
    budget: int
    output: int
    transforms: int
    matrix_inputs: int
    operand_inputs: int
    pointwise: int
    output_loops: int
    fixed: int

    @property
    def total(self) -> int:
        return sum((self.transforms, self.matrix_inputs, self.operand_inputs, self.pointwise, self.output_loops, self.fixed))
FIXED_SLOT_POINT_ACTIONS = unit_action_rows('operand_left_load', 'operand_right_load', 'matrix_left_load', 'matrix_right_load', 'first_field_multiply', 'second_field_multiply', 'output_add_subtract', 'output_store', 'operand_left_pointer_update', 'operand_right_pointer_update', 'matrix_left_pointer_update', 'matrix_right_pointer_update')
DIRECT_POINT_ACTIONS = unit_action_rows('operand_a_address', 'operand_a_load', 'operand_b_address', 'operand_b_load', 'matrix_r11_address', 'matrix_r11_load', 'matrix_r12_address', 'matrix_r12_load', 'matrix_r21_address', 'matrix_r21_load', 'matrix_r22_address', 'matrix_r22_load', 'first_field_multiply', 'second_field_multiply', 'third_field_multiply', 'fourth_field_multiply', 'first_output_add_subtract', 'second_output_add_subtract', 'output_c_store', 'output_d_store')
DIRECT_PLACEMENT_ACTIONS = unit_action_rows('source_address', 'source_load', 'destination_address', 'destination_store', 'destination_pointer_update')
DIRECT_POINT_REQUIRED_MULTISET = {'operand_a_address': 1, 'operand_a_load': 1, 'operand_b_address': 1, 'operand_b_load': 1, 'matrix_r11_address': 1, 'matrix_r11_load': 1, 'matrix_r12_address': 1, 'matrix_r12_load': 1, 'matrix_r21_address': 1, 'matrix_r21_load': 1, 'matrix_r22_address': 1, 'matrix_r22_load': 1, 'first_field_multiply': 1, 'second_field_multiply': 1, 'third_field_multiply': 1, 'fourth_field_multiply': 1, 'first_output_add_subtract': 1, 'second_output_add_subtract': 1, 'output_c_store': 1, 'output_d_store': 1}
DIRECT_OUTPUT_ADDRESS_REUSE = {'output_c_store': 'operand_a_address', 'output_d_store': 'operand_b_address'}

def assert_required_action_multiset(actual: dict[str, int], required: dict[str, int]) -> None:
    assert actual == required, (actual, required)

def action_kind_count(actions: dict[str, int], kind: str) -> int:
    return sum((value for name, value in actions.items() if kind in name.split('_')))

def core_kernel_io_sweep() -> tuple[tuple[str, str, int, int, int], ...]:
    rows = []
    for width in range(1, 8):
        components = block_body_components(width)
        radix = 1 << width
        assert components['input_load'] == radix
        assert components['output_store'] == radix
        rows.append(('B/C/D', f'transform-block-width-{width}', sum(components.values()), radix, radix))
    for name, actions, loads, stores in (('node-simple-point', NODE_SIMPLE_POINT_ACTIONS, 2, 1), ('node-extended-point', NODE_EXTENDED_POINT_ACTIONS, 3, 1), ('fixed-slot-output-point', FIXED_SLOT_POINT_ACTIONS, 4, 1), ('direct-two-output-point', DIRECT_POINT_ACTIONS, 6, 2)):
        assert action_kind_count(actions, 'load') == loads
        assert action_kind_count(actions, 'store') == stores
        rows.append(('D', name, sum(actions.values()), loads, stores))
    return tuple(rows)
CORE_KERNEL_IO_SWEEP = core_kernel_io_sweep()

@dataclass(frozen=True)
class OuterStep:
    degree: int
    level: int
    budget: int
    node: int
    apply: ApplyCharge
    driver: int

    @property
    def total(self) -> int:
        return self.node + self.apply.total + self.driver

def classical_tail(degree: int) -> int:
    return sum((16 * d + 27 for d in range(1, degree + 1)))

def normalization() -> int:
    return 512 * 5 + 5 * 17 + 8
```

## Appendix X.2: exact-integer ledger

```python
#!/usr/bin/env python3
"""Exact-integer union ledger for the r10-v11 construction.

Every operation and memory row is generated from the declared r10 dimensions,
named primitive actions, immutable apply plans and allocator events. Reference
submission values are not ledger inputs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, getcontext
from functools import cache
from pathlib import Path

import ledger_base as H
import ledger_core as U


getcontext().prec = 90
ROUND = 10
CFG = dict(H.CONFIGS[ROUND])

OMEGA_TABLE_ENTRY_ACTIONS = U.action_loop_rows(
    U.ActionLoop("two_source_words", 2, ("source_address", "source_load")),
    U.ActionLoop("one_power_step", 1, ("field_multiply",)),
    U.ActionLoop("one_destination", 1, ("destination_address", "destination_store")),
    U.ActionLoop("sixteen_bit_reversal_steps", 16, ("bit_reversal_step",)),
    U.ActionLoop("entry_and_loop_close", 1, ("entry_action", "loop_close")),
)
OMEGA_BOUNDARY_ACTIONS = U.action_loop_rows(
    U.ActionLoop("four_row_factors", 4,
                 ("first_table_load", "second_table_load", "field_multiply")),
)
BATCH_COEFFICIENT_ACTIONS = U.unit_action_rows(
    "prefix_address", "prefix_load", "value_address", "value_load",
    "prefix_multiply", "prefix_store", "backward_prefix_load",
    "backward_value_load", "first_backward_multiply",
    "second_backward_multiply", "field_negation", "inverse_store",
    "loop_update", "loop_branch",
)
BATCH_CHUNK_ACTIONS = U.action_loop_rows(
    U.ActionLoop("chunk_entry_and_zero_test", 1,
                 ("entry_action", "zero_test", "zero_branch")),
    U.ActionLoop("chunk_bounds", 1,
                 ("bound_load", "comparison", "branch")),
    U.ActionLoop("chunk_pointer_setup", 3,
                 ("pointer_load", "pointer_store")),
    U.ActionLoop("chunk_inversion_call", 1,
                 ("call", "return", "status_load", "status_store")),
    U.ActionLoop("chunk_close", 1,
                 ("loop_update", "comparison", "branch", "return")),
)

# The active adaptive apply owns these action structures.  None of the
# coefficients below is borrowed from the inactive FixedSlotApplyPlan in the
# shared core.
ADAPTIVE_COPY_COEFFICIENT_ACTIONS = U.unit_action_rows(
    "source_address", "source_load", "destination_address",
    "destination_store", "source_pointer_update",
    "destination_pointer_update", "loop_update",
)
ADAPTIVE_ZERO_COEFFICIENT_ACTIONS = U.unit_action_rows(
    "destination_address", "destination_store",
    "destination_pointer_update", "loop_comparison", "loop_branch",
)
ADAPTIVE_FOLD_COEFFICIENT_ACTIONS = U.unit_action_rows(
    "source_address", "source_load", "destination_address",
    "destination_load", "field_add", "destination_store",
    "source_pointer_update", "destination_pointer_update",
    "loop_comparison", "loop_branch",
)
ADAPTIVE_FIXED_POINT_ACTIONS = U.unit_action_rows(
    "operand_a_address", "operand_a_load",
    "operand_b_address", "operand_b_load",
    "matrix_r11_address", "matrix_r11_load",
    "matrix_r12_address", "matrix_r12_load",
    "matrix_r21_address", "matrix_r21_load",
    "matrix_r22_address", "matrix_r22_load",
    "first_field_multiply", "second_field_multiply",
    "third_field_multiply", "fourth_field_multiply",
    "first_output_add_subtract", "second_output_add_subtract",
    "output_c_address", "output_c_store",
    "output_d_address", "output_d_store",
    "output_c_pointer_update", "output_d_pointer_update",
)
ADAPTIVE_PLACEMENT_COEFFICIENT_ACTIONS = U.unit_action_rows(
    "source_address", "source_load", "scale_load", "field_multiply",
    "destination_address", "destination_store",
    "destination_pointer_update", "loop_update",
)
ADAPTIVE_PLACEMENT_CLOSE_ACTIONS = U.unit_action_rows(
    "counter_load", "comparison", "branch", "call", "return",
)
ADAPTIVE_SLOT_PLACEMENT_CLOSE_ACTIONS = U.action_loop_rows(
    U.ActionLoop("four_output_fragments", 4,
                 ("counter_load", "comparison", "branch", "call", "return")),
)
ADAPTIVE_ENTRY_ACTIONS = U.action_loop_rows(
    U.ActionLoop("ten_entry_records", 10,
                 ("argument_load", "argument_store", "pointer_load",
                  "pointer_store", "length_load", "length_store",
                  "comparison", "branch")),
)
ADAPTIVE_SCALE_PLAN_ACTIONS = U.action_loop_rows(
    U.ActionLoop("sixty_four_scale_records", 64,
                 ("scale_load", "scale_store", "pointer_load",
                  "pointer_store", "counter_update", "comparison", "branch")),
)
ADAPTIVE_LENGTH_CHECK_ACTIONS = U.action_loop_rows(
    U.ActionLoop("eleven_length_checks", 11, ("comparison", "branch")),
)
ADAPTIVE_SLOT_CONTROL_ACTIONS = U.unit_action_rows(
    "counter_update", "comparison", "branch",
)
ADAPTIVE_CALL_CLOSE_ACTIONS = U.unit_action_rows(
    "status_load", "status_store", "counter_update",
    "comparison", "branch", "return",
)
ADAPTIVE_PLANNER_CANDIDATE_ACTIONS = U.unit_action_rows(
    "exponent_load", "point_count_compute", "matrix_limit_load",
    "matrix_limit_comparison", "direct_limit_comparison",
    "slot_compute", "candidate_store", "counter_update",
)
ADAPTIVE_PLANNER_CLOSE_ACTIONS = U.action_loop_rows(
    U.ActionLoop("six_winner_records", 6,
                 ("winner_load", "winner_store", "comparison")),
)
ADAPTIVE_ALLOCATOR_REQUEST_SETUP_ACTIONS = U.action_loop_rows(
    U.ActionLoop("one_request_statement", 1, ("call",)),
    U.ActionLoop("twelve_request_records", 12,
                 ("first_load", "second_load", "first_store", "second_store",
                  "pointer_update", "address_update", "comparison", "branch",
                  "alignment_operation", "header_operation")),
)
ADAPTIVE_ALLOCATOR_EXAMINED_SEGMENT_ACTIONS = U.unit_action_rows(
    "header_address", "header_load", "size_address", "size_load",
    "live_flag_address", "live_flag_load", "first_comparison",
    "second_comparison", "selection_branch", "next_pointer_address",
    "next_pointer_load", "loop_update", "loop_branch",
)
ADAPTIVE_ALLOCATOR_FREE_SETUP_ACTIONS = U.action_loop_rows(
    U.ActionLoop("fifteen_free_records", 15,
                 ("first_load", "second_load", "first_store", "second_store",
                  "pointer_update", "comparison", "branch")),
)
ADAPTIVE_ALLOCATOR_FIND_SEGMENT_ACTIONS = U.unit_action_rows(
    "header_address", "header_load", "name_comparison",
    "live_comparison", "pointer_update", "branch",
)
ADAPTIVE_ALLOCATOR_MERGE_SEGMENT_ACTIONS = U.unit_action_rows(
    "first_header_load", "second_header_load", "live_comparison",
    "size_add", "header_store", "pointer_update", "branch",
)
ADAPTIVE_ALLOCATOR_RELEASE_SEGMENT_ACTIONS = U.unit_action_rows(
    "tail_load", "live_comparison", "extent_store", "pointer_update", "branch",
)
assert sum(OMEGA_TABLE_ENTRY_ACTIONS.values()) == 25
assert sum(OMEGA_BOUNDARY_ACTIONS.values()) == 12
assert sum(BATCH_COEFFICIENT_ACTIONS.values()) == 14
assert sum(BATCH_CHUNK_ACTIONS.values()) == 20
assert sum(ADAPTIVE_COPY_COEFFICIENT_ACTIONS.values()) == 7
assert sum(ADAPTIVE_ZERO_COEFFICIENT_ACTIONS.values()) == 5
assert sum(ADAPTIVE_FOLD_COEFFICIENT_ACTIONS.values()) == 10
assert sum(ADAPTIVE_FIXED_POINT_ACTIONS.values()) == 24
assert sum(ADAPTIVE_PLACEMENT_COEFFICIENT_ACTIONS.values()) == 8
assert sum(ADAPTIVE_PLACEMENT_CLOSE_ACTIONS.values()) == 5
assert sum(ADAPTIVE_SLOT_PLACEMENT_CLOSE_ACTIONS.values()) == 20
assert sum(ADAPTIVE_ENTRY_ACTIONS.values()) == 80
assert sum(ADAPTIVE_SCALE_PLAN_ACTIONS.values()) == 448
assert sum(ADAPTIVE_LENGTH_CHECK_ACTIONS.values()) == 22
assert sum(ADAPTIVE_SLOT_CONTROL_ACTIONS.values()) == 3
assert sum(ADAPTIVE_CALL_CLOSE_ACTIONS.values()) == 6
assert sum(ADAPTIVE_PLANNER_CANDIDATE_ACTIONS.values()) == 8
assert sum(ADAPTIVE_PLANNER_CLOSE_ACTIONS.values()) == 18
assert sum(ADAPTIVE_ALLOCATOR_REQUEST_SETUP_ACTIONS.values()) == 121
assert sum(ADAPTIVE_ALLOCATOR_EXAMINED_SEGMENT_ACTIONS.values()) == 13
assert sum(ADAPTIVE_ALLOCATOR_FREE_SETUP_ACTIONS.values()) == 105
assert sum(ADAPTIVE_ALLOCATOR_FIND_SEGMENT_ACTIONS.values()) == 6
assert sum(ADAPTIVE_ALLOCATOR_MERGE_SEGMENT_ACTIONS.values()) == 7
assert sum(ADAPTIVE_ALLOCATOR_RELEASE_SEGMENT_ACTIONS.values()) == 5


def ceil5(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.00001"), rounding=ROUND_CEILING)


def request_bytes(words: int) -> int:
    return ((words * 32 + 63) // 64) * 64 + 64


@cache
def optimized_widths(layers: int, per_block: bool) -> tuple[int, ...]:
    """Least-charge partition into widths at most seven.

    The objective is the sum of this package's independently derived forward
    and inverse pass formulas.  Ties choose the lexicographically smaller
    width sequence, so the plan is deterministic.
    """
    best: dict[int, tuple[int, tuple[int, ...]]] = {layers: (0, ())}
    for level in range(layers - 1, -1, -1):
        candidates = []
        for width in range(1, min(7, layers - level) + 1):
            primitive = (U.per_block_upper_pass if per_block
                         else U.shared_running_pass)
            charge = (primitive(layers, level, width, False)
                      + primitive(layers, level, width, True))
            tail_charge, tail_widths = best[level + width]
            candidates.append((charge + tail_charge,
                               (width,) + tail_widths))
        best[level] = min(candidates)
    return best[0][1]


def optimized_schedule(layers: int, per_block: bool) -> tuple[tuple[int, int], ...]:
    level = 0
    rows = []
    for width in optimized_widths(layers, per_block):
        rows.append((level, width))
        level += width
    assert level == layers
    return tuple(rows)


@cache
def optimized_row_transform(layers: int, inverse: bool = False,
                            per_block: bool = False) -> int:
    primitive = U.per_block_upper_pass if per_block else U.shared_running_pass
    return sum(primitive(layers, level, width, inverse)
               for level, width in optimized_schedule(layers, per_block))


@cache
def optimized_transform(points: int, inverse: bool = False,
                        per_block: bool = False) -> int:
    if points & (points - 1) == 0:
        return optimized_row_transform(points.bit_length() - 1,
                                       inverse, per_block)
    assert points % 3 == 0
    row = points // 3
    assert row & (row - 1) == 0
    return (8 * row + 3 * optimized_row_transform(
        row.bit_length() - 1, inverse, per_block,
    ))


COLUMN_CONSTANTS = {1: 5, 2: 6, 3: 10, 4: 18, 5: 34, 6: 139, 7: 269}
COLUMN_SLOPES = {1: 11, 2: 20, 3: 52, 4: 128, 5: 304, 6: 704, 7: 1600}


@cache
def column_widths(layers: int, positions: int) -> tuple[int, ...]:
    groups = (positions + 1023) // 1024
    best: dict[int, tuple[int, tuple[int, ...]]] = {layers: (0, ())}
    for level in range(layers - 1, -1, -1):
        candidates = []
        for width in range(1, min(7, layers - level) + 1):
            rows = 1 << width
            charge = (COLUMN_SLOPES[width] * positions
                      + groups * (COLUMN_CONSTANTS[width] + 2 * rows + 11)
                      + U.loop8(positions))
            tail, widths = best[level + width]
            candidates.append((charge + tail, (width,) + widths))
        best[level] = min(candidates)
    return best[0][1]


def optimized_col_transform(points: int, positions: int,
                            inverse: bool = False) -> int:
    radix3 = points % 3 == 0
    row = points // 3 if radix3 else points
    assert row & (row - 1) == 0
    groups = (positions + 1023) // 1024
    total = 25 * positions + 23 * groups if radix3 else 0
    for width in column_widths(row.bit_length() - 1, positions):
        rows = 1 << width
        total += (COLUMN_SLOPES[width] * positions
                  + groups * (COLUMN_CONSTANTS[width] + 2 * rows + 11)
                  + U.loop8(positions))
    if inverse:
        total += positions
    return total


def partial_forward(length: int, points: int) -> int:
    assert points % 3 == 0 and 0 < length <= points
    row = points // 3
    return (6 + 8 * ((length + 2) // 3)
            + 3 * optimized_row_transform(row.bit_length() - 1))


def partial_inverse(output: int, points: int) -> int:
    assert points % 3 == 0 and 0 < output <= points
    row = points // 3
    return (3 + 3 * optimized_row_transform(row.bit_length() - 1, True)
            + 8 * ((output + 2) // 3))


def adaptive_allocator_rows(arrays: int) -> dict[str, int]:
    """Price the branch-local six-array trace from atomic action families."""
    assert arrays >= 0
    request_setup = sum(ADAPTIVE_ALLOCATOR_REQUEST_SETUP_ACTIONS.values())
    examined = sum(ADAPTIVE_ALLOCATOR_EXAMINED_SEGMENT_ACTIONS.values())
    free_setup = sum(ADAPTIVE_ALLOCATOR_FREE_SETUP_ACTIONS.values())
    find = sum(ADAPTIVE_ALLOCATOR_FIND_SEGMENT_ACTIONS.values())
    merge = sum(ADAPTIVE_ALLOCATOR_MERGE_SEGMENT_ACTIONS.values())
    release = sum(ADAPTIVE_ALLOCATOR_RELEASE_SEGMENT_ACTIONS.values())
    rows = {
        "requests": sum(request_setup + index * examined
                        for index in range(arrays)),
        "frees": sum(free_setup + index * find + index * merge + release
                     for index in range(arrays, 0, -1)),
    }
    assert rows["requests"] == sum(
        U.pool_request_charge(index) for index in range(arrays)
    )
    assert rows["frees"] == sum(
        U.pool_free_charge(index, index, 1)
        for index in range(arrays, 0, -1)
    )
    return rows


def adaptive_allocator_total(arrays: int) -> int:
    return sum(adaptive_allocator_rows(arrays).values())


@dataclass(frozen=True)
class ApplyPlan:
    kind: str
    points: int
    degree: int
    budget: int
    blocks: int
    tested_sizes: int
    rows: tuple[tuple[str, int], ...]

    @property
    def total(self) -> int:
        return sum(value for _name, value in self.rows)

    @property
    def temporary_bytes(self) -> int:
        return 6 * request_bytes(self.points)

    def operation_rows(self) -> dict[str, int]:
        return dict(self.rows)

    def allocation_arrays(self) -> tuple[tuple[str, int, str, str], ...]:
        return tuple(
            (f"matrix-{entry}-spectrum", self.points,
             "matrix coefficient form", "L")
            for entry in ("r11", "r12", "r21", "r22")
        ) + (
            ("operand-a-spectrum-output-c", self.points,
             "operand a then output c", "H"),
            ("operand-b-spectrum-output-d", self.points,
             "operand b then output d", "H"),
        )


APPLY_PLANS: dict[tuple[int, int], ApplyPlan] = {}
APPLY_PLANNER_CHARGES: dict[tuple[int, int], int] = {}
OUTER_DRIVER_ROWS: dict[tuple[int, int], dict[str, int]] = {}
PLANNER_ROWS: tuple[tuple[str, tuple[int, ...], int], ...] = ()


@cache
def adaptive_apply(degree: int, budget: int) -> U.ApplyCharge:
    """Enumerate every direct and fixed-slot 3*2^e plan from the proof rule."""
    matrix_lengths = (budget + 1, budget, budget, max(1, budget - 1))
    output_c = degree - budget
    output_d = output_c - 1
    candidates: list[tuple[U.ApplyCharge, str, int, tuple[tuple[str, int], ...]]] = []
    tested = 0
    for exponent in range(2, 33):
        points = 3 * (1 << exponent)
        tested += 1
        if points < matrix_lengths[0]:
            continue
        matrix_forward = sum(partial_forward(length, points)
                             for length in matrix_lengths)
        copy_actions = sum(ADAPTIVE_COPY_COEFFICIENT_ACTIONS.values())
        zero_actions = sum(ADAPTIVE_ZERO_COEFFICIENT_ACTIONS.values())
        fold_actions = sum(ADAPTIVE_FOLD_COEFFICIENT_ACTIONS.values())
        placement_actions = sum(
            ADAPTIVE_PLACEMENT_COEFFICIENT_ACTIONS.values()
        )
        placement_close = sum(ADAPTIVE_PLACEMENT_CLOSE_ACTIONS.values())
        matrix_input = sum(
            copy_actions * length + zero_actions * (points - length)
            for length in matrix_lengths
        )
        if points >= output_c:
            operand_input = 2 * (
                copy_actions * points
                + fold_actions * max(0, degree + 1 - points)
            )
            transforms = (matrix_forward + 2 * partial_forward(points, points)
                          + partial_inverse(output_c, points)
                          + partial_inverse(output_d, points))
            pointwise = (sum(U.DIRECT_POINT_ACTIONS.values()) * points
                         + U.loop8(points))
            placement = (placement_actions * output_c + placement_close
                         + placement_actions * output_d + placement_close)
            fixed = (
                sum(ADAPTIVE_ENTRY_ACTIONS.values())
                + sum(ADAPTIVE_SCALE_PLAN_ACTIONS.values())
                + sum(ADAPTIVE_LENGTH_CHECK_ACTIONS.values())
                + adaptive_allocator_total(len(ApplyPlan(
                    "direct", points, degree, budget, 1, tested, (),
                ).allocation_arrays()))
            )
            charge = U.ApplyCharge(points, budget, output_c, transforms,
                                   matrix_input, operand_input, pointwise,
                                   placement, fixed)
            rows = (
                ("transforms", transforms),
                ("matrix_inputs", matrix_input),
                ("operand_inputs", operand_input),
                ("fused_two_output_pointwise", pointwise),
                ("output_scaling_and_placement", placement),
                ("entry_allocator_and_close", fixed),
            )
            assert sum(value for _name, value in rows) == charge.total
            candidates.append((charge, "direct", 1, rows))
        slot = points - budget
        if slot > 0:
            blocks = (output_c + slot - 1) // slot
            operand_input = 0
            transforms = matrix_forward
            pointwise = 0
            placement = 0
            for index in range(blocks - 1, -1, -1):
                low = max(0, index * slot - budget)
                high = min((index + 1) * slot, output_c)
                window = high - low
                assert 0 < window <= points
                operand_input += 2 * (
                    copy_actions * window
                    + zero_actions * (points - window)
                )
                transforms += 2 * partial_forward(window, points)
                formed = points if index else min(slot, output_c)
                transforms += 2 * partial_inverse(formed, points)
                pointwise += (
                    sum(ADAPTIVE_FIXED_POINT_ACTIONS.values()) * points
                    + U.loop8(points)
                )
                placed_c = min(slot, output_c - index * slot)
                placed_d = min(slot, max(0, output_d - index * slot))
                placement += (
                    placement_actions * placed_c + placement_close
                    + placement_actions * placed_d + placement_close
                    + sum(ADAPTIVE_SLOT_PLACEMENT_CLOSE_ACTIONS.values())
                )
            fixed = (
                sum(ADAPTIVE_ENTRY_ACTIONS.values())
                + sum(ADAPTIVE_SCALE_PLAN_ACTIONS.values())
                + sum(ADAPTIVE_LENGTH_CHECK_ACTIONS.values())
                + sum(ADAPTIVE_SLOT_CONTROL_ACTIONS.values()) * blocks
                + sum(ADAPTIVE_CALL_CLOSE_ACTIONS.values())
                + adaptive_allocator_total(len(ApplyPlan(
                    "fixed", points, degree, budget, blocks, tested, (),
                ).allocation_arrays()))
            )
            charge = U.ApplyCharge(points, budget, output_c, transforms,
                                   matrix_input, operand_input, pointwise,
                                   placement, fixed)
            rows = (
                ("transforms", transforms),
                ("matrix_inputs", matrix_input),
                ("operand_window_inputs", operand_input),
                ("fused_two_output_pointwise", pointwise),
                ("descending_slot_placement", placement),
                ("entry_allocator_and_close", fixed),
            )
            assert sum(value for _name, value in rows) == charge.total
            candidates.append((charge, "fixed", blocks, rows))
        if points >= output_c:
            break
    selected, kind, blocks, selected_rows = min(
        candidates, key=lambda row: (row[0].total, row[0].points, row[1])
    )
    planner = (
        tested * sum(ADAPTIVE_PLANNER_CANDIDATE_ACTIONS.values())
        + U.loop8(tested)
        + sum(ADAPTIVE_PLANNER_CLOSE_ACTIONS.values())
    )
    APPLY_PLANNER_CHARGES[(degree, budget)] = planner
    APPLY_PLANS[(degree, budget)] = ApplyPlan(
        kind, selected.points, degree, budget, blocks, tested, selected_rows,
    )
    return selected


def stage_d() -> tuple[int, tuple[U.OuterStep, ...], dict[str, int]]:
    m = (5 ** 16 - 1) // 2
    U.ODD_DEGREE = m
    U.NODE_ROWS.clear()
    U.node_bf.cache_clear()
    adaptive_apply.cache_clear()
    APPLY_PLANS.clear()
    APPLY_PLANNER_CHARGES.clear()
    OUTER_DRIVER_ROWS.clear()
    degree = m
    steps = []
    while True:
        chosen = None
        for level in range(31, 6, -1):
            budget = (1 << level) - 1
            if 2 * budget + 1 <= degree:
                chosen = level, budget
                break
        if chosen is None:
            break
        level, budget = chosen
        apply = adaptive_apply(degree, budget)
        post = degree - budget
        driver = (sum(H.OUTER_DIVISION_COEFFICIENT_ACTIONS.values()) * post
                  + sum(H.OUTER_QUOTIENT_TEST_ACTIONS.values())
                  + sum(H.OUTER_DRIVER_FIXED_ACTIONS.values()))
        # The bump reservation is released before the apply.  Four coefficient
        # matrix entries remain, with their exact copy/allocation loops.
        matrix_words = 4 * (budget + 1)
        matrix_lengths = (budget + 1, budget, budget, max(1, budget - 1))
        assert sum(matrix_lengths) == matrix_words - 4
        matrix_handoff = (
            sum(ADAPTIVE_COPY_COEFFICIENT_ACTIONS.values()) * matrix_words
            + U.loop8(matrix_words)
            + adaptive_allocator_total(len(matrix_lengths))
            + adaptive_allocator_total(len((matrix_words,)))
        )
        OUTER_DRIVER_ROWS[(degree, budget)] = {
            "post_node_length": post,
            "linear_division": (
                sum(H.OUTER_DIVISION_COEFFICIENT_ACTIONS.values()) * post
            ),
            "quotient_degree_test": sum(H.OUTER_QUOTIENT_TEST_ACTIONS.values()),
            "fixed_driver_actions": sum(H.OUTER_DRIVER_FIXED_ACTIONS.values()),
            "matrix_handoff": matrix_handoff,
        }
        steps.append(U.OuterStep(degree, level, budget, U.node_bf(level),
                                 apply, driver + matrix_handoff))
        degree -= budget + 1
    rows = {
        "outer_steps": sum(step.total for step in steps),
        "classical_euclid": U.classical_tail(degree),
        "normalization": U.normalization(),
        "entry": sum(U.DRIVER_ENTRY_ACTIONS.values()),
        "exit_and_frees": sum(U.DRIVER_EXIT_ACTIONS.values()),
    }
    return sum(rows.values()), tuple(steps), rows


def stage_c() -> tuple[int, dict[str, int]]:
    total, rows = H.stage_c(ROUND, CFG)
    rows = dict(rows)
    old_tables = rows["tables_and_plans"]
    new_tables = (
        2 * (1 << 16) * sum(OMEGA_TABLE_ENTRY_ACTIONS.values())
        + 30 * CFG["cosets"] * (512 * 5 + 8)
        + 20 * (CFG["le"] + CFG["lq"] + CFG["lx"])
        + sum(U.STAGE_BOOKKEEPING_ACTIONS.values())
    )
    rows["tables_and_plans"] = new_tables
    # Two table loads with addresses and one multiplication for each of four
    # row factors cost twelve extra actions in each b=1 boundary call.
    rows["powering_loop"] += 45 * sum(OMEGA_BOUNDARY_ACTIONS.values())
    n1 = CFG["h"] * CFG["cosets"]
    chunks = (n1 + (1 << 16) - 1) // (1 << 16)
    rows["batch_inversion"] = (
        sum(BATCH_COEFFICIENT_ACTIONS.values()) * n1 + U.loop8(n1)
        + chunks * (512 * 5 + sum(BATCH_CHUNK_ACTIONS.values()))
    )
    return sum(rows.values()), rows


class ArenaTrace:
    """Two-ended first-fit pool plus mechanically selected slab classes."""

    def __init__(self) -> None:
        self.pool_threshold = 1 << 24
        self.pools = {"L": [], "H": []}
        self.extents = {"L": 0, "H": 0}
        self.slots: dict[int, list[bool]] = {}
        self.slab_peak_live: dict[int, int] = {}
        self.live: dict[str, tuple[str, int, int | None]] = {}
        self.events: list[tuple] = []
        self.roles: list[tuple] = []
        self.allocator_events: list[dict[str, int | str | bool]] = []
        self.stage_peaks: dict[str, int] = {}
        self.pool_peak = 0

    def reserved(self) -> int:
        return self.extents["L"] + self.extents["H"] + sum(
            size * len(slots) for size, slots in self.slots.items()
        )

    def live_bytes(self) -> int:
        return sum(row[1] for row in self.live.values())

    def record(self, stage: str, action: str, name: str,
               region: str, amount: int) -> None:
        live = self.live_bytes()
        self.stage_peaks[stage] = max(self.stage_peaks.get(stage, 0), live)
        self.events.append((len(self.events) + 1, stage, action, name,
                            region, amount, live, self.extents["L"],
                            self.extents["H"], self.reserved()))

    def alloc(self, stage: str, name: str, words: int,
              side: str = "L") -> None:
        assert name not in self.live and words >= 1
        need = request_bytes(words)
        if need <= self.pool_threshold:
            size = 1 << max(7, (need - 1).bit_length())
            slots = self.slots.setdefault(size, [])
            examined = 0
            slot = None
            for candidate, occupied in enumerate(slots):
                examined += 1
                if not occupied:
                    slot = candidate
                    break
            created = slot is None
            if created:
                slot = len(slots)
                slots.append(True)
            else:
                slots[slot] = True
            self.slab_peak_live[size] = max(
                self.slab_peak_live.get(size, 0), sum(slots)
            )
            region = f"S{size.bit_length()-1}:{slot}"
            self.live[name] = (region, size, size)
            self.allocator_events.append({
                "stage": stage, "action": "slab-alloc", "name": name,
                "examined": examined, "created": created,
                "charge": U.slab_request_charge(examined, created),
            })
            self.record(stage, "alloc", name, region.split(":")[0], size)
            return
        segments = self.pools[side]
        examined = 0
        for index, segment in enumerate(segments):
            examined += 1
            if not segment["live"] and int(segment["size"]) >= need:
                start = int(segment["start"])
                remainder = int(segment["size"]) - need
                replacement = [{"start": start, "size": need,
                                "name": name, "live": True}]
                if remainder:
                    replacement.append({"start": start + need,
                                        "size": remainder, "name": None,
                                        "live": False})
                segments[index:index + 1] = replacement
                break
        else:
            segments.append({"start": self.extents[side], "size": need,
                             "name": name, "live": True})
            self.extents[side] += need
        self.pool_peak = max(self.pool_peak,
                             self.extents["L"] + self.extents["H"])
        self.live[name] = (side, need, None)
        self.allocator_events.append({
            "stage": stage, "action": "pool-alloc", "name": name,
            "examined": examined, "created": False,
            "charge": U.pool_request_charge(examined),
        })
        self.record(stage, "alloc", name, side, need)

    def free(self, stage: str, name: str) -> None:
        side, amount, slab_size = self.live.pop(name)
        if slab_size is not None:
            prefix, slot_text = side.split(":")
            slot = int(slot_text)
            assert self.slots[slab_size][slot]
            self.slots[slab_size][slot] = False
            self.allocator_events.append({
                "stage": stage, "action": "slab-free", "name": name,
                "examined": 0, "created": False,
                "charge": U.slab_free_charge(),
            })
            self.record(stage, "free", name, prefix, amount)
            return
        segments = self.pools[side]
        match = None
        find_examined = 0
        for segment in segments:
            find_examined += 1
            if segment["live"] and segment["name"] == name:
                match = segment
                break
        assert match is not None
        match["live"] = False
        match["name"] = None
        merge_examined = len(segments)
        merged = []
        for segment in segments:
            if merged and not merged[-1]["live"] and not segment["live"]:
                merged[-1]["size"] = int(merged[-1]["size"]) + int(segment["size"])
            else:
                merged.append(segment)
        released = 0
        while merged and not merged[-1]["live"]:
            self.extents[side] = int(merged[-1]["start"])
            merged.pop()
            released += 1
        segments[:] = merged
        self.allocator_events.append({
            "stage": stage, "action": "pool-free", "name": name,
            "examined": find_examined, "merge_examined": merge_examined,
            "released_tail": released, "created": False,
            "charge": U.pool_free_charge(find_examined, merge_examined,
                                           released),
        })
        self.record(stage, "free", name, side, amount)

    def reuse(self, stage: str, name: str, old: str, new: str) -> None:
        assert name in self.live
        self.roles.append((len(self.roles) + 1, stage, name, old, new))


def memory(steps: tuple[U.OuterStep, ...]) -> tuple[int, dict[str, object]]:
    trace = ArenaTrace()
    n1 = CFG["h"] * CFG["cosets"]
    m = (5 ** 16 - 1) // 2
    block = 3 * (1 << 31)

    trace.alloc("B", "B-values", CFG["kappa"] * block, "H")
    trace.alloc("B", "stage-B-twiddle-table", block // 2, "H")
    trace.alloc("B", "g-coefficients", m + 1, "L")
    trace.free("B", "stage-B-twiddle-table")
    trace.free("B", "B-values")

    trace.alloc("C", "g-value-padding", n1 - (m + 1), "L")
    trace.alloc("C", "newton-reversed", CFG["ell"], "L")
    trace.alloc("C", "newton-reciprocal", CFG["ell"], "L")
    trace.alloc("C", "newton-scratch-a", CFG["ell"], "H")
    trace.alloc("C", "newton-scratch-b", CFG["ell"], "H")
    product_ranges = []

    def emit_product(index: int, plan, start: int | None = None) -> None:
        first = len(trace.events) + 1 if start is None else start
        for action, suffix, words, role in plan.allocation_schedule():
            name = f"C-product-{index}-{suffix}"
            if action == "alloc":
                trace.alloc("C", name, words, "H")
                trace.reuse("C", name, "allocated", role)
            else:
                trace.free("C", name)
        product_ranges.append((index, first, len(trace.events), plan.mode,
                               plan.left, plan.right, plan.output, plan.points))

    product_plans = tuple(H.PRODUCT_PLANS.values())
    assert len(product_plans) == 69
    for index, plan in enumerate(product_plans[:-1], 1):
        emit_product(index, plan)
    trace.free("C", "newton-scratch-b")
    trace.free("C", "newton-scratch-a")
    # Product 69 is the quotient product.  Its coefficient destination and
    # the later value-domain R1 destination are live for the complete call.
    quotient_start = len(trace.events) + 1
    trace.alloc("C", "R1-q-values", n1, "H")
    trace.alloc("C", "barrett-quotient", CFG["ell"], "H")
    trace.reuse("C", "barrett-quotient", "allocated",
                "quotient-product coefficient destination")
    trace.reuse("C", "R1-q-values", "allocated",
                "quotient-product value destination")
    emit_product(len(product_plans), product_plans[-1], quotient_start)
    trace.reuse("C", "barrett-quotient",
                "quotient-product coefficient destination",
                "completed quotient coefficients")
    trace.reuse("C", "R1-q-values", "quotient-product value destination",
                "q on O2")
    trace.free("C", "barrett-quotient")
    trace.free("C", "newton-reciprocal")
    trace.free("C", "newton-reversed")
    # Step 2 consumes q on O2 together with R2, so R2 is allocated here.
    trace.alloc("C", "R2", n1, "H")
    trace.alloc("C", "G1", n1, "L")
    trace.alloc("C", "stage-C-coset-scalars", 30 * CFG["cosets"], "H")
    trace.alloc("C", "omega-table-high", 1 << 16, "H")
    trace.alloc("C", "omega-table-low", 1 << 16, "H")
    trace.alloc("C", "stage-C-correlation-kernels",
                2 * max(CFG["le"], CFG["lx"]), "H")
    trace.alloc("C", "stage-C-group-buffer", (1 << 10) * CFG["le"], "H")
    trace.alloc("C", "stage-C-transform-row", CFG["le"], "H")
    trace.alloc("C", "batch-inversion-prefix", 1 << 16, "L")
    trace.free("C", "batch-inversion-prefix")
    for name in ("stage-C-transform-row", "stage-C-group-buffer",
                 "stage-C-correlation-kernels", "omega-table-low",
                 "omega-table-high", "stage-C-coset-scalars", "G1",
                 "R1-q-values"):
        trace.free("C", name)

    trace.alloc("D", "scale-table-1-over-2-powers", 31, "H")
    node_ranges = []
    apply_ranges = []
    for index, step in enumerate(steps, 1):
        node_start = len(trace.events) + 1
        level = step.level
        subarrays = 12 + 16 * (level - 6)
        bump_words = H.pdmem_words(level) + 2 * subarrays
        bump = f"D{index}-recursive-bump-reservation"
        trace.alloc("D", bump, bump_words, "L")
        for sub in range(subarrays):
            trace.record("D", "bump-alloc", f"D{index}-node-array-{sub}",
                         f"B{index}", 64)
        coefficient_matrix = f"D{index}-coefficient-matrix"
        trace.alloc("D", coefficient_matrix, 4 * (step.budget + 1), "H")
        for sub in reversed(range(subarrays)):
            trace.record("D", "bump-free", f"D{index}-node-array-{sub}",
                         f"B{index}", 64)
        trace.free("D", bump)
        node_ranges.append((index, node_start, len(trace.events), level,
                            coefficient_matrix))

        plan = APPLY_PLANS[(step.degree, step.budget)]
        apply_start = len(trace.events) + 1
        plan_names = []
        for suffix, words, role, side in plan.allocation_arrays()[:4]:
            name = f"D{index}-apply-{suffix}"
            trace.alloc("D", name, words, side)
            trace.reuse("D", name, "allocated", role)
            plan_names.append(name)
        trace.free("D", coefficient_matrix)
        for suffix, words, role, side in plan.allocation_arrays()[4:]:
            name = f"D{index}-apply-{suffix}"
            trace.alloc("D", name, words, side)
            trace.reuse("D", name, "allocated", role)
            plan_names.append(name)
        for name in plan_names[-2:]:
            trace.reuse("D", name, "operand spectrum", "pointwise output")
            trace.reuse("D", name, "pointwise output", "inverse output")
        for name in reversed(plan_names):
            trace.free("D", name)
        apply_ranges.append((index, apply_start, len(trace.events), plan.kind,
                             plan.points, plan.blocks))
        quotient = f"D{index}-linear-quotient"
        trace.alloc("D", quotient, 2, "H")
        trace.free("D", quotient)
    trace.free("D", "scale-table-1-over-2-powers")

    trace.alloc("E", "gcd-polynomial", 17, "L")
    trace.free("D", "R2")
    trace.free("D", "g-value-padding")
    trace.free("D", "g-coefficients")
    for name, words in (("random-shift-word", 1),
                        ("taylor-shift-scratch", 17),
                        ("character-power-residue", 17),
                        ("gcd-plus", 17), ("gcd-minus", 17),
                        ("split-selection-buffer", 17)):
        trace.alloc("E", name, words, "L")
    for name in ("split-selection-buffer", "gcd-minus", "gcd-plus",
                 "character-power-residue", "taylor-shift-scratch",
                 "random-shift-word", "gcd-polynomial"):
        trace.free("E", name)
    for name, words in (("root", 1), ("tonelli-power-table", 33),
                        ("tonelli-state", 8), ("back-map-coordinates", 6)):
        trace.alloc("F", name, words, "L")
    for name in ("tonelli-state", "tonelli-power-table", "root"):
        trace.free("F", name)
    for name, words in (("reference-state-a", 3),
                        ("reference-state-b", 3),
                        ("canonical-messages", 4), ("digest-pair", 2),
                        ("output-record", 4)):
        trace.alloc("G", name, words, "L")
    trace.free("F", "back-map-coordinates")
    for name in ("reference-state-a", "reference-state-b",
                 "canonical-messages", "digest-pair", "output-record"):
        trace.free("G", name)

    assert not trace.live
    assert trace.extents == {"L": 0, "H": 0}
    assert all(not any(slots) for slots in trace.slots.values())
    slab_rows = tuple(
        (f"slab-class-{size.bit_length()-1}", len(trace.slots[size]),
         size * len(trace.slots[size]), trace.slab_peak_live[size])
        for size in sorted(trace.slots)
    )
    slab_area = sum(row[2] for row in slab_rows)
    arena = trace.pool_peak + slab_area + 128
    allocator_routine_actions = max(
        int(row["charge"]) for row in trace.allocator_events
    )
    base_image, base_code = H.emitted_image(ROUND, allocator_routine_actions)
    union_offset = ((base_code + 63) // 64) * 64
    union_image = {
        "name": "adaptive-apply-omega-and-pass-planner",
        "kind": "routine", "offset": union_offset, "size": 32_768,
        "end": union_offset + 32_768,
        "formula": "2048 instructions * conservative 16-byte maximum",
    }
    image_manifest = tuple(base_image) + (union_image,)
    code = ((union_image["end"] + 63) // 64) * 64
    register_file = 12_384
    offline = 576
    frame_words = {name: sum(fields.values())
                   for name, fields in H.FRAME_FIELDS.items()}
    stack_chains = (
        ("stage-B", (("runtime", 1), ("line_sampler", 1),
                     ("transform", 1), ("allocator", 1))),
        ("stage-C", (("runtime", 1), ("stage_c_driver", 1),
                     ("planner", 1), ("transform", 7), ("allocator", 1))),
        ("stage-D", (("runtime", 1), ("hgcd_driver", 1),
                     ("hgcd_recursive", 26), ("planner", 1),
                     ("transform", 7), ("allocator", 1))),
        ("stage-E", (("runtime", 1), ("isolation", 1), ("allocator", 1))),
        ("stage-FG", (("runtime", 1), ("encoding_verify", 1),
                      ("allocator", 1))),
        ("offline", (("offline_generator", 1),)),
    )
    stack_chain_rows = []
    for name, frames in stack_chains:
        words = sum(frame_words[frame] * count for frame, count in frames)
        stack_chain_rows.append((name, frames, words, words * 32))
    stack_live = max(row[3] for row in stack_chain_rows)
    stack = ((stack_live + 16_383) // 16_384) * 16_384
    total = arena + code + register_file + offline + stack
    allocator_by_stage: dict[str, int] = {}
    allocator_by_owner: dict[str, int] = {}
    for row in trace.allocator_events:
        stage = str(row["stage"])
        allocator_by_stage[stage] = allocator_by_stage.get(stage, 0) + int(row["charge"])
        name = str(row["name"])
        if stage != "D":
            owner = stage
        elif "recursive-bump" in name:
            owner = "D.node"
        elif "-apply-" in name or "coefficient-matrix" in name:
            owner = "D.apply"
        elif "linear-quotient" in name or "scale-table" in name:
            owner = "D.driver"
        else:
            owner = "D.tail"
        allocator_by_owner[owner] = allocator_by_owner.get(owner, 0) + int(row["charge"])

    node_memory_rows = tuple(
        (level, (12 * (1 << 6) if level == 6 else 16 * (1 << (level - 1))),
         H.pdmem_words(level))
        for level in range(6, 32)
    )
    node_bump_rows = tuple(
        (level, 12 + 16 * (level - 6), H.pdmem_words(level),
         request_bytes(H.pdmem_words(level) + 2 * (12 + 16 * (level - 6))))
        for level in range(6, 32)
    )

    def witness(stage: str) -> dict[str, object]:
        replay: dict[str, int] = {}
        best = None
        objects = ()
        for event in trace.events:
            _number, current_stage, action, name, _region, amount, live = event[:7]
            if action == "alloc":
                replay[name] = amount
            elif action == "free":
                replay.pop(name)
            if current_stage == stage and (best is None or live > best[1]):
                best = (event[0], live)
                objects = tuple(sorted(replay.items()))
        assert best is not None and sum(value for _name, value in objects) == best[1]
        return {"event": best[0], "live_bytes": best[1], "objects": objects}

    return total, {
        "pool_peak": trace.pool_peak, "slab_area": slab_area,
        "arena": arena, "code": code, "register_file": register_file,
        "offline_workspace": offline, "stack": stack,
        "stage_b": trace.stage_peaks["B"],
        "stage_c": trace.stage_peaks["C"],
        "stage_d": trace.stage_peaks["D"],
        "stage_e": trace.stage_peaks["E"],
        "stage_f": trace.stage_peaks["F"],
        "stage_g": trace.stage_peaks["G"],
        "events": tuple(trace.events), "role_events": tuple(trace.roles),
        "allocator_events": tuple(trace.allocator_events),
        "allocator_operations_by_stage": allocator_by_stage,
        "allocator_operations_by_owner": allocator_by_owner,
        "slab_events": slab_rows, "product_event_ranges": tuple(product_ranges),
        "node_event_ranges": tuple(node_ranges),
        "apply_event_ranges": tuple(apply_ranges),
        "peak_witnesses": {"C": witness("C"), "D": witness("D")},
        "pool_gap": 128, "image_manifest": image_manifest,
        "allocator_routine_actions": allocator_routine_actions,
        "max_pool_alloc_walk": max(
            int(row["examined"]) for row in trace.allocator_events
            if row["action"] == "pool-alloc"
        ),
        "max_pool_free_find_walk": max(
            int(row["examined"]) for row in trace.allocator_events
            if row["action"] == "pool-free"
        ),
        "frame_fields": H.FRAME_FIELDS, "frame_words": frame_words,
        "stack_chain_rows": tuple(stack_chain_rows),
        "stack_live": stack_live,
        "node_memory_rows": node_memory_rows,
        "node_bump_rows": node_bump_rows,
        "offline_workspace_rows": {
            "sixteen_32_byte_field_words": 512,
            "one_64_byte_digit_buffer": 64,
        },
    }


def estimate() -> dict[str, object]:
    global PLANNER_ROWS
    old_row = U.row_transform
    old_transform = U.transform
    old_col = H.col_transform
    U.row_transform = optimized_row_transform
    U.transform = optimized_transform
    H.col_transform = optimized_col_transform
    try:
        b = H.stage_b(ROUND, CFG)
        c, crows = stage_c()
        d, steps, drows = stage_d()
        other = H.remaining_components(ROUND, CFG, steps)
        _old_planner, planner_rows = H.planner_components(CFG, steps)
        retained_planner_rows = tuple(
            row for row in planner_rows if row[0] != "apply"
        )
        adaptive_planner_rows = tuple(
            ("adaptive-apply", (degree, budget,
                                APPLY_PLANS[(degree, budget)].points,
                                APPLY_PLANS[(degree, budget)].blocks), charge)
            for (degree, budget), charge in sorted(APPLY_PLANNER_CHARGES.items())
        )
        PLANNER_ROWS = retained_planner_rows + adaptive_planner_rows
        other["plan_misses"] = sum(row[2] for row in PLANNER_ROWS)
        memory_bytes, memory_rows = memory(steps)
        allocator = memory_rows["allocator_operations_by_stage"]
        b += allocator.get("B", 0)
        crows["allocator_trace"] = allocator.get("C", 0)
        c += crows["allocator_trace"]
        drows["allocator_trace"] = allocator.get("D", 0)
        d += drows["allocator_trace"]
        for stage in ("E", "F", "G"):
            other[stage] += allocator.get(stage, 0)
    finally:
        U.row_transform = old_row
        U.transform = old_transform
        H.col_transform = old_col

    nmax = b + c + d + sum(other.values())
    raw_time = ((Decimal(nmax).ln() - Decimal(426).ln())
                / Decimal(2).ln())
    raw_memory = Decimal(memory_bytes).ln() / Decimal(2).ln()
    time = ceil5(raw_time)
    memory_log = ceil5(raw_memory)
    score = time + memory_log - 20
    d_split = {
        "pass": sum(step.node for step in steps),
        "apply": sum(step.apply.total for step in steps),
        "driver": sum(step.driver for step in steps),
        "allocator": memory_rows["allocator_operations_by_stage"].get("D", 0),
    }
    d_split["tail"] = d - sum(d_split.values())
    assert sum(d_split.values()) == d
    return {
        "B": b, "C": c, "D": d, "N": nmax,
        "time": time, "memory_bytes": memory_bytes,
        "memory": memory_log, "score": score,
        "fixed_applies": sum(plan.kind == "fixed" for plan in APPLY_PLANS.values()),
        "direct_applies": sum(plan.kind == "direct" for plan in APPLY_PLANS.values()),
        "row_splits": {str(level): optimized_widths(level, False)
                       for level in range(1, 33)},
        "memory_rows": memory_rows,
        "stage_c_components": crows,
        "stage_d_components": drows,
        "rest": sum(other.values()), "crows": crows, "drows": drows,
        "mrows": memory_rows, "d_split": d_split,
        "steps": steps,
        "other": other,
    }




ROUNDS = ROUND
CONFIG = CFG
RESULT = estimate()
DEGREE = 5 ** (ROUNDS + 6)
ODD_DEGREE = (DEGREE - 1) // 2
COMPRESSION = 216 + 21 * ROUNDS
STAGE_B = RESULT["B"]
STAGE_C = RESULT["C"]
STAGE_D = RESULT["D"]
STAGE_C_COMPONENTS = RESULT["stage_c_components"]
STAGE_D_COMPONENTS = RESULT["stage_d_components"]
OUTER_STEPS = RESULT["steps"]
OTHER_ROWS = RESULT["other"]
LEDGER = dict(OTHER_ROWS)
LEDGER.update({"B": STAGE_B, "C": STAGE_C, "D": STAGE_D})
N_MAX = RESULT["N"]
MEMORY_BYTES = RESULT["memory_bytes"]
MEMORY_COMPONENTS = RESULT["memory_rows"]
ALLOCATOR_EVENTS = MEMORY_COMPONENTS["events"]
TIME_CLAIM = RESULT["time"]
MEMORY_CLAIM = RESULT["memory"]
SCORE = RESULT["score"]
RAW_TIME = (Decimal(N_MAX).ln() - Decimal(COMPRESSION).ln()) / Decimal(2).ln()
RAW_MEMORY = Decimal(MEMORY_BYTES).ln() / Decimal(2).ln()
PRODUCT_PLANS = H.PRODUCT_PLANS
direct_geometric = H.direct_geometric
fft_geometric = H.fft_geometric
powering_dimensions = H.powering_dimensions
KERNEL_IO_SWEEP = H.KERNEL_IO_SWEEP
REST_ROW_COMPONENTS = H.REST_ROW_COMPONENTS
STAGE_E_ONE_ROUND_ROWS = H.STAGE_E_ONE_ROUND_ROWS
STAGE_F_FIELD_ROWS = H.STAGE_F_FIELD_ROWS
REMAINING_ACTION_FAMILIES = H.REMAINING_ACTION_FAMILIES
G_CORRELATION_ACTIONS = H.G_CORRELATION_ACTIONS
Q_CORRELATION_ACTIONS = H.Q_CORRELATION_ACTIONS
INTERPOLATION_LENGTH_ACTIONS = H.INTERPOLATION_LENGTH_ACTIONS
INTERPOLATION_COSET_ACTIONS = H.INTERPOLATION_COSET_ACTIONS
ALLOCATION_ZERO_ACTIONS = H.ALLOCATION_ZERO_ACTIONS
STAGE_C_MISC_ACTIONS = H.STAGE_C_MISC_ACTIONS
OUTER_DIVISION_COEFFICIENT_ACTIONS = H.OUTER_DIVISION_COEFFICIENT_ACTIONS
OUTER_QUOTIENT_TEST_ACTIONS = H.OUTER_QUOTIENT_TEST_ACTIONS
OUTER_DRIVER_FIXED_ACTIONS = H.OUTER_DRIVER_FIXED_ACTIONS
PLAN_CHARGE = OTHER_ROWS["plan_misses"]
D_SPLIT_ROWS = RESULT["d_split"]


def validate() -> None:
    assert DEGREE == 5 ** 16
    assert ODD_DEGREE == (DEGREE - 1) // 2
    assert CONFIG["h"] * CONFIG["cosets"] >= ODD_DEGREE + 1
    assert len(OUTER_STEPS) == 72
    assert OUTER_STEPS[0].degree == ODD_DEGREE
    for current, following in zip(OUTER_STEPS, OUTER_STEPS[1:]):
        assert following.degree == current.degree - current.budget - 1
    assert sum(STAGE_C_COMPONENTS.values()) == STAGE_C
    assert sum(STAGE_D_COMPONENTS.values()) == STAGE_D
    assert sum(LEDGER.values()) == N_MAX
    assert sum(D_SPLIT_ROWS.values()) == STAGE_D
    assert ALLOCATOR_EVENTS[-1][6] == 0
    assert max(event[7] + event[8] for event in ALLOCATOR_EVENTS) == MEMORY_COMPONENTS["pool_peak"]
    assert MEMORY_BYTES == (MEMORY_COMPONENTS["arena"] + MEMORY_COMPONENTS["code"]
                            + MEMORY_COMPONENTS["register_file"]
                            + MEMORY_COMPONENTS["offline_workspace"]
                            + MEMORY_COMPONENTS["stack"])
    assert TIME_CLAIM >= RAW_TIME and MEMORY_CLAIM >= RAW_MEMORY
    assert len(APPLY_PLANS) == len(OUTER_STEPS)
    assert all(sum(plan.operation_rows().values()) == plan.total
               for plan in APPLY_PLANS.values())


def main() -> None:
    validate()
    print("stage_c_components", STAGE_C_COMPONENTS)
    print("stage_d_components", STAGE_D_COMPONENTS)
    print("pass_splits", {level: optimized_widths(level, False)
                          for level in range(1, 33)})
    print("apply_plans", {key: (plan.kind, plan.points, plan.blocks, plan.total)
                          for key, plan in APPLY_PLANS.items()})
    print("node_fixed_events", U.NODE_FIXED_EVENTS, sum(U.NODE_FIXED_EVENTS.values()))
    print("ledger", LEDGER)
    print("n_max", N_MAX)
    print("allocator_events", len(ALLOCATOR_EVENTS))
    print("memory_components", {key: value for key, value in MEMORY_COMPONENTS.items()
          if key not in ("events", "role_events", "allocator_events")})
    print("memory_bytes", MEMORY_BYTES)
    print("raw_time", RAW_TIME, "time_claim", TIME_CLAIM)
    print("raw_memory", RAW_MEMORY, "memory_claim", MEMORY_CLAIM)
    print("score", SCORE)


if __name__ == "__main__":
    main()
```

## Appendix X.3: shared value-domain formulas

```python
from __future__ import annotations
import math
import sys
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, getcontext
from pathlib import Path
import ledger_core as U
getcontext().prec = 80
CONFIGS = {9: dict(kappa=3, h=1 << 30, cosets=15, vshift=1 << 31, ell=4183523331, le=48, lq=24, lx=32, hgcd_cap=30, lmax=3 * (1 << 31), block=1 << 30), 10: dict(kappa=12, h=1 << 32, cosets=18, vshift=1 << 33, ell=9605400609, le=64, lq=24, lx=48, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 11: dict(kappa=60, h=1 << 32, cosets=89, vshift=1 << 35, ell=35142101151, le=384, lq=96, lx=192, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 12: dict(kappa=297, h=1 << 31, cosets=889, vshift=1 << 37, ell=139203283733, le=3072, lq=768, lx=3072, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 13: dict(kappa=1481, h=3 * (1 << 32), cosets=741, vshift=1 << 40, ell=1110480762723, le=3072, lq=1024, lx=1536, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 14: dict(kappa=7402, h=3 * (1 << 32), cosets=3701, vshift=1 << 43, ell=8799399089385, le=12288, lq=6144, lx=8192, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 15: dict(kappa=37008, h=1 << 32, cosets=55512, vshift=1 << 45, ell=35188017522823, le=196608, lq=65536, lx=131072, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 16: dict(kappa=185038, h=3 * (1 << 32), cosets=92519, vshift=1 << 47, ell=140742830623389, le=393216, lq=131072, lx=196608, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 17: dict(kappa=925186, h=1 << 32, cosets=1387779, vshift=1 << 50, ell=1125900848379147, le=4194304, lq=2097152, lx=3145728, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 18: dict(kappa=4625930, h=1 << 32, cosets=6938894, vshift=1 << 52, ell=4503600040085809, le=25165824, lq=8388608, lx=16777216, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 19: dict(kappa=23129647, h=3 * (1 << 32), cosets=11564824, vshift=1 << 54, ell=18014409162993135, le=50331648, lq=16777216, lx=25165824, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 20: dict(kappa=115648232, h=1 << 32, cosets=173472348, vshift=1 << 57, ell=144115189803804069, le=536870912, lq=268435456, lx=402653184, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 21: dict(kappa=578241159, h=1 << 32, cosets=867361738, vshift=1 << 59, ell=576460752353229875, le=3221225472, lq=1073741824, lx=2147483648, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31), 22: dict(kappa=2891205794, h=3 * (1 << 32), cosets=1445602897, vshift=1 << 61, ell=2305843013757693177, le=6442450944, lq=2147483648, lx=3221225472, hgcd_cap=31, lmax=3 * (1 << 32), block=1 << 31)}
G_CORRELATION_ACTIONS = {'source_row_base_and_address': 2, 'destination_row_base_and_address': 2, 'chirp_pointer_and_address': 2, 'kernel_pointer_and_address': 2, 'source_load_and_address': 2, 'destination_store_and_address': 2, 'chirp_load_and_multiply': 2, 'loop_index_and_branch': 2}
Q_CORRELATION_ACTIONS = {'six_row_base_address_pairs': 12, 'four_chirp_kernel_pointer_pairs': 8, 'six_source_load_address_pairs': 12, 'six_destination_store_address_pairs': 12, 'four_field_multiply_accumulates': 8, 'four_index_bound_updates': 4, 'call_return_and_tail_tests': 4}
INTERPOLATION_LENGTH_ACTIONS = {'eight_source_load_address_pairs': 16, 'eight_destination_store_address_pairs': 16, 'six_chirp_field_operations': 6, 'four_pointer_updates': 4, 'four_loop_controls': 4, 'two_calls_and_two_returns': 4}
INTERPOLATION_COSET_ACTIONS = dict(INTERPOLATION_LENGTH_ACTIONS)
ALLOCATION_ZERO_ACTIONS = {'sixteen_zero_store_address_pairs': 32, 'sixteen_source_load_address_pairs': 32, 'sixteen_destination_store_address_pairs': 32, 'eight_allocator_header_updates': 8, 'eight_pointer_updates': 8, 'eight_bound_tests_and_branches': 8, 'four_calls_and_four_returns': 8}
STAGE_C_MISC_ACTIONS = {f'ten_bookkeeping_{name}': 10 * value for name, value in U.STAGE_BOOKKEEPING_ACTIONS.items()}
STAGE_C_O1_FUSED_LOOPS = (U.ActionLoop('input_lanes', 4, ('input_load',)), U.ActionLoop('forward_butterflies', 4, ('field_add', 'field_subtract', 'twiddle_multiply')), U.ActionLoop('g1_lanes', 4, ('g1_load', 'field_square', 'field_multiply')), U.ActionLoop('inverse_butterflies', 4, ('field_add', 'field_subtract', 'twiddle_multiply')), U.ActionLoop('output_lanes', 4, ('output_store',)), U.ActionLoop('position_control', 1, ('position_update', 'position_branch')))
STAGE_C_O2_FUSED_LOOPS = (U.ActionLoop('input_lanes', 4, ('input_load',)), U.ActionLoop('forward_butterflies', 4, ('field_add', 'field_subtract', 'twiddle_multiply')), U.ActionLoop('scale_word', 1, ('scale_load',)), U.ActionLoop('residue_lanes', 4, ('r2_load', 'g2_load', 'field_square', 'first_field_multiply', 'second_field_multiply', 'field_add', 'scale_multiply')), U.ActionLoop('inverse_butterflies', 4, ('field_add', 'field_subtract', 'twiddle_multiply')), U.ActionLoop('output_lanes', 4, ('output_store',)), U.ActionLoop('position_control', 1, ('position_update', 'position_branch')))
STAGE_C_BIT_ONE_EXTRA_LOOPS = (U.ActionLoop('factor_word', 1, ('factor_load',)), U.ActionLoop('factor_lanes', 4, ('factor_multiply', 'residue_multiply')))
STAGE_C_FUSED_FIXED_LOOPS = (U.ActionLoop('kernel_call_paths', 2, ('call', 'return')), U.ActionLoop('pointer_bundles', 2, ('source_pointer_load', 'destination_pointer_load', 'source_pointer_store', 'destination_pointer_store')), U.ActionLoop('bound_paths', 2, ('bound_load', 'comparison', 'branch', 'bound_store')))
PRODUCT_POINT_ACTIONS = U.unit_action_rows('left_address', 'left_load', 'right_address', 'right_load', 'output_address', 'output_load', 'field_multiply', 'field_add', 'output_store', 'pointer_update')

def loop_action_multiset(loops: tuple[U.ActionLoop, ...]) -> dict[str, int]:
    result: dict[str, int] = {}
    for loop in loops:
        assert loop.total == loop.iterations * len(loop.actions)
        for action in loop.actions:
            result[action] = result.get(action, 0) + loop.iterations
    return result

def loop_total(loops: tuple[U.ActionLoop, ...]) -> int:
    return sum((loop.total for loop in loops))

def stage_c_kernel_io_sweep() -> tuple[tuple[str, str, int, int, int], ...]:
    rows = []
    for name, loops, expected, loads, stores in (('O1-four-lane-boundary', STAGE_C_O1_FUSED_LOOPS, 46, 8, 4), ('O2-four-lane-boundary', STAGE_C_O2_FUSED_LOOPS, 63, 13, 4)):
        actions = loop_action_multiset(loops)
        assert loop_total(loops) == expected
        assert U.action_kind_count(actions, 'load') == loads
        assert U.action_kind_count(actions, 'store') == stores
        rows.append(('C', name, expected, loads, stores))
    assert sum(PRODUCT_POINT_ACTIONS.values()) == 10
    assert U.action_kind_count(PRODUCT_POINT_ACTIONS, 'load') == 3
    assert U.action_kind_count(PRODUCT_POINT_ACTIONS, 'store') == 1
    rows.append(('C', 'product-point', 10, 3, 1))
    assert loop_total(STAGE_C_BIT_ONE_EXTRA_LOOPS) == 9
    assert loop_total(STAGE_C_FUSED_FIXED_LOOPS) == 20
    return tuple(rows)
KERNEL_IO_SWEEP = U.CORE_KERNEL_IO_SWEEP + stage_c_kernel_io_sweep()

def col_transform(points: int, positions: int, inverse: bool=False) -> int:
    radix3 = points % 3 == 0
    row = points // 3 if radix3 else points
    assert row & row - 1 == 0
    layers = row.bit_length() - 1
    groups = (positions + 1023) // 1024
    total = 0
    if radix3:
        total += 25 * positions + 23 * groups
    for level, width in U.pass_schedule(layers):
        constants = {1: 5, 2: 6, 3: 10, 4: 18, 5: 34, 6: 139, 7: 269}
        slopes = {1: 11, 2: 20, 3: 52, 4: 128, 5: 304, 6: 704, 7: 1600}
        rows = 1 << width
        total += slopes[width] * positions
        total += groups * (constants[width] + 2 * rows + 11)
        total += U.loop8(positions)
    if inverse:
        total += positions
    return total

def direct_geometric(k: int, h: int) -> int:
    groups, rem = divmod(h, 1024)
    assert rem == 0
    per_position = 8 * k + k * k + k * (k - 1) + 8 * k + 5
    return 2 * (7 * k + 2) + groups * (20 + 3 + 2 * (2 * k - 1) + 1024 * per_position) + 2

def fft_geometric(k: int, h: int, length: int) -> int:
    return col_transform(length, h) + col_transform(length, h, True) + sum(PRODUCT_POINT_ACTIONS.values()) * length * h + 14 * k * h + U.loop8(h) + U.CALL_CLOSE

def powering_dimensions(vshift: int, degree: int) -> tuple[int, int, int]:
    assert vshift & vshift - 1 == 0 and vshift < degree
    width = vshift.bit_length() - 1
    bits = bin((U.PALLAS_P - 1) // 2)[2:]
    assert set(bits[1:1 + width]) <= {'0'}
    active = bits[1 + width:]
    return (len(active), active.count('1'), width)

@dataclass(frozen=True)
class Product:
    points: int
    total: int
    blocks: int

@dataclass(frozen=True)
class PolynomialProductPlan:
    mode: str
    left: int
    right: int
    output: int
    points: int
    left_blocks: int
    right_blocks: int
    output_slots: int
    rows: tuple[tuple[str, int], ...]

    @property
    def total(self) -> int:
        return sum((value for _name, value in self.rows))

    def operation_rows(self) -> dict[str, int]:
        return dict(self.rows)

    def allocation_schedule(self) -> tuple[tuple[str, str, int, str], ...]:
        events: list[tuple[str, str, int, str]] = []
        if self.mode == 'direct':
            events.extend((('alloc', 'left-spectrum-output', self.points, 'left input then pointwise/output'), ('alloc', 'right-spectrum', self.points, 'right input'), ('free', 'right-spectrum', self.points, 'right input'), ('free', 'left-spectrum-output', self.points, 'inverse output')))
            return tuple(events)
        for index in range(self.left_blocks):
            events.append(('alloc', f'left-block-{index}-spectrum', self.points, 'persistent operand form'))
        for index in range(self.right_blocks):
            events.append(('alloc', f'right-block-{index}-spectrum', self.points, 'persistent operand form'))
        for slot in range(self.output_slots):
            events.append(('alloc', f'output-slot-{slot}-accumulator', self.points, 'pointwise accumulator and inverse output'))
            events.append(('free', f'output-slot-{slot}-accumulator', self.points, 'placed output'))
        for index in reversed(range(self.right_blocks)):
            events.append(('free', f'right-block-{index}-spectrum', self.points, 'persistent operand form'))
        for index in reversed(range(self.left_blocks)):
            events.append(('free', f'left-block-{index}-spectrum', self.points, 'persistent operand form'))
        return tuple(events)
PRODUCT_PLANS: dict[tuple[int, int, int], PolynomialProductPlan] = {}

def product(left: int, right: int, output: int) -> Product:
    required = left + right - 1
    choices: list[tuple[Product, PolynomialProductPlan]] = []
    for points in U.admissible_points(required):
        transforms = 2 * U.transform(points) + U.transform(points, True)
        io = 7 * (left + right) + 5 * (2 * points - left - right)
        pointwise = sum(PRODUCT_POINT_ACTIONS.values()) * points
        out = 4 * output + U.loop8(output)
        fixed = U.PLAN_DISPATCH + 6
        plan = PolynomialProductPlan('direct', left, right, output, points, 1, 1, 1, (('three_transforms', transforms), ('copy_and_zero', io), ('pointwise', pointwise), ('output_placement', out), ('two_allocations_dispatch_and_call', fixed)))
        choices.append((Product(points, plan.total, 2), plan))
    if choices:
        selected, plan = min(choices, key=lambda row: (row[0].total, row[0].points))
        PRODUCT_PLANS[left, right, output] = plan
        return selected
    block = 3 * (1 << 31)
    points = 2 * block
    nl = (left + block - 1) // block
    nr = (right + block - 1) // block
    no = min(nl + nr - 1, (output + block - 1) // block)
    transforms = (nl + nr) * U.transform(points) + no * U.transform(points, True)
    io = 7 * (left + right) + 5 * ((nl + nr) * block - left - right) + no * (7 * min(block, output) + U.loop8(min(block, output)))
    pointwise = nl * nr * (sum(PRODUCT_POINT_ACTIONS.values()) * points + U.loop8(points))
    fixed = (nl + nr + no) * U.PRODUCT_FIXED + U.CALL_CLOSE
    plan = PolynomialProductPlan('block-slot', left, right, output, points, nl, nr, no, (('operand_and_output_transforms', transforms), ('copy_zero_and_placement', io), ('all_block_pair_pointwise', pointwise), ('allocation_dispatch_and_close', fixed)))
    PRODUCT_PLANS[left, right, output] = plan
    return Product(points, plan.total, nl + nr + no)

def reciprocal(precision: int) -> tuple[int, list[tuple[int, int]]]:
    current = 1
    rows = []
    while True:
        target = min(2 * current, precision)
        charge = product(target, current, target).total + product(current, target, target).total + 12 * target + U.loop8(target) + U.CALL_CLOSE
        rows.append((target, charge))
        if target == precision:
            return (sum((row[1] for row in rows)), rows)
        current = target

def stage_b(rounds: int, cfg: dict) -> int:
    block = 3 * (1 << 31)
    kappa = cfg['kappa']
    points = kappa * block
    evaluations = 2 * points * (216 + 21 * rounds)
    loop = points * (13 + 11 * 31)
    inverse = kappa * U.transform(block, True)
    if kappa == 3:
        solve = block * (2 * kappa + kappa * kappa + kappa * (kappa - 1) + 4 * kappa + 3) + 2 * kappa * 512 * 5 + 97
    else:
        size = min((p for p in U.admissible_points(2 * kappa - 1)))
        one_corr = 2 * U.transform(size) + sum(PRODUCT_POINT_ACTIONS.values()) * size + 14 * kappa
        solve = block * (2 * one_corr) + 4 * U.transform(size) + sum(PRODUCT_POINT_ACTIONS.values()) * size
    table = block // 2 * 8 + U.CALL_CLOSE
    normalise = 5 * ((5 ** (rounds + 6) + 1) // 2) + U.loop8((5 ** (rounds + 6) + 1) // 2)
    return evaluations + loop + inverse + solve + table + normalise + 31

def stage_c(rounds: int, cfg: dict) -> tuple[int, dict[str, int]]:
    PRODUCT_PLANS.clear()
    m = (5 ** (rounds + 6) - 1) // 2
    h, k, n1 = (cfg['h'], cfg['cosets'], cfg['h'] * cfg['cosets'])
    ell, le, lq, lx = (cfg['ell'], cfg['le'], cfg['lq'], cfg['lx'])
    steps, ones, _width = powering_dimensions(cfg['vshift'], m)
    inner = U.transform(h)
    inner_inv = U.transform(h, True)
    if k <= 18:
        geometric = direct_geometric(k, h)
    else:
        geometric = fft_geometric(k, h, lx)
    extension = k * (inner + inner_inv) + geometric
    tables = 10 * h + 30 * k * (512 * 5 + 8) + 20 * (le + lq + lx) + sum(U.STAGE_BOOKKEEPING_ACTIONS.values())
    newton, _ = reciprocal(ell)
    qprod = product(ell, ell, 2 * ell - 1).total + 9 * ell + U.loop8(ell)
    g_geo = col_transform(le, h) + col_transform(le, h, True) + sum(PRODUCT_POINT_ACTIONS.values()) * le * h + 24 * k * h + U.loop8(h) + U.CALL_CLOSE
    g_inner = 2 * k * inner
    q_geo = col_transform(lq, h) + col_transform(lq, h, True) + sum(PRODUCT_POINT_ACTIONS.values()) * lq * h + 24 * k * h + U.loop8(h) + U.CALL_CLOSE
    step3 = q_geo + k * inner + 8 * n1 + U.loop8(n1)
    chunk = 1 << 16
    chunks = (n1 + chunk - 1) // chunk
    batch = 14 * n1 + U.loop8(n1) + chunks * (512 * 5 + 20)
    if rounds == 9:
        bit0 = 2 * extension + 20 * n1 + 2 * U.loop8(n1) + 20
        bit1 = bit0 + 4 * n1
    else:
        layers = h.bit_length() - 1
        pass2 = k * U.shared_running_pass(layers, layers - 2, 2)
        pos = n1 // 4
        fused0 = loop_total(STAGE_C_O1_FUSED_LOOPS) * pos + U.loop8(pos) + loop_total(STAGE_C_O2_FUSED_LOOPS) * pos + U.loop8(pos) + loop_total(STAGE_C_FUSED_FIXED_LOOPS)
        bit0 = 2 * extension - 4 * pass2 + fused0
        bit1 = bit0 + loop_total(STAGE_C_BIT_ONE_EXTRA_LOOPS) * pos + U.loop8(pos)
    exit_step = extension + 19 * n1 + U.loop8(n1)
    interp_geo = 4 * col_transform(lx, h) + 20 * lx * h + 28 * k * h + 2 * U.loop8(h) + 84
    interpolate = 2 * (k * inner_inv + interp_geo) + 31
    g_correlation_control = sum(G_CORRELATION_ACTIONS.values()) * k * h
    q_correlation_control = sum(Q_CORRELATION_ACTIONS.values()) * k * h
    interpolation_control = 2 * h * (sum(INTERPOLATION_LENGTH_ACTIONS.values()) * lx + sum(INTERPOLATION_COSET_ACTIONS.values()) * k)
    allocation_zero_control = sum(ALLOCATION_ZERO_ACTIONS.values()) * n1 + U.loop8(n1)
    other = 5 * (n1 - m - 1) + U.loop8(n1 - m - 1) + 8 * n1 + U.loop8(n1) + sum(STAGE_C_MISC_ACTIONS.values())
    rows = {'tables_and_plans': tables, 'newton_reciprocal': newton, 'quotient_product': qprod, 'g_geometric_evaluation': g_geo, 'g_correlation_control': g_correlation_control, 'g_inner_transforms': g_inner, 'start_residue': step3, 'q_correlation_control': q_correlation_control, 'first_extension': extension, 'batch_inversion': batch, 'powering_loop': (steps - ones) * bit0 + ones * bit1, 'exit_montgomery': exit_step, 'two_interpolations': interpolate, 'interpolation_control': interpolation_control, 'allocation_and_zero_control': allocation_zero_control, 'zero_fills_allocations_and_control': other, 'entry_exit': sum(U.STAGE_BOOKKEEPING_ACTIONS.values())}
    return (sum(rows.values()), rows)
OUTER_DIVISION_COEFFICIENT_ACTIONS = {'two_loads_with_addresses': 4, 'two_field_multiplications': 2, 'two_field_subtractions': 2, 'one_store_with_address': 2, 'loop_counter_test_and_branch': 3, 'if_k_test_and_branch': 2}
OUTER_QUOTIENT_TEST_ACTIONS = {'quotient_degree_comparison': 1, 'abort_branch': 1}
OUTER_DRIVER_FIXED_ACTIONS = {'addressed_pair_and_degree_loads': 16, 'addressed_pair_stores': 8, 'pair_pointer_updates': 12, 'comparisons': 4, 'branches': 4, 'calls_and_returns': 6, 'two_one_item_loop_controls': 2 * U.loop8(1)}

def pdmem_words(level: int) -> int:
    assert level >= 6
    if level == 6:
        return 12 * (1 << 6)
    n = 1 << level - 1
    return pdmem_words(level - 1) + 16 * n
FRAME_FIELDS = {'runtime': {'return_pc': 1, 'saved_pool_ends': 2, 'target_pointer': 1, 'config_pointer': 1, 'stage_counter': 1, 'status': 1, 'output_pointer': 1}, 'line_sampler': {'centre_words': 4, 'line_coordinates': 6, 'sampler_counters': 4, 'pointers': 6}, 'stage_c_driver': {'four_value_array_pointers': 4, 'coset_and_length_fields': 8, 'scalar_state': 8, 'allocator_marks': 4, 'loop_counters': 8}, 'transform': {'value_pointers': 8, 'twiddle_pointers': 4, 'offset_pointers': 8, 'layer_and_loop_fields': 8, 'saved_register_words': 4}, 'planner': {'three_lengths': 3, 'candidate_fields': 5, 'selected_plan_fields': 5, 'pointers': 3}, 'hgcd_driver': {'pair_pointers': 4, 'degree_fields': 4, 'budget_fields': 3, 'arena_marks': 2, 'return_fields': 3}, 'hgcd_recursive': {'four_matrix_pointers': 4, 'pair_pointers': 4, 'degree_budget_split': 5, 'window_fields': 3, 'arena_marks': 2, 'return_fields': 6}, 'allocator': {'request_fields': 4, 'list_pointers': 4, 'split_fields': 4, 'statistics': 4}, 'isolation': {'six_polynomial_pointers': 6, 'degree_fields': 4, 'shift_state': 4, 'loop_fields': 4}, 'encoding_verify': {'two_messages': 4, 'two_states': 6, 'two_digests': 2, 'encoding_fields': 4}, 'offline_generator': {'sixteen_field_words': 16, 'digit_buffer_words': 2, 'loop_fields': 4}}

def emitted_image(rounds: int, allocator_routine_actions: int) -> tuple[tuple[dict, ...], int]:
    records: list[dict] = []
    offset = 0

    def emit(name: str, kind: str, size: int, formula: str) -> None:
        nonlocal offset
        offset = (offset + 63) // 64 * 64
        assert size >= 0
        records.append({'name': name, 'kind': kind, 'offset': offset, 'size': size, 'end': offset + size, 'formula': formula})
        offset += size
    for direction in ('forward', 'inverse'):
        for width in range(1, 8):
            standard = 4 * U.block_body(width)
            group_zero = 4 * (U.block_body(width) - ((1 << width) - 1))
            emit(f'block-{direction}-w{width}', 'routine', 4 * standard, f'4-byte instructions * 4 unrolled blocks * B({width})')
            emit(f'block-{direction}-group-zero-w{width}', 'routine', 4 * group_zero, f'4-byte instructions * 4 blocks * twiddle-one body({width})')
    column_counts = (11, 20, 52, 128, 304, 704, 1600)
    for width, count in enumerate(column_counts, 1):
        emit(f'column-w{width}', 'routine', 4 * 8 * count, f'4-byte instructions * 8 positions * {count}')
    emit('target-compression', 'routine', 4 * (216 + 21 * rounds), f'4-byte instructions * C({rounds})')
    for name, count in (('montgomery-mul', 330), ('field-invert', 2310), ('field-encode', 512)):
        emit(name, 'routine', 4 * count, f'4-byte instructions * {count}')
    emit('allocator', 'routine', 4 * allocator_routine_actions, '4-byte instructions * maximum traced top-level allocator call')
    driver_count = sum(U.NODE_FIXED_EVENTS.values()) + 8 * U.PLAN_DISPATCH + U.CALL_CLOSE
    emit('polynomial-driver', 'routine', 4 * driver_count, '4-byte instructions * node, plan, and close actions')
    emit('fixed-slot-two-output-pointwise', 'routine', 4 * (8 * 12 + U.loop8(8)), '4-byte instructions * eight-position two-output spectral body')
    emit('fixed-slot-overlap-add', 'routine', 4 * (8 * 7 + U.loop8(8)), '4-byte instructions * eight-position scaled overlap body')
    emit('direct-two-output-pointwise', 'routine', 4 * (8 * sum(U.DIRECT_POINT_ACTIONS.values()) + U.loop8(8)), '4-byte instructions * eight addressed direct points')
    emit('direct-output-placement', 'routine', 4 * (8 * sum(U.DIRECT_PLACEMENT_ACTIONS.values()) + U.loop8(8)), '4-byte instructions * eight direct output placements')
    emit('outer-linear-division', 'routine', 4 * (8 * 15 + 2), '4-byte instructions * eight coefficients plus quotient test')
    emit('half-gcd-base', 'routine', 4 * 512, '4-byte instructions * conservative finite base-loop image')
    emit('stage-c-driver', 'routine', 4 * sum(U.STAGE_BOOKKEEPING_ACTIONS.values()), '4-byte instructions * expanded Stage-C bookkeeping image')
    emit('sampler-and-line-setup', 'routine', 4 * 1228, '4-byte instructions * charged sampler/line entry body')
    emit('reference-verification-wrapper', 'routine', 4 * sum(REFERENCE_VERIFY_OVERHEAD_ACTIONS.values()), '4-byte instructions * expanded verification wrapper')
    emit('stage-e-driver', 'routine', 4 * sum(STAGE_E_DRIVER_ACTIONS.values()), '4-byte instructions * named isolation driver actions')
    emit('stage-f-driver', 'routine', 4 * (sum(TONELLI_CONTROL_ACTIONS.values()) // 32), '4-byte instructions * one Tonelli control body')
    emit('pass-plan-table', 'data', 2 * 33 * 32, 'two directions * 33 depths * one 32-byte plan word')
    emit('literal-table', 'data', 212 * 32, '212 field/word literals * 32 bytes')
    emit('output-buffer', 'data', 8192, '256 words * 32 bytes')
    for left, right in zip(records, records[1:]):
        assert left['end'] <= right['offset']
    return (tuple(records), (offset + 63) // 64 * 64)

def planner_components(cfg: dict, steps: tuple) -> tuple[int, tuple[tuple[str, tuple[int, ...], int], ...]]:
    keys: set[tuple[str, tuple[int, ...]]] = set()
    current = 1
    precision = cfg['ell']
    while True:
        target = min(2 * current, precision)
        keys.add(('product', (target, current, target)))
        keys.add(('product', (current, target, target)))
        if target == precision:
            break
        current = target
    keys.add(('product', (precision, precision, 2 * precision - 1)))
    keys.add(('transform', (3 * (1 << 31),)))
    for size in (cfg['h'], cfg['le'], cfg['lq'], cfg['lx']):
        keys.add(('transform', (size,)))
    for step in steps:
        keys.add(('apply', (step.degree, step.budget, step.apply.points)))
    rows = []
    for kind, values in sorted(keys):
        if kind == 'product':
            left, right, _output = values
            candidates = max(1, len(U.admissible_points(left + right - 1)))
        elif kind == 'apply':
            degree, budget, _points = values
            output = degree - budget
            candidates = 1 if degree > cfg['lmax'] else max(1, len(U.admissible_points(output)))
        else:
            candidates = 1
        charge = 18 + U.loop8(len(values)) + candidates * 27 + U.loop8(candidates)
        rows.append((kind, values, charge))
    return (sum((row[2] for row in rows)), tuple(rows))
SCHOOLBOOK_COEFFICIENT_ACTIONS = {'four_loads_with_addresses': 8, 'two_field_multiplications': 2, 'two_field_additions': 2, 'accumulator_load_and_store_with_addresses': 4, 'two_pointer_updates': 2, 'counter_test_and_branch': 3, 'coefficient_bound_test': 1}
SCHOOLBOOK_ROW_ACTIONS = {'six_loads_with_addresses': 12, 'two_stores_with_addresses': 4, 'two_pointer_updates': 2, 'test_and_branch': 2}
SCHOOLBOOK_FIXED_ACTIONS = {'argument_loads_with_addresses': 16, 'result_pointer_stores_with_addresses': 8, 'length_and_bound_word_operations': 12, 'comparisons': 8, 'branches': 8, 'call_and_return': 2, 'loop_entry_and_exit': 10}
STAGE_E_POINT_ACTIONS = {'three_loads_with_addresses': 6, 'field_multiplication': 1, 'store_with_address': 2, 'pointer_update': 1, 'counter_test_and_branch': 3, 'character_and_zero_tests': 3}
STAGE_E_DIVISION_FIXED_ACTIONS = {'coefficient_and_degree_loads': 8, 'quotient_stores_with_addresses': 4, 'field_operations': 5, 'pointer_updates': 4, 'comparisons_and_branches': 4, 'calls_and_returns': 2}
STAGE_E_ROUND_CLOSE_ACTIONS = {'split_choice_loads_with_addresses': 16, 'split_choice_stores_with_addresses': 8, 'degree_and_zero_comparisons': 8, 'branches': 8, 'pointer_updates': 8, 'calls_and_returns': 4, 'loop_updates_tests_and_exit': 12}
STAGE_E_SHIFT_ACTIONS = {'eight_loads_with_addresses': 16, 'eight_stores_with_addresses': 16}
STAGE_E_DRIVER_ACTIONS = {'random_word_and_reduction': 31, 'zero_replacement_test_and_branch': 7, 'three_polynomial_call_pairs': 6, 'degree_selection_loads_with_addresses': 12, 'degree_comparisons_and_branches': 12, 'pointer_updates': 12, 'round_counter_update_test_branch': 3, 'allocator_mark_updates': 8, 'round_entry_and_exit': 4}
FIELD_OPERATION_WITH_MEMORY_ACTIONS = {'two_operand_loads_with_addresses': 4, 'field_operation': 1, 'result_store_with_address': 2, 'call_and_loop_control': 3}
TONELLI_CONTROL_ACTIONS = U.action_loop_rows(U.ActionLoop('thirty_two_outer_rounds', 32, ('state_load', 'state_address', 'round_test', 'round_branch', 'table_pointer_update', 'counter_update', 'call', 'return')), U.ActionLoop('five_hundred_twenty_eight_scan_steps', sum(range(1, 33)), ('table_load', 'table_address', 'residue_load', 'residue_address', 'comparison', 'branch', 'index_update', 'loop_test')), U.ActionLoop('four_hundred_ninety_six_update_steps', sum(range(32)), ('state_load', 'state_address', 'table_load', 'table_address', 'state_store', 'state_store_address', 'pointer_update', 'counter_update', 'loop_test', 'loop_branch')), U.ActionLoop('two_hundred_fifty_three_exponent_steps', 253, ('bit_load', 'bit_test', 'branch', 'counter_update', 'loop_test')), U.ActionLoop('thirty_three_table_entries', 33, ('table_address', 'table_store', 'pointer_update', 'bound_test')))
REFERENCE_VERIFY_OVERHEAD_ACTIONS = U.action_loop_rows(U.ActionLoop('sixty_four_canonical_input_bytes', 64, ('source_load', 'source_address', 'range_test', 'branch', 'field_limb_load', 'field_limb_address', 'shift', 'mask', 'field_or', 'destination_store', 'destination_address', 'source_pointer_update', 'destination_pointer_update', 'counter_update', 'loop_test', 'loop_branch')), U.ActionLoop('sixty_four_message_copy_bytes', 64, ('source_load', 'source_address', 'destination_store', 'destination_address', 'source_pointer_update', 'destination_pointer_update', 'length_load', 'length_test', 'branch', 'counter_update', 'loop_test', 'loop_branch')), U.ActionLoop('three_state_words', 3, ('constant_load', 'state_address', 'state_store', 'state_pointer_update', 'capacity_load', 'capacity_store', 'word_test', 'branch', 'call_argument_store', 'call', 'return', 'result_load', 'result_address', 'result_store', 'counter_update', 'loop_test')), U.ActionLoop('ten_round_wrapper_steps', 10, ('round_constant_load', 'round_constant_address', 'state_a_pointer_load', 'state_b_pointer_load', 'state_c_pointer_load', 'state_a_address', 'state_b_address', 'state_c_address', 'round_index_load', 'round_index_test', 'branch', 'call_argument_a', 'call_argument_b', 'call_argument_c', 'call', 'return', 'first_result_load', 'second_result_load', 'third_result_load', 'first_result_store', 'second_result_store', 'third_result_store', 'state_pointer_update', 'round_update', 'loop_test', 'loop_branch', 'status_load', 'status_test', 'status_branch', 'scratch_clear', 'scratch_address', 'scratch_store', 'wrapper_counter_update', 'wrapper_bound_test')), U.ActionLoop('thirty_two_digest_bytes', 32, ('state_load', 'state_address', 'shift', 'mask', 'digest_store', 'digest_address', 'state_pointer_update', 'digest_pointer_update', 'counter_update', 'loop_test', 'loop_branch', 'range_test')), U.ActionLoop('two_final_message_checks', 2, ('message_pointer_load', 'digest_pointer_load', 'length_load', 'comparison', 'difference_accumulate', 'pointer_update', 'branch', 'status_store')))
INIT_CLOSE_ACTIONS = {'loads_with_addresses': 4, 'stores_with_addresses': 4, 'pointer_updates': 3, 'comparisons': 2, 'branches': 2, 'call_and_return': 2}
SETUP_CLOSE_ACTIONS = {'loads_with_addresses': 32, 'stores_with_addresses': 24, 'field_operations': 16, 'pointer_updates': 12, 'comparisons': 6, 'branches': 6, 'calls_and_returns': 2, 'loop_updates_and_exits': 5}
SAMPLER_CONTROL_ACTIONS = {'word_loads_with_addresses': 16, 'conditional_subtraction_field_actions': 12, 'comparisons': 12, 'branches': 12, 'pointer_updates': 12, 'counter_updates': 8, 'calls_and_returns': 4, 'stores_with_addresses': 8, 'entry_and_exit': 13}
OUTPUT_CALL_ACTIONS = {'loads_with_addresses': 20, 'stores_with_addresses': 16, 'encoding_word_operations': 16, 'pointer_updates': 10, 'comparisons': 6, 'branches': 4, 'calls_and_returns': 4, 'loop_updates_and_exits': 4}
OFFLINE_HEX_DIGIT_ACTIONS = {'input_load': 1, 'lookup_table_load': 1, 'shift': 1, 'or': 1, 'loop_control': 1}
OFFLINE_FIELD_OPERATION_COUNTS = {'constant_two': 1, 'montgomery_R_squarings': 8, 'montgomery_R_squared': 1, 'organizer_constant_conversions': 201, 'capacity_constant': 8, 'constant_five': 2, 'Tonelli_generator_power': 268}
OFFLINE_BIT_STEP_COUNTS = {'Tonelli_generator_exponent_squarings': 222}
OFFLINE_WORD_OPERATION_COUNTS = {'p_minus_one': 4, 'odd_part_shift': 12, 'q_plus_one_over_two': 16, 'p_minus_one_over_two': 12, 'p_minus_two': 4, 'inverse_fifth_exponent': 26, 'Montgomery_word_inverse': 16}
REMAINING_ACTION_FAMILIES = {'schoolbook coefficient': SCHOOLBOOK_COEFFICIENT_ACTIONS, 'schoolbook row': SCHOOLBOOK_ROW_ACTIONS, 'schoolbook fixed': SCHOOLBOOK_FIXED_ACTIONS, 'stage E point': STAGE_E_POINT_ACTIONS, 'stage E division fixed': STAGE_E_DIVISION_FIXED_ACTIONS, 'stage E round close': STAGE_E_ROUND_CLOSE_ACTIONS, 'stage E shift': STAGE_E_SHIFT_ACTIONS, 'stage E driver': STAGE_E_DRIVER_ACTIONS, 'field operation with memory': FIELD_OPERATION_WITH_MEMORY_ACTIONS, 'Tonelli control': TONELLI_CONTROL_ACTIONS, 'reference verification': REFERENCE_VERIFY_OVERHEAD_ACTIONS, 'init close': INIT_CLOSE_ACTIONS, 'setup close': SETUP_CLOSE_ACTIONS, 'sampler control': SAMPLER_CONTROL_ACTIONS, 'output call': OUTPUT_CALL_ACTIONS, 'offline hexadecimal digit': OFFLINE_HEX_DIGIT_ACTIONS, 'offline field operations': OFFLINE_FIELD_OPERATION_COUNTS, 'offline bit steps': OFFLINE_BIT_STEP_COUNTS, 'offline word operations': OFFLINE_WORD_OPERATION_COUNTS}

def exponent_operation_count(exponent: int) -> int:
    assert exponent > 0
    return exponent.bit_length() - 1 + bin(exponent).count('1') - 1
STAGE_E_ONE_ROUND_ROWS: dict[str, int] = {}
STAGE_F_FIELD_ROWS: dict[str, int] = {}

def stage_e_components() -> dict[str, int]:
    exponent = (U.PALLAS_P - 1) // 2
    exponent_steps = exponent_operation_count(exponent)
    degree = 16
    cells = (degree + 1) ** 2
    school = cells * sum(SCHOOLBOOK_COEFFICIENT_ACTIONS.values()) + (degree + 1) * sum(SCHOOLBOOK_ROW_ACTIONS.values()) + sum(SCHOOLBOOK_FIXED_ACTIONS.values())
    euclid = 2 * sum((sum(STAGE_E_POINT_ACTIONS.values()) * d + sum(STAGE_E_DIVISION_FIXED_ACTIONS.values()) for d in range(1, degree + 1)))
    one_round = {'fixed_exponent_schoolbook': exponent_steps * school, 'split_point_actions': 8 * cells, 'split_point_loop': U.linear_loop(cells), 'round_close': sum(STAGE_E_ROUND_CLOSE_ACTIONS.values()), 'two_classical_gcds': euclid, 'shift_coefficients': sum(STAGE_E_SHIFT_ACTIONS.values()) * degree, 'driver': sum(STAGE_E_DRIVER_ACTIONS.values())}
    assert sum(one_round.values()) > 0
    STAGE_E_ONE_ROUND_ROWS.clear()
    STAGE_E_ONE_ROUND_ROWS.update(one_round)
    return {'sixty_four_rounds': 64 * sum(one_round.values()), 'stage_bookkeeping': sum(U.STAGE_BOOKKEEPING_ACTIONS.values())}

def stage_f_components() -> dict[str, int]:
    p = U.PALLAS_P
    q = p - 1 >> 32
    inverse_fifth = (4 * (p - 1) + 1) // 5
    ts_field = sum((parameter + 2 for parameter in range(1, 33)))
    field_rows = {'power_by_q': exponent_operation_count(q), 'power_by_q_plus_one_over_two': exponent_operation_count((q + 1) // 2), 'Tonelli_steps': ts_field, 'six_inverse_fifth_powers': 6 * exponent_operation_count(inverse_fifth), 'two_back_map_affine_updates': 2 * (2 + 2 + 2), 'two_antipodal_point_updates': 2}
    assert sum(field_rows.values()) == 3401
    STAGE_F_FIELD_ROWS.clear()
    STAGE_F_FIELD_ROWS.update(field_rows)
    return {'stage_bookkeeping': sum(U.STAGE_BOOKKEEPING_ACTIONS.values()), 'Tonelli_control': sum(TONELLI_CONTROL_ACTIONS.values()), 'root_nonzero_comparison_and_branch': 2, 'field_operations_with_memory': sum(field_rows.values()) * sum(FIELD_OPERATION_WITH_MEMORY_ACTIONS.values())}

def offline_components() -> dict[str, int]:
    digit = sum(OFFLINE_HEX_DIGIT_ACTIONS.values())
    input_literals = 202 * (64 * digit + 4)
    field_literals = 4 * sum(OFFLINE_FIELD_OPERATION_COUNTS.values()) + 3 * sum(OFFLINE_BIT_STEP_COUNTS.values())
    word_literals = 3 * sum(OFFLINE_WORD_OPERATION_COUNTS.values())
    output_literals = 211 * (64 * digit + 4) + (16 * digit + 1)
    rows = {'input_literal_loops': input_literals, 'field_literal_operations_and_bit_loops': field_literals, 'word_literal_operations': word_literals, 'output_literal_loops': output_literals}
    assert sum(rows.values()) == 136785
    return rows
REST_ROW_COMPONENTS: dict[str, dict[str, int]] = {}

def remaining_components(rounds: int, cfg: dict, steps: tuple) -> dict[str, int]:
    compression = 216 + 21 * rounds
    init_rows = {'organizer_constant_words': 201 * 8, 'four_field_inversions': 4 * 512 * 5, 'six_table_pages': 6 * 1024, 'entry_call_and_bounds': sum(INIT_CLOSE_ACTIONS.values())}
    setup_rows = {'three_field_inversions': 3 * 512, 'nine_mds_products': 9 * 256, 'three_line_solves': 3 * 321, 'calls_branches_and_stores': sum(SETUP_CLOSE_ACTIONS.values())}
    stage_a_rows = {'random_word_and_call': 2, 'two_field_reductions': 512 * 2, 'two_sampler_control_paths': 2 * sum(SAMPLER_CONTROL_ACTIONS.values()), 'stores_and_exit': 8}
    stage_e_rows = stage_e_components()
    stage_f_rows = stage_f_components()
    stage_g_rows = {'two_target_compressions': 2 * compression, 'two_reference_wrappers': 2 * sum(REFERENCE_VERIFY_OVERHEAD_ACTIONS.values()), 'pair_difference_comparison_and_branch': 2}
    trial_rows = dict(U.DRIVER_ENTRY_ACTIONS)
    plans, _plan_rows = planner_components(cfg, steps)
    output_rows = {'two_field_serializations': 2 * 5 * (1 << 18), 'two_message_copies': 2 * 4 * (1 << 17), 'two_digest_copies': 2 * 3 * (1 << 16), 'two_output_call_paths': 2 * sum(OUTPUT_CALL_ACTIONS.values())}
    offline_rows = offline_components()
    REST_ROW_COMPONENTS.clear()
    REST_ROW_COMPONENTS.update({'init': init_rows, 'setup': setup_rows, 'A': stage_a_rows, 'E': stage_e_rows, 'F': stage_f_rows, 'G': stage_g_rows, 'trial_loop': trial_rows, 'plan_misses': {'generated_planner_keys': plans}, 'output': output_rows, 'offline': offline_rows})
    return {name: sum(rows.values()) for name, rows in REST_ROW_COMPONENTS.items()}
```

## 9. Probability space, premises, and success bound

### 9.1 H-ONE

**Statement.** For the fixed target poseidon-orchard-r10-prefix-v1 and its line polynomial F of degree 152587890625, at least 0.3931 p centres have between one and sixteen usable nonzero-square roots of the monic odd part g_c. Equivalently P(E_c)>=q=0.3931 for a uniform centre. This premise is score-critical for success probability only.

**Scope.** The fixed Poseidon target poseidon-orchard-r10-prefix-v1, this line construction (the line j = 0 of the first two rounds, odd part about a centre, proof.md sections 2-3), the polynomial F of proof.md section 2.3; centres uniform on F_p. Not claimed for other round counts. The other terms of the success bound are H-NORMAL (proof.md 9.5) and proved terms: the coin bias, the stage-C zero test and the isolation lemma (proof.md 4.1.1, 9.2, 9.4); the time and memory bounds do not depend on the premise.

### 9.2 Success probability

**(a) Probability space.** The only random input is the sampler of 4.1.1. Its words are independent and uniform on `[0,2^256)`. Reduction modulo the Pallas prime has total-variation distance below `2^-128.9` per word and below `eps_coin = 2^-122` over all 65 draws.

**(b) Stage-C zero event.** Stage C tests every batch-inversion prefix for zero. If `g_c` vanishes at one of the `n1 = 77,309,411,328` points of `O1`, the trial executes the charged allocator reset and ABORTs before inversion. For one fixed point, `g_c(x)` is a nonzero polynomial in the centre of degree at most `D-1 = 152,587,890,624`. Since one residue has at most four 256-bit preimages,

    delta_C <= n1*(D-1)*4/2^256 = 4.07505558544531428109415424692223780742399603466636571890512060525331371214257371598410062E-55.

This is a proved event bound, not a heuristic. Algebraic value-domain conversion remains exact whenever the zero test passes.

**(c) Isolation.** The conservative value `eps_iso=2^-48` is substituted instead of the tighter `120(1/2+2^-127)^64`.

**(d) Bound.** With `q=0.3931`, H-NORMAL allowance `delta=0.001` and `K=1`,

    P(success) >= q-delta-delta_C-eps_coin-eps_iso
               > 0.39209.

The claim uses the conservative decimal `0.39209`. **(g) Scope and cost.** H-NORMAL changes only this probability; the ABORT prefix argument of 6.3 makes every abnormal trial no more expensive than the priced normal trace.

### 9.3 Complete support and limitations for H-ONE

For the hyperoctahedral group `B_m`, the number `k` of positive fixed points has binomial moments `E[binom(k,j)] = 2^-j/j!`. Inclusion-exclusion gives `P(k>=1)=1-sum_{j=0}^m(-1/2)^j/j!`, tending to `1-e^-1/2 = 0.3934693403`; four moments give the finite Bonferroni lower bound `151/384 = 0.3932291666...`, above `q=0.3931`. At two and three deployed S-box layers, the computed arithmetic monodromy is `B_12` and `B_62`, so the law is a theorem there. The toy-field enumeration and organizer experiments named below measure the same line construction and root event; no independence or population interval is inferred from organizer seeds.

#### 9.3(a) Signed-permutation law, moments, and deployed-constant computations


(a) *The law.* The roots of `G(c, t)` in `t` are `+-t_1, ..., +-t_m`, where `u_i = t_i^2` are the roots of `g_c`. So the Galois group `Gamma` of the cover `G(c, t) = 0` of the `c`-line acts by signed permutations: `Gamma` is a subgroup of the hyperoctahedral group `B_m` (10.3, Grok job 137). For a centre off the branch locus, `k(c)` is the number of positive fixed points of the Frobenius element: the indices `i` with `t_i` in `F_p`.

For a uniform element of `B_m`, the binomial moments of this number are `E[C(k, j)] = 2^-j / j!` for `j <= m`, so `P(k >= 1) = 1 - sum_(j <= m) (-1/2)^j / j!`. This is 0.375 at `m = 2`, 0.3958 at `m = 3`, 0.3932 at `m = 4`, and 0.3934693403 for every `m >= 12`: the Poisson(1/2) value `1 - e^(-1/2)`. The tail is negligible: `P(k > 16) < 2.3e-20`. With Chebotarev's theorem (Frobenius elements equidistributed in `Gamma`), this law is the frequency over the centres.

(b) *Moments and counts.* `E[C(k, j)] = N_j / (2^j j! p)`, where `N_j` is the number of points `(c, t_1, ..., t_j)` over `F_p` with `G(c, t_i) = 0`, `t_i != 0` and `t_a^2 != t_b^2` (for `j = 1, 2` these are the counts `N*` and `N_off` of our earlier premise `H-GEOM-w1`).

For every integer `k >= 1`, `sum_(j=1..4) (-1)^(j+1) C(k, j) = 1 - C(k-1, 4)`. This is 1 for `k <= 5` and at most 0 for `k >= 6`, and the sum is 0 at `k = 0`. So `1_(1 <= k <= DMAX) >= k - C(k, 2) + C(k, 3) - C(k, 4)` for every integer `k >= 0`, and `P(E_c) >= S_1 - S_2 + S_3 - S_4` (Bonferroni at order 4). With the moments of (a) this is `151/384 = 0.3932292`.

Hence `H-ONE` follows from four count statements, `N_1 >= (1 - eps) p`, `N_2 <= (1 + eps) p`, `N_3 >= (1 - eps) p` and `N_4 <= (1 + eps) p`, with `eps <= 0.0032835`. The premise is stated as the weaker statement `H-ONE` itself.

(c) *A theorem at two and three layers.* Let `F_N` be the truncation of 10.3: the first `N` S-box layers, degree `5^N`. On the deployed constants and the construction's line, 10.3 gives the arithmetic monodromy `Gamma = B_12` at `N = 2` and `Gamma = B_62` at `N = 3` (`pi(Gamma) = S_m`, `K = F_2^m`).

The geometric monodromy is normal in `Gamma` with a cyclic quotient. It therefore contains the commutator subgroup `{(eps, pi) : pi in A_m, prod eps = 1}` of `B_m`. That subgroup acts transitively on ordered `j`-tuples of signed distinct indices for `j <= m - 2`: `A_m` is `(m-2)`-transitive, and a free sign fixes the parity.

So for `j <= 8` the curve counted by `N_j` is absolutely irreducible, a complete intersection of degree at most `(5^N - 1)^j`. The Aubry-Perret bound gives `N_j = p (1 + rho_j)` with `|rho_j| <= (5^N - 1)^(2j) p^(-1/2)`: below `2^-53` at `N = 2` and below `2^-15` at `N = 3` (`j <= 8`).

The Bonferroni bounds of orders 7 and 8 then give `0.39346933 <= P(E_c) <= 0.39346944` for `F_2` and for `F_3`. At these depths `H-ONE` is a theorem, with margin 0.00237.

 At `N = 4`, the cycle types `(312)` and `(311,1)` of 10.3 make `pi(Gamma)` 2-transitive of degree 312. The only such groups are `A_312`, `S_312`, and the groups between `PSL(2,311)` and `PGL(2,311)`, whose non-identity elements fix at most two points. Centres with `k(c) = 3` and `k(c) = 4` occur (our runs, 10.5.1), and the 312-cycle is odd, so `pi(Gamma) = S_312`. The sign kernel at `N = 4` is not computed.

(d) *Measured.*
-  Toy fields, exact over all centres: deployed constants reduced modulo `p = 1,048,627` and six random-constant seeds, 3 to 8 S-box layers, partial rounds included, 27 cases. `P(k >= 1)` lies between 0.39214 and 0.39436; the largest deviation from 0.3934693 is 0.00133, that is `1.36 / sqrt(p)`.
- The real field: the organizer-run tests of 10.5.1 and our runs, reproducible observations at `m = 12` and `62`; no probability bound is drawn from them.

(e) *The extrapolation.* At `N = 16` neither the monodromy nor the counts can be computed. Weil's bound exceeds `p` for `j >= 2` (relative error `2^21.6` at `j = 2`).

The premise states that this `F` stays within `0.0003693` of the law of (a) (`q = 0.3931 <= 151/384 = 0.3932292`): no structure appears between the third layer and the 16-th that changes the law of the positive fixed points by 0.1%.

The measured deviations shrink like `p^(-1/2)` and do not grow with the degree. On the toy fields the deviation is `1.36 / sqrt(p)` . The counts of Grok job 139 give `eps ~ 3.1 / sqrt(p)` over degrees 5 to 1,953,125 (10.3).

#### 9.3(b) Exact toy-field table

| field | layers | exact cases | full-centre range | largest deviation |
| --- | ---: | ---: | ---: | ---: |
| `p=1,048,627`, deployed constants plus six fixed random-constant seeds | 3 through 8 | 27 | 0.39214 through 0.39436 | 0.00133 |

#### 9.3(c) Extrapolation

The theorem reaches the deployed constants through three S-box layers. H-ONE extrapolates the same law to depth 16 with the explicit 0.0003693 allowance.

**Limitations.** It concerns this F, not every polynomial of degree D: it is false for permutation polynomials (k = 0 at every centre) and for a decomposable F with imprimitive monodromy (the axis line of proof.md 10.3, Theorem C), and false at one layer (m = 2: the law gives exactly 0.375). At N = 16 neither the monodromy nor the counts are computed (Weil's bound exceeds p for the fibre powers of degree 5^16); the premise is the extrapolation of a law that is a theorem at N = 2, 3 and measured on toy fields and at N <= 5. The organizer tests compute k(c) inside the submitted program; the runner checks only the returned witness pairs, so they are evidence under trusted execution of that program, printed in full in experiments/exp_euclid.py. The success bound assumes nothing about the organizer-seeded trials (no independence or identical distribution of the trials is used).

### 9.4 Isolation lemma

For distinct roots `u,v`, the quadratic-character sum `sum_a chi((a+u)(a+v))=-1`; therefore a fresh shift separates the pair with probability at least `1/2-2^-127`. Four successful halvings reduce degree at most 16 to one. The union bound over at most 120 pairs gives `120(1/2+2^-127)^64 < 6.6e-18 < 2^-48`. Section 9.2 explicitly substitutes the looser `2^-48` value.

### 9.5 H-NORMAL

**Statement.** For the centre c uniform on F_p, the Euclidean remainder sequence of (g_c, R_c - 1), where g_c is the monic odd part of proof.md section 3 (degree m = 76,293,945,312) and R_c = S^((p-1)/2) mod g_c, is normal down to its gcd (deg(R_c - 1) = m - 1 and every quotient has degree 1) except with probability at most delta = 0.001 (2^-9.966). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, proof.md 4.4, 6.3). With H-ONE (q = 0.3931) and one centre (K = 1) the success bound is q - delta - delta_C - eps_coin - eps_iso = 0.39209 (proof.md 9.2).

**Scope.** The pairs (g_c, R_c - 1) of the target poseidon-orchard-r10-prefix-v1, c uniform on F_p. It enters only the success probability: the time and memory bounds hold for every remainder sequence, because a trial with an abnormal sequence ends at its first failed test after executing a prefix of the charged work (proof.md 6.3). Not claimed for other round counts. The premise is bradcush's (entries e6dcb600 and 1aa56884); the organizer-run tests follow gta6rp's entries (fe269c23); the split of the success allowance (q = 0.3931 with a separate H-NORMAL delta, here 0.001) follows cryptogakusei's entry 4888e783; delta = 0.001 is that of our accepted r = 9 entry 5b96dbb5.

**Extrapolation and evidence.** For a uniformly random pair of degrees m and m - 1 the sequence is abnormal exactly when one of the m principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most 2m in the coefficients, so by Schwartz-Zippel the probability is at most 2 m^2 / p < 2^-180.7; the premise extrapolates a much weaker form of this random-pair behaviour (delta = 0.001) to the structured pair (g_c, R_c - 1). Measured support, organizer-run (proof.md 10.5.1): the six experiments euclid-normal-n2-t256-l2-a to -f compute the complete Euclidean sequence of (g_c, R_c - 1) for this construction on the truncation F_2 of the digest polynomial (proof.md 10.3; m = 12) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; euclid-normal-n3-t24 and euclid-normal-n4-t2 do the same at m = 62, 312. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (delta = 0.001 is the declared premise). Our local runs of the eight entries: 3,098 sequences, all normal. Reported by our earlier entries, not organizer-run (proof.md 10.5): the complete sequences on the sibling targets with r' = 0 (8 centres, m = 7,812) and r' = 1 (2 centres, m = 39,062), every quotient of degree 1.

**Limitations.** The Schwartz-Zippel bound does not transfer, because the coefficients of R_c have degree about p in those of g_c. The success bound stays at least 0.39 for every delta <= 0.0030999 (proof.md 9.2(d)), above the stated delta = 0.001. The organizer-run tests are at m = 12 to 312, far below m; normality is computed inside the submitted program and the runner checks only the returned witness pairs. The success bound assumes nothing about the organizer-seeded trials (no independence or identical distribution of the trials is used).

## 10. Evidence

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypothesis of our earlier premise `H-GEOM-w` (the law of 9.3; not declared here) exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-ONE` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.

**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypothesis of our earlier premise `H-GEOM-w` (the law of 9.3; not declared here) exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B. Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the construction's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 16`; the line and the first layers do not depend on r). The results:

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the construction's line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-ONE` (9.1) extrapolates the measured trend (`w = 1` at `N = 1, 2, 3` on the deployed constants, below) to `N = 16`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the construction's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend, and the lemma gives w = 1 or w = 2 given (a) and 2-transitivity.

**Grok job 139 (the counts of the premise on toy copies).** Grok (xAI) computed `N*` and `N_off` exactly for width-3 Hades toy permutations over prime fields `p < 2^22` with `p mod 5 != 1` (S-box `x -> x^5`, uniformly random MDS matrix and round constants, the line `(L, 2L+1, 3L+5)`, `N` full rounds and `k` partial rounds, `deg F = 5^(N+k)` up to 1,953,125), by the fibre counts `N* = sum_y m_y (m_y - 1)` and `N_off = sum_c 4 r(c) (r(c) - 1)` (checked against brute force on the small cases), on 1,316 generic seeds with `p >= 1024` (the five degenerate seeds, where the degree drops, are excluded). The relative error `eps_obs = max(|N*/p - 1|, |N_off/p - w|/w)` with `w = 1` is `<= 0.2197` for every generic seed with `p >= 2053`, and the least-squares fit is `eps_obs = 3.10 / sqrt(p)` for a typical seed (`5.17 / sqrt(p)` for the maximum of four seeds), with no dependence on the degree (adding a term linear in `deg F` moves `R^2` from 0.5508 to 0.5509; the mean of `eps sqrt(p)` is 2.3 to 3.7 for every degree from 5 to 1,953,125); at `p = 2,097,169` the largest generic `eps_obs` is 0.0068. These counts support the premise of 9.1: the deviations shrink like `3 / sqrt(p)` and do not grow with the degree.


This section is the evidence for the premise `H-ONE` and for the digest of the target. The computations of 10.3 are ours; the experiments of 10.2 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.2 The organizer experiments declared in `experiments/manifest.json`

Sixteen experiments of kind `python-message-pairs-v1` (five here, eleven in 10.5.1 and 10.5.2), run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The three Python sources are 58,143 bytes together (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r10-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.


(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 10: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining sixteen rounds applied to `alpha + beta W` (`deg F = 5^16`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-ONE` is about (a root of `g_c`). The count of returned pairs at each width is a reproducible observation of the construction's own antipodal pairs on the target; no probability, rate or population bound is drawn from it (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed), and it does not enter section 9.


### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 10` applies the Euclidean algorithm to `g_c` (degree `m = 76,293,945,312`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. This section and 10.5.1 are the measured support of the premise `H-NORMAL` (9.5): stage D is charged for the normal remainder sequence and a trial ends at the first quotient of degree other than 1 (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at the gcd (degree 0, or degree 1 at the r' = 0 centres 2, 4, 7) after `m - deg gcd` divisions, and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core.

At r = 10, the live ledger derives 9,895,806,318,240 bytes and 8,669,211,530,023,973 operations. The organizer sandbox does not host that scale; sections 6 and 7 give the finite formula counts.

### 10.5.1 Organizer-run tests: normality (`experiments/exp_euclid.py`)

Eleven experiments of kind `python-message-pairs-v1`, declared in `experiments/manifest.json` and run by the organizer's runner (program `experiments/exp_euclid.py`, 25,241 bytes, Python standard library only, the program of our r = 9 entry `5b96dbb5`): the normality tests `euclid-normal-n2-t256-l2-a` to `-f` (two centres per trial, `m = 12`, 512 sequences each, 3,072 in all), `euclid-normal-n3-t24` and `euclid-normal-n4-t2` (one centre per trial, `m = 62` and `312`), and the good-centre tests `euclid-gcdpos-n2-t256-a`, `-b` and `euclid-gcdpos-n3-t24` (10.5.2). The design follows gta6rp's organizer-run normality tests (entry fe269c23, its 10.5.1); the program is our own. For each computed trial the program takes a centre `c` from the trial seed (the rule of `exp_line.py`) and builds, exactly over `F_p`, the polynomial `F_N(c + X)`: the `F_N` of 10.3 (start state `alpha + beta W` of the line `j = 0`, the S-box layers of rounds 2 and 3 (full), then 4 and 5 (partial, coordinate 0), the MDS after each; degree `5^N`). It checks `F_N` against direct iteration of those layers at `c + 1`, `c - 1`, `c + 2`, `c - 2` and the odd-part identity `2 x g(x^2) = F_N(c + x) - F_N(c - x)` at `x = 1, 2`; takes the monic odd part `g` (degree `m = (5^N - 1)/2`); computes `R = X^((p-1)/2) mod g` (253 squarings and 45 multiplications by `X`); and runs the complete Euclidean sequence of `(g, R - 1)` down to the zero remainder, recording the degree of every quotient. The sequence is normal when `deg(R - 1) = m - 1` and every quotient has degree 1, the condition of 6.3 and 9.5. A normality trial whose sequences are all normal and pass the checks, or a good-centre trial whose checks pass with `deg gcd(g, R - 1) >= 1`, returns two distinct canonical messages: the points `c + s` of the line, `s = 1, 2, ...`, are mapped back to `(nk, rho)` as in 10.2(b), and the first two whose digests of the selected target agree on the first 6 bits of the big-endian reading are returned. Among 65 points such a pair always exists, so a computed trial that passes always returns a pair. Every other trial, and every trial past the first `T` (`T` = 256 for the `n2` entries, 24 for the `n3` entries and 2 for `n4`, the sandbox budget of 20 s), returns two nulls. The organizer-checked count of returned pairs therefore equals the number of computed trials that pass. The per-trial counts listed in the manifest are reported as observations, which the runner labels untrusted. Expected: every computed sequence is normal in the normality tests, so all 6 x 256, 24 and 2 computed trials return a pair; zero abnormal in the 3,072 sequences of the `-l2` entries is a reproducible observation consistent with `H-NORMAL`, and `delta = 0.001` is the declared premise (9.5), not an interval computed from these runs. The good-centre tests are in 10.5.2. No probability, rate or population bound is drawn from any of these organizer-seeded trials (public seeds; nothing is assumed about the trials being independent or identically distributed), and none enters section 9. For `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2` (its layers come before the final full rounds), so the tests measure the same family of pairs as the premise; only the witness uses the digest at r = 10.


### 10.5.2 Organizer-counted good centres (`H-ONE`)

