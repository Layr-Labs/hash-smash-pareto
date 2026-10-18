# Orchard Poseidon, r = 21: algebraic collision algorithm with stage C in the value domain. Two free rounds on a line, odd part about a random centre, half-gcd, at most 2 centres

## 1. Claim

Target: `poseidon-orchard-r21-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, twenty-one partial rounds 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 and 24, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

**Base entries and what this entry changes.** This entry is a revision of the r = 21 entry e6dcb600 (bradcush, normalized cost 122.911), which is itself a revision of the r = 21 entry f62fb39 (submitted by Jbenisek, commit a031a50); both are declared as dependencies of this submission. The construction, the algorithm outside stages C and D, the coins, the stopping rule, the premise `H-GEOM-w1` with its reduction, and the evidence are those of f62fb39 ("the base entry"), and their text is reproduced here (sections 2, 3, 4.1.1, 4.1.2, 4.2 except the new bullets, 4.3, 5, 9.1, 9.3, 9.4, 10, Appendices D, F and G.1), except for sentences that are this entry's or e6dcb600's: the first paragraph of 4.3, the last sentence of 9.3, the framing sentences of 10 and 10.5 that point to `H-NORMAL`, the sentences of 10.2 on the organizer's counts, and the scope figures of 10.4 and 10.5. In the reproduced text, "we" and "our" refer to the author of the base entry: the executed runs at r = 3, 4, 5, the Grok jobs, the sibling Euclid runs and the experiment programs are the base entry's evidence, cited as such; this entry did not repeat them, and the programs of Grok jobs 135, 137, 138 and 139 are not in this package (the base entry prints those of jobs 136 and the sibling runs); the organizer experiments of 10.2 have not been run for this package at the time of writing. The rows of the ledger other than C and D are the base entry's rows, unchanged, plus the two rows added by e6dcb600 (a second allowance for the plan_invN misses, 95,759 operations, and the allocator's statistics charge for the unexpanded rows, `6.4 * 10^11` per trial); the allocator's flat 64 per call is charged on every allocation and free of stages C and D. From e6dcb600 this entry keeps: the truncated second recursive call of the half-gcd (lemma 4.4), the charge of stage D for the normal remainder sequence with an ABORT at the first quotient of degree other than 1 (premise `H-NORMAL`, 6.3, 9.5), and scheme (c) of the block products (4.5). This entry changes three things:

1. *Stage C in the value domain (4.6, lemmas 4.6 and 4.7).* The residue `R~ = S^e P1 mod g` is held by its values on `O1` and `O2`, two sets of `2^32 * 867,361,738` points made of cosets of the subgroup of order `2^32` whose coset representatives raised to the power `2^32` form a geometric progression, and `P1` is the product of `X^(2^32) - n_k` over the cosets of `O1`. A modular squaring is a Montgomery reduction modulo `P1`: one pointwise pass on `O1`, an extension of the result to `O2`, one pointwise pass on `O2`, an extension back to `O1`. An extension is one transform of `2^32` points per coset and, per inner position, one convolution with a fixed kernel across the cosets (Lagrange interpolation at geometric nodes). No product of polynomials, no `MU` and no quotient appear in the loop, and the inner transforms carry no zero padding; the start `S^v P1 mod g` is one Barrett reduction, and the result is brought back to coefficient form by the interpolation of section 3. Row C falls from 4.06e24 to 1.08e24, and the stage C peak from 5.31 to 4.00 copies of `m` elements.
2. *Block products at the cheapest block length (4.5).* Scheme (c) is evaluated at every block length `2^b` (`b = 6 .. 31`) whose outer transform exists (`n2 <= 3 * 2^32`), and every product of stage D, also one that fits a single transform, uses the cheapest of the single transform, scheme (a) and scheme (c). Smaller blocks move transform layers from the zero-padded inner transforms to the unpadded outer ones.
3. *Stage D (4.4, lemma 4.8).* A node that wants its matrix only forms only the top window of `c` and `d` that the rest of the node reads; the base case works in place (no allocation per division step); the top node holds `g` and `R` as two pieces each, frees the high pieces as soon as no operation reads them, and forms `c`, then `d`, from the low pieces. Small calls run in a scratch region, and the arena is compacted when a request finds no hole (4.2). Row D falls from 1.36e24 to 1.06e24, and the stage D peak from 4.85 to 3.82 copies.

Appendix E (`stage_cd.py`) is the ledger with these changes; it prints and asserts the rows C and D, the peaks of the live set and `N_max`. Appendix G.4 (`vd_check.py`) runs stage C in the value domain at small sizes over the Pallas field against `S^E mod g` and checks its counted charges against the ledger; Appendix G.5 compares the half-gcd of the ledger, call by call, with the real algorithm (windows, pieces); G.2, G.3 and G.6 check the block products, the truncated half-gcd and the charges of scheme (c); G.7 (`alloc_sim.py`) replays the allocations and frees of stages C and D at r = 21 at their addresses in the arena.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and 578241159 inverse transforms (one per coset, section 3), compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod in the value domain (which ABORTs the trial if `g_c` vanishes on `O1`) and a half-gcd (which ABORTs the trial on an abnormal remainder sequence), and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. At most `K = 2` centres are tried, one after the other, on a single thread; the first verified collision ends the algorithm.
* `success_probability = 0.39560`: a lower bound for the probability, over the algorithm's fresh random words, that one of the `K` centres yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta + delta_C)^K - K (eps_iso + eps_coin)` with `q = 0.22257` (the bound for `P(1 <= k <= DMAX)` of section 9.2, from `H-GEOM-w1`), `delta = 2^-100` (the bound on an abnormal remainder sequence, from `H-NORMAL`), `delta_C < 2^-129` (a zero of `g_c` on `O1`, proved in 9.2(f)), `K = 2`, `eps_iso < 2^-48`, `eps_coin < 2^-128`. The value is `0.395602595` to nine decimals (section 9.2(f)).
* `time_log2 = 72.475` in target-compression units (`C(21) = 657` primitive operations per unit): the operation count of section 6, `T_fixed + K * T_trial` with every trial charged in full (stage D for the normal sequence, which bounds every trial since an abnormal one aborts; stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 4,307,721,017,619,165,469,436,718` operations, `log2(N_max / 657) = 72.4734495361`. Claimed as `72.475`: the count rounds up to 72.47345 at five decimals, and the claim rounds further up to three decimals, a margin of `4.6 * 10^21` operations (0.00155 bits) for any charge this count may have missed. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 68.693` (`476,837,370,801,240,364,492` bytes, section 7): the arena is the peak of the live set, and Appendix G.7 places every array of stages C and D at its address in an arena of that size with the allocator of 4.2, which compacts the arena 3 times per trial in stage D (charged). Normalized cost `72.475 + (68.693 - 20) = 121.168`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `130` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^27`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search, as in the base entry; the half-gcd is the padded half-gcd of Thome (2003) and Stehle and Zimmermann (2004); the squaring in the value domain is Montgomery's reduction (Montgomery 1985) in its residue-number-system form with two bases and base extensions (Bajard, Didier and Kornerup 1998), here for polynomials, with the extension done by Lagrange interpolation at geometric nodes (the chirp-z identities of Bluestein 1970 and Rabiner, Schafer and Rader 1969, as in section 3); the submission note repeats these credits.
* Declared heuristics (claim.json): `H-GEOM-w1` (score-critical, section 9.1, the base entry's premise, unchanged) and `H-NORMAL` (score-critical for the success probability only, section 9.5, from e6dcb600). The costs are the declared cost model, not heuristics: the charging rules of section 4.2, the register file of 18 words of 256 bits whose operands are not charged as loads (the base entry's disclosed interpretation of the model; every array access is charged), and the arena of section 7 sized at the peak of the live set. Everything else is proved or counted here: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the lemmas 4.4 (truncation), 4.6 (the step), 4.7 (extension) and 4.8 (windows and pieces), the bound on the stage C abort (9.2(f)), the Cauchy-Schwarz reduction (section 9.2), the isolation lemma (section 9.4), the independence of the centres, the cap rules and every operation count (sections 4, 6, 7).

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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 (partial), 60, 61, 62, 63 (full) put twenty-seven S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^27 = D = 7,450,580,596,923,828,125`. The leading coefficient is obtained by
propagating leading coefficients through the twenty-seven layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x036b153bb044072edf9f26b65249c0916ff2a474ed84a710a60ff678516cb3a3`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 3,725,290,298,461,914,062`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. At this r no transform of `H >= m + 1` points exists: `p - 1 = 2^32 * 3 * q` has roots of unity of order `3 * 2^a` for `a <= 32` only, and `m + 1 = 3,725,290,298,461,914,063 > 3 * 2^32`. Let `B = 3 * 2^31 = 6,442,450,944`, `zeta` a primitive `2B`-th root of unity (`2B = 3 * 2^32` divides `p - 1`) and `omega = zeta^2`, a primitive `B`-th root. Let `kappa = ceil((m + 1) / B) = 578241159`, `v_k = 2^k` and `u_k = v_k^2 = 4^k` for `k < kappa`, and `z = 4^B`; the `kappa` numbers `n_k = u_k^B = z^k` form a geometric progression and are pairwise distinct, because the order of `z` exceeds `kappa` (Appendix G: `z^d != 1` for every divisor `d` of `p - 1` up to `6 * 10^8`, and `kappa < 6 * 10^8`). The evaluation points are `s_{k,i} = v_k zeta^i` for `k < kappa`, `i < B`, so that `S_{k,i} = s_{k,i}^2 = u_k omega^i`, and `g_c(S_{k,i}) = (F(c + s_{k,i}) - F(c - s_{k,i})) / (2 s_{k,i})`. Write `g_c(x) = sum_{t < kappa} x^{tB} h_t(x)` with `deg h_t < B`. For `y = omega^i` we have `y^B = 1`, hence `g_c(u_k y) = w_k(y)` with `w_k(y) = sum_t n_k^t h_t(u_k y)`, a polynomial of degree `< B`. One inverse transform of size `B` of the values `(g_c(S_{k,i}))_i` returns the coefficients `w_k[j] = u_k^j sum_t n_k^t h_t[j]`. After multiplication by `u_k^{-j}`, for every `j < B` the numbers `W_k[j] = sum_t n_k^t h_t[j]` (`k < kappa`) are the values of the polynomial `h^(j)(X) = sum_t h_t[j] X^t` at the nodes `z^k`, and its coefficients `h_t[j] = g_c[j + tB]` are recovered from them by two correlations of length `kappa` (Lagrange interpolation at geometric nodes, the chirp-z form). Let `M(X) = prod_k (X - z^k) = sum_i mu_i X^i`; the q-binomial theorem gives `mu_{kappa-j} = (-1)^j z^{j(j-1)/2} [kappa choose j]_z`, and `M'(z^k) = z^{k(k-1)/2 + k(kappa-1-k)} prod_{j <= k} (z^j - 1) prod_{j <= kappa-1-k} (1 - z^j)`. With `a_k = W_k[j] / M'(z^k)` and `A(i) = sum_k a_k z^{ki}` (`i < kappa`) we have `h_t[j] = sum_{i > t} mu_i A(i - t - 1)`. Since `z^{ki} = z^{C(k+i,2) - C(k,2) - C(i,2)}` with `C(n,2) = n(n-1)/2`, `A(i) z^{C(i,2)}` is the correlation of the sequence `a_k z^{-C(k,2)}` with the chirp `z^{C(n,2)}` (first correlation), and `h_t[j]` is the correlation of `A` with `(mu_1, ..., mu_kappa)` (second correlation). Each correlation is one cyclic convolution of length `S = 1,610,612,736` (the smallest `2^a` or `3 * 2^a` that is at least `2 kappa - 1`), done with the transform of length `S` (forward, pointwise product, inverse); the transforms of the fixed sequences (the chirp and `mu`) and the constants `mu_i`, `1/M'(z^k)`, `z^{-C(k,2)}` are computed once per trial and shared by the `B` positions `j`. Appendix G runs this solve against the direct recovery at `kappa = 7`. The `2 kappa B = 7,450,580,601,318,408,192` evaluations of `F` are each charged as one target-compression unit (`C(21) = 657` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation. The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 s_{k,i})`, two multiplications for the recurrences of `s_{k,i}` and `1/s_{k,i}`, one store with its address operation, the loop control, the update of the row counter, and the executed shifts, masks, ors and loop control of the bit-reversed index, which are counted inside that function) and the solve (per `j`: two correlations, each two transforms of length `S` with `S/2 log2` butterflies at the charge of the model's own pass cost and `10 S` operations for the pointwise product and the scalings, and `14 kappa` operations for the chirp scalings, the division by `M'`, the loads and the stores) and its once-per-trial constants (`kappa` times two inversions, 40 operations per index, four transforms of length `S` and `10 S` operations) are charged on top.



## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (7,450,580,601,318,408,192 evaluations + 578241159 inverse NTTs of size 6,442,450,944 + the geometric solve of the 578241159 cosets (two correlations of length 1,610,612,736 per position) + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (in the value domain on 2K cosets of the subgroup of order 2^32, section 4.6: Barrett start at S^(2^59), 194 Montgomery squarings, 45 of them with the factor x on O2, exit and interpolation to coefficient form; ABORT if g vanishes on O1)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4; every division tests that its quotient has degree 1, and on any other quotient the trial ABORTs: it ends, next t)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (657 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 61 bits after the leading one are zero, so the algorithm starts from `S^v` with `v = 2^59` (a multiple of `2^32` below `m`; this absorbs 59 of the 253 squarings, 59 + 194 = 253), reached by one Barrett reduction of `X^v P1` (section 4.6), and the squaring loop of stage C has 194 steps, of which 45 also multiply by `S` (the factor `x` on `O2`, section 4.6).

Stopping rule over the `K` centres. The loop bound `K = 2` is a constant of the algorithm. A trial is run to its end, or to an ABORT in stage C (a zero of `g` on `O1`, 4.6) or in stage D, whatever its outcome; the claim charges every trial at its maximum (stage D for the normal remainder sequence, stages E to G at their worst case, section 6), so a trial that fails early or aborts is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B and C have lengths fixed by `m` and the exponent (sections 3, 4.6), the powering has a fixed number of steps, and on a normal remainder sequence the half-gcd has a fixed recursion: 56 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 1,862,645,149,230,957,031` and is halved, rounded up, until it is at most 96), and at most 56 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 3,725,290,298,461,914,062 to at most 192). A remainder sequence that is not normal is detected at its first quotient of degree other than 1, before any work that the normal sequence would not do, and the trial ends there (section 6.3). Hence the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

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
* block transform (section 4.5): the transform of `NB = 2 HB` points used by the block products at block length `HB = 2^b` is one row of the radix-2 passes above (passes of at most four layers), preceded by a copy of the block into the transform array (a load and a store per coefficient, each with its address operation) and a zero fill of the rest (a store per element), with the loop control of the eight-element rule; the inverse is the inverse passes; the factor `NB` is removed where the result is placed. The inner transform of 4.6 is the same row of passes on `2^32` points, in place on a coset, without copy or zero fill.
* index registers (as in the base entry's passes): the kernels keep their row addresses and loop counters in integer registers besides the 18 field registers of 256 bits (a kernel of radix 8 uses 8 row addresses and a counter); address formation is charged at every access and every address update as stated above.
* compaction and handles (this entry, section 7): an array is reached through its handle (the pointer in the stack frame of the procedure that owns it). When no free block fits a request of more than 196,608 bytes, the allocator moves every live block of more than 196,608 bytes down, in address order, rewrites the pointers of the moved arrays held in the stack frames (the handle table of Appendix G.7), and serves the request from the free space between the moved blocks and the lowest small block. Small blocks are placed at the highest free address that fits, so they sit above the large blocks; the guarantee that the freed space is one block needs this, and Appendix G.7 asserts it at each compaction of its replay. A compaction is charged 5 per moved element (a load and a store with their addresses, and the loop), 200 per moved block and 20,000 per compaction (the failed search, the walk over the blocks, at most 64 frames of at most 40 pointers rewritten at 6 operations each). Appendix G.7 counts the compactions of stages C and D (3 per trial, 29 blocks, `2.29 * 10^19` elements) and row D charges them (`compact_charge`, `1.15 * 10^20` operations).
* the scratch region of stage D (this entry, 4.4): one block allocated at the start of stage D; a call of `hgcd` with `k < 2^44` made from a call with `k >= 2^44`, and the iterations of the Euclid driver with `k < 2^44`, run inside it with the allocator of this section restricted to the region (the region is reset when such a call returns; its returned matrix is copied into the arena: 4 per element and 20, and four arena allocations charged as at 1,000 live blocks). Its size is the largest total of the blocks allocated by one such call or by the rest of the driver (`Tr.tot`, Appendix E): `1.14 * 10^18` bytes (0.0096 copies of `m`). The region never overflows: its free space is one block at the start of such a call and shrinks only by the requests served from its ends, whose total is at most the region's size.
* allocator statistics: the flat 64 of the allocator's statistics is charged on every allocation and on every free in Appendix E (rows C and D), and as an allowance of 64 for each of at most `10^10` allocator calls per trial in the rows A, B, E, F and G, which are taken from the base entry unexpanded (section 6).
* outer transforms (section 4.5, and the geometric phase of 4.6): a transform of `n = 2^a` or `3 * 2^a` points across the rows of an array, at each of `cnt` positions, is a twiddle-free radix-3 stage (kernel `ob3`, Good-Thomas) when `3 | n`, then in each of the (one or three) rows of `2^a` points radix-2 passes of at most three layers (kernels `ob2f`, `ob4f`, `ob8f`; inverse `ob8i`, `ob4i`, `ob2i`, then `ob3` with the conjugate constant). A pass of `k` layers keeps its `2^k` data words and `2^k - 1` twiddles in registers for the whole loop over the positions (`ob8f`: 8 + 7 + the butterfly temporary = 16 of the 18 words of the register file). The kernel text is printed in Appendix E and executed there under these rules: a load or a store is 2 (the access and its address operation), a field operation 1, a loop 3 per iteration and 2 on exit, a call 10; the driver charges 4 per block address and 3 per twiddle index, and the twiddle table of the transform is built at each call (`6 n + 2`). `check_outer` runs the kernels on arrays at 19 sizes, asserts that they compute the transform and its inverse, and asserts that the executed count equals the closed form `ontt` used by the ledger.
* row loops of 4.6: a row of `cnt` elements copied with a scale that advances along the positions is 16 operations per row (10 for the addresses, the factor and its step loaded, the factor stored back) and 6 per element (a load, the multiplication by the factor, the multiplication of the factor by its step, a store); with a constant per row, 12 per row and 5 per element; a zeroed row 10 per row and 2 per element; pointwise passes over a coset 14 per coset and the per-element count of their loads, multiplications, additions and store; every loop over the elements of a row or a coset is charged by the eight-element rule, every other loop by `3n + 2`. Appendix G.4 executes the loops of the geometric phases (the row copies, the zeroed rows, the pointwise products by the kernel, the resets of the running factors) with counted charges and asserts the closed forms; the per-element counts of the pointwise passes and of the batch inversion are itemized in 4.6.
* random words: the cost model's random-word primitive (an independent uniform 256-bit word) is one operation per word. The word of a draw is also loaded, stored into the cell `y` of the draw and addressed (one load, one store and three control operations), 6. A draw is that word (6), the reduction modulo `p` (three steps each of a comparison, a conditional branch and a field subtraction, 9, with the loop control of three iterations, 11), the conversion of the result to the internal representation (1), the entry (2) and the address of `y` (2): 31 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: 657 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation: every array is taken from one preallocated arena by a first-fit allocator with a 64-byte header per block (size, size of the previous block, in-use flag); a request of more than 196,608 bytes takes the first free block that fits, a smaller request the last free block that fits, a block is split when the remainder is at least 128 bytes, and a free merges with a free neighbour on either side. The allocator is charged per executed load, store, comparison, branch and address computation (550 per allocation and 105 per free at 16 live blocks), inside the stage rows, and a flat 64 per call for its statistics. The memory it uses is the arena of section 7.
* trial loop: the test of the trial counter, its increment and the bookkeeping of the trial, at most 12 operations per trial, are `TRIAL_EXTRA` = 12 in the ledger; the loop test and update of stage A are 5.
* the offline derivation of the constants is charged in section 6.2.



### 4.3 Stage C: the powering schedule (cyclic form, below the block length; block mode in 4.5)

At r = 21 stage C runs in the value domain (4.6) and the step below, the base entry's cyclic form for moduli below the block length, is not executed. What this entry uses from this section is the cyclic product itself (one transform of `3 * 2^a` points, rows processed one at a time) and the Newton iteration, for the reciprocal of 4.6 and for the products of the half-gcd that are computed by a single transform.

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
In this cyclic form the spectra of `MU` and of `g` are not stored (nor are they in block mode, section 4.5): for each multiplication the second operand is transformed one row of the Good-Thomas layout at a time into a buffer `tmp`, immediately multiplied into the corresponding row of `Y`, and discarded.
`MU` is computed once from `g` by Newton iteration with the same row-wise products. The leading exponent bits are absorbed by starting from the monomial `S^v` with `v < m`.
All charges of this stage depend only on `m` and the exponent, not on the coefficients.
### 4.4 Stage D: the half-gcd

Notation: a polynomial is stored as its coefficient array with the top coefficient nonzero (length = degree + 1). Euclid sequence of `(a, b)`, `deg a > deg b`: `r_0 = a`, `r_1 = b`, `r_{i-1} = q_i r_i + r_{i+1}`; `d_j = deg q_1 + ... + deg q_j`, so `deg r_j = deg a - d_j`;
`R_j = Q_1 ... Q_j` with `Q_i = [[q_i, 1], [1, 0]]` (entries of degree at most `d_j`; the first-row entries of degree exactly `d_j` for `r11`), and `(r_0, r_1)^T = R_j (r_j, r_{j+1})^T`.

`hgcd(a, b, k)` (`deg a = n`) returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` (when asked) and the pair `(r_h, r_{h+1})` (when asked). The procedure: if `b = 0` or `n - deg b > k` return the identity. If `k <= 96`, plain Euclid while the next quotient degree fits the remaining parameter, *in place* (this entry): the two remainders are two arrays, a division step whose quotient has two coefficients (the normal case) is one pass `r_k = a_k - q0 b_k - q1 b_(k-1)` written over the array of `a` (output index `k` reads index `k` of `a` and `k`, `k - 1` of `b`), with the charges of `poly_divrem_naive` (per element 2 loads, 2 multiplications, 2 subtractions, 1 store, each load and store with its address operation, the loop control of 3 and the test `if (k)` of 2 operations), and the roles of the two arrays swap (4 operations); the matrix entries are four arrays of `k + 2` elements allocated once, and `R := R Q` writes `r11 q + r12` over `r12` (index `j` reads `r11` at `j` and `j - 1` and `r12` at `j`) with the charges of `mul_add_q2`, and the column labels swap. No array is allocated or freed inside the loop (the base entry allocated the quotient and the remainder at every step).
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted, no pair wanted); if it returns `d_1 != k1` while its last remainder is nonzero, the trial ABORTs (the return test); (2) `(c, d) = R1^{-1} (a, b)` (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`; the high coefficients of `c` and `d` cancel, so the result modulo `X^N - 1` is exact for `N` at least the true length `la - h`; the product is computed by whichever of the single transform (cyclically on `3 * 2^j` points: the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each of the four matrix entries are transformed once and the two output rows are inverse transformed, `conv_bilin_otf`, the sign of each output absorbed in the scale factor `1/N`) and the block products of 4.5 (schemes (a) and (c), `need = la - h`) has the smaller charge (this entry). In a node that wants its matrix only, with `s3 > 0` below, a block product forms only the *top window* of `c` and `d`, the coefficients of degree at least `s3 - 1` (lemma 4.8; this entry); such a node tests that the coefficients of `c` and `d` at their normal leading degrees `la - h - 1` and `la - h - 2` are nonzero and ABORTs otherwise (2 tests, charged), so it never reports a zero or shorter remainder from a window; (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1` (`d_1 = deg R1`) return `R1` and `(c, d)`; (4) if `deg c - deg d != 1` the trial ABORTs (a comparison and a branch, charged at every division); otherwise divide `c = q d + e` (`q` of two coefficients: one pass, as in the base case; on the windows when they are used); (5) put `k3 = k - d_1 - 1` and `s3 = deg d - 2 k3`. If `s3 > 0`: `R2 = hgcd(d quo x^s3, e quo x^s3, k3)` (the top parts, matrix wanted, no pair wanted), with the return test, and only when the caller wants the reduced pair, `(c', d') = R2^{-1} (d, e)` by `apply_inv`; if `s3 <= 0`: `R2, (c', d') = hgcd(d, e, k3)`, with the return test. Return `R1 Q R2` (only if the matrix is wanted: `R1 Q` by two passes of `mul_add_q2`, then the product of the two 2 x 2 matrices by whichever of the single transform (each of the eight entries transformed once per row, with the right-factor entries of one column pair held and the left-factor entries streamed, the four outputs inverse transformed, `conv_bilin_otf`) and the block products of 4.5 is cheaper) and `(c', d')` when asked.
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: `(c, d) = hgcd(a, b, floor((n+1)/2))` (pair wanted, matrix not wanted), the return test, the ABORT test of the quotient degree and one division `c = q d + e` by a quotient of two coefficients, and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid with the same test; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). The only calls that want the reduced pair are those of `poly_gcd_own` and, recursively, the second calls with `s3 <= 0` inside them; every call inside a first call, and every truncated second call, wants the matrix only.
*The top node* (this entry). The first call of `poly_gcd_own` (`a = g`, `b = R - 1`, `k = (m + 1)/2` rounded down) is `hgcd` with these changes, which only change where arrays live and how its two pair-forming products are computed. Stage C leaves `g` and `R` as two pieces each, the coefficients `[0, cut)` and `[cut, l)` with `cut = Kc 2^32 = 2,793,967,726,031,273,984 >= lc = m + 1 - k1` (4.6, step 8). (i) Its first call frees the high pieces of `g` and of `R` right after its own `apply_inv`. (ii) The pair `(c, d)` is formed from the low pieces, `c` first (by the block products of 4.5, window `[0, lc)` of a product of true length `cut + len(r) - 1`), then `r22` and `r12` are freed, then `d`, then `r11`, `r21` and the low pieces are freed (`apply_inv_split`). (iii) `d` and the remainder `e` are written as two pieces at `cut2 = deg d + 1 - k3`; the second call frees their high pieces after its own `apply_inv`, and `(c', d') = R2^{-1} (d, e)` is formed from their low pieces in the same way. Every quotient and every length is that of `hgcd`.

**Lemma 4.8 (windows and pieces).** (a) In a node that wants its matrix only, with `s3 > 0`, the rest of the node reads `c` only at degrees at least `s3` and `d` only at degrees at least `s3 - 1`. (b) In the top node, after the first call's `apply_inv` no operation reads `a` or `b` at degrees at least `cut`, and `c`, `d` computed from `a mod X^cut`, `b mod X^cut` as the low `lc` and `lc - 1` coefficients are the `c`, `d` of step (2); the same holds for `(d, e)`, `cut2` and `(c', d')`. *Proof.* (a) The stopping test and the quotient test use `deg c` and `deg d`, the quotient `q = q1 x + q0` uses the top two coefficients of `c` and of `d`, and `e_i = c_i - q0 d_i - q1 d_(i-1)`; the second call reads only `d quo x^s3` and `e quo x^s3`, that is `d_i` and `e_i` for `i >= s3`, hence `c_i` for `i >= s3` and `d_i` for `i >= s3 - 1`; after it the node needs only `R1`, `q` and `R2` (`s3 - 1 <= deg d - 1`, so the top two coefficients are in the window). (b) The first call reads `a quo x^s` and `b quo x^s` and, after its `apply_inv`, only its own arrays; the top node then reads `a` and `b` only in step (2). For `i < lc <= cut`, the coefficient `i` of `r22 a` is `sum_j r22_j a_(i-j)` with `i - j < cut`, so it equals the coefficient `i` of `r22 (a mod X^cut)`; `c` has length `lc`, so it is the low `lc` coefficients of `r22 (a mod X^cut) - r12 (b mod X^cut)` (times `s`), and likewise `d`. For the second half, `cut2 = deg d + 1 - k3 >= lc' = deg d + 1 - h3` with `h3 = k3` on a normal sequence. ∎ Appendix G.5 runs the real half-gcd with the windows at every eligible node and the top node with its high pieces overwritten by garbage after they are freed, and compares the gcd with plain Euclid; a window one coefficient too large is detected.

**Lemma 4.4 (truncation).** Let `deg a = n > deg b`, let `a*`, `b*` agree with `a`, `b` on every coefficient of degree at least `t`, where `t <= n - 2k`, and let `q_1, q_2, ...` be the quotients and `d_j` their degree sums for `(a, b)`. Then every quotient `q_j` with `d_j <= k` is also the `j`-th quotient of `(a*, b*)`, and the stopping test of `hgcd(., ., k)` (the next quotient degree exceeds `k - d_h`, or the next remainder is zero) has the same outcome for both pairs. *Proof.* Induction on `j`. Let `q_1, ..., q_(j-1)` be common and `R = R_(j-1)`; the entries of `R^(-1)` (the adjugate of `R` up to sign) have degree at most `d_(j-1)`. So `r_(j-1) - r*_(j-1)` and `r_j - r*_j` are `R^(-1)` applied to `(a - a*, b - b*)`, of degree `< t + d_(j-1)`. Now `deg r_j = n - d_j` and the quotient of `r_(j-1)` by `r_j` depends only on their coefficients of degree at least `deg r_j - deg q_j = n - 2 d_j + d_(j-1)`. If `d_j <= k` this bound is at least `n - 2k + d_(j-1) >= t + d_(j-1)`, above the degree of the differences, so `deg r*_j = deg r_j` and `q*_j = q_j`. For the stopping test after `h` quotients: `d_(h+1) > k` holds iff `deg r_(h+1) < n - k` (or `r_(h+1) = 0`), and the coefficients of `r_(h+1)` and `r*_(h+1)` of degree at least `n - k >= t + d_h` agree, so the test has the same outcome. ∎ Applied with `a* = x^s (a quo x^s)` (`t = s = n - 2 k1`), the first call's quotients are those of `(a, b)`; dividing by `x^s` changes no quotient. Applied to the second call with `t = s3 = deg d - 2 k3`, likewise; the returned `R2` is the product of the quotient matrices of `(d, e)`, so `R2^{-1} (d, e)` is the reduced pair of `(d, e)` and `R1 Q R2 = R_h` for `(a, b)`. The base entry uses the lemma for the first call only. Appendix G.3 runs both forms (second call truncated, and not) on random pairs over the Pallas field against the plain Euclidean algorithm, and records that with the truncation every call has at most `2 k + 1` coefficients (without it, up to 20 times more at those sizes).

**Division and the two tests.** On the normal remainder sequence every division of stage D (in `hgcd`, in the base case and in `poly_gcd_own`) has a quotient of two coefficients and is the one-pass division above. Two tests, 2 operations each and charged wherever they execute, detect any other sequence: the *quotient test* at every division (a quotient used by the algorithm has degree 1), and the *return test* after every recursive call and every call of `poly_gcd_own` (the call returned exactly its parameter `k` as degree count, unless its last remainder is zero). On a normal sequence neither test fails: by lemma 4.4 every quotient a call uses is a quotient of the whole pair, hence of degree 1, and a call with parameter `k` stops exactly after `k` of them unless a remainder is zero (with `d_j = j` the stopping test fails first at `j = k + 1`). If either test fails the trial ABORTs, so the Newton division (`divrem_fast`) of the base entry is never run. A windowed node reads the top coefficients of `c` and `d` inside the window: if the coefficient at a normal leading degree is zero it ABORTs (the sequence is not normal there), and otherwise the degrees are the normal ones and the quotient test sees the same quotient as with whole outputs.

### 4.5 Products longer than `3 * 2^32` points (block mode)

The 2-adic part of `p - 1 = 2^32 * 3 * 463 * q'` is `2^32`, so the transforms of 4.2 (lengths `2^a` and `3 * 2^a`) exist only up to `3 * 2^32` points, and a product whose transform would be longer is computed by blocks. At this r that concerns the products of the half-gcd whose operands have several blocks and the products of the Newton reciprocal of 4.6; the squaring loop of stage C uses no product at all (4.6). This section replaces section 4.5 of the base entry; scheme (a) is the base entry's, scheme (c) and the choice of the block length are this entry's (scheme (c) was introduced by the entry e6dcb600 at the single block length `2^31`).

