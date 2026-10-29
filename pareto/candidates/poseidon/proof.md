# Orchard Poseidon, r = 5: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, a Graeffe prefix, value-domain powering on truncated point sets, inversion-free half-gcd, running twiddle factors, one centre

## 1. Claim

Target: `poseidon-orchard-r5-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, five partial rounds 4, 5, 6, 7 and 8, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises: `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots, and `H-NORMAL` (section 9.5), a statement about the normality of the remainder sequence that enters only the success probability. Section 9.2 derives the success probability from them.

* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, replace `g_c` by its 22-fold Graeffe transform `g = g_c^(22)` (monic, degree `m`, its roots the `2^22`-th powers of those of `g_c`; section 4.3G), compute `R = S^((p-1)/2^23) mod g` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 1491 * 2^14 = 24,428,544` points (1491 of the 2048 depth-11 nodes of the subgroup of order `2^25` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T), every product transform of stages C and D with running twiddle factors in the block form of 4.2 (no product-pass twiddle table in either stage), take `G = gcd(g, R - 1)` by the inversion-free half-gcd of bradcush `b30de9bf`/`4bcabff8` (matrices in coefficient form, node products on two rows (applies on three), outer step `k <= 2^21 - 1` as in weijiekoh `a78f526e`, the matrix of each outer step applied to `(g, R)` by the cheapest of the plans of section 4.4, among them the direct whole-pair and fixed-slot plans of 0xplemonade's `ff21bd28` and the in-place whole-pair plan of 0xplemonade's `390451a3` and `dc8bb986`, the transforms of the nodes and applies in passes of up to seven layers, section 4.4), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root `y` of `G` in at most `Z = 64` rounds, find `s` with `s^(2^23) = y` and `F(c + s) = F(c - s)` among at most `2^22` candidates (4.1.3), map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39209`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.001` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 2.371e-15`, `eps_coin <= 65 p / 2^512 <= 1.404e-76`, `eps_g <= 2^22 n' (D - 1) / p < 2^-181` (the centre makes `g` vanish at a point of `O1`, 4.3G) (sections 4.1.1, 4.3T, 9.2). The value the formula gives is `0.392099999999997628` (at or above the organizer floor 0.39); the claim is that value floored at five decimals.
* `time_log2 = 32.24641` in target-compression units (`C(5) = 321` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C a Graeffe prefix of 22 steps (4.3G) and value-domain powering on truncated point sets (4.3T), stage D the inversion-free half-gcd charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), stage E at its cap of `Z` rounds at degree `DMAX`, and the scan of stage F at its cap of `2^22` candidates (4.1.3). `N_max = 1,635,457,448,090` operations, `log2(N_max / 321) = 32.24640...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is counted, at most `367,149` operations, and charged at its declared cap of 1,000,000 operations; that cap is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 31.54602` (`3,135,437,004` bytes, section 7). Under the pareto convention `time_log2 + max(0, memory_log2_bytes - 20)` this gives `32.24641 + 11.54602 = 43.79243`; the time-only scalar is `32.24641`, and the memory is reviewed separately.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `65` field elements (`130` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^11`, then the roots of its odd part about a centre, found, after a Graeffe prefix (Dandelin-Graeffe root squaring), with a gcd against `S^((p-1)/2^23) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against our r = 5 entry `b885e0eb` (time + memory penalty 43.79985, the same algorithm and package), three changes, all in rows B, E and F (credits in dependencies.json). (i) Line program (rows B, F): each line evaluation is one execution of the straight-line program `L` of Appendix L, `L(x) = F(x - E0_0) / OUTSCALE`, scaled lanes and sparse partial rounds, `135 + 12 r = 195` operations in place of `155 + 21 r = 260`: the form of mpjunior92's r = 5 entry `5ae6d1c7` (its listing form read as text in its r = 10 entry `4c6dc4cf`, Appendix L), built by our own program from the organizer constants and checked against the reference rounds (L.2). (ii) Stage-B point loop (row B): the positions of the transform input are visited in storage order and `s`, `1/(2s)` come from digit-factored root tables, the method of mpjunior92's r = 3 entry `1ac48175` (read as text), here on the mixed-radix layout of our plan (Appendix B): 18 operations per point beside the two evaluations in place of 196 (the 23-bit bit-reversed index and its call, 175, the row counter and the two recurrences). (iii) Stage E register-resident (row E): the procedure and closed-form charge of `4c6dc4cf` Appendix S, as in `5ae6d1c7`, `R(16) = 196,915` per round (Appendix S). Row B `12,715,462,159` (was `20,462,141,906`), row E `12,603,760` (was `166,081,821`), row F `1,687,238,500` (was `2,232,498,018`); rows A, C, D, G, the arena and the allocation walk are unchanged; `28,672` bytes of code and static data are added (section 7): footprint `3,135,437,004` bytes (was `3,135,408,332`); time_log2 `32.24641` (was `32.25384`), time + memory penalty `43.79243` (was `43.79985`; `5ae6d1c7`: 43.79637); H-ONE, H-NORMAL, the success bound and the experiments are unchanged.
* Against our r = 5 entry `107ea107` (time + memory penalty 43.84483, the same algorithm and package), one change in the node of the stage-D half-gcd (4.4). In each node the four chunks of each of `a`, `b` are folded onto the three rows `Y - 1`, `Y + 1`, `Y - i` in one loop (22 operations per position: four loads and three stores at 2 each, eight field operations) in place of a copy and three accumulating passes per row, and each matrix-vector map of the node is one two-output pass of 20 operations per point in place of two passes per output; the two loop bodies are `342` instructions, `1,368` bytes, added to the footprint (4.2, 7). Row D `354,378,608,236` (was `406,442,442,666`); row C, the allocation sequence and every other charge are unchanged; footprint `3,135,408,332` bytes (was `3,135,406,964`); time_log2 `32.25384` (was `32.29882`), time + memory penalty `43.79985` (was `43.84483`); H-ONE, H-NORMAL, the success bound and the experiments are unchanged. 
* Against our r = 5 entry `f673b472` (time + memory penalty 43.86261, the same algorithm and package), three changes. (i) Stage C on the 256 field registers of the declared file, re-split (4.3T, 4.3G): the 25 layers split 3 | 5, 5, 6 | 6 in place of 3 | 6, 6, 6 | 4 (the cheapest of the splits we counted); two middle passes of radix 32 and one of radix 64, every group twiddle in registers, nothing spilled; the bottom pass runs 64-point blocks with their 63 twiddles in registers, the fused Graeffe bottom pass the 64-point blocks of `E` and `O` together; layers 1-13 run class-batch by class-batch, 128 batches of 32 classes, with a batch buffer of `71,296` words (was `142,592`); the new block bodies are counted as code (4.2, 7). (ii) The transforms of stage D (the node products and the applies of 4.4) run in passes of 1 to 7 layers, the layers of each transform split by the split of least charge (4.2) in place of the evenly split passes of at most 6 layers with a last pass of at most 4 that stage C needs for its fused pointwise layers: the width-seven node transforms of 0xplemonade's `751fb1c3` (read as text, charged in our cost model); a block of 7 layers holds 128 values and 127 twiddles in the field registers, 3 twiddles beyond the 252 not reserved are loaded per block and stored per group, and the declared file counts the 128 row bases of such a block: one file of 391 words, 256 field registers of 256 bits plus 135 integer address registers. (iii) The apply of each outer step may also be the in-place whole-pair apply of 0xplemonade's entries `390451a3` (r = 7) and `dc8bb986` (r = 5) (4.4): the first `N` words of `g` and `R` are the transform arrays, only the four matrix spectra are allocated, on `N <= 3 * 2^22` points: 7 fixed-slot, 14 in place whole-pair, 10 on the earlier in-place plans. Row C `1,266,659,004,655` (was `1,272,411,466,607`), row D `406,442,442,666` (was `420,618,385,018`); footprint `3,135,406,964` bytes, `2^31.54601` (was `3,137,429,004`, `2^31.54694`); H-ONE, H-NORMAL, the success bound and the experiments are unchanged. Our entry `f673b472` against our r = 5 entry `f5723a28` (time + memory penalty 44.16842, the same algorithm and package), one change to stage D: the matrix of each outer step is applied to `(g, R)` by the direct whole-pair and fixed-slot plans of 0xplemonade's r = 10 entry `ff21bd28` (read as text, charged in our cost model; 4.4): four matrix spectra formed once, one fused pointwise pass for both outputs, no entries of `M` folded row by row of `2^16` points. The 8 largest outer steps run fixed-slot on `4,194,304` or `6,291,456` points, 10 direct whole-pair, 13 keep the in-place plans (E.2); the apply spectra lie at the far end of the pool, under its stage-C high-water mark (7). Row D `420,618,385,018` (was `825,774,552,296`); `N_max = 1,715,895,104,150`; footprint `3,137,429,004` bytes, `2^31.54694` (was `3,137,396,236`, `2^31.54693`: `32,768` bytes of code for the apply routines); row C, every other row, H-ONE, H-NORMAL, the success bound and the experiments are unchanged. Our entry `f5723a28` against our r = 5 entry `6d853b6e` (time + memory penalty 44.22332, the same algorithm and package): the union-machine charges of 0xplemonade's r = 5 entry `d4b13ccd` (44.18129; first at r = 6 in `1dcbb731`, built on our r = 15 entry `c7ef0551`), in our cost model: (i) the register file of the machine is one file of 331 words, 256 field registers of 256 bits plus 75 integer address registers (was 107: 64 field and 43 integer), `10,592` bytes counted in the footprint (7); (ii) the middle layers of the truncated transforms of stage C split 6, 6, 6 in place of 5, 4, 4, 5 (three radix-64 passes, the 64 values and 63 group twiddles of a block in registers, none spilled), so that layers 1-15 run class-batch by class-batch, 64 batches of 16 classes, with a batch buffer of `142,592` words (4.3T); (iii) the product passes of stages C and D take up to six layers (a block of `2^k <= 64` points with its `2^k - 1` twiddles in registers), the layers of each transform split as evenly as possible, the larger first, the last (fused) pass at most four layers (4.2); (iv) the unrolled bodies of the radix-64 middle block (in place of the radix-16 and radix-32 ones) and of the 5- and 6-layer product blocks: `15,528` operations of code in all (was `8,655`), one 4-byte instruction each (4.2, 7). Row C `1,272,411,466,607` (was `1,333,942,511,313`), row D `825,774,552,296` (was `848,148,491,942`); footprint `3,137,396,236` bytes, `2^31.54693` (was `2^31.54586`); H-ONE, H-NORMAL, the success bound and the experiments are unchanged. Our entry `6d853b6e` against our r = 5 entry `98f2ba70` (time + memory penalty 44.29068), two changes to its algorithm: (i) every product pass of stages C and D (the Newton and quotient products of 4.3T, the node products and the applies of 4.4) runs in the block form with running twiddle factors of our r = 8 entry `27fbfbe7` (4.2), as 0xplemonade's r = 5 entry `3237ea8c` (44.25102) does for the transforms of the half-gcd node; neither stage builds a product-pass twiddle table (the stage-D table of `2^19` entries leaves the stage-D live set, whose peak is now `2,637,733,760` bytes; the high-water mark, set in stage C, is unchanged, 7); (ii) the block loops of the transform passes of rows C and D are unrolled by four, a block charged 3 control in place of 5 (4.2), with `34,620` bytes of code (one 4-byte instruction per operation, 4.2) added to the footprint (7). The machine declares its integer address registers: one register file of 107 words, 64 field registers of 256 bits plus 43 integer registers (4.2), `3,424` bytes counted in the footprint (7), and the `576`-byte working set of the offline derivation (6.2) is counted in the footprint. Row C `1,333,942,511,313` (was `1,346,966,135,742`), row D `848,148,491,942` (was `940,293,795,311`); the footprint `3,135,080,104` bytes is claimed rounded up at five decimals, `2^31.54586` (was `2^31.546` at three). The success bound takes the `H-NORMAL` allowance `delta = 0.001` (was `0.003`) of our accepted r = 9 entry `5b96dbb5` on the same six two-centre organizer-run entries, and `H-ONE` is organizer-counted by `euclid-gcdpos-n2-t256-a`, `-b` and `euclid-gcdpos-n3-t24` in place of the one-centre entries (9.5, 10.5.1, 10.5.2): `0.392099999999997628` (was `0.390099999999997628`). Our entry `98f2ba70` against our r = 5 entry `e0ef7608` (time + memory penalty 44.35138), one change to its algorithm: the product step `M = M1 [[Q, 1], [b^2, 0]] M2` of each half-gcd node runs on the two rows `Y - 1`, `Y + 1` (`2n` points) in place of three; its entries have degree at most `2n - 1` on the normal sequence (4.4). Row D `940,293,795,311` (was `1,039,563,293,257`); every other row, the memory and the success bound are unchanged. Our entry `e0ef7608` against our r = 5 entry `ebbb87b0` (time + memory penalty 44.37412), one change to its algorithm: a Graeffe prefix (4.3G). Stage C first applies 22 Graeffe steps `g(Y) <- E(Y)^2 - Y O(Y)^2` on `O1` (`4,031,113,422` operations each) and then raises `S` to `(p-1)/2^23` (209 squaring steps in place of 231); the gcd keeps exactly the `2^22`-th powers of the usable roots (`1 <= deg G <= k(c)`), and stage F finds the root of `g_c` above the isolated one by a scan of at most `2^22` candidates on the line map (4.1.3). Row C `1,346,966,135,742` (was `1,387,466,466,885`), row F `2,232,498,018` (was `47,012`); memory unchanged. `H-NORMAL` is stated for the pair of the transformed polynomial and its organizer-run tests compute that pair (9.5, 10.5.1); `H-ONE`, every other charge and the other experiments are unchanged.
* Prior entries: `ebbb87b0` (44.37412) improved our r = 5 entry `d2edbd3d` (44.64067) by charging the loads and stores of the pass-block data words one operation each and running layers 1-12 of the truncated transforms class-batch by class-batch in a `71,296`-word buffer; `d2edbd3d` improved our r = 5 entry `647649ab` (time + memory penalty 44.83898: the one-centre algorithm of our r = 6 entry `c318f442` with bradcush's truncated-point-set stage C, entries `b30de9bf`, `a41aecdd`, and the memory schedule of 0xshikhar's entries `52120fad` and `716c3818`) by three changes: (i) stage D is the inversion-free half-gcd of bradcush (`b30de9bf`, whose source revises `4bcabff8`; read as text only), charged in this cost model with the outer-step cap `KMAX = 2^21 - 1` (4.4); (ii) the kernel charges of stage C (4.3T): the passes split top 3 | middle 5, 4, 4, 5 | bottom 4 on the 64 field registers stated as a restriction in claim.json (4.2), the form of our r = 3 entry `ef123c2b`; the bottom twiddles from the two-level table with register constants, running supergroup twiddles in the middle passes, the pruned top pass, the recovery with the path value in a register, the scaling fused into the adjacent pass, and the batch-inversion chunk in the batch buffer; (iii) each line evaluation of stage B charged at the operations it executes, `155 + 21 r = 260`, in place of `C(5) = 321` (section 3). The premises, the coins, stages A and E-G and the organizer-run tests are those of `647649ab` (`H-ONE` at `q = 0.3931`, `H-NORMAL` at `delta = 0.003` with the split of cryptogakusei's entry `4888e783`, the ABORT discipline of bradcush's `e6dcb600` and the test form of gta6rp's entry `bef31fdd`). The memory is the allocator high-water mark of the one trial (section 7).
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres, and `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.001` and supported by organizer-run tests. Both are statements about probability. The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2, the machine (391 registers, 256 field registers of 256 bits plus 135 integer address registers, counted in the memory; constants as immediates; every load, store and spill counted), stated as a restriction in claim.json as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic, the inversion-free half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8 (partial), 60, 61, 62, 63 (full) put eleven S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^11 = D = 48,828,125`. The leading coefficient is obtained by propagating leading coefficients through the eleven layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x3d8a63413498ea10d01ec5a3bc7106382d152c057486fdb7dfe795da6ea4e687` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 24,414,062`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). This gcd divides the squarefree `S^((p-1)/2) - 1`, so it is a product of `k(c)` distinct linear factors over `F_p` (9.1); stage D computes instead the gcd of 4.3G, whose roots are their `2^22`-th powers.

Construction of `g_c` by evaluation. `H = 25,165,824 = 3 * 2^23` divides `p - 1` (`p - 1 = 2^32 * 3 * q`) and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`; one inverse transform of size `H` returns the coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). Each of the `2H = 50,331,648` evaluations is one execution of the line program `L` of Appendix L at `x = c' + s` or `c' - s` (`c' = c + E0_0`, one addition per trial): `L(x) = F(x - E0_0) / OUTSCALE`, `135 + 12 r = 195` operations at `r = 5`, so the stored values are `g_c(omega^i) / OUTSCALE`, which the normalisation to monic absorbs; rounds 0 and 1 are not executed (section 2). `(F(c + s) - F(c - s)) / (2 s)` is even in `s`, so the point `-zeta^i` gives the value of `zeta^i`. The loop of Appendix B visits the positions of the transform input in storage order and takes `s` and `1/(2s)` from digit-factored root tables: per point the two table loads with their addresses and the two products 6, the two point additions 2, the two calls 2, one subtraction 1, one multiplication by `1/(2s)` 1, the store with its address and the pointer increment 3, the loop control 3: 18 operations beside the two evaluations; the outer levels and the tables are itemised in Appendix B. The twiddle table of the transform is built by stage B (4.2).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   constants (once; no twiddle table: stage B builds the table of its transform; the product passes of stages C and D use running twiddle factors, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (50,331,648 executions of L, Appendix L, in the loop of Appendix B + one inverse NTT of size 25,165,824 + the nonzero-leading-coefficient test + normalisation)
  C  g := g^(22): 22 Graeffe steps on O1 (section 4.3G); R := S^((p-1)/2^23) mod g, in the value domain on the truncated point sets O1, O2 of n' = 24,428,544 points (section 4.3T): 209 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root y of G (4.1.2); if none within Z = 64 rounds (Appendix S): trial ends.
  F  u := a 2^23-th root of y (23 Tonelli-Shanks square roots, 2-adicity 32); for j = 0, ..., 2^22 - 1: s := u mu^j, until L(c' + s) = L(c' - s); W1 = c + s, W2 = c - s (4.1.3); tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (300 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16` (the register-resident procedure and charge of Appendix S); `eps_iso <= 2.371e-15` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

4.1.3 Stage F: the root of `g_c` above `y`. By 4.3G, `y = S^(2^22)` for a usable root `S` of `g_c`, and the solutions of `S'^(2^22) = y` are `u^2 mu^(2j)`, `j < 2^22`, where `u^(2^23) = y` and `mu` is a fixed primitive `2^23`-th root of unity (`2^23 | p - 1`; a constant of the offline derivation, 6.2). `u` comes from 23 successive Tonelli-Shanks square roots: `y` is a `2^23`-th power, and if `x` is a `2^k`-th power with `1 <= k <= 23`, both square roots of `x` are `2^(k-1)`-th powers (`-1` is a `2^(k-1)`-th power, `2^k | p - 1`). The scan takes `s = u mu^j` for `j = 0, 1, ..., 2^22 - 1` and stops at the first `j` with `F(c + s) = F(c - s)` (two line evaluations of section 3). For `S' = s^2` a root of `g_c` this holds, because `F(c + s) - F(c - s) = 2 s g_c(s^2)`, so the scan stops at the latest at the `j` of `S`; any stop has `s != 0` (`y != 0`) and `F(c + s) = F(c - s)`, a collision by 2.4. Charge per candidate: `s <- s mu` 1, `c' + s` and `c' - s` 2, two executions of `L` (Appendix L; `L(c' + s) = L(c' - s)` exactly when `F(c + s) = F(c - s)`, `OUTSCALE != 0`) `2 * 195`, their calls 4, the comparison and branch 2, the loop control 3: `402`; at most `2^22` candidates, `1,686,110,208`, and the loop exit 2. The 23 square roots are charged `47,012` each (the whole row F of the algorithm without the prefix, a square root and the back-map), `1,081,276`, `W1 = c + s`, `W2 = c - s` at the stop 2, and the back-map `47,012`: row F = `1,687,238,500`.

### 4.2 Machine model and charging rules (summary; `C(5) = 321`)

Every field operation, load, store, control operation and random word is one primitive operation; `C(r) = 216 + 21 r = 321` primitive operations is one target-compression unit. The register file is the machine restriction of claim.json: one file of 391 words, 256 field registers of 256 bits plus 135 integer address registers, counted in the memory (7). The 135 integer registers are counted kernel by kernel from the loop nests and the loads and stores charged (every loop live inside a kernel holds an index and a bound, every array or table it addresses a base, a block whose `2^k` words lie at a pass stride one row base per word, a contiguous block base plus an immediate offset, and the stack pointer): the most, 135, in a block of a block-form product pass of 7 layers (below): the 128 row bases and 7 more (the data array index, the block loop bound, the position counter and its bound, the layer counter, the twist index and the stack pointer). The other kernels use fewer: the two batched radix-32 middle passes (4.3T) at most 43 (32 row bases, the block, range, group and batch loops, the array and batch-buffer bases and the stack pointer), the radix-64 middle pass 70 (64 row bases), the block-form product passes of 6 layers 70 (64 row bases), the top passes 24, the bottom passes at most 14 (the step on `O2`), the fused Graeffe bottom pass 10, the recovery 12, the stage-D loops (CRTs, pointwise, pseudo-division, applies) and the allocators at most 9. The field registers (they hold the data words and the group twiddles of a radix-8, radix-16, radix-32 or radix-64 block, at most the 64 values and 63 twiddles of a radix-64 block or of a bottom-pass block, or the 64-point blocks of `E` and `O` of a fused Graeffe bottom block with their 63 twiddles (191 of the 256), none spilled, or the `2^k` values and `2^k - 1` twiddles of a block-form product block, `k <= 7`; the largest set is 255 of the 256 (`k = 7`): 4 field registers hold the running factor, the step constants and the temporaries of the chain, so of the 255 words of a 7-layer block 3 twiddles are loaded from memory once per block and stored once per group, 2 operations each (in the pass charge below); every other value is charged as a load or store; a load or store of a data word of a block of a transform pass of 4.3T is one operation, its address the base plus index of the load or store itself: one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`) and the 135 integer registers are the only register assumption; the algorithm runs on one thread, no dispatch. The block loops of the transform passes of rows C and D are unrolled by four: a block is charged 3 control in place of 5 (the loop counter, test and branch, 3 operations per four blocks, charged 1 per block, and the 2 address updates; a block that advances more array pointers is charged 1 more per pointer: the bottom block of a squaring step on `O2` 2 more (data, `A2`, `g`, output; 3 on a 1-bit, the point), the fused Graeffe bottom block 1 more (`E`, `O`, output); a block loop of one or two blocks is straight code). This applies to the radix-32 and radix-64 middle blocks (4.3T: 307 and 707), the 64-point blocks of the bottom passes of 4.3T, the fused bottom block of a Graeffe step (4.3G), and the blocks of the block-form product passes of stages C and D (below); the fused pointwise passes, the top passes and row B keep their charges. The three further copies of each unrolled block body (every body at its full charge: the radix-32 and radix-64 middle blocks, 307 and 707; the 64-point bottom-pass blocks, forward 774, inverse 839, the step bottoms of `O1` 1,671 and of `O2` 2,059 and 2,252 (without and with the 1-bit multiplication); the fused Graeffe bottom block 2,376; the forward and inverse block-form product-pass blocks of 1 to 7 layers, 10, 23, 55, 131, 307, 707 and 1,609 each; `16,669` per copy) hold `50,007` primitive operations, one 4-byte instruction each (the instruction width of the machine declared by cryptogakusei `1533f8f0`, its H2): `200,028` bytes of code, and one copy of each body that is new against the program text of our entry `f673b472` (the radix-32 middle block, the six 64-point bottom-pass bodies, the product blocks of 7 layers), `13,496` operations, `53,984` bytes, added to the footprint (section 7). The two straight-line row bodies of the node (4.4: the fold row of `8 * 22 + 3 = 179` and the two-output row of `8 * 20 + 3 = 163` operations, eight positions each) are `342` instructions, `1,368` bytes, added to the footprint (section 7). Allocation: one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes. A block of more than `2^14` bytes is served by the two-ended pool (one region, two ends, first-fit in address order, the statements marked `# pool:H` using the high end); every smaller block by its slab class (the least `j >= 7` with `2^j >= need`, a slot of `2^j` bytes). The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows (a pool request `97` operations besides the walk and `13` per block examined, a slab request at most `126`, a free `81` for a slab block and at most `105` for a pool block). The memory of both allocators is the arena of section 7. Twiddle tables: none is built in init; stage B builds the table of its transform (`2^(a-1)` entries for `3*2^a` points: its root, 5 operations per entry and the loop) and frees it, charged in row B. Every product pass of stages C and D (the Newton and quotient products of stage C, 4.3T; the node products and the applies of stage D, 4.4) forms its twiddles as running factors, in the block form of our r = 8 entry `27fbfbe7` (as 0xplemonade `3237ea8c` and `dde74bba` use it for the transforms of the half-gcd node): per pass and layer the step and chain constants (`150` operations: at most 64 squarings, the loop, 4 loads and stores); per position `j` (`2^(a-l0-k)` of them) the running root advanced by one multiplication, `k - 1` squarings and `2^k - 1 - k` multiplications by register constants give its `2^k - 1` twiddles, kept in registers, plus 5 control (`2^k + 4`); the `2^l0` blocks that share them each load `2^k` values and store `2^k` values at one operation each (base plus index), make `k 2^(k-1)` butterflies at 3, plus 3 control (the block loop unrolled by four) (`2 * 2^k + 3 k 2^(k-1) + 3`). Per pass of `k` layers the blocks and positions are joined by the per-pass overhead: the `150 k` of the constants and `9 k + 19` (forward) or `9 k + 20` (inverse) operations of the pass entry, pointers, exit and call, so that a forward pass of `k` layers on `2^a` points costs `2^(a-k) (2 * 2^k + 3 k 2^(k-1) + 3) + 2^(a-l0-k) (2^k + 4) + 159 k + 19`; the fused pointwise layers of a product charge `159 k + 17` (squaring) or `159 k + 18` (product) besides their groups. The layers of a product transform of stage C (the `2^a`-point part of a plan; the Newton and quotient products, 4.3T) are split top-down into passes of at most 6 layers: the last, fused, pass takes `min(4, a)` layers and the other `a - min(4, a)` are split into `ceil((a - min(4, a)) / 6)` passes as evenly as possible, the larger first (`a = 22`: 6, 6, 6, 4; `a = 21`: 6, 6, 5, 4; `a = 11`: 4, 3, 4). The layers of a transform of stage D (the node products and the applies of 4.4: plain forward and inverse passes, no fused pointwise layers) are split into passes of 1 to 7 layers by the split of least charge for one forward plus one inverse transform of `2^a` points (the passes taken in order from level 0; a pass of `k` layers starting at level `l0` charged as above, `9` or `10` more per pass for the entry and exit of a forward or inverse pass), found by dynamic programming over the pass starts; for `k = 7` the term per block is `2 * 2^7 + 3 * 7 * 2^6 + 3 + 6 = 1,609` and the term per position `2^7 + 4 + 6 = 138`, the 6 being the 3 spilled twiddles at 2 operations each. The split for each `a` = 5 to 23 (the passes in order): 5: 5; 6: 6; 7: 7; 8: 5, 3; 9: 5, 4; 10: 6, 4; 11: 6, 5; 12: 6, 6; 13: 6, 7; 14: 7, 7; 15: 6, 5, 4; 16: 6, 5, 5; 17: 6, 6, 5; 18: 6, 6, 6; 19: 6, 6, 7; 20: 6, 7, 7; 21: 7, 7, 7; 22: 6, 6, 5, 5; 23: 6, 6, 6, 5; one 4-byte entry per `a`, `76` bytes of static data in the footprint (7). Stages C and D build no product-pass twiddle table. The passes of 4.3T use two-level root tables of `4 x 4,096` words (built in stage C and kept live into stage D, whose applies use the same truncated transforms).

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(22)`, 22 Graeffe steps, then computes `R = S^e mod g^(22)`, `e = (p-1)/2^23` (2-adicity 32), and stage D takes `G = gcd(g^(22), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^22)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(22)(Y) = prod_i (Y - S_i^(2^22))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^23`-th powers of `F_p^*`. If `S_i^(2^22) = u^(2^23)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^22) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^23) = 1` (`2^23 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^22) = v^(2^23)`. So `deg G` is the number of distinct `2^22`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input blocks below the length (3 or 2 of the 8 per offset, two offset ranges per batch; no zero-fill); the fused bottom pass (the 64-point blocks of `E` and `O` and their 63 twiddles held in registers together, 4.2) forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point); one truncated inverse stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a batch buffer of `71,296` words of their own; no array is added and the high-water mark of section 7 is unchanged. One step is `3,790,556,562` operations (Appendix E.1), 22 steps; stage C then runs 209 squaring steps in place of 231 (the exponent loses 22 low zero bits). A step saves one squaring step (`5,541,224,588`) for `3,790,556,562` and doubles the scan of 4.1.3 (`2^s * 402` with the program `L`); `s = 22` is kept: `s = 23` would lower the total by `64,510,794` operations (`5 * 10^-5` in `time_log2`) but changes the transformed pair of `H-NORMAL` and its organizer-run tests.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(22)`: `g^(22)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^22` values `x` with `x^(2^22) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(22) vanishes on O1) <= 2^22 n' (D - 1) / p = eps_g < 2^-181`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 1491 of 2048 nodes)

