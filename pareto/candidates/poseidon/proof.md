# Orchard Poseidon, r = 13: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, half-gcd, one centre; stage B on column passes (this entry)

## 1. Claim

Target: `poseidon-orchard-r13-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, thirteen partial rounds 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 and 16, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

**This entry's change (stage B on column passes; Appendix B2).** This package is `b8f4c780` (mpjunior92, time + memory penalty 81.48491) taken from its evaluated commit and edited in place, so the line numbers before the appendices are preserved. One change, in row B only: the `1481` inverse transforms of size `6,442,450,944` and the four transforms of length `S = 3,072` per position of the geometric solve are run as the column passes of section 4.2 (the kernels `ob2` to `ob128` and `ob3` of stage C, with their call, kernel and loop charges), the inverse transforms across the cosets (cnt = `1481`) and the solve in groups of `1,024` positions; the point loop stores in natural order (no bit-reversed index). The interpolation itself (section 3) is unchanged. Row B `8,795,496,609,191,077` (was `15,833,147,877,225,909`), `N_max = 1,409,170,237,589,955,182` (was `1,416,207,888,857,990,014`), `time_log2 = 51.35587` (was `51.36305`), `memory_log2_bytes = 50.12186` (the solve buffers, 134,807,552 bytes, added as term (e) of section 7), time + memory penalty `81.47773` (was `81.48491`). Every other row, the premises, the success bound and the experiments are those of `b8f4c780`. Authorship. This package is the r = 13 entry `a0f3fd39` (Jbenisek) with two changes made by the base entry `b8f4c780`, both in low-order rows: (i) every line evaluation of stage B is the straight-line program `L` of Appendix L (`135 + 12 r = 291` field operations: scaled lanes and sparse partial rounds in the form of the r = 56 entries `3a1b25b6`, `9fb982e8`, `69e14209`, re-derived and checked by our own program) in place of the `C(13) = 489` operations charged per evaluation; the loop around the evaluations is otherwise unchanged, so row B loses exactly `19,082,539,696,128 * (489 - 291) = 3,778,342,859,833,344` (section 6); (ii) stage E keeps its polynomials in field registers and charges every field operation once, with an inversion-free gcd (Appendix S), row E `12,603,760` in place of `166,079,773`. Stages A, C, D, F and G, the arena, the premises, the success bound and the experiments are those of `a0f3fd39` unchanged; text that says "our" entry or "we" outside the changed parts refers to the authors of `a0f3fd39`. Where the text of `a0f3fd39` describes a line evaluation by the charge `C(r)`, this entry runs `L` (`L(x) = F(x - E0_0) / OUTSCALE`, Appendix L; evaluating `L(c' + s) - L(c' - s)` with `c' = c + E0_0` gives `2 s g_c(s^2) / OUTSCALE`, and the normalisation to monic removes the constant). Totals: `N_max = 1,416,207,888,857,990,014` (was `1,416,207,888,857,990,014`), `time_log2 = 51.36305`, `memory_log2_bytes = 50.12186` (`1,225,130,838,019,052` bytes: `16,384` bytes of code and static data added for `L`, its constants and stage E), normalized cost `81.48491` (was `81.48876`). This entry is an algorithm (sections 2-4) with a worst-case operation count (sections 6-7) and a success probability derived from the premises `H-ONE` (section 9.1) and `H-NORMAL` (section 9.5), statements about the usable roots of the fixed digest polynomial and its remainder sequences; section 9.2 derives the success probability from them with explicit constants.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and 1481 inverse transforms (one per coset, section 3), compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod in the value domain (section 4.6, the method of bradcush 1aa56884) and a half-gcd in the lean form of 1aa56884 (4.4.1), and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the one centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta + delta_C)^K - K (eps_iso + eps_coin) = q - delta - delta_C - eps_iso - eps_coin` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1: at least `0.3931 p` centres have between 1 and `DMAX = 16` usable roots), `delta = 0.003` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `delta_C < 2^-166.8` the stage-C zero test (proved, 9.2(b)), `eps_iso <= P[Bin(64, w) <= 3] = sum_(j <= 3) C(64, j) w^j (1 - w)^(64 - j) = 2.371e-15 < 2^-48` (each isolation round halves `deg G <= 16` with probability at least `w = 1/2 - 7.869e-40` whatever came before, and four halvings reach degree 1; lemma 9.4), `eps_coin < 2^-128`. The exact value is `0.390099999999997615`. The value of `q` is `0.3934693 - 0.3931 = 0.0003693` below `1 - e^(-1/2) = 0.3934693` (and `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound), the law of the usable roots in section 9.3, which is a theorem for the first two and three S-box layers on the deployed constants (9.3(c)).

* `time_log2 = 51.35587` in target-compression units (`C(13) = 489` primitive operations per unit): the worst-case operation count, derived in section 6 as `T_fixed + K * T_trial` with every trial charged in full (stage D for the normal remainder sequence, which bounds every trial because a trial with any other sequence ends after a prefix of that work, section 6.3; stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 1,409,170,237,589,955,182` operations, `log2(N_max / 489) = 51.3558609628`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is counted exactly, `T_off = 136,785` operations, and charged at its declared cap of 1,000,000 operations; that cap is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 50.12186` (`1,225,130,838,019,052` bytes: the footprint of `a0f3fd39`, `1,225,130,838,002,668` bytes, plus `16,384` bytes of code and static data for `L`, its constants and the register-resident stage E, section 7). This entry adds the stage-B solve buffers, `134,807,552` bytes (section 7, term (e)): footprint `1,225,130,972,826,604` bytes.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `65` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^19`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against our r = 13 entry `a9505ae2` (time + memory penalty 81.59808; the same package is also entry `c8a548bf`; it has the stage-D block lengths `3 * 2^b` and the 256-word register file of the next two bullets): the eight-position loops of the column kernels and the two-row node product of the next bullet (time + memory penalty 81.49853 with them alone, staged, not filed) and two block-form changes (4.2): group 0 of each block-form pass runs a variant without the multiplications by twiddle 1 (`2^k - 1` butterflies per block at 2 operations, 3 control operations more per pass), and the block loop of a group is written four blocks per pass (3 of control per block, was 5). Row C `900,591,793,083,154,699` (was `900,936,145,465,628,772`), row D `499,782,930,700,487,073` (was `508,947,982,108,876,658`); arena `1,225,130,832,311,296` bytes (was `1,225,165,462,582,272`); term (a) `363,008` bytes more code (7(a)); memory_log2 `50.12186`, rounded up at five decimals (was `50.122` at three). Every other charge, the premises and the experiments are unchanged.
* Against our r = 13 entry `51f21390` (time + memory penalty 81.69936): the change of the next bullet (time + memory penalty 81.68086 with it alone) and the register file of the machine is 256 words of 256 bits (was 64), counted in the memory (7(d)), as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits: the column passes of stage C and of the outer transforms of stage D take up to seven layers (`ob64`, `ob128`) and the block-form passes of the products up to seven layers (blocks of 128 points with their 127 twiddles in registers); 4.2; every column pass runs its position loop eight positions per pass, with the loop control `F(cnt) = 1 + 3 floor(cnt / 8) + 2 + 3 (cnt mod 8) + 2` per call in place of 3 per position (our r = 17 entry `8346be35`; 4.2, 4.6); the product step `M = M1 [[Q, 1], [b^2, 0]] M2` of each half-gcd node runs on the two rows `Y - 1`, `Y + 1` (`2n` points) in place of three; its entries have degree at most `2n - 1` on the normal sequence (van der Hoeven, arXiv 2212.12389, Prop. 7; 4.4). Row C `900,936,145,465,628,772` (was `993,188,394,886,063,505`), row D `508,947,982,108,876,658` (was `609,277,230,454,279,005`); arena `1,225,165,462,582,272` bytes (was `1,225,135,265,821,696`), memory_log2 unchanged. Every other charge, the premises and the experiments are unchanged.
* Against our r = 13 entry `51f21390` (time + memory penalty 81.69936, the same algorithm and package): stage-D block lengths `3 * 2^b`: the block products of stage D in scheme (c) take their block length from `3 * 2^b` (b = 5..31) as well as `2^b` (b = 6..31), whichever has the least charge; a block of `3 * 2^b` coefficients is transformed with `3 * 2^(b+1)` points, the radix-3 stage and three rows of radix-2 passes with the kernels and charges of the transforms of `3 * 2^32` points (4.5); 4.4.1 item 6. Row D `609,277,230,454,279,005` (was `630,212,367,639,217,250`), row C unchanged; arena `1,225,135,265,821,696` bytes (was `1,225,130,832,311,296`), memory_log2 unchanged; on an 18-register machine `1,996,311,701,168,937,977` (time + memory penalty 81.98136). Every other charge, the premises and the experiments are unchanged.
* Against our r = 13 entry `e92c329e` (time + memory penalty 81.78139, the same algorithm and package): three kernel changes. (i) A column-kernel butterfly whose twiddle is 1 is charged 2 operations (its call at offset 0 a straight-line variant, 4.2). (ii) The block-form passes take up to five layers (blocks of 32 points; 32 data words, 31 twiddles and the temporary, within the 64 words of the declared file, as `ob32`; 4.2). (iii) In the extensions of the loop the radix-3 pass of the inner transforms is made in the copies of the geometric phase (Winograd 3-point form, 8 operations per triple; groups of `3 * 2^10` positions; 4.6). Row C `993,188,394,886,063,505` (was `1,065,474,079,879,478,492`), row D `630,212,367,639,217,250` (was `654,051,839,407,993,186`); the live-set peak `1,223,000,830,647,680` bytes (was `1,223,000,629,321,088`): the group buffer of `3 * 2^10` rows of `3 * 2^10` elements, `301,989,888` bytes (was `100,663,296`, `2^10` rows), a slab-class block; the pool `1,223,000,528,559,360` bytes and the slab area `2,130,303,734,912` bytes are unchanged (section 7), so arena and memory_log2 are unchanged; on an 18-register machine `2,022,989,054,388,419,617` (was `2,096,201,468,255,049,462`). Every other charge, the premises and the experiments are unchanged.
* Against our r = 13 entry `d0b0971b` (time + memory penalty 81.95041, the same algorithm and package): step (1) of each matrix-only node of stage D with `2^7 - 1 <= 2^j - 1 <= 2^37 - 1` runs the inversion-free half-gcd on three rows of bradcush `4bcabff8` (4.4.1 item 9): row D `654,051,839,407,993,186` (was `856,703,029,462,603,064`), row C unchanged; arena `1,225,130,832,311,296` bytes (was `1,233,206,170,896,192`): the pool `1,223,000,528,559,360` bytes (was `1,231,694,342,337,984`), its high-water mark now reached in stage C, and the slab area `2,130,303,734,912` bytes (was `1,511,828,541,184`) (section 7); memory_log2 50.122 (was 50.132). Every other charge, the premises and the experiments are unchanged.
* Against our r = 13 entry `e9f1ae43` (time + memory penalty 82.02995, the same algorithm and package): the loads and stores of the block-form passes of 4.2 are charged one operation each (base plus index, as the column kernels `ob4` to `ob32`): row C `1,065,474,079,879,478,492` (was `1,067,475,857,621,007,500`), row D `856,703,029,462,603,064` (was `964,769,222,939,172,588`); memory unchanged. Every other charge, the premises and the experiments are unchanged.
* Against our r = 13 entry `e7142668` (time + memory penalty 82.09714, the same algorithm and package): the transform passes of the products of stages C and D (all but the fused pass of each product) run in the block form of our r = 3 entries `ef123c2b` / `253629b9` (per group the `2^k - 1` twiddles held in registers), on the 64-word register file stated as a restriction in claim.json: row C `1,067,475,857,621,007,500` (was `1,069,303,936,242,444,786`), row D `964,769,222,939,172,588` (was `1,060,764,714,659,505,398`); arena `1,233,206,170,896,192` bytes (was `1,233,206,170,871,616`). Every other charge, the premises and the experiments are unchanged. On an 18-register machine (column passes of at most 3 layers and leaf passes) the count is `N_max = 2,362,810,413,434,183,447` (time + memory penalty 82.23352).
* Prior entry: this entry is the r = 13 version of our r = 7 algebraic entry 05a41d88 (the same algorithm, ledger method, premise structure and evidence design). The ruling on 05a41d88 (not_evaluable on the experiments lane) is answered here in the same way: the organizer experiments `line-ladder-w6`, `-w8`, `-w10` and `-w12` on the antipodal line pairs of this construction at r = 13 (10.2), the computations of Grok job 136 and their re-run on the deployed constants and the construction's line (10.3), and the measurement of the Euclidean sequences on the sibling targets (10.5). Stage C is the value-domain powering of bradcush's entry 1aa56884 (section 4.6), stage D its lean half-gcd (4.4.1), and stage D is charged for the normal remainder sequence under the premise `H-NORMAL` of bradcush (entries e6dcb600, 1aa56884) with gta6rp's allowance and organizer-run tests (9.5); all credited in the dependencies and the note.
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1) and `H-NORMAL` (score-critical for the success probability only, section 9.5). Both are statements about probability. `H-NORMAL` is bradcush's premise (entries e6dcb600 and 1aa56884), stated here with the allowance `delta = 0.003` and supported by organizer-run normality tests, the recipe of gta6rp's entries (42dec7f5 at this round count); the test program `experiments/exp_euclid.py` is our own (10.5.1). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2 on the machine stated as a restriction in claim.json (256 field registers of 256 bits plus 131 integer address registers; every load, store and spill counted), as the accepted entries `89b451ff` and `fb176310` state theirs and as our r = 3 entries `ef123c2b` and `253629b9` do, and the base-plus-index addressing of the stage-C column kernels (4.2), stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation. Everything else is proved or counted here: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the success bound (section 9.2), the stage-C zero-test bound (9.2(b)), the isolation lemma (section 9.4), the uniformity of the centre, the cap rules and every operation count (sections 4, 6, 7).
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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 (partial), 60, 61, 62, 63 (full) put nineteen S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^19 = D = 19,073,486,328,125`. The leading coefficient is obtained by
propagating leading coefficients through the nineteen layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x04db8dee80118dfda8dbd9e674b73b3122a28ff42d6a7d902c37b159f4d5cec2`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 9,536,743,164,062`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. At this r no transform of `H >= m + 1` points exists: `p - 1 = 2^32 * 3 * q` has roots of unity of order `3 * 2^a` for `a <= 32` only, and `m + 1 = 9,536,743,164,063 > 3 * 2^32`. Let `B = 3 * 2^31 = 6,442,450,944`, `zeta` a primitive `2B`-th root of unity (`2B = 3 * 2^32` divides `p - 1`) and `omega = zeta^2`, a primitive `B`-th root. Let `kappa = ceil((m + 1) / B) = 1481`, `v_k = 2^k` and `u_k = v_k^2 = 4^k` for `k < kappa`, and `z = 4^B`; the `kappa` numbers `n_k = u_k^B = z^k` form a geometric progression and are pairwise distinct, because the order of `z` exceeds `kappa` (`z^d != 1` for every divisor `d` of `p - 1` up to `2 * 10^8`, and `kappa < 2 * 10^8`). The evaluation points are `s_{k,i} = v_k zeta^i` for `k < kappa`, `i < B`, so that `S_{k,i} = s_{k,i}^2 = u_k omega^i`, and `g_c(S_{k,i}) = (F(c + s_{k,i}) - F(c - s_{k,i})) / (2 s_{k,i})`. Write `g_c(x) = sum_{t < kappa} x^{tB} h_t(x)` with `deg h_t < B`. For `y = omega^i` we have `y^B = 1`, hence `g_c(u_k y) = w_k(y)` with `w_k(y) = sum_t n_k^t h_t(u_k y)`, a polynomial of degree `< B`. One inverse transform of size `B` of the values `(g_c(S_{k,i}))_i` returns the coefficients `w_k[j] = u_k^j sum_t n_k^t h_t[j]`. After multiplication by `u_k^{-j}`, for every `j < B` the numbers `W_k[j] = sum_t n_k^t h_t[j]` (`k < kappa`) are the values of the polynomial `h^(j)(X) = sum_t h_t[j] X^t` at the nodes `z^k`, and its coefficients `h_t[j] = g_c[j + tB]` are recovered from them by two correlations of length `kappa` (Lagrange interpolation at geometric nodes, the chirp-z form). Let `M(X) = prod_k (X - z^k) = sum_i mu_i X^i`; the q-binomial theorem gives `mu_{kappa-j} = (-1)^j z^{j(j-1)/2} [kappa choose j]_z`, and `M'(z^k) = z^{k(k-1)/2 + k(kappa-1-k)} prod_{j <= k} (z^j - 1) prod_{j <= kappa-1-k} (1 - z^j)`. With `a_k = W_k[j] / M'(z^k)` and `A(i) = sum_k a_k z^{ki}` (`i < kappa`) we have `h_t[j] = sum_{i > t} mu_i A(i - t - 1)`. Since `z^{ki} = z^{C(k+i,2) - C(k,2) - C(i,2)}` with `C(n,2) = n(n-1)/2`, `A(i) z^{C(i,2)}` is the correlation of the sequence `a_k z^{-C(k,2)}` with the chirp `z^{C(n,2)}` (first correlation), and `h_t[j]` is the correlation of `A` with `(mu_1, ..., mu_kappa)` (second correlation). Each correlation is one cyclic convolution of length `S = 3,072` (the smallest `2^a` or `3 * 2^a` that is at least `2 kappa - 1`), done with the transform of length `S` (forward, pointwise product, inverse); the transforms of the fixed sequences (the chirp and `mu`) and the constants `mu_i`, `1/M'(z^k)`, `z^{-C(k,2)}` are computed once per trial and shared by the `B` positions `j`. The `2 kappa B = 19,082,539,696,128` evaluations of `F` are each charged as one target-compression unit (`C(13) = 489` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation. The loop work, the inverse transforms and the solve are charged as in Appendix B2 (this entry): the point loop runs in natural order (per point the two additions for the points, the subtraction, the multiplication by `1/(2 s_{k,i})`, the two multiplications of the recurrences of `s_{k,i}` and `1/(2 s_{k,i})`, one store at `i * kappa + k` with its address operation and 3 of loop control: `2 * 291 + 11` with the two evaluations), the `kappa` inverse transforms of size `B` are made together as column passes across the cosets (decimation in frequency, natural order in, transform order out), and the solve is made in groups of `1,024` positions (slots) in a group buffer of `S` rows: gather with the factor `c_k (4^(-j))^k` (`c_k = z^(-C(k,2)) / M'(z^k)`; `W_k[j] = (4^(-j))^k w_k[j]` because `u_k^(-j) = (4^(-j))^k`), first correlation (forward transform of length `S`, product by the chirp spectrum, inverse transform), rows `i < kappa` times `z^(-C(i,2)) / S`, second correlation (forward transform, product by the spectrum of `(mu_1, ..., mu_kappa)`, inverse transform), scatter of `h_t[j]` to `g[j + tB]` with `1/S`; every transform on the column passes of section 4.2 (no pruning, no twiddle-1 saving); the once-per-trial constants and the normalisation are counted there as well.

## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (19,082,539,696,128 evaluations + 1481 inverse NTTs of size 6,442,450,944 + the geometric solve of the 1481 cosets (two correlations of length 3,072 per position) + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; value domain, section 4.6: from S^v, v = 2^40; 213 squaring steps, 45 of them also multiply by S, pointwise)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (489 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 43 bits after the leading one are zero, so the algorithm starts from the monomial `S^v` with `v = 2^40` (a multiple of `2^32`, the power of two in `h`, below m, 4.6, `VSHIFT = 3`; 40 + 213 = 253), and the loop of stage C has 213 steps, of which 45 also multiply by `S` (pointwise).

Stopping rule. The loop bound `K = 1` is a constant of the algorithm: one centre is tried. A trial is run to its end, or to an ABORT of stage D on an abnormal remainder sequence (6.3) or of stage C on a zero of g on O1 (4.6 step 5), which then resets the allocator and draws the next centre; the claim charges every trial at its maximum (stages E to G at their worst case, section 6), so a trial that fails early is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3, 4.4), the powering has a fixed number of steps, and the half-gcd has a fixed recursion: 37 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 4,768,371,582,031` and is halved, rounded up, until it is at most 96) and at most 37 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 9,536,743,164,062 to at most 192). Hence, with stage D charged for the normal remainder sequence and every other sequence ending its trial after a prefix of that work (section 6.3), the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success, by an ABORT of a trial (the next centre is then drawn), or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

The only randomness of the algorithm is the cost model's random-word primitive (fresh independent algorithmic coins): an independent uniform 256-bit word, each use returning a fresh word, uniform on `0..2^256-1` and independent of everything else, and costing one operation. **Probability space:** every probability of section 9 is over these words. A draw is one fresh word `y`; the draw is `x = y mod p`, computed by at most three steps `if y >= p then y := y - p` (`y < 2^256 < 4p`, so three steps bring `y` below `p`). Write `2^256 = 3p + s0` with `0 < s0 < p`: the residues below `s0` have exactly four preimages below `2^256` and the other `S3 = p - s0 = 4p - 2^256` residues have exactly three, so `P[x = z] = 4/2^256` or `3/2^256` for every residue `z`, every residue has probability at least `3/2^256`, and all but `S3` residues have probability `4/2^256`. The draw is within statistical distance `S3 (1/p - 3/2^256) = 1.574e-39 (2^-128.90) < 2^-128` of uniform on `F_p`. A draw costs 31 operations: for the word one random-word operation, one load, one store into the cell `y` and three control operations (two addresses, the increment of the word index), 6 in all; for the reduction three steps each of a comparison, a conditional branch and a field subtraction (9 operations), with the loop control of 3 per iteration and 2 on exit (11); one Montgomery conversion of `x` (1); the entry of the call (2) and the address of `y` (2). Draws are made once per trial for the centre and once per isolation round for the shift: at most `K (1 + Z) = 65` draws, `65` words. No word is used twice, and the number of words used before a draw depends only on earlier words, so each draw is independent of the earlier course of the algorithm.

#### 4.1.2 Stage E: isolating a root of G

`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). The roots `r` of `G` are the usable `S`. While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw `a` (a draw as in 4.1.1; if it is 0, `a := 1`, since the Taylor shift uses `1/a`; the zero test is 5 operations and the replacement 2, charged in every round), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds: a round separates two given roots for at least `(p-3)/2` shifts, so it halves the degree with probability at least `w = 1/2 - 7.869e-40`, and four halvings take `16` to `1`; the failure probability is at most `P[Bin(64, w) <= 3] = 2.371e-15`, a finite sum, no premise.

