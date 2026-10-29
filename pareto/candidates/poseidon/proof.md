# Orchard Poseidon, r = 17: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, half-gcd on aligned budgets with the inversion-free node on three rows, one centre

## 1. Claim

Target: `poseidon-orchard-r17-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, seventeen partial rounds 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 and 20, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with a worst-case operation count (sections 6-7) and a success probability derived from the premises `H-ONE` (section 9.1) and `H-NORMAL` (section 9.5), statements about the usable roots of the fixed digest polynomial and its remainder sequences; section 9.2 derives the success probability from them with explicit constants.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation (the line program `L` of Appendix L in the root-table loop of Appendix B) and 925186 inverse transforms (one per coset, section 3), compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod in the value domain (section 4.6, the method of bradcush 1aa56884) and a half-gcd in the lean form of 1aa56884 (4.4.1), its budgets below `2^54` split at powers of two and every matrix-only call of budget `2^j - 1` (`6 <= j <= 31`) run on bradcush's inversion-free half-gcd on three rows (4bcabff8; 4.4.3), and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds (Appendix S), take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the one centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta + delta_C)^K - K (eps_iso + eps_coin) = q - delta - delta_C - eps_iso - eps_coin` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1: at least `0.3931 p` centres have between 1 and `DMAX = 16` usable roots), `delta = 0.003` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `delta_C < 2^-148.2` the stage-C zero test (proved, 9.2(b)), `eps_iso <= P[Bin(64, w) <= 3] = sum_(j <= 3) C(64, j) w^j (1 - w)^(64 - j) = 2.371e-15 < 2^-48` (each isolation round halves `deg G <= 16` with probability at least `w = 1/2 - 7.869e-40` whatever came before, and four halvings reach degree 1; lemma 9.4), `eps_coin < 2^-122`. The exact value is `0.390099999999997615`. The value of `q` is `0.3934693 - 0.3931 = 0.0003693` below `1 - e^(-1/2) = 0.3934693` (and `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound of 9.3(b)), the law of the usable roots in section 9.3, which is a theorem for the first two and three S-box layers on the deployed constants (9.3(c)).

* `time_log2 = 60.95242` in target-compression units (`C(17) = 573` primitive operations per unit): the worst-case operation count, derived in section 6 as `T_fixed + K * T_trial` with every trial charged in full (stage D for the normal remainder sequence, which bounds every trial because a trial with any other sequence ends after a prefix of that work, section 6.3; stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 1,278,384,030,871,839,189,844` operations, `log2(N_max / 573) = 60.95241995572471`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is at most `554,785` operations (`136,785` counted exactly for the 212 literals of the base and the bound of 6.2 for the literals of Appendices L and B), and charged at its declared cap of 1,000,000 operations; that cap is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 59.40491` (`763,233,830,447,488,172` bytes, section 7).
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `65` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^23`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against our r = 17 entry `61a57387` (time + memory penalty 100.36434, the same algorithm and package), four changes (credits in dependencies.json): (i) the base case of the inversion-free half-gcd of 4.4.3 has parameter 31 (was 63), so its nodes run for `6 <= j <= 31` (4.4.3); (ii) each line evaluation is one execution of the straight-line program `L` of Appendix L, `L(x) = F(x - E0_0) / OUTSCALE`, scaled lanes and sparse partial rounds, `135 + 12 r = 339` operations in place of the unit `C(17) = 573`: the form of mpjunior92's entry `1291df5c` (a credited tune-up of `61a57387`; listing form of its r = 10 entry `4c6dc4cf`, Appendix L), built by our own program from the organizer constants and checked against the reference rounds (L.2); (iii) the stage-B point loop visits the positions of the `925186` transform inputs in storage order and takes `s`, `1/(2s)` from digit-factored root tables and two running coset factors, the method of mpjunior92's r = 3 entry `1ac48175` on our cosets and mixed-radix layout (Appendix B): 18 operations per point beside the two evaluations in place of 252 (the 31-bit bit-reversed index and its call, the row counter and the two recurrences); (iv) stage E is register-resident, the procedure and charge form of `4c6dc4cf` Appendix S (as in `1291df5c`) with both gcds of 4.1.2 formed, so the lemma of 9.4 holds unchanged: `R(16) = 200,101` per round (Appendix S). Row B `13,162,919,785,736,610,792` (was `17,346,909,391,789,871,764`), row D `490,849,790,089,740,583,521` (was `492,884,823,047,532,535,981`), row E `12,807,664` (was `166,079,773`); rows A, C, F, G, the arena and the allocator walk are unchanged; `129,440` bytes are added (section 7): footprint `763,233,830,447,488,172` bytes (was `763,233,830,447,358,732`); `N_max` `1,278,384,030,871,839,189,844` (was `1,284,603,053,435,837,675,385`), time_log2 `60.95242` (was `60.95943`), normalized cost `100.35733` (was `100.36434`; `1291df5c`: 100.36120); H-ONE, H-NORMAL, the success bound and the experiments are unchanged.
* Against our r = 17 entry `ea38c298` (time + memory penalty 100.48567, the same algorithm and package), five changes: (i) stage D splits its budgets below `2^54` at powers of two and runs every matrix-only call of budget `2^j - 1` (`7 <= j <= 31`) on the inversion-free half-gcd on three rows of bradcush's entry `4bcabff8`, ported as in our r = 3 entry `bcf8e01c` and our r = 22 entry `907f3c9e` (4.4.3); (ii) with the apply plans of 0xplemonade's entry `ff21bd28`, each apply of steps (2) and (6) of a half-gcd node runs the cheaper of its block products or single transform and a direct whole-pair or fixed-slot plan on one transform size (4.4.1 item 9); (iii) with the batch-inversion prefix of `ff21bd28`, stage C runs the batch inversion in chunks of `2^16` elements (its auxiliary array `2^16` elements, was `h`) and forms the `omega^e` of the `b = 1` boundary pass from two tables of `2^16` entries (was one table of `h` entries; 4.6); (iv) the layers of the block-form passes and of the column passes are split into passes of at most seven layers by the split of least charge, in place of seven at a time with the remainder in one pass (4.2; the exact pass split of 0xplemonade's entry `d4b13ccd`); (v) in the node of the inversion-free half-gcd (4.4.3), the four chunks of each of `a`, `b` are folded onto the three rows in one loop of 22 operations per position and each matrix-vector map of the node is one two-output pass of 20 operations per point (the fused two-output rows of 0xplemonade's entry `8b1eb62a`, read as text, priced by the direct apply row of `ff21bd28`). Row C `774,371,320,979,164,667,614` (was `774,939,955,238,989,735,670`), row D `492,884,823,047,532,535,981` (was `603,517,345,027,724,104,333`); `N_max` `1,284,603,053,435,837,675,385` (was `1,395,804,209,675,854,311,793`), time_log2 `60.95943` (was `61.07920`); the live peak of stage C `762,939,781,910,416,896` bytes (was `762,940,056,782,032,384`), the arena `763,233,830,441,051,264` bytes (was `764,060,663,235,442,560`); term (a) `71,008` bytes more code (7(a)); memory `763,233,830,447,358,732` bytes, memory_log2 `59.40491` (was `59.40647`). The premises, the success bound and the experiments are unchanged.
* Against our r = 17 entry `8346be35` (normalized cost 100.56544, the same algorithm and package): (i) the register file of the machine is one file of 387 words, 256 field registers of 256 bits (was 64) plus the 131 integer address registers of an `ob128` call, counted in the memory (7(d), 12,384 bytes), as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits: the column passes of stage C and of the outer transforms of stage D take up to seven layers (`ob64`, `ob128`) and the block-form passes of the products up to seven layers (blocks of 128 points with their 127 twiddles in registers); 4.2. (ii) In group 0 of every block-form pass a butterfly whose twiddle is 1 is its addition and subtraction, 2 operations (a straight-line variant of the block body, 3 control operations more per pass), as in the column kernels of `8346be35`; 4.2. (iii) The block loop of a group runs four blocks per pass of a straight-line body (a group of one block has no block loop): 3 control operations per block (was 5); 4.2. Row C `774,939,955,238,989,735,670` (was `808,554,829,734,367,600,124`), row D `603,517,345,027,724,104,333` (was `648,709,979,759,137,530,455`); arena `764,060,663,235,442,560` bytes (was `764,060,663,214,081,920`), code bound 7(a) +907,520 bytes for the straight-line bodies; memory claimed at five decimals, `59.40647` (was `59.407`); the count on an 18-register machine is unchanged. Every other charge, the premises and the experiments are unchanged. Change (i) alone was our entry `fdb6bc0e` (normalized cost 100.49855), refuted on F-REG-OVERCOMMIT because the integer registers were not declared; the submission note answers that ruling finding by finding.
* Against our r = 17 entry `ae66d079` (normalized cost 100.60536, the same algorithm and package): two kernel changes. (i) A column-kernel butterfly whose twiddle is 1 is charged 2 operations (its call at offset 0 a straight-line variant, 4.2). (ii) The block-form passes take up to five layers (blocks of 32 points; 32 data words, 31 twiddles and the temporary, the 64 words of the declared file, as `ob32`; 4.2). Row C `808,554,829,734,367,600,124` (was `824,685,508,081,126,888,160`), row D `648,709,979,759,137,530,455` (was `673,957,233,414,905,998,009`); plan sizes 56 (was 57); arena `764,060,663,214,081,920` bytes (was `764,060,663,208,617,856`), memory_log2 unchanged; on an 18-register machine `1,761,163,112,330,946,314,601` (was `1,779,836,319,669,219,139,254`). Every other charge, the premises and the experiments are unchanged.
* Against our r = 17 entry `ed1cce17` (normalized cost 100.67935, the same algorithm and package): the loads and stores of the block-form passes of 4.2 are charged one operation each (base plus index, as the column kernels `ob4` to `ob32`): row C `824,685,508,081,126,888,160` (was `827,342,355,038,777,214,608`), row D `673,957,233,414,905,998,009` (was `751,077,917,388,338,708,164`); arena `764,060,663,208,617,856` bytes (was `764,060,663,208,621,952`), memory_log2 unchanged. Every other charge, the premises and the experiments are unchanged.
* Against the same algorithm with the leaf passes of 4.2 in every product (normalized cost 100.74441): the transform passes of the products of stages C and D (all but the fused pass of each product) run in the block form of our r = 3 entries `ef123c2b` / `253629b9` (per group the `2^k - 1` twiddles held in registers), on the 64-word register file stated as a restriction in claim.json: row C `827,342,355,038,777,214,608` (was `830,501,778,318,643,481,801`), row D `751,077,917,388,338,708,164` (was `821,528,726,644,774,503,229`); arena `764,060,663,208,621,952` bytes (was `764,060,663,218,681,728`). Every other charge, the premises and the experiments are unchanged. On an 18-register machine (column passes of at most 3 layers and leaf passes) the count is `N_max = 1,779,836,319,669,219,139,254` (normalized cost 100.83685).
* Prior entry: this entry is the r = 17 version of our r = 7 algebraic entry 05a41d88 (the same algorithm, ledger method, premise structure and evidence design). The ruling on 05a41d88 (not_evaluable on the experiments lane) is answered here in the same way: the organizer experiments `line-ladder-w6`, `-w8`, `-w10` and `-w12` on the antipodal line pairs of this construction at r = 17 (10.2), the computations of Grok job 136 and their re-run on the deployed constants and the construction's line (10.3), and the measurement of the Euclidean sequences on the sibling targets (10.5). Stage C is the value-domain powering of bradcush's entry 1aa56884 (section 4.6), stage D its lean half-gcd (4.4.1), and stage D is charged for the normal remainder sequence under the premise `H-NORMAL` of bradcush (entries e6dcb600, 1aa56884) with gta6rp's allowance and organizer-run tests (9.5); all credited in the dependencies and the note.
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1) and `H-NORMAL` (score-critical for the success probability only, section 9.5). Both are statements about probability. `H-NORMAL` is bradcush's premise (entries e6dcb600 and 1aa56884), stated here with the allowance `delta = 0.003` and supported by organizer-run normality tests, the recipe of gta6rp's entries (c1364311 at this round count); the test program `experiments/exp_euclid.py` is our own (10.5.1). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2 on the machine stated as a restriction in claim.json (256 field registers of 256 bits plus 131 integer address registers; every load, store and spill counted), as the accepted entries `89b451ff` and `fb176310` state theirs and as our r = 3 entries `ef123c2b` and `253629b9` do, and the base-plus-index addressing of the stage-C column kernels (4.2), stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation. Everything else is proved or counted here: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the success bound (section 9.2), the stage-C zero-test bound (9.2(b)), the isolation lemma (section 9.4), the uniformity of the centre, the cap rules and every operation count (sections 4, 6, 7).
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

Construction of `g_c` by evaluation. At this r no transform of `H >= m + 1` points exists: `p - 1 = 2^32 * 3 * q'` has roots of unity of order `3 * 2^a` for `a <= 32` only, and `m + 1 = 5,960,464,477,539,063 > 3 * 2^32`. Let `B = 3 * 2^31 = 6,442,450,944`, `zeta` a primitive `2B`-th root of unity (`2B = 3 * 2^32` divides `p - 1`) and `omega = zeta^2`, a primitive `B`-th root. Let `kappa = ceil((m + 1) / B) = 925186`, `v_k = 2^k` and `u_k = v_k^2 = 4^k` for `k < kappa`, and `z = 4^B`; the `kappa` numbers `n_k = u_k^B = z^k` form a geometric progression and are pairwise distinct, because the order of `z` exceeds `kappa` (`z^d != 1` for every divisor `d` of `p - 1` up to `2 * 10^8`, and `kappa < 2 * 10^8`). The evaluation points are `s_{k,i} = v_k zeta^i` for `k < kappa`, `i < B`, so that `S_{k,i} = s_{k,i}^2 = u_k omega^i`, and `g_c(S_{k,i}) = (F(c + s_{k,i}) - F(c - s_{k,i})) / (2 s_{k,i})`. Write `g_c(x) = sum_{t < kappa} x^{tB} h_t(x)` with `deg h_t < B`. For `y = omega^i` we have `y^B = 1`, hence `g_c(u_k y) = w_k(y)` with `w_k(y) = sum_t n_k^t h_t(u_k y)`, a polynomial of degree `< B`. One inverse transform of size `B` of the values `(g_c(S_{k,i}))_i` returns the coefficients `w_k[j] = u_k^j sum_t n_k^t h_t[j]`. After multiplication by `u_k^{-j}`, for every `j < B` the numbers `W_k[j] = sum_t n_k^t h_t[j]` (`k < kappa`) are the values of the polynomial `h^(j)(X) = sum_t h_t[j] X^t` at the nodes `z^k`, and its coefficients `h_t[j] = g_c[j + tB]` are recovered from them by two correlations of length `kappa` (Lagrange interpolation at geometric nodes, the chirp-z form). Let `M(X) = prod_k (X - z^k) = sum_i mu_i X^i`; the q-binomial theorem gives `mu_{kappa-j} = (-1)^j z^{j(j-1)/2} [kappa choose j]_z`, and `M'(z^k) = z^{k(k-1)/2 + k(kappa-1-k)} prod_{j <= k} (z^j - 1) prod_{j <= kappa-1-k} (1 - z^j)`. With `a_k = W_k[j] / M'(z^k)` and `A(i) = sum_k a_k z^{ki}` (`i < kappa`) we have `h_t[j] = sum_{i > t} mu_i A(i - t - 1)`. Since `z^{ki} = z^{C(k+i,2) - C(k,2) - C(i,2)}` with `C(n,2) = n(n-1)/2`, `A(i) z^{C(i,2)}` is the correlation of the sequence `a_k z^{-C(k,2)}` with the chirp `z^{C(n,2)}` (first correlation), and `h_t[j]` is the correlation of `A` with `(mu_1, ..., mu_kappa)` (second correlation). Each correlation is one cyclic convolution of length `S = 2,097,152` (the smallest `2^a` or `3 * 2^a` that is at least `2 kappa - 1`), done with the transform of length `S` (forward, pointwise product, inverse); the transforms of the fixed sequences (the chirp and `mu`) and the constants `mu_i`, `1/M'(z^k)`, `z^{-C(k,2)}` are computed once per trial and shared by the `B` positions `j`. The `2 kappa B = 11,920,930,838,151,168` evaluations are executions of the line program `L` of Appendix L at `x = c' + s` or `c' - s` (`c' = c + E0_0`, one addition per trial): `L(x) = F(x - E0_0) / OUTSCALE`, `135 + 12 r = 339` operations at `r = 17`, so the stored values are `g_c(S_{k,i}) / OUTSCALE`, which the normalisation to monic absorbs; rounds 0 and 1 are not executed (section 2). `(F(c + s) - F(c - s)) / (2 s)` is even in `s`, so the point `-s_{k,i}` gives the value of `s_{k,i}`. The loop of Appendix B visits the positions of the `kappa` transform inputs in storage order and takes `s` and `1/(2s)` from digit-factored root tables and two running coset factors: per point the two table loads with their addresses and the two products 6, the two point additions 2, the two calls 2, one subtraction 1, one multiplication by `1/(2s)` 1, the store with its address and the pointer increment 3, the loop control 3: 18 operations beside the two evaluations; the cosets, rows, outer levels and tables are itemised in Appendix B. The solve (per `j`: two correlations, each two transforms of length `S` with `S/2 log2` butterflies at the charge of the model's own pass cost and `10 S` operations for the pointwise product and the scalings, and `14 kappa` operations for the chirp scalings, the division by `M'`, the loads and the stores) and its once-per-trial constants (`kappa` times two inversions, 40 operations per index, four transforms of length `S` and `10 S` operations) are charged on top.

## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (11,920,930,838,151,168 executions of L, Appendix L, in the loop of Appendix B + 925186 inverse NTTs of size 6,442,450,944 + the geometric solve of the 925186 cosets (two correlations of length 2,097,152 per position) + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; value domain, section 4.6: from S^v, v = 2^50; 203 squaring steps, 45 of them also multiply by S, pointwise)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2, Appendix S).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (573 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 52 bits after the leading one are zero, so the algorithm starts from the monomial `S^v` with `v = 2^50` (a multiple of h below m, 4.6, `VSHIFT = 2`; 50 + 203 = 253), and the loop of stage C has 203 steps, of which 45 also multiply by `S` (pointwise).

Stopping rule. The loop bound `K = 1` is a constant of the algorithm: one centre is tried. A trial is run to its end, or to an ABORT of stage D on an abnormal remainder sequence (6.3) or of stage C on a zero of g on O1 (4.6 step 5), which then resets the allocator and draws the next centre; the claim charges every trial at its maximum (stages E to G at their worst case, section 6), so a trial that fails early is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3, 4.4), the powering has a fixed number of steps, and the half-gcd has a fixed recursion: 46 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 2,980,232,238,769,531` and is halved, rounded up, until it is at most 96) and at most 46 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 5,960,464,477,539,062 to at most 192). Hence, with stage D charged for the normal remainder sequence and every other sequence ending its trial after a prefix of that work (section 6.3), the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success, by an ABORT of a trial (the next centre is then drawn), or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