Point sets. `N = 2^25` divides `p - 1` (2-adicity 32). Let `psi` have order `2^26`, `H_N = <psi^2>` and `Y = X^(2^14)`. `H_N` is the union of the 2048 depth-11 nodes `{x : x^(2^14) = r_j}`, `r_j` the 2048-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 1491 nodes, `n' = 1491 * 2^14 = 24,428,544 >= m + 1 = 24,414,063` points, and `O2` the same 1491 nodes of the coset `psi H_N` (`x^(2^14) = r'_j`, `r'_j^2048 = -1`), disjoint from `O1`. `P1 = prod_{j<1491} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (1491 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<2048} P_k Y^k` with `deg P_k < 2^14` and `P_k = 0` for `k >= 1491`; its values on the 1491 nodes determine it and are determined by it (the CRT for the 1491 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 3 layers on all `N/8` offsets (no truncation saving is charged), the middle layers only on the blocks above present nodes, and the bottom 6 layers on the `n'` points. The inverse runs the same layers in reverse, scales each 64-point block of its bottom pass by `diag(1, c^-1 J)` (`c = y^64` of the block, `V^T V = 64 diag(1, cJ)`; 63 multiplications and the load of `c^-1`, 65 operations per block), and recovers the residues of the dropped part `[1491, 2048)`, the maximal subtrees `{1491}`, `{1492..1495}`, `{1496..1503}`, `{1504..1535}`, `{1536..2047}` (depths 11, 9, 8, 6, 2), from the known zero chunks `P_k = 0` along their paths to the root, as bradcush recovers the one dropped leaf; with the value of the path held in a register this is charged 8 operations (3 multiplications, 3 additions, the load of the known value) per point of a dropped subtree per layer of its path and one store (2) per point. Layers 1-13 (the top pass, the first two middle passes and the recoveries) act on each class of the `8,192` positions with equal low 12 bits separately (`5,964` in `O1`, `2,228` above `n'`: the dropped nodes and the lane-5 tail), so they run class-batch by class-batch, `128` batches of `32` classes, the `2,228` positions above `n'` of each class of the batch held in one batch buffer of `71,296` words (one transform runs at a time) and discarded after the batch; the passes below layer 13 touch only the `n'` positions. Charged once per batch: the groups, the pass overhead and the batch loop of the two batched middle passes (the first radix 32: `8` groups, each with `32` inner loops of 5, one per contiguous range of the batch offsets; the second: `256` groups), the top-pass overhead with its `1,024` inner loops (`60 + 20 + 1,024 * 5`), the path constants of each recovery (`256`), and before the top of each truncated forward the zero-fill of the `5,760` coefficient positions of lane 5 above `n'` (a store, 2, each and the loop). The passes are fused as in `b30de9bf` 4.5 under the 256 field registers of the declared register file (4.2), the 25 layers split 3 | 5, 5, 6 | 6 (`TR_CFG`): a bottom pass (64-point blocks: forward layers, the pointwise map, inverse layers; one set of 63 twiddles for both directions, held in registers with the 64 values, 67 operations per block: two loads from the two-level table, one multiplication, five squarings, 57 multiplications by register constants; `V^T V = 64 diag(1, cJ)` with `c = y^64` of the block, so every inverse bottom pass scales each block by `diag(1, c^-1 J)`: 63 multiplications and the load of `c^-1`, 65 operations per block), two middle passes of radix 32 (a running supergroup factor, 1 multiplication per group, and the group twiddles formed from it and held in registers: 32 loads and 32 stores at one operation each, 80 butterflies and 3 control (the block loop unrolled by four, 4.2), 307 per block, 31 twiddles by 4 squarings and 26 multiplications and control, 36 per group) and one of radix 64 (64 loads and 64 stores at one operation each, 192 butterflies and 3 control, 707 per block, 63 twiddles by 5 squarings and 57 multiplications and control, 68 per group), and a pruned top pass that fuses the inverse top of one set with the forward top of the other: only the `b = 6` depth-3 subtrees that hold points of the 1491 nodes are formed or read (the butterflies of the 8-point top block counted on the needed and nonzero lanes, `_top_counts`), and the coset twiddle is applied on those `b` blocks. The applies of stage D on `n'` points use the same transforms.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and per block the load of `delta_j` (2) and 2 address updates beyond the block control (4.2); 3 more per point for a 1-bit (the load of the point and a multiplication) and 1 more address update per block.

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^22 = 6,291,456` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 4,208,787` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^22` points with running twiddle factors in the block form of 4.2); on node `j` of `O2`, `x^v P1(x) = r'_j^256 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^16` points: prefix products, one inversion, two multiplications per point; the `2^16` prefixes are kept in the batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-181` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `209` squaring steps (the exponent `(p-1)/2^23`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 1491 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g` on `O2`, `A` on `O2`, `A` on `O1`, `k1` on `O1`), the batch buffer of `71,296` words, the tables (`1,521 + 16,384` words: 30 constants, the 1491 `delta_j`, the two-level root tables) and, while `q` is formed, the Newton arrays. The step-by-step count is expanded in Appendix E.1 and totals **row C = 1,266,659,004,655** (section 6).

### 4.4 Stage D: the inversion-free half-gcd (the method of bradcush `b30de9bf`/`4bcabff8`)

`G = gcd(g, R - 1)` is computed by a recursive half-gcd on the normal remainder sequence that keeps every matrix in coefficient form and never inverts a leading coefficient (pseudo-division). A node `hgcd(a, b, k)` of budget `k = 2^j - 1` runs its first child (budget `2^(j-1) - 1`) on the top window, applies the child's matrix `M1`, `(c, d) = adj(M1)(a, b)`, makes one pseudo-division with a quotient of degree 1 (its remainder `e` only on the `2^j - 1` positions the second child reads), runs the second child (`M2`) and forms `M = M1 [[Q, 1], [b^2, 0]] M2`. The apply of a node is formed on the three rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), one transform of `n` points per row in the block form of 4.2 (the twist of the rows `Y + 1`, `Y - i` as a running product fused into the pass, 2 operations per point), and recombined by a 3-row CRT (22 operations per position); the product `M` on the two rows `Y - 1`, `Y + 1` only, recombined by the 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` (10 operations per position, the `1/2` folded into the `1/n` of the inverse). The product needs no third row: on the normal sequence every quotient has degree 1 and `b^2` is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the values of each child's matrix on the row `Y - 1` are reused by its parent, the values of `M1` from the apply are reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). Two loops of the node are single passes. Fold: the window `a` of `4n` coefficients (`b` has `4n - 1`) is reduced modulo `X^n - 1`, `X^n + 1` and `X^n - i` in one loop over the positions `t < n`: it loads `a_0 = a[t]`, `a_1 = a[t + n]`, `a_2 = a[t + 2n]`, `a_3 = a[t + 3n]`, forms `s = a_0 + a_2`, `s' = a_1 + a_3`, `u = a_0 - a_2`, `u' = a_1 - a_3` and stores `s + s'` (row `Y - 1`), `s - s'` (row `Y + 1`) and `u + i u'` (row `Y - i`, `i^2 = -1`, one multiplication), which are `a mod (X^n - c)` for `c = 1, -1, i` because `X^(jn) = c^j` there. It is charged 22 per position (four loads and three stores, each with its address update, 2 operations, and eight field operations) and `2 + for8(n)` for the eight-element loop; the twist of the rows `Y + 1` and `Y - i` by their running factors is charged as before, 2 per point and row. Pointwise maps: on each of the three rows one pass forms `C = r22 A - r12 B` and `D = r11 B - r21 A` from the row values of `a`, `b` and the four entries of `M1`, and on each of the two rows of the product two passes form the two columns of `M = P M2`, `P = M1 [[Q, 1], [b^2, 0]]`, from the entries of `P` and the column of `M2`; each is one two-output pass (six loads, four multiplications, a subtraction, an addition and two stores over the operands), charged 20 per point as the direct whole-pair row of 0xplemonade's `ff21bd28` (read as text), and `2 + for8(n)` for the loop. The bodies of the two loops (eight positions each) are code (4.2). The base case is budget `2^6 - 1`, two remainder steps per pass.

