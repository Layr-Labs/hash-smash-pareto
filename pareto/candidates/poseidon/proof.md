# Orchard Poseidon, r = 10: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, half-gcd, one centre

## 1. Claim

Target: `poseidon-orchard-r10-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, ten partial rounds 4, 5, 6, 7, 8, 9, 10, 11, 12 and 13, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

Authorship. This package is the r = 10 entry `6f1d38c7` (Jbenisek) with two changes made by this entry, both in low-order rows: (i) every line evaluation of stage B is the straight-line program `L` of Appendix L (`135 + 12 r = 255` field operations: scaled lanes and sparse partial rounds in the form of the r = 56 entries `3a1b25b6`, `9fb982e8`, `69e14209`, re-derived and checked by our own program) in place of the `C(10) = 426` operations charged per evaluation; the loop around the evaluations is otherwise unchanged, so row B loses exactly `154,618,822,656 * (426 - 255) = 26,439,818,674,176` (section 6); (ii) stage E keeps its polynomials in field registers and charges every field operation once, with an inversion-free gcd (Appendix S), row E `12,603,760` in place of `166,079,773`. Stages A, C, D, F and G, the arena, the premises, the success bound and the experiments are those of `6f1d38c7` unchanged; text that says "our" entry or "we" outside the changed parts refers to the authors of `6f1d38c7`. Where the text of `6f1d38c7` describes a line evaluation by the charge `C(r)`, this entry runs `L` (`L(x) = F(x - E0_0) / OUTSCALE`, Appendix L; evaluating `L(c' + s) - L(c' - s)` with `c' = c + E0_0` gives `2 s g_c(s^2) / OUTSCALE`, and the normalisation to monic removes the constant). Totals: `N_max = 8,084,632,502,538,269` (was `8,084,632,502,538,269`), `time_log2 = 44.10940`, `memory_log2_bytes = 43.18006` (`9,965,327,907,196` bytes: `16,384` bytes of code and static data added for `L`, its constants and stage E), normalized cost `67.28946` (was `67.29417`). This entry is an algorithm (sections 2-4) with a worst-case operation count (sections 6-7) and a success probability derived from the premises `H-ONE` (section 9.1) and `H-NORMAL` (section 9.5), statements about the usable roots of the fixed digest polynomial and its remainder sequences; section 9.2 derives the success probability from them with explicit constants.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and 12 inverse transforms (one per coset, section 3), compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod in the value domain (section 4.6, the method of bradcush 1aa56884) and a half-gcd whose outer steps run the inversion-free half-gcd on three rows of bradcush 4bcabff8 (4.4.2; the last steps the lean form of 1aa56884, 4.4.1), and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39209`: a lower bound for the probability, over the algorithm's fresh random words, that the one centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta + delta_C)^K - K (eps_iso + eps_coin) = q - delta - delta_C - eps_iso - eps_coin` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1: at least `0.3931 p` centres have between 1 and `DMAX = 16` usable roots), `delta = 0.001` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `delta_C < 2^-180.7` the stage-C zero test (proved, 9.2(b)), `eps_iso < 2^-48`, `eps_coin < 2^-128`. The exact value is `0.392099999999997615`. The value of `q` is `0.3934693 - 0.3931 = 0.0003693` below `1 - e^(-1/2) = 0.3934693` (and `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound), the law of the usable roots in section 9.3, which is a theorem for the first two and three S-box layers on the deployed constants (9.3(c)).

* `time_log2 = 44.10940` in target-compression units (`C(10) = 426` primitive operations per unit): the worst-case operation count, derived in section 6 as `T_fixed + K * T_trial` with every trial charged in full (stage D for the normal remainder sequence, which bounds every trial because a trial with any other sequence ends after a prefix of that work, section 6.3; stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 8,084,632,502,538,269` operations, `log2(N_max / 426) = 44.1093939987`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is counted exactly, `T_off = 136,785` operations, and charged at its declared cap of 1,000,000 operations; that cap is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 43.18006` (`9,965,327,907,196` bytes: the footprint of `6f1d38c7`, `9,965,327,890,812` bytes, plus `16,384` bytes of code and static data for `L`, its constants and the register-resident stage E, section 7).
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `65` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^16`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against our r = 10 entry `3db5de78` (time + memory penalty 67.42201, the same algorithm and package): one change, the extension of stage C (4.6), the algorithm unchanged. The `K x K` Toeplitz product of the extension (`K = 18`) is formed per position by Karatsuba-type splitting with the fixed kernel (two-way at order 18, three-way at order 9, direct at order 3; the kernel-side sums once per trial) in place of the direct product: 378 operations per position in place of 630 (162 multiplications and 216 additions and subtractions in place of 324 and 306); and the running factors of its inputs and outputs (36 factors, 36 steps) are held in registers over the position loop, 4 operations per element (the access with its address 2, the factor 1, the factor step 1) in place of 8; the kernel holds its 90 constants, the 72 factors and steps and at most 40 live values: 202 of the 256 field registers (4.6). Per position `527` (was `923`); the geometric phase of one extension `2,264,299,208,962` (was `3,964,644,884,738`), one loop step `24,091,637,580,372` / `24,282,763,625,044` for `b = 0` / `b = 1` (was `27,492,328,931,924` / `27,683,454,976,596`). Row C `5,452,281,925,966,666` (was `6,203,834,714,659,050`); row D unchanged; `N_max` `8,084,632,502,538,269` (was `8,862,625,263,380,842`), time_log2 `44.11411` (was `44.24195`); term (a) `16,384` bytes more code for the kernel, memory `9,965,327,890,812` bytes, memory_log2 `43.18006` (unchanged); time + memory penalty `67.29417` (was 67.42201). The 18-register program, the premises, the success bound and the experiments are unchanged.
* Against our r = 10 entry `74b52835` (time + memory penalty 67.75433, the same algorithm and package), with the stage-D apply plans of 0xplemonade's entry `ff21bd28` (credited): (i) the apply of `adj(M)` in each outer step of stage D is a direct whole-pair apply or a fixed-slot apply on one transform size, with four matrix spectra, two operand/output spectra and one pointwise pass, in place of the block products of scheme (c) (no chunk forms, no accumulators; 4.4.2); (ii) the layers of the block-form passes of a row and of a run of stage-C column passes are split into passes of at most seven layers by least charge, in place of seven at a time (4.2); (iii) stage C allocates `R1` at the product for `q` and `R2` before step 2, not at its entry, runs the batch inversion in chunks of `2^16` elements (its auxiliary array `2^16` elements, was `h`), and forms the `omega^i` of the `b = 1` boundary pass from two tables of `2^16` entries (was one table of `h` entries; 4.6); (iv) the ends of the pool taken by the stage-D matrix and apply spectra (4.2). Row C `6,203,834,714,659,050` (was `6,240,900,265,287,956`), row D `2,561,608,653,181,651` (was `3,289,088,417,470,781`); plan_invN misses `98,848` for 32 plan sizes (was `154,450` for 50); `N_max` `8,862,625,263,380,842` (was `9,627,170,578,354,480`), time_log2 `44.24195` (was `44.36133`); the live peak of the trial is now in stage C, `9,964,332,544,704` bytes (was `11,548,601,747,904`, stage D), the arena `9,965,321,867,712` bytes (was `11,550,289,901,184`); term (a) `32,768` bytes more code; memory `9,965,327,874,428` bytes, memory_log2 `43.18006` (was `43.39300`). On an 18-register machine (column passes of at most 3 layers and leaf passes, the same algorithm) the count is at most `12,213,841,860,367,842` (time + memory penalty at most 67.88472). The premises, the success bound and the experiments are unchanged.
* Against our r = 10 entry `149cc898` (time + memory penalty 67.76710, the same algorithm and package): two block-form changes and one column-kernel change (4.2), the algorithm unchanged. Group 0 of each block-form pass runs a variant without the multiplications by twiddle 1 (`2^k - 1` butterflies per block at 2 operations, 3 control operations more per pass); the block loop of a group is written four blocks per pass (3 of control per block, was 5); the position loop of the stage-C column kernels `ob4` to `ob128`, `ob4m` and the boundary kernels is written four positions per pass (loop step 2 per position, was 3). Row C `6,240,900,265,287,956` (was `6,269,977,083,960,614`), row D `3,289,088,417,470,781` (was `3,345,580,304,248,561`); plan_invN misses `154,450` for 50 plan sizes (was `157,539` for 51); `N_max` `9,627,170,578,354,480` (was `9,712,739,283,808,007`), time_log2 `44.36133` (was `44.37410`); the arena `11,550,289,901,184` bytes (was `11,550,298,289,792`; the allocator run of 7(b) on the new allocation sequence); term (a) `645,008` bytes more code, term (e) the offline working set (7); memory_log2 `43.39300`, rounded up at five decimals (`11,550,295,875,132` bytes, was `11,550,303,618,156` and `43.393` at three). Every other charge is unchanged. The success bound takes the `H-NORMAL` allowance `delta = 0.001` (was `0.003`) of our accepted r = 9 entry `5b96dbb5`, with its organizer-run normality entries `euclid-normal-n2-t256-l2-a` to `-f`, `-n3-t24` and `-n4-t2`, and `H-ONE` is organizer-counted by `euclid-gcdpos-n2-t256-a`, `-b` and `euclid-gcdpos-n3-t24` in place of the one-centre entries (9.5, 10.5.1, 10.5.2): `0.392099999999997615` (was `0.390099999999997615`).
* Against our r = 10 entry `df162b2d` (time + memory penalty 68.04476, the same algorithm and package): the register file of the machine is 387 words, 256 field registers of 256 bits plus 131 integer address registers (was 64), counted in the memory (7(d)), as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits: the column passes of stage C take up to seven layers (`ob64`, `ob128`; the outer transforms of stage D keep their passes of up to five layers) and the block-form passes of the products up to seven layers (blocks of 128 points with their 127 twiddles in registers); 4.2; the product step `M = M1 [[Q, 1], [b^2, 0]] M2` of each half-gcd node runs on the two rows `Y - 1`, `Y + 1` (`2n` points) in place of three; its entries have degree at most `2n - 1` on the normal sequence (van der Hoeven, arXiv 2212.12389, Prop. 7; 4.4); the extension of 4.6 (`K = 18`) is the direct `K x K` Toeplitz product per position in registers (54 words), not the group-buffer transforms (4.6). Row C `6,269,977,083,960,614` (was `7,545,320,272,415,400`), row D `3,345,580,304,248,561` (was `4,131,617,227,700,581`); arena `11,550,298,289,792` bytes (was `11,550,299,854,464`), memory_log2 unchanged. Every other charge, the premises and the experiments are unchanged.
* Against our filed r = 10 entry `7eba9197` (time + memory penalty 68.30127, the same algorithm and package), three changes: (i) the outer steps of stage D run bradcush's inversion-free half-gcd on three rows (entry `4bcabff8`, with the transform reuse of `b30de9bf`), as in our r = 3 entry `bcf8e01c`, ported to `r = 10` at the budget `2^j - 1 <= 2^31 - 1` and charged in this cost model (4.4.2), in place of the lean half-gcd calls of `1aa56884` on the whole pair; (ii) the top step is such an outer step as well, so `g` and `R` leave stage C as one array each instead of two pieces (4.4.1 item 5 and lemma 4.8(b) are no longer used, and the piece selection of 4.6 is gone); (iii) stage C starts from `S^v` with `v = 2^33` (`VSHIFT = 3`, was `2^34`): one more squaring step and a shorter Newton reciprocal (`ell = 9,605,400,609`, was `18,195,335,201`), which lowers the live peak of stage C below that of stage D (section 7). Row C `7,545,320,272,415,400` (was `7,540,491,423,345,042`), row D `4,131,617,227,700,581` (was `5,604,354,524,296,783`); plan sizes 51 (was 36); arena `11,550,299,854,464` bytes (was `12,262,380,160,640`), memory_log2 43.393 (was 43.480; the peak is now in stage D, section 7). Every other charge, the premises and the experiments are unchanged.
* Earlier entries: `7eba9197` is our r = 10 entry `bf3439e4` with the transform passes of the products in the block form of our r = 3 entries `ef123c2b` / `253629b9` and the column kernels `ob16` / `ob32` of stage D (`a6f13c58`), and the loads and stores of the block-form passes charged one operation each, base plus index (the wording of the accepted `89b451ff` and `070a02b2`).
* Prior entry: this entry is the r = 10 version of our r = 7 algebraic entry 05a41d88 (the same algorithm, ledger method and evidence design; the premises here are `H-ONE` and `H-NORMAL`). The ruling on 05a41d88 (not_evaluable on the experiments lane) is answered here in the same way: the organizer experiments `line-ladder-w6`, `-w8`, `-w10` and `-w12` on the antipodal line pairs of this construction at r = 10 (10.2), the computations of Grok job 136 and their re-run on the deployed constants and the construction's line (10.3), and the measurement of the Euclidean sequences on the sibling targets (10.5). Stage C is the value-domain powering of bradcush's entry 1aa56884 (section 4.6), stage D its lean half-gcd (4.4.1) with the outer steps on bradcush's inversion-free half-gcd on three rows (4bcabff8, 4.4.2), and stage D is charged for the normal remainder sequence under the premise `H-NORMAL` of bradcush (entries e6dcb600, 1aa56884) with gta6rp's allowance and organizer-run tests (9.5); all credited in the dependencies and the note.
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1) and `H-NORMAL` (score-critical for the success probability only, section 9.5). Both are statements about probability. `H-NORMAL` is bradcush's premise (entries e6dcb600 and 1aa56884), stated here with the allowance `delta = 0.001` (that of our accepted r = 9 entry `5b96dbb5`; the split of the success allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`) and supported by organizer-run normality tests, the recipe of gta6rp's entries (fe269c23); `H-ONE` is organizer-counted by the good-centre tests (10.5.2); the test program `experiments/exp_euclid.py` is our own (10.5.1). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2 on the machine stated as a restriction in claim.json (256 field registers of 256 bits plus 131 integer address registers; every load, store and spill counted), as the accepted entries `89b451ff` and `fb176310` state theirs and as our r = 3 entries `ef123c2b` and `253629b9` do, and the base-plus-index addressing of the stage-C column kernels (4.2), stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation. Everything else is proved or counted here: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the success bound (section 9.2), the stage-C zero-test bound (9.2(b)), the isolation lemma (section 9.4), the uniformity of the centre, the cap rules and every operation count (sections 4, 6, 7).
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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 (partial), 60, 61, 62, 63 (full) put sixteen S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^16 = D = 152,587,890,625`. The leading coefficient is obtained by
propagating leading coefficients through the sixteen layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x17599b3e1f896e6cec97db7882869a7227b0664565956716aded25bb1f47a0f3`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
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
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 40 bits after the leading one are zero, so the algorithm starts from the monomial `S^v` with `v = 2^33` (a multiple of h below m, 4.6, `VSHIFT = 3`; 33 + 220 = 253), and the loop of stage C has 220 steps, of which 45 also multiply by `S` (pointwise).

Stopping rule. The loop bound `K = 1` is a constant of the algorithm: one centre is tried. A trial is run to its end, or to an ABORT of stage D on an abnormal remainder sequence (6.3) or of stage C on a zero of g on O1 (4.6 step 5), which then resets the allocator and draws the next centre; the claim charges every trial at its maximum (stages E to G at their worst case, section 6), so a trial that fails early is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3, 4.4), the powering has a fixed number of steps, and the half-gcd has a fixed recursion: 30 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 38,146,972,656` and is halved, rounded up, until it is at most 96) and at most 30 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 76,293,945,312 to at most 192). Hence, with stage D charged for the normal remainder sequence and every other sequence ending its trial after a prefix of that work (section 6.3), the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success, by an ABORT of a trial (the next centre is then drawn), or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

The only randomness of the algorithm is the cost model's random-word primitive (fresh independent algorithmic coins): an independent uniform 256-bit word, each use returning a fresh word, uniform on `0..2^256-1` and independent of everything else, and costing one operation. **Probability space:** every probability of section 9 is over these words. A draw is one fresh word `y`; the draw is `x = y mod p`, computed by at most three steps `if y >= p then y := y - p` (`y < 2^256 < 4p`, so three steps bring `y` below `p`). Write `2^256 = 3p + s0` with `0 < s0 < p`: the residues below `s0` have exactly four preimages below `2^256` and the other `S3 = p - s0 = 4p - 2^256` residues have exactly three, so `P[x = z] = 4/2^256` or `3/2^256` for every residue `z`, every residue has probability at least `3/2^256`, and all but `S3` residues have probability `4/2^256`. The draw is within statistical distance `S3 (1/p - 3/2^256) = 1.574e-39 (2^-128.90) < 2^-128` of uniform on `F_p`. A draw costs 31 operations: for the word one random-word operation, one load, one store into the cell `y` and three control operations (two addresses, the increment of the word index), 6 in all; for the reduction three steps each of a comparison, a conditional branch and a field subtraction (9 operations), with the loop control of 3 per iteration and 2 on exit (11); one Montgomery conversion of `x` (1); the entry of the call (2) and the address of `y` (2). Draws are made once per trial for the centre and once per isolation round for the shift: at most `K (1 + Z) = 65` draws, `65` words. No word is used twice, and the number of words used before a draw depends only on earlier words, so each draw is independent of the earlier course of the algorithm.

#### 4.1.2 Stage E: isolating a root of G

`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). The roots `r` of `G` are the usable `S`. While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw `a` (a draw as in 4.1.1; if it is 0, `a := 1`, since the Taylor shift uses `1/a`; the zero test is 5 operations and the replacement 2, charged in every round), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds.

