# Orchard Poseidon, r = 17: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, half-gcd, at most 2 centres

## 1. Claim

Target: `poseidon-orchard-r17-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, seventeen partial rounds 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 and 20, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with a worst-case operation count (sections 6-7) and a success probability derived from the premises `H-GEOM-w1` (section 9.1) and `H-NORMAL` (section 9.5), a statement about the number of rational components of two algebraic curves attached to the fixed digest polynomial; section 9.2 derives the success probability from it with explicit constants.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and 925186 inverse transforms (one per coset, section 3), compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod in the value domain (section 4.6, the method of bradcush 1aa56884) and a half-gcd in the lean form of 1aa56884 (4.4.1), and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. At most `K = 2` centres are tried, one after the other, on a single thread; the first verified collision ends the algorithm.
* `success_probability = 0.41286`: a lower bound for the probability, over the algorithm's fresh random words, that one of the `K` centres yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta + delta_C)^K - K (eps_iso + eps_coin)` with `q = 0.24375` (the linear two-moment bound for `P(1 <= k <= DMAX)` of section 9.2(e'), from the same two moments as the Cauchy-Schwarz bound `0.22257` of 9.2(d)-(e); the reduction is gta6rp's, entry c1364311), `delta = 0.01` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `delta_C < 2^-148.2` the stage-C zero test (proved, 9.2(g)), `K = 2`, `eps_iso < 2^-48`, `eps_coin < 2^-128`. The exact value is `0.412860937` (`0.428085937` with `delta = 0`). The score does not change: `K = 2` centres are still needed (9.3).
* `time_log2 = 63.03322` in target-compression units (`C(17) = 573` primitive operations per unit): the worst-case operation count, derived in section 6 as `T_fixed + K * T_trial` with every trial charged in full (stage D for the normal remainder sequence, which bounds every trial because a trial with any other sequence ends after a prefix of that work, section 6.3; stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 5,408,072,822,851,330,654,318` operations, `log2(N_max / 573) = 63.033213242357846`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 59.407` (`764,059,563,750,454,540` bytes, section 7).
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `130` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^23`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Prior entry: this entry is the r = 17 version of our r = 7 algebraic entry 05a41d88 (the same algorithm, ledger method, premise structure and evidence design). The ruling on 05a41d88 (not_evaluable on the experiments lane) is answered here in the same way: the organizer experiments `line-ladder-w6`, `-w8`, `-w10` and `-w12` on the antipodal line pairs of this construction at r = 17 (10.2), the computations of Grok job 136 and their re-run on the deployed constants and the attack line (10.3), and the measurement of the Euclidean sequences on the sibling targets (10.5). Stage C is the value-domain powering of bradcush's entry 1aa56884 (section 4.6), stage D its lean half-gcd (4.4.1), and stage D is charged for the normal remainder sequence under the premise `H-NORMAL` of bradcush (entries e6dcb600, 1aa56884) with gta6rp's allowance and organizer-run tests (9.5); all credited in the dependencies and the note.
* Declared heuristics (claim.json): `H-GEOM-w1` (score-critical, section 9.1) and `H-NORMAL` (score-critical for the success probability only, section 9.5). Both are statements about probability. `H-NORMAL` is bradcush's premise (entries e6dcb600 and 1aa56884), stated here with the allowance `delta = 0.01` and supported by organizer-run normality tests, the recipe of gta6rp's entries (c1364311 at this round count); the test program `experiments/exp_euclid.py` is our own (10.5.1). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2, the register file of 18 words, stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation. Everything else is proved or counted here: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the Cauchy-Schwarz and linear two-moment reductions (section 9.2), the stage-C zero-test bound (9.2(g)), the isolation lemma (section 9.4), the independence of the centres, the cap rules and every operation count (sections 4, 6, 7).
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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 (partial), 60, 61, 62, 63 (full) put twenty-three S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^23 = D = 11,920,928,955,078,125`. The leading coefficient is obtained by
propagating leading coefficients through the twenty-three layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x115915986431c2e7966cb72756a3adaca346bb8ce561469beedfe128852b688f`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 5,960,464,477,539,062`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. At this r no transform of `H >= m + 1` points exists: `p - 1 = 2^32 * 3 * q` has roots of unity of order `3 * 2^a` for `a <= 32` only, and `m + 1 = 5,960,464,477,539,063 > 3 * 2^32`. Let `B = 3 * 2^31 = 6,442,450,944`, `zeta` a primitive `2B`-th root of unity (`2B = 3 * 2^32` divides `p - 1`) and `omega = zeta^2`, a primitive `B`-th root. Let `kappa = ceil((m + 1) / B) = 925186`, `v_k = 2^k` and `u_k = v_k^2 = 4^k` for `k < kappa`, and `z = 4^B`; the `kappa` numbers `n_k = u_k^B = z^k` form a geometric progression and are pairwise distinct, because the order of `z` exceeds `kappa` (Appendix G: `z^d != 1` for every divisor `d` of `p - 1` up to `2 * 10^8`, and `kappa < 2 * 10^8`). The evaluation points are `s_{k,i} = v_k zeta^i` for `k < kappa`, `i < B`, so that `S_{k,i} = s_{k,i}^2 = u_k omega^i`, and `g_c(S_{k,i}) = (F(c + s_{k,i}) - F(c - s_{k,i})) / (2 s_{k,i})`. Write `g_c(x) = sum_{t < kappa} x^{tB} h_t(x)` with `deg h_t < B`. For `y = omega^i` we have `y^B = 1`, hence `g_c(u_k y) = w_k(y)` with `w_k(y) = sum_t n_k^t h_t(u_k y)`, a polynomial of degree `< B`. One inverse transform of size `B` of the values `(g_c(S_{k,i}))_i` returns the coefficients `w_k[j] = u_k^j sum_t n_k^t h_t[j]`. After multiplication by `u_k^{-j}`, for every `j < B` the numbers `W_k[j] = sum_t n_k^t h_t[j]` (`k < kappa`) are the values of the polynomial `h^(j)(X) = sum_t h_t[j] X^t` at the nodes `z^k`, and its coefficients `h_t[j] = g_c[j + tB]` are recovered from them by two correlations of length `kappa` (Lagrange interpolation at geometric nodes, the chirp-z form). Let `M(X) = prod_k (X - z^k) = sum_i mu_i X^i`; the q-binomial theorem gives `mu_{kappa-j} = (-1)^j z^{j(j-1)/2} [kappa choose j]_z`, and `M'(z^k) = z^{k(k-1)/2 + k(kappa-1-k)} prod_{j <= k} (z^j - 1) prod_{j <= kappa-1-k} (1 - z^j)`. With `a_k = W_k[j] / M'(z^k)` and `A(i) = sum_k a_k z^{ki}` (`i < kappa`) we have `h_t[j] = sum_{i > t} mu_i A(i - t - 1)`. Since `z^{ki} = z^{C(k+i,2) - C(k,2) - C(i,2)}` with `C(n,2) = n(n-1)/2`, `A(i) z^{C(i,2)}` is the correlation of the sequence `a_k z^{-C(k,2)}` with the chirp `z^{C(n,2)}` (first correlation), and `h_t[j]` is the correlation of `A` with `(mu_1, ..., mu_kappa)` (second correlation). Each correlation is one cyclic convolution of length `S = 2,097,152` (the smallest `2^a` or `3 * 2^a` that is at least `2 kappa - 1`), done with the transform of length `S` (forward, pointwise product, inverse); the transforms of the fixed sequences (the chirp and `mu`) and the constants `mu_i`, `1/M'(z^k)`, `z^{-C(k,2)}` are computed once per trial and shared by the `B` positions `j`. Appendix G runs this solve against the direct recovery at `kappa = 7`. The `2 kappa B = 11,920,930,838,151,168` evaluations of `F` are each charged as one target-compression unit (`C(17) = 573` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation. The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 s_{k,i})`, two multiplications for the recurrences of `s_{k,i}` and `1/s_{k,i}`, one store with its address operation, the loop control, the update of the row counter, and the executed shifts, masks, ors and loop control of the bit-reversed index, which are counted inside that function) and the solve (per `j`: two correlations, each two transforms of length `S` with `S/2 log2` butterflies at the charge of the model's own pass cost and `10 S` operations for the pointwise product and the scalings, and `14 kappa` operations for the chirp scalings, the division by `M'`, the loads and the stores) and its once-per-trial constants (`kappa` times two inversions, 40 operations per index, four transforms of length `S` and `10 S` operations) are charged on top.



## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (11,920,930,838,151,168 evaluations + 925186 inverse NTTs of size 6,442,450,944 + the geometric solve of the 925186 cosets (two correlations of length 2,097,152 per position) + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; value domain, section 4.6: from S^v, v = 2^50; 203 squaring steps, 45 of them also multiply by S, pointwise)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (573 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 52 bits after the leading one are zero, so the algorithm starts from the monomial `S^v` with `v = 2^50` (a multiple of h below m, 4.6, `VSHIFT = 2`; 50 + 203 = 253), and the loop of stage C has 203 steps, of which 45 also multiply by `S` (pointwise).

Stopping rule over the `K` centres. The loop bound `K = 2` is a constant of the algorithm. A trial is run to its end, or to an ABORT of stage D on an abnormal remainder sequence (6.3) or of stage C on a zero of g on O1 (4.6 step 5), which then resets the allocator and draws the next centre; the claim charges every trial at its maximum (stages E to G at their worst case, section 6), so a trial that fails early is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3, 4.4), the powering has a fixed number of steps, and the half-gcd has a fixed recursion: 46 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 2,980,232,238,769,531` and is halved, rounded up, until it is at most 96) and at most 46 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 5,960,464,477,539,062 to at most 192). Hence, with stage D charged for the normal remainder sequence and every other sequence ending its trial after a prefix of that work (section 6.3), the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success, by an ABORT of a trial (the next centre is then drawn), or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

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
* random words: the cost model's random-word primitive (an independent uniform 256-bit word) is one operation per word. The word of a draw is also loaded, stored into the cell `y` of the draw and addressed (one load, one store and three control operations), 6. A draw is that word (6), the reduction modulo `p` (three steps each of a comparison, a conditional branch and a field subtraction, 9, with the loop control of three iterations, 11), the conversion of the result to the internal representation (1), the entry (2) and the address of `y` (2): 31 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: 573 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation: every array is taken from one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes (`need` bytes), and `need` decides the allocator. A block of more than 2^45 = 35,184,372,088,832 bytes comes from the pool, one region with two ends: its blocks follow each other in address order, each with a header (size, size of the previous block, in-use flag), no two free blocks are adjacent, and the unused middle between the two ends is one free block. Each allocation statement of the program uses one end of the pool, a constant of the statement: the statements marked `# pool:H` in the listing of Appendix E (`g` of stage A, the block array of stage B, `MU` and `Y`, the work arrays of the Newton products, of a squaring step (in a chunked product of a squaring step, all its arrays except the accumulators of the square `R^2`, which use the low end) and of a shift, and the results inside the half-gcd: the quotient and remainder of a node and of the outer loop, the outputs of apply_inv, of the matrix products and of mul_add_q2, every allocation of the lean stage D (`ld_new`, all sites `# pool:H`, including the working arrays of its block products), and the reversed `g` and the operand rev(X^v P1) of stage C step 1 (4.6)) use the high end, every other statement the low end, except that the copies of the remainders returned by a node that applies its second matrix (4.4, step (6)) are taken from the low end. A low request walks the blocks upward from the bottom of the pool, a high request downward from the top (the two sizes in the header give both neighbours, so the two walks are the same code mirrored); it takes the first free block with at least `need` bytes (the unused middle is the last block of either walk) and cuts the block from the side nearest its own end, and the rest stays a free block when it is at least 128 bytes (else it belongs to the block); a free merges the block with a free neighbour on either side, the unused middle included, the same code for both ends. Since no two free blocks are adjacent and a walk ends at the middle, a walk examines at most 2 P + 1 blocks, P the live blocks on its side of the pool, and one block examined is 13 operations (two comparisons with branches, two loads, the advance). A block of at most 2^45 bytes comes from the slab classes: the class `j` is the least `j >= 7` with `2^j >= need`, a slot is `2^j` bytes; a request takes the first slot of the free list of its class, else a new slot from the end of the slab area, and writes the class and the in-use flag into the header; a free puts the slot on the free list of its class. The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows: a request of the pool 97 operations besides the walk (the statement that calls the allocator, the set-up, the split, the header stores, and a flat 64 for the statistics) and 13 per block examined, a request of a slab class at most `126` (the statement that calls the allocator, the class `j` by a binary search over 7..63 in 6 steps of 6 operations, the pop or the bump, the two header stores, and a flat 64 for the statistics), a free 81 for a slab block and at most 105 for a pool block (a free tests the size of the block to choose the allocator, in place of the test for a null pointer, which the program never needs). Every allocation of the walk is charged `1 + 120 + 13 (2 L + 1)` with L the live blocks at that point, which covers the pool (P <= L, the 97 operations and 13 per block examined) and the slab path (at most `126 <= 1 + 120 + 13` operations), and every free 105 (550 per allocation and 105 per free at 16 live blocks in stage E). The memory of both allocators is the arena of section 7.
* trial loop: the test of the trial counter, its increment and the bookkeeping of the trial, at most 12 operations per trial, are `TRIAL_EXTRA` = 12 in the ledger; the loop test and update of stage A are 5.
* the offline derivation of the constants is charged in section 6.2.



### 4.3 Stage C: the powering schedule (cyclic form, below the block length; block mode in 4.5)

In this entry stage C runs in the value domain (section 4.6). This section and 4.5 define the transforms, the products and the Newton reciprocal that 4.6 uses for its set-up.

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
### 4.4 Stage D: the half-gcd

Notation: a polynomial is stored as its coefficient array with the top coefficient nonzero (length = degree + 1). Euclid sequence of `(a, b)`, `deg a > deg b`: `r_0 = a`, `r_1 = b`, `r_{i-1} = q_i r_i + r_{i+1}`; `d_j = deg q_1 + ... + deg q_j`, so `deg r_j = deg a - d_j`;
`R_j = Q_1 ... Q_j` with `Q_i = [[q_i, 1], [1, 0]]` (entries of degree at most `d_j`; the first-row entries of degree exactly `d_j` for `r11`), and `(r_0, r_1)^T = R_j (r_j, r_{j+1})^T`.

`hgcd(a, b, k)` (`deg a = n`) returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` and, only when asked (the calls of the Euclid driver, below), the pair `(r_h, r_{h+1})`; the inner calls return the matrix only. The procedure: if `b = 0` or `n - deg b > k` return the identity. If `k <= 96`, plain Euclid (`poly_divrem_naive`) while the next quotient degree fits the remaining parameter; a division step whose quotient has two coefficients (the normal case) is one pass over the remainder, `r_k = a_k - q0 b_k - q1 b_(k-1)`, with `b_(k-1)` kept from the previous iteration and no copy of `a` (per element 2 loads, 2 multiplications, 2 subtractions, 1 store, each load and store with its address operation, the loop control of 3 and the test `if (k)` of 2 operations), and `R := R Q` for a two-coefficient quotient is likewise one pass per entry pair (`mul_add_q2`).
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`, evaluated cyclically on `3 * 2^j` points (the high coefficients of `c` and `d` cancel, so the cyclic result is exact); the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each of the four matrix entries are transformed once (six forward transforms of a row) and the two output rows are inverse transformed (`conv_bilin_otf`), the sign of each output being absorbed in the scale factor `1/N`; (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1`
(`d_1 = deg R1`) return `R1` and `(c, d)`; (4) divide `c = q d + e` (`divrem_any`); (5) `k3 = k - d_1 - deg q`, `s3 = deg d - 2 k3`; if `s3 > 0`, `R2 = hgcd(d quo x^s3, e quo x^s3, k3)` (the top `2 k3 + 1` coefficients of `d` and the coefficients of `e` of the same degrees, read in place, matrix wanted), otherwise the call runs on `(d, e)`; this is the same top-coefficient lemma that step (1) uses (the quotients of a pair whose degrees sum to at most `k3`, and the stopping test, depend only on those coefficients; von zur Gathen and Gerhard, Modern Computer Algebra, chapter 11; the same truncation as bradcush 1aa56884, its lemma 4.4), and 1aa56884 (its Appendix G.3) runs the node with and without it against plain Euclid; (6) only if the caller wants the pair, `(c', d') = R2^{-1} (d, e)` by `apply_inv`, each moved into an array of its own length; return `R1 Q R2` (matrix products by NTT, only if the matrix is wanted; the product of the two 2 x 2 matrices transforms each of the eight entries once per row, with the right-factor entries of one column pair held and the left-factor entries streamed, and inverse transforms the four outputs, `conv_bilin_otf` again).
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: `(c, d) = hgcd(a, b, floor((n+1)/2))`, one division `c = q d + e` and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). With `H-NORMAL` (9.5) stage D runs the normal-sequence procedure of bradcush (entry e6dcb600): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter ; a zero remainder met inside hgcd or in the division of the outer loop also ends the trial (ABORT); on any other case the trial ends (ABORT) and the next centre is drawn (section 6.3).

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

#### 4.4.1 The lean stage D (this entry; the stage D of bradcush 1aa56884, its section 4.4 and lemmas 4.4 and 4.8, credited)

This entry runs the half-gcd above with six changes, all from 1aa56884 (credited in the dependencies and the note), charged by this model's rules of 4.2 and 4.5 (Appendix E, the block `LEAND`). They change where arrays live and which coefficients are formed, never a quotient: every quotient used is a quotient of the whole pair (lemma 4.4 above, and lemma 4.8 below).

1. *The base case in place.* For `k <= 96` the two remainders are two arrays and a division step with a quotient of two coefficients is one pass `r_k = a_k - q0 b_k - q1 b_(k-1)` written over the array of `a`; the roles of the two arrays swap. The four matrix entries are four arrays of `k + 2` elements allocated once, and `R := R Q` writes `r11 q + r12` over `r12`. No array is allocated or freed inside the loop.
2. *Matrix-only calls.* A call returns the reduced pair only when its caller wants it: the calls of the Euclid driver `poly_gcd_own` and, inside them, the second calls with `s3 <= 0`. Every call inside a first call, and every truncated second call, returns its matrix only.
3. *Windows.* In a node that wants its matrix only and has `s3 > 0`, the block products of `apply_inv` form only the top window of `c` and `d`: the coefficients of degree at least `s3 - 1` (lemma 4.8 (a)). Such a node tests that the coefficients of `c` and `d` at their normal leading degrees `la - h - 1` and `la - h - 2` are nonzero (2 tests, charged) and ABORTs otherwise, so it never reports a shorter remainder from a window.
4. *The two tests and the ABORT.* At every division the quotient test (the quotient has degree 1) and after every recursive call and every call of `poly_gcd_own` the return test (the call returned exactly its parameter as degree count; a zero remainder inside hgcd or in the outer-loop division also ABORTs), 2 operations each, charged wherever they execute. If a test fails the trial ABORTs: the allocator is reset to its state after initialisation (`1,000` operations, charged in section 6) and the next centre is drawn. On the normal remainder sequence neither test fails (6.3), so every division of stage D is the one-pass division by a quotient of two coefficients and the Newton division is never run.
5. *The top node in pieces.* Stage C leaves `g` and `R` in two pieces each, the coefficients `[0, cut)` and `[cut, l)` with `cut = 4,470,352,285,532,160`. The first call of `poly_gcd_own` frees the high pieces of `g` and `R` right after its own `apply_inv`; the pair `(c, d)` is then formed from the low pieces only (`c` first, by the block products of 4.5 with the window `[0, lc)`, `lc = m + 1 - k1`; then `r22` and `r12` are freed; then `d`; then `r11`, `r21` and the low pieces are freed). The pair `(d, e)` of the second call is written as two pieces at `cut2 = deg d + 1 - k3` and handled the same way.
6. *Block products of stage D.* Each product of apply_inv, of the top node and of mat_mul uses the cheapest of the single transform, scheme (a) at block length 2^31 (one row of passes of 2^32 points) and scheme (c) at the block length 2^b of least charge (b = 6..31, transforms of 2^(b+1) points). The number of chunks is the least power of two that brings a chunk form to at most `m // 16` elements. The outputs are allocated first at their true lengths, the chunks accumulate into them, the working arrays follow and are freed at the end, and the operands are freed after the last chunk. This replaces, for stage D, the Blocks, Choice, stage-D and Scaling bullets of 4.5. There is no placement pass in stage D: each output of a scheme (c) product is untwisted straight into its window with the scaled weight `sign / (NB n2) * w^(-e)` (the sign of the output, the factor `1/NB` of the unnormalised inverse transform and `1/n2` of the outer transform applied here), charged 15 operations per product (the scale and the weight base), 7 per untwist call (load the table entry, load the scale, multiply, store) and the chunk and outer-point loops; at r = 17 this is 1,990,733,201,301,664 operations per trial (290,596 products, 151,512,250,017,674 untwist calls), included in row D (Appendix E). The choice between the single transform and the block products counts every charge of each path, including the allocations and frees the block path adds.

**Lemma 4.8 (windows and pieces; 1aa56884's lemma 4.8).** (a) In a node that wants its matrix only, with `s3 > 0`, the rest of the node reads `c` only at degrees at least `s3` and `d` only at degrees at least `s3 - 1`. (b) In the top node, after the first call's `apply_inv` no operation reads `a` or `b` at degrees at least `cut`, and the low `lc` and `lc - 1` coefficients of `c` and `d` computed from `a mod X^cut` and `b mod X^cut` are the `c` and `d` of step (2); the same holds for `(d, e)`, `cut2` and `(c', d')`.
*Proof.* (a) The stopping test and the quotient test use `deg c` and `deg d`; the quotient `q = q1 x + q0` uses the top two coefficients of `c` and of `d`; and `e_i = c_i - q0 d_i - q1 d_(i-1)`. The second call reads only `d quo x^s3` and `e quo x^s3`, that is `d_i` and `e_i` for `i >= s3`, hence `c_i` for `i >= s3` and `d_i` for `i >= s3 - 1`. After it the node needs only `R1`, `q` and `R2` (and `s3 - 1 <= deg d - 1`, so the top two coefficients are inside the window). (b) The first call reads `a quo x^s` and `b quo x^s` and, after its `apply_inv`, only its own arrays; the top node then reads `a` and `b` only in step (2). For `i < lc <= cut` the coefficient `i` of `r22 a` is `sum_j r22_j a_(i-j)` with `i - j < cut`, so it equals the coefficient `i` of `r22 (a mod X^cut)`; `c` has length `lc`, so it is the low `lc` coefficients of `s (r22 (a mod X^cut) - r12 (b mod X^cut))`, and likewise `d`. For the second call, `cut2 = deg d + 1 - k3 >= lc'` with `lc' = deg d + 1 - h3` and `h3 = k3` on the normal sequence. QED

The charges of these steps are this model's (4.2, 4.5), not 1aa56884's: with 1aa56884's own conventions the same walk gives its published row D to the unit (`1,062,106,645,154,198,605,714,641` at r = 21, recomputed in our model with their conventions switched on), and with this model's primitives it gives row D of section 6.

### 4.5 Products longer than `3 * 2^32` points (block mode)

The bullets of earlier entries on the coefficient-domain stage C are not repeated: stage C is 4.6, which uses this section only for the Newton reciprocal and the q product of its step 1. Stage D uses 4.4.1 item 6.

At this r the transforms of 4.3 and 4.4 would have up to `3 * 2^52` points (the square of stage C, `2m - 1 = 11,920,928,955,078,123` coefficients) and `3 * 2^51` points (`m + 1`, the products by `g`, and the products by the half-gcd matrices, whose entries have several blocks). The field has no root of unity of such an order (`p - 1 = 2^32 * 3 * q`). Grok (xAI), job 140, determined the cost of multiplying polynomials of lengths `3 * 2^34`, `3 * 2^36` and `3 * 2^38` over this field and recommends the block NTT (its scheme (a)) for `3 * 2^34` and `3 * 2^36` and the same split with an outer transform across the blocks (its scheme (b), the outer FFT) for `3 * 2^38`: a product is cut into blocks, the blocks are transformed with the longest available transform, and the products of block spectra are summed in the transform domain. Grok job 140 checked both schemes against schoolbook on random products of length `2^14` with a transform cap of `2^10` (every coefficient equal, and the counted multiplications and additions equal to its formulas, `551,999` and `890,850` for scheme (a)). Both schemes are the same operations at every block count; at the lengths of this r we apply them by the charging rules of 4.2 (our theory beyond the lengths Grok analysed). Appendix G repeats the check for the forms used here (windows, subtraction placement, the bilinear form of `apply_inv` and the matrix product with multi-block entries, the outer scheme with its fold and wrap rule, and the coset solve of section 3) at transform size `24`. The schemes, as used by the algorithm:

* Blocks. `B = 3 * 2^31` coefficients per block, transform size `NB = 2B = 3 * 2^32 = 12,884,901,888` (the plan of the largest transform of 4.3, with its kernels and charges). An operand of `l` coefficients has `ceil(l / B)` blocks; each block is zero-padded to `NB` points and transformed once (forward: the radix-3 stage and three rows of radix-2 passes). A product of two blocks has at most `2B - 1 < NB` coefficients, so a block product does not wrap.
* Scheme (a), slots. The slot `s` of a product `A C` is the sum of the block products `A_i C_j` with `i + j = s`; it is formed pointwise in the transform domain (`NB` multiplications per pair, additions or subtractions for the further pairs), inverse transformed once, and placed at offset `s B` of the output: a loop with a load, the multiplication by `1/NB` (and the sign), a store, and for the coefficients that overlap the previous slot a load of the output value and an addition (a subtraction when the placement subtracts into an array). Only the slots that meet the wanted window of the product are formed. The windows are those of 4.3: the Newton products use `[0, l2)`; the quotient `q` of a step is the window `[m - 2, 2m - 3)` of `T1 * MU`; the remainder uses the window `[0, m)` of `q g`.
* Scheme (b), outer transform (the scheme from which (c) below is derived; it is not used at this r). Let `ns` be the number of slots of the product, `[s0, s1]` the slots that meet the window, and `n2` the smallest `2^a` or `3 * 2^a` that is at least `max(s1 + 2, ns + 1 - s0)` (it divides `3 * 2^32`, so the roots exist). For every position `t < B` the `n2` values of the blocks of an operand at that position (zero beyond its last block) are transformed with the `n2`-point transform across the blocks (twiddles: powers of a primitive `n2`-th root of unity); this gives, for each of the `n2` outer points `o`, a polynomial of `B` coefficients, which is transformed with the block transform (`NB` points). For each outer point the spectra are multiplied pointwise (and summed over the products of the bilinear form), the result is inverse transformed, and its upper part (positions `B ..`) is multiplied by the `o`-th power of the outer root and added to the lower part (the fold). The inverse `n2`-point transform across the outer points returns, for each position `t`, the coefficients of the pieces of the product; the cyclic wrap of length `n2` does not reach the pieces of the window. The window is placed with the scaling `1/NB` and `1/n2`. Price of the outer transform (exact, from its kernels): a transform of `n2` points at each of the `B` positions of a block is a twiddle table of `n2` entries (3 operations each), `n2/3` calls of the radix-3 kernel `ob3` when `3` divides `n2`, and `n2/2` calls of the radix-2 kernel `ob2` in each of the `log2` radix-2 layers; a call of `ob3` is charged `7 + 24 B` and a call of `ob2` `5 + 13 B` (every load, store, field operation and loop step of the kernel text in `ntt_kern.h`, parsed like every other kernel), plus 10 for the call (block addresses, twiddle address, call and return). The charges are integers; nothing is averaged or truncated.
* Forms. The form of an operand of `l` coefficients is what a product multiplies pointwise. In scheme (a) it is the `ceil(l / B)` block spectra of `NB` points each (`ceil(l / B) * NB` elements). In scheme (b), when `l > B`, it is the `n2` outer-domain arrays of `B` elements each (`n2 * B` elements): the blocks are copied into one array of `n2` blocks, zero beyond the last block (the copy is charged, `7 l + 2` operations, and so is the zero fill of the other `n2 B - l` positions, `5 (n2 B - l) + 2` operations, because the form is taken from the pool, whose memory holds the data of earlier arrays), and transformed across the blocks; when `l <= B` the form is the one spectrum of `NB` points. A form is made from the coefficient array of the operand and charged as in 4.2 (each block transform, or the copy and the outer transform); the coefficient array is freed as soon as the form exists whenever the operand is not needed again. In scheme (b) the inner transform of an outer point is made when that point is multiplied, into a working array of `NB` points, and the output of an outer point overwrites a dead operand array of that point (a further outer-domain array is allocated only if the product has more outputs than operand forms of more than one block). The working arrays of a product are allocated at its start and freed at its end: in scheme (a) one accumulator of `NB` elements; in scheme (b) one array of `NB` elements for each operand and each output of the product.
* Stage D, products above one block. The entries of the half-gcd matrices and the operands `a`, `b` of `apply_inv` have several blocks at the top levels of the recursion. `apply_inv` forms `c = r22 a - r12 b` and `d = r11 b - r21 a`, a bilinear form with two outputs, each the sum of two products. The forms of the four entries are made first; when the matrix is not needed again, the coefficient array of an entry is freed as soon as it is transformed. The blocks of `a` and `b` are transformed one at a time as the slots advance and pass through a sliding window of `kR + 1` blocks for each of the two operands (`kR` is the largest number of blocks of an entry): a slot meets at most `kR` consecutive blocks of an operand, and the block after the slot is transformed before the slot is placed; a block that leaves the window is freed, and every block is transformed once, as the cost counts it. The slots are formed in order, each with the accumulator, inverse transformed and placed. The outputs `c` and `d` are written over `a` and `b` when those arrays belong to the node and have `nres` elements (the placement of slot `s` writes the blocks `s` and `s + 1` of the output, which are already transformed), otherwise into arrays of `nres` elements of their own. In scheme (b) the forms of the four entries and of `a` and `b` (outer-domain arrays; the outputs of the outer points overwrite the forms of `a` and `b`) and the working arrays are held together while the outer points are multiplied, and then freed; the outputs are written over `a` and `b` or into arrays of their own as above. The exact `c` and `d` have fewer than `nres` coefficients (the high coefficients cancel, 4.4), so slots that start at or beyond `nres` are not formed. The matrix product (`mat_mul`) of the half-gcd is the same bilinear form with four outputs, each the sum of two products. The forms of one factor are held whole and those of the other factor one row (or column) at a time, in whichever of the two orders holds fewer blocks, and each row forms its two outputs into arrays of their own length; the coefficient arrays of both factors are freed as soon as they are transformed. In scheme (b) the forms of all eight entries and the working arrays are held together while the outer points are multiplied; the four outputs are allocated when the operand arrays that are dead have been freed. The Newton division (`divrem_fast`) holds, besides the arrays of its caller, the arrays of the normal sequence (the Newton division is not run on it, 4.4.1 item 4) and the forms and working arrays of its largest block product, in the scheme in which that product is charged. All other products of stage D, and the Newton products below `3 * 2^32` points, are as in 4.3 and 4.4.
* Scheme (c), chunked outer transform (`P` chunks). The outer length `n2` is the one of scheme (b) (the smallest `2^a` or `3 * 2^a` that is at least `max(s1 + 2, ns + 1 - s0)`). If `P` divides `n2` and `Q = n2 / P` is of the form `2^a` or `3 * 2^a`, the outer points `o = j1 + P * j2` (`0 <= j1 < P`, `0 <= j2 < Q`) are handled in `P` chunks, chunk `j1` holding the `Q` points with that `j1`; otherwise the product uses one chunk (`P = 1`). The operands stay in coefficient form: nothing is copied into an outer-domain array. Let `w` be a primitive `n2`-th root of unity and `x_i` the blocks of an operand (`k` of them, `B` positions each; zero beyond `k`). Chunk `j1` is assembled from the blocks: for every `i2 < Q` the array `z_(i2) = sum over i = i2 + Q i1 < k of w^(i j1) x_i`, by one call of the kernel `ocp` (`z = c x`, charge `5 + 7 B`) for the first block of the sum and one call of `oax` (`z += c x`, `5 + 10 B`) for each further block (the last block over its own positions only), the weight `c` being the entry `(i j1) mod n2` of a table of the `n2 + 1` powers of `w` (3 operations per entry, built at the start of the product), and by one call of `ozf` (`z = 0`, `3 + 4 B`) for an `i2` that no block reaches, and for the positions of the last block's array beyond the last coefficient when that block starts its array (the chunk arrays are taken from the pool, whose memory holds the data of earlier arrays); each call is charged `30` more (the two block addresses, the exponent `i j1 mod n2` with the reduction, the table address, call and return). The `Q` arrays are then transformed with the `Q`-point transform across the arrays (root `w^P`; the twiddle table of `Q` entries at 3 operations each, `Q/3` calls of `ob3` when 3 divides `Q`, `Q/2` calls of `ob2` in each radix-2 layer; `ob3` is charged `7 + 24 B`, `ob2` `5 + 13 B`, plus 10 per call), after which array `j2` is `sum over i of w^(i (j1 + P j2)) x_i`, the outer-domain array of the point `o = j1 + P j2`. From there each point is treated as in the outer-transform scheme: the inner transform (`NB` points) of the arrays of its operands (made at every use, charged for every point of every operand of more than one block, including the persistent operands `MU` and `g` of stage C), the pointwise products, the inverse inner transform and the fold of the upper `B` positions with the `o`-th power of `w`. The `Q` folded arrays of the chunk are transformed back with the `Q`-point transform (root `w^(-P)`), and for every output piece `s` of the window (`s = s0 .. min(s1, ns - 1) + 1`, the `tc` pieces) the piece is accumulated, `acc_s += w^(-j1 s) U_(s mod Q)`, by one call of `ocp` in the first chunk and `oax` in the others (charged `1` more per call: the weight is the table entry `n2 - ((j1 s) mod n2)`). The sum over the chunks is the piece `s` multiplied by `n2`; the factor `1/n2` is applied by the placement. A product that is the quotient estimate, the remainder or a stage-C step computes its pieces into accumulators of `tc B` elements and places them into the destination afterwards; a product of a division (6.3) accumulates the pieces of the window directly into the output array of the division, so that it has no accumulator (the calls then run only over the positions of the window). Because the operands are in coefficient form for the whole product, every operand array and every chunk form is charged where it is used; no spectrum or outer-domain form is stored between products.
* Choice. At this r stage C uses `P = 4` chunks (stage D: 4.4.1, item 6): each block product uses scheme (a) or scheme (c), whichever has the smaller charge, as a function of the lengths and the window only; scheme (b) is not used. The number of chunks is a constant of the algorithm for each r, fixed before the run; it was chosen by comparing the scores of Appendix E at these pairs (stage C, stage D): (4, 16). The pair used has the least score of them.
* Stage D in scheme (c). `apply_inv`: the coefficient arrays of the four entries, of `a` and of `b` stay live while the chunks are processed; the arrays of a chunk are the chunk forms of the six operands, the working arrays, the tables and two accumulators (`c` and `d`). After the last chunk the entries are freed when the matrix is not needed again; `c` and `d` are placed over `a` and `b` when those arrays belong to the node and have `nres` elements, otherwise into arrays of `nres` elements of their own; the accumulators are freed. `mat_mul`: the arrays of both factors stay live during the chunks (chunk forms of the eight entries, working arrays, tables, four accumulators); after the last chunk both factors are freed and the four outputs are placed into arrays of their own length, each accumulator being freed after its output is placed. Divisions: the arrays of 6.3, and the chunk forms, working arrays and tables of the largest block product of the division, the product accumulating its pieces directly into the output array of the division the arrays of the normal sequence (the Newton division is not run on it, 4.4.1 item 4), so that the division has no accumulator.
* Memory in scheme (c). A chunk form is `Q = n2 / P` arrays of `B` elements, so a product holds `Q B` elements for each operand of more than one block (and for each output beyond the number of such operands), where scheme (b) holds `n2 B`; the coefficient arrays of the operands and the accumulators are the other arrays of the product. The walk of Appendix E allocates and frees every array named here.
* Scaling (coefficient-domain stage C and the products of 4.5; for stage D see 4.4.1 item 6, where the scale is applied at the untwist). The factor `NB` of the unnormalised inverse transform is removed in the placement (one multiplication per coefficient placed); the stored reciprocal `MU` and the polynomial `g` are not rescaled.
* Memory. The arena of section 7 is computed by Appendix E, which runs the allocator of 4.2 on the allocations and frees of every array named in this section, in the order of the program (a block is `64 + 32 * slots` bytes rounded up to a multiple of 64; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order). For the products in scheme (c) the arrays are those of the two bullets on scheme (c) above. Stage C, products in scheme (a): the twiddle table, `g` and `F`; in the Newton iteration also `MU`, `Y` and the forms and working arrays of the product in progress; in the loop `F` and the persistent forms of `MU` and `g` (`g` itself is freed) and, in a step, the form of `R` (then of `T1`, then of `q`), `T1` (then `q`) and the working arrays of the product in progress, in a shift by `x` the work array of the regeneration of `g`; at the end `g` is regenerated while the persistent form of `g` is still live. Stage D: the arrays of the nodes of the half-gcd, with in `apply_inv` and `mat_mul` the forms, the window and the working arrays described above, and in a division the quotient of two coefficients and the remainder only (6.3: on the normal sequence every quotient has degree 1, so the Newton division never runs). The truncated second call of a node reads the top coefficients of `d` and `e` in place (no array); the second `apply_inv` at the calls of the Euclid driver and the two copies of the returned remainders are counted with the node. In scheme (b) a form is `n2` outer-domain arrays of `B` elements, so the scheme holds `n2 * B` elements for each operand of more than one block. The twiddle table is the one of the transform of `3 * 2^32` points (`2^31` elements, `ntt_init(32)`).
* Cost. The charges are those of 4.2 applied to these operations: each block transform and each inverse transform with the kernels and pass structure of the transform of `3 * 2^32` points, each pointwise product `NB` times the per-point charge of the bilinear form of 4.4, each placement as stated above. Appendix E (`stage_cd.py`) expands stages C and D with these rules and asserts the totals.

The three kernels of scheme (c), from `ntt_kern.h` (`LD(n)` and `ST(n)` are charged `2 n` operations, `CTL(n)` `n`, `fp_mul` and `fp_add` one each; the charges `5 + 7 cnt`, `5 + 10 cnt` and `3 + 4 cnt` of the text above are the constants `OCP`, `OAX` and `OZF` of Appendix E; the model parses them from this text and asserts the equality):

```c
static void ocp(fp *z, const fp *x, const fp *w, size_t cnt) {
    fp u; fp wr = *w; LD(1); CTL(3);              /* weight into a register; entry, loop set-up and exit */
    for (size_t grp = 0; grp < cnt; grp++) {
        u = x[grp]; LD(1); fp_mul(&u, &u, &wr);
        z[grp] = u; ST(1); CTL(2);
    }
}
static void oax(fp *z, const fp *x, const fp *w, size_t cnt) {
    fp u, v; fp wr = *w; LD(1); CTL(3);
    for (size_t grp = 0; grp < cnt; grp++) {
        u = x[grp]; LD(1); v = z[grp]; LD(1); fp_mul(&u, &u, &wr); fp_add(&v, &v, &u);
        z[grp] = v; ST(1); CTL(2);
    }
}
static void ozf(fp *z, size_t cnt) {
    fp zr = {{0, 0, 0, 0}}; CTL(3);
    for (size_t grp = 0; grp < cnt; grp++) {
        z[grp] = zr; ST(1); CTL(2);
    }
}
```

### 4.6 Stage C in the value domain (this entry; the method of bradcush 1aa56884, its proof section 4.6)

In this entry stage C is not the coefficient-domain squaring of 4.3 and 4.5: it is the value-domain powering of bradcush's entry 1aa56884 (proof section 4.6 there, credited in the submission note), re-implemented and charged in this entry's cost model (`powx_vd` in Appendix E). The residue is held by its values on two sets of `n1` points. One modular squaring is a Montgomery reduction whose only non-pointwise work is two changes of point set (extensions). No product of polynomials, no `MU` and no quotient is formed in the loop. Sections 4.3 and 4.5 still define the transforms, the kernels and the Newton reciprocal that the set-up below uses.

**Points.** Here `h = 2^32` and `K` is the number of cosets of each point set (not the number of centres of 4.1). `H` is the subgroup of order `h` of `F_p^*`, with generator `omega = 5^((p-1)/h)`, which has order `h` because 5 is a non-square. Put `u_k = 5^k`, `C_k = u_k H` and `n_k = u_k^h = z^k` with `z = 5^h`. `p - 1 = 2^32 * 3 * 463 * q1 * q2` with `q1 = 539,204,044,132,271,846,773` prime, and `z^((p-1)/q1) != 1`, so the order of `z` is at least `q1 > 2K`. Hence the nodes `z^k` (`k < 2K`) are distinct and the cosets `C_k` are pairwise disjoint (`C_j = C_k` if and only if `z^(k-j) = 1`). Our script `zorder_check.py` (standard library) checks these three facts: `q1` is prime by a deterministic Miller-Rabin test with the bases up to 41 (valid for `n < 3.3 * 10^24`), `z^((p-1)/q1) != 1`, and `5^((p-1)/2) != 1`; all three hold. At r = 17: `m = 5,960,464,477,539,062`, `K = ceil((m + 1)/h) = 1,387,779`, `n1 = K h = 5,960,465,419,075,584 = m + 941,536,522`. Put `O1 = C_0 u ... u C_(K-1)` and `O2 = C_K u ... u C_(2K-1)`, `M(Y) = prod_(k<K) (Y - z^k)` and `P1(X) = M(X^h)`. `P1` has degree `n1`, is squarefree, has root set exactly `O1`, and on a coset `C_k` with `k >= K` it is the nonzero constant `M(n_k)`.

**Representation.** A polynomial `f` of degree `< n1` is determined by its values on `O1`, and also by its values on `O2`. Write `f = sum_(j<h) X^j F_j(X^h)` with `deg F_j < K`. Then `f mod (X^h - n_k) = sum_j F_j(n_k) X^j`, so the values of `f` on `C_k` are the transform of size `h` of `(u_k^j F_j(n_k))_j`. Each array holds the values coset by coset, in the output order of the inner transform. The inner transform is the transform of `h` points of 4.2 (one row of radix-2 passes, in place on the coset).

**Lemma 4.6 (the step).** Let `g` be monic of degree `m` with `g(x) != 0` on `O1`. Let `R~` have degree `<= m`, and let `u0` be the polynomial of degree `< n1` with `u0(x) = -R~(x)^2 / g(x)` on `O1`. Then `W = (R~^2 + u0 g) / P1` is a polynomial of degree `<= m - 1`, and `W = R~^2 P1^(-1) mod g`. On `C_k` with `k >= K`, its values are `(R~(x)^2 + u0(x) g(x)) / M(n_k)`. *Proof.* `R~^2 + u0 g` vanishes on the `n1` distinct roots of the squarefree `P1`, so `P1` divides it. Its degree is at most `max(2m, n1 - 1 + m) = n1 + m - 1` because `n1 >= m + 1`, so `deg W <= m - 1`. Modulo `g`, `W P1 = R~^2`, and `P1` is invertible modulo `g` because `g` has no root in `O1`. The values follow from `P1(x) = M(n_k)` on `C_k`. QED. So the invariant `R~_i = S^(e_i) P1 mod g` passes from step to step with `R~' = X^b W` (`e_(i+1) = 2 e_i + b`, `deg R~' <= m`). The same argument with `R~` in place of `R~^2` leaves the Montgomery form (step 7).

**Lemma 4.7 (extension).** Let `f` have degree `< n1`, with its values on `O1` given. The inverse inner transform of each coset gives `h u_k^j F_j(n_k)`. Fix a position `j`, write `F = F_j`, and put `s_i = F(z^i) z^(-i) / M'(z^i)` and `kappa(e) = 1/(z^e - 1)` for `1 <= e <= 2K - 1`. Then `F(z^(K+t)) = M(z^(K+t)) sum_(i<K) s_i kappa(K + t - i)` for `t < K`. *Proof.* `deg F < K`, so `F` is the Lagrange interpolant of its values at the `K` distinct nodes, and `z^(K+t) - z^i = z^i (z^(K+t-i) - 1)` with `1 <= K + t - i <= 2K - 1`. QED. The direction `O2 -> O1` is the same with the nodes `z^(K+i)`. The sum is a cyclic convolution of length `Lx = 3 * 2^20 >= 2K` with a fixed kernel, and no index wraps.

**The stage** (the eight steps of 1aa56884, with our parameters at r = 17). The exponent `E = (p-1)/2` starts from `S^v` with `v = 2^50`, a multiple of `h` below `m` (`VSHIFT = 2`: two more squaring steps and a shorter reciprocal), and runs `203` steps, `45` of them with `b = 1`.
1. *Barrett start:* the reciprocal of the reversed `g` modulo `X^ell`, `ell = 1,125,900,848,379,147`, by the Newton iteration of 4.3 with the products of 4.5. Then `q = floor(X^v P1 / g)` by one product (`Kq = 262,145` rows).
2. *`g` on `O1` and on `O2`* by the chirp evaluation of section 3 (one convolution of length `Le = 2^22 >= 3K - 1` per position) and `2K` forward inner transforms.
3. *`R~_0` on `O2`:* `q` evaluated at the nodes of `O2` (`Lq = 2^21`), then `R2 := u_k^v M(n_k) - R2 * G2` pointwise. This gives the values of `X^v P1 - q g = X^v P1 mod g`.
4. *`R~_0` on `O1`:* an extension `O2 -> O1` (lemma 4.7).
5. *`-1/g` on `O1`* by Montgomery's batch inversion per coset. A zero prefix product means `g` vanishes on `O1`, and the trial ABORTs as in 4.4.1 item 4 (allocator reset, ledger row 'ABORT reset') after a prefix of the charged work; the probability is below `2^-148.2` (9.2(g)).
6. *The loop*, for each bit `b`: `R1 := R1^2 G1` (`u0` on `O1`); the extension `O1 -> O2`; `R2 := x^b (R2^2 + R1 G2) / M(n_k)`; the extension `O2 -> O1`. By lemma 4.6 the invariant holds after every step.
7. *Leaving the Montgomery form:* `R1 := R1 G1`, the extension `O1 -> O2`, `R2 := (R2 + R1 G2) / M(n_k)`. `R2` now holds `R = S^E mod g` (degree `< m`).
8. *Coefficient form for stage D:* `R2` and `g` are interpolated in place (inverse inner transforms, then two chirp correlations of length `Lx` per position), each into two pieces, the coefficients `[0, cut)` and `[cut, l)` with `cut = 4,470,352,285,532,160`, which the top node of stage D frees early (4.4.1, step 5).

**Charges** (Appendix E, `powx_vd`; the split by component is recomputed from the same functions, and the total is the row C that `stage_cd.py` prints and asserts):

| component | operations |
|---|---:|
| inner transform of one coset (forward / inverse, without the call of 10) | 449,396,745,182 / 465,144,958,609 |
| geometric phase of one extension (340.352 per element of `n1`) | 2,028,655,133,279,680,048 |
| one extension with its `2K` inner transforms | 3,297,836,904,461,132,495 |
| one loop step, `b = 0` / `b = 1` | 6,719,353,466,434,696,774 / 6,743,195,328,110,999,110 |
| tables: `30 K` constants, the `omega` table, the kernel spectra | 300,344,270,639 |
| Newton reciprocal (step 1, with its allocations) | 10,870,841,496,979,886,133 |
| product for `q` (step 1) | 2,717,908,717,561,621,467 |
| evaluation of `g` (step 2, geometric part) | 2,902,096,994,273,621,550 |
| `2K` forward inner transforms of `g` (step 2) | 1,247,326,731,299,943,812 |
| step 3 | 2,094,656,886,452,137,510 |
| step 4 (one extension) | 3,297,836,904,461,132,495 |
| step 5 (batch inversion) | 87,916,868,646,449,249 |
| step 6, the loop: 203 steps (45 with `b = 1`) | 1,365,101,637,461,677,050,242 |
| step 7 | 3,409,595,631,135,413,091 |
| step 8 (two interpolations) | 9,305,167,698,457,844,202 |
| allocations, exponent scan, zero fills, end of stage | 10,200,587,620 |
| stage C of one trial, with the stage bookkeeping of 1,000 (ledger row C) | 1,401,034,985,701,489,959,010 |

The inner transform of a coset matches 1aa56884's published r = 21 charge to the operation (`h` is the same at every r). Our geometric phase charges more per element (the row kernels of 4.2 instead of a register-blocked outer kernel). With the pieces of 4.4.1 every coset access of a pass also selects the base of its piece (a comparison and a branch, 2 operations), included in the figures above. Every charge depends only on `m` and the exponent, not on the coefficients.

**Memory.** The loop holds `R1`, `R2`, `G1` and the array of `g` (which holds `g` on `O2` during the loop and `g` in coefficient form at the exit): four arrays of `n1` elements. It also holds the tables and the group buffer of `VCNT = 2^10` rows of `Lmax = Le = 2^22` elements (the longest kernel), and one transform row of `Lmax` elements. The live peak of stage C is `3.0000` arrays of `n1` above its entry , plus the array of `g` from stage A. Section 7 walks these allocations with the rest of the trial.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: worst-case operation count (primitive operations; `C(17) = 573`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, the trial loop and the allocator reset after an ABORT (charged in every trial); `T_off` = the offline bound of section 6.2. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 2`, and `time_log2 = ceil_5(log2(N_max / 573))`.

Every stage is charged by the rules of section 4.2 where it executes. Section 6.1 compares the same counting with the instrumented totals of our executed entries at r = 3, 4, 5. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(32-1)` elements (`ntt_init(32)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 17,179,887,292 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,382 |
| B (per trial) | `925186` cosets of `6,442,450,944` points, each point with two evaluations of `F` (at `c + s` and `c - s`) at `C(17) = 573` operations each, the loop work around them, `925186` inverse transforms of size `6,442,450,944`, the geometric solve of the cosets (two correlations of length `2,097,152` per position), the normalisation | 16,824,333,175,932,967,600 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain (section 4.6): the Barrett start (Newton reciprocal and the product for `q`), the evaluations of `g` and `q`, the batch inversion, `203` steps (45 with `b = 1`), each two pointwise passes and two extensions, the exit and the two interpolations; expanded in Appendix E | 1,401,034,985,701,489,959,010 |
| D (per trial) | half-gcd of `(g, R - 1)` (sections 4.4, 4.4.1), charged for the normal remainder sequence with the quotient and return tests; any other sequence ends the trial after a prefix of this work (section 6.3); expanded in Appendix E | 1,286,177,092,539,484,062,135 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16` (below) | 166,079,773 |
| F (per trial) | square root, back-map (below) | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 573 + 32` | 12,492 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| ABORT reset (per trial) | the reset of the allocator when a test of stage D (quotient, return or window) or the zero test of stage C (4.6 step 5) fails and the trial ends (section 6.3): the 47 free-list heads (classes 7 to 53), the end of the slab area, the two ends of the pool and the header of its free middle block; at most 1,000, charged in every trial | 1,000 |
| plan_invN misses | one per distinct plan size (36 sizes) | 111,204 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 2 * T_trial + T_off` | **5,408,072,822,851,330,654,318** |

The rows C and D are not asserted: Appendix E (`stage_cd.py`) expands them from the transform sizes, the Newton levels, the squaring steps and the half-gcd levels, with the kernel charges of section 4.2, and prints and asserts the two values 1,401,034,985,701,489,959,010 and 1,286,177,092,539,484,062,135.

`N_max = 5,408,072,822,851,330,654,318` operations `= 8,231,465,483,791,979,686.94` units, `log2(N_max / 573) = 63.033213242357846`, claimed as `63.03322` (rounded up at five decimals).

Stage B charges each of the `11,920,930,838,151,168` evaluations of `F` as one reduced permutation, `C(17) = 216 + 21 * 17 = 573` operations, although a line evaluation is a strict subset of the work of a reference permutation; the loop work around the evaluations is charged on top (section 3).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the isolation loop until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 31, the zero test of the shift (5, and at most 2 for the replacement of a zero draw by 1) and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because the memory-access charge adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `2,640` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = 2,594,979`, of which `pow_half` is 2,471,032, the Taylor shift 11,700 and the two gcds 54,395 each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + 64 * R(16) + 114 = 166,079,773`.

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`.

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.1 Ledger recomputation and validation

The sum of section 6 is recomputed by the following script (standard library only).

```python
from math import log2, ceil
K, C = 2, 573
fixed = [17179887292, 4910, 111204, 5644, 3384436]   # init, setup, plan_invN misses, stage H, stage I
trial = [1382, 16824333175932967600, 1401034985701489959010, 1286177092539484062135, 166079773, 47012, 12492, 12, 1000]   # stages A, B, C, D, E (cap), F, G, main, ABORT reset
offline = 1000000
N = sum(fixed) + K * sum(trial) + offline
print('N =', format(N, ','))
print('units =', round(N / C, 1))
print('time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))
```

Comparison of the counting with the instrumented totals of our executed entries (algorithmic totals; the executed runs at r = 3, 4, 5 had fixed centres and a different stage A, and their thread charges are excluded): the count is above the measured total in every row, and its heap peak equals the measured heap peak at r = 3 and r = 5 and is 64 bytes below it at r = 4. The executed programs at r = 3, 4, 5 ran the second call of 4.4 on the whole reduced pair and stage C in coefficient form, so this comparison counts that algorithm (computed with the switches of the earlier coefficient-domain model; not part of the Appendix E listing).

| run | counted total | measured total | counted - measured | slack (bits) | counted heap peak | measured heap peak |
|---|---:|---:|---:|---:|---:|---:|
| r = 3, earlier program (fixed centre) | 410,937,818,567 | 409,369,056,359 | 1,568,762,208 | 0.00552 | 244,745,792 | 244,745,792 |
| r = 4, earlier program (fixed centre) | 3,993,660,556,174 | 3,977,289,295,772 | 16,371,260,402 | 0.00593 | 1,072,730,560 | 1,072,730,624 |
| r = 5, earlier program (fixed centre) | 9,217,469,769,975 | 9,171,678,989,504 | 45,790,780,471 | 0.00718 | 4,759,669,952 | 4,759,669,952 |

### 6.2 Offline derivation of the literals (preprocessing)

The algorithm uses constants that are derived from the organizer's constants and from `p` offline: the 192 round constants and 9 MDS entries in Montgomery form, `R^2 mod p`, `R mod p`, `2^65` and `5^q` in Montgomery form, the exponents `q`, `(q+1)/2`, `(p-1)/2`, `p - 2` and the integer `e = (4(p-1)+1)/5`. There is no search and no choice: each literal is the value of one closed formula in the organizer's constants. The Montgomery form of a constant `x` is `x * 2^256 mod p`, one modular multiplication plus parsing 64 hexadecimal digits; `5^q` is a square-and-multiply of 221 squarings and at most 221 multiplications; the exponents are shifts and subtractions of `p`. Each literal costs at most 4,000 word operations, there are at most 250 literals: 1,000,000 operations in all. This bound is inside `N_max` and is the declared `preprocessing_log2 = 20` (`2^20 = 1,048,576 >= 1,000,000`). The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry e6dcb600)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c, R_c - 1)`: every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centering division of a node, the division of each repetition of the outer loop, each step of the base case) tests that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); (c) the window test of 4.4.1 item 3 (2 tests, 2 operations each); a zero remainder inside hgcd or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state after the twiddle table (1,000 operations, charged in every trial) and the next centre is drawn. Lemma (prefix; e6dcb600, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each call splits at k1 = ceil(k/2) and, with every quotient of degree 1, every degree in the tree is fixed by m and the number of quotients so far and the parameters of the second call and of the outer loop are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's hgcd calls and divisions produce has degree at least 94 (n >= 193), so a gcd of degree at most 94, and so every gcd of degree at most DMAX, first appears in the classical Euclid below degree 192, after a prefix of the degree-0 work. A zero remainder anywhere earlier (gcd degree above 94, a failed trial anyway) ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2(g)). Appendix E (`stage_cd.py`) prints, for `r = 17`, the charge of stage D for the normal sequence with the tests, `1,286,177,092,539,484,062,135`, and asserts it.

## 7. Memory

Three terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 399,216 bytes of code, 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages): 5,250,444 bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (the second trial repeats the first from the same state: a trial frees every array but the twiddle table, and the simulation checks that the pool is back to that state). `python3 stage_cd.py` of Appendix E records every allocation and free of the trial in the order of the program (the twiddle table, stage A, stage B, stage C, stage D; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order), checks that these events reproduce the live-set walk of every stage (bytes in use, peak, live blocks), and runs the allocator on them. By the prefix lemma of section 6.3 every size in the sequence is a function of `m` and of the shape of the recursion on the normal sequence (and the block counts of the products), so the sequence is the same for every input. The two-ended pool takes the blocks of more than 2^45 bytes and is simulated address by address (two lists in address order, the low one from the bottom and the high one, for the statements marked `# pool:H`, from the top; the first free block that fits on the request's side is cut from the side nearest its end; a free merges with its free neighbours and with the unused middle); its capacity is the largest sum of the extents of the two ends over the trial, `762,939,573,641,675,136` bytes (after stage C `762,939,573,641,675,136`, after stage D `762,939,573,641,675,136`), plus 128 bytes so that the unused middle is always at least 128 bytes. The live-set peak of the same sequence is `762,940,056,647,814,656` bytes and the arena is `1.00147` times it: the blocks that die first are taken from the top and the long-lived ones from the bottom, so the holes left by freed blocks are small. The slab classes take the blocks of at most 2^45 bytes (a block of at most `2^j` bytes gets a slot of `2^j` bytes; the free list of the class first, else a new slot from the end of the slab area), so the slab area is the sum over the classes of the peak number of live blocks of the class times `2^j`: `1,119,990,103,446,400` bytes (Appendix E prints the peaks per class). Stages E to I hold at most 16 live arrays of at most 17 elements (16 slots of 1,024 bytes), and the allocator keeps 47 free-list heads (classes 7 to 53) and the end of the slab area (48 words, 384 bytes): `16,896` bytes with a margin of 128. The arena is `764,059,563,745,138,560` bytes (the three terms, rounded up to 64 bytes), in the stage with the highest pool address, C. The peaks of the live set per stage (twiddle table, `g`, `F` and the live set of the stage; the arena above is larger): A 190,734,962,129,895,616; B 381,469,855,540,314,368; C 762,940,056,647,814,656; D 721,616,155,584,940,992; stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The walk of stage D is the walk of the normal remainder sequence (6.3) with the pieces and windows of 4.4.1: every array of stage D has the length the normal sequence gives it, and a trial with any other sequence ends (ABORT) after a prefix of these allocations, so the walk bounds every trial. The largest transform has `3 * 2^32` points and uses roots of unity of order 3 and `2^32` (`p - 1` is divisible by 3 and by `2^32`); products that would need a longer transform are computed by blocks (section 4.5). The largest buffers are those of stage C (section 4.6: `R1`, `R2`, `G1` and the array of `g`, `n1 = 5,960,465,419,075,584` elements each, the tables and the group buffer; the Newton phase of its set-up holds three arrays of `ell` elements and the forms of one product) and those of stage D (4.4, 4.4.1).

(c) A stack bound of 65,536 bytes.

Total: (a) + (b) + (c) = `764,059,563,750,454,540` bytes `= 2^59.40646`, claimed as `memory_log2_bytes = 59.407` (rounded up at three decimals). The memory penalty is `max(0, 59.407 - 20) = 39.407`. The offline derivation of section 6.2 is a closed formula per constant; its memory is bounded by 1,024 bytes, inside the figure above. The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init".

## 8. What is provided

* The algebraic derivation (sections 2-3), the algorithm and its worst-case charges (4, 6, 7), the premise `H-GEOM-w1` with its reduction to explicit constants (section 9), the isolation lemma with proof (9.4), and the evidence, labelled as evidence (section 10).
* The claim is the worst-case count of the algorithm, `memory_log2_bytes` its footprint, and a success probability that follows from the premises `H-GEOM-w1` and `H-NORMAL`. The cost claim is in the model of section 4.2.
* No certificates (the certificate manifest is empty); the experiments are those of 10.2 and 10.5.1.
## 9. Success probability and the premises `H-GEOM-w1` and `H-NORMAL`

### 9.1 The premise

Notation. `p` is the Pallas prime, `D = 5^23`, and `F` is the fixed polynomial of section 2.3 at r = 17 (degree `D`, leading coefficient `f_D(0) != 0`). Put
`G(c, t) = (F(c + t) - F(c - t)) / (2 t)` in `F_p[c, t]`, a polynomial of total degree `D - 1` (section 3: `G(c, t) = g_c(t^2)`). For `c` in `F_p` let `k(c)` be the number of nonzero squares `S = t^2` with `G(c, t) = 0`; this is `deg G_c` of section 3. Let `O` be the set of triples `(c, s_1, s_2)` with `G(c, s_1) = G(c, s_2) = 0`, `s_1^2 != s_2^2` and `s_1 s_2 != 0`; `N_off = #O(F_p)`, and `w` is the main-term constant of its count (for a curve with `w` absolutely irreducible components over `F_p`, `N_off ~ w p`).

**Premise `H-GEOM-w1`.** Let `N*` be the number of points `(c, t)` of `G = 0` over `F_p` with `t != 0`, and `N_off` the number of points `(c, s_1, s_2)` over `F_p` with `G(c, s_1) = G(c, s_2) = 0`, `s_1^2 != s_2^2` and `s_1 s_2 != 0`. Then `N* / p >= 1 - eps` and `N_off / p <= w (1 + eps)`, with `w = 1` and `eps = 0.21`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r17-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2), the polynomial `F` of section 2.3; centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:** it concerns this `F`, not every polynomial of degree `D`: it is false for permutation polynomials, in particular for every pure composition of maps `x -> a x^5 + b` (`p = 2 mod 5`, so those maps are bijective), and it is not implied by a statement about components over the algebraic closure alone (`F(X) = X^3` over `F_101`: `(F(X) - F(Y)) / (X - Y)` splits into two conjugate lines over `F_(101^2)`, the curve has no off-diagonal rational point, and `k` is zero for every `c`). The explicit constants of 9.2 apply for every r >= 13 as stated, with no genus bound: the Weil majorant of the second moment (Grok job 138) exceeds the main term from r = 13, so the premise is stated as the count statement itself, which Grok job 139 measures on toy copies (10.3).

What the premise does not contain: no random-polynomial model, no independence of different centres (they are independent because each draw uses distinct fresh random words), no statement about the number of roots beyond the two moments of 9.2.

### 9.2 The reduction to explicit constants, and the success bound

For `c` uniform in `F_p` write `E[.]` for the mean over `c`.

(a) *Squares.* For `t != 0` the values `t` and `-t` give the same `S = t^2` and different points `(c, t)`, so `E[k] = N* / (2p)` with `N* = #{ (c, t) : t != 0, G(c, t) = 0 }`.

(b) *First moment.* By the premise `N* >= (1 - eps) p`, so `E[k] = N* / (2p) >= 1/2 - e_1` with `e_1 = eps / 2`; `e_1 = 1.050e-01` at r = 17. No genus bound is used.

(c) *Second moment.* `k(k-1)` counts ordered pairs of distinct usable squares; each pair lifts to 4 points `(s_1, s_2)` by independent signs, and `s_1^2 != s_2^2`, `s_1 s_2 != 0` define `O`. So `E[k(k-1)] = N_off / (4p) <= w (1 + eps) / 4 = w/4 + e_2` with `e_2 = w eps / 4`; `e_2 = 5.250e-02` at r = 17. (The bound of the premise has the form of the weakest count statement that keeps the success bound at 0.39: Grok job 138, `N*^2 >= q_* p (2 N* + N_off)`; the relative form used here, with one `eps` on both counts, is a sufficient condition for it.)

(d) *Cauchy-Schwarz.* `(E[k])^2 = (E[k 1_(k >= 1)])^2 <= E[k^2] P(k >= 1)` and `E[k^2] = E[k] + E[k(k-1)]`, so `P(k >= 1) >= a^2 / (a + b)` with `a = E[k]` and `b = E[k(k-1)]`. The right side increases in `a` and decreases in `b`, so its minimum over `a >= 1/2 - e_1`, `b <= w/4 + e_2` is at the corner: `P(k >= 1) >= (1/2 - e_1)^2 / (1/2 - e_1 + w/4 + e_2) = 0.2236917563`.

(e) *The cap `DMAX`.* `k >= DMAX + 1` implies `k(k-1) >= (DMAX+1) DMAX = 272`, so by Markov `P(k > DMAX) <= (w/4 + e_2) / 272 = 0.0011121324`. Therefore, for `c` uniform, the event `E_c : 1 <= k(c) <= DMAX` has probability at least `0.2225796239` by this route; the entry uses the larger bound of (e').

(e') *A sharper bound from the same two moments (gta6rp, entry c1364311, 9.2(e') there).* For every integer `k >= 0`, `1_(1 <= k <= DMAX) >= k - k(k-1)/2`: the right side is `k (3 - k) / 2`, which is 0, 1, 1, 0 at `k = 0, 1, 2, 3` and negative for `k >= 4`, while the left side is 1 for `1 <= k <= DMAX` and 0 otherwise (`DMAX = 16 >= 3`). Taking means over `c`, `P(1 <= k <= DMAX) >= E[k] - E[k(k-1)]/2 >= (1/2 - e_1) - (w/4 + e_2)/2 = 0.2437500000`. No tail term is needed, because the right side is already nonpositive beyond `k = 3`. This bound exceeds the Cauchy-Schwarz bound exactly when `E[k] > E[k(k-1)]` at the corner (`a > b` in (d)); at r = 17 it is the larger one (0.2437500000 against 0.2225796239), and the entry uses `q = 0.24375`. With the count premise it reads `3/8 - 5 eps/8`, and two moments alone cannot give more for one centre: the distribution `P(k = 0) = 121/160`, `P(k = 1) = 37/400`, `P(k = 2) = 121/800` has `E[k] = 0.395` and `E[k(k-1)] = 0.3025` exactly and `P(k >= 1) = 0.24375`.

(f) *Centres and isolation.* The algorithm draws its centres `c_1, ..., c_K` from fresh random words by the rule of 4.1.1; each is within statistical distance `eps_coin < 2^-128` of uniform (the exact value is 1.574e-39 (2^-128.90)), and the draws are independent. If `E_(c_t)` holds, the isolation of stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48` over words that are fresh for that stage (lemma 9.4). A trial with `E_(c_t)`, `N_(c_t)`, not `Z_(c_t)` (see (g)) and a successful isolation ends in a verified collision (sections 2-5). Therefore

`P[no collision in K trials] <= (1 - q)^K + K (eps_coin + eps_iso)`,

for an algorithm without the ABORT and the zero test (delta = delta_C = 0) this form gives

`P[success] >= 1 - (1 - q)^K - K (eps_coin + eps_iso) = 0.428085937`, with `q = 0.24375` from (e'), `K = 2`, `w = 1`, before the allowances of (g), which give the claimed 0.41286. The bound of this algorithm is (g).

The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 17 enters it. The arithmetic of (b)-(f) is recomputed with exact rationals by the script of Appendix D, which prints every number used here. The Cauchy-Schwarz route of (d) without the cap tail gives 0.397345511 for two centres; the linear bound of (e') needs no tail, so dropping the cap leaves 0.428085937.

(g) *The ABORT of stage D (`H-NORMAL`) and the zero test of stage C.* For a centre `c` let `N_c` be the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient of degree 1, section 6.3); by the premise `H-NORMAL` (9.5), `P(not N_c) <= delta = 0.01` for `c` uniform. Let `Z_c` be the event that `g_c` vanishes at a point of the set `O1` of the value-domain stage C (its zero test, section 4.6, ends the trial): for each of the `n1` points `x` of `O1`, `g_c(x)` (before normalisation) is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so it has at most `D - 1` roots, and each residue is drawn with probability at most `4/2^256` (4.1.1); hence `P(Z_c) <= delta_C = n1 (D - 1) 4 / 2^256 = 2.455e-45 (2^-148.2)`, proved, no premise. If `E_(c_t)` and `N_(c_t)` hold and `Z_(c_t)` does not, stages C and D run to their end and return `G = gcd(g_c, R_c - 1)`; a trial with `E_(c_t)`, `N_(c_t)`, not `Z_(c_t)`, and a successful isolation ends in a verified collision. For `c` uniform `P(E_c and N_c and not Z_c) >= q - delta - delta_C`, so the bound of (f) becomes

`P[success] >= 1 - (1 - q + delta + delta_C)^K - K (eps_coin + eps_iso) = 0.412860937 >= 0.41286`

(`q = 0.24375`, `delta = 0.01`, `K = 2`; exact rationals, Appendix D). This is bradcush's form (entry 1aa56884, 9.2(f) there) with gta6rp's allowance `delta = 0.01` (entry c1364311). The bound stays at least 0.39 for every `delta <= 0.0247`, above the stated 0.01. With the Cauchy-Schwarz `q = 0.22257` of (e) the same `delta` would give 0.379953995, below 0.39; the bound of (e') is what leaves room for `delta`.

### 9.3 The parameter w

With the count premise and `w = 1`: the worst corner `N*/p = 1 - eps`, `N_off/p = 1 + eps` gives `q(eps) = (1 - eps)^2 / (3 - eps)` for the Cauchy-Schwarz ratio, decreasing in `eps`; `q(eps) >= 0.22369` at `eps = 0.21`. Without the cap tail the largest `eps` with `1 - (1 - q)^2 >= 0.39` is 0.2197 (Grok job 138; 0.3676 for three centres), and with the tail of 9.2(e) it is 0.2174; with the linear bound of 9.2(e'), `q(eps) = 3/8 - 5 eps/8`, it is 0.2496, and 0.2336 with the allowance `delta = 0.01` of 9.2(g). The smallest good fraction `q'` (the probability of `E_c`) for which `K` centres give 0.39 is 0.39000 for K=1, 0.21898 for K=2, 0.15191 for K=3 and 0.11625 for K=4 (the terms `K (eps_coin + eps_iso)` are below `10^-14`); with the submitted `K = 2` the good fraction can be smaller than `q = 0.24375` by the factor `0.939` (down to `0.22898`) with `delta = 0.01` (`0.898`, `q' = 0.21898`, with `delta = 0`); the allowances of 9.2(g) take it to `q - 0.01 - delta_C`, above `q'` before the bound falls below 0.39. The time bound is `T_fixed + K T_trial` with `T_fixed` much smaller than `T_trial`, so `K'` centres instead of `K` cost about `log2(K'/K)` more in `time_log2`.

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - S3)/2^256 = 1/2 - 7.869e-40` (`S3` of 4.1.1) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `S3` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - S3)/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`, computed exactly in Appendix D. This is a proved bound under the random words, not a premise and not a sample.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries e6dcb600 and 1aa56884, with the allowance and the organizer-run tests of gta6rp's entry c1364311)

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 5,960,464,477,539,062`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.01` (`2^-6.64`).

Four fields (as in claim.json). **Role:** score-critical for the success probability only. The time and memory bounds hold for every sequence: stage D is charged for the normal sequence, every division tests its quotient and every call its return, and on any other case the trial ends after a prefix of the charged work (6.3). **Scope:** the pairs `(g_c, R_c - 1)` of the target `poseidon-orchard-r17-prefix-v1`, `c` uniform on `F_p`; nothing is claimed for other round counts. **Extrapolation and evidence:** for a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-148.2`. That bound does not transfer directly, because the coefficients of `R_c` have degree about `p` in those of `g_c`; the premise asserts far less than random-pair behaviour, an abnormality probability of at most `delta = 0.01`, which is all the bound of 9.2(g) uses (every `delta <= 0.0247` keeps it at least 0.39). Measured support, organizer-run (10.5.1): the experiments `euclid-normal-n2-t256`, `euclid-normal-n3-t24` and `euclid-normal-n4-t2` compute the complete sequence of `(g_c, R_c - 1)` for this construction on the truncations `F_2`, `F_3`, `F_4` of the digest polynomial (10.3; `m = 12`, `62`, `312`) at 256, 24 and 2 organizer-seeded centres, and return a witness pair exactly when the sequence is normal; the prediction is that every computed sequence is normal. Our runs of the same program: 1,066 sequences at `m = 12`, `62` and `312`, every quotient of degree 1 (10.5.1). Reported by our earlier entries, not organizer-run (10.5): the complete sequences on the sibling targets with `r' = 0` and `r' = 1` partial rounds (`m = 7,812` and `39,062`), every quotient of degree 1 in all 10 runs. **Limitations:** not verified at r = 17, which would need the computation itself; an algebraic relation between `g_c` and `R_c` that forces a principal subresultant coefficient to vanish for many centres would invalidate the premise, and none is known. The tests reach `m = 312` (the sibling runs `m = 39,062`), far below `m = 5,960,464,477,539,062`: they test the construction, not its scale. Normality is computed inside the submitted program; the runner checks only the returned witness pairs, so the tests are evidence under trusted execution of that program, which is printed in full in `experiments/exp_euclid.py`.

## 10. Evidence

This section is the evidence for the premise `H-GEOM-w1` and for the digest of the target. The executions of 10.1 and the computations of 10.3 are ours; the experiments of 10.2 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

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

Eight experiments of kind `python-message-pairs-v1` (five here, three in 10.5.1), run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The three Python sources are 56,878 bytes together (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r17-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run is the evidence: 256 of 256 trials returned a verified pair at r = 17, and the output was byte-identical on repetition. Our own earlier local run of the same events (plain Python on our machine) agreed: 256 of 256 trials.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 17: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining twenty-three rounds applied to `alpha + beta W` (`deg F = 5^23`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-GEOM-w1` is about (a root of `g_c`). In the picture of the premise, `F(c+s) - F(c-s) = 2 s g_c(s^2)` takes random-function values in `s` at these widths, so a trial returns a pair with probability `1-(1-2^-w)^150`: 0.9058, 0.4441, 0.1363 and 0.0360, that is about 232, 114, 35 and 9 of the 256 trials for `w` = 6, 8, 10, 12. A clustering of the roots of `g_c`, or a bias of the odd structure, would move these counts.

The intake report of the organizer's run records 232, 115, 36, 5 of the 256 trials with a verified pair for `w` = 6, 8, 10, 12 respectively, and byte-identical output on repetition. 

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-GEOM-w1` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.


**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B (program `certify.py` of job 136, printed in Appendix F). Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the attack's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 23`; the line and the first layers do not depend on r). The results (`certify_dep.py`, Appendix F):

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the attack line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-GEOM-w1` states `w = 1` at `N = 23`; this is the measured trend of the premise (`w = 1` at `N = 1, 2, 3` on the deployed constants, below), and it is our theory that the trend continues to `N = 23`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the attack's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend, and the premise states w = 1 at N = 23: this is our theory, the measured w = 1 at N = 1, 2, 3 continues, and the lemma gives w = 1 or w = 2 given (a) and 2-transitivity.

**Grok job 139 (the counts of the premise on toy copies).** Grok (xAI) computed `N*` and `N_off` exactly for width-3 Hades toy permutations over prime fields `p < 2^22` with `p mod 5 != 1` (S-box `x -> x^5`, uniformly random MDS matrix and round constants, the line `(L, 2L+1, 3L+5)`, `N` full rounds and `k` partial rounds, `deg F = 5^(N+k)` up to 1,953,125), by the fibre counts `N* = sum_y m_y (m_y - 1)` and `N_off = sum_c 4 r(c) (r(c) - 1)` (checked against brute force on the small cases), on 1,316 generic seeds with `p >= 1024` (the five degenerate seeds, where the degree drops, are excluded). The relative error `eps_obs = max(|N*/p - 1|, |N_off/p - w|/w)` with `w = 1` is `<= 0.2197` for every generic seed with `p >= 2053`, and the least-squares fit is `eps_obs = 3.10 / sqrt(p)` for a typical seed (`5.17 / sqrt(p)` for the maximum of four seeds), with no dependence on the degree (adding a term linear in `deg F` moves `R^2` from 0.5508 to 0.5509; the mean of `eps sqrt(p)` is 2.3 to 3.7 for every degree from 5 to 1,953,125); at `p = 2,097,169` the largest generic `eps_obs` is 0.0068. The premise of 9.1 states `eps = 0.21` for the target; this is our theory: the trend `eps ~ 3 / sqrt(p)` continues to `p` of 254 bits (where it is about `2^-126`) and to the polynomial `F` of this target, with the number of components `w = 1` of 10.3 above. The count statement is a sufficient condition for the success bound of 9.2 (Grok job 138).

### 10.4 Scope

One trial at r = 17 needs about 764059564 GB of live memory and about 40263254.1 times the work of an r = 6 trial. The claim rests on the premises `H-GEOM-w1` and `H-NORMAL` with the reduction of section 9.2; the executed centres at r = 3, 4, 5, the experiments of 10.2, the theorems and computations of 10.3 and the measurements of 10.5 are the evidence for it.
### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 17` applies the Euclidean algorithm to `g_c` (degree `m = 5,960,464,477,539,062`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. This section and 10.5.1 are the measured support of the premise `H-NORMAL` (9.5): stage D is charged for the normal remainder sequence and a trial ends at the first quotient of degree other than 1 (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (`sib_euclid.py`, centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at the gcd (degree 0, or degree 1 at the r' = 0 centres 2, 4, 7) after `m - deg gcd` divisions, and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core. The program `sib_euclid.py` is printed in Appendix F.

At `r = 17` the stages need about 764059564 GB and 5.4e21 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7.

### 10.5.1 Organizer-run normality tests (`experiments/exp_euclid.py`)

Three experiments of kind `python-message-pairs-v1`, declared in `experiments/manifest.json` and run by the organizer's runner: `euclid-normal-n2-t256`, `euclid-normal-n3-t24` and `euclid-normal-n4-t2` (program `experiments/exp_euclid.py`, 23,976 bytes, Python standard library only). The design follows gta6rp's organizer-run normality tests (entry c1364311, its 10.5.1); the program is our own. For each computed trial the program takes a centre `c` from the trial seed (the rule of `exp_line.py`) and builds, exactly over `F_p`, the polynomial `F_N(c + X)`: the `F_N` of 10.3 (start state `alpha + beta W` of the line `j = 0`, the S-box layers of rounds 2 and 3 (full), then 4 and 5 (partial, coordinate 0), the MDS after each; degree `5^N`). It checks `F_N` against direct iteration of those layers at `c + 1`, `c - 1`, `c + 2`, `c - 2` and the odd-part identity `2 x g(x^2) = F_N(c + x) - F_N(c - x)` at `x = 1, 2`; takes the monic odd part `g` (degree `m = (5^N - 1)/2`); computes `R = X^((p-1)/2) mod g` (253 squarings and 45 multiplications by `X`); and runs the complete Euclidean sequence of `(g, R - 1)` down to the zero remainder, recording the degree of every quotient. The sequence is normal when `deg(R - 1) = m - 1` and every quotient has degree 1, the condition of 6.3 and 9.5. A computed trial whose sequence is normal and whose checks pass returns two distinct canonical messages: the points `c + s` of the line, `s = 1, 2, ...`, are mapped back to `(nk, rho)` as in 10.2(b), and the first two whose digests of the selected target agree on the first 6 bits of the big-endian reading are returned. Among 65 points such a pair always exists, so a computed normal trial always returns a pair. Every other trial, and every trial past the first `T` (`T` = 256, 24, 2, the sandbox budget of 20 s), returns two nulls. The organizer-checked count of returned pairs therefore equals the number of computed trials found normal. The per-trial counts (`deg_r_minus_1`, `steps`, `abnormal_quotients`, `first_abnormal_step`, `max_quotient_degree`, `gcd_degree`) are reported as observations, which the runner labels untrusted. Prediction: 256, 24 and 2 of the 256 trials return a pair (`m = 12`, `62`, `312`). For `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2` (its layers come before the final full rounds), so the tests measure the same family of pairs as the premise; only the witness uses the digest at r = 17.

Our runs of the same program (2026-10-18, seeds of our own): in the runner's image `python:3.12.12-slim-bookworm` with one CPU and 128 MiB, 256, 24 and 2 sequences at `m = 12`, `62`, `312` in 4.6, 5.5 and 5.4 s of program time, byte-identical on repetition; with further seeds (Python 3.14), 512 more at `m = 12`, 256 at `m = 62` and 16 at `m = 312`. In all 1,066 sequences (768, 280 and 18) every quotient had degree 1, and the gcd had positive degree in 301, 117 and 7 of them (fractions 0.392, 0.418 and 0.389: a usable root of `g_c`, as `E[k]` about `1/2` in 9.2 predicts). What these tests show: under trusted execution, the construction's own pairs `(g_c, R_c - 1)` have normal remainder sequences at `m = 12` to `312`. What they do not show: anything at `m = 5,960,464,477,539,062`, where `H-NORMAL` remains a premise that asserts only `delta = 0.01`.

## 11. Appendix D: the premise arithmetic (`premise_numbers.py`)

`python3 premise_numbers.py` recomputes with exact rationals every number of 9.2(a)-(g) except 0.379953995; the 9.3 thresholds are not printed.

#### premise_numbers.py

```python
#!/usr/bin/env python3
"""Exact-rational recomputation of the success bound of proof.md section 9 for r = 17 (standard library only; prints every number used).
Premise H-GEOM-w gives E[k] >= 1/2 - e1 and E[k(k-1)] <= w/4 + e2 (Weil's bound replaced by the count premise of section 9.1; section 9.2).
Cauchy-Schwarz: P(k >= 1) >= E[k]^2 / (E[k] + E[k(k-1)]).  Markov on k(k-1): P(k >= DMAX+1) <= E[k(k-1)] / ((DMAX+1) DMAX).
q = P(1 <= k <= DMAX) >= the difference; K independent centres: 1 - (1-q)^K - K (eps_coin + eps_iso)."""
import math
from fractions import Fraction as Fr
from math import comb
P = (1 << 254) + 0x224698FC094CF91B992D30ED00000001
SP = 1 << 127                                   # floor(sqrt(P)) = 2^127, (2^127 + 1)^2 > P
R, DMAX, ZCAP = 17, 16, 64
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
# H-NORMAL (section 9.5): the allowance delta for an abnormal remainder sequence (the trial ends); LIN: the linear two-moment bound of 9.2(e') is used when it is the larger
DELTA = Fr(1, 100)
LIN = 1
# value-domain stage C (9.2(g)): g_c vanishes at a point of O1 (n1 points) with probability at most delta_C = n1 (D - 1) 4 / 2^256 (proved); n1 = 0 without it
N1 = 5960465419075584
DELTA_C = Fr(N1 * (D - 1) * 4, 1 << 256)
def fl5(x): return Fr(math.floor(x * 100000), 100000)       # floor at 5 decimals (exact)
def bound(w, K):
    e2 = e2_of(w)
    a = Fr(1, 2) - e1
    b = Fr(w, 4) + e2
    q_cs = a * a / (a + b)
    tail = b / ((DMAX + 1) * DMAX)
    q_lin = a - b / 2                  # 9.2(e'): 1_(1<=k<=DMAX) >= k - k(k-1)/2 for every integer k >= 0
    q = max(q_cs - tail, q_lin) if LIN else q_cs - tail
    succ = 1 - (1 - q + DELTA + DELTA_C) ** K - K * (eps_coin + eps_iso)
    return dict(e2=e2, a=a, b=b, q_cs=q_cs, tail=tail, q_lin=q_lin, q=q, succ=succ, succ_notail=1 - (1 - q_cs) ** K)
def succ_claim(q5, K, delta=None):
    """the bound with q floored at 5 decimals: 1 - (1 - q5 + delta + delta_C)^K - K (eps_coin + eps_iso)"""
    return 1 - (1 - q5 + (DELTA if delta is None else delta) + DELTA_C) ** K - K * (eps_coin + eps_iso)
def f(x, n=12): return '%.*f' % (n, float(x))
if __name__ == '__main__':
    W, K = 1, 2
    B = bound(W, K)
    print('D = 5^%d = %d, d = D - 1' % (6 + R, D))
    print('e1 = %.3e' % float(e1)); print('e2 = %s' % f(B['e2'], 10))
    print('E[k] >= 1/2 - e1; E[k(k-1)] <= w/4 + e2 = %s  (w = %d)' % (f(B['b'], 10), W))
    print('Cauchy-Schwarz: P(k >= 1) >= %s' % f(B['q_cs'], 10))
    print('Markov tail:    P(k > %d)  <= %s' % (DMAX, f(B['tail'], 10)))
    print('q = P(1 <= k <= %d) >= %s' % (DMAX, f(B['q'], 10)))
    print('K = %d without the tail (P(k >= 1) only): %s' % (K, f(B['succ_notail'], 10)))
    print('per-round good probability w >= %s = 1/2 - %.3e' % (f(wq, 20), float(Fr(1, 2) - wq)))
    print('eps_iso < %.3e (2^%.2f)   eps_coin < %.3e (2^%.2f)' % (float(eps_iso), math.log2(float(eps_iso)), float(eps_coin), math.log2(float(eps_coin))))
    if LIN or DELTA or DELTA_C:
        q5 = fl5(B['q'])
        print("linear bound (9.2(e')): q >= E[k] - E[k(k-1)]/2 = %s; Cauchy-Schwarz minus the tail: %s; q = the larger = %s, used as %s" % (f(B['q_lin'], 10), f(B['q_cs'] - B['tail'], 10), f(B['q'], 10), '%.5f' % q5))
        print('delta = %s (H-NORMAL), delta_C = n1 (D - 1) 4 / 2^256 = %.3e (2^%.1f), n1 = %d' % (f(DELTA, 2), float(DELTA_C), math.log2(DELTA_C) if DELTA_C else float('-inf'), N1))
        print('without the allowances: 1 - (1 - q)^%d - %d (eps_coin + eps_iso) = %s' % (K, K, f(1 - (1 - q5) ** K - K * (eps_coin + eps_iso), 12)))
        sc = succ_claim(q5, K)
        print('success >= 1 - (1 - q + delta + delta_C)^%d - %d (eps_coin + eps_iso) = %s' % (K, K, f(sc, 12)))
        r = 1 - Fr(39, 100) - K * (eps_coin + eps_iso); s = Fr(math.isqrt(r.numerator * 10 ** 40 // r.denominator), 10 ** 20)    # sqrt(r) rounded down
        print('the bound stays >= 0.39 for every delta <= %.4f' % (math.floor((s - (1 - q5) - DELTA_C) * 10000) / 10000))
        assert sc >= Fr(39, 100)
        print('claimed success_probability: %s (floor at 5 decimals)' % ('%.5f' % fl5(sc)))
    else:
        print('success >= 1 - (1-q)^%d - %d (eps_coin + eps_iso) = %s' % (K, K, f(B['succ'], 12)))
        print('claimed success_probability: %s (floor at 5 decimals)' % ('%.5f' % (int(B['succ'] * 100000) / 100000)))
    for w in (1, 2, 3):
        Bw = bound(w, 2)
        print('w = %d: P(k>=1) >= %s, q >= %s, K=2 success %s, K=3 success %s' % (w, f(Bw['q_cs'], 8), f(Bw['q'], 8), f(Bw['succ'], 8), f(bound(w, 3)['succ'], 8)))
```

## 12. Appendix E: the stage C and stage D totals (`stage_cd.py`)

`python3 stage_cd.py` expands the two rows of section 6 that carry almost all of the cost, 1,401,034,985,701,489,959,010 (stage C) and 1,286,177,092,539,484,062,135 (stage D), from the dimensions: the block transform (12,884,901,888 points) and the block products of 4.5, the Newton levels, the 203 squaring steps, the half-gcd levels, and the kernel charges of section 4.2. It prints both totals and asserts them. It also records the allocations and frees of one trial and runs the allocator of section 4.2 on them (the two-ended pool address by address, the slab classes by their peak counts): it prints the largest sum of the two ends of the pool after each stage, the slab area and the arena of section 7, and asserts them.

#### stage_cd.py

```python
#!/usr/bin/env python3
"""Appendix E: stage C and stage D of one trial at r = 17, expanded into their totals (standard library only).
Block mode: a product longer than 3*2^32 points is computed by blocks of 3*2^31 coefficients with transforms of 3*2^32 points (Grok job 140, scheme (a); see block products below).
Run:  python3 stage_cd.py      prints S_C = 1,401,034,985,701,489,959,010 and S_D = 1,286,177,092,539,484,062,135 and asserts them.

The inputs are the dimensions m = (5^23 - 1)/2 = 5,960,464,477,539,062 (degree of the modulus), the exponent (p-1)/2, and the charging rules of section 4.2,
which fix the per-kernel charges in the tables PASS and K3 below (butterfly 3 field operations or 2 when the twiddle is 1, twiddle load with
address, 8 operations per radix-3 leaf, loop control 3 per iteration and 2 on exit). Everything else is a finite recurrence:
  stage C: transform sizes 3*2^a >= 2m-1 and >= m+1; Newton levels l -> min(2l, m-1); the exponent: 203 squaring steps, 45 of them with the multiplication by S;
           the value-domain powering powx_vd (proof 4.6): Newton reciprocal, chirp evaluations, 203 steps (45 with b = 1), each two pointwise passes and two extensions;
  stage D: the outer loop of the Euclid driver, hgcd(k) with k halved (rounded up) until k <= 96, in each level the two recursive calls,
           apply_inv (one bilinear convolution), the division by a quotient of degree one, the 2x2 matrix product (conv_bilin_cost);
  below k <= 96 and n <= 192: classical division steps with quotient of two coefficients (divrem_naive).
`Tr` accumulates the operations and walks every allocation and free (an allocation is charged 121 + 13 (2 live + 1), a free 105; a block is 64 + 32 * slots rounded up to 64 bytes,
header included), with the live bytes and their peak, and the peak of the temporary arrays inside one call (the quotient and working arrays of every division, the workspaces of the
outer-transform scheme of the block products); it also records the events of the walk: every allocation and free with the identity of its block (the arrays given to a call by name).
The charge of stage D is the charge of the normal remainder sequence (proof.md 6.3) with the lean stage D of 4.4.1 (LEAND = 1), the quotient, return and window tests (the allocator reset after an ABORT is the separate ledger row of 1,000, proof.md 6); the script prints the stage totals and the
peak of the live set of each stage.
The arena is not the peak of the live set: the script runs the allocator of proof.md 4.2 on the events of one trial (init, A, B, C, D in the order of the program; sizes are functions of m and
the recursion shape only, the same for every input): the blocks of more than 2^BIG_EXP bytes are placed address by address by the two-ended pool (TwoEnd: two first-fit lists, the low one from
the bottom, the high one, for the statements marked `# pool:H`, from the top; split, coalescing, the largest sum of the two ends is its capacity), the other blocks by the slab classes (slot of 2^class bytes, one new slot from the end of the slab area when the free list of the class is empty: the area is the
sum over the classes of the peak number of live blocks times the slot), and it checks that the events reproduce the walk (walk_check)."""
import functools, math, collections, sys

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


BIG_EXP = 45                           # a block (header included) of more than 2^BIG_EXP bytes is served by the two-ended pool, every other block by its slab class (proof 4.2); a constant of the algorithm for each r
MIDPROD = 7                             # bit 1: the product (q g)[0..m-1] of the squaring step of stage C is formed cyclically (outer length for the window only) with the known high coefficients subtracted; bit 2: windows of the Newton products
QMIN = 7                               # smallest slab class: slots of 2^7 = 128 bytes
SLAB_ALLOC_OPS = 126                   # operations of an allocation from a slab class (proof 4.2): 125 plus the NEW_FP statement; below the charge 1 + 120 + 13 (2 L + 1) of every allocation
SLAB_FREE_OPS = 81                     # operations of a free of a slab block (proof 4.2); the charge of a free is FREE_OPS = 105
assert SLAB_ALLOC_OPS <= 1 + 120 + 13 and SLAB_FREE_OPS <= 105


class Slot(int):
    """an array of v slots together with the identity of its block, so that the walk is also the sequence of allocations and frees of the program (proof 4.2, 7)"""
    def __new__(cls, v, ident):
        o = int.__new__(cls, v); o.id = ident; return o


class Ctx:
    """identities of the blocks of one walk: the root walk, or one memoised call of hgcd (ids >= 0 local to the call, ids < 0 the arrays given to it)"""
    def __init__(self): self.n = 0


CTX_STACK = [Ctx()]


def new_id():
    c = CTX_STACK[-1]; i = c.n; c.n += 1; return i


class Rec:
    """the events of one memoised call of hgcd, recorded once: ('A', id, slots) allocation, ('F', id, slots) free, ('T', slots...) temporary arrays of one call (allocated in the
    order listed, freed in the reverse order), ('R', n, events) a self-contained group repeated n times, ('C', rec, base, args) a call of a recorded call"""
    def __init__(self, ev, nloc): self.ev = ev; self.nloc = nloc


POOL_H_LINES = frozenset(k + 1 for k, ln in enumerate(open(__file__, encoding='utf-8').read().split(chr(10))) if ln.rstrip().endswith('# pool:' + 'H'))


def _site(depth):
    """the list of the pool that serves the allocation statement that called: 1 (high list) for the statements marked `# pool:H` in this file, else 0 (low list); a constant of the statement"""
    f = sys._getframe(depth); return 1 if (f.f_code.co_filename == __file__ and f.f_lineno in POOL_H_LINES) else 0


class Tr:
    """sequential trace: ops, current live bytes/blocks relative to entry, peaks, and the events (allocations and frees) of the walk"""
    __slots__ = ('ops', 'cur', 'peak', 'cnt', 'pcnt', 'base', 'ev')

    def __init__(self, base=0):
        self.ops = 0; self.cur = 0; self.peak = 0; self.cnt = 0; self.pcnt = 0; self.base = base; self.ev = []

    def here(self): return self.base + self.cnt            # live blocks now (for sub-traces)

    def bump(self, slots):                                  # peak of a temporary array of `slots` elements that is live only inside one call (no operation charged)
        if slots > 0:
            self.peak = max(self.peak, self.cur + blk(slots)); self.pcnt = max(self.pcnt, self.cnt + 1)
            self.ev.append(('T', (int(slots),), _site(2)))

    def bump_blocks(self, slot_list):                       # peak of several temporary arrays live together inside one call (no operation charged)
        self.peak = max(self.peak, self.cur + sum(blk(x) for x in slot_list)); self.pcnt = max(self.pcnt, self.cnt + len(slot_list))
        if slot_list: self.ev.append(('T', tuple(int(x) for x in slot_list), _site(2)))

    def ctl(self, n): self.ops += n
    def ld(self, n): self.ops += 2 * n
    def st(self, n): self.ops += 2 * n
    def loopc(self, n): self.ops += 3 * n + 2

    def add(self, o):
        self.ops += o.ops
        self.peak = max(self.peak, self.cur + o.peak); self.pcnt = max(self.pcnt, self.cnt + o.pcnt)
        self.cur += o.cur; self.cnt += o.cnt
        self.ev.extend(o.ev)

    def new_fp(self, slots):
        slots = max(slots, 1) if slots else 1
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1) + ASTAT        # pos_leand: ASTAT = 0 except in the gate (1aa56884 allocator statistics)
        b = blk(slots); self.cur += b; self.cnt += 1
        self.peak = max(self.peak, self.cur); self.pcnt = max(self.pcnt, self.cnt)
        i = new_id(); self.ev.append(('A', i, int(slots), _site(2)))
        return Slot(slots, i)

    def free(self, slots):
        self.ops += FREE_OPS + ASTAT
        self.cur -= blk(slots); self.cnt -= 1
        self.ev.append(('F', slots.id, int(slots)))


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


BIGA = 32                              # v2(p-1) = 32: transform sizes 3*2^a exist in F_p for a <= 32 only; longer products use blocks (Grok job 140, scheme (a))
P32, _c32 = make_plan(3, BIGA)         # the block transform plan 3*2^32
NB = P32.N; HB = NB // 2               # block transform size NB = 3*2^32, block length HB = NB/2


def plan3_for_len(ln):
    c = 0
    for a in range(2, 96):                 # pos_vdc: 96 (r = 22 needs a = 64, 65)
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
        raise NotImplementedError('plain rows==1 forward copy is not used on the charged path')
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


def conv_core_row(Pl, mode):
    return 9 + fwd_passes(Pl, Pl.np - 1) + 4 + fused(Pl, mode) + inv_passes(Pl, Pl.np - 2) + 4


def conv_sq(Pl, ln, outlen):
    if Pl.a > BIGA: return conv_sq_big(ln, outlen)
    c = stageA_fwd(Pl, ln)
    c += Pl.rows * conv_core_row(Pl, 'sq') + 2
    return c + stageA_inv(Pl, outlen)


def mulc_otf_row(Pl, r, lenB, boff):
    c = 12 + stageA_row(Pl, r, lenB, boff)
    c += fwd_passes(Pl, Pl.np) + 2
    c += fwd_passes(Pl, Pl.np - 1) + fused(Pl, 'mul') + inv_passes(Pl, Pl.np - 2) + 4
    return c


def conv_mulc_otf(Pl, ln, lenB, boff, outlen, sub=False, cached=False, wrap=False):
    if Pl.a > BIGA: return conv_mulc_big(ln, lenB, (Pl.N - boff) % Pl.N, outlen, sub, cached, wrap)
    c = 2 + stageA_fwd(Pl, ln) + 4
    for r in range(3):
        c += mulc_otf_row(Pl, r, lenB, boff)
    return c + 2 + stageA_inv(Pl, outlen)


def pw_loop(n, mode):
    return for8(n) + n * (7 if mode == 0 else 10)


def conv_bilin_cost(Pl, nout, outlen, groups, hboff=0):
    if Pl.a > BIGA: return conv_bilin_big(nout, outlen, groups, (Pl.N - hboff) % Pl.N if hboff else 0)
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
                c += 6 + stageA_row(Pl, r, lh, hboff) + fwd_passes(Pl, Pl.np)
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


# ---------------------------------------------------------------- products longer than 3*2^32: block products (Grok job 140, scheme (a))
# A product of two polynomials is split into blocks of HB = 3*2^31 coefficients.  Every block is transformed once with the transform of size NB = 3*2^32
# (plan P32, the same kernels), the transforms of a slot s (the block pairs i + j = s) are multiplied pointwise and summed in the transform domain,
# every slot that meets the wanted output window is inverse transformed once and placed (overlap-added, scaled by 1/NB, or subtracted) into the output.
@functools.lru_cache(maxsize=None)
def big_fwd(bl):                       # forward transform of a block of bl coefficients (zero-padded to NB), all three rows
    return stageA_fwd(P32, bl) + 3 * fwd_passes(P32, P32.np)


@functools.lru_cache(maxsize=None)
def big_inv(outn):                     # inverse transform of one slot, the first outn coefficients are needed
    return 3 * inv_passes(P32, P32.np - 1) + stageA_inv(P32, outn)


def big_pw(mode):                      # one pointwise product over NB points: mode 0 write, 1 add, 2 subtract (as pw_loop)
    return 3 * pw_loop(P32.n, mode)


def nblk(l): return -(-l // HB)


def big_fwd_all(l):                    # all blocks of an operand of l coefficients (closed form)
    k = nblk(l)
    return (k - 1) * big_fwd(HB) + big_fwd(l - (k - 1) * HB)


def big_place(cnt, ov, sub):           # place a slot: cnt coefficients read from the accumulator, scaled by 1/NB, stored; ov of them added to, or all subtracted from, the output
    c = 3 * cnt + 2 + 2 * cnt + cnt + 2 * cnt            # loop control, load, scale multiplication, store
    return c + (cnt if sub else ov) * 3                   # load of the output value and the add or subtract


# ---------------------------------------------------------------- extension for r >= 12 (pricing model, 2026-10-17): closed-form slot sums and the outer-NTT block product (Grok job 140, j = 3)
OB2 = (5, 13)                            # kernel ob2 of ntt_kern.h, one radix-2 butterfly of two blocks over cnt positions: charge 5 + 13 cnt (parsed and asserted in Leaf)
OB3 = (7, 24)                            # kernel ob3, one twiddle-free radix-3 butterfly of three blocks over cnt positions: charge 7 + 24 cnt
OCALL = 10                               # one call of ob2 or ob3: the two or three block addresses (a multiplication and an addition each), the twiddle address, call and return
OCP = (5, 7)                             # kernel ocp of ntt_kern.h (chunked outer transform): z = w x over cnt positions, charge 5 + 7 cnt (parsed and asserted in Leaf)
OAX = (5, 10)                            # kernel oax: z += w x, charge 5 + 10 cnt
OZF = (3, 4)                             # kernel ozf: z = 0, charge 3 + 4 cnt
OCALL_C = 30                             # one call of ocp, oax or ozf in the assembly of a chunk: the two block addresses (a multiplication and an addition each), the exponent i * j1 mod n2 (a multiplication and a reduction of 20), the table address (a multiplication and an addition), call and return
OCALL_I = 31                             # one call of ocp or oax in the accumulation of a chunk: as OCALL_C and one subtraction (the weight w^(-e) is the table entry n2 - e)


def ontt_at(n, cnt):
    """one outer transform of n = 2^a or 3*2^a points at each of cnt positions: the twiddle table (n entries: a multiplication, a store
    and a control each), the radix-3 stage (n/3 calls of ob3) and a radix-2 layers (n/2 calls of ob2 each), every call charged in full"""
    c = 3 * n; q = n
    if n % 3 == 0:
        q = n // 3; c += q * (OCALL + OB3[0] + OB3[1] * cnt)
    lg = q.bit_length() - 1
    assert (1 << lg) == q, n
    return c + lg * (n // 2) * (OCALL + OB2[0] + OB2[1] * cnt)


def pad23(n):
    best = None
    for a in range(0, 33):
        for c in (1, 3):
            v = c << a
            if v >= n and (best is None or v < best): best = v
    assert best is not None, n
    return best


MODE_LOG = {}
OUTER_LIMIT = None                      # elements: outside the squaring loop of stage C a block product uses scheme (b) only if its workspace is at most this (None: no limit)
LIMIT_MULT = None                       # OUTER_LIMIT = LIMIT_MULT * m (None: no limit); a constant of the algorithm for each r (proof 4.5)
DIRECT_DIV = True                      # scheme (c) in a division: the chunks of a product are accumulated into the output array of the division itself (no separate accumulator); a constant of the algorithm
CHUNK_C = 4                          # scheme (c): number of chunks of the outer points of the block products of stage C (None: no scheme (c) in stage C); a constant of the algorithm for each r (proof 4.5)
CHUNK_D = 16                          # the same for the block products of stage D
SEQ_OUT = False                         # scheme (b) of apply_inv: the two outputs are formed one after the other, so that fewer operand forms are live together; a constant of the algorithm for each r (proof 4.5)


def set_outer_limit(m):
    global OUTER_LIMIT
    OUTER_LIMIT = None if LIMIT_MULT is None else LIMIT_MULT * m
    hgcd.cache_clear(); worst_div.cache_clear(); padded_division_full.cache_clear()
    if 'ld_ontt' in globals(): ld_ontt.cache_clear()        # pos_leand: the outer charge depends on LD_CONV


def chunk_req():
    """the number of chunks asked for the block products of the stage being evaluated (None: scheme (c) is not available there)"""
    return CHUNK_C if CTX['stage'] == 'C' else CHUNK_D if CTX['stage'] == 'D' else None


def ok23(q):
    while q % 2 == 0: q //= 2
    return q in (1, 3)
CTX = {'loop': False, 'seq': False, 'stage': None, 'direct': False}     # loop: True while the products of the squaring loop of stage C are evaluated (no limit applies to them); seq: the outputs of the bilinear form being evaluated (apply_inv) are formed one after the other in scheme (b)
PL = {}                                 # description of the last block product evaluated by conv_bilin_big: scheme, outer length, operand forms, working arrays


def copy_ops(l):                        # copy of l coefficients into the outer-domain array of an operand: a load, a store and the loop step per coefficient
    return 7 * l + 2


def fill_ops(l, n2):                    # the outer-domain form of an operand of l coefficients (n2 arrays of HB points): the copy of the l coefficients, then the zero fill of the n2 HB - l positions
    return copy_ops(l) + 5 * (n2 * HB - l) + 2   # beyond them (a store and the loop step per position): the form comes from the pool, which holds stale data (ruling 3476cad8)


def form_slots(l, mode, n2, pc=1):
    """slots of the transform-domain form of an operand of l coefficients: nblk(l) spectra of NB points (scheme (a), and an operand of one block in every scheme),
    or the n2 outer-domain arrays of HB points of scheme (b), or the n2 / pc arrays of HB points of the chunk of scheme (c)"""
    if mode == 'a' or nblk(l) == 1: return nblk(l) * NB
    return (n2 // pc) * HB


def prod_work(P, nout):
    """slots of the arrays that the block product described by P (a copy of PL) holds besides the forms of its operands and its outputs in coefficient form: the working
    arrays (scheme (a): one accumulator of NB points; scheme (b): one array of NB points per operand form at the current outer point and per output, and the table of the n2
    outer twiddles) and, in scheme (b), further outer-domain arrays for the outputs that have no dead operand form to overwrite (the output of an outer point overwrites a dead operand array of that point)"""
    if P['mode'] == 'a': return [NB]
    if P['mode'] == 'c':      # one chunk: Q arrays of HB points per output that has no dead operand form to overwrite, one array of NB points per operand form and output, the tables, the accumulators
        return [(P['n2'] // P['pc']) * HB] * max(0, nout - P['nf']) + [NB] * P['nwork'] + [P['n2'] + 1, P['n2'] // P['pc']] + list(P['acc'])
    return [P['n2'] * HB] * max(0, nout - P['nf']) + [NB] * P['nwork'] + [P['n2']]            # the last: the table of the n2 outer twiddles


def prod_arrays(P, ops, nout):
    """every transform-domain array live during the block product P: the form of each operand in ops (the operands that are not persistent) and prod_work"""
    if P['mode'] == 'c': ops = list(ops) + list(P['hc'])           # the cached operands have no persistent form in scheme (c): their chunk forms are made at each use
    return [form_slots(l, P['mode'], P['n2'], P.get('pc', 1)) for l in ops] + prod_work(P, nout)


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


def chunk_fill_ops(l, Q, pc):
    """assembly of the pc chunks of the outer-domain form of an operand of l coefficients (k = nblk(l) blocks): in every chunk each block is read once with the weight w^(i j1)
    (ocp for the blocks i < Q, which start the arrays, oax for the others; the last block has l - (k - 1) HB positions) and the Q - k arrays that no block reaches are zeroed (ozf)"""
    k = nblk(l); last = l - (k - 1) * HB
    nocp = min(k, Q); noax = k - nocp
    full = lambda ch_, n_: n_ * (OCALL_C + ch_[0] + ch_[1] * HB)
    c = full(OCP, nocp) + full(OAX, noax)
    if nocp == k:                                                 # the last block starts an array: its other HB - last positions are zeroed (ozf; the array comes from the pool, ruling 3476cad8)
        c -= OCP[1] * (HB - last)
        if last < HB: c += OCALL_C + OZF[0] + OZF[1] * (HB - last)
    else: c -= OAX[1] * (HB - last)
    if k < Q: c += (Q - k) * (OCALL_C + OZF[0] + OZF[1] * HB)
    return pc * c


def conv_bilin_big(nout, outlen, groups, ws=0, sub=False, shared=False, cached=False, wrap=False):
    """block version of conv_bilin_cost.  Returns (ops, eps) and describes the scheme used in PL.  Scheme (a) (all block pairs, closed form) or, when it is cheaper and, outside the
    squaring loop, its workspace is within OUTER_LIMIT, the outer-NTT scheme of Grok job 140 (j = 3).  cached: the H operands are persistent (stage C keeps the spectra, or the
    outer-domain arrays, of MU and g from one step to the next); scheme (a) does not transform them again, scheme (b) repeats the inner transform of every outer point of such
    an operand at each use (the persistent outer-domain array has HB elements per point, not NB)."""
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
    ops_ = []; hc_ = []
    for g in groups:
        if cached: hc_ += list(g['H'])
        else: ops_ += list(g['H'])
        if not shared: ops_ += list(g['S'])
    pw0, pw1 = big_pw(0), big_pw(1)
    # ---- scheme (a)
    ca = 2 + sum(big_fwd_all(l) for l in ops_)
    ninfo = []
    for k in range(nout):
        if not eps[k] or not prods[k]: continue
        s0, s1, we = window_slots(ws, outlen[k])
        stot = max(nblk(ls) + nblk(lh) - 1 for ls, lh in prods[k])
        A, B = s0, min(s1, stot - 1)
        ninfo.append((k, s0, s1, stot, we))
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
    # ---- outer scheme
    co = None; n2 = 0; wrapinfo = None
    nf = sum(1 for l in ops_ if nblk(l) > 1); nwork = len(ops_) + len(hc_) + nout
    extra_seq = 0                                                  # scheme (b), outputs one after the other (apply_inv): the operands of several outputs are transformed again for each further output
    if CTX['seq']:
        hm = sum(1 for g in groups for l in g['H'] if nblk(l) > 1)
        sk = [0] * nout
        for g in groups:
            for kind in ('H', 'S'):
                for i_, l in enumerate(g[kind]):
                    outs_ = {o for (si, hi_), (o, sg) in g['prod'].items() if o >= 0 and (hi_ if kind == 'H' else si) == i_}
                    if nblk(l) > 1 and len(outs_) > 1: extra_seq += len(outs_) - 1
                    if kind == 'S' and nblk(l) > 1:
                        for o in outs_: sk[o] += 1
        nf = hm + max(sk)                                          # operand forms live together: those of the H operands and those of the S operands of one output
    if ninfo and max(nblk(l) for l in ops_ + hc_) > 1:
        n2 = 1
        for (k, s0, s1, stot, we) in ninfo: n2 = max(n2, pad23(s1 + 2 if wrap else max(s1 + 2, stot + 1 - s0)))
        co = 2
        for l in ops_:
            if nblk(l) == 1: co += big_fwd(l)
            else: co += n2 * big_fwd(HB) + ontt_at(n2, HB) + fill_ops(l, n2)
        for l in hc_:
            if nblk(l) > 1: co += n2 * big_fwd(HB)             # the inner transform of every outer point of a persistent operand, at each use (a one-block operand is kept as its spectrum)
        co += extra_seq * n2 * big_fwd(HB)
        for (k, s0, s1, stot, we) in ninfo:
            npk = len(prods[k])
            co += n2 * (pw0 + (npk - 1) * pw1) + n2 * big_inv(NB - 1) + n2 * big_place(HB, HB, False) + ontt_at(n2, HB) + big_place(outlen[k], outlen[k], sub)
            if wrap:                                                   # cyclic mod x^(n2 HB) - 1: the upper half of the last slot is added to the first slot, and the known coefficients at positions >= n2 HB (the high half of R^2) are added back
                full = max(ls + lh - 1 for ls, lh in prods[k])
                wc = max(0, full - n2 * HB)
                co += big_place(HB, HB, False) + 10 * wc + 2
                wrapinfo = (n2 * HB, wc)
    # ---- chunked outer scheme (c): the outer points are processed in pc chunks (four-step split n2 = pc * Q); the operands stay in coefficient form, a chunk holds Q outer points
    cc_ = None; pcs = 1; accs = []; acck = []
    pc_req = chunk_req()
    if pc_req is not None and ninfo and max(nblk(l) for l in ops_ + hc_) > 1:
        pcs = pc_req if (n2 % pc_req == 0 and ok23(n2 // pc_req)) else 1
        Q = n2 // pcs
        cc_ = 2 + 3 * (n2 + 1)                                    # the table of the n2 + 1 outer twiddles
        for l in ops_ + hc_:
            if nblk(l) > 1: cc_ += n2 * big_fwd(HB) + chunk_fill_ops(l, Q, pcs) + pcs * ontt_at(Q, HB)
        for l in ops_:
            if nblk(l) == 1: cc_ += big_fwd(l)                    # an operand of one block: its spectrum, once
        for (k, s0, s1, stot, we) in ninfo:
            npk = len(prods[k])
            A_, B_ = s0, min(s1, stot - 1)
            tc = max(0, min(n2, B_ - A_ + 2))                     # the output blocks A..B + 1 (the high half of slot B goes to block B + 1)
            if not CTX['direct']: accs.append(tc * HB); acck.append(k)
            cc_ += n2 * (pw0 + (npk - 1) * pw1) + n2 * big_inv(NB - 1) + n2 * big_place(HB, HB, False) + pcs * ontt_at(Q, HB) + big_place(outlen[k], outlen[k], sub)
            if CTX['direct']:      # the pieces are accumulated into the destination array itself: only the positions of the window, the first chunk assigns (ocp), the others add (oax)
                cwin = lambda sp_: min((sp_ + 1) * HB, ws + outlen[k]) - max(sp_ * HB, ws)
                edges_ = sorted(set(range(A_, min(A_ + 5, A_ + tc))) | set(range(max(A_, A_ + tc - 5), A_ + tc)))
                for sp_ in edges_:
                    cw = cwin(sp_)
                    if cw > 0: cc_ += (OCALL_I + OCP[0] + OCP[1] * cw) + (pcs - 1) * (OCALL_I + OAX[0] + OAX[1] * cw)
                if tc > len(edges_):                                  # the pieces between the first five and the last five lie inside the window (asserted): HB positions each
                    assert cwin(A_ + 5) == HB and cwin(A_ + tc - 6) == HB, (A_, tc, ws, outlen[k])
                    cc_ += (tc - len(edges_)) * ((OCALL_I + OCP[0] + OCP[1] * HB) + (pcs - 1) * (OCALL_I + OAX[0] + OAX[1] * HB))
            else:
                cc_ += tc * (OCALL_I + OCP[0] + OCP[1] * HB) + (pcs - 1) * tc * (OCALL_I + OAX[0] + OAX[1] * HB)
    # 10-17 (ruling fb911c77 H-COST-OUTER): the outer transform is charged by its own kernels ob3 and ob2 (ontt_at), every call in full, integer charges only;
    # the scheme with the smaller charge is used, provided (outside the squaring loop) the workspace of scheme (b), max(operand forms live together, outputs) * n2 * HB + nwork * NB, is within OUTER_LIMIT.
    lim = None if CTX['loop'] else OUTER_LIMIT
    if pc_req is not None:
        use_c = cc_ is not None and cc_ < ca                      # a stage with chunks: scheme (a) or scheme (c), the smaller charge (no scheme (b))
        use_b = False
    else:
        use_c = False
        use_b = co is not None and co < ca and (lim is None or max(nf, 1 if CTX['seq'] else nout) * n2 * HB + nwork * NB <= lim)
    if use_c:
        nfc = sum(1 for l in ops_ + hc_ if nblk(l) > 1)
        PL.clear(); PL.update(seq=False, mode='c', n2=n2, pc=pcs, nf=nfc, nwork=len(ops_) + len(hc_) + nout, nout=nout, ops=tuple(ops_), hc=tuple(hc_), ca=ca, co=co, cc=cc_, acc=tuple(accs), acck=tuple(acck))
        MODE_LOG['chunk'] = MODE_LOG.get('chunk', 0) + 1
        return cc_, eps
    PL.clear(); PL.update(wrap=bool(wrap) and use_b, wrapinfo=wrapinfo if use_b else None, seq=bool(CTX['seq']) and use_b, mode='b' if use_b else 'a', n2=n2 if use_b else 0, nf=nf, nwork=nwork, nout=nout, ops=tuple(ops_), hc=tuple(hc_), ca=ca, co=co)
    if use_b:
        MODE_LOG['outer'] = MODE_LOG.get('outer', 0) + 1
        return co, eps
    MODE_LOG['a'] = MODE_LOG.get('a', 0) + 1
    return ca, eps


def conv_sq_big(ln, outlen):
    return conv_bilin_big(1, [outlen], [dict(H=[ln], S=[ln], prod={(0, 0): (0, 1)})], shared=True)[0] + 4


def conv_mulc_big(ln, lenB, ws, outlen, sub=False, cached=False, wrap=False):
    return conv_bilin_big(1, [outlen], [dict(H=[lenB], S=[ln], prod={(0, 0): (0, 1)})], ws, sub, False, cached, wrap)[0] + 6


def product_peak(T, Pl, nout=1):
    """the transform-domain arrays of the product just evaluated (Newton phase of stage C), allocated at its start and freed at its end"""
    arr = prod_arrays(PL, PL['ops'], nout) if Pl.a > BIGA else [Pl.n]       # a product that fits one transform: its transform row
    ids = [T.new_fp(x) for x in arr]  # pool:H
    for x in ids: T.free(x)


def persist_ops(l, P):
    """creation of the persistent form of a cached operand of l coefficients: its spectra (scheme (a), or one block), or the copy into the outer-domain array and the outer transform"""
    if nblk(l) == 1: return big_fwd(l)
    if P['mode'] == 'c': return 0                                 # scheme (c): the coefficient array itself is kept; its chunk forms are made at each use
    if P['mode'] == 'a': return big_fwd_all(l)
    return fill_ops(l, P['n2']) + ontt_at(P['n2'], HB)


def persist(T, l, P):
    """the persistent form of a cached operand of l coefficients: allocated, made from the coefficient array (with the table of the outer twiddles in scheme (b)); returns its slot"""
    sl = T.new_fp(form_slots(l, P['mode'], P['n2']))
    if P['mode'] == 'b' and nblk(l) > 1:
        tw = T.new_fp(P['n2']); T.free(tw)
    T.ops += persist_ops(l, P)
    return sl


def regen_ops(l, P, place):
    """regeneration of the l coefficients of g from its persistent form P.  Scheme (a) (and one block): the inverse transform of each block spectrum into one work array of NB points,
    block by block; for the shift by x (place = False) the factor 1/NB is folded into the multiplier (one multiplication), at the end of stage C (place = True) the block is placed with
    its scaling into the array of g.  Scheme (b): the inverse outer transform of the persistent array in place and its scaling by 1/n2 (a load, a multiplication, a store and the loop
    step per coefficient); for the shift the forward outer transform that restores the form follows; at the end of stage C the blocks are copied into the array of g"""
    k = nblk(l)
    if P['mode'] == 'a' or k == 1:
        last = l - (k - 1) * HB
        if place: return (k - 1) * (big_inv(HB) + big_place(HB, 0, False)) + big_inv(last) + big_place(last, 0, False) + 6 * k
        return (k - 1) * big_inv(HB) + big_inv(last) + 6 * k + 1
    return (1 if place else 2) * ontt_at(P['n2'], HB) + 8 * l + 2 + (copy_ops(l) if place else 0)


def regen_work(T, P, l):
    """allocation and free of the work array of a regeneration of g (one array of NB points, or the table of the n2 outer twiddles)"""
    x = T.new_fp(NB if (P['mode'] == 'a' or nblk(l) == 1) else P['n2']); T.free(x)  # pool:H


def chunk_phase(S, P, nout=1, hi=False, ha=None):
    """the arrays of a product of scheme (c) while its chunks are processed: the chunk forms of all operands, the working arrays, the tables and the accumulators; returns (the ids of
    the accumulators, a function that frees everything else).  The coefficient arrays of the operands are the caller's and stay live.  hi: the list (high = True) of the arrays other than
    the accumulators; ha: the list of the accumulators (None = hi)"""
    arr = prod_arrays(P, P['ops'], nout); na = len(P['acc']); nr = len(arr) - na
    ha = hi if ha is None else ha
    if hi: rest = [S.new_fp(x) for x in arr[:nr]]  # pool:H
    else: rest = [S.new_fp(x) for x in arr[:nr]]
    if ha: acc = [S.new_fp(x) for x in arr[nr:]]  # pool:H
    else: acc = [S.new_fp(x) for x in arr[nr:]]
    def done():
        for x in rest: S.free(x)
    return acc, done


def step_walk(base, m, Psq, Pq, Pg):
    """the arrays of one squaring step of the streamed schedule (proof 4.5), with every allocation and free charged: F holds R and receives the low half of R^2 and then the
    result; the persistent forms of MU and g are the caller's.  Psq, Pq, Pg describe the three products (copies of PL).  Returns the trace of one step (all arrays freed).
    A product of scheme (c) keeps its operand (R, T1, q) in coefficient form until its last chunk is processed, accumulates its output in the accumulators and places it afterwards."""
    S = Tr(base)
    if Psq['mode'] == 'c':
        acc, done = chunk_phase(S, Psq, hi=True, ha=False)           # the accumulators of the square R^2 (two operand-lengths, the largest arrays of the step) go to the low list, above F
        done()                                                        # R is dead after the last chunk: the low half of R^2 is placed into F
        sT1 = S.new_fp(m - 1)                                         # the high half of R^2  # pool:H
        for x in acc: S.free(x)
    else:
        fR = S.new_fp(form_slots(m, Psq['mode'], Psq['n2']))              # the form of R; F is free to receive the low half of R^2  # pool:H
        wk = [S.new_fp(x) for x in prod_work(Psq, 1)]  # pool:H
        sT1 = S.new_fp(m - 1)                                             # the high half of R^2  # pool:H
        for x in wk: S.free(x)
        S.free(fR)
    if Pq['mode'] == 'c':
        acc, done = chunk_phase(S, Pq, hi=True)
        done(); S.free(sT1)                                           # T1 is dead after the last chunk
        sq = S.new_fp(m - 1)                                          # the quotient estimate q  # pool:H
        for x in acc: S.free(x)
    else:
        fT = S.new_fp(form_slots(m - 1, Pq['mode'], Pq['n2']))            # the form of T1; T1 is free once it is transformed (kept until the end of the step when (q g) is formed cyclically)  # pool:H
        if not Pg.get('wrap'): S.free(sT1)
        wk = [S.new_fp(x) for x in prod_work(Pq, 1)]  # pool:H
        sq = S.new_fp(m - 1)                                              # the quotient estimate q  # pool:H
        for x in wk: S.free(x)
        S.free(fT)
    if Pg['mode'] == 'c':
        acc, done = chunk_phase(S, Pg, hi=True)
        done(); S.free(sq)                                            # q is dead after the last chunk; (q g)[0..m-1] is subtracted from F by the placement
        for x in acc: S.free(x)
    else:
        fq = S.new_fp(form_slots(m - 1, Pg['mode'], Pg['n2']))            # the form of q; q is free once it is transformed  # pool:H
        S.free(sq)
        wk = [S.new_fp(x) for x in prod_work(Pg, 1)]                      # (q g)[0..m-1] is subtracted from F by the placement  # pool:H
        for x in wk: S.free(x)
        S.free(fq)
        if Pg.get('wrap'): S.free(sT1)
    assert S.cur == 0 and S.cnt == 0
    return S


def ebit(E, i): return (E >> i) & 1


def powx_lean(m, b, E=PM1H, sg=None):
    """sg: the array g of the caller (stage C frees it after its form is made)"""
    CTX['stage'] = 'C'
    try: return powx_vd(m, b, E, sg) if vd_active(m) else powx_lean_(m, b, E, sg)
    finally: CTX['stage'] = None


def powx_lean_(m, b, E=PM1H, sg=None):
    T = Tr(b)
    PN, c1 = plan3_for_len(2 * m - 1); PNp, c2 = plan3_for_len(m + 1)
    T.ctl(c1 + c2)
    N, Np = PN.N, PNp.N
    BIG = PN.a > BIGA
    if BIG:
        assert PNp.a > BIGA
        # block mode, streamed (proof 4.5): g and F are the arrays of the caller (F holds the reversed g in the Newton phase and the state R in the loop); the Newton phase holds
        # MU (m-1) and the product buffer Y (m-1) besides them; the loop holds the persistent forms of MU and g and, per step, the arrays of step_walk
        sM = T.new_fp(m - 1); sY = T.new_fp(m - 1)  # pool:H
    else:
        sY = T.new_fp(N); sT = T.new_fp(PN.n); sM = T.new_fp(m - 1)
    # newton_lean
    L = m - 1
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
        if BIG:
            assert P1.a > BIGA or P1.N <= m - 1                      # a product that fits one transform uses Y (m-1 slots) as its transform buffer
            product_peak(T, P1)
        T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l                                       # pl_run MULC
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
        if BIG:
            assert P2.a > BIGA or P2.N <= m - 1                      # a product that fits one transform uses Y (m-1 slots) as its transform buffer
            product_peak(T, P2)
        T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)                                 # pl_run NEGMULC: mul + sub per element
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    T.ld(L); T.st(L); T.loopc(L // 2); T.ctl(2 * (L // 2))
    # prefix + scale
    T.ctl(plan_invN_ops(PN)); T.ctl(plan_invN_ops(PNp)); T.ops += 1
    T.ops += m - 1; T.ld(m - 1); T.st(m - 1); T.loopc(m - 1)
    gamma = N - (m - 2)
    if BIG:
        # the three products of a step, in the order of the step; the two cached operands (MU, g) are persistent
        CTX['loop'] = True
        try:
            sq_ops = conv_sq(PN, m, 2 * m - 1); Psq = dict(PL)
            q_ops = conv_mulc_otf(PN, m - 1, m - 1, gamma, m - 1, False, True); Pq = dict(PL)
            qg_ops = conv_mulc_otf(PNp, m - 1, m + 1, 0, m, True, True, bool(MIDPROD & 1)); Pg = dict(PL)
        finally:
            CTX['loop'] = False
        T.free(sY)                                            # the Newton phase is over: the persistent forms replace MU and the workspace
        keepM = Pq['mode'] == 'c' and nblk(m - 1) > 1         # scheme (c): MU and g stay in coefficient form (their chunk forms are made at each use, charged in the products)
        keepG = Pg['mode'] == 'c' and nblk(m + 1) > 1
        sPM = None if keepM else persist(T, m - 1, Pq)
        if not keepM: T.free(sM)
        sPG = None if keepG else persist(T, m + 1, Pg)
        if not keepG: T.free(sg)                              # g is freed: it is regenerated from its form for each shift by x and, at the end of stage C, for stage D
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
    if BIG:      # F holds R and receives the low half of R^2; T1 is read from its own array; q is placed into its array; (q g)[0..m-1] is subtracted from F by the placement
        S = step_walk(T.here(), m, Psq, Pq, Pg)
        step = sq_ops + 8 + q_ops + qg_ops + S.ops
    else:
        step = conv_sq(PN, m, 2 * m - 1) + 8
        step += for8(lim) + 7 * lim + for8(m - lim) + 4 * (m - lim) + for8(m - 1) + 4 * (m - 1)
        step += conv_mulc_otf(PN, m - 1, m - 1, gamma, m - 1) + conv_mulc_otf(PNp, m - 1, m + 1, 0, m)
        step += for8(m) + 7 * m
    step += 14 + 6
    mulx = 2 + for8(m - 1) + 8 * (m - 1) + 2 + 4
    nset = sum(ebit(E, b) for b in range(bit))
    if BIG and not keepG:      # each shift by x regenerates the coefficients of g from the persistent form (the work array of the regeneration is allocated and freed in the shift)
        Mw = Tr(T.here()); regen_work(Mw, Pg, m + 1); assert Mw.cur == 0
        mulx += Mw.ops + regen_ops(m + 1, Pg, False)
    T.ops += steps * step + nset * mulx
    if BIG:
        T.peak = max(T.peak, T.cur + S.peak); T.pcnt = max(T.pcnt, T.cnt + S.pcnt)
        if not keepG: T.peak = max(T.peak, T.cur + Mw.peak)
        T.ev.append(('R', steps, tuple(S.ev)))
        if not keepG: T.ev.append(('R', nset, tuple(Mw.ev)))      # every step and every shift allocates and frees its arrays: the group restores the allocator
    T.ops += 1 + m; T.ld(m); T.st(m); T.loopc(m)
    T.ctl(2 + 500)
    if BIG:      # the loop is over: MU's form is freed, g is regenerated into an array of its own for stage D, then its form is freed (scheme (c): MU is freed, g is the array it always was)
        if keepM: T.free(sM)
        else: T.free(sPM)
        if not keepG:
            sg2 = T.new_fp(m + 1); regen_work(T, Pg, m + 1); T.ops += regen_ops(m + 1, Pg, True)
            T.free(sPG)
        else: sg2 = sg                                          # scheme (c): g stayed the caller's array; it goes to stage D as it is
    else:
        T.free(sY); T.free(sT); T.free(sM)
    info = dict(steps=steps, nset=nset, PN=PN, PNp=PNp, step=step, mulx=mulx)
    if BIG: info.update(modes=(Psq['mode'], Pq['mode'], Pg['mode']), n2=(Psq['n2'], Pq['n2'], Pg['n2']), sg2=sg2)
    return T, info


# ---------------------------------------------------------------- stage C in the value domain (VDC = 1): pos_vdc pricing, the method of bradcush 1aa56884 (its proof 4.6), charged in this model's primitives
# The residue is held by its values on O1 = C_0 u ... u C_(K-1) and O2 = C_K u ... u C_(2K-1), C_k = 5^k H, H the subgroup of order h = 2^32, K = ceil((m+1)/h), n1 = K h >= m + 1
# (each of O1, O2 is the union of K cosets, n1 points).  A squaring step is two pointwise passes and two extensions (change of point set); an extension is an inner transform of h
# points per coset (one row of the passes of 4.2, in place) and, per inner position, one cyclic convolution over the coset index with a fixed kernel (Lagrange interpolation at the
# geometric nodes z^k, z = 5^h).  The convolutions of a group of VCNT positions run in a group buffer with one row of L elements per position (position-major: the copies into and out
# of it are strided, one address operation per element charged); each row is one cyclic convolution of L points with the stored spectrum of the kernel, charged by the row kernels of
# this model (conv_core_row: forward passes, the fused pass with the pointwise product by the stored spectrum, inverse passes; for L = 3 * 2^a with the radix-3 input and output
# stages stageA_fwd / stageA_inv, as conv_sq does).
VDC = 1              # stage C in the value domain (1) or the coefficient-domain squaring of 4.5 (0); a constant of the algorithm
VD_H = 1 << 32       # h: the order of the subgroup H; the inner transform of h points is one row of passes (plan rows = 1, a = 32), in place on a coset
VCNT = 1 << 10       # inner positions per group of the geometric phase
VSHIFT = 2           # the start monomial is S^v, v = (the largest power of two below m) >> VSHIFT, a multiple of h: VSHIFT more squaring steps, a shorter Newton reciprocal
VD_CALL = 10         # one call of an inner transform: the coset address (a multiplication and an addition), the plan and twiddle arguments, call and return
VD_ROW = 16          # one row of a group copy with a running factor: the factor and its step loaded (LD 2 = 4), the factor stored back (ST 1 = 2), two addresses (4), call, entry, exit (6)
VD_ROWC = 12         # one row of a group copy with a per-row constant: the constant loaded (2), two addresses (4), call, entry, exit (6)
VD_PWC = 14          # one coset of a pointwise pass: its constants loaded (1/M(n_k), u_k, the factor of the coset) and the addresses
VD_GROUP = 20        # one group of the geometric phase: its position offset, the buffer and table addresses, the calls
VD_SPLIT = 0         # pos_leand: g and R in two pieces: the base of a coset is selected (a comparison and a branch) at every coset access of a pass (2), else 0


def vd_active(m):
    """the value-domain stage C is used (VDC = 1) where it is defined: the start monomial v (the largest power of two below m, shifted by VSHIFT) is a multiple of h"""
    return bool(VDC) and m.bit_length() - 1 - VSHIFT >= VD_H.bit_length() - 1


def vd_plan(L):
    """the plan of a cyclic convolution of L = 2^a or 3 * 2^a points (a <= 32: the roots of unity exist in F_p)"""
    rows = 3 if L % 3 == 0 else 1
    a = (L // rows).bit_length() - 1
    Pl, c = make_plan(rows, a)
    assert Pl.N == L and a <= BIGA, L
    return Pl, c


def vd_inv1():
    """one field inversion (fp_inv): the power p - 2 and its control"""
    return powcost(PM2) + INV_CTL


def vd_dims(m, E=PM1H):
    """the dimensions of the value-domain stage C for the modulus degree m: K, n1, the convolution lengths, the start exponent v, the steps, the Barrett length ell"""
    h = VD_H; K = -(-(m + 1) // h); n1 = K * h
    assert n1 >= m + 1                                                     # O1 and O2 each hold n1 >= m + 1 points: a polynomial of degree <= m is determined by its values
    Lx = pad23(2 * K)                                                      # extensions and interpolations (indices <= 2K - 1 < Lx, no wrap into the outputs)
    Le = pad23(3 * K - 1) if 3 * K - 1 <= 3 << BIGA else None             # one chirp evaluation of g at the 2K nodes; None: two evaluations of K nodes at Lx
    top = 255; zc = 0
    while top > 0 and not ebit(E, top): top -= 1; zc += 1
    v = 1; bit = top; vb = 0
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1; vb += 1
    for _ in range(VSHIFT):
        assert ebit(E, bit) == 0
        v >>= 1; bit += 1
    assert v & (v - 1) == 0 and v % h == 0                                 # x^v = u_k^v on the coset C_k
    ell = v + n1 - m + 1                                                   # q = floor(X^v P1 / g) has ell = deg + 1 coefficients
    Kq = -(-ell // h); Lq = pad23(Kq + K - 1)
    return dict(h=h, K=K, n1=n1, Lx=Lx, Le=Le, v=v, steps=bit, top=top, zc=zc, vb=vb, ell=ell, Kq=Kq, Lq=Lq,
                nset=sum(ebit(E, i) for i in range(bit)))


def vd_gslots(m):
    """the array of g (stages A to D): n1 slots; the values of g on O2 are written into it in place (stage C, step 2) and it goes to stage D as g in coefficient form"""
    return vd_dims(m)['n1']


def vd_conv(Pl, kin, outlen):
    """one cyclic convolution of one position's row (kin live inputs) with a stored kernel spectrum: rows = 1: the zero fill of the other L - kin entries and the row kernels in place;
    rows = 3: the radix-3 input stage from the row into the transform buffer, the three row convolutions, the output stage back into the row (outlen outputs); 5: the position loop and address"""
    if Pl.rows == 1:
        z = Pl.N - kin
        return 5 + 2 * z + for8(z) + conv_core_row(Pl, 'mul')
    return 5 + stageA_fwd(Pl, kin) + 3 * conv_core_row(Pl, 'mul') + 2 + stageA_inv(Pl, outlen)


def vd_rows(cnt, rows, per, row_over):
    """rows of cnt elements copied between a coset array and the group buffer: per element `per` (running factor: a load, the multiplication by the factor, the multiplication of
    the factor by its step, a store, the strided address = 7; per-row constant: a load, a multiplication, a store, the strided address = 6), per row row_over, loops by the eight-element rule"""
    return rows * (row_over + VD_SPLIT + for8(cnt) + per * cnt) + 3 * rows + 2


def vd_phase(per_group):
    ng = VD_H // VCNT
    return ng * (VD_GROUP + per_group) + 3 * ng + 2


def vd_reset(rows):
    """the running factors of a phase set from their base table: per row a load and a store, the loop"""
    return 7 * rows + 2


def vd_ext(K, Px):
    """the geometric phase of one extension (O1 -> O2 or O2 -> O1): K rows in with their factors, one convolution per position, K rows out with their factors"""
    return 2 * vd_reset(K) + vd_phase(vd_rows(VCNT, K, 7, VD_ROW) + VCNT * vd_conv(Px, K, 2 * K) + vd_rows(VCNT, K, 7, VD_ROW))


def vd_eval(kin, kout, Pl):
    """chirp evaluation of kin coefficient rows at kout geometric nodes: rows in with a per-row constant, one convolution with the chirp per position, kout rows out with their factors"""
    return vd_reset(kout) + vd_phase(vd_rows(VCNT, kin, 6, VD_ROWC) + VCNT * vd_conv(Pl, kin, kin + kout - 1) + vd_rows(VCNT, kout, 7, VD_ROW))


def vd_interp(K, Px):
    """interpolation at K geometric nodes back to coefficient form: rows in with their factors, the chirp correlation, the K results moved with a per-index constant (two loads, a
    multiplication, a store), the correlation with the coefficients of M, rows out with a per-row constant"""
    mid = vd_conv(Px, K, 2 * K - 1) + 7 * K + for8(K) + 4 + vd_conv(Px, K, 2 * K)
    return vd_reset(K) + vd_phase(vd_rows(VCNT, K, 7, VD_ROW) + VCNT * mid + vd_rows(VCNT, K, 6, VD_ROWC))


def vd_inner(ncos, inv, PH):
    """ncos inner transforms of h points, one per coset, in place (the first pass may read another array: the same charges)"""
    one = inv_passes(PH, PH.np - 1) if inv else fwd_passes(PH, PH.np)
    return ncos * (one + VD_CALL + VD_SPLIT) + 3 * ncos + 2


def vd_pw(ncos, per):
    """a pointwise pass over ncos cosets of h values: per element `per`, per coset VD_PWC, loops by the eight-element rule"""
    return ncos * (VD_PWC + VD_SPLIT + for8(VD_H) + per * VD_H) + 3 * ncos + 2


def vd_batch_inv(ncos):
    """-1/g in place on ncos cosets (Montgomery's batch inversion): per coset the prefix products into the auxiliary array (a load, a multiplication, a store), one inversion and its
    zero test (a zero prefix ends the trial: g vanishes on O1), the backward pass (two loads, two multiplications, the negation, a store), 20 for the coset"""
    h = VD_H
    return ncos * (20 + VD_SPLIT + for8(h) + 5 * h + vd_inv1() + 2 + for8(h) + 9 * h) + 3 * ncos + 2


def vd_spectrum(Pl, nent):
    """a fixed kernel of L points: nent entries computed (each charged as one inversion and 20 operations), the rest zero (rows = 1: zero fill; rows = 3: the radix-3 input stage reads
    the nent entries only), the forward transform (all passes: the fused pass of vd_conv multiplies by it)"""
    c = nent * (vd_inv1() + 20) + 4
    if Pl.rows == 1:
        z = Pl.N - nent
        return c + 2 * z + for8(z) + fwd_passes(Pl, Pl.np)
    return c + stageA_fwd(Pl, nent) + 3 * fwd_passes(Pl, Pl.np)


VD = {}              # description of the last value-domain stage C (filled by powx_vd)


def powx_vd(m, b, E=PM1H, sg=None):
    """stage C in the value domain.  Entry: g in coefficient form in the caller's array sg of n1 slots (stage A; its slots above m are zeroed here).  Exit: R = S^E mod g in an array of
    n1 slots (the first allocation of the stage, at the low end) and g in coefficient form in sg; both go to stage D.  Returns (Tr, info)."""
    T = Tr(b)
    d = vd_dims(m, E)
    h, K, n1, ell, Kq = d['h'], d['K'], d['n1'], d['ell'], d['Kq']
    assert sg is not None and (sum(int(x) for x in sg) if isinstance(sg, tuple) else int(sg)) == n1
    PH, c0 = make_plan(1, BIGA); assert PH.N == h
    Px, c1 = vd_plan(d['Lx']); Pq, c2 = vd_plan(d['Lq'])
    Pe, c3 = vd_plan(d['Le']) if d['Le'] else (None, 0)
    T.ctl(c0 + c1 + c2 + c3)
    T.ctl(12 * d['zc'] + 25 * d['vb'] + 4 * VSHIFT)                        # the exponent: its leading bit, the start monomial, the shift
    # tables (per trial): 30 K constants (u_k, 1/u_k, the base factors of the copies, 1/M(n_k), u_k^v M(n_k), M'(z^k)^-1, M(z^(K+t)), M2'^-1, M2(z^t) z^-t, the chirp scales, the
    # coefficients mu_i of M), each charged as two inversions and 60 operations; the table of omega^i in transform order (h entries); the kernel spectra
    spec = [(Px, 2 * K), (Pq, Kq + K - 1), (Px, 2 * K - 1), (Px, K + 1)]   # extension kernel; chirp of the evaluation of q; chirp of the interpolation; the coefficients of M
    if Pe: spec.append((Pe, 3 * K - 1))                                   # chirp of the evaluation of g at the 2K nodes (one convolution of length Le)
    NTAB = 30 * K
    sTab = T.new_fp(NTAB + h + sum(P_.N for P_, _ in spec))
    T.ctl(NTAB * (2 * vd_inv1() + 60) + 10 * h + sum(vd_spectrum(P_, n_) for P_, n_ in spec))
    Lmax = max(P_.N for P_, _ in spec)
    sB1 = T.new_fp(VCNT * Lmax)                                           # the group buffer: one row of Lmax elements per position
    sBT = T.new_fp(Lmax) if any(P_.rows == 3 for P_, _ in spec) else None # the transform row of a convolution of 3 * 2^a points
    zg = n1 - (m + 1); T.st(zg); T.ctl(for8(zg))                          # the slots of g above its m + 1 coefficients are zeroed (the rows of g are read whole in step 2)
    sR2 = (T.new_fp(sg[0]), T.new_fp(sg[1])) if isinstance(sg, tuple) else T.new_fp(n1)       # R on O2 (pos_leand: two pieces as g), then R in coefficient form for stage D (allocated first: the bottom of the low end)
    sR1 = T.new_fp(n1)                                                    # q (its first ell elements) from step 1 to step 3, then R~ on O1 (or u0 on O1 / O2)
    # (1) Barrett start: the reciprocal of the reversed g modulo X^ell (Newton, the products of 4.5), then q = rev(rev(X^v P1) mod X^ell * reciprocal mod X^ell)
    sG = T.new_fp(ell)  # pool:H
    sM = T.new_fp(ell)  # pool:H
    sY = T.new_fp(ell)  # pool:H
    L = ell
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)                                # the reversed top ell coefficients of g
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
        assert P1.a > BIGA or P1.N <= L                                   # a product that fits one transform uses Y (ell slots) as its transform buffer
        if P1.a > BIGA: product_peak(T, P1)
        T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
        assert P2.a > BIGA or P2.N <= L
        if P2.a > BIGA: product_peak(T, P2)
        T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    T.free(sY); T.free(sG)
    sTt = T.new_fp(ell)  # pool:H
    T.st(ell); T.ctl(for8(ell)); T.ctl(Kq * (vd_inv1() + 30))              # rev(X^v P1) mod X^ell: zero fill, the Kq coefficients mu_i at the multiples of h
    PQ, c = plan3_for_len(2 * ell - 1); T.ctl(c)
    T.ctl(conv_mulc_otf(PQ, ell, ell, 0, ell))                            # q (reversed) into the first ell elements of R1, window [0, ell)
    if PQ.a > BIGA: product_peak(T, PQ)
    T.ctl(plan_invN_ops(PQ))
    T.free(sTt); T.free(sM)
    T.ld(ell); T.st(ell); T.loopc(ell // 2); T.ctl(2 * (ell // 2))          # reversal of q in place
    # (2) g on O1 (array G1) and on O2 (in place in the array of g): chirp evaluation of the K coefficient rows, the 2K forward inner transforms
    sG1 = T.new_fp(n1)
    if Pe: T.ctl(vd_eval(K, 2 * K, Pe))
    else: T.ctl(2 * vd_eval(K, K, Px))                                    # no length >= 3K - 1: the nodes of O1 and of O2 in two evaluations
    T.ctl(vd_inner(2 * K, False, PH))
    # (3) R~_0 = X^v P1 mod g on O2: q evaluated at the K nodes of O2 into R2, the forward inner transforms, R2 := u_k^v M(n_k) - R2 * G2 (8 per element)
    zq = Kq * h - ell; T.st(zq); T.ctl(for8(zq))                          # the tail of the last row of q in R1
    T.ctl(vd_eval(Kq, K, Pq) + vd_inner(K, False, PH) + vd_pw(K, 8))
    # (4) R~_0 on O1: inverse inner transforms of O2 reading R2 and writing R1, the extension O2 -> O1 in place on R1, the forward inner transforms
    ext = vd_inner(K, True, PH) + vd_ext(K, Px) + vd_inner(K, False, PH)
    T.ctl(ext)
    # (5) -1/g on O1, in place in G1 (auxiliary array of h elements); a zero prefix product ends the trial
    sAux = T.new_fp(h); T.ctl(vd_batch_inv(K)); T.free(sAux)
    # (6) the squaring loop, one step per bit b of E below the start: (i) R1 := R1^2 G1 (8); (ii) extension O1 -> O2 in place on R1; (iii) R2 := x^b (R2^2 + R1 G2) / M(n_k)
    # (12, 16 when b = 1: omega^i loaded, multiplied by u_k, the product by x); (iv) extension O2 -> O1 from R2 into R1; 20 for the step
    step0 = vd_pw(K, 8) + ext + vd_pw(K, 12) + ext + 20
    step1 = vd_pw(K, 8) + ext + vd_pw(K, 16) + ext + 20
    steps, nset = d['steps'], d['nset']
    T.ctl((steps - nset) * step0 + nset * step1)
    # (7) leaving the Montgomery form: R1 := R1 G1 (7), the extension O1 -> O2, R2 := (R2 + R1 G2) / M(n_k) (11): R2 holds R = S^E mod g on O2
    T.ctl(vd_pw(K, 7) + ext + vd_pw(K, 11))
    T.free(sR1); T.free(sG1)
    # (8) R (in R2) and g (in the array of g) back to coefficient form, in place: inverse inner transforms, interpolation at the K nodes of O2
    interp = vd_inner(K, True, PH) + vd_interp(K, Px)
    T.ctl(2 * interp)
    if sBT is not None: T.free(sBT)
    T.free(sB1); T.free(sTab)
    T.ctl(2 + 500)
    VD.clear(); VD.update(d, ext=ext, step0=step0, step1=step1, interp=interp, Lmax=Lmax, NTAB=NTAB)
    info = dict(steps=steps, nset=nset, PN=Px, PNp=PH, step=step0, mulx=step1 - step0, sg2=sg, sR2=sR2, vd=dict(VD))
    return T, info


# ---------------------------------------------------------------- hgcd.c on shapes (normal Euclid; the earlier worst-case model (off under LEAND, NORMALD))
WC_MEM = False       # worst-case live set of stage D: the quotient array of every division at its largest length and the working arrays of the Newton division
WORST_D = False      # worst-case recurrence of stage D: at every node of the half-gcd tree the normal local charge plus the charge of one full division at that node (proof.md 6.3)
TRUNC2 = 1           # the second recursive call of a node runs on the top 2 k3 + 1 coefficients of the reduced pair (Thome 2003, Stehle-Zimmermann 2004; proof 4.4) and its matrix is applied to the whole pair only where the node returns the remainders
TRUNC2_SHRINK = 7    # with TRUNC2: the remainders returned by a node that applies the second matrix are moved into arrays of their own length (one copy each; bit 1: c, bit 2: d, bit 4: from the low end of the pool)
NORMALD = 1          # stage D for the normal remainder sequence only: every division tests that its quotient has degree 1 and every call of hgcd that it returns its parameter (a zero remainder inside hgcd also ends the trial), 2 operations each; any other case ends the trial (premise H-NORMAL; WORST_D and WC_MEM are then off)

# full division at a node: the charge of divrem_any by the model's own routines (schoolbook division, or the Newton division = one series inverse + two products)
CMUL_INNER = 12      # one inner step of the schoolbook division: mul, sub, LD(2) = 4, ST(1) = 2, loop 3, index 1 -> 1 + 1 + 4 + 2 + 3 + 1
CMUL_OUTER = 15
SMALL_EUCLID = 12 * (2 * 96 + 1) ** 2 + 20 * (2 * 96 + 1) + 400000      # closing loop of poly_gcd_own with n <= 192: Euclid with arbitrary quotients, quadratic bound


def naive_general(lx, ly):
    """poly_divrem_naive on the general path: lx coefficients by ly, quotient of lx - ly + 1 coefficients"""
    dq1 = lx - ly + 1
    return 3 + 7 * lx + powcost(PM2) + INV_CTL + dq1 * ((ly - 1) * CMUL_INNER + CMUL_OUTER)


DIVLOG = None        # when a list, prod_cost appends the transform-domain arrays of every block product it evaluates (the memory walk of the division)


def prod_cost(la, lb, outlen, ws=0, out=None):
    """product of la by lb coefficients whose support has outlen coefficients (outlen = la + lb - 1, or the length of the true product when high zeros are padded).
    Default: all outlen coefficients are placed.  Window (MIDPROD): only the out coefficients from position ws are placed (out = None: all of them).
    ws = 0: the transform has at least outlen points (no wrap-around) and only the first out coefficients are inverse transformed and placed.
    ws > 0 (middle product, Hanrot-Quercia-Zimmermann 2004): the product is formed cyclically with N >= max(ws + out, outlen - ws) points; the coefficients of positions >= N wrap onto
    positions < outlen - N <= ws, below the window, so the window is exact; the operand H is read shifted by N - ws so that the window starts at position 0"""
    if out is None: out = outlen - ws
    if ws == 0 and out == outlen: need = outlen
    else:
        need = outlen if ws == 0 else max(ws + out, outlen - ws)
        assert ws + out <= need and outlen - ws <= need or ws == 0
    Pl, c = plan3_for_len(max(need, 2))
    g = dict(H=[lb], S=[la], prod={(0, 0): (0, 1)})
    CTX['direct'] = DIRECT_DIV                                # a division accumulates the chunks of a product into the output array of the division (listed in wc_div_arrays)
    try: cc, eps = conv_bilin_cost(Pl, 1, [out], [g], (Pl.N - ws) % Pl.N if ws else 0)
    finally: CTX['direct'] = False
    if Pl.a > BIGA and DIVLOG is not None: DIVLOG.append(prod_arrays(PL, PL['ops'], 1))
    return c + cc + plan_invN_ops(Pl) + 3 * out + 20          # product + scaling/placement + control


def series_inverse_cost(lf, k):
    c = 0; t = 1
    while t < k:
        t2 = min(2 * t, k); lft = min(lf, t2); m2 = t2 - t
        if MIDPROD & 2: p1 = prod_cost(lft, t, lft + t - 1, t, m2)                      # middle product: only the coefficients t .. t2 - 1 of g_(t2) phi_t are used
        else: p1 = prod_cost(lft, t, lft + t - 1)
        p2 = prod_cost(m2, m2, 2 * m2 - 1, 0, m2) if MIDPROD & 4 else prod_cost(m2, m2, 2 * m2 - 1)     # only the first m2 coefficients of phi e are used
        c += p1 + p2 + 12 * m2 + 12 * m2 + 40
        t = t2
    return c


def fast_division(la, lb):
    k = la - lb + 1
    return (powcost(PM2) + INV_CTL + 8 * k + 8 * lb + series_inverse_cost(min(lb, k), k)
            + (prod_cost(k, k, 2 * k - 1, 0, k) + prod_cost(k, lb, la, 0, lb - 1) if MIDPROD & 4 else prod_cost(k, k, 2 * k - 1) + prod_cost(k, lb, la)) + 8 * la + 400)


def div_cost(la, lb):
    """divrem_any: schoolbook if the quotient has at most 64 coefficients or the divisor at most 64, else the Newton division"""
    k = la - lb + 1
    if k <= 64 or lb <= 64: return naive_general(la, lb)
    return fast_division(la, lb)


@functools.lru_cache(maxsize=None)
def padded_division_full(la, kmax):
    """(charge, transform-domain arrays of the block product of largest live size) of the re-centering division in its padded form (10-17, ruling 643de050 H-COST-DIV-MAX), for the Newton range 64 <= dq <= dmax = min(kmax, la - 65):
    the program runs it with the quotient precision kN = dmax + 1 and the divisor in a buffer of lbp = la - 64 coefficients (zeros above its top
    coefficient, so the polynomial is unchanged), the reversed divisor in a buffer of min(lbp, kN) and the quotient truncated to dq + 1 coefficients in
    a buffer of kN (zeros above); the sizes are the same for every dq, so the charge is one number: the three buffer loops (load, store, loop step,
    one select per element, allocation and free) and the Newton division at the padded sizes"""
    global DIVLOG
    old = DIVLOG; DIVLOG = []
    try:
        dmax = min(kmax, la - 65)
        kN = dmax + 1; lbp = la - 64
        loops = sum(dupv(n, 0)[0].ops + n + 105 for n in (lbp, min(lbp, kN), kN))
        ops = loops + (powcost(PM2) + INV_CTL + 8 * kN + 8 * lbp + series_inverse_cost(min(lbp, kN), kN)
                       + (prod_cost(kN, kN, 2 * kN - 1, 0, kN) + prod_cost(kN, lbp, la, 0, lbp - 1) if MIDPROD & 4 else prod_cost(kN, kN, 2 * kN - 1) + prod_cost(kN, lbp, la)) + 8 * la + 400)
        arrays = max(DIVLOG, key=lambda x: sum(blk(y) for y in x), default=[])
    finally:
        DIVLOG = old
    return ops, tuple(arrays)


def padded_division(la, kmax):
    return padded_division_full(la, kmax)[0]


@functools.lru_cache(maxsize=None)
def worst_div(la, kmax):
    """the charge of one re-centering division of a polynomial of la coefficients by one of la - dq, for every 1 <= dq <= kmax: in the schoolbook
    range (quotient or divisor of at most 64 coefficients) every dq is evaluated (at most 127 values); in the Newton range the division runs padded
    (padded_division), one charge for every dq; the result is the larger of the two"""
    hi = min(kmax, la - 1); best = 0
    for d in set(range(1, min(hi, 63) + 1)) | set(range(max(1, la - 64), hi + 1)):
        best = max(best, naive_general(la, la - d))
    if hi >= 64 and la - 65 >= 64:
        best = max(best, padded_division(la, kmax))
    return best


def wc_div_arrays(lcc, dq):
    """slots of the arrays live together inside divrem_fast (dq + 1 quotient coefficients, dividend of lcc coefficients), besides the caller's arrays"""
    k = dq + 1
    if k <= 64: return []
    pl, _ = plan3_for_len(max(lcc, 2 * k - 1))                  # the largest product of divrem_fast: q_rev = a_rev * g (2k - 1 coefficients) or q * b (lcc)
    if pl.a > BIGA: ws = list(padded_division_full(lcc, dq)[1])        # the transform-domain arrays of the largest block product of the padded division (its scheme as priced)
    else: ws = [pl.n, pl.n, pl.N]
    return [k, k, k, 2 * k - 1, lcc, lcc - 64, min(lcc - 64, k)] + ws              # the last two: the padded divisor and the reversed divisor (padded_division)

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
    s = T.new_fp(lo if lo else 1)  # pool:H
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
    BIG = Pl.a > BIGA
    N = Pl.N
    if not BIG:
        tH0 = T.new_fp(Pl.n); tH1 = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        ob = [T.new_fp(N) for _ in range(4)]  # pool:H
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
    cc, eps = conv_bilin_cost(Pl, 4, Ls, groups); T.ctl(cc)
    if BIG:
        # block mode, streamed (proof 4.5): the arrays of A and B are dead after the product and are freed as soon as they are transformed; the four outputs have their own length
        P = dict(PL)
        ob = [None] * 4
        for M_ in (A, B):
            for x, s_ in zip(M_[0], M_[1]):
                if not x and s_: T.free(s_)                          # an empty entry keeps only its one-slot array
        if P['mode'] == 'a':
            # scheme (a): the spectra of one matrix are held whole and those of the other one row (or column) at a time, the smaller of the two orders; each row (column) forms its two outputs
            nA = [nblk(x) if x else 0 for x in Al]; nBm = [nblk(x) if x else 0 for x in Bl]
            wsA = sum(nBm) + max(nA[0] + nA[1], nA[2] + nA[3])           # B whole, a row of A at a time
            wsB = sum(nA) + max(nBm[0] + nBm[2], nBm[1] + nBm[3])        # A whole, a column of B at a time
            if wsA <= wsB: whole, stream, rows = B, A, ((0, 1), (2, 3))
            else: whole, stream, rows = A, B, ((0, 2), (1, 3))
            held = []
            for x, s_ in zip(whole[0], whole[1]):
                if x:
                    held.append(T.new_fp(nblk(x) * NB)); T.free(s_)
            for r_ in rows:                                           # the entries of a row (column) of the streamed matrix are the entries of the two outputs of that row (column)
                cur = []
                for e in r_:
                    if stream[0][e]:
                        cur.append(T.new_fp(nblk(stream[0][e]) * NB)); T.free(stream[1][e])
                acc = T.new_fp(NB)
                for k in r_: ob[k] = T.new_fp(Ls[k] if Ls[k] else 1)  # pool:H
                T.free(acc)
                for x in cur: T.free(x)
            for x in held: T.free(x)
        elif P['mode'] == 'c':
            # scheme (c): the entries of A and B stay in coefficient form until the last chunk, the four outputs are accumulated and then placed into arrays of their own
            acc, done = chunk_phase(T, P, 4)
            done()
            for M_ in (A, B):
                for x, s_ in zip(M_[0], M_[1]):
                    if x: T.free(s_)
            accd = dict(zip(P['acck'], acc))
            for k in range(4):
                ob[k] = T.new_fp(Ls[k] if Ls[k] else 1)
                if k in accd: T.free(accd[k])
        else:
            # scheme (b): the outer-domain arrays of all operands; the output of an outer point overwrites a dead operand array of that point; the outputs in coefficient form
            # are allocated when the products are placed, after the operand arrays that are dead have been freed
            n2 = P['n2']
            fB = []; fA = []
            for x, s_ in zip(Bl, B[1]):
                if x:
                    fB.append(T.new_fp(form_slots(x, 'b', n2))); T.free(s_)
            for x, s_ in zip(Al, A[1]):
                if x:
                    fA.append(T.new_fp(form_slots(x, 'b', n2))); T.free(s_)
            wk = [T.new_fp(y) for y in prod_work(P, 4)]
            for x in wk + fB: T.free(x)
            for k in range(4): ob[k] = T.new_fp(Ls[k] if Ls[k] else 1)  # pool:H
            for x in fA: T.free(x)
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
        o = T.new_fp(l if l else 1); T.ctl(3)  # pool:H
        if eps[k]:
            T.ops += l; T.ld(l); T.st(l); T.loopc(l)
        T.free(ob[k])
        outs[k] = o
        if l: T.ctl(trim(1))
        outl[k] = l
    return T, outl, outs, BIG


def fslots(m):
    """slots of the array F (the state R of stage C and the second operand of stage D): in block mode m + 1, so that the output d of the apply_inv of the top node
    (nres = m + 1 coefficients) can be written over it"""
    return m + 1 if plan3_for_len(2 * m - 1)[0].a > BIGA else m


def apply_inv(Rl, Rs, h, la, lb, consume, b, own_in=(0, 0), sa=0, sb=0):
    """returns (Tr, lc, sc, ld, sd, reuse); reuse = (c was written over the owned a, d over the owned b), block mode only"""
    T = Tr(b)
    nres = la
    Pl, c = plan3_for_len(nres); T.ctl(c)
    N = Pl.N
    BIG = Pl.a > BIGA
    reuse = (False, False)
    if BIG:
        # block mode, streamed (proof 4.5): the outputs c and d are written over the owned inputs a and b when those arrays have nres slots (the placement of slot s writes the
        # blocks s and s + 1, which are already transformed), else into arrays of their own
        reuse = (bool(own_in[0]) and sa >= nres, bool(own_in[1]) and sb >= nres)
    else:
        tH = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        sc_ = T.new_fp(N); sd_ = T.new_fp(N)  # pool:H
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
    CTX['seq'] = BIG and SEQ_OUT
    try:
        cc, eps = conv_bilin_cost(Pl, 2, [nres, nres], groups); T.ctl(cc)
    finally:
        CTX['seq'] = False
    if BIG:
        P = dict(PL)
        if P['mode'] != 'c':
            sc_ = sa if reuse[0] else T.new_fp(nres)  # pool:H
            sd_ = sb if reuse[1] else T.new_fp(nres)  # pool:H
        if consume:
            for x, s_ in zip(Rl, Rs):
                if not x and s_: T.free(s_)                          # an empty entry keeps only its one-slot array
        if P['mode'] == 'c':
            # scheme (c): a, b and the entries stay in coefficient form until the last chunk; the outputs c and d are accumulated in two accumulators and placed afterwards,
            # over a and b when those are owned and long enough, else into arrays of their own
            acc, done = chunk_phase(T, P, 2)
            done()
            if consume:
                for x, s_ in zip(Rl, Rs):
                    if x: T.free(s_)
            sc_ = sa if reuse[0] else T.new_fp(nres)  # pool:H
            sd_ = sb if reuse[1] else T.new_fp(nres)  # pool:H
            for x in acc: T.free(x)
        elif P['mode'] == 'a':
            # scheme (a): the spectra of the four entries (each entry is freed as soon as it is transformed when R is consumed); a and b pass through a sliding window of
            # kR + 1 blocks each (an entry of kR blocks meets kR blocks of an operand at a slot, and the block after the slot is transformed before the slot is placed), one accumulator
            kR = max([nblk(x) for x in Rl if x] or [1])
            sp = []
            for x, s_ in zip(Rl, Rs):
                if x:
                    sp.append(T.new_fp(nblk(x) * NB))
                    if consume: T.free(s_)
            win = [T.new_fp(min(nblk(x), kR + 1) * NB) for x in (la, lb) if x]
            acc = T.new_fp(NB)
            for x in [acc] + win + sp: T.free(x)
        else:
            # scheme (b): the outer-domain arrays of the four entries and of a and b (the output of an outer point overwrites a dead operand array of that point), the working arrays
            n2 = P['n2']
            if P['seq']:
                # the outputs one after the other: the forms of a and b are made once and kept; c = r22 a - r12 b needs the forms of r22 and r12, which are freed after c is placed,
                # then d = r11 b - r21 a those of r11 and r21 (the inner transforms of a and b at each outer point are made again for d, charged); the output of an outer point overwrites a dead entry form
                fab = [T.new_fp(form_slots(x, 'b', n2)) for x in (la, lb) if x]
                for ph in ((3, 1), (2, 0)):
                    fo = []
                    for e in ph:
                        if Rl[e]:
                            fo.append(T.new_fp(form_slots(Rl[e], 'b', n2)))
                            if consume: T.free(Rs[e])
                    wk = [T.new_fp(y) for y in prod_work(P, 1)]
                    for x in wk + fo: T.free(x)
                for x in fab: T.free(x)
            else:
                # the outer-domain arrays of the four entries and of a and b (the output of an outer point overwrites a dead operand array of that point), the working arrays
                fo = []
                for x, s_ in zip(Rl, Rs):
                    if x:
                        fo.append(T.new_fp(form_slots(x, 'b', n2)))
                        if consume: T.free(s_)
                for x in (la, lb):
                    if x: fo.append(T.new_fp(form_slots(x, 'b', n2)))
                wk = [T.new_fp(y) for y in prod_work(P, 2)]
                for x in wk + fo: T.free(x)
    else:
        T.free(tH); T.free(tS)
        if consume:
            mat_free(T, Rs)
    T.ctl(plan_invN_ops(Pl))
    for k in range(2):
        T.ctl(3)
        if not eps[k]:
            T.st(nres); T.loopc(nres); continue
        if BIG: continue                                      # the scale 1/NB and the sign are applied by the placement of the slots
        if eps[k] < 0: T.ops += 1
        T.ops += nres; T.ld(nres); T.st(nres); T.loopc(nres)
    lc = la - h; ld = lc - 1
    T.ctl(trim(1 + (nres - lc)) + trim(1 + (nres - ld)))
    return T, lc, sc_, ld, sd_, reuse


HGCD_CACHE = {}


def _relink(x, base, ext):
    """the arrays in the result of a recorded call, named in the ids of the caller (ids < 0 are the arrays given to the call)"""
    if isinstance(x, Slot): return Slot(int(x), ext[-x.id - 1] if x.id < 0 else base + x.id)
    if isinstance(x, list): return [_relink(y, base, ext) for y in x]
    if isinstance(x, tuple): return tuple(_relink(y, base, ext) for y in x)
    return x


def hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b):
    """hgcd memoised by shape: the body _hgcd runs once for each shape and records its events with ids relative to the call; every use links them to the arrays of the caller.
    returns (Tr, out) ; out = (lc, sc, ld, sd, Rl, Rs, h)"""
    key = (la, int(sa), lb, int(sb), k, want_mat, own, wc, wd, b)
    ent = HGCD_CACHE.get(key)
    if ent is None:
        ctx = Ctx(); CTX_STACK.append(ctx)
        try:
            T, out = _hgcd(la, Slot(int(sa), -1) if sa else 0, lb, Slot(int(sb), -2) if sb else 0, k, want_mat, own, wc, wd, b)
        finally:
            CTX_STACK.pop()
        ent = (T, out, Rec(T.ev, ctx.n)); HGCD_CACHE[key] = ent
    T, out, rec = ent
    ctx = CTX_STACK[-1]; base = ctx.n; ctx.n += rec.nloc
    ext = (sa.id if sa else None, sb.id if sb else None)
    Tc = Tr(T.base); Tc.ops, Tc.cur, Tc.peak, Tc.cnt, Tc.pcnt = T.ops, T.cur, T.peak, T.cnt, T.pcnt
    Tc.ev = [('C', rec, base, ext)]
    return Tc, _relink(out, base, ext)


hgcd.cache_clear = HGCD_CACHE.clear


def _hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b):
    if LEAND: return _hgcd_ld(la, sa, lb, sb, k, want_mat, own, wc, wd, b)      # pos_leand
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
    if NORMALD: T.ctl(2)                                      # the return test: h1 == k1 (a zero remainder inside hgcd also ends the trial), else the trial ends
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    assert h1 >= 1, 'non-generic shape'
    t2, lcc, scc, ldd, sdd, reuse = apply_inv(R1l, R1s, h1, la, lb, not want_mat, T.here(), (own & 1, (own >> 1) & 1), sa, sb)
    T.add(t2); T.ctl(4)
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
    if NORMALD: T.ctl(2)                                      # the quotient test: dq == 1, else the trial ends
    dqm = max(dq, k2) if WC_MEM else dq
    sq = T.new_fp(dqm + 1); srm = T.new_fp(lcc)  # pool:H
    if WC_MEM: T.bump_blocks(wc_div_arrays(lcc, dqm))
    T.ctl(3)                                                  # divrem_any
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)
    T.ctl(dc)
    if WORST_D: T.ops += worst_div(lcc, k2)                   # recurrence of 6.3: plus one full division of this node at its worst quotient degree
    T.free(scc)
    k3 = k2 - dq
    s3 = ldd - 1 - 2 * k3
    if TRUNC2: T.ctl(3 + 7)                                   # s3 (a shift, two subtractions) and the test s3 > 0, lrem != 0, ldd - lrem <= k3 (comparisons, a subtraction, branches)
    if TRUNC2 and s3 > 0 and lrem and ldd - lrem <= k3:
        # the truncated second call (proof 4.4): its operands are the top 2 k3 + 1 coefficients of d and the top lrem - s3 of the remainder, read in place (shifted by s3, like the
        # first call); it returns its matrix only, and the matrix is applied to the whole pair (d, remainder) where this node returns the remainders
        T.ctl(4 + 2)                                          # the two shifted addresses (a shift and an addition each) and the two lengths
        t3, o3 = hgcd(ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here())
        T.add(t3)
        if NORMALD: T.ctl(2)                                  # the return test: h3 == k3 (a zero remainder inside hgcd also ends the trial), else the trial ends
        R3l, R3s, h3 = o3[4], o3[5], o3[6]
        T.ctl(4)                                              # the tests of wc and wd
        if wc or wd:
            t4, lc3, sc3, ld3, sd3, reuse3 = apply_inv(R3l, R3s, h3, ldd, lrem, not want_mat, T.here(), (1, 1), sdd, srm)
            T.add(t4); T.ctl(4 + 4)                           # the two reuse tests and the tests of wc and wd
            if not reuse3[0]: T.free(sdd)
            if not reuse3[1]: T.free(srm)
            if not wc:
                T.free(sc3); lc3 = sc3 = None
            if not wd:
                T.free(sd3); ld3 = sd3 = None
            if TRUNC2_SHRINK:
                # the remainders are written over d and the remainder of the node (arrays of up to the caller's length); each is moved into an array of its own length
                # (one copy: a load, a store and the loop step per coefficient), and the long array is freed.  bit 1: c, bit 2: d, bit 4: the copies from the low end of the pool
                T.ctl(2 * (3 + 1))                            # per remainder: the length test (a load of the block size, a comparison, a branch) and the pointer assignment
                if (TRUNC2_SHRINK & 1) and sc3 is not None and int(sc3) > lc3:
                    if TRUNC2_SHRINK & 4: s_ = T.new_fp(lc3)
                    else: s_ = T.new_fp(lc3)  # pool:H
                    T.ld(lc3); T.st(lc3); T.loopc(lc3); T.free(sc3); sc3 = s_
                if (TRUNC2_SHRINK & 2) and sd3 is not None and int(sd3) > ld3:
                    if TRUNC2_SHRINK & 4: s_ = T.new_fp(ld3)
                    else: s_ = T.new_fp(ld3)  # pool:H
                    T.ld(ld3); T.st(ld3); T.loopc(ld3); T.free(sd3); sd3 = s_
        else:
            T.free(sdd); T.free(srm)
            lc3 = sc3 = ld3 = sd3 = None
            T.ctl(2)                                          # the test of want_mat
            if not want_mat: mat_free(T, R3s)
        o3 = (lc3, sc3, ld3, sd3, R3l, R3s, h3)
    else:
        t3, o3 = hgcd(ldd, sdd, lrem, srm, k3, want_mat, 3, wc, wd, T.here())
        T.add(t3)
        if NORMALD: T.ctl(2)                                  # the return test: h3 == k3 (a zero remainder inside hgcd also ends the trial), else the trial ends
    h = h1 + dq + o3[6]
    if want_mat:
        R1l2, R1s2 = mat_mulQ(T, R1l, R1s)
        tm, Ml, Ms, cons = mat_mul((R1l2, R1s2), (o3[4], o3[5]), T.here()); T.add(tm)
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
        if NORMALD: T.ctl(2)                                  # the quotient test: dq == 1, else the trial ends
        sq = T.new_fp(dq + 1); sr = T.new_fp(lx)
        dc, lq, lr, _ = divrem_naive(lx, ly)
        T.ctl(dc)
        if WORST_D: T.ops += max(0, naive_general(lx, ly) - dc)   # recurrence of 6.3: a step of the base case charged on the general path (a step of quotient degree d is at most d steps of degree 1)
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


def gcd_cost(m, dG, b, sx, sy):
    CTX['stage'] = 'D'
    try: return gcd_cost_ld(m, dG, b, sx, sy) if LEAND else gcd_cost_(m, dG, b, sx, sy)      # pos_leand
    finally: CTX['stage'] = None


def gcd_cost_(m, dG, b, sx, sy):
    """poly_gcd_own(g (m+1 coefficients), R-1 (m coefficients)), normal Euclid, gcd degree dG.  sx, sy: the arrays of g (m+1 slots) and of F (fslots(m) slots) of the caller.
    Returns (Tr, (lg, sg))."""
    T = Tr(b)
    lx, ly = m + 1, m
    T.ctl(3); T.ctl(3)
    while ly > 0:
        T.ctl(2)
        n = lx - 1
        T.ctl(4)
        if n <= 2 * 96:
            if NORMALD: T.ctl(2)                              # the quotient test: lx - ly == 1, else the trial ends
            sq = T.new_fp(lx - ly + 1); sr = T.new_fp(lx)
            last = (ly == dG + 1)
            dc, lq, lr, _ = divrem_naive(lx, ly, term_zero=1 if (last and dG >= 1) else 0)
            if last and dG == 0:
                lr = 0
            T.ctl(dc)
            T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
            T.free(sq); T.ctl(5)
            continue
        k = (n + 1) // 2
        t, o = hgcd(lx, sx, ly, sy, k, False, 3, True, True, T.here())
        T.add(t)
        if NORMALD: T.ctl(2 + 2)                              # the return test (h == k or a zero remainder) and the quotient test (lc - ld == 1), else the trial ends
        lc, sc, ld, sd = o[0], o[1], o[2], o[3]
        T.ctl(2)
        dqm = (lc if WC_MEM else lc - ld)
        sq = T.new_fp(dqm + 1); sr = T.new_fp(lc)  # pool:H
        if WC_MEM: T.bump_blocks(wc_div_arrays(lc, dqm))
        T.ctl(3)
        dc, lq, lr, _ = divrem_naive(lc, ld)
        T.ctl(dc)
        if WORST_D: T.ops += worst_div(lc, lc - 1)            # recurrence of 6.3: the division of the outer loop at its worst quotient degree
        T.free(sc); T.free(sq)
        sx = sd; lx = ld; sy = sr; ly = lr; T.ctl(5)
    T.free(sy)
    T.ctl(2)
    if WORST_D: T.ops += SMALL_EUCLID                         # recurrence of 6.3: the closing loop (n <= 192) with arbitrary quotients
    T.ops += powcost(PM2); T.ctl(INV_CTL); T.ld(1)
    T.ops += lx - 1
    T.ld(lx); T.st(lx); T.loopc(lx)
    return T, (lx, sx)


# ---------------------------------------------------------------- LEAND: stage D charged the way of bradcush 1aa56884 (its proof 4.4, lemma 4.8, 4.5; e6dcb600 4.4), in this model's primitives
# Read as text only (no code of the entry was run, compiled or imported); the shapes follow Grok job 163 stage_d.py / products.py (our research tool, which reproduces the entry's row D to the unit).
# What LEAND changes in stage D: (1) the base case (k <= 96) runs in place: the matrix entries are four arrays of k + 2 elements allocated once, no array is allocated inside the loop;
# (2) apply_inv forms c, d cyclically on their true lengths la - h, la - h - 1 (their high coefficients cancel), by whichever of the single transform and the block products is cheaper;
# (3) a node that wants its matrix only forms the top window of c and d (degrees >= s3 - 1, lemma 4.8(a)); (4) the top node works on the two pieces [0, cut), [cut, n1) of g and R
# (lemma 4.8(b)): its first call frees the high pieces after its own apply_inv and c, d are formed one after the other from the low pieces; (5) mat_mul by the cheaper of the single
# transform and the block products; (6) the block products: scheme (a) at the block length 2^31 (one-row block transform of 2^32 points) or scheme (c) (chunked outer product) at the
# block length 2^b of smallest charge, b = 6 .. 31, chunk bound LD_CF elements.  The charges of every primitive are this model's (proof 4.2): passes, Good-Thomas stages, pointwise
# loops, allocations, the outer transform ontt_at (kernels ob2, ob3), the chunk assembly (ocp, oax, ozf), the placement; LD_CONV switches each primitive to the 1aa56884 convention
# (gate only).
LEAND = 1            # 1: stage D as above (requires NORMALD = 1 or AMORT = 1)
AMORT = 0            # with LEAND: premise-free stage D = the normal-sequence trace (tests charged, no abort) + one fast division of length m + the zero-scan allowance; top-node pieces off
LD_WIN = 1           # windows of lemma 4.8(a)
LD_PIECES = None     # top-node pieces of lemma 4.8(b); None: on with NORMALD, off with AMORT (the pieces need h1 = k1 and h3 = k3, a normal sequence)
LD_CF = None         # chunk bound (elements) of the scheme (c) products of stage D; None: m // CHUNK_D
LD_CONV = dict(astat=0, outer=0, fold=0, acc=0, frow=0, pctl=0, scratch=0, compact=0, base3=0)   # 1: the convention of 1aa56884 for that primitive (gate), 0: this model's
LD_ABORT = 2         # one quotient or return test (a comparison and a branch)
LD_CFV = None        # the chunk bound in use (set by run_stages: LD_CF, or m // CHUNK_D)
LD_KSCR = 1 << 44    # 1aa56884 scratch region (gate convention only)
LD_COMPACT_ELEMS = 22924228636997165691      # 1aa56884 G.7 compaction count at r = 21 (CLAIMED; gate convention only)
LD_ROOTS = 6 * (330 + INV_CTL)                # 1aa56884 scheme (c) roots and constants per product (gate convention only)
LD_KCH = {'ob3': (16, 23), 'ob2f': (14, 14), 'ob2i': (14, 14), 'ob4f': (18, 31), 'ob4i': (18, 31), 'ob8f': (26, 71), 'ob8i': (26, 71)}   # 1aa56884 register-blocked outer kernels (gate only)
ASTAT = 0            # allocator statistics per allocation and free (1aa56884: 64; this model: 0); set only inside stage D by run_stages
HB31 = 1 << 31; NB32 = 1 << 32
LD_LOG = collections.Counter()
VLOG = collections.Counter()        # the charge of the scale and loops below on the distinct block products evaluated (a record, not a charge)
LD_SITE = dict(inv=1, div=1, mat=1, tmp=1, top=1, outer=1, topdiv=1)   # the end of the pool of each LEAND allocation statement (1: high, `# pool:H`; 0: low), a constant of the statement
VFIX_PP = 15         # per scheme (c) product: the root w and the scale sign/(NB n2) of its outputs, from an offline table of 2^-i and 1/3 (VERIFY_undercharge U1)
VFIX_PC = 7          # per untwist call of scheme (c): the scaled weight w^(-e) sign/(NB n2) (load the table entry, load the scale, multiply, store) (U1)
VFIX_LOOP = 1        # 1: the chunk loop (3 per chunk + 2, set-up 6 per chunk) and the outer-point loop (3 per point and 2 per chunk) of scheme (c), and the fetch of w^o per output per point (4) (U2)
VFREEZE = 0          # 1 (comparison only): every choice (block length, scheme, single vs block) made on the charge without the three lines above
VCHOICE = 1          # 1: the single-vs-block choice of mat_mul and apply_inv also counts the allocations and frees the block path adds (len(temps) - 7 in mat_mul, len(temps) - 2 in apply_inv)


def ld_new(T, slots, site):
    if LD_SITE[site]: return T.new_fp(slots)  # pool:H
    return T.new_fp(slots)


def ld_pieces_on():
    return bool(LEAND) and (LD_PIECES if LD_PIECES is not None else not AMORT)


def ld_pieces(m):
    """the two pieces of g and R for the top node (1aa56884 4.6 step 8): [0, cut) and [cut, n1), cut = Kc 2^32 >= m + 1 - k1, k1 the first parameter of the top node"""
    h = VD_H; K = -(-(m + 1) // h)
    k1 = (((m + 1) // 2) + 1) >> 1
    Kc = -(-(m + 1 - k1) // h)
    return Kc * h, (K - Kc) * h


def ld_rowfill(Pl, ln):
    """copy of ln coefficients into a transform row of Pl.n points and the zero fill of the rest: a load and a store per coefficient, a store per zero, eight-element loops"""
    return 4 + for8(ln) + 4 * ln + for8(Pl.n - ln) + 2 * (Pl.n - ln) + 2


@functools.lru_cache(maxsize=None)
def ld_bplan(hb): return make_plan(1, (2 * hb).bit_length() - 1)[0]


@functools.lru_cache(maxsize=None)
def ld_bfwd(bl, hb):
    """block transform of NB = 2 hb points (one row of passes) of a block of bl coefficients"""
    P = ld_bplan(hb); return ld_rowfill(P, bl) + fwd_passes(P, P.np)


@functools.lru_cache(maxsize=None)
def ld_binv(hb):
    P = ld_bplan(hb); return inv_passes(P, P.np - 1)


def ld_invN(size):
    """plan_invN of a transform of `size` points (the scale 1/N): a scan of the cache"""
    return 7 * CACHE


@functools.lru_cache(maxsize=None)
def ld_ontt(n, cnt, inv):
    """one outer transform of n = 2^a or 3 * 2^a points at cnt positions with its twiddle table: this model's kernels ob3, ob2 (ontt_at), or (gate) the ob8/ob4/ob2 kernels of 1aa56884"""
    if not LD_CONV['outer']: return ontt_at(n, cnt)
    r3 = n % 3 == 0; M = n // 3 if r3 else n; a = M.bit_length() - 1
    assert (1 << a) == M, n
    ks = ([a % 3] if a % 3 else []) + [3] * (a // 3)
    c = 6 * n + 2; nrows = 3 if r3 else 1
    if r3:
        k0, k1 = LD_KCH['ob3']; c += 10 + 3 * M + 2 + M * (3 * 4 + k0 + k1 * cnt)
    c += 3 * nrows + 2
    per_row = 3 * len(ks) + 2; Ns = M
    for k in ks:
        h = Ns >> k; nb = M // Ns; k0, k1 = LD_KCH['ob%d%s' % (1 << k, 'i' if inv else 'f')]
        per_row += (3 * nb + 2) + nb * (3 * h + 2) + nb * h * ((1 << k) * 4 + ((1 << k) - 1) * 3 + k0 + k1 * cnt)
        Ns >>= k
    return c + nrows * per_row


def ld_nblk(l, hb): return -(-l // hb)


def ld_segs(ws, ln, hb):
    """the pieces of the window [ws, ws + ln) cut at the multiples of hb: (length, count)"""
    e = ws + ln
    if ln <= 0: return []
    q = min(e, (ws // hb + 1) * hb)
    if q == e: return [(ln, 1)]
    out = [(q - ws, 1)]; full = (e - q) // hb; rest = e - q - full * hb
    if full: out.append((hb, full))
    if rest: out.append((rest, 1))
    return out


def ld_fold(l, n3, tw, hb):
    """twist and fold of an operand of l coefficients into the n3 rows of hb elements of one chunk (tw: not the first chunk)"""
    kx = ld_nblk(l, hb); last = l - (kx - 1) * hb
    if not LD_CONV['fold']:          # this model's chunk assembly: ocp for a block that starts a row, oax for a block added to a row, ozf for a row (or the tail of a row) no block reaches
        nocp = min(kx, n3); noax = kx - nocp
        c = nocp * (OCALL_C + OCP[0] + OCP[1] * hb) + noax * (OCALL_C + OAX[0] + OAX[1] * hb)
        if nocp == kx:
            c -= OCP[1] * (hb - last)
            if last < hb: c += OCALL_C + OZF[0] + OZF[1] * (hb - last)
        else: c -= OAX[1] * (hb - last)
        if kx < n3: c += (n3 - kx) * (OCALL_C + OZF[0] + OZF[1] * hb)
        return c
    wr = 4 + tw; ac = 7 + tw; first = min(kx, n3); acc = kx - first; zero_rows = max(0, n3 - kx); c = 0
    if kx <= n3:
        c += (first - 1) * (10 + for8(hb) + wr * hb) + 10 + for8(last) + wr * last + for8(hb - last) + 2 * (hb - last)
    else:
        c += first * (10 + for8(hb) + wr * hb) + (acc - 1) * (10 + for8(hb) + ac * hb) + 10 + for8(last) + ac * last
    c += zero_rows * (10 + for8(hb) + 2 * hb)
    return c + 3 * (kx + zero_rows) + 2


def ld_acc(ws, ln, first, sub, hb):
    """untwist of one chunk of an output into its window [ws, ws + ln) (the first chunk stores, the others add)"""
    if not LD_CONV['acc']:           # this model's kernels: ocp (first chunk) or oax (the others) per piece of the window, OCALL_I per call
        assert not sub
        ch = OCP if first else OAX
        return sum(cnt * (OCALL_I + ch[0] + ch[1] * x) for x, cnt in ld_segs(ws, ln, hb))
    per = 5 if (first and not sub) else 8
    return sum(cnt * (10 + for8(x) + per * x + 3) for x, cnt in ld_segs(ws, ln, hb)) + 2


def ld_frow(hb):
    """the inverse block transform of an outer point folded modulo X^hb - w^o into the row of the output chunk array"""
    if not LD_CONV['frow']: return big_place(hb, hb, False)
    return 8 * hb + for8(hb) + 4


def ld_nc(n2, cf, hb):
    nc = 1
    while cf is not None and (n2 // nc) * hb > cf and (n2 // nc) % 2 == 0: nc *= 2
    return nc


def ld_scheme_c(hb, need, ops, prods, live, outlen, ws, sub, cf):
    q = -(-need // hb)
    if q > 3 << BIGA: return None
    n2 = pad23(q); nc = ld_nc(n2, cf, hb); n3 = n2 // nc; nb2 = 2 * hb
    pw0, pw1 = pw_loop(nb2, 0), pw_loop(nb2, 1)
    mops = [l for l in ops if ld_nblk(l, hb) > 1]; singles = [l for l in ops if ld_nblk(l, hb) == 1]
    pc = LD_CONV['pctl']
    co = (2 + LD_ROOTS + 3 * nc + 2 if pc else 2 + 3 * (n2 + 1)) + sum(ld_bfwd(l, hb) for l in singles)
    for j_first, mult in ((True, 1), (False, nc - 1)):
        if not mult: continue
        cj = (6 if pc else 0) + sum(ld_fold(l, n3, 0 if j_first else 1, hb) for l in mops) + len(mops) * ld_ontt(n3, hb, False)
        cj += n3 * ((8 if pc else 0) + len(mops) * ld_bfwd(hb, hb))
        for k in live:
            cj += n3 * (pw0 + (len(prods[k]) - 1) * pw1 + ld_binv(hb) + ld_frow(hb))
            cj += ld_ontt(n3, hb, True) + ld_acc(ws, outlen[k], j_first, sub, hb)
        co += mult * cj
    temps = [n3 * hb] * max(len(mops), len(live)) + [nb2] * (len(ops) + len(live)) + ([n3] if pc else [n2 + 1, n3])
    ex = VFIX_PP + VFIX_PC * nc * sum(sum(cnt for x, cnt in ld_segs(ws, outlen[k], hb)) for k in live)
    if VFIX_LOOP: ex += 2 + nc * (3 + 2 + 6) + n2 * (3 + 4 * len(live))
    return co + ex, temps, n2, nc, ex


def ld_window_slots(ws, outlen):
    we = ws + outlen
    s0 = max(0, (ws + 1) // HB31 - 3)
    while (s0 + 2) * HB31 - 1 <= ws: s0 += 1
    s1 = -(-we // HB31) + 2
    while s1 * HB31 >= we: s1 -= 1
    return s0, s1, we


def ld_slot_cost(s, s0, ws, we, sub):
    lo, hi = s * HB31, (s + 2) * HB31 - 1
    cnt = min(hi, we) - max(lo, ws); ov = 0
    if s > s0: ov = max(0, min((s + 1) * HB31 - 1, we) - max(s * HB31, ws))
    return ld_binv(HB31) + big_place(cnt, ov, sub)


def ld_choose(need, ops, prods, live, outlen, ws, sub, cf):
    """the cheapest of scheme (a) at the block length 2^31 and scheme (c) at the block length 2^b of smallest charge (b = 6 .. 31). Returns (ops, temps, mode, hb)"""
    ca = 2 + sum((ld_nblk(l, HB31) - 1) * ld_bfwd(HB31, HB31) + ld_bfwd(l - (ld_nblk(l, HB31) - 1) * HB31, HB31) for l in ops)
    pw0, pw1 = pw_loop(NB32, 0), pw_loop(NB32, 1)
    for k in live:
        s0, s1, we = ld_window_slots(ws, outlen[k])
        stot = max(ld_nblk(ls, HB31) + ld_nblk(lh, HB31) - 1 for ls, lh in prods[k])
        A, B = s0, min(s1, stot - 1)
        if B < A: continue
        npr = sum(pairs_range(ld_nblk(ls, HB31), ld_nblk(lh, HB31), A, B) for ls, lh in prods[k])
        cnt_s = B - A + 1
        ca += cnt_s * (pw0 - pw1) + pw1 * npr
        edges = sorted(set(range(A, min(A + 3, B + 1))) | set(range(max(B - 2, A), B + 1)))
        for s in edges: ca += ld_slot_cost(s, s0, ws, we, sub)
        mid = cnt_s - len(edges)
        if mid > 0: ca += mid * ld_slot_cost(edges[2] + 1, s0, ws, we, sub)
    temps_a = [ld_nblk(l, HB31) * NB32 for l in ops] + [NB32]
    best = None
    for bb in range(6, BIGA):
        r = ld_scheme_c(1 << bb, need, ops, prods, live, outlen, ws, sub, cf)
        if r is not None:
            key = r[0] - (r[4] if VFREEZE else 0)
            if best is None or key < best[0]: best = (key,) + r + (1 << bb,)
    assert best is not None, need
    key, co, temps_c, n2, nc, ex, hbc = best
    if key <= ca: return co, temps_c, 'c', hbc, ex
    return ca, temps_a, 'a', HB31, 0


def ld_bilin_big(nout, outlen, groups, ws=0, ltrue=None):
    """the block form of a bilinear product (apply_inv, mat_mul): need from the true lengths (cancellation) or the product lengths; returns (ops, eps, temps, mode, hb)"""
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
    for g in groups: ops_ += list(g['H']) + list(g['S'])
    live = [k for k in range(nout) if eps[k] and prods[k]]
    need = 0
    for k in live:
        L = ltrue[k] if ltrue else max(ls + lh - 1 for ls, lh in prods[k])
        need = max(need, ws + outlen[k], L - ws)
    co, temps, mode, hb, ex = ld_choose(need, ops_, prods, live, list(outlen), ws, False, LD_CFV)
    VLOG['ex'] += ex
    return co, eps, temps, mode, hb, ex


def ld_scratch_return(T, kc, k, Rl):
    """1aa56884 scratch region (gate convention): the matrix of a call with k < 2^44 made from a call with k >= 2^44 is copied into the arena"""
    if LD_CONV['scratch'] and Rl is not None and kc < LD_KSCR <= k:
        T.ctl(4 * sum(Rl) + 20 + 4 * (121 + 13 * 2001 + 64))


def mat_mul_ld(A, B, b):
    """R1 Q R2 of a node (1aa56884 4.4): the four outputs by the single transform or the block products, whichever is cheaper; returns (Tr, lens, slots, consumed)"""
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
    cb, eb, temps, mode, hb, exb = ld_bilin_big(4, Ls, groups)
    BIG = Pl.a > BIGA
    if not BIG:
        cs, es = conv_bilin_cost(Pl, 4, Ls, groups)
        BIG = cb - (exb if VFREEZE else 0) + VCHOICE * (len(temps) - 7) * (122 + 13 * (2 * (T.base + T.cnt) + 1) + FREE_OPS) < cs + sum(Ls[k] * 8 + 2 for k in range(4) if es[k])
    if not BIG:
        tH0 = T.new_fp(Pl.n); tH1 = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        ob = [T.new_fp(N) for _ in range(4)]  # pool:H
        cc, eps = cs, es
    else:
        cc, eps = cb, eb
    T.ctl(cc)
    if BIG:
        LD_LOG['mat_' + mode] += 1
        ob = [ld_new(T, Ls[k] if Ls[k] else 1, 'mat') for k in range(4)]
        held = [ld_new(T, y, 'tmp') for y in temps]
        for x in held: T.free(x)
        for M_ in (A, B):
            for s_ in M_[1]:
                if s_: T.free(s_)
    else:
        LD_LOG['mat_single'] += 1
        T.free(tH0); T.free(tH1); T.free(tS)
    T.ctl(ld_invN(2 * hb if BIG else Pl.N))
    for k in range(4):
        l = Ls[k]
        if BIG:
            T.ctl(3)
            if not eps[k]: T.st(l); T.loopc(l)
            outs[k] = ob[k]
            if l: T.ctl(trim(1))
            outl[k] = l
            continue
        o = T.new_fp(l if l else 1); T.ctl(3)  # pool:H
        if eps[k]:
            T.ops += l; T.ld(l); T.st(l); T.loopc(l)
        T.free(ob[k])
        outs[k] = o
        if l: T.ctl(trim(1))
        outl[k] = l
    return T, outl, outs, BIG


def apply_inv_ld(Rl, Rs, h, la, lb, consume, b, own_in=(0, 0), sa=0, sb=0, win=0):
    """(c, d) = R^-1 (a, b) on the true lengths la - h, la - h - 1 (the high coefficients cancel: cyclic exactness for need >= the true length), the top window [win, .) when win > 0
    (block products only); the single transform or the block products, whichever is cheaper.  Returns (Tr, lc, sc, ld, sd, (False, False, win))"""
    T = Tr(b)
    nres = la
    Pl, c = plan3_for_len(nres); T.ctl(c)
    sgn = -1 if (h & 1) else 1
    T.ctl(60)
    ec = [3, 1]; ed = [2, 0]; scv = [sgn, -sgn]; sdv = [-sgn, sgn]
    lV = [la, lb]
    groups = []
    for v in range(2):
        g = dict(H=[lV[v]], S=[], prod={})
        if not lV[v]: continue
        if Rl[ec[v]]:
            g['prod'][(len(g['S']), 0)] = (0, scv[v]); g['S'].append(Rl[ec[v]])
        if Rl[ed[v]]:
            g['prod'][(len(g['S']), 0)] = (1, sdv[v]); g['S'].append(Rl[ed[v]])
        if g['S']: groups.append(g)
        T.ctl(10)
    lc0 = la - h; ld0 = lc0 - 1
    cb, eb, temps, mode, hb, exb = ld_bilin_big(2, [lc0 - win, ld0 - win], groups, win, [lc0, ld0])
    BIG = Pl.a > BIGA
    if not BIG:
        cs, es = conv_bilin_cost(Pl, 2, [nres, nres], groups)
        BIG = cb - (exb if VFREEZE else 0) + VCHOICE * (len(temps) - 2) * (122 + 13 * (2 * (T.base + T.cnt) + 1) + FREE_OPS) + 6 < cs + sum(8 * nres + 2 + (1 if es[k] < 0 else 0) for k in range(2) if es[k])
    if not BIG: win = 0
    if BIG:
        LD_LOG['inv_' + mode] += 1
        sc_ = ld_new(T, lc0 - win, 'inv')
        sd_ = ld_new(T, ld0 - win, 'inv')
        cc, eps = cb, eb
        T.ctl(cc)
        held = [ld_new(T, y, 'tmp') for y in temps]
        for x in held: T.free(x)
        if consume: mat_free(T, Rs)
    else:
        LD_LOG['inv_single'] += 1
        N = Pl.N
        tH = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        sc_ = ld_new(T, N, 'inv')
        sd_ = ld_new(T, N, 'inv')
        cc, eps = cs, es
        T.ctl(cc)
        T.free(tH); T.free(tS)
        if consume: mat_free(T, Rs)
    T.ctl(ld_invN(2 * hb if BIG else Pl.N))
    for k in range(2):
        T.ctl(3)
        if not eps[k]:
            T.st(nres); T.loopc(nres); continue
        if BIG: continue
        if eps[k] < 0: T.ops += 1
        T.ops += nres; T.ld(nres); T.st(nres); T.loopc(nres)
    lc = la - h; ld = lc - 1
    if BIG: T.ctl(trim(1) + trim(1))
    else: T.ctl(trim(1 + (nres - lc)) + trim(1 + (nres - ld)))
    return T, lc, sc_, ld, sd_, (False, False, win)


def hgcd_base_ld(la, sa, lb, sb, k, want_mat, own, wc, wd, T):
    """the base case in place (1aa56884 4.4): the division r = a - q0 b - q1 b' written over the array of a, the roles swapped; R := R Q by mul_add_q2 written over r12 / r22"""
    if own & 1: sx = sa
    else:
        t, sx = dupv(la, T.here()); T.add(t)
    if own & 2: sy = sb
    else:
        t, sy = dupv(lb, T.here()); T.add(t)
    lx, ly = la, lb
    Rl = Rs = None
    if want_mat:
        Rs = [T.new_fp(k + 2) for _ in range(4)]
        T.st(2); T.ctl(8)
        Rl = [1, 0, 0, 1]
    ssum = 0
    while ly > 0:
        dq = lx - ly
        T.ctl(6)
        if dq > k - ssum: break
        dc, lq, lr, _ = divrem_naive(lx, ly)
        T.ctl(dc + LD_ABORT + 4)
        if want_mat:
            for e, f in ((0, 1), (2, 3)):
                le, lf = Rl[e], Rl[f]
                lt = le + 1 if le else 0; lo = max(lt, lf)
                T.ops += (le + max(le - 1, 0) + (1 if le > 0 else 0)) + (max(le - 1, 0) + (min(lf, le + 1) if le > 0 else 0))
                T.ld(le + lf); T.st(lo); T.loopc(lo); T.ctl(8 + 8 * lo); T.ctl(trim(1))
                Rl[e], Rl[f] = lo, le; Rs[e], Rs[f] = Rs[f], Rs[e]
            T.ctl(4)
        ssum += dq
        lx, ly = ly, lr; sx, sy = sy, sx
    lc = sc = ld = sd = None
    if wc: lc, sc = lx, sx
    else: T.free(sx)
    if wd: ld, sd = ly, sy
    else: T.free(sy)
    return T, (lc, sc, ld, sd, Rl, Rs, ssum)


def _hgcd_ld(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr=()):
    """hgcd of 1aa56884 4.4 (memoised through hgcd(); fr: arrays of the caller freed after the first apply_inv, the top node only)"""
    T = Tr(b); T.ctl(40)
    n = la - 1
    if lb == 0 or n - (lb - 1) > k:
        Rl = Rs = None
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
        return hgcd_base_ld(la, sa, lb, sb, k, want_mat, own, wc, wd, T)
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    las = la - s; lbs = lb - s if lb > s else 0
    t1, o1 = hgcd(las, 0, lbs, 0, k1, 1, 0, False, False, T.here())
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    ld_scratch_return(T, k1, k, R1l)
    T.ctl(LD_ABORT)                                           # the return test
    assert h1 >= 1, 'non-generic shape'
    w = 0
    if LD_WIN and want_mat and not wc and not wd:             # lemma 4.8(a): the top window of c and d, degrees >= s3 - 1
        lc_ = la - h1; ld_ = la - h1 - 1; k3_ = k - h1 - 1; s3_ = (ld_ - 1) - 2 * k3_
        if s3_ > 0 and not (ld_ == 0 or (lc_ - ld_) > k - h1): w = s3_ - 1
    t2, lcc, scc, ldd, sdd, reuse = apply_inv_ld(R1l, R1s, h1, la, lb, not want_mat, T.here(), (own & 1, (own >> 1) & 1), sa, sb, w)
    T.add(t2); T.ctl(4)
    w = reuse[2]
    if w: T.ctl(2 * LD_ABORT)                                 # the windowed node tests the coefficients at the leading degrees
    for x in fr: T.free(x)
    if own & 1: T.free(sa)
    if own & 2: T.free(sb)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    if ldd == 0 or (lcc - ldd) > k2:
        Rl = Rs = None
        if want_mat: Rl, Rs = R1l, R1s
        lc = sc = ld = sd = None
        if wc: lc, sc = lcc, scc
        else: T.free(scc)
        if wd: ld, sd = ldd, sdd
        else: T.free(sdd)
        return T, (lc, sc, ld, sd, Rl, Rs, h1)
    dq = lcc - ldd
    dqm = max(dq, k2) if WC_MEM else dq
    sq = ld_new(T, dqm + 1, 'div')
    srm = ld_new(T, lcc - w, 'div')
    if WC_MEM: T.bump_blocks(wc_div_arrays(lcc - w, dqm))
    T.ctl(3)
    dc, lq, lrem, _ = divrem_naive(lcc - w, ldd - w)
    lrem += w
    T.ctl(dc + LD_ABORT)                                      # the quotient test
    T.free(scc)
    k3 = k2 - dq
    s3 = (ldd - 1) - 2 * k3
    if s3 > 0:
        t3, o3 = hgcd(ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here())
        T.add(t3)
        R2l, R2s, h3 = o3[4], o3[5], o3[6]
        ld_scratch_return(T, k3, k, R2l)
        T.ctl(LD_ABORT)
        lc3 = sc3 = ld3 = sd3 = None
        if wc or wd:
            t4, lc4, sc4, ld4, sd4, reuse4 = apply_inv_ld(R2l, R2s, h3, ldd, lrem, not want_mat, T.here(), (1, 1), sdd, srm, 0)
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
        t3, o3 = hgcd(ldd, sdd, lrem, srm, k3, want_mat, 3, wc, wd, T.here())
        T.add(t3)
        T.ctl(LD_ABORT)
    h = h1 + dq + o3[6]
    Rl = Rs = None
    if want_mat:
        R1l2, R1s2 = mat_mulQ(T, R1l, R1s)
        tm, Ml, Ms, cons = mat_mul_ld((R1l2, R1s2), (o3[4], o3[5]), T.here()); T.add(tm)
        if not cons:
            mat_free(T, o3[5]); mat_free(T, R1s2)
        Rl, Rs = Ml, Ms
    T.free(sq)
    return T, (o3[0], o3[1], o3[2], o3[3], Rl, Rs, h)


def apply_inv_split_ld(Rl, Rs, h, cut, outl, b, dcut=None, lowp=()):
    """the top node (1aa56884 4.4 (ii), (iii)): c, then d, from the low pieces (window [0, l) of products of true length cut + len(r) - 1, not cancelled); the entries that a finished
    output no longer needs are freed before the next output; d in two pieces at dcut when asked; the low pieces freed at the end"""
    T = Tr(b); T.ctl(60)
    out = []
    sgn = -1 if (h & 1) else 1
    for o, (e1, e2, sg) in enumerate(((3, 1, sgn), (0, 2, sgn))):
        lo = outl[o]
        if o == 1 and dcut:
            hnd = (ld_new(T, dcut, 'top'), ld_new(T, lo - dcut, 'top'))
        else:
            hnd = ld_new(T, lo, 'top')
        groups = [dict(H=[cut], S=[Rl[e1]], prod={(0, 0): (0, sg)}), dict(H=[cut], S=[Rl[e2]], prod={(0, 0): (0, -sg)})]
        cc, eps, temps, mode, hb, _ex = ld_bilin_big(1, [lo], groups, 0)
        LD_LOG['top_' + mode] += 1
        T.ctl(cc + 10)
        held = [ld_new(T, y, 'tmp') for y in temps]
        for x in held: T.free(x)
        T.free(Rs[e1]); T.free(Rs[e2])
        out.append(hnd)
    for x in lowp: T.free(x)
    T.ctl(7 * 64 + 2 * 3 + trim(1) + trim(1))                # plan_invN of the block plan, two trims, two scales
    return T, out


def hgcd_top_ld(la, lb, k, cut, b, high, low):
    """the top node of stage D with the pieces of g and R (1aa56884 4.4, lemma 4.8(b)); the normal shape is asserted (h1 = k1, h3 = k3, cut >= lc)"""
    T = Tr(b); T.ctl(40)
    n = la - 1
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    t1, o1 = _hgcd_ld(la - s, 0, lb - s, 0, k1, 1, 0, False, False, T.here(), tuple(high))
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    T.ctl(LD_ABORT)
    lcc = la - h1; ldd = lcc - 1
    assert cut >= lcc and h1 == k1, (cut, lcc, h1, k1)
    k3 = k - h1 - 1
    cut2 = ldd - k3
    t2, (scc, sdd) = apply_inv_split_ld(R1l, R1s, h1, cut, (lcc, ldd), T.here(), cut2, tuple(low))
    T.add(t2); T.ctl(4)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    assert not (ldd == 0 or (lcc - ldd) > k2), 'top shape'
    dq = lcc - ldd
    sq = ld_new(T, dq + 1, 'topdiv')
    srm = (ld_new(T, cut2, 'topdiv'), ld_new(T, lcc - cut2, 'topdiv'))
    T.ctl(3)
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)
    T.ctl(dc + LD_ABORT)
    T.free(scc)
    assert k3 == k2 - dq
    s3 = (ldd - 1) - 2 * k3
    assert s3 > 0, s3
    t3, o3 = _hgcd_ld(ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here(), (sdd[1], srm[1]))
    T.add(t3)
    R2l, R2s, h3 = o3[4], o3[5], o3[6]
    T.ctl(LD_ABORT)
    assert h3 == k3, (h3, k3)
    lc4 = ldd - h3; ld4 = lc4 - 1
    t4, (sc4, sd4) = apply_inv_split_ld(R2l, R2s, h3, cut2, (lc4, ld4), T.here(), None, (sdd[0], srm[0]))
    T.add(t4); T.ctl(4)
    T.free(sq)
    return T, (lc4, sc4, ld4, sd4, None, None, h1 + dq + h3)


def ld_fastdiv(m):
    """AMORT (Grok job 163): one fast division of length m, the Newton reciprocal of m + 1 coefficients and two products of m + 1 by m + 1 coefficients (this model's fast_division,
    the block products of stage D)"""
    return fast_division(2 * m + 1, m + 1)


def ld_zscan(m):
    """AMORT: the scans past zero leading coefficients of abnormal remainders (trim, 11 per coefficient): a remainder of index j is formed at most twice per level of the recursion
    and has deg q_j - 1 such zeros, sum_j (deg q_j - 1) <= m; levels <= bit length of m"""
    return 2 * 11 * m * m.bit_length()


def gcd_cost_ld(m, dG, b, sx, sy):
    """poly_gcd_own of 1aa56884 4.4 on the normal remainder sequence, with the top node on pieces when sx, sy are (low, high) pairs; AMORT: + ld_fastdiv(m) + ld_zscan(m)"""
    T = Tr(b)
    lx, ly = m + 1, m
    pieces = isinstance(sx, tuple)
    topcut = int(sx[0]) if pieces else 0
    T.ctl(3); T.ctl(3)
    tail = False
    while ly > 0:
        T.ctl(2)
        n = lx - 1
        T.ctl(4)
        if n <= 2 * 96:
            sq = T.new_fp(lx - ly + 1); sr = T.new_fp(lx)
            last = (ly == dG + 1)
            dc, lq, lr, _ = divrem_naive(lx, ly, term_zero=1 if (last and dG >= 1) else 0)
            if last and dG == 0: lr = 0
            T.ctl(dc + LD_ABORT)
            T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
            T.free(sq); T.ctl(5)
            continue
        k = (n + 1) // 2
        if k < LD_KSCR: tail = True
        if pieces and lx == m + 1:
            t, o = hgcd_top_ld(lx, ly, k, topcut, T.here(), (sx[1], sy[1]), (sx[0], sy[0]))
        else:
            t, o = hgcd(lx, sx, ly, sy, k, False, 3, True, True, T.here())
        T.add(t)
        lc, sc, ld, sd = o[0], o[1], o[2], o[3]
        T.ctl(LD_ABORT)                                       # the return test
        T.ctl(2)
        dqm = lc if WC_MEM else lc - ld
        sq = ld_new(T, dqm + 1, 'outer')
        sr = ld_new(T, lc, 'outer')
        if WC_MEM: T.bump_blocks(wc_div_arrays(lc, dqm))
        T.ctl(3)
        dc, lq, lr, _ = divrem_naive(lc, ld)
        T.ctl(dc + LD_ABORT)                                  # the quotient test
        T.free(sc); T.free(sq)
        sx = sd; lx = ld; sy = sr; ly = lr; T.ctl(5)
    T.free(sy)
    if tail and LD_CONV['scratch']: T.ctl(40)
    T.ctl(2)
    T.ops += powcost(PM2); T.ctl(INV_CTL); T.ld(1)
    T.ops += lx - 1
    T.ld(lx); T.st(lx); T.loopc(lx)
    if AMORT:
        LD_LOG['fastdiv'] = ld_fastdiv(m); LD_LOG['zscan'] = ld_zscan(m)
        T.ops += LD_LOG['fastdiv'] + LD_LOG['zscan']
    return T, (lx, sx)


# ---------------------------------------------------------------- the allocator of proof 4.2 on the walk: two-ended pool for the big blocks, slab classes for the others
def _big_events(ev, T, memo):
    """the events of the two-ended pool (blocks of more than T bytes, header included) in ev, sizes in bytes; None if there is none"""
    out = []
    for e in ev:
        t = e[0]
        if t == 'A':
            if blk(e[2]) > T: out.append(('A', e[1], blk(e[2]), e[3]))
        elif t == 'F':
            if blk(e[2]) > T: out.append(('F', e[1]))
        elif t == 'T':
            sz = tuple(blk(x) for x in e[1] if blk(x) > T)
            if sz: out.append(('T', sz, e[2]))
        elif t == 'R':
            sub = _big_events(e[2], T, memo)
            if sub: out.append(('R', sub))
        else:
            if id(e[1]) not in memo: memo[id(e[1])] = _big_events(e[1].ev, T, memo)
            if memo[id(e[1])]: out.append(('C', memo[id(e[1])], e[2], e[3]))
    return out or None


class FirstFit:
    """one list of the pool: its blocks [size, id] (id None = free) in address order counted from the list's own end of the pool, no two free blocks adjacent, the unused middle of the
    pool beyond the last block.  An allocation takes the free block nearest its own end with at least `need` bytes, else the unused middle; it takes the side of the block nearest its own
    end, and the rest stays a free block if it is at least 128 bytes (else it is part of the allocated block).  A free merges the block with a free neighbour on either side, and with the
    unused middle.  end = the extent of the list (the far side of its outermost block)."""
    def __init__(self): self.L = []; self.end = 0; self.scans = 0; self.nblk = 0

    def alloc(self, i, need):
        L = self.L
        for k in range(len(L)):
            b = L[k]
            if b[1] is None and b[0] >= need:
                rem = b[0] - need; b[1] = i
                if rem >= 128:
                    b[0] = need; L.insert(k + 1, [rem, None])
                self.scans += k + 1
                return
        self.scans += len(L) + 1
        L.append([need, i]); self.end += need
        self.nblk = max(self.nblk, len(L))

    def free(self, i):
        L = self.L
        k = next(k for k in range(len(L)) if L[k][1] == i and L[k][1] is not None)
        b = L[k]; b[1] = None
        if k + 1 < len(L) and L[k + 1][1] is None:
            b[0] += L[k + 1][0]; del L[k + 1]
        if k > 0 and L[k - 1][1] is None:
            L[k - 1][0] += b[0]; del L[k]; k -= 1; b = L[k]
        if k == len(L) - 1:
            self.end -= b[0]; del L[k]


class TwoEnd:
    """the pool of proof 4.2: one region, list 0 grows from the bottom, list 1 (the statements marked `# pool:H`) from the top, the unused middle between them.  An allocation uses the
    list of its statement only; a free goes back to the list of its block.  high = the largest sum of the two ends; the pool has high + 128 bytes, so the middle is never shorter than 128 bytes."""
    def __init__(self): self.P = (FirstFit(), FirstFit()); self.where = {}; self.high = 0

    def alloc(self, i, need, c):
        self.where[i] = c; self.P[c].alloc(i, need)
        self.high = max(self.high, self.P[0].end + self.P[1].end)

    def free(self, i): self.P[self.where.pop(i)].free(i)

    def snap(self): return tuple(tuple(tuple(b) for b in Q.L) for Q in self.P)


def _ff_run(P, ev, base, ext):
    for e in ev:
        t = e[0]
        if t == 'A': P.alloc(ext[-e[1] - 1] if e[1] < 0 else base + e[1], e[2], e[3])
        elif t == 'F': P.free(ext[-e[1] - 1] if e[1] < 0 else base + e[1])
        elif t == 'T':
            for k, s in enumerate(e[1]): P.alloc(('t', k), s, e[2])
            for k in reversed(range(len(e[1]))): P.free(('t', k))
        elif t == 'R':
            before = P.snap()
            _ff_run(P, e[1], base, ext)
            assert P.snap() == before, 'a repeated group does not restore the pool'
        else:
            _ff_run(P, e[1], base + e[2], tuple(None if x is None else (ext[-x - 1] if x < 0 else base + x) for x in e[3]))


def slab_class(need): return max(QMIN, (need - 1).bit_length())            # the slot of a block of `need` bytes is 2^class bytes


def _slab_walk(ev, T, memo):
    """for each slab class (blocks of at most T bytes): (net, peak) number of live blocks of the events, relative to the entry"""
    cur = collections.defaultdict(int); pk = collections.defaultdict(int)
    for e in ev:
        t = e[0]
        if t == 'A':
            if blk(e[2]) <= T:
                c = slab_class(blk(e[2])); cur[c] += 1; pk[c] = max(pk[c], cur[c])
        elif t == 'F':
            if blk(e[2]) <= T: cur[slab_class(blk(e[2]))] -= 1
        elif t == 'T':
            for c, n in collections.Counter(slab_class(blk(x)) for x in e[1] if blk(x) <= T).items(): pk[c] = max(pk[c], cur[c] + n)
        else:
            if t == 'R': net, pe = _slab_walk(e[2], T, memo)
            else:
                if id(e[1]) not in memo: memo[id(e[1])] = _slab_walk(e[1].ev, T, memo)
                net, pe = memo[id(e[1])]
            for c in set(net) | set(pe):
                pk[c] = max(pk[c], cur[c] + pe.get(c, 0)); cur[c] += net.get(c, 0)
    return dict(cur), dict(pk)


def _walk_sum(ev, memo):
    """(net bytes, peak bytes, net blocks, peak blocks) of the events, relative to the entry: the live-set walk, recomputed from the events"""
    cur = pk = cnt = pc = 0
    for e in ev:
        t = e[0]
        if t == 'A':
            cur += blk(e[2]); cnt += 1; pk = max(pk, cur); pc = max(pc, cnt)
        elif t == 'F':
            cur -= blk(e[2]); cnt -= 1
        elif t == 'T':
            pk = max(pk, cur + sum(blk(x) for x in e[1])); pc = max(pc, cnt + len(e[1]))
        else:
            if t == 'R': r = _walk_sum(e[2], memo)
            else:
                if id(e[1]) not in memo: memo[id(e[1])] = _walk_sum(e[1].ev, memo)
                r = memo[id(e[1])]
            pk = max(pk, cur + r[1]); pc = max(pc, cnt + r[3]); cur += r[0]; cnt += r[2]
    return cur, pk, cnt, pc


QE_BYTES = 16 * 1024 + 512              # stage E and the later stages: at most 16 live arrays of at most 17 elements (a slot of 1,024 bytes each), taken from the slab classes; and the 48 words of the allocator (47 free-list heads, the end of the slab area)


def pool_account(stage_ev, big_exp):
    """the arena of one trial for the allocator of proof 4.2: stage_ev = [(name, events)] in the order of the program (init, A, B, C, D).  Blocks of more than 2^big_exp bytes come from the
    two-ended pool (TwoEnd, simulated address by address on the events), the others from the slab classes (a slot of 2^class bytes; a class takes a new slot from the end of the slab area when
    its free list is empty, so that the area is the sum over the classes of the peak number of live blocks times the slot).  The pool has `high + 128` bytes (high = the largest sum of the two ends; the unused middle
    is then always at least 128 bytes)."""
    T = 1 << big_exp
    P = TwoEnd(); bm = {}; sm = {}; wm = {}
    cur = collections.defaultdict(int); pk = collections.defaultdict(int); per = {}
    wcur = wpk = wcnt = wpc = 0
    for name, ev in stage_ev:
        f = _big_events(ev, T, bm) or []
        _ff_run(P, f, 0, ())
        per[name] = P.high
        net, pe = _slab_walk(ev, T, sm)
        for c in set(net) | set(pe):
            pk[c] = max(pk[c], cur[c] + pe.get(c, 0)); cur[c] += net.get(c, 0)
        if name == 'init': post = (P.snap(), {c: n for c, n in cur.items() if n})
    assert P.snap() == post[0] and {c: n for c, n in cur.items() if n} == post[1], 'a trial does not return the allocator to its state after init (the second trial would differ)'
    slab = sum(pk[c] << c for c in pk)
    arena = (P.high + 128 + slab + QE_BYTES + 63) & ~63
    return dict(T=T, big_exp=big_exp, big_high=P.high, big_stage=per, slab=slab, slab_peaks={c: pk[c] for c in sorted(pk)}, arena=arena, scans=P.P[0].scans + P.P[1].scans, big_blocks=P.P[0].nblk + P.P[1].nblk,
                big_final=P.snap())


def walk_check(stage_ev):
    """the live-set walk recomputed from the events: (bytes in use, peak bytes, blocks, peak blocks) of each stage"""
    memo = {}
    return {name: _walk_sum(ev, memo) for name, ev in stage_ev}


IMAGE_EXTRA = 399216 + 32 + 4851196        # text + data + static bss besides the arena (proof section 7)
STACK = 65536


def ceil3(x): return math.ceil(x * 1000) / 1000


def twiddle_slots(m):
    a = 2
    while 3 * (1 << a) < 2 * m - 1: a += 1
    return (1 << min(a, BIGA)) // 2                           # init_stage: the table of nmax/2 elements, nmax = 2^min(a, 32)


def stage_AB(m):
    """the arrays of the stages before C: the twiddle table (init), g (stage A), the block array of the cosets of stage B (freed after the inverse transforms) and F"""
    assert m + 1 > (1 << BIGA)                                # block mode of stage B (the three cosets): no transform of 2^a >= m + 1 points exists
    Pl = make_plan(3, BIGA - 1)[0]; ncos = -(-(m + 1) // Pl.N); H = ncos * Pl.N
    I = Tr(0); I.new_fp(twiddle_slots(m))
    pcs = ld_pieces(m) if (vd_active(m) and ld_pieces_on()) else None     # LEAND: g (and R) in two pieces [0, cut), [cut, n1) for the top node of stage D (lemma 4.8(b))
    A = Tr(1)
    if pcs: sg = (A.new_fp(pcs[0]), A.new_fp(pcs[1]))  # pool:H
    else: sg = A.new_fp(vd_gslots(m) if vd_active(m) else m + 1)  # pool:H
    B = Tr(2); sb = B.new_fp(H); B.free(sb)  # pool:H
    sF = None if vd_active(m) else B.new_fp(fslots(m))                 # VDC: no array F (R leaves stage C in an array of its own)
    return I, A, B, sg, sF


def main():
    global WORST_D, WC_MEM, LD_CFV
    m = (5 ** 23 - 1) // 2
    set_outer_limit(m)
    assert not any(LD_CONV.values())                           # this model's charges for every primitive (the other conventions are a comparison tool only)
    if LEAND: assert vd_active(m) and bool(NORMALD) != bool(AMORT), 'LEAND needs VDC and exactly one of NORMALD, AMORT'
    LD_CFV = LD_CF if LD_CF is not None else (m // CHUNK_D if CHUNK_D else None)     # the chunk bound of the scheme (c) products of the lean stage D
    def stages():
        global VD_SPLIT
        hgcd.cache_clear()
        I, A, B, sg, sF = stage_AB(m)
        pcs = isinstance(sg, tuple)
        VD_SPLIT = 2 if pcs else 0                             # g and R in two pieces: the base of a coset is selected (a comparison and a branch) at every coset access of stage C
        C, cinfo = powx_lean(m, 3, PM1H, sg); C.ctl(STAGE_BK)
        VD_SPLIT = 0
        db = 3 + (2 if pcs else 0)                             # live blocks at the entry of stage D: the twiddle table, g and R (two pieces each with the pieces)
        D = Tr(db); D.ctl(STAGE_BK); D.ops += 1; D.ctl(11)
        t, (lg, sgg) = gcd_cost(m, 0, db, cinfo['sg2'], cinfo['sR2'] if vd_active(m) else sF)
        D.add(t); D.ctl(2); D.free(sgg)
        return C, cinfo, D, (I, A, B)
    WORST_D = False; WC_MEM = False
    Cn, cinfo, Dn, _ = stages()                                # the normal local charge of the half-gcd tree, no division beyond the quotient of two coefficients
    WORST_D = not NORMALD; WC_MEM = not NORMALD
    if LEAND: WORST_D = False; WC_MEM = bool(AMORT)            # the lean stage D: no per-node recurrence (NORMALD: the normal sequence with the quotient and return tests; AMORT: one fast division of length m, its arrays held)
    C, cinfo, D, (I, A, B) = stages()                          # the earlier worst-case model (off under LEAND, NORMALD), summed over the tree (NORMALD: the normal sequence with the abort tests); every allocation walked
    print('m =', format(m, ','), '| transform sizes', cinfo['PN'].N, cinfo['PNp'].N, '| squaring steps', cinfo['steps'], 'of which with S:', cinfo['nset'])
    print('S_C =', format(C.ops, ','))
    print('S_D normal local charges of the tree =', format(Dn.ops, ','))
    if LEAND and NORMALD: print('S_D of the lean stage D on the normal remainder sequence, with the quotient and return tests =', format(D.ops, ','))
    elif LEAND: print('S_D of the lean stage D: the normal-sequence trace with the tests, one fast division of length m and the zero-scan allowance =', format(D.ops, ','))
    else: print('S_D with one full division at every node (and the outer loop, and the closing loop) =', format(D.ops, ','))
    print('S_D =', format(D.ops, ','))
    tws = twiddle_slots(m); twb = blk(tws); g_b = blk(m + 1); F_b = blk(fslots(m))
    pA = twb + A.peak; pB = twb + g_b + B.peak
    pC = twb + g_b + F_b + C.peak; pD = twb + g_b + F_b + D.peak
    if vd_active(m):      # the live set at the entry of each stage is what the earlier stages left
        pB = twb + A.cur + B.peak; pC = twb + A.cur + B.cur + C.peak; pD = twb + A.cur + B.cur + C.cur + D.peak
    peaks = dict(A=pA, B=pB, C=pC, D=pD)
    for x in 'ABCD': print('peak of the live set, stage %s = %s bytes' % (x, format(peaks[x], ',')))
    # the allocator of section 4.2 on the sequence of allocations and frees of one trial (the second trial repeats it from the same state)
    stage_ev = [('init', I.ev), ('A', A.ev), ('B', B.ev), ('C', C.ev), ('D', D.ev)]
    walk = walk_check(stage_ev)                                # the events reproduce the walk: bytes in use, peak and live blocks of every stage
    for x, T_ in zip('ABCD', (A, B, C, D)): assert walk[x] == (T_.cur, T_.peak, T_.cnt, T_.pcnt), x
    pool = pool_account(stage_ev, BIG_EXP)
    print('two-ended pool: blocks of more than 2^%d bytes; largest sum of the two ends after each stage (bytes): %s; at most %d blocks; %s blocks examined in all'
          % (BIG_EXP, ', '.join('%s %s' % (k, format(v, ',')) for k, v in pool['big_stage'].items()), pool['big_blocks'], format(pool['scans'], ',')))
    print('slab classes (class: peak number of live blocks): %s; slab area = %s bytes' % (', '.join('%d: %d' % kv for kv in pool['slab_peaks'].items()), format(pool['slab'], ',')))
    arena = pool['arena']                                      # pool high-water + 128 + slab area + QE_BYTES, rounded up to 64
    mem = arena + IMAGE_EXTRA + STACK
    print('arena = %s bytes (two-ended pool %s + 128, slab classes %s, stages E and later %s), memory = %s bytes, log2 = %.3f'
          % (format(arena, ','), format(pool['big_high'], ','), format(pool['slab'], ','), format(QE_BYTES, ','), format(mem, ','), ceil3(math.log2(mem))))
    assert C.ops == 1401034985701489959010 and D.ops == 1286177092539484062135
    assert peaks == dict(A=190734962129895616, B=381469855540314368, C=762940056647814656, D=721616155584940992) and arena == 764059563745138560 and mem == 764059563750454540


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