The driver: while the degree `n` of `g` admits it, `k = 2^j - 1` is the largest with `2k + 1 <= n` and `k <= KMAX = 2^21 - 1` (the outer-step cap of weijiekoh `a78f526e`), `hgcd(k)` runs on the top window and its matrix is applied to `(g, R)` in place (`plan_apply`: the cheapest by charge of the plans (a), (b), (c), (d) below); from degree 254 down the schoolbook pseudo-division Euclid, then the normalisation of `G`. Every node works in one bump arena (allocation and release 10 operations each), `node_mem(j)` words at its peak (`33,554,176` at `j = 21`). On the normal sequence every length, parameter and allocation is a function of `m` alone: 31 outer steps (7 fixed-slot applies on `6,291,456` points, 14 in-place whole-pair applies on `8,388,608` down to `384` points, 10 in-place applies of plan (a) on `196,608` down to `256` points) and the Euclid from degree 141. The apply plans: (a) in place (the plans of our earlier entries): `g` and `R` folded or zero-extended in place to a `2^a`- or `3*2^a`-point transform in the block form of 4.2, the four entries of `M` transformed into a buffer of `4N` words, two pointwise loops per output, two inverses, `1/N` fused into the pointwise loop (the truncated transform of 4.3T on `n'` points, with the entries of `M` row by row of `2^16` points, is still offered and no longer chosen). (b) direct whole-pair and (c) fixed-slot, the apply plans of 0xplemonade's r = 10 entry `ff21bd28` (read as text, charged here), on a plan of `N = 2^a` or `3*2^a <= 3*2^21` points: the four entries of `M` (`k + 1` coefficients each) are transformed once into four matrix spectra of `N` words and the coefficient matrix is freed; `1/N` is formed by one inversion (`powcost(p - 2) + 2,310`); one fused pointwise pass forms both outputs from the two operand spectra (22 operations per point: 6 loads, 4 multiplications, 2 additions or subtractions, 2 stores, and the loop control), then two inverse transforms and the store of the outputs over `g` and `R` scaled by `1/N` (load, multiplication, store, loop: 8 per coefficient). (b) when `N >= lc = n - k + 1`: `g` and `R` are folded modulo `X^N - 1` into the two operand spectra (a copy, and 7 per folded coefficient); on the normal sequence `adj(M)(g, R)` has `lc` coefficients (its top cancels), so its cyclic product of length `N >= lc` is exact. (c) otherwise: the `lc` outputs in blocks of `B = N - k` from the top down; block `[s, e)` transforms the windows `g[s - k, e)` and `R[s - k, e)` (at most `N` coefficients; output `i` reads the operand coefficients `i - k .. i` only), the cyclic wrap reaches only the first `k` positions of the window, which are not outputs of the block, and the outputs are stored over `g[s, e)`, `R[s, e)`, which no lower block reads (20 control per block). (d) in place whole-pair (the in-place family of 0xplemonade's `390451a3` and `dc8bb986`, read as text, charged here), when `lc <= N <= lb` (`lb = la - 1` the length of the shorter array, so both arrays hold at least `N` words) on a plan of `N = 2^a` or `3*2^a <= 3*2^22` points: the four entries of `M` are transformed into four matrix spectra of `N` words as in (b); the coefficients of `g` and of `R` above `N` (charged as `la - N` each) are added onto their first `N` words in place (7 per folded coefficient and the loop) and the first `N` words of `g` and of `R` are transformed in place (the radix-3 stage and three rows of block-form passes for `3*2^a`, no copy and no zero fill); one fused pointwise pass forms both outputs over the two operand spectra (22 per point); two inverse transforms leave `c` over `g` and `d` over `R`, the `lc` outputs scaled by `1/N` (8 per coefficient); only the four matrix spectra are allocated (the coefficient matrix freed once they are formed). The transforms are those of 4.2: the radix-3 stage and the block-form passes for `3*2^a` points, a copy, a zero fill and the block-form passes for `2^a` points, in the passes of 1 to 7 layers of the split of 4.2.

