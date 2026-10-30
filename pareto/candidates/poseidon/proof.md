# Orchard Poseidon r3: 16-round root-isolation budget

## 1. Claim

Target: `poseidon-orchard-r3-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, three partial rounds 4, 5 and 6, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

Authorship and evidence provenance. This is 5kyguy's cap-16 derivative of mpjunior92 submission `1ac48175-29fa-4d12-8ec3-c1defb1f408f`, exact commit `fcd712f2344427d9fb99b2fbb12a4436451877f3`. The entire construction, register machine, line program L, stage-C/D accounting, arena and experiment sources are materially inherited from that package, itself derived from Jbenisek's `c6e5d126` and the credited contributions below. Our substantive change is the stopping rule of stage E: at most 16 fresh-shift splitting rounds instead of 64, aborting if no linear factor has been isolated. We recompute its finite failure bound, total coin count and resource ledger; H-ONE, H-NORMAL and all other stages stay the same. Every historical statement below about an executed run, local measurement, monodromy job, simulation, accepted predecessor or an earlier "our"/"we" result is the source authors' report, not a new execution or independently authenticated organizer result of this derivative. We have executed no participant code or compiler on the host. The preserved experiments must be rerun by the organizer; they do not certify full-scale success or the resource bounds. No full collision is claimed to have been produced. This ready exploratory package specifies an algorithm and a conditional resource/probability argument, not a proved break or accepted score.

* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation on `2^20` points and one inverse transform, replace `g_c` by its 17-fold Graeffe transform `g = g_c^(17)` (monic, degree `m`, its roots the `2^17`-th powers of those of `g_c`; section 4.3G), compute `R = S^((p-1)/2^18) mod g` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 477 * 2^11 = 976,896` points (477 of the 512 depth-9 nodes of the subgroup of order `2^20` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T; radix-32 and radix-64 passes under the 256 field registers of the declared register file, 4.2; every product transform of stages C and D with running twiddle factors in the block form of 4.2, passes of up to 7 layers, no twiddle table in either stage), take `G = gcd(g, R - 1)` by the inversion-free half-gcd on three rows of bradcush `4bcabff8` (outer step `k <= 2^16 - 1`, the matrix of each outer step applied by the cheapest of the plans of section 4.4, among them the direct whole-pair and fixed-slot plans of 0xplemonade's `ff21bd28`), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root `y` of `G` in at most `Z = 16` rounds, find `s` with `s^(2^18) = y` and `F(c + s) = F(c - s)` among at most `2^17` candidates (4.1.3), map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39026`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.001` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 0.001831054688`, `eps_coin <= 17 p / 2^512 <= 3.671e-77`, `eps_g <= 2^17 n' (D - 1) / p < 2^-196` (the centre makes `g` vanish at a point of `O1`, 4.3G) (sections 4.1.1, 4.3T, 9.2). The conservative lower bound is strictly greater than `0.39026894531` (above the organizer floor 0.39), claimed as `0.39026` by downward rounding (9.2).
* `time_log2 = 27.43502` in target-compression units (`C(3) = 279` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C a Graeffe prefix of 17 steps (4.3G) and value-domain powering on truncated point sets (4.3T), stage D the inversion-free half-gcd on three rows charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), stage E at its cap of `Z` rounds at degree `DMAX`, and the scan of stage F at its cap of `2^17` candidates (4.1.3). `N_max = 50,625,218,139` operations, `log2(N_max / 279) = 27.435015856...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 26.91115` (`126,200,572` bytes, section 7, rounded up at five decimals: the footprint of `c6e5d126` plus `16,384` bytes of code and static data for the line program, its constants, the stage-B root tables and the register-resident stage E). The normalized cost is `27.43502 + max(0, 26.91115 - 20) = 27.43502 + 6.91115 = 34.34617` (`c6e5d126`: `34.35841`).
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `17` field elements (`34` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^9`, then the roots of its odd part about a centre, found, after a Graeffe prefix (Dandelin-Graeffe root squaring), with a gcd against `S^((p-1)/2^18) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Historical source comparison (Jbenisek): against r = 3 entry `e4867cde` (normalized cost 34.39685, the same algorithm and package), one change in the node of the stage-D half-gcd (4.4). In each node the four chunks of each of `a`, `b` are folded onto the three rows `Y - 1`, `Y + 1`, `Y - i` in one loop (22 operations per position: four loads and three stores at 2 each, eight field operations) in place of a copy and three accumulating passes per row, and each matrix-vector map of the node is one two-output pass of 20 operations per point in place of two passes per output; the two loop bodies are `342` instructions, `1,368` bytes, added to the footprint (4.2, 7). Row D `10,416,313,186` (was `11,795,520,058`); row C, the allocation sequence and every other charge are unchanged; footprint `126,184,188` bytes (was `126,182,820`); time_log2 `27.44745` (was `27.48590`), normalized cost `34.35841` (was `34.39685`); H-ONE, H-NORMAL, the success bound and the experiments are unchanged.
* Historical source comparison (Jbenisek): against r = 3 entry `166e035c` (normalized cost 34.49126), three changes. (i) Its machine and passes: the wide block form of our r = 15 entry `c7ef0551` as 0xplemonade combines it with our block form (`56272e37`) in the entries `625bbb03`, `d4b13ccd` and `1dcbb731` (4.2): every block-form product pass of stages C and D has up to 7 layers (was 4; the last pass of a transform keeps at most 4), the passes of 7 layers first, then the remainder, then the last; position 0 of every block-form pass runs a straight-line variant whose `2^k - 1` twiddle-one butterflies take 2 operations, not 3; the register file grows to 391 words, 256 field registers (`2^7` values, `2^7 - 1` twiddles, one temporary) plus 135 integer registers (`2^7` row bases and 7 more, 4.2), `12,512` bytes, and the new straight-line bodies (5 to 7 layers, and the position-0 variants of 1 to 7 layers, forward and inverse, four copies each) add `166,592` bytes of code, both counted in the footprint (7). (ii) Stage C on that register file (4.3T, 4.3G; as 0xplemonade's r = 3 entry `7df03b8c` runs wider stage-C passes on it): the 20 layers split 4 | 5, 6 | 5 in place of 4 | 4, 4, 4 | 4 (our count of the 11 splits with middle passes of 4 to 7 layers and a bottom pass of 4 to 6), radix-32 and radix-64 middle blocks and 32-point bottom blocks with every twiddle in registers; the first copies of the new block bodies, `6,140` operations, are code in the footprint (4.2, 7). (iii) The apply of each outer step of stage D is the cheapest by charge of the plans of 4.4 and the direct whole-pair and fixed-slot apply plans of 0xplemonade's r = 10 entry `ff21bd28` (read as text, charged in our cost model, transforms of at most `3 * 2^16` points): 10 outer steps take a fixed-slot plan and 6 a direct plan; the bump arena of stage D grows to `1,441,792` words (4.4). Row C `39,693,958,128` (was `42,115,369,462`), row D `11,795,520,058` (was `13,044,814,819`), `N_max = 52,442,490,560` (was `56,113,196,655`); the footprint `126,182,820` bytes (was `125,904,496`), `2^26.91095` (was `2^26.90776`); the success bound and the experiments are unchanged. Our entry `166e035c` against our r = 3 entry `26797647` (normalized cost 34.53537), three changes to its algorithm: (i) every product pass of stages C and D (the Newton and quotient products of 4.3T, the node products and the applies of 4.4) runs in the block form with running twiddle factors of our r = 8 entry `27fbfbe7` (4.2), as 0xplemonade's r = 7 entry `dde74bba` does for the transforms of the half-gcd node; neither stage builds a twiddle table, so the stage-C table of the products (`2^16` entries) and the stage-D table (`2^18` entries) leave the work and the live set (7); (ii) the block loops of the transform passes of rows C and D are unrolled by four, a block charged 3 control in place of 5 (4.2), with `41,568` bytes of code (one 4-byte instruction per operation, 4.2) added to the footprint (7); (iii) stage B interpolates on `H = 2^20` points, the least transform size at or above `m + 1`, in place of `3 * 2^19` (section 3): row B `722,818,013` (was `1,075,093,735`). The machine declares its integer address registers: one register file of 90 words, 64 field registers of 256 bits plus 26 integer registers (4.2), `2,880` bytes counted in the footprint (7); every block is charged one address update per array index it advances beyond two (4.2); and the `576`-byte working set of the offline derivation (6.2, counted exactly there) is counted in the footprint. Row C `42,115,369,462` (was `42,602,465,472`), row D `13,044,814,819` (was `13,937,663,593`); the footprint `125,904,496` bytes is claimed rounded up at five decimals, `2^26.90776` (was `2^26.908` at three). The success side changes as well: the H-NORMAL allowance is `delta = 0.001` (was `0.003`, 9.5), as in our accepted r = 9 entry `5b96dbb5`, so the success bound is raised from `0.39009` to `0.39209` (9.2), and the organizer-counted H-ONE runs are euclid-gcdpos-n2-t256-a, -b and euclid-gcdpos-n3-t24 (10.5.1) in place of the one-centre-* runs; the time and the memory do not depend on this change. Our entry `26797647` against our r = 3 entry `6c151a2e` (normalized cost 34.58689), one change to its algorithm: the product step `M = M1 [[Q, 1], [b^2, 0]] M2` of each half-gcd node runs on the two rows `Y - 1`, `Y + 1` (`2n` points) in place of three; its entries have degree at most `2n - 1` on the normal sequence (4.4). Row D `13,937,663,593` (was `16,040,973,753`); every other row, the memory and the success bound are unchanged. Our entry `6c151a2e` made one change against our r = 3 entry `0c925670` (normalized cost 34.60828): a Graeffe prefix (4.3G). Stage C first applies 17 Graeffe steps `g(Y) <- E(Y)^2 - Y O(Y)^2` on `O1` (`124,876,887` operations each at that entry's charges; `123,570,391` each in this entry, 4.3G) and then raises `S` to `(p-1)/2^18` (219 squaring steps in place of 236); the gcd keeps exactly the `2^17`-th powers of the usable roots (`1 <= deg G <= k(c)`), and stage F finds the root of `g_c` above the isolated one by a scan of at most `2^17` candidates on the line map (4.1.3). Row C `42,602,465,472` (was `43,557,525,975`), row F `59,613,486` (was `47,012`); memory unchanged. `H-NORMAL` is stated for the pair of the transformed polynomial and its organizer-run tests compute that pair (9.5, 10.5.1); `H-ONE`, every other charge and the other experiments are unchanged.
* Historical source comparisons (Jbenisek): r = 3 entry `0c925670` and its predecessors replaced our filed r = 3 entry `95d8b186` (normalized cost 35.59204) by the same algorithm with three changes: (i) stage D is bradcush's inversion-free half-gcd on the rows `Y - 1`, `Y + 1`, `Y - i` (entry `4bcabff8`), ported and charged in this cost model (4.4), with the normal-sequence charging and the ABORT of bradcush `e6dcb600` as before, in place of the lean cofactor-free half-gcd with a memory cap; (ii) the transforms of stage C run radix-16 passes on the 64-register machine stated as a restriction in claim.json (4.2, 4.3T), the twist and `1/N` scalings are running products fused into the adjacent pass, the batch inversion of `k1` works in the scratch buffer of the stage, and the table of the Newton and quotient products is sized to their transforms (`3*2^17` points); (iii) a line evaluation of stage B is charged at its counted field operations, `155 + 21 r = 218` (section 3), in place of one target-compression unit. `95d8b186` is the one-centre algorithm of our r = 6 entry `c318f442` with the stage C of bradcush `b30de9bf`/`a41aecdd`, the memory schedule of 0xshikhar `52120fad` (each stage builds and frees the twiddle table of its own transforms) and the premises `H-ONE` at `q = 0.3931` and `H-NORMAL` at `delta = 0.003` (the split of cryptogakusei's entry `4888e783`, organizer-run tests in the form of gta6rp's entry `bef31fdd`); it replaced our executed r = 3 entry `bb9cca58`. Against our entry `253629b9` (normalized cost 34.82599), the same package, our entry `bcf8e01c` (normalized cost 34.77736) changes four things in the transforms of stage C (4.2, 4.3T): (a) the dropped row 15 of the top pass is formed in registers inside the top pass from the zero chunk of the coefficients, and the residues of row 14 at the `6,144` offsets above `n'` from the 14 complete rows, so the scratch is `6,144` words (from `71,680`); (b) `A` and `g` on `O2` are held as `delta_j A` and `delta_j^2 g`, so the step applies no node factor per point and `delta_j^-1` enters the inverse scaling of a block; (c) the point `x` of a 1-bit step is formed in registers; (d) one two-level table of the `2^21`-th roots (`3,072` words) serves every root lookup (from `4 x 4,096` words), `c^-1` being looked up once per group of 16 blocks. The memory is the allocator high-water mark of the one trial (section 7). Against `bcf8e01c`, the same algorithm and package, `0c925670` (34.60828) charges the loads and stores of the data words of the transform-pass blocks of 4.3T (top, middle and bottom passes) one operation each, base plus index (4.2): row C `43,557,525,975` (was `51,044,458,967`), row D `16,040,973,753` (was `16,119,330,233`, its applies on `O1` use the same transforms); memory unchanged; every other charge, the premises and the experiments are unchanged.
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres; `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.001` and supported by organizer-run tests. The machine (391 registers, 256 field registers of 256 bits plus 135 integer address registers, counted in the memory; constants as immediates; every load, store and spill counted) is stated as a restriction in claim.json, as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic (4.2). The costs are the declared cost model of this entry: the charging rules of section 4.2 with that register file, the half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6 (partial), 60, 61, 62, 63 (full) put nine S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^9 = D = 1,953,125`. The leading coefficient is obtained by propagating leading coefficients through the nine layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x11f9cfdeecb8c5965318cbdc58480d2e6db510f12862658af639ce81578c3e23` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 976,562`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). This gcd divides the squarefree `S^((p-1)/2) - 1`, so it is a product of `k(c)` distinct linear factors over `F_p` (9.1); stage D computes instead the gcd of 4.3G, whose roots are their `2^17`-th powers.

Construction of `g_c` by evaluation. `H = 1,048,576 = 2^20` divides `p - 1` (`p - 1 = 2^32 * 3 * q`) and `H >= m + 1 = 976,563`; it is the least transform size `2^a` or `3 * 2^a` at or above `m + 1`. Let `omega` be a primitive `H`-th root of unity and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`; one inverse transform of size `H` returns the coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 2,097,152` evaluations of `F` are each one execution of the straight-line program `L` of Appendix L: `L(x) = F(x - E0_0) / OUTSCALE` with fixed nonzero field constants `E0_0`, `OUTSCALE`, `135 + 12 r = 171` field operations at `r = 3` (107 multiplications, 64 additions; 64 constants as immediates; 18 working field registers), checked against the reference hash (Appendix L.2). With `c' = c + E0_0` (one addition per trial) the loop evaluates `L(c' + s) - L(c' - s) = 2 s g_c(s^2) / OUTSCALE`, so the interpolated polynomial is `g_c / OUTSCALE`; the normalisation to monic removes the constant and the leading-coefficient test is unchanged (`f_D(0) / OUTSCALE != 0`). The loop stores position `k` of the array, `k = 0 .. H-1` in order, with the value at `omega^(rev20(k))`, the input order of the inverse transform of row B (the order in which `c6e5d126` placed its values through the bit-reversed index); the point `s = zeta^(rev20(k))` and `1/(2s)` come from four 32-entry tables and their inverses (Appendix L.3), so no bit reversal is computed. Loop work per point (Appendix L.3): 360 operations including the two evaluations; the twiddle table of the transform is built by stage B as before (4.2).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

```text
init:   constants (once; no twiddle table: stage B builds the table of its transform; the product passes of stages C and D use running twiddle factors, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (2,097,152 evaluations of the program L of Appendix L + one inverse NTT of size 1,048,576 + the nonzero-leading-coefficient test + normalisation)
  C  g := g^(17): 17 Graeffe steps on O1 (section 4.3G); R := S^((p-1)/2^18) mod g, in the value domain on the truncated point sets O1, O2 of n' = 976,896 points (section 4.3T): 219 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd on three rows (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root y of G (4.1.2, register-resident, Appendix S); if none within Z = 16 rounds: trial ends.
  F  u := a 2^18-th root of y (18 Tonelli-Shanks square roots, 2-adicity 32); for j = 0, ..., 2^17 - 1: s := u mu^j, W1 = c + s, W2 = c - s, until F(W1) = F(W2), each side by the program L (4.1.3); tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (279 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 17` draws (`34` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 17 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 17 p / 2^512 <= 3.671e-77` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 16` rounds at degree `<= 16`; `eps_iso <= 0.001831054688` bounds the probability that 16 rounds fail to isolate a root when `deg G >= 1` (section 9.4). This entry runs the rounds register-resident (Appendix S): a round draws `a`, computes `B = (X + a)^((p-1)/2) mod H` by left-to-right square-and-multiply on the 253 bits below the top bit of `(p-1)/2` (253 squarings, 45 multiplications by `X + a`), forms `T = gcd(H, B - 1)` by inversion-free elimination with one inversion at the end, and keeps `T` when `1 <= deg T < deg H`, else keeps `H`; the current factor `H`, `B`, the square and the gcd rows (at most 100 field registers of the 256) never leave the register file, so every field operation is charged once and no load or store is charged inside a round. Charge of a round at degree `d <= 16`: at most `R(16) = 196,915` (Appendix S), against `2,595,011` in `c6e5d126`, whose stage E charged every field operation 10 (a memory-access convention) and ran a Taylor shift and two classical gcds per round.

4.1.3 Stage F: the root of `g_c` above `y`. By 4.3G, `y = S^(2^17)` for a usable root `S` of `g_c`, and the solutions of `S'^(2^17) = y` are `u^2 mu^(2j)`, `j < 2^17`, where `u^(2^18) = y` and `mu` is a fixed primitive `2^18`-th root of unity (`2^18 | p - 1`; a constant of the offline derivation, 6.2). `u` comes from 18 successive Tonelli-Shanks square roots: `y` is a `2^18`-th power, and if `x` is a `2^k`-th power with `1 <= k <= 18`, both square roots of `x` are `2^(k-1)`-th powers (`-1` is a `2^(k-1)`-th power, `2^k | p - 1`). The scan takes `s = u mu^j` for `j = 0, 1, ..., 2^17 - 1` and stops at the first `j` with `F(c + s) = F(c - s)` (two executions of the program `L` of Appendix L at `c' + s` and `c' - s`, `c' = c + E0_0`, compared: `L` is `F` up to the fixed nonzero factor `1/OUTSCALE`, so equality is the same test). For `S' = s^2` a root of `g_c` this holds, because `F(c + s) - F(c - s) = 2 s g_c(s^2)`, so the scan stops at the latest at the `j` of `S`; any stop has `s != 0` (`y != 0`) and `F(c + s) = F(c - s)`, a collision by 2.4. Charge per candidate: `s <- s mu` 1, `c' + s` and `c' - s` (into the input register of `L`) 2, two executions of `L` `2 * 171`, their calls 4, the move of the first result out of the register `x` 1, the comparison and branch 2, the loop control 3: `355` (`c6e5d126`: `448` with the dense evaluation of 218); at most `2^17` candidates, `46,530,560`, and the loop exit 2. The 18 square roots are charged `47,012` each (the whole row F of the algorithm without the prefix, a square root and the back-map), `846,216`, and the back-map `47,012`: row F = `47,423,790`.

### 4.2 Machine model and charging rules (summary; `C(3) = 279`)

Every field operation, load, store, control operation and random word is one primitive operation; `C(r) = 216 + 21 r = 279` primitive operations is one target-compression unit. The register file is the machine restriction of claim.json: one file of 391 words, 256 field registers of 256 bits plus 135 integer (address) registers, counted in the memory (7). The 135 integer registers are the most any kernel holds at once, counted kernel by kernel from the operands its charges read: a block-form product pass of up to 7 layers (4.2) holds 128 row bases j*2^l0, 1 data array index, 1 block loop bound, 2 position counter and bound, 1 layer counter, 1 twist index, 1 stack pointer (`135`); the others hold fewer: a radix-64 middle pass (4.3T) 72, the pointwise bottom pass on `O2` (4.3T) 42, the fused Graeffe bottom pass (4.3G) 41, the pointwise bottom pass on `O1` 40, a forward or inverse bottom pass 40, the top pass 21, the tail solve of row 14 19, the pointwise loop of an apply (4.4) 11, a chunked outer-transform call (4.4) 11, the 3-row CRT (4.4) 8; the loop counter and the address updates of an unrolled block loop use the block loop bound and the array indices. The field registers (they hold the `2^k` values and the `2^k - 1` twiddles of a radix-32 or radix-64 block or group, the 32 values and 31 twiddles of a bottom block, the 32-point blocks of `E` and `O` of a fused Graeffe bottom block with their 31 twiddles, or the `2^k` values, the `2^k - 1` twiddles and one temporary of a block-form product block, `k <= 7`; every other value is charged as a load or store, 2 operations each (the access and the addition of its address); a load or store of a data word of a block of a transform pass of 4.3T is one operation, its address the base plus index of the load or store itself: one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`; the transform passes of the Newton and quotient products of stage C and of the products of stage D run in the block form with running twiddle factors below, rows C and D of Appendix E) and the 135 integer registers are the only register assumption; the algorithm runs on one thread, no dispatch. The block loops of the transform passes of rows C and D are unrolled by four: a block is charged 3 control in place of 5 (the loop counter, test and branch, 3 operations per four blocks, charged 1 per block, and the 2 address updates; a block that advances more array indices is charged 1 more per index: the bottom block of a squaring step on `O2` 1 more (block array, `A2'`, `g~`), the fused Graeffe bottom block 1 more (`E`, `O`, output); a block loop of one or two blocks is straight code). This applies to the radix-32 and radix-64 middle blocks (4.3T: 307 and 707), the 32-point blocks of the bottom passes of 4.3T, the offsets of the top passes and of the tail solve of row 14 (4.3T: 277, 155, 125 and 60), the fused bottom block of a Graeffe step (4.3G) and the blocks of the block-form product passes of stages C and D (below); the fused pointwise passes, the pruned top passes of a Graeffe step and row B keep their charges. The three further copies of each unrolled body (the radix-32 and radix-64 middle blocks, the three top-pass and the tail-solve offset bodies, the seven bottom-pass blocks, the fused Graeffe bottom block, and the forward and inverse block-form product blocks of 1 to 4 layers, at their full charges) hold `21,585` primitive operations, one 4-byte instruction each (the instruction width of the machine declared by cryptogakusei `1533f8f0`, its H2): `86,340` bytes of code, added to the footprint (section 7); the first copies of the bodies new against the radix-16 program text (the radix-32 and radix-64 middle blocks, the 32-point bottom blocks and the fused Graeffe bottom block) `6,140` operations, `24,560` bytes, also added. The block-form bodies of 5 to 7 layers and the position-0 variants of 1 to 7 layers (below; forward and inverse, the body and its three unrolled copies, at their charges) hold `41,648` further primitive operations: `166,592` bytes of code, also added to the footprint (section 7). The two straight-line row bodies of the node (4.4: the fold row of `8 * 22 + 3 = 179` and the two-output row of `8 * 20 + 3 = 163` operations, eight positions each) are `342` instructions, `1,368` bytes, added to the footprint (section 7). Allocation: one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes. A block of more than `2^10` bytes is served by the two-ended pool (one region, two ends, first-fit in address order, the statements marked `# pool:H` using the high end and, with the depth-parity placement of section 7, the end `(j + bit8) mod 2` of a half-gcd node at depth `j`); every smaller block by its slab class (the least `j >= 7` with `2^j >= need`, a slot of `2^j` bytes). The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows (a pool request `97` operations besides the walk and `13` per block examined, a slab request at most `126`, a free `81` for a slab block and at most `105` for a pool block). The memory of both allocators is the arena of section 7. Twiddle tables: none is built in init; stage B builds the table of its transform (`2^19` entries for its `2^20` points: its root, 5 operations per entry and the loop) and frees it, charged in row B. Every product pass of stages C and D (the Newton and quotient products of stage C, 4.3T; the node products and the applies of stage D, 4.4) forms its twiddles as running factors, in the block form of our r = 8 entry `27fbfbe7` (as 0xplemonade `dde74bba` uses it for the transforms of the half-gcd node): per pass and layer the step and chain constants (`150` operations: at most 64 squarings, the loop, 4 loads and stores); per position `j` (`2^(a-l0-k)` of them) the running root advanced by one multiplication, `k - 1` squarings and `2^k - 1 - k` multiplications by register constants give its `2^k - 1` twiddles, kept in registers, plus 5 control (`2^k + 4`); the `2^l0` blocks that share them each load `2^k` values and store `2^k` values at one operation each (base plus index), make `k 2^(k-1)` butterflies at 3, plus 3 control (the block loop unrolled by four) (`2 * 2^k + 3 k 2^(k-1) + 3`); at position 0 (running root 1) the `2^l0` blocks run a straight-line variant whose `2^k - 1` twiddle-one butterflies take 2 operations (an addition and a subtraction), not 3, so a pass is charged `2^l0 (2^k - 1)` less. Pass widths: a transform of `2^a` points runs a last pass of `min(4, a)` layers (the fused pointwise pass where there is one) and above it passes of at most `k = 7` layers, the passes of 7 first, then the remainder, then the last (`a = 15`: 7, 4, 4; `a = 17`: 7, 6, 4; `a = 20`: 7, 7, 2, 4); the pass constant `c0 = 4` is the same for every `k`. Besides its blocks and positions, each block-form pass of `k` layers is charged `159 k + 19` (forward) or `159 k + 20` (inverse): the `150` per layer above, `9 k + 2` for its layer setup, and its call, entry, exit and pointers. Stages C and D build no twiddle table; the passes of 4.3T use one two-level table of the `2^21`-th roots of unity `psi^e` (`2^11 + 2^10 = 3,072` words, `psi^(1024 a)` and `psi^b`: a root is two loads and one multiplication, an inverse root also the negated exponent, 1 operation), built in stage C and kept for the applies of stage D on `O1`, which frees it.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(17)`, 17 Graeffe steps, then computes `R = S^e mod g^(17)`, `e = (p-1)/2^18` (2-adicity 32), and stage D takes `G = gcd(g^(17), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^17)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(17)(Y) = prod_i (Y - S_i^(2^17))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^18`-th powers of `F_p^*`. If `S_i^(2^17) = u^(2^18)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^17) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^18) = 1` (`2^18 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^17) = v^(2^18)`. So `deg G` is the number of distinct `2^17`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input chunks below the length (8 or 7 of the 16 per offset, two offset ranges; no zero-fill) and form the 15 present rows; the fused bottom pass forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point; the 32-point blocks of `E` and `O` and their 31 twiddles fit the 256 field registers); one truncated inverse (row 15 formed in registers, the tail solve of row 14 and the recoveries of 4.3T) stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a scratch of `6,144` words of their own (allocated and zero-filled for the prefix, freed after it); no array is added and the high-water mark of section 7 is unchanged. One step is `116,019,127` operations (Appendix E.1), 17 steps; stage C then runs 219 squaring steps in place of 236 (the exponent loses 17 low zero bits). A step saves one squaring step (`168,893,024`) for `116,019,127` and doubles the scan of 4.1.3 (`2^s * 448` in `c6e5d126`); `s = 17` minimised the total there. With the scan at `355` per candidate (4.1.3) an 18th step would save a further `52,873,897 - 46,530,560 = 6,343,337` operations, but it would change the transformed pair of the premise `H-NORMAL` and its organizer-run tests (`-g17`); this entry keeps `s = 17` and the premises and experiments of `c6e5d126` unchanged.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(17)`: `g^(17)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^17` values `x` with `x^(2^17) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(17) vanishes on O1) <= 2^17 n' (D - 1) / p = eps_g < 2^-196`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 477 of 512 nodes)

Point sets. `N = 2^20` divides `p - 1` (2-adicity 32). Let `psi` have order `2^21`, `H_N = <psi^2>` and `Y = X^(2^11)`. `H_N` is the union of the 512 depth-9 nodes `{x : x^(2^11) = r_j}`, `r_j` the 512-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 477 nodes, `n' = 477 * 2^11 = 976,896 >= m + 1 = 976,563` points, and `O2` the same 477 nodes of the coset `psi H_N` (`x^(2^11) = r'_j`, `r'_j^512 = -1`), disjoint from `O1`. `P1 = prod_{j<477} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (477 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<512} P_k Y^k` with `deg P_k < 2^11` and `P_k = 0` for `k >= 477`; its values on the 477 nodes determine it and are determined by it (the CRT for the 477 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 4 layers on all `N/16` offsets, the middle layers only on the blocks above present nodes, and the bottom 5 layers on the `n'` points; the inverse runs the same layers in reverse. The dropped part `[477, 512)` is the maximal subtrees `{480..511}` (row 15 of the top pass, depth 4) and `{478..479}`, `{477}` (depths 8 and 9, inside row 14). Row 15 is never stored. Write `y_j(o)` for the residue of row `j` at offset `o < N/16` and `F_k(o)` for the coefficient at position `k N/16 + o`: `y_j(o) = sum_k F_k(o) r_j^k` over the 16 depth-4 roots `r_j` (the 16th roots of unity on `O1`, the 16 roots of `r^16 = -1` on `O2`), and `F_15(o) = 0` since the degree is `< n' <= 15 N/16`; so `sum_j r_j y_j(o) = 0` and `y_15(o) = sum_{j<15} c_j y_j(o)` with `c_j = -r_j / r_15`, the 16th roots of unity other than `-1`, one of them `1`. The top pass forms `y_15` in registers (14 multiplications by register constants and 14 additions, 28 per offset) and forms only the 15 nonzero chunks of the inverse and the 15 present rows of the forward (pruned 16-point butterflies: 94 and 92 field operations in place of 96). At the `6,144` offsets `o >= 59,392` the chunk `F_14(o)` is zero as well (`14 N/16 + o >= n'`); the two equations give `y_14(o) = sum_{j<14} alpha_j y_j(o)` with fixed constants `alpha_j` (the 2 x 2 system in `y_14`, `y_15` has determinant `r_14^-15 r_15^-15 (r_14 - r_15) != 0`), formed from the 14 complete rows before row 14 is finished (the tail solve: per offset 14 loads, 14 multiplications, 13 additions, one store and 3 of control (the offset loop unrolled by four, 4.2), 60; the 14 constants loaded once per pass). From these residues the inverse recovers the subtrees `{477}` and `{478..479}` inside row 14 along their paths below the top pass (layers 4 to 8 and 4 to 7), charged 10 operations (3 multiplications, 3 additions, a load and a store) per point per layer, as bradcush recovers the one dropped node. The passes are fused as in `b30de9bf` 4.5 under the 256 field registers of the declared register file (4.2), the 20 layers split 4 | 5, 6 | 5 (the cheapest by charge of the splits with middle passes of 4 to 7 layers and a bottom pass of 4 to 6): a bottom pass (32-point blocks: forward layers, the pointwise map, inverse layers; one set of 31 twiddles for both directions, 35 operations per block: two loads from the two-level table, one multiplication, four squarings, 26 multiplications by register constants; `V^T V = 32 diag(1, cJ)` with `c = y^32` of the block, so every inverse bottom pass scales each block by `diag(1, c^-1 J)`: 31 multiplications and the factor `c^-1`; the blocks `m = 16 q + r` of an aligned group of 16 (the children of one depth-11 node) have `c_m^-1 = c_{16q}^-1 zeta^-bitrev4(r)`, so `c_{16q}^-1` is looked up once per group (the negated exponent, two loads, one multiplication: 6) and multiplied by a register constant per block (none for `r = 0`): 32 operations per block and 5 per group), two middle passes of radix 32 and 64 (per block `2^k` loads and `2^k` stores, one operation each with the base-plus-index address (4.2), `k 2^(k-1)` butterflies and 3 control (the block loop unrolled by four, 4.2), 307 and 707; the `2^k - 1` twiddles of a group in registers (two loads and one multiplication from the two-level table, `k - 1` squarings, `2^k - 1 - k` multiplications by register constants, 5 control), 40 and 72 per group), and a top pass over all `N/16` offsets that fuses the inverse top of one set with the forward top of the other (the 16 values, the 31 coset constants, the 14 constants `c_j != 1` and one temporary: 62 of the 256 field registers; per offset 15 loads and 15 stores, one operation each (4.2), 28 for row 15, 94 for the inverse, 30 for the twist of the 15 nonzero chunks, 92 for the forward and 3 of control (the offset loop unrolled by four, 4.2): 277; the unfused inverse top 155; the forward from coefficient form 125, a cleared register (1) in place of the load (1) at the 6,144 offsets whose chunk-14 position is at or above `n'`).

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). On `O2` the algorithm holds `A2' = delta_j A2` and `g~ = delta_j^2 g`: then `B2' = A2'^2 + U g~ = delta_j^2 (A2^2 + U g) = delta_j B2`, which is the next `A2'` (times `x` on a 1-bit), so no node factor is applied per point; the inverse bottom pass on `O2` scales each block by `diag(e, e c^-1 J)` with `e = delta_j^-1` (a block of 16 points lies in one node: one more multiplication per block, and per group of 16 blocks the load of `delta_j^-1` and its product with `c_{16q}^-1`, 3). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2', sqr, LD g~, mul, add, ST` (9), and per block one address update beyond the block control (4.2); 2 more for a 1-bit: `x = y zeta^e` from the base `y` of the block and a register constant (no multiplication for `zeta^0`) and the product `x B2'`.

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each, the scaling a running product fused into its first pass, 2 operations per point), then `g~ = delta_j^2 g` on `O2` (per node the load of `delta_j` and a squaring, per point a load, a multiplication and a store). The start residue is `A0 = X^v P1 mod g`, `v = 2^17 = 131,072` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 131,407` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^17` points with running twiddle factors in the block form of 4.2); on node `j` of `O2`, `x^v P1(x) = r'_j^64 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0' = delta_j A0` (per node a load, per point 5) and `A0` goes to `O1` (its inverse on `O2` with `e = delta_j^-1`). `k1` is formed by chunked batch inversion on `O1` (chunks of `6,144` points, 159 chunks: prefix products, held in the scratch buffer of the stage, one inversion, two multiplications per point); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-196` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`, forming `delta_j B2 = delta_j A2' + U g~` on `O2`, 11 per point with the load of `delta_j`) and two truncated inverses with their scaling (`e = delta_j^-1` for `R`, `e = delta_j^-2` for `g~`: one more squaring per group), which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `219` squaring steps (the exponent `(p-1)/2^18`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 477 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g~` on `O2`, `A2'` on `O2`, `A` on `O1`, `k1` on `O1`), the tables (`984 + 3,072` words: 30 constants, the 477 `delta_j` and the 477 `delta_j^-1`, the two-level root table), and one scratch buffer of `15 N/16 - n' = 6,144` words (zero-filled once) that extends the array being transformed to the positions of row 14 at or above `n'`, which the first middle pass (`983,040` positions), the tail solve and the recovered subtrees `{477}`, `{478..479}` use (one transform runs at a time, so the in-place schedule needs no other storage; row 15 exists only in registers inside the top pass), and which holds the prefix products of one batch-inversion chunk (`6,144` points). The step-by-step count is expanded in Appendix E.1 and totals **row C = 39,693,958,128** (section 6).

### 4.4 Stage D: the inversion-free half-gcd on three rows (bradcush `4bcabff8`)

`G = gcd(g, R - 1)` is computed by bradcush's inversion-free half-gcd (entry `4bcabff8`, read as text only; ported and charged in this cost model). Matrices and remainders are kept up to scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside the recursion. A node of budget `k = 2^j - 1` makes two child calls of budget `2^(j-1) - 1`; with `n = 2^(j-1)` and `Y = X^n` its products run on the rows `Y - 1`, `Y + 1`, `Y - i`, each a power-of-two transform of `n` points in the block form of 4.2 after a twist: `(c, d) = adj(M1)(a, b)` on the top window on all three rows (`3n` points, 3-row CRT), the pseudo-division, and the product `M = M1 [[Q, 1], [b^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and `b^2` is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the row `Y - 1` values of each child's matrix are returned by the child, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). Two loops of the node are single passes. Fold: the window `a` of `4n` coefficients (`b` has `4n - 1`) is reduced modulo `X^n - 1`, `X^n + 1` and `X^n - i` in one loop over the positions `t < n`: it loads `a_0 = a[t]`, `a_1 = a[t + n]`, `a_2 = a[t + 2n]`, `a_3 = a[t + 3n]`, forms `s = a_0 + a_2`, `s' = a_1 + a_3`, `u = a_0 - a_2`, `u' = a_1 - a_3` and stores `s + s'` (row `Y - 1`), `s - s'` (row `Y + 1`) and `u + i u'` (row `Y - i`, `i^2 = -1`, one multiplication), which are `a mod (X^n - c)` for `c = 1, -1, i` because `X^(jn) = c^j` there. It is charged 22 per position (four loads and three stores, each with its address update, 2 operations, and eight field operations) and `2 + for8(n)` for the eight-element loop; the twist of the rows `Y + 1` and `Y - i` by their running factors is charged as before, 2 per point and row. Pointwise maps: on each of the three rows one pass forms `C = r22 A - r12 B` and `D = r11 B - r21 A` from the row values of `a`, `b` and the four entries of `M1`, and on each of the two rows of the product two passes form the two columns of `M = P M2`, `P = M1 [[Q, 1], [b^2, 0]]`, from the entries of `P` and the column of `M2`; each is one two-output pass (six loads, four multiplications, a subtraction, an addition and two stores over the operands), charged 20 per point as the direct whole-pair row of 0xplemonade's `ff21bd28` (read as text), and `2 + for8(n)` for the loop. The bodies of the two loops (eight positions each) are code (4.2). The base case (budget 63) runs two remainder steps per pass over its window (the second reads the first remainder from registers). The driver calls `hgcd(a, b, k)` on the top window with `k = 2^j - 1 <= 2^16 - 1` the largest with `2k + 1 <= deg a`, applies the returned matrix to the whole pair by the cheapest of three transforms and the two apply plans below (the truncated set `O1` of 4.3T with its root table, `2^a` or `3 * 2^a` points; the matrix entries row-wise in rows of `2^16` when the transform has at least `2^17` points), and repeats; below degree `2 * 63 + 1` classical division steps finish and `G` is normalised. Apply plans of 0xplemonade's `ff21bd28` (read as text, charged in this cost model). With `h = k`, `(c, d) = adj(M)(a, b)` has `lc = la - h` coefficients (the high coefficients cancel). A plan uses one transform size `N = 2^e` or `3 * 2^e` with `2(h + 1) <= N <= 3 * 2^16` and one of two forms; every such size and both forms are priced and the cheapest of these and of the three transforms above is taken (8 arena operations and 20 control per apply besides). A transform of an array of `l <= N` coefficients into an `N`-word spectrum is 6 plus, for `3 * 2^e`, the radix-3 input stage over the `l` coefficients and three rows of block-form passes, or, for `2^e`, the copy of the `l` coefficients, the zero-fill of the other `N - l` words and one row of passes (4.2); an inverse is 3 plus the inverse passes (and the radix-3 output stage over the coefficients formed); the store of `t` outputs with `1/N` into their array is `8t + 5`. Both forms first transform the four entries of `M` (`h + 1` coefficients each) into four matrix spectra and form `1/N` by one inversion. (i) Direct whole-pair (`N >= lc`): `a` and `b` are folded modulo `X^N - 1` (a copy and an addition per coefficient beyond `N`) and transformed into the operand spectra `A`, `B`; one pass over the `N` points forms `C = r22 A - r12 B` over `A` and `D = r11 B - r21 A` over `B` (six loads and two stores at 2, four multiplications, a subtraction and an addition: 22 per point, and the loop); two inverses and the stores give `c` and `d` exactly, since their degree is below `lc <= N`. (ii) Fixed-slot (`B = N - h > 0`): the outputs are cut into `nb = ceil(lc / B)` blocks of `B` coefficients, handled from the highest to the lowest (`3 nb + 6` of loop control); block `i` transforms the windows `[max(0, iB - h), min((i + 1) B, lc))` of `a` and of `b` (at most `N` coefficients) into `A` and `B`, forms `C` and `D` in one pass (22 per point and the loop), inverts both, and stores its `B` outputs of `c` and `d` over the operand arrays (20 control per block); the cyclic product of a window of at most `N` coefficients with an entry of `h + 1` coefficients differs from the true product only in its lowest `h` positions, below the `B` outputs the block keeps, and a lower block reads only operand positions below the outputs already stored. Every working array of the half-gcd lives in one bump arena (an allocation or release is 10 operations) of `1,441,792` words, the peak of the recursion and of the applies (an outer step of budget `2^16 - 1` on an apply plan: the matrix, `4 * 2^16` words, and the four matrix spectra and two operand/output spectra of `3 * 2^16` words).

Charges (Appendix E.2): field operation 1, load or store 2, loop control `3 n + 2`, the passes of section 4.2 for the row transforms, the truncated transforms of 4.3T for an apply on `O1`; the twist of a row and the `1/n` of an inverse are running products fused into the adjacent loop (2 operations per point, 1 for `1/n` alone). Appendix E.3 lists the outer steps with their budgets, charges and apply plans: 28 outer steps (13 at `k = 65,535`) and the classical tail from degree 206. On the normal sequence every length, budget and allocation is a function of `m` alone.

The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter (2 operations each), and a zero remainder met inside a budgeted `hgcd` call ABORTs that trial. In the classical tail, the first zero remainder is instead the ordinary successful Euclidean termination: return the preceding nonzero divisor, normalised to monic `G`, and proceed to the existing stage-E degree guard. An abnormal quotient still ABORTs before division (section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The total is **row D = 10,416,313,186** (section 6.3, 6).

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^17)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (primitive operations; `C(3) = 279`)

| row | what is charged | operations |
| --- | --- | --- |
| init | constants and bookkeeping (once; no twiddle table, 4.2) | 17,987 |
| setup | the line (`line_setup`, once) | 4,910 |
| A (per trial) | stage bookkeeping, loop test and update, the coin draw (63, two words), one allocation | 1,228 |
| B (per trial) | `2,097,152` evaluations of `F` by the program `L` of Appendix L (171 operations each), the loop work (360 per point in all, Appendix L.3), the root tables, the twiddle table and the inverse transform of size `1,048,576`, the normalisation (section 6) | 459,872,141 |
| C (per trial) | the Graeffe prefix, 17 steps (section 4.3G), then `S^((p-1)/2^18) mod g` in the value domain on the truncated point sets `O1`, `O2` (477 of 512 nodes, `n' = 976,896`), VSHIFT = 2, 219 squaring steps, radix-32/64 passes, the dropped row formed in the top pass, `A` on `O2` held as `delta_j A` (section 4.3T); expanded in Appendix E | 39,693,958,128 |
| D (per trial) | inversion-free half-gcd of `(g, R - 1)` on three rows, the product step of each node on two (4.4), charged for the normal remainder sequence with the quotient and return tests (sections 4.4, 6.3), product passes in block form (4.2), applies by the plans of 4.4 and of `ff21bd28`; expanded in Appendix E | 10,416,313,186 |
| E (per trial, cap) | `Z = 16` rounds at degree `DMAX = 16`, register-resident, each at most `R(16) = 196,915` with its draw of 63 (two words) (4.1.2, Appendix S), the stage bookkeeping 1,000 and the load of `G` into registers 200 | 3,151,840 |
| F (per trial) | the `2^18`-th root of `y` (18 square roots at 47,012), the scan of at most `2^17` candidates at 355 and its exit, the back-map 47,012 (4.1.3) | 47,423,790 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 279 + 32` | 6,612 |
| trial-loop (per trial) | trial-loop bookkeeping (12) and the allocator reset after an ABORT (1,000), charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size | 77,225 |
| output rows | the fixed output rows (stages H and I) | 3,390,080 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 1 * T_trial + T_off` | **50,625,218,139** |

`T_off = 1,000,000` (the declared cap; the original constants take `137,169`, with L the bound is `337,753`, 6.2); `T_trial = A + B + C + D + E + F + G + trial-loop = 50,620,727,937`; `T_fixed = init + setup + plan_invN misses + output rows = 3,490,202`; `K = 1`, so `N_max = 3,490,202 + 50,620,727,937 + 1,000,000 = 50,625,218,139`. `log2(N_max / 279) = 27.435015856...`, rounded up at five decimals to `27.43502`. Against direct parent `1ac48175` (`50,634,670,059`), only row E changes by `-48 * 196,915 = -9,451,920`; every other row and the memory upper bound are retained. Against earlier `c6e5d126` (`51,063,283,688`): row B `-262,945,872`, row E `-162,929,981`, row F `-12,189,696`; every other row is unchanged. Rows C and D are expanded part by part in Appendix E (E.1, E.2) from the dimensions of 4.3T and the half-gcd levels with the kernel charges of 4.2; the parts add up exactly to `39,693,958,128` and `10,416,313,186`. Row B is the row of our entry `26797647` with the stage-B size changed from `3 * 2^19` to `2^20` points, each part counted for both sizes by the same charges: the evaluation loop (two line evaluations at `218`, the loop work, the bit-reversed index of `a` bits at `7a`, the store and the loop control) is `604` operations per point at `3 * 2^19` and `611` at `2^20`, plus `2` on loop exit at either size, so `1,572,864 * 604 + 2 = 950,009,858` and `1,048,576 * 611 + 2 = 640,679,938`, a change of `640,679,938 - 950,009,858 = -309,329,920`; the rest of the row (the plan, the roots and constants, the inverse transform, the leading-coefficient test and the normalisation) `77,942,106 - 122,985,059 = -45,042,953` (one power-of-two transform of `2^20` points in place of the size-`3 * 2^19` transform with its radix-3 layer); the twiddle table `4,194,678 - 2,097,527 = 2,097,151` (`2^19` entries in place of `2^18`). Row B `= 1,075,093,735 - 352,275,722 = 722,818,013` (at `3 * 2^19` the three parts `950,009,858 + 122,985,059 + 2,097,527` sum to `1,075,092,444`; the row of `26797647` charges `1,291` more, kept here unchanged). The stage-B live peak is `81,592,512` bytes (`g` of stage A, the array of `2^20` words and the table), below the stage-C peak (7). This entry replaces the evaluation loop: `1,048,576 * 360 + 32,768 * 7 + 1,024 * 7 + 32 * 5 + 2 = 377,724,066` (Appendix L.3) in place of `640,679,938`, and adds the eight 32-entry root tables and the constants of `L`, `10,000` (Appendix L.3); the rest of the row (`77,942,106`), the twiddle table (`4,194,678`) and the `1,291` are kept, so row B `= 377,724,066 + 10,000 + 77,942,106 + 4,194,678 + 1,291 = 459,872,141`. The root tables are a fixed static area (8,192 bytes, counted in 7), not arena blocks, so the allocation walk of Appendix E.3 is unchanged.

### 6.1 Validation

The kernel charges and the allocator rules are those compared with the instrumented totals of our executed runs at `r = 3, 4, 5` (the arena rule within 64 bytes of the measured heap peaks there); the truncated-set stage C (4.3T) and the stage D of 4.4 have no executed counterpart, and their counts are the formulas of Appendix E.

### 6.2 Offline derivation

The literals of the sources are computed once, offline, from `p` and the organizer's 192 round constants and 9 MDS entries, one literal at a time (working set: at most 16 words of 32 bytes and a 64-byte digit buffer, `576` bytes, counted in the memory, 7); each is the value of one closed formula, with no search and no choice. Count in the primitives of 4.2 (orchard-field-ram-v2: every field operation, load, store and control operation is 1): a field operation is charged 4 (the operation, two operand loads, one store), a 64-bit word operation 3 (the operation, one load, one store), a hexadecimal digit 5 (its load, the table load, a shift, an or, the loop control). (a) Input: 202 values of 64 hexadecimal digits (`p`, the 192 round constants, the 9 MDS entries), 324 each with the 4 word stores: `65,448`. (b) Field literals, 504 field operations: `2 = 1 + 1` (1); `R = 2^256 mod p`, `2` squared 8 times (8); `R^2 mod p` (1); the Montgomery forms `x R mod p` of the 201 organizer constants (201); `2^65 R mod p` (`2` squared 6 times, times `2`, times `R`: 8); `5 = 2 + 2 + 1` (2); `5^t R mod p` with `t = (p-1)/2^32`, the odd exponent of the Tonelli-Shanks of stage F (223 bits, 46 of them 1: 222 squarings, 45 multiplications, times `R`: 268); `mu R mod p`, `mu = (5^t)^(2^14)` of order `2^18` (4.1.3; 14 squarings, times `R`: 15); charged `4 * 504 + 3 * 222` (the bit steps of the square-and-multiply) `= 2,682`. (c) Word literals, 90 word operations: `p - 1` (4), `t` (a shift by 32 over 4 words, 12), `(t+1)/2` (16), `(p-1)/2` (12), `p - 2` (4), `e = (4(p-1)+1)/5` (a shift by 2 into 5 words 15, plus 1, a division by 5 word by word 10: 26), `-p^-1 mod 2^64` (5 Newton steps `x <- x (2 - p_0 x)` from `x = p_0`, 3 each, and a negation: 16); charged `3 * 90 = 270`. (d) Output: 212 literals of 64 hexadecimal digits (the 201 Montgomery forms, `R`, `R^2`, `2^65 R`, `5^t R`, `mu R`, `t`, `(t+1)/2`, `(p-1)/2`, `p - 2`, `e`, `p`), 324 each, and `-p^-1 mod 2^64` (16 digits, 81): `68,769`. `T_off = 65,448 + 2,682 + 270 + 68,769 = 137,169` operations. The ledger charges the declared cap `1,000,000 >= T_off` (`preprocessing_log2 = 20`, `2^20 = 1,048,576`), inside `N_max`: a counted bound, not a premise. This entry adds the 64 constants of the line program and `E0_0`, `OUTSCALE` (Appendix L.1): at most `200,584` more, `T_off <= 337,753 <= 1,000,000`, so the charged cap is unchanged.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g, R - 1)`, `g = g_c^(17)` (4.3G): every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the pseudo-division of a node, each step of the base case and of the classical tail) tests, before it does any work beyond reading the two leading coefficients, that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` ends the trial because it cannot complete the required budget. In the classical tail a zero remainder from a permitted degree-one quotient terminates the gcd computation normally: keep the preceding nonzero divisor as `G`, perform the existing leading-coefficient inversion and normalisation, and proceed to E. The degree-zero or degree-above-16 cases are rejected by the existing stage-E guard. This resolves an ambiguity in the inherited prose; the tail and normalisation are already included in the 349,351-operation tail row of Appendix E.2, and the stage-E guard is already in its 1,000-operation bookkeeping allowance. No new algorithmic branch, allocation, inversion or repeated scan is introduced. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state at the start of the trial (`1,000` operations, charged in every trial). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each node calls its children with budget `2^(j-1) - 1` and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the budgets of the outer loop (`k` the largest `2^j - 1 <= 2^16 - 1` with `2k + 1 <= n`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls produce has degree above the classical tail, so every gcd of degree at most `DMAX = 16` first appears in the classical tail (from degree 206); a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The charging follows `e6dcb600` and the half-gcd follows `4bcabff8`, both read as text only (no entry script was run, compiled or imported). Appendix E.2 expands, for `r = 3`, the charge of stage D for the normal sequence with the tests, `10,416,313,186`, part by part.

The `r = 3` trial (`~126 MB`, `~5.6e10` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the register file of 391 words (256 field, 135 integer address registers) is the machine restriction of claim.json.

## 7. Memory: the arena of one trial

The arena is the capacity of the allocator of 4.2 on the allocation/free sequence of the trial. Appendix E.3 runs the allocator on every allocation and free of the trial in the order of the program and reports the two-ended-pool high-water mark (the largest sum of the extents of the two ends over the trial), the slab area and the peaks of the live set per stage. The two-ended pool takes the blocks of more than `2^10` bytes. The Graeffe prefix (4.3G) holds `E` and `O` on `O1` in the arrays of `A` on `O2` and on `O1` before stage C fills them, with a scratch of `6,144` words that it frees: it adds no array and leaves the high-water mark unchanged. Its high-water mark is reached in stage C: `125,369,472` bytes (the four arrays of `n'` words of 4.3T, the scratch of `6,144` words, which also holds the prefix products of one batch-inversion chunk, and the table block of `984 + 3,072` words: the 30 constants, the 477 `delta_j`, the 477 `delta_j^-1` and the two-level root table), plus 128 bytes so the unused middle is always at least 128 bytes. Stage D holds `g`, `R`, the table block of stage C (`984 + 3,072` words, freed by stage D) and the bump arena of the half-gcd (`1,441,792` words, 4.4: the matrix and the six spectra of an apply plan at its largest); under the H-NORMAL ABORT these are the normal-case arrays, and a trial with any other sequence ends after a prefix of these allocations (6.3), so the normal-case walk bounds every trial. The stage-D live peak is `108,788,736` bytes, below the stage-C peak. No block of `2^10` bytes or less is live in stages A to D (slab area 0). Stages E and later hold at most 16 small arrays and the free-list heads: `16,896` bytes. The arena is `125,386,496` bytes (two-ended pool `125,369,472 + 128`, stages E and later `16,896`). Peaks of the live set per stage (bytes): A `31,260,736`; B `81,592,512`; C `125,369,472`; D `108,788,736`. With `719,068` bytes of code and static data (`399,216` of code, `86,340` for the block loops unrolled by four, `24,560` for the first copies of the new stage-C bodies, `166,592` for the block-form bodies of 5 to 7 layers and the position-0 variants, 4.2; `1,368` for the two row bodies of the node of 4.4; `32,768` for the apply plans of 4.4, at most 8,192 instructions; `32` of initialised data; the `8,192`-byte output buffer; every table of the algorithm is a block of the arena, built at run time and charged in its stage, so no table is static), the register file of the machine (391 words of 256 bits: 256 field and 135 integer address registers, 4.2; `12,512` bytes), the working set of the offline derivation (6.2: 16 words of 32 bytes and the 64-byte digit buffer, `576` bytes) and a `65,536`-byte stack, the footprint of `c6e5d126` is `125,386,496 + 719,068 + 12,512 + 576 + 65,536 = 126,184,188` bytes. This entry adds `16,384` bytes of code and static data (Appendix L.4: the program `L` inlined once as a subroutine shared by stages B and F, 171 instructions; its 64 constants, 2,048 bytes; the eight 32-entry root tables of stage B, 8,192 bytes; the stage-B and stage-F loop bodies; the register-resident stage E of Appendix S, at most 1,100 instructions; at most 15,564 bytes in all (684 + 2,048 + 8,192 + 160 + 80 + 4,400), rounded up to `16,384`), so the footprint is `125,386,496 + 735,452 + 12,512 + 576 + 65,536 = 126,200,572` bytes `= 2^26.9111432`, claimed as `memory_log2_bytes = 26.91115` (rounded up at five decimals). The arena and the allocation walk are unchanged. No stored advice; the twiddle table of stage B and the root table of stage C are built at run time and charged in their rows, and the product passes of stages C and D form their twiddles as running factors (4.2).

## 8. Review points, answered by location

1. Row D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3): by the prefix lemma every trial executes a prefix of the normal-case work, so the time and memory bounds hold for every sequence; `H-NORMAL` (9.5) enters only the success probability.
2. Stage D (4.4) is listed outer step by outer step in Appendix E.3 (budget, half-gcd charge, apply charge and plan); its bump arena (`1,441,792` words) is a block of the allocation walk, and its live peak (`108,788,736` bytes) is below the stage-C peak, the high-water mark of the trial.
3. Row B reproducible from sections 3 and 6 and Appendix L (points * 360 for the loop with its two executions of the 171-operation program, the table levels, the root tables + the kept rest of the row: the twiddle table and the inverse transform + normalisation). The register file of 256 field and 135 integer address registers (the machine restriction of claim.json, 4.2, counted in the memory, 7) is the only register assumption; every value beyond it is charged as a load or store.
4. The offline derivation is counted literal class by literal class in 6.2 (`T_off = 137,169` operations) and charged at the declared cap `1,000,000` (`preprocessing_log2 = 20`); the cap over the count moves `time_log2` by less than `2.3e-5`.
5. The mem penalty uses the rounded-up `mem_log2`, a self-penalizing over-charge.
6. `success = q - delta - eps_coin - eps_iso - eps_g >= 0.39` from the premises `H-ONE` and `H-NORMAL` (9.2, 9.5) with `K = 1`, `q = 0.3931`, `delta = 0.001`; the lower bound is strictly greater than `0.39026894531`. The `H-ONE` allowance below the law value is stated exactly (`0.3934693 - 0.3931 = 0.0003693`; `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound, 9.1), and `delta = 0.001` is the declared premise; the 3,072 organizer-seeded sequences are reproducible observations consistent with it (10.5.1).
7. The organizer-checkable output is the returned witness-pair count. For euclid-gcdpos (10.5.1) a pair is returned only when `deg G >= 1`, so that count is the organizer-counted good-centre fraction at `N = 2, 3`; for euclid-normal a pair is returned only when the sequences are normal. The step from those depths to `N = 9` is the premises H-ONE (9.1) and H-NORMAL (9.5), not an organizer-verified proof.
8. The Graeffe prefix (4.3G) is exact and adds nothing to the premises of the time or the memory; the success bound uses `H-NORMAL` stated for the pair of the transformed polynomial (9.5), whose organizer-run tests compute that pair (10.5.1).

## 9. The premise and the success bound

### 9.1 H-ONE

The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (stage D returns `G` with `1 <= deg G <= k(c)` when `k(c) >= 1`, 4.3G). The premise states `q = 0.3931`, the law value `1 - e^(-1/2) = 0.3934693` (9.3) less the extrapolation allowance stated exactly as `0.0003693`; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292`. The split of the allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`: with `delta = 0.001` (9.5) and `K = 1` the good-and-normal-centre bound before isolation is `0.3921`, leaving `0.0021` for isolation and the other errors; section 9.2 deducts them for the cap-16 algorithm. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1.

### 9.2 The success bound

The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g, R_c - 1)` (`g = g_c^(17)`, 4.3G) is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.001`). The Graeffe prefix and the value-domain stage C reproduce `g^(17)` and `R = S^((p-1)/2^18) mod g^(17)` exactly (4.3G, 4.3T) and add no premise; stage C needs `g^(17)` nonzero on `O1`, which fails with probability at most `eps_g = 2^17 n' (D - 1) / p < 2^-196` over the centre (4.3G). If `E_c` and `N_c` hold and `g^(17)` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g^(17), R_c - 1)` with `1 <= deg G <= DMAX` (4.3G); a successful isolation and the scan of 4.1.3 then end in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g^(17)` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.001`, `eps_iso <= 0.001831054688`, `eps_coin <= 3.671e-77`, `eps_g < 2^-196`: `q - delta = 0.3921`, and after subtracting the stated error bounds success is strictly greater than `0.39026894531 > 0.39`. The bound stays at or above `0.39` for every `delta <= 0.00126894` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)

The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma

With `1 <= deg G <= 16`, the cap is `Z = 16`. This finite argument adapts the pair-separation lemma of mpjunior92's `1ac48175` to the shorter stopping rule. By 4.3G, `G` divides `Y^((p-1)/2^18) - 1`, hence is squarefree, nonzero at zero and split over `F_p`. Fix any pair of its distinct roots `t_i,t_j`. At each step the current factor H is nested inside G. When the pair is still in H and its two shifted quadratic characters are nonzero and different, exactly one lies in `T = gcd(H,(X+a)^((p-1)/2)-1)`. Then T is a nonempty proper factor, the algorithm keeps T and the pair cannot survive. A pair can therefore survive only on shifts with equal nonzero characters or one of the two exceptional zeros. For a fresh uniform shift, `sum_a chi((a+t_i)(a+t_j)) = -1`; there are `(p-3)/2` equal-nonzero shifts and two exceptional shifts, giving a conditional survival probability at most `1/2 + 1/(2p) < 1/2 + 2^-127`. This bound holds after any history in which the pair survives; no independence between different root pairs or between the nested factors is assumed. Fresh independent shifts give a survival bound `(1/2 + 2^-127)^16` for each fixed pair. If the algorithm has not reached degree one after 16 rounds, some pair of the original at most 16 roots survives. Thus `eps_iso <= C(16,2) (1/2 + 2^-127)^16 < 0.001831054688`. The constant term is exactly `120/65536 = 0.0018310546875`, and the correction is less than `4e-40`. This argument is for ideal uniform field draws; section 4.1.1 and the coupling of 9.2 charge the actual sampler's bias once through eps_coin. For degree one the algorithm exits immediately and isolation failure is zero.

For clarity about the budget choice, the same bound with 15 rounds has principal term `120/32768 = 0.003662109375`, exceeding the available `q - delta - 0.39 = 0.0021`. Sixteen is the smallest cap certified by this particular worst-degree pair-union argument and these unchanged premises. This is not a claim that every smaller-cap algorithm must fail.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(h_c, R_c - 1)`, where `h_c = g_c^(17)` is the 17-fold Graeffe transform (4.3G) of the monic odd part `g_c` of section 3 (monic, degree `m = 976,562`) and `R_c = S^((p-1)/2^18) mod h_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.001` (`2^-9.966`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-213`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.001`) to the structured pair `(h_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-g17-a` to `-f` compute the complete Euclidean sequence of `(h_c, R_c - 1)` for this construction (17 Graeffe steps, exponent `(p-1)/2^18`) on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24-g17` and `euclid-normal-n4-t2-g17` do the same at `m = 62, 312`. The prediction is that every computed sequence is normal. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.001` is the declared premise). Not verified at `r = 3`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`. The success bound assumes nothing about the organizer-seeded trials (no independence or identical distribution of the trials is used).

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, euclid-gcdpos) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-g17-a to -f compute the complete Euclidean sequence of `(h_c, R_c - 1)` (the pair of 9.5: 17 Graeffe steps, exponent `(p-1)/2^18`) for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n3-t24-g17 and -n4-t2-g17 compute one sequence per trial at `m = 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the prediction (H-NORMAL, 9.5) is that every trial returns a pair, so the abnormal count is zero, a reproducible observation consistent with the premise. We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.001` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. euclid-gcdpos-n2-t256-a, -b and euclid-gcdpos-n3-t24 (H-ONE, 9.1) take one organizer-seeded centre per trial at `N = 2, 3` (`m = 12, 62`), without the Graeffe prefix (H-ONE is a statement about `g_c`, which the prefix does not change, 4.3G), compute `G = gcd(g_c, R_c - 1)` with `R_c = S^((p-1)/2) mod g_c` (`deg G = k(c)`) and return a witness pair ONLY when `deg G >= 1`, so the organizer's returned-pair count is the good-centre count. Expected: the fraction of good centres is the law of 9.3, a theorem at these depths; the returned counts are reproducible observations consistent with it, and no probability, rate or population bound is drawn from them (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed). Our runs of these three entries on local seeds (one CPU): 106 and 100 of 256 (3.8 s, 3.7 s) and 12 of 24 (5.7 s). line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure (random-function model), not the score-critical basis. Our runs of the six -l2-g17 entries with local seeds (one CPU; 6.7 to 7.4 s each on our workstation): 3,072 sequences, all normal, 256 pairs per entry; the gcd had positive degree for 1,189 of the 3,072 centres. Our runs of -n3-t24-g17 and -n4-t2-g17: 24 and 2 sequences, all normal. The organizer-checkable output is the returned witness-pair count; the step from these depths to `N = 9` is the premises H-ONE and H-NORMAL, not an organizer-verified proof. The success bound assumes nothing about the organizer-seeded trials (no independence or identical distribution of the trials is used).

## Appendix E: rows C and D expanded, and the allocation walk of one trial

Rows C and D and the arena of section 7 are exact counts of the algorithm of sections 4.2-4.4 at `r = 3`. E.1 and E.2 expand each row into its parts, each part a count from the dimensions of 4.3G, 4.3T and the half-gcd levels with the charges of 4.2; each table adds up exactly to its row. E.3 is the output of our counting program for one trial: the outer steps of stage D, the stage totals, the live-set peaks per stage, the two-ended-pool high-water mark and the arena, the allocator of 4.2 run on every allocation and free of the trial in program order.

### E.1 Row C = 39,693,958,128

Row C is the sum of the steps of section 4.3T in the order the stage runs them:

| part of stage C | operations |
| --- | ---: |
| plans of the passes, the exponent, the tables (`30` constants, the `477` `delta_j` and `477` `delta_j^-1`, the `3,072`-word root table, built), the zero-fill of `g` above `m` | 5,287,450 |
| the allocation of `A` on `O1`; the Graeffe prefix (4.3G): `17` steps (below), the allocation, zero-fill and free of its `6,144`-word scratch | 1,972,340,415 |
| the Newton reciprocal of the reversed `g` to `ell` coefficients (doubling steps, block-form products) | 162,214,151 |
| the product `q = floor(X^v P1 / g)` (one product of `2 ell - 1` points) and its copy | 47,946,726 |
| `g` to `O1` and `O2` (two scalings, two truncated forwards; the `6,144`-word scratch allocated and zero-filled once) | 81,708,731 |
| `g~ = delta_j^2 g` on `O2` (per node 3, per point 5) | 5,258,450 |
| the start residue `A0` on `O2` (zero-fill, scaling, truncated forward of `q`, pointwise pass at 8) | 51,036,336 |
| `A0' = delta_j A0` on `O2` (per node 2, per point 5) | 5,257,973 |
| `A0` to `O1` (truncated inverse on `O2` with `e = delta_j^-1`, scaling, truncated forward) | 83,363,960 |
| `k1` on `O1` by chunked batch inversion (159 chunks of `6,144`, zero tests) | 14,834,543 |
| the squaring steps (step 6; below) | 37,074,119,136 |
| the exit step `Mont(A, 1)` (pointwise passes at 7 and 11, one extension), the frees | 101,644,766 |
| two truncated inverses with scaling (`R` with `e = delta_j^-1`, `g` with `e = delta_j^-2`), the free of the scratch, the closing control | 88,944,491 |
| stage bookkeeping (entry, exit) | 1,000 |
| **row C** | **39,693,958,128** |

The squaring steps: `174` steps with exponent bit 0 and `45` with bit 1, `174 * 168,893,024 + 45 * 170,816,288 = 37,074,119,136`. One step (4.3T) is:

| part of one step (bit 0) | operations |
| --- | ---: |
| bottom pass on `O1` (`U = A^2 k1`, 4 per point) | 22,661,336 |
| two inverse middle-pass sets, 20,260,760 each | 40,521,520 |
| two forward middle-pass sets, 20,260,232 each | 40,520,464 |
| two fused top passes (inverse top with row 15 formed in registers, coset twiddle, forward top), 18,153,616 each | 36,307,232 |
| bottom pass on `O2` (`B2' = A2'^2 + U g~`, 9 per point; `delta_j^-1` in the block scaling) | 27,582,068 |
| address updates of the `O2` bottom blocks (one per block beyond the block control, 4.2) | 30,528 |
| two tail solves of row 14 (`6,144` offsets), 368,688 each | 737,376 |
| two recoveries of the subtrees `{477}`, `{478..479}` inside row 14, 266,240 each | 532,480 |
| step control | 20 |
| **one step, bit 0** | **168,893,024** |

A step with bit 1 adds 2 per point of `O2` in its bottom pass (`x = y zeta^e`, `x B2'`), less the `30,528` blocks whose point `zeta^0 y` is `y`: `170,816,288 - 168,893,024 = 1,923,264 = 2 * 976,896 - 30,528`.

The Graeffe prefix (4.3G): `17` steps of `116,019,127` each, `1,972,325,159`; with the allocation of `A` on `O1` and the allocation, zero-fill and free of the scratch of the prefix, `1,972,340,415`. One Graeffe step (`gt2_step`) is:

| part of one Graeffe step | operations |
| --- | ---: |
| two pruned forward top passes (the 15 present rows), `E` and `O` read from `g` at stride 2 (`tr_top_half`) | 12,472,335 |
| three middle-pass sets (forward `E`, forward `O`, inverse), 20,260,232, 20,260,232, 20,260,760 | 60,781,224 |
| fused bottom pass (forward bottom layers of `E` and `O`, `G = (E^2 - y O^2)/N` at 5 per point, inverse bottom layers with the block scaling; per block one address update beyond the block control) | 31,972,376 |
| inverse top pass with row 15 formed in registers (stores into `g`) | 10,158,224 |
| tail solve of row 14 and recovery of the subtrees `{477}`, `{478..479}` | 634,928 |
| step control | 40 |
| **one Graeffe step** | **116,019,127** |

### E.2 Row D = 10,416,313,186

The Euclid driver of 4.4 makes 28 outer steps, each one `hgcd` call of budget `k` on the top window and the apply of its matrix to the whole pair; E.3 lists each step; the `hgcd` charge of a call includes the fold and the two-output passes of its nodes (4.4). Row D is:

| part of row D | operations |
| --- | ---: |
| the half-gcd calls of the 28 outer steps (E.3, `hgcd` column, each with its call) | 8,028,359,706 |
| the applies of their matrices to the whole pair (E.3, `apply` column) | 2,387,602,483 |
| the classical tail from degree 206 with the quotient tests, the inversion of the leading coefficient and the normalisation of `G` | 349,351 |
| stage frame: entry, the bump arena of `1,441,792` words, the frees of the arena, the tables and the arrays of stage C | 1,646 |
| **row D** | **10,416,313,186** |

### E.3 Totals and the allocation walk of one trial

```text
m = 976,562 | truncated point sets: n1 = 976,896 of N = 1,048,576 (TRC = 477 of 512 nodes) | squaring steps 219 of which with S: 45
stage C: one squaring step 168,893,024 operations (with S: 170,816,288), pass split {'a': 4, 'b': 5, 'mid': [5, 6]}
S_C = 39,693,958,128
stage D outer steps (degree n, budget k, hgcd ops, apply ops, apply plan):
  n = 976562 k = 65535 hgcd 549,784,753 apply 284,166,769 ('fix3', 16, 196608)
  n = 911027 k = 65535 hgcd 549,784,753 apply 281,502,661 ('fix3', 16, 196608)
  n = 845492 k = 65535 hgcd 549,784,753 apply 247,394,213 ('fix3', 16, 196608)
  n = 779957 k = 65535 hgcd 549,784,753 apply 244,730,165 ('fix3', 16, 196608)
  n = 714422 k = 65535 hgcd 549,784,753 apply 210,621,609 ('fix3', 16, 196608)
  n = 648887 k = 65535 hgcd 549,784,753 apply 207,957,649 ('fix3', 16, 196608)
  n = 583352 k = 65535 hgcd 549,784,753 apply 173,849,029 ('fix3', 16, 196608)
  n = 517817 k = 65535 hgcd 549,784,753 apply 171,185,133 ('fix3', 16, 196608)
  n = 452282 k = 65535 hgcd 549,784,753 apply 137,076,393 ('fix3', 16, 196608)
  n = 386747 k = 65535 hgcd 549,784,753 apply 131,931,562 ('fix1', 17, 131072)
  n = 321212 k = 65535 hgcd 549,784,753 apply 87,211,774 ('p1', 18, 262144)
  n = 255677 k = 65535 hgcd 549,784,753 apply 69,284,138 ('dir3', 16, 196608)
  n = 190142 k = 65535 hgcd 549,784,753 apply 43,427,930 ('p1', 17, 131072)
  n = 124607 k = 32767 hgcd 251,236,129 apply 33,438,838 ('dir3', 15, 98304)
  n = 91840 k = 32767 hgcd 251,236,129 apply 20,487,142 ('p1', 16, 65536)
  n = 59073 k = 16383 hgcd 114,116,169 apply 16,104,140 ('dir3', 14, 49152)
  n = 42690 k = 16383 hgcd 114,116,169 apply 9,819,926 ('p1', 15, 32768)
  n = 26307 k = 8191 hgcd 51,438,029 apply 7,729,584 ('dir3', 13, 24576)
  n = 18116 k = 8191 hgcd 51,438,029 apply 4,294,300 ('p3', 12, 12288)
  n = 9925 k = 4095 hgcd 22,942,847 apply 1,942,586 ('p3', 11, 6144)
  n = 5830 k = 2047 hgcd 10,234,751 apply 1,147,006 ('p1', 12, 4096)
  n = 3783 k = 1023 hgcd 4,510,639 apply 847,487 ('dir3', 10, 3072)
  n = 2760 k = 1023 hgcd 4,510,639 apply 494,740 ('p1', 11, 2048)
  n = 1737 k = 511 hgcd 1,952,535 apply 419,435 ('dir3', 9, 1536)
  n = 1226 k = 511 hgcd 1,952,535 apply 238,532 ('p1', 10, 1024)
  n = 715 k = 255 hgcd 820,587 apply 121,056 ('p1', 9, 512)
  n = 460 k = 127 hgcd 326,365 apply 116,462 ('p1', 9, 512)
  n = 333 k = 127 hgcd 326,365 apply 62,224 ('p1', 8, 256)
stage D: classical tail from degree 206; half-gcd operations 10,416,311,540; bump arena 1,441,792 words
S_D = 10,416,313,186
peak of the live set, stage A = 31,260,736 bytes
peak of the live set, stage B = 81,592,512 bytes
peak of the live set, stage C = 125,369,472 bytes
peak of the live set, stage D = 108,788,736 bytes
two-ended pool: blocks of more than 2^10 bytes; largest sum of the two ends after each stage (bytes): init 0, A 31,260,736, B 81,592,512, C 125,369,472, D 125,369,472; at most 9 blocks; 39 blocks examined in all
slab classes (class: peak number of live blocks): ; slab area = 0 bytes
KBF 7 TW1 1 REGF 12512 regs 256 135 wide code bytes 166592
arena = 125,386,496 bytes (two-ended pool 125,369,472 + 128, slab classes 0, stages E and later 16,896), memory = 126,184,188 bytes, log2 = 26.91096
```

The output above is the inherited participant report from `c6e5d126`, not an execution of this derivative. This entry leaves the arena and the walk unchanged and adds `16,384` bytes of code and static data (section 7): memory `126,200,572` bytes, `log2 = 26.9111432`, claimed `26.91115`. Rows B, E and F and `N_max` are those of section 6 (`N_max = 50,625,218,139`).

## Appendix L: the inherited line program `L` (mpjunior92)

### L.1 Construction

`L(x) = F(x - E0_0) / OUTSCALE`, `F` the digest on the line of 2.2 (`W = tau^5`). The state after round 1 is `A + W B` (2.2: `alpha = A + c_2`, `beta = B`); the round-2 S-box input of lane `i` is `A_i + c_{2,i} + W B_i = B_i (W + E0_i)`, `E0_i = (A_i + c_{2,i}) / B_i` (every `B_i != 0` on the deployed constants). With `x = W + E0_0` lane 0 is `B_0 x` and lane `i` is `B_i (x + e_i)`, `e_i = E0_i - E0_0`: the program starts with `y1 = x + e1`, `y2 = x + e2` (2 additions) and holds lane `i` as `y_i` with the scale `B_i`. Every lane is held as its true value divided by a known nonzero scale: an S-box of a held lane is the true S-box output divided by the fifth power of the scale (3 multiplications), and the fifth powers are folded into the next linear layer, each output lane being held divided by its coefficient on `z0`: a dense layer with the next round's constants is `y_i = z0 + a_i z1 + b_i z2 + k_i` (2 multiplications, 3 additions per lane). Partial rounds use the sparse form of Grassi, Khovratovich, Rechberger, Roy and Schofnegger (USENIX Security 2021) with the same scaling, as in the r = 56 entries `3a1b25b6`, `9fb982e8` and `69e14209`: lane 0 is held as `lambda h0 + gamma`, lanes 1, 2 as `P (h1, h2) + q` with `P = Mww^j P0` after `j` partial rounds (`Mww` the lower-right 2x2 block of `M`) and `P0 = Mww^-r D`, `D` diagonal, so `P` is diagonal at the exit; one partial round is `u = h0 + k`, `x5 = u^5` (3 multiplications), `h0 = x5 + n1 h1 + n2 h2`, `h1 = h1 + v1 x5`, `h2 = h2 + v2 x5` (`h0` from the old `h1`, `h2`): 12 operations. Counts: entry 2; round 2 (S-boxes 9, dense layer with the round-3 constants 15); round 3 (S-boxes 9, into the partial form 6 multiplications and 6 additions, `D` normalising the `z0` coefficients); `r` partial rounds, 12 each; exit 3 (the round-60 constants); rounds 60-62 (24 each); round 63 (S-boxes 9, row 0 held divided by its `z0` coefficient `OUTSCALE`, 2 multiplications and 2 additions): `2 + 24 + 21 + 12 r + 3 + 72 + 13 = 135 + 12 r = 171`. Every constant is a closed formula of the deployed constants, derived once, offline, by the rules of 6.2: at most `64 * (2 * 330 + 40) = 44,800` field operations (at most two inversions and 40 products per literal), charged 4 each (`179,200`), and the output of 66 literals (with `E0_0`, `OUTSCALE`) at 324 each (`21,384`): `200,584`, so the offline total is at most `137,169 + 200,584 = 337,753`, inside the declared cap `1,000,000` of 6.2.

### L.2 Check

`E0_0 = 0x3a4bd2e80f62c6cde67f816c4a67f17bbd43a70c4d2fca9784cc22ba736569ff`, `OUTSCALE = 0x008849bc678a8b58033adbecedb2aaa16af6496d6d8b66315471382503443b8a`. Our program (standard library only) builds `L` from the organizer constants file, executes it, and asserts `OUTSCALE * L(W + E0_0) = digest(message(W))` with the reference rounds of `verifier/poseidon.py` at 200 random `W` (r = 3; also r = 0, 1, 9 with `135 + 12 r` operations); `message(W)` is the canonical pair of 2.2 (`tau = W^e`, `(U, V) = Q + tau (a, b)`, `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`). An independent construction of the same form for r = 56 (the 807-operation step of `69e14209`) gives the same `OUTSCALE` at r = 3 when its round count is set to 3.

### L.3 Stage B loop and its tables

Position `k = k4 2^15 + k3 2^10 + k2 2^5 + k1` (four 5-bit digits) holds the value at `y = omega^(rev20(k))`, `s = zeta^(rev20(k))` (`zeta` of order `2^21`, `zeta^2 = omega`), `rev20(k) = rev5(k1) 2^15 + rev5(k2) 2^10 + rev5(k3) 2^5 + rev5(k4)`, so `s = A1[k1] A2[k2] A3[k3] A4[k4]` with `A1[t] = zeta^(2^15 rev5(t))`, `A2[t] = zeta^(2^10 rev5(t))`, `A3[t] = zeta^(2^5 rev5(t))`, `A4[t] = zeta^(rev5(t))`, and `1/(2s) = A1'[k1] A2'[k2] A3'[k3] A4'[k4]` with `Aj'[t] = 1/Aj[t]` and the factor `1/2` folded into `A4'`. The eight tables (256 words) are built once per run in a fixed static area: `zeta = 5^((p-1)/2^21)` (5 is a non-square; at most 1,346 operations), `zeta^-1` (1,346), the powers `zeta^(2^j)` and their inverses (42), each table by doubling over the five bits (one multiplication, one store and 3 of control per entry, 5 per entry, 1,280 in all), and the program constants into their immediates: charged `10,000` with the load of `c' = c + E0_0`. Loops (k4 outermost, k1 innermost, so the stored positions are consecutive):

```text
for k4:  m4 = A4[k4]; m4' = A4'[k4]                       (2 loads, 3 control)                     32 times:          5
 for k3: m3 = m4 A3[k3]; m3' = m4' A3'[k3]                 (2 loads, 2 multiplications, 3 control)  1,024 times:       7
  for k2: m2 = m3 A2[k2]; m2' = m3' A2'[k2]                (2 loads, 2 multiplications, 3 control)  32,768 times:      7
   for k1: s = m2 A1[k1]; t = m2' A1'[k1]                  (2 loads, 2 multiplications)             1,048,576 times:   360
           x = c' + s; call L; r1 = x                      (1 addition, call 2, L 171, 1 move)
           x = c' - s; call L                              (1 subtraction, call 2, L 171)
           v = (r1 - x) t; store v at position k; k += 1   (1 subtraction, 1 multiplication, 1 store, 1 index update)
           loop control                                    (3)
exit                                                                                                 2
```

Per innermost point `4 + 1 + 2 + 171 + 1 + 1 + 2 + 171 + 1 + 1 + 1 + 1 + 3 = 360`; the loop is `1,048,576 * 360 + 32,768 * 7 + 1,024 * 7 + 32 * 5 + 2 = 377,724,066` operations. The values `v = (L(c' + s) - L(c' - s)) / (2s) = g_c(y) / OUTSCALE` are those of section 3 up to the constant `1/OUTSCALE`; the inverse transform, the leading-coefficient test and the normalisation of row B follow unchanged. Registers: the 18 working registers of `L`, `c'`, `s`, `t`, `r1`, `m2`, `m2'`, `m3`, `m3'`, `m4`, `m4'` (28 field registers) and 6 integer registers.

### L.4 Code and static data added to the footprint

`L` once, as a subroutine shared by stages B and F: 171 instructions, 684 bytes, and its 64 constants, 2,048 bytes; the eight root tables, 8,192 bytes; the stage-B loop bodies (at most 40 instructions, 160 bytes) and the stage-F scan body (at most 20, 80 bytes); stage E of Appendix S (at most 1,100 instructions, 4,400 bytes). At most 15,564 bytes; `16,384` are added to the footprint (section 7).

### L.5 Constants of `L` at r = 3

```text
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
k13 = 0x0d3b8a827917fcedebf0d034bf1557dfefb690b5523cb6ab02ec48b528557c01
k14 = 0x3c51ef0bf66e23d3d883a88c0e0f4eb1d89b78ef0fc4a05ade70ea7ec97bcc63
k15 = 0x2a409ab0300c6ee67b12fc9104ccf1c566b75f5f0f860d249de65a3b9db2a87b
k16 = 0x3d4970a7e2c26786353bda89becc598b7042beef6bdcf07d7273bc06ac2762b1
k17 = 0x34058bb8920441623716adeb0155288a2cca42fa34af13309820b9953e4336cf
k18 = 0x3cd8dc7d461075170dcead8e173c5c9d577c29e728791efca0567a1592066dcf
k19 = 0x0e334770d9a1cba5f4e9c4fcd0d147159e79d7bd6eadbcb552a81de3fae0ed39
k20 = 0x049c270cbedc284494fc4e969377218f4f2e2ed7d3c406b44cea0e0c15843b68
k21 = 0x2d1dab66e79d7bead58d8c4d2f109c05a9fb3064ed4b61e0e4e76b807cf9005c
k22 = 0x266144e217c50738f29b2b098b54686e360c94c1f64cc0b43c6b0a0cc37fc9eb
k23 = 0x0657ab4543abcbf1d5f5aab1029046cc72ad6a27b791384b6a6fe27358419854
k24 = 0x3ef5006b32ec0bffe5f3f7bf0c7bd49502a051b709841e76d74ff8e123427e24
k25 = 0x3ed26539265c0e605e2d0650be5306224e46ba83d7b1016e0076dcadaf6f4c19
k26 = 0x022719e05d1494103cfd7422aba69a4dbe6165523a20092f3dd21b28c10cb519
k27 = 0x1565f5ef914944ad12c16e36ec616abd4dd0f8c94d990dc4ff415ad5a506d732
k28 = 0x156214d27401407378d606df25b968bd41d967d52df3a6a903bf380400ad1d6c
k29 = 0x3714076e62afdb8214304dfba9a42918220381139891c43452af4f7bfdfee38e
k30 = 0x02b4b159801d76a2a36953aabd921ca80f48bd6af49dadee9e304a1b572dab81
k31 = 0x28574841141cbf4c4758fd5bba57d7295c67e10b0c063cf9e3c4841d9fce3809
k32 = 0x1ed57725ab23590895239b675115bb0d9271807fce557c21c1ce117c9e96ffc3
k33 = 0x20e7e686d1e4b9dfe8a38386e50a5f06737d0401a9e495e7b1be271f3c0343a5
k34 = 0x31cfeee55be79bbd06549097bdcea9c952e9016c446c9ae188f490fc9b9d7900
k35 = 0x06592ea4bd4f4210765882c48eb7f4c39354f02ffd346b6acdd09c3703727dcc
k36 = 0x2752b5397b4004eaf6c506dc7628d6c575dcb4891f711bcf7ce8f4d5f3cbaab8
k37 = 0x3387f84097496c3f8a22283650e7d70bbe879cd005c9525ef68d3688145018fc
k38 = 0x137b6ec98d09c5869a31ba5e4fd3874de96ba02db5f640e09f11e1cdaadcac09
k39 = 0x3abe7b019b99d2fb4ffe5bf2905ca150a803618c13a1a36447466d86fad47023
k40 = 0x08bdffe323e2e32f56a5e34e22c6eb00a95383a03a20a5d7baef58d4162bb3f6
k41 = 0x3e4ad51517f33d367e9aa928ec409936cfa140ece605c57f0c6f0a63067089c8
k42 = 0x0fef0d4a472316cd2f6db1afc16c31b994c52389f8ba23dc0d2587587bc6640b
k43 = 0x047ee1de5c33ae8bce3850bacf15e98e1f108449542e8069d9c100659d9a4224
k44 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k45 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
k46 = 0x3421c5de1563c975760bad6279fb8f1169db5b47b9082fbb9a2c04f3aaa35aac
k47 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
k48 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
k49 = 0x1a4e835896b907401ad4a6b47a50b33e28de519afea4efba78a09268a17e4731
k50 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
k51 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
k52 = 0x27d60ff68478312cf044bc46e72157d484b4a321d26aa4fa40142958f1312b7c
k53 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k54 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
k55 = 0x002ba68ad57360a5970c1d3dc72e9feb020d6b2489a822ee741e7f619332efe8
k56 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
k57 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
k58 = 0x1fb8b3ab07c64b98794431c62ac87406f18174e1bf69a767e2df4342236a4a77
k59 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
k60 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
k61 = 0x3dec0c88875b02c1cde5628d31d20897abb117626314a0a8a6cb386c4aec49b2
k62 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
k63 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
```

### L.6 Listing of `L` at r = 3 (171 operations; `x` is input and output; `e1 = k0`, `e2 = k1`)

```text
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
ADD y0, h0, k32
ADD y1, h1, k33
ADD y2, h2, k34
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k35
MUL t2, z2, k36
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k37
MUL t1, z1, k38
MUL t2, z2, k39
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k40
MUL t1, z1, k41
MUL t2, z2, k42
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k43
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k44
MUL t2, z2, k45
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k46
MUL t1, z1, k47
MUL t2, z2, k48
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k49
MUL t1, z1, k50
MUL t2, z2, k51
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k52
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k53
MUL t2, z2, k54
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k55
MUL t1, z1, k56
MUL t2, z2, k57
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k58
MUL t1, z1, k59
MUL t2, z2, k60
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k61
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k62
MUL t2, z2, k63
ADD x, z0, t1
ADD x, x, t2
```

## Appendix S: inherited register-resident stage E, changed cap

Input `G` monic, `1 <= d = deg G <= 16`, a product of distinct linear factors over `F_p` (4.3G). If `d = 1` the root is `-G_0`. Otherwise `H := G` (loaded into field registers) and at most `Z = 16` rounds:

1. draw `a` (63, two words, 4.1.1) and test it (5);
2. `B := (X + a)^((p-1)/2) mod H`: start `B = X + a` (3), then for each of the 253 bits below the top bit of `(p-1)/2` one squaring modulo `H` and, on the 45 one-bits, one multiplication by `X + a` modulo `H`;
3. `B := B - 1` (1);
4. `T := gcd(H, B)` monic, by inversion-free elimination: while the second row is nonzero, order the rows by degree and replace the higher row `A` by `lc(B) A - lc(A) X^(deg A - deg B) B` (its top coefficient cancels; at most `3 d` field operations, 6 control, 3 for the ordering), strip zero top coefficients (2 each); then one inversion of the leading coefficient by square-and-multiply on the 254 bits below the top bit of `p - 2` (76 one-bits: 254 squarings and 76 multiplications, 4 control per bit) and `d` multiplications;
5. keep `T` if `1 <= deg T < deg H`, else keep `H` (6); stop with the root `-H_0` when `deg H = 1`.

Charges at degree `d` (field operations 1 each; every operand is a register: `H` (`d` words), `B` (`d`), the square (`2d - 1`) and the two gcd rows (`2d + 1`), at most 100 field registers with the shift and the loop registers; no load or store inside a round):

* squaring modulo `H`: the `d (d - 1)/2` cross products, accumulated per slot (`d (d - 1)/2 - (2 d - 3)` additions), doubled (`2 d - 3`), the `d` squares and their `d - 2` additions to the cross sums of even slots, and the reduction of the `d - 1` top coefficients (`2 d` each): `S(d) = d (d+1)/2 + d (d-1)/2 - (2d - 3) + (2d - 3) + (d - 2) + 2 d (d - 1)`, `S(16) = 750`, plus 4 of bit control;
* multiplication by `X + a` modulo `H`: `4 d` (per coefficient one product with the top coefficient, one subtraction, one product by `a`, one addition);
* gcd: at most `2 d - 1` eliminations (each lowers the sum of the two degrees), `(2 d - 1)(3 d + 9) + 2 (2 d + 1)` with the strips, the inversion `254 * 5 + 76 = 1,346` and `d`: `3,195` at `d = 16`.

`R(d) = 68 + 3 + 253 (S(d) + 4) + 45 * 4 d + 1 + gcd(d) + 6`, non-decreasing in `d`; `R(16) = 68 + 3 + 190,762 + 2,880 + 1 + 3,195 + 6 = 196,915`. Row E charges every one of the 16 rounds at `d = 16`: `16 * 196,915 + 1,000 + 200 = 3,151,840`. The loop bound is an immediate of the same instruction width; no code, register or arena growth is required. The source author reports that the predecessor procedure was executed with this counter on random products of distinct linear factors of degree 2 to 16 over `F_p` (175 rounds): every run isolated a true root, and the largest charge of a round at degree 16 was `195,817 <= R(16)`. The isolation bound of 9.4 applies to this procedure (the rule of step 5 separates a pair whenever its two characters are nonzero and different).
