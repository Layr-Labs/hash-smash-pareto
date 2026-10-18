## 1. Claim

Target: `poseidon-orchard-r20-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, twenty partial rounds 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 and 23, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

**What this entry is, and credit.** This entry is Jbenisek's algorithm at r = 20 (entry 5d6dda61, the base of this package's passed coefficient-domain entry fe269c23; and his value-domain entry 7b276afd, the best-scoring entry at this round count (in review, not human-accepted), normalized cost 117.88213) with stage C in the value domain (bradcush's method, 1aa56884, as re-implemented and charged by Jbenisek in 7b276afd; section 4.6) and the lean stage D of bradcush's r = 21 entry e6dcb600 (section 4.4). Jbenisek (entry 5d6dda61, 7b276afd and the family of entries they belong to) designed the algorithm and the construction, wrote the premise `H-GEOM-w1` with its reduction, the proof text reproduced here, the rows of the ledger other than C and D, the evidence and the experiments; in 7b276afd he re-implemented bradcush's value-domain stage C in his row-kernel cost model, fixed its parameter rule (`h = 2^32`, the start monomial, the convolution lengths, the group buffer) and fixed its parameters at this r and proved the bound on its zero test (9.2(f)). bradcush contributed (1) the value-domain stage C (entry 1aa56884, r = 21, judged not_evaluable for an unpublished reason; its lemmas 4.6 and 4.7, the eight steps and the zero-test argument are reproduced here in this package's words), and, from e6dcb600, (2) the truncated second recursive call of the half-gcd (lemma 4.4); (3) stage D charged for the normal remainder sequence, with the quotient and return tests, the ABORT and the premise `H-NORMAL`; (4) block products with blocks of `2^31` coefficients, a one-row block transform of `2^32` points and the chunked outer product (scheme (c)) with register-blocked outer kernels, used here by the Newton reciprocal of 4.6 and by stage D; (5) the allocator's flat statistics charge on every allocation and free. Passages from those entries are reproduced with attribution; "we" and "our" in reproduced passages refer to their authors, and none of the authors has reviewed this package. This package adds: (a) a re-implementation of the value-domain stage C (Appendix E, `powx_vd`), written from the printed program of 7b276afd (read, not run), which reproduces the row C asserted by Jbenisek's six value-domain entries (r = 17, 18, 19, 20, 21) to the operation under his charging conventions (`checkvd`) and is then evaluated under this package's conventions (the set-up products by the block products of 4.5 with this package's chunk bound, and the statistics charge of 4.2 on every allocation and free); (b) a re-implementation of e6dcb600's stage D ledger (Appendix E, from its printed program, read, not run), which reproduces the totals asserted by e6dcb600 at r = 21 exactly; (c) the evaluation at this r; (d) the chunk bounds of the products at this r (4.5), chosen by a sweep of the ledger; (e) the placement of every array in the two-ended pool and slab classes of 4.2 (Jbenisek's allocator), with the remainder of a division written over its dead dividend, and the arena found by simulating that allocator on the complete allocation sequence of a trial (section 7); (f) the coset-solve workspace of stage B in the allocation walk; (g) an explicit charge for the reset of the allocator after an ABORT or after the zero test of stage C; (h) small-size checks of the procedures of 4.4 and 4.5 (Appendix G.2) and of the value-domain stage, lemmas 4.6 and 4.7 included, against direct computation over the Pallas field (Appendix G.3); (i) the linear two-moment success bound of 9.2(e'), which raises the success probability to 0.41286 (0.428085937 before the `H-NORMAL` allowance of 9.5) under the same premises without changing the cost; (j) the return test strengthened to fire on a zero last remainder as well (4.4, 6.3(b)), so that the prefix argument of 6.3 holds for every input; (k) the zero-test term `delta_C` of 9.2(f) carried into the success bound (no change at nine decimals). Papers: Bariant, Bouvier, Leurent and Perrin (ToSC 2022(3), the two-round bypass); Thome (2003) and Stehle and Zimmermann (2004), the padded half-gcd with both recursive calls truncated; Montgomery (1985), the reduction that lemma 4.6 performs in the value domain, and Montgomery's batch inversion (step 5 of 4.6). Grok (xAI) jobs 133-140, reproduced from entry 5d6dda61: the moment reduction and its constants, the Markov cap, the toy theorems, the certificate program, the monodromy lemma and the block-NTT schemes.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and 115648232 inverse transforms (one per coset, section 3), compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod in the value domain (section 4.6: `196` Montgomery squaring steps on the values of the residue at two sets of `n1 = 745,058,061,420,331,008` points; a zero of `g_c` on the first set ends the trial) and a half-gcd (which ABORTs the trial on an abnormal remainder sequence), and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. At most `K = 2` centres are tried, one after the other, on a single thread; the first verified collision ends the algorithm.
* `success_probability = 0.41286`: from `H-GEOM-w1` (section 9.2) with the sharper reduction 9.2(e') of this package (`P(1 <= k <= DMAX) >= E[k] - E[k(k-1)]/2`, giving `q = 0.24375` in place of Jbenisek's `q = 0.22257` under the same two moments; the score is unchanged, `K = 2` is still needed), `K = 2`, `eps_iso < 2^-48`, `eps_coin < 2^-128`; with the ABORT of stage D and the zero test of stage C the bound is `P >= 1 - (1 - q + delta)^K - K (eps_iso + eps_coin + delta_C)`, `delta = 0.01` from `H-NORMAL` (9.5) and `delta_C` the probability that `g_c` vanishes at a point of the set `O1` of 4.6, bounded in 9.2(f) without a premise (below `10^-14` with the other two terms). Its exact value is `0.412860937` (9.2(g); `0.428085937` with `delta = 0`); Jbenisek's entry claimed `0.39560` from `q = 0.22257`.
* `time_log2 = 70.15381` in target-compression units (`C(20) = 636` primitive operations per unit): the operation count of section 6, `T_fixed + K * T_trial + T_off` with every trial charged in full (stage C by its fixed schedule, 4.6, which a trial that fails the zero test executes a prefix of; stage D for the normal remainder sequence, which bounds every trial since an abnormal one aborts after a prefix of that work, 6.3; stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 834,634,600,684,798,065,055,682` operations, `log2(N_max / 636) = 70.15260796`, claimed as `70.15381`: rounded up at five decimals after adding 0.0012, a margin of `695,700,991,597,112,623,181` operations for any charge this count may have missed. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 66.718` (`121,195,470,720,620,202,060` bytes = `2^66.71590`, section 7): the arena found by simulating the allocator of 4.2 on the allocation sequence of a trial, plus code, static data and stack. The claimed bound is above the arena and above the live-set peak of section 7 taken by itself, so it does not depend on accepting the allocator model. Normalized cost `70.15381 + (66.718 - 20) = 116.87181`, against 117.88213 for Jbenisek's value-domain entry 7b276afd (time 70.89213, memory 66.990) and 118.15634 for this package's coefficient-domain predecessor fe269c23 (time 71.37934, memory 66.777). This is the Pareto track's scoring policy `hashsmash-orchard-tm-v1` (`normalizedTimeMemoryLog2 = time_log2 + max(0, memory_log2_bytes - 20)`); the cost model's own time-only score is `time_log2`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `130` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^26`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Declared heuristics (claim.json): `H-GEOM-w1` (score-critical, section 9.1, Jbenisek's premise, unchanged) and `H-NORMAL` (score-critical for the success probability only, section 9.5, e6dcb600's premise restated at this r). The costs are the declared cost model, not heuristics: the charging rules of section 4.2 (the register file of 18 words of 256 bits whose operands are not charged as loads, Jbenisek's disclosed interpretation of the model; every array access is charged), and the arena of section 7, the capacity of the allocator of 4.2 on the allocation sequence of one trial, found by simulation. Everything else is proved or counted: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the truncation lemma 4.4, the value-domain step and the extension (lemmas 4.6 and 4.7), the bound on the zero test of stage C (9.2(f)), the Cauchy-Schwarz reduction (section 9.2), the isolation lemma (section 9.4), the independence of the centres, the cap rules and every operation count (sections 4, 6, 7).

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a
bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the
deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`.
`(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`.
The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant
`M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let
`(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, where
`d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i`
(the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 (partial), 60, 61, 62, 63 (full) put twenty-six S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^26 = D = 1,490,116,119,384,765,625`. The leading coefficient is obtained by
propagating leading coefficients through the twenty-six layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x07aca9fe41420cd68f8ef9981201f15871afba84a8821b5e4b6afb11566217d2`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 745,058,059,692,382,812`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. At this r no transform of `H >= m + 1` points exists: `p - 1 = 2^32 * 3 * q` has roots of unity of order `3 * 2^a` for `a <= 32` only, and `m + 1 = 745,058,059,692,382,813 > 3 * 2^32`. Let `B = 3 * 2^31 = 6,442,450,944`, `zeta` a primitive `2B`-th root of unity (`2B = 3 * 2^32` divides `p - 1`) and `omega = zeta^2`, a primitive `B`-th root. Let `kappa = ceil((m + 1) / B) = 115648232`, `v_k = 2^k` and `u_k = v_k^2 = 4^k` for `k < kappa`, and `z = 4^B`; the `kappa` numbers `n_k = u_k^B = z^k` form a geometric progression and are pairwise distinct, because the order of `z` exceeds `kappa` (Appendix G: `z^d != 1` for every divisor `d` of `p - 1` up to `2 * 10^8`, and `kappa < 2 * 10^8`). The evaluation points are `s_{k,i} = v_k zeta^i` for `k < kappa`, `i < B`, so that `S_{k,i} = s_{k,i}^2 = u_k omega^i`, and `g_c(S_{k,i}) = (F(c + s_{k,i}) - F(c - s_{k,i})) / (2 s_{k,i})`. Write `g_c(x) = sum_{t < kappa} x^{tB} h_t(x)` with `deg h_t < B`. For `y = omega^i` we have `y^B = 1`, hence `g_c(u_k y) = w_k(y)` with `w_k(y) = sum_t n_k^t h_t(u_k y)`, a polynomial of degree `< B`. One inverse transform of size `B` of the values `(g_c(S_{k,i}))_i` returns the coefficients `w_k[j] = u_k^j sum_t n_k^t h_t[j]`. After multiplication by `u_k^{-j}`, for every `j < B` the numbers `W_k[j] = sum_t n_k^t h_t[j]` (`k < kappa`) are the values of the polynomial `h^(j)(X) = sum_t h_t[j] X^t` at the nodes `z^k`, and its coefficients `h_t[j] = g_c[j + tB]` are recovered from them by two correlations of length `kappa` (Lagrange interpolation at geometric nodes, the chirp-z form). Let `M(X) = prod_k (X - z^k) = sum_i mu_i X^i`; the q-binomial theorem gives `mu_{kappa-j} = (-1)^j z^{j(j-1)/2} [kappa choose j]_z`, and `M'(z^k) = z^{k(k-1)/2 + k(kappa-1-k)} prod_{j <= k} (z^j - 1) prod_{j <= kappa-1-k} (1 - z^j)`. With `a_k = W_k[j] / M'(z^k)` and `A(i) = sum_k a_k z^{ki}` (`i < kappa`) we have `h_t[j] = sum_{i > t} mu_i A(i - t - 1)`. Since `z^{ki} = z^{C(k+i,2) - C(k,2) - C(i,2)}` with `C(n,2) = n(n-1)/2`, `A(i) z^{C(i,2)}` is the correlation of the sequence `a_k z^{-C(k,2)}` with the chirp `z^{C(n,2)}` (first correlation), and `h_t[j]` is the correlation of `A` with `(mu_1, ..., mu_kappa)` (second correlation). Each correlation is one cyclic convolution of length `S = 268,435,456` (the smallest `2^a` or `3 * 2^a` that is at least `2 kappa - 1`), done with the transform of length `S` (forward, pointwise product, inverse); the transforms of the fixed sequences (the chirp and `mu`) and the constants `mu_i`, `1/M'(z^k)`, `z^{-C(k,2)}` are computed once per trial and shared by the `B` positions `j`. Appendix G runs this solve against the direct recovery at `kappa = 7`. The `2 kappa B = 1,490,116,122,840,662,016` evaluations of `F` are each charged as one target-compression unit (`C(20) = 636` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation. The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 s_{k,i})`, two multiplications for the recurrences of `s_{k,i}` and `1/s_{k,i}`, one store with its address operation, the loop control, the update of the row counter, and the executed shifts, masks, ors and loop control of the bit-reversed index, which are counted inside that function) and the solve (per `j`: two correlations, each two transforms of length `S` with `S/2 log2` butterflies at the charge of the model's own pass cost and `10 S` operations for the pointwise product and the scalings, and `14 kappa` operations for the chirp scalings, the division by `M'`, the loads and the stores) and its once-per-trial constants (`kappa` times two inversions, 40 operations per index, four transforms of length `S` and `10 S` operations) are charged on top.


## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (1,490,116,122,840,662,016 evaluations + 115648232 inverse NTTs of size 6,442,450,944 + the geometric solve of the 115648232 cosets (two correlations of length 268,435,456 per position) + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (value-domain powering, section 4.6: the residue is held by its values on two point sets of n1 = 745,058,061,420,331,008 points; 196 Montgomery squaring steps from S^(2^57), 45 of them with the multiplication by S; a zero of g on the first point set ends the trial, next t)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4; every division tests that its quotient has degree 1, and on any other quotient the trial ABORTs: it ends, the allocator is reset, next t)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (636 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 59 bits after the leading one are zero, so the algorithm may start from any monomial `S^v` with `v = 2^j`, `j <= 59`; the value-domain stage (4.6) starts from `v = 2^57` (a multiple of `h = 2^32`, so that `S^v` is constant on every coset, and small enough for a short Barrett start; Jbenisek's choice, `VSHIFT = 2`), which absorbs 57 of the 253 squarings, and the squaring loop of stage C has 196 steps, of which 45 also multiply by `S` (a pointwise multiplication by the point, 4.6).

Stopping rule over the `K` centres. The loop bound `K = 2` is a constant of the algorithm. A trial is run to its end, or to an ABORT in stage D, or to its end at the zero test of stage C (4.6, step 5), whatever its outcome; the claim charges every trial at its maximum (stage C in full, stage D for the normal remainder sequence, stages E to G at their worst case, section 6), so a trial that fails early or aborts is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B and C have lengths fixed by `m` and the exponent (sections 3 and 4.6), the powering has a fixed number of steps, and on a normal remainder sequence the half-gcd has a fixed recursion: 53 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 372,529,029,846,191,406` and is halved, rounded up, until it is at most 96) and at most 53 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 745,058,059,692,382,812 to at most 192). A remainder sequence that is not normal is detected at its first quotient of degree other than 1, before any work that the normal sequence would not do, and the trial ends there (section 6.3); a zero of `g` on the point set `O1` is detected by the batch inversion of 4.6 (step 5), before the loop, and the trial ends there. Hence the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

The only randomness of the algorithm is the cost model's random-word primitive (fresh independent algorithmic coins): an independent uniform 256-bit word, each use returning a fresh word, uniform on `0..2^256-1` and independent of everything else, and costing one operation. **Probability space:** every probability of section 9 is over these words. A draw is one fresh word `y`; the draw is `x = y mod p`, computed by at most three steps `if y >= p then y := y - p` (`y < 2^256 < 4p`, so three steps bring `y` below `p`). Write `2^256 = 3p + s0` with `0 < s0 < p`: the residues below `s0` have exactly four preimages below `2^256` and the other `S3 = p - s0 = 4p - 2^256` residues have exactly three, so `P[x = z] = 4/2^256` or `3/2^256` for every residue `z`, every residue has probability at least `3/2^256`, and all but `S3` residues have probability `4/2^256`. The draw is within statistical distance `S3 (1/p - 3/2^256) = 1.574e-39 (2^-128.90) < 2^-128` of uniform on `F_p`. A draw costs 31 operations: for the word one random-word operation, one load, one store into the cell `y` and three control operations (two addresses, the increment of the word index), 6 in all; for the reduction three steps each of a comparison, a conditional branch and a field subtraction (9 operations), with the loop control of 3 per iteration and 2 on exit (11); one Montgomery conversion of `x` (1); the entry of the call (2) and the address of `y` (2). Draws are made once per trial for the centre and once per isolation round for the shift: at most `K (1 + Z) = 130` draws, `130` words. No word is used twice, and the number of words used before a draw depends only on earlier words, so each draw is independent of the earlier course of the algorithm.

#### 4.1.2 Stage E: isolating a root of G

`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). The roots `r` of `G` are the usable `S`. While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw `a` (a draw as in 4.1.1; if it is 0, `a := 1`, since the Taylor shift uses `1/a`; the zero test is 5 operations and the replacement 2, charged in every round), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds.

### 4.2 Machine model and charging rules

Every operation of the algorithm is counted where it executes; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation).
* every loop: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). Loops over the elements of an array written eight elements per pass (the pointwise, copy, fold and subtraction loops of the powering and of the products) are charged 3 per pass of eight, 1 for the bound, 2 when the main loop is left, and 3 per iteration for the remaining 0 to 7 elements.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, comparison, conditional branch, assignment of a register, and the selection of an element of the register block (16 data words) by a computed index. Data-dependent tests are charged per executed test.
* index arithmetic uses only shifts, additions, subtractions, comparisons and branches (the benchmark's primitive list has no integer multiplication, division or modulo): a multiplication by a power of two is a shift, by 3 or 5 a shift and an addition, and a product of an index and a stride is a running sum; each is charged as a control operation where it occurs.
* transforms: a transform of size `3 * 2^a` is a twiddle-free radix-3 stage (8 operations per leaf) followed by three rows of radix-2 passes of at most four layers. A pass works on blocks of `2^k <= 16` points held in registers; each butterfly is three field operations (none for the multiplication when the twiddle is 1), each twiddle is one load with its address operation (the first twiddle of a layer also 2 operations of address formation), and the group and block loops around a block are charged 3 per iteration and 2 on exit. The working registers are a disclosed assumption: the 16 data words, the twiddle operand and the butterfly temporary, a register file of 18 words of 256 bits. The 256-bit constants of the radix-3 stage are loaded at every use.
* block transform (e6dcb600, section 4.5): the transform of `NB = 2^32` points used by the block products is one row of the radix-2 passes above (eight passes of four layers), preceded by a copy of the block into the transform array (a load and a store per coefficient, each with its address operation) and a zero fill of the rest (a store per element), with the loop control of the eight-element rule; the inverse is the inverse passes; the factor `NB` is removed where the result is placed.
* outer transforms (e6dcb600, section 4.5): a transform of `n = 2^a` or `3 * 2^a` points across the blocks of an array, at each of `cnt` positions, is a twiddle-free radix-3 stage (kernel `ob3`, Good-Thomas) when `3 | n`, then in each of the (one or three) rows of `2^a` points radix-2 passes of at most three layers (kernels `ob2f`, `ob4f`, `ob8f`; inverse `ob8i`, `ob4i`, `ob2i`, then `ob3` with the conjugate constant). A pass of `k` layers keeps its `2^k` data words and `2^k - 1` twiddles in registers for the whole loop over the positions (`ob8f`: 8 + 7 + the butterfly temporary = 16 of the 18 words of the register file). The kernel text is printed in e6dcb600's Appendix E and is charged under these rules: a load or a store is 2 (the access and its address operation), a field operation 1, a loop 3 per iteration and 2 on exit, a call 10; the driver charges 4 per block address and 3 per twiddle index, and the twiddle table of the transform is built at each call (`6 n + 2`). The per-call charges `c0 + c1 cnt` are `ob3` (16, 23), `ob2f`/`ob2i` (14, 14), `ob4f`/`ob4i` (18, 31), `ob8f`/`ob8i` (26, 71): for `ob(2^k)` the call 10, the `2^k - 1` twiddle loads and the loop exit 2, and per position `2^k` loads and `2^k` stores (2 each), `k 2^(k-1)` butterflies of 3 operations and the loop step 3; for `ob3` the call 10, two constant loads and the loop exit, and per position 3 loads, 8 field operations, 3 stores and the loop step (Appendix E, `_kch`, asserts these values, which equal e6dcb600's executed counts).
* random words: the cost model's random-word primitive (an independent uniform 256-bit word) is one operation per word. The word of a draw is also loaded, stored into the cell `y` of the draw and addressed (one load, one store and three control operations), 6. A draw is that word (6), the reduction modulo `p` (three steps each of a comparison, a conditional branch and a field subtraction, 9, with the loop control of three iterations, 11), the conversion of the result to the internal representation (1), the entry (2) and the address of `y` (2): 31 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: 636 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation (the two-ended pool and slab classes of Jbenisek's entries at r = 8 to 21; the end of every statement is this package's, 4.4 and 4.6): every array is taken from one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes (`need` bytes), and `need` decides the allocator. A block of more than `2^51 = 2,251,799,813,685,248` bytes comes from the pool, one region with two ends (low and high): its blocks follow each other in address order, each with a header (size, size of the previous block, in-use flag), no two free blocks are adjacent, and the unused middle between the two ends is one free block. Each allocation statement uses one end, fixed in advance by the rule of 4.4 (stage D: an end derived from the result end `ys` passed to the call of `hgcd` that executes the statement) and 4.6 (stage C: a constant of the statement); the statements of stages A and B and every statement not named there use the low end. A request walks the blocks of its end from that end inward, takes the first free block with at least `need` bytes (the unused middle is the last block of either walk), cuts it on the side nearest its end and leaves the rest free when the rest is at least 128 bytes (else it belongs to the block); a free merges the block with a free neighbour on either side, the unused middle included. Since no two free blocks are adjacent and a walk ends at the middle, a walk examines at most `2 P + 1` blocks, `P` the live blocks of its end. A block of at most `2^51` bytes comes from the slab classes: its class `j` is the least `j >= 7` with `2^j >= need`; a request takes the first slot of the free list of its class, else a new slot of `2^j` bytes from the end of the slab area, and writes the class and the in-use flag into the header; a free puts the slot on the free list of its class. Charges, inside the stage rows: every allocation `1 + 120 + 13 (2 L + 1) + 64` operations, `L` the live blocks at that point (this covers a pool request, 97 operations besides the walk and 13 per block examined with `P <= L`, and a slab request, at most 126, as in Jbenisek's entries), and every free `105 + 64`; the second 64 is the flat statistics charge that e6dcb600 adds on every allocation and free. An allocation and a free that the program replaces by writing in place (the remainder of a division written over its dividend, 4.4) stay charged. The memory of both allocators is the arena of section 7.
* allocator statistics (e6dcb600's reading of the rule above): the flat 64 of the allocator's statistics is charged on every allocation and on every free in Appendix E (rows C and D), and as an allowance of 64 for each of at most `10^10` allocator calls per trial in the rows A, B, E, F and G, which this package takes from Jbenisek's entry unexpanded (section 6).
* trial loop: the test of the trial counter, its increment and the bookkeeping of the trial, at most 12 operations per trial, are `TRIAL_EXTRA` = 12 in the ledger; the loop test and update of stage A are 5.
* the offline derivation of the constants is charged in section 6.2.


### 4.3 Stage C: the powering schedule (cyclic form, below the block length; block mode in 4.5)

Stage C of this package is the value-domain powering of 4.6; neither the cyclic step below (Jbenisek's form for moduli below the block length) nor the block-mode step of e6dcb600 (used by this package's coefficient-domain ledger entries at r <= 20) is executed at this r. What is used from this section is the cyclic product itself (one transform of `3 * 2^a` points, rows processed one at a time) for the products below the block length (the first Newton levels of the reciprocal of 4.6, step 1, and the lower levels of the half-gcd), and the Newton iteration for a reciprocal, which 4.6 runs modulo `X^ell` with `ell = 144,115,189,803,804,069`. (The text below is Jbenisek's.)

For the exponent `E` (here `(p-1)/2`), `m` the degree of the modulus, `N = 3 * 2^a >= 2m - 1` and `N' = 3 * 2^b >= m + 1`. A transform of size `3 * 2^a` is a twiddle-free radix-3 stage (Good-Thomas; each radix-3 leaf costs 8 operations) followed by three independent
rows of radix-2 transforms of length `2^a`, run as passes of at most four layers (blocks of at most 16 data words in registers; with the two working words the register file is 18 words of 256 bits, see section 4.2). The state is `s = a / N` so no scaling is needed in the loop.
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
### 4.4 Stage D: the half-gcd (e6dcb600's procedure: truncated second call, normal sequence with the quotient and return tests)

Notation: a polynomial is stored as its coefficient array with the top coefficient nonzero (length = degree + 1). Euclid sequence of `(a, b)`, `deg a > deg b`: `r_0 = a`, `r_1 = b`, `r_{i-1} = q_i r_i + r_{i+1}`; `d_j = deg q_1 + ... + deg q_j`, so `deg r_j = deg a - d_j`;
`R_j = Q_1 ... Q_j` with `Q_i = [[q_i, 1], [1, 0]]` (entries of degree at most `d_j`; the first-row entries of degree exactly `d_j` for `r11`), and `(r_0, r_1)^T = R_j (r_j, r_{j+1})^T`.

The text of this section up to the paragraph *Placement* is e6dcb600's (bradcush), whose procedure this package uses; it replaces the half-gcd of Jbenisek's entry, whose second recursive call received the whole reduced pair. The return test of steps (1) and (5) is strengthened by this package (it fires on a zero last remainder too, 6.3(b)); the rest is e6dcb600's text.

`hgcd(a, b, k)` (`deg a = n`) returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` (when asked) and the pair `(r_h, r_{h+1})` (when asked). The procedure: if `b = 0` or `n - deg b > k` return the identity. If `k <= 96`, plain Euclid (`poly_divrem_naive`) while the next quotient degree fits the remaining parameter; a division step whose quotient has two coefficients (the normal case) is one pass over the remainder, `r_k = a_k - q0 b_k - q1 b_(k-1)`, with `b_(k-1)` kept from the previous iteration and no copy of `a` (per element 2 loads, 2 multiplications, 2 subtractions, 1 store, each load and store with its address operation, the loop control of 3 and the test `if (k)` of 2 operations), and `R := R Q` for a two-coefficient quotient is likewise one pass per entry pair (`mul_add_q2`).
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted, no pair wanted); if it returns `d_1 != k1`, the trial ABORTs (the return test), whether or not its last remainder is zero (a normal sequence whose gcd has degree at most 96 always reaches `d_1 = k1` here, 6.3(b); a call that stops short has met either a zero remainder of the whole pair, which means a gcd of degree at least 96 > `DMAX`, or, by lemma 4.4, a quotient of the whole pair of degree other than 1; in both cases the trial cannot succeed, so no successful trial is lost); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`, evaluated cyclically on `3 * 2^j` points (the high coefficients of `c` and `d` cancel, so the cyclic result is exact); the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each of the four matrix entries are transformed once (six forward transforms of a row) and the two output rows are inverse transformed (`conv_bilin_otf`), the sign of each output being absorbed in the scale factor `1/N`; in block mode the same bilinear form by scheme (a) or (c) of 4.5; (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1` (`d_1 = deg R1`) return `R1` and `(c, d)`; (4) if `deg c - deg d != 1` the trial ABORTs (a comparison and a branch, charged at every division); otherwise divide `c = q d + e` (`q` of two coefficients: one pass, as in the base case); (5) put `k3 = k - d_1 - 1` and `s3 = deg d - 2 k3`. If `s3 > 0`: `R2 = hgcd(d quo x^s3, e quo x^s3, k3)` (the top parts, matrix wanted, no pair wanted), with the return test, and only when the caller wants the reduced pair, `(c', d') = R2^{-1} (d, e)` by `apply_inv`; if `s3 <= 0`: `R2, (c', d') = hgcd(d, e, k3)`, with the return test. Return `R1 Q R2` (matrix products by NTT, only if the matrix is wanted; the product of the two 2 x 2 matrices transforms each of the eight entries once per row, with the right-factor entries of one column pair held and the left-factor entries streamed, and inverse transforms the four outputs, `conv_bilin_otf` again; in block mode the same bilinear form by scheme (a) or (c)) and `(c', d')` when asked.
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: `(c, d) = hgcd(a, b, floor((n+1)/2))` (pair wanted, matrix not wanted), the return test, the ABORT test of the quotient degree and one division `c = q d + e` by a quotient of two coefficients, and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid with the same test; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). The only calls that want the reduced pair are those of `poly_gcd_own` and, recursively, the second calls with `s3 <= 0` inside them; every call inside a first call, and every truncated second call, wants the matrix only.

**Lemma 4.4 (truncation; e6dcb600).** Let `deg a = n > deg b`, let `a*`, `b*` agree with `a`, `b` on every coefficient of degree at least `t`, where `t <= n - 2k`, and let `q_1, q_2, ...` be the quotients and `d_j` their degree sums for `(a, b)`. Then every quotient `q_j` with `d_j <= k` is also the `j`-th quotient of `(a*, b*)`, and the stopping test of `hgcd(., ., k)` (the next quotient degree exceeds `k - d_h`, or the next remainder is zero) has the same outcome for both pairs. *Proof.* Induction on `j`. Let `q_1, ..., q_(j-1)` be common and `R = R_(j-1)`; the entries of `R^(-1)` (the adjugate of `R` up to sign) have degree at most `d_(j-1)`. So `r_(j-1) - r*_(j-1)` and `r_j - r*_j` are `R^(-1)` applied to `(a - a*, b - b*)`, of degree `< t + d_(j-1)`. Now `deg r_j = n - d_j` and the quotient of `r_(j-1)` by `r_j` depends only on their coefficients of degree at least `deg r_j - deg q_j = n - 2 d_j + d_(j-1)`. If `d_j <= k` this bound is at least `n - 2k + d_(j-1) >= t + d_(j-1)`, above the degree of the differences, so `deg r*_j = deg r_j` and `q*_j = q_j`. For the stopping test after `h` quotients: `d_(h+1) > k` holds iff `deg r_(h+1) < n - k` (or `r_(h+1) = 0`), and the coefficients of `r_(h+1)` and `r*_(h+1)` of degree at least `n - k >= t + d_h` agree, so the test has the same outcome. QED. Applied with `a* = x^s (a quo x^s)` (`t = s = n - 2 k1`), the first call's quotients are those of `(a, b)`; dividing by `x^s` changes no quotient. Applied to the second call with `t = s3 = deg d - 2 k3`, likewise; the returned `R2` is the product of the quotient matrices of `(d, e)`, so `R2^{-1} (d, e)` is the reduced pair of `(d, e)` and `R1 Q R2 = R_h` for `(a, b)`. Appendix G.2 (this package's check) runs this half-gcd against the plain Euclidean algorithm over the Pallas field and confirms that every recursive call runs on at most `2k + 1` coefficients.

**Division and the two tests (e6dcb600; the return test strengthened by this package).** On the normal remainder sequence every division of stage D (in `hgcd`, in the base case and in `poly_gcd_own`) has a quotient of two coefficients and is the one-pass division above. Two tests, 2 operations each and charged wherever they execute, detect any other sequence: the *quotient test* at every division (a quotient used by the algorithm has degree 1), and the *return test* after every recursive call and every call of `poly_gcd_own` (the call returned exactly its parameter `k` as degree count; a zero last remainder does not exempt it: this package's strengthening of e6dcb600's test, see 6.3(b)). On a normal sequence whose gcd has degree at most 96 neither test fails: by lemma 4.4 every quotient a call uses is a quotient of the whole pair, hence of degree 1, no call of `hgcd` meets a zero remainder (6.3(b)), and a call with parameter `k` stops exactly after `k` of them (with `d_j = j` the stopping test fails first at `j = k + 1`). If either test fails the trial ABORTs, so the Newton division (`divrem_fast`) of Jbenisek's entry is never run.

**Placement (this package).** These rules fix the end of the pool (4.2) of every array of stage D; they change no operation count (the allocations and frees are the same statements, in the same number, at the same live counts; Appendix E checks the totals against the untraced ledger). `poly_gcd_own` passes to `hgcd` the result end `ys` = the end of `g` and `R` (the low end; both are arrays of `n1` slots left by stage C, 4.6). (i) A call that returns the reduced pair and no matrix owns its operands, which lie on `ys`: its first call is passed `ys` (so `R1` lies inside the operands), its `apply_inv` writes `c`, `d` and its working arrays on the other end, the division and the second call use that end (the truncated second call is passed the other end), and its final `apply_inv` writes `(c', d')` on `ys`. (ii) A call that returns a matrix keeps its own arrays (`c`, `d`, the division, the outputs of `mat_mul` and its working arrays) on `ys`; its two calls are passed the other end, where `mat_mulQ` also writes its two new entries, and `mat_mul` frees all of these after writing `R` on `ys`. (iii) `apply_inv` allocates `d` before `c` (so `c`, which is freed first, is the innermost); in a product that fits one transform, the output arrays are allocated before the row buffers, and the work arrays of `mat_mul` are taken from the end of its factors, before its row buffers. (iv) The remainder `e` of a division `c = q d + e` by a two-coefficient quotient is written over `c` when the array of `c` has exactly the length of `e`'s array (block mode: `c` is an output of `apply_inv` of its exact length): each `e_i = c_i - q_0 d_i - q_1 d_(i-1)` is formed after `c_i` is read and `c` is not used after the division. The allocation of `e` and the free of `c` that this saves stay charged. Section 7 shows the effect: the pool's high-water mark is the peak of the live set at this r to within the figure stated there.

### 4.5 Products longer than `3 * 2^32` points (block mode; e6dcb600's schemes, with this package's parameters at r = 20; used by the Newton reciprocal of 4.6 and by stage D)

At this r the products of the half-gcd (4.4) and of the Newton reciprocal of 4.6 (step 1: `ell = 144,115,189,803,804,069` coefficients, products of up to `2 ell - 1` coefficients) would need transforms of up to `3 * 2^58` points. The field has no root of unity of such an order (`p - 1 = 2^32 * 3 * 463 * q'` with `q'` odd and prime to 3, so `v2(p - 1) = 32`), so every product whose transform would exceed `3 * 2^32` points is computed by blocks. The bullets up to *Choice* are e6dcb600's (bradcush) text; the parameters of this r, the workspace rule and the placement are this package's. (The squaring loop of stage C forms no product of polynomials at all, 4.6.)

* Blocks. `HB = 2^31` coefficients per block, block transform of `NB = 2 HB = 2^32 = 4,294,967,296` points (one row, section 4.2). An operand of `l` coefficients has `ceil(l / HB)` blocks. A product of two blocks has at most `2 HB - 1 < NB` coefficients, so it does not wrap.
* Scheme (a), slots (Jbenisek's). The slot `s` of a product `A C` is the sum of the block products `A_i C_j` with `i + j = s`; every block of every operand is transformed once, the slot is formed pointwise in the transform domain (`NB` multiplications per pair, additions or subtractions for the further pairs), inverse transformed once, and placed at offset `s HB` of the output (a load, the multiplication by `1/NB` and the sign, a store, and for the coefficients that overlap the previous slot a load of the output value and an addition, or a subtraction when the placement subtracts into an array). Only the slots that meet the wanted window are formed. Workspace: the block spectra of the operands and one accumulator of `NB` elements.
* Scheme (c), chunked outer product (e6dcb600). Write `Y = X^HB` and `A = sum_i A_i Y^i` with blocks `A_i` of `HB` coefficients. Let `need` be the length modulo which the wanted coefficients are exact: for a window `[ws, ws + len)` of a product of true length `L`, `need = max(ws + len, L - ws)` (an index `i` of the window receives `i + N` only if `i + N < L` and `i - N` only if `i >= N`); for `apply_inv`, `L` is the true length of the outputs (their high coefficients cancel, 4.4); for the product `q g` of e6dcb600's coefficient-domain squaring step, which this package does not form, `need = m + 1` by its lemma 4.5. Let `n2` be the smallest `2^a` or `3 * 2^a` with `n2 HB >= need` (`n2` divides `3 * 2^32`), `w` a primitive `n2`-th root of unity; the product is computed modulo `Y^n2 - 1 = X^(n2 HB) - 1`, which by the choice of `n2` gives the wanted coefficients exactly. Choose a power of two `nc` (the number of chunks) and put `n3 = n2 / nc`. Chunk `j < nc` handles the outer points `o = j + nc u`, `u < n3`. For each operand of more than one block it forms the chunk array of `n3` rows of `HB` elements, row `u' = sum over the blocks i = u' (mod n3) of w^(j i) A_i` (twist and fold), and transforms it with the outer transform of `n3` points (root `w^nc`) across the rows, at each of the `HB` positions. Row `u` then holds `A mod (X^HB - w^o)`. At each outer point the rows of the operands are transformed with the block transform (zero-padded to `NB` points), multiplied pointwise and summed over the products of the bilinear form (with their signs), inverse transformed, and folded modulo `X^HB - w^o` (lower half plus `w^o` times the upper half) into the row `u` of the output chunk array, which overwrites a row of an operand chunk array that is no longer needed. Each output chunk array is inverse transformed across the rows (root `w^-nc`) and untwisted into the output: block `s` of the result modulo `Y^n2 - 1` is `(1/(NB n2)) sum_j w^(-j s) z^(j)_(s mod n3)`, accumulated over the chunks in coefficient form, only for the wanted window (the first chunk stores, the others load, add and store; a subtraction into an array loads and subtracts). An operand of one block is transformed once and used at every outer point. Appendix G.2 (this package's check) runs this scheme against schoolbook products reduced modulo `X^(n2 HB) - 1`, for windows, a bilinear form of two signed products, and `nc` from 1 to 4.
* Charges of scheme (c) (e6dcb600; Appendix E, `conv_bilin_big`): per product the roots and constants (`w`, `w^nc`, their inverses, `1/(NB n2)` and the radix-3 constants, 6 inversions or exponentiations at `330 + 2,310` each), the block transforms of the one-block operands, and per chunk: the twist and fold of each operand (per coefficient a load, a multiplication by the twist factor except in chunk 0, an addition for a row already started, a store; per piece 10 for the twist factor and the addresses, and the loops; a row with no block is zeroed), one outer transform of `n3` points at `HB` positions per operand of more than one block (`ontt`, 4.2), at each outer point one block transform per operand row, one pointwise pass per product (a write for the first, an addition or subtraction for the others), one inverse block transform per output and its fold (`8 HB` plus the loop), one inverse outer transform per output, and the untwist into the window (a load, the multiplication by the block factor, a store, and for chunks after the first or a subtraction a load and an addition or subtraction, per coefficient). The charges are integers; nothing is averaged.
* Workspace of scheme (c) (e6dcb600). The operands stay in coefficient form for the whole product (every chunk reads them) and the outputs are arrays in coefficient form; besides them the product holds, while a chunk is processed, `max(#operands of more than one block, #outputs)` chunk arrays of `n3 HB` elements, one working array of `NB` elements for each operand and each output, and the twiddle table of `n3` elements. Nothing is kept between products. The chunk count is the smallest power of two with `n3 HB <= cf` (and `n3` of the form `2^a` or `3 * 2^a`), where `cf` is the chunk bound of the kind of product.
* Parameters at r = 20 (this package; constants of the algorithm for this r, chosen by a sweep of the ledger of Appendix E over the chunk bounds of the Newton products and of stage D, minimising `time_log2 + memory_log2_bytes` with the live-set peak as the memory; the arena of section 7 was then found for the chosen values). Chunk bounds: the Newton products of 4.6, step 1, `186,264,514,923,095,703` elements (`0.2500 m`); stage D `96,857,547,760,009,776` elements (`0.1300 m`). Workspace rule: no cap on either kind.
* Choice. For each product the algorithm uses whichever of schemes (a) and (c) has the smaller charge, except where the workspace rule of its kind excludes scheme (a) (when the workspace of scheme (a), the block spectra of its operands and the accumulator, exceeds the cap); the choice is a function of the lengths, the window, the chunk bound and the cap only, and Appendix E evaluates both schemes. (e6dcb600 uses the cheaper scheme with no cap.)
* Stage D, products above one block (e6dcb600). `apply_inv` forms `c = r22 a - r12 b` and `d = r11 b - r21 a`, a bilinear form with two outputs of true lengths `la - h` and `la - h - 1`, by scheme (a) or (c); `a` and `b` stay live for the whole product and `c`, `d` are written into arrays of their own lengths. The matrix product of the half-gcd (`mat_mul`) is the same bilinear form with four outputs, each the sum of two products; the four outputs are allocated first, the arrays of both factors stay live for the product and are freed after it. All other products of stage D, and the products below `3 * 2^32` points, are as in 4.3 and 4.4.
* Placement (this package). Stage C: the rule of 4.6 (*Memory*). Stage D: the rule of 4.4 (*Placement*); the working arrays of a product take the end of the product's outputs.
* Memory. The arena of section 7 is the capacity of the allocator of 4.2 on the allocation sequence of a trial, which Appendix E records (a block is `64 + 32 * slots` bytes rounded up to a multiple of 64): stage C as listed in 4.6 (*Memory*). Stage D: the arrays of the nodes of the half-gcd, with the outputs and workspaces of `apply_inv` and `mat_mul`. The twiddle table is the one of the transform of `3 * 2^32` points (`2^31` elements, `ntt_init(32)`); the block transform of `2^32` points and the inner transform of 4.6 (one row of `2^32` points) use the same table.
* Cost. The charges are those of 4.2 applied to these operations; Appendix E expands stages C and D with these rules.

### 4.6 Stage C in the value domain (bradcush's method, entry 1aa56884; Jbenisek's re-implementation and charges, entry 7b276afd and its siblings; this package's port)

**Credit and what is whose.** Stage C of this package is not the coefficient-domain squaring of 4.3 (Jbenisek's cyclic step) or of e6dcb600 (the block-mode step with `MU` and the quotient, used by this package's coefficient-domain predecessor fe269c23). It is the value-domain powering that bradcush introduced in entry 1aa56884 (r = 21; the entry was judged not_evaluable, for a reason that is not published) and that Jbenisek re-implemented and charged in his row-kernel cost model in entry 7b276afd (r = 20) and its siblings 1ebf2b44, 628641e6, 1b8cd7a6, f4f93349 and 86db9605 (r = 16, 17, 18, 19, 21), all six of which the AI review has accepted (status: in review, not human-accepted, at the time of writing). The procedure, the invariant, the two lemmas, the eight steps and the zero-test argument are theirs; the parameter rule (`h = 2^32`, `K = ceil((m + 1)/h)`, the start monomial `S^v` with `v` the largest power of two below `m` shifted down twice, the convolution lengths the smallest `2^a` or `3 * 2^a` that fit, the group buffer of `2^10` rows) and the kernel charges of the geometric phase, the batch inversion and the tables are Jbenisek's; the text of this section is this package's, written in its own words. The ledger function `powx_vd` of Appendix E is this package's re-implementation from 7b276afd's printed program (read, not run), validated by reproducing the row C asserted by his six value-domain entries (r = 16 to 21) to the operation under his charging conventions (`python3 cd_ledger.py checkvd`), and then evaluated under this package's conventions, which differ from his in two places only: the block products of the set-up (step 1) are those of 4.5 (e6dcb600's blocks of `2^31` coefficients and chunked outer product, at this package's chunk bound) instead of his blocks of `3 * 2^31` coefficients with four chunks; and every allocation and free carries the statistics charge of 64 of 4.2. Every other charge of the stage is his, and the charge table below says which rows coincide.

**Point sets.** Let `h = 2^32` and let `H` be the subgroup of order `h` of `F_p^*`; `p - 1 = 2^32 * 3 * 463 * q1 * q2` with `q1 = 539,204,044,132,271,846,773` prime (Appendix G.3 checks the primality and the factorisation). `H` is generated by `omega = 5^((p-1)/h)`, which has order exactly `h` because 5 is a non-square modulo `p` (`5^((p-1)/2) = -1`, G.3). Put `u_k = 5^k`, `C_k = u_k H` (a coset of `H`) and `n_k = u_k^h = z^k` with `z = 5^h`. Since `z^((p-1)/q1) != 1` (G.3), `q1` divides the order of `z`, so the order of `z` is at least `q1`, far above `2K` at every round count up to 21; hence the `2K` nodes `z^k` (`k < 2K`) are distinct, and the cosets `C_0, ..., C_(2K-1)` are pairwise disjoint (`C_j = C_k` exactly when `z^(j-k) = 1`). In this section `K` is the number of cosets of a point set, not the number of centres of 4.1: `K = ceil((m + 1) / h) = 173,472,348`, and each point set has `n1 = K h = 745,058,061,420,331,008 = m + 1,727,948,196` points, at least `m + 1`. The two sets are `O1 = C_0 u ... u C_(K-1)` and `O2 = C_K u ... u C_(2K-1)`. Let `M(Y) = prod_(k < K) (Y - z^k)` and `P1(X) = M(X^h)`: `P1` has degree `n1`, its root set is exactly `O1` (`X^h = z^k` has the `h` solutions `u_k omega^i`, `i < h`), so it is squarefree, and on a coset `C_k` with `k >= K` it is the nonzero constant `M(n_k)`.

**Representation.** A polynomial `f` of degree below `n1` is determined by its values on `O1`, and also by its values on `O2`. Write `f = sum_(j < h) X^j F_j(X^h)` with `deg F_j < K` (the rows `F_j`: the coefficients `j, j + h, j + 2h, ...`). On `C_k` we have `X^h = n_k`, so `f(u_k omega^i) = sum_j (u_k^j F_j(n_k)) omega^(i j)`: the `h` values of `f` on a coset are the transform of `h` points (one row of the radix-2 passes of 4.2, `a = 32`, in place) of the `h` numbers `u_k^j F_j(n_k)`, and the inverse transform recovers them. A value array holds the cosets one after the other, each in the output order of that inner transform; its `n1` slots are the `K` rows of `h` positions.

**Lemma 4.6 (the squaring step is a Montgomery reduction in the value domain; 1aa56884, restated).** Let `g` be monic of degree `m` with no root in `O1`, let `R~` have degree at most `m`, and let `u0` be the polynomial of degree below `n1` whose value at every `x` in `O1` is `-R~(x)^2 / g(x)`. Then `W = (R~^2 + u0 g) / P1` is a polynomial of degree at most `m - 1`, `W = R~^2 P1^(-1) mod g`, and on a coset `C_k` with `k >= K` its values are `(R~(x)^2 + u0(x) g(x)) / M(n_k)`. *Proof.* `R~^2 + u0 g` vanishes at the `n1` distinct roots of the squarefree `P1`, so `P1` divides it; its degree is at most `max(2m, (n1 - 1) + m) = n1 + m - 1` because `n1 >= m + 1`, so `deg W <= m - 1`. Modulo `g`, `W P1 = R~^2`, and `P1` is invertible modulo `g` since `g` has no root in `O1` and `P1` splits into distinct linear factors with roots in `O1`. On `C_k` (`k >= K`) `P1` is the constant `M(n_k)`. QED. The stage keeps the invariant `R~_i = S^(e_i) P1 mod g` with `deg R~_i <= m`: from `R~_i` it forms `W` and sets `R~_(i+1) = X^b W` (`b` the next exponent bit), so `e_(i+1) = 2 e_i + b` and `deg R~_(i+1) <= m`. The same computation with `R~` in place of `R~^2` (step 7) removes the factor `P1` at the end.

**Lemma 4.7 (extension by a fixed-kernel convolution; 1aa56884, restated).** Let `f` have degree below `n1` and let its values on `O1` be given. The inverse inner transform of the coset `C_k` (`k < K`) gives, at position `j`, the number `h u_k^j F_j(n_k)`. Fix `j`, write `F = F_j` (degree below `K`, known at the `K` nodes `z^i`, `i < K`) and put `s_i = F(z^i) z^(-i) / M'(z^i)` and `kappa(e) = 1 / (z^e - 1)` for `1 <= e <= 2K - 1`. Then `F(z^(K+t)) = M(z^(K+t)) sum_(i < K) s_i kappa(K + t - i)` for `t < K`. *Proof.* `F` is the Lagrange interpolant of its values at the `K` distinct nodes `z^i`: `F(y) = M(y) sum_i F(z^i) / (M'(z^i) (y - z^i))`, and `z^(K+t) - z^i = z^i (z^(K+t-i) - 1)` with `1 <= K + t - i <= 2K - 1`. QED. The sum is the linear convolution of the `K`-term sequence `(s_i)` with the kernel `(kappa(e))`, read at the indices `K, ..., 2K - 1`; one cyclic convolution of length `Lx >= 2K` gives those `K` outputs exactly (the linear convolution is supported on `[1, 3K - 2]`, and an index `e >= K` can only alias with `e + Lx >= 3K`). The forward inner transforms of the cosets `C_(K+t)` (with the factors `u_(K+t)^j`) then give the values of `f` on `O2`. The direction `O2 -> O1` is the same statement with the known nodes `z^(K+i)` and the wanted nodes `z^t`, and with both index sets run in reverse order it uses the same kernel `kappa` (`z^(K-1-t') - z^(2K-1-i') = -z^(K-1-t') (z^(K+t'-i') - 1)`), so one stored kernel spectrum serves both directions. In the ledger the per-row factors (`1/h`, `z^(-i) / M'(z^i)`, `M(z^(K+t))`, and the `u_k^(+-j)` of the inner transforms, which run along a row as geometric sequences) are the running factors of the copies into and out of the group buffer. Appendix G.3 checks both lemmas, and the whole stage below, against direct computation over the Pallas field at toy size.

**The stage (the eight steps of 1aa56884, with Jbenisek's parameters at r = 20).** The exponent is `E = (p - 1)/2`. The powering starts from `S^v` with `v = 2^57`, a power of two below `m` and a multiple of `h`, so that `X^v` is the constant `u_k^v` on every coset (`omega^v = 1`); the leading bit and the next 57 bits of `E` (which are zero) are absorbed by this start, and the loop runs `196` steps, `45` of them with `b = 1`. (`v = 2^59` would be the largest admissible power of two; Jbenisek's `VSHIFT = 2` takes two bits fewer in exchange for a reciprocal four times shorter in step 1; the ledger evaluates the schedule as given.)

1. *Barrett start.* The reciprocal of the reversed `g` modulo `X^ell`, `ell = v + n1 - m + 1 = 144,115,189,803,804,069`, by the Newton iteration of 4.3 with the block products of 4.5 at the chunk bound of the kind `newton` (the reversed top `ell` coefficients of `g`, levels `l -> min(2l, ell)`, each level two products on the Good-Thomas rows or by blocks). Then `q = floor(X^v P1 / g)`, which has `ell` coefficients, as the reversal of `rev(X^v P1) * rev(g)^(-1) mod X^ell`: the top `ell` coefficients of `X^v P1 = X^v M(X^h)` are the `Kq = ceil(ell / h) = 33,554,433` coefficients `mu_i` of `M` at the multiples of `h`, written into a zero-filled array, one product of `ell` by `ell` coefficients (window `[0, ell)`), and the reversal of the result in place.
2. *`g` on `O1` and on `O2`.* The `K` coefficient rows `g_j` (the coefficients `j + h i`, `i < K`; the slots of the array of `g` above `m` are zero) are evaluated at the `2K` nodes `z^k` by the chirp-z method of section 3, one cyclic convolution of length `Le = 2^29 >= 3K - 1` per position with a stored chirp spectrum, then multiplied by the factors `u_k^j` and transformed by `2K` forward inner transforms: `G1 = g` on `O1` in a new array, `G2 = g` on `O2` written in place of the coefficients of `g` (an array of `n1` slots, stage A).
3. *`R~_0` on `O2`.* `q` (its `Kq` rows) is evaluated at the `K` nodes of `O2` (one convolution of length `Lq = 2^28 >= Kq + K - 1` per position) into `R2`, the `K` forward inner transforms follow, and then pointwise `R2 := u_k^v M(n_k) - R2 * G2` (8 operations per element: two loads, a multiplication, a subtraction from the per-coset constant, a store, with the addresses). This is `X^v P1 - q g = X^v P1 mod g` on `O2`, of degree below `m`.
4. *`R~_0` on `O1`.* One extension `O2 -> O1` (lemma 4.7) into `R1`: inverse inner transforms of the `K` cosets of `R2`, the geometric phase, forward inner transforms into `R1`.
5. *`-1/g` on `O1`.* Montgomery's batch inversion coset by coset in place of `G1` (the prefix products into an auxiliary array of `h` elements, one inversion, the backward pass with the negation): 5 and 9 operations per element with the loads and stores, one inversion per coset. The prefix product of a coset is zero exactly when `g` vanishes at a point of the coset; the inversion tests it (2 operations) and a zero ends the trial (next `t`): the *zero test*, whose probability `delta_C` is bounded in 9.2(f) without a premise. The trial has then executed a prefix of the charged work and a prefix of the allocation sequence.
6. *The loop*, for each of the `196` bits `b` below the start: (i) `R1 := R1^2 G1` on `O1`, the values of `u0` (8 per element); (ii) the extension `O1 -> O2` in place of `R1` (`u0` on `O2`); (iii) `R2 := X^b (R2^2 + R1 G2) / M(n_k)` on `O2` (12 per element; 16 when `b = 1`: the point `x = u_k omega^i` is formed from the table of `omega^i` and multiplied in), which by lemma 4.6 is `R~_(i+1)` on `O2`; (iv) the extension `O2 -> O1` from `R2` into `R1`. The invariant `R~ = S^e P1 mod g` holds after every step, and no product of polynomials, no `MU` and no quotient is formed.
7. *Leaving the Montgomery form.* `R1 := R1 G1` (`-R~/g` on `O1`, 7 per element), the extension `O1 -> O2`, `R2 := (R2 + R1 G2) / M(n_k)` (11 per element): by the remark after lemma 4.6 this is `R~ P1^(-1) mod g = S^E mod g` on `O2`, of degree below `m`. `R1` and `G1` are freed.
8. *Coefficient form for stage D.* `R` (in `R2`) and `g` (its array, holding `G2`) are brought back to coefficient form in place: `K` inverse inner transforms each, then the interpolation at the `K` nodes `z^(K+t)` of `O2`, position by position, by the two chirp correlations of length `Lx` of section 3 (the first from the scaled values to the sums `A(i)`, the second with the coefficients of `M2(Y) = prod_(k >= K) (Y - z^k)`), with the `K` intermediate results moved with a per-index constant between them. Stage D (4.4) receives `g` and `R` in these two arrays of `n1` slots; their coefficients above `m` are zero.

The tables, built once per trial: `5,204,170,440` constants (`30 K`: `u_k`, `1/u_k`, the base factors of the row copies, `1/M(n_k)`, `u_k^v M(n_k)`, `1/M'(z^k)`, `M(z^(K+t))`, `1/M2'(z^(K+t))`, `M2(z^t) z^(-t)`, the chirp scales, the coefficients `mu_i` of `M`, and their inverses as needed; each charged as two inversions and 60 operations, which covers the running products that produce them), the table of `omega^i` in transform order (`h` entries, 10 each), and the stored spectra of the fixed kernels (the extension kernel `kappa` on `Lx` points, the chirps of the evaluation of `q` and of the interpolation, the `K + 1` coefficients of `M2(Y) = prod_(k >= K) (Y - z^k)` for the interpolation at the nodes of `O2` (those of `M` scaled by powers of `z^K`), the chirp of the evaluation of `g` on `Le` points; each entry one inversion and 20 operations, then the forward transform). The geometric phase of an extension, of an evaluation or of an interpolation works on groups of `2^10` inner positions: for each group the `K` rows of `2^10` elements are copied (strided, one address operation per element) into a group buffer of `2^10` rows of `Lmax = 536,870,912` elements, multiplied by their running factors (7 operations per element: a load, the multiplication by the factor, the update of the factor, a store and the address; 6 when the factor is a per-row constant), each row is convolved with the stored kernel spectrum (the zero fill of the unused entries, the forward passes, the fused pass with the pointwise product, the inverse passes; for a length `3 * 2^a` the radix-3 input and output stages of 4.3, through a transform row of `Lmax` elements), and the outputs are copied back with their factors; per row 16 (12) operations for the factor and the addresses, per group 20, and the loops by the eight-element rule. The inner transform of a coset is one row of eight radix-2 passes of four layers (4.2), `449,396,745,180` operations forward and `465,144,958,607` inverse, plus 10 per call for the coset address and the arguments.

**Charges** (Appendix E, `powx_vd`, which prints these components; every one of them is a function of `m` and the exponent alone, and none depends on the coefficients):

| component | operations | Jbenisek's 7b276afd |
|---|---:|---:|
| inner transform of one coset (forward / inverse, without the call) | 449,396,745,180 / 465,144,958,607 | the same |
| geometric phase of one extension (468.255 per element of `n1`) | 348,877,404,340,561,752,334 | the same |
| one extension with its `2K` inner transforms | 507,525,101,044,923,415,262 | the same |
| one loop step, `b = 0` / `b = 1` | 1,030,510,156,871,951,482,276 / 1,033,490,389,117,632,806,308 | the same |
| tables: `30 K` constants, the `omega` table, the kernel spectra (inside step 1 below) | 32,271,564,475,855 | the same |
| step 1, the Newton reciprocal (with the plans, the exponent scan, the tables, the allocations of the stage arrays and of the product workspaces) | 1,098,824,565,309,309,832,976 | 1,568,707,512,132,806,089,057 (his blocks and chunks, without the tables and plans) |
| step 1, the product for `q` (the zero fill, the `Kq` coefficients `mu_i`, the product, the reversal, with its allocations) | 404,913,238,801,019,565,628 | 392,153,640,844,941,155,699 |
| step 2, evaluation of `g` at the `2K` nodes (geometric part) | 490,454,522,773,052,174,604 | the same |
| step 2, the `2K` forward inner transforms of `g` | 155,915,817,144,374,846,330 | the same |
| step 3 (evaluation of `q`, `K` inner transforms, the pointwise pass) | 305,448,486,124,727,488,048 | the same |
| step 4 (one extension) | 507,525,101,044,923,415,262 | the same |
| step 5 (batch inversion with the zero test) | 10,989,606,869,988,413,270 | the same |
| step 6, the loop: 196 steps (45 with `b = 1`) | 202,114,101,197,958,150,107,536 | the same |
| step 7 (exit from the Montgomery form) | 521,494,939,704,187,404,978 | the same |
| step 8 (two interpolations) | 1,544,333,801,272,663,531,828 | the same |
| the zero fill of the tail of the last row of `q` (step 3), the allocations of `G1` and of the auxiliary array, the frees, the end of the stage and the stage bookkeeping of 1,000 | 6,096,673,727 | - |
| stage C of one trial (ledger row C) | 207,154,001,277,008,493,454,187 | 207,611,124,658,151,579,699,613 |

The loop is 97.6 percent of the row; the set-up (steps 1 to 5 with the tables) is 1.4 percent. Against 7b276afd's row C (207,611,124,658,151,579,699,613), this package's row is 457,123,381,143,086,245,426 operations lower; the only charges that differ are the two block products of step 1 (the Newton reciprocal and the product for `q`, which here use the scheme (c) of 4.5 with blocks of `2^31` coefficients at the chunk bound of 4.5 instead of his blocks of `3 * 2^31` coefficients with four chunks: the reciprocal is cheaper here and the product for `q` slightly dearer, net lower) and the allocation charge (64 higher per allocation and free than his, 4.2; included in the rows above). The inner transform of a coset is the kernel of the row transforms of 4.2 (`a = 32`), the same kernel that this package's stage B and stage D rows already carry.

**Memory and placement (this package's rule for stage C).** Stage A allocates `g` with `n1` slots at the low end of the pool. Stage C allocates the tables (`30 K + h + sum of the kernel lengths` elements, `368,396,917,056` bytes at this r), the group buffer (`2^10 * Lmax` elements, `17,592,186,044,480` bytes) and, when a kernel length is `3 * 2^a`, the transform row of `Lmax` elements. The tables are below the pool threshold of 4.2 (`2^51` bytes) and come from the slab classes (at r <= 14, where they exceed the threshold, they take the high end of the pool). The group buffer, its transform row and the auxiliary array of `h` elements of step 5 are below the threshold and come from the slab classes (their classes lie within the peaks that stage D sets, so they add nothing to the slab area of section 7). From the low end of the pool it takes, in this order, `R2` and `R1` (`n1` slots each) and in step 2 `G1` (`n1` slots). The Newton phase of step 1 holds, at the high end, three arrays of `ell` elements (the reciprocal, the reversed `g`, a product buffer), then the zero-filled array `Tt` of `ell` elements for the product for `q`, and the workspace of the product in progress (4.5, high end); these are freed at the end of step 1. The loop holds `g` (`G2`), `R2`, `R1`, `G1`: four arrays of `n1` elements, plus the tables and the group buffer, which is the stage C peak of section 7 (4.0000 copies of `m`, the same four arrays as in Jbenisek's value-domain entries, 7b276afd included); the peak of the trial is stage D's. At the exit of the stage `R1`, `G1`, the group buffer, its transform row and the tables are freed, so the high end of the pool is empty and its low end holds `g` and `R` (`R2`) side by side for stage D, which `poly_gcd_own` receives as the operands on the low end (4.4, *Placement*). The twiddle table of `ntt_init(32)` serves the inner transforms (`2^32` points) and every convolution of the geometric phase (`Lx`, `Lq`, `Le` of at most `3 * 2^32` points).

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: operation count, every trial at its maximum (primitive operations; `C(20) = 636`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, the trial loop, the allocator statistics of the unexpanded rows and the reset after an ABORT or a failed zero test; `T_off` = the offline bound of section 6.2. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 2`, and `time_log2 = ceil_5(log2(N_max / 636) + 0.0012)`.

Every stage is charged by the rules of section 4.2 where it executes. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G. The rows other than C and D are Jbenisek's rows at this r (entry 7b276afd, section 6 there; they equal those of the earlier entry 5d6dda61 except for the B row, 186 operations lower), unchanged except for the four rows marked as added.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(32-1)` elements (`ntt_init(32)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 17,179,887,292 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,196 |
| B (per trial) | `115648232` cosets of `6,442,450,944` points, each point with two evaluations of `F` (at `c + s` and `c - s`) at `C(20) = 636` operations each, the loop work around them, `115648232` inverse transforms of size `6,442,450,944`, the geometric solve of the cosets (two correlations of length `268,435,456` per position), the normalisation | 2,534,607,690,146,512,986,054 |
| B, coset-solve workspace (per trial, added) | the allocation and free of the workspace of the geometric solve, now in the allocation walk of stage B (an allowance) | 10,000 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain (section 4.6): the tables, the Barrett start (Newton reciprocal modulo `X^ell` and the product for `q`, block products of 4.5), the evaluations of `g` and `q` at the geometric nodes, the batch inversion with the zero test, `196` squaring steps (45 with `b = 1`), each two pointwise passes and two extensions, the exit and the two interpolations; expanded in Appendix E | 207,154,001,277,008,493,454,187 |
| D (per trial) | half-gcd of `(g, R - 1)` (section 4.4, truncated second call) on the normal remainder sequence, with the test of every quotient degree and of every return (section 6.3); expanded in Appendix E | 207,628,691,374,595,267,697,955 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16` (below) | 166,079,773 |
| F (per trial) | square root, back-map (below) | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 636 + 32` | 13,752 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| allocator statistics, rows A, B, E, F, G (per trial, added, e6dcb600) | the flat 64 of the allocator's statistics (4.2) for at most `10^10` allocator calls in the rows that Appendix E does not expand (rows C and D charge it on every allocation and free) | 640,000,000,000 |
| reset after an ABORT or a failed zero test (per trial, added) | a trial that aborts (stage D) or fails the zero test (stage C) resets the allocator to its state after init (the two ends of the pool, the 35 free-list heads) | 1,000 |
| plan_invN misses | one per distinct plan size (31 sizes) | 95,759 |
| plan_invN misses, second allowance (added, e6dcb600) | the plans of the lean products differ from Jbenisek's; a second allowance of the row above | 95,759 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 2 * T_trial + T_off` | **834,634,600,684,798,065,055,682** |

The rows C and D are not asserted by hand: Appendix E expands them from the coset count and the convolution lengths of 4.6, the block products and chunk counts of 4.5, the Newton levels, the squaring steps and the half-gcd levels with the truncated second call, with the kernel charges of section 4.2, and prints the two values 207,154,001,277,008,493,454,187 and 207,628,691,374,595,267,697,955 (Jbenisek's value-domain entry 7b276afd: 207,611,124,658,151,579,699,613 and 486,614,267,735,446,320,435,327, the latter for every remainder sequence; this package's coefficient-domain predecessor fe269c23: 765,696,884,086,284,137,096,991 and 207,628,691,374,595,267,697,955).

`N_max = 834,634,600,684,798,065,055,682` operations `= 1,312,318,554,535,846,014,238.5` units, `log2(N_max / 636) = 70.1526079575`, claimed as `time_log2 = 70.15381` (0.0012 added, then rounded up at five decimals: a margin of `695,700,991,597,112,623,181` operations).

Stage B charges each of the `1,490,116,122,840,662,016` evaluations of `F` as one reduced permutation, `C(20) = 216 + 21 * 20 = 636` operations, although a line evaluation is a strict subset of the work of a reference permutation; the loop work around the evaluations is charged on top (section 3).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the isolation loop until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 31, the zero test of the shift (5, and at most 2 for the replacement of a zero draw by 1) and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because the memory-access charge adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `2,640` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = 2,594,979`, of which `pow_half` is 2,471,032, the Taylor shift 11,700 and the two gcds 54,395 each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + 64 * R(16) + 114 = 166,079,773`.

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`.

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.1 Ledger recomputation and validation

The sum of section 6 is recomputed by the following script (standard library only).

```python
from math import log2, ceil
K, C = 2, 636
fixed = [17179887292, 4910, 95759, 95759, 5644, 3384436]   # init, setup, plan_invN misses (two allowances), stage H, stage I
trial = [1196, 2534607690146512996054, 207154001277008493454187, 207628691374595267697955, 166079773, 47012, 13752, 12, 640000000000, 1000]   # stages A, B (with the workspace allowance), C, D, E (cap), F, G, trial loop, allocator statistics, reset after an ABORT or a failed zero test
offline = 1000000
N = sum(fixed) + K * sum(trial) + offline
print('N =', format(N, ','))
print('log2(N/C) =', log2(N / C))
print('time_log2 =', '%.5f' % (ceil((log2(N / C) + 0.0012) * 100000 - 1e-6) / 100000))
```

It prints `N = 834,634,600,684,798,065,055,682`, `log2(N/C) = 70.1526079575` and `time_log2 = 70.15381`. Appendix E prints the same `N_max` from the ledger.

Jbenisek's entry compares the same counting rules with the instrumented totals of its executed entries (algorithmic totals; those runs used the earlier programs, not the stages C and D of this package); the table is reproduced as Jbenisek's validation of the charging rules of 4.2:

| run | counted total | measured total | counted - measured | slack (bits) | counted heap peak | measured heap peak |
|---|---:|---:|---:|---:|---:|---:|
| r = 3, earlier program (fixed centre) | 410,937,818,567 | 409,369,056,359 | 1,568,762,208 | 0.00552 | 244,745,792 | 244,745,792 |
| r = 4, earlier program (fixed centre) | 3,993,660,556,174 | 3,977,289,295,772 | 16,371,260,402 | 0.00593 | 1,072,730,560 | 1,072,730,624 |
| r = 5, earlier program (fixed centre) | 9,217,469,769,975 | 9,171,678,989,504 | 45,790,780,471 | 0.00718 | 4,759,669,952 | 4,759,669,952 |

### 6.2 Offline derivation of the literals (preprocessing)

The algorithm uses constants that are derived from the organizer's constants and from `p` offline: the 192 round constants and 9 MDS entries in Montgomery form, `R^2 mod p`, `R mod p`, `2^65` and `5^q` in Montgomery form, the exponents `q`, `(q+1)/2`, `(p-1)/2`, `p - 2` and the integer `e = (4(p-1)+1)/5`. There is no search and no choice: each literal is the value of one closed formula in the organizer's constants. The Montgomery form of a constant `x` is `x * 2^256 mod p`, one modular multiplication plus parsing 64 hexadecimal digits; `5^q` is a square-and-multiply of 221 squarings and at most 221 multiplications; the exponents are shifts and subtractions of `p`. Each literal costs at most 4,000 word operations, there are at most 250 literals: 1,000,000 operations in all. This bound is inside `N_max` and is the declared `preprocessing_log2 = 20` (`2^20 = 1,048,576 >= 1,000,000`). The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

### 6.3 Stage D: the normal remainder sequence, and the abort (e6dcb600)

The text of this section is e6dcb600's (bradcush), restated for r = 20; it replaces Jbenisek's worst-case charge of stage D for every remainder sequence.

The row D is the charge of the half-gcd of section 4.4 on a normal remainder sequence: every quotient of the Euclidean sequence of `(g, R - 1)` has degree 1, from `deg g = m` down to the gcd. (a) *Lengths.* On such a sequence `d_j = j`, every call `hgcd(a, b, k)` of the recursion has the parameter fixed by the recursion (`k1 = ceil(k/2)`, `k3 = k - k1 - 1`), its first call has `2 k1 + 1` coefficients and its second call at most `2 k3 + 1` (lemma 4.4), the reduced pairs have the lengths `deg a - h` and `deg a - h - 1`, and every matrix of a call with parameter `k` has entries of at most `k + 1` coefficients. Every length of the program is therefore a function of `m` alone, and Appendix E evaluates the charge on these shapes exactly (`gcd_cost(m, 0)`, with the gcd of degree 0). (b) *A gcd of positive degree.* When the gcd has degree `d >= 1` the normal sequence ends at a zero remainder after `m - d` divisions. If `d <= 96` that zero remainder occurs in the classical Euclid of `poly_gcd_own` (every `hgcd` call of the top loop stops at a degree of at least 96, its parameter being at most `(n+1)/2` with `n > 192`), so the program executes a prefix of the calls of the degree-0 case, with the same lengths at every executed call (a call whose second operand is zero, or whose remaining parameter is exhausted, returns at its first test). If `d > 96` the zero remainder may instead be met inside an `hgcd` call of the top loop, which then returns a degree count below its parameter, and the trial ABORTs at the return test of its caller (4.4, step (1): the test fires whether or not the remainder is zero) before any `apply_inv` on operands of other than the normal shapes; such a trial could not have succeeded (`d > DMAX`). In both cases the charge is at most row D. (c) *The tests and the abort.* The quotient test and the return test of 4.4 (2 operations each, charged wherever they execute in Appendix E) are passed by every normal sequence. Consider any other sequence and the first point, in execution order, at which a call whose degree count `h` is still below its parameter `k` finds that the next quotient of its own pair has degree other than 1 (a call with `h = k` stops whatever its next quotient is, as on a normal sequence). If that quotient fits the remaining parameter, the call uses it and the quotient test fails at that division. If it does not fit, the call stops early: the base case breaks out of its loop, a node returns at step (3) after its first call and `apply_inv`, which were executed with normal shapes because every quotient before this point had degree 1; the call returns a degree count below its parameter, and the return test of its caller fails (zero remainder or not, 4.4 step (1)) before the caller does anything with the result; in particular no `apply_inv` is ever executed on operands of other than the normal shapes. In both cases the trial ends having executed only operations that the normal sequence also executes, with the same lengths (lemma 4.4: until that point the truncated calls see the quotients of the whole pair). Hence row D bounds stage D for every input, and the abort affects only the success probability, through the premise `H-NORMAL` (9.2(g), 9.5). (d) *Memory.* The same argument applies to the allocations: an aborted trial executes a prefix of the allocation sequence of the normal one (and then frees its live arrays before the next trial, at most the charge of the frees of the normal sequence), so the arena of section 7, found on the normal sequence, serves every trial. Jbenisek's entry instead charged stage D for every remainder sequence (1,640,086,107,769,334,539,824,888 operations at this r); this package does not need that bound.

## 7. Memory

Three terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 399,216 bytes of code, 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages), Jbenisek's figure, plus an allowance of 65,536 bytes for the code of the outer-transform kernels and of the one-row block transform: 5,315,980 bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is the capacity of the allocator of 4.2 on the allocation sequence of one trial, found by simulation, not the peak of the live set. Appendix E records every allocation and free of a trial in the order of the program (the twiddle table; stage A: `g`, an array of `n1` slots (4.6); stage B: the coset array and the coset-solve workspace; stage C: the tables, the group buffer and its transform row, `R2`, `R1`, the three Newton arrays and the workspace of each product, `Tt`, `G1`, the batch-inversion array; stage D) and runs the allocator on it: the two-ended pool takes the blocks of more than `2^51` bytes and is simulated address by address, block by block (two lists in address order, from the two ends; the first free block that fits on the request's side, cut on the side nearest its end; a free merges with its free neighbours and with the unused middle); the slab classes take the other blocks, and their area is the sum over the classes of the peak number of live blocks of the class times the slot. The calls of the half-gcd on fewer than `2^45` coefficients are evaluated once per shape and summarised by their slab-class counts (net and peak), after Appendix E checks that they allocate no pool block; every larger call, and every array of stages A to C, is placed individually. The simulation checks that a trial returns the allocator to its state after init, so the second trial repeats the first; after an ABORT the program resets the allocator to that state (section 6).

Results at r = 20: the high-water mark of the pool (the largest sum of the extents of its two ends) is `121,123,418,761,573,974,208` bytes (after stage A `23,841,857,965,450,592,320`, after stage B `47,683,715,930,901,184,640`, after stage C `95,367,431,861,802,369,280`, after stage D `121,123,418,761,573,974,208`); the peak of the live set is `121,123,419,930,878,821,184` bytes (stage A `23,841,858,034,170,069,120`, B `47,683,716,045,082,630,144`, C `95,367,450,045,723,630,400`, D `121,123,419,930,878,821,184`; in units of `32 m` bytes, one copy of a polynomial of `m` coefficients: 1.0000, 2.0000, 4.0000, 5.0803), so the pool is `1.000000` times the live-set peak. The peak of stage C is the loop of 4.6 (`g`, `R2`, `R1`, `G1`, four arrays of `n1` elements, with the tables and the group buffer; Jbenisek's entry 7b276afd has the same stage C peak), and the peak of the trial is stage D's, where this package's coefficient-domain predecessor fe269c23 peaked in stage C (5.2901 copies). The slab area is `72,051,959,040,829,312` bytes; stages E to I hold at most 16 live arrays of at most 17 elements and the allocator keeps 36 words, `16,896` bytes. The arena is the pool plus 128 bytes (so that the unused middle is always at least 128 bytes), the slab area and those `16,896` bytes, rounded up to 64: `121,195,470,720,614,820,544` bytes.

With the end rules of 4.4 and 4.6 the pool has no hole at the moment of its largest demand (it is below the live-set peak because the twiddle table is a slab block). An aborted trial, and a trial that fails the zero test of 4.6, executes a prefix of the allocation sequence of the normal one, so the arena serves it too (6.3 (d)).

(c) A stack bound of 65,536 bytes.

Total: (a) + (b) + (c) = `121,195,470,720,620,202,060` bytes `= 2^66.71590`, which rounds up at three decimals to 66.716; claimed as `memory_log2_bytes = 66.718` (0.002 added: `2^66.718 = 121,372,207,447,549,312,974` bytes, `176,736,726,929,110,914` bytes above the total); Jbenisek's value-domain entry 7b276afd claims 66.990 (its arena is set by its worst-case stage D walk, 6.15 copies of `m`) and this package's coefficient-domain predecessor fe269c23 66.777. The memory penalty is `max(0, 66.718 - 20) = 46.718`. The offline derivation of section 6.2 is a closed formula per constant; its memory is bounded by 1,024 bytes, inside the figure above. The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init".

## 8. What is provided

* The algebraic derivation (sections 2-3), the algorithm and its charges (4, 6, 7), the truncation lemma 4.4 and the value-domain lemmas 4.6 and 4.7 with proofs, the bound on the zero test of stage C (9.2(f)), the premises with the reduction to explicit constants (section 9), the isolation lemma with proof (9.4), and the evidence, labelled as evidence (section 10).
* The claim is the operation count of the algorithm (every trial at its maximum), `memory_log2_bytes` its footprint (the allocator's arena, section 7), and a success probability that follows from the two premises. The cost claim is in the model of section 4.2.
* The ledger of stages C and D with the allocator simulation (Appendix E, this package's program, which also reproduces the row C of Jbenisek's six value-domain entries and the totals of e6dcb600 as validation), the small-size checks of Appendix G.2 and the checks of the value-domain stage of Appendix G.3, standard library only. No certificates (the certificate manifest is empty); the experiments are Jbenisek's organizer experiments for this target (10.2), unchanged.

## 9. Success probability and the premise `H-GEOM-w1` and `H-NORMAL`

### 9.1 The premise

Notation. `p` is the Pallas prime, `D = 5^26`, and `F` is the fixed polynomial of section 2.3 at r = 20 (degree `D`, leading coefficient `f_D(0) != 0`). Put
`G(c, t) = (F(c + t) - F(c - t)) / (2 t)` in `F_p[c, t]`, a polynomial of total degree `D - 1` (section 3: `G(c, t) = g_c(t^2)`). For `c` in `F_p` let `k(c)` be the number of nonzero squares `S = t^2` with `G(c, t) = 0`; this is `deg G_c` of section 3. Let `O` be the set of triples `(c, s_1, s_2)` with `G(c, s_1) = G(c, s_2) = 0`, `s_1^2 != s_2^2` and `s_1 s_2 != 0`; `N_off = #O(F_p)`, and `w` is the main-term constant of its count (for a curve with `w` absolutely irreducible components over `F_p`, `N_off ~ w p`).

**Premise `H-GEOM-w1`.** Let `N*` be the number of points `(c, t)` of `G = 0` over `F_p` with `t != 0`, and `N_off` the number of points `(c, s_1, s_2)` over `F_p` with `G(c, s_1) = G(c, s_2) = 0`, `s_1^2 != s_2^2` and `s_1 s_2 != 0`. Then `N* / p >= 1 - eps` and `N_off / p <= w (1 + eps)`, with `w = 1` and `eps = 0.21`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r20-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2), the polynomial `F` of section 2.3; centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:** it concerns this `F`, not every polynomial of degree `D`: it is false for permutation polynomials, in particular for every pure composition of maps `x -> a x^5 + b` (`p = 2 mod 5`, so those maps are bijective), and it is not implied by a statement about components over the algebraic closure alone (`F(X) = X^3` over `F_101`: `(F(X) - F(Y)) / (X - Y)` splits into two conjugate lines over `F_(101^2)`, the curve has no off-diagonal rational point, and `k` is zero for every `c`). The explicit constants of 9.2 apply for every r >= 13 as stated, with no genus bound: the Weil majorant of the second moment (Grok job 138) exceeds the main term from r = 13, so the premise is stated as the count statement itself, which Grok job 139 measures on toy copies (10.3).

What the premise does not contain: no random-polynomial model, no independence of different centres (they are independent because each draw uses distinct fresh random words), no statement about the number of roots beyond the two moments of 9.2.

### 9.2 The reduction to explicit constants, and the success bound

For `c` uniform in `F_p` write `E[.]` for the mean over `c`.

(a) *Squares.* For `t != 0` the values `t` and `-t` give the same `S = t^2` and different points `(c, t)`, so `E[k] = N* / (2p)` with `N* = #{ (c, t) : t != 0, G(c, t) = 0 }`.

(b) *First moment.* By the premise `N* >= (1 - eps) p`, so `E[k] = N* / (2p) >= 1/2 - e_1` with `e_1 = eps / 2`; `e_1 <= 1.050e-01` at r = 20. No genus bound is used.

(c) *Second moment.* `k(k-1)` counts ordered pairs of distinct usable squares; each pair lifts to 4 points `(s_1, s_2)` by independent signs, and `s_1^2 != s_2^2`, `s_1 s_2 != 0` define `O`. So `E[k(k-1)] = N_off / (4p) <= w (1 + eps) / 4 = w/4 + e_2` with `e_2 = w eps / 4`; `e_2 <= 5.250e-02` at r = 20. (The bound of the premise has the form of the weakest count statement that keeps the success bound at 0.39: Grok job 138, `N*^2 >= q_* p (2 N* + N_off)`; the relative form used here, with one `eps` on both counts, is a sufficient condition for it.)

(d) *Cauchy-Schwarz.* `(E[k])^2 = (E[k 1_(k >= 1)])^2 <= E[k^2] P(k >= 1)` and `E[k^2] = E[k] + E[k(k-1)]`, so `P(k >= 1) >= a^2 / (a + b)` with `a = E[k]` and `b = E[k(k-1)]`. The right side increases in `a` and decreases in `b`, so its minimum over `a >= 1/2 - e_1`, `b <= w/4 + e_2` is at the corner: `P(k >= 1) >= (1/2 - e_1)^2 / (1/2 - e_1 + w/4 + e_2) = 0.2236917563`.

(e) *The cap `DMAX`.* `k >= DMAX + 1` implies `k(k-1) >= (DMAX+1) DMAX = 272`, so by Markov `P(k > DMAX) <= (w/4 + e_2) / 272 = 0.0011121324`. Therefore, for `c` uniform, the event `E_c : 1 <= k(c) <= DMAX` has probability at least `q = 0.2236917563 - 0.0011121324 = 0.2225796239`; Jbenisek's entry uses `q = 0.22257`, and this entry uses the larger bound of (e').

(e') *A sharper bound from the same two moments (this package).* For every integer `k >= 0`, `1_(1 <= k <= DMAX) >= k - k(k-1)/2`: the right side is 0, 1, 1, 0 at `k = 0, 1, 2, 3` and negative for `k >= 4`, while the left side is 0 or 1 and equals 1 at `k = 1, 2, 3`. Taking means over `c`, `P(1 <= k <= DMAX) >= E[k] - E[k(k-1)]/2 >= (1/2 - e_1) - (w/4 + e_2)/2 = 3/8 - 5 eps/8 = 0.24375` (`w = 1`, `eps = 0.21`), which is larger than the `0.2225796239` of (d)-(e) and needs no separate tail term, because the right side is already nonpositive beyond `k = 3`. The entry therefore uses `q = 0.24375`; (d) and (e) are kept as Jbenisek's original derivation. Two moments alone cannot give more than `0.24375` for one centre: the distribution `P(k = 0) = 121/160`, `P(k = 1) = 37/400`, `P(k = 2) = 121/800` has `E[k] = 0.395` and `E[k(k-1)] = 0.3025` exactly and attains it. So `K = 2` centres remain necessary and the time bound is unchanged. For `w >= 2` the Cauchy-Schwarz bound of (d)-(e) is the larger of the two, and the script of Appendix D takes the larger one in its sensitivity table.

(f) *Centres, isolation and the zero test of stage C.* The algorithm draws its centres `c_1, ..., c_K` from fresh random words by the rule of 4.1.1; each is within statistical distance `eps_coin < 2^-128` of uniform (the exact value is 1.574e-39 (2^-128.90)), and the draws are independent. Let `Z_c` be the event that `g_c` vanishes at a point of the set `O1` of 4.6, which ends the trial at the batch inversion (4.6, step 5). Write `G(c, t) = g(c, t^2)` with `g(c, x)` in `F_p[c, x]` (section 3: `g_c(x) = g(c, x)`). In `(c + t)^D - (c - t)^D = 2 sum_(i odd) C(D, i) c^(D-i) t^i`, dividing by `2 t` leaves `D c^(D-1)` as the only term of degree `D - 1` in `c`, and every term of `F` of degree below `D` contributes degree below `D - 1` in `c`; so the coefficient of `c^(D-1)` in `g(c, x)` is the constant `D f_D(0)`, nonzero because `D = 5^26 < p` and `f_D(0) != 0` (2.3). Hence for every `x` in `F_p` (square or not) `g(c, x)` is a polynomial in `c` of degree exactly `D - 1` and has at most `D - 1` roots `c`; the draw gives every residue probability at most `4 / 2^256` (4.1.1), so `P(Z_c) <= delta_C = 4 n1 (D - 1) / 2^256 = 3.835e-41 (2^-134.26)` with `n1 = 745,058,061,420,331,008`, without a premise (the argument of bradcush's entry 1aa56884 and of Jbenisek's 7b276afd, restated). If `E_(c_t)` holds, the isolation of stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48` over words that are fresh for that stage (lemma 9.4). A trial with `E_(c_t)`, not `Z_(c_t)`, and a successful isolation ends in a verified collision (sections 2-5). The three error terms `eps_coin`, `eps_iso` and `delta_C` are together below `10^-14` and do not move the ninth decimal of the bounds below. Therefore

`P[no collision in K trials] <= (1 - q)^K + K (eps_coin + eps_iso + delta_C)`,

and, given the premise,

`P[success] >= 1 - (1 - q)^K - K (eps_coin + eps_iso + delta_C) = 0.428085937`, with `q = 0.24375` from (e'), `K = 2`, `w = 1` (before the `H-NORMAL` allowance `delta` of (g), which gives the claimed 0.41286).

The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 20 enters it. The arithmetic of (b)-(f) is recomputed with exact rationals by the script of Appendix D, which prints every number used here. With Jbenisek's `q = 0.22257` from (d)-(e) the same arithmetic gives 0.395602595, the value claimed by the base entry.

(g) *The ABORT of stage D and `H-NORMAL` (e6dcb600's addition).* For a centre `c` let `N_c` be the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd (every quotient of degree 1, section 6.3); by the premise `H-NORMAL` (9.5), `P(not N_c) <= delta = 0.01` for `c` uniform. If `N_(c_t)` holds, stage D runs without ABORT and returns `G = gcd(g_c, R - 1)`; a trial with `E_(c_t)`, `N_(c_t)` and a successful isolation ends in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so the bound of (f) becomes `P[success] >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + delta_C) = 0.412860937 >= 0.41286` (`q = 0.24375`, `delta = 0.01`, `K = 2`, computed with exact rationals by this package, Appendix D; with `delta = 0` the bound is 0.428085937). It stays at least 0.39 for every `delta <= 0.0247`.

### 9.3 The parameter w

With the count premise and `w = 1`: the worst corner `N*/p = 1 - eps`, `N_off/p = 1 + eps` gives `q(eps) = (1 - eps)^2 / (3 - eps)` for the Cauchy-Schwarz ratio, decreasing in `eps`; `q(eps) >= 0.22369` at `eps = 0.21`. Without the cap tail the largest `eps` with `1 - (1 - q)^2 >= 0.39` is 0.2197 (Grok job 138; 0.3676 for three centres), and with the tail of 9.2(e) it is 0.2146; with the linear bound of 9.2(e'), `q(eps) = 3/8 - 5 eps/8`, it is 0.2496. The smallest good fraction `q'` (the probability of `E_c`) for which `K` centres give 0.39 is 0.39000 for K=1, 0.21898 for K=2, 0.15191 for K=3 and 0.11625 for K=4 (the terms `K (eps_coin + eps_iso)` are below `10^-14`); with the submitted `K = 2` the good fraction can be smaller than `q = 0.24375` by the factor `0.898` (down to `q' = 0.21898`) before the bound falls below 0.39. The time bound is `T_fixed + K T_trial` with `T_fixed` much smaller than `T_trial`, so `K'` centres instead of `K` cost about `log2(K'/K)` more in `time_log2`.

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - S3)/2^256 = 1/2 - 7.869e-40` (`S3` of 4.1.1) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `S3` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - S3)/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`, computed exactly in Appendix D. This is a proved bound under the random words, not a premise and not a sample.

### 9.5 The premise `H-NORMAL` (e6dcb600's premise, restated at r = 20)

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 745,058,059,692,382,812`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.01` (`2^-6.64`).

Four fields (as in claim.json). **Role:** score-critical for the success probability only: the time and memory bounds hold for every sequence, because an abnormal sequence ends the trial at its first abnormal quotient after a prefix of the charged work (6.3). **Scope:** the pairs `(g_c, R_c - 1)` of this target at r = 20, `c` uniform; nothing is claimed for other round counts. **Extrapolation and evidence:** for a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-134`. That bound does not transfer directly, because the coefficients of `R_c` are polynomials of degree about `p` in those of `g_c`; the premise asserts much less than random-pair behaviour: an abnormality probability of at most `delta = 0.01`, which is all the success bound uses (9.2(g): every `delta <= 0.0247` keeps it above 0.39). Measured support, organizer-executed (this package, section 10.5.1): the experiments `euclid-normal-d25-n256`, `euclid-normal-d125-n32` and `euclid-normal-d625-n2` compute in the organizer's sandbox the complete Euclidean remainder sequence of `(g_c, R_c - 1)` for the same construction on the first 4, 5 and 6 rounds of the permutation (degrees 25, 125 and 625; `m = 12`, `62` and `312`) at 256, 32 and 2 fresh centres from the organizer's seeds, and return a witness pair for a trial exactly when its sequence is normal; the prediction is that every computed sequence is normal (our local runs of the same program: 256, 40 and 3 sequences, no quotient of degree other than 1). Reported by Jbenisek's entry (not organizer-executed, section 10.5): the complete sequences on the sibling targets with `r' = 0` and `r' = 1` partial rounds, every quotient of degree 1 in all 10 runs (8 runs of 7,811 steps and 2 of 39,061 steps, 140,610 quotients in all). **Limitations:** not verified at r = 20, which would need the computation itself; a structural reason for a quotient of degree above 1 (an algebraic relation between `g_c` and `R_c` that forces a principal subresultant coefficient to vanish for many centres) would invalidate it, and none is known. The success bound of 9.2 stays at least 0.39 for every `delta <= 0.0247`, above the stated `delta = 0.01`. The organizer-executed tests are at degrees up to 625, far below `m`: they test the construction, not its scale, and the premise at this `r` remains a premise.

## 10. Evidence

This section is the evidence for the premise `H-GEOM-w1` and for the digest of the target. The executions of 10.1, the computations of 10.3 and the runs of 10.5 are reported by Jbenisek's entry 5d6dda61; neither this package nor the organizer executed them, so they motivate the premises without being verified execution evidence. The experiments of 10.2 and 10.5.1 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.1 Executed full-scale outcomes at r = 3, 4, 5

| run | degree of F | m | centres tried (in order) | outcome per centre (`deg G`) | successes | operations N (executed) | time_log2 | memory (bytes) | threads, wall |
|---|---:|---:|---|---|---:|---:|---:|---:|---|
| r = 3, earlier program | 5^9 | 976,562 | 1 (fixed) | c=1: 1 | 1 | 317,054,280,703 | 30.08182 | 250,386,180 | 1 thread, 3,202.9 s |
| r = 4, earlier program | 5^10 | 4,882,812 | 1, 2 (fixed) | c=1: 0 (no usable root); c=2: 1 | 1 | 3,992,419,235,666 | 33.63159 | 1,231,371,140 | 6 threads, 13,030.2 s |
| r = 5, earlier program | 5^11 | 24,414,062 | 1 (fixed) | c=1: 1 | 1 | 9,205,778,231,873 | 34.73925 | 5,604,188,884 | 13 threads, 22,048.3 s |

These are the executed entries of the same construction with the centres 1, 2, ... in place of coin draws (their operation counts are the instrumented totals of those runs, thread charges included). Usable roots appeared at three of the four centres tried; each run stops at its first success.

The collisions found (each is a pair of distinct canonical `(nk, rho)` with equal digests at its own round count, accepted by the organizer's digest function when the entry was filed):
* r = 3 (centre 1):
  * nk1  = 0x0499f5c4354bafa11ca451e656d380d078444ed6561d6355487453741e1a6815
  * rho1 = 0x21625d728b86cf0865d7ad7cd99a0c20464939e5253940d95b3a639d7a909af7
  * nk2  = 0x1009050c8c1414cf5975db612457a2e49b06db64fce28c7dd5ad52ed8fc2c567
  * rho2 = 0x31611cd777dc6c418e048d96a497f46fa51523b47dbadcd97d0ad171160fcdb8
  * digest (field element) = 0x325165c946fe20c28af82e940ec89fca03e6fb74afa1a3fa28a54e552a1f12ec, as the organizer's 32 little-endian bytes `ec121f2a554ea528faa3a1af74fbe603ca9fc80e942ef88ac220fe46c9655132`
* r = 4 (centre 2):
  * nk1  = 0x25c10b7d8d36b332b4a4ddb92f1f1a3ffa40259b7b77b0ba458ad0be367ab979
  * rho1 = 0x2e568f6667ceaedd4195dbd24a55c365075306af4a5d0931b1707ba0bf7616ea
  * nk2  = 0x2acbf624301319ca0830c5fda78ae08e00d75798f24adf1320401f1a3bc4c580
  * rho2 = 0x162fa98e63ff13622228cd9e3b4d9039124a918f1f11d12718a2a782ed69fb17
  * digest (field element) = 0x3deca6a0b865e914ebcc74484b3cedb56b9f6293338881693e00cbee0c161fa1, as the organizer's 32 little-endian bytes `a11f160ceecb003e6981883393629f6bb5ed3c4b4874cceb14e965b8a0a6ec3d`
* r = 5 (centre 1):
  * nk1  = 0x35aefd661e07cec063071e6f92f2bbcfd6bbc794bc99be91c008fed0a2a5ebb5
  * rho1 = 0x3dd4caae629bb08efa85dd470f72f2fc183cf026de9cd1aa356e147f058a0090
  * nk2  = 0x242b99e697375e309d54e5db54c215cb6526b420e7ff760eec690a5fb189c764
  * rho2 = 0x2e9a4cf95fce4bbf8ebe8eb72485446ceca86268a6c2305f70d4460179334e37
  * digest (field element) = 0x2425532a0c6af3e7c0864ce59d3b1ddbd62ea79ba594c3305f8fbacf7c184249, as the organizer's 32 little-endian bytes `4942187ccfba8f5f30c394a59ba72ed6db1d3b9de54c86c0e7f36a0c2a532524`

### 10.2 The organizer experiments declared in `experiments/manifest.json`

Five experiments of kind `python-message-pairs-v1`, run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The two Python sources are 32,902 bytes together (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r20-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run, when the organizer executes it, records the observed count; the prediction is 256 of 256 trials (every trial returns a pair). Jbenisek's entry 5d6dda61 reports a local run of the same events with 256 of 256 trials; this package executed nothing.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 20: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining twenty-six rounds applied to `alpha + beta W` (`deg F = 5^26`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-GEOM-w1` is about (a root of `g_c`). In the picture of the premise, `F(c+s) - F(c-s) = 2 s g_c(s^2)` takes random-function values in `s` at these widths, so a trial returns a pair with probability `1-(1-2^-w)^150`: 0.9058, 0.4441, 0.1363 and 0.0360, that is about 232, 114, 35 and 9 of the 256 trials for `w` = 6, 8, 10, 12. A clustering of the roots of `g_c`, or a bias of the odd structure, would move these counts.

The intake report of the organizer's run records the observed counts of the 256 trials when the organizer executes them (this package executed nothing) with a verified pair for `w` = 6, 8, 10, 12 respectively, and byte-identical output on repetition. 

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-GEOM-w1` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.


**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B (program `certify.py` of job 136, printed in Appendix F). Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the attack's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 26`; the line and the first layers do not depend on r). The results (`certify_dep.py`, Appendix F):

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the attack line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-GEOM-w1` states `w = 1` at `N = 26`; this is the measured trend of the premise (`w = 1` at `N = 1, 2, 3` on the deployed constants, below), and it is our theory that the trend continues to `N = 26`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the attack's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend, and the premise states w = 1 at N = 26: this is our theory, the measured w = 1 at N = 1, 2, 3 continues, and the lemma gives w = 1 or w = 2 given (a) and 2-transitivity.

**Grok job 139 (the counts of the premise on toy copies).** Grok (xAI) computed `N*` and `N_off` exactly for width-3 Hades toy permutations over prime fields `p < 2^22` with `p mod 5 != 1` (S-box `x -> x^5`, uniformly random MDS matrix and round constants, the line `(L, 2L+1, 3L+5)`, `N` full rounds and `k` partial rounds, `deg F = 5^(N+k)` up to 1,953,125), by the fibre counts `N* = sum_y m_y (m_y - 1)` and `N_off = sum_c 4 r(c) (r(c) - 1)` (checked against brute force on the small cases), on 1,316 generic seeds with `p >= 1024` (the five degenerate seeds, where the degree drops, are excluded). The relative error `eps_obs = max(|N*/p - 1|, |N_off/p - w|/w)` with `w = 1` is `<= 0.2197` for every generic seed with `p >= 2053`, and the least-squares fit is `eps_obs = 3.10 / sqrt(p)` for a typical seed (`5.17 / sqrt(p)` for the maximum of four seeds), with no dependence on the degree (adding a term linear in `deg F` moves `R^2` from 0.5508 to 0.5509; the mean of `eps sqrt(p)` is 2.3 to 3.7 for every degree from 5 to 1,953,125); at `p = 2,097,169` the largest generic `eps_obs` is 0.0068. The premise of 9.1 states `eps = 0.21` for the target; this is our theory: the trend `eps ~ 3 / sqrt(p)` continues to `p` of 254 bits (where it is about `2^-126`) and to the polynomial `F` of this target, with the number of components `w = 1` of 10.3 above. The count statement is a sufficient condition for the success bound of 9.2 (Grok job 138).

### 10.4 Scope

One trial at r = 20 needs about 121195470720 GB of memory (section 7) and about 4.2e+23 operations (section 6). The claim is the premise `H-GEOM-w1` with the reduction of section 9.2; the executed centres at r = 3, 4, 5, the experiments of 10.2, the theorems and computations of 10.3 and the measurements of 10.5 are the evidence for it.
### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 20` applies the Euclidean algorithm to `g_c` (degree `m = 745,058,059,692,382,812`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. This section is the measured support of the premise `H-NORMAL` (9.5): stage D is charged for the normal remainder sequence, and a trial ABORTs at the first quotient of degree other than 1 (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (`sib_euclid.py`, centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at degree 0 after `m - 1` steps (7,811 and 39,061 steps; no run had a quotient of degree other than 1), and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core. The program `sib_euclid.py` is printed in Appendix F.

At `r = 20` the stages need about 121195470720 GB and 8.3e+23 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7, and `H-NORMAL` at this `r` is a premise.

### 10.5.1 Organizer-run normality tests (this package; declared, executed by the organizer's runner at evaluation)

Three experiments of kind `python-message-pairs-v1`, declared in `experiments/manifest.json` and run by the organizer's runner (program `experiments/exp_normal.py`, 22,310 bytes; the three sources together are 55,212 bytes, under the 65,536 limit). For each organizer trial the program takes a centre `c` from the trial seed, builds symbolically the digest polynomial `F_k(W)` of the first `4 + k` rounds of the selected permutation on the attack's line (full rounds 0-3 and partial rounds `4..3+k`, coordinate 0; the same constants, MDS and line `j = 0` as section 2, with no final full rounds so that the degree `5^(2+k)` stays small), its monic odd part `g_c` about `c` (degree `m = (5^(2+k) - 1)/2`), `R_c = x^((p-1)/2) mod g_c` and the complete Euclidean remainder sequence of `(g_c, R_c - 1)`, all exactly over `F_p` with the standard library (products by Kronecker substitution, a Newton inverse and Barrett reduction). The sequence is normal when every quotient has degree 1 down to the gcd (4.4, 6.3). When it is normal the program returns two distinct canonical messages of the selected target whose digests agree on the declared 6-bit mask, found by a short search of the points `c + s` on the line (the witness that the trial was computed and found normal); when a quotient of degree other than 1 occurs it returns two nulls. The mask event is the witness channel; the measurement is the normality check, whose counts (`steps`, `abnormal_quotients`, `gcd_degree`) the program reports as observations, which the runner labels untrusted. The experiment id fixes the degree and the number of leading trials computed (the sandbox allows 20 s for the 256 trials of an experiment): `euclid-normal-d25-n256` (`k = 0`, degree 25, `m = 12`, all 256 trials), `euclid-normal-d125-n32` (`k = 1`, degree 125, `m = 62`, trials 0-31) and `euclid-normal-d625-n2` (`k = 2`, degree 625, `m = 312`, trials 0-1); the remaining trials return two nulls, so the predicted counts of returned pairs are 256, 32 and 2 of 256. Prediction: every computed sequence is normal. Our local runs of the same program (a Python 3.12 container with one CPU and 128 MiB, seeds of our own): 256, 40 and 3 sequences at `m = 12`, `62` and `312`, no quotient of degree other than 1, in 6.0, 9.1 and 7.3 seconds; the gcd had positive degree in 91, 20 and 2 of them (a usable root of `g_c`, as `E[k]` about `1/2` in 9.2 predicts), and every returned pair was checked against the organizer's reference digest. What these tests show: under trusted execution, the construction's pairs `(g_c, R_c - 1)` have normal remainder sequences at degrees 12 to 312. What they do not show: anything at degree `m = 745,058,059,692,382,812`, where `H-NORMAL` (9.5) remains a premise, now asserting only `delta = 0.01`. The sibling-target runs of 10.5 at `m = 7,812` and `39,062` are Jbenisek's reported computations (entry 5d6dda61), not executed here or by the organizer.

## 11. Appendix D: the premise arithmetic (`premise_numbers.py`)

`python3 premise_numbers.py` recomputes with exact rationals every number of section 9.2 and 9.3, the zero-test term `delta_C` of 9.2(f) included. It prints:

```
D = 5^26 = 1490116119384765625, d = D - 1
e1 < 1.050e-01
e2 < 0.0525000000
E[k] >= 1/2 - e1; E[k(k-1)] <= w/4 + e2 = 0.3025000000  (w = 1)
Cauchy-Schwarz: P(k >= 1) >= 0.2236917563
Markov tail:    P(k > 16)  <= 0.0011121324
Cauchy-Schwarz minus tail (Jbenisek): q >= 0.2225796239, K=2 success 0.395617558855
q = P(1 <= k <= 16) >= E[k] - E[k(k-1)]/2 = 0.2437500000  (linear bound, used by this entry)
K = 2 without the tail (P(k >= 1) only): 0.3973455107
per-round good probability w >= 0.50000000000000000000 = 1/2 - 7.869e-40
eps_iso < 2.371e-15 (2^-48.58)   eps_coin < 1.574e-39 (2^-128.90)   delta_C = 4 n1 (D-1) / 2^256 = 3.835e-41 (2^-134.26), n1 = 745058061420331008
success with delta = 0 >= 1 - (1-q)^2 - 2 (eps_coin + eps_iso + delta_C) = 0.428085937500
success >= 1 - (1-q+delta)^2 - 2 (eps_coin + eps_iso + delta_C) = 0.412860937500   (delta = 0.0100, H-NORMAL)
claimed success_probability: 0.41286 (floor at 5 decimals)
w = 1: P(k>=1) >= 0.22369176, q >= 0.24375000, K=2 success 0.41286094, K=3 success 0.55010469
w = 2: P(k>=1) >= 0.15602500, q >= 0.15380074, K=2 success 0.26692282, K=3 success 0.37233986
w = 3: P(k>=1) >= 0.11978887, q >= 0.11645247, K=2 success 0.20157281, K=3 success 0.28656736
```

#### premise_numbers.py

```python
#!/usr/bin/env python3
"""Exact-rational recomputation of the success bound of proof.md section 9 for r = 20 (standard library only; prints every number used).
Premise H-GEOM-w gives E[k] >= 1/2 - e1 and E[k(k-1)] <= w/4 + e2 (Weil's bound replaced by the count premise of section 9.1; section 9.2).
Cauchy-Schwarz: P(k >= 1) >= E[k]^2 / (E[k] + E[k(k-1)]).  Markov on k(k-1): P(k >= DMAX+1) <= E[k(k-1)] / ((DMAX+1) DMAX).
Linear bound (9.2(e')): P(1 <= k <= DMAX) >= E[k] - E[k(k-1)]/2, from 1_(1<=k<=DMAX) >= k - k(k-1)/2 for every integer k >= 0; this is the q the entry uses.
q = P(1 <= k <= DMAX) >= the difference; K independent centres: 1 - (1-q)^K - K (eps_coin + eps_iso + delta_C), delta_C the zero test of stage C (9.2(f))."""
import math
from fractions import Fraction as Fr
from math import comb
P = (1 << 254) + 0x224698FC094CF91B992D30ED00000001
SP = 1 << 127                                   # floor(sqrt(P)) = 2^127, (2^127 + 1)^2 > P
R, DMAX, ZCAP = 20, 16, 64
DELTA = Fr(1, 100)   # the H-NORMAL abnormality allowance (section 9.5)
D = 5 ** (6 + R); d = D - 1
N1 = -(-((D - 1) // 2 + 1) // (1 << 32)) * (1 << 32)   # the points of the set O1 of stage C (4.6): K h with K = ceil((m + 1)/h), h = 2^32
DELTA_C = Fr(4 * N1 * (D - 1), 1 << 256)              # the zero test of stage C (9.2(f)): at most D - 1 bad centres per point, each of probability <= 4/2^256
# first moment: the count premise N*/p >= 1 - eps gives E[k] = N*/(2p) >= (1 - eps)/2 = 1/2 - e1
EPS = Fr(21, 100)
e1 = EPS / 2
# pair curve V: Bezout degree delta = d^2; N_V <= w (P+1) + (delta-1)(delta-2) sqrt(P) + (delta-1)(delta-2)/2 + delta^2; E[k(k-1)] = N_V / (4P)
delta = d * d
# second moment: the count premise N_off/p <= w (1 + eps) gives E[k(k-1)] = N_off/(4p) <= w/4 + e2, e2 = w eps / 4
def e2_of(w): return Fr(w) * EPS / 4
# coins: a draw is x = w mod P for one uniform 256-bit word w. 2^256 = 3 P + RES with 0 < RES < P: the residues below RES have 4 preimages, the other S3 = P - RES = 4 P - 2^256 have 3.
# statistical distance of x from uniform: eps_coin = S3 (1/P - 3/2^256).
# isolation lemma: a round is good (both parts nonconstant) when the shift a lies in a set of (P-1)/2 residues, at least (P-3)/2 of them nonzero; a is the draw x with 0 replaced by 1,
# every residue has at least 3 preimages and all but S3 residues have 4, so P[a in good] >= (4 (P-3)/2 - S3) / 2^256
RES = (1 << 256) - 3 * P
S3 = P - RES
assert 0 < RES < P and S3 == 4 * P - (1 << 256)
wq = Fr(4 * ((P - 3) // 2) - S3, 1 << 256)
eps_iso = sum(comb(ZCAP, j) * wq ** j * (1 - wq) ** (ZCAP - j) for j in range(0, 4))
eps_coin = S3 * (Fr(1, P) - Fr(3, 1 << 256))
def bound(w, K):
    e2 = e2_of(w)
    a = Fr(1, 2) - e1
    b = Fr(w, 4) + e2
    q_cs = a * a / (a + b)
    tail = b / ((DMAX + 1) * DMAX)
    q_cs_tail = q_cs - tail
    q_lin = a - b / 2                              # linear bound of 9.2(e'); the entry's q at w = 1
    assert all(((1 <= k <= DMAX) >= k - k * (k - 1) // 2) for k in range(0, 10 * DMAX))
    q = max(q_lin, q_cs_tail)                      # the larger valid bound (linear at w = 1)
    succ0 = 1 - (1 - q) ** K - K * (eps_coin + eps_iso + DELTA_C)
    succ = 1 - (1 - q + DELTA) ** K - K * (eps_coin + eps_iso + DELTA_C)   # with the H-NORMAL abnormality allowance delta (9.5)
    succ_cs = 1 - (1 - q_cs_tail) ** K - K * (eps_coin + eps_iso + DELTA_C)
    return dict(e2=e2, b=b, q_cs=q_cs, tail=tail, q_cs_tail=q_cs_tail, q=q, succ=succ, succ0=succ0, succ_cs=succ_cs, succ_notail=1 - (1 - q_cs) ** K)
def f(x, n=12): return '%.*f' % (n, float(x))
if __name__ == '__main__':
    W, K = 1, 2
    B = bound(W, K)
    print('D = 5^%d = %d, d = D - 1' % (6 + R, D))
    print('e1 < %.3e' % float(e1)); print('e2 < %s' % f(B['e2'], 10))
    print('E[k] >= 1/2 - e1; E[k(k-1)] <= w/4 + e2 = %s  (w = %d)' % (f(B['b'], 10), W))
    print('Cauchy-Schwarz: P(k >= 1) >= %s' % f(B['q_cs'], 10))
    print('Markov tail:    P(k > %d)  <= %s' % (DMAX, f(B['tail'], 10)))
    print('Cauchy-Schwarz minus tail (Jbenisek): q >= %s, K=2 success %s' % (f(B['q_cs_tail'], 10), f(B['succ_cs'], 12)))
    print('q = P(1 <= k <= %d) >= E[k] - E[k(k-1)]/2 = %s  (linear bound, used by this entry)' % (DMAX, f(B['q'], 10)))
    print('K = %d without the tail (P(k >= 1) only): %s' % (K, f(B['succ_notail'], 10)))
    print('per-round good probability w >= %s = 1/2 - %.3e' % (f(wq, 20), float(Fr(1, 2) - wq)))
    print('eps_iso < %.3e (2^%.2f)   eps_coin < %.3e (2^%.2f)   delta_C = 4 n1 (D-1) / 2^256 = %.3e (2^%.2f), n1 = %d' % (float(eps_iso), math.log2(float(eps_iso)), float(eps_coin), math.log2(float(eps_coin)), float(DELTA_C), math.log2(float(DELTA_C)), N1))
    print('success with delta = 0 >= 1 - (1-q)^%d - %d (eps_coin + eps_iso + delta_C) = %s' % (K, K, f(B['succ0'], 12)))
    print('success >= 1 - (1-q+delta)^%d - %d (eps_coin + eps_iso + delta_C) = %s   (delta = %s, H-NORMAL)' % (K, K, f(B['succ'], 12), f(DELTA, 4)))
    print('claimed success_probability: %s (floor at 5 decimals)' % ('%.5f' % (int(B['succ'] * 100000) / 100000)))
    for w in (1, 2, 3):
        Bw = bound(w, 2)
        print('w = %d: P(k>=1) >= %s, q >= %s, K=2 success %s, K=3 success %s' % (w, f(Bw['q_cs'], 8), f(Bw['q'], 8), f(Bw['succ'], 8), f(bound(w, 3)['succ'], 8)))
```

## 12. Appendix E: the stage C and stage D ledger and the allocator (`cd_ledger.py`, this package)

`cd_ledger.py` is this package's program (standard library only). Two parts of it are re-implementations written from the printed text of other entries' ledgers (read, not run): (1) the charging rules of e6dcb600 (bradcush; proof.md 4.2-4.5 and Appendix E there), which extend Jbenisek's ledger: the transform kernels and pass charges, the cyclic products, the block products (schemes (a) and (c)), the outer-transform charges (`ontt`, with the kernel charges counted from e6dcb600's kernel text), the coefficient-domain stage C (`powx_lean`, kept for validation only) and the half-gcd on the normal sequence (`hgcd`, `gcd_cost`); (2) the value-domain stage C of Jbenisek's entry 7b276afd (his proof 4.6 and Appendix E, `powx_vd`; bradcush's method; the same program in his entries at r = 16-19 and 21): the dimensions (`vd_dims`), the inner transforms, the geometric phase with its group buffer, the chirp evaluations and interpolations, the batch inversion, the tables and the kernel spectra, and the eight steps (`powx_vd`). Its own additions are the workspace rule (`ACAP`), the end rules of 4.4 and 4.6, the recording of every allocation and free in program order and the allocator simulation (`simulate`), and, for the validation only, a re-implementation of Jbenisek's block-product charges (`jb_*`: blocks of `3 * 2^31` coefficients, his outer kernels, four chunks) so that his row C can be reproduced with his conventions.

Validation. `python3 cd_ledger.py check21` reproduces the totals that e6dcb600 asserts at r = 21 with its chunk bounds and its coefficient-domain stage C: `S_C = 4,062,062,219,504,740,890,363,177`, `S_D = 1,360,756,098,766,545,569,709,103` and the four stage peaks (`119,209,289,619,500,726,912`, `238,418,579,240,595,258,048`, `632,939,936,390,951,625,792`, `577,946,978,315,814,447,872` bytes). `python3 cd_ledger.py checkvd` reproduces the row C asserted by Jbenisek's six value-domain entries with his conventions (his block products for the set-up, his allocation charge without the statistics 64, the live-block base of his call): r = 16 (1ebf2b44) `315,694,368,193,453,406,618`, r = 17 (628641e6) `1,401,025,390,875,007,771,940`, r = 18 (1b8cd7a6) `7,631,016,575,947,362,265,783`, r = 19 (f4f93349) `47,791,743,731,725,187,002,589`, r = 20 (7b276afd) `207,611,124,658,151,579,699,613`, r = 21 (86db9605) `1,125,652,627,902,830,084,736,451`, each to the operation (`match: True` six times), and prints the per-component split of 4.6 for each. Both validations run in a few seconds.

The run for this r (the call below, which traces the allocation sequence, and the untraced ledger, which must give the same `S_C` and `S_D`) uses the parameters of 4.5: chunk bounds `{"newton": 186264514923095703, "D": 96857547760009776}` (elements: the Newton products of 4.6 step 1 and the products of stage D; the coefficient-domain step kinds `sq`, `q`, `qg` of the predecessor are gone), workspace caps `{}` (elements; a cap of 0 means scheme (c) only), the pool threshold `2^51` bytes. It gives `S_C = 207,154,001,277,008,493,454,187`, `S_D = 207,628,691,374,595,267,697,955` and the allocator figures of section 7, in about 30 s, and prints the value-domain dimensions (`K = 173,472,348`, `n1 = 745,058,061,420,331,008`, `Lx = 402,653,184`, `Le = 536,870,912`, `Lq = 268,435,456`, `v = 2^57`, `ell = 144,115,189,803,804,069`, `196` steps) and the component charges of the table of 4.6.

The call that produces the figures of sections 6 and 7 at this r (in the folder of `cd_ledger.py`):

```python
import cd_ledger as L
res = L.run(20, cf={"newton": 186264514923095703, "D": 96857547760009776}, acap={}, trace=True, big_exp=51, lcut_shift=1)
plain = L.run(20, cf={"newton": 186264514923095703, "D": 96857547760009776}, acap={})            # the untraced ledger: the same S_C and S_D
assert (res['S_C'], res['S_D']) == (plain['S_C'], plain['S_D']) == (207154001277008493454187, 207628691374595267697955)
```

The validation of the value-domain port against Jbenisek's entries prints:

```
r = 16: K = 277,556, n1 = 1,192,093,942,808,576, Lx = 786,432, Le = 1,048,576, v = 2^48, steps 205 (45 with b = 1), ell = 281,476,024,011,421, Kq = 65,537, Lq = 393,216
  inner transform fwd / inv 449,396,745,180 / 465,144,958,607; geometric phase of one extension 483,262,304,733,579,998 (405.389 per element of n1); one extension 737,098,841,877,101,030
  step b = 0 / 1: 1,498,933,633,079,692,500 / 1,503,702,008,850,926,804; tables 94,490,745,861; Newton 2,617,763,975,440,187,705; product for q 654,778,069,640,487,811; eval g 618,578,477,129,091,804; 2K inner of g 249,465,526,017,576,618; step 3 372,509,300,221,327,680; step 4 737,098,841,877,101,030; step 5 17,583,386,398,888,798; loop 307,495,971,691,042,506,180; step 7 759,450,603,316,974,298; step 8 2,171,168,314,656,053,828
  row C = 315,694,368,193,453,406,618   (Jbenisek asserts 315,694,368,193,453,406,618)  match: True
r = 17: K = 1,387,779, n1 = 5,960,465,419,075,584, Lx = 3,145,728, Le = 4,194,304, v = 2^50, steps 203 (45 with b = 1), ell = 1,125,900,848,379,147, Kq = 262,145, Lq = 2,097,152
  inner transform fwd / inv 449,396,745,180 / 465,144,958,607; geometric phase of one extension 2,028,631,850,211,636,784 (340.348 per element of n1); one extension 3,297,813,621,387,538,115
  step b = 0 / 1: 6,719,306,900,281,956,898 / 6,743,148,761,958,259,234; tables 300,344,270,639; Newton 10,870,841,799,560,336,822; product for q 2,717,908,717,561,622,847; eval g 2,902,062,069,671,556,654; 2K inner of g 1,247,326,731,294,392,696; step 3 2,094,643,045,880,920,602; step 4 3,297,813,621,387,538,115; step 5 87,916,868,643,673,691; loop 1,365,092,184,532,670,855,414; step 7 3,409,572,348,056,267,595; step 8 9,305,121,132,316,206,558
  row C = 1,401,025,390,875,007,771,940   (Jbenisek asserts 1,401,025,390,875,007,771,940)  match: True
r = 18: K = 6,938,894, n1 = 29,802,322,800,410,624, Lx = 16,777,216, Le = 25,165,824, v = 2^52, steps 201 (45 with b = 1), ell = 4,503,600,040,085,809, Kq = 1,048,577, Lq = 8,388,608
  inner transform fwd / inv 449,396,745,180 / 465,144,958,607; geometric phase of one extension 11,863,089,509,435,068,106 (398.059 per element of n1); one extension 18,208,997,450,772,870,932
  step b = 0 / 1: 37,036,393,099,959,573,672 / 37,155,602,391,161,216,168; tables 1,330,204,155,324; Newton 45,068,721,602,328,715,635; product for q 11,266,824,449,212,364,189; eval g 18,675,886,367,401,725,640; 2K inner of g 6,236,632,757,678,473,086; step 3 9,267,381,161,841,999,452; step 4 18,208,997,450,772,870,932; step 5 439,584,279,867,598,156; loop 7,449,679,431,195,948,220,392; step 7 18,767,791,003,585,881,472; step 8 53,405,325,669,504,065,504
  row C = 7,631,016,575,947,362,265,783   (Jbenisek asserts 7,631,016,575,947,362,265,783)  match: True
r = 19: K = 34,694,470, n1 = 149,011,614,002,053,120, Lx = 100,663,296, Le = 134,217,728, v = 2^55, steps 198 (45 with b = 1), ell = 36,028,799,082,540,527, Kq = 8,388,609, Lq = 50,331,648
  inner transform fwd / inv 449,396,745,180 / 465,144,958,607; geometric phase of one extension 84,130,209,965,148,441,050 (564.588 per element of n1); one extension 115,859,749,671,837,455,164
  step b = 0 / 1: 234,811,490,335,744,069,272 / 235,407,536,791,752,281,752; tables 6,498,781,661,015; Newton 379,529,632,250,464,697,221; product for q 94,876,883,733,173,335,716; eval g 109,014,357,896,424,819,160; 2K inner of g 31,183,163,788,392,365,422; step 3 54,645,451,428,283,430,828; step 4 115,859,749,671,837,455,164; step 5 2,197,921,399,337,990,772; loop 46,519,497,176,997,695,277,456; step 7 118,653,717,435,902,507,848; step 8 366,285,677,118,375,567,152
  row C = 47,791,743,731,725,187,002,589   (Jbenisek asserts 47,791,743,731,725,187,002,589)  match: True
r = 20: K = 173,472,348, n1 = 745,058,061,420,331,008, Lx = 402,653,184, Le = 536,870,912, v = 2^57, steps 196 (45 with b = 1), ell = 144,115,189,803,804,069, Kq = 33,554,433, Lq = 268,435,456
  inner transform fwd / inv 449,396,745,180 / 465,144,958,607; geometric phase of one extension 348,877,404,340,561,752,334 (468.255 per element of n1); one extension 507,525,101,044,923,415,262
  step b = 0 / 1: 1,030,510,156,871,951,482,276 / 1,033,490,389,117,632,806,308; tables 32,271,564,475,855; Newton 1,568,707,544,408,474,487,463; product for q 392,153,640,844,941,157,079; eval g 490,454,522,773,052,174,604; 2K inner of g 155,915,817,144,374,846,330; step 3 305,448,486,124,727,488,048; step 4 507,525,101,044,923,415,262; step 5 10,989,606,869,988,413,270; loop 202,114,101,197,958,150,107,536; step 7 521,494,939,704,187,404,978; step 8 1,544,333,801,272,663,531,828
  row C = 207,611,124,658,151,579,699,613   (Jbenisek asserts 207,611,124,658,151,579,699,613)  match: True
r = 21: K = 867,361,738, n1 = 3,725,290,298,511,720,448, Lx = 2,147,483,648, Le = 3,221,225,472, v = 2^59, steps 194 (45 with b = 1), ell = 576,460,752,353,229,875, Kq = 134,217,729, Lq = 1,073,741,824
  inner transform fwd / inv 449,396,745,180 / 465,144,958,607; geometric phase of one extension 1,995,826,927,672,968,639,762 (535.751 per element of n1); one extension 2,789,065,409,365,693,546,760
  step b = 0 / 1: 5,655,430,592,463,669,209,312 / 5,670,331,753,657,716,091,104; tables 161,250,505,882,757; Newton 6,477,172,507,671,885,485,802; product for q 1,619,198,992,526,255,390,600; eval g 3,106,966,548,432,229,528,848; 2K inner of g 779,579,083,924,287,250,870; step 3 1,415,266,904,548,748,148,420; step 4 2,789,065,409,365,693,546,760; step 5 54,948,034,223,240,525,760; loop 1,097,824,087,191,683,936,287,168; step 7 2,858,914,602,500,952,221,636; step 8 8,727,428,627,942,774,090,568
  row C = 1,125,652,627,902,830,084,736,451   (Jbenisek asserts 1,125,652,627,902,830,084,736,451)  match: True
```

#### cd_ledger.py

```python
#!/usr/bin/env python3
"""Ledger of stages C and D for the Orchard Poseidon algebraic collision algorithm (Jbenisek's algorithm): stage C in the value domain
(the method of bradcush's entry 1aa56884, re-implemented from the printed program of Jbenisek's entry 7b276afd, read not run: two point sets
of K cosets of the subgroup of order 2^32, Montgomery squaring steps that are two pointwise passes and two extensions by a fixed-kernel cyclic
convolution over the coset index) and the lean stage D of bradcush's r = 21 entry e6dcb600 (truncated second half-gcd call, chunked
outer-transform products with blocks of HB = 2^31 and a one-row 2^32-point block transform, the normal remainder sequence with the abort
test), evaluated at any r.  The coefficient-domain stage C of e6dcb600 (powx_lean) is kept for the validation check21 and is not used by the claim.

This is a re-implementation, written for this package from the printed text of e6dcb600's ledger (read, not run), of the charging rules stated in e6dcb600 (proof.md 4.2-4.5, 6.3,
Appendix E there), which in turn extend the ledger of Jbenisek's f62fb39.  It is validated by reproducing every total that e6dcb600
asserts at r = 21 (S_C, S_D, the four stage peaks), see check_r21().  New here: every allocation and free is recorded in program order
and the allocator of section 7 (a two-ended first-fit pool for large blocks, slab classes for the others, the design of Jbenisek's
r = 8..20 entries) is simulated on that sequence, so the arena is an allocator capacity, not the peak of the live set.

Placement (this package; no operation count depends on it): every allocation statement has an end of the pool (stage C: a constant; stage D: derived
from the result end `ys` passed to hgcd, proof.md 4.4), and the remainder of a division is written over its dividend when the dividend's array has
exactly its length (the allocation and free this saves stay charged).  The workspace rule ACAP excludes scheme (a) for a product kind when its
workspace exceeds the cap; in the coefficient-domain step of the validation path, when q g is in scheme (a) the wrap of the square is not added (e6dcb600's lemma 4.5).

Exact integer arithmetic throughout; standard library only.
Usage: python3 cd_ledger.py check21      (reproduce e6dcb600's r = 21 totals with the coefficient-domain stage C)
       python3 cd_ledger.py checkvd 16 17 18 19 20 21  (reproduce Jbenisek's value-domain row C of 1ebf2b44, 628641e6, 1b8cd7a6, f4f93349, 7b276afd, 86db9605 exactly, with his charges)
       or call run(r, cf, acap, trace=True, big_exp=..., lcut_shift=1) as in proof.md Appendix E (vd=True: the value-domain stage C, the claim).
"""
import math
import sys

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
PM2, PM1H = P - 2, (P - 1) >> 1
INV_CTL, STAGE_BK, CACHE = 2310, 1000, 64


def powcost(e):
    """square-and-multiply cost of x^e on one element: squarings + multiplications"""
    return (e.bit_length() - 1) + (bin(e).count('1') - 1) if e > 0 else 0


# radix-2 pass kernels of a transform (section 4.2): for k = 1..4 layers, (c0, a, b): charge c0 + a G + b G S
PASS = {
    'f': ((4, 17, 19), (4, 35, 43), (4, 80, 96), (4, 185, 213)),
    'i': ((4, 17, 21), (4, 36, 47), (4, 82, 102), (4, 188, 221)),
    'usq': ((3, 18, 0), (3, 49, 0), (3, 128, 0), (3, 315, 0)),
    'umul': ((4, 23, 0), (4, 58, 0), (4, 145, 0), (4, 348, 0)),
}
# radix-3 position kernels: K3[type][pattern of nonzero rows][rotation]
K3 = {
    'f': [(6, 6, 6), (8, 14, 14), (14, 8, 14), (19, 19, 25), (14, 14, 8), (19, 25, 19), (25, 19, 19), (24, 24, 24)],
    'i': [None, (10, 16, 16), (16, 10, 16), (20, 20, 26), (16, 16, 10), (20, 26, 20), (26, 20, 20), (24, 24, 24)],
    'r0': [(2, 2, 2), (4, 4, 4), (4, 4, 4), (7, 7, 7), (4, 4, 4), (7, 7, 7), (7, 7, 7), (10, 10, 10)],
    'r1': [(2, 2, 2), (4, 7, 7), (7, 4, 7), (10, 10, 13), (7, 7, 4), (10, 13, 10), (13, 10, 10), (16, 16, 16)],
    'r2': [(2, 2, 2), (4, 7, 7), (7, 4, 7), (10, 10, 13), (7, 7, 4), (10, 13, 10), (13, 10, 10), (16, 16, 16)],
}
ROT = ((0, 0, 0), (0, 1, 2), (0, 2, 1))


def pass_fwd(a, l0, k):
    c0, p, q = PASS['f'][k - 1]
    g = 1 << l0
    return 5 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_inv(a, l0, k):
    c0, p, q = PASS['i'][k - 1]
    g = 1 << l0
    return 6 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_fused(a, k, mode):
    c0, p, q = PASS['usq' if mode == 'sq' else 'umul'][k - 1]
    return 6 + (9 * k + 2) + 6 + c0 + p * (1 << (a - k))


FREE_OPS = 105
ALLOC_STAT = 64                    # the allocator's flat statistics charge, on every allocation and every free


def blk(slots):
    """bytes of a block of `slots` field elements: 64-byte header + payload rounded up to 64"""
    return 64 + ((slots * 32 + 63) & ~63)


# ---------------------------------------------------------------- the walk: operation count, live set, and (when tracing) the event log
class Slot(int):
    """an array, represented by its number of slots; `sid` identifies a large block in the event log"""
    pass


TAGS = {}
POLICY = {}            # allocation statement (tag) -> end of the pool: 0 low, 1 high, 'p0'/'p1' alternate with the depth of the half-gcd recursion
DEPTH = [0]


def side_of(tag, default):
    v = POLICY.get(tag, default)
    if v == 'p0': return DEPTH[0] & 1
    if v == 'p1': return 1 - (DEPTH[0] & 1)
    return v
TRACE = {'log': None, 'depth': 0, 'big': None, 'sid': 0}   # log: events in program order; depth > 0 inside a summarised (cached) call;
                                                           # big: blocks of more than `big` bytes are pool blocks (identity kept)


def slab_class(nbytes):
    return max(7, (nbytes - 1).bit_length())


class Tr:
    __slots__ = ('ops', 'cur', 'peak', 'cnt', 'pcnt', 'base', 'live', 'ccur', 'cpk')

    def __init__(self, base=0):
        self.ops = 0; self.cur = 0; self.peak = 0; self.cnt = 0; self.pcnt = 0; self.base = base
        self.live = TRACE['log'] is not None and TRACE['depth'] == 0
        self.ccur = {}; self.cpk = {}

    def here(self):
        return self.base + self.cnt

    def ctl(self, n): self.ops += n
    def ld(self, n): self.ops += 2 * n
    def st(self, n): self.ops += 2 * n
    def loopc(self, n): self.ops += 3 * n + 2

    def _cls_add(self, c, d):
        v = self.ccur.get(c, 0) + d
        self.ccur[c] = v
        if v > self.cpk.get(c, 0): self.cpk[c] = v

    def add(self, o):
        self.ops += o.ops
        self.peak = max(self.peak, self.cur + o.peak); self.pcnt = max(self.pcnt, self.cnt + o.pcnt)
        self.cur += o.cur; self.cnt += o.cnt
        if TRACE['log'] is not None and not o.live:
            if self.live:
                TRACE['log'].append(('S', dict(o.ccur), dict(o.cpk)))
            else:
                for c in set(o.ccur) | set(o.cpk):
                    pk = self.ccur.get(c, 0) + o.cpk.get(c, 0)
                    if pk > self.cpk.get(c, 0): self.cpk[c] = pk
                    self.ccur[c] = self.ccur.get(c, 0) + o.ccur.get(c, 0)

    def new_fp(self, slots, side=0, tag=None):
        slots = max(slots, 1) if slots else 1
        if tag is not None: side = side_of(tag, side)
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1) + ALLOC_STAT
        b = blk(slots); self.cur += b; self.cnt += 1
        self.peak = max(self.peak, self.cur); self.pcnt = max(self.pcnt, self.cnt)
        s = Slot(slots)
        if TRACE['log'] is not None:
            if b > TRACE['big']:
                assert self.live, 'a pool block inside a summarised call'
                TRACE['sid'] += 1; s.sid = TRACE['sid']
                TRACE['log'].append(('A', s.sid, b, side)); TAGS[s.sid] = tag
            elif self.live:
                TRACE['log'].append(('a', slab_class(b)))
            else:
                self._cls_add(slab_class(b), 1)
        return s

    def charge_alloc_free(self):
        """the charge of an allocation and a free that the program replaces by writing in place (kept, so the count is an upper bound)"""
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1) + ALLOC_STAT + FREE_OPS + ALLOC_STAT

    def free(self, slots):
        self.ops += FREE_OPS + ALLOC_STAT
        b = blk(slots); self.cur -= b; self.cnt -= 1
        if TRACE['log'] is not None:
            if b > TRACE['big']:
                assert self.live and hasattr(slots, 'sid'), 'a pool block freed without identity'
                TRACE['log'].append(('F', slots.sid))
            elif self.live:
                TRACE['log'].append(('f', slab_class(b)))
            else:
                self._cls_add(slab_class(b), -1)


# ---------------------------------------------------------------- transform plans and the cyclic products (below the block length)
class Plan:
    def __init__(self, rows, a):
        self.rows = rows; self.a = a; self.n = 1 << a; self.N = 3 * self.n if rows == 3 else self.n
        self.c0 = (1 if a & 1 else 2) if rows == 3 else 0
        self.np = (a + 3) >> 2
        kk = [0] * self.np; rem = a
        for i in range(self.np - 1, -1, -1):
            k = min(4, rem); kk[i] = k; rem -= k
        self.kk = kk


def plan_invN_ops(Pl):
    return 7 * CACHE


def udivmod_cost(a, b):
    nb = a.bit_length(); q = a // b
    return 4 * nb + 2 + 10 * nb + 2 * bin(q).count('1') + 4


def for8(n):
    return 1 + 3 * (n // 8) + 2 + 3 * (n % 8) + 2


def make_plan(rows, a):
    p = Plan(rows, a)
    return p, 18 + 4 + (3 * p.np + 2) + 4 * p.np + 2 + (4 if rows == 3 else 0)


BIGA = 32                               # transforms of 3 * 2^a points exist in F_p for a <= 32 only
P32 = make_plan(1, BIGA)[0]             # the block transform: one row of 2^32 points
NB = P32.N; HB = NB // 2


def plan3_for_len(ln):
    c = 0
    for a in range(2, 64):
        c += 8
        if 3 * (1 << a) >= ln:
            p, cc = make_plan(3, a)
            return p, c + cc
    raise ValueError(ln)


def split_regions(n, N, boff, lenB):
    c = 3; bp = [0]; nt0 = 0
    for t in range(3):
        st = nt0 + N - boff
        if st >= N: st -= N
        nt0 += n; c += 9
        c += 3
        if st < lenB:
            x = lenB - st; c += 4
            if 0 < x < n: bp.append(x); c += 1
        c += 3
        if st > 0:
            x = N - st; c += 4
            if 0 < x < n: bp.append(x); c += 1
            x = N + lenB - st; c += 5
            if 0 < x < n: bp.append(x); c += 1
    c += 2
    bp.append(n); c += 1
    cnt = len(bp)
    for a in range(1, cnt):                      # insertion sort, charged per step
        key = bp[a]; b = a - 1; c += 5
        while b >= 0 and bp[b] > key:
            bp[b + 1] = bp[b]; b -= 1; c += 6
        c += 3
        bp[b + 1] = key
    c += 2
    out = []; pats = []
    for a in range(cnt - 1):
        c += 6
        if bp[a + 1] > bp[a]:
            lo = bp[a]; p = 0; nt1 = 0
            for t in range(3):
                idx = lo + nt1 + N - boff
                if idx >= N: idx -= N
                p |= (1 if idx < lenB else 0) << t; nt1 += n; c += 13
            c += 5
            out.append(lo); pats.append(p); c += 2
    c += 2
    out.append(n); c += 1
    return out, pats, c


def driver(typ, pat, c0, lo, hi):
    K = [K3[typ][pat][r] for r in ROT[c0]]
    i = lo
    c = udivmod_cost(lo, 3); ph = lo % 3; c += 1
    c += 2
    if ph == 1:
        c += 2
        if i < hi:
            c += K[1]; i += 1; c += 1
            c += 2
            if i < hi:
                c += K[2]; i += 1; c += 1
    else:
        c += 2
        if ph == 2:
            c += 2
            if i < hi:
                c += K[2]; i += 1; c += 1
    nt = 0; c += 2
    if hi > i:
        nt = (hi - i) // 3; c += udivmod_cost(hi - i, 3); c += 2
    c += nt * (K[0] + K[1] + K[2] + 4)
    i += 3 * nt
    c += 4
    if hi > i:
        rem = hi - i; c += 1
        c += K[0]; i += 1; c += 1
        c += 2
        if rem == 2:
            c += K[1]
    return c


def stageA_fwd(Pl, ln):
    c = 4; n = Pl.n
    if Pl.rows == 1:                      # the one-row block transform: copy ln coefficients (load + store each), zero the rest (a store each)
        assert Pl.a > BIGA - 1 and ln <= n
        return c + for8(ln) + 4 * ln + for8(n - ln) + 2 * (n - ln) + 2
    bp, pat, cc = split_regions(n, Pl.N, 0, ln); c += cc + 2
    for q in range(len(pat)):
        c += 4 + driver('f', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_inv(Pl, outlen):
    if Pl.rows == 1:
        return 0
    c = 2
    bp, pat, cc = split_regions(Pl.n, Pl.N, 0, outlen); c += cc + 2
    for q in range(len(pat)):
        c += 2
        if pat[q] == 0:
            c += 3; continue
        c += 4 + driver('i', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_row(Pl, r, lenB, boff):
    bp, pat, c = split_regions(Pl.n, Pl.N, boff, lenB)
    c += 2
    for q in range(len(pat)):
        c += 3 * 11 + 2 + 4 + driver('r%d' % r, pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def fwd_passes(Pl, cnt):
    l0 = 0; c = 0
    for p in range(cnt):
        c += pass_fwd(Pl.a, l0, Pl.kk[p]) + 4; l0 += Pl.kk[p]
    return c


def inv_passes(Pl, first):
    l0 = sum(Pl.kk[:first + 1]); c = 0
    for p in range(first, -1, -1):
        l0 -= Pl.kk[p]
        c += pass_inv(Pl.a, l0, Pl.kk[p]) + 4
    return c


def fused(Pl, mode):
    return pass_fused(Pl.a, Pl.kk[-1], mode)


def conv_core_row(Pl, mode):
    return 9 + fwd_passes(Pl, Pl.np - 1) + 4 + fused(Pl, mode) + inv_passes(Pl, Pl.np - 2) + 4


def conv_sq(Pl, ln, outlen):
    assert Pl.a <= BIGA
    c = stageA_fwd(Pl, ln) + Pl.rows * conv_core_row(Pl, 'sq') + 2
    return c + stageA_inv(Pl, outlen)


def mulc_otf_row(Pl, r, lenB, boff):
    c = 12 + stageA_row(Pl, r, lenB, boff)
    c += fwd_passes(Pl, Pl.np) + 2
    c += fwd_passes(Pl, Pl.np - 1) + fused(Pl, 'mul') + inv_passes(Pl, Pl.np - 2) + 4
    return c


def conv_mulc_otf(Pl, ln, lenB, boff, outlen, sub=False):
    if Pl.a > BIGA:
        return conv_mulc_big(ln, lenB, (Pl.N - boff) % Pl.N, outlen, sub)
    c = 2 + stageA_fwd(Pl, ln) + 4
    for r in range(3):
        c += mulc_otf_row(Pl, r, lenB, boff)
    return c + 2 + stageA_inv(Pl, outlen)


def pw_loop(n, mode):
    return for8(n) + n * (7 if mode == 0 else 10)


def _eps(nout, groups):
    eps = [0] * nout
    for g in groups:
        for s in range(len(g['S'])):
            for h in range(len(g['H'])):
                o, sg = g['prod'].get((s, h), (-1, 0))
                if o >= 0 and not eps[o]:
                    eps[o] = sg
    return eps


def conv_bilin_cost(Pl, nout, outlen, groups):
    """a bilinear form (several products summed into nout outputs) on one cyclic transform, rows processed one at a time"""
    if Pl.a > BIGA:
        return conv_bilin_big(nout, outlen, groups)
    c = 2 + 2 + 3 * nout
    eps = _eps(nout, groups)
    for g in groups:
        c += 6 * len(g['S']) * len(g['H'])
    for r in range(3):
        c += 2 + 2 + nout + 1
        done = [0] * nout
        for g in groups:
            c += 7
            for lh in g['H']:
                c += 6 + stageA_row(Pl, r, lh, 0) + fwd_passes(Pl, Pl.np)
            for s, ls in enumerate(g['S']):
                c += 6 + stageA_row(Pl, r, ls, 0) + fwd_passes(Pl, Pl.np)
                for h in range(len(g['H'])):
                    c += 8
                    o, sg = g['prod'].get((s, h), (-1, 0))
                    if o < 0: continue
                    if not done[o]:
                        done[o] = 1; c += pw_loop(Pl.n, 0)
                    elif sg == eps[o]:
                        c += pw_loop(Pl.n, 1)
                    else:
                        c += pw_loop(Pl.n, 2)
        for k in range(nout):
            c += 3
            if eps[k]:
                c += inv_passes(Pl, Pl.np - 1)
    for k in range(nout):
        c += 3
        if eps[k]:
            c += stageA_inv(Pl, outlen[k])
    return c, eps


# ---------------------------------------------------------------- block products (section 4.5): blocks of HB = 2^31, block transform of NB = 2^32 points
_BF = {}


def big_fwd(bl):                        # forward block transform of a block of bl coefficients, zero-padded to NB
    if bl not in _BF:
        _BF[bl] = stageA_fwd(P32, bl) + P32.rows * fwd_passes(P32, P32.np)
    return _BF[bl]


def big_inv(outn):                      # inverse block transform (the factor NB is removed by the placement)
    return P32.rows * inv_passes(P32, P32.np - 1) + stageA_inv(P32, outn)


def big_pw(mode):                       # one pointwise pass over NB points: 0 write, 1 add, 2 subtract
    return P32.rows * pw_loop(P32.n, mode)


def nblk(l): return -(-l // HB)


def big_fwd_all(l):
    k = nblk(l)
    return (k - 1) * big_fwd(HB) + big_fwd(l - (k - 1) * HB)


def big_place(cnt, ov, sub):
    c = 3 * cnt + 2 + 2 * cnt + cnt + 2 * cnt
    return c + (cnt if sub else ov) * 3


# outer-transform kernels (e6dcb600, Appendix E: ob3, ob2f/ob4f/ob8f, ob2i/ob4i/ob8i), charge c0 + c1 * cnt counted from their text:
# ob3: call 10, two constant loads 4, loop exit 2; per position 3 loads (6), 8 field operations, 3 stores (6), loop step 3.
# ob(2^k): call 10, (2^k - 1) twiddle loads, loop exit 2; per position 2^k loads, k 2^(k-1) butterflies of 3 operations, 2^k stores, loop step 3.
def _kch(k):
    if k == 0:
        return 10 + 4 + 2, 6 + 8 + 6 + 3
    w = 1 << k
    return 10 + 2 * (w - 1) + 2, 2 * w + 3 * k * (w // 2) + 2 * w + 3


KCH = {'ob3': _kch(0)}
for _k in (1, 2, 3):
    KCH['ob%df' % (1 << _k)] = KCH['ob%di' % (1 << _k)] = _kch(_k)
assert KCH['ob3'] == (16, 23) and KCH['ob2f'] == (14, 14) and KCH['ob4f'] == (18, 31) and KCH['ob8f'] == (26, 71)
ADR_CTL, TWI_CTL = 4, 3


def outer_plan(n):
    r3 = n % 3 == 0; M = n // 3 if r3 else n
    a = M.bit_length() - 1
    assert (1 << a) == M, n
    return r3, M, ([a % 3] if a % 3 else []) + [3] * (a // 3)


def ontt(n, cnt, inv=False):
    """charge of the outer transform of n points at cnt positions (twiddle table 6n + 2, Good-Thomas radix-3 stage, passes of <= 3 layers)"""
    r3, M, ks = outer_plan(n)
    c = 6 * n + 2
    nrows = 3 if r3 else 1
    if r3:
        k0, k1 = KCH['ob3']
        c += 10 + 3 * M + 2 + M * (3 * ADR_CTL + k0 + k1 * cnt)
    c += 3 * nrows + 2
    per_row = 3 * len(ks) + 2; Ns = M
    for k in ks:
        h = Ns >> k; nb = M // Ns
        k0, k1 = KCH[('ob%d' % (1 << k)) + ('i' if inv else 'f')]
        per_row += 3 * nb + 2 + nb * (3 * h + 2) + nb * h * ((1 << k) * ADR_CTL + ((1 << k) - 1) * TWI_CTL + k0 + k1 * cnt)
        Ns >>= k
    return c + nrows * per_row


def pad23(n):
    best = None
    for a in range(0, 33):
        for c in (1, 3):
            v = c << a
            if v >= n and (best is None or v < best): best = v
    assert best is not None, n
    return best


CTX = {'cf': None, 'ltrue': None, 'cyc': None, 'acap': None}
ACAP = {}
PL = {}
CF = {}


def nc_for(n2, cf):
    nc = 1
    while cf is not None and (n2 // nc) * HB > cf and (n2 // nc) % 2 == 0: nc *= 2
    return nc


def segs(ws, ln):
    e = ws + ln
    if ln <= 0: return []
    q = min(e, (ws // HB + 1) * HB)
    if q == e: return [(ln, 1)]
    out = [(q - ws, 1)]
    full = (e - q) // HB; rest = e - q - full * HB
    if full: out.append((HB, full))
    if rest: out.append((rest, 1))
    return out


def fold_ops(l, n3, tw):
    """twist and fold an operand of l coefficients into its chunk array of n3 rows of HB"""
    kx = nblk(l); last = l - (kx - 1) * HB
    wr = 4 + tw; ac = 7 + tw
    first = min(kx, n3); acc = kx - first; zero_rows = max(0, n3 - kx)
    c = 0
    if kx <= n3:
        c += (first - 1) * (10 + for8(HB) + wr * HB) + 10 + for8(last) + wr * last + for8(HB - last) + 2 * (HB - last)
    else:
        c += first * (10 + for8(HB) + wr * HB) + (acc - 1) * (10 + for8(HB) + ac * HB) + 10 + for8(last) + ac * last
    c += zero_rows * (10 + for8(HB) + 2 * HB)
    return c + 3 * (kx + zero_rows) + 2


def acc_ops(ws, ln, first, sub):
    per = 5 if (first and not sub) else 8
    return sum(c * (10 + for8(x) + per * x + 3) for x, c in segs(ws, ln)) + 2


FOLD_ROW = 8 * HB + for8(HB) + 4


def _gp(n, kb):
    if n <= 0: return 0
    return n * (n + 1) // 2 if n <= kb else kb * (kb + 1) // 2 + (n - kb) * kb


def pairs_upto(ka, kb, s):
    if s < 0: return 0
    return _gp(s + 1, kb) - _gp(s + 1 - ka, kb)


def pairs_range(ka, kb, A, B):
    return pairs_upto(ka, kb, B) - pairs_upto(ka, kb, A - 1)


def window_slots(ws, outlen):
    we = ws + outlen
    s0 = max(0, (ws + 1) // HB - 3)
    while (s0 + 2) * HB - 1 <= ws: s0 += 1
    s1 = -(-we // HB) + 2
    while s1 * HB >= we: s1 -= 1
    return s0, s1, we


def slot_cost(s, s0, ws, we, sub):
    lo, hi = s * HB, (s + 2) * HB - 1
    outn = min(NB - 1, we - lo); cnt = min(hi, we) - max(lo, ws)
    ov = 0
    if s > s0: ov = max(0, min((s + 1) * HB - 1, we) - max(s * HB, ws))
    return big_inv(outn) + big_place(cnt, ov, sub)


ROOTS = 6 * (330 + INV_CTL)
MODE_LOG = {}


def conv_bilin_big(nout, outlen, groups, ws=0, sub=False, shared=False):
    """a block product (bilinear form): scheme (a) (slots) or scheme (c) (chunked outer product modulo Y^n2 - 1), whichever is cheaper"""
    eps = _eps(nout, groups)
    prods = [[] for _ in range(nout)]
    for g in groups:
        for (si, hi_), (o, sg) in g['prod'].items():
            if o >= 0: prods[o].append((g['S'][si], g['H'][hi_]))
    ops_ = []
    for g in groups:
        ops_ += list(g['H'])
        if not shared: ops_ += list(g['S'])
    pw0, pw1 = big_pw(0), big_pw(1)
    # scheme (a)
    ca = 2 + sum(big_fwd_all(l) for l in ops_)
    live = []
    for k in range(nout):
        if not eps[k] or not prods[k]: continue
        live.append(k)
        s0, s1, we = window_slots(ws, outlen[k])
        stot = max(nblk(ls) + nblk(lh) - 1 for ls, lh in prods[k])
        A, B = s0, min(s1, stot - 1)
        if B < A: continue
        npr = sum(pairs_range(nblk(ls), nblk(lh), A, B) for ls, lh in prods[k])
        cnt_s = B - A + 1
        ca += cnt_s * (pw0 - pw1) + pw1 * npr
        edges = sorted(set(range(A, min(A + 3, B + 1))) | set(range(max(B - 2, A), B + 1)))
        for s in edges: ca += slot_cost(s, s0, ws, we, sub)
        mid = cnt_s - len(edges)
        if mid > 0:
            ca += mid * slot_cost(edges[2] + 1, s0, ws, we, sub)
    temps_a = [nblk(l) * NB for l in ops_] + [NB]
    # scheme (c)
    need = 0
    lt = CTX['ltrue']
    for k in live:
        if CTX['cyc']:
            need = max(need, CTX['cyc'])
        else:
            L = lt[k] if lt else max(ls + lh - 1 for ls, lh in prods[k])
            need = max(need, ws + outlen[k], L - ws)
    n2 = pad23(-(-need // HB)); nc = nc_for(n2, CTX['cf']); n3 = n2 // nc
    mops = [l for l in ops_ if nblk(l) > 1]; singles = [l for l in ops_ if nblk(l) == 1]
    co = 2 + ROOTS + sum(big_fwd(l) for l in singles) + 3 * nc + 2
    for j_first, mult in ((True, 1), (False, nc - 1)):
        if not mult: continue
        cj = 6 + sum(fold_ops(l, n3, 0 if j_first else 1) for l in mops) + len(mops) * ontt(n3, HB) + n3 * (8 + len(mops) * big_fwd(HB))
        for k in live:
            cj += n3 * (pw0 + (len(prods[k]) - 1) * pw1 + big_inv(NB - 1) + FOLD_ROW) + ontt(n3, HB, True) + acc_ops(ws, outlen[k], j_first, sub)
        co += mult * cj
    temps_c = [n3 * HB] * max(len(mops), len(live)) + [NB] * (len(ops_) + len(live)) + [n3]
    use_c = co <= ca
    if CTX.get('acap') is not None and sum(temps_a) > CTX['acap']:
        use_c = True                       # the workspace rule (this package): scheme (a) only when its workspace fits under the cap
    PL.clear()
    PL.update(mode='c' if use_c else 'a', n2=n2 if use_c else 0, nc=nc if use_c else 0, temps=temps_c if use_c else temps_a, ca=ca, co=co)
    MODE_LOG[PL['mode']] = MODE_LOG.get(PL['mode'], 0) + 1
    return (co if use_c else ca), eps


def conv_mulc_big(ln, lenB, ws, outlen, sub=False):
    return conv_bilin_big(1, [outlen], [dict(H=[lenB], S=[ln], prod={(0, 0): (0, 1)})], ws, sub, False)[0] + 6


def product_peak(T, Pl):
    """the temporary arrays of the product just evaluated, allocated at its start and freed at its end"""
    arr = PL['temps'] if Pl.a > BIGA else [Pl.n]
    ids = [T.new_fp(x, 1, 'tmpN') for x in arr]
    for x in ids: T.free(x)


# ---------------------------------------------------------------- stage C: S^((p-1)/2) mod g (section 4.5 of e6dcb600: the lean step)
def ebit(E, i): return (E >> i) & 1


def step_walk(base, m, Psq, Pq, Pg, Fcur):
    """the arrays of one squaring step: Fn and T1 receive S^bit R^2, R (the array F) is freed, q gets its own array, T1 is freed, q g is
    subtracted from Fn, q is freed; Fn is the new F.  Returns the trace and the new F."""
    S = Tr(base)
    sT1 = S.new_fp(m, 1, 'T1'); sFn = S.new_fp(m + 1, 0, 'Fn')               # T1 and the temporaries from the high end of the pool, F, Fn and q from the low end
    for x in [S.new_fp(y, 1, 'tmpC') for y in Psq['temps']]: S.free(x)
    S.free(Fcur)
    sq = S.new_fp(m, 0, 'qC')
    for x in [S.new_fp(y, 1, 'tmpC') for y in Pq['temps']]: S.free(x)
    S.free(sT1)
    for x in [S.new_fp(y, 1, 'tmpC') for y in Pg['temps']]: S.free(x)
    S.free(sq)
    assert S.cur == 0 and S.cnt == 0
    return S, sFn


def powx_lean(m, b, Fslot, E=PM1H):
    T = Tr(b)
    PN, c1 = plan3_for_len(2 * m - 1); PNp, c2 = plan3_for_len(m + 1)
    T.ctl(c1 + c2)
    N, Np = PN.N, PNp.N
    BIG = PN.a > BIGA
    if BIG:
        assert PNp.a > BIGA
        sM = T.new_fp(m, 1, 'MU'); sY = T.new_fp(m, 0, 'Y')          # MU from the high end for the whole of stage C
        L = m
        CTX['cf'] = CF.get('newton'); CTX['acap'] = ACAP.get('newton')
    else:
        sY = T.new_fp(N, 0, 'Yc'); sT = T.new_fp(PN.n, 0, 'Tc'); sM = T.new_fp(m - 1, 0, 'MUc')
        L = m - 1
    # Newton iteration for the reciprocal
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
        if BIG:
            assert P1.a > BIGA or P1.N <= m - 1
            product_peak(T, P1)
        T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
        if BIG:
            assert P2.a > BIGA or P2.N <= m - 1
            product_peak(T, P2)
        T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    CTX['cf'] = None; CTX['acap'] = None
    T.ld(L); T.st(L); T.loopc(L // 2); T.ctl(2 * (L // 2))
    T.ctl(plan_invN_ops(PN)); T.ctl(plan_invN_ops(PNp)); T.ops += 1
    T.ops += L; T.ld(L); T.st(L); T.loopc(L)
    gamma = N - (m - 2)
    info = {}
    if BIG:
        CTX['cf'] = CF.get('sq'); CTX['acap'] = ACAP.get('sq')
        sq_ops = conv_bilin_big(1, [2 * m - 1], [dict(H=[m], S=[m], prod={(0, 0): (0, 1)})], 0, False, True)[0] + 4; Psq = dict(PL)
        CTX['cf'] = CF.get('q'); CTX['acap'] = ACAP.get('q')
        q_ops = conv_bilin_big(1, [m], [dict(H=[m], S=[m], prod={(0, 0): (0, 1)})], m - 1)[0] + 6; Pq = dict(PL)
        CTX['cf'] = CF.get('qg'); CTX['acap'] = ACAP.get('qg'); CTX['cyc'] = m + 1
        qg_ops = conv_bilin_big(1, [m], [dict(H=[m + 1], S=[m], prod={(0, 0): (0, 1)})], 0, True)[0] + 6; Pg = dict(PL)
        CTX['cf'] = None; CTX['cyc'] = None; CTX['acap'] = None
        # e6dcb600 has every step product in scheme (c) at r = 21.  At smaller r scheme (a) can be cheaper; the square and the quotient are
        # exact windows in either scheme, and q g in scheme (a) is the exact linear product: then A - q g has degree < m (lemma 4.5 with no
        # cyclic reduction), Fn = A[0..m) - (q g)[0..m) and no wrap of A is added (nf = 0).
        T.free(sY)
        Nq = Pg['n2'] * HB if Pg['mode'] == 'c' else None
        nf = max(0, 2 * m - Nq) if Nq is not None else 0
        fold_F = for8(nf) + 7 * nf + 10
        info['prods'] = {'sq': (Psq['mode'], Psq['n2'], Psq['nc'], sq_ops), 'q': (Pq['mode'], Pq['n2'], Pq['nc'], q_ops), 'qg': (Pg['mode'], Pg['n2'], Pg['nc'], qg_ops)}
    info['peakN'] = T.peak
    top = 255
    while top > 0 and not ebit(E, top):
        top -= 1; T.ctl(12)
    v = 1; bit = top
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1; T.ctl(25)
    T.st(m); T.loopc(m)
    T.ctl(plan_invN_ops(PN)); T.st(1)
    steps = bit
    lim = (2 * m - 2 - Np + 1) if 2 * m - 2 >= Np else 0
    lim = min(lim, m)
    Fnow = Fslot
    if BIG:
        S, Fnow = step_walk(T.here(), m, Psq, Pq, Pg, Fnow)
        step = sq_ops + 8 + 4 + fold_F + q_ops + qg_ops + S.ops
        if TRACE['log'] is not None:          # the event log: every step allocates and frees its arrays (identical charges)
            for _ in range(steps - 1):
                _, Fnow = step_walk(T.here(), m, Psq, Pq, Pg, Fnow)
    else:
        step = conv_sq(PN, m, 2 * m - 1) + 8
        step += for8(lim) + 7 * lim + for8(m - lim) + 4 * (m - lim) + for8(m - 1) + 4 * (m - 1)
        step += conv_mulc_otf(PN, m - 1, m - 1, gamma, m - 1) + conv_mulc_otf(PNp, m - 1, m + 1, 0, m)
        step += for8(m) + 7 * m
    step += 14 + 6
    nset = sum(ebit(E, i) for i in range(bit))
    mulx = 0 if BIG else 2 + for8(m - 1) + 8 * (m - 1) + 2 + 4
    T.ops += steps * step + nset * mulx
    if BIG:
        T.peak = max(T.peak, T.cur + S.peak); T.pcnt = max(T.pcnt, T.cnt + S.pcnt)
        info['peakS'] = T.cur + S.peak
    T.ops += 1 + m; T.ld(m); T.st(m); T.loopc(m)
    T.ctl(2 + 500)
    if BIG:
        T.free(sM)
    else:
        T.free(sY); T.free(sT); T.free(sM)
    info.update(steps=steps, nset=nset, step=step, mulx=mulx, BIG=BIG, F=Fnow)
    return T, info


# ---------------------------------------------------------------- (i) Jbenisek's block products (7b276afd, Appendix E there), re-implemented for the validation only
JB = {'NB': 3 << 32, 'HB': 3 << 31}
_P32J = make_plan(3, 32)[0]
JB_OB2, JB_OB3, JB_OCALL = (5, 13), (7, 24), 10
JB_OCP, JB_OAX, JB_OZF, JB_OCALL_C, JB_OCALL_I = (5, 7), (5, 10), (3, 4), 30, 31
JB_CHUNKS = 4            # CHUNK_C of 7b276afd (stage C)
_JBF = {}


def jb_nblk(l): return -(-l // JB['HB'])


def jb_fwd(bl):
    if bl not in _JBF: _JBF[bl] = stageA_fwd(_P32J, bl) + 3 * fwd_passes(_P32J, _P32J.np)
    return _JBF[bl]


def jb_inv(outn): return 3 * inv_passes(_P32J, _P32J.np - 1) + stageA_inv(_P32J, outn)


def jb_pw(mode): return 3 * pw_loop(_P32J.n, mode)


def jb_fwd_all(l):
    k = jb_nblk(l); HB = JB['HB']
    return (k - 1) * jb_fwd(HB) + jb_fwd(l - (k - 1) * HB)


def jb_place(cnt, ov, sub):
    return 3 * cnt + 2 + 2 * cnt + cnt + 2 * cnt + (cnt if sub else ov) * 3


def jb_ontt(n, cnt):
    c = 3 * n; q = n
    if n % 3 == 0:
        q = n // 3; c += q * (JB_OCALL + JB_OB3[0] + JB_OB3[1] * cnt)
    lg = q.bit_length() - 1
    assert (1 << lg) == q
    return c + lg * (n // 2) * (JB_OCALL + JB_OB2[0] + JB_OB2[1] * cnt)


def jb_chunk_fill(l, Q, pc):
    HB = JB['HB']; k = jb_nblk(l); last = l - (k - 1) * HB
    nocp = min(k, Q); noax = k - nocp
    full = lambda ch, n: n * (JB_OCALL_C + ch[0] + ch[1] * HB)
    c = full(JB_OCP, nocp) + full(JB_OAX, noax)
    if nocp == k:
        c -= JB_OCP[1] * (HB - last)
        if last < HB: c += JB_OCALL_C + JB_OZF[0] + JB_OZF[1] * (HB - last)
    else: c -= JB_OAX[1] * (HB - last)
    if k < Q: c += (Q - k) * (JB_OCALL_C + JB_OZF[0] + JB_OZF[1] * HB)
    return pc * c


def _gp(n, kb):
    if n <= 0: return 0
    return n * (n + 1) // 2 if n <= kb else kb * (kb + 1) // 2 + (n - kb) * kb


def _pairs_upto(ka, kb, s): return 0 if s < 0 else _gp(s + 1, kb) - _gp(s + 1 - ka, kb)


def _pairs_range(ka, kb, A, B): return _pairs_upto(ka, kb, B) - _pairs_upto(ka, kb, A - 1)


def _ok23(q):
    while q % 2 == 0: q //= 2
    return q in (1, 3)


JBPL = {}


def jb_mulc_big(ln, lenB, ws, outlen, sub=False):
    """one product (S of ln coefficients times H of lenB), window [ws, ws + outlen), by Jbenisek's scheme (a) (slots) or scheme (c) (chunked outer
    product, 4 chunks), whichever is cheaper; describes the scheme in JBPL.  +6 for the call (conv_mulc_big)."""
    NB, HB = JB['NB'], JB['HB']
    ops_ = [lenB, ln]
    pw0, pw1 = jb_pw(0), jb_pw(1)
    we = ws + outlen
    s0 = max(0, (ws + 1) // HB - 3)
    while (s0 + 2) * HB - 1 <= ws: s0 += 1
    s1 = -(-we // HB) + 2
    while s1 * HB >= we: s1 -= 1
    stot = jb_nblk(ln) + jb_nblk(lenB) - 1
    A, B = s0, min(s1, stot - 1)
    # scheme (a)
    ca = 2 + sum(jb_fwd_all(l) for l in ops_)

    def slot(s):
        lo, hi = s * HB, (s + 2) * HB - 1
        outn = min(NB - 1, we - lo); cnt = min(hi, we) - max(lo, ws)
        ov = max(0, min((s + 1) * HB - 1, we) - max(s * HB, ws)) if s > s0 else 0
        return jb_inv(outn) + jb_place(cnt, ov, sub)
    if B >= A:
        npr = _pairs_range(jb_nblk(ln), jb_nblk(lenB), A, B)
        cnt_s = B - A + 1
        ca += cnt_s * (pw0 - pw1) + pw1 * npr
        edges = sorted(set(range(A, min(A + 3, B + 1))) | set(range(max(B - 2, A), B + 1)))
        ca += sum(slot(s) for s in edges)
        mid = cnt_s - len(edges)
        if mid > 0: ca += mid * slot(edges[2] + 1)
    cc = None; n2 = 0; pcs = 1; acc = 0
    if max(jb_nblk(l) for l in ops_) > 1:
        n2 = pad23(max(s1 + 2, stot + 1 - s0))
        pcs = JB_CHUNKS if (n2 % JB_CHUNKS == 0 and _ok23(n2 // JB_CHUNKS)) else 1
        Q = n2 // pcs
        cc = 2 + 3 * (n2 + 1)
        for l in ops_:
            if jb_nblk(l) > 1: cc += n2 * jb_fwd(HB) + jb_chunk_fill(l, Q, pcs) + pcs * jb_ontt(Q, HB)
            else: cc += jb_fwd(l)
        tc = max(0, min(n2, B - A + 2)); acc = tc * HB
        cc += n2 * pw0 + n2 * jb_inv(NB - 1) + n2 * jb_place(HB, HB, False) + pcs * jb_ontt(Q, HB) + jb_place(outlen, outlen, sub)
        cc += tc * (JB_OCALL_I + JB_OCP[0] + JB_OCP[1] * HB) + (pcs - 1) * tc * (JB_OCALL_I + JB_OAX[0] + JB_OAX[1] * HB)
    use_c = cc is not None and cc < ca
    nf = sum(1 for l in ops_ if jb_nblk(l) > 1)
    if use_c:
        temps = [(n2 // pcs) * HB if jb_nblk(l) > 1 else jb_nblk(l) * NB for l in ops_] + [(n2 // pcs) * HB] * max(0, 1 - nf) + [NB] * 3 + [n2 + 1, n2 // pcs, acc]
    else:
        temps = [jb_nblk(l) * NB for l in ops_] + [NB]
    JBPL.clear(); JBPL.update(mode='c' if use_c else 'a', n2=n2 if use_c else 0, nc=pcs if use_c else 0, temps=temps, ca=ca, cc=cc)
    return (cc if use_c else ca) + 6


def jb_mulc_otf(Pl, ln, lenB, boff, outlen):
    """conv_mulc_otf of 7b276afd: a product below the block length on one cyclic transform (identical kernels to ours), else jb_mulc_big"""
    if Pl.a > 32: return jb_mulc_big(ln, lenB, (Pl.N - boff) % Pl.N, outlen)
    return conv_mulc_otf(Pl, ln, lenB, boff, outlen)


def jb_product_peak(T, Pl):
    arr = JBPL['temps'] if Pl.a > 32 else [Pl.n]
    ids = [T.new_fp(x, 1, 'tmpN') for x in arr]
    for x in ids: T.free(x)


# ---------------------------------------------------------------- (ii) the value-domain stage C
VD_H = 1 << 32         # h: the subgroup order; one coset = one row of the radix-2 passes of 4.2 (a = 32), transformed in place
VCNT = 1 << 10         # inner positions per group of the geometric phase
VSHIFT = 2             # the start monomial S^v: the largest power of two below m, shifted down VSHIFT times (a multiple of h; two more steps, a shorter reciprocal)
VD_CALL = 10           # one call of an inner transform: the coset address, the plan and twiddle arguments, call and return
VD_ROW = 16            # one row of a group copy with a running factor: the factor and its step loaded, the factor stored back, two addresses, call, entry, exit
VD_ROWC = 12           # one row of a group copy with a per-row constant: the constant loaded, two addresses, call, entry, exit
VD_PWC = 14            # one coset of a pointwise pass: its constants loaded (1/M(n_k), u_k, the coset factor) and the addresses
VD_GROUP = 20          # one group of the geometric phase: its position offset, the buffer and table addresses, the calls
VD_NTAB = 30           # per-coset constants of the tables (u_k, 1/u_k, the base factors of the copies, 1/M(n_k), u_k^v M(n_k), 1/M'(z^k), M(z^(K+t)), 1/M2'(z^(K+t)), M2(z^t) z^-t, the chirp scales, the coefficients mu_i of M, ...)
VD = {}


def vd_inv1(): return powcost(PM2) + INV_CTL


def vd_plan(Lc):
    """the plan of a cyclic convolution of Lc = 2^a or 3 * 2^a points (a <= 32)"""
    rows = 3 if Lc % 3 == 0 else 1
    a = (Lc // rows).bit_length() - 1
    Pl, c = make_plan(rows, a)
    assert Pl.N == Lc and a <= 32, Lc
    return Pl, c


def vd_dims(m, E=PM1H):
    """K cosets, n1 = K h points per set, the convolution lengths, the start exponent v (a power of two, multiple of h), the step count, the Barrett length ell"""
    h = VD_H; K = -(-(m + 1) // h); n1 = K * h
    assert n1 >= m + 1
    Lx = pad23(2 * K)
    Le = pad23(3 * K - 1) if 3 * K - 1 <= 3 << 32 else None
    top = 255; zc = 0
    while top > 0 and not ebit(E, top): top -= 1; zc += 1
    v = 1; bit = top; vb = 0
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1; vb += 1
    for _ in range(VSHIFT):
        assert ebit(E, bit) == 0
        v >>= 1; bit += 1
    assert v & (v - 1) == 0 and v % h == 0
    ell = v + n1 - m + 1
    Kq = -(-ell // h); Lq = pad23(Kq + K - 1)
    return dict(h=h, K=K, n1=n1, Lx=Lx, Le=Le, v=v, steps=bit, top=top, zc=zc, vb=vb, ell=ell, Kq=Kq, Lq=Lq, nset=sum(ebit(E, i) for i in range(bit)))


def vd_conv(Pl, kin, outlen):
    """one cyclic convolution of one row (kin live inputs) with a stored kernel spectrum, 5 for the position loop and the address"""
    if Pl.rows == 1:
        z = Pl.N - kin
        return 5 + 2 * z + for8(z) + conv_core_row(Pl, 'mul')
    return 5 + stageA_fwd(Pl, kin) + 3 * conv_core_row(Pl, 'mul') + 2 + stageA_inv(Pl, outlen)


def vd_rows(cnt, rows, per, over):
    """rows of cnt elements copied between the coset arrays and the group buffer (strided), per element `per`, per row `over`, eight-element loops"""
    return rows * (over + for8(cnt) + per * cnt) + 3 * rows + 2


def vd_phase(per_group):
    ng = VD_H // VCNT
    return ng * (VD_GROUP + per_group) + 3 * ng + 2


def vd_reset(rows): return 7 * rows + 2


def vd_ext(K, Px):
    """the geometric phase of one extension O1 -> O2 or O2 -> O1: K rows in with running factors, one convolution per position, K rows out with running factors"""
    return 2 * vd_reset(K) + vd_phase(vd_rows(VCNT, K, 7, VD_ROW) + VCNT * vd_conv(Px, K, 2 * K) + vd_rows(VCNT, K, 7, VD_ROW))


def vd_eval(kin, kout, Pl):
    """chirp evaluation of kin coefficient rows at kout geometric nodes"""
    return vd_reset(kout) + vd_phase(vd_rows(VCNT, kin, 6, VD_ROWC) + VCNT * vd_conv(Pl, kin, kin + kout - 1) + vd_rows(VCNT, kout, 7, VD_ROW))


def vd_interp(K, Px):
    """interpolation at the K geometric nodes back to coefficient rows: two chirp correlations and the move of the K intermediate results"""
    mid = vd_conv(Px, K, 2 * K - 1) + 7 * K + for8(K) + 4 + vd_conv(Px, K, 2 * K)
    return vd_reset(K) + vd_phase(vd_rows(VCNT, K, 7, VD_ROW) + VCNT * mid + vd_rows(VCNT, K, 6, VD_ROWC))


def vd_inner(ncos, inv, PH):
    """ncos inner transforms of h points, one per coset, in place"""
    one = inv_passes(PH, PH.np - 1) if inv else fwd_passes(PH, PH.np)
    return ncos * (one + VD_CALL) + 3 * ncos + 2


def vd_pw(ncos, per):
    """a pointwise pass over ncos cosets of h values, `per` operations per element"""
    return ncos * (VD_PWC + for8(VD_H) + per * VD_H) + 3 * ncos + 2


def vd_batch_inv(ncos):
    """-1/g on O1 in place, coset by coset (Montgomery's batch inversion): prefix products, one inversion with its zero test, the backward pass"""
    h = VD_H
    return ncos * (20 + for8(h) + 5 * h + vd_inv1() + 2 + for8(h) + 9 * h) + 3 * ncos + 2


def vd_spectrum(Pl, nent):
    """the stored spectrum of a fixed kernel of nent entries (each one inversion and 20 operations), zero-filled and transformed"""
    c = nent * (vd_inv1() + 20) + 4
    if Pl.rows == 1:
        z = Pl.N - nent
        return c + 2 * z + for8(z) + fwd_passes(Pl, Pl.np)
    return c + stageA_fwd(Pl, nent) + 3 * fwd_passes(Pl, Pl.np)


def powx_vd(m, b, sg, E=PM1H, mulc=None, peak=None, tab_side=1):
    """stage C in the value domain.  Entry: g in coefficient form in the caller's array sg of n1 slots (its slots above m are zeroed here).
    Exit: R = S^E mod g in an array of n1 slots (the first allocation of the stage, low end) and g in coefficient form in sg; both go to stage D.
    mulc / peak: the block-product charge and its workspace walk used for the Newton reciprocal and the product for q (default: this ledger's
    conv_mulc_otf / product_peak of 4.5; the validation mode passes Jbenisek's).  Returns (Tr, info)."""
    mulc = mulc or conv_mulc_otf; peak = peak or product_peak
    T = Tr(b)
    d = vd_dims(m, E)
    h, K, n1, ell, Kq = d['h'], d['K'], d['n1'], d['ell'], d['Kq']
    assert int(sg) == n1
    PH, c0 = make_plan(1, 32); assert PH.N == h
    Px, c1 = vd_plan(d['Lx']); Pq, c2 = vd_plan(d['Lq'])
    Pe, c3 = vd_plan(d['Le']) if d['Le'] else (None, 0)
    T.ctl(c0 + c1 + c2 + c3)
    T.ctl(12 * d['zc'] + 25 * d['vb'] + 4 * VSHIFT)                       # the exponent: its leading bit, the start monomial, the shift
    spec = [(Px, 2 * K), (Pq, Kq + K - 1), (Px, 2 * K - 1), (Px, K + 1)]  # the extension kernel, the chirp of the evaluation of q, the chirp of the interpolation, the coefficients of M2 (the interpolation at the nodes of O2)
    if Pe: spec.append((Pe, 3 * K - 1))                                  # the chirp of the evaluation of g at the 2K nodes
    NTAB = VD_NTAB * K
    sTab = T.new_fp(NTAB + h + sum(P_.N for P_, _ in spec), tab_side, 'vd_tab')   # the tables (the omega table alone has 2^32 entries) exceed the pool threshold at r <= 14 and then take the high end of the pool; the group buffer and its row are slab blocks at every r
    T.ctl(NTAB * (2 * vd_inv1() + 60) + 10 * h + sum(vd_spectrum(P_, n_) for P_, n_ in spec))
    Lmax = max(P_.N for P_, _ in spec)
    sB1 = T.new_fp(VCNT * Lmax, tab_side, 'vd_buf')                       # the group buffer: one row of Lmax elements per position
    sBT = T.new_fp(Lmax, tab_side, 'vd_bufT') if any(P_.rows == 3 for P_, _ in spec) else None
    zg = n1 - (m + 1); T.st(zg); T.ctl(for8(zg))                         # the slots of g above its m + 1 coefficients are zeroed
    sR2 = T.new_fp(n1, 0, 'vd_R2')                                        # R on O2, then R in coefficient form for stage D
    sR1 = T.new_fp(n1, 0, 'vd_R1')                                        # q (its first ell elements) in steps 1-3, then R~ on O1
    # (1) Barrett start: the reciprocal of the reversed g modulo X^ell (Newton), then q = floor(X^v P1 / g) by one product; the block products of 4.5
    # with the chunk bound and workspace cap of the kind `newton`
    CTX['cf'] = CF.get('newton'); CTX['acap'] = ACAP.get('newton')
    sG = T.new_fp(ell, 1, 'vd_G'); sM = T.new_fp(ell, 1, 'vd_M'); sY = T.new_fp(ell, 1, 'vd_Y')
    Lr = ell
    T.ld(Lr); T.st(Lr); T.loopc(Lr); T.ctl(Lr)                           # the reversed top ell coefficients of g
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < Lr:
        l2 = min(2 * l, Lr)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(mulc(P1, l, l2, 0, l2))
        assert P1.a > 32 or P1.N <= Lr
        if P1.a > 32: peak(T, P1)
        T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(mulc(P2, l2 - l, l, 0, l2 - l))
        assert P2.a > 32 or P2.N <= Lr
        if P2.a > 32: peak(T, P2)
        T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    newton_ops = T.ops
    T.free(sY); T.free(sG)
    sTt = T.new_fp(ell, 1, 'vd_Tt')
    T.st(ell); T.ctl(for8(ell)); T.ctl(Kq * (vd_inv1() + 30))              # rev(X^v P1) mod X^ell: zero fill, the Kq coefficients mu_i at the multiples of h
    PQ, c = plan3_for_len(2 * ell - 1); T.ctl(c)
    T.ctl(mulc(PQ, ell, ell, 0, ell))                                     # q (reversed) into the first ell elements of R1
    if PQ.a > 32: peak(T, PQ)
    T.ctl(plan_invN_ops(PQ))
    T.free(sTt); T.free(sM)
    T.ld(ell); T.st(ell); T.loopc(ell // 2); T.ctl(2 * (ell // 2))          # q reversed in place
    CTX['cf'] = None; CTX['acap'] = None
    q_ops = T.ops - newton_ops
    # (2) g on O1 (array G1) and on O2 (in place in the array of g): chirp evaluation of the K coefficient rows at the 2K nodes, 2K forward inner transforms
    sG1 = T.new_fp(n1, 0, 'vd_G1')
    ev_g = vd_eval(K, 2 * K, Pe) if Pe else 2 * vd_eval(K, K, Px)
    inner_g = vd_inner(2 * K, False, PH)
    T.ctl(ev_g + inner_g)
    # (3) R~_0 = X^v P1 mod g on O2: q at the K nodes of O2 into R2, forward inner transforms, R2 := u_k^v M(n_k) - R2 G2 (8 per element)
    zq = Kq * h - ell; T.st(zq); T.ctl(for8(zq))
    st3 = vd_eval(Kq, K, Pq) + vd_inner(K, False, PH) + vd_pw(K, 8); T.ctl(st3)
    # (4) R~_0 on O1: inverse inner transforms of R2 into R1, the extension O2 -> O1 on R1, forward inner transforms
    ext = vd_inner(K, True, PH) + vd_ext(K, Px) + vd_inner(K, False, PH)
    T.ctl(ext)
    # (5) -1/g on O1 in place in G1 (an auxiliary array of h elements); a zero prefix product ends the trial (9.2(f))
    sAux = T.new_fp(h, 0, 'vd_aux'); st5 = vd_batch_inv(K); T.ctl(st5); T.free(sAux)
    # (6) the loop: R1 := R1^2 G1 (8); extension O1 -> O2; R2 := x^b (R2^2 + R1 G2) / M(n_k) (12; 16 when b = 1); extension O2 -> O1; 20 per step
    step0 = vd_pw(K, 8) + ext + vd_pw(K, 12) + ext + 20
    step1 = vd_pw(K, 8) + ext + vd_pw(K, 16) + ext + 20
    steps, nset = d['steps'], d['nset']
    T.ctl((steps - nset) * step0 + nset * step1)
    # (7) leaving the Montgomery form: R1 := R1 G1 (7), extension O1 -> O2, R2 := (R2 + R1 G2) / M(n_k) (11)
    st7 = vd_pw(K, 7) + ext + vd_pw(K, 11); T.ctl(st7)
    T.free(sR1); T.free(sG1)
    # (8) R (in R2) and g (in its array) to coefficient form in place: inverse inner transforms, interpolation at the K nodes of O2
    interp = vd_inner(K, True, PH) + vd_interp(K, Px)
    T.ctl(2 * interp)
    if sBT is not None: T.free(sBT)
    T.free(sB1); T.free(sTab)
    T.ctl(2 + 500)
    VD.clear(); VD.update(d, ext=ext, step0=step0, step1=step1, interp=interp, Lmax=Lmax, NTAB=NTAB, spec_len=sum(P_.N for P_, _ in spec), newton=newton_ops, q=q_ops, ev_g=ev_g, inner_g=inner_g,
                          st3=st3, st5=st5, st7=st7, loop=(steps - nset) * step0 + nset * step1, geo=vd_ext(K, Px), inner_f=fwd_passes(PH, PH.np), inner_i=inv_passes(PH, PH.np - 1),
                          tables=NTAB * (2 * vd_inv1() + 60) + 10 * h + sum(vd_spectrum(P_, n_) for P_, n_ in spec))
    info = dict(steps=steps, nset=nset, step=step0, mulx=step1 - step0, BIG=True, F=sR2, vd=dict(VD))
    return T, info


# ---------------------------------------------------------------- validation: Jbenisek's row C (7b276afd and its r = 17-19, 21 siblings), with his charges
JB_C = {16: 315694368193453406618, 17: 1401025390875007771940, 18: 7631016575947362265783, 19: 47791743731725187002589, 20: 207611124658151579699613, 21: 1125652627902830084736451}


def check_jb(r, verbose=True):
    """reproduce Jbenisek's asserted row C: his block products for the set-up, his allocation charge (no statistics 64), base 3, + 1,000 stage bookkeeping"""
    m = (5 ** (6 + r) - 1) // 2
    global ALLOC_STAT
    ALLOC_STAT = 0
    try:
        TRACE['log'] = None
        d = vd_dims(m)
        A = Tr(1); sg = A.new_fp(d['n1'], 0, 'g')
        C, info = powx_vd(m, 3, sg, mulc=jb_mulc_otf, peak=jb_product_peak, tab_side=0)
        C.ctl(STAGE_BK)
    finally:
        ALLOC_STAT = 64
    ok = C.ops == JB_C.get(r)
    if verbose:
        v = info['vd']
        f = lambda x: format(x, ',')
        print('r = %d: K = %s, n1 = %s, Lx = %s, Le = %s, v = 2^%d, steps %d (%d with b = 1), ell = %s, Kq = %s, Lq = %s' % (
            r, f(v['K']), f(v['n1']), f(v['Lx']), v['Le'] and f(v['Le']), v['v'].bit_length() - 1, v['steps'], v['nset'], f(v['ell']), f(v['Kq']), f(v['Lq'])))
        print('  inner transform fwd / inv %s / %s; geometric phase of one extension %s (%.3f per element of n1); one extension %s' % (
            f(v['inner_f']), f(v['inner_i']), f(v['geo']), v['geo'] / v['n1'], f(v['ext'])))
        print('  step b = 0 / 1: %s / %s; tables %s; Newton %s; product for q %s; eval g %s; 2K inner of g %s; step 3 %s; step 4 %s; step 5 %s; loop %s; step 7 %s; step 8 %s' % (
            f(v['step0']), f(v['step1']), f(v['tables']), f(v['newton']), f(v['q']), f(v['ev_g']), f(v['inner_g']), f(v['st3']), f(v['ext']), f(v['st5']), f(v['loop']), f(v['st7']), f(2 * v['interp'])))
        print('  row C = %s   (Jbenisek asserts %s)  match: %s' % (f(C.ops), f(JB_C.get(r, 0)), ok))
    return C.ops, ok



# ---------------------------------------------------------------- stage D: the half-gcd (section 4.4 of e6dcb600), the normal remainder sequence
ABORT_TEST = 2


def dupv(ln, b):
    T = Tr(b); s = T.new_fp(ln if ln else 1, 0, 'dup')
    T.ld(ln); T.st(ln); T.loopc(ln)
    return T, s


def trim(it): return 11 * it


def divrem_naive(lx, ly, term_zero=0):
    c = 3
    la, lb = lx, ly
    assert la == lb + 1
    if lb >= 2:
        c += powcost(PM2) + INV_CTL + 3 + 1
        c += 2 * 3 + 2 * 2 + 6
        c += 2 * (lb - 1) + 2 * max(lb - 2, 0)
        c += 4 * (lb - 1) + 2 * (lb - 1) + 3 * (lb - 1) + 2 + 4 + 2 * (lb - 1)
        it = 1 + term_zero * (lb - 1)
        c += trim(it)
        return c, 2, lb - 1 - term_zero * (lb - 1), it
    c += 2 * la + 2 * la + 3 * la + 2
    c += powcost(PM2) + INV_CTL
    c += (la - lb + 1) * (1 + 2 + 2 + 2 + 7)
    c += trim(1)
    return c, la - lb + 1, 0, 1


def mat_identity(b):
    T = Tr(b); sl = [T.new_fp(1, 0, 'id') for _ in range(4)]
    T.st(2)
    return T, [1, 0, 0, 1], sl


def mat_free(T, sl):
    for s in sl:
        if s: T.free(s)


def mul_add_q2(T, le, lf, side=0):
    lt = le + 1 if le else 0
    lo = max(lt, lf)
    s = T.new_fp(lo if lo else 1, side, 'maq')
    muls = le + max(le - 1, 0) + (1 if le > 0 else 0)
    adds = max(le - 1, 0) + (min(lf, le + 1) if le > 0 else 0)
    T.ops += muls + adds
    T.ld(le + lf); T.st(lo); T.loopc(lo); T.ctl(8 + 8 * lo)
    T.ctl(trim(1))
    return lo, s


def mat_mulQ(T, lens, sl, side=0):
    l0, s0 = mul_add_q2(T, lens[0], lens[1], side)
    l2, s2 = mul_add_q2(T, lens[2], lens[3], side)
    T.free(sl[1]); T.free(sl[3])
    return [l0, lens[0], l2, lens[2]], [s0, sl[0], s2, sl[2]]


def poly_mul_naive_cost(la, lb):
    return la * lb * 11 + (la * lb - (la + lb - 1)) + (la + lb - 1) * 11 + 2


def mat_mul(A, B, b, side=0):
    T = Tr(b); T.ctl(80)
    Al, Bl = A[0], B[0]
    Ls = [0] * 4
    for i in range(2):
        for j in range(2):
            l = 0
            for t in range(2):
                la, lb = Al[2 * i + t], Bl[2 * t + j]
                if la and lb and la + lb - 1 > l: l = la + lb - 1
            Ls[2 * i + j] = l
    Lmax = max(1, max(Ls))
    outl = [0] * 4; outs = [0] * 4
    if Lmax <= 48:
        for i in range(2):
            for j in range(2):
                l = Ls[2 * i + j]
                o = T.new_fp(l if l else 1)
                T.st(l); T.loopc(l)
                for t in range(2):
                    la, lb = Al[2 * i + t], Bl[2 * t + j]
                    if not la or not lb: continue
                    tmp = T.new_fp(la + lb - 1)
                    T.ops += poly_mul_naive_cost(la, lb)
                    T.ops += la + lb - 1
                    T.ld(2 * (la + lb - 1)); T.st(la + lb - 1); T.loopc(la + lb - 1)
                    T.free(tmp); T.ctl(6)
                T.ctl(trim(1))
                outl[2 * i + j] = l; outs[2 * i + j] = o
        return T, outl, outs, False
    Pl, c = plan3_for_len(Lmax); T.ctl(c)
    BIG = Pl.a > BIGA
    N = Pl.N
    if not BIG:
        ob = [T.new_fp(N, 1 - side, 'mm_ob') for _ in range(4)]               # work buffers on the end of the factors, then the row buffers (freed first)
        tH0 = T.new_fp(Pl.n, 1 - side, 'mm_tmp'); tH1 = T.new_fp(Pl.n, 1 - side, 'mm_tmp'); tS = T.new_fp(Pl.n, 1 - side, 'mm_tmp')
    groups = []
    for t in range(2):
        g = dict(H=[], S=[], prod={}); hj = [-1, -1]
        for j in range(2):
            if Bl[2 * t + j]:
                hj[j] = len(g['H']); g['H'].append(Bl[2 * t + j])
        for i in range(2):
            if Al[2 * i + t]:
                s = len(g['S']); g['S'].append(Al[2 * i + t])
                for j in range(2):
                    if hj[j] >= 0: g['prod'][(s, hj[j])] = (2 * i + j, 1)
        if g['H'] and g['S']: groups.append(g)
        T.ctl(20)
    CTX['cf'] = CF.get('D') if BIG else None
    CTX['acap'] = ACAP.get('D') if BIG else None
    cc, eps = conv_bilin_cost(Pl, 4, Ls, groups); T.ctl(cc)
    CTX['cf'] = None; CTX['acap'] = None
    if BIG:
        Pd = dict(PL)
        ob = [T.new_fp(Ls[k] if Ls[k] else 1, side, 'mm_out') for k in range(4)]
        for x in [T.new_fp(y, side, 'mm_tmp') for y in Pd['temps']]: T.free(x)
        for M_ in (A, B):
            for s_ in M_[1]:
                if s_: T.free(s_)
    else:
        T.free(tH0); T.free(tH1); T.free(tS)
    T.ctl(plan_invN_ops(Pl))
    for k in range(4):
        l = Ls[k]
        if BIG:
            T.ctl(3)
            if not eps[k]: T.st(l); T.loopc(l)
            outs[k] = ob[k]
            if l: T.ctl(trim(1))
            outl[k] = l
            continue
        o = T.new_fp(l if l else 1, side, 'mm_out'); T.ctl(3)
        if eps[k]:
            T.ops += l; T.ld(l); T.st(l); T.loopc(l)
        T.free(ob[k])
        outs[k] = o
        if l: T.ctl(trim(1))
        outl[k] = l
    return T, outl, outs, BIG


def fslots(m):
    return m + 1 if plan3_for_len(2 * m - 1)[0].a > BIGA else m


def apply_inv(Rl, Rs, h, la, lb, consume, b, side=0):
    T = Tr(b)
    nres = la
    Pl, c = plan3_for_len(nres); T.ctl(c)
    N = Pl.N
    BIG = Pl.a > BIGA
    if BIG:
        lc0 = la - h; ld0 = lc0 - 1
        sd_ = T.new_fp(ld0, side, 'ai_out'); sc_ = T.new_fp(lc0, side, 'ai_out')     # d first: c is freed first
    else:
        sd_ = T.new_fp(N, side, 'ai_out'); sc_ = T.new_fp(N, side, 'ai_out')       # outputs first, then the two row buffers (freed first)
        tH = T.new_fp(Pl.n, side, 'ai_tmp'); tS = T.new_fp(Pl.n, side, 'ai_tmp')
    sgn = -1 if (h & 1) else 1
    T.ctl(60)
    ec = [3, 1]; ed = [2, 0]; sc = [sgn, -sgn]; sd = [-sgn, sgn]
    lV = [la, lb]
    groups = []
    for v in range(2):
        g = dict(H=[lV[v]], S=[], prod={})
        if not lV[v]: continue
        if Rl[ec[v]]:
            g['prod'][(len(g['S']), 0)] = (0, sc[v]); g['S'].append(Rl[ec[v]])
        if Rl[ed[v]]:
            g['prod'][(len(g['S']), 0)] = (1, sd[v]); g['S'].append(Rl[ed[v]])
        if g['S']: groups.append(g)
        T.ctl(10)
    if BIG:
        CTX['ltrue'] = [lc0, ld0]; CTX['cf'] = CF.get('D')
        CTX['acap'] = ACAP.get('D')
    cc, eps = conv_bilin_cost(Pl, 2, [lc0, ld0] if BIG else [nres, nres], groups); T.ctl(cc)
    CTX['ltrue'] = None; CTX['cf'] = None; CTX['acap'] = None
    if BIG:
        Pa = dict(PL)
        for x in [T.new_fp(y, side, 'ai_tmp') for y in Pa['temps']]: T.free(x)
        if consume: mat_free(T, Rs)
    else:
        T.free(tH); T.free(tS)
        if consume: mat_free(T, Rs)
    T.ctl(plan_invN_ops(Pl))
    for k in range(2):
        T.ctl(3)
        if not eps[k]:
            T.st(nres); T.loopc(nres); continue
        if BIG: continue
        if eps[k] < 0: T.ops += 1
        T.ops += nres; T.ld(nres); T.st(nres); T.loopc(nres)
    lc = la - h; ld = lc - 1
    T.ctl(trim(1) + trim(1) if BIG else trim(1 + (nres - lc)) + trim(1 + (nres - ld)))
    return T, lc, sc_, ld, sd_


HCACHE = {}
GSIDE = [0]
INPLACE_NB = [False, False]     # also write the remainder over a longer (transform-length) dividend array: [in the half-gcd, in the outer driver]
LCUT = [None]          # when tracing: calls with la > LCUT run live (their events go to the log), the others are cached and summarised


def hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys=0):
    if TRACE['log'] is not None and TRACE['depth'] == 0 and la > LCUT[0]:
        return _hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys)
    key = (la, int(sa), lb, int(sb), k, want_mat, own, wc, wd, b)
    r = HCACHE.get(key)
    if r is None:
        TRACE['depth'] += 1
        try:
            r = _hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys)
        finally:
            TRACE['depth'] -= 1
        HCACHE[key] = r
    return r


def _hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys=0):
    DEPTH[0] += 1
    try:
        return _hgcd_body(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys)
    finally:
        DEPTH[0] -= 1


def _hgcd_body(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys):
    """returns (Tr, (lc, sc, ld, sd, Rl, Rs, h)).  ys: the end of the pool for the results.  A call that returns a pair (and no matrix) owns its
    inputs, which lie on ys: its first call returns R1 on ys, its own arrays go to the other end, the final pair to ys.  A call that returns a
    matrix keeps its arrays and its matrix on ys and has its two calls return their matrices on the other end."""
    pairnode = (wc or wd) and not want_mat
    own_side = 1 - ys if pairnode else ys
    T = Tr(b); T.ctl(40)
    n = la - 1
    Rl = Rs = None
    if lb == 0 or n - (lb - 1) > k:
        if want_mat:
            t, Rl, Rs = mat_identity(T.here()); T.add(t)
        T.ctl(4)
        lc = sc = ld = sd = None
        if wc:
            if own & 1: sc = sa
            else:
                t, sc = dupv(la, T.here()); T.add(t)
            lc = la
        elif own & 1: T.free(sa)
        if wd:
            if own & 2: sd = sb
            else:
                t, sd = dupv(lb, T.here()); T.add(t)
            ld = lb
        elif own & 2: T.free(sb)
        return T, (lc, sc, ld, sd, Rl, Rs, 0)
    if k <= 96:
        return hgcd_base(la, sa, lb, sb, k, want_mat, own, wc, wd, T)
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    las = la - s; lbs = lb - s if lb > s else 0
    t1, o1 = hgcd(las, 0, lbs, 0, k1, 1, 0, False, False, T.here(), ys if pairnode else 1 - ys)
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    T.ctl(ABORT_TEST)
    assert h1 >= 1, 'non-generic shape'
    t2, lcc, scc, ldd, sdd = apply_inv(R1l, R1s, h1, la, lb, not want_mat, T.here(), own_side)
    T.add(t2); T.ctl(4)
    if own & 1: T.free(sa)
    if own & 2: T.free(sb)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    if ldd == 0 or (lcc - ldd) > k2:
        if want_mat: Rl, Rs = R1l, R1s
        lc = sc = ld = sd = None
        if wc: lc, sc = lcc, scc
        else: T.free(scc)
        if wd: ld, sd = ldd, sdd
        else: T.free(sdd)
        return T, (lc, sc, ld, sd, Rl, Rs, h1)
    dq = lcc - ldd
    sq = T.new_fp(dq + 1, own_side, 'div_q')
    inplace = int(scc) == lcc or (INPLACE_NB[0] and int(scc) > lcc)
    if inplace:
        srm = scc; T.charge_alloc_free()  # the remainder c - q d is written over c (dead after the division); the allocation and free it replaces stay charged
    else:
        srm = T.new_fp(lcc, own_side, 'div_r')
    T.ctl(3)
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)
    T.ctl(dc + ABORT_TEST)
    if not inplace: T.free(scc)
    k3 = k2 - dq
    s3 = (ldd - 1) - 2 * k3
    if s3 > 0:
        # the truncated second call: the top 2 k3 + 1 coefficients of (d, r), matrix only; R2^-1 applied to the whole pair only if the caller wants it
        t3, o3 = hgcd(ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here(), 1 - own_side if not pairnode else 1 - ys)
        T.add(t3)
        R2l, R2s, h3 = o3[4], o3[5], o3[6]
        T.ctl(ABORT_TEST)
        lc3 = sc3 = ld3 = sd3 = None
        if wc or wd:
            t4, lc4, sc4, ld4, sd4 = apply_inv(R2l, R2s, h3, ldd, lrem, not want_mat, T.here(), ys)
            T.add(t4); T.ctl(4)
            T.free(sdd); T.free(srm)
            if wc: lc3, sc3 = lc4, sc4
            else: T.free(sc4)
            if wd: ld3, sd3 = ld4, sd4
            else: T.free(sd4)
        else:
            T.free(sdd); T.free(srm)
            if not want_mat: mat_free(T, R2s)
        o3 = (lc3, sc3, ld3, sd3, R2l, R2s, h3)
    else:
        t3, o3 = hgcd(ldd, sdd, lrem, srm, k3, want_mat, 3, wc, wd, T.here(), own_side)
        T.add(t3); T.ctl(ABORT_TEST)
    h = h1 + dq + o3[6]
    if want_mat:
        R1l2, R1s2 = mat_mulQ(T, R1l, R1s, 1 - ys)
        tm, Ml, Ms, cons = mat_mul((R1l2, R1s2), (o3[4], o3[5]), T.here(), ys); T.add(tm)
        if not cons:
            mat_free(T, o3[5]); mat_free(T, R1s2)
        Rl, Rs = Ml, Ms
    T.free(sq)
    return T, (o3[0], o3[1], o3[2], o3[3], Rl, Rs, h)


def hgcd_base(la, sa, lb, sb, k, want_mat, own, wc, wd, T):
    if own & 1: sx = sa
    else:
        t, sx = dupv(la, T.here()); T.add(t)
    if own & 2: sy = sb
    else:
        t, sy = dupv(lb, T.here()); T.add(t)
    lx, ly, ssum = la, lb, 0
    Rl = Rs = None
    if want_mat:
        t, Rl, Rs = mat_identity(T.here()); T.add(t)
    while ly > 0:
        dq = lx - ly
        T.ctl(6)
        if dq > k - ssum: break
        sq = T.new_fp(dq + 1, 0, 'base_q'); sr = T.new_fp(lx, 0, 'base_r')
        dc, lq, lr, _ = divrem_naive(lx, ly)
        T.ctl(dc + ABORT_TEST)
        if want_mat:
            Rl, Rs = mat_mulQ(T, Rl, Rs)
        ssum += dq
        T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
        T.free(sq)
    lc = sc = ld = sd = None
    if wc: lc, sc = lx, sx
    else: T.free(sx)
    if wd: ld, sd = ly, sy
    else: T.free(sy)
    return T, (lc, sc, ld, sd, Rl, Rs, ssum)


def gcd_cost(m, dG, b, gS, FS):
    """poly_gcd_own(g, R - 1) on the normal remainder sequence, gcd of degree dG; gS, FS: the arrays g (m + 1) and F"""
    T = Tr(b)
    lx, ly = m + 1, m
    sx = gS; sy = FS
    T.ctl(3); T.ctl(3)
    while ly > 0:
        T.ctl(2)
        n = lx - 1
        T.ctl(4)
        if n <= 2 * 96:
            sq = T.new_fp(lx - ly + 1, 0, 'gcd_q'); sr = T.new_fp(lx, 0, 'gcd_r')
            last = (ly == dG + 1)
            dc, lq, lr, _ = divrem_naive(lx, ly, term_zero=1 if (last and dG >= 1) else 0)
            if last and dG == 0:
                lr = 0
            T.ctl(dc + ABORT_TEST)
            T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
            T.free(sq); T.ctl(5)
            continue
        k = (n + 1) // 2
        t, o = hgcd(lx, sx, ly, sy, k, False, 3, True, True, T.here(), GSIDE[0])
        T.add(t)
        lc, sc, ld, sd = o[0], o[1], o[2], o[3]
        T.ctl(ABORT_TEST)
        T.ctl(2)
        sq = T.new_fp(lc - ld + 1, 0, 'gcd_q')
        inplace = int(sc) == lc or (INPLACE_NB[1] and int(sc) > lc)
        if inplace:
            sr = sc; T.charge_alloc_free()   # the remainder is written over c (dead after the division); the allocation and free stay charged
        else:
            sr = T.new_fp(lc, GSIDE[0], 'gcd_r')
        T.ctl(3)
        dc, lq, lr, _ = divrem_naive(lc, ld)
        T.ctl(dc + ABORT_TEST)
        if not inplace: T.free(sc)
        T.free(sq)
        sx = sd; lx = ld; sy = sr; ly = lr; T.ctl(5)
    T.free(sy)
    T.ctl(2)
    T.ops += powcost(PM2); T.ctl(INV_CTL); T.ld(1)
    T.ops += lx - 1
    T.ld(lx); T.st(lx); T.loopc(lx)
    return T, (lx, sx)


# ---------------------------------------------------------------- the allocator (section 7): a two-ended first-fit pool for blocks of more than 2^BIG_EXP bytes,
# slab classes (slots of 2^j bytes, j >= 7, a free list per class, new slots from the end of the slab area) for the others
class FirstFit:
    """one end of the pool: blocks [size, sid] (sid None = free) in address order from this end; no two free blocks adjacent; the unused middle
    lies beyond the last block.  An allocation takes the first free block (from this end) with at least `need` bytes, cuts it on the side nearest
    this end and leaves the rest free if it is at least 128 bytes; otherwise it extends this end into the middle.  A free merges with free
    neighbours and, if it is the outermost block, with the middle."""
    def __init__(self):
        self.L = []; self.end = 0; self.scans = 0; self.maxblocks = 0

    def alloc(self, sid, need):
        L = self.L
        for k in range(len(L)):
            b = L[k]
            if b[1] is None and b[0] >= need:
                rem = b[0] - need; b[1] = sid
                if rem >= 128:
                    b[0] = need; L.insert(k + 1, [rem, None])
                self.scans += k + 1
                return
        self.scans += len(L) + 1
        L.append([need, sid]); self.end += need
        self.maxblocks = max(self.maxblocks, len(L))

    def free(self, sid):
        L = self.L
        k = next(i for i in range(len(L)) if L[i][1] == sid)
        L[k][1] = None
        if k + 1 < len(L) and L[k + 1][1] is None:
            L[k][0] += L[k + 1][0]; del L[k + 1]
        if k > 0 and L[k - 1][1] is None:
            L[k - 1][0] += L[k][0]; del L[k]; k -= 1
        if k == len(L) - 1:
            self.end -= L[k][0]; del L[k]


DEBUG_SNAP = [False, None]


def simulate(stages):
    """stages: [(name, events)] in program order.  Returns the pool high-water (largest sum of the two ends), per stage, the slab area and class peaks."""
    ends = (FirstFit(), FirstFit()); where = {}
    high = 0; per = {}
    ccur = {}; cpk = {}
    snap_init = None
    for name, ev in stages:
        for e in ev:
            t = e[0]
            if t == 'A':
                where[e[1]] = e[3]; ends[e[3]].alloc(e[1], e[2])
                if ends[0].end + ends[1].end > high:
                    high = ends[0].end + ends[1].end
                    if DEBUG_SNAP[0]: DEBUG_SNAP[1] = (name, [list(b) for b in ends[0].L], [list(b) for b in ends[1].L])
            elif t == 'F':
                ends[where.pop(e[1])].free(e[1])
            elif t == 'a':
                v = ccur.get(e[1], 0) + 1; ccur[e[1]] = v; cpk[e[1]] = max(cpk.get(e[1], 0), v)
            elif t == 'f':
                ccur[e[1]] = ccur.get(e[1], 0) - 1
            else:
                _, sc, sp = e
                for c in set(sc) | set(sp):
                    cpk[c] = max(cpk.get(c, 0), ccur.get(c, 0) + sp.get(c, 0)); ccur[c] = ccur.get(c, 0) + sc.get(c, 0)
        per[name] = high
        if name == 'init':
            snap_init = (tuple(tuple(b) for b in ends[0].L), tuple(tuple(b) for b in ends[1].L), {c: v for c, v in ccur.items() if v})
    snap_end = (tuple(tuple(b) for b in ends[0].L), tuple(tuple(b) for b in ends[1].L), {c: v for c, v in ccur.items() if v})
    assert snap_end == snap_init, 'a trial does not return the allocator to its state after init'
    slab = sum(v << c for c, v in cpk.items())
    return dict(high=high, per=per, slab=slab, cpk=dict(sorted(cpk.items())), scans=ends[0].scans + ends[1].scans,
                maxblocks=ends[0].maxblocks + ends[1].maxblocks)


QE_BYTES = 16 * 1024 + 512        # stages E and later: at most 16 live arrays of at most 17 elements (1,024-byte slots) and the allocator's 36 words
IMAGE_EXTRA = 399216 + 32 + 4851196
CODE_EXTRA = 65536                # code of the outer-transform kernels and of the one-row block transform added by the lean stages (an allowance)
STACK = 65536


def ceil3(x): return math.ceil(x * 1000) / 1000
def ceil5(x): return math.ceil(x * 100000 - 1e-6) / 100000


def twiddle_slots(m):
    a = 2
    while 3 * (1 << a) < 2 * m - 1: a += 1
    return (1 << min(a, BIGA)) // 2


def corr_len(kappa):
    return min(v for a in range(1, 64) for v in (1 << a, 3 << a) if v >= 2 * kappa - 1)


F_FIRST = [True]


def n_steps(m, E=PM1H):
    top = E.bit_length() - 1; v = 1; bit = top
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1
    return bit


def stage_AB(m, solve_ws=True, vd=False):
    """the arrays before stage C: the twiddle table (init), g (stage A; n1 slots in the value-domain stage, 4.6), the coset array of stage B with the
    workspace of the geometric solve (block mode) or the inverse-transform array (one transform), then F (coefficient-domain stage C only)"""
    I = Tr(0); I.new_fp(twiddle_slots(m), 0, 'tw')
    A = Tr(1); sg = A.new_fp(vd_dims(m)['n1'] if vd else m + 1, 0, 'g')
    B = Tr(2)
    if m + 1 > (1 << BIGA):
        Pl = make_plan(3, BIGA - 1)[0]; ncos = -(-(m + 1) // Pl.N); H = ncos * Pl.N
        sb = B.new_fp(H, 0, 'H')
        if solve_ws:
            S = corr_len(ncos)
            sw = B.new_fp(4 * S + 3 * ncos, 1, 'ws')      # chirp and mu transforms, correlation buffer, transform scratch, three arrays of kappa constants
            B.free(sw)
        if vd:
            B.free(sb)
            return I, A, B, sg, None
        if F_FIRST[0] and n_steps(m) % 2 == 1 and plan3_for_len(2 * m - 1)[0].a > BIGA:
            # an odd number of squaring steps: F is taken before the coset array is freed, so that F alternates back into the slot next to g
            sF = B.new_fp(fslots(m), 0, 'F'); B.free(sb)
            return I, A, B, sg, sF
        B.free(sb)
    else:
        H = min(v for a in range(2, 64) for v in (1 << a, 3 << a) if v >= m + 1)
        sb = B.new_fp(H, 0, 'H'); B.free(sb)
        if vd: return I, A, B, sg, None
    sF = B.new_fp(fslots(m), 0, 'F')
    return I, A, B, sg, sF


# ---------------------------------------------------------------- the rows that this ledger does not expand: Jbenisek's entries at each r (section 6 there)
ROWS = {   # r: (C(r), fixed = [init, setup, plan_invN misses, H, I], A, B, E, F, G, trial loop, source entry)
    6: (342, [536889025, 4910, 80314, 5644, 3384436], 1196, 202448149150, '18369013'),
    7: (363, [2147501759, 4910, 86492, 5644, 3384436], 1196, 858062870469, 'df42fe1f'),
    8: (384, [8589952701, 4910, 92670, 5644, 3384436], 1196, 3656592954235, '7d53191b'),
    9: (405, None, 1196, 23115473037075, 'e76bdab0'),
    10: (426, None, 1196, 97164545020652, '418d61f1'),
    11: (447, None, 1196, 539088909426379, '9562cddb'),
    12: (468, None, 1196, 3655884838496434, '048f4110'),
    13: (489, None, 1196, 19262428006970633, 'd57ebc31'),
    14: (510, None, 1196, 107946671426269314, '299f77ac'),
    15: (531, None, 1196, 626993782321806337, 'c5aaccf4'),
    16: (552, None, 1196, 3036821731738006548, '1ebf2b44'),
    # r = 16-21: the rows of Jbenisek's value-domain entries (B is 186 operations below his earlier entries' B at each r)
    17: (573, None, 1196, 16824333175932967600, '628641e6'),
    18: (594, None, 1196, 97722233724525086001, '1b8cd7a6'),
    19: (615, None, 1196, 461146671982189275566, 'f4f93349'),
    20: (636, None, 1196, 2534607690146512986054, '7b276afd'),
    21: (657, None, 1196, 14724903587095649952430, '86db9605'),
}
FIXED_BIG = [17179887292, 4910, 95759, 5644, 3384436]
E_CAP, F_ROW, TRIAL_EXTRA, OFFLINE = 166079773, 47012, 12, 1000000
PLAN_EXTRA = 95759                 # e6dcb600: a second allowance for the plan_invN misses (the plans of the lean products differ)
STAT_EXTRA = 64 * 10 ** 10         # e6dcb600: per trial, the flat 64 of the allocator statistics for at most 10^10 calls in rows A, B, E, F, G
B_ALLOC_EXTRA = 10000
RESET_EXTRA = 1000                 # this package: the reset of the allocator after an ABORT (section 6, row 'ABORT reset')              # this package: the allocation and free of the coset-solve workspace added to the walk of stage B (an allowance)
CF_E6 = dict(sq=0.375, q=0.18, qg=0.70, newton=0.25, D=0.06)


def g_row(Cr): return 1000 + 10 * 2 * Cr + 32


def run(r, cf=None, trace=False, big_exp=None, lcut_shift=3, quiet=False, solve_ws=True, acap=None, vd=True):
    m = (5 ** (6 + r) - 1) // 2
    cf = dict(CF_E6 if cf is None else cf)
    CF.clear(); CF.update({k: (v if isinstance(v, int) else int(v * m)) for k, v in cf.items()})
    ACAP.clear(); ACAP.update({k: (v if isinstance(v, int) else int(v * m)) for k, v in (acap or {}).items()})
    HCACHE.clear(); MODE_LOG.clear()
    res = {}
    if trace:
        TRACE['log'] = []; TRACE['depth'] = 0; TRACE['sid'] = 0
        TRACE['big'] = 1 << big_exp
        LCUT[0] = (1 << big_exp) >> (5 + lcut_shift)
    try:
        I, A, B, sg, sF = stage_AB(m, solve_ws, vd)
        evAB = None
        if trace:
            evAB = list(TRACE['log']); TRACE['log'].clear()
            # split the A/B log by stage: init = first event, A = second, B = the rest
            stages = [('init', evAB[:1]), ('A', evAB[1:2]), ('B', evAB[2:])]
        C, cinfo = powx_vd(m, 3, sg) if vd else powx_lean(m, 3, sF); C.ctl(STAGE_BK)
        if trace:
            stages.append(('C', list(TRACE['log']))); TRACE['log'].clear()
        D = Tr(3); D.ctl(STAGE_BK); D.ops += 1; D.ctl(11)
        t, (lg, sgg) = gcd_cost(m, 0, 3, sg, cinfo['F'])
        D.add(t); D.ctl(2); D.free(sgg)
        if trace:
            stages.append(('D', list(TRACE['log'])))
    finally:
        TRACE['log'] = None; TRACE['depth'] = 0
    twb = blk(twiddle_slots(m))     # the live set at the entry of a stage is what the earlier stages left (g; F or nothing)
    peaks = dict(A=twb + A.peak, B=twb + A.cur + B.peak, C=twb + A.cur + B.cur + C.peak, D=twb + A.cur + B.cur + C.cur + D.peak)
    res.update(r=r, m=m, cf=cf, acap=dict(acap or {}), S_C=C.ops, S_D=D.ops, peaks=peaks, cinfo=cinfo, modes=dict(MODE_LOG), vd=vd)
    if trace:
        sim = simulate(stages)
        arena = (sim['high'] + 128 + sim['slab'] + QE_BYTES + 63) & ~63
        res.update(sim=sim, arena=arena, big_exp=big_exp, nevents=sum(len(e) for _, e in stages))
        mem = arena + IMAGE_EXTRA + CODE_EXTRA + STACK
    else:
        arena = (max(peaks.values()) + 63) & ~63
        mem = arena + IMAGE_EXTRA + CODE_EXTRA + STACK
    res['mem'] = mem; res['mem_log2'] = math.log2(mem); res['mem_claim'] = ceil3(math.log2(mem) + 0.002)  # the claim adds 0.002 before rounding (section 7)
    Cr, fixed, rowA, rowB, src = ROWS[r]
    fixed = FIXED_BIG if fixed is None else fixed
    trial = [rowA, rowB + B_ALLOC_EXTRA, C.ops, D.ops, E_CAP, F_ROW, g_row(Cr), TRIAL_EXTRA, STAT_EXTRA, RESET_EXTRA]
    N = sum(fixed) + PLAN_EXTRA + 2 * sum(trial) + OFFLINE
    res.update(Cr=Cr, fixed=fixed, trial=trial, N=N, time_log2=math.log2(N / Cr), time_claim=ceil5(math.log2(N / Cr) + 0.0012))  # the claim adds 0.0012 before rounding (section 6.1)
    res['score'] = res['time_claim'] + max(0, res['mem_claim'] - 20)
    if not quiet:
        report(res)
    return res


def report(res):
    f = lambda x: format(x, ',')
    print('r = %d, m = %s, chunk fractions %s' % (res['r'], f(res['m']), res['cf']))
    ci = res['cinfo']
    if res.get('vd'):
        v = ci['vd']
        print('  stage C (value domain): K = %s cosets, n1 = %s, Lx = %s, Le = %s, Lq = %s, v = 2^%d, ell = %s (Kq = %s rows); %d steps (%d with b = 1)' % (
            f(v['K']), f(v['n1']), f(v['Lx']), f(v['Le']) if v['Le'] else '-', f(v['Lq']), v['v'].bit_length() - 1, f(v['ell']), f(v['Kq']), v['steps'], v['nset']))
        print('    inner transform fwd / inv %s / %s; geometric phase of one extension %s (%.3f per element of n1); one extension %s; step b = 0 / 1: %s / %s' % (
            f(v['inner_f']), f(v['inner_i']), f(v['geo']), v['geo'] / v['n1'], f(v['ext']), f(v['step0']), f(v['step1'])))
        print('    set-up: tables %s, Newton reciprocal (with plans, exponent scan, tables, allocations) %s, product for q %s, evaluation of g %s + %s, step 3 %s, step 4 %s, step 5 %s; loop %s; step 7 %s; step 8 %s' % (
            f(v['tables']), f(v['newton']), f(v['q']), f(v['ev_g']), f(v['inner_g']), f(v['st3']), f(v['ext']), f(v['st5']), f(v['loop']), f(v['st7']), f(2 * v['interp'])))
    else:
        print('  stage C: %d squaring steps (%d with S), one step = %s ops%s' % (ci['steps'], ci['nset'], f(ci['step']), '' if not ci.get('prods') else
              '; ' + ', '.join('%s (%s) n2=%d nc=%d %s' % (k, v[0], v[1], v[2], f(v[3])) for k, v in ci['prods'].items())))
    print('  S_C = %s   S_D = %s   block-product schemes used: %s' % (f(res['S_C']), f(res['S_D']), res['modes']))
    m32 = 32 * res['m']
    print('  live-set peaks: ' + ', '.join('%s %s (%.4f m)' % (k, f(v), v / m32) for k, v in res['peaks'].items()))
    if 'sim' in res:
        s = res['sim']
        print('  allocator: pool high-water %s (%.6f x live peak), per stage %s; slab area %s; arena %s; %d events' %
              (f(s['high']), s['high'] / max(res['peaks'].values()), {k: f(v) for k, v in s['per'].items()}, f(s['slab']), f(res['arena']), res['nevents']))
    print('  memory = %s bytes, log2 = %.5f, claimed %.3f' % (f(res['mem']), res['mem_log2'], res['mem_claim']))
    print('  N_max = %s, log2(N/%d) = %.8f, time_log2 claimed %.5f, score %.5f' % (f(res['N']), res['Cr'], res['time_log2'], res['time_claim'], res['score']))


def check_r21():
    """reproduce the totals asserted by e6dcb600 at r = 21 with its chunk fractions"""
    res = run(21, CF_E6, quiet=True, solve_ws=False, vd=False)
    assert res['S_C'] == 4062062219504740890363177, res['S_C']
    assert res['S_D'] == 1360756098766545569709103, res['S_D']
    assert res['peaks'] == dict(A=119209289619500726912, B=238418579240595258048, C=632939936390951625792, D=577946978315814447872), res['peaks']
    return res


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == 'check21':
        res = check_r21(); report(res)
        print('peaks match e6dcb600:', res['peaks'] == dict(A=119209289619500726912, B=238418579240595258048, C=632939936390951625792, D=577946978315814447872))
    elif args and args[0] == 'checkvd':
        for r_ in [int(a) for a in args[1:]] or sorted(JB_C): check_jb(r_)
    else:
        r = int(args[0]); tr = '--trace' in args; vd_ = '--lean' not in args
        be = int(args[args.index('--big') + 1]) if '--big' in args else None
        cfa = None
        if '--cf' in args:
            v = [float(x) for x in args[args.index('--cf') + 1].split(',')]
            cfa = dict(zip(('sq', 'q', 'qg', 'newton', 'D'), v))
        run(r, cfa, tr, be, vd=vd_)
```

## 13. Appendix F: the programs of 10.3 and 10.5

The three programs, as run. `certify.py` is the certificate program of Grok job 136 (python-flint); `certify_dep.py` runs it unchanged on the deployed constants and on the attack line, reading the constants and `line()` from `experiments/exp_line.py` (same folder); `sib_euclid.py` is the measurement of 10.5 (same folder).

### F.1 certify.py (Grok job 136)

```python
"""
Certify H_ci pieces for the first N full rounds of the Orchard Poseidon
permutation (Pallas base field, t=3, x^5, Grain MDS and round constants
from grain.py / params.txt).

Line: state(lambda) = (lambda, 2*lambda+1, 3*lambda+5).
Points compared by the attack are lambda = c±s.
Output word F is coordinate 0 after N full rounds
    state <- MDS * (state + RC[r])**5.

Run:
    python certify.py 1
    python certify.py 2
    python certify.py 3
    python certify.py 4 --start 1 --stride 1 --limit 4000
"""

from __future__ import annotations

import argparse
import os
import time
from math import gcd as int_gcd

from flint import fmpz_mod_poly, fmpz_mod_poly_ctx

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
HERE = os.path.dirname(os.path.abspath(__file__))
CTX = fmpz_mod_poly_ctx(P)
X = fmpz_mod_poly([0, 1], CTX)


def load_params():
    path = os.path.join(HERE, "params.txt")
    if not os.path.exists(path):
        raise SystemExit("params.txt missing; run python grain.py")
    mds = []
    rc = []
    mode = None
    with open(path, encoding="ascii") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line == "mds":
                mode = "mds"
                continue
            if line == "rc":
                mode = "rc"
                continue
            if line.startswith("cauchy") or line.startswith("p ") or line.startswith("t ") or line.startswith("RF") or line.startswith("RP") or line.startswith("alpha"):
                mode = None
                continue
            if mode == "mds":
                mds.append([int(x) for x in line.split()])
            elif mode == "rc":
                rc.append([int(x) for x in line.split()])
    if len(mds) != 3 or any(len(r) != 3 for r in mds):
        raise SystemExit("bad mds")
    if len(rc) < 4:
        raise SystemExit("need at least 4 round-constant rows")
    return mds, rc


def low(poly):
    if poly.is_zero():
        return [0]
    return [int(c) % P for c in poly.coeffs()]


def C(n):
    return fmpz_mod_poly([n % P], CTX)


def add_const(poly, c):
    cs = low(poly)
    cs[0] = (cs[0] + c) % P
    return fmpz_mod_poly(cs, CTX)


def pow5(poly):
    s2 = poly.square()
    s4 = s2.square()
    return s4 * poly


def matvec(mds, vec):
    out = []
    for i in range(3):
        acc = fmpz_mod_poly([0], CTX)
        for j in range(3):
            acc += vec[j] * (mds[i][j] % P)
        out.append(acc)
    return out


def build_F(N, mds, rc):
    state = [
        fmpz_mod_poly([0, 1], CTX),       # lambda
        fmpz_mod_poly([1, 2], CTX),       # 2*lambda + 1
        fmpz_mod_poly([5, 3], CTX),       # 3*lambda + 5
    ]
    for r in range(N):
        state = [pow5(add_const(state[i], rc[r][i])) for i in range(3)]
        state = matvec(mds, state)
    return state[0]


def leading_by_slopes(N, mds):
    L = [1, 2, 3]
    for _ in range(N):
        powered = [pow(v, 5, P) for v in L]
        L = [
            sum(mds[i][j] * powered[j] for j in range(3)) % P
            for i in range(3)
        ]
    return L[0]


def H_at(F, c):
    """H(c, u) where G(c, t) = H(c, t^2) = (F(c+t)-F(c-t))/(2t)."""
    c %= P
    Fp = F.compose(X + c)
    Fm = F.compose(C(c) - X)
    diff = Fp - Fm
    cs = low(diff)
    if cs[0] % P != 0:
        raise RuntimeError("F(c+t)-F(c-t) has a constant term")
    # divide by t, then by 2; keep even powers (poly in u=t^2)
    halved = cs[1:]
    inv2 = pow(2, -1, P)
    halved = [(v * inv2) % P for v in halved]
    hcoeffs = halved[0::2]
    # odd positions must vanish
    if any(halved[i] % P != 0 for i in range(1, len(halved), 2)):
        raise RuntimeError("G is not even in t")
    return fmpz_mod_poly(hcoeffs, CTX)


def G_in_c(F, t):
    """G(c, t) as a polynomial in c, t a nonzero field element."""
    if t % P == 0:
        raise ValueError("t=0")
    diff = F.compose(X + (t % P)) - F.compose(X - (t % P))
    inv = pow((2 * t) % P, -1, P)
    return diff * inv


def eval_poly(poly, a):
    return int(poly.evaluate(a % P)) % P


def factor_degrees(poly):
    fac = poly.factor()
    degs = []
    squarefree = True
    for g, e in fac[1]:
        e = int(e)
        if e != 1:
            squarefree = False
        degs.extend([int(g.degree())] * e)
    degs.sort()
    return degs, squarefree, fac


def is_prime_small(q):
    if q < 2:
        return False
    if q % 2 == 0:
        return q == 2
    d = 3
    while d * d <= q:
        if q % d == 0:
            return False
        d += 2
    return True


def largest_prime_leq(n):
    q = n
    while q >= 2 and not is_prime_small(q):
        q -= 1
    return q


def pow_x(poly):
    return X.pow_mod(P, poly)


def linear_gcd(poly):
    xp = pow_x(poly)
    g = poly.gcd(xp - X)
    return g


def squarefree_poly(g):
    if g.degree() <= 0:
        return True
    d = g.gcd(g.derivative())
    return d.degree() <= 0


def simple_root_stats(F):
    d1 = F.derivative()
    d2 = d1.derivative()
    g = d1.gcd(d2)
    deg = int(d1.degree())
    gdeg = int(g.degree()) if not g.is_zero() else -1
    # number of distinct roots in the algebraic closure that are simple
    # equals deg(d1 / rad_multiple). If g = gcd(d1, d1'), then d1/g is the
    # squarefree product of the simple-root factors only when every multiple
    # root's multiplicity is exactly the amount removed... standard fact:
    # d1 / gcd(d1, d1') is squarefree and its roots are exactly the distinct
    # roots of d1. That counts DISTINCT roots, not simple roots.
    # Simple roots: let s = d1 / gcd(d1, d1'). The multiple-root factors are
    # those of g. A root is simple iff it divides s and not g.
    # product of (x-r) over simple r  =  s / gcd(s, g) but g divides a power
    # of the multiple part and is coprime to the simple part, so gcd(s, g)
    # is 1 if s was computed as d1/g in a UFD... actually d1/g is coprime to
    # the radical of the multiple part only after removing all shared roots.
    # In char 0 or p > deg, gcd(d1, d1') is exactly the product (x-r)^{m_r-1}.
    # Then d1/gcd has each distinct root once, INCLUDING multiple roots.
    # The simple ones are the roots of d1/gcd that are not roots of gcd.
    quot = d1.exact_division(g) if g.degree() >= 0 and not g.is_zero() else d1
    # remove roots that are still multiple, i.e. divide out gcd(quot, g)
    shared = quot.gcd(g)
    if shared.degree() > 0:
        simple = quot.exact_division(shared)
    else:
        simple = quot
    n_simple_factors_deg = int(simple.degree()) if simple.degree() >= 0 else 0
    return {
        "deg_Fprime": deg,
        "deg_gcd_Fp_Fpp": int(g.degree()) if g.degree() >= 0 else -1,
        "deg_simple_part": n_simple_factors_deg,
    }


def interpolate(xs, ys):
    n = len(xs)
    xs = [int(x) % P for x in xs]
    dd = [int(y) % P for y in ys]
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            dd[i] = ((dd[i] - dd[i - 1]) * pow((xs[i] - xs[i - j]) % P, -1, P)) % P
    out = fmpz_mod_poly([dd[0]], CTX)
    basis = fmpz_mod_poly([1], CTX)
    for j in range(1, n):
        basis *= X - xs[j - 1]
        out += basis * (dd[j] % P)
    return out


def eliminant_in_s2(F, s1, bound):
    """Res_c(G(c,s1), G(c,s2)) as a polynomial in s2, degree <= bound."""
    gs1 = G_in_c(F, s1)
    # sample s2 = 1..bound+1, skipping 0 and collisions are fine (zeros)
    xs = []
    ys = []
    s2 = 1
    while len(xs) < bound + 1:
        if s2 % P == 0:
            s2 += 1
            continue
        gs2 = G_in_c(F, s2)
        val = gs1.resultant(gs2)
        xs.append(s2)
        ys.append(int(val) % P)
        s2 += 1
    return interpolate(xs, ys)


def divide_out_linear(poly, root, max_mult=64):
    mult = 0
    root %= P
    factor = X - root
    while poly.degree() >= 1:
        q, r = poly.divmod(factor)
        if r.degree() > 0 or (not r.is_zero() and low(r)[0] % P != 0):
            break
        # r should be 0
        if not r.is_zero():
            break
        poly = q
        mult += 1
        if mult > max_mult:
            break
    return poly, mult


def sign_of_cycle_type(degs):
    # sign of a permutation is (-1)^{sum (len-1)}
    s = sum(d - 1 for d in degs)
    return -1 if s % 2 else 1


def log(msg):
    print(msg, flush=True)
    try:
        with open(os.path.join(HERE, "runlog.txt"), "a", encoding="utf-8") as fh:
            fh.write(msg + "\n")
    except OSError:
        pass


def certify_derivative_and_degree(N, F, mds):
    D = 5 ** N
    deg = int(F.degree())
    lead = int(F.leading_coefficient()) % P
    pred = leading_by_slopes(N, mds)
    stats = simple_root_stats(F)
    # identity H(c,0) == F'(c) at a few points
    dF = F.derivative()
    ident_ok = True
    for c in (1, 2, 5, 17):
        h0 = eval_poly(H_at(F, c), 0)
        fp = eval_poly(dF, c)
        if h0 != fp:
            ident_ok = False
            log(f"IDENTITY FAIL c={c} H(c,0)={h0} F'(c)={fp}")
    # random point agreement: poly vs not needed, build is symbolic
    log(
        f"N={N} degF={deg} expect={D} lead={lead} slope_lead={pred} "
        f"lead_match={lead == pred} H0_is_Fprime={ident_ok} simple={stats}"
    )
    return {
        "deg": deg,
        "lead": lead,
        "lead_match": lead == pred and lead != 0 and deg == D,
        "ident_ok": ident_ok,
        "simple": stats,
    }


def search_cycle_types(N, F, start, stride, limit, time_cap):
    """Search specialisations c = start, start+stride, ... 

    Stops early once an m-cycle, an (m-1)-cycle and a Jordan q-cycle
    have all been seen, or after `limit` values, or after time_cap seconds.
    """
    D = 5 ** N
    m = (D - 1) // 2
    q = largest_prime_leq(m - 3) if m >= 6 else None
    fixed_for_q = (m - q) if q is not None else None
    log(f"search N={N} m={m} jordan_q={q} fixed_points={fixed_for_q} start={start} stride={stride} limit={limit}")
    found = {"m_cycle": None, "m1_cycle": None, "jordan": None}
    t0 = time.perf_counter()
    checked = 0
    c = start
    samples = []
    use_full = N <= 3
    while checked < limit:
        if time.perf_counter() - t0 > time_cap:
            log(f"time cap {time_cap}s hit after {checked} values, last c={c - stride}")
            break
        H = H_at(F, c)
        if int(H.degree()) != m:
            log(f"degree drop c={c} deg={H.degree()}")
            c += stride
            checked += 1
            continue
        if use_full:
            degs, sqf, _fac = factor_degrees(H)
            if len(samples) < 12:
                samples.append((c, degs, sqf))
                log(f"sample c={c} squarefree={sqf} degs={degs}")
            if sqf and found["m_cycle"] is None and degs == [m]:
                found["m_cycle"] = c
                log(f"FOUND m-cycle c={c} time={time.perf_counter()-t0:.2f}s")
            if sqf and found["m1_cycle"] is None and degs == [1, m - 1]:
                found["m1_cycle"] = c
                log(f"FOUND (m-1,1) c={c} time={time.perf_counter()-t0:.2f}s")
            if (
                sqf
                and q is not None
                and found["jordan"] is None
                and degs == [1] * fixed_for_q + [q]
            ):
                found["jordan"] = (c, q, fixed_for_q)
                log(
                    f"FOUND jordan {q}-cycle + {fixed_for_q} fixed "
                    f"c={c} time={time.perf_counter()-t0:.2f}s"
                )
        else:
            g = linear_gcd(H)
            gd = int(g.degree()) if g.degree() > 0 else 0
            sf = squarefree_poly(g) if gd > 0 else True
            if found["m_cycle"] is None and gd == 0 and H.is_irreducible():
                found["m_cycle"] = c
                log(f"FOUND m-cycle c={c} time={time.perf_counter()-t0:.2f}s")
            if found["m1_cycle"] is None and gd == 1 and sf:
                quot = H.exact_division(g.monic())
                if quot.is_irreducible():
                    found["m1_cycle"] = c
                    log(f"FOUND (m-1,1) c={c} time={time.perf_counter()-t0:.2f}s")
            if q is not None and found["jordan"] is None and gd == fixed_for_q and sf:
                quot = H.exact_division(g.monic())
                if int(quot.degree()) == q and quot.is_irreducible():
                    found["jordan"] = (c, q, fixed_for_q)
                    log(
                        f"FOUND jordan {q}-cycle + {fixed_for_q} fixed "
                        f"c={c} time={time.perf_counter()-t0:.2f}s"
                    )
        checked += 1
        if checked % 25 == 0:
            log(
                f"progress checked={checked} c={c} elapsed={time.perf_counter()-t0:.1f}s "
                f"found={found}"
            )
        if found["m_cycle"] and found["m1_cycle"] and (q is None or found["jordan"]):
            log("all targets found")
            break
        c += stride
    elapsed = time.perf_counter() - t0
    log(f"search done checked={checked} elapsed={elapsed:.2f}s found={found}")
    return {
        "m": m,
        "q": q,
        "found": found,
        "samples": samples,
        "checked": checked,
        "elapsed": elapsed,
    }


def multiplicity_of_root(poly, root):
    poly, mult = divide_out_linear(poly, root, max_mult=10000)
    return poly, mult


def n1_eliminant(F):
    """For N=1, compute Res_c(G(c,s1), G(c,s2)) at several s1 and factor."""
    # degree bound: (5-1)^2 = 16, take 24 to see the true degree
    bound = 24
    results = []
    for s1 in (3, 5, 8, 13):
        t0 = time.perf_counter()
        poly = eliminant_in_s2(F, s1, bound)
        # trim leading zeros already handled by degree
        deg = int(poly.degree())
        log(f"eliminant s1={s1} deg={deg} time={time.perf_counter()-t0:.3f}s")
        # divide out (s2-s1) and (s2+s1)
        poly, m_plus = multiplicity_of_root(poly, s1)       # s2 = s1
        poly, m_minus = multiplicity_of_root(poly, (-s1) % P)  # s2 = -s1
        degs, sqf, fac = factor_degrees(poly)
        log(
            f"  after removing (s2-s1)^{m_plus} (s2+s1)^{m_minus}: "
            f"deg={poly.degree()} squarefree={sqf} factor_degs={degs}"
        )
        results.append(
            {
                "s1": s1,
                "raw_deg": deg,
                "mult_s2_eq_s1": m_plus,
                "mult_s2_eq_minus_s1": m_minus,
                "cofactor_degs": degs,
                "cofactor_squarefree": sqf,
                "cofactor": poly,
            }
        )
    return results


def abs_irreducible_univariate_specialization(bivariate_builder, degree, divisors):
    """Not used for large degree. Placeholder kept out; N=1 uses direct test."""
    raise NotImplementedError


def test_abs_irred_phi(cofactor_poly_at_s1_builder, s1_values_in_ext, degree):
    pass


def n1_absolute(F):
    """Absolute irreducibility of the N=1 cofactor via extension specialisations.

    Build the bivariate-in-practice eliminant cofactor as a univariate in s2
    over an extension of the s1-line, by specialising s1 in F_{p^k}.
    """
    from flint import fq_default_ctx, fq_default_poly_ctx

    # First get Phi over F_p at s1=3, as produced by n1, and its degree.
    # We recompute a monic cofactor in F_p[s2] and then, for each prime-power
    # divisor, specialise s1 inside F_{p^k}.
    #
    # Concrete method: G_in_c needs F over the prime field, resultant too.
    # For s1 in F_{p^k}, do the resultant inside that extension.
    D = 5
    # Rebuild F over prime field is already `F`. For extension arithmetic,
    # convert F's coefficients into the extension and repeat eliminant
    # interpolation there only for k in the divisor set of the cofactor degree.
    base = eliminant_in_s2(F, 3, 24)
    base, m1 = multiplicity_of_root(base, 3)
    base, m2 = multiplicity_of_root(base, (-3) % P)
    degs, sqf, fac = factor_degrees(base)
    log(f"base cofactor at s1=3 degs={degs} sqf={sqf} mults {m1},{m2}")
    # If several F_p factors, test each factor's absolute irreducibility
    # by the specialization method on that factor's degree.
    factors = []
    for g, e in fac[1]:
        factors.append((g.monic(), int(g.degree()), int(e)))
    reports = []
    for g, deg, e in factors:
        divs = [d for d in range(2, deg + 1) if deg % d == 0]
        # only need to forbid a split into d conjugate pieces; the extension
        # degree to test is d (number of conjugates). For deg<=16 this is fine.
        log(f"absolute test factor deg={deg} exp={e} divisors={divs}")
        verdicts = []
        for k in divs:
            Fld = fq_default_ctx(P, k)
            PC = fq_default_poly_ctx(Fld)
            Y = PC.gen()
            # lift prime-field F into extension polys in c
            fcoeffs = low(F)

            def lift_poly(coeffs):
                # coeffs low to high as field elements
                return sum(
                    (PC.gen() ** 0) * 0,
                    (),
                )  # placeholder replaced below

            # Build extension polynomial from prime-field coefficient list.
            def ext_poly(coeffs, PC=PC):
                # Use the prime-field embedding: fq elements from ints.
                cs = []
                for a in coeffs:
                    cs.append(Fld(int(a) % P))
                # fq_default_poly from list?
                return PC([Fld(int(a) % P) for a in coeffs]) if False else None

            # Construct via the context call pattern that worked for fmpz:
            # try PC.zero and accumulation.
            acc = None
            # We'll build using evaluate-and-interpolate over the extension,
            # calling resultant in the extension.
            verdicts.append((k, "deferred"))
        reports.append({"deg": deg, "exp": e, "divs": divs, "verdicts": verdicts})
    return {"factors": [(d, e) for _, d, e in factors], "reports": reports, "sqf": sqf}


def build_ext_poly(PC, Fld, coeffs):
    """coeffs low-to-high integers -> fq poly."""
    # Try constructor
    try:
        return PC([Fld(int(a) % P) for a in coeffs])
    except Exception:
        pass
    x = PC.gen()
    acc = PC.zero()
    powx = PC.one()
    for a in coeffs:
        acc += powx * Fld(int(a) % P)
        powx *= x
    return acc


def g_in_c_ext(F_coeffs, t_ext, PC, Fld):
    """G(c, t) in the extension, t_ext an fq element, as a poly in c."""
    # F(c+t) = sum f_k (c+t)^k. Use horner in the polynomial ring.
    x = PC.gen()
    # shift variable to x+t
    # Horner
    acc_p = PC.zero()
    acc_m = PC.zero()
    # evaluate horner with the polynomial (x+t) substituted: just horner the
    # coefficient list into the element (x + t) of the polynomial ring.
    xp = x + t_ext
    xm = x - t_ext
    for a in reversed(F_coeffs):
        acc_p = acc_p * xp + Fld(int(a) % P)
        acc_m = acc_m * xm + Fld(int(a) % P)
    diff = acc_p - acc_m
    inv = (Fld(2) * t_ext) ** -1
    return diff * inv


def eliminant_ext(F_coeffs, s1_ext, bound, PC, Fld):
    gs1 = g_in_c_ext(F_coeffs, s1_ext, PC, Fld)
    # interpolate in s2 at field elements 1,2,... 
    xs = []
    ys = []
    s2 = 1
    x = PC.gen()
    while len(xs) < bound + 1:
        s2_e = Fld(s2)
        if s2_e.is_zero():
            s2 += 1
            continue
        gs2 = g_in_c_ext(F_coeffs, s2_e, PC, Fld)
        val = gs1.resultant(gs2)
        xs.append(s2_e)
        ys.append(val)
        s2 += 1
    # Newton interpolation over Fq
    n = len(xs)
    dd = list(ys)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            dd[i] = (dd[i] - dd[i - 1]) / (xs[i] - xs[i - j])
    out = PC.zero() + dd[0]
    # PC.zero()+dd[0] might fail if types differ; use accumulation
    basis = PC.one()
    out = basis * dd[0]
    for j in range(1, n):
        basis *= x - xs[j - 1]
        out += basis * dd[j]
    return out


def divide_linear_ext(poly, root, PC):
    x = PC.gen()
    mult = 0
    factor = x - root
    while poly.degree() >= 1:
        q, r = poly.divmod(factor)
        if not r.is_zero():
            break
        poly = q
        mult += 1
        if mult > 64:
            break
    return poly, mult


def horner_ext(coeffs, point, Fld):
    acc = Fld(0)
    for a in reversed(coeffs):
        acc = acc * point + Fld(int(a) % P)
    return acc


def n1_absolute_run(F):
    """Interpolate Phi(s1, s2), the degree-8 cofactor of the eliminant, and
    test absolute irreducibility by irreducible specialisations over F_{p^k}.
    """
    from flint import fq_default_ctx, fq_default_poly_ctx

    samples = []
    for s1 in range(1, 25):
        poly = eliminant_in_s2(F, s1, 20)
        raw = int(poly.degree())
        poly, m1 = multiplicity_of_root(poly, s1)
        poly, m2 = multiplicity_of_root(poly, (-s1) % P)
        if m1 != 4 or m2 != 4:
            log(f"unexpected multiplicity s1={s1} ({m1},{m2})")
        cs = low(poly)
        samples.append((s1, cs, raw, int(poly.degree())))
    deg_s2 = max(d for _, _, _, d in samples)
    log(f"Phi samples deg_s2={deg_s2} raw_degs={sorted(set(r for _,_,r,_ in samples))}")
    # coefficient of s2^j as a polynomial in s1
    coeff_polys = []
    for j in range(deg_s2 + 1):
        xs = [s1 for s1, _, _, _ in samples]
        ys = []
        for _, cs, _, _ in samples:
            ys.append(cs[j] if j < len(cs) else 0)
        coeff_polys.append(interpolate(xs, ys))
        log(f"  coeff s2^{j} deg_s1={int(coeff_polys[-1].degree())}")
    # consistency: a second interpolation on a subset must agree on a fresh s1
    check_s1 = 30
    poly = eliminant_in_s2(F, check_s1, 20)
    poly, _, = multiplicity_of_root(poly, check_s1)
    # recompute properly
    poly = eliminant_in_s2(F, check_s1, 20)
    poly, _m1 = multiplicity_of_root(poly, check_s1)
    poly, _m2 = multiplicity_of_root(poly, (-check_s1) % P)
    got = low(poly)
    pred = [eval_poly(coeff_polys[j], check_s1) for j in range(deg_s2 + 1)]
    while got and got[-1] == 0:
        got.pop()
    while pred and pred[-1] == 0:
        pred.pop()
    if got != pred:
        log(f"INTERPOLATION MISMATCH s1={check_s1} got_deg={len(got)-1} pred_deg={len(pred)-1}")
        # show first difference
        for i, (a, b) in enumerate(zip(got, pred)):
            if a != b:
                log(f"  first diff at s2^{i}")
                break
        else:
            log(f"  length mismatch {len(got)} vs {len(pred)}")
        raise SystemExit(1)
    log(f"interpolation agrees at s1={check_s1}")
    # content
    content = coeff_polys[0]
    for cp in coeff_polys[1:]:
        content = content.gcd(cp)
    log(f"content degree {int(content.degree())} (0 means constant)")
    # F_p factorisation of one specialisation already logged; repeat at s1=13
    spec = [eval_poly(coeff_polys[j], 13) for j in range(deg_s2 + 1)]
    spec_poly = fmpz_mod_poly(spec, CTX)
    degs, sqf, _ = factor_degrees(spec_poly)
    log(f"Phi(13,s2) squarefree={sqf} degs={degs}")
    divs = [d for d in range(2, deg_s2 + 1) if deg_s2 % d == 0]
    tests = []
    for k in divs:
        t0 = time.perf_counter()
        Fld = fq_default_ctx(P, k)
        PC = fq_default_poly_ctx(Fld)
        # several s1 in the extension, stop at the first full-degree irreducible
        z = Fld.gen()
        hit = None
        for tadd in range(0, 40):
            s1 = z + Fld(tadd + 1)
            ev = [horner_ext(low(coeff_polys[j]), s1, Fld) for j in range(deg_s2 + 1)]
            # drop leading zeros
            while ev and ev[-1].is_zero():
                ev.pop()
            if len(ev) - 1 != deg_s2:
                continue
            fp = PC.zero()
            # build by horner in PC
            x = PC.gen()
            acc = PC.zero()
            for a in reversed(ev):
                acc = acc * x + a
            fp = acc
            if int(fp.degree()) == deg_s2 and fp.is_irreducible():
                hit = tadd + 1
                break
        dt = time.perf_counter() - t0
        log(f"  ext k={k} irreducible full-degree hit_t={hit} time={dt:.2f}s")
        tests.append({"k": k, "hit": hit, "time": dt})
    return {"deg_s2": deg_s2, "tests": tests, "content_deg": int(content.degree())}


def disc_quadratic(F):
    """For degree-5 F, H is quadratic in u. Return disc(u) as poly in c, factored."""
    # Sample H at many c and interpolate the discriminant polynomial.
    # H = A u^2 + B(c) u + C(c), A = leading = const.
    # disc = B^2 - 4 A C.
    # Degree of disc: B has deg <= 3? Let's just interpolate high enough.
    # deg F=5, H degree 2 in u, coeffs of u^1 and u^0 have degree <= 4.
    # disc degree <= 8. Sample 12 points.
    xs = []
    ys = []
    A = None
    for c in range(1, 14):
        H = H_at(F, c)
        cs = low(H)
        while len(cs) < 3:
            cs.append(0)
        if A is None:
            A = cs[2]
        disc = (cs[1] * cs[1] - 4 * cs[2] * cs[0]) % P
        xs.append(c)
        ys.append(disc)
    poly = interpolate(xs, ys)
    degs, sqf, fac = factor_degrees(poly)
    log(f"disc poly deg={poly.degree()} squarefree={sqf} factor_degs={degs} lead={int(poly.leading_coefficient())%P}")
    # Is disc a square in F_p-bar(c)? Squarefree part degree > 0 => no.
    sqfree_degs = []
    for g, e in fac[1]:
        if int(e) % 2 == 1:
            sqfree_degs.append(int(g.degree()))
    log(f"odd-exponent factor degrees {sqfree_degs}")
    return {
        "deg": int(poly.degree()),
        "factor_degs": degs,
        "squarefree": sqf,
        "odd_factor_degs": sqfree_degs,
        "lead": int(poly.leading_coefficient()) % P,
    }


def spot_check_F(N, F, mds, rc):
    """Compare F(lambda) with direct round iteration at a few lambdas."""
    ok = True
    for lam in (0, 1, 2, 7, 19):
        state = [lam % P, (2 * lam + 1) % P, (3 * lam + 5) % P]
        for r in range(N):
            state = [pow((state[i] + rc[r][i]) % P, 5, P) for i in range(3)]
            state = [
                sum(mds[i][j] * state[j] for j in range(3)) % P
                for i in range(3)
            ]
        pred = eval_poly(F, lam)
        if pred != state[0]:
            ok = False
            log(f"SPOT FAIL N={N} lam={lam} poly={pred} direct={state[0]}")
    log(f"spot check N={N} ok={ok}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("N", type=int)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--time-cap", type=float, default=600.0)
    ap.add_argument("--skip-search", action="store_true")
    args = ap.parse_args()
    mds, rc = load_params()
    log(f"loaded rc rows {len(rc)} mds00 {mds[0][0]}")
    t0 = time.perf_counter()
    F = build_F(args.N, mds, rc)
    log(f"built F N={args.N} in {time.perf_counter()-t0:.3f}s deg={F.degree()}")
    spot_check_F(args.N, F, mds, rc)
    info = certify_derivative_and_degree(args.N, F, mds)
    if args.N == 1:
        disc_quadratic(F)
        n1_eliminant(F)
        n1_absolute_run(F)
    if not args.skip_search and args.N >= 2:
        search_cycle_types(args.N, F, args.start, args.stride, args.limit, args.time_cap)
    elif args.N == 1 and not args.skip_search:
        # small cycle types of H for the record
        search_cycle_types(1, F, 1, 1, 30, 60)


if __name__ == "__main__":
    main()
```

### F.2 certify_dep.py

```python
# Grok 136 certificate code (certify.py, unchanged) run on the DEPLOYED constants and the attack's own line.
# F_N = coordinate 0 of the first N S-box layers of the digest polynomial of proof.md section 2.3, in the variable W:
# start state alpha + beta W (the line j = 0 after the first two rounds), layers = rounds 2, 3 (full), 4, 5, ... (partial, coordinate 0 only).
# usage: python certify_dep.py N [--limit L --time-cap T --skip-search]   (certify.py and exp_line.py in this folder)
import sys, os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exp_line.py')).read()
exec(src[:src.index('NPAIR = 150')], globals())          # P, MDS, RC, line(), rounds_from()
import certify as Z
from flint import fmpz_mod_poly
Z.HERE = os.path.dirname(os.path.abspath(__file__))
FULL = [True, True] + [False] * 20
_qu, _qv, _a, _b, AL, BE = line(7)
def load_params(): return MDS, [RC[2 + r] for r in range(20)]
def build_F(N, mds, rc):
    st = [Z.add_const(Z.C(0), 0) * 0 + Z.X * BE[i] + AL[i] for i in range(3)]
    for r in range(N):
        st = [Z.add_const(st[i], rc[r][i]) for i in range(3)]
        st = [Z.pow5(st[i]) if (FULL[r] or i == 0) else st[i] for i in range(3)]
        st = Z.matvec(mds, st)
    return st[0]
def leading_by_slopes(N, mds):
    L = [(v, 1) for v in BE]                      # (leading coefficient, degree) of each coordinate
    for r in range(N):
        pw = [(pow(v, 5, P), 5 * d) if (FULL[r] or i == 0) else (v, d) for i, (v, d) in enumerate(L)]
        top = max(d for _, d in pw)
        L = [(sum(mds[i][j] * pw[j][0] for j in range(3) if pw[j][1] == top) % P, top) for i in range(3)]
    return L[0][0]
def spot_check_F(N, F, mds, rc):
    ok = True
    for w in (0, 1, 2, 7, 19):
        s = [(AL[i] + BE[i] * w) % P for i in range(3)]
        for r in range(N):
            s = [(s[i] + rc[r][i]) % P for i in range(3)]
            s = [pow(s[i], 5, P) if (FULL[r] or i == 0) else s[i] for i in range(3)]
            s = [sum(mds[i][j] * s[j] for j in range(3)) % P for i in range(3)]
        if Z.eval_poly(F, w) != s[0]: ok = False; Z.log(f"SPOT FAIL N={N} w={w}")
    Z.log(f"spot check N={N} ok={ok} (deployed constants, attack line)")
    return ok
Z.load_params, Z.build_F, Z.leading_by_slopes, Z.spot_check_F = load_params, build_F, leading_by_slopes, spot_check_F
Z.log = lambda msg: print(msg, flush=True)
if __name__ == "__main__": Z.main()
```

### F.3 sib_euclid.py

```python
# Euclid-normality measurement (A1 of H1-charging-rules) on the real Orchard digest polynomial of the sibling targets
# r' = 0,1,2 partial rounds (same constants, same line j=0 of rounds 0-1, degree 5^(6+r')). Uses python-flint. usage: sib_euclid.py R NCENTRES [START]
import sys, time, json, hashlib, re
from flint import fmpz_mod_poly_ctx, fmpz_mod_ctx
src = open('exp_line.py').read()
exec(src[:src.index('req = json.loads')].replace('NPAIR = 150', 'NPAIR = 150'), globals())   # P, MDS, RC, line()
R = int(sys.argv[1]); NC = int(sys.argv[2]); START = int(sys.argv[3]) if len(sys.argv) > 3 else 1
ctx = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)); X = ctx.gen()
qu, qv, a, bb, al, be = line(R)
s = [al[i] + be[i] * X for i in range(3)]
for i in (*range(2, 4), *range(4, 4 + R), *range(60, 64)):
    s = [x + c for x, c in zip(s, RC[i])]
    for j in (range(3) if i < 4 or i >= 60 else range(1)): s[j] = s[j] ** 5
    s = [sum((MDS[r][k] * s[k] for k in range(3)), ctx.zero() if hasattr(ctx, 'zero') else 0 * X) for r in range(3)]
F = s[0]; D = F.degree(); assert D == 5 ** (6 + R), D
m = (D - 1) // 2
out = []
for c in range(START, START + NC):
    t0 = time.time()
    Fc = F.compose(X + c); co = Fc.coeffs()
    g = ctx([co[2 * k + 1] for k in range(m + 1)]).monic()
    Rr = X.pow_mod((P - 1) // 2, g) - 1
    t1 = time.time()
    a_, b_ = g, Rr; steps = 0; bad = []; 
    while b_.degree() > 0:
        q, r = a_.divmod(b_); steps += 1
        if q.degree() != 1: bad.append((steps, q.degree()))
        a_, b_ = b_, r
    rec = dict(r=R, centre=c, D=D, m=m, deg_R1=Rr.degree(), euclid_steps=steps, nonnormal=bad[:5], n_nonnormal=len(bad), final_deg=a_.degree() if b_.is_zero() else b_.degree(), sec_pow=round(t1 - t0, 1), sec_euclid=round(time.time() - t1, 1))
    print(json.dumps(rec), flush=True)
```


## 14. Appendix G: block products, the outer scheme and the coset solve at small sizes (`bigmul_check.py`)

The programs of proof.md 4.5 and 3 at block length 12 and transform size 24 over the Pallas field, against schoolbook products: one product with several windows, the square, the subtraction into an array, the bilinear form of `apply_inv` with a short exact result (also with entries of three blocks and operands of five), the 2 x 2 matrix product with multi-block entries, the outer-transform scheme (outer length, inner transforms, fold, wrap rule), the chunked scheme (c) of 4.5 with 1, 2, 3, 4, 6 and 8 chunks (assembly by `ocp`, `oax` and `ozf`, the `Q`-point transforms across the arrays, the accumulation with the weights `w^(-j1 s)`, with the counts of the three kernels asserted), the streamed schedule of 4.5 (three squaring steps of stage C with the persistent forms of `MU` and `g` made once, in scheme (a) and in scheme (b), against the remainder of the square modulo `g`; `apply_inv` with a sliding window of `kR + 1` block spectra of each of `a` and `b` and the outputs written over `a` and `b`, which asserts that no block of an input is overwritten before it is transformed and that each block is transformed once; the matrix product by rows), the interpolation by `kappa = 3` cosets with the Vandermonde recombination, and the geometric-node solve of section 3 (q-binomial coefficients of `M`, the closed form of `M'`, the two correlations) at `kappa = 7`. It also checks that the nodes `u_k^B` for `v_k = 1, 2, 3` and `B = 3 * 2^31` are pairwise distinct, that the odd cofactor of `2^32 * 3 * 463` in `p - 1` has no divisor from 3 to `2 * 10^8` (by trial division), and that `z = 4^B` has no power `z^d = 1` for the divisors `d` of `p - 1` up to `2 * 10^8`. Run: `python3 bigmul_check.py`.

### G.1 bigmul_check.py

```python
#!/usr/bin/env python3
"""Appendix G: the block product (proof.md 4.5) and the coset interpolation (proof.md 3) at small sizes over the Pallas field, against schoolbook.
Run: python3 bigmul_check.py   (standard library only; asserts, prints ok).
Small sizes: block length B = 12, transform size NB = 2B = 24 = 3 * 2^3 (the real sizes are 3 * 2^31 and 3 * 2^32)."""
import random
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
inv = lambda x: pow(x, P - 2, P)


def root(n):                              # a primitive n-th root of unity (n | 2^32 * 3)
    w = pow(5, (P - 1) // n, P)
    for q in (2, 3):
        if n % q == 0: assert pow(w, n // q, P) != 1
    assert pow(w, n, P) == 1
    return w


def dft(a, w, n):                         # naive transform of size n on a zero-padded to n
    a = a + [0] * (n - len(a))
    return [sum(a[j] * pow(w, i * j, P) for j in range(n)) % P for i in range(n)]


def school(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): r[i + j] = (r[i + j] + x * y) % P
    return r


B, NB = 12, 24
W = root(NB)


def blocks(a): return [a[i:i + B] for i in range(0, len(a), B)]


def block_product(prods, ws, outlen, out):
    """prods: list of (A, C, sign); out: list modified in place (placement adds sign * result); window [ws, ws+outlen) of the sum of the products.
    Only the slots meeting the window are formed (proof.md 4.5)."""
    TA = {}
    def tr(x, i):
        k = (id(x), i)
        if k not in TA: TA[k] = dft(blocks(x)[i], W, NB)
        return TA[k]
    ns = max(len(blocks(a)) + len(blocks(c)) - 1 for a, c, _ in prods)
    for s in range(ns):
        if not (s * B < ws + outlen and (s + 2) * B - 1 > ws): continue
        acc = [0] * NB
        for a, c, sg in prods:
            for i in range(len(blocks(a))):
                j = s - i
                if 0 <= j < len(blocks(c)):
                    ta, tc = tr(a, i), tr(c, j)
                    acc = [(x + sg * y * z) % P for x, y, z in zip(acc, ta, tc)]
        slot = [x * inv(NB) % P for x in dft(acc, inv(W), NB)]       # inverse transform and scale 1/NB
        for t in range(NB - 1):
            pos = s * B + t
            if ws <= pos < ws + outlen: out[pos - ws] = (out[pos - ws] + slot[t]) % P


def rnd(n): return [random.randrange(P) for _ in range(n)]


def main():
    random.seed(1)
    # 1. one product, several windows (full, middle, low), lengths with a short last block
    for la, lc in ((30, 29), (24, 24), (12, 35), (13, 13), (7, 31)):
        a, c = rnd(la), rnd(lc); ref = school(a, c)
        for ws, ol in ((0, la + lc - 1), (la - 2, lc - 1), (0, la), (5, 20)):
            ol = min(ol, la + lc - 1 - ws)
            out = [0] * ol; block_product([(a, c, 1)], ws, ol, out)
            assert out == ref[ws:ws + ol], (la, lc, ws, ol)
    # 2. squaring, and subtraction into an array (the placement of the step of stage C)
    a = rnd(30); ref = school(a, a); out = [0] * 59; block_product([(a, a, 1)], 0, 59, out); assert out == ref
    base = rnd(30); out = list(base); c = rnd(31); block_product([(a, c, -1)], 0, 30, out)
    assert out == [(x - y) % P for x, y in zip(base, school(a, c)[:30])]
    # 3. the bilinear form of apply_inv: c = r3 a - r1 b with a = r1 u + e1, b = r3 u + e2: the exact c is short, and the slots beyond the window are not formed
    r1, r3, u, e1, e2 = rnd(10), rnd(11), rnd(30), rnd(4), rnd(3)
    a = school(r1, u); b = school(r3, u)
    for i, x in enumerate(e1): a[i] = (a[i] + x) % P
    for i, x in enumerate(e2): b[i] = (b[i] + x) % P
    exact = [(x - y) % P for x, y in zip(school(r3, a) + [0] * 80, school(r1, b) + [0] * 80)]
    assert all(x == 0 for x in exact[15:])
    nres = 15
    out = [0] * nres; block_product([(a, r3, 1), (b, r1, -1)], 0, nres, out)
    assert out == exact[:nres]
    # 4. coset interpolation: kappa = 3 cosets of the group of order B, nodes u_k^B distinct, Vandermonde recombination
    kappa, m = 3, 29
    g = rnd(m + 1); zeta = W; omega = zeta * zeta % P
    v = [1, 2, 3]; u = [x * x for x in v]
    nodes = [pow(x, B, P) for x in u]; assert len(set(nodes)) == kappa
    wk = []
    for k in range(kappa):
        vals = [sum(g[j] * pow(u[k] * pow(omega, i, P), j, P) for j in range(m + 1)) % P for i in range(B)]   # g at S = u_k omega^i
        coef = [x * inv(B) % P for x in dft(vals, inv(omega), B)]                                             # inverse transform of size B
        wk.append([coef[j] * inv(pow(u[k], j, P)) % P for j in range(B)])                                      # W_k[j] = sum_t nodes_k^t h_t[j]
    # solve the Vandermonde system per j (Gauss-Jordan over F_p)
    rec = [0] * (kappa * B)
    for j in range(B):
        M = [[pow(nodes[k], t, P) for t in range(kappa)] + [wk[k][j]] for k in range(kappa)]
        for c0 in range(kappa):
            piv = next(r for r in range(c0, kappa) if M[r][c0]); M[c0], M[piv] = M[piv], M[c0]
            iv = inv(M[c0][c0]); M[c0] = [x * iv % P for x in M[c0]]
            for r in range(kappa):
                if r != c0: f = M[r][c0]; M[r] = [(x - f * y) % P for x, y in zip(M[r], M[c0])]
        for t in range(kappa): rec[j + t * B] = M[t][kappa]
    assert rec == g + [0] * (kappa * B - len(g))
    # the real constants: the nodes u_k^B for v_k = 1, 2, 3 and B = 3 * 2^31 are pairwise distinct
    Br = 3 << 31
    real = [pow(x * x, Br, P) for x in (1, 2, 3)]
    assert len(set(real)) == 3 and all(x != 0 for x in real)
    # 5. multi-block matrix entries (r >= 10): the bilinear form of apply_inv with entries of 3 blocks and operands of 5 blocks, and the 2 x 2 matrix product with multi-block entries
    r1, r3, u, e1, e2 = rnd(33), rnd(34), rnd(60), rnd(4), rnd(3)
    a = school(r1, u); b = school(r3, u)
    for i, x in enumerate(e1): a[i] = (a[i] + x) % P
    for i, x in enumerate(e2): b[i] = (b[i] + x) % P
    exact = [(x - y) % P for x, y in zip(school(r3, a) + [0] * 200, school(r1, b) + [0] * 200)]
    assert all(x == 0 for x in exact[64:])
    out = [0] * 64; block_product([(a, r3, 1), (b, r1, -1)], 0, 64, out)
    assert out == exact[:64]
    A4 = [rnd(30), rnd(31), rnd(29), rnd(36)]; B4 = [rnd(35), rnd(26), rnd(13), rnd(37)]
    for i in range(2):
        for j in range(2):
            ref = [0] * 80
            for t_ in range(2):
                pr = school(A4[2 * i + t_], B4[2 * t_ + j])
                for k_, x in enumerate(pr): ref[k_] = (ref[k_] + x) % P
            ln = max(len(A4[2 * i + t_]) + len(B4[2 * t_ + j]) - 1 for t_ in range(2))
            out = [0] * ln; block_product([(A4[2 * i], B4[j], 1), (A4[2 * i + 1], B4[2 + j], 1)], 0, ln, out)
            assert out == ref[:ln], (i, j)
    # 6. the outer-NTT scheme (Grok job 140, j = 3): outer transform of length n2 across the blocks, inner transform per outer point, fold of the upper half with the outer root
    def pad23(n):
        return min(c << a_ for a_ in range(0, 12) for c in (1, 3) if (c << a_) >= n)
    def outer_product(prods, ws, outlen, out):
        ns = max(len(blocks(a_)) + len(blocks(c_)) - 1 for a_, c_, _ in prods)       # slots 0 .. ns-1; the folded pieces are 0 .. ns
        s0 = max(0, (ws + 1) // B - 3)
        while (s0 + 2) * B - 1 <= ws: s0 += 1
        s1 = -(-(ws + outlen) // B) + 2
        while s1 * B >= ws + outlen: s1 -= 1
        n2 = pad23(max(s1 + 2, ns + 1 - s0))
        W2 = root(n2)
        spec = {}
        def outer_spec(x):             # for every outer point o: the polynomial sum_i W2^(o i) x_i (B coefficients), then its inner transform
            k_ = id(x)
            if k_ not in spec:
                bl = blocks(x); rows = []
                for o in range(n2):
                    pol = [0] * B
                    for i, blk_ in enumerate(bl):
                        f = pow(W2, o * i, P)
                        for t_, v_ in enumerate(blk_): pol[t_] = (pol[t_] + f * v_) % P
                    rows.append(dft(pol, W, NB))
                spec[k_] = rows
            return spec[k_]
        folded = []
        for o in range(n2):
            acc = [0] * NB
            for a_, c_, sg in prods:
                ta, tc = outer_spec(a_)[o], outer_spec(c_)[o]
                acc = [(x + sg * y * z) % P for x, y, z in zip(acc, ta, tc)]
            slot = [x * inv(NB) % P for x in dft(acc, inv(W), NB)]
            fo = pow(W2, o, P)
            folded.append([(slot[t_] + fo * slot[B + t_]) % P if B + t_ < NB - 1 else slot[t_] for t_ in range(B)])
        for t_ in range(B):            # inverse outer transform: the coefficient of piece s at position t
            col = [folded[o][t_] for o in range(n2)]
            piece = [x * inv(n2) % P for x in dft(col, inv(W2), n2)]
            for s in range(n2):
                pos = s * B + t_
                if ws <= pos < ws + outlen and s <= ns: out[pos - ws] = (out[pos - ws] + piece[s]) % P
    for la, lc in ((30, 29), (60, 37), (25, 25), (50, 50)):
        a, c = rnd(la), rnd(lc); ref = school(a, c)
        for ws, ol in ((0, la + lc - 1), (la - 2, lc - 1), (0, la), (17, 40)):
            ol = min(ol, la + lc - 1 - ws)
            out = [0] * ol; outer_product([(a, c, 1)], ws, ol, out)
            assert out == ref[ws:ws + ol], ('outer', la, lc, ws, ol)
    a, c, d_ = rnd(40), rnd(29), rnd(22)                        # two products into one output (the bilinear form), the sign by the combination
    ref = [(x - y) % P for x, y in zip(school(a, c) + [0] * 60, school(d_, c) + [0] * 60)]
    out = [0] * 64; outer_product([(a, c, 1), (d_, c, -1)], 0, 64, out); assert out == ref[:64]
    # 6b. the chunked outer scheme (c) (proof 4.5): n2 = pc * Q outer points in pc chunks (four-step split); the operands stay in coefficient form; chunk j1 holds the outer points j1 + pc j2;
    # its Q arrays are assembled from the blocks (z_(i2) = sum over i = i2 + Q i1 of w^(i j1) x_i: ocp for the blocks i < Q, oax for the others, zero for the arrays no block reaches),
    # transformed across the Q arrays with the root w^pc, multiplied pointwise (inner transforms, fold with w^(o) for the outer point o = j1 + pc j2), transformed back across the Q points and
    # accumulated into the output pieces s = A .. B + 1 with the weight w^(-j1 s) (ocp for the first chunk, oax for the others).
    def chunk_product(prods, ws, outlen, out, pc):
        ns = max(len(blocks(a_)) + len(blocks(c_)) - 1 for a_, c_, _ in prods)
        s0 = max(0, (ws + 1) // B - 3)
        while (s0 + 2) * B - 1 <= ws: s0 += 1
        s1 = -(-(ws + outlen) // B) + 2
        while s1 * B >= ws + outlen: s1 -= 1
        n2 = pad23(max(s1 + 2, ns + 1 - s0))
        if n2 % pc: pc_ = 1
        else: pc_ = pc
        Q = n2 // pc_
        W2 = root(n2); WQ = pow(W2, pc_, P); assert pc_ == 1 or WQ == root(Q)
        tw = [pow(W2, e, P) for e in range(n2 + 1)]
        A_, B_ = s0, min(s1, ns - 1); tc = max(0, min(n2, B_ - A_ + 2))
        acc = [[0] * B for _ in range(tc)]
        ops = {'ocp': 0, 'oax': 0, 'ozf': 0}
        def assemble(x, j1):                    # the Q arrays of the chunk, then the Q-point transform across them
            bl = blocks(x); z = [None] * Q
            for i, blk_ in enumerate(bl):
                i2 = i % Q; wgt = tw[(i * j1) % n2]
                row = [wgt * v_ % P for v_ in blk_] + [0] * (B - len(blk_))
                if z[i2] is None: z[i2] = row; ops['ocp'] += 1
                else: z[i2] = [(u_ + v_) % P for u_, v_ in zip(z[i2], row)]; ops['oax'] += 1
            for i2 in range(Q):
                if z[i2] is None: z[i2] = [0] * B; ops['ozf'] += 1
            return [[sum(z[i2][t_] * pow(WQ, i2 * j2, P) for i2 in range(Q)) % P for t_ in range(B)] for j2 in range(Q)]
        for j1 in range(pc_):
            forms = {}
            def form(x):
                if id(x) not in forms: forms[id(x)] = assemble(x, j1)
                return forms[id(x)]
            fold = []
            for j2 in range(Q):
                o = j1 + pc_ * j2
                accn = [0] * NB
                for a_, c_, sg in prods:
                    ta, tc_ = dft(form(a_)[j2], W, NB), dft(form(c_)[j2], W, NB)
                    accn = [(x + sg * y * z_) % P for x, y, z_ in zip(accn, ta, tc_)]
                slot = [x * inv(NB) % P for x in dft(accn, inv(W), NB)]
                fo = pow(W2, o, P)
                fold.append([(slot[t_] + fo * slot[B + t_]) % P if B + t_ < NB - 1 else slot[t_] for t_ in range(B)])
            for t_ in range(B):                 # inverse across the Q points, then the weight w^(-j1 s) of each piece s of the window
                col = [fold[j2][t_] for j2 in range(Q)]
                U = [sum(col[j2] * pow(inv(WQ), j2 * t2, P) for j2 in range(Q)) % P for t2 in range(Q)]
                for k_ in range(tc):
                    s = A_ + k_
                    wgt = tw[n2 - (j1 * s) % n2]
                    acc[k_][t_] = (acc[k_][t_] + wgt * U[s % Q]) % P
        for k_ in range(tc):
            s = A_ + k_
            for t_ in range(B):
                pos = s * B + t_
                if ws <= pos < ws + outlen and s <= ns: out[pos - ws] = (out[pos - ws] + acc[k_][t_] * inv(n2)) % P
        return ops, n2, pc_
    for pc in (1, 2, 3, 4, 6, 8):
        for la, lc in ((30, 29), (60, 37), (25, 25)):
            a, c = rnd(la), rnd(lc); ref = school(a, c)
            for ws, ol in ((0, la + lc - 1), (la - 2, lc - 1), (17, 40)):
                ol = min(ol, la + lc - 1 - ws)
                out = [0] * ol; chunk_product([(a, c, 1)], ws, ol, out, pc)
                assert out == ref[ws:ws + ol], ('chunk', pc, la, lc, ws, ol)
        a, c, d_ = rnd(40), rnd(29), rnd(22)
        ref = [(x - y) % P for x, y in zip(school(a, c) + [0] * 60, school(d_, c) + [0] * 60)]
        out = [0] * 64; chunk_product([(a, c, 1), (d_, c, -1)], 0, 64, out, pc); assert out == ref[:64]
    a = rnd(60); ref = school(a, a); out = [0] * 119; chunk_product([(a, a, 1)], 0, 119, out, 4); assert out == ref      # the square
    a = rnd(30); c = rnd(31); base = rnd(30); out = list(base); chunk_product([(a, c, -1)], 0, 30, out, 4)      # subtraction into an array (the placement of stage C)
    assert out == [(x - y) % P for x, y in zip(base, school(a, c)[:30])]
    # the counts of the model (chunk_fill_ops): per chunk, min(k, Q) ocp, k - min(k, Q) oax, Q - k ozf calls for an operand of k blocks
    for pc in (1, 2, 4, 8):
        a, c = rnd(60), rnd(37); ops, n2_, pc_ = chunk_product([(a, c, 1)], 0, 96, [0] * 96, pc)
        Q_ = n2_ // pc_; ks = [len(blocks(a)), len(blocks(c))]
        assert ops == {'ocp': pc_ * sum(min(k_, Q_) for k_ in ks), 'oax': pc_ * sum(k_ - min(k_, Q_) for k_ in ks), 'ozf': pc_ * sum(max(0, Q_ - k_) for k_ in ks)}, (ops, pc)
    # 7. stage B at any number of cosets: geometric nodes n_k = z^k, z = u^B with u = 4 (v_k = 2^k); the solve per position is two correlations of length kappa (chirp-z), checked at kappa = 7
    kappa, m = 7, 80
    g = rnd(m + 1); zeta = W; omega = zeta * zeta % P
    u = [pow(4, k, P) for k in range(kappa)]
    z = pow(4, B, P); nodes = [pow(z, k, P) for k in range(kappa)]; assert nodes == [pow(x, B, P) for x in u] and len(set(nodes)) == kappa
    wk = []
    for k in range(kappa):
        vals = [sum(g[j] * pow(u[k] * pow(omega, i, P), j, P) for j in range(m + 1)) % P for i in range(B)]
        coef = [x * inv(B) % P for x in dft(vals, inv(omega), B)]
        wk.append([coef[j] * inv(pow(u[k], j, P)) % P for j in range(B)])
    cz2 = lambda n_: n_ * (n_ - 1) // 2
    # M(X) = prod (X - z^k) by the q-binomial theorem: m_(kappa-j) = (-1)^j z^C(j,2) [kappa, j]_z
    qb = [1]
    for j in range(1, kappa + 1):
        qb.append(qb[-1] * (pow(z, kappa - j + 1, P) - 1) % P * inv(pow(z, j, P) - 1) % P)
    mc = [0] * (kappa + 1)
    for j in range(kappa + 1): mc[kappa - j] = (-1) ** j * pow(z, cz2(j), P) * qb[j] % P
    M_ = [1]
    for k in range(kappa):
        M_ = [((M_[i - 1] if i > 0 else 0) - nodes[k] * (M_[i] if i < len(M_) else 0)) % P for i in range(len(M_) + 1)]
    assert M_ == mc
    def mprime(k):                      # M'(z^k) in closed form: z^(C(k,2) + k (kappa-1-k)) prod_(j <= k) (z^j - 1) prod_(j <= kappa-1-k) (1 - z^j)
        d1 = 1
        for j in range(1, k + 1): d1 = d1 * (pow(z, j, P) - 1) % P
        d2 = 1
        for j in range(1, kappa - k): d2 = d2 * (1 - pow(z, j, P)) % P
        return pow(z, cz2(k) + k * (kappa - 1 - k), P) * d1 % P * d2 % P
    for k in range(kappa):
        nv = 1
        for l in range(kappa):
            if l != k: nv = nv * (nodes[k] - nodes[l]) % P
        assert mprime(k) == nv
    S_ = pad23(2 * kappa - 1); WS = root(S_)
    def corr(f, gg, n):                 # c_j = sum_k f_k gg_(k+j), j < n, by one cyclic convolution of length S_ >= 2 kappa - 1 (the chirp-z form)
        X = dft(f[::-1], WS, S_); Y = dft(gg, WS, S_)
        prod = dft([a_ * b_ % P for a_, b_ in zip(X, Y)], inv(WS), S_)
        return [prod[len(f) - 1 + j] * inv(S_) % P for j in range(n)]
    chirp = [pow(z, cz2(n_), P) for n_ in range(2 * kappa - 1)]
    rec = [0] * (kappa * B)
    for j in range(B):
        a_k = [wk[k][j] * inv(mprime(k)) % P for k in range(kappa)]
        f = [a_k[k] * inv(pow(z, cz2(k), P)) % P for k in range(kappa)]
        Aj = [x * inv(pow(z, cz2(jj), P)) % P for jj, x in enumerate(corr(f, chirp, kappa))]          # A(j) = sum_k a_k z^(kj), first convolution
        assert Aj == [sum(a_k[k] * pow(z, k * jj, P) for k in range(kappa)) % P for jj in range(kappa)]
        # h_t = sum_(i > t) m_i A(i-t-1) = sum_j m_(t+1+j) A(j): the second correlation (m_1, ..., m_kappa against A)
        hh = corr(Aj, mc[1:], kappa)
        for t_ in range(kappa): rec[j + t_ * B] = hh[t_]
    assert rec == g + [0] * (kappa * B - len(g))
    # 8. the streamed schedule of proof.md 4.5 at small sizes
    def polydivmod(num, den):                 # den monic: quotient and remainder
        num = list(num); q_ = [0] * max(0, len(num) - len(den) + 1)
        for i in range(len(num) - len(den), -1, -1):
            c_ = num[i + len(den) - 1]; q_[i] = c_
            for j in range(len(den)): num[i + j] = (num[i + j] - c_ * den[j]) % P
        return q_, num[:len(den) - 1]
    # 8a. the squaring step with the persistent forms of MU and g: the forms are made once (the dictionaries below) and used by every step; scheme (a) and scheme (b)
    m8 = 29
    g8 = rnd(m8) + [1]                                              # monic, m + 1 coefficients
    MU8 = polydivmod([0] * (2 * m8 - 2) + [1], g8)[0]               # floor(x^(2m-2) / g), m - 1 coefficients
    assert len(MU8) == m8 - 1
    made = {'a': 0, 'b': 0}
    pers_a = {}; pers_b = {}
    def prod_a(prods, ws, outlen, out):                              # scheme (a); the operands MU8 and g8 have persistent block spectra
        ns = max(len(blocks(a_)) + len(blocks(c_)) - 1 for a_, c_, _ in prods)
        loc = {}
        def tr(x, i):
            if x is MU8 or x is g8:
                if (id(x), i) not in pers_a: pers_a[(id(x), i)] = dft(blocks(x)[i], W, NB); made['a'] += 1
                return pers_a[(id(x), i)]
            if (id(x), i) not in loc: loc[(id(x), i)] = dft(blocks(x)[i], W, NB)
            return loc[(id(x), i)]
        for s_ in range(ns):
            if not (s_ * B < ws + outlen and (s_ + 2) * B - 1 > ws): continue
            acc = [0] * NB
            for a_, c_, sg in prods:
                for i in range(len(blocks(a_))):
                    j = s_ - i
                    if 0 <= j < len(blocks(c_)): acc = [(x + sg * y * z) % P for x, y, z in zip(acc, tr(a_, i), tr(c_, j))]
            slot = [x * inv(NB) % P for x in dft(acc, inv(W), NB)]
            for t_ in range(NB - 1):
                pos = s_ * B + t_
                if ws <= pos < ws + outlen: out[pos - ws] = (out[pos - ws] + slot[t_]) % P
    def prod_b(prods, ws, outlen, out):                              # scheme (b); the persistent operands are kept as outer-domain arrays (B coefficients per outer point), the inner transform is repeated at each use
        ns = max(len(blocks(a_)) + len(blocks(c_)) - 1 for a_, c_, _ in prods)
        s0 = max(0, (ws + 1) // B - 3)
        while (s0 + 2) * B - 1 <= ws: s0 += 1
        s1 = -(-(ws + outlen) // B) + 2
        while s1 * B >= ws + outlen: s1 -= 1
        n2 = pad23(max(s1 + 2, ns + 1 - s0)); W2 = root(n2)
        loc = {}
        def arrays(x):                                               # the outer-domain arrays of x: for each outer point o the polynomial sum_i W2^(o i) x_i
            def build():
                bl = blocks(x); rows = []
                for o in range(n2):
                    pol = [0] * B
                    for i, blk_ in enumerate(bl):
                        f = pow(W2, o * i, P)
                        for t_, v_ in enumerate(blk_): pol[t_] = (pol[t_] + f * v_) % P
                    rows.append(pol)
                return rows
            if x is MU8 or x is g8:
                if (id(x), n2) not in pers_b: pers_b[(id(x), n2)] = build(); made['b'] += 1
                return pers_b[(id(x), n2)]
            if id(x) not in loc: loc[id(x)] = build()
            return loc[id(x)]
        folded = []
        for o in range(n2):
            acc = [0] * NB
            for a_, c_, sg in prods:
                ta, tc = dft(arrays(a_)[o], W, NB), dft(arrays(c_)[o], W, NB)
                acc = [(x + sg * y * z) % P for x, y, z in zip(acc, ta, tc)]
            slot = [x * inv(NB) % P for x in dft(acc, inv(W), NB)]
            fo = pow(W2, o, P)
            folded.append([(slot[t_] + fo * slot[B + t_]) % P if B + t_ < NB - 1 else slot[t_] for t_ in range(B)])
        for t_ in range(B):
            piece = [x * inv(n2) % P for x in dft([folded[o][t_] for o in range(n2)], inv(W2), n2)]
            for s_ in range(n2):
                pos = s_ * B + t_
                if ws <= pos < ws + outlen and s_ <= ns: out[pos - ws] = (out[pos - ws] + piece[s_]) % P
    def step(R_, prod):
        T_ = [0] * (2 * m8 - 1); prod([(R_, R_, 1)], 0, 2 * m8 - 1, T_)             # (1) R^2: the low m coefficients stay in F, the other m - 1 are T1
        F_ = T_[:m8]; T1 = T_[m8:]
        q_ = [0] * (m8 - 1); prod([(T1, MU8, 1)], m8 - 2, m8 - 1, q_)               # (2) q = window [m-2, 2m-3) of T1 * MU
        prod([(q_, g8, -1)], 0, m8, F_)                                              # (3) (q g)[0..m-1] subtracted from F by the placement
        return F_
    for prod, kind in ((prod_a, 'a'), (prod_b, 'b')):
        R_ = rnd(m8); ref = R_
        for _ in range(3):
            R_ = step(R_, prod); ref = polydivmod(school(ref, ref), g8)[1]
            assert R_ == ref, ('step', kind)
        assert made[kind] > 0
    assert made['a'] == len(blocks(MU8)) + len(blocks(g8)), 'the persistent block spectra of MU and g are made once in scheme (a)'
    assert made['b'] == 2, 'the persistent outer-domain arrays of MU and g are made once in scheme (b)'
    # 8a'. the regeneration of g from its persistent form (the coefficients of g are freed once the form exists): scheme (a) inverse transforms each block spectrum, scheme (b) inverse transforms the persistent
    # array across the blocks in place (scaled by 1/n2) and the forward outer transform restores it
    for i, bl_ in enumerate(blocks(g8)):
        dec = [x * inv(NB) % P for x in dft(pers_a[(id(g8), i)], inv(W), NB)]
        assert dec[:len(bl_)] == bl_ and all(x == 0 for x in dec[len(bl_):])
    (key_,) = [k_ for k_ in pers_b if k_[0] == id(g8)]; n2g = key_[1]; rows_ = pers_b[key_]; W2g = root(n2g)
    dec_blocks = [[0] * B for _ in range(n2g)]
    for t_ in range(B):
        piece = [x * inv(n2g) % P for x in dft([rows_[o][t_] for o in range(n2g)], inv(W2g), n2g)]
        for s_ in range(n2g): dec_blocks[s_][t_] = piece[s_]
    flat = [x for bl_ in dec_blocks for x in bl_]
    assert flat[:len(g8)] == g8 and all(x == 0 for x in flat[len(g8):])
    for o in range(n2g):
        pol = [0] * B
        for s_ in range(n2g):
            f = pow(W2g, o * s_, P)
            for t_ in range(B): pol[t_] = (pol[t_] + f * dec_blocks[s_][t_]) % P
        assert pol == rows_[o], 'the forward outer transform restores the persistent array'
    # 8b. apply_inv with a sliding window of kR + 1 block spectra of each of a and b, c written over a and d over b (arrays of nres elements)
    def apply_inv_stream(R4, a_, b_, nres):
        r11, r12, r21, r22 = R4
        SR = {nm: [dft(bl, W, NB) for bl in blocks(x)] for nm, x in (('r11', r11), ('r12', r12), ('r21', r21), ('r22', r22))}   # the forms of the entries
        kR = max(len(v) for v in SR.values())
        A_ = list(a_) + [0] * (nres - len(a_)); B_ = list(b_) + [0] * (nres - len(b_))
        lens = {'a': len(a_), 'b': len(b_)}; arrs = {'a': A_, 'b': B_}
        win = {'a': {}, 'b': {}}; over = {'a': set(), 'b': set()}; made_ = {'a': 0, 'b': 0}; maxwin = 0
        def spec(w, j):
            if j in win[w] or j * B >= lens[w]: return
            assert j not in over[w], 'a block was overwritten before it was transformed'
            win[w][j] = dft(arrs[w][j * B:(j + 1) * B], W, NB); made_[w] += 1
        for s_ in range(-(-nres // B)):
            for j in (s_, s_ + 1): spec('a', j); spec('b', j)                    # the block after the slot is transformed before the slot is placed
            for w in 'ab':
                for j in [j for j in win[w] if j < s_ - kR + 1]: del win[w][j]
                maxwin = max(maxwin, len(win[w]))
            def slot(terms):
                acc = [0] * NB
                for nm, w, sg in terms:
                    for i, sr in enumerate(SR[nm]):
                        j = s_ - i
                        if j in win[w]: acc = [(x + sg * y * z) % P for x, y, z in zip(acc, sr, win[w][j])]
                return [x * inv(NB) % P for x in dft(acc, inv(W), NB)]
            outs_ = (('a', slot([('r22', 'a', 1), ('r12', 'b', -1)])), ('b', slot([('r11', 'b', 1), ('r21', 'a', -1)])))
            for w, sl in outs_:
                for t_ in range(NB - 1):
                    pos = s_ * B + t_
                    if pos >= nres: break
                    arrs[w][pos] = (arrs[w][pos] + sl[t_]) % P if (t_ < B - 1 and s_ > 0) else sl[t_]     # the B - 1 positions that the previous slot also wrote are added, the others stored
                over[w].update(j for j in (s_, s_ + 1) if j * B < nres)
        assert maxwin <= kR + 1 and made_['a'] == len(blocks(a_)) and made_['b'] == len(blocks(b_)), (maxwin, kR)
        return A_, B_
    for la_, lb_, ents in ((60, 59, (33, 34, 25, 31)), (40, 41, (13, 12, 9, 14)), (61, 30, (24, 25, 12, 26))):
        R4 = [rnd(x) for x in ents]; a_, b_ = rnd(la_), rnd(lb_); nres = max(la_, lb_)
        cc_, dd_ = apply_inv_stream(R4, a_, b_, nres)
        r11, r12, r21, r22 = R4
        ec = [(x - y) % P for x, y in zip(school(r22, a_) + [0] * 300, school(r12, b_) + [0] * 300)]
        ed = [(x - y) % P for x, y in zip(school(r11, b_) + [0] * 300, school(r21, a_) + [0] * 300)]
        assert cc_ == ec[:nres] and dd_ == ed[:nres], ('apply_inv stream', la_, lb_)
        oc_ = [0] * nres; od_ = [0] * nres                                   # scheme (b), the outputs one after the other: c = r22 a - r12 b, then d = r11 b - r21 a
        prod_b([(a_, r22, 1), (b_, r12, -1)], 0, nres, oc_); prod_b([(b_, r11, 1), (a_, r21, -1)], 0, nres, od_)
        assert oc_ == ec[:nres] and od_ == ed[:nres], ('apply_inv scheme (b), outputs in turn', la_, lb_)
    # 8c. the 2 x 2 matrix product by rows: the spectra of B held whole, those of one row of A at a time, each row forming its two outputs
    A4 = [rnd(30), rnd(31), rnd(29), rnd(36)]; B4 = [rnd(35), rnd(26), rnd(13), rnd(37)]
    SB = [[dft(bl, W, NB) for bl in blocks(x)] for x in B4]
    for i in range(2):
        SA = [[dft(bl, W, NB) for bl in blocks(A4[2 * i + t_])] for t_ in range(2)]        # the row of A, freed after the row
        for j in range(2):
            ln = max(len(A4[2 * i + t_]) + len(B4[2 * t_ + j]) - 1 for t_ in range(2)); out = [0] * ln
            for s_ in range(-(-ln // B) + 1):
                acc = [0] * NB
                for t_ in range(2):
                    for u_, sa_ in enumerate(SA[t_]):
                        v_ = s_ - u_
                        if 0 <= v_ < len(SB[2 * t_ + j]): acc = [(x + y * z) % P for x, y, z in zip(acc, sa_, SB[2 * t_ + j][v_])]
                sl = [x * inv(NB) % P for x in dft(acc, inv(W), NB)]
                for t_ in range(NB - 1):
                    pos = s_ * B + t_
                    if pos < ln: out[pos] = (out[pos] + sl[t_]) % P
            ref = [0] * 80
            for t_ in range(2):
                for k_, x in enumerate(school(A4[2 * i + t_], B4[2 * t_ + j])): ref[k_] = (ref[k_] + x) % P
            assert out == ref[:ln], ('rows', i, j)
    # the real constants: z = 4^B (B = 3 * 2^31) has order greater than every kappa used (kappa < ZB): p - 1 = 2^32 * 3 * 463 * c; the loop below checks that the odd number c has no divisor
    # between 3 and ZB, so the divisors of p - 1 up to ZB are the numbers 2^a 3^b 463^e, and z^d != 1 for each of them
    ZB = 2 * 10 ** 8
    Br = 3 << 31; zr = pow(4, Br, P)
    cc_ = P - 1
    ex_ = {}
    for q_ in (2, 3, 463):
        ex_[q_] = 0
        while cc_ % q_ == 0: cc_ //= q_; ex_[q_] += 1
    assert ex_ == {2: 32, 3: 1, 463: 1} and cc_ % 2 == 1
    assert all(cc_ % q_ for q_ in range(3, ZB + 1, 2))
    assert zr != 1 and all(pow(zr, (1 << a_) * 3 ** b_ * 463 ** c_, P) != 1 for a_ in range(33) for b_ in range(2) for c_ in range(2) if (1 << a_) * 3 ** b_ * 463 ** c_ <= ZB)
    print('ok: block products, windows, subtraction placement, bilinear form, multi-block matrix entries, 2 x 2 matrix product, outer-NTT scheme, streamed squaring step with persistent forms and the regeneration of g from its form (both schemes), apply_inv with a sliding window and outputs over the inputs (scheme (b): outputs in turn), matrix product by rows, coset interpolation (Vandermonde at kappa = 3, geometric nodes at kappa = 7); nodes u_k^B (k = 1, 2, 3) distinct at B = 3 * 2^31; z^d != 1 for all d | p - 1 below ZB')

if __name__ == '__main__':
    main()
```

### G.2 small_checks.py (this package)

Small-size checks over the Pallas field, written for this package (standard library only, about 1 s): the half-gcd of 4.4 with the truncated second call against the plain Euclidean algorithm (matrix, degree count, reduced pair; the quotient and return tests never fail on random pairs; every recursive call runs on at most `2k + 1` coefficients), scheme (c) of 4.5 against schoolbook products modulo `X^(n2 HB) - 1` (windows, a signed bilinear form, `nc = 1, 2, 4`), and the squaring step of e6dcb600's coefficient-domain stage C with the cyclic and with the exact `q g` against the remainder of the square (part (3); that step is not executed by this package, whose stage C is 4.6, and is kept as the check of the ledger's validation path `powx_lean`). Output of `python3 small_checks.py`:

```
(1) truncated half-gcd: ok (1344 calls; largest operand length / (2k + 1) over the recursive calls = 1.000; quotient and return tests passed)
(2) scheme (c), chunked outer product: ok
(3) squaring step, cyclic and exact q g: ok
```

```python
#!/usr/bin/env python3
"""Small-size checks over the Pallas field of the stage C and stage D procedures of proof.md 4.4 and 4.5 (standard library only).
  (1) the half-gcd of 4.4 with the truncated second call, against the plain Euclidean algorithm stopped at the same degree sum:
      matrix, degree count and reduced pair; on normal pairs the quotient test and the return test of 4.4 never fail;
      every call runs on at most 2k + 1 coefficients;
  (2) scheme (c) of 4.5 (twist and fold, outer transform of n2/nc points, inner transform, fold modulo X^HB - w^o, inverse,
      untwist and accumulate over the chunks) against the schoolbook product reduced modulo X^(n2 HB) - 1, for windows,
      a bilinear form of two signed products, and nc = 1, 2, 4;
  (3) the squaring step of e6dcb600's coefficient-domain stage C (its lemma 4.5; the validation path powx_lean of Appendix E, not executed by this package): q = window [m - 1, 2m - 1) of T1 * MU equals floor(A / g), and
      (A mod (X^N' - 1)) - ((q g) mod (X^N' - 1)) agrees with A mod g on [0, m), for N' >= m + 1 (the cyclic q g of scheme (c))
      and for the exact linear q g (scheme (a): no wrap of A is added), for the exponent bit b = 0 and 1.
Run: python3 small_checks.py   (prints ok for each part)."""
import random

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
GEN = 5                                  # 5 generates a subgroup containing the 2^32 * 3 part used here (checked below)


def trim(a):
    while a and a[-1] == 0: a.pop()
    return a


def add(a, b):
    n = max(len(a), len(b)); return trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % P for i in range(n)])


def sub(a, b):
    n = max(len(a), len(b)); return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % P for i in range(n)])


def mul(a, b):
    if not a or not b: return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b): out[i + j] = (out[i + j] + x * y) % P
    return trim(out)


def scal(a, c): return trim([x * c % P for x in a])


def divmod_(a, b):
    a = list(a); q = [0] * max(0, len(a) - len(b) + 1); inv = pow(b[-1], P - 2, P)
    for i in range(len(a) - len(b), -1, -1):
        c = a[i + len(b) - 1] * inv % P; q[i] = c
        if c:
            for j, y in enumerate(b): a[i + j] = (a[i + j] - c * y) % P
    return trim(q), trim(a)


def deg(a): return len(a) - 1


def quo_x(a, s): return trim(list(a[s:])) if s > 0 else list(a)


# ---------------------------------------------------------------- (1) the half-gcd with the truncated second call
I2 = ([1], [], [], [1])                  # 2x2 matrices as (r11, r12, r21, r22)


def mmul(A, B):
    return (add(mul(A[0], B[0]), mul(A[1], B[2])), add(mul(A[0], B[1]), mul(A[1], B[3])),
            add(mul(A[2], B[0]), mul(A[3], B[2])), add(mul(A[2], B[1]), mul(A[3], B[3])))


def apply_inv(R, h, a, b):
    s = 1 if h % 2 == 0 else P - 1
    return scal(sub(mul(R[3], a), mul(R[1], b)), s), scal(sub(mul(R[0], b), mul(R[2], a)), s)


STATS = {'maxlen_ratio': 0.0, 'calls': 0, 'abnormal': 0}


def hgcd(a, b, k, want_pair, depth=0):
    """returns (R, h, pair or None); the quotient test and the return test of 4.4 are counted in STATS['abnormal'] if they fail"""
    n = deg(a)
    STATS['calls'] += 1
    if depth > 0: STATS['maxlen_ratio'] = max(STATS['maxlen_ratio'], len(a) / (2 * k + 1))   # every recursive call
    if not b or n - deg(b) > k:
        return I2, 0, ((a, b) if want_pair else None)
    if k <= 4:                                   # base case: plain Euclid while the next quotient fits
        R, h, x, y = I2, 0, a, b
        while y and deg(x) - deg(y) <= k - h:
            q, r = divmod_(x, y)
            if deg(q) != 1: STATS['abnormal'] += 1
            R = mmul(R, (q, [1], [1], [])); h += deg(q); x, y = y, r
        return R, h, ((x, y) if want_pair else None)
    k1 = (k + 1) >> 1
    if 2 * k1 > n: k1 = n >> 1
    s = n - 2 * k1
    R1, h1, _ = hgcd(quo_x(a, s), quo_x(b, s), k1, False, depth + 1)
    c, d = apply_inv(R1, h1, a, b)
    if d and h1 != k1: STATS['abnormal'] += 1          # return test
    if not d or deg(c) - deg(d) > k - h1:
        return R1, h1, ((c, d) if want_pair else None)
    q, e = divmod_(c, d)
    if deg(q) != 1: STATS['abnormal'] += 1              # quotient test
    k3 = k - h1 - deg(q); s3 = deg(d) - 2 * k3
    if s3 > 0:
        R2, h3, _ = hgcd(quo_x(d, s3), quo_x(e, s3), k3, False, depth + 1)
        pair = apply_inv(R2, h3, d, e) if want_pair else None
    else:
        R2, h3, pair = hgcd(d, e, k3, want_pair, depth + 1)
    if (pair[1] if pair else apply_inv(R2, h3, d, e)[1]) and h3 != k3: STATS['abnormal'] += 1
    return mmul(mmul(R1, (q, [1], [1], [])), R2), h1 + deg(q) + h3, pair


def euclid_to(a, b, k):
    R, h, x, y = I2, 0, a, b
    while y and deg(x) - deg(y) <= k - h:
        q, r = divmod_(x, y)
        R = mmul(R, (q, [1], [1], [])); h += deg(q); x, y = y, r
    return R, h, (x, y)


def check_hgcd(rnd):
    for trial in range(40):
        n = rnd.randrange(8, 130)
        a = [rnd.randrange(P) for _ in range(n)] + [1]
        b = [rnd.randrange(P) for _ in range(n - 1)] + [rnd.randrange(1, P)]
        for k in ((n + 1) // 2, rnd.randrange(5, n)):
            R, h, pair = hgcd(a, b, k, True)
            R0, h0, pair0 = euclid_to(a, b, k)
            assert (R, h, pair) == (R0, h0, pair0), (n, k)
            assert h == k, 'a random pair is normal: the degree count equals the parameter'
    assert STATS['abnormal'] == 0
    assert STATS['maxlen_ratio'] <= 1.0 + 1e-12, STATS['maxlen_ratio']
    return STATS


# ---------------------------------------------------------------- (2) scheme (c), chunked outer product modulo Y^n2 - 1, Y = X^HB
def root(n):
    assert (P - 1) % n == 0
    w = pow(GEN, (P - 1) // n, P)
    assert pow(w, n, P) == 1 and all(pow(w, n // f, P) != 1 for f in (2, 3) if n % f == 0)
    return w


def dft(x, w):
    n = len(x); return [sum(x[i] * pow(w, i * k, P) for i in range(n)) % P for k in range(n)]


def blocks(A, HB, n):
    return [[(A[i * HB + t] if i * HB + t < len(A) else 0) for t in range(HB)] for i in range(n)]


def chunked(prods, HB, n2, nc, nout):
    """prods: list of (out, sign, A, B); returns the outputs modulo X^(n2 HB) - 1 (coefficient lists of n2 HB)"""
    NB = 2 * HB; w = root(n2); wNB = root(NB); n3 = n2 // nc; wc = pow(w, nc, P)
    kmax = max(max(-(-len(A) // HB), -(-len(B) // HB)) for _, _, A, B in prods)
    out = [[0] * (n2 * HB) for _ in range(nout)]
    for j in range(nc):
        def chunk(A):
            Ab = blocks(A, HB, -(-len(A) // HB))
            z = [[0] * HB for _ in range(n3)]
            for i, blk_ in enumerate(Ab):                 # twist by w^(j i) and fold i modulo n3
                f = pow(w, j * i, P)
                for t in range(HB): z[i % n3][t] = (z[i % n3][t] + f * blk_[t]) % P
            cols = [dft([z[u][t] for u in range(n3)], wc) for t in range(HB)]   # outer transform across the rows
            return [[cols[t][u] for t in range(HB)] for u in range(n3)]
        CA = [(o, sg, chunk(A), chunk(B)) for o, sg, A, B in prods]
        res = [[[0] * HB for _ in range(n3)] for _ in range(nout)]
        for u in range(n3):
            wo = pow(w, j + nc * u, P)
            acc = [[0] * NB for _ in range(nout)]
            for o, sg, ca, cb in CA:                     # inner transform, pointwise product (signed), summed
                fa = dft(ca[u] + [0] * HB, wNB); fb = dft(cb[u] + [0] * HB, wNB)
                for t in range(NB): acc[o][t] = (acc[o][t] + sg * fa[t] * fb[t]) % P
            for o in range(nout):
                c = dft(acc[o], pow(wNB, P - 2, P)); invNB = pow(NB, P - 2, P)
                c = [x * invNB % P for x in c]
                res[o][u] = [(c[t] + wo * c[t + HB]) % P for t in range(HB)]   # fold modulo X^HB - w^o
        for o in range(nout):
            cols = [dft([res[o][u][t] for u in range(n3)], pow(wc, P - 2, P)) for t in range(HB)]  # inverse outer transform (times n3)
            for s in range(n2):                          # untwist and accumulate: piece s += w^(-j s) z_(s mod n3)
                f = pow(w, (n2 - (j * s) % n2) % n2, P) * pow(n2, P - 2, P) % P
                for t in range(HB): out[o][s * HB + t] = (out[o][s * HB + t] + f * cols[t][s % n3]) % P
    return out


def cyc(a, L):
    out = [0] * L
    for i, x in enumerate(a): out[i % L] = (out[i % L] + x) % P
    return out


def check_chunked(rnd):
    HB = 4
    for n2 in (4, 6, 8, 12):
        for nc in (1, 2, 4):
            if n2 % nc or (n2 // nc) % 1: continue
            if not ((n2 // nc) & (n2 // nc - 1) == 0 or ((n2 // nc) % 3 == 0 and ((n2 // nc // 3) & (n2 // nc // 3 - 1)) == 0)): continue
            L = n2 * HB
            A = [rnd.randrange(P) for _ in range(rnd.randrange(HB + 1, L))]; B = [rnd.randrange(P) for _ in range(rnd.randrange(HB + 1, L))]
            C = [rnd.randrange(P) for _ in range(rnd.randrange(1, L))]; D = [rnd.randrange(P) for _ in range(rnd.randrange(HB + 1, L))]
            got = chunked([(0, 1, A, B), (0, P - 1, C, D), (1, 1, A, D)], HB, n2, nc, 2)
            want0 = cyc(sub(mul(A, B), mul(C, D)), L); want1 = cyc(mul(A, D), L)
            assert got[0] == want0 and got[1] == want1, (n2, nc)
            ws = rnd.randrange(0, L // 2); ln = rnd.randrange(1, L - ws)        # a window of the cyclic result
            assert got[0][ws:ws + ln] == want0[ws:ws + ln]
    return True


# ---------------------------------------------------------------- (3) the squaring step (lemma 4.5)
def check_step(rnd):
    HB = 4
    for m in (9, 13, 22, 30):
        g = [rnd.randrange(P) for _ in range(m)] + [1]
        MU, _ = divmod_([0] * (2 * m - 1) + [1], g)               # floor(X^(2m-1) / g)
        for b in (0, 1):
            R = [rnd.randrange(P) for _ in range(m)]
            A = mul(R, R)
            if b: A = [0] + A                                       # S^b R^2: the offset of the square by one coefficient
            A = A + [0] * (2 * m - len(A))
            T1 = trim(list(A[m:2 * m])); A0 = trim(list(A[:m]))
            q = trim(list(mul(T1, MU)[m - 1:2 * m - 1]))           # window [m - 1, 2m - 1)
            qq, rem = divmod_(trim(list(A)), g)
            assert q == qq, (m, b)
            # exact linear q g (scheme (a)): A[0..m) - (q g)[0..m) is the remainder
            qg = mul(q, g) + [0] * (2 * m)
            r_exact = trim([(A[i] - qg[i]) % P for i in range(m)])
            assert r_exact == rem
            # cyclic q g modulo X^N' - 1 (scheme (c)), N' = n2' HB >= m + 1, with the wrap of A added to Fn
            n2p = 1
            while n2p * HB < m + 1: n2p *= 2
            Np = n2p * HB
            Fn = list(A[:m]) + [0] * (Np - m)
            for i in range(2 * m - Np):                              # Fn[i] += T1[i + N' - m]
                if i < m: Fn[i] = (Fn[i] + A[i + Np]) % P
            qgc = chunked([(0, 1, q, g)], HB, n2p, 1, 1)[0] if len(q) > HB and len(g) > HB else cyc(mul(q, g), Np)
            r_cyc = trim([(Fn[i] - qgc[i]) % P for i in range(m)])
            assert r_cyc == rem, (m, b)
    return True


if __name__ == '__main__':
    rnd = random.Random(20261017)
    st = check_hgcd(rnd)
    print('(1) truncated half-gcd: ok (%d calls; largest operand length / (2k + 1) over the recursive calls = %.3f; quotient and return tests passed)' % (st['calls'], st['maxlen_ratio']))
    print('(2) scheme (c), chunked outer product: ok' if check_chunked(rnd) else 'FAIL')
    print('(3) squaring step, cyclic and exact q g: ok' if check_step(rnd) else 'FAIL')
```

### G.3 vd_check.py (this package): the group facts of 4.6 and the eight steps at toy size

Written for this package (standard library only, about 12 s). Part (1) checks the facts that 4.6 uses about the field: the factorisation `p - 1 = 2^32 * 3 * 463 * q1 * q2` with `q1 = 539,204,044,132,271,846,773` prime (deterministic Miller-Rabin with the bases 2 to 41, valid below 3.3e24), that 5 is a non-square so that `omega = 5^((p-1)/2^32)` has order exactly `2^32`, and that `z = 5^(2^32)` satisfies `z^((p-1)/q1) != 1`, so `q1` divides the order of `z` and the order exceeds `2K` at every round count up to 21 (the nodes are distinct, the cosets disjoint). Part (2) runs the eight steps of 4.6 literally at toy size over the Pallas field (`h = 16`, `K = 3`, `n1 = 48`, a random monic `g` of degree `m = 40`, the start `v = 32`, `ell = 41`, the full exponent `(p-1)/2`: the Barrett start, the values of `g` and `q` on the cosets, the extensions of lemma 4.7 by the kernel `kappa(e) = 1/(z^e - 1)` in both directions (the second through the identity `z^t - z^(K+i) = -z^t (z^(K+i-t) - 1)` with the same kernel; the reversed-row form that the ledger charges is this sum re-indexed), the batch inversion with the zero test, the Montgomery loop of lemma 4.6 and the exit), interpolates `W` from its values on `O2` at every step to check the degree bound and the congruence of lemma 4.6, and compares the result with `S^((p-1)/2) mod g` computed directly by square-and-multiply. The transforms of the toy are direct evaluations (the inner transform of 4.2 and the chirp-z convolutions of section 3 are standard; what the toy checks is the algebra of the stage). Output of `python3 vd_check.py`:

```
(1) group facts: q1 prime, q2 = 143 bits, 5 non-square, ord(omega) = 2^32, q1 | ord(z): ok (ord(z) >= q1 = 5.392e+20 > 2K <= 1734723476 for r <= 21)
(2) the eight steps of 4.6 at h = 16, K = 3, m = 40 (248 loop steps, lemmas 4.6 and 4.7 checked at every step): ok
```

```python
#!/usr/bin/env python3
"""vd_check.py (this package, standard library only, about 12 s): checks of the value-domain stage C of proof.md 4.6.
  (1) the group facts: p - 1 = 2^32 * 3 * 463 * q1 * q2 with q1 = 539,204,044,132,271,846,773 prime (deterministic Miller-Rabin, bases 2..41, valid
      below 3.3e24); 5 is a non-square mod p, so omega = 5^((p-1)/2^32) has order exactly 2^32; z = 5^(2^32) has z^((p-1)/q1) != 1, so q1 divides
      the order of z and ord(z) >= q1 > 2K = 2 ceil((m+1)/2^32) at every r <= 21: the nodes z^k (k < 2K) are distinct and the cosets 5^k H disjoint;
  (2) the eight steps of 4.6 at toy size over the Pallas field (h = 16, K = 3, n1 = 48, m = 40, v = 32, ell = 41, the full exponent (p-1)/2):
      the Barrett start, the chirp-free evaluations, the extension of lemma 4.7 by the kernel kappa(e) = 1/(z^e - 1) (both directions, the second
      through z^t - z^(K+i) = -z^t (z^(K+i-t) - 1) with the same kernel), the batch inversion, the Montgomery loop of lemma 4.6 and the exit, against S^((p-1)/2) mod g computed directly;
      lemma 4.6's degree bound (deg W <= m - 1) is checked at every step by interpolating W from O2.
Run: python3 vd_check.py   (prints ok for each part)."""
import random

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
Q1 = 539204044132271846773


def miller_rabin(n):
    if n < 2: return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
    for s in small:
        if n % s == 0: return n == s
    d, r = n - 1, 0
    while d % 2 == 0: d //= 2; r += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True


def part1():
    rest = (P - 1) // ((1 << 32) * 3 * 463)
    assert (P - 1) == (1 << 32) * 3 * 463 * rest and rest % Q1 == 0
    q2 = rest // Q1
    assert miller_rabin(Q1), 'q1 composite'
    assert pow(5, (P - 1) // 2, P) == P - 1, '5 is a square'
    omega = pow(5, (P - 1) >> 32, P)
    assert pow(omega, 1 << 31, P) == P - 1 and pow(omega, 1 << 32, P) == 1
    z = pow(5, 1 << 32, P)
    assert pow(z, (P - 1) // Q1, P) != 1, 'q1 does not divide ord(z)'
    worst = 0
    for r in range(6, 22):
        m = (5 ** (6 + r) - 1) // 2
        K = -(-(m + 1) // (1 << 32)); worst = max(worst, 2 * K)
    assert Q1 > worst
    print('(1) group facts: q1 prime, q2 = %d bits, 5 non-square, ord(omega) = 2^32, q1 | ord(z): ok (ord(z) >= q1 = %.3e > 2K <= %d for r <= 21)' % (q2.bit_length(), Q1, worst))


# ---------------------------------------------------------------- polynomial helpers (coefficient lists, low degree first)
def trim(a):
    while a and a[-1] == 0: a.pop()
    return a


def pmul(a, b):
    out = [0] * (len(a) + len(b) - 1) if a and b else []
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b): out[i + j] = (out[i + j] + x * y) % P
    return trim(out)


def pdivmod(a, b):
    a = list(a); q = [0] * max(0, len(a) - len(b) + 1); inv = pow(b[-1], P - 2, P)
    for i in range(len(a) - len(b), -1, -1):
        c = a[i + len(b) - 1] * inv % P; q[i] = c
        if c:
            for j, y in enumerate(b): a[i + j] = (a[i + j] - c * y) % P
    return trim(q), trim(a)


def peval(a, x):
    v = 0
    for c in reversed(a): v = (v * x + c) % P
    return v


def interp(xs, ys):
    """Lagrange interpolation at distinct nodes (toy size)"""
    n = len(xs); out = [0] * n
    for i in range(n):
        num = [1]; den = 1
        for j in range(n):
            if j != i:
                num = pmul(num, [(-xs[j]) % P, 1]); den = den * (xs[i] - xs[j]) % P
        f = ys[i] * pow(den, P - 2, P) % P
        for k, c in enumerate(num): out[k] = (out[k] + f * c) % P
    return trim(out)


def part2(seed=1):
    rnd = random.Random(seed)
    h, K = 16, 3
    n1 = K * h; m = 40; v = 32; E = (P - 1) >> 1
    omega = pow(5, (P - 1) // h, P)                    # order h: h | 2^32 and 5 is a non-square
    assert pow(omega, h, P) == 1 and pow(omega, h // 2, P) != 1
    z = pow(5, h, P)
    nodes = [pow(z, k, P) for k in range(2 * K)]
    assert len(set(nodes)) == 2 * K
    cos = [[pow(5, k, P) * pow(omega, i, P) % P for i in range(h)] for k in range(2 * K)]     # C_k = 5^k H in the natural order i
    O1 = [x for k in range(K) for x in cos[k]]; O2 = [x for k in range(K, 2 * K) for x in cos[k]]
    assert len(set(O1 + O2)) == 2 * n1
    M = [1]
    for k in range(K): M = pmul(M, [(-nodes[k]) % P, 1])
    P1 = [0] * (n1 + 1)
    for i, c in enumerate(M): P1[i * h] = c                                              # P1(X) = M(X^h)
    Mn = [peval(M, nodes[k]) for k in range(2 * K)]                                       # M(n_k): 0 on O1's cosets, nonzero on O2's
    assert all(Mn[k] == 0 for k in range(K)) and all(Mn[k] != 0 for k in range(K, 2 * K))
    # the extension of lemma 4.7: values at the K nodes of one set -> the K nodes of the other, by the kernel kappa
    kappa = {e: pow((pow(z, e, P) - 1) % P, P - 2, P) for e in range(1, 2 * K)}
    Md = [pmul([1], [1])]
    def dM(nodes_known, x):
        d = 1
        for y in nodes_known:
            if y != x: d = d * (x - y) % P
        return d
    def extend(vals, known, wanted):
        """vals at the nodes z^known[i] -> values at z^wanted[t], with the Lagrange identity in the form of lemma 4.7"""
        nk = [pow(z, i, P) for i in known]; nw = [pow(z, t, P) for t in wanted]
        Mw = [1]
        for y in nk: Mw = pmul(Mw, [(-y) % P, 1])
        s = [vals[i] * pow(dM(nk, nk[i]), P - 2, P) % P for i in range(len(known))]
        out = []
        for t_i, t in enumerate(wanted):
            acc = 0
            for i_i, i in enumerate(known):
                e = t - i
                if e > 0: acc = (acc + s[i_i] * pow(z, (-i) % (P - 1), P) % P * kappa[e]) % P          # z^t - z^i = z^i (z^(t-i) - 1)
                else: acc = (acc - s[i_i] * pow(z, (-t) % (P - 1), P) % P * kappa[-e]) % P             # z^t - z^i = -z^t (z^(i-t) - 1): the reversed direction
            out.append(peval(Mw, nw[t_i]) * acc % P)
        return out
    # a random f of degree < n1: lemma 4.7 in both directions, against direct evaluation
    f = [rnd.randrange(P) for _ in range(n1)]
    for known, wanted in ((list(range(K)), list(range(K, 2 * K))), (list(range(K, 2 * K)), list(range(K)))):
        for j in range(h):
            Fj = [f[j + h * i] for i in range(K)]
            got = extend([peval(Fj, pow(z, i, P)) for i in known], known, wanted)
            assert got == [peval(Fj, pow(z, t, P)) for t in wanted], 'lemma 4.7'
    # values on a coset <-> the row numbers u_k^j F_j(n_k) (the inner transform); here by direct evaluation
    def values(poly, cosets):
        return [[peval(poly, x) for x in cos[k]] for k in cosets]
    def rows_from_values(V, cosets):
        """inverse inner transform per coset: h u_k^j F_j(n_k) / h"""
        hinv = pow(h, P - 2, P); out = []
        for k_i, k in enumerate(cosets):
            uk = pow(5, k, P); row = []
            for j in range(h):
                sj = sum(V[k_i][i] * pow(omega, (-i * j) % h, P) for i in range(h)) % P * hinv % P
                row.append(sj * pow(pow(uk, j, P), P - 2, P) % P)                                     # F_j(n_k)
            out.append(row)
        return out
    def values_from_rows(Rw, cosets):
        out = []
        for k_i, k in enumerate(cosets):
            uk = pow(5, k, P)
            out.append([sum(Rw[k_i][j] * pow(uk, j, P) % P * pow(omega, i * j % h, P) for j in range(h)) % P for i in range(h)])
        return out
    def ext_values(V, src, dst):
        """the extension of values from the cosets src to the cosets dst: inverse inner transforms, lemma 4.7 per position, forward inner transforms"""
        Rw = rows_from_values(V, src)
        newrows = [[0] * h for _ in dst]
        for j in range(h):
            got = extend([Rw[k_i][j] for k_i in range(len(src))], src, dst)
            for k_i in range(len(dst)): newrows[k_i][j] = got[k_i]
        return values_from_rows(newrows, dst)
    # the modulus: monic g of degree m without a root in O1 (random: a root in O1 has probability ~ n1/p)
    g = [rnd.randrange(P) for _ in range(m)] + [1]
    assert all(peval(g, x) for x in O1)
    # (1) Barrett start: q = floor(X^v P1 / g) (toy: schoolbook), ell = v + n1 - m + 1 coefficients
    A = [0] * v + P1
    q, rem = pdivmod(A, g)
    assert len(q) == v + n1 - m + 1 == 41
    # (2) g on O1 and O2; (3) R~_0 on O2 = u_k^v M(n_k) - q g on O2 (v = 32 is a multiple of h: X^v = u_k^v on C_k)
    G1 = values(g, range(K)); G2 = values(g, range(K, 2 * K))
    Q2 = values(q, range(K, 2 * K))
    R2 = [[(pow(pow(5, k, P), v, P) * Mn[k] - Q2[k_i][i] * G2[k_i][i]) % P for i in range(h)] for k_i, k in enumerate(range(K, 2 * K))]
    assert R2 == values(rem, range(K, 2 * K))                                              # X^v P1 - q g = X^v P1 mod g
    # (4) R~_0 on O1
    R1 = ext_values(R2, list(range(K, 2 * K)), list(range(K)))
    assert R1 == values(rem, range(K))
    # (5) -1/g on O1 (batch inversion per coset, with the prefix-product zero test)
    for k_i in range(K):
        pref = 1
        for x in G1[k_i]: pref = pref * x % P
        assert pref != 0
        G1[k_i] = [(-pow(x, P - 2, P)) % P for x in G1[k_i]]
    # (6) the loop over the bits of E below the start v = 2^5 (the leading 1 and five zero bits absorbed)
    top = E.bit_length() - 1
    assert (E >> (top - 5)) == v
    Rt = list(rem); e = v                                                                  # R~ = S^e P1 mod g (coefficient form, for the checks only)
    nsteps = 0
    for bit in range(top - 6, -1, -1):
        b = (E >> bit) & 1
        U1 = [[R1[k_i][i] * R1[k_i][i] % P * G1[k_i][i] % P for i in range(h)] for k_i in range(K)]          # u0 on O1
        U2 = ext_values(U1, list(range(K)), list(range(K, 2 * K)))
        R2n = []
        for k_i, k in enumerate(range(K, 2 * K)):
            inv = pow(Mn[k], P - 2, P); uk = pow(5, k, P)
            row = []
            for i in range(h):
                w = (R2[k_i][i] * R2[k_i][i] + U2[k_i][i] * G2[k_i][i]) % P * inv % P
                if b: w = w * (uk * pow(omega, i, P) % P) % P                                                    # times x = u_k omega^i
                row.append(w)
            R2n.append(row)
        # lemma 4.6: W = (R~^2 + u0 g) / P1 has degree <= m - 1 and equals R~^2 P1^-1 mod g (checked by interpolation from the values on O2)
        W2 = interp(O2, [x for row in R2n for x in row])
        _, Rt2 = pdivmod(pmul(Rt, Rt), g)
        assert len(W2) - 1 <= m - 1 + b
        assert pdivmod(pmul(W2, P1), g)[1] == pdivmod([0] * b + Rt2, g)[1], 'lemma 4.6'
        R2 = R2n; R1 = ext_values(R2, list(range(K, 2 * K)), list(range(K)))
        Rt = pdivmod(W2, g)[1]; e = 2 * e + b; nsteps += 1
    assert e == E
    # (7) leaving the Montgomery form: R = R~ / P1 mod g
    U1 = [[R1[k_i][i] * G1[k_i][i] % P for i in range(h)] for k_i in range(K)]
    U2 = ext_values(U1, list(range(K)), list(range(K, 2 * K)))
    Rfin = [[(R2[k_i][i] + U2[k_i][i] * G2[k_i][i]) % P * pow(Mn[k], P - 2, P) % P for i in range(h)] for k_i, k in enumerate(range(K, 2 * K))]
    # (8) coefficient form from O2 (toy: Lagrange interpolation at the n1 points of O2)
    R = interp(O2, [x for row in Rfin for x in row])
    direct = [1]
    for bit in range(top, -1, -1):
        direct = pdivmod(pmul(direct, direct), g)[1]
        if (E >> bit) & 1: direct = pdivmod([0] + direct, g)[1]
    assert R == direct, 'S^E mod g'
    print('(2) the eight steps of 4.6 at h = 16, K = 3, m = 40 (%d loop steps, lemmas 4.6 and 4.7 checked at every step): ok' % nsteps)


if __name__ == '__main__':
    part1()
    part2()
```