### 4.2 Machine model and charging rules

Every operation of the algorithm is counted where it executes; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation). Exception, the stage-C column kernels `ob4`, `ob8`, `ob16`, `ob32`, `ob64`, `ob128`, `ob4m` and the two boundary passes of the loop (4.6): each load or store is 1 operation with no address operation. An element of the call's block at the position `j` is addressed as row base plus position offset, and a twiddle or spectrum word of the call as the table base plus the call's index scaled by a constant of the layer, the base-plus-index addressing of the load itself; the `2^k` row bases and the twiddle address are formed once per call (in the call charge `2 * 2^k + 6`) and held in integer registers, and the position offset advances with the index update of the loop step. Everywhere else (stage D, the `ob2` and `ob3` passes and the first and last passes of an extension of stage C included) the address operation is charged as above.
* every loop: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). Loops over the elements of an array written eight elements per pass (the pointwise, copy, fold and subtraction loops of the powering and of the products) are charged 3 per pass of eight, 1 for the bound, 2 when the main loop is left, and 3 per iteration for the remaining 0 to 7 elements.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, comparison, conditional branch, assignment of a register, and the selection of an element of the register block (16 data words) by a computed index. Data-dependent tests are charged per executed test.
* index arithmetic uses only shifts, additions, subtractions, comparisons and branches (the benchmark's primitive list has no integer multiplication, division or modulo): a multiplication by a power of two is a shift, by 3 or 5 a shift and an addition, and a product of an index and a stride is a running sum; each is charged as a control operation where it occurs.
* transforms: a transform of size `3 * 2^a` is a twiddle-free radix-3 stage (8 operations per leaf) followed by three rows of radix-2 passes of at most seven layers (the `L` layers of a run of block-form passes on a row of `2^a` points are cut into passes of at most seven layers by the split of least charge: of all sequences `k_1, ..., k_r` with `k_i <= 7` and sum `L`, pass `i` starting at layer `l = k_1 + ... + k_(i-1)`, the one with the least sum over its passes of `2 (2^(a-k) blk(k) + 2^l grp(k) + 9k + 2 - (2^k - 1) 2^(a-k-l) + 3) + 35`, the forward and inverse charges of a pass of this bullet with `blk(k) = 2^(k+1) + 3k 2^(k-1) + 3` per block and `grp(k)` per group; a dynamic program over the layer boundaries, a constant of the algorithm for each `(a, L)`, the inverse run using the same split in reverse). A pass works on blocks of `2^k <= 128` points held in registers. The passes of the transforms of the products of stages C and D (and of the transforms of the evaluation of `g` and of the kernel spectra of 4.6) run in the block form of our r = 3 entries `ef123c2b` and `253629b9` (their `pd_fwdp`, `pd_invp`): per block its `2^k` loads and `2^k` stores (1 each: a block element is addressed as the table base plus its index, the base-plus-index addressing of the load or store itself, as for `ob4` to `ob128` above; one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`), `k 2^(k-1)` butterflies at three field operations each (two in group 0 where the twiddle is 1, below) and 3 of control (the block loop of a group is written four blocks per pass: per block 2 operations that form its addresses and per pass of four blocks 3 of loop control, `2 + 3/4 <= 3`; a group of one or two blocks runs them in line, with no loop); per group its `2^k - 1` twiddles formed and held in registers for all its blocks (24 operations for `k = 4`: two loads with their addresses, one multiplication, three squarings, eleven multiplications by register constants and control; 16 for `k <= 3`; for `k = 5, 6, 7` its `2^k - 1` twiddles loaded from the twiddle table, 1 each (base plus index), with 9 operations of address formation and control, `2^k + 8`: 40, 72, 136); per pass `5 + (9k + 2) + 12` (forward) or `6 + (9k + 2) + 12` (inverse) of pass set-up. Group 0 of a pass (its `2^(a-k-l0)` blocks for a pass of `k` layers from layer `l0` of a row of `2^a` points) runs a variant of the block body without the multiplications by its twiddle 1: in the pass layer with `2^j` distinct group twiddles (`j = 0..k-1`) the twiddle of group 0 is 1 on `2^(k-1-j)` of the `2^(k-1)` butterflies of a block, `2^k - 1` per block, each its addition and subtraction, 2 operations (the convention of the last pass of a product, below: none for the multiplication when the twiddle is 1); the variant adds 3 control operations per pass. The inverse transforms of stage B and the fused pass of a product (its last forward layers, the pointwise product and its first inverse layers) are leaf passes: each butterfly is three field operations (none for the multiplication when the twiddle is 1), each twiddle is one load with its address operation (the first twiddle of a layer also 2 operations of address formation), and the group and block loops around a block are charged 3 per iteration and 2 on exit. The register file is the machine restriction of claim.json: one register file of 387 words, 256 field registers of 256 bits plus 131 integer (address) registers (as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits), counted in the memory (7(d)) (a block-form pass uses at most 256: 128 data words, 127 twiddles and the butterfly temporary; the column passes `ob128` of stage C use 256: 128 data words, 127 twiddles and the butterfly temporary, and `ob32` of stage D 64), and the 131 integer registers of the file for a call (at most 128 row bases, the twiddle address, the position offset and the loop bound); every other value is charged as a load or store. Stage C (4.6) and the outer transforms of stage D (4.4.1, item 6) use column kernels: a column pass of `k` radix-2 layers (`k <= 7` in stage C, `k <= 5` in stage D) runs over `2^k` rows at `cnt` positions and keeps its `2^k - 1` twiddles in registers for the whole position loop (`ob128`: 128 data words, 127 twiddles and the butterfly temporary, the 256 field registers; `ob64`: 64 + 63 + 1; `ob32`: 32 + 31 + 1; `ob16`: 16 + 15 + 1; `ob8`: 8 + 7 + 1; `ob4`: 4 + 3 + 1). Per position it loads `2^k` elements, makes `k 2^(k-1)` butterflies at 3 operations each (also where the twiddle is 1) and stores `2^k` elements, plus the loop step: 3 in stage D, and 2 in the stage-C kernels `ob4` to `ob128`, `ob4m` and the two boundary passes, whose position loop is written four positions per pass (per position 1 for the offset update and per pass of four positions 3 of loop control, `1 + 3/4 <= 2`; up to three remaining positions run in line); each load or store is 2 with its address operation in stage D and 1 in stage C (base-plus-index, above). Charges: stage C `ob128` `269 + 1602 cnt`, `ob64` `139 + 706 cnt` (per call their 127 or 63 twiddles loaded at 2 each with the address operation, 3 of control and 2 per layer after the first: `269 = 254 + 3 + 12`, `139 = 126 + 3 + 10`; per position `1602 = 256 + 1344 + 2`, `706 = 128 + 576 + 2`), `ob32` `34 + 306 cnt`, `ob16` `18 + 130 cnt`, `ob8` `10 + 54 cnt`, `ob4` `6 + 22 cnt` (a run of `L` layers is cut into passes of at most seven layers by the split of least charge, a dynamic program over the layer boundaries on the charges above at the run's row count and positions, a constant of the algorithm for each run); stage D, with the block addresses of the call, `ob32` `74 + 371 cnt`, `ob16` `42 + 163 cnt`, `ob8` `26 + 71 cnt`, `ob4` `18 + 31 cnt`, `ob2` `14 + 14 cnt`, `ob3` `16 + 23 cnt` (the register-blocked outer kernels of bradcush 1aa56884, credited, extended to 16 and 32 rows on the 256 field registers of the register file; a run of `L` layers is one pass of `L mod 5` layers, if any, then `floor(L/5)` `ob32` passes). The 256-bit constants of the radix-3 stage are loaded at every use.
* random words: the cost model's random-word primitive (an independent uniform 256-bit word) is one operation per word. The word of a draw is also loaded, stored into the cell `y` of the draw and addressed (one load, one store and three control operations), 6. A draw is that word (6), the reduction modulo `p` (three steps each of a comparison, a conditional branch and a field subtraction, 9, with the loop control of three iterations, 11), the conversion of the result to the internal representation (1), the entry (2) and the address of `y` (2): 31 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: 426 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation: every array is taken from one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes (`need` bytes), and `need` decides the allocator. A block of more than 2^26 = 67,108,864 bytes comes from the pool, one region with two ends: its blocks follow each other in address order, each with a header (size, size of the previous block, in-use flag), no two free blocks are adjacent, and the unused middle between the two ends is one free block. Each allocation statement of the program uses one end of the pool, a constant of the statement: the statements (`g` of stage A, the block array of stage B, `MU` and `Y`, the work arrays of the Newton products, of a squaring step (in a chunked product of a squaring step, all its arrays except the accumulators of the square `R^2`, which use the low end) and of a shift, and the results inside the half-gcd: the quotient and remainder of a node and of the outer loop, the outputs of apply_inv, of the matrix products and of mul_add_q2, every allocation of the lean stage D (`ld_new`, all sites `# pool:H`, including the working arrays of its block products), and the reversed `g` and the operand rev(X^v P1) of stage C step 1 (4.6)) use the high end, every other statement the low end, except that the copies of the remainders returned by a node that applies its second matrix (4.4, step (6)) are taken from the low end. In stage D the coefficient matrix of an outer step (4.4.2) and the two operand/output spectra of its apply use the high end, and its four matrix spectra the low end. A low request walks the blocks upward from the bottom of the pool, a high request downward from the top (the two sizes in the header give both neighbours, so the two walks are the same code mirrored); it takes the first free block with at least `need` bytes (the unused middle is the last block of either walk) and cuts the block from the side nearest its own end, and the rest stays a free block when it is at least 128 bytes (else it belongs to the block); a free merges the block with a free neighbour on either side, the unused middle included, the same code for both ends. Since no two free blocks are adjacent and a walk ends at the middle, a walk examines at most 2 P + 1 blocks, P the live blocks on its side of the pool, and one block examined is 13 operations (two comparisons with branches, two loads, the advance). A block of at most 2^26 bytes comes from the slab classes: the class `j` is the least `j >= 7` with `2^j >= need`, a slot is `2^j` bytes; a request takes the first slot of the free list of its class, else a new slot from the end of the slab area, and writes the class and the in-use flag into the header; a free puts the slot on the free list of its class. The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows: a request of the pool 97 operations besides the walk (the statement that calls the allocator, the set-up, the split, the header stores, and a flat 64 for the statistics) and 13 per block examined, a request of a slab class at most `126` (the statement that calls the allocator, the class `j` by a binary search over 7..63 in 6 steps of 6 operations, the pop or the bump, the two header stores, and a flat 64 for the statistics), a free 81 for a slab block and at most 105 for a pool block (a free tests the size of the block to choose the allocator, in place of the test for a null pointer, which the program never needs). Every allocation of the walk is charged `1 + 120 + 13 (2 L + 1)` with L the live blocks at that point, which covers the pool (P <= L, the 97 operations and 13 per block examined) and the slab path (at most `126 <= 1 + 120 + 13` operations), and every free 105 (550 per allocation and 105 per free at 16 live blocks in stage E). The memory of both allocators is the arena of section 7.
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
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: one outer step, which is the inversion-free half-gcd of 4.4.2 on the top window with its matrix applied to the whole pair while `(n - 1)/2 >= 127`, and `(c, d) = hgcd(a, b, floor((n+1)/2))` below, then one division `c = q d + e` and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). With `H-NORMAL` (9.5) stage D runs the normal-sequence procedure of bradcush (entry e6dcb600): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter ; a zero remainder met inside hgcd or in the division of the outer loop also ends the trial (ABORT); on any other case the trial ends (ABORT) and the next centre is drawn (section 6.3).

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

#### 4.4.1 The lean stage D (this entry; the stage D of bradcush 1aa56884, its section 4.4 and lemmas 4.4 and 4.8, credited)

This entry runs the half-gcd above (its last outer step, 4.4.2) with the changes below, all from 1aa56884 (credited in the dependencies and the note), charged by this model's rules of 4.2 and 4.5. They change where arrays live and which coefficients are formed, never a quotient: every quotient used is a quotient of the whole pair (lemma 4.4 above, and lemma 4.8 below).

1. *The base case in place.* For `k <= 96` the two remainders are two arrays and a division step with a quotient of two coefficients is one pass `r_k = a_k - q0 b_k - q1 b_(k-1)` written over the array of `a`; the roles of the two arrays swap. The four matrix entries are four arrays of `k + 2` elements allocated once, and `R := R Q` writes `r11 q + r12` over `r12`. No array is allocated or freed inside the loop.
2. *Matrix-only calls.* A call returns the reduced pair only when its caller wants it: the calls of the Euclid driver `poly_gcd_own` and, inside them, the second calls with `s3 <= 0`. Every call inside a first call, and every truncated second call, returns its matrix only.
3. *Windows.* In a node that wants its matrix only and has `s3 > 0`, the block products of `apply_inv` form only the top window of `c` and `d`: the coefficients of degree at least `s3 - 1` (lemma 4.8 (a)). Such a node tests that the coefficients of `c` and `d` at their normal leading degrees `la - h - 1` and `la - h - 2` are nonzero (2 tests, charged) and ABORTs otherwise, so it never reports a shorter remainder from a window.
4. *The two tests and the ABORT.* At every division the quotient test (the quotient has degree 1) and after every recursive call and every call of `poly_gcd_own` the return test (the call returned exactly its parameter as degree count; a zero remainder inside hgcd or in the outer-loop division also ABORTs), 2 operations each, charged wherever they execute. If a test fails the trial ABORTs: the allocator is reset to its state after initialisation (`1,000` operations, charged in section 6) and the next centre is drawn. On the normal remainder sequence neither test fails (6.3), so every division of stage D is the one-pass division by a quotient of two coefficients and the Newton division is never run.
5. *No pieces.* 1aa56884's top node on two pieces of `g` and `R` is not used: stage C leaves `g` and `R` as one array each, and the first step of `poly_gcd_own` is an outer step of 4.4.2 like the others.
6. *Block products of stage D.* Each product of apply_inv and of mat_mul of the lean half-gcd (repetition 73 of 11.2; the apply of an outer step is that of 4.4.2) uses the cheaper of the single transform and scheme (c) at the block length 2^b of least charge (b = 6..31, transforms of 2^(b+1) points); scheme (a) of 4.5 is not used in stage D. The number of chunks is the least power of two that brings a chunk form to at most `m // 8` elements. The outputs are allocated first at their true lengths, the chunks accumulate into them, the working arrays follow and are freed at the end, and the operands are freed after the last chunk. This replaces, for stage D, the Blocks, Choice, stage-D and Scaling bullets of 4.5. There is no placement pass in stage D: each output of a scheme (c) product is untwisted straight into its window with the scaled weight `sign / (NB n2) * w^(-e)` (the sign of the output, the factor `1/NB` of the unnormalised inverse transform and `1/n2` of the outer transform applied here), charged 15 operations per product (the scale and the weight base), 7 per untwist call (load the table entry, load the scale, multiply, store) and the chunk and outer-point loops; at r = 10 this is 181 operations per trial (2 products, 10 untwist calls), included in row D. The outer transforms of scheme (c) use the column kernels of 4.2 (`ob128`, `ob64`, `ob32`, `ob16`, `ob8`, `ob4`, `ob2` across the outer points, `ob3` for the radix-3 stage), and the assembly of a chunk, the untwist into the window and the fold of an outer point into the row of its chunk are loops of eight elements per pass (4.2): the assembly 4 per element written (5 after the first chunk, where the twist is applied), 7 (8) per element added, 2 per element zeroed and 10 per row; the untwist 5 per element in the first chunk and 8 in the others, 13 per piece; the row fold 8 per element and 4 per row (the conventions of 1aa56884 for these four primitives, credited). The kernels `ocp`, `oax` and `ozf` of 4.5 are not used in stage D. The choice between the single transform and the block products counts every charge of each path, including the allocations and frees the block path adds.

**Lemma 4.8 (windows; 1aa56884's lemma 4.8 (a)).** (a) In a node that wants its matrix only, with `s3 > 0`, the rest of the node reads `c` only at degrees at least `s3` and `d` only at degrees at least `s3 - 1`.
*Proof.* (a) The stopping test and the quotient test use `deg c` and `deg d`; the quotient `q = q1 x + q0` uses the top two coefficients of `c` and of `d`; and `e_i = c_i - q0 d_i - q1 d_(i-1)`. The second call reads only `d quo x^s3` and `e quo x^s3`, that is `d_i` and `e_i` for `i >= s3`, hence `c_i` for `i >= s3` and `d_i` for `i >= s3 - 1`. After it the node needs only `R1`, `q` and `R2` (and `s3 - 1 <= deg d - 1`, so the top two coefficients are inside the window). QED

The charges of these steps are this model's (4.2, 4.5), not 1aa56884's: with 1aa56884's own conventions the same walk gives its published row D to the unit (`1,062,106,645,154,198,605,714,641` at r = 21, recomputed in our model with their conventions switched on), and with this model's primitives, with 1aa56884's conventions for the four primitives of item 6, it gives row D of section 6.

#### 4.4.2 The outer steps: the inversion-free half-gcd on three rows (bradcush `4bcabff8`)

Each outer step of `poly_gcd_own` with `(n - 1)/2 >= 127` runs bradcush's inversion-free half-gcd (entry `4bcabff8`, with the transform reuse of `b30de9bf`; read as text only, ported and charged in this cost model as in our r = 3 entry `bcf8e01c`). Matrices and remainders are kept up to nonzero scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside the recursion; the gcd is the same up to a scalar and is made monic at the end. A node of budget `k = 2^j - 1` makes two child calls of budget `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a power-of-two transform of `n` points in the block form of 4.2 after a twist, joined by a 3-row CRT for `(c, d) = adj(M1)(a, b)` on the top window; then the pseudo-division and the product `M = M1 [[Q, 1], [b^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and the scale of a step is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the row `Y - 1` values of each child's matrix are returned by the child, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The twists use roots of order `2n` and `4n` (`4n <= 2^32` divides `p - 1`, so `j <= 31`), from the squaring chain of the running twiddle factors of the row transform (4.2); the scales `1/2^a` (`a <= 30`) are a table of 31 words built at the entry of stage D (`1/2 = (p + 1)/2` an immediate, 29 multiplications). The base case (budget 63) runs two remainder steps per pass over its window. An outer step calls the node on the top window of the pair with `k = 2^j - 1` the largest with `k <= min(2^31 - 1, (n - 1)/2)` and applies `adj(M)` to the whole pair in place (the apply below), then makes one division with the quotient test; once `(n - 1)/2 < 127` the outer step is the lean `hgcd` of 4.4 and 4.4.1, and below degree `192` classical division steps finish. The working arrays of a node live in one bump arena (an allocation or release is 10 operations) of `1,099,511,619,584` bytes at `j = 31`, the peak of its recursion, released before the apply (section 7: the live peak of stage D is `7,490,422,965,888` bytes, below that of stage C, `9,964,332,544,704`). On the normal sequence every length, budget and allocation is a function of `m` alone. Every division and pseudo-division tests that its quotient has degree 1 and every node tests on return that it removed exactly its budget (2 operations each), a zero remainder also ends the trial, and on any other case the trial ABORTs (6.3). The repetitions are listed in 11.2.

**The apply of an outer step** (the direct whole-pair and fixed-slot apply plans of 0xplemonade's entry `ff21bd28`, read as text, re-implemented and charged in this cost model). With `h = 2^j - 1`, `(c, d) = adj(M)(a, b)`, `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, has `lc = la - h` and `lc - 1` coefficients (the high coefficients cancel, 4.4). The apply uses one transform size `N = 3 * 2^e` (`e <= 32`) and one of two forms; both forms are priced at every `e = 2, 3, ...` up to the first with `N >= lc` (8 control operations and the plan set-up per size) and the cheaper is run; 80 operations of entry, 448 for the plan scale (4.4.1) and 22 for the two length checks. A transform of an array of `l <= N` coefficients is `6` plus the radix-3 input stage over the `l` coefficients plus three rows of block-form passes (4.2); an inverse is `3` plus three rows of inverse passes plus the radix-3 output stage over the coefficients formed; the scaling by `s/N` of `t` outputs into their array is `8t + 5` (a load, a multiplication, a store and the loop step per coefficient). Both forms first transform the four entries (`h + 1`, `h`, `h`, `h - 1` coefficients) into four spectra of `N` points and free the coefficient matrix.
(i) Direct whole-pair (`N >= lc`): `a` and `b` are folded in place modulo `X^N - 1` (10 per coefficient beyond `N`: two loads, the addition, the store, the loop step) and transformed into the operand spectra `A` and `B`; one pass over the `N` points forms `C = r22 A - r12 B` over `A` and `D = r11 B - r21 A` over `B` (per point six loads with their address operations, four multiplications, a subtraction and an addition, and the two stores at the addresses of the loads of `A` and `B`: 20; the eight-element loop of 4.2, `2 + for8(N)`); the two inverses form the first `lc` and `lc - 1` coefficients and the scaled outputs are written over `a` and `b`. Since `deg c, deg d < lc <= N` the cyclic results are exact.
(ii) Fixed-slot (`B = N - h > 0`): the outputs are cut into `nb = ceil(lc / B)` blocks of `B` coefficients, handled from the highest to the lowest (`3 nb + 6` of loop control). Block `i` transforms the windows `[max(0, iB - h), min((i + 1) B, lc))` of `a` and of `b` (at most `N` coefficients) into `A` and `B`, forms `C` and `D` in one pass over the `N` points (charged 24 per point: six loads and two stores with their address operations, four multiplications, a subtraction and an addition, 22; `2 + for8(N)`), inverse transforms both (all `N` outputs; block 0 only its outputs) and writes the scaled outputs of the block over the same positions of `a` and `b`; 20 of control per block. A window of `w <= N` coefficients times an entry of at most `h + 1` gives at most `w + h` coefficients, so the cyclic wrap of length `N` reaches only positions below `w + h - N <= h`: block `i > 0` keeps the positions `h .. N - 1`, which are exact, and block 0 (`w <= B`) has no wrap. The order is safe: block `i` writes positions `[iB, (i + 1) B)` of `a` and `b`, and the blocks after it read only positions below `iB`.
Memory of an apply: the four matrix spectra and the two operand/output spectra, six arrays of `N` words, besides the pair; no chunk form, accumulator or output array. At r = 10 the outer steps run 30 fixed-slot and 42 direct applies (11.2).

### 4.5 Products longer than `3 * 2^32` points (block mode)

The bullets of earlier entries on the coefficient-domain stage C are not repeated: stage C is 4.6, which uses this section only for the Newton reciprocal and the q product of its step 1. Stage D uses 4.4.1 item 6.

At this r the transforms of 4.3 and 4.4 would have up to `3 * 2^36` points (the square of stage C, `2m - 1 = 152,587,890,623` coefficients) and `3 * 2^35` points (`m + 1`, the products by `g`, and the products by the half-gcd matrices, whose entries have several blocks). The field has no root of unity of such an order (`p - 1 = 2^32 * 3 * q'`). Grok (xAI), job 140, determined the cost of multiplying polynomials of lengths `3 * 2^34`, `3 * 2^36` and `3 * 2^38` over this field and recommends the block NTT (its scheme (a)) for `3 * 2^34` and `3 * 2^36` and the same split with an outer transform across the blocks (its scheme (b), the outer FFT) for `3 * 2^38`: a product is cut into blocks, the blocks are transformed with the longest available transform, and the products of block spectra are summed in the transform domain. Grok job 140 checked both schemes against schoolbook on random products of length `2^14` with a transform cap of `2^10` (every coefficient equal, and the counted multiplications and additions equal to its formulas, `551,999` and `890,850` for scheme (a)). Both schemes are the same operations at every block count; at the lengths of this r we apply them by the charging rules of 4.2. The schemes, as used by the algorithm:

* Blocks. `B = 3 * 2^31` coefficients per block, transform size `NB = 2B = 3 * 2^32 = 12,884,901,888` (the plan of the largest transform of 4.3, with its kernels and charges). An operand of `l` coefficients has `ceil(l / B)` blocks; each block is zero-padded to `NB` points and transformed once (forward: the radix-3 stage and three rows of radix-2 passes). A product of two blocks has at most `2B - 1 < NB` coefficients, so a block product does not wrap.
* Scheme (a), slots. The slot `s` of a product `A C` is the sum of the block products `A_i C_j` with `i + j = s`; it is formed pointwise in the transform domain (`NB` multiplications per pair, additions or subtractions for the further pairs), inverse transformed once, and placed at offset `s B` of the output: a loop with a load, the multiplication by `1/NB` (and the sign), a store, and for the coefficients that overlap the previous slot a load of the output value and an addition (a subtraction when the placement subtracts into an array). Only the slots that meet the wanted window of the product are formed. The windows are those of 4.3: the Newton products use `[0, l2)`; the quotient `q` of a step is the window `[m - 2, 2m - 3)` of `T1 * MU`; the remainder uses the window `[0, m)` of `q g`.
* Scheme (b), outer transform (the scheme from which (c) below is derived; it is not used at this r). Let `ns` be the number of slots of the product, `[s0, s1]` the slots that meet the window, and `n2` the smallest `2^a` or `3 * 2^a` that is at least `max(s1 + 2, ns + 1 - s0)` (it divides `3 * 2^32`, so the roots exist). For every position `t < B` the `n2` values of the blocks of an operand at that position (zero beyond its last block) are transformed with the `n2`-point transform across the blocks (twiddles: powers of a primitive `n2`-th root of unity); this gives, for each of the `n2` outer points `o`, a polynomial of `B` coefficients, which is transformed with the block transform (`NB` points). For each outer point the spectra are multiplied pointwise (and summed over the products of the bilinear form), the result is inverse transformed, and its upper part (positions `B ..`) is multiplied by the `o`-th power of the outer root and added to the lower part (the fold). The inverse `n2`-point transform across the outer points returns, for each position `t`, the coefficients of the pieces of the product; the cyclic wrap of length `n2` does not reach the pieces of the window. The window is placed with the scaling `1/NB` and `1/n2`. Price of the outer transform (exact, from its kernels): a transform of `n2` points at each of the `B` positions of a block is a twiddle table of `n2` entries (3 operations each), `n2/3` calls of the radix-3 kernel `ob3` when `3` divides `n2`, and `n2/2` calls of the radix-2 kernel `ob2` in each of the `log2` radix-2 layers; a call of `ob3` is charged `7 + 24 B` and a call of `ob2` `5 + 13 B` (every load, store, field operation and loop step of the kernel text in `ntt_kern.h`, parsed like every other kernel), plus 10 for the call (block addresses, twiddle address, call and return). The charges are integers; nothing is averaged or truncated.
* Forms. The form of an operand of `l` coefficients is what a product multiplies pointwise. In scheme (a) it is the `ceil(l / B)` block spectra of `NB` points each (`ceil(l / B) * NB` elements). In scheme (b), when `l > B`, it is the `n2` outer-domain arrays of `B` elements each (`n2 * B` elements): the blocks are copied into one array of `n2` blocks, zero beyond the last block (the copy is charged, `7 l + 2` operations, and so is the zero fill of the other `n2 B - l` positions, `5 (n2 B - l) + 2` operations, because the form is taken from the pool, whose memory holds the data of earlier arrays), and transformed across the blocks; when `l <= B` the form is the one spectrum of `NB` points. A form is made from the coefficient array of the operand and charged as in 4.2 (each block transform, or the copy and the outer transform); the coefficient array is freed as soon as the form exists whenever the operand is not needed again. In scheme (b) the inner transform of an outer point is made when that point is multiplied, into a working array of `NB` points, and the output of an outer point overwrites a dead operand array of that point (a further outer-domain array is allocated only if the product has more outputs than operand forms of more than one block). The working arrays of a product are allocated at its start and freed at its end: in scheme (a) one accumulator of `NB` elements; in scheme (b) one array of `NB` elements for each operand and each output of the product.
* Stage D, products above one block. The entries of the half-gcd matrices and the operands `a`, `b` of `apply_inv` have several blocks at the top levels of the recursion. `apply_inv` forms `c = r22 a - r12 b` and `d = r11 b - r21 a`, a bilinear form with two outputs, each the sum of two products. The forms of the four entries are made first; when the matrix is not needed again, the coefficient array of an entry is freed as soon as it is transformed. The blocks of `a` and `b` are transformed one at a time as the slots advance and pass through a sliding window of `kR + 1` blocks for each of the two operands (`kR` is the largest number of blocks of an entry): a slot meets at most `kR` consecutive blocks of an operand, and the block after the slot is transformed before the slot is placed; a block that leaves the window is freed, and every block is transformed once, as the cost counts it. The slots are formed in order, each with the accumulator, inverse transformed and placed. The outputs `c` and `d` are written over `a` and `b` when those arrays belong to the node and have `nres` elements (the placement of slot `s` writes the blocks `s` and `s + 1` of the output, which are already transformed), otherwise into arrays of `nres` elements of their own. In scheme (b) the forms of the four entries and of `a` and `b` (outer-domain arrays; the outputs of the outer points overwrite the forms of `a` and `b`) and the working arrays are held together while the outer points are multiplied, and then freed; the outputs are written over `a` and `b` or into arrays of their own as above. The exact `c` and `d` have fewer than `nres` coefficients (the high coefficients cancel, 4.4), so slots that start at or beyond `nres` are not formed. The matrix product (`mat_mul`) of the half-gcd is the same bilinear form with four outputs, each the sum of two products. The forms of one factor are held whole and those of the other factor one row (or column) at a time, in whichever of the two orders holds fewer blocks, and each row forms its two outputs into arrays of their own length; the coefficient arrays of both factors are freed as soon as they are transformed. In scheme (b) the forms of all eight entries and the working arrays are held together while the outer points are multiplied; the four outputs are allocated when the operand arrays that are dead have been freed. The Newton division (`divrem_fast`) holds, besides the arrays of its caller, the arrays of the normal sequence (the Newton division is not run on it, 4.4.1 item 4) and the forms and working arrays of its largest block product, in the scheme in which that product is charged. All other products of stage D, and the Newton products below `3 * 2^32` points, are as in 4.3 and 4.4.
* Scheme (c), chunked outer transform (`P` chunks). The outer length `n2` is the one of scheme (b) (the smallest `2^a` or `3 * 2^a` that is at least `max(s1 + 2, ns + 1 - s0)`). If `P` divides `n2` and `Q = n2 / P` is of the form `2^a` or `3 * 2^a`, the outer points `o = j1 + P * j2` (`0 <= j1 < P`, `0 <= j2 < Q`) are handled in `P` chunks, chunk `j1` holding the `Q` points with that `j1`; otherwise the product uses one chunk (`P = 1`). The operands stay in coefficient form: nothing is copied into an outer-domain array. Let `w` be a primitive `n2`-th root of unity and `x_i` the blocks of an operand (`k` of them, `B` positions each; zero beyond `k`). Chunk `j1` is assembled from the blocks: for every `i2 < Q` the array `z_(i2) = sum over i = i2 + Q i1 < k of w^(i j1) x_i`, by one call of the kernel `ocp` (`z = c x`, charge `5 + 7 B`) for the first block of the sum and one call of `oax` (`z += c x`, `5 + 10 B`) for each further block (the last block over its own positions only), the weight `c` being the entry `(i j1) mod n2` of a table of the `n2 + 1` powers of `w` (3 operations per entry, built at the start of the product), and by one call of `ozf` (`z = 0`, `3 + 4 B`) for an `i2` that no block reaches, and for the positions of the last block's array beyond the last coefficient when that block starts its array (the chunk arrays are taken from the pool, whose memory holds the data of earlier arrays); each call is charged `30` more (the two block addresses, the exponent `i j1 mod n2` with the reduction, the table address, call and return). The `Q` arrays are then transformed with the `Q`-point transform across the arrays (root `w^P`; the twiddle table of `Q` entries at 3 operations each, `Q/3` calls of `ob3` when 3 divides `Q`, `Q/2` calls of `ob2` in each radix-2 layer; `ob3` is charged `7 + 24 B`, `ob2` `5 + 13 B`, plus 10 per call), after which array `j2` is `sum over i of w^(i (j1 + P j2)) x_i`, the outer-domain array of the point `o = j1 + P j2`. From there each point is treated as in the outer-transform scheme: the inner transform (`NB` points) of the arrays of its operands (made at every use, charged for every point of every operand of more than one block, including the persistent operands `MU` and `g` of stage C), the pointwise products, the inverse inner transform and the fold of the upper `B` positions with the `o`-th power of `w`. The `Q` folded arrays of the chunk are transformed back with the `Q`-point transform (root `w^(-P)`), and for every output piece `s` of the window (`s = s0 .. min(s1, ns - 1) + 1`, the `tc` pieces) the piece is accumulated, `acc_s += w^(-j1 s) U_(s mod Q)`, by one call of `ocp` in the first chunk and `oax` in the others (charged `1` more per call: the weight is the table entry `n2 - ((j1 s) mod n2)`). The sum over the chunks is the piece `s` multiplied by `n2`; the factor `1/n2` is applied by the placement. A product that is the quotient estimate, the remainder or a stage-C step computes its pieces into accumulators of `tc B` elements and places them into the destination afterwards; a product of a division (6.3) accumulates the pieces of the window directly into the output array of the division, so that it has no accumulator (the calls then run only over the positions of the window). Because the operands are in coefficient form for the whole product, every operand array and every chunk form is charged where it is used; no spectrum or outer-domain form is stored between products.
* Choice. At this r stage C uses `P = 4` chunks (stage D: 4.4.1, item 6): each block product uses scheme (a) or scheme (c), whichever has the smaller charge, as a function of the lengths and the window only; scheme (b) is not used. The number of chunks is a constant of the algorithm for each r, fixed before the run; it was chosen by comparing the scores of the ledger at these pairs (stage C, stage D): (4, 4), (4, 6), (4, 8), (4, 10), (4, 12), (4, 16), (8, 4) and (16, 4). The pair used, (4, 8), has the least score of them (equal to that of (4, 6)).
* Stage D in scheme (c). `apply_inv`: the coefficient arrays of the four entries, of `a` and of `b` stay live while the chunks are processed; the arrays of a chunk are the chunk forms of the six operands, the working arrays, the tables and two accumulators (`c` and `d`). After the last chunk the entries are freed when the matrix is not needed again; `c` and `d` are placed over `a` and `b` when those arrays belong to the node and have `nres` elements, otherwise into arrays of `nres` elements of their own; the accumulators are freed. `mat_mul`: the arrays of both factors stay live during the chunks (chunk forms of the eight entries, working arrays, tables, four accumulators); after the last chunk both factors are freed and the four outputs are placed into arrays of their own length, each accumulator being freed after its output is placed. Divisions: the arrays of 6.3, and the chunk forms, working arrays and tables of the largest block product of the division, the product accumulating its pieces directly into the output array of the division the arrays of the normal sequence (the Newton division is not run on it, 4.4.1 item 4), so that the division has no accumulator.
* Memory in scheme (c). A chunk form is `Q = n2 / P` arrays of `B` elements, so a product holds `Q B` elements for each operand of more than one block (and for each output beyond the number of such operands), where scheme (b) holds `n2 B`; the coefficient arrays of the operands and the accumulators are the other arrays of the product. The memory walk of section 7 allocates and frees every array named here.
* Scaling (coefficient-domain stage C and the products of 4.5; for stage D see 4.4.1 item 6, where the scale is applied at the untwist). The factor `NB` of the unnormalised inverse transform is removed in the placement (one multiplication per coefficient placed); the stored reciprocal `MU` and the polynomial `g` are not rescaled.
* Memory. The arena of section 7 is computed by running the allocator of 4.2 on the allocations and frees of every array named in this section, in the order of the program (a block is `64 + 32 * slots` bytes rounded up to a multiple of 64; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order). For the products in scheme (c) the arrays are those of the two bullets on scheme (c) above. Stage C, products in scheme (a): the twiddle table, `g` and `F`; in the Newton iteration also `MU`, `Y` and the forms and working arrays of the product in progress; in the loop `F` and the persistent forms of `MU` and `g` (`g` itself is freed) and, in a step, the form of `R` (then of `T1`, then of `q`), `T1` (then `q`) and the working arrays of the product in progress, in a shift by `x` the work array of the regeneration of `g`; at the end `g` is regenerated while the persistent form of `g` is still live. Stage D: the arrays of the nodes of the half-gcd, with in `apply_inv` and `mat_mul` the forms, the window and the working arrays described above, and in a division the quotient of two coefficients and the remainder only (6.3: on the normal sequence every quotient has degree 1, so the Newton division never runs). The truncated second call of a node reads the top coefficients of `d` and `e` in place (no array); the second `apply_inv` at the calls of the Euclid driver and the two copies of the returned remainders are counted with the node. In scheme (b) a form is `n2` outer-domain arrays of `B` elements, so the scheme holds `n2 * B` elements for each operand of more than one block. The twiddle table is the one of the transform of `3 * 2^32` points (`2^31` elements, `ntt_init(32)`).
* Cost. The charges are those of 4.2 applied to these operations: each block transform and each inverse transform with the kernels and pass structure of the transform of `3 * 2^32` points, each pointwise product `NB` times the per-point charge of the bilinear form of 4.4, each placement as stated above.

The three kernels of scheme (c), from `ntt_kern.h` (`LD(n)` and `ST(n)` are charged `2 n` operations, `CTL(n)` `n`, `fp_mul` and `fp_add` one each; these are the charges `5 + 7 cnt`, `5 + 10 cnt` and `3 + 4 cnt` of the text above):

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

**Points.** Here `h = 2^32` and `K` is the number of cosets of each point set (not the number of centres of 4.1). `H` is the subgroup of order `h` of `F_p^*`, with generator `omega = 5^((p-1)/h)`, which has order `h` because 5 is a non-square. Put `u_k = 5^k`, `C_k = u_k H` and `n_k = u_k^h = z^k` with `z = 5^h`. `p - 1 = 2^32 * 3 * 463 * q1 * q2` with `q1 = 539,204,044,132,271,846,773` prime, and `z^((p-1)/q1) != 1`, so the order of `z` is at least `q1 > 2K`. Hence the nodes `z^k` (`k < 2K`) are distinct and the cosets `C_k` are pairwise disjoint (`C_j = C_k` if and only if `z^(k-j) = 1`). Our script `zorder_check.py` (standard library) checks these three facts: `q1` is prime by a deterministic Miller-Rabin test with the bases up to 41 (valid for `n < 3.3 * 10^24`), `z^((p-1)/q1) != 1`, and `5^((p-1)/2) != 1`; all three hold. At r = 10: `m = 76,293,945,312`, `K = ceil((m + 1)/h) = 18`, `n1 = K h = 77,309,411,328 = m + 1,015,466,016`. Put `O1 = C_0 u ... u C_(K-1)` and `O2 = C_K u ... u C_(2K-1)`, `M(Y) = prod_(k<K) (Y - z^k)` and `P1(X) = M(X^h)`. `P1` has degree `n1`, is squarefree, has root set exactly `O1`, and on a coset `C_k` with `k >= K` it is the nonzero constant `M(n_k)`.

**Representation.** A polynomial `f` of degree `< n1` is determined by its values on `O1`, and also by its values on `O2`. Write `f = sum_(j<h) X^j F_j(X^h)` with `deg F_j < K`. Then `f mod (X^h - n_k) = sum_j F_j(n_k) X^j`, so the values of `f` on `C_k` are the transform of size `h` of `(u_k^j F_j(n_k))_j`. Each array holds the values coset by coset, in the output order of the inner transform. The inner transforms of the cosets of an array are made together, as column passes across the cosets (position = coset, stride `h`): the 32 layers in column passes of at most seven layers, split by least charge, in place on the array (4.2).

**Lemma 4.6 (the step).** Let `g` be monic of degree `m` with `g(x) != 0` on `O1`. Let `R~` have degree `<= m`, and let `u0` be the polynomial of degree `< n1` with `u0(x) = -R~(x)^2 / g(x)` on `O1`. Then `W = (R~^2 + u0 g) / P1` is a polynomial of degree `<= m - 1`, and `W = R~^2 P1^(-1) mod g`. On `C_k` with `k >= K`, its values are `(R~(x)^2 + u0(x) g(x)) / M(n_k)`. *Proof.* `R~^2 + u0 g` vanishes on the `n1` distinct roots of the squarefree `P1`, so `P1` divides it. Its degree is at most `max(2m, n1 - 1 + m) = n1 + m - 1` because `n1 >= m + 1`, so `deg W <= m - 1`. Modulo `g`, `W P1 = R~^2`, and `P1` is invertible modulo `g` because `g` has no root in `O1`. The values follow from `P1(x) = M(n_k)` on `C_k`. QED. So the invariant `R~_i = S^(e_i) P1 mod g` passes from step to step with `R~' = X^b W` (`e_(i+1) = 2 e_i + b`, `deg R~' <= m`). The same argument with `R~` in place of `R~^2` leaves the Montgomery form (step 7).

**Lemma 4.7 (extension).** Let `f` have degree `< n1`, with its values on `O1` given. The inverse inner transform of each coset gives `h u_k^j F_j(n_k)`. Fix a position `j`, write `F = F_j`, and put `s_i = F(z^i) z^(-i) / M'(z^i)` and `kappa(e) = 1/(z^e - 1)` for `1 <= e <= 2K - 1`. Then `F(z^(K+t)) = M(z^(K+t)) sum_(i<K) s_i kappa(K + t - i)` for `t < K`. *Proof.* `deg F < K`, so `F` is the Lagrange interpolant of its values at the `K` distinct nodes, and `z^(K+t) - z^i = z^i (z^(K+t-i) - 1)` with `1 <= K + t - i <= 2K - 1`. QED. The direction `O2 -> O1` is the same with the nodes `z^(K+i)`. The sum is a cyclic convolution of length `Lx = 3 * 2^4 >= 2K` with a fixed kernel, and no index wraps.

**The stage** (the eight steps of 1aa56884, with our parameters at r = 10). The exponent `E = (p-1)/2` starts from `S^v` with `v = 2^33`, a multiple of `h` below `m` (`VSHIFT = 3`: three more squaring steps and a shorter reciprocal), and runs `220` steps, `45` of them with `b = 1`.
1. *Barrett start:* the reciprocal of the reversed `g` modulo `X^ell`, `ell = 9,605,400,609`, by the Newton iteration of 4.3 with the products of 4.5. Then `q = floor(X^v P1 / g)` by one product (`Kq = 3` rows).
2. *`g` on `O1` and on `O2`* by the chirp evaluation of section 3 (one convolution of length `Le = 2^6 >= 3K - 1` per position) and `2K` forward inner transforms.
3. *`R~_0` on `O2`:* `q` evaluated at the nodes of `O2` (`Lq = 3 * 2^3`), then `R2 := u_k^v M(n_k) - R2 * G2` pointwise. This gives the values of `X^v P1 - q g = X^v P1 mod g`.
4. *`R~_0` on `O1`:* an extension `O2 -> O1` (lemma 4.7).
5. *`-1/g` on `O1`* by Montgomery's batch inversion per coset in chunks of `2^16` elements: per chunk the prefix products into one auxiliary array of `2^16` elements (a load, a multiplication, a store), one inversion with its zero test and the backward pass (two loads, two multiplications, the negation, a store), 9 of chunk control; 20 per coset. A zero prefix product means `g` vanishes on `O1`, and the trial ABORTs as in 4.4.1 item 4 (allocator reset, ledger row 'ABORT reset') after a prefix of the charged work; the probability is below `2^-180.7` (9.2(g)).
6. *The loop*, for each bit `b`: `R1 := R1^2 G1` (`u0` on `O1`); the extension `O1 -> O2`; `R2 := x^b (R2^2 + R1 G2) / M(n_k)`; the extension `O2 -> O1`. By lemma 4.6 the invariant holds after every step.
7. *Leaving the Montgomery form:* `R1 := R1 G1`, the extension `O1 -> O2`, `R2 := (R2 + R1 G2) / M(n_k)`. `R2` now holds `R = S^E mod g` (degree `< m`).
8. *Coefficient form for stage D:* `R2` and `g` are interpolated in place (inverse inner transforms, then two chirp correlations of length `Lx` per position), each into one array of its own (no pieces, 4.4.1 item 5).

**Kernels.** In the loop, the last two forward layers of the inner transforms, the pointwise step and the first two inverse layers are one column pass per boundary: on `O1` (`9 + 46 cnt`) per position 4 loads, 4 butterflies, for each of the 4 elements a load of `G1`, a squaring and a multiplication, 4 inverse butterflies, 4 stores and the loop step of 2; on `O2` (`11 + 63 cnt`, `27 + 72 cnt` for `b = 1`) the same with the load of `1/M(n_k)` and per element the loads of `R2` and `G2`, a squaring, two multiplications and an addition (`b = 1`: the factor `u_k` and two more multiplications per element, and per call the four `omega^e` of its rows, each the product of one entry of each of two tables of `2^16` entries, `omega^e = T1[y] T2[x]` for the position `p = x 2^16 + y` with exponent `e = 2^16 rev16(y) + rev16(x)` in the bit-reversed output order of the inner transform, `T1[y] = omega^(2^16 rev16(y))`, `T2[x] = omega^(rev16(x))`: two loads with their addresses and one multiplication per value, 12 more per call than one load per value from a table of `h` entries), within the 18 words. The extension (`K = 18` cosets: the sum above is, per position, the product `y = T s` of the `18 x 18` Toeplitz matrix `T[t][i] = kappa(K + t - i)` with the vector `s` of the scaled inputs, `s_i = f_i v_i`) is computed directly in registers, position by position (the direct form of the cyclic convolution, here cheaper than the transforms of length `Lx`), and the product with the fixed kernel is formed by splitting (Karatsuba type; the sums of kernel entries below are formed once per trial). *Order 18, two-way:* with `A = T[0..8][0..8] = T[9..17][9..17]`, `B = T[0..8][9..17]` and `C = T[9..17][0..8]` (Toeplitz matrices of order 9) and `s = (s0, s1)`: `P1 = A (s0 + s1)`, `P2 = (B - A) s1`, `P3 = (C - A) s0`, `y0 = P1 + P2`, `y1 = P1 + P3` (indeed `A s0 + B s1 = P1 + P2` and `C s0 + A s1 = P1 + P3`). *Order 9, three-way* (for each of the matrices `A`, `B - A`, `C - A`): a Toeplitz matrix of order 9 has the blocks `T[r][c] = T_(2 + r - c)` (`r, c < 3`, `T_0, ..., T_4` Toeplitz matrices of order 3); with `V = (V0, V1, V2)`: `Q0 = (T_0 + T_1 + T_2) V2`, `Q1 = (T_3 + T_2 + T_1) V1`, `Q2 = (T_4 + T_3 + T_2) V0`, `Q3 = T_2 (V0 - V2)`, `Q4 = T_1 (V1 - V2)`, `Q5 = T_3 (V0 - V1)`, `y0 = Q0 + Q3 + Q4`, `y1 = Q1 + Q5 - Q4`, `y2 = Q2 - Q5 - Q3` (each `y` expands to `T_2 V0 + T_1 V1 + T_0 V2`, `T_3 V0 + T_2 V1 + T_1 V2`, `T_4 V0 + T_3 V1 + T_2 V2`). *Order 3:* the direct product, 9 multiplications and 6 additions (15). So `C(3) = 15`, `C(9) = 6 C(3) + 27 = 117` (9 subtractions before, 6 additions or subtractions after for each of the three outputs: 27) and `C(18) = 3 C(9) + 27 = 378` (9 additions before, 18 after): 162 multiplications, 162 additions and 54 subtractions. The 18 products of order 3 use 18 kernels of 5 constants, 90 constants in all (the kernel entries `kappa`, their differences `B - A`, `C - A` and the sums `T_0 + T_1 + T_2`, `T_3 + T_2 + T_1`, `T_4 + T_3 + T_2`), formed once per trial from the 35 entries `kappa(e)`, `1 <= e <= 35`, by 124 additions and subtractions and stored (2 each, with the address operation). The direction `O2 -> O1` has the transposed matrix (`T[i][t]` for `T[t][i]`, the kernel array reversed; the factors `z^(-t)` that depend on `t` alone are part of the output factors), whose 90 constants are formed the same way: 2 * (124 + 180) = 608 operations in the tables of the stage. Per group of `VCNT` positions the 90 constants are loaded (2 each, with the address operation); the running factors `f_i` of the `K` inputs and `g_t` of the `K` outputs and their steps (the constants `u_k^(-1)` of the input cosets and `u_k` of the output cosets) stay in registers over the whole phase (set from their base table at its start, `vd_reset`); per position the `K` inputs are read from the coset array (the load and its address 2), multiplied by their factors (1) and the factors by their steps (1): 4 each; the product costs 378; the `K` outputs are multiplied by their factors (1), the factors by their steps (1) and written (the store and its address 2): 4 each; 5 for the position loop and its address: `2 * 90 + cnt (4K + 378 + 4K + 5)` per group, `527` per position. The schedule is the recursion above in the order written (the sums of inputs first, the products in the order of their numbers, each output formed when its last product is added): at most 40 values are live at once (the 18 inputs and the partial results), so the kernel uses 90 + 72 + 40 = 202 of the 256 field registers (the integer address registers are separate: the 18 + 18 coset bases, the position and the loop count).

**Charges** (the components sum to row C of section 6):

| component | operations |
|---|---:|
| inner transforms, per coset (column passes of 4.2; forward / inverse) | 368,427,663,376 / 368,427,663,376 |
| geometric phase of one extension (29.289 per element of `n1`) | 2,264,299,208,962 |
| one extension with its `2K` inner transforms | 11,863,282,680,098 |
| one loop step, `b = 0` / `b = 1` | 24,091,637,580,372 / 24,282,763,625,044 |
| tables: `30 K` constants, the two `omega` tables of `2^16` entries, the kernel spectra, the 2 x 90 constants of the extension kernels | 4,634,460 |
| Newton reciprocal (step 1, with its allocations) | 18,060,840,801,479 |
| product for `q` (step 1) | 5,429,417,913,149 |
| evaluation of `g` (step 2, geometric part) | 11,735,876,501,760 |
| `2K` forward inner transforms of `g` (step 2) | 9,491,206,635,536 |
| step 3 | 13,299,798,245,920 |
| step 4 (one extension; its last two forward layers are in the first boundary pass of the loop) | 11,413,384,855,840 |
| step 5 (batch inversion in chunks of `2^16`) | 1,143,452,860,832 |
| step 6, the loop: 220 steps (45 with `b = 1`) | 5,308,760,939,692,080 |
| step 7 (with the boundary pass of the last two forward layers of the extension) | 13,762,731,967,552 |
| step 8 (two interpolations) | 59,174,071,304,484 |
| allocations, exponent scan, zero fills, end of stage | 10,200,552,574 |
| stage C of one trial, with the stage bookkeeping of 1,000 (ledger row C) | 5,452,281,925,966,666 |

The inner transforms are column passes and the geometric phase uses the register-blocked kernels above (the outer-kernel convention of 1aa56884). Every charge depends only on `m` and the exponent, not on the coefficients.

**Memory.** The loop holds `R1`, `R2`, `G1` and the array of `g` (which holds `g` on `O2` during the loop and `g` in coefficient form at the exit): four arrays of `n1` elements. `R1` is allocated at the product for `q` (step 1 writes `q` into it) and `R2` before step 2, after the arrays of the Newton reciprocal are freed, so the Newton phase holds neither. The loop also holds the tables (the `30 K` constants, the two `omega` tables of `2^16` entries, the kernel spectra, the 2 x 90 constants of the extension kernels; the table of about 4.2 million bytes stays in its slab class of `2^23` bytes), the group buffer of `VCNT = 2^10` rows of `Lmax = Le = 2^6` elements (the longest kernel) and one transform row of `Lmax` elements; step 5 adds one array of `2^16` elements. The live peak of stage C is `3.0000` arrays of `n1` above its entry (`7,421,711,905,344` bytes), plus the twiddle table and the array of `g` from stage A: `9,964,332,544,704` bytes, the live peak of the trial. Section 7 walks these allocations with the rest of the trial.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: worst-case operation count (primitive operations; `C(10) = 426`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, the trial loop and the allocator reset after an ABORT (charged in every trial); `T_off` = the offline bound of section 6.2. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 1` (one centre, section 9.2), and `time_log2 = ceil_5(log2(N_max / 426))`.

Every stage is charged by the rules of section 4.2 where it executes. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(32-1)` elements (`ntt_init(32)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 17,179,887,292 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,196 |
| B (per trial) | (this entry: each evaluation by the program `L` of Appendix L, `255` operations, in place of `426`) `12` cosets of `6,442,450,944` points, each point with two evaluations of `F` (at `c + s` and `c - s`) at `C(10) = 426` operations each, the loop work around them, `12` inverse transforms of size `6,442,450,944`, the geometric solve of the cosets (two correlations of length `24` per position), the normalisation | 70,724,726,346,290 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain (section 4.6): the Barrett start (Newton reciprocal and the product for `q`), the evaluations of `g` and `q`, the batch inversion, `220` steps (45 with `b = 1`), each two pointwise passes and two extensions, the exit and the two interpolations | 5,452,281,925,966,666 |
| D (per trial) | half-gcd of `(g, R - 1)` (sections 4.4, 4.4.1, 4.4.2), charged for the normal remainder sequence with the quotient and return tests, the outer steps with the applies of 4.4.2; any other sequence ends the trial after a prefix of this work (section 6.3) | 2,561,608,653,181,651 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, register-resident, each at most `R(16) = 196,915` with its draw (Appendix S), the stage bookkeeping 1,000 and the load of `G` into registers 200 | 12,603,760 |
| F (per trial) | square root, back-map (below) | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 426 + 32` | 9,552 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| ABORT reset (per trial) | the reset of the allocator when a test of stage D (quotient, return or window) or the zero test of stage C (4.6 step 5) fails and the trial ends (section 6.3): the 47 free-list heads (classes 7 to 53), the end of the slab area, the two ends of the pool and the header of its free middle block; at most 1,000, charged in every trial | 1,000 |
| plan_invN misses | one per distinct plan size (32 sizes) | 98,848 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **8,084,632,502,538,269** |

Row C is the sum of the charges of section 4.6 (added up in 11.1); row D is the charge of the half-gcd of sections 4.4, 4.4.1 and 4.4.2 with the products of 4.5, on the normal remainder sequence (6.3).

`N_max = 8,084,632,502,538,269` operations `= 18,978,010,569,338.66` units, `log2(N_max / 426) = 44.1093939987`, claimed as `44.10940` (rounded up at five decimals).

Stage B charges each of the `154,618,822,656` evaluations of `F` as one reduced permutation, `C(10) = 216 + 21 * 10 = 426` operations, although a line evaluation is a strict subset of the work of a reference permutation; the loop work around the evaluations is charged on top (section 3).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the isolation loop until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 31, the zero test of the shift (5, and at most 2 for the replacement of a zero draw by 1) and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because the memory-access charge adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `2,640` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = 2,594,979`, of which `pow_half` is 2,471,032, the Taylor shift 11,700 and the two gcds 54,395 each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + 64 * R(16) + 114 = 166,079,773`. This entry replaces this stage E by the register-resident procedure of Appendix S (no Taylor shift, inversion-free gcd, every field operation charged once): `R(16) = 196,915`, row E `12,603,760`.

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`.

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.2 Offline derivation of the literals (preprocessing)

The literals of the sources are computed once, offline, from `p` and the organizer's 192 round constants and 9 MDS entries, one literal at a time (working set: at most 16 words of 32 bytes and a 64-byte digit buffer); each is the value of one closed formula, with no search and no choice. Count in the primitives of 4.2 (orchard-field-ram-v2: every field operation, load, store and control operation is 1): a field operation is charged 4 (the operation, two operand loads, one store), a 64-bit word operation 3 (the operation, one load, one store), a hexadecimal digit 5 (its load, the table load, a shift, an or, the loop control). (a) Input: 202 values of 64 hexadecimal digits (`p`, the 192 round constants, the 9 MDS entries), 324 each with the 4 word stores: `65,448`. (b) Field literals, 489 field operations: `2 = 1 + 1` (1); `R = 2^256 mod p`, `2` squared 8 times (8); `R^2 mod p` (1); the Montgomery forms `x R mod p` of the 201 organizer constants (201); `2^65 R mod p` (`2` squared 6 times, times `2`, times `R`: 8); `5 = 2 + 2 + 1` (2); `5^t R mod p` with `t = (p-1)/2^32`, the odd exponent of the Tonelli-Shanks of stage F (223 bits, 46 of them 1: 222 squarings, 45 multiplications, times `R`: 268); charged `4 * 489 + 3 * 222` (the bit steps of the square-and-multiply) `= 2,622`. (c) Word literals, 90 word operations: `p - 1` (4), `t` (a shift by 32 over 4 words, 12), `(t+1)/2` (16), `(p-1)/2` (12), `p - 2` (4), `e = (4(p-1)+1)/5` (a shift by 2 into 5 words 15, plus 1, a division by 5 word by word 10: 26), `-p^-1 mod 2^64` (5 Newton steps `x <- x (2 - p_0 x)` from `x = p_0`, 3 each, and a negation: 16); charged `3 * 90 = 270`. (d) Output: 211 literals of 64 hexadecimal digits (the 201 Montgomery forms, `R`, `R^2`, `2^65 R`, `5^t R`, `t`, `(t+1)/2`, `(p-1)/2`, `p - 2`, `e`, `p`), 324 each, and `-p^-1 mod 2^64` (16 digits, 81): `68,445`. `T_off = 65,448 + 2,622 + 270 + 68,445 = 136,785` operations. The ledger charges the declared cap `1,000,000 >= T_off` (`preprocessing_log2 = 20`, `2^20 = 1,048,576`), inside `N_max`: a counted bound, not a premise. The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry e6dcb600)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c, R_c - 1)`: every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centering division or pseudo-division of a node, the division of each repetition of the outer loop, each step of the base case) tests that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); (c) the window test of 4.4.1 item 3 (2 tests, 2 operations each); a zero remainder inside hgcd or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state after the twiddle table (1,000 operations, charged in every trial) and the next centre is drawn. Lemma (prefix; e6dcb600, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each call splits at k1 = ceil(k/2) (a node of 4.4.2 at the fixed budgets `2^(j-1) - 1`, its outer budget a function of `n`) and, with every quotient of degree 1, every degree in the tree is fixed by m and the number of quotients so far and the parameters of the second call and of the outer loop are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's hgcd calls and divisions produce has degree at least 94 (n >= 193), so a gcd of degree at most 94, and so every gcd of degree at most DMAX, first appears in the classical Euclid below degree 192, after a prefix of the degree-0 work. A zero remainder anywhere earlier (gcd degree above 94, a failed trial anyway) ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2(g)). Row D of section 6 is this charge, `2,561,608,653,181,651`.

## 7. Memory

Five terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 1,044,224 bytes of code (399,216, plus 645,008 for the bodies written four times per loop, 4.2, at most 16 bytes per instruction: the block-form passes, per direction and `k = 1..7` three more copies of the block body and the group-0 variant, `2 * 4 * 16 * 2,836` with a body of at most `2^(k+1) + 3 k 2^(k-1) + 3` instructions; the stage-C column kernels, three more copies of the per-position body of `ob4` to `ob128` (forward and inverse), `ob4m` and the three boundary kernels, `3 * 16 * 5,875`), 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages): 5,895,452 bytes; and 49,152 bytes (at most 3,072 instructions of 16 bytes) for the routines of this entry, the two apply forms of 4.4.2, the chunked batch inversion, the two `omega` tables of 4.6 and the extension kernel of 4.6 (at most 800 instructions: the group loads of its 90 constants, the 527 instructions of the position body, the loop): 5,944,604 bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (the second trial repeats the first from the same state: a trial frees every array but the twiddle table, and the simulation checks that the pool is back to that state). The simulation records every allocation and free of the trial in the order of the program (the twiddle table, stage A, stage B, stage C, stage D; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order), checks that these events reproduce the live-set walk of every stage (bytes in use, peak, live blocks), and runs the allocator on them. By the prefix lemma of section 6.3 every size in the sequence is a function of `m` and of the shape of the recursion on the normal sequence (and the transform sizes of the products), so the sequence is the same for every input. The two-ended pool takes the blocks of more than 2^26 bytes and is simulated address by address (two lists in address order, the low one from the bottom and the high one, for the statements of 4.2 that use the high end, from the top; the first free block that fits on the request's side is cut from the side nearest its end; a free merges with its free neighbours and with the unused middle); its capacity is the largest sum of the extents of the two ends over the trial, `9,964,324,127,040` bytes (reached in stage C; stage D stays at or below it), plus 128 bytes so that the unused middle is always at least 128 bytes. The live-set peak of the same sequence is `9,964,332,544,704` bytes (stage C; pool and slab blocks together) and the arena is `9,965,321,867,712` bytes, `1.000099` times it: the pool capacity plus 128, the slab area `997,723,648` (the sum of the per-class peaks, reached at different points of the trial) and `16,896`, rounded up to 64 bytes (the slab blocks are in the live set, so the pool capacity lies `8,417,664` bytes below the live-set peak). The slab classes take the blocks of at most 2^26 bytes (a block of at most `2^j` bytes gets a slot of `2^j` bytes; the free list of the class first, else a new slot from the end of the slab area), so the slab area is the sum over the classes of the peak number of live blocks of the class times `2^j`: `997,723,648` bytes. Stages E to I hold at most 16 live arrays of at most 17 elements (16 slots of 1,024 bytes), and the allocator keeps 47 free-list heads (classes 7 to 53) and the end of the slab area (48 words, 384 bytes): `16,896` bytes with a margin of 128. The peaks of the live set per stage (twiddle table, `g`, `F` and the live set of the stage; the arena above is larger): A 2,542,620,639,360; B 5,016,521,801,920; C 9,964,332,544,704; D 7,490,422,965,888; stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The walk of stage D is the walk of the normal remainder sequence (6.3) with the windows of 4.4.1, the node arena and the apply arrays of 4.4.2 and the table of the scales `1/2^a` (31 words, one allocation, live from the entry of stage D to its end): every array of stage D has the length the normal sequence gives it, and a trial with any other sequence ends (ABORT) after a prefix of these allocations, so the walk bounds every trial. The largest transform has `3 * 2^32` points and uses roots of unity of order 3 and `2^32` (`p - 1` is divisible by 3 and by `2^32`); products that would need a longer transform are computed by blocks (section 4.5) or, in the outer steps of stage D, by the fixed-slot apply of 4.4.2. The largest buffers are those of stage C (section 4.6: `R1`, `R2`, `G1` and the array of `g`, `n1 = 77,309,411,328` elements each, and the tables; the Newton phase of its set-up holds three arrays of `ell` elements and the forms of one product, without `R1` and `R2`) and those of stage D (4.4.2: the pair, the node arena, the six arrays of an apply).

(c) A stack bound of 65,536 bytes.

(d) The register file of the machine of claim.json: one file of 387 words (256 field registers and 131 integer address registers), each counted as a 256-bit word, 12,384 bytes.

(e) The working set of the offline derivation of section 6.2: 16 words of 32 bytes and the 64-byte digit buffer, 576 bytes.

Total: (a) + (b) + (c) + (d) + (e) = `9,965,327,890,812` bytes `= 2^43.18005441`, claimed as `memory_log2_bytes = 43.18006` (rounded up at five decimals). The rows of section 6 and this arena are generated by our counting program (section 11 prints its trace of rows C and D): it adds the charges of 4.2 over every call of the algorithm of section 4 in program order and runs the allocator of 4.2 on the same allocation sequence; each term is the closed formula stated in sections 4 and 6, and the program is not attached. The memory penalty is `max(0, 43.18006 - 20) = 23.18006`. The offline derivation of section 6.2 handles one literal at a time; its working set is term (e). The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init". This entry adds `16,384` bytes of code and static data (Appendix L.4: `L` as one subroutine, its constants, the call site and the register-resident stage E of Appendix S): footprint `9,965,327,907,196` bytes `= 2^43.1800544`, claimed `memory_log2_bytes = 43.18006`; the arena and the allocation walk are unchanged.

## 9. Success probability and the premises `H-ONE` and `H-NORMAL`

### 9.1 The premise `H-ONE`

Notation. `p` is the Pallas prime, `D = 5^16`, and `F` is the fixed polynomial of section 2.3 at r = 10 (degree `D`, leading coefficient `f_D(0) != 0`). `g_c` is the monic odd part about the centre `c` (section 3, degree `m = 76,293,945,312`), and `G(c, t) = (F(c + t) - F(c - t)) / (2 t) = g_c(t^2)`. For `c` in `F_p`, let `k(c)` be the number of nonzero squares `S` with `g_c(S) = 0`; this is `deg G_c` of section 3, the degree of `gcd(g_c, S^((p-1)/2) - 1)`. `E_c` is the event `1 <= k(c) <= DMAX` (`DMAX = 16`) under which stage E runs.

**Premise `H-ONE`.** The number of centres `c` in `F_p` with `1 <= k(c) <= 16` is at least `0.3931 p`. Equivalently, for `c` uniform on `F_p`, `P(E_c) >= q = 0.3931`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r10-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2) and the polynomial `F` of section 2.3, with centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:**
- The premise concerns this `F`, not every polynomial of degree `D`. It is false for permutation polynomials: every pure composition of maps `x -> a x^5 + b` is bijective and has `k = 0` at every centre. It is also false for a decomposable `F` with imprimitive monodromy (the axis line of 10.3, Theorem C).
- It is false at one layer (`F_1`, `m = 2`: the law of 9.3(a) gives exactly 0.375) and true at two and three layers (9.3(c)).
- The value `0.3931` is `0.3934693 - 0.3931 = 0.0003693` below the value `1 - e^(-1/2) = 0.3934693` of the law of 9.3(a), and below the four-moment Bonferroni bound `151/384 = 0.3932292` (9.3(b)). With `delta = 0.001` (9.5), the bound of 9.2 needs `P(E_c) >= 0.391000000000002345`.

What the premise does not contain: no random-polynomial model; no independence of centres (one centre is drawn); no statement about the remainder sequences (that is `H-NORMAL`, 9.5); and nothing about the cost.

### 9.2 The success bound with one centre

(a) *Centre.* The centre is one draw (4.1.1) and lies within statistical distance `eps_coin < 2^-128` of uniform on `F_p`; the exact value is 1.574e-39 (2^-128.90). So `P(E_c) >= q - eps_coin` for the drawn centre.

(b) *The ABORT of stage D and the zero test of stage C.* Let `N_c` be the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd: `deg(R_c - 1) = m - 1` and every quotient of degree 1 (section 6.3). By the premise `H-NORMAL` (9.5), `P(not N_c) <= delta = 0.001` for `c` uniform.

Let `Z_c` be the event that `g_c` vanishes at a point of the set `O1` of the value-domain stage C; its zero test (section 4.6) ends the trial. For each of the `n1` points `x` of `O1`, `g_c(x)` (before normalisation) is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so it has at most `D - 1` roots. Each residue is drawn with probability at most `4/2^256` (4.1.1). Hence `P(Z_c) <= delta_C = n1 (D - 1) 4 / 2^256 = 4.075e-55 (2^-180.7)`, proved, no premise.

If `E_c` and `N_c` hold and `Z_c` does not, stages C and D run to their end and return `G = gcd(g_c, R_c - 1)`.

(c) *Isolation.* If `E_c` holds, stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48`, over words that are fresh for that stage (lemma 9.4).

(d) *The bound.* A trial with `E_c`, `N_c`, not `Z_c`, and a successful isolation ends in a verified collision (sections 2-5). For `c` uniform, `P(E_c and N_c and not Z_c) >= q - delta - delta_C`. So, with `K = 1`,

`P[success] >= 1 - (1 - q + delta + delta_C)^K - K (eps_coin + eps_iso) = q - delta - delta_C - eps_coin - eps_iso = 0.392099999999997615 >= 0.39209`

with `q = 0.3931`, `delta = 0.001` and `K = 1`. This is the form of bradcush's entry 1aa56884 (9.2(f) there) at `K = 1`. The bound stays at least 0.39 for every `delta <= 0.0030999` at `q = 0.3931`, and for every pair with `q - delta >= 0.390000000000002345`. The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 10 enters it.

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

The Bonferroni bounds of orders 7 and 8 then give `0.39346933 <= P(E_c) <= 0.39346944` for `F_2` and for `F_3`. At these depths `H-ONE` is a theorem, with margin 0.00237.

 At `N = 4`, the cycle types `(312)` and `(311,1)` of 10.3 make `pi(Gamma)` 2-transitive of degree 312. The only such groups are `A_312`, `S_312`, and the groups between `PSL(2,311)` and `PGL(2,311)`, whose non-identity elements fix at most two points. Centres with `k(c) = 3` and `k(c) = 4` occur (our runs, 10.5.1), and the 312-cycle is odd, so `pi(Gamma) = S_312`. The sign kernel at `N = 4` is not computed.

(d) *Measured.*
-  Toy fields, exact over all centres: deployed constants reduced modulo `p = 1,048,627` and six random-constant seeds, 3 to 8 S-box layers, partial rounds included, 27 cases. `P(k >= 1)` lies between 0.39214 and 0.39436; the largest deviation from 0.3934693 is 0.00133, that is `1.36 / sqrt(p)`.
- The real field: the organizer-run tests of 10.5.1 and our runs, reproducible observations at `m = 12` and `62`; no probability bound is drawn from them.

(e) *The extrapolation.* At `N = 16` neither the monodromy nor the counts can be computed. Weil's bound exceeds `p` for `j >= 2` (relative error `2^21.6` at `j = 2`).

The premise states that this `F` stays within `0.0003693` of the law of (a) (`q = 0.3931 <= 151/384 = 0.3932292`): no structure appears between the third layer and the 16-th that changes the law of the positive fixed points by 0.1%.

The measured deviations shrink like `p^(-1/2)` and do not grow with the degree. On the toy fields the deviation is `1.36 / sqrt(p)` . The counts of Grok job 139 give `eps ~ 3.1 / sqrt(p)` over degrees 5 to 1,953,125 (10.3).

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - S3)/2^256 = 1/2 - 7.869e-40` (`S3` of 4.1.1) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `S3` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - S3)/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`. This is a proved bound under the random words, not a premise and not a sample.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries e6dcb600 and 1aa56884, with the allowance and the organizer-run tests of gta6rp's entry fe269c23)

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 76,293,945,312`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.001` (`2^-9.966`).

Four fields (as in claim.json). **Role:** score-critical for the success probability only. The time and memory bounds hold for every sequence: stage D is charged for the normal sequence, every division tests its quotient and every call its return, and on any other case the trial ends after a prefix of the charged work (6.3). **Scope:** the pairs `(g_c, R_c - 1)` of the target `poseidon-orchard-r10-prefix-v1`, `c` uniform on `F_p`; nothing is claimed for other round counts. **Extrapolation and evidence:** for a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-180.7`. That bound does not transfer directly, because the coefficients of `R_c` have degree about `p` in those of `g_c`; the premise asserts far less than random-pair behaviour, an abnormality probability of at most `delta = 0.001`, which is all the bound of 9.2(d) uses (every `delta <= 0.0030999` keeps it at least 0.39). Measured support, organizer-run (10.5.1): the experiments `euclid-normal-n2-t256-l2-a` to `-f` compute the complete sequence of `(g_c, R_c - 1)` for this construction on the truncation `F_2` of the digest polynomial (10.3; `m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all), and `euclid-normal-n3-t24` and `euclid-normal-n4-t2` on `F_3` and `F_4` (`m = 62`, `312`) for 24 and 2 organizer-seeded centres; each returns a witness pair exactly when the sequences of a trial are normal. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.001` is the declared premise). Our local runs of these eight entries (seeds of our own, one CPU): 3,098 sequences (3,072 at `m = 12`, 24 at `m = 62`, 2 at `m = 312`), all normal. Reported by our earlier entries, not organizer-run (10.5): the complete sequences on the sibling targets with `r' = 0` and `r' = 1` partial rounds (`m = 7,812` and `39,062`), every quotient of degree 1 in all 10 runs. **Limitations:** the tests reach `m = 312` (the sibling runs `m = 39,062`), far below `m = 76,293,945,312`. Normality is computed inside the submitted program; the runner checks only the returned witness pairs, so the tests are evidence under trusted execution of that program, which is printed in full in `experiments/exp_euclid.py`.

## 10. Evidence

This section is the evidence for the premise `H-ONE` and for the digest of the target. The computations of 10.3 are ours; the experiments of 10.2 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.2 The organizer experiments declared in `experiments/manifest.json`

Sixteen experiments of kind `python-message-pairs-v1` (five here, eleven in 10.5.1 and 10.5.2), run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The three Python sources are 58,143 bytes together (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r10-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run is the evidence: 256 of 256 trials returned a verified pair at r = 10, and the output was byte-identical on repetition. Our own earlier local run of the same events (plain Python on our machine) agreed: 256 of 256 trials.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 10: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining sixteen rounds applied to `alpha + beta W` (`deg F = 5^16`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-ONE` is about (a root of `g_c`). The count of returned pairs at each width is a reproducible observation of the construction's own antipodal pairs on the target; no probability, rate or population bound is drawn from it (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed), and it does not enter section 9.

The intake report of the organizer's run records 238, 103, 32, 11 of the 256 trials with a verified pair for `w` = 6, 8, 10, 12 respectively, and byte-identical output on repetition. 

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

### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 10` applies the Euclidean algorithm to `g_c` (degree `m = 76,293,945,312`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. This section and 10.5.1 are the measured support of the premise `H-NORMAL` (9.5): stage D is charged for the normal remainder sequence and a trial ends at the first quotient of degree other than 1 (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at the gcd (degree 0, or degree 1 at the r' = 0 centres 2, 4, 7) after `m - deg gcd` divisions, and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core.

At `r = 10` the stages need about 11,550 GB and 9.6e15 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7.

### 10.5.1 Organizer-run tests: normality (`experiments/exp_euclid.py`)

Eleven experiments of kind `python-message-pairs-v1`, declared in `experiments/manifest.json` and run by the organizer's runner (program `experiments/exp_euclid.py`, 25,241 bytes, Python standard library only, the program of our r = 9 entry `5b96dbb5`): the normality tests `euclid-normal-n2-t256-l2-a` to `-f` (two centres per trial, `m = 12`, 512 sequences each, 3,072 in all), `euclid-normal-n3-t24` and `euclid-normal-n4-t2` (one centre per trial, `m = 62` and `312`), and the good-centre tests `euclid-gcdpos-n2-t256-a`, `-b` and `euclid-gcdpos-n3-t24` (10.5.2). The design follows gta6rp's organizer-run normality tests (entry fe269c23, its 10.5.1); the program is our own. For each computed trial the program takes a centre `c` from the trial seed (the rule of `exp_line.py`) and builds, exactly over `F_p`, the polynomial `F_N(c + X)`: the `F_N` of 10.3 (start state `alpha + beta W` of the line `j = 0`, the S-box layers of rounds 2 and 3 (full), then 4 and 5 (partial, coordinate 0), the MDS after each; degree `5^N`). It checks `F_N` against direct iteration of those layers at `c + 1`, `c - 1`, `c + 2`, `c - 2` and the odd-part identity `2 x g(x^2) = F_N(c + x) - F_N(c - x)` at `x = 1, 2`; takes the monic odd part `g` (degree `m = (5^N - 1)/2`); computes `R = X^((p-1)/2) mod g` (253 squarings and 45 multiplications by `X`); and runs the complete Euclidean sequence of `(g, R - 1)` down to the zero remainder, recording the degree of every quotient. The sequence is normal when `deg(R - 1) = m - 1` and every quotient has degree 1, the condition of 6.3 and 9.5. A normality trial whose sequences are all normal and pass the checks, or a good-centre trial whose checks pass with `deg gcd(g, R - 1) >= 1`, returns two distinct canonical messages: the points `c + s` of the line, `s = 1, 2, ...`, are mapped back to `(nk, rho)` as in 10.2(b), and the first two whose digests of the selected target agree on the first 6 bits of the big-endian reading are returned. Among 65 points such a pair always exists, so a computed trial that passes always returns a pair. Every other trial, and every trial past the first `T` (`T` = 256 for the `n2` entries, 24 for the `n3` entries and 2 for `n4`, the sandbox budget of 20 s), returns two nulls. The organizer-checked count of returned pairs therefore equals the number of computed trials that pass. The per-trial counts listed in the manifest are reported as observations, which the runner labels untrusted. Expected: every computed sequence is normal in the normality tests, so all 6 x 256, 24 and 2 computed trials return a pair; zero abnormal in the 3,072 sequences of the `-l2` entries is a reproducible observation consistent with `H-NORMAL`, and `delta = 0.001` is the declared premise (9.5), not an interval computed from these runs. The good-centre tests are in 10.5.2. No probability, rate or population bound is drawn from any of these organizer-seeded trials (public seeds; nothing is assumed about the trials being independent or identically distributed), and none enters section 9. For `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2` (its layers come before the final full rounds), so the tests measure the same family of pairs as the premise; only the witness uses the digest at r = 10.

Our local runs of the eight normality entries (seeds of our own, one CPU): 3,098 sequences (3,072 at `m = 12`, 24 at `m = 62`, 2 at `m = 312`), all normal. What these tests show: under trusted execution, the construction's own pairs `(g_c, R_c - 1)` have normal remainder sequences at `m = 12` to `312`. What they do not show: anything at `m = 76,293,945,312`, where `H-NORMAL` remains a premise that asserts only `delta = 0.001`.

### 10.5.2 Organizer-counted good centres (`H-ONE`)

euclid-gcdpos-n2-t256-a, -b and euclid-gcdpos-n3-t24 take one organizer-seeded centre per trial at `N = 2, 3` (`m = 12, 62`), compute `G = gcd(g_c, R_c - 1)` with `R_c = S^((p-1)/2) mod g_c` (`deg G = k(c)`, the quantity of `H-ONE`) and return a witness pair ONLY when `deg G >= 1` and the checks pass, so the organizer's returned-pair count is the good-centre count. Expected: the fraction of good centres is the law of 9.3, a theorem at these depths; the returned counts are reproducible observations consistent with it, and no probability, rate or population bound is drawn from them (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed). Our runs of these three entries on seeds of our own (one CPU): 106 and 100 of 256 and 12 of 24.

## 11. The generated trace of rows C and D (instrumented run of the counting program of section 6; no new charge)

Every row below is a partial sum of the program's own charges; each table adds up exactly to its ledger row, and each row follows from the dimensions and the charging rules of section 4.2.

### 11.1 Row C = 5,452,281,925,966,666

The components of section 4.6 add up to row C: 4,634,460 + 18,060,840,801,479 + 5,429,417,913,149 + 11,735,876,501,760 + 9,491,206,635,536 + 13,299,798,245,920 + 11,413,384,855,840 + 1,143,452,860,832 + 5,308,760,939,692,080 + 13,762,731,967,552 + 59,174,071,304,484 + 10,200,552,574 + 1,000 = 5,452,281,925,966,666. The loop (step 6) is `175` steps with `b = 0` and `45` with `b = 1`: `175 * 24,091,637,580,372 + 45 * 24,282,763,625,044 = 5,308,760,939,692,080`. One loop step is the two pointwise passes and the two extensions of 4.6 step 6; an extension is `K` inverse inner transforms of one point set, the geometric phase and `K` forward inner transforms of the other, and every inner transform is the column passes of 4.2 at `cnt = K` positions per call.

### 11.2 Row D = 2,561,608,653,181,651

The Euclid driver of 4.4 makes 184 repetitions. Repetitions 1-72 are outer steps of 4.4.2: the inversion-free node of budget `k = 2^j - 1` (the largest with `k <= min(2^31 - 1, (n - 1)/2)`) on the top window, the apply of `adj(M)` to the whole pair in place, then one division with the quotient and return tests; `node` is the charge of the node with its call, `form` the apply form and its transform size `N` (4.4.2), `apply` the charge of the apply, and the last column the repetition with the matrix allocations, the arena, the division and the tests. Repetition 73 (`(n - 1)/2 < 127`) is the lean half-gcd of 4.4.1; below degree `192` the classical Euclid runs 111 steps.

| repetition | operand lengths | j | k | node | form, N | apply | repetition total |
|---:|---:|---:|---:|---:|---|---:|---:|
| 1 | 76,293,945,313, 76,293,945,312 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 30,602,259,429,359 | 85,718,638,440,199 |
| 2 | 74,146,461,665, 74,146,461,664 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 30,555,014,789,133 | 85,639,181,545,253 |
| 3 | 71,998,978,017, 71,998,978,016 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 30,495,584,556,595 | 85,547,539,057,995 |
| 4 | 69,851,494,369, 69,851,494,368 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 30,422,570,112,581 | 85,442,312,359,261 |
| 5 | 67,704,010,721, 67,704,010,720 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 30,355,648,464,645 | 85,343,178,456,605 |
| 6 | 65,556,527,073, 65,556,527,072 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 26,678,554,339,711 | 81,633,872,076,951 |
| 7 | 63,409,043,425, 63,409,043,424 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 26,631,309,699,511 | 81,554,415,182,031 |
| 8 | 61,261,559,777, 61,261,559,776 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 26,571,879,466,947 | 81,462,772,694,747 |
| 9 | 59,114,076,129, 59,114,076,128 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 26,498,865,022,971 | 81,357,545,996,051 |
| 10 | 56,966,592,481, 56,966,592,480 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 26,320,260,159,429 | 81,146,728,877,789 |
| 11 | 54,819,108,833, 54,819,108,832 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 22,754,849,250,081 | 77,549,105,713,721 |
| 12 | 52,671,625,185, 52,671,625,184 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 22,707,604,609,863 | 77,469,648,818,783 |
| 13 | 50,524,141,537, 50,524,141,536 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 22,648,174,377,329 | 77,378,006,331,529 |
| 14 | 48,376,657,889, 48,376,657,888 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 22,506,987,491,771 | 77,204,607,191,251 |
| 15 | 46,229,174,241, 46,229,174,240 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 22,447,557,259,199 | 77,112,964,703,959 |
| 16 | 44,081,690,593, 44,081,690,592 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 18,831,144,160,433 | 73,464,339,350,473 |
| 17 | 41,934,206,945, 41,934,206,944 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 18,783,899,520,223 | 73,384,882,455,543 |
| 18 | 39,786,723,297, 39,786,723,296 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 18,693,714,824,085 | 73,262,485,504,685 |
| 19 | 37,639,239,649, 37,639,239,648 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 18,634,284,591,549 | 73,170,843,017,429 |
| 20 | 35,491,756,001, 35,491,756,000 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 16,787,078,490,253 | 71,291,424,661,413 |
| 21 | 33,344,272,353, 33,344,272,352 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 14,907,439,070,801 | 69,379,572,987,241 |
| 22 | 31,196,788,705, 31,196,788,704 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 14,860,194,430,593 | 69,300,116,092,313 |
| 23 | 29,049,305,057, 29,049,305,056 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 14,800,764,198,073 | 69,208,473,605,073 |
| 24 | 26,901,821,409, 26,901,821,408 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 12,973,805,822,587 | 67,349,302,974,867 |
| 25 | 24,754,337,761, 24,754,337,760 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 12,914,375,590,087 | 67,257,660,487,647 |
| 26 | 22,606,854,113, 22,606,854,112 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 10,983,733,981,191 | 65,294,806,624,031 |
| 27 | 20,459,370,465, 20,459,370,464 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^32` | 10,936,489,340,945 | 65,215,349,729,065 |
| 28 | 18,311,886,817, 18,311,886,816 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 9,160,533,154,907 | 63,407,181,288,307 |
| 29 | 16,164,403,169, 16,164,403,168 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 9,101,102,922,431 | 63,315,538,801,111 |
| 30 | 14,016,919,521, 14,016,919,520 | 31 | 2,147,483,647 | 54,004,182,080,871 | direct, `3 * 2^32` | 7,088,995,139,397 | 61,271,218,763,357 |
| 31 | 11,869,435,873, 11,869,435,872 | 31 | 2,147,483,647 | 54,004,182,080,871 | direct, `3 * 2^32` | 7,017,312,319,748 | 61,167,323,688,988 |
| 32 | 9,721,952,225, 9,721,952,224 | 31 | 2,147,483,647 | 54,004,182,080,871 | fixed, `3 * 2^31` | 5,347,260,487,269 | 59,465,059,601,789 |
| 33 | 7,574,468,577, 7,574,468,576 | 31 | 2,147,483,647 | 54,004,182,080,871 | direct, `3 * 2^31` | 3,495,360,208,712 | 57,580,947,068,512 |
| 34 | 5,426,984,929, 5,426,984,928 | 31 | 2,147,483,647 | 54,004,182,080,871 | direct, `3 * 2^31` | 3,411,491,796,852 | 57,464,866,401,932 |
| 35 | 3,279,501,281, 3,279,501,280 | 30 | 1,073,741,823 | 25,619,629,261,547 | direct, `3 * 2^30` | 1,689,924,048,678 | 27,342,639,707,074 |
| 36 | 2,205,759,457, 2,205,759,456 | 30 | 1,073,741,823 | 25,619,629,261,547 | direct, `3 * 2^29` | 857,468,952,589 | 26,494,078,483,625 |
| 37 | 1,132,017,633, 1,132,017,632 | 29 | 536,870,911 | 12,131,065,984,573 | direct, `3 * 2^28` | 405,988,844,287 | 12,545,982,034,669 |
| 38 | 595,146,721, 595,146,720 | 28 | 268,435,455 | 5,742,099,438,557 | direct, `3 * 2^27` | 199,403,607,526 | 5,946,403,720,052 |
| 39 | 326,711,265, 326,711,264 | 27 | 134,217,727 | 2,712,503,833,405 | direct, `3 * 2^26` | 98,489,166,269 | 2,813,880,407,723 |
| 40 | 192,493,537, 192,493,536 | 26 | 67,108,863 | 1,278,564,413,309 | direct, `3 * 2^26` | 92,064,383,123 | 1,372,509,571,521 |
| 41 | 125,384,673, 125,384,672 | 25 | 33,554,431 | 601,230,876,205 | direct, `3 * 2^25` | 46,000,247,465 | 648,608,582,279 |
| 42 | 91,830,241, 91,830,240 | 25 | 33,554,431 | 601,230,876,205 | direct, `3 * 2^25` | 44,675,737,969 | 646,780,756,303 |
| 43 | 58,275,809, 58,275,808 | 24 | 16,777,215 | 281,979,840,533 | direct, `3 * 2^24` | 22,238,366,520 | 304,840,690,942 |
| 44 | 41,498,593, 41,498,592 | 24 | 16,777,215 | 281,979,840,533 | direct, `3 * 2^23` | 11,455,288,235 | 293,805,954,417 |
| 45 | 24,721,377, 24,721,376 | 23 | 8,388,607 | 131,867,151,769 | direct, `3 * 2^23` | 10,650,872,183 | 142,763,020,481 |
| 46 | 16,332,769, 16,332,768 | 22 | 4,194,303 | 61,469,630,699 | direct, `3 * 2^22` | 5,337,720,668 | 66,989,433,336 |
| 47 | 12,138,465, 12,138,464 | 22 | 4,194,303 | 61,469,630,699 | direct, `3 * 2^22` | 5,170,838,759 | 66,759,636,867 |
| 48 | 7,944,161, 7,944,160 | 21 | 2,097,151 | 28,628,203,147 | direct, `3 * 2^21` | 2,471,935,815 | 31,187,849,091 |
| 49 | 5,847,009, 5,847,008 | 21 | 2,097,151 | 28,628,203,147 | direct, `3 * 2^21` | 2,388,939,999 | 31,073,395,995 |
| 50 | 3,749,857, 3,749,856 | 20 | 1,048,575 | 13,285,565,931 | direct, `3 * 2^20` | 1,189,928,185 | 14,516,018,325 |
| 51 | 2,701,281, 2,701,280 | 20 | 1,048,575 | 13,285,565,931 | direct, `3 * 2^20` | 1,148,875,336 | 14,459,236,836 |
| 52 | 1,652,705, 1,652,704 | 19 | 524,287 | 6,140,894,763 | direct, `3 * 2^19` | 567,510,410 | 6,725,336,422 |
| 53 | 1,128,417, 1,128,416 | 19 | 524,287 | 6,140,894,763 | direct, `3 * 2^18` | 290,897,565 | 6,440,859,257 |
| 54 | 604,129, 604,128 | 18 | 262,143 | 2,825,596,123 | direct, `3 * 2^17` | 142,485,356 | 2,973,216,248 |
| 55 | 341,985, 341,984 | 17 | 131,071 | 1,293,415,619 | direct, `3 * 2^17` | 130,006,068 | 1,426,590,376 |
| 56 | 210,913, 210,912 | 16 | 65,535 | 588,489,287 | direct, `3 * 2^16` | 64,343,326 | 655,018,262 |
| 57 | 145,377, 145,376 | 16 | 65,535 | 588,489,287 | direct, `3 * 2^15` | 33,195,545 | 622,887,441 |
| 58 | 79,841, 79,840 | 15 | 32,767 | 265,869,721 | direct, `3 * 2^14` | 15,373,894 | 281,954,704 |
| 59 | 47,073, 47,072 | 14 | 16,383 | 119,756,857 | direct, `3 * 2^14` | 13,806,109 | 134,028,295 |
| 60 | 30,689, 30,688 | 13 | 8,191 | 53,481,497 | direct, `3 * 2^13` | 6,902,599 | 60,726,545 |
| 61 | 22,497, 22,496 | 13 | 8,191 | 53,481,497 | direct, `3 * 2^13` | 6,580,011 | 60,281,077 |
| 62 | 14,305, 14,304 | 12 | 4,095 | 23,636,121 | direct, `3 * 2^12` | 3,272,897 | 27,067,147 |
| 63 | 10,209, 10,208 | 12 | 4,095 | 23,636,121 | direct, `3 * 2^11` | 1,728,016 | 25,460,826 |
| 64 | 6,113, 6,112 | 11 | 2,047 | 10,310,505 | direct, `3 * 2^11` | 1,532,095 | 11,908,569 |
| 65 | 4,065, 4,064 | 10 | 1,023 | 4,423,265 | direct, `3 * 2^10` | 777,082 | 5,250,956 |
| 66 | 3,041, 3,040 | 10 | 1,023 | 4,423,265 | direct, `3 * 2^10` | 736,784 | 5,195,298 |
| 67 | 2,017, 2,016 | 9 | 511 | 1,855,213 | direct, `3 * 2^9` | 377,090 | 2,259,872 |
| 68 | 1,505, 1,504 | 9 | 511 | 1,855,213 | direct, `3 * 2^9` | 357,245 | 2,232,347 |
| 69 | 993, 992 | 8 | 255 | 753,667 | direct, `3 * 2^8` | 185,037 | 954,753 |
| 70 | 737, 736 | 8 | 255 | 753,667 | direct, `3 * 2^8` | 175,399 | 941,275 |
| 71 | 481, 480 | 7 | 127 | 297,845 | direct, `3 * 2^7` | 83,255 | 391,389 |
| 72 | 353, 352 | 7 | 127 | 297,845 | direct, `3 * 2^7` | 78,710 | 384,924 |

| row D component | operations |
|---|---:|
| repetitions 1-72 above | 2,561,608,651,995,420 |
| repetition 73: operands 225, 224, the lean half-gcd with `k = 112` (charge 707,447), the division and tests | 712,522 |
| the classical Euclid below degree 192 (111 steps, quotient test each) | 469,328 |
| driver entry (6 control operations and the table of the scales `1/2^a`: one allocation, 29 multiplications, 30 stores, the loop) | 399 |
| driver exit (the frees, the inversion of the leading coefficient, the normalisation) | 2,863 |
| stage bookkeeping 1,000, entry 1 + 11, exit 2, one free 105 | 1,119 |
| **total row D** | **2,561,608,653,181,651** |

The rows add up to row D; the scheme (c) products of stage D (4.4.1 item 6) are those of repetition 73: their scale fix per trial: 181 = 15 x 2 scheme (c) products (30) + 7 x 10 untwist calls (70) + loops 81.

## Appendix L: the line program `L` (this entry)

### L.1 Construction

`L(x) = F(x - E0_0) / OUTSCALE`, `F` the digest on the line of 2.2 (`W = tau^5`). The state after round 1 is `A + W B` (2.2: `alpha = A + c_2`, `beta = B`); the round-2 S-box input of lane `i` is `A_i + c_{2,i} + W B_i = B_i (W + E0_i)`, `E0_i = (A_i + c_{2,i}) / B_i` (every `B_i != 0` on the deployed constants). With `x = W + E0_0` lane 0 is `B_0 x` and lane `i` is `B_i (x + e_i)`, `e_i = E0_i - E0_0`: the program starts with `y1 = x + e1`, `y2 = x + e2` (2 additions) and holds lane `i` as `y_i` with the scale `B_i`. Every lane is held as its true value divided by a known nonzero scale: an S-box of a held lane is the true S-box output divided by the fifth power of the scale (3 multiplications), and the fifth powers are folded into the next linear layer, each output lane being held divided by its coefficient on `z0`: a dense layer with the next round's constants is `y_i = z0 + a_i z1 + b_i z2 + k_i` (2 multiplications, 3 additions per lane). Partial rounds use the sparse form of Grassi, Khovratovich, Rechberger, Roy and Schofnegger (USENIX Security 2021) with the same scaling, as in the r = 56 entries `3a1b25b6`, `9fb982e8` and `69e14209`: lane 0 is held as `lambda h0 + gamma`, lanes 1, 2 as `P (h1, h2) + q` with `P = Mww^j P0` after `j` partial rounds (`Mww` the lower-right 2x2 block of `M`) and `P0 = Mww^-r D`, `D` diagonal, so `P` is diagonal at the exit; one partial round is `u = h0 + k`, `x5 = u^5` (3 multiplications), `h0 = x5 + n1 h1 + n2 h2`, `h1 = h1 + v1 x5`, `h2 = h2 + v2 x5` (`h0` from the old `h1`, `h2`): 12 operations. Counts: entry 2; round 2 (S-boxes 9, dense layer with the round-3 constants 15); round 3 (S-boxes 9, into the partial form 6 multiplications and 6 additions, `D` normalising the `z0` coefficients); `r` partial rounds, 12 each; exit 3 (the round-60 constants); rounds 60-62 (24 each); round 63 (S-boxes 9, row 0 held divided by its `z0` coefficient `OUTSCALE`, 2 multiplications and 2 additions): `2 + 24 + 21 + 12 r + 3 + 72 + 13 = 135 + 12 r = 255`. Every constant is a closed formula of the deployed constants (the offline derivation of 6.2 prices the derivation of a literal; the 64 constants are derived once, offline, by the same rules, at most `64 * (2 * 330 + 40) = 44,800` field operations for the at most two inversions and the products of each, inside the declared cap of 6.2 together with its `137,169`).

### L.2 Check

`E0_0 = 0x3a4bd2e80f62c6cde67f816c4a67f17bbd43a70c4d2fca9784cc22ba736569ff`, `OUTSCALE = 0x2328f6536f89b0e16595d7b9e98c7e2c83f9f74bef9de0b6c7d854c5c3e4d885`. Our program (standard library only) builds `L` from the organizer constants file, executes it, and asserts `OUTSCALE * L(W + E0_0) = digest(message(W))` with the reference rounds of `verifier/poseidon.py` at 100 random `W` (r = 10; also r = 0, 1, 3, 9 with `135 + 12 r` operations); `message(W)` is the canonical pair of 2.2 (`tau = W^e`, `(U, V) = Q + tau (a, b)`, `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`). An independent construction of the same form for r = 56 (the 807-operation step of `69e14209`) gives the same `OUTSCALE` at r = 3 when its round count is set to 3 (checked at r = 3 only).

### L.3 Stage B

The loop of stage B and its charges are those of the base entry except that each evaluation is one execution of `L` (`255` operations) at `c' + s` and `c' - s` (`c' = c + E0_0`, one addition per trial); the values become `g_c / OUTSCALE`, which the normalisation to monic absorbs.

### L.4 Code and static data added to the footprint

`L` once, as a subroutine used by stage B: 255 instructions, and its 99 constants at 32 bytes; the call site in the stage-B loop (at most 20 instructions); stage E of Appendix S (at most 1,100 instructions, 4,400 bytes). At most `4 * 255 + 32 * 99 + 80 + 4,400 < 16,384` bytes at r <= 22; `16,384` are added to the footprint (section 7).

### L.5 Constants of `L` at r = 10

```
k0 = 0x3be50976ed9a36ed2193914455ff9b57110fbf67a5b17ed704b45f293ea16e52
k1 = 0x3f30a282c5b89b63ebabd204830a688ed50a9b6efae93b0434327bc6ee6794ba
k2 = 0x3c6619d59a8bff38f5e82d878afa1572b0de568df0f44727f5eebde8a520bb09
k3 = 0x182d2a33a05d2cf29f1f85fe18c296f96b485a4642bc47e0c096ed309334539d
k4 = 0x2ee7536394e8e06338e11ac0050022dbb3b058a98b297c7058173227f0c5f0b5
k5 = 0x2840fd97d3b51c865aebbadaaf03e4d7bb8a06a0ed729dcfdcb232668cc21036
k6 = 0x24d83320489d9f6acf96dd55a02381c22b9ae568c345217a4d3a3ebc6c68733e
k7 = 0x2ccbdb9536e63c46650cd03d3d3591a809a0e4a07b7c585b6e3b8c06db9ef42e
k8 = 0x37d59d01327c0e9ea9ea53e1bb643c6d9e2dd42b1be96d0ae502e5ad6685ef91
k9 = 0x3890183d51fa8d8e79f20615fc8cdc01a44e932c575a7833d6118362f946104a
k10 = 0x007ee07c6df20f7997f9b145f92b2e13ed55421ba5fd692e198160cbd4b2086e
k11 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k12 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
k13 = 0x371290fe8cfc2fde9e5c3c96eedb1c2b629003f65a736ce7de4a66689416afe0
k14 = 0x17c2419cbd4be24d33118d89881b8f4415a2c4b2587462f4c8dfbd18e97c75ae
k15 = 0x085e2bf516a28e562fc487c9a6797ac33739589ae9d25434d6d6021a9c68d2c3
k16 = 0x0395532f8a1a03fe06f359629ad81572a681e6c3f11fe4f95a8b176bcbb58bea
k17 = 0x34058bb8920441623716adeb0155288a2cca42fa34af13309820b9953e4336cf
k18 = 0x0d9cf43f72a120e5dfcefa6bc53b46ad197bf0de6eb9f56f465b362845efa4b0
k19 = 0x3d6f2faead111fd722e9781f22d25d05dc7a10c6286ce642aca361d146f7b658
k20 = 0x28b3281eadd833686cd9261304d7ec8c9da195e33438987b72b73182815447e0
k21 = 0x3fe69d8563f320f6db006a7e48d85b849b6250bb068fa4c338e424a6b1a420ff
k22 = 0x266144e217c50738f29b2b098b54686e360c94c1f64cc0b43c6b0a0cc37fc9eb
k23 = 0x0a49be03d40212df2fc9eb63fc6a9b540d8a635798cd4694dc6a286d006749f5
k24 = 0x3b02edaca295c5128c1fb70c12a1800d67c358872848102d6555b2e77b1ccc83
k25 = 0x355424441b8080743d93f8f21f2a18194f6f758a0e40c899e44676f45571eb00
k26 = 0x00777180357c08a136685e414d2d2da7864793e805921756edcc8a32aca4f27b
k27 = 0x1565f5ef914944ad12c16e36ec616abd4dd0f8c94d990dc4ff415ad5a506d732
k28 = 0x2e50dc1b527d63eaeb87439a295d88f2bdf63235008c96870bae00905ad00b58
k29 = 0x1e2540258433b80aa17f1140a60008e2a5e6b6b3c5f8d4564ac086efa3dbf5a2
k30 = 0x0ae4194249b681747774a68c08b3e33a8900df0ec80bb9247ffbea0e74d101be
k31 = 0x21529dae58bf19c4e637c457b035527cff5d327735c23bd2830cac716031cc22
k32 = 0x31f134c3cb80372eff4d98f34741c78bf04e38ca64691c338f55660789f29b61
k33 = 0x300901d881236c8a00fd718159f26037307e7b917b6f8454bd579f8d95bd4eb2
k34 = 0x3094568415e68d022977d9fd591741d0ca1b4a6bc5ac4d3a24bab190a97ebd88
k35 = 0x29c944371cb382c3354ac48078bd75282aa57a258442f89cc5de5f40690ebf80
k36 = 0x3fef15d8e084a94e64cf06704497b6d682243eb7718a1d0a0533ab73d96934f9
k37 = 0x2ca8302ed55720cd2a1b9478af5a5f4a223bd4fe9f778963e71519b2113aecb6
k38 = 0x0dd0be5e541057553e6d1db505c3e693960d90694c293e31aad805d59f9bccc9
k39 = 0x0e31f3e43729ae4876acdb568e2f30aab06a7dfffa2f8ccef8d9b1486b8d2623
k40 = 0x2f83f768ba7bf1166c89c4652fc26b8e702392af3dd1801ec1aa08dd50e6946a
k41 = 0x1fde0803c15099009b442410f2ce5533ebb576377ba2a5f4523740e584c3a6d8
k42 = 0x0fb74a39edbf99a426252d65ab2f5b558bfc999d3ec24ddad0ab5d3c66a49cba
k43 = 0x1751e70cf36166ffdceedb779da8547398b5392d407ce4c6080302d5ce967cf8
k44 = 0x058d2e96d4f9cbadad06102f79614f9a180aa6e3f151dcfd1bac95b2010e3767
k45 = 0x1e9b065f95cd399b9758a76bc6d9ccf319a42a30a7d8d9ca137971c03a7bcaf4
k46 = 0x111063df8c59e8b2b0fb801f33d8d5541688ad00ec672943a49547782e74e646
k47 = 0x0111ad1e97070de2c1edeeacffc3a8f1f81c885c649e20b3955b4a2fac77be23
k48 = 0x1175b7611fe6148467193d724955c2f1b5c5c82c3a95f3b0bf3cdeddf4f3de85
k49 = 0x190fc4caada6dc620c7618d520eee97e4e7c2a97505d6745acea09f2adc2ecd5
k50 = 0x391e585921ba44319c6905f6b9a2fb3d2306d8e2517eedf2f8f776d71994b7c1
k51 = 0x2c253ed553799ed5b4fd191c20717c3042333232c2f9e9237ac42fccc9f94f90
k52 = 0x193745c8d553088262dcb58e17e3468dd24422f6a3987ac69306c8d2935e7ff2
k53 = 0x0908d0b12537deef53b1ebdb322e65e8029ea0163ad4f17fd266a073d3cb7d5c
k54 = 0x17ce6d79d587fa5a5d103748f65d100ecff29f80fcceffb1a60ab9ac9b099331
k55 = 0x1e5a3cca2bc69f27fbc5324f88f977620200293e9b6321d7b9395ba804426e09
k56 = 0x25ae13cf74a7ef51ad1d6dcb5d96dac3a65e531b7a43d3383f3372ce4983160c
k57 = 0x35f659b85ed4e1f3c1c3e1f1fdde5ed7f9eb3b2b83d43f106d2416dba5965f7b
k58 = 0x10bb60fb76525d1bcf3185cc0e0f9026062bbef74b4cb1256524fa6d025d0f50
k59 = 0x022778c63482a47c789f3828a7222a80d89e9d77037d7da267aac56d9e8fcd4d
k60 = 0x0441dac341d9486b62d060a4dc584afdd4ecb303a10d06f21a26b8ecd9dbfb74
k61 = 0x20154d084ef86d769819e934c1d55da450ad4d7b3c870c35d3ac7a6040cb4c7d
k62 = 0x1fb04a7de4c56520f2aaf051fc8ec4eab6978daf4ad22c53ef4fde9bf6100f69
k63 = 0x07e4ea1ca9a246f62ad3773e66bb223f8b4335f3e32d6b6f17f9382ce100e9b5
k64 = 0x1dc4c74515ea0a91c81004be0217703d7012b234bfda34b6101ad08c8935419e
k65 = 0x21e3ac5797482938397c0b69a60942836172fd6a2802f3ef087c5973658d9f01
k66 = 0x0a5e9a44bc299a0b777b892499291eee5d70797471c03cb0d29cedb5f1d1f1df
k67 = 0x38bc91acba3154e91f55b9109bfe1d416cd31c5dae4882e47d5fe730806eed25
k68 = 0x1ad80fb8e4271d719d4e71310bb759986b3123ae4c7c8f174027feb68017a9c3
k69 = 0x004c19ca3d5d2b79ade163607096836bf6bdb82a603e7433835c74112f70a42f
k70 = 0x3f1df374c9b9f9648be997314faf7e3be24b1493a70c0635b5a2d82af5c3c63b
k71 = 0x304f82bcaa5268282e82feb517111471a2ab915fe273e2230ce323f6117c1939
k72 = 0x2c85a145c41c778b7535a740ecd1c54590dd779027bb8a3a7fc1a4971a18abb9
k73 = 0x242ac6ed349779f2c8d1dd575b39c392977e44aeca044ce6592719f5709aab15
k74 = 0x1b48b35e7f5a8e459282eae21aa50732af8d0149432bc4d8a855f5ae025a5a26
k75 = 0x07a7dcce0fad305623bb0c0d036696409dc768012aa568e03317b83230cfed7d
k76 = 0x09018f2da4f14a6fab8ecea1bfc1b4bd20e007d2c32a56b864028dd3f095299c
k77 = 0x0e4f089bc7f02e230ad3f8cf690a5faf9034f58d46b68a409928a03595e7df9e
k78 = 0x0101b4cd23520f2db5219b1e2a283d45bbfc804a2788243aa75271e690618107
k79 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k80 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
k81 = 0x0772abb6a5cadcd179734721de68ad5b5fbccdd78ac00c6f822d58a5f156c31f
k82 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
k83 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
k84 = 0x19be5bf2157b86a288db699355d48213d4d1ff1f9377f39b22e27748f4051c38
k85 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
k86 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
k87 = 0x30f5f0bbf647681806ff4a109a1813c16ee313578e8ef110cc3d1d099dbc2a52
k88 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k89 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
k90 = 0x010a56e1b167234694539ff1c4f6626afd3cd3b8fe36d26fdb2f8417fb1414dc
k91 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
k92 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
k93 = 0x2794d96d1a5461b4f78a4f457fe5361e7418d85be67af57d0403032e7b12feaf
k94 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
k95 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
k96 = 0x0276fda24ca2e130356993c7b2ac65716a9bd33eab3c8ff08028fac0956857b3
k97 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k98 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
```

### L.6 Listing of `L` at r = 10 (255 operations; `x` is input and output; `e1 = k0`, `e2 = k1`)

```
ADD y1, x, k0
ADD y2, x, k1
MUL s_z0, x, x
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, x
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k2
MUL t2, z2, k3
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k4
MUL t1, z1, k5
MUL t2, z2, k6
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k7
MUL t1, z1, k8
MUL t2, z2, k9
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k10
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k11
MUL t2, z2, k12
ADD h0, z0, t1
ADD h0, h0, t2
MUL t1, z1, k13
MUL t2, z2, k14
ADD h1, z0, t1
ADD h1, h1, t2
MUL t1, z1, k15
MUL t2, z2, k16
ADD h2, z0, t1
ADD h2, h2, t2
ADD u, h0, k17
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k18
MUL t2, h2, k19
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k20
ADD h1, h1, t1
MUL t2, x5, k21
ADD h2, h2, t2
ADD u, h0, k22
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k23
MUL t2, h2, k24
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k25
ADD h1, h1, t1
MUL t2, x5, k26
ADD h2, h2, t2
ADD u, h0, k27
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k28
MUL t2, h2, k29
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k30
ADD h1, h1, t1
MUL t2, x5, k31
ADD h2, h2, t2
ADD u, h0, k32
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k33
MUL t2, h2, k34
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k35
ADD h1, h1, t1
MUL t2, x5, k36
ADD h2, h2, t2
ADD u, h0, k37
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k38
MUL t2, h2, k39
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k40
ADD h1, h1, t1
MUL t2, x5, k41
ADD h2, h2, t2
ADD u, h0, k42
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k43
MUL t2, h2, k44
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k45
ADD h1, h1, t1
MUL t2, x5, k46
ADD h2, h2, t2
ADD u, h0, k47
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k48
MUL t2, h2, k49
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k50
ADD h1, h1, t1
MUL t2, x5, k51
ADD h2, h2, t2
ADD u, h0, k52
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k53
MUL t2, h2, k54
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k55
ADD h1, h1, t1
MUL t2, x5, k56
ADD h2, h2, t2
ADD u, h0, k57
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k58
MUL t2, h2, k59
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k60
ADD h1, h1, t1
MUL t2, x5, k61
ADD h2, h2, t2
ADD u, h0, k62
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k63
MUL t2, h2, k64
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k65
ADD h1, h1, t1
MUL t2, x5, k66
ADD h2, h2, t2
ADD y0, h0, k67
ADD y1, h1, k68
ADD y2, h2, k69
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k70
MUL t2, z2, k71
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k72
MUL t1, z1, k73
MUL t2, z2, k74
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k75
MUL t1, z1, k76
MUL t2, z2, k77
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k78
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k79
MUL t2, z2, k80
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k81
MUL t1, z1, k82
MUL t2, z2, k83
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k84
MUL t1, z1, k85
MUL t2, z2, k86
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k87
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k88
MUL t2, z2, k89
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k90
MUL t1, z1, k91
MUL t2, z2, k92
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k93
MUL t1, z1, k94
MUL t2, z2, k95
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k96
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k97
MUL t2, z2, k98
ADD x, z0, t1
ADD x, x, t2
```

## Appendix S: stage E, register-resident (this entry)

Input `G` monic, `1 <= d = deg G <= 16`, a product of distinct linear factors over `F_p` (4.3G). If `d = 1` the root is `-G_0`. Otherwise `H := G` (loaded into field registers) and at most `Z = 64` rounds:

1. draw `a` (63, two words, 4.1.1) and test it (5);
2. `B := (X + a)^((p-1)/2) mod H`: start `B = X + a` (3), then for each of the 253 bits below the top bit of `(p-1)/2` one squaring modulo `H` and, on the 45 one-bits, one multiplication by `X + a` modulo `H`;
3. `B := B - 1` (1);
4. `T := gcd(H, B)` monic, by inversion-free elimination: while the second row is nonzero, order the rows by degree and replace the higher row `A` by `lc(B) A - lc(A) X^(deg A - deg B) B` (its top coefficient cancels; at most `3 d` field operations, 6 control, 3 for the ordering), strip zero top coefficients (2 each); then one inversion of the leading coefficient by square-and-multiply on the 254 bits below the top bit of `p - 2` (76 one-bits: 254 squarings and 76 multiplications, 4 control per bit) and `d` multiplications;
5. keep `T` if `1 <= deg T < deg H`, else keep `H` (6); stop with the root `-H_0` when `deg H = 1`.

Charges at degree `d` (field operations 1 each; every operand is a register: `H` (`d` words), `B` (`d`), the square (`2d - 1`) and the two gcd rows (`2d + 1`), at most 100 field registers with the shift and the loop registers; no load or store inside a round):

* squaring modulo `H`: the `d (d - 1)/2` cross products, accumulated per slot (`d (d - 1)/2 - (2 d - 3)` additions), doubled (`2 d - 3`), the `d` squares and their `d - 2` additions to the cross sums of even slots, and the reduction of the `d - 1` top coefficients (`2 d` each): `S(d) = d (d+1)/2 + d (d-1)/2 - (2d - 3) + (2d - 3) + (d - 2) + 2 d (d - 1)`, `S(16) = 750`, plus 4 of bit control;
* multiplication by `X + a` modulo `H`: `4 d` (per coefficient one product with the top coefficient, one subtraction, one product by `a`, one addition);
* gcd: at most `2 d - 1` eliminations (each lowers the sum of the two degrees), `(2 d - 1)(3 d + 9) + 2 (2 d + 1)` with the strips, the inversion `254 * 5 + 76 = 1,346` and `d`: `3,195` at `d = 16`.

`R(d) = 68 + 3 + 253 (S(d) + 4) + 45 * 4 d + 1 + gcd(d) + 6`, non-decreasing in `d`; `R(16) = 68 + 3 + 190,762 + 2,880 + 1 + 3,195 + 6 = 196,915`. Row E charges every one of the 64 rounds at `d = 16`: `64 * 196,915 + 1,000 + 200 = 12,603,760`. The procedure was executed with this counter on random products of distinct linear factors of degree 2 to 16 over `F_p` (175 rounds): every run isolated a true root, and the largest charge of a round at degree 16 was `195,817 <= R(16)`. The isolation bound of 9.4 applies to this procedure (the rule of step 5 separates a pair whenever its two characters are nonzero and different).