* Blocks. A block product at block length `HB = 2^b` cuts every operand into blocks of `HB` coefficients and multiplies blocks with the block transform of `NB = 2 HB = 2^(b+1)` points (one row of radix-2 passes, section 4.2): a product of two blocks has at most `2 HB - 1 < NB` coefficients, so it does not wrap. Scheme (a) is used at `HB = 2^31` only; scheme (c) at any `b` from 6 to 31.
* Scheme (a), slots (base entry). The slot `s` of a product `A C` is the sum of the block products `A_i C_j` with `i + j = s`; every block of every operand is transformed once, the slot is formed pointwise in the transform domain (`NB` multiplications per pair, additions or subtractions for the further pairs), inverse transformed once, and placed at offset `s HB` of the output (a load, the multiplication by `1/NB` and the sign, a store, and for the coefficients that overlap the previous slot a load of the output value and an addition, or a subtraction when the placement subtracts into an array). Only the slots that meet the wanted window are formed. Workspace: the block spectra of the operands and one accumulator of `NB` elements.
* Scheme (c), chunked outer product. Write `Y = X^HB` and `A = sum_i A_i Y^i` with blocks `A_i` of `HB` coefficients. Let `need` be the length modulo which the wanted coefficients are exact: for a window `[ws, ws + len)` of a product of true length `L`, `need = max(ws + len, L - ws)` (an index `i` of the window receives `i + N` only if `i + N < L` and `i - N` only if `i >= N`); for `apply_inv`, `L` is the true length of the outputs (their high coefficients cancel, 4.4), except in the top node of 4.4, whose operands are truncated and whose products are not cancelled. Let `n2` be the smallest `2^a` or `3 * 2^a` with `n2 HB >= need`; scheme (c) is admissible at `HB` only if `n2 <= 3 * 2^32` (`n2` then divides `3 * 2^32`). Let `w` be a primitive `n2`-th root of unity; the product is computed modulo `Y^n2 - 1 = X^(n2 HB) - 1`, which by the choice of `n2` gives the wanted coefficients exactly. Choose a power of two `nc` (the number of chunks) and put `n3 = n2 / nc`. Chunk `j < nc` handles the outer points `o = j + nc u`, `u < n3`. For each operand of more than one block it forms the chunk array of `n3` rows of `HB` elements, row `u' = sum over the blocks i = u' (mod n3) of w^(j i) A_i` (twist and fold), and transforms it with the outer transform of `n3` points (root `w^nc`) across the rows, at each of the `HB` positions. Row `u` then holds `A mod (X^HB - w^o)`. At each outer point the rows of the operands are transformed with the block transform (zero-padded to `NB` points), multiplied pointwise and summed over the products of the bilinear form (with their signs), inverse transformed, and folded modulo `X^HB - w^o` (lower half plus `w^o` times the upper half) into the row `u` of the output chunk array, which overwrites a row of an operand chunk array that is no longer needed. Each output chunk array is inverse transformed across the rows (root `w^-nc`) and untwisted into the output: block `s` of the result modulo `Y^n2 - 1` is `(1/(NB n2)) sum_j w^(-j s) z^(j)_(s mod n3)`, accumulated over the chunks in coefficient form, only for the wanted window (the first chunk stores, the others load, add and store; a subtraction into an array loads and subtracts). An operand of one block is transformed once and used at every outer point (its value at every `w^o` is the block itself). Appendix G.2 checks this scheme against schoolbook products reduced modulo `X^(n2 HB) - 1`, and Appendix G.6 executes it with counted charges against the ledger's closed form.
* Charges of scheme (c) (Appendix E, `scheme_c`): per product the roots and constants (`w`, `w^nc`, their inverses, `1/(NB n2)` and the radix-3 constants, 6 inversions or exponentiations at `330 + 2,310` each), the block transforms of the one-block operands, and per chunk: the twist and fold of each operand (per coefficient a load, a multiplication by the twist factor except in chunk 0, an addition for a row already started, a store; per piece 10 for the twist factor and the addresses, and the loops; a row with no block is zeroed), one outer transform of `n3` points at `HB` positions per operand of more than one block (`ontt`, 4.2), at each outer point one block transform per operand row, one pointwise pass per product (a write for the first, an addition or subtraction for the others), one inverse block transform per output and its fold (`8 HB` plus the loop), one inverse outer transform per output, and the untwist into the window (a load, the multiplication by the block factor, a store, and for chunks after the first or a subtraction a load and an addition or subtraction, per coefficient). The charges are integers; nothing is averaged.
* Workspace of scheme (c). The operands stay in coefficient form for the whole product (every chunk reads them) and the outputs are arrays in coefficient form; besides them the product holds, while a chunk is processed, `max(#operands of more than one block, #outputs)` chunk arrays of `n3 HB` elements, one working array of `NB` elements for each operand and each output, and the twiddle table of `n3` elements. Nothing is kept between products. The chunk count is the smallest power of two with `n3 HB <= cf`, where the chunk bound `cf` is `floor(f m)` with `f = 0.25` for the Newton products of 4.6 and `0.06` for stage D (`CF_FRAC` in Appendix E); these are parameters of the algorithm, chosen to balance time and memory.
* Choice. For each product the algorithm uses the cheapest of: the single transform of 4.3 and 4.4 (when the product fits `3 * 2^32` points), scheme (a) at `HB = 2^31`, and scheme (c) at the admissible block length `2^b` (`b = 6 .. 31`) of smallest charge; in the Newton phase of 4.6 scheme (a) is not used when its block spectra would exceed `0.9 m` elements. The choice is a function of the lengths, the window and the chunk bound only, and Appendix E evaluates every candidate. The gain of the variable block length comes from the 2-adic bound: at `HB = 2^31` the inner transforms, which carry the factor 2 of the zero padding, are 32 layers deep, while the outer transforms (no padding) are short; a smaller `HB` with up to `3 * 2^32` outer points moves layers from the padded inner transforms to the unpadded outer ones (for example an `apply_inv` with `k = 2^46` costs 0.78 of its charge at `HB = 2^31`).
* Stage D, products above one transform. `apply_inv` forms `c = r22 a - r12 b` and `d = r11 b - r21 a`, a bilinear form with two outputs of true lengths `la - h` and `la - h - 1` (or their top windows, 4.4); `a` and `b` stay live for the whole product and `c`, `d` are written into arrays of their own lengths. In the top node of 4.4 the two outputs are formed one after the other from the low pieces of the operands (`apply_inv_split`), and the two entries that a finished output no longer needs are freed before the second output is formed. The matrix product of the half-gcd (`mat_mul`) is the same bilinear form with four outputs, each the sum of two products; the four outputs are allocated first, the arrays of both factors stay live for the product and are freed after it.
* Memory. The arena of section 7 is the maximum over the stages of the bytes in use, computed by the walk of Appendix E, which allocates and frees every array named in this section and in 4.6 (a block is `64 + 32 * slots` bytes rounded up to a multiple of 64). The twiddle table is the one of the transform of `3 * 2^32` points (`2^31` elements, `ntt_init(32)`); every block transform and the inner transforms of 4.6 use the same table.
* Cost. The charges are those of 4.2 applied to these operations; Appendix E (`stage_cd.py`) expands stages C and D with these rules and asserts the totals.

### 4.6 Stage C in the value domain (this entry)

This section replaces the squaring step of the base entry (4.3, 4.5 there) and of e6dcb600. The residue is not held in coefficient form: it is held by its values on two sets of `n1` points, and one modular squaring is a Montgomery reduction whose only non-pointwise operations are two changes of point set (extensions), each a transform per coset and one convolution with a fixed kernel per inner position. No product of polynomials, no `MU` and no quotient is formed in the loop.

**Points.** In this section `K` is the number of cosets of each point set (not the number of centres of 4.1) and `h = 2^32`. `H` is the subgroup of order `h` of `F_p^*` (generator `omega = 5^((p-1)/h)`, of order `h` because `5^((p-1)/2) != 1`), `u_k = 5^k`, the coset `C_k = u_k H`, and `n_k = u_k^h = z^k` with `z = 5^h`. Write `p - 1 = 2^32 * 1389 * q1 * q2` with `q1 = 539,204,044,132,271,846,773` prime; the order of `z` divides `1389 q1 q2`, and `z^(1389 q2) != 1`, so `q1` divides it and it is at least `q1 > 2K` (Appendix G.4 checks the primality of `q1` and the power). So the nodes `z^k` (`0 <= k < 2K`) are distinct, the cosets `C_k` are pairwise disjoint, and `z^e != 1` for `1 <= e < 2K`. `K = ceil((m + 1)/h) = 867,361,738`, `n1 = K h = 3,725,290,298,511,720,448 = m + 49,806,386`; `O1 = C_0 u ... u C_(K-1)`, `O2 = C_K u ... u C_(2K-1)`. `M(Y) = prod_{k<K} (Y - z^k)` and `P1(X) = M(X^h) = prod_{k<K} (X^h - n_k)`, of degree `n1`: it is squarefree with root set exactly `O1` (`X^h - n_k` has the `h` distinct roots `C_k`), and on a coset `C_k` with `k >= K` it is the nonzero constant `M(n_k)`.

**Representation.** A polynomial `f` of degree `< n1` is determined by its values on `O1`, and by its values on `O2`. Write `f = sum_{j<h} X^j F_j(X^h)` with `deg F_j < K`. Then `f mod (X^h - n_k) = sum_j F_j(n_k) X^j`, and the values of `f` on `C_k` are the transform of size `h` of `(u_k^j F_j(n_k))_j`: `f(u_k omega^i) = sum_j u_k^j F_j(n_k) omega^(i j)`. The arrays of this section hold, coset after coset, the values in the output order of the inner transform (the transform of `h = 2^32` points of 4.2, one row of radix-2 passes, in place on the coset; its first pass may read another array, at the same charge).

**Lemma 4.7 (extension).** Let `f` have degree `< n1` and let its values on `O1` be given. The inverse inner transform of each coset of `O1` gives `h u_k^j F_j(n_k)`. For each position `j`, with `F = F_j`, `s_i = F(z^i) z^(-i) / M'(z^i)` (`i < K`) and `kappa(e) = 1/(z^e - 1)` (`1 <= e <= 2K - 1`): `F(z^(K+t)) = M(z^(K+t)) sum_{i<K} s_i kappa(K + t - i)` for `t < K`. With `M2(Y) = prod_{i<K} (Y - z^(K+i))` and the values on `O2` given, `F(z^t) = -M2(z^t) z^(-t) sum_{i<K} [F(z^(K+i)) / M2'(z^(K+i))] kappa(K + i - t)`. *Proof.* `deg F < K`, so `F` is the Lagrange interpolant of its values at the `K` distinct nodes: `F(y) = M(y) sum_i F(z^i) / (M'(z^i) (y - z^i))` for every `y` outside the nodes, and `z^(K+t) - z^i = z^i (z^(K+t-i) - 1)` with `1 <= K + t - i <= 2K - 1`. The second formula is the same with the nodes `z^(K+i)` and `z^t - z^(K+i) = -z^t (z^(K+i-t) - 1)`. ∎ The sum is a convolution: the outputs are the entries `K .. 2K - 1` of the cyclic convolution of length `Lx = 2^31 >= 2K - 1` of `(s_0, ..., s_(K-1), 0, ...)` with `(0, kappa(1), ..., kappa(2K - 1), 0, ...)`; no index wraps (`1 <= K + t - i <= 2K - 1 < Lx`). The direction `O2 -> O1` is the same convolution with the same kernel, the inputs in reversed order (row `r` holds `i = K - 1 - r`) and the output `t` in row `2K - 1 - t`. Then the forward inner transform of each coset of the target set takes `u_k^j F_j(n_k)` to the values. The factors `u_k^(-j)`, `1/h`, `z^(-i)/M'(z^i)` (or `1/M2'`) on the input side and `1/Lx`, `M(z^(K+t))` (or `-M2(z^t) z^(-t)`), `u_k^j` on the output side are applied as one multiplication per element, with the factor of a coset advanced along the positions by one multiplication per element (`rows_rec`).

**The geometric phase.** The `h` positions are processed in groups of `VCNT = 2^10` positions. A group copies the `K` input rows (one row of `VCNT` elements per coset, with the scaling above) into a buffer of `Lx` rows, zeroes the other rows, runs the outer transform of `Lx` points at the `VCNT` positions (`ontt`, the kernels of 4.2), multiplies each row by the stored transform of the kernel (one constant per row), runs the inverse outer transform and copies the `K` output rows back (with their scaling) into the coset array, in place. The kernel's transform (one forward outer transform of `Lx` points) and the constants of the factors are computed once per trial.

**Lemma 4.6 (the step).** Let `g` be monic of degree `m` with `g(x) != 0` for every `x` in `O1`, let `R~` have degree at most `m`, and let `u0` be the polynomial of degree `< n1` with `u0(x) = -R~(x)^2 / g(x)` on `O1`. Then `W = (R~^2 + u0 g) / P1` is a polynomial of degree at most `m - 1`, `W = R~^2 P1^(-1) mod g`, and on `C_k`, `k >= K`, its values are `(R~(x)^2 + u0(x) g(x)) / M(n_k)`. For `b` in `{0, 1}`, `R~' = X^b W` has degree at most `m` and `R~' = X^b R~^2 P1^(-1) (mod g)` (a congruence: for `b = 1`, `R~'` may have degree `m` and is then not the reduced residue). *Proof.* `R~^2 + u0 g` vanishes on `O1`, the `n1` distinct roots of the squarefree `P1`, so `P1` divides it. Its degree is at most `max(2m, n1 - 1 + m) = n1 + m - 1` (`n1 >= m + 1`), so `deg W <= m - 1`. Modulo `g`, `W P1 = R~^2`, and `P1` is invertible modulo `g` because `g` has no root in `O1`. The values follow from `P1(x) = M(n_k)` on `C_k`. ∎ Hence if `R~ = R P1 mod g` then `R~' = X^b R^2 P1 mod g`: the invariant "`R~_i = R_i P1 (mod g)`, `deg R~_i <= m`, with `R_i = S^(e_i) mod g`" passes from step to step (`e_(i+1) = 2 e_i + b`). And for `R~` of degree at most `m`, the polynomial `(R~ + u0 g)/P1` with `u0 = -R~/g` on `O1` has degree at most `m - 1` and equals `R~ P1^(-1) mod g` (the same proof): this leaves the Montgomery form.

**The stage.** Every array below has `n1` elements unless stated. The exponent `E = (p-1)/2` has its leading bit at position 253 and zeros at 252 .. 192; the stage starts from `S^v` with `v = 2^59` (a multiple of `h`, below `m`) and runs `194` steps, the bits 193 .. 0 of `E`, of which 45 have `b = 1`.