The only randomness is the cost-model random-word primitive. The words are fresh, independent and uniform on `[0, 2^256)`. A centre is `c = w mod p` for one word `w` (at most three conditional subtractions); the isolation of stage E draws at most 64 further words, reduced the same way. At most 65 words per run; a draw is 31 operations. There is no rejection and no retry. The reduction is not exactly uniform on `F_p`: `2^256 = 3p + r` with `0 < p - r = 4(p - 2^254) < 2^127.1`, so every residue has 3 or 4 preimages and `w mod p` is within statistical distance `r (p - r) / (p 2^256) < 2^-128.9` of uniform on `F_p`. Over the 65 words the distance is `eps_coin <= 65 * 2^-128.9 < 2^-122`, and the success bound (9.2) subtracts it.

#### 4.1.2 Stage E: isolating a root of G

`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). The roots `r` of `G` are the usable `S`. While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw `a` (a draw as in 4.1.1; if it is 0, `a := 1`, since the Taylor shift uses `1/a`; the zero test is 5 operations and the replacement 2, charged in every round), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). This entry runs each round as the register-resident procedure of Appendix S, which forms the same `G_+` and `G_-` without the Taylor shift (a root `r` of `G` lies in `G_+` iff `(r + a)^((p-1)/2) = 1`). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds: a round separates two given roots for at least `(p-3)/2` shifts, so it halves the degree with probability at least `w = 1/2 - 7.869e-40`, and four halvings take `16` to `1`; the failure probability is at most `P[Bin(64, w) <= 3] = 2.371e-15`, a finite sum, no premise.

### 4.2 Machine model and charging rules

Every operation of the algorithm is counted where it executes; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation). Exception, the column kernels `ob4`, `ob8`, `ob16`, `ob32`, `ob64`, `ob128`, `ob4m` and the two boundary passes of the loop of stage C (4.6), and the kernels `ob4` to `ob128` in the outer transforms of stage D (4.4.1, item 6): each load or store is 1 operation with no address operation. An element of the call's block at the position `j` is addressed as row base plus position offset, and a twiddle or spectrum word of the call as the table base plus the call's index scaled by a constant of the layer, the base-plus-index addressing of the load itself; the `2^k` row bases and the twiddle address are formed once per call (in the call charge `2 * 2^k + 6`, which is added to the kernel's per-call constant below; neither contains the other) and held in integer registers, and the position offset advances with the index update of the loop step. Everywhere else (the rest of stage D, the `ob2` and `ob3` passes and the first and last passes of an extension of stage C included) the address operation is charged as above.
* every loop: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). Loops over the elements of an array written eight elements per pass (the pointwise, copy, fold and subtraction loops of the powering and of the products) are charged 3 per pass of eight, 1 for the bound, 2 when the main loop is left, and 3 per iteration for the remaining 0 to 7 elements.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, comparison, conditional branch, assignment of a register, and the selection of an element of the register block (at most 32 data words) by a computed index. Data-dependent tests are charged per executed test.
* index arithmetic uses only shifts, additions, subtractions, comparisons and branches (the benchmark's primitive list has no integer multiplication, division or modulo): a multiplication by a power of two is a shift, by 3 or 5 a shift and an addition, and a product of an index and a stride is a running sum; each is charged as a control operation where it occurs.
* transforms: a transform of size `3 * 2^a` is a twiddle-free radix-3 stage (8 operations per leaf) followed by three rows of radix-2 passes of at most seven layers (the layers of each transform are split into passes by the exact minimum of the charges of this section: over every split of its layers into passes of `k <= 7` layers, the sum of the charges of a pass of `k` layers from layer `l0` of a row of `2^a` points, with the group-0 variant below, is least; the layers of the column passes of stage C and of the outer transforms of stage D are split the same way, by the least sum of the column-pass charges over passes of up to seven layers; the exact pass split of 0xplemonade's entry `d4b13ccd`). A pass works on blocks of `2^k <= 128` points held in registers, in the block form of our r = 3 entries `ef123c2b` and `253629b9` (their `pd_fwdp`, `pd_invp`): per block its `2^k` loads and `2^k` stores (1 each: a block element is addressed as the table base plus its index, the base-plus-index addressing of the load or store itself, as for `ob4` to `ob128` above; one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`), `k 2^(k-1)` butterflies at three field operations each (two where the twiddle is 1 in group 0, below) and 3 of control (2 for the base of the block and 1 for its share of the block loop, below); per group its `2^k - 1` twiddles formed and held in registers for all its blocks (24 operations for `k = 4`: two loads with their addresses, one multiplication, three squarings, eleven multiplications by register constants and control; 16 for `k <= 3`; for `k = 5, 6, 7` its `2^k - 1` twiddles are loaded from the twiddle table, 1 each (base plus index, as for `ob32`), with 9 operations of address formation and control, `2^k + 8`: 40, 72, 136); per pass `5 + (9k + 2) + 12` (forward) or `6 + (9k + 2) + 12` (inverse) of pass set-up. Block loop: a pass of `k` layers at layer `l0` of a row of `2^a` points has `2^l0` groups of `n = 2^(a - l0 - k)` blocks; `n` is a constant of the pass, stored with the other parameters of the pass in the plan of the product, and the pass is entered at the body for its `n`. A group of `n >= 4` blocks runs them four per pass of a straight-line body (the four blocks addressed as the block base plus the constants 0 to 3 times the block stride in the loads and stores themselves), loop control `1 + 3 n / 4 + 2 <= n` for `n >= 12` (at r = 17 every group of more than one block has `n >= 16`); a group of one block has no block loop. So 1 per block covers the block loop. Twiddle 1 in the block-form passes: the twiddles of a group depend only on the group and the layer, and in group 0 the first twiddle of each layer is `w^0 = 1`; in every block of group 0 the butterflies of these twiddles, `2^(k-1-j)` in the layer `j = 0, ..., k-1` of the pass, `2^k - 1` per block, are their addition and subtraction, 2 operations. Group 0 of every block-form pass (forward and inverse) runs a straight-line variant of the block body without these multiplications: `2^k - 1` operations less per block of group 0 (`2^(a - l0 - k)` blocks) and 3 control operations more per pass. The one pass of a product that fuses its last forward layers, the pointwise product and its first inverse layers keeps the charge of a leaf pass: each butterfly is three field operations (none for the multiplication when the twiddle is 1), each twiddle is one load with its address operation. The first twiddle of a layer is read through a running pointer of that layer, held in an integer register with its stride: moving it to the next block of the group is 1 operation (a pass call forms the `k` strides, one shift per layer, and for an inverse pass also the shift counts (one addition per layer) and its base pointer (a shift and an addition); each group sets its `k` pointers for block 1 anew, 1 operation per layer, and a range of blocks that does not start at block 1 sets them by a shift and an addition per layer). The blocks of a group after the first are processed four at a time by a straight-line body, then one at a time for the 0 to 3 that remain; for `n` such blocks the loop control is `1 + 3 floor(n / 4) + 2 + 3 (n mod 4) + 2` operations (the bound `n & ~3`, 3 per pass of four, 2 when the main loop is left, 3 per remaining block, 2 when the second loop is left), and the group loop is charged 3 per iteration; the pointers, strides, shift counts and loop counters are integer registers. The register file is the machine restriction of claim.json: one register file of 387 words, 256 field registers of 256 bits plus 131 integer (address) registers (as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits), counted in the memory (7(d)), every other value charged as a load or store (a block-form pass uses at most 256: the 128 data words, 127 twiddles and the butterfly temporary, as `ob128`; the fused leaf pass 18: the 16 data words, the twiddle operand and the butterfly temporary; the stage-C pass `ob128` uses 256: 128 data words, 127 twiddles and the butterfly temporary), and the 131 integer registers of the file for a call of `ob128` (the 128 row bases, the twiddle address, the position offset and the loop bound; fewer in the smaller kernels). Stage C (4.6) and the outer transforms of stage D (4.4.1, item 6) use column kernels: a column pass of `k` radix-2 layers (`k <= 7`, in stage C and in the outer transforms of stage D) runs over `2^k` rows at `cnt` positions and keeps its `2^k - 1` twiddles in registers for the whole position loop (`ob8`: 8 data words, 7 twiddles and the butterfly temporary, 16 of the 18 words; `ob4`: 4 + 3 + 1). Per position it loads `2^k` elements, makes `k 2^(k-1)` butterflies at 3 operations each (2 where the twiddle is 1, below) and stores `2^k` elements, each load or store 1 (base-plus-index, above); the position loop is written eight positions per pass (the eight positions of a pass are addressed by the position offset plus the constants 0 to 7 in the loads and stores themselves, and the offset advances once per pass), so its control is `F(cnt) = 1 + 3 floor(cnt / 8) + 2 + 3 (cnt mod 8) + 2` per call (the eight-element loop rule above), not 3 per position. Charges: `ob128` `269 + 1600 cnt + F(cnt)`, `ob64` `139 + 704 cnt + F(cnt)` (per call their 127 or 63 twiddles loaded at 2 each, a load with its address operation, 3 of control and 2 per layer after the first: `269 = 254 + 3 + 12`, `139 = 126 + 3 + 10`; per position `2^k` loads and `2^k` stores and `k 2^(k-1)` butterflies at 3: `1600 = 256 + 1344`, `704 = 128 + 576`), `ob32` `34 + 304 cnt + F(cnt)`, `ob16` `18 + 128 cnt + F(cnt)`, `ob8` `10 + 52 cnt + F(cnt)`, `ob4` `6 + 20 cnt + F(cnt)`, and for the radix-3 stage and a one-layer remainder `ob3` `7 + 22 cnt + F(cnt)` and `ob2` `5 + 11 cnt + F(cnt)` (their loads and stores 2 each with the address operation); a call of a column kernel of `k` layers costs `(2 * 2^k + 6) + c0 + c1 cnt + F(cnt)` plus 3 for the loop over the calls (and 2 when it is left), and its per-call constant `c0` is its `2^k - 1` twiddle loads (1 each) and 3 control operations (`34 = 31 + 3`, `18 = 15 + 3`, `10 = 7 + 3`, `6 = 3 + 3`; the boundary passes and `ob4m` of 4.6 likewise: their twiddle and spectrum loads and 3 or 5 control operations); per position `2^k` loads and `2^k` stores (1 each), `k 2^(k-1)` butterflies at 3 (`304 = 64 + 240`) (a run of `L` layers is cut into passes of at most seven layers by the split of least charge, a dynamic program over the layer boundaries on the charges above at the run's row count and positions, a constant of the algorithm for each run); the outer transforms of stage D use the same kernels with the same charges (4.4.1, item 6). In the outer transforms of 4.5 outside stage D, `ob3` and `ob2` keep a loop step of 3 per position (`7 + 25 B`, `5 + 14 B`, 4.5). The four 256-bit constants of the twiddle-free radix-3 stage of the transforms above (`W3[1]`, `W3[2]` and the two constants of the inverse and row kernels) are loaded into four registers once per call of a region driver of the stage (4 loads, 8 operations) and used from the registers; the position kernels of that stage use at most 6 words of the file for their own data, so the 4 constants and these words are within the 18 words. Twiddle 1 in the column kernels (the convention of the fused leaf pass above and of 1aa56884: a butterfly whose twiddle is 1 is its addition and subtraction, 2 operations): a column pass of `k` layers on a row of `2^a` points runs from the large-span end (forward) or towards it (inverse), and the butterflies with twiddle 1 of its layers are those at offset 0 of each block, `2^j` in its `j`-th layer, all in the call at offset 0 of each block (`2^k - 1` per position; `2^n - 1` per position over a run of `n` layers of a row); that call is a straight-line variant of the kernel without their multiplications, 1 operation less per such butterfly and position and 3 control operations more per such call. In the two-layer passes at the small-span end (the `ob4` pass of an inner transform, `ob4m` and the two boundary passes of 4.6) 3 of the 4 butterflies of each position and direction have twiddle 1 (both of the layer of span 2, one of the layer of span 4): 3 operations less per 4 points and direction.
* random words: the cost model's random-word primitive (an independent uniform 256-bit word) is one operation per word. The word of a draw is also loaded, stored into the cell `y` of the draw and addressed (one load, one store and three control operations), 6. A draw is that word (6), the reduction modulo `p` (three steps each of a comparison, a conditional branch and a field subtraction, 9, with the loop control of three iterations, 11), the conversion of the result to the internal representation (1), the entry (2) and the address of `y` (2): 31 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: 573 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation: every array is taken from one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes (`need` bytes), and `need` decides the allocator. A block of more than 2^43 = 8,796,093,022,208 bytes comes from the pool, one region with two ends: its blocks follow each other in address order, each with a header (size, size of the previous block, in-use flag), no two free blocks are adjacent, and the unused middle between the two ends is one free block. Each allocation statement of the program uses one end of the pool, a constant of the statement: the statements (`g` of stage A, the block array of stage B, `MU` and `Y`, the work arrays of the Newton products, of a squaring step (in a chunked product of a squaring step, all its arrays except the accumulators of the square `R^2`, which use the low end) and of a shift, and the results inside the half-gcd: the quotient and remainder of a node and of the outer loop, the outputs of apply_inv, of the matrix products and of mul_add_q2, every allocation of the lean stage D (`ld_new`, all sites `# pool:H`, including the working arrays of its block products), and the reversed `g` and the operand rev(X^v P1) of stage C step 1 (4.6)) use the high end, every other statement the low end, except that the copies of the remainders returned by a node that applies its second matrix (4.4, step (6)) are taken from the low end. A low request walks the blocks upward from the bottom of the pool, a high request downward from the top (the two sizes in the header give both neighbours, so the two walks are the same code mirrored); it takes the first free block with at least `need` bytes (the unused middle is the last block of either walk) and cuts the block from the side nearest its own end, and the rest stays a free block when it is at least 128 bytes (else it belongs to the block); a free merges the block with a free neighbour on either side, the unused middle included, the same code for both ends. Since no two free blocks are adjacent and a walk ends at the middle, a walk examines at most 2 P + 1 blocks, P the live blocks on its side of the pool, and one block examined is 13 operations (two comparisons with branches, two loads, the advance). A block of at most 2^43 bytes comes from the slab classes: the class `j` is the least `j >= 7` with `2^j >= need`, a slot is `2^j` bytes; a request takes the first slot of the free list of its class, else a new slot from the end of the slab area, and writes the class and the in-use flag into the header; a free puts the slot on the free list of its class. The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows: a request of the pool 97 operations besides the walk (the statement that calls the allocator, the set-up, the split, the header stores, and a flat 64 for the statistics) and 13 per block examined, a request of a slab class at most `126` (the statement that calls the allocator, the class `j` by a binary search over 7..63 in 6 steps of 6 operations, the pop or the bump, the two header stores, and a flat 64 for the statistics), a free 81 for a slab block and at most 105 for a pool block (a free tests the size of the block to choose the allocator, in place of the test for a null pointer, which the program never needs). Every allocation of the walk is charged `1 + 120 + 13 (2 L + 1)` with L the live blocks at that point, which covers the pool (P <= L, the 97 operations and 13 per block examined) and the slab path (at most `126 <= 1 + 120 + 13` operations), and every free 105 (550 per allocation and 105 per free at 16 live blocks in stage E). The memory of both allocators is the arena of section 7.
* trial loop: the test of the trial counter, its increment and the bookkeeping of the trial, at most 12 operations per trial, are `TRIAL_EXTRA` = 12 in the ledger; the loop test and update of stage A are 5.
* the offline derivation of the constants is charged in section 6.2.

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
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: `(c, d) = hgcd(a, b, floor((n+1)/2))`, one division `c = q d + e` and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). With `H-NORMAL` (9.5) stage D runs the normal-sequence procedure of bradcush (entry e6dcb600): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter ; a zero remainder met inside hgcd or in the division of the outer loop also ends the trial (ABORT); on any other case the trial ends (ABORT) and the next centre is drawn (section 6.3).

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

#### 4.4.1 The lean stage D (this entry; the stage D of bradcush 1aa56884, its section 4.4 and lemmas 4.4 and 4.8, credited)

This entry runs the half-gcd above with six changes, all from 1aa56884 (credited in the dependencies and the note) and, in item 9, the apply plans of 0xplemonade ff21bd28 (credited likewise), charged by this model's rules of 4.2 and 4.5. They change where arrays live and which coefficients are formed, never a quotient: every quotient used is a quotient of the whole pair (lemma 4.4 above, and lemma 4.8 below).

1. *The base case in place.* For `k <= 96` the two remainders are two arrays and a division step with a quotient of two coefficients is one pass `r_k = a_k - q0 b_k - q1 b_(k-1)` written over the array of `a`; the roles of the two arrays swap. The four matrix entries are four arrays of `k + 2` elements allocated once, and `R := R Q` writes `r11 q + r12` over `r12`. No array is allocated or freed inside the loop.
2. *Matrix-only calls.* A call returns the reduced pair only when its caller wants it: the calls of the Euclid driver `poly_gcd_own` and, inside them, the second calls with `s3 <= 0`. Every call inside a first call, and every truncated second call, returns its matrix only.
3. *Windows.* In a node that wants its matrix only and has `s3 > 0`, the block products of `apply_inv` (or the plan of item 9) form only the top window of `c` and `d`: the coefficients of degree at least `s3 - 1` (lemma 4.8 (a)). Such a node tests that the coefficients of `c` and `d` at their normal leading degrees `la - h - 1` and `la - h - 2` are nonzero (2 tests, charged) and ABORTs otherwise, so it never reports a shorter remainder from a window.
4. *The two tests and the ABORT.* At every division the quotient test (the quotient has degree 1) and after every recursive call and every call of `poly_gcd_own` the return test (the call returned exactly its parameter as degree count; a zero remainder inside hgcd or in the outer-loop division also ABORTs), 2 operations each, charged wherever they execute. If a test fails the trial ABORTs: the allocator is reset to its state after initialisation (`1,000` operations, charged in section 6) and the next centre is drawn. On the normal remainder sequence neither test fails (6.3), so every division of stage D is the one-pass division by a quotient of two coefficients and the Newton division is never run.
5. *The top node in pieces.* Stage C leaves `g` and `R` in two pieces each, the coefficients `[0, cut)` and `[cut, l)` with `cut = 4,470,352,285,532,160`. The first call of `poly_gcd_own` frees the high pieces of `g` and `R` right after its own `apply_inv`; the pair `(c, d)` is then formed from the low pieces only (`c` first, by the block products of 4.5 with the window `[0, lc)`, `lc = m + 1 - k1`; then `r22` and `r12` are freed; then `d`; then `r11`, `r21` and the low pieces are freed). The pair `(d, e)` of the second call is written as two pieces at `cut2 = deg d + 1 - k3` and handled the same way.
6. *Block products of stage D.* Each product of apply_inv (unless the apply runs a plan of item 9), of the top node and of mat_mul uses the cheapest of the single transform, scheme (a) at block length 2^31 (one row of passes of 2^32 points) and scheme (c) at the block length 2^b of least charge (b = 6..31, transforms of 2^(b+1) points). The number of chunks is the least power of two that brings a chunk form to at most `m // 16` elements. The outputs are allocated first at their true lengths, the chunks accumulate into them, the working arrays follow and are freed at the end, and the operands are freed after the last chunk. This replaces, for stage D, the Blocks, Choice, stage-D and Scaling bullets of 4.5. There is no placement pass in stage D: each output of a scheme (c) product is untwisted straight into its window with the scaled weight `sign / (NB n2) * w^(-e)` (the sign of the output, the factor `1/NB` of the unnormalised inverse transform and `1/n2` of the outer transform applied here), charged 15 operations per product (the scale and the weight base), 7 per untwist call (the table entry and the scale loaded and the result stored, each 2 with its address operation, and one multiplication) and the chunk and outer-point loops; at r = 17 this is 43,320,818,875,032,208 operations per trial (1,040,802 scheme (c) products, 3,354,894,907,849,992 untwist calls), included in row D. These figures differ from those of our entry de55484d (68,722,733,100 products, 57,573,557,761,539,720 operations) only because the choice above now goes another way for many products (the single transforms of item 7, and the block products with the outer transforms below); the charge per product and per untwist call is as before. The outer transforms of scheme (c) are column passes across the outer points with the kernels and charges of stage C (4.2: `ob128`, `ob64`, `ob32`, `ob16`, `ob8`, `ob4`, `ob2` as the layer count needs, `ob3` for the radix-3 stage, a call `(2 * 2^k + 6) + c0 + c1 cnt + F(cnt)` at `cnt = B` positions, base-plus-index loads and stores, for each of the three rows when 3 divides `n2`), with the twiddle table of `n2` entries at 3 operations each (4.5); the assembly of a chunk, the untwist into the window and the fold of an outer point into the row of its chunk are loops of eight elements per pass (4.2), with 1aa56884's conventions for these three primitives (credited). The kernels `ocp`, `oax` and `ozf` of 4.5 are not used in stage D. The pieces of a product outside its window are dropped (never accumulated or untwisted): the cyclic wrap of length `n2` does not reach the window (4.5), so the window's coefficients do not depend on them. The choice between the single transform and the block products counts every charge of each path, including the allocations and frees the block path adds.