### 4.2 Machine model and charging rules

Every operation of the algorithm is counted where it executes; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation). Exception, the column kernels `ob4`, `ob8`, `ob16`, `ob32`, `ob64`, `ob128`, `ob4m` and the two boundary passes of the loop of stage C (4.6), and the `ob4`, `ob8`, `ob16`, `ob32`, `ob64` and `ob128` passes of the outer transforms of stage D (4.4.1 item 6): each load or store is 1 operation with no address operation. An element of the call's block at the position `j` is addressed as row base plus position offset, and a twiddle or spectrum word of the call as the table base plus the call's index scaled by a constant of the layer, the base-plus-index addressing of the load itself; the `2^k` row bases and the twiddle address are formed once per call (in the call charge `2 * 2^k + 6`, which is added to the kernel's per-call constant below; neither contains the other) and held in integer registers, and the position offset advances with the index update of the loop step. Everywhere else (the rest of stage D, the `ob2` and `ob3` passes of both stages and the first and last passes of an extension of stage C included) the address operation is charged as above.
* every loop: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). Loops over the elements of an array written eight elements per pass (the pointwise, copy, fold and subtraction loops of the powering and of the products) are charged 3 per pass of eight, 1 for the bound, 2 when the main loop is left, and 3 per iteration for the remaining 0 to 7 elements.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, comparison, conditional branch, assignment of a register, and the selection of an element of the register block (at most 32 data words) by a computed index. Data-dependent tests are charged per executed test.
* index arithmetic uses only shifts, additions, subtractions, comparisons and branches (the benchmark's primitive list has no integer multiplication, division or modulo): a multiplication by a power of two is a shift, by 3 or 5 a shift and an addition, and a product of an index and a stride is a running sum; each is charged as a control operation where it occurs.
* transforms: a transform of size `3 * 2^a` is a twiddle-free radix-3 stage (8 operations per leaf) followed by three rows of radix-2 passes of at most seven layers (the layers of these passes of a product are taken seven at a time, the remainder in its first forward and its last inverse pass). A pass works on blocks of `2^k <= 128` points held in registers, in the block form of our r = 3 entries `ef123c2b` and `253629b9` (their `pd_fwdp`, `pd_invp`): per block its `2^k` loads and `2^k` stores (1 each: a block element is addressed as the table base plus its index, the base-plus-index addressing of the load or store itself, as for `ob4` to `ob128` above; one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`), `k 2^(k-1)` butterflies at three field operations each (two in group 0 where the twiddle is 1, below) and 3 of control (the block loop of a group is written four blocks per pass: per block 2 operations that form its addresses and per pass of four blocks 3 of loop control, `2 + 3/4 <= 3`; a group of one or two blocks runs them in line, with no loop); per group its `2^k - 1` twiddles formed and held in registers for all its blocks (24 operations for `k = 4`: two loads with their addresses, one multiplication, three squarings, eleven multiplications by register constants and control; 16 for `k <= 3`; for `k = 5, 6, 7` its `2^k - 1` twiddles are loaded from the twiddle table, 1 each (base plus index, as for `ob32`), with 9 operations of address formation and control, `2^k + 8`: 40, 72, 136); per pass `5 + (9k + 2) + 12` (forward) or `6 + (9k + 2) + 12` (inverse) of pass set-up. Group 0 of a pass (its `2^(a-k-l0)` blocks for a pass of `k` layers from layer `l0` of a row of `2^a` points) runs a variant of the block body without the multiplications by its twiddle 1: in the pass layer with `2^j` distinct group twiddles (`j = 0..k-1`) the twiddle of group 0 is 1 on `2^(k-1-j)` of the `2^(k-1)` butterflies of a block, `2^k - 1` per block, each its addition and subtraction, 2 operations (the convention of the column kernels below and of 1aa56884); the variant adds 3 control operations per pass. The one pass of a product that fuses its last forward layers, the pointwise product and its first inverse layers keeps the charge of a leaf pass: each butterfly is three field operations (none for the multiplication when the twiddle is 1), each twiddle is one load with its address operation and one addition to its pointer: the first twiddle of each layer of a block is read at a running pointer of that layer, which then steps by the layer's stride (one addition; one subtraction in an inverse pass), and each further twiddle of the layer at the previous one plus a fixed offset (one addition or subtraction). Per pass the strides are formed once (one shift per layer; an inverse pass also forms the top of the table, 2 operations, and adds the scale shift to each layer, 1 more per layer) and 1 operation forms the number of blocks of a group after block 0; per group, block 0 (whose twiddles are 1) is followed by the pointers of block 1 (one addition or subtraction per layer) and the address of block 1 (1). The other blocks of the group run eight per pass of a loop with a straight-line body, each with 1 operation that advances the block address; the block loop is charged 1 for its bound, 3 per pass of eight, 2 when the main loop is left, 3 per remaining block (0 to 7) and 2 when the second loop is left, and the group loop 3 per group and 1 for the base of the next group. The register file is the machine restriction of claim.json: one register file of 387 words, 256 field registers of 256 bits plus 131 integer (address) registers (as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits), counted in the memory (7(d)), every other value charged as a load or store (a block-form pass uses at most 256: the 128 data words, 127 twiddles and the butterfly temporary, as `ob128`; the fused leaf pass 18: the 16 data words, the twiddle operand and the butterfly temporary; the pass `ob128`, in stage C and in the outer transforms of stage D, uses 256: 128 data words, 127 twiddles and the butterfly temporary), and the 131 integer registers of the file in a call of `ob128` (the 128 row bases, the twiddle address, the position offset and the loop bound; fewer in the smaller kernels); the fused leaf pass of `k <= 4` layers holds its `k` running twiddle pointers and `k` strides in integer registers. Stage C (4.6) and the outer transforms of stage D (4.4.1, item 6) use column kernels: a column pass of `k` radix-2 layers (`k <= 7`) runs over `2^k` rows at `cnt` positions and keeps its `2^k - 1` twiddles in registers for the whole position loop (`ob8`: 8 data words, 7 twiddles and the butterfly temporary, 16 of the 18 words; `ob4`: 4 + 3 + 1). Per position it loads `2^k` elements, makes `k 2^(k-1)` butterflies at 3 operations each (2 where the twiddle is 1, below) and stores `2^k` elements; its position loop is written eight positions per pass (the positions of a pass are addressed by the position offset plus the constants 0 to 7 in the loads and stores themselves, and the offset advances once per pass), so its loop control is `F(cnt) = 1 + 3 floor(cnt / 8) + 2 + 3 (cnt mod 8) + 2` per call, not 3 per position; each load or store is 1 (base-plus-index, above), in stage C and in the outer transforms of stage D alike. Charges: `ob128` `269 + 1600 cnt + F(cnt)`, `ob64` `139 + 704 cnt + F(cnt)` (per call their 127 or 63 twiddles loaded at 2 each, a load with its address operation, 3 of control and 2 per layer after the first: `269 = 254 + 3 + 12`, `139 = 126 + 3 + 10`; per position `2^k` loads and `2^k` stores, `k 2^(k-1)` butterflies at 3 : `1600 = 256 + 1344`, `704 = 128 + 576`), `ob32` `34 + 304 cnt + F(cnt)`, `ob16` `18 + 128 cnt + F(cnt)`, `ob8` `10 + 52 cnt + F(cnt)`, `ob4` `6 + 20 cnt + F(cnt)`, and for the radix-3 stage and a one-layer remainder `ob3` `7 + 22 cnt + F(cnt)` and `ob2` `5 + 11 cnt + F(cnt)` (their loads and stores 2 each with the address operation); a call of a column kernel over `nb` rows (`nb = 2^k`; 3 for `ob3`) costs the call charge `2 * nb + 6` (`sc_ocall` of the cost model) plus `c0 + c1 cnt + F(cnt)`, plus 3 for the loop over the calls (and 2 when it is left), and its per-call constant `c0` is its `2^k - 1` twiddle loads (1 each) and 3 control operations (`34 = 31 + 3`, `18 = 15 + 3`, `10 = 7 + 3`, `6 = 3 + 3`; the boundary passes and `ob4m` of 4.6 likewise: their twiddle and spectrum loads and 3 or 5 control operations); per position `2^k` loads and `2^k` stores (1 each), `k 2^(k-1)` butterflies at 3 (`304 = 64 + 240`). A run of `L` layers is `floor(L/7)` `ob128` passes and one pass for the remaining layers. The outer transforms of stage D (4.4.1 item 6) use these kernels with these charges: a transform of `n = 3 * 2^a` (or `2^a`) outer points at `cnt` positions is the radix-3 stage as `2^a` calls of `ob3`, then each of its three rows (one row for `2^a`) as a run of `a` layers, plus its twiddle table of `n` entries at 3 each (a multiplication, a store and a control operation). The four 256-bit constants of the radix-3 stage of the row transforms (`w`, `w^2`, `(w + w^2)/2 = -1/2` and `(w - w^2)/2`) are loaded into four registers once per call of a region driver of that stage (4 loads with their address operations, 8 operations) and held for the call, so a use costs no load; a radix-3 position works in at most 10 more words (three inputs, three outputs, four temporaries), 14 words of the file. Twiddle 1 in the column kernels (the convention of the fused leaf pass above and of 1aa56884: a butterfly whose twiddle is 1 is its addition and subtraction, 2 operations): a column pass of `k` layers on a row of `2^a` points runs from the large-span end (forward) or towards it (inverse), and the butterflies with twiddle 1 of its layers are those at offset 0 of each block, `2^j` in its `j`-th layer, all in the call at offset 0 of each block (`2^k - 1` per position; `2^n - 1` per position over a run of `n` layers of a row); that call is a straight-line variant of the kernel without their multiplications, 1 operation less per such butterfly and position and 3 control operations more per such call. In the two-layer passes at the small-span end (the `ob4` pass of an inner transform, `ob4m` and the two boundary passes of 4.6) 3 of the 4 butterflies of each position and direction have twiddle 1 (both of the layer of span 2, one of the layer of span 4): 3 operations less per 4 points and direction.
* random words: the cost model's random-word primitive (an independent uniform 256-bit word) is one operation per word. The word of a draw is also loaded, stored into the cell `y` of the draw and addressed (one load, one store and three control operations), 6. A draw is that word (6), the reduction modulo `p` (three steps each of a comparison, a conditional branch and a field subtraction, 9, with the loop control of three iterations, 11), the conversion of the result to the internal representation (1), the entry (2) and the address of `y` (2): 31 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: 489 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation: every array is taken from one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes (`need` bytes), and `need` decides the allocator. A block of more than 2^36 = 68,719,476,736 bytes comes from the pool, one region with two ends: its blocks follow each other in address order, each with a header (size, size of the previous block, in-use flag), no two free blocks are adjacent, and the unused middle between the two ends is one free block. Each allocation statement of the program uses one end of the pool, a constant of the statement: the statements (`g` of stage A, the block array of stage B, `MU` and `Y`, the work arrays of the Newton products, of a squaring step (in a chunked product of a squaring step, all its arrays except the accumulators of the square `R^2`, which use the low end) and of a shift, and the results inside the half-gcd: the quotient and remainder of a node and of the outer loop, the outputs of apply_inv, of the matrix products and of mul_add_q2, every allocation of the lean stage D (`ld_new`, all sites `# pool:H`, including the working arrays of its block products), and the reversed `g` and the operand rev(X^v P1) of stage C step 1 (4.6)) use the high end, every other statement the low end, except that the copies of the remainders returned by a node that applies its second matrix (4.4, step (6)) are taken from the low end. A low request walks the blocks upward from the bottom of the pool, a high request downward from the top (the two sizes in the header give both neighbours, so the two walks are the same code mirrored); it takes the first free block with at least `need` bytes (the unused middle is the last block of either walk) and cuts the block from the side nearest its own end, and the rest stays a free block when it is at least 128 bytes (else it belongs to the block); a free merges the block with a free neighbour on either side, the unused middle included, the same code for both ends. Since no two free blocks are adjacent and a walk ends at the middle, a walk examines at most 2 P + 1 blocks, P the live blocks on its side of the pool, and one block examined is 13 operations (two comparisons with branches, two loads, the advance). A block of at most 2^36 bytes comes from the slab classes: the class `j` is the least `j >= 7` with `2^j >= need`, a slot is `2^j` bytes; a request takes the first slot of the free list of its class, else a new slot from the end of the slab area, and writes the class and the in-use flag into the header; a free puts the slot on the free list of its class. The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows: a request of the pool 97 operations besides the walk (the statement that calls the allocator, the set-up, the split, the header stores, and a flat 64 for the statistics) and 13 per block examined, a request of a slab class at most `126` (the statement that calls the allocator, the class `j` by a binary search over 7..63 in 6 steps of 6 operations, the pop or the bump, the two header stores, and a flat 64 for the statistics), a free 81 for a slab block and at most 105 for a pool block (a free tests the size of the block to choose the allocator, in place of the test for a null pointer, which the program never needs). Every allocation of the walk is charged `1 + 120 + 13 (2 L + 1)` with L the live blocks at that point, which covers the pool (P <= L, the 97 operations and 13 per block examined) and the slab path (at most `126 <= 1 + 120 + 13` operations), and every free 105 (550 per allocation and 105 per free at 16 live blocks in stage E). The memory of both allocators is the arena of section 7.
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

This entry runs the half-gcd above with six changes, all from 1aa56884 (credited in the dependencies and the note), charged by this model's rules of 4.2 and 4.5. They change where arrays live and which coefficients are formed, never a quotient: every quotient used is a quotient of the whole pair (lemma 4.4 above, and lemma 4.8 below).

1. *The base case in place.* For `k <= 96` the two remainders are two arrays and a division step with a quotient of two coefficients is one pass `r_k = a_k - q0 b_k - q1 b_(k-1)` written over the array of `a`; the roles of the two arrays swap. The four matrix entries are four arrays of `k + 2` elements allocated once, and `R := R Q` writes `r11 q + r12` over `r12`. No array is allocated or freed inside the loop.
2. *Matrix-only calls.* A call returns the reduced pair only when its caller wants it: the calls of the Euclid driver `poly_gcd_own` and, inside them, the second calls with `s3 <= 0`. Every call inside a first call, and every truncated second call, returns its matrix only.
3. *Windows.* In a node that wants its matrix only and has `s3 > 0`, the block products of `apply_inv` form only the top window of `c` and `d`: the coefficients of degree at least `s3 - 1` (lemma 4.8 (a)). Such a node tests that the coefficients of `c` and `d` at their normal leading degrees `la - h - 1` and `la - h - 2` are nonzero (2 tests, charged) and ABORTs otherwise, so it never reports a shorter remainder from a window.
4. *The two tests and the ABORT.* At every division the quotient test (the quotient has degree 1) and after every recursive call and every call of `poly_gcd_own` the return test (the call returned exactly its parameter as degree count; a zero remainder inside hgcd or in the outer-loop division also ABORTs), 2 operations each, charged wherever they execute. If a test fails the trial ABORTs: the allocator is reset to its state after initialisation (`1,000` operations, charged in section 6) and the next centre is drawn. On the normal remainder sequence neither test fails (6.3), so every division of stage D is the one-pass division by a quotient of two coefficients and the Newton division is never run.
5. *The top node in pieces.* Stage C leaves `g` and `R` in two pieces each, the coefficients `[0, cut)` and `[cut, l)` with `cut = 7,164,005,449,728`. The first call of `poly_gcd_own` frees the high pieces of `g` and `R` right after its own `apply_inv`; the pair `(c, d)` is then formed from the low pieces only (`c` first, by the block products of 4.5 with the window `[0, lc)`, `lc = m + 1 - k1`; then `r22` and `r12` are freed; then `d`; then `r11`, `r21` and the low pieces are freed). The pair `(d, e)` of the second call is written as two pieces at `cut2 = deg d + 1 - k3` and handled the same way.
6. *Block products of stage D.* Each product of apply_inv, of the top node and of mat_mul uses the cheapest of the single transform, scheme (a) at block length 2^31 (one row of passes of 2^32 points) and scheme (c) at the block length of least charge among `2^b` (b = 6..31, transforms of `2^(b+1)` points, one row of passes) and `3 * 2^b` (b = 5..31, transforms of `3 * 2^(b+1)` points: the radix-3 stage and three rows of radix-2 passes, with the kernels and charges of the transforms of `3 * 2^32` points of 4.5, the radix-3 output stage charged on all `3 * 2^(b+1)` points). The number of chunks is the least power of two that brings a chunk form to at most `m // 16` elements. The outputs are allocated first at their true lengths, the chunks accumulate into them, the working arrays follow and are freed at the end, and the operands are freed after the last chunk. This replaces, for stage D, the Blocks, Choice, stage-D and Scaling bullets of 4.5. There is no placement pass in stage D: each output of a scheme (c) product is untwisted straight into its window with the scaled weight `sign / (NB n2) * w^(-e)` (the sign of the output, the factor `1/NB` of the unnormalised inverse transform and `1/n2` of the outer transform applied here), charged 15 operations per product (the scale and the weight base), 7 per untwist call (the table entry and the scale loaded and the result stored, each 2 with its address operation, and one multiplication) and the chunk and outer-point loops; at r = 13 this is 40,642,624,997,470 operations per trial (537 scheme (c) products, 4,054,233,958,440 untwist calls), included in row D. These figures differ from those of our entry 03fbfbed (134,279,232 products, 105,774,871,473,234 operations) because the single transforms of item 7 now win the choice above for most products that took the block path there and the outer transforms are charged by the stage-C column kernels; the block products themselves are formed as before. The outer transforms of scheme (c) use the column kernels of stage C with their charges (4.2: `ob128`, `ob64`, `ob32`, `ob16`, `ob8`, `ob4`, `ob2` across the outer points as the layer count needs, `ob3` for the radix-3 stage, base-plus-index loads and stores, the twiddle table of the outer points at 3 per entry), and the assembly of a chunk, the untwist into the window and the fold of an outer point into the row of its chunk are loops of eight elements per pass (4.2): the assembly 4 per element written (5 after the first chunk, where the twist is applied), 7 (8) per element added, 2 per element zeroed and 10 per row; the untwist 5 per element in the first chunk and 8 in the others, 13 per piece; the row fold 8 per element and 4 per row (the conventions of 1aa56884 for these three primitives, credited). The kernels `ocp`, `oax` and `ozf` of 4.5 are not used in stage D. The pieces of a product outside its window are dropped (never accumulated or untwisted): the cyclic wrap of length `n2` does not reach the window (4.5), so the window's coefficients do not depend on them. The choice between the single transform and the block products counts every charge of each path, including the allocations and frees the block path adds.

Two further changes, from weijiekoh a78f526e (its proof 4.4, `mat_mul`, `mat_apply` and the division step; credited), re-implemented and charged by this model's rules:

7. *Product forms.* (a) Scope: the whole-operand single-transform path of `apply_inv` only (the block products of item 6 and their top window are unchanged). On that path the single transform is sized by the output: its length `N` is the least admissible length with `N >= lc = la - h`, the length of `c`, not the operand length `la`. `c = s (r22 a - r12 b)` and `d` have degree below `lc` (the high coefficients cancel, step (2) of 4.4), so they equal their reductions mod `X^N - 1`, and the products are taken of the operands reduced mod `X^N - 1`: an operand longer than `N` is folded as it is read into the transform input, 10 operations per folded coefficient per row read (load, add, store, loop step). Folding the operands before the products and the subtraction is exact: reduction mod `X^N - 1` is a ring homomorphism, so `(r22 a - r12 b) mod (X^N - 1)` is the reduction of the same expression with each of `a`, `b`, `r12` and `r22` first reduced mod `X^N - 1`. (b) Each single-transform product of stage D (`apply_inv`, `mat_mul`) takes the cheaper by total charge of the transform of `3 * 2^a` points of 4.2 and a plain transform of `2^a'` points, `2^a'` the least power of two that holds the result, taken only when `a' <= 32` (roots of unity of order `2^a'` exist only for `a' <= 32`): one row of the radix-2 passes of 4.2 (the same kernels and twiddle table, no radix-3 stage, no reordering), each operand copied in at 7 operations per coefficient and the rest of the input zero-filled at 5 per slot (a store with its address operation and the loop step), the pointwise products and the inverse passes as for one row, the outputs read in place. The block products of item 6 are charged as before; only which products take them changes (item 6, the figures at r = 13).
8. *Division without inversion.* Every division by a divisor `d` of at most 2,048 coefficients (the steps of the base case and the node and outer-loop divisions of short pairs) is the scaled step `e = v^2 c - (A x + B) d` with `v = lc(d)`, `A = v lc(c)`, `B = v c_(n-1) - lc(c) d_(n-2)` (`n = deg c`; `d_(-1) = 0` when `deg d = 0`): no field inversion (5 field operations in place of the inversion and 4), one more multiplication per remainder coefficient (`v^2 c_i`), and the matrix update by `[[A x + B, 1], [v^2, 0]]`, one more multiplication per coefficient of the column it scales (`v^2 r_f`); all charged. Each remainder so formed is the exact one times a nonzero scalar of its own (if `c = lambda c*` and `d = mu d*`, then `e = v^2 lambda e*`; the two members of a pair generally carry different scalars), each matrix so formed is `D1 R D2` with `R` the exact matrix and `D1`, `D2` diagonal with nonzero entries (the inner factors between consecutive steps multiply to scalars), and `apply_inv` applies the adjugate, so in every pair `(c, d)` each member is a nonzero scalar multiple of the exact one: the degrees, the quotient degrees, the tests of 6.3 and the stopping rules are those of the exact sequence (they read degrees and whether a coefficient is zero), and `poly_gcd_own` makes the last nonzero remainder monic at the end (4.4). Longer divisors keep the inversion.

One further change, from bradcush 4bcabff8 (credited), re-implemented and charged by this model's rules:

9. *The first call of a matrix-only node on the inversion-free half-gcd* (bradcush `4bcabff8`, with the transform reuse of `b30de9bf`; read as text only, ported and charged in this cost model as in our r = 3 entry `bcf8e01c`). In a node that wants its matrix only (item 2), let `j` be the largest with `2^j - 1 <= k1 = ceil(k/2)`; if `7 <= j <= 37`, step (1) runs with the parameter `k1' = 2^j - 1` in place of `k1` (`s = n - 2 k1'`, the top `2^(j+1) - 1` coefficients of `a` and `b`) and its matrix `R1` is computed by the inversion-free half-gcd of budget `2^j - 1`; steps (2) to (6) of the node are unchanged, with `k2 = k - d_1` and `k3` for the smaller `d_1 = 2^j - 1`. The top-coefficient lemma of step (1) holds for every first parameter `k1' <= n/2`, so the node returns the same `R_h` (up to the diagonal scalars of item 8). The inversion-free half-gcd keeps matrices and remainders up to nonzero scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside it. A node of budget `2^j - 1` makes two child calls of budget `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a power-of-two transform of `n` points in the block form of 4.2 after a twist, joined by a 3-row CRT for `(c, d) = adj(M1)(a, b)` on the top window; then the pseudo-division and the product `M = M1 [[Q, 1], [b^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and the scale of a step is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the row `Y - 1` values of each child's matrix are returned by the child, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The twist roots of order `2n` and `4n` come from the squaring chain of the running twiddle factors of the row transform (4.2); the scales `1/2^a` (`a <= 36`) are a table of 37 words built at the entry of stage D (`1/2 = (p + 1)/2` an immediate, 35 multiplications, 36 stores and the loop). The base case (budget 63) runs two remainder steps per pass over its window. Every pseudo-division tests that its quotient has degree 1 and every call tests on return that it removed exactly its budget (2 operations each; the ABORT of item 4). The matrix is returned in coefficient form (four arrays of `2^j`, `2^j - 1`, `2^j - 1`, `2^j - 2` words); the working arrays of the half-gcd live in one bump arena (an allocation or release is 10 operations), `2,199,023,255,296` words at `j = 37`, the peak of its recursion. Above `j = 37` step (1) is the lean call of 4.4; the cap keeps the pool extent of stage D at or below its high-water mark in stage C (section 7). On the normal sequence every budget and allocation is a function of `m` alone (6.3).

**Lemma 4.8 (windows and pieces; 1aa56884's lemma 4.8).** (a) In a node that wants its matrix only, with `s3 > 0`, the rest of the node reads `c` only at degrees at least `s3` and `d` only at degrees at least `s3 - 1`. (b) In the top node, after the first call's `apply_inv` no operation reads `a` or `b` at degrees at least `cut`, and the low `lc` and `lc - 1` coefficients of `c` and `d` computed from `a mod X^cut` and `b mod X^cut` are the `c` and `d` of step (2); the same holds for `(d, e)`, `cut2` and `(c', d')`.
*Proof.* (a) The stopping test and the quotient test use `deg c` and `deg d`; the quotient `q = q1 x + q0` uses the top two coefficients of `c` and of `d`; and `e_i = c_i - q0 d_i - q1 d_(i-1)`. The second call reads only `d quo x^s3` and `e quo x^s3`, that is `d_i` and `e_i` for `i >= s3`, hence `c_i` for `i >= s3` and `d_i` for `i >= s3 - 1`. After it the node needs only `R1`, `q` and `R2` (and `s3 - 1 <= deg d - 1`, so the top two coefficients are inside the window). (b) The first call reads `a quo x^s` and `b quo x^s` and, after its `apply_inv`, only its own arrays; the top node then reads `a` and `b` only in step (2). For `i < lc <= cut` the coefficient `i` of `r22 a` is `sum_j r22_j a_(i-j)` with `i - j < cut`, so it equals the coefficient `i` of `r22 (a mod X^cut)`; `c` has length `lc`, so it is the low `lc` coefficients of `s (r22 (a mod X^cut) - r12 (b mod X^cut))`, and likewise `d`. For the second call, `cut2 = deg d + 1 - k3 >= lc'` with `lc' = deg d + 1 - h3` and `h3 = k3` on the normal sequence. QED

The charges of these steps are this model's (4.2, 4.5), not 1aa56884's: with 1aa56884's own conventions the same walk gives its published row D to the unit (`1,062,106,645,154,198,605,714,641` at r = 21, recomputed in our model with their conventions switched on), and with this model's primitives, with 1aa56884's conventions for the three primitives of item 6 named there and the outer transforms by the stage-C column kernels, it gives row D of section 6.

### 4.5 Products longer than `3 * 2^32` points (block mode)

The bullets of earlier entries on the coefficient-domain stage C are not repeated: stage C is 4.6, which uses this section only for the Newton reciprocal and the q product of its step 1. Stage D uses 4.4.1 item 6.

At this r the transforms of 4.3 and 4.4 would have up to `3 * 2^43` points (the square of stage C, `2m - 1 = 19,073,486,328,123` coefficients) and `3 * 2^42` points (`m + 1`, the products by `g`, and the products by the half-gcd matrices, whose entries have several blocks). The field has no root of unity of such an order (`p - 1 = 2^32 * 3 * q`). Grok (xAI), job 140, determined the cost of multiplying polynomials of lengths `3 * 2^34`, `3 * 2^36` and `3 * 2^38` over this field and recommends the block NTT (its scheme (a)) for `3 * 2^34` and `3 * 2^36` and the same split with an outer transform across the blocks (its scheme (b), the outer FFT) for `3 * 2^38`: a product is cut into blocks, the blocks are transformed with the longest available transform, and the products of block spectra are summed in the transform domain. Grok job 140 checked both schemes against schoolbook on random products of length `2^14` with a transform cap of `2^10` (every coefficient equal, and the counted multiplications and additions equal to its formulas, `551,999` and `890,850` for scheme (a)). Both schemes are the same operations at every block count; at the lengths of this r we apply them by the charging rules of 4.2. The schemes, as used by the algorithm:

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

**Points.** Here `h = 3 * 2^32 = 12,884,901,888` (it divides `p - 1`) and `K` is the number of cosets of each point set (not the number of centres of 4.1). `H` is the subgroup of order `h` of `F_p^*`, with generator `omega = 5^((p-1)/h)`, which has order `h` because 5 is neither a square nor a cube (`5^((p-1)/2) != 1`, `5^((p-1)/3) != 1`). Put `u_k = 5^k`, `C_k = u_k H` and `n_k = u_k^h = z^k` with `z = 5^h`. `p - 1 = 2^32 * 3 * 463 * q1 * q2` with `q1 = 539,204,044,132,271,846,773` prime, and `z^((p-1)/q1) != 1`, so the order of `z` is at least `q1 > 2K`. Hence the nodes `z^k` (`k < 2K`) are distinct and the cosets `C_k` are pairwise disjoint (`C_j = C_k` if and only if `z^(k-j) = 1`). These four facts are checked by direct computation (Python standard library): `q1` is prime by a deterministic Miller-Rabin test with the bases up to 41 (valid for `n < 3.3 * 10^24`), `z^((p-1)/q1) != 1`, `5^((p-1)/2) != 1` and `5^((p-1)/3) != 1`; all four hold. At r = 13: `m = 9,536,743,164,062`, `K = ceil((m + 1)/h) = 741`, `n1 = K h = 9,547,712,299,008 = m + 10,969,134,946`. Put `O1 = C_0 u ... u C_(K-1)` and `O2 = C_K u ... u C_(2K-1)`, `M(Y) = prod_(k<K) (Y - z^k)` and `P1(X) = M(X^h)`. `P1` has degree `n1`, is squarefree, has root set exactly `O1`, and on a coset `C_k` with `k >= K` it is the nonzero constant `M(n_k)`.

**Representation.** A polynomial `f` of degree `< n1` is determined by its values on `O1`, and also by its values on `O2`. Write `f = sum_(j<h) X^j F_j(X^h)` with `deg F_j < K`. Then `f mod (X^h - n_k) = sum_j F_j(n_k) X^j`, so the values of `f` on `C_k` are the transform of size `h` of `(u_k^j F_j(n_k))_j`. The inner transform of size `h = 3 * 2^32` is the Good-Thomas form of 4.3: a twiddle-free radix-3 pass (first in the forward transform, last in the inverse) and three rows of `2^32` points, the output index `i` stored in row `i mod 3` at position `i mod 2^32`; the input index `j` is in the matching Good-Thomas order, and every per-position table (the `omega^i` table, the factors of the copies) is stored in that order. Each array holds the values coset by coset, in the output order of the inner transform. The inner transforms of the cosets of an array are made together, as column passes across the cosets (position = coset, stride `h`): one `ob3` pass for the radix-3 stage and, on each of the three rows, four `ob128` passes and two `ob4` passes for the 32 layers, in place on the array (4.2); in the extensions of the loop (step 6) the radix-3 pass is made by the geometric phase instead (Kernels, below).

**Lemma 4.6 (the step).** Let `g` be monic of degree `m` with `g(x) != 0` on `O1`. Let `R~` have degree `<= m`, and let `u0` be the polynomial of degree `< n1` with `u0(x) = -R~(x)^2 / g(x)` on `O1`. Then `W = (R~^2 + u0 g) / P1` is a polynomial of degree `<= m - 1`, and `W = R~^2 P1^(-1) mod g`. On `C_k` with `k >= K`, its values are `(R~(x)^2 + u0(x) g(x)) / M(n_k)`. *Proof.* `R~^2 + u0 g` vanishes on the `n1` distinct roots of the squarefree `P1`, so `P1` divides it. Its degree is at most `max(2m, n1 - 1 + m) = n1 + m - 1` because `n1 >= m + 1`, so `deg W <= m - 1`. Modulo `g`, `W P1 = R~^2`, and `P1` is invertible modulo `g` because `g` has no root in `O1`. The values follow from `P1(x) = M(n_k)` on `C_k`. QED. So the invariant `R~_i = S^(e_i) P1 mod g` passes from step to step with `R~' = X^b W` (`e_(i+1) = 2 e_i + b`, `deg R~' <= m`). The same argument with `R~` in place of `R~^2` leaves the Montgomery form (step 7).

**Lemma 4.7 (extension).** Let `f` have degree `< n1`, with its values on `O1` given. The inverse inner transform of each coset gives `h u_k^j F_j(n_k)`. Fix a position `j`, write `F = F_j`, and put `s_i = F(z^i) z^(-i) / M'(z^i)` and `kappa(e) = 1/(z^e - 1)` for `1 <= e <= 2K - 1`. Then `F(z^(K+t)) = M(z^(K+t)) sum_(i<K) s_i kappa(K + t - i)` for `t < K`. *Proof.* `deg F < K`, so `F` is the Lagrange interpolant of its values at the `K` distinct nodes, and `z^(K+t) - z^i = z^i (z^(K+t-i) - 1)` with `1 <= K + t - i <= 2K - 1`. QED. The direction `O2 -> O1` is the same with the nodes `z^(K+i)`. The sum is a cyclic convolution of length `Lx = 3 * 2^9 = 1,536 >= 2K` with a fixed kernel, and no index wraps.

**The stage** (the eight steps of 1aa56884, with our parameters at r = 13). The exponent `E = (p-1)/2` starts from `S^v` with `v = 2^40`, a multiple of `2^32` (the power of two in `h`) below `m` (`VSHIFT = 3`: three more squaring steps and a shorter reciprocal), and runs `213` steps, `45` of them with `b = 1`.
1. *Barrett start:* the reciprocal of the reversed `g` modulo `X^ell`, `ell = 1,110,480,762,723`, by the Newton iteration of 4.3 with the products of 4.5. Then `q = floor(X^v P1 / g)` by one product (`Kq = 87` rows).
2. *`g` on `O1` and on `O2`* by the chirp evaluation of section 3 (one convolution of length `Le = 3 * 2^10 = 3,072 >= 3K - 1` per position) and `2K` forward inner transforms.
3. *`R~_0` on `O2`:* `q` evaluated at the nodes of `O2` (`Lq = 2^10`), then `R2 := x^v M(n_k) - R2 * G2` pointwise. At the point `x = u_k omega^i` of `C_k`, `x^v = u_k^v zeta^(i mod 3)` with `zeta = omega^v`, a primitive cube root of unity (`v` is a multiple of `2^32` and not of 3), so `x^v M(n_k)` is one of three constants on each coset, one per row of the Good-Thomas layout: per coset the three constants `u_k^v M(n_k) zeta^r` (9 operations) and per row the pass over its `2^32` elements. This gives the values of `X^v P1 - q g = X^v P1 mod g`.
4. *`R~_0` on `O1`:* an extension `O2 -> O1` (lemma 4.7).
5. *`-1/g` on `O1`* by Montgomery's batch inversion per coset. A zero prefix product means `g` vanishes on `O1`, and the trial ABORTs as in 4.4.1 item 4 (allocator reset, ledger row 'ABORT reset') after a prefix of the charged work; the probability is below `2^-166.8` (9.2(b)).
6. *The loop*, for each bit `b`: `R1 := R1^2 G1` (`u0` on `O1`); the extension `O1 -> O2`; `R2 := x^b (R2^2 + R1 G2) / M(n_k)`; the extension `O2 -> O1`. By lemma 4.6 the invariant holds after every step.
7. *Leaving the Montgomery form:* `R1 := R1 G1`, the extension `O1 -> O2`, `R2 := (R2 + R1 G2) / M(n_k)`. `R2` now holds `R = S^E mod g` (degree `< m`).
8. *Coefficient form for stage D:* `R2` and `g` are interpolated in place (inverse inner transforms, then two chirp correlations of length `Lx` per position), each into two pieces, the coefficients `[0, cut)` and `[cut, l)` with `cut = 7,164,005,449,728`, which the top node of stage D frees early (4.4.1, step 5).

**Kernels.** Every column pass of this section, the pruned first and last passes included, runs its position loop eight positions per pass with the control `F(cnt)` per call (4.2), not 3 per position. In the loop, the last two forward layers of the inner transforms, the pointwise step and the first two inverse layers are one column pass per boundary: on `O1` (`9 + 44 cnt + F(cnt)`) per position 4 loads, 4 butterflies, for each of the 4 elements a load of `G1`, a squaring and a multiplication, 4 inverse butterflies and 4 stores; on `O2` (`11 + 61 cnt + F(cnt)`, `15 + 70 cnt + F(cnt)` for `b = 1`) the same with the load of `1/M(n_k)` and per element the loads of `R2` and `G2`, a squaring, two multiplications and an addition (`b = 1`: the factor `u_k` and two more multiplications per element), within the 18 words. The extension is computed in a coset-major group buffer (`L` rows of `VCNT` positions) with column passes (`ob128`, `ob64`, `ob32`, `ob16`, `ob8`, `ob4`, `ob2` as the layer count needs; `ob3` for the radix-3 stage): the first forward pass reads the `K` input rows from the coset array with their factors and skips the zero rows; the last two forward layers, the product by the kernel spectrum and the first two inverse layers are one pass (`ob4m`, `13 + 36 cnt + F(cnt)`: 4 data words, 3 + 3 twiddles and 4 spectrum words); the last inverse pass forms and writes only the rows `K .. 2K - 1`, with their factors, into the coset array. In the extensions of the loop (step 6) the radix-3 pass of the inverse inner transforms (their last pass) and that of the forward inner transforms (their first pass) are not `ob3` passes: a group of `VCNT = 3 * 2^10` positions is `2^10` Good-Thomas triples (positions `i`, `i + h/3`, `i + 2h/3`), the first forward pass makes the 3-point transform of each triple of each of the `K` input rows as it reads it, and the last inverse pass makes it for each triple of each of the rows `K .. 2K - 1` before it writes it. A row of such a group is three runs of `2^10` positions, each with its own running factor: the per-element charges of the copies are unchanged, and the per-row set-up of a copy is charged once per run (three times per row). The 3-point transform is the Winograd form `s = b + c`, `d = b - c`, `y0 = a + s`, `t = a + c1 s`, `e = c2 d`, `y1 = t + e`, `y2 = t - e`, with the immediates `c1 = -1/2` and `c2 = (zeta - zeta^2)/2` (`zeta` the cube root of unity of the transform, `zeta^(-1)` for the inverse; `zeta^2 = -1 - zeta`): 8 field operations per triple. The other inner transforms (steps 2, 3, 4, 7 and 8, and the extension rows of the table below) keep their `ob3` pass.

**Charges** (the components sum to row C of section 6):

| component | operations |
|---|---:|
| inner transforms of the `K` cosets of one array (the `ob3` pass and the radix-2 column passes of 4.2 at `cnt = K`; forward / inverse) | 637,133,721,324,874 / 637,133,721,324,874 |
| geometric phase of one extension (88.932 per element of `n1`) | 849,094,813,689,996 |
| one extension with its `2K` inner transforms | 2,123,362,256,339,744 |
| one loop step, `b = 0` / `b = 1` | 4,121,034,240,919,112 / 4,142,529,478,493,768 |
| tables: `30 K` constants, the `omega` table, the kernel spectra, the twiddle table of the group passes | 128,985,917,637 |
| Newton reciprocal (step 1, with its allocations) | 5,078,709,088,291,297 |
| product for `q` (step 1) | 1,483,178,572,367,399 |
| evaluation of `g` (step 2, geometric part) | 2,265,635,836,930,186 |
| `2K` forward inner transforms of `g` (step 2) | 1,273,473,123,112,441 |
| step 3 | 1,380,828,074,684,923 |
| step 4 (one extension; the last two forward layers are in the first boundary pass of the loop) | 2,081,744,023,241,502 |
| step 5 (batch inversion) | 140,828,758,394,027 |
| step 6, the loop: 213 steps (45 with `b = 1`) | 878,747,579,006,630,376 |
| step 7 (with the last two forward layers of the final extension of the loop, one `ob4` pass) | 2,351,160,879,304,214 |
| step 8 (two interpolations) | 5,788,475,731,526,434 |
| allocations, exponent scan, zero fills, end of stage | 51,002,753,263 |
| stage C of one trial, with the stage bookkeeping of 1,000 (ledger row C) | 900,591,793,083,154,699 |

The inner transforms are column passes and the geometric phase uses the register-blocked kernels above (the outer-kernel convention of 1aa56884). With the pieces of 4.4.1 every coset access of a row pass (the pointwise passes, the batch inversion, the rows read or written by an extension) also selects the base of its piece (a comparison and a branch, 2 operations), and every column pass splits its coset loop at the piece boundary (4 operations per call); both are included in the figures above. Every charge depends only on `m` and the exponent, not on the coefficients.

**Memory.** The loop holds `R1`, `R2`, `G1` and the array of `g` (which holds `g` on `O2` during the loop and `g` in coefficient form at the exit): four arrays of `n1` elements. It also holds the tables and the group buffer of `VCNT = 3 * 2^10` rows of `Lmax = Le = 3 * 2^10` elements (the longest kernel), and one transform row of `Lmax` elements. The live peak of stage C is `3.0027` arrays of `n1` above its entry, plus the array of `g` from stage A. Section 7 walks these allocations with the rest of the trial.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: worst-case operation count (primitive operations; `C(13) = 489`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, the trial loop and the allocator reset after an ABORT (charged in every trial); `T_off` = the offline bound of section 6.2. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 1` (one centre, section 9.2), and `time_log2 = ceil_5(log2(N_max / 489))`.

Every stage is charged by the rules of section 4.2 where it executes. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(32-1)` elements (`ntt_init(32)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 17,179,887,292 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,382 |
| B (per trial) | (this entry: the inverse transforms and the geometric solve on the column passes of 4.2, the point loop in natural order; Appendix B2) (this entry: each evaluation by the program `L` of Appendix L, `291` operations, in place of `489`) `1481` cosets of `6,442,450,944` points, each point with two evaluations of `F` (at `c + s` and `c - s`) at `C(13) = 489` operations each, the loop work around them, `1481` inverse transforms of size `6,442,450,944`, the geometric solve of the cosets (two correlations of length `3,072` per position), the normalisation | 8,795,496,609,191,077 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain (section 4.6): the Barrett start (Newton reciprocal and the product for `q`), the evaluations of `g` and `q`, the batch inversion, `213` steps (45 with `b = 1`), each two pointwise passes and two extensions, the exit and the two interpolations | 900,591,793,083,154,699 |
| D (per trial) | half-gcd of `(g, R - 1)` (sections 4.4, 4.4.1), charged for the normal remainder sequence with the quotient and return tests; any other sequence ends the trial after a prefix of this work (section 6.3) | 499,782,930,700,487,073 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, register-resident, each at most `R(16) = 196,915` with its draw (Appendix S), the stage bookkeeping 1,000 and the load of `G` into registers 200 | 12,603,760 |
| F (per trial) | square root, back-map (below) | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 489 + 32` | 10,812 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| ABORT reset (per trial) | the reset of the allocator when a test of stage D (quotient, return or window) or the zero test of stage C (4.6 step 5) fails and the trial ends (section 6.3): the 47 free-list heads (classes 7 to 53), the end of the slab area, the two ends of the pool and the header of its free middle block; at most 1,000, charged in every trial | 1,000 |
| plan_invN misses | one per distinct plan size the cost model counts (57 sizes, 3,089 each) | 176,073 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **1,409,170,237,589,955,182** |

Row C is the sum of the charges of section 4.6; row D is the charge of the half-gcd of sections 4.4 and 4.4.1 with the products of 4.5, on the normal remainder sequence (6.3).

`N_max = 1,409,170,237,589,955,182` operations `= 2,881,738,727,177,822.46` units, `log2(N_max / 489) = 51.3558609628`, claimed as `51.35587` (rounded up at five decimals).

Stage B charges each of the `19,082,539,696,128` evaluations of `F` as one reduced permutation, `C(13) = 216 + 21 * 13 = 489` operations, although a line evaluation is a strict subset of the work of a reference permutation; the loop work around the evaluations is charged on top (section 3). This entry: the loop work, the `1481` inverse transforms and the geometric solve are charged on the column passes of section 4.2 (Appendix B2, where row B is expanded part by part and the counting program is printed): row B `8,795,496,609,191,077` (was `15,833,147,877,225,909`).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the isolation loop until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 31, the zero test of the shift (5, and at most 2 for the replacement of a zero draw by 1) and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because the memory-access charge adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `2,640` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = 2,594,979`, of which `pow_half` is 2,471,032, the Taylor shift 11,700 and the two gcds 54,395 each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + 64 * R(16) + 114 = 166,079,773`. This entry replaces this stage E by the register-resident procedure of Appendix S (no Taylor shift, inversion-free gcd, every field operation charged once): `R(16) = 196,915`, row E `12,603,760`.

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`.

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.2 Offline derivation of the literals (preprocessing)

The literals of the sources are computed once, offline, from `p` and the organizer's 192 round constants and 9 MDS entries, one literal at a time (working set: at most 16 words of 32 bytes and a 64-byte digit buffer); each is the value of one closed formula, with no search and no choice. Count in the primitives of 4.2 (orchard-field-ram-v2: every field operation, load, store and control operation is 1): a field operation is charged 4 (the operation, two operand loads, one store), a 64-bit word operation 3 (the operation, one load, one store), a hexadecimal digit 5 (its load, the table load, a shift, an or, the loop control). (a) Input: 202 values of 64 hexadecimal digits (`p`, the 192 round constants, the 9 MDS entries), 324 each with the 4 word stores: `65,448`. (b) Field literals, 489 field operations: `2 = 1 + 1` (1); `R = 2^256 mod p`, `2` squared 8 times (8); `R^2 mod p` (1); the Montgomery forms `x R mod p` of the 201 organizer constants (201); `2^65 R mod p` (`2` squared 6 times, times `2`, times `R`: 8); `5 = 2 + 2 + 1` (2); `5^t R mod p` with `t = (p-1)/2^32`, the odd exponent of the Tonelli-Shanks of stage F (223 bits, 46 of them 1: 222 squarings, 45 multiplications, times `R`: 268); charged `4 * 489 + 3 * 222` (the bit steps of the square-and-multiply) `= 2,622`. (c) Word literals, 90 word operations: `p - 1` (4), `t` (a shift by 32 over 4 words, 12), `(t+1)/2` (16), `(p-1)/2` (12), `p - 2` (4), `e = (4(p-1)+1)/5` (a shift by 2 into 5 words 15, plus 1, a division by 5 word by word 10: 26), `-p^-1 mod 2^64` (5 Newton steps `x <- x (2 - p_0 x)` from `x = p_0`, 3 each, and a negation: 16); charged `3 * 90 = 270`. (d) Output: 211 literals of 64 hexadecimal digits (the 201 Montgomery forms, `R`, `R^2`, `2^65 R`, `5^t R`, `t`, `(t+1)/2`, `(p-1)/2`, `p - 2`, `e`, `p`), 324 each, and `-p^-1 mod 2^64` (16 digits, 81): `68,445`. `T_off = 65,448 + 2,622 + 270 + 68,445 = 136,785` operations. The ledger charges the declared cap `1,000,000 >= T_off` (`preprocessing_log2 = 20`, `2^20 = 1,048,576`), inside `N_max`: a counted bound, not a premise. The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry e6dcb600)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c, R_c - 1)`: every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centering division of a node, the division of each repetition of the outer loop, each step of the base case) tests that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); (c) the window test of 4.4.1 item 3 (2 tests, 2 operations each); a zero remainder inside hgcd or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state after the twiddle table (1,000 operations, charged in every trial) and the next centre is drawn. Lemma (prefix; e6dcb600, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each call splits at k1 = ceil(k/2) and, with every quotient of degree 1, every degree in the tree is fixed by m and the number of quotients so far and the parameters of the second call and of the outer loop are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's hgcd calls and divisions produce has degree at least 94 (n >= 193), so a gcd of degree at most 94, and so every gcd of degree at most DMAX, first appears in the classical Euclid below degree 192, after a prefix of the degree-0 work. A zero remainder anywhere earlier (gcd degree above 94, a failed trial anyway) ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2(b)). Row D of section 6 is this charge, `499,782,930,700,487,073`.

## 7. Memory

Three terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 762,224 bytes of code (399,216, plus 363,008 for the block-form bodies of 4.2 written four blocks per pass and the group-0 variants: per direction and `k = 1..7` four more bodies of at most `2^(k+1) + 3 k 2^(k-1) + 3` instructions of at most 16 bytes, `2 * 4 * 16 * 2,836`), 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages): 5,613,452 bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (a trial frees every array but the twiddle table, and the simulation checks that the pool is back to that state at the end of the trial). The simulation records every allocation and free of the trial in the order of the program (the twiddle table, stage A, stage B, stage C, stage D; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order), checks that these events reproduce the live-set walk of every stage (bytes in use, peak, live blocks), and runs the allocator on them. By the prefix lemma of section 6.3 every size in the sequence is a function of `m` and of the shape of the recursion on the normal sequence (and the block counts of the products), so the sequence is the same for every input. The two-ended pool takes the blocks of more than 2^36 bytes and is simulated address by address (two lists in address order, the low one from the bottom and the high one, for the statements marked `# pool:H`, from the top; the first free block that fits on the request's side is cut from the side nearest its end; a free merges with its free neighbours and with the unused middle); its capacity is the largest sum of the extents of the two ends over the trial, `1,223,000,528,559,360` bytes (reached in stage C; stage D does not raise it), plus 128 bytes so that the unused middle is always at least 128 bytes. The live-set peak of the same sequence is `1,223,000,830,647,680` bytes and the arena is `1.00176` times it: the blocks that die first are taken from the top and the long-lived ones from the bottom, so the holes left by freed blocks are small. The slab classes take the blocks of at most 2^36 bytes (a block of at most `2^j` bytes gets a slot of `2^j` bytes; the free list of the class first, else a new slot from the end of the slab area), so the slab area is the sum over the classes of the peak number of live blocks of the class times `2^j`: `2,130,303,734,912` bytes. Stages E to I hold at most 16 live arrays of at most 17 elements (16 slots of 1,024 bytes), and the allocator keeps 47 free-list heads (classes 7 to 53) and the end of the slab area (48 words, 384 bytes): `16,896` bytes with a margin of 128. The arena is `1,225,130,832,311,296` bytes (the three terms, rounded up to 64 bytes). The pool term is reached in stage C; stage D, with the scale table, the coefficient-form matrices and the bump arenas of 4.4.1 item 9, does not raise it. The slab term includes the arrays of item 9 of at most 2^36 bytes. The peaks of the live set per stage (twiddle table, `g`, `F` and the live set of the stage; the arena above is larger): A 305,595,513,045,184; B 610,916,148,183,296; C 1,223,000,830,647,680; D 1,148,545,324,578,752; stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The walk of stage D is the walk of the normal remainder sequence (6.3) with the pieces and windows of 4.4.1: every array of stage D has the length the normal sequence gives it, and a trial with any other sequence ends (ABORT) after a prefix of these allocations, so the walk bounds every trial. The largest transform has `3 * 2^32` points and uses roots of unity of order 3 and `2^32` (`p - 1` is divisible by 3 and by `2^32`); products that would need a longer transform are computed by blocks (section 4.5). The largest buffers are those of stage C (section 4.6: `R1`, `R2`, `G1` and the array of `g`, `n1 = 9,547,712,299,008` elements each, the tables and the group buffer; the Newton phase of its set-up holds three arrays of `ell` elements and the forms of one product) and those of stage D (4.4, 4.4.1).

(c) A stack bound of 65,536 bytes.

(d) The register file of the machine of claim.json: one file of 387 words (256 field registers and 131 integer address registers), each counted as a 256-bit word, 12,384 bytes.

(e) This entry's stage-B solve buffers (Appendix B2), allocated in stage B and freed at its end: the group buffer of `1,024 * 3,072` elements, the two kernel spectra of `3,072` elements, the two tables of `1481` constants and three arrays of `1,024` slot words, each counted as a slab slot of its own (64-byte header, payload rounded up to the power of two): `134,807,552` bytes, added on top of the footprint below (an upper bound: the stage-B live set of the base, at most two arrays of `n` elements, is unchanged). With it the footprint is `1,225,130,972,826,604` bytes `= 2^50.1218574`, claimed as `memory_log2_bytes = 50.12186`. The base package's total follows. Total: (a) + (b) + (c) + (d) = `1,225,130,838,002,668` bytes `= 2^50.12185`, claimed as `memory_log2_bytes = 50.12186` (rounded up at five decimals). The rows of section 6 and this arena are generated by our counting program: it adds the charges of 4.2 over every call of the algorithm of section 4 in program order and runs the allocator of 4.2 on the same allocation sequence; each term is the closed formula stated in sections 4 and 6, and the program is not attached. The memory penalty is `max(0, 50.12186 - 20) = 30.12186`. The offline derivation of section 6.2 handles one literal at a time; its working set (at most 16 words of 32 bytes and a 64-byte digit buffer, 576 bytes) is below 1,024 bytes, inside the figure above. The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init". This entry adds `16,384` bytes of code and static data (Appendix L.4: `L` as one subroutine, its constants, the call site and the register-resident stage E of Appendix S): footprint `1,225,130,838,019,052` bytes `= 2^50.1218573`, claimed `memory_log2_bytes = 50.12186`; the arena and the allocation walk are unchanged.

## 9. Success probability and the premises `H-ONE` and `H-NORMAL`

### 9.1 The premise `H-ONE`

Notation. `p` is the Pallas prime, `D = 5^19`, and `F` is the fixed polynomial of section 2.3 at r = 13 (degree `D`, leading coefficient `f_D(0) != 0`). `g_c` is the monic odd part about the centre `c` (section 3, degree `m = 9,536,743,164,062`), and `G(c, t) = (F(c + t) - F(c - t)) / (2 t) = g_c(t^2)`. For `c` in `F_p`, let `k(c)` be the number of nonzero squares `S` with `g_c(S) = 0`; this is `deg G_c` of section 3, the degree of `gcd(g_c, S^((p-1)/2) - 1)`. `E_c` is the event `1 <= k(c) <= DMAX` (`DMAX = 16`) under which stage E runs.

**Premise `H-ONE`.** The number of centres `c` in `F_p` with `1 <= k(c) <= 16` is at least `0.3931 p`. Equivalently, for `c` uniform on `F_p`, `P(E_c) >= q = 0.3931`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r13-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2) and the polynomial `F` of section 2.3, with centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:**
- The premise concerns this `F`, not every polynomial of degree `D`. It is false for permutation polynomials: every pure composition of maps `x -> a x^5 + b` is bijective and has `k = 0` at every centre. It is also false for a decomposable `F` with imprimitive monodromy (the axis line of 10.3, Theorem C).
- It is false at one layer (`F_1`, `m = 2`: the law of 9.3(a) gives exactly 0.375) and true at two and three layers (9.3(c)).
- The value `0.3931` is `0.3934693 - 0.3931 = 0.0003693` below the value `1 - e^(-1/2) = 0.3934693` of the law of 9.3(a), and below the four-moment Bonferroni bound `151/384 = 0.3932292` (9.3(b)). With `delta = 0.003` (9.5), the bound of 9.2 needs `P(E_c) >= 0.393000000000002345`.

What the premise does not contain: no random-polynomial model; no independence of centres (one centre is drawn); no statement about the remainder sequences (that is `H-NORMAL`, 9.5); and nothing about the cost.

### 9.2 The success bound with one centre

(a) *Centre.* The centre is one draw (4.1.1) and lies within statistical distance `eps_coin < 2^-128` of uniform on `F_p`; the exact value is 1.574e-39 (2^-128.90). So `P(E_c) >= q - eps_coin` for the drawn centre.

(b) *The ABORT of stage D and the zero test of stage C.* Let `N_c` be the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd: `deg(R_c - 1) = m - 1` and every quotient of degree 1 (section 6.3). By the premise `H-NORMAL` (9.5), `P(not N_c) <= delta = 0.003` for `c` uniform.

Let `Z_c` be the event that `g_c` vanishes at a point of the set `O1` of the value-domain stage C; its zero test (section 4.6) ends the trial. For each of the `n1` points `x` of `O1`, `g_c(x)` (before normalisation) is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so it has at most `D - 1` roots. Each residue is drawn with probability at most `4/2^256` (4.1.1). Hence `P(Z_c) <= delta_C = n1 (D - 1) 4 / 2^256 = 6.291e-51 (2^-166.8)`, proved, no premise.

If `E_c` and `N_c` hold and `Z_c` does not, stages C and D run to their end and return `G = gcd(g_c, R_c - 1)`.

(c) *Isolation.* If `E_c` holds, stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48`, over words that are fresh for that stage (lemma 9.4): each round, whatever came before, halves the degree with probability at least `w = 1/2 - 7.869e-40` (the `(p-3)/2` shifts that separate two roots, 4.1.1 weights), four halvings take `deg G <= 16` to 1, so the failure probability is at most `P[Bin(64, w) <= 3] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15`. Proved, no premise.

(d) *The bound.* A trial with `E_c`, `N_c`, not `Z_c`, and a successful isolation ends in a verified collision (sections 2-5). For `c` uniform, `P(E_c and N_c and not Z_c) >= q - delta - delta_C`. So, with `K = 1`,

`P[success] >= 1 - (1 - q + delta + delta_C)^K - K (eps_coin + eps_iso) = q - delta - delta_C - eps_coin - eps_iso = 0.390099999999997615 >= 0.39009`

with `q = 0.3931`, `delta = 0.003` and `K = 1`. This is the form of bradcush's entry 1aa56884 (9.2(f) there) at `K = 1`. The bound stays at least 0.39 for every `delta <= 0.0030999` at `q = 0.3931`, and for every pair with `q - delta >= 0.390000000000002345`. The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 13 enters it.

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

The Bonferroni bounds of orders 7 and 8 then give `0.39346933 <= P(E_c) <= 0.39346944` for `F_2` and for `F_3`. At these depths `H-ONE` is a theorem, with margin 0.00036933.

 At `N = 4`, the cycle types `(312)` and `(311,1)` of 10.3 make `pi(Gamma)` 2-transitive of degree 312. The only such groups are `A_312`, `S_312`, and the groups between `PSL(2,311)` and `PGL(2,311)`, whose non-identity elements fix at most two points. Centres with `k(c) = 3` and `k(c) = 4` occur (our runs, 10.5.1), and the 312-cycle is odd, so `pi(Gamma) = S_312`. The sign kernel at `N = 4` is not computed.

(d) *Measured.*
-  Toy fields, exact over all centres: deployed constants reduced modulo `p = 1,048,627` and six random-constant seeds, 3 to 8 S-box layers, partial rounds included, 27 cases. `P(k >= 1)` lies between 0.39214 and 0.39436; the largest deviation from 0.3934693 is 0.00133, that is `1.36 / sqrt(p)`.
- The real field: the organizer-run tests of 10.5.1 and our runs, reproducible observations at `m = 12` and `62`; no probability bound is drawn from them.

(e) *The extrapolation.* At `N = 19` neither the monodromy nor the counts can be computed. Weil's bound exceeds `p` for `j >= 2` (relative error `2^49.5` at `j = 2`).

The premise states that this `F` stays within `0.0003693` of the law of (a) (`q = 0.3931 <= 151/384 = 0.3932292`): no structure appears between the third layer and the 19-th that changes the law of the positive fixed points by 0.1%.

The measured deviations shrink like `p^(-1/2)` and do not grow with the degree. On the toy fields the deviation is `1.36 / sqrt(p)` . The counts of Grok job 139 give `eps ~ 3.1 / sqrt(p)` over degrees 5 to 1,953,125 (10.3).

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - S3)/2^256 = 1/2 - 7.869e-40` (`S3` of 4.1.1) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `S3` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - S3)/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`. This is a proved bound under the random words, not a premise and not a sample.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries e6dcb600 and 1aa56884, with the allowance and the organizer-run tests of gta6rp's entry 42dec7f5)

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 9,536,743,164,062`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.003` (`2^-8.38`).

Four fields (as in claim.json). **Role:** score-critical for the success probability only. The time and memory bounds hold for every sequence: stage D is charged for the normal sequence, every division tests its quotient and every call its return, and on any other case the trial ends after a prefix of the charged work (6.3). **Scope:** the pairs `(g_c, R_c - 1)` of the target `poseidon-orchard-r13-prefix-v1`, `c` uniform on `F_p`; nothing is claimed for other round counts. **Extrapolation and evidence:** for a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-166.8`. That bound does not transfer directly, because the coefficients of `R_c` have degree about `p` in those of `g_c`; the premise asserts far less than random-pair behaviour, an abnormality probability of at most `delta = 0.003`, which is all the bound of 9.2(d) uses (every `delta <= 0.0030999` keeps it at least 0.39). Measured support, organizer-run (10.5.1): the experiments `euclid-normal-n2-t256-l2-a` and `-b` compute the complete sequence of `(g_c, R_c - 1)` for this construction on the truncation `F_2` of the digest polynomial (10.3; `m = 12`) at 512 organizer-seeded centres each, and return a witness pair exactly when both sequences of a trial are normal; the one-centre tests also compute it at `m = 12` and `62`. Zero abnormal sequences in these runs is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.003` is the declared premise). Our runs of an earlier version of the program (its normality computation, before the one-centre tests were added): 1,066 sequences at `m = 12`, `62` and `312`, every quotient of degree 1 (10.5.1). Reported by our earlier entries, not organizer-run (10.5): the complete sequences on the sibling targets with `r' = 0` and `r' = 1` partial rounds (`m = 7,812` and `39,062`), every quotient of degree 1 in all 10 runs. **Limitations:** the organizer-run tests reach `m = 62` (our own runs `m = 312`, the sibling runs `m = 39,062`), far below `m = 9,536,743,164,062`. Normality is computed inside the submitted program; the runner checks only the returned witness pairs, so the tests are evidence under trusted execution of that program, which is printed in full in `experiments/exp_euclid.py`.

## 10. Evidence

This section is the evidence for the premise `H-ONE` and for the digest of the target. The computations of 10.3 are ours; the experiments of 10.2 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.2 The organizer experiments declared in `experiments/manifest.json`

Nine experiments of kind `python-message-pairs-v1` (five here, four in 10.5.1), run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The three Python sources are 60,921 bytes together (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r13-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run is the evidence: 256 of 256 trials returned a verified pair at r = 13, and the output was byte-identical on repetition. Our own earlier local run of the same events (plain Python on our machine) agreed: 256 of 256 trials.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 13: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining nineteen rounds applied to `alpha + beta W` (`deg F = 5^19`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-ONE` is about (a root of `g_c`). The count of returned pairs at each width is a reproducible observation of the construction's own antipodal pairs on the target; no probability, rate or population bound is drawn from it (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed), and it does not enter section 9.

The intake report of the organizer's run records 237, 125, 36, 15 of the 256 trials with a verified pair for `w` = 6, 8, 10, 12 respectively, and byte-identical output on repetition. 

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypotheses (a) and (b) of this section exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-ONE` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.

**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypotheses (a) and (b) of this section exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B. Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the construction's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 19`; the line and the first layers do not depend on r). The results:

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the construction's line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-ONE` (9.1) extrapolates the measured trend (`w = 1` at `N = 1, 2, 3` on the deployed constants, below) to `N = 19`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the construction's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend, and the lemma gives w = 1 or w = 2 given (a) and 2-transitivity.

**Grok job 139 (the counts of the premise on toy copies).** Grok (xAI) computed `N*` and `N_off` exactly for width-3 Hades toy permutations over prime fields `p < 2^22` with `p mod 5 != 1` (S-box `x -> x^5`, uniformly random MDS matrix and round constants, the line `(L, 2L+1, 3L+5)`, `N` full rounds and `k` partial rounds, `deg F = 5^(N+k)` up to 1,953,125), by the fibre counts `N* = sum_y m_y (m_y - 1)` and `N_off = sum_c 4 r(c) (r(c) - 1)` (checked against brute force on the small cases), on 1,316 generic seeds with `p >= 1024` (the five degenerate seeds, where the degree drops, are excluded). The relative error `eps_obs = max(|N*/p - 1|, |N_off/p - w|/w)` with `w = 1` is `<= 0.2197` for every generic seed with `p >= 2053`, and the least-squares fit is `eps_obs = 3.10 / sqrt(p)` for a typical seed (`5.17 / sqrt(p)` for the maximum of four seeds), with no dependence on the degree (adding a term linear in `deg F` moves `R^2` from 0.5508 to 0.5509; the mean of `eps sqrt(p)` is 2.3 to 3.7 for every degree from 5 to 1,953,125); at `p = 2,097,169` the largest generic `eps_obs` is 0.0068. These counts support the premise of 9.1: the deviations shrink like `3 / sqrt(p)` and do not grow with the degree.

### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 13` applies the Euclidean algorithm to `g_c` (degree `m = 9,536,743,164,062`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. This section and 10.5.1 are the measured support of the premise `H-NORMAL` (9.5): stage D is charged for the normal remainder sequence and a trial ends at the first quotient of degree other than 1 (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at the gcd (degree 0, or degree 1 at the r' = 0 centres 2, 4, 7) after `m - deg gcd` divisions, and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core.

At `r = 13` the stages need about 1232519 GB and 3.0e18 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7.

### 10.5.1 Organizer-run tests: normality and one centre (`experiments/exp_euclid.py`)

Four experiments of kind `python-message-pairs-v1`, declared in `experiments/manifest.json` and run by the organizer's runner (program `experiments/exp_euclid.py`, 28,019 bytes, Python standard library only): the normality tests `euclid-normal-n2-t256-l2-a` and `-b` (two centres per trial, `m = 12`, 512 sequences each) and the one-centre tests `one-centre-n2-t256` and `one-centre-n3-t24` (one trial of the algorithm at depth `N = 2` and `3`, `m = 12` and `62`). The design follows gta6rp's organizer-run normality tests (entry 42dec7f5, its 10.5.1); the program is our own. For each computed trial the program takes a centre `c` from the trial seed (the rule of `exp_line.py`) and builds, exactly over `F_p`, the polynomial `F_N(c + X)`: the `F_N` of 10.3 (start state `alpha + beta W` of the line `j = 0`, the S-box layers of rounds 2 and 3 (full), then 4 and 5 (partial, coordinate 0), the MDS after each; degree `5^N`). It checks `F_N` against direct iteration of those layers at `c + 1`, `c - 1`, `c + 2`, `c - 2` and the odd-part identity `2 x g(x^2) = F_N(c + x) - F_N(c - x)` at `x = 1, 2`; takes the monic odd part `g` (degree `m = (5^N - 1)/2`); computes `R = X^((p-1)/2) mod g` (253 squarings and 45 multiplications by `X`); and runs the complete Euclidean sequence of `(g, R - 1)` down to the zero remainder, recording the degree of every quotient. The sequence is normal when `deg(R - 1) = m - 1` and every quotient has degree 1, the condition of 6.3 and 9.5. A normality trial whose two sequences are normal, or a one-centre trial whose sequence is normal with `1 <= k(c) <= 16` and whose isolated root passes the check `F_N(c + s) = F_N(c - s)`, returns two distinct canonical messages: the points `c + s` of the line, `s = 1, 2, ...`, are mapped back to `(nk, rho)` as in 10.2(b), and the first two whose digests of the selected target agree on the first 6 bits of the big-endian reading are returned. Among 65 points such a pair always exists, so a computed normal trial always returns a pair. Every other trial, and every trial past the first `T` (`T` = 256, 256, 256, 24, the sandbox budget of 20 s), returns two nulls. The organizer-checked count of returned pairs therefore equals the number of computed trials that pass. The per-trial counts listed in the manifest are reported as observations, which the runner labels untrusted. Expected: every computed sequence is normal in the normality tests; for the one-centre tests the law of 9.3, a theorem at `N = 2` and `3`, gives the fraction of centres that pass, and the returned counts are reproducible observations consistent with it. No probability, rate or population bound is drawn from any of these organizer-seeded trials (public seeds; nothing is assumed about the trials being independent or identically distributed), and none enters section 9. These counts are reproducible observations consistent with the premises; the organizer-seeded centres are not treated as independent unselected samples, and no interval or population bound is drawn from them. For `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2` (its layers come before the final full rounds), so the tests measure the same family of pairs as the premise; only the witness uses the digest at r = 13.

Our runs of an earlier version of the program (its normality computation, before the one-centre tests were added; 2026-10-18, seeds of our own): in the runner's image `python:3.12.12-slim-bookworm` with one CPU and 128 MiB, 256, 24 and 2 sequences at `m = 12`, `62`, `312` in 4.6, 5.5 and 5.4 s of program time, byte-identical on repetition; with further seeds (Python 3.14), 512 more at `m = 12`, 256 at `m = 62` and 16 at `m = 312`. In all 1,066 sequences (768, 280 and 18) every quotient had degree 1, and the gcd had positive degree in 301, 117 and 7 of them (fractions 0.392, 0.418 and 0.389; observations of our own runs, not organizer-run, and not used in section 9). What these tests show: under trusted execution, the construction's own pairs `(g_c, R_c - 1)` have normal remainder sequences at `m = 12` to `312`. What they do not show: anything at `m = 9,536,743,164,062`, where `H-NORMAL` remains a premise that asserts only `delta = 0.003`.

## Appendix L: the line program `L` (this entry)

### L.1 Construction

`L(x) = F(x - E0_0) / OUTSCALE`, `F` the digest on the line of 2.2 (`W = tau^5`). The state after round 1 is `A + W B` (2.2: `alpha = A + c_2`, `beta = B`); the round-2 S-box input of lane `i` is `A_i + c_{2,i} + W B_i = B_i (W + E0_i)`, `E0_i = (A_i + c_{2,i}) / B_i` (every `B_i != 0` on the deployed constants). With `x = W + E0_0` lane 0 is `B_0 x` and lane `i` is `B_i (x + e_i)`, `e_i = E0_i - E0_0`: the program starts with `y1 = x + e1`, `y2 = x + e2` (2 additions) and holds lane `i` as `y_i` with the scale `B_i`. Every lane is held as its true value divided by a known nonzero scale: an S-box of a held lane is the true S-box output divided by the fifth power of the scale (3 multiplications), and the fifth powers are folded into the next linear layer, each output lane being held divided by its coefficient on `z0`: a dense layer with the next round's constants is `y_i = z0 + a_i z1 + b_i z2 + k_i` (2 multiplications, 3 additions per lane). Partial rounds use the sparse form of Grassi, Khovratovich, Rechberger, Roy and Schofnegger (USENIX Security 2021) with the same scaling, as in the r = 56 entries `3a1b25b6`, `9fb982e8` and `69e14209`: lane 0 is held as `lambda h0 + gamma`, lanes 1, 2 as `P (h1, h2) + q` with `P = Mww^j P0` after `j` partial rounds (`Mww` the lower-right 2x2 block of `M`) and `P0 = Mww^-r D`, `D` diagonal, so `P` is diagonal at the exit; one partial round is `u = h0 + k`, `x5 = u^5` (3 multiplications), `h0 = x5 + n1 h1 + n2 h2`, `h1 = h1 + v1 x5`, `h2 = h2 + v2 x5` (`h0` from the old `h1`, `h2`): 12 operations. Counts: entry 2; round 2 (S-boxes 9, dense layer with the round-3 constants 15); round 3 (S-boxes 9, into the partial form 6 multiplications and 6 additions, `D` normalising the `z0` coefficients); `r` partial rounds, 12 each; exit 3 (the round-60 constants); rounds 60-62 (24 each); round 63 (S-boxes 9, row 0 held divided by its `z0` coefficient `OUTSCALE`, 2 multiplications and 2 additions): `2 + 24 + 21 + 12 r + 3 + 72 + 13 = 135 + 12 r = 291`. Every constant is a closed formula of the deployed constants (the offline derivation of 6.2 prices the derivation of a literal; the 64 constants are derived once, offline, by the same rules, at most `64 * (2 * 330 + 40) = 44,800` field operations for the at most two inversions and the products of each, inside the declared cap of 6.2 together with its `137,169`).

### L.2 Check

`E0_0 = 0x3a4bd2e80f62c6cde67f816c4a67f17bbd43a70c4d2fca9784cc22ba736569ff`, `OUTSCALE = 0x229243618e7731895858a7e8b4c553ea614eb31d12b1f3b31f656fccb3c8e310`. Our program (standard library only) builds `L` from the organizer constants file, executes it, and asserts `OUTSCALE * L(W + E0_0) = digest(message(W))` with the reference rounds of `verifier/poseidon.py` at 100 random `W` (r = 13; also r = 0, 1, 3, 9 with `135 + 12 r` operations); `message(W)` is the canonical pair of 2.2 (`tau = W^e`, `(U, V) = Q + tau (a, b)`, `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`). An independent construction of the same form for r = 56 (the 807-operation step of `69e14209`) gives the same `OUTSCALE` at r = 3 when its round count is set to 3 (checked at r = 3 only).

### L.3 Stage B

The loop of stage B and its charges are those of the base entry except that each evaluation is one execution of `L` (`291` operations) at `c' + s` and `c' - s` (`c' = c + E0_0`, one addition per trial); the values become `g_c / OUTSCALE`, which the normalisation to monic absorbs.

### L.4 Code and static data added to the footprint

`L` once, as a subroutine used by stage B: 291 instructions, and its 114 constants at 32 bytes; the call site in the stage-B loop (at most 20 instructions); stage E of Appendix S (at most 1,100 instructions, 4,400 bytes). At most `4 * 291 + 32 * 114 + 80 + 4,400 < 16,384` bytes at r <= 22; `16,384` are added to the footprint (section 7).

### L.5 Constants of `L` at r = 13

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
k13 = 0x207a9d7da411c6e07aff7f01aa1788f0a603be328c30590aaf0f31e235b38a0c
k14 = 0x38bad5a821bc5617ea0398d5ece88db49f3972ea579012e3103e0b6b7f01c400
k15 = 0x08570cb0c0674e468f6819c78320791a4ec621a430df68d6d6c83ed641c7d884
k16 = 0x1a8067a6d7396a5429a2c879879be24bf753a057e715a11aea57a8658cbd7771
k17 = 0x34058bb8920441623716adeb0155288a2cca42fa34af13309820b9953e4336cf
k18 = 0x02dd8ff8d902421f1267deff8aede72bed98d9ad08aee5d754eb5677d87ddc87
k19 = 0x082e93f546affe9df050938b5d1fbc86e6168efb852afcbf04e61094b4697e80
k20 = 0x02f1f6d844ded9ae024fefe7bf480ceded243d98a36afcabd92a0a4459a215f6
k21 = 0x2b1591b30a8708595a89d86245cb767326818ce7516c57ae0232e004ef74d82f
k22 = 0x266144e217c50738f29b2b098b54686e360c94c1f64cc0b43c6b0a0cc37fc9eb
k23 = 0x24fcbddd30b1e2c31b280e3f1db7a5f7c3fbcfebd231f018711f0c9ae6f2a0e9
k24 = 0x204fedd345e5f52ea0c19430f1547569b151ebf2eee366a9d0a0ceb99491758f
k25 = 0x08ac5950af523d904f5e0de2523364d2ace6c29e0bb33b8a228b28a33de79cbd
k26 = 0x19f7a4a41358b3a0f760ca697fffc522bc78c8f6021be09851c44b229466771c
k27 = 0x1565f5ef914944ad12c16e36ec616abd4dd0f8c94d990dc4ff415ad5a506d732
k28 = 0x095740231c327ee0790f8b5ee74f97de10fc9b7e5e155798d934bfa5e56c7e36
k29 = 0x031edc1dba7e9d1513f6c97be80df9f73099b46e5f231a28e40c96ed193f82c3
k30 = 0x0ac74e7d4dee0f6152c4f27e5b3351731185b9a27d412c462a5a7fcd02468d0d
k31 = 0x126a6b5410f3149ce8e0b911239539985f989eeefce445a235b7d95270e44332
k32 = 0x31f134c3cb80372eff4d98f34741c78bf04e38ca64691c338f55660789f29b61
k33 = 0x3974ac5b900ed1c127b889b5ff231bccf9842414a47440ada7cc1f27c0bc779d
k34 = 0x2728ac0106fb27cb02bcc1c8b3e6863b0115a1e89ca790e13a4631f67e7f949d
k35 = 0x20f6d50f0298799a65c9629e322c17a995b58e47f4db999067368f23af143e1b
k36 = 0x0f11031569a53f36a311e2e01a21b96e96ed088cfaf1cab0fdc4824400f91e26
k37 = 0x2ca8302ed55720cd2a1b9478af5a5f4a223bd4fe9f778963e71519b2113aecb6
k38 = 0x1b023d46a48c055c28742aff1a92a1169c5c18efe5d18a81db1d0a955480014e
k39 = 0x010074fbe6ae00418ca5ce0c79607627aa1bf5796087407ec894ac88b6a8f19e
k40 = 0x05fc855684aa4f2b566bd97f0ff67f67bd8cc0e3cec523bd1b5e6019b6c49cd2
k41 = 0x13d9784844eb74765f988ce553e53b8b9f633949a875aaaba381fc5fbb1fc0c3
k42 = 0x0fb74a39edbf99a426252d65ab2f5b558bfc999d3ec24ddad0ab5d3c66a49cba
k43 = 0x03ca781f13169f6c784360d9c98ce7cfa064a51ca41448c610d6e6fb61b21dec
k44 = 0x19149d84b544934111b18acd4d7cbc3e105b3af48dba78fd12d8b18c6df29673
k45 = 0x17ed4e900d361a2dd8cd11e023f4c00eadf3d1d0adda2fb5b130b9f34197f47e
k46 = 0x3b71c4800d16010589b719389c6dc374bceffe51b49005cb11a92e52685615a2
k47 = 0x0111ad1e97070de2c1edeeacffc3a8f1f81c885c649e20b3955b4a2fac77be23
k48 = 0x14fc2d7c0ce9af4af9d366e0ff19bc2c73503af8cf667fb02c1885b8a68396bb
k49 = 0x15894eafc0a3419b79bbef666b2af04390f1b7cabb8cdb46400e6317fc33349f
k50 = 0x1e305194f13ecc3dbd329ea1e422b386f5d8a21728ee51510d376983cb4f864e
k51 = 0x2d341288974d6e06b7add32be95497a1e7e0ea00e3d9e20b4dbde5707b3cdeb5
k52 = 0x193745c8d553088262dcb58e17e3468dd24422f6a3987ac69306c8d2935e7ff2
k53 = 0x1ed0eb5c479953bf4bef9694c8bbe4ae8233aafa839a16814a402b24bd2fdcb1
k54 = 0x020652ceb326858a64d28c8f5fcf9148505d949cb409dab02e312efbb1a533dc
k55 = 0x322132f6200f32fbc03b6fbdb12ee04e74032e1ff062ffdbd83cf356daef6956
k56 = 0x3dba878538365aec7aabe6e07a2bab7b37069727fcff71125368041954577fd6
k57 = 0x35f659b85ed4e1f3c1c3e1f1fdde5ed7f9eb3b2b83d43f106d2416dba5965f7b
k58 = 0x026d449360a17d3f45925e70a3ffdb75fb19f58e696a9a49dcc4e55d24fb040f
k59 = 0x1075952e4a338459023e5f841131df30e3b066dfe55f947df00ada7d7bf1d88e
k60 = 0x0b8664db8938b65e95b5e1e395405c1e58570c78591c1e22809dee721a5e56c9
k61 = 0x35941d3fe6fa96730e6c1c4cb109e06af15e93edbdd25b4c73c65c2383be469c
k62 = 0x1fb04a7de4c56520f2aaf051fc8ec4eab6978daf4ad22c53ef4fde9bf6100f69
k63 = 0x26337af2d59f9b0116483f0134c72ef2d2ac5a1c4040562924222447bccf5a7d
k64 = 0x3f76366ee9ecb686dc9b3cfb340b638a4af027086c1443179d1f155ead66d0d7
k65 = 0x0441d016153dbb2de8e7d9eabbe2a70f8cf32bf38e3add525d4378efafb8436e
k66 = 0x16e2a5d47423a66bea12b6adf73d3df95cbaf68c77edc7c946e8bdc3c328fea9
k67 = 0x0194f78e9a984a28533ec9f0ef5d08ac0ef765a3eade233a3b45b21ae5fb06ee
k68 = 0x1bddf9d4239ebd1829ec9b13710eb904a837106dc4827f2faaae5bb360f919ba
k69 = 0x0c03edb606bd4a37cdd7d9ceffe32f97082d4562a06894ea62d53c641ced933a
k70 = 0x1276442d4ad4546a0b3283cc9626dca5ff3de5e6838cbf34acee5effc0816d4d
k71 = 0x09ef09baabc23389e8efafa60b51d6afd0bda04093eaf7fe2b19c5764f734815
k72 = 0x31a5317e72939ab937a13512d323f3d6e2545604b200351fe2c862a30e2c0059
k73 = 0x16f76f9a02eac3ef0b1eb28fcdb2cf2aeb7ebe32a5075f2d3eac24b4da94f9de
k74 = 0x36fdd64e2d385774400afd593045de0f616452efab12c476487c6170c7d5cb35
k75 = 0x3e78bc27237267f446059d4721a73338b6c21ba62d5c1d51286a20363063e013
k76 = 0x19a66114b2b40a72788b41701433d2b71e0c2efa597951132d856a900678747a
k77 = 0x1782f320036b1c7bc40a2dd19526d90235056921c75ac9170bfe77cd1becbcb2
k78 = 0x088f8afe6229d986dfca8063fb044d8e121717443ef2cf25fa7cfee6bcba58c8
k79 = 0x0bc1e912b2209adfd159ec64c1181a4f0a70b97b88016e532dcb6d7793eeb4d7
k80 = 0x1a5ea2c70cdefcc10c9dc95304639fb579c9cd24998632b229f8bb32104a5585
k81 = 0x13a7f4ab039b401ac45ca5ff27b089ce5eaeccf45660e89c70d1a38eb70278b7
k82 = 0x2f6fb6e19ae7da65012f16913b2dd427b1e8e312b4e56074e95988429572d9cc
k83 = 0x3f705b2e65e0320040a6aa9489fac62cc30a636607f4665f81e9b5fb2149b469
k84 = 0x2707f34face9c0d8f10ef280fa9aa7846cf29566f3d4d8da42b043d975cf4695
k85 = 0x09519782e54c487d6a2339432587ed6b2899c2a252654f6d3b69dfbc73ab0d24
k86 = 0x342f3d997264cd82cd3c749d436c2e3feda321ffd82abf0368c28adddc7a7242
k87 = 0x02ee1dd7c43d722a33b68c8ebf48fd717e6928054238b65a696e9eeda72abb21
k88 = 0x1e6b444a50e3a1204d0108d416e3593efb0f73e70d1289578bf3bcb30a268a49
k89 = 0x3d7f573cd9e6088c10f82dfd47c7314eec190ef96e04840815b97f5a330928ad
k90 = 0x3f5af9b7a0b903be025e8a7df8f0bb62331aa1597bf1d9b48c00215920e2b8b8
k91 = 0x06eeb82144fc434a5d069e15f31c6c3f00d7a86d4e940e4b98fedd5fe566adbd
k92 = 0x01a1574a9115b9109dac302372f2a9b25e40a20a39c7959da2dc2803129656f1
k93 = 0x2494fd25207686fc5b94c5a3297aa43c64596556c76d269518c8caba70cc9357
k94 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k95 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
k96 = 0x2e4381055c474772ed1aa2a94c351e4ac393d20ac070850393f39d8c292b77c2
k97 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
k98 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
k99 = 0x08430f76762d2789fe0e967473de6de1a3872b16b784cee50fdbeafc531b2e05
k100 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
k101 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
k102 = 0x04fedd23c28ecd379f6dca16cb8f86f5a10e0ae9820965cd6025744565007d64
k103 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k104 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
k105 = 0x273655f5e6350ba8661db840e3301b8f7f84ef750bbaa606828a8be89fff3fe7
k106 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
k107 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
k108 = 0x0e49fe19e0ad7fcad81e9d797a6305de4223eeeea840c8a0d6f25930833912b5
k109 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
k110 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
k111 = 0x08c9652137fae60dde120c7035ed51e0da41fa38c52bc2135f3003eafef9e931
k112 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k113 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
```

### L.6 Listing of `L` at r = 13 (291 operations; `x` is input and output; `e1 = k0`, `e2 = k1`)

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
ADD u, h0, k67
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k68
MUL t2, h2, k69
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k70
ADD h1, h1, t1
MUL t2, x5, k71
ADD h2, h2, t2
ADD u, h0, k72
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k73
MUL t2, h2, k74
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k75
ADD h1, h1, t1
MUL t2, x5, k76
ADD h2, h2, t2
ADD u, h0, k77
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k78
MUL t2, h2, k79
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k80
ADD h1, h1, t1
MUL t2, x5, k81
ADD h2, h2, t2
ADD y0, h0, k82
ADD y1, h1, k83
ADD y2, h2, k84
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k85
MUL t2, z2, k86
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k87
MUL t1, z1, k88
MUL t2, z2, k89
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k90
MUL t1, z1, k91
MUL t2, z2, k92
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k93
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k94
MUL t2, z2, k95
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k96
MUL t1, z1, k97
MUL t2, z2, k98
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k99
MUL t1, z1, k100
MUL t2, z2, k101
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k102
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k103
MUL t2, z2, k104
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k105
MUL t1, z1, k106
MUL t2, z2, k107
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k108
MUL t1, z1, k109
MUL t2, z2, k110
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k111
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k112
MUL t2, z2, k113
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

## Appendix B2: stage B on column passes (this entry)

This appendix replaces the charge of row B of `b8f4c780`; it changes how stage B is executed and charged, not what it computes. The output of stage B (the monic `g_c` in coefficient form, section 3), every other row of section 6, the arena of stages C and D, the premises `H-ONE` and `H-NORMAL`, the success bound and the experiments are unchanged.

**B2.1 What changes.** In the base package the `kappa` inverse transforms of size `B` and the four transforms of length `S` per position `j` of the geometric solve were charged butterfly by butterfly at the model's generic pass cost, and the point loop formed a bit-reversed store index for every point. Here every one of these transforms runs on the column passes that section 4.2 defines for stage C (a pass of `k <= 7` radix-2 layers over `2^k` rows at `cnt` positions with its `2^k - 1` twiddles in registers, charged `2 nb + 6` for the call, the kernel constant, the per-position charge times `cnt`, `F(cnt)`, and 3 per call plus 2 per loop for the loop of the calls; `ob3` for the radix-3 stage; the layers of a run split as section 4.2 of this package splits a run of column passes: `floor(L/7)` passes of seven layers and one pass of the remaining layers). Nothing is pruned (zero rows are transformed) and no twiddle-1 saving is taken, so the figures are upper bounds for these passes.

**B2.2 The stage, step by step** (notation of section 3; `B = 6,442,450,944`, `S` the smallest `2^a` or `3 * 2^a` with `S >= 2 kappa - 1`).

1. *Point loop* (natural order). For each coset `k < kappa` and `i < B`: `s = v_k zeta^i` and `1/(2s) = (2 v_k)^(-1) zeta^(-i)` by two running products, `x = c' + s`, `x' = c' - s` (`c' = c + E0_0`, formed once), the two evaluations of the program `L` of Appendix L (291 operations each), `y = (L(x) - L(x')) * (1/(2s))`, and one store of `y` at address `i * kappa + k` of the value array (coset-minor layout) with its address operation; per point `2 * 291 + 11` (2 additions, 1 subtraction, 3 multiplications, the store and its address 2, loop control 3), per coset 20.
2. *Inverse transforms.* The `kappa` inverse transforms of size `B` are made together, in place, as column passes across the cosets: the positions of a pass are the `kappa` cosets (contiguous in the coset-minor layout), its rows the transform index. Decimation in frequency: the input is in natural order and the output in the transform's order, so slot `sigma` of a coset then holds `w_k[j]` for the coefficient position `j = pi(sigma)`, `pi` the fixed digit-reversal permutation of the Good-Thomas layout (radix-3 stage and three rows of 31 radix-2 layers). The factor `1/B` is folded into `c_k` below.
3. *Solve*, in `B / 1,024` groups of 1,024 consecutive slots, in a group buffer of `S` rows of 1,024 positions (row = index of the correlation, position = slot). Per slot the position `j = pi(sigma)` is formed (digit reversal, charged 300) and `rho_j = 4^(-j)` (square-and-multiply on at most 33 bits, charged 400). (a) Gather: row `(-k) mod S` (`k < kappa`) of the buffer receives `w_k[j] * c_k * rho_j^k` with `c_k = z^(-C(k,2)) / (B M'(z^k))` (a table) and the running power `rho_j^k` (an array of 1,024 words), 10 operations per element with the address operations; this is `a_k z^(-C(k,2))` of section 3, because `W_k[j] = u_k^(-j) w_k[j]` and `u_k^(-j) = 4^(-kj) = rho_j^k`. The other `S - kappa` rows are set to zero (1 store per element); with the rows reversed in this way each correlation is one cyclic convolution of length `S`. (b) First correlation: forward transform of length `S`, product by the precomputed spectrum of the chirp `z^(C(n,2))` (a row constant: per row one load with its address, per element a load, a multiplication and a store), inverse transform. (c) Rows `i < kappa` multiplied by `z^(-C(i,2)) / S` and moved to row `(-i) mod S` for the second correlation (4 per element), the other `S - kappa` rows zeroed (1 store per element). (d) Second correlation with `(mu_1, ..., mu_kappa)` the same way. (e) Scatter: `h_t[j]` (row `t < kappa`, `j + tB <= m`) times `1/S` stored at `g[j + tB]`, the address from the row base and the slot's offset (6 per element). Per group 700 per slot and 1,000 of set-up.
4. *Once per trial:* the tables `c_k` and `z^(-C(i,2))/S` (two inversions per index, 2,640 each, and 40 per index), the chirp and `mu` (40 per index), their two spectra (two transforms of length `S` at `cnt = 1`, and `10 S`), allocations and set-up 10,000.
5. *Normalisation:* the leading coefficient tested (5) and inverted (2,640); per coefficient a load, a multiplication and a store with the address operations (6).

The interpolation is exactly that of section 3 (Lagrange interpolation at the geometric nodes `z^k`, two correlations); only the slot order of the inverse transforms and the per-slot factor `rho_j^k` are made explicit. The standard-library program `stageb_toy.py` below runs this sequence (inverse transforms with the slots permuted, the factors `rho_j^k`, both correlations as cyclic convolutions of length `S`) on random polynomials over the Pallas field at toy sizes and recovers every coefficient:

```
Bt 6 kappa 3 ok
Bt 12 kappa 5 ok
Bt 24 kappa 4 ok
Bt 8 kappa 7 ok
Bt 48 kappa 2 ok
```

**B2.3 Charges at r = 13** (`python3 stageb_count.py 13`; `m = 9,536,743,164,062`, `kappa = 1481`, `S = 3,072`, program `L` 291 operations):

| part | operations |
|---|---:|
| evaluations | 5,553,019,051,573,248 |
| point loop | 104,953,968,358,326 |
| inverse transforms | 611,009,765,049,352 |
| solve | 2,469,293,356,744,706 |
| constants | 8,478,420 |
| normalisation | 57,220,458,987,025 |
| **row B (this entry)** | **8,795,496,609,191,077** |

Row B of `b8f4c780`: `15,833,147,877,225,909`; the evaluations (`5,553,019,051,573,248`) are the same in both, so the whole difference, `7,037,651,268,034,832`, is in the loop work, the inverse transforms and the solve.

**B2.4 Ledger.** `N_max = 1,416,207,888,857,990,014 - 15,833,147,877,225,909 + 8,795,496,609,191,077 = 1,409,170,237,589,955,182`, `log2(N_max / 489) = 51.35586096282`, claimed `time_log2 = 51.35587` (rounded up at five decimals; was `51.36305`).

**B2.5 Memory.** The solve buffers (section 7, the added term): the group buffer (`1,024 * S` elements), the two spectra (`S` each), the two tables of `kappa` constants and three arrays of 1,024 words, each as its own slab slot: `134,807,552` bytes. Footprint `1,225,130,838,019,052 + 134,807,552 = 1,225,130,972,826,604` bytes, `log2 = 50.12185742`, claimed `memory_log2_bytes = 50.12186` (was `50.12186`). The value array and `g` are the two arrays of the base's stage B; the stage-B live set stays below the stage-C high-water mark that sets the pool.

**B2.6 The counting program** (`stageb_count.py`, standard library only) and its output at this r:

```python
"""Operation count of stage B (construction of g_c) with the geometric solve on column passes.
Standard library only.  Every charge is an integer; `python3 stageb_count.py R` prints the breakdown at R partial rounds."""
import sys

B = 3 * 2**31            # points per coset (transform size of the inverse transforms)
VCNT = 2**10            # positions per group of the solve (columns of the group buffer)

def F(cnt):              # loop control of a column pass, eight positions per pass (section 4.2)
    return 1 + 3 * (cnt // 8) + 2 + 3 * (cnt % 8) + 2

# column kernels of section 4.2: (rows, kernel constant, per-position charge)
COL = {7: (128, 269, 1600), 6: (64, 139, 704), 5: (32, 34, 304), 4: (16, 18, 128),
       3: (8, 10, 52), 2: (4, 6, 20), 1: (2, 5, 11)}
OB3 = (3, 7, 22)

def call(kern, cnt):     # one call: sc_ocall 2*nb + 6, kernel constant, per position, loop control, loop of calls 3
    nb, k0, kp = kern
    return 2 * nb + 6 + k0 + kp * cnt + F(cnt) + 3

def radix2_run(a, cnt):
    """a run of `a` radix-2 layers (rows of 2^a points) split as section 4.2 of this package splits a run:
    floor(a / 7) passes of seven layers and one pass of the remaining a mod 7 layers; returns the charge of the run
    for ONE row (2^(a-k) calls per pass of k layers), loop exits included."""
    ks = [7] * (a // 7) + ([a % 7] if a % 7 else [])
    return sum((2**a // 2**k) * call(COL[k], cnt) + 2 for k in ks)

def size_split(n):
    a, t = 0, n
    while t % 2 == 0:
        t //= 2; a += 1
    assert t in (1, 3), n
    return t, a

def col_transform(n, cnt):
    """one forward or inverse transform of length n (n = 2^a or 3 * 2^a) on `cnt` positions by column passes:
    the radix-3 stage (n/3 calls of ob3) and the radix-2 layers of each of the t rows; no pruning, no twiddle-1 saving."""
    t, a = size_split(n)
    c = 0
    if t == 3:
        c += (n // 3) * call(OB3, cnt) + 2
    c += t * radix2_run(a, cnt)
    return c

def row_pass_rowconst(n, cnt):
    """a pass over n rows of cnt positions that multiplies every element by a constant of its row:
    per row the constant loaded (load + address, 2), the call 2 + 6, the loop F(cnt) and 3 for the loop of rows;
    per element a load, a multiplication and a store (3)."""
    return n * (2 + 8 + F(cnt) + 3 + 3 * cnt) + 2

def S_of(kappa):
    best = None
    for a in range(0, 80):
        for v in (2**a, 3 * 2**a):
            if v >= 2 * kappa - 1 and (best is None or v < best):
                best = v
    return best

def count(r):
    D = 5**(6 + r); m = (D - 1) // 2
    kappa = -(-(m + 1) // B)
    S = S_of(kappa)
    ev = 135 + 12 * r
    out = {}
    # (1) point loop: per point 2 evaluations, 2 additions (c' + s, c' - s), 1 subtraction, 1 multiplication by 1/(2s),
    #     2 multiplications for the running s and 1/(2s), 1 store with its address (2), loop control 3: 2 ev + 11;
    #     per coset 20 (row set-up: v_k, 1/(2 v_k), the row base, loop control).
    out['evaluations'] = 2 * kappa * B * ev
    out['point loop'] = kappa * B * 11 + kappa * 20 + 2
    # (2) the kappa inverse transforms of size B, made together as column passes across the cosets (the value array
    #     is coset-minor: the value of point i of coset k is at i * kappa + k), cnt = kappa, in place, decimation in
    #     frequency (natural order in, transform order out), plus 1,000 for the driver.
    out['inverse transforms'] = col_transform(B, kappa) + 1000
    # (3) the solve, per group of VCNT slots (B / VCNT groups):
    G = B // VCNT
    per_group = 0
    # gather: rows k < kappa, per element load w, load and update the running power rho_j^k (load, mul, store),
    #   multiply by it and by the row constant c_k = z^(-C(k,2)) / M'(z^k), store: 10 per element (address included),
    #   per row 2 + 8 + F + 3; the rows kappa .. S-1 zero-filled: 1 store per element, per row 8 + F + 3.
    per_group += kappa * (13 + F(VCNT) + 10 * VCNT) + (S - kappa) * (11 + F(VCNT) + VCNT) + 4
    # first correlation: forward transform, pointwise by the chirp spectrum (row constant), inverse transform
    per_group += 2 * col_transform(S, VCNT) + row_pass_rowconst(S, VCNT)
    # between: rows i < kappa multiplied by z^(-C(i,2)) / S (row constant) and moved to the second correlation's layout
    #   (load, mul, store, 3 per element, plus 1 for the address of the moved row), rows kappa .. S-1 zero-filled
    per_group += kappa * (13 + F(VCNT) + 4 * VCNT) + (S - kappa) * (11 + F(VCNT) + VCNT) + 4
    # second correlation: forward transform, pointwise by the spectrum of (mu_1 .. mu_kappa) (row constant), inverse
    per_group += 2 * col_transform(S, VCNT) + row_pass_rowconst(S, VCNT)
    # scatter: rows t < kappa, per element load, multiplication by 1/S, store to g[j + tB] with its address formed
    #   from the row base and the slot's offset (load of the offset, addition): 6 per element; per row 13 + F
    per_group += kappa * (13 + F(VCNT) + 6 * VCNT) + 4
    # per group: the VCNT slot offsets j = pi(slot) (digit reversal, 300 each), rho_j = 4^(-j) and the running powers
    #   (exponentiation of 33 bits: 400 each), group set-up 1,000
    per_group += VCNT * 700 + 1000
    out['solve'] = G * per_group + 3 * G + 2
    # (4) once per trial: the constants c_k (two inversions at 2,640 each and 40 per index), the chirp z^(C(n,2)) for
    #     n < S and mu_i (40 per index), the two kernel spectra (two transforms of length S at cnt = 1, plus 10 S),
    #     the group buffer allocation and the stage set-up (10,000)
    out['constants'] = kappa * (2 * 2640 + 40) + 2 * S * 40 + 2 * (col_transform(S, 1) + 10 * S) + 10000
    # (5) normalisation: the leading coefficient tested (5) and inverted (2,640); per coefficient a load, a
    #     multiplication and a store with the address operations (6)
    out['normalisation'] = 6 * (m + 1) + 2645 + 2
    total = sum(out.values())
    return dict(r=r, m=m, kappa=kappa, S=S, ev=ev, parts=out, total=total)

if __name__ == '__main__':
    r = int(sys.argv[1])
    c = count(r)
    print('r', r, 'm', c['m'], 'kappa', c['kappa'], 'S', c['S'], 'program', c['ev'])
    for k, v in c['parts'].items():
        print('  %-20s %40s' % (k, format(v, ',')))
    print('  %-20s %40s' % ('row B', format(c['total'], ',')))
```

```
r 13 m 9536743164062 kappa 1481 S 3072 program 291
  evaluations                             5,553,019,051,573,248
  point loop                                104,953,968,358,326
  inverse transforms                        611,009,765,049,352
  solve                                   2,469,293,356,744,706
  constants                                           8,478,420
  normalisation                              57,220,458,987,025
  row B                                   8,795,496,609,191,077
```

**B2.7 The toy check** (`stageb_toy.py`, standard library only):

```python
"""Toy-size check of the stage-B solve of proof.md section 3 (Appendix B2): values of a random polynomial g on the
kappa cosets u_k <omega> (u_k = 4^k, omega of order Bt) -> per-coset inverse transforms (output in digit-reversed
slot order) -> per-slot scaling rho_j^k -> first correlation (chirp) -> scaling z^(-C(i,2)) -> second correlation (mu)
-> coefficients of g.  Pallas field, standard library only."""
import random
p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
def inv(a): return pow(a, p - 2, p)
def root(order):                      # an element of exact multiplicative order `order` (order | 3 * 2^32)
    g = pow(5, (p - 1) // order, p)
    for q in (2, 3):
        if order % q == 0: assert pow(g, order // q, p) != 1
    return g
def dft(a, w):                         # direct transform: A[t] = sum_i a[i] w^(i t)
    n = len(a); return [sum(a[i] * pow(w, i * t, p) for i in range(n)) % p for t in range(n)]
def cyc_conv(x, y, w):                 # cyclic convolution through transforms of length n with root w
    n = len(x); X = dft(x, w); Y = dft(y, w); Z = [a * b % p for a, b in zip(X, Y)]
    ni = inv(n); return [v * ni % p for v in dft(Z, inv(w))]
def digit_reverse_perm(Bt):            # any fixed permutation of the slots (the transform order); here bit reversal of
    a = Bt.bit_length() - 1            # the radix-2 part with the radix-3 digit last, as an example of a transform order
    if Bt == 2**a:
        return [int(format(i, '0%db' % a)[::-1], 2) for i in range(Bt)]
    t = Bt // 3; a = t.bit_length() - 1
    return [3 * int(format(i % t, '0%db' % a)[::-1], 2) + i // t for i in range(Bt)]
def run(Bt, kappa, trials=3, seed=1):
    rnd = random.Random(seed)
    for _ in range(trials):
        m = kappa * Bt - 1 - rnd.randrange(Bt)               # deg g = m, kappa = ceil((m + 1) / Bt)
        g = [rnd.randrange(p) for _ in range(m + 1)]
        omega = root(Bt); z = pow(4, Bt, p)
        # values on the cosets
        vals = [[sum(g[e] * pow(pow(4, k, p) * pow(omega, i, p) % p, e, p) for e in range(m + 1)) % p
                 for i in range(Bt)] for k in range(kappa)]
        # per-coset inverse transform; slot sigma holds coefficient position j = pi[sigma]
        pi = digit_reverse_perm(Bt); assert sorted(pi) == list(range(Bt))
        w = [[0] * Bt for _ in range(kappa)]
        for k in range(kappa):
            co = [v * inv(Bt) % p for v in dft(vals[k], inv(omega))]   # co[j] = u_k^j W_k[j]
            for s in range(Bt): w[k][s] = co[pi[s]]
        # constants of the solve
        S = min(v for v in [2**a for a in range(40)] + [3 * 2**a for a in range(40)] if v >= 2 * kappa - 1)
        wS = root(S)
        nodes = [pow(z, k, p) for k in range(kappa)]
        mu = [1]                                               # M(X) = prod (X - z^k), coefficients mu_0 .. mu_kappa
        for x in nodes:
            mu = [((mu[i - 1] if i > 0 else 0) - x * (mu[i] if i < len(mu) else 0)) % p for i in range(len(mu) + 1)]
        Mp = []
        for k in range(kappa):
            t = 1
            for l in range(kappa):
                if l != k: t = t * (nodes[k] - nodes[l]) % p
            Mp.append(t)
        C2 = lambda n: n * (n - 1) // 2
        ck = [pow(inv(z), C2(k), p) * inv(Mp[k]) % p for k in range(kappa)]
        chirp = [pow(z, C2(n), p) for n in range(S)]
        out = [0] * (kappa * Bt)
        for s in range(Bt):
            j = pi[s]; rho = inv(pow(4, j, p)); P = 1
            a = []
            for k in range(kappa):                             # gather: w * rho_j^k * c_k
                a.append(w[k][s] * P % p * ck[k] % p); P = P * rho % p
            # first correlation A(i) z^(C(i,2)) = sum_k a_k z^(C(k+i,2)), i < kappa, as a cyclic convolution of length S
            x = [0] * S
            for k in range(kappa): x[(-k) % S] = a[k]
            y = cyc_conv(x, chirp, wS)
            A = [y[i] * pow(inv(z), C2(i), p) % p for i in range(kappa)]
            # second correlation h_t = sum_{i > t} mu_i A(i - t - 1), t < kappa
            x2 = [0] * S; y2 = [0] * S
            for i in range(kappa): x2[(-i) % S] = A[i]
            for i in range(1, kappa + 1): y2[i - 1] = mu[i]
            hcon = cyc_conv(x2, y2, wS)
            for t in range(kappa):
                if j + t * Bt <= m: out[j + t * Bt] = hcon[t]
        assert out[:m + 1] == g, 'mismatch'
    return True
if __name__ == '__main__':
    for Bt, kappa in ((6, 3), (12, 5), (24, 4), (8, 7), (48, 2)):
        print('Bt', Bt, 'kappa', kappa, 'ok' if run(Bt, kappa) else 'FAIL')
```