The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division tests that its quotient has degree 1 (inside the fixed charge of each division: 30 per node division, 10 per base step) and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter (2 operations, twice per node), and a zero remainder also ends the trial; on any other case the trial ABORTs (section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The charges are those of 4.2 (expanded in Appendix E.2); the total is **row D = 354,378,608,236** (sections 6.3, 6).

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^22)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (primitive operations; `C(5) = 321`)

| row | what is charged | operations |
| --- | --- | --- |
| init | constants and bookkeeping (once; no twiddle table, 4.2) | 17,983 |
| setup | the line (`line_setup`, once) | 4,910 |
| A (per trial) | stage bookkeeping, loop test and update, the coin draw (63, two words), one allocation | 1,228 |
| B (per trial) | `50,331,648` executions of `L` at `195` operations each (section 3, Appendix L), the point loop on root tables `457,378,879` (Appendix B), the twiddle table, the inverse transform of size `25,165,824` and the normalisation `2,443,411,920` (unchanged) | 12,715,462,159 |
| C (per trial) | the Graeffe prefix, 22 steps (section 4.3G), then `S^((p-1)/2^23) mod g` in the value domain on the truncated point sets `O1`, `O2` (1491 of 2048 nodes, `n' = 24,428,544`), VSHIFT = 2, 209 squaring steps (section 4.3T); expanded in Appendix E | 1,266,659,004,655 |
| D (per trial) | inversion-free half-gcd of `(g, R - 1)` (node products on two rows; outer-step applies on the whole-pair, fixed-slot and in-place plans of 4.4), charged for the normal remainder sequence with the quotient and return tests (sections 4.4, 6.3), product passes in block form (4.2); expanded in Appendix E | 354,378,608,236 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, register-resident, each at most `R(16) = 196,915` with its draw (Appendix S), the stage bookkeeping 1,000 and the load of `G` into registers 200 | 12,603,760 |
| F (per trial) | the `2^23`-th root of `y` (23 square roots at 47,012), the scan of at most `2^22` candidates at 402 and its exit, `W1`, `W2` 2, the back-map 47,012 (4.1.3) | 1,687,238,500 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 321 + 32` | 7,452 |
| trial-loop (per trial) | trial-loop bookkeeping (12) and the allocator reset after an ABORT (1,000), charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size | 108,115 |
| output rows | the fixed output rows (stages H and I) | 3,390,080 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 1 * T_trial + T_off` | **1,635,457,448,090** |

`T_off = 1,000,000` (the declared cap; the count is at most `367,149`, 6.2); `T_trial = A + B + C + D + E + F + G + trial-loop = 1,635,452,927,002`; `T_fixed = init + setup + plan_invN misses + output rows = 3,521,088`; `K = 1`, so `N_max = 3,521,088 + 1,635,452,927,002 + 1,000,000 = 1,635,457,448,090`. `log2(N_max / 321) = 32.24640...`, rounded up at five decimals to `32.24641`. Rows C and D are expanded part by part in Appendix E (E.1, E.2) from the dimensions of 4.3T and the half-gcd levels of 4.4 with the kernel charges of 4.2; the parts add up exactly to `1,266,659,004,655` and `354,378,608,236`.

### 6.1 Validation
The kernel charges and the allocator rules are those compared with the instrumented totals of our executed runs at `r = 3, 4, 5` (the arena rule within 64 bytes of the measured heap peaks there); the truncated-set stage C (4.3T) has no executed counterpart, and its count is the formula of Appendix E. Rows C and D are the finite recurrences of Appendix E (E.1, E.2), summed term by term; no coefficient is fitted or extrapolated.

### 6.2 Offline derivation
The literals of the sources are computed once, offline, from `p` and the organizer's 192 round constants and 9 MDS entries, one literal at a time (working set: at most 16 words of 32 bytes and a 64-byte digit buffer; the literals of Appendices L and B use at most 64 further words, section 7); each is the value of one closed formula, with no search and no choice. The 75 literals of Appendix L (its 74 constants and `E0_0`) take at most two inversions (330 field operations each) and 40 products each, `75 * 700` field operations at 4: at most `210,000`; the 454 entries of the root tables of Appendix B (powers of `zeta`, the 448 table entries by successive products, eight inversions for the inverse tables and the row constants) at most `5,000` field operations at 4: `20,000`; with the `137,149` counted below the offline work is at most `367,149`, inside the declared cap. Count in the primitives of 4.2 (orchard-field-ram-v2: every field operation, load, store and control operation is 1): a field operation is charged 4 (the operation, two operand loads, one store), a 64-bit word operation 3 (the operation, one load, one store), a hexadecimal digit 5 (its load, the table load, a shift, an or, the loop control). (a) Input: 202 values of 64 hexadecimal digits (`p`, the 192 round constants, the 9 MDS entries), 324 each with the 4 word stores: `65,448`. (b) Field literals, 499 field operations: `2 = 1 + 1` (1); `R = 2^256 mod p`, `2` squared 8 times (8); `R^2 mod p` (1); the Montgomery forms `x R mod p` of the 201 organizer constants (201); `2^65 R mod p` (`2` squared 6 times, times `2`, times `R`: 8); `5 = 2 + 2 + 1` (2); `5^t R mod p` with `t = (p-1)/2^32`, the odd exponent of the Tonelli-Shanks of stage F (223 bits, 46 of them 1: 222 squarings, 45 multiplications, times `R`: 268); `mu R mod p`, `mu = (5^t)^(2^9)` of order `2^23` (9 squarings, times `R`: 10); charged `4 * 499 + 3 * 222` (the bit steps of the square-and-multiply) `= 2,662`. (c) Word literals, 90 word operations: `p - 1` (4), `t` (a shift by 32 over 4 words, 12), `(t+1)/2` (16), `(p-1)/2` (12), `p - 2` (4), `e = (4(p-1)+1)/5` (a shift by 2 into 5 words 15, plus 1, a division by 5 word by word 10: 26), `-p^-1 mod 2^64` (5 Newton steps `x <- x (2 - p_0 x)` from `x = p_0`, 3 each, and a negation: 16); charged `3 * 90 = 270`. (d) Output: 212 literals of 64 hexadecimal digits (the 201 Montgomery forms, `R`, `R^2`, `2^65 R`, `5^t R`, `mu R`, `t`, `(t+1)/2`, `(p-1)/2`, `p - 2`, `e`, `p`), 324 each, and `-p^-1 mod 2^64` (16 digits, 81): `68,769`. `T_off = 65,448 + 2,662 + 270 + 68,769 = 137,149` operations. The ledger charges the declared cap `1,000,000 >= T_off` (`preprocessing_log2 = 20`, `2^20 = 1,048,576`), inside `N_max`: a counted bound, not a premise.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g, R - 1)`, `g = g_c^(22)` (4.3G): every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the pseudo-division of a node, each step of the base case and of the closing Euclid) tests, before it does any work beyond reading the two leading coefficients, that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state at the start of the trial (`1,000` operations, charged in every trial). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because a node of budget `2^j - 1` calls two children of budget `2^(j-1) - 1` and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the parameters of the outer loop (`k = 2^j - 1`, the largest with `2k + 1 <= n` and `k <= KMAX`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls and divisions produce has degree at least the base-case bound, so every gcd of degree at most `DMAX = 16` first appears in the classical Euclid below the base-case degree, after a prefix of the degree-0 work; a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The method follows bradcush's notes (`b30de9bf`, whose source revises `4bcabff8`) and the outer cap follows `a78f526e`, all read as text only (no entry script was run, compiled or imported). Appendix E.2 expands, for `r = 5`, the charge of stage D for the normal sequence with the tests, `354,378,608,236`, outer step by outer step.