Two further changes, from weijiekoh a78f526e (its proof 4.4, `mat_mul`, `mat_apply` and the division step; credited), re-implemented and charged by this model's rules:

7. *Product forms.* (a) Scope: the whole-operand single-transform path of `apply_inv` only (the block products of item 6 and their top window are unchanged). On that path the single transform is sized by the output: its length `N` is the least admissible length with `N >= lc = la - h`, the length of `c`, not the operand length `la`. `c = s (r22 a - r12 b)` and `d` have degree below `lc` (the high coefficients cancel, step (2) of 4.4), so they equal their reductions mod `X^N - 1`, and the products are taken of the operands reduced mod `X^N - 1`: an operand longer than `N` is folded as it is read into the transform input, 10 operations per folded coefficient per row read (load, add, store, loop step). Folding the operands before the products and the subtraction is exact: reduction mod `X^N - 1` is a ring homomorphism, so `(r22 a - r12 b) mod (X^N - 1)` is the reduction of the same expression with each of `a`, `b`, `r12` and `r22` first reduced mod `X^N - 1`. (b) Each single-transform product of stage D (`apply_inv`, `mat_mul`) takes the cheaper by total charge of the transform of `3 * 2^a` points of 4.2 and a plain transform of `2^a'` points, `2^a'` the least power of two that holds the result, taken only when `a' <= 32` (roots of unity of order `2^a'` exist only for `a' <= 32`): one row of the radix-2 passes of 4.2 (the same kernels and twiddle table, no radix-3 stage, no reordering), each operand copied in at 7 operations per coefficient and the rest of the input zero-filled at 5 per slot (a store with its address operation and the loop step), the pointwise products and the inverse passes as for one row, the outputs read in place. The block products of item 6 are charged as before; only which products take them changes (item 6, the figures at r = 17).
8. *Division without inversion.* Every division by a divisor `d` of at most 2,048 coefficients (the steps of the base case and the node and outer-loop divisions of short pairs) is the scaled step `e = v^2 c - (A x + B) d` with `v = lc(d)`, `A = v lc(c)`, `B = v c_(n-1) - lc(c) d_(n-2)` (`n = deg c`; `d_(-1) = 0` when `deg d = 0`): no field inversion (5 field operations in place of the inversion and 4), one more multiplication per remainder coefficient (`v^2 c_i`), and the matrix update by `[[A x + B, 1], [v^2, 0]]`, one more multiplication per coefficient of the column it scales (`v^2 r_f`); all charged. Each remainder so formed is the exact one times a nonzero scalar of its own (if `c = lambda c*` and `d = mu d*`, then `e = v^2 lambda e*`; the two members of a pair generally carry different scalars), each matrix so formed is `D1 R D2` with `R` the exact matrix and `D1`, `D2` diagonal with nonzero entries (the inner factors between consecutive steps multiply to scalars), and `apply_inv` applies the adjugate, so in every pair `(c, d)` each member is a nonzero scalar multiple of the exact one: the degrees, the quotient degrees, the tests of 6.3 and the stopping rules are those of the exact sequence (they read degrees and whether a coefficient is zero), and `poly_gcd_own` makes the last nonzero remainder monic at the end (4.4). Longer divisors keep the inversion.
9. *Apply plans (the direct whole-pair and fixed-slot apply plans of 0xplemonade's entry `ff21bd28`, read as text, re-implemented and charged in this cost model).* An apply `(c, d) = adj(R1)(a, b)` of steps (2) and (6) of 4.4 (`c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `h = d_1`, `lc = la - h` and `ld = lc - 1` coefficients; in a node of item 3 only the coefficients from `w = s3 - 1` on) runs either the products of item 6 and the single-transform forms of item 7 or one of the two plans below, whichever has the smaller charge. The live peak of stage D with the plans is 741,758,100,658,197,120 bytes, below that of stage C (762,939,781,910,416,896 bytes), so no plan raises the memory (7). The lengths, budgets and windows of every call are fixed on the normal sequence (6.3), so this choice is a constant of the algorithm for each call of the walk: at r = 17, of the 1,275 distinct apply calls of the walk, 497 run a plan (348 direct, 149 fixed-slot; 148 of them on a window). A plan uses one transform size `N = 3 * 2^e`; both forms are priced at every `e = 2, 3, ...` up to the first with `N >= lc - w + h` (8 control operations and the plan set-up per size), and the cheapest is run; 80 operations of entry, the plan scale `1/N` (plan_invN, as for every transform) and 22 for the two length checks. A transform of an array of `l <= N` coefficients is `6` plus the radix-3 input stage over the `l` coefficients plus three rows of block-form passes (4.2); an inverse is `3` plus three rows of inverse passes plus the radix-3 output stage over the coefficients formed; the scaling by `s/N` of `t` outputs into their array is `8t + 5` (a load, a multiplication, a store and the loop step per coefficient). Both forms first transform the nonzero entries of `R1` into spectra of `N` points; `R1` is freed then when the call consumes it.
(i) Direct whole-pair (no window, `N >= lc`): `a` and `b` are folded modulo `X^N - 1` (10 per coefficient beyond `N`: two loads, the addition, the store, the loop step) and transformed into the operand spectra `A` and `B`; one pass over the `N` points forms `C = r22 A - r12 B` over `A` and `D = r11 B - r21 A` over `B` (per point six loads with their address operations, four multiplications, a subtraction and an addition, and the two stores at the addresses of the loads of `A` and `B`: 20; the eight-element loop of 4.2, `2 + for8(N)`); the two inverses form the first `lc` and `ld` coefficients and the scaled outputs are written. Since `deg c, deg d < lc <= N` the cyclic results are exact.
(ii) Fixed-slot (`B = N - h > 0`): the outputs from `w` (`w = 0` without a window) are cut into `nb = ceil((lc - w) / B)` blocks of `B` coefficients, handled from the highest to the lowest (`3 nb + 6` of loop control). Block `i` covers the outputs `[s, e)`, `s = w + i B`, `e = min(s + B, lc)`: it transforms the windows `[max(0, s - h), e)` of `a` and of `b` (at most `N` coefficients) into `A` and `B`, forms `C` and `D` in one pass over the `N` points (charged 24 per point: six loads and two stores with their address operations, four multiplications, a subtraction and an addition, 22; `2 + for8(N)`), inverse transforms both (all `N` outputs; the first block of an apply without a window only its outputs) and writes the scaled outputs `[s, e)` of `c` and `[s, min(e, ld))` of `d`; 20 of control per block. A window of `v <= N` coefficients times an entry of at most `h + 1` coefficients has at most `v + h` coefficients, so the cyclic wrap of length `N` reaches only the positions below `v + h - N`; the outputs of block `i` sit at the positions from `min(s, h)` of its window on, and `v + h - N <= min(s, h)` since `e - s <= B`, so they are exact. The form is used when the first block that reads a full window of `N` coefficients has index at most 8 (the blocks from it to the last but one are charged alike).
The outputs are written over `a` and `b` when the caller owns both and there is no window (the direct form reads `a` and `b` before it writes; a fixed-slot block writes `[s, e)` and the blocks after it read only positions below `s`), else into two arrays of `lc - w` and `ld - w` elements. Memory of a plan: the four matrix spectra and the two operand/output spectra, six arrays of `N` elements (lean stage-D allocations, 4.2), besides the pair and the outputs; no chunk form or accumulator.

**Lemma 4.8 (windows and pieces; 1aa56884's lemma 4.8).** (a) In a node that wants its matrix only, with `s3 > 0`, the rest of the node reads `c` only at degrees at least `s3` and `d` only at degrees at least `s3 - 1`. (b) In the top node, after the first call's `apply_inv` no operation reads `a` or `b` at degrees at least `cut`, and the low `lc` and `lc - 1` coefficients of `c` and `d` computed from `a mod X^cut` and `b mod X^cut` are the `c` and `d` of step (2); the same holds for `(d, e)`, `cut2` and `(c', d')`.
*Proof.* (a) The stopping test and the quotient test use `deg c` and `deg d`; the quotient `q = q1 x + q0` uses the top two coefficients of `c` and of `d`; and `e_i = c_i - q0 d_i - q1 d_(i-1)`. The second call reads only `d quo x^s3` and `e quo x^s3`, that is `d_i` and `e_i` for `i >= s3`, hence `c_i` for `i >= s3` and `d_i` for `i >= s3 - 1`. After it the node needs only `R1`, `q` and `R2` (and `s3 - 1 <= deg d - 1`, so the top two coefficients are inside the window). (b) The first call reads `a quo x^s` and `b quo x^s` and, after its `apply_inv`, only its own arrays; the top node then reads `a` and `b` only in step (2). For `i < lc <= cut` the coefficient `i` of `r22 a` is `sum_j r22_j a_(i-j)` with `i - j < cut`, so it equals the coefficient `i` of `r22 (a mod X^cut)`; `c` has length `lc`, so it is the low `lc` coefficients of `s (r22 (a mod X^cut) - r12 (b mod X^cut))`, and likewise `d`. For the second call, `cut2 = deg d + 1 - k3 >= lc'` with `lc' = deg d + 1 - h3` and `h3 = k3` on the normal sequence. QED

The charges of these steps are this model's (4.2, 4.5), not 1aa56884's: with 1aa56884's own conventions the same walk gives its published row D to the unit (`1,062,106,645,154,198,605,714,641` at r = 21, recomputed in our model with their conventions switched on), and with this model's primitives, with 1aa56884's conventions for the chunk assembly, the untwist and the fold of item 6 and the stage-C column kernels for its outer transforms, it gives row D of section 6.

#### 4.4.3 Aligned budgets and the inversion-free node on three rows (this entry; the half-gcd of bradcush 4bcabff8, credited, as ported in our r = 3 entry bcf8e01c)

This entry runs the half-gcd of 4.4 and 4.4.1 with two changes. Neither changes a quotient, the stopping tests or the result: every call returns the matrix of the first `h` quotients of its pair, `h` equal to its parameter on the normal sequence.

1. *Aligned split.* A node of parameter `k < 2^54` gives its first call the parameter `k1 = 2^(b-1) - 1`, `b` the bit length of `k`, in place of `ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`, as before); the second call takes the parameter left over, `k3 = k - h1 - deg q`, as in 4.4 step (5). A node of parameter at least `2^54` splits as before. The top-coefficient lemma of 4.4 steps (1) and (5) holds for every `k1 < k`: the quotients of the first call are fixed by the top `2 k1 + 1` coefficients of the pair, and the second call continues the same sequence (von zur Gathen and Gerhard, Modern Computer Algebra, chapter 11; the split point is free). The point is that a parameter `2^j - 1` splits into `2^(j-1) - 1`, one division and `2^(j-1) - 1`, so below `2^54` most calls have a parameter of that form.
2. *The inversion-free node.* A call that wants its matrix only (the first calls and the truncated second calls of 4.4.1 item 2) with parameter `k = 2^j - 1`, `6 <= j <= 31`, reads the top `2k + 2` coefficients of its pair (its caller takes `s` and `s3` of 4.4 one smaller; by lemma 4.8(a) the windowed `c` and `d` of item 3 then start one degree lower) and runs bradcush's inversion-free half-gcd (entry 4bcabff8, with the transform reuse of b30de9bf; read as text only, ported and charged in this cost model as in our r = 3 entry bcf8e01c). Remainders are kept up to nonzero constants by pseudo-division, `lc(b)^2 a = Q b + e` with `Q` of degree 1 on the normal sequence: this is the scaled step of 4.4.1 item 8 (`sigma = lc(b)^2`, `Q = A x + B`), so the matrix the node returns is a product of the matrices `[[A x + B, 1], [sigma, 0]]` of that item and its argument applies to it and to every pair formed from it (every member of a pair is a nonzero scalar multiple of the exact one, so the degrees, the quotient degrees, the tests of 6.3 and the stopping rules are those of the exact sequence). A node of parameter `2^j - 1` makes two child calls of parameter `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a transform of `n` points in the block form of 4.2 after a twist, joined by a 3-row CRT for `(c, d) = adj(M1)(a, b)` on the window; then the pseudo-division and the product `M = M1 [[Q, 1], [lc(b)^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and the scale of a step is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; each child returns the row `Y - 1` values of its matrix, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The twist of the row `Y - i` needs a root of unity of order `4n = 2^(j+1) <= 2^32`, the 2-part of `p - 1`, hence `j <= 31`. The base case (parameter 31) runs two remainder steps per pass over its window. Every pseudo-division tests that its quotient has degree 1 and every call tests on return that it removed exactly its parameter (2 operations each); on any other case the trial ends (ABORT, 6.3). The node returns its matrix in coefficient form in four arrays of `2^j + 1` words (entries of lengths `k + 1`, `k`, `k`, `k - 1`), which the caller uses as in 4.4.1.

**The two loops of the node (this entry).** *Fold.* The window of `a` (`4n'` coefficients, `n' = 2^(j-1)`) and the window of `b` (`4n' - 1`) are read once and the three rows `Y - 1`, `Y + 1`, `Y - i` are formed in one loop of eight positions per pass (4.2), position by position: `a_0 + a_2` and `a_1 + a_3` (2), their sum and difference for the rows `Y - 1` and `Y + 1` (2), and `(a_0 - a_2) + i (a_1 - a_3)` for the row `Y - i` (4, with the multiplication by `i`): eight field operations, four loads and three stores, each load and store with its address operation, 22 per position, and `2 + for8(n')` for the loop (`for8` as in 4.2), once for `a` and once for `b`; the twist of the rows `Y + 1` and `Y - i` by their running factors (2 per point and row) and the three forward transforms follow. This is charged in place of the row-by-row formation of the rows from the window, which per row copied the first chunk (4 per coefficient, and `3 n' + 2` of loop control) and folded the other three chunks into it in one accumulating loop (7 per coefficient, 8 on the row `Y - i`, and `3 (3 n') + 2` of loop control). *Two-output pass.* On each of the three rows of the apply one pass forms `C = r22 A - r12 B` and `D = r11 B - r21 A` from the row values of `a`, `b` and the four entries of `M1`; and in the product `M = P M2`, `P = M1 [[Q, 1], [b^2, 0]]`, on each of the two rows `Y - 1`, `Y + 1` one pass per column of `M2` forms the two entries of that column of `M` from the four entries of `P` and the column. Each is the two-output pass of 4.4.1 item 9 (i): six loads with their address operations, four multiplications, two additions or subtractions and two stores at the addresses of the loads of the two operands, 20 per point, and `2 + for8(n')` for the loop. This is charged in place of two pointwise passes per output. The bodies of the two loops, eight positions each, `8 * 22 + 3 = 179` and `8 * 20 + 3 = 163` instructions (3 of loop control), are counted as code in 7(a). Neither loop adds an array: the fold fills the six row arrays of the apply and a two-output pass writes over its operands, the arrays counted in the node arena. 0xplemonade's entry `8b1eb62a` (r = 7), whose note itemizes the node as fused two-output pointwise rows, was read as text and prompted charging the maps as two-output passes, priced here by the direct apply row of `ff21bd28`; no number or program is taken from it.

Charges (the rules of 4.2): for the rows that the two loops above do not form (the four entries of `M1` and of `M2` on their rows), a row of a product costs the copy of its window (4 per coefficient: a load and a store, each with its address operation), the zero fill of the rest of the row (2 per slot), the fold of a window longer than the row (7 per coefficient, 8 on the row `Y - i` with its multiplication), the twist (2 per point on the rows `Y + 1` and `Y - i`: the running factor and the multiplication), the forward transform of `n` points in the block form of 4.2 plus 10; the pointwise products are the two-output passes above; the inverse transform of a row plus 10, with `1/n` (row `Y - 1`) or the untwist times `1/n` (2 per point) fused into the CRT, which costs 22 per point (10 field operations, 3 loads, 3 stores, each load and store with its address operation); every loop carries the loop control of 4.2 (`3 n + 2`). The pseudo-division costs 30 and 13 per coefficient of the window the second child reads; the values of `Q` and of `M1 Q` cost 25 per point on each row of the product, which has the two rows `Y - 1`, `Y + 1` only (its 2-row CRT 10 per point, above); a node costs 40 for its call, 14 bump-arena operations (the allocations and releases of its working arrays) of 10 each, and its return tests 4. The scales `1/2^a` (`a <= 30`) are a table of 31 words built at the entry of stage D (one allocation; `1/2 = (p + 1)/2` an immediate, 29 multiplications, 30 stores, the loop), and the twist roots come from the twiddle table of 4.2. A matrix-only call on the node costs 40, the four allocations of its matrix and the allocation and release of its bump arena (the allocator of 4.2), and the node, `node(j) + 10`; the arena of the node holds at most `34,359,738,112` words (`j = 31`), far below the stage-C peak (section 7). Per trial on the normal sequence:

| j | parameter `2^j - 1` | `node(j) + 10` | calls per trial |
|---:|---:|---:|---:|
| 6 | 63 | 88,307 | 6 |
| 7 | 127 | 235,569 | 22 |
| 8 | 255 | 592,037 | 19 |
| 9 | 511 | 1,457,867 | 21 |
| 10 | 1,023 | 3,480,471 | 18 |
| 11 | 2,047 | 8,128,783 | 18 |
| 12 | 4,095 | 18,680,479 | 20 |
| 13 | 8,191 | 42,385,887 | 17 |
| 14 | 16,383 | 95,197,055 | 19 |
| 15 | 32,767 | 212,013,023 | 16 |
| 16 | 65,535 | 471,301,773 | 16 |
| 17 | 131,071 | 1,040,092,425 | 16 |
| 18 | 262,143 | 2,281,053,473 | 16 |
| 19 | 524,287 | 4,976,017,009 | 18 |
| 20 | 1,048,575 | 10,804,225,585 | 17 |
| 21 | 2,097,151 | 23,362,352,849 | 16 |
| 22 | 4,194,303 | 50,331,590,961 | 15 |
| 23 | 8,388,607 | 108,378,394,079 | 14 |
| 24 | 16,777,215 | 232,576,968,795 | 13 |
| 25 | 33,554,431 | 497,574,420,083 | 10 |
| 26 | 67,108,863 | 1,061,550,075,843 | 10 |
| 27 | 134,217,727 | 2,259,072,308,099 | 10 |
| 28 | 268,435,455 | 4,796,430,687,267 | 12 |
| 29 | 536,870,911 | 10,162,117,080,707 | 11 |
| 30 | 1,073,741,823 | 21,526,508,651,313 | 8 |
| 31 | 2,147,483,647 | 45,507,495,255,469 | 2,775,548 |

The nodes charge `126,308,623,185,860,447,944` operations of row D in all (2,775,926 calls; the sizes `j` with no call on the normal sequence have no row); the aligned split and the node give row D = `490,849,790,089,740,583,521`.

### 4.5 Products longer than `3 * 2^32` points (block mode)

The bullets of earlier entries on the coefficient-domain stage C are not repeated: stage C is 4.6, which uses this section only for the Newton reciprocal and the q product of its step 1. Stage D uses 4.4.1 item 6.

At this r the transforms of 4.3 and 4.4 would have up to `3 * 2^52` points (the square of stage C, `2m - 1 = 11,920,928,955,078,123` coefficients) and `3 * 2^51` points (`m + 1`, the products by `g`, and the products by the half-gcd matrices, whose entries have several blocks). The field has no root of unity of such an order (`p - 1 = 2^32 * 3 * q'`). Grok (xAI), job 140, determined the cost of multiplying polynomials of lengths `3 * 2^34`, `3 * 2^36` and `3 * 2^38` over this field and recommends the block NTT (its scheme (a)) for `3 * 2^34` and `3 * 2^36` and the same split with an outer transform across the blocks (its scheme (b), the outer FFT) for `3 * 2^38`: a product is cut into blocks, the blocks are transformed with the longest available transform, and the products of block spectra are summed in the transform domain. Grok job 140 checked both schemes against schoolbook on random products of length `2^14` with a transform cap of `2^10` (every coefficient equal, and the counted multiplications and additions equal to its formulas, `551,999` and `890,850` for scheme (a)). Both schemes are the same operations at every block count; at the lengths of this r we apply them by the charging rules of 4.2. The schemes, as used by the algorithm:

* Blocks. `B = 3 * 2^31` coefficients per block, transform size `NB = 2B = 3 * 2^32 = 12,884,901,888` (the plan of the largest transform of 4.3, with its kernels and charges). An operand of `l` coefficients has `ceil(l / B)` blocks; each block is zero-padded to `NB` points and transformed once (forward: the radix-3 stage and three rows of radix-2 passes). A product of two blocks has at most `2B - 1 < NB` coefficients, so a block product does not wrap.
* Scheme (a), slots. The slot `s` of a product `A C` is the sum of the block products `A_i C_j` with `i + j = s`; it is formed pointwise in the transform domain (`NB` multiplications per pair, additions or subtractions for the further pairs), inverse transformed once, and placed at offset `s B` of the output: a loop with a load, the multiplication by `1/NB` (and the sign), a store, and for the coefficients that overlap the previous slot a load of the output value and an addition (a subtraction when the placement subtracts into an array). Only the slots that meet the wanted window of the product are formed. The windows are those of 4.3: the Newton products use `[0, l2)`; the quotient `q` of a step is the window `[m - 2, 2m - 3)` of `T1 * MU`; the remainder uses the window `[0, m)` of `q g`.
* Scheme (b), outer transform (the scheme from which (c) below is derived; it is not used at this r). Let `ns` be the number of slots of the product, `[s0, s1]` the slots that meet the window, and `n2` the smallest `2^a` or `3 * 2^a` that is at least `max(s1 + 2, ns + 1 - s0)` (it divides `3 * 2^32`, so the roots exist). For every position `t < B` the `n2` values of the blocks of an operand at that position (zero beyond its last block) are transformed with the `n2`-point transform across the blocks (twiddles: powers of a primitive `n2`-th root of unity); this gives, for each of the `n2` outer points `o`, a polynomial of `B` coefficients, which is transformed with the block transform (`NB` points). For each outer point the spectra are multiplied pointwise (and summed over the products of the bilinear form), the result is inverse transformed, and its upper part (positions `B ..`) is multiplied by the `o`-th power of the outer root and added to the lower part (the fold). The inverse `n2`-point transform across the outer points returns, for each position `t`, the coefficients of the pieces of the product; the cyclic wrap of length `n2` does not reach the pieces of the window. The window is placed with the scaling `1/NB` and `1/n2`. Price of the outer transform (exact, from its kernels): a transform of `n2` points at each of the `B` positions of a block is a twiddle table of `n2` entries (3 operations each), `n2/3` calls of the radix-3 kernel `ob3` when `3` divides `n2`, and `n2/2` calls of the radix-2 kernel `ob2` in each of the `log2` radix-2 layers; a call of `ob3` is charged `7 + 25 B` and a call of `ob2` `5 + 14 B` (every load, store, field operation and loop step of the kernel text in `ntt_kern.h`, parsed like every other kernel), plus 10 for the call (block addresses, twiddle address, call and return). The charges are integers; nothing is averaged or truncated.
* Forms. The form of an operand of `l` coefficients is what a product multiplies pointwise. In scheme (a) it is the `ceil(l / B)` block spectra of `NB` points each (`ceil(l / B) * NB` elements). In scheme (b), when `l > B`, it is the `n2` outer-domain arrays of `B` elements each (`n2 * B` elements): the blocks are copied into one array of `n2` blocks, zero beyond the last block (the copy is charged, `7 l + 2` operations, and so is the zero fill of the other `n2 B - l` positions, `5 (n2 B - l) + 2` operations, because the form is taken from the pool, whose memory holds the data of earlier arrays), and transformed across the blocks; when `l <= B` the form is the one spectrum of `NB` points. A form is made from the coefficient array of the operand and charged as in 4.2 (each block transform, or the copy and the outer transform); the coefficient array is freed as soon as the form exists whenever the operand is not needed again. In scheme (b) the inner transform of an outer point is made when that point is multiplied, into a working array of `NB` points, and the output of an outer point overwrites a dead operand array of that point (a further outer-domain array is allocated only if the product has more outputs than operand forms of more than one block). The working arrays of a product are allocated at its start and freed at its end: in scheme (a) one accumulator of `NB` elements; in scheme (b) one array of `NB` elements for each operand and each output of the product.
* Stage D, products above one block. The entries of the half-gcd matrices and the operands `a`, `b` of `apply_inv` have several blocks at the top levels of the recursion. `apply_inv` forms `c = r22 a - r12 b` and `d = r11 b - r21 a`, a bilinear form with two outputs, each the sum of two products. The forms of the four entries are made first; when the matrix is not needed again, the coefficient array of an entry is freed as soon as it is transformed. The blocks of `a` and `b` are transformed one at a time as the slots advance and pass through a sliding window of `kR + 1` blocks for each of the two operands (`kR` is the largest number of blocks of an entry): a slot meets at most `kR` consecutive blocks of an operand, and the block after the slot is transformed before the slot is placed; a block that leaves the window is freed, and every block is transformed once, as the cost counts it. The slots are formed in order, each with the accumulator, inverse transformed and placed. The outputs `c` and `d` are written over `a` and `b` when those arrays belong to the node and have `nres` elements (the placement of slot `s` writes the blocks `s` and `s + 1` of the output, which are already transformed), otherwise into arrays of `nres` elements of their own. In scheme (b) the forms of the four entries and of `a` and `b` (outer-domain arrays; the outputs of the outer points overwrite the forms of `a` and `b`) and the working arrays are held together while the outer points are multiplied, and then freed; the outputs are written over `a` and `b` or into arrays of their own as above. The exact `c` and `d` have fewer than `nres` coefficients (the high coefficients cancel, 4.4), so slots that start at or beyond `nres` are not formed. The matrix product (`mat_mul`) of the half-gcd is the same bilinear form with four outputs, each the sum of two products. The forms of one factor are held whole and those of the other factor one row (or column) at a time, in whichever of the two orders holds fewer blocks, and each row forms its two outputs into arrays of their own length; the coefficient arrays of both factors are freed as soon as they are transformed. In scheme (b) the forms of all eight entries and the working arrays are held together while the outer points are multiplied; the four outputs are allocated when the operand arrays that are dead have been freed. The Newton division (`divrem_fast`) holds, besides the arrays of its caller, the arrays of the normal sequence (the Newton division is not run on it, 4.4.1 item 4) and the forms and working arrays of its largest block product, in the scheme in which that product is charged. All other products of stage D, and the Newton products below `3 * 2^32` points, are as in 4.3 and 4.4.
* Scheme (c), chunked outer transform (`P` chunks). The outer length `n2` is the one of scheme (b) (the smallest `2^a` or `3 * 2^a` that is at least `max(s1 + 2, ns + 1 - s0)`). If `P` divides `n2` and `Q = n2 / P` is of the form `2^a` or `3 * 2^a`, the outer points `o = j1 + P * j2` (`0 <= j1 < P`, `0 <= j2 < Q`) are handled in `P` chunks, chunk `j1` holding the `Q` points with that `j1`; otherwise the product uses one chunk (`P = 1`). The operands stay in coefficient form: nothing is copied into an outer-domain array. Let `w` be a primitive `n2`-th root of unity and `x_i` the blocks of an operand (`k` of them, `B` positions each; zero beyond `k`). Chunk `j1` is assembled from the blocks: for every `i2 < Q` the array `z_(i2) = sum over i = i2 + Q i1 < k of w^(i j1) x_i`, by one call of the kernel `ocp` (`z = c x`, charge `5 + 8 B`) for the first block of the sum and one call of `oax` (`z += c x`, `5 + 11 B`) for each further block (the last block over its own positions only), the weight `c` being the entry `(i j1) mod n2` of a table of the `n2 + 1` powers of `w` (3 operations per entry, built at the start of the product), and by one call of `ozf` (`z = 0`, `3 + 5 B`) for an `i2` that no block reaches, and for the positions of the last block's array beyond the last coefficient when that block starts its array (the chunk arrays are taken from the pool, whose memory holds the data of earlier arrays); each call is charged `30` more (the two block addresses, the exponent `i j1 mod n2` with the reduction, the table address, call and return). The `Q` arrays are then transformed with the `Q`-point transform across the arrays (root `w^P`; the twiddle table of `Q` entries at 3 operations each, `Q/3` calls of `ob3` when 3 divides `Q`, `Q/2` calls of `ob2` in each radix-2 layer; `ob3` is charged `7 + 25 B`, `ob2` `5 + 14 B`, plus 10 per call), after which array `j2` is `sum over i of w^(i (j1 + P j2)) x_i`, the outer-domain array of the point `o = j1 + P j2`. From there each point is treated as in the outer-transform scheme: the inner transform (`NB` points) of the arrays of its operands (made at every use, charged for every point of every operand of more than one block, including the persistent operands `MU` and `g` of stage C), the pointwise products, the inverse inner transform and the fold of the upper `B` positions with the `o`-th power of `w`. The `Q` folded arrays of the chunk are transformed back with the `Q`-point transform (root `w^(-P)`), and for every output piece `s` of the window (`s = s0 .. min(s1, ns - 1) + 1`, the `tc` pieces) the piece is accumulated, `acc_s += w^(-j1 s) U_(s mod Q)`, by one call of `ocp` in the first chunk and `oax` in the others (charged `1` more per call: the weight is the table entry `n2 - ((j1 s) mod n2)`). The sum over the chunks is the piece `s` multiplied by `n2`; the factor `1/n2` is applied by the placement. A product that is the quotient estimate, the remainder or a stage-C step computes its pieces into accumulators of `tc B` elements and places them into the destination afterwards; a product of a division (6.3) accumulates the pieces of the window directly into the output array of the division, so that it has no accumulator (the calls then run only over the positions of the window). Because the operands are in coefficient form for the whole product, every operand array and every chunk form is charged where it is used; no spectrum or outer-domain form is stored between products.
* Choice. At this r stage C uses `P = 4` chunks (stage D: 4.4.1, item 6): each block product uses scheme (a) or scheme (c), whichever has the smaller charge, as a function of the lengths and the window only; scheme (b) is not used. The number of chunks is a constant of the algorithm for each r, fixed before the run; it was chosen by comparing the scores of the ledger at these pairs (stage C, stage D): (4, 16). The pair used has the least score of them.
* Stage D in scheme (c). `apply_inv`: the coefficient arrays of the four entries, of `a` and of `b` stay live while the chunks are processed; the arrays of a chunk are the chunk forms of the six operands, the working arrays, the tables and two accumulators (`c` and `d`). After the last chunk the entries are freed when the matrix is not needed again; `c` and `d` are placed over `a` and `b` when those arrays belong to the node and have `nres` elements, otherwise into arrays of `nres` elements of their own; the accumulators are freed. `mat_mul`: the arrays of both factors stay live during the chunks (chunk forms of the eight entries, working arrays, tables, four accumulators); after the last chunk both factors are freed and the four outputs are placed into arrays of their own length, each accumulator being freed after its output is placed. Divisions: the arrays of 6.3, and the chunk forms, working arrays and tables of the largest block product of the division, the product accumulating its pieces directly into the output array of the division the arrays of the normal sequence (the Newton division is not run on it, 4.4.1 item 4), so that the division has no accumulator.
* Memory in scheme (c). A chunk form is `Q = n2 / P` arrays of `B` elements, so a product holds `Q B` elements for each operand of more than one block (and for each output beyond the number of such operands), where scheme (b) holds `n2 B`; the coefficient arrays of the operands and the accumulators are the other arrays of the product. The memory walk of section 7 allocates and frees every array named here.
* Scaling (coefficient-domain stage C and the products of 4.5; for stage D see 4.4.1 item 6, where the scale is applied at the untwist). The factor `NB` of the unnormalised inverse transform is removed in the placement (one multiplication per coefficient placed); the stored reciprocal `MU` and the polynomial `g` are not rescaled.
* Memory. The arena of section 7 is computed by running the allocator of 4.2 on the allocations and frees of every array named in this section, in the order of the program (a block is `64 + 32 * slots` bytes rounded up to a multiple of 64; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order). For the products in scheme (c) the arrays are those of the two bullets on scheme (c) above. Stage C, products in scheme (a): the twiddle table, `g` and `F`; in the Newton iteration also `MU`, `Y` and the forms and working arrays of the product in progress; in the loop `F` and the persistent forms of `MU` and `g` (`g` itself is freed) and, in a step, the form of `R` (then of `T1`, then of `q`), `T1` (then `q`) and the working arrays of the product in progress, in a shift by `x` the work array of the regeneration of `g`; at the end `g` is regenerated while the persistent form of `g` is still live. Stage D: the arrays of the nodes of the half-gcd, with in `apply_inv` and `mat_mul` the forms, the window and the working arrays described above, and in a division the quotient of two coefficients and the remainder only (6.3: on the normal sequence every quotient has degree 1, so the Newton division never runs). The truncated second call of a node reads the top coefficients of `d` and `e` in place (no array); the second `apply_inv` at the calls of the Euclid driver and the two copies of the returned remainders are counted with the node. In scheme (b) a form is `n2` outer-domain arrays of `B` elements, so the scheme holds `n2 * B` elements for each operand of more than one block. The twiddle table is the one of the transform of `3 * 2^32` points (`2^31` elements, `ntt_init(32)`).
* Cost. The charges are those of 4.2 applied to these operations: each block transform and each inverse transform with the kernels and pass structure of the transform of `3 * 2^32` points, each pointwise product `NB` times the per-point charge of the bilinear form of 4.4, each placement as stated above.

The three kernels of scheme (c), from `ntt_kern.h` (`LD(n)` and `ST(n)` are charged `2 n` operations, `CTL(n)` `n`, `fp_mul` and `fp_add` one each; the source counts `5 + 7 cnt`, `5 + 10 cnt` and `3 + 4 cnt`; this entry charges the loop step of each position 3, by the loop rule of 4.2, so the charges are `5 + 8 cnt`, `5 + 11 cnt` and `3 + 5 cnt`, as in the text above, and likewise `ob3` and `ob2` one more per position than their source):

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

In this entry stage C is not the coefficient-domain squaring of 4.3 and 4.5: it is the value-domain powering of bradcush's entry 1aa56884 (proof section 4.6 there, credited in the submission note), re-implemented and charged in this entry's cost model. The residue is held by its values on two sets of `n1` points. One modular squaring is a Montgomery reduction whose only non-pointwise work is two changes of point set (extensions). No product of polynomials, no `MU` and no quotient is formed in the loop. Sections 4.3 and 4.5 still define the transforms, the kernels and the Newton reciprocal that the set-up below uses.

**Points.** Here `h = 2^32` and `K` is the number of cosets of each point set (not the number of centres of 4.1). `H` is the subgroup of order `h` of `F_p^*`, with generator `omega = 5^((p-1)/h)`, which has order `h` because 5 is a non-square. Put `u_k = 5^k`, `C_k = u_k H` and `n_k = u_k^h = z^k` with `z = 5^h`. `p - 1 = 2^32 * 3 * 463 * q1 * q2` with `q1 = 539,204,044,132,271,846,773` prime, and `z^((p-1)/q1) != 1`, so the order of `z` is at least `q1 > 2K`. Hence the nodes `z^k` (`k < 2K`) are distinct and the cosets `C_k` are pairwise disjoint (`C_j = C_k` if and only if `z^(k-j) = 1`). Our script `zorder_check.py` (standard library) checks these three facts: `q1` is prime by a deterministic Miller-Rabin test with the bases up to 41 (valid for `n < 3.3 * 10^24`), `z^((p-1)/q1) != 1`, and `5^((p-1)/2) != 1`; all three hold. At r = 17: `m = 5,960,464,477,539,062`, `K = ceil((m + 1)/h) = 1,387,779`, `n1 = K h = 5,960,465,419,075,584 = m + 941,536,522`. Put `O1 = C_0 u ... u C_(K-1)` and `O2 = C_K u ... u C_(2K-1)`, `M(Y) = prod_(k<K) (Y - z^k)` and `P1(X) = M(X^h)`. `P1` has degree `n1`, is squarefree, has root set exactly `O1`, and on a coset `C_k` with `k >= K` it is the nonzero constant `M(n_k)`.

**Representation.** A polynomial `f` of degree `< n1` is determined by its values on `O1`, and also by its values on `O2`. Write `f = sum_(j<h) X^j F_j(X^h)` with `deg F_j < K`. Then `f mod (X^h - n_k) = sum_j F_j(n_k) X^j`, so the values of `f` on `C_k` are the transform of size `h` of `(u_k^j F_j(n_k))_j`. Each array holds the values coset by coset, in the output order of the inner transform. The inner transforms of the cosets of an array are made together, as column passes across the cosets (position = coset, stride `h`): column passes of at most seven layers for the 32 layers, split by least charge (4.2), in place on the array.

**Lemma 4.6 (the step).** Let `g` be monic of degree `m` with `g(x) != 0` on `O1`. Let `R~` have degree `<= m`, and let `u0` be the polynomial of degree `< n1` with `u0(x) = -R~(x)^2 / g(x)` on `O1`. Then `W = (R~^2 + u0 g) / P1` is a polynomial of degree `<= m - 1`, and `W = R~^2 P1^(-1) mod g`. On `C_k` with `k >= K`, its values are `(R~(x)^2 + u0(x) g(x)) / M(n_k)`. *Proof.* `R~^2 + u0 g` vanishes on the `n1` distinct roots of the squarefree `P1`, so `P1` divides it. Its degree is at most `max(2m, n1 - 1 + m) = n1 + m - 1` because `n1 >= m + 1`, so `deg W <= m - 1`. Modulo `g`, `W P1 = R~^2`, and `P1` is invertible modulo `g` because `g` has no root in `O1`. The values follow from `P1(x) = M(n_k)` on `C_k`. QED. So the invariant `R~_i = S^(e_i) P1 mod g` passes from step to step with `R~' = X^b W` (`e_(i+1) = 2 e_i + b`, `deg R~' <= m`). The same argument with `R~` in place of `R~^2` leaves the Montgomery form (step 7).

**Lemma 4.7 (extension).** Let `f` have degree `< n1`, with its values on `O1` given. The inverse inner transform of each coset gives `h u_k^j F_j(n_k)`. Fix a position `j`, write `F = F_j`, and put `s_i = F(z^i) z^(-i) / M'(z^i)` and `kappa(e) = 1/(z^e - 1)` for `1 <= e <= 2K - 1`. Then `F(z^(K+t)) = M(z^(K+t)) sum_(i<K) s_i kappa(K + t - i)` for `t < K`. *Proof.* `deg F < K`, so `F` is the Lagrange interpolant of its values at the `K` distinct nodes, and `z^(K+t) - z^i = z^i (z^(K+t-i) - 1)` with `1 <= K + t - i <= 2K - 1`. QED. The direction `O2 -> O1` is the same with the nodes `z^(K+i)`. The sum is a cyclic convolution of length `Lx = 3 * 2^20 >= 2K` with a fixed kernel, and no index wraps.

**The stage** (the eight steps of 1aa56884, with our parameters at r = 17). The exponent `E = (p-1)/2` starts from `S^v` with `v = 2^50`, a multiple of `h` below `m` (`VSHIFT = 2`: two more squaring steps and a shorter reciprocal), and runs `203` steps, `45` of them with `b = 1`.
1. *Barrett start:* the reciprocal of the reversed `g` modulo `X^ell`, `ell = 1,125,900,848,379,147`, by the Newton iteration of 4.3 with the products of 4.5. Then `q = floor(X^v P1 / g)` by one product (`Kq = 262,145` rows).
2. *`g` on `O1` and on `O2`* by the chirp evaluation of section 3 (one convolution of length `Le = 2^22 >= 3K - 1` per position) and `2K` forward inner transforms.
3. *`R~_0` on `O2`:* `q` evaluated at the nodes of `O2` (`Lq = 2^21`), then `R2 := u_k^v M(n_k) - R2 * G2` pointwise. This gives the values of `X^v P1 - q g = X^v P1 mod g`.
4. *`R~_0` on `O1`:* an extension `O2 -> O1` (lemma 4.7).
5. *`-1/g` on `O1`* by Montgomery's batch inversion per coset in chunks of `2^16` elements (the `2^16`-element batch-inversion prefix of 0xplemonade's entry `ff21bd28`): per chunk the prefix products into one auxiliary array of `2^16` elements (a load, a multiplication, a store), one inversion with its zero test and the backward pass (two loads, two multiplications, the negation, a store), 9 of chunk control; 20 per coset. A zero prefix product means `g` vanishes on `O1`, and the trial ABORTs as in 4.4.1 item 4 (allocator reset, ledger row 'ABORT reset') after a prefix of the charged work; the probability is below `2^-148.2` (9.2(g)).
6. *The loop*, for each bit `b`: `R1 := R1^2 G1` (`u0` on `O1`); the extension `O1 -> O2`; `R2 := x^b (R2^2 + R1 G2) / M(n_k)`; the extension `O2 -> O1`. By lemma 4.6 the invariant holds after every step.
7. *Leaving the Montgomery form:* `R1 := R1 G1`, the extension `O1 -> O2`, `R2 := (R2 + R1 G2) / M(n_k)`. `R2` now holds `R = S^E mod g` (degree `< m`).
8. *Coefficient form for stage D:* `R2` and `g` are interpolated in place (inverse inner transforms, then two chirp correlations of length `Lx` per position), each into two pieces, the coefficients `[0, cut)` and `[cut, l)` with `cut = 4,470,352,285,532,160`, which the top node of stage D frees early (4.4.1, step 5).