1. *Barrett start.* `T = X^v P1` (`deg T = v + n1`; its coefficients are the `mu_i` of `M`, `M(Y) = sum mu_i Y^i`, at the degrees `v + i h`), `delta = v + n1 - m` and `ell = delta + 1 = 576,460,752,353,229,875`. The reciprocal of the reversed `g` modulo `X^ell` is computed by the Newton iteration of 4.3 (two products per doubling; the products by 4.5 with chunk bound `0.25 m`), in an array of `ell` elements, from a copy of the reversed top `ell` coefficients of `g`; `q = floor(T / g)` is the reversal of the low `ell` coefficients of `rev(T) mod X^ell` times the reciprocal (one product, window `[0, ell)`, written into the first `ell` elements of the array `R1`, which is allocated before the Newton phase so that no hole is left when `q` dies; `rev(T) mod X^ell` is written into an array of `ell` elements: a zero fill and the `mu_i` of the degrees at least `m`, each `mu_i` charged as one inversion and 30 operations). This is the standard identity `floor(A / g) = rev(rev(A) rev(g)^(-1) mod X^(deg A - m + 1))` for `deg A >= m`. The reversed `g` is freed after the Newton phase, the reciprocal and `rev(T)` after the product.
2. *`g` on `O1` and `O2`.* From the coefficients of `g` (the array of stage B): for each position `j`, the polynomial `G_j(Y) = sum_t g[j + t h] Y^t` (`K` coefficients) is evaluated at the `2K` nodes `z^k` by the chirp transform of section 3 (`z^(t k) = z^(C(t+k,2) - C(t,2) - C(k,2))`: one convolution of length `Le = 3 * 2^30 >= 3K - 1` with the chirp `z^(C(n,2))`), the outputs scaled by `z^(-C(k,2)) u_k^j`, and the `2K` forward inner transforms give `g` on `O1` (array `G1`) and on `O2` (array `G2`, two pieces, see 8). The array of the coefficients of `g` is freed.
3. *`R~_0` on `O2`.* `q` (`Kq = ceil(ell / h) = 134,217,729` rows) is evaluated in the same way at the `K` nodes `z^(K+k)` (convolution of length `Lq = 2^30 >= Kq + K - 1`, the inputs scaled by `z^(K t)`) into the array `R2` (two pieces, allocated where the array of `g` was: that array has `n1 + 2` elements, so the two pieces fit its place exactly), then `R2 := u_k^v M(n_k) - R2 * G2` pointwise (`x^v = u_k^v` on `C_k` because `h | v`). Now `R2` holds the values of `X^v P1 - q g = X^v P1 mod g` (degree `< m`), that is `R~_0` with `R_0 = S^v`.
4. *`R~_0` on `O1`.* The inverse inner transforms of the cosets of `O2` read `R2` and write the array `R1` (`q` is no longer needed); the geometric phase `O2 -> O1` and the forward inner transforms run in place on `R1` (lemma 4.7).
5. *`-1/g` on `O1`*, in place in `G1`: per coset the prefix products into an auxiliary array of `h` elements, one inversion with a zero test, and the backward pass (Montgomery's batch inversion). If a prefix product is zero, `g` vanishes at a point of `O1` and the trial ABORTs (probability below `2^-129`, 9.2(f)).
6. *The loop*, for each bit `b` of `E` from position 193 down to 0: (i) `R1 := R1^2 * G1` pointwise (`u0` on `O1`); (ii) the extension `O1 -> O2` in place on `R1`; (iii) `R2 := x^b (R2^2 + R1 * G2) / M(n_k)` pointwise (`1/M(n_k)` and `u_k` per coset from the tables, `x = u_k omega^i` from a table of the `omega^i` in transform order when `b = 1`); (iv) the extension `O2 -> O1` from `R2` into `R1` (the inverse inner transforms read `R2` and write `R1`). By lemma 4.6 the invariant holds after every step, and after the last step `R~` represents `S^E P1 mod g`, of degree at most `m`.
7. *Leaving the Montgomery form.* `R1 := R1 * G1` (that is `-R~/g`), the extension `O1 -> O2`, `R2 := (R2 + R1 * G2) / M(n_k)`: `R2` holds the values of `R = S^E mod g` (degree `< m`, lemma 4.6). `R1` and `G1` are freed.
8. *Coefficient form for stage D.* `R2` and `G2` are interpolated in place: the inverse inner transforms, then per position the interpolation at the `K` nodes `z^(K+k)` by the two correlations of section 3 (`a_k = W_k / M'(z^k)`, the chirp correlation `A(i) z^(C(i,2)) = sum_k a_k z^(-C(k,2)) z^(C(k+i,2))`, then `h_t = sum_{i>t} mu_i A(i - t - 1)`, both of length `Lx`, applied to `G(Y) = F(z^K Y)` and unscaled by `z^(-K t)`). Row `t` of the coset array becomes the coefficients `[t h, (t + 1) h)`. Each of the two arrays is two pieces, the cosets `[0, Kc)` and `[Kc, K)` with `Kc = ceil((m + 1 - k1) / h) = 650,521,304` and `k1 = 931,322,574,615,478,516` the parameter of the first call of the top node of stage D, so that stage D can free the high pieces early (4.4).

**Charges** (Appendix E, `powx_vd`). Inner transforms: `449,396,745,180` operations for a forward and `465,144,958,607` for an inverse transform of a coset (the passes of 4.2), plus 10 for the call and the coset address. The geometric phase of one extension: `1,879,077,809,384,025,781,522` (`504.4` per element of `n1`: the running factors set from their base tables (7 per row), per group 20 operations, the copies with scaling (16 per row and 6 per element: a load, two multiplications, a store), the zeroed rows (a store per element), two outer transforms of `Lx` points at `VCNT` positions (`95.87` per element of the buffer of `Lx` rows each, from `ontt`, that is `237.4` per element of `n1`), the pointwise product by the kernel (a load, a multiplication and a store per element), with the loops by the eight-element rule). One extension with its `2K` inner transforms: `2,672,316,291,076,750,688,520`. Pointwise passes per element (each load and store with its address operation): 8 for (i) (2 loads, 2 multiplications, a store) and for the start of 3, 12 for (iii) (3 loads, the square, the product `u0 g`, the addition, the multiplication by `1/M(n_k)`, a store; 16 when `b = 1`: the load of `omega^i` and two multiplications), 7 and 11 for step 7; per coset 14 operations for its constants and addresses. One step: `5,421,932,355,885,783,492,832` operations (`b = 0`; `1455.4` per element of `n1`) or `5,436,833,517,079,830,374,624` (`b = 1`). Set-up: the Newton reciprocal `4,268,812,284,126,511,564,533`, the product for `q` `1,580,309,527,890,998,379,685`, the evaluation of `g` `2,837,681,060,777,466,295,568` plus `2K` forward inner transforms, the evaluation of `q`, the extension of 4, the batch inversion `54,948,034,223,240,525,760`, the tables (`30 K` constants at two inversions and 60 operations each, the five kernel spectra); the exit and two interpolations (`3,726,839,897,177,867,958,922` each for the geometric part). Every allocation and free is charged (4.2). Row C: `1,077,028,960,067,639,720,672,037` operations.

**Memory.** The loop holds the twiddle table, `R1`, `R2`, `G1`, `G2` (four arrays of `n1` elements), the tables (`30 K` constants including the table of `omega^i`, the five kernel spectra and the twiddle table of the outer transforms: about `3.3 * 10^10` elements) and two group buffers of `Le * VCNT` elements: 4.0000 copies of `m` elements; the peak of the stage is at step 5, which holds also the auxiliary array of `h` elements. The set-up stays below it (the Newton phase holds `g`, `R1`, the tables, three arrays of `ell` elements and the workspace of one product; step 2 holds `g`, `R1`, `G1` and `G2`). The order of the allocations leaves no hole that a later array cannot fill: the tables, the buffers and `R1` are allocated first, after `g`; `G1` and `G2` follow the space of the Newton phase; `R2` takes the place of `g`. Appendix E walks these allocations and Appendix G.7 places them at their addresses in the arena (no compaction is needed in stage C).

**Evidence.** Appendix G.4 (`vd_check.py`) first checks the order of `z` at r = 21 (the primality of `q1` by a deterministic Miller-Rabin test, `z^(1389 q2) != 1`, and `5^((p-1)/2) != 1`), then runs this stage with real arithmetic over the Pallas field at `h = 4, 8, 16` (`K = 5 .. 7`): the chirp evaluation of `g`, the Barrett start, both extensions, the loop over the exponent bits with `x^b` on `O2`, the exit and the interpolations, and compares `R` with `S^E mod g` and the interpolated `g` with `g`; after every step it interpolates `R~` and checks `deg R~ <= m` and `R~ = S^e P1 (mod g)`. It also executes the geometric phases of an extension (both directions), of the evaluation and of the interpolation with counted charges (the rules of 4.2, the outer kernels of Appendix E) and asserts that the counts equal the closed forms `geo_ext`, `geo_eval` and `geo_interp` of the ledger.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: operation count, every trial at its maximum (primitive operations; `C(21) = 657`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, and the trial loop; `T_off` = the offline bound of section 6.2. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 2`, and `time_log2 = ceil_5(log2(N_max / 657))`.

Every stage is charged by the rules of section 4.2 where it executes. Section 6.1 reproduces the base entry's comparison of the same counting with the instrumented totals of its executed entries at r = 3, 4, 5. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(32-1)` elements (`ntt_init(32)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 17,179,887,292 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,196 |
| B (per trial) | `578241159` cosets of `6,442,450,944` points, each point with two evaluations of `F` (at `c + s` and `c - s`) at `C(21) = 657` operations each, the loop work around them, `578241159` inverse transforms of size `6,442,450,944`, the geometric solve of the cosets (two correlations of length `1,610,612,736` per position), the normalisation | 14,724,903,587,095,649,952,616 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain (section 4.6): Barrett start (Newton reciprocal modulo `X^ell`, one product), `g` and `q` evaluated on the cosets, `194` steps (two pointwise passes and two extensions each), exit and two interpolations; expanded in Appendix E | 1,077,028,960,067,639,720,672,037 |
| D (per trial) | half-gcd of `(g, R - 1)` (section 4.4) on the normal remainder sequence, with the test of every quotient degree (section 6.3), the scratch region and the three compactions of the arena (4.2, Appendix G.7); expanded in Appendix E | 1,062,106,645,154,198,605,714,641 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16` (below) | 166,079,773 |
| F (per trial) | square root, back-map (below) | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 657 + 32` | 14,172 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| allocator statistics, rows A, B, E, F, G (per trial) | the flat 64 of the allocator's statistics (4.2) for at most `10^10` allocator calls in the rows that Appendix E does not expand (rows C and D charge it on every allocation and free) | 640,000,000,000 |
| plan_invN misses | one per distinct plan size (31 sizes) | 95,759 |
| plan_invN misses, second allowance | the plans of the revised products differ from the base entry's; a second allowance of the row above (62 sizes in all) | 95,759 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 2 * T_trial + T_off` | **4,307,721,017,619,165,469,436,718** |

The rows C and D are not asserted by hand: Appendix E (`stage_cd.py`) expands them from the cosets, the transforms and the geometric phases of 4.6, the block products of 4.5 at their chosen block lengths, the Newton levels and the half-gcd levels, with the kernel charges of section 4.2, and prints and asserts the two values 1,077,028,960,067,639,720,672,037 and 1,062,106,645,154,198,605,714,641 (one squaring step is 5,421,932,355,885,783,492,832 operations, 5,436,833,517,079,830,374,624 when `b = 1`: two extensions of 2,672,316,291,076,750,688,520 and the two pointwise passes; the 194 steps are 1.0525e24 of row C, the set-up, exit and interpolations 2.45e22; row D includes the compactions, 114,621,143,184,985,894,255). The other rows are the base entry's.

`N_max = 4,307,721,017,619,165,469,436,718` operations `= 6,556,652,994,854,133,134,606.9` units, `log2(N_max / 657) = 72.4734495361`, rounded up at five decimals to 72.47345 (the value printed by the script of 6.1 and asserted in Appendix E) and claimed as `time_log2 = 72.475` (rounded up at three decimals: a margin of `4.6 * 10^21` operations, 0.00155 bits, for any charge this count may have missed).

Stage B charges each of the `7,450,580,601,318,408,192` evaluations of `F` as one reduced permutation, `C(21) = 216 + 21 * 21 = 657` operations, although a line evaluation is a strict subset of the work of a reference permutation; the loop work around the evaluations is charged on top (section 3).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the isolation loop until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 31, the zero test of the shift (5, and at most 2 for the replacement of a zero draw by 1) and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because the memory-access charge adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `2,640` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = 2,594,979`, of which `pow_half` is 2,471,032, the Taylor shift 11,700 and the two gcds 54,395 each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + 64 * R(16) + 114 = 166,079,773`.

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`.

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.1 Ledger recomputation and validation

The sum of section 6 is recomputed by the following script (standard library only).

```python
from math import log2, ceil
K, C = 2, 657
fixed = [17179887292, 4910, 95759, 95759, 5644, 3384436]   # init, setup, plan_invN misses (two allowances), stage H, stage I
trial = [1196, 14724903587095649952616, 1077028960067639720672037, 1062106645154198605714641, 166079773, 47012, 14172, 12, 640000000000]   # stages A, B, C, D, E (cap), F, G, main, allocator statistics
offline = 1000000
N = sum(fixed) + K * sum(trial) + offline
print('N =', format(N, ','))
print('units =', round(N / C, 1))
print('time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))
```

The base entry compares its counting with the instrumented totals of its executed entries (algorithmic totals; the executed runs at r = 3, 4, 5 had fixed centres and a different stage A, and their thread charges are excluded): the count is above the measured total in every row, and its heap peak equals the measured heap peak at r = 3 and r = 5 and is 64 bytes below it at r = 4. Those runs used the base entry's programs, not the stages C and D of this entry; the table is reproduced as the base entry's validation of the charging rules of 4.2. The charges of this entry's new loops are checked by execution at small sizes instead: the outer kernels (`check_outer`, Appendix E), scheme (c) (Appendix G.6), the geometric phases of 4.6 (Appendix G.4) and the shapes of the half-gcd (Appendix G.5) and the placement of every array in the arena (Appendix G.7).

| run | counted total | measured total | counted - measured | slack (bits) | counted heap peak | measured heap peak |
|---|---:|---:|---:|---:|---:|---:|
| r = 3, earlier program (fixed centre) | 410,937,818,567 | 409,369,056,359 | 1,568,762,208 | 0.00552 | 244,745,792 | 244,745,792 |
| r = 4, earlier program (fixed centre) | 3,993,660,556,174 | 3,977,289,295,772 | 16,371,260,402 | 0.00593 | 1,072,730,560 | 1,072,730,624 |
| r = 5, earlier program (fixed centre) | 9,217,469,769,975 | 9,171,678,989,504 | 45,790,780,471 | 0.00718 | 4,759,669,952 | 4,759,669,952 |

### 6.2 Offline derivation of the literals (preprocessing)

The algorithm uses constants that are derived from the organizer's constants and from `p` offline: the 192 round constants and 9 MDS entries in Montgomery form, `R^2 mod p`, `R mod p`, `2^65` and `5^q` in Montgomery form, the exponents `q`, `(q+1)/2`, `(p-1)/2`, `p - 2` and the integer `e = (4(p-1)+1)/5`. There is no search and no choice: each literal is the value of one closed formula in the organizer's constants. The Montgomery form of a constant `x` is `x * 2^256 mod p`, one modular multiplication plus parsing 64 hexadecimal digits; `5^q` is a square-and-multiply of 221 squarings and at most 221 multiplications; the exponents are shifts and subtractions of `p`. Each literal costs at most 4,000 word operations, there are at most 250 literals: 1,000,000 operations in all. This bound is inside `N_max` and is the declared `preprocessing_log2 = 20` (`2^20 = 1,048,576 >= 1,000,000`). The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

### 6.3 Stage D: the normal remainder sequence, and the abort

The row D is the charge of the half-gcd of section 4.4 on a normal remainder sequence: every quotient of the Euclidean sequence of `(g, R - 1)` has degree 1, from `deg g = m` down to the gcd. (a) *Lengths.* On such a sequence `d_j = j`, every call `hgcd(a, b, k)` of the recursion has the parameter fixed by the recursion (`k1 = ceil(k/2)`, `k3 = k - k1 - 1`), its first call has `2 k1 + 1` coefficients and its second call at most `2 k3 + 1` (lemma 4.4), the reduced pairs have the lengths `deg a - h` and `deg a - h - 1`, the windows of lemma 4.8 and the pieces of the top node are functions of these lengths, and every matrix of a call with parameter `k` has entries of at most `k + 1` coefficients. Every length of the program is therefore a function of `m` alone, and Appendix E evaluates the charge on these shapes exactly (`gcd_cost(m, 0)`, with the gcd of degree 0); Appendix G.5 compares these shapes, call by call, with the real algorithm. (b) *A gcd of positive degree.* When the gcd has degree `d >= 1` the normal sequence ends at a zero remainder after `m - d` divisions. The program then executes a prefix of the calls of the degree-0 case, with the same lengths at every executed call (a call whose second operand is zero, or whose remaining parameter is exhausted, returns at its first test), so its charge is at most row D. (c) *The tests and the abort.* The quotient test and the return test of 4.4 (2 operations each, charged wherever they execute in Appendix E) are passed by every normal sequence. Consider any other sequence and the first point, in execution order, at which a call whose degree count `h` is still below its parameter `k` finds that the next quotient of its own pair has degree other than 1 (a call with `h = k` stops whatever its next quotient is, as on a normal sequence). If that quotient fits the remaining parameter, the call uses it and the quotient test fails at that division. If it does not fit, the call stops early: the base case breaks out of its loop, a node returns at step (3) after its first call and `apply_inv`, which were executed with normal shapes because every quotient before this point had degree 1; the call returns a degree count below its parameter with a nonzero remainder, and the return test of its caller fails before the caller does anything with the result. A windowed node ABORTs when a coefficient of `c` or `d` at its normal leading degree is zero, and otherwise reads the same top coefficients as with whole outputs (lemma 4.8), so it sees the same quotient. In both cases the trial ends having executed only operations that the normal sequence also executes, with the same lengths (lemma 4.4: until that point the truncated calls see the quotients of the whole pair). Hence row D bounds stage D for every input, and the abort affects only the success probability, through the premise `H-NORMAL` (9.2(f), 9.5). The ABORT of stage C (a zero of `g` on `O1`, found by the zero test of the batch inversion, 4.6 step 5) also comes after a prefix of the charged work; its probability is bounded in 9.2(f) without a premise.

## 7. Memory

Three terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 399,216 bytes of code, 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages): 5,250,444 bytes (the base entry's figure; the kernels of the outer transforms, of the one-row block transform and of the loops of 4.6 add a few kilobytes of code, covered by the rounding margin stated at the end of this section).

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The declared cost model counts memory as the peak of the bytes in use, and the arena is that peak, with no reserve factor; `python3 stage_cd.py` of Appendix E walks every allocation and free of stages A to D with the sizes of 4.5 and 4.6 and prints the peak of each stage, the arena and the memory figure below. The peaks per stage (in units of `32 m` bytes, one copy of a polynomial of `m` coefficients): A 119,209,289,621,094,531,264 (1.0000); B 238,418,579,242,189,062,400 (2.0000); C 476,837,370,801,235,048,512 (4.0000); D 455,265,475,194,479,467,904 (3.8190, the scratch region included); stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The base entry's walk of stage B holds the twiddle table, `g` and the coset array; the buffers of the coset solve (the transforms of the chirp and of `mu`, the correlation buffer and three arrays of `kappa` constants, about `2.1 * 10^11` bytes, with their transform scratch) are not in it, and are far below the stage C peak. The arena is `476,837,370,801,235,048,512` bytes, the peak of stage C, reached at its step 5 (4.6): the twiddle table, the four value arrays `R1`, `R2`, `G1`, `G2` of `n1` elements, the tables and kernel spectra (about `3.3 * 10^10` elements), the two group buffers (`Le * 2^10` elements each) and the auxiliary array of the batch inversion. Stage D stays below it: its peak is in the top node's first call (lemma 4.8: the high pieces of `g` and `R` are already freed). The peak of the live set is not by itself an arena size for an allocator that can leave holes; Appendix G.7 places every array of stages C and D at its address in an arena of exactly this size, with the allocator of 4.2: stage C leaves no hole (its order of allocation, 4.6), and in stage D first fit alone fails (holes between the matrix entries of the half-gcd; about 4.25 copies would be needed), so the allocator compacts the arena when a request finds no hole (4.2): 3 compactions per trial, charged in row D. With compaction every request is served, because the peak of the live set, which includes the request, never exceeds the arena (with the small blocks above the large ones, asserted by the replay). The arrays inside the scratch region are not placed one by one: the region is one block of the arena, sized by the total of the blocks of its largest call (4.2). The largest single transform has `3 * 2^32` points; products that would need a longer transform are computed by blocks (section 4.5). Nothing is held in transform form between products.

(c) A stack bound of 65,536 bytes.

Total: (a) + (b) + (c) = `476,837,370,801,240,364,492` bytes `= 2^68.69206`, claimed as `memory_log2_bytes = 68.693` (rounded up at three decimals; the rounding leaves a margin of `3.1 * 10^17` bytes, which covers the code of the added kernels many times over). The memory penalty is `max(0, 68.693 - 20) = 48.693`. The offline derivation of section 6.2 is a closed formula per constant; its memory is bounded by 1,024 bytes, inside the figure above. The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init", and the tables of 4.6 are built in every trial and charged in row C.

## 8. What is provided

* The algebraic derivation (sections 2-3), the algorithm and its charges (4, 6, 7), the truncation lemma 4.4, the extension lemma 4.7, the step lemma 4.6 and the window lemma 4.8 with proofs, the premises `H-GEOM-w1` and `H-NORMAL` with the reduction to explicit constants (section 9), the isolation lemma with proof (9.4), and the evidence, labelled as evidence (section 10).
* The claim is the operation count of the algorithm (every trial at its maximum), `memory_log2_bytes` its footprint, and a success probability that follows from `H-GEOM-w1` and `H-NORMAL`. The cost claim is in the model of section 4.2.
* The ledger of stages C and D (Appendix E), five small-size checks over the Pallas field (G.2 the chunked products of scheme (c); G.3 the truncated half-gcd; G.4 stage C in the value domain, results and counted charges; G.5 the shapes, windows and pieces of the half-gcd against the ledger; G.6 scheme (c) executed with counted charges against the ledger), and G.7, the placement of every array of stages C and D in the arena at r = 21 with the allocator of 4.2 and its compactions; standard library only. No certificates (the certificate manifest is empty); the experiments are those of 10.2 (the base entry's programs, unchanged).

## 9. Success probability and the premises `H-GEOM-w1` and `H-NORMAL`

### 9.1 The premise

Notation. `p` is the Pallas prime, `D = 5^27`, and `F` is the fixed polynomial of section 2.3 at r = 21 (degree `D`, leading coefficient `f_D(0) != 0`). Put
`G(c, t) = (F(c + t) - F(c - t)) / (2 t)` in `F_p[c, t]`, a polynomial of total degree `D - 1` (section 3: `G(c, t) = g_c(t^2)`). For `c` in `F_p` let `k(c)` be the number of nonzero squares `S = t^2` with `G(c, t) = 0`; this is `deg G_c` of section 3. Let `O` be the set of triples `(c, s_1, s_2)` with `G(c, s_1) = G(c, s_2) = 0`, `s_1^2 != s_2^2` and `s_1 s_2 != 0`; `N_off = #O(F_p)`, and `w` is the main-term constant of its count (for a curve with `w` absolutely irreducible components over `F_p`, `N_off ~ w p`).

**Premise `H-GEOM-w1`.** Let `N*` be the number of points `(c, t)` of `G = 0` over `F_p` with `t != 0`, and `N_off` the number of points `(c, s_1, s_2)` over `F_p` with `G(c, s_1) = G(c, s_2) = 0`, `s_1^2 != s_2^2` and `s_1 s_2 != 0`. Then `N* / p >= 1 - eps` and `N_off / p <= w (1 + eps)`, with `w = 1` and `eps = 0.21`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r21-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2), the polynomial `F` of section 2.3; centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:** it concerns this `F`, not every polynomial of degree `D`: it is false for permutation polynomials, in particular for every pure composition of maps `x -> a x^5 + b` (`p = 2 mod 5`, so those maps are bijective), and it is not implied by a statement about components over the algebraic closure alone (`F(X) = X^3` over `F_101`: `(F(X) - F(Y)) / (X - Y)` splits into two conjugate lines over `F_(101^2)`, the curve has no off-diagonal rational point, and `k` is zero for every `c`). The explicit constants of 9.2 apply for every r >= 13 as stated, with no genus bound: the Weil majorant of the second moment (Grok job 138) exceeds the main term from r = 13, so the premise is stated as the count statement itself, which Grok job 139 measures on toy copies (10.3).

What the premise does not contain: no random-polynomial model, no independence of different centres (they are independent because each draw uses distinct fresh random words), no statement about the number of roots beyond the two moments of 9.2.

### 9.2 The reduction to explicit constants, and the success bound

For `c` uniform in `F_p` write `E[.]` for the mean over `c`.

(a) *Squares.* For `t != 0` the values `t` and `-t` give the same `S = t^2` and different points `(c, t)`, so `E[k] = N* / (2p)` with `N* = #{ (c, t) : t != 0, G(c, t) = 0 }`.

(b) *First moment.* By the premise `N* >= (1 - eps) p`, so `E[k] = N* / (2p) >= 1/2 - e_1` with `e_1 = eps / 2`; `e_1 < 1.050e-01` at r = 21. No genus bound is used.

(c) *Second moment.* `k(k-1)` counts ordered pairs of distinct usable squares; each pair lifts to 4 points `(s_1, s_2)` by independent signs, and `s_1^2 != s_2^2`, `s_1 s_2 != 0` define `O`. So `E[k(k-1)] = N_off / (4p) <= w (1 + eps) / 4 = w/4 + e_2` with `e_2 = w eps / 4`; `e_2 < 5.250e-02` at r = 21. (The bound of the premise has the form of the weakest count statement that keeps the success bound at 0.39: Grok job 138, `N*^2 >= q_* p (2 N* + N_off)`; the relative form used here, with one `eps` on both counts, is a sufficient condition for it.)

(d) *Cauchy-Schwarz.* `(E[k])^2 = (E[k 1_(k >= 1)])^2 <= E[k^2] P(k >= 1)` and `E[k^2] = E[k] + E[k(k-1)]`, so `P(k >= 1) >= a^2 / (a + b)` with `a = E[k]` and `b = E[k(k-1)]`. The right side increases in `a` and decreases in `b`, so its minimum over `a >= 1/2 - e_1`, `b <= w/4 + e_2` is at the corner: `P(k >= 1) >= (1/2 - e_1)^2 / (1/2 - e_1 + w/4 + e_2) = 0.2236917563`.

(e) *The cap `DMAX`.* `k >= DMAX + 1` implies `k(k-1) >= (DMAX+1) DMAX = 272`, so by Markov `P(k > DMAX) <= (w/4 + e_2) / 272 = 0.0011121324`. Therefore, for `c` uniform, the event `E_c : 1 <= k(c) <= DMAX` has probability at least `q = 0.2236917563 - 0.0011121324 = 0.2225796239`; the entry uses `q = 0.22257`.

(f) *Centres, normal sequences, the zero test of stage C and isolation.* The algorithm draws its centres `c_1, ..., c_K` from fresh random words by the rule of 4.1.1; each is within statistical distance `eps_coin < 2^-128` of uniform (the exact value is 1.574e-39 (2^-128.90)), and the draws are independent. For a centre `c` let `N_c` be the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd (every quotient of degree 1, section 6.3); by the premise `H-NORMAL` (9.5), `P(not N_c) <= delta = 2^-100` for `c` uniform. Let `Z_c` be the event that `g_c` vanishes at a point of `O1` (the ABORT of stage C, 4.6 step 5). For every `x` in `F_p` (square or not), `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D != 0`: in `F(c + s) - F(c - s) = 2 s g_c(s^2)`, an identity of polynomials in `(c, s)`, the coefficient of `c^(D-1)` is `2 s D f_D`, and every `f_i` with `i < D` contributes only degrees below `D - 1` in `c`. So for each of the `n1` points of `O1` at most `D - 1` values of `c` are zeros, every value has probability at most `4/2^256` under the draw of 4.1.1, and `P(Z_c) <= delta_C = n1 (D - 1) 4 / 2^256 = 9.59e-40 < 2^-129` for the drawn centre, without a premise. If `N_(c_t)` holds and `Z_(c_t)` does not, stages C and D run without ABORT and return `G = gcd(g_c, R - 1)`. If `E_(c_t)` holds as well, the isolation of stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48` over words that are fresh for that stage (lemma 9.4). A trial with `E_(c_t)`, `N_(c_t)`, not `Z_(c_t)` and a successful isolation ends in a verified collision (sections 2-5). For `c` uniform, `P(E_c and N_c) >= q - delta`. Therefore

`P[no collision in K trials] <= (1 - q + delta + delta_C)^K + K (eps_coin + eps_iso)`,

and, given the two premises,

`P[success] >= 1 - (1 - q + delta + delta_C)^K - K (eps_coin + eps_iso) = 0.395602595 >= 0.39560`, with `q = 0.22257`, `delta = 2^-100`, `delta_C < 2^-129`, `K = 2`, `w = 1` (the terms in `delta` and `delta_C` change the bound by less than `10^-30`).

The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 21 enters it. The arithmetic of (b)-(f) is recomputed with exact rationals by the script of Appendix D (the base entry's), which evaluates the bound at the unrounded `q = 0.2225796239` and without `delta` (0.39562); the claimed value uses `q` rounded down to 0.22257 and the term `delta`: `1 - (1 - 0.22257 + 2^-100)^2 - 2 (eps_coin + eps_iso) = 0.395602595`. If only `k >= 1` were required (no cap `DMAX`), the same arithmetic would give 0.397345511 for two centres.

### 9.3 The parameter w

With the count premise and `w = 1`: the worst corner `N*/p = 1 - eps`, `N_off/p = 1 + eps` gives `q(eps) = (1 - eps)^2 / (3 - eps)` for the Cauchy-Schwarz ratio, decreasing in `eps`; `q(eps) >= 0.22369` at `eps = 0.21`. Without the cap tail the largest `eps` with `1 - (1 - q)^2 >= 0.39` is 0.2197 (Grok job 138; 0.3676 for three centres), and with the tail of 9.2(e) it is 0.2146. The smallest good fraction `q'` (the probability of `E_c`) for which `K` centres give 0.39 is 0.39000 for K=1, 0.21898 for K=2, 0.15191 for K=3 and 0.11625 for K=4 (the terms `K (eps_coin + eps_iso)` are below `10^-14`); with the submitted `K = 2` the good fraction can be smaller than `q` by the factor `0.984` (down to `q' = 0.21898`) before the bound falls below 0.39. The time bound is `T_fixed + K T_trial` with `T_fixed` much smaller than `T_trial`, so `K'` centres instead of `K` cost about `log2(K'/K)` more in `time_log2`. With the premise `H-NORMAL` the good fraction of a centre is `P(E_c and N_c) >= q - delta`; the bound of 9.2(f) stays at least 0.39 as long as `delta <= 0.22257 - 0.21898 = 0.00359`.

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - S3)/2^256 = 1/2 - 7.869e-40` (`S3` of 4.1.1) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `S3` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - S3)/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`, computed exactly in Appendix D. This is a proved bound under the random words, not a premise and not a sample.

### 9.5 The premise `H-NORMAL` (this entry)

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 3,725,290,298,461,914,062`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 2^-100`.

Four fields (as in claim.json). **Role:** score-critical for the success probability only: the time and memory bounds hold for every sequence, because an abnormal sequence ends the trial at its first abnormal quotient after a prefix of the charged work (6.3). **Scope:** the pairs `(g_c, R_c - 1)` of this target at r = 21, `c` uniform; nothing is claimed for other round counts. **Extrapolation and evidence:** for a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-129`. That bound does not transfer directly, because the coefficients of `R_c` are polynomials of degree about `p` in those of `g_c`; the premise is that the structured pair behaves like a random pair in this respect, with a margin of `2^29` in the stated `delta`. Measured support: the base entry ran the complete Euclidean sequence of `(g_c, R_c - 1)` for the same construction on the sibling targets with `r' = 0` and `r' = 1` partial rounds (section 10.5): every quotient had degree 1 in all 10 runs (8 runs of 7,811 steps and 2 of 39,061 steps, 140,610 quotients in all). **Limitations:** not verified at r = 21, which would need the computation itself; a structural reason for a quotient of degree above 1 (an algebraic relation between `g_c` and `R_c` that forces a principal subresultant coefficient to vanish for many centres) would invalidate it, and none is known. The success bound of 9.2 stays at least 0.39 for every `delta <= 0.00359` (9.3), so the claim needs far less than the stated `2^-100`.

## 10. Evidence

This section is the evidence for the premise `H-GEOM-w1` and for the digest of the target, and (10.5) for the premise `H-NORMAL`. It is the base entry's evidence: the executions of 10.1, the computations of 10.3 and the runs of 10.5 were made by the base entry's author; the experiments of 10.2 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

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

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r21-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run is the evidence; this entry declares the base entry's experiments unchanged and does not restate counts that it has not observed. The hypothesis of the manifest is that every one of the 256 trials returns a pair.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 21: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining twenty-seven rounds applied to `alpha + beta W` (`deg F = 5^27`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-GEOM-w1` is about (a root of `g_c`). In the picture of the premise, `F(c+s) - F(c-s) = 2 s g_c(s^2)` takes random-function values in `s` at these widths, so a trial returns a pair with probability `1-(1-2^-w)^150`: 0.9058, 0.4441, 0.1363 and 0.0360, that is about 232, 114, 35 and 9 of the 256 trials for `w` = 6, 8, 10, 12. A clustering of the roots of `g_c`, or a bias of the odd structure, would move these counts.

The counts of the organizer's run are in its intake report; this entry does not restate counts that it has not observed. The expected counts are those stated above (about 232, 114, 35 and 9). 

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypothesis of `H-GEOM-w1` exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-GEOM-w1` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.


**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypothesis of `H-GEOM-w1` exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B (program `certify.py` of job 136, printed in Appendix F). Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the attack's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 27`; the line and the first layers do not depend on r). The results (`certify_dep.py`, Appendix F):

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the attack line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-GEOM-w1` states `w = 1` at `N = 27`; this is the measured trend of the premise (`w = 1` at `N = 1, 2, 3` on the deployed constants, below), and it is our theory that the trend continues to `N = 27`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the attack's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend, and the premise states w = 1 at N = 27: this is our theory, the measured w = 1 at N = 1, 2, 3 continues, and the lemma gives w = 1 or w = 2 given (a) and 2-transitivity.

**Grok job 139 (the counts of the premise on toy copies).** Grok (xAI) computed `N*` and `N_off` exactly for width-3 Hades toy permutations over prime fields `p < 2^22` with `p mod 5 != 1` (S-box `x -> x^5`, uniformly random MDS matrix and round constants, the line `(L, 2L+1, 3L+5)`, `N` full rounds and `k` partial rounds, `deg F = 5^(N+k)` up to 1,953,125), by the fibre counts `N* = sum_y m_y (m_y - 1)` and `N_off = sum_c 4 r(c) (r(c) - 1)` (checked against brute force on the small cases), on 1,316 generic seeds with `p >= 1024` (the five degenerate seeds, where the degree drops, are excluded). The relative error `eps_obs = max(|N*/p - 1|, |N_off/p - w|/w)` with `w = 1` is `<= 0.2197` for every generic seed with `p >= 2053`, and the least-squares fit is `eps_obs = 3.10 / sqrt(p)` for a typical seed (`5.17 / sqrt(p)` for the maximum of four seeds), with no dependence on the degree (adding a term linear in `deg F` moves `R^2` from 0.5508 to 0.5509; the mean of `eps sqrt(p)` is 2.3 to 3.7 for every degree from 5 to 1,953,125); at `p = 2,097,169` the largest generic `eps_obs` is 0.0068. The premise of 9.1 states `eps = 0.21` for the target; this is our theory: the trend `eps ~ 3 / sqrt(p)` continues to `p` of 254 bits (where it is about `2^-126`) and to the polynomial `F` of this target, with the number of components `w = 1` of 10.3 above. The count statement is a sufficient condition for the success bound of 9.2 (Grok job 138).

### 10.4 Scope

One trial at r = 21 needs about 4.8e20 bytes of live memory and 2.2e24 operations. The claim is the premise `H-GEOM-w1` with the reduction of section 9.2, and the premise `H-NORMAL` (9.5); the executed centres at r = 3, 4, 5, the experiments of 10.2, the theorems and computations of 10.3 and the measurements of 10.5 are the evidence for them.
### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 21` applies the Euclidean algorithm to `g_c` (degree `m = 3,725,290,298,461,914,062`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. In this entry this section is the evidence for the premise `H-NORMAL` (9.5): stage D is charged for the normal sequence and a trial aborts on any other (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (`sib_euclid.py`, centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at their gcd (at degree 0 after `m - 1` steps, 7,811 and 39,061 steps, or at degree 1 at the centres with a usable root listed below; no run had a quotient of degree other than 1), and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core. The program `sib_euclid.py` is printed in Appendix F.

At `r = 21` the stages need about 4.8e20 bytes and 4.3e24 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7.

## 11. Appendix D: the premise arithmetic (`premise_numbers.py`)

`python3 premise_numbers.py` recomputes with exact rationals every number of section 9.2 and 9.3.

#### premise_numbers.py

```python
#!/usr/bin/env python3
"""Exact-rational recomputation of the success bound of proof.md section 9 for r = 21 (standard library only; prints every number used).
Premise H-GEOM-w1 gives E[k] >= 1/2 - e1 and E[k(k-1)] <= w/4 + e2 (Weil's bound replaced by the count premise of section 9.1; section 9.2).
Cauchy-Schwarz: P(k >= 1) >= E[k]^2 / (E[k] + E[k(k-1)]).  Markov on k(k-1): P(k >= DMAX+1) <= E[k(k-1)] / ((DMAX+1) DMAX).
q = P(1 <= k <= DMAX) >= the difference; K independent centres: 1 - (1-q)^K - K (eps_coin + eps_iso)."""
import math
from fractions import Fraction as Fr
from math import comb
P = (1 << 254) + 0x224698FC094CF91B992D30ED00000001
SP = 1 << 127                                   # floor(sqrt(P)) = 2^127, (2^127 + 1)^2 > P
R, DMAX, ZCAP = 21, 16, 64
D = 5 ** (6 + R); d = D - 1
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
    q = q_cs - tail
    succ = 1 - (1 - q) ** K - K * (eps_coin + eps_iso)
    return dict(e2=e2, b=b, q_cs=q_cs, tail=tail, q=q, succ=succ, succ_notail=1 - (1 - q_cs) ** K)
def f(x, n=12): return '%.*f' % (n, float(x))
if __name__ == '__main__':
    W, K = 1, 2
    B = bound(W, K)
    print('D = 5^%d = %d, d = D - 1' % (6 + R, D))
    print('e1 < %.3e' % float(e1)); print('e2 < %s' % f(B['e2'], 10))
    print('E[k] >= 1/2 - e1; E[k(k-1)] <= w/4 + e2 = %s  (w = %d)' % (f(B['b'], 10), W))
    print('Cauchy-Schwarz: P(k >= 1) >= %s' % f(B['q_cs'], 10))
    print('Markov tail:    P(k > %d)  <= %s' % (DMAX, f(B['tail'], 10)))
    print('q = P(1 <= k <= %d) >= %s' % (DMAX, f(B['q'], 10)))
    print('K = %d without the tail (P(k >= 1) only): %s' % (K, f(B['succ_notail'], 10)))
    print('per-round good probability w >= %s = 1/2 - %.3e' % (f(wq, 20), float(Fr(1, 2) - wq)))
    print('eps_iso < %.3e (2^%.2f)   eps_coin < %.3e (2^%.2f)' % (float(eps_iso), math.log2(float(eps_iso)), float(eps_coin), math.log2(float(eps_coin))))
    print('success >= 1 - (1-q)^%d - %d (eps_coin + eps_iso) = %s' % (K, K, f(B['succ'], 12)))
    print('claimed success_probability: %s (floor at 5 decimals)' % ('%.5f' % (int(B['succ'] * 100000) / 100000)))
    for w in (1, 2, 3):
        Bw = bound(w, 2)
        print('w = %d: P(k>=1) >= %s, q >= %s, K=2 success %s, K=3 success %s' % (w, f(Bw['q_cs'], 8), f(Bw['q'], 8), f(Bw['succ'], 8), f(bound(w, 3)['succ'], 8)))
```

## 12. Appendix E: the stage C and stage D totals (`stage_cd.py`)

`python3 stage_cd.py` expands the two rows of section 6 that carry almost all of the cost of a trial after stage B, 1,077,028,960,067,639,720,672,037 (stage C) and 1,062,106,645,154,198,605,714,641 (stage D), from the dimensions: stage C in the value domain (`powx_vd`: the tables, the Newton reciprocal and the product for `q`, the evaluations, the 194 steps with their pointwise passes, inner transforms and geometric phases, the exit and the interpolations, 4.6), the block products of 4.5 (the single transform, scheme (a), scheme (c) at every admissible block length, the outer-transform kernels executed by `check_outer`), the half-gcd levels (4.4: truncated second call, windows, the in-place base case, the top node), and the kernel charges of section 4.2. It prints and asserts both totals, the peaks of the live set, the memory figure and `N_max` (about one minute, standard library only). It is the base entry's `stage_cd.py` (Appendix E there), as revised by e6dcb600, with the changes listed in its docstring.

#### stage_cd.py

```python
#!/usr/bin/env python3
"""Appendix E: stage C and stage D of one trial at r = 21, expanded into their totals (standard library only).
Run:  python3 stage_cd.py      prints S_C = 1,077,028,960,067,639,720,672,037 and S_D = 1,062,106,645,154,198,605,714,641, the peaks of the live set,
the memory figure and N_max, and asserts them (about 1 minute).

This is the ledger of the base entry f62fb39 (commit a031a50, Appendix E there) as revised by the entry e6dcb600, with the changes of this entry
(proof.md 4.4, 4.5, 4.6):
  * stage C in the value domain (powx_vd, proof.md 4.6): the residue is held by its values on 2K cosets of the subgroup of order h = 2^32 (O1 and O2),
    one step is two pointwise passes and two extensions (inner transforms of 2^32 points, a convolution across the cosets with outer transforms);
    the start S^v P1 mod g by one Barrett reduction (Newton reciprocal); the exit by one Montgomery reduction and two interpolations to coefficient form;
  * block products (proof.md 4.5): scheme (c) at the cheapest block length HB = 2^b (b = 6 .. 31), and any product, also one that fits a single transform,
    uses whichever of the single transform and schemes (a) and (c) has the smaller charge;
  * stage D (proof.md 4.4): the truncated second recursive call and the normal remainder sequence (every quotient of degree 1; any other quotient aborts
    the trial, 2 operations per test), as in e6dcb600; a node that wants its matrix only forms the top window of c and d; the base case works in place;
    the top node holds g and R as two pieces each and frees the high pieces early; its two applications of a matrix form c, then d (apply_inv_split);
    small calls run in a scratch region (KSCR); the arena is compacted when a request finds no hole (COMPACT, measured by Appendix G.7).
The inputs are m = (5^27 - 1)/2 = 3,725,290,298,461,914,062, the exponent (p-1)/2 and the charging rules of section 4.2 (tables PASS and K3: butterfly 3 field
operations or 2 when the twiddle is 1, twiddle load with address, 8 operations per radix-3 leaf, loop control 3 per iteration and 2 on exit; the outer
kernels ob3, ob2f .. ob8i are executed with their charges by check_outer).
`Tr` accumulates the operations and walks every allocation and free (an allocation is charged 121 + 13 (2 live + 1) + 64, a free 105 + 64; a block is
64 + 32 * slots rounded up to 64 bytes, header included), with the live bytes and their peak and the peak of the temporary arrays inside one call."""
import functools, math

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
PM2, PM1H = P - 2, (P - 1) >> 1
INV_CTL, STAGE_BK, CACHE = 2310, 1000, 64


def powcost(e):
    return (e.bit_length() - 1) + (bin(e).count('1') - 1) if e > 0 else 0


PASS = {   # kernel -> for k = 1..4 layers: (c0, a, b), charge c0 + a*G + b*G*S  (G groups, S = 2^(layers below) - 1)
    'f': ((4, 17, 19), (4, 35, 43), (4, 80, 96), (4, 185, 213)),
    'i': ((4, 17, 21), (4, 36, 47), (4, 82, 102), (4, 188, 221)),
    'usq': ((3, 18, 0), (3, 49, 0), (3, 128, 0), (3, 315, 0)),
    'umul': ((4, 23, 0), (4, 58, 0), (4, 145, 0), (4, 348, 0)),
}

K3 = {   # radix-3 position kernels: K3[type][pattern of nonzero rows 0..7][rotation 0..2]
    'f': [(6,6,6),(8,14,14),(14,8,14),(19,19,25),(14,14,8),(19,25,19),(25,19,19),(24,24,24)],
    'i': [None,(10,16,16),(16,10,16),(20,20,26),(16,16,10),(20,26,20),(26,20,20),(24,24,24)],
    'r0': [(2,2,2),(4,4,4),(4,4,4),(7,7,7),(4,4,4),(7,7,7),(7,7,7),(10,10,10)],
    'r1': [(2,2,2),(4,7,7),(7,4,7),(10,10,13),(7,7,4),(10,13,10),(13,10,10),(16,16,16)],
    'r2': [(2,2,2),(4,7,7),(7,4,7),(10,10,13),(7,7,4),(10,13,10),(13,10,10),(16,16,16)],
}
ROT = ((0, 0, 0), (0, 1, 2), (0, 2, 1))      # rotation of the three kernels of a position triple, by the phase c0


def pass_fwd(a, l0, k):
    c0, p, q = PASS['f'][k - 1]; g = 1 << l0
    return 5 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_inv(a, l0, k):
    c0, p, q = PASS['i'][k - 1]; g = 1 << l0
    return 6 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_fused(a, k, mode):
    c0, p, q = PASS['usq' if mode == 'sq' else 'umul'][k - 1]
    return 6 + (9 * k + 2) + 6 + c0 + p * (1 << (a - k))


FREE_OPS = 105


def blk(slots):
    return 64 + ((slots * 32 + 63) & ~63)


ALLOC_STAT = 64      # the allocator's flat statistics charge (proof.md 4.2), charged on every allocation and every free

class Tr:
    """sequential trace: ops, current live bytes/blocks relative to entry, peaks"""
    __slots__ = ('ops', 'cur', 'peak', 'cnt', 'pcnt', 'base', 'tot')

    def __init__(self, base=0):
        self.ops = 0; self.cur = 0; self.peak = 0; self.cnt = 0; self.pcnt = 0; self.base = base; self.tot = 0   # tot: bytes of all blocks allocated (Appendix G.7)

    def here(self): return self.base + self.cnt            # live blocks now (for sub-traces)

    def bump(self, slots):                                  # peak of a temporary array of `slots` elements that is live only inside one call (no operation charged)
        if slots > 0:
            self.peak = max(self.peak, self.cur + blk(slots)); self.pcnt = max(self.pcnt, self.cnt + 1)

    def bump_blocks(self, slot_list):                       # peak of several temporary arrays live together inside one call (no operation charged)
        self.peak = max(self.peak, self.cur + sum(blk(x) for x in slot_list)); self.pcnt = max(self.pcnt, self.cnt + len(slot_list))

    def ctl(self, n): self.ops += n
    def ld(self, n): self.ops += 2 * n
    def st(self, n): self.ops += 2 * n
    def loopc(self, n): self.ops += 3 * n + 2

    def add(self, o):
        self.ops += o.ops
        self.peak = max(self.peak, self.cur + o.peak); self.pcnt = max(self.pcnt, self.cnt + o.pcnt)
        self.cur += o.cur; self.cnt += o.cnt; self.tot += o.tot

    def new_fp(self, slots):
        slots = max(slots, 1) if slots else 1
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1) + ALLOC_STAT
        b = blk(slots); self.cur += b; self.cnt += 1; self.tot += b
        self.peak = max(self.peak, self.cur); self.pcnt = max(self.pcnt, self.cnt)
        return slots

    def free(self, slots):
        self.ops += FREE_OPS + ALLOC_STAT
        self.cur -= blk(slots); self.cnt -= 1


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


def for8(n):                           # FOR8 / for8_ctl charge of the loop control
    return 1 + 3 * (n // 8) + 2 + 3 * (n % 8) + 2


def make_plan(rows, a):
    p = Plan(rows, a)
    c = 18 + 4 + (3 * p.np + 2) + 4 * p.np + 2 + (4 if rows == 3 else 0)
    return p, c


BIGA = 32                              # v2(p-1) = 32: transform sizes 3*2^a exist in F_p for a <= 32 only; longer products use blocks (proof.md 4.5)
P32, _c32 = make_plan(1, BIGA)         # the block transform plan: one row of 2^32 points
NB = P32.N; HB = NB // 2               # block transform size NB, block length HB = NB/2


def plan3_for_len(ln):
    c = 0
    for a in range(2, 64):
        c += 3 + 1 + 2 + 2
        if 3 * (1 << a) >= ln:
            p, cc = make_plan(3, a); return p, c + cc
    raise ValueError


def split_regions(n, N, boff, lenB):
    c = 3; bp = [0]
    nt0 = 0
    for t in range(3):
        st = nt0 + N - boff
        if st >= N: st -= N
        nt0 += n; c += 9
        c += 3
        if st < lenB:
            x = lenB - st; c += 1; c += 3
            if 0 < x < n: bp.append(x); c += 1
        c += 3
        if st > 0:
            x = N - st; c += 1; c += 3
            if 0 < x < n: bp.append(x); c += 1
            x = N + lenB - st; c += 2; c += 3
            if 0 < x < n: bp.append(x); c += 1
    c += 2
    bp.append(n); c += 1
    cnt = len(bp)
    for a in range(1, cnt):
        key = bp[a]; b = a - 1; c += 3 + 2
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
    c += 2
    c += 2
    if hi > i:
        rem = hi - i; c += 1
        c += K[0]; i += 1; c += 1
        c += 2
        if rem == 2:
            c += K[1]
    return c


def stageA_fwd(Pl, ln):
    c = 4
    n = Pl.n
    if Pl.rows == 1:
        # lean, single row: copy the ln coefficients into the transform array (a load and a store each) and zero the rest (a store each)
        assert ln <= n
        return c + for8(ln) + 4 * ln + for8(n - ln) + 2 * (n - ln) + 2
    bp, pat, cc = split_regions(n, Pl.N, 0, ln); c += cc
    c += 2
    for q in range(len(pat)):
        c += 4 + driver('f', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_inv(Pl, outlen):
    if Pl.rows == 1:
        return 0
    c = 2
    bp, pat, cc = split_regions(Pl.n, Pl.N, 0, outlen); c += cc
    c += 2
    for q in range(len(pat)):
        c += 2
        if pat[q] == 0:
            c += 3; continue
        c += 4 + driver('i', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_row(Pl, r, lenB, boff):
    n = Pl.n
    bp, pat, c = split_regions(n, Pl.N, boff, lenB)
    c += 2
    for q in range(len(pat)):
        c += 3 * 11 + 2 + 4 + driver('r%d' % r, pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def fwd_passes(Pl, cnt):
    l0 = 0; c = 0
    for p in range(cnt):
        c += pass_fwd(Pl.a, l0, Pl.kk[p]) + 4; l0 += Pl.kk[p]
    return c


def inv_passes(Pl, first):            # inverse passes p = first down to 0
    l0 = sum(Pl.kk[:first + 1]); c = 0
    for p in range(first, -1, -1):
        l0 -= Pl.kk[p]
        c += pass_inv(Pl.a, l0, Pl.kk[p]) + 4
    return c


def fused(Pl, mode):
    return pass_fused(Pl.a, Pl.kk[-1], mode)


def mulc_otf_row(Pl, r, lenB, boff):
    c = 12 + stageA_row(Pl, r, lenB, boff)
    c += fwd_passes(Pl, Pl.np) + 2
    c += fwd_passes(Pl, Pl.np - 1) + fused(Pl, 'mul') + inv_passes(Pl, Pl.np - 2) + 4
    return c


def conv_mulc_otf(Pl, ln, lenB, boff, outlen, sub=False, cached=False):
    if Pl.a > BIGA: return conv_mulc_big(ln, lenB, (Pl.N - boff) % Pl.N, outlen, sub, cached)
    c = 2 + stageA_fwd(Pl, ln) + 4
    for r in range(3):
        c += mulc_otf_row(Pl, r, lenB, boff)
    return c + 2 + stageA_inv(Pl, outlen)


def pw_loop(n, mode):
    return for8(n) + n * (7 if mode == 0 else 10)


def conv_bilin_cost(Pl, nout, outlen, groups):
    if Pl.a > BIGA: return conv_bilin_big(nout, outlen, groups)
    c = 2
    eps = [0] * nout
    c += 2 + 3 * nout
    for g in groups:
        for s in range(len(g['S'])):
            for h in range(len(g['H'])):
                c += 6
                o, sg = g['prod'].get((s, h), (-1, 0))
                if o >= 0 and not eps[o]:
                    eps[o] = sg
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
        c += 0
    for k in range(nout):
        c += 3
        if eps[k]:
            c += stageA_inv(Pl, outlen[k])
    return c, eps


# ---------------------------------------------------------------- products longer than 3*2^32: block products (proof.md 4.5)
# A product of two polynomials is split into blocks of HB = 2^31 coefficients.  Scheme (a) (base entry): every block is transformed once with the block
# transform of NB = 2^32 points (plan P32: one row, a copy with zero fill and the radix-2 passes), the transforms of a slot s (the block pairs i + j = s) are multiplied pointwise and summed in the transform domain,
# every slot that meets the wanted output window is inverse transformed once and placed (overlap-added, scaled by 1/NB, or subtracted) into the output.
@functools.lru_cache(maxsize=None)
def big_fwd(bl):                       # forward block transform of a block of bl coefficients (zero-padded to NB)
    return stageA_fwd(P32, bl) + P32.rows * fwd_passes(P32, P32.np)


@functools.lru_cache(maxsize=None)
def big_inv(outn):                     # inverse transform of one slot, the first outn coefficients are needed
    return P32.rows * inv_passes(P32, P32.np - 1) + stageA_inv(P32, outn)


def big_pw(mode):                      # one pointwise product over NB points: mode 0 write, 1 add, 2 subtract (as pw_loop)
    return P32.rows * pw_loop(P32.n, mode)


def nblk(l): return -(-l // HB)


def big_fwd_all(l):                    # all blocks of an operand of l coefficients (closed form)
    k = nblk(l)
    return (k - 1) * big_fwd(HB) + big_fwd(l - (k - 1) * HB)


def big_place(cnt, ov, sub):           # place a slot: cnt coefficients read from the accumulator, scaled by 1/NB, stored; ov of them added to, or all subtracted from, the output
    c = 3 * cnt + 2 + 2 * cnt + cnt + 2 * cnt            # loop control, load, scale multiplication, store
    return c + (cnt if sub else ov) * 3                   # load of the output value and the add or subtract


# ---------------------------------------------------------------- scheme (c): the chunked outer product (proof.md 4.5)
OCALL = 10                               # one kernel call: call, return and argument setup


# ---------------------------------------------------------------- lean: register-blocked outer transform, kernel text executed under the charging rules of 4.2
# The outer transform of n = 2^a or 3*2^a points runs at each of cnt positions on n blocks of an array.  3 | n: Good-Thomas, a twiddle-free radix-3 stage
# (ob3) then three rows of 2^a points; each row is a radix-2 DIF of passes of at most three layers (ob2f, ob4f, ob8f; the short pass first).  A pass of k
# layers keeps 2^k data words and its 2^k - 1 twiddles in registers for the whole position loop (ob8: 8 + 7 + the butterfly temporary = 16 of the 18 words).
# The inverse is the same pass structure in reverse order (ob8i, ob4i, ob2i: DIT, inverse twiddles), then ob3 with the conjugate constant; it returns n x.
# KCOUNT counts every executed primitive: LD and ST 2 each (the access and its address operation), MUL/ADD/SUB 1, CTL k, LOOP 3 per iteration and 2 on exit.
KCOUNT = [0]


def LD(a, i): KCOUNT[0] += 2; return a[i]
def ST(a, i, v): KCOUNT[0] += 2; a[i] = v
def MUL(x, y): KCOUNT[0] += 1; return x * y % P
def ADD(x, y): KCOUNT[0] += 1; return (x + y) % P
def SUB(x, y): KCOUNT[0] += 1; return (x - y) % P
def CTL(k): KCOUNT[0] += k


def LOOP(n):
    for t in range(n):
        KCOUNT[0] += 3; yield t
    KCOUNT[0] += 2


OUTER_KERNELS = r'''
def ob3(A, p, cst, cnt):
    CTL(OCALL)
    p0, p1, p2 = p
    c1 = LD(cst, 0); c2 = LD(cst, 1)
    for t in LOOP(cnt):
        a = LD(A, p0 + t); b = LD(A, p1 + t); c = LD(A, p2 + t)
        s = ADD(b, c); d = SUB(b, c)
        u = ADD(a, MUL(c1, s)); v = MUL(c2, d)
        ST(A, p0 + t, ADD(a, s)); ST(A, p1 + t, ADD(u, v)); ST(A, p2 + t, SUB(u, v))


def ob2f(A, p, tw, e, cnt):
    CTL(OCALL)
    p0, p1 = p
    w0 = LD(tw, e[0])
    for t in LOOP(cnt):
        a0 = LD(A, p0 + t); a1 = LD(A, p1 + t)
        b = SUB(a0, a1); a0 = ADD(a0, a1); a1 = MUL(b, w0)
        ST(A, p0 + t, a0); ST(A, p1 + t, a1)


def ob4f(A, p, tw, e, cnt):
    CTL(OCALL)
    p0, p1, p2, p3 = p
    w0 = LD(tw, e[0]); w1 = LD(tw, e[1]); w2 = LD(tw, e[2])
    for t in LOOP(cnt):
        a0 = LD(A, p0 + t); a1 = LD(A, p1 + t); a2 = LD(A, p2 + t); a3 = LD(A, p3 + t)
        b = SUB(a0, a2); a0 = ADD(a0, a2); a2 = MUL(b, w0)
        b = SUB(a1, a3); a1 = ADD(a1, a3); a3 = MUL(b, w1)
        b = SUB(a0, a1); a0 = ADD(a0, a1); a1 = MUL(b, w2)
        b = SUB(a2, a3); a2 = ADD(a2, a3); a3 = MUL(b, w2)
        ST(A, p0 + t, a0); ST(A, p1 + t, a1); ST(A, p2 + t, a2); ST(A, p3 + t, a3)


def ob8f(A, p, tw, e, cnt):
    CTL(OCALL)
    p0, p1, p2, p3, p4, p5, p6, p7 = p
    w0 = LD(tw, e[0]); w1 = LD(tw, e[1]); w2 = LD(tw, e[2]); w3 = LD(tw, e[3]); w4 = LD(tw, e[4]); w5 = LD(tw, e[5]); w6 = LD(tw, e[6])
    for t in LOOP(cnt):
        a0 = LD(A, p0 + t); a1 = LD(A, p1 + t); a2 = LD(A, p2 + t); a3 = LD(A, p3 + t)
        a4 = LD(A, p4 + t); a5 = LD(A, p5 + t); a6 = LD(A, p6 + t); a7 = LD(A, p7 + t)
        b = SUB(a0, a4); a0 = ADD(a0, a4); a4 = MUL(b, w0)
        b = SUB(a1, a5); a1 = ADD(a1, a5); a5 = MUL(b, w1)
        b = SUB(a2, a6); a2 = ADD(a2, a6); a6 = MUL(b, w2)
        b = SUB(a3, a7); a3 = ADD(a3, a7); a7 = MUL(b, w3)
        b = SUB(a0, a2); a0 = ADD(a0, a2); a2 = MUL(b, w4)
        b = SUB(a1, a3); a1 = ADD(a1, a3); a3 = MUL(b, w5)
        b = SUB(a4, a6); a4 = ADD(a4, a6); a6 = MUL(b, w4)
        b = SUB(a5, a7); a5 = ADD(a5, a7); a7 = MUL(b, w5)
        b = SUB(a0, a1); a0 = ADD(a0, a1); a1 = MUL(b, w6)
        b = SUB(a2, a3); a2 = ADD(a2, a3); a3 = MUL(b, w6)
        b = SUB(a4, a5); a4 = ADD(a4, a5); a5 = MUL(b, w6)
        b = SUB(a6, a7); a6 = ADD(a6, a7); a7 = MUL(b, w6)
        ST(A, p0 + t, a0); ST(A, p1 + t, a1); ST(A, p2 + t, a2); ST(A, p3 + t, a3)
        ST(A, p4 + t, a4); ST(A, p5 + t, a5); ST(A, p6 + t, a6); ST(A, p7 + t, a7)


def ob2i(A, p, tw, e, cnt):
    CTL(OCALL)
    p0, p1 = p
    w0 = LD(tw, e[0])
    for t in LOOP(cnt):
        a0 = LD(A, p0 + t); a1 = LD(A, p1 + t)
        b = MUL(a1, w0); a1 = SUB(a0, b); a0 = ADD(a0, b)
        ST(A, p0 + t, a0); ST(A, p1 + t, a1)


def ob4i(A, p, tw, e, cnt):
    CTL(OCALL)
    p0, p1, p2, p3 = p
    w0 = LD(tw, e[0]); w1 = LD(tw, e[1]); w2 = LD(tw, e[2])
    for t in LOOP(cnt):
        a0 = LD(A, p0 + t); a1 = LD(A, p1 + t); a2 = LD(A, p2 + t); a3 = LD(A, p3 + t)
        b = MUL(a1, w2); a1 = SUB(a0, b); a0 = ADD(a0, b)
        b = MUL(a3, w2); a3 = SUB(a2, b); a2 = ADD(a2, b)
        b = MUL(a2, w0); a2 = SUB(a0, b); a0 = ADD(a0, b)
        b = MUL(a3, w1); a3 = SUB(a1, b); a1 = ADD(a1, b)
        ST(A, p0 + t, a0); ST(A, p1 + t, a1); ST(A, p2 + t, a2); ST(A, p3 + t, a3)


def ob8i(A, p, tw, e, cnt):
    CTL(OCALL)
    p0, p1, p2, p3, p4, p5, p6, p7 = p
    w0 = LD(tw, e[0]); w1 = LD(tw, e[1]); w2 = LD(tw, e[2]); w3 = LD(tw, e[3]); w4 = LD(tw, e[4]); w5 = LD(tw, e[5]); w6 = LD(tw, e[6])
    for t in LOOP(cnt):
        a0 = LD(A, p0 + t); a1 = LD(A, p1 + t); a2 = LD(A, p2 + t); a3 = LD(A, p3 + t)
        a4 = LD(A, p4 + t); a5 = LD(A, p5 + t); a6 = LD(A, p6 + t); a7 = LD(A, p7 + t)
        b = MUL(a1, w6); a1 = SUB(a0, b); a0 = ADD(a0, b)
        b = MUL(a3, w6); a3 = SUB(a2, b); a2 = ADD(a2, b)
        b = MUL(a5, w6); a5 = SUB(a4, b); a4 = ADD(a4, b)
        b = MUL(a7, w6); a7 = SUB(a6, b); a6 = ADD(a6, b)
        b = MUL(a2, w4); a2 = SUB(a0, b); a0 = ADD(a0, b)
        b = MUL(a3, w5); a3 = SUB(a1, b); a1 = ADD(a1, b)
        b = MUL(a6, w4); a6 = SUB(a4, b); a4 = ADD(a4, b)
        b = MUL(a7, w5); a7 = SUB(a5, b); a5 = ADD(a5, b)
        b = MUL(a4, w0); a4 = SUB(a0, b); a0 = ADD(a0, b)
        b = MUL(a5, w1); a5 = SUB(a1, b); a1 = ADD(a1, b)
        b = MUL(a6, w2); a6 = SUB(a2, b); a2 = ADD(a2, b)
        b = MUL(a7, w3); a7 = SUB(a3, b); a3 = ADD(a3, b)
        ST(A, p0 + t, a0); ST(A, p1 + t, a1); ST(A, p2 + t, a2); ST(A, p3 + t, a3)
        ST(A, p4 + t, a4); ST(A, p5 + t, a5); ST(A, p6 + t, a6); ST(A, p7 + t, a7)
'''
exec(OUTER_KERNELS, globals())
FWD_K = {1: ob2f, 2: ob4f, 3: ob8f}
INV_K = {1: ob2i, 2: ob4i, 3: ob8i}
ADR_CTL, TWI_CTL = 4, 3                  # driver: a block address (an addition, a comparison, a branch, a conditional subtraction), a twiddle index (two additions and a mask)


def kernel_charge(name):
    """(c0, c1): the executed charge of kernel `name` is c0 + c1 * cnt, measured by running its text at cnt = 1, 2, 3"""
    f = globals()[name]; k = {'ob3': 0, 'ob2f': 1, 'ob2i': 1, 'ob4f': 2, 'ob4i': 2, 'ob8f': 3, 'ob8i': 3}[name]
    got = []
    for cnt in (1, 2, 3):
        nb = 3 if k == 0 else 1 << k
        A = list(range(1, nb * cnt + 1)); p = [i * cnt for i in range(nb)]
        KCOUNT[0] = 0
        if k == 0: f(A, p, [2, 3], cnt)
        else: f(A, p, list(range(5, 5 + (1 << k))), list(range((1 << k) - 1)), cnt)
        got.append(KCOUNT[0])
    c1 = got[1] - got[0]; c0 = got[0] - c1
    assert got[2] == c0 + 3 * c1, name
    return c0, c1


KCH = {nm: kernel_charge(nm) for nm in ('ob3', 'ob2f', 'ob4f', 'ob8f', 'ob2i', 'ob4i', 'ob8i')}


def outer_plan(n):
    r3 = n % 3 == 0; M = n // 3 if r3 else n
    a = M.bit_length() - 1
    assert (1 << a) == M, n
    return r3, M, ([a % 3] if a % 3 else []) + [3] * (a // 3)


def outer_run(A, n, cnt, w, inv=False):
    """execute the outer transform of n points at cnt positions on A (block b at offset b*cnt), w a primitive n-th root, with KCOUNT charging.
    Forward: block (M k1 + 3 i2) mod n of row k1 ends holding the transform at k = CRT(k1 mod 3, bitrev(position) mod M).  inv: the inverse map (times n)."""
    r3, M, ks = outer_plan(n)
    tw = [0] * n; x = 1
    for i in LOOP(n):
        ST(tw, i, x); x = MUL(x, w)
    rows = [[(M * k1 + 3 * i2) % n for i2 in range(M)] for k1 in range(3)] if r3 else [list(range(n))]
    if r3:
        om = pow(w, M, P); i2v = pow(2, P - 2, P)
        c1 = (om + om * om) * i2v % P; c2 = (om - om * om) * i2v % P
        cst = [c1, (P - c2) % P if inv else c2]; CTL(10)
    def radix3():
        for i2 in LOOP(M):
            CTL(3 * ADR_CTL)
            ob3(A, [((M * i1 + 3 * i2) % n) * cnt for i1 in range(3)], cst, cnt)
    def passes(rb, order):
        for k, Ns in LOOP_LIST(order):
            h = Ns >> k; kern = (INV_K if inv else FWD_K)[k]
            for base in LOOP(M // Ns):
                b0 = base * Ns
                for i in LOOP(h):
                    CTL((1 << k) * ADR_CTL + ((1 << k) - 1) * TWI_CTL)
                    ex = [(i + q * (Ns >> 3 if k == 3 else Ns >> 2 if k == 2 else Ns >> 1)) * (n // Ns) for q in range(1 << (k - 1))]
                    if k >= 2: ex += [(i + q * (Ns >> 3 if k == 3 else Ns >> 2)) * (2 * n // Ns) for q in range(1 << (k - 2))]
                    if k == 3: ex += [i * (4 * n // Ns)]
                    if inv: ex = [(n - x_) % n for x_ in ex]
                    kern(A, [rb[b0 + i + q * h] * cnt for q in range(1 << k)], tw, ex, cnt)
    sched = []; Ns = M
    for k in ks: sched.append((k, Ns)); Ns >>= k
    if not inv and r3: radix3()
    for rb in LOOP_LIST(rows):
        passes(rb, sched if not inv else sched[::-1])
    if inv and r3: radix3()


def LOOP_LIST(xs):
    for t in LOOP(len(xs)): yield xs[t]


def ontt(n, cnt, inv=False):
    """closed form of the charge of outer_run(n, cnt): asserted equal to the executed count at small sizes (check_outer)"""
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


def check_outer():
    """the kernels compute the outer transform and its inverse, and ontt equals the executed count"""
    import random
    rnd = random.Random(5)
    for n in (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 768):
        cnt = 2
        w = pow(5, (P - 1) // n, P)
        assert pow(w, n, P) == 1 and all(pow(w, n // q, P) != 1 for q in (2, 3) if n % q == 0)
        x = [rnd.randrange(P) for _ in range(n * cnt)]
        A = x[:]; KCOUNT[0] = 0; outer_run(A, n, cnt, w); assert KCOUNT[0] == ontt(n, cnt), n
        r3, M, ks = outer_plan(n); a = M.bit_length() - 1
        rev = lambda v: int(format(v, '0%db' % a)[::-1], 2) if a else 0
        for k1 in range(3 if r3 else 1):
            for pos in range(M):
                k2 = rev(pos)
                k = next(kk for kk in range(n) if kk % M == k2 and (not r3 or kk % 3 == k1))
                b = (M * k1 + 3 * pos) % n if r3 else pos
                for t in range(cnt):
                    assert A[b * cnt + t] == sum(x[i * cnt + t] * pow(w, i * k, P) for i in range(n)) % P, (n, k)
        KCOUNT[0] = 0; outer_run(A, n, cnt, w, inv=True); assert KCOUNT[0] == ontt(n, cnt, True), n
        assert A == [v * n % P for v in x], n
    return True


def pad23(n):
    best = None
    for a in range(0, 33):
        for c in (1, 3):
            v = c << a
            if v >= n and (best is None or v < best): best = v
    assert best is not None, n
    return best


MODE_LOG = {}
CTX = {'cf': None, 'ltrue': None, 'cyc': None, 'cfrel': None}   # cf: the chunk bound of the product being evaluated (elements of one chunk array); ltrue: true lengths of the outputs
                                                  # (apply_inv: the high coefficients cancel); cyc: the cyclic length the product may wrap at (q*g of stage C)
PL = {}                                           # description of the last block product evaluated by conv_bilin_big: scheme, n2, nc, and its temporary arrays
CF = {}                                           # chunk bounds per product kind, in elements (set by main from fractions of m): sq, q, qg, newton, D


def nc_for(n2, cf):
    """the number of chunks: the smallest power of two nc with (n2 / nc) * HB <= cf (n2 / nc stays of the form 2^a or 3 * 2^a)"""
    nc = 1
    while cf is not None and (n2 // nc) * HB > cf and (n2 // nc) % 2 == 0: nc *= 2
    return nc


def segs(ws, ln):
    """the pieces of the coefficient window [ws, ws + ln) cut at the block boundaries (multiples of HB), as (length, count) pairs"""
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
    """twist and fold an operand of l coefficients (kx blocks) into its chunk array of n3 rows of HB: row u = sum over the blocks i = u (mod n3) of w^(j i) X_i.
    tw = 1 for a chunk j > 0 (one multiplication per coefficient), 0 for j = 0.  The first block of a row: load, (multiply), store; a further block: load both,
    (multiply), add, store; a row with no block, and the tail of a partial first block, are zeroed (a store).  Each (row, block) piece: 10 operations (the twist
    factor of the block, a multiplication, and the addresses) and the loop control of the piece; the loop over the pieces 3 per piece and 2."""
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
    """untwist the inverse-transformed chunk into the output window [ws, ws + ln): per coefficient a load, the multiplication by the block factor
    w^(-j s) / (NB n2), and a store, plus (j > 0, or an output subtracted from an array) a load of the output value and the addition or subtraction"""
    per = 5 if (first and not sub) else 8
    ss = segs(ws, ln)
    return sum(c * (10 + for8(x) + per * x + 3) for x, c in ss) + 2


FOLD_ROW = 8 * HB + for8(HB) + 4      # the inner fold of one outer point: lower + w^o * upper half of the inverse inner transform, into a row of the output chunk array


def _gp(n, kb):
    if n <= 0: return 0
    return n * (n + 1) // 2 if n <= kb else kb * (kb + 1) // 2 + (n - kb) * kb


def pairs_upto(ka, kb, s):
    """number of block pairs (i, j) with i + j <= s"""
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




@functools.lru_cache(maxsize=None)
def bplan(hb):
    """the block transform of NB = 2 hb points (one row of radix-2 passes, section 4.2) for blocks of hb coefficients"""
    return make_plan(1, (2 * hb).bit_length() - 1)[0]


@functools.lru_cache(maxsize=None)
def bfwd(bl, hb):
    P_ = bplan(hb); return stageA_fwd(P_, bl) + fwd_passes(P_, P_.np)


@functools.lru_cache(maxsize=None)
def binv(hb):
    P_ = bplan(hb); return inv_passes(P_, P_.np - 1)


def nblk_h(l, hb): return -(-l // hb)


def segs_h(ws, ln, hb):
    e = ws + ln
    if ln <= 0: return []
    q = min(e, (ws // hb + 1) * hb)
    if q == e: return [(ln, 1)]
    out = [(q - ws, 1)]
    full = (e - q) // hb; rest = e - q - full * hb
    if full: out.append((hb, full))
    if rest: out.append((rest, 1))
    return out


def fold_ops_h(l, n3, tw, hb):
    """fold_ops at block length hb"""
    kx = nblk_h(l, hb); last = l - (kx - 1) * hb
    wr = 4 + tw; ac = 7 + tw
    first = min(kx, n3); acc = kx - first; zero_rows = max(0, n3 - kx)
    c = 0
    if kx <= n3:
        c += (first - 1) * (10 + for8(hb) + wr * hb) + 10 + for8(last) + wr * last + for8(hb - last) + 2 * (hb - last)
    else:
        c += first * (10 + for8(hb) + wr * hb) + (acc - 1) * (10 + for8(hb) + ac * hb) + 10 + for8(last) + ac * last
    c += zero_rows * (10 + for8(hb) + 2 * hb)
    return c + 3 * (kx + zero_rows) + 2


def acc_ops_h(ws, ln, first, sub, hb):
    per = 5 if (first and not sub) else 8
    return sum(c * (10 + for8(x) + per * x + 3) for x, c in segs_h(ws, ln, hb)) + 2


def fold_row_h(hb): return 8 * hb + for8(hb) + 4


def nc_for_h(n2, cf, hb):
    nc = 1
    while cf is not None and (n2 // nc) * hb > cf and (n2 // nc) % 2 == 0: nc *= 2
    return nc


HB_BITS = range(6, BIGA)          # the block lengths 2^b of scheme (c) (proof.md 4.5): the cheapest admissible one is used


def scheme_c(hb, need, ops_, prods, live, nout, outlen, ws, sub):
    """scheme (c) at block length hb: returns (charge, temps, n2, nc) or None when n2 would exceed 3 * 2^32"""
    q = -(-need // hb)
    if q > 3 << BIGA: return None
    n2 = pad23(q)
    cfx = CTX['cf']
    if CTX.get('cfrel') is not None and cfx is not None: cfx = min(cfx, max(hb, int(CTX['cfrel'] * n2 * hb)))
    nc = nc_for_h(n2, cfx, hb); n3 = n2 // nc
    nb2 = 2 * hb
    pw0, pw1 = pw_loop(nb2, 0), pw_loop(nb2, 1)
    mops = [l for l in ops_ if nblk_h(l, hb) > 1]; singles = [l for l in ops_ if nblk_h(l, hb) == 1]
    co = 2 + ROOTS + sum(bfwd(l, hb) for l in singles) + 3 * nc + 2
    for j_first, mult in ((True, 1), (False, nc - 1)):
        if not mult: continue
        cj = 6 + sum(fold_ops_h(l, n3, 0 if j_first else 1, hb) for l in mops) + len(mops) * ontt(n3, hb) + n3 * (8 + len(mops) * bfwd(hb, hb))
        for k in live:
            cj += n3 * (pw0 + (len(prods[k]) - 1) * pw1 + binv(hb) + fold_row_h(hb)) + ontt(n3, hb, True) + acc_ops_h(ws, outlen[k], j_first, sub, hb)
        co += mult * cj
    temps = [n3 * hb] * max(len(mops), len(live)) + [nb2] * (len(ops_) + len(live)) + [n3]
    return co, temps, n2, nc


ROOTS = 6 * (330 + INV_CTL)       # per block product: the roots w (order n2) and w^nc, their inverses, 1/n2 and the radix-3 constants, each charged as one inversion or exponentiation


def conv_bilin_big(nout, outlen, groups, ws=0, sub=False, shared=False, cached=False):
    """block version of conv_bilin_cost (lean).  Returns (ops, eps) and describes the scheme used in PL.  Scheme (a) (all block pairs, closed form, unchanged), or
    scheme (c), the chunked outer product: the result is formed modulo Y^n2 - 1 (Y = X^HB) with n2 * HB at least what the window needs (the output length, or the
    true length of the bilinear form when its high coefficients cancel, or the cyclic length of q*g), in nc chunks of n3 = n2 / nc outer points (residues o = j mod nc).
    Chunk j: every operand of more than one block is twisted and folded into a chunk array of n3 rows of HB and outer-transformed (ontt); at each outer point
    the rows are inner-transformed, multiplied pointwise (summed over the products), inverse inner-transformed and folded into a row of the output chunk array
    (it overwrites a dead operand row); each output chunk array is inverse outer-transformed and untwisted into the output in coefficient form.  Operands of one
    block are transformed once.  The operands stay in coefficient form for the whole product; nothing is persistent."""
    assert not cached
    eps = [0] * nout
    for g in groups:
        for s in range(len(g['S'])):
            for h in range(len(g['H'])):
                o, sg = g['prod'].get((s, h), (-1, 0))
                if o >= 0 and not eps[o]: eps[o] = sg
    prods = [[] for _ in range(nout)]
    for g in groups:
        for (si, hi_), (o, sg) in g['prod'].items():
            if o >= 0: prods[o].append((g['S'][si], g['H'][hi_]))
    ops_ = []
    for g in groups:
        ops_ += list(g['H'])
        if not shared: ops_ += list(g['S'])
    pw0, pw1 = big_pw(0), big_pw(1)
    # ---- scheme (a)
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
            rep = edges[2] + 1
            ca += mid * slot_cost(rep, s0, ws, we, sub)
    temps_a = [nblk(l) * NB for l in ops_] + [NB]
    # ---- scheme (c), chunked
    need = 0
    lt = CTX['ltrue']
    for k in live:
        if CTX['cyc']: need = max(need, CTX['cyc'])
        else:
            L = lt[k] if lt else max(ls + lh - 1 for ls, lh in prods[k])
            need = max(need, ws + outlen[k], L - ws)
    best = None
    for bb in HB_BITS:
        r_ = scheme_c(1 << bb, need, ops_, prods, live, nout, outlen, ws, sub)
        if r_ is not None and (best is None or r_[0] < best[0]): best = r_ + (1 << bb,)
    co, temps_c, n2, nc, hbc = best
    use_c = co <= ca or (CTX.get('tcap') is not None and sum(temps_a) > CTX['tcap'])
    PL.clear(); PL.update(mode='c' if use_c else 'a', n2=n2 if use_c else 0, nc=nc if use_c else 0, hb=hbc if use_c else HB, temps=temps_c if use_c else temps_a, ca=ca, co=co)
    MODE_LOG[PL['mode']] = MODE_LOG.get(PL['mode'], 0) + 1
    return (co if use_c else ca), eps




def conv_mulc_big(ln, lenB, ws, outlen, sub=False, cached=False):
    return conv_bilin_big(1, [outlen], [dict(H=[lenB], S=[ln], prod={(0, 0): (0, 1)})], ws, sub, False, cached)[0] + 6


def product_peak(T, Pl, nout=1):
    """the temporary arrays of the product just evaluated (allocated at its start and freed at its end)"""
    arr = PL['temps'] if Pl.a > BIGA else [Pl.n]                   # a product that fits one transform: its transform row
    ids = [T.new_fp(x) for x in arr]
    for x in ids: T.free(x)


def ebit(E, i): return (E >> i) & 1


VH = 1 << BIGA                 # h: the inner transform of 2^32 points (plan P32, one row of radix-2 passes), in place on a coset of the value array
VCNT = 1 << 10                 # inner positions per group of the geometric phase (the outer kernels run over these positions)
VSHIFT = 2                     # the start monomial is S^(2^(61 - VSHIFT)); VSHIFT more squaring steps, a shorter Newton reciprocal
INNER_CALL = 10                # the call of one inner transform and its coset address


def inner_all(ncos, inv):
    """ncos inner transforms of h points, one per coset, in place (the first pass may read another array: the same charges)"""
    one = inv_passes(P32, P32.np - 1) if inv else fwd_passes(P32, P32.np)
    return ncos * (one + INNER_CALL) + 3 * ncos + 2


def rows_rec(cnt, rows):
    """copy rows of cnt elements between the value array and a group buffer with a scale that changes along the positions: per element a load,
    the multiplication by the factor, the multiplication of the factor by its step, a store; per row the factor and its step loaded, the factor
    stored back for the next group, and the addresses"""
    return rows * (16 + for8(cnt) + 6 * cnt) + 3 * rows + 2


def rows_const(cnt, rows):
    """rows of cnt elements multiplied by a per-row constant (copy or in place): per element a load, a multiplication, a store; per row the constant"""
    return rows * (12 + for8(cnt) + 5 * cnt) + 3 * rows + 2


def rows_zero(cnt, rows):
    return rows * (10 + for8(cnt) + 2 * cnt) + 3 * rows + 2


def gconv(Lc, kin, cnt):
    """the convolution of a group with a fixed kernel: rows kin .. Lc - 1 zeroed, forward outer transform (ontt) of Lc points at cnt positions,
    pointwise product by the stored kernel spectrum (a per-row constant), inverse outer transform"""
    return rows_zero(cnt, Lc - kin) + ontt(Lc, cnt) + rows_const(cnt, Lc) + ontt(Lc, cnt, True)


def geo_phase(per_group, cnt=VCNT):
    ng = VH // cnt
    return ng * (20 + per_group) + 3 * ng + 2


def rows_reset(rows):
    """the running factors of a phase set from their base table: per row a load and a store, the loop"""
    return 7 * rows + 2


def geo_ext(kin, kout, Lc, cnt=VCNT):
    """extension across the cosets: kin rows in (scaled, from the inverse inner transforms), convolution, kout rows out (scaled, for the forward inner transforms)"""
    return rows_reset(kin) + rows_reset(kout) + geo_phase(rows_rec(cnt, kin) + gconv(Lc, kin, cnt) + rows_rec(cnt, kout), cnt)


def geo_eval(kin, kout, Lc, cnt=VCNT):
    """chirp evaluation of a polynomial in coefficient form (rows of h coefficients) at kout geometric nodes: rows scaled by per-row constants, one
    convolution with the chirp, kout rows out with the per-(row, position) scale of the forward inner transforms"""
    return rows_reset(kout) + geo_phase(rows_const(cnt, kin) + gconv(Lc, kin, cnt) + rows_rec(cnt, kout), cnt)


def geo_interp(k, Lc, cnt=VCNT):
    """interpolation at k geometric nodes back to coefficient form (rows of h coefficients): rows in with the per-(row, position) scale, the first
    correlation (with the chirp), the rows moved with a per-row scale, the second correlation (with the coefficients of M), rows out with a per-row scale"""
    return rows_reset(k) + geo_phase(rows_rec(cnt, k) + gconv(Lc, k, cnt) + rows_const(cnt, k) + gconv(Lc, k, cnt) + rows_const(cnt, k), cnt)


def pw_cosets(ncos, per_elt, per_coset=14):
    """a pointwise pass over ncos cosets of h values: per element per_elt, per coset its constants and addresses, loops by the eight-element rule"""
    return ncos * (per_coset + for8(VH) + per_elt * VH) + 3 * ncos + 2


def batch_inv(ncos):
    """-1/g in place on ncos cosets: per coset the prefix products (load, multiplication, store into the auxiliary array), one inversion with its zero
    test (a zero prefix product ABORTs the trial), and the backward pass (two loads, two multiplications, the negation, a store)"""
    return ncos * (20 + for8(VH) + 5 * VH + 330 + INV_CTL + 2 + for8(VH) + 9 * VH) + 3 * ncos + 2


def kernel_spectrum(Lc, nent):
    """a fixed kernel of Lc points: nent entries computed (each charged as one inversion and 20 operations), the rest zeroed, one forward outer transform"""
    return nent * (330 + INV_CTL + 20) + 2 * (Lc - nent) + ontt(Lc, 1)


def newton_recip(T, L):
    """the reciprocal of the reversed g modulo X^L by the Newton iteration of the base entry (two products per doubling), into an array of L elements;
    the reversed top L coefficients of g are first copied into an array of their own"""
    sG = T.new_fp(L); T.ld(L); T.st(L); T.loopc(L); T.ctl(L)
    sM = T.new_fp(L); sY = T.new_fp(L)
    CTX['cf'] = CF.get('newton'); CTX['tcap'] = TCAP_NEWTON[0]
    try:
        T.ctl(4 + 8); T.st(1)
        l = 1
        while l < L:
            l2 = min(2 * l, L)
            T.ctl(8)
            P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
            T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
            if P1.a > BIGA: product_peak(T, P1)
            else: T.bump(P1.n)
            T.ctl(plan_invN_ops(P1))
            T.ops += l2 - l
            T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
            P2, c = plan3_for_len(l2 - 1); T.ctl(c)
            T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
            if P2.a > BIGA: product_peak(T, P2)
            else: T.bump(P2.n)
            T.ctl(plan_invN_ops(P2))
            T.ops += 2 * (l2 - l)
            T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
            l = l2
    finally:
        CTX['cf'] = None; CTX['tcap'] = None
    T.free(L)                                                     # sY
    return sG, sM


TCAP_NEWTON = [None]                                              # set by main: 0.9 m (the temporaries of the Newton products)
def GSLOTS(m):
    """the array of g (stages A, B, C): n1 + 2 slots, so that the two pieces of R on O2 fit in its place when it is freed (proof.md 7)"""
    return -(-(m + 1) // VH) * VH + 2


VD = {}                                                           # description of the value-domain stage C (filled by powx_vd)


def powx_vd(m, b, E=PM1H):
    """stage C in the value domain.  Entry: g in coefficient form (m + 1 coefficients, the caller's array).  Exit: R = S^E mod g and g, both in coefficient
    form in arrays of n1 = K h elements (the caller's array of g is freed here).  Returns the trace."""
    T = Tr(b)
    K = -(-(m + 1) // VH); n1 = K * VH
    assert n1 >= m + 1
    Lx = pad23(2 * K - 1); Le = pad23(3 * K - 1)
    # the exponent: the leading bit, then the start monomial S^v with v = 2^(61 - VSHIFT) (all bits after the leading one down to there are zero)
    top = 255
    while top > 0 and not ebit(E, top):
        top -= 1; T.ctl(12)
    v = 1; bit = top
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1; T.ctl(25)
    for _ in range(VSHIFT):
        assert ebit(E, bit) == 0
        v >>= 1; bit += 1
    assert v & (v - 1) == 0 and v % VH == 0                       # v is a power of two and a multiple of h, so x^v = u_k^v on coset k
    steps = bit
    nset = sum(ebit(E, i) for i in range(bit))
    delta = v + n1 - m; ell = delta + 1                           # q = floor(X^v P1 / g) has degree delta
    Kq = -(-ell // VH); Lq = pad23(Kq + K - 1)
    # tables (per trial): u_k, 1/u_k, the base factors of the extensions, evaluations and interpolations, 1/M(n_k), u_k^v M(n_k), the running factors
    # (30 K elements); the kernel spectra (the extension kernel, used by both directions, the two chirps and the two kernels of the interpolation) and the
    # twiddle table of the outer transforms (Le elements); two group buffers
    NTAB = 30 * K
    sTab = T.new_fp(NTAB + Lx + 2 * Le + Lq + 2 * Lx)
    T.ctl(NTAB * (2 * (330 + INV_CTL) + 60))
    T.ctl(kernel_spectrum(Lx, 2 * K - 1) + kernel_spectrum(Le, 3 * K - 1) + kernel_spectrum(Lq, Kq + K - 1) + kernel_spectrum(Lx, 2 * K) + kernel_spectrum(Lx, K + 1))
    sB1 = T.new_fp(Le * VCNT); sB2 = T.new_fp(Le * VCNT)
    # the array of R on O1 is allocated now: it holds q (its first ell elements) from step 1 to step 3, then R~ on O1 (no hole is left, proof.md 7)
    sR1 = T.new_fp(n1)
    # (1) Barrett start: q = floor(X^v P1 / g) from the reciprocal of the reversed g modulo X^ell and the reversed top of X^v P1 (sparse: the coefficients
    # mu_i of M(Y), Y = X^h, at the degrees v + i h)
    sG, sM = newton_recip(T, ell)
    T.free(sG)                                                    # the reversed g
    sTt = T.new_fp(ell); T.st(ell); T.ctl(for8(ell)); T.ctl(Kq * (330 + INV_CTL + 30))
    CTX['cf'] = CF.get('newton'); CTX['tcap'] = TCAP_NEWTON[0]
    try:
        qp = conv_bilin_big(1, [ell], [dict(H=[ell], S=[ell], prod={(0, 0): (0, 1)})], 0)[0] + 6; Pq0 = dict(PL)
    finally:
        CTX['cf'] = None; CTX['tcap'] = None
    T.ctl(qp)                                                     # q into the first ell elements of the array R1
    for x in [T.new_fp(y) for y in Pq0['temps']]: T.free(x)
    T.free(sTt); T.free(sM)                                       # T_top, the reciprocal
    T.ld(ell); T.st(ell); T.loopc(ell // 2); T.ctl(2 * (ell // 2))  # reversal of q in place
    # (2) g on O1 and O2 from its coefficients: one chirp evaluation at the 2K nodes, the forward inner transforms
    # the arrays that leave stage C (g and R on O2, then in coefficient form) are two pieces each, cosets [0, Kc) and [Kc, K), Kc h >= the length of
    # the output c of the top apply_inv of stage D (proof.md 4.4): stage D frees the high pieces early
    k1 = (((m + 1) // 2) + 1) >> 1; Kc = -(-(m + 1 - k1) // VH); lo, hi = Kc * VH, (K - Kc) * VH
    sG1 = T.new_fp(n1); sG2 = (T.new_fp(lo), T.new_fp(hi))
    T.ctl(geo_eval(K, 2 * K, Le) + inner_all(2 * K, False))
    T.free(GSLOTS(m))                                             # the coefficients of g (the caller's array of n1 + 2 slots: proof.md 4.6, 7)
    # (3) R~_0 = X^v P1 mod g = X^v P1 - q g on O2: q (in R1) evaluated on O2 into the array of R on O2 (two pieces, in the place of g), then
    # R := u_k^v M(n_k) - q g pointwise
    sR2 = (T.new_fp(lo), T.new_fp(hi))
    T.ctl(geo_eval(Kq, K, Lq) + inner_all(K, False) + pw_cosets(K, 8))
    # (4) R~_0 on O1: inverse inner transforms on O2 into the array R1 (q is no longer needed), extension O2 -> O1, forward inner transforms
    ext = inner_all(K, True) + geo_ext(K, K, Lx) + inner_all(K, False)
    T.ctl(ext)
    # (5) -1/g on O1, in place (auxiliary array of h elements)
    sAux = T.new_fp(VH); T.ctl(batch_inv(K)); T.free(sAux)
    # (6) the squaring loop
    # per element: (i) 2 loads, 2 multiplications, a store = 8; (iii) 3 loads, the square, the product u0 g, the addition, the multiplication by 1/M(n_k),
    # a store = 12, and with b = 1 the load of omega^i, its multiplication by u_k and the multiplication by x = 16
    step0 = pw_cosets(K, 8) + ext + pw_cosets(K, 12) + ext + 20
    step1 = pw_cosets(K, 8) + ext + pw_cosets(K, 16) + ext + 20
    T.ctl((steps - nset) * step0 + nset * step1)
    # (7) leave the Montgomery form: u0 = -R~ / g on O1, extension O1 -> O2, R = (R~ + u0 g) / M(n_k) on O2
    T.ctl(pw_cosets(K, 7) + ext + pw_cosets(K, 11))               # 2 loads, a multiplication, a store; 3 loads, 2 multiplications, an addition, a store
    T.free(sR1); T.free(sG1)                                      # R on O1 (u0), -1/g on O1
    # (8) R and g back to coefficient form, in place: inverse inner transforms, interpolation at the K nodes of O2
    interp = inner_all(K, True) + geo_interp(K, Lx)
    T.ctl(2 * interp)
    T.free(sB1); T.free(sB2); T.free(sTab)
    T.ctl(2 + 500)
    VD.clear(); VD.update(K=K, n1=n1, Lx=Lx, Le=Le, Lq=Lq, Kq=Kq, v=v, ell=ell, steps=steps, nset=nset, step0=step0, step1=step1, ext=ext,
                         newton_q=qp, interp=interp)
    VD.update(cut=lo, hi=hi, R=sR2, G=sG2)
    return T, (lo, hi)                                            # the exit arrays: R and g, two pieces each


# ---------------------------------------------------------------- hgcd.c on shapes: the normal remainder sequence (every quotient of degree 1); any other quotient aborts the trial (proof.md 4.4)
ABORT_TEST = 2       # every division tests that its quotient has degree 1, and every return of hgcd that its degree count is the parameter k unless the remainder
                     # is zero (the normal case); otherwise the trial aborts (a comparison and a branch each)






















def dupv(ln, b):
    T = Tr(b); s = T.new_fp(ln if ln else 1)
    T.ld(ln); T.st(ln); T.loopc(ln)
    return T, s


def trim(it): return 11 * it           # trimlen: CTL(9 it) + LD(it)


def divrem_naive(lx, ly, term_zero=0):
    """cost of poly_divrem_naive for consecutive lengths (lx = ly + 1); returns (ops, lq, lr, iterations of the final trim)"""
    c = 3
    la, lb = lx, ly
    assert la == lb + 1
    if lb >= 2:
        c += powcost(PM2) + INV_CTL + 3 + 1
        c += 2 * 3 + 2 * 2 + 6
        c += (2 * (lb - 1) + 2 * max(lb - 2, 0))
        c += 4 * (lb - 1) + 2 * (lb - 1) + 3 * (lb - 1) + 2 + 4 + 2 * (lb - 1)
        it = 1 + term_zero * (lb - 1)
        c += trim(it)
        return c, 2, lb - 1 - term_zero * (lb - 1), it
    # general path, lb == 1 (la == 2)
    c += 2 * la + 2 * la + 3 * la + 2
    c += powcost(PM2) + INV_CTL
    c += (la - lb + 1) * (1 + 2 + 2 + 2 + 7) + (la - lb + 1) * 0
    c += trim(1)
    return c, la - lb + 1, 0, 1


def mat_identity(b):
    T = Tr(b); sl = [T.new_fp(1) for _ in range(4)]
    T.st(2)
    return T, [1, 0, 0, 1], sl


def mat_free(T, sl):
    for s in sl:
        if s: T.free(s)


def mul_add_q2(T, le, lf):
    lt = le + 1 if le else 0
    lo = max(lt, lf)
    s = T.new_fp(lo if lo else 1)
    muls = (le + max(le - 1, 0) + (1 if le > 0 else 0))
    adds = max(le - 1, 0) + (min(lf, le + 1) if le > 0 else 0)
    T.ops += muls + adds
    T.ld(le + lf); T.st(lo); T.loopc(lo); T.ctl(8 + 8 * lo)
    T.ctl(trim(1))
    return lo, s


def mat_mulQ(T, lens, sl):
    l0, s0 = mul_add_q2(T, lens[0], lens[1])
    l2, s2 = mul_add_q2(T, lens[2], lens[3])
    T.free(sl[1]); T.free(sl[3])
    return [l0, lens[0], l2, lens[2]], [s0, sl[0], s2, sl[2]]




def poly_mul_naive_cost(la, lb):
    return la * lb * 11 + (la * lb - (la + lb - 1)) + (la + lb - 1) * 11 + 2


def mat_mul(A, B, b):
    """A, B = (lens, slots); returns (Tr, lens, slots, consumed); consumed: the product has itself freed the arrays of A and B (block mode: each is freed as soon as it is transformed)"""
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
    N = Pl.N
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
    CTX['cf'] = CF.get('D')
    try:
        cb, eb = conv_bilin_big(4, Ls, groups); Pb = dict(PL)
    finally:
        CTX['cf'] = None
    BIG = Pl.a > BIGA
    if not BIG:
        cs, es = conv_bilin_cost(Pl, 4, Ls, groups)
        BIG = cb < cs + sum(Ls[k] * 8 + 2 for k in range(4) if es[k])
    if not BIG:
        tH0 = T.new_fp(Pl.n); tH1 = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        ob = [T.new_fp(N) for _ in range(4)]
        cc, eps = cs, es
    else:
        cc, eps = cb, eb
    T.ctl(cc)
    if BIG:
        # block mode: the four outputs (their own lengths) are allocated first, the arrays of A and B stay live for the whole product (every chunk reads them),
        # the temporary arrays of the product, then A and B are freed
        ob = [T.new_fp(Ls[k] if Ls[k] else 1) for k in range(4)]
        for x in [T.new_fp(y) for y in Pb['temps']]: T.free(x)
        for M_ in (A, B):
            for s_ in M_[1]:
                if s_: T.free(s_)
    else:
        T.free(tH0); T.free(tH1); T.free(tS)
    T.ctl(plan_invN_ops(Pl))
    for k in range(4):
        l = Ls[k]
        if BIG:                                               # the placement of the slots already wrote the scaled output
            T.ctl(3)
            if not eps[k]: T.st(l); T.loopc(l)
            outs[k] = ob[k]
            if l: T.ctl(trim(1))
            outl[k] = l
            continue
        o = T.new_fp(l if l else 1); T.ctl(3)
        if eps[k]:
            T.ops += l; T.ld(l); T.st(l); T.loopc(l)
        T.free(ob[k])
        outs[k] = o
        if l: T.ctl(trim(1))
        outl[k] = l
    return T, outl, outs, BIG


def apply_inv(Rl, Rs, h, la, lb, consume, b, own_in=(0, 0), sa=0, sb=0, win=0):
    """returns (Tr, lc, sc, ld, sd, reuse); reuse = (False, False, the window used).  The product is the single transform of section 4.4 or a block product
    (scheme (a) or (c) of 4.5), whichever has the smaller charge (a single transform exists only up to 3 * 2^32 points).  win: in block mode only the
    coefficients from win upward of c and d are formed (a node that wants its matrix only: proof.md 4.4); sc, sd are then the slots of the windows"""
    T = Tr(b)
    nres = la
    Pl, c = plan3_for_len(nres); T.ctl(c)
    N = Pl.N
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
    lc0 = la - h; ld0 = lc0 - 1
    CTX['ltrue'] = [lc0, ld0]; CTX['cf'] = CF.get('D')
    try:
        cb, eb = conv_bilin_big(2, [lc0 - win, ld0 - win], groups, win); Pb = dict(PL)
    finally:
        CTX['ltrue'] = None; CTX['cf'] = None
    BIG = Pl.a > BIGA
    if not BIG:
        cs, es = conv_bilin_cost(Pl, 2, [nres, nres], groups)
        small_extra = sum(8 * nres + 2 + (1 if es[k] < 0 else 0) for k in range(2) if es[k])
        BIG = cb + 2 * 3 < cs + small_extra
    if not BIG: win = 0
    reuse = (False, False, win)
    if BIG:
        sc_ = T.new_fp(lc0 - win); sd_ = T.new_fp(ld0 - win)
        cc, eps = cb, eb
        T.ctl(cc)
        for x in [T.new_fp(y) for y in Pb['temps']]: T.free(x)
        if consume:
            mat_free(T, Rs)
    else:
        tH = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        sc_ = T.new_fp(N); sd_ = T.new_fp(N)
        cc, eps = cs, es
        T.ctl(cc)
        T.free(tH); T.free(tS)
        if consume:
            mat_free(T, Rs)
    T.ctl(plan_invN_ops(Pl))
    for k in range(2):
        T.ctl(3)
        if not eps[k]:
            T.st(nres); T.loopc(nres); continue
        if BIG: continue                                      # the scale and the sign are applied by the placement (untwist) into the output
        if eps[k] < 0: T.ops += 1
        T.ops += nres; T.ld(nres); T.st(nres); T.loopc(nres)
    lc = la - h; ld = lc - 1
    T.ctl(trim(1) + trim(1) if BIG else trim(1 + (nres - lc)) + trim(1 + (nres - ld)))
    return T, lc, sc_, ld, sd_, reuse


COMPACT = dict(n=3, blocks=29, elements=22924228636997165691)   # compactions of stage D, measured by Appendix G.7 (alloc_sim.py), which asserts its counts are at most these


def compact_charge():
    """a compaction moves each live large block down: per element a load and a store with their addresses (4) and its share of the loop (1); per
    block 200 (its header, the loop, the handle); per compaction 20,000 (the search that fails, the walk over the blocks, the rewrite of the array
    pointers held in the stack frames: at most 64 frames of at most 40 pointers, 6 operations each, 15,360)"""
    return 5 * COMPACT['elements'] + 200 * COMPACT['blocks'] + 20000 * COMPACT['n']


KSCR = 1 << 44          # calls of hgcd with k < KSCR made from a call with k >= KSCR, and the driver iterations with k < KSCR, run in the scratch region (proof.md 4.4)
SCRMAX = [0]            # the bytes of all blocks allocated by one such call (its Tr.tot), the largest: the size of the scratch region


def scratch_return(T, kc, k, t, Rl):
    """a call that ran in the scratch region returns: its matrix is copied into the arena (per element a load and a store with their addresses, 20 for the loop),
    four arena allocations (each charged as at 1,000 live blocks: 121 + 13 * 2001 + 64), and the region is reset"""
    if kc < KSCR <= k:
        T.ctl(4 * sum(Rl) + 20 + 4 * (121 + 13 * 2001 + ALLOC_STAT))
        SCRMAX[0] = max(SCRMAX[0], t.tot)


@functools.lru_cache(maxsize=None)
def hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr=()):
    """returns (Tr, out) ; out = (lc, sc, ld, sd, Rl, Rs, h)"""
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
    t1, o1 = hgcd(las, 0, lbs, 0, k1, 1, 0, False, False, T.here())
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    scratch_return(T, k1, k, t1, R1l)
    T.ctl(ABORT_TEST)                                         # the returned degree count is k1 (normal sequence), else ABORT (proof.md 4.4)
    assert h1 >= 1, 'non-generic shape'
    w = 0
    if want_mat and not wc and not wd:
        lc_, ld_ = la - h1, la - h1 - 1; k3_ = k - h1 - 1; s3_ = (ld_ - 1) - 2 * k3_
        if s3_ > 0 and not (ld_ == 0 or (lc_ - ld_) > k - h1): w = s3_ - 1      # the second call reads d from s3 - 1 (through e) and c from s3
    t2, lcc, scc, ldd, sdd, reuse = apply_inv(R1l, R1s, h1, la, lb, not want_mat, T.here(), (own & 1, (own >> 1) & 1), sa, sb, w)
    T.add(t2); T.ctl(4)
    w = reuse[2]
    if w: T.ctl(2 * ABORT_TEST)                               # a windowed node: the leading coefficients of c and d at their normal degrees are nonzero, else ABORT
    for x in fr: T.free(x)                                    # the top node: the high pieces of g and R are no longer read (proof.md 4.4)
    if (own & 1) and not reuse[0]: T.free(sa)
    if (own & 2) and not reuse[1]: T.free(sb)
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
    sq = T.new_fp(dq + 1); srm = T.new_fp(lcc - w)
    T.ctl(3)                                                  # divrem_any
    dc, lq, lrem, _ = divrem_naive(lcc - w, ldd - w)
    lrem += w
    T.ctl(dc + ABORT_TEST)
    T.free(scc)
    k3 = k2 - dq
    s3 = (ldd - 1) - 2 * k3
    if s3 > 0:
        # lean: the second call runs on the top 2 k3 + 1 coefficients of (d, r) and returns its matrix R2; the full reduced pair is formed (R2^-1 applied
        # to the whole d and r) only when the caller wants it.  Without this the operands of a chain of t second calls grow to about 2^t k.
        t3, o3 = hgcd(ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here())
        T.add(t3)
        R2l, R2s, h3 = o3[4], o3[5], o3[6]
        scratch_return(T, k3, k, t3, R2l)
        T.ctl(ABORT_TEST)                                     # the returned degree count is k3 unless the remainder is zero, else ABORT
        lc3 = sc3 = ld3 = sd3 = None
        if wc or wd:
            t4, lc4, sc4, ld4, sd4, reuse = apply_inv(R2l, R2s, h3, ldd, lrem, not want_mat, T.here(), (1, 1), sdd, srm)
            T.add(t4); T.ctl(4)
            if not reuse[0]: T.free(sdd)
            if not reuse[1]: T.free(srm)
            if wc: lc3, sc3 = lc4, sc4
            else: T.free(sc4)
            if wd: ld3, sd3 = ld4, sd4
            else: T.free(sd4)
        else:
            T.free(sdd); T.free(srm)
            if not want_mat: mat_free(T, R2s)
        o3 = (lc3, sc3, ld3, sd3, R2l, R2s, h3)
    else:
        t3, o3 = hgcd(ldd, sdd, lrem, srm, k3, want_mat, 3, wc, wd, T.here())
        T.add(t3); T.ctl(ABORT_TEST)
    h = h1 + dq + o3[6]
    if want_mat:
        R1l2, R1s2 = mat_mulQ(T, R1l, R1s)
        tm, Ml, Ms, cons = mat_mul((R1l2, R1s2), (o3[4], o3[5]), T.here()); T.add(tm)
        if not cons:
            mat_free(T, o3[5]); mat_free(T, R1s2)
        Rl, Rs = Ml, Ms
    T.free(sq)
    return T, (o3[0], o3[1], o3[2], o3[3], Rl, Rs, h)


def apply_inv_split(Rl, Rs, h, cut, outl, b, dcut=None, lowp=None):
    """apply_inv on the low pieces a' = a mod X^cut, b' = b mod X^cut (cut >= the output length la - h): c = s (r22 a' - r12 b') mod X^(la - h) is formed
    first (window [0, lc) of a product of true length cut + len(r) - 1, exact without the cancellation), r22 and r12 are freed, then d = s (r11 b' - r21 a'),
    then r11, r21 and the low pieces are freed.  dcut: d is written into two pieces [0, dcut) and [dcut, ld)."""
    T = Tr(b); T.ctl(60)
    out = []
    sgn = -1 if (h & 1) else 1
    for o, (e1, e2, sg) in enumerate(((3, 1, sgn), (0, 2, sgn))):    # c: r22 a - r12 b ; d: r11 b - r21 a
        lo = outl[o]
        if o == 1 and dcut:
            hnd = (T.new_fp(dcut), T.new_fp(lo - dcut))
        else:
            hnd = T.new_fp(lo)
        groups = [dict(H=[cut], S=[Rl[e1]], prod={(0, 0): (0, sg)}), dict(H=[cut], S=[Rl[e2]], prod={(0, 0): (0, -sg)})]
        CTX['cf'] = CF.get('Dtop', CF.get('D'))
        try:
            cc, eps = conv_bilin_big(1, [lo], groups, 0)
        finally:
            CTX['cf'] = None
        T.ctl(cc + 10); P_ = dict(PL)
        for x in [T.new_fp(y) for y in P_['temps']]: T.free(x)
        T.free(Rs[e1]); T.free(Rs[e2])
        out.append(hnd)
    for x in lowp: T.free(x)
    T.ctl(plan_invN_ops(P32) + 2 * 3 + trim(1) + trim(1))
    return T, out


def hgcd_top(la, lb, k, cut, b):
    """the first call of poly_gcd_own (pair wanted, matrix not wanted) with g and R held as two pieces each, [0, cut) and [cut, l): the first recursive
    call frees the high pieces after its apply_inv, the top apply_inv runs on the low pieces (apply_inv_split); otherwise the body of hgcd"""
    T = Tr(b); T.ctl(40)
    n = la - 1
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    t1, o1 = hgcd(la - s, 0, lb - s, 0, k1, 1, 0, False, False, T.here(), TOPHIGH[0])
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    T.ctl(ABORT_TEST)
    lcc = la - h1; ldd = lcc - 1
    assert cut >= lcc and h1 == k1
    k3 = k - h1 - 1; cut2 = ldd - k3                              # the second call returns k3 quotients (normal sequence); c', d' have ldd - k3, ldd - k3 - 1
    t2, (scc, sdd) = apply_inv_split(R1l, R1s, h1, cut, (lcc, ldd), T.here(), cut2, TOPLOW[0])
    T.add(t2); T.ctl(4)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    assert not (ldd == 0 or (lcc - ldd) > k2)
    dq = lcc - ldd
    sq = T.new_fp(dq + 1); srm = (T.new_fp(cut2), T.new_fp(lcc - cut2))   # the remainder e in two pieces
    T.ctl(3)
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)
    T.ctl(dc + ABORT_TEST)
    T.free(scc)
    assert k3 == k2 - dq
    s3 = (ldd - 1) - 2 * k3
    assert s3 > 0
    t3, o3 = hgcd(ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here(), (sdd[1], srm[1]))
    T.add(t3)
    R2l, R2s, h3 = o3[4], o3[5], o3[6]
    T.ctl(ABORT_TEST)
    assert h3 == k3
    lc4 = ldd - h3; ld4 = lc4 - 1
    t4, (sc4, sd4) = apply_inv_split(R2l, R2s, h3, cut2, (lc4, ld4), T.here(), None, (sdd[0], srm[0]))
    T.add(t4); T.ctl(4)
    T.free(sq)
    return T, (lc4, sc4, ld4, sd4, None, None, h1 + dq + h3)


def hgcd_base(la, sa, lb, sb, k, want_mat, own, wc, wd, T):
    """the base case in place (proof.md 4.4): the two remainders are two arrays (the owned inputs or copies); a division step writes the new remainder
    r_(i+1) = r_(i-1) - q r_i over the array of r_(i-1) (output index j reads only index j and j - 1 of r_i, and index j of r_(i-1)) and the roles swap;
    the quotient's two coefficients stay in registers; the matrix entries are four arrays of k + 2 elements allocated once, R := R Q writes
    r11 q + r12 over r12 (index j reads r11 at j and j - 1, r12 at j) and the column labels swap.  The charges of the division and of R Q are those of
    poly_divrem_naive and mul_add_q2; no array is allocated or freed inside the loop."""
    if own & 1: sx = sa
    else:
        t, sx = dupv(la, T.here()); T.add(t)
    if own & 2: sy = sb
    else:
        t, sy = dupv(lb, T.here()); T.add(t)
    lx, ly, ssum = la, lb, 0
    Rl = Rs = None
    if want_mat:
        Rs = [T.new_fp(k + 2) for _ in range(4)]; T.st(2); T.ctl(8)
        Rl = [1, 0, 0, 1]
    while ly > 0:
        dq = lx - ly
        T.ctl(6)
        if dq > k - ssum: break
        dc, lq, lr, _ = divrem_naive(lx, ly)
        T.ctl(dc + ABORT_TEST + 4)                            # + the swap of the two array addresses
        if want_mat:
            for e, f in ((0, 1), (2, 3)):
                le, lf = Rl[e], Rl[f]
                lt = le + 1 if le else 0; lo = max(lt, lf)
                muls = (le + max(le - 1, 0) + (1 if le > 0 else 0)); adds = max(le - 1, 0) + (min(lf, le + 1) if le > 0 else 0)
                T.ops += muls + adds
                T.ld(le + lf); T.st(lo); T.loopc(lo); T.ctl(8 + 8 * lo); T.ctl(trim(1))
                Rl[e], Rl[f] = lo, le
                Rs[e], Rs[f] = Rs[f], Rs[e]
            T.ctl(4)
        ssum += dq
        lx, ly = ly, lr
        sx, sy = sy, sx
    lc = sc = ld = sd = None
    if wc: lc, sc = lx, sx
    else: T.free(sx)
    if wd: ld, sd = ly, sy
    else: T.free(sy)
    return T, (lc, sc, ld, sd, Rl, Rs, ssum)


TOPCUT = [0]; TOPHI = [0]; TOPLOW = [None]; TOPHIGH = [None]                  # the two pieces of g and of R at the entry of stage D (set by main from stage C)


def gcd_cost(m, dG, b, slots):
    """poly_gcd_own(g (m+1 coefficients), R-1 (m coefficients)), normal Euclid, gcd degree dG.  Returns (Tr, (lg, sg)).  slots: the sizes of the arrays of g and R."""
    T = Tr(b)
    lx, ly = m + 1, m
    sx, sy = slots                                             # slots of the arrays of g and of R
    tail0 = None
    T.ctl(3); T.ctl(3)
    while ly > 0:
        T.ctl(2)
        n = lx - 1
        T.ctl(4)
        if n <= 2 * 96:
            sq = T.new_fp(lx - ly + 1); sr = T.new_fp(lx)
            last = (ly == dG + 1)
            dc, lq, lr, _ = divrem_naive(lx, ly, term_zero=1 if (last and dG >= 1) else 0)
            if last and dG == 0:
                lr = 0
            T.ctl(dc + ABORT_TEST)
            T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
            T.free(sq); T.ctl(5)
            continue
        k = (n + 1) // 2
        if k < KSCR and tail0 is None: tail0 = T.tot                 # the rest of the driver runs in the scratch region
        if TOPCUT[0] and lx == m + 1:
            t, o = hgcd_top(lx, ly, k, TOPCUT[0], T.here())
        else:
            t, o = hgcd(lx, sx, ly, sy, k, False, 3, True, True, T.here())
        T.add(t)
        lc, sc, ld, sd = o[0], o[1], o[2], o[3]
        T.ctl(ABORT_TEST)                                     # the returned degree count is k unless the remainder is zero, else ABORT
        T.ctl(2)
        sq = T.new_fp(lc - ld + 1); sr = T.new_fp(lc)
        T.ctl(3)
        dc, lq, lr, _ = divrem_naive(lc, ld)
        T.ctl(dc + ABORT_TEST)
        T.free(sc); T.free(sq)
        sx = sd; lx = ld; sy = sr; ly = lr; T.ctl(5)
    T.free(sy)
    if tail0 is not None: SCRMAX[0] = max(SCRMAX[0], T.tot - tail0); T.ctl(40)   # the gcd copied out of the scratch region
    T.ctl(2)
    T.ops += powcost(PM2); T.ctl(INV_CTL); T.ld(1)
    T.ops += lx - 1
    T.ld(lx); T.st(lx); T.loopc(lx)
    return T, (lx, sx)


IMAGE_EXTRA = 399216 + 32 + 4851196        # text + data + static bss besides the arena (proof section 7)
STACK = 65536


def ceil3(x): return math.ceil(x * 1000) / 1000


def twiddle_slots(m):
    a = 2
    while 3 * (1 << a) < 2 * m - 1: a += 1
    return (1 << min(a, BIGA)) // 2                           # init_stage: the table of nmax/2 elements, nmax = 2^min(a, 32)


def stage_AB_peaks(m, twb, g_b):
    """stage A holds the table and g; stage B (build_g) the table, g and the block array of H = ncos * 3 * 2^31 elements, then F"""
    assert m + 1 > (1 << BIGA)                                # block mode of stage B (the three cosets): no transform of 2^a >= m + 1 points exists
    Pl = make_plan(3, BIGA - 1)[0]; ncos = -(-(m + 1) // Pl.N); H = ncos * Pl.N
    return twb + g_b, twb + g_b + max(blk(H), blk(m + 1))


# the rows of proof.md section 6 that this ledger does not expand (the same as in the base entry f62fb39, commit a031a50), at r = 21, plus PLAN_EXTRA:
# a second allowance for the plan_invN misses (the plans of this entry differ from the base entry's; 95,759 covers 31 sizes, the two allowances 62)
ROWS21 = dict(fixed=[17179887292, 4910, 95759, 5644, 3384436], A=1196, B=14724903587095649952616, E=166079773, F=47012, G=14172, trial=12, offline=1000000)
PLAN_EXTRA = 95759
STAT_EXTRA = 64 * 10 ** 10      # per trial: the statistics charge (64) of at most 10^10 allocator calls in the rows A, B, E, F, G that this ledger does not expand
CF_FRAC = dict(newton=0.25, D=0.06)   # chunk bounds of the block products, as fractions of m (proof.md 4.5)


def main(verbose=True):
    assert check_outer()
    r = 21
    m = (5 ** (6 + r) - 1) // 2
    CF.clear(); CF.update({k: int(v * m) for k, v in CF_FRAC.items()}); TCAP_NEWTON[0] = int(0.9 * m)
    hgcd.cache_clear()
    C, (sR, sGc) = powx_vd(m, 3); C.ctl(STAGE_BK)
    D = Tr(3); D.ctl(STAGE_BK); D.ops += 1; D.ctl(11)
    lo, hi = sR, sGc
    TOPCUT[0] = lo; TOPHI[0] = hi
    TOPLOW[0] = (VD['G'][0], VD['R'][0]); TOPHIGH[0] = (VD['G'][1], VD['R'][1])   # the pieces of g and R (handles of their arrays)
    SCRMAX[0] = 0
    t, (lg, sg) = gcd_cost(m, 0, 3, (lo + hi, lo + hi))
    D.add(t); D.ctl(2); D.free(sg)
    scr = -(-SCRMAX[0] // 32)                                  # the scratch region, one block allocated at the start of stage D and freed at its end
    D.ctl(2 * (121 + 13 * 9 + ALLOC_STAT) + FREE_OPS); D.peak += blk(scr)
    D.ctl(compact_charge())                                    # the compactions of the arena (proof.md 4.2, 7; counted by Appendix G.7)
    tws = twiddle_slots(m); twb = blk(tws); g_b = blk(GSLOTS(m))  # the array of g has n1 + 2 slots (proof.md 7)
    pA, pB = stage_AB_peaks(m, twb, g_b)
    pC = twb + g_b + C.peak; pD = twb + 2 * (blk(lo) + blk(hi)) + D.peak
    peaks = dict(A=pA, B=pB, C=pC, D=pD)
    arena = (max(peaks.values()) + 63) & ~63
    mem = arena + IMAGE_EXTRA + STACK
    R = ROWS21; K, Cr = 2, 216 + 21 * r
    trial = [R['A'], R['B'], C.ops, D.ops, R['E'], R['F'], R['G'], R['trial'], STAT_EXTRA]
    N = sum(R['fixed']) + PLAN_EXTRA + K * sum(trial) + R['offline']
    tl = math.ceil(math.log2(N / Cr) * 100000 - 1e-6) / 100000
    if verbose:
        print('stage C (value domain):', {k: (format(v, ',') if isinstance(v, int) else v) for k, v in VD.items()})
        print('per step (bit 0) per element of n1: %.1f' % (VD['step0'] / VD['n1']))
        print('S_C =', format(C.ops, ','), '%.4e' % C.ops)
        print('S_D =', format(D.ops, ','), '%.4e' % D.ops, '| scratch region of stage D: %s bytes (%.5f copies)' % (format(blk(scr), ','), blk(scr) / (32 * m)))
        for x in 'ABCD': print('peak of the live set, stage %s = %s bytes (%.4f copies of m elements)' % (x, format(peaks[x], ','), peaks[x] / (32 * m)))
        print('arena = %s bytes, memory = %s bytes, log2 = %.5f, claimed %.3f' % (format(arena, ','), format(mem, ','), math.log2(mem), ceil3(math.log2(mem))))
        print('trial =', format(sum(trial), ','), '%.4e' % sum(trial))
        print('N_max = %s operations, log2(N_max / %d) = %.10f, time_log2 = %.5f' % (format(N, ','), Cr, math.log2(N / Cr), tl))
        print('normalized cost = %.5f + (%.3f - 20) = %.5f' % (tl, ceil3(math.log2(mem)), tl + ceil3(math.log2(mem)) - 20))
    assert C.ops == 1077028960067639720672037 and D.ops == 1062106645154198605714641
    assert peaks == dict(A=119209289621094531264, B=238418579242189062400, C=476837370801235048512, D=455265475194479467904)
    assert arena == 476837370801235048512 and mem == 476837370801240364492 and ceil3(math.log2(mem)) == 68.693
    assert N == 4307721017619165469436718 and tl == 72.47345
    return dict(C=C.ops, D=D.ops, peaks=peaks, arena=arena, mem=mem, N=N, tl=tl, score=tl + ceil3(math.log2(mem)) - 20)


if __name__ == '__main__':
    main()
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


## 14. Appendix G: block products, the outer scheme and the coset solve at small sizes

G.1 is the base entry's check (`bigmul_check.py`) of its block products and of the coset solve of section 3; scheme (a) and the coset solve are used here unchanged, its scheme (b) and persistent forms are not used by this entry. G.2 to G.7 are the checks of scheme (c), of the truncated half-gcd, of stage C in the value domain, of the shapes of the half-gcd, of the charges of scheme (c) and of the placement of the arrays in the arena (standard library only; each asserts and prints ok).

The programs of proof.md 4.5 and 3 at block length 12 and transform size 24 over the Pallas field, against schoolbook products: one product with several windows, the square, the subtraction into an array, the bilinear form of `apply_inv` with a short exact result (also with entries of three blocks and operands of five), the 2 x 2 matrix product with multi-block entries, the outer-transform scheme (outer length, inner transforms, fold, wrap rule), the streamed schedule of 4.5 (three squaring steps of stage C with the persistent forms of `MU` and `g` made once, in scheme (a) and in scheme (b), against the remainder of the square modulo `g`; `apply_inv` with a sliding window of `kR + 1` block spectra of each of `a` and `b` and the outputs written over `a` and `b`, which asserts that no block of an input is overwritten before it is transformed and that each block is transformed once; the matrix product by rows), the interpolation by `kappa = 3` cosets with the Vandermonde recombination, and the geometric-node solve of section 3 (q-binomial coefficients of `M`, the closed form of `M'`, the two correlations) at `kappa = 7`. It also checks that the nodes `u_k^B` for `v_k = 1, 2, 3` and `B = 3 * 2^31` are pairwise distinct, that the odd cofactor of `2^32 * 3 * 463` in `p - 1` has no divisor from 3 to `6 * 10^8` (by trial division), and that `z = 4^B` has no power `z^d = 1` for the divisors `d` of `p - 1` up to `6 * 10^8`. Run: `python3 bigmul_check.py`.

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
    ZB = 6 * 10 ** 8
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

### G.2 chunk_check.py

Scheme (c) of 4.5 at block length 4 over the Pallas field: chunked bilinear products of two signed terms modulo `X^(n2 HB) - 1` with `n2` of 6, 8 and 12 points and `nc` from 1 to 4, for the whole result and a window, against schoolbook products reduced modulo `X^(n2 HB) - 1`. Run: `python3 chunk_check.py`.

```python
#!/usr/bin/env python3
"""Small-size check of the chunked outer block product over the Pallas field.

A polynomial of l coefficients is cut into blocks of HB coefficients (variable Y = X^HB).
The product is formed at the n2 outer points Y = w^o, o < n2, processed in nc chunks of
residue classes o = j (mod nc): chunk j twists and folds each operand into n2/nc blocks,
transforms them across blocks, multiplies at each outer point with an inner product of length
2*HB, folds the inner product modulo X^HB - w^o, inverse transforms across blocks and adds the
untwisted chunk into the output window.  The result is the product modulo Y^n2 - 1."""
import random

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
GEN = 5


def root(n):
    assert (P - 1) % n == 0
    w = pow(GEN, (P - 1) // n, P)
    assert pow(w, n, P) == 1 and all(pow(w, n // q, P) != 1 for q in (2, 3) if n % q == 0)
    return w


def dft(v, w):
    n = len(v)
    return [sum(v[i] * pow(w, i * k, P) for i in range(n)) % P for k in range(n)]


def schoolbook(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % P
    return out


def inner_mul(x, y, HB):
    """product of two block polynomials of < HB coefficients via a length-2HB transform"""
    NB = 2 * HB; z = root(NB)
    X = dft(x + [0] * (NB - len(x)), z); Yv = dft(y + [0] * (NB - len(y)), z)
    inv = pow(NB, P - 2, P)
    return [c * inv % P for c in dft([u * v % P for u, v in zip(X, Yv)], pow(z, P - 2, P))]


def blocks(a, HB):
    k = -(-len(a) // HB)
    return [a[i * HB:(i + 1) * HB] + [0] * (HB - len(a[i * HB:(i + 1) * HB])) for i in range(k)]


def chunked_product(terms, n2, nc, HB, ws, outlen):
    """sum over (sign, a, b) in terms of sign * a * b, modulo X^(n2 HB) - 1, window [ws, ws + outlen)"""
    assert n2 % nc == 0
    w = root(n2); n3 = n2 // nc; w3 = pow(w, nc, P); w3i = pow(w3, P - 2, P)
    out = [0] * outlen
    inv_n2 = pow(n2, P - 2, P)
    for j in range(nc):
        def outer(a):
            bl = blocks(a, HB); y = [[0] * HB for _ in range(n3)]
            for i, blk in enumerate(bl):
                t = pow(w, j * i, P)
                for c in range(HB): y[i % n3][c] = (y[i % n3][c] + t * blk[c]) % P
            cols = [dft([y[u][c] for u in range(n3)], w3) for c in range(HB)]
            return [[cols[c][u] for c in range(HB)] for u in range(n3)]
        acc = [[0] * HB for _ in range(n3)]
        for sg, a, b in terms:
            A, B = outer(a), outer(b)
            for u in range(n3):
                o = j + nc * u; wo = pow(w, o, P)
                prod = inner_mul(A[u], B[u], HB)
                folded = [(prod[c] + wo * prod[c + HB]) % P for c in range(HB)]
                acc[u] = [(acc[u][c] + sg * folded[c]) % P for c in range(HB)]
        z = [dft([acc[u][c] for u in range(n3)], w3i) for c in range(HB)]
        for idx in range(outlen):
            pos = ws + idx; s, c = divmod(pos, HB); s %= n2
            out[idx] = (out[idx] + pow(w, (P - 1 - (j * s) % (P - 1)) % (P - 1), P) * z[c][s % n3] * inv_n2) % P
    return out


def cyclic_ref(full, period, ws, outlen):
    red = [0] * period
    for i, c in enumerate(full): red[i % period] = (red[i % period] + c) % P
    return [red[(ws + i) % period] for i in range(outlen)]


def rnd(n): return [random.randrange(P) for _ in range(n)]


def check_products():
    random.seed(7); HB = 4
    for (la, lb, n2, nc) in ((9, 7, 8, 2), (13, 13, 8, 4), (11, 6, 6, 3), (16, 9, 12, 4), (10, 10, 8, 1)):
        a, b, c, d = rnd(la), rnd(lb), rnd(la), rnd(lb)
        full = [(x - y) % P for x, y in zip(schoolbook(a, b), schoolbook(c, d))]
        period = n2 * HB
        for ws, ol in ((0, min(period, len(full))), (3, 5)):
            got = chunked_product([(1, a, b), (P - 1, c, d)], n2, nc, HB, ws, ol)
            assert got == cyclic_ref(full, period, ws, ol), (la, lb, n2, nc, ws)
    print('chunked bilinear products: ok')


if __name__ == '__main__':
    check_products()
```

### G.3 hgcd_trunc_check.py

The half-gcd of 4.4 with plain arithmetic over the Pallas field (base case `k <= 4`), in both forms (second call truncated, and not truncated as in the base entry), on 60 random pairs of degrees `n` and `n - 1` (`n` from 8 to 139) with `k = ceil(n/2)` or random `k`, against the plain Euclidean algorithm stopped at the same degree sum: the matrix, the degree count and the reduced pair agree (lemma 4.4). It prints the largest ratio of an operand length to `2k + 1` over the calls: 1.00 truncated, up to 20 not truncated. Run: `python3 hgcd_trunc_check.py`.

```python
#!/usr/bin/env python3
"""Appendix G.3: small-size check of the half-gcd of proof.md 4.4 with a truncated second call, over the Pallas field.

Polynomials are coefficient lists, low degree first, no trailing zeros.  hgcd(a, b, k) follows the shape of hgcd in the
ledger: the first call on the top 2 k1 + 1 coefficients, R1^-1 applied to (a, b), one division, the second call (on the top
2 k3 + 1 coefficients when trunc, else on the whole pair), R = R1 Q R2.  Both variants must return the same matrix and
degree count as the plain Euclidean algorithm stopped at the same point, and the truncated variant keeps la <= 2 k + 1."""
import random

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
BASE = 4


def trim(a):
    while a and a[-1] == 0: a.pop()
    return a


def add(a, b):
    out = [0] * max(len(a), len(b))
    for i, x in enumerate(a): out[i] = x
    for i, x in enumerate(b): out[i] = (out[i] + x) % P
    return trim(out)


def neg(a): return [(-x) % P for x in a]


def mul(a, b):
    if not a or not b: return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): out[i + j] = (out[i + j] + x * y) % P
    return trim(out)


def divrem(a, b):
    a = a[:]; q = [0] * max(0, len(a) - len(b) + 1); inv = pow(b[-1], P - 2, P)
    while len(a) >= len(b) and a:
        c = a[-1] * inv % P; s = len(a) - len(b); q[s] = c
        for i, y in enumerate(b): a[i + s] = (a[i + s] - c * y) % P
        trim(a)
    return trim(q), a


def top(a, s): return a[s:] if s > 0 else a[:]


def ident(): return [[[1], []], [[], [1]]]


def mmul(A, B):
    return [[add(mul(A[i][0], B[0][j]), mul(A[i][1], B[1][j])) for j in range(2)] for i in range(2)]


def apply_inv(R, a, b):
    """(c, d) = R^-1 (a, b) with det R = +-1: R^-1 = det * [[R11, -R01], [-R10, R00]]"""
    det = add(mul(R[0][0], R[1][1]), neg(mul(R[0][1], R[1][0])))
    assert len(det) == 1 and det[0] in (1, P - 1)
    sg = det[0]
    c = [x * sg % P for x in add(mul(R[1][1], a), neg(mul(R[0][1], b)))]
    d = [x * sg % P for x in add(mul(R[0][0], b), neg(mul(R[1][0], a)))]
    return trim(c), trim(d)


MAXRATIO = [0.0]


def hgcd(a, b, k, trunc):
    """returns (R, h, c, d): (a, b) = R (c, d), h = deg a - deg c, h <= k, the pair reduced as far as k allows"""
    n = len(a) - 1
    if k > 0: MAXRATIO[0] = max(MAXRATIO[0], len(a) / (2 * k + 1))
    if not b or n - (len(b) - 1) > k: return ident(), 0, a, b
    if k <= BASE:
        R = ident(); c, d = a, b; h = 0
        while d and (len(c) - len(d)) <= k - h:
            q, r = divrem(c, d); h += len(c) - len(d)
            R = mmul(R, [[q, [1]], [[1], []]]); c, d = d, r
        return R, h, c, d
    k1 = (k + 1) >> 1
    if 2 * k1 > n: k1 = n >> 1
    s = n - 2 * k1
    R1, h1, _, _ = hgcd(top(a, s), top(b, s), k1, trunc)
    c, d = apply_inv(R1, a, b)
    k2 = k - (n - (len(c) - 1))
    if not d or (len(c) - len(d)) > k2: return R1, h1, c, d
    q, r = divrem(c, d); dq = len(c) - len(d)
    k3 = k2 - dq
    s3 = (len(d) - 1) - 2 * k3
    if trunc and s3 > 0:
        R2, h3, _, _ = hgcd(top(d, s3), top(r, s3), k3, trunc)
        e, f = apply_inv(R2, d, r)
    else:
        R2, h3, e, f = hgcd(d, r, k3, trunc)
    R = mmul(mmul(R1, [[q, [1]], [[1], []]]), R2)
    return R, h1 + dq + h3, e, f


def euclid_stop(a, b, k):
    """plain Euclid: every quotient taken while the degrees removed stay <= k"""
    R = ident(); c, d = a, b; h = 0
    while d and (len(c) - len(d)) <= k - h:
        q, r = divrem(c, d); h += len(c) - len(d)
        R = mmul(R, [[q, [1]], [[1], []]]); c, d = d, r
    return R, h, c, d


def main():
    rnd = random.Random(7)
    for trial in range(60):
        n = rnd.randrange(8, 140)
        a = [rnd.randrange(P) for _ in range(n)] + [rnd.randrange(1, P)]
        b = [rnd.randrange(P) for _ in range(n - 1)] + [rnd.randrange(1, P)]
        k = rnd.randrange(1, n // 2 + 2) if trial % 2 else (n + 1) // 2
        ref = euclid_stop(a, b, k)
        for trunc in (False, True):
            MAXRATIO[0] = 0.0
            got = hgcd(a, b, k, trunc)
            assert got[0] == ref[0] and got[1] == ref[1] and got[2] == ref[2] and got[3] == ref[3], (trial, trunc, n, k)
            if trunc: tr = MAXRATIO[0]
            else: un = MAXRATIO[0]
        if trial % 10 == 0: print('n %3d k %3d  max len/(2k+1): untruncated %.2f truncated %.2f' % (n, k, un, tr))
    print('ok')


if __name__ == '__main__':
    main()
```

### G.4 vd_check.py

Stage C in the value domain (4.6) at `h = 4, 8, 16` and `m = 25, 37, 40, 70` over the Pallas field, with real arithmetic and the outer kernels of Appendix E: the chirp evaluation of `g` on `O1` and `O2`, the Barrett start (Newton reciprocal, checked against long division), `R~_0` on `O2` and its extension to `O1`, the loop over the exponent bits (both extensions, `x^b` on `O2`), the exit from the Montgomery form and the interpolation of `R` and `g` to coefficient form, against `S^E mod g` and `g`; after every step `R~` is interpolated and `deg R~ <= m`, `R~ = S^e P1 (mod g)` are asserted (lemmas 4.6, 4.7). The geometric phases of an extension (both directions), of the evaluation and of the interpolation are executed with counted charges (the rules of 4.2) and the counts are asserted equal to the closed forms `geo_ext`, `geo_eval` and `geo_interp` of Appendix E. Run: `python3 vd_check.py` (with `stage_cd.py` in the same folder; a few seconds).

```python
#!/usr/bin/env python3
"""Appendix G.4: stage C in the value domain (proof.md 4.6) at small sizes over the Pallas field (standard library only).
Runs the algorithm of 4.6 with real arithmetic: g evaluated on O1 and O2 by the chirp evaluation, the Barrett start R~_0 = X^v P1 mod g on O2, the
extensions O2 -> O1 and O1 -> O2 by the convolution with the kernel 1/(z^t - 1) (outer transforms executed by the kernels of Appendix E), the squaring
loop (exponent bits, x^b on O2), the exit from the Montgomery form and the interpolation of R and g back to coefficient form, and compares with
X^E mod g and g computed directly.  It also checks the invariant R~_i = X^(e_i) P1 (mod g), deg R~_i <= m after every step, and runs the geometric
phases with counted charges (KCOUNT, the rules of 4.2) against the closed forms geo_ext, geo_eval and geo_interp of Appendix E.
usage: python3 vd_check.py  (stage_cd.py in the same folder)"""
import importlib.util, os, random, sys
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('E', os.path.join(here, 'stage_cd.py'))
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)
P = E.P
inv = lambda x: pow(x, P - 2, P)
LD, ST, MUL, ADD, SUB, CTL, LOOP, KC = E.LD, E.ST, E.MUL, E.ADD, E.SUB, E.CTL, E.LOOP, E.KCOUNT


def pmul(f, g):
    r = [0] * (len(f) + len(g) - 1)
    for i, x in enumerate(f):
        if x:
            for j, y in enumerate(g): r[i + j] = (r[i + j] + x * y) % P
    return r


def pdivmod(f, g):
    f = f[:]; q = [0] * max(1, len(f) - len(g) + 1); li = inv(g[-1])
    while len(f) >= len(g):
        c = f[-1] * li % P; s = len(f) - len(g); q[s] = c
        for i, y in enumerate(g): f[s + i] = (f[s + i] - c * y) % P
        f.pop()
    while f and f[-1] == 0: f.pop()
    return q, f


def ev(f, x):
    r = 0
    for c in reversed(f): r = (r * x + c) % P
    return r


def trim(f):
    f = list(f)
    while f and f[-1] == 0: f.pop()
    return f


def C2(n): return n * (n - 1) // 2


def for8_loop(n, body):
    """an eight-element loop charged as for8(n) (section 4.2), body(i) executes the element"""
    CTL(1)
    for blk in range(n // 8):
        CTL(3)
        for i in range(8): body(8 * blk + i)
    CTL(2)
    for i in range(8 * (n // 8), n):
        CTL(3); body(i)
    CTL(2)


class VD:
    def __init__(self, h, m, cnt):
        self.h, self.m, self.cnt = h, m, cnt
        self.w = pow(5, (P - 1) // h, P)                              # primitive h-th root (5 is a primitive root of F_p)
        self.K = -(-(m + 1) // h); self.n1 = self.K * h
        K = self.K
        self.u = [pow(5, k, P) for k in range(2 * K)]; self.z = pow(5, h, P)
        assert all(pow(self.u[k], h, P) == pow(self.z, k, P) for k in range(2 * K))
        assert len({pow(self.z, k, P) for k in range(2 * K)}) == 2 * K
        self.Lx = E.pad23(2 * K - 1); self.Le = E.pad23(3 * K - 1)
        z = self.z
        self.M1 = [1]
        for k in range(K): self.M1 = pmul(self.M1, [(-pow(z, k, P)) % P, 1])
        self.M2 = [1]
        for k in range(K): self.M2 = pmul(self.M2, [(-pow(z, K + k, P)) % P, 1])
        d1 = [sum(i * c * pow(z, k * (i - 1), P) for i, c in enumerate(self.M1) if i) % P for k in range(K)]          # M1'(z^k)
        d2 = [sum(i * c * pow(z, (K + k) * (i - 1), P) for i, c in enumerate(self.M2) if i) % P for k in range(K)]   # M2'(z^(K+k))
        self.kap = [0] + [inv((pow(z, t, P) - 1) % P) for t in range(1, 2 * K)]
        # scale factors of the extensions (base factor of coset k at position 0, step 1/u_k or u_k along the positions)
        self.s12 = [pow(z, (P - 1 - k) % (P - 1), P) * inv(d1[k]) * inv(h) % P for k in range(K)]       # in: z^-k / M1'(z^k) / h
        self.o12 = [ev(self.M1, pow(z, K + k, P)) for k in range(K)]                                    # out: M1(z^(K+k))
        self.s21 = [inv(d2[k]) * inv(h) % P for k in range(K)]                                          # in: 1 / M2'(z^(K+k)) / h
        self.o21 = [(-ev(self.M2, pow(z, k, P)) * inv(pow(z, k, P))) % P for k in range(K)]           # out: -M2(z^k) z^-k
        self.invM = [inv(ev(self.M1, pow(z, K + k, P))) for k in range(K)]                            # 1 / P1 on coset K + k

    # ---- the inner transform of a coset (values <-> residue coefficients times u_k^j), plain DFT at this size
    def vals(self, res_tw):
        h, w = self.h, self.w
        return [sum(res_tw[j] * pow(w, i * j, P) for j in range(h)) % P for i in range(h)]

    def ivals(self, v):                                                # returns h * (u_k^j r_j)
        h, w = self.h, self.w
        return [sum(v[i] * pow(w, (-i * j) % h, P) for i in range(h)) % P for j in range(h)]

    def point(self, k, i): return self.u[k] * pow(self.w, i, P) % P

    # ---- the geometric phase on one group of positions, executed with counted charges (rows of cnt elements in a buffer of L rows)
    def conv_group(self, B, L, kin, spec):
        cnt = self.cnt
        for r in LOOP(L - kin):                                        # rows_zero
            CTL(10); for8_loop(cnt, lambda i, r=r: ST(B, (kin + r) * cnt + i, 0))
        wL = pow(5, (P - 1) // L, P)
        E.outer_run(B, L, cnt, wL)
        for r in LOOP(L):                                              # rows_const: pointwise by the kernel spectrum
            CTL(10); c = LD(spec, r)
            for8_loop(cnt, lambda i, r=r, c=c: ST(B, r * cnt + i, MUL(LD(B, r * cnt + i), c)))
        E.outer_run(B, L, cnt, wL, inv=True)

    def spectrum(self, L, ker):
        x = ker + [0] * (L - len(ker)); E.outer_run(x, L, 1, pow(5, (P - 1) // L, P)); return x

    def reset(self, table):
        """the running factors of a phase, set from their base table (charged as rows_reset)"""
        run = [0] * len(table)
        for r in LOOP(len(table)): ST(run, r, LD(table, r))
        return run

    def rows_rec(self, SA, sidx, DA, didx, rows, base, step, j0):
        """rows of cnt elements with the scale base[r] * step[r]^j (j = j0 .. j0 + cnt - 1): loaded from SA[sidx(r, i)], stored into DA[didx(r, i)];
        per row 10 control operations (addresses), the factor and its step loaded, the factor stored back (16 in all), per element a load, two
        multiplications (the element, the factor by its step) and a store"""
        cnt = self.cnt
        for r in LOOP(rows):
            CTL(10); f = LD(base, r); st = LD(step, r)
            fb = [f]                                                   # the running factor is held in a register
            def body(i, r=r, st=st):
                ST(DA, didx(r, i), MUL(LD(SA, sidx(r, i)), fb[0])); fb[0] = MUL(fb[0], st)
            for8_loop(cnt, body)
            ST(base, r, fb[0])

    def ext(self, arr, direction):
        """in place: arr[k] holds the values on coset (k if direction 12 else K + k); afterwards the values on the other set"""
        K, h, cnt, L = self.K, self.h, self.cnt, self.Lx
        srcK = 0 if direction == 12 else K; dstK = K - srcK
        res = [x for k in range(K) for x in self.ivals(arr[k])]        # inverse inner transforms (h * u^j r_j), flat: coset k at k h
        spec = self.spectrum(L, self.kap)
        if direction == 12:
            base_in = [self.s12[k] for k in range(K)]; step_in = [inv(self.u[k]) for k in range(K)]
            base_out = [self.o12[k] for k in range(K)]; step_out = [self.u[K + k] for k in range(K)]
            rin = lambda r: r; rout = lambda n: n - K
        else:
            base_in = [self.s21[K - 1 - r] for r in range(K)]; step_in = [inv(self.u[K + K - 1 - r]) for r in range(K)]
            base_out = [self.o21[2 * K - 1 - n] for n in range(K, 2 * K)]; step_out = [self.u[2 * K - 1 - n] for n in range(K, 2 * K)]
            rin = lambda r: K - 1 - r; rout = lambda n: 2 * K - 1 - n
        out = [0] * (K * h)
        base_out = [x * inv(L) % P for x in base_out]                  # the factor L of the inverse outer transform is folded into the output factors
        base_in = self.reset(base_in); base_out = self.reset(base_out)
        for g0 in LOOP(h // cnt):
            j0 = g0 * cnt; CTL(20)
            B = [0] * (L * cnt)
            self.rows_rec(res, lambda r, i: rin(r) * h + j0 + i, B, lambda r, i: r * cnt + i, K, base_in, step_in, j0)
            self.conv_group(B, L, K, spec)
            self.rows_rec(B, lambda r, i: (K + r) * cnt + i, out, lambda r, i: rout(K + r) * h + j0 + i, K, base_out, step_out, j0)
        for k in range(K): arr[k] = self.vals(out[k * h:(k + 1) * h])  # forward inner transforms

    def eval_coef(self, f, nodes0, kout, L):
        """values of the polynomial f (coefficient list, rows of h) on the kout cosets nodes0 .. nodes0 + kout - 1 by the chirp evaluation"""
        K_, h, cnt, z = -(-len(f) // self.h), self.h, self.cnt, self.z
        f = f + [0] * (K_ * h - len(f))
        chi = [pow(z, C2(n), P) for n in range(K_ + kout - 1)]
        spec = self.spectrum(L, chi)
        # input row t' = K_ - 1 - t holds f_t z^(nodes0 t) z^-C(t,2); output row n = K_ - 1 + k, scale z^-C(k,2) * u^j (twist of the forward inner transform)
        cin = [pow(z, (nodes0 * (K_ - 1 - r) - C2(K_ - 1 - r)) % (P - 1), P) for r in range(K_)]
        base_out = [pow(z, (-C2(k)) % (P - 1), P) * inv(L) % P for k in range(kout)]; step_out = [self.u[nodes0 + k] for k in range(kout)]
        out = [0] * (kout * h)
        base_out = self.reset(base_out)
        for g0 in LOOP(h // cnt):
            j0 = g0 * cnt; CTL(20)
            B = [0] * (L * cnt)
            for r in LOOP(K_):                                         # rows_const
                CTL(10); c = LD(cin, r)
                for8_loop(cnt, lambda i, r=r, c=c: ST(B, r * cnt + i, MUL(LD(f, (K_ - 1 - r) * h + j0 + i), c)))
            self.conv_group(B, L, K_, spec)
            self.rows_rec(B, lambda r, i: (K_ - 1 + r) * cnt + i, out, lambda r, i: r * h + j0 + i, kout, base_out, step_out, j0)
        return [self.vals(out[k * h:(k + 1) * h]) for k in range(kout)]

    def interp(self, arr):
        """coefficients (rows of h) of the polynomial of degree < K h whose values on O2 are arr"""
        K, h, cnt, z, L = self.K, self.h, self.cnt, self.z, self.Lx
        res = [x for k in range(K) for x in self.ivals(arr[k])]
        M = [1]
        for k in range(K): M = pmul(M, [(-pow(z, k, P)) % P, 1])
        dM = [sum(i * c * pow(z, k * (i - 1), P) for i, c in enumerate(M) if i) % P for k in range(K)]
        chi = [pow(z, C2(n), P) for n in range(2 * K - 1)]
        sp1 = self.spectrum(L, chi); sp2 = self.spectrum(L, [0] + M[1:K + 1])
        base_in = [inv(dM[K - 1 - r]) * pow(z, (-C2(K - 1 - r)) % (P - 1), P) * inv(h) % P for r in range(K)]; step_in = [inv(self.u[K + K - 1 - r]) for r in range(K)]
        mid = [pow(z, (-C2(i)) % (P - 1), P) * inv(L) % P for i in range(K)]
        cout = [pow(z, (-K * t) % (P - 1), P) * inv(L) % P for t in range(K)]
        coef = [0] * (K * h)
        base_in = self.reset(base_in)
        for g0 in LOOP(h // cnt):
            j0 = g0 * cnt; CTL(20)
            B = [0] * (L * cnt); B2 = [0] * (L * cnt)
            self.rows_rec(res, lambda r, i: (K - 1 - r) * h + j0 + i, B, lambda r, i: r * cnt + i, K, base_in, step_in, j0)
            self.conv_group(B, L, K, sp1)
            # A(i) z^C(i,2) sits in row K - 1 + i; A(i) goes to row K - 1 - i of the second buffer (reversed for the correlation with mu)
            for r in LOOP(K):
                CTL(10); c = LD(mid, r)
                for8_loop(cnt, lambda i, r=r, c=c: ST(B2, (K - 1 - r) * cnt + i, MUL(LD(B, (K - 1 + r) * cnt + i), c)))
            self.conv_group(B2, L, K, sp2)
            for r in LOOP(K):                                          # h_t in row K + t
                CTL(10); c = LD(cout, r)
                for8_loop(cnt, lambda i, r=r, c=c: ST(coef, r * h + j0 + i, MUL(LD(B2, (K + r) * cnt + i), c)))
        return coef


def run(h, m, E_, cnt, seed):
    rnd = random.Random(seed)
    V = VD(h, m, cnt); K, n1 = V.K, V.n1
    g = [rnd.randrange(P) for _ in range(m)] + [1]
    gO = V.eval_coef(g, 0, 2 * K, V.Le)
    for k in range(2 * K):
        assert gO[k] == [ev(g, V.point(k, i)) for i in range(h)], 'g evaluation'
    g1, g2 = gO[:K], gO[K:]
    assert all(x for c in g1 for x in c), 'g vanishes on O1 (the trial would ABORT)'
    ng1 = [[(-inv(x)) % P for x in c] for c in g1]
    # the exponent: the start monomial S^v (v a power of two, a multiple of h, v < m), then the bits of E_ below
    top = E_.bit_length() - 1; v = 1; bit = top
    while bit >= 1 and ((v << 1) | ((E_ >> (bit - 1)) & 1)) < m:
        v = (v << 1) | ((E_ >> (bit - 1)) & 1); bit -= 1
    assert v & (v - 1) == 0 and v % h == 0
    # Barrett start: q = floor(X^v P1 / g) from the reciprocal of the reversed g and the reversed top of X^v P1
    P1 = [0] * (n1 + 1)
    for i, c in enumerate(V.M1): P1[i * h] = c
    T = [0] * v + P1
    delta = len(T) - 1 - m; ell = delta + 1
    rg = g[::-1]; rec = [1]
    while len(rec) < ell:                                              # Newton: rec := rec (2 - rg rec) mod X^(2 len)
        l2 = min(2 * len(rec), ell); e_ = pmul(rg[:l2], rec)[:l2]
        e_ = [(-x) % P for x in e_]; e_[0] = (e_[0] + 2) % P
        rec = pmul(rec, e_)[:l2]
    assert pmul(rg[:ell], rec)[:ell] == [1] + [0] * (ell - 1)
    q = pmul(T[::-1][:ell], rec)[:ell][::-1]
    assert q == trim(pdivmod(T, g)[0]) + [0] * (ell - len(trim(pdivmod(T, g)[0]))), 'Barrett quotient'
    qO2 = V.eval_coef(q, K, K, E.pad23(-(-ell // h) + K - 1))
    R2 = [[(pow(V.u[K + k], v, P) * ev(V.M1, pow(V.z, K + k, P)) - qO2[k][i] * g2[k][i]) % P for i in range(h)] for k in range(K)]
    want0 = pdivmod(T, g)[1]
    assert R2 == [[ev(want0, V.point(K + k, i)) for i in range(h)] for k in range(K)], 'R~_0 on O2'
    R1 = [c[:] for c in R2]; V.ext(R1, 21)
    assert R1 == [[ev(want0, V.point(k, i)) for i in range(h)] for k in range(K)], 'extension O2 -> O1'
    e = v; P1g = pdivmod(P1, g)[1]
    for b_ in range(bit - 1, -1, -1):
        b = (E_ >> b_) & 1
        W = [[(R1[k][i] * R1[k][i] % P) * ng1[k][i] % P for i in range(h)] for k in range(K)]          # u0 = -R~^2 / g on O1
        V.ext(W, 12)
        R2 = [[pow(V.point(K + k, i), b, P) * (R2[k][i] * R2[k][i] + W[k][i] * g2[k][i]) % P * V.invM[k] % P for i in range(h)] for k in range(K)]
        R1 = [c[:] for c in R2]; V.ext(R1, 21)
        e = 2 * e + b
        Rc = V.interp(R2)
        assert len(trim(Rc)) <= m + 1, 'deg R~ <= m'
        assert pdivmod(Rc, g)[1] == pdivmod(pmul(pdivmod([0] * e + [1], g)[1], P1g), g)[1], 'invariant R~ = X^e P1 mod g'
        assert all(R1[k] == [ev(Rc, V.point(k, i)) for i in range(h)] for k in range(K))
    assert e == E_
    W = [[R1[k][i] * ng1[k][i] % P for i in range(h)] for k in range(K)]                                # leave the Montgomery form
    V.ext(W, 12)
    R2 = [[(R2[k][i] + W[k][i] * g2[k][i]) * V.invM[k] % P for i in range(h)] for k in range(K)]
    Rc = trim(V.interp(R2)); gc = trim(V.interp(g2))
    assert Rc == pdivmod([0] * E_ + [1], g)[1], 'S^E mod g'
    assert gc == g, 'g back in coefficient form'
    return V


def check_charges(h, m, cnt):
    """the executed charges of the geometric phases equal the closed forms of Appendix E"""
    V = VD(h, m, cnt); K = V.K
    arr = [[random.randrange(P) for _ in range(h)] for _ in range(K)]
    saved = (E.VH,); E.VH = h
    try:
        res = [V.ivals(a) for a in arr]
        # extension geometric phase alone (the inner transforms are charged by inner_all)
        V.ivals = lambda v: v; V.vals = lambda v: v
        KC[0] = 0; V.spectrum_saved = V.spectrum
        spec_cost = [0]
        orig = V.spectrum
        def sp(L, ker):
            k0 = KC[0]; x = orig(L, ker); spec_cost[0] += KC[0] - k0; return x
        V.spectrum = sp
        KC[0] = 0; V.ext([a[:] for a in res], 12); got = KC[0] - spec_cost[0]
        assert got == E.geo_ext(K, K, V.Lx, cnt), (got, E.geo_ext(K, K, V.Lx, cnt))
        spec_cost[0] = 0; KC[0] = 0; V.ext([a[:] for a in res], 21); got = KC[0] - spec_cost[0]
        assert got == E.geo_ext(K, K, V.Lx, cnt)
        f = [random.randrange(P) for _ in range(m + 1)]
        spec_cost[0] = 0; KC[0] = 0; V.eval_coef(f, 0, 2 * K, V.Le); got = KC[0] - spec_cost[0]
        assert got == E.geo_eval(K, 2 * K, V.Le, cnt), (got, E.geo_eval(K, 2 * K, V.Le, cnt))
        spec_cost[0] = 0; KC[0] = 0; V.interp(arr); got = KC[0] - spec_cost[0]
        assert got == E.geo_interp(K, V.Lx, cnt), (got, E.geo_interp(K, V.Lx, cnt))
    finally:
        E.VH = saved[0]


def check_order():
    """the order of z = 5^(2^32) exceeds 2K at r = 21 (4.6 Points, lemma 4.7): p - 1 = 2^32 * 3 * 463 * q1 * q2 with q1 = 539204044132271846773 prime
    (deterministic Miller-Rabin with the prime bases up to 41, valid below 3.3 * 10^24) and q1 > 2K.  ord(z) divides (p - 1)/2^32 = 1389 q1 q2; if
    z^(1389 q2) != 1 then q1 divides ord(z), so ord(z) >= q1 > 2K: the nodes z^k, k < 2K, are distinct and z^e != 1 for 1 <= e < 2K"""
    q1, q2 = 539204044132271846773, 8999194758858563409123804352480028797519453
    assert P - 1 == 2 ** 32 * 1389 * q1 * q2 and q1 > 2 * 867361738
    d, s = q1 - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41):
        x = pow(a, d, q1)
        if x in (1, q1 - 1): continue
        for _ in range(s - 1):
            x = x * x % q1
            if x == q1 - 1: break
        else: raise AssertionError('q1 composite')
    assert pow(5, (P - 1) // 2, P) != 1                           # omega = 5^((p-1)/2^32) has order 2^32
    z = pow(5, 2 ** 32, P)
    assert pow(z, 1389 * q2, P) != 1
    print('ok: ord(z) >= q1 > 2K = %d at r = 21' % (2 * 867361738))


if __name__ == '__main__':
    random.seed(7)
    check_order()
    for (h, m, E_, cnt, seed) in ((8, 37, (1 << 11) | 0b101101, 4, 1), (8, 40, (1 << 12) | 0b1100111, 8, 2), (16, 70, (1 << 14) | 0b11010011, 8, 3), (4, 25, (1 << 9) | 0b10111, 2, 4)):
        run(h, m, E_, cnt, seed)
        check_charges(h, m, cnt)
        print('ok: h = %d, m = %d, E = %d: S^E mod g, g and every step invariant; geometric charges equal geo_ext / geo_eval / geo_interp' % (h, m, E_))
```

### G.5 check2_hgcd_shapes.py

The half-gcd of 4.4 with real arithmetic (big-integer Kronecker products) on random pairs over the Pallas field (`m = 500, 1234, 3000`), with the windows of the program, the in-place base case and the top node (its freed high pieces overwritten with garbage), against the plain Euclidean algorithm; every call of `hgcd`, `apply_inv`, `apply_inv_split` and `mat_mul` is recorded with its lengths and window, and the records must equal, in execution order, those of the ledger's `gcd_cost` (Appendix E). At these sizes the program forms whole outputs (single transforms), so a second pass applies the window of lemma 4.8 at every eligible node and checks the gcd, and a window one coefficient too large is shown to be detected. Run: `python3 check2_hgcd_shapes.py` (with `stage_cd.py`; about 20 s).

```python
#!/usr/bin/env python3
"""Check 2: the half-gcd shapes charged by the ledger (stage_cd.py, Appendix E) equal the shapes of the real algorithm of proof.md 4.4.
This revision: the real algorithm forms only the top window of (c, d) in a node that wants its matrix only and divides on the windows; the top node of
the driver computes c, then d, from the low pieces a mod X^cut, b mod X^cut, and the high pieces of (a, b) (after the first call's apply_inv) and of
(d, e) (after the second call's apply_inv) are overwritten with garbage, so any later read of them would corrupt the gcd.

The real algorithm runs on random pairs (g of m+1 coefficients, b of m) over the Pallas field, with the base case at k <= 96 and the driver
switching to classical Euclid at n <= 192, exactly as the ledger.  Every call of hgcd records (len a, len b, k); every apply_inv records
(entry lengths of the matrix, len a, len b, output lengths); every matrix product R1 Q R2 records the entry lengths of R1 Q and of R2.
The ledger's hgcd, apply_inv and mat_mul are wrapped (cache bypassed) to record the same tuples from gcd_cost(m, 0).  The two sequences of
records, in execution order, must be identical."""
import importlib.util, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('L', os.path.join(HERE, 'stage_cd.py'))
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
P = L.P
BASE, DRIVER_SMALL = 96, 192


def trim(a):
    while a and a[-1] == 0: a.pop()
    return a


def mul(a, b):
    """product by Kronecker substitution (one big-integer multiplication)"""
    if not a or not b: return []
    W = (2 * 255 + max(len(a), len(b)).bit_length() + 8 + 7) // 8
    A = int.from_bytes(b''.join(x.to_bytes(W, 'little') for x in a), 'little')
    B = int.from_bytes(b''.join(x.to_bytes(W, 'little') for x in b), 'little')
    C = (A * B).to_bytes(W * (len(a) + len(b)), 'little')
    return trim([int.from_bytes(C[i * W:(i + 1) * W], 'little') % P for i in range(len(a) + len(b) - 1)])


def add(a, b):
    out = [0] * max(len(a), len(b))
    for i, x in enumerate(a): out[i] = x
    for i, x in enumerate(b): out[i] = (out[i] + x) % P
    return trim(out)


def neg(a): return [(-x) % P for x in a]


def divrem(a, b):
    a = a[:]; q = [0] * max(0, len(a) - len(b) + 1); inv = pow(b[-1], P - 2, P)
    while len(a) >= len(b) and a:
        c = a[-1] * inv % P; s = len(a) - len(b); q[s] = c
        for i, y in enumerate(b): a[i + s] = (a[i + s] - c * y) % P
        trim(a)
    return trim(q), a


def top(a, s): return a[s:] if s > 0 else a[:]
def ident(): return [[[1], []], [[], [1]]]
def mmul(A, B): return [[add(mul(A[i][0], B[0][j]), mul(A[i][1], B[1][j])) for j in range(2)] for i in range(2)]
def lens(R): return [len(R[0][0]), len(R[0][1]), len(R[1][0]), len(R[1][1])]


REC = []


def apply_inv(R, a, b, w=0):
    det = add(mul(R[0][0], R[1][1]), neg(mul(R[0][1], R[1][0])))
    sg = det[0]
    c = trim([x * sg % P for x in add(mul(R[1][1], a), neg(mul(R[0][1], b)))])
    d = trim([x * sg % P for x in add(mul(R[0][0], b), neg(mul(R[1][0], a)))])
    REC.append(('apply_inv', tuple(lens(R)), len(a), len(b), len(c), len(d), w))
    return c[w:], d[w:], len(c), len(d)


def apply_inv_split(R, a, b, cut, lc, ld):
    """the top node: c, then d, from the low pieces only (window [0, lc) of a product that does not cancel)"""
    det = add(mul(R[0][0], R[1][1]), neg(mul(R[0][1], R[1][0])))
    sg = det[0]
    a_, b_ = a[:cut], b[:cut]
    c = trim([x * sg % P for x in add(mul(R[1][1], a_), neg(mul(R[0][1], b_)))][:lc])
    d = trim([x * sg % P for x in add(mul(R[0][0], b_), neg(mul(R[1][0], a_)))][:ld])
    REC.append(('apply_inv_split', tuple(lens(R)), cut, lc, ld))
    return c, d


GARBLE = []
FORCE = [False, 0]


def garble(x, frm):
    for i in range(frm, len(x)): x[i] = (x[i] * 7 + 12345) % P


def hgcd(a, b, k, want_mat, want_pair, hook=None):
    REC.append(('hgcd', len(a), len(b), k))
    n = len(a) - 1
    if not b or n - (len(b) - 1) > k: return ident(), 0, a, b
    if k <= BASE:
        R = ident(); c, d = a, b; h = 0
        while d and (len(c) - len(d)) <= k - h:
            assert len(c) - len(d) == 1, 'abnormal'
            q, r = divrem(c, d); h += 1
            R = mmul(R, [[q, [1]], [[1], []]]); c, d = d, r
        return R, h, c, d
    k1 = (k + 1) >> 1
    if 2 * k1 > n: k1 = n >> 1
    s = n - 2 * k1
    R1, h1, _, _ = hgcd(top(a, s), top(b, s), k1, True, False)
    assert h1 == k1, 'return test'
    w = 0
    if want_mat and not want_pair:
        lc_, ld_ = len(a) - h1, len(a) - h1 - 1; k3_ = k - h1 - 1; s3_ = (ld_ - 1) - 2 * k3_
        if s3_ > 0 and not (ld_ == 0 or (lc_ - ld_) > k - h1): w = s3_ - 1
        if w and not FORCE[0]: w = L.apply_inv(tuple(lens(R1)), [0] * 4, h1, len(a), len(b), False, 3, (0, 0), 0, 0, w)[5][2]   # the window the program uses (block products only)
        if w and FORCE[0]: w += FORCE[1]                       # FORCE: every eligible node uses its window (FORCE[1] = 1: a window one too large, must fail)
    c, d, lc, ld = apply_inv(R1, a, b, w)
    if w: assert len(c) == lc - w and len(d) == ld - w, 'a windowed node: a leading coefficient at its normal degree is zero (ABORT)'
    if hook: hook()
    k2 = k - (n - (lc - 1))
    if not d or lc - ld > k2: return R1, h1, c, d
    assert lc - ld == 1, 'abnormal'
    q, e = divrem(c, d)                                # on the windows: q is the quotient of the whole pair, e[i'] = e_(w + i') for i' >= 1
    k3 = k2 - 1
    s3 = (ld - 1) - 2 * k3
    if s3 > 0:
        R2, h3, _, _ = hgcd(top(d, s3 - w), top(e, s3 - w), k3, True, False)
        cc = dd = None
        if want_pair: cc, dd, _, _ = apply_inv(R2, d, e)
    else:
        assert w == 0
        R2, h3, cc, dd = hgcd(d, e, k3, want_mat, want_pair)
    R = None
    if want_mat:
        R1Q = mmul(R1, [[q, [1]], [[1], []]])
        REC.append(('mat_mul', tuple(lens(R1Q)), tuple(lens(R2))))
        R = mmul(R1Q, R2)
    return R, h1 + 1 + h3, cc, dd


def hgcd_top(a, b, k, want_mat=False, want_pair=True):
    """the top node of the driver (pair wanted), as hgcd_top of the ledger"""
    REC.append(('hgcd', len(a), len(b), k))
    n = len(a) - 1
    k1 = (k + 1) >> 1
    if 2 * k1 > n: k1 = n >> 1
    s = n - 2 * k1
    lc = len(a) - k1; ld = lc - 1; cut = lc
    R1, h1, _, _ = hgcd(top(a, s), top(b, s), k1, True, False, hook=lambda: (garble(a, cut), garble(b, cut)))
    assert h1 == k1, 'return test'
    c, d = apply_inv_split(R1, a, b, cut, lc, ld)
    assert len(c) == lc and len(d) == ld
    q, e = divrem(c, d)
    assert len(c) - len(d) == 1 and len(e) == ld - 1
    k3 = k - h1 - 1; cut2 = ld - k3
    s3 = (ld - 1) - 2 * k3
    assert s3 > 0
    R2, h3, _, _ = hgcd(top(d, s3), top(e, s3), k3, True, False, hook=lambda: (garble(d, cut2), garble(e, cut2)))
    assert h3 == k3
    cc, dd = apply_inv_split(R2, d, e, cut2, ld - h3, ld - h3 - 1)
    return None, h1 + 1 + h3, cc, dd


def gcd_real(a, b):
    first = [True]
    while b:
        n = len(a) - 1
        if n <= DRIVER_SMALL:
            q, r = divrem(a, b); a, b = b, r; continue
        _, _, c, d = (hgcd_top if first[0] else hgcd)(a, b, (n + 1) // 2, False, True); first[0] = False
        if not d: return c
        q, e = divrem(c, d); a, b = d, e
    return a


def ledger_records(m, cut, hi):
    out = []
    raw_h, raw_a, raw_m, raw_s, raw_t = L.hgcd.__wrapped__, L.apply_inv, L.mat_mul, L.apply_inv_split, L.hgcd_top
    def h(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr=()):
        out.append(('hgcd', la, lb, k)); return raw_h(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr)
    def ai(Rl, Rs, hh, la, lb, *rest, **kw):
        res = raw_a(Rl, Rs, hh, la, lb, *rest, **kw)
        out.append(('apply_inv', tuple(Rl), la, lb, res[1], res[3], res[5][2])); return res
    def sp(Rl, Rs, hh, cut_, outl, b, dcut=None, lowp=None):
        out.append(('apply_inv_split', tuple(Rl), cut_, outl[0], outl[1])); return raw_s(Rl, Rs, hh, cut_, outl, b, dcut, lowp)
    def tp(la, lb, k, cut_, b):
        out.append(('hgcd', la, lb, k)); return raw_t(la, lb, k, cut_, b)
    def mm(A, B, b):
        out.append(('mat_mul', tuple(A[0]), tuple(B[0]))); return raw_m(A, B, b)
    L.hgcd, L.apply_inv, L.mat_mul, L.apply_inv_split, L.hgcd_top = h, ai, mm, sp, tp
    L.TOPCUT[0], L.TOPHI[0] = cut, hi
    L.TOPLOW[0], L.TOPHIGH[0] = (cut, cut), (hi, hi)
    try:
        L.gcd_cost(m, 0, 3, (cut + hi, cut + hi))
    finally:
        L.hgcd, L.apply_inv, L.mat_mul, L.apply_inv_split, L.hgcd_top = L.functools.lru_cache(maxsize=None)(raw_h), raw_a, raw_m, raw_s, raw_t
    return out


def gcd_plain(a, b):
    while b:
        q, r = divrem(a, b); a, b = b, r
    return a


def main():
    rnd = random.Random(21)
    for m in [int(x) for x in sys.argv[1:]] or [500, 1234, 3000]:
        g = [rnd.randrange(P) for _ in range(m)] + [1]
        b = [rnd.randrange(P) for _ in range(m - 1)] + [rnd.randrange(1, P)]
        REC.clear(); G = gcd_real(g[:], b[:]); assert G == gcd_plain(g, b), 'gcd differs from plain Euclid'
        real = list(REC)
        k1 = (((m + 1) // 2) + 1) >> 1; cut = m + 1 - k1
        led = ledger_records(m, cut, m + 1 - cut)
        kinds = {k: sum(1 for r in real if r[0] == k) for k in ('hgcd', 'apply_inv', 'mat_mul')}
        same = real == led
        print('m = %5d  gcd degree %d  records: real %d, ledger %d  (%s)  identical: %s' % (m, len(G) - 1, len(real), len(led), kinds, same))
        if not same:
            for i, (x, y) in enumerate(zip(real, led)):
                if x != y: print('  first difference at record', i, '\n   real  ', x, '\n   ledger', y); break
            else: print('  lengths differ')
            sys.exit(1)
    print('ok: the ledger charges exactly the calls and shapes of the real algorithm')
    # windows at every eligible node (at these sizes the program's products are single transforms, which form whole outputs)
    for m in (1234, 3000):
        g = [rnd.randrange(P) for _ in range(m)] + [1]
        b = [rnd.randrange(P) for _ in range(m - 1)] + [rnd.randrange(1, P)]
        FORCE[0], FORCE[1] = True, 0
        REC.clear(); G = gcd_real(g[:], b[:]); nw = sum(1 for r in REC if r[0] == 'apply_inv' and r[-1] > 0)
        assert G == gcd_plain(g, b) and nw > 0
        FORCE[1] = 1; bad = False
        try:
            REC.clear(); bad = gcd_real(g[:], b[:]) != gcd_plain(g, b)
        except AssertionError:
            bad = True
        FORCE[0] = False
        assert bad, 'a window one coefficient too large is not detected'
        print('m = %5d  windows at %d nodes: gcd equal to plain Euclid; a window one coefficient too large is detected' % (m, nw))
    print('ok: windows')


if __name__ == '__main__':
    main()
```

### G.6 check3_chunk_counts.py

Scheme (c) of 4.5 executed with real arithmetic and counted charges at small block lengths (4 and 8; squares, windows, cyclic products with subtraction, two-output bilinear forms, one-block operands, radix-3 outer transforms, chunk counts 1 to 4), against the charge `scheme_c` of the ledger at the same block length; the products are checked against schoolbook products. Run: `python3 check3_chunk_counts.py` (with `stage_cd.py`).

```python
#!/usr/bin/env python3
"""Check 3: scheme (c) of proof.md 4.5 executed with counted charges, against the closed form of the ledger (stage_cd.py scheme_c, via conv_bilin_big).

The block length is set to a small value (HB_BITS restricted to it).  The executed product does real arithmetic over the Pallas field and charges
every operation it executes under the rules of proof.md 4.2: loads and stores 2, field operations 1, the eight-element loop rule for8,
3 per iteration and 2 on exit for the piece and segment loops, 10 per piece for its factor and addresses.  The outer transforms are
executed by the ledger's own kernels (outer_run, counted by KCOUNT).  Only the inner block transform of 2 HB points and the pointwise pass are
charged as the ledger's per-call constants at that block length (bfwd, binv, pw_loop) and computed exactly instead (a schoolbook product of
the two rows).  Each product is checked against the schoolbook product reduced modulo X^(n2 HB) - 1, and the executed count must equal
PL['co'] of conv_bilin_big for the same lengths, window and chunk bound."""
import importlib.util, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('L', os.path.join(HERE, 'stage_cd.py'))
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
P = L.P


def set_hb(hb):
    L.HB = hb; L.NB = 2 * hb
    L.FOLD_ROW = 8 * hb + L.for8(hb) + 4
    L.big_fwd.cache_clear()
    L.HB_BITS = [hb.bit_length() - 1]                          # scheme (c) at this block length (the ledger picks the cheapest of 2^6 .. 2^31)


class Count:
    def __init__(self): self.n = 0
    def __iadd__(self, k): self.n += k; return self


C = Count()


def FOR8(n):
    """loop over n elements written eight per pass: charged for8(n) as a whole"""
    global C
    C += L.for8(n)
    return range(n)


def LOOP(n):
    global C
    for t in range(n):
        C += 3; yield t
    C += 2


def root(n):
    w = pow(5, (P - 1) // n, P)
    assert pow(w, n, P) == 1 and all(pow(w, n // q, P) != 1 for q in (2, 3) if n % q == 0)
    return w


def schoolbook(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b): out[i + j] = (out[i + j] + x * y) % P
    return out


def outer_points(n3):
    """position b of a forward-transformed chunk array holds the value at the point k (the map of check_outer)"""
    r3, M, ks = L.outer_plan(n3); a = M.bit_length() - 1
    rev = lambda v: int(format(v, '0%db' % a)[::-1], 2) if a else 0
    pos_k = {}
    for k1 in range(3 if r3 else 1):
        for pos in range(M):
            k2 = rev(pos)
            k = next(kk for kk in range(n3) if kk % M == k2 and (not r3 or kk % 3 == k1))
            b = (M * k1 + 3 * pos) % n3 if r3 else pos
            pos_k[b] = k
    return pos_k


def executed(groups, outlen, ws, sub, shared, n2, nc):
    """scheme (c) on real data, charged; returns (outputs, charge)"""
    global C
    C = Count(); HB, NB = L.HB, L.NB
    operands = []                                            # (length, data) in the ledger's order: H then (unless shared) S of each group
    for g in groups:
        operands += g['Hd']
        if not shared: operands += g['Sd']
    nout = len(outlen)
    prods = [[] for _ in range(nout)]                         # (sign, index of S operand, index of H operand)
    base = 0
    for g in groups:
        nh = len(g['Hd']); ns = len(g['Sd'])
        for (si, hi), (o, sg) in g['prod'].items():
            sidx = base + hi if shared else base + nh + si
            prods[o].append((sg, sidx, base + hi))
        base += nh + (0 if shared else ns)
    w = root(n2); n3 = n2 // nc; w3 = pow(w, nc, P); inv_n2 = pow(n2, P - 2, P)
    C += 2 + L.ROOTS
    blocks = lambda a: [a[i * HB:(i + 1) * HB] for i in range(L.nblk(len(a)))]
    multi = [i for i, a in enumerate(operands) if L.nblk(len(a)) > 1]
    single = [i for i, a in enumerate(operands) if L.nblk(len(a)) == 1]
    for i in single: C += L.bfwd(len(operands[i]), HB)        # transformed once, used at every outer point
    out = [[0] * outlen[k] for k in range(nout)]
    pos_k = outer_points(n3)
    C += 3 * nc + 2
    for j in range(nc):
        first = j == 0; tw = 0 if first else 1
        C += 6
        chunk = {}
        for i in multi:                                       # twist and fold
            bl = blocks(operands[i]); kx = len(bl)
            arr = [0] * (n3 * HB); started = [False] * n3
            for t in LOOP(kx + max(0, n3 - kx)):
                if t < kx:
                    u = t % n3; f = pow(w, (j * t) % n2, P); C += 10
                    blk = bl[t]
                    for c in FOR8(len(blk)):
                        x = blk[c]; C += 2
                        if tw: x = x * f % P; C += 1
                        if started[u]: x = (x + arr[u * HB + c]) % P; C += 3
                        arr[u * HB + c] = x; C += 2
                    if not started[u]:
                        for c in FOR8(HB - len(blk)) if (kx <= n3 and t == kx - 1) else ():
                            arr[u * HB + len(blk) + c] = 0; C += 2
                    started[u] = True
                else:                                         # a row with no block is zeroed
                    u = t; C += 10
                    for c in FOR8(HB): arr[u * HB + c] = 0; C += 2
            L.KCOUNT[0] = 0; L.outer_run(arr, n3, HB, w3); C += L.KCOUNT[0]
            chunk[i] = arr
        outs = {k: [0] * (n3 * HB) for k in range(nout) if prods[k]}
        for b in range(n3):                                   # the outer points of this chunk
            C += 8
            o = (j + nc * pos_k[b]) % n2; wo = pow(w, o, P)
            rows = {}
            for i in multi: C += L.bfwd(HB, HB); rows[i] = chunk[i][b * HB:(b + 1) * HB]
            for i in single: rows[i] = operands[i] + [0] * (HB - len(operands[i]))
            for k in outs:
                acc = [0] * (2 * HB)
                for t, (sg, si, hi) in enumerate(prods[k]):
                    C += L.pw_loop(2 * HB, 0) if t == 0 else L.pw_loop(2 * HB, 1)
                    pr = schoolbook(rows[si], rows[hi])
                    for c, v in enumerate(pr): acc[c] = (acc[c] + sg * v) % P
                C += L.binv(HB)
                C += 4                                        # the fold modulo X^HB - w^o into row b of the output chunk array
                for c in FOR8(HB):
                    outs[k][b * HB + c] = (acc[c] + wo * acc[c + HB]) % P; C += 8
        for k in outs:
            L.KCOUNT[0] = 0; L.outer_run(outs[k], n3, HB, w3, inv=True); C += L.KCOUNT[0]
            z = outs[k]                                       # n3 * (the inverse transform), natural order
            per = 5 if (first and not sub) else 8
            pos = ws; end = ws + outlen[k]; nseg = 0
            while pos < end:                                  # untwist into the window, segment by segment (cut at block boundaries)
                seg_end = min(end, (pos // HB + 1) * HB); s = pos // HB; C += 10; nseg += 1
                fac = pow(w, (-(j * (s % n2))) % n2, P) * inv_n2 % P
                for c in FOR8(seg_end - pos):
                    t = pos + c; v = z[(s % n3) * HB + t % HB] * fac % P
                    if per == 5: out[k][t - ws] = v
                    else: out[k][t - ws] = (out[k][t - ws] + (-v if sub else v)) % P
                    C += per
                pos = seg_end
            C += 3 * nseg + 2
    return out, C.n


def cyclic(full, period, ws, ln):
    red = [0] * period
    for i, c in enumerate(full): red[i % period] = (red[i % period] + c) % P
    return [red[(ws + i) % period] for i in range(ln)]


def case(name, hb, lens_groups, outlen, ws=0, sub=False, shared=False, cf=None, cyc=None, ltrue=None, rnd=random.Random(3)):
    set_hb(hb)
    groups = []
    for H, S, prod in lens_groups:
        Hd = [[rnd.randrange(P) for _ in range(l)] for l in H]; Sd = Hd if shared else [[rnd.randrange(P) for _ in range(l)] for l in S]
        groups.append(dict(H=H, S=S, prod=prod, Hd=Hd, Sd=Sd))
    L.CTX['cf'] = cf; L.CTX['cyc'] = cyc; L.CTX['ltrue'] = ltrue
    try:
        ops, eps = L.conv_bilin_big(len(outlen), outlen, [dict(H=g['H'], S=g['S'], prod=g['prod']) for g in groups], ws, sub, shared)
    finally:
        L.CTX['cf'] = None; L.CTX['cyc'] = None; L.CTX['ltrue'] = None
    PL = dict(L.PL)
    need = 0                                                   # the ledger's rule for n2 (conv_bilin_big), recomputed: PL keeps n2, nc only when scheme (c) is chosen
    for k in range(len(outlen)):
        if cyc: need = max(need, cyc); continue
        lk = ltrue[k] if ltrue else max(len(sd) + len(hd) - 1 for g in groups for (si, hi), (o, sg) in g['prod'].items() if o == k
                                        for sd, hd in [((g['Hd'] if shared else g['Sd'])[si], g['Hd'][hi])])
        need = max(need, ws + outlen[k], lk - ws)
    n2 = L.pad23(-(-need // hb)); nc = L.nc_for(n2, cf)
    if PL['mode'] == 'c': assert (n2, nc) == (PL['n2'], PL['nc'])
    PL['n2'], PL['nc'] = n2, nc
    got, charge = executed(groups, outlen, ws, sub, shared, n2, nc)
    period = PL['n2'] * hb
    for k in range(len(outlen)):
        full = []
        for g in groups:
            for (si, hi), (o, sg) in g['prod'].items():
                if o != k: continue
                pr = schoolbook((g['Hd'] if shared else g['Sd'])[si], g['Hd'][hi])
                full = [(a + sg * b) % P for a, b in zip(full + [0] * (len(pr) - len(full)), pr + [0] * (len(full) - len(pr)))]
        ref = cyclic(full, period, ws, outlen[k])
        if sub: ref = [(-x) % P for x in ref]
        assert got[k] == ref, (name, k)
    ok = charge == PL['co']
    print('%-34s HB=%2d n2=%3d nc=%d  executed %9d  ledger co %9d  %s  (scheme chosen by the ledger: %s)' % (name, hb, PL['n2'], PL['nc'], charge, PL['co'], 'equal' if ok else 'DIFFER', PL['mode']))
    return ok


def main():
    allok = True
    m = 45
    allok &= case('square (shared operand), nc=1', 4, [([m], [m], {(0, 0): (0, 1)})], [2 * m - 1], shared=True)
    allok &= case('square, chunked nc=4', 4, [([m], [m], {(0, 0): (0, 1)})], [2 * m - 1], shared=True, cf=4 * 7)
    allok &= case('quotient window [m-1, 2m-1), nc=2', 4, [([m], [m], {(0, 0): (0, 1)})], [m], ws=m - 1, cf=4 * 13)
    allok &= case('q*g cyclic N\'>=m+1, subtract, nc=2', 4, [([m + 1], [m], {(0, 0): (0, 1)})], [m], sub=True, cf=4 * 7, cyc=m + 1)
    allok &= case('apply_inv-like, 2 outputs x 2 terms', 4, [([37], [9, 9], {(0, 0): (0, 1), (1, 0): (1, -1)}), ([36], [10, 8], {(0, 0): (0, -1), (1, 0): (1, 1)})],
                  [28, 27], ltrue=[28, 27], cf=4 * 4)
    allok &= case('one-block operand times multi-block', 8, [([60], [6], {(0, 0): (0, 1)})], [65])
    allok &= case('radix-3 outer (n2 = 3 * 2^a), nc=2', 4, [([20], [27], {(0, 0): (0, 1)})], [46], cf=4 * 6)
    allok &= case('odd window, partial blocks', 8, [([33], [21], {(0, 0): (0, 1)})], [30], ws=7, cf=5 * 4)
    print('ok: the executed charges equal the ledger closed form' if allok else 'MISMATCH')
    sys.exit(0 if allok else 1)


if __name__ == '__main__':
    main()
```

### G.7 alloc_sim.py

The arena of section 7 at r = 21 at the level of addresses: the allocator of 4.2 (first fit for large requests, last fit for small ones, splitting, merging, and compaction when a large request finds no hole) on an arena of exactly the claimed size, replaying the allocations and frees of the ledger (Appendix E) in execution order: stage C in full, stage D with every call of `hgcd` with `k >= 2^44` (13,106,194 allocations), the calls with `k < 2^44` and the rest of the driver inside the scratch region. It asserts that every request is served and that the compactions (3 per trial, 29 blocks, 22,924,228,636,997,165,691 elements moved) are at most those charged in row D. Without compaction first fit fails in stage D at this size. Run: `python3 alloc_sim.py` (with `stage_cd.py`; about ten minutes).

```python
#!/usr/bin/env python3
"""Appendix G.7: the arena of section 7 serves stages C and D at the level of addresses (standard library only; several minutes).
The allocator of 4.2 is simulated on an arena of exactly the claimed size (the peak of the live set walked by Appendix E): blocks of 64 + 32 * slots bytes
rounded up to 64 (header included); a request of more than 196,608 bytes takes the free block of lowest address that fits, a smaller request the free block
of highest address that fits; a block is split when the remainder is at least 128 bytes (the request at the low end for a large request, at the high end for
a small one); a free merges with free neighbours.  Compaction (4.2, this entry): when no free block fits a large request, every live large block is moved
down, in address order, to close the gaps (the arrays are reached through a handle table, which is updated), and the request is served from the space
freed; the moves are counted.  The events are those of the ledger (stage_cd.py, Appendix E): its allocations and frees are replayed in execution order
(a free names the block of the matching allocation; where the ledger frees by a size, the most recent live block of that size).  Start: the twiddle
table, then the array of g (stages A, B).  Stage C runs in full.  Stage D: the scratch region (4.4) is allocated at its start; every call of hgcd with
k >= 2^44 runs with its events, a call with k < 2^44 runs inside the scratch region and its returned matrix is allocated in the arena; when the driver
reaches k < 2^44 the rest of stage D runs in the scratch region.  It asserts that every request is served (a compaction serves any request that the live
set leaves room for, so this checks the peak walk too) and prints the number of compactions and of moved elements, which bound the row of section 6."""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('L', os.path.join(HERE, 'stage_cd.py'))
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
SMALL = 196608
M = (5 ** 27 - 1) // 2


class H(int):
    """a slot count that carries the identity of its block"""
    pass


class Arena:
    def __init__(self, size):
        self.b = [[0, size, None]]                  # [address, bytes, owner id or None (free)], sorted by address
        self.size = size; self.nid = 0; self.slots = {}; self.live = []; self.small = {}
        self.ncomp = 0; self.moved = 0; self.blocks_moved = 0

    def _place(self, nbytes, hid, high):
        idx = range(len(self.b) - 1, -1, -1) if high else range(len(self.b))
        for i in idx:
            a, sz, own = self.b[i]
            if own is None and sz >= nbytes:
                rest = sz - nbytes
                if rest >= 128:
                    self.b[i:i + 1] = [[a, rest, None], [a + rest, nbytes, hid]] if high else [[a, nbytes, hid], [a + nbytes, rest, None]]
                else:
                    self.b[i][2] = hid
                return True
        return False

    def compact(self):
        """move every live large block down to close the gaps; small blocks (at the top) stay"""
        out = []; addr = 0; tops = []
        for a, sz, own in self.b:
            if own is None: continue
            if self.small[own]: tops.append([a, sz, own]); continue
            if a != addr: self.moved += self.slots[own]; self.blocks_moved += 1
            out.append([addr, sz, own]); addr += sz
        lowest_top = min([t[0] for t in tops] + [self.size])
        assert addr <= lowest_top
        res = out + ([[addr, lowest_top - addr, None]] if lowest_top > addr else [])
        prev = lowest_top
        for t in sorted(tops):
            if t[0] > prev: res.append([prev, t[0] - prev, None])
            res.append(t); prev = t[0] + t[1]
        if prev < self.size: res.append([prev, self.size - prev, None])
        self.b = res; self.ncomp += 1

    def alloc(self, nbytes, slots):
        self.nid += 1; hid = self.nid
        high = nbytes <= SMALL
        if not self._place(nbytes, hid, high):
            free = sum(x[1] for x in self.b if x[2] is None)
            if high or free < nbytes:
                raise MemoryError('request of %d bytes fails: %d bytes free in all (live %d blocks)' % (nbytes, free, len(self.live)))
            self.compact()
            assert self._place(nbytes, hid, high)
        self.slots[hid] = slots; self.live.append(hid); self.small[hid] = high
        return hid

    def free(self, hid):
        for i, x in enumerate(self.b):
            if x[2] == hid: break
        else:
            raise KeyError(hid)
        x[2] = None
        if i + 1 < len(self.b) and self.b[i + 1][2] is None:
            x[1] += self.b[i + 1][1]; del self.b[i + 1]
        if i > 0 and self.b[i - 1][2] is None:
            self.b[i - 1][1] += x[1]; del self.b[i]
        self.live.remove(hid); del self.slots[hid]; del self.small[hid]

    def free_size(self, slots):
        for hid in reversed(self.live):
            if self.slots[hid] == slots: return self.free(hid)
        raise KeyError(slots)


A = None
ON = [True]
on_new, on_free = L.Tr.new_fp, L.Tr.free


def new_fp(self, slots):
    r = on_new(self, slots)
    if not ON[0]: return r
    h = H(r); h.hid = A.alloc(L.blk(r), r)
    return h


def free(self, slots):
    on_free(self, slots)
    if not ON[0]: return
    if isinstance(slots, H) and slots.hid in A.slots: A.free(slots.hid)
    else: A.free_size(int(slots))


raw_h = L.hgcd.__wrapped__
cached = L.hgcd
TAIL = [False]


def hg(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr=()):
    if TAIL[0] or not ON[0]: return cached(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr)
    if k >= L.KSCR: return raw_h(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr)
    if own or wc or wd:                                        # a driver iteration with k < 2^44: the rest of stage D runs in the scratch region
        TAIL[0] = True; ON[0] = False
        return cached(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr)
    assert want_mat and not fr
    ON[0] = False
    try:
        t, o = cached(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr)
    finally:
        ON[0] = True
    Rs = []
    for x in o[5]:                                             # the returned matrix, copied into the arena
        if x:
            h = H(x); h.hid = A.alloc(L.blk(x), x); Rs.append(h)
        else: Rs.append(x)
    return t, o[:5] + (Rs,) + o[6:]


def main():
    global A
    m = M
    r = L.main(False)                                          # the ledger: the arena (peak of the live set)
    arena = r['arena']
    L.Tr.new_fp, L.Tr.free = new_fp, free
    L.CF.clear(); L.CF.update({k: int(v * m) for k, v in L.CF_FRAC.items()}); L.TCAP_NEWTON[0] = int(0.9 * m)
    L.hgcd.cache_clear()
    ON[0] = False
    C0, (lo, hi) = L.powx_vd(m, 3)
    L.TOPCUT[0] = lo; L.TOPHI[0] = hi; L.TOPLOW[0] = (L.VD['G'][0], L.VD['R'][0]); L.TOPHIGH[0] = (L.VD['G'][1], L.VD['R'][1])
    L.SCRMAX[0] = 0; L.gcd_cost(m, 0, 3, (lo + hi, lo + hi)); scr = -(-L.SCRMAX[0] // 32)
    A = Arena(arena)
    ON[0] = True
    A.alloc(L.blk(L.twiddle_slots(m)), L.twiddle_slots(m))
    gs = L.GSLOTS(m); A.alloc(L.blk(gs), gs)
    C, (lo, hi) = L.powx_vd(m, 3)
    print('stage C: every request served in the arena of %s bytes; %d compactions' % (format(arena, ','), A.ncomp), flush=True)
    nc0, mv0 = A.ncomp, A.moved
    A.alloc(L.blk(scr), scr)
    L.TOPCUT[0] = lo; L.TOPHI[0] = hi; L.TOPLOW[0] = (L.VD['G'][0], L.VD['R'][0]); L.TOPHIGH[0] = (L.VD['G'][1], L.VD['R'][1])
    L.hgcd = hg
    nev0 = A.nid
    L.gcd_cost(m, 0, 3, (lo + hi, lo + hi))
    print('stage D: scratch region %s bytes; %d allocations replayed with addresses; every request served; %d compactions moving %d blocks, %s elements (%.3f copies of m)'
          % (format(L.blk(scr), ','), A.nid - nev0, A.ncomp - nc0, A.blocks_moved, format(A.moved - mv0, ','), (A.moved - mv0) / m))
    assert A.ncomp <= L.COMPACT['n'] and A.blocks_moved <= L.COMPACT['blocks'] and A.moved <= L.COMPACT['elements'], 'the ledger charges fewer compactions'
    print('ok: the arena of %s bytes serves stages C and D; compactions per trial %d, moved blocks %d, moved elements %d (charged in row D: %s)' % (format(arena, ','), A.ncomp, A.blocks_moved, A.moved, L.COMPACT))
    return A.ncomp, A.blocks_moved, A.moved


if __name__ == '__main__':
    sys.setrecursionlimit(100000)
    main()
```