The `r = 5` trial (`~3.14 GB`, `~1.7e12` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the register file of 391 words (256 field, 135 integer address registers) is the machine restriction of claim.json.

## 7. Memory: the arena of one trial

The arena is the capacity of the allocator of 4.2 on the allocation/free sequence of the trial. Appendix E.3 runs the allocator on every allocation and free of the trial in the order of the program and reports the two-ended-pool high-water mark (the largest sum of the extents of the two ends over the trial), the slab area and the peaks of the live set per stage. The two-ended pool takes the blocks of more than `2^14` bytes. Under the H-NORMAL ABORT the stage-D live set is the normal-case walk: `g` and `R` (`n'` words each), the root tables of 4.3T kept from stage C, and per outer step the bump arena of `hgcd(k)` (`node_mem(j)` words, the matrix `M` at its bottom, the rest released after the call), then, for an apply of plan (b) or (c) of 4.4, four matrix spectra of `N` words at the high end of the pool (the coefficient matrix freed once they are formed) and two operand/output spectra of `N` words at the low end (`N <= 3*2^21`: at most `6 x 201,326,656` bytes with headers), for plan (d) the four matrix spectra alone (`N <= 3*2^22`), or for plan (a) the buffer of the four transforms of the entries of `M`; a trial with any other sequence ends after a prefix of these allocations (6.3). The stage-D live peak is `2,906,177,600` bytes, below the stage-C peak; the stage-D trace of Appendix E.3 has no event that raises the pool's high-water mark. The high-water mark is `3,129,708,480` bytes, reached in stage C (the four arrays of `n'` words of 4.3T, the batch buffer of `71,296` words and the tables of `1,521 + 16,384` words; each block with its 64-byte header: `4 x 781,713,472 + 2,281,536 + 573,056`), plus 128 bytes so the unused middle is always at least 128 bytes. The Graeffe prefix (4.3G) holds `E` and `O` on `O1` in the arrays of `A` on `O2` and on `O1` before stage C fills them, with a batch buffer of `71,296` words that it frees: it adds no array and leaves the high-water mark unchanged. The only blocks of the walk that are not served by the pool are the four matrix spectra of the in-place apply of the 30th outer step (`N = 384` points, `12,352` bytes each with the header), which take slab class 14 (a slot of `2^14` bytes; slab area `65,536` bytes). Stages E and later hold at most 16 small arrays and the free-list heads: `16,896` bytes. The arena is `3,129,791,040` bytes (two-ended pool `3,129,708,480 + 128`, slab `65,536`, stages E and later `16,896`). Peaks of the live set per stage (bytes): A `781,713,472`; B `1,721,237,696`; C `3,129,708,480`; D `2,906,177,600`. With `5,567,340` bytes of code and static data (`200,028` of them for the three further copies of the unrolled block bodies and `53,984` for the first copies of the bodies new against the text of `f673b472`, 4.2; `1,368` for the two row bodies of the node of 4.4; `32,768` for the apply routines of 4.4; `76` for the table of the stage-D splits, 4.2; `28,672` for the program `L` with its call sites and its 75 literals, the root tables of Appendix B with their nest, the stage-E routine of Appendix S and the 64 further words of the offline derivation, at most `24,516`, Appendices L, B, S), the register file of the machine (391 words of 256 bits: 256 field and 135 integer address registers, 4.2; `12,512` bytes), the working set of the offline derivation (6.2: 16 words of 32 bytes and the 64-byte digit buffer, `576` bytes) and a `65,536`-byte stack, the footprint is `3,135,437,004` bytes `= 2^31.546019`, claimed as `memory_log2_bytes = 31.54602` (rounded up at five decimals); the allocator walk of Appendix E is unchanged (its printed total is the footprint before the `28,672` bytes of Appendices L, B, S). No stored advice; the twiddle table of stage B and the root tables of stage C are built at run time and charged in their rows, and the product passes of stages C and D form their twiddles as running factors (4.2).

## 8. Review points, answered by location

1. Row D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3): by the prefix lemma every trial executes a prefix of the normal-case work, so the time and memory bounds hold for every sequence; `H-NORMAL` (9.5) enters only the success probability.
2. The outer-step cap (4.4) is a constant of the algorithm (`KMAX = 2^21 - 1`); the stage-D allocations (the bump arena of each `hgcd`, the buffers of the apply) are walked by Appendix E (the high-water mark `3,129,708,480` is set in stage C; the stage-D live peak `2,906,177,600` is below it, in the two-ended pool and slab class 14 (4.4, 7); no stage-D event raises the high-water mark). All 335 stage-D pool events of Appendix E.3 (the first 24 are listed) follow one rule: the allocator of 4.2 (first fit in address order) on the allocations and frees of the stage-D arrays of 4.4 in program order, their sizes fixed by `m` on the normal sequence; the largest sum of the two ends over all 335 events is `2,906,177,600` bytes (event 119).
3. Row B reproducible from sections 3 and 6 and Appendices L, B (evaluations * 195, the operations of `L`, + the point loop `457,378,879` + the twiddle table, the inverse transform and the normalisation `2,443,411,920`).
4. The offline derivation is counted literal class by literal class in 6.2 (`T_off = 137,149` operations for the literals of the base, at most `367,149` with those of Appendices L and B) and charged at the declared cap `1,000,000` (`preprocessing_log2 = 20`); the cap over the count moves `time_log2` by less than `10^-6`.
5. The mem penalty uses the rounded-up `mem_log2`, a self-penalizing over-charge.
6. `success = q - delta - eps_coin - eps_iso - eps_g >= 0.39` from the premises `H-ONE` and `H-NORMAL` (9.2, 9.5) with `K = 1`, `q = 0.3931`, `delta = 0.001`; the value is `0.392099999999997628`. The `H-ONE` allowance below the law value is stated exactly (`0.3934693 - 0.3931 = 0.0003693`; `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound, 9.1), and `delta = 0.001` is the declared premise; the 3,072 organizer-seeded sequences are reproducible observations consistent with it (10.5.1).
7. The organizer-checkable output is the returned witness-pair count. For euclid-gcdpos (10.5.2) a pair is returned only when `deg G >= 1`, so that count is the organizer-counted good-centre fraction at `N = 2, 3`; the step from there to `N = 11` is the premise H-ONE (9.1), not an organizer-verified proof.
8. The Graeffe prefix (4.3G) is exact and adds nothing to the premises of the time or the memory; the success bound uses `H-NORMAL` stated for the pair of the transformed polynomial (9.5), whose organizer-run tests compute that pair (10.5.1).

## 9. The premise and the success bound

### 9.1 H-ONE
The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (stage D returns `G` with `1 <= deg G <= k(c)` when `k(c) >= 1`, 4.3G). The premise states `q = 0.3931`, the law value `1 - e^(-1/2) = 0.3934693` (9.3) less the extrapolation allowance stated exactly as `0.0003693`; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292`. The split of the allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`: here `q = 0.3931` with a separate `H-NORMAL` allowance `delta = 0.001` (9.5), as in our accepted r = 9 entry `5b96dbb5`. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1, 10.5.2.