**Kernels.** In the loop, the last two forward layers of the inner transforms, the pointwise step and the first two inverse layers are one column pass per boundary: on `O1` (`9 + 44 cnt + F(cnt)`) per position 4 loads, 4 butterflies, for each of the 4 elements a load of `G1`, a squaring and a multiplication, 4 inverse butterflies and 4 stores; on `O2` (`11 + 61 cnt + F(cnt)`, `27 + 70 cnt + F(cnt)` for `b = 1`) the same with the load of `1/M(n_k)` and per element the loads of `R2` and `G2`, a squaring, two multiplications and an addition (`b = 1`: the factor `u_k` and two more multiplications per element, and per call the four `omega^e` of its rows, each the product of one entry of each of two tables of `2^16` entries, `omega^e = T1[y] T2[x]` for the position `p = x 2^16 + y` with exponent `e = 2^16 rev16(y) + rev16(x)` in the bit-reversed output order of the inner transform, `T1[y] = omega^(2^16 rev16(y))`, `T2[x] = omega^(rev16(x))`: two loads with their addresses and one multiplication per value, 12 more per call than one load per value from a table of `h` entries, the 12 being in the constant `27`; the two tables are built at `10` per entry), within the 18 words. The extension is computed in a coset-major group buffer (`L` rows of `VCNT` positions) with column passes (`ob128`, `ob64`, `ob32`, `ob16`, `ob8`, `ob4`, `ob2` as the layer count needs; `ob3` for the radix-3 stage): the first forward pass reads the `K` input rows from the coset array with their factors and skips the zero rows; the last two forward layers, the product by the kernel spectrum and the first two inverse layers are one pass (`ob4m`, `13 + 36 cnt + F(cnt)`: 4 data words, 3 + 3 twiddles and 4 spectrum words); the last inverse pass forms and writes only the rows `K .. 2K - 1`, with their factors, into the coset array (the register-blocked scheme of 1aa56884, credited). Every column pass of this section, the pruned first and last passes included, runs its position loop eight positions per pass with the control `F(cnt)` per call (4.2), not 3 per position.

**Charges** (the components sum to row C of section 6):

| component | operations |
|---|---:|
| inner transforms of the `K` cosets of one array (column passes of 4.2 at `cnt = K`; forward / inverse) | 352,401,018,269,855,382 / 352,401,018,269,855,382 |
| geometric phase of one extension (188.757 per element of `n1`) | 1,125,078,968,503,399,984 |
| one extension with its `2K` inner transforms | 1,829,881,005,043,110,748 |
| one loop step, `b = 0` / `b = 1` | 3,695,897,254,648,391,368 / 3,709,308,319,021,180,616 |
| tables: `30 K` constants, the two `omega` tables of `2^16` entries, the kernel spectra | 256,894,022,729 |
| Newton reciprocal (step 1, with its allocations) | 8,062,348,407,867,173,551 |
| product for `q` (step 1) | 2,047,224,824,018,654,259 |
| evaluation of `g` (step 2, geometric part) | 1,707,350,870,505,059,886 |
| `2K` forward inner transforms of `g` (step 2) | 704,801,905,738,193,817 |
| step 3 | 1,222,362,261,688,312,313 |
| step 4 (one extension) | 1,829,881,005,043,110,748 |
| step 5 (batch inversion in chunks of `2^16`) | 88,158,881,544,430,925 |
| step 6, the loop: 203 steps (45 with `b = 1`) | 750,870,640,590,398,963,864 |
| step 7 | 1,946,110,080,781,698,032 |
| step 8 (two interpolations) | 5,892,441,884,471,874,398 |
| allocations, exponent scan, zero fills, end of stage | 10,213,172,092 |
| stage C of one trial, with the stage bookkeeping of 1,000 (ledger row C) | 774,371,320,979,164,667,614 |

The inner transforms are column passes and the geometric phase uses the register-blocked kernels above (the outer-kernel convention of 1aa56884). With the pieces of 4.4.1 every coset access of a row pass (the pointwise passes, the batch inversion, the rows read or written by an extension) also selects the base of its piece (a comparison and a branch, 2 operations), and every column pass splits its coset loop at the piece boundary (4 operations per call); both are included in the figures above. Every charge depends only on `m` and the exponent, not on the coefficients.

**Memory.** The loop holds `R1`, `R2`, `G1` and the array of `g` (which holds `g` on `O2` during the loop and `g` in coefficient form at the exit): four arrays of `n1` elements. It also holds the tables and the group buffer of `VCNT = 2^10` rows of `Lmax = Le = 2^22` elements (the longest kernel), and one transform row of `Lmax` elements; the tables are the `30 K` constants, the two `omega` tables of `2^16` entries and the kernel spectra, and step 5 adds one array of `2^16` elements. The live peak of stage C is `3.0000` arrays of `n1` above its entry , plus the array of `g` from stage A. Section 7 walks these allocations with the rest of the trial.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: worst-case operation count (primitive operations; `C(17) = 573`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, the trial loop and the allocator reset after an ABORT (charged in every trial); `T_off` = the offline derivation of section 6.2, at most 554,785 (136,785 counted exactly and the bound of 6.2 for the literals of Appendices L and B) and charged at its declared cap 1,000,000. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 1` (one centre, section 9.2), and `time_log2 = ceil_5(log2(N_max / 573))`.

Every stage is charged by the rules of section 4.2 where it executes. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(32-1)` elements (`ntt_init(32)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 17,179,887,292 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,382 |
| B (per trial) | `925186` cosets of `6,442,450,944` points, each point with two executions of `L` (at `c' + s` and `c' - s`; section 3, Appendix L) at `339` operations each, the point loop on root tables `107,545,495,681,159,510` (Appendix B), `925186` inverse transforms of size `6,442,450,944`, the geometric solve of the cosets (two correlations of length `2,097,152` per position), the normalisation (these `9,014,178,735,922,205,330` unchanged) | 13,162,919,785,736,610,792 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain (section 4.6): the Barrett start (Newton reciprocal and the product for `q`), the evaluations of `g` and `q`, the batch inversion, `203` steps (45 with `b = 1`), each two pointwise passes and two extensions, the exit and the two interpolations | 774,371,320,979,164,667,614 |
| D (per trial) | half-gcd of `(g, R - 1)` (sections 4.4, 4.4.1, 4.4.3), charged for the normal remainder sequence with the quotient and return tests; any other sequence ends the trial after a prefix of this work (section 6.3) | 490,849,790,089,740,583,521 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, register-resident, each at most `R(16) = 200,101` (Appendix S), the stage bookkeeping 1,000, the load of `G` and the exit 200 | 12,807,664 |
| F (per trial) | square root, back-map (below) | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 573 + 32` | 12,492 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| ABORT reset (per trial) | the reset of the allocator when a test of stage D (quotient, return or window) or the zero test of stage C (4.6 step 5) fails and the trial ends (section 6.3): the 47 free-list heads (classes 7 to 53), the end of the slab area, the two ends of the pool and the header of its free middle block; at most 1,000, charged in every trial | 1,000 |
| plan_invN misses | one per distinct plan size (52 sizes) | 160,628 |
| plan_invN misses, model residual | the 5 further distinct plan sizes of the model (57 in all, 3,089 each): the part of the model's total not itemized in the rows above | 15,445 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2: `T_off <= 554,785`, charged at the declared cap | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **1,278,384,030,871,839,189,844** |

Row C is the sum of the charges of section 4.6; row D is the charge of the half-gcd of sections 4.4, 4.4.1 and 4.4.3 with the products of 4.5, on the normal remainder sequence (6.3).

`N_max = 1,278,384,030,871,839,189,844` operations `= 2,231,036,703,092,214,991.00` units, `log2(N_max / 573) = 60.95241995572471`, claimed as `60.95242` (rounded up at five decimals).

Stage B charges each of the `11,920,930,838,151,168` evaluations as one execution of the line program `L`, `135 + 12 * 17 = 339` operations (Appendix L, checked against the reference rounds in L.2); the point loop of Appendix B, `107,545,495,681,159,510` (was `1,502,037,285,607,047,170` for the loop of the base entry, `252` per point and 2), is charged on top; the inverse transforms, the solve and the normalisation (`9,014,178,735,922,205,330`) are unchanged (section 3).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping), loads `G` into field registers and ends with the root `-H_0` (200 with the exit), and runs at most `Z = 64` rounds of the register-resident procedure of Appendix S, each charged at degree `DMAX = 16`: `R(16) = 200,101`, `E_cap = 1,000 + 200 + 64 * 200,101 = 12,807,664` (was `166,079,773` for the Taylor-shift rounds of 4.1.2 with every field operation charged 10 and the allocations of their arrays).

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`.

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.2 Offline derivation of the literals (preprocessing)

The literals of the sources are computed once, offline, from `p` and the organizer's 192 round constants and 9 MDS entries, one literal at a time (working set: at most 16 words of 32 bytes and a 64-byte digit buffer); each is the value of one closed formula, with no search and no choice. Count in the primitives of 4.2 (orchard-field-ram-v2: every field operation, load, store and control operation is 1): a field operation is charged 4 (the operation, two operand loads, one store), a 64-bit word operation 3 (the operation, one load, one store), a hexadecimal digit 5 (its load, the table load, a shift, an or, the loop control). (a) Input: 202 values of 64 hexadecimal digits (`p`, the 192 round constants, the 9 MDS entries), 324 each with the 4 word stores: `65,448`. (b) Field literals, 489 field operations: `2 = 1 + 1` (1); `R = 2^256 mod p`, `2` squared 8 times (8); `R^2 mod p` (1); the Montgomery forms `x R mod p` of the 201 organizer constants (201); `2^65 R mod p` (`2` squared 6 times, times `2`, times `R`: 8); `5 = 2 + 2 + 1` (2); `5^t R mod p` with `t = (p-1)/2^32`, the odd part of `p - 1` (the exponent written `q` in the Tonelli-Shanks of stage F; 223 bits, 46 of them 1: 222 squarings, 45 multiplications, times `R`: 268); charged `4 * 489 + 3 * 222` (the bit steps of the square-and-multiply) `= 2,622`. (c) Word literals, 90 word operations: `p - 1` (4), `t` (a shift by 32 over 4 words, 12), `(t+1)/2` (16), `(p-1)/2` (12), `p - 2` (4), `e = (4(p-1)+1)/5` (a shift by 2 into 5 words 15, plus 1, a division by 5 word by word 10: 26), `-p^-1 mod 2^64` (5 Newton steps `x <- x (2 - p_0 x)` from `x = p_0`, 3 each, and a negation: 16); charged `3 * 90 = 270`. (d) Output: 211 literals of 64 hexadecimal digits (the 201 Montgomery forms, `R`, `R^2`, `2^65 R`, `5^t R`, `t`, `(t+1)/2`, `(p-1)/2`, `p - 2`, `e`, `p`), 324 each, and `-p^-1 mod 2^64` (16 digits, 81): `68,445`. `T_off = 65,448 + 2,622 + 270 + 68,445 = 136,785` operations over the 212 literals. (e) The literals of Appendices L and B: the 135 literals of `L` (its 134 constants and `E0_0`) take at most two inversions (330 field operations each) and 40 products each, `135 * 700` field operations at 4: at most `378,000`; the 1,798 entries of the root tables of Appendix B (the generators by powers of `zeta`, the 1,792 table entries by successive products, eight inversions for the inverse tables and the row constants) at most `10,000` field operations at 4: `40,000`; one literal at a time with at most 64 further words (7(e)). With them the offline work is at most `136,785 + 378,000 + 40,000 = 554,785`. The ledger charges the declared cap `1,000,000 >= T_off` (`preprocessing_log2 = 20`, `2^20 = 1,048,576`), inside `N_max`: a counted bound, not a premise. The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry e6dcb600)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c, R_c - 1)`: every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centering division of a node, the division of each repetition of the outer loop, each step of the base case) tests that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); (c) the window test of 4.4.1 item 3 (2 tests, 2 operations each); a zero remainder inside hgcd or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state after the twiddle table (1,000 operations, charged in every trial) and the next centre is drawn. Lemma (prefix; e6dcb600, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each call splits at k1 = ceil(k/2) (at k1 = 2^(b-1) - 1, b the bit length of k, when k < 2^54, 4.4.3) and, with every quotient of degree 1, every degree in the tree is fixed by m and the number of quotients so far and the parameters of the second call and of the outer loop are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's hgcd calls and divisions produce has degree at least 94 (n >= 193), so a gcd of degree at most 94, and so every gcd of degree at most DMAX, first appears in the classical Euclid below degree 192, after a prefix of the degree-0 work. A zero remainder anywhere earlier (gcd degree above 94, a failed trial anyway) ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2(g)). Row D of section 6 is this charge, `490,849,790,089,740,583,521`.

## 7. Memory

Five terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 399,216 bytes of code, 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages), and at most 907,520 bytes for the straight-line block bodies of 4.2 (for `k = 1, ..., 7`, forward and inverse: the four-block and one-block bodies and their group-0 variants, at most `10 (2^(k+1) + 3k 2^(k-1) + 3)` instructions of at most 16 bytes each): 6,157,964 bytes; and 32,768 bytes (at most 2,048 instructions of 16 bytes) for the routines of this entry, the apply plans of 4.4.1 item 9, the chunked batch inversion and the two `omega` tables of 4.6 and the pass splits of 4.2: 6,190,732 bytes; and 32,768 bytes (at most 2,048 instructions of 16 bytes) for the routines of the node of 4.4.3, the loop bodies at eight positions per pass of `8 c + 3` instructions for a charge of `c` per position (4.2): the row copy (4) 35, the zero fill (2) 19, the fold-accumulate (7, 8) 59 and 67, the twist (2) 19, the pseudo-division (13) 107, the values of `Q` and of `M1 Q` (25) 203, the 3-row CRT (22) 179, the 2-row CRT (10) 83, the base-case remainder loop (13 and 9 in one body, 22) 179 and its matrix-column loop (22) 179, and the table of the scales 100, 1,229 instructions in all, with its call, arena and test code inside the 2,048: 6,223,500 bytes; and 5,472 bytes for the two row bodies of the node of 4.4.3 (the fold row, `8 * 22 + 3 = 179` instructions, and the two-output row, `8 * 20 + 3 = 163`), 342 instructions of at most 16 bytes: 6,228,972 bytes; and `127,392` bytes for this entry's program `L` with its call sites, the nest of Appendix B and the routine of Appendix S (at most 4,096 instructions of 16 bytes, `65,536`) and their literals (the 135 of `L` and the 1,798 entries of the root tables, `1,933` words of 32 bytes, `61,856`): `6,356,364` bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (the second trial repeats the first from the same state: a trial frees every array but the twiddle table, and the simulation checks that the pool is back to that state). The simulation records every allocation and free of the trial in the order of the program (the twiddle table, stage A, stage B, stage C, stage D; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order), checks that these events reproduce the live-set walk of every stage (bytes in use, peak, live blocks), and runs the allocator on them. By the prefix lemma of section 6.3 every size in the sequence is a function of `m` and of the shape of the recursion on the normal sequence (and the block counts of the products), so the sequence is the same for every input. The two-ended pool takes the blocks of more than 2^43 bytes and is simulated address by address (two lists in address order, the low one from the bottom and the high one, for the statements marked `# pool:H`, from the top; the first free block that fits on the request's side is cut from the side nearest its end; a free merges with its free neighbours and with the unused middle); its capacity is the largest sum of the extents of the two ends over the trial, `762,939,573,641,675,136` bytes (after stage C `762,939,573,641,675,136`, after stage D `762,939,573,641,675,136`), plus 128 bytes so that the unused middle is always at least 128 bytes. The live-set peak of the same sequence is `762,939,781,910,416,896` bytes and the arena is `1.00039` times it: the blocks that die first are taken from the top and the long-lived ones from the bottom, so the holes left by freed blocks are small. The slab classes take the blocks of at most 2^43 bytes (a block of at most `2^j` bytes gets a slot of `2^j` bytes; the free list of the class first, else a new slot from the end of the slab area), so the slab area is the sum over the classes of the peak number of live blocks of the class times `2^j`: `294,256,799,359,104` bytes. Stages E to I hold at most 16 live arrays of at most 17 elements (16 slots of 1,024 bytes), and the allocator keeps 47 free-list heads (classes 7 to 53) and the end of the slab area (48 words, 384 bytes): `16,896` bytes with a margin of 128. The arena is `763,233,830,441,051,264` bytes (the three terms, rounded up to 64 bytes), in the stage with the highest pool address, C. The peaks of the live set per stage (twiddle table, `g`, `F` and the live set of the stage; the arena above is larger): A 190,734,962,129,895,616; B 381,469,855,540,314,368; C 762,939,781,910,416,896; D 741,758,100,658,197,120; stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The walk of stage D is the walk of the normal remainder sequence (6.3) with the pieces and windows of 4.4.1, its apply plans (item 9: six arrays of `N` elements and the outputs per plan) and 4.4.3: every array of stage D has the length the normal sequence gives it, and a trial with any other sequence ends (ABORT) after a prefix of these allocations, so the walk bounds every trial. The largest transform has `3 * 2^32` points and uses roots of unity of order 3 and `2^32` (`p - 1` is divisible by 3 and by `2^32`); products that would need a longer transform are computed by blocks (section 4.5). The largest buffers are those of stage C (section 4.6: `R1`, `R2`, `G1` and the array of `g`, `n1 = 5,960,465,419,075,584` elements each, the tables and the group buffer; the Newton phase of its set-up holds three arrays of `ell` elements and the forms of one product) and those of stage D (4.4, 4.4.1); the arrays of 4.4.3 (the table of 31 scales, the four matrix arrays of `2^j + 1` words and the node arena of at most `34,359,738,112` words of each matrix-only call) are blocks of at most `2^41` bytes, below the pool threshold `2^43`, and are inside the slab area above.