### 9.2 The success bound
The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g, R_c - 1)` (`g = g_c^(22)`, 4.3G) is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.001`). The Graeffe prefix and the value-domain stage C reproduce `g^(22)` and `R = S^((p-1)/2^23) mod g^(22)` exactly (4.3G, 4.3T) and add no premise; stage C needs `g^(22)` nonzero on `O1`, which fails with probability at most `eps_g = 2^22 n' (D - 1) / p < 2^-181` over the centre (4.3G). If `E_c` and `N_c` hold and `g^(22)` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g^(22), R_c - 1)` with `1 <= deg G <= DMAX` (4.3G); a successful isolation and the scan of 4.1.3 then end in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g^(22)` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.001`, `eps_iso <= 2.371e-15`, `eps_coin <= 1.404e-76`, `eps_g < 2^-181`: `q - delta = 0.3921`, and the value is `0.392099999999997628 >= 0.39`. The bound stays at or above `0.39` for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso <= 2.371e-15`. Finite derivation: `G` divides `Y^((p-1)/2^23) - 1` (4.3G), a divisor of `Y^(p-1) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps `T = gcd(H, (X + a)^((p-1)/2) - 1)` when `1 <= deg T < deg H` and `H` otherwise (Appendix S), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128` of uniform (4.1.1), so per round the bound is `1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 <= 2.371e-15`; the looser stated value `2.371e-15` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(h_c, R_c - 1)`, where `h_c = g_c^(22)` is the 22-fold Graeffe transform (4.3G) of the monic odd part `g_c` of section 3 (monic, degree `m = 24,414,062`) and `R_c = S^((p-1)/2^23) mod h_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.001` (`2^-9.966`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-203`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.001`) to the structured pair `(h_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-g22-a` to `-f` compute the complete Euclidean sequence of `(h_c, R_c - 1)` for this construction (22 Graeffe steps, exponent `(p-1)/2^23`) on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24-g22` and `euclid-normal-n4-t2-g22` do the same at `m = 62, 312`. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.001` is the declared premise). Not verified at `r = 5`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, euclid-gcdpos) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-g22-a to -f compute the complete Euclidean sequence of `(h_c, R_c - 1)` (the pair of 9.5: 22 Graeffe steps, exponent `(p-1)/2^23`) for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n3-t24-g22 and -n4-t2-g22 compute one sequence per trial at `m = 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the count of trials that return a pair is a reproducible observation consistent with the premise H-NORMAL (9.5). We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.001` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure, not the score-critical basis. Our runs of the six -l2-g22 entries with local seeds (one CPU; 6.2 to 6.5 s each on our workstation): 3,072 sequences, all normal, 256 pairs per entry; the gcd had positive degree for 1,183 of the 3,072 centres (0.385). Our runs of -n3-t24-g22 and -n4-t2-g22: 24 and 2 sequences, all normal. The organizer-checkable output is the returned witness-pair count (here the number of trials whose sequences are all normal).

10.5.2 Organizer-counted good centres (H-ONE). euclid-gcdpos-n2-t256-a, -b and euclid-gcdpos-n3-t24 take one organizer-seeded centre per trial at `N = 2, 3` (`m = 12, 62`), compute `G = gcd(g_c, R_c - 1)` with `R_c = S^((p-1)/2) mod g_c` (no Graeffe prefix; `deg G = k(c)`, the statement of H-ONE, which the prefix does not change, 4.3G) and return a witness pair ONLY when `deg G >= 1`, so the organizer's returned-pair count is the good-centre count. Expected: the fraction of good centres is the law of 9.3, a theorem at these depths; the returned counts are reproducible observations consistent with it, and no probability, rate or population bound is drawn from them (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed). Our runs of these three entries on local seeds (one CPU): 106 and 100 of 256 (3.3 s each) and 12 of 24 (4.8 s).

## Appendix E: rows C and D expanded, and the allocation walk of one trial

Rows C and D and the arena of section 7 are exact counts of the algorithm of sections 4.2-4.4 at `r = 5`. E.1 and E.2 expand each row into its parts, each part a count from the dimensions of 4.3G, 4.3T and the half-gcd levels with the charges of 4.2; each table adds up exactly to its row. E.3 is the allocator of 4.2 run on every allocation and free of the trial in program order: the totals, the live-set peaks per stage, the two-ended-pool high-water mark, the slab classes, and the stage-D allocation/free trace against the high-water mark.

### E.1 Row C = 1,266,659,004,655

Row C is the sum of the steps of section 4.3T in the order the stage runs them:

| part of stage C | operations |
| --- | ---: |
| plans of the passes, the exponent, the node constants and the two-level root tables (built), the zero-fill of `g` above `m`, the first allocations | 8,321,926 |
| the allocation of `A` on `O1`; the Graeffe prefix (4.3G): `22` steps (below) and the allocation and free of its batch buffer | 83,392,245,023 |
| the Newton reciprocal of the reversed `g` to `ell` coefficients (doubling steps, products with running twiddle factors) | 6,489,198,781 |
| the product `q = floor(X^v P1 / g)` (one product of `2 ell - 1` points) and its copy | 1,910,411,988 |
| `g` to `O1` and `O2` (two scaling passes, two truncated forwards; the batch buffer allocated) | 2,542,504,110 |
| the start residue `A0` on `O2` (zero-fill, scaling, truncated forward of `q`, pointwise pass at 8) | 1,523,862,773 |
| `A0` to `O1` (one extension: truncated inverse, scaling, truncated forward) | 2,746,670,800 |
| `k1` on `O1` by chunked batch inversion (chunks of `2^16`, zero tests) | 361,560,465 |
| the squaring steps (step 6; below) | 1,161,430,968,652 |
| the exit step `Mont(A, 1)` (pointwise passes and one extension), the frees | 3,204,706,363 |
| two truncated inverses with scaling (`kappa R` and `g` in coefficient form), the frees, the closing control | 3,048,552,774 |
| stage bookkeeping (entry, exit) | 1,000 |
| **row C** | **1,266,659,004,655** |

The squaring steps: `164` steps with exponent bit 0 and `45` with bit 1, `164 * 5,541,224,588 + 45 * 5,614,891,916 = 1,161,430,968,652`. One step (`tr_step`, 4.3T) is:

| part of one step (bit 0) | operations |
| --- | ---: |
| bottom pass on `O1` (`U = A^2 k1`, 4 per point) | 637,814,036 |
| four middle-pass sets (inverse and forward, both sides), 748,383,892 each | 2,993,535,568 |
| two fused top passes (inverse top, coset twiddle, forward top), 369,764,352 each | 739,528,704 |
| bottom pass on `O2` (`B2 = (A2^2 + U g) delta_j`, 10 per point for bit 0) | 784,385,300 |
| loads of `delta_j` (2 per block of 64 points) | 763,392 |
| address updates of the `O2` bottom blocks beyond the 2 of the block control (2 per block: 4 array pointers, 4.2) | 763,392 |
| two recoveries of the dropped subtrees, 192,217,088 each | 384,434,176 |
| step control | 20 |
| **one step, bit 0** | **5,541,224,588** |

A step with bit 1 adds 3 per point of `O2` in its bottom pass and 1 address update (the point pointer) per block: `5,614,891,916 - 5,541,224,588 = 73,667,328 = 3 * 24,428,544 + 381,696`.

The Graeffe prefix (4.3G): `22` steps of `3,790,556,562` each, `83,392,244,364`; with the allocation of `A` on `O1` and the allocation and free of the batch buffer of the prefix, `83,392,245,023`. One Graeffe step (`gt2_step`) is:

| part of one Graeffe step | operations |
| --- | ---: |
| two pruned forward top passes, `E` and `O` read from `g` at stride 2 (`tr_top_half`) | 231,702,938 |
| three middle-pass sets (forward `E`, forward `O`, inverse), 748,383,892 each | 2,245,151,676 |
| fused bottom pass (forward bottom layers of `E` and `O`, `G = (E^2 - y O^2)/N` at 5 per point, inverse bottom layers) | 906,909,716 |
| inverse top pass (stores into `g`) | 214,575,104 |
| recovery of the dropped subtrees | 192,217,088 |
| step control | 40 |
| **one Graeffe step** | **3,790,556,562** |

Pass charges (4.3T, `TR_CFG`: top `3` | middle 5, 5, 6 | bottom `6` of the 25 layers, `n' = 24,428,544`): bottom block of `2^6` points with its twiddles, middle blocks and groups of radix 32/64, top blocks of `2^3` points over all `N / 2^3` offsets; the positions above `n'` that layers 1-13 touch are those of the batch buffer, one batch of classes at a time (4.3T). Middle-pass sets `tr_middle = 748,383,892`; top pass, fused, `369,764,352`; one recovery `192,217,088`.

### E.2 Row D = 354,378,608,236

The driver of 4.4 makes 31 outer steps, each `hgcd(k)` (`k = 2^j - 1`, the largest with `2k + 1 <= n` and `k <= KMAX = 2^21 - 1`) on the top window, then the apply of its matrix to the pair in place on the cheapest plan of `plan_apply`; from degree `141` the schoolbook pseudo-division Euclid, then the normalisation of `G`. The `hgcd(k)` charge includes the fold and the two-output passes of the nodes (4.4).

| outer step | degree `n` | k | `hgcd(k)` charge | apply charge (plan, points) | step total (with the arena and buffer allocations) |
|---:|---:|---:|---:|---:|---:|
| 1 | 24,414,062 | 2,097,151 | 25,794,231,889 | 9,277,889,453 (fixed-slot `3*2^a`, 6,291,456) | 35,072,124,606 |
| 2 | 22,316,911 | 2,097,151 | 25,794,231,889 | 7,989,211,267 (fixed-slot `3*2^a`, 6,291,456) | 33,783,446,420 |
| 3 | 20,219,760 | 2,097,151 | 25,794,231,889 | 7,889,471,201 (fixed-slot `3*2^a`, 6,291,456) | 33,683,706,354 |
| 4 | 18,122,609 | 2,097,151 | 25,794,231,889 | 6,600,792,895 (fixed-slot `3*2^a`, 6,291,456) | 32,395,028,048 |
| 5 | 16,025,458 | 2,097,151 | 25,794,231,889 | 6,501,052,893 (fixed-slot `3*2^a`, 6,291,456) | 32,295,288,046 |
| 6 | 13,928,307 | 2,097,151 | 25,794,231,889 | 5,212,374,531 (fixed-slot `3*2^a`, 6,291,456) | 31,006,609,684 |
| 7 | 11,831,156 | 2,097,151 | 25,794,231,889 | 5,112,634,637 (fixed-slot `3*2^a`, 6,291,456) | 30,906,869,790 |
| 8 | 9,734,005 | 2,097,151 | 25,794,231,889 | 3,461,665,147 (in place whole-pair `2^a`, 8,388,608) | 29,255,899,380 |
| 9 | 7,636,854 | 2,097,151 | 25,794,231,889 | 2,530,501,640 (in place whole-pair `3*2^a`, 6,291,456) | 28,324,735,873 |
| 10 | 5,539,703 | 2,097,151 | 25,794,231,889 | 1,697,918,155 (in place whole-pair `2^a`, 4,194,304) | 27,492,152,388 |
| 11 | 3,442,552 | 1,048,575 | 12,001,622,769 | 1,211,738,594 (in place whole-pair `3*2^a`, 3,145,728) | 13,213,363,707 |
| 12 | 2,393,977 | 1,048,575 | 12,001,622,769 | 775,663,281 (in place whole-pair `2^a`, 2,097,152) | 12,777,288,394 |
| 13 | 1,345,402 | 524,287 | 5,565,821,745 | 380,348,893 (in place whole-pair `2^a`, 1,048,576) | 5,946,172,982 |
| 14 | 821,115 | 262,143 | 2,571,783,585 | 282,240,068 (in place whole-pair `3*2^a`, 786,432) | 2,854,025,997 |
| 15 | 558,972 | 262,143 | 2,571,783,585 | 179,703,085 (in place whole-pair `2^a`, 524,288) | 2,751,489,014 |
| 16 | 296,829 | 131,071 | 1,183,354,569 | 80,943,496 (`3*2^a`, 196,608) | 1,264,299,146 |
| 17 | 165,758 | 65,535 | 541,911,373 | 42,759,253 (in place whole-pair `2^a`, 131,072) | 584,672,970 |
| 18 | 100,223 | 32,767 | 246,791,551 | 31,848,874 (in place whole-pair `3*2^a`, 98,304) | 278,642,769 |
| 19 | 67,456 | 32,767 | 246,791,551 | 17,089,000 (`3*2^a`, 49,152) | 263,881,632 |
| 20 | 34,689 | 16,383 | 112,261,983 | 8,292,150 (`3*2^a`, 24,576) | 120,555,214 |
| 21 | 18,306 | 8,191 | 50,748,991 | 4,042,974 (`3*2^a`, 12,288) | 54,793,046 |
| 22 | 10,115 | 4,095 | 22,768,895 | 1,994,672 (`3*2^a`, 6,144) | 24,764,648 |
| 23 | 6,020 | 2,047 | 10,116,047 | 1,065,524 (`2^a`, 4,096) | 11,182,652 |
| 24 | 3,973 | 1,023 | 4,434,919 | 836,549 (in place whole-pair `3*2^a`, 3,072) | 5,273,812 |
| 25 | 2,950 | 1,023 | 4,434,919 | 514,404 (`2^a`, 2,048) | 4,950,404 |
| 26 | 1,927 | 511 | 1,906,499 | 417,777 (in place whole-pair `3*2^a`, 1,536) | 2,326,620 |
| 27 | 1,416 | 511 | 1,906,499 | 250,516 (`2^a`, 1,024) | 2,158,096 |
| 28 | 905 | 255 | 793,745 | 215,321 (in place whole-pair `3*2^a`, 768) | 1,011,410 |
| 29 | 650 | 255 | 793,745 | 123,844 (`2^a`, 512) | 918,670 |
| 30 | 395 | 127 | 317,511 | 107,216 (in place whole-pair `3*2^a`, 384) | 427,071 |
| 31 | 268 | 127 | 317,511 | 62,836 (`2^a`, 256) | 381,428 |

| part of row D | operations |
| --- | ---: |
| the 31 outer steps above | 354,378,440,271 |
| the schoolbook Euclid from degree 141 | 163,983 |
| the normalisation of `G` (inversion of the leading coefficient, scaling) | 2,653 |
| stage entry (bookkeeping) | 1,012 |
| stage exit (closing control, the frees of the root tables, `g` and `R`) | 317 |
| **row D** | **354,378,608,236** |

### E.3 Totals and the allocation walk of one trial

```
m = 24,414,062 | truncated point sets: n1 = 24,428,544 of N = 33,554,432 (TRC = 1491 of 2048 nodes) | squaring steps 209 of which with S: 45
stage C pass split {'a': 3, 'b': 6, 'mid': [5, 5, 6]} (256 field registers of the declared register file)
S_C = 1,266,659,004,655
  stage D outer step: deg 24,414,062, hgcd(2,097,151) 25,794,231,889, apply 9,277,889,453 on fix3 (6,291,456 points)
  stage D outer step: deg 22,316,911, hgcd(2,097,151) 25,794,231,889, apply 7,989,211,267 on fix3 (6,291,456 points)
  stage D outer step: deg 20,219,760, hgcd(2,097,151) 25,794,231,889, apply 7,889,471,201 on fix3 (6,291,456 points)
  stage D outer step: deg 18,122,609, hgcd(2,097,151) 25,794,231,889, apply 6,600,792,895 on fix3 (6,291,456 points)
  stage D outer step: deg 16,025,458, hgcd(2,097,151) 25,794,231,889, apply 6,501,052,893 on fix3 (6,291,456 points)
  stage D outer step: deg 13,928,307, hgcd(2,097,151) 25,794,231,889, apply 5,212,374,531 on fix3 (6,291,456 points)
  stage D outer step: deg 11,831,156, hgcd(2,097,151) 25,794,231,889, apply 5,112,634,637 on fix3 (6,291,456 points)
  stage D outer step: deg 9,734,005, hgcd(2,097,151) 25,794,231,889, apply 3,461,665,147 on inp1 (8,388,608 points)
  stage D outer step: deg 7,636,854, hgcd(2,097,151) 25,794,231,889, apply 2,530,501,640 on inp3 (6,291,456 points)
  stage D outer step: deg 5,539,703, hgcd(2,097,151) 25,794,231,889, apply 1,697,918,155 on inp1 (4,194,304 points)
  stage D outer step: deg 3,442,552, hgcd(1,048,575) 12,001,622,769, apply 1,211,738,594 on inp3 (3,145,728 points)
  stage D outer step: deg 2,393,977, hgcd(1,048,575) 12,001,622,769, apply 775,663,281 on inp1 (2,097,152 points)
  stage D outer step: deg 1,345,402, hgcd(524,287) 5,565,821,745, apply 380,348,893 on inp1 (1,048,576 points)
  stage D outer step: deg 821,115, hgcd(262,143) 2,571,783,585, apply 282,240,068 on inp3 (786,432 points)
  stage D outer step: deg 558,972, hgcd(262,143) 2,571,783,585, apply 179,703,085 on inp1 (524,288 points)
  stage D outer step: deg 296,829, hgcd(131,071) 1,183,354,569, apply 80,943,496 on p3 (196,608 points)
  stage D outer step: deg 165,758, hgcd(65,535) 541,911,373, apply 42,759,253 on inp1 (131,072 points)
  stage D outer step: deg 100,223, hgcd(32,767) 246,791,551, apply 31,848,874 on inp3 (98,304 points)
  stage D outer step: deg 67,456, hgcd(32,767) 246,791,551, apply 17,089,000 on p3 (49,152 points)
  stage D outer step: deg 34,689, hgcd(16,383) 112,261,983, apply 8,292,150 on p3 (24,576 points)
  stage D outer step: deg 18,306, hgcd(8,191) 50,748,991, apply 4,042,974 on p3 (12,288 points)
  stage D outer step: deg 10,115, hgcd(4,095) 22,768,895, apply 1,994,672 on p3 (6,144 points)
  stage D outer step: deg 6,020, hgcd(2,047) 10,116,047, apply 1,065,524 on p1 (4,096 points)
  stage D outer step: deg 3,973, hgcd(1,023) 4,434,919, apply 836,549 on inp3 (3,072 points)
  stage D outer step: deg 2,950, hgcd(1,023) 4,434,919, apply 514,404 on p1 (2,048 points)
  stage D outer step: deg 1,927, hgcd(511) 1,906,499, apply 417,777 on inp3 (1,536 points)
  stage D outer step: deg 1,416, hgcd(511) 1,906,499, apply 250,516 on p1 (1,024 points)
  stage D outer step: deg 905, hgcd(255) 793,745, apply 215,321 on inp3 (768 points)
  stage D outer step: deg 650, hgcd(255) 793,745, apply 123,844 on p1 (512 points)
  stage D outer step: deg 395, hgcd(127) 317,511, apply 107,216 on inp3 (384 points)
  stage D outer step: deg 268, hgcd(127) 317,511, apply 62,836 on p1 (256 points)
  stage D tail: schoolbook Euclid from degree 141, 163,983
S_D = 354,378,608,236
peak of the live set, stage A = 781,713,472 bytes
peak of the live set, stage B = 1,721,237,696 bytes
peak of the live set, stage C = 3,129,708,480 bytes
peak of the live set, stage D = 2,906,177,600 bytes
two-ended pool: blocks of more than 2^14 bytes; largest sum of the two ends after each stage (bytes): init 0, A 781,713,472, B 1,721,237,696, C 3,129,708,480, D 3,129,708,480; at most 10 blocks; 622 blocks examined in all
slab classes (class: peak number of live blocks): 14: 4; slab area = 65,536 bytes
arena = 3,129,791,040 bytes (two-ended pool 3,129,708,480 + 128, slab classes 65,536, stages E and later 16,896), memory = 3,135,408,332 bytes, log2 = 31.54601
stage D on the two-ended pool (blocks of more than 2^14 bytes): after init, A, B, C: low end 782,286,528, high end 781,713,472, live 1,564,000,000, largest sum so far 3,129,708,480
  stage D: 335 pool events (166 allocations, 169 frees) on 169 distinct blocks; the first 24:
  alloc #4              268,435,520 bytes pool L | live      1,832,435,520 | pool low      1,050,722,048 high        781,713,472 sum      1,832,435,520
  alloc #5              805,298,240 bytes pool L | live      2,637,733,760 | pool low      1,856,020,288 high        781,713,472 sum      2,637,733,760
  free  #5              805,298,240 bytes pool   | live      1,832,435,520 | pool low      1,050,722,048 high        781,713,472 sum      1,832,435,520
  alloc #6              201,326,656 bytes pool H | live      2,033,762,176 | pool low      1,050,722,048 high        983,040,128 sum      2,033,762,176
  alloc #7              201,326,656 bytes pool H | live      2,235,088,832 | pool low      1,050,722,048 high      1,184,366,784 sum      2,235,088,832
  alloc #8              201,326,656 bytes pool H | live      2,436,415,488 | pool low      1,050,722,048 high      1,385,693,440 sum      2,436,415,488
  alloc #9              201,326,656 bytes pool H | live      2,637,742,144 | pool low      1,050,722,048 high      1,587,020,096 sum      2,637,742,144
  free  #4              268,435,520 bytes pool   | live      2,369,306,624 | pool low        782,286,528 high      1,587,020,096 sum      2,369,306,624
  alloc #10             201,326,656 bytes pool L | live      2,570,633,280 | pool low        983,613,184 high      1,587,020,096 sum      2,570,633,280
  alloc #11             201,326,656 bytes pool L | live      2,771,959,936 | pool low      1,184,939,840 high      1,587,020,096 sum      2,771,959,936
  free  #10             201,326,656 bytes pool   | live      2,570,633,280 | pool low      1,184,939,840 high      1,587,020,096 sum      2,771,959,936
  free  #11             201,326,656 bytes pool   | live      2,369,306,624 | pool low        782,286,528 high      1,587,020,096 sum      2,369,306,624
  free  #6              201,326,656 bytes pool   | live      2,167,979,968 | pool low        782,286,528 high      1,587,020,096 sum      2,369,306,624
  free  #7              201,326,656 bytes pool   | live      1,966,653,312 | pool low        782,286,528 high      1,587,020,096 sum      2,369,306,624
  free  #8              201,326,656 bytes pool   | live      1,765,326,656 | pool low        782,286,528 high      1,587,020,096 sum      2,369,306,624
  free  #9              201,326,656 bytes pool   | live      1,564,000,000 | pool low        782,286,528 high        781,713,472 sum      1,564,000,000
  alloc #12             268,435,520 bytes pool L | live      1,832,435,520 | pool low      1,050,722,048 high        781,713,472 sum      1,832,435,520
  alloc #13             805,298,240 bytes pool L | live      2,637,733,760 | pool low      1,856,020,288 high        781,713,472 sum      2,637,733,760
  free  #13             805,298,240 bytes pool   | live      1,832,435,520 | pool low      1,050,722,048 high        781,713,472 sum      1,832,435,520
  alloc #14             201,326,656 bytes pool H | live      2,033,762,176 | pool low      1,050,722,048 high        983,040,128 sum      2,033,762,176
  alloc #15             201,326,656 bytes pool H | live      2,235,088,832 | pool low      1,050,722,048 high      1,184,366,784 sum      2,235,088,832
  alloc #16             201,326,656 bytes pool H | live      2,436,415,488 | pool low      1,050,722,048 high      1,385,693,440 sum      2,436,415,488
  alloc #17             201,326,656 bytes pool H | live      2,637,742,144 | pool low      1,050,722,048 high      1,587,020,096 sum      2,637,742,144
  free  #12             268,435,520 bytes pool   | live      2,369,306,624 | pool low        782,286,528 high      1,587,020,096 sum      2,369,306,624
  the 0 events that raise the high-water mark (the last 0 shown; event number first):
  after stage D: low end 0, high end 0; high-water mark of the pool over the trial 3,129,708,480 bytes
```

## Appendix L: the line program `L` (this entry; the form of mpjunior92 `5ae6d1c7`, listing form of `4c6dc4cf` Appendix L)

### L.1 Construction

`L(x) = F(x - E0_0) / OUTSCALE`, `F` the digest on the line of 2.2 (`W = tau^5`). The state after round 1 is `A + W B` (2.2: `alpha = A + c_2`, `beta = B`); the round-2 S-box input of lane `i` is `A_i + c_{2,i} + W B_i = B_i (W + E0_i)`, `E0_i = (A_i + c_{2,i}) / B_i` (every `B_i != 0` on the deployed constants). With `x = W + E0_0` lane 0 is `B_0 x` and lane `i` is `B_i (x + e_i)`, `e_i = E0_i - E0_0`. Every lane is held as its true value divided by a known nonzero scale; an S-box of a held lane is 3 multiplications and divides the true output by the fifth power of the scale, which the next linear layer absorbs, each output lane held divided by its coefficient on `z0`: a dense layer with the next round's constants is `y_k = z0 + a_k z1 + b_k z2 + k_k` (2 multiplications, 3 additions). Partial rounds use the sparse form of Grassi, Khovratovich, Rechberger, Roy and Schofnegger (USENIX Security 2021) with the same scaling: lane 0 is held as `lambda h0 + gamma`, lanes 1, 2 as `P (h1, h2) + q` with `P = Mww^j P0` after `j` partial rounds (`Mww` the lower-right 2x2 block of `M`) and `P0 = Mww^-r D`, `D` diagonal, so `P = D` at the exit; one partial round is `u = h0 + k`, `x5 = u^5` (3), `h0 = x5 + n1 h1 + n2 h2` (from the old `h1`, `h2`), `h1 = h1 + v1 x5`, `h2 = h2 + v2 x5`: 12 operations. Counts: entry 2; round 2 (S-boxes 9, dense layer with the round-3 constants 15); round 3 (S-boxes 9, into the partial form 6 multiplications and 6 additions, `D` normalising the `z0` coefficients); `r` partial rounds, 12 each; exit 3 (the round-60 constants); rounds 60-62 (24 each); round 63 (S-boxes 9, row 0 held divided by its `z0` coefficient `OUTSCALE`, 2 multiplications and 2 additions): `2 + 24 + 21 + 12 r + 3 + 72 + 13 = 135 + 12 r = 195` at `r = 5`. Every constant is a closed formula of the deployed constants (6.2).

### L.2 Check

`E0_0 = 0x3a4bd2e80f62c6cde67f816c4a67f17bbd43a70c4d2fca9784cc22ba736569ff`, `OUTSCALE = 0x3b04da4c4762d1474ebac1974ca95db33bd1a107565d5024796a5e231ec9bd09`. Our program (standard library only) builds `L` from the organizer constants file, executes it with an operation counter, and asserts `OUTSCALE * L(W + E0_0) = digest(message(W))` with the reference rounds of `verifier/poseidon.py` at 100 random `W` (r = 5: 195 operations executed each; also r = 0, 1, 3, 10 with `135 + 12 r` operations); `message(W)` is the canonical pair of 2.2. At r = 10 it gives the `OUTSCALE` printed in `4c6dc4cf` L.2.

### L.3 Constants of `L` at r = 5

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
pf_a1 = 0x056843b97dddae3d7a2b7700b183fcc8ee3c980877b43443208df496048ae660
pf_b1 = 0x2fd9d2701b436291393cabc36cdfa1fbcd3d2b232c7f72620e7cecb6300d6e95
pf_a2 = 0x16acf09f2b76a5e57f323de5c67e245a9135244acc705555319139a76b92e96b
pf_b2 = 0x0cf09b10a4a47376a1da95893a406263dfa04ac849b9173722a4160b7ac92c5a
p0_k = 0x34058bb8920441623716adeb0155288a2cca42fa34af13309820b9953e4336cf
p0_n1 = 0x0150debac3f0266464a3c1b65c8d22ab4af610a2c8fecb700a65196280bd9701
p0_n2 = 0x09bb45335bc21a589e14b0d48b80810788b95805c4db17264f6c4daa0c29c406
p0_v1 = 0x20c5a9f8591309427b53865ba78f7afd6ef13ea771b6626357334dafcd7de723
p0_v2 = 0x23861cdec5c0797a4de12420c57418ffe8acc112842b714b88b240a29c6bb20b
p1_k = 0x266144e217c50738f29b2b098b54686e360c94c1f64cc0b43c6b0a0cc37fc9eb
p1_n1 = 0x1d7f3490c813f945184daecf3fc6cd5b4eff3f426c7925458acb147f6ffa3841
p1_n2 = 0x27cd771fae83deaca39bf3a0cf454e06264e7c9c549c317cb6f4c6d50b89de37
p1_v1 = 0x270717abafe0f8adfea5b5ea79071b3537427281383cc8d1d10a1ad0c73a7381
p1_v2 = 0x0becd39750a32a5bc9531cb46537637807b5bfd5458dbc002d9f1c10de99b292
p2_k = 0x1565f5ef914944ad12c16e36ec616abd4dd0f8c94d990dc4ff415ad5a506d732
p2_n1 = 0x0ef9564641f8bc032ed26fec5d7204312a0098bbbfca77a3a20ca38f770376b1
p2_n2 = 0x3d7cc5fa94b85ff25e33e4ee71eb8da439dc502d06baf339b461e3f087a88a49
p2_v1 = 0x0a6a9ca9e4d631f412ccc2ef72920cf7c357d41bdc5eb074ae677b2bd272eda2
p2_v2 = 0x05fb782ad558098a2176f3af013f352b6f7b9de1314de8016466257700f0e7c6
p3_k = 0x31f134c3cb80372eff4d98f34741c78bf04e38ca64691c338f55660789f29b61
p3_n1 = 0x2c70049cb970e97efbb0980abc4725622d6aa5f04477e546dff03e6013076354
p3_n2 = 0x342d53bfdd99100d2ec4b373f6c27ca5cd2f200cfca3ec48022212be2c34a8e6
p3_v1 = 0x2e8364aa898745ef5ee93c31fc6cae534fc6dbbecaf9db219d46e483b35b8470
p3_v2 = 0x0634fcc189679fedfe140f8d02b546560df4c66406a33f1ac24be0bdf35aa781
p4_k = 0x2ca8302ed55720cd2a1b9478af5a5f4a223bd4fe9f778963e71519b2113aecb6
p4_n1 = 0x3abde54c29589b2167c2e32a5d2b052a331b2252de37e91f44ac6ba51f7d2c1e
p4_n2 = 0x2144ccf661e16a7c4d5715e136c8121435a38512716ddafcf8327c65ebabc6cf
p4_v1 = 0x322de1c36fdcc5f5df026d9cd3462ec4cc0fb86304aff492586cc5c668ca29f8
p4_v2 = 0x34c5885af3476c9a4c2f9d891bbb34a41714ee0c1852b1091b3cd98201613b5f
x_k0 = 0x1cc681ff1b551c10a7a4f50c7e8e8d930471b6efc158b8e62d62b5c2ae9e9e11
x_k1 = 0x103ff3b557ddef5abc4d2a6470c25adf357f4abed7ab239bc7de9187addf5e65
x_k2 = 0x388dc064035f4ccbbedc72973bb9acf262e8238a6bc769096f0e8a48cde8be9b
r60_a0 = 0x27db26d6319d1053d0fb8187b6d011dc7759196721f9e51cdea070f77e713152
r60_b0 = 0x3dd1a9c4cf21fe25a88665dc2e95716b0cd27e0f5131da4223c45f4cd183afe3
r60_k0 = 0x161e73e3041493ca141481e15d2f104782df6625923371ff5d82ffd44f9310ed
r60_a1 = 0x1f0e3ddfda5886b6f8572da2a6bc003dedd86653fec12a613e75889176a1c658
r60_b1 = 0x1f9f3b9673cd66bd4dca71417e4ee3de4c2057e63ab51475b7c7740c7d4049e2
r60_k1 = 0x187259505547bd059cf70bc33b91d605d83cc429e9170fbec70e12fe76294797
r60_a2 = 0x0cdb31c73de164a6d3177d83af774897ac7cfd23ff43f9845b3e25fa124777c5
r60_b2 = 0x0316e65f6867e76caaba441b60918c0786668fbece8ba6a47f922aa11cb1047d
r60_k2 = 0x2df1813844cdf6044f98845215e2ddd8807287bcdf2c5b726b12c2a58d80d0c6
r61_a0 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
r61_b0 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
r61_k0 = 0x070d1fc5c9e163d62bb8e3ae11b7f6ca07bf63c64a74a8380dd9ddc4f8abfeb8
r61_a1 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
r61_b1 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
r61_k1 = 0x340a2e595e66931c2d612a064f6771b71af4e99644bdf09ad4eb4e18e49ff10d
r61_a2 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
r61_b2 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
r61_k2 = 0x1040344a883cb42d55b8b07af3f4f6c2e27b960a88365ad339630790844a097c
r62_a0 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
r62_b0 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
r62_k0 = 0x3cf43ef257d769dd4c3dd9a8951aa32ccd65b5cf9513da0ec823de4e6bdc9d49
r62_a1 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
r62_b1 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
r62_k1 = 0x2b9a13d4cf08daa595df0ee48e182de3638fb83ab15cb8d97b96ba77ceb77927
r62_a2 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
r62_b2 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
r62_k2 = 0x145f0fbf0afc64867daa5e3e922bc73ac8aa614c3dfc6c797a0c9a31569a893f
o_a = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
o_b = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
```

### L.4 Listing of `L` at r = 5 (195 operations; `x` is input and output; `e1`, `e2` and the other names below are the constants of L.3)

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

## Appendix B: the stage-B point loop on root tables (this entry; the method of mpjunior92 `1ac48175`, on our mixed-radix layout)

Layout (4.2): the transform of `H = 3 * 2^23` points stores the value for exponent `k` at position `row * n + rev_23(k mod n)`, `row = k mod 3`, `n = 2^23`. The base loop ran over `k` and paid per point the two point additions, one subtraction, one multiplication by `1/(2 zeta^k)`, the two recurrences, the store with its address 2, the calls 10 (the two evaluations, the index routine, the row counter), the index routine `12 + 7 * 23 + 2 = 175` and the loop control 3: 196 per point, `196 * H + 2 = 4,932,501,506`.

Here the positions are visited in storage order: `row` (3), then `j` in `[0, n)` by the four digits of `j` (5, 6, 6, 6 bits, high digit outermost). By the Chinese remainder theorem `k = (row * e3 + k2 * en) mod 3n` with `k2 = rev_23(j)`, `e3 = 0 mod n`, `e3 = 1 mod 3`, `en = 0 mod 3`, `en = 1 mod n`, so `zeta^k = +/- zeta^(row e3) * (zeta^en)^(k2)` (`zeta^(3n) = -1`), and the stored value is the same for both signs (section 3). `(zeta^en)^(rev_23(j))` is the product over the digits `x_l` of `j` of the table entries `T_l[x_l] = (zeta^en)^(rev_(d_l)(x_l) * 2^(23 - o_l - d_l))` (`o_l` the bit offset of digit `l`), and `1/(2s)` the product of the inverse tables with the row constant `1/(2 zeta^(row e3))`. Each level holds its partial products `s`, `u` in registers: an outer iteration loads two entries and forms two products (9 with its loop control), the innermost iteration is the 18 of section 3; every loop exit 2; per trial `c' = c + E0_0` and the start pointer 2. Tables: `32 + 3 * 64 = 224` entries and their inverses and 6 row constants, `454` words, built offline (6.2). Levels: rows: 3 iterations, 23; 5-bit digit: 96 iterations, 870; 6-bit digit: 6,144 iterations, 55,488; 6-bit digit: 393,216 iterations, 3,551,232; 6-bit digit: 25,165,824 iterations, 453,771,264; total `457,378,879` operations (was `4,932,501,506`). Our program executes this nest with an operation counter on plans of `3 * 2^a` points (`a = 6, 8, 9`), asserts `s^2 = zeta^(2k)` and `2 s u = 1` at every position against the base layout, and the counter equals the closed form.

## Appendix S: stage E, register-resident (the procedure and charge of `4c6dc4cf` Appendix S, as in `5ae6d1c7`)

Input `G` monic, `1 <= d = deg G <= 16`, a product of distinct linear factors over `F_p` (9.4). If `d = 1` the root is `-G_0`. Otherwise `H := G` (loaded into field registers) and at most `Z = 64` rounds: 1. draw `a` (63, two words, 4.1.1) and test it (5); 2. `B := (X + a)^((p-1)/2) mod H`: start `B = X + a` (3), then for each of the 253 bits below the top bit of `(p-1)/2` one squaring modulo `H` and, on the 45 one-bits, one multiplication by `X + a` modulo `H`; 3. `B := B - 1` (1); 4. `T := gcd(H, B)` monic, by inversion-free elimination: while the second row is nonzero, order the rows by degree and replace the higher row `A` by `lc(B) A - lc(A) X^(deg A - deg B) B` (at most `3 d` field operations, 6 control, 3 for the ordering), strip zero top coefficients (2 each); then one inversion of the leading coefficient by square-and-multiply on the 254 bits below the top bit of `p - 2` (76 one-bits: 254 squarings and 76 multiplications, 4 control per bit) and `d` multiplications; 5. keep `T` if `1 <= deg T < deg H`, else keep `H` (6); stop with the root `-H_0` when `deg H = 1`.

Charges at degree `d` (field operations 1 each; every operand is a field register: `H` (`d`), `B` (`d`), the square (`2d - 1`) and the two gcd rows (`2d + 1`), at most 100 of the 256 field registers of 4.2 with the shift and the loop registers; no load or store inside a round): squaring modulo `H`, `S(d) = d (d+1)/2 + d (d-1)/2 - (2d - 3) + (2d - 3) + (d - 2) + 2 d (d - 1)`, `S(16) = 750`, plus 4 of bit control; multiplication by `X + a` modulo `H`, `4 d`; gcd, at most `2 d - 1` eliminations, `(2 d - 1)(3 d + 9) + 2 (2 d + 1)` with the strips, the inversion `254 * 5 + 76 = 1,346` and `d`: `3,195` at `d = 16`. `R(d) = 68 + 3 + 253 (S(d) + 4) + 45 * 4 d + 1 + gcd(d) + 6`, non-decreasing in `d`; `R(16) = 68 + 3 + 190,762 + 2,880 + 1 + 3,195 + 6 = 196,915`. Row E charges every one of the 64 rounds at `d = 16`: `64 * 196,915 + 1,000 + 200 = 12,603,760`. The isolation bound of 9.4 holds for this procedure: a pair with distinct nonzero characters always lands on opposite sides of the kept factor.