(c) A stack bound of 65,536 bytes.

(d) The register file of the machine of claim.json: one file of 387 words (256 field registers and 131 integer address registers), each counted as a 256-bit word, 12,384 bytes.

(e) The working set of the offline derivation of section 6.2: 16 words of 32 bytes and the 64-byte digit buffer, 576 bytes, and at most 64 further words for the literals of Appendices L and B, 2,048 bytes: 2,624 bytes.

Total: (a) + (b) + (c) + (d) + (e) = `763,233,830,447,488,172` bytes `= 2^59.4049027`, claimed as `memory_log2_bytes = 59.40491` (the exponent rounded up at five decimals; 59.40491 is above 59.4049027). The rows of section 6 and this arena are generated by our counting program: it adds the charges of 4.2 over every call of the algorithm of section 4 in program order and runs the allocator of 4.2 on the same allocation sequence; each term is the closed formula stated in sections 4 and 6, and the program is not attached. The memory penalty is `max(0, 59.40491 - 20) = 39.40491`. The offline derivation of section 6.2 is a closed formula per constant; its working set is term (e). The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init".

## 9. Success probability and the premises `H-ONE` and `H-NORMAL`

### 9.1 The premise `H-ONE`

Notation. `p` is the Pallas prime, `D = 5^23`, and `F` is the fixed polynomial of section 2.3 at r = 17 (degree `D`, leading coefficient `f_D(0) != 0`). `g_c` is the monic odd part about the centre `c` (section 3, degree `m = 5,960,464,477,539,062`), and `G(c, t) = (F(c + t) - F(c - t)) / (2 t) = g_c(t^2)`. For `c` in `F_p`, let `k(c)` be the number of nonzero squares `S` with `g_c(S) = 0`; this is `deg G_c` of section 3, the degree of `gcd(g_c, S^((p-1)/2) - 1)`. `E_c` is the event `1 <= k(c) <= DMAX` (`DMAX = 16`) under which stage E runs.

**Premise `H-ONE`.** The number of centres `c` in `F_p` with `1 <= k(c) <= 16` is at least `0.3931 p`. Equivalently, for `c` uniform on `F_p`, `P(E_c) >= q = 0.3931`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r17-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2) and the polynomial `F` of section 2.3, with centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:**
- The premise concerns this `F`, not every polynomial of degree `D`. It is false for permutation polynomials: every pure composition of maps `x -> a x^5 + b` is bijective and has `k = 0` at every centre. It is also false for a decomposable `F` with imprimitive monodromy (the axis line of 10.3, Theorem C).
- It is false at one layer (`F_1`, `m = 2`: the law of 9.3(a) gives exactly 0.375) and true at two and three layers (9.3(c)).
- The value `0.3931` is `0.3934693 - 0.3931 = 0.0003693` below the value `1 - e^(-1/2) = 0.3934693` of the law of 9.3(a), stated exactly as the extrapolation allowance; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292` (9.3(b)). With `delta = 0.003` (9.5), the bound of 9.2 needs `P(E_c) >= 0.393000000000002345`.

What the premise does not contain: no random-polynomial model; no independence of centres (one centre is drawn); no statement about the remainder sequences (that is `H-NORMAL`, 9.5); and nothing about the cost.

### 9.2 The success bound with one centre

(a) *Centre.* The centre is one draw (4.1.1); the words of the run are within statistical distance `eps_coin < 2^-122` of uniform (4.1.1). So `P(E_c) >= q - eps_coin` for the drawn centre.

(b) *The ABORT of stage D and the zero test of stage C.* Let `N_c` be the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd: `deg(R_c - 1) = m - 1` and every quotient of degree 1 (section 6.3). By the premise `H-NORMAL` (9.5), `P(not N_c) <= delta = 0.003` for `c` uniform.

Let `Z_c` be the event that `g_c` vanishes at a point of the set `O1` of the value-domain stage C; its zero test (section 4.6) ends the trial. For each of the `n1` points `x` of `O1`, `g_c(x)` (before normalisation) is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so it has at most `D - 1` roots. Each residue is drawn with probability at most `4/2^256` (4.1.1). Hence `P(Z_c) <= delta_C = n1 (D - 1) 4 / 2^256 = 2.455e-45 (2^-148.2)`, proved, no premise.

If `E_c` and `N_c` hold and `Z_c` does not, stages C and D run to their end and return `G = gcd(g_c, R_c - 1)`.

(c) *Isolation.* If `E_c` holds, stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48`, over words that are fresh for that stage (lemma 9.4): each round, whatever came before, halves the degree with probability at least `w = 1/2 - 7.869e-40` (the `(p-3)/2` shifts that separate two roots, 4.1.1 weights), four halvings take `deg G <= 16` to 1, so the failure probability is at most `P[Bin(64, w) <= 3] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15`. Proved, no premise.

(d) *The bound.* A trial with `E_c`, `N_c`, not `Z_c`, and a successful isolation ends in a verified collision (sections 2-5). For `c` uniform, `P(E_c and N_c and not Z_c) >= q - delta - delta_C`. So, with `K = 1`,

`P[success] >= 1 - (1 - q + delta + delta_C)^K - K (eps_coin + eps_iso) = q - delta - delta_C - eps_coin - eps_iso = 0.390099999999997615 >= 0.39009`

with `q = 0.3931`, `delta = 0.003` and `K = 1`. This is the form of bradcush's entry 1aa56884 (9.2(f) there) at `K = 1`. The bound stays at least 0.39 for every `delta <= 0.0030999` at `q = 0.3931`, and for every pair with `q - delta >= 0.390000000000002345`. The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 17 enters it.

(e) *Why one centre needs `H-ONE`.* Two moments of `k` cannot give 0.39 with one centre. The law of 9.3(a) has the exact values `E[k] = 1/2` and `E[k(k-1)] = 1/4`, and the sharp lower bound on `P(k >= 1)` over all laws with these moments is `3/8 = 0.375`: the law `P(0) = 5/8`, `P(1) = 1/4`, `P(2) = 1/8` attains it. With three moments the bound is still 0.375. This is why entries built on two moments (our earlier premise `H-GEOM-w1`, and gta6rp's linear two-moment bound) use two centres. One centre needs a statement about the event itself, or four moments (9.3(b)).

### 9.3 Where the number comes from (support of `H-ONE`; not used in the bound)

(a) *The law.* The roots of `G(c, t)` in `t` are `+-t_1, ..., +-t_m`, where `u_i = t_i^2` are the roots of `g_c`. So the Galois group `Gamma` of the cover `G(c, t) = 0` of the `c`-line acts by signed permutations: `Gamma` is a subgroup of the hyperoctahedral group `B_m` (10.3, Grok job 137). For a centre off the branch locus, `k(c)` is the number of positive fixed points of the Frobenius element: the indices `i` with `t_i` in `F_p`.

For a uniform element of `B_m`, the binomial moments of this number are `E[C(k, j)] = 2^-j / j!` for `j <= m`, so `P(k >= 1) = 1 - sum_(j <= m) (-1/2)^j / j!`. This is 0.375 at `m = 2`, 0.3958 at `m = 3`, 0.3932 at `m = 4`, and 0.3934693403 for every `m >= 12`: the Poisson(1/2) value `1 - e^(-1/2)`. The tail is negligible: `P(k > 16) < 2.3e-20`. With Chebotarev's theorem (Frobenius elements equidistributed in `Gamma`), this law is the frequency over the centres.

(b) *Moments and counts.* `E[C(k, j)] = N_j / (2^j j! p)`, where `N_j` is the number of points `(c, t_1, ..., t_j)` over `F_p` with `G(c, t_i) = 0`, `t_i != 0` and `t_a^2 != t_b^2` (for `j = 1, 2` these are the counts `N*` and `N_off` of our earlier premise `H-GEOM-w1`).

For every integer `k >= 1`, `sum_(j=1..4) (-1)^(j+1) C(k, j) = 1 - C(k-1, 4)`. This is 1 for `k <= 5` and at most 0 for `k >= 6`, and the sum is 0 at `k = 0`. So `1_(1 <= k <= DMAX) >= k - C(k, 2) + C(k, 3) - C(k, 4)` for every integer `k >= 0`, and `P(E_c) >= S_1 - S_2 + S_3 - S_4` (Bonferroni at order 4). With the moments of (a) this is `151/384 = 0.3932292`.

Hence `H-ONE` follows from four count statements, `N_1 >= (1 - eps) p`, `N_2 <= (1 + eps) p`, `N_3 >= (1 - eps) p` and `N_4 <= (1 + eps) p`, with `eps <= 0.0032835`. The premise is stated as the weaker statement `H-ONE` itself.

(c) *A theorem at two and three layers.* Let `F_N` be the truncation of 10.3: the first `N` S-box layers, degree `5^N`. On the deployed constants and the construction's line, 10.3 gives the arithmetic monodromy `Gamma = B_12` at `N = 2` and `Gamma = B_62` at `N = 3` (`pi(Gamma) = S_m`, `K = F_2^m`).

The geometric monodromy is normal in `Gamma` with a cyclic quotient. It therefore contains the commutator subgroup `{(eps, pi) : pi in A_m, prod eps = 1}` of `B_m`. That subgroup acts transitively on ordered `j`-tuples of signed distinct indices for `j <= m - 2`: `A_m` is `(m-2)`-transitive, and a free sign fixes the parity.

So for `j <= 8` the curve counted by `N_j` is absolutely irreducible, a complete intersection of degree at most `(5^N - 1)^j`. The Aubry-Perret bound gives `N_j = p (1 + rho_j)` with `|rho_j| <= (5^N - 1)^(2j) p^(-1/2)`: below `2^-53` at `N = 2` and below `2^-15` at `N = 3` (`j <= 8`).

The Bonferroni bounds of orders 7 and 8 then give `0.39346933 <= P(E_c) <= 0.39346944` for `F_2` and for `F_3`. At these depths `H-ONE` is a theorem, with margin 0.00037.

 At `N = 4`, the cycle types `(312)` and `(311,1)` of 10.3 make `pi(Gamma)` 2-transitive of degree 312. The only such groups are `A_312`, `S_312`, and the groups between `PSL(2,311)` and `PGL(2,311)`, whose non-identity elements fix at most two points. Centres with `k(c) = 3` and `k(c) = 4` occur (our runs, 10.5.1), and the 312-cycle is odd, so `pi(Gamma) = S_312`. The sign kernel at `N = 4` is not computed.

(d) *Measured.*
-  Toy fields, exact over all centres: deployed constants reduced modulo `p = 1,048,627` and six random-constant seeds, 3 to 8 S-box layers, partial rounds included, 27 cases. `P(k >= 1)` lies between 0.39214 and 0.39436; the largest deviation from 0.3934693 is 0.00133, that is `1.36 / sqrt(p)`.
- The real field: the organizer-run tests of 10.5.1 and our runs, reproducible observations at `m = 12` and `62`; no probability bound is drawn from them.

(e) *The extrapolation.* At `N = 23` neither the monodromy nor the counts can be computed. Weil's bound exceeds `p` for `j >= 2` (relative error `2^86.6` at `j = 2`).

The premise states that this `F` stays within `0.0003693` of the law of (a) (`q = 0.3931 <= 151/384`): no structure appears between the third layer and the 23-th that changes the law of the positive fixed points by 0.1%.

The measured deviations shrink like `p^(-1/2)` and do not grow with the degree. On the toy fields the deviation is `1.36 / sqrt(p)` . The counts of Grok job 139 give `eps ~ 3.1 / sqrt(p)` over degrees 5 to 1,953,125 (10.3).

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 or of Appendix S (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - S3)/2^256 = 1/2 - 7.869e-40` (`S3` of 4.1.1) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `S3` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - S3)/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`. This is a proved bound under the random words, not a premise and not a sample.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries e6dcb600 and 1aa56884, with the allowance and the organizer-run tests of gta6rp's entry c1364311)

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 5,960,464,477,539,062`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.003` (`2^-8.38`).

Four fields (as in claim.json). **Role:** score-critical for the success probability only. The time and memory bounds hold for every sequence: stage D is charged for the normal sequence, every division tests its quotient and every call its return, and on any other case the trial ends after a prefix of the charged work (6.3). **Scope:** the pairs `(g_c, R_c - 1)` of the target `poseidon-orchard-r17-prefix-v1`, `c` uniform on `F_p`; nothing is claimed for other round counts. **Extrapolation and evidence:** for a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-148.2`. That bound does not transfer directly, because the coefficients of `R_c` have degree about `p` in those of `g_c`; the premise asserts far less than random-pair behaviour, an abnormality probability of at most `delta = 0.003`, which is all the bound of 9.2(d) uses (every `delta <= 0.0030999` keeps it at least 0.39). Measured support, organizer-run (10.5.1): the experiments `euclid-normal-n2-t256-l2-a` and `-b` compute the complete sequence of `(g_c, R_c - 1)` for this construction on the truncation `F_2` of the digest polynomial (10.3; `m = 12`) at 512 organizer-seeded centres each, and return a witness pair exactly when both sequences of a trial are normal; the one-centre tests also compute it at `m = 12` and `62`. Zero abnormal sequences in these runs is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.003` is the declared premise). Our runs of an earlier version of the program (its normality computation, before the one-centre tests were added): 1,066 sequences at `m = 12`, `62` and `312`, every quotient of degree 1 (10.5.1). Reported by our earlier entries, not organizer-run (10.5): the complete sequences on the sibling targets with `r' = 0` and `r' = 1` partial rounds (`m = 7,812` and `39,062`), every quotient of degree 1 in all 10 runs. **Limitations:** the tests reach `m = 312` (the sibling runs `m = 39,062`), far below `m = 5,960,464,477,539,062`. Normality is computed inside the submitted program; the runner checks only the returned witness pairs, so the tests are evidence under trusted execution of that program, which is printed in full in `experiments/exp_euclid.py`.

## 10. Evidence

This section is the evidence for the premise `H-ONE` and for the digest of the target. The computations of 10.3 are ours; the experiments of 10.2 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.2 The organizer experiments declared in `experiments/manifest.json`

Eight experiments of kind `python-message-pairs-v1` (five here, three in 10.5.1), run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The three Python sources are 56,878 bytes together (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r17-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run is the evidence: 256 of 256 trials returned a verified pair at r = 17, and the output was byte-identical on repetition. Our own earlier local run of the same events (plain Python on our machine) agreed: 256 of 256 trials.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 17: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining twenty-three rounds applied to `alpha + beta W` (`deg F = 5^23`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-ONE` is about (a root of `g_c`). The count of returned pairs at each width is a reproducible observation of the construction's own antipodal pairs on the target; no probability, rate or population bound is drawn from it (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed), and it does not enter section 9.

The intake report of the organizer's run records 232, 115, 36, 5 of the 256 trials with a verified pair for `w` = 6, 8, 10, 12 respectively, and byte-identical output on repetition. 

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-ONE` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.

**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B. Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the construction's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 23`; the line and the first layers do not depend on r). The results:

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the construction's line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-ONE` (9.1) extrapolates the measured trend (`w = 1` at `N = 1, 2, 3` on the deployed constants, below) to `N = 23`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the construction's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend, and the lemma gives w = 1 or w = 2 given (a) and 2-transitivity.

**Grok job 139 (the counts of the premise on toy copies).** Grok (xAI) computed `N*` and `N_off` exactly for width-3 Hades toy permutations over prime fields `p < 2^22` with `p mod 5 != 1` (S-box `x -> x^5`, uniformly random MDS matrix and round constants, the line `(L, 2L+1, 3L+5)`, `N` full rounds and `k` partial rounds, `deg F = 5^(N+k)` up to 1,953,125), by the fibre counts `N* = sum_y m_y (m_y - 1)` and `N_off = sum_c 4 r(c) (r(c) - 1)` (checked against brute force on the small cases), on 1,316 generic seeds with `p >= 1024` (the five degenerate seeds, where the degree drops, are excluded). The relative error `eps_obs = max(|N*/p - 1|, |N_off/p - w|/w)` with `w = 1` is `<= 0.2197` for every generic seed with `p >= 2053`, and the least-squares fit is `eps_obs = 3.10 / sqrt(p)` for a typical seed (`5.17 / sqrt(p)` for the maximum of four seeds), with no dependence on the degree (adding a term linear in `deg F` moves `R^2` from 0.5508 to 0.5509; the mean of `eps sqrt(p)` is 2.3 to 3.7 for every degree from 5 to 1,953,125); at `p = 2,097,169` the largest generic `eps_obs` is 0.0068. These counts support the premise of 9.1: the deviations shrink like `3 / sqrt(p)` and do not grow with the degree.

### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 17` applies the Euclidean algorithm to `g_c` (degree `m = 5,960,464,477,539,062`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. This section and 10.5.1 are the measured support of the premise `H-NORMAL` (9.5): stage D is charged for the normal remainder sequence and a trial ends at the first quotient of degree other than 1 (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at the gcd (degree 0, or degree 1 at the r' = 0 centres 2, 4, 7) after `m - deg gcd` divisions, and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core.

At `r = 17` the stages need about 763233830 GB and 1.3e21 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7.

### 10.5.1 Organizer-run tests: normality and one centre (`experiments/exp_euclid.py`)

Four experiments of kind `python-message-pairs-v1`, declared in `experiments/manifest.json` and run by the organizer's runner (program `experiments/exp_euclid.py`, 28,019 bytes, Python standard library only): the normality tests `euclid-normal-n2-t256-l2-a` and `-b` (two centres per trial, `m = 12`, 512 sequences each) and the one-centre tests `one-centre-n2-t256` and `one-centre-n3-t24` (one trial of the algorithm at depth `N = 2` and `3`, `m = 12` and `62`). The design follows gta6rp's organizer-run normality tests (entry c1364311, its 10.5.1); the program is our own. For each computed trial the program takes a centre `c` from the trial seed (the rule of `exp_line.py`) and builds, exactly over `F_p`, the polynomial `F_N(c + X)`: the `F_N` of 10.3 (start state `alpha + beta W` of the line `j = 0`, the S-box layers of rounds 2 and 3 (full), then 4 and 5 (partial, coordinate 0), the MDS after each; degree `5^N`). It checks `F_N` against direct iteration of those layers at `c + 1`, `c - 1`, `c + 2`, `c - 2` and the odd-part identity `2 x g(x^2) = F_N(c + x) - F_N(c - x)` at `x = 1, 2`; takes the monic odd part `g` (degree `m = (5^N - 1)/2`); computes `R = X^((p-1)/2) mod g` (253 squarings and 45 multiplications by `X`); and runs the complete Euclidean sequence of `(g, R - 1)` down to the zero remainder, recording the degree of every quotient. The sequence is normal when `deg(R - 1) = m - 1` and every quotient has degree 1, the condition of 6.3 and 9.5. A normality trial whose two sequences are normal, or a one-centre trial whose sequence is normal with `1 <= k(c) <= 16` and whose isolated root passes the check `F_N(c + s) = F_N(c - s)`, returns two distinct canonical messages: the points `c + s` of the line, `s = 1, 2, ...`, are mapped back to `(nk, rho)` as in 10.2(b), and the first two whose digests of the selected target agree on the first 6 bits of the big-endian reading are returned. Among 65 points such a pair always exists, so a computed normal trial always returns a pair. Every other trial, and every trial past the first `T` (`T` = 256, 256, 256, 24, the sandbox budget of 20 s), returns two nulls. The organizer-checked count of returned pairs therefore equals the number of computed trials that pass. The per-trial counts listed in the manifest are reported as observations, which the runner labels untrusted. Expected: every computed sequence is normal in the normality tests; for the one-centre tests the law of 9.3, a theorem at `N = 2` and `3`, gives the fraction of centres that pass, and the returned counts are reproducible observations consistent with it. No probability, rate or population bound is drawn from any of these organizer-seeded trials (public seeds; nothing is assumed about the trials being independent or identically distributed), and none enters section 9. These counts are reproducible observations consistent with the premises; the organizer-seeded centres are not treated as independent unselected samples, and no interval or population bound is drawn from them. For `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2` (its layers come before the final full rounds), so the tests measure the same family of pairs as the premise; only the witness uses the digest at r = 17.

Our runs of an earlier version of the program (its normality computation, before the one-centre tests were added; 2026-10-18, seeds of our own): in the runner's image `python:3.12.12-slim-bookworm` with one CPU and 128 MiB, 256, 24 and 2 sequences at `m = 12`, `62`, `312` in 4.6, 5.5 and 5.4 s of program time, byte-identical on repetition; with further seeds (Python 3.14), 512 more at `m = 12`, 256 at `m = 62` and 16 at `m = 312`. In all 1,066 sequences (768, 280 and 18) every quotient had degree 1, and the gcd had positive degree in 301, 117 and 7 of them (fractions 0.392, 0.418 and 0.389; observations of our own runs, not organizer-run, and not used in section 9). What these tests show: under trusted execution, the construction's own pairs `(g_c, R_c - 1)` have normal remainder sequences at `m = 12` to `312`. What they do not show: anything at `m = 5,960,464,477,539,062`, where `H-NORMAL` remains a premise that asserts only `delta = 0.003`.

## Appendix L: the line program `L` (this entry; the form of mpjunior92 `1291df5c`, listing form of `4c6dc4cf` Appendix L)

### L.1 Construction

`L(x) = F(x - E0_0) / OUTSCALE`, `F` the digest on the line of 2.2 (`W = tau^5`). The state after round 1 is `A + W B` (2.2: `alpha = A + c_2`, `beta = B`); the round-2 S-box input of lane `i` is `A_i + c_{2,i} + W B_i = B_i (W + E0_i)`, `E0_i = (A_i + c_{2,i}) / B_i` (every `B_i != 0` on the deployed constants). With `x = W + E0_0` lane 0 is `B_0 x` and lane `i` is `B_i (x + e_i)`, `e_i = E0_i - E0_0`. Every lane is held as its true value divided by a known nonzero scale; an S-box of a held lane is 3 multiplications and divides the true output by the fifth power of the scale, which the next linear layer absorbs, each output lane held divided by its coefficient on `z0`: a dense layer with the next round's constants is `y_k = z0 + a_k z1 + b_k z2 + k_k` (2 multiplications, 3 additions). Partial rounds use the sparse form of Grassi, Khovratovich, Rechberger, Roy and Schofnegger (USENIX Security 2021) with the same scaling: lane 0 is held as `lambda h0 + gamma`, lanes 1, 2 as `P (h1, h2) + q` with `P = Mww^j P0` after `j` partial rounds (`Mww` the lower-right 2x2 block of `M`) and `P0 = Mww^-r D`, `D` diagonal, so `P = D` at the exit; one partial round is `u = h0 + k`, `x5 = u^5` (3), `h0 = x5 + n1 h1 + n2 h2` (from the old `h1`, `h2`), `h1 = h1 + v1 x5`, `h2 = h2 + v2 x5`: 12 operations. Counts: entry 2; round 2 (S-boxes 9, dense layer with the round-3 constants 15); round 3 (S-boxes 9, into the partial form 6 multiplications and 6 additions, `D` normalising the `z0` coefficients); `r` partial rounds, 12 each; exit 3 (the round-60 constants); rounds 60-62 (24 each); round 63 (S-boxes 9, row 0 held divided by its `z0` coefficient `OUTSCALE`, 2 multiplications and 2 additions): `2 + 24 + 21 + 12 r + 3 + 72 + 13 = 135 + 12 r = 339` at `r = 17`. Every constant is a closed formula of the deployed constants (6.2).

### L.2 Check

`E0_0 = 0x3a4bd2e80f62c6cde67f816c4a67f17bbd43a70c4d2fca9784cc22ba736569ff`, `OUTSCALE = 0x17db9517cf5ad9c23c0321880241842b0ebf7881fdf24856a090e1a3590d1774`. Our program (standard library only) builds `L` from the organizer constants file, executes it with an operation counter, and asserts `OUTSCALE * L(W + E0_0) = digest(message(W))` with the reference rounds of `verifier/poseidon.py` at 100 random `W` (r = 17: 339 operations executed each); `message(W)` is the canonical pair of 2.2.

### L.3 Constants of `L` at r = 17

```
e1 = 0x3be50976ed9a36ed2193914455ff9b57110fbf67a5b17ed704b45f293ea16e52
e2 = 0x3f30a282c5b89b63ebabd204830a688ed50a9b6efae93b0434327bc6ee6794ba
r2_a0 = 0x3c6619d59a8bff38f5e82d878afa1572b0de568df0f44727f5eebde8a520bb09
r2_b0 = 0x182d2a33a05d2cf29f1f85fe18c296f96b485a4642bc47e0c096ed309334539d
r2_k0 = 0x2ee7536394e8e06338e11ac0050022dbb3b058a98b297c7058173227f0c5f0b5
r2_a1 = 0x2840fd97d3b51c865aebbadaaf03e4d7bb8a06a0ed729dcfdcb232668cc21036
r2_b1 = 0x24d83320489d9f6acf96dd55a02381c22b9ae568c345217a4d3a3ebc6c68733e
r2_k1 = 0x2ccbdb9536e63c46650cd03d3d3591a809a0e4a07b7c585b6e3b8c06db9ef42e
r2_a2 = 0x37d59d01327c0e9ea9ea53e1bb643c6d9e2dd42b1be96d0ae502e5ad6685ef91
r2_b2 = 0x3890183d51fa8d8e79f20615fc8cdc01a44e932c575a7833d6118362f946104a
r2_k2 = 0x007ee07c6df20f7997f9b145f92b2e13ed55421ba5fd692e198160cbd4b2086e
pf_a0 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
pf_b0 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
pf_a1 = 0x04fe4af9f711df603f5a8469425ca7929b38d107329d114a05fda6c05042e17f
pf_b1 = 0x339027b5de4f5edcfebb4f0aa4b473cdfbb3577357c38aca37764eee8a64c375
pf_a2 = 0x335afbd17281d3775eed4501cb4c751f29e11fdad72c259b26b2eb1e03e40394
pf_b2 = 0x0c64b97b1e4c3cc40c96040c84d3049a37523218bd8574c92281945716a1c36c
p0_k = 0x34058bb8920441623716adeb0155288a2cca42fa34af13309820b9953e4336cf
p0_n1 = 0x1dfc5c70d867e8ba0fff63f9519d05b21e90e00e2d886ca7b009132be797d616
p0_n2 = 0x2d0fc77d474a5802f2b90e9196709e00d7652196699e6f0a42f584cda54f84f2
p0_v1 = 0x2a544187e86511124775480535da07ad99bb041fa777ca62db9839ae19c5ff89
p0_v2 = 0x01f1e178494911b8aa4c3303ddaea2b867a03d09b333f77857f9351645f0f9a5
p1_k = 0x266144e217c50738f29b2b098b54686e360c94c1f64cc0b43c6b0a0cc37fc9eb
p1_n1 = 0x1dda871fea2214e7aed5a1d4b6290b15458c45dbd64f6bdb9940bd26987bbd0e
p1_n2 = 0x277224908c75c30a0d14009b58e3104c2fc17602eac5eae6a87f1e2de308596a
p1_v1 = 0x14f67269f11acd2c913cc1f285c4d9cdf59079f09caed6bda265dbff2996e8a8
p1_v2 = 0x293743faf6be34ea13dbfb8439292f566c83f84164c28a6b08c2ee15465fcfdc
p2_k = 0x1565f5ef914944ad12c16e36ec616abd4dd0f8c94d990dc4ff415ad5a506d732
p2_n1 = 0x38972e0ac2a8bef4fad22bed4b58c627824f5c357ae17db1f70fd7b9a952b9a9
p2_n2 = 0x13deee3614085d00923428ed8404cbade18d8cb34ba3ed2b5f5eafc655594751
p2_v1 = 0x0ee1b32405b97b37d1a3c4fc7f741496587191ee1259a0063697a6d2a72df3b2
p2_v2 = 0x35a1810a93deb42caf73fedce9c2d3d0beab09112ac07bd14cd05a5203aa2958
p3_k = 0x31f134c3cb80372eff4d98f34741c78bf04e38ca64691c338f55660789f29b61
p3_n1 = 0x2e85e250345aad375bd21805fe9ee068aca539f66cc4662a4f9e7fab73d607e8
p3_n2 = 0x3217760c62af4c54cea33378b46ac19f4df48c06d4576b649273d172cb660452
p3_v1 = 0x2fb4cea068934f0a9b78223e74342f34c2ff9dadb5b8e221de68ff928e2b352e
p3_v2 = 0x071d1070908b12cb4e8a533f2a9046d9edef4493091c82857d26857ce86c263f
p4_k = 0x2ca8302ed55720cd2a1b9478af5a5f4a223bd4fe9f778963e71519b2113aecb6
p4_n1 = 0x3c4b13b173c4862b3cd8113160f185638682188cc6b9b37e0a9ca146714fcd10
p4_n2 = 0x1fb79e9117757f727841e7da330191dae23c8ed888ec109e324246c499d925dd
p4_v1 = 0x28854eb642c9ed37c8f12949cede12297333091b605bf8d8727b19dd23238aab
p4_v2 = 0x31d9a4d019d418f7e60aba8b63e171f73c19c1ee32036d72a43f5b268ea7ca3e
p5_k = 0x0fb74a39edbf99a426252d65ab2f5b558bfc999d3ec24ddad0ab5d3c66a49cba
p5_n1 = 0x0849b2f7a8d8cdc788b7a37431d766492a805d416a6116176a1b38b8ecb0e7c3
p5_n2 = 0x149562ac1f8264e6013d4832e5323dc4863f82cfc76dababb9945fcee2f3cc9c
p5_v1 = 0x0cc75bfbd31e155b202497118c73a35b94de84797dffa1848446bd5f71b6dbaa
p5_v2 = 0x0dcda988d4665d8722f6aac700b602c58007060d9891b491bde8debe13ee774d
p6_k = 0x0111ad1e97070de2c1edeeacffc3a8f1f81c885c649e20b3955b4a2fac77be23
p6_n1 = 0x03371cee0ea3574b78918508abdf18808fbc15c47fad0f304e21d89009589b49
p6_n2 = 0x274e5f3dbee9999afafdd13ebe6593ef7485dcff0b464bc61e051040995e3011
p6_v1 = 0x08a15bc96aadfc483cbab6e2faf38e62b77bd806d6e0431691b534d4ced7965d
p6_v2 = 0x29639a6ac7b87c6dfb978266ef236ced22c4147b3ee96f6371f17a23e197da25
p7_k = 0x193745c8d553088262dcb58e17e3468dd24422f6a3987ac69306c8d2935e7ff2
p7_n1 = 0x0cf31dd94eaeea2ec7d4b9d8fc7389d99a73454c2c022f251d36b7348d3ebcc8
p7_n2 = 0x13e42051ac10ef1ae8ed694b2c17ec1d381dfa4b0ba1c20c5b3aa2ebe19653c5
p7_v1 = 0x2c3ea971295f22cf632bb98efa46fe20a1e6021fc0dde20403ba8be719041e17
p7_v2 = 0x0df9d4cbc6d8f36c94c4f6a62468b9944097411c5b0160429dd7569c7b0d88d2
p8_k = 0x35f659b85ed4e1f3c1c3e1f1fdde5ed7f9eb3b2b83d43f106d2416dba5965f7b
p8_n1 = 0x3fc8e1bbeb1923f866bd02e9dc9bf4d331727dea3a1d1fcbbb25769d1d047cc9
p8_n2 = 0x1319f805bfbbdd9fe113bb0ad895c5d3cf9e77801dfa0817aad77a2a83e85fd5
p8_v1 = 0x3da75da012362b40c7deb3ba7a53b4af6fefa1c274bef06a3d49af889a241900
p8_v2 = 0x38e65392d667ad0291b16493752a98f3fc055979d67c6cc4acf420daadb994cd
p9_k = 0x1fb04a7de4c56520f2aaf051fc8ec4eab6978daf4ad22c53ef4fde9bf6100f69
p9_n1 = 0x3eb2121eff79b3a42cf7c684a4e93afdf7337f8752360c5db76d585b2887ef36
p9_n2 = 0x26f79f42c0129de3c5ebb577c3e9577f2669019d5a1e8ce309d3e14b41ae3c1e
p9_v1 = 0x18948d3bcf2d9b1679dbf7d133c28e71a8f77998f53cac069af5d1da4d3ef3f4
p9_v2 = 0x2e0e64f2ac814bf757ff6cb13a3a9818a174bca9eab9bea91a0bd55008676a30
p10_k = 0x0194f78e9a984a28533ec9f0ef5d08ac0ef765a3eade233a3b45b21ae5fb06ee
p10_n1 = 0x32f607febdf345c1232552c47a72eeaf49e7bc5d39cf54eb87bd441f483477fd
p10_n2 = 0x34ebdf8b6c68c18ed49f221df67ef9ec88c3326f3468b84a1ef384e535b234f8
p10_v1 = 0x1a36f05f374e2f878e70bfcadfb7b91472dc644e4a502bb7171b5b761a0ef328
p10_v2 = 0x3363f765056708f106ecc10635e516540eada76b2a7afa91f8f4ea6d17a2b317
p11_k = 0x31a5317e72939ab937a13512d323f3d6e2545604b200351fe2c862a30e2c0059
p11_n1 = 0x1a6a43fc2d11b6811bff746145373e4400a44e3dfaedaea379b99d0ed1cbf2ee
p11_n2 = 0x338b01ec031164e22f2a3b87b8c16ef64c3ec2e4552c75000d6ee916d09ed225
p11_v1 = 0x21f871080d8aac4d50df990cd3bae1ed8565485e63ba0be2945f9fac4e68098a
p11_v2 = 0x3f8fce43f559a6a50c06087c204a63c76c94a884dc5d1cbba83be961e2b4ca9f
p12_k = 0x1782f320036b1c7bc40a2dd19526d90235056921c75ac9170bfe77cd1becbcb2
p12_n1 = 0x2fc29312c5ea6767099616bf4ae72392c7675e21468e5bb184508c74e68b2e27
p12_n2 = 0x248ee0fe4e600cffa78e56097135444a77670b9a89b2dae33d2510d66a1ddf79
p12_v1 = 0x3286726693e6789e667610c3c349f0ebb6c1592b0782f056181c0d0755f42e58
p12_v2 = 0x1b0e42afa19f830c5fce83bee7a401b1529c31318434a57a737b81edef529f56
p13_k = 0x26d9b6dbc2d14b67b0301adf9666424dc64420144c0a37dff3d57b6cacf108c7
p13_n1 = 0x08fe6b6ceaa555bc446769c2299bdb78dc3bf76c9f2cdf30da456d975bb7b660
p13_n2 = 0x289bdb24fc937c2c95cfa79cb8acceb3b9ba4847e72162aec8fa63d7e2dfa9a0
p13_v1 = 0x2bad1cfc63cffed2118a3161d018566d33fe2019f4c1a31b7168e74295e3f76a
p13_v2 = 0x0a8074327e0d06f8c17089f79321a136fcff28d132170557d9b77284188e873d
p14_k = 0x2bca342742d0580cf65fa95da4684862e4e0e66ed103e200add1a4f1940701ba
p14_n1 = 0x3b609a09e33cd9180fb971e8a5711da3e29310e7c6df6f6faea245e836903c43
p14_n2 = 0x181a19729278a7083281761b8117dd9108879646e44eca76c63470257d37c9b5
p14_v1 = 0x03e1bc9fd8c3347c580c7e2eeece3db170bf23290dc33f5f3ab0d848bcc50088
p14_v2 = 0x2ca0edc4e545c77586202667dae03297deece3c6275b4679fd30f732521eaa19
p15_k = 0x0faa11fee955d83c4d2df7dbd66296897532dab0798f422e29a978527a54c52a
p15_n1 = 0x202454a43fa5ce7fe88dcefb186de184512c43b902de6c2b3024c5261043fa8e
p15_n2 = 0x3feaa7c047ab00bca3db2f65867e11a05f8ab432ada7a8f63633ecf90594b707
p15_v1 = 0x02891b3b5bfafcf6537fe8b05362d1330df6b6f3e322cd7b2b2f757669607d94
p15_v2 = 0x1caa70dd349a00bd35db552f9437e64992251a0a36769606e34ee80bb77b0ec3
p16_k = 0x254ff5c8d0e8ce1725d0fabdf7b0b71b6d72caf59a43c2bb470c46d1796b8942
p16_n1 = 0x375a8f6155bfeb767acf27f94abd65f1d70d8dd52ae5d771c1de36c9512867b9
p16_n2 = 0x3cc9d95fe5c8a1bb3ee5c2e1a7e912d2a2cfa7335a0b60af75c18516c61c901f
p16_v1 = 0x0906e00e0a7112bd060ee5df9a4636bb0edb2756cc20dd9eac100de276775578
p16_v2 = 0x3bba524e6bed950a3e37a98f3a68e5ada5e515445de3c68245685be781bf16ae
x_k0 = 0x38b5a390ebcb3190ba2e53d6cb4633ca34bb4fa5b8879b9ccfd5df21f96688d8
x_k1 = 0x15cbca93e975fd8ad41cf255d49d347a2322651239b2d6d10cd2c622552a2263
x_k2 = 0x29fae40e2332773cef4c3af5b8fdbb013672e23d5c99bca5c296763e633dcedd
r60_a0 = 0x003bbf458ab1e9d940ebc5e1f7955ec47abad4660f71dd5958679200af34e6e8
r60_b0 = 0x22b136e0781706ddd5812ec81208aab800f7a7feb87aea27c19addb6ac4ed8f5
r60_k0 = 0x317aca53d0a6d05dd59227b18d2277f77fba9c46285f66fc3f495de98851b85e
r60_a1 = 0x09105d59b8e6674a06ad7a7fa10ea7f334bc902eab353dcd45042d91fb610948
r60_b1 = 0x0ffde87c6a712f674c7abb772178243ce3b146029d6cfe65bea79896de51a0bd
r60_k1 = 0x0c1de64562bbcbd2412fb2c90819ae8e894ad352414e3a1a4d91c4d06042a1ef
r60_a2 = 0x0e68dc514a8b9fdc6013ec448576b4a210b7fa1ed9903df557e00721cfd4d30e
r60_b2 = 0x0c17d567bde816467fd0274cae2bf7a1b7862a38bb5a81104fcd0381749e19c8
r60_k2 = 0x377e1a96fcb01994c33606bd9cb3e176e8ec1b05fa04f7e8286ea23e0da7b3ad
r61_a0 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
r61_b0 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
r61_k0 = 0x1dfc894e0bd5ae3a915da5c54286a0d44e77caf501d192c223e427b5cc1775a6
r61_a1 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
r61_b1 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
r61_k1 = 0x15a6074edc8c3e94353408aa7ec4fb666a93a443e3d9f8fbb62a0492e6c8e164
r61_a2 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
r61_b2 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
r61_k2 = 0x240d0e66bcb8aa06a43ef7acc269e8f181571476b71fe63d953c8294bd10f32e
r62_a0 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
r62_b0 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
r62_k0 = 0x2576836a4cd639ab27431d6f85eb1445b836dd9acafbc112553983fa1f22cbb3
r62_a1 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
r62_b1 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
r62_k1 = 0x0b93b5b28cbbcb825c9a20c07dfeaba116c331b315dcabfe61da9fb8613ca627
r62_a2 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
r62_b2 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
r62_k2 = 0x22a6728673fdf64270e172a18d40ebe132a29a0195c157809eab6133c016edde
o_a = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
o_b = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
```

### L.4 Listing of `L` at r = 17 (339 operations; `x` is input and output; the other names are the constants of L.3)

```
y1 := + x e1
y2 := + x e2
t2 := * x x
t4 := * t2 t2
z0 := * t4 x
t2 := * y1 y1
t4 := * t2 t2
z1 := * t4 y1
t2 := * y2 y2
t4 := * t2 t2
z2 := * t4 y2
m1 := * r2_a0 z1
m2 := * r2_b0 z2
s := + z0 m1
s := + s m2
x := + s r2_k0
m1 := * r2_a1 z1
m2 := * r2_b1 z2
s := + z0 m1
s := + s m2
y1 := + s r2_k1
m1 := * r2_a2 z1
m2 := * r2_b2 z2
s := + z0 m1
s := + s m2
y2 := + s r2_k2
t2 := * x x
t4 := * t2 t2
z0 := * t4 x
t2 := * y1 y1
t4 := * t2 t2
z1 := * t4 y1
t2 := * y2 y2
t4 := * t2 t2
z2 := * t4 y2
m1 := * pf_a0 z1
m2 := * pf_b0 z2
s := + z0 m1
h0 := + s m2
m1 := * pf_a1 z1
m2 := * pf_b1 z2
s := + z0 m1
h1 := + s m2
m1 := * pf_a2 z1
m2 := * pf_b2 z2
s := + z0 m1
h2 := + s m2
u := + h0 p0_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p0_n1 h1
m2 := * p0_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p0_v1 x5
h1 := + h1 m1
m2 := * p0_v2 x5
h2 := + h2 m2
u := + h0 p1_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p1_n1 h1
m2 := * p1_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p1_v1 x5
h1 := + h1 m1
m2 := * p1_v2 x5
h2 := + h2 m2
u := + h0 p2_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p2_n1 h1
m2 := * p2_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p2_v1 x5
h1 := + h1 m1
m2 := * p2_v2 x5
h2 := + h2 m2
u := + h0 p3_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p3_n1 h1
m2 := * p3_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p3_v1 x5
h1 := + h1 m1
m2 := * p3_v2 x5
h2 := + h2 m2
u := + h0 p4_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p4_n1 h1
m2 := * p4_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p4_v1 x5
h1 := + h1 m1
m2 := * p4_v2 x5
h2 := + h2 m2
u := + h0 p5_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p5_n1 h1
m2 := * p5_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p5_v1 x5
h1 := + h1 m1
m2 := * p5_v2 x5
h2 := + h2 m2
u := + h0 p6_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p6_n1 h1
m2 := * p6_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p6_v1 x5
h1 := + h1 m1
m2 := * p6_v2 x5
h2 := + h2 m2
u := + h0 p7_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p7_n1 h1
m2 := * p7_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p7_v1 x5
h1 := + h1 m1
m2 := * p7_v2 x5
h2 := + h2 m2
u := + h0 p8_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p8_n1 h1
m2 := * p8_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p8_v1 x5
h1 := + h1 m1
m2 := * p8_v2 x5
h2 := + h2 m2
u := + h0 p9_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p9_n1 h1
m2 := * p9_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p9_v1 x5
h1 := + h1 m1
m2 := * p9_v2 x5
h2 := + h2 m2
u := + h0 p10_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p10_n1 h1
m2 := * p10_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p10_v1 x5
h1 := + h1 m1
m2 := * p10_v2 x5
h2 := + h2 m2
u := + h0 p11_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p11_n1 h1
m2 := * p11_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p11_v1 x5
h1 := + h1 m1
m2 := * p11_v2 x5
h2 := + h2 m2
u := + h0 p12_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p12_n1 h1
m2 := * p12_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p12_v1 x5
h1 := + h1 m1
m2 := * p12_v2 x5
h2 := + h2 m2
u := + h0 p13_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p13_n1 h1
m2 := * p13_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p13_v1 x5
h1 := + h1 m1
m2 := * p13_v2 x5
h2 := + h2 m2
u := + h0 p14_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p14_n1 h1
m2 := * p14_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p14_v1 x5
h1 := + h1 m1
m2 := * p14_v2 x5
h2 := + h2 m2
u := + h0 p15_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p15_n1 h1
m2 := * p15_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p15_v1 x5
h1 := + h1 m1
m2 := * p15_v2 x5
h2 := + h2 m2
u := + h0 p16_k
t2 := * u u
t4 := * t2 t2
x5 := * t4 u
m1 := * p16_n1 h1
m2 := * p16_n2 h2
s := + x5 m1
h0 := + s m2
m1 := * p16_v1 x5
h1 := + h1 m1
m2 := * p16_v2 x5
h2 := + h2 m2
x := + h0 x_k0
y1 := + h1 x_k1
y2 := + h2 x_k2
t2 := * x x
t4 := * t2 t2
z0 := * t4 x
t2 := * y1 y1
t4 := * t2 t2
z1 := * t4 y1
t2 := * y2 y2
t4 := * t2 t2
z2 := * t4 y2
m1 := * r60_a0 z1
m2 := * r60_b0 z2
s := + z0 m1
s := + s m2
x := + s r60_k0
m1 := * r60_a1 z1
m2 := * r60_b1 z2
s := + z0 m1
s := + s m2
y1 := + s r60_k1
m1 := * r60_a2 z1
m2 := * r60_b2 z2
s := + z0 m1
s := + s m2
y2 := + s r60_k2
t2 := * x x
t4 := * t2 t2
z0 := * t4 x
t2 := * y1 y1
t4 := * t2 t2
z1 := * t4 y1
t2 := * y2 y2
t4 := * t2 t2
z2 := * t4 y2
m1 := * r61_a0 z1
m2 := * r61_b0 z2
s := + z0 m1
s := + s m2
x := + s r61_k0
m1 := * r61_a1 z1
m2 := * r61_b1 z2
s := + z0 m1
s := + s m2
y1 := + s r61_k1
m1 := * r61_a2 z1
m2 := * r61_b2 z2
s := + z0 m1
s := + s m2
y2 := + s r61_k2
t2 := * x x
t4 := * t2 t2
z0 := * t4 x
t2 := * y1 y1
t4 := * t2 t2
z1 := * t4 y1
t2 := * y2 y2
t4 := * t2 t2
z2 := * t4 y2
m1 := * r62_a0 z1
m2 := * r62_b0 z2
s := + z0 m1
s := + s m2
x := + s r62_k0
m1 := * r62_a1 z1
m2 := * r62_b1 z2
s := + z0 m1
s := + s m2
y1 := + s r62_k1
m1 := * r62_a2 z1
m2 := * r62_b2 z2
s := + z0 m1
s := + s m2
y2 := + s r62_k2
t2 := * x x
t4 := * t2 t2
z0 := * t4 x
t2 := * y1 y1
t4 := * t2 t2
z1 := * t4 y1
t2 := * y2 y2
t4 := * t2 t2
z2 := * t4 y2
m1 := * o_a z1
m2 := * o_b z2
s := + z0 m1
x := + s m2
```

## Appendix B: the stage-B point loop on root tables (this entry; the method of mpjunior92 `1ac48175`, on our cosets and mixed-radix layout)

Layout (section 3, 4.2): coset `k < kappa = 925186` fills the transform input `k` of `B = 3 n` points, `n = 2^31`, and stores the value at `s_{k,i} = v_k zeta^i` at position `row * n + rev_31(i mod n)`, `row = i mod 3`; the inputs of the cosets follow each other. The base loop ran over `(k, i)` and paid per point the two point additions, one subtraction, one multiplication by `1/(2 s_{k,i})`, the two recurrences, the store with its address 2, the calls 10 (the two evaluations, the index routine, the row counter), the index routine `12 + 7 * 31 + 2 = 231` and the loop control 3: 252 per point, `252 kappa B + 2 = 1,502,037,285,607,047,170` (the loop work of row B in the base ledger, itemised by our counting program).

Here the positions are visited in storage order: coset `k`, then `row` (3), then `j` in `[0, n)` by the four digits of `j` (7, 8, 8, 8 bits, high digit outermost). By the Chinese remainder theorem `i = (row * e3 + k2 * en) mod B` with `k2 = rev_31(j)`, `e3 = 0 mod n`, `e3 = 1 mod 3`, `en = 0 mod 3`, `en = 1 mod n`, so `zeta^i = +/- zeta^(row e3) * (zeta^en)^(k2)` (`zeta^B = -1`), and the stored value is the same for both signs (section 3). `(zeta^en)^(rev_31(j))` is the product over the digits `x_l` of `j` of the table entries `T_l[x_l] = (zeta^en)^(rev_(d_l)(x_l) * 2^(31 - o_l - d_l))` (`o_l` the bit offset of digit `l`), and `1/(2s)` the product of the inverse tables with the row constant `1/(2 zeta^(row e3))` and `w_k = 1/v_k`. Per trial `c' = c + E0_0` and the start pointer 2 and `v_0 = w_0 = 1` 2; per coset `v_(k+1) = v_k + v_k`, `w_(k+1) = w_k / 2` (a product by the constant `1/2`) and the loop control: 5; per row the two row constants loaded with their addresses and multiplied by `v_k`, `w_k`, with the loop control: 9; each outer digit level loads two entries and forms two products (9 with its loop control); the innermost iteration is the 18 of section 3; every loop exit 2. Tables: `896` entries and their inverses and 6 row constants, `1,798` words, built offline (6.2). Levels: cosets: 925,186 iterations, 4,625,932; rows: 2,775,558 iterations, 26,830,394; 7-bit digit: 355,271,424 iterations, 3,202,993,932; 8-bit digit: 90,949,484,544 iterations, 819,255,903,744; 8-bit digit: 23,283,068,043,264 iterations, 209,729,511,358,464; 8-bit digit: 5,960,465,419,075,584 iterations, 107,334,943,679,447,040; total `107,545,495,681,159,510` operations (was `1,502,037,285,607,047,170`). Our program executes this nest with an operation counter on plans of `3 * 2^a` points with several cosets (`a = 6, 7, 8, 9`, 2 to 5 cosets), asserts at every position `s^2 = (v_k zeta^i)^2` against the base layout and `2 s u = 1`, and the counter equals the closed form.

## Appendix S: stage E, register-resident (the procedure and charge form of `4c6dc4cf` Appendix S, as in `1291df5c`, with both gcds of 4.1.2)

Input `G` monic, `1 <= d = deg G <= 16`, a product of distinct linear factors over `F_p` (4.1.2). If `d = 1` the root is `-G_0`. Otherwise `H := G` (loaded into field registers) and at most `Z = 64` rounds: 1. draw `a` (one word, 31, 4.1.1); if it is 0, `a := 1` (the zero test 5 and the replacement 2, charged in every round, as in 4.1.2); 2. `B := (X + a)^((p-1)/2) mod H`: start `B = X + a` (3), then for each of the 253 bits below the top bit of `(p-1)/2` one squaring modulo `H` and, on the 45 one-bits, one multiplication by `X + a` modulo `H`; 3. `B - 1` and `B + 1` (2); 4. `G_+ := gcd(H, B - 1)` and `G_- := gcd(H, B + 1)`, monic, each by inversion-free elimination: while the second row is nonzero, order the rows by degree and replace the higher row `A` by `lc(B) A - lc(A) X^(deg A - deg B) B` (at most `3 d` field operations, 6 control, 3 for the ordering), strip zero top coefficients (2 each); then one inversion of the leading coefficient by square-and-multiply on the 254 bits below the top bit of `p - 2` (76 one-bits: 254 squarings and 76 multiplications, 4 control per bit) and `d` multiplications; 5. keep, as the new `H`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant (three comparisons with their branches 6, the copy of the kept factor into the registers of `H`, at most `d + 1`); 6. the round test and count (3); stop with the root `-H_0` when `deg H = 1`. A root `r` of `H` lies in `G_+` iff `(r + a)^((p-1)/2) = 1` and in `G_-` iff it is `-1`, as in 4.1.2 for the shifted `G`, so the lemma of 9.4 holds for these rounds unchanged.

Charges at degree `d` (field operations 1 each; every operand is a field register: `H` (`d + 1`), `B` (`d`), the square (`2d - 1`), the two gcd rows (`2d + 1`) and the kept `G_+` (`d + 1`), at most 128 of the 256 field registers of 4.2 with `a` and the loop registers; no load or store inside a round): squaring modulo `H`, `S(d) = d (d+1)/2 + d (d-1)/2 - (2d - 3) + (2d - 3) + (d - 2) + 2 d (d - 1)`, `S(16) = 750`, plus 4 of bit control; multiplication by `X + a` modulo `H`, `4 d`; one gcd, at most `2 d - 1` eliminations, `(2 d - 1)(3 d + 9) + 2 (2 d + 1)` with the strips, the inversion `254 * 5 + 76 = 1,346` and `d`: `3,195` at `d = 16`. `R(d) = 38 + 3 + 253 (S(d) + 4) + 45 * 4 d + 2 + 2 gcd(d) + (6 + d + 1) + 3`, non-decreasing in `d`; `R(16) = 38 + 3 + 190,762 + 2,880 + 2 + 6,390 + 23 + 3 = 200,101`. Row E charges every one of the 64 rounds at `d = 16`: `64 * 200,101 + 1,000 + 200 = 12,807,664`.
